from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('autorizados')
        else:
            return render(request, 'usuarios/login.html', {
                'erro': 'Usuário ou senha inválidos.'
            })

    return render(request, 'usuarios/login.html')


def autorizados(request):
    return render(request, 'usuarios/usuarios.html')