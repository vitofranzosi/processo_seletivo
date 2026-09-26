# Feature Specification: Contrato de executabilidade do Processo publicado

**Feature Branch**: `claude/spec-046-processo-executabilidade-31fa38`

**Created**: 2026-09-26

**Status**: Draft

**Input**: proposta do usuário de 26/09/2026, *"SPEC 046 — Contrato de executabilidade do Processo
publicado"*. Consolida a B-3 da [auditoria de consolidação](../../doc/auditoria-de-consolidacao-2026-09-26.md)
— `RC-29`, `RC-30` (`D-G1`), `RC-32` e `RC-72` — e responde à pergunta `DP-06` das
[decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md), cujo registro entra lá, no
bloco *"O que foi decidido"*.

> **Faixa de identificadores.** Abre em **FR-746** e **SC-275**. O teto medido em 26/09/2026 em todas
> as worktrees (`git worktree list`) e nas branches abertas é `FR-745` e `SC-274`, da `045`, já na
> `main` — sem negrito, porque não são requisitos desta spec. Nenhuma espécie `UX-` nova: as frases
> desta feature são recusas e avisos da validação, que já têm gramática (`032`, `FR-458`). As
> **decisões** reiniciam em `D-001`; decisão de outra spec é citada pelo requisito que a registra, e
> nunca pelo número local dela.

> **Teto proporcional.** Quatro achados, quatro histórias, e cada requisito tem de nomear o que a
> tela ou o ato fazem de diferente. O que não passar nisso é nota de tarefa.

---

## Por que esta feature existe

**A publicação deveria ser uma fronteira de confiança, e em quatro pontos não é.** Depois que uma
versão do Edital é publicada — ato imutável —, o sistema deveria poder assumir que o que ele próprio
se propõe a executar estava consistente naquele instante. A `032` fez essa varredura para o marco
classificatório e parou ali. A auditoria de 26/09 encontrou o resto, e a conferência contra o código
em `aeb575a` reproduziu os quatro:

| | O que acontece hoje | Reproduzido em 26/09 |
|---|---|---|
| `RC-29` | Etapa com duas avaliações por inscrição, ou eliminatória pontuada sem nota mínima, ou decisória não eliminatória **publica sem achado nenhum** — e a consolidação recusa a Etapa inteira depois | `validate_for_publication` não emite código algum para as três formas; `impedimento_da_regra` (`resultados/domain/regra.py:57`) recusa as três |
| `RC-30` | Perfil cujo único marco não declara regra de corte publica com **aviso**: classifica, e ninguém dele pode ser convocado | `milestone_without_cut_rule` sai como `WARNING` (`editais/domain/validation.py:1713-1756`) |
| `RC-32` | A tela do Edital **publicado** diz *"Impede — o período de inscrições encerrou… corrija… antes de publicar"*, e avisa que *"o Edital será publicado"* | `_pendencias` de um Edital `PUBLICADO` devolveu `erro · registration_period_closed` |
| `RC-72` | A **"Fonte de demonstração"** — semente fixa `12345 67890…` — é oferecida no seletor e aceita na publicação, em qualquer ambiente | publicação sem achado; `FONTES` sem condição de ambiente (`sorteios/infrastructure/fontes/__init__.py:83-92`) |

**O contrato, em uma frase.** A publicação não garante que o Processo dará certo. Garante algo mais
estreito e verificável: **naquele instante, o sistema não conhece impossibilidade estrutural que ele
próprio criou ou permitiu configurar**.

**E a distinção que impede o exagero.** Há duas espécies de condição, e só uma é desta feature:

| | O que é | Onde mora |
|---|---|---|
| **Invariante estrutural** | já na publicação se sabe que a configuração **nunca** executará, para candidato nenhum | o gate desta feature |
| **Condição operacional** | só se sabe quando existirem inscrições, avaliações, recursos ou resultados | continua no mecanismo que a consome |

### O que a verificação contra o código mudou na proposta

A proposta foi conferida contra a `main` em `aeb575a`. Seis fatos mudam o desenho, e nenhum muda a
direção. Os dois primeiros foram levados ao usuário e decididos em 26/09 (`D-001`, `D-002`).

1. **O Resultado de uma Etapa nem sempre é exigido.** O fluxo publicado só o consome em quatro
   lugares: o caráter eliminatório (a progressão exclui quem foi eliminado), a enumeração por marco
   (a combinação devolve `SEM_PONTUACAO` e a pessoa fica sem posição), a regra de corte que governa a
   Etapa (a convocação lê quem habilitou nela) e a Etapa de habilitação de um método de sorteio (a
   relação lê quem habilitou nela). Uma Etapa que não é nenhuma das quatro não trava nada se nunca
   consolidar. Impedir a publicação dela seria proibir o que um Edital pode legitimamente publicar — a
   recusa exata que a `013` registrou em 03/09 (`FR-047`). **O impeditivo é para a Etapa cujo Resultado
   o fluxo exige; a outra recebe aviso** (`D-001`).
