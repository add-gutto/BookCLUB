# viewsAPI.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import ResenhaSerializer, CreateResenhaSerializer
from .models import Resenha, Livro
from user.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resenhas(request, id):
    user = get_object_or_404(User, id=id)
    resenhas = Resenha.objects.filter(usuario=user).order_by("-id")
    serializer = ResenhaSerializer(resenhas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_resenha(request, livro_id):
    user = request.user
    livro = get_object_or_404(Livro, id=livro_id)

    # Verifica se já existe resenha desse user para esse livro
    if Resenha.objects.filter(usuario=user, livro=livro).exists():
        return Response(
            {"detail": "Você já avaliou este livro."},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data.copy()
    data["usuario"] = user.id      # usuário autenticado
    data["livro"] = livro.id       # livro informado via URL

    serializer = CreateResenhaSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)