import logging

import feedparser
from django.db.models import Q
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from russianNews.models import NewsItem, LastFetch
from django.utils.dateparse import parse_datetime
import requests

import xml.etree.ElementTree as Et
from dateutil import parser
from googletrans import Translator

logging.basicConfig(filename='feed_log.txt', level=logging.INFO)



def news_list(request):
    """
    View to display a list of news items.
    """

    # fetch_news()
    search_query = request.GET.get('search', '')  # Get the search query from the URL query parameter

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


def news_detail(request, news_id):
    """
    View to display a detailed news item.
    """
    news_item = NewsItem.objects.get(id=news_id)
    return render(request, 'news_list.html', {'news_item': news_item})


from django.utils.dateparse import parse_datetime


def fetch_news():
    feed_url = 'https://www.mk.ru/rss/news/index.xml'
    xml = getXML(feed_url)
    last_build, items = extract_items_and_lbd(xml)
    translator = Translator()

    for entry in items:

        if not NewsItem.objects.filter(link=entry["link"]).exists():
            pub_date_parsed = parser.parse(entry.get("pub_date"))

            title_ru = entry.get("title")
            title_en = translator.translate(title_ru, src='ru', dest='en').text

            link = entry.get("link")
            desc_ru = entry.get("description")
            desc_en = translator.translate(desc_ru, src='ru', dest='en').text
            pub_date = pub_date_parsed

            category_ru = entry.get("category")
            category_en = translator.translate(category_ru, src='ru', dest='en').text

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

        response = requests.get(url)
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