2. **O Cenário C do briefing já está implementado.** Todo marco que **declara** regra de corte sem
   informação suficiente para determinar o limite já é recusado na publicação desde a `014`: espécie
   do alvo ausente, alvo fixo sem número, alvo derivado sem linha do quadro, desfecho de empate,
   política de continuação e Etapa governada (`_regra_de_corte_do_marco`, `_forma_do_alvo`,
   `_quadro_para_o_corte`, em `validation.py:808-1000`). O que sobra do `RC-30` é a **ausência** de
   regra — e ela é a opção *"Este marco não corta"* da tela (`_marco.html:513`), um estado legítimo com
   semântica definida: a Etapa seguinte recebe todos os habilitados (`014`, `FR-214`), a ocupação é
   apurável, e a convocação não alcança ninguém, porque só chama dentro de faixa.
3. **A premissa da `D-G1` não se sustenta no código.** A `D-G1` (19/09) disse que *"não governa
   Etapa alguma"* é a declaração explícita alternativa ao corte. Não é: essa declaração continua sendo
   **regra de corte**, com alvo, empate e continuação obrigatórios. Aplicada por marco, a `D-G1`
   obrigaria o marco que legitimamente não corta — o preliminar de um Perfil com dois marcos — a
   inventar um alvo. **A invariante passa a ser do Perfil**: pelo menos um marco dele declara corte
   (`D-002`).
4. **O `RC-32` tem duas superfícies, e não bloqueia operação nenhuma.** `_pendencias`
   (`interface/views.py:816`) é chamada pela tela do Edital (`:2791`) e pelo assistente de composição
   (`:1271`) em qualquer estado, com o ato de publicação e o relógio de agora. Ela alimenta só a
   **previsão** de recusa dos atos de submeter e publicar (`interface/acoes.py:181-198`), que não
   existem num Edital publicado. O dano é informação falsa, e não operação impedida: o briefing
   supunha o contrário. A correção mínima é uma: a validação de publicabilidade só se apresenta antes
   da publicação (`D-003`).
5. **A fonte de demonstração não precisa de guarda nova: precisa sair do vocabulário.** O
   vocabulário fechado de fontes (`021`, `FR-076`) já é a fonte única que a composição, a gravação,
   a publicação, a Retificação e a observação da ocorrência consultam. Tirá-la dele em produção fecha
   os cinco pontos de uma vez (`D-004`).
6. **A Retificação precisa ver o aviso, e hoje há um caminho para ele sumir.** A confirmação da
   Retificação subtrai os códigos que **impediriam a publicação** (`retificacoes.py:583-588`). Um
   código desta feature que fosse impeditivo na publicação e advertência na Retificação seria
   descartado ali, em silêncio — exatamente o cenário da issue #117, que a auditoria mandou tratar
   junto. **A feature evita o cenário em vez de corrigir a issue**: a Etapa ganha dois códigos, e a
   #117 continua aberta, sem que a `046` dependa dela (`D-005`).

---

## User Scenarios & Testing *(mandatory)*

> **Prioridade é valor, e não ordem de execução.** As histórias estão na ordem do valor que entregam.
> A implementação corre em outra ordem — `US3`, `US4`, `US2`, `US1` —, porque as duas primeiras são
> pequenas e não tocam fixture, e as duas últimas mudam fixture da suíte inteira; a razão está no
> [plano](plan.md), *Ordem de entrega*.

### User Story 1 - A Etapa que o fluxo não consegue concluir não atravessa a publicação (Priority: P1)

Quem publica é impedido de publicar Etapa cujo Resultado o próprio Edital exige e que a consolidação
já sabe que nunca produzirá, e lê qual Etapa, por quê e onde corrigir. A Etapa cujo Resultado nada
consome continua publicável, com aviso.

**Why this priority**: é o único dos quatro achados com trabalho humano desperdiçado. Com duas
avaliações por inscrição, a distribuição atribui, dois avaliadores leem e concluem, e só então a
consolidação recusa a Etapa inteira — sobre um ato que não se desfaz. A saída por Retificação
entrega a inscrição a outro impedimento, que descarta uma das leituras
([achado de 21/09](../../doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md)).

**Independent Test**: compor um Edital com uma Etapa eliminatória de duas avaliações por inscrição e
tentar submetê-lo; conferir a recusa e a mensagem; trocar para uma avaliação e conferir que publica.
Repetir com a mesma Etapa **não** eliminatória e fora de todo marco, e conferir que publica com aviso.

**Acceptance Scenarios**:

1. **Given** uma Etapa eliminatória com duas avaliações por inscrição, **When** alguém submete ou
   publica o Edital, **Then** o ato é recusado, e a recusa nomeia a Etapa, diz que o Edital não declara
   como combinar as avaliações, que por isso nenhuma inscrição terá Resultado nela, e que a correção é
   na etapa Etapas.
2. **Given** uma Etapa pontuada, eliminatória e sem nota mínima, **When** alguém submete o Edital,
   **Then** o ato é recusado pela mesma razão que a consolidação daria.
