# Implementation Plan: Trilha da unidade

**Branch**: `claude/108-trilha-da-unidade`, sobre a `main` em `ca1e53ed` | **Date**: 2026-10-30 |
**Spec**: [spec.md](spec.md)

**Input**: a spec, com D-001 a D-009 no [research.md](research.md). **Aprovação**: o pedido de
30/10/2026 autoriza especificar e implementar até o PR, sem merge; as três pendências de governança
ficam com a saída que não concede nada.

## Summary

Uma página de leitura e um seletor. O seletor `trilha_da_unidade` lê a trilha do escopo do ator,
restrita aos cinco assuntos administrativos, mais as concessões de vínculo da unidade gravadas no
escopo institucional (D-002, D-007). A view confere `auditoria:consultar` na unidade ativa (D-001,
D-003), monta as linhas a partir do próprio registro e enriquece avisos e interrupções com uma
consulta por tipo (D-005, D-006). A barra ganha o item no grupo da unidade (D-008). O guia de
implantação passa a apontar a página.

**Nada se grava.** Nenhuma migration, nenhuma tabela, nenhum evento novo: o `M` do
`provisionar_papeis` continua **46**.

**Onde está o risco**: no escopo. A única leitura fora do escopo do ator é a condição de `D-002`, e
ela tem teste próprio de vazamento com duas unidades.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django. Nenhuma dependência nova.

**Storage**: PostgreSQL; leitura de `auditoria_registroauditoria`, de `avisos_aviso` e de
`avisos_interrupcaodoaviso`. A condição sobre `detalhe` usa a busca por chave do `JSONField`.

**Testing**: pytest contra PostgreSQL. Casos em `tests/interface/test_trilha_da_unidade.py`
(acesso, escopo, assuntos, linhas, paginação, consultas, dado pessoal); o item da barra entra pelo
teste existente de `test_shell_da_gestao.py`, que deriva os destinos de `SECOES`.

**Target Platform**: `GET /gestao/trilha-da-unidade`, com `?assunto=` e `?cursor=`.

**Performance Goals**: número de consultas constante por página (`FR-3168`, `SC-1023`).

**Constraints**: CSP sem `unsafe-inline` — estilo em `interface/telas/`, nenhum script; toda classe
nova com regra na folha. Seletor de demonstração com os oito papéis.

**Scale/Scope**: dezenas a poucos milhares de eventos administrativos por unidade por ano.

## Constitution Check

| Princípio | Como se cumpre |
|---|---|
| III — Negar por padrão e escopo | a permissão é conferida no servidor; a unidade vem do ator, e nunca do pedido (`FR-3154`); a exceção de escopo de `D-002` está num lugar só, com teste de vazamento |
| III — Proteção de dados | nenhum dado de candidato; nem assunto nem corpo de aviso ou de modelo; o nome da pessoa pela tradução da `107` (`FR-3164`) |
| III — Auditoria | a trilha só é lida; nada se reescreve nem se acrescenta (`FR-3169`) |
| II — Nada se exclui; imutabilidade | nenhuma migration; nenhuma escrita em tabela append-only |
| V — Rastreabilidade e simplicidade | um seletor e uma view, sobre o `consultar` que já existe; sem subsistema paralelo de log (a decisão dezoito da `011`) |
| VI — Jornada demonstrável | o Auditor do seletor abre a página no banco de demonstração; roteiro no [quickstart](quickstart.md) |
| Governança do usuário | P1, P2 e P3 ficam perguntas, com a saída que não concede nada |

Sem violação. Nada a justificar em complexidade.

## Project Structure

### Documentation (this feature)

```text
specs/108-trilha-da-unidade/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/trilha-da-unidade.md
├── checklists/requirements.md
├── tasks.md
└── verificacao.md        # escrito na implementação
```

### Source Code

```text
backend/processo_seletivo/
├── auditoria/selectors.py                     # trilha_da_unidade; paginação comum
├── interface/
│   ├── trilha_da_unidade.py                   # a view e a montagem das linhas
│   ├── urls.py                                # a rota
│   ├── navegacao.py                           # o item da barra
│   ├── templates/interface/base.html          # o ícone do item
│   ├── templates/interface/trilha_da_unidade.html
│   └── static/interface/telas/trilha_da_unidade.css
backend/tests/
├── interface/test_trilha_da_unidade.py
├── interface/test_shell_da_gestao.py          # o teste do ícone passa a identificar o Auditor
└── test_gramatica_das_portas.py               # MODULOS_DE_VIEW
doc/implantacao-em-producao-ubuntu.md          # §20.3
```

**Structure Decision**: o monólito Django existente; a view em módulo próprio, como as telas
desde a `099` (D-008).

## Fases

1. **Seletor** (D-002, D-007): `trilha_da_unidade` e a paginação comum; testes de escopo e de
   assunto sobre o seletor.
2. **View e template** (D-001, D-005, D-006, D-009): a página, as linhas, o filtro, a paginação;
   testes de acesso, conteúdo, dado pessoal e consultas.
3. **Barra** (D-008): o item, o ícone e o guardião de módulos.
4. **Documentação**: o guia de implantação, o quickstart e a verificação.
