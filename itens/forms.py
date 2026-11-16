from django import forms
from django.core.exceptions import ValidationError

from .models import Categoria, Item, Movimentacao


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {'descricao': forms.Textarea(attrs={'rows': 3})}


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nome', 'codigo', 'categoria', 'descricao', 'quantidade_total', 'status']
        labels = {'quantidade_total': 'Quantidade total'}
        widgets = {'descricao': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = 'Selecione a categoria'

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip()
        if '/' in codigo:
            raise ValidationError('O código não pode ter a barra "/".')
        return codigo

    def clean_quantidade_total(self):
        total = self.cleaned_data['quantidade_total']
        if total < 0:
            raise ValidationError('A quantidade não pode ser negativa.')
        if self.instance.pk and total < self.instance.emprestado:
            raise ValidationError(
                f'{self.instance.emprestado} unidade(s) estão emprestadas; o total não pode ser menor que isso.')
        return total

    def clean(self):
        dados = super().clean()
        nome, categoria = dados.get('nome'), dados.get('categoria')
        if nome and categoria:  # UC03/E2: item já cadastrado
            iguais = Item.objects.filter(nome__iexact=nome.strip(), categoria=categoria)
            if self.instance.pk:
                iguais = iguais.exclude(pk=self.instance.pk)
            if iguais.exists():
                self.add_error('nome', 'Já existe um item com esse nome nessa categoria. Edite o existente.')
        return dados


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['tipo', 'item', 'quantidade', 'emprestado_a', 'prazo_dias', 'emprestimo']
        labels = {'emprestado_a': 'Emprestado a (nome ou matrícula)', 'prazo_dias': 'Prazo de devolução'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipo'].choices = [('S', 'Saída (empréstimo)'), ('E', 'Entrada (devolução)')]
        self.fields['tipo'].initial = 'S'
        self.fields['item'].required = False
        self.fields['item'].empty_label = 'Selecione o item'
        self.fields['item'].queryset = Item.objects.order_by('nome')
        self.fields['prazo_dias'].initial = 7
        self.fields['emprestimo'].help_text = ''

        # Só aparecem empréstimos que ainda têm algo a devolver
        abertos = [m.pk for m in Movimentacao.objects.filter(tipo='S') if m.pendente > 0]
        if self.instance.pk and self.instance.emprestimo_id:
            abertos.append(self.instance.emprestimo_id)
        campo = self.fields['emprestimo']
        campo.queryset = Movimentacao.objects.filter(pk__in=abertos).select_related('item')
        campo.empty_label = 'Selecione o empréstimo'
        campo.label_from_instance = lambda m: f'{m.item.nome} - {m.emprestado_a} - pendente: {m.pendente}'

        # Ao editar, tipo, item e empréstimo ficam travados
        if self.instance.pk:
            for nome in ('tipo', 'item', 'emprestimo'):
                self.fields[nome].disabled = True

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        if quantidade < 1:
            raise ValidationError('A quantidade deve ser pelo menos 1.')
        return quantidade

    def clean(self):
        dados = super().clean()
        tipo = dados.get('tipo')

        if tipo == 'S':
            dados['emprestimo'] = None
            if not dados.get('item'):
                self.add_error('item', 'Escolha o item.')
        elif tipo == 'E':
            dados['emprestado_a'] = ''
            dados['prazo_dias'] = None
            if dados.get('emprestimo'):
                dados['item'] = dados['emprestimo'].item  # a devolução herda o item do empréstimo
            else:
                self.add_error('emprestimo', 'Escolha o empréstimo que está sendo devolvido.')
        return dados