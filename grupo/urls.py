from django.urls import path
from .viewsAPI import (GrupoListCreateView, GrupoDetailView, GrupoMembrosListView, AddMembroView, RemoveMembroView)
from . import views

urlpatterns = [
    path("", GrupoListCreateView.as_view(), name="grupo-list"),
    path("<int:pk>/", GrupoDetailView.as_view(), name="grupo-detail"),

    # membros
    path("<int:grupo_id>/membros/", GrupoMembrosListView.as_view(), name="grupo-membros"),
    path("<int:grupo_id>/membros/add/", AddMembroView.as_view(), name="add-membro"),
    path("<int:grupo_id>/membros/remove/<int:usuario_id>/", RemoveMembroView.as_view(), name="remove-membro"),

    path("criar/", views.criar_grupo, name="criar_grupo"),
    path("membros/selecionar/", views.selecionar_membros, name="selecionar_membros"),
   path("chats/", views.chats_ajax, name="chats"),
   path("grupo/<int:pk>/", views.grupo_detail, name="grupo_detail"),
   path("chat/<int:topico_id>/", views.chat_detail, name="chat_detail"),

]
