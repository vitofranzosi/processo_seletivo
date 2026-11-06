# Mapa das Etapas de avaliação e da ligação com os marcos

Só leitura, worktree `gps-jornada-operacional-b991ed` (main em `250efe97`). Caminhos relativos a
`backend/processo_seletivo/`. **[C]** = confirmado no código; **[I]** = inferência.

---

## 0. Três fatos que mudam a proposta

1. **Não existe "publicar o resultado da Etapa".** `ResultadoEtapa` não tem coluna de publicação
   nem de estado (`resultados/models.py:41-166`) **[C]**. O que se publica é um `AtoDeOrdenacao` de
   **marco** (`divulgacao/models.py:35-60`, FK `ato`) **[C]**. O candidato só **vê** o seu Resultado
   de uma Etapa N quando existe `PublicacaoResultado` vigente de um marco do Perfil dele que
   **enumera** N (`resultados/application/selectors.py:170-222`) **[C]**. Ele só pode **recorrer**
   dele nessa mesma condição: fora dela a recusa é `appeal_not_visible`, 404
   (`recursos/application/interpor.py:317-332`) **[C]**. A coluna "publicação do resultado da Etapa"
   não tem ato próprio. Ela só existe derivada do marco que enumera a Etapa.
2. **Uma Etapa pode estar ligada a um marco de três jeitos, e cada jeito tem efeito próprio.** O
   código descreve isso em `editais/domain/validation.py:2024-2067` (`_quem_exige_o_resultado`)
   **[C]**:
   - **enumerada** (`stages`): dá nota ou porta para a ordem, visibilidade, recurso e janela;
   - **governada pelo corte** (`cutRule.governedStage`): a faixa restringe quem participa da Etapa,
     e o `HABILITADA` dela decide ocupação e convocação;
   - **Etapa de habilitação do sorteio** (`drawMethod.qualifyingStageId`): filtra a relação.

   Há uma quarta ligação, que não passa por marco: o **caráter eliminatório** da própria Etapa. Ele
   alimenta a progressão entre Etapas (seção 3).
3. **A V1 só consolida leitura única.** Se `evaluationsPerRegistration > 1`, a Etapa inteira fica
   bloqueada com `regra_de_combinacao_ausente` (`resultados/domain/regra.py:57-97`) **[C]**. Não
   existe ato de "divergência entre avaliadores" (seção 1.6).

---

## 1. A sequência operacional de uma Etapa

Todos os atos de gestão passam por `comando_de_comissao`
(`comissoes/application/__init__.py:75-93`). Ele abre a transação, faz `select_for_update` no
Processo, reautoriza com `pode_gerir_comissao` (permissão `comissao:gerir` **ou** presidência deste
Processo, `comissoes/domain/autorizacao.py:81-97`), confere `ensure_processo_accepts_changes` e
reserva a idempotência **[C]**. Nas telas, a porta é `_etapa_para_distribuir`
(`interface/views.py:6314-6351`): 404 para Edital de outro escopo, recusa explicada
(`require_authorization_base`, bases `BASES_DA_GESTAO_DA_COMISSAO`) para quem não gere, 404 para
Etapa fora do conteúdo vigente **[C]**.

### 1.1 Comissão e alocação de avaliadores (011)

| | |
|---|---|
| Serviço | `comissoes/application/comissao.py:67` `adicionar_membro`, `:126` `adicionar_varios`, `:202` `alterar_funcao`, `:236` `remover_membro`; `comissoes/application/alocacao.py:21` `alocar`, `:97` `alocar_varios`, `:204`/`:242` remover, `:309` `definir_distribuicao` (a matriz) **[C]** |
| Pré-requisitos / recusas | `pessoa_nao_e_membro_ativo` (422); Edital de outro Processo → 404; Etapa fora do vigente → 404; `edital_sem_versao_vigente` (Edital nunca publicado); `comissao_sem_presidente` (409: "Designe a presidência antes de distribuir trabalho."); `alocacao_ja_existe` (409) — `alocacao.py:36-80` **[C]** |
| Evidência | `MembroComissao`, `AlocacaoEtapa(membro, edital, etapa_id, ativo)`; trilha `ALOCACAO_INCLUIR` / `ALOCACAO_REMOVER` **[C]** |
| Papel | `comissao:gerir` ou presidência **[C]** |
| URL | `processos/<id>/comissao` e `processos/<id>/alocacoes` (`interface/urls.py:447-454`), views `views.py:6033` e `:6167` **[C]** |

A alocação **não** consulta forma, caráter nem regra da Etapa. Dá para alocar numa Etapa que nunca
poderá ser consolidada **[C, pela ausência no código citado]**.

### 1.2 Distribuição (012): quem avalia qual inscrição

