from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Item(models.Model):
    STATUS = [
        ('ESTOQUE', 'Em Estoque'),
        ('BAIXO', 'Baixo Estoque'),
        ('REPARO', 'Necessita de Reparo'),
        ('ESGOTADO', 'Esgotado'),
    ]

    codigo = models.CharField(max_length=30, unique=True, blank=True, help_text='Deixe em branco para gerar automaticamente.')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    quantidade_total = models.IntegerField(default=1)
    # Calculado: total - o que está emprestado (saídas - entradas)
    quantidade_disponivel = models.IntegerField(default=1, editable=False)

    status = models.CharField(max_length=10, choices=STATUS, default='ESTOQUE')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="itens")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    def _soma(self, tipo, ignorar=None):
        movs = self.movimentacoes.filter(tipo=tipo)
        if ignorar:
            movs = movs.exclude(pk=ignorar)
        return movs.aggregate(s=Sum('quantidade'))['s'] or 0

    @property
    def emprestado(self):
        """Unidades que saíram e ainda não voltaram."""
        return self._soma('S') - self._soma('E') if self.pk else 0

    def disponivel_sem(self, mov_pk=None):
        """Quanto estaria livre se a saída `mov_pk` não existisse (usado ao editar um empréstimo)."""
        return self.quantidade_total - (self._soma('S', mov_pk) - self._soma('E'))

    def save(self, *args, **kwargs):
        self.quantidade_disponivel = max(self.quantidade_total - self.emprestado, 0)

        if self.quantidade_disponivel == 0:
            self.status = 'ESGOTADO'
        elif self.status == 'ESGOTADO':
            self.status = 'ESTOQUE'
        super().save(*args, **kwargs)

        if not self.codigo:  # código automático: ITM-0001, ITM-0002...
            self.codigo = f'ITM-{self.pk:04d}'
            super().save(update_fields=['codigo'])


class Movimentacao(models.Model):
    ENTRADA = 'E'
    SAIDA = 'S'
    TIPO_CHOICES = [(ENTRADA, 'Entrada'), (SAIDA, 'Saída')]
    PRAZO_CHOICES = [(5, '5 dias'), (7, '7 dias'), (10, '10 dias'), (15, '15 dias'), (30, '30 dias')]

    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='movimentacoes')
    quantidade = models.PositiveIntegerField()
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)

    # Saída (empréstimo)
    emprestado_a = models.CharField(max_length=100, blank=True, help_text='Obrigatório em saídas.')
    prazo_dias = models.PositiveIntegerField(
        choices=PRAZO_CHOICES, null=True, blank=True,
        help_text='Obrigatório em saídas. A devolução prevista é calculada a partir do dia do empréstimo.'
    )
    data_prevista = models.DateField(null=True, blank=True, editable=False)

    # Entrada (devolução): qual empréstimo está sendo devolvido
    emprestimo = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.PROTECT,
        related_name='devolucoes', limit_choices_to={'tipo': 'S'},
        verbose_name='empréstimo devolvido',
        help_text='Obrigatório em entradas.'
    )

    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.item.nome} ({self.quantidade})"

    @property
    def pendente(self):
        if self.tipo != self.SAIDA:
            return 0
        devolvido = self.devolucoes.aggregate(s=Sum('quantidade'))['s'] or 0
        return max(self.quantidade - devolvido, 0)

    @property
    def dias_atraso(self):
        if self.data_prevista and self.pendente > 0:
            return max((timezone.localdate() - self.data_prevista).days, 0)
        return 0

    @property
    def situacao(self):
        if self.tipo != self.SAIDA:
            return ''
        if self.pendente == 0:
            return 'Devolvido'
        return 'Atrasado' if self.dias_atraso > 0 else 'Em dia'

    @property
    def pessoa(self):
        return self.emprestado_a or (self.emprestimo.emprestado_a if self.emprestimo_id else '')

    def clean(self):
        if not self.item_id or self.quantidade is None:
            return

        if self.tipo == self.SAIDA:
            if not self.emprestado_a:
                raise ValidationError({'emprestado_a': 'Informe quem está levando o item.'})
            if not self.prazo_dias:
                raise ValidationError({'prazo_dias': 'Escolha o prazo de devolução.'})

            livre = self.item.disponivel_sem(self.pk)
            if self.quantidade > livre:
                raise ValidationError({'quantidade': f'Só há {max(livre, 0)} unidade(s) disponível(is).'})

            if self.pk:
                devolvido = self.devolucoes.aggregate(s=Sum('quantidade'))['s'] or 0
                if self.quantidade < devolvido:
                    raise ValidationError({'quantidade': f'{devolvido} unidade(s) deste empréstimo já foram devolvidas.'})

        elif self.tipo == self.ENTRADA:
            if not self.emprestimo_id:
                raise ValidationError({'emprestimo': 'Escolha o empréstimo que está sendo devolvido.'})
            if self.emprestimo.item_id != self.item_id:
                raise ValidationError({'emprestimo': 'Esse empréstimo é de outro item.'})

            ja_devolvido = self.emprestimo.devolucoes.exclude(pk=self.pk).aggregate(s=Sum('quantidade'))['s'] or 0
            falta = self.emprestimo.quantidade - ja_devolvido
            if self.quantidade > falta:
                raise ValidationError({'quantidade': f'Só faltam {falta} unidade(s) para devolver neste empréstimo.'})

    def save(self, *args, **kwargs):
        if self.tipo == self.SAIDA and self.prazo_dias:
            base = timezone.localtime(self.data_hora).date() if self.data_hora else timezone.localdate()
            self.data_prevista = base + timedelta(days=self.prazo_dias)
        else:
            self.data_prevista = None
        super().save(*args, **kwargs)


# Qualquer criação, edição ou exclusão de movimentação recalcula o estoque do item.
@receiver([post_save, post_delete], sender=Movimentacao)
def recalcular_estoque(sender, instance, **kwargs):
    Item.objects.get(pk=instance.item_id).save()