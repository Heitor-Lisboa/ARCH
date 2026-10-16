from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Item(models.Model):
    # Escolhas (CHOICES) seguindo a padronização das tuplas do slide
    STATUS = [
        ('ESTOQUE', 'Em Estoque'),
        ('BAIXO', 'Baixo Estoque'),
        ('REPARO', 'Necessita de Reparo'),
        ('ESGOTADO', 'Esgotado'),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    # Quantidades
    quantidade_total = models.IntegerField(default=1)
    quantidade_disponivel = models.IntegerField(default=1)
    
    # Campo de escolhas (CHOICES) idêntico ao campo prioridade/status do slide
    status = models.CharField(max_length=10, choices=STATUS, default='ESTOQUE')
    
    # Relacionamento Foreign Key com a Categoria (protegendo exclusão acidental)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="itens"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"