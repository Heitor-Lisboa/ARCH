from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Perfil
from .permissoes import tipo_do_usuario

User = get_user_model()


class UsuarioForm(forms.Form):
    """Cadastro e edição de usuário. Na edição, deixe a senha em branco para mantê-la."""
    nome = forms.CharField(label='Nome', max_length=150)
    username = forms.CharField(label='Login', max_length=150)
    email = forms.EmailField(label='E-mail')
    matricula = forms.CharField(label='Matrícula', max_length=30, required=False)
    tipo = forms.ChoiceField(label='Tipo de usuário', choices=Perfil.TIPOS)
    ativo = forms.BooleanField(label='Conta ativa', required=False, initial=True)
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput, required=False)
    confirmar_senha = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput, required=False)

    def __init__(self, *args, usuario=None, logado=None, **kwargs):
        self.usuario = usuario
        if usuario:
            kwargs['initial'] = {
                'nome': usuario.first_name,
                'username': usuario.username,
                'email': usuario.email,
                'matricula': getattr(getattr(usuario, 'perfil', None), 'matricula', ''),
                'tipo': tipo_do_usuario(usuario),
                'ativo': usuario.is_active,
            }
        super().__init__(*args, **kwargs)

        self.fields['senha'].required = usuario is None
        self.fields['confirmar_senha'].required = usuario is None
        if usuario:
            self.fields['senha'].help_text = 'Deixe em branco para manter a senha atual.'
        # Ninguém pode tirar o próprio acesso
        if usuario and logado and usuario.pk == logado.pk:
            self.fields['ativo'].disabled = True
            self.fields['tipo'].disabled = True

    def _ja_existe(self, **filtro):
        achados = User.objects.filter(**filtro)
        if self.usuario:
            achados = achados.exclude(pk=self.usuario.pk)
        return achados.exists()

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if self._ja_existe(username__iexact=username):
            raise ValidationError('Já existe um usuário com esse login.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if self._ja_existe(email__iexact=email):
            raise ValidationError('Já existe um usuário com esse e-mail.')
        return email

    def clean(self):
        dados = super().clean()
        senha = dados.get('senha')
        if senha or dados.get('confirmar_senha'):
            if senha != dados.get('confirmar_senha'):
                self.add_error('confirmar_senha', 'As senhas não coincidem.')
            else:
                try:
                    validate_password(senha, self.usuario)
                except ValidationError as erro:
                    self.add_error('senha', erro)
        return dados

    def salvar(self):
        dados = self.cleaned_data
        user = self.usuario or User()
        user.username = dados['username']
        user.first_name = dados['nome']
        user.email = dados['email']
        user.is_active = dados['ativo']
        if dados['senha']:
            user.set_password(dados['senha'])
        user.save()
        Perfil.objects.update_or_create(
            user=user, defaults={'tipo': dados['tipo'], 'matricula': dados['matricula']}
        )
        return user