| | |
|---|---|
| Serviço | `avaliacoes/application/distribuicao.py:270` `distribuir` (manual, uniforme); `:445` `propor_rodizio` (não grava nada); `:485` `confirmar_rodizio` (grava); `:645` `remover_atribuicao` **[C]** |
| Erros do pedido (desfazem o lote) | `selecao_vazia`; `inscricoes_em_curso` (409) enquanto o período de inscrições está aberto ou é futuro (`avaliacoes/domain/conjunto.py:68-94`, chamado em `distribuicao.py:141-149`, nos três caminhos); `pessoa_nao_e_membro_ativo`; `avaliador_sem_alocacao` (`:159-187`); `inscricao_nao_atribuivel` (não submetida); `inscricao_fora_da_etapa`, com frase de `prontidao.motivo_de_nao_participar` — eliminada antes, aguardando a anterior, ou fora da faixa (`:190-233`); `proposta_mudou` no rodízio (`:546`) **[C]** |
| Recusas de linha (o lote segue) | impedimento, atribuição já existente, conclusão anterior da mesma pessoa, excesso sobre o teto `avaliacoes_previstas` (+1 com reavaliação pendente) (`:300-379`) **[C]** |
| Evidência | `Atribuicao(membro, edital, etapa_id, inscricao, ativo)` (`avaliacoes/models.py:36-74`); trilha `AVALIACAO_ATRIBUIR`, uma por atribuição **[C]** |
| Papel | gestão da comissão **[C]** |
| URL / template / volta | `editais/<id>/distribuicao/<etapa_id>` (`urls.py:463-467`), view `views.py:6748-6880`, `interface/distribuicao.html`. POST-redirect-GET para a própria distribuição, com o resultado declarado na sessão **[C]** |

A remoção de atribuição com avaliação concluída é recusada (`MOTIVO_DE_FR_092`,
`distribuicao.py:57-61`). As saídas são o impedimento (`avaliacoes/application/impedimento.py:157`
`registrar_impedimento`, URL `.../impedimentos`) ou a reabertura **[C]**.

### 1.3 Avaliação (Mesa, 012)

| | |
|---|---|
| Serviço | `avaliacoes/application/avaliacao.py:142` `gravar` (rascunho) e `:197` `concluir` **[C]** |
| Autorização | `pode_avaliar_inscricao` = alocação ativa e Etapa no vigente (`comissoes/domain/autorizacao.py:152-176`) + participação (`prontidao.participa_da_etapa`) + Atribuição ativa (`avaliacoes/domain/autorizacao.py:42-73`). Tudo que falha responde 404 **[C]** |
| Recusas de `concluir` | `avaliacao_concluida` (409); `inscricao_ja_tem_resultado` (409, RC-62, salvo reavaliação pendente: `:345-400`); `versao_nao_reconhecida` (422); `versao_mudou` (409: "O Edital foi retificado enquanto você avaliava…"); campo da outra forma (`_recusar_campo_da_outra_forma`, `:119-140`); `parecer_obrigatorio` (422) no sentido desfavorável (decisória) ou com nota abaixo da mínima em eliminatória (pontuada); `stale_revision` (412) — `:197-301` **[C]** |
| Período | `_fora_do_periodo` (`avaliacoes/application/mesa.py:223-246`) é **informado, não aplicado**: a Mesa avisa, e concluir fora do prazo é admitido **[C]** |
| Evidência | `Avaliacao(estado RASCUNHO/CONCLUIDA, forma, pontuacao xor sentido, versao, concluida_por)`, com a constraint `ck_avaliacao_concluida_completa` (`avaliacoes/models.py:77-177`); `ConclusaoAvaliacao`, append-only, uma por conclusão (`:180-231`); trilha `CONCLUIR` sem nota **[C]** |
| Papel | o **avaliador alocado e atribuído**. Presidir não dá Mesa (`autorizacao.py:152-158`, "presidir não é atuar") **[C]** |
| URL / volta | `minhas-etapas/<edital>/<etapa>` (Mesa, `views.py:10208`), `.../inscricoes/<id>` (`views.py:6906`), `.../avaliacao` e `.../avaliacao/concluir` (`urls.py:788-817`). Depois de concluir, `_para_a_proxima` leva à **próxima pendente da Mesa**, ou fica na inscrição com "Não há mais inscrições pendentes suas nesta Etapa." (`views.py:7050-7115`) **[C]** |

A reabertura é da **presidência ou do gestor**: `avaliacao.py:505` `reabrir`, com motivo
obrigatório, `transicao_invalida` se não estiver concluída e `avaliacao_fundamenta_resultado` (409)
se já houver Resultado. A frase manda ao recurso (`:423-476`). URL `.../reabrir`
(`urls.py:493`) **[C]**.

