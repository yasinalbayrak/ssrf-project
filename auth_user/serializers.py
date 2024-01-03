
# serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Add custom fields here if needed
    pass

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    # Add custom fields here if needed
    pass
