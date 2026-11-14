// Login: mostrar/ocultar senha
document.addEventListener('DOMContentLoaded', function () {
    const botao = document.getElementById('btnVerSenha');
    const input = document.getElementById('password');
    const icone = document.getElementById('iconeOlho');
    if (!botao || !input || !icone) return;

    botao.addEventListener('click', function () {
        const mostrar = input.type === 'password';
        input.type = mostrar ? 'text' : 'password';
        icone.classList.toggle('fa-eye', !mostrar);
        icone.classList.toggle('fa-eye-slash', mostrar);
    });
});