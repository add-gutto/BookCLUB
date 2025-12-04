# app/serializers.py
from rest_framework import serializers
from .models import Livro, Resenha
from grupo.models import Topico
from user.serializers import ProfileSerializer
    


class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = "__all__"

class TopicoSerializer(serializers.ModelSerializer):
    livro = LivroSerializer(read_only=True)

    class Meta:
        model = Topico
        fields = "__all__"



class ResenhaSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()
    livro = LivroSerializer(read_only=True)

    class Meta:
        model = Resenha
        fields = "__all__"

    def get_usuario(self, obj):
        profile = obj.usuario.profile  
        return ProfileSerializer(profile).data


class CreateResenhaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resenha
        fields = "__all__"
