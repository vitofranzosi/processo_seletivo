# Descoberta 018 · Decisão C — como um recurso deferido supera um `ResultadoEtapa` consolidado

**Sessão de análise conduzida em 06/09/2026**, sobre `124ff0b` — a `main` com o PR #44 integrado.
Nenhuma linha de código foi escrita, nenhuma spec existente foi alterada e a SPEC 018 não foi
aberta. O que está aqui responde à pergunta **C** da §14 do relatório
`doc/e2e/017-exploratoria/relatorio.md`, e só a ela:

> *Um recurso deferido pode alterar um `ResultadoEtapa` consolidado? Se pode, por qual mecanismo —
> anulação, superação, ou outro?*

As perguntas **A** (que fato torna uma publicação definitiva) e **B** (que fato autoriza mostrar ao
candidato o Resultado individual da Etapa) **não** são decididas aqui. A §9 registra, sem decidi-las,
o que a resposta a C oferece e o que ela não oferece a cada uma.

---

## 1. Resumo da decisão

**Um recurso deferido pode produzir efeito sobre um `ResultadoEtapa` consolidado, e o mecanismo é a
superação por sucessor append-only** — a mesma forma que o `AtoDeOrdenacao` (015) e a
`PublicacaoResultado` (017) já usam, aplicada ao elo que ficou sem ela.

O Resultado consolidado **não** é alterado, anulado, marcado nem apagado. Nasce outra linha, que
cita a que superou e a decisão que a autorizou; vigente passa a ser o Resultado que ninguém sucedeu.
`uq_resultado_inscricao_etapa` deixa de ser incondicional e vira o par de constraints que a 015 e a
017 já escreveram duas vezes: unicidade da **raiz** e unicidade do **sucessor**.

O que isso custa não é mecanismo novo — é **percorrer os seletores que hoje leem "existe Resultado"
como se isso significasse "existe um só"**. A lista é fechada e está na §7.

O que isso **não** resolve, e é decisão institucional, está na §10. Duas dessas perguntas são
bloqueantes para a 018 e uma delas — *quem fixa a nota nova* — decide se o modelo ganha uma terceira
origem ou não.

---

## 2. O mapa factual da cadeia

```text
Atribuicao (ativo) ─1:1─ Avaliacao ──┐
   uq_atribuicao_ativa                │  RASCUNHO ⇄ CONCLUIDA (reabrir)
   (membro, edital, etapa, inscricao) │  uq_avaliacao_concluida_por_pessoa
                                      │  └─< ConclusaoAvaliacao (append-only, ordem)
                                      ↓
                          ResultadoEtapa  ← append-only, ÚNICO por Inscrição × Etapa
                          origem: AVALIACAO | OCORRENCIA        ← SEM SUCESSÃO
                                      ↓  calcular_ordem lê TODOS os Resultados das
                                      ↓  Etapas que o marco enumera
                    AtoDeOrdenacao + PosicaoNaOrdem   ← append-only, COM sucessão
                    universo.stageResults = conjunto de ids de Resultado
                                      ↓  publicar_resultado
        PublicacaoResultado + SituacaoDivulgada + DocumentoDoResultado
                                      ← append-only, COM sucessão
```

### 2.1 Quais registros são imutáveis

`seguranca/papeis.py:26` lista as tabelas de que o papel de runtime **não tem `UPDATE` nem
`DELETE`**. Da cadeia acima, são imutáveis nas três camadas — `save`/`delete` do modelo, trigger de
banco e privilégio negado:

| registro | camadas |
|---|---|
| `ResultadoEtapa` | `save`/`delete` (`resultados/models.py`), trigger `resultado_etapa_append_only` (`BEFORE UPDATE OR DELETE`, migration `0001`), papel |
| `AtoDeOrdenacao`, `PosicaoNaOrdem` | `save`/`delete` (`classificacao/models.py`), papel |
| `PublicacaoResultado`, `SituacaoDivulgada`, `DocumentoDoResultado` | `save`/`delete` (`divulgacao/models.py`), papel |
| `ConclusaoAvaliacao`, `RegistroAuditoria`, `AtoAdministrativo`, `VersaoConsolidada`, `ValorDeFato` | papel + modelo |

**Não** são imutáveis, e é importante para C: `Avaliacao` (transita `RASCUNHO ⇄ CONCLUIDA` por
`reabrir`) e `Atribuicao` (tem `ativo`, que o impedimento desliga). O regime append-only começa
exatamente no `ResultadoEtapa` — ele é a **fronteira** entre o que ainda se corrige mutando e o que
só se corrige acrescentando.

### 2.2 Quais possuem sucessão

Duas, e as duas escrevem a mesma forma:

```text
AtoDeOrdenacao            uq_ato_raiz_por_marco       UNIQUE(edital, perfil, marco) WHERE ato_anterior IS NULL
  classificacao/models.py:49,54,58
                          uq_ato_sucessor_unico       UNIQUE(ato_anterior)          WHERE ato_anterior IS NOT NULL
                          ck_sucessao_com_motivo      ato_anterior IS NULL OR motivo_da_sucessao <> ''

PublicacaoResultado       uq_publicacao_raiz_por_marco      UNIQUE(edital, perfil, marco) WHERE publicacao_anterior IS NULL
  divulgacao/models.py:74,79,88
                          uq_publicacao_sucessora_unica     UNIQUE(publicacao_anterior)   WHERE NOT NULL
                          uq_publicacao_por_ato_natureza    UNIQUE(ato, natureza)
```

