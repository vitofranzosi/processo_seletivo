# 2. Proposta: a agenda da Etapa

*Tudo aqui é **proposta** [P], salvo onde cita fato do diagnóstico. As regras R-01 a R-26 são as
que o protótipo demonstra; o comentário de cada trecho de `prototipo/static/agenda.js` aponta a
sua.*

## 2.1 O princípio

**A Etapa diz quem participa. A agenda diz quando e onde cada pessoa é atendida. A avaliação continua
onde está.**

A agenda **existe ou não**. Não há caixa "esta Etapa exige agendamento" no Edital: a comissão
configura a agenda da Etapa que pede comparecimento, e a que não pede simplesmente não tem agenda.
Uma caixa no Edital seria norma nova, retificável e sem efeito próprio — o que o Edital precisa dizer
sobre comparecimento (onde se publica, o que acontece com quem falta) ele já diz em texto, e a
ausência já é Ocorrência.

## 2.2 Jornada da comissão

**Configurar → Montar → Conferir → Publicar → Avisar → Remarcar.**

1. **Configurar** (tela "Configurar a agenda", a partir da página da Etapa). Atendimento remoto ou
   presencial; duração; intervalo; dias, com uma ou mais janelas por dia; bancas, cada uma com nome e
   local ou endereço da sala; orientações ao candidato. A capacidade é calculada **enquanto se
   digita**, no painel ao lado, e comparada com quem participa hoje. Dá para configurar antes de a
   lista fechar.
2. **Montar** (tela "Montar a agenda"). No alto, o resumo: participam, horários, com horário, sem
   horário, livres — e, se faltar, "Faltam 11 horários" com o caminho para ajustar. Uma aba por dia,
   com a grade horário × banca. Ao lado, "Pessoas sem horário". Duas formas de alocar:
   - **"Preencher horários livres"** mostra uma **prévia** (quem vai para onde, quantas sobram, a
     ordem usada), e só "Aplicar" grava;
   - **à mão:** clicar numa pessoa e escolher, no painel, um horário livre de qualquer dia; ou
     clicar num horário livre e escolher quem vai para ele. Sem arrastar nada. *(Redesenhado na
     segunda rodada: ver [04-redesign.md](04-redesign.md).)*
3. **Conferir** (tela "Confira antes de publicar a agenda", a mesma moldura da `140`). O que impede,
   em destaque e com o caminho para resolver; o que será publicado; a prévia exata da página
   pública; a mensagem de cada pessoa; a autoridade signatária. Nada é gravado aqui.
4. **Publicar.** Um botão: "Publicar a agenda e avisar as pessoas". Nasce um ato imutável, a página
   pública e a área de cada pessoa passam a mostrar o horário, e os avisos entram na fila.
5. **Acompanhar** (tela "Agenda publicada"). Quantos avisos saíram, quantos estão na fila, quais
   falharam e "Reenviar o aviso"; quem passou a participar depois da publicação e "Agendar esta
   pessoa"; a lista com "Remarcar" em cada linha.
6. **Remarcar** (tela "Remarcar uma pessoa"). Escolher um horário livre, escrever o motivo, e
   confirmar: só aquela pessoa muda e só ela é avisada.

## 2.3 Jornada do candidato

1. Antes da publicação, a área dele diz "Seu horário ainda não foi publicado", com o período do
   cronograma.
2. Publicada a agenda, recebe um aviso por e-mail, e a área mostra o dia e a hora em destaque, a
   duração, a banca, **o botão da sala virtual** (ou o local), e as orientações.
3. Na página pública da seleção, encontra o próprio horário pelo número de inscrição (ou pelo nome,
   onde ele é público).
4. Remarcado, a área abre com "Seu horário mudou em 14/11. O horário anterior não vale mais", e um
   aviso novo chega só a ele.

## 2.4 As regras

### Configuração e capacidade

- **R-01** A agenda é da Etapa e operacional: referida por `etapa_id` (como `AlocacaoEtapa`), uma
  por Etapa. Não muda o Edital nem pede Retificação.
- **R-02** Quem participa vem da projeção da Etapa (`participacao_detalhada`), sempre. A agenda não
  tem lista de participantes.
- **R-03** A configuração tem: forma de atendimento (remota ou presencial), duração e intervalo em
  minutos, dias com janelas, bancas (nome; local ou endereço da sala), orientações.
