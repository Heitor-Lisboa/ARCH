from django.urls import path
from . import views

urlpatterns = [
    path('', views.estoque, name='estoque'),
    path('exportar/', views.exportar_estoque, name='exportar_estoque'),
    path('novo/', views.item_novo, name='item_novo'),
    path('<str:codigo>/editar/', views.item_editar, name='item_editar'),
    path('<str:codigo>/excluir/', views.item_excluir, name='item_excluir'),

    path('categorias/', views.categorias, name='categorias'),
    path('categorias/nova/', views.categoria_nova, name='categoria_nova'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/excluir/', views.categoria_excluir, name='categoria_excluir'),

    path('movimentacoes/', views.movimentacoes, name='movimentacoes'),
    path('movimentacoes/nova/', views.movimentacao_nova, name='movimentacao_nova'),
    path('movimentacoes/<int:pk>/editar/', views.movimentacao_editar, name='movimentacao_editar'),
    path('movimentacoes/<int:pk>/excluir/', views.movimentacao_excluir, name='movimentacao_excluir'),
]