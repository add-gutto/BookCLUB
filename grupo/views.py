# grupos/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Grupo, GrupoMembro, Topico, Mensagem
from user.models import User
from .forms import GrupoForm



@login_required
def selecionar_membros(request):
    # lista de usuários que eu sigo
    usuarios = request.user.seguindo.all().values_list('seguindo', flat=True)
    usuarios = User.objects.filter(pk__in=usuarios)

    if request.method == "POST":
        membros_ids = request.POST.getlist("membros")  # IDs dos usuários selecionados
        request.session['membros_selecionados'] = membros_ids  # salva na sessão
        return redirect("criar_grupo")  # vai pra view de criar grupo

    return render(request, "grupos/membros.html", {"usuarios": usuarios})

@login_required
def criar_grupo(request):
    membros_ids = request.session.get('membros_selecionados', [])

    if request.method == "POST":
        form = GrupoForm(request.POST, request.FILES)

        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.administrador = request.user
            grupo.save()

            # adiciona o usuário administrador
            GrupoMembro.objects.create(grupo=grupo, usuario=request.user)

            # adiciona os membros selecionados
            for usuario_id in membros_ids:
                usuario = User.objects.get(pk=usuario_id)
                GrupoMembro.objects.create(grupo=grupo, usuario=usuario)

            # cria o tópico geral automaticamente
            Topico.objects.create(
                grupo=grupo,
                nome="Tópico Geral",
                criado_por=request.user,
                livro=None
            )

            # limpa a sessão
            if 'membros_selecionados' in request.session:
                del request.session['membros_selecionados']

            return redirect("grupo_detail", pk=grupo.pk)

    else:
        form = GrupoForm()

    return render(request, "grupos/form.html", {"form": form, "button_text": "Criar Grupo"})

@login_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    # Apenas o administrador pode editar
    if request.user != grupo.administrador:
        return redirect("home")  # ou mostrar erro 403

    if request.method == "POST":
        form = GrupoForm(request.POST, request.FILES, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect("dashboard")  # ou a página do grupo
    else:
        form = GrupoForm(instance=grupo)

    return render(request, "grupo/form.html", {
        "form": form,
        "grupo": grupo,
        "button_text": "Editar Grupo"
    })

@login_required
def chats_ajax(request):
    print("Chats AJAX chamado")  # para debug no console do Django
    chats = request.user.grupos_participando.all()  # pega os grupos/chats do usuário
    return render(request, "chats/partials/chats_lista.html", {"chats": chats})

def grupo_detail(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    return render(request, "chats/grupo_detail.html", {"grupo": grupo})

def chat_detail(request, topico_id):
    chat = get_object_or_404(Topico, id=topico_id)
    mensagens = chat.mensagens.all()

    return render(request, "chats/topico_detail.html", {
        "chat": chat,
        "mensagens": mensagens
    })