# Implementation Plan: Referência da Loteria Federal conferida antes do compromisso

**Branch**: `claude/loteria-federal-validation-gps-a628fa` | **Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/116-referencia-da-loteria-federal/spec.md`

Os caminhos são relativos a `backend/processo_seletivo/`, e os de teste a `backend/tests/`. Todos
foram conferidos na `main` em `83cd5863`, que é também a base da POC: entre ela e a `origin/main` de
03/11/2026 não há commit.

## Summary

A Caixa só responde, de forma verificável, qual é o último concurso realizado. Esta feature faz
essa pergunta antes de quatro atos (submissão, publicação, publicação de Retificação e congelamento)
e aplica a decisão da spec a cada uma das quatro situações. Também confere sem rede a forma
numérica da referência na gravação.

Três peças novas:

1. **Uma regra pura** em `sorteios/domain/conferencia.py`: as situações, a decisão por ato e as
   mensagens. É a POC adaptada.
2. **Uma consulta** no adaptador da Loteria Federal, ao lado da granularidade que a `102` já declara
   por fonte. As fontes de demonstração respondem por tabela.
3. **Um orquestrador** em `sorteios/application/conferencia.py`. Ele roda **fora** da transação,
   devolve as situações por referência, e é chamado pelos quatro comandos e pela conferência sob
   demanda.

A validação de publicação recebe as situações já resolvidas, como já recebe `marcos_sorteados`, e
continua pura. O registro vai ao `RegistroAuditoria.detalhe` do ato. Não há migration.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (monólito existente)
**Primary Dependencies**: nenhuma nova. `urllib`, como o adaptador já usa.
**Storage**: PostgreSQL. Nenhuma tabela ou coluna nova. Usa-se `RegistroAuditoria.detalhe`
(`JSONField`, já existente desde a `051`).
**Testing**: pytest contra PostgreSQL (`make test-pg`). A fonte é substituída em toda a suíte, e um
vigia recusa conexão à Caixa.
**Target Platform**: servidor Linux (VM institucional)
**Project Type**: aplicação web, monólito com interface Django e API DRF
**Performance Goals**: no máximo duas chamadas por referência e uma principal por ato, cada chamada
com tempo limite. A espera acrescentada a um ato com a Caixa fora do ar não passa de 15 s
(SC-1097).
**Constraints**:
- nenhuma chamada de rede dentro de `command_context()` nem de `comando_de_comissao`;
- nenhuma chamada em renderização;
- a suíte não acessa a internet.
**Scale/Scope**: um adaptador, uma regra pura, quatro comandos, três telas, um template de campo.

## Constitution Check

| Princípio | Como esta feature o atende |
|---|---|
| I. Linguagem ubíqua | "Referência", "concurso", "realizado" e "congelamento" são os termos que a `021` e a `102` já usam. A situação "ainda não realizado" diz o que a fonte afirma, e nada além disso (D-003) |
| II. Imutabilidade e temporalidade | Nada publicado é alterado ou reconferido (FR-3652). O instante da consulta e o do ato são distintos e ambos registrados (FR-3632). Mensagens no fuso institucional (FR-3642) |
| III. Auditoria | A conferência fica no registro do ato, sem corpo da fonte nem rastro de pilha (FR-3647, FR-3648). Nenhuma permissão nova: a conferência herda a do ato |
| IV. Regras no backend; ver antes do ato | A regra mora no domínio e é a mesma pela tela e pela API. A conferência sob demanda mostra o resultado antes do ato irreversível (FR-3645) |
| IV. Concorrência | Consulta fora da transação. Dentro dela, só vale para o conteúdo travado (FR-3632). A precedência na constituição continua sendo a garantia final |
| V. Simplicidade | Sem tabela, fila, cache, agendador ou dependência. O adaptador existente ganha uma consulta |
| V. Testes | A matriz da POC vira teste de domínio, e cada ato ganha teste de integração com a fonte substituída |
| VI. Jornada | Na recusa, a mensagem diz o que fazer, e no congelamento diz também o ato que falta |

Sem violação. *Complexity Tracking* vazio.

## Project Structure

### Documentation (this feature)

```text
specs/116-referencia-da-loteria-federal/
├── spec.md
├── plan.md               # este arquivo
├── tasks.md
├── rastreabilidade.md    # requisito → tarefa → teste
├── contracts/
│   └── mensagens.md      # as frases, que os testes conferem
└── checklists/
    └── requirements.md
