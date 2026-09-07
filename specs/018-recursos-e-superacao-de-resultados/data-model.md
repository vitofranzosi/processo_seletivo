# Fase 1 — Modelo de dados

**Feature**: 018 — Recursos e Superação de Resultados · **Spec**: [spec.md](./spec.md) ·
**Pesquisa**: [research.md](./research.md)

Quatro tabelas novas, três colunas e um valor de enum no `ResultadoEtapa`, três colunas na
`PublicacaoResultado`, e um campo no conteúdo publicado. **Quatro migrations.**

---

## 1. A cadeia inteira, depois desta feature

```text
Avaliacao ──┐
            ├──▶ ResultadoEtapa ◀── DecisaoRecurso ◀── JuizoDeAdmissibilidade ◀── Recurso
Ocorrência ─┘        │  ▲                  ▲                                       │
                     │  └── resultado_anterior (sucessão, append-only)             │
                     ▼                     │                                       │
              AtoDeOrdenacao ──────────────┘                                       │
                     │      CitacaoDeDecisao (o ato cita a decisão)                │
                     ▼                                                             │
             PublicacaoResultado ◀───────────────────────────────────────────────── ┘
                                        (objeto atacado, o outro dos dois)
```

O `Recurso` aponta para **um** dos dois objetos atacados. A `DecisaoRecurso` é citada pelo
`ResultadoEtapa` sucessor, e — quando determina providência a jusante — pelo `AtoDeOrdenacao` que a
executa. É essa dupla direção que T-001 discute e que T-015 estende.

---

## 2. `recursos.Recurso` — a peça interposta

Append-only. Nasce e não muda.

| campo | tipo | observação |
|---|---|---|
| `id` | UUID | |
| `protocolo` | texto, `unique=True` | `REC-2026-XXXXXXXX`, alfabeto compartilhado com a Inscrição (T-012) |
| `inscricao` | FK `Inscricao`, PROTECT | a Inscrição de quem recorre; determina Edital e Processo |
| `interposto_por` | texto | `identity_subject`, e não vínculo: a autoria é histórica |
| `interposto_em` | instante | |
| `fundamentacao` | texto | obrigatório e não vazio (FR-006) |
| `publicacao_atacada` | FK `PublicacaoResultado`, anulável, PROTECT | um dos dois |
| `resultado_atacado` | FK `ResultadoEtapa`, anulável, PROTECT | o outro dos dois |
| `versao` | FK `VersaoConsolidada`, PROTECT | a norma vigente no instante da interposição |
| `janela_abriu_em` | instante, anulável | nulo quando não havia janela computável |
| `janela_fecha_em` | instante, anulável | idem — os dois juntos são o "havia prazo, e era este" |

**Constraints — 6.** `unique=True` no protocolo **é** unicidade de banco, ainda que declarada no
campo e não em `Meta.constraints`; contá-la de fora seria subdeclarar o que o esquema garante.

| nome | o que garante |
|---|---|
| `uq_recurso_protocolo` (via `unique=True`) | o protocolo é único no certame |
| `ck_recurso_objeto_unico` | `(publicacao_atacada IS NULL) <> (resultado_atacado IS NULL)` — exatamente um |
| `ck_recurso_fundamentacao` | `fundamentacao <> ''` |
| `ck_recurso_janela_completa` | `(janela_abriu_em IS NULL) = (janela_fecha_em IS NULL)` |
| `uq_recurso_por_publicacao` | `UNIQUE(inscricao, publicacao_atacada) WHERE publicacao_atacada IS NOT NULL` |
| `uq_recurso_por_resultado` | `UNIQUE(inscricao, resultado_atacado) WHERE resultado_atacado IS NOT NULL` |

As duas últimas são a FR-011 no banco: um recurso por titular e objeto, pendente ou já decidido. A
unicidade é por `(inscricao, objeto)` e não por `(interposto_por, objeto)` porque a Inscrição **é** a
titularidade — e é ela que o contrato do portal verifica.

**Por que a janela é gravada, e não recalculada.** Recalcular na leitura responderia com a norma de
hoje sobre um ato de ontem. A FR-024 exige que a peça registre se estava dentro da janela computável
**quando existia**: é proveniência, pela mesma razão que `ResultadoEtapa.versao` é campo e não
caminho até a fonte.

