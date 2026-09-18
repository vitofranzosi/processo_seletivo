# Quickstart — validação da `034` · Ordem por recorte em marco computado

Quatro cenários. **Os três primeiros são pela interface administrativa, sem shell e sem banco** — é
o que o Princípio VI cobra, e é o que pegou, na `032` e na `033`, defeitos que teste nenhum pegou.

## Preparação

```bash
cd backend && uv sync --extra dev && make preparar
```

Confira que a saída termina em `N de M` com **N diferente de zero** — a segunda passada é a que
concede privilégio sobre as tabelas append-only criadas pelas migrations.

O `runserver` precisa de `INTERFACE_SELETOR_IDENTIDADE=true`, ou `/gestao/` devolve 503.

> **O `seed_demo` não monta este certame.** O cenário abaixo se monta à mão pela interface, como o
> manual faz. É mais lento e é o ponto: o percurso é o que se está validando.

**O Edital do cenário**: um Perfil, Quadro de Vagas **7 / 1 / 2** — sete na linha geral, uma para
PcD, duas para PPI —, as duas Modalidades reservadas com fundamento legal declarado, uma Etapa
pontuada e um marco classificatório que **não** sorteia. Inscrições: pelo menos duas sem
autodeclaração, uma em PcD e duas em PPI, com pontuações distintas.

---

## Cenário 1 — a ordem do recorte reservado passa a existir (`FR-490`, `FR-492`)

1. Publique o Edital, receba as inscrições, avalie e consolide a Etapa.
2. Abra a tela do marco.

**Esperado**: a tela nomeia **três** recortes — ampla concorrência, PcD e PPI —, e diz em qual se
está.

3. Emita a ordem da ampla concorrência.

**Esperado**: a ordem traz **todos** os inscritos, inclusive os autodeclarados. Esta é a contraprova
do `D-001`: se os autodeclarados não estiverem aqui, a decisão foi implementada ao contrário.

4. Vá ao recorte PPI **pelo caminho oferecido na página** — o endereço lido do `href`, sem digitar
   nada — e emita a ordem dele.

**Esperado**: nasce um ato **daquele recorte**, com as duas autodeclaradas de PPI e ninguém mais. A
ordem da ampla continua vigente e **inalterada** — confira o identificador do ato dela antes e
depois.

5. Volte ao recorte da ampla.

**Esperado**: a ordem que estava lá, intacta. Nenhum aviso de obsolescência.

### Contraprova — o Edital sem reserva não muda (`FR-493`)

Num Edital com Perfil **sem** Modalidade reservada, a tela do marco MUST continuar como sempre foi:
uma ordem, sem escolha de recorte, sem navegação nova.

---

## Cenário 2 — a cauda inteira, do corte à convocação (`SC-169`)

Continuando no mesmo Edital, e **sempre pelo caminho que a página oferece**:

1. No recorte PPI, abra o corte e emita a faixa.
2. Abra a ocupação.

**Esperado**: o recorte PPI oferece **Apurar a ocupação deste recorte**, e a ação conclui. Onde antes
se lia *"A apuração deste recorte acontece fora do sistema"*, agora há o botão — e ele funciona
(`FR-502`, `SC-170`).

3. Apure, e convoque.

**Esperado**: a convocação alcança quem está na faixa daquele recorte.

4. Repita para PcD.

**Esperado**: o mesmo, com o número da linha própria de PcD — **1**, e não 7.

**Este cenário é o `SC-169` inteiro.** Ele é o cenário 4 da reauditoria de 16/09, que parou na
convocação. Se qualquer passo exigir shell, banco ou endereço digitado, o critério **não** fechou.

---

## Cenário 3 — o produto para de avisar sobre o que resolveu (`FR-501`, `SC-174`)

1. Componha um Edital novo, igual ao do cenário 1, e abra a **Revisão** antes de publicar.

**Esperado**: o aviso da reserva sem via de apuração **não aparece**.

2. No mesmo Edital, declare um marco que **sorteia** e confira a Revisão de novo.

**Esperado**: continua sem o aviso — o sorteio sempre teve via. É a contraprova de que o predicado
não foi invertido.

3. Abra o Edital **69/2026** do acervo, ou qualquer um sem reserva.

**Esperado**: nada mudou para ele.

---

## Cenário 4 — o acervo não se mexeu (`FR-504`, `SC-173`)

Este precisa do banco, e é o único que precisa.

1. **Antes** de qualquer mudança, exporte o estado do acervo: para cada publicação, o
   `content_hash`, o resumo do conteúdo canônico e os bytes do documento.
2. Ao fim da implementação, exporte de novo.

**Esperado**: os dois arquivos **idênticos**. Mesmo `schemaVersion`, mesmo número de publicações,
versões consolidadas e documentos, e cada um com o mesmo resumo.

**E o censo dos degraus de elevação**: nenhum degrau novo. Um degrau acrescentado por engano
reescreveria o conteúdo de toda versão consolidada do acervo de uma vez, e a contagem é o guarda.

---

## Verificação

```bash
cd backend && make lint check test-pg
```

`test-pg` e **nunca** `test` — sem o par `TEST_DB_ENGINE=postgresql` e `POSTGRES_USER` a suíte cai
para SQLite e falha por motivo que não é o diff. `lint` são **dois** passos: `ruff check` e
`ruff format --check`.

**Não edite arquivos do projeto enquanto a suíte roda** — arquivo criado ou apagado no meio dá falha
que não é do diff.

### A conferência que não é pela contagem

`research.md` lista, por nome, os **11 casos** que esta feature altera, em 4 arquivos. A conferência
é **caso a caso** contra essa lista: um teste pode manter o número de asserções e trocar o que
afirma, e a suíte fica verde do mesmo jeito. Foi assim que a `033` quase deixou passar um conjunto
aceito alargado.
