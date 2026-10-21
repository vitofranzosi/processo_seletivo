# Feature Specification: A recusa da verificação anti-falsificação na moldura do sistema

**Feature Branch**: `claude/relaxed-bartik-660e4a`, sobre a `main` em `745f115f`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: o resíduo que a `091` e a `092` registraram e não resolveram (a pesquisa da `091`, na lista
do que ficou; o R-008 da `092`): quando a verificação anti-falsificação recusa um envio, quem responde
é a página do próprio framework, que traz o estilo embutido. Sob a política de segurança de conteúdo
em recusa, o navegador não aplica esse estilo, e a página aparece sem desenho, na gestão e no portal.
Trocá-la por uma página do sistema, na moldura da área de onde o envio veio, com status 403 e uma
mensagem em português que diga o que aconteceu e o que fazer — sem afrouxar a política, sem
dependência nova, sem regra de negócio nem permissão nova.

> **Faixa de identificadores.** Esta spec usa FR-2150 a FR-2160 e SC-827 a SC-829. A faixa reservada
> era FR-2150–2169 e SC-820–829; na `main` (`745f115f`) o maior FR é FR-2145 e o maior SC é SC-826,
> da `092`, que já tomou SC-820 a SC-826. Os três SC desta spec são os que sobram da reserva.

---

## Por que esta feature existe

**A recusa mais comum é a de quem não fez nada de errado.** A verificação existe para que uma página
de fora não pratique atos em nome de quem está com a sessão aberta (a FR-008 da `003`). Mas quem mais
a encontra é a pessoa legítima: o formulário que ficou aberto numa aba por muito tempo, o navegador que
apagou os dados do site, a página guardada e reaberta. A `092` registrou o caso mais provável: o
candidato com a página aberta desde ontem que clica em Enviar ou em Sair.

**E o que ela vê hoje não lhe diz nada.** A página do framework é em inglês, fala em "CSRF" e em
"cookie", e — desde que a política passou a recusar estilo embutido — aparece sem desenho, sem o
cabeçalho do sistema, sem um caminho de volta. Não diz que nada foi gravado, que é o que a pessoa
precisa saber antes de qualquer outra coisa, nem o que fazer para enviar de novo.

**O que não muda, e não se negocia aqui:** quais envios a verificação recusa e quais aceita; a
política de segurança de conteúdo; nenhuma isenção nova; nenhuma regra de negócio, permissão, dado ou
dependência.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O candidato cujo formulário expirou (Priority: P1)

A candidata deixou a página de inscrição aberta de um dia para o outro, e nesse meio tempo o navegador
apagou os dados do site. Ela clica em Enviar. Em vez de uma página crua em inglês, vê o portal de
sempre — o cabeçalho, a folha, o "Voltar às seleções" —, com um título que diz que o formulário não
pôde ser enviado, a frase "Nada foi gravado", o motivo em palavras dela (o formulário expirou ou veio
de outra página) e o que fazer: voltar, recarregar a página e enviar de novo, copiando antes o que
tiver digitado. Um link reabre a página de onde ela veio.

**Why this priority**: é quem mais encontra a recusa, e o canal em que a página crua mais confunde.

**Independent Test**: enviar um formulário do portal sem a prova anti-falsificação e ler a resposta:
status, moldura, texto e cabeçalho da política; abri-la no navegador e ler o console.

**Acceptance Scenarios**:

1. **Given** um formulário do portal, **When** enviado sem a prova anti-falsificação válida, **Then** a
   resposta é 403, na moldura do portal, com o título, a frase "Nada foi gravado" e o que fazer.
2. **Given** essa resposta, **When** aberta no navegador a 1280 e a 375 px, **Then** ela aparece com o
   desenho do portal e o console não registra violação da política.
3. **Given** que a página de origem era do próprio sistema, **When** a recusa é servida, **Then** um
   link reabre essa página; **Given** que a origem era outro site ou é desconhecida, **Then** o link não
   aparece.

---

### User Story 2 — O servidor na gestão (Priority: P1)

O servidor preenche uma tela da gestão numa aba aberta há muito tempo e envia. A recusa aparece com o
cabeçalho e a barra da gestão, a mesma mensagem e um link que reabre a tela como está gravada.

