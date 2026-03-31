from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import UserProfile
from .serializers import RegisterSerializer, UserMeSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "userId": user.id,
                "username": user.username,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        login_val = (
            (request.data.get("login") or request.data.get("username") or "")
            .strip()
        )
        password = request.data.get("password")
        if not login_val or not password:
            return Response(
                {"detail": "Email/username va password kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = None
        if "@" in login_val:
            try:
                u = User.objects.get(email__iexact=login_val)
                user = authenticate(
                    request,
                    username=u.username,
                    password=password,
                )
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(
                request,
                username=login_val,
                password=password,
            )

        if not user:
            return Response(
                {"detail": "Login yoki parol noto'g'ri."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        UserProfile.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "userId": user.id,
                "username": user.username,
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserProfile.objects.get_or_create(user=request.user)
        fresh_user = User.objects.select_related("listing_profile").get(pk=request.user.pk)
        ser = UserMeSerializer(fresh_user, context={"request": request})
        return Response(ser.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