- **R-04** **Os horários são derivados, não gravados.** Em cada janela, o primeiro atendimento
  começa no início; o seguinte, depois da duração mais o intervalo; o último termina até o fim da
  janela. Cada horário existe uma vez por banca.
- **R-05** A configuração **recusa**, com frase que diz o que fazer: dia fora do período do Evento da
  Etapa no cronograma vigente; janela que termina antes de começar; janela menor que a duração;
  janelas que se sobrepõem no mesmo dia; banca sem nome ou com nome repetido. **Informa**, sem
  recusar, a sobra no fim de uma janela que não cabe outro atendimento.
- **R-06** Capacidade = horários × bancas. Insuficiência é **aviso** na configuração e na montagem,
  com o número que falta; vira **impedimento** na publicação, pela R-13.
- **R-07** Mudar a configuração **não move ninguém em silêncio**. Em montagem, quem estava num
  horário que deixou de existir volta para "sem horário", e a tela diz quem. Publicada a agenda, só
  se acrescenta (dia, janela, banca); um horário publicado e ocupado não se remove.

### Montagem

- **R-08** Uma pessoa tem no máximo um horário na agenda; um horário de uma banca tem no máximo uma
  pessoa. As duas são constraints no banco, e não só checagem.
- **R-09** O preenchimento automático usa **uma ordem**, escrita na tela: pessoas por nome, e pelo
  protocolo no empate; horários do mais cedo ao mais tarde; com mais de uma banca, as bancas lado a
  lado em cada horário. Aloca só quem está sem horário, só em horário livre, e nunca mexe em quem já
  tem horário.
- **R-10** O preenchimento tem **prévia sem efeito**. A aplicação leva a versão da agenda; se ela
  mudou desde a prévia, a aplicação recusa e mostra a prévia nova.
- **R-11** **Dois operadores no mesmo horário:** quem confirma depois é recusado pela unicidade, com
  "Esse horário acabou de ser ocupado", e vê a grade atualizada.

### Conferência e publicação

- **R-12** A conferência não grava, não envia e não reserva nada (padrão da `140`).
- **R-13** **Impedem a publicação:** pessoa que participa sem horário; pessoa agendada que não
  participa mais; configuração que a R-05 recusa (inclusive se o Evento foi retificado depois);
  banca sem local ou endereço; nenhuma autoridade vigente.
- **R-14** A confirmação leva a **assinatura da conferência** (configuração e pares
  pessoa-horário) e a **chave de idempotência**. Agenda mudada desde a conferência: recusa e refaz
  a conferência. Clique repetido: devolve o ato já criado, sem segundo ato e sem segundo aviso.
- **R-15** A publicação é **ato append-only**: autor, autoridade signatária, instante, conteúdo
  público em bytes canônicos com SHA-256, como a `149`.
- **R-16** O conteúdo público tem, por pessoa: dia, horário, banca (o nome) e a identificação da
  R-25. **Nunca** o endereço da sala, CPF, e-mail ou telefone.
- **R-17** **Avisos.** Um por pessoa, pela origem nova AGENDA do app de avisos (`066`), que cita o
  ato. A confirmação não envia: o despacho envia depois, como hoje. Um aviso por pessoa por ato.
- **R-18** **Falha de envio não desfaz o ato.** A agenda vale para quem não recebeu o e-mail; a tela
  da agenda publicada lista as falhas, e o reenvio é o da `066`.

### Depois da publicação

- **R-19** Publicada a agenda, **acabou a edição em bloco**: não há preenchimento automático nem
  "Liberar" sobre horário publicado. Toda mudança é **ato individual**, com motivo.
- **R-20** **Remarcação**: um horário livre, motivo obrigatório (na trilha, nunca para o candidato
  nem para o público), ato append-only que **substitui** o item anterior sem apagá-lo. Página
  pública e área da pessoa mostram o horário novo com "remarcado em"; o anterior fica no histórico.
  Só essa pessoa é avisada.
- **R-21** **Inclusão**: quem passa a participar depois da publicação (recurso deferido,
  reabilitação) aparece em "Passou a participar depois da publicação", e é agendado um a um, pelo
  mesmo ato da remarcação, sem horário anterior.
