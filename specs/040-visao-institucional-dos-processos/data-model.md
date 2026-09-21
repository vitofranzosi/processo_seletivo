# Phase 1 — Modelo de dados: a visão institucional

**Feature**: `040-visao-institucional-dos-processos` · **Data**: 2026-09-21

> **Nenhuma entidade persistente nasce aqui, e nenhuma migration.** O que segue são **formas de
> leitura**: estruturas montadas na requisição e descartadas com ela. Não têm identidade, não têm
> persistência, e nenhuma delas conhece o banco — é a mesma disciplina, e a mesma redação, de
> `interface/supervisao.py` §1.

---

## 1. O que já existe e é lido

| Fonte | O que se lê | Onde |
|---|---|---|
| `ProcessoSeletivo` | `id`, `title`, `institutional_code`, `status`, `institution_scope` | `processos/models.py` |
| `Edital` | `id`, `processo_id`, `number`, `year`, `status` | idem |
| `VersaoConsolidada` | `edital_id`, `valid_from`, `materialized_at`, `content` | `publicacoes/models_retificacao.py` |
| `content["profiles"][]` | `id`, `name`, `code`, `immediateVacancies`, `reserveType`, `reserveLimit` | conteúdo publicado |
| `content["schedule"][]` | o Evento com `isRegistrationPeriod`, `startAt`, `endAt` | idem |
| `Inscricao` | `edital_id`, `profile_id`, `status` | `inscricoes/models.py` |

**Nada mais.** Os indicadores registrados (`§9` da spec, 7 a 14) leriam `SituacaoDivulgada`,
`Convocacao`, `ApuracaoDeOcupacao` e `RequerimentoDeMatricula` — e nenhum deles é lido nesta entrega.

---

## 2. As formas de leitura

### 2.1 `Ausencia` — a razão pela qual um número não existe

```
Ausencia
  especie:  NAO_APLICAVEL | NAO_DISPONIVEL | NAO_PUBLICADO
  motivo:   texto legível, escrito para a tela
```

**É tipo, e não `None`.** Um `None` solto no contexto obrigaria o template a decidir **qual** das
quatro ausências ele é — e o template decidindo isso é a segunda verdade que `FR-582` proíbe. Com
tipo, a derivação decide e a tela apenas escreve.

**A quarta ausência não mora aqui.** *Parcial* qualifica um número que **existe**, e por isso é
atributo de `Numero`, e não espécie de `Ausencia`. Colapsá-las faria *"40 submetidas, ainda
crescendo"* virar ausência — que é o erro simétrico que `FR-591` proíbe.

### 2.2 `Numero` — um valor, ou a razão de não haver valor

```
Numero
  valor:     int | Decimal | None
  ausencia:  Ausencia | None        # exatamente um dos dois é preenchido
  parcial:   bool                   # só faz sentido com valor
  porque:    texto                  # o motivo da parcialidade, vazio quando não parcial
```

**Invariante**: `valor is None` ⇔ `ausencia is not None`. **E `valor == 0` é valor**, nunca ausência
— é `FR-591` expressa na forma, e é o ponto em que a primeira redação da spec errava.

### 2.3 `LinhaDoEdital` — uma linha da tabela

```
LinhaDoEdital
  edital:           o objeto, para o link e o rótulo
  processo_titulo:  texto
  situacao:         Edital.status
  periodo:          SituacaoDoPeriodo | Ausencia
  vagas:            Numero
  submetidas:       Numero
  em_preenchimento: Numero
  razao:            Numero           # uma casa decimal
  marcas:           tupla de Marca
```

### 2.4 `SituacaoDoPeriodo` — reusada, não redefinida

```
SituacaoDoPeriodo
  estado:  futuro | aberto | encerrado        (de inscricoes.domain.periodo)
  inicio:  datetime | None
  fim:     datetime | None
```

**Os três estados vêm do domínio da `009`**, e `nao-designado` vira `Ausencia`. Não há vocabulário
novo: *"o candidato e a supervisão precisam responder a mesma pergunta, e dois vocabulários para «as
inscrições estão abertas» é o que o Princípio I recusa"*.

