import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from .models import Item, Movimentacao


def _itens_filtrados(query):
    itens = Item.objects.select_related('categoria').all()
    if query:
        itens = itens.filter(nome__icontains=query)
    return itens


@login_required(login_url='login')
def estoque(request):
    query = request.GET.get('q', '').strip()
    itens = _itens_filtrados(query)
    return render(request, 'itens/itens.html', {'itens': itens, 'query': query})


@login_required(login_url='login')
def exportar_estoque(request):
    query = request.GET.get('q', '').strip()
    itens = _itens_filtrados(query)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="estoque_labmaker.csv"'
    response.write('﻿')  # BOM para abrir acentuação corretamente no Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Código', 'Nome', 'Categoria', 'Qtd. disponível', 'Qtd. total', 'Status'])

    for item in itens:
        writer.writerow([
            item.codigo,
            item.nome,
            item.categoria.nome,
            item.quantidade_disponivel,
            item.quantidade_total,
            item.get_status_display(),
        ])

    return response


@login_required(login_url='login')
def movimentacoes(request):
    q = request.GET.get('q', '').strip()
    campo = request.GET.get('campo', 'todos')
    ordem = request.GET.get('ordem', 'recentes')

    registros = Movimentacao.objects.select_related(
        'item', 'item__categoria', 'emprestimo'
    )

    if q:
        filtros = {
            'item': Q(item__nome__icontains=q),
            'categoria': Q(item__categoria__nome__icontains=q),
            'pessoa': Q(emprestado_a__icontains=q) | Q(emprestimo__emprestado_a__icontains=q),
        }
        if campo in filtros:
            registros = registros.filter(filtros[campo])
        else:
            registros = registros.filter(filtros['item'] | filtros['categoria'] | filtros['pessoa'])

    registros = registros.order_by('data_hora' if ordem == 'antigas' else '-data_hora')

    return render(request, 'itens/movimentacoes.html', {
        'movimentacoes': registros,
        'q': q, 'campo': campo, 'ordem': ordem,
    })