from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import UsuarioForm
from .models import registrar
from .permissoes import exige, nome_do_tipo

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    proximo = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is None:
            # UC02/E2: conta inativa tem mensagem própria
            conta = User.objects.filter(username__iexact=username).first()
            if conta and not conta.is_active and conta.check_password(password):
                erro = 'Esta conta está inativa. Procure um coordenador.'
            else:
                erro = 'Usuário ou senha inválidos.'
            return render(request, 'usuarios/login.html', {'erro': erro, 'proximo': proximo})

        login(request, user)
        if not request.POST.get('lembrar'):
            request.session.set_expiry(0)  # sessão termina ao fechar o navegador
        registrar(user, 'LOGIN', 'Entrou no sistema.')

        if proximo and url_has_allowed_host_and_scheme(
                proximo, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(proximo)
        return redirect('home')

    return render(request, 'usuarios/login.html', {'proximo': proximo})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def usuarios(request):
    lista = User.objects.select_related('perfil').order_by('first_name', 'username')
    linhas = [(u, nome_do_tipo(u)) for u in lista]
    return render(request, 'usuarios/usuarios.html', {'linhas': linhas})


@exige('gerenciar_usuarios')
def usuario_novo(request):
    form = UsuarioForm(request.POST or None, logado=request.user)
    if request.method == 'POST' and form.is_valid():
        user = form.salvar()
        registrar(request.user, 'CADASTRO', f'Usuário {user.username} cadastrado.')
        messages.success(request, f'Usuário {user.username} cadastrado.')
        return redirect('usuarios')
    return render(request, 'form.html', {
        'form': form, 'titulo': 'Cadastrar usuário', 'voltar': reverse('usuarios')})


@exige('gerenciar_usuarios')
def usuario_editar(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UsuarioForm(request.POST or None, usuario=user, logado=request.user)
    if request.method == 'POST' and form.is_valid():
        user = form.salvar()
        registrar(request.user, 'ATUALIZACAO', f'Usuário {user.username} atualizado.')
        messages.success(request, f'Usuário {user.username} atualizado.')
        return redirect('usuarios')
    return render(request, 'form.html', {
        'form': form, 'titulo': f'Editar usuário: {user.username}', 'voltar': reverse('usuarios')})


@exige('gerenciar_usuarios')
def usuario_excluir(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'Você não pode excluir a própria conta.')
        return redirect('usuarios')

    nome = f'usuário {user.username}'
    if request.method == 'POST':
        user.delete()
        registrar(request.user, 'REMOCAO', f'Removeu {nome}.')
        messages.success(request, f'Removido: {nome}.')
        return redirect('usuarios')
    return render(request, 'confirmar.html', {'nome': nome, 'voltar': reverse('usuarios')})