Nos dois casos **vigente é o que ninguém sucedeu** — `sucessores__isnull=True`,
`sucessoras__isnull=True` — e não há coluna de vigência a alternar. Não há estado a manter coerente
porque não há estado: a vigência é derivada da cadeia.

`ConclusaoAvaliacao` guarda histórico ordenado (`uq_conclusao_ordem`), mas **não** é sucessão de
vigência: a conclusão vigente é a da `Avaliacao` corrente, e as linhas preservadas existem para que
"o que aquela pessoa havia concluído antes" seja consulta e não arqueologia.

**`ResultadoEtapa` é o único elo da cadeia sem sucessão.** É a lacuna que C precisa fechar.

### 2.3 Quais apenas registram contestação

Dois mecanismos, e os dois são **declaração sem decisão**:

1. **`contestacoes_supervenientes()`** (`resultados/application/selectors.py:122`). Quando um
   Impedimento alcança, depois da consolidação, a pessoa que produziu a Avaliação fonte, a listagem
   de Resultados passa a exibir que aquela origem foi contestada. Nada é recalculado, nada é
   invalidado. O contrato da 013 é explícito: *"`resultados_contestados` é campo novo, e é
   declaração, não decisão"*. É hoje **a única forma pela qual o sistema registra que algo saiu
   errado num Resultado** — e ela não corrige nada.

2. **`_recusar_se_fundamenta_resultado()`** (`avaliacoes/application/avaliacao.py:333`). Reabrir uma
   Avaliação que fundamenta Resultado responde **409**, e a frase da recusa já nomeia a lacuna que
   esta descoberta preenche:

   > *"Corrigir um Resultado consolidado exige anulação, que é ato de outra natureza."*

   O código, portanto, já sabia que faltava um ato — e já sabia que ele não existia.

### 2.4 Quais constraints impedem hoje um novo resultado

São **oito**, em três camadas, e listá-las é metade da resposta a C, porque cada alternativa é
julgada por quais delas precisa remover.

| # | onde | o quê |
|---|---|---|
| 1 | `resultados/models.py:112` | `uq_resultado_inscricao_etapa` UNIQUE(`inscricao_id`, `etapa_id`) — **incondicional**. Bloqueia qualquer segundo Resultado, superador ou não. |
| 2 | `resultados/models.py:76` | `avaliacao` é **`OneToOneField`**. Uma Avaliação fundamenta no máximo um Resultado. |
| 3 | `resultados/models.py:133` | `ck_resultado_origem`: `AVALIACAO ⟹ avaliacao NOT NULL AND forma <> ''`; `OCORRENCIA ⟹ avaliacao NULL AND forma = ''`. |
| 4 | `resultados/models.py:148` | `ck_resultado_completo_por_forma`: `forma = '' ⟹ pontuacao IS NULL AND sentido = ''`. |
| 5 | migration `0004` | trigger `resultado_etapa_coerente` `BEFORE INSERT` — a fonte tem de estar `CONCLUIDA`, sob Atribuição `ativo`, e coincidir em inscrição, Etapa, Edital, forma, pontuação, sentido e versão. |
| 6 | migration `0001` + `papeis.py` | trigger `resultado_etapa_append_only` e o papel sem `UPDATE`/`DELETE`. |
| 7 | `avaliacoes/models.py:136` | `uq_avaliacao_concluida_por_pessoa` UNIQUE(`identity_subject`, `etapa_id`, `inscricao_id`) WHERE `CONCLUIDA` — a mesma pessoa não conclui duas vezes o mesmo par. |
| 8 | aplicação | `_estado_do_participante` devolve `CONSOLIDADA`; `ocorrencia.py` recusa a linha com *"esta inscrição já possui Resultado nesta Etapa"*; `reabrir` responde 409. |

**As duas consequências não óbvias, e as duas importam para a decisão:**

- **De (2) + (7): reabrir e reconcluir a mesma Avaliação nunca poderia fundamentar um segundo
  Resultado**, mesmo que (1) e (8) fossem removidas. `reabrir` faz `compare_and_swap` sobre a
  **mesma linha** de `Avaliacao`; o Resultado antigo já detém o `OneToOne` sobre ela. O caminho
  "recorreu → reabre → recorrige a nota → consolida de novo" está estruturalmente fechado, e não por
  descuido. Um Resultado sucessor com origem em avaliação exige uma **Avaliação diferente** — o que
  é possível hoje, porque `uq_atribuicao_ativa` é por *membro*: outro avaliador pode receber
  Atribuição ativa para o mesmo par e concluir.
- **De (3) + (4): hoje não existe Resultado com pontuação sem Avaliação fonte.** A `OCORRENCIA` é
  toda de ausências — sem forma, sem pontuação, sem sentido. Logo, **uma banca recursal que fixe
  diretamente a nota nova não tem hoje como gravá-la**: precisaria de um terceiro ramo de origem.
  Isso transforma uma pergunta que parecia de processo — *quem fixa a nota?* — em pergunta de
  esquema, e é por isso que ela aparece na §10 como bloqueante.

### 2.5 Quais seletores assumem unicidade

Este é o inventário que qualquer alternativa com dois Resultados vivos para o mesmo par tem de
pagar. Está separado entre o que **quebra em silêncio** e o que apenas muda de significado.

**Quebram em silêncio — produzem resultado errado sem erro:**

