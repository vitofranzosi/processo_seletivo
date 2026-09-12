# Implementation Plan: Ocupação de Vagas entre Listas de Concorrência

**Feature:** `016` · **Spec:** [spec.md](spec.md) · **Criado:** 2026-09-12
**Base medida:** `daded41` — a `main` com a `014` integrada

## Summary

A feature apura, por recorte do ato de ordenação, quantas vagas o Edital publicou, quantas estão
ocupadas e quantas faltam; reverte vaga reservada não preenchida para a ampla concorrência quando o
Edital declara; trata quem ocupa por duas listas ao mesmo tempo; e entrega o déficit à `014` como
causa da faixa seguinte.

**Três decisões do usuário governam o plano inteiro** (`D-006`, `D-007`, `D-008` da spec), e a
terceira é a que mais custa: a apuração é **ato append-only por recorte**, não projeção. Isso põe
entidade, migration e privilégio **antes** da primeira tela.

**O molde já existe e não se inventa nada.** `Corte` (`classificacao/models.py:217`) é a resposta a
exatamente este formato de problema — ato imutável por recorte `(perfil_id, marco_id, lista_id)`,
com `versao` congelada, sucessão por auto-FK e **vigência que não é coluna**. Este plano copia a
forma e nomeia, na §*As armadilhas*, os três pontos em que copiá-la sem pensar quebra.

## Technical Context

**Linguagem/versão:** Python 3.13 · Django 5.2 LTS · DRF
**Persistência:** PostgreSQL — e **só** PostgreSQL para as garantias desta feature (gatilho
append-only e constraint parcial com `NULL`)
**Testes:** pytest, `make test-pg` (4862 passando em `daded41`)
**Alvo:** monólito modular, `backend/processo_seletivo/`

### O que a feature lê, e de onde

| Entrada | Origem | Leitura |
|---|---|---|
| quantidade por recorte | `vacancyTable[].immediateVacancies` no Perfil publicado, degrau 12 | da **linha**, nunca do total do Perfil (`FR-240`) |
| qual Modalidade é a ampla | `generalCompetitionModalityId` (degrau 13) | identidade declarada, nunca nome (`FR-241`) |
| a ordem do recorte | `AtoDeOrdenacao` vigente, recorte `(perfil_id, marco_id, lista_id)` | recusa se não vigente (`FR-243`) |
| quem foi recusado | consequência da `PosicaoNaOrdem` e o efeito da Etapa governada | — |
| a faixa que progrediu | `Corte` vigente da geração | — |
| ordem de chamada entre recortes | `callRules` | **não é desta feature** (`D-006`) |

### Onde a feature mora — e a dependência que decide isso

**Módulo novo, `ocupacao`.** A alternativa era acomodar tudo em `classificacao`, onde `Corte` já
está, e ela foi **recusada por causa do sentido da dependência**:

```
ocupacao  ──lê──▶  classificacao (AtoDeOrdenacao, Corte)
ocupacao  ──lê──▶  publicacoes    (VersaoConsolidada, conteúdo publicado)
ocupacao  ──chama──▶ classificacao.application.emissao_do_corte   (a faixa seguinte)

classificacao ──▶ ocupacao       NUNCA
```

A `FR-255` manda o déficit ser entregue à `014` como causa da faixa seguinte. Se `classificacao`
lesse a apuração para descobrir a causa, as duas passariam a se importar mutuamente — e o import
circular é o menor dos problemas: o grave é que a `014` deixaria de ser compreensível sozinha,
contra a fronteira que a decisão de 11/09 fixou. **Quem causa é a `016`**, chamando a emissão da
`014` com o número em mão. É a leitura literal do diagrama daquela decisão.

Pôr tudo em `classificacao` também tornaria o nome do módulo falso: ele classifica: ordena, combina,
desempata e corta. Ocupação de vaga não é classificação — é a consequência dela sobre o quadro.

## Constitution Check

| Princípio | Como este plano o atende |
|---|---|
| **I** Linguagem ubíqua | `ApuracaoDeOcupacao`, `MovimentoDeVaga`, `reversao`, `esgotamento`, `saldo` — vocabulário dos próprios Editais. Chave publicada em inglês (`vacancyReversion`), domínio em português, como a `025` fixou |
| **II** Integridade normativa | a declaração da reversão é conteúdo publicado, com **degrau 14**, caminho de leitura das anteriores e entrada no catálogo de Retificação. Ausência ≠ padrão (`FR-251`) |
| **II** Imutabilidade | duas tabelas append-only novas, com gatilho **e** privilégio ausente. Correção é sucessão (`FR-260`, `FR-262`) |
| **III** Auditoria | emissão grava ator, ato, estados, motivo e correlação; `FR-259` exige trilha de todo número exibido |
| **IV** Regras explícitas | o gatilho da reversão é **declarado**, nunca inferido (`FR-249`); ausência de declaração significa "não move" (`D-002` da spec) |
| **V** Rastreabilidade | matriz em `rastreabilidade.md` na entrega; `FR-239`–`FR-263` citados em teste |
| **VI** Completude de jornada | o gate da §9 da spec é percurso pela interface administrativa, sem shell e sem banco. **O passo 3 da ordem de execução é a tela**, e não o fim da fila |