**Por que não há coluna de situação.** D-010: a situação deriva de quais atos alcançaram a peça.

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

**Constraints — 2**: `uq_juizo_por_recurso` (`UNIQUE(recurso)`) e `ck_juizo_motivo`
(`motivo <> ''`).

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

**Constraints — 9**

| nome | o que garante |
|---|---|
| `uq_decisao_por_recurso` | `UNIQUE(recurso)` |
| `ck_decisao_motivacao` | `motivacao <> ''` |
| `ck_decisao_especie` | a espécie está entre as quatro. `TextChoices` valida no formulário e **não** cria constraint: num registro append-only a espécie inventada entraria uma vez e ficaria. É a mesma razão de `ck_resultado_consequencia` na 013 |
| `ck_decisao_correcao_completa` | `CORRECAO_FIXADA ⟹ consequencia, etapa_id e resultado_protegido presentes` |
| `ck_decisao_reavaliacao` | `REAVALIACAO_DETERMINADA ⟹ etapa_id e resultado_protegido presentes, consequencia nula` |
| `ck_decisao_sem_efeito` | `INDEFERIDO ou PROVIDENCIA_A_JUSANTE ⟹ consequencia e resultado_protegido nulos` |
| `ck_decisao_consequencia` | a consequência está vazia ou no vocabulário — `choices` não protege o banco |
| `ck_decisao_conclusao_por_forma` | forma, pontuação e sentido formam conclusão válida, como no Resultado |
| `ck_decisao_sem_grandeza_residual` | só `CORRECAO_FIXADA` carrega grandeza; as demais não deixam pontuação pendurada |

**As quatro espécies são um enum, e a providência não.** O que a espécie discrimina é o **efeito**, e
é o efeito que o esquema e a aferição de definitividade precisam distinguir. Qual providência a
decisão determina é fundamentação escrita: o cumprimento é verificado pela **citação** do ato que a
executa (T-015), e não por espécie.

**`resultado_protegido` é FK, e não derivado.** Derivá-lo exigiria perguntar "qual era o vigente
naquele instante", que é consulta temporal sobre uma cadeia. Uma FK responde em uma junção e é
honesta: a decisão de fato se referiu àquele Resultado (T-011).

---

## 5. `classificacao.CitacaoDeDecisao` — a citação que o ato carrega

Append-only. **Não é ato administrativo e não é registro de cumprimento**: é proveniência do
`AtoDeOrdenacao`, do mesmo tipo de `motivo_da_sucessao`, declarada por quem emite, no ato de emitir.
Não tem autoridade, instante nem motivo próprios (T-015).

*Chamava-se `CumprimentoDeProvidencia`, e o nome mentia sobre o que a linha afirma: ela registra que
um ato **citou** uma decisão, não que a providência foi cumprida. Cumprimento é conclusão, e depende
de publicação — ver §5.2.*

| campo | tipo | observação |
|---|---|---|
| `id` | UUID | |
| `ato` | FK `AtoDeOrdenacao`, PROTECT | o ato emitido em cumprimento |
| `decisao` | FK `"recursos.DecisaoRecurso"`, PROTECT | referência tardia, como em `resultados` |

**Constraint — 1**: `uq_citacao_ato_decisao` (`UNIQUE(ato, decisao)`) — um ato não cita a mesma
decisão duas vezes, e nada além disso.

### 5.1 Por que **não** existe `UNIQUE(decisao)`

Uma redação anterior tinha as duas, com a segunda justificada como "a decisão é cumprida uma vez".
Ela estava errada em três frentes, e cada uma sozinha bastaria:

1. **Contradizia a FR-089.** Unicidade global faria a citação, sozinha, encerrar a pendência — e a
   FR-089 exige ato **publicado**. Citar é intenção; publicar é o remédio.
2. **Criava beco.** Emitido `C2` citando a decisão, e ficando `C2` obsoleto antes de ser publicado —
   por Retificação ou por outro Resultado superado —, o sucessor `C3` **não poderia recitar** a
   mesma decisão. A providência ficaria eternamente pendente, e a definitiva do marco, impedida
   para sempre. É exatamente o beco que a decisão do cumprimento derivado existia para evitar.
