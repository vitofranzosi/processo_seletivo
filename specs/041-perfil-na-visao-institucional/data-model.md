# Phase 1 — Modelo de dados: o Perfil na visão institucional

**Feature**: `041-perfil-na-visao-institucional` · **Data**: 2026-09-21

> **Nenhuma entidade persistente, nenhuma migration.** Como na `040`, o que segue são **formas de
> leitura** — montadas na requisição e descartadas com ela. Nenhuma conhece o banco.

---

## 1. O que já existe e passa a ser lido inteiro

| Fonte | Lido hoje | Passa a ser lido |
|---|---|---|
| `content["profiles"][]` | `id`, `immediateVacancies`, `reserveType` | \+ `name`, `code`, `locality`, `reserveLimit` |
| `Inscricao` agregada | submetidas **por Perfil**; rascunho **por Edital** | rascunho **por Perfil** |

**Nada mais.** Os indicadores registrados da `040` — classificados, convocados, ocupação,
requerimentos — continuam fora.

---

## 2. As formas novas

### 2.1 `PerfilDaLinha`

```
PerfilDaLinha
  identidade:        str            # o id publicado, que casa com Inscricao.profile_id
  denominacao:       str            # `name`, ou `code` quando não houver
  codigo:            str            # `code`, ao lado da denominação e nunca em coluna própria
  localidade:        str            # `locality` como publicado — "" quando não declarado
  vagas:             Numero
  reserva:           Reserva
  submetidas:        Numero
  em_preenchimento:  Numero
  razao:             Numero
  marcas:            tuple de Marca
```

**Reusa `Numero`, `Ausencia` e `Marca` da `040`** — não nascem tipos paralelos. A razão do Perfil é
`Ausencia(NAO_APLICAVEL)` onde ele não publica vaga imediata, pela **mesma** função que a linha do
Edital usa: duas implementações da mesma regra divergiriam na primeira mudança.

### 2.2 `Reserva` — três espécies, e a limitada carrega o limite

```
Reserva
  especie:  NENHUM | LIMITADO | ILIMITADO
  limite:   int | None            # só em LIMITADO, e obrigatório nela
```

**É tipo, e não um booleano `tem_reserva`.** A `040` carregava justamente isso na linha do Edital —
*"algum Perfil tem reserva"* —, que no agregado já era ambíguo e no Perfil seria perda: `LIMITADO`
publica uma quantidade, e colapsá-la apagaria o que o Edital declarou (`FR-608`).

### 2.3 `LinhaDoEdital` — o que ela ganha

```
LinhaDoEdital
  …os campos da 040…
  perfis:                 tuple de PerfilDaLinha
  submetidas_sem_perfil:  int      # inscrições cujo Perfil saiu da versão vigente
  rascunhos_sem_perfil:   int
```

**`tem_reserva` sai.** Ele era a resposta grosseira que a expansão substitui; mantê-lo criaria duas
formas de dizer a mesma coisa, com precisões diferentes.

---

## 3. Regras de derivação

| Regra | De onde vem |
|---|---|
| Os Perfis são os da **versão consolidada vigente** | `FR-606` |
| `denominacao` = `name`, e `code` quando `name` for vazio | `FR-607` |
| `localidade` apresentada como publicada, sem interpretação | `FR-609` |
| `Reserva.limite` obrigatório em `LIMITADO`, ausente nas outras duas | `FR-608` |
| razão do Perfil = submetidas do Perfil ÷ vagas do Perfil; **não aplicável** sem vaga imediata | `FR-611` |
| `Σ perfis.vagas == linha.vagas` e `Σ perfis.submetidas + submetidas_sem_perfil == linha.submetidas` | `FR-612`, `FR-613a` |
| a razão do Edital é **recalculada** — `Σ submetidas dos Perfis com vaga ÷ Σ vagas desses Perfis` — e **nunca** somada ou mediada das razões dos Perfis | `FR-612` |
| a diferença é declarada **em texto**; nenhuma linha, agrupamento ou rótulo faz as vezes de Perfil | `FR-613a` |
| `SEM_PROCURA` no Perfil ⇔ período encerrado **e** submetidas `0` — **com ou sem denominador** | `FR-615` |
| `DEMANDA_ABAIXO_DA_OFERTA` no Perfil ⇔ período encerrado **e** razão `< 1` | `FR-613` |
| marca do Edital = por espécie, *"N de M Perfis…"*, **com o denominador de cada uma** — todos os vigentes para *sem procura*, só os com vaga imediata para *demanda abaixo*; com `M == 1`, a mensagem do próprio Perfil | `FR-614`, `R-004` |
| o filtro *Somente com atenção* é aplicado **depois** da materialização, e o consolidado o acompanha | `FR-621`, `R-009` |

**Nenhuma transição de estado.** As formas nascem na requisição e morrem com ela.

---

## 4. O que muda na `040`, e o que não muda

| | |
|---|---|
| **Muda** | `_marcas` deixa de operar sobre o agregado e passa a operar sobre os Perfis; a `FR-602` é substituída (`FR-616`) |
| **Muda** | `contagens_por_edital` acumula rascunho por Perfil — mesma consulta |
| **Muda** | `vagas_do_conteudo` devolve o conjunto **completo** de Perfis, e não só os com vaga |
| **Não muda** | a linha é o Edital; o consolidado; os filtros; a gramática da ausência; o orçamento de consulta |
