# Feature Specification: O efeito do desfecho da Etapa por lista

**Feature Branch**: `claude/164-efeito-do-desfecho-por-lista`, sobre a `main` em `37ed0ad0`

**Created**: 2026-11-14

**Status**: Draft. Só a spec, sem plano nem código. Uma pergunta ao usuário (Q-1) continua aberta, e o
requisito que depende dela está escrito com a recomendação e diz que depende dela.

**Input**: a decisão **P-2** do usuário em 13/11/2026, no estudo da verificação da autodeclaração
(`doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, PR #541, regra R-2):

> *O Edital declara o efeito do desfecho desfavorável, com "sai da reserva e fica na ampla" como
> padrão. "Elimina" continua possível.*

É a segunda entrega da camada A desse estudo. A primeira é a `163`, o alcance da Etapa por
Modalidade, no PR #542, **ainda sem merge**. Esta spec parte do alcance que a `163` cria e não o
redefine. A nota de 13/11 na DP-10 (`doc/decisoes-pendentes-da-consolidacao.md`) registra a família
"heteroidentificação" como decidida.

> **Faixa de identificadores.** Esta spec abre em **FR-7000**, **SC-2330** e **UX-740**. Os tetos
> medidos em 14/11/2026 eram, na `main`, o requisito seis mil novecentos e cinquenta e um, o critério
> dois mil trezentos e quatro e o requisito de experiência setecentos e vinte e sete. A `163`, no PR
> #542, vai até o requisito seis mil novecentos e oitenta e sete e reservou até o seis mil novecentos e
> noventa e nove. A pasta `164` estava livre na `main`, nos dois PRs abertos (#541 e #542) e nas
> worktrees locais. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-047 da `013`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> **A `163` é citada só pelo assunto**, porque não está na `main`: um identificador dela citado aqui
> seria, até o merge do #542, uma citação para o nada.

---

## Por que esta feature existe

Hoje o desfecho desfavorável de uma Etapa eliminatória produz `ELIMINADA`, e `ELIMINADA` tira a
inscrição **de todas as listas**:

- ela não participa de nenhuma Etapa seguinte (a progressão da `013`);
- ela fica sem posição na ordem de **cada** recorte do marco, a ampla inclusive (a `094` monta um
  universo só para todos os recortes);
- ela não ocupa vaga nem é convocada por lista nenhuma.

A heteroidentificação dos Editais do Ifes não diz isso. Ela tira o candidato **da reserva**, e o deixa
concorrer pela ampla:

- Edital 28/2026, 6.9.15: o candidato *indeferido pela ausência das características fenotípicas será
  mantido como deferido na lista de Ampla Concorrência*;
- Edital 57/2026, 8.10: o candidato que não comparecer ou cuja autodeclaração for indeferida *será
  desclassificado da lista de pretos, pardos e indígenas, permanecendo apenas na lista de ampla
  concorrência*;
- a Lei 15.142/2025 e a IN Conjunta 261/2025, para concursos, também mantêm o não confirmado na ampla
  e reservam a eliminação à fraude.

E há Edital que elimina: o próprio 57/2026, no 8.11, diz que o não comparecimento implica *a
consequente eliminação do Processo Seletivo*, e a Res. CS 61/2019, art. 16, elimina por falsidade.

Composta hoje no GPS, mesmo com o alcance da `163`, a heteroidentificação eliminaria o candidato da
ampla também. A `163` registrou isso como risco e deixou a correção para esta spec.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- como o Edital declara o efeito do desfecho desfavorável numa Etapa de alcance restrito;
- o que acontece com a inscrição em cada lista: a reservada da Modalidade declarada e a ampla;
- a Retificação desse efeito;
- o que o documento do Edital diz;
- o que o candidato vê no acompanhamento.

**Fica fora:**

- as **regras de deliberação** dos pareceres (R-4 do estudo, decisão P-3): spec própria;
- o **vídeo** (camada B), bloqueado por norma (P-0);
- a **análise documental de indígenas**, que é Documento Exigido e conferência, e não Etapa;
- a **visibilidade e a recorribilidade** da Etapa que nenhum marco enumera (R-8 do estudo);
- o **efeito por motivo**, e não por Etapa (ver *Edge Cases* e *Achados*);
- a **migração para outra lista reservada** (D-006);
- o **indeferimento na convocação** com alcance por causa, a QC4 do estudo da concorrência
  concomitante de 07/11. É ato da conferência documental da convocação, e não Resultado de Etapa.

---

## Clarifications

### Session 2026-11-13 (decisões do usuário, no estudo)

- **P-2 — O que o desfecho desfavorável da verificação produz?** O Edital declara. O padrão é *"sai da
  reserva e fica na ampla"*, e *"elimina"* continua possível. *(Estudo da verificação da
  autodeclaração, README, "Decisões"; diagnóstico, §7.)* É o objeto desta spec.
- **P-1** é a `163`. **P-3** é a spec seguinte. Esta spec não antecipa a P-3: o desfecho desfavorável
  continua saindo da regra de consolidação de hoje, e esta spec diz só o que ele produz.

### Session 2026-11-14 (decisões desta spec, abertas à revisão do usuário)

As decisões D-001 a D-011 são as que a redação exigiu, e cada uma registra a alternativa descartada.
Nenhuma toma decisão normativa do Ifes: todas deixam ao Edital a escolha que ele já faz por escrito.

### Pergunta ao usuário

- **Q-1 — O não comparecimento tem o mesmo efeito do desfecho desfavorável?** É a P-6 do estudo, que
  o README deixou entre as que podem esperar. Os Editais divergem: o 57/2026 diz as duas coisas, "fica
  na ampla" no 8.10 e "elimina" no 8.11; o 28/2026 manda o indeferido por fenótipo para a ampla e
  silencia sobre o ausente. *Recomendação desta spec, e é a que a FR-7004 traz:* o Edital declara o
  efeito do não comparecimento à parte, e o padrão é **o mesmo que ele declarou para o desfecho
  desfavorável** (D-007). *Alternativas:* (a) um efeito só para os dois casos, sem declaração à parte;
  (b) o não comparecimento sempre elimina, como a Ocorrência da `013` faz hoje.

---

## User Scenarios & Testing *(mandatory)*

Os exemplos usam o Edital da `163`: três Perfis (C1, C2 e C3), cada um com as Modalidades `AC`, `PPI`
e `PcD`, e quatro Etapas na ordem: Prova (pontuada, classificatória, para todas as inscrições),
**Heteroidentificação** (decisória, eliminatória, só `PPI`), Análise documental (decisória, para
todas, governada pelo corte) e Entrevista (pontuada, para todas). O marco de classificação enumera a
Prova e a Heteroidentificação.

### User Story 1 — Quem elabora declara o que o desfecho desfavorável produz (Priority: P1)

Quem elabora o Edital restringe a Heteroidentificação a `PPI` e a marca como eliminatória. A tela
passa a perguntar *"O que acontece com quem tem desfecho desfavorável nesta Etapa?"*, com a primeira
opção já marcada: *"Deixa de concorrer pela reserva e continua na ampla concorrência"*. A segunda é
*"É eliminado do processo seletivo"*. Ela mantém a primeira. O documento passa a dizer, na Etapa, que
o candidato com desfecho desfavorável deixa de concorrer pela vaga reservada e continua concorrendo
pela ampla concorrência.

**Why this priority**: sem a declaração, nada do resto existe, e é a única parte que muda o documento
oficial.

**Independent Test**: compor o Edital acima, publicar, e conferir no conteúdo publicado, na Revisão e
no documento que a Heteroidentificação declara o efeito, e que as outras três Etapas não declaram
nada.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração com a Heteroidentificação restrita a `PPI` e eliminatória,
   **When** quem elabora a abre, **Then** a pergunta do efeito aparece com *"Deixa de concorrer pela
   reserva e continua na ampla concorrência"* marcada.
2. **Given** a mesma Etapa, **When** quem elabora escolhe *"É eliminado do processo seletivo"* e
   grava, **Then** a gravação passa, e a Revisão diz que o desfecho desfavorável elimina.
3. **Given** a Etapa Prova, para todas as inscrições, **When** quem elabora a abre, **Then** a pergunta
   do efeito não aparece: a Etapa que alcança todas as inscrições continua só eliminando.
4. **Given** uma Etapa restrita e **não** eliminatória, **When** quem elabora a abre, **Then** a
   pergunta do efeito não aparece.
5. **Given** o Edital composto com *"Deixa de concorrer pela reserva"*, **When** é publicado, **Then**
   o documento diz o efeito na Heteroidentificação, em todas as redações que descrevem a Etapa, e as
   outras três Etapas saem com o texto que sairiam antes desta feature.
6. **Given** o conteúdo de uma Etapa que declara *"Deixa de concorrer pela reserva"* e alcança todas
   as inscrições, por qualquer caminho, **When** chega à publicação, **Then** a publicação é impedida,
   e a mensagem diz que só a Etapa restrita tem reserva de onde tirar alguém.

---

### User Story 2 — O desfecho desfavorável tira da reserva e deixa na ampla (Priority: P1)

Maria (`PPI`, C1) teve 82 pontos na Prova. A comissão conclui a Heteroidentificação de Maria em
sentido desfavorável, e a presidência consolida. O Resultado de Maria diz *"Indeferido — deixa de
concorrer pela reserva Pretos e pardos (`PPI`) e continua na ampla concorrência"*.

Na ordem do marco, Maria não tem posição na lista `PPI`, e tem na ampla, com os 82 pontos. Ela
participa da Análise documental se estiver na faixa do corte **da ampla**. Pode ocupar uma vaga da
ampla e ser convocada por ela. Nunca ocupa vaga reservada nem é convocada pela lista `PPI`.

**Why this priority**: é a decisão P-2 inteira. Sem ela, a heteroidentificação composta no GPS
contraria todo Edital lido.

**Independent Test**: no Edital acima, consolidar a Heteroidentificação com um `PPI` desfavorável sob
o efeito *"Deixa de concorrer pela reserva"*. Conferir a ordem dos dois recortes, a participação na
Análise documental, a ocupação e a fila de convocação de cada lista.

**Acceptance Scenarios**:

1. **Given** a conclusão desfavorável de Maria sob o efeito *"Deixa de concorrer pela reserva"*,
   **When** a presidência consolida, **Then** o Resultado de Maria tem a consequência *retirada da
   reserva*, e não *eliminada*. O motivo cita o rótulo publicado do desfecho e o nome da reserva.
2. **Given** o Resultado de Maria, **When** a ordem do marco é calculada, **Then** Maria aparece sem
   posição na lista `PPI`, com o motivo, e com a posição dos 82 pontos na ampla.
3. **Given** a Análise documental governada pelo corte, com Maria na faixa da ampla, **When** a
   distribuição é aberta, **Then** Maria participa. Com Maria fora da faixa da ampla e dentro da faixa
   `PPI`, ela não participa.
4. **Given** Maria habilitada na Análise documental pela faixa da ampla, **When** a ocupação da lista
   `PPI` é apurada, **Then** Maria não é contada nela, e a fila da lista `PPI` não a oferece. A
   ocupação e a fila da ampla a tratam como tratam qualquer inscrição da ampla.
5. **Given** a mesma conclusão sob o efeito *"É eliminado do processo seletivo"*, **When** a
   presidência consolida, **Then** o Resultado é *eliminada*, e tudo segue como hoje: sem posição em
   todas as listas, fora das Etapas seguintes, fora da ocupação e da convocação.
6. **Given** o candidato `PPI` com desfecho favorável, **When** a presidência consolida, **Then** nada
   muda em relação a hoje.

---

### User Story 3 — O candidato entende que perdeu a reserva, e não o certame (Priority: P1)

No acompanhamento, Maria não lê *"Eliminado"*. Ela lê que, na Heteroidentificação, o resultado foi
*Indeferido*, que por isso deixou de concorrer pela reserva Pretos e pardos e que continua concorrendo
pela ampla concorrência. O cartão da ampla mostra a posição dela. O cartão da reserva diz que ela
deixou de concorrer por ela, e por quê.

**Why this priority**: *"Eliminado"* para quem continua no certame é informação falsa sobre um direito.
Faria a pessoa desistir, ou recorrer contra o que não aconteceu.

**Independent Test**: abrir o acompanhamento de Maria sob cada um dos dois efeitos e comparar a
situação e as linhas.

**Acceptance Scenarios**:

1. **Given** o Resultado de Maria com *retirada da reserva*, numa Etapa que o marco enumera e com a
   ordem publicada, **When** Maria abre o acompanhamento, **Then** a situação não é *"Eliminado"*. Ela
   segue a classificação de Maria na ampla, e uma linha diz a Etapa, o rótulo do desfecho, a reserva
   perdida e que ela continua na ampla.
2. **Given** o mesmo Resultado, **When** Maria abre o cartão da lista `PPI`, **Then** ele diz que ela
   deixou de concorrer por essa lista e cita o motivo, sem posição.
3. **Given** o Resultado *eliminada*, sob o efeito *"É eliminado"*, **When** Maria abre o
   acompanhamento, **Then** ela vê *"Eliminado"*, com a frase de hoje.
4. **Given** o Resultado de Maria com *retirada da reserva*, **When** o prazo de recurso contra ele
   está aberto, **Then** o acompanhamento oferece o recurso como oferece contra a eliminação.

---

### User Story 4 — O recurso devolve a reserva sem mecanismo novo (Priority: P2)

Maria recorre, e a CPVA, julgando com `recurso:julgar`, defere. A decisão fixa a consequência
*habilitada*. O Resultado de Maria é sucedido, como na `018`. A ordem do marco fica obsoleta, como fica
hoje quando um deferimento muda o universo, e Maria volta a concorrer pela lista `PPI`.

**Why this priority**: o recurso contra o desfecho da verificação é obrigação da Res. CS 61/2019, art.
17. O caminho já existe e precisa só aceitar a consequência nova.

**Independent Test**: deferir o recurso contra um Resultado de retirada e conferir a sucessão, a
obsolescência da ordem e a volta à lista reservada.

**Acceptance Scenarios**:

1. **Given** o recurso deferido, **When** a decisão fixa *habilitada*, **Then** o Resultado é sucedido,
   e Maria volta à lista `PPI` no próximo cálculo da ordem.
2. **Given** o recurso contra um Resultado *habilitada* numa Etapa cujo efeito é *"Deixa de concorrer
   pela reserva"*, **When** a decisão tenta fixar *eliminada*, **Then** ela é recusada: a consequência
   desfavorável que a Etapa admite é a *retirada da reserva*.
3. **Given** o recurso indeferido, **When** a decisão é registrada, **Then** o Resultado de retirada
   continua vigente, e nada muda nas listas.

---

### User Story 5 — A Retificação do efeito não muda a regra no meio do caminho (Priority: P2)

Publicado o Edital, alguém percebe que a cláusula do Edital elimina e a composição diz *"Deixa de
concorrer pela reserva"*. Uma Retificação troca o efeito antes de a comissão consolidar qualquer
desfecho desfavorável, e passa. Em outro Edital, a mesma troca vem depois de três Resultados de
retirada, e é recusada: a mensagem diz quantos Resultados desfavoráveis a Etapa já tem.

**Why this priority**: o efeito é norma, e norma publicada só muda por Retificação. Trocá-lo depois de
aplicado faria dois candidatos com o mesmo desfecho terem efeitos diferentes.

**Independent Test**: retificar o efeito antes e depois do primeiro Resultado desfavorável na Etapa.

**Acceptance Scenarios**:

1. **Given** a Etapa sem nenhum Resultado desfavorável vigente, **When** uma Retificação troca o
   efeito, **Then** ela passa, e todo desfecho consolidado depois dela segue o efeito novo.
2. **Given** a Etapa com Resultado desfavorável vigente, **When** uma Retificação troca o efeito,
   **Then** ela é recusada, e a mensagem nomeia a Etapa e diz quantos Resultados desfavoráveis
   impedem.
3. **Given** a Etapa restrita com Resultado de retirada, **When** uma Retificação a devolve a *"Todas
   as inscrições"*, **Then** ela é recusada pela mesma razão: a Etapa para todas não tem efeito de
   retirada, e devolvê-la mudaria o efeito.
4. **Given** uma Retificação em elaboração que troca o efeito, **When** a presidência consolida, ao
   mesmo tempo, um desfecho desfavorável na Etapa, **Then** um dos dois atos prevalece por inteiro.
   Ou a consolidação aplica o efeito vigente e a Retificação é recusada na publicação, ou a
   Retificação é publicada e a consolidação aplica o efeito novo. Nunca um Resultado com o efeito de
   uma versão que não era a vigente no ato.

---

### Edge Cases

Cada caso abaixo é requisito, e cita o requisito que o resolve.

- **O não comparecimento.** A Ocorrência de ausência numa Etapa restrita produz o efeito que o Edital
  declara para o não comparecimento. O padrão é o mesmo efeito do desfecho desfavorável (FR-7004,
  Q-1). Numa Etapa para todas as inscrições, a Ocorrência continua eliminando, como hoje.
- **O efeito por motivo.** O 28/2026 manda para a ampla só o indeferido *por fenótipo*, e lista outros
  motivos de indeferimento: o formulário, a recusa às orientações, a recusa a ser filmado. Esta spec
  declara o efeito **por Etapa**, e não por motivo. Todo desfecho desfavorável por avaliação tem o
  mesmo efeito; só a ausência tem efeito à parte. O Edital que distinga motivos não é representável
  aqui, e isso fica registrado em *Achados* (FR-7003).
- **Eliminado depois em outra Etapa.** Maria, retirada da reserva, é depois eliminada na Análise
  documental. A eliminação vale como hoje, para todas as listas. A retirada anterior não a atenua
  (FR-7011).
- **Retirada numa Etapa anterior à última do marco.** Quando a Etapa restrita vem antes da última
  Etapa que o marco enumera, seja ela enumerada ou não, a inscrição retirada sai do universo da lista
  reservada, como a eliminada sai hoje de todos. Ela continua no universo da ampla. Quando a Etapa
  restrita **é** a última enumerada, a inscrição fica no universo reservado, sem posição e com o
  motivo, como a eliminada fica hoje (FR-7012).
- **Retirada numa Etapa posterior ao marco.** Quando a Etapa restrita vem **depois** da última Etapa
  que o marco enumera, a retirada não muda a ordem daquele marco, como a eliminação de hoje também
  não muda (FR-7012). A heteroidentificação *"dos sorteados"* do 57/2026 cairia aí, e nem a eliminação
  de hoje chega à ocupação e à convocação desse marco. Fica em *Achados*, e não é escopo.
- **A faixa do corte já emitida.** O corte que governa a Análise documental foi emitido antes da
  Heteroidentificação, e Maria estava na faixa `PPI` e fora da faixa da ampla. Retirada, ela não
  participa da Análise documental. A faixa `PPI` **não** se reabre para o seguinte. A vaga reservada
  que fica sem ocupante segue o caminho de hoje para vaga reservada sem ocupante: suplência, a
  continuação da ordem quando o Edital a admite, e a destinação da `155` (FR-7013, FR-7015).
- **Habilitada na Etapa governada pela faixa da ampla.** Maria, retirada, está nas duas faixas e é
  habilitada na Análise documental. A ocupação da lista `PPI` lê *"progrediu na faixa `PPI` e foi
  habilitada na Etapa governada"*, e a contaria. Ela **não** é contada na reserva, nem oferecida pela
  fila da reserva (FR-7014).
- **Concorrência concomitante e o 8.9 do 57/2026.** O candidato `PPI` classificado dentro das vagas da
  ampla ocupa a ampla, e não é contado na reserva. Isso não muda. A retirada não altera a ocupação da
  ampla de ninguém (FR-7014).
- **Já convocado pela reserva.** Pela regra acima, a retirada só chega à ordem do marco que a lê antes
  de a ordem ser emitida. O caminho para uma convocação pela reserva existir antes de um Resultado de
  retirada é a superação, quando um recurso ou uma regularização muda o Resultado depois da
  convocação. Ele segue o tratamento que a superação de um Resultado tem hoje: a ordem fica obsoleta,
  e nenhum mecanismo novo de desfazimento é criado (FR-7016).
- **Recurso que devolve a reserva.** A decisão que fixa *habilitada* sucede o Resultado de retirada. A
  inscrição volta à lista reservada pelo mesmo caminho de obsolescência que o deferimento de uma
  eliminação já percorre (FR-7019).
- **A Modalidade declarada como ampla e a inscrição sem Modalidade.** A Etapa restrita nunca as alcança
  (a regra da `163`). Logo, nunca têm Resultado de retirada.
- **A Etapa restrita a mais de um código.** A Heteroidentificação restrita a `PPI` e `PcD` tira cada
  inscrição da reserva da **sua** Modalidade declarada. Não há outra, porque a inscrição declara uma
  só (FR-7010).
- **Outra lista reservada.** Uma Modalidade `EP-PPI` (escola pública e pretos e pardos) retirada não
  passa para a lista `EP`: o GPS não sabe o que o código significa, e os Editais lidos dizem *"apenas
  na ampla"* (FR-7010, D-006).
- **Retificação que amplia o alcance.** A `163` aceita a Retificação que acrescenta código ao alcance.
  As inscrições que passam a ser alcançadas recebem o efeito declarado, que não mudou. O efeito não é
  tocado (FR-7021).
- **Retificação que torna a Etapa não eliminatória.** É mudança de efeito, e segue a FR-7020.
- **Etapa sem nenhuma inscrição alcançada.** O efeito é declarado e publicado, e não produz nada (a
  regra da `163` sobre a Etapa sem alcançados).
- **Ato histórico.** O Resultado de retirada continua lido pela consequência que gravou e pela versão
  que citou, ainda que uma Retificação posterior, quando permitida, mude o efeito (FR-7008).
- **A prévia da classificação.** A prévia da `094` e da `098` simula eliminação em Etapa. Ela não
  ganha cenário de retirada nesta spec, e a equivalência entre a prévia e o caminho oficial continua
  valendo para tudo o que ela simula (FR-7026).
- **Painéis e relatórios.** O relatório do Edital conta as eliminadas por avaliação e por Ocorrência. A
  retirada **não** entra nessa conta. É contada à parte (FR-7025).
- **A Etapa que nenhum marco enumera.** Ela não é visível nem recorrível para o titular, e a `163`
  deixou isso para a spec da R-8. A retirada nela também fica invisível até lá: o candidato não acha
  o cartão da reserva, e não lê o porquê. Fica registrado como risco (FR-7024).

## Requirements *(mandatory)*

### Functional Requirements

#### A declaração

- **FR-7000**: A Etapa de alcance restrito e eliminatória DEVE declarar o **efeito do desfecho
  desfavorável**, de uma de duas formas: **retira da reserva**, e então a inscrição deixa de concorrer
  pela lista reservada da sua Modalidade e continua na ampla; ou **elimina**, e então a inscrição é
  eliminada do processo seletivo, como hoje (D-001).
- **FR-7001**: Na composição, a Etapa que passa a ser restrita e eliminatória DEVE nascer com o efeito
  **retira da reserva** marcado, e assim DEVE ser lida a Etapa restrita de rascunho que ainda não o
  declarou. O conteúdo **publicado** antes desta feature, que não tem a declaração, DEVE ser lido como
  **elimina**, que é o que ele significava quando foi publicado (D-002).
- **FR-7002**: A Etapa que alcança todas as inscrições, e a Etapa não eliminatória, NÃO DEVEM declarar
  efeito. A publicação e a Retificação DEVEM ser impedidas quando uma delas declarar **retira da
  reserva**, com mensagem que nomeie a Etapa e diga por que ela não tem reserva de onde retirar.
- **FR-7003**: O efeito DEVE ser **um por Etapa**, e valer para todo desfecho desfavorável por
  avaliação nela, qualquer que seja o motivo registrado. Só o não comparecimento tem declaração à
  parte (FR-7004).
- **FR-7004**: A Etapa restrita e eliminatória DEVE declarar também o **efeito do não comparecimento**,
  com as mesmas duas formas. O padrão DEVE ser o mesmo efeito declarado para o desfecho desfavorável
  (D-007). *Depende da Q-1.*
- **FR-7005**: O efeito DEVE fazer parte do conteúdo normativo publicado do Edital, num degrau novo da
  versão canônica. O conteúdo publicado antes desse degrau DEVE ser lido como **elimina** nos dois
  efeitos, sem invenção. O resumo canônico de toda Publicação existente DEVE continuar o mesmo (D-002).
- **FR-7006**: O efeito DEVE ser classificado no contrato de mutabilidade como **retificável**, com a
  restrição da FR-7020. O guardião do contrato DEVE cobri-lo como cobre os demais campos da Etapa.

#### O Resultado

- **FR-7007**: O desfecho desfavorável numa Etapa cujo efeito é **retira da reserva** DEVE produzir um
  Resultado da Etapa com uma consequência própria, **retirada da reserva**, distinta de *habilitada* e
  de *eliminada* (D-003). A consequência DEVE sair da regra publicada, como sai hoje. Nem a
  presidência nem a comissão a escolhem.
- **FR-7008**: O Resultado de retirada DEVE guardar a versão normativa que o fundamentou e o motivo.
  O motivo DEVE citar o rótulo publicado do desfecho e o nome da reserva perdida, e DEVE dizer que a
  inscrição continua na ampla. Lido depois, ele DEVE significar o mesmo, por si, ainda que uma
  Retificação posterior mude o efeito.
- **FR-7009**: A Ocorrência de não comparecimento numa Etapa restrita DEVE produzir a consequência que
  o efeito do não comparecimento declara: **retirada da reserva** ou **eliminada**. Numa Etapa que
  alcança todas as inscrições, ela DEVE continuar produzindo **eliminada**.

#### O que acontece em cada lista

- **FR-7010**: A retirada DEVE tirar a inscrição **só** da lista reservada da Modalidade que ela
  declarou. A inscrição DEVE continuar na ampla, com tudo o que a ampla lhe daria sem a Etapa. Ela
  NÃO DEVE passar a outra lista reservada (D-006).
- **FR-7011**: Para as Etapas seguintes, a retirada NÃO DEVE excluir a inscrição, como a eliminação
  exclui. Ela DEVE satisfazer a exigência de habilitação na Etapa anterior, como a habilitação
  satisfaz (D-004). Uma eliminação, anterior ou posterior, DEVE continuar valendo para todas as listas,
  e a retirada não a atenua.
- **FR-7012**: Na ordem de cada marco, a retirada DEVE produzir **na lista reservada** da Modalidade da
  inscrição exatamente o efeito que a eliminação na mesma Etapa produz hoje em todas as listas: fora do
  universo, quando a Etapa precede a última que o marco enumera, enumerada ou não; sem posição, com a
  consequência e o motivo, quando ela é a última que o marco enumera; nenhum, quando ela vem depois
  da última que o marco enumera. **Na ampla, a retirada NÃO DEVE produzir efeito nenhum** (D-005).
- **FR-7013**: Na faixa do corte que governa uma Etapa seguinte, a inscrição retirada DEVE ser contada
  só pela faixa da ampla, e não pela faixa da lista reservada que perdeu. Estar na faixa reservada não
  a faz participar da Etapa governada.
- **FR-7014**: A inscrição retirada NÃO DEVE ser contada como ocupante da lista reservada, nem oferecida
  pela fila de convocação dela, ainda que tenha progredido na faixa reservada e sido habilitada na
  Etapa governada. Na ampla, ela DEVE ser contada e oferecida como qualquer inscrição da ampla, e a
  regra de hoje da concorrência concomitante DEVE continuar valendo.
- **FR-7015**: A vaga reservada que fica sem ocupante por causa de uma retirada DEVE seguir o caminho
  que a vaga reservada sem ocupante já segue: suplência, continuação da ordem quando o Edital a
  admite, e destinação pela `155`. Esta spec NÃO DEVE criar caminho próprio para ela, nem reabrir a
  faixa de corte já emitida.
- **FR-7016**: A mudança de um Resultado de retirada por superação, seja por recurso ou por
  regularização, DEVE tornar obsoletos os atos que leram o Resultado anterior (ordem, corte, apuração),
  pelos mesmos mecanismos de obsolescência que existem hoje. Esta spec NÃO DEVE criar mecanismo de
  desfazimento de convocação.
- **FR-7017**: A publicação dos convocados (`149`) e a publicação da ordem DEVEM listar a inscrição
  retirada só nas listas em que ela ainda concorre. A parte pública NÃO DEVE trazer o motivo da
  retirada. Ele vai só ao titular, como o motivo da eliminação vai hoje.
- **FR-7018**: Nenhuma leitura da consequência de Resultado da Etapa DEVE tratar a **retirada** como
  *eliminada* ou como *habilitada* por omissão. Toda superfície que hoje distingue as duas DEVE dizer o
  que faz com a terceira, e um guardião DEVE recusar a leitura que a ignore.

#### Recurso

- **FR-7019**: O Resultado de retirada DEVE ser recorrível como o Resultado de eliminação é. A decisão
  recursal que fixa consequência DEVE poder fixar só as que a Etapa admite pela versão que o Resultado
  citou: *habilitada* e o efeito desfavorável declarado. A decisão que fixa *habilitada* DEVE suceder
  o Resultado de retirada pelo mecanismo da `018`, e a inscrição DEVE voltar à lista reservada.

#### A Retificação

- **FR-7020**: A Retificação que **muda o efeito** de uma Etapa DEVE ser impedida enquanto a Etapa
  tiver ao menos um Resultado vigente desfavorável, por avaliação, Ocorrência ou recurso. Isso vale
  para a troca entre as duas formas, para a troca do efeito do não comparecimento, para a Etapa que
  volta a alcançar todas as inscrições e para a que deixa de ser eliminatória. A mensagem DEVE nomear
  a Etapa e dizer quantos Resultados desfavoráveis impedem (D-008).
- **FR-7021**: A Retificação que não muda o efeito, como a que amplia o alcance, NÃO DEVE ser impedida
  por esta spec. As inscrições que passam a ser alcançadas DEVEM receber o efeito declarado.
- **FR-7022**: A Retificação do efeito e a consolidação ou a Ocorrência na mesma Etapa DEVEM ser
  serializadas: o Resultado DEVE aplicar o efeito da versão vigente no instante do ato, e a Retificação
  DEVE ser recusada se, ao ser publicada, a FR-7020 a impedir.

#### O que o documento, a gestão e o candidato leem

- **FR-7023**: O documento do Edital DEVE dizer, na Etapa que declara o efeito, o que o desfecho
  desfavorável produz e, quando diferente, o que o não comparecimento produz, em todas as redações em
  que descreve a Etapa. A Etapa sem declaração DEVE sair com o texto que sairia antes desta feature
  (D-010). A Revisão, a página pública do Edital e a tela de Retificação DEVEM dizer o efeito com as
  mesmas palavras.
- **FR-7024**: O acompanhamento NÃO DEVE apresentar como *"Eliminado"* o titular cujo único desfecho
  desfavorável é retirada. A situação dele DEVE seguir a classificação nas listas em que ele ainda
  concorre. Uma linha DEVE dizer a Etapa, o rótulo do desfecho, a reserva perdida e que ele continua
  na ampla, e o cartão da lista reservada DEVE dizer que ele deixou de concorrer por ela e por quê. A
  visibilidade da linha DEVE ser a que a Etapa tem hoje para o titular (D-011).
- **FR-7025**: Os painéis e relatórios da gestão que contam desfechos por Etapa DEVEM contar a retirada
  **à parte** da eliminação, e nunca somá-la a ela. A Mesa e o panorama da Etapa DEVEM mostrar a
  consequência pelo nome.
- **FR-7026**: A prévia da classificação NÃO DEVE simular retirada nesta entrega. A equivalência entre
  a prévia e o caminho oficial DEVE continuar valendo para todo cenário que ela simula.

### Requisitos de experiência

- **UX-740**: A pergunta do efeito DEVE aparecer só na Etapa restrita e eliminatória, como duas opções
  exclusivas escritas pelo que acontece com a pessoa: *"Deixa de concorrer pela reserva e continua na
  ampla concorrência"* e *"É eliminado do processo seletivo"*. A primeira DEVE vir marcada.
- **UX-741**: A pergunta do não comparecimento DEVE vir logo abaixo, com a opção *"O mesmo efeito"* como
  padrão, de modo que quem não precisa distinguir não precise ler duas perguntas.
- **UX-742**: O texto ao candidato DEVE usar *"deixou de concorrer pela reserva «Modalidade»"* e
  *"continua concorrendo pela ampla concorrência"*. NÃO DEVE usar *"eliminado"*, *"desclassificado"* nem
  *"excluído"* para a retirada.
- **UX-743**: Na tela de consolidação, antes da confirmação, a presidência DEVE ver quantas inscrições
  serão retiradas da reserva e quantas eliminadas, cada uma pelo nome da consequência.

### Key Entities

- **Etapa de avaliação**: ganha o **efeito do desfecho desfavorável** e o **efeito do não
  comparecimento**, só quando restrita e eliminatória. É norma publicada, retificável até o primeiro
  Resultado desfavorável.
- **Resultado da Etapa**: ganha a terceira consequência, **retirada da reserva**, ao lado de
  *habilitada* e *eliminada*. Continua imutável, sucedido só pela `018`.
- **Decisão de recurso**: pode fixar a consequência nova, nos limites da FR-7019.
- **Lista de concorrência**: a ampla, sem Modalidade, e a reservada de cada Modalidade. A retirada
  tira a inscrição da reservada da sua Modalidade e não a tira da ampla.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2330**: **Todo** Edital publicado antes desta feature, recomposto depois dela, produz o mesmo
  resumo canônico e o mesmo documento, byte a byte.
- **SC-2331**: No Edital de exemplo, com dez `PPI` desfavoráveis sob *"Deixa de concorrer pela
  reserva"*, **zero** deles ficam com posição, ocupação ou lugar na fila da lista `PPI`, e **dez de
  dez** ficam com a posição na ampla que teriam sem a Etapa.
- **SC-2332**: No mesmo Edital, sob *"É eliminado"*, a ordem, a ocupação e a fila de cada lista saem
  **idênticas** às que o sistema de antes desta feature produz para o mesmo cenário.
- **SC-2333**: **Zero** titulares cujo único desfecho desfavorável é retirada veem *"Eliminado"* no
  acompanhamento.
- **SC-2334**: **100%** das Retificações que mudariam o efeito de Etapa com Resultado desfavorável são
  recusadas, e nenhuma linha de Resultado muda.
- **SC-2335**: O guardião da FR-7018 acha **zero** leituras da consequência que ignorem a retirada.
- **SC-2336**: *(humano)* Uma pessoa da CPS ou da comissão de heteroidentificação, lendo só o
  documento publicado do Edital de exemplo, responde corretamente o que acontece com o candidato
  indeferido e com o ausente.

## Assumptions

- **A `163` entra antes.** Esta spec usa o alcance da Etapa por Modalidade, a regra que impede a Etapa
  restrita de decidir algo que valha para todas as listas (ordem pontuada, peso, desempate, corte e
  habilitação ao sorteio) e o estado *fora do alcance*. Se a `163` mudar no merge, esta spec é revista.
- **Uma Modalidade por inscrição**, imutável depois do envio. É o que torna "a reserva da inscrição"
  uma lista só.
- **O GPS não sabe o que o código significa.** Ele não distingue cota racial de outra. É o Edital que
  restringe a Etapa a `PPI` e declara o efeito.
- **O desfecho desfavorável continua saindo da regra de consolidação de hoje.** Com mais de uma
  avaliação por inscrição, a Etapa continua sem regra de combinação até a spec da P-3.
- **A Etapa restrita não é governada pelo corte** (regra da `163`). Por isso nenhuma apuração de
  ocupação lê a retirada **como Resultado da Etapa governada**. Ela chega à ocupação pela ordem, pela
  faixa e pela FR-7014.

## Out of Scope

- A regra de deliberação dos pareceres (P-3).
- O vídeo assíncrono (camada B).
- A análise documental de indígenas.
- A visibilidade e a recorribilidade da Etapa que nenhum marco enumera (R-8).
- O efeito por motivo de indeferimento.
- A migração da inscrição retirada para outra lista reservada.
- O indeferimento na convocação com alcance por causa (QC4 do estudo de 07/11).
- O alcance, na ocupação e na convocação, da Etapa posterior à última Etapa que o marco enumera
  (*Achados*).
- O aviso por e-mail do desfecho (avisos complementares da `066`).
- O cenário de retirada na prévia da classificação.

## Dependências

- **Esta spec depende de:**
  - a `163`, pelo alcance;
  - a `013`, pela consolidação, pela Ocorrência e pela progressão;
  - a `014`, pela faixa do corte;
  - a `016` e a `019`, pela ocupação, a concorrência concomitante e a convocação;
  - a `018`, pelo recurso e pela superação;
  - a `094`, pelo universo da ordem;
  - a `149` e a `155`, pela publicação dos convocados e pela vaga não preenchida.
- **Desta spec depende** a spec da P-3, que dirá *quando* o desfecho é desfavorável. Esta diz o que ele
  produz.

## Achados (registro, e não escopo)

- **A Etapa posterior ao marco não chega às listas dele.** A ocupação e a convocação leem os Resultados
  da Etapa **governada** pelo corte, e a ordem lê as Etapas até a última que o marco enumera. Uma Etapa
  depois disso, e não governada, não alcança a ordem, a ocupação nem a convocação daquele marco. A
  eliminação de hoje também não alcança. A heteroidentificação *"dos sorteados dentro do número de
  vagas"* do 57/2026 vem depois do sorteio, e cairia aí. É decisão do usuário se e como ela entra.
- **O efeito por motivo.** O 28/2026 distingue o indeferido por fenótipo, que vai para a ampla, dos
  demais motivos do 6.9.14, sobre os quais silencia. O 57/2026 contradiz a si mesmo sobre o ausente,
  no 8.10 e no 8.11. As duas leituras são perguntas à CPVA, ao lado da P-3. Se a resposta for "por
  motivo", o efeito desta spec ganha uma dimensão, e a lista fechada de motivos da R-5 do estudo passa
  a ser precondição.

## Decisões

### D-001 — O efeito é declaração da Etapa restrita, com duas formas

A P-2 diz que o Edital declara. Declarar na Etapa, e não no Perfil ou na Modalidade, é o que a
heteroidentificação pede: o efeito é da verificação, e não da cota. As duas formas são as que os
Editais lidos escrevem: o 28/2026 e o 57/2026, 8.10, tiram da reserva; o 57/2026, 8.11, e a Res. CS
61/2019, art. 16, eliminam. *Descartados:*

- **efeito por Modalidade.** Duas Modalidades na mesma Etapa com efeitos diferentes não aparecem em
  Edital nenhum, e a declaração dobraria;
- **uma terceira forma, "não produz efeito".** É a Etapa não eliminatória, que já existe, e a FR-047
  da `013` continua impedindo a decisória sem efeito.

### D-002 — O padrão é para o que se compõe, e não para o que já foi publicado

A P-2 fixou o padrão *"sai da reserva"*, e ele vale onde alguém está compondo: a Etapa restrita nasce
com ele marcado. O conteúdo já publicado, que não tem a declaração, é lido como **elimina**, porque é o
que ele produzia no dia em que foi publicado. Lê-lo pelo padrão novo mudaria, sem Retificação, o efeito
de norma publicada. Por isso o documento e o resumo canônico do acervo não mudam (SC-2330).
*Descartado:* ler o publicado pelo padrão novo, que é a mesma infração com a melhor das intenções.

### D-003 — A retirada é consequência do Resultado, e não leitura do Edital sobre o *eliminada*

O Resultado poderia continuar *eliminada*, e cada leitor consultar o efeito na versão da Etapa. Isso
deixaria o Resultado mentindo por si: quem o lê sem a versão leria que a pessoa foi eliminada. E todo
leitor que hoje compara com *eliminada* continuaria eliminando, em silêncio, até alguém lembrar dele. A
consequência própria obriga cada leitor a decidir (FR-7018), e o ato fica reproduzível pelo que gravou,
como a Constituição pede no Princípio II. *Descartado:* manter *eliminada* com um marcador de alcance,
que tem os dois defeitos acima com um campo a mais.

### D-004 — Para as Etapas seguintes, a retirada segue

A inscrição retirada continua no certame pela ampla, e as Etapas seguintes são da ampla também.
Tratá-la como **não habilitada** a pararia na Análise documental, e a ampla que o Edital lhe garante
seria letra morta. *Descartado:* uma quarta situação de progressão, que seria estrutura para a mesma
resposta.

### D-005 — Na lista reservada, a retirada faz o que a eliminação faz hoje, e só isso

A ordem, a faixa e o universo já sabem o que fazer com quem uma Etapa tirou: depende de onde a Etapa
está em relação ao marco. A retirada repete a mesma regra, restrita à lista reservada. Assim nenhum
caminho novo é inventado, e o lugar em que a eliminação de hoje não chega fica igualmente sem a
retirada, registrado em *Achados*. O único acréscimo é a FR-7014, porque a ocupação conta pela faixa e
pela Etapa governada, e a inscrição retirada pode estar habilitada nela pela ampla. É o caso em que
"fazer o que a eliminação faz" não basta, porque a eliminação nunca chega habilitada à Etapa governada.
*Descartado:* uma regra própria de alcance temporal para a retirada.

### D-006 — Da reserva vai-se para a ampla, e não para outra reserva

Os Editais lidos dizem *"permanecendo apenas na lista de ampla concorrência"*. Mandar a inscrição
`EP-PPI` para a lista `EP` exigiria saber que uma contém a outra, e o GPS não sabe o que o código
significa. *Descartado:* a migração entre reservas, que precisaria de um Edital que a escreva e de um
marcador semântico que a `039` não criou.

### D-007 — O não comparecimento tem efeito à parte, com o mesmo padrão

Os Editais divergem sobre o ausente, e o 57/2026 diverge de si mesmo. Um efeito só obrigaria o Edital
que elimina o ausente e mantém o indeferido na ampla a escolher uma cláusula e trair a outra. Dois
efeitos com o mesmo padrão não pesam para quem não precisa distinguir (UX-741). É a recomendação da
Q-1, e não decisão fechada. *Descartados:* (a) um efeito só; (b) o ausente sempre eliminado, como a
Ocorrência da `013` faz hoje, que contraria o 8.10 do 57/2026.

### D-008 — O efeito se retifica até o primeiro Resultado desfavorável

Depois de aplicado, o efeito decidiu a vida de alguém. Trocá-lo daria a dois candidatos com o mesmo
desfecho efeitos diferentes, e reescrever o Resultado já consolidado é proibido. É a razão que a `163`
deu para recusar o estreitamento do alcance sobre inscrição avaliada, aplicada ao efeito. O Resultado
favorável não impede, porque o efeito não o tocou. *Descartados:* **não retificável**, que deixaria sem
correção o erro de composição mais provável, a divergência entre a cláusula e a opção marcada; e
**retificável com efeito só para o futuro**, que é a desigualdade acima.

### D-009 — "Elimina" é o efeito de hoje, inteiro

A forma **elimina** não é uma eliminação nova. É a de hoje, com todas as leituras que a eliminação tem.
Por isso o cenário sob *"É eliminado"* sai idêntico ao que o sistema de antes produz (SC-2332).

### D-010 — O documento fala do efeito só quando ele é declarado

A Etapa sem declaração, que é todo o acervo e toda Etapa para todas as inscrições, sai com o texto de
hoje. A Etapa que declara ganha uma frase com o efeito, e outra para o ausente quando ele for
diferente. Um Edital que restringe a Heteroidentificação a `PPI` e não diz o que acontece com o
indeferido é o defeito de leitura que a P-2 fecha.

### D-011 — O retirado não é "Eliminado" na tela

O acompanhamento da `063` tem o degrau *"Eliminado"* acima da classificação. O retirado continua
classificado na ampla, e o degrau certo para ele é o da classificação, com a linha que explica a
reserva perdida. *Descartado:* um degrau novo, *"Retirado da reserva"*, acima da classificação. Ele
esconderia a informação que importa à pessoa, a posição na ampla, atrás da que ela já perdeu.
