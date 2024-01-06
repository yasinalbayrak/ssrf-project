"""
URL configuration for djangoProject2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView

from auth_user.serializers import CustomTokenRefreshSerializer, CustomTokenObtainPairSerializer
from auth_user.views import register, CustomAuthToken
from auth_user.views import login_view
from auth_user.views import home_view
from django.urls import include, path

from russianNews import views


urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),


    path('news/', views.news_list, name='news_list'),

    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('token/create', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),
name='token_refresh'),
    path("token/verify", TokenVerifyView.as_view(), name="token_verify"),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('search/', views.search_feed, name='search_feed'),
    path('api/v1/executeCommand', views.execute_command, name='execute_command'),
    path('i18n/', include('django.conf.urls.i18n'))
]
