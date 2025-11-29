from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests

from .models import Livro, Resenha
from grupo.models import Grupo, Topico
from .serializers import TopicoSerializer
from .external.google_books import buscar_livros_google

# Página para buscar livros e criar tópico


@login_required
def buscar_livro_pagina(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    return render(request, "livro/search-livro.html", {"grupo": grupo})


@api_view(["GET"])
@permission_classes([AllowAny])
def buscar_livros_api(request):
    q = request.GET.get("q")
    if not q:
        return Response({"erro": "Parâmetro 'q' é obrigatório."}, status=400)
    resultados = buscar_livros_google(q)
    return Response(resultados)


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

    if Topico.objects.filter(grupo=grupo, livro=livro).exists():
        return Response(
            {"erro": "Este livro já possui um tópico neste grupo."},
            status=status.HTTP_400_BAD_REQUEST
        )

    topico = Topico.objects.create(
        grupo=grupo,
        nome=livro.titulo,
        criado_por=request.user,
        livro=livro
    )

    serializer = TopicoSerializer(topico)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@login_required
def livro_detail(request, identificador_api):
    # Exemplo: buscar via API do Google Books
    url = f'https://www.googleapis.com/books/v1/volumes/{identificador_api}'
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        livro = {
            "titulo": data['volumeInfo'].get('title', ''),
            "autor": ', '.join(data['volumeInfo'].get('authors', [])),
            "sinopse": data['volumeInfo'].get('description', ''),
            "paginas": data['volumeInfo'].get('pageCount', ''),
            "capa": data['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
            "identificador_api": identificador_api
        }
    else:
        livro = {
            "titulo": "Livro não encontrado",
            "autor": "",
            "sinopse": "",
            "paginas": "",
            "capa": "/static/template/img/placeholder.jpg",
            "identificador_api": identificador_api
        }

    return render(request, 'livro/sinopse.html', {'livro': livro})

@login_required
def resenha_form(request, id):
    livro = get_object_or_404(Livro, id=id)

    resenha_existente = Resenha.objects.filter(
        usuario=request.user, livro=livro
    ).first()

    if request.method == "POST" and not resenha_existente:
        nota = int(request.POST.get("nota") or 0)
        comentario = request.POST.get("comentario", "")

        Resenha.objects.create(
            usuario=request.user,
            livro=livro,
            nota=nota,
            comentario=comentario
        )

        return redirect("livro:livro_detail", identificador_api=livro.identificador_api)

    return render(request, "livro/resenha_form.html", {
        "livro": livro,
        "resenha_existente": resenha_existente,
        "stars": range(1, 6),  # 1..5
    })