**Why this priority**: a gestão é onde os atos irreversíveis acontecem; quem lê a recusa precisa saber,
antes de tudo, que nada foi gravado.

**Independent Test**: o mesmo da história 1, sob `/gestao/`.

**Acceptance Scenarios**:

1. **Given** um formulário da gestão, **When** enviado sem a prova válida, **Then** a resposta é 403,
   na moldura da gestão, com a mesma mensagem.
2. **Given** essa resposta, **When** aberta no navegador a 1280 e a 375 px, **Then** ela aparece com o
   desenho da gestão e sem violação da política.
3. **Given** um ato irreversível enviado sem a prova, **When** recusado, **Then** nada é gravado —
   como hoje.

---

### User Story 3 — Quem mantém o sistema descobre o motivo (Priority: P2)

A pessoa que administra o sistema recebe o relato de um candidato que "não conseguiu enviar". A página
não lhe mostrou o motivo técnico; o registro do servidor mostra, com o endereço do envio.

**Why this priority**: tirar o motivo da página não pode tirá-lo de quem precisa diagnosticar.

**Independent Test**: provocar a recusa e ler o registro.

**Acceptance Scenarios**:

1. **Given** uma recusa da verificação, **When** servida, **Then** o registro do servidor traz o
   motivo técnico e o endereço, e a página não traz nenhum dos dois termos técnicos.

### Edge Cases

- **Um envio de fato forjado, vindo de outro site.** A recusa é a mesma página, e o link de reabrir
  não aparece: a origem é de fora, e o sistema não oferece link para ela (FR-2156).
- **A origem é desconhecida** (o navegador não informou de onde veio). Sem link de reabrir; o texto
  basta, e o "Voltar" do portal ou da gestão continua.
- **Envio fora das duas áreas.** Não há hoje formulário do sistema fora de `/gestao/` e `/selecoes/`
  que passe pela verificação — a API é isenta e autentica por cabeçalho. Se um vier a existir, a recusa
  sai na moldura do portal, que é a pública (D-002).
- **Servidor local com depuração ligada.** A página é a mesma do sistema, e não a técnica do framework
  (D-003); o motivo fica no terminal do servidor.
- **Envio feito por fragmento (htmx)** — a barra de documentos do portal. O htmx não troca a página por
  resposta 4xx: o botão parece não responder, como hoje. Registrado, e não resolvido aqui (R-004).
- **O candidato com sessão aberta.** A moldura do portal mostra o "Sair", que é um formulário: a página
  de recusa emite uma prova nova, e o "Sair" dela funciona.
- **A página com estilo ou script embutido.** Não pode haver: a recusa é servida por modelos que já
  passam pelos guardiões da `091` e da `092`.

## Requirements *(mandatory)*

### Functional Requirements

#### A página

- **FR-2150**: A recusa da verificação anti-falsificação de um envio sob `/gestao/` MUST ser servida
  pela página de recusa da gestão, com o cabeçalho e as folhas da gestão.
- **FR-2151**: A recusa de qualquer outro envio MUST ser servida pela página de recusa do portal, com o
  cabeçalho e a folha do portal (D-002).
- **FR-2152**: A resposta MUST ter status 403.
- **FR-2153**: A página MUST dizer, em português e sem termo técnico: que o formulário não pôde ser
  enviado; que nada foi gravado; que o formulário expirou ou veio de outra página; e o que fazer —
  voltar, recarregar a página e enviar de novo, copiando antes o que se quiser manter. O texto MUST ser
  o mesmo nas duas áreas (D-004).
- **FR-2154**: A página MUST NOT exibir o motivo técnico da recusa, nem os termos "CSRF", "token",
  "cookie" ou "Referer".
- **FR-2155**: O motivo técnico e o endereço do envio MUST ir ao registro do servidor, em nível de
  aviso.
- **FR-2156**: Quando a página de onde o envio veio é do próprio sistema, a recusa MUST oferecer um
  link que a reabre; quando é de outro site, ou desconhecida, MUST NOT oferecer link nenhum para ela
  (D-005).
- **FR-2157**: A página MUST NOT conter estilo nem script embutido, e MUST receber a política de
  segurança de conteúdo em recusa, a mesma das outras páginas.

