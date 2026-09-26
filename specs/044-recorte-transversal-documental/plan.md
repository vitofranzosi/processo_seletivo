# Implementation Plan: Recorte transversal do documento exigido

**Branch**: `claude/044-recorte-transversal-documental` | **Date**: 2026-09-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/044-recorte-transversal-documental/spec.md`

## Summary

O Documento Exigido ganha `modalityCode`, que recorta pela Modalidade de um código **em todos os
Perfis que a têm**. Esse recorte é lido pela mesma função que decide o que o portal pede. Essa
função passa a devolver, para cada documento, o **veredito** (obrigatório, facultativo, não se
aplica) com o recorte que o produziu.

No envio, a inscrição grava esses vereditos numa tabela append-only nova, protegida por privilégio e
por gatilho. A Mesa, a consulta administrativa e a inscrição enviada no portal passam a ler a lista
gravada. As inscrições anteriores à feature têm a lista reconstruída sobre a versão que aceitaram, e
a tela diz que é reconstruída.

A publicação ganha quatro recusas (exclusividade, código inexistente, ampla, coerência de
denominação), e a da #161 ganha a terceira saída. O documento publicado agrupa por código. A versão
canônica sobe para 17, com o degrau que lê o conteúdo antigo como "não recorta por código".

**O planejamento e a análise corrigiram a spec**, sempre por escrito nela:
- o resumo público nomeia o campo e não o valor, como já faz com todos (`D-008`);
- a Retificação não junta linhas, porque não remove documento (`D-009`);
- a divergência da #161 também se registra na lista **gravada**, e só para quem concorre na
  modalidade de mesma denominação (`FR-727`);
- a tela do portal que a lista alimenta é a da inscrição enviada, e não o "acompanhamento", que não
  lista documentos. E ela não anuncia a reconstrução, porque mostra só o que foi enviado (`FR-720`,
  `FR-726`);
- a gravação do rascunho recusa o código inalcançável e o da ampla, no precedente do `modalityId`
  (`D-010`, `FR-724`).

## Technical Context

**Language/Version**: Python 3.13 · Django 5.2. Nenhuma dependência nova.

**Primary Dependencies**: as do projeto: Django, DRF, o gerador de PDF próprio
(`publicacoes/infrastructure/pdf.py`), HTMX nas telas de composição.

**Storage**: PostgreSQL. **Duas migrations**:
- `editais.0022`: uma coluna e uma restrição;
- `inscricoes.0005`: uma tabela, as restrições e dois gatilhos.

Tabelas append-only: **33 → 34**.

**Testing**: pytest + pytest-django contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio). As
garantias da lista moram no banco, e por isso os testes de imutabilidade são `transaction=True`.

**Target Platform**: a gestão (`/gestao/`: composição, Retificação, Revisão, Mesa, consulta), o
portal do candidato e o documento publicado.

**Project Type**: monólito Django, projeto único.

**Performance Goals**: a lista "Inscrições recebidas" continua com o **mesmo** número de consultas
para 5 e para 300 inscrições, com uma consulta a mais por página, e não por linha (`R-006`). A Mesa
lê a lista de uma inscrição numa consulta.

**Constraints**:
- nenhum documento publicado regenerado (`FR-725`);
- nenhuma lista escrita para inscrição antiga (`D-004`). Isso é garantido pela **aplicação**, e não
  pelo banco: só o ato de envio grava, nenhuma migration preenche, e um teste prende as duas coisas
  (`R-005` explica por que o gatilho não alcança);
- nenhuma permissão nova (`FR-728`);
- nenhum dado pessoal novo;
- conflito previsto com o PR #167 em `mesa.py` e `mesa_inscricao.html`, resolvido preservando a
  instrução.

**Scale/Scope**: 30 requisitos funcionais, 4 de interface, 9 critérios de sucesso, 10 decisões. Cerca
de 20 módulos tocados, a maior parte com mudança pequena. O centro de gravidade são três arquivos:
`editais/domain/documentos.py`, `inscricoes/application/lista_exigida.py` (novo) e a migration da
tabela.

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado após a Fase 1. Nenhuma violação.*

| Princípio | Como esta feature o atende | Verificado por |
|---|---|---|
| **I — Linguagem ubíqua** | *Modalidade*, *Perfil*, *Documento Exigido* e *código* são os do domínio. O termo novo, **lista exigida**, nomeia uma coisa nova: o que foi pedido a uma inscrição, que não é o Documento Exigido do Edital. "Não se aplica" é estado com nome, e não ausência de linha | revisão de texto; `UX-081` |
| **II — Integridade normativa** | O recorte tem **uma** regra de aplicabilidade para o cartão, o rascunho, o envio, a lista e a reconstrução (`FR-705`, `R-003`). O PDF agrupa pelo mesmo campo (`R-008`). A Constituição pede *"reproduzir os documentos exigidos para cada Inscrição"*, e é o que a lista gravada faz. Publicação imutável: nada regenerado, degrau de elevação só no fluxo de Retificação (`R-002`) | `test_elevacao_degrau_17`; testes de lista depois de Retificação (`SC-264`) |
| **III — Segurança e dados pessoais** | Nenhuma permissão nova. A lista é lida por quem já lê os documentos da inscrição. Nenhum dado pessoal novo: a razão é recorte do **Edital**. A auditoria não repete a lista (`FR-728`, `FR-729`, §LGPD da spec) | testes de autorização existentes da Mesa e da consulta |
| **IV — Regras explícitas** | As recusas moram no domínio e na publicação (`R-007`), com a restrição de banco como segunda barreira (`ck_documento_recorte_exclusivo`). Concorrência: a lista é gravada na transação do ato, sob o `FOR SHARE` do Edital que já conflita com a publicação da Retificação. O `BEFORE INSERT` prende a versão da lista à versão aceita | testes de publicação; teste do gatilho de coerência |
| **V — Qualidade e simplicidade** | Um campo, uma tabela, um degrau, sem entidade nova no conteúdo. Descartada a categoria declarada no Edital (D1 da decisão). A tabela nova se justifica pela Constituição, e não por conveniência | `research.md` |
| **VI — Jornada e valor** | Quem compõe declara "todo candidato PcD" numa linha. O candidato PcD de qualquer Perfil recebe o pedido. Quem analisa vê o que foi pedido e o que não se aplicava. Três atores, três canais, sem shell | `quickstart.md`, cenários A a D; `SC-268` |

**Dois pontos que o gate exige registrar.**

1. **A tabela append-only nova tem duas camadas, e o precedente mais próximo tem uma.**
   `ValorDeFato`, gravado no mesmo ato, é protegido só por privilégio. A lista segue as duas camadas que
   o CLAUDE.md descreve (`R-005`). A falta do gatilho em `ValorDeFato` vai para
   registro, e não para esta feature.
2. **A spec mudou durante o plano.** As correções acima estão escritas na spec, com decisão
   numerada, e não só aqui. É o que o Princípio V pede: divergência resolvida explicitamente.

## Project Structure

### Documentation (this feature)

```text
specs/044-recorte-transversal-documental/
├── spec.md              # 30 FRs, 4 UXs, 9 SCs, D-001 a D-010
├── plan.md              # este arquivo
├── research.md          # Fase 0: R-001 a R-014
├── data-model.md        # Fase 1: o campo, a tabela, o degrau
├── contracts/
│   ├── recorte-transversal.md   # o campo, a aplicabilidade, os achados, as grafias
│   └── lista-exigida.md         # a gravação, a leitura, os três estados
├── quickstart.md        # Fase 1: cenários A a D e a suíte
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2: NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── domain/documentos.py          # + aplicabilidade, Veredito, Recorte, predicado da #161,
│   │                                 #   razão legível; aplicaveis passa a receber o conteúdo;
│   │                                 #   recusas de modalityCode na gravação
│   ├── domain/validation.py          # + campo publicado; 4 achados; mensagem da #161
│   ├── domain/mutabilidade.py        # + ("documentRequirements", "modalityCode"): retificável
│   ├── models/documentos.py          # + modalidade_codigo, ck_documento_recorte_exclusivo
│   ├── migrations/0022_documento_modalidade_codigo.py
│   ├── application/draft.py          # persistir e reler o campo
│   └── api/serializers.py            # + modalityCode
├── publicacoes/
│   ├── application/publish_edital.py # escrever modalityCode no snapshot
│   ├── domain/elevacao.py            # degrau 17
│   ├── domain/alteracoes.py          # rótulo "Modalidade em todos os Perfis"
│   └── infrastructure/pdf.py         # grupo por código
├── shared/canonical.py               # SCHEMA_VERSION = 17
├── inscricoes/
│   ├── models.py                     # + ItemDaListaExigida
│   ├── migrations/0005_item_da_lista_exigida.py
│   ├── application/lista_exigida.py  # novo: gravar, ler, reconstruir
│   ├── application/submissao.py      # gravar no ato
│   ├── application/rascunho.py       # aplicaveis(conteudo, …)
│   └── application/consulta.py       # ler a lista (recebidas e detalhe)
├── avaliacoes/application/mesa.py    # ler a lista
├── seguranca/papeis.py               # + tabela em TABELAS_APPEND_ONLY
├── interface/
│   ├── forms.py                      # alcance com códigos; ler e reenviar modalityCode
│   ├── retificacao.py                # campo e opções de modalityCode
│   ├── revisao.py                    # _alcance por código
│   ├── views.py                      # destino do achado de denominação
│   └── templates/interface/
│       ├── _documento.html           # optgroups
│       ├── mesa_inscricao.html       # três estados, razão, avisos
│       └── inscricao_detalhe.html    # idem
├── portal/views.py                   # _documentos da enviada lê a lista
└── processos/management/commands/seed_demo.py   # gravar a lista das inscrições semeadas

