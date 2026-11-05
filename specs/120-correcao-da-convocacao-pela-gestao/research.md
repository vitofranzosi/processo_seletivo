# Research: A correção da convocação pela gestão

Fase 0 do plano. Não havia `NEEDS CLARIFICATION` no contexto técnico: as perguntas abaixo são as de
desenho, e cada uma registra a escolha, a razão e o que se descartou. Leitura do código em 04/11/2026,
sobre a `main` em `015861c7`. As decisões de produto estão na spec (D-001 a D-010); aqui ficam as de
implementação, numeradas `R-`.

## R-001 — As conferências moram no comando, sob a trava que ele já toma

**Decisão.** A convocação nomeada (FR-3843) e a assinatura da prévia (FR-3857) são conferidas dentro
de `convocar`, em `comando_de_comissao`, depois do `select_for_update` sobre o Processo.

**Razão.** Duas confirmações do mesmo cartão, em duas abas, só se ordenam pela trava. Conferir na
view, antes do comando, deixaria a janela entre a conferência e a gravação aberta — a perda de
atualização que a Constituição (IV) manda tratar. A trava é a do Processo, a mesma que todo ato da
comissão toma, de modo que nenhum outro ato do recorte grava entre a conferência e a sucessora.

**Descartado.** Conferir na view (janela aberta); `select_for_update` sobre a convocação (o
`FOR UPDATE` em tabela append-only falha com o papel de runtime, e a trava do Processo já serializa).

## R-002 — A repetição vem antes da conferência

**Decisão.** `ctx.repetido` continua o primeiro passo do comando, antes de qualquer conferência da
correção. A chave é a do formulário, nascida no GET, com o sufixo `-corrigir-<convocação>`.

**Razão.** O duplo clique é a mesma intenção duas vezes. Se a conferência viesse antes, o segundo
clique encontraria a nomeada já sucedida — pelo primeiro — e receberia `convocacao_corrigida_sucedida`:
verdadeiro, e errado, porque diria a quem conduz que outra pessoa corrigiu. Com a repetição antes, ele
recebe o resultado do primeiro. O formulário **antigo**, de outra abertura da tela, tem outra chave, e
passa pela conferência (FR-3848, FR-3843).

**A comunicação na repetição.** `convocar_e_comunicar` chama `comunicar_cada` depois de `convocar`,
também na repetição, com a chave `‹chave›:comunicar:‹convocação›`. O `comunicar` é idempotente por
ela, e reserva a chave **antes** de enviar, numa transação curta e própria: a emissão concluída volta
como estava — enviada ou com falha registrada —, sem segunda mensagem; a reserva ainda pendente (o
primeiro envio em curso) é recusada como estado indeterminado, também sem enviar, e a recusa entra na
contagem do resultado; a forma por publicação não emite nada, e volta como aguardando. A SC-1144
conta **mensagens enviadas**, e o teste prende os três resultados.

**O limite conhecido.** `_recusar_vencimento_passado` e o vencimento obrigatório ficam em
`convocar_e_comunicar`, antes do comando, como hoje. A repetição de um envio feito depois de o próprio
vencimento novo passar é recusada em vez de devolver o resultado. Não grava nada, e exige repetir o
envio depois do prazo que se acabou de dar.

**Descartado.** Uma chave por clique, gerada no POST (o duplo clique praticaria dois atos — é a razão,
já registrada na view, de a chave nascer no GET).

## R-003 — A assinatura da prévia segue o molde da assinatura do alcance da `050`

**Decisão.** `alcance.assinatura_da_correcao(convocacao_id, apuracao_id, versao_id, forma, especie)`,
por `canonical_sha256`, num dicionário com o gesto `"correcao"`. O formulário a leva num campo oculto;
o comando a recalcula sob a trava e compara.

**Razão.** O gesto dos vencidos da `050` já resolve o mesmo problema — confirmar o que se viu — com
`alcance.assinatura(gesto, apuracao_id, versao_id, forma, identidades)`. A correção tem uma pessoa só,
e precisa da espécie, que nos vencidos não entra. Uma função própria evita mudar o resumo dos
vencidos acrescentando um campo `None`.

**Por que estes cinco.** O fundamento gravado é função da espécie, dos rótulos do Edital e do recorte
(da versão), da data da apuração e do complemento, que viaja no formulário. A forma entra porque a
prévia diz o que a comunicação fará. A convocação entra para que a assinatura de um cartão não sirva
para outro.

**Descartado.**
- Assinar o **texto** do fundamento: equivalente, e mais frágil — a tela teria de montar o texto com
  o complemento que ainda não foi digitado.
- Mandar os componentes abertos e comparar um a um: diria o que mudou, mas a recusa recarrega a
  prévia nova, que já mostra; o comando registra no detalhe quais diferem, para o diagnóstico.
- Uma tela intermediária de confirmação (D-008).

