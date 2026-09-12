# Data Model — Ocupação de Vagas entre Listas de Concorrência

**Feature:** `016` · **Base medida:** `daded41`

Duas entidades novas, append-only, no módulo `ocupacao`; e uma coluna nova no `PerfilVaga`, que é a
declaração normativa. Nada existente é reescrito.

---

## 1. `ApuracaoDeOcupacao`

O ato que diz, para um recorte, quantas vagas o Edital publicou, quantas estão ocupadas e quantas
faltam. **Append-only** (`D-008`): correção é sucessão.

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `edital` | FK `Edital`, `PROTECT` | |
| `perfil_id` | UUID | **identidade publicada**, não FK para a elaboração |
| `marco_id` | UUID | idem |
| `lista_id` | UUID, anulável | **`NULL` = ampla concorrência** — a grafia de `AtoDeOrdenacao` e de `Corte` |
| `ato` | FK `AtoDeOrdenacao`, `PROTECT` | a ordem que a apuração leu |
| `corte` | FK `Corte`, `PROTECT`, anulável | a faixa que a alimentou; nula onde o recorte não tem corte |
| `versao` | FK `VersaoConsolidada`, `PROTECT` | qual conteúdo publicado foi lido (`FR-259`) |
| `apuracao_anterior` | FK `self`, `PROTECT`, anulável | sucessão (`FR-262`); **nula na primeira** |
| `motivo_da_sucessao` | texto | por que sucedeu |
| `publicadas` | inteiro ≥ 0 | quantidade da **linha** do quadro (`FR-240`) |
| `ocupadas` | inteiro ≥ 0 | dentro da faixa **e** `HABILITADA` (`R-001` da pesquisa) |
| `faltando` | inteiro ≥ 0 | `publicadas + recebidas − cedidas − ocupadas`, onde recebidas e cedidas são as somas dos `MovimentoDeVaga` deste recorte |
| `linha_do_quadro_id` | UUID, anulável | **qual** linha foi lida — a quantidade sozinha não identifica |
| `universo` | JSON | quadro, declaração de reversão e recusas congelados no instante |
| `emitida_por` | texto | |
| `emitida_em` | datetime | |

**Por que `publicadas`, `ocupadas` e `faltando` são colunas.** `R-006` da pesquisa: a tela lista
recortes, e recalcular abrindo o snapshot por linha é a consulta por listagem que o orçamento já
reprovou. É o mesmo motivo — e medido — pelo qual `Corte.etapa_governada_id` existe.

**Por que `linha_do_quadro_id` existe.** É a lição literal do `Corte`, que guarda o `rowId` quando o
alvo é derivado: *"sem ele, retificado o quadro, não há como dizer se aquele corte ficou para trás —
a quantidade sozinha não identifica a linha"* (`classificacao/models.py:277`). Sem esta coluna, a
causa de obsolescência por retificação do quadro (`FR-263`) não é determinável.

**O que NÃO é coluna, e a razão é dura:** `vigente` e `obsoleto`. A tabela é append-only e o
papel de runtime **não tem `UPDATE`** — uma coluna dessas falha no provisionamento, não no
teste. Vigente é a apuração que ninguém sucedeu no recorte; obsolescência é calculada com as
causas nomeadas, como `corte.py:292` já faz (`R-003`).

### Constraints

```python
# Uma primeira apuração por recorte — e são DUAS, porque no PostgreSQL dois NULL não colidem
# (R-004, medido). Com uma só, dois recortes de ampla concorrência passariam no mesmo marco.
UniqueConstraint(
    fields=["edital", "perfil_id", "marco_id"],
    condition=Q(apuracao_anterior__isnull=True, lista_id__isnull=True),
    name="uq_apuracao_primeira_por_marco",
)
UniqueConstraint(
    fields=["edital", "perfil_id", "marco_id", "lista_id"],
    condition=Q(apuracao_anterior__isnull=True),
    name="uq_apuracao_primeira_por_marco_e_lista",
)
CheckConstraint(check=Q(publicadas__gte=0) & Q(ocupadas__gte=0) & Q(faltando__gte=0),
                name="ck_apuracao_nao_negativa")
# Ocupar mais do que se publicou é defeito, nunca arredondamento.
CheckConstraint(check=Q(ocupadas__lte=F("publicadas")), name="ck_apuracao_ocupadas_no_limite")
```

*A última tem uma ressalva que o teste precisa cobrir: com reversão, o limite efetivo da linha geral
sobe. A checagem é contra `publicadas` **da própria linha**, e o excedente recebido viaja em
`MovimentoDeVaga` — é o que mantém a constraint verdadeira sem ela precisar conhecer reversão.*

## 2. `MovimentoDeVaga`

