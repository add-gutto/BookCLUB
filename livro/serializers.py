# app/serializers.py
from rest_framework import serializers
from .models import Livro
from grupo.models import Topico

class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = "__all__"


class TopicoSerializer(serializers.ModelSerializer):
    livro = LivroSerializer(read_only=True)

    class Meta:
        model = Topico
        fields = "__all__"