#### O que não muda

- **FR-2158**: A verificação MUST recusar exatamente os envios que recusa hoje: nenhuma isenção nova,
  nenhum envio passa a ser aceito, e a API continua isenta e autenticada por cabeçalho.
- **FR-2159**: A política de segurança de conteúdo MUST NOT mudar, nem ganhar exceção para esta
  página.
- **FR-2160**: A página MUST ser a mesma com a depuração ligada e desligada (D-003); nenhuma
  dependência, regra de negócio, permissão ou dado MUST mudar.

### Key Entities

Nenhuma. Só a página que responde a uma recusa que já existe.

## Decisões

### D-001 — Uma view, e não só um modelo

O framework aceita trocar só o modelo da página de recusa. Mas ele o renderiza sem a requisição: sem
ela, o modelo não sabe de que área veio o envio, nem quem está identificado, e as bases da gestão e do
portal não se compõem — o cabeçalho depende da identidade, a barra da gestão, das capacidades. Uma view
própria recebe a requisição, escolhe a moldura pelo caminho e renderiza as recusas que já existem, com
os processadores de contexto de sempre. Ela mora em `interface/erros.py`, junto das outras duas
traduções de recusa em página.

### D-002 — Fora da gestão, a moldura do portal

As recusas do domínio só se traduzem sob os dois prefixos, e fora deles deixam a resposta do
framework. Esta não pode deixar: a resposta do framework é a que sai sem desenho. Fora de `/gestao/`,
a moldura é a do portal, que é a pública: a página da gestão, para quem não é servidor, mostraria o
cabeçalho institucional a quem não lhe diz respeito — o mesmo motivo que levou a raiz a mandar o
navegador à vitrine.

### D-003 — A mesma página com depuração ligada

Com a depuração ligada, o framework mostra uma página técnica com o motivo, e ela escaparia da
política pela marca da depuração (a decisão 010 da `091`). Esta view responde igual nos dois casos: o
runserver mostra o que a produção mostra, e o motivo, que é o que a página técnica acrescentaria, já
vai ao registro, que no runserver é o terminal.

### D-004 — Um texto para as duas áreas

O que aconteceu e o que fazer não mudam de uma área para a outra, e o texto foi escrito para quem se
inscreve, que é o leitor mais distante do sistema. Duas redações seriam duas para manter. O que muda é
a moldura e o rótulo do link de reabrir: "Reabrir a tela como está gravada", na gestão, que já é o
rótulo da recusa do envio grande; "Abrir a página do formulário de novo", no portal.

### D-005 — O link de reabrir só para o próprio sistema

O link vem da página que o navegador informa como origem do envio. Numa falsificação de fato, essa
origem é o site do atacante, e um link para ela seria o sistema convidando a pessoa a voltar lá. A
origem só vira link quando é do próprio servidor, pela mesma conferência que a recusa do envio grande
já faz; o código dela passa a ser um só, usado pelas duas.

## Success Criteria *(mandatory)*

- **SC-827**: Enviado sem a prova anti-falsificação um formulário da gestão e um do portal, as **duas**
  recusas aparecem com o desenho da área, a 1280 e a 375 px, com **zero** violações da política no
  console e **zero** estouros de largura.
- **SC-828**: **Zero** ocorrências, na página de recusa, do motivo técnico e dos termos "CSRF",
  "token", "cookie" e "Referer"; e **todas** as recusas trazem o motivo no registro do servidor.
- **SC-829**: A suíte contra PostgreSQL continua sem falhas, e **nenhum** dos testes da verificação
  anti-falsificação que existiam antes desta feature muda.

## Assumptions

- A verificação anti-falsificação continua sendo a do framework, com a prova num cookie (e não na
  sessão); esta feature só troca quem escreve a página da recusa.
- "Moldura" é a base da área — cabeçalho, folhas, identidade —, e a página de recusa que cada área já
  tem: a desta feature não é um terceiro desenho.
- A mensagem não precisa distinguir as causas (prova ausente, prova trocada, origem de fora): para
  quem lê, o que fazer é o mesmo em todas, e distinguir exigiria expor o motivo.