```

Sem `research.md` (as decisões estão na spec, e a pesquisa está no estudo de 03/11), sem
`data-model.md` (nenhuma entidade persistida) e sem `quickstart.md` (o roteiro local cabe na seção
*Roteiro local*, abaixo).

### Source Code (repository root)

```text
backend/processo_seletivo/
├── sorteios/
│   ├── domain/conferencia.py                  # NOVO: situações, decisão por ato, mensagens (pura)
│   ├── application/conferencia.py             # NOVO: consulta fora da transação, por ato
│   ├── infrastructure/fontes/__init__.py      # porta: FORMA_DA_REFERENCIA, ultimo_e_datas()
│   ├── infrastructure/fontes/loteria_federal.py  # a consulta; a demonstração por tabela
│   └── application/relacao.py                 # congelamento confere antes de comando_de_comissao
├── editais/
│   ├── domain/perfis.py                       # forma por fonte em _validar_forma_da_ocorrencia
│   ├── domain/validation.py                   # achados: situacoes= e o código novo
│   └── application/draft.py                   # zeros à esquerda normalizados em replace_draft
├── publicacoes/application/
│   ├── publish_edital.py                      # submit_edital e publish_edital conferem antes
│   └── retificacoes.py                        # publish_retification confere o introduzido
└── interface/
    ├── views.py                               # conferência sob demanda (POST, htmx); desfechos
    └── templates/interface/                   # _marco.html, compor_classificacao.html,
                                               # sorteio.html, detalhe (aviso pós-ato)
