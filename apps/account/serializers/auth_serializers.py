from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField(required=True)
        self.fields.pop('username', None)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.pop('password')

        if not email:
            raise serializers.ValidationError('Email is required.')

        user = authenticate(username=email, password=password)

        if user is None or not user.is_active:
            raise serializers.ValidationError(
                'Invalid email or password.',
            )

        self.user = user
        refresh = self.get_token(user)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
