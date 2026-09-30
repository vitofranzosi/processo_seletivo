# Verificação — 055 · Polish da folha e dos componentes

**Protocolo.** Banco `ps_055_polish` (cópia de `ps_polish_audit`, o banco da auditoria), servidor
nativo na porta 8055 com o seletor de identidade e o portal de demonstração, identidade
`ana.gestora` com todos os papéis, candidata do fixture no portal. Janela de 1280 × 900; medidas pelo
`getBoundingClientRect` na página renderizada, e as de 375 px com o viewport emulado. "Antes" medido
em 30/09/2026 sobre `c0f5ad3d` com a folha intocada; "depois" sobre a árvore desta feature. O passo a
passo está no [quickstart](quickstart.md).

## Antes e depois

| # | Medida | Antes | Depois | Critério |
|---|---|---|---|---|
| 1 | **Corte** — a faixa calculada | 12 itens numa fileira (y = 516), rótulo e número alternados: cada número entre dois rótulos | 6 blocos, o número acima do rótulo dentro de cada um | ✅ **SC-371** |
| 2 | **Ocupação** — o recorte apurado | `section` flex; os quatro números num `dl` de 70 px ao lado do título | `section` em bloco; 4 blocos de 80 a 100 px, abaixo do título | ✅ **SC-372** |
| 3 | **Inscrições** do 51/2026 — altura da linha | 69,2 px (a auditoria mediu 70) | 62,8 px com a marca de CPF repetido; **39,5 px** sem ela | ⚠️ **SC-373** parcial — [D-021](research.md) |
| 4 | **Assistente** (Cronograma) — Voltar, Salvar rascunho, Avançar | 26 / 38 / 36 px | 40 / 40 / 40 px | ✅ **SC-374** |
| 5 | Revisão — Voltar, Visualizar, Submeter, Ver situação (quatro **links**) | 30 / 44 / 42 / 30 px | 40 / 40 / 40 / 40 px | ✅ **FR-1006** |
| 6 | Anexos — Voltar, Avançar | 30 / 42 px | 40 / 40 px | ✅ **FR-1007** |
| 7 | Retificação — Ver o que vai mudar, Voltar | 38 / 30 px | 40 / 40 px | ✅ **FR-1007** |
| 8 | Rodapé de confirmação (Encerrar) — Confirmar, Cancelar | — | 40 / 40 px | ✅ **FR-1007** |
| 9 | "Filtrar" — Inscrições, Distribuição, Comissão | 26 px (`.acao`) | 40 px (`.botao`) | ✅ **SC-375** |
| 10 | "Ver o que sairá vazio" — Matrículas | 26 px (`.acao`) | 40 px, na altura do `select` ao lado | ✅ **SC-375** |
| 11 | **Portal** — "Guardar e continuar depois" | botão nativo: Arial 13,3 px, 22 px de altura | secundário do portal: Open Sans 16 px, 43,4 px | ✅ **SC-376** |
| 12 | **Títulos** — Convocação (h2 / h3) | 18,4 / **18,7** px | 18,4 / 16,0 px | ✅ **SC-377** |
| 13 | Títulos — Processo (h2 / h3 "Atenção") | **16,0** / 18,7 px | 18,4 / 16,0 px | ✅ **SC-377** |
| 14 | Títulos — Revisão (três h2 irmãos) | 16,0 / 18,4 / 16,0 px | 18,4 / 18,4 / 18,4 px | ✅ **FR-1011** |
| 15 | Títulos — Retificação (h2 das seções) | 16,0 px, caixa-alta | 18,4 px, caixa normal | ✅ **FR-1011** |
| 16 | **Controles** — Visão Geral (`select` / busca) | 41 / 39 px | 40 / 40 px | ✅ **SC-378** |
| 17 | Controles — Requerimento do portal (texto / `select` / data) | 40 / 42 / 42 px | 42 / 42 / 42 px | ✅ **SC-378** |
| 18 | Controles — Comissão (busca / texto / `select` / seletor do cartão) | 39 / 37 / 39 / 36 px | 40 / 40 / 40 / 40 px | ✅ **SC-378** |
| 19 | Controles — Cronograma (texto / data e hora) | 39 / 41 px | 40 / 40 px | ✅ **FR-1012** |
| 20 | **Filtro da Distribuição** — topo do `select` / do `input` / do Filtrar | 1.218 / 1.196 / 1.231 (desnível de **22 px**) | 1.200 / 1.200 / 1.200 (**0**), Filtrar com 40 px | ✅ **SC-379** |
| 21 | Filtro das Inscrições — topo da busca / da Concorrência | 322 / 343 (21 px) | 321,7 / 321,7 (0) | ✅ **FR-1013** |
| 22 | Filtro da Comissão — centro da busca / da marca / do Filtrar | marca 24 px acima | 318,09 / 318,09 / 318,09 | ✅ **FR-1013** |
| 23 | Filtro do Reaproveitar (fora da lista, alcançado pela folha) | — | busca e Filtrar no mesmo topo, 40 px | ✅ **FR-1013** |
| 24 | **Seleção sem sorteio** (01/2026) — topo das Vagas / do Cronograma | 493 / 808 (**315 px** abaixo) | 493 / 493 | ✅ **SC-380** |
| 25 | Seleção com sorteio (26/2026) — Sorteio / Cronograma | 493 / 742 | 493 / 742 (inalterado) | ✅ **FR-1015** |
| 26 | **Comissão** — Identificador institucional / Nome | 1.190 / 1.190 px | 320 px (20 rem) / 685 px (`--leitura`) | ✅ **SC-381** |
| 27 | **Requerimento** — Telefone celular | 1.232 px | 296 px (~18,5 rem) | ✅ **SC-382** |
| 28 | Requerimento — Nome da mãe / do pai / Faixa de renda | 1.232 px cada | 640 px (40 rem) cada | ✅ **FR-1016** |
| 29 | Requerimento — UF do endereço | 296 px, sozinha na linha | 296 px, sozinha na linha (D-013) | = |
| 30 | Anexos — Arquivo / Rótulo | 1.190 / 685 px | 366 / 685 px | ✅ **FR-1016** |
| 31 | **Ordem do marco** — alinhamento da pontuação | esquerda ("26") | direita | ✅ **SC-383** |

## A 375 px

Largura de rolagem do documento igual à janela (375 px), e nenhum elemento fora dela fora de um
contêiner de rolagem próprio, nas quatro telas de **FR-1018**:

| Tela | Largura de rolagem | Observação |
|---|---:|---|
| Inscrições | 375 | busca, Concorrência e Filtrar empilhados, 40 px cada |
| Requerimento do portal | 375 | uma coluna; Telefone com 343 px |
| Seleção do portal (sem sorteio) | 375 | Vagas, Cronograma e Documentos, nessa ordem |
| Barra de filtro — Distribuição e Comissão | 375 | controles empilhados; a ajuda sob o campo |

✅ **SC-385**

## O teto da distribuição

`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`, isolado, com a asserção trocada
por um `print` (D-001):

| | Caracteres |
|---|---:|
| Antes | 119.953 |
| Depois | **119.884** |
| **Saldo** | **−69** |
| Margem sob 120.000 | de 47 para **116** |

O saldo é negativo porque as regras substituídas saíram junto com as novas, e as declarações que
ficaram iguais à nova regra global de célula saíram também (D-010). A prosa nova está em comentário
de Django, que não é servido. Nenhum comentário existente foi removido.

✅ **FR-1017**

## Capturas

A 1280 px, pelo cliente de teste e pelo Chrome sem janela (D-018), em [capturas/](capturas/):
`antes-*.png` e `depois-*.png` do Corte, da Ocupação, das Inscrições, do assistente (Cronograma) e da
Distribuição.

## A suíte

Ver o PR: `make lint check test-pg` sobre esta árvore.
