# Implementation Plan: Documentos e conferência na convocação

**Branch**: `claude/nice-zhukovsky-0b4397` | **Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/115-documentos-na-convocacao/spec.md`

> **Este plano não autoriza implementar.** A spec aguarda a revisão do usuário, e as decisões D-008 a
> D-018 são propostas. Se a revisão mudar alguma, este plano e as tarefas mudam junto.

## Summary

O Documento Exigido ganha **momento** (inscrição ou convocação) e **aproveitamento** opcional. A
inscrição passa a ver só os da inscrição. A raiz de cada chamada grava, na mesma transação, a
**lista da convocação**, no molde do `ItemDaListaExigida` da `044`.

O titular apresenta arquivos na tela da convocação do portal, com as mesmas validações,
armazenamento e hash da inscrição. Cada envio é uma **apresentação** append-only, e o aproveitamento
é uma apresentação **por referência** ao `DocumentoSubmetido`, sem cópia.

Quem pode conferir registra **conferências** append-only por item. O aceite e a regularização ganham
uma guarda que lê o estado derivado dos itens. A conferência é autorizada por um predicado único, que
acrescenta à base atual do desfecho uma **alocação à conferência**, no molde da `AlocacaoEtapa`.

Ainda neste plano: a trilha registra a consulta ao dossiê (A-07) e os atos novos, e o PDF ganha a
seção neutra da convocação.

São três tabelas append-only novas (46 → 49 no provisionamento), uma tabela de alocação e dois campos
no Documento Exigido. Não há desfecho novo, estado gravado nem mensagem nova.

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)
**Primary Dependencies**: as do projeto; nenhuma nova. Playwright no grupo opcional `navegador`, que já
existe (`107`)
**Storage**: PostgreSQL. Migrations em:
- `editais`: dois campos no Documento Exigido;
- `convocacao`: três tabelas append-only, com gatilhos no molde de `inscricoes/0005`;
- `comissoes`: a alocação à conferência.

Os arquivos vão ao `ArmazenamentoPrivado` (`inscricoes/storage.py`), num prefixo próprio
(`convocacoes/<raiz_da_chamada>/<uuid4>.pdf`).
**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME` próprio da worktree). Também:
- casos transacionais para trava, gatilho e privilégio (`como_producao`);
- `tests/navegador/` para as três jornadas, com o grupo `navegador`.
**Target Platform**: servidor Linux (produção), macOS (desenvolvimento)
**Project Type**: aplicação web (gestão e portal em templates Django)
**Performance Goals**:
- a condução da convocação ganha contagens por linha numa consulta agregada, sem consulta por linha;
- o orçamento de consultas da tela existente cresce em, no máximo, uma consulta constante, provado na
  suíte.
**Constraints**:
- CSP sem inline: estilo em arquivo e classe com regra na folha;
- vocabulário proibido da FR-3610, com varredura literal (lista de templates explícita);
- nenhum `FOR UPDATE` em tabela append-only (`tests/guardiao_de_travas.py`): a serialização trava a
  linha da `Inscricao`;
- `convocacao` continua sem ser importada por `ocupacao`, `classificacao` e `resultados`
  (`tests/test_dependencia_da_convocacao.py`);
- `inscricoes` não importa `convocacao`.
**Scale/Scope**: dezenas de convocados por chamada; poucos documentos por pessoa.

## Constitution Check

| Princípio | Como a feature o respeita |
|---|---|
| I. Linguagem ubíqua; nada se exclui | "Apto para formalização" × "encaminhado" × vínculo; "conforme" ≠ "autêntico"; três tabelas append-only em duas camadas; arquivo nunca removido (FR-3615) |
| II. Integridade normativa e imutabilidade | Momento e aproveitamento publicados e não retificáveis (D-014); lista congelada por chamada (FR-3573); seção do PDF derivada dos dados; Edital publicado não se regenera |
| III. Segurança, LGPD, auditoria | Predicado único (FR-3595); recusa indistinguível; trilha com ator e unidade (FR-3602 a FR-3604); A-07 resolvido; minimização como benefício principal; avaliação de LGPD na spec |
| IV. Regras explícitas e consistência | A guarda do aceite está no command do desfecho, e não só na tela; estados derivados, sem máquina nova (D-004); serialização na `Inscricao`; nenhum lote novo |
| V. Simplicidade, rastreabilidade | Cada entidade tem a regra que a consome (tabela de conflitos da spec); `rastreabilidade.md` com FR, SC e casos-limite na implementação |
| VI. Jornada demonstrável | US1, US2 e US3 pelo portal e pela gestão, e no navegador (SC-1089) |

