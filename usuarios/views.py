from django.shortcuts import render

def autorizados(request):
    return render(request, 'usuarios/usuarios.html')