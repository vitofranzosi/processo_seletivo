# Fase 1 — Modelo de dados

**Feature**: 018 — Recursos e Superação de Resultados · **Spec**: [spec.md](./spec.md) ·
**Pesquisa**: [research.md](./research.md)

Três tabelas novas, três colunas e um valor de enum no `ResultadoEtapa`, uma coluna na
`PublicacaoResultado`, e um campo no conteúdo publicado. Nada mais.

---

## 1. A cadeia inteira, depois desta feature

```text
Avaliacao ──┐
            ├──▶ ResultadoEtapa ◀── DecisaoRecurso ◀── JuizoDeAdmissibilidade ◀── Recurso
Ocorrência ─┘        │  ▲                                                          │
                     │  └── resultado_anterior (sucessão, append-only) ────────────┤
                     ▼                                                             │
              AtoDeOrdenacao ──▶ PublicacaoResultado ◀───────────────────────────── ┘
                                        (objeto atacado, o outro dos dois)
```

O `Recurso` aponta para **um** dos dois objetos atacados; a `DecisaoRecurso` é citada pelo
`ResultadoEtapa` sucessor. É essa dupla direção que T-001 discute.

---

## 2. `recursos.Recurso` — a peça interposta

Append-only. Nasce e não muda.

| campo | tipo | observação |
|---|---|---|
| `id` | UUID | |
| `protocolo` | texto único | `REC-2026-XXXXXXXX`, alfabeto compartilhado com a Inscrição (T-012) |
| `inscricao` | FK `Inscricao`, PROTECT | a Inscrição de quem recorre; determina Edital e Processo |
| `interposto_por` | texto | `identity_subject`, e não vínculo: a autoria é histórica |
| `interposto_em` | instante | |
| `fundamentacao` | texto | obrigatório e não vazio (FR-006) |
| `publicacao_atacada` | FK `PublicacaoResultado`, anulável, PROTECT | um dos dois |
| `resultado_atacado` | FK `ResultadoEtapa`, anulável, PROTECT | o outro dos dois |
| `versao` | FK `VersaoConsolidada`, PROTECT | a norma vigente no instante da interposição |
| `janela_abriu_em` | instante, anulável | nulo quando não havia janela computável |
| `janela_fecha_em` | instante, anulável | idem — os dois juntos são o "havia prazo, e era este" |

**Constraints**

```text
uq_recurso_protocolo             UNIQUE(protocolo)
ck_recurso_objeto_unico          (publicacao_atacada IS NULL) <> (resultado_atacado IS NULL)
ck_recurso_fundamentacao         fundamentacao <> ''
ck_recurso_janela_completa       (abriu IS NULL) = (fecha IS NULL)
uq_recurso_por_publicacao        UNIQUE(inscricao, publicacao_atacada) WHERE publicacao NOT NULL
uq_recurso_por_resultado         UNIQUE(inscricao, resultado_atacado)  WHERE resultado NOT NULL
```

As duas últimas são a FR-011 no banco: um recurso por titular e objeto, pendente ou já decidido. A
unicidade é por `(inscricao, objeto)` e não por `(interposto_por, objeto)` porque a Inscrição **é** a
titularidade — e é ela que o contrato do portal verifica.

**Por que a janela é gravada, e não recalculada.** Recalcular na leitura responderia com a norma de
hoje sobre um ato de ontem. A FR-024 exige que a peça registre se estava dentro da janela computável
**quando existia**, e é proveniência: a mesma razão pela qual `ResultadoEtapa.versao` é campo, e não
caminho até a fonte.

**Por que não há coluna de situação.** D-010: a situação deriva de quais atos alcançaram a peça.
Uma coluna seria estado a manter coerente onde a existência de linha já responde.

---

## 3. `recursos.JuizoDeAdmissibilidade` — receber não é admitir

Append-only.

| campo | tipo | observação |
|---|---|---|
| `id` | UUID | |
| `recurso` | FK `Recurso`, PROTECT | |
| `admitido` | booleano | |
| `motivo` | texto | obrigatório nas duas direções: admitir também é ato motivado |
| `decidido_por` | texto | `identity_subject` |
| `decidido_em` | instante | |

```text
uq_juizo_por_recurso   UNIQUE(recurso)
ck_juizo_motivo        motivo <> ''
```

Um por recurso. A segunda tentativa concorrente perde no banco, e recebe recusa por estado obsoleto
— não por leitura prévia.

---

## 4. `recursos.DecisaoRecurso` — o julgamento do mérito

Append-only, e fonte jurídica citada pelo Resultado sucessor.

