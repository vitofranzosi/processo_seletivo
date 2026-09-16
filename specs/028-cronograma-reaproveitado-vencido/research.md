# Pesquisa — 028 · Cronograma reaproveitado não nasce publicável

Fase 0. As perguntas que o plano precisou responder antes de existir, cada uma medida no código de
15/09/2026. Onde a resposta recusou uma alternativa, a razão da recusa está escrita: é ela que
impede a decisão de ser reaberta por esquecimento.

**O achado que mudou o formato do plano** está em `T-002` e `T-004`: dois dos três requisitos que
pareciam caros — a leitura do período encerrado e a conferência rodando no ponto mais cedo — **já
existem prontos no repositório**, e o que sobra é ligá-los. O custo verdadeiro está num lugar só, o
`T-008`: seis fixtures que publicam Edital com a inscrição já encerrada, porque hoje nada os
impede.

---

## T-001 — De onde vem o instante de referência

**Decisão: parâmetro `agora` em `validate_for_publication`, resolvido uma vez no topo; os dois
comandos que a chamam passam o `now` que já têm.**

A `FR-341` exige **um** instante por ato, e a Constituição a antecede: *"operações relacionadas
DEVEM compartilhar referência temporal consistente na mesma transação"* (Princípio II). O
repositório já pratica isso e não foi preciso inventar nada — `shared/application/commands.py` é
literalmente três linhas:

```python
def command_context():
    with transaction.atomic():
        yield timezone.now()
```

`submit_edital` e `publish_edital` já recebem esse `now` e já o distribuem para tudo o que grava no
ato. Passá-lo também para a conferência é o que faz o achado e o registro da publicação falarem do
mesmo instante.

**O padrão é `None`, e ele erra pelo lado certo.** Quem não passa `agora` lê o relógio — uma vez, no
topo da função, e não a cada Evento. A escolha copia a do `ato` que a `027` introduziu, e pela mesma
razão: esquecer o parâmetro faz a conferência **acusar**, e não silenciar.

**A zona vem de `shared/tempo.py`, e não de `settings`.** `validation.py` é domínio e hoje não
importa Django; `datetime.now(ZONA)` resolve sem inverter nada, e `shared/tempo.py` foi criado
exatamente para que o domínio pudesse importar a zona sem passar pela interface — está escrito lá.

**Recusado: ler `timezone.now()` dentro de cada verificação.** Dois Eventos do mesmo cronograma
seriam julgados contra instantes diferentes, e um cronograma cujo Evento vence entre a primeira e a
segunda leitura produziria um relatório que não corresponde a estado nenhum. É a `FR-341` ao pé da
letra.

---

## T-002 — Quem responde "o período de inscrições está encerrado"

**Decisão: `periodo_de_inscricoes(conteudo, agora)`, que já existe em
`inscricoes/domain/periodo.py` e já responde exatamente esta pergunta.**

A função lê o **mesmo** dicionário que a validação lê, encontra o Evento designado pela marca (e
nunca por texto em `type`), recebe `agora` por injeção e devolve um dos quatro estados. O
`ENCERRADO` dela é a `FR-346` inteira:

```python
if fim is not None and agora > fim:
    return Periodo(ENCERRADO, inicio, fim)
```

E o `>` estrito já é a `FR-347`: término exatamente igual ao instante do ato **não** encerra. A
`FR-347` não custa linha nenhuma — ela descreve o que a função já faz, e existe para que ninguém a
troque por `>=` sem perceber o que está decidindo.

**Por que não escrever a leitura de novo dentro de `validation.py`.** Porque essa função é a que o
**portal** obedece para decidir se aceita uma inscrição. Se a validação dissesse "encerrado" e o
portal dissesse "aberto", o sistema recusaria publicar um Edital que em seguida receberia inscrição
— dado independente e divergente, que é o que o Princípio II proíbe. *"Uma segunda porta para as
mesmas invariantes é o defeito que este repositório mais evita"*, e a `023` já pagou por ele.

### A dependência que isto cria, e por que ela é aceita

`editais/domain/validation.py` passa a importar de `inscricoes/domain/periodo.py`. Medido antes de
aceitar:

