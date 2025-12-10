import json
from django.conf import settings
from rest_framework import serializers
from .models import Grupo, GrupoMembro, Topico, Mensagem
from user.serializers import ProfileSerializer
from user.models import User


class CreateGrupoSerializer(serializers.ModelSerializer):
    membros = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Grupo
        fields = ["nome", "descricao", "privado", "imagem", "membros"]

    def to_internal_value(self, data):
        data = data.copy()  # QueryDict é imutável

        # ✅ Caso Flutter Multipart: membros = "[1,2]"
        if "membros" in data:
            raw = data.get("membros")

            # Se vier como string JSON
            if isinstance(raw, str):
                try:
                    membros = json.loads(raw)  # [1,2]
                    data.setlist("membros", membros)
                except json.JSONDecodeError:
                    data.setlist("membros", [])

        return super().to_internal_value(data)

    def create(self, validated_data):
        membros_data = validated_data.pop("membros", [])
        grupo = Grupo.objects.create(**validated_data)

        GrupoMembro.objects.bulk_create([
            GrupoMembro(
                grupo=grupo,
                usuario=User.objects.get(pk=user_id)
            )
            for user_id in membros_data
            if User.objects.filter(pk=user_id).exists()
        ])

        return grupo



class TopicoSerializer(serializers.ModelSerializer):
    ultima_mensagem = serializers.SerializerMethodField()

    class Meta:
        model = Topico
        fields = [
            "id",
            "nome",
            "livro",
            "criado_em",
            "criado_por",
            "qtd_mensagens",
            "tem_spoilers",
            "ultima_mensagem",
        ]

    def get_ultima_mensagem(self, obj):
        msg = obj.ultima_mensagem()
        if not msg:
            return None
        
        return {
            "usuario": msg.usuario.username if msg.usuario else "Desconhecido",
            "conteudo": msg.conteudo,
            "criado_em": msg.criado_em,
        }

class MensagemSerializer(serializers.ModelSerializer):
    usuario_detail = ProfileSerializer(source="usuario.profile", read_only=True)

    lidos_por = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    imagem = serializers.SerializerMethodField()

    class Meta:
        model = Mensagem
        fields = [
            "id",
            "topico",
            "usuario_detail",
            "conteudo",
            "imagem",
            "capitulo",
            "is_spoiler",
            "criado_em",
            "lidos_por",
        ]
        read_only_fields = ["id", "usuario_detail", "criado_em", "lidos_por"]

    def get_imagem(self, obj):
        if not obj.imagem:
            return None
        return f"{settings.MEDIA_URL}{obj.imagem.name}"