### 2.5 `Marca` — a atenção derivada, e não um sinal do catálogo

```
Marca
  especie:   SEM_PROCURA | DEMANDA_ABAIXO_DA_OFERTA
  mensagem:  texto legível sem cor
```

**Duas espécies e nada mais** (`FR-602`). **Sem identificador `UX-`, sem destino próprio** — o
destino da linha é o Edital, como o de qualquer outra linha (`D-007`). Acrescentar espécie aqui
**não** altera o catálogo fechado da `022`/`038`.

### 2.6 `Consolidado` — os quatro números e os seus denominadores

```
Consolidado
  editais:              int
  processos:            int          # contexto
  editais_publicados:   int          # denominador de `vagas`
  vagas:                Numero
  submetidas:           Numero
  razao:                Numero
  perfis_com_vaga:      int          # denominador de `razao`
  fora_da_razao:        int          # Editais sem Perfil com vaga imediata (FR-590)
  parciais:             int          # somandos ainda em curso (FR-595)
```

**Os denominadores são campos, e não prosa montada no template**: é o que permite testá-los sem
renderizar, e é o que `FR-585` cobra ao exigir que eles acompanhem o número que explicam.

### 2.7 `Recorte` — o que o usuário pediu, saneado

```
Recorte
  ano:               int | TODOS
  situacao:          Edital.Status | ""
  situacao_periodo:  futuro | aberto | encerrado | nao-designado | ""
  busca:             texto
  ordem:             chave de ORDENS
  anos_disponiveis:  tupla de int
  padrao:            bool            # nada veio na URL, e o ano corrente foi aplicado
```

**Saneado na entrada, no padrão de `portal/leitura.py`**: valor fora do conjunto aceito vira o
padrão, e nunca chega à consulta. `padrao` existe para a tela poder declarar o recorte aplicado
(`FR-599`) sem reinspecionar a URL.

---

## 3. Regras de validação e derivação

| Regra | De onde vem |
|---|---|
| `valor is None` ⇔ `ausencia is not None` | `FR-591`, `FR-594` |
| `vagas` = `Σ profiles[].immediateVacancies` da versão **vigente** | `FR-587`, `D-003` |
| Edital sem versão vigente → `vagas = Ausencia(NAO_PUBLICADO)` | `FR-587` |
| numerador da razão = submetidas cujo `profile_id` publica `immediateVacancies > 0` | `FR-588`, `D-012` |
| nenhum Perfil com vaga imediata → `razao = Ausencia(NAO_APLICAVEL)` | `FR-589` |
| Edital sem denominador não entra no consolidado, e é contado em `fora_da_razao` | `FR-590` |
| `submetidas.parcial` ⇔ período `aberto` | `FR-595` |
| `SEM_PROCURA` ⇔ período `encerrado` **e** `submetidas.valor == 0` | `FR-602` |
| `DEMANDA_ABAIXO_DA_OFERTA` ⇔ período `encerrado` **e** `razao.valor < 1` | `FR-602` |
| ordenação: ausência ao fim **nos dois sentidos** | `FR-601`, `R-008` |
| recorte sem parâmetro → ano corrente, `padrao = True` | `FR-599`, `D-013` |

**Nenhuma transição de estado.** Não há agregado com ciclo de vida nesta feature: as formas nascem
na requisição e morrem com ela.

---

## 4. O que deliberadamente **não** está modelado

| Ausente | Por quê |
|---|---|
| `Classificados`, `Convocados`, `Ocupacao`, `Requerimentos` | definidos na §9 da spec e **registrados**, não obrigados (`D-011`) |
| `PessoasDistintas` | decisão do usuário pendente (`G-003`), e erro não mensurável (`D-006`) |
| `PontoDaSerie` | a série sai desta entrega (`D-013`), e a forma dela depende de `G-013` |
| Qualquer coluna de indicador em tabela | seria a tabela duplicada de indicadores que `§15` recusa |
| `ObsolescenciaDaApuracao` | recomputá-la no recorte institucional é caro; a página **declara** o limite (`FR-596`) |
