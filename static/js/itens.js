// Estoque: aplica o filtro de categoria assim que ela é escolhida.
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('filtrosEstoque');
    const categoria = document.getElementById('filtroCategoria');
    if (!form || !categoria) return;

    categoria.addEventListener('change', function () {
        form.submit();
    });
});