from django.shortcuts import render
from .models import Item  # 1. Importe o model Item


def estoque(request):
  # 2. Crie a variável 'itens' buscando os dados no banco
  itens = Item.objects.all()

  # 3. Agora a variável 'itens' existe e pode ser passada para o template
  return render(request, 'itens/itens.html', {'itens': itens})