## R-004 — Uma função pura decide a espécie da sucessora, para a tela e para o comando

**Decisão.** `especie.especie_da_sucessora(contexto, anterior)`: a espécie derivada da posição
(`derivada(inscricao, ocupando, alcancados, regularizaveis)`) e, sem ela, a da convocação corrigida —
a regra que o comando já aplica em linha.

**Razão.** A prévia e o comando precisam chegar à mesma espécie, ou a assinatura nunca casa. Uma regra
escrita duas vezes diverge na primeira mudança.

## R-005 — A view de convocar ganha um ramo, e não uma rota

**Decisão.** `convocar_view` recebe a correção quando o POST traz `corrige`. Nenhuma rota nova.

**Razão.** É o mesmo ato, com o mesmo comando, a mesma autorização (`_edital_para_classificar` com
`somente_gestao=True`) e o mesmo destino. Uma rota nova exigiria uma linha no inventário de negativas
da `033` e duplicaria a porta. O ramo existe só para o portador da recusa (R-007) e para o resultado
(`acao = "correcao"`).

## R-006 — O impedimento do recorte se lê da leitura que a tela já faz

**Decisão.** Apuração ausente e apuração superada saem de `leitura["apuracao"]` e
`leitura["causasDeObsolescencia"]`, que a tela já usa no topo. A ordem vigente, se a leitura não a
trouxer pronta, sai de **uma** chamada a `ato_vigente` por página. As frases são as do topo da tela,
num parcial comum para não haver duas grafias.

**Razão.** A FR-3839 pede as mesmas palavras e nenhum formulário fadado à recusa; a SC-1147 proíbe
consulta por cartão.

**A conferir na T001.** Se a tela com ordem não vigente chega a montar os cartões — talvez a página
inteira já diga outra coisa antes. O plano trata os três impedimentos; o teste confirma qual a tela
alcança.

## R-007 — A recusa da correção tem portador próprio na sessão

**Decisão.** `recusa_da_correcao`, gravada pela view e consumida pela tela seguinte, com a convocação
nomeada, a inscrição, o código, a frase, o campo, os quatro valores digitados e se o cartão mudou.
`erro_da_convocacao` continua para os demais atos.

**Razão.** A recusa de topo de hoje não sabe a que cartão pertence e não leva os campos. A sessão é o
portador que a tela já usa para resultado e erro, entre um redirecionamento e a leitura seguinte.

**Descartado.** Renderizar a tela inteira na resposta do POST (perde o padrão POST-redirect-GET e
duplica a montagem da página); `htmx` (a memória do projeto registra que fragmento com 4xx não troca,
e a tela não usa `htmx` hoje).

## R-008 — O motivo, no cartão que mudou, é texto para copiar

**Decisão.** Com `convocacao_corrigida_sucedida` ou `convocacao_corrigida_com_desfecho`, o motivo
digitado aparece num `<blockquote>` com *"Copie, se ainda quiser usá-lo"*, e o formulário da
sucessora, se houver, nasce vazio.

**Razão.** O motivo foi escrito para a convocação que outra pessoa já corrigiu, ou que já teve
desfecho. Pré-preenchê-lo no formulário da sucessora transformaria o motivo de uma correção no motivo
de outra, com um clique.

## R-009 — O efeito sobre o prazo se diz por um script estático, e sem ele por regra

**Decisão.** `interface/static/interface/correcao-da-convocacao.js`, carregado com `defer`, compara o
vencimento informado (campo ou fim do Evento, por `data-fim`) com `data-vencimento-atual`, no formato
do `datetime-local`, e troca o texto de uma região `aria-live="polite"`. Sem script, a região diz as
três regras. O resultado do ato diz qual se aplicou, calculado no servidor.

**Razão.** É a única parte da prévia que depende do que se digita (D-008, na revisão de `4b2bd844`).
A CSP só aceita script de arquivo; os demais scripts da gestão seguem esse padrão, com teste em
`tests/javascript/`. A comparação de texto vale porque os dois lados estão no mesmo formato e no fuso
da instituição — o mesmo que a tela usa para mostrar o vencimento.

**Descartado.** Uma rodada ao servidor para calcular o efeito (rota nova, latência, e nada que o
cliente não saiba).

## R-010 — A jornada no navegador se monta como a do vencido da `115`

**Decisão.** `tests/navegador/test_jornada_da_correcao_da_convocacao.py`, com a classe `Tela` e o
padrão de `test_jornada_dos_documentos_da_convocacao.py`: preparação por fixtures, ações só no
navegador, verificações na tela, no banco e na trilha. O vencido nasce com vencimento de dois segundos
e uma espera de três, como no teste vencido da `115`.

**Razão.** A Constituição (VI) exige o canal do ator para as ações; as fixtures montam o estado
inicial, que não é a ação demonstrada. O relógio adiantado por `mock`, que os testes de interface usam,
não se compartilha com segurança com o servidor do `live_server`.
