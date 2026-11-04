# Implementation Plan: A jornada consolidada do candidato convocado

**Branch**: `claude/sweet-blackwell-dc658d` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/118-jornada-consolidada-do-convocado/spec.md`

> **Só documental nesta etapa.** A implementação começa em sessão própria, depois do merge, e a T001
> aplica as revisões de outras specs (D-011).

## Summary

Uma função pura nova, no molde de `portal/situacao.py`, recebe o que as views já leem — a leitura
documental da chamada, o estado do prazo, o desfecho e a política do Requerimento — e devolve as
**obrigações da convocação**: o momento da chamada, as tarefas em ordem, o que está com a comissão, o
que foi conferido, os opcionais, o Requerimento, os totais e as frases (FR-3721 a FR-3729).

Duas telas a consomem:

- o **acompanhamento**, cuja ação, com documento na chamada, passa a vir dela e a levar sempre à
  convocação (FR-3730 a FR-3734);
- a **tela da convocação**, reordenada em cinco blocos, com o que fazer agora no topo e a página só
  de histórico depois do desfecho (FR-3735 a FR-3745).

Os textos mudam em constantes, num lugar só (FR-3746 a FR-3751). A página do Requerimento ganha o
caminho de volta, o prazo e o estado do vencido sem a recusa genérica (FR-3752 a FR-3755).

Não há tabela, migration, rota, endpoint, estado gravado, mensagem nem mudança de regra (FR-3756).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)
**Primary Dependencies**: as do projeto; nenhuma nova. Playwright no grupo opcional `navegador`
**Storage**: PostgreSQL; **nenhuma migration**. O provisionamento continua protegendo 49 tabelas
**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME` próprio da worktree); jornadas no
navegador com o grupo `navegador`
**Target Platform**: portal do candidato (servidor Django, HTML sem script inline, CSP `'self'`)
**Project Type**: monólito web
**Performance Goals**: acompanhamento sem convocação com as mesmas consultas de hoje; com convocação,
número fixo (SC-1125)
**Constraints**: CSP sem `unsafe-inline` (estilo na folha `portal/static/portal/portal.css`); 375 px
sem rolagem horizontal; linguagem simples da `069`; varreduras de vocabulário com lista literal
**Scale/Scope**: três templates principais, um parcial, dois módulos de texto, um módulo novo, duas
views; nenhum comando

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — publicação imutável; nada se exclui | nada é gravado nem excluído | ✅ |
| II — o domínio decide, a tela lê | a projeção não decide desfecho, prazo nem disponibilidade; lê as fontes da `019`, da `029` e da `115` | ✅ |
| III — negar por padrão; LGPD | nenhuma rota nova, nenhum dado novo; titularidade e recusa indistinguível como hoje | ✅ |
| IV — ato em lote mostra alcance | nenhum ato | ✅ |
| V — necessidade demonstrável | a projeção é consumida por duas telas, e resolve F1–F3 do relatório | ✅ |
| VI — cenário demonstrável | os cenários A–K, pelo portal, no navegador | ✅ |

Nenhuma entrada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/118-jornada-consolidada-do-convocado/
├── spec.md
├── plan.md              # este arquivo
├── tasks.md
├── quickstart.md
├── checklists/requirements.md
└── (na implementação) rastreabilidade.md, verificacao.md, capturas/
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── portal/
│   ├── obrigacoes.py                       # NOVO: a projeção pura e as frases (FR-3721–FR-3729, FR-3746–FR-3749)
│   ├── situacao.py                         # _acao_da_convocacao lê a projeção; formato do prazo; frase do aceite
│   ├── views.py                            # acompanhamento e convocacao passam a projeção; requerimento (FR-3754)
│   ├── templates/portal/
│   │   ├── acompanhamento.html             # linha secundária do Requerimento; frase de conclusão
│   │   ├── convocacao.html                 # cinco blocos (FR-3735)
│   │   ├── _documentos_da_convocacao.html  # cartões por bloco; selos; nomes acessíveis
│   │   ├── _chamado_do_requerimento.html   # entra no bloco certo
│   │   ├── _convocacao_da_inscricao.html   # formato do prazo
│   │   └── requerimento.html               # Voltar à convocação; prazo; vencido sem rascunho
│   └── static/portal/portal.css            # selos, destaque do cartão, marcador, texto oculto
├── convocacao/application/documentos.py    # frase_do_prazo_decorrido: o núcleo da FR-3748
└── requerimentos/application/selectors.py  # explicação do enviado (FR-3752)

backend/tests/
├── unit/portal/test_obrigacoes_da_convocacao.py            # NOVO
├── unit/portal/test_situacao_da_inscricao.py               # ajustado
├── portal/test_acompanhamento_pela_situacao.py             # ajustado
├── interface/test_portal_jornada_consolidada.py            # NOVO
├── interface/test_portal_documentos_da_convocacao.py       # ajustado
├── interface/test_portal_caminho_da_convocacao.py          # ajustado
├── interface/test_portal_requerimento.py                   # ajustado
├── navegador/test_jornada_consolidada_do_convocado.py      # NOVO
└── test_vocabulario_*.py                                   # listas literais ampliadas
```

**Structure Decision**: tudo no app `portal`, onde mora a situação da `063`. A frase única do prazo
continua no módulo de documentos da convocação, porque os comandos de envio a usam nas recusas
(FR-3622 da `115`).

## Design

### A projeção (`portal/obrigacoes.py`)

```text
obrigacoes_da_convocacao(
    *, leitura, requerimento, estado_do_prazo, escrita_aberta, desfecho, vencimento
) -> Obrigacoes | None
```

- `leitura`: a `LeituraDocumental` da chamada (`convocacao/application/documentos.py`), já lida pela
  view com `leitura_da_chamada` — consultas de número fixo.
- `requerimento`: um dos cinco estados da FR-3725, traduzido na view a partir de
  `preencher_requerimento.apurar` (o que `_requerimento_da_convocacao` já consulta), ampliando o
  vocabulário de `"preencher"`, `"conferir"`, `""` para incluir *não enviado até o prazo* e *não
  enviado*. O chamado de hoje (FR-1098 da `059`) continua derivado do mesmo valor.
- `estado_do_prazo`: o de `estado_de` (019).
- `escrita_aberta`: o mesmo `pode_apresentar` que `_documentos_da_convocacao_para_a_tela` já calcula
  (`em_aberto`, `prazo_decorrido`, Processo não final). **Não há segunda conta.**
- `desfecho`: o vigente.
- Devolve `None` quando a leitura não tem item pedido: a tela é a de antes (FR-3743).

`Obrigacoes` é imutável e tem: `momento` (`ABERTA`, `ENCERRADA`, `DECIDIDA`), `tarefas` (em ordem,
cada uma com o item, a categoria e a âncora), `com_a_comissao`, `conferidos`, `opcionais`,
`requerimento`, `totais`, `frase_de_estado` e, por item, `texto` (a célula da FR-3746).

**Sem relógio e sem banco**, como `situacao_da_inscricao` (o molde da `063`). O teste de custo da
`063` que prova zero consultas na derivação ganha um irmão para esta função.

### O acompanhamento

`_acao_da_convocacao` recebe `obrigacoes`. Com `obrigacoes` presente, a tabela da FR-3730 decide
`principal`, `link` e `link_rotulo`; o Requerimento enviado vira o campo novo `secundaria` da `Acao`
(com texto e link). Sem `obrigacoes`, o caminho de hoje fica intacto (FR-3732). As frases novas são
constantes do módulo, onde a varredura e o SC-453 da `063` as leem.

A view `acompanhamento` só chama `leitura_da_chamada` quando há convocação vigente (FR-3734), como
`_requerimento_da_convocacao` já faz para o Requerimento.

### A tela da convocação

`convocacao.html` ganha os cinco blocos quando `obrigacoes` existe; sem ela, a estrutura atual com o
texto comum novo (FR-3743). O parcial `_documentos_da_convocacao.html` passa a desenhar um cartão
por chamada de *include*, com o texto pronto da projeção: o template não escreve frase de estado.

A âncora de cada tarefa é a que a `115` já usa (`#item-<id>`), e o redirecionamento do envio volta a
ela. O botão de navegação do bloco 1 é um link para a primeira âncora (D-004).

### Estilo e acessibilidade

- Na folha do portal: o selo (texto, nunca só cor), o destaque do cartão a corrigir, o marcador sem
  forma de botão de opção e a classe de texto visualmente oculto (se a folha ainda não a tiver).
  Classe citada no template precisa de regra na folha, ou o guardião de acessibilidade reprova.
- O nome acessível do botão sai de texto oculto dentro do botão; a descrição acessível do campo
  aponta para a linha de situação **e** para o limite do arquivo.
- Título `h3` por cartão, sob o `h2` do bloco.

### O Requerimento

- `requerimentos/application/selectors.py`: a explicação do enviado recebe o momento da convocação
  (FR-3752). `leitura()` já trata o vencido com rascunho; a view passa a tratar o vencido **sem**
  requerimento vigente antes de chamar `abrir_rascunho`, que hoje recusa com 409 e cai na página
  genérica (FR-3754). Nada se grava.
- `requerimento.html`: *"Voltar à convocação"* com convocação vigente; a linha do prazo.
- O aviso do envio (FR-3755) consulta se a chamada tem item pedido: uma consulta, só quando o envio
  acontece.

### A frase única do vencido

`frase_do_prazo_decorrido` passa a devolver o núcleo da FR-3748, com a hora em `HHhMM`. As recusas
dos comandos (documento e Requerimento) continuam a usá-la, e as telas compõem os complementos.

## Validação planejada

### Por requisito

| Requisito | Prova | Onde |
|---|---|---|
| FR-3721 a FR-3729, SC-1126 | tabela de combinações item × situação × momento × Requerimento; zero consultas | `unit/portal/test_obrigacoes_da_convocacao.py` |
| FR-3730 a FR-3733 | a ação por cenário A–K | `unit/portal/test_situacao_da_inscricao.py`, `portal/test_acompanhamento_pela_situacao.py` |
| FR-3734, SC-1125 | contagem de consultas com 0, 1 e 6 itens; sem convocação, igual à de antes | `portal/test_acompanhamento_pela_situacao.py` (molde do teste de custo da `063`) |
| FR-3735 a FR-3743 | ordem dos títulos, presença e ausência de blocos e formulários por cenário | `interface/test_portal_jornada_consolidada.py` |
| FR-3744, FR-3745, SC-1122 | selo em texto; nomes acessíveis únicos; Tab; foco; 375 px; CSP | `navegador/test_jornada_consolidada_do_convocado.py` |
| FR-3746 a FR-3750 | o texto literal de cada célula | unitário da projeção e `interface/test_portal_documentos_da_convocacao.py` |
| FR-3748 (recusas) | a recusa do documento e a do Requerimento com o mesmo núcleo | `integration/requerimentos/test_prazo_da_chamada.py`, `integration/convocacao/test_documentos_da_convocacao.py` |
| FR-3751 | termos proibidos nos arquivos novos | `test_vocabulario_dos_documentos_da_convocacao.py`, varredura da `063` em `portal/test_acompanhamento_pela_situacao.py` |
| FR-3752 a FR-3755 | explicação por momento; Voltar à convocação; vencido sem rascunho sem 409 e sem linha nova; aviso | `interface/test_portal_requerimento.py` |
| FR-3756 a FR-3759 | `migrate --check` sem nada a criar; rotas iguais; telas da gestão e "Minhas inscrições" sem mudança; FR-3614 | `test_dependencia_da_convocacao.py`, testes da `059` e da `115` sem edição de expectativa nesses pontos |
| SC-1117 a SC-1121, SC-1123 | cenários A–K, a 375 px e em desktop | navegador e capturas |
| SC-1124 | as quatro perguntas por cenário, com o texto literal | `verificacao.md` |

### Os cenários

