# Research: O desfecho da convocação comunicado ao candidato (156)

Decisões de implementação, sobre a spec revista no PR #488, lida contra a `main` em `17e9665c`. Cada
uma diz o que foi escolhido, por quê e o que ficou de lado. Nenhuma toca norma: onde a leitura do
código mostrou atrito com um requisito, a decisão diz como o requisito se cumpre.

## R-001 — As frases moram num módulo puro do portal

**Decisão**: `portal/desfecho.py`, no molde de `portal/situacao.py` e `portal/obrigacoes.py`: funções
puras, sem banco nem relógio, que recebem o que a view já leu. Ele guarda a frase simples de cada
desfecho (FR-6406, FR-6407), a da convocação sem desfecho (FR-6442), o próximo passo (FR-6410 a
FR-6413) e o caminho para recorrer (FR-6414). `situacao.py`, `obrigacoes.py` e as views o chamam; a
constante `obrigacoes.ACEITE` passa a ser a frase do aceite da FR-6406, sem a segunda oração.

**Por quê**: as três telas (convocação, acompanhamento, chamada) precisam dizer a mesma coisa, e as
varreduras de vocabulário leem as frases nos arquivos-fonte. Um módulo só entra nas listas literais
das varreduras (`test_vocabulario_da_convocacao.py`, `test_vocabulario_dos_documentos_da_convocacao.py`,
`test_vocabulario_do_requerimento.py`) uma vez.

**Alternativa descartada**: espalhar as frases nos templates. As varreduras de template não leem
`{% if %}` por espécie, e a mesma frase seria escrita três vezes.

**Cuidados**: nenhuma frase do portal usa *"homologa"* (a varredura do Requerimento o proíbe em
`situacao.py` e `obrigacoes.py`), *"dentro das vagas"* (UX-158 da `063`), *"concluíd"* nem
*"atendid[oa] pelo"*. *"Convocação não atendida"* e *"sem que ela fosse atendida"* ficam em
`desfecho.py`, fora da projeção que a lista de `test_obrigacoes_da_convocacao.py` varre.

## R-002 — As duas camadas são `<details>` nativo

**Decisão**: o fundamento recolhido é `<details class="fundamento-do-ato"><summary>Fundamento do
registro</summary>…</details>` (ou *"Fundamento da convocação"*), com a regra na folha do portal. No
acompanhamento, a linha *"Registrado em ‹data›: ‹fundamento›"* do porquê (`situacao.py:253`) vira a
frase simples, e o fundamento vai para um campo novo da `Linha`, que o template recolhe.

**Por quê**: abre sem script (CSP da `091`), anuncia o estado aos leitores de tela (UX-621) e o
portal já usa `<details>` em quatro lugares, com regra na folha.

**Custo**: a frase da inércia precisa do atestado, que `vigentes_por_inscricao` não traz. O
`prefetch` ganha `desfechos__atestado`, para que `situacao_da_inscricao` continue sem consulta
(`TestCusto` da `063`).

## R-003 — A seção aplicável sai do plano do documento publicado, e o caminho é a página do Edital

**Decisão**: a view lê o snapshot da versão vigente (`selecao_publica`, que a view da convocação já
tem) e pergunta ao plano do documento (`publicacoes/infrastructure/apresentacao.plano`) se a seção de
chave `matricula` — ou a apresentada *"Como será a matrícula?"*, com as partes que o catálogo da
`069` lhe junta — sai no documento, e com que título. O mesmo para `recursos`. A função pura recebe
`(titulo_ou_vazio)` e compõe a frase. O caminho é a página pública do Edital, no bloco *"Edital e
documentos"* (`portal:selecao` com a âncora `#documentos-titulo`), onde está o PDF.

**Por quê**: a página pública não renderiza o texto das seções, e o PDF não tem destino nomeado. A
suposição da spec previa o caso (*"o plano decide entre criar a âncora e levar ao topo da página"*):
levar ao bloco do documento é o caminho que existe, e o título publicado diz onde ler. Usar o plano, e
não `content["sections"]` direto, faz *"não vazia"* significar o mesmo que o PDF mostra: na
apresentação por perguntas, a seção sai também com a declaração do Requerimento.

**Alternativa descartada**: âncoras no PDF. Mexe no compositor do ato oficial, e o PDF já publicado não
se regenera.