3. **Given** uma Etapa decisória **não** eliminatória enumerada num marco, **When** alguém submete o
   Edital, **Then** o ato é recusado; e **Given** a mesma Etapa fora de todo marco, de toda regra de
   corte e de todo método de sorteio, **When** alguém submete, **Then** o ato passa, com aviso de que
   a Etapa não terá Resultado.
4. **Given** uma Etapa com uma avaliação, eliminatória e com nota mínima — ou decisória e eliminatória
   —, **When** alguém submete, **Then** nenhum achado desta família aparece (Cenário B).
5. **Given** a Revisão de um Edital em elaboração com uma Etapa assim, **When** quem compõe a abre,
   **Then** a pendência aparece na etapa Etapas, com a mesma frase da recusa.
6. **Given** um Edital publicado com uma Etapa impedida de consolidar, **When** alguém confirma uma
   Retificação qualquer dele, **Then** a confirmação mostra a advertência — e a Retificação não é
   recusada por ela.

---

### User Story 2 - Um Perfil que não convoca ninguém não é publicado como completo (Priority: P2)

Quem publica é impedido de publicar Perfil em que nenhum marco declara regra de corte. O marco que não
corta, num Perfil em que outro marco corta, continua publicável.

**Why this priority**: é decisão tomada desde 19/09 (`D-G1`) e não executada. O defeito é de
consequência tardia — o Perfil classifica, publica a ordem, e só na convocação se descobre que
ninguém pode ser chamado —, e a correção é pequena.

**Independent Test**: compor um Perfil com um único marco em *"Este marco não corta"* e tentar
submeter; conferir a recusa. Acrescentar um segundo marco com regra de corte e conferir que publica,
com o aviso da `032` sobre o primeiro.

**Acceptance Scenarios**:

1. **Given** um Perfil cujo único marco não declara regra de corte, **When** alguém submete o Edital,
   **Then** o ato é recusado, e a recusa nomeia o Perfil, diz que nenhum marco dele corta, que sem
   corte não há faixa e a convocação não alcança ninguém, e que a correção é na etapa Classificação.
2. **Given** um Perfil com dois marcos, o preliminar sem regra de corte e o final com ela, **When**
   alguém submete, **Then** o ato passa, e o marco preliminar recebe o aviso que a `032` já emite
   (`FR-461`) — Cenário D.
3. **Given** um Perfil cujo único marco declara regra de corte que não governa Etapa alguma, **When**
   alguém submete, **Then** nenhum achado desta família aparece.
4. **Given** um marco que declara regra de corte sem alvo, sem linha do quadro, sem desfecho de empate,
   sem política de continuação ou sem Etapa governada, **When** alguém submete, **Then** a recusa é a
   que já existe desde a `014`, e nenhuma nova se soma a ela (Cenário C).
5. **Given** um Edital do acervo publicado com Perfil sem corte, **When** alguém o retifica, **Then** a
   Retificação é aceita como hoje (`032`, `FR-460`).

---

### User Story 3 - O Edital publicado não é julgado como se ainda fosse publicar (Priority: P3)

Quem abre um Edital publicado, encerrado ou cancelado não lê pendência de publicação nenhuma — nem
*"Impede"*, nem *"o Edital será publicado"*. Antes da publicação, nada muda.

**Why this priority**: é informação falsa em ato imutável, e ela instrui a pessoa a *"corrigir antes
de publicar"* o que já foi publicado. Não impede operação (verificado), e por isso vem depois das
duas primeiras.

**Independent Test**: publicar um Edital com período de inscrições designado, avançar o relógio para
depois do término e abrir a tela do Edital e a Revisão do assistente; conferir que nenhuma pendência
aparece. Refazer com o mesmo conteúdo em elaboração e conferir que o impeditivo aparece.

**Acceptance Scenarios**:

1. **Given** um Edital publicado cujo período de inscrições já encerrou, **When** qualquer pessoa abre
   a tela dele, **Then** não há seção *"Validação do conteúdo"*, nem marcador *"Impede"*.
2. **Given** o mesmo Edital, **When** alguém abre qualquer etapa do assistente em modo de leitura,
   **Then** nenhuma pendência de publicação aparece.
3. **Given** um Edital em elaboração, em revisão ou homologado com o mesmo conteúdo, **When** alguém
   abre a tela ou o assistente, **Then** o impeditivo aparece exatamente como hoje.
4. **Given** um Edital publicado, **When** alguém inicia uma Retificação dele, **Then** a confirmação
   continua mostrando as advertências do ato de Retificação, sobre o conteúdo vigente (`027`,
   `FR-336`).

---

### User Story 4 - A semente de demonstração não chega a um Processo real (Priority: P4)

Em produção, a *"Fonte de demonstração"* não existe: não é oferecida, não é aceita, não é publicada e
não é executada. Em desenvolvimento e nos testes, continua existindo.

