# Quickstart — 021 · Sorteio público auditável

Como provar que a feature funciona, ponta a ponta, pelos canais dos atores. Nada aqui usa shell para
fazer o que a tela deveria fazer: a Constituição §VI não aceita demonstração por chamada manual.

## Pré-requisitos

```bash
cd backend && make install
```

Banco provisionado e migrado (a `021` acrescenta migrations em `sorteios`, `classificacao` e
`editais`):

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py migrate
```

Dados de demonstração, incluindo o certame de sorteio que esta feature acrescenta ao `seed_demo`:

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py seed_demo
```

Servidor com o seletor de identidade, que é como se alterna entre os atores:

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver
```

## O roteiro — o ciclo do 77/2026

Oito passos, e o teste da spec é este. Cada um é executável pelo canal do ator.

### 1 · Declarar o método (gestão)

Em `/gestao/editais/<id>/sorteio/`, declarar algoritmo, fonte, ocorrência, derivação, normalização e
regra de substituição. **Antes** de congelar qualquer coisa.

*Esperado:* método gravado, com resumo próprio, e a tela dizendo que o universo ainda não está
comprometido.

### 2 · Publicar a relação de habilitados (gestão)

Um clique. O sistema projeta as inscrições submetidas do recorte, numera de 1 a N por protocolo
crescente, calcula o resumo e publica — **publicar é congelar**.

*Esperado:* quantidade, resumo, instante e ator gravados; a relação visível no portal, com números
públicos e o critério de projeção escrito.

*Prova negativa:* não há, em tela alguma, botão de incluir, excluir ou renumerar participante.

### 3 · Conferir o compromisso (portal, anônimo)

`/selecoes/<id>/sorteio/<recorte>/relacao` mostra a relação e o resumo.

*Esperado:* qualquer pessoa vê o universo **antes** de a semente existir. É o passo que a prática
atual não tem.

### 4 · Observar a ocorrência (gestão)

Na data e hora publicadas, a tela busca a ocorrência declarada na fonte externa.

*Esperado:* material bruto e semente normalizada gravados e exibidos. *Prova negativa:* não existe
campo para digitar semente; com a fonte indisponível, a tela aplica a regra publicada de substituição
e registra a evidência — e continua sem oferecer digitação.

### 5 · Realizar o sorteio (gestão, com a tela transmitida)

Um botão só. O comando lê a ocorrência, calcula a ordem de **todos** os participantes e constitui o
ato, numa transação.

*Esperado:* ordem completa, ato constituído com `origem = SORTEIO`, manifesto com resumo gravado.

*Prova negativa:* pedir de novo, sobre a mesma tupla, é recusado; duas abas ao mesmo tempo produzem
**um** ato.

### 6 · Publicar o resultado (gestão)

A divulgação do ato segue o caminho que a `017` já tem.

*Esperado:* a ordem publicada no portal, com identidade do sorteio, algoritmo, semente e resumos.

### 7 · Verificar por conta própria (portal, anônimo, e fora do sistema)

`/selecoes/<id>/sorteio/<drawId>/verificar` recalcula das entradas e relata.

E a prova que importa, **fora** do sistema:

```bash
cd backend && node tests/javascript/sorteio-cli.js < manifesto.json
```

*Esperado:* a mesma ordem, item a item, sem tocar no sistema e sem o vídeo.

### 8 · Anular e suceder (gestão)

Anular com motivo, publicar relação nova, observar ocorrência nova, constituir o sucessor.

*Esperado:* os dois sorteios coexistem; o primeiro continua íntegro e verificável; o sucessor cita o
anterior e o motivo.

## Os testes automatizados

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER="$USER" DB_NAME=test_021_sorteio uv run pytest
```

`TEST_DB_ENGINE=postgresql` **e** `DB_USER` são obrigatórios: sem o primeiro a suíte cai para SQLite
e pula em silêncio os testes que dependem de constraint e trigger. `DB_NAME` próprio evita que duas
suítes em worktrees diferentes disputem o mesmo banco.

Recortes úteis:

```bash
uv run pytest tests/contract/test_vetores_de_sorteio.py     # os vetores normativos, em Python
uv run pytest tests/test_javascript.py                      # os mesmos vetores, em JavaScript
uv run pytest tests/integration/sorteios                    # relação, congelamento, constituição
uv run pytest tests/portal/test_verificacao_de_sorteio.py   # a verificação pública
```

## O que este roteiro não demonstra, de propósito

Quem ocupa as 39 vagas do 77/2026, quem é suplente e até onde a análise documental desce. A ordem
publicada é o fim desta feature; o resto é `014` e `016`.
