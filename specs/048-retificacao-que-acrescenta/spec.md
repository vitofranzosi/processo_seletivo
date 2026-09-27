# Feature Specification: A Retificação acrescenta o que o contrato já permite

**Feature Branch**: `claude/retificacao-cobertura-auditoria-b7eabb`

**Created**: 2026-09-26

**Status**: Draft

**Input**: proposta do usuário de 26/09/2026, *"SPEC 048 — Cobertura de retificação das informações
publicadas"*. Consolida a B-4 da [auditoria de consolidação](../../doc/auditoria-de-consolidacao-2026-09-26.md)
— `RC-37` (a `D-G5`) e `RC-38` — e executa o item 2 da recomendação da `DP-08` das
[decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md): a `D-G5` vai para a B-4.

> **Faixa de identificadores.** Abre em **FR-777** e **SC-288**. O teto medido em 26/09/2026 em todas
> as worktrees e nas branches abertas é 776 para os requisitos funcionais e 287 para os critérios de
> sucesso, da `047` (PR #191, ainda não mesclado) — escritos por extenso porque nenhuma spec desta
> árvore os define. **Dois números ficaram sem uso**, o 783 dos requisitos e o 293 dos critérios: eram da
> guarda genérica de objeto inteiro, retirada pelo parecer de 26/09 (achado A-6). Não foram
> reaproveitados, para não mudar o sentido de quem já os leu. Nenhuma espécie `UX-` nova: as frases desta feature são recusas e avisos da
> validação, que já têm gramática própria. As **decisões** reiniciam em `D-001`; decisão de outra spec
> é citada pelo requisito que a registra, e nunca pelo número local dela.

> **Teto proporcional.** Dois achados, cinco objetos concretos. Cada requisito tem de nomear o que a
> tela ou o ato fazem de diferente; o que não passar nisso é nota de tarefa.

---

## Por que esta feature existe

**A Constituição já decidiu a questão, e o código ainda não a cumpriu.** O Princípio VI diz que *"uma
capacidade que o domínio sustenta mas que nenhuma interface alcança NÃO DEVE ser considerada
entregue"*. A verificação de 26/09 mostrou que é esse o caso dos dois achados. O domínio e a API já
aceitam acrescentar Modalidade a um Perfil publicado e fazer nascer janela recursal, regra de corte e
reversão. O contrato de mutabilidade da `026` declara que os três últimos *"podem passar a existir"*
(`FR-313`). Mas a tela da Retificação não oferece nenhum desses caminhos, e ela é o único canal de quem
retifica.

O custo é concreto, e a auditoria o chamou de *"o único caso de Edital publicado sem correção
possível"* (19/09 e 20/09):

| | O que acontece hoje | Conferido em 26/09, em `717eb0c` |
|---|---|---|
| `RC-37` | Um Perfil publicado com duas ou mais cotas e **sem a ampla concorrência** não recebe inscrição de quem não é cotista: o formulário exige escolher uma das Modalidades declaradas. A tela da Retificação diz, com todas as letras, *"Modalidades de Concorrência ainda não são definidas por aqui"*. O único remédio é cancelar e republicar | `SECOES_QUE_ACRESCENTAM = {perfis, cronograma, anexos}` (`interface/retificacao.py:1108`); `retificar.html:158-159`; inscrição em `inscricoes/application/rascunho.py:280-313` |
| `RC-38` · corte | Desde a `037` e a `046`, a tela do corte manda o marco sem regra para *"Retificar o Edital para declarar a regra de corte"*. A Retificação não oferece campo nenhum da regra para esse marco, e o caminho termina num beco | `views.py:6203-6229`; `retificacao.py:905`; `test_corte.py:373-386` prende o link, e nada prende o destino |
| `RC-38` · janela e reversão | Um marco publicado sem janela recursal não a ganha pela tela, nem um Perfil sem reversão. A ausência da reversão é **presa por teste** | `retificacao.py:816-817, 912`; `tests/interface/test_retificar_reversao.py:84-94` |
| `RC-38` · desempate | A Retificação **remove** um critério de desempate, mas não o **acrescenta**. A tela só consegue reduzir a regra de desempate, e não corrigi-la | `retificacao.py:979-990` (removível); `CAMPOS_CRITERIO` só tem a ordem |

### A avaliação da proposta

A proposta foi conferida contra a `main` em `717eb0c`. **A direção se sustenta**: os dois achados
continuam com a mesma identificação, continuam `NÃO IMPLEMENTADO` e nenhuma spec de `027` a `046` os
absorveu (a varredura de `specs/` por *"pode passar a existir"*, `FR-313` e *"nascer"* só encontra a
`026`). A verificação mudou oito coisas na forma, e nenhuma mudou a direção.

1. **O inventário não é requisito do sistema: é esta spec.** O primeiro requisito da proposta dizia *"o sistema MUST
   ter suas informações… identificadas"*, e isso não é comportamento que um teste observe. O inventário
   foi feito agora e mora na seção [*Inventário*](#inventário-o-que-a-retificação-alcança-e-o-que-não-alcança).
   Os requisitos abaixo são só o que ele confirmou.
2. **O mecanismo já existe, e ele é mais genérico do que a proposta temia.** Há dois caminhos de
   acréscimo na Retificação. O primeiro é o **nascimento de objeto**: um objeto ausente é declarado
   inteiro num ato só. É o caminho do método do sorteio, desde a `021`. O segundo é o **acréscimo de
   item a coleção**: Perfil, linha do quadro, Evento e Anexo. Todos os casos desta spec cabem num dos
   dois. O terceiro e o quarto requisitos da proposta se cumprem sem abstração nova, e a spec as mantém como restrição
   (`FR-802`).
3. **A "inclusão de elementos" tem dois casos concretos, e só dois**: Modalidade num Perfil e critério
   de desempate num marco. Os dois estão na auditoria e na B-4. Nenhum outro foi generalizado.
4. **Três das cinco restrições da `D-G5` já valem por construção, e nenhuma está demonstrada.** A
   inscrição congela a Modalidade escolhida no envio (`inscricoes/models.py:34`). A ordem é por recorte,
   e a Modalidade nova não torna obsoleta a de nenhum outro recorte (`classificacao/domain/universo.py`).
   O recorte novo aparece sem ordem, e nada a emite sozinho. Mas o teste que devia prová-lo
   (`test_ordem_por_recorte.py:356`) não retifica nada: ele emite outro recorte e remete ao cenário 5.2
   da `034`, que nunca foi executável. **A demonstração é trabalho desta spec** (`SC-289`).
5. **Três restrições apareceram, e o usuário as decidiu em 26/09.**
   - A janela que nasce depois de um resultado divulgado pode transformar o silêncio do Edital em
     recusa de recurso: `D-003`.
   - A regra de corte que nasce depois de a Etapa governada ter Resultado tira dela quem já foi
     avaliado: `D-002`.
   - O critério de desempate entra: `D-004`.
6. **O contrato não é aplicado a objeto inteiro, e isso fica registrado, e não resolvido.** A gramática
   recusa um campo não retificável endereçado sozinho, mas aceita pela API a substituição do objeto
   inteiro que o contém. A porta é anterior a esta feature e não nasceu dos achados da auditoria. A
   primeira redação a fechava com uma guarda genérica, e o parecer de 26/09 a retirou: achado incidental
   vira registro, e não escopo (achado A-6). A tela desta feature não a usa para trocar: ela só oferece
   os campos de nascimento quando o objeto está ausente.
7. **A "prévia" da proposta não existe na Retificação, e não será criada.** Na Retificação, a
   conferência é o resumo *antes → depois* e as advertências do ato. O documento PDF nasce na
   publicação, a partir do conteúdo retificado, e já mostra o que o conteúdo tiver. O segundo cenário da proposta
   virou `FR-800`, sobre a conferência que existe.
8. **Forma.**
   - A numeração da proposta, que recomeçava em um, entra na faixa global.
   - O ator *"presidente/operador"* é, no sistema, quem tem a capacidade de elaborar Retificação.
   - A proposta dizia *"a 047 apresenta o estado retificado"*. Ela apresenta, mas o *"O que mudou"*
     público cala os nascimentos (`RC-111`): ver *Achados registrados*.

---

## Inventário: o que a Retificação alcança, e o que não alcança

Extraído do contrato de mutabilidade (`editais/domain/mutabilidade.py`, `CONTRATO` e
`PODE_PASSAR_A_EXISTIR`), dos caminhos de acréscimo de `interface/retificacao.py` e dos achados da
auditoria. **Só entra aqui o que o sistema já cadastra e publica.** Nenhuma linha foi acrescentada para
ampliar o escopo.

Classes: **A** deve ser retificável e passa a ser · **B** não deve, com razão escrita · **C** já
resolvido · **D** pertence a outro problema.

| Informação | Cadastrável? | Publicada? | Retificável hoje? | Deve ser? | Classe e ação |
|---|:-:|:-:|:-:|:-:|---|
| Modalidade nova num Perfil publicado (`RC-37`) | sim | sim | só pela API | sim — `D-G5` | **A** · `FR-777` a `FR-782` |
| Janela recursal de marco que não a declarava (`RC-38`) | sim | sim | só pela API | sim, concedendo | **A** · `FR-786`, `FR-787`; `D-003` |
| Regra de corte de marco que não cortava (`RC-38`) | sim | sim | só pela API | sim, com guarda | **A** · `FR-788` a `FR-790`; `D-002` |
| Reversão de Perfil que não a declarava (`G16-001`, em `RC-38`) | sim | sim | só pela API | sim | **A** · `FR-791` |
| Critério de desempate novo num marco (NOVO-3 do lote 5, em `RC-38`) | sim | sim | não | sim | **A** · `FR-792` a `FR-794`; `D-004` |
| Troca da espécie do alvo, Etapa governada ou continuação por substituição do objeto inteiro | — | sim | **sim, pela API** — e não devia | não | **D** · porta anterior, fora dos achados da auditoria: achado A-6 |
| Regra normativa em Modalidade **já publicada** sem regra | sim | sim | não | não | **B** · razão no contrato: *"é criar reserva que o Edital publicado não tinha"*. Continua (`D-001`) |
| Campos não retificáveis soltos — número, ano, espécie do cadastro reserva, tipo do critério, espécie do Evento etc. | sim | sim | não | não | **B** · razão normativa escrita em cada entrada; `RC-98` resolvido |
| Campos derivados e estruturais — fase do Evento, identidades, Etapa do Evento | — | sim | não | não | **B** · a convergência de 20/09 (§21) vetou retificá-los |
| Método do sorteio de marco que não o declarava | sim | sim | sim | sim | **C** · `021` e segunda revisão do PR #114 |
| Linha do quadro nova · Perfil novo · Evento novo · Anexo novo | sim | sim | sim | sim | **C** · `025` e anteriores |
| Documento Exigido novo · Fato, Marco, Etapa ou Seção novos | sim | sim | não | — | **fora** · nenhum achado da auditoria; a restrição do Documento tem razão escrita na tela. Nada muda |
| *"O que mudou"* público cala os nascimentos e 45 dos 84 campos | — | — | — | — | **D** · `RC-111`, dicionário e guardião |
| Alcance da Etapa por Perfil ou Modalidade | não | — | — | — | **D** · `RC-64`, B-17, espera a `DP-10` |
| Catálogo de Modalidades no Edital (`039`) | não | — | — | — | **D** · `DP-08`, item 1: encerrar a `039` é decisão à parte |

---

## User Scenarios & Testing *(mandatory)*

> **Prioridade é valor, e não ordem de execução.** A ordem de implementação fica com o
> [plano](plan.md).

> **Conferir e confirmar são duas fases, e os cenários as distinguem.** *Conferir* é a primeira fase
> do formulário: mostra o resumo *antes → depois* e ainda não grava nada. *Confirmar* grava o ato, e é
> nela que a validação de publicação corre sobre o conteúdo resultante, como já acontece hoje. Uma
> recusa sobre a entidade acrescentada vem **ao conferir**; uma recusa que depende do conteúdo
> resultante inteiro vem **ao confirmar**.

### User Story 1 - Um Perfil publicado ganha a Modalidade que faltava (Priority: P1)

Quem retifica abre a Retificação de um Edital publicado. Sob um Perfil, acrescenta uma Modalidade de
Concorrência com os mesmos campos da composição. Se ela for cota, dá a ela, no mesmo ato, a sua linha
do quadro; se for a ampla concorrência, declara-a como tal, e as vagas dela são as da linha geral do
quadro. Confere o resumo e publica. Daí em diante, quem se
inscreve naquele Perfil encontra a Modalidade entre as opções.

**Why this priority**: é o único Edital publicado sem conserto possível. Sem a ampla, o não-cotista
não se inscreve. O remédio de hoje, cancelar e republicar, desfaz um ato que já produziu efeito.

**Independent Test**: publicar um Edital cujo Perfil declara duas cotas e nenhuma ampla; retificá-lo
pela tela acrescentando a ampla, declarada como tal, com as vagas na linha geral; conferir que a
inscrição passa a oferecê-la; conferir que as ordens já emitidas da ampla e das cotas continuam
vigentes. Repetir acrescentando uma cota com vagas, e conferir que o recorte dela aparece sem ordem.

**Acceptance Scenarios**:

1. **Given** um Perfil publicado sem a ampla concorrência, **When** quem retifica acrescenta a
   Modalidade, a declara ampla e publica, **Then** a versão nova oferece a Modalidade na inscrição, e o
   documento da Retificação a mostra.
2. **Given** uma cota acrescentada com as suas vagas, **When** quem retifica confere antes de confirmar,
   **Then** o resumo mostra o acréscimo da Modalidade e o da linha do quadro, cada um com *antes* e
   *depois*; e **Given** a ampla acrescentada, **Then** o resumo mostra a declaração da ampla.
3. **Given** inscrições já enviadas por uma cota, **When** a Retificação é publicada, **Then** nenhuma
   delas muda de Modalidade nem de lista exigida.
4. **Given** uma ordem já emitida para um recorte de cota, **When** a Retificação que acrescenta outra
   Modalidade é publicada, **Then** essa ordem continua vigente; e, sendo cota a Modalidade nova, o
   recorte dela aparece sem ordem até alguém emiti-la. A ampla declarada não cria recorte: ela é o da
   linha geral, que já existia.
5. **Given** uma Modalidade acrescentada com código igual ao de outra do mesmo Perfil, ou sem
   denominação, ou com fundamento e sem versão, **When** quem retifica confere, **Then** o ato é
   recusado com a mesma razão que a composição daria.
6. **Given** uma Modalidade de cota acrescentada sem linha no quadro, **When** quem retifica confirma,
   **Then** vale a mesma validação da publicação sobre o conteúdo retificado: aviso, ou recusa se um
   corte derivar o alvo do quadro.
7. **Given** a Modalidade acrescentada declarada ampla **e** com vagas próprias, **When** quem retifica
   confere, **Then** o ato é recusado: as vagas da ampla são as da linha geral, que é a regra que a
   publicação já aplica.

---

### User Story 2 - A tela do corte deixa de terminar num beco (Priority: P2)

Quem abre a tela do corte de um marco sem regra segue o caminho *"Retificar o Edital para declarar a
regra de corte"*. Chega a uma Retificação que oferece a regra inteira para aquele marco, declara-a e
publica. Se a Etapa que o corte governaria já tiver Resultado, o ato é recusado, e a recusa diz por quê.

**Why this priority**: a `037` e a `046` criaram o caminho, e ele termina num beco. É o `ACH-40` de
novo: um caminho aberto para remover um beco que entrega outro.

**Independent Test**: publicar um Edital com um marco sem regra de corte, seguir o link da tela do
corte, declarar a regra e publicar; conferir que o corte pode ser emitido. Repetir com Resultado já
registrado na Etapa governada e conferir a recusa.

**Acceptance Scenarios**:

1. **Given** um marco publicado sem regra de corte, **When** quem retifica abre a Retificação, **Then**
   o marco oferece a regra inteira: espécie do alvo, quantidade, excedente, desfecho do empate, Etapa
   governada e continuação.
2. **Given** a regra declarada inteira, **When** a Retificação é publicada, **Then** o marco passa a
   cortar pela versão nova, e a tela do corte deixa de recusar por falta de regra.
3. **Given** a regra declarada pela metade, **When** quem retifica confirma, **Then** o ato é recusado
   com as mesmas mensagens da publicação.
4. **Given** uma Etapa governada que já tem Resultado registrado, **When** quem retifica declara a regra
   que a governaria, **Then** o ato é recusado, nomeando o marco e a Etapa, e dizendo que o corte
   excluiria dela quem já foi avaliado.
5. **Given** um marco que **já tem** regra de corte, **When** quem retifica abre a Retificação, **Then**
   os três campos não retificáveis continuam fora da tela, com a razão, como hoje.

---

### User Story 3 - O marco sem janela recursal ganha o prazo de recurso (Priority: P3)

Quem retifica declara, num marco que não previa recurso, em quantos dias corridos ele admite recurso.
A tela não pergunta se admite, porque a única janela que pode nascer é a que concede; declarar *"não
admite"* onde o Edital calava só seria possível pela API, e ali é recusado.

**Why this priority**: conceder prazo de recurso é a correção mais comum que o Edital precisa depois da
publicação, e a menos arriscada, porque não retira direito de ninguém.

**Independent Test**: publicar um Edital com marco sem janela; retificar declarando que admite recurso
em 3 dias corridos; conferir que a interposição passa a contar o prazo; conferir que a tela não
oferece *"não admite"*. A recusa de *"não admite"* pela API é teste de integração.

**Acceptance Scenarios**:

1. **Given** um marco sem janela recursal, **When** quem retifica declara que admite recurso em N dias
   corridos, com N maior que zero, e publica, **Then** a versão nova tem a janela, e a interposição a lê.
2. **Given** o mesmo marco, **When** quem retifica abre a Retificação, **Then** a tela oferece só o
   prazo, e não a pergunta *"admite recurso?"*; e **Given** uma Retificação pela API que faz nascer a
   janela com *"não admite"*, **Then** o ato é recusado: a Retificação concede prazo onde não havia, e
   não o retira.
3. **Given** um marco sem janela, **When** quem retifica altera qualquer outro campo do Edital e não toca
   a janela, **Then** nenhuma janela nasce.
4. **Given** um marco que **já tem** janela, **When** quem retifica a altera, **Then** vale a regra de
   hoje, sem mudança.

---

### User Story 4 - O critério de desempate se corrige, e não só se reduz (Priority: P4)

Quem retifica acrescenta a um marco publicado um critério de desempate, com o que ele compara, o
parâmetro, o que fazer quando o valor não existe e a ordem de aplicação.

**Why this priority**: sem isso, trocar o critério errado é impossível. A tela remove o errado e não
põe o certo no lugar.

**Independent Test**: publicar um Edital com um critério de desempate; retificar removendo-o e
acrescentando outro; conferir o conteúdo vigente e que a ordem já emitida daquele marco fica obsoleta e
recomputável.

**Acceptance Scenarios**:

1. **Given** um marco publicado, **When** quem retifica acrescenta um critério completo e publica,
   **Then** a versão nova o tem, e a ordem já emitida daquele marco fica obsoleta, como já fica hoje
   quando um critério é removido.
2. **Given** um critério com ordem igual à de outro do mesmo marco, ou com parâmetro que aponta Etapa
   não classificatória ou fato de outro Perfil, **When** quem retifica confere, **Then** o ato é recusado com a
   razão da composição.
3. **Given** um critério removido e outro acrescentado no mesmo ato, **When** a Retificação é publicada,
   **Then** as duas alterações valem juntas.

---

### User Story 5 - O Perfil sem reversão passa a declará-la (Priority: P5)

Quem retifica escolhe, num Perfil publicado sem reversão de vaga reservada, a espécie da reversão e
publica.

**Why this priority**: é o `G16-001`, e é o menor dos cinco: um campo de escolha, com a validação que
já existe.

**Independent Test**: publicar um Edital com quadro e sem reversão; retificar declarando a espécie;
conferir o conteúdo vigente. Repetir num Perfil sem quadro e conferir a recusa.

**Acceptance Scenarios**:

1. **Given** um Perfil com quadro e sem reversão, **When** quem retifica escolhe a espécie e publica,
   **Then** a versão nova declara a reversão.
2. **Given** um Perfil sem quadro, **When** quem retifica declara a reversão sem acrescentar linha no
   mesmo ato, **Then** o ato é recusado pela validação que já existe; e **Given** a linha acrescentada no
   mesmo ato, **Then** passa.
3. **Given** um Perfil sem reversão, **When** quem retifica deixa o campo em *"Nenhum"*, **Then** nada
   nasce.

---

### Edge Cases

Estes casos são requisitos. Cada um tem linha na matriz de rastreabilidade.

- **Perfil acrescentado no mesmo ato.** Ele nasce sem Modalidade, como hoje. A Modalidade dele entra na
  Retificação seguinte, pela mesma razão que já vale para as linhas do quadro: a identidade do Perfil
  nasce no servidor, e o ato não alcança o que ele mesmo acrescenta.
- **Documento Exigido para a Modalidade nova.** Um documento já publicado pode passar a pedi-la pela
  retificação do recorte dele, que já é retificável, **na Retificação seguinte**: as opções do recorte
  vêm do conteúdo vigente, e a Modalidade do mesmo ato ainda não está nele. Pela Modalidade, o recorte
  é por `modalityId`. Pelo código (`044`), só alcança código presente em todos os Perfis. Criar
  documento novo continua fora (ver *Inventário*).
- **Período de inscrições encerrado.** A Modalidade acrescentada só serve a inscrições novas. Esta
  feature não reabre o período: reabri-lo é retificar as datas do Evento, no mesmo ato ou em outro.
- **Rascunho de inscrição aberto.** O rascunho de quem já tinha uma Modalidade assumida, num Perfil que
  passa de uma para duas, **não envia em silêncio**: o envio é recusado até a pessoa reconhecer a
  versão nova, como em toda Retificação durante o preenchimento (`009`). A Modalidade assumida ficou
  gravada no rascunho, e continua sendo a escolha dele depois do reconhecimento — a pessoa pode
  trocá-la pela ampla, e nada a troca por ela. *Corrigido na implementação*: a primeira redação dizia
  que a escolha passaria a ser exigida, e o teste mostrou que a assumida fica gravada. Assumir sem
  perguntar é o achado A-1, e não desta feature. *Revisitado em 27/09*: com a `DP-14`, o Perfil com
  vaga na linha geral oferece a ampla sem Modalidade, e nada é assumido; o caso-limite continua valendo
  para o Perfil com tudo em cota, e é esse que o teste monta.
- **Janela que nasce depois da divulgação.** O prazo conta da divulgação do ato, pela regra que já
  existe. A spec não reabre prazo nem move a âncora, e uma janela que nasce já vencida não concede
  prazo a ato já divulgado.
- **Regra de corte que não governa Etapa.** Não há Etapa em que o corte excluiria alguém avaliado, e a
  guarda da `D-002` não se aplica.
- **Resultado registrado entre a conferência e a publicação.** A guarda do corte é conferida de novo na
  publicação da Retificação, e não só na confirmação.
- **Nada preenchido.** Abrir a Retificação e publicar sem tocar os campos de um objeto ausente não faz
  nascer objeto nenhum. O controle de *"admite recurso"* não pode nascer pré-marcado.
- **Modalidade acrescentada com regra normativa.** A regra nasce junto, inteira, com os campos que a
  composição oferece. Os parâmetros opacos nascem vazios, como na composição.

---

## Requirements *(mandatory)*

### A Modalidade acrescentada a um Perfil publicado

- **FR-777**: A Retificação de um Edital publicado MUST permitir acrescentar Modalidade de Concorrência
  a qualquer Perfil existente, com os campos que a composição oferece: código, denominação, descrição
  e, opcionalmente, fundamento, versão do fundamento e percentual.
- **FR-778**: A Modalidade acrescentada MUST atender às mesmas exigências da composição: código único no
  Perfil, denominação preenchida, versão quando há fundamento, percentual na faixa. A recusa MUST vir ao
  conferir, com a razão que a composição daria, e MUST valer de novo ao confirmar e ao publicar, por
  qualquer canal.
- **FR-779**: Quem acrescenta a Modalidade MUST poder, no mesmo ato, declará-la a ampla concorrência do
  Perfil, ou, sendo cota, dar a ela a sua linha do quadro de vagas. A ampla não tem linha própria: as
  vagas dela são as da linha geral, como a publicação já exige.
- **FR-780**: O conteúdo retificado MUST passar pela mesma validação de publicação que já confere quadro,
  documentos e regras dependentes. A Modalidade nova não tem isenção.
- **FR-781**: O acréscimo de Modalidade MUST NOT alterar inscrição já enviada, a Modalidade que ela
  declarou nem a lista exigida gravada, e MUST NOT tornar obsoleta, por si, ordem, relação de
  habilitados ou sorteio de outro recorte. Sendo cota, o recorte novo MUST nascer sem ordem. Alterar o
  quadro de vagas no mesmo ato continua tendo o efeito que já tem hoje sobre corte e apuração.
- **FR-782**: A frase da tela que declara que *"Modalidades de Concorrência ainda não são definidas por
  aqui"* MUST sair.

### O que nasce inteiro

- **FR-784**: Todo objeto que nasce por Retificação MUST nascer inteiro, num ato só, e MUST passar pela
  mesma validação que a publicação aplica a ele quando declarado na composição.
- **FR-785**: Um objeto ausente MUST NOT nascer quando quem retifica não preencheu nenhum campo dele.
  Nenhum controle da tela pode declarar valor por estar pré-selecionado.

### A janela recursal

- **FR-786**: A Retificação MUST oferecer, em marco publicado sem janela recursal, a declaração de que
  ele admite recurso e a duração em dias corridos.
- **FR-787**: A janela que nasce por Retificação MUST admitir recurso. Declarar *"não admite"* onde o
  Edital não declarava janela MUST ser recusado, com a razão (`D-003`).

### A regra de corte

- **FR-788**: A Retificação MUST oferecer, em marco publicado sem regra de corte, a regra inteira,
  inclusive os três campos que não se retificam depois de declarados: espécie do alvo, Etapa governada
  e continuação.
- **FR-789**: A Retificação que faz nascer a regra de corte governando uma Etapa que já tem Resultado
  registrado MUST ser recusada, na confirmação e de novo na publicação. A recusa nomeia o marco e a
  Etapa (`D-002`).
- **FR-790**: O caminho *"Retificar o Edital para declarar a regra de corte"* da tela do corte MUST levar
  a uma Retificação que oferece a regra daquele marco.

### A reversão

- **FR-791**: A Retificação MUST oferecer, em Perfil publicado sem reversão de vaga reservada, a escolha
  da espécie da reversão. O vazio continua significando que o Perfil não reverte.

### O critério de desempate

- **FR-792**: A Retificação MUST permitir acrescentar critério de desempate a um marco publicado, com o
  que o critério compara, o parâmetro, o que fazer quando o valor não existe e a ordem de aplicação.
- **FR-793**: O critério acrescentado MUST atender às exigências da composição: parâmetro que aponta
  Etapa classificatória do Edital ou fato declarado do Perfil, conforme o tipo; comportamento na ausência declarado; ordem única no
  marco, contados os critérios que continuam depois do ato. A recusa MUST vir ao conferir, e MUST valer
  de novo ao confirmar e ao publicar, por qualquer canal.
- **FR-794**: Acrescentar critério MUST tornar a ordem já emitida daquele marco obsoleta e recomputável,
  pela mesma regra que já vale para a remoção.

### O que vale para todos

- **FR-795**: Toda alteração desta feature MUST ser feita pela tela de Retificação que já existe, sem
  canal novo, e MUST produzir o mesmo ato, a mesma versão consolidada, o mesmo documento e o mesmo
  histórico que as demais alterações produzem.
- **FR-796**: A publicação anterior MUST continuar consultável, com o conteúdo que tinha, depois da
  Retificação que acrescenta.
- **FR-797**: As leituras que já usam o conteúdo vigente — inscrição, página pública da seleção,
  classificação por recorte, tela do corte, interposição de recurso — MUST passar a refletir o que
  nasceu ou foi acrescentado, a partir da vigência da versão nova.
- **FR-798**: O documento da Retificação MUST mostrar a Modalidade, a linha do quadro, a janela, a
  regra de corte, o critério e a reversão que o ato fez nascer.
- **FR-799**: Cada campo oferecido para nascer MUST ter o rótulo do vazio dizendo o que o vazio
  significa, como os campos do método do sorteio já fazem.
- **FR-800**: A conferência antes da confirmação MUST listar cada acréscimo e cada nascimento, com
  *antes* em branco e *depois* legível, e as advertências do ato sobre o conteúdo resultante.
- **FR-801**: Toda recusa desta feature MUST dizer o que foi recusado, por quê e o que fazer, na
  gramática das recusas da validação.
- **FR-802**: A feature MUST NOT criar mecanismo de acréscimo além dos dois que existem, nascimento de
  objeto e acréscimo de item a coleção, nem acréscimo genérico para coleção que esta spec não nomeia.
- **FR-803**: O contrato de mutabilidade MUST continuar sendo a única fonte da decisão do que se
  retifica e do que pode nascer. Oferecer campo não retificável no nascimento MUST ser decisão
  declarada, e não exceção silenciosa à guarda que confere a tela contra o contrato.

### Key Entities

- **Modalidade de Concorrência**: continua pertencendo ao Perfil. Ganha um caminho de acréscimo na
  Retificação, e nenhum campo novo.
- **Declarações que podem nascer**: janela recursal, regra de corte e reversão. Cada uma é um objeto do
  conteúdo publicado que pode estar ausente e passar a existir.
- **Critério de desempate**: item de coleção do marco. Ganha acréscimo na Retificação.
- **Retificação, Alteração Normativa e Versão Consolidada**: inalteradas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-288**: O percurso completo — publicar Perfil sem a ampla, retificar pela tela acrescentando-a,
  inscrever um não-cotista — fecha **sem** cancelar o Edital, sem API e sem banco.
- **SC-289**: Numa Retificação que acrescenta Modalidade, **0** inscrições enviadas mudam de Modalidade
  ou de lista exigida, e **0** ordens vigentes de outros recortes ficam obsoletas. Um teste de ponta a
  ponta prova isso retificando de fato, e não emitindo recorte à mão.
- **SC-290**: Os **4** objetos que o contrato declara que podem nascer (janela, corte, reversão e
  método) têm caminho pela tela. Hoje é **1** de 4.
- **SC-291**: O caminho da tela do corte para a Retificação leva a um formulário em que a regra daquele
  marco pode ser declarada em **100%** dos marcos sem regra.
- **SC-292**: **0** Retificações publicam conteúdo que a composição recusaria nos objetos e itens que
  esta feature acrescenta.
- **SC-294**: Uma Retificação que só altera um texto, num Edital com marcos sem janela e sem corte e
  Perfis sem reversão, emite **exatamente** a alteração do texto.

## Correlação com a auditoria de consolidação

Cada linha diz: a evidência original; o que o código faz hoje; se o achado permanece; o requisito que o
atende; onde a correção será demonstrada; e o que sobra, de propósito.

### RC-37 — A Retificação não acrescenta Modalidade (`D-G5`)

| | |
|---|---|
| **Evidência original** | `D-G5` ([reavaliação de 18–19/09](../../doc/reavaliacao-ux-2026-09-18.md)); REAV §13; convergência §20.3; `specs/034-ordem-por-recorte/achado-percurso-ampla-sem-inscricao.md`; US2 da `039`, não implementada |
| **Comportamento atual** | O domínio aceita `ADD` de Modalidade por API (`tests/integration/publicacoes/test_quadro_na_retificacao.py:119-152`). A tela não oferece o caminho e declara a ausência. A forma da Modalidade não é conferida no conteúdo publicado, e um objeto só com `id` e `code` publica (`test_enderecamento.py:610-633`) |
| **Situação** | **integral**, conferido em 26/09 |
| **Atendido por** | `FR-777` a `FR-782`; User Story 1; `D-001` |
| **Demonstração** | teste de ponta a ponta pela tela (`SC-288`, `SC-289`); teste da conferência com as recusas da composição (`SC-292`) |
| **Resíduo deliberado** | Modalidade num Perfil acrescentado no mesmo ato; Documento Exigido novo para ela; encerrar a `039` (`DP-08`, item 1) |

### RC-38 — O que "pode nascer" não tem porta

| | |
|---|---|
| **Evidência original** | `G16-001` (`doc/e2e/016-ocupacao-de-vagas/relatorio.md:148-161`); [achado do objeto que nasce só pelo método](../../doc/achado-objeto-que-nasce-so-pelo-metodo.md); NOVO-1 do lote 1; NOVO-3 do lote 5; AX-1 da [granularidade normativa](../../doc/auditoria-granularidade-normativa-2026-09-15.md) |
| **Comportamento atual** | A tela oferece só o método. Corte, janela e reversão aparecem só quando já existem; um teste prende a ausência da reversão. O critério se remove e não se acrescenta. A tela do corte manda para a Retificação e a Retificação não tem o campo |
| **Situação** | **integral**, conferido em 26/09. As linhas citadas pela auditoria envelheceram, e as atuais estão na tabela do início |
| **Atendido por** | `FR-784` a `FR-794`; User Stories 2 a 5; `D-002` a `D-004` |
| **Demonstração** | testes de interface por objeto; o de `test_retificar_reversao.py:84` passa a prender a presença; teste de ponta a ponta do caminho da tela do corte (`SC-291`); teste da janela *"não admite"* pela API; teste da Retificação só de texto (`SC-294`) |
| **Resíduo deliberado** | causa de obsolescência da apuração quando a reversão muda; janela lida da versão vigente para ato já divulgado. Os dois estão registrados abaixo |

### O que esta feature fecha na auditoria

Das três unidades de grupo A que a auditoria contou como trabalho novo — `RC-37`, `RC-38` e `RC-111` —,
esta feature fecha **duas**. Também:

- executa a `D-G5`, decidida em 19/09 e órfã duas vezes;
- responde ao item 2 da `DP-08`;
- desfaz o beco que a correção da `037` e o impeditivo da `046` deixaram na tela do corte.

**Não** fecha o `RC-111`, e o aumenta: cada nascimento desta feature é mais uma alteração que o *"O que
mudou"* público não descreve.

---

## Assumptions

### D-001 — A Modalidade nova nasce com a regra da composição

A `D-G5` decidiu que a Retificação acrescenta Modalidade, e a auditoria lê *"sem a ampla (ou sem uma
cota)"*. A spec segue a letra: qualquer Modalidade, com os campos que a composição oferece. O contrato
recusa que a regra normativa **nasça numa Modalidade já publicada**: *"acrescentá-lo depois é criar
reserva que o Edital publicado não tinha"*. Essa recusa continua. A Modalidade inteira nascendo com a
sua regra é outra coisa: é o que a `D-G5` autorizou, e cria a reserva de propósito.

**Decidido pelo usuário em 26/09, no parecer sobre o `/speckit-analyze`: qualquer Modalidade, inclusive
cota.** A auditoria define o problema como a ausência *"da ampla ou de uma cota"*, e limitar à ampla
deixaria parte do `RC-37` aberta.

### D-002 — A regra de corte nasce com guarda

Decidido pelo usuário em 26/09. A regra nasce inteira, e com ela os três campos que depois não se
trocam. Declarar não é alterar, e a razão desses campos é sobre mudar o que já foi aplicado. O
nascimento é recusado se a Etapa governada já tem Resultado: é a própria razão do contrato para
`cutRule/governedStage` (*"moveria, em silêncio, quem continua"*) aplicada ao nascimento. Regra nova,
e pequena.

### D-003 — A janela que nasce concede

Decidido pelo usuário em 26/09. A razão que o contrato dá para a janela nascer é *"conceder é menos
grave do que retirar"*. Uma janela que nasce com *"não admite"* retira: faz a interposição devolver
*"recurso não previsto"* onde antes havia silêncio, que era juízo humano de tempestividade. A restrição
sai da razão que já está escrita, e não de uma nova.

### D-004 — O critério de desempate entra

Decidido pelo usuário em 26/09. É o caso concreto de estrutura repetível que a proposta descreve: já
admite vários itens, já admite alteração e remoção, e não admite acréscimo. O efeito sobre a ordem
emitida é o mesmo da remoção de hoje.

### Outras premissas

- **A tela de Retificação é o canal.** Nenhuma API nova, nenhum comando.
- **A regra da classificação, do corte, da ocupação e do recurso não muda.** Esta feature as alimenta
  com conteúdo; não as afrouxa.
- **A `047` não é tocada.** Ela projeta o estado vigente, e o estado vigente passa a conter o que esta
  feature produz.

## Out of Scope

- Redesenhar a Retificação, metamodelo de campos, motor de versionamento, retificação aditiva genérica.
- Tornar retificável o que o contrato classifica como não retificável, derivado ou estrutural.
- Prévia em PDF da Retificação.
- O *"O que mudou"* público (`RC-111`) e a apresentação pública da Retificação (`047`).
- Documento Exigido, Fato, Marco, Etapa ou Seção novos por Retificação.
- Área do Candidato, consolidação, classificação e resultado.
- Alcance da Etapa (`RC-64`) e catálogo de Modalidades no Edital (`039`).
- Os achados abaixo.

## Achados registrados, fora do escopo

Registro, não escopo: governança é do usuário. Todos foram lidos no código e **não** percorridos.

- **A-1 · Perfil com uma cota só põe todo candidato nela** `[VALIDAR]`. Quando o Perfil declara
  exatamente uma Modalidade e ela é cota, a inscrição a assume sem perguntar
  (`inscricoes/application/rascunho.py:59`), e o não-cotista concorre como cotista e recebe a lista de
  documentos da cota. É o caso da `D-G5` com outra forma, e não está na auditoria. A correção da
  Retificação o conserta depois da publicação. Impedir que ele se publique é regra de composição.
  *Corrigido em 27/09 pela `DP-14`, opção A*: com vaga na linha geral, a inscrição oferece a ampla sem
  Modalidade ([decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md#dp-14--quando-a-inscrição-oferece-a-ampla-concorrência)).
- **A-2 · A reversão muda e a apuração não fica obsoleta.** Nenhuma causa de obsolescência compara a
  reversão (`ocupacao/application/selectors.py:80-163`), e uma apuração emitida sob a declaração
  anterior continua *"vigente"*. Vale já hoje para quem retifica a espécie, e esta feature só a amplia.
- **A-3 · A janela de ato já divulgado segue a versão vigente.** Já registrado pela `047`. Esta feature
  só concede, e por isso não piora o caso de encurtar.
- **A-4 · Os nascimentos são silenciosos no portal.** O *"O que mudou"* não descreve linha do quadro,
  declaração da ampla, janela, corte nem reversão. É o `RC-111`.
- **A-5 · A `039` continua sem encerramento registrado** (`DP-08`, item 1).
- **A-6 · Objeto inteiro troca campo não retificável pela API.** A gramática recusa o campo não
  retificável endereçado sozinho (`publicacoes/domain/changes.py`, `apply_change`), mas aceita o
  `REPLACE` do objeto que o contém: uma regra de corte existente pode ter a espécie do alvo, a Etapa
  governada e a continuação trocadas; um critério, o tipo; um Perfil, a espécie do cadastro reserva. É
  anterior a esta feature, e nenhum teste a exercita. A primeira redação desta spec a fechava com uma
  guarda genérica; o parecer de 26/09 a tirou do escopo. **Se for tratada, a guarda não pode morar em
  `apply_changes`**, que também reproduz atos já publicados (`research.md`, `R-1`).