- **R-22** **Cancelamento**: quem estava agendado e deixou de participar (eliminado por outra via)
  aparece sinalizado; cancelar o agendamento é ato individual com motivo, que tira a pessoa da lista
  vigente sem apagar o publicado.

### O que a agenda não faz

- **R-23** A agenda não registra presença, nota, parecer nem ausência. A ausência continua sendo
  Ocorrência na Etapa; a tela da Ocorrência pode **mostrar** o horário publicado, como informação.
- **R-24** O endereço da sala virtual só chega à própria pessoa: na área dela, identificada, e no
  e-mail dela.
- **R-25** A identificação pública é **nome e protocolo**, como a `149`, salvo quando a Etapa revela
  dado sensível — a de alcance por Modalidade reservada (heteroidentificação) —, quando é **só o
  protocolo**. Ver a decisão pendente Q-2.
- **R-26** O GPS **não calcula prazo** a partir do horário (a justificativa de 24 h do 28/2026 fica
  com o Edital); ele grava e mostra o horário como dado do ato.

## 2.5 Modelo mínimo de domínio

Cinco tabelas novas — três operacionais e duas append-only — e uma origem nova num enum existente.
Nada muda em `EtapaAvaliacao`, `EventoCronograma`, `Inscricao` ou `ResultadoEtapa`.

```text
AgendaDaEtapa ─────────┬── JanelaDaAgenda (n)
 (operacional)         ├── BancaDaAgenda (n)
 edital, etapa_id      └── Agendamento (n) ─── Inscricao
 forma, duração,            (operacional: o estado corrente)
 intervalo, orientações,
 versão                 AtoDaAgenda (append-only) ─── HorarioPublicado (n, append-only)
                         PUBLICACAO | REMARCACAO |          inscrição, banca, início, fim,
                         INCLUSAO | CANCELAMENTO             substitui → HorarioPublicado
                                │
                                └── Aviso (066), origem AGENDA
```

| Entidade | Para quê | Invariantes |
|---|---|---|
| `AgendaDaEtapa` | a configuração; uma por Etapa | `UNIQUE(edital, etapa_id)`; duração > 0; intervalo ≥ 0; `versao` para a R-10 (CAS, `shared/concurrency.py`) |
| `JanelaDaAgenda` | dia e intervalo de atendimento | início < fim; fim − início ≥ duração; sem sobreposição no dia (domínio) |
| `BancaDaAgenda` | ponto de atendimento | `UNIQUE(agenda, nome)`; local ou endereço obrigatório para publicar |
| `Agendamento` | quem está em que horário **agora** | `UNIQUE(agenda, inscricao)`; `UNIQUE(agenda, banca, inicio)`; origem MANUAL ou AUTOMATICA |
| `AtoDaAgenda` | publicação, remarcação, inclusão, cancelamento | append-only; autor; autoridade (na publicação); motivo (nos individuais); chave de idempotência; conteúdo público + SHA-256 |
| `HorarioPublicado` | o que cada ato publicou | append-only; `substitui` aponta o item que ele troca; vigente = não substituído |

**Por que `Agendamento` continua depois da publicação.** É a tabela com as duas unicidades, e é ela
que barra dois operadores no mesmo horário (R-11) — inclusive na remarcação. O ato atualiza o
`Agendamento` e grava o `HorarioPublicado` na mesma transação; o histórico mora no append-only.

**Por que os horários não são tabela.** São função da configuração (R-04). Gravá-los seria uma
segunda fonte, e uma janela mudada exigiria reconciliar linhas.

**Alternativa descartada: reusar `Convocacao`.** Ela é de **vaga** (`019`), com espécie, chamada,
sucessão e prazo que corre do envio; a agenda não tem nenhum dos quatro. Reusá-la faria a
ocupação de vagas enxergar "convocados" que não foram chamados para vaga nenhuma.

**Alternativa descartada: horário no `EventoCronograma`.** O Evento é norma e é um só por Etapa.

## 2.6 Concorrência e repetição