| seletor | o que assume | o que aconteceria |
|---|---|---|
| `classificacao/application/calculo.py:97` | `pontuacoes = {str(etapa_id): pontuacao}` | Dois Resultados na mesma Etapa **colapsam**: o último do queryset vence, e o queryset não tem `order_by`. Ordem classificatória errada, sem exceção, sem log. **É a assunção mais perigosa do sistema.** |
| `resultados/application/prontidao.py:143` | `~Exists(... consequencia=ELIMINADA)` sobre Etapas anteriores | Uma eliminação **superada** continuaria excluindo a pessoa de toda Etapa seguinte, da distribuição, da Mesa, da inscrição de trabalho e da próxima pendente. O deferimento não teria efeito nenhum onde mais importa. |
| `resultados/application/prontidao.py:174,183` | `participa_da_etapa`, mesma regra na rota individual | Mesmo efeito, agora como 404 uniforme para o avaliador. |
| `resultados/application/selectors.py:35` | `eliminadas_ate` | Idem, na forma em conjunto. |
| `resultados/application/selectors.py:24` | `habilitadas_em` | Pertinência satisfeita por qualquer Resultado `HABILITADA`, superado inclusive. |
| `resultados/application/selectors.py:122` | `contestacoes_supervenientes` indexa por `(identity_subject, inscricao_id)` | Dois Resultados da mesma inscrição por avaliadores distintos colidem na chave e um perde a marcação de contestação. |

**Mudam de significado — passam a responder "existe algum" onde queriam "existe o vigente":**

`ha_resultado_em` (o gate de D-003), `inscricoes_com_resultado`, `_estado_do_participante`,
`contagens` (a partição deixaria de somar), `resultados_da_etapa` (a listagem passaria a ter N
linhas por inscrição), `avaliacoes/application/impedimento.py:148`.

**Imune por construção, e vale registrar por quê:** `classificacao/application/reproducao.py:34` lê
os Resultados por `pk__in` dos ids gravados em `ato.universo.stageResults`, e recusa com
`historical_input_missing` se algum sumir. **A reprodução histórica de um ato já emitido não é
afetada por Resultado novo nenhum** — ela é função pura da proveniência gravada. Este fato é o que
torna a alternativa 2 barata em auditoria e a alternativa 3 impossível.

### 2.6 Que efeitos um recurso deferido teria sobre atos e publicações posteriores

**A cadeia a jusante já sabe reagir, e reage sozinha.** Este é o achado central da sessão.

O `AtoDeOrdenacao` grava em `universo.stageResults` (`calculo.py:235`) o **conjunto de ids** dos
Resultados que o produziram. `comparar()` (`classificacao/domain/universo.py:69`) confronta esse
conjunto com o do cálculo de agora e, se diferirem, emite `resultados_alterados`. Daí:

```text
Resultado novo entra no universo
  → comparar() emite "resultados_alterados"
  → estado_do_marco().obsoleto = True
  → aferir() devolve IMPEDIMENTO / publication_act_stale (422), admite_sucessor = True
  → a prévia de publicação NÃO oferece o botão e nomeia o caminho:
    "Emita o ato sucessor na tela de classificação do marco e publique o ato vigente."
  → emitir_ordem() cria o sucessor e EXIGE motivo_da_sucessao (ck_sucessao_com_motivo)
  → publicar_resultado() sucede a publicação vigente (aviso, não impedimento)
  → situacoes_do_candidato() filtra publicacao__sucessoras__isnull=True
    → a Área do Candidato passa a mostrar a nova situação, sozinha
  → a publicação anterior permanece consultável, íntegra, marcada como sucedida
```

Nada disso precisa ser construído. A 015 e a 017 já o entregaram, e o relatório da E2E-017 provou
empiricamente que a publicação sucedida preserva o conteúdo original (`95,00` contra os `190,00` que
a regra de hoje produziria).

**Duas arestas ficam:**

1. **Regressão de natureza é proibida.** `publicar_resultado` recusa `DEFINITIVA → PRELIMINAR` com
   `publication_nature_regresses`. Se um marco já foi publicado como **definitivo** e um recurso é
   deferido depois, a publicação sucessora só pode ser outra **definitiva**. Não existe rebaixar,
   não existe anular publicação. Institucionalmente isso é uma retificação de resultado definitivo,
   e o produto hoje não tem palavra para ela — só a sucessão silenciosa de natureza igual.
2. **`uq_publicacao_por_ato_natureza`** impede publicar o **mesmo** ato duas vezes na mesma natureza.
   Não é obstáculo: o remédio do recurso deferido é um ato **novo**, e sobre ele a natureza está
   livre. Mas é o que fecha o caminho "republicar sem emitir ato", que seria a saída preguiçosa.

---

## 3. As quatro alternativas, avaliadas

Os critérios são os pedidos: auditabilidade e reprodução histórica; aderência à Constituição;
impacto em `uq_resultado_inscricao_etapa`; necessidade de estado vigente ou de `supersedes`; efeito
sobre atos classificatórios já emitidos; efeito sobre publicações preliminares ou definitivas;
concorrência, idempotência e autorização; e capacidade de explicar ao candidato e à auditoria.

### Alternativa 1 — Anular o Resultado anterior e emitir outro, preservando ambos

Duas variantes, e as duas falham por motivos diferentes.

**1a · anulação como coluna no próprio `ResultadoEtapa`** (`anulado_em`, `anulado_por`, `motivo`).
Morre no primeiro critério: gravar a anulação é `UPDATE` sobre a linha, que a trigger
`resultado_etapa_append_only` recusa, que o papel de runtime não tem privilégio para fazer e que o
`save()` do modelo levanta. Manter a coluna exigiria **desmontar as três camadas** de um registro que
a Constituição classifica entre os "registros normativos, publicados, históricos ou auditáveis". Não
é ajuste: é a revogação do regime.

**1b · anulação como tabela própria** (`AnulacaoResultado(resultado, motivo, ator, instante)`).
Preserva o append-only, e é honesta. Falha em dois pontos:

- **`uq_resultado_inscricao_etapa` não tem como sobreviver.** A unicidade teria de ser "um Resultado
  não anulado por par", e essa condição vive noutra tabela — uma `UniqueConstraint` condicional não
  atravessa junção. A invariante 1 da 013 deixaria de ser constraint e viraria promessa de código,
  que é exatamente o que o `data-model.md` da 013 recusa em duas passagens: *"unicidade precisa ser
  constraint"*, *"é ela — não o botão da tela, não o bloqueio — que torna FR-024 verdadeiro sob
  qualquer concorrência"*.
- **A anulação não obriga a substituição.** Anulado e não reemitido, o par volta a não ter Resultado
  vigente — e a progressão lê ausência de linha como `PENDENTE` (D-006 da 013). Uma Etapa já
  percorrida reabriria para aquela inscrição, a Mesa voltaria a oferecê-la e a prontidão a
  contaria. A alternativa cria um estado intermediário que o domínio não sabe representar.

**Auditoria e explicação ao candidato:** boas, mas não melhores que a alternativa 2 — "foi anulado e
outro foi emitido" e "foi superado por outro" contam a mesma história, e a segunda garante no banco
que a segunda metade existe.

**Descartada.**

### Alternativa 2 — Superar por sucessor append-only

`ResultadoEtapa` ganha `resultado_anterior` (FK `self`, nulável, `PROTECT`), `motivo_da_superacao` e
a citação da decisão que autorizou. As constraints trocam de forma:

```text
antes:  uq_resultado_inscricao_etapa    UNIQUE(inscricao_id, etapa_id)

depois: uq_resultado_raiz_por_par       UNIQUE(inscricao_id, etapa_id) WHERE resultado_anterior IS NULL
        uq_resultado_sucessor_unico     UNIQUE(resultado_anterior)     WHERE resultado_anterior IS NOT NULL
        ck_superacao_com_motivo         resultado_anterior IS NULL OR motivo_da_superacao <> ''
```

**É, literalmente, o par que `AtoDeOrdenacao` e `PublicacaoResultado` já escreveram.** Cadeia linear,
sem bifurcação, vigente derivado por `sucessor__isnull=True`.

| critério | avaliação |
|---|---|
| **Auditabilidade** | Máxima. Nada é alterado; a cadeia inteira fica legível na ordem em que aconteceu, com motivo obrigatório em cada elo. |
| **Reprodução histórica** | **Imune por construção.** `reproduzir_ato` lê os Resultados por id do universo gravado; o ato antigo continua reproduzindo a ordem antiga com as entradas antigas. IO-5 da 015 — *"a mesma proveniência reproduz a mesma ordem"* — permanece verdadeira sem nenhum cuidado adicional. |
| **Constituição** | Princípio I (registros históricos não são fisicamente excluídos, invariantes persistentes usam constraints), II (imutabilidade, reprodutibilidade do estado vigente em qualquer instante), IV (estados e transições explícitos), V (a solução mais simples que preserva os requisitos — e esta não inventa mecanismo: é o terceiro uso do mesmo). |
| **`uq_resultado_inscricao_etapa`** | Substituída, não removida. Migration `RemoveConstraint` + dois `AddConstraint`, **sem backfill**: todo Resultado existente tem `resultado_anterior IS NULL` e continua sendo raiz única do seu par. Não desliga trigger nenhuma. |
| **Estado vigente / `supersedes`** | `supersedes` sim (`resultado_anterior`); **estado vigente não** — vigência é derivada, como nos outros dois. Nenhuma coluna a manter coerente. |
| **Atos já emitidos** | Obsoletados automaticamente pelo diff de `stageResults`, com o caminho do sucessor já nomeado na recusa. Nenhum ato é alterado. |
| **Publicações** | Sucessão, que a 017 já entrega. Preliminares e definitivas permanecem consultáveis; a Área do Candidato acompanha sozinha pelo filtro de `sucessoras__isnull=True`. Resta a aresta da §2.6.1 (definitiva sucedida por definitiva). |
| **Concorrência** | O invólucro `comando_de_comissao` — transação, bloqueio do Processo, reavaliação da autorização **depois** do bloqueio, reserva da chave — é o mesmo de `consolidar` e `ocorrencia`. A corrida "dois deferimentos sobre o mesmo Resultado" é resolvida por `uq_resultado_sucessor_unico`, no banco, e não por leitura prévia. |
| **Idempotência** | `IdempotencyRecord.result_payload` com o desfecho declarado, como os três comandos irmãos. |
| **Autorização** | Ver §10.6 — é pergunta institucional aberta, não obstáculo técnico. |
| **Explicação** | A melhor das quatro: *"o Resultado X foi superado pelo Resultado Y em razão do recurso Z, deferido em tal data por tal autoridade"*, com os dois consultáveis lado a lado. Auditoria e candidato leem a mesma frase. |
| **Custo** | O inventário da §2.5. Real, enumerável, sem descoberta pendente. |

**Recomendada.**

### Alternativa 3 — Manter o Resultado e registrar decisão de recurso que altere a leitura efetiva

Uma `DecisaoRecurso` que a leitura consulta e "aplica" sobre o Resultado original, que permanece
intocado e continua sendo a única linha do par.

**Falha em três frentes, e a primeira é fatal:**

1. **Mata a reprodução histórica.** `reproduzir_ato` lê o Resultado pelo id gravado no universo e o
   toma pelo valor que ele afirma. Com leitura efetiva, ou a reprodução devolve a ordem **errada**
   (lê o valor cru, que já não é o que vigora), ou ela tem de reaplicar a decisão — e aí deixa de
   ser função pura da proveniência gravada, porque passa a depender do estado de outra tabela no
   instante da leitura. IO-5 da 015 cai nos dois caminhos.
