# Percursos — cinco, e o quinto é o que a feature não pode quebrar

**Tudo pela interface.** Shell e banco preparam o ambiente e diagnosticam; **não atravessam passo
que deveria estar disponível à pessoa**. Não havendo caminho, registre a lacuna e siga — protocolo
da `034`.

**Antes**: seletor de identidade da gestão ligado, e um Processo com **dois** Editais publicados —
o `seed_demo` precisa de dois, porque prazo aberto e resultado divulgado não cabem no mesmo.

---

## 1 — O Processo passa a conduzir (`SC-196`, `SC-197`)

1. Abra a página do **Processo**.

**Esperado**: por Edital, o pulso — quanto chegou, o período, o que vem — e a Atenção. Hoje a página
lista Editais e oferece encerrar ou cancelar.

2. Abra a **Supervisão** do mesmo Processo e compare.

**Esperado**: **os mesmos números**. Se divergirem, alguém recalculou em vez de ler (`FR-557`).

3. Entre como alguém que alcança o Processo e **não alcança** o destino de um sinal.

**Esperado**: lê o estado, e **não recebe o caminho** (`FR-558`).

4. Abra um Processo **sem sinal algum**.

**Esperado**: **uma linha** declarando a ausência — não uma seção vazia por espécie (`FR-559`).

---

## 2 — Avaliação parada, e o que ela não é (`SC-198`)

1. Distribua uma Etapa e **não conclua** as avaliações.

**Esperado**: sinal que nomeia Etapa e Edital, levando ao trabalho.

2. **Contraprova**: numa Etapa **sem distribuição**, confira que o sinal é o `UX-003` — cobertura —
   e **não** o novo.

**Esperado**: um fato, um sinal. Se os dois dispararem pelo mesmo Edital e Etapa, a condição da
espécie nova está frouxa.

---

## 3 — Recurso, e a fronteira com o `UX-005` (`SC-198`)

1. Interponha recurso e deixe-o **aguardando julgamento**, com ao menos um membro **não impedido**.

**Esperado**: sinal novo, levando aos recursos daquele Edital.

2. **Contraprova, e é a que importa**: torne **todos** os membros impedidos para aquela peça.

**Esperado**: o sinal novo **some** e o `UX-005` aparece — nunca os dois. Se ambos aparecerem, os
dois cálculos se separaram, que é exatamente o que o contrato proíbe.

---

## 4 — Recorte e ato (`SC-198`)

1. Emita a ordem de um recorte e **não apure** a ocupação.

**Esperado**: sinal levando à ocupação daquele recorte.

2. Emita um ato de ordenação e **não o divulgue**.

**Esperado**: sinal levando à publicação daquele resultado.

> **Se a `037` ainda não entrou**, o passo 2 não é percorrível: a derivação vive em
> `interface/views.py` e a extração espera a feature anterior. **Registre, não contorne** — é a
> `FR-567`, e a `034` criou o precedente. *Nesse caso a `SC-198` é conferida contra **três**
> espécies, e não quatro: ela mede o entregue contra o decidido.*

---

## 5 — O que não pode ter mudado (`SC-199`, `SC-200`)

1. Leia as mensagens dos quatro sinais novos.

**Esperado**: **nenhuma nomeia pessoa**. Dizem o que está parado e onde se resolve (`FR-564`).

2. Conte as espécies que o produto apresenta e as que o requisito nomeia.

**Esperado**: **o mesmo número**. Hoje são seis no código e cinco no requisito, e é a `FR-565` que
fecha essa distância.

3. Rode o orçamento de consulta dos sinais.

**Esperado**: as três espécies de leitura existente **não acrescentam consulta**; a quarta acrescenta
**uma**, e o orçamento é remedido com o número novo escrito. *Esta é a guarda que a feature mais
facilmente quebra.*

4. Confira que as **seis** espécies antigas continuam disparando como antes.