### 1.4 Conclusão pontuada e decisória → consequência

`resultados/domain/regra.py` **[C]**:

- **Pontuada**: elimina se é eliminatória, tem mínima publicada e a nota fica abaixo dela. Sem
  caráter eliminatório, habilita sempre (`:100-127`).
- **Decisória**: só é consolidável se for **eliminatória**. `DESFAVORAVEL` vira `ELIMINADA` e
  `FAVORAVEL` vira `HABILITADA`, com o rótulo publicado no motivo (`:130-143`).
- **Impedimentos da Etapa inteira** (`impedimento_da_regra`, `:57-97`):
  - mais de uma avaliação prevista → `regra_de_combinacao_ausente`;
  - pontuada eliminatória sem mínima → `regra_insuficiente`;
  - decisória não eliminatória → `regra_insuficiente`.

  Na publicação do Edital, esses impedimentos **impedem** a publicação quando um marco consome a
  Etapa (enumerada e não porta, governada ou de habilitação) ou quando ela é eliminatória. Fora
  disso são só advertência (`editais/domain/validation.py:2085-2135`) **[C]**.

### 1.5 Consolidação: o Resultado da Etapa (013, app `resultados`)

| | |
|---|---|
| Serviço | `resultados/application/consolidacao.py:315` `consolidar`; leitura prévia em `:282` `prever` e `:296` `prever_as_prontas` **[C]** |
| Prontidão | `resultados/application/prontidao.py:515-588` `panorama_da_etapa` faz uma partição de toda inscrição submetida em `eliminada-antes`, `aguardando-anterior`, `fora-do-corte`, `consolidada`, `pronta`, `nao-consolidavel` e `reavaliacao-determinada`, com `contagens` (`:625-652`) **[C]** |
| Erros do pedido | o bloqueio da Etapa (`regra_*`, ou `corte-obsoleto`: "a faixa que governa esta Etapa está para trás…", `:164-201`) sai como `DomainError` 422; `nada_pronto` ("Nenhuma inscrição desta Etapa está pronta para consolidar agora."); `selecao_vazia`; `inscricao_nao_consolidavel`; `inscricao_fora_da_etapa` (`consolidacao.py:84-123`, `:235-279`) **[C]** |
| Recusas de linha | `SEM_CONCLUSAO`; `CONCLUSOES_DEMAIS`; incompatibilidade de norma (`resultados/domain/compatibilidade.py`); `SEM_REAVALIACAO`; `PIORARIA` (`consolidacao.py:126-230`, `prontidao.py:598-622`) **[C]** |
| Evidência | `ResultadoEtapa(origem AVALIACAO, avaliacao, versao, forma, pontuacao/sentido, consequencia, consolidado_por)`, append-only nas três camadas; o vigente é lido por `ResultadoEtapa.vigentes` **[C]** |
| Papel | gestão da comissão (presidência ou `comissao:gerir`) **[C]** |
| URL / volta | `.../distribuicao/<etapa>/consolidar` (`urls.py:471`), view `views.py:6476-6558`. Primeiro passo: `interface/consolidacao_confirmar.html`, com o total por consequência. Depois do ato, volta à **distribuição** (`destino`, `:6496`) **[C]** |

O **desfecho sem avaliação** é a Ocorrência: `resultados/application/ocorrencia.py:129`
`registrar_ocorrencia`. É sempre `ELIMINADA`, com motivo obrigatório, e funciona até em Etapa
bloqueada para consolidar (`:1-33`). URL `.../ocorrencia` (`urls.py:478`), view `views.py:6561`
**[C]**.

### 1.6 Divergência entre avaliadores

Não há ato nem estado de divergência **[C]**:

- Com `previstas > 1`, a Etapa inteira cai em `regra_de_combinacao_ausente` e nada consolida
  (`regra.py:71-76`).
- Com `previstas == 1` e mais de uma conclusão elegível (a quantidade mudou depois), a linha cai em
  `CONCLUSOES_DEMAIS` ("o sistema não escolhe qual vale", `prontidao.py:93-95`, `:613-616`).
- A única "divergência" nomeada é a de **norma**: a conclusão foi feita sob uma versão incompatível
  com a vigente (`compatibilidade.incompatibilidade`, `prontidao.py:617-621`).

### 1.7 Publicação do resultado da Etapa

Não existe (ver 0.1) **[C]**. O efeito equivalente nasce da `PublicacaoResultado` do marco que
enumera a Etapa: visibilidade (`resultados/application/selectors.py:170-222`) e janela recursal
(`recursos/application/interpor.py:164-227`) **[C]**.

### 1.8 Recurso e reavaliação (018, 036)

