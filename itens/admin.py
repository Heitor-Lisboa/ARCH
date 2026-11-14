from django.contrib import admin

from .models import Categoria, Item, Movimentacao


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criada_em')
    search_fields = ('nome',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'categoria', 'quantidade_disponivel', 'quantidade_total', 'status')
    list_filter = ('categoria', 'status')
    search_fields = ('codigo', 'nome')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'tipo', 'item', 'quantidade', 'emprestado_a', 'data_prevista')
    list_filter = ('tipo', 'item__categoria')
    search_fields = ('item__nome', 'emprestado_a')