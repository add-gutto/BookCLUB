from django.urls import path
from . import views

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

]
