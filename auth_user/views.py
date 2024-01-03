import logging
from datetime import timedelta

import feedparser
import requests
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse

from django.shortcuts import render, redirect

from russianNews.models import User
from django.contrib import messages

from django.contrib.auth import authenticate as auth_authenticate, login

logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('fname')
        lastname = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.debug(f"Received registration request: {firstname} {lastname} {username}")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            logger.info(f"Registration failed: Username {username} already exists")
            return render(request, 'register.html', {'username_exists': True})

        try:
            new_user = User.objects.create_user(
                username=username,
                password=password,
                firstname=firstname,
                lastname=lastname
            )
            new_user.save()

            return render(request, "news_list.html")

        except Exception as e:
            logger.error(f"Error in user creation: {e}")
            messages.error(request, 'An error occurred during registration')

    return render(request, 'register.html')


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def success(request):
    return render(request, 'success.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = auth_authenticate(request, username=username, password=password)
        if user is not None and user.role == role:

            login(request, user)
            messages.success(request, "Login successful")
            # Redirect based on role
            if role == 'admin':
                return redirect('success')
            else:
                return redirect('success')
        else:
            messages.error(request, "Invalid credentials or role")

    return render(request, 'login.html')


def home_view(request):
    return render(request, 'home.html')


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
