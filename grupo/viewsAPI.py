from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Grupo, GrupoMembro, Topico
from .serializers import (
    GrupoSerializer,
    GrupoDetailSerializer,
    GrupoMembroSerializer
)


# ---------------------------
# LISTAR E CRIAR GRUPOS
# ---------------------------

class GrupoListCreateView(generics.ListCreateAPIView):
    queryset = Grupo.objects.all().order_by("-data_criacao")
    serializer_class = GrupoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        grupo = serializer.save(administrador=self.request.user)

        GrupoMembro.objects.create(
            grupo=grupo,
            usuario=self.request.user
        )
        
        Topico.objects.create(
            grupo=grupo,
            nome="Tópico Geral",
            criado_por=self.request.user,
            livro=None      # ← sem livro relacionado
        )


# ---------------------------
# DETALHES DO GRUPO (GET, PUT, DELETE)
# ---------------------------
class GrupoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grupo.objects.all()
    serializer_class = GrupoDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        grupo = self.get_object()

        if grupo.administrador != request.user:
            return Response(
                {"detail": "Apenas o administrador pode editar o grupo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        grupo = self.get_object()

        if grupo.administrador != request.user:
            return Response(
                {"detail": "Apenas o administrador pode deletar o grupo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)


# ---------------------------
# LISTAR MEMBROS DO GRUPO
# ---------------------------
class GrupoMembrosListView(generics.ListAPIView):
    serializer_class = GrupoMembroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        grupo_id = self.kwargs["grupo_id"]
        return GrupoMembro.objects.filter(grupo_id=grupo_id).order_by("ordem")


# ---------------------------
# ADICIONAR MEMBRO AO GRUPO
# ---------------------------
class AddMembroView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, grupo_id):
        grupo = Grupo.objects.get(id=grupo_id)

        if grupo.administrador != request.user:
            return Response(
                {"detail": "Apenas o administrador pode adicionar membros."},
                status=status.HTTP_403_FORBIDDEN
            )

        usuario_id = request.data.get("usuario_id")
        if not usuario_id:
            return Response({"detail": "Informe 'usuario_id'."}, status=400)

        # impede duplicação
        if GrupoMembro.objects.filter(grupo=grupo, usuario_id=usuario_id).exists():
            return Response({"detail": "Usuário já está no grupo."}, status=400)

        membro = GrupoMembro.objects.create(
            grupo=grupo,
            usuario_id=usuario_id
        )

        return Response(
            GrupoMembroSerializer(membro).data,
            status=status.HTTP_201_CREATED
        )


# ---------------------------
# REMOVER MEMBRO DO GRUPO
# ---------------------------
class RemoveMembroView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, grupo_id, usuario_id):
        grupo = Grupo.objects.get(id=grupo_id)

        if grupo.administrador != request.user:
            return Response(
                {"detail": "Apenas o administrador pode remover membros."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            membro = GrupoMembro.objects.get(
                grupo=grupo,
                usuario_id=usuario_id
            )
        except GrupoMembro.DoesNotExist:
            return Response(
                {"detail": "Usuário não faz parte do grupo."},
                status=status.HTTP_404_NOT_FOUND
            )

        membro.delete()

        return Response({"detail": "Membro removido com sucesso."})