```

## Desenho

### 1. A porta da fonte (D-008)

Em `FonteExterna`, dois atributos com padrão "não se aplica":

- `FORMA_DA_REFERENCIA = None`: expressão de forma, ou nenhuma;
- `consultar_ultimo()` e `consultar_data(numero)`: devolvem o último concurso e a data de um número,
  ou `None` quando não souberem. O padrão é **não declarar** (`SABE_CONFERIR = False`), e então a
  conferência não roda para a fonte.

`LoteriaFederal` declara `^\d{1,6}$` e implementa as duas consultas:

- `/federal` e `/federal/{n}`;
- **uma tentativa** por chamada, com tempo limite `SORTEIO_CONFERENCIA_TIMEOUT_SEGUNDOS` (padrão 5),
  de modo que a pior espera é de duas chamadas, cerca de 10 s, dentro dos 15 s da SC-1097;
- a validação de *payload* da POC (`_extracao`): número inteiro, data `dd/mm/aaaa` e cinco bilhetes.

A observação (`observar`) **não muda**: três tentativas, a mesma classificação e o mesmo achado
lateral.

As duas fontes de demonstração declaram a forma de hoje (`None`) e respondem por tabela
(FR-3650):

- `REALIZADAS = {"5000": date(2015, 8, 26)}`. Só o 5000, e não o 6113: seis arquivos de teste
  declaram `6113` (o Edital 72), alguns com a fonte de demonstração, e nenhum declara `5000` ou
  `9998` (conferido em 03/11 por `grep`);
- `INCONCLUSIVA = "9998"`;
- último concurso `6114`, de 01/11/2026.

### 2. A regra pura (`sorteios/domain/conferencia.py`)

A POC (`doc/estudo-extracao-da-loteria-federal-2026-11-03/conferencia.py`) adaptada:

- `Situacao` com `estado ∈ {REALIZADO, AINDA_NAO_REALIZADO, INCONCLUSIVO, REFERENCIA_INVALIDA}`, mais
  referência, último, data do último, data da referência, instante da consulta e motivo;
- `situacao(referencia, ultimo, data_da_referencia)`, pura, já com os números na mão;
- `decisao(situacao, ato)`, que devolve `IMPEDE`, `ADVERTE`, `INFORMA` ou `NADA`, conforme a tabela
  das FR-3634 a FR-3637;
- `mensagem(situacao, ato, declarada_em)`, com as frases de [contracts/mensagens.md](contracts/mensagens.md);
- `registro(situacao, decisao)`, o dicionário da FR-3647, sem nada da resposta crua.

**Divergências da POC, deliberadas:**

| POC | Aqui | Por quê |
|---|---|---|
| `NAO_REALIZADA` → "CONFERIDA" | `AINDA_NAO_REALIZADO` → informação | 3ª decisão do usuário; SC-1095 |
| `DESCONHECIDA` | `INCONCLUSIVO` | vocabulário da spec |
| `situacao()` fazia I/O | o I/O sai para o adaptador e o orquestrador | domínio puro, como `viabilidade.py` |
| mensagem só de publicação | mensagem por ato | no congelamento, a saída é retificar antes de congelar (FR-3639) |
| zeros normalizados na leitura | normalizados na gravação (`replace_draft`) | `OcorrenciaDaFonte` é única por `(fonte, referência)` em texto: `006114` e `6114` seriam duas linhas para a mesma extração |
| sem instante da consulta | instante registrado | FR-3632, FR-3640 |

### 3. O orquestrador (`sorteios/application/conferencia.py`)

`conferir(referencias_por_fonte, *, agora) -> dict[(fonte, referencia), Situacao]`:

1. agrupa por fonte e descarta as fontes que não sabem conferir;
2. a referência fora da forma vira `REFERENCIA_INVALIDA`, sem chamada;
3. **uma** chamada `consultar_ultimo()` por fonte. Sem resposta válida, toda referência da fonte é
   `INCONCLUSIVO`, com o motivo nas palavras da FR-3641;
4. para cada referência ≤ último, uma chamada `consultar_data(n)`. A falha deixa a data `None`, e a
   situação continua `REALIZADO` (FR-3629).

E `referencias_a_conferir(conteudo, *, base=None, marcos_sorteados=frozenset())`, pura, que aplica a
FR-3633:

- percorre os métodos que governam marco por sorteio, pela mesma `marcos.metodo_que_governa` que a
  `102` usa em `_extracao_inviavel`;
- exclui os marcos sem sorteio a fazer;
- com `base`, a Retificação, mantém só as referências diferentes da do mesmo método na base.

### 4. Os quatro atos

**Padrão comum, por causa da FR-3632:**

```text
leitura sem trava  →  referencias_a_conferir  →  conferir (rede)  →  command_context()/comando_de_comissao
                                                                        └ relê o conteúdo travado
                                                                        └ referências sem situação → INCONCLUSIVO
                                                                        └ achados / recusa / registro