3. **Impedia a pertinência múltipla.** Uma decisão cuja providência é normativa — o erro está na
   norma, e o remédio é Retificação — alcança **todos** os marcos que a regra retificada governa.
   Cada um emite o seu ato sucessor, e cada um precisa citar a mesma decisão.

### 5.2 A regra de cumprimento, e ela é por Marco

```text
cumprida_para(decisao, ato_candidato) =
      existe CitacaoDeDecisao(ato_candidato, decisao)
   OU existe CitacaoDeDecisao(A, decisao), com A do MESMO marco do ato_candidato
      e A já publicado
```

O primeiro ramo é o ato que executa o remédio agora: ele não é impedido pela pendência que ele
próprio cura. O segundo é o remédio **já executado e divulgado**: publicado o ato citante, um
sucessor posterior emitido por razão alheia não reabre a pendência.

**"Do mesmo marco" não é detalhe.** Publicado o ato citante de `M1`, a providência continua pendente
para `M2`, porque o remédio de `M2` não foi executado. Apurar globalmente liberaria a definitiva de
`M2` pelo trabalho feito em `M1`.

**Recitação é legítima e esperada.** Enquanto nenhum ato citante for publicado, qualquer sucessor do
marco pode citar a decisão de novo. É o que impede o beco de 5.1.2.

**Por que uma linha por par, e não uma FK única no ato.** Dois deferimentos com providência sobre o
mesmo marco são alcançáveis, e uma FK única obrigaria a emitir um ato por decisão — a "sucessão que
não sucedeu nada" que a D-007 da 017 critica. Um ato cita quantas decisões cumprir.

**Por que mora em `classificacao`, e não em `recursos`.** A citação é do ato, e é `emitir_ordem` quem
a grava, na mesma transação em que grava o ato. Pô-la em `recursos` faria `classificacao` escrever
dentro de outro app no seu próprio comando.

---

## 6. `resultados.ResultadoEtapa` — o que muda

**Campos**

```text
+ resultado_anterior   FK(self, null, PROTECT, related_name="sucessor")
+ motivo_da_superacao  TextField(blank, default="")
+ decisao              FK("recursos.DecisaoRecurso", null, PROTECT, related_name="resultados")
  origem               AVALIACAO | OCORRENCIA | RECURSO        ← terceiro valor
  avaliacao            continua OneToOne anulável — nula quando origem = RECURSO
```

### 6.1 A matriz de origem — quatro linhas, e só quatro

Esta é a parte que uma redação anterior deste documento errou, e o erro tornava a FR-068
**impossível**: ela exigia `decisao IS NULL` no ramo `AVALIACAO`, enquanto
`ck_sucessor_cita_decisao` exige `decisao IS NOT NULL` em todo sucessor. Um sucessor por reavaliação
não podia existir.

A matriz correta distingue **raiz de sucessor**, e é esta:

| linha | `origem` | `avaliacao` | `decisao` | `resultado_anterior` | quem a cria |
|---|---|---|---|---|---|
| raiz por avaliação | `AVALIACAO` | presente | **ausente** | ausente | consolidação ordinária |
| **sucessor por reavaliação** | `AVALIACAO` | presente | **presente** | presente | consolidação em cumprimento de decisão (FR-068) |
| raiz por ocorrência | `OCORRENCIA` | ausente | ausente | ausente | constatação da presidência |
| sucessor por recurso | `RECURSO` | ausente | presente | presente | deferimento com correção fixada |

**Constraints**

```text
- uq_resultado_inscricao_etapa
+ uq_resultado_raiz_por_par      UNIQUE(inscricao, etapa_id) WHERE resultado_anterior IS NULL
+ uq_resultado_sucessor_unico    UNIQUE(resultado_anterior)  WHERE resultado_anterior IS NOT NULL
+ ck_superacao_com_motivo        resultado_anterior IS NULL OR motivo_da_superacao <> ''
+ ck_sucessor_cita_decisao       (resultado_anterior IS NULL     AND decisao IS NULL)
                              OR (resultado_anterior IS NOT NULL AND decisao IS NOT NULL)

~ ck_resultado_origem
    (origem='AVALIACAO'  AND avaliacao IS NOT NULL AND forma <> '')
 OR (origem='OCORRENCIA' AND avaliacao IS NULL AND forma = '' AND resultado_anterior IS NULL)
 OR (origem='RECURSO'    AND avaliacao IS NULL AND resultado_anterior IS NOT NULL)

  ck_resultado_completo_por_forma   INALTERADA — ver abaixo
```