| Situação | Defesa |
|---|---|
| Dois operadores no mesmo horário | `UNIQUE(agenda, banca, inicio)` + trava da agenda no comando; a segunda recebe recusa nomeada |
| A mesma pessoa em dois horários | `UNIQUE(agenda, inscricao)` |
| Preenchimento sobre agenda que mudou | `versao` na prévia; recusa e prévia nova |
| Publicar uma agenda diferente da conferida | assinatura da conferência (R-14) |
| Duplo clique em "Publicar" | chave de idempotência; o segundo devolve o primeiro ato |
| Aviso duplicado | `UNIQUE(aviso, inscricao)` da `066`; um aviso por ato e pessoa |
| Remarcar duas vezes ao mesmo tempo | trava da agenda; o segundo vê o horário já trocado e recusa |

## 2.7 Os dois cenários

**A — Entrevista (Cefor, 146/2025).** Etapa 2, 43 pessoas habilitadas na análise documental. A
comissão configura 23/11, das 8h às 12h e das 13h às 17h, 10 min com 5 de intervalo, uma banca: 32
horários. A tela diz "faltam 11". Acrescenta 24/11: 64. Preenche, ajusta duas à mão, confere,
publica. Uma pessoa perde a conexão: a comissão a remarca para 24/11 às 14h, com o motivo "falha de
conexão comprovada, item 6.9.9". Depois da entrevista, a Mesa registra a nota como hoje; quem faltou
recebe Ocorrência.

**B — Verificação da autodeclaração (28/2026, com a `163`).** Etapa 3, alcança só a reserva para
pretos e pardos: 23 pessoas. Duas salas da RNP, duas bancas da CLVA, 20 min com 10 de intervalo:
uma manhã dá 16, falta 7; com a tarde, 32. A página pública mostra **só o protocolo**; a sala vai a
cada pessoa; as orientações repetem o 6.9 do Edital (documento, nome = número do documento, menor
com responsável, gravação). Os pareceres são os da `165`; nada disso passa pela agenda.

**O que é do núcleo e o que é de cada Etapa.** Núcleo: horários, bancas, montagem, publicação,
aviso, remarcação. Da Etapa, e só como **texto** das orientações ou como dado que já existe em
outra spec: documento exigido, menor com responsável, gravação, tentativas de conexão, consequência
da ausência, composição da banca, exposição da Modalidade. O agendamento não tem regra de
heteroidentificação.

## 2.8 Decisões de interface

- **Uma aba por dia**, e não a semana numa tela: com 3 dias de 32 horários, a grade inteira passa
  de 100 linhas. A aba mostra "32/32" ocupados.
- **"Pessoas sem horário" fixa ao lado** no desktop, e acima da grade em telas menores que 64rem.
- **A grade é o que se vê; o painel é onde se age.** Clicar numa pessoa ou num horário livre abre
  o painel com as escolhas; nenhum botão se repete pela grade. Funciona com teclado, leitor de tela e
  toque; arrastar seria um extra, nunca o caminho. (Segunda rodada, [04-redesign.md](04-redesign.md).)
- **No celular, a grade vira lista cronológica** com a banca dentro de cada bloco — a mesma
  marcação, só CSS.
- **A ação principal é a que falta fazer**: "Preencher automaticamente" enquanto há gente sem
  horário; "Conferir e publicar" depois.
- **Estados vazios ensinam**: "Esta Etapa ainda não tem agenda" diz para que serve e que dá para
  configurar antes de a lista fechar.
- **Mensagens dizem o que fazer**: "A janela 12:00–12:05 não comporta um atendimento de 10 minutos.
  Amplie a janela ou reduza a duração."
- **Tudo com as folhas reais** da gestão e do portal, sob a CSP de produção: nenhum estilo em
  linha. As peças novas (grade, painel de capacidade, lista pública) cabem num arquivo de tela.

## 2.9 As cinco perguntas do registro de 09/10

| Pergunta | Resposta proposta |
|---|---|
| Convocar para Etapa é ato próprio, com lista congelada? | **Sim**: a publicação da agenda é ato, e congela os pares pessoa-horário publicados. A participação continua projeção; a diferença aparece como "sem horário" ou "não participa mais" |
| Quem é alcançado na heteroidentificação? | Quem a Etapa alcança, pela `163`. A agenda não decide |
| Horário individual, ou data e local por Etapa? | Horário individual, com banca |
| Exposição da Modalidade | Só o protocolo na página pública quando a Etapa tem alcance por Modalidade (Q-2) |
| Relação com o aviso | Origem nova do aviso da `066`, com revisão da FR-084 (Q-5) |
