from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from grupo.models import Topico, Mensagem
# Create your views here.

@login_required
def chats_ajax(request):
    print("Chats AJAX chamado")  

    chats_data = []

    for chat in request.user.grupos_participando.all():
        mensagens_nao_lidas = Mensagem.objects.filter(
            topico__grupo=chat
        ).exclude(
            lidos_por=request.user
        ).count()

        chats_data.append({
            "chat": chat,
            "mensagens_nao_lidas_count": mensagens_nao_lidas
        })

    return render(request, "chats/partials/chats_lista.html", {
        "chats_data": chats_data
    })

@login_required
def chat_detail(request, topico_id):
    chat = get_object_or_404(Topico, id=topico_id)
    mensagens = chat.mensagens.all()

    return render(request, "chats/topico_detail.html", {
        "chat": chat,
        "mensagens": mensagens
    })