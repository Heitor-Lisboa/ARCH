from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Historico, Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'matricula')
    list_filter = ('tipo',)


@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'acao', 'descricao')
    list_filter = ('acao',)
    search_fields = ('descricao', 'usuario__username')