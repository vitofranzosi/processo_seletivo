# Decisão — a conclusão de Avaliação deixa de pressupor nota

**Tomada em 03/09/2026**, a partir da análise de três Editais reais do Cefor/Ifes: o 35/2026
(Especialização, sorteio), o 57/2026 (Aperfeiçoamento, sorteio, unificado em dois cursos) e o
14/2026 (Orientador de TFC, prova de títulos e entrevista).

É **mudança de requisito da 012**, e não spec nova. Não reabre nada que a 012 tenha recusado: o
§21 recusa barema estruturado, avaliação cega, distribuição automática, recurso e comunicação, e
**não menciona conclusão não-numérica** em lugar nenhum. A 012 não decidiu que concluir exige
nota; ela só nunca teve pela frente uma Etapa que não pontuasse.

## O que os Editais reais mostraram

Nos Editais 35 e 57, a Etapa central não pontua. Depois do sorteio, a comissão faz a **análise
documental** dos candidatos sorteados e o que ela produz é `deferido` ou `indeferido` — nunca uma
nota. É dela que dependem a chamada do próximo da fila, a matrícula e a suplência.

O mesmo vale para a verificação da autodeclaração e para a elegibilidade PcD, e vale para o
Edital 14 no que ele chama de conferência da documentação.

> Uma Etapa avaliada por pessoas nem sempre produz número. Fingir que produz — deferido igual a 1,
> indeferido igual a 0 — inventaria uma grandeza que o Edital não publicou, e a 013 teria de
> descobrir, por convenção não escrita, que aquele `0` elimina.

É o mesmo erro de categoria que a 012 já recusa em outro lugar: heteroidentificação não é
"avaliação com nota zero".

## O que está no caminho, exatamente

A obrigatoriedade da nota não é um campo frouxo. Ela está gravada em três níveis, de propósito:

1. `ck_avaliacao_concluida_completa` exige `pontuacao__isnull=False` para o estado `CONCLUIDA`
   (`avaliacoes/models.py`). O comentário acima dela é explícito sobre a intenção: *"O que
   'concluída' significa, dito no banco."*
2. `ConclusaoAvaliacao.pontuacao` é **não-nulável**, e essa tabela está em `TABELAS_APPEND_ONLY`
   (`seguranca/papeis.py`), onde o papel de runtime recebe `SELECT` e `INSERT` e nada mais, com
   trigger como segunda camada.
3. `pontuacao.normalizar()` recusa `None` e `""` com *"Informe a pontuação."*

Relaxar um campo não resolve isso e não deveria resolver. **O invariante forte se mantém; o que
muda é o que ele afirma.**

## A decisão

> Uma Avaliação concluída precisa possuir uma **conclusão completa segundo a forma que a Etapa
> publicou**. Completa deixa de significar "tem nota" e passa a significar "tem o que a forma
> exige".

```text
ConclusaoAvaliacao
├── forma:     PONTUADA | DECISORIA     ← publicada pela Etapa, gravada na linha
├── pontuacao: decimal(7,4)             ← exigida quando PONTUADA, ausente quando DECISORIA
├── sentido:   FAVORAVEL | DESFAVORAVEL ← exigido quando DECISORIA, ausente quando PONTUADA
└── parecer
```

### Por que a forma vive na própria linha

Duas razões, e a segunda é a que importa mais.

**A constraint precisa continuar sendo do banco.** Uma `CheckConstraint` do PostgreSQL não
referencia outra tabela. Se a regra fosse "válida segundo o instrumento da Etapa", ela deixaria de
ser verificável na linha e voltaria para a aplicação — justamente a camada de que a 012 desconfiou
ao escrever `ck_avaliacao_concluida_completa`. Com a forma na linha, a regra volta a ser local:

```sql
forma = 'PONTUADA'  → pontuacao NOT NULL AND sentido IS NULL
forma = 'DECISORIA' → sentido   NOT NULL AND pontuacao IS NULL
```

**A conclusão é histórica.** Se uma Retificação mudar a natureza da Etapa depois, a conclusão
antiga precisa continuar interpretável sob a regra que a governou. É exatamente por isso que a
conclusão já guarda `versao`, e não consulta a versão vigente (FR-071). Gravar a forma não é
duplicação — é a mesma preservação de sentido, no padrão que a 012 estabeleceu.

### Por que o sentido é binário e neutro, e o rótulo é dado publicado

`Deferido/Indeferido`, `Apto/Inapto`, `Elegível/Não elegível` e `Classificado/Desclassificado` são
o mesmo juízo com o vocabulário que cada Edital escolheu. Um enum com os quatro pares teria oito
valores para dois significados e cresceria a cada Edital novo — que é hard-code de regra sujeita a
legislação, vedado pelas Restrições do Domínio.

O domínio guarda `FAVORAVEL | DESFAVORAVEL`. **O rótulo que o avaliador lê na tela e que o PDF
imprime vem da Etapa publicada**, pelo mesmo padrão de `ModalidadeConcorrencia`, onde `code` e
`name` são dados e não enumeração.

Nos três Editais analisados, toda decisão de avaliação é binária. O "parcialmente deferido"
aparece só em **recurso**, que é outra feature e outro conceito.

### P-006 continua de pé

*"Avaliar não é decidir"* permanece intacto, e é por isso que o campo **não** se chama `decisão`.
O que a pessoa registra continua sendo *o que ela afirmou sobre aquela inscrição* — duas análises
documentais podem afirmar sentidos opostos, e resolver isso é da 013, exatamente como média,
quórum e divergência já eram. A 012 não ganhou poder de decidir; ela ganhou uma segunda forma de
afirmar.

Pelo mesmo motivo o campo não se chama `tipo_resultado`: `Resultado` passa a ser a entidade da
013, e o Princípio I não admite o termo significando duas coisas.

## Consequências de implantação

- Migração sobre `avaliacoes_conclusaoavaliacao`, que é append-only por privilégio e por trigger.
  O papel de migração altera esquema; o de runtime não. **As linhas existentes são todas
  `PONTUADA`** e continuam completas sob a regra nova — nenhuma conclusão histórica perde
  validade.
- `ck_avaliacao_concluida_completa` passa a alternar por forma, e continua sendo o que define
  `CONCLUIDA` no banco.
- `pontuacao.normalizar()` deixa de ser o único caminho de conclusão; a recusa *"Informe a
  pontuação."* passa a valer só na forma pontuada.
- A forma é propriedade **publicada** da Etapa, então entra no conteúdo canônico e sobe o
  `SCHEMA_VERSION` (hoje 5), pelo mesmo caminho de D-001. Regra que afeta direito não pode ser
  configuração de tela (P-007).
- A Mesa passa a apresentar dois instrumentos conforme a forma. O parecer segue obrigatório onde
  já era, e a razão não muda: é ele que o recurso terá contra o que responder.

## Limite nomeado, e deliberadamente não construído agora

Existe uma terceira forma plausível que **nenhum dos três Editais exercita**: conceito ordinal
(A/B/C, "aprovado com distinção", menção de prova didática), comum em stricto sensu e em concurso
docente. Ela não é pontuada nem binária.

Não construímos para ela. `forma` é justamente o ponto de extensão por onde ela entraria, e
inventá-la agora seria desenhar a estrutura antes da regra que a consome. **Quando aparecer um
Edital que a use, esta decisão é o lugar onde a terceira forma se acrescenta.**

## O que esta decisão não é

Não é barema. Pontuação por critério, com itens e limites por item, continua fora da 012 pela
recusa do §21, que segue valendo por inteiro. A conclusão decisória não pontua nada — ela é o que
permite **não** pontuar.
