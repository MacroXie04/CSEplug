"""API views for authentication."""

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import REFRESH_COOKIE_NAME
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .services import (
    blacklist_refresh_token,
    clear_jwt_cookies,
    generate_tokens,
    set_jwt_cookies,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        access_token, refresh_token = generate_tokens(user)

        response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        set_jwt_cookies(response, access_token, refresh_token)
        return response


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        access_token, refresh_token = generate_tokens(user)

        response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        set_jwt_cookies(response, access_token, refresh_token)
        return response


class RefreshTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not raw_refresh:
            raise AuthenticationFailed("Refresh token missing.")

        try:
            refresh = RefreshToken(raw_refresh)
        except TokenError as exc:  # pragma: no cover - defensive branch
            raise AuthenticationFailed("Invalid refresh token.") from exc

        try:
            user = User.objects.get(pk=refresh["user_id"])
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found.") from exc

        # Blacklist the old refresh token when rotation is enabled
        blacklist_refresh_token(raw_refresh)

        new_access, new_refresh = generate_tokens(user)
        response = Response({"detail": "Token refreshed."}, status=status.HTTP_200_OK)
        set_jwt_cookies(response, new_access, new_refresh)
        return response


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        blacklist_refresh_token(raw_refresh)

        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        clear_jwt_cookies(response)
        return response


class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        data = UserSerializer(request.user).data
        return Response(data, status=status.HTTP_200_OK)

