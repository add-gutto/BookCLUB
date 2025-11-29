from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from grupo.models import Grupo, Mensagem
from .serializers import GrupoSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chats_ajax_api(request):
    grupos = request.user.grupos_participando.all()
    grupos_data = []

    for grupo in grupos:
        mensagens_nao_lidas = Mensagem.objects.filter(
            topico__grupo=grupo
        ).exclude(
            lidos_por=request.user
        ).count()

        grupo_serializer = GrupoSerializer(grupo, context={'request': request})
        data = grupo_serializer.data
        data['mensagens_nao_lidas_count'] = mensagens_nao_lidas  # adicionado manualmente
        grupos_data.append(data)

    return Response({"chats": grupos_data})

