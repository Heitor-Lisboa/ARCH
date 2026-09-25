# ARCH — Sistema de Estoque do LabMAKER (IFRN/SGA)

## Sobre o projeto

Projeto acadêmico desenvolvido no IFRN, Campus São Gonçalo do Amarante, usando o framework Django. O ARCH organiza o estoque do LabMAKER, controlando o cadastro de itens, empréstimos, devoluções, perdas e o histórico de movimentações do laboratório, com acesso restrito a bolsistas, coordenadores de laboratório e demais usuários autorizados.

O projeto é dividido em aplicativos, cada um com uma responsabilidade própria:

| App | Responsabilidade |
| ------------ | ---------------------------------------------------------------------------------------------------------------- |
| usuarios | Cuida da autenticação e do cadastro de usuários moderadores |
| itens | Gerencia o estoque: cadastrar, editar, remover e consultar itens |
| emprestimos | Cuida de empréstimos, devoluções, prazos, alertas e registro de perdas (RF07 a RF11) — planejado, ainda não implementado |

O `emprestimos` foi definido como um app separado de `itens` porque um empréstimo se relaciona a várias outras referências além do próprio item (pessoa, prazo, status, registro de perda), e não só ao estoque. O histórico de movimentações (RF12) ainda não tem uma definição de onde vai morar.

Desenvolvido por Heitor Lisboa dos Santos, Gabriel Endrel da Silva, Pedro Jerônimo Mendonça da Silva e Kaiser Silva de Oliveira.

## Funcionalidades previstas

| Código | Requisito | Status |
| ------ | ------------------------------------------------------------------------------------ | ------------------------------------- |
| RF01 | Cadastro de usuários (bolsista, coordenador de laboratório ou usuário autorizado) | Em desenvolvimento (app `usuarios`) |
| RF02 | Autenticação de usuários por credenciais cadastradas | Em desenvolvimento (app `usuarios`) |
| RF03 | Cadastro de itens no estoque (nome, descrição, quantidade, categoria) | Em desenvolvimento (app `itens`) |
| RF04 | Atualização das informações de itens cadastrados | Em desenvolvimento (app `itens`) |
| RF05 | Remoção de itens do sistema | Em desenvolvimento (app `itens`) |
| RF06 | Consulta e busca de itens disponíveis no estoque | Em desenvolvimento (app `itens`) |
| RF07 | Registro de empréstimos, com item, responsável e data de retirada | Planejado (app `emprestimos`) |
| RF08 | Registro de devoluções, com data de devolução | Planejado (app `emprestimos`) |
| RF09 | Prazo limite de devolução para cada item emprestado | Planejado (app `emprestimos`) |
| RF10 | Alertas quando o prazo de devolução é ultrapassado | Planejado (app `emprestimos`) |
| RF11 | Registro de itens perdidos ou não devolvidos | Planejado (app `emprestimos`) |
| RF12 | Histórico das movimentações e atividades dos usuários | Planejado |

## Regras de negócio

- Acesso ao sistema restrito a usuários moderadores (bolsistas, coordenadores de laboratório ou outros usuários autorizados).
- Um item só pode ser emprestado se houver quantidade disponível em estoque.
- Todo item emprestado tem um prazo máximo de devolução, definido no momento do empréstimo.
- Todo item emprestado deve ser devolvido e registrado, exceto em casos de perda justificada.
- Itens não devolvidos no prazo podem ser registrados como perdidos após análise do moderador responsável.
- A quantidade em estoque é atualizada automaticamente a cada empréstimo, devolução, adição ou perda.
- Toda ação no sistema é registrada no histórico, com usuário responsável, data e tipo de operação.

## Tecnologias utilizadas

- Python
- Django
- HTML e CSS
- JavaScript
- SQLite (ambiente de desenvolvimento) / MySQL (planejado para produção, no DataCenter do campus)
- python-dotenv

## Estrutura do projeto

