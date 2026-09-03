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

`Sentido` é do **domínio** e nunca carrega vocabulário de Edital. O que o avaliador lê na tela e o
que o documento imprime são `rotuloFavoravel` e `rotuloDesfavoravel`, publicados pela Etapa — o
mesmo padrão de `ModalidadeConcorrencia`, onde código e denominação são dados e não enumeração.

Quatro pares reais colapsam nos mesmos dois valores: Deferido/Indeferido, Apto/Inapto, Elegível/Não
elegível, Classificado/Desclassificado.

## 2. Conteúdo publicado — `stages[]` na versão canônica 6

| campo | tipo | nulo | aplicabilidade |
|---|---|---|---|
| `forma` | `"PONTUADA" \| "DECISORIA"` | sim¹ | sempre |
| `rotuloFavoravel` | string | sim | obrigatório em `DECISORIA`, proibido em `PONTUADA` |
| `rotuloDesfavoravel` | string | sim | obrigatório em `DECISORIA`, proibido em `PONTUADA` |
| `minimumScore` | decimal canônico | sim | admitido em `PONTUADA`, proibido em `DECISORIA` |
| `maximumScore` | decimal canônico | sim | admitido em `PONTUADA`, proibido em `DECISORIA` |
| `weight` | decimal canônico | sim | **inalterado**: descreve a composição entre Etapas, não a conclusão |
| `eliminatory` | bool | não | **inalterado** — e, na forma decisória, é ele que dá consequência ao sentido |

¹ Nulo ou ausente significa `PONTUADA` (012, FR-120). A elevação escreve o valor literal; o consumo
interpreta a ausência. As duas leituras vêm da mesma função.

**Elevação, degrau novo** (TR-001, TR-002):

```text
5 → 6   forma := "PONTUADA"   rotuloFavoravel := null   rotuloDesfavoravel := null
```

## 3. `avaliacoes.Avaliacao` — delta

| campo | mudança |
|---|---|
| `forma` | **novo**, anulável, `choices=Forma` — gravado na conclusão, lido da versão validada |
| `sentido` | **novo**, anulável, `choices=Sentido` |
| `pontuacao` | inalterado no tipo; deixa de ser exigido pela conclusão em toda forma |

`ck_avaliacao_concluida_completa` passa a alternar:

```text
RASCUNHO   → sem exigência
CONCLUIDA  → versao ∧ concluida_em ∧ concluida_por ∧ forma
             ∧ ( forma = PONTUADA  ∧ pontuacao ≠ NULL ∧ sentido = NULL )
             ∨ ( forma = DECISORIA ∧ sentido  ≠ NULL ∧ pontuacao = NULL )
```

Inalterados: `uq_avaliacao_concluida_por_pessoa`, a tripla copiada da Atribuição, `revision`, a
autoria histórica em `identity_subject` / `concluida_por`.

**`forma` é a única cópia nova.** Máxima, mínima e caráter continuam proibidos por FR-072: eles não
participam de nenhuma verificação local, e a forma participa da que define "concluída".

## 4. `avaliacoes.ConclusaoAvaliacao` — delta

| campo | mudança |
|---|---|
| `forma` | **novo**, `NOT NULL` depois do backfill |
| `sentido` | **novo**, anulável |
| `pontuacao` | `NOT NULL` → **anulável**, governada pela constraint que alterna |

Append-only por privilégio (`TABELAS_APPEND_ONLY`) e por trigger. Migração em três passos, com
`DROP TRIGGER` / backfill / `CREATE TRIGGER` na mesma transação (TR-005).

Todas as linhas existentes recebem `forma = 'PONTUADA'` e continuam completas sob a regra nova —
**nenhuma conclusão histórica perde validade**.

## 5. `resultados.ResultadoEtapa` — delta

| campo | mudança |
|---|---|
| `forma` | **novo**, `NOT NULL` depois do backfill |
| `sentido` | **novo**, anulável |
| `pontuacao` | `NOT NULL` → **anulável** |
| `consequencia` | inalterado — `HABILITADA \| ELIMINADA` nas duas formas |
| `motivo` | inalterado no tipo; passa a citar o **rótulo publicado** na forma decisória |

`check_stage_result_source()` passa a conferir três campos contra a Avaliação fonte, sem alternar:

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

A Etapa de elaboração ganha `forma`, `rotulo_favoravel` e `rotulo_desfavoravel`, que o
`edital_snapshot` transcreve para o conteúdo publicado. Nenhum outro modelo de elaboração muda.

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
