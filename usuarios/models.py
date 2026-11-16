from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Dados extras do usuário: tipo (RF01) e matrícula."""
    BOLSISTA = 'B'
    COORDENADOR = 'C'
    AUTORIZADO = 'A'
    TIPOS = [
        (BOLSISTA, 'Bolsista'),
        (COORDENADOR, 'Coordenador de laboratório'),
        (AUTORIZADO, 'Usuário autorizado'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=1, choices=TIPOS, default=AUTORIZADO)
    matricula = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_tipo_display()})'


class Historico(models.Model):
    """Registro de tudo que acontece no sistema (RF12)."""
    ACOES = [
        ('LOGIN', 'Login'),
        ('CADASTRO', 'Cadastro'),
        ('ATUALIZACAO', 'Atualização'),
        ('REMOCAO', 'Remoção'),
        ('EMPRESTIMO', 'Empréstimo'),
        ('DEVOLUCAO', 'Devolução'),
        ('PERDA', 'Perda'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='historico'
    )
    acao = models.CharField(max_length=15, choices=ACOES)
    descricao = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora']
        verbose_name_plural = 'histórico'

    def __str__(self):
        return f'{self.get_acao_display()}: {self.descricao}'


def registrar(usuario, acao, descricao):
    """Grava uma linha no histórico. Uso: registrar(request.user, 'CADASTRO', 'Item X cadastrado.')"""
    Historico.objects.create(
        usuario=usuario if getattr(usuario, 'is_authenticated', False) else None,
        acao=acao,
        descricao=descricao[:255],
    )