\`\`\`
ARCH/
├── venv/ # Ambiente virtual (não vai para o GitHub)
├── manage.py
├── .env # Variáveis de ambiente (não vai para o GitHub)
├── .env.example # Modelo do .env (vai para o GitHub)
├── .gitignore
├── requirements.txt
├── setup/ # Configurações do projeto
│ ├── settings.py
│ ├── urls.py
│ ├── asgi.py
│ └── wsgi.py
├── itens/ # App de itens do estoque
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── migrations/
├── emprestimos/ # App de empréstimos, devoluções e perdas (planejado)
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── migrations/
├── usuarios/ # App de usuários
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── migrations/
├── templates/ # Arquivos HTML
│ ├── base.html
│ ├── itens/
│ ├── emprestimos/
│ └── usuarios/
└── static/
└── css/
\`\`\`

## Pré-requisitos

- Python instalado (versão 3.10 ou superior)
- Git instalado
- Conta no GitHub

## Como configurar o projeto na sua máquina

### 1. Clone o repositório

\`\`\`
git clone https://github.com/Heitor-Lisboa/ARCH.git
cd ARCH
\`\`\`

O comando `git clone` baixa uma cópia completa do projeto para a sua máquina.

### 2. Crie o ambiente virtual

O ambiente virtual isola as dependências do projeto do resto do sistema:

\`\`\`
python -m venv ./venv
\`\`\`

Ative o ambiente.

No Windows:

\`\`\`
venv\Scripts\activate
\`\`\`

No Linux ou Mac:

\`\`\`
source venv/bin/activate
\`\`\`

Quando ativar, o terminal passa a mostrar `(venv)` no início da linha.

### 3. Instale as dependências

Com a venv ativada, execute:

\`\`\`
pip install -r requirements.txt
\`\`\`

### 4. Crie o arquivo .env

Copie o arquivo modelo e renomeie para `.env`:

\`\`\`
cp .env.example .env
\`\`\`

No Windows, se o comando `cp` não funcionar:

\`\`\`
copy .env.example .env
\`\`\`

O `.env` deve conter algo como:

\`\`\`
SECRET_KEY=
DEBUG=True
\`\`\`

A `SECRET_KEY` fica vazia de propósito: cada pessoa gera a sua própria, e ela nunca é enviada para o GitHub.

### 5. Gere a sua SECRET_KEY

Com o ambiente ativado, execute:

\`\`\`
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
\`\`\`

### 6. Cole a chave no .env

Copie a chave impressa no terminal e cole no arquivo, sem aspas e sem espaços:

\`\`\`
SECRET_KEY=<chave-gerada-no-passo-anterior>
DEBUG=True
\`\`\`

### 7. Crie o banco de dados

O arquivo `db.sqlite3` também não vai para o GitHub. Cada máquina cria o seu banco local:

\`\`\`
python manage.py migrate
\`\`\`

### 8. Rode o projeto

\`\`\`
python manage.py runserver
\`\`\`

Acesse `http://localhost:8000/` no navegador.

## Como manter o projeto atualizado

Sempre comece o trabalho buscando as mudanças que os colegas enviaram:

\`\`\`
git pull
\`\`\`

Depois de alterar o código, envie as mudanças:

\`\`\`
git add .
git commit -m "descrição do que foi feito"
git pull
git push
\`\`\`

O `git pull` antes do `git push` evita conflitos: se alguém já enviou mudanças, o Git baixa e tenta juntar tudo.

| Erro | Causa | Solução |
| --------------------------------------- | --------------------------------------------- | ------------------------------------------------------------ |
| `SECRET_KEY must not be empty` | Arquivo `.env` não foi criado ou está vazio | Refazer os passos 4 a 6 |
| Comando `manage.py` não é reconhecido | Ambiente virtual não está ativado | Verificar se o terminal mostra `(venv)` no início da linha |
| Página 404 no navegador | URL digitada não corresponde a nenhuma rota | Conferir os caminhos no `urls.py` de cada app |

## Roadmap

- [ ] Implementar o app `emprestimos`: empréstimos, devoluções e prazos (RF07 a RF09)
- [ ] Implementar o registro de perdas no app `emprestimos` (RF11)
- [ ] Implementar a emissão de alertas de atraso no app `emprestimos` (RF10)
- [ ] Definir e implementar o histórico centralizado de movimentações (RF12)
- [ ] Configurar a conexão com o banco de dados MySQL para produção
- [ ] Implementar o controle de permissões por tipo de usuário (Bolsista, Coordenador, Autorizado)
- [ ] Escrever testes automatizados para as regras de negócio
- [ ] Finalizar os templates de interface conforme os protótipos de tela

## Equipe

- Heitor Lisboa dos Santos
- Gabriel Endrel da Silva
- Pedro Jerônimo Mendonça da Silva
- Kaiser Silva de Oliveira