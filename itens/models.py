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

    codigo = models.CharField(max_length=30, unique=True)
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

    def save(self, *args, **kwargs):
        if self.pk:
            total = lambda t: self.movimentacoes.filter(tipo=t).aggregate(s=Sum('quantidade'))['s'] or 0
            emprestado = total('S') - total('E')
            self.quantidade_disponivel = max(self.quantidade_total - emprestado, 0)
        else:
            self.quantidade_disponivel = self.quantidade_total

        if self.quantidade_disponivel == 0:
            self.status = 'ESGOTADO'
        elif self.status == 'ESGOTADO':
            self.status = 'ESTOQUE'
        super().save(*args, **kwargs)


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
        if not self.item_id:
            return
        if self.tipo == self.SAIDA:
            if not self.emprestado_a:
                raise ValidationError({'emprestado_a': 'Informe quem está levando o item.'})
            if not self.prazo_dias:
                raise ValidationError({'prazo_dias': 'Escolha o prazo de devolução.'})
            if not self.pk and self.quantidade > self.item.quantidade_disponivel:
                raise ValidationError({
                    'quantidade': f'Só há {self.item.quantidade_disponivel} unidade(s) disponível(is).'
                })
        elif self.tipo == self.ENTRADA:
            if not self.emprestimo_id:
                raise ValidationError({'emprestimo': 'Escolha o empréstimo que está sendo devolvido.'})
            if self.emprestimo.item_id != self.item_id:
                raise ValidationError({'emprestimo': 'Esse empréstimo é de outro item.'})

    def save(self, *args, **kwargs):
        if self.tipo == self.SAIDA and self.prazo_dias:
            base = timezone.localtime(self.data_hora).date() if self.data_hora else timezone.localdate()
            self.data_prevista = base + timedelta(days=self.prazo_dias)
        super().save(*args, **kwargs)


# Qualquer criação, edição ou exclusão de movimentação recalcula o estoque do item.
@receiver([post_save, post_delete], sender=Movimentacao)
def recalcular_estoque(sender, instance, **kwargs):
    Item.objects.get(pk=instance.item_id).save()