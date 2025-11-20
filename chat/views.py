from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from grupo.models import Topico
# Create your views here.

@login_required
def chats_ajax(request):
    print("Chats AJAX chamado")  # para debug no console do Django
    chats = request.user.grupos_participando.all()  # pega os grupos/chats do usuário
    return render(request, "chats/partials/chats_lista.html", {"chats": chats})

def chat_detail(request, topico_id):
    chat = get_object_or_404(Topico, id=topico_id)
    mensagens = chat.mensagens.all()

    return render(request, "chats/topico_detail.html", {
        "chat": chat,
        "mensagens": mensagens
    })