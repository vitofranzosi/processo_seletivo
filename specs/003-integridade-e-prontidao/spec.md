# Feature Specification: Integridade Normativa e Prontidão para Produção

**Feature Branch**: `003-integridade-e-prontidao`

**Created**: 2026-08-29

**Status**: Draft

**Input**: Revisão de segurança e integridade sobre o estado consolidado das features
`001-processo-seletivo-editais` e `002-frontend-administrativo` (commit `b12b8f6`). A revisão
encontrou seis defeitos bloqueadores, todos reproduzidos com teste executável, e um conjunto de
lacunas de endurecimento. Esta especificação organiza a correção e define o que significa "pronto
para implantar".

## Contexto e Justificativa

O sistema produz **atos administrativos com efeito jurídico**. Um Edital publicado e suas
Retificações são a norma que rege direitos de candidatos. Por isso, a régua desta feature não é
"o sistema funciona", é "o sistema não pode publicar como norma algo que ninguém decidiu".

Os defeitos abaixo foram confirmados por execução, não por leitura. Cada um está reproduzido em
`Evidência` com o resultado observado.

### Defeito 1 — Retificação atinge o item normativo errado *(mais grave)*

Os caminhos normativos endereçam coleções por índice (`/profiles/1/name`). O índice não é
estável: outra Retificação que remova ou insira um Perfil anterior desloca todos os seguintes.
Como `expectedPreviousHash` é opcional e nem a interface nem os testes o enviam,
`requires_content_check` retorna falso e **nenhuma verificação de conteúdo acontece** para
`REPLACE` e `REMOVE`.

**Evidência**: partindo de um Edital com `Perfil 1`, `Perfil 2`, `Perfil 3`, uma Retificação
elaborada para renomear o `Perfil 2` (`/profiles/1/name`) foi publicada depois de outra
Retificação que removeu o `Perfil 1`. Resultado publicado:

```
base:  ['Perfil 1', 'Perfil 2', 'Perfil 3']
final: [('P2', 'Perfil 2'), ('P3', 'RENOMEADO')]
```

O ato renomeou o `Perfil 3`. O sistema publicou como norma vigente uma alteração que **nenhuma
autoridade homologou**, sem erro, sem aviso e sem rastro de que algo divergiu.

### Defeito 2 — Retificação publica Edital estruturalmente inválido

`publish_retification` verifica que houve efeito prático e que a composição é determinística, mas
o snapshot resultante **não volta a passar por `validate_for_publication`**. As invariantes que
`publish_edital` impõe (título, ao menos um Perfil, ao menos um Evento) não valem para o conteúdo
que a Retificação faz vigorar.

**Evidência**: remover o único Perfil por Retificação retornou `201` e deixou a versão vigente com
`profiles: []` — estado que a publicação original rejeitaria com `blocking_findings`.

### Defeito 3 — Autenticação da API pode ser forjada

`InstitutionalBearerAuthentication` aceita `subject|scope|permissões` sem assinatura nem
verificação externa. Qualquer cliente declara a própria identidade **e as próprias permissões**.
É limitação conhecida e documentada como adaptador provisório, mas é bloqueador absoluto: com ela
ligada, todo o modelo de autorização do backend é decorativo.

### Defeito 4 — POSTs administrativos sem proteção CSRF

`CsrfViewMiddleware` não está em `MIDDLEWARE`. Os `{% csrf_token %}` presentes nos templates não
são fiscalizados por ninguém. Como a interface autentica por sessão, qualquer página externa pode
praticar atos em nome de quem estiver logado.

**Evidência**: `POST /gestao/identificar` sem token, com `Client(enforce_csrf_checks=True)`,
retornou `302 -> /gestao/`.

### Defeito 5 — Contrato de idempotência não implementado nas Retificações

O OpenAPI exige `Idempotency-Key` em criar, submeter, homologar, devolver, cancelar e publicar
Retificação. As views ignoram o cabeçalho. Os comandos ainda gravam `correlation_id=""`, quebrando
a correlação entre log e auditoria que a Constituição (princípio V) exige.

**Evidência**: duas criações com a mesma chave retornaram `201` com ids distintos
(`039f301b…` e `1ed6368b…`); o evento de auditoria gravou `correlation_id: ''`.

