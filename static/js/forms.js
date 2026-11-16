// Formulários do ARCH

// 1) Campos numéricos: troca as setinhas padrão do navegador por botões − e +
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.form-field input[type="number"]').forEach(function (input) {
        const caixa = document.createElement('div');
        caixa.className = 'number-field';
        input.parentNode.insertBefore(caixa, input);
        caixa.appendChild(input);

        function botao(texto, rotulo, passo) {
            const b = document.createElement('button');
            b.type = 'button';
            b.className = 'number-btn';
            b.textContent = texto;
            b.setAttribute('aria-label', rotulo);
            b.disabled = input.disabled;
            b.addEventListener('click', function () {
                if (passo > 0) input.stepUp(); else input.stepDown();
                input.dispatchEvent(new Event('input', { bubbles: true }));
            });
            return b;
        }

        caixa.insertBefore(botao('−', 'Diminuir', -1), input);
        caixa.appendChild(botao('+', 'Aumentar', 1));
    });
});

// 2) Movimentação: mostra só os campos do tipo escolhido
// (Saída: item, pessoa e prazo / Entrada: empréstimo que está sendo devolvido).
document.addEventListener('DOMContentLoaded', function () {
    const tipo = document.getElementById('id_tipo');
    if (!tipo || !document.getElementById('campo-emprestimo')) return;

    const camposSaida = ['item', 'emprestado_a', 'prazo_dias'];
    const camposEntrada = ['emprestimo'];

    function mostrar(nomes, visivel) {
        nomes.forEach(function (nome) {
            const campo = document.getElementById('campo-' + nome);
            if (campo) campo.hidden = !visivel;
        });
    }

    function atualizar() {
        mostrar(camposSaida, tipo.value === 'S');
        mostrar(camposEntrada, tipo.value === 'E');
    }

    tipo.addEventListener('change', atualizar);
    atualizar();
});