# app/urls.py
from django.urls import path
from .views import (
    buscar_livros_api,
    criar_topico_com_livro
)

urlpatterns = [
    path("buscar/", buscar_livros_api, name="buscar_livros_api"),
    path("topicos/criar-com-livro/<int:grupo_id>/", criar_topico_com_livro, name="criar_topico_com_livro"),
]
