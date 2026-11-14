// ARCH — scripts gerais. Carregado no <head>, depois do <link id="theme-stylesheet">.

// 1) Tema: aplica o tema salvo antes da página pintar (evita "flash")
(function () {
    try {
        var link = document.getElementById('theme-stylesheet');
        var tema = localStorage.getItem('arch-theme') || 'light';

        if (link && tema === 'dark') {
            link.href = link.dataset.darkUrl;
        }
        document.documentElement.setAttribute('data-theme', tema);
    } catch (e) {}
})();

// 2) Tema: switch claro/escuro
document.addEventListener('DOMContentLoaded', function () {
    const root = document.documentElement;
    const switchInput = document.getElementById('switch');
    const themeLink = document.getElementById('theme-stylesheet');

    if (!switchInput || !themeLink) return;

    // O switch fica "marcado" (mostrando o sol) quando o tema atual é o claro
    switchInput.checked = root.getAttribute('data-theme') !== 'dark';

    switchInput.addEventListener('change', function () {
        const novoTema = switchInput.checked ? 'light' : 'dark';

        root.setAttribute('data-theme', novoTema);
        themeLink.href = novoTema === 'dark' ? themeLink.dataset.darkUrl : themeLink.dataset.lightUrl;

        try {
            localStorage.setItem('arch-theme', novoTema);
        } catch (e) {
            // localStorage indisponível (ex.: aba anônima) - segue sem salvar
        }
    });
});

// 3) Notificações (sino)
document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('notifBtn');
    const painel = document.getElementById('notifPanel');
    if (!btn || !painel) return;

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        painel.hidden = !painel.hidden;
        btn.setAttribute('aria-expanded', String(!painel.hidden));
    });

    document.addEventListener('click', function (e) {
        if (!painel.contains(e.target)) {
            painel.hidden = true;
            btn.setAttribute('aria-expanded', 'false');
        }
    });
});

// 4) Pesquisa de abas no menu lateral
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('sidebarSearch');
    const itens = document.querySelectorAll('.sidebar-nav li');
    if (!input || !itens.length) return;

    const normalizar = (texto) =>
        texto.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

    function filtrar() {
        const termo = normalizar(input.value.trim());
        itens.forEach(function (li) {
            li.hidden = termo !== '' && !normalizar(li.textContent).includes(termo);
        });
    }

    input.addEventListener('input', filtrar);

    input.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter') return;
        const primeiro = Array.from(itens).find((li) => !li.hidden);
        if (primeiro) window.location.href = primeiro.querySelector('a').href;
    });
});