- **Interpor** (titular, no portal): `recursos/application/interpor.py:44`. O objeto é
  `PublicacaoResultado` **ou** `ResultadoEtapa` (`recursos/models.py:58-71`, XOR). As recusas são
  `appeal_reason_required`, `appeal_target_superseded`, `appeal_not_visible` (404),
  `appeal_already_filed`, `appeal_window_closed` e "não admite" (`NAO_PREVISTO`). A janela contra
  o Resultado da Etapa é a mais generosa entre os marcos que **enumeram** a Etapa
  (`:164-260`) **[C]**.
- **Instruir**: gestão da comissão (`recursos/application/instruir.py:216-218`). URL
  `recursos/<id>/instruir` **[C]**.
- **Admitir e julgar**: permissão própria `recurso:julgar` (`recursos/application/admitir.py:26`,
  `julgar.py:55`), com impedimento reavaliado sob trava (`porta.py:51-56`, recusa 403). As espécies
  são `INDEFERIDO`, `CORRECAO_FIXADA` (cria o sucessor do Resultado na hora, `julgar.py:64-65`),
  `REAVALIACAO_DETERMINADA` e `PROVIDENCIA_A_JUSANTE` (`recursos/models.py:174-178`). URLs
  `recursos/<id>/admitir` e `/julgar` (`urls.py:772-786`) **[C]**.
- **Cumprir a reavaliação**: abre uma vaga a mais na distribuição (`distribuicao.py:316-327`). Um
  **outro** avaliador conclui, porque RC-62 cede para o par pendente (`avaliacao.py:385-386`), e a
  presidência consolida pela seleção, não pelo botão "prontas" (`consolidacao.py:252-265`). O
  sucessor cita a decisão. A pendência é derivada: `recursos/application/selectors.py:298`
  `reavaliacoes_pendentes` **[C]**.

---

## 2. O que a ordem exige das Etapas enumeradas

### 2.1 `calcular_ordem` (`classificacao/application/calculo.py:21-178`)

**[C]**

- O universo é o das submetidas do Perfil e do recorte, restritas por `restringir_a_participantes`
  na **última Etapa enumerada** (`:61-77`, `_ultima_etapa` `:192-200`). Isso significa: não
  eliminada em Etapa anterior; habilitada na imediatamente anterior, se esta já tiver Resultado e
  puder habilitar; dentro da faixa, se um corte governar essa Etapa.
- Lê os `ResultadoEtapa.vigentes` das Etapas enumeradas e das de desempate (`:102-119`).
- `universo_classificavel.preparar` (`classificacao/domain/universo_classificavel.py:25-101`):
  - eliminado numa Etapa enumerada → sem posição, com a consequência dela;
  - falta pontuação numa enumerada pontuada → sem posição, com o motivo
    **"Sem pontuação nas Etapas enumeradas: X, Y."** (`:126-134`);
  - Etapa decisória enumerada é **porta** e não parcela (`combinacao.py:93-100`, `:119-122`).
    Marco só de portas dá pontuação `None`, um grupo único (`:130-134`).
- **Recusas**: só `not_found`, `marco_sem_etapa` (`:195-199`) e `resultado_sem_norma`
  (`:203-215`). `RegraIncompleta` sobe como erro interno quando falta peso ou arredondamento
  (`combinacao.py:48-77`) **[C]**.

### 2.2 `emitir_ordem` (`classificacao/application/emissao.py:21-182`)

**[C]**

- Recusa `ordering_milestone_is_drawn` em marco de sorteio (`:231-259`),
  `ordering_confirmation_required` (`:116-121`), `stale_ordering_calculation` /
  `ordering_act_already_exists` (`:123-140`) e `ordering_succession_reason_required` (`:141-147`).
- **Nenhuma recusa por Etapa não avaliada, não consolidada ou parcialmente consolidada.**
- Grava `AtoDeOrdenacao` e faz `bulk_create` de `PosicaoNaOrdem` para `posicoes` **e** para
  `sem_posicao` (`:148-163`).

### 2.3 Caso do Edital 91: 12 inscrições, nenhuma avaliação, nenhum Resultado

- **[C]** `emitir_ordem` grava a ordem: um ato com zero posições e uma `PosicaoNaOrdem` sem posição
  por participante considerado (`emissao.py:160-163`). Nada na cadeia
  view → `estado_do_marco` → `calcular_ordem` → `emitir_ordem` recusa por falta de Resultado:
  - `estado_do_marco` (`classificacao/application/selectors.py:317-400`) só desvia para sorteio,
    para marco removido ou para comparação com o vigente;
  - a view `emitir_ordenacao` (`interface/views.py:7715-7822`) só desvia marco de sorteio;
  - o formulário aparece quando `pode_emitir and recomputavel`
    (`interface/templates/interface/ordenacao.html:253`), e `pode_emitir` é só
    `pode_gerir_comissao` (`views.py:7349`).
