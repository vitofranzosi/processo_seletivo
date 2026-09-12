# Contrato — a ocupação e a declaração que a governa

Dois contratos, **de naturezas diferentes**, e a distinção não é detalhe de forma.

O primeiro é de **API**, e não é novo: a declaração da reversão entra no `openapi.yaml` da `001`,
nos **dois** lugares em que o Perfil aparece, como `vacancyTable` e `generalCompetitionModalityId`
já estão.

O segundo é de **aplicação**: a forma que os *selectors* da ocupação devolvem e que os commands
aceitam, consumida pela interface administrativa. **Não há endpoint HTTP nesta feature**, e a §2
descrevia três — `GET /api/editais/{id}/ocupacao` e dois `POST` — que rota nenhuma serve. A
capacidade é alcançada pela tela, como a `014` fez com o corte: ali o `openapi.yaml` recebeu apenas
a **forma do conteúdo** (`cutRule`, `generalCompetitionModalityId`), e nenhum caminho de
classificação, corte ou sorteio existe nele até hoje.

*Corrigido na convergência da `T061`. Declarar caminhos que respondem 404 seria documentar interface
que o sistema não serve — e um contrato de API é a promessa mais barata de quebrar sem notar, porque
nenhum teste a confronta com as rotas.* Que a ocupação venha a ter API é decisão aberta, e o dia em
que tiver, os nomes desta seção são o desenho de partida.

---

## 1. `vacancyReversion` no Perfil

### `PerfilInput` — o rascunho

```yaml
vacancyReversion:
  type: object
  nullable: true
  required: [kind]
  properties:
    kind:
      type: string
      enum: [ON_EXHAUSTION, ON_BALANCE]
      description: >
        Gatilho da reversão de vaga reservada para a ampla concorrência (016, D-007).
        ON_EXHAUSTION reverte só quando a lista reservada não tem mais ninguém a ocupar;
        ON_BALANCE reverte a quantidade não preenchida, ainda que a lista tenha gente.
```

### `PerfilOutput` — o publicado

A mesma forma. **Objeto `null` significa "este Edital não declara reversão"** — e portanto não
reverte. Não existe objeto pela metade: declarar reversão sem `kind` é recusado na publicação
(`FR-251`).

### Erros

| Código | Quando | Severidade |
|---|---|---|
| `vacancy_reversion_kind_required` | objeto presente sem `kind` | impeditivo |
| `vacancy_reversion_kind_unknown` | `kind` fora do enum | impeditivo |
| `vacancy_reversion_sem_quadro` | reversão declarada em Perfil sem `vacancyTable` | impeditivo |

O terceiro merece a razão: reverter pressupõe quantidade por recorte. Declarar reversão num Perfil
que não publicou quadro é regra inexequível — e regra publicada inexequível é o que a `014` já
recusou a publicar, ao exigir linha de quadro para todo recorte que o marco ordena.

### Degrau canônico 14

`SCHEMA_VERSION` 13 → 14. A conversão escreve `vacancyReversion: null` em todo Perfil de Edital
publicado antes do degrau, e a afirmação é verdadeira sobre todos eles: a capacidade não existia,
não havia onde declarar o gatilho. **Conversão sem invenção**, como os degraus 12 e 13.

### Retificação

Entrada em `CAMPOS_PERFIL` (`interface/retificacao.py:51`) com tipo **`REFERENCIA`** e uma lista
de opções — **não** caixa de texto. É o precedente literal do `cutRule/tieOutcome` da `014`
(`retificacao.py:113`), cujo comentário dá a razão: são valores fechados, e `REFERENCIA` *"os
oferece conferindo a escolha contra a lista"*, enquanto texto livre publicaria valor que o
cálculo não interpreta. As opções vão com as mesmas palavras da tela de composição:

```python
ESPECIES_DE_REVERSAO = (
    ("ON_EXHAUSTION", "Só quando a lista reservada esgota"),
    ("ON_BALANCE", "A quantidade que ficou sem preencher"),
)
```

E o rótulo do vazio precisa dizer o que o vazio provoca, como o do desfecho do empate já diz: sem
espécie, a reversão declarada não publica.

**Declarada antes da primeira emissão do snapshot**, pela lição que a `025` registrou em letras:
endereço de retificação não se conserta depois, porque publicação é ato imutável.

---

## 2. A leitura da apuração — contrato de aplicação

Os nomes abaixo são os do **DTO** que `ocupacao/application/selectors.py` devolve, escritos em YAML
porque é a notação que este repositório já usa para forma. Eles não são coluna nem endpoint: a tela
os lê, e a Constituição proíbe expor entidade de persistência como contrato.

### `ocupacao_do_recorte(...)` — a leitura de um recorte

Devolve, por recorte, os quatro números e o estado da apuração vigente. A tela chama uma vez por
recorte do marco, por `recortes_do_marco(...)`.

