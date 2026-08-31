# Fase 1 — Como demonstrar e validar

**Feature**: 008 — Composição Institucional do Edital | **Data**: 2026-08-30

A condição de merge de cada entrega é o **documento gerado e inspecionado**, não a contagem de
testes (princípio VI da Constituição, P-006 da spec). Este guia diz como preparar o ambiente, o que
rodar, o que abrir e o que se deve ver.

---

## Pré-requisitos

Três particularidades deste ambiente, todas conhecidas e nenhuma da feature.

**PostgreSQL local precisa de `LC_ALL`, e a role padrão da máquina não existe no cluster** —
sobrescreva `DB_USER`.

**`TEST_DB_ENGINE=postgresql` é obrigatório e é o que se esquece.** `config/settings/test.py` só olha
essa variável; sem ela a suíte usa sqlite em memória **sem avisar** e pula dezenas de testes de
integridade. Nos dois casos a suíte fica verde, então o sinal é a contagem de skips.

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" uv run pytest -q
```

**A interface exige o seletor de identidade ligado**; sem a variável, `/gestao/` devolve 503:

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true DB_USER="$(whoami)" uv run python manage.py runserver 8008
```

---

## Pendência de entrada — referências visuais

A comparação é parte do critério emblemático da feature e precisa de dois documentos.

**O "antes" está versionado**: `referencias/estado-inicial-apos-007.pdf` — o que o sistema produz
hoje, depois da `007`. Duas páginas, cabeçalho em linha única sem o Ministério, seções sem número,
Perfil e Cronograma em prosa, Etapa com `caráter: …; peso: …; nota mínima: …`, `INTEGRIDADE` com
`Versão do schema: 3` no corpo e nenhum bloco de autoridade. É exatamente o conjunto de defeitos que
as cinco entregas atacam, e serve de linha de base para todo "antes e depois".

**O "alvo" falta**: ao menos um Edital oficial do Cefor, versionado no mesmo diretório. **É a
primeira tarefa da entrega 1 e a bloqueia** — sem alvo, R-01 a R-03 não têm contra o quê ser
conferidos. Não sendo possível versioná-lo, registrar `referencias/referencias.md` identificando-o
por fonte, número, ano e página, com a lista das características observáveis comparadas.

---

## O cenário-base

O cenário da referência versionada, `referencias/estado-inicial-apos-007.pdf`: Edital 07/2026 do
Processo `PS-DOC-2026`, dez seções, **um** Perfil com atribuições, requisitos e uma modalidade com
percentual, dois Eventos de Cronograma e duas Etapas — uma com peso e nota mínima, outra só com
caráter. É o mesmo conteúdo da fixture contratual, então o "antes e depois" é conferível a qualquer
momento.

*A `007` foi revista sobre um `documento2.pdf` com dois Perfis, e é dele que vem o defeito de
paginação que a entrega 2 corrige. Esse arquivo não está no repositório; o cenário de dois Perfis é
montado para a demonstração da entrega 2, abaixo.*

O **cenário de dois Perfis** — usado na entrega 2 — acrescenta um segundo Perfil dimensionado para
não caber no espaço restante da primeira página. É o que reproduz o defeito observado no
`documento2.pdf`.

O **cenário longo** — usado nas entregas 2 e 4 — é o cenário-base com Perfis repetidos até o
documento passar de três páginas. Ele já existe na suíte (`test_long_content_paginates_and_every_page_is_numbered`).

O **cenário incompleto** — usado na entrega 1 — é um Edital **sem Etapas de Avaliação**, para provar
que a numeração não tem lacuna (FR-011). É o único defeito da feature que o cenário-base não revela.

O **cenário extremo** — usado na entrega 2 — é um Perfil cujas atribuições passam de uma página
inteira, para provar que a cascata de FR-021 termina em alternativa exequível.

---

## Como abrir o documento

**Prévia** (entregas 1 a 4), pela interface administrativa, no detalhe do Edital em elaboração:

```text
/gestao/ → Processo → Edital → Prévia do documento
```

**Publicado** (entrega 5), no detalhe do Edital publicado, depois de escolher a autoridade
signatária no ato de publicar.

*Prévia e publicado usam o mesmo compositor (FR-041); é por isso que as quatro primeiras entregas se
demonstram sem publicar nada.*

---

## Validação por entrega

Cada entrega confere os itens da sua faixa na `### Rubrica de inspeção` da spec, e nenhum item de
faixa anterior pode ter regredido.

### Entrega 1 — Identidade institucional e numeração (US1)