| campo | tipo | observação |
|---|---|---|
| `id` | UUID | |
| `recurso` | FK `Recurso`, PROTECT | |
| `especie` | enum | `INDEFERIDO` · `CORRECAO_FIXADA` · `REAVALIACAO_DETERMINADA` · `PROVIDENCIA_A_JUSANTE` |
| `motivacao` | texto | obrigatório, sempre |
| `versao` | FK `VersaoConsolidada`, PROTECT | a norma sob a qual se decidiu |
| `decidido_por` | texto | `identity_subject` |
| `decidido_em` | instante | |
| `resultado_protegido` | FK `ResultadoEtapa`, anulável, PROTECT | o vigente do par quando se decidiu (T-011) |
| `etapa_id` | UUID, anulável | o par que a decisão alcança, quando alcança um |
| `consequencia` | enum, anulável | o que a decisão declara, na correção fixada |
| `forma`, `pontuacao`, `sentido` | conforme a Etapa, anuláveis | a conclusão fixada, quando há grandeza |

```text
uq_decisao_por_recurso        UNIQUE(recurso)
ck_decisao_motivacao          motivacao <> ''
ck_decisao_correcao_completa  especie = 'CORRECAO_FIXADA'
                              ⟹ consequencia IS NOT NULL AND etapa_id IS NOT NULL
                                 AND resultado_protegido IS NOT NULL
ck_decisao_reavaliacao        especie = 'REAVALIACAO_DETERMINADA'
                              ⟹ etapa_id IS NOT NULL AND resultado_protegido IS NOT NULL
                                 AND consequencia IS NULL
ck_decisao_sem_efeito         especie IN ('INDEFERIDO','PROVIDENCIA_A_JUSANTE')
                              ⟹ consequencia IS NULL AND resultado_protegido IS NULL
```

**As quatro espécies são um enum, e a providência não.** O que a espécie discrimina é o **efeito** —
e o efeito é o que o esquema e a aferição de definitividade precisam distinguir. Qual providência a
decisão determina é fundamentação escrita: o cumprimento não é verificado por espécie (D-009,
T-010), e um vocabulário a mais só teria de responder o que fazer quando a providência real fosse
outra.

**`resultado_protegido` é FK, e não derivado.** Derivá-lo exigiria perguntar "qual era o vigente
naquele instante", que é consulta temporal sobre uma cadeia. Uma FK responde em uma junção e é
honesta: a decisão de fato se referiu àquele Resultado (T-011).

---

## 5. `resultados.ResultadoEtapa` — o que muda

**Campos**

```text
+ resultado_anterior   FK(self, null, PROTECT, related_name="sucessor")
+ motivo_da_superacao  TextField(blank, default="")
+ decisao              FK("recursos.DecisaoRecurso", null, PROTECT, related_name="resultados")
  origem               AVALIACAO | OCORRENCIA | RECURSO        ← terceiro valor
  avaliacao            continua OneToOne anulável — nula também quando origem = RECURSO
```

**Constraints**

```text
- uq_resultado_inscricao_etapa
+ uq_resultado_raiz_por_par      UNIQUE(inscricao, etapa_id) WHERE resultado_anterior IS NULL
+ uq_resultado_sucessor_unico    UNIQUE(resultado_anterior)  WHERE resultado_anterior IS NOT NULL
+ ck_superacao_com_motivo        resultado_anterior IS NULL OR motivo_da_superacao <> ''
+ ck_sucessor_cita_decisao       (anterior IS NULL AND decisao IS NULL)
                              OR (anterior IS NOT NULL AND decisao IS NOT NULL)

~ ck_resultado_origem
    (origem='AVALIACAO'  AND avaliacao IS NOT NULL AND forma <> '' AND decisao IS NULL)
 OR (origem='OCORRENCIA' AND avaliacao IS NULL     AND forma =  '' AND decisao IS NULL)
 OR (origem='RECURSO'    AND avaliacao IS NULL     AND decisao IS NOT NULL)

~ ck_resultado_completo_por_forma   passa a depender de origem × forma (T-002)
```

**`ck_sucessor_cita_decisao` é bidirecional de propósito**: sucessor sem decisão seria superação sem
fundamento, e raiz com decisão seria consolidação disfarçada de julgamento.

**Note o que não muda.** `avaliacao` continua `OneToOne` e continua anulável, e o Resultado por
recurso não a cita. É isso que impede, **no banco**, a Avaliação sintética que a decisão C recusou:
não há como gravar uma linha que se diga `RECURSO` e aponte para uma `Avaliacao`.

