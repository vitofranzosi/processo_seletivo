# Modelo de dados — Supervisão do Processo

**Nenhuma entidade nova. Nenhuma coluna nova. Nenhuma migration.**

Esta é a afirmação mais importante do documento, e ela é verificável: `D-007` e `SC-014` fazem da
necessidade de persistir estado um motivo para revisar a spec, não para escrever migration.

O que segue é o **modelo de leitura**: quais entidades existentes são consultadas, o que se extrai
de cada uma, e as formas que a interface recebe.

---

## 1. Entidades lidas, e nada além

| Entidade | App | O que a supervisão lê | Escreve? |
|---|---|---|---|
| `ProcessoSeletivo` | `processos` | identidade, situação, escopo institucional | não |
| `Edital` | `processos` | número, ano, título, situação, pertencimento ao Processo | não |
| `Cronograma` | `editais` | vínculo com o Edital | não |
| `EventoCronograma` | `editais` | `start_at`, `end_at`, `order`, `status`, marca de período de inscrições | não |
| `EtapaAvaliacao` | `editais` | nome, ordem, avaliações previstas, vínculo (anulável) com Evento | não |
| `Inscricao` | `inscricoes` | `status`, `submitted_at`, Edital | não |
| `Atribuicao` | `avaliacoes` | vínculo ativo com Etapa e Inscrição | não |
| `Avaliacao` | `avaliacoes` | estado, e a autoria da conclusão | não |
| `Impedimento` | `avaliacoes` | par identidade × inscrição | não |
| `MembroComissao` | `comissoes` | vínculo ativo com o Processo, função | não |
| `ResultadoEtapa` | `resultados` | vigência, autoria da consolidação, avaliação de origem | não |
| `AtoDeOrdenacao` | `classificacao` | vigência, `emitido_em`, `emitido_por`, universo, versão | não |
| `PublicacaoResultado` | `divulgacao` | ato citado, autoria da publicação | não |
| `Recurso` | `recursos` | situação, objeto atacado, inscrição | não |

**A coluna “Escreve?” é o invariante.** Qualquer `save`, `create`, `update` ou `delete` originado
nesta feature é violação de fronteira.

---

## 2. As formas de leitura

Estruturas de transporte, montadas na requisição e descartadas com ela. Não são modelos; não têm
identidade nem persistência.

### 2.1 `Pulso`

```text
Pulso
├── submetidas_no_processo : inteiro          soma dos Editais
├── rascunhos_no_processo  : inteiro          grandeza distinta, nunca somada
├── ultimas_24h            : inteiro          por instante de submissão
├── por_edital : lista de PulsoDoEdital
└── lido_em    : instante                      FR-009
```

```text
PulsoDoEdital
├── edital                 : identificação e número/ano — sempre nomeado (FR-011, FR-020)
├── submetidas             : inteiro
├── rascunhos              : inteiro
├── periodo_de_inscricoes  : PeriodoDeInscricoes | ausente
├── serie                  : lista de (dia, quantidade)      FR-014, FR-015
└── proximos_marcos        : lista de Marco
```

```text
PeriodoDeInscricoes
├── inicio, fim   : instantes do Evento marcado como período
├── restante      : duração até o fim, quando ainda não encerrado
└── situacao      : antes | em curso | encerrado    derivada, nunca gravada
```

```text
Marco
├── descricao, inicio, fim
├── edital        : sempre presente — não há marco do Processo (D-005)
└── declarado     : o status do Evento, apresentado como declaração (D-004)
```

**Sobre a série.** Um ponto por dia dentro do período declarado, inclusive dias com zero — a
ausência de um dia na série faria a leitura supor continuidade que não houve. Dia é o do fuso da
aplicação, e o recorte é o período do Edital; submissões fora dele, se existirem, permanecem no
total e não na série.

**Sobre o percentual.** Não existe campo de percentual em nenhuma forma do Pulso. É `FR-017`
materializado: não há denominador para inscrição, e um campo opcional seria o convite a preenchê-lo.

### 2.2 `Sinal`

Uma forma só para os cinco. O que muda entre eles é o conteúdo, não a estrutura — é o que mantém o
catálogo fechado legível e a região uniforme (`D-002`, `UX-006`).

