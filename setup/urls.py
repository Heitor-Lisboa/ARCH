"""
URL configuration for setup project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('itens/', include('itens.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('', views.home, name='home'),
]