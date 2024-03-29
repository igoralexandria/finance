from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import render, redirect
from extrato.models import Valores
from perfil.models import Categoria, Conta
from .models import ContaPagar, ContaPaga
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    else:
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            dia_pagamento=dia_pagamento
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
        return redirect('/contas/definir_contas')


@login_required
def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day

    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)

    contas_proximas_vencimento = contas.filter(dia_pagamento__lte=DIA_ATUAL + 5).filter(
        dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)

    restantes = contas.exclude (id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(
        id__in=contas_proximas_vencimento)

    return render(request, 'ver_contas.html',
                  {'contas_vencidas': contas_vencidas, 'contas_proximas_vencimento': contas_proximas_vencimento,
                   'restantes': restantes, 'contas_pagas': contas_pagas})


def pagar_conta(request, conta_id):
    conta = get_object_or_404(ContaPagar, pk=conta_id)

    try:
        conta_paga = ContaPaga.objects.create(
            conta=conta,
            data_pagamento=datetime.now()
        )
    except Exception as e:
        return HttpResponseBadRequest("Erro ao pagar a conta.")

    messages.success(request, 'Conta paga com sucesso!')
    return redirect('ver_contas')


@login_required
def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total += v.valor

        dados[categoria.categoria] = total
    # Por outro método mais curto
    '''for categoria in categorias:
        dados[categoria.categoria] = Valores.objects.filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum']'''

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})


@login_required
def definir_mensais(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    periodo_get = request.GET.get('periodo')

    valores = Valores.objects.all()

    if conta_get:
        valores = valores.filter(conta__id=conta_get)
    if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)

    # Adicione a lógica para filtrar por período
    if periodo_get:
        hoje = timezone.now().date()
        if periodo_get == '7':
            valores = valores.filter(data__gte=hoje - timezone.timedelta(days=7))
        elif periodo_get == '15':
            valores = valores.filter(data__gte=hoje - timezone.timedelta(days=15))
        elif periodo_get == '30':
            valores = valores.filter(data__gte=hoje - timezone.timedelta(days=30))

    return render(request, 'definir_mensais.html', {'valores': valores, 'contas': contas, 'categorias': categorias})
