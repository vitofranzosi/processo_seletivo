# Verificação — 056 · Polish do assistente de composição

**Protocolo.** Banco `ps_056_polish` (cópia de `ps_polish_audit`, o banco da auditoria), servidor
nativo na porta 8056 com o seletor de identidade, identidade `ana.gestora` com os papéis de
responsabilidade, Edital **76/2027** em elaboração (Retificar: Edital 01/2026). Janela de 1280 × 900;
medidas pelo `getBoundingClientRect` na página renderizada, e as de 375 px com o viewport emulado.
"Antes" medido em 30/09/2026 sobre `a7ade983`, antes de qualquer template, folha ou script mudar;
"depois" sobre a árvore desta feature. O passo a passo está no [quickstart](quickstart.md).

## A tabela "antes" da auditoria

A da §9 da auditoria, remedida aqui no mesmo banco; as linhas da auditoria que não são deste lote
ficam como estavam.

| Medida | Auditoria | Remedido (antes) |
|---|---:|---:|
| Topo do conteúdo da etapa Perfis | y = 524 | y = 524 |
| Conteúdo do Edital | 4.790 px | 4.876 px |
| Revisão | 7.987 px | 7.992 px |
| Retificar (Edital 01/2026) | 13.735 px | 13.988 px |
| Editor de um Perfil aberto | 3.283 px | 3.321 px |

## Antes e depois

| # | Medida | Antes | Depois | Critério |
|---|---|---|---|---|
| 1 | **Stepper** — altura, linhas, larguras dos `li` | 174 px, 2 linhas (7 + 2), 171 e 613 px | | SC-386 |
| 2 | h2 da etapa Perfis | y = 524 | | SC-387 |
| 3 | h2 das outras etapas (Identificação e Revisão / as demais) | 541 / 524 | | UX-137 |
| 4 | **Cronograma** — topo de Início / Término | 978 / 1.072 (linhas diferentes) | | SC-388 |
| 5 | Cronograma — largura da Descrição / de "Onde acontece" | 258 / 436 px (Descrição cortada) | | SC-388 |
| 6 | Cronograma — altura do cartão de Evento | 215 px | | SC-389 |
| 7 | Cronograma — legenda | "Evento do Cronograma 1 de 3" | | SC-390 |
| 8 | **Etapas** — cartões / linha só de ações | 388, 388, 468 px / sim, nos três | | SC-390 |
| 9 | **Documentos exigidos** — cartões / linha só de ações | 337 px (×3) / sim, nos três | | SC-390 |
| 10 | **Modalidade** (editor do DOC-INFO) — cartões / linha só de ações / legenda | 241 px (×2) / sim / "Modalidade de Concorrência" | | SC-390 |
| 11 | **Conteúdo do Edital** — altura da página | 4.876 px | | SC-391 |
| 12 | **Revisão** — altura da página | 7.992 px (teto: 8.791) | | SC-392 |
| 13 | Descrição do Perfil (DOC-INFO) | `input`, 386 px, cortada | | SC-393 |
| 14 | Instrução ao candidato (três documentos) | `input`, 499 px, sem corte no seed | | SC-393 |
| 15 | Retificar — Título do Edital / Descrição / Declaração do Requerimento | `input`, 312 px, cortados os três | | SC-393 |
| 16 | **Anexos** — "Avançar" (esquerda–direita) | 607–709 px; nas outras etapas 1.155–1.256 | | SC-394 |
| 17 | Retificar — ordem do Perfil | Requisitos, Modalidade ampla, Denominação, Descrição, Localidade, … | | FR-1038 |

## O envio de "Salvar rascunho"

O corpo que o navegador monta para o botão "Salvar rascunho", sem o token de CSRF, serializado em
pares e resumido por SHA-256 (16 primeiros hexadecimais). Não enviado ([D-005](research.md)). O
formulário 0 de toda página é o de sair, e não entra.

| Etapa | Pares | Antes | Depois | Igual? |
|---|---:|---|---|---|
| Identificação | 3 | `e9fc0a40f86dae0f` | | |
| Perfis | 66 | `1ff85b8b6b8bd574` | | |
| Cronograma | 22 | `42131277ff91a63b` | | |
| Etapas | 43 | `6b2b70c9ea074e40` | | |
| Classificação | 71 | `a41d89b0b3ea59d4` | | |
| Inscrição | 32 | `6574ad7d1847a468` | | |
| Anexos (acrescentar) | 3 | `fe29d413d5a8dec3` | | |
| Conteúdo | 18 | `0076b7289229c5ac` | | |
| Revisão | — | sem formulário de etapa | | |

## O teto da distribuição

`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`, isolado, com um `print` temporário:

| | Caracteres |
|---|---:|
| Antes | 83.093 |
| Depois | |
| **Saldo** | |

## A 375 px

| Tela | Largura de rolagem | Observação |
|---|---:|---|
| Stepper | | |
| Cronograma | | |
| Conteúdo | | |

## Capturas

A 1280 px, pelo cliente de teste e pelo Chrome sem janela, em [capturas/](capturas/): `antes-*.png` e
`depois-*.png` do topo da etapa Perfis, do Cronograma (cartões de Evento), do Conteúdo e da Revisão.
