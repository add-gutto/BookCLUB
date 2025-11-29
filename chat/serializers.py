from rest_framework import serializers
from grupo.models import Grupo

class GrupoSerializer(serializers.ModelSerializer):
    imagem = serializers.ImageField(
        max_length=None,
        use_url=False,  # Retorna só o path relativo
        required=False,
        allow_null=True
    )

    class Meta:
        model = Grupo
        fields = ['id', 'nome', 'descricao', 'privado', 'imagem']
