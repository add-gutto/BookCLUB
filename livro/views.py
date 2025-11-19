from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Livro
from grupo.models import Grupo, Topico
from .serializers import LivroSerializer, TopicoSerializer
from .external.google_books import buscar_livros_google


# 1️⃣ Buscar livros na API Google Books
@api_view(["GET"])
@permission_classes([AllowAny])  # <<< AGORA QUALQUER UM PODE ACESSAR
def buscar_livros_api(request):
    q = request.GET.get("q")

    if not q:
        return Response({"erro": "Parâmetro 'q' é obrigatório."}, status=400)

    resultados = buscar_livros_google(q)
    return Response(resultados)


# 2️⃣ Criar Tópico já vinculado a um livro da API externa
@api_view(["POST"])
def criar_topico_com_livro(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    livro_dados = request.data.get("livro")
    if not livro_dados:
        return Response({"erro": "Campo 'livro' é obrigatório."}, status=400)

    livro, _ = Livro.objects.get_or_create(
        titulo=livro_dados.get("titulo"),
        autor=livro_dados.get("autor"),
        ano_publicacao=livro_dados.get("ano_publicacao"),
    )

    topico = Topico.objects.create(
        grupo=grupo,
        nome=request.data.get("nome"),
        descricao=request.data.get("descricao"),
        criado_por=request.user,
        livro=livro,
    )

    return Response(TopicoSerializer(topico).data, status=status.HTTP_201_CREATED)
