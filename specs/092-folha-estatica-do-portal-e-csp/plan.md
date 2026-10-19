# Implementation Plan: A folha do portal em arquivo, e o portal sob a política de segurança de conteúdo

**Branch**: `claude/hungry-swirles-ac1f38` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

O `<style>` do `portal/templates/portal/base.html` (65.839 bytes, 124 comentários de CSS e nenhum
`{% comment %}`) vai, na mesma ordem, para `portal/static/portal/portal.css`, carregado pela tag
`estatico` da `089` depois dos tokens; só sete grafias mudam, as que a varredura de sintaxe vazada
acusaria num arquivo estático (R-002). O `style=""` da barra de documentos (`_documentos.html`) vira
uma classe por percentual, `.largura-0` a `.largura-100`, no arquivo do portal. Os guardiões que liam a
folha no modelo ou na página passam a ler o arquivo, ou a folha aplicada, e cada um é provado por
mutação (R-004). Então `shared/politica_de_conteudo.py` deixa de decidir pelo caminho: todo HTML vai em
recusa, o modo de observação sai, e o protótipo do painel perde a marca `em_observacao` (D-003). Nenhuma
migration, permissão, view, endereço, consulta ou texto muda.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2.17, PostgreSQL (nada de banco muda).

**Primary Dependencies**: `django.contrib.staticfiles` e a tag `estatico` da `089`; o middleware da
`091`. Nenhuma dependência nova.

**Storage**: N/A.

**Testing**: pytest (`make test-pg`); os guardiões em `tests/interface/`, `tests/portal/` e
`tests/integration/`, pelo apoio `tests/interface/folha.py`; a prova visual e de console por
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/`, com Chrome sem cabeça.

**Target Platform**: o runserver local e o caminho de produção do guia: o nginx já serve
`/static/` da release, e `portal/static/portal/` está debaixo dele.

**Project Type**: monólito web Django, interface por modelos.

**Performance Goals**: cada página inteira do portal perde ≈ 65 KB de HTML; a folha vem uma vez e fica no
cache, com a versão do conteúdo no endereço.

**Constraints**: zero mudança visual; nenhum guardião enfraquecido; sem dependência nova;
`.claude/launch.json` intocado; base na branch do PR #308, ainda aberto.

**Scale/Scope**: 1 folha de 954 linhas; 1 atributo `style`; 1 módulo de política; 1 view; 14 arquivos de
teste repontados ou estendidos (R-004).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Negar por padrão (III, IV)**: a política passa a valer em recusa em todo HTML, e a área nova nasce
  sob ela, em vez de nascer em observação. Nenhuma view, permissão ou escopo muda.
- **Imutabilidade e preservação (II)**: nenhum dado normativo, tabela ou documento publicado muda; o
  comprovante em PDF sai de outro escritor, e o teste de bytes dele não é tocado.
- **Linguagem ubíqua (I)**: nomes em português (`portal.css`, `recebe_a_politica`, `FOLHA_DO_PORTAL`).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py` — que passa a varrer `*.css` (R-004).
- **Simplicidade (V)**: um arquivo, e não um por área (D-001); a política perde um ramo e uma função.
- **Completude de jornada (VI)**: as telas do portal alcançáveis da vitrine e da área de seis
  candidatas, mais três rascunhos com a barra em 0, 50 e 100%, antes e depois, com o console de cada
  uma; o papel do comprovante.

Sem violação a justificar. Reavaliado depois do desenho: igual.

## Project Structure

### Documentation (this feature)

```text
specs/092-folha-estatica-do-portal-e-csp/
├── spec.md
├── plan.md
├── research.md          # R-001..R-007
├── quickstart.md        # o roteiro da prova
├── rastreabilidade.md   # requisito → onde é provado
├── tasks.md
└── checklists/requirements.md
```

`data-model.md` e `contracts/` não se aplicam: não há entidade, e o contrato com o navegador é o
cabeçalho, que a suíte testa.

### Source Code

| Peça | Mudança |
|---|---|
| `portal/static/portal/portal.css` | novo: o `<style>` da base, com cabeçalho, as sete grafias e as classes de percentual |
| `portal/templates/portal/base.html` | `<link>` pela `estatico` no lugar do `<style>` |
| `portal/templates/portal/_documentos.html` | `largura-N` no lugar do `style="width:N%"` |
| `shared/estaticos.py` | `portal/portal.css` em `FOLHAS`, conferida pela verificação de sistema |
| `shared/politica_de_conteudo.py` | uma política, em recusa, para todo HTML; sai `EM_RECUSA`, o cabeçalho de observação e `em_observacao` |
| `interface/prototipo_do_assistente.py` | sem `em_observacao` |
| `backend/tests/…` | os guardiões repontados (R-004) e os novos |
| `doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/` | `capturar_portal.py`, `preparar_rascunhos.py`, `equivalencia.py`, `mutacoes.py`, `pesar_portal.py`, e os resultados |

## Ordem

0. Partir da branch do PR #308 (`git merge --ff-only`), que a `main` ainda não tem.
1. Medir antes, por `git archive` do commit de partida: preparar os rascunhos no banco-modelo do
   inventário, rastrear e capturar o portal, a passada de ruído, as bases e o papel.
2. A folha para arquivo; o atributo para classe; `FOLHAS`.
3. Os guardiões repontados, e a suíte acusando os que quebram alto.
4. A política em recusa em todo HTML; o protótipo.
5. Medir depois e comparar; equivalência; mutação; peso; `make lint check test-pg`.
6. `/code-review` no PR, sem `--comment`; corrigir os achados confirmados.

## Verificação

`cd backend && make lint check test-pg DB_NAME=ps_092 POSTGRES_USER=$USER` com `LC_ALL=pt_BR.UTF-8`,
depois de `uv sync --extra dev --extra assistente`; o roteiro do [quickstart](quickstart.md).