| Pergunta | Medição |
|---|---|
| `periodo.py` importa algo de `editais`? | **não** — só `dataclasses`, `datetime` e `django.utils.dateparse`. Não há ciclo |
| Já existe importação de domínio entre apps? | **sim** — `avaliacoes/domain/conjunto.py` importa este mesmo módulo |
| `validation.py` já conhece a marca do período? | **sim** — `_periodo_de_inscricoes` já conta os Eventos marcados, e `EVENTO_PUBLICADO` já declara a forma de `isRegistrationPeriod` |

A terceira linha é a que decide. A recusa que `validation.py` registrou uma vez — não importar as
formas de conclusão de `avaliacoes`, porque *"confere a string publicada contra o contrato, e não
conhece o domínio da conclusão"* — não se aplica aqui: o período de inscrições **não** é domínio
estrangeiro a este módulo, é conteúdo do Cronograma que ele já confere.

**Recusado por ora: mover `periodo.py` para `editais/domain/`.** Seria a arrumação mais correta por
camada — a leitura de calendário do Cronograma pertence a quem tem o Cronograma —, e continua
disponível. Fica fora porque toca seis importadores para uma feature que a auditoria mediu como
"esforço P", e porque o ganho é de arquitetura e não de comportamento. Se um segundo consumidor de
`editais` precisar da leitura, a mudança se paga e deve ser feita então.

---

## T-003 — Onde o selo do Cronograma lê a validade

**Decisão: um predicado puro em `editais/domain/calendario.py`, chamado pelos dois lados sobre as
duas formas do mesmo instante.**

A `FR-359` muda o critério de `_progresso`, que hoje é:

```python
"cronograma": CONCLUIDA
if getattr(edital, "cronograma", None) and edital.cronograma.eventos.exists()
else PENDENTE,
```

O problema é que `_progresso` trabalha sobre **objetos do ORM** (`start_at`, `end_at` como
`datetime`), e a validação trabalha sobre o **snapshot** (`startAt`, `endAt` como texto ISO). A
regra é uma; as entradas são duas.

**A saída é o predicado sobre instantes**, e não sobre nenhuma das duas formas:

```
vencido(inicio, termino, *, agora) -> bool
```

`validation.py` converte o texto ISO antes de chamar; `_progresso` passa os `datetime` do ORM
direto. Uma regra, um lugar, e nenhuma chance de o selo e a Revisão discordarem sobre o mesmo
cronograma.

**Custo de consulta: zero a mais.** `.exists()` vira `.all()` sobre a mesma relação — um Cronograma
tem uma dezena de Eventos, e a página já os carrega quando é a etapa atual.

**Recusado: montar o snapshot dentro de `_progresso` e reusar a validação inteira.**
`edital_snapshot` faz `prefetch_related` de perfis, modalidades, fatos, marcos, critérios e quadro
de vagas. `_progresso` roda em **todas** as nove páginas do assistente; pagar a carga inteira para
responder "algum Evento venceu?" é desproporcional, e a resposta não ficaria mais correta.

**Recusado: filtrar no banco** (`Q(start_at__lt=agora) | Q(end_at__lt=agora)`). Seria uma consulta,
mas poria a regra numa expressão de ORM, onde o predicado do domínio não alcança — e a `FR-359`
passaria a ter duas grafias que ninguém compara. É a mesma armadilha da `T-002`, um andar abaixo.

> **O ano não entra no selo.** A `FR-359` fala de Evento no passado, e só. Divergência de ano é
> advertência e nada mais; fazê-la apagar o selo daria a um Edital legítimo de dezembro a aparência
> de incompleto.

---

## T-004 — Por onde os achados chegam à etapa Cronograma

**Descoberta: não é preciso construir nada. Já está feito.**

A `FR-356` — *"a conferência MUST rodar assim que existir Cronograma com ao menos um Evento"* —
parecia o requisito mais caro do conjunto. Não é: `interface/views.py` já chama `_pendencias(edital)`
na montagem de **cada** página do assistente, e já entrega à etapa só o que se resolve nela:

```python
"pendencias": pendencias,
# A tela de revisão mostra tudo; as demais, só o que se resolve nelas — pendência
# exibida onde não há como agir vira ruído que a pessoa aprende a ignorar.
"pendencias_aqui": _pendencias_da_etapa(pendencias, etapa),
```

E `compor_cronograma.html` já renderiza `pendencias_aqui` num bloco `role="status"`.

