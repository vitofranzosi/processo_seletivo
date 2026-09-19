# Varredura dos doze Editais da amostra real — `T046` · `SC-174`

**O que esta varredura responde**: quais avisos da família da `032` ainda disparam em cada Edital da
amostra, e quais deixaram de disparar por causa da `034`.

**Por que ela existe, e por que é leitura Edital a Edital.** Checklist, `analyze` e o teste de
citações ficam verdes com regras que se contradizem — foi a varredura equivalente da `032` que
confirmou a decisão de tratar por aviso, e é ela que separa "a regra está escrita" de "a regra
alcança o acervo real".

**Fonte**: [doc/avaliacao-de-capacidade-editais-2026-09-12.md](../../doc/avaliacao-de-capacidade-editais-2026-09-12.md),
seção *Por Edital — a amostra inteira*, e
[doc/achados-editais-externos.md](../../doc/achados-editais-externos.md). Os PDFs originais não estão
no repositório.

---

## A família, antes e depois

| Achado | Antes da `034` | Depois |
|---|---|---|
| `profile_without_milestone` | impedimento | **inalterado** |
| `drawn_milestone_without_method` | impedimento | **inalterado** |
| `milestone_without_cut_rule` | aviso | **inalterado** |
| `reserved_row_without_ordering` | aviso | **aposentado** (`FR-501`) |

**A família passou de quatro achados para três**, e foi essa mudança que a varredura mediu Edital a
Edital.

---

## Por Edital

O que decide se o aviso aposentado **dispararia** é a conjunção: o Perfil reparte vagas em Modalidade
reservada **e** o marco que o governa **não** ordena por sorteio.

| Edital | Reparte cota? | O marco sorteia? | O aviso disparava? | Depois da `034` |
|---|---|---|---|---|
| **58/2026** 3 cursos FIC | não | sim | não | sem mudança |
| **59/2026** Libras A1 | não | sim | não | sem mudança |
| **69/2026** Multimeios | não | sim | não | sem mudança |
| **77/2026** FIC remanescentes | não | sim | não | sem mudança |
| **78/2026** Libras A1 remanescentes | não | sim | não | sem mudança |
| **158/2024** FIC Educação Especial | não | sim | não | sem mudança |
| **57/2026** unificado, 2 cursos | **sim** — três listas | sim | não | sem mudança |
| **28/2026** Informática na Educação | **sim** — 7 polos × 3 modalidades | sim | não | sem mudança |
| **173/2025** Designer Educacional | **sim** — ordem por modalidade | **não** — computado, prova de títulos | **sim** | **deixa de disparar** |
| **14/2026** Orientador de TFC | não | não — computado | não | sem mudança |
| **76/2026** Secretaria Escolar | bloqueado pela `P-8` antes do quadro | — | não alcançado | sem mudança |
| **46/2026** técnicos integrados | fora do alvo por decisão | — | — | — |

### A correção de uma contagem herdada

O docstring de `_reserva_sem_via_de_apuracao`, escrito pela `032`, dizia que **três** Editais da
amostra declaram reserva em marco computado: *"57/2026, 28/2026 e 173/2025"*. A leitura Edital a
Edital mostra que **é um**: o 57/2026 e o 28/2026 repartem cota, mas os marcos deles **sorteiam** — e
o sorteio emite por lista desde a `021`, de modo que o aviso nunca os alcançou. A conjunção que o
aviso exige é cota **e** marco computado, e só o **173/2025** a satisfaz.

*A frase da `032` não errou o que importava para ela* — os três são Editais reais com cota, e para os
três a apuração por recorte acontecia fora do sistema, porque a `021` emite a ordem sorteada mas a
`016` não tinha a via computada. O que a frase misturou foi *"declaram reserva em marco computado"*
com *"têm cota cuja cauda não fecha"*. Esta varredura separa as duas.

**Consequência para a `034`**: o efeito da feature sobre o acervo lido é **maior** do que o aviso
media, e não menor. O aviso alcançava um Edital; a ordem por recorte alcança os **três** que repartem
cota — porque o que faltava ao 57/2026 e ao 28/2026 não era a ordem (o sorteio já a emitia), e sim a
cauda que a `016` e a `019` já tinham. A `034` fecha o lado computado, que era o único que faltava.

---

## `SC-174` — o critério, e o que resta

> **Nenhum** aviso da família da `032` dispara sobre recorte que passou a ter via de apuração, e a
> varredura contra os doze Editais da amostra real registra quais avisos restam.

**Cumprido.** Nenhum aviso da família dispara por causa de reserva sem via de apuração, em Edital
nenhum da amostra — o achado que o fazia não existe mais.

**Os que restam**, e que a `034` não toca:

| Edital | Aviso que permanece | Por quê |
|---|---|---|
| **14/2026** | `milestone_without_cut_rule` — se o marco não declarar regra de corte | é outra regra, da família do corte (`FR-463`) |
| **69/2026** | nenhum — a regra de corte dele declara não governar Etapa alguma, e isso é legítimo | `FR-224` |
| **76/2026** | `P-8` continua bloqueando antes do quadro | é inversão de estrutura, e não achado desta família |

**Nenhum Edital da amostra ganhou aviso novo por causa da `034`.** A feature remove um achado e não
cria nenhum.
