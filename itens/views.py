from django.shortcuts import render

def estoque(request):
    return render(request, 'itens/itens.html')