# Data Model: revisão de compatibilidade 012–013

**Revisão**: `012-013-revisao-formas-de-conclusao` | **Data**: 2026-09-03

Só o **delta**. Os modelos completos estão em
[`012/data-model.md`](../012-mesa-de-avaliacao/data-model.md) e
[`013/data-model.md`](../013-consolidacao-resultado-etapa/data-model.md), e nada aqui os substitui.

---

## 1. Os dois enums, e onde eles vivem

```text
Forma    PONTUADA | DECISORIA        ← publicada pela Etapa, gravada em cada conclusão
Sentido  FAVORAVEL | DESFAVORAVEL    ← o que o avaliador afirma na forma decisória
```

Os dois vivem em `backend/processo_seletivo/avaliacoes/domain/formas.py`, e o lugar segue a direção
de dependência que já existe: `resultados` importa de `avaliacoes`, nunca o contrário, e os dois
enums descrevem **a conclusão**, que é conceito da 012. `editais` importa `Forma` no **modelo** de
elaboração, para as `choices` — a alternativa seria uma terceira cópia dos literais —, e mantém a
tupla literal no **validador** do conteúdo publicado, onde o que se confere é a string do snapshot.

`Sentido` é do **domínio** e nunca carrega vocabulário de Edital. O que o avaliador lê na tela e o
que o documento imprime são `rotuloFavoravel` e `rotuloDesfavoravel`, publicados pela Etapa — o
mesmo padrão de `ModalidadeConcorrencia`, onde código e denominação são dados e não enumeração.

Quatro pares reais colapsam nos mesmos dois valores: Deferido/Indeferido, Apto/Inapto, Elegível/Não
elegível, Classificado/Desclassificado.

## 2. Conteúdo publicado — `stages[]` na versão canônica 6

| campo | tipo | nulo | aplicabilidade |
|---|---|---|---|
| `forma` | `"PONTUADA" \| "DECISORIA"` | **não**¹ | sempre |
| `rotuloFavoravel` | string | sim | obrigatório em `DECISORIA`, proibido em `PONTUADA` |
| `rotuloDesfavoravel` | string | sim | obrigatório em `DECISORIA`, proibido em `PONTUADA` |
| `minimumScore` | decimal canônico | sim | valor admitido em `PONTUADA`; **nulo** em `DECISORIA` |
| `maximumScore` | decimal canônico | sim | valor admitido em `PONTUADA`; **nulo** em `DECISORIA` |
| `weight` | decimal canônico | sim | **inalterado**: descreve a composição entre Etapas, não a conclusão |
| `eliminatory` | bool | não | **inalterado** — e, na forma decisória, é ele que dá consequência ao sentido |

**"Proibido" significa nulo, e nunca ausente**: toda chave da Etapa está sempre presente no
conteúdo publicado, e o que a forma decisória proíbe é o **valor**, não a chave.

¹ **Na versão 6, `forma` é obrigatória e não nula.** Admitir nulo criaria duas grafias canônicas
para a mesma versão, e a versão existe para identificar *uma* forma. A ausência é lida como
`PONTUADA` apenas em **conteúdo anterior à v6** (012, FR-120), e quem a interpreta é o leitor legado.
A elevação sempre escreve o literal, e nenhum snapshot v5 cru chega ao validador de publicação — ele
roda sobre a projeção de elaboração, sobre a publicação e sobre a consolidação de Retificação, e nos
três o conteúdo já está na forma vigente (TR-003).

No modelo de **elaboração**, `forma` não é anulável e tem `default="PONTUADA"` — o que também alcança
as Etapas já em rascunho, que sem isso ficariam impublicáveis (TR-003).

**Elevação, degrau novo** (TR-001, TR-002):

```text
5 → 6   forma := "PONTUADA"   rotuloFavoravel := null   rotuloDesfavoravel := null
```

## 3. `avaliacoes.Avaliacao` — delta

| campo | mudança |
|---|---|
| `forma` | **novo**, `blank`/`default=""`, `choices=Forma` — gravado na conclusão, lido da versão validada |
| `sentido` | **novo**, `blank`/`default=""`, `choices=Sentido` — e `choices` **não** basta: a constraint nomeia os dois valores |
| `pontuacao` | inalterado no tipo; deixa de ser exigido pela conclusão em toda forma |

**Vazio, e não nulo**: o projeto não usa `NULL` em campo de texto, e a mesma constraint já compara
`~Q(concluida_por="")`.

**Backfill obrigatório**: o PostgreSQL valida a tabela inteira ao criar a constraint, e toda
avaliação já concluída reprovaria sem forma.

```text
estado = CONCLUIDA  → forma := 'PONTUADA'
estado = RASCUNHO   → forma permanece vazia
```

Os rascunhos ficam sem forma de propósito: ela é lida e gravada **no ato de concluir**, e carimbá-la
no nascimento afirmaria uma regra que a conclusão ainda vai ler (TR-004a).

`ck_avaliacao_concluida_completa` passa a alternar:

```text
RASCUNHO   → sem exigência
CONCLUIDA  → versao ∧ concluida_em ∧ concluida_por
             ∧ ( forma = PONTUADA  ∧ pontuacao ≠ NULL ∧ sentido = '' )
             ∨ ( forma = DECISORIA ∧ pontuacao = NULL ∧ sentido ∈ {FAVORAVEL, DESFAVORAVEL} )
```

**Vazio, e não `NULL`, para os dois campos de texto**: é a convenção do projeto, e a mesma constraint
já comparava `~Q(concluida_por="")`. E o sentido é restrito **aos dois valores**, não apenas a "não
vazio": `TextChoices` valida no formulário e no `full_clean` e **não cria constraint**, de modo que
um `INSERT` cru com valor inventado entraria — e `_consequencia_decisoria` trata tudo que não é
`DESFAVORAVEL` como favorável, o que habilitaria a inscrição por um valor que ninguém escreveu. É o
mesmo motivo pelo qual `ck_resultado_consequencia` existe na 013 desde sempre.

Inalterados: `uq_avaliacao_concluida_por_pessoa`, a tripla copiada da Atribuição, `revision`, a
autoria histórica em `identity_subject` / `concluida_por`.

**`forma` é a única cópia nova.** Máxima, mínima e caráter continuam proibidos por FR-072: eles não
participam de nenhuma verificação local, e a forma participa da que define "concluída".

## 4. `avaliacoes.ConclusaoAvaliacao` — delta

| campo | mudança |
|---|---|
| `forma` | **novo**, `NOT NULL` depois do backfill |
| `sentido` | **novo**, vazio por padrão; a constraint o restringe aos dois valores na forma decisória |
| `pontuacao` | `NOT NULL` → **anulável**, governada pela constraint que alterna |

Append-only por privilégio (`TABELAS_APPEND_ONLY`) e por trigger. **O `DROP TRIGGER` previsto não
foi necessário**: o preenchimento vem do `DEFAULT` do `ADD COLUMN`, que é DDL e não dispara trigger
de linha, e `preserve_default=False` remove o default em seguida para que ele não afirme, para
sempre, que conclusão sem forma é pontuada.

Todas as linhas existentes recebem `forma = 'PONTUADA'` — aqui não há rascunho, porque uma conclusão
preservada é sempre uma conclusão — e continuam completas sob a regra nova: **nenhuma conclusão
histórica perde validade**.

## 5. `resultados.ResultadoEtapa` — delta

| campo | mudança |
|---|---|
| `forma` | **novo**, `NOT NULL` depois do backfill |
| `sentido` | **novo**, vazio por padrão; restrito aos dois valores na forma decisória |
| `pontuacao` | `NOT NULL` → **anulável** |
| `consequencia` | inalterado — `HABILITADA \| ELIMINADA` nas duas formas |
| `motivo` | inalterado no tipo; passa a citar o **rótulo publicado** na forma decisória |

Todas as linhas existentes recebem `forma = 'PONTUADA'`, pelo mesmo caminho e pela mesma razão.

`check_stage_result_source()` passa a conferir três campos contra a Avaliação fonte,
**incondicionalmente** — a spec da 013 foi emendada para dizer isso, porque a primeira redação dela
falava em alternar por forma:

```sql
fonte.forma     IS DISTINCT FROM NEW.forma      → erro
fonte.pontuacao IS DISTINCT FROM NEW.pontuacao  → erro
fonte.sentido   IS DISTINCT FROM NEW.sentido    → erro
```

Comparar os três incondicionalmente é mais forte e mais simples que alternar: formas iguais tornam a
alternância redundante, e formas divergentes já reprovam no primeiro teste (TR-006).

Inalterados: `uq_resultado_inscricao_etapa`, `resultado_etapa_append_only`, a autoria histórica, e o
fato de o Resultado não guardar norma — a versão é alcançada por `avaliacao__versao`.

## 6. `editais` — elaboração

A Etapa de elaboração ganha três campos, que o `edital_snapshot` transcreve para o conteúdo publicado:

| campo | nulo | default |
|---|---|---|
| `forma` | não | `"PONTUADA"` — o mesmo padrão de `eliminatory` e `classificatory` |
| `rotulo_favoravel` | sim | nenhum |
| `rotulo_desfavoravel` | sim | nenhum |

O default de `forma` não é conveniência: é o que mantém publicável todo Edital **já em elaboração**,
cujas Etapas nasceriam sem forma e falhariam a validação de publicação. Os rótulos não têm default,
porque neles o "não se aplica" é real (D-008.2).

Na **entrada da API**, `forma` omitida vale `PONTUADA` e `forma: null` explícito é recusado; o
caminho de rascunho não escreve `None` no lugar da ausência, sob pena de contornar o default do
modelo. Nenhum outro modelo de elaboração muda.

## 7. Transições de estado

Nenhuma nova. `RASCUNHO → CONCLUIDA → RASCUNHO` (reabertura) continua sendo o ciclo inteiro da
Avaliação, e `ResultadoEtapa` continua nascendo e não mudando. O que mudou é **o que uma transição
para `CONCLUIDA` exige**, e isso é constraint, não estado.

## 8. Regras de validação, por camada

| camada | o que ela garante |
|---|---|
| `editais/domain/validation.py` | forma é um dos dois valores; rótulos obrigatórios em `DECISORIA` e proibidos em `PONTUADA`; mínima e máxima proibidas em `DECISORIA` |
| `avaliacoes/domain` | o envio traz o campo da forma publicada, e não o da outra; parecer obrigatório em `DESFAVORAVEL` |
| banco — `avaliacoes` | conclusão completa segundo a forma, nas duas tabelas |
| banco — `resultados` | Resultado idêntico à fonte em forma, pontuação e sentido |
| `resultados/domain/regra.py` | a Etapa tem regra suficiente; a consequência é lida, nunca inferida |
| `resultados/domain/compatibilidade.py` | a forma histórica é a forma vigente |
| `openapi.yaml` (001) | a forma publicada é a que o domínio transcreve — conferido por `test_forma_publicada.py` |
