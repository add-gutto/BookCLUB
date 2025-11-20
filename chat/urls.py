from django.urls import path
from . import views

urlpatterns = [
   path("chats/", views.chats_ajax, name="chats"),
   path("chat/<int:topico_id>/", views.chat_detail, name="chat_detail"),

]