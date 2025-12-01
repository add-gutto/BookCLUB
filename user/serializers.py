from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import Profile, User

# ------------------------------------------------------------
# SERIALIZER DE USUÁRIO BÁSICO
# ------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    total_resenhas = serializers.IntegerField(read_only=True)
    total_seguidores = serializers.IntegerField(read_only=True)
    total_seguindo = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "total_resenhas", "total_seguidores", "total_seguindo"]


# ------------------------------------------------------------
# SERIALIZER DE PERFIL
# ------------------------------------------------------------
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    profile_picture = serializers.ImageField(max_length=None, use_url=False, required=False, allow_null=True)
    thumbnail = serializers.ImageField(max_length=None, use_url=False, required=False, allow_null=True)

    total_resenhas = serializers.IntegerField(read_only=True)
    total_seguidores = serializers.IntegerField(read_only=True)
    total_seguindo = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id", "name", "bio", "profile_picture", "thumbnail",
            "user", "username", "total_resenhas", "total_seguidores", "total_seguindo"
        ]


# ------------------------------------------------------------
# REGISTRO
# ------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "name"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            name=validated_data.get("name"),
            password=validated_data.get("password"),
        )
        return user


# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Usuário ou senha inválidos.")
        data["user"] = user
        return data


# ------------------------------------------------------------
# ALTERAÇÃO DE SENHA
# ------------------------------------------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A nova senha deve ter pelo menos 8 caracteres.")
        return value


# ------------------------------------------------------------
# RESET DE SENHA (REQUEST)
# ------------------------------------------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Nenhum usuário encontrado com este e-mail.")
        return value


# ------------------------------------------------------------
# RESET DE SENHA (CONFIRM)
# ------------------------------------------------------------
class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Token inválido ou usuário inexistente.")

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("Token inválido ou expirado.")

        data["user"] = user
        return data