**Gates**: sem violação. O único alcance novo de autorização, o membro alocado, está explícito e
restrito (FR-3595 a FR-3601). Nenhuma entrada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/115-documentos-na-convocacao/
├── spec.md
├── plan.md              # este arquivo
├── data-model.md        # entidades, constraints e gatilhos
├── quickstart.md        # roteiro dos três cenários e dos negativos
├── tasks.md
├── checklists/
│   └── requirements.md
└── rastreabilidade.md   # criada na implementação (T049), cobrindo todo FR, SC e caso-limite
```

### Source Code (repository root)

Caminhos relativos a `backend/processo_seletivo/`.

```text
editais/
├── models/documentos.py            # + momento, + aproveita (UUID do requisito; não FK, como requisito_id)
├── domain/documentos.py            # da_inscricao()/da_convocacao(): filtro por momento antes da aplicabilidade
├── domain/validation.py            # schema publicado + regras do aproveitamento (FR-3566)
├── domain/mutabilidade.py          # (documentRequirements, moment|reusesRequirementId) não retificáveis
├── domain/secoes.py                # seção "documentos-na-convocacao" nos catálogos da 054 e da 069
├── application/draft.py            # os dois campos viajam no payload (delete + bulk_create)
└── migrations/0024_momento_do_documento_exigido.py
interface/forms.py, interface/templates/interface/_documento.html   # elaboração: "Quando é pedido" e "Atendido pelo documento da inscrição"
interface/revisao.py, publicacoes/domain/alteracoes.py               # rótulos dos campos novos
publicacoes/
├── application/publish_edital.py   # moment, reusesRequirementId na forma publicada
├── domain/elevacao.py              # degrau 18: {"moment": "AT_ENROLLMENT", "reusesRequirementId": None}
└── infrastructure/pdf.py, infrastructure/apresentacao.py   # _documentos_exigidos filtra; _documentos_na_convocacao nova
shared/canonical.py                 # SCHEMA_VERSION 17 → 18
duvidas/domain/cobertura.py         # o assistente passa a conhecer o momento (sem mudar o que responde)
inscricoes/application/
├── lista_exigida.py, submissao.py, rascunho.py   # usam da_inscricao(); nada mais muda
convocacao/
├── models.py                       # ItemDaListaDaConvocacao, ApresentacaoDeDocumento, ConferenciaDeDocumento
├── domain/documentos.py            # estado derivado do item e da convocação (puro); guarda do aceite
├── domain/nomes.py                 # códigos de recusa novos
├── application/lista.py            # gravar_lista_da_chamada(raiz), raiz_da_chamada(convocacao)
├── application/apresentar.py       # apresentar(), com trava na Inscricao e idempotência
├── application/conferir.py         # conferir(), com o predicado e a exigência de abertura
├── application/convocar.py, fluxo.py   # chamam gravar_lista_da_chamada na raiz
├── application/desfechar.py        # a guarda da FR-3592 antes de gravar
├── application/selectors.py        # documentos_da_chamada(), contagens agregadas por recorte
└── migrations/0005_documentos_da_convocacao.py (+ gatilhos)
comissoes/
├── models.py                       # AlocacaoAConferencia(membro, edital, perfil_id NULL = todos, ativo…)
├── domain/autorizacao.py           # pode_conferir_documentos(ator, processo, *, edital, perfil_id) → Base | None
├── application/alocacao.py         # alocar/revogar, com trilha
└── migrations/00NN_alocacao_a_conferencia.py
seguranca/papeis.py                 # TABELAS_APPEND_ONLY + 3 (46 → 49)
auditoria/selectors.py              # _atos_da_conducao inclui apresentação, conferência e alocação
interface/
├── views.py                        # inscricao_recebida grava CONSULTAR_DOSSIE (A-07); documentos_da_convocacao; documento_da_convocacao; conferir_documento_view; alocacoes (conferência)
├── urls.py
├── templates/interface/convocacao.html          # resumo documental por linha, ordem, "Apto para formalização", fundamento pré-redigido
├── templates/interface/convocacao_documentos.html   # nova, filha da condução
├── templates/interface/alocacoes.html           # seção "Conferência dos documentos da convocação"
└── static/interface/telas/convocacao_documentos.css
portal/
├── views.py                        # convocacao: lista e estados; apresentar_documento; documento_da_convocacao (titular)
├── situacao.py                     # frases da FR-3612
├── templates/portal/convocacao.html + _documentos_da_convocacao.html
└── static/portal/portal.css
```

**Structure Decision**: as três tabelas ficam na `convocacao`, porque pertencem à chamada (D-009), e a
`convocacao` já conhece `inscricoes` (FK da `Convocacao`). A alocação fica na `comissoes`, ao lado da
`AlocacaoEtapa`, porque é competência da comissão (D-010). Nenhum app novo.

## Desenho, em decisões de implementação

**R-001 — Aproveitamento por UUID do requisito, e não FK.** O Documento Exigido é recriado a cada
gravação do rascunho (`draft.py`, `delete` + `bulk_create`). Uma FK entre linhas do mesmo rascunho se
perderia na recriação. O aproveitamento guarda o `id` do requisito aproveitado, como o
`ItemDaListaExigida.requisito_id`, e a validação confere a coerência na publicação.

**R-002 — A raiz da chamada.** `raiz_da_chamada(convocacao)` segue `convocacao_anterior` até a linha
sem anterior. A lista, as apresentações e as conferências têm FK `PROTECT` para a raiz. A sucessora
não grava nada (D-009). Escolhida a raiz, e não "a vigente", porque a vigente muda a cada correção.

**R-003 — Gravação da lista.** `gravar_lista_da_chamada` roda dentro do `convocar` (raiz) e do lote de
titulares. Ela:
- lê a versão consolidada vigente;
- filtra `da_convocacao()`;
- chama `aplicabilidade(conteudo, profile_id=…, modality_id=…)` com os dados da inscrição;
- faz `bulk_create`.

No mesmo passo, cria a apresentação por referência dos itens com aproveitamento atendido (FR-3576).
O gatilho de coerência exige `gravada_em = convocacao.criado_em` e raiz sem anterior.

**R-004 — Apresentação.** Ordem dentro de `transaction.atomic`:
1. `select_for_update` na `Inscricao`, que não é append-only;
2. conferir a titularidade, a chamada em aberto, o vencimento não decorrido e o item aplicável;
3. `aceitar()` e `resumo()` de `shared/arquivos.py`;
4. hash igual ao da vigente devolve a vigente;
5. senão, `numero = max + 1`.

A unicidade `(item, numero)` é a segunda camada. A idempotência usa `reserve()`, como os commands da
comissão. O arquivo é gravado antes do `INSERT` e apagado em `on_commit` de falha, no padrão de
`rascunho.anexar_documento`. Nunca há sobrescrita.

**R-005 — Conferência.** Exige o predicado da FR-3595 e a chamada em aberto. Recusa:
- apresentação não vigente (`versao_superada`);
- "conforme" sem `CONSULTAR_DOCUMENTO_DA_CONVOCACAO` do próprio ator para aquela apresentação
  (`conforme_sem_abertura`), lido na trilha por `aggregate_id` e `actor_subject`;
- substituição sem motivo.

A trava também é na `Inscricao`, para serializar com a apresentação.

**R-006 — Guarda do desfecho.** Em `desfechar.py`, antes de qualquer gravação, se a espécie está em
`DESFECHOS_QUE_INCLUEM`: `convocacao.domain.documentos.pendencias_para_incluir(itens)` devolve os
itens obrigatórios sem conferência vigente *conforme* ou *não se aplica* sobre a apresentação vigente.
Se houver, a recusa é 409 `documentos_nao_conferidos`, com os nomes. O estado é lido sob a mesma trava
da `Inscricao`.

**R-007 — Predicado único.** `pode_conferir_documentos` devolve `Base`:
- `comissao:gerir`, `comissao:presidir` ou `comissao:conferir_documentos` (esta última é só o nome da
  base para a frase de recusa, e não capacidade do catálogo);
- `None` se o escopo é alheio, se não há base, ou se a alocação não cobre o Perfil.

Toda view da gestão desta feature chama só ele. A condução existente (`_edital_para_classificar`)
passa a aceitar, no GET, também o alocado, e a filtrar as linhas pelos Perfis da alocação.

**R-008 — Unidade de atuação.** A coluna `unidade_de_atuacao` (código da unidade, texto) vai na linha
de apresentação, conferência e alocação. Para o servidor, vem da unidade ativa da sessão
(`Actor.institution_scope`); para o candidato, do Edital. Nenhuma constraint a compara com o
`institution_scope` do Edital (§7 do complemento, item 4).

**R-009 — Trilha.** Operações novas:
- `CONVOCACAO_APRESENTAR` e `CONVOCACAO_CONFERIR`;
- `CONVOCACAO_ALOCAR_CONFERENCIA` e `CONVOCACAO_REVOGAR_ALOCACAO`;
- `CONSULTAR_DOCUMENTO_DA_CONVOCACAO`, `CONSULTAR_DOCUMENTOS_DA_CONVOCACAO` (a página) e
  `CONSULTAR_DOSSIE` (A-07).

Todas entram em `OPERACOES` (rótulos) e em `AGREGADOS`, e as de convocação em `_atos_da_conducao`.
`detalhe` não leva nome original nem motivo. A integridade reaproveita `INTEGRIDADE`.

**R-010 — Contrato de mutabilidade e forma publicada.** Dois pares `NAO_RETIFICAVEL` com razão escrita.
A fixture `rascunho_completo` (`tests/fixtures/snapshot.py`) ganha os dois campos com valor, senão o
guardião acusa natureza sem campo. `test_a_conta_fecha_com_a_matriz` continua em 84 retificáveis. O
degrau 18 da elevação lê forma publicada antiga como inscrição e sem aproveitamento.

**R-011 — PDF.** `_documentos_exigidos` filtra `moment == "AT_ENROLLMENT"`. `_documentos_na_convocacao`
usa o mesmo agrupamento e a mesma frase de documento, acrescida da frase do aproveitamento. A seção
só entra no catálogo quando houver item. Os PDFs dos cenários existentes são comparados byte a byte
com UUIDs normalizados (SC-1085).

**R-012 — Telas.** Nenhum painel novo:
- **portal**: um bloco na `convocacao.html`;
- **condução**: colunas e ordem na `convocacao.html` da gestão;
- **página filha**: `convocacao_documentos.html`, no padrão de `convocacao_historico.html`;
- **alocação**: seção na `alocacoes.html`, que já aloca à Etapa.

O formulário de desfecho:
- pré-redige o fundamento do indeferimento a partir das pendências (FR-3594);
- mostra a recusa do aceite antes do clique, como `recusa_certa` faz na `113`, sem deixar de recusar
  no command.

## Estratégia de testes

| Camada | O que prova | Onde |
|---|---|---|
| Unidade | estado derivado do item e da convocação, tabela inteira da FR-3590 e da FR-3591; filtro por momento; validação do aproveitamento; frases da FR-3612 | `tests/unit/convocacao/test_estado_documental.py`, `tests/unit/editais/test_momento_do_documento.py` |
| Contrato | natureza dos campos novos; forma publicada e elevação; seção do PDF | `tests/contract/test_mutabilidade.py` (inalterado, fixture estendida), `tests/unit/publicacoes/test_elevacao.py`, `tests/integration/publicacoes/test_secao_da_convocacao.py` |
| Integração (transacional) | lista gravada na raiz e herdada pela sucessora; aproveitamento sem cópia; apresentação com versões; duplicado e concorrência; conferência e recusas; guarda do aceite; nada automático no vencimento | `tests/integration/convocacao/test_documentos_da_convocacao.py`, `test_conferencia.py`, `test_guarda_do_aceite.py`, `test_concorrencia_da_apresentacao.py` |
| Banco | gatilhos append-only e de coerência; privilégio ausente (`como_producao`); contagem 49; `PROTECT` | `tests/integration/test_database_permissions.py` (parametrizado), `tests/seguranca/test_homologacao_preservada.py` (46 → 49) |
| Autorização | a matriz de permissões, linha a linha, contra as quatro rotas da gestão e as duas do portal; inventário de negativas da `033` | `tests/interface/test_permissoes_dos_documentos_da_convocacao.py`, `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` |
| Trilha | um registro por ato, com ator e unidade, sem nome nem motivo; A-07 | `tests/integration/auditoria/test_trilha_dos_documentos_da_convocacao.py`, `tests/interface/test_consulta_ao_dossie.py` |
| Interface | contagens e ordem; recusas visíveis; vocabulário proibido (varredura literal com os templates novos); CSP; classe com regra na folha; orçamento de consultas | `tests/interface/test_conducao_com_documentos.py`, `test_vocabulario_*` e `test_acessibilidade` existentes, com os templates novos na lista |
| Regressão | Editais sem documento da convocação inalterados; FR-402 (`test_convivencia_com_o_anexo.py`) inalterada; FR-084 (`test_situacoes_de_mensagem.py`) inalterada; dependência da convocação | suíte existente |
| Navegador | US1, US2 e US3, a 375 px e desktop, sem violação de CSP; a apresentação do PDF pelo `set_input_files` | `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` |

Os negativos do pedido têm caso próprio:
- acesso indevido: a matriz;
- prazo vencido: US4 e FR-3582;
- envio duplicado: FR-3581;
- arquivo inválido: FR-3582;
- documento pendente: FR-3592;
- convocação sem exigência documental: FR-3574.

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| A lista de convocação esquecida num caminho de convocação (lote, regularização) | convocado sem lista e aceite sem guarda | um teste por caminho que cria raiz: individual, lote de titulares, suplência, para regularizar |
| A guarda do aceite contornada pela sucessão de desfecho | aceite sem conferência | a guarda vale para todo desfecho que inclui, raiz ou sucessor |
| O filtro por momento esquecido num leitor da inscrição | inscrição bloqueada por documento da convocação | `da_inscricao()` é o único caminho, e um teste por leitor: envio, rascunho, lista, Mesa, portal, assistente |
| Contagem append-only, PDF ou forma publicada mudando testes antigos | suíte vermelha por contagem | contagens nomeadas nas tarefas; PDFs existentes comparados normalizados |
| Abrir PDF malicioso | estação do conferente comprometida | D-016; bloqueia produção, e não a implementação |
| Guardar para sempre | o GPS vira acervo por inércia | QI-4; bloqueia produção |
| Membro alocado vendo linha de outro Perfil na condução | vazamento de dado de convocado | filtro na consulta da condução, e não na tela; teste da matriz |
| Assimetria entre o Requerimento e o documento depois do vencimento | candidato confuso | frase da FR-3612; pendência da D-011 |

## Fases

1. **Fundação**: momento, aproveitamento, contrato, forma publicada, filtro da inscrição e PDF. É
   entregável sozinha: os Editais passam a pedir menos na inscrição.
2. **Lista e apresentação**: tabelas, gatilhos, gravação na raiz, portal.
3. **Conferência e desfecho**: predicado, alocação, conferência, guarda, condução e página filha.
4. **Trilha e A-07**.
5. **Navegador, rastreabilidade e verificação completa** (`make lint check test-pg`).

## Complexity Tracking

Nenhuma violação a justificar.
