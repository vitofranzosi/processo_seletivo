# Quickstart — Publicação de Resultados

O roteiro que demonstra o gate da spec, inteiro pelo navegador, alternando atores. Ele não é teste
automatizado: é o percurso que a suíte de aceitação reproduz e que a auditoria exploratória repete à
mão.

## Pré-requisitos

O estado que a 015 já sabe produzir — e que `seed_demo` monta:

- Edital publicado, com Perfil, marco classificatório e critérios de desempate;
- inscrições submetidas, avaliadas e consolidadas;
- **um `AtoDeOrdenacao` emitido e vigente** para o marco.

Atores: `paula.publicadora` (papel Publicador, agora com `resultado:publicar`),
`paulo.presidente` (presidência da comissão, que emitiu o ato), `aurora.auditora`, e uma candidata
com inscrição no universo do ato.

```bash
cd backend && uv run python manage.py seed_demo
```

```bash
cd backend && uv run python manage.py runserver
```

> A interface administrativa exige o seletor de identidade ligado; sem ele, `/gestao/` devolve 503.

## 1 — A autoridade encontra a ação

Como **paula.publicadora**, abrir o ato de ordenação do marco. O cartão de ações oferece **Publicar
resultado**.

Como **paulo.presidente**, abrir o mesmo ato: a ação **não** aparece — emitir não concede publicar
(FR-026, SC-014).

## 2 — A prévia

Abrir **Publicar resultado**. A tela mostra título, Processo e Edital, marco, natureza a escolher,
autoridade signatária a escolher, e a lista exata que será divulgada. Nada foi gravado (FR-035).

Conferir na lista: posições compartilhadas aparecem como tais (1º, 2º, 3º, 3º), os nomes são de
gente e não identificadores, e **nenhum valor de desempate** aparece — nem data de nascimento, nem
meses de experiência (FR-020, SC-015).

## 3 — Publicar

Escolher **Resultado preliminar** e a autoridade; confirmar. Nasce a publicação, com autor,
instante e signatário (SC-003).

**Duplo submit**: reenviar o mesmo formulário devolve a mesma publicação, e o histórico do marco
lista **uma** (SC-013). Em duas abas, com chaves de idempotência diferentes, a segunda é recusada
pela unicidade `(ato, natureza)` — que é o caso que a idempotência sozinha não pega (SC-021).

## 4 — A página pública

Sair da sessão administrativa e abrir o endereço da publicação. Sem autenticação, a página mostra o
resultado, diz "Resultado preliminar" em texto, informa quando foi publicado e quem assinou
(SC-007, SC-019).

Voltar à vitrine, abrir o Edital: o resultado publicado está listado ali, e é assim que quem não
tem o endereço chega a ele (SC-018).

A 375 px, `document.documentElement.scrollWidth === 375` (SC-016).

## 5 — A candidata

Entrar como a candidata e abrir **Minhas inscrições** → a inscrição → acompanhamento.

Aparece a natureza, a posição e a pontuação, com o caminho para o resultado completo (SC-009).

> **Antes do passo 3 essa informação não existia na tela** — e é o que a suíte afirma pela ordem
> inversa: o mesmo acompanhamento, antes de publicar, não menciona resultado algum (SC-008).

Para uma candidata considerada e sem posição: a própria situação e o motivo aparecem, e o nome dela
**não** está na lista pública (SC-020).

## 6 — O documento

Baixar o documento pela página pública. Ele traz Edital, marco, natureza, ato de origem, data e
hora, autoridade e o resumo criptográfico do conteúdo — e a lista é a mesma da página (SC-010).

## 7 — Obsolescência e sucessão

Como **gustavo.gestor**, retificar o Edital alterando o peso de uma Etapa do marco e publicar a
Retificação.

Como **paula.publicadora**, tentar publicar o **mesmo** ato de novo: recusado, com a razão nomeada e
o caminho — emitir o ato sucessor (SC-012).

Como **paulo.presidente**, emitir o ato sucessor na tela da 015. Como **paula.publicadora**,
publicá-lo como **Resultado definitivo**.

> **O caminho sem recurso também vale**: não havendo ato sucessor a emitir — ninguém contestou, ou
> os recursos não mudaram a ordem —, o **mesmo** ato é publicado como definitivo, e a P2 sucede a P1
> sem que a 015 registre uma sucessão que não sucedeu nada (FR-039, SC-021).

Abrir o endereço de **P1**: ela continua exatamente como era, e diz que foi sucedida, com o caminho
para a vigente (SC-005, SC-006, SC-011).

Como **aurora.auditora**, abrir o histórico do marco: as duas publicações, com natureza, instante,
autor e situação (SC-017).

## O gate

```text
classificação emitida → prévia → publicação → página pública
                      → candidata vê na própria Inscrição → documento
                      → P1 permanece histórica quando sucedida
```

## Suíte

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER=$USER DB_NAME=test_017 uv run pytest -q
```

> As constraints de cadeia sob concorrência e as duas triggers append-only **só** são exercidas
> contra PostgreSQL; sem `TEST_DB_ENGINE=postgresql` a suíte cai para sqlite e as pula em silêncio.
> `DB_NAME` próprio evita disputa com outra worktree.