Consequência: **assim que os três achados existirem e forem roteados para `cronograma`, eles
aparecem na etapa, sem uma linha de template nova** — inclusive na primeira abertura depois do
reaproveitamento, porque a conferência é derivada e não depende de gravação. A `UX-049` fica
satisfeita pelo caminho que a `006` já construiu, e o texto é o da própria mensagem do achado.

Isto reordena o plano: o que sobra de interface é o selo (`T-003`), e mais nada.

---

## T-005 — O caminho de cada achado, e a armadilha do `/schedule`

**Decisão: os três achados endereçam o Evento — `/schedule/id=<uuid>/<campo>` —, e nenhum deles
endereça `/schedule`.**

`DESTINO_DA_PENDENCIA` tem uma entrada por caminho exato que existe justamente para o período de
inscrições:

```python
"/schedule": ("inscricao", "#inscricao-periodo", True),
```

com a razão escrita: *"A designação do período é achado sobre `/schedule`, mas se resolve na etapa
`Inscrição`, que é onde existe o controle."* Está certo — para a **designação**.

**Mas a data se corrige na etapa 3.** Um impedimento de inscrição encerrada escrito em `/schedule`
casaria com a chave exata e mandaria quem lê para a etapa 6, que não tem campo de data nenhum. É a
`FR-349` inteira, e é o defeito que a auditoria já registrou uma vez em outra tela — *"Pendência de
marco roteada para a tela errada"*, P1.

Com o caminho da entidade, `_destino` percorre os segmentos de trás para a frente, não casa com a
chave exata, encontra `schedule` e devolve `("cronograma", "#cronograma-titulo", True)`. Nenhuma
entrada nova em `DESTINO_DA_PENDENCIA`, e nenhuma em `DESTINO_POR_CODIGO`.

| Achado | Caminho | Etapa de destino |
|---|---|---|
| `schedule_event_in_past` | `/schedule/id=<uuid>/startAt` ou `/endAt` | `cronograma` |
| `schedule_event_year_mismatch` | `/schedule/id=<uuid>/startAt` | `cronograma` |
| `registration_period_closed` | `/schedule/id=<uuid>/endAt` | `cronograma` |
| `registration_period_missing` *(já existe)* | `/schedule` | `inscricao` |
| `registration_period_ambiguous` *(já existe)* | `/schedule` | `inscricao` |

Os três códigos novos são próprios e não reusam prefixo por acidente: `registration_period_closed`
compartilha o prefixo dos dois existentes porque fala da mesma coisa, e há teste no repositório que
filtra por `startswith("registration_period")` — ele passa a ver o código novo, e é o comportamento
desejado.

**`_caminho_da_entidade` já produz essa gramática** (`004`), e recua para a posição quando o Evento
não tem `id` utilizável. Nada a escrever.

---

## T-006 — O ano lido na zona institucional

**Decisão: `instante.astimezone(ZONA).year`, comparado com `snapshot["year"]`.**

O snapshot carrega `"year": edital.year` como inteiro, e cada Evento carrega o instante como texto
ISO **com deslocamento** — a forma é fixada por `INSTANTE` em `validation.py` e materializada por
`datetime.isoformat()`.

Ler o ano sem converter para a zona institucional produziria advertência inventada num caso real e
comum: um Evento em **31/12/2026 23:30 em Vitória** é `2027-01-01T02:30Z`. Um Edital de 2026 que o
declare corretamente seria acusado de divergir de si mesmo — e só nos últimos horários do ano, que é
a forma mais cara de defeito que existe, porque não reproduz quando alguém vai olhar.

Não é hipótese: [doc/achado-teste-com-data-em-utc.md](../../doc/achado-teste-com-data-em-utc.md)
registra a classe, encontrada quando o CI do PR #102 reprovou *"num teste que aquele branch não
toca"*, e a conclusão de lá é a mesma — *"a instância foi corrigida; a classe fica registrada"*. Esta
feature é a primeira que precisa dela protegida, e a `SC-118` é o que a guarda.

**O ano do término não é conferido separadamente.** Um Evento que começa em dezembro e termina em
janeiro é normal — é a definição de período que atravessa o ano. Conferir os dois produziria
advertência em todo Edital de fim de ano, que é exatamente o caso que a `D-006` decidiu não
incomodar. O ano do Evento é o do **início**.

---

## T-007 — O que a suíte paga pela advertência de evento no passado

**Medido, e é menos do que parecia: quase nada.**