**Como as quatro linhas passam, e as duas que não existem são barradas:**

| tentativa | resultado |
|---|---|
| raiz `AVALIACAO` | ramo 1 ✓; `anterior` nulo ⟹ `decisao` nula ✓ |
| sucessor `AVALIACAO` | ramo 1 ✓; `anterior` presente ⟹ `decisao` presente ✓ |
| raiz `OCORRENCIA` | ramo 2 ✓ |
| sucessor `RECURSO` | ramo 3 ✓ |
| **raiz `RECURSO`** | barrada: o ramo 3 exige `resultado_anterior IS NOT NULL` |
| **sucessor `OCORRENCIA`** | barrada: o ramo 2 exige `resultado_anterior IS NULL` |

**Nenhum `CheckConstraint` olha outra tabela.** A espécie da decisão citada, a coerência de par e a
cronologia são conferidas na **trigger**, que é onde as coerências entre tabelas moram neste projeto
— `CHECK` não atravessa tabelas em PostgreSQL.

**`ck_sucessor_cita_decisao` é bidirecional de propósito**: sucessor sem decisão seria superação sem
fundamento, e raiz com decisão seria consolidação disfarçada de julgamento.

**`ck_resultado_completo_por_forma` não muda, e a implementação mostrou por quê.** Uma redação
anterior deste documento dizia que ela passaria a depender de origem × forma. Não passa: ela diz se
a linha é internamente coerente **dada a sua forma**, e quem diz qual forma cada origem admite é
`ck_resultado_origem`. Os três ramos que já existem bastam — o terceiro, o das três ausências, serve
à Ocorrência **e** ao desfecho sem grandeza do recurso. Duplicar a origem aqui repetiria a regra em
dois lugares, que é exatamente o erro que a matriz de §6.1 corrigiu.

**Note o que não muda.** `avaliacao` continua `OneToOne` e continua anulável, e o Resultado por
recurso não a cita. É isso que impede, **no banco**, a Avaliação sintética que a decisão C recusou.

### 6.2 A trigger `resultado_etapa_coerente`, recriada por inteiro

Molde da `0004`, nome preservado — a trigger é a mesma, e foi assim que a `0004` acrescentou o ramo
da Ocorrência. Ramos novos:

