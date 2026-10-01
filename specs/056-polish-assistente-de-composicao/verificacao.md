# Verificação — 056 · Polish do assistente de composição

**Protocolo.** Banco `ps_056_polish` (cópia de `ps_polish_audit`, o banco da auditoria), servidor
nativo na porta 8056 com o seletor de identidade, identidade `ana.gestora` com os papéis de
responsabilidade, Edital **76/2027** em elaboração (Retificar: Edital 01/2026). Janela de 1280 × 900;
medidas pelo `getBoundingClientRect` na página renderizada, e as de 375 px com o viewport emulado.
"Antes" medido em 30/09/2026 sobre `a7ade983`, antes de qualquer template, folha ou script mudar;
"depois" sobre a árvore desta feature, no mesmo banco, sem gravar nada entre as duas. O passo a passo
está no [quickstart](quickstart.md).

## A tabela "antes" da auditoria

A da §9 da auditoria, remedida no mesmo banco. As linhas dela que não são deste lote ficam de fora.

| Medida | Auditoria | Antes (remedido) | Depois |
|---|---:|---:|---:|
| Topo do conteúdo da etapa Perfis | y = 524 | y = 524 | **y = 416** |
| Conteúdo do Edital | 4.790 px | 4.876 px | **2.908 px** |
| Revisão | 7.987 px | 7.992 px | 8.328 px (+4,2%) |
| Retificar (Edital 01/2026) | 13.735 px | 13.988 px | 13.903 px |
| Editor de um Perfil aberto | 3.283 px | 3.321 px | 3.152 px |

## Antes e depois

| # | Medida | Antes | Depois | Critério |
|---|---|---|---|---|
| 1 | **Stepper** — altura, linhas, larguras dos `li` | 174 px, 2 linhas (7 + 2), 171 e 613 px | **66 px**, 1 linha, 131 px todos | ✅ **SC-386** |
| 2 | h2 da etapa Perfis | y = 524 | **y = 416** | ✅ **SC-387** |
| 3 | h2 das outras etapas (Identificação e Revisão / as demais) | 541 / 524 | 433 / 416 | ✅ **UX-137** |
| 4 | **Cronograma** — topo de Início / Término | 978 / 1.072 (linhas diferentes) | mesmo topo | ✅ **SC-388** |
| 5 | Cronograma — largura da Descrição / de "Onde acontece" | 258 / 436 px | **406 / 320 px** | ✅ **SC-388** |
| 6 | Cronograma — altura do cartão de Evento | 215 px | 216 px | ⚠️ **SC-389** fora de alcance — ver abaixo |
| 7 | Cronograma — legenda | "Evento do Cronograma 1 de 3" | "Evento do Cronograma 1 de 3 · **Inscrições**" | ✅ **SC-390** |
| 8 | **Etapas** — altura dos cartões / linha só de ações | 388, 388, 468 px / sim, nos três | **299, 299, 378 px** / não: ações na linha da legenda | ✅ **SC-390** |
| 9 | **Documentos exigidos** — altura / linha só de ações | 337 px (×3) / sim, nos três | 304 px (×3) / não | ✅ **SC-390** |
| 10 | **Modalidade** (editor do DOC-INFO) — altura / linha só de ações / legenda | 241 px (×2) / sim / "Modalidade de Concorrência" | **200 px** (×2) / não / "… **AC**", "… **PPP**" | ✅ **SC-390** |
| 11 | Ações × legenda (os quatro cartões) — centro vertical | — | igual ao da legenda, ±1 px; nenhum campo sob o grupo | ✅ **FR-1023** |
| 12 | Reordenação — legenda depois de "Descer" no 1º Evento | — | "1 de 3 · Prova objetiva", "2 de 3 · Inscrições": a posição acompanha, o nome vai com o cartão | ✅ **FR-1025** |
| 13 | **Conteúdo do Edital** — altura da página | 4.876 px | **2.908 px** | ✅ **SC-391** |
| 14 | Conteúdo — seções que dizem "(vazia — não sai no documento)" | 18 | 18 | ✅ **SC-391** |
| 15 | Conteúdo — cartão / área de texto / seção vazia / seção gerada | 1.232 / 685 / 171 / 121–139 px | 719 / 685 / 99 / 61 px | ✅ **FR-1029**, **FR-1030**, **FR-1032** |
| 16 | Conteúdo — digitar numa seção vazia | a marca some e a numeração se refaz | igual: "Público-Alvo (vazia — …)" → "1. Público-Alvo" → volta | ✅ **FR-1031** |
| 17 | **Revisão** — altura / rótulos em coluna | 7.992 px / "Rótulo: valor" corrido | **8.328 px** (+4,2%; teto 8.791) / 76 pares em 29 `dl` | ✅ **SC-392** |
| 18 | Revisão — texto de cada item, na ordem | — | **52 de 52 iguais** (pares recompostos como "Rótulo: valor") | ✅ **FR-1034** |
| 19 | Descrição do Perfil (DOC-INFO) | `input`, 386 px, **cortada** | `textarea` de 2 linhas, sem corte | ✅ **SC-393** |
| 20 | Instrução ao candidato (três documentos) | `input`, 499 px | `textarea` de 2 linhas, sem corte | ✅ **SC-393** |
| 21 | Retificar — Título / Descrição / Declaração do Requerimento | `input` de 312 px, os três **cortados** | `textarea` de 2 / 2 / 4 linhas, sem corte (D-014) | ✅ **SC-393** |
| 22 | Retificar — digitar no Título marca o campo alterado | sim | sim; e desmarca ao voltar ao valor | ✅ **FR-1036** |
| 23 | **Anexos** — "Avançar" (esquerda–direita) | 607–709 px | **1.154–1.256 px**; nas outras etapas 1.155–1.256 | ✅ **SC-394** |
| 24 | Anexos — estado vazio / acrescentar / navegação | 685 / 1.232 / 685 px | 1.232 / 1.232 / 1.232 px | ✅ **FR-1037** |
| 25 | Retificar — ordem do Perfil | Requisitos, Modalidade ampla, Denominação, Descrição, Localidade, … | Denominação, Localidade, Descrição, Carga horária, Remuneração, Atribuições, Requisitos, … — nomes `g2c1`…`g2c12` iguais | ✅ **FR-1038** |

### A meta de 150 px do cartão de Evento (SC-389)

**Não alcançada: 215 px antes, 216 depois.** Registrado como o prompt manda, sem ampliar o escopo
([D-006](research.md)). O cartão já tinha duas linhas de campo antes — as ações dividiam a segunda
com o Término, e não tinham linha própria —, e a 5ª decisão recebida mantém duas: Tipo, Descrição,
Início e Término numa, "Onde acontece" na de baixo. Duas linhas de campo com o rótulo em cima somam
~165 px pelo ritmo da folha antes do preenchimento do cartão. Os 150 px pediriam "Onde acontece" na
primeira linha (contra a 5ª decisão) ou o rótulo dele ao lado do campo (um desenho que a folha não
tem). O que o Evento ganhou é leitura: datas lado a lado, Descrição de 258 para 406 px, a legenda
dizendo qual Evento é.

## O envio de "Salvar rascunho"

O corpo que o navegador monta para o botão "Salvar rascunho", sem o token de CSRF, serializado em
pares e resumido por SHA-256 (16 primeiros hexadecimais). Não enviado ([D-005](research.md)). Onde o
resumo muda, a comparação é do conjunto de pares (chave, valor), com repetição.

| Etapa | Pares | Antes | Depois | Resultado |
|---|---:|---|---|---|
| Identificação | 3 | `e9fc0a40f86dae0f` | `e9fc0a40f86dae0f` | **idêntico** |
| Perfis | 66 | `1ff85b8b6b8bd574` | `c88c247a5d45bf26` | **mesmo conjunto**, com o `ruleId` gerado no render mascarado ([D-015](research.md)) |
| Cronograma | 22 | `42131277ff91a63b` | `9f34119c7b6b4a9c` | **mesmo conjunto**; muda só a ordem — `location` depois de `endAt` ([D-005](research.md), [D-006](research.md)) |
| Etapas | 43 | `6b2b70c9ea074e40` | `6b2b70c9ea074e40` | **idêntico** |
| Classificação | 71 | `a41d89b0b3ea59d4` | `a41d89b0b3ea59d4` | **idêntico** |
| Inscrição | 32 | `6574ad7d1847a468` | `6574ad7d1847a468` | **idêntico** (a Instrução virou `textarea` e manda o mesmo valor) |
| Anexos (acrescentar) | 3 | `fe29d413d5a8dec3` | `fe29d413d5a8dec3` | **idêntico** |
| Conteúdo | 18 | `0076b7289229c5ac` | `0076b7289229c5ac` | **idêntico** |
| Revisão | — | sem formulário de etapa | — | — |

**Diff dos envios: vazio** — nenhuma chave entra ou sai, nenhum valor muda. ✅ **SC-395**

## O teto da distribuição

`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`, isolado, com um `print` temporário:

| | Caracteres |
|---|---:|
| Antes | 83.093 |
| Depois | 83.294 |
| **Saldo** | **+201** |
| Margem sob 120.000 | de 36.907 para 36.706 |

A prosa nova da folha comum está em comentário de Django, que não vai no HTML. O estilo do Conteúdo,
da Revisão, do Cronograma e de Anexos foi para o `estilo_da_pagina` de cada etapa. Nenhum comentário
existente foi removido para abrir espaço; os que descreviam regras que saíram (a reserva de rótulo e
a coluna do grupo dentro da faixa de campos) saíram com elas. ✅ **FR-1040**

## A 375 px

| Tela | Largura de rolagem | Observação |
|---|---:|---|
| Stepper | 375 | 2 colunas de 160 px, 5 linhas; a 9ª sozinha, na largura das outras |
| Cronograma | 375 | campos empilhados; o grupo de ações numa linha abaixo da legenda, à direita |
| Conteúdo | 375 | nenhum controle fora da janela |

✅ **SC-397**. Também a 375 px, Etapas, Inscrição e o editor do Perfil ficam na largura da janela.
A primeira medição "depois" achou o editor do Perfil com 481 px: no fluxo, o grupo de ações da
Modalidade — duas ações em texto, que não quebram — não cabia, e o `fieldset`, que cresce até o
conteúdo mínimo dele, alargava o cartão do Perfil inteiro. O grupo passou a quebrar no fluxo, e a
página voltou a 375 px. A guarda está em `test_a_folha_leva_o_grupo_para_a_borda_e_o_devolve_em_tela_estreita`.

## Capturas

A 1280 px, pelo cliente de teste e pelo Chrome sem janela, em [capturas/](capturas/): `antes-*.png` e
`depois-*.png` do topo da etapa Perfis, do Cronograma (cartões de Evento), do Conteúdo e da Revisão.

## A suíte

`make lint check test-pg`, com `DB_NAME` próprio, sobre esta árvore, depois da última mudança: verde — os totais estão na descrição do PR. A suíte de checkpoint, antes das correções da D-016 e do grupo em tela estreita, deu 9 falhas, todas tratadas acima.
