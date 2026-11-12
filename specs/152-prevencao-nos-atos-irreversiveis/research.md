# Research: Prevenção de erro nos atos irreversíveis da convocação

Decisões técnicas do plano. As decisões de produto estão na spec, de D-001 a D-011, e não se repetem
aqui. Cada item abaixo diz o que se escolheu, por quê, e o que se descartou.

O mapa do código foi lido na `main` em `be830e65`. Ele está resumido no fim deste documento, para
que quem implementa não precise refazê-lo.

## R-001 — A ciência do prazo mora na trilha, e não numa coluna

**Decisão**: a ciência do indeferimento fica registrada no evento de trilha do desfecho
(`CONVOCACAO_DESFECHAR`). Vai em dois lugares:

- no `reason`, por extenso;
- no `detalhe`, estruturada: o vencimento mostrado, ou a falta dele, e os itens pendentes no
  instante do ato.

O modelo `DesfechoDaConvocacao` não ganha campo.

**Por quê**: é o precedente da ciência das inaplicabilidades da `131`. O comando a confere e a
escreve no `reason` por `_ciencia_na_trilha`, sem coluna. A trilha é append-only e é onde a
auditoria lê. Uma coluna exigiria migration numa tabela append-only, e ainda nova constraint e nova
passagem no provisionamento — custo sem leitor, porque nenhuma tela filtra desfechos pela ciência.
O `auditar` já aceita `detalhe=`, e a ciência é o primeiro uso dele no desfecho.

**Descartado**: um booleano no desfecho, pelo custo acima; e gravar a ciência só no `reason`, que não
dá à auditoria o vencimento como dado.

## R-002 — "Prazo em curso" é a negação de `prazo.decorrido`

**Decisão**: a ciência é exigida quando a espécie é indeferimento, há obrigatório não atendido
(`pendencias_para_incluir`) e o prazo **não** decorreu pela regra de `prazo.decorrido`. Essa regra
pede envio, vencimento e `agora > vencimento`. Ficam cobertos três casos:

- a convocação com vencimento ainda por vir (FR-5803);
- a convocação sem vencimento informado (FR-5804);
- a convocação ainda não comunicada. O relógio dela nem começou, e a pessoa ainda nem soube.

**Por quê**: é a mesma leitura que libera o não atendimento (`_recusar_nao_atendimento_prematuro`).
O indeferimento passa a pedir ciência exatamente onde o não atendimento ainda é recusado. Uma
segunda definição de "em curso" divergiria da primeira.

**Interpretação registrada**: a spec diz "documento pedido ainda não conforme". O plano lê isso como
obrigatório não atendido, o mesmo critério que impede o aceite. O facultativo não decide desfecho
nenhum (FR-3592 da `115`), e pedir ciência por ele seria aviso sem consequência.

## R-003 — "Apresentado nesta chamada" é apresentação com arquivo

**Decisão**: `ItemLido.apresentado_pela_pessoa` é verdadeiro quando alguma apresentação do item
**na chamada** tem arquivo. Conta qualquer versão, e não só a vigente. O aproveitamento grava
apresentação sem arquivo, com `documento_da_inscricao` ou `apresentacao_de_origem`, e por isso não
conta (D-011).

**Por quê**: o envio pelo portal é o único caminho que grava arquivo na chamada. O aproveitamento é
feito pelo sistema na criação da convocação, com `apresentado_por=convocacao:<raiz>`; ele não é
resposta da pessoa. Olhar só a vigente erraria em sentido conhecido: a vigente de um item reenviado
tem arquivo, mas a de um item que a comissão marcou pendente sem apresentação não tem nenhuma.

**Custo**: as apresentações da chamada já vêm em `leituras_por_chamada` (por `prefetch`). Saber se
alguma tem arquivo não acrescenta consulta.

## R-004 — Uma verificação para a chamada, extraída de `convocar`

**Decisão**: `verificar_chamada` reúne as recusas que `convocar` faz pela leitura do recorte, na
ordem de hoje, e devolve o que a conferência precisa mostrar: espécie, posição, anteriores e
vencimento. `convocar` a chama sob a trava. `conferencia_da_chamada` a chama fora da trava, depois de
`ensure_processo_accepts_changes`, pelo mesmo desenho de `verificar_titulares` (a decisão de
verificação única da `140`).

**O que fica fora dela**:

- as recusas da correção, que pertencem à prévia assinada da `120`;
- as que só o comando pode fazer — a base de comissão sob a trava, a reserva da chave.

**Descartado**: compor a conferência com as peças soltas (`especie.derivada`, `contexto_do_recorte`,
`fila.precedencia`) sem extrair a verificação. A conferência mostraria botão para o que o comando
recusaria, e a lista de recusas teria duas cópias.

## R-005 — Os desfechos cabíveis são predicados puros, e as guardas os chamam

**Decisão**: `convocacao/domain/desfechos_cabiveis.py` tem um predicado por guarda. Cada um recebe
primitivos (espécie da chamada, envio, vencimento, agora, atestados, ocupação, pendências) e devolve
`None` ou `(codigo, frase, a_partir_de)`. São estes:

- compatibilidade com a espécie da chamada;
- não atendimento prematuro;
- inércia sem ocupação;
- inércia sem atestado;
- inclusão com documento por conferir.

As guardas de `desfechar` continuam onde estão, e passam a levantar `DomainError` a partir do que o
predicado devolve.

**Por quê**: a FR-5838 pede uma verificação só. Os predicados puros cabem na tela, que monta dezenas
de linhas a partir do que já carregou, e cabem no comando, que lê o mesmo sob a trava. As frases da
nota (FR-5836) são, por construção, as da recusa.

