# Modelo de dados — 025 · Quadro de Vagas por Modalidade

Fase 1. **Uma entidade nova**, um degrau de schema, e nenhuma entidade existente alterada.

O tamanho desta página é o argumento do plano: a `D-002` escolheu uma coleção normativa própria do
Perfil, e coleção própria do Perfil é uma forma que este repositório já tem cinco vezes —
`competitionModalities`, `declaredFacts`, `classificationMilestones`, `tiebreakers`,
`documentRequirements`. Nada aqui é forma nova.

---

## Entidade nova

### `LinhaDoQuadroDeVagas`

Em `backend/processo_seletivo/editais/models/perfis.py`, ao lado de `ModalidadeConcorrencia` e
`FatoDeclarado`.

Uma quantidade de vagas imediatas com identidade própria. **Sem** referência a Modalidade, é a
**linha geral** — a da ampla concorrência; **com** referência, é **linha reservada** (`D-002`).

| Campo | Tipo | Notas |
|---|---|---|
| `id` | `UUIDField` PK, `default=uuid4` | identidade estável e publicada; é por ela que a Retificação alcança a linha (`FR-170`) |
| `perfil` | FK `PerfilVaga`, `CASCADE`, `related_name="quadro_de_vagas"` | a linha é do Perfil, e some com ele |
| `modalidade` | FK `ModalidadeConcorrencia`, **`null=True`**, `PROTECT` | `NULL` **é** a ampla concorrência, e não ausência (`D-004`) |
| `vagas_imediatas` | `PositiveIntegerField` | inteiro absoluto ≥ 0 (`FR-156`); nunca derivado (`FR-157`) |
| `ordem` | `PositiveIntegerField` | determiniza a emissão; **não é publicada** (`R-003`) |

```python
class Meta:
    ordering = ["ordem", "id"]
    constraints = [
        UniqueConstraint(fields=["perfil", "modalidade"], name="uq_linha_por_modalidade",
                         condition=Q(modalidade__isnull=False)),
        UniqueConstraint(fields=["perfil"], name="uq_linha_geral_por_perfil",
                         condition=Q(modalidade__isnull=True)),
    ]
```

**As duas constraints não são redundantes, e uma só seria mais fraca.** No PostgreSQL dois `NULL`
não colidem: `UniqueConstraint(perfil, modalidade)` sozinha deixaria passar duas linhas gerais no
mesmo Perfil, que é exatamente o que a `FR-154` proíbe. É a mesma cirurgia de
`classificacao/models.py:86-100`, e pela mesma razão.

**`PROTECT` na Modalidade é a `D-008` escrita no banco**, para o caminho da elaboração: remover a
Modalidade não pode fazer a quantidade sumir como efeito colateral. Para o conteúdo **publicado**, a
mesma regra é um *finding* impeditivo (ver abaixo) — banco e conteúdo publicado são duas camadas
independentes, como a Constituição pede para tudo o que é normativo.

**`ordem` existe por determinismo, e não por norma.** Sem ela a emissão sairia em ordem indefinida e
dois snapshots do mesmo conteúdo teriam resumos canônicos diferentes, quebrando a `FR-168`. Ela não é
publicada porque a `D-009` diz que a ordem não carrega significado normativo próprio — publicá-la
faria o quadro afirmar uma precedência entre listas que é de outra feature.

**Migration**: `editais/migrations/0016_quadro_de_vagas.py`. Cria a tabela e as duas constraints.
**Não altera nem remove nada** — nenhum campo da `RegraNormativa` é tocado (`FR-174`).

---

## Entidades existentes: o que muda, e o que explicitamente não muda

