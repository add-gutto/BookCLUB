from django.urls import path
from . import views
from . import viewsAPI

app_name = "livro"

urlpatterns = [
    path("buscar/<int:grupo_id>/", views.buscar_livro_pagina, name="buscar_livro_pagina"),
    path("api/buscar-livros/", views.buscar_livros_api, name="buscar_livros_api"),
    path("api/criar-topico/<int:grupo_id>/",  views.criar_topico_com_livro, name="criar_topico_com_livro"),
    path('<str:identificador_api>/', views.livro_detail, name='livro_detail'),

    #Resenhas
    path('resenha/<int:id>/', views.resenha_form, name='resenha_form'),

    #API
    path("api/resenha/<int:id>/", viewsAPI.resenhas, name="resenhas"),
    path("api/create/resenha/<int:livro_id>/", viewsAPI.create_resenha, name="create_resenha"),

]