### Invariantes do domínio tocados

- **"Cotas DEVEM ser definidas por Perfil"** — a declaração da reversão é do **Perfil**, e é onde os
  Editais a escrevem. Não há campo por linha do quadro, e a §*O que este plano não faz* diz por quê.
- **"Mudança futura NÃO PODE alterar Edital publicado"** — o degrau 14 escreve `null` no objeto
  inteiro para todo Edital anterior, significando "não declarou reversão". Conversão sem invenção,
  como os degraus 12 e 13.
- **"Migrations aplicadas NÃO PODEM ser reescritas"** — três migrations novas, nenhuma reescrita.
- **"Cancelamento DEVE ser ato de domínio, nunca exclusão"** — apuração não se apaga; fica sucedida.

### Gate: nenhuma violação

Nenhum princípio exige justificativa nesta feature. A `Complexity Tracking` registra a única escolha
que **adiciona** peso — o módulo novo — e por que ela reduz acoplamento em vez de aumentá-lo.

## Project Structure

### Documentation (this feature)

```
specs/016-ocupacao-de-vagas/
├── spec.md
├── plan.md              ← este arquivo
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ocupacao.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```
backend/processo_seletivo/
├── ocupacao/                          ← módulo novo
│   ├── domain/
│   │   ├── apuracao.py                # o cálculo puro: quadro + ordem + recusas → números
│   │   ├── reversao.py                # as duas espécies de gatilho (D-007)
│   │   └── nomes.py                   # vocabulário e códigos de recusa
│   ├── application/
│   │   ├── emissao.py                 # emitir a apuração (ato), sucessão, autorização
│   │   ├── movimento.py               # reversão e liberação — os dois sentidos
│   │   ├── causar_faixa.py            # chama classificacao.emissao_do_corte com o déficit
│   │   └── selectors.py               # leitura da vigente e das causas de obsolescência
│   ├── models.py                      # ApuracaoDeOcupacao, MovimentoDeVaga
│   └── migrations/
│       ├── 0001_apuracao.py
│       └── 0002_movimento.py
├── editais/
│   ├── domain/validation.py           # conferência da declaração de reversão
│   ├── migrations/00NN_reversao.py    # `especie_de_reversao` no PerfilVaga — uma coluna
│   └── application/draft.py           # leitura do rascunho
├── publicacoes/
│   ├── domain/elevacao.py             # degrau 14
│   └── application/publish_edital.py  # `vacancyReversion` no Perfil do snapshot
├── shared/canonical.py                # SCHEMA_VERSION 13 → 14
├── seguranca/papeis.py                # as duas tabelas novas em TABELAS_APPEND_ONLY (24 → 26)
└── interface/
    ├── retificacao.py                 # CAMPOS_PERFIL += a declaração
    ├── forms.py, views.py             # elaboração e a tela dos três números
    └── templates/interface/ocupacao.html