```

| Ato | Onde | O que muda |
|---|---|---|
| Submissão | `publish_edital.py:478` `submit_edital` | Antes de `command_context()`: snapshot sem trava, referências, `conferir`. Dentro: `validate_for_publication(..., situacoes=...)`. O CAS de `expected_revision` já garante que o conteúdo travado é o lido; a FR-3632 cobre o resto. Registro no `detalhe` do evento `SUBMETER` |
| Publicação | `publish_edital.py:686` `publish_edital` | O conteúdo é a revisão homologada (imutável), então a leitura sem trava é exata. Confere de novo, porque é outro instante (a FR-358 da `028`). Registro no evento de publicação |
| Retificação | `retificacoes.py:926` `publish_retification` | `referencias_a_conferir(content, base=conteudo_base, marcos_sorteados=...)`. `_assert_well_formed` (`:706`) recebe as situações. Sem referência introduzida, nenhuma chamada (SC-1100) |
| Congelamento | `sorteios/application/relacao.py:37` `publicar_relacao` | Antes de `comando_de_comissao`: a versão vigente agora, o método do recorte, a referência declarada (calada se registrada indisponível, como `previa._congelar_agora_inviavel`), `conferir`. Dentro: realizado → `DomainError("draw_occurrence_already_drawn", ..., 409)`; inválida ou inconclusiva → `advertencias` no dicionário devolvido; registro no `detalhe` |

**`validate_for_publication(..., situacoes=None)`.** `None` quer dizer "a conferência não rodou", e
então não há achado desta feature. É o caso da revisão e da tela de confirmar, que **não podem**
consultar (FR-3644). Esse padrão silencioso é a escolha oposta à do `ato=` padrão do módulo. Por
isso cada um dos quatro comandos tem teste que prova que a conferência rodou: a fonte substituta
conta as chamadas. É o guardião contra esquecer o argumento.

**Os achados.** Códigos novos:

| Código | Severidade |
|---|---|
| `draw_occurrence_already_drawn` | impeditivo |
| `draw_occurrence_not_checked` | advertência |
| `draw_occurrence_not_drawn_yet` | `INFO` |
| `draw_occurrence_malformed` | impeditivo (forma) |

O caminho do achado (`path`) é o do método, como na `102`, para a revisão levar ao campo.

### 5. A forma e a normalização

- `perfis._validar_forma_da_ocorrencia` (`:746`) recebe também a fonte e consulta
  `fontes.forma_da_referencia(fonte)`. Fora da forma, `ProfileValidationError` com a frase da
  FR-3626. Continua desligada na Retificação de acervo (`conferir_forma_da_ocorrencia=False`, a
  FR-514 da `035`). A Retificação que introduz a referência é coberta pela situação
  `REFERENCIA_INVALIDA` do orquestrador.
- `editais/application/draft.py:163` `replace_draft` remove os zeros à esquerda da referência de
  método da Loteria Federal **antes** de validar, no mesmo ponto e pela mesma razão de
  `derivar_linha_geral`: é por onde passam a tela e a API.

### 6. Interface

- **Campo** (`_marco.html:393`, `compor_classificacao.html:144`): rótulo "Número do concurso", ajuda
  "só o número, como 6115 — sem dígito verificador, texto ou ano" (FR-3643).
- **Conferência sob demanda** (FR-3645):
  - um `POST` htmx por método (`interface:conferir_referencia`), que lê fonte e referência do
    formulário e responde um fragmento com a mensagem;
  - permissão: a de ver a tela de origem (`edital:elaborar` na composição, a base de comissão no
    sorteio), negada por padrão;
  - recusa de fragmento com 200 e `HX-Retarget`, como o projeto já faz para htmx;
  - CSP: sem `style=`, `<style>` ou `<script>` inline; classes novas com regra na folha da gestão.
- **Depois do ato** (FR-3646):
  - na submissão e na publicação, o detalhe do Edital (`?ato=`) lê o `detalhe` do último registro
    daquele ato e mostra a advertência ou a informação, sem sessão nova;
  - no congelamento, `_desfecho_do_sorteio` já guarda o dicionário devolvido, e o template de
    `sorteio.html` mostra `advertencias`;
  - recusas aparecem como as demais: `confirmar.html` com `erro`, e a sessão `erro_do_sorteio`.

### 7. Trilha (FR-3647 a FR-3649)

`record_event(..., detalhe={"conferenciaDaReferencia": [...]})`, uma entrada por referência
conferida:

```json
{"fonte": "Loteria Federal", "referencia": "6116", "consultadaEm": "2026-11-03T19:03:48-03:00",
 "ultimo": 6114, "ultimoEm": "2026-11-01", "situacao": "AINDA_NAO_REALIZADO",
 "conclusiva": true, "decisao": "PROSSEGUIU", "motivo": ""}