A vaga que muda de recorte. **Os dois sentidos na mesma entidade**, porque são o mesmo fato — uma
quantidade que sai de um recorte e entra em outro — e separá-los faria o invariante da soma ter de
somar duas tabelas.

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `apuracao` | FK `ApuracaoDeOcupacao`, `PROTECT` | a apuração que o fundamentou |
| `especie` | texto | `REVERSAO_DE_COTA` \| `LIBERACAO_POR_CONCOMITANCIA` |
| `origem_lista_id` | UUID, anulável | de qual recorte saiu — `NULL` = ampla |
| `destino_lista_id` | UUID, anulável | para qual entrou — `NULL` = ampla |
| `quantidade` | inteiro > 0 | |
| `causa` | texto | o que autorizou (`FR-248`) |
| `inscricao` | FK `Inscricao`, `PROTECT`, anulável | preenchida só na liberação, que é de pessoa |
| `registrado_por` / `registrado_em` | texto / datetime | |

### Invariantes

1. **Soma constante** (`FR-247`): `Σ publicadas (quadro) + Σ movimentos = Σ quantidades efetivas`.
   Verificado por teste de propriedade sobre sequências aleatórias — a composição erra, não cada
   movimento (`R-007`).
2. **Nenhuma vaga atravessa Perfil** (`FR-246`): origem e destino pertencem ao mesmo `perfil_id` da
   apuração. É o que o 57/2026 proíbe por escrito no item 4.5.
3. **Reversão vai para a linha geral**; **liberação volta para o recorte reservado** (`FR-253`). São
   sentidos opostos, e trocá-los mantém a soma certa com o recorte errado — o defeito que só o teste
   de recorte pega.
4. `origem_lista_id ≠ destino_lista_id`.

```python
CheckConstraint(check=Q(quantidade__gt=0), name="ck_movimento_quantidade_positiva")
CheckConstraint(
    check=~Q(origem_lista_id=F("destino_lista_id")), name="ck_movimento_recortes_distintos"
)
# A liberação é de pessoa; a reversão é de quantidade.
CheckConstraint(
    check=Q(especie="REVERSAO_DE_COTA", inscricao__isnull=True)
    | Q(especie="LIBERACAO_POR_CONCOMITANCIA", inscricao__isnull=False),
    name="ck_movimento_inscricao_conforme_especie",
)
```

## 3. `PerfilVaga.especie_de_reversao` — a declaração normativa

Uma coluna anulável no modelo que já existe (`editais/models/perfis.py`).

| Valor | Significado |
|---|---|
| `NULL` | **este Edital não declara reversão** — e portanto não reverte (`D-002` da spec) |
| `ON_EXHAUSTION` | reverte só quando a lista reservada não tem mais ninguém a ocupar |
| `ON_BALANCE` | reverte a quantidade não preenchida, ainda que a lista tenha gente |

**Uma coluna, e não duas**, porque o objeto publicado tem hoje um campo só — ver `R-005`. No
conteúdo publicado a forma é objeto (`vacancyReversion`), para que um campo novo da mesma decisão
entre sem um segundo degrau.

**Nula não é padrão de comportamento.** A `FR-251` recusa a publicação que declare reversão sem a
espécie; e a ausência do objeto inteiro significa "não declarou", como a lista vazia do quadro
significa "não publicou" (`025`) e o `cutRule` nulo significa "marco que não corta" (`014`).

## 4. Tabelas append-only

As duas entram em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:26`), levando o total de **24 para
26**:

```
ocupacao_apuracaodeocupacao
ocupacao_movimentodevaga
```

**Gatilho e privilégio ausente — as duas camadas, e nenhuma delas contornável em
desenvolvimento.** O registro em `papeis.py` não pode ficar para depois: a segunda passada do
provisionamento é a que concede privilégio sobre as tabelas que a migration acabou de criar, e
tabela append-only sem privilégio ausente é append-only de mentira.

## 5. Transições

`ApuracaoDeOcupacao` não tem estado mutável — é ato. O que existe é **relação entre atos**:

```
        ┌──────────────── sucede (apuracao_anterior) ────────────────┐
        │                                                            │
   apuração A ──── emitida ────▶ vigente ──── nova emissão ────▶ sucedida
                                    │
                                    └── obsoleta (calculada, três causas — FR-263):
                                        · a ordem do recorte foi sucedida
                                        · o corte que a alimentou ficou obsoleto
                                        · o quadro publicado foi retificado na linha lida
```

Obsoleta **não** é sucedida: a primeira é leitura do mundo em volta, a segunda é ato novo. Uma
apuração pode estar vigente e obsoleta ao mesmo tempo — e nesse estado **não causa faixa seguinte**
(`FR-263`), que é exatamente o que a `014` faz com corte obsoleto.
