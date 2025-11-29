from rest_framework import serializers
from .models import Grupo, GrupoMembro, Topico
from user.serializers import ProfileSerializer


class CreateGrupoSerializer(serializers.ModelSerializer):
    membros = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Grupo
        fields = ["nome", "descricao", "privado", "imagem", "membros"]



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
