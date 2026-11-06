# Implementation Plan: Os textos que o operador do sorteio lê

**Branch**: `claude/elegant-bohr-422170` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

Três correções de texto, sem tabela, migration, rota, permissão ou comportamento novo. A observação
da Caixa passa a dizer a falha com os motivos da conferência, e o detalhe técnico vai ao log; a
recusa perde os asteriscos; a tela do sorteio diz o que a fonte publica do instante; e a ajuda da
etapa de Classificação ganha o item da ocorrência.

## Technical Context

**Language/Version**: Python 3.13, Django, templates do Django

**Storage**: nenhum dado novo. Na falha de acesso nada se grava, e continua assim (FR-3968).

**Testing**: pytest contra PostgreSQL (`make test-pg`)

**Constraints**: a CSP recusa estilo e script inline (091, 092) — nenhum estilo novo é necessário;
o item novo da ajuda usa `dt`, `dd` e `q`, sem classe. Toda `span.oculto` com `id` continua
apontada (`tests/interface/test_medida_dos_campos.py`).

## Constitution Check

| Princípio | Como esta feature o atende |
|---|---|
| I · Linguagem Ubíqua | os motivos são os quatro da `116`, e não uma tradução nova (D-001) |
| III · Auditoria | nada se grava na falha de acesso; o detalhe técnico vai ao log estruturado (FR-3962), que é onde a FR-3649 da `116` já põe o que não é ato |
| IV · Publicação imutável | nada publicado muda: a tela do sorteio lê a ocorrência como está |
| V · Observabilidade | o registro `observacao_sem_acesso_a_fonte` leva fonte, referência e as falhas de cada tentativa |

## Onde mexe

| Arquivo | O quê |
|---|---|
| `backend/processo_seletivo/sorteios/infrastructure/fontes/loteria_federal.py` | `_motivo_da_falha`, compartilhada por `_uma_chamada` e `observar`; evidência nova; log |
| `backend/processo_seletivo/sorteios/application/ocorrencia.py` | a recusa `source_unreachable` sem `**` |
| `backend/processo_seletivo/interface/views.py` | `fonte_publica_so_a_data` no contexto da tela do sorteio |
| `backend/processo_seletivo/interface/templates/interface/sorteio.html` | três frases para o "Aconteceu não antes de" |
| `backend/processo_seletivo/interface/templates/interface/_como_preencher_o_marco.html` | o item "Ocorrência que fixará a semente" |

## Testes

| Arquivo | O que prova |
|---|---|
| `backend/tests/integration/sorteios/test_falha_de_acesso_a_fonte.py` | os motivos por falha, a mensagem sem nome de exceção e sem `**`, o log |
| `backend/tests/interface/test_tela_do_sorteio.py` | as frases da fonte que publica só o dia e da que publica a hora |
| `backend/tests/interface/test_metodo_do_marco.py` | o item da ajuda e as frases idênticas às da descrição |
