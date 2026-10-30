# Research: Jornada operacional da Retificação

As decisões de produto estão em [spec.md](spec.md), em `D-001` a `D-008`. Aqui ficam as escolhas
técnicas, em `R-NNN`.

## R-001 — Uma derivação dos atos, em `atos_retificacao.py`

**Decision**: `disponiveis(retificacao, ator)` continua sendo "permissão e situação". Por cima dela:
`ofertas(retificacao, ator)` devolve cada ato disponível com o motivo previsível (hoje só a
segregação em `publicar`), e `impedimento` passa a devolver `{"motivo": "segregacao"}`. O próximo
responsável é uma tabela por situação; "é você" é "o ato principal da situação está entre as minhas
ofertas sem motivo". O resumo de uma Retificação em curso, usado pela Lista, pelo Edital e por
Retificar, sai de `resumo(retificacao, ator)`.

**Rationale**: FR-2730 pede uma derivação só. As funções do Edital
(`impede_por_segregacao`, `homologar_fecharia_a_publicacao`) recebem um dicionário com `elaborou` e
`homologou`; a Retificação monta esse dicionário com `prepared_by` e `homologated_by`, sem copiar a
regra. A entrega do ato reaproveita `acoes.entrega_para`, chaveada pela chave do ato, que é a mesma.

**Alternatives considered**: estender `acoes.PROXIMO_RESPONSAVEL` com as situações da Retificação —
misturaria dois agregados numa tabela e trocaria "homologado" por "homologada" num dicionário de
outro dono.

## R-002 — A Lista lê as Retificações em curso numa consulta

**Decision**: depois de montar os Processos, a view junta os identificadores dos Editais exibidos e
faz uma consulta `Retificacao.objects.filter(edital_id__in=ids, status__in=EM_CURSO)` com
`.only(...)` dos campos que a derivação usa. A derivação é Python puro sobre esses objetos.

**Rationale**: FR-2707. A marca precisa da situação, de `prepared_by` e de `homologated_by`, e nada
mais.

**Alternatives considered**: um `Exists` anotado por Edital — diria só "há", e não qual ato cabe a
quem.

## R-003 — O detalhe do Edital e a tela de Retificar compartilham um parcial

**Decision**: `_retificacoes_em_curso.html` desenha a lista (situação, criação, justificativa,
próximo responsável, ato da pessoa, link). O detalhe do Edital o põe numa seção própria, logo depois
das colunas de ações e participantes; a tela de Retificar o põe num aviso antes do formulário, com o
link "Continuar a elaboração" para a que está em elaboração.

**Rationale**: as duas telas mostram a mesma coisa ao mesmo público; um parcial impede que divirjam.

## R-004 — O detalhe da Retificação responde às quatro perguntas

**Decision**: o cartão "O que fazer agora" passa a ter a frase de passagem de bastão (`bastao`, a
classe que o Edital já usa), o motivo da devolução quando há, "Editar a Retificação" como primeira
ação em elaboração, e cada oferta com o mesmo desenho de `_acao_do_edital.html` (habilitada como
link, ou desabilitada com o motivo associado por `aria-describedby`). Um cartão "Quem atuou" mostra
criação, submissão, homologação e publicação, na forma do cartão do Edital.

**Rationale**: o teste da auditoria procura `>Publicar Retificação</a>`; o ato desabilitado é um
`<span>`, como no Edital, e o motivo continua visível (FR-024 da `002`: nem oferecido, nem
escondido).

## R-005 — A edição é uma rota própria sobre o mesmo miolo de Retificar

**Decision**: `retificar` é partida em `_compor_retificacao(request, ator, edital, base, projecao,
modo)`. A porta de criação passa a base vigente e grava por `criar_retificacao_com_gestos`; a porta
nova, `retificacao_editar`, passa a base da Retificação, o conteúdo **proposto** como projeção, e
grava pela fusão e por `edit_retification`. O template é o mesmo, com `edicao` no contexto: título,
texto de "Como funciona", campo oculto da revisão, a lista de remoções a desfazer, o rótulo do botão
("Gravar a Retificação") e a ausência dos botões de gesto (D-008).

