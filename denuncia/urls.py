from django.urls import path
from . import views

app_name = 'denuncia'

urlpatterns = [
    path('criar/', views.criar_denuncia, name='criar'),
    path('', views.lista_denuncias, name='lista'),
    path('ajax/buscar/', views.ajax_busca_denuncias, name='ajax_buscar'),
    path('<int:pk>/', views.detalhe_denuncia, name='detalhe'),
    path('<int:pk>/atualizar-status/', views.atualizar_status, name='atualizar_status'),
]