## R-004 — O contato: o canal, ou nada

**Decisão**: `identificacao.da_unidade(escopo).canal()` (unidade, depois instalação), **sem padrão de
texto**. Vazio, nas telas da convocação e do resultado, a linha *"Atendimento"* e a frase *"fale com o
atendimento"* não saem: `frase_do_atendimento("")` devolve vazio, `situacao.py:651` passa o canal, e
um parcial novo (`_atendimento_da_convocacao.html`) substitui `_atendimento.html` só nessas telas —
as outras continuam com a frase genérica (FR-6416). Nas mensagens da convocação e da correção,
`comunicar._dados_da_mensagem` deixa de usar *"a comissão do certame"*, e os modelos põem a linha só
com canal.

**Custo**: o acompanhamento passa a ler a unidade também com desfecho de aceite ou regularização (o
próximo passo termina no contato). É uma consulta, constante por página; os orçamentos de consulta
(`test_portal_jornada_consolidada.py`) comparam 1 contra 6 itens, e continuam constantes.

## R-005 — O rótulo "Espécie" sai do portal

**Decisão**: nas três telas que o mostram (`convocacao.html:60`, `_convocacao_da_inscricao.html:21`,
`_obrigacoes_da_convocacao.html:89`), *"Espécie: Para vaga inicial"* vira *"Chamada: 1ª chamada, para
vaga inicial"*, a forma que a `121` registrou sem desenvolver (`T5`).

**Por quê**: a FR-6403 proíbe *"espécie"* fora do fundamento, e nenhum requisito anterior exige o
rótulo.

## R-006 — A mensagem da convocação perde a cláusula

**Decisão**: os quatro modelos (`inicial.txt|html`, `correcao.txt|html`) dizem *"Prazo para atender:
até ‹por extenso›."* e *"Prazo válido para atender: até ‹por extenso›."*. Os testes que asseriam a
cláusula (`tests/unit/convocacao/test_mensagem.py`, `tests/integration/convocacao/test_mensagem_da_convocacao.py`)
passam a asserir a ausência. O resumo do modelo gravado na comunicação (FR-3889 da `121`) muda por si
para as mensagens novas; as gravadas não se tocam.

## R-007 — O pedido de desistência: duas tabelas que não se alteram, e estado derivado

**Decisão**: na app `convocacao`, `PedidoDeDesistencia` e `CancelamentoDoPedidoDeDesistencia`, append-only
nas três camadas (modelo, gatilho, privilégio), numa migration `convocacao/0008`. O `M` do
provisionamento vai de 58 a 60. O estado do pedido — *pendente*, *cancelado*, *homologado*,
*encerrado por outro desfecho* — é derivado: cancelado se há cancelamento; senão, homologado ou
encerrado conforme a espécie do desfecho vigente da chamada; senão, pendente.

**Por quê**: nada se exclui, e um estado gravado exigiria `UPDATE` numa tabela que não o admite. O
desfecho já é o fato que encerra o pedido (FR-6425), e derivar dele evita uma terceira tabela que
poderia discordar do desfecho.

**A "credencial que fez o pedido"** (FR-6420) é o `subject` da identidade autenticada, como em
`ApresentacaoDeDocumento.apresentado_por`: a sessão do portal guarda só a identidade, e a credencial
(`CandidateEmail`) se remove, o que a tornaria imprópria para chave estrangeira de tabela que não se
exclui. O registro não copia endereço.

**O pedido é da chamada** (D-009): ele guarda a convocação raiz da chamada, e lê a vigente pela cadeia.

**Protocolo**: `DES-` seguido de oito caracteres hexadecimais do identificador, com `UNIQUE`. Oito, e
não quatro, porque protocolo curto colide com trechos de UUID nos testes de substring.

## R-008 — A trava e a idempotência do pedido

**Decisão**: o comando trava o Processo com `FOR SHARE` (o padrão do envio do Requerimento) e a
Inscrição com `FOR UPDATE` (o padrão do envio de documentos): é assim que a *"trava da convocação"* da
FR-6420 se faz, porque a convocação mora em tabela que não se altera e não pode ser travada. A
idempotência tem duas camadas: a chave de idempotência do formulário, reservada com o ator do
candidato (`shared.idempotency.reservar`), como pede a FR-6420; e o estado — com pedido pendente da
mesma chamada, o comando devolve o existente —, que cobre o envio repetido de outra aba, com outra
chave. O cancelamento segue o mesmo par.