- **[C]** Mensagens na tela da ordem: `"Nenhum participante recebeu posição neste recorte."`
  (`ordenacao.html:208`), seguida da tabela "Participantes considerados sem posição" com a coluna
  **Motivo** (`ordenacao.html:211-218`). Ali cada linha deveria ler "Sem pontuação nas Etapas
  enumeradas: …" (`universo_classificavel.py:126-134`).
- **[C]** A confirmação em dois passos (`interface/templates/interface/ordenacao_confirmar.html:44-53`)
  mostra "Participantes com posição: 0" e "Participantes sem posição: N — protocolos…". **Não diz o
  motivo** e não diz que nenhuma Etapa foi consolidada.
- **[I]** Se a tela do 91 mostra "Nenhum participante recebeu posição" **sem** a tabela de sem
  posição, então o universo saiu vazio, e não com 12 sem pontuação. Causas possíveis: participação
  restrita por eliminação anterior, gate da anterior, ou faixa de corte governando a última Etapa
  enumerada. Vale conferir `estado["proposta"]["sem_posicao"]` no shell.
- **[C]** O ato não fica preso para sempre. Quando os Resultados chegarem, `comparar` aponta
  `participantes_alterados` / `resultados_alterados` (`classificacao/domain/universo.py:82-123`),
  o ato fica obsoleto e a sucessão exige motivo.
- **[C]** Também não há guarda na divulgação: os códigos de `divulgacao/domain/publicabilidade.py:34-54`
  não incluem "ordem vazia" nem "Etapa sem Resultado". **[I]** Só um teste ponta a ponta
  confirmaria se outra condição barra a publicação de uma ordem vazia.
- **[C]** A guarda que existe está **antes**: a publicação do **Edital** impede a Etapa que um
  marco enumera e que nunca poderia ser consolidada (`validation.py:2024-2067`). Ela fala da norma,
  não da execução.

---

## 3. A Etapa decisória fora de marco

### 3.1 Mecanismos gerais

Lidos todos do conteúdo publicado **[C]**:

| Mecanismo | Onde | Precisa estar em marco? |
|---|---|---|
| **Regra 1**: eliminada em qualquer Etapa anterior sai de todas as seguintes | `resultados/application/prontidao.py:438-448`, `resultados/domain/progressao.py:47-70` | não, só da `order` |
| **Regra 2**: só segue quem foi habilitado na **imediatamente anterior**, depois que ela produz Resultado e se ela puder habilitar | `prontidao.py:378-405`, `:449-459` | não |
| **Regra 3**: a faixa do corte restringe quem participa da Etapa **governada** | `prontidao.py:263-354`, `:460-473` | sim, governada por `cutRule` |
| Universo da ordem: participantes da **última enumerada** (regras 1 a 3 aplicadas a ela) | `calculo.py:71-77` | a Etapa anterior não enumerada filtra pela progressão |
| Ocupação e convocação contam como habilitado quem tem `HABILITADA` vigente na Etapa **governada** pelo corte (ou toda a faixa, se `NONE`) | `ocupacao/application/selectors.py:457-497`, `:594`; `ocupacao/application/emissao.py:168`; `convocacao/application/selectors.py:157` | sim, governada |
| Relação do sorteio filtrada pelo `HABILITADA` na Etapa de habilitação | `sorteios/application/habilitacao.py:14-28`, `sorteios/application/relacao.py:296-310` | sim, `qualifyingStageId` |
| Visibilidade e recurso do Resultado pelo titular | `resultados/application/selectors.py:213-222`; `interpor.py:189-200`, `:317-332` | sim, **enumerada** |
| Relatório do Edital: linhas por Etapa | `interface/relatorio_do_edital.py:400-409` (enumeradas e governadas) | sim |
| Pendências e encerramento | `processos/application/pendencias_do_edital.py:87-240` só olham recursos e decisões por marco **enumerado** (`recursos/application/selectors.py:445-454`) | — |

Pontos que valem para todos os casos:

- **[C]** Nenhuma Etapa bloqueia o **encerramento** nem o **desfecho** por estar sem avaliação ou
  sem consolidação. `pendencias_do_edital.situacoes` não lê `panorama` nem `resumo_da_etapa`.
- **[C]** A Etapa que só filtra pela progressão bloqueia indiretamente: enquanto não consolida, a
  Regra 2 fica dormente (`prontidao.py:400-405`) e a seguinte segue com todos. Assim que **um**
  Resultado entra, quem ainda não tem Resultado nela passa a `aguardando-anterior` na seguinte.

### 3.2 Os quatro casos