```yaml
OcupacaoPorRecorte:
  type: object
  required: [profileId, milestoneId, listId, published, effective, occupied, remaining, state]
  properties:
    profileId:   { type: string, format: uuid }
    milestoneId: { type: string, format: uuid }
    listId:
      type: string
      format: uuid
      nullable: true
      description: "null = ampla concorrência, a mesma grafia da ordem e do corte"
    published:
      type: integer
      minimum: 0
      nullable: true
      description: "da linha do quadro, nunca do total do Perfil; null em NO_VACANCY_TABLE"
    effective:
      type: integer
      minimum: 0
      nullable: true
      description: "published mais o recebido, menos o cedido; null sem apuração emitida"
    occupied:
      type: integer
      minimum: 0
      nullable: true
      description: "null sem apuração emitida — zero é afirmação, e ausência não é zero"
    remaining:
      type: integer
      minimum: 0
      nullable: true
      description: "effective menos occupied; null sem apuração emitida"
    movements:
      type: array
      items: { $ref: "#/components/schemas/MovimentoDeVaga" }
    state:
      type: string
      enum: [CURRENT, OBSOLETE, NOT_APPRAISED, NO_VACANCY_TABLE]
    obsolescenceCauses:
      type: array
      items: { type: string }
      description: "causas nomeadas, nunca 'divergências' (016, FR-263)"
```

**`state` tem quatro valores, e dois deles não são erro.** `NOT_APPRAISED` é recorte que ainda não
teve apuração emitida; `NO_VACANCY_TABLE` é Edital publicado antes do degrau 12, que **não** tem
quadro. Colapsar os dois em "0 vagas" é o defeito que esta distinção existe para impedir.

**E é por isso que as quatro quantidades são anuláveis**, com a regra dita campo a campo:

| Estado | published | effective, occupied, remaining |
|---|---|---|
| `CURRENT`, `OBSOLETE` | da apuração | da apuração |
| `NOT_APPRAISED` | **da linha do quadro** — fato do Edital, e não de apuração | `null` |
| `NO_VACANCY_TABLE` | `null` | `null` |

**Zero é afirmação, e `null` é ausência.** Depois de apurar, `occupied: 0` quer dizer que um ato
contou e não encontrou ninguém ocupando; antes, quer dizer que ninguém contou. Devolver zero nos
dois casos faria a leitura produzir número que ato nenhum sustenta — contra a `FR-259` e contra a
`FR-261`, que é o "ler não ocupa" desta feature.

```yaml
MovimentoDeVaga:
  type: object
  required: [kind, quantity, cause]
  properties:
    kind:
      type: string
      enum: [QUOTA_REVERSION]
      description: >
        Uma espécie só. A concorrência concomitante do item 8.9 do 28/2026 não move quantidade
        nenhuma — ela aparece como ocupação menor na lista reservada, e não como movimento.
    fromListId:      { type: string, format: uuid, nullable: true }
    toListId:        { type: string, format: uuid, nullable: true }
    quantity:        { type: integer, minimum: 1 }
    cause:           { type: string }
```

### `emitir_apuracao(...)` — o ato

Emite a apuração de um recorte. **Command explícito e idempotente**: exige `idempotency_key`, como
todo command irreversível deste sistema, e a tela a gera no GET — não no POST —, porque chave
sorteada a cada envio faria um duplo clique produzir duas apurações sucessivas sem que ninguém
pedisse. É a mesma lição que o corte da `014` registra.

```yaml
EmitirApuracaoCommand:
  type: object
  required: [profileId, milestoneId]
  properties:
    profileId:   { type: string, format: uuid }
    milestoneId: { type: string, format: uuid }
    listId:      { type: string, format: uuid, nullable: true }
    reason:      { type: string, description: "obrigatório quando sucede uma apuração anterior" }
```

| Erro | Quando |
|---|---|
| `ordem_nao_vigente` | a ordem do recorte foi sucedida (`FR-243`) |
| `sem_quadro_publicado` | o Edital não publicou quadro (`FR-242`) |
| `recorte_sem_linha` | a lista ordena e não tem linha no quadro |
| `motivo_da_sucessao_obrigatorio` | há apuração anterior e falta o motivo |

### `causar_faixa_seguinte(...)` — a causa entregue à `014`

Entrega o déficit apurado à `014` como causa da faixa seguinte (`FR-255`). **Esta função não
seleciona ninguém**: ela chama a emissão do corte da `014`, que é quem lê ordem e escolhe.

| Erro | Quando |
|---|---|
| `deficit_zero` | o déficit apurado é zero (`FR-256`) |
| `apuracao_obsoleta` | a apuração vigente está obsoleta (`FR-263`) |

### O que estes contratos deliberadamente não expõem

- **Nenhum endpoint HTTP**, e a razão está no cabeçalho: a capacidade é alcançada pela tela, e
  caminho declarado sem rota que o sirva é promessa que nada confronta.
- **Nenhum campo de convocação, aceite, matrícula ou desistência.** Não existem antes da `019`
  (`FR-258`), e o vocabulário é verificado por varredura (`UX-034`).
- **Nenhuma função que ordene, desempate ou selecione** (`FR-257`) — e a proibição é estrutural, e
  não textual: `tests/test_dependencia_da_ocupacao.py` varre os imports e prova que a dependência
  tem um sentido só.
- **Nenhuma entidade de persistência como contrato**, conforme a Constituição: `published`,
  `occupied` e `remaining` são DTO, e não colunas expostas.
