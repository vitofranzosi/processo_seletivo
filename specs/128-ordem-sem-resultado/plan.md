# Implementation Plan: A ordem por pontuação sem nenhum resultado é recusada

**Branch**: `claude/128-ordem-sem-resultado-9720fd`, sobre `claude/126-orientacao-p0-307906` (PR #414) |
**Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: a spec desta pasta; a *Decisão do usuário* da `126` (opção b da G-01).

## Summary

Uma regra nova, escrita uma vez e lida em quatro lugares:

- **A regra** (D-004, R-1): `universo_classificavel.nenhuma_com_resultado(marco, linhas)`, pura, diz se
  um universo não vazio não tem Resultado em Etapa enumerada; `classificacao/application/ordem_sem_resultado.py`
  monta, da proposta calculada, o impedimento — a frase, a contagem e as Etapas — e a recusa
  `ordering_without_stage_results`.
- **O comando** (`emitir_ordem`): chama a recusa logo depois de `calcular_ordem`, sob a trava, antes da
  busca do vigente, da assinatura e do motivo (FR-4206, D-005). A sucessão e o gesto passam por aqui.
- **A conferência do gesto** (`conducao_do_marco._alcance_da_ordem`): chama a mesma recusa dentro do
  `try` que já transforma `DomainError` em *impedido* (FR-4216).
- **A tela da ordem** (`views.ordenacao`, `ordenacao.html`): o impedimento entra no contexto; o
  formulário, a sucessão e o pedido "peça a alguém que a emita" dão lugar ao bloco UX-261, com os links
  da distribuição para quem gere. A rota da confirmação volta à tela em vez de abrir (FR-4215).
- **A confirmação da `126`** (`conferencia_da_ordem.resumo`): `nenhuma_com_resultado` passa a vir da
  função da regra (FR-4217).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL. **Sem migration**, sem tabela, sem coluna (FR-4219)

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio); captura de antes e depois
da tela da ordem num banco descartável montado pelos helpers dos testes

**Target Platform**: a gestão, em navegador, renderizada no servidor

**Project Type**: aplicação web

**Performance Goals**: **nenhuma consulta nova**. A regra lê a proposta que o cálculo já montou (R-1); a
tela já calcula a proposta. O orçamento de consulta da ordem (`tests/performance/`) não muda.

**Constraints**: CSP sem `inline` (o bloco usa classes que já têm regra na folha: `aviso`); classe citada
em template exige regra na folha; vocabulário pela varredura; a `126` toca `ordenacao.html`,
`ordenacao_confirmar.html`, `views.py` e `conducao_do_marco.py`, e esta branch parte dela (R-6)

**Scale/Scope**: dois módulos de domínio/aplicação, o comando, a conferência do gesto, uma view, um
template; testes e fixtures que emitiam ordem sem resultado (R-5)

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | "recorte", "Resultado", "Etapa enumerada", "ordem" são os termos do domínio; a frase usa "resultado" e "Etapa" como as telas | ✅ |
| II — imutabilidade e temporalidade | nada do acervo é tocado: a ordem vazia gravada continua vigente e reproduzível (FR-4219); a regra é avaliada no instante da emissão, sob a trava, com a versão que o cálculo lê | ✅ |
| III — negar por padrão | uma recusa a mais, nenhuma permissão nova; os links da distribuição só para quem tem a base que a distribuição exige (FR-4213) | ✅ |
| IV — regra explícita | uma função, chamada pelo comando, pela tela e pela conferência do gesto; a confirmação da `126` usa a mesma (D-004) | ✅ |
| V — simplicidade e rastreabilidade | sem estado novo; testes ajustados nomeados em `verificacao.md` (FR-4220) | ✅ |
| VI — jornada demonstrável | captura antes e depois da tela da ordem (quickstart) | ✅ |

Nenhuma entrada em *Complexity Tracking*. Reavaliado depois do desenho: sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/128-ordem-sem-resultado/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/telas.md
├── tasks.md
├── rastreabilidade.md
├── verificacao.md
├── capturas/
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── classificacao/domain/universo_classificavel.py        # nenhuma_com_resultado (pura)
├── classificacao/application/ordem_sem_resultado.py      # impedimento e recusa, da proposta
├── classificacao/application/emissao.py                  # a recusa no comando
├── interface/conducao_do_marco.py                        # a recusa na conferência do gesto
├── interface/conferencia_da_ordem.py                     # a confirmação da 126 lê a mesma regra
├── interface/views.py                                    # ordenacao e emitir_ordenacao
└── interface/templates/interface/ordenacao.html          # o bloco no lugar do formulário

backend/tests/
├── unit/classificacao/test_ordem_sem_resultado.py
├── integration/classificacao/test_ordem_sem_resultado.py
├── interface/test_ordem_sem_resultado.py
└── (os ajustes de R-5)
```

**Structure Decision**: a regra fica em `classificacao`, junto do universo que ela lê; a interface só a
chama.

## Complexity Tracking

Nada a justificar.