Os dois rascunhos de base do repositório carregam data **fixa**, escrita quando era futura:

| Fixture | Cronograma | Hoje (15/09/2026) |
|---|---|---|
| `tests/fixtures/edital.py:27` (`complete_draft`) | um Evento, `startAt 2026-09-01T09:00-03:00`, sem `endAt` | **no passado** |
| `tests/fixtures/selecao.py:97` (`rascunho_de_selecao`) | um Evento, `2026-09-01` a `2026-09-29` | início **no passado** |

Logo, quase toda chamada de `validate_for_publication` na suíte passa a devolver um
`schedule_event_in_past` a mais. A pergunta é o que isso derruba, e a resposta foi **medida arquivo
a arquivo**, e não estimada:

| Como o teste lê os achados | Quantos arquivos | Efeito da advertência nova |
|---|---|---|
| `blocking_findings(...)` — descarta advertência por construção | 9 | nenhum |
| filtro por prefixo de código (`vacancy_`, `registration_period`, `DA_014`, `/stages`) | 6 | nenhum |
| `any(... Severity.WARNING ...)` | 1 | nenhum — `any`, e não igualdade |

**Zero asserções sobre lista não filtrada de achados.** A disciplina já estava no repositório: todo
teste que lê a conferência filtra pelo assunto dele. A advertência nova não quebra uma asserção
sequer.

**O selo também não derruba nada.** A `FR-359` muda `_progresso`, e o único teste que lê `progresso`
é `tests/interface/test_acessibilidade.py`, nas duas vezes sobre a chave `conteudo`.

> **Esta medição corrige a primeira leitura desta pesquisa**, que dava ~11 asserções a ajustar e
> apontava a suíte como o custo principal da feature. Ela não é: o custo é o `T-008`, e é de seis
> lugares.

**Os fixtures ficam como estão.** Torná-los relativos a `agora` foi considerado — uma data fixa num
fixture é uma data que estava certa no dia em que foi escrita e fica errada sozinha —, e não entra
nesta feature: não corrige defeito nenhum aqui, e mudar o instante dos fixtures de base muda os
bytes canônicos de todo conteúdo publicado por eles, que é risco desproporcional ao ganho. Fica
**registrado** como observação: os dois Eventos de base nasceram no futuro e hoje estão no passado,
e a próxima feature que precisar deles corretos já sabe onde estão.

---

## T-008 — Os seis lugares que publicam com a inscrição já encerrada

**Medido, e é o único ponto em que o impedimento derruba teste verde.**

A `FR-346` recusa publicar Edital cujo período de inscrições já terminou. Seis lugares fazem
exatamente isso hoje, de propósito, para obter um Edital publicado com conjunto fechado:

| Lugar | O que faz |
|---|---|
| `tests/integration/avaliacoes/test_conjunto_fechado.py:137` | período de `-9d` a `-1h`; distribuir exige conjunto fechado |
| `tests/integration/portal/test_vitrine.py:178-180` | seleção encerrada, que não deve aparecer na vitrine |
| `tests/integration/portal/test_situacao_inscricoes.py:74` | `fim = agora - 1d` |
| `tests/integration/portal/test_cronograma_publico.py:214` | cronograma público de uma seleção encerrada |
| `tests/integration/supervisao/test_pulso.py:254` | Edital de `-30d` a `-10d` |
| `seed_demo._edital_encerrado` | o segundo Edital da demonstração, *"já com as inscrições encerradas"* |

> **Um sétimo candidato foi descartado na conferência, e vale dizer qual.**
> `test_cronograma_publico.py:40` também declara `endAt` no passado, mas naquele cenário o Evento
> vencido é a **Homologação**, e o período de inscrições corre de `-2d` a `+10d` — aberto. Ele não é
> bloqueado; ganha a advertência nova e nada mais. A marca `isRegistrationPeriod` é o que separa os
> dois casos, e procurá-la evento a evento é a única leitura que responde: um `grep` por `endAt` no
> passado acusa os dois.

**Decisão: eles passam a publicar com o período aberto e a fechá-lo por Retificação.**

É o que acontece na realidade — nenhum Edital do mundo é publicado depois de as inscrições fecharem;
ele é publicado antes, e o prazo vence com o tempo. A `FR-355` decidiu por escrito que a Retificação
que declara término já passado **não** é recusada, e é essa porta que os fixtures passam a usar.

