from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from apps.account.models import OTP, User
from apps.account.serializers.user_serializer import UserSerializer
from apps.account.tasks import send_otp_email_task, send_password_changed_email_task
from apps.global_config.permissions import IsStaffOrHasPermission


class RegisterView(APIView):
    permission_classes = [IsStaffOrHasPermission]
    queryset = User.objects.none()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                'message': 'Registration successful',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie(
            'access_token', str(refresh.access_token),
            httponly=True, samesite='Lax', path='/',
        )
        response.set_cookie(
            'refresh_token', str(refresh),
            httponly=True, samesite='Lax', path='/',
        )
        return response


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


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')

        if not all([old_password, new_password, confirm_new_password]):
            return Response(
                {'detail': 'All fields are required: old_password, new_password, confirm_new_password.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_password != confirm_new_password:
            return Response(
                {'detail': 'New passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if not user.check_password(old_password):
            return Response(
                {'detail': 'Old password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        send_password_changed_email_task.delay(user.email, user.name)

        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'detail': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Always return same response regardless of whether email exists
        if User.objects.filter(email=email).exists():
            import random
            otp_code = ''.join(str(random.randint(0, 9)) for _ in range(6))
            OTP.objects.create(email=email, otp=otp_code)
            send_otp_email_task.delay(email, otp_code)

        return Response(
            {'detail': 'If this email exists, an OTP has been sent.'},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        if not email or not otp_code:
            return Response(
                {'detail': 'Email and OTP are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj = OTP.objects.filter(
            email=email,
            otp=otp_code,
            is_verified=False,
        ).first()

        if not otp_obj or otp_obj.is_expired():
            return Response(
                {'detail': 'Invalid or expired OTP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj.is_verified = True
        otp_obj.save()

        return Response(
            {'detail': 'OTP verified successfully.'},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')

        if not all([email, new_password, confirm_new_password]):
            return Response(
                {'detail': 'All fields are required: email, new_password, confirm_new_password.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_password != confirm_new_password:
            return Response(
                {'detail': 'New passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj = OTP.objects.filter(email=email, is_verified=True).first()
        if not otp_obj or otp_obj.is_expired():
            return Response(
                {'detail': 'OTP not verified or expired. Please request a new OTP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response(
                {'detail': 'Password reset successfully.'},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
