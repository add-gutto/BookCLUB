from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db import models
from django.views.decorators.http import require_POST
from .models import Denuncia


def criar_denuncia(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        alvo_tipo = request.POST.get("alvo_tipo", "").strip()
        alvo_id = request.POST.get("alvo_id", "").strip()

        if not titulo or not descricao:
            return render(request, "denuncia/criar.html", {
                "erro": "Preencha título e descrição."
            })

        denuncia = Denuncia.objects.create(
            autor=request.user if request.user.is_authenticated else None,
            titulo=titulo,
            descricao=descricao,
            alvo_tipo=alvo_tipo,
            alvo_id=alvo_id,
            ip_origem=request.META.get("REMOTE_ADDR"),
        )
        return redirect("denuncia:lista")

    return render(request, "denuncia/criar.html")


def is_staff(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff)
def lista_denuncias(request):
    busca = request.GET.get("q", "").strip()
    status_filtro = request.GET.get("status", "").strip()

    queryset = Denuncia.objects.all()

    if busca:
        queryset = queryset.filter(
            models.Q(titulo__icontains=busca)
            | models.Q(descricao__icontains=busca)
            | models.Q(autor__username__icontains=busca)
        )

    if status_filtro:
        queryset = queryset.filter(status=status_filtro)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "denuncia/lista.html", {
        "page_obj": page_obj,
        "busca": busca,
        "status_filtro": status_filtro,
    })


@user_passes_test(is_staff)
def detalhe_denuncia(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, "denuncia/detalhe.html", {"denuncia": denuncia})


@user_passes_test(is_staff)
@require_POST
def atualizar_status(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    novo_status = request.POST.get("status")

    if novo_status not in dict(Denuncia.STATUS_CHOICES):
        return HttpResponseBadRequest("Status inválido.")

    denuncia.status = novo_status
    denuncia.save()

    return redirect("denuncia:detalhe", pk=pk)


@user_passes_test(is_staff)
def ajax_busca_denuncias(request):
    busca = request.GET.get("q", "").strip()
    status_filtro = request.GET.get("status", "").strip()
    page = int(request.GET.get("page", 1))
    por_pagina = int(request.GET.get("per_page", 15))

    queryset = Denuncia.objects.all()

    if busca:
        queryset = queryset.filter(
            models.Q(titulo__icontains=busca)
            | models.Q(descricao__icontains=busca)
            | models.Q(autor__username__icontains=busca)
        )

    if status_filtro:
        queryset = queryset.filter(status=status_filtro)

    paginator = Paginator(queryset, por_pagina)
    page_obj = paginator.get_page(page)

    resultados = [
        {
            "id": d.id,
            "titulo": d.titulo,
            "autor": d.autor.username if d.autor else "Anônimo",
            "status": d.status,
            "alvo_tipo": d.alvo_tipo,
            "alvo_id": d.alvo_id,
            "created_at": d.created_at.strftime("%d/%m/%Y %H:%M"),
        }
        for d in page_obj
    ]

    return JsonResponse({
        "pagina_atual": page_obj.number,
        "total_paginas": paginator.num_pages,
        "total_resultados": paginator.count,
        "resultados": resultados,
    })