**Rationale**: o formulário de Retificar tem dezenas de casos especiais testados; reescrevê-lo para
a edição seria a segunda cópia que a spec proíbe.

**Alternatives considered**: reconstruir o POST de criação a partir do proposto (formulário sobre a
base, com os acréscimos como linhas novas) — exigiria o inverso de seis montadores de entidade nova,
cada um com regras próprias; a fusão sobre caminhos é uma função só.

## R-006 — A fusão: alterações existentes mais a diferença, conferida pelo resultado

**Decision**: `fundir(base, existentes, diferenca, desfeitas)`:

1. tira das existentes as remoções desfeitas, e aplica as que ficam à base: o **proposto**;
2. aplica a diferença ao proposto: o **conferido**;
3. para cada existente, o caminho canônico é o próprio caminho, ou, num acréscimo ao fim de coleção
   (`…/-`) cujo valor tem `id`, o seletor `…/id=<id>`. Remoção fica como está. As demais passam a
   valer o que o conferido tem nesse caminho; somem se o caminho não existe mais no conferido; e uma
   substituição que voltou ao valor da base também some;
4. cada alteração da diferença cujo caminho é o canônico de uma existente, ou fica abaixo dele, já
   está absorvida; as outras entram depois das existentes, na ordem em que vieram;
5. aplica o resultado à base e compara com o conferido. Diferente, recusa (`FusaoInconsistente`) e
   nada é gravado.

**Rationale**: o passo 5 transforma uma heurística sobre caminhos numa garantia: ou o ato gravado
produz o que a pessoa conferiu, ou nada é gravado (FR-2718). As precondições de conteúdo continuam
sendo derivadas da base pelo comando (`_replace_changes`), como na criação.

**Alternatives considered**: concatenar a diferença às existentes — duas substituições no mesmo
caminho teriam precondição tirada da base, e a segunda recusaria na publicação por hash.

## R-007 — A revisão viaja no formulário e é conferida antes de ler o POST

**Decision**: campo oculto `revisao`. Se diferir da revisão atual, a view devolve a tela com a
recusa (412, "Esta Retificação foi alterada depois que você abriu a tela…") sem interpretar o
formulário; se a corrida acontecer entre a leitura e a gravação, `compare_and_swap` recusa com
`stale_revision`, e a mesma frase é mostrada.

**Rationale**: as referências do formulário são posições no conteúdo proposto que a tela mostrou;
lidas contra outro proposto, apontariam para outro campo (D-007).

## R-008 — A edição entra na trilha como `ALTERAR_RASCUNHO`

**Decision**: `edit_retification` grava `record_event(operation="ALTERAR_RASCUNHO",
permission="retificacao:elaborar", previous_revision=expected_revision, previous_state=status)`,
com `correlation_id` opcional. A API passa o dela.

**Rationale**: a operação e o rótulo ("Alteração do rascunho") já existem para o Edital; a trilha
fica legível sem entrada nova.

## R-009 — Recusas da edição

**Decision**: sem `retificacao:elaborar`, `DomainError("forbidden", …, 403)` com a frase que nomeia a
permissão; fora de `EM_ELABORACAO`, `DomainError("invalid_state", …, 409)` com a situação e a saída;
fora do escopo, o `Http404` de `_retificacao_do_ator`, já inventariado na `033`. O middleware de
recusa compõe a página.

## R-010 — Testes de jornada por sessões independentes

**Decision**: `tests/interface/test_jornada_da_retificacao.py` reaproveita os auxiliares do teste da
auditoria (`sessao`, `navegar`, `alcancada`) e acrescenta `editar(cliente, retificacao, **campos)`,
que lê os campos do contexto da tela de edição e devolve todos, com as trocas pedidas por caminho
normativo. As jornadas A a H são casos separados. A concorrência verdadeira (duas transações) é
coberta por um caso com `threading` e duas conexões, como `test_a_segunda_homologacao…` faz em série.
