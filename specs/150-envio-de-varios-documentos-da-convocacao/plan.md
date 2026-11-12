# Implementation Plan: O envio de vários documentos da convocação, sem perder escolha

**Branch**: `claude/unruffled-lamport-1394f8` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: a spec da `150`, mergeada no #471 só com a spec (FR-5600 a FR-5614, SC-1800 a SC-1805,
UX-500 a UX-503, D-001 a D-005). Neste PR a spec é revista para incluir o achado 11 do estudo da
jornada final — o mesmo arquivo em dois documentos —, com a User Story 5, FR-5615 a FR-5619, UX-504,
SC-1806, SC-1807, D-006 e três perguntas ao usuário, todas com resposta adotada por padrão.

## Summary

Hoje cada cartão da convocação é um formulário que envia só o seu arquivo e recarrega a página; as
escolhas dos outros cartões somem em silêncio. O plano conserta isso **no navegador**, sem regra de
domínio nova, com quatro mudanças:

1. **Um script novo, `portal/static/portal/varios.js`**, que conta os cartões com arquivo escolhido,
   reescreve o rótulo do botão ("Enviar os N documentos escolhidos"), oferece "Remover a escolha" e,
   no `submit` de qualquer cartão com N ≥ 2, envia os N arquivos **um por requisição**, em sequência,
   pelo mesmo endereço do envio individual (D-002, R-001).
2. **A view do envio responde ao lote em JSON.** Com o cabeçalho `X-Envio-De-Varios: k/n`, a
   `apresentar_documento_da_convocacao` devolve o resultado daquele documento em JSON, em vez do
   redirecionamento, e acumula na sessão o recebido e o recusado. O comando `apresentar` da `115`
   não muda (R-002, R-003).
3. **A volta do lote é a volta de hoje, com listas.** Terminado o lote, o script navega para
   `#confirmacao` (algum recebido) ou para o cartão do primeiro recusado (nenhum recebido). A
   confirmação da `121` passa a aceitar vários envios — "Recebemos 3 de 4 documentos" — e a recusa,
   uma por cartão (R-004).
4. **O arquivo repetido (achado 11).** Cada cartão com apresentação vigente traz o resumo SHA-256
   dela num atributo `data-`; ao escolher um arquivo, o script calcula o resumo no navegador
   (`crypto.subtle`) e compara com os escolhidos e com os vigentes dos outros cartões. Coincidindo,
   o cartão avisa; o envio continua possível (D-006, R-005, R-006).

Sem script, nada muda no envio; a tela ganha uma frase em `<noscript>` (FR-5612, R-007).

**Nenhuma rota, tabela, migration, papel, estado, comando ou frase de recusa nova.** As tabelas
append-only continuam **58**.

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório); JavaScript ES5 sem módulo, como
os scripts do portal
**Primary Dependencies**: as do projeto; nenhuma nova. `crypto.subtle` e `fetch` do navegador
**Storage**: PostgreSQL, sem migration. A sessão do Django guarda o lote em curso (R-003)
**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio); `node --test` em
`tests/javascript/varios.test.js`, com o shim de `dom.js`; jornada no navegador com o grupo
`navegador`, em `tests/navegador/test_jornada_dos_documentos_da_convocacao.py`
**Target Platform**: portal do candidato a 375 px, com e sem script; contexto seguro (HTTPS em
produção, `localhost` em desenvolvimento) para o `crypto.subtle`
**Project Type**: monólito web
**Performance Goals**: a tela da convocação com a **mesma** contagem de consultas de hoje, com 1 e
com 6 itens — o resumo vigente já vem no *prefetch* das apresentações (R-005). Um envio do lote custa
o mesmo que o envio individual. O resumo de um PDF de 10 MiB no navegador, abaixo de um segundo num
celular médio
**Constraints**:
- **CSP** `script-src 'self'`, `style-src 'self'`: nada embutido; estilo novo em
  `portal/static/portal/portal.css`; `<noscript>` não é script e passa.
