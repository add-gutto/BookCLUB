# grupos/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Grupo, GrupoMembro, Topico, Mensagem
from user.models import User
from .forms import GrupoForm



@login_required
def selecionar_membros(request):
    usuarios = request.user.seguindo.all().values_list('seguindo', flat=True)
    usuarios = User.objects.filter(pk__in=usuarios)

    if request.method == "POST":
        membros_ids = request.POST.getlist("membros")  
        request.session['membros_selecionados'] = membros_ids  
        return redirect("criar_grupo")  

    return render(request, "grupo/membros.html", {"usuarios": usuarios})

@login_required
def criar_grupo(request):
    membros_ids = request.session.get('membros_selecionados', [])

    if request.method == "POST":
        form = GrupoForm(request.POST, request.FILES)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.administrador = request.user
            grupo.save()
            GrupoMembro.objects.create(grupo=grupo, usuario=request.user)

            for usuario_id in membros_ids:
                usuario = User.objects.get(pk=usuario_id)
                GrupoMembro.objects.create(grupo=grupo, usuario=usuario)

            Topico.objects.create(
                grupo=grupo,
                nome="Tópico Geral",
                criado_por=request.user,
                livro=None
            )
            if 'membros_selecionados' in request.session:
                del request.session['membros_selecionados']

            return redirect("grupo_detail", pk=grupo.id)

    else:
        form = GrupoForm()

    return render(request, "grupo/form.html", {"form": form, "button_text": "Criar Grupo"})

@login_required
def grupo_detail(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    return render(request, "grupo/grupo_detail.html", {"grupo": grupo})

@login_required
def editar_grupo(request, pk):
    grupo = get_object_or_404(Grupo, id=pk)

    if request.user != grupo.administrador:
        return redirect("home")  

    if request.method == "POST":
        form = GrupoForm(request.POST, request.FILES, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect("grupo_detail", pk=grupo.id)  
    else:
        form = GrupoForm(instance=grupo)

    return render(request, "grupo/form.html", {
        "form": form,
        "grupo": grupo,
        "button_text": "Editar Grupo"
    })

@login_required
def sair_grupo(request, pk):
    grupo = get_object_or_404(Grupo, id=pk)

    if request.user == grupo.administrador:
        novo_membro_info = grupo.membros_info.exclude(usuario=request.user).first()
        
        if novo_membro_info:
            grupo.administrador = novo_membro_info.usuario
            grupo.save()
        else:
            grupo.delete()
            return redirect("home")

        GrupoMembro.objects.filter(grupo=grupo, usuario=request.user).delete()

        return redirect("home")

    membro = get_object_or_404(GrupoMembro, grupo=grupo, usuario=request.user)
    membro.delete()
    return redirect("home")


@login_required
def adicionar_membros(request, pk):
    grupo = get_object_or_404(Grupo, id=pk)

    if request.user != grupo.administrador:
        return redirect("grupo_detail", pk=pk)

    seguindo_ids = request.user.seguindo.all().values_list('seguindo', flat=True)
    usuarios = User.objects.filter(pk__in=seguindo_ids).exclude(
        id__in=grupo.membros_info.values_list("usuario_id", flat=True)
    )

    if request.method == "POST":
        membros_ids = request.POST.getlist("membros")
        membros_ids = [uid for uid in membros_ids if uid in map(str, seguindo_ids)]

        for usuario_id in membros_ids:
            usuario = User.objects.get(pk=usuario_id)
            GrupoMembro.objects.get_or_create(grupo=grupo, usuario=usuario)

        return redirect("grupo_detail", pk=grupo.id)

    return render(request, "grupo/membros.html", {
        "usuarios": usuarios,
        "grupo": grupo,
    })

@login_required
def search(request):
    return render(request, "search.html")

@login_required
def search_ajax(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', 'grupo')

    results = []

    if query:
        # Buscar GRUPOS
        if tipo == 'grupo':
            grupos = Grupo.objects.filter(privado=False, nome__icontains=query)[:20]
            for g in grupos:
                results.append({
                    'id': g.id,
                    'nome': g.nome,
                    'imagem': g.imagem.url if g.imagem else '/static/template/img/placeholder.jpg',
                    'tipo': 'grupo'
                })

        # Buscar USUÁRIOS
        elif tipo == 'usuario':
            usuarios = User.objects.filter(username__icontains=query)[:20]
            for u in usuarios:
                foto = '/static/template/img/placeholder.jpg'
                if hasattr(u, "profile") and u.profile.profile_picture:
                    foto = u.profile.profile_picture.url

                results.append({
                    'id': u.id,
                    'nome': u.profile.name if hasattr(u, "profile") else u.username,
                    'username': u.username,
                    'imagem': foto,
                    'tipo': 'usuario'
                })

    return JsonResponse({'results': results})

