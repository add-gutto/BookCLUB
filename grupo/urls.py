from django.urls import path
from . import views
from . import viewsAPI
from .viewsAPI import SearchAPIView, MensagemListAPIView
urlpatterns = [
    # criar grupo
    path("membros/selecionar/", views.selecionar_membros, name="selecionar_membros"),
    path("criar/", views.criar_grupo, name="criar_grupo"),
    path("<int:pk>/", views.grupo_detail, name="grupo_detail"),
    path("editar/<int:pk>/", views.editar_grupo, name="editar_grupo"),
    path("sair/<int:pk>/", views.sair_grupo, name="sair_grupo"),
    path("add/membros/<int:pk>/", views.adicionar_membros, name="adicionar_membros"),
    path("search/", views.search, name="search"),
    path("search/ajax/", views.search_ajax, name="search_ajax"),
    path("entrar/<int:id>/", views.entrar_no_grupo, name="entrar_no_grupo"),


    path('api/search/', SearchAPIView.as_view(), name='search_api'),
    path("api/grupos/<int:id>/topicos/", viewsAPI.listar_topicos_grupo),
    path("api/membros/selecionar/", viewsAPI.selecionar_membros),
    path("api/criar/", viewsAPI.criar_grupo, name="api_criar_grupo"),
    path("api/editar/<int:id>/", viewsAPI.editar_grupo, name="api_editar_grupo"),
    path("api/sair/<int:id>/", viewsAPI.sair_grupo, name="api_sair_grupo"),
    path("api/add/membros/<int:id>/", viewsAPI.adicionar_membros, name="api_adicionar_membros"),
    path('api/mensagens/<int:id>/', MensagemListAPIView.as_view(), name='mensagens-list'),
    path("api/entrar/<int:id>/", viewsAPI.api_entrar_no_grupo, name="api_entrar_grupo"),


]
