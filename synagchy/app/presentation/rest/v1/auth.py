from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.presentation.rest.v1.serializers import (
    RegisterSerializer, UserSerializer, LoginSerializer,
    ChangePasswordSerializer, AuthResponseSerializer, MessageSerializer,
)
from app.infrastructure.database.models import User


AUTH_RESPONSE_DESC = openapi.Response(
    description="Üstünlikli. **refresh** (token)-i täze access token almak üçin, "
                "**access** bolsa API soraglarynda Authorization header-de ulanyň.",
    schema=AuthResponseSerializer(),
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Üstünlikli hasap döredildi. Access token 1 gün, refresh token 7 gün güýjünli.",
                schema=AuthResponseSerializer(),
            ),
            400: openapi.Response(description="Nädogry maglumat. Eger username/email eýýäm bar bolsa ýa-da parol tizlikli bolsa."),
        },
        operation_description=(
            "Täze ulanyjy hasabyny döredýır. "
            "Kabul edilmeli meýdanlar: username, email, first_name (at), last_name (familiýa), phone, password we region (etrap). "
            "Sorag Jezasy: access (1 gün) we refresh (7 gün) token berilýär. "
            "Access token bilen gizli endpoint-lere giriş amala aşyrylýar."
        ),
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Üstünlikli giriş. Access we refresh token berilýär.",
                schema=AuthResponseSerializer(),
            ),
            400: openapi.Response(description="Ulanyjy ady ýa-da parol ýalňyş. Ulanyjy tapylmady ýa-da parol gabat gelmedi."),
        },
        operation_description=(
            "Ulanyjy ady we parol bilen ulgama girer. "
            "Dogry maglumat berilse access (1 gün) we refresh (7 gün) token berilýär. "
            "Bu token bilen şahsy maglumatlar, testler, abuna we tölegler bilen işlemek üçin ulanylýar."
        ),
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description="Parol üstünlikli üýtgedildi."),
            400: openapi.Response(description="Nädogry maglumat. Täze parollary birme-bir däl ýa-da häzirki parol ýalňyş."),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş. Authorization header-da access token gerek."),
        },
        operation_description=(
            "Ulanyjy öz parolyny üýtgetmek üçin ulanylýar. "
            "Häzirki parol, täze parol we täze parolyň tassyklamasy hökmany. "
            "Diňe hasaba giren (tokenly) ulanyjylar ulyp biler."
        ),
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {'current_password': ['Ýalňyş parol.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Parol üstünlikli üýtgedildi.'})