| Entidade | Muda? |
|---|---|
| `PerfilVaga` | **não**. `immediate_vacancies` continua declarado por quem compõe e **não** passa a ser calculado (`FR-162`). Ganha só o `related_name` da linha |
| `ModalidadeConcorrencia` | **não**. Continua com `code`, `name`, `description`. Passa a ser referenciável, e a ser protegida contra remoção enquanto houver linha |
| `RegraNormativa` | **não**. `percentage`, `calculation`, `rounding`, `distribution` seguem intactos e publicados como sempre (`FR-174`, `D-003`). Nada é depreciado |
| `Inscricao`, `AtoDeOrdenacao`, `RelacaoDeHabilitados` | **não**. Esta feature declara o quadro; não ocupa, não convoca e não corta (`FR-175`) |

---

## Conteúdo publicado

### A coleção

`vacancyTable`, dentro de cada item de `profiles[]`, irmã de `competitionModalities`.

```json
"vacancyTable": [
  { "id": "…", "modalityId": null, "immediateVacancies": 56 },
  { "id": "…", "modalityId": "…-pcd", "immediateVacancies": 4 },
  { "id": "…", "modalityId": "…-ppi", "immediateVacancies": 20 }
]
```

| Chave | Tipo | Significado |
|---|---|---|
| `id` | uuid | identidade estável; endereço de retificação |
| `modalityId` | uuid \| `null` | `null` **é** a linha geral, a da ampla concorrência |
| `immediateVacancies` | inteiro ≥ 0 | a quantidade publicada; é a fonte (`D-003`) |

O emissor é `publicacoes/application/publish_edital.py`, no dicionário do Perfil
(`publish_edital.py:169-193`), depois de `competitionModalities`. A ordem de emissão é
`order_by("ordem", "id")` — determinismo, não norma.

### As duas declarações

```python
# publicacoes/domain/colecoes.py — COLECOES_COM_CHAVE
"/profiles/*/vacancyTable",

# editais/domain/validation.py — PERFIL_PUBLICADO
Campo("vacancyTable", list, tipo_do_item=dict),
```

Sem a primeira, a coleção nasce **irretificável**: a gramática recusa `id=` e sobra o endereçamento
por posição, que o sistema proíbe. Sem a segunda, os guardas de `tests/fixtures/snapshot.py:275` e
`:301` acusam coleção não declarada.

### O degrau 12

`SCHEMA_VERSION`: **11 → 12** (`shared/canonical.py:105`).

```python
DEGRAUS_DE_PERFIL = {
    7: {"classificationMilestones": [], "declaredFacts": []},
    12: {"vacancyTable": []},
}
```

Todo conteúdo publicado antes do degrau ganha a coleção **vazia**. Lista vazia diz *este Edital não
publicou quadro*, e é verdade sobre todos eles, porque a capacidade não existia (`D-005`, `FR-167`).
Nunca zero vaga.

---

## Invariantes, e onde cada um é sustentado

Os sete da §5 da spec, e a camada que responde por cada um:

| # | Invariante | Onde é sustentado |
|---|---|---|
| 1 | Nenhuma quantidade é derivada de percentual | ausência de caminho de escrita: `vagas_imediatas` só é escrito a partir do formulário e do serializer. Teste de varredura |
| 2 | A ampla concorrência aparece uma vez por Perfil | `uq_linha_geral_por_perfil` (banco) + `validate_profile` (domínio) |
| 3 | Toda linha reservada referencia Modalidade do próprio Perfil | FK (banco) + `validate_profile` (`FR-158`) + `_identidades_aninhadas_alheias` (`draft.py:34`) + finding impeditivo no publicado (`FR-166`) |
| 4 | Toda linha publicada é alcançável por identidade, e nenhuma por posição | `COLECOES_COM_CHAVE` + a gramática de `changes.py`, que **recusa** índice onde há chave |
| 5 | Quadro ausente nunca significa zero | degrau 12 escreve `[]`; o documento omite a seção; nenhum caminho lê ausência como `0` |
| 6 | Nenhum valor publicado é reescrito | tabelas append-only por trigger e por privilégio; a Retificação materializa versão nova |
| 7 | Nenhuma tela atribui pessoa a linha | a feature não tem caminho de escrita entre `Inscricao` e linha. Ausência verificável |

