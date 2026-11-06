from django.urls import path
from . import views

urlpatterns = [
    path('', views.autorizados, name="autorizados"),
    path('login/', views.login_view, name='login'),
]