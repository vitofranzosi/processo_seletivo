# Contrato: recusas, impedimentos e frases

As frases são o contrato: os testes as conferem por trecho, e a tela as mostra como estão. `«…»` é
substituído pelo dia por extenso, pelas horas, pelo nome da banca, pelo número ou pela pessoa. Toda
frase diz o que fazer, e não só o que está errado (UX-766). As frases vêm do protótipo aprovado
(`doc/estudo-agendamento-da-etapa-2026-11-14/prototipo/static/agenda.js`), salvo onde a spec as fixa
literalmente — e então vale a da spec.

Os códigos são os de `RecusaDaAgenda.codigo` (`agendamento/domain/recusas.py`, [research.md](../research.md)
T-008). Uma recusa de comando devolve 422 na tela inteira e, num fragmento htmx, 200 com
`HX-Retarget` para a área de mensagem, como as telas da composição (o htmx não troca resposta 4xx).

## 1. Configuração (FR-7204, SC-2391)

Recusas de gravação. A configuração inteira é recusada, nada se grava, e cada problema vem numa linha.
São oito casos, os oito da FR-7204, mais os dois de lista vazia que o formulário pode produzir.

| Código | Quando | Frase |
|---|---|---|
| `duracao_nao_positiva` | duração ≤ 0 ou vazia | Informe a duração de cada atendimento, em minutos. |
| `intervalo_negativo` | intervalo < 0 | O intervalo entre atendimentos não pode ser negativo. Use 0 para nenhum intervalo. |
| `sem_dia` | nenhum dia | Acrescente ao menos um dia de atendimento. |
| `sem_banca` | nenhuma banca | Acrescente ao menos uma banca. |
| `dia_fora_do_periodo` | dia fora do `start_at`–`end_at` do Evento vigente, na zona institucional | «Segunda-feira, 30/11/2026» está fora do período da Etapa no cronograma publicado («de 23 a 25/11/2026»). Escolha um dia dentro dele; mudar o período pede Retificação. |
| `janela_invertida` | fim ≤ início | Em «Seg., 23/11», a janela «13:00–12:00» termina antes de começar. |
| `janela_menor_que_a_duracao` | fim − início < duração | A janela «12:00–12:05» não comporta um atendimento de «10» minutos. Amplie a janela ou reduza a duração. *(literal do cenário 4 da US1; o prefixo «Em Seg., 23/11,» antecede a frase quando há mais de um dia)* |
| `janelas_sobrepostas` | duas janelas do mesmo dia se cruzam | Em «Seg., 23/11», as janelas «08:00–12:00» e «11:30–14:00» se sobrepõem. Ajuste uma delas. |
| `banca_sem_nome` | nome vazio | Dê um nome a cada banca, como "Banca 1". |
| `bancas_com_o_mesmo_nome` | nomes iguais depois de aparar espaços e sem distinção de caixa | Duas bancas se chamam "«Sala 1»". Os nomes aparecem para o candidato e precisam ser distintos. |
| `dia_repetido` | o mesmo dia duas vezes | «Seg., 23/11» aparece duas vezes. Junte as janelas num dia só. |

A Etapa **sem Evento** no cronograma não tem `dia_fora_do_periodo`: a configuração é aceita, e a
conferência mostra o aviso da seção 4 (Edge Cases).

### Depois da publicação (FR-7208)

| Código | Quando | Frase |
|---|---|---|
| `horario_publicado_removido` | a configuração nova não deriva um horário que está em `HorarioPublicado` vigente | A agenda já foi publicada, e «Fulana (INS-…)» tem horário em «Seg., 23/11, 09:30, Banca 1», que esta configuração removeria. Depois da publicação, só se acrescenta dia, janela ou banca; para mudar uma pessoa, use Remarcar. |
| `parametro_publicado_alterado` | duração, intervalo, forma de atendimento ou orientações mudam; uma janela existente muda; uma banca publicada muda de nome, de local ou de endereço da sala | A agenda já foi publicada com «10» minutos e «5» de intervalo, em atendimento «remoto». Depois da publicação, só se acrescenta dia, janela ou banca. |

Nem o **local** nem o **endereço da sala** de uma banca publicada se corrigem pela configuração: a
FR-7208 só admite acréscimo, e a pessoa já recebeu o endereço no aviso, que nenhuma situação de
mensagem desta spec corrigiria. Quem precisa de outra sala acrescenta uma banca e remarca as pessoas
(research T-015).

## 2. Informação, sem recusa (FR-7205, FR-7206, FR-7207, FR-7208)

| Situação | Frase |
|---|---|
| capacidade suficiente | Cabem todas as «43» pessoas. Sobram «21» horários. |
| capacidade insuficiente | Faltam «11» horários para as «43» pessoas. |
| conta por janela | «16» atendimentos por banca × «1» banca |
| lista ainda aberta | A Etapa anterior ainda não tem Resultado: as «43» pessoas são as que participam hoje, e a lista ainda pode mudar. |
| sobra no fim da janela | Em «Seg., 23/11», o último atendimento da janela «13:00–17:00» termina às «16:40»: sobram «15» minutos, que não cabem outro atendimento. |
| configuração salva | Configuração salva. A agenda continua em rascunho: nada é público até você conferir e publicar. |
| configuração salva com devolvidos | Configuração salva, e «2 pessoas voltaram» para "sem horário", porque o horário delas deixou de existir: «Fulana, Beltrano». |

A sobra é `fim − (fim do último atendimento) − intervalo`, informada quando positiva: o intervalo que
sobra depois do último atendimento não é sobra (T-004).

Os atalhos do simulador (04-redesign, decisão 3) dizem o ganho: «Acrescentar Ter., 24/11» «+32»;
«Acrescentar uma banca» «+32»; «Tirar o intervalo» «+16». O atalho que resolve a falta sozinho ganha
destaque.

## 3. Montagem (FR-7211 a FR-7217)

| Código | Quando | Frase |
|---|---|---|
| `horario_ocupado` | o `UNIQUE(agenda, banca, inicio)` recusou, ou o horário já tem alguém sob a trava | **Esse horário acabou de ser ocupado** por outra pessoa da comissão, noutra sessão. A grade foi atualizada; escolha outro. |
| `pessoa_ja_agendada` | o `UNIQUE(agenda, inscricao)` recusou um agendamento novo | «Fulana» já tem horário, em «Seg., 23/11, 09:30». A grade foi atualizada. |
| `pessoa_nao_participa` | agendar quem a projeção não põe na Etapa | «Fulana» não participa desta Etapa: «motivo de `motivo_de_nao_participar`». |
| `horario_inexistente` | o horário não deriva da configuração vigente | Esse horário não existe mais na configuração. A grade foi atualizada. |
| `agenda_mudou_desde_a_previa` | a `versao` da aplicação ≠ a da agenda (FR-7215) | A agenda mudou desde a prévia. Veja a prévia nova antes de aplicar. |
| `agenda_publicada` | preencher ou liberar com a agenda publicada (FR-7240) | A agenda já foi publicada. Para mudar uma pessoa, use Remarcar na agenda publicada. |
| `sem_configuracao` | montar sem configuração | Esta Etapa ainda não tem agenda. Configure os dias, os horários e as bancas primeiro. |

| Situação | Frase |
|---|---|
| prévia | «32» pessoas recebem horário. «11» continuam sem horário. *(ou)* Todas as «43» pessoas recebem horário. |
| ordem da prévia | Ordem: pessoas pelo nome, e pelo protocolo no empate; horários do mais cedo ao mais tarde; as bancas lado a lado em cada horário. |
| aplicada | «32» pessoas receberam horário. |
| à mão | «Fulana» agendada em «Ter., 24/11, 08:15, Banca 1». |
| mudança | «Fulana» passou de «Seg., 23/11, 09:30» para «Ter., 24/11, 14:30». |
| liberação | Horário liberado. «Fulana» voltou para "Sem horário". |
| não participa mais | «Fulana» tem horário, mas não participa mais da Etapa: «motivo». Libere o horário. |
| devolvidos pela configuração (US2, cenário 9) | «2» pessoas voltaram para "Sem horário" porque a configuração de «14/11 às 10:12» removeu o horário delas: «Fulana, Beltrano». |
| completa | Todas as «43» pessoas têm horário. |

## 4. Conferência (FR-7220 a FR-7223, SC-2393)

### Impedimentos (cada um com o caminho de corrigir)

| Código | Frase | Caminho |
|---|---|---|
| `participantes_sem_horario` | «9» pessoas estão sem horário. Toda pessoa que participa da Etapa precisa de um horário antes da publicação: a ausência tem consequência no Edital. Volte à montagem e agende essas pessoas. *(com a lista nominal)* | Voltar à montagem |
| `agendados_que_nao_participam` | «Fulana (INS-…)» tem horário, mas não participa mais da Etapa: «motivo». Volte à montagem e libere o horário. | Voltar à montagem |
| `configuracao_invalida` | A configuração tem problemas: «as frases da seção 1, relidas contra o cronograma vigente». | Ajustar a configuração |
| `banca_sem_local` | «Banca 2» sem «endereço da sala \| local». Quem for atendido nessa banca não saberia aonde ir. Informe na configuração. | Ajustar a configuração |
| `sem_autoridade_vigente` | A unidade do Edital não tem autoridade signatária vigente. Peça ao Administrador institucional que registre uma na tela "Unidades". | Unidades (quem pode) |

### Avisos (não impedem)

| Situação | Frase |
|---|---|
| Etapa sem Evento | Esta Etapa não tem período publicado no cronograma; os dias não foram conferidos contra ele. |
| capacidade sobrando | *(nenhuma: horário livre aparece como livre)* |

### Prontidão (04-redesign, decisão 2)

Quatro linhas no topo, cada uma ✓ ou ✗: «43 de 43 com horário»; «Dias dentro do período do
cronograma»; «Toda banca com endereço de sala | local»; «Autoridade signatária, escolhida no fim da
página».

### Recusas da confirmação

| Código | Quando | Frase |
|---|---|---|
| `agenda_mudou_desde_a_conferencia` | a assinatura enviada ≠ a recomputada (FR-7223) | A agenda mudou desde esta conferência. Confira de novo. |
| `veiculo_nao_escolhido` | nenhum dos dois veículos | Escolha onde a agenda é publicada: na página pública do GPS, ou fora dele. |
| `declaracao_do_veiculo_ausente` | GPS como veículo sem a declaração do item do Edital | Diga o item do Edital que admite a página pública do GPS como veículo da publicação. |
| `publicacao_externa_incompleta` | fora do GPS sem onde ou sem quando | Diga onde e quando a agenda foi publicada fora do GPS. |
| `autoridade_invalida` | autoridade escolhida fora de vigência ou de outra unidade | A autoridade escolhida não está vigente na unidade do Edital. Escolha outra. |
| `ja_publicada` | — | *(não é recusa: a confirmação repetida devolve o ato já criado, com 200 e a tela da agenda publicada; FR-7223, SC-2396)* |

### O botão e os avisos

Com os avisos aos candidatos ligados: «Publicar a agenda e avisar as pessoas», e, acima dele, «A
publicação criará «43» avisos, um para cada pessoa da agenda. O envio sai pelo despacho dos avisos.»

Desligados (`D-011`): «Publicar a agenda», e, acima dele, «Os avisos por e-mail estão desligados nesta
instalação. A agenda vale pela publicação, e nenhum aviso será criado.» A mesma frase vai à agenda
publicada, no lugar do resumo dos avisos.

## 5. Agenda publicada, remarcação, inclusão, cancelamento (FR-7233, FR-7240 a FR-7247)

| Código | Quando | Frase |
|---|---|---|
| `motivo_ausente` | remarcar, incluir ou cancelar sem motivo (US5, cenário 2) | Escreva o motivo. Ele fica na trilha e não aparece para o candidato. |
| `horario_nao_escolhido` | sem horário novo | Escolha o novo horário. |
| `horario_ocupado` | o mesmo da seção 3, sob concorrência (US5, cenário 7) | **Esse horário acabou de ser ocupado** por outra pessoa da comissão, noutra sessão. A lista foi atualizada; escolha outro. |
| `mesmo_horario` | remarcar para o horário atual | «Fulana» já está nesse horário. Escolha outro. |
| `pessoa_ja_agendada` | incluir quem já tem horário | «Fulana» já tem horário publicado. Para mudá-la, use Remarcar. |
| `inclusao_de_quem_nao_participa` | incluir quem a projeção não põe na Etapa | «Fulana» não participa desta Etapa: «motivo». |
| `cancelamento_de_quem_participa` | cancelar quem ainda participa | «Fulana» ainda participa da Etapa. Cancelar o agendamento só cabe a quem deixou de participar; para mudar o horário, use Remarcar. |
| `agenda_nao_publicada` | ato individual antes da publicação | A agenda ainda não foi publicada. Antes da publicação, ajuste a pessoa na montagem. |
| `sem_horario_publicado` | remarcar ou cancelar quem não tem horário publicado | «Fulana» não tem horário publicado. Para agendá-la, use Agendar esta pessoa. |
| `aviso_nao_reenviavel` | reenviar aviso que saiu, que está na fila ou que já tem reenvio (T-024) | O aviso de «Fulana» não está entre os que não saíram. Não há o que reenviar. |
| `aviso_de_agenda_sem_reenvio` | o reenvio pela tela da `066` (T-024) | O aviso de agenda se reenvia pela agenda publicada da Etapa, pessoa a pessoa. |

| Situação | Frase |
|---|---|
| sem horário livre (US5, cenário 8) | Não há horário livre. Acrescente um dia, uma janela ou uma banca na configuração. |
| remarcada | Remarcação feita: «Fulana», «Ter., 24/11, 14:00». Só essa pessoa recebe aviso; a página pública mostra o horário novo, com a marca "remarcado em «14/11»". |
| incluída | Agendamento feito: «Fulana», «Ter., 24/11, 14:00». Só essa pessoa recebe aviso. |
| cancelada | Agendamento cancelado: «Fulana» saiu da agenda vigente, e o horário ficou livre. O que foi publicado antes continua no histórico. |
| passou a participar | Passou a participar depois da publicação *(seção, com "Agendar esta pessoa")* |
| deixou de participar | Tem horário e não participa mais *(seção, com "Cancelar o agendamento")* |
| avisos | «41» avisos enviados. «1» na fila. «1» não entregue. |
| não entregue | O aviso de «Fulana» não foi entregue: «motivo do servidor». A agenda vale para essa pessoa do mesmo jeito, pela publicação. *(com "Reenviar o aviso")* |
| na fila | Os avisos estão na fila e saem em até um minuto. A agenda já está pública. |
| horário fora do período vigente | O Evento da Etapa foi retificado depois da publicação, e «2» horários publicados estão fora do período vigente. Eles continuam valendo como foram publicados. |

O botão da remarcação: «Remarcar e avisar esta pessoa»; o da inclusão: «Agendar e avisar esta
pessoa» — com os avisos desligados, «Remarcar esta pessoa» e «Agendar esta pessoa» (`D-011`); o do cancelamento: «Cancelar o agendamento».

## 6. Portal (FR-7225 a FR-7229, FR-7245)

| Situação | Frase |
|---|---|
| antes da publicação | Seu horário na «Etapa 2 · Entrevista» ainda não foi publicado. A Etapa acontece «de 23 a 25/11/2026», pelo cronograma. |
| publicado | «Terça-feira, 24/11/2026» · «08:15» *(em destaque)*; Duração prevista de «10» minutos; Banca «1»; Local «…» \| botão «Entrar na sala virtual» |
| remarcado | Seu horário mudou em «14/11». O horário anterior não vale mais. |
| página pública, busca | Encontre o seu horário pelo número de inscrição «ou pelo nome». |
| página pública, sem resultado | Nenhum horário com esse número «ou nome». Confira o número na sua área: Minhas inscrições. |
| página pública, marca | remarcado em «14/11/2026» |