**Rubrica**: R-01, R-02, R-03.

| Deve aparecer | Não pode aparecer |
|---|---|
| `MINISTÉRIO DA EDUCAÇÃO` / `INSTITUTO FEDERAL DO ESPÍRITO SANTO` / unidade, abrindo a página 1 | título de seção como primeiro texto do documento |
| `EDITAL Nº 01/2026` como maior corpo da página | descrição com corpo igual ou maior que o do título |
| `1. APRESENTAÇÃO` … `10. DISPOSIÇÕES FINAIS` | seção sem número |
| numeração contínua no **cenário incompleto** | lacuna do tipo `5.`, `7.`, `8.` |

**Também verificar**: o número não está no conteúdo homologado — abrir a edição da seção e conferir
que o texto não o contém (FR-012).

### Entrega 2 — Perfis em quadro e paginação por bloco (US2)

**Rubrica**: R-04, R-05, R-06.

| Deve aparecer | Não pode aparecer |
|---|---|
| cada Perfil delimitado por fio, separado do seguinte | Perfil como sequência de linhas `rótulo: valor` |
| identificação em disposição tabular | tabela única com todos os campos do Perfil |
| requisitos em lista; modalidades em tabela | célula preenchida onde o dado não existe |
| no cenário de dois Perfis, o segundo **inteiro** na página 2 | o segundo Perfil começando no fim da página 1 |

**Também verificar**: no cenário extremo, o documento é composto sem erro e a quebra ocorre dentro do
sub-bloco, por parágrafo (FR-021).

### Entrega 3 — Cronograma e Etapas (US3)

**Rubrica**: R-07, R-08, R-09, R-10.

| Deve aparecer | Não pode aparecer |
|---|---|
| Cronograma como grade com colunas alinhadas | Cronograma como parágrafos numerados |
| Evento pontual com término ausente | data de término inventada |
| cabeçalho de tabela repetido na continuação | cabeçalho de tabela isolado no fim da página |
| `Caráter`, `Peso`, `Nota mínima` em pares alinhados | `caráter: …; peso: …; nota mínima: …` |

**Também verificar**: a data da Etapa continua vindo do Evento vinculado, e nenhuma data foi
duplicada no domínio (FR-028).

### Entrega 4 — Tipografia, órfãos e espaçamento (US4)

**Rubrica**: R-06, R-11.

| Deve aparecer | Não pode aparecer |
|---|---|
| todo título com conteúdo abaixo de si na mesma página | título fechando página sozinho |
| espaço antes de seção > antes de bloco > antes de parágrafo | espaço vertical sem causa |
| linhas dentro da margem em todas as páginas | linha estourando a margem |

**Também verificar** no cenário longo, percorrendo **todas** as páginas.

### Entrega 5 — Autoridade e integridade discreta (US5)

**Rubrica**: R-12, R-13, R-14.

| Deve aparecer | Não pode aparecer |
|---|---|
| nome e cargo da autoridade ao final do publicado | praça ou data no bloco de autoridade |
| bloco de verificação **após** a autoridade, em corpo de nota | `Versão do schema` como seção do Edital |
| SHA-256 completo no bloco; abreviado no rodapé | UUID em qualquer lugar do corpo |
| prévia **sem** autoridade e **sem** integridade | prévia que pareça publicada |

**Também verificar**: publicar uma Retificação e conferir que o documento consolidado tem a mesma
composição e a autoridade da própria Publicação da Retificação (FR-043).

---

## Regeneração da fixture

Toda entrega que muda a composição regenera a fixture contratual **no mesmo commit**, com o diff
revisado (FR-044):

```bash
cd backend && uv run python scripts/gerar_fixture_documento.py
```

A partir da entrega 5 o gerador exige a autoridade fixa versionada em
`tests/contract/fixtures/autoridade_publicada.json` — sem ela, compor em modo publicado é recusado
(D-005, D-009).

**Regenerar para fazer um teste passar continua sendo erro.** A fixture existe para acusar mudança
não intencional; refazê-la sem mudança intencional apaga exatamente o que ela guarda.

---

## Suíte

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" uv run pytest -q
cd backend && uv run ruff check .
```

Os testes que afirmam **invariante** — determinismo, acentuação, ausência de UUID, suficiência do
snapshot para o corpo normativo, prévia sem integridade, parágrafos preservados — não podem falhar em
nenhuma entrega. Os que afirmam **forma da apresentação** são atualizados junto da entrega que os
torna falsos, nunca antes e nunca depois (D-010).