### Defeito 6 — Editais podem nascer em Processo encerrado

`add_edital` não chama `ensure_processo_accepts_changes` e não bloqueia o Processo pai, violando
FR-035 da 001 e abrindo corrida com a finalização concorrente.

**Evidência**: `POST /processos/{id}/editais` sobre Processo `ENCERRADO` retornou `201` com o
Edital em `EM_ELABORACAO`.

## Clarifications

### Session 2026-08-29

- Q: Corrigir o endereçamento por índice exige trocar o modelo de dados agora? → A: Não de
  imediato. São duas correções de alcance diferente e ambas são necessárias. A **contenção** é
  tornar a precondição de conteúdo obrigatória e verificada sempre: o servidor deriva o hash do
  conteúdo que a pessoa efetivamente enxergou (a versão consolidada usada como base) e o confronta
  na publicação. Isso transforma o ato silenciosamente errado em recusa explícita `409`, sem
  alterar o contrato público. A **cura** é endereçar coleções por chave estável, e é mudança de
  `data-model` e de contrato que merece seu próprio ciclo.
- Q: A precondição derivada pelo servidor não deveria ser responsabilidade do cliente? → A: Não.
  O cliente pode declarar `expectedPreviousHash` e sua declaração prevalece. Mas a ausência da
  declaração não pode significar "publique sem verificar" — significa "verifique contra a base que
  eu declarei", que é informação que o servidor já tem em `baseSnapshotId`. Precondição opcional
  para o cliente, obrigatória para o sistema.
- Q: Autenticação institucional entra nesta feature? → A: A integração com o diretório é incremento
  próprio, como a 002 já registrou. Aqui entra o que impede o dano enquanto ela não existe: um
  módulo de configuração de produção que **recusa iniciar** com o adaptador provisório, o seletor
  de identidade, chave secreta padrão ou HTTPS desligado. Prontidão é falhar cedo, não confiar em
  disciplina de implantação.
- Q: Qual a régua de "pronto para produção" desta feature? → A: `manage.py check --deploy` sem
  achados no módulo de produção, os seis defeitos com teste de regressão, e a suíte executada
  também contra PostgreSQL — os 20 testes hoje ignorados cobrem justamente concorrência,
  permissões de banco e migrações, que são onde os riscos transacionais vivem.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Retificação atinge o que a pessoa decidiu (Priority: P1)

Como autoridade que homologa uma Retificação, quero que o ato publicado altere exatamente o item
normativo que estava à minha frente quando homologuei, para que minha assinatura não recaia sobre
conteúdo que eu não vi.

**Why this priority**: É o único defeito que faz o sistema publicar norma falsa em silêncio.
Nenhum outro achado produz um documento oficial incorreto sem sinal algum.

**Independent Test**: Elaborar duas Retificações sobre a mesma versão consolidada, publicar
primeiro a que desloca índices e depois a outra, verificando que a segunda é recusada em vez de
aplicada ao item deslocado.

**Acceptance Scenarios**:

1. **Given** duas Retificações elaboradas sobre a mesma versão consolidada, uma removendo um
   Perfil anterior e outra alterando um Perfil seguinte, **When** a primeira é publicada e depois
   a segunda, **Then** a segunda é recusada com `409` e mensagem que indica o caminho divergente e
   orienta refazer sobre a versão vigente.
2. **Given** uma Retificação cujo caminho alvo não foi tocado por nenhuma outra publicada no
   intervalo, **When** é publicada, **Then** é aceita normalmente.
3. **Given** uma Retificação recusada por divergência, **When** a pessoa a reaponta para a versão
   consolidada atual e revisa o conteúdo, **Then** pode submetê-la de novo sem recriar o ato.
4. **Given** uma Retificação que declara `expectedPreviousHash` explicitamente, **When** é
   publicada, **Then** a declaração do cliente prevalece sobre a precondição derivada.

---

### User Story 2 - Nenhuma Retificação publica Edital inválido (Priority: P1)

Como responsável pela publicação, quero que o conteúdo que passa a vigorar depois de uma
Retificação obedeça às mesmas invariantes estruturais exigidas na publicação original, para que
não exista Edital vigente sem Perfil, sem Cronograma ou sem título.

