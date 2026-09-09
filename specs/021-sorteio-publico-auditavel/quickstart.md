# Quickstart — 021 · Sorteio público auditável

Como provar que a feature funciona, ponta a ponta, pelos canais dos atores. Nada aqui usa shell para
fazer o que a tela deveria fazer: a Constituição §VI não aceita demonstração por chamada manual.

## Pré-requisitos

```bash
cd backend && make install
```

Banco provisionado e migrado (a `021` acrescenta migrations em `sorteios`, `classificacao`,
`divulgacao` e `editais`):

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

### 1 · Declarar o método (composição do Edital, e não gestão do sorteio)

Na composição do marco de classificação, declarar algoritmo, fonte, ocorrência, derivação,
normalização e regra de substituição, e publicar a versão. **Antes** de congelar qualquer coisa.

*Esperado:* o método no conteúdo publicado do Edital, em
`/profiles/id=…/classificationMilestones/id=…/drawMethod`, com resumo canônico próprio.

*Prova de que é normativo, e não configuração:* retificar
`…/drawMethod/substitutionRule` funciona pela gramática existente e gera versão nova; **não há**
caminho na gestão do sorteio que altere o método (D-013, FR-014).

### 2 · Publicar a relação de habilitados (gestão)

Um clique. O sistema projeta as inscrições submetidas do recorte, numera de 1 a N por protocolo
crescente, cita a versão e o resumo do método do marco, calcula o resumo da relação e publica —
**publicar é congelar**.

*Esperado:* quantidade, resumo, `metodo_hash`, instante e ator gravados; a relação visível no portal,
com número, nome e protocolo de cada participante e o critério de projeção escrito.

*Prova negativa:* não há, em tela alguma, botão de incluir, excluir ou renumerar participante; e
publicar segunda relação raiz para o mesmo recorte é recusado **pelo banco** (FR-070).

### 3 · Conferir o compromisso (portal, anônimo)

`/selecoes/<id>/sorteio/<recorte>/relacao` mostra a relação e o resumo.

*Esperado:* qualquer pessoa vê o universo **antes** de a semente existir. É o passo que a prática
atual não tem.

*Prova que fecha o círculo:* recalcular o `canonical_sha256` da relação a partir **do que a página
mostra** dá o mesmo resumo publicado. Nenhum dado que o portal esconde entra na conta (R-015).

### 4 · Observar a ocorrência (gestão)

Na data e hora publicadas, a tela busca a ocorrência declarada na fonte externa.

A tela nomeia **qual** ocorrência vai buscar, e a referência é derivada da regra publicada — não
escolhida por quem opera.

*Esperado:* material bruto gravado e exibido, junto com **quando a extração aconteceu** — que é o
instante que a FR-016 compara com o do congelamento. A semente normalizada **não** é gravada aqui:
ela nasce na constituição, sob a regra do método (D-016).

*Prova negativa:* não existe campo para digitar semente nem para trocar a referência; com a fonte
indisponível, a tela registra a evidência, a regra publicada aponta a ocorrência seguinte e o botão
passa a nomeá-la. As descartadas continuam visíveis, com a evidência de cada uma — é o controle da
R-006. Esgotadas as substitutas previstas, o sistema para e diz que prosseguir exige Retificação:
ele não escolhe fonte por conta própria.

### 5 · Realizar o sorteio (gestão, com a tela transmitida)

Um botão só. O comando lê a ocorrência **já registrada** — não vai à rede —, lê o método pela versão
que a relação cita, confere o resumo dele contra o que a relação comprometeu, normaliza, calcula a
ordem de **todos** os participantes e constitui o ato, numa transação.

*Esperado:* ordem completa, ato constituído com `origem = SORTEIO`, manifesto com resumo gravado.

*Prova negativa:* pedir de novo, sobre a mesma tupla, é recusado; duas abas ao mesmo tempo produzem
**um** ato.

### 6 · Publicar o resultado (gestão)

A divulgação do ato segue o caminho que a `017` já tem, agora com a dimensão da lista.

*Esperado:* a ordem publicada no portal, com identidade do sorteio, algoritmo, semente e resumos.

*No certame com cotas* — o 57 e o 28 —, as três listas do marco produzem **três** publicações, cada
uma citando o seu ato; e a publicação sem lista de um marco comum continua única, exatamente como
antes (D-015, FR-068).

### 7 · Verificar por conta própria (portal, anônimo, e fora do sistema)

`/selecoes/<id>/sorteio/<drawId>/verificar` recalcula das entradas e relata.

E a prova que importa, **fora** do sistema:

```bash
cd backend && node processo_seletivo/portal/static/portal/sorteio-cli.js < manifesto.json
```

