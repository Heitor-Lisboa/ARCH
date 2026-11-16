from django.urls import path
from . import views

urlpatterns = [
    path('', views.usuarios, name='usuarios'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('novo/', views.usuario_novo, name='usuario_novo'),
    path('<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('<int:pk>/excluir/', views.usuario_excluir, name='usuario_excluir'),
]