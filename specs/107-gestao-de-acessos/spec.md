# Feature Specification: Gestão de acessos pela interface, verificável sem o Ifes

**Feature Branch**: `claude/107-gestao-de-acessos`, **empilhada** sobre a branch da `106`
(`claude/eloquent-wing-4d768b`, PR #345, em `8af15129`). Integra-se depois do #345, nunca antes.

**Created**: 2026-10-30

**Status**: Incremento 1 implementado nesta branch; merge não autorizado. As decisões que o
incremento 2 esperava foram tomadas pelo usuário em 30/10/2026 (§Decisões do usuário), e o
incremento 2 está **especificado, e não implementado** (US6 a US9, FR-3135 em diante).

**Input**: o pedido de 30/10/2026, "entregar uma experiência utilizável de gestão de acessos que se
possa desenvolver e verificar sem conexão real com a autenticação institucional do Ifes", sobre a
[`106`](../106-identidade-institucional-preparada/spec.md) e o roteiro de
[ativação do SSO](../../doc/ativacao-do-sso-institucional.md), §3 e §4.

> **Faixa de identificadores.** Esta spec abre em **FR-3101** e **SC-1011**. O teto medido em
> 30/10/2026 na `main` e nas branches abertas é o requisito três mil e trinta e um e o critério mil
> e seis, os dois da `106`. **Nenhum `UX-` é aberto aqui.** As decisões técnicas reiniciam em
> `D-001` e moram no `research.md`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-3012 da `106`"); decisão de outra feature pelo assunto e pelo número por extenso.

---

## Por que esta feature existe

A `106` deixou pronta a arquitetura: a pessoa com identificador interno estável, os vínculos
pessoa × unidade × papel, a concessão e a revogação na camada de aplicação, a sessão institucional
e um provedor simulado nos testes. Mas nada disso tem tela. Hoje, para alguém ganhar acesso, é
preciso abrir um `shell` no servidor; quem entra sem vínculo volta à página de acesso sem saber por
quê; a barra mostra `pessoa-1b4e…` no lugar do nome; a unidade ativa não tem botão de troca; e a
sessão institucional dura o que o padrão do framework disser.

Esta feature dá à gestão de acessos uma jornada pela interface, e a prova pelo navegador **sem o
Ifes**: com identidades fictícias, vínculos e respostas do provedor preparados pelo ambiente de
testes.

### O que foi reconferido em 30/10/2026, antes de especificar

| Item | Situação | Onde |
|---|---|---|
| PR #345 | aberto, sem revisão, CI verde em `8af15129` | GitHub |
| Achado 1 da revisão: retorno lia `estado` e não `state` | **corrigido** em `8af15129`, com teste de regressão | `seguranca/autenticacao.py`, `estado_do_retorno`; `test_entrada_institucional.py::test_o_retorno_le_o_state_do_protocolo_e_nao_o_nome_interno` |
| Achado 2: dois primeiros administradores institucionais simultâneos | **corrigido** em `8af15129`, com trava de transação e teste concorrente | `seguranca/application/acessos.py`; `test_concorrencia.py::test_duas_primeiras_administracoes_simultaneas_gravam_uma_so` |
| Concessão e revogação com as recusas da `106` | **capacidade existente**, sem tela | `seguranca/application/acessos.py` |
| Leitura dos vínculos vigentes da unidade | **capacidade existente** (`acesso:consultar`), sem tela | idem, `vinculos_vigentes_da_unidade` |
| Troca da unidade ativa | **capacidade existente**, rota sem botão | `POST /gestao/unidade-ativa` |
| Quem é o administrador institucional; quem concede na unidade; qual identificador do provedor | **propostas** da `106` no início desta spec; **decididas** pelo usuário em 30/10 (§Decisões do usuário) | spec da `106`, §Propostas ao usuário |
| Tempos de sessão (8 h e 30 min) | **proposta** no início desta spec; **decididos** em 30/10 (P4) | `doc/ativacao-do-sso-institucional.md`, §1, decisão 5 |
| Suspensão de pessoa; retirada do administrador institucional | **inexistentes**; decididas em 30/10 (P1 a P3), e especificadas no incremento 2 | idem, §4 |

Os dois achados não reaparecem como requisito aqui: a `107` não reabre a `106`, e os testes de
regressão deles continuam na suíte (`SC-1015`).

### O que esta spec cobre, e o que fica fora

**Incremento 1 — entra agora.** Cada item é uma jornada pela interface:

1. **Sem acesso**: quem entra pelo provedor e não tem acesso vigente vê o próprio nome, o que falta
   e a quem pedir.
2. **A barra com o nome e a unidade ativa**, e a troca de unidade por um botão.
3. **Acessos da unidade**: consultar quem atua na unidade, conceder e revogar papéis operacionais,
   com busca de pessoas, confirmação e motivo, e o histórico das alterações.
4. **Administração de acessos das unidades**: o mesmo para o administrador de acessos de cada
   unidade, no nível institucional.
5. **Prazo da sessão institucional**: duração máxima e encerramento por inatividade, com valores
   declarados por ambiente.
6. **A jornada pelo navegador nos testes**, com servidor, identidades, vínculos e respostas do
   provedor preparados pelo ambiente de testes.

**Incremento 2 — especificado, não implementado** (US6 a US9). As decisões que ele esperava foram
tomadas em 30/10:

- suspensão e reativação de pessoa, global, com motivo, trilha e fim de todas as sessões (US6, US7);
- retirada e substituição da administração institucional, pelo comando de implantação (US8);
- o nome da pessoa nas demais telas que exibem o `subject` (históricos da comissão, da trilha, do
  Edital) (US9).

**Fora**: conexão real com AD/LDAP ou outro provedor; escolha do protocolo; credenciais reais;
abertura da gestão em produção; a API; mudança nas regras de segregação do certame (a emenda à
FR-021 da `001` continua fora); a comissão apontando para pessoa.

---

## Clarifications

### Session 2026-10-30

Respostas tiradas do pedido e do repositório — nenhuma é decisão institucional nova.

- Q: Quem concede e revoga em cada nível? → A: O que a `106` implementou, sem mudar: papel
  operacional por quem tem `acesso:gerir` na unidade; o Administrador de acessos da unidade por quem
  tem `acesso:administrar` no escopo institucional; o Administrador institucional só pelo comando
  de implantação. As telas pedem a **capacidade**, e não o papel: se o usuário decidir que o Gestor
  concede (proposta 3 da `106`), nenhuma tela muda.
- Q: O seletor de demonstração ganha os papéis de acesso, para que a homologação manual alcance as
  telas novas? → A: Não. O pedido exige o seletor com os mesmos oito papéis (FR-3001 da `106`). As
  telas novas são do modo institucional, e a demonstração delas é a jornada pelo navegador do
  ambiente de testes (`FR-3131`). A homologação manual continua como hoje e **não** alcança as telas
  de acessos — é a incompatibilidade entre demonstração e restrições, resolvida aqui, antes do
  plano.
- Q: Um provedor fictício de execução, para o navegador entrar fora dos testes? → A: Não. O pedido o
  proíbe, e o provedor simulado da `106` continua só no código de teste.
- Q: Quem a busca de pessoas alcança? → A: Quem já entrou pelo provedor ao menos uma vez e está
  ativo — é o único universo que o sistema conhece, sem diretório integrado. Quem nunca entrou não
  existe para o sistema; o primeiro vínculo começa por a pessoa entrar uma vez e ver a tela sem
  acesso (`FR-3101`).
- Q: Os tempos de sessão? → A: São decisão do usuário. O mecanismo entra agora, com os valores
  lidos da configuração; fora de produção o padrão é a proposta (8 h e 30 min), marcada como
  proposta; produção recusa subir sem os dois declarados (`FR-3124`).

### Session 2026-10-30 (respostas do usuário)

Decisões de governança, do usuário, em resposta ao PR #346. Registradas aqui como foram dadas; o
detalhe está em §Decisões do usuário.

- Q: P1, a suspensão? → A: **C** — os dois mecanismos: a suspensão global da pessoa e a revogação
  dos vínculos de uma unidade. O administrador institucional suspende pessoas; a suspensão do
  administrador institucional é da implantação. Suspender exige motivo, trilha e o fim de todas as
  sessões existentes.
- Q: P2, a reativação? → A: **A** — a suspensão interrompe sem desfazer vínculos; ao reativar,
  voltam a valer os ainda vigentes, e os revogados continuam revogados. A confirmação mostra os
  acessos que voltarão a valer. Nenhuma sessão anterior volta a funcionar, mesmo que a pessoa não
  tenha feito requisição durante a suspensão.
- Q: P3, a administração institucional? → A: **A** — pelo comando de implantação, com motivo e
  trilha. A substituição concede ao novo responsável e revoga o anterior numa operação só.
- Q: P4, os tempos? → A: **8 horas** de duração máxima e **30 minutos** de inatividade, declarados
  expressamente na configuração de produção; ajustes posteriores são documentados.
- Q: Proposta 1 da `106`, o identificador externo? → A: o identificador estável do provedor,
  associado ao emissor — em OIDC, `iss` + `sub`. Nome e e-mail não determinam a associação. Os
  atos continuam com o identificador interno.
- Q: Proposta 2 da `106`, o administrador institucional? → A: **duas pessoas** nominalmente
  designadas por ato formal, com contas individuais, e a referência ao ato na concessão.
- Q: Proposta 3 da `106`, quem concede na unidade? → A: o papel próprio de Administrador de acessos
  da unidade, separado do Gestor; a mesma pessoa pode acumular os dois por concessões explícitas.
- A ativação em produção e o merge continuam sujeitos às autorizações próprias.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem entra sem acesso sabe onde está (Priority: P1)

Uma servidora entra pela primeira vez com a conta institucional. Ela não tem vínculo em unidade
nenhuma. Em vez de voltar à página de acesso, como hoje, ela vê o próprio nome e e-mail, a frase
de que não tem acesso vigente em nenhuma unidade, e a quem pedir. Pode sair.

**Why this priority**: é o primeiro passo de toda concessão. Sem ele a pessoa não sabe que entrou,
e o administrador não a encontra na busca.

**Independent Test**: com o provedor simulado, uma pessoa sem vínculo entra e vê a tela sem acesso,
com o nome dela; nenhuma tela da gestão a atende.

**Acceptance Scenarios**:

1. **Given** uma pessoa sem vínculo nenhum, **When** entra pelo provedor, **Then** vê a tela sem
   acesso, com o nome e o e-mail que o provedor informou, e a quem pedir.
2. **Given** a mesma pessoa, **When** abre qualquer endereço da gestão, **Then** volta à tela sem
   acesso.
3. **Given** uma pessoa cujo vínculo na unidade ativa foi revogado, e que tem vínculo em outra,
   **When** faz a requisição seguinte, **Then** vê a tela sem acesso com as unidades em que ainda
   atua, e troca para uma delas por um botão.
4. **Given** a tela sem acesso, **When** ela sai, **Then** a sessão é encerrada.

---

### User Story 2 — O nome e a unidade ativa na barra (Priority: P1)

A pessoa institucional vê na barra o próprio nome, e não o identificador interno, e a unidade em
que está atuando. Se atua em mais de uma — ou no escopo institucional —, troca por um seletor na
barra, e passa a ter só as permissões da escolhida.

**Why this priority**: sem o nome, a gestão é ilegível no modo institucional; sem a troca, quem
atua em duas unidades fica preso na primeira.

**Independent Test**: uma pessoa com vínculos no `cefor` e no `campus-a` vê o nome dela e o seletor;
troca pelo seletor e perde, na tela seguinte, o que só tinha no `cefor`.

**Acceptance Scenarios**:

1. **Given** uma pessoa institucional, **When** abre a gestão, **Then** a barra mostra o nome dela e
   a unidade ativa.
2. **Given** vínculos em duas unidades, **When** escolhe a outra no seletor, **Then** as permissões
   são as da escolhida, e nenhuma da anterior.
3. **Given** vínculo numa unidade só, **When** abre a gestão, **Then** não há seletor.
4. **Given** uma sessão de demonstração, **When** abre a gestão, **Then** a barra é a de hoje.

---

### User Story 3 — Acessos da unidade (Priority: P1)

O administrador de acessos do `cefor` abre "Acessos da unidade". Vê quem atua no `cefor`, com que
papel, desde quando e por concessão de quem. Concede: busca a pessoa pelo nome ou e-mail, escolhe o
papel, confere numa tela de confirmação a pessoa, a unidade, o papel, o que o papel permite e a
consequência, informa o motivo e confirma. Revoga: escolhe o vínculo, confere, informa o motivo e
confirma. O histórico mostra cada concessão e cada revogação, com quem, quando e por quê.

**Why this priority**: é a jornada que substitui o `shell` do servidor.

**Independent Test**: pela tela, uma concessão e uma revogação produzem o vínculo, a revogação e os
dois eventos de trilha; a pessoa de destino ganha e perde a permissão na requisição seguinte.

**Acceptance Scenarios**:

1. **Given** o administrador de acessos do `cefor`, **When** busca uma pessoa que já entrou, escolhe
   Elaborador e confirma com motivo, **Then** o vínculo nasce, a trilha o registra, e a pessoa passa
   a elaborar na requisição seguinte.
2. **Given** a tela de confirmação, **When** o motivo está vazio, **Then** nada é gravado e a tela
   diz o que falta.
3. **Given** a tela de confirmação, **When** ele cancela, **Then** nada é gravado.
4. **Given** um vínculo vigente, **When** o revoga com motivo, **Then** a pessoa perde a permissão na
   requisição seguinte — inclusive com a sessão dela aberta —, e nenhum caminho pela comissão a
   devolve.
5. **Given** a busca, **When** ele procura o próprio nome, **Then** ele não aparece; e **When** monta
   à mão o envio de concessão para si, **Then** a recusa é a da autoconcessão.
6. **Given** a busca, **When** o termo tem menos de três caracteres, **Then** nada é listado.
7. **Given** um vínculo do `campus-a`, **When** ele monta à mão a revogação dele, **Then** a resposta
   é "não encontrado".
8. **Given** uma pessoa sem `acesso:gerir`, **When** abre "Acessos da unidade", **Then** a recusa diz
   o que falta, e a barra não oferecia o item.

---

### User Story 4 — Administração de acessos das unidades (Priority: P2)

A administradora institucional troca para "Administração institucional" no seletor e abre
"Administração de acessos". Vê, por unidade, quem é administrador de acessos. Concede a uma pessoa
o Administrador de acessos de uma unidade, e revoga, com a mesma busca, confirmação e motivo. Não
vê nem altera os papéis operacionais das unidades.

**Why this priority**: sem ela, o primeiro administrador de cada unidade ainda nasce pelo `shell`.

**Independent Test**: pela tela, a administradora institucional concede o Administrador de acessos
do `cefor` a uma pessoa, que passa a ver "Acessos da unidade" na requisição seguinte.

**Acceptance Scenarios**:

1. **Given** a administradora institucional no escopo institucional, **When** concede o
   Administrador de acessos do `cefor` com motivo, **Then** o vínculo nasce e a trilha o registra.
2. **Given** a mesma, **When** tenta pela tela conceder a si mesma, **Then** é recusada.
3. **Given** a mesma, **When** monta à mão uma concessão de papel operacional, **Then** é recusada.
4. **Given** o administrador de acessos de uma unidade, **When** abre a administração
   institucional, **Then** a recusa diz o que falta.

---

### User Story 5 — A sessão institucional tem prazo (Priority: P2)

A sessão institucional termina por duração máxima, contada da entrada, e por inatividade, contada
da última ação da pessoa na gestão. Ao terminar, a pessoa volta à página de acesso, que diz por quê.

**Why this priority**: é condição da implantação, e o mecanismo não depende da decisão dos valores.

**Independent Test**: com o relógio fixado pelo teste, a sessão vale até o limite e cai depois dele,
nas duas contagens.

**Acceptance Scenarios**:

1. **Given** uma sessão aberta há mais que a duração máxima, **When** a pessoa age, **Then** a
   sessão cai, mesmo com atividade constante.
2. **Given** uma sessão sem ação há mais que o limite de inatividade, **When** a pessoa volta,
   **Then** a sessão cai, e a página de acesso diz que foi por inatividade.
3. **Given** uma requisição que a interface declara automática, **When** chega, **Then** não conta
   como atividade.
4. **Given** uma sessão de demonstração, ou a do portal do candidato, **When** passa o mesmo tempo,
   **Then** nada muda para ela.

---

### User Story 6 — Suspender uma pessoa em todas as unidades (Priority: P1, incremento 2)

A administradora institucional precisa tirar alguém do sistema agora — uma conta comprometida, um
afastamento. Em "Administração de acessos", busca a pessoa, escolhe "Suspender", confere quais
acessos param de valer e que todas as sessões dela terminam, informa o motivo e confirma. A pessoa
perde o acesso em todas as unidades na requisição seguinte, em qualquer navegador; os vínculos dela
não são revogados.

**Why this priority**: é o caso urgente que a revogação unidade por unidade não atende.

**Independent Test**: com duas sessões abertas da pessoa, a suspensão pela tela as encerra as duas,
e nenhum vínculo ganha revogação.

**Acceptance Scenarios**:

1. **Given** uma pessoa com vínculos no `cefor` e no `campus-a` e duas sessões abertas, **When** a
   administradora institucional a suspende com motivo, **Then** as duas sessões terminam na
   requisição seguinte, a suspensão vai à trilha, e os vínculos continuam sem revogação.
2. **Given** a pessoa suspensa, **When** ela tenta entrar pelo provedor, **Then** a entrada é recusada
   com a frase de que o acesso está suspenso e a quem pedir.
3. **Given** a pessoa suspensa, **When** um administrador de unidade tenta conceder a ela, **Then** é
   recusado, e a busca não a mostra.
4. **Given** a administradora institucional, **When** tenta suspender a si mesma ou outra
   administradora institucional pela tela, **Then** é recusada: isso é da implantação.
5. **Given** a implantação, **When** suspende uma administradora institucional pelo comando, com
   motivo, **Then** a suspensão vale como a da tela, e vai à trilha sob o ator de implantação.

---

### User Story 7 — Reativar sem devolver o que não devia (Priority: P1, incremento 2)

A administradora institucional reativa uma pessoa suspensa. A confirmação mostra os acessos que
voltarão a valer — os vínculos ainda vigentes — e diz que os revogados continuam revogados e que
nenhuma sessão anterior volta. A pessoa precisa entrar de novo.

**Why this priority**: a suspensão é temporária, e a reativação precisa ser previsível.

**Independent Test**: uma sessão aberta antes da suspensão, sem nenhuma requisição durante ela, não
vale depois da reativação; uma entrada nova vale, com os vínculos que estavam vigentes.

**Acceptance Scenarios**:

1. **Given** uma pessoa suspensa com Elaborador vigente no `cefor` e Gestor revogado durante a
   suspensão, **When** é reativada, **Then** volta a ter Elaborador, e não Gestor.
2. **Given** uma sessão aberta antes da suspensão e não usada durante ela, **When** a pessoa é
   reativada e o navegador volta a usar a sessão, **Then** ela não vale.
3. **Given** a confirmação da reativação, **When** a administradora a abre, **Then** vê, por unidade,
   cada papel que voltará a valer.
4. **Given** duas reativações simultâneas da mesma suspensão, **When** chegam, **Then** uma vale e a
   outra é recusada.

---

### User Story 8 — Retirar e substituir a administração institucional (Priority: P2, incremento 2)

Quem implanta retira a administração institucional de uma pessoa, ou a substitui por outra, pelo
comando, com o ato que o determina como motivo. A substituição concede à nova pessoa e revoga a
anterior numa operação só.

**Why this priority**: fecha a lacuna da `106` — hoje não há como retirar esse acesso.

**Independent Test**: a substituição grava a concessão e a revogação na mesma transação; se uma
falha, nenhuma é gravada.

**Acceptance Scenarios**:

1. **Given** uma administradora institucional vigente, **When** a implantação a substitui por outra
   pessoa com motivo, **Then** a nova tem o papel, a anterior não, e a trilha tem os dois eventos.
2. **Given** a substituição para quem já é administradora institucional, **When** o comando roda,
   **Then** é recusada e nada muda.
3. **Given** a retirada pelo comando, com motivo, **When** roda, **Then** o vínculo ganha revogação e
   a pessoa perde a administração na requisição seguinte.

---

### User Story 9 — O nome nas demais telas (Priority: P3, incremento 2)

As telas que mostram quem praticou um ato — históricos da comissão, da trilha, do Edital, da
distribuição — mostram o nome da pessoa institucional, e não `pessoa-<uuid>`. A demonstração
continua mostrando o identificador escolhido no seletor.

**Why this priority**: a gestão é ilegível no modo institucional sem isso; não bloqueia acesso.

**Independent Test**: com atos praticados por uma pessoa institucional, cada tela que exibia o
identificador exibe o nome, e o identificador continua nos registros.

---

### Edge Cases

- **A busca acha mais de dez pessoas**: mostra dez e pede para refinar; não pagina.
- **A pessoa escolhida foi desativada entre a busca e a confirmação**: a concessão é recusada.
- **Dois administradores concedem o mesmo papel à mesma pessoa ao mesmo tempo**: um vale, o outro
  recebe "já vigente" (a regra da `106`), e a tela o diz.
- **Dois revogam o mesmo vínculo ao mesmo tempo**: um vale, o outro recebe "já revogado".
- **A confirmação é reenviada (voltar e enviar de novo)**: a segunda é recusada como já vigente ou
  já revogado; nada se duplica.
- **O administrador perde `acesso:gerir` entre abrir a confirmação e confirmar**: a confirmação é
  recusada.
- **A unidade ativa deixa de ter vínculo da pessoa no meio da sessão**: a requisição seguinte vai à
  tela sem acesso (cenário 3 da US1).
- **Uma unidade sem nome registrado**: aparece pelo código.
- **A pessoa sem nome informado pelo provedor**: aparece pelo e-mail; sem os dois, por "pessoa sem
  nome informado" — nunca pelo identificador interno.
- **O administrador institucional também atua numa unidade**: entra nela (FR-3019 da `106`) e troca
  para o institucional pelo seletor.
- **Sessão de demonstração abre o endereço de "Acessos da unidade"**: recusada; a demonstração não
  tem as capacidades de acesso.

---

## Requirements *(mandatory)*

### Functional Requirements

**Sem acesso e barra**

- **FR-3101**: Quem tem sessão institucional sem acesso vigente na unidade ativa MUST ver a tela
  sem acesso, com o próprio nome e e-mail, a frase de que não tem acesso vigente e a quem pedi-lo, e
  a saída. Toda porta da gestão MUST levá-lo a ela, e não à página de acesso.
- **FR-3102**: Na tela sem acesso, se a pessoa tiver acesso vigente em outro escopo, MUST oferecer a
  troca para cada um deles. A tela MUST NOT revelar nada além disso — nem papéis, nem quem
  concedeu.
- **FR-3103**: No modo institucional, a barra e a página de acesso MUST mostrar o nome da pessoa (ou
  o e-mail, ou "pessoa sem nome informado"), e MUST NOT mostrar o identificador interno. A trilha e
  os registros continuam gravando o identificador interno.
- **FR-3104**: A barra MUST mostrar a unidade ativa da pessoa institucional e, se ela tiver acesso
  vigente em mais de um escopo, um seletor com cada um, pelo nome; o escopo institucional, como
  "Administração institucional". A troca MUST valer só para escopo com acesso vigente (FR-3019 da
  `106`).
- **FR-3105**: No modo demonstração, a barra e a página de acesso MUST continuar exatamente as de
  hoje.

**Acessos da unidade**

- **FR-3106**: A tela de acessos da unidade MUST exigir `acesso:consultar` na unidade ativa, e MUST
  listar só os vínculos vigentes daquela unidade: pessoa (nome e e-mail), papel, desde quando e quem
  concedeu (pelo nome).
- **FR-3107**: O histórico da unidade MUST listar as concessões e revogações dela, mais recentes
  primeiro, com quem, quando e o motivo, lidos dos próprios vínculos e revogações — e nunca de
  outra unidade.
- **FR-3108**: Conceder MUST exigir `acesso:gerir` na unidade ativa, e MUST oferecer os papéis
  operacionais (os oito do catálogo e o Integrante da unidade), com o que cada um permite em
  palavras. Os papéis de acesso MUST NOT ser oferecidos ali.
- **FR-3109**: A concessão MUST ser feita na unidade ativa do ator, e a unidade MUST NOT vir do
  formulário.
- **FR-3110**: Revogar MUST partir de um vínculo vigente listado, e o vínculo MUST ser procurado só
  entre os da unidade ativa: de outra unidade, ou inexistente, responde "não encontrado".
- **FR-3111**: A tela MUST oferecer revogar só os vínculos que o ator tem autoridade de revogar
  (as regras da `106`); o servidor MUST recusar os demais de qualquer modo.

**Busca de pessoas**

- **FR-3112**: A busca MUST exigir, no escopo ativo, a capacidade de conceder do nível da tela —
  `acesso:gerir` na unidade, ou `acesso:administrar` no institucional —, conferida no servidor
  antes de consultar.
- **FR-3113**: A busca MUST exigir termo de ao menos três caracteres, MUST procurar no nome e no
  e-mail, e MUST devolver no máximo dez pessoas, ordenadas pelo nome, dizendo quando houver mais.
- **FR-3114**: A busca MUST alcançar só pessoas institucionais ativas, e MUST NOT incluir o próprio
  ator. Cada resultado MUST mostrar só nome e e-mail — nem o identificador interno, nem o do
  provedor, nem os vínculos que a pessoa tem em outra unidade.
- **FR-3115**: O termo da busca MUST NOT ir ao endereço da página.

**Confirmação, motivo e trilha**

- **FR-3116**: Toda concessão e toda revogação pela tela MUST passar por uma tela de confirmação que
  mostra pessoa, unidade, papel, alcance (o que o papel permite) e consequência — quando passa a
  valer, e que o registro não se apaga — antes de gravar. Nada MUST ser gravado antes da confirmação.
- **FR-3117**: A confirmação MUST exigir motivo; sem ele, MUST recusar sem gravar e voltar à mesma
  confirmação dizendo o que falta.
- **FR-3118**: A confirmação MUST reconferir no servidor tudo o que a primeira etapa conferiu —
  capacidade, escopo, pessoa ativa, autoconcessão, vínculo já vigente ou já revogado —, e MUST
  dizer na tela a recusa do domínio.
- **FR-3119**: A gravação e o evento de trilha MUST ser da mesma transação (as funções da `106`), e
  a tela MUST NOT gravar por outro caminho.

**Administração institucional**

- **FR-3120**: A tela de administração de acessos MUST exigir `acesso:administrar` no escopo
  institucional, e MUST listar, por unidade registrada e ativa, os administradores de acessos
  vigentes.
- **FR-3121**: Ela MUST conceder e revogar só o Administrador de acessos da unidade, numa unidade
  registrada e ativa escolhida da lista, com a mesma busca, confirmação e motivo; MUST NOT oferecer
  nem aceitar papel operacional nem o Administrador institucional.

**Sessão institucional**

- **FR-3122**: A sessão institucional MUST terminar quando passar a duração máxima contada do
  instante da entrada, com ou sem atividade. A troca de unidade MUST NOT renová-la.
- **FR-3123**: A sessão institucional MUST terminar quando passar o limite de inatividade contado da
  última requisição da pessoa à gestão que não seja declarada automática. Requisições fora da
  gestão e as declaradas automáticas MUST NOT contar como atividade.
- **FR-3124**: Os dois limites MUST vir da configuração do ambiente. Fora de produção, sem
  declaração, valem 8 horas e 30 minutos — a proposta do início desta spec, que o usuário adotou
  em 30/10 (P4). Produção com provedor institucional MUST recusar subir sem os dois declarados,
  como a decisão manda.
- **FR-3125**: O término por prazo MUST encerrar a sessão como a saída (FR-3020 da `106`), ir à
  trilha com o motivo, e a página de acesso MUST dizer por que a sessão terminou.
- **FR-3126**: Os prazos MUST NOT alcançar a sessão de demonstração nem a identidade do portal do
  candidato.

**Segurança das telas**

- **FR-3127**: As telas de acessos MUST exigir sessão institucional, além da capacidade: a
  demonstração não as alcança por caminho nenhum.
- **FR-3128**: A barra MUST oferecer cada tela nova só a quem tem a capacidade dela, e a recusa no
  servidor MUST valer com o link ausente.
- **FR-3129**: Nenhuma tela nova MUST ler identidade de cabeçalho, parâmetro ou corpo além do que a
  sessão institucional já resolve, e a pessoa de destino MUST ser lida de um identificador que o
  servidor reconfere — nunca digitado.
- **FR-3130**: As telas novas MUST cumprir a política de conteúdo (sem estilo nem script embutidos).

**Demonstração sem o Ifes**

- **FR-3131**: As jornadas das US1 a US5 MUST ser verificadas por testes de navegador, com servidor,
  identidades, vínculos e respostas do provedor preparados pelo ambiente de testes; a entrada MUST
  atravessar a ida ao provedor e o retorno pela aplicação. Durante as ações, nenhum passo usa shell,
  edição de sessão ou manipulação do banco; as verificações das consequências vêm depois.
- **FR-3132**: A jornada pelo navegador MUST poder ser assistida por uma pessoa, com o navegador
  visível, a partir de um comando só.
- **FR-3133**: A documentação MUST separar o roteiro manual da homologação (seletor, oito papéis,
  sem telas de acesso) do roteiro do navegador do ambiente de testes, e MUST NOT prometer
  demonstração manual institucional.

**Preservação**

- **FR-3134**: A feature MUST NOT criar tabela nem migration, MUST NOT mudar o seletor de
  demonstração, e MUST NOT alterar as regras de concessão da `106` além de recusar pessoa inativa.

### Functional Requirements — incremento 2 (especificados, não implementados)

O `FR-3134` vale para o incremento 1. O incremento 2 cria duas tabelas append-only e uma migration
(`FR-3149`).

**Suspensão (P1, decisão C)**

- **FR-3135**: A suspensão MUST ser global: a pessoa suspensa MUST NOT ter ator em escopo nenhum, e
  MUST NOT entrar pelo provedor, até ser reativada. A revogação por unidade continua existindo ao
  lado dela, sem mudança.
- **FR-3136**: Suspender e reativar pela tela MUST exigir `acesso:administrar` no escopo
  institucional. A tela MUST recusar suspender ou reativar o próprio ator e qualquer pessoa com
  Administrador institucional vigente.
- **FR-3137**: A suspensão e a reativação de quem tem Administrador institucional vigente MUST ser
  feitas só pelo comando de implantação, com motivo, sob o ator de implantação. O comando MUST
  servir também a qualquer outra pessoa.
- **FR-3138**: Suspender MUST exigir motivo, MUST ir à trilha na mesma transação, e MUST encerrar
  **todas** as sessões existentes da pessoa, em qualquer navegador, na requisição seguinte de cada
  uma.
- **FR-3139**: A suspensão MUST NOT revogar vínculo nenhum. Os vínculos da pessoa suspensa continuam
  vigentes e inertes, e a tela de acessos da unidade MUST mostrá-los com a marca de suspensa.
- **FR-3140**: A pessoa suspensa MUST NOT aparecer na busca e MUST NOT receber vínculo novo.
- **FR-3141**: A pessoa suspensa que tenta entrar MUST ver que o acesso está suspenso e a quem
  pedir, sem o motivo nem quem suspendeu.
- **FR-3142**: A confirmação da suspensão MUST mostrar a pessoa, cada acesso que deixará de valer, e
  que todas as sessões terminam.

**Reativação (P2, decisão A)**

- **FR-3143**: Reativar MUST exigir motivo, MUST ir à trilha, e MUST devolver só a possibilidade de
  entrar: voltam a valer os vínculos ainda vigentes, e os revogados — antes ou durante a suspensão —
  continuam revogados.
- **FR-3144**: Nenhuma sessão aberta antes da suspensão MUST voltar a valer depois da reativação,
  mesmo que não tenha feito requisição nenhuma durante a suspensão.
- **FR-3145**: A confirmação da reativação MUST mostrar, por unidade, cada papel que voltará a
  valer, e dizer que a pessoa precisa entrar de novo.
- **FR-3146**: Suspender quem já está suspenso e reativar quem não está MUST ser recusados, também
  sob concorrência.

**Administração institucional (P3, decisão A; proposta 2 da `106`)**

- **FR-3147**: Um comando de implantação MUST retirar a administração institucional de uma pessoa,
  com motivo, revogando o vínculo sob o ator de implantação.
- **FR-3148**: Um comando de implantação MUST substituir a administração institucional de uma
  pessoa por outra numa transação só: a revogação da anterior e a concessão à nova, as duas na
  trilha com o mesmo motivo; recusada uma, nenhuma é gravada. A nova MUST NOT já ter o papel, e a
  anterior MUST tê-lo vigente.
- **FR-3149**: A suspensão e a reativação MUST ser registros próprios, append-only nas duas camadas
  (gatilho e privilégio ausente), uma reativação no máximo por suspensão. A migration MUST só criar
  essas tabelas.

**O nome nas demais telas**

- **FR-3150**: Toda tela da gestão que exibe o `subject` de quem praticou um ato MUST exibir, para
  pessoa institucional, o nome (ou o e-mail, ou "pessoa sem nome informado"); para identidade de
  demonstração, o próprio `subject`, como hoje. Os registros continuam com o identificador interno.
- **FR-3151**: A tradução de identificadores em nomes MUST custar no máximo uma consulta por página,
  e nenhuma no modo demonstração.

### Key Entities

Incremento 1: nenhuma nova. As da `106` — Pessoa, Identidade externa, Vínculo, Revogação — e a
unidade ativa, que mora na sessão. A sessão institucional passa a guardar também o instante da
entrada e o da última atividade.

Incremento 2:

- **Suspensão de pessoa**: quem, quando, por quem e por quê. Imutável. Aberta enquanto não houver
  reativação.
- **Reativação**: o encerramento de uma suspensão, com quem, quando e por quê. Imutável, uma por
  suspensão.

---

## Decisões do usuário (30/10/2026)

Respostas do usuário ao PR #346, registradas como foram dadas. **Nenhuma foi tomada por esta
spec.** O merge e a ativação em produção continuam sujeitos às autorizações próprias.

| | Pergunta | Decisão | Onde se aplica |
|---|---|---|---|
| P1 | A suspensão | **C**: suspensão global **e** revogação por unidade. O administrador institucional suspende pessoas; a suspensão do administrador institucional é da implantação. Motivo, trilha e fim de todas as sessões | US6; FR-3135 a FR-3142 |
| P2 | A reativação | **A**: os vínculos não se desfazem; voltam a valer os vigentes, os revogados não. A confirmação mostra o que volta. Nenhuma sessão anterior volta, mesmo sem requisição durante a suspensão | US7; FR-3143 a FR-3146 |
| P3 | Retirar ou substituir a administração institucional | **A**: comando de implantação, com motivo e trilha; a substituição concede e revoga numa operação só | US8; FR-3147, FR-3148 |
| P4 | Os tempos de sessão | **8 h** de duração máxima e **30 min** de inatividade, declarados expressamente na configuração de produção; ajustes posteriores, documentados | FR-3124, já implementado: produção não sobe sem a declaração; `doc/ativacao-do-sso-institucional.md`, §5 |
| Proposta 1 da `106` | O identificador externo | o estável do provedor, com o emissor: em OIDC, `iss` + `sub`. Nome e e-mail não associam | o adaptador real, na ativação; nenhum dado gravado muda |
| Proposta 2 da `106` | O administrador institucional | **duas pessoas** designadas nominalmente por ato formal, contas individuais, o ato como motivo da concessão | o comando da `106`, com `--adicional` para a segunda; a retirada e a substituição, FR-3147 e FR-3148 |
| Proposta 3 da `106` | Quem concede na unidade | o papel próprio de Administrador de acessos da unidade, separado do Gestor; acúmulo só por concessões explícitas | nada muda: é o que o catálogo da `106` já faz |

**A escolha que pede mais cuidado é a P2**: preservar os vínculos torna a suspensão temporária
previsível, mas exige mostrar com clareza o que será restabelecido — é a `FR-3145`.

### O que as respostas não dizem, e fica em aberto

- **A retirada do último administrador institucional.** A P3 manda retirar pelo comando, e a
  proposta 2 fala em duas pessoas; nada diz se a retirada pode deixar **nenhuma**. O plano propõe
  que o comando recuse deixar zero sem uma marca explícita, como o `--adicional` faz na concessão —
  **salvaguarda proposta, não decidida** (`D-018` do research).

## Achados registrados (fora de escopo)

- **Não há como retirar a administração institucional** (`_autoridade` recusa o papel nos dois
  sentidos, e o comando só concede). Impacto: uma conta comprometida só sai pelo banco. Decidido em
  30/10 (P3), e especificado no incremento 2 (US8); continua aberto até ser implementado.
- **A concessão da `106` não recusa pessoa inativa.** A `107` passa a recusá-la (FR-3134), porque a
  busca não a oferece e a confirmação a reconfere.
- **Encerrar a sessão institucional encerra também a identidade do portal no mesmo navegador**: o
  `logout()` do framework apaga a sessão inteira, e o portal guarda a identidade do candidato na
  mesma sessão. Impacto baixo — servidor e candidato no mesmo navegador —, e é o comportamento
  seguro. Registrado, não alterado.
- **A recusa da gestão manda pedir "a quem administra o sistema no Cefor"** (`recusa.html`). No modo
  institucional o papel existe e tem nome. A frase é canônica da `033`, e mudá-la é decisão dela.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1011**: Uma concessão completa — buscar, escolher, conferir, confirmar — se faz em no máximo
  quatro telas, sem digitar identificador.
- **SC-1012**: Em 100% dos casos exercitados, a revogação feita pela tela vale na primeira
  requisição seguinte da pessoa de destino, com a sessão dela aberta.
- **SC-1013**: Zero caminhos de tela ou envio montado à mão concedem a si mesmo, alcançam outra
  unidade ou listam pessoa sem termo de busca.
- **SC-1014**: A jornada pelo navegador cobre as cinco histórias, e passa sem nenhuma ação fora do
  navegador entre a preparação e as verificações.
- **SC-1015**: A suíte existente — inclusive os testes da `106` e os de regressão dos dois achados —
  passa contra PostgreSQL sem mudar resultado esperado.
- **SC-1016**: No modo demonstração, as telas existentes não fazem consulta nenhuma a mais.

Do incremento 2, a medir quando for implementado:

- **SC-1017**: Em 100% dos casos exercitados, a suspensão encerra todas as sessões abertas da
  pessoa na requisição seguinte de cada uma, sem revogar vínculo nenhum.
- **SC-1018**: Em 100% dos casos exercitados, nenhuma sessão anterior à suspensão vale depois da
  reativação, inclusive a que não fez requisição durante ela.
- **SC-1019**: Zero estados em que a substituição da administração institucional grava só a
  concessão ou só a revogação.
- **SC-1020**: Nenhuma tela da gestão mostra `pessoa-<uuid>` como autor de ato no modo
  institucional.

## Assumptions

- A `106` entra na `main` antes desta feature. Esta branch não muda nada dela além do que FR-3134
  diz.
- As unidades dos testes de duas unidades são o `cefor` e a fictícia `campus-a`, como na `106`.
- O e-mail institucional e o nome são dados que os servidores já veem uns dos outros no Ifes;
  mostrá-los a quem concede acesso não amplia a exposição. A retenção deles é a do B-2, fora.
- Hoje nenhuma requisição da gestão é automática (não há sondagem periódica); o mecanismo de
  declaração existe para a primeira que vier.