---

## Integridade referencial no conteúdo publicado

Um *finding* impeditivo novo em `editais/domain/validation.py`:

| Código | Quando | Mensagem |
|---|---|---|
| `vacancy_row_modality_missing` | uma linha de `vacancyTable` tem `modalityId` que não existe no Perfil | nomeia **a linha** que impede (`FR-172`, `D-008`) |

Ele é aplicado sem código de orquestração novo, porque os três pontos já chamam
`validate_for_publication`:

- `retificacoes.py:515` (`_assert_well_formed`) — sobre o conteúdo que a Retificação **produziria**;
- `retificacoes.py:555` (`_assert_structurally_publishable`) — por fronteira de vigência;
- `publish_edital.py:376` e `:594` — submissão e publicação (`FR-166`).

Verificar o **resultado**, e não a operação, é o que faz remover Modalidade **e** linha no mesmo ato
passar, e remover só a Modalidade ser recusado — que é literalmente o que a `D-008` pede.

E um *finding* de **aviso**, que nunca bloqueia:

| Código | Quando |
|---|---|
| `vacancy_row_percentage_divergence` | a quantidade declarada diverge do percentual publicado na Regra Normativa da Modalidade (`FR-163`, `D-003`) |

---

## A conferência da soma (`FR-161`)

Roda **só** quando o quadro é **completo**: linha geral presente **e** nenhuma Modalidade declarada
no Perfil sem linha.

```
completo?  →  soma(linhas)  ==  perfil.immediate_vacancies   (FR-161)
parcial?   →  a igualdade não roda: somar linhas incompletas produziria acusação falsa (D-006)
ausente?   →  não roda; o Edital continua submetível e publicável (FR-160)

sempre     →  soma(linhas)  <=  perfil.immediate_vacancies   (FR-177)
```

**O limite superior não espera pela completude.** Somar menos que o total é legítimo num quadro
parcial; somar **mais** não é legítimo em quadro algum — nenhum Edital reserva mais vagas do que
oferece. É essa metade que alcança o Edital que declara uma Modalidade chamada "Ampla concorrência" e
que, por isso, nunca fica completo.

Divergência **recusa a submissão**, e a mensagem diz os três números: o que soma, o que foi
declarado, e a diferença (`UX-023`). **A conferência alcança a Retificação**, sobre o conteúdo que
ela produziria: reduzir uma linha e o total do Perfil é um ato só, e quem retifica declara os dois —
como na `D-008` (`FR-161`). O total do Perfil **não** é sobrescrito (`FR-162`): calcular a
partir das linhas apagaria o caso em que o Edital publica um total que a repartição não fecha — que
existe, e que o sistema precisa saber recusar em vez de esconder (`D-007`).

> **Lacuna registrada, e só parcialmente fechada.** No Edital que declara uma Modalidade chamada
> "Ampla concorrência" — que a spec diz ser o caso normal —, seguir a `FR-176` deixa essa Modalidade
> sem linha e o quadro nunca fica completo, de modo que a **igualdade** da `FR-161` nunca roda ali. O
> limite superior da `FR-177` roda, e pega a direção perigosa. O que sobra aberto é o quadro que soma
> **menos** do que o total nesse formato. Ver `research.md`, `R-006`: as duas saídas que fechariam o
> resto estão nomeadas com o custo de cada uma, e a escolha é do usuário.

---

## Reaproveitamento entre Editais (`023`)

`editais/domain/reaproveitamento.py` troca **toda** identidade ao copiar um Edital para o seguinte. A
linha entra nos **dois** passos:

1. registrar o `id` da linha no mapa de identidades (`reaproveitamento.py:56-67`);
2. trocar o `id` da linha **e** o `modalityId` dela (`reaproveitamento.py:95-111`).

Esquecer o segundo é o defeito silencioso da feature: a linha copiada continuaria apontando a
Modalidade do Edital **anterior**. `modalityId` nulo atravessa intocado.
