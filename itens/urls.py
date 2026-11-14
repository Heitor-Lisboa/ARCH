from django.urls import path
from . import views

urlpatterns = [
    path('', views.estoque, name="estoque"),
    path('exportar/', views.exportar_estoque, name="exportar_estoque"),
    path('movimentacoes/', views.movimentacoes, name="movimentacoes"),
]