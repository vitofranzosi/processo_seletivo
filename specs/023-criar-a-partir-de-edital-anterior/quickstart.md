# Quickstart — Criar Edital a partir de Edital anterior

Como exercitar e conferir a feature. Os cenários são a prova de `US1`–`US3` e a contraprova dos
`SC`; a tabela do fim liga cada `FR` ao cenário que o observa.

## Preparação

```bash
cd backend && make lint check test-pg
```

`test-pg` e não `test`: sem o par `TEST_DB_ENGINE=postgresql` e `DB_USER` a suíte cai para SQLite e
mente. Havendo mais de uma worktree ativa, passe um `DB_NAME` próprio — suítes paralelas disputam o
mesmo banco de teste e se derrubam.

Para a jornada pelo navegador:

```bash
cd backend && make preparar && make seed && make runserver
```

O seletor de identidade precisa estar ligado (`INTERFACE_SELETOR_IDENTIDADE=true`), ou `/gestao/`
devolve `503`. `make seed` deixa um Edital publicado a servir de origem; para o cenário 8, publique
**uma Retificação** sobre ele antes de copiar.

**Os papéis importam, e são dois.** Quem cria o Processo é o **Gestor** (`processo:criar`); quem
escolhe a origem é o **Elaborador** (`edital:elaborar`). Fazer os dois passos com a mesma identidade
esconde justamente a decisão que `D-001` tomou.

---

## Cenário 1 — A jornada, do começo ao fim (`US1`)

1. Como Gestor, crie o Processo e o primeiro Edital, com número e ano da nova oferta.
2. Troque para o Elaborador e abra a composição desse Edital.
3. Na primeira etapa, escolha *partir de um Edital anterior* e selecione um Edital publicado.
4. Percorra as etapas: Perfis, Cronograma, Etapas, Classificação, Inscrição, Anexos e Conteúdo.

**Esperado**: cada etapa traz a configuração da origem, editável pelos controles de sempre. Nenhuma
tela nova além da escolha da origem. O Edital continua **em elaboração**.

## Cenário 2 — A origem não se mexe (`SC-004`)

Antes de copiar, anote da origem: situação, revisão e o resumo criptográfico da versão vigente.
Depois de copiar, confira os três.

**Esperado**: idênticos. Nenhuma escrita atingiu a origem.

## Cenário 3 — O certame anterior não veio junto (`US2`, `SC-006`)

Use como origem um Edital **com execução**: inscrições recebidas, avaliações, resultado divulgado e
recurso julgado. Depois de copiar, abra no Edital novo as telas de inscrições, distribuição,
resultados e recursos.

**Esperado**: zero em todas. E a comissão do Processo de destino é a que aquele Processo já tinha —
não a da origem.

## Cenário 4 — As quatro referências que a gravação não confere (`FR-010a`, `SC-003`)

O cenário mais importante, e o que precisa de origem preparada: ela tem de **usar** as quatro.

| Referência | Como observar no destino |
|---|---|
| Documento Exigido → Anexo | baixe o modelo pelo requisito: é o artefato **do destino** |
| marco → Etapas que enumera | as Etapas somadas pelo marco são as do destino |
| critério → Etapa e → fato | o critério de desempate aponta Etapa e fato do destino |
| método do sorteio → Etapa de habilitação | a Etapa de habilitação é a do destino |

**Esperado**: nenhuma delas alcança objeto da origem. **Contraprova**: com o remapeamento desligado
para qualquer uma das quatro, a gravação **passa** — é por isso que cada uma tem teste próprio, e não
uma verificação genérica.

## Cenário 5 — O calendário não vem cumprido (`FR-008a`)

Use origem cujos Eventos estejam `CONCLUIDO` ou `CANCELADO`.

**Esperado**: no destino, todos `PLANEJADO`. A designação do período de inscrições, essa sim,
acompanha.

## Cenário 6 — O que não tem tela não veio (`FR-008`)

Use origem com `maxInscricoesPorCandidato`, `classificationInformation` ou `callInformation`
preenchidos — hoje só a API os escreve.

**Esperado**: o destino não os tem, e a prévia mostra a ausência. Nenhum deles chega ao documento do
novo Edital.

