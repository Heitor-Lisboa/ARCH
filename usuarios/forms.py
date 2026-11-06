from django import forms

class LoginForms (forms.Form):
    nome = forms.CharField(label='Nome')
    email = forms.CharField(label='E-mail')
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(label='Confimar senha', widget=forms.PasswordInput)

def clean (self):
    cleaned_data = super().clean()
    senha = cleaned_data.get('senha')
    confirmar_senha = cleaned_data.get('confirmar senha')

    if senha != confirmar_senha:
        raise forms.ValidationError('As senhas não coincidem')
    
    return cleaned_data
    
