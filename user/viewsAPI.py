from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.db import IntegrityError, transaction

from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Profile, Seguidor, User
from .forms import AuthenticationForm
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    ProfileSerializer, PasswordResetRequestSerializer
)

def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: openapi.Response("Usuário registrado", UserSerializer)},
        operation_description="Registra usuário e retorna JWT (access + refresh)."
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        Profile.objects.create(user=user)

        tokens = generate_tokens_for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        form = AuthenticationForm(request=request, data=request.data)

        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        user = form.get_user()

        login(request, user)

        tokens = generate_tokens_for_user(user)

        return Response({
            "tokens": tokens,
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Invalida o refresh token e finaliza a sessão JWT."
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            logout(request)
            return Response({"message": "Logout realizado."}, status=status.HTTP_200_OK)

        except Exception:
            return Response({"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.profile

    @swagger_auto_schema(
        operation_description="Obtém ou atualiza o perfil do usuário autenticado."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response({"error": "Senha atual incorreta."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)

class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        form = PasswordResetForm(data=request.data)

        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                email_template_name="user/email/resetar_senha_email.txt",
                html_email_template_name="user/email/resetar_senha_email.html",
                subject_template_name="user/email/resetar_senha_assunto.txt",
                extra_email_context={"APP_NAME": getattr(settings, "APP_NAME", "BookCLUB")},
            )
            return Response({"message": "E-mail enviado."}, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class SeguirUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Verifica se o usuário logado já está seguindo outro usuário.
        """
        usuario = get_object_or_404(User, pk=user_id)

        if usuario == request.user:
            return Response({"seguindo": False})

        seguindo = Seguidor.objects.filter(
            usuario=request.user,
            seguindo=usuario
        ).exists()

        return Response({"seguindo": seguindo})

    def post(self, request, user_id):
        """
        Segue o usuário. Se já segue, retorna seguindo=True sem duplicar.
        """
        usuario = get_object_or_404(User, pk=user_id)

        if usuario == request.user:
            return Response({"erro": "Você não pode seguir a si mesmo."}, status=400)

        try:
            seguidor, created = Seguidor.objects.get_or_create(
                usuario=request.user,
                seguindo=usuario
            )
            return Response({"message": "seguido", "seguindo": True})
        except IntegrityError:
            # Caso de duplicidade ou outro erro
            return Response({"message": "erro ao seguir"}, status=400)

    def delete(self, request, user_id):
        """
        Deixa de seguir o usuário.
        """
        usuario = get_object_or_404(User, pk=user_id)

        Seguidor.objects.filter(
            usuario=request.user,
            seguindo=usuario
        ).delete()

        return Response({"message": "unfollowed", "seguindo": False})