```text
origem = RECURSO:
  não cita Avaliação nenhuma;
  supera alguma coisa — raiz por recurso é recusada aqui, com mensagem própria, antes que o
    `CHECK` a pegue: o gatilho roda primeiro, e a mensagem precisa nomear o problema certo;
  a decisão citada tem espécie CORRECAO_FIXADA;
  a decisão é da mesma Inscrição, do mesmo Edital e da mesma Etapa;
  **a conclusão inteira** — consequência, forma, pontuação e sentido — é a que a decisão fixou;
  a versão citada é a da decisão, e pertence a este Edital.

origem = AVALIACAO com resultado_anterior NOT NULL:
  a decisão citada tem espécie REAVALIACAO_DETERMINADA;
  a versão citada é **do mesmo Edital** da decisão — e não a mesma versão dela. Exigir identidade
    quebraria o caminho: entre decidir e reavaliar pode haver Retificação, e a D-005 da 013 é
    explícita ao dizer que Versões Consolidadas diferentes podem descrever a mesma regra da Etapa.
    Como a decisão é imutável, a identidade produziria um sucessor permanentemente inconsolidável;
  a decisão é da mesma Inscrição, do mesmo Edital e da mesma Etapa;
  a Avaliação fonte confere com a linha, como já confere hoje;
  a Avaliação fonte é DIFERENTE da que fundamentou o superado.

qualquer origem, com resultado_anterior NOT NULL:
  o superado é **exatamente** o `resultado_protegido` da decisão citada — sem isto, a decisão e a
    superação apontariam para linhas diferentes do mesmo par, e a *non reformatio*, que compara
    contra o protegido, compararia com o Resultado errado;
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

## 7. `divulgacao.PublicacaoResultado` — três colunas

| campo | tipo |
|---|---|
| `prazo_encerrado_declarado_em` | instante, anulável |
| `prazo_encerrado_declarado_por` | texto, em branco por padrão |
| `prazo_encerrado_fundamento` | texto, em branco por padrão |

**Constraint — 1**: `ck_declaracao_completa` — os três presentes, ou os três ausentes.

Preenchidos **no nascimento**, como todo o resto da linha: a tabela é append-only e nasce completa.
Exigidos quando a natureza é `DEFINITIVA` e não há janela computável; recusados quando há janela
computável (FR-086).

---

## 8. Conteúdo publicado — o degrau 8

Dentro de cada marco classificatório:

```json
"appealWindow": {"admits": true, "durationDays": 5, "unit": "DIAS_CORRIDOS"}
```

**Três estados, e os três respondem coisas diferentes** (FR-113, D-004):

```text
ausente ou null   →  janela não declarada; nenhum prazo é exibido, calculado ou aplicado
admits: false     →  o marco NÃO admite recurso; a interposição por esta via é recusada
admits: true      →  admite, e `durationDays` diz por quanto tempo
```

Nenhum dos três é janela de zero dias. Confundir os dois primeiros transformaria *"não cabe
recurso"* em *"cabe recurso para sempre"*, e o campo `admits` deixaria de ter função — nascendo,
na prática, como um booleano que só o `true` consegue afirmar.

```text
SCHEMA_VERSION      7 → 8
DEGRAUS_DE_MARCO    {8: {"appealWindow": None}}       ← nível novo na elevação (T-007)
```

**Isto não é migration.** `appealWindow` vive no JSON de `VersaoConsolidada.content`; o degrau é
código de leitura e elevação, exercido no fluxo de Retificação. Nenhuma coluna nova em
`publicacoes`.

---

## 9. Inventário de migrations

```text
resultados/0004  ──▶  recursos/0001  ──▶  resultados/0005
                            │
                            └──▶  classificacao/0004
                      divulgacao/0002   (independente das demais)
```

| # | migration | conteúdo | depende de |
|---|---|---|---|
| 1 | `recursos/0001` | 3 tabelas, 17 constraints, 5 triggers | `resultados/0004`, `divulgacao/0001`, `classificacao/0003`, `inscricoes`, `publicacoes` |
| 2 | `resultados/0005` | 3 colunas, 4 constraints novas, 2 recriadas, trigger recriada | `recursos/0001` |
| 3 | `classificacao/0004` | 1 tabela, 1 constraint, 2 triggers | `recursos/0001` |
| 4 | `divulgacao/0002` | 3 colunas, 1 constraint | `divulgacao/0001` |

**O grafo é acíclico** porque a granularidade é a migration, e não o app: `recursos/0001` vem depois
de `resultados/0004` e antes de `resultados/0005`. Em Python não há import circular — `resultados` e
`classificacao` declaram a FK como *string* (`"recursos.DecisaoRecurso"`), que é a referência tardia
do Django.

**Contagem de constraints em `recursos/0001`**: 6 no `Recurso` — incluindo a unicidade do protocolo,
declarada no campo — + 2 no `JuizoDeAdmissibilidade` + 9 na `DecisaoRecurso` = **17**.

---

## 10. Inventário de triggers

O projeto usa **uma função SQL dedicada por trigger** — não há função compartilhada, e cada uma traz
a sua própria mensagem de recusa. É o padrão de `divulgacao/0001` e de `resultados/0004`.

| tabela | trigger | tipo | o que faz |
|---|---|---|---|
| `recursos_recurso` | `recurso_append_only` | imutabilidade | recusa `UPDATE`/`DELETE` |
| `recursos_recurso` | `recurso_coerente` | coerência | o objeto atacado pertence à Inscrição; a versão citada é do Edital dela |
| `recursos_juizodeadmissibilidade` | `juizo_de_admissibilidade_append_only` | imutabilidade | |
| `recursos_decisaorecurso` | `decisao_recurso_append_only` | imutabilidade | |
| `recursos_decisaorecurso` | `decisao_recurso_coerente` | coerência | o recurso citado está **admitido**; `resultado_protegido` é do mesmo par e Edital; `etapa_id` confere |
| `classificacao_citacaodedecisao` | `citacao_de_decisao_append_only` | imutabilidade | |
| `classificacao_citacaodedecisao` | `citacao_coerente` | coerência | a decisão é `PROVIDENCIA_A_JUSANTE` **e pertinente ao Perfil e ao Marco do ato** — ver §10.1 |
| `resultados_resultadoetapa` | `resultado_etapa_coerente` | coerência | **recriada**, com os ramos de §6.2. Nome inalterado |
| `resultados_resultadoetapa` | `resultado_etapa_append_only` | imutabilidade | **inalterada, e não desligada** |

**Uma trigger não valida outra tabela.** Por isso a coerência da `DecisaoRecurso` é instalada **na
`DecisaoRecurso`**, e não no `Recurso`: são duas triggers de coerência em `recursos`, e não uma.

### 10.1 `citacao_coerente` — a pertinência ao Marco é invariante persistente

Uma redação anterior desta trigger conferia apenas o **Edital**, e deixava aberta a porta que a
citação existe para fechar: uma gravação direta poderia ligar uma decisão pertinente ao marco `M1` a
um ato de `M2` do mesmo Edital, e liberar indevidamente a definitiva de `M2`. O Perfil e o Marco
passam a ser conferidos no banco.

```text
1. a decisão citada tem espécie PROVIDENCIA_A_JUSANTE;
2. o recurso da decisão é do mesmo Edital do ato;
3. pertinência, conforme o objeto que o recurso atacou:

   ataca PublicacaoResultado  →  (publicacao.edital_id, perfil_id, marco_id)
                                 =  (ato.edital_id, ato.perfil_id, ato.marco_id)

   ataca ResultadoEtapa       →  inscricao.profile_id = ato.perfil_id
                                 E o marco do ato, lido de `ato.versao.content`,
                                   ENUMERA `resultado.etapa_id`