**(a) Marco por pontuação com duas pontuadas; o corte governa "Análise documental" (decisória, fora
de marco).**

- **[C]** A Análise documental só recebe quem progrediu na faixa (Regra 3). Ela bloqueia a
  consolidação inteira enquanto o corte estiver obsoleto (`prontidao.py:164-201`).
- **[C]** O `HABILITADA` dela é o que ocupação e convocação contam, e por isso o publicador do
  Edital é obrigado a torná-la consolidável (`validation.py:2062-2067`). Sem consolidar a Análise
  documental, ninguém conta como ocupante nem é chamável. É **pré-requisito real** da
  apuração e da convocação.
- **[C]** Ela não entra na ordem, que é calculada antes.
- **[C]** O Resultado dela **não fica visível ao titular nem é recorrível pelo sistema**: nenhum
  marco a enumera (seção 3.1).
- **[I]** Se for desejado que ela seja recorrível, isso é achado, não defeito da proposta.

**(b) Marco por pontuação que não governa Etapa (terminal ou sem corte); heteroidentificação
decisória fora de marco.**

- **[C]** Sem ligação de marco, ela vale só pela progressão: o `ELIMINADA` dela tira a pessoa das
  Etapas de `order` maior. Se ela for anterior à última enumerada, também tira a pessoa do universo
  da ordem.
- **[I]** Se for posterior às Etapas do marco, ela **não tem efeito** em ordem, corte, ocupação ou
  convocação. Com corte `NONE`, ocupação e convocação usam a faixa inteira
  (`ocupacao/application/selectors.py:477-497`).
- **[C]** Não é visível nem recorrível pelo titular e não aparece no relatório.
- **[C]** Se não for eliminatória, nem consolida (`regra_insuficiente`): só advertência na
  publicação, e só Ocorrência registra desfecho nela.

**(c) Marco de sorteio sem Etapa; duas decisórias fora de marco.**

- **[C]** O marco entra no começo da jornada (`classificacao/domain/jornada.py:150-155`). Cada
  decisória vale pelo que o método e o corte declaram:
  - se uma é `qualifyingStageId`, a relação do sorteio exige que ela esteja **consolidada antes**,
    porque `habilitadas_na_etapa` lê `HABILITADA` vigente;
  - se uma é `governedStage`, ela segue o caso (a);
  - sem nenhuma das duas, segue o caso (b).
- **[I]** Pela descrição, a forma provável é o sorteio que precede a análise documental
  (`jornada.py:15-16`, FR-432), com corte governando a primeira decisória. Confirmar no conteúdo.

**(d) Marco de sorteio que enumera uma decisória chamada "Sorteio".**

- **[C]** No sorteio, a Etapa enumerada **não entra na ordem** (`faixa.py:93-97`,
  `prontidao.py:271-272`). `emitir_ordem` recusa o marco (`emissao.py:231-259`).
- **[C]** A enumeração ainda tem efeitos: autoriza a visibilidade e o recurso do Resultado dessa
  Etapa depois da publicação do marco. Põe a Etapa no relatório. Faz `reavaliacoes_pendentes_do_marco`
  considerá-la. O reingresso é ignorado em marco sorteado (`publicabilidade.py:317`).
- **[C]** Por ser porta, a validação não a exige (`validation.py:2036-2042`, `:2057-2058`).
- **[I]** É uma Etapa que existe só para satisfazer a validação antiga (comentário em
  `faixa.py:93-97`). Ela aparece na Mesa e é distribuível (a alocação e a distribuição não leem
  forma nem caráter). Se não for eliminatória, não consolida. **Para o "andamento", ela gera uma
  coluna de avaliação que ninguém precisa preencher.** A proposta precisa de regra para não cobrar
  "falta avaliar" de Etapa enumerada por marco de sorteio que ninguém consome.

---

## 4. Derivações que já existem do andamento das Etapas

