# Research: Interface Administrativa

**Nota sobre a ordem.** O `plan.md` prevê este documento na Fase 0, antes da implementação. Não foi
o que aconteceu: as seis histórias foram implementadas primeiro e este registro veio depois. Ele
descreve o que de fato foi decidido e descoberto, incluindo onde a realidade divergiu do plano.
Registrar a divergência é o ponto — um documento que fingisse antecedência valeria menos que
nenhum.

## 1. Design system do SUAP

**Decisão do plano**: usar o [design system do SUAP](https://suap.ifrn.edu.br/comum/design_system/),
que é feito para templates Django e traz tema gov.br, alto contraste e modo daltonismo.

**O que aconteceu**: o design system **não foi obtido**. O `plan.md` registrava um ponto de
confirmação — como ele é distribuído e licenciado para uso fora do SUAP — e essa confirmação
depende de quem administra o SUAP no Ifes. Sem ela, foi escrito CSS próprio, inspirado na
organização visual do SUAP (cabeçalho institucional escuro, cartões, chips de situação, passos
numerados), com cerca de 200 linhas embutidas em `base.html`.

**Consequência**: os três temas que o design system traria não existem. Alto contraste e modo
daltonismo eram parte do que adiantaria FR-024; hoje há uma paleta única, verificada em WCAG 2.1 AA
(ver [accessibility.md](./accessibility.md)).

**Custo de trocar depois**: baixo para o HTML, que é semântico e não depende das classes do design
system; a troca é de folha de estilo. O que não é baixo é a decisão institucional pendente.

**Pendente**: confirmar com quem administra o SUAP no Ifes se há pacote distribuível, se o CSS pode
ser incorporado e se o Ifes mantém customização própria.

## 2. HTMX: versão, obtenção e convivência com CSP

**Decisão**: HTMX 2.0.4, servido pelo próprio projeto em
`processo_seletivo/interface/static/interface/htmx.min.js` (50.917 bytes), sem CDN.

**Rationale**: um arquivo estático servido pelo próprio serviço não depende de rede externa em
ambiente institucional, não vaza navegação para terceiros e não quebra quando um CDN muda. HTMX 2 não
tem dependências.

**Descoberta que custou caro**: o arquivo foi colocado em `backend/static/`, que o Django **não
varre** — `AppDirectoriesFinder` procura `static/` dentro de cada app e `FileSystemFinder` olha
`STATICFILES_DIRS`, que estava vazio. O arquivo existia, o template o referenciava, e o navegador
recebia 404. Sem a biblioteca, `hx-get` e `hx-target` são atributos inertes: nenhum botão dinâmico
funcionava, e compor um Edital pela interface era impossível. Nenhum teste alcançava isso porque
todos exercitavam os endpoints de fragmento diretamente. Hoje há teste que resolve cada
`<script src>` pelos finders do Django.

**CSP**: o plano pedia confirmar como o HTMX convive com Content Security Policy. **Não há CSP
configurada** neste projeto, então a questão não se colocou. Ela volta antes de produção, e há um
ponto de atenção: `hx-vals='js:{...}'` — usado para gerar o índice de cada linha nova — exige
`allowEval`, que uma CSP com `unsafe-eval` proibido bloquearia. A alternativa é o servidor gerar o
índice, o que é mudança pequena mas precisa ser feita antes de haver CSP.

**Alternativa descartada**: Alpine.js. Resolveria o mesmo com estado no cliente, mas HTMX mantém o
servidor como fonte do fragmento, que é coerente com a Decisão 2 do plano.

## 3. Ferramenta de verificação de acessibilidade

**Decisão**: [axe-core](https://github.com/dequelabs/axe-core) 4.13.0, executado no navegador sobre
as telas renderizadas, com as regras `wcag2a`, `wcag2aa`, `wcag21a` e `wcag21aa`.

**Rationale**: axe-core é a base dos verificadores mais usados (Lighthouse, WAVE em parte, extensões
do Chrome e Firefox), tem licença MPL-2.0, não exige serviço externo e roda contra a página real —
o que importa porque contraste só é verificável com o CSS aplicado.

**Alternativas consideradas**:

- **ASES**, o avaliador do próprio Governo Federal para eMAG. É a referência normativa brasileira,
  mas é uma aplicação desktop Java e não se integra a uma suíte automatizada. Continua sendo o que
  vale para uma verificação oficial de eMAG, e não foi executado.
- **pa11y** e **Lighthouse CI**: ambos embrulham axe-core; acrescentariam Node ao ciclo de teste sem
  acrescentar cobertura.

**Limites medidos, não presumidos** (detalhe em [accessibility.md](./accessibility.md)):

- axe-core **não avalia estados de interação**: um contraste que só falha no `:hover` passa. Um caso
  real foi encontrado assim, no cálculo manual dos pares de cor.
- axe-core **aprova um link de salto que não funciona**: ele confere que o link e o alvo existem,
  não o que acontece ao ativar. O link de salto desta interface movia a rolagem e não o foco.
- A ferramenta cobre por volta de um terço dos critérios da norma. Leitor de tela com pessoa usuária
  real continua sendo exigência não substituível, e continua pendente.

## 4. Rascunho no navegador (FR-020)

**Decisão do plano** (Decisão 5): o conteúdo em preenchimento vive no armazenamento do navegador,
associado ao Edital e à pessoa, e é descartado quando o domínio aceita o envio.

**O que aconteceu**: **não foi implementado.** Não há `localStorage` nem `sessionStorage` no código
da interface.

O que existe é preservação no servidor: quando o domínio recusa, a view relê o que foi digitado e
reexibe com "O que você digitou foi preservado abaixo". Isso cobre recusa, que é o caso frequente, e
**não cobre os dois casos que FR-020 nomeia** — expiração de sessão e falha de comunicação. Nos dois,
o conteúdo se perde.

FR-020 e SC-007 estão, portanto, não atendidos. Consta como tarefa em [tasks.md](./tasks.md).

## 5. Identidade durante o desenvolvimento

**Decisão**: um seletor de identidade em `/gestao/identificar`, sob a variável
`INTERFACE_SELETOR_IDENTIDADE`, que grava pessoa e papéis na sessão do Django.

**Rationale**: permite exercitar segregação de funções e diferenças de permissão sem LDAP, que é
justamente o que a validação com servidores do Cefor precisa.

**Garantia verificada**: com a variável desligada, a rota devolve 503 e nenhum papel aparece no HTML.

**⚠️ Não é fronteira de segurança.** O adaptador de desenvolvimento do backend aceita
`Bearer <pessoa>|<escopo>|<permissões>`: qualquer pessoa declara qualquer identidade. Esta feature
não é implantável em produção antes da autenticação institucional. Está registrado na especificação,
no plano e aqui.

## 6. Papéis e permissões

**Decisão**: cinco papéis fixos em `identidade.py` — elaborador, homologador, publicador, gestor e
auditor —, cada um mapeando um conjunto de permissões que o backend já reconhece.

**Rationale**: FR-025 perguntava a origem das permissões e a resposta escolhida foi "o que for mais
simples inicialmente". Papéis fixos no código não exigem esquema novo nem tela de administração, e
tornam explícito o que cada um pode — a tela de identificação lista as permissões de cada papel.

**Consequência**: qualquer mudança de papel é mudança de código. Aceitável enquanto a origem real for
o diretório institucional, que trará seus próprios grupos.
