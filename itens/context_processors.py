from django.utils import timezone

from .models import Movimentacao


def notificacoes(request):
    """Empréstimos vencidos e ainda não devolvidos; somem quando a entrada é registrada."""
    if not request.user.is_authenticated:
        return {}

    saidas = Movimentacao.objects.filter(
        tipo=Movimentacao.SAIDA, data_prevista__lt=timezone.localdate()
    ).select_related('item').order_by('data_prevista')
    atrasados = [m for m in saidas if m.pendente > 0]
    return {'notificacoes_atraso': atrasados, 'notificacoes_total': len(atrasados)}