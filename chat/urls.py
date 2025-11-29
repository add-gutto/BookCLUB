from django.urls import path
from . import views
from .viewsAPI import chats_ajax_api

urlpatterns = [
   path("chats/", views.chats_ajax, name="chats"),
   path("chat/<int:topico_id>/", views.chat_detail, name="chat_detail"),
   path('api/chats/', chats_ajax_api, name='chats_ajax_api'),

]