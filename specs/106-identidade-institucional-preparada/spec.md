# Feature Specification: Identidade institucional preparada — a gestão pronta para o SSO, com a homologação intacta

**Feature Branch**: `claude/eloquent-wing-4d768b`, sobre a `main` em `4d93c1f8`

**Created**: 2026-10-30

**Status**: Implementada nesta branch; merge não autorizado. Três propostas esperam o usuário
(§Propostas ao usuário), e nenhuma bloqueia o que foi implementado.

**Input**: o pedido de 30/10/2026, "GPS — Evolução gradual da autenticação, preservando o ambiente
de homologação"; a [auditoria da administração institucional](../../doc/auditoria-administracao-institucional-2026-10-30.md),
cujo parecer do usuário prevalece sobre as §8 e §10 dela; o
[estudo do B-1](../../doc/estudo-identidade-e-acessos-2026-10-30.md); o
[diagnóstico Django Auth × identidade própria](../../doc/diagnostico-autenticacao-da-gestao-2026-10-30.md)
e a [ADR](../../doc/decisao-identidade-e-autorizacao-da-gestao.md), escritos como primeiro passo
desta feature.

> **Faixa de identificadores.** Esta spec abre em **FR-3001** e **SC-1001**. O teto medido em
> 30/10/2026 em `specs/` de todas as worktrees desta máquina é o requisito dois mil novecentos e
> seis e o critério novecentos e noventa e três, os dois da `105`. **Nenhum `UX-` é aberto aqui.**
> As decisões reiniciam em `D-001` e moram no `research.md`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-021 da `001`"); decisão do estudo ou de outra feature pelo assunto e pelo número por extenso
> ("a decisão 5 do estudo").

---

## Por que esta feature existe

A gestão não tem autenticação em produção e responde 503 lá. Em desenvolvimento e homologação, a
entrada é o seletor de demonstração: a pessoa escolhe quem é e quais papéis tem, e é assim que o
usuário homologa o GPS. O pedido é preparar a arquitetura definitiva — usuários, vínculos por
unidade e permissões, prontos para receber a identidade do SSO do Ifes — **sem** integrar o SSO e
**sem** tocar no seletor.

### O que foi reconferido no código em 30/10/2026

O diagnóstico detalha cada ponto. Os que decidem o desenho:

- O `Actor` se constrói num ponto só da gestão, e o resto do sistema autoriza por ele.
- O `subject` vai como texto a colunas append-only, e a segregação compara esses textos. O valor
  que entrar em produção não se corrige depois.
- `django.contrib.auth` está instalado, e o `auth_user` existe em todo banco. Nenhum código o usa.
- A trilha exige agregado com UUID.
- Presidência e participação em comissão vêm de `MembroComissao`, procurado pelo `subject` do ator,
  depois de conferido o escopo.
- O seletor desenha uma caixa por papel do `PAPEIS`: papel novo ali aparece na tela de
  identificação.
- A recusa de produção ao seletor é só de inicialização.

### O que esta spec cobre, e o que fica fora

**Cobre** os quatro incrementos do pedido:

- **A, arquitetura e compatibilidade:** o diagnóstico, a ADR, a estratégia de identidade e o
  contrato do adaptador;
- **B, núcleo de identidade e autorização:** a pessoa, a identidade externa, o vínculo e a
  revogação; a resolução do `Actor`; a sessão institucional; as regras de concessão;
- **C, adaptador institucional simulado:** um provedor falso só nos testes, sem rede;
- **D, preparação da ativação:** a configuração por ambiente, as recusas de produção, a
  documentação de implantação e os testes de segurança.

**Fica fora**: o SSO real e qualquer biblioteca de cliente OIDC ou SAML; a migração para produção;
a emenda da segregação (FR-021 da `001`, decisão 8 do estudo); telas de administração de acessos,
de troca de unidade na barra e de "sem acesso"; a exibição do nome no lugar do identificador
opaco; tempo de sessão e inatividade; suspensão de pessoa; a API, que continua fechada em
produção; a comissão apontando para pessoa. Cada um está em
[`doc/ativacao-do-sso-institucional.md`](../../doc/ativacao-do-sso-institucional.md), com o que
pede.

---

## Clarifications

### Session 2026-10-30

- Q: O seletor de demonstração muda? → A: Não. Mesma tela, mesmos oito papéis, mesma sessão. O
  pedido o exige, e os 260 arquivos de teste que identificam por ele são a prova.
- Q: Qual provedor? → A: Nenhum agora. O pedido adia a integração real; o contrato do adaptador é
  o que se especifica, e um provedor falso o exercita nos testes.
- Q: Django Auth ou identidade própria? → A: Django Auth para a identidade e a sessão; autorização
  do GPS, por vínculos. Ver `D-001` e a ADR.
- Q: Qual identificador do provedor vai aos atos? → A: Nenhum. Vai um identificador interno,
  gerado pelo GPS (`D-002`); o do provedor só localiza a pessoa, e qual dele usar fica proposto ao
  usuário.
- Q: Quem administra acessos? → A: Dois papéis de acesso, num catálogo ao lado do `PAPEIS`, e a
  regra de que ninguém concede a si mesmo (`D-004`, `D-005`). Quem os exerce é governança, e fica
  proposto.
- Q: Telas de administração? → A: Não nesta etapa. O pedido diz para evitá-las se domínio e testes
  bastarem, e bastam: a concessão é exercida pela camada de aplicação, e o primeiro administrador,
  por comando.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A homologação continua exatamente como hoje (Priority: P1)

O usuário abre `/gestao/identificar` no ambiente de homologação, escolhe "Acessar ambiente de
demonstração", seleciona uma identidade e os papéis dela, e percorre elaboração, homologação,
publicação, retificação e comissões, como faz hoje.

**Why this priority**: é a condição do pedido. Uma regressão aqui impede a homologação do GPS
inteiro.

**Independent Test**: com o seletor ligado e sem provedor institucional, a suíte existente passa
sem alteração dos resultados esperados, e a página de acesso é a mesma.

**Acceptance Scenarios**:

1. **Given** o seletor ligado, **When** a pessoa se identifica pelo seletor, **Then** a sessão, o
   destino e as permissões são os de hoje.
2. **Given** o seletor ligado e um provedor institucional também configurado, **When** a pessoa se
   identifica pelo seletor, **Then** nada muda para ela, e nenhuma pessoa institucional nem
   vínculo é criado.
3. **Given** dados de homologação já gravados com identidades de demonstração, **When** o
   incremento é aplicado, **Then** nenhum registro, documento ou ato existente muda.

---

### User Story 2 — Uma identidade institucional produz o `Actor` certo (Priority: P1)

Uma servidora entra pelo provedor institucional — nos testes, o simulado. O GPS a localiza (ou a
cria, no primeiro acesso), lê os vínculos dela e produz um `Actor` com o identificador estável, a
unidade ativa e as permissões dos papéis vigentes ali. Com esse `Actor`, ela executa os mesmos
fluxos que a demonstração executa.

**Why this priority**: é a preparação pedida. Sem ela, a ativação do SSO reescreveria o negócio.

**Independent Test**: com o provedor simulado configurado, a entrada produz o `Actor` esperado, e
uma operação da gestão autorizada pelo papel vigente funciona pela tela.

**Acceptance Scenarios**:

1. **Given** uma pessoa com Elaborador vigente no `cefor`, **When** ela entra pelo provedor,
   **Then** o `Actor` tem o identificador estável dela, o escopo `cefor` e as permissões do
   Elaborador.
2. **Given** a mesma pessoa Gestora no `cefor` e Elaboradora no `campus-a`, **When** ela troca a
   unidade ativa, **Then** as permissões são as da unidade ativa, e nenhuma da outra.
3. **Given** a pessoa com sessão aberta, **When** o vínculo dela é revogado, **Then** a requisição
   seguinte já não tem a permissão.
4. **Given** a pessoa que elaborou e homologou um Edital, **When** ela sai, entra de novo, e o
   provedor informa outro nome e outro e-mail, **Then** a publicação é recusada pela segregação,
   porque o identificador é o mesmo.
5. **Given** um cliente que envia cabeçalho ou parâmetro dizendo quem é, **When** chega ao retorno
   sem uma autenticação concluída pelo provedor, **Then** nada é autenticado.

---

### User Story 3 — Os acessos se concedem e se revogam com regra e trilha (Priority: P2)

O administrador institucional concede o Administrador de acessos de uma unidade; este concede os
papéis operacionais da unidade dele; um e outro revogam. Ninguém concede a si mesmo, e ninguém
alcança unidade que não é sua.

**Why this priority**: sem ela não há como alguém ganhar acesso em produção; mas ela só vale depois
da US2.

**Independent Test**: as regras de concessão e revogação, exercidas pela camada de aplicação,
recusam o que devem e gravam na trilha o que aceitam.

**Acceptance Scenarios**:

1. **Given** o Administrador de acessos do `cefor`, **When** concede Elaborador a outra pessoa no
   `cefor`, com motivo, **Then** o vínculo nasce e a trilha registra quem, quando e por quê.
2. **Given** o mesmo administrador, **When** tenta conceder a si mesmo, **Then** é recusado e nada é
   gravado.
3. **Given** o mesmo administrador, **When** tenta conceder no `campus-a`, **Then** a unidade é
   tratada como inexistente.
4. **Given** o mesmo administrador, **When** tenta conceder um papel de acesso, **Then** é recusado.
5. **Given** o administrador institucional, **When** abre um ato do `cefor`, **Then** não tem
   permissão operacional nenhuma.
6. **Given** a presidente de uma comissão do `cefor`, **When** todos os vínculos dela no `cefor` são
   revogados, **Then** ela não gere mais a comissão, por caminho nenhum.

---

### User Story 4 — Produção só entra pela autenticação institucional (Priority: P1)

Quem implanta declara o provedor institucional. Sem ele, a gestão fica bloqueada. Com o seletor, com
um provedor de teste ou com um provedor que não existe, produção não sobe. Em nenhum caso o acesso
cai para a demonstração.

**Why this priority**: é a garantia que torna seguro manter o seletor no código.

**Independent Test**: as configurações de produção exercitadas nos testes recusam o que devem, e uma
sessão de demonstração não vale com a marca de produção ligada.

**Acceptance Scenarios**:

1. **Given** produção sem provedor, **When** alguém abre a gestão, **Then** recebe a página de
   entrada não configurada, com 503, e nenhuma oferta de demonstração.
2. **Given** produção com o seletor ligado, **When** o processo sobe, **Then** recusa, nomeando a
   variável.
3. **Given** produção com o provedor simulado declarado, **When** o processo sobe, **Then** recusa.
4. **Given** a marca de produção ligada e o seletor ligado em execução, **When** chega uma sessão
   de demonstração, **Then** ela não vale.

---

### Edge Cases

- **Primeiro acesso sem vínculo nenhum**: a pessoa é criada, mas não há `Actor`; a gestão a manda
  de volta à página de acesso, como a quem não entrou.
- **Pessoa só com vínculo institucional**: a unidade ativa é o escopo institucional, e ela só vê o
  que `acesso:administrar` alcança.
- **Duas revogações simultâneas do mesmo vínculo**: uma vale, a outra é recusada.
- **Duas concessões simultâneas do mesmo papel**: uma vale, a outra é recusada como já vigente.
- **Mesmo identificador externo chegando por outro provedor**: é outra identidade externa, e
  portanto outra pessoa, até um ato explícito associar.
- **Mesmo e-mail em duas contas do provedor**: duas pessoas. O e-mail não associa.
- **Superusuário do Django sem vínculo**: não entra.
- **Pessoa desativada com sessão aberta**: a sessão cai na requisição seguinte.
- **Retorno do provedor repetido** (o mesmo estado duas vezes): o segundo é recusado.
- **Provedor configurado, retorno sem estado**: recusa, sem criar pessoa.
- **Sessão institucional num ambiente que deixou de ter provedor**: encerrada.
- **Unidade inativa ou não registrada**: não recebe vínculo.

---

## Requirements *(mandatory)*

### Functional Requirements

**Modo demonstração**

- **FR-3001**: O seletor de demonstração MUST continuar com a mesma tela, os mesmos oito papéis, a
  mesma sessão e os mesmos destinos. Nenhum teste existente muda o resultado esperado por causa
  desta feature.
- **FR-3002**: A demonstração MUST NOT criar pessoa institucional, identidade externa nem vínculo,
  e a resolução institucional MUST NOT localizar pessoa pelo texto de um `subject`. Identidade
  fictícia nunca se converte em institucional.
- **FR-3003**: O seletor MUST se declarar indisponível sempre que o ambiente for de produção, mesmo
  que a chave dele esteja ligada em execução — além da recusa de inicialização que já existe.

**Identidade interna**

- **FR-3004**: Cada pessoa institucional MUST ter um identificador interno gerado pelo sistema na
  primeira entrada, sem dado pessoal e de formato que a demonstração não produz por acaso. É ele o
  `subject` dos atos e da trilha, e ele MUST NOT mudar — o banco recusa a alteração.
- **FR-3005**: Os identificadores do provedor MUST ser associados à pessoa por par
  (provedor, identificador) único, no máximo um por pessoa e provedor, em registro que não se altera
  nem se exclui. A associação MUST NOT se fazer pelo e-mail.
- **FR-3006**: A primeira entrada MUST criar a pessoa e a associação; as seguintes MUST atualizar
  nome e e-mail sem mudar o identificador interno.
- **FR-3007**: Pessoa MUST NOT se excluir. Ela não tem senha utilizável, e as marcas de
  superusuário e de equipe do framework MUST NOT conceder permissão nenhuma.

**Vínculos e catálogo**

- **FR-3008**: Um vínculo MUST registrar pessoa, escopo, papel, quem concedeu, quando e o motivo, e
  MUST NOT se alterar nem se excluir. A revogação MUST ser registro próprio, com quem, quando e o
  motivo, no máximo um por vínculo, e também imutável.
- **FR-3009**: Os papéis concedíveis MUST ser os oito do `PAPEIS`, sem mudança; mais o
  *Integrante da unidade*, sem permissão sistêmica, para quem atua só pela comissão; mais dois
  papéis de acesso — *Administrador de acessos da unidade* (`acesso:gerir`, `acesso:consultar`) e
  *Administrador institucional de acessos* (`acesso:administrar`) — num catálogo à parte, que o
  seletor não mostra.
- **FR-3010**: Conceder ou revogar papel operacional MUST exigir `acesso:gerir` na unidade do
  vínculo. Sem a permissão, a recusa é 403; com a permissão em outra unidade, a unidade é tratada
  como inexistente (404).
- **FR-3011**: Conceder ou revogar o Administrador de acessos de uma unidade MUST exigir
  `acesso:administrar` no escopo institucional. O Administrador institucional MUST NOT ser
  concedido pela aplicação: nasce só pelo comando de implantação (FR-3029).
- **FR-3012**: Ninguém MUST conceder nem revogar vínculo próprio. A comparação é pelo identificador
  interno estável.
- **FR-3013**: A concessão MUST recusar: motivo vazio; papel fora do catálogo; papel de acesso pela
  porta operacional; vínculo igual já vigente; unidade não registrada ou inativa; escopo
  institucional numa concessão de unidade.
- **FR-3014**: A revogação MUST seguir as regras de autoridade da concessão do mesmo papel, exigir
  motivo e recusar o vínculo já revogado, também sob concorrência.
- **FR-3015**: Toda concessão e toda revogação MUST ir à trilha com ator, permissão, escopo não
  vazio, operação e motivo.
- **FR-3016**: A leitura dos vínculos vigentes de uma unidade MUST exigir `acesso:consultar` naquela
  unidade.

**Sessão e `Actor`**

- **FR-3017**: No modo institucional, o `Actor` MUST ter como `subject` o identificador interno,
  como escopo a unidade ativa, e como permissões a união dos papéis dos vínculos vigentes nela. Ele
  MUST ser recalculado a cada requisição, e MUST NOT guardar papel na sessão.
- **FR-3018**: Sem vínculo vigente na unidade ativa, MUST NOT haver `Actor` — e por isso nenhuma
  autorização derivada de comissão ou presidência o alcança.
- **FR-3019**: A unidade ativa inicial MUST ser a primeira unidade, em ordem de código, em que a
  pessoa tem vínculo vigente; sem nenhuma, o escopo institucional, se houver vínculo nele. A troca
  MUST aceitar só escopo com vínculo vigente, MUST NOT carregar permissão de um para o outro, e MUST
  ir à trilha.
- **FR-3020**: A entrada institucional MUST trocar o identificador da sessão e descartar a sessão
  anterior de outra pessoa, e MUST ir à trilha. A saída MUST encerrar a sessão e ir à trilha.
- **FR-3021**: Pessoa desativada MUST perder a sessão na requisição seguinte.

**Adaptador**

- **FR-3022**: O adaptador institucional MUST entregar (provedor, identificador, nome, e-mail) de
  uma autenticação concluída, ou nada. O sistema MUST NOT ler identidade de cabeçalho, parâmetro ou
  corpo enviado pelo cliente fora do que o adaptador devolve.
- **FR-3023**: O retorno do provedor MUST carregar o estado criado na ida, de uso único, ligado à
  sessão. Sem ele, ou repetido, MUST recusar sem criar nada.
- **FR-3024**: O provedor simulado MUST existir só no código de teste, sem rede, e MUST se declarar
  provedor de teste.
- **FR-3025**: A página de acesso MUST oferecer a entrada institucional só quando há provedor
  configurado. Sem provedor, ela MUST ficar como hoje.

**Ativação e produção**

- **FR-3026**: Produção MUST recusar subir com um provedor que se declare de teste, que esteja no
  código de teste, ou que não se importe; e com qualquer *backend* de autenticação além do
  institucional.
- **FR-3027**: Produção sem provedor MUST manter a gestão bloqueada, com a página de entrada não
  configurada, e MUST NOT oferecer demonstração.
- **FR-3028**: Sessão cuja origem deixou de ser admitida no ambiente MUST ser encerrada na leitura —
  a de demonstração sem o seletor, como hoje; a institucional sem o provedor.
- **FR-3029**: Um comando de implantação MUST conceder o Administrador institucional a uma
  identidade externa, com motivo obrigatório, sob o ator de implantação, e MUST recusar uma segunda
  pessoa sem a marca explícita de concessão adicional.

**Preservação**

- **FR-3030**: As migrations desta feature MUST só criar as tabelas novas e proteger a pessoa; MUST
  NOT alterar, reescrever nem excluir tabela, linha ou documento existente.
- **FR-3031**: A feature MUST deixar documentado como manter a homologação funcionando e o que falta
  para ativar o SSO real.

### Key Entities

- **Pessoa**: quem atua na gestão pelo modo institucional. Identificador interno estável, nome,
  e-mail, situação (ativa ou não). Não guarda senha nem papel.
- **Identidade externa**: um identificador de um provedor, associado a uma pessoa. Imutável.
- **Vínculo**: pessoa × escopo (unidade, ou o institucional) × papel, com quem concedeu, quando e
  por quê. Imutável; encerra-se por revogação.
- **Revogação**: o encerramento de um vínculo, com quem, quando e por quê. Imutável, uma por
  vínculo.
- **Unidade ativa**: o escopo em que a sessão está atuando. Não é dado persistido: mora na sessão.

---

## Propostas ao usuário

Governança, e não técnica. O implementado as acomoda; a resposta é condição da ativação, e não
deste merge.

1. **Qual identificador do provedor localiza a pessoa** (decisão 2 do estudo). Proposta: o
   identificador imutável do provedor (`sub` do OIDC, `objectGUID`). Como o que vai aos atos é o
   identificador interno, a escolha deixou de ser irreversível.
2. **Quem é o Administrador institucional de acessos, e por qual ato** (decisão 4 do estudo).
   Proposta: quem a portaria indicar, uma ou duas pessoas, concedido pelo comando com o número da
   portaria como motivo.
3. **Quem concede na unidade** (decisão 5 do estudo). Proposta: o papel próprio de Administrador de
   acessos da unidade, separado do Gestor. A alternativa — o Gestor recebe `acesso:gerir` — é uma
   linha no catálogo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1001**: A suíte existente passa contra PostgreSQL sem mudar nenhum resultado esperado de
  comportamento. Só mudam os guardiões que contam tabelas append-only e migrations, que existem
  para subir junto com a justificativa.
- **SC-1002**: Os doze testes obrigatórios do pedido existem, cada um nomeado na matriz de
  rastreabilidade, e passam.
- **SC-1003**: Em todas as configurações de produção exercitadas, zero caminhos autenticam pela
  demonstração ou por provedor de teste.
- **SC-1004**: Em 100% dos casos exercitados, a revogação vale na primeira requisição seguinte.
- **SC-1005**: No modo institucional, a resolução do `Actor` custa no máximo duas consultas por
  requisição, por mais que a página o leia.
- **SC-1006**: No modo demonstração, as telas existentes não fazem consulta nenhuma a mais.

## Assumptions

- Não há banco de produção com atos gravados: a gestão nunca abriu lá. Os bancos de homologação têm
  atos com identidades de demonstração, e eles ficam como estão.
- As unidades usadas nos testes de duas unidades são o `cefor` e a fictícia `campus-a`, registrada
  por *fixture*.
- O escopo institucional reservado é um valor que não é código de unidade.
- A integração real do SSO cumprirá o contrato do adaptador; se o provedor escolhido não entregar
  um identificador estável, a proposta 1 muda, e o identificador interno não.