**Trigger `resultado_etapa_coerente`, recriada por inteiro** no molde da `0004`, com dois ramos
novos e o nome preservado:

```text
origem = RECURSO:
  não cita Avaliação nenhuma;
  a decisão citada está deferida, e é da mesma Inscrição, do mesmo Edital e da mesma Etapa;
  a consequência da linha é a que a decisão declarou;
  a versão citada é a da decisão, e pertence a este Edital.

qualquer origem, com resultado_anterior NOT NULL:
  o superado é do mesmo (inscricao_id, etapa_id, edital_id);
  o superado ainda não tem sucessor;      ← redundante com a constraint, e barato: a constraint
                                            responde à concorrência, a trigger à leitura
  NEW.consolidado_em > superado.consolidado_em.
```

**Migration `resultados/0005`: nenhuma linha é escrita.** Toda linha existente tem
`resultado_anterior IS NULL` e já satisfaz a unicidade de raiz; as três colunas nascem nulas. A
trigger `resultado_etapa_append_only` **não é desligada** — a `0004` precisou desligá-la porque
preencheu `versao` linha a linha, e aqui não há preenchimento.

---

## 6. `divulgacao.PublicacaoResultado` — uma coluna

| campo | tipo | observação |
|---|---|---|
| `prazo_encerrado_declarado_em` | instante, anulável | |
| `prazo_encerrado_declarado_por` | texto, em branco por padrão | |
| `prazo_encerrado_fundamento` | texto, em branco por padrão | |

```text
ck_declaracao_completa   os três presentes, ou os três ausentes
```

Preenchidos **no nascimento**, como todo o resto da linha — a tabela é append-only e nasce completa.
Exigidos quando a natureza é `DEFINITIVA` e não há janela computável; recusados quando há janela
computável, porque declarar o que o sistema verifica seria pedir à pessoa que respondesse pelo que a
máquina sabe (FR-086).

---

## 7. Conteúdo publicado — o degrau 8

Dentro de cada marco classificatório:

```json
"appealWindow": {
  "admits": true,
  "durationDays": 5,
  "unit": "DIAS_CORRIDOS"
}
```

`null` ou ausente significa **janela não declarada** — e não janela de zero dias.

```text
SCHEMA_VERSION      7 → 8
DEGRAUS_DE_MARCO    {8: {"appealWindow": None}}       ← nível novo na elevação (T-007)
```

`unit` tem um valor admissível na V1, e continua sendo campo publicado porque a frase "5 dias
corridos" é normativa e aparece no documento. Declaração em outra unidade é recusada na publicação,
nomeando a razão (FR-021).

---

## 8. Situações derivadas — o que **não** vira coluna

| situação | derivada de |
|---|---|
| aguardando admissibilidade | `Recurso` sem `JuizoDeAdmissibilidade` |
| inadmitido | juízo com `admitido = false` — terminal |
| aguardando julgamento | admitido, sem `DecisaoRecurso` |
| decidido | decisão existente |
| reavaliação determinada, não cumprida | decisão `REAVALIACAO_DETERMINADA` sem sucessor do par posterior a ela |
| providência não cumprida | decisão `PROVIDENCIA_A_JUSANTE` e o ato publicado ainda é o reconhecido viciado |
| Resultado vigente | `sucessor__isnull=True` |
| reabilitada por recurso | Resultado vigente que é sucessor, com consequência habilitante |
| janela aberta | função pura da publicação âncora e da norma |

Nove situações, zero colunas de estado. É o mesmo idioma de `PENDENTE`/`CONSOLIDADO` na 013 e da
vigência na 015 e na 017.

---

## 9. Política de privilégios e teste estrutural

```text
seguranca/papeis.py   TABELAS_APPEND_ONLY += recursos_recurso,
                                             recursos_juizodeadmissibilidade,
                                             recursos_decisaorecurso

tests/migrations/     APPS += "recursos"
                      TRIGGERS_POR_APP["recursos"] = (recurso_append_only,
                                                      juizo_de_admissibilidade_append_only,
                                                      decisao_recurso_append_only,
                                                      recurso_coerente)
```

`TRIGGERS_POR_APP["resultados"]` **não** ganha nome novo: `resultado_etapa_coerente` é recriada, e a
trigger é a mesma — foi assim que a `0004` acrescentou o ramo da Ocorrência.

O teste estrutural de vigência (T-004) é artefato próprio desta feature: ele varre
`ResultadoEtapa.objects` no código de aplicação e falha em uso não declarado, com duas exceções
explícitas — a reprodução histórica e a consulta do histórico do par.
