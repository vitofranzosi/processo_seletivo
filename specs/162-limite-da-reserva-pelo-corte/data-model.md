# Data Model: O limite do cadastro de reserva lido do corte

**Feature**: [spec.md](spec.md) · **Research**: [research.md](research.md)

**Nenhuma tabela, nenhuma coluna; uma migration.** O número do cadastro deixa de ser dado gravado em
Edital novo e passa a ser derivado do conteúdo. A `editais/0028` afrouxa a metade limitada de
`ck_perfil_reserve_limit_compatible`: a `0001` exigia `reserve_limit` não nulo em `LIMITED`, e agora o
limitado admite nulo — todo Perfil gravado depois da `162` — e o número que o rascunho salvo antes
guarda. Só afrouxa: nenhuma linha existente viola a condição nova. *O plano dizia "nenhuma
migration"; a constraint apareceu na primeira medição da implementação.* A contagem de tabelas
append-only (`59`) não muda.

---

## O que já existe e continua

### `PerfilVaga` (`editais/models/perfis.py`)

| Campo | Antes | Depois |
|---|---|---|
| `reserve_type` | `NONE` / `LIMITED` / `UNLIMITED`, declarado | igual; continua não retificável |
| `reserve_limit` | inteiro ≥ 0 obrigatório em `LIMITED`; `NULL` nos outros | **sempre `NULL` em gravação nova** (T-003). A coluna fica: rascunhos antigos a usam, e a advertência da FR-6940 a lê |

### O conteúdo publicado (`profiles[*]`)

| Chave | Antes | Depois |
|---|---|---|
| `reserveType` | declarado | igual |
| `reserveLimit` | o número digitado em `LIMITED`; `null` nos outros | `null` em todo Perfil publicado depois desta feature; o número digitado continua no conteúdo dos publicados antes, que é o que os marca como **legado** (T-002) |

A forma do snapshot não muda: a chave continua presente, sempre, como `test_forma_do_snapshot` exige.

### A regra de corte (`classificationMilestones[*].cutRule`)

Sem mudança. Passa a ser a fonte do número. `targetCount` e `surplusCount` continuam retificáveis;
`targetKind`, `governedStage` e `continuation`, não.

---

## O valor derivado: `Cadastro` (`editais/domain/cadastro_de_reserva.py`)

Imutável, sem banco. Os campos estão na T-001 da pesquisa.

```text
do_perfil(perfil) -> Cadastro
  marcos_que_convocam = [m for m in perfil.classificationMilestones
                         if marco_que_le(perfil, m.id) is None and m.cutRule]
  listas = perfil.vacancyTable  or  [linha geral com perfil.immediateVacancies]
  para cada marco que convoca, para cada lista:
      alcance = vagas_da_linha + excedente           se alvo do quadro
              = alvo + excedente                     se alvo fixo
      numero  = alcance - vagas_da_linha
  por_lista       = os números do primeiro marco que convoca
  alcance_cresce  = algum marco que convoca admite continuação
  admite_empate   = algum marco que convoca tem tieOutcome = ADMITS_SURPLUS
  legado          = reserveType == LIMITED e reserveLimit inteiro
```

### Invariantes conferidas na publicação (`incoerencias(ato)`)

| Invariante | Requisito | Quando |
|---|---|---|
| `LIMITED` não legado ⇒ nenhum marco que convoca admite continuação | FR-6933 | publicação e Retificação |
| `UNLIMITED` com corte no marco que convoca ⇒ todos admitem continuação | FR-6934 | publicação |
| `LIMITED` não legado ⇒ ao menos um marco que convoca com corte | FR-6935 | publicação |
| `LIMITED` não legado ⇒ `numero > 0` em toda lista | FR-6936, FR-6951 | publicação e Retificação |
| `LIMITED` não legado com dois ou mais marcos que convocam ⇒ mesmo `numero` por lista | FR-6939 | publicação e Retificação |

### Estados de um Perfil limitado

```text
rascunho com número digitado ──(próxima gravação pela tela)──▶ rascunho sem número
         │                                                          │
         └──(publicação: o número não entra no conteúdo)──▶ publicado, derivado
publicado antes desta feature ───────────────────────────────▶ legado (para sempre, mesmo retificado)
```
