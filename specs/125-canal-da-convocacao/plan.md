# Implementation Plan: A convocação segue o canal

**Branch**: `claude/gifted-elbakyan-1ab054` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/125-canal-da-convocacao/spec.md`

**Estado**: plano escrito sobre as propostas D-001 a D-008 da spec, que **aguardam o usuário**. Cada
seção diz o que muda se uma delas for recusada. Nenhum código foi alterado.

## Summary

Três mudanças independentes sobre a convocação, que podem sair em três incrementos.

- **A. Visibilidade** (P1, 1ª decisão). Um predicado derivado, *visível ao candidato*, mora no seletor
  da `019`. O portal inteiro lê por ele: lista, acompanhamento, tela, endereço direto, envio e consulta
  de documento, e Requerimento da chamada. A convocação por publicação sem registro, e sem cadeia já
  comunicada, é tratada como ausente. A gestão não muda de leitura, só passa a dizer que o candidato
  ainda não vê.
- **B. Aviso e prévia** (P1, 2ª decisão). Sete campos ganham *"Este texto será mostrado ao
  candidato."*. Seis formulários da condução ganham um passo *"Conferir o texto"*, renderizado pelo
  servidor, que só aparece com texto digitado e é sempre exigido no desfecho. Esse passo mostra o texto
  composto e o número de pessoas, e assina o texto. A correção da `120` recebe o texto na prévia que já
  tem.
- **C. Vocabulário** (P2, 3ª decisão). Uma tabela por forma alimenta portal, gestão e recusas, e um
  teste varre as telas nas duas formas.

Sem migration, rota, tabela ou coluna nova. A regra do prazo não muda.

## Technical Context

**Language/Version**: Python 3.13, Django 5.x (o do `pyproject.toml`)

**Primary Dependencies**: as da `main`. Nenhuma nova.

**Storage**: PostgreSQL. Nenhuma migration; tabelas append-only intocadas.

**Testing**: pytest contra PostgreSQL (`make test-pg`); testes de seletor, de view, de comando, de
contagem de consultas (`tests/performance/`) e de vocabulário.

**Target Platform**: o monólito Django; portal do candidato e gestão, sem script novo (CSP `'self'`).

**Project Type**: aplicação web.

**Performance Goals**: lista e acompanhamento em número fixo de consultas (FR-1092 da `059`, `118`).
K-pub custa até três consultas a mais, constantes (R-002).

**Constraints**: CSP sem `unsafe-inline`; nada de 404 novo fora do inventário da `033` (R-005);
idempotência e alcance assinado preservados no passo da prévia; o repositório é público — nenhum nome
real em teste ou captura.

**Scale/Scope**: 7 superfícies do portal (A); 7 campos e 6 formulários da gestão, mais a prévia da
correção (B); cerca de 38 frases em 12 arquivos (C, [inventário](contracts/vocabulario-do-canal.md)).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| I. Linguagem ubíqua | *Publicada* e *enviada* passam a nomear fatos diferentes, com uma fonte só (R-007) | ✅ |
| II. Imutabilidade | Visibilidade derivada, sem `UPDATE` em append-only; trilha antiga intocada (R-001, R-008) | ✅ |
| III. Negar por padrão, LGPD | Convocação invisível responde como ausente, sem vazamento por diferença (R-003, R-005); o texto livre ganha aviso e prévia | ✅ |
| IV. Regras explícitas, lote | A recusa do envio e do Requerimento sai no comando; o alcance do lote e o texto são mostrados antes do ato irreversível (R-006) | ✅ |
| V. Rastreabilidade, simplicidade | Revisões escritas nas specs revistas com a anterior preservada; nenhuma camada nova; um teste por requisito e por caso-limite | ✅ |
| VI. Jornada pelo canal do ator | O candidato acha a convocação no portal assim que ela existe para o mundo, e o operador sabe quando isso acontece (FR-4000) | ✅ |

Nenhuma violação. Reavaliado depois do desenho: igual.

## Project Structure

### Documentation (this feature)

```text
specs/125-canal-da-convocacao/
├── spec.md
├── plan.md                      # este arquivo
├── research.md                  # R-001 a R-010
├── data-model.md                # a propriedade derivada e o que a prévia assina
├── quickstart.md                # roteiro de verificação
├── contracts/
│   ├── superficies-do-portal.md # A: o que cada superfície faz com a convocação invisível
│   ├── previa-do-texto.md       # B: campos, passo, assinatura
│   └── vocabulario-do-canal.md  # C: o inventário, frase por frase
├── checklists/requirements.md
└── tasks.md                     # próximo passo, /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── convocacao/
│   ├── application/selectors.py      # A: visiveis_ao_candidato, vigentes_por_inscricao, chamada_em_aberto, comunicacao_de
│   ├── application/documentos.py     # A: recusa do envio e da consulta (nao_encontrado)
│   ├── application/comunicar.py      # C: recusas e texto da trilha por canal; resultado com a referência
│   ├── application/desfechar.py      # C: recusa do não atendimento por canal
│   ├── application/fluxo.py          # B: alcance e texto composto para a prévia; C: recusa das pendentes, forma no resultado em lote
│   └── domain/vocabulario_do_canal.py# C: novo, a tabela de frases por forma
├── requerimentos/application/preencher.py   # A: lê chamada_em_aberto já filtrada (sem mudança própria, salvo docstring)
├── portal/
│   ├── views.py                      # A: convocacao (houve convocação visível), contexto da forma; C: comunicacao_de
│   ├── obrigacoes.py                 # C: PRAZO_NAO_INICIADO por canal; linha_da_substituida "Enviada em"
│   └── templates/portal/{convocacao,_obrigacoes_da_convocacao,_convocacao_da_inscricao}.html   # C
└── interface/
    ├── views.py                      # B: etapa de conferência nos seis POSTs da condução
    └── templates/interface/
        ├── convocacao.html           # B: avisos, rótulo do derivado, bloco da prévia; C: frases
        ├── _conferir_o_texto.html    # B: novo, o bloco da prévia
        ├── _correcao_da_convocacao.html, _resultado_da_comunicacao.html,
        │   _vencimento_da_convocacao.html, convocacao_historico.html   # B/C
