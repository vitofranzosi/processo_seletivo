# Implementation Plan: Quadro de Vagas por Modalidade

**Branch**: `claude/speckit-plan-025-a11ba8` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

> **A spec veio de outro branch.** Ela nasceu em `claude/quadro-vagas-modalidade-7b10d4` e, quando
> este plano foi escrito, ainda vivia no PR #99 e não na `main` — foi preciso trazê-la por merge
> para que o plano ficasse ao lado dela. Os dois branches convergem quando o #99 entrar.

**Input**: Feature specification from `specs/025-quadro-de-vagas-por-modalidade/spec.md`

---

## Summary

O Perfil de Vaga passa a declarar **quantas vagas cabem em cada recorte** — uma linha geral, que é a
ampla concorrência, e uma linha por Modalidade de Concorrência —, e essas quantidades viajam no
conteúdo publicado, aparecem no documento e são alcançáveis por Retificação **linha a linha**.

**A abordagem técnica cabe numa frase: é mais uma coleção do Perfil, e o repositório já tem cinco.**
`competitionModalities`, `declaredFacts`, `classificationMilestones`, `tiebreakers` e
`documentRequirements` percorreram exatamente este caminho — modelo, emissão, declaração de
endereçamento, degrau de schema, catálogo de Retificação, documento. Nenhuma forma nova é inventada.

Isso decide o formato do plano: **uma entidade, uma migration, um degrau de schema (11 → 12), duas
declarações em catálogos existentes, e nenhum módulo novo.** O risco não está na engenharia; está em
**esquecer uma das travessias**, e é por isso que a §*Ordem de execução* nomeia as quatro que matam
em silêncio.

Uma coisa o plano **encontrou e resolveu pela metade**: a igualdade da `FR-161` não roda no formato
de Edital mais comum, por interação com a `D-004`. A `FR-177` fecha a direção perigosa — soma que
**excede** o total é recusada em qualquer quadro —, e o que resta aberto é o quadro que soma menos do
que o total nesse formato. Está em [research.md](research.md), `R-006`, com as duas saídas que
fechariam o resto e o custo de cada uma. É achado; a escolha é do usuário.

---

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2, Django REST Framework 3.16. **Nenhuma dependência nova**

