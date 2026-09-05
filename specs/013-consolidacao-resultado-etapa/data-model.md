# Phase 1 — Modelo de dados: Consolidação do Resultado da Etapa

**Feature**: 013 | **Spec**: [spec.md](./spec.md) | **Pesquisa**: [research.md](./research.md)

Uma tabela nova, num app novo. Nada mais é criado, e nada existente é alterado em forma — a 013
acrescenta colunas a **nenhum** modelo da 012 e não toca conteúdo publicado (FR-041).

---

## `ResultadoEtapa` — app `resultados`

A consequência administrativa de consolidar a Avaliação elegível de uma inscrição numa Etapa. Nasce
e não muda mais.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | `UUIDField`, pk, `default=uuid4` | identidade estável; não autoriza (princípio I) |
| `inscricao` | `FK(Inscricao, PROTECT)` | a inscrição consolidada; `PROTECT` porque Resultado é histórico |
| `edital` | `FK(Edital, PROTECT)` | redundante via inscrição, e presente pelo mesmo motivo da 012: a consulta é por Edital e Etapa, e a junção extra a cada listagem é o custo que se evita |
| `etapa_id` | `UUIDField` | identidade da Etapa no **conteúdo publicado**, não FK — ver abaixo |
| `avaliacao` | `OneToOne(Avaliacao, PROTECT)` | a Avaliação fonte; `PROTECT` impede que apagar a fonte deixe o Resultado órfão |
| `pontuacao` | `DecimalField(7,4)`, não nula | cópia exata da pontuação da fonte (FR-016) |
| `consequencia` | `CharField(20)`, choices | `HABILITADA` \| `ELIMINADA` |
| `motivo` | `TextField`, não vazio | a causa da consequência, em texto exibível: "pontuação inferior à nota mínima da Etapa (55,0000 < 60,0000)" |
| `consolidado_em` | `DateTimeField` | instante do ato, do `now` da transação |
| `consolidado_por` | `CharField(255)`, não vazio | `identity_subject` de quem consolidou; identificador estável, não vínculo (FR-025) |

### Por que `etapa_id` não é chave estrangeira

A mesma razão da 011 e da 012, e ela continua valendo: existe Etapa real no Edital vigente sem linha
de elaboração para uma FK apontar, porque a Retificação sabe acrescentar item a coleção com chave e
não escreve de volta em `editais`. Consolidar contra a linha de elaboração consolidaria contra um
registro que a Retificação altera depois.

### Por que a versão **não** é copiada — **revertido por D-1 em 04/09/2026**

> **A versão passou a ser campo do Resultado.** O argumento abaixo tinha duas metades, e as duas
> deixaram de valer quando o Resultado passou a existir sem Avaliação: não há junção a economizar
> quando não há junção possível, e a contradição que ele temia é impedida pela trigger, que é como
> as outras quatro já são. O texto fica como registro do que se sabia; a redação vigente está na
> seção **A extensão D-1** ao final deste documento, e o argumento inteiro na §2 da spec.

Uma redação anterior materializava `versao` no Resultado, argumentando que a divergência seria
impossível porque as linhas de origem são imutáveis. O argumento não se sustenta: imutabilidade
impede que uma linha correta se torne incorreta depois, e não impede que uma combinação errada seja
gravada uma vez — que, num registro append-only, é a pior das duas, porque fica incorrigível.

A versão é alcançada pela fonte, `avaliacao__versao`, no mesmo `select_related` que já traz a
Avaliação. Não há junção extra a economizar, e há uma forma a menos de o Resultado se contradizer.

O que também **não** se copia: nota mínima, pontuação máxima e caráter da Etapa. A versão os
reproduz, e duplicá-los criaria a segunda fonte divergente que o princípio II proíbe — a mesma
decisão que a 012 tomou em `avaliacoes/models.py:101`.

### O que sobra de redundante, e como fica garantido