```text
Sinal
├── especie      : UX-001 | UX-002 | UX-003 | UX-004 | UX-005
├── edital       : a que Edital pertence            sempre presente
├── alvo         : Etapa, Evento, marco ou o Edital
├── mensagem     : o fato, na redação do UX correspondente
├── medida       : (numerador, denominador) | ausente     FR-032
└── destino      : para onde se resolve, ou ausente quando o ator não alcança
```

**`medida` é par ou nada.** Não existe percentual solto: ou vêm numerador e denominador, ou não vem
medida. É `FR-032` expresso na forma, e não confiado à disciplina de quem escreve o template.

**`destino` ausente suprime o sinal inteiro** (`FR-004`). A supressão é silenciosa: a forma não
carrega marca de “havia algo aqui”.

**Não existe `Sinal.gravidade`.** Os cinco são igualmente acionáveis; introduzir severidade pediria
uma ordenação que o domínio não determina e que viraria juízo da tela.

---

## 3. Regras de derivação

Ficam aqui porque são o conteúdo do modelo de leitura — as fórmulas, sem código.

### 3.1 Inscrições

```text
submetidas(edital)  = Inscricao onde status = SUBMETIDA
rascunhos(edital)   = Inscricao onde status = RASCUNHO
ultimas_24h(edital) = submetidas com agora − 24h < submitted_at ≤ agora
serie(edital)       = submetidas agrupadas por dia de submitted_at, dentro do período
```

Não há estado `CANCELADA` no domínio; nenhuma derivação o pressupõe.

**As duas bordas da janela são fechadas de propósito, e a redação já custou uma contradição.** A
inferior é **estrita**: uma submissão de exatamente 24 horas atrás não está *nas últimas* 24 horas,
está na borda delas — é onde o fora-por-um mora, e é o que `T018a` afirma. A superior é o instante
declarado da leitura, e não "agora" de novo: sem teto, uma submissão gravada entre a montagem do
`Pulso` e a contagem entrava no número e ficava fora da série, que sempre teve teto — e a página
declara `lido_em`. Este parágrafo existe porque a fórmula dizia `≥ agora − 24h` e não dizia teto
nenhum, contradizendo a tarefa e o código que a implementa.

### 3.2 Posição temporal (`UX-002`)

```text
posicao(evento, agora) = antes | em curso | encerrado | indeterminada (sem end_at)
divergente(evento)     = status ≠ CANCELADO
                       ∧ posicao ≠ indeterminada
                       ∧ status declarado incompatível com posicao
```

A tabela de incompatibilidade está em `research.md` (`T-005`). Nem o `status` nem a posição é
corrigido: os dois são apresentados.

### 3.3 Cobertura (`UX-003`)

```text
esperado    = submetidas(edital) × avaliações previstas na Etapa
distribuído = Atribuicao ativa na Etapa
carente     = inscrição submetida com atribuições ativas < previstas
```

`carente` é o numerador do sinal, e `submetidas` o denominador (`FR-032`). Unidade sem distribuição
**é** carente, e por isso permanece no denominador (`FR-033`).

### 3.4 Obsolescência (`UX-004`)

Duas passagens, definidas em `T-003`: filtro barato por fato posterior ao ato vigente, confirmação
exata pelo cálculo existente apenas nos candidatos. O sinal só nasce da confirmação.

### 3.5 Impedimento agregado (`UX-005`)

```text
impedidos(recurso) = autores da avaliação que fundamentou os Resultados alcançados
                   ∪ quem consolidou esses Resultados
                   ∪ quem emitiu o ato publicado, quando o objeto é publicação
                   ∪ quem praticou a publicação atacada
                   ∪ quem tem Impedimento declarado na Inscrição

sinal ⇔ ∃ recurso pendente : membros_ativos(processo) − impedidos(recurso) = ∅
```

**O que a fórmula não diz, e a mensagem também não pode dizer:** que ninguém pode julgar. A
titularidade da permissão de julgar não é determinável pelo sistema (`T-004`), e por isso o sinal se
limita ao que verifica — a comissão inteira impedida (`FR-030a`).

---

## 4. Invariantes do modelo de leitura

1. Nenhuma escrita, em nenhuma tabela.
2. Nenhum campo derivado é gravado, nem em cache persistente.
3. Toda forma que carrega data carrega o Edital a que ela pertence.
4. `medida` é par completo ou ausente.
5. Rascunho nunca compõe total de submetidas, em nenhuma forma.
6. Sinal sem destino alcançável não é montado.