**Storage**: PostgreSQL 16. **Uma** migration — `editais/migrations/0016_quadro_de_vagas.py` — que
cria uma tabela e duas constraints parciais. Não altera coluna existente, não remove nada, não toca
em dado normativo

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg`). Unidade em
`tests/unit/editais/` e `tests/unit/publicacoes/`; contrato em `tests/contract/`, com
`test_elevacao_degrau_12.py` na convenção estrita de nome; interface em `tests/interface/`;
aceitação em `tests/acceptance/`

**Target Platform**: servidor web; interface administrativa server-side com htmx, sem SPA e sem build
de front

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**: o maior caso do alvo é 7 Perfis × 4 linhas. A emissão do snapshot já faz
`prefetch_related` sobre as coleções do Perfil; o quadro entra no mesmo e **não acrescenta consulta
por Perfil**

**Constraints**: nenhuma quantidade derivada de percentual (`FR-157`); nenhum valor publicado
reescrito (`FR-173`, `FR-174`); endereçamento sempre por identidade, nunca por posição (`FR-170`);
conteúdo publicado antes do degrau lido com coleção **vazia**, nunca com zero (`FR-167`, `D-005`)

**Scale/Scope**: uma entidade nova; ~18 arquivos de produção tocados; quatro entregas demonstráveis

**Nenhum NEEDS CLARIFICATION.** As quatorze questões técnicas estão resolvidas em
[research.md](research.md). Os dois nomes que a `D-010` delegou ao plano ficam fixados na `R-001`.

---

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado depois da Fase 1. Ambas as passadas: aprovado.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | `vacancyTable` é o termo que os Editais imprimem, e `modalityId` é o nome que `documentRequirements` já usa para a mesma referência. A `R-011` **encontrou uma colisão** — `_quadro_de_vagas` já existia no gerador do PDF significando outra coisa — e a desfaz renomeando aquela função para `_quadro_de_perfis`, que é o que ela faz | ✅ |
| **II — Integridade normativa e imutabilidade** | A quantidade publicada é fonte única e autoritativa (`D-003`); o percentual fundamenta e não calcula (`FR-157`). Nada publicado é reescrito: a Retificação materializa versão nova, e o degrau 12 converte **para leitura** sem tocar em byte gravado. `FR-174` proíbe depreciar campo algum da Regra Normativa | ✅ |
| **III — Segurança e proteção de dados** | Nenhuma permissão nova e nenhum ator novo: `edital:elaborar` para compor, `edital:publicar` para publicar, e a segregação de funções continua valendo. Nenhum dado pessoal — o quadro é contagem de vagas, e a `FR-175` proíbe atribuir pessoa a linha | ✅ |
| **IV — Regras explícitas e consistência** | Toda regra vive no domínio, e não no serializer — pela razão que `editais/domain/perfis.py:29-31` já registra: a interface invoca o command diretamente. A conferência da soma e as recusas de referência são achados classificados pela operação de publicar, que é o mecanismo que o próprio princípio exige | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | Cada FR tem cenário no [quickstart.md](quickstart.md). A simplicidade é o eixo: **zero módulo novo, zero mecanismo novo** — a `R-007` descobriu que o ponto de verificação que a `FR-172` precisa já existe e é chamado em três lugares. A divergência que a `R-006` encontrou foi **resolvida explicitamente**, e não herdada: a `FR-177` fecha a direção perigosa, e o que resta aberto está nomeado com o custo | ✅ |
| **VI — Completude de jornada** | É o princípio que **motiva** a feature: há Editais reais que o sistema conduz até a ordem do sorteio e não consegue publicar. O cenário demonstrável é o percurso do [quickstart.md](quickstart.md), conduzido pela interface administrativa — o canal do ator que elabora —, sem shell e sem banco | ✅ |

### Invariantes do domínio tocados

| Invariante da Constituição | Efeito |
|---|---|
| "Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar modalidade, fundamento, percentual…" | a feature acrescenta a **quantidade**, que faltava, sem tocar nos demais. "Mudança futura NÃO PODE alterar Edital publicado" é o que o degrau 12 e a `FR-173` garantem |
| "Registros normativos NÃO DEVEM ser fisicamente excluídos" | nada é excluído. A `D-008` recusa até a cascata que apagaria linha como efeito colateral |
| "O PDF DEVE derivar dos dados estruturados… A cadeia deve ser demonstrável" | o quadro é composto a partir do snapshot homologado, como todo o resto do documento |
| "Mudanças persistentes DEVEM usar migrations versionadas; migrations aplicadas NÃO PODEM ser reescritas" | uma migration nova, aditiva |
| "APIs DEVEM ter contratos explícitos" | `openapi.yaml` acompanha em dois lugares — o rascunho e o publicado —, detalhado em [contracts/quadro-de-vagas.md](contracts/quadro-de-vagas.md) |
| "Entidades DEVEM possuir identificadores estáveis" | a linha nasce com UUID preservado entre gravações, como Perfil, Modalidade e Etapa |

**Sem violações. A tabela de Complexity Tracking fica vazia**, e é a conclusão certa: uma feature que
acrescenta uma tabela e uma entrada em dois dicionários não tem complexidade a justificar.

---

## Project Structure

### Documentation (this feature)

```text
specs/025-quadro-de-vagas-por-modalidade/
├── plan.md              # este arquivo
├── spec.md              # a especificação
├── research.md          # R-001 a R-014, todas resolvidas
├── data-model.md        # a entidade nova, o degrau, os invariantes
├── quickstart.md        # os quatro percursos, contra o servidor real
├── contracts/
│   └── quadro-de-vagas.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/perfis.py                    # NOVO modelo LinhaDoQuadroDeVagas
│   ├── migrations/0016_quadro_de_vagas.py  # NOVO — tabela + duas constraints parciais
│   ├── domain/perfis.py                    # validação da linha e da referência cruzada (FR-154..FR-158)
│   ├── domain/validation.py                # Campo("vacancyTable") em PERFIL_PUBLICADO;
│   │                                       #   findings: soma, referência pendurada, advertência
│   ├── domain/reaproveitamento.py          # os DOIS passos: registrar o id, trocar o modalityId
│   ├── api/serializers.py                  # VacancyTableRowSerializer + campo em ProfileSerializer
│   └── application/draft.py                # criação da linha + identidade aninhada alheia
├── publicacoes/
│   ├── application/publish_edital.py       # emissão de vacancyTable no dicionário do Perfil
│   ├── domain/elevacao.py                  # DEGRAUS_DE_PERFIL[12] = {"vacancyTable": []}
│   ├── domain/colecoes.py                  # "/profiles/*/vacancyTable" em COLECOES_COM_CHAVE
│   └── infrastructure/pdf.py               # bloco do quadro; RENOMEIA _quadro_de_vagas → _quadro_de_perfis
├── interface/
│   ├── forms.py                            # ler + persistir + reexibir as linhas (as três travessias)
│   ├── views.py                            # fragmento htmx da linha
│   ├── retificacao.py                      # CAMPOS_DA_LINHA + "vacancyTable": [] no NOVO_PERFIL
│   ├── revisao.py                          # o quadro na tela de conferência
│   └── templates/interface/
│       ├── _perfil.html                    # a seção do quadro dentro do cartão
│       └── _linha_do_quadro.html           # NOVO — a linha, reusada como fragmento
└── shared/canonical.py                     # SCHEMA_VERSION 11 → 12, com o degrau narrado