`inscricao`, `edital`, `etapa_id` e `pontuacao` continuam materializados, cada um por um motivo que
não é economia de junção:

- `inscricao` e `etapa_id` sustentam a unicidade que é a invariante 1 da spec, e ela precisa ser
  constraint;
- `edital` acompanha `etapa_id` pelo padrão que `AlocacaoEtapa` já usa (`comissoes/models.py:81`) e
  sustenta o escopo das listagens;
- `pontuacao` descreve o **Resultado**, não a fonte: a V1 a copia, e a feature de combinação não
  necessariamente copiará.

Nenhum deles é verificado por promessa de código. A trigger de coerência abaixo confere, no
`INSERT`, que os quatro correspondem à Avaliação fonte.

### Constraints

```text
uq_resultado_inscricao_etapa   UNIQUE (inscricao_id, etapa_id)
ck_resultado_consequencia      consequencia IN ('HABILITADA', 'ELIMINADA')
ck_resultado_motivo_presente   motivo <> ''
ck_resultado_autor_presente    consolidado_por <> ''
```

E uma trigger, porque `CHECK` não atravessa tabelas em PostgreSQL:

```text
resultado_etapa_coerente   BEFORE INSERT
  a Avaliação fonte pertence à mesma inscrição, à mesma Etapa e ao mesmo Edital;
  NEW.pontuacao é igual à pontuação da fonte;
  a fonte está CONCLUIDA;
  a Atribuição que a governa está ATIVA.
  RAISE EXCEPTION 'stage result does not match its source evaluation'
```

A quarta linha é a que fecha a invariante 2. Sem ela, a trigger provaria que o Resultado aponta
para a Avaliação certa, e não que essa Avaliação **estava elegível** — elegibilidade, na 012, é
conclusão sob Atribuição ativa. Um Resultado nascido de conclusão sob Atribuição já inativada
ficaria consolidado para sempre, porque append-only não corrige, só congela.

E a verificação é barata porque a junção já é obrigatória: `Avaliacao.atribuicao` é `OneToOne`, e é
a **Atribuição** que carrega `inscricao_id`, `etapa_id` e `edital_id`. A trigger junta uma vez e lê
os quatro campos de coerência mais o `ativo` na mesma linha.

Note o instante: `ativo` é conferido **no `INSERT`**, e é isso que a invariante afirma. Impedimento
posterior inativa a Atribuição sem tornar o Resultado inválido — a fonte *era* elegível quando
consolidada, e passou a ser contestada depois (FR-031, FR-032).

A unicidade é a invariante 1 da spec dita no banco, e é ela — não o botão da tela, não o bloqueio —
que torna FR-024 verdadeiro sob qualquer concorrência e qualquer número de reenvios. O `OneToOne` em
`avaliacao` acrescenta a recíproca: uma Avaliação fundamenta no máximo um Resultado.

### Índices

```text
ix_resultado_edital_etapa      (edital_id, etapa_id)
```

Um só, e ele serve às consultas quentes: as eliminadas em Etapas anteriores e as habilitadas na
imediatamente anterior (T-005), as contagens de prontidão (T-008) e a listagem de Resultados de uma
Etapa. A unicidade já indexa
`(inscricao_id, etapa_id)`, que é a consulta do detalhe.

### Imutabilidade

Três camadas, como `ConclusaoAvaliacao` e `VersaoConsolidada` (T-002):

1. `save()` recusa quando não é criação; `delete()` recusa sempre;
2. trigger `resultado_etapa_append_only` `BEFORE UPDATE OR DELETE`, criada na migration ao lado da
   trigger de coerência — as duas são o mesmo raciocínio em tempos diferentes: uma impede que a
   linha mude, a outra impede que ela nasça errada, e sem a segunda a primeira apenas congela o erro;
3. `resultados_resultadoetapa` acrescentada a `TABELAS_APPEND_ONLY` em `seguranca/papeis.py`, o que
   retira `UPDATE` e `DELETE` do papel de runtime.