backend/tests/                        # testes novos e revistos (R-010)
```

**Fora do alcance de propósito:** `sorteio.html`, `compor_classificacao.html`, `loteria_federal.py` e
`ocorrencia.py`, que a sessão paralela do sorteio altera. Nenhum deles é tocado.

## Design

### A. Visibilidade (FR-3981 a FR-3990)

1. `visiveis_ao_candidato(convocacoes)` implementa a FR-3981 com a D-001, pelos três passos da
   R-002. A convocação recebe, em memória, a forma lida (`forma_lida`), para que C não leia de novo.
2. `vigentes_por_inscricao` escolhe a vigente mais recente **entre as visíveis**. Lista,
   acompanhamento, tela e Requerimento (`_convocacao_do_requerimento`) continuam chamando o mesmo
   seletor.
3. `chamada_em_aberto` filtra pela visibilidade (D-003, R-004).
4. Na view `convocacao`, *houve convocação no recorte* passa a contar só as visíveis (R-003), e
   `_registrar_leitura_da_convocacao` não roda sem convocação visível (FR-3983).
5. `apresentar` e a consulta do arquivo apresentado recusam com `nao_encontrado()` (R-005).
6. Gestão: nada muda na leitura. A frase *"o candidato ainda não vê"* é de C (FR-4000), com a D-007.

**Se a D-001 for recusada:** o passo 2 da R-002 sai, e a visibilidade olha só a própria convocação. A
correção de convocação publicada some do portal até a publicação da correção. **Se a D-002 for
recusada:** desfecho registrado torna a convocação visível, com uma condição a mais no predicado.

### B. Aviso e prévia (FR-3991 a FR-3997)

1. Os sete campos recebem o aviso visível, ligado por `aria-describedby` (contrato
   [`previa-do-texto.md`](contracts/previa-do-texto.md)). O fundamento derivado, onde já é mostrado,
   ganha o rótulo *"O candidato lerá este fundamento"*.
2. Os seis POSTs da condução ganham a etapa de conferência (R-006). A composição vem de `fluxo` e de
   `fundamento.com_complemento`, e o número vem do alcance assinado. A view devolve a tela com o bloco
   `_conferir_o_texto.html`, sem praticar nada.
3. A confirmação confere a chave, o alcance e o resumo do texto. Se o texto divergir, ela recusa com a
   prévia nova à vista.
4. A correção da `120` passa a mostrar o complemento composto na prévia que já tem.

**Se a D-004 for recusada** (passo sempre): muda só a condição da etapa.

### C. Vocabulário (FR-3998 a FR-4004)

1. `vocabulario_do_canal.py` traz as frases por forma, extraídas do
   [inventário](contracts/vocabulario-do-canal.md).
2. Portal: `comunicacao_de` devolve forma, instante e referência. Os três templates trocam
   *"Comunicação enviada em"* e *"contado do envio da comunicação"* pelas frases do canal.
   `PRAZO_NAO_INICIADO` passa a ser por canal, e `linha_da_substituida` passa a dizer *"Enviada em"*
   (D-008).
3. Gestão: pastilha, situação, cartão, histórico, seção das pendentes, botões, confirmação do registro
   com a referência, a frase de `_vencimento_da_convocacao.html` e *"A comunicação sai no mesmo ato"*.
4. Recusas: o vencimento anterior ao envio, a emissão em estado indeterminado, o não atendimento antes
   do envio e *nenhuma comunicação pendente*, todas por canal.
5. Trilha: o texto dos registros novos de publicação muda (R-008).

### Ordem e entrega

Três incrementos, cada um num PR, nesta ordem: **A → B → C**. A e C mexem nos mesmos templates do
portal, mas em linhas diferentes. B é só da gestão. Os três podem ir num PR só, se o usuário preferir.

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| Convocações K-pub já existentes na instalação, algumas com documento enviado | No dia da implantação elas somem do portal até o registro da publicação | Consulta no quickstart para contá-las antes; nada se apaga; decisão do usuário sobre registrar antes |
| Contagem de consultas | Os testes de desempenho da `059`/`118` reprovam se o predicado ler por item | R-002 por conjunto, e cenário K-pub com N inscrições nos testes |
| O passo da prévia no desfecho é sempre exigido | Um clique a mais em todo desfecho | D-004 limita o passo a texto digitado; o desfecho exige fundamento, então o clique é o preço da decisão |
| Testes que prendem a redação antiga | Dezenas de asserções de *"envio da comunicação"* e de visibilidade em K | Mudança citando a revisão (R-010); a suíte inteira contra PostgreSQL antes de cada PR |
| Conflito de arquivo com PRs abertos | O README e as specs da `118`/`121` também são editados pelo #409 (`123`) e pela `124` | Linhas diferentes; rebase no merge, que é do usuário |
| A sessão paralela do sorteio | Colisão de arquivo | Nenhum arquivo dela é tocado |

## Estimativa

| Incremento | Código | Testes | Total |
|---|---|---|---|
| A. Visibilidade | ~0,5 dia | ~0,5 dia | **~1 dia** |
| B. Aviso e prévia | ~0,75 dia | ~0,75 dia | **~1,5 dia** |
| C. Vocabulário | ~0,5 dia | ~0,5 dia | **~1 dia** |
| Rastreabilidade, verificação no navegador, suíte | | | **~0,5 dia** |

Cerca de **4 dias de sessão**, com a suíte contra PostgreSQL (~10 min) ao fim de cada incremento.

## Complexity Tracking

Nenhuma violação constitucional a justificar.