specs/001-processo-seletivo-editais/contracts/openapi.yaml   # PerfilInput e PerfilPublicado

backend/tests/
├── contract/
│   ├── test_elevacao_degrau_12.py          # NOVO — convenção estrita de nome
│   ├── test_forma_publicada.py             # ampliado
│   └── test_documento_publicado.py         # fixture de bytes regenerada de propósito
├── unit/editais/
│   ├── test_quadro_de_vagas.py             # NOVO — linha geral única, referência, soma
│   └── test_forma_do_snapshot.py           # ampliado
├── unit/publicacoes/test_colecoes.py       # ampliado — a coleção é declarada
├── integration/publicacoes/
│   └── test_quadro_na_retificacao.py       # NOVO — remoção recusada, alteração por identidade
├── interface/
│   ├── test_compor_quadro.py               # NOVO — a seção, as recusas, a advertência
│   └── test_round_trip_do_rascunho.py      # ampliado — o teste que a seção nova TEM de satisfazer
└── acceptance/test_us2_perfis.py           # ampliado — o ciclo do 57/2026
```

**Structure Decision**: o monólito Django existente, sem projeto novo, sem camada nova e **sem
módulo novo**. A entidade mora em `editais`, junto das demais coleções do Perfil; o degrau mora em
`publicacoes`, junto dos onze anteriores. A direção de dependência não muda.

`sorteios/` **não é tocado**. A `§7` da spec põe fora de escopo reconciliar as duas grafias da ampla
concorrência, e o ato de ordenação não é reescrito por esta feature.

---

## Ordem de execução

A da §8 da spec, e cada etapa é demonstrável sozinha:

| # | Entrega | US | Depende de | O que carrega o risco |
|---|---|---|---|---|
| 1 | Declaração e integridade na elaboração | `US1` | `R-002`, `R-008`, `R-009` | as quatro travessias do rascunho |
| 2 | Publicação, degrau 12 e documento | `US2` | `R-004`, `R-005`, `R-011` | a colisão de nome no PDF; a fixture de bytes |
| 3 | Retificação por identidade | `US3` | `R-005`, `R-007`, `R-014` | copiar o precedente errado |
| 4 | Composição sem digitação supérflua | `US4` | `R-009` | — |

A **1** é a que entrega a lacuna; a **3** é a que concentra o risco de projeto; a **2** é a que
concentra o risco de regressão. A **4** depende só da 1, e a **3** depende da 2.

### Declarar a coleção antes de emiti-la

`"/profiles/*/vacancyTable"` entra em `COLECOES_COM_CHAVE` na etapa **2**, **antes** de o snapshot a
emitir. Não é ordem arbitrária: é a razão que a `015` registrou na `T-007` e que `colecoes.py:25-30`
guarda por escrito. Emitir primeiro deixaria o primeiro Edital publicado com quadro **sem endereço
de retificação**, e endereço de retificação não se conserta depois.

### As quatro travessias que matam em silêncio

`replace_draft` **apaga e recria tudo**: `PerfilVaga.objects.filter(...).delete()` e recriação a
partir do que recebeu. Uma coleção do Perfil que falte em qualquer uma das quatro some na gravação
da etapa **seguinte**, sem erro:

1. `interface/forms.py:338` — `ler_perfis`, que lê o formulário;
2. `interface/forms.py:598` — `perfis_persistidos`, que **reenvia** ao gravar outra etapa;
3. `interface/forms.py:543` — `perfis_do_edital`, que reexibe;
4. `editais/application/draft.py:218` — a recriação, preservando o `id` recebido.

`tests/interface/test_round_trip_do_rascunho.py` existe exatamente para pegar isso — compara a
coleção **inteira** depois de gravar outra etapa, e nasceu do `E2E17-001`. Ampliá-lo é parte da
etapa 1, não da verificação final.

### Três armadilhas nomeadas

1. **O precedente mais próximo da `FR-172` é o que a `D-008` recusa.** Ao remover um Anexo, a tela de
   Retificação **emite automaticamente** o `REPLACE …/attachmentId → None` que desfaz o vínculo
   (`interface/retificacao.py:920-966`). É o padrão que se copiaria sem pensar. Aqui está proibido:
   lá a emissão automática desfaz um vínculo; aqui **apagaria uma quantidade publicada** como efeito
   colateral de outro movimento — a alternativa que a `D-008` recusou por escrito. A resposta certa é
   **recusar**, nomeando a linha.

2. **O nome `_quadro_de_vagas` já existe no PDF, e é outra coisa** (`pdf.py:1332`: a tabela
   comparativa de Perfis). A etapa 2 o renomeia para `_quadro_de_perfis` **antes** de escrever o
   bloco novo. É função privada e o PDF sai byte a byte idêntico — o que
   `tests/contract/test_documento_publicado.py:136` prova de graça.

3. **O reaproveitamento entre Editais tem dois passos, e o segundo é o que quebra calado.**
   `reaproveitamento.py` precisa registrar o `id` da linha **e** trocar o `modalityId` dela. Sem o
   segundo, a linha copiada aponta a Modalidade do Edital **anterior**, e nada acusa.

### O que a etapa 2 obriga a regenerar

Mudar a composição do documento obriga a regenerar a fixture de bytes por
`backend/scripts/gerar_fixture_documento.py`, e **só na mesma tarefa que muda a composição de
propósito** — é a regra que `test_documento_publicado.py` impõe, e ela existe porque a asserção de
bytes é o que impede a mudança acidental de documento publicado.

---

## O que este plano deliberadamente não faz

- **Não deprecia nada da `RegraNormativa`** (`D-003`, `FR-174`). `percentage`, `calculation`,
  `rounding` e `distribution` seguem publicados e intactos.
- **Não reparte cadastro de reserva** (`D-011`), e **não prepara o campo** para isso. Admitir a
  segunda quantidade antes de existir regra que a consuma é construir a estrutura antes do uso — o
  que o próprio repositório recusou ao modelar os campos descritivos do Perfil.
- **Não identifica mecanicamente a Modalidade de ampla concorrência** (`R-006`). Fazê-lo seria
  decidir, no plano, a reconciliação das duas grafias que a §7 da spec declarou fora de escopo.
- **Não publica a ordem da linha** (`R-003`), e por isso a Retificação não reordena o quadro. A
  `FR-171` pede acrescentar, alterar e remover, e é o que ela ganha.
- **Não ocupa vaga, não convoca e não corta** (`FR-175`). É o corte que a spec repete duas vezes, e é
  o mais tentador de violar.

---

## Complexity Tracking

> Preenchido apenas quando o Constitution Check tem violação a justificar.

**Vazio.** Nenhuma violação: uma entidade nova numa app existente, uma migration aditiva, um degrau
na cadeia que já tem onze, e duas linhas em catálogos declarativos. Nenhum serviço, nenhuma
dependência, nenhum padrão novo.