---

## O que **não** é persistido

| Conceito | Como existe |
|---|---|
| `PENDENTE` | ausência de linha para o par participante+Etapa (D-006) |
| `CONSOLIDADO` | existência da linha |
| Participação na Etapa | conjunto derivado: submetidas do Edital, menos as eliminadas em qualquer Etapa anterior, menos — quando a imediatamente anterior já produziu Resultado — as sem `HABILITADA` nela (D-003) |
| Prontidão | classificação derivada por participante: elegibilidade, compatibilidade, regra disponível, Resultado existente. Calculada em `resultados/application/prontidao.py` a cada leitura, nunca gravada |
| Desfecho do lote | `IdempotencyRecord.result_payload`, que a 012 já criou; não é entidade do domínio |

Persistir qualquer um deles criaria estado a manter a cada gravação — a razão pela qual a 012 deixou
os filtros da Mesa derivados (`selectors.py:207`), e a que D-006 herda.

---

## Relação com o que já existe

```text
Inscricao ──┐
            ├─< ResultadoEtapa >──1:1── Avaliacao ──> VersaoConsolidada
Edital ─────┘
                a norma histórica é alcançada pela fonte,
                e não duplicada no Resultado
```

Nenhuma coluna é acrescentada a `Inscricao`, `Avaliacao`, `Atribuicao`, `Impedimento`,
`EtapaAvaliacao`, `Publicacao` ou `VersaoConsolidada`. O acoplamento com a 012 é de leitura —
`avaliacoes_elegiveis` — e de guard — duas funções que passam a perguntar por Resultado antes de
mutar a fonte.

---

## Migrations

| App | Migration | Conteúdo |
|---|---|---|
| `resultados` | `0001_initial` | o modelo, as constraints, o índice, a trigger de coerência e a trigger append-only |

**Nenhuma migration em `editais`, `publicacoes` ou `auditoria`.** A 013 não cria incremento canônico
(FR-041), não altera conteúdo publicado e não precisa de campo novo na trilha: `RegistroAuditoria` já
tem ator, operação, agregado, correlação e chave, e `IdempotencyRecord.result_payload` já guarda
desfecho de lote desde a 012.

---

## A extensão D-1 — o Resultado sem Avaliação

*Acrescentada em 04/09/2026. O que está acima descreve a 013 como ela foi entregue; esta seção diz o
que D-1 mudou, e por quê. Nada aqui é migration fora de `resultados`, e nada toca conteúdo
publicado.*

### Campos

| Campo | Antes | Depois |
|---|---|---|
| `origem` | — | `CharField(20)`, choices `AVALIACAO` \| `OCORRENCIA`, obrigatório |
| `avaliacao` | `OneToOne(Avaliacao, PROTECT)` obrigatório | **anulável**: `NOT NULL` quando a origem é Avaliação, `NULL` quando é Ocorrência |
| `versao` | — (alcançada por `avaliacao__versao`) | `FK(VersaoConsolidada, PROTECT)`, **obrigatória sempre** — a norma que fundamentou o desfecho |
| `forma` | `CharField(20)`, choices | **vazia** na Ocorrência: não houve conclusão sob forma nenhuma |

`pontuacao` e `sentido` já eram anuláveis desde a revisão de D-008, e na Ocorrência os dois vêm
vazios: o Edital não publicou grandeza para quem não compareceu, e a linha não pode afirmar uma.

### Constraints

```text
ck_resultado_origem            (origem = 'AVALIACAO'  AND avaliacao_id IS NOT NULL AND forma <> '')
                            OR (origem = 'OCORRENCIA' AND avaliacao_id IS NULL     AND forma  = '')

ck_resultado_completo_por_forma  ganha um terceiro ramo, feito de ausências:
                                 forma = '' AND pontuacao IS NULL AND sentido = ''
```