2. **Cria a segunda fonte que o princípio II proíbe.** Passa a haver duas respostas para "qual é a
   pontuação desta inscrição nesta Etapa": a da coluna e a da leitura. O `data-model.md` da 013
   recusa exatamente esse desenho ao decidir não copiar nota mínima e caráter da Etapa — *"duplicá-los
   criaria a segunda fonte divergente que o princípio II proíbe"*.
3. **O diff de obsolescência deixa de disparar.** `comparar()` olha o conjunto de **ids** de
   Resultado. Sem linha nova, o conjunto não muda, o ato não fica obsoleto, e a publicação vigente
   continua publicável sobre uma ordem que já não é a verdadeira. A cadeia inteira a jusante ficaria
   cega ao deferimento — e teria de ganhar um segundo mecanismo de detecção, paralelo ao que já
   funciona.

**Uma variante mais fraca merece nota:** registrar a decisão do recurso **sem** alterar leitura
nenhuma, apenas declarando ao lado do Resultado — como `contestacoes_supervenientes` faz com o
Impedimento. É honesta e não viola nada. Mas **não responde a C**: não há superação, o Edital promete
recurso contra resultado divulgado, e um recurso que não pode mudar nada é um formulário.

**Descartada como mecanismo de efeito.** A forma declaratória sobrevive como complemento — ver §5,
invariante I-R7.

### Alternativa 4 — Restringir recursos ao período anterior à consolidação

O recurso incidiria sobre a **Avaliação**, e o mecanismo já existe: `reabrir` com motivo obrigatório,
cujo docstring diz textualmente *"Recurso e erro material existem; o que não pode existir é
reabertura silenciosa"*. Depois de consolidado, o Resultado seria definitivo.

**Falha por contradizer o objeto do recurso:**

- **Recorre-se do que foi divulgado.** A 017 existe para criar *"o marco público contra o qual um
  recurso futuro poderá ser interposto"* (§6 da spec da 017). Consolidação é ato interno; o candidato
  não a vê — e, por E2E17-004, quem foi eliminado numa Etapa anterior não vê nada, nem que houve
  resultado. Um recurso anterior à consolidação recorre de um resultado que ninguém conhece.
- **Contradiz a 015**, que descreve o caso real: *"Há Editais que publicam a ordem intermediária,
  recebem recurso sobre ela e a republicam antes de convocar para a Etapa seguinte"*.
- **Contradiz o Edital que o produto já emite.** A seção "Dos Recursos"
  (`editais/domain/secoes.py:136`) promete recurso *"contra os resultados divulgados"*.

**Mas ela não é inteiramente descartada, e este é o recorte que a §4 formaliza:** existe uma classe
de recurso deferido que **não** toca `ResultadoEtapa` e para a qual a alternativa 4 é a resposta
certa por outro caminho — a sucessão de ato que a 015 já tem. Ver §4.

**Descartada como regra geral; preservada como recorte.**

---

## 4. O recorte — nem todo recurso deferido supera Resultado

A pergunta C pressupõe que o efeito recaia sobre o `ResultadoEtapa`. Boa parte dos deferimentos não
recai, e reconhecê-lo reduz o escopo da 018 sem perder capacidade.

| o que o recurso ataca | onde está o erro | remédio | toca `ResultadoEtapa`? |
|---|---|---|---|
| a pontuação ou o sentido de uma Etapa | na Avaliação / na consequência consolidada | **superação de Resultado** (§3, alt. 2) → obsoleta o ato → sucessor de ato → publicação sucessora | **sim** |
| a constatação de ausência (não compareceu, descumpriu pré-requisito) | no Resultado por `OCORRENCIA` | superação, com o Resultado sucessor declarando o desfecho correto | **sim** |
| o cálculo, o desempate, a modalidade aplicada, o universo considerado | no `AtoDeOrdenacao` | **sucessor de ato**, que a 015 já entrega, com `motivo_da_sucessao` citando o recurso | **não** |
| a forma, o conteúdo ou a autoridade da divulgação | na `PublicacaoResultado` | **publicação sucessora**, que a 017 já entrega | **não** |
| a própria regra normativa | no Edital | **Retificação**, que a 006/007 já entregam — e que obsoleta atos por `regra_alterada` | **não** |

Só as duas primeiras linhas exigem primitiva nova. As três últimas exigem que a **decisão do
recurso** saiba citar o ato que a executa — o que é vínculo de auditoria, não mecanismo.

---

## 5. Invariantes propostos

Numerados `I-R` para não colidir com os das specs existentes. São proposta de descoberta, não
requisitos aprovados.

- **I-R1 — Um vigente por par.** Para toda Inscrição × Etapa existe no máximo um `ResultadoEtapa`
  **vigente**, e vigente é o que nenhum outro sucedeu. Garantido no banco por
  `uq_resultado_raiz_por_par` + `uq_resultado_sucessor_unico`, e não por leitura da aplicação.
- **I-R2 — A cadeia é linear e do mesmo par.** Todo Resultado sucessor cita exatamente um superado;
  o superado é do mesmo `(inscricao, etapa_id, edital)`; nenhum Resultado se sucede a si mesmo nem
  fecha ciclo. A coerência de par é conferida pela trigger `resultado_etapa_coerente`, que já é o
  lugar onde as coerências entre tabelas moram.
- **I-R3 — Superação só nasce de decisão.** Nenhum caminho cria Resultado sucessor senão a execução
  de uma decisão de recurso deferido; a linha cita essa decisão. Consolidação e ocorrência continuam
  criando **apenas raízes**, e continuam recusando o par que já tem vigente.
