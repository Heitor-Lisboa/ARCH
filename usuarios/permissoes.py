"""Quem pode fazer o quê. Para mudar uma regra, edite só o dicionário PERMISSOES.

Letras: B = Bolsista, C = Coordenador, A = Usuário autorizado (conforme o diagrama de classes do PDF).
Superusuário (criado com createsuperuser) conta sempre como Coordenador.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Perfil

PERMISSOES = {
    'gerenciar_itens': 'BCA',         # cadastrar, editar e remover itens e categorias
    'registrar_movimentacao': 'BC',   # empréstimos e devoluções
    'gerenciar_usuarios': 'C',        # cadastrar, editar e remover usuários
}


def tipo_do_usuario(user):
    if user.is_superuser:
        return Perfil.COORDENADOR
    try:
        return user.perfil.tipo
    except Perfil.DoesNotExist:
        return Perfil.AUTORIZADO  # usuário criado antes do sistema de tipos


def nome_do_tipo(user):
    return dict(Perfil.TIPOS)[tipo_do_usuario(user)]


def pode(user, permissao):
    return user.is_authenticated and tipo_do_usuario(user) in PERMISSOES[permissao]


def exige(permissao):
    """Decorador: exige login e a permissão indicada."""
    def decorador(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not pode(request.user, permissao):
                messages.error(request, 'Você não tem permissão para fazer isso.')
                return redirect('home')
            return view(request, *args, **kwargs)
        return login_required(login_url='login')(wrapper)
    return decorador