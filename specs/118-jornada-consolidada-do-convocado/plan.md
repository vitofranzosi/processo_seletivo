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
    *, leitura, requerimento, estado_do_prazo, causa_do_fechamento, desfecho, vencimento
) -> Obrigacoes | None
```

- `leitura`: a `LeituraDocumental` da chamada (`convocacao/application/documentos.py`), já lida pela
  view com `leitura_da_chamada` — consultas de número fixo.
- `requerimento`: as três leituras da FR-3725, todas da `Disponibilidade` que
  `preencher_requerimento.apurar` já devolve (o que `_requerimento_da_convocacao` consulta): o
  `momento` declarado e `exigido` (exigência), `enviado` e `status_do_requerimento` (situação),
  `disponivel` e `prazo_decorrido` (disponibilidade). A tabela da FR-3725 roda **dentro** da projeção,
  com a exigência e a situação antes da disponibilidade (D-016). O chamado de hoje (FR-1098 da `059`)
  continua derivado da mesma `Disponibilidade`.
- `estado_do_prazo`: o de `estado_de` (019).
- `causa_do_fechamento`: `None`, `PROCESSO` ou `PRAZO`, das mesmas três condições que
  `_documentos_da_convocacao_para_a_tela` já calcula para `pode_apresentar` (`em_aberto`,
  `prazo_decorrido`, Processo fora de `PROCESSO_FINAL`), com o Processo antes do prazo (D-015).
  **Não há segunda conta**: a view passa a devolver a causa junto do booleano. `pode_apresentar`
  continua sendo `aberta and causa_do_fechamento is None` — o desfecho fecha a escrita antes de
  qualquer causa, e a causa só existe com a chamada em aberto (revisão independente, achado 2). Na
  projeção, isso é `momento == ABERTA`.
- `desfecho`: o vigente.
- Devolve `None` quando a leitura não tem item pedido: a tela é a de antes (FR-3743).

`Obrigacoes` é imutável e tem: `momento` (`ABERTA`, `ENCERRADA_PELO_PRAZO`, `ENCERRADA_PELO_PROCESSO`,
`DECIDIDA`), `tarefas` (em ordem,
cada uma com o item, a categoria e a âncora), `com_a_comissao`, `conferidos`, `opcionais`,
`requerimento`, `totais`, `frase_de_estado` e, por item, `texto` (a célula da FR-3746).

**Sem relógio e sem banco**, como `situacao_da_inscricao` (o molde da `063`). O teste de custo da
`063` que prova zero consultas na derivação ganha um irmão para esta função.

### O acompanhamento

`_acao_da_convocacao` recebe `obrigacoes`. Com `obrigacoes` presente, a tabela da FR-3730 decide
`principal`, `link` e `link_rotulo`; o Requerimento enviado vira o campo novo `secundaria` da `Acao`
(com texto e link). Sem `obrigacoes` — a chamada sem documento —, o caminho de hoje fica **intacto**,
inclusive `REQUERIMENTO_ENVIADO` como ação principal (FR-3732, D-017); mudam só os textos comuns.
A única adição sem documento é a linha informativa da FR-3732 (D-019): um campo `informativo` da
`Acao`, preenchido a partir da mesma `Disponibilidade` que `_requerimento_da_convocacao` já obtém
(hoje ela devolve `""` com prazo decorrido; passa a devolver também a marca do não enviado) e do
desfecho já lido. Nenhuma consulta nova; o teste de custo da `063` prova. As frases novas são
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
| FR-3721 a FR-3729, SC-1126 | tabela de combinações item × situação × os quatro momentos × as seis linhas do Requerimento; Processo e prazo juntos (documentos *encerrada pelo Processo*, Requerimento *não enviado até o prazo*); desfecho com Processo aberto sem formulário; zero consultas | `unit/portal/test_obrigacoes_da_convocacao.py` |
| FR-3730 a FR-3733 | a ação por cenário, inclusive B2 e M | `unit/portal/test_situacao_da_inscricao.py`, `portal/test_acompanhamento_pela_situacao.py` |
| FR-3734, SC-1125 | contagem de consultas com 0, 1 e 6 itens; sem convocação, igual à de antes | `portal/test_acompanhamento_pela_situacao.py` (molde do teste de custo da `063`) |
| FR-3735 a FR-3743 | ordem dos títulos, presença e ausência de blocos e formulários por cenário, inclusive L e M | `interface/test_portal_jornada_consolidada.py` |
| FR-3744, FR-3745, SC-1122 | selo em texto; nomes acessíveis únicos; Tab; foco; 375 px; CSP | `navegador/test_jornada_consolidada_do_convocado.py` |
| FR-3746 a FR-3750 | o texto literal de cada célula, nas quatro colunas; K2 sem data em nenhum cartão | unitário da projeção e `interface/test_portal_documentos_da_convocacao.py` |
| FR-3748 (recusas) | a recusa do documento e a do Requerimento com o mesmo núcleo; em M, a recusa do documento **não** usa o núcleo | `integration/requerimentos/test_prazo_da_chamada.py`, `integration/convocacao/test_documentos_da_convocacao.py` |
| FR-3751 | termos proibidos nos arquivos novos | `test_vocabulario_dos_documentos_da_convocacao.py`, varredura da `063` em `portal/test_acompanhamento_pela_situacao.py` |
| FR-3752 a FR-3755 | explicação por momento; Voltar à convocação; vencido sem rascunho sem 409 e sem linha nova; aviso | `interface/test_portal_requerimento.py` |
| FR-3756: **sem escrita** | contagem de linhas de todas as tabelas antes e depois de um GET de cada tela em cada cenário: só a leitura da convocação na trilha muda; o GET da FR-3754 não cria rascunho | `interface/test_portal_jornada_consolidada.py` |
| FR-3756: **autorização e privacidade** | inscrição alheia e inexistente com a mesma recusa nas três telas; a página do Requerimento continua com resposta privada; nenhum dado pessoal novo em URL | os testes de titularidade da `059` e da `029` sem edição; um caso novo por tela em `interface/test_portal_jornada_consolidada.py` |
| FR-3756 a FR-3759: **sem mudança de regra** | `migrate --check` sem nada a criar; rotas iguais; telas da gestão e "Minhas inscrições" sem mudança; FR-3614 | `test_dependencia_da_convocacao.py`, testes da `059` e da `115` sem edição de expectativa nesses pontos |
| SC-1117 a SC-1121, SC-1123, SC-1127, SC-1128 | os cenários, a 375 px e em desktop | navegador e capturas |
| SC-1124 | as quatro perguntas por cenário, com o texto literal | `verificacao.md` |

### Os cenários

Os doze cenários do relatório, montados pelas fixtures da `115` e da `059`, como no roteiro
`doc/revisao-ux-jornada-do-convocado-2026-11-04/roteiro-de-captura.py` (PR #375), e cinco de controle
que a revisão do PR pediu:

| | Cenário | O que prova |
|---|---|---|
| A | documentos sem Requerimento | ação "Você ainda precisa enviar 4 documentos"; bloco 1 na primeira tela |
| B | Requerimento sem documentos, a preencher | **sem regressão**: caminho direto ao Requerimento |
| C1 | os dois, nada enviado | tarefas com o Requerimento por último; link à convocação |
| C2 | os dois, só o Requerimento enviado | **sem falsa conclusão**: o enviado é linha secundária |
| D | aproveitado da inscrição | sem "atendido"; "não precisa enviar de novo"; com a comissão |
| E | enviados, aguardando | "Nada por enquanto" + frase de conclusão |
| F | pendente com prazo em curso | "corrigir 1 e enviar 1"; selo; motivo; ordem |
| G | pendente com prazo vencido | núcleo do vencido; resumo com o Requerimento não enviado; Requerimento sem 409 |
| H | tudo conferido, sem desfecho | "Conferido: de acordo com o Edital"; sem "tudo enviado" |
| I1 | aceite | "Vaga aceita" nas duas telas; frase do aceite; histórico |
| I2 | indeferido com itens não enviados | histórico sem convite; "não foi conferido antes do resultado" |
| J | pendência sem envio anterior | "Envie o arquivo" |
| K | prazo não iniciado | sem data como prazo; "Você já pode enviar" |
| **B2** | Requerimento sem documentos, já enviado | **sem regressão**: "Seu Requerimento de Matrícula foi enviado." continua a ação principal (D-017) |
| **L** | só um facultativo sem envio, nenhuma tarefa | bloco *Documentos opcionais* com o envio; frase de conclusão; nenhuma contagem (D-018) |
| **M** | Processo encerrado, chamada em aberto, prazo correndo, um item recebido, Requerimento a preencher | "O envio pelo portal está encerrado"; nenhuma menção a prazo vencido; nenhuma promessa de conferência; sem formulário de documento; o Requerimento continua alcançável no bloco 3, porque a política o admite (D-015, FR-3741) |
| **N** | indeferido, com documento, Requerimento pedido na convocação e nunca enviado (com e sem rascunho) | "Requerimento de Matrícula: não enviado." na convocação; a página dele diz "não enviado", nunca "Ainda não é a hora"; nunca "não pedido" (D-016, FR-3754) |
| **K2** | prazo não iniciado, com um pendente, uma tarefa e um opcional | nenhum cartão, opcional ou frase de conclusão com data; "Você já pode enviar" (FR-3749) |
| **G0** | sem documento, Requerimento pedido na convocação e não enviado (com e sem rascunho), prazo decorrido | ação de hoje + "Requerimento de Matrícula: não enviado até o prazo. Não é mais possível enviá-lo pelo portal.", sem link; mesmas consultas; nada gravado (D-019, SC-1128) |
| **N0** | sem documento, Requerimento pedido e não enviado, desfecho registrado | ação de hoje + "Requerimento de Matrícula: não enviado.", sem link; a página dele diz "não enviado" (D-019, FR-3754, SC-1128) |

Mais dois de controle: **Edital sem documento e sem Requerimento** (SC-1123) e **inscrição sem
convocação** (SC-1125). As capturas, a 375 × 812 e a 1280 × 900, vão para
`specs/118-jornada-consolidada-do-convocado/capturas/`, com o mesmo nome do relatório para comparar
antes e depois.

### Testes que prendem os textos de hoje

Mudam junto, e cada mudança de expectativa é nomeada **por cenário** no PR de implementação
(SC-1123). Uma expectativa só muda quando o texto que ela prende saiu da spec; a garantia que o teste
dava — ausência de convite, de vocabulário proibido, de dado de quem conferiu — MUST continuar
provada, no mesmo teste ou num novo. A lista do §8 do relatório, conferida em `fb0e1ddc` e ampliada:

| Arquivo | O que prende hoje | Muda para |
|---|---|---|
| `tests/unit/portal/test_situacao_da_inscricao.py` | `REQUERIMENTO_ENVIADO`, `SIGA_AS_INSTRUCOES`, `PRAZO_NAO_INICIADO`, "terminou em" | a tabela da FR-3730 com documento; **sem documento, `REQUERIMENTO_ENVIADO` e `SIGA_AS_INSTRUCOES` continuam** (B, B2); a frase da FR-3749; o núcleo da FR-3748 |
| `tests/portal/test_acompanhamento_pela_situacao.py` | `REQUERIMENTO_ENVIADO`, `SIGA_AS_INSTRUCOES`, "Conferir o Requerimento de Matrícula enviado" | com documento, o enviado como linha secundária; sem documento, como hoje |
| `tests/interface/test_portal_documentos_da_convocacao.py` | "Falta enviar", "Pendente", "Atendido pelo documento", "aguardando conferência", "Envie até", "A comissão vai decidir", "terminou em" | os textos da FR-3746 e o núcleo da FR-3748; **"Falta enviar" continua** |
| `tests/interface/test_portal_caminho_da_convocacao.py` | "não decide nada sozinho" (2), "Conferir o Requerimento de Matrícula enviado", "terminou em" | o núcleo da FR-3748 (que mantém "não decide nada sozinho"); o link de conferir continua, em lugar que depende de haver documento |
| `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` | "Falta enviar", "Pendente", "Atendido pelo documento", "aguardando conferência" (2), "A comissão vai decidir", "terminou em" | os textos da FR-3746 e o núcleo; **"Falta enviar" continua** |
| `tests/integration/requerimentos/test_prazo_da_chamada.py` | "A comissão vai decidir" (2) | o núcleo da FR-3748 |
| `tests/integration/convocacao/test_documentos_da_convocacao.py` | "A comissão vai decidir" | o núcleo da FR-3748 |
| `tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py` | "Prazo para atender" | o rótulo e o formato da FR-3747 |
| `tests/interface/test_permissoes_dos_documentos_da_convocacao.py` | "Atendido pelo documento" | o texto do aproveitado da FR-3746; a garantia de permissão não muda |
| `tests/interface/test_portal_requerimento.py` | a explicação do enviado; a recusa do vencido | FR-3752 e FR-3754 |
| `tests/test_vocabulario_dos_documentos_da_convocacao.py` | lista literal `DA_115` | acrescenta `portal/obrigacoes.py` e os parciais novos |
| `tests/test_vocabulario_da_convocacao.py`, `tests/test_vocabulario_do_requerimento.py` | listas literais | acrescentam os arquivos novos que tocam a convocação e o Requerimento |

**Os textos que saem**, e só eles, voltam a busca vazia nos testes (salvo onde o teste prova que o
texto não aparece mais):

- *"Atendido pelo documento enviado na inscrição"*;
- *"aguardando conferência"* como sufixo do item (o selo *"Aguardando conferência"* entra);
- *"Pendente: "* como início da linha do item e *"Envie outro arquivo"*;
- *"Envie até "* como cabeçalho da lista;
- *"A comissão vai decidir."* e *"O prazo informado nesta convocação já passou"*;
- *"Prazo para atender"*;
- *"Situação registrada: "*;
- *"Se algo mudar e você for convocado"* **só** nos casos com convocação vigente.

Ficam, e não entram na busca: *"Falta enviar."*, *"Não se aplica: "*, *"Conferir o Requerimento de
Matrícula enviado"*, *"Seu Requerimento de Matrícula foi enviado."* (sem documento), *"Siga as
instruções do Edital para esta convocação."* (sem documento e sem Requerimento) e *"não decide nada
sozinho"*.

### Ajustes da revisão do PR (04/11/2026)

| Conflito | Decisão | Teste planejado |
|---|---|---|
| Opcionais no bloco que some sem tarefa; facultativo em duas categorias | O bloco 3 existe também só com opcionais; classificação por situação e depois por estado (D-018; FR-3722, FR-3735, FR-3738) | cenário L; tabela de combinações com "exatamente uma categoria" |
| "O prazo terminou" com o Processo encerrado; promessa de conferência que o sistema recusa | Causa do fechamento derivada; Processo prevalece; texto próprio, sem prazo vencido nem conferência futura (D-015; FR-3721, FR-3741, FR-3746, FR-3748) | cenário M; recusa do documento em M sem o núcleo |
| "Ainda indisponível" lido como "não pedido" depois do desfecho | Exigência e situação antes da disponibilidade (D-016; FR-3725) | cenário N, com e sem rascunho; as seis linhas da FR-3725 no unitário |
| Data como prazo nos cartões e no opcional antes da comunicação | O prazo não iniciado prevalece sobre toda menção; "Você já pode enviar" só com escrita aberta (FR-3746, FR-3749, FR-3728) | cenário K2 |
| Sem documento e com o Requerimento enviado: ação indefinida | A de hoje, inclusive o enviado como ação principal (D-017; FR-3732) | cenário B2; os testes da `063` sobre B e B2 sem edição, salvo texto comum |
| FR-3756 proibia mudar as views que as tarefas mudam | Proíbe escrita, rota, comando e regra; as views leem a projeção, com titularidade, recusas e resposta privada iguais (FR-3756) | contagem de linhas antes e depois dos GET; recusa indistinguível nas três telas |
| Revisão independente (04/11): Processo e prazo juntos; `pode_apresentar` sem o desfecho; `estado_de` descrito errado; Requerimento em M; página do Requerimento em N; N e G sem documento; termo "opcional sem conferência"; Requerimento *na inscrição*; motivo em J; D-007 | FR-3725 lê desfecho e prazo da política; `pode_apresentar` mantém o desfecho; FR-3721 corrigida; FR-3741 diz onde fica o Requerimento; FR-3754 cobre o desfecho sem envio; N e G com documento, e a lacuna sem documento registrada; "opcional a enviar"; linhas 3 e 4 para qualquer momento; o motivo no bloco 1 e a pendência primeiro | cenário M com Requerimento; N na página do Requerimento; Processo e prazo juntos no unitário; desfecho com Processo aberto sem formulário |
| Encerramento (04/11): sem documento, o Requerimento não enviado depois do prazo ou do desfecho não aparecia fora da página dele | Exceção informativa, sem link, só com a política fechada; ação principal de hoje (D-019; FR-3732, FR-3743) | cenários G0 e N0; B e B2 sem a linha; contagem de consultas igual |
| Busca genérica por "textos antigos" incluía textos que continuam | Lista explícita do que sai e do que fica (acima) | a busca da T032 sobre a lista |

## Riscos

- **Acoplamento com a `063`.** A tabela da FR-1175 é prendida pelo SC-453; mudar sem revisar a `063`
  quebraria o guardião. Por isso a T001 aplica as revisões antes do código.
- **Varredura de vocabulário com lista literal.** Arquivo novo escapa em silêncio. A T003 o
  acrescenta antes de escrever o texto.
- **Guardião das classes da folha.** Classe nova no template sem regra na folha reprova
  `test_acessibilidade`.
- **O teste de tempo da ocupação oscila sob carga** (`CLAUDE.md`). Não é desta feature.
- **O roteiro de captura está na `main`** desde o merge do #375 (04/11/2026); o #374 foi encerrado
  como superado. Nenhum dos dois é código.
- **O PR #373 (`117`) mexe na gestão.** No portal, toca só `portal/arquivos.py`, que esta feature
  não muda; conferir conflito na hora do merge.