- **Proxy**: `/selecoes/` limita o corpo a 12 MB, um arquivo por requisição (D-002). O lote não muda
  isso.
- **Nada no navegador** (FR-5611, FR-042): o guardião `tests/test_armazenamento_no_navegador.py` lê
  todo `.js` do portal e alcança o script novo sem mudança.
- **Sem script, o envio de hoje**: os formulários mantêm `action` e `method`; o script só intercepta.
**Scale/Scope**: uma convocação pede da ordem de uma dezena de documentos; dois módulos
Python (`views.py`, `obrigacoes.py`), dois templates, um script novo e a folha do portal

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Situação |
|---|---|---|
| I. Linguagem ubíqua | "documento", "convocação", "enviar", "recebido", "conferência" — o vocabulário da `115`/`121`; nenhuma palavra que prometa juízo ("aceito", "aprovado") | ✅ |
| II. Imutabilidade | Cada documento do lote é uma `ApresentacaoDeDocumento` própria, append-only, pelo comando de hoje; nada se exclui nem se reescreve | ✅ |
| III. Segurança e dados | Mesma titularidade (`_inscricao_do_titular`) e CSRF por requisição; nada guardado no navegador; o resumo exposto no HTML é do arquivo da própria pessoa, numa página só do titular (R-006) | ✅ |
| IV. Regras explícitas | Prazo, validação e estado continuam no comando; o script não decide aceitação. O aviso do achado 11 é informação, não regra (D-006) | ✅ |
| V. Rastreabilidade e simplicidade | Um script, um cabeçalho, nenhuma rota; teste por FR e SC; a trilha de cada envio é a de hoje | ✅ |
| VI. Completude de jornada | Lote, recusa parcial, queda de conexão, acesso expirado, sem script e o arquivo repetido têm cenário de aceitação e teste | ✅ |

Nenhuma violação; a seção *Complexity Tracking* fica vazia.

**Re-check depois da Fase 1**: o contrato ([contracts/envio-de-varios.md](contracts/envio-de-varios.md))
não cria rota nem muda o comando; a resposta JSON é só um outro corpo da mesma rota, sob o mesmo
`require_POST`, titularidade e CSRF. Continua ✅.

## Os cruzamentos com outras features em curso

Em 11/11/2026, três sessões mexem na convocação e no portal. Nenhuma sobrepõe este escopo, mas os
arquivos se cruzam. **Quem implementar a 150 confere, antes, o que delas já está na `main`.**

