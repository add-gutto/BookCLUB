from rest_framework import serializers
from grupo.models import Grupo
from user.models import User

class GrupoSerializer(serializers.ModelSerializer):
    imagem = serializers.ImageField(
        max_length=None,
        use_url=False,  
        required=False,
        allow_null=True
    )

    membros = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Grupo
        fields = ['id', 'nome', 'descricao', 'privado', 'imagem', 'membros']