*Esperado:* a mesma ordem, item a item, sem tocar no sistema e sem o vídeo.

### 8 · Anular e suceder (gestão, e uma Retificação)

**Retificar o Edital para declarar a ocorrência nova**, anular com motivo, publicar relação nova,
observar a ocorrência declarada e constituir o sucessor.

A Retificação não é burocracia acidental (D-017): a ocorrência é conteúdo declarado, e um sucessor
que usasse outra extração sem a norma dizê-lo estaria escolhendo a extração. O efeito é a garantia
mais forte desta feature — não existe anular até o resultado agradar, porque cada refazimento custa
um ato normativo publicado.

*Esperado:* os dois sorteios coexistem; o primeiro continua íntegro e verificável; o sucessor cita o
anterior e o motivo.

## Os testes automatizados

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER="$USER" DB_NAME=test_021_sorteio uv run pytest
```

`TEST_DB_ENGINE=postgresql` **e** `DB_USER` são obrigatórios: sem o primeiro a suíte cai para SQLite
e pula em silêncio os testes que dependem de constraint e trigger. `DB_NAME` próprio evita que duas
suítes em worktrees diferentes disputem o mesmo banco.

**O tempo medido (SC-004).** `tests/integration/sorteios/test_desempenho.py` percorre o caminho
completo com 300 participantes e imprime o número:

```text
[SC-004] 300 participantes — congelamento 0,01s, constituição 0,02s, total 0,04s
```

A SC-004 pede menos de um minuto de operação, que é o tempo de uma tomada de transmissão. A folga é
esperada e o teste não a celebra: o custo real do ato é a chamada à fonte externa, que acontece
**antes** da transação e num comando separado. O que o limite de 60 segundos detecta é regressão de
ordem de grandeza — uma consulta por participante nascendo dentro de um laço.

Recortes úteis:

```bash
uv run pytest tests/contract/test_vetores_de_sorteio.py     # os vetores normativos, em Python
uv run pytest tests/test_javascript.py                      # os mesmos vetores, em JavaScript
uv run pytest tests/integration/sorteios                    # relação, congelamento, constituição
uv run pytest tests/portal/test_verificacao_de_sorteio.py   # a verificação pública
```

## Os quatro recortes da amostra, e até onde o sistema conduz cada um (SC-006)

A SC-006 pede que os quatro Editais de sorteio da amostra tenham o seu mecanismo de seleção
executável no sistema. Conduz **não** é o mesmo que concluir o certame, e a tabela diz onde cada um
para — a fronteira é a mesma para os quatro, e é deliberada (FR-064).

| Edital | Recortes | Até onde o sistema o conduz | Onde ele para |
|---|---|---|---|
| **77/2026** | perfil único, sem cotas — **1 ordem** | Do congelamento à ordem publicada, com manifesto e verificação pública. É o percurso dos oito passos acima | Na ordem publicada. Quem ocupa as 39 vagas é `014`/`016` |
| **76/2026** | polos com cadastro de reserva, sem cotas — **1 ordem por polo** | Um recorte por polo, cada um com relação, ocorrência e ato próprios. A tela de gestão lista os polos juntos, e é o que evita publicar dois e esquecer o terceiro | Na ordem de cada polo. O cadastro de reserva — quem é chamado, e em que ordem entre polos — está fora |
| **57/2026** | 2 cursos × (AC, PPI, PcD) — **3 ordens por curso** | As três listas de cada curso, com o cotista figurando em duas e recebendo número próprio em cada. As três se divulgam separadamente, cada uma com a sua cadeia | Na ordem de cada lista. **A interação entre listas fica fora**: o cotista sorteado nas duas continua nas duas, e quem decide em qual ele fica é outra capacidade |
| **28/2026** | 7 polos × (AC, PPI, PcD) — **21 ordens** | O mesmo do 57, multiplicado pelos polos. Uma extração da fonte semeia as 21 ordens, e o `relationHash` as separa — é o vetor `mesma-semente-recortes-distintos` provando isso | Igual ao 57, e com a mesma fronteira |

**A fronteira é a mesma nos quatro, e é a frase que governa a feature**: o sistema entrega a ordem,
e não decide quem entrou. Um roteiro que "terminasse" o 28/2026 estaria respondendo a pergunta que
a `021` recusa responder.

**Os quatro exigem a mesma preparação**: o marco de classificação declara o `drawMethod` no Edital,
antes do congelamento. Sem ele o sistema recusa congelar a relação, e a recusa nomeia o Edital como
o lugar da correção — e não a tela do sorteio.

## O que este roteiro não demonstra, de propósito

Quem ocupa as 39 vagas do 77/2026, quem é suplente e até onde a análise documental desce. A ordem
publicada é o fim desta feature; o resto é `014` e `016`.
