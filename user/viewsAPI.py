from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordResetForm
from rest_framework import generics, status, permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction


from .models import Profile
from .forms import AuthenticationForm
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    ProfileSerializer, PasswordResetRequestSerializer
)


# ----------------------------
# REGISTRO
# ----------------------------
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: openapi.Response("Usuário criado com sucesso.", UserSerializer)},
        operation_description="Cria um novo usuário, o perfil associado e retorna o token de autenticação."
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Profile.objects.create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

# ----------------------------
# LOGIN
# ----------------------------
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response("Login bem-sucedido.", UserSerializer),
            400: "Credenciais inválidas."
        },
        operation_description="Autentica o usuário via nome de usuário ou e-mail e retorna o token de acesso."
    )
    def post(self, request):
        form = AuthenticationForm(request=request, data=request.data)

        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        user = form.get_user()
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)


# ----------------------------
# LOGOUT
# ----------------------------
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Response("Logout realizado com sucesso.")},
        operation_description="Finaliza a sessão e remove o token de autenticação do usuário logado."
    )
    def post(self, request):
        # Deleta o token para invalidar o login
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logout realizado com sucesso."}, status=status.HTTP_200_OK)


# ----------------------------
# PERFIL (visualizar e editar)
# ----------------------------
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    Retorna ou atualiza o perfil do usuário autenticado.
    Permite upload de imagem via multipart/form-data.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.profile

    @swagger_auto_schema(
        operation_description="Obtém ou atualiza o perfil do usuário autenticado (upload de imagem permitido via multipart/form-data)."
    )
    def put(self, request, *args, **kwargs):
        """Atualiza o perfil (PUT completo)"""
        return super().update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Atualiza parcialmente o perfil (PATCH)"""
        return super().partial_update(request, *args, **kwargs)


# ----------------------------
# ALTERAR SENHA
# ----------------------------
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("Senha alterada com sucesso."),
            400: "Senha atual incorreta."
        },
        operation_description="Permite ao usuário autenticado alterar sua senha, informando a senha atual e a nova senha."
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Senha atual incorreta."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)


# ----------------------------
# RESET DE SENHA (envia e-mail)
# ----------------------------
class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response("E-mail de redefinição de senha enviado com sucesso."),
            400: "E-mail não encontrado ou inválido."
        },
        operation_description="Envia um e-mail com o link de redefinição de senha, caso o e-mail informado exista no sistema."
    )
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
            return Response(
                {"message": "E-mail de redefinição de senha enviado com sucesso."},
                status=status.HTTP_200_OK
            )

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