**Why this priority**: A Constituição exige que erro impeditivo bloqueie a publicação. Hoje a
regra vale na porta da frente e não vale na Retificação, que é justamente o caminho pelo qual o
conteúdo muda depois de público.

**Independent Test**: Publicar uma Retificação que remove o único Perfil e verificar que o ato é
recusado com erro impeditivo, e que a versão vigente permanece a anterior.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com um único Perfil, **When** uma Retificação que o remove é
   publicada, **Then** o ato é recusado com `422` e a lista de erros impeditivos.
2. **Given** uma Retificação que esvazia o Cronograma, **When** é publicada, **Then** é recusada
   pelo mesmo caminho.
3. **Given** uma Retificação estruturalmente válida, **When** é publicada, **Then** a validação não
   interfere no fluxo normal.
4. **Given** uma Retificação recusada por erro impeditivo, **When** a recusa ocorre, **Then**
   nenhuma Publicação, documento ou versão consolidada é materializada.

---

### User Story 3 - A sessão administrativa não pratica atos que a pessoa não pediu (Priority: P1)

Como servidor autenticado na interface, quero que uma página externa não consiga praticar atos em
meu nome enquanto minha sessão está aberta, para que minha identidade não seja usada por terceiros.

**Why this priority**: Toda a interface administrativa autentica por sessão. Sem CSRF, cada ato
irreversível do sistema — publicar, homologar, encerrar — é alcançável por requisição forjada.

**Independent Test**: Emitir POST sem token para cada rota de ato da interface com verificação CSRF
ligada e confirmar recusa; repetir com token válido e confirmar aceitação.

**Acceptance Scenarios**:

1. **Given** uma sessão administrativa aberta, **When** chega um POST sem token CSRF válido,
   **Then** a requisição é recusada com `403` e nenhum efeito de domínio ocorre.
2. **Given** a mesma sessão, **When** o POST vem dos formulários da própria interface, **Then** é
   processado normalmente.
3. **Given** a API `/api/v1/`, **When** recebe requisições autenticadas por cabeçalho, **Then**
   segue funcionando sem exigir token de sessão.
4. **Given** qualquer resposta HTML da interface, **When** é servida, **Then** traz política de
   enquadramento que impede exibição em moldura de terceiros.

---

### User Story 4 - Ato final encerra de verdade (Priority: P2)

Como gestor que encerra um Processo Seletivo, quero que o encerramento impeça qualquer alteração
posterior em seus Editais, inclusive a criação de novos, para que o desfecho signifique o que diz.

**Independent Test**: Encerrar um Processo e tentar criar Edital nele; repetir com finalização
concorrente sob PostgreSQL, verificando que uma das operações perde.

**Acceptance Scenarios**:

1. **Given** um Processo `ENCERRADO` ou `CANCELADO`, **When** alguém tenta criar um Edital nele,
   **Then** a operação é recusada com `409` e a mesma mensagem dos demais atos bloqueados.
2. **Given** um Processo `ATIVO`, **When** a criação de um Edital e o encerramento do Processo
   ocorrem concorrentemente, **Then** apenas uma das duas prevalece e o estado final é coerente.
3. **Given** um Processo em estado final, **When** a auditoria é consultada, **Then** a tentativa
   recusada não aparece como ato praticado.

---

### User Story 5 - Repetir a requisição não duplica o ato (Priority: P2)

Como cliente da API, quero que reenviar uma requisição de Retificação com a mesma
`Idempotency-Key` devolva o mesmo resultado em vez de criar um segundo ato, para que uma falha de
rede não vire duplicidade normativa.

**Independent Test**: Repetir cada operação de Retificação com a mesma chave e verificar
identidade do resultado; repetir com corpo diferente e verificar `409`.

**Acceptance Scenarios**:

1. **Given** uma criação de Retificação já processada, **When** a mesma chave e o mesmo corpo são
   reenviados, **Then** a resposta descreve a mesma Retificação, sem criar outra.
2. **Given** a mesma chave com corpo diferente, **When** é reenviada, **Then** a resposta é `409`
   `idempotency_conflict`.
3. **Given** qualquer ato de Retificação, **When** é praticado, **Then** o evento de auditoria
   grava o `X-Correlation-ID` da requisição e a `Idempotency-Key` utilizada.
4. **Given** o contrato OpenAPI, **When** a conformidade é verificada, **Then** as operações de
   Retificação exigem `Idempotency-Key` de fato, e não apenas no documento.

---

### User Story 6 - O ambiente de produção recusa configuração insegura (Priority: P2)

Como responsável pela implantação, quero que o sistema se recuse a iniciar em produção com
adaptador de autenticação provisório, seletor de identidade, chave secreta padrão, HTTPS desligado
ou banco mal configurado, para que a segurança não dependa de lembrar de uma variável.

**Independent Test**: Iniciar o módulo de produção com cada variável ausente ou insegura e
verificar falha imediata com mensagem que nomeia a variável.

**Acceptance Scenarios**:

1. **Given** o módulo de configuração de produção, **When** `DJANGO_SECRET_KEY` está ausente ou é
   o valor de desenvolvimento, **Then** a inicialização falha nomeando a variável.
2. **Given** o mesmo módulo, **When** `INTERFACE_SELETOR_IDENTIDADE` está ligado ou a autenticação
   configurada é o adaptador provisório, **Then** a inicialização falha explicando que não há
   fronteira de segurança.
3. **Given** o mesmo módulo, **When** `ALLOWED_HOSTS` está vazio ou contém `*`, **Then** a
   inicialização falha.
4. **Given** o módulo de produção corretamente configurado, **When** `manage.py check --deploy` é
   executado, **Then** não há achados.

---

### User Story 7 - O histórico publicado não pode ser reescrito (Priority: P3)

Como auditor, quero que Retificação, Alteração Normativa, Ato Administrativo e Revisão de Edital
tenham a mesma proteção de banco que a Versão Consolidada já tem, para que o histórico não dependa
de disciplina da aplicação.

**Acceptance Scenarios**:

1. **Given** um registro normativo publicado, **When** alguém tenta alterá-lo por `QuerySet.update()`
   ou por acesso direto ao banco com o papel de runtime, **Then** a operação é recusada pelo banco.
2. **Given** o papel de migração, **When** aplica migrações, **Then** as operações legítimas de
   esquema continuam possíveis.
3. **Given** o provisionamento do banco, **When** é executado do zero, **Then** os `GRANT`s de cada
   papel são criados por script versionado, sem etapa manual não documentada.

---

### Edge Cases

- Retificação elaborada sobre a versão consolidada mais recente, publicada sem concorrência: a
  precondição derivada confere e o ato passa. A contenção não pode transformar o caminho feliz em
  recusa.
- Retificação com `effectiveAt` futuro publicada antes de outra com vigência anterior: a
  precondição vale contra o conteúdo vigente **no início da própria vigência**, não contra o
  conteúdo de hoje.
- `ADD` em lista continua sem precondição de conteúdo — inserir não sobrescreve. A regra de
  `add_overwrites` para objeto permanece como está.
- Consulta temporal com instante ingênuo: rejeitar explicitamente em vez de assumir o fuso do
  servidor.
- `targetPath`, hashes e `X-Correlation-ID` acima do tamanho da coluna: recusar na borda HTTP com
  `422`, nunca deixar chegar ao PostgreSQL como erro `500`.

## Requirements *(mandatory)*

### Functional Requirements

**Integridade normativa**

- **FR-001**: O sistema DEVE verificar a precondição de conteúdo de toda Alteração Normativa
  `REPLACE` e `REMOVE` na publicação da Retificação, contra o conteúdo vigente no início da
  vigência do ato.
- **FR-002**: Quando o cliente não declarar `expectedPreviousHash`, o sistema DEVE derivar a
  precondição do conteúdo do `baseSnapshotId` declarado, no momento da elaboração, e persistí-la
  junto da Alteração Normativa.
- **FR-003**: O `expectedPreviousHash` declarado pelo cliente DEVE prevalecer sobre a precondição
  derivada.
- **FR-004**: A recusa por divergência DEVE identificar os caminhos divergentes e orientar a
  reelaboração sobre a versão consolidada atual.
- **FR-005**: A base declarada em `baseSnapshotId` DEVE ser o conteúdo efetivamente apresentado
  a quem elabora o ato, e DEVE ser a versão em vigor no início da vigência declarada. Quando
  divergirem — caso de uma Retificação que vigora antes de outra já publicada —, a Publicação DEVE
  recusar, e não presumir qual das duas a pessoa quis dizer.
- **FR-006**: O conteúdo que passa a vigorar após uma Retificação DEVE ser submetido às mesmas
  validações estruturais de publicação exigidas do Edital original, e erro impeditivo DEVE recusar
  o ato.
- **FR-007**: A recusa de uma Retificação NÃO DEVE deixar Publicação, documento publicado ou
  Versão Consolidada materializados.

**Autorização e sessão**

- **FR-008**: Requisições que alteram estado pela interface administrativa DEVEM exigir token
  anti-falsificação válido, e a ausência DEVE recusar a requisição sem efeito de domínio.
- **FR-009**: Respostas HTML DEVEM declarar política de enquadramento que impeça exibição em
  moldura de terceiros.
- **FR-010**: A API autenticada por cabeçalho NÃO DEVE passar a exigir token de sessão.

**Invariantes de ciclo de vida**

- **FR-011**: A criação de Edital DEVE recusar Processo Seletivo em estado final, com a mesma
  mensagem dos demais atos bloqueados por FR-035 da 001.
- **FR-012**: A criação de Edital DEVE bloquear o Processo pai na transação, de modo que
  finalização e criação concorrentes não produzam Edital em Processo já encerrado.

**Idempotência, auditoria e correlação**

- **FR-013**: Criar, submeter, homologar, devolver, cancelar e publicar Retificação DEVEM honrar
  `Idempotency-Key`, devolvendo o resultado original quando a chave e o corpo se repetirem.
- **FR-014**: A mesma chave com corpo diferente DEVE ser recusada com `409 idempotency_conflict`.
- **FR-015**: Todo evento de auditoria de Retificação DEVE gravar o identificador de correlação da
  requisição e a chave de idempotência utilizada.

**Prontidão de produção**

- **FR-016**: DEVE existir módulo de configuração de produção que falhe na inicialização quando
  chave secreta, hosts permitidos, HTTPS, cookies seguros ou autenticação institucional não
  estiverem corretamente configurados.
- **FR-017**: O módulo de produção NÃO DEVE admitir o adaptador de autenticação provisório nem o
  seletor de identidade da interface.
- **FR-018**: `manage.py check --deploy` sobre o módulo de produção NÃO DEVE apresentar achados.
- **FR-019**: O provisionamento dos papéis PostgreSQL e seus `GRANT`s DEVE ser versionado e
  executável do zero, sem etapa manual não documentada.

**Robustez de borda**

- **FR-020**: Campos de texto que alimentam colunas limitadas — `targetPath`,
  `expectedPreviousHash`, `X-Correlation-ID`, `Idempotency-Key` — DEVEM ser limitados na borda
  HTTP, com recusa de domínio em vez de erro de persistência.
- **FR-021**: Consultas temporais públicas DEVEM recusar instante sem fuso declarado.
- **FR-022**: O rascunho mantido no navegador DEVE expirar e ser descartado após prazo definido.

**Imutabilidade e desempenho**

- **FR-023**: Retificação, Alteração Normativa, Ato Administrativo e Revisão de Edital DEVEM ter
  proteção de imutabilidade no banco, equivalente à da Versão Consolidada.
- **FR-024**: A paginação do histórico NÃO DEVE carregar o conjunto completo em memória para
  ordenar.

**Lacunas funcionais herdadas**

- **FR-025**: A interface DEVE oferecer a criação de Processo Seletivo com seu primeiro Edital
  (FR-004 da 002, hoje sem implementação).
- **FR-026**: A composição DEVE validar datas, reserva de vagas e dependências condicionais antes
  do envio ao servidor (FR-006 da 002).
- **FR-027**: As pendências de revisão DEVEM ser apresentadas junto do campo a que se referem
  (FR-009 da 002).
- **FR-028**: O campo `editorialContent` DEVE ser persistido ou removido do contrato; aceitar e
  descartar em silêncio NÃO é admissível.

### Key Entities

- **Precondição de Conteúdo**: hash canônico do conteúdo que a Alteração Normativa encontrou na
  base sobre a qual foi elaborada. Declarada pelo cliente ou derivada pelo servidor; persistida com
  a Alteração; confrontada com o conteúdo vigente no momento da publicação.
- **Configuração de Produção**: conjunto de variáveis cuja ausência ou valor inseguro impede a
  inicialização. Não é documentação, é código que falha.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Os seis defeitos reproduzidos na revisão possuem teste de regressão que falha no
  código anterior e passa no corrigido.
- **SC-002**: Nenhuma Retificação publicada altera item normativo diferente do apresentado a quem
  homologou, verificado por cenário de concorrência entre atos.
- **SC-003**: Nenhum conteúdo vigente viola as invariantes estruturais exigidas na publicação.
- **SC-004**: `manage.py check --deploy` sobre o módulo de produção retorna zero achados.
- **SC-005**: A suíte completa executa também contra PostgreSQL, com os 20 testes hoje ignorados
  ativos, cobrindo concorrência, permissões de banco e migrações.
- **SC-006**: Cobertura com branches não regride abaixo do patamar atual de 89%.
- **SC-007**: Nenhuma requisição malformada de borda produz erro `500`.

## Estado da implementação

Correções emergenciais aplicadas nesta branch, sob a ressalva de correção emergencial justificada
do fluxo constitucional. Cada uma tem teste de regressão que falha no código anterior.

| Requisito | Estado | Onde |
| --- | --- | --- |
| FR-001 a FR-004 | Feito | `publicacoes/domain/conflicts.py` (`derive_preconditions`), `application/retificacoes.py` |
| FR-005 | Feito | Verificado por `test_out_of_order_publications_compose_by_validity_not_by_publication_order` |
| FR-006, FR-007 | Feito | `_assert_structurally_publishable` em `application/retificacoes.py` |
| FR-008 a FR-010 | Feito | `CsrfViewMiddleware` e `XFrameOptionsMiddleware` em `config/settings/base.py`; `tests/interface/test_csrf.py` |
| FR-011, FR-012 | Feito | `add_edital` em `processos/application/commands.py` |
| FR-013 a FR-015 | Feito | `publicacoes/api/views.py` e `application/retificacoes.py` |
| FR-016 a FR-018 | Feito | `config/settings/production.py`; `tests/test_configuracao_producao.py` |
| FR-019 a FR-028 | Aberto | Exige plano próprio |

Abertos por ordem de risco: FR-023 (imutabilidade no banco), FR-020/FR-021 (limites de borda e
instante ingênuo), FR-019 (provisionamento de papéis), FR-025 a FR-028 (lacunas funcionais da
002), FR-024 e FR-022.

Fora desta feature e ainda bloqueadores de implantação: a integração com o diretório institucional
e o endereçamento normativo por chave estável. O que esta feature entrega quanto a eles é a
barreira que impede subir sem o primeiro e a contenção que impede o dano do segundo.

## Assumptions

- A integração com o diretório institucional permanece incremento próprio. Esta feature entrega a
  barreira que impede implantar sem ela, não a integração.
- A troca do endereçamento por índice para chave estável é evolução do modelo de dados e do
  contrato público, planejada em ciclo próprio. Aqui entra apenas a contenção que torna o erro
  impossível de passar em silêncio.
- Manter `expectedPreviousHash` opcional no contrato preserva os clientes existentes; a obrigação
  passa a ser do servidor, que sempre tem a base declarada.
- Alterações Normativas persistidas antes desta feature têm precondição vazia e seguem sem
  verificação de conteúdo. Como só Retificações não publicadas importam, o volume é o das que
  estiverem em elaboração, revisão ou homologadas no momento da implantação; reenviar o rascunho
  as regulariza. Um backfill é dispensável e fica registrado como decisão, não como omissão.

## Out of Scope

- Integração com LDAP/SUAP e o ciclo de vida de sessão institucional.
- Endereçamento normativo por chave estável (UUID) e a migração das Retificações existentes.
- Requisitos de acessibilidade ainda abertos na 002 (CSP, leitores de tela, ASES, contraste).
- Qualquer funcionalidade nova de domínio.

## Dependencies

- Features `001-processo-seletivo-editais` e `002-frontend-administrativo` no estado do commit
  `b12b8f6`.
- PostgreSQL disponível para a execução completa da suíte (SC-005).