## Cenário 7 — Rascunho não vazio (`FR-002`)

Componha qualquer coisa no Edital de destino — um Perfil basta — e procure a opção de partir de outro
Edital.

**Esperado**: a opção não aparece. Forçando a operação, o sistema recusa nomeando o que já existe, e
**nada do que estava lá é apagado**.

## Cenário 8 — Origem retificada (`SC-008`, `D-003`)

Publique uma Retificação na origem que altere uma data e uma quantidade de vagas. Depois copie.

**Esperado**: o destino nasce com os valores **retificados**. Este é o cenário que separa ler a versão
vigente de ler o estado relacional, e é o que mais silenciosamente falharia se a fonte estivesse
errada.

**Variante, no mesmo cenário**: origem cuja versão vigente está num degrau **anterior** do esquema
canônico. O destino sai completo e no esquema atual, sem declarar o que aquele degrau não declarava —
é a integração `elevar → copiar`, e não só a leitura.

## Cenário 9 — Origem inelegível (`FR-004`, `T-007`)

Tente como origem: um Edital de outro escopo, um Edital em elaboração e um Edital cancelado.

**Esperado**: os três respondem igual — `404` indistinguível. A lista de escolha não os oferece.

**E o outro lado da fronteira**, que é metade do cenário: origem `PUBLICADO` **e** origem `ENCERRADO`
são aceitas, e a lista oferece as duas.

## Cenário 10 — Duas submissões (`FR-017`)

Envie a operação duas vezes com a mesma chave.

**Esperado**: uma cópia só. Nenhum Anexo duplicado, nenhuma coleção em dobro, e **o mesmo Edital de
volta — não uma recusa de rascunho não vazio**. Depois da primeira cópia o rascunho deixou de estar
vazio; é por isso que a repetição é reconhecida antes das precondições (`FR-017a`).

## Cenário 11 — A origem fica dita (`US3`, `SC-005`)

Abra a composição do Edital novo e depois a trilha dele. Publique-o e volte à trilha.

**Esperado**: o aviso nomeia a origem e pede a atualização; a trilha registra a **versão** de onde o
conteúdo saiu, o ator e o instante; e o registro continua lá depois da publicação.

**E a trilha é legível**: a entrada diz *a partir do Edital 173/2025, versão de <data>* — **não um
identificador cru**. O aviso desaparece quando o Edital sai da elaboração; a trilha é o que sobra, e
é por ela que `US3` se verifica depois de publicado (`FR-014a`). **Some ao
cenário 8**: retifique a origem depois da cópia e volte à trilha — ela continua dizendo de qual
versão se partiu, que é o que a Constituição pede ao exigir *independência e versão*.

## Cenário 12 — Independência (`FR-018`)

Altere o destino; confira a origem. Publique uma Retificação na origem; confira o destino.

**Esperado**: nenhum dos dois alcança o outro.

## Cenário 13 — A régua de tamanho (`SC-007`)

```bash
cd backend && uv run python manage.py makemigrations --check --dry-run
```

**Esperado**: limpo. E na revisão do diff: nenhum modelo novo, nenhuma entrada nova em `PAPEIS`,
nenhum achado impeditivo novo em `validate_for_publication`.

---

## Cobertura

| Requisito | Cenário |
|---|---|
| FR-001, FR-003 | 1 |
| FR-002 | 7 |
| FR-004 | 1, 9 |
| FR-005 | 8 |
| FR-006 | 1 |
| FR-007 | 1 (número e ano são os que se digitou) |
| FR-008 | 6 |
| FR-008a | 5 |
| FR-009, FR-010, FR-010a | 4 |
| FR-011 | 4 (o modelo baixado é o do destino) |
| FR-012 | 2 |
| FR-013 | 3 |
| FR-014, FR-015, FR-015a | 11 |
| FR-016 | 11 (a origem não aparece no documento publicado) |
| FR-017 | 10 |
| FR-018 | 12 |
| FR-019 | 7, 9 |
| FR-020 | 1 |
| SC-001 | 1 |
| SC-002, SC-003 | 4 |
| SC-004 | 2 |
| SC-005 | 11 |
| SC-006 | 3 |
| SC-007 | 13 |
| SC-008 | 8 |
