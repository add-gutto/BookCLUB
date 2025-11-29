# views.py
from  django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from .models import Grupo
from user.models import Profile
from chat.serializers import GrupoSerializer
from user.serializers import ProfileSerializer
from .serializers import TopicoSerializer, CreateGrupoSerializer
from rest_framework.decorators import api_view
from .models import Grupo, GrupoMembro, Topico
from user.models import User



class SearchAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        tipo = request.GET.get('tipo', 'grupo')  # 'grupo' ou 'usuario'
        results = []

        if query:
            if tipo == 'grupo':
                # Busca grupos públicos cujo nome contenha a query
                grupos = Grupo.objects.filter(privado=False, nome__icontains=query)[:20]
                serializer = GrupoSerializer(grupos, many=True, context={'request': request})
                results = serializer.data

            elif tipo == 'usuario':
                # Busca profiles cujo user.username contenha a query
                usuarios = Profile.objects.filter(user__username__icontains=query)[:20]
                serializer = ProfileSerializer(usuarios, many=True, context={'request': request})
                results = serializer.data

        return Response({'results': results}, status=status.HTTP_200_OK)

@login_required
@api_view(["GET"])
def listar_topicos_grupo(request, id):
    try:
        grupo = Grupo.objects.get(id=id)
    except Grupo.DoesNotExist:
        return Response({"detail": "Grupo não encontrado."}, status=404)

    topicos = grupo.topicos.all().order_by('criado_em')
    serializer = TopicoSerializer(topicos, many=True)

    return Response(serializer.data, status=200)

@api_view(["GET"])
@login_required
def selecionar_membros(request):
    seguindo_ids = request.user.seguindo.all().values_list("seguindo", flat=True)
    profiles = Profile.objects.filter(user__id__in=seguindo_ids)
    serializer = ProfileSerializer(profiles, many=True)

    return Response(serializer.data)

@api_view(["POST"])
@login_required
def criar_grupo(request):
    serializer = CreateGrupoSerializer(data=request.data)

    if serializer.is_valid():
        # Cria o grupo com o administrador atual
        grupo = serializer.save(administrador=request.user)

        # Adiciona o próprio administrador como membro
        GrupoMembro.objects.create(grupo=grupo, usuario=request.user)

        # Adiciona os membros passados na requisição
        membros_ids = request.data.get("membros", [])
        for uid in membros_ids:
            try:
                usuario = User.objects.get(pk=uid)
                GrupoMembro.objects.get_or_create(grupo=grupo, usuario=usuario)
            except User.DoesNotExist:
                continue

        # Cria um tópico inicial padrão
        Topico.objects.create(
            grupo=grupo,
            nome="Tópico Geral",
            criado_por=request.user,
        )

        return Response(GrupoSerializer(grupo).data, status=201)

    return Response(serializer.errors, status=400)

@api_view(["PUT"])
@login_required
def editar_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    if request.user != grupo.administrador:
        return Response({"detail": "Apenas o administrador pode editar."}, status=403)

    serializer = CreateGrupoSerializer(grupo, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(GrupoSerializer(grupo).data)

    return Response(serializer.errors, status=400)


@api_view(["POST"])
@login_required
def sair_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    if request.user == grupo.administrador:
        novo_admin = grupo.membros_info.exclude(usuario=request.user).first()

        if novo_admin:
            grupo.administrador = novo_admin.usuario
            grupo.save()
        else:
            grupo.delete()
            return Response({"detail": "Grupo excluído pois não restaram membros."})

    GrupoMembro.objects.filter(grupo=grupo, usuario=request.user).delete()

    return Response({"detail": "Removido do grupo com sucesso."})

@api_view(["POST"])
@login_required
def adicionar_membros(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    # Apenas o administrador pode adicionar membros
    if request.user != grupo.administrador:
        return Response(
            {"detail": "Apenas o administrador pode adicionar membros."},
            status=403
        )

    # IDs recebidos: [1, 5, 9]
    membros_ids = request.data.get("membros", [])

    if not isinstance(membros_ids, list):
        return Response(
            {"detail": "Envie uma lista de IDs de usuários."},
            status=400
        )

    adicionados = 0

    for uid in membros_ids:
        usuario = User.objects.filter(id=uid).first()

        if usuario:
            # Evita duplicação automaticamente
            _, created = GrupoMembro.objects.get_or_create(
                grupo=grupo,
                usuario=usuario
            )
            if created:
                adicionados += 1

    return Response({
        "detail": f"{adicionados} membro(s) adicionado(s) ao grupo.",
        "grupo": GrupoSerializer(grupo).data
    })