| Derivação | Onde | Responde | Granularidade | Custo |
|---|---|---|---|---|
| **Minhas Etapas** | `interface/views.py:10170`, `comissoes/application/selectors.py:204` `minhas_etapas`, `avaliacoes/application/selectors.py:371-436` `carga_nas_etapas` | "falta avaliar N" **do próprio avaliador** (pendentes e concluídas, com progressão aplicada) | Etapa × Edital; sem Perfil | uma leitura do conteúdo por Edital + **uma agregação**; teto de 10 consultas (`tests/performance/test_comissao_em_escala.py`) **[C]** |
| **Mesa** | `views.py:10208`, `avaliacoes/application/selectors.py:306` `mesa` | pendentes, rascunhos e concluídas do avaliador | Etapa | teto de 22 (`tests/performance/test_escala_da_mesa.py:170`) **[C]** |
| **Distribuição / resumo** | `avaliacoes/application/selectors.py:200-282` `resumo_da_etapa` + `panorama.contagens` | `carentes` (sem avaliador suficiente), `sem_nenhum`, `sem_conclusao` (**falta avaliar**), `prontas` (**falta consolidar**), `consolidadas`, `nao_consolidaveis`, `reavaliacoes`, `fora_do_corte`, `eliminadas_antes`, `aguardando_anterior` | **Etapa inteira, sem corte por Perfil** **[C]** (a população é de todos os Perfis do Edital) | panorama de custo constante (prontidão, `prontidao.py:1-17`) + uma agregação + um count **[C]**; o teste de escala só prende que não cresce (`test_escala_da_mesa.py:306`) |
| **Supervisão UX-003** | `interface/supervisao.py:625-653` | Etapa com inscrição carente de avaliador (`carentes/inscricoes`) | Etapa | um `resumo_da_etapa` (sem panorama) **por Etapa por Edital** (`:598-622`) **[C]** |
| **Supervisão UX-063** | `supervisao.py:656-689` | avaliação distribuída e não concluída (`completas − avaliadas`) | Etapa | a mesma leitura do UX-003 **[C]** |
| **Trabalho (104)** | `interface/trabalho.py:176-196` | "Avaliar (N pendentes)" do próprio ator, levando à `minha-etapa` | Etapa | o custo de Minhas Etapas **[C]** |
| **`pendencias_do_edital`** | `processos/application/pendencias_do_edital.py:61-84`, `:220-240` | `REAVALIACAO_PENDENTE` e `PROVIDENCIA_PENDENTE` **por marco**, só se o marco tem publicação; `RECURSO_AGUARDANDO` | marco | duas consultas por marco + a contagem de recursos **[C]** |
| **Relatório do Edital** | `interface/relatorio_do_edital.py:400-409`, `:566-576`, `:1043-1061` | por **Perfil × Etapa**: avaliadas, habilitadas, eliminadas, por ocorrência, `registrada` | Perfil × Etapa (só enumeradas e governadas) | **uma** agregação de `ResultadoEtapa.vigentes` para o Edital **[C]** |
| **Prévia, jornada** | `classificacao/domain/jornada.py` | ordem Etapas ↔ marcos, `porta`, `etapa_alimentada` | Perfil | pura **[C]** |

O que **não** existe hoje **[C, pelas leituras acima]**:

- **"falta consolidar" na Atenção da Supervisão.** Não há espécie para `prontas > 0`. Esse número só
  aparece na tela da distribuição.
- **"falta avaliar" ou "falta consolidar" por Perfil.** O resumo é por Etapa sobre o Edital todo.
  **[I]** Para quebrar por Perfil, seria preciso anotar `profile_id` no panorama: ele já lê as
  inscrições (`prontidao.py:120-137`), então dá para trazer o Perfil na mesma consulta sem custo
  extra.
- **"falta publicar o resultado da Etapa"**: a pergunta não tem ato (seção 0.1). O equivalente é
  "o marco que enumera esta Etapa tem publicação vigente?" (`resultados/application/selectors.py:194-205`).
- **[C]** `interface/conducao_do_marco.py` (049) só tem quatro operações (ordem, corte, apuração,
  publicação) e nenhum pré-requisito de Etapa.

---

## 5. Quem responde por cada ato

| Ato | Responsável | Base no código |
|---|---|---|
| Compor a comissão, alocar | `comissao:gerir` ou presidência | `comissoes/domain/autorizacao.py:81-97` **[C]** |
| Distribuir, remover atribuição, impedimento | idem | `distribuicao.py:288`, `views.py:6314-6351` **[C]** |
| Avaliar e concluir | avaliador **alocado na Etapa e atribuído à inscrição** | `avaliacoes/domain/autorizacao.py:42-73` **[C]** |
| Reabrir avaliação | gestão da comissão | `avaliacao.py:505-540` **[C]** |
| Consolidar, Ocorrência | gestão da comissão | `consolidacao.py:315-330`, `ocorrencia.py:1-13` **[C]** |
| Instruir recurso | gestão da comissão | `instruir.py:216-218` **[C]** |
| Admitir e julgar recurso | `recurso:julgar`, sem impedimento | `admitir.py:26`, `julgar.py:55`, `porta.py:51-56` **[C]** |
| Emitir ordem e corte | gestão da comissão (`somente_gestao=True`) | `views.py:7724`, `:7349` **[C]** |
| Publicar resultado do marco | `resultado:publicar` | `supervisao.py:1347-1350` **[C]** |