Os doze cenários do relatório, montados pelas fixtures da `115` e da `059`, como no roteiro
`doc/revisao-ux-jornada-do-convocado-2026-11-04/roteiro-de-captura.py` (PR #375):

| | Cenário | O que prova |
|---|---|---|
| A | documentos sem Requerimento | ação "Você ainda precisa enviar 4 documentos"; bloco 1 na primeira tela |
| B | Requerimento sem documentos | **sem regressão**: caminho direto ao Requerimento |
| C1 | os dois, nada enviado | tarefas com o Requerimento por último; link à convocação |
| C2 | os dois, só o Requerimento enviado | **sem falsa conclusão**: o enviado é linha secundária |
| D | aproveitado da inscrição | sem "atendido"; "não precisa enviar de novo"; com a comissão |
| E | enviados, aguardando | "Nada por enquanto" + frase de conclusão |
| F | pendente com prazo em curso | "corrigir 1 e enviar 1"; selo; motivo; ordem |
| G | pendente com prazo vencido | frase única; resumo com o Requerimento não enviado; Requerimento sem 409 |
| H | tudo conferido, sem desfecho | "Conferido: de acordo com o Edital"; sem "tudo enviado" |
| I1 | aceite | "Vaga aceita" nas duas telas; frase do aceite; histórico |
| I2 | indeferido com itens não enviados | histórico sem convite; "não foi conferido antes do resultado" |
| J | pendência sem envio anterior | "Envie o arquivo" |
| K | prazo não iniciado | sem data como prazo; "Você já pode enviar" |

Mais dois de controle: **Edital sem documento e sem Requerimento** (SC-1123) e **inscrição sem
convocação** (SC-1125). As capturas, a 375 × 812 e a 1280 × 900, vão para
`specs/118-jornada-consolidada-do-convocado/capturas/`, com o mesmo nome do relatório para comparar
antes e depois.

### Testes que prendem os textos de hoje

Mudam junto, e cada mudança de expectativa é nomeada no PR de implementação (SC-1123). A lista do §8
do relatório, conferida em `fb0e1ddc` e ampliada:

| Arquivo | O que prende hoje | Muda para |
|---|---|---|
| `tests/unit/portal/test_situacao_da_inscricao.py` | `REQUERIMENTO_ENVIADO`, `SIGA_AS_INSTRUCOES`, `PRAZO_NAO_INICIADO`, "terminou em" | a tabela da FR-3730; a frase da FR-3749; o núcleo da FR-3748 |
| `tests/portal/test_acompanhamento_pela_situacao.py` | `REQUERIMENTO_ENVIADO`, `SIGA_AS_INSTRUCOES`, "Conferir o Requerimento de Matrícula enviado" | o enviado como linha secundária; a ação da projeção |
| `tests/interface/test_portal_documentos_da_convocacao.py` | "Falta enviar", "Pendente", "Atendido pelo documento", "aguardando conferência", "Envie até", "A comissão vai decidir", "terminou em" | os textos da FR-3746 e o núcleo da FR-3748 |
| `tests/interface/test_portal_caminho_da_convocacao.py` | "não decide nada sozinho" (2), "Conferir o Requerimento de Matrícula enviado", "terminou em" | o núcleo da FR-3748 (que mantém "não decide nada sozinho"); o enviado como linha secundária |
| `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` | "Falta enviar", "Pendente", "Atendido pelo documento", "aguardando conferência" (2), "A comissão vai decidir", "terminou em" | os textos da FR-3746 e o núcleo |
| `tests/integration/requerimentos/test_prazo_da_chamada.py` | "A comissão vai decidir" (2) | o núcleo da FR-3748 |
| `tests/integration/convocacao/test_documentos_da_convocacao.py` | "A comissão vai decidir" | o núcleo da FR-3748 |
| `tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py` | "Prazo para atender" | o rótulo e o formato da FR-3747 |
| `tests/interface/test_permissoes_dos_documentos_da_convocacao.py` | "Atendido pelo documento" | o texto do aproveitado da FR-3746 |
| `tests/interface/test_portal_requerimento.py` | a explicação do enviado; a recusa do vencido | FR-3752 e FR-3754 |
| `tests/test_vocabulario_dos_documentos_da_convocacao.py` | lista literal `DA_115` | acrescenta `portal/obrigacoes.py` e os parciais novos |
| `tests/test_vocabulario_da_convocacao.py`, `tests/test_vocabulario_do_requerimento.py` | listas literais | acrescentam os arquivos novos que tocam a convocação e o Requerimento |

Depois de ajustar, **a busca pelos textos antigos nos testes deve voltar vazia**, salvo onde o
teste prova que o texto antigo **não** aparece mais.

## Riscos

- **Acoplamento com a `063`.** A tabela da FR-1175 é prendida pelo SC-453; mudar sem revisar a `063`
  quebraria o guardião. Por isso a T001 aplica as revisões antes do código.
- **Varredura de vocabulário com lista literal.** Arquivo novo escapa em silêncio. A T003 o
  acrescenta antes de escrever o texto.
- **Guardião das classes da folha.** Classe nova no template sem regra na folha reprova
  `test_acessibilidade`.
- **O teste de tempo da ocupação oscila sob carga** (`CLAUDE.md`). Não é desta feature.
- **O PR #374 e o PR #375 não estão mergeados.** Os dois são documentos; a implementação não depende
  do merge, só do roteiro, que pode ser lido da branch.
- **O PR #373 (`117`) mexe na gestão.** No portal, toca só `portal/arquivos.py`, que esta feature
  não muda; conferir conflito na hora do merge.