```

Conferido antes de fixar:

- **Limite**: `detalhe` é `JSONField` sem limite, e o registro tem uma entrada por método, poucas
  centenas de bytes.
- **Semântica**: `detalhe` já carrega "o que o gesto alcançou" (a FR-921 da `051`). `reason`
  continua sendo o motivo humano do ato, e por isso não é usado aqui.
- **Serialização**: só tipos JSON, com datas em ISO no fuso institucional.
- **Exposição**: `auditoria/api.py` serializa `reason` e **não** `detalhe`. A tela de trilha da
  unidade lê o `detalhe` só para o escopo. Nenhum dado pessoal entra no registro.

O ato recusado não grava trilha (D-004). `logger.info("conferencia_da_referencia", extra={...,
"correlation_id": ...})` registra a conferência e a recusa.

### 8. Suíte (FR-3651, SC-1099)

- `tests/conftest.py` ganha um vigia *autouse* que substitui `LoteriaFederal.consultar_ultimo` e
  `consultar_data` por uma Caixa gravada configurável. O padrão é "último 6114, nada realizado acima
  disso", com as datas das respostas de `doc/…/respostas/`. Ele recusa qualquer `urlopen` para
  `caixa.gov.br` fora do opt-in.
- **Atenção: a Caixa gravada diz 6113 realizado**, e 7 casos declaram `6113` (o Edital 72). O padrão
  do vigia é, por isso, "nenhuma referência realizada", e a gravação só se usa nos casos desta
  feature. A conferência é ortogonal ao que esses casos testam.
- **`test_sorteio_com_a_fonte_de_producao.py`** publica e congela "no passado" com o 6098, que a
  Caixa real registra como realizado. Com a conferência, a publicação e o congelamento seriam
  recusados. A correção: o caso substitui a conferência só nas etapas em que `recuar_o_relogio` está
  ativo, e a observação continua real. Sem isso a FR-3651 falha.
- Inventário (tarefa T003): os 18 arquivos que declaram `"source": "Loteria Federal"`. Os cinco com
  `"Concurso 6100"` e afins **não** passam por validação (são de PDF), e ficam como estão. Os que
  comparam a lista inteira de achados podem ver o `INFO` novo, e a tarefa os lista antes de mudar
  qualquer expectativa.

### Roteiro local

Com `SORTEIO_FONTE_DE_DEMONSTRACAO` ligada:

- declare "Fonte de demonstração" com o concurso `5000` e submeta: recusa;
- com `9998`, a advertência;
- com `6200`, a informação.

Para a Loteria Federal de verdade sem rede, não há roteiro: é a suíte.

### 9. O reaproveitamento (emenda de 04/11/2026)

A revisão completa — diagnóstico, alternativas, recomendação, testes, riscos e critério de liberação
— está em [revisao-do-reaproveitamento.md](revisao-do-reaproveitamento.md). O desenho, em resumo
(D-009):

- `editais/domain/reaproveitamento.py::payload_do_conteudo` tira `occurrence` e `occurrenceAt` do
  método comum e do método de cada marco, depois de `remapear` e antes de `replace_draft`. O resto
  do método passa como está; a Etapa de habilitação já vem remapeada;
- `editais/domain/perfis.py::_validar_metodo_de_sorteio` ganha `exigir_a_extracao`, ligado por
  padrão. A gravação do rascunho — `validate_classification_milestones`, que só a gravação chama, e
  `validate_common_draw_method` a partir de `replace_draft` — o desliga. A publicação e a Retificação
  chamam a função direto e não o desligam;
- a ausência dos dois campos tem mensagem própria, que diz o que declarar e onde (FR-3717);
- `sorteios/application/conferencia.py::referencias_a_conferir` deixa de fora o método sem
  referência: não há o que perguntar à Caixa;
- a composição mostra, no desfecho do reaproveitamento, quantos métodos esperam a extração, e a
  escolha da origem a lista entre o que não vem (FR-3718);
- `tests/fixtures/legado.py::antes_da_116()` é o único lugar da suíte que reconstitui o acervo sem a
  forma e sem a conferência, e o corpus passa por ele (FR-3720).

Nenhuma migration, estado ou tabela. O conteúdo publicado não muda.

## Riscos

| Risco | Mitigação |
|---|---|
| `situacoes=None` esquecido num comando (passa calado) | Teste por comando que conta as chamadas à fonte substituta |
| A API da Caixa muda de forma | Degrada para inconclusivo, sem recusa. O E2E opt-in mede o contrato. O gatilho agendado é o do achado de 10/09, fora daqui |
| Bloqueio antirrobô passa a alcançar a API | Mesma degradação. A observação (dia do sorteio) seria afetada também, o que é problema anterior a esta feature |
| Latência no clique de publicar | Uma tentativa e 5 s por chamada. Medida no teste com a fonte que dorme |
| O `INFO` novo muda expectativas de testes | Inventário antes (T003) |
| Achado novo no meio da revisão de um Edital já submetido | A publicação confere de novo: um concurso que virou realizado entre submeter e publicar é recusado ali, com a saída "devolver para elaboração" |
| O reaproveitamento traz a derivação em prosa, que pode citar o concurso antigo | É regra, e a `023` copia regra. A mensagem de FR-3718 pede conferir a derivação junto da extração; revisá-la é de quem compõe |
| Um rascunho sem a extração passa a se gravar também fora do reaproveitamento | É o mesmo método que espera a extração, e a submissão recusa com a mesma indicação (FR-3717). O método pela metade continua recusado |
| Concurso realizado nos segundos entre consulta e trava | A conferência vale para o instante registrado, e a precedência na constituição continua (FR-3638) |

## Revisão crítica (03/11/2026)

As dez perguntas do usuário, respondidas contra a spec e este plano:

1. **Impede o concurso histórico com a Caixa respondendo?** Sim. A submissão, a publicação e o
   congelamento recusam (FR-3634, FR-3636), e a Retificação também, se o introduzir (FR-3635). Uma
   Retificação que muda só a data e mantém o número antigo não confere a referência (6ª decisão),
   e o congelamento pega.
2. **Protege o congelamento?** Sim. A conferência é do comando, e não da prévia (FR-3636).
3. **Afirma algo indevido sobre datas futuras?** Não. "Ainda não realizado na consulta de…" mais "a
   data prevista não é verificada pela Caixa", e a SC-1095 proíbe "validado/confirmado/conferido" por
   teste.
4. **A Caixa fora do ar paralisa?** Não. Advertência nos quatro atos, e a espera é limitada a 15 s
   (SC-1096, SC-1097).
5. **Dá para contornar pela API interna?** A tela e a API passam pelos mesmos comandos. O ponto fraco
   é `situacoes=None` silencioso, e o guardião é o teste por comando que conta as chamadas (T013).
   Um comando novo de publicação que nasça sem a conferência não é pego por esse teste. Ele é pego
   pela recusa na constituição, como hoje.
6. **As Retificações legítimas continuam possíveis?** Sim. Só o introduzido é conferido, e a
   Retificação que não toca a referência faz zero consultas (SC-1100).
7. **Há risco de chamadas excessivas?** Não. Uma principal por ato, mais uma por referência
   realizada, nenhuma em renderização, e o sob demanda só por clique.
8. **Transação e integridade estão preservadas?** Sim. A consulta é feita fora da transação, a
   decisão vale só para o conteúdo travado, e a trilha é gravada na mesma transação do ato. Nada
   append-only é tocado.
9. **Há *overengineering*?** Dois candidatos a cortar, se o usuário quiser um MVP ainda menor:
   - a **US6** (conferência sob demanda, P3): os atos já recusam, e ela só antecipa a informação;
   - o **`INFO` de ainda não realizado** na lista de achados: a informação pode ir só para o
     registro, sem achado.

   Nenhum dos dois toca a garantia.
10. **Entrega e testa isolada, sem mexer no motor?** Sim. `observar`, a substituição e a
    constituição não mudam, e a T007 prende o `observar` inalterado.

**Riscos residuais:**

- com a Caixa fora do ar, o concurso antigo passa pelos atos e só é recusado na constituição;
- concurso realizado nos segundos entre a consulta e a trava;
- a forma da API muda e a conferência degrada em silêncio para "inconclusivo", até alguém notar as
  advertências;
- a cadeia de substituição continua inexecutável contra a Caixa
  ([achado](../../doc/achado-cadeia-de-substituicao-inexecutavel-contra-a-caixa.md)).

## Complexity Tracking

Vazio: nenhuma violação da Constituição a justificar.