Representação na spec 104 **[C]**: `interface/trabalho.py:176-196` só emite o objeto `avaliacao`
para o **avaliador** com pendências: título "Etapa — Edital", ato "Avaliar (N pendentes)" e
destino `interface:minha-etapa`. **Não** há objeto para a presidência ("distribuir", "consolidar
N prontas", "registrar ocorrência"), e o texto `FORA_DA_FAIXA` (`:45-48`) declara que
classificação e divulgação ficam fora.

---

## 6. Convocação para Etapa (entrevista, heteroidentificação)

**Não implementada.**

- `doc/registro-convocacao-para-etapas-2026-10-09.md` registra a capacidade como futura e não
  priorizada, com perguntas em aberto.
- O que existe: a Etapa aponta um único Evento (`scheduleEventId`, mostrado na Mesa,
  `views.py:10235-10248`), e a ausência vira Ocorrência (`ocorrencia.py`).
- `Convocacao` (019) é para vaga, sobre a faixa e o `HABILITADA` da Etapa governada. **[C]** grep
  sem ocorrência de modelo ou serviço de convocação para Etapa; nenhuma spec entre 115 e 122 o
  trata (só nomes de pasta conferidos).
- **[C]** O desfecho da convocação **para vaga** pode gerar um `ResultadoEtapa` de origem
  `REGULARIZACAO`, com `desfecho_de_convocacao_id` (`resultados/models.py:66`, `:166`, `:196-214`).
  É o caminho inverso (convocação → Resultado), e não convocação para comparecer a uma Etapa.

---

## 7. Métodos de ordenação implementados

**[C]**

- **Origem da ordem**: só `COMPUTADO` ("Computado a partir de Etapas") e `SORTEIO`
  (`classificacao/models.py:18-22`). A forma é declarada por `orderProduction` = `POR_PONTUACAO` ou
  `POR_SORTEIO` (`editais/domain/marcos.py:29-30`, `:114-141`).
- **Combinação no computado**:
  - `SOMA_PONDERADA` e `MEDIA_PONDERADA`, normalização `PELA_SOMA_DOS_PESOS`;
  - arredondamento `MEIO_PARA_CIMA`, `MEIO_PARA_PAR` ou `TRUNCAR`, escala de 0 a 4;
  - peso lido da Etapa;
  - decisória enumerada é porta (`classificacao/domain/combinacao.py:21-163`).
- **Desempate** (`classificacao/domain/desempate.py:25-32`): `MAIOR_PONTUACAO_NA_ETAPA` (inclusive
  de Etapa não enumerada, 114), `MAIOR_VALOR_DE_FATO`, `MENOR_VALOR_DE_FATO`, com
  `whenMissing` = `ULTIMO_NO_CRITERIO` / `CRITERIO_NAO_SE_APLICA`. O empate residual **não** é
  resolvido: as pessoas compartilham a posição (1, 1, 3) (`:14-20`).
- **Desempate dentro do sorteio**: chave crescente e, depois, número público crescente
  (`sorteios/domain/chave.py:88-92`).
- **Não existem**: ordem de inscrição ou protocolo como método, nem sorteio como desempate de ordem
  computada (busca por termos, sem ocorrência em `classificacao` nem em `editais/domain`).
- **"CR" (096)** é só impressão de cadastro de reserva sem vaga imediata, não método de ordenação
  (`specs/096-cadastro-de-reserva-como-cr/spec.md`).

---

## Consequências para a proposta

Inferências **[I]**:

1. **As colunas por ato precisam ser por ligação da Etapa ao marco, e não por "Etapa".** A forma
   genérica para todas as classificações é: enumerada (avaliar → consolidar → pesa na ordem e fica
   visível ao titular na publicação do marco), governada (avaliar → consolidar → condiciona ocupação
   e convocação), habilitação do sorteio (consolidar antes da relação), e só progressão (filtra as
   Etapas seguintes). Sorteio e pontuação só diferem em de onde vem a ordem.
2. **"O que fazer agora" para a presidência não tem fonte pronta por Perfil.** `panorama.contagens`
   dá, por Etapa, avaliar (`sem_conclusao`), distribuir (`carentes`) e consolidar (`prontas`).
   Quebrar por Perfil pede uma anotação a mais. A faixa da 104 só cobre o avaliador.
3. **Falta uma guarda ou um aviso de "nenhuma Etapa enumerada consolidada"** antes de emitir a
   ordem, e a confirmação não diz o motivo de ninguém ter posição. Isso é achado para registrar, não
   escopo.
4. **Etapa decisória fora de marco e não governada não é recorrível nem visível ao titular** pelo
   sistema. É achado de governança, a registrar.
5. **A Etapa decisória enumerada por marco de sorteio** (caso d) precisa ser tratada como "sem
   cobrança de andamento", senão a orientação manda avaliar o que ninguém consome.