**Por quê**: tabela que não se altera não pode ser travada (`tests/guardiao_de_travas.py`). O desfecho
trava o Processo com `FOR UPDATE`, e o `FOR SHARE` do pedido se serializa com ele: não há pedido
gravado depois de um desfecho que ele não viu.

## R-009 — A homologação passa pelo comando de desfecho

**Decisão**: o atalho *"Registrar a desistência pedida"* é um formulário próprio no cartão, que posta
para `desfechar_view` com a espécie fixa e o fundamento derivado do pedido, e passa pela conferência do
texto da `125` (o fundamento é texto que o candidato lê). O comando `desfechar` ganha
`ciencia_do_pedido`: com pedido pendente e espécie diferente da desistência expressa, sem a ciência,
recusa com `pedido_de_desistencia_pendente` (409). A marca viaja pela conferência do texto como campo
oculto, como a das inaplicabilidades.

**Por quê**: um caminho só registra desfecho (`registrar`), e a ciência é conferida no comando, e não
só na tela (FR-6425).

**Lote**: `alcance.vencidas` recebe as chamadas com pedido pendente e as conta em
`fora["pedidoDeDesistencia"]` (FR-6426); a tela dos vencidos ganha a linha.

## R-010 — Onde o pedido aparece na condução

**Decisão**:
- `conducao_da_convocacao.passo_da_chamada` ganha o código `PEDIDO_DE_DESISTENCIA`, logo depois de
  `DESFECHADA` na precedência (FR-6443), com a ação `desfecho`.
- `interface/andamento.situacoes_da_convocacao` ganha a célula *Pendente* *"Registrar a desistência
  pedida pelo portal"*, com a contagem e a âncora do primeiro cartão (FR-6427), no molde da dos
  vencidos.
- `processos/application/pendencias_do_edital` ganha o tipo `PEDIDO_DE_DESISTENCIA_PENDENTE`, que entra
  em `encerramento.DA_099`, em `TIPOS_NO_PROCESSO` e na frase do relatório (FR-6444). Os guardiões
  da advertência do Processo cobram o tipo novo num dos dois conjuntos.

## R-011 — O aviso do desfecho é uma origem nova da `066`

**Decisão**:
- `avisos.domain.nomes.DESFECHO` em `ORIGENS`, e a migration `avisos/0003`: as duas *constraints* da
  origem (ato da origem como o da pendência: natureza e referência vazias) e a coluna anulável
  `DestinatarioDoAviso.desfecho`, que liga o destinatário ao desfecho que o motivou.
- O texto em `avisos/domain/desfecho.py` (assunto, corpo, rodapé, a instrução de acesso por código, o
  contato quando houver), puro e escapado, sem variável e sem nome.
- A gravação em `avisos/application/desfechos.py`, chamada **dentro** da transação do desfecho
  (`desfechar` e o lote), quando a opção vem marcada. Um aviso e um destinatário por pessoa; sem
  endereço, nada é gravado, e a resposta o diz.
- O despacho relê antes de cada tentativa: se a convocação foi sucedida ou o desfecho vigente da
  chamada não é o do destinatário, interrompe com o motivo, como faz com a pendência (FR-6432). A
  trilha de cada envio, que hoje é só da pendência, passa a cobrir as duas origens.
- O cartão mostra o estado pelo registro: `avisos_por_raiz` deixa de fixar a origem, e `anotar` mostra
  o aviso do desfecho também em convocação desfechada (FR-6445).

**Por quê a coluna**: o aviso não tem chave para o desfecho, e a releitura precisa saber qual desfecho
foi avisado para dizer se ele ainda é o vigente. A coluna é anulável porque as outras origens não a
usam; tabela que não se altera admite coluna nova.

**A autorização** é a do desfecho (`pode_gerir_comissao`), como na chamada e na pendência
(`comando.base_do_aviso`): quem pode registrar o resultado pode pedir que se avise dele.

## R-012 — As duas chaves

**Decisão**: `AVISOS_DE_DESFECHO = os.getenv("AVISOS_DE_DESFECHO", "false") == "true"` na base; ligada
em `development` e `test`, como a geral. `avisos.application.comando.envio_do_desfecho_habilitado()`
é `AVISOS_AOS_CANDIDATOS and AVISOS_DE_DESFECHO`. Desligada:
- a confirmação do desfecho não mostra a opção;
- o POST com a opção marcada é recusado com `aviso_envio_desabilitado` **antes** de registrar o
  desfecho (FR-6438);
