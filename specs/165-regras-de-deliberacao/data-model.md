# Data Model: As regras de deliberação dos pareceres

As decisões que justificam cada forma estão em [research.md](research.md).

## EtapaAvaliacao (elaboração) — coluna nova

| Campo | Tipo | Regra |
|---|---|---|
| `regra_de_deliberacao` | texto, escolha fechada, vazio = não declarada | `MAIORIA`, `UNANIMIDADE_PARA_O_FAVORAVEL`, `UNANIMIDADE_PARA_O_DESFAVORAVEL`; `CheckConstraint` literal (`ck_etapa_regra_de_deliberacao`) |

Migration `editais/0031_regra_de_deliberacao`. Não é tabela append-only.

## Conteúdo publicado — degrau 24

Em cada item de `stages`:

| Chave | Valores | Leitura do `null` |
|---|---|---|
| `deliberationRule` | `"MAJORITY"`, `"UNANIMOUS_FOR_FAVORABLE"`, `"UNANIMOUS_FOR_UNFAVORABLE"`, `null` | sem regra: a Etapa colegiada é impedida na consolidação, como hoje |

A elevação de toda versão anterior escreve `null` (`publicacoes/domain/elevacao.py`, `DEGRAUS[24]`).
Contrato de mutabilidade: `("stages", "deliberationRule")` retificável, com as recusas de
`retificacoes.py` (T-004).

**Etapa colegiada** = forma `DECISORIA`, `evaluationsPerRegistration` > 1 e `deliberationRule` não
nulo.

## ResultadoEtapa — origem e campos novos

| Campo | Tipo | Regra |
|---|---|---|
| `origem` | + `DELIBERACAO` | — |
| `regra_de_deliberacao` | texto, vazio fora da deliberação | a grafia publicada da regra aplicada |
| `favoraveis` | inteiro, nulo fora da deliberação | ≥ 0 |
| `desfavoraveis` | inteiro, nulo fora da deliberação | ≥ 0 |

`CheckConstraint` `ck_resultado_deliberacao`:

```text
origem = DELIBERACAO  →  avaliacao NULL, forma = DECISORIA, sentido ≠ '', pontuacao NULL,
                         regra ≠ '', favoraveis NOT NULL, desfavoraveis NOT NULL,
                         favoraveis + desfavoraveis ≥ 2
origem ≠ DELIBERACAO  →  regra = '', favoraveis NULL, desfavoraveis NULL
```

A `ck_resultado_origem` de hoje ganha o ramo novo. `versao`: a vigente no ato, deste Edital.

## ParecerDaDeliberacao — tabela nova, append-only

`resultados_parecer_da_deliberacao`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | — |
| `resultado` | FK `ResultadoEtapa`, `PROTECT` | origem `DELIBERACAO` |
| `avaliacao` | FK `Avaliacao`, `PROTECT`, **única** | concluída; mesma inscrição, Edital e Etapa do Resultado; não citada por `ResultadoEtapa.avaliacao` |

Gatilhos (migration `resultados/0008_deliberacao`):

- `parecer_da_deliberacao_append_only`: recusa `UPDATE` e `DELETE`;
- `parecer_da_deliberacao_coerente` (`BEFORE INSERT`): as condições da tabela acima;
- `resultado_etapa_coerente`, reescrito: o ramo `DELIBERACAO` e a recusa de `avaliacao` já citada
  em `ParecerDaDeliberacao`;
- `resultado_deliberado_completo` (`CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED`, `AFTER
  INSERT` em `ResultadoEtapa`): ao fim da transação, os pareceres ligados somam
  `favoraveis + desfavoraveis`, e os de sentido favorável somam `favoraveis`.

Entra em `TABELAS_APPEND_ONLY` (`M` 59 → 60).

## ExposicaoAoParecer — tabela nova, append-only

`avaliacoes_exposicao_ao_parecer`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | — |
| `edital` | FK `Edital`, `PROTECT` | — |
| `etapa_id` | UUID | a identidade da Etapa no conteúdo publicado |
| `inscricao` | FK `Inscricao`, `PROTECT` | — |
| `pessoa` | texto (o `subject`) | — |
| `registrada_em` | instante | — |

`UniqueConstraint` (`edital`, `etapa_id`, `inscricao`, `pessoa`). Gravada por
`INSERT ... ON CONFLICT DO NOTHING`. Gatilho append-only (`exposicao_ao_parecer_append_only`).
Migration `avaliacoes/0006_exposicao_ao_parecer`. Entra em `TABELAS_APPEND_ONLY` (`M` 60 → **61**).

Guarda o fato, nunca o conteúdo entregue (FR-7082, FR-054 da `012`).

## Estados da inscrição na Etapa colegiada (prontidão)

```text
participante
  ├─ menos de N pareceres elegíveis ──► NAO_CONSOLIDAVEL      ("faltam k de N pareceres",
  │                                                            contada em aguardando_pareceres)
  ├─ N pareceres, algum incompatível ─► NAO_CONSOLIDAVEL      (frase de hoje)
  ├─ N pareceres compatíveis ─────────► PRONTA
  └─ mais de N ───────────────────────► NAO_CONSOLIDAVEL      (pareceres demais)
PRONTA ──(consolidação)──► CONSOLIDADA (Resultado DELIBERACAO + N ParecerDaDeliberacao)
CONSOLIDADA ──(correção fixada)──► sucessor RECURSO (sem pareceres)
CONSOLIDADA ──(reavaliação determinada)──✗ recusada antes de gravar
```

## Deliberacao (valor de domínio, sem tabela)

`resultados/domain/deliberacao.py`: `regra`, `sentidos` (a lista na ordem de conclusão),
`favoraveis`, `desfavoraveis`, `sentido` (o deliberado), `pareceres` (as identidades), `versao_id` (a
vigente). Expõe `forma = DECISORIA`, `pontuacao = None` e `sentido`, para `regra.consequencia` a ler
como lê uma conclusão.