**Why this priority**: é o único furo de auditabilidade da auditoria — um sorteio publicado com
semente previsível —, mas não há evidência de que tenha sido usado, e a instituição ainda não opera
sorteio pelo sistema. A correção é de uma linha de vocabulário, e é a última porque é a que menos
depende das outras.

**Independent Test**: carregar a configuração de produção e conferir que o seletor de fonte do método
de sorteio oferece só a Loteria Federal, e que um Edital que declara a fonte de demonstração é
recusado na gravação e na publicação; carregar a de desenvolvimento e conferir que `seed_demo` e o
sorteio da suíte continuam rodando sem rede.

**Acceptance Scenarios**:

1. **Given** o ambiente de produção, **When** quem compõe abre o método de sorteio de um marco,
   **Then** a fonte de demonstração não está entre as opções.
2. **Given** o ambiente de produção e um conteúdo que declara a fonte de demonstração — por API, por
   reaproveitamento de Edital ou por Retificação —, **When** alguém grava, submete, publica ou retifica,
   **Then** o ato é recusado, e a recusa diz que aquela fonte não é publicada por este sistema e quais
   são.
3. **Given** o ambiente de produção configurado para incluí-la, **When** a aplicação inicia, **Then**
   ela se recusa a subir e nomeia a configuração, como já faz com os seletores de identidade.
4. **Given** o ambiente de desenvolvimento ou de teste, **When** `seed_demo` roda ou a suíte sorteia,
   **Then** a fonte de demonstração continua disponível e executa sem rede.

---

### Edge Cases

- **Etapa impedida de consolidar e referenciada só por marco de sorteio em `stages`.** O marco de
  sorteio enumera Etapa para satisfazer a validação e não a consome (`classificacao/domain/faixa.py:93-97`).
  A regra de `D-001` conta **toda** enumeração por marco, e erra pelo lado que recusa: distinguir o
  marco de sorteio seria reescrever aqui a leitura da ordem. A correção é retirar a Etapa do marco ou
  dar-lhe regra — as duas estão ao alcance de quem compõe.
- **Etapa impedida de consolidar que só precede outra Etapa.** A progressão exige habilitação na Etapa
  anterior **só depois** que ela produziu algum Resultado (`resultados/application/prontidao.py:150-154`);
  sem Resultado, a seguinte recebe todos. A precedência não entra em `D-001`, e o risco que resta é
  operacional — ver *Achados registrados*, `A-1`.
- **Retificação que introduz o defeito.** Retificar *"Avaliações por inscrição"* de 1 para 2 produz uma
  Etapa impedida num Edital publicado. A Retificação recebe a advertência (`FR-751`) e não é recusada:
  distinguir o que a Retificação introduziu do que o acervo já tinha seria uma máquina nova, e
  coagir o acervo não é o mecanismo (`027`). É resíduo deliberado.
- **Mais de um Perfil, e só um sem corte.** O impeditivo é por Perfil e nomeia o Perfil; os outros
  publicam.
- **Perfil sem marco algum.** Já recusado pela `032` (`FR-457`); o impeditivo do corte não se empilha
  sobre ele.
- **Edital `ENCERRADO` ou `CANCELADO`.** Mesma regra do publicado: saiu da elaboração, não tem
  pendência de publicação.
- **Edital em produção que já declare a fonte de demonstração.** A execução do sorteio passa a
  recusá-lo, e toda Retificação dele é recusada até trocar a fonte. Não se sabe se existe algum: só a
  base de produção responde — ver *Impacto sobre Editais já publicados*.
- **Edital reaproveitado cujo original declarava a fonte de demonstração.** O conteúdo copiado é
  recusado na gravação em produção, como qualquer outro.

## Requirements *(mandatory)*

### A Etapa que o fluxo exige e que não se consolida

- **FR-746**: O sistema MUST recusar, como impeditivo do **ato de publicação**, Etapa que a regra da
  consolidação já recusa por inteiro — mais de uma avaliação por inscrição sem regra de combinação;
  pontuada, eliminatória e sem nota mínima; decisória e não eliminatória — **quando o fluxo publicado
  exige o Resultado dela**. O fluxo exige o Resultado da Etapa que é eliminatória, ou que é
  referenciada por algum marco do Edital: enumerada no marco, governada por regra de corte, ou
  designada Etapa de habilitação de método de sorteio, próprio do marco ou comum ao Edital (`D-001`).
- **FR-747**: A razão da recusa MUST sair da **mesma** regra que a consolidação aplica, e a publicação
  MUST NOT reescrever nenhum dos três predicados. Uma Etapa MUST ser acusada na publicação se, e
  somente se, a consolidação a recusaria.
- **FR-748**: Etapa que a consolidação recusa e cujo Resultado o fluxo publicado **não** exige MUST
  receber **aviso**, e não impeditivo, dizendo que ela não terá Resultado e por quê.
