from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Livro
from grupo.models import Grupo, Topico
from .serializers import TopicoSerializer
from .external.google_books import buscar_livros_google

# Página para buscar livros e criar tópico


@login_required
def buscar_livro_pagina(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    return render(request, "livro/buscarLivro.html", {"grupo": grupo})

# API que retorna livros da Google Books


@api_view(["GET"])
@permission_classes([AllowAny])
def buscar_livros_api(request):
    q = request.GET.get("q")
    if not q:
        return Response({"erro": "Parâmetro 'q' é obrigatório."}, status=400)
    resultados = buscar_livros_google(q)
    return Response(resultados)

# API que cria tópico usando livro


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def criar_topico_com_livro(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    livro_dados = request.data.get("livro")
    if not livro_dados or not livro_dados.get("identificador_api"):
        return Response({"erro": "Livro precisa de identificador_api."}, status=400)

    # ⚡ get_or_create pelo identificador_api
    livro, created = Livro.objects.get_or_create(
        identificador_api=livro_dados["identificador_api"],
        defaults={
            "titulo": livro_dados.get("titulo"),
            "autor": livro_dados.get("autor"),
            "descricao": livro_dados.get("descricao"),
            "capa": livro_dados.get("capa"),
            "ano_publicacao": livro_dados.get("ano_publicacao"),
        }
    )

    # ⛔ VERIFICAÇÃO IMPORTANTE
    # Evita criar tópico duplicado no mesmo grupo
    if Topico.objects.filter(grupo=grupo, livro=livro).exists():
        return Response(
            {"erro": "Este livro já possui um tópico neste grupo."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cria o tópico com o nome do livro
    topico = Topico.objects.create(
        grupo=grupo,
        nome=livro.titulo,
        criado_por=request.user,
        livro=livro
    )

    serializer = TopicoSerializer(topico)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
