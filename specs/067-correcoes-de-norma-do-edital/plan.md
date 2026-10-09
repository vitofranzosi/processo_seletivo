# Implementation Plan: Correções de norma do Edital em PDF — recurso com objeto, sorteio sem conta e Perfil sem vaga imediata

**Branch**: `claude/067-correcoes-de-norma-do-edital` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/067-correcoes-de-norma-do-edital/spec.md`

## Summary

Três correções do documento oficial, cada uma com o lado da validação e da tela que a sustenta:

- **ED-02.** A frase de recurso do marco passa a nomear o resultado pelo nome do marco entre aspas
  (`D-001`), na mesma função que o documento, a prévia, o consolidado e a Revisão já leem (`D-005`);
  e uma conferência nova emite **um aviso** com os prazos dos marcos e os Eventos de recurso do
  Cronograma, lado a lado, sempre que algum marco publicar regra de recurso (`D-002`, `D-006`).
- **ED-03.** Sob marco que **declara** ordem por sorteio (`D-004`), a validação deixa de exigir
  arredondamento, o documento e a Revisão deixam de imprimir arredondamento e empate no corte, a tela
  deixa de mostrar e de gravar arredondamento (`D-008`), e a emissão recusa o marco por sorteio antes
  de calcular, para que o caso novo não vire erro interno (`D-009`).
- **ED-12.** Perfil sem vaga imediata (`D-007`) não imprime quadro nem reversão, e a contagem de
  tabelas da `065` segue a mesma regra; a Revisão diz que a reversão declarada não sai (`D-003`).

Nada de modelo, migration, campo ou esquema. Documento já publicado não muda (`FR-1325`); a fixture de
contrato continua byte a byte (`D-010`).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: nenhuma nova.

**Storage**: nenhuma mudança — nenhum modelo, campo, migration ou versão de esquema (`FR-1327`).

**Testing**: pytest contra PostgreSQL (`make test-pg` com `DB_NAME` próprio); unidade do compositor e
da validação; interface (Revisão, tela do marco, Retificação); integração (submissão, publicação,
Retificação, emissão); o guardião de bytes e de texto dos cenários da auditoria; a fixture de
contrato inalterada.

**Target Platform**: o monólito Django; a interface administrativa (`/gestao/`).

**Project Type**: aplicação web (monólito).

**Performance Goals**: nenhuma consulta nova na Revisão, na submissão e na publicação — a conferência
é função do snapshot (`D-006`). A emissão ganha a leitura da versão vigente antes do cálculo
(`D-009`), num comando que já a lê.

**Constraints**: o documento só muda nos três casos pretendidos (`SC-502`, `SC-505`); nenhuma regra
de direito sobre texto livre (`D-002`); marco sem forma declarada sai como sempre (`D-004`).

**Scale/Scope**: o maior Edital medido — o cenário B — tem 18 Perfis, 18 Eventos e 4 Eventos de
recurso.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "resultado", "marco", "prazo", "Evento", "vaga imediata", com o sentido de hoje; o aviso não usa código interno (`UX-190`) | ✅ |
| II. Integridade normativa, imutabilidade | documento publicado não muda (`FR-1325`); o consolidado de Retificação é documento novo (`FR-1326`, como o `FR-1196`); cada frase tem uma fonte só (`D-005`, `D-007`); a regra inerte sai do conteúdo em vez de ser escondida (`D-008`) | ✅ |
| III. Segurança e auditoria | nenhuma permissão nova; as conferências rodam nos atos que já exigem permissão | ✅ |
| IV. Regras explícitas | a dispensa e o aviso moram no domínio e rodam nas mesmas portas; o aviso é aviso, classificado como tal (`D-002`); o que o documento deixa de imprimir é dito na Revisão antes do ato (`UX-192`) | ✅ |
| V. Qualidade, rastreabilidade, simplicidade | dois predicados de domínio, uma conferência, nenhuma dependência; a diferença de texto dos cenários fica na suíte (`D-010`); casos-limite com teste na matriz | ✅ |
| VI. Jornada demonstrável | os cenários A e B pelo fluxo real, antes e depois, com páginas renderizadas ([quickstart.md](quickstart.md)) | ✅ |

**Re-check depois do desenho (Fase 1):** sem violação. A importação adiada do compositor pela
validação (`D-006`) repete a da `065` e tem a mesma justificativa: a grafia do prazo e do instante é
uma só.

## Project Structure

### Documentation (this feature)

```text
specs/067-correcoes-de-norma-do-edital/
├── spec.md
├── plan.md
├── research.md            # D-004 a D-011
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── frase-de-recurso.md
│   ├── aviso-de-conferencia-de-recurso.md
│   └── documento-sob-sorteio-e-sem-vaga.md
├── checklists/requirements.md
├── demonstracao/          # PDFs e páginas de A e B depois da feature (T-final)
├── rastreabilidade.md     # na implementação
├── verificacao.md         # na implementação
└── tasks.md               # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── marcos.py                     # declara_sorteio (D-004)
│   ├── quadro.py                     # sem_vaga_imediata (D-007)
│   └── validation.py                 # dispensa do arredondamento; _conferencia_do_recurso (D-006)
├── publicacoes/infrastructure/
│   └── pdf.py                        # _janela_recursal, prazo_do_recurso; _marcos; quadro e reversão; tabelas_do_documento
├── classificacao/application/
│   └── emissao.py                    # recusa do sorteio antes do cálculo (D-009)
└── interface/
    ├── revisao.py                    # arredondamento e empate pela forma declarada; nota da reversão
    ├── forms.py                      # rounding {} sob sorteio (D-008)
    ├── retificacao.py                # dica do vazio do arredondamento
    └── templates/interface/_marco.html, _como_preencher_o_marco.html