- o despacho deixa de selecionar destinatários da origem `DESFECHO` — sem interromper: religada a
  chave dentro da janela, o aviso sai; fora dela, expira (D-011).

**Produção** herda o padrão desligado, como herda o da chave geral: ligar é ato de configuração,
condicionado às pendências PI-1 a PI-6 (FR-6440). Não há recusa de subir ligada, porque a `066` não
a tem para a chave geral, e uma recusa impediria a ativação quando a validação existir.

## R-013 — A sexta situação na guarda da FR-084

**Decisão**: `REVISAO_DA_FR_084_PELA_156 = "2026-11-11"` no despacho, ao lado das outras duas; o
par `("avisos/application/despacho.py", "o aviso do desfecho da convocação (156)")` em `SITUACOES`;
a contagem passa a seis, três no despacho; e um teste novo, no molde do da `134`, exige no trecho da
FR-084 *"pela `156` em 2026-11-11"*, *"**seis**"*, *"aviso do desfecho"* e a redação anterior da
`134`. Nenhum módulo novo monta mensagem: o despacho é o único remetente.

## R-014 — O canal fictício dos cenários de treinamento

**Decisão**: o carregador dos cenários (`treinamento/`) registra um canal fictício
(`selecao@treinamento.exemplo.test`) na unidade que usa, quando ela não tem canal, pelo comando de
edição do registro de unidades, com motivo e trilha, e só com `CENARIOS_DE_TREINAMENTO` ligada
(FR-6417). Restaurar o cenário não o desfaz: o registro não se exclui.

## R-015 — O que se cruza com outros incrementos

| Incremento | Estado em 12/11 | Arquivos em comum | Como fica |
|---|---|---|---|
| `152` (prevenção) | plano mergeado (#480); MVP só em `claude/152-prevencao-mvp` | `desfechar.py`, `conducao_da_convocacao.py`, `interface/convocacao.html`, `interface/views.py`, `convocacao/application/documentos.py` | esta parte da `main`; a ciência do pedido e a da `152` são marcas distintas; antes da validação final, integrar o que já estiver mergeado |
| `154` (depois do envio) | plano no #484 | `portal/obrigacoes.py`, `portal/situacao.py`, `_chamada_da_convocacao.html`, `_obrigacoes_da_convocacao.html` | a `154` mexe nas chamadas abertas; esta, no estado decidido e no fundamento. Conflitos de texto, não de regra |
| `150` (vários documentos) | plano no #483 | `_cartao_do_documento_da_convocacao.html`, `portal/static/portal/envio.js`, `portal/views.py` | esta não toca o cartão do documento; só `portal/views.py` em comum |
| `153` (formalização) | mergeada (#486) | `interface/andamento.py`, `interface/encerramento.py`, `relatorio_do_edital.py` | parte dela: o molde das providências e da advertência |

## R-016 — Como se prova

- **Unitários puros**: as frases de `portal/desfecho.py` por espécie, a seção aplicável presente e
  ausente, o contato vazio, o texto do aviso (assunto não começa por "Convocação", sem espécie, rodapé
  fixo, escape), o estado derivado do pedido, `alcance.vencidas` com pedido pendente.
- **Integração contra PostgreSQL**: pedir, cancelar e homologar (com trava e idempotência), a recusa
  sem ciência, o lote, o aviso gravado na transação do desfecho e recusado com a chave desligada, o
  despacho que envia, que interrompe e que pula a origem com a chave própria desligada, as tabelas
  append-only (gatilho e privilégio) e o orçamento de consultas das telas.
- **Interface**: as três telas do portal em cada espécie, a confirmação e o cancelamento do pedido, o
  cartão com o pedido e o atalho, a confirmação de encerrar.
- **Varredura nova** (`tests/test_vocabulario_do_desfecho.py`): renderiza o portal em cada espécie de
  desfecho e de convocação, tira o conteúdo dos `<details>` e procura os termos da FR-6403 (SC-2120).
- **Navegador**: o portal do convocado com aceite, desistência e não atendimento, a 390 px e em tela
  larga ([quickstart](quickstart.md)).