**Fora do predicado**: a lista incompleta (`LISTA_DA_CONVOCACAO_INCOMPLETA`) e as assinaturas da
`131` são falha de registro ou mudança concorrente, e não "ainda não cabe". Continuam só no comando.

## R-006 — O seletor não consulta por linha

**Decisão**: a ocupação do recorte vem de um `contexto_do_recorte` por recorte, que a tela já monta.
Os atestados, o envio, o vencimento e as pendências já estão na linha (`leitura_do_recorte`,
`_documentos_por_linha`). A tela passa conjuntos e valores aos predicados, sem consulta nova.

**Por quê**: o orçamento de consultas da tela reprova leitura por listagem, e uma consulta por linha
num recorte de 40 chamadas seria 40 consultas.

## R-007 — A faixa seguinte ganha assinatura opcional; a da ocupação não muda

**Decisão**: `continuar_corte` aceita `confirmacao_do_calculo=None`. Quando vem, o comando a confere
por `assinatura_da_proposta(proposta, geracao=vigente)`, como na emissão; diferente, recusa com
`calculo_divergente`. A tela do corte sempre a manda. `causar_faixa_seguinte`, da `016`, não a manda,
e continua como está.

**Por quê**: o gesto da tela é o que recebe quantidade digitada, e é o que a spec cobre (FR-5829).
A faixa causada pela ocupação tem quantidade derivada do déficit e outra tela; torná-la
obrigatória quebraria a `016` sem pedido.

**Achado, para registro**: o gesto "pedir a faixa seguinte" da ocupação também emite num clique. Não
entra nesta spec.

## R-008 — Uma página de conferência para o lote e para a chamada

**Decisão**: `convocacao_conferir.html` ganha o modo de uma pessoa. Muda o título do grupo ("Será
convocada"), entra "Passa à frente de" no lugar de "Ficam de fora", entra o Resultado que a
regularização regulariza, e o form posta em `interface:convocar`. O resto é o mesmo:

- o fundamento, a mensagem e o prazo;
- o complemento editável;
- "Conferir de novo" e "Cancelar e voltar".

**Por quê**: a D-004 da spec pede "a mesma conferência". Duas páginas divergiriam no primeiro
polimento, como divergiram a ordem e o lote até o #467.

**Descartado**: uma página nova `convocacao_conferir_chamada.html`, pela razão acima.

## R-009 — A recusa do desfecho devolve o formulário preenchido

**Decisão**: na recusa, `desfechar_view` grava na sessão `recusa_do_desfecho`, com:

- a convocação;
- a espécie;
- o fundamento;
- o atestado;
- a ciência.

A tela consome a chave ao renderizar, como o portador `recusa_da_correcao` da `120`, e reabre o
`<details>` daquela linha com os campos preenchidos e a frase da recusa (FR-5805).

**Por quê**: hoje a recusa do desfecho só deixa a frase em `erro_da_convocacao`, e o fundamento
digitado se perde. Com a ciência nova, a recusa mais provável é a da marca esquecida, e perder o
texto nela seria punir quem esqueceu a marca.

## R-010 — A frase da conferência do texto vem do composto

**Decisão**: `_texto_do_desfecho` passa a devolver também a frase do prazo, quando a ciência é
exigida. `_conferir_o_texto.html` a mostra acima do botão. A marca viaja nos `campos` da sessão, como
os campos da `131` já viajam (FR-5807).

**Por quê**: o fundamento é obrigatório, e por isso todo desfecho passa pela conferência do texto. Sem
a frase ali, a pessoa marcaria a ciência num formulário e confirmaria noutro, sem a ver de novo.

## Mapa do código (11/11/2026, `be830e65`)

- **Lote de titulares (`140`)**:
  - `interface/views.py`: `convocar_titulares_view` e `_pagina_da_conferencia_dos_titulares`;
  - `convocacao/application/fluxo.py`: `verificar_titulares`, `conferencia_dos_titulares`,
    `gesto_ja_concluido` (operação fixa `GESTO_TITULARES`), `_prazo_da_conferencia` e
    `resolver_vencimento`;
  - `comunicar.previa_das_mensagens`.
- **Chamada individual**: `convocar_view` usa `conferencia_do_texto.exigir`, que só intercepta com
  complemento e grava na sessão. As recusas estão todas em `convocar.py`, sob `comando_de_comissao`,
  e a precedência é conferida em `convocar.py`, nas duas espécies, por `fila.precedencia`. Não há
  verificação sem efeito.
- **Desfecho** (`desfechar.py`), guardas em ordem: espécie, fundamento, sucedida, já registrado,
  incompatível, não atendimento prematuro, inércia sem ocupação, inclusão sem documentos (com a
  ciência da `131`), atestado, sucessor da regularização. A recusa na tela só guarda a frase.
- **Leitura documental**:
  - estados de item `A_APRESENTAR`, `RECEBIDO`, `PENDENTE`, `COMPLEMENTADO`, `CONFORME` e
    `NAO_SE_APLICA`;
  - `impede_incluir` cobre tudo fora de conforme e não se aplica;
  - a leitura não sabe do prazo (`documentos.prazo_decorrido` é à parte);
  - o aproveitamento grava apresentação sem arquivo.
- **Passo do cartão**: `interface/conducao_da_convocacao.py`, `passo_da_chamada` e `anotar`. O passo
  `VENCIDA` aponta o desfecho.
- **Corte**:
  - `emitir_corte` confere a assinatura (`_conferir`), e a tela já a manda;
  - `continuar_corte` não tem assinatura, e é chamado também por `ocupacao/application/causar_faixa.py`;
  - o desenho de dois passos a copiar é `emitir_ordenacao` (`confirmar=1`, assinatura recomposta,
    `calculo_mudou`).