| Feature | Onde se cruza | O que a 150 muda ali | O que a outra muda ali | Como conviver |
|---|---|---|---|---|
| **154** — a convocação depois do envio, e o nome do reenviado (PR #479, só spec) | `portal/obrigacoes.py`: `ConfirmacaoDoEnvio`, `confirmacao_do_envio`, `RECEBEMOS`, `FRASE_DE_CONCLUSAO`; o texto do cartão (`item.texto`, selos) | A confirmação recebe **vários** envios: a frase "Recebemos N de M documentos" e a lista; a próxima tarefa e a conclusão continuam calculadas uma vez, do estado depois do último envio | O título e a conclusão depois do último envio (*"Acompanhe sua convocação"*); o texto do cartão do reenviado | A 150 **não** reescreve `proxima`, `conclusao` nem `rotulo`: só acrescenta a lista. Se a 154 entrar antes, a 150 rebaseia sobre a conclusão dela; se depois, a 154 não precisa saber do lote. Implementar a 150 **depois** do merge da 154 evita o conflito em `confirmacao_do_envio`. |
| **154** | `portal/templates/portal/_cartao_do_documento_da_convocacao.html` | Só o bloco `.envio` (formulário, "Remover a escolha", aviso do arquivo repetido) e o `data-resumo-recebido` no `<li>`; a recusa passa a vir do item (R-004) | O topo do cartão: selos e frase de estado do reenviado | Blocos diferentes do mesmo arquivo: conflito textual possível, semântico não. |
| **154** | `portal/templates/portal/convocacao.html` | A `<noscript>` antes do primeiro cartão com envio; o quarto `<script>` | O título, a frase de conclusão, o resumo | Idem. |
| **156** — comunicação do desfecho e textos do portal | `portal/obrigacoes.py` (frases do desfecho) e `convocacao.html` (bloco do desfecho) | Nada nas frases do desfecho | As frases do desfecho e da comunicação | Sem sobreposição funcional; possível conflito textual em `obrigacoes.py`. |
| **157** — visualizador na conferência, do lado da gestão | Nenhum arquivo do portal | — | A tela de conferência da gestão | A Pergunta 2 da spec (mostrar à comissão a coincidência de arquivo) cairia na tela da 157; fica fora desta spec. |

Os guardiões que a 150 aciona e que as outras também podem acionar: o de scripts da convocação
(`test_a_convocacao_carrega_os_tres_scripts_e_nenhum_outro`, que passa a quatro), o de vocabulário
(`tests/test_vocabulario_dos_documentos_da_convocacao.py`) e o de classe sem regra na folha.

## Project Structure

### Documentation (this feature)

```text
specs/150-envio-de-varios-documentos-da-convocacao/
├── spec.md              # revista neste PR (achado 11)
├── research.md          # D-001 a D-006 (spec) e R-001 a R-008 (plano)
├── plan.md              # este arquivo
├── data-model.md        # nenhuma entidade; o estado do lote na sessão e no DOM
├── quickstart.md        # roteiro de verificação
├── contracts/
│   └── envio-de-varios.md   # cabeçalho, JSON, sessão e marcação do cartão
├── checklists/requirements.md
└── tasks.md             # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/portal/
├── views.py                          # apresentar_documento_da_convocacao: ramo do lote (JSON + sessão);
│                                     # _volta_do_envio: listas de recebidos e recusas
├── obrigacoes.py                     # confirmacao_do_envio aceita vários; recusa por âncora;
│                                     # resumo vigente por item (sem consulta nova)
├── templates/portal/
│   ├── convocacao.html               # <noscript> (FR-5612); quarto script
│   └── _cartao_do_documento_da_convocacao.html
│                                     # data-resumo-recebido; "Remover a escolha" (hidden);
│                                     # região do aviso; recusa da lista
└── static/portal/
    ├── varios.js                     # NOVO: contagem, rótulo, remover, lote, resumo e aviso
    ├── arquivo.js                    # sem mudança: continua o da inscrição (R-001)
    └── portal.css                    # regras das classes novas

backend/tests/
├── javascript/varios.test.js         # NOVO: node --test, com dom.js
├── interface/test_portal_documentos_da_convocacao.py   # ramo JSON, sessão, confirmação de vários, <noscript>, 4 scripts
├── integration/portal/test_envio_de_varios.py           # NOVO: lote ponta a ponta pelo cliente de teste
├── interface/test_portal_jornada_consolidada.py        # contagem de consultas da convocação com o resumo
└── navegador/test_jornada_dos_documentos_da_convocacao.py   # jornada do lote e do arquivo repetido
```

**Structure Decision**: monólito; tudo no app `portal`. O app `convocacao` não muda: o comando
`apresentar` já faz tudo o que um documento do lote precisa.

## Fases

- **Fase 0** — [research.md](research.md), seção *Fase 0 do plano*: R-001 a R-008.
- **Fase 1** — [data-model.md](data-model.md), [contracts/envio-de-varios.md](contracts/envio-de-varios.md),
  [quickstart.md](quickstart.md).
- **Fase 2** — [tasks.md](tasks.md), pelo `$speckit-tasks`.

## Complexity Tracking

Nenhuma violação a justificar.