- **I-R4 — Nada é alterado nem apagado.** Superado e superador são igualmente imutáveis nas três
  camadas. O regime append-only não é relaxado em ponto nenhum, e nenhuma migration futura desliga a
  trigger para gravar superação.
- **I-R5 — Toda leitura de efeito considera só o vigente.** Progressão, participação, prontidão,
  consolidação, classificação e divulgação leem o Resultado vigente do par. Ler o superado é
  privilégio de duas superfícies e de mais nenhuma: a consulta histórica e a reprodução de ato.
- **I-R6 — A superação obsoleta a jusante, e não corrige a jusante.** Superar um Resultado torna
  obsoleto todo `AtoDeOrdenacao` cujo universo cite o superado, e nenhuma publicação nova é possível
  sobre esse ato. **Nenhum ato e nenhuma publicação são recalculados, alterados ou anulados em
  cascata** — a correção é sempre ato humano autorizado, emitido com motivo. É o que separa esta
  decisão de um recálculo silencioso.
- **I-R7 — O superado permanece consultável e legível.** Quem consulta o histórico do par vê os dois,
  em ordem, com motivo, autor, instante e a decisão que autorizou. A forma declaratória que
  `contestacoes_supervenientes` já usa é o molde da apresentação.
- **I-R8 — O ato é autorizado, transacional e idempotente.** Mesmo invólucro de `consolidar` e
  `ocorrencia`: transação, bloqueio do Processo, reavaliação da autorização depois do bloqueio,
  reserva da chave, desfecho serializado. Repetir a chave devolve o desfecho original e cria zero
  linhas.
- **I-R9 — A cronologia é monotônica.** O `consolidado_em` do sucessor é posterior ao do superado.
  Sem isto, "o mais recente" e "o vigente" poderiam divergir na leitura de auditoria.

---

## 6. Transições de estado

**`ResultadoEtapa` não ganha máquina de estados, e não deve ganhar** — pelo mesmo motivo que
`PublicacaoResultado` não tem: *"nasce publicado e é sucedido por outra linha, ou não é"*. Uma coluna
de vigência seria estado a manter coerente onde a cadeia já o deriva.

A transição é da **cadeia**, e é irreversível:

```text
(sem linha)  ──consolidar│ocorrência──▶  R1 · vigente
                                          │
                                          │ recurso deferido com efeito sobre a Etapa
                                          ▼
                                        R1 · superado  ──▶ (terminal)
                                        R2 · vigente
                                          │
                                          │ novo recurso deferido
                                          ▼
                                        R2 · superado / R3 · vigente   …
```

E o acoplamento com a máquina do Recurso — que é da 018 e **não** é decidida aqui — se dá num ponto
só:

```text
Recurso:  INTERPOSTO ──▶ ADMITIDO ──▶ JULGADO
                     └─▶ INADMITIDO      ├─ INDEFERIDO ──▶ nada muda no domínio
                                          └─ DEFERIDO
                                               ├─ com efeito sobre Resultado ──▶ cria R(n+1)
                                               └─ sem efeito sobre Resultado ──▶ §4: sucessor de
                                                  ato, publicação sucessora ou Retificação
```

O ponto de contato é `DEFERIDO com efeito → cria sucessor`. Se esse passo é automático ou é ato
separado da presidência é pergunta institucional (§10.2).

---

## 7. Impacto provável

### 7.1 Modelos

`resultados/models.py` — três campos e três constraints:

```text
+ resultado_anterior   FK(self, null=True, PROTECT, related_name="sucessor")
+ motivo_da_superacao  TextField(blank, default="")
+ (a citação da decisão de recurso — forma depende de §10.1)

- uq_resultado_inscricao_etapa
+ uq_resultado_raiz_por_par        UNIQUE(inscricao, etapa_id) WHERE resultado_anterior IS NULL
+ uq_resultado_sucessor_unico      UNIQUE(resultado_anterior)  WHERE resultado_anterior IS NOT NULL
+ ck_superacao_com_motivo          resultado_anterior IS NULL OR motivo_da_superacao <> ''
```

**Se** a decisão de §10.1 for "a banca recursal fixa a nota", acrescenta-se um terceiro valor a
`origem` e um terceiro ramo a `ck_resultado_origem` e a `ck_resultado_completo_por_forma` — porque
hoje um Resultado sem Avaliação é obrigatoriamente sem pontuação (§2.4). **Se** for "manda
reavaliar", nada disso é necessário: a origem continua `AVALIACAO`, apontando outra Avaliação.

`classificacao/models.py` e `divulgacao/models.py` — **nenhuma alteração**. As duas cadeias de
sucessão já existem e já reagem.

### 7.2 Migrations

Uma, em `resultados` (`0005`). Não toca conteúdo publicado, não eleva `SCHEMA_VERSION` (hoje 7), e
**não desliga a trigger append-only**: a troca de constraint não escreve em linha nenhuma, porque
todo Resultado existente já é raiz. A trigger `resultado_etapa_coerente` é recriada por inteiro —
molde que a `0004` já estabeleceu — para ganhar a conferência de par do ramo com sucessor.

**Nenhuma migration em `classificacao`, `divulgacao`, `publicacoes`, `avaliacoes` ou `editais`** para
a decisão C isolada. A 018 inteira terá as suas, pela entidade Recurso.

### 7.3 Comandos

