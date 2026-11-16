from .permissoes import PERMISSOES, nome_do_tipo, pode


def permissoes(request):
    """Deixa `perm.gerenciar_itens` etc. disponíveis em todos os templates."""
    if not request.user.is_authenticated:
        return {}
    return {
        'perm': {nome: pode(request.user, nome) for nome in PERMISSOES},
        'tipo_usuario': nome_do_tipo(request.user),
    }