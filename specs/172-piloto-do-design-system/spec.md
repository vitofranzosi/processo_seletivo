# Feature Specification: O piloto do design system em três telas

**Feature Branch**: `claude/172-piloto-do-design-system`, nascida da `main` em `c0f715c9` (depois
do merge da P0, PRs #557 e #559, e da Visão do Sistema, #560)

**Created**: 2026-11-15

**Status**: Especificada, planejada e com tarefas em 15/11 (#563, mergeada). **Implementada no mesmo dia**,
na branch `claude/172-piloto-implementacao`, sem merge: as três telas, a fotografia de 64 estados, a
comparação, a conferência de acessibilidade e o levantamento dos guardiões. O resultado, os desvios e
os achados estão em [relatorio.md](relatorio.md). **A validação com a equipe (US4) não aconteceu**: o
roteiro, os bancos e as duas versões estão prontos, e as sessões são do usuário. O merge é do usuário.

**Input**: o terceiro passo da sequência que o usuário aprovou para o estudo de design system
(`doc/auditoria-design-system-2026-11-14/`, mergeado no #549): *"a spec do piloto pelo Spec Kit,
com a confirmação de ato, a Ocupação de vagas e a Lista de Processos"*. O piloto está no
`05-roadmap.md`, seção *O piloto*, a direção experimental no `03-design-system.md`, os três
pareceres no `06-revisao.md`, os estados da Ocupação no `07-fixtures-da-ocupacao.md`, e a P0 e a
referência no `08-p0.md` e em `referencia-p0/`.

> **Faixa de identificadores.** Esta spec abre em **FR-7700**, **SC-2600** e **UX-850**, e reserva
> até o requisito sete mil setecentos e noventa e nove. Os tetos medidos em 15/11/2026, somando
> todas as worktrees, eram o requisito sete mil seiscentos e seis, o critério dois mil quinhentos e
> onze e o requisito de experiência oitocentos e vinte e dois. Na `main`, o teto é da `170`. As
> decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-2807 da `104`"). Uma decisão de outra feature é citada pelo assunto e pela
> feature. Os itens do estudo (`S1` a `S11`, `P0.1` a `P3.6`, as decisões 1 a 9 do roadmap) são
> dele, e são citados por extenso.

---

## Por que esta feature existe

O estudo de 14/11 mostrou que o GPS tem fundação sólida, mas não tem contratos de composição: 71
aberturas de página em 89 telas, 63 regras de caixa, 28 de aviso, quatro alturas para o mesmo botão.
Ele propôs uma direção visual (os neutros da tela de entrada, o cabeçalho de página, três
composições, botão, indicador, aviso e cartão) e mostrou, em protótipos, que ela é **viável**. Não
mostrou que ela **opera melhor**: os protótipos resumem conteúdo, usam outra quantidade de registros
e encurtam textos decididos em spec.

O piloto existe para responder a essa pergunta. **Com o mesmo conteúdo e o mesmo comportamento, a
composição nova opera melhor?** A resposta vem de três telas, com o estilo novo delimitado a elas,
comparadas consigo mesmas no mesmo estado e lidas pela equipe nas duas versões. A migração das
outras telas **não** é decidida aqui. Ela depende do que o piloto devolver, e a decisão é do
usuário.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| A confirmação de ato do Edital (`confirmar.html`) nos **sete** atos que ela serve | as confirmações do Processo e da Retificação, que dividem com ela a folha da P0 (D-002) |
| A Ocupação de vagas (`ocupacao.html`) e as **duas conferências** dela (D-001) | o Histórico da ocupação, que só lê |
| A Lista de Processos Seletivos (`lista.html`), sem a coluna "Fase e próximo passo" | a coluna, que é informação nova e continua sendo a decisão 9 do roadmap |
| A fotografia dos estados antes e depois, e o inventário de conteúdo de cada um | um guardião novo: nenhum entra no aceite (D-009) |
| A conferência manual de acessibilidade das cinco telas | a acessibilidade das outras telas |
| A validação com a equipe, nas versões antiga e nova | um teste formal de usabilidade |
| Os tokens novos, só acrescentados | apontar `--texto`, `--borda` e `--fundo` para os novos (decisão 8 do roadmap) |
| O levantamento do que cada guardião candidato protegeria | criar os guardiões (decisão 7) |

**Ficam adiados, e não só fora do escopo** (terceiro parecer): a redução tipográfica, o
recolhimento e o deslocamento de explicações, a coluna "Fase e próximo passo" e toda mudança global
de CSS. O experimento opcional de escala tipográfica do roadmap não é desta spec.

---

## Clarifications

### Session 2026-11-14 (a sequência e as condições do usuário, nos três pareceres)

- A direção visual vale **como experimento, só nas telas do piloto**. A migração completa só se
  decide depois dos resultados.
- O estilo fica delimitado **por folha de grupo e classe de escopo**, sem mudança global de `.acao`
  e sem guardião novo no aceite.
- As telas mantêm a fonte, os tamanhos, os textos completos e as ações. Nada é recolhido, resumido
  ou movido para dentro de um recolhido.
- O aceite confere **textos, quantidades, associações e ações como conjunto**. A ordem tem critério
  próprio, com as sequências que não se invertem declaradas nesta spec.
- A spec diz **explicitamente** se as duas telas de conferência da Ocupação entram (D-001).
- As confirmações se avaliam **pelo entendimento das consequências e pela prevenção de erro**, e não
  só pela aparência (D-007).
- A validação com a equipe executa **as mesmas tarefas** na versão antiga e na nova (D-008).

### Session 2026-11-15 (o pedido desta spec)

- A spec decide os seis pontos que o pedido nomeou: as conferências (D-001), os estados fotografados
  (D-004), o caminho até a imagem (D-005), o aceite por conjunto (D-006), a avaliação das
  confirmações (D-007) e a validação com a equipe (D-008). Cada decisão está tomada para que o plano
  possa existir, e **o usuário pode revê-la na leitura do PR**. Nenhuma ficou como pergunta, porque
  todas têm um caminho razoável que os documentos do estudo já apontam.

### Session 2026-11-15 (o usuário, depois de ver o antes e o depois do piloto implementado)

- Q: A primeira versão prendeu toda prosa em 80 caracteres e centrou a confirmação numa coluna
  estreita, e o usuário a achou pior que a `main` ("o texto não está utilizando o espaço
  disponível"). Como as telas devem usar a largura? → A: **o texto ocupa a largura do conteúdo**,
  inclusive onde a `main` hoje o limita; ficam os cartões, os indicadores e os botões (D-012). A
  FR-7704, a FR-7730, a SC-2603 e a UX-850 foram revistas por esta decisão.
- Na segunda leitura, o usuário pediu três padrões, para generalizar: indicadores que dividem a
  linha em partes iguais; campos de texto na largura do formulário; e "rótulo: valor" na mesma
  linha em toda lista de definição. Entram na D-012. A tela de um notebook citada no pedido foi só
  exemplo, e não critério de medida.

---

## User Scenarios & Testing *(mandatory)*

Os atores são as pessoas da equipe de seleção, pelos papéis que já existem: quem elabora, homologa,
publica e encerra o Edital; quem apura a ocupação (quem emite) e quem só a lê; e qualquer pessoa da
gestão que abre a Lista de Processos. O piloto não cria papel, permissão nem rota.

### User Story 1 — Quem confirma um ato sabe o que vai acontecer, e não confirma o ato errado (Priority: P1)

Quem abre a confirmação de um dos sete atos do Edital (submeter, homologar, devolver, revogar a
homologação, publicar, encerrar e cancelar) lê, numa coluna centrada e na medida de leitura, o que
impede o ato, o que o deixa seguir com atenção, o que ele provoca e se ele se desfaz, e só depois o
formulário e o botão. O conteúdo é o mesmo de hoje, palavra por palavra. O que muda é a composição:
cabeçalho de página, avisos como componente, com a marca de espécie da P0 ("Impedimento:",
"Atenção:"), as consequências em destaque e a barra de ações ao pé.

**Why this priority**: é a tela de maior consequência do sistema, um template que serve sete rotas,
e é onde o terceiro parecer pediu que o critério seja o entendimento e não a aparência.

**Independent Test**: abrir cada um dos doze estados da confirmação (C-01 a C-12) antes e depois,
conferir o inventário e as sequências, e pedir à equipe que diga, sem confirmar, o que o ato
provoca, o que impede e se ele se desfaz.

**Acceptance Scenarios**:

1. **Given** o Edital em Publicado com uma pendência que impede o encerramento e uma que continua
   depois dele, **When** quem pode encerrar abre "Encerrar", **Then** o que impede aparece antes do
   que continua, os dois antes das consequências, e as consequências antes do motivo; o botão de
   confirmar não aparece, como hoje; e todo bloco de texto de antes existe depois, com as mesmas
   palavras.
2. **Given** quem elaborou o Edital abre "Homologar", **When** a tela aparece, **Then** a atenção
   "Depois de homologar, você não poderá publicar esta revisão" vem antes do formulário e do botão,
   com a marca "Atenção:".
3. **Given** a confirmação de "Cancelar", **When** quem a abre usa o teclado, **Then** a ordem de
   tabulação é a ordem visual, o foco fica visível em todo controle e nenhuma barra fixa o cobre.
4. **Given** um envio recusado pelo comando, **When** a tela volta, **Then** a recusa recebe o foco,
   aparece antes do formulário e cita o que faltou.
5. **Given** a confirmação de "Publicar" numa janela de 1280 × 800, **When** ela abre, **Then** o
   botão de confirmar aparece sem rolagem, ou a tela diz, acima da dobra, que ele existe.

---

### User Story 2 — Quem apura a ocupação acha o número e o gesto de cada lista, e entende o que cada gesto faz (Priority: P1)

Quem abre a Ocupação de vagas de um marco vê, por recorte, os números juntos como indicadores
(publicadas, acrescidas, efetivas, ocupadas, a ocupar), a situação da vaga sem quem a ocupe e, perto
do número de que dependem, os gestos que pode praticar: apurar, emitir nova apuração, pedir a faixa
seguinte, conferir o acréscimo de vaga, conferir o desfazimento dele, declarar a vaga não preenchida
e desfazer a declaração. As duas conferências, a do acréscimo e a da vaga não preenchida, recebem a
mesma composição centrada da confirmação de ato. Quem só lê vê os mesmos números, sem os gestos, e a
frase de a quem pedir.

**Why this priority**: é a tela de operação de tamanho médio que prova o indicador, o trilho e a
ação junto do dado. O roadmap e o segundo parecer a mantiveram no piloto porque nenhuma tela de
histórico testa os três juntos.

**Independent Test**: abrir os dezoito estados da página (O-01 a O-18), os doze retornos (R-01 a
R-12) e os nove estados das conferências (K-01 a K-09) antes e depois, conferir inventário e
sequências, e pedir à equipe que localize "a ocupar" de uma lista e diga o que acontece ao conferir
o acréscimo.

**Acceptance Scenarios**:

1. **Given** um marco com três recortes, um apurado e vigente, outro não apurado e o terceiro sem
   inscrito, **When** quem emite abre a Ocupação, **Then** cada recorte mostra os seus números e só
   os gestos que concluem ali, e os números aparecem sempre juntos, nunca um sozinho, como pede a
   UX-031 da `016`.
2. **Given** a apuração obsoleta, **When** a tela abre, **Then** o aviso de obsolescência e as
   causas aparecem antes dos números que a apuração tinha apurado, e a sucessão com motivo vem
   aberta, como hoje.
3. **Given** a conferência de um acréscimo, **When** ela abre, **Then** os números e "quem a ordem
   alcança" vêm antes da apuração seguinte e do que não se apaga, e esses vêm antes do formulário de
   confirmar.
4. **Given** quem só lê, **When** abre a mesma Ocupação, **Then** a lista de ações (destinos de link
   e de formulário, com os nomes de campo) é idêntica à de antes para esse papel, e diferente da de
   quem emite exatamente como antes.
5. **Given** um gesto que o comando recusa, **When** a tela volta, **Then** a recusa recebe o foco,
   diz qual gesto falhou e aparece antes dos recortes.

---

### User Story 3 — Quem abre a Lista acha o Processo, a situação dele e o trabalho que é seu (Priority: P2)

Quem abre a Lista de Processos Seletivos, que é a porta de entrada da gestão, vê o cabeçalho de
página com o nome da unidade e a ação "Novo Processo Seletivo", os avisos que a tela é obrigada a
dar, a faixa "Ações disponíveis para você", as abas por situação com a contagem, a busca e a frase do
recorte, e então os Processos, cada um com os seus Editais e a situação de cada um. Continua sendo
**lista, e não tabela** (D-011), e nenhuma coluna nova entra.

**Why this priority**: todo perfil vê esta tela, e ela prova o cabeçalho de página, o cartão e os
segmentos. Fica em P2 porque é a de menor risco de domínio das três.

**Independent Test**: abrir os doze estados da Lista (L-01 a L-12) antes e depois e conferir
inventário e sequências. Pedir à equipe que ache um Processo pela busca, diga em que situação estão
os Editais dele e encontre a ação que é sua.

**Acceptance Scenarios**:

1. **Given** a aba "Em andamento" e uma busca, **When** a busca devolve resultados, **Then** a frase
   que diz que a busca procurou em todas as situações vem antes dos resultados (a UX-273 da `129`).
2. **Given** a identidade de demonstração ligada e uma conta sem papel, **When** a Lista abre,
   **Then** os dois avisos aparecem antes da faixa de ações (a FR-2807 da `104`).
3. **Given** a Lista a 375 px, **When** ela abre, **Then** nada rola de lado, e o título do Edital
   que difere do do Processo continua obedecendo à FR-4318 da `129`.
4. **Given** quem preside a comissão de um Processo e quem só a integra, **When** cada um abre a
   Lista, **Then** os selos e as ações "Comissão" e "Alocação por Etapa" aparecem para quem pode
   geri-la, exatamente como antes.

---

### User Story 4 — A equipe faz as mesmas tarefas nas duas versões, e o usuário decide com o que ela disse (Priority: P2)

Duas ou três pessoas da equipe de seleção fazem as mesmas tarefas nas telas antigas e nas novas,
cada versão num servidor próprio sobre uma cópia do mesmo banco: achar a ação principal, dizer o que
acontece ao confirmar, dizer o que impede, localizar um número. Metade começa pela versão antiga e
metade pela nova. O que cada pessoa disse, acertou e errou fica registrado, por tarefa e por versão.

**Why this priority**: é o que devolve ao usuário a evidência para a decisão sobre a migração. Fica
em P2 porque depende das três telas prontas.

**Independent Test**: com as duas versões no ar e o roteiro impresso, uma pessoa da equipe faz as
tarefas nas duas, e o registro sai preenchido para cada tarefa.

**Acceptance Scenarios**:

1. **Given** o roteiro com o gabarito escrito antes da sessão, **When** a pessoa termina as tarefas
   de confirmação, **Then** o registro diz, por versão, se ela disse corretamente o que o ato
   provoca, o que impede e se o ato se desfaz.
2. **Given** uma tarefa em que o ato pedido está impedido, **When** a pessoa a faz, **Then** o
   registro diz se ela percebeu o impedimento antes de procurar o botão.
3. **Given** a sessão terminada, **When** o registro é lido, **Then** ele traz o que a pessoa disse
   que lê e o que pula, que é a evidência que a decisão 5 do roadmap espera.

---

### User Story 5 — Quem mantém o produto confere, por medida, que nada fora do piloto mudou (Priority: P3)

Depois de implementado, o instrumento do estudo roda de novo sobre o banco da referência da P0, e
só as linhas das telas do piloto diferem no `telas.csv`. As capturas das demais são conferidas por
amostra de vinte.

**Why this priority**: é a garantia de que a delimitação funcionou. A construção já a dá, e a medida
a confirma.

**Independent Test**: rodar o rastreio da `referencia-p0/` sobre o `ps_p0_referencia` com a branch
do piloto e comparar com o `telas.csv` da referência.

**Acceptance Scenarios**:

1. **Given** o `telas.csv` da referência e o da branch do piloto, **When** os dois são comparados
   linha a linha, **Then** só diferem as linhas das cinco telas do piloto.
2. **Given** vinte telas de fora do piloto sorteadas, **When** as capturas são comparadas com as da
   referência, **Then** nenhuma diferença passa da linha de ruído de duas capturas do mesmo código.

---

### Edge Cases

- **O contêiner de escopo desfaz a medida da P0.** A folha `grupos/confirmacao-de-ato.css` limita
  aviso, erro, bastão, consequências e formulário por `main>…`, ou seja, só os filhos diretos de
  `main`. Envolver o conteúdo de `confirmar.html` num contêiner de escopo tira esses blocos de lá, e
  a linha de 81 caracteres volta a 162 em silêncio. A medida de leitura precisa valer dentro do
  escopo (FR-7704), e o aceite a mede (SC-2603).
- **A folha da P0 é dividida com duas telas que não são do piloto.** Mudar `confirmacao-de-ato.css`
  mudaria a confirmação do Processo e a da Retificação. Ela não muda (D-002).
- **Definição antes do primeiro uso.** "Termos desta tela" define *recorte* e *faixa* no primeiro
  uso (a FR-424 da `030`). Levá-lo a um trilho que venha **depois** dos recortes na ordem do
  documento o tiraria do primeiro uso para o leitor de tela, mesmo que ele apareça ao lado na tela.
  A definição continua antes do primeiro recorte nas duas ordens (sequência O-S1).
- **Trilho no celular.** Abaixo da largura do trilho, ele desce para o fim. O que a Ocupação puser no
  trilho não pode ser pendência nem condição de gesto, porque no estreito apareceria depois do
  botão. A condição de cada gesto fica junto dele (O-S5).
- **Quem só lê e quem emite veem a mesma página com ações diferentes.** O inventário é por papel, e
  a comparação nunca mistura os dois.
- **Retorno de sucesso da confirmação.** O ato aceito redireciona ao detalhe do Edital, que não é
  tela do piloto. O piloto cobre a recusa reexibida, e não o sucesso, da confirmação (C-12).
- **O botão perigoso e o irreversível.** Cancelar é o único ato com o botão perigoso; Publicar,
  Encerrar e Cancelar são irreversíveis. A marca de cada um continua dizendo a espécie em texto, e
  não só na cor.
- **Barra de ações fixa.** Se a composição puser os botões numa barra fixa ao pé, ela não pode cobrir
  o elemento em foco (a 2.4.11 do WCAG 2.2), nem a recusa que recebe o foco.
- **Zoom de 400%.** Equivale a 320 px de CSS numa janela de 1280: a barra fixa e o cabeçalho de
  página não podem tomar a altura útil a ponto de esconder o conteúdo.
- **Prazos relativos.** O banco da referência data prazos a partir de 14/11. Mede-se nele como está,
  e não num banco remontado (o `README` da `referencia-p0/`). As fotografias da suíte não dependem
  da data, porque as fixtures montam o estado a cada caso.
- **Diferença que é da fixture, e não do design.** Identificadores, datas de registro e nomes
  gerados variam entre duas montagens. O inventário os normaliza antes de comparar (FR-7722).
- **Classe citada sem regra, e regra lida como texto.** Classe nova nasce com regra no mesmo commit,
  e os guardiões que leem a folha como texto continuam verdes: muda-se valor, e não seletor
  existente (o quadro de riscos do roadmap).
- **CSP.** Nenhum estilo nem script no template: a política de conteúdo os recusaria em silêncio.

---

## Requirements *(mandatory)*

### Functional Requirements

#### O escopo e a delimitação

- **FR-7700**: O piloto DEVE alcançar exatamente cinco templates: `confirmar.html`, `ocupacao.html`
  com as parciais que ele inclui, `ocupacao_acrescimo.html`, `ocupacao_nao_preenchida.html` e
  `lista.html` (D-001, D-002).
- **FR-7701**: O estilo novo DEVE morar numa folha de grupo própria, carregada só por esses cinco
  templates pelo bloco de estilo da página, e toda regra dela DEVE estar sob uma classe de escopo
  aplicada a um contêiner que envolve o conteúdo de cada um (D-003).
- **FR-7702**: Nenhuma regra de `componentes.css`, `formularios.css`, `tabelas.css`, `telas.css`,
  `moldura.css` nem de `grupos/confirmacao-de-ato.css` PODE mudar de valor ou de seletor. A base da
  gestão não muda.
- **FR-7703**: Os tokens da direção experimental DEVEM ser só acrescentados a `tokens.css`, com nomes
  novos. Nenhum token existente PODE mudar de valor (D-010).
- **FR-7704**: *(revista em 15/11, D-012)* Dentro do escopo, aviso, erro, bastão, consequências e
  formulário da confirmação DEVEM ir até a largura do conteúdo, como o resto da prosa: a medida que a
  P0 lhes deu não vale no piloto. Fora dele, nas confirmações do Processo e da Retificação, ela
  continua.
- **FR-7705**: O `.acao` com altura única e a barra de ações DEVEM valer só dentro do escopo do
  piloto. Fora dele, o `.acao` continua com as quatro alturas de hoje.
- **FR-7706**: Nenhum template fora dos cinco PODE mudar, salvo uma parcial que só eles incluem.
  Parcial incluída também por outra tela DEVE continuar igual, e o escopo a estiliza de fora.

#### O conteúdo e o comportamento preservados

- **FR-7707**: Em todo estado do catálogo (D-004), todo bloco de texto visível antes DEVE existir
  depois, com as mesmas palavras, e nenhum bloco novo PODE aparecer. A comparação é de conjunto, e
  não de ordem.
- **FR-7708**: Todo número exibido antes DEVE aparecer depois, com o mesmo rótulo.
- **FR-7709**: Cada rótulo DEVE continuar junto do seu valor, cada campo junto da sua ajuda e da sua
  recusa, e cada aviso junto do controle ou do bloco a que se refere. "Junto" quer dizer no mesmo
  item da estrutura (o mesmo recorte, o mesmo item de lista, o mesmo campo), e não só na mesma tela.
- **FR-7710**: Por papel, a lista de destinos de link e de formulário, com o método e os nomes de
  campo, DEVE ser idêntica antes e depois. Nenhum texto de ato muda, nem o de um botão.
- **FR-7711**: Nenhum texto PODE ser recolhido, resumido, cortado ou movido para dentro de um
  recolhido que antes não o continha. O recolhido que já existe ("Termos desta tela", a sucessão da
  apuração) fica como está, inclusive o que hoje abre sozinho.
- **FR-7712**: A fonte e os tamanhos de fonte DEVEM ser os de hoje em todo elemento das cinco telas.
- **FR-7713**: Nenhuma consulta ao banco PODE ser acrescentada às cinco telas. A Lista continua no
  orçamento de consultas que já tem.

#### A ordem

- **FR-7714**: As sequências que não se invertem (seção *As sequências declaradas*) DEVEM valer na
  ordem do documento, que é a do teclado e do leitor de tela, e na ordem visual, em toda largura do
  catálogo.
- **FR-7715**: Fora dessas sequências, a ordem PODE mudar. Toda mudança DEVE ficar registrada na
  comparação de cada estado, bloco por bloco.

#### Os estados e a fotografia

- **FR-7716**: Cada estado do catálogo (D-004) DEVE ser fotografado antes e depois, nas cinco larguras
  do estudo (375, 768, 1280, 1440 e 1920 px), com o mesmo papel e os mesmos registros.
- **FR-7717**: A fotografia DEVE sair de uma jornada de navegador que monta cada estado pelas
  fixtures da suíte e grava, por estado e largura, a captura da página inteira e o inventário de
  conteúdo (D-005).
- **FR-7718**: Antes de fotografar, a jornada DEVE confirmar que o estado pedido foi alcançado, pelo
  trecho que o identifica. Um estado que não se alcança falha a jornada, e não produz foto do estado
  errado.
- **FR-7719**: A jornada DEVE rodar só sob demanda e não entrar no veredito da suíte comum. Sem a
  variável que a liga, ela pula (D-005).
- **FR-7720**: A fotografia "antes" DEVE ser tirada sobre o código da `main` de que o piloto parte:
  na branch do piloto, com só o catálogo e a jornada escritos e nenhuma mudança de template, folha ou
  token, e guardada para a comparação.
- **FR-7721**: O inventário de cada estado DEVE conter quatro listas: os blocos de texto, as
  quantidades com rótulo, as associações (cada bloco com o item da estrutura a que pertence) e as
  ações (destino, método e nomes de campo). Também DEVE conter as duas ordens dos blocos, a do
  documento e a visual.
- **FR-7722**: Antes de comparar, o inventário DEVE normalizar o que varia entre montagens:
  identificadores, datas e horas de registro, chaves de idempotência e o token de CSRF.
- **FR-7723**: A comparação de dois inventários DEVE dizer, por estado, o que faltou, o que sobrou,
  o que mudou de associação, as sequências que se inverteram e o que mudou de ordem fora delas.

#### Acessibilidade conferida à mão

- **FR-7724**: Em cada uma das cinco telas, a ordem de tabulação DEVE ser a ordem visual, todo
  controle DEVE ser alcançável e nada pode prender o foco.
- **FR-7725**: O foco DEVE ser visível em todo controle e não PODE ser coberto por barra fixa nem
  por cabeçalho.
- **FR-7726**: A 320 px de largura, e com zoom de 200% e de 400%, nada se perde e nada rola em dois
  eixos, salvo a tabela dentro da moldura rolável.
- **FR-7727**: A recusa DEVE receber o foco, citar o campo ou o gesto, e o campo DEVE apontar para ela
  quando a recusa for dele.
- **FR-7728**: Todo campo DEVE ter rótulo visível e associado, conferido no navegador, e não só pela
  presença de atributo.
- **FR-7729**: O aviso e a situação DEVEM dizer a espécie em texto, e não só na cor. A marca da P0
  ("Impedimento:", "Atenção:") fica onde está.

#### Legibilidade e localização da ação

- **FR-7730**: *(revista em 15/11, D-012)* A prosa das cinco telas DEVE ocupar a largura do conteúdo,
  que a moldura limita a `--pagina`. O comprimento da linha é registrado como diagnóstico, sem valor
  de aprovação.
- **FR-7731**: Quando o estado tem ação principal, ela DEVE aparecer sem rolagem a 1280 × 800, ou a
  tela DEVE dizer, acima da dobra, que ela existe.
- **FR-7732**: O dado de que a ação depende DEVE ficar à vista junto dela.
- **FR-7733**: No celular, a pendência e a ajuda de preenchimento DEVEM aparecer antes da ação de
  avançar ou de confirmar.
- **FR-7734**: A ocupação da metade direita DEVE ser registrada como diagnóstico, e não PODE ser
  critério de aprovação.

#### A avaliação das confirmações e a validação com a equipe

- **FR-7735**: As confirmações (a do Edital e as duas da Ocupação) DEVEM ser avaliadas pelo
  entendimento das consequências e pela prevenção de erro, com perguntas e gabarito escritos antes
  da sessão, a partir do texto da própria tela (D-007).
- **FR-7736**: A validação DEVE ter de duas a três pessoas da equipe de seleção, cada uma fazendo as
  mesmas tarefas na versão antiga e na nova, com metade começando por cada uma (D-008).
- **FR-7737**: As duas versões DEVEM rodar em servidores próprios, sobre cópias do mesmo banco, com
  os estados que as tarefas pedem. As tarefas de cada versão usam registros diferentes no mesmo
  estado, para que a segunda não seja lembrança da primeira.
- **FR-7738**: O banco da validação DEVE sair da cópia do banco da referência da P0, mais os estados
  da Ocupação que as tarefas pedem, acrescentados por um procedimento versionado e reproduzível, sem
  código novo no produto (D-005).
- **FR-7739**: O registro da validação DEVE dizer, por pessoa, tarefa e versão: o que ela respondeu,
  se acertou pelo gabarito, onde hesitou, o que disse que lê e o que pula. Não pode guardar nome de
  pessoa da equipe, só um código.
- **FR-7740**: Ao fim, o piloto DEVE devolver ao usuário um relatório com o resultado de cada
  critério, a validação e a resposta a cada hipótese do quadro *O que o piloto devolve para decisão*
  do roadmap. Nenhuma hipótese vira regra sem decisão do usuário.
- **FR-7741**: O piloto DEVE entregar o levantamento do que cada guardião candidato do
  `03-design-system.md` protegeria nas cinco telas, com a lista do que existe hoje, sem criar nenhum.

### As sequências declaradas

São as ordens que não se invertem. O aceite as confere nas duas ordens, a do documento e a visual
(FR-7714). Cada sequência vale onde os seus blocos existem no estado. Fora delas, a ordem pode mudar
(FR-7715).

**Em todas as cinco telas**

| Id | Sequência |
|---|---|
| T-S1 | a trilha de navegação, e depois o título da página |
| T-S2 | a recusa (`.erro` com foco), e depois o primeiro formulário da página |
| T-S3 | o que impede, e depois o que só informa ou avisa |

**Confirmação de ato do Edital**

| Id | Sequência |
|---|---|
| C-S1 | o **fundamento**: o título do ato e o Edital, e depois os impedimentos, as atenções e as pendências |
| C-S2 | os impedimentos ("Impedimento:"), e depois as atenções ("Atenção:"), inclusive no desfecho de encerrar e cancelar |
| C-S3 | as atenções, e depois a **consequência**: "Este ato não pode ser desfeito" ou "O que este ato provoca", com a passagem de bastão |
| C-S4 | a consequência, e depois a **confirmação**: autoridade signatária, motivo e botão |
| C-S5 | o campo (autoridade ou motivo) com a ajuda dele, e depois o botão de confirmar |
| C-S6 | o botão de confirmar, e depois "Cancelar e voltar" na ordem do documento. Na ordem visual, a barra pode pô-los em qualquer lado, desde que a do teclado continue esta |

**Ocupação de vagas**

| Id | Sequência |
|---|---|
| O-S1 | "Termos desta tela", e depois o primeiro recorte, nas duas ordens |
| O-S2 | o retorno do gesto (sucesso ou recusa, com foco), e depois "Próximo nesta lista", e depois os recortes |
| O-S3 | "Abrir esta tela não apura nada", e depois os números do primeiro recorte |
| O-S4 | dentro do recorte: o título do recorte; o aviso de estado (não apurado, obsoleta e as causas); os números; as notas da divergência entre publicadas e efetivas; os movimentos; a situação da vaga; e só então os gestos e os caminhos (histórico, convocação) |
| O-S5 | a condição ou a ajuda de um gesto, e depois o botão que o pratica (o déficit antes de "Pedir a faixa seguinte", a ajuda do acréscimo antes dos campos) |
| O-S6 | a frase de a quem pedir, para quem só lê, antes dos recortes |

**As duas conferências da Ocupação**

| Id | Sequência |
|---|---|
| K-S1 | a recusa ("aviso" com foco), e depois tudo o mais |
| K-S2 | o **fundamento**: as vagas e quem a ordem alcança, ou a vaga e os atos anteriores |
| K-S3 | depois do fundamento, a **consequência**: a apuração seguinte, o efeito e o que não se apaga |
| K-S4 | depois da consequência, a **confirmação**: os dados que serão gravados e o botão, e por último "Voltar à ocupação" na ordem do documento |

**Lista de Processos Seletivos**

| Id | Sequência |
|---|---|
| L-S1 | os avisos obrigatórios (ambiente de demonstração, sem permissões), e depois a faixa "Ações disponíveis para você" |
| L-S2 | a faixa, e depois as abas, a busca e os Processos |
| L-S3 | a frase do recorte, e depois o primeiro Processo |
| L-S4 | dentro do Processo: o título, o código e a situação, e depois as ações do Processo e os Editais |
| L-S5 | os Processos, e depois a paginação |

### Requisitos de experiência

- **UX-850**: *(revista em 15/11, D-012)* A confirmação de ato e as duas conferências usam a largura
  do conteúdo, e não uma coluna centrada, com os avisos como componente, as consequências em cartão e
  a barra de ações ao pé.
- **UX-851**: A Ocupação usa a composição **principal e trilho** a partir de 80rem de janela, a
  largura em que o trilho de 21rem cabe ao lado do trabalho. No trilho só vai o que é apoio de leitura e vale para a página inteira, nunca condição de
  gesto nem pendência. Abaixo dessa largura, o trilho desce sem violar a O-S1 nem a O-S5.
- **UX-852**: Os números de cada recorte da Ocupação e das conferências viram **indicadores**, com o
  número em destaque e o rótulo embaixo, sempre juntos. Zero esmaece; ausência de apuração não se
  desenha como número.
- **UX-853**: A Lista usa a composição **cheia**, com o cabeçalho de página (título, unidade e "Novo
  Processo Seletivo" à direita), as abas como segmentos, a busca como barra de filtros e cada
  Processo como item de lista dentro de um cartão, sem caixa por item.
- **UX-854**: Dentro do escopo, o botão tem uma altura só por tamanho (40 e 32 px), o `a` e o
  `button` com a mesma altura, e no máximo um botão cheio por bloco de gesto. A convenção de um botão
  cheio por tela é observada, e não exigida (é hipótese do roadmap).
- **UX-855**: Os neutros da tela de entrada entram como tokens novos, usados só dentro do escopo. As
  cores de atenção e de perigo não mudam.

### Key Entities

- **Estado do catálogo**: uma combinação de tela, situação dos registros, papel e, quando há, gesto
  praticado. Tem um código (C-NN, O-NN, R-NN, K-NN, L-NN), o trecho que prova que foi alcançado e a
  fixture que o monta.
- **Fotografia**: por estado e largura, a captura da página inteira e o inventário de conteúdo,
  tirada sobre um commit.
- **Inventário de conteúdo**: os blocos de texto, as quantidades com rótulo, as associações, as
  ações, e as duas ordens dos blocos de um estado, normalizados.
- **Comparação**: para um estado, a diferença entre o inventário de antes e o de depois e o
  resultado de cada sequência declarada.
- **Registro da validação**: por pessoa (em código), tarefa e versão, a resposta, o acerto pelo
  gabarito, a hesitação e o comentário.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2600**: Em 100% dos estados do catálogo e para cada papel, a comparação acusa **zero** bloco
  de texto ausente, **zero** bloco novo, **zero** quantidade sem o mesmo rótulo, **zero** associação
  desfeita e **zero** diferença na lista de ações.
- **SC-2601**: Em 100% dos estados, nas cinco larguras e nas duas ordens, **nenhuma** sequência
  declarada se inverte.
- **SC-2602**: No rastreio sobre o banco da referência da P0, **só** as linhas das cinco telas do
  piloto diferem do `telas.csv` da referência, e nenhuma das vinte capturas de amostra de fora do
  piloto passa da linha de ruído.
- **SC-2603**: *(revisto em 15/11, D-012)* Em todos os estados, a prosa ocupa a largura do conteúdo:
  nenhum parágrafo, nota, aviso ou item de lista para antes dela.
- **SC-2604**: Em todos os estados que têm ação principal, ela aparece sem rolagem a 1280 × 800, ou a
  tela a anuncia acima da dobra.
- **SC-2605**: Nas cinco telas, **zero** perda de conteúdo e **zero** rolagem em dois eixos a 320 px e
  com zoom de 200% e de 400%; **zero** controle com foco coberto ou invisível; a ordem de tabulação
  igual à visual em todo estado conferido.
- **SC-2606**: Na validação, para cada tarefa de confirmação, a proporção de respostas certas sobre o
  que o ato provoca, o que impede e se ele se desfaz é **igual ou maior** na versão nova do que na
  antiga. E, nas tarefas de prevenção de erro, as vezes em que uma pessoa procura o botão de um ato
  impedido **sem ter notado o impedimento** não são mais numerosas na versão nova do que na antiga.
- **SC-2607**: Na validação, as tarefas de localizar (a ação principal, um número da Ocupação, um
  Processo na Lista) têm a mesma proporção de acerto ou maior na versão nova. O tempo é registrado
  como diagnóstico, sem valor de aprovação.
- **SC-2608**: A suíte contra PostgreSQL e o `lint` fecham verdes, os guardiões que já existem
  continuam intactos, sem afrouxar nenhum, e **nenhum** guardião novo entra.
- **SC-2609**: O relatório final responde a cada uma das sete hipóteses do quadro do roadmap, com a
  evidência de cada resposta, e o usuário tem o que precisa para decidir se a migração continua.

---

## Assumptions

- **A referência é a da P0.** O `telas.csv` e as capturas de `referencia-p0/`, sobre o banco
  `ps_p0_referencia` como ele está, com a cópia `pg_dump` na pasta de notas das sessões deste
  trabalho. Nada de remontar o banco para comparar (o `README` dela).
- **A jornada de navegador sobre as fixtures é o caminho de menor custo.** O levantamento das
  fixtures mostrou que a suíte desenha 51 dos 63 ramos da Ocupação. A jornada consolidada do
  convocado (`118`) já faz o mesmo com cenários por letra: monta, abre, grava a captura e o texto
  visível.
- **A equipe pode dedicar uma sessão de cerca de uma hora por pessoa.** São de duas a três pessoas,
  porque a equipe inicial é desse tamanho e os papéis se acumulam.
- **"Mesmo papel" é o mesmo conjunto de permissões e o mesmo vínculo de comissão.** Na demonstração,
  pela identidade de demonstração.
- **A linha de ruído das capturas** é a diferença entre duas capturas do mesmo código: hora,
  cantos e cursor. É medida antes de comparar.
- **O piloto parte da `main` atual**, com a P0 mergeada, e não altera regra de negócio.

## Out of Scope

- As confirmações do Processo e da Retificação, e as outras 28 rotas de confirmação da família P2.1.
- O Histórico da ocupação, a Convocação, o assistente e o portal.
- A redução tipográfica e o experimento opcional dela, o recolhimento de explicações, a coluna "Fase
  e próximo passo", a mudança global de `.acao` e o apontamento dos tokens antigos para os novos.
- Guardiões novos, inclusive os cinco candidatos do `03-design-system.md`: o piloto só os levanta.
- Teste formal de usabilidade, com amostra e estatística. A validação é conferência.
- Leitor de tela, se não houver na equipe quem possa conferir. Fica registrado como não conferido.
- A prévia de publicação do resultado, com a linha de 176, achado da P0.

## Dependências

- A P0 na `main` (#557 e #559): a marca de espécie e a medida de leitura da confirmação.
- A referência da P0 (`referencia-p0/`) e o banco `ps_p0_referencia` intocado no cluster local.
- O grupo opcional `navegador` (Playwright e Chromium) para a jornada de fotografia.
- O instrumento do estudo (`medicoes/metricas.js` e `medicoes/largura.js`) e os scripts da
  referência, para o critério SC-2602.
- Duas ou três pessoas da equipe de seleção, para a US4.

## Achados (registro, e não escopo)

- **O roadmap conta seis atos na confirmação, e são sete.** `confirmar.html` serve também "Revogar
  homologação" (`revogar-homologacao`, a partir de Homologado, com motivo). O catálogo o inclui
  (C-04). A tabela do roadmap e a do `README` do estudo continuam dizendo seis.
- **A folha da P0 só vale para filhos diretos de `main`.** Os seletores `main>:is(.aviso,…)` de
  `confirmacao-de-ato.css` deixam de alcançar os blocos que um contêiner envolver. Isso não é defeito
  da P0, mas qualquer contêiner nessas três telas, do piloto ou não, desfaz a medida de leitura sem
  aviso. O piloto a reproduz dentro do escopo (FR-7704); as telas do Processo e da Retificação seguem
  com a da P0.
- **"Tabela em cartão" na Lista contraria a decisão da `129`.** O roadmap diz que a Lista "prova o
  cabeçalho de página e a tabela em cartão", e a P2.5 fala em "Lista de Processos em tabela". O
  template da `129` escolheu **lista, e não tabela**, para que nada role de lado a 375 px, e a linha
  diz só fatos (a FR-4318 da `129`). O piloto mantém a lista (D-011). Mudar para tabela é decisão do
  usuário, e de spec própria.
- **Os cenários de treinamento chegam a um estado só da Ocupação.** Por isso o banco da validação
  precisa de estados acrescentados (FR-7738). Um cenário de treinamento novo para a Ocupação seria
  útil à equipe além do piloto, mas é escopo da `134`, e não deste.
- **Quatro ramos da Ocupação ficam sem fotografia** (D-004): as obsolescências pelas outras seis
  causas, a nota do cadastro legado, "Nada mais em aberto nesta lista" e o sucesso com a apuração
  seguinte pendente.

---

## Decisões

### D-001 — As duas conferências da Ocupação entram

`ocupacao_acrescimo.html` e `ocupacao_nao_preenchida.html` entram no piloto, com a composição
centrada da confirmação de ato e só os componentes que o piloto já usa.

**Por quê.** São as telas em que se pratica o ato da Ocupação, e é nelas que se lê o que o
acréscimo e a declaração mudam: quem a ordem alcança, a apuração seguinte e o que não se apaga. O
terceiro parecer pediu que as confirmações se avaliem pelo entendimento das consequências, e as
duas conferências são confirmações. Deixá-las fora faria a tarefa da equipe começar na Ocupação nova,
passar pela conferência antiga e voltar à nova, o que mistura as duas versões numa mesma tarefa e
contamina a comparação. O custo é pequeno: 108 e 112 linhas, sete e quatro testes de tela que já as
desenham, e nenhum componente que a confirmação do Edital não traga.

**O que se descartou.** Deixá-las para a P2.1, a família das confirmações. Manteria o piloto menor
em dois templates, ao preço de validar o gesto da Ocupação pela metade.

### D-002 — Só a confirmação do Edital, e a folha da P0 não muda

A confirmação de ato do piloto é `confirmar.html`, nos sete atos. As do Processo
(`processo_confirmar.html`) e da Retificação (`retificacao_confirmar.html`) ficam como a P0 as
deixou, e `grupos/confirmacao-de-ato.css` não é tocada.

**Por quê.** A folha da P0 é carregada pelas três. Mudar uma regra dela muda duas telas fora do
piloto e reprova o SC-2602. A medida de leitura é reproduzida dentro do escopo (FR-7704).

### D-003 — Uma folha de grupo e uma classe de escopo, e a base não muda

O estilo novo mora numa folha de grupo própria, em `interface/grupos/`, carregada só pelos cinco
templates, e toda regra dela fica sob uma classe de escopo, num contêiner que envolve o conteúdo de
cada template dentro do bloco `conteudo`. É o mecanismo que o produto já usa para grupo de telas. A
`base.html` não muda, e o mapa de quem carrega cada folha, que um guardião já confere, ganha a linha
da folha nova.

**Por quê.** É a delimitação por construção que o primeiro parecer pediu: o `.acao` das outras telas
não muda porque a regra nova não as alcança, e não porque alguém tomou cuidado.

### D-004 — O catálogo: 12 estados da confirmação, 18 da Ocupação, 12 retornos, 9 das conferências e 12 da Lista

> **Revisto na implementação (15/11):** a C-12 virou C-12 (a recusa do envio) e C-13 (quem não tem a
> permissão), porque são duas páginas, e o catálogo tem 64 estados. A O-06 e a O-14 mostram menos do
> que a tabela abaixo descreve; o porquê está em `doc/auditoria-design-system-2026-11-14/piloto/README.md`.

O catálogo parte dos 51 ramos da Ocupação que a suíte já desenha e dos estados que o roadmap lista.
Ele fotografa **combinações de página**, e não ramos soltos: um marco com três recortes em situações
diferentes é um estado só, que mostra três ramos ao mesmo tempo, como a pessoa os vê.

**Confirmação de ato do Edital**

| Código | Estado | Papel |
|---|---|---|
| C-01 | Submeter, sem pendência, com a passagem de bastão | quem elabora |
| C-02 | Submeter com uma pendência que impede e uma de atenção: recusa certa, sem botão | quem elabora |
| C-03 | Homologar, por quem elaborou: a atenção de que não poderá publicar | quem elabora e homologa |
| C-04 | Revogar homologação, com o motivo | quem homologa |
| C-05 | Devolver para elaboração, com o motivo | quem homologa |
| C-06 | Publicar, com a autoridade signatária a escolher e a prévia | quem publica |
| C-07 | Publicar impedido por segregação de funções | quem elaborou, homologou e publica |
| C-08 | Publicar sem autoridade vigente na unidade: recusa certa | quem publica |
| C-09 | Encerrar, com o que impede e o que continua: as três faixas do S6 | quem encerra |
| C-10 | Encerrar sem nada que impeça | quem encerra |
| C-11 | Cancelar: o botão perigoso, irreversível, com motivo | quem cancela |
| C-12 | Recusa do envio reexibida, com o foco nela; e quem não pode praticar o ato (a parcial de impedimento) | quem encerra; sem a permissão |

**Ocupação de vagas, a página**

| Código | Estado | Papel |
|---|---|---|
| O-01 | Marco intermediário, que não apura e aponta o marco que apura | quem emite |
| O-02 | Sem quadro de vagas, para quem não retifica | quem emite |
| O-03 | Sem quadro de vagas, para quem retifica (o link da Retificação) | quem emite e retifica |
| O-04 | Não apurado, com ordem: o botão de apurar | quem emite |
| O-05 | Não apurado, sem ordem: a razão e o caminho no lugar do botão | quem emite |
| O-06 | Marco com cotas, três recortes: um vigente, um não apurado e um sem inscrito | quem emite |
| O-07 | Vigente com vaga a ocupar, o Edital admite a faixa seguinte: o pedido e a sucessão recolhida | quem emite |
| O-08 | Vigente com vaga a ocupar, o Edital não admite chamar além da faixa | quem emite |
| O-09 | Vigente com vaga a ocupar, o marco não declara regra de corte | quem emite |
| O-10 | Vigente com vaga a ocupar, para quem só lê: a frase de a quem pedir | quem só lê |
| O-11 | Vigente sem vaga a ocupar | quem emite |
| O-12 | Apuração obsoleta, pela causa "efeito posterior", com a sucessão aberta | quem emite |
| O-13 | Com vagas acrescidas: a lista, o desfazimento disponível, efetivas diferentes das publicadas e o formulário de acréscimo | quem emite |
| O-14 | Com movimento de vaga entre recortes (reversão de cota), e o acréscimo recusado fora da linha geral | quem emite |
| O-15 | A vaga sem quem a ocupe, com o Edital silente: os dois caminhos e a declaração disponível | quem emite e retifica |
| O-16 | A declaração de vaga não preenchida na lista, desfazível | quem emite |
| O-17 | A declaração que não se desfaz, por haver chamada dependente | quem emite |
| O-18 | A vaga sem quem a ocupe, para quem não apura | quem só lê |

**Ocupação de vagas, o retorno de cada gesto**

| Código | Gesto | Retorno |
|---|---|---|
| R-01, R-02 | Apurar, ou emitir nova apuração | sucesso, com "Próximo nesta lista"; recusa |
| R-03, R-04 | Pedir a faixa seguinte | sucesso; recusa |
| R-05, R-06 | Acrescentar vaga, depois da conferência | sucesso, com a apuração seguinte emitida; recusa |
| R-07, R-08 | Desfazer o acréscimo | sucesso; recusa |
| R-09, R-10 | Declarar a vaga não preenchida | sucesso; recusa |
| R-11, R-12 | Desfazer a declaração | sucesso; recusa |

**As conferências**

| Código | Estado |
|---|---|
| K-01 | Conferir o acréscimo, com quem a ordem alcança e o processo administrativo preenchido |
| K-02 | Conferir o acréscimo, com a ordem alcançando menos pessoas que as vagas |
| K-03 | Conferir o acréscimo com a apuração já obsoleta por outra causa: este ato não a emite |
| K-04 | Conferir o desfazimento de um acréscimo |
| K-05 | A recusa na conferência do acréscimo |
| K-06 | Conferir a declaração de vaga não preenchida |
| K-07 | Conferir o desfazimento da declaração |
| K-08 | O desfazimento da declaração que não cabe, por haver pessoa chamada: só "Voltar" |
| K-09 | A recusa na conferência da declaração |

**Lista de Processos Seletivos**

| Código | Estado | Papel |
|---|---|---|
| L-01 | "Em andamento", com a faixa de ações, "Novo Processo Seletivo" e Processos com um, vários e nenhum Edital | quem tem os papéis da demonstração |
| L-02 | "Encerrados" | idem |
| L-03 | "Cancelados" | idem |
| L-04 | "Todos" | idem |
| L-05 | Busca com resultado, a partir de "Em andamento" | idem |
| L-06 | Busca sem resultado | idem |
| L-07 | Escopo sem Processo: a lista vazia | idem |
| L-08 | A segunda página da paginação | idem |
| L-09 | Edital com Retificação em curso: a marca na linha | quem homologa |
| L-10 | Quem preside a comissão de um Processo, e quem só a integra, sem `comissao:gerir` | presidente; membro |
| L-11 | Sem a faixa de ações e sem "Novo Processo Seletivo" | quem só lê |
| L-12 | Conta sem papel nenhum, com a identidade de demonstração ligada: os dois avisos | sem papel |

**O que fica fora, e por quê.** As obsolescências pelas outras seis causas mudam só a frase da
causa, num bloco que o O-12 já fotografa. O quadro retificado não tem teste que o monte. A nota do
cadastro legado pede um Edital com o número digitado de antes da `162`, que nenhuma fixture monta, e
é o ramo mais caro. "Nada mais em aberto nesta lista" não tem teste. O sucesso com a apuração
seguinte pendente muda uma frase do R-05. Os quatro estão no registro de achados. Ficam dentro dois
dos doze ramos que a suíte não desenhava, porque são baratos: o sem quadro para quem retifica (O-03)
e o acréscimo com processo administrativo (K-01).

### D-005 — A imagem sai de uma jornada de navegador sobre as fixtures, e o banco da equipe sai da referência

**Para a comparação**, uma jornada nova em `tests/navegador/`, um módulo só, parametrizado pelo
código do estado, com o catálogo repartido por tela, como a jornada consolidada do convocado da `118`: monta o estado pelas fixtures da
suíte, abre a tela no `live_server` com o papel do estado, confere o trecho que prova o estado
(FR-7718) e grava, nas cinco larguras, a captura e o inventário. Ela pula sem a variável que a liga
(FR-7719), e por isso não pesa no CI nem vira guardião. Fica no repositório, para que a mesma
fotografia se repita antes e depois e na P2.

**Para a equipe**, o banco da validação é uma cópia do `ps_p0_referencia`, mais os Editais nos
estados da Ocupação que as tarefas pedem, acrescentados por um roteiro versionado na pasta desta
spec que reusa as funções de montagem das fixtures. As duas versões sobem em servidores próprios,
cada uma sobre a sua cópia.

**O que se descartou.** Um cenário de treinamento novo, que é escopo da `134`. E montar os estados à
mão, pela interface, que não se repete igual nas duas versões.

### D-006 — O aceite é por inventário, e a ordem se confere à parte

O texto do `main` como sequência única reprovaria a mudança de posição, que é o que o piloto existe
para testar. O aceite compara, por estado e papel, quatro conjuntos (os blocos de texto, as
quantidades com rótulo, as associações e as ações) e confere as sequências declaradas nas duas
ordens. "Bloco" é o menor elemento com texto próprio que se lê como unidade: parágrafo, item de
lista, célula, rótulo, legenda, botão e link. A associação é o item da estrutura que contém o bloco
(o recorte, o item da lista, o campo), dito por ele, e não por posição na tela.

### D-007 — As confirmações se avaliam pelo que a pessoa entende e pelo erro que ela evita

Para cada tarefa de confirmação, o roteiro traz três perguntas, com o gabarito tirado do texto da
própria tela antes da sessão: *o que acontece se você confirmar?*, *alguma coisa impede este ato?*
e *dá para desfazer depois?*. E traz uma tarefa de prevenção de erro, em que o ato pedido está
impedido, ou em que há dois Editais e só um deles é o certo. Conta o acerto, e não o tempo. A pessoa
não confirma ato nenhum fora do banco da validação.

**Por quê.** O terceiro parecer pediu exatamente isso: o que conta é se quem confirma sabe o que vai
acontecer e se evita o ato errado. Uma composição mais bonita que esconda o impedimento é pior, e só
uma pergunta direta mostra isso.

### D-008 — A validação: as mesmas tarefas, nas duas versões, com a ordem alternada

De duas a três pessoas da equipe, cada uma em sessão própria, fazem as mesmas tarefas nas duas
versões. Metade começa pela antiga. As tarefas de cada versão usam registros diferentes no mesmo
estado, para que a segunda não seja lembrança da primeira. Quem conduz não explica a tela. Lê a
tarefa, anota o que a pessoa diz e só pergunta, no fim, o que ela leu e o que pulou. O registro fica
na pasta desta spec, com a pessoa em código. É conferência, e não teste formal: o número de pessoas
não sustenta estatística, e o relatório não finge que sustenta.

### D-009 — Nenhum guardião novo, e os existentes continuam como estão

Nenhum teste novo que recuse uma forma de CSS ou de template entra no aceite. A jornada de
fotografia só grava e confere que o estado foi alcançado. Os guardiões que já existem não são
afrouxados. Acrescentar a folha nova ao mapa que um deles mantém, de quem carrega cada folha, é
cumprir o guardião, e não criar outro. O piloto entrega o levantamento do que cada guardião
candidato protegeria (FR-7741). Quais nascem é a decisão 7 do roadmap.

### D-010 — Os tokens novos se acrescentam a `tokens.css`, e os antigos não mudam

Os neutros da entrada e as escalas de espaço, raio e controle entram em `tokens.css` com nomes novos,
como recomenda o roadmap para o piloto ("acrescentar"). Nenhuma tela de fora os usa, e por isso
nenhuma muda. Os de tamanho de fonte (`--t-*`) **não** entram, porque o piloto mantém os tamanhos de
hoje.

**Por quê.** `tokens.css` é o único lugar de valor literal na governança proposta. Declarar os
neutros na folha do piloto criaria uma segunda fonte de cor, que é o defeito que o estudo mediu.

### D-012 — O texto ocupa a largura do conteúdo (decisão do usuário, 15/11)

O usuário viu o antes e o depois da primeira versão, com a prosa presa em 80 caracteres e a
confirmação numa coluna centrada, e a achou pior que a `main`: a página ficou mais alta, a direita
vazia e o texto mais espremido. A pergunta foi entre usar a largura por colunas, deixar o texto
ocupar a largura toda, ou voltar à composição da `main` com os componentes novos; **o usuário
escolheu o texto na largura toda.**

Consequências: a medida de leitura não vale nas cinco telas, nem a da P0 nas confirmações; a
composição centrada sai; a linha longa vira diagnóstico. Os cartões, os indicadores, os avisos e os
botões ficam, com três padrões da segunda leitura: os indicadores de um grupo dividem a linha em
partes iguais, o campo de texto ocupa a largura do formulário e a lista de definição põe rótulo e
valor na mesma linha, o rótulo em peso maior. Os dois-pontos que o usuário mencionou chegaram a ser
gerados pela folha (`dt::after`) e saíram na revisão de código de 15/11, aprovada por ele: era texto
que o template não tem, fora do alcance da comparação do conteúdo, e na gestão inteira escrevia
"Volta atrás?:" em rótulo que é pergunta. Pôr os dois-pontos no texto do template mudaria o conteúdo
(FR-7707), e fica para quando o usuário o pedir como mudança de texto. A preferência do usuário pelo aproveitamento da tela vale como premissa para a
migração das outras famílias, e o "Texto explicativo" e a "medida de leitura" do estudo de 14/11
ficam subordinados a ela.

### D-011 — A Lista continua lista, e não tabela

O piloto aplica à Lista o cabeçalho de página, os segmentos, a barra de filtros e o cartão, e mantém
a estrutura de lista da `129`: sem cabeçalho de colunas, nada rola de lado a 375 px, e o título do
Edital só aparece quando difere do do Processo.

**Por quê.** Trocar lista por tabela muda a estrutura, e não só a composição, e contraria uma
escolha registrada da `129`. Se a tabela for melhor, é decisão do usuário, numa spec da P2.5.
