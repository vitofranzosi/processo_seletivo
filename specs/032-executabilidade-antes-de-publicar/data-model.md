# Data Model — 032 · Executabilidade antes de publicar

**Nenhuma migration. Nenhum campo novo no conteúdo normativo. Nenhum degrau de elevação.**

Isso não é economia: é o que a feature **é**. Ela não acrescenta nada ao que o Edital declara — ela
confere o que ele já declara, e imprime no documento o que já está no snapshot e não chegava ao
papel. Uma migration aqui seria sinal de que o escopo escorregou.

O que muda de forma é de três espécies, e nenhuma delas é persistência.

---

## 1. Achados de validação — quatro novos, nenhuma estrutura nova

`ValidationFinding(severity, code, message, path)` permanece como está. Os quatro achados entram
como valores, não como forma.

| Código | Severidade | `path` | Requisito |
|---|---|---|---|
| `profile_without_milestone` | `BLOCKING_ERROR` | `/profiles/id=…/classificationMilestones` | `FR-457` |
| `milestone_without_cut_rule` | `WARNING` | `/profiles/id=…/classificationMilestones/id=…/cutRule` | `FR-461` |
| `drawn_milestone_without_method` | `BLOCKING_ERROR` | `/profiles/id=…/classificationMilestones/id=…/drawMethod` | `FR-467` |
| `reserved_row_without_ordering` | `WARNING` | `/profiles/id=…/vacancyTable` | `FR-470` |

Os quatro caminhos já roteiam para a etapa certa pelo `_destino` existente — `classificacao` para os
três primeiros, `perfis` para o quarto. **Nenhuma entrada nova em `DESTINO_POR_CODIGO`**, e é isso
que faz `FR-458` não custar infraestrutura.

**Invariantes que a forma impõe:**

- os dois impeditivos são emitidos **somente** quando `ato == ATO_DE_PUBLICACAO`;
- os dois avisos também recebem `ato`, para não encher a Retificação do acervo de avisos sobre o que
  ele já publicou;
- `milestone_without_cut_rule` distingue **ausência de `cutRule`** de **`cutRule` que declara não
  governar Etapa alguma** (`FR-224` da `014`), e só a primeira o dispara.

---

## 2. Seção do marco no documento publicado — pares novos, ordem declarada

A seção de cada marco é hoje uma lista de pares. A feature acrescenta pares e condiciona dois dos
existentes. **A ordem abaixo é a ordem impressa**, e faz parte do contrato.

| Par | Quando aparece | De onde vem |
|---|---|---|
| **Ordem** | sempre que o marco declara a forma | `orderProduction` do marco |
| **Combinação** | só quando a ordem **não** nasce de sorteio | como hoje |
| **Normalização** | só quando a ordem **não** nasce de sorteio | como hoje |
| **Arredondamento** | como hoje | como hoje |
| **Sorteio — algoritmo** | quando a ordem nasce de sorteio | `marcos.metodo_que_governa` |
| **Sorteio — fonte da semente** | idem | idem |
| **Sorteio — ocorrência** e **quando** | idem | idem |
| **Sorteio — derivação da ocorrência** | idem | idem |
| **Sorteio — normalização da semente** | idem | idem |
| **Sorteio — se a ocorrência faltar** | idem | idem |
| **Sorteio — origem do método** | quando a ordem nasce de sorteio | "comum a este Edital" ou "próprio deste marco, divergente do comum" |
| **Recurso** | como hoje | como hoje |
| **Corte** | como hoje | como hoje |

**Marco do acervo que não declara `orderProduction`** não ganha o par **Ordem** e é impresso
exatamente como hoje. É a mesma leitura que a `030` fixou: a ausência significa o que sempre
significou, e sorteia quem declara método.

**Os rótulos não são inventados aqui.** Os sete campos do método já estão nomeados em português em
`CAMPOS_DO_METODO`; o documento os reusa, para que a norma publicada e a tela de composição digam a
mesma coisa com as mesmas palavras — Princípio I.

---

## 3. Leitura da ocupação — um campo, e não um estado novo

O recorte hoje carrega `estado`, com quatro valores nomeados em `ocupacao/domain/nomes.py`:
`CURRENT`, `OBSOLETE`, `NOT_APPRAISED`, `NO_VACANCY_TABLE`.

**Acrescenta-se um booleano, e não um quinto valor.** A leitura de cada recorte ganha:

| Campo | Significado |
|---|---|
| `apuravel` | falso quando o marco daquele Perfil não emite ordem naquele recorte — hoje, todo recorte de lista reservada em marco que não sorteia |
| `faixaDisponivel` | falso quando o marco não declara regra de corte alguma |

**Por que campo e não valor de enum.** Um recorte reservado em marco computado **é**, de fato,
`NOT_APPRAISED` — e continuará sendo. Acrescentar um quinto valor obrigaria todo consumidor que
hoje distingue os quatro a aprender um quinto, e a `016` registra por escrito que colapsar estados é
o que a `UX-032` proíbe — o contrário também vale: multiplicá-los sem necessidade. Um campo é
aditivo: quem não o lê continua lendo o que lia.

**O que os dois campos governam.** Em `ocupacao.html`, `apuravel` retira o botão "Apurar a ocupação
deste recorte" (`FR-472`) e `faixaDisponivel` retira "Pedir a faixa seguinte com este déficit"
(`FR-463`). Nos dois casos **a razão ocupa o lugar do botão** — não um `disabled`, não um alerta
depois do clique. É o padrão que o produto adotou em três telas no PR #120 e que a auditoria
registrou como padrão a preservar.

---

## Entidades que a feature **lê** e não muda

- **Marco classificatório** — `orderProduction`, `drawMethod`, `cutRule`, `stages`.
- **Método do sorteio** — os sete campos, próprios do marco ou comuns do Edital.
- **Regra de corte** — e, dentro dela, a declaração de qual Etapa governa **ou** de que não governa
  nenhuma.
- **Quadro de vagas** — a linha, o `modalityId` e a quantidade. O `NULL` é a ampla concorrência.
- **Perfil de Vaga** — `generalCompetitionModalityId`, para não confundir a Modalidade "AC"
  declarada com o recorte `NULL` que o ato computado emite.
