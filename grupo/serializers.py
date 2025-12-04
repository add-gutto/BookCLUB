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
        # Se vier membros[] (caso do multipart do Flutter)
        if "membros[]" in data:
            data = data.copy()                        # QueryDict é imutável
            membros_lista = data.getlist("membros[]") # pega cada valor
            data.setlist("membros", membros_lista)    # converte para "membros"
        
        return super().to_internal_value(data)

    def create(self, validated_data):
        membros_data = validated_data.pop('membros', [])
        grupo = Grupo.objects.create(**validated_data)

        for user_id in membros_data:
            try:
                usuario = User.objects.get(pk=user_id)
                GrupoMembro.objects.create(grupo=grupo, usuario=usuario)
            except User.DoesNotExist:
                pass  

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
    imagem = serializers.ImageField(
        max_length=None,
        use_url=False,  # só envia o caminho relativo
        required=False,
        allow_null=True
    )

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