`ck_resultado_origem` existe porque `null=True` sozinho seria uma permissão solta: uma linha
`AVALIACAO` sem fonte, ou uma `OCORRENCIA` com fonte, atravessaria — e a trigger, que confere a
fonte, não tem o que conferir num nulo que a coluna passou a admitir.

### A trigger, recriada por inteiro

```text
resultado_etapa_coerente   BEFORE INSERT

  origem = OCORRENCIA:
    a linha NÃO cita Avaliação nenhuma;
    a Versão Consolidada citada pertence a ESTE Edital.
    RAISE 'stage result by occurrence must not cite a source evaluation'
    RAISE 'stage result cites a consolidated version of another edital'

  origem = AVALIACAO:
    tudo o que ela já conferia — inscrição, Etapa, Edital, forma, pontuação, sentido,
    estado CONCLUIDA e Atribuição ATIVA — mais
    NEW.versao_id é igual ao da fonte.
    RAISE 'stage result does not match its source evaluation'
```

A conferência da versão no ramo por Ocorrência é a **única** que sobra ali: sem Avaliação, a versão
não vem copiada de lugar nenhum — quem escreve a linha a escolhe. Sem ela, o Resultado poderia
afirmar ter sido fundamentado por norma que nunca governou este certame, e I-2 seria letra morta
neste ramo.

### Leitura

`avaliacao__versao` sai dos seletores: a norma vem de `ResultadoEtapa.versao`. E `versao` fica
**fora** do `select_related` — ela carrega o Edital inteiro em JSON mais os bytes canônicos, e
trazê-la por linha da página não mudaria a contagem de consultas, de modo que nenhum teste de custo
denunciaria. `vigencias_das_versoes` a resolve uma vez por versão distinta, como
`conteudos_das_versoes` já fazia do outro lado.

### Migrations

| App | Migration | Conteúdo |
|---|---|---|
| `resultados` | `0004_resultado_por_ocorrencia` | `origem` com `DEFAULT` que sai do esquema; `versao` anulável → preenchida por `Subquery` sobre `avaliacao__versao` → obrigatória; `avaliacao` anulável; `forma` com branco; as duas constraints; a trigger recriada; e a guarda de reversão |

O preenchimento de `versao` é o único passo destas migrations que **desliga
`resultado_etapa_append_only`** pelo tempo em que corre: não há valor constante a oferecer como
`DEFAULT`, e um `UPDATE` linha a linha numa tabela append-only é exatamente o que aquela trigger
existe para recusar. A migração pode fazê-lo e o runtime não — o papel de migração é o dono da
tabela, e o de runtime nem `UPDATE` tem.

---

## Regras de validação, e onde vivem

| Regra | Camada | Onde |
|---|---|---|
| Consequência a partir de nota mínima e caráter | domínio puro | `resultados/domain/regra.py` |
| Compatibilidade normativa entre versão e vigente | domínio puro | `resultados/domain/compatibilidade.py` |
| Etapa anterior e Etapas anteriores | domínio puro | `resultados/domain/progressao.py` |
| Conjuntos de eliminadas e de habilitadas | consulta | `resultados/application/selectors.py` |
| Classificação de prontidão do participante | aplicação | `resultados/application/prontidao.py` |
| Elegibilidade da Avaliação | herdada | `avaliacoes/application/selectors.py` |
| Quantidade prevista e teto | herdadas | `avaliacoes/domain/previsao.py` |
| Unicidade do par | banco | constraint |
| Coerência com a fonte | banco | trigger `BEFORE INSERT` |
| Imutabilidade | banco + modelo + privilégio | trigger, `save`/`delete`, `TABELAS_APPEND_ONLY` |

As três funções de domínio não tocam banco e são testáveis com dicionários — que é o que faz a
tabela-verdade de T-003 caber num teste unitário em vez de num cenário de aceitação.
