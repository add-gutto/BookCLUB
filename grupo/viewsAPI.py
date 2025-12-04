from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import views, status, generics, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Grupo, GrupoMembro, Topico, Mensagem
from user.models import User, Profile

from chat.serializers import GrupoSerializer
from user.serializers import ProfileSerializer
from .serializers import TopicoSerializer, CreateGrupoSerializer, MensagemSerializer



# ============================================================
# BUSCA (GRUPOS / USUÁRIOS)
# ============================================================

class SearchAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        tipo = request.GET.get('tipo', 'grupo')
        results = []

        if query:
            if tipo == 'grupo':
                grupos = Grupo.objects.filter(
                    privado=False,
                    nome__icontains=query
                )[:20]

                serializer = GrupoSerializer(
                    grupos, many=True,
                    context={'request': request}
                )
                results = serializer.data

            elif tipo == 'usuario':
                usuarios = Profile.objects.filter(
                    user__username__icontains=query
                ).exclude(
                    user=request.user  # 👈 REMOVE O USUÁRIO LOGADO
                )[:20]

                serializer = ProfileSerializer(
                    usuarios, many=True,
                    context={'request': request}
                )
                results = serializer.data

        return Response({'results': results}, status=status.HTTP_200_OK)



# ============================================================
# LISTAR TÓPICOS DO GRUPO
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_topicos_grupo(request, id):
    try:
        grupo = Grupo.objects.get(id=id)
    except Grupo.DoesNotExist:
        return Response({"detail": "Grupo não encontrado."}, status=404)

    topicos = grupo.topicos.all().order_by('criado_em')
    serializer = TopicoSerializer(topicos, many=True)
    return Response(serializer.data, status=200)


# ============================================================
# LISTAR MEMBROS QUE O USUÁRIO SEGUE
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def selecionar_membros(request):
    seguindo_ids = request.user.seguindo.all().values_list("seguindo", flat=True)
    profiles = Profile.objects.filter(user__id__in=seguindo_ids)
    serializer = ProfileSerializer(profiles, many=True)

    return Response(serializer.data)


# ============================================================
# CRIAR GRUPO
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def criar_grupo(request):
    serializer = CreateGrupoSerializer(data=request.data)

    if serializer.is_valid():
        grupo = serializer.save(administrador=request.user)
        GrupoMembro.objects.get_or_create(grupo=grupo, usuario=request.user)

        Topico.objects.create(
            grupo=grupo,
            nome="Tópico Geral",
            criado_por=request.user,
        )
        return Response(GrupoSerializer(grupo).data, status=201)

    # LOG AQUI 👇
    print("📦 Request Data:", request.data)
    print("❌ Erros do serializer:", serializer.errors)

    return Response(serializer.errors, status=400)



# ============================================================
# EDITAR GRUPO
# ============================================================

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def editar_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    if request.user != grupo.administrador:
        return Response({"detail": "Apenas o administrador pode editar."}, status=403)

    serializer = CreateGrupoSerializer(grupo, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(GrupoSerializer(grupo).data)

    return Response(serializer.errors, status=400)


# ============================================================
# SAIR DO GRUPO
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
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


# ============================================================
# ADICIONAR MEMBROS
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def adicionar_membros(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    if request.user != grupo.administrador:
        return Response(
            {"detail": "Apenas o administrador pode adicionar membros."},
            status=403
        )

    membros_ids = request.data.get("membros", [])

    if not isinstance(membros_ids, list):
        return Response({"detail": "Envie uma lista de IDs de usuários."}, status=400)

    adicionados = 0

    for uid in membros_ids:
        usuario = User.objects.filter(id=uid).first()
        if usuario:
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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_entrar_no_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    # Se já for membro, retorna mensagem
    if GrupoMembro.objects.filter(grupo=grupo, usuario=request.user).exists():
        return Response(
            {"detail": "Usuário já é membro do grupo."},
            status=status.HTTP_200_OK
        )

    # Criar vínculo
    GrupoMembro.objects.create(grupo=grupo, usuario=request.user)

    return Response(
        {"detail": "Usuário entrou no grupo com sucesso.", "grupo_id": grupo.id},
        status=status.HTTP_201_CREATED
    )

class MensagemListAPIView(generics.ListAPIView):
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        topico_id = self.kwargs.get('id')
        return Mensagem.objects.filter(topico_id=topico_id).order_by('criado_em')