backend/tests/                         # famílias em quickstart.md
AGENTS.md                              # 33 → 34 tabelas append-only
specs/001-processo-seletivo-editais/contracts/openapi.yaml   # + modalityCode
```

**Structure Decision**: monólito existente. Nenhum app novo. A lista mora em `inscricoes` porque é
da inscrição, e a regra em `editais/domain` porque é do Edital, onde a aplicabilidade já mora.

## Ordem de construção

As histórias da spec têm dependência real, e a ordem a respeita:

1. **O domínio primeiro:** `aplicabilidade`, o veredito, o predicado da #161, as recusas. Tudo puro,
   testável sem banco. Nenhum comportamento muda ainda, porque nenhum conteúdo tem `modalityCode`.
2. **O campo, de ponta a ponta na autoria** (US1): migration de `editais`, rascunho, API, snapshot,
   degrau 17, validação de publicação, PDF, Revisão, composição.
3. **A lista** (US2): migration de `inscricoes`, gravação no envio, leitura na Mesa, na consulta e no
   portal. A reconstrução entra aqui, porque sem ela as inscrições existentes quebrariam a Mesa no
   primeiro deploy. Por isso o fallback da US4 não é opcional nesta fase.
4. **A Retificação** (US3): o campo na tela, a mutabilidade, o rótulo do resumo.
5. **Semente, contagens, documentação:** `seed_demo`, `AGENTS.md`, `openapi.yaml`.

A US4 não tem fase própria: ela é a reconstrução (fase 3) mais o predicado (fase 1).

## Riscos

| Risco | Mitigação |
|---|---|
| O merge com o PR #167 conflita em `mesa.py` e `mesa_inscricao.html` | quem for mergeado depois preserva a instrução; a `044` não a remove |
| Os seis chamadores diretos de `aplicaveis` mudam de assinatura | a troca é mecânica e acontece de uma vez; o tipo do primeiro argumento muda de lista para dicionário, e um chamador esquecido falha no primeiro teste que o exercita |
| Suíte longa com migration nova | conferir `migrate --check` antes de investigar falha estranha; banco de teste por worktree |
| Guardiões de contagem de migration | `R-013` lista cada um, com o número novo e a justificativa |

## Complexity Tracking

Nenhuma violação a justificar. A tabela nova e o gatilho de coerência são complexidade que o
projeto **pede**: *"reproduzir os documentos exigidos"*, pela Constituição, e as duas camadas
independentes das tabelas append-only, pelo CLAUDE.md. Não é complexidade opcional.
