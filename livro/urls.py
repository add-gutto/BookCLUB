from django.urls import path
from . import views

app_name = "livro"

urlpatterns = [
    path("buscar/<int:grupo_id>/", views.buscar_livro_pagina,
         name="buscar_livro_pagina"),
    path("api/buscar-livros/", views.buscar_livros_api, name="buscar_livros_api"),
    path("api/criar-topico/<int:grupo_id>/",
         views.criar_topico_com_livro, name="criar_topico_com_livro"),
]
