# Feature Specification: O assistente na página do Edital, no desenvolvimento local

**Feature Branch**: `claude/assistente-pagina-edital-local-d6f44f`, sobre a `main` `bc6dd96b` (com o
protótipo da Fase C, #280)

**Created**: 2026-10-14

**Status**: Implementada — o percurso com o modelo real é do responsável pelo produto

**Input**: correção de premissa do responsável pelo produto, em 14/10/2026: *"o sistema existe apenas
no meu computador. Não há implantação pública nem candidatos reais utilizando-o. Quero concluir a
experiência local do assistente na página real de cada seleção, acessível pela visão do candidato,
sem precisar entrar como gestor para testar."* Sem nova auditoria, sem reconstruir o que já
funciona, e sem condicionar a entrega à autenticação institucional, à `073`, à L4 ou aos requisitos
de lançamento público.

> **Faixa de identificadores.** Esta spec abre em FR-1680 e SC-640, acima da faixa que a `073`, em
> worktree paralela, já tomou.

---

## Por que esta feature existe

A `071` tratou o assistente como piloto **interno**: só na gestão, com permissão própria, e nenhuma
rota pública (`FR-1460` a `FR-1464`). O protótipo da Fase C (#280) desenhou o painel sobre a página
pública verdadeira, mas na rota da gestão, com o mesmo acesso do piloto. Para testar a experiência
**como candidato**, era preciso entrar como gestor — o que mede a tela, e não o percurso.

O rigor era o de um sistema em produção, e o sistema só existe na máquina de desenvolvimento. Esta
feature abre o painel na página pública da seleção **só ali**, por chave de desenvolvimento, e deixa
registrado o que a abertura de verdade vai pedir.

**O que continua valendo, e não se negocia aqui:** as fontes vigentes no instante (`070`), a
separação das conversas, a credencial só no servidor e os limites de chamada que já existem. E,
com o OpenRouter, a pergunta livre ainda sai da máquina e custa — a página ser local não muda isso.

### Relação com a `071`

O `FR-1462` da `071` ("nenhuma rota pública") continua valendo para o piloto e para qualquer
implantação: esta feature não o revoga. Ela acrescenta uma exceção de **desenvolvimento local**,
desligada por padrão e recusada por produção (`FR-1683`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O candidato conversa com o assistente na página da seleção (Priority: P1)

Na máquina de desenvolvimento, com a chave ligada, quem abre a página pública de uma seleção vê o
botão "Dúvidas sobre este Edital", abre o painel, escolhe uma pergunta sugerida (e a opção, quando
o Edital tem mais de uma), faz uma pergunta livre de continuação e começa uma conversa nova — sem
entrar na gestão e sem se identificar no portal.

**Independent Test**: com a chave ligada, um cliente sem sessão de gestão percorre o painel; com a
chave desligada, nem o painel nem as rotas existem.

**Acceptance Scenarios**:

1. **Given** a chave desligada (o padrão), **When** alguém abre a página da seleção ou envia para as
   rotas do assistente, **Then** a página não traz o painel e as rotas respondem 404.
2. **Given** a chave ligada, **When** um visitante sem identidade abre a página com `?painel=1`,
   **Then** o painel abre, com os envios apontando para o portal e nenhum para a gestão.
3. **Given** a chave ligada, **When** o visitante escolhe "Que documentos preciso enviar?" num Edital
   com mais de uma opção, **Then** o painel pergunta "Para qual opção?" e, escolhida, responde pela
   `070`, sem chamar o modelo.
4. **Given** uma sugestão respondida, **When** o visitante pergunta "Preciso enviar todos?", **Then**
   a pergunta segue pela mesma `perguntar` do piloto, com a sugestão no histórico.
5. **Given** uma conversa nesta sessão e neste Edital, **When** a mesma pessoa abre outro Edital, ou
   outra sessão abre este, **Then** a conversa não aparece; "Nova conversa" começa do zero, até o
   teto de conversas da sessão naquele Edital.
6. **Given** um visitante que só lê a página, **When** ela é mostrada, **Then** nada é gravado na
   sessão: a conversa nasce no primeiro envio.

### Edge Cases

- **Edital sem página pública** (inexistente, rascunho, sem versão vigente): os envios respondem 404
  e nada chega ao modelo.
- **Os estados simulados** (`?simulacao=`) continuam só do protótipo da gestão: na página pública o
  parâmetro é ignorado.
- **O protótipo da gestão com a chave ligada** continua com um painel só — o dele.
- **Serviço não configurado** (sem tokenizer, sem credencial): as sugestões respondem; a pergunta
  livre termina no estado explícito da `071` (`SEM_TOKENIZER`, `INDISPONIVEL`), sem chamada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1680**: Com a chave de desenvolvimento `ASSISTENTE_NA_PAGINA_DO_EDITAL` ligada, a página
  pública de cada seleção MUST oferecer o painel do assistente, sem exigir a identidade da gestão nem
  a do candidato. Desligada — o padrão em todo módulo de configuração —, a página MUST NOT trazer o
  painel, e as rotas do assistente no portal MUST responder 404.
- **FR-1681**: O painel e os envios MUST ser os do protótipo da Fase C: as sugestões respondidas pela
  `070`, a pergunta livre pela `perguntar` da `071`, a espera, a falha e a mudança de versão como já
  estão. Nenhuma arquitetura de conversa nova; os estados simulados ficam só no protótipo da gestão.
- **FR-1682**: A conversa MUST ser da sessão e do Edital, com chave de sessão própria — separada da
  do protótipo e da tela técnica —, e "Nova conversa" MUST começar outra. A página que traz o painel
  MUST NOT ir para cache compartilhado.
- **FR-1683**: Produção MUST recusar subir com a chave ligada, como recusa o seletor de identidade.
- **FR-1684**: Os requisitos da abertura ao público MUST ficar registrados como pendências da
  implantação, e MUST NOT bloquear o desenvolvimento local (ver *Pendências para a implantação*).
- **FR-1685**: Os envios MUST manter o que já protege o piloto: as fontes vigentes no instante, a
  credencial só no servidor, o registro sem identidade, e os limites existentes — tamanho da
  pergunta, turnos por conversa, teto de chamadas simultâneas e o limite de gasto da chave. Como o
  limite de turnos é por conversa, a página pública MUST limitar também as conversas que uma sessão
  abre em cada Edital (`ASSISTENTE_CONVERSAS_POR_SESSAO`), para que "Nova conversa" não dê turnos
  novos sem fim; o limite por visitante, que não dependa do cookie, é pendência da implantação.

### Key Entities

Nenhuma nova. A troca continua a `TrocaDoPiloto` da `071`, com a origem `TELA`.

## Success Criteria *(mandatory)*

- **SC-640**: Com a chave ligada, um visitante sem identidade percorre a página da seleção — abre o
  painel, recebe uma sugestão, escolhe a opção, faz uma pergunta livre e começa conversa nova —,
  provado em teste e no navegador.
- **SC-641**: Com a chave desligada, a página não traz o painel e as três rotas respondem 404; com
  ela ligada, produção não sobe.
- **SC-642**: Conversas de sessões ou Editais diferentes não se misturam, nem a da página com a do
  protótipo.

## Pendências para a implantação

Registradas, e não bloqueios deste incremento (`FR-1684`). Cada uma é decisão ou trabalho da
abertura ao público:

| Pendência | Onde está |
|---|---|
| Autenticação institucional da gestão (lacuna B-1) e o lugar da página pública na implantação | guia de implantação; `073` |
| Configurar e verificar a implantação pela linha de comando | `073`, em worktree própria |
| A avaliação no Ollama da L4 e as medições | tarefas T058 a T060 da `071` |
| A sessão acompanhada com o setor de seleção | tarefa T065 da `071` |
| Limites por visitante (por endereço ou por sessão) e a proteção contra uso automatizado | a definir na spec da Fase C pública |
| A avaliação de LGPD do texto livre de candidatos reais, e a retenção | a definir com o setor |
| O texto definitivo das falhas e da apresentação (o `DA-01` da auditoria) | spec da Fase C pública |
| A revisão das fontes de cada Edital antes de abrir (os pontos da `070`) | spec da Fase C pública |
| O critério de aceite da qualidade das respostas (DP-3 da `071`) | `071` |

## Decisões

### D-001 — Uma chave própria, e não a do piloto

O `ASSISTENTE_PILOTO` controla o acesso da gestão, e o teste local não deveria abri-lo; a chave nova
controla só a página pública, e produção recusa só ela. As duas são independentes: as sugestões
respondem sem modelo, e a pergunta livre cai num estado explícito sem serviço configurado.

### D-002 — As rotas no portal, o painel do protótipo

Os envios moram no portal, ao lado da página da seleção, e chamam as mesmas funções do protótipo,
que passou a recebê-las com a conversa e o destino. A página da seleção renderiza o fragmento do
protótipo. A alternativa — copiar o painel para o portal — faria duas telas que precisam concordar.

### D-003 — A origem continua `TELA`, sem migration

Distinguir a origem "página pública" exigiria migration num registro que se exclui em 90 dias, para
uma diferença que só existe no desenvolvimento local. Fica para a spec da Fase C pública, se a
avaliação precisar separar.

### D-004 — Um teto de conversas por sessão, e não um limite por visitante

A revisão de código mostrou que "Nova conversa" zerava o limite de turnos. Contar as perguntas de
todas as conversas da sessão tornaria falsa a mensagem do limite ("comece uma nova conversa"); um
teto de conversas por sessão e Edital mantém a mensagem verdadeira e fecha o atalho do botão. Quem
descarta o cookie escapa dele, e é por isso que o limite por visitante continua na lista da
implantação.

## Assumptions

- A chave só se liga numa máquina de desenvolvimento, por variável de ambiente; nenhum módulo de
  configuração a liga sozinho.
- O custo do OpenRouter continua limitado só pelo limite de gasto da chave (DP-4 da `071`).