```

**O terceiro ramo não é caro nem inédito**: é literalmente o caminho que
`check_ordering_act_provenance` já percorre em `classificacao/0003` — `jsonb_array_elements` sobre
`content -> 'profiles' -> 'classificationMilestones' -> 'stages'`, com `perfil_id` e `marco_id` como
filtros. O precedente está escrito, a conferência é `set-based` e roda uma vez por citação.

**O que continua no comando**: oferecer ao operador **quais** decisões pendentes daquele marco ele
pode citar. A trigger recusa a citação impertinente; a tela evita que ela seja tentada.

---

## 11. O manager de vigência — onde ele mora

`ResultadoEtapa.vigentes` é **manager de modelo**, e vive em `resultados/models.py` (ou em
`resultados/managers.py`, importado pelo modelo). Os selectors **consomem** o manager; não o
declaram (T-004).

```python
class ResultadoEtapa(models.Model):
    objects = models.Manager()          # tudo, inclusive superados
    vigentes = VigentesManager()        # sucessor__isnull=True
```

**Nomeado, e não `objects` redefinido**: a reprodução histórica precisa ver os superados, e um
default que os esconde faria o caminho correto ser o exótico.

---

## 12. Situações derivadas — o que **não** vira coluna

| situação | derivada de |
|---|---|
| aguardando admissibilidade | `Recurso` sem `JuizoDeAdmissibilidade` |
| inadmitido | juízo com `admitido = false` — terminal |
| aguardando julgamento | admitido, sem `DecisaoRecurso` |
| decidido | decisão existente |
| reavaliação determinada, não cumprida | decisão `REAVALIACAO_DETERMINADA` sem sucessor do par posterior a ela |
| providência não cumprida **para um marco** | decisão `PROVIDENCIA_A_JUSANTE` pertinente ao marco, sem citação pelo ato candidato e sem ato citante já publicado naquele marco (§5.2) |
| Resultado vigente | `sucessor__isnull=True` |
| reabilitada por recurso | Resultado vigente que é sucessor, com consequência habilitante |
| janela aberta | função pura da publicação âncora e da norma |

Nove situações, zero colunas de estado. É o mesmo idioma de `PENDENTE`/`CONSOLIDADO` na 013 e da
vigência na 015 e na 017.
