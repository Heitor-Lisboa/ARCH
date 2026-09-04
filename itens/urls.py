from django.urls import path
from itens.views import index

urlpatterns = [
    path('', index),
]