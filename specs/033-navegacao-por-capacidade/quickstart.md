# Quickstart — como se verifica que esta feature funcionou

Quatro cenários. Os três primeiros são pela interface administrativa, percorridos com o seletor de
identidade; o quarto é a prova de que nada foi afrouxado, e é o que decide se a feature pode entrar.

## Pré-requisitos

```bash
cd backend && make lint check test-pg
```

`test-pg`, nunca `test`. `lint` são dois passos. `/gestao/` devolve 503 sem
`INTERFACE_SELETOR_IDENTIDADE=true`.

Monte, pela interface, um Edital publicado com **ato de classificação emitido** — é a situação em que
existe algo a divulgar. O seletor de identidade oferece os papéis separados, que é o que torna a
configuração segregada observável.

---

## Cenário 1 — o Publicador puro chega à divulgação (US1, `FR-473`/`FR-474`, `SC-164`)

**Entre como Publicador puro**: com a capacidade de publicar resultado e **sem vínculo de comissão
nenhum**.

| O que observar | Esperado |
|---|---|
| A tela do Edital | traz os marcos e, para cada ato emitido, o caminho até a divulgação |
| Clicar nesse caminho | a tela de divulgação **abre** |
| **URLs digitadas** | **zero** — é a medida de `SC-164` |
| Destinos de ordenação, corte e ocupação | **não** aparecem para ele: não são dele |

**Depois, entre como presidência sem capacidade de publicar.** Ela vê **tudo o que via antes** e nada
a menos — `FR-475`. Se algum destino sumiu para ela, a feature retirou caminho de alguém, e isso é
regressão, não melhoria.

**Depois, entre como quem preside e publica.** Vê os dois conjuntos, **sem o mesmo destino repetido**.

**E a ausência que não é recusa:** num Edital cujo marco ainda **não tem ato emitido**, o Publicador
não vê caminho de divulgação. Oferecer um caminho que termina em nada é o mesmo defeito com outra
roupa.

---

## Cenário 2 — a recusa se explica (US2, `FR-478`–`FR-481`)

**Entre como Publicador puro** e abra a tela de **distribuição** do mesmo Edital.

| O que observar | Esperado |
|---|---|
| Hoje | "não encontrado", sem explicação |
| Depois | recusa explicada: o que falta, a quem pedir, e que **nada foi alterado** |

**As contraprovas, e elas valem mais que o caso feliz:**

| Situação | Esperado |
|---|---|
| Edital de **outro escopo institucional** | **continua "não encontrado"** — `FR-480`. Se virar recusa explicada, a feature passou a vazar a existência de Editais de outras unidades |
| Identificador que não corresponde a nada | **"não encontrado"** — é a verdade |
| A mesma URL montada à mão, sem passar pela tela | **mesma recusa** — `FR-482`. Esconder o link não é a proteção |
| Uma recusa no **portal do candidato** | **404 uniforme, inalterado** — doutrina diferente, canal diferente |

---

## Cenário 3 — quem trava sabe a quem pedir (US3, `FR-484`–`FR-486`)

**Entre como presidência sem capacidade de publicar** e abra a tela do ato de classificação — é para
onde a tela de ordenação a manda.

| O que observar | Esperado |
|---|---|
| Hoje | *"Você não tem ação disponível sobre este ato."* |
| Depois | nomeia a capacidade que resolve e diz para pedir a quem a tem |

**As duas contraprovas de `FR-485`, e elas puxam para lados opostos de propósito:**

1. Onde a tela aceita **mais de uma base** — a permissão de gerir a comissão **ou** a presidência
   daquele Processo —, a frase nomeia **as duas** (`FR-479`). Nomear só a presidência mandaria a
   pessoa pedir metade do que resolve, e uma das duas **é** um papel.
2. Onde a tela aceita **só o vínculo**, a frase nomeia a presidência e **não** inventa um papel que a
   conceda, porque nenhum concede.

O que `FR-485` proíbe é nomear papel que **não** resolve aquele caso — não é nomear papel.

---

## Cenário 4 — nada foi afrouxado (`FR-483`, `SC-168`)

**É o cenário que decide se a feature entra.** Faça-o com o diff na mão.

**Antes de mudar qualquer coisa**, registre a contagem de `tests/authorization/` — hoje **197 casos**
em 38 arquivos.

**Depois**, a conferência é aritmética:

| O que conferir | Esperado |
|---|---|
| Casos removidos | **zero** |
| Casos que mudaram | apenas o **status esperado**, de `404` para `403` |
| Casos que passaram a esperar sucesso onde esperavam recusa | **zero** — qualquer um derruba a feature |
| Asserções sobre **quem** entra | **intactas**, uma a uma |

**Leia o diff caso a caso, e não só a contagem.** Um caso pode manter o número de asserções e trocar
o ator — e a suíte fica verde. É o modo de falha que este cenário existe para pegar, e nenhum teste
o pega por você.

**O caso renomeado:** `test_quem_nao_tem_vinculo_nenhum_recebe_inexistente` afirma no próprio nome a
doutrina antiga. O nome muda; a asserção de que aquele ator **não entra** fica idêntica.