```

## Ordem de execução

Segue a §8 da spec, com o que cada passo entrega e o que ele **não** pode deixar para depois.

1. **O cálculo puro** — `ocupacao/domain/apuracao.py`. Lê quadro, ordem e recusas; devolve
   publicadas, ocupadas e faltando por recorte. Determinístico, sem gravar, sem Django ORM na
   assinatura — é a forma de `classificacao/domain/faixa.py`, e é o que torna `FR-244` testável sem
   banco.
2. **O ato de apuração** — modelo, migration, **as duas tabelas em `TABELAS_APPEND_ONLY`**, gatilho,
   privilégio, emissão, autorização, auditoria, sucessão e as causas de obsolescência.
   *Não deixar o registro em `papeis.py` para depois*: tabela append-only sem privilégio ausente é
   append-only de mentira, e a segunda passada do provisionamento é o que a concede.
3. **A tela dos três números** — História 1, `UX-031` e `UX-032`. É o que substitui a planilha, e o
   Princípio VI não considera entregue capacidade que nenhuma interface alcança.
4. **A declaração publicada da reversão** — degrau 14, `SCHEMA_VERSION`, caminho de leitura,
   elaboração, documento, `CAMPOS_PERFIL` e conferência. As duas espécies da `D-007` entram juntas.
5. **A reversão** — `MovimentoDeVaga`, o invariante da soma constante (`FR-247`) e `UX-033`.
6. **A causa para a `014`** — `causar_faixa.py`, `FR-255` e `FR-256`.
7. **A concorrência concomitante** — a liberação em sentido contrário, História 4.

Os passos 1 a 3 e 6 fecham o 77/2026. Os 4, 5 e 7 alcançam o 57 e o 28.

### As três armadilhas que matam em silêncio

**1. Vigência e obsolescência não são flags materializadas.** Mantê-las exigiria `UPDATE`, operação
proibida nas tabelas append-only — o provisionamento instala e verifica essa proibição. O `Corte`
resolve por derivação: vigente é a geração cuja raiz ninguém sucedeu, e a obsolescência é
**calculada** com as causas nomeadas (`corte.py:292` devolve `{"obsoleto": ..., "causas": [...]}`).
Esta feature faz igual. Quem acrescentar a coluna não é barrado ao criá-la — é barrado quando tentar
atualizá-la, que é o modo de falha mais tardio possível.

**2. A constraint parcial precisa vir em par, por causa do `NULL`.** `lista_id` nulo é a ampla
concorrência, e **no PostgreSQL dois `NULL` não colidem**: uma `UniqueConstraint` sobre
`(edital, perfil_id, marco_id, lista_id)` deixaria passar duas raízes de ampla concorrência no mesmo
marco. `uq_corte_raiz_por_marco` e a irmã dela existem por isso, e a `025` pagou o mesmo preço nas
duas constraints da linha geral do quadro. **Duas constraints, sempre.**

**3. O número não pode sair de leitura do conteúdo publicado por linha de listagem.** O orçamento de
consulta já reprovou esse desenho: a condição precisa sair de **coluna e de SQL**. Por isso as
quantidades apuradas são colunas do ato — como `etapa_governada_id` é coluna no `Corte`, com a razão
medida escrita no próprio modelo — e não se recalculam abrindo o snapshot a cada leitura de tela.

### A travessia que a `D-007` obriga

A declaração da reversão tem de atravessar **seis** lugares, e é o mesmo caminho que a `025` e a
`014` percorreram para o quadro e para a regra de corte:

```
rascunho (draft.py)  →  conferência (validation.py)  →  snapshot (publish_edital.py)
      →  elevação (elevacao.py, degrau 14)  →  documento (pdf)  →  Retificação (CAMPOS_PERFIL)
```

**O último é o que não tem conserto depois.** A `025` registrou a lição em letras: endereço de
retificação não se conserta, porque publicação é ato imutável — sem a entrada no catálogo, o
primeiro Edital publicado com reversão nasce irretificável naquele campo.

## O que este plano deliberadamente não faz

- **Não cria campo de reversão por linha do quadro.** Os Editais declaram por Perfil, e a
  Constituição manda cota ser definida por Perfil. Uma reversão por linha resolveria Editais que
  ninguém leu ainda, ao custo de catálogo de Retificação e tela por linha.
- **Não deriva quantidade de `percentage`.** Recusado pela `FR-157` da `025`, e o plano não
  reintroduz a conta por outro caminho.
- **Não implementa a cascata entre recortes.** É alvo derivado da `014` (`D-006`), e nem o
  `callRules` é consumido aqui.
- **Não toca a lacuna da `R-006`.** A apuração lê a **linha**, e por isso não herda a divergência da
  soma. O achado é decisão do usuário, registrado em
[`doc/achado-igualdade-da-soma-sem-a-ampla-declarada.md`](../../doc/achado-igualdade-da-soma-sem-a-ampla-declarada.md).
- **Não introduz vigência nem obsolescência em coluna.** Ver armadilha 1.
- **Não reimplementa ordem, desempate ou seleção.** `FR-257` proíbe, e o teste de vocabulário
  (`UX-034`) torna a proibição verificável, como a `014` fez com o vocabulário do corte.

## Complexity Tracking

| Escolha | Peso que adiciona | Por que ainda assim |
|---|---|---|
| **módulo `ocupacao` novo** | mais um app Django, mais um lugar para procurar | mantém a dependência em **um** sentido e preserva a `014` compreensível sozinha. O contrário — tudo em `classificacao` — acopla as duas features que a decisão de 11/09 separou de propósito |
| **duas tabelas append-only** | gatilho, privilégio, provisionamento, 24 → 26 | a `D-008` decidiu ato, e ato neste sistema é append-only. Não é peso opcional: é o que a decisão implica |
| **degrau canônico 14** | elevação, caminho de leitura, documento, Retificação | a `D-007` decidiu conteúdo publicado. Sem o degrau, o acervo anterior fica inendereçável naquele campo |
| **duas espécies de gatilho** | um enum a mais na conferência e na tela | os dois Editais escrevem diferente, e uma regra só fixaria em ato publicado uma divergência de norma |
