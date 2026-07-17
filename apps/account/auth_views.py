from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response(
            {'message': 'Login successful'},
            status=status.HTTP_200_OK,
        )
        self._set_cookies(response, serializer.validated_data)
        return response

    def _set_cookies(self, response, data):
        access = data.get('access')
        refresh = data.get('refresh')
        if access:
            response.set_cookie(
                'access_token', access,
                httponly=True, samesite='Lax', path='/',
            )
        if refresh:
            response.set_cookie(
                'refresh_token', refresh,
                httponly=True, samesite='Lax', path='/',
            )


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'refresh' not in data and 'refresh_token' in request.COOKIES:
            data['refresh'] = request.COOKIES['refresh_token']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        response = Response(
            {'message': 'Token refreshed'},
            status=status.HTTP_200_OK,
        )

        access = serializer.validated_data.get('access')
        if access:
            response.set_cookie(
                'access_token', access,
                httponly=True, samesite='Lax', path='/',
            )

        refresh = serializer.validated_data.get('refresh')
        if refresh:
            response.set_cookie(
                'refresh_token', refresh,
                httponly=True, samesite='Lax', path='/',
            )

        return response


class CookieTokenBlacklistView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'refresh' not in data and 'refresh_token' in request.COOKIES:
            data['refresh'] = request.COOKIES['refresh_token']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response
