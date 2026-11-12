# Feature Specification: A formalização na jornada guiada do Edital

**Feature Branch**: `claude/eager-snyder-f9441b`, sobre a `main` em `95eee5ed`

**Created**: 2026-11-11

**Status**: **Em implementação, no mesmo PR da spec.** As **perguntas P-1 a P-5** foram respondidas pelo
usuário em 11/11/2026, todas na alternativa recomendada (ver Clarifications). A P-6 e a P-7 ficaram fora,
como a spec recomenda. As decisões D-001 a D-008, abaixo, são **propostas de desenho**.

**Input**: o pedido de 11/11/2026, vindo da sessão do estudo da jornada final: *"levar a formalização
para a jornada guiada do Edital"*. Ele trata o achado de experiência número 05 do
[estudo da jornada final](../../doc/estudo-jornada-final-2026-11-11/index.html) (PR #472), chamado
"UX 05" no estudo. Prioridade alta, causa "Interface (derivação)".

> **Faixa de identificadores.** Esta spec abre em **FR-6100**, **SC-1950** e **UX-560**, com folga
> sobre o teto medido em 11/11/2026 na `main` e nos PRs abertos. O teto era: o requisito cinco mil
> setecentos e trinta e seis e o critério mil oitocentos e sessenta e cinco, os dois da `149`; o
> critério de experiência quatrocentos e sessenta e cinco, da `148`; e, no PR #471 da `150`, a faixa
> do requisito cinco mil e seiscentos, do critério mil e oitocentos e da experiência quinhentos. O
> número desta spec é `153`: ela nasceu como `152`, e a spec irmã de prevenção nos atos da
> convocação (#475), aberta no mesmo dia, também tomou a `152`. As faixas não se sobrepõem — a irmã
> abre no requisito cinco mil e oitocentos, no critério mil e novecentos e na experiência quinhentos
> e trinta —, e por isso só a pasta mudou.
> As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3669 da `117`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número. Os achados do estudo são citados como "UX 05", sem hífen, porque o identificador
> com hífen seria lido como requisito de experiência desta base.

---

## Por que esta feature existe

**No estudo, a jornada parecia terminar no aceite.** No Edital SIM09/2026 do cenário de treinamento
C09, duas pessoas, e depois três, ficaram *aptas para formalização* (desfecho Aceite). Mesmo assim,
nenhuma destas três telas falou do que vinha depois:

- o "O que fazer agora" do Centro do Edital;
- a fase Conclusão (`?fase=conclusao`);
- a confirmação de encerrar (`/gestao/editais/<id>/atos/encerrar`).

Nenhuma delas mencionou definir os documentos que vão ao setor, designar quem os recebe ou exportar.
A definição do Edital estava **vazia** e ninguém foi avisado. As evidências estão no estudo:

| Imagem | O que mostra |
|---|---|
| `F04-apos-aceite.png` | o Centro depois do aceite, sem nada sobre o setor |
| `F06-formalizacao-definicao-vazia.png` | a definição dos documentos nunca gravada |
| `F07-fase-conclusao.png` | a fase Conclusão: "Tudo tem desfecho, e o Edital pode ser encerrado?" |
| `X06-encerramento-sim09.png` | a confirmação de encerrar: uma advertência só, do resultado de uma lista |

**O estudo chegou à formalização porque quem conduzia sabia onde procurar.** O botão "Documentos para
a formalização" fica em "Administração e histórico". O impacto que o estudo registrou é este: os
documentos podem nunca chegar ao setor, e o Edital pode ser encerrado assim.

**O GPS já sabe tudo o que falta.** A `117` registra quatro coisas:

- a definição, append-only e versionada (FR-3653 a FR-3655 da `117`);
- a designação, com revogação (FR-3662 da `117`);
- quem está apto, lido na hora (FR-3669 da `117`);
- cada pacote gerado (FR-3700 da `117`).

A `127` e a `136` sabem derivar providências e pô-las numa fase. **Falta ligar uma coisa à outra.**
Esta spec não cria estado novo nem registro novo.

### O que esta spec cobre

- **A.** Três providências derivadas no nível 1 da `127`, cada uma do seu papel:
  - definir os documentos;
  - designar quem recebe;
  - exportar os das pessoas aptas.
- **B.** O bloco **"Disponibilizar ao setor"** na fase Conclusão do Centro (`136`), com a lista das três
  e o que falta em cada uma.
- **C.** A frase da fase Conclusão sobre o limite da responsabilidade do GPS: ela termina em
  *disponibilizado ao setor*.
- **D.** A advertência na confirmação de encerrar o Edital (`113`) quando há pessoas aptas sem
  documentos disponibilizados.

### O que fica fora

- **Confirmação de recebimento pelo setor.** Ela continua fora, pela decisão da `117` que a deixou
  fora do MVP (FR-3707 da `117`).
- **Mudar quem designa.** A proposta de a presidência designar
  (`doc/achado-designacao-da-formalizacao-pela-presidencia.md`, na worktree da `127`) **não está
  decidida**, e esta spec não a pressupõe. A D-006 diz como as duas convivem.
- **Oferecer o papel Formalização no ambiente de demonstração** (UX 06 do estudo).
- **Mudar a página do setor** ("Formalização", FR-3675 da `117`). Ver P-6.
- **O cancelamento do Edital.** Esta spec não acrescenta advertência ao cancelar. Ver Edge Cases.
- **Estado, registro, tabela, migration ou evento de trilha novo.**

---

## Clarifications

### Session 2026-11-11

O usuário respondeu as perguntas P-1 a P-5, todas na alternativa recomendada. A P-6 e a P-7 ficaram
como a spec recomenda, fora do escopo.

- Q: O nome é "Encaminhar ao setor" ou "Disponibilizar ao setor"? → A: **"Disponibilizar ao setor"**
  (P-1). A decisão de terminologia da `117` não se reabre.
- Q: O que conta como pessoa disponibilizada? → A: **Estar incluída em algum pacote gerado do
  Edital**, em qualquer versão da definição e em qualquer chamada (P-2, FR-6102).
- Q: No Edital encerrado, as providências continuam? → A: **Sim** (P-3, FR-6117).
- Q: A advertência entra no relatório do Edital da `099`? → A: **Sim** (P-4, FR-6127).
- Q: O "Encerrar Processo" da `130` também adverte? → A: **Sim, pela mesma regra** (P-5, FR-6128).
- Q: Pela regra da `099`, um Edital encerrado com pendência ganha o relatório de acompanhamento, e o
  consolidado da unidade o conta entre os que têm providência em curso. A pendência da passagem ao setor
  conta também? → A: **Sim, conta como pendência** (D-009). Perguntada durante a implementação, quando a
  suíte mostrou o efeito.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A presidência sabe que falta definir os documentos (Priority: P1)

A presidência registra o aceite de Alice. Ao voltar ao Centro do Edital, o "O que fazer agora" mostra
uma ação dela: **"Definir os documentos que vão ao setor"**. A razão diz que uma pessoa está apta e que
nenhum documento foi definido. O link leva à tela da definição da `117`.

**Why this priority**: é a omissão mais cara do estudo. Sem definição, nenhum documento chega ao setor
(FR-3653 da `117`), e nada avisava.

**Independent Test**: num Edital com definição nunca gravada e uma pessoa apta, abrir o Centro como
presidência e conferir a providência e o link. Depois, gravar a definição e conferir que a providência
some.

**Acceptance Scenarios**:

1. **Given** um Edital publicado sem nenhuma versão da definição e duas pessoas aptas, **When** a
   presidência abre o Centro, **Then** o "O que fazer agora" mostra "Definir os documentos que vão ao
   setor" como ação dela, com a razão "2 pessoas aptas para formalização; nenhum documento definido
   para o setor", e o link leva à tela da definição.
2. **Given** o mesmo Edital, **When** quem tem `comissao:gerir` abre o Centro, **Then** a providência
   também é dele, com o mesmo link.
3. **Given** o mesmo Edital, **When** um avaliador abre o Centro, **Then** a providência aparece entre
   as de outro papel, como "Quem conduz a seleção: definir os documentos que vão ao setor", sem link.
4. **Given** a definição gravada, inclusive uma versão sem nenhum documento e com motivo, **When**
   qualquer papel abre o Centro, **Then** a providência de definir não aparece.
5. **Given** um Edital sem nenhuma pessoa apta, **When** a presidência abre o Centro, **Then** nenhuma
   providência desta spec aparece, mesmo com a definição vazia.

---

### User Story 2 — Fica visível que ninguém foi designado para receber (Priority: P1)

A definição está gravada e há pessoas aptas, mas ninguém está designado para o Edital. A providência
**"Designar quem recebe os documentos"** aparece:

- para quem administra os acessos da unidade, como ação dele, com o link da designação;
- para a presidência, como providência de outro papel, que nomeia quem o resolve.

**Why this priority**: sem designação efetiva, ninguém do setor alcança os documentos (FR-3664 da
`117`). No estudo, isso só se descobriu ao entrar como setor.

**Independent Test**: definição gravada, uma pessoa apta e nenhuma designação. Abrir o Centro como
presidência e como administrador de acessos.

**Acceptance Scenarios**:

1. **Given** definição gravada, uma pessoa apta e nenhuma designação vigente, **When** a presidência
   abre o Centro, **Then** aparece, entre as de outro papel, "Quem administra os acessos da unidade:
   designar quem recebe os documentos", com a razão "ninguém está designado para receber os
   documentos deste Edital" e sem link.
2. **Given** o mesmo Edital, **When** quem tem `acesso:gerir` na unidade do Edital abre o Centro,
   **Then** a providência é dele, com o link da designação para a formalização.
3. **Given** uma designação vigente só para o Perfil A e uma pessoa apta no Perfil B, **When**
   qualquer papel abre o Centro, **Then** a providência aparece com a razão "1 pessoa apta de Perfil
   sem designação". O Perfil não é nomeado (FR-6116).
4. **Given** uma designação vigente de quem perdeu o papel Formalização ou está suspenso, **When** o
   Centro é aberto, **Then** essa designação não conta como efetiva, e a providência aparece.
5. **Given** a definição nunca gravada, **When** o Centro é aberto, **Then** a providência de designar
   não aparece. Só aparece a de definir (FR-6106).

---

### User Story 3 — As pessoas aptas sem documentos disponibilizados contam como pendência (Priority: P1)

Com definição e designação em ordem, a providência **"Exportar os documentos das pessoas aptas"**
aparece como do setor da formalização, com a contagem de pessoas aptas cujos documentos ainda não
foram disponibilizados. Quando o setor gera o pacote que as inclui, a providência some.

**Why this priority**: é o terceiro passo, e o único que fecha a passagem.

**Independent Test**: definição gravada, designação efetiva e três pessoas aptas. Exportar uma pelo
setor e conferir a contagem antes e depois.

**Acceptance Scenarios**:

1. **Given** três pessoas aptas, definição gravada com documentos aplicáveis, designação efetiva e
   nenhum pacote gerado, **When** a presidência abre o Centro, **Then** aparece, entre as de outro
   papel, "O setor da formalização: exportar os documentos de 3 pessoas aptas", sem link.
2. **Given** um pacote gerado que inclui duas das três, **When** o Centro é aberto, **Then** a contagem
   é 1.
3. **Given** a definição nunca gravada, ou nenhuma designação efetiva para alguma pessoa, **When** o
   Centro é aberto, **Then** a providência de exportar conta só as pessoas que o setor já pode
   exportar. As demais estão nas providências de definir ou de designar, e nenhuma pessoa é contada
   duas vezes (FR-6106).
4. **Given** uma pessoa apta cujo Perfil não tem nenhum documento na definição vigente, **When** o
   Centro é aberto, **Then** ela não conta como pendente: não há o que disponibilizar (FR-6104).
5. **Given** uma pessoa incluída num pacote e depois desfechada de novo, ainda apta, numa chamada
   seguinte, **When** o Centro é aberto, **Then** ela segue a P-2.

---

### User Story 4 — O encerramento adverte sobre as pessoas aptas sem documentos disponibilizados (Priority: P1)

O Gestor abre a confirmação de encerrar o SIM09/2026. Além das advertências de hoje, lê sob "Continuam
depois do encerramento":

> **"2 pessoas aptas para formalização ainda não tiveram os documentos disponibilizados ao setor. A
> exportação continua possível depois do encerramento."**

A frase diz o que falta (definir, designar ou exportar). O caminho aparece só se a tela de destino
aceitar o Gestor; se não aceitar, a frase diz a quem pedir.

**Why this priority**: o estudo mostrou o Edital prestes a ser encerrado sem que nada falasse do setor
(`X06`).

**Independent Test**: num Edital com pessoas aptas pendentes, abrir a confirmação de encerrar e
conferir a advertência, a contagem e o caminho para cada papel.

**Acceptance Scenarios**:

1. **Given** duas pessoas aptas pendentes, **When** o Gestor abre a confirmação de encerrar, **Then** a
   advertência aparece sob "Continuam depois do encerramento", com a contagem e sem nome, CPF ou
   protocolo.
2. **Given** a advertência presente, **When** o Gestor confirma, **Then** o encerramento acontece. A
   advertência não impede.
3. **Given** nenhuma pessoa apta pendente, **When** a confirmação é aberta, **Then** a advertência não
   aparece, e a frase de "nada impede" da `113` segue a regra dela.
4. **Given** pendência por falta de definição e um Gestor que não pode gravá-la, **When** a confirmação
   é aberta, **Then** a frase diz que se peça a quem conduz a seleção, sem link.
5. **Given** um Edital encerrado com pessoas aptas pendentes, **When** o setor exporta depois do
   encerramento, **Then** a exportação acontece (FR-3710 da `117`), e o Centro deixa de contá-las.

---

### User Story 5 — A fase Conclusão diz onde termina a responsabilidade do GPS (Priority: P2)

A presidência abre a fase Conclusão. Além do que a `136` já diz, lê o bloco **"Disponibilizar ao
setor"**:

- quantas pessoas estão aptas;
- uma linha por passo: documentos definidos, quem recebe, pessoas disponibilizadas;
- a frase fixa: *"O GPS termina ao disponibilizar os documentos ao setor. A matrícula, a bolsa ou o
  contrato acontecem fora do GPS, e ele não registra o recebimento."*

Quando todas as pessoas aptas estão disponibilizadas, o bloco diz: *"Documentos de todas as 3 pessoas
aptas disponibilizados ao setor; o último pacote em 11/11/2026."*

**Why this priority**: dá forma à leitura certa, mas a pendência já aparece pelas US1 a US4.

**Independent Test**: abrir a fase Conclusão nas quatro situações (sem pessoas aptas, sem definição,
sem designação e tudo disponibilizado) e conferir o bloco.

**Acceptance Scenarios**:

1. **Given** nenhuma pessoa apta, **When** a fase Conclusão é aberta, **Then** o bloco não aparece.
2. **Given** pessoas aptas e definição vazia, **When** a fase é aberta, **Then** o bloco mostra três
   linhas: "Documentos que o setor recebe: não definidos", "Quem recebe: ainda depende da definição" e
   "Pessoas disponibilizadas: 0 de 2". Só a primeira tem ação, e só para quem pode praticá-la.
3. **Given** tudo disponibilizado, **When** a fase é aberta, **Then** o bloco diz isso com a data do
   último pacote. Ele não usa "encaminhado", "entregue", "recebido" nem "concluído" (FR-6123).
4. **Given** qualquer situação, **When** a fase é aberta, **Then** a frase do limite da
   responsabilidade aparece sempre que o bloco aparece.

---

### Edge Cases

- **Chamada nova de quem já foi disponibilizado.** Uma pessoa disponibilizada pode ter uma convocação
  seguinte e ficar apta de novo, por exemplo pela vaga que vagou. Se ela volta a contar depende da
  P-2.
- **A pessoa deixa de estar apta.** A aptidão vem do desfecho vigente da chamada mais recente
  (FR-3669 da `117`). Se ele muda, ela sai de toda contagem na leitura seguinte. Nada se grava.
- **Definição nova depois de um pacote.** A FR-3656 da `117` diz que a versão nova vale para as
  exportações seguintes, inclusive de quem já foi exportado. Se a pessoa volta a contar segue a P-2.
- **Documento indisponível ou com divergência de integridade.** A derivação não lê arquivo
  (FR-6105). A pessoa conta como pendente até um pacote incluí-la. A verificação da `117` é onde o
  setor descobre o arquivo faltante.
- **Download individual pelo setor.** O "Baixar" de um documento não gera registro de exportação
  (FR-3700 da `117`). Se ele conta como disponibilização segue a P-2.
- **Designação revogada depois do pacote.** Quem já foi disponibilizado continua disponibilizado. A
  revogação afeta só as pessoas pendentes, que voltam à providência de designar.
- **Ninguém na unidade tem o papel Formalização.** A designação seria recusada (FR-3663 da `117`). A
  providência de designar continua com quem administra os acessos, que concede o papel e depois
  designa. A razão diz isso (FR-6113).
- **Edital encerrado.** A exportação continua (FR-3710 da `117`), e as providências desta spec
  continuam enquanto houver pessoa apta pendente. Ver P-3.
- **Edital cancelado.** Esta spec não adverte no cancelamento, nem deriva providência num Edital
  cancelado. A `117` não diz se a formalização de um Edital cancelado continua. Fica registrado em
  "Fora de escopo".
- **Perfil pequeno.** As contagens são do Edital, nunca por Perfil, pela mesma proteção do relatório
  da `099` que a confirmação da `113` adota (FR-6116).
- **O setor abre o Centro.** Se o papel Formalização alcançar o detalhe do Edital, a providência de
  exportar é dele, com o link da página "Documentos para formalização". Se não alcançar, nada muda
  para ele (FR-6112).

---

## Requirements *(mandatory)*

### Functional Requirements

#### Os conjuntos

- **FR-6100**: As providências e a advertência desta spec MUST se aplicar só a Edital **publicado** ou
  **encerrado**. Não se aplicam ao cancelado, nem ao Edital antes da publicação.
- **FR-6101**: **Pessoa apta** MUST ser a da FR-3669 da `117`, lida na hora pelo mesmo critério da
  página do setor, e não por uma segunda definição.
- **FR-6102**: **Pessoa disponibilizada** MUST ser a pessoa apta que figura como *incluída* em ao menos
  um registro de exportação do Edital (FR-3700 da `117`). A leitura segue a P-2, cuja recomendação
  adotada é esta.
- **FR-6103**: **Definição gravada** MUST significar que existe ao menos uma versão da definição do
  Edital (FR-3655 da `117`), **inclusive uma versão sem nenhum documento**. Gravar sem documento, com
  motivo, é a decisão da condução de que o setor não precisa de documento deste Edital (D-003).
- **FR-6104**: **Pessoa sem documento a disponibilizar** MUST ser a pessoa apta cujo conjunto, com a
  definição gravada, não tem nenhum documento *incluído*, pelo seletor único da `117` (FR-3672 e
  FR-3674 da `117`). *Ajustada na implementação:* a primeira redação dizia "nenhum requisito
  aplicável", mas a pessoa com documento só *não apresentado* também não pode ser exportada, porque
  o pacote exige arquivo. Contá-la como "a exportar" daria ao setor uma providência impossível.
- **FR-6105**: A derivação MUST NOT ler arquivo do armazenamento, nem montar ou verificar o conjunto
  documental. Ela lê só registros: desfecho, definição, designação, papel, suspensão e exportação.
  Quem confere o arquivo é a verificação da `117`.
- **FR-6106**: **Pessoa pendente** MUST ser a pessoa apta que não está disponibilizada nem sem
  documento a disponibilizar. Cada pessoa pendente MUST estar em **exatamente uma** destas causas,
  nesta ordem:
  1. **sem definição** — a definição nunca foi gravada;
  2. **sem quem receba** — o Perfil dela não está coberto por nenhuma designação efetiva;
  3. **a exportar** — os demais casos.
- **FR-6107**: **Designação efetiva** MUST ser a designação vigente, isto é, não revogada (FR-3662 da
  `117`), de pessoa que tem o papel Formalização vigente na unidade do Edital e não está suspensa. É o
  mesmo critério que faz o predicado da FR-3664 da `117` ser verdadeiro para essa pessoa. A designação
  sem Perfis cobre todos os Perfis.

#### As providências do nível 1

- **FR-6108**: O nível 1 da `127` MUST ganhar até três providências, uma por causa com ao menos uma
  pessoa pendente:

  | Causa | Ato | Responsável |
  |---|---|---|
  | sem definição | **"Definir os documentos que vão ao setor"** | quem conduz a seleção (a presidência ou `comissao:gerir`, FR-3654 da `117`) |
  | sem quem receba | **"Designar quem recebe os documentos"** | quem administra os acessos da unidade (`acesso:gerir`, FR-3663 da `117`) |
  | a exportar | **"Exportar os documentos das pessoas aptas"** | o setor da formalização (designação efetiva) |

  O rótulo comum das três é **"Disponibilizar ao setor"** (P-1).
- **FR-6109**: Cada providência MUST ter a situação *Pendente*. Ela MUST NOT ter prazo: a `117` não
  fixa prazo para a passagem ao setor.
- **FR-6110**: A razão de cada providência MUST dizer a contagem da causa:
  - **sem definição**: "N pessoas aptas para formalização; nenhum documento definido para o setor";
  - **sem quem receba**, quando nenhuma designação é efetiva: "ninguém está designado para receber os
    documentos deste Edital";
  - **sem quem receba**, nos demais casos: "N pessoas aptas de Perfis sem designação";
  - **a exportar**: "N pessoas aptas ainda sem documentos disponibilizados".
- **FR-6111**: A providência MUST ser **da pessoa** quando ela pode praticar o ato na tela real:
  - **definir**: o predicado de gravar a definição da `117`;
  - **designar**: `acesso:gerir` na unidade do Edital;
  - **exportar**: designação efetiva do ator no Edital.
  
  Só então ela leva o link da tela do ato (FR-4084 da `127`, FR-4706 e FR-4707 da `136`). Para os
  demais, ela MUST nomear o papel e não ter link.
- **FR-6112**: A pessoa do setor só vê a providência de exportar como dela se o detalhe do Edital já a
  aceita. Esta spec MUST NOT abrir o Centro a quem só tem o papel Formalização (FR-3665 da `117`).
- **FR-6113**: Sem nenhuma pessoa com o papel Formalização vigente na unidade, a razão da providência
  de designar MUST acrescentar: "Antes, é preciso conceder o papel Formalização a alguém do setor".
- **FR-6114**: As três providências MUST entrar na ordem fixa da FR-4082 da `127`. Os dois papéis
  novos, *quem administra os acessos da unidade* e *o setor da formalização*, MUST ficar depois dos
  papéis de hoje, nesta ordem.
- **FR-6115**: As três providências MUST pertencer à fase **Conclusão** do Centro (D-002). Isso estende
  a regra de pertença da FR-4716 da `136`. A soma das providências das fases continua igual ao total do
  nível 1.
- **FR-6116**: Nenhuma providência, linha do bloco ou advertência desta spec MUST mostrar nome, CPF,
  protocolo, contato ou o nome do Perfil da pessoa. Só contagens do Edital (FR-4081 da `127`, FR-3540
  da `113`).
- **FR-6117**: As três providências MUST contar em "Onde estamos" como as demais (FR-4718 da `136`). O
  Edital com pessoa pendente MUST NOT ler "Seleção concluída. Nada em aberto." (P-3).

#### A fase Conclusão

- **FR-6118**: Com ao menos uma pessoa apta, a fase Conclusão consultada MUST mostrar o bloco
  **"Disponibilizar ao setor"**, com:
  - o total de pessoas aptas;
  - **Documentos que o setor recebe**: "não definidos", "definidos em DD/MM/AAAA" ou "nenhum
    documento, por decisão de DD/MM/AAAA";
  - **Quem recebe**: "ninguém designado", "N pessoas designadas", "N pessoas designadas; N pessoas
    aptas de Perfis sem designação" ou "ainda depende da definição";
  - **Pessoas disponibilizadas**: "X de Y", e, havendo pacote, a data do último.
  
  Os nomes de quem foi designado ficam onde já estão: a presidência os lê na tela da definição
  (FR-3668 da `117`). O bloco mostra contagens.
- **FR-6119**: Cada linha com causa em aberto MUST oferecer o ato da linha só a quem o pratica
  (FR-6111). Para os demais, ela nomeia o papel.
- **FR-6120**: O bloco MUST sempre trazer a frase do limite da responsabilidade: *"O GPS termina ao
  disponibilizar os documentos ao setor. A matrícula, a bolsa ou o contrato acontecem fora do GPS, e
  ele não registra o recebimento."*
- **FR-6121**: Com todas as pessoas aptas disponibilizadas ou sem documento a disponibilizar, o bloco
  MUST dizer *"Documentos de todas as N pessoas aptas disponibilizados ao setor; o último pacote em
  DD/MM/AAAA."* Quando a definição foi gravada sem documento, ele diz *"Nenhum documento vai ao setor
  neste Edital, por decisão de DD/MM/AAAA."*
- **FR-6122**: O andamento da fase Conclusão MUST continuar o da FR-4714 da `136` (D-005). O bloco
  e as providências não mudam se a fase está *Ainda não começou*, *Em curso* ou *Concluída*.
- **FR-6123**: Nenhum texto desta spec MUST usar "encaminhado", "entregue", "recebido", "obtido" ou
  "concluído" para dizer o que aconteceu com os documentos. O GPS afirma só o que ele fez: definiu,
  designou, gerou e disponibilizou (a decisão de terminologia da `117`).

#### A confirmação de encerrar

- **FR-6124**: Com ao menos uma pessoa pendente, a confirmação de encerrar o Edital MUST exibir, sob
  "Continuam depois do encerramento", a advertência *"N inscrições aptas para formalização ainda sem
  documentos disponibilizados ao setor (…)."* A advertência MUST NOT impedir o encerramento. *Ajustada
  na implementação:* a frase é **a do relatório, sem acréscimo**, porque a `130` exige a mesma frase
  (FR-4351 da `130`). Que a exportação continua já é o que o título do bloco diz. Diz "inscrições", e
  não "pessoas", porque a camada executiva do relatório não fala de pessoas (FR-2546 da `099`).
- **FR-6125**: A advertência MUST dizer a causa de cada parte, pelas contagens da FR-6106: "falta
  definir os documentos", "falta designar quem recebe" ou "falta o setor exportar". Com uma causa só,
  entre parênteses; com mais de uma, a contagem de cada uma.
- **FR-6126**: O caminho de cada causa MUST seguir a FR-3538 da `113`: o link vai só a quem a tela de
  destino aceita; para os demais, a frase diz a quem pedir, na forma canônica da `033`.
- **FR-6127**: A advertência MUST constar também do relatório do Edital da `099`, pela mesma regra.
  Assim continua verdadeira a frase da FR-3542 da `113`, segundo a qual o que aparece como advertência
  "consta do relatório do Edital" (P-4).
- **FR-6128**: A confirmação de "Encerrar Processo" da `130` MUST exibir a mesma advertência, Edital a
  Edital, pela regra da FR-4351 da `130` (P-5).

#### O que não muda

- **FR-6129**: Esta spec MUST NOT:
  - criar tabela, coluna, registro, evento de trilha ou estado por pessoa;
  - mudar a regra de "última exportação" (FR-3701 da `117`);
  - mudar quem define, quem designa ou quem exporta;
  - mudar o predicado da FR-3664 da `117`.
- **FR-6130**: As providências desta spec MUST NOT existir para Edital sem pessoa apta, ainda que a
  definição esteja vazia. O Edital que não chegou à formalização não ganha pendência.

### Requisitos de experiência

- **UX-560**: Os textos MUST seguir a linguagem simples da `069` e caber em 375 px, como os da `117`
  (FR-3680 da `117`).
- **UX-561**: O bloco "Disponibilizar ao setor" MUST ser uma lista de verificação: cada linha começa
  pelo estado, *feito* ou *em aberto*, em texto e não só em cor ou ícone.
- **UX-562**: O link da providência de definir MUST levar à tela da definição já com o foco nos
  documentos do Edital. A volta ao Centro segue a `139`.
- **UX-563**: O botão "Documentos para a formalização", em "Administração e histórico", MUST continuar
  onde está (FR-4088 da `127`). Esta spec não o remove: ele é o caminho de quem já sabe.

### Key Entities

Nenhuma entidade nova. A derivação lê só o que já existe:

- a **definição dos documentos para a formalização** (`117`): se existe versão e quais requisitos;
- a **designação para a formalização** e a **revogação dela** (`117`);
- o **vínculo** com o papel Formalização e a **suspensão** de pessoa (`107`);
- o **registro da exportação** (`117`): quem foi incluído;
- o **desfecho da convocação** (`115`): quem está apto.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1950**: Refeita a fase F do estudo no cenário C09, a presidência encontra a falta de definição
  pelo "O que fazer agora" **sem abrir "Administração e histórico"**, em todas as tentativas.
- **SC-1951**: Em toda combinação de definição (nunca gravada, gravada com documento, gravada sem
  documento), designação (nenhuma, parcial por Perfil, total, de quem perdeu o papel) e exportação
  (nenhuma, parcial, total), a soma das pessoas das três causas, mais as disponibilizadas e as sem
  documento, é igual ao total de pessoas aptas, e nenhuma pessoa é contada duas vezes.
- **SC-1952**: A contagem de pessoas pendentes é a mesma no nível 1, no bloco da fase Conclusão, na
  confirmação de encerrar e no relatório do Edital, lida no mesmo instante.
- **SC-1953**: Para cada papel (presidência, `comissao:gerir`, administrador de acessos, avaliador,
  Gestor e auditor), o link de cada providência aparece se, e só se, a tela de destino aceita aquela
  pessoa. A tela continua recusando quem não recebeu o link.
- **SC-1954**: Nenhuma tela desta spec exibe nome, CPF, protocolo ou nome de Perfil de pessoa apta. A
  varredura dos textos não encontra "encaminhad", "entregue", "recebid" nem "obtid" referidos aos
  documentos.
- **SC-1955**: A leitura do Centro faz o mesmo número de consultas com 1 e com 200 pessoas aptas, e
  nenhuma leitura de arquivo do armazenamento.
- **SC-1956**: O SIM09/2026 com pessoas pendentes, encerrado depois da advertência, continua permitindo
  ao setor exportar. Depois da exportação, o Centro deixa de contá-las.

---

## Proteção de dados (LGPD)

A spec não trata dado pessoal novo. Ela mostra contagens do Edital, como o nível 1 da `127` e a
confirmação da `113` já fazem. O nome do Perfil fica fora porque, com um Perfil pequeno, a contagem
identificaria a pessoa. A contagem de pacotes gerados já é lida pela presidência na tela da definição,
que mostra o histórico de exportações. Ninguém passa a ver o que não via.

---

## Assumptions

- A tela da definição da `117` (`/gestao/editais/<id>/formalizacao`) é a tela do ato de definir. A
  tela da designação da gestão de acessos (`/gestao/acessos/formalizacao`) é a de designar.
- O papel *quem conduz a seleção* da `127` coincide com a base de gerir a comissão, que é a que grava
  a definição (FR-3654 da `117`).
- O setor da formalização, hoje, não abre o detalhe do Edital. A providência de exportar aparece, na
  prática, como de outro papel. A spec não muda isso (FR-6112).
- A derivação cabe no orçamento de consultas do Centro, porque só lê registros (FR-6105). O plano
  confirma.

---

## Compatibilidade com regras anteriores

As revisões abaixo são **propostas**. Como na `117`, cada uma se aplica ao arquivo da feature de
origem na primeira tarefa da implementação, e só depois de aprovada.

| Regra | Feature | Revisão proposta |
|---|---|---|
| FR-4716 | `136` | acrescenta a natureza "formalização", que pertence à Conclusão (FR-6115) |
| FR-4082 | `127` | acrescenta os dois papéis novos ao fim da ordem dos grupos (FR-6114) |
| FR-3534 | `113` | acrescenta a advertência de pessoas aptas pendentes (FR-6124) |
| FR-4351 | `130` | acrescenta a mesma advertência ao "Encerrar Processo" (FR-6128, se a P-5 for sim) |
| as providências do relatório | `099` | acrescentam a mesma pendência (FR-6127), que conta para a espécie e para o consolidado da `100` (D-009) |

A FR-4714 da `136` não muda (D-005). A FR-3665 e a FR-3701 da `117` não mudam.

---

## Fora de escopo

- A confirmação de recebimento, o encaminhamento ativo e a integração com outro sistema (FR-3707 da
  `117`).
- A designação pela presidência (achado da `127`, não decidido).
- O papel Formalização no ambiente de demonstração (UX 06 do estudo).
- A contagem de pendências na página do setor (P-6).
- O cancelamento do Edital. A `117` não diz se a formalização de um Edital cancelado continua. Se a
  questão interessar, ela é de outra spec.
- Qualquer outro achado do estudo.

---

## Decisões

### D-001 — Três providências, um bloco

*Proposta.* A maquete 3 do estudo desenha uma fase "Encaminhar ao setor" com lista de verificação.
Esta spec a divide em dois lugares:

- **no nível 1**, três providências, porque cada passo tem um responsável distinto, e o nível 1 só
  marca como "sua" a ação de quem a pratica (FR-4084 da `127`). Uma providência única com três
  responsáveis não seria "sua" de ninguém;
- **na fase Conclusão**, um bloco que as junta como lista, porque ali o leitor quer ver o caminho
  inteiro.

**Rejeitado:** uma nona macrofase. A FR-4708 da `136` fixa oito fases, e a passagem ao setor não tem
pontos por lista: ela é do Edital.

### D-002 — Na fase Conclusão, e não na Convocação

*Proposta.* A pessoa fica apta na Convocação, mas a passagem ao setor é o que vem depois do desfecho.
A pergunta da Conclusão, "Tudo tem desfecho, e o Edital pode ser encerrado?", é exatamente onde o
estudo procurou. Pôr as providências na Convocação misturaria o ato da comissão sobre o candidato com
o ato sobre os documentos, que tem outros responsáveis.

### D-003 — A definição gravada sem documento é decisão, e não omissão

*Proposta.* A `117` aceita gravar a definição vazia com motivo. Se a providência de definir
persistisse depois disso, a condução não teria como dizer "este Edital não manda documento ao setor".
A versão gravada sem documento encerra a causa, e o bloco diz que foi uma decisão, com a data.

### D-004 — Uma pessoa, uma causa

*Proposta.* As causas se encadeiam: sem definição não se sabe o que exportar, e sem designação ninguém
exporta. Contar a mesma pessoa em mais de uma causa inflaria a soma e daria ao setor uma providência
que ele não pode cumprir. A ordem da FR-6106 põe cada pessoa na primeira causa que a prende. Por isso a
providência de exportar nunca fica *Impedida*: o que a impediria já é outra providência.

### D-005 — O andamento da Conclusão não muda

*Proposta.* A FR-4714 da `136` liga a Conclusão ao encerramento, e a FR-3710 da `117` diz que a
formalização sobrevive a ele. Fazer o andamento depender da exportação faria a fase *Concluída* do
Edital encerrado voltar a *Em curso* quando uma pessoa ficasse apta depois. O bloco e as providências
dizem o que falta sem mexer no andamento.

### D-006 — Independente da proposta de a presidência designar

*Proposta.* A providência de designar é de quem pode designar, pelo predicado da tela real (FR-6111).
Se a proposta registrada no achado da `127` for aprovada, a presidência passa a ter a providência como
dela sem que esta spec mude: muda o predicado, e a derivação o segue. Esta spec não decide nem
antecipa nada sobre a proposta.

### D-007 — Contagens do Edital, sem Perfil

*Proposta.* É a proteção que o relatório da `099` e a confirmação da `113` já usam. A presidência que
precisa saber qual Perfil está sem designação tem a tela da definição, onde as designações aparecem
com os Perfis (FR-3668 da `117`).

### D-008 — Sem leitura de arquivo

*Proposta.* O Centro é aberto muitas vezes por dia por vários papéis, e a verificação da `117` lê
cada arquivo. A derivação conta pela existência de registro, e não pela integridade do arquivo. O
arquivo indisponível aparece onde já aparece: na verificação, a quem exporta.

### D-009 — A passagem ao setor conta como pendência do relatório

**Decidida pelo usuário em 11/11/2026**, durante a implementação. Pela regra da `099`, o Edital
encerrado com pendência ganha o relatório *de acompanhamento*, e não o *de encerramento*. O
consolidado da unidade (`100`) também o conta entre os que têm providência em curso. A alternativa,
listar a passagem à parte sem mudar a espécie, foi recusada.

**Consequência nos testes anteriores.** Os cenários do relatório têm aceite e não tratam da
formalização. Eles passam a gravar a definição sem documento (`dispensar_a_formalizacao`), que é a
decisão de que nada vai ao setor, e continuam provando o que provavam.

## Perguntas para o usuário

**Respondidas pelo usuário em 11/11/2026**, todas na recomendação (ver Clarifications). Ficam aqui
como foram perguntadas, para a leitura do porquê.

- **P-1 — O nome: "Encaminhar ao setor" ou "Disponibilizar ao setor"?** O estudo e o pedido usam
  "Encaminhar ao setor". **A decisão de terminologia da `117`, aprovada em 04/11, recusou
  "encaminhado"**: o encaminhamento efetivo não tem mecanismo no GPS e, por isso, não tem palavra
  (FR-3699 da `117`). **Recomendação: "Disponibilizar ao setor"**, que é o que o GPS afirma. Manter
  "Encaminhar" reabre aquela decisão.
- **P-2 — O que conta como disponibilizada?** Recomendação: **estar incluída em algum pacote gerado do
  Edital**, em qualquer versão da definição e em qualquer chamada. Há três alternativas:
  1. contar também o download individual, que não tem registro de exportação, só evento de trilha;
  2. exigir um pacote sob a definição **vigente**, de modo que a pessoa volte a contar quando a
     definição muda;
  3. exigir um pacote **depois do desfecho vigente**, de modo que a pessoa reconvocada volte a contar.
  
  As alternativas 2 e 3 são mais exatas, e mais ruidosas: cada nova versão da definição reabriria
  todas as pessoas.
- **P-3 — No Edital encerrado, as providências continuam?** Recomendação: **sim**. A exportação
  continua possível (FR-3710 da `117`), e o "Seleção concluída. Nada em aberto." seria falso. A
  alternativa é silenciá-las no encerrado e confiar no relatório.
- **P-4 — A advertência entra no relatório do Edital da `099`?** Recomendação: **sim**. A confirmação
  da `113` diz que o que adverte "consta do relatório", e uma advertência que não constasse dele
  tornaria a frase falsa.
- **P-5 — O "Encerrar Processo" da `130` também adverte?** Recomendação: **sim, pela mesma regra**,
  como a `130` já faz com as demais providências da `113`.
- **P-6 — A página do setor ganha a contagem de pendentes?** A página "Formalização" lista os Editais
  da designação (FR-3675 da `117`) sem dizer em quais há pessoas a exportar. Seria a forma de a
  providência de exportar chegar a quem a pratica. Recomendação: **registrar como achado, fora desta
  spec**: ela muda a tela da `117`, e o pedido é sobre a jornada da condução.
- **P-7 — O cancelamento também adverte?** Recomendação: **não nesta spec**. Antes, é preciso decidir
  se a formalização de um Edital cancelado continua, o que a `117` não diz.
