from rest_framework import serializers
from .models import Grupo, GrupoMembro


class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = [
            "id",
            "nome",
            "descricao",
            "privado",
            "imagem",
            "data_criacao",
        ]


class GrupoDetailSerializer(serializers.ModelSerializer):
    administrador = serializers.StringRelatedField()
    quantidade_membros = serializers.SerializerMethodField()

    class Meta:
        model = Grupo
        fields = "__all__"

    def get_quantidade_membros(self, obj):
        return obj.membros.count()


class GrupoMembroSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = GrupoMembro
        fields = ["usuario", "data_entrada", "ordem"]
