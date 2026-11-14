# Research: As regras de deliberação dos pareceres

Decisões técnicas da `165`. Cada uma diz o que foi escolhido, por quê e o que foi descartado. Os
identificadores `T-` são locais a este documento.

## T-001 — A regra é uma coluna da Etapa, e um campo novo do conteúdo publicado

**Decisão.** `EtapaAvaliacao.regra_de_deliberacao`, texto de escolha fechada, vazio quando não
declarada: `MAIORIA`, `UNANIMIDADE_PARA_O_FAVORAVEL`, `UNANIMIDADE_PARA_O_DESFAVORAVEL`
(`editais/0031`). No conteúdo publicado, `deliberationRule` em cada item de `stages`: `"MAJORITY"`,
`"UNANIMOUS_FOR_FAVORABLE"`, `"UNANIMOUS_FOR_UNFAVORABLE"` ou `null`. É o **degrau 24**
(`SCHEMA_VERSION` 23 → 24), e a elevação escreve `null` em toda Etapa anterior.

**Por quê.** É o molde do efeito da `164` (colunas de elaboração, grafia publicada em inglês, degrau
com `null` para o acervo). A leitura do `null` é "sem regra", que é a verdade do acervo: a Etapa
colegiada publicada antes continua impedida (FR-7054, D-002).

**Descartado.** Um inteiro ou um booleano por regra: três regras exclusivas são uma escolha, e o
`null` precisa existir para o acervo.

## T-002 — A publicação grava a regra só na Etapa colegiada

**Decisão.** `resultados/domain/deliberacao.py::publicar(item, coluna)` devolve `deliberationRule`
explícito só quando a Etapa é decisória e prevê mais de uma avaliação; `null` em toda outra. A
composição só **lê** o campo nessa Etapa (o formulário ignora o enviado nas demais, pela razão das
marcas do alcance e do efeito).

**Por quê.** Uma Etapa pontuada, ou de uma avaliação, com a regra escrita seria a coerência que a
FR-7053 recusa; não gravá-la é mais barato que recusá-la depois. O achado de coerência continua
existindo para o que chega por Retificação (T-003).

## T-003 — Três achados de publicação, e um só deles depende do ato

**Decisão.** `_coerencia_da_deliberacao(snapshot)`, em `editais/domain/validation.py`:

| Código | Quando | Ato |
|---|---|---|
| `regra_invalida` | valor fora dos três | publicação e Retificação |
| `regra_sem_colegiado` | regra declarada em Etapa pontuada ou de uma avaliação | publicação e Retificação |
| `maioria_com_numero_par` | `MAJORITY` com número par | publicação e Retificação |
| `deliberacao_sem_regra` | decisória com mais de uma avaliação e `null` | **só publicação** |

Na Retificação, a falta de regra é recusada por `retificacoes.py` **apenas** quando o ato toca a
Etapa: Etapa nova, forma, número de avaliações ou a própria regra (`_recusar_colegiada_sem_regra`).

**Por quê.** O conteúdo retificado é elevado ao degrau corrente antes da conferência, e por isso a
validação pura não distingue o acervo do que se compõe. Se a falta de regra fosse impeditiva em toda
Retificação, todo Edital do acervo com uma Etapa colegiada ficaria sem poder corrigir nada, nem um
prazo, até alguém declarar uma regra que a CPVA ainda não escolheu. A FR-7051 continua cumprida: a
Etapa que o ato compõe ou recompõe precisa declarar a regra.

**Descartado.** Ler a versão de origem do conteúdo para isentar o acervo: a elevação apaga essa
informação de propósito.

## T-004 — A Retificação da regra e do número para no primeiro Resultado por avaliação

**Decisão.** `_recusar_deliberacao_mudada_apos_resultado`, em `publicacoes/application/retificacoes.py`,
compara a regra e o número de avaliações **da Etapa decisória** entre a base e o conteúdo, e recusa
(`stage_deliberation_changed_after_result`) quando o seletor novo
`resultados_por_avaliacao_registrados(edital, etapa_id)` conta algum Resultado de origem `AVALIACAO`
ou `DELIBERACAO`, vigente ou superado. `_recusar_reducao_abaixo_das_conclusoes` recusa
(`stage_evaluations_below_concluded`) a redução do número abaixo do maior número de conclusões
elegíveis de uma inscrição, e conta quantas inscrições ficariam assim.

**Por quê.** É a forma do impedimento histórico da `164`, com o recorte da D-008: a regra decide
também o favorável. Os dois rodam sob o bloqueio do Processo que a consolidação toma (FR-7074).

## T-005 — O Resultado deliberado é uma origem nova, com os pareceres numa tabela à parte

**Decisão.**
- `ResultadoEtapa.Origem.DELIBERACAO`. O Resultado deliberado tem `avaliacao` nula, `forma`
  `DECISORIA`, `sentido` preenchido, `pontuacao` nula, e três campos novos: `regra_de_deliberacao`
  (a grafia publicada), `favoraveis` e `desfavoraveis` (inteiros). Nas outras origens, a regra é vazia
  e os dois inteiros são nulos.
- `ParecerDaDeliberacao` (append-only, `resultados_parecer_da_deliberacao`): `resultado` e
  `avaliacao`, com `avaliacao` **única** na tabela.
- A versão do Resultado deliberado é a da regra aplicada: a vigente no ato (D-006).

**Por quê.** Os readers de `origem` são poucos: o relatório separa Ocorrência de "avaliação" e conta a
origem nova com a avaliação, que é o certo. Os que leem `resultado.avaliacao` (impedimento, instrução,
parecer ao titular, supervisão) precisam aprender a ler os pareceres de qualquer forma, e a origem
nova diz a eles, por si, que a fonte é outra. Manter `AVALIACAO` com `avaliacao` nula afrouxaria a
constraint de hoje para todo Resultado por avaliação.

**Descartado.**
- `avaliacao` apontando para um dos pareceres, que escolhe qual valeu (D-006);
- um `JSONField` com os ids, que nenhuma chave estrangeira protege e que o append-only não alcança;
- uma `ManyToMany` do Django, que cria tabela sem gatilho nem privilégio.

## T-006 — A invariante de proveniência é revista com a mesma força

**Decisão.** A migração `resultados/0008` reescreve `resultado_etapa_coerente` e acrescenta:

1. no ramo `DELIBERACAO`: `avaliacao` nula, versão deste Edital (como o ramo da Ocorrência), regra e
   contagens presentes;
2. um gatilho em `ParecerDaDeliberacao`: o Resultado é `DELIBERACAO`; a Avaliação está concluída e é da
   mesma inscrição, do mesmo Edital e da mesma Etapa; e ela **não** é a `avaliacao` de Resultado
   nenhum;
3. o simétrico em `ResultadoEtapa`: a `avaliacao` citada não está em `ParecerDaDeliberacao`;
4. um gatilho de constraint **adiável** (`DEFERRABLE INITIALLY DEFERRED`) no `INSERT` do Resultado
   deliberado: ao fim da transação, os pareceres ligados somam `favoraveis + desfavoraveis`, e os
   favoráveis entre eles são `favoraveis`.

O ramo de uma avaliação fica palavra por palavra.

O banco confere a **contagem** e a coerência dos pareceres; a **regra** aplicada à contagem é do
domínio (`deliberacao.deliberar`), e a reprodução a confere (FR-7065). Escrever a tabela-verdade em
PL/pgSQL duplicaria a regra num segundo lugar, livre para divergir.

**Por quê.** A garantia de hoje é do banco, e a FR-7065 pede a mesma força. O adiável é o que permite
gravar o Resultado e os pareceres na mesma transação, em qualquer ordem, sem que um Resultado
deliberado sem pareceres sobreviva ao `COMMIT`.

## T-007 — Um módulo puro diz a regra e delibera

**Decisão.** `resultados/domain/deliberacao.py`, sem banco:
- `REGRAS`, `regra_publicada(etapa)`, `colegiada(etapa)` (decisória, mais de uma avaliação, regra
  declarada);
- `deliberar(regra, sentidos) -> Sentido`, pela tabela da FR-7050;
- `motivo(etapa, deliberacao)` (FR-7066) e `frase_da_regra(etapa)` (documento, Revisão e
  Retificação, FR-7075);
- `publicar`, `para_coluna`, `da_coluna`, no molde de `efeito.py`.

`regra.py` passa a aceitar a Etapa colegiada: `impedimento_da_regra` só devolve
`REGRA_DE_COMBINACAO_AUSENTE` quando a Etapa prevê mais de uma avaliação e **não** é colegiada; e
`consequencia(etapa, conclusao)` recebe uma `Deliberacao` (forma `DECISORIA`, o sentido deliberado e a
contagem), cujo motivo sai de `deliberacao.motivo`. A pontuada com mais de uma avaliação continua
impedida.

**Por quê.** A tabela-verdade inteira cabe num teste unitário (SC-2351), como a de `regra.py`.

## T-008 — A prontidão ganha "aguardando pareceres"

**Decisão.** Em `_estado_do_participante`, na Etapa colegiada: com menos conclusões elegíveis que o
número previsto, o estado é `AGUARDANDO_PARECERES`, com o motivo "faltam k de N pareceres"; com
exatamente N, cada uma passa pela incompatibilidade de hoje, e a inscrição está pronta; com mais, o
`CONCLUSOES_DEMAIS` de hoje. `contagens` ganha `aguardando_pareceres`, e o resumo da Etapa o mostra à
parte (FR-7079).

**Por quê.** Hoje a falta de conclusão é `NAO_CONSOLIDAVEL` com "sem conclusão". Na colegiada, a
inscrição com dois de três pareceres não está impedida: está a caminho, e a presidência precisa
distinguir as duas coisas.

## T-009 — A consolidação delibera dentro do plano que já existe

**Decisão.** `_planejar` passa a montar, na Etapa colegiada, uma `Deliberacao` com os N pareceres do
panorama, e `Consolidavel` a carrega. O ato cria o Resultado `DELIBERACAO` com a versão vigente
(`selecao_publica`, lida uma vez antes do laço) e os pareceres em `bulk_create`. A trilha continua um
evento por Resultado, com a consequência e sem contagem (FR-7060).

O cumprimento de reavaliação numa Etapa colegiada não chega aqui, porque o julgamento o recusa (T-010);
se chegasse, `_planejar` o recusaria pela mesma frase.

**Por quê.** Uma regra para o ato e para a conferência (FR-7067): a previsão e o ato leem o mesmo
plano.

## T-010 — O julgamento recusa a reavaliação colegiada antes de gravar

**Decisão.** Em `recursos/application/julgar.py`, depois do impedimento e da admissão e antes de
`_gravar`: se a espécie é `REAVALIACAO_DETERMINADA` e a Etapa do par é colegiada (o Resultado
protegido é `DELIBERACAO`, ou a Etapa vigente é colegiada), recusa com
`reavaliacao_colegiada_indisponivel` (422). A reserva de idempotência nasce dentro da mesma transação
e some com a recusa. A tela de julgamento não oferece a espécie nesse caso, e diz por quê.

A correção fixada continua o caminho de hoje: o julgador informa o sentido, `regra.consequencia`
deriva a consequência, e o sucessor é `RECURSO`, sem contagem (FR-7070).

## T-011 — Impedimento, instrução e supervisão leem os pareceres da deliberação

**Decisão.**
- `recursos/domain/elegibilidade.py`: impedido quem concluiu algum parecer ligado ao Resultado
  deliberado, e quem tem Atribuição ativa sem conclusão vigente sobre o par (FR-7069). O segundo vale
  para toda Etapa colegiada.
- `recursos/application/instruir.py`: a peça mostra ao julgador todos os pareceres, com autoria
  (FR-7081).
- `interface/supervisao.py`: o conjunto dos impedidos ganha os autores dos pareceres.

## T-012 — O titular lê os pareceres desfavoráveis da deliberação

**Decisão.** `recursos/application/selectors.py::pareceres_do_titular` devolve, para o Resultado
deliberado desfavorável, a **lista** dos textos dos pareceres desfavoráveis ligados a ele, lidos das
conclusões preservadas, nas mesmas condições da `036`. O template do acompanhamento passa a desenhar
uma lista. O motivo do Resultado já diz a regra e a contagem (FR-7066), e é ele a linha da FR-7076.

A reabertura de parecer ligado a Resultado é recusada como a de hoje, por
`_recusar_se_fundamenta_resultado`, que passa a ler `ParecerDaDeliberacao`. Por isso o texto não muda
depois do Resultado.

## T-013 — O "às cegas" é uma função só, aplicada no servidor

**Decisão.** `avaliacoes/application/cegas.py`:
- `pendentes(subject, edital, etapa_id) -> set[inscricao_id]`: Atribuição ativa sem conclusão vigente,
  numa consulta;
- `ocultar(linhas, subject, pendentes)`: marca `oculta=True` e esvazia sentido, pontuação, parecer e
  critérios das conclusões de **outros** autores sobre as inscrições pendentes.

Aplicada só na Etapa colegiada, nos seletores que entregam conclusões a uma tela:
`conclusoes_preservadas`, `avaliacoes_inelegiveis` e a conferência da consolidação. As views passam o
`subject` do ator. A Mesa não muda: ela já entrega só a própria Atribuição (FR-7057), e o teste a
congela.

**Por quê.** Ocultar no template deixaria o dado no contexto, no fragmento htmx e no link direto. No
seletor, nada chega.

## T-014 — A exposição é uma tabela append-only, gravada na leitura

**Decisão.** `ExposicaoAoParecer` (append-only, `avaliacoes_exposicao_ao_parecer`): `edital`,
`etapa_id`, `inscricao`, `pessoa` (o `subject`), `registrada_em`; única por (`edital`, `etapa_id`,
`inscricao`, `pessoa`). `cegas.registrar_exposicao(subject, edital, etapa_id, inscricao_ids)` grava por
`bulk_create(ignore_conflicts=True)` as inscrições cujas conclusões de **outro** autor a tela entregou.
Chamada pelas views de conclusões preservadas, impedimentos e conferência da consolidação, numa
consulta por página.

`distribuir` e o rodízio recusam o membro exposto, com o motivo `exposto_aos_pareceres`, e
`reabrir` recusa a Avaliação cujo autor está exposto (`parecer_exposto`), oferecendo a inativação da
Atribuição (FR-7083).

**Por quê.** O fato que decide é a entrega (D-010). O `INSERT ... ON CONFLICT DO NOTHING` não é
`UPDATE` e passa pelo gatilho append-only. Gravar num `GET` tem precedente: a consulta de documento já
grava evento.

**Descartado.** Inferir a exposição da trilha de consulta: a trilha não guarda quais inscrições uma
página mostrou.

## T-015 — A composição mostra a pergunta só na Etapa colegiada

**Decisão.** No cartão da Etapa, um grupo de três rádios, nenhum marcado, com classe `so-decisoria`
(a folha o esconde na pontuada, como esconde os rótulos) e a classe `so-colegiada`, que o script da
composição alterna pelo número de avaliações. Sem JavaScript, o grupo aparece na decisória com a
frase "só vale com mais de uma avaliação por inscrição", e o servidor ignora a escolha quando o número
é um (T-002). Os rótulos das opções usam os rótulos publicados digitados no cartão (UX-750); sem eles,
"favorável" e "desfavorável".

`ler_etapas`, `etapas_do_edital`, `etapas_persistidas`, o serializer e `replace_draft` levam o campo,
no molde do efeito da `164`.

## T-016 — O documento, a Revisão e a Retificação dizem a regra com as mesmas palavras

**Decisão.** `deliberacao.frase_da_regra(etapa)`: "Cada inscrição recebe N pareceres, registrados por
membros da comissão sem conhecer o dos demais. O resultado é «X» quando …". Chamada em `pdf.py` (os
dois modos), em `apresentacao.py` e em `revisao.py` (linha "Deliberação"). A Retificação ganha o campo
em `CAMPOS_ETAPA`, com as quatro opções (a vazia diz "Não declarada"), e `alteracoes.CAMPOS` o
rótulo. A frase vazia das demais Etapas é o que recompõe o acervo byte a byte (SC-2350).

## T-017 — A conferência da consolidação mostra a contagem

**Decisão.** A tabela da confirmação ganha, por inscrição deliberada, "«desfecho» — k de N pareceres
«desfecho», por «regra»", e o total por desfecho continua o de `_por_consequencia` (UX-752).

## T-018 — Os guardiões que a feature alcança

- `test_leitores_da_consequencia.py`: nenhuma consequência nova; os leitores novos de
  `ResultadoEtapa.consequencia` (nenhum previsto) entram no inventário se aparecerem.
- `test_database_permissions.py`, `TABELAS_APPEND_ONLY`: duas tabelas novas, `M` de 59 para **61**. O
  `CLAUDE.md` e o README registram.
- A contagem de migrations por app em `tests/migrations/test_migrations.py`: editais 31, resultados 8,
  avaliacoes 6.
- `test_campos_vem_do_contrato.py` e o contrato de mutabilidade: `("stages", "deliberationRule")`.
- `test_citacoes_de_requisito.py` e `test_readme_acompanha_o_codigo.py`.

## T-019 — O que fica fora da implementação

- A prévia da classificação não simula deliberação (FR-7080): nada muda nela.
- O aviso por e-mail do desfecho.
- A reavaliação colegiada (P-5).
