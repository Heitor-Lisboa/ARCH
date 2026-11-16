import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from usuarios.models import registrar
from usuarios.permissoes import exige

from .forms import CategoriaForm, ItemForm, MovimentacaoForm
from .models import Categoria, Item, Movimentacao


# ---------- funções de apoio (servem para itens, categorias e movimentações) ----------

def _cadastro(request, form, titulo, voltar, acao, texto):
    """Mostra o formulário; se for válido salva, registra no histórico e volta para a lista."""
    if request.method == 'POST' and form.is_valid():
        objeto = form.save()
        registrar(request.user, acao, texto(objeto))
        messages.success(request, texto(objeto))
        return redirect(voltar)
    return render(request, 'form.html', {'form': form, 'titulo': titulo, 'voltar': reverse(voltar)})


def _excluir(request, objeto, nome, voltar, motivo):
    """GET pede confirmação; POST exclui. Se houver registros ligados ao objeto, explica o motivo."""
    if request.method == 'POST':
        try:
            objeto.delete()
        except ProtectedError:
            messages.error(request, motivo)
        else:
            registrar(request.user, 'REMOCAO', f'Removeu {nome}.')
            messages.success(request, f'Removido: {nome}.')
        return redirect(voltar)
    return render(request, 'confirmar.html', {'nome': nome, 'voltar': reverse(voltar)})


# ---------- estoque ----------

def _itens_filtrados(query, categoria, campo='todos'):
    itens = Item.objects.select_related('categoria').order_by('nome')
    if query:
        filtros = {
            'nome': Q(nome__icontains=query),
            'id': Q(codigo__icontains=query),
        }
        itens = itens.filter(filtros.get(campo) or (filtros['nome'] | filtros['id']))
    if categoria.isdigit():
        itens = itens.filter(categoria_id=categoria)
    return itens


@login_required(login_url='login')
def estoque(request):
    query = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    campo = request.GET.get('campo', 'todos')
    return render(request, 'itens/itens.html', {
        'itens': _itens_filtrados(query, categoria, campo),
        'query': query,
        'campo': campo,
        'categorias': Categoria.objects.order_by('nome'),
        'categoria_selecionada': categoria,
    })


@login_required(login_url='login')
def exportar_estoque(request):
    itens = _itens_filtrados(request.GET.get('q', '').strip(), request.GET.get('categoria', ''),
                             request.GET.get('campo', 'todos'))

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="estoque_labmaker.csv"'
    response.write('﻿')  # BOM para o Excel abrir a acentuação corretamente

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Código', 'Nome', 'Categoria', 'Qtd. disponível', 'Qtd. total', 'Status'])
    for item in itens:
        writer.writerow([item.codigo, item.nome, item.categoria.nome,
                         item.quantidade_disponivel, item.quantidade_total, item.get_status_display()])
    return response


@exige('gerenciar_itens')
def item_novo(request):
    return _cadastro(request, ItemForm(request.POST or None), 'Cadastrar item', 'estoque',
                     'CADASTRO', lambda o: f'Item "{o.nome}" cadastrado.')


@exige('gerenciar_itens')
def item_editar(request, codigo):
    item = get_object_or_404(Item, codigo=codigo)
    return _cadastro(request, ItemForm(request.POST or None, instance=item), f'Editar item: {item.nome}',
                     'estoque', 'ATUALIZACAO', lambda o: f'Item "{o.nome}" atualizado.')


@exige('gerenciar_itens')
def item_excluir(request, codigo):
    item = get_object_or_404(Item, codigo=codigo)
    return _excluir(request, item, f'item "{item.nome}"', 'estoque',
                    'Este item tem movimentações registradas e não pode ser excluído (o histórico é preservado).')


# ---------- categorias ----------

@login_required(login_url='login')
def categorias(request):
    lista = Categoria.objects.annotate(total=Count('itens')).order_by('nome')
    return render(request, 'itens/categorias.html', {'categorias': lista})


@exige('gerenciar_itens')
def categoria_nova(request):
    return _cadastro(request, CategoriaForm(request.POST or None), 'Cadastrar categoria', 'categorias',
                     'CADASTRO', lambda o: f'Categoria "{o.nome}" cadastrada.')


@exige('gerenciar_itens')
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    return _cadastro(request, CategoriaForm(request.POST or None, instance=categoria),
                     f'Editar categoria: {categoria.nome}', 'categorias',
                     'ATUALIZACAO', lambda o: f'Categoria "{o.nome}" atualizada.')


@exige('gerenciar_itens')
def categoria_excluir(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    return _excluir(request, categoria, f'categoria "{categoria.nome}"', 'categorias',
                    'Esta categoria ainda tem itens. Mova ou exclua os itens antes.')


# ---------- movimentações ----------

@login_required(login_url='login')
def movimentacoes(request):
    q = request.GET.get('q', '').strip()
    campo = request.GET.get('campo', 'todos')
    ordem = request.GET.get('ordem', 'recentes')

    registros = Movimentacao.objects.select_related('item', 'item__categoria', 'emprestimo')

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
        'movimentacoes': registros, 'q': q, 'campo': campo, 'ordem': ordem,
    })


@exige('registrar_movimentacao')
def movimentacao_nova(request):
    inicial = {}
    devolver = request.GET.get('devolver', '')  # atalho "Devolver" da lista de movimentações
    if devolver.isdigit():
        saida = Movimentacao.objects.filter(pk=devolver, tipo='S').first()
        if saida and saida.pendente > 0:
            inicial = {'tipo': 'E', 'emprestimo': saida.pk, 'quantidade': saida.pendente}

    form = MovimentacaoForm(request.POST or None, initial=inicial)
    if request.method == 'POST' and form.is_valid():
        mov = form.save()
        if mov.tipo == 'S':
            texto = f'{mov.quantidade}x {mov.item.nome} emprestado(s) a {mov.emprestado_a} (prazo de {mov.prazo_dias} dias).'
            registrar(request.user, 'EMPRESTIMO', texto)
        else:
            texto = f'{mov.quantidade}x {mov.item.nome} devolvido(s) por {mov.pessoa}.'
            registrar(request.user, 'DEVOLUCAO', texto)
        messages.success(request, texto)
        return redirect('movimentacoes')
    return render(request, 'form.html', {
        'form': form, 'titulo': 'Cadastrar movimentação', 'voltar': reverse('movimentacoes')})


@exige('registrar_movimentacao')
def movimentacao_editar(request, pk):
    mov = get_object_or_404(Movimentacao, pk=pk)
    return _cadastro(request, MovimentacaoForm(request.POST or None, instance=mov),
                     f'Editar movimentação: {mov.item.nome}', 'movimentacoes', 'ATUALIZACAO',
                     lambda o: f'Movimentação de {o.quantidade}x {o.item.nome} atualizada.')


@exige('registrar_movimentacao')
def movimentacao_excluir(request, pk):
    mov = get_object_or_404(Movimentacao, pk=pk)
    return _excluir(request, mov, f'movimentação de {mov.quantidade}x {mov.item.nome}', 'movimentacoes',
                    'Este empréstimo já tem devoluções registradas. Exclua as devoluções primeiro.')