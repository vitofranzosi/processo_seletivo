# Research: Andamento da seleção (127)

As decisões de produto estão na spec (D-001 a D-016). Aqui ficam as escolhas de implementação, cada
uma com a alternativa descartada. Conferidas na `main` em `250efe97`.

## R-001 — Duas camadas no mesmo módulo: os fatos e as regras

**Decisão**: `interface/andamento.py` lê os fatos com as funções que já decidem cada tela
(`previa.recortes_do_marco`, `conducao_do_marco.indicador_do_marco`, `panorama_da_etapa` +
`resumo_da_etapa`, `leitura_do_recorte` + as três prévias da convocação, `publicabilidade.aferir`,
`trabalho.do_ator`) e entrega dicionários simples a funções puras — `situacao_da_relacao(fatos)`,
`situacao_da_etapa(fatos)`, … — que devolvem a `Celula`. A montagem das providências e a ordem do
nível 1 também são puras (`interface/providencias.py`).

**Por quê**: as sete situações em sete famílias são 49 combinações, e S3 e P3 não têm cenário no
banco. Funções puras testam todas sem banco; os testes de integração ficam para a coerência com as
telas (SC-1230) e para o custo. É o desenho que a `094` usou (`jornada()` pura, a prévia lendo).

**Alternativa descartada**: uma função por tela que lê e decide junto — cada teste de situação
precisaria de um certame inteiro no banco, e os casos compostos (S3, P3) ficariam sem teste.

## R-002 — A sequência do Perfil pela `jornada()`, com um selecionado qualquer

**Decisão**: `jornada(etapas, marcos, selecionado)` é chamada com as Etapas do conteúdo vigente
(`id`, `name`, `order`, `forma` por `previsao.forma_publicada`) e os marcos do Perfil com `sub` igual
ao índice; o selecionado é o primeiro. Os estados de simulação (`simulado`, `contexto`…) são
ignorados: só se leem `tipo`, as Etapas e o marco de cada ponto. Os pontos `avaliacoes` (grupo)
viram uma coluna por Etapa; `porta`, `fora` e `etapa_alimentada` viram uma coluna; `marco` vira
relação + semente + sorteio (sorteio) ou ordem (pontuação), seguidos de corte (se corta), apuração,
resultado e convocação. Corte, apuração, resultado e convocação ficam **no fim do marco**: são do
mesmo marco, e a Etapa alimentada entra entre o corte e a apuração (D-014).

**D-011 na prática**: o ponto do marco por sorteio com `qualifyingStageId` é retirado da posição que a
`jornada()` lhe deu (o começo) e reinserido logo depois do ponto que contém aquela Etapa.

**Alternativa descartada**: mudar a `jornada()` — a prévia da `094` a usa, os testes dela prendem a
sequência, e a prévia não simula sorteio. A correção é da composição, não da função.

## R-003 — A expectativa por uma função pública da validação

**Decisão**: `editais/domain/validation.quem_exige_o_resultado(snapshot)` passa a ser o nome público de
`_quem_exige_o_resultado` (o privado continua, chamando o público). O andamento soma: as Etapas de
`desempate.etapas_do_desempate(marco)` (D-012); a progressão, por ponto fixo — a Etapa consolidável
(`impedimento_da_regra is None`) de `order` menor que a de uma Etapa esperada passa a esperada; e
tira a enumerada só por marco de sorteio que não consolida.

**Alternativa descartada**: reescrever as três ligações no andamento — a lição da `103` e da `104`:
duas regras para a mesma pergunta divergem na primeira mudança.

## R-004 — A Etapa: o panorama da distribuição, e o Perfil numa consulta

**Decisão**: para cada Etapa esperada, `panorama_da_etapa(edital, etapa, conteudo=)` e
`resumo_da_etapa(panorama=)`, exatamente como a view `distribuicao` chama; `recusa_por_inscricoes_em_
curso(conteudo, agora)` como ela. Por Perfil: `Inscricao.objects.filter(edital, SUBMETIDA)
.values_list("id", "profile_id")` uma vez, e a partição do `panorama["estados"]` contada por Perfil
em memória. A Etapa sem efeito não paga panorama.

**Custo**: o panorama é de custo constante por Etapa (013); o total cresce com o número de Etapas
esperadas, e não com inscrições.

**Alternativa descartada**: anotar `profile_id` dentro de `participacao_detalhada` — mexeria na 013
para um consumidor novo; a consulta à parte custa uma por Edital.

## R-005 — O que vem depois da ordem: o indicador da condução, refinado

**Decisão**: `conducao_do_marco.indicador_do_marco(..., pode_classificar=, pode_publicar=)` por marco
dá ordem, corte, apuração e publicação por lista com *Feito*, *Obsoleto*, *Falta* e *Não se aplica*.
O andamento troca *Falta* por *Depois* ou *Pendente* conforme o ponto anterior da mesma lista, e usa
as URLs dele. No marco por sorteio, a coluna da ordem do indicador não é mostrada: a relação, a
semente e o sorteio a substituem, e a obsolescência do sorteio vem do indicador.

**Por quê**: é a função que a tela de condução já usa; quando a `126` mudar uma célula dela (*Não se
aplica* na lista sem inscrito), a mudança chega aqui sem regra paralela.

## R-006 — O definitivo: a mesma aferição da tela de publicação

**Decisão**: com a célula da publicação *Feito* e nota "preliminar", `publicabilidade.aferir(edital,
marco_id, ato, natureza="DEFINITIVA", lista_id)`. Sem impedimento → *Pendente* de quem publica, com o
link à prévia; com `JANELA_ABERTA`, `RECURSO_PENDENTE`, `REAVALIACAO_PENDENTE`,
`PROVIDENCIA_PENDENTE` → *Aguarda*, com a mensagem da aferição; outros impedimentos → *Impedido*.

**Custo**: `aferir` chama `estado_do_marco`; só para listas com preliminar vigente.

## R-007 — A convocação: as três prévias da tela

**Decisão**: para lista com apuração vigente e não obsoleta, `leitura_do_recorte` uma vez e
`previa_dos_titulares`, `previa_dos_vencidos` e `previa_das_pendentes` com `leitura=`. Titulares →
"Convocar N titulares"; pendentes → "Emitir N comunicações" (ou "Registrar a publicação de N", na
forma por publicação); vencidos → "Registrar o não atendimento de N"; `porEstado[EM_CURSO]` →
*Aguarda* até o menor vencimento em curso; `impedimento` da prévia dos titulares com a forma não
declarada → *Impedido*. Sem titular, com `ocupacao["faltando"] > 0` e fila → *Pendente* condicional
"chamar a próxima da fila"; com a fila esgotada (`esgotou`), marco que corta e linha no quadro →
"pedir a faixa seguinte". Documentos: `_documentos_por_linha` não é chamado (é da view); a
conferência pendente vem de uma agregação das apresentações sem conferência das convocações vigentes
do recorte (R-008).

## R-008 — Conferência de documentos

**Decisão**: `convocacao.application.documentos` já tem a leitura por chamada usada no desfecho
(`leitura_da_chamada(...).pendencias_para_incluir`). Para não pagar uma leitura por chamada, o
andamento conta, por recorte, as apresentações vigentes sem conferência numa consulta agregada pelas
convocações vigentes que a leitura já trouxe — a mesma pergunta "apresentado e não conferido" que a
tela dos documentos responde por linha. A providência leva à convocação do recorte (a tela dos
documentos é por convocação).

## R-009 — Quem é "você"

**Decisão**: um objeto `Alcance` por requisição: `conduz = pode_gerir_comissao(ator, processo) is not
None`; `consulta = conduz or ator.can("auditoria:consultar")`; `publica = ator.can("resultado:
publicar")`; `julga = ator.can(recursos_admitir.PERMISSAO)`; `retifica = acoes.pode_retificar`;
`confere` = alocação à conferência do Perfil (a mesma função que `_exigir_alcance_da_conferencia`
usa). A segregação de funções não se aplica aos atos depois da publicação (só a publicação do Edital
e da Retificação a têm), e por isso não entra além do que a `104` já faz na Retificação.

## R-010 — Os objetos da `104` dentro do Edital

**Decisão**: `trabalho.do_ator(ator, [edital])` dá recurso, Retificação e avaliação deste Edital.
Recurso e Retificação viram providências *Pendente* "suas"; a avaliação vira a providência "avaliar"
da Etapa correspondente (FR-4063). Para quem não tem, o andamento diz "quem julga recursos: N" pela
mesma contagem (`acoes.recursos_aguardando_decisao`), e as Retificações em curso continuam no cartão
como a `104` as pôs (a FR-2819 e a FR-2820 da `104`).

## R-011 — O custo do detalhe

**Decisão**: teste de orçamento em `tests/performance/test_andamento_em_escala.py`: o mesmo cenário
com 3 e com 30 inscrições, número de consultas igual; e um teto absoluto, fixado na primeira medição
com folga de 20%, para um Edital por sorteio com três listas e um por pontuação com duas Etapas. O
`effective_version` é lido uma vez e entregue; as funções que o releem por dentro são as das telas e
não são alteradas.

## R-012 — As transições pela mesma derivação

**Decisão**: `andamento.da_lista(edital, ator, marco_id, lista_id)` devolve a primeira providência em
aberto da lista e as das outras listas do marco, e cada view de ato a chama só no GET que mostra a
mensagem de sucesso (a sessão já carrega o desfecho). Um parcial `_proximo_nesta_lista.html` é
incluído logo abaixo da mensagem. Feito por último (D-015).

## R-013 — Estilo

**Decisão**: folha própria `interface/telas/andamento.css`, carregada no detalhe pelo bloco
`estilo_da_pagina`, e a moldura de rolagem da `058` (`rolavel`), sem `style=` nem `<script>` (CSP).
