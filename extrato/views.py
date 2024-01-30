import os
from io import BytesIO
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from weasyprint import HTML
from perfil.models import Categoria, Conta
from extrato.models import Valores
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all()
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')

        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)

        if tipo == 'E':
            conta.valor += int(valor)
        else:
            conta.valor -= int(valor)

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
        return redirect('/extrato/novo_valor')


@login_required
def view_extrato(request):
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
        elif periodo_get == 'more_than_30':
            valores = valores.filter(data__lt=hoje - timezone.timedelta(days=30))

    return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias})


def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    path_output = BytesIO()

    template_render = render_to_string(path_template, {'valores': valores, 'contas': contas, 'categorias': categorias})
    HTML(string=template_render).write_pdf(path_output)

    # Volte o ponteiro pro início do arquivo
    path_output.seek(0)

    # FileResponse -> para o usuário baixar o arquivo
    return FileResponse(path_output, filename="extrato.pdf")