backend/tests/
├── unit/publicacoes/test_frase_de_recurso.py                # NOVO — FR-1300 a FR-1304
├── unit/publicacoes/test_documento_sob_sorteio.py            # NOVO — FR-1313, FR-1314
├── unit/publicacoes/test_perfil_sem_vaga_imediata.py         # NOVO — FR-1320 a FR-1323, tabelas
├── unit/editais/test_conferencia_do_recurso.py               # NOVO — FR-1305 a FR-1310
├── unit/editais/test_arredondamento_sob_sorteio.py           # NOVO — FR-1311, FR-1312
├── interface/test_correcoes_de_norma_na_revisao.py           # NOVO — Revisão, tela do marco, Retificação, UX
├── integration/publicacoes/test_correcoes_de_norma_na_publicacao.py  # NOVO — atos, acervo, Retificação
├── integration/classificacao/test_emissao_de_marco_por_sorteio.py    # NOVO ou acréscimo — FR-1318
├── unit/publicacoes/test_itens_do_documento.py               # bytes contra demonstracao/ + diferença de texto (D-010)
└── contract/ (fixture de bytes)                              # inalterada — SC-505
```

**Structure Decision**: monólito existente; dois predicados de domínio, uma conferência, mudanças
localizadas no compositor, na Revisão e na tela do marco. Nenhum app, modelo, rota ou migration.

## Fases de implementação (para o `$speckit-tasks`)

1. **Ponto de partida** — medir a suíte das áreas tocadas e gravar os textos dos PDFs da auditoria
   para a comparação.
2. **Predicados** (`declara_sorteio`, `sem_vaga_imediata`) — independentes.
3. **US1 — frase de recurso** no compositor; os testes antigos que prendem a frase sem objeto mudam
   de propósito (`test_pdf.py`).
4. **US3 — sorteio**: validação, compositor, Revisão, tela, Retificação, emissão.
5. **US4 — Perfil sem vaga imediata**: compositor, contagem de tabelas, Revisão.
6. **US2 — aviso de conferência**: validação, destino na interface, Retificação.
7. **US5 e bytes**: integração do acervo e da Retificação; os PDFs esperados em `demonstracao/`; o
   guardião de bytes e o de diferença de texto; a fixture de contrato inalterada.
8. **Cenários A e B pelo fluxo real**, antes e depois, em bancos novos; páginas por CoreGraphics;
   diff de texto; `rastreabilidade.md`, `verificacao.md`; `make lint check test-pg`.

## Riscos

| Risco | Mitigação |
|---|---|
| A contagem de tabelas da `065` diverge do documento | um predicado só (`D-007`); o guardião que compõe de verdade |
| Mudança acidental do documento fora dos três casos | fixture de contrato inalterada (`SC-505`); diferença de texto dos cenários presa por teste (`D-010`) |
| Marco do acervo sem forma declarada muda de saída | regra pela forma declarada (`D-004`); teste do marco sem forma |
| Arredondamento opcional abre erro interno na emissão | recusa antes do cálculo (`D-009`) e teste com Etapas enumeradas |
| Voltar de sorteio para pontuação deixa os campos em branco | valores ocultos com o padrão (`D-008`) e teste do cartão recomposto |
| Aviso de recurso some na confirmação da Retificação | código que não coincide com impeditivo (`D-006`) e teste da confirmação |
| Testes antigos que prendem a frase e o quadro zerado | atualizados na tarefa que muda o comportamento, com a razão no commit |
| Suítes paralelas disputam o banco de teste | `DB_NAME` próprio da worktree |

## Complexity Tracking

Sem violações a justificar.