| comando | mudança |
|---|---|
| `resultados/application/consolidacao.py` | nenhuma de comportamento — continua criando só raízes e recusando o par que já tem vigente. A recusa passa a ler "já possui Resultado **vigente**". |
| `resultados/application/ocorrencia.py` | idem. O docstring já diz *"para uma Inscrição × Etapa existe no máximo um Resultado vigente"* — a palavra já estava lá, aguardando a constraint. |
| `avaliacoes/application/avaliacao.py::reabrir` | a recusa 409 permanece e melhora: a frase deixa de prometer uma "anulação" que não existe e passa a nomear o ato que existe. |
| **novo** — executar o deferimento | comando próprio, invólucro idêntico a `consolidar`. |

### 7.4 Seletores — o trabalho real

Todo o inventário da §2.5 precisa de um filtro de vigência. A forma que o restante do código já usa
é `sucessor__isnull=True`, e ela cabe onde os `Exists` correlacionados já estão — sem round-trip
adicional e sem quebrar os orçamentos de consulta que a 011, a 012 e a 015 escreveram em teste.

Ordem de risco decrescente:

1. `classificacao/application/calculo.py:97` — **o colapso silencioso do dicionário de pontuações.**
   Precisa de filtro de vigência *e* de `order_by` determinístico, para que a ausência do filtro
   nunca mais possa produzir uma ordem arbitrária sem erro. É o teste de regressão mais importante da
   018.
2. `resultados/application/prontidao.py:143,154,174,183` — os quatro `Exists` da progressão. Sem
   isto, o deferimento não tem efeito onde ele mais importa.
3. `resultados/application/selectors.py` — `eliminadas_ate`, `habilitadas_em`,
   `inscricoes_com_resultado`, `ha_resultado_em`, `resultados_da_etapa`,
   `contestacoes_supervenientes` (esta também precisa de chave que não colida).
4. `avaliacoes/application/impedimento.py:148`.
5. `classificacao/application/reproducao.py` — **não mexer.** Ler por id do universo é o que garante
   a reprodução histórica, e acrescentar filtro de vigência ali a quebraria.

### 7.5 Interface

Superfícies que passam a ter o que dizer: a listagem de Resultados da Etapa (histórico do par, ao
lado da contestação superveniente, que já ocupa esse espaço); a tela do marco (a divergência já é
exibida, e ganha uma causa nova a nomear); a prévia de publicação (a recusa já existe e já nomeia o
caminho). O Princípio VI exige o cenário demonstrável de ponta a ponta pelo canal do ator — e ele
atravessa quatro telas, o que é escopo de spec, não de decisão.

---

## 8. Consequências para atos e publicações posteriores

Consolidado da §2.6, agora como afirmação:

1. **Nenhum ato de ordenação é alterado.** Ele fica obsoleto, e obsolescência já é observável na
   interface sem alterar o vigente (IO-6 da 015).
2. **Nenhuma publicação é alterada nem anulada.** A anterior permanece consultável no mesmo endereço,
   íntegra, marcada como sucedida — e o E2E-017 provou isso empiricamente.
3. **A correção é sempre ato humano autorizado**, com motivo obrigatório em cada elo:
   `motivo_da_superacao` no Resultado, `motivo_da_sucessao` no ato, e a publicação sucessora que
   herda a narrativa do ato de origem.
4. **A Área do Candidato acompanha sozinha**, porque `situacoes_do_candidato` já filtra por
   publicação vigente. Nenhuma alteração ali.
5. **A cascata é de bloqueio, não de recálculo.** O Resultado superado impede publicar o ato antigo;
   ele não emite ato novo. Isso é deliberado: recalcular em silêncio é exatamente o que a D-002 da
   015 separou ao distinguir calcular de emitir.
6. **A aresta aberta é a definitiva sucedida por definitiva** (§2.6.1). O produto sabe fazê-lo — a
   regressão proibida é só `DEFINITIVA → PRELIMINAR` — mas não tem palavra institucional para isso. É
   a §10.7.

---

## 9. O que C fornece — e o que não fornece — a A e a B

**Nada aqui decide A ou B.** O que segue é o registro pedido: se a solução de C entrega a primitiva
que elas poderão consumir.

**Para A — *que fato institucional torna uma publicação definitiva?***

C **fornece parcialmente**. Ao criar a entidade Recurso com estados explícitos, C torna disponível o
fato *"existem recursos pendentes de julgamento sobre este marco"* — que é candidato natural a
compor a condição de definitividade. C **não** fornece o outro fato de que A provavelmente precisa:
*"o prazo recursal expirou"*. E há um achado factual relevante para A:

> **Não existe prazo recursal estruturado no conteúdo publicado.** A seção "Dos Recursos" é textual
> (`editais/domain/secoes.py:136`), e `EventoCronograma.type` é **texto livre**, sem validação —
> o próprio modelo registra que *"inferir o período dali seria decidir uma regra de direito lendo o
> que alguém digitou"*. Um prazo recursal computável exigiria a mesma solução que o período de
> inscrições recebeu: uma **marca estrutural** no Evento, no molde de `is_registration_period`
> (`editais/models/cronograma.py:37`), com unicidade parcial. Isso é campo publicado novo, elevação
> de `SCHEMA_VERSION` (hoje 7) e caminho de leitura das versões anteriores.

Ou seja: C entrega a metade "não há recurso pendente" e deixa a metade "o prazo acabou" como custo
próprio de A. Se A e B compartilham uma primitiva, ela não é a de C.

**Para B — *que fato autoriza mostrar ao candidato seu Resultado individual da Etapa?***

C **não fornece a primitiva**, e a relação é a inversa da que se poderia supor:

- C torna B **mais caro**, não mais barato. Se o Resultado individual passar a ser visível, o que se
  mostra tem de ser o **vigente**, e a superação tem de ser explicável a quem a recebe — "a sua nota
  mudou porque o seu recurso foi deferido" é uma frase que só existe depois de C.
- Mas B é **pré-requisito de jornada** de uma parte de C. Recorre-se do que se conhece. Enquanto
  valer E2E17-004 — quem foi eliminado numa Etapa anterior não vê nada, nem que houve resultado —,
  **o recurso contra um `ResultadoEtapa` de Etapa eliminatória não tem como ser interposto pelo
  candidato**, porque ele não sabe do que recorreria. Recurso contra o marco classificatório
  divulgado, esse funciona: a 017 já entrega o marco público.

Isso é dependência real e vale registrá-la sem convertê-la em decisão: **a 018 pode entregar recurso
contra o resultado divulgado sem responder B, e não pode entregar recurso contra Resultado de Etapa
sem responder B.** Qual das duas a 018 entrega é decisão de escopo, e é do usuário.

---

## 10. Perguntas que dependem de decisão institucional

Registradas, não decididas. As duas primeiras são **bloqueantes** para especificar a 018.

**10.1 · Quem fixa a nota nova quando o recurso é deferido — a banca recursal, ou uma reavaliação?**
*(bloqueante; é pergunta de esquema, não só de processo)*
Se a banca recursal fixa a nota diretamente, o Resultado sucessor tem pontuação **sem Avaliação
fonte** — e isso hoje é impossível: `ck_resultado_origem` + `ck_resultado_completo_por_forma` exigem
que todo Resultado sem Avaliação seja também sem forma, sem pontuação e sem sentido (§2.4). Seria
preciso um terceiro valor de `origem`. Se o deferimento **manda reavaliar**, nada muda no esquema
além da superação — outro avaliador recebe Atribuição ativa (o que `uq_atribuicao_ativa` já permite,
por ser por membro), conclui, e o Resultado sucessor tem origem `AVALIACAO` como qualquer outro.
Note que a terceira via — reabrir a Avaliação original e recorrigi-la — **está estruturalmente
fechada** pelo `OneToOne` de `ResultadoEtapa.avaliacao`, e não por escolha de escopo.

**10.2 · O deferimento produz efeito automaticamente, ou o efeito é ato separado da presidência?**
*(bloqueante)*
Decide se a superação é escrita na mesma transação do julgamento ou é comando próprio com sua
autorização, sua idempotência e sua trilha. A 015 já tomou a decisão análoga — *calcular não é
emitir* — e o paralelo sugere *julgar não é executar*, mas isso é analogia, não decisão.

**10.3 · Recurso deferido pode piorar a situação de quem recorreu?**
Pode um deferimento transformar `HABILITADA` em `ELIMINADA`, ou baixar a nota? O modelo suporta
qualquer dos dois — nada em `ResultadoEtapa` restringe a consequência do sucessor. É política, e a
013 registra o precedente exato ao decidir **não** transformar em constraint que a Ocorrência sempre
elimina: *"que atos a V1 permite é política"*.

**10.4 · O deferimento pode reabrir Etapa já ultrapassada — e o que acontece com as seguintes?**
*(a de maior consequência operacional)*
Uma inscrição eliminada na Etapa 1 e reabilitada por recurso **não foi avaliada** na Etapa 2, que
pode já ter terminado e sido consolidada para todos os demais. A superação a devolve ao conjunto de
participantes da Etapa 2 (o `~Exists` da progressão passa a ignorar a eliminação superada), e ela
aparece como `PENDENTE` numa Etapa encerrada. O domínio **suporta** isso — distribuir, avaliar e
consolidar tardiamente são operações que existem —, mas quem opera precisa saber que é isso que vai
acontecer, e o Edital precisa admiti-lo. Alternativa institucional: limitar o efeito à Etapa do
recurso e tratar a progressão retroativa como caso a decidir por ato próprio.

**10.5 · Até quando um recurso pode ser interposto, e até quando o deferimento pode produzir efeito?**
Depende do achado da §9 sobre prazo recursal não estruturado. Enquanto o prazo for texto livre, o
limite temporal só pode ser exercido por decisão humana, não verificado pelo sistema.

**10.6 · Quem julga?**
Presidência, comissão recursal própria, ou autoridade signatária? Hoje há duas bases —
`comissao:gerir` (sistêmica) e `comissao:presidir` — e nenhuma permissão de julgamento. A
Constituição exige autorização específica para *"julgamento de recurso"*, nomeando-o explicitamente
entre as operações que a exigem (Princípio III). Provável permissão nova; e vale a pergunta se quem
julga pode ser quem avaliou.

**10.7 · Publicação já definitiva, recurso deferido depois — como se chama o que se publica?**
`DEFINITIVA → PRELIMINAR` é proibido; a sucessora só pode ser outra definitiva. Institucionalmente
isso é retificação de resultado definitivo, e o produto não tem hoje palavra para ela. Aceita-se uma
segunda definitiva sucedendo a primeira, ou o vocabulário precisa crescer?

**10.8 · O recurso é do candidato, ou também de terceiro?**
Impugnação por terceiro contra resultado alheio existe em certames. Muda a autorização de
interposição e o que o interessado vê.

---

## 11. O que esta sessão não fez

- Não abriu a SPEC 018 e não gerou artefatos de spec.
- Não alterou nenhuma spec existente. A `013` continua registrando "recurso, anulação, correção ou
  reconsolidação de Resultado" como fora de escopo, e é assim que ela deve permanecer: a decisão é
  desta descoberta, não retroage às features que a antecederam.
- Não decidiu A nem B.
- Não escreveu código, migration nem teste.