O custo é pequeno porque o ajudante já existe: `tests/fixtures/publicacao.py:190` tem
`retify(api_client, edital, changes, ...)` numa chamada. São duas linhas por lugar.

**Recusado: excetuar a publicação quando o Edital "é de demonstração" ou quando um sinalizador de
teste está ligado.** Seria a saída barata e é a pior: faria a regra que existe para proteger o
acervo ter uma porta lateral, e a primeira pessoa a precisar dela em produção a encontraria.

**Recusado: congelar o relógio na suíte.** Não há `freezegun` nem `time-machine` nas dependências de
desenvolvimento, e acrescentar biblioteca para não mexer em seis fixtures é a troca errada — ver
`T-010`.

---

## T-009 — O quarto Edital da demonstração

**Decisão: criado pelo serviço de reaproveitamento, a partir do Edital encerrado, e deixado em
elaboração.**

A `FR-366` pede um Edital reaproveitado que exercite o cenário inteiro; a `FR-367` diz que ele fica
em elaboração — **e não é escolha, é consequência**: o sistema o impede de publicar, e é isso que
ele demonstra.

A origem natural é o **segundo** Edital da demonstração, aquele cujo cronograma vai de `-60d` a
`-40d`: reaproveitá-lo produz, sem nenhum arranjo, as três condições ao mesmo tempo — Eventos no
passado, período de inscrições encerrado, e, com o ano do Edital novo declarado um à frente, também
a divergência de ano. É o 12/2027 da auditoria reconstruído a partir do que a demonstração já tem.

`reaproveitamento.py` exige rascunho vazio e origem publicada ou encerrada; o segundo Edital é
publicado, e o quarto nasce vazio. Nada a afrouxar.

**Recusado: semear o quarto Edital escrevendo o rascunho direto.** Ele deve nascer **pela mesma
porta** que a pessoa usa, ou a demonstração deixa de demonstrar o caminho que ela vai percorrer —
que é a razão de a `023` existir.

---

## T-010 — `REFERENCE_NOW` existe, não é usada, e continua não sendo

`tests/fixtures/clock.py` tem três linhas e uma constante:

```python
REFERENCE_NOW = datetime(2026, 8, 28, 12, 0, tzinfo=UTC)
```

**Nenhum arquivo do repositório a importa.** A varredura de 15/09/2026 encontrou zero referências
fora da própria definição.

Foi tentador: um relógio fixo na suíte inteira tornaria `T-007` e `T-008` desnecessários de uma vez
— o `2026-09-01` dos fixtures voltaria a ser futuro, e nenhum período estaria encerrado. **Recusado,
e a razão é que o remédio seria pior que a doença**: fixar o instante exigiria interceptar
`timezone.now()` globalmente — sem biblioteca para isso —, e a suíte passaria a afirmar coisas sobre
um presente que o código não vive. Os testes de prazo recursal, de convocação e de sorteio leem o
relógio de verdade; congelá-lo para uns e não para outros é o começo de uma suíte que concorda
consigo mesma e não com o sistema.

Fica como está, e o achado fica **registrado**: é constante morta, e removê-la ou usá-la é decisão
de quem governa o escopo, não desta feature.

---

## Resumo das decisões

| # | Decisão | Custo |
|---|---|---|
| T-001 | `agora` por parâmetro, resolvido uma vez; comandos passam o `now` da transação | 1 parâmetro, 2 chamadas |
| T-002 | Reusar `periodo_de_inscricoes` de `inscricoes/domain` | 1 importação |
| T-003 | Predicado `vencido(inicio, termino, *, agora)` em `editais/domain/calendario.py` | 1 módulo de poucas linhas |
| T-004 | Nada a construir: `pendencias_aqui` já entrega à etapa | zero |
| T-005 | Caminho da entidade, nunca `/schedule` | zero linhas de roteamento |
| T-006 | Ano do **início**, na zona institucional | — |
| T-007 | Nada a fazer: toda asserção da suíte já filtra o que lê | zero |
| T-008 | Seis lugares publicam abertos e retificam para fechar | 6 × 2 linhas |
| T-009 | Quarto Edital da demonstração, pela porta do reaproveitamento | 1 função em `seed_demo` |
| T-010 | `REFERENCE_NOW` fica como está, e o achado fica registrado | zero |