- **FR-749**: A recusa e o aviso MUST nomear a Etapa pelo nome publicado, dizer o que falta (a frase
  da regra da consolidação), por que isso impede a execução (quem precisa do Resultado: o caráter
  eliminatório, ou o marco que a referencia, por código) e em que etapa do assistente a correção é
  feita — Etapas, ou Classificação quando a correção é retirar a referência (`032`, `FR-458`).
- **FR-750**: O `como-preencher` da etapa Etapas MUST dizer que mais de uma avaliação por inscrição
  exige regra de combinação que o sistema não publica, e que a Etapa assim configurada não se
  consolida. O cartão da Etapa MUST NOT ganhar texto visível novo.
- **FR-751**: No ato de Retificação, esta família MUST ser **advertência** para toda Etapa que a
  consolidação recusa, e nunca impeditiva (`032`, `FR-460`). A advertência MUST chegar à confirmação da
  Retificação: nenhuma advertência desta família pode ser descartada pela subtração dos códigos que
  impediriam a publicação (issue #117, `D-005`).

### O Perfil que não convoca ninguém

- **FR-752**: O sistema MUST recusar, como impeditivo do **ato de publicação**, Perfil em que nenhum
  marco declara regra de corte. A recusa MUST nomear o Perfil, dizer que nenhum marco dele corta, que
  sem corte não há faixa e a convocação não alcança ninguém, e que a correção é na etapa Classificação
  (`D-002`). Regra de corte que declara não governar Etapa alguma conta como corte declarado.
- **FR-753**: Marco sem regra de corte num Perfil em que outro marco a declara MUST continuar
  publicável, com o aviso da `032` (`FR-461`). No Perfil recusado por `FR-752`, os avisos por marco
  MUST NOT se somar à recusa: é uma causa, e ela tem um relato.
- **FR-754**: O impeditivo de `FR-752` MUST NOT alcançar o ato de Retificação (`032`, `FR-460`).
  *Substitui a `D-G1` de 19/09 naquilo em que ela manda impedir o marco sem corte: a invariante é do
  Perfil, e não de cada marco.*

### O Edital publicado não passa pela validação de publicabilidade

- **FR-755**: Os achados da validação de publicabilidade MUST ser apresentados somente enquanto o
  Edital está antes da publicação — em elaboração, em revisão ou homologado. Em Edital publicado,
  encerrado ou cancelado, nenhuma superfície — a tela do Edital, o assistente em modo de leitura, a
  previsão de recusa dos atos — MUST apresentar achado dela (`D-003`).
- **FR-756**: A validação de publicabilidade MUST ser consultada somente pelos atos que conferem
  conteúdo normativo — submissão, publicação e Retificação, esta com o próprio ato — e pelas
  superfícies que os antecipam antes da publicação. Nenhuma operação sobre Processo publicado MUST
  depender dela.

### A fonte de demonstração fora de produção

- **FR-757**: Em produção, a fonte de demonstração MUST NOT pertencer ao vocabulário de fontes do
  sorteio. Por consequência, e sem verificação própria em cada ponto: ela MUST NOT ser oferecida na
  composição, nem aceita na gravação, na publicação ou na Retificação, nem executada na observação da
  ocorrência (`D-004`).
- **FR-758**: A aplicação MUST recusar-se a iniciar em produção com qualquer configuração que
  reinclua a fonte de demonstração, nomeando a configuração a corrigir — a mesma barreira dos
  seletores de identidade (`003`, `FR-016`).
- **FR-759**: Em desenvolvimento e nos testes, a fonte de demonstração MUST continuar declarável e
  executável sem rede, pelo mesmo nome, para `seed_demo`, para o roteiro do `quickstart` e para a
  suíte.

## Success Criteria *(mandatory)*

- **SC-275**: Percorrida a tabela-verdade inteira da regra da consolidação — as três razões, e cada
  uma nas cinco situações de exigência (eliminatória; enumerada; governada por corte; Etapa de
  habilitação de sorteio; nenhuma das quatro) —, a publicação recusa **exatamente** os casos em que a
  consolidação recusa e o Resultado é exigido, e avisa **exatamente** os demais: **zero** divergências
  entre as duas.
- **SC-276**: Os Editais executáveis que a suíte já publica — as três famílias da amostra real, o
  sorteio do 77/2026 e o corte sem Etapa governada do 69/2026 — continuam publicando com **zero**
  achados novos desta feature (Cenário B).
- **SC-277**: Percorrido pela interface, um Perfil de marco único sem corte é recusado na submissão;
  o mesmo Perfil com um segundo marco que corta é publicado, e o marco sem corte recebe **um** aviso,
  e não dois.
- **SC-278**: Num Edital publicado com o período de inscrições encerrado, a tela do Edital e as nove
  etapas do assistente exibem **zero** pendências de publicação; o mesmo conteúdo em elaboração exibe
  o impeditivo nas duas superfícies.
- **SC-279**: Com a configuração de produção carregada, a fonte de demonstração aparece em **zero**
  opções e é recusada nos quatro atos (gravação, submissão, publicação, Retificação) e na observação
  da ocorrência; a configuração de produção que a reinclui não sobe; e a suíte, em desenvolvimento,
  continua sorteando com ela.
- **SC-280**: **100%** das recusas e dos avisos novos nomeiam a entidade, o que falta, por que isso
  impede a execução e a etapa do assistente em que se corrige — conferido um a um.
- **SC-281**: **Zero** migrations de dado, e **zero** linhas de conteúdo publicado alteradas: nenhum
  Edital do acervo muda de estado nem de conteúdo por causa desta feature.

---

## Correlação com a auditoria de consolidação

Cada linha diz: a evidência original; o que o código faz hoje; se o achado permanece; o requisito que
o atende; onde a correção será demonstrada; e o que sobra, de propósito.

### RC-29 — Etapa publicável e não consolidável

| | |
|---|---|
| **Evidência original** | [achado de 21/09](../../doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md), LONG-1, NOVO-1 do lote 7; `validation.py:234` (`minimo=1`); `regra.py:57-95`; `tests/integration/resultados/test_prontidao.py:67` |
| **Comportamento atual** | `evaluationsPerRegistration` só é conferido na faixa (`validation.py:241`). As três formas publicam sem achado; a consolidação recusa a Etapa inteira (`regra.py:57`, `prontidao.py:504`), e a tela da Mesa o diz (`distribuicao.html:71-73`) — depois da publicação |
| **Situação** | **integral**, reproduzido em 26/09 |
| **Atendido por** | `FR-746` a `FR-751`; User Story 1; `D-001`, `D-005` |
| **Demonstração** | teste unitário da validação percorrendo a tabela-verdade da regra (`SC-275`); teste de interface da recusa na submissão e do aviso na Revisão; teste da confirmação da Retificação com a advertência presente |
| **Resíduo deliberado** | a regra de combinação de avaliações — spec própria, só com Edital real de dupla leitura (`DP-06`, opção C); a Retificação que introduz o defeito recebe advertência, e não recusa; o risco da Ocorrência (`A-1`) |

### RC-30 / D-G1 — Marco classificatório sem corte

| | |
|---|---|
| **Evidência original** | `D-G1` ([reavaliação de 18–19/09](../../doc/reavaliacao-ux-2026-09-18.md), §14-bis); issue #117; `validation.py:1735` (`WARNING`); `test_hardening_pos_auditoria.py:1100` prende o aviso |
| **Comportamento atual** | Regra de corte **declarada** e insuficiente já é impeditiva desde a `014` (`validation.py:808-1000`). A **ausência** de regra — *"Este marco não corta"* — sai como aviso, e a convocação não alcança ninguém daquele marco (`convocacao/application/selectors.py:119-137`: sem corte, `habilitadas` é vazio) |
| **Situação** | **parcial**: o limite insuficiente já está resolvido; o Perfil que não convoca ninguém continua publicando |
| **Atendido por** | `FR-752` a `FR-754`; User Story 2; `D-002` |
| **Demonstração** | teste unitário do impeditivo por Perfil e da ausência dele com um segundo marco que corta; o teste de `test_hardening_pos_auditoria.py:1100` passa a prender o novo par (aviso por marco + impeditivo por Perfil); regressão das recusas de `test_regra_de_corte.py` |
| **Resíduo deliberado** | a letra da `D-G1` por marco (substituída); a Retificação do acervo sem corte continua aceita; a convocação sob corte que não governa Etapa (`A-2`) |

### RC-32 — Revalidação do Edital publicado

| | |
|---|---|
| **Evidência original** | ACH-29, NOVO-1 do lote 2; `interface/views.py:2787` → `_pendencias` → `validate_for_publication(…, ato=ATO_DE_PUBLICACAO, agora=agora)`; `detalhe.html:168-180`; marcado `[VALIDAR]` |
| **Comportamento atual** | Duas superfícies, não uma: `detalhe` (`views.py:2791`) e `compor_etapa` (`:1271`) chamam `_pendencias` em qualquer estado, sobre o relacional — que num Edital retificado guarda o estado do dia da publicação. Os atos não usam essas pendências depois da publicação (`acoes.py:181-198`) |
| **Situação** | **integral**, reproduzido em 26/09: Edital `PUBLICADO` com `erro · registration_period_closed` e `aviso · schedule_event_in_past` (*"o Edital será publicado"*) |
| **Atendido por** | `FR-755`, `FR-756`; User Story 3; `D-003` |
| **Demonstração** | teste de interface das duas superfícies em Edital publicado com relógio depois do término, e da mesma tela em elaboração; varredura que prende quem chama a validação (`FR-756`) |
| **Resíduo deliberado** | validar o conteúdo **vigente** com o ato da Retificação na tela do Edital — descartado (`D-003`) |

### RC-72 — Fonte demonstrativa impossível em produção

| | |
|---|---|
| **Evidência original** | `D-G3`, NOVO-1 do lote 4; `fontes/__init__.py:88-92`; `interface/forms.py:318-322`; `config/settings/production.py` sem guarda |
| **Comportamento atual** | O elemento é a entrada `"Fonte de demonstração"` do dicionário `FONTES`, que aponta para `FonteDeTeste` (`sorteios/infrastructure/fontes/loteria_federal.py:142`). O dicionário é lido pelo seletor (`forms.py:318-322`), pela validação do método (`editais/domain/perfis.py:534-539`), e pela execução (`fonte_declarada`, chamada em `sorteios/application/ocorrencia.py:68`) — em qualquer ambiente |
| **Situação** | **integral**, reproduzido em 26/09 |
| **Atendido por** | `FR-757` a `FR-759`; User Story 4; `D-004` |
| **Demonstração** | teste de configuração de produção (`tests/test_configuracao_producao.py`) e teste do vocabulário sob a configuração de produção; a suíte de sorteio, inalterada, prova `FR-759` |
| **Resíduo deliberado** | a verificação na base de produção de Editais que já a declarem (ver abaixo) |

---

## O que o gate verifica, e o que continua downstream

| Invariante | Na publicação (esta feature) | Continua no mecanismo |
|---|---|---|
| Etapa com Resultado exigido e regra inconsolidável | **impeditivo** (`FR-746`) | a consolidação continua recusando, como hoje |
| Etapa com regra inconsolidável e Resultado não exigido | **aviso** (`FR-748`) | a consolidação continua recusando |
| Perfil sem marco que corte | **impeditivo** (`FR-752`) | — |
| Regra de corte declarada e insuficiente | já impeditivo (`014`) | — |
| Fonte do sorteio que o ambiente não fornece | fora do vocabulário (`FR-757`) | a observação recusa pelo mesmo vocabulário |
| Duas conclusões onde se prevê uma (após Retificação) | — | consolidação (`prontidao.py:589`) |
| Avaliador suficiente, cobertura, prazo, quórum | — | distribuição e Mesa |
| Vaga faltante, faixa esgotada, habilitação na Etapa governada | — | ocupação e convocação |
| Fonte indisponível no dia do sorteio | — | a regra de substituição publicada |

## Impacto sobre Editais já publicados

- **Nenhum Edital publicado muda de estado nem de conteúdo.** Os impeditivos novos valem só no ato
  de publicação; a Retificação recebe advertência (`FR-751`) ou nada (`FR-754`).
- **O `RC-32` só remove texto falso** das telas do Edital publicado.
- **A fonte de demonstração é o único impacto possível, e ele não é medível daqui.** Se a base de
  produção tiver Edital publicado que a declare, depois desta feature o sorteio dele é recusado e toda
  Retificação dele exige trocar a fonte. É o resultado certo — hoje esse sorteio sairia com semente
  fixa —, mas precisa ser sabido **antes** da implantação: uma consulta na base de produção pelo valor
  `"Fonte de demonstração"` no método de sorteio do conteúdo publicado. A auditoria já fazia a mesma
  pergunta (*"há algum controle fora do repositório…?"*).
- **Nenhuma migration.** Nada nesta feature é estado persistido.

---

## Assumptions

### D-001 — O Resultado é exigido quando o fluxo publicado o consome

Decidido pelo usuário em 26/09/2026, ao escolher *"Impede só se exigido"*. Responde à `DP-06` com
resposta diferente da recomendada ali (aviso para as três formas) e diferente da literal do briefing
(impedir sempre).

**Por que não impedir sempre.** A `013` recusou, em 03/09, *"exigir caráter eliminatório de toda
Etapa decisória, proibindo na elaboração o que um Edital poderia legitimamente publicar"* — a razão que a `FR-047` de lá registra e que o comentário de `impedimento_da_regra` repete.
Impedir toda Etapa decisória não eliminatória seria exatamente isso. E é desnecessário: o código mostra
que uma Etapa cujo Resultado nada consome não trava coisa alguma se nunca consolidar.

**Por que não só avisar.** Uma Etapa eliminatória que nunca consolida não elimina ninguém — a
progressão só exclui quem tem Resultado `ELIMINADA` —, e o Edital passaria a ser executado sem o
critério que publicou. Uma Etapa enumerada que nunca consolida deixa o Perfil sem ninguém posicionado.
Os dois são impossibilidade conhecida no instante da publicação, e aviso não impede ato imutável.

**Os quatro consumidores** são os que o código tem, e nenhum outro: a exclusão por eliminação
(`prontidao.py:147`), a combinação do marco (`classificacao/domain/combinacao.py:115-125`), a
habilitação na Etapa governada (`convocacao/application/selectors.py:119-121`) e a Etapa de habilitação
do sorteio (`sorteios/application/habilitacao.py:14-28`).

### D-002 — A invariante do corte é do Perfil, e não do marco

Decidido pelo usuário em 26/09/2026, ao escolher *"Invariante do Perfil"*. Substitui a `D-G1` de
19/09 naquilo em que ela manda impedir o marco sem corte.

A `D-G1` partia de que *"não governa Etapa alguma"* seria a declaração explícita de quem não corta.
Não é: é uma regra de corte, com alvo. O marco que legitimamente não corta — o preliminar, num Perfil
que corta no final — não tem outra forma de existir senão a ausência, e a tela a oferece por extenso.
O que o sistema sabe na publicação é outra coisa: se **nenhum** marco do Perfil corta, ninguém dele
será convocado. É isso que se impede.

### D-003 — Edital publicado não passa pela validação de publicabilidade

A auditoria abria duas saídas: validar a versão **vigente** com o ato da Retificação, ou não validar
o publicado. Fica a segunda. A primeira repetiria na tela do Edital o que a confirmação da Retificação
já faz no momento em que importa (`027`, `FR-336`), e daria à tela do Edital publicado uma lista de
advertências que ninguém pode resolver ali. A correção é um ponto só: a montagem das pendências, que
as duas superfícies compartilham.

### D-004 — A fonte de demonstração sai do vocabulário de produção

A auditoria sugeria *"a mesma barreira de produção dos seletores de identidade"*. A barreira entra
(`FR-758`), mas ela sozinha não bastaria: o que decide o que a composição oferece, o que a validação
aceita e o que a execução roda é o vocabulário de fontes, e ele é um só desde a `021` (`FR-076` de lá).
Tirar a fonte dele em produção fecha os cinco pontos sem verificação nova em nenhum. A escolha do
adaptador continua sendo pelo nome publicado, e não pelo ambiente — o que a `021` exigiu: o ambiente
decide apenas se aquele nome existe.

### D-005 — A advertência da Retificação não pode sumir na subtração

A confirmação da Retificação mostra as advertências do ato e subtrai os códigos que impediriam a
publicação. `FR-746` e `FR-751` criam, pela primeira vez, uma verificação que é impeditiva num ato e
advertência no outro sobre a **mesma** Etapa. Com um código só nas duas severidades, a advertência de
`FR-751` seria descartada em silêncio — o defeito que a issue #117 descreveu em abstrato e que esta
feature tornaria concreto.

**A forma escolhida é não criar o cenário**: um código impeditivo, só na publicação, e outro de aviso
e advertência, que nunca está no conjunto subtraído (`research.md`, `R-3`). É também o que o invariante
de `test_invariantes_da_declaracao_unica.py` já exige — num mesmo ato, aviso e impeditivo não
compartilham código. **A #117 fica aberta**: corrigir a chave da subtração continua certo para o dia
em que um código precisar das duas severidades, e esta feature não precisa. O requisito é o efeito
observável — a advertência chega à confirmação —, e ele vale sem a correção.

### Outras premissas

- **A instituição ainda não opera sorteio em produção pelo sistema.** Se operar, o impacto descrito
  acima deixa de ser hipotético e a consulta vira pré-requisito da implantação.
- **A regra da consolidação não muda.** Esta feature a consulta; não a afrouxa nem a amplia.
- **A `045` não é tocada.** Ela trata da condução do Processo vivo; esta, do que atravessa a
  publicação. A única superfície comum é a tela do Edital, e a `045` não altera a seção de pendências.

## Out of Scope

- Regra de combinação de avaliações de uma mesma Etapa.
- Nova estratégia de Resultado, engine de regras, simulador de Processo ou lint genérico de Edital.
- A relação entre avisos de composição e a Atenção da `038` (`RC-34`).
- Redesign da página pública, da área do candidato ou do documento publicado; notificações; painel.
- Mecanismo do sorteio, requerimento e exportação de matrícula.
- Os achados abaixo.

## Achados registrados, fora do escopo

Registro, não escopo (governança é do usuário). Os dois foram lidos no código e **não** percorridos.

- **A-1 · A Ocorrência abre o portão de uma Etapa que nunca consolida** `[VALIDAR]`. A Ocorrência
  (ausência) é aceita em Etapa impedida de consolidar, por desenho (`resultados/application/ocorrencia.py:14-20`),
  e produz `ELIMINADA`. Um único Resultado basta para ativar a exigência de habilitação na Etapa
  seguinte (`prontidao.py:150-154`), e todos os que não têm Resultado ali ficam *aguardando a anterior*
  para sempre. É condição operacional — depende de alguém registrar uma ausência —, e por isso não
  entra no gate.
- **A-2 · Corte que não governa Etapa pode não convocar ninguém** `[VALIDAR]`. A convocação lê a
  habilitação na Etapa governada pelo corte vigente (`convocacao/application/selectors.py:119-121`), e
  `habilitadas_na_etapa` devolve conjunto vazio quando não há Etapa (`ocupacao/application/selectors.py:381-388`).
  Lido assim, o 69/2026 — *"sorteia, publica, convoca e manda comparecer"*, segundo a `032` — não
  convocaria ninguém. Nenhum teste de convocação exercita corte sem Etapa governada. Se confirmado,
  `FR-752` continua certo (o Perfil sem corte nunca convoca), mas deixa de ser suficiente.
