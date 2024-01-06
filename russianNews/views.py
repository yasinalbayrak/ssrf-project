import subprocess
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
import logging
import time

import feedparser
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from requests import ReadTimeout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django import forms

from .forms import CommentForm
from .models import Comment
from russianNews.models import NewsItem, LastFetch
from django.utils.dateparse import parse_datetime
import requests
from russianNews.models import User
import xml.etree.ElementTree as Et
from dateutil import parser
from googletrans import Translator

logging.basicConfig(filename='feed_log.txt', level=logging.INFO)


def news_list(request):
    """
    View to display a list of news items.
    """
    # fetch_news()

    # Get the search query from the URL query parameter
    search_query = request.GET.get('search', '')

    if search_query:

        news_items = NewsItem.objects.filter(
            Q(title_en__icontains=search_query) |
            Q(title_ru__icontains=search_query) |
            Q(description_en__icontains=search_query) |
            Q(description_ru__icontains=search_query)
        ).order_by('-pub_date')
    else:
        news_items = NewsItem.objects.all().order_by('-pub_date')

    return render(request, 'news_list.html', {'news_items': news_items, 'search_query': search_query})


def translate_text_with_retry(text, src, dest, max_retries=3):
    translator = Translator()
    for attempt in range(max_retries):
        try:
            return translator.translate(text, src=src, dest=dest).text
        except ReadTimeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:

                return text


def fetch_news():
    feed_url = 'https://www.mk.ru/rss/news/index.xml'
    xml = getXML(feed_url)
    last_build, items = extract_items_and_lbd(xml)

    for entry in items:
        if not NewsItem.objects.filter(link=entry["link"]).exists():
            pub_date_parsed = parser.parse(entry.get("pub_date"))

            title_ru = entry.get("title")
            title_en = translate_text_with_retry(title_ru, src='ru', dest='en')

            link = entry.get("link")
            desc_ru = entry.get("description")
            desc_en = translate_text_with_retry(desc_ru, src='ru', dest='en')

            pub_date = pub_date_parsed

            category_ru = entry.get("category")
            category_en = translate_text_with_retry(
                category_ru, src='ru', dest='en')

            news_item = NewsItem(
                title_ru=title_ru,
                title_en=title_en,
                link=link,
                description_ru=desc_ru,
                description_en=desc_en,
                pub_date=pub_date,
                category_ru=category_ru,
                category_en=category_en
            )
            news_item.save()


def getXML(url):
    try:

        response = requests.get(url, timeout=100)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def extract_items_and_lbd(xml_data):
    root = Et.fromstring(xml_data)

    # Initialize a list to store news_item objects
    news_items = []
    lastBuildDate = root.find('.//lastBuildDate').text
    # Iterate through the 'item' elements in the XML
    for item_elem in root.findall('.//item'):
        title = item_elem.find('title').text
        link = item_elem.find('link').text
        description = item_elem.find('description').text
        pub_date = item_elem.find('pubDate').text
        category = item_elem.find('category').text
        # Extract other information as needed (e.g., category, enclosure)

        # Create a news_item dictionary
        news_item = {
            'title': title,
            'link': link,
            'description': description,
            'pub_date': pub_date,
            'category': category

        }

        # Append the news_item to the list
        news_items.append(news_item)

    return lastBuildDate, news_items


@login_required
def news_detail(request, pk):
    news_item = get_object_or_404(NewsItem, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)
            comment.news_item = news_item
            comment.author = request.user
            comment.save()

            return redirect('news_detail', pk=news_item.pk)
    else:
        form = CommentForm()
    return render(request, 'news_detail.html', {'news_item': news_item, 'form': form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if the user is authorized to delete the comment
    if request.user == comment.author or request.user.is_staff:
        comment.delete()
        return redirect('news_detail', pk=comment.news_item.id)
    else:
        # Handle unauthorized attempts
        messages.error(
            request, "You do not have permission to delete this comment.")
        return redirect('news_detail', pk=comment.news_item.id)


@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    users = User.objects.all()

    if request.method == "POST" and 'delete_user' in request.POST:
        user_id = request.POST.get('delete_user')
        user_to_delete = User.objects.get(id=user_id)

        if user_to_delete.role == "user":
            user_to_delete.delete()

        else:
            pass
            # Not authorized

        return redirect('manage_users')

    return render(request, 'manage_users.html', {'users': users})


def search_feed(request):
    feed_url = request.GET.get('feed', '')
    if feed_url:
        try:
            response = requests.get(feed_url)
            # Assuming the feed returns JSON data

            return render(request, 'news_list.html', {'data': response.text})
        except requests.RequestException as e:
            return HttpResponse(f"Error fetching the feed: {e}")

    return render(request, "news_list.html")


@require_http_methods(["GET"])
def execute_command(request):
    try:
        command = request.GET.get('command', '')

        if command:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            exit_code = process.wait()

            if exit_code == 0:
                return JsonResponse({'status': 'success', 'output': stdout.decode()})
            else:
                return JsonResponse({'status': 'error', 'output': stderr.decode()})
        else:
            return JsonResponse({'error': 'No command provided'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def getCurrency(request):
    try:
        divident = request.GET.get('from')
        divisor = request.GET.get('to')
        command = f"python3 currency.py {divident} {divisor}"
        if divident or divisor:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            exit_code = process.wait()
            if exit_code == 0:
                return JsonResponse({'result': stdout.decode()})
            else:
                return JsonResponse({'status': 'error', 'output': stderr.decode()})
        else:
            return JsonResponse({'error': 'No command provided'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def serve_image_from_url(request):
    image_url = 'https://example.com/path/to/image.jpg'
    response = requests.get(image_url, stream=True)

    if response.status_code != 200:
        return HttpResponse('Failed to fetch image', status=404)

    # Get the content type of the image
    content_type = response.headers['content-type']
    return HttpResponse(response.content, content_type=content_type)


from django.shortcuts import render
from django.http import HttpResponse
from .forms import ImageUrlForm


def get_image(request):
    context = {
        'form': ImageUrlForm(),
        'image_url': None,
        'status_message': '',
        "response": "",
        'error_message': None,
        "last_message": ""
    }

    if request.method == 'POST':
        form = ImageUrlForm(request.POST)
        if form.is_valid():
            image_url = form.cleaned_data['image_url']
            try:
                response = requests.get(image_url, stream=True)

                if response.status_code == 200:
                    context['image_url'] = image_url
                    context['response'] = response.content
                    context['last_message'] = "Successfully Uploaded"
                else:
                    context['last_message'] = 'Failed to fetch image with status code: {}'.format(response.status_code)

            except Exception as e:
                context['last_message'] = 'Failed to fetch image {}'.format(str(e))

    return render(request, 'fetch_image.html', context)
