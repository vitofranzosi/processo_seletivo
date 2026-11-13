# Feature Specification: A organização da lista de Processos Seletivos

**Feature Branch**: `claude/gps-processos-seletivos-diagnostico-d9db4f`, sobre a `main` em `5cf5f179`
(com a `126`, a `127` e a `128`)

**Created**: 2026-11-06

**Status**: Implementada e mergeada (estudo e spec #420, implementação #422). *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Draft. **Leitura e apresentação, sem regra de negócio nova.** A página inicial da gestão
passa a recortar, buscar e paginar os Processos, e a linha de cada Edital deixa de oferecer ações.
Sem migration, tabela, coluna, permissão ou estado persistido novo. Nenhum fluxo de elaboração,
homologação, publicação, classificação, sorteio ou convocação muda.

**Input**: *"Organização da página de Processos Seletivos da gestão (`/gestao/`), Frente A do estudo
`doc/estudo-pagina-processos-seletivos-2026-11-06-revisao.md`. Recorte pelo estado do Processo, abas
com contagem, busca em todas as situações incluindo N/AAAA, 20 Processos por página, filtros no
endereço, listagem compacta sem a coluna 'O que posso fazer', nota de cobertura completa na faixa,
faixa calculada sobre toda a unidade, consultas constantes para todo papel, inclusive o exportador.
Fora: ampliar a faixa, sinal de pronto para encerrar, encerramento automático, arquivamento, a
advertência no Encerrar Processo, os achados de domínio."*

> **Faixa de identificadores.** Esta spec usa a faixa reservada para ela: os requisitos funcionais de
> quatro mil e trezentos a quatro mil trezentos e quarenta e nove, os critérios de mil trezentos e dez
> a mil trezentos e dezenove e os de experiência de duzentos e setenta a duzentos e setenta e quatro;
> os não usados ficam livres. O teto foi medido em 06/11/2026 em `specs/` de todas as worktrees desta
> máquina: o requisito quatro mil duzentos e vinte, o critério mil trezentos e seis e o de experiência
> duzentos e sessenta e dois; a `128` reservou até o requisito quatro mil duzentos e vinte e nove, o
> critério mil trezentos e nove e o de experiência duzentos e sessenta e quatro. As decisões reiniciam
> em `D-001`.
>
> **Origem.** O [estudo de 06/11/2026](../../doc/estudo-pagina-processos-seletivos-2026-11-06.md) e a
> [revisão do mesmo dia](../../doc/estudo-pagina-processos-seletivos-2026-11-06-revisao.md), com as
> medições, as maquetes e os 25 casos exploratórios contra PostgreSQL. A sétima decisão da revisão (a
> coluna de ações sai da lista, variante V1) foi **decidida pelo usuário em 06/11/2026**.

## Por que esta feature existe

A página inicial da gestão lista **todos** os Processos da unidade, sem recorte, busca nem paginação,
e cada Edital carrega uma coluna de ações. Com o acervo crescendo, ela deixa de servir a quem abre a
gestão para trabalhar:

- com 211 Processos, a página mede ~53 mil pixels no computador (59 telas) e ~91 mil no celular;
- quem elabora lê 181 vezes "Nenhuma ação disponível para seus papéis", e quem julga vê 227 botões
  "Recursos aguardando decisão (0)";
- o resumo do topo conta **Editais** numa página que lista **Processos**;
- quem pode exportar para matrícula paga duas consultas por Edital: 451 consultas com 249 Editais, e
  1 323 com 739.

Ao mesmo tempo, a faixa "Ações disponíveis para você" (`104`) diz que não cobre só três famílias de
trabalho, quando são onze, e diz isso no fim, em cinza.

O que a revisão mediu sobre o risco do recorte é o que define o desenho:
- **o recorte não pode ser pelo Edital**: Edital encerrado ainda convoca, recebe documento,
  Requerimento, aviso e recurso;
- **pelo Processo é seguro**, desde que a faixa continue lendo a unidade inteira.

### O que esta spec cobre, e o que fica fora

**Cobre**:
- o recorte por situação do Processo, com quatro abas;
- a busca em todas as situações;
- a paginação e o endereço;
- a linha compacta, sem ações;
- a nota de cobertura da faixa;
- a faixa independente do recorte;
- o custo constante para todo papel.

**Fica fora, e cada item tem dono**:

| Fora | Por quê, e onde fica |
|---|---|
| Ampliar o que a faixa cobre (convocação, resultado, sorteio…) | Frente B do estudo. A derivação existe por Edital na `127`, mas agregá-la sobre a unidade exige uma leitura em lote que ainda não existe |
| Sinal de "pronto para encerrar" | Não é derivável com segurança: a validade do certame é seção textual do Edital (seção 4 da revisão) |
| Encerramento automático, arquivamento, ocultação manual | Fora do pedido, e inseguro com cadastro de reserva |
| A advertência das providências em aberto na confirmação de "Encerrar Processo" | Correção de segurança em separado (a décima decisão da revisão). Advertir reduz o risco e não o elimina; impedir seria outra decisão de domínio |
| Os achados de domínio A-1 a A-6 (recurso, formalização, avisos e exportação com o Processo final; o texto da decisão 021 da `127`) | Registrados na seção 7 da revisão, para priorização do usuário. O A-1 primeiro |
| Mudanças no detalhe do Processo ou do Edital | O detalhe continua o lugar de todos os atos, inclusive dos que saem da lista |
| Reordenar a faixa, renomeá-la, renomear "Minhas Etapas" | Pede validação com pessoas (decisão 007 da `104`) |
| Memória do recorte em sessão; parâmetro de volta nos detalhes | Evolução separada, se a validação pedir |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem abre a gestão vê o que está em andamento, e não o acervo (Priority: P1)

A presidente de comissão abre a gestão de manhã. A página mostra a faixa de ações, o botão "Novo
Processo Seletivo" e, abaixo, só os Processos em andamento: 20 por vez, numa linha compacta por
Processo e uma por Edital. Os encerrados e os cancelados estão a um clique, nas abas ao lado.

**Why this priority**: é a razão da feature. Sem o recorte e a paginação, toda a outra melhoria se
perde numa página de dezenas de telas.

**Independent Test**: com uma unidade de 200 Processos, 60 em andamento, abrir a página sem
parâmetros e conferir a aba marcada, as contagens, os 20 primeiros e a navegação para a página 2.

**Acceptance Scenarios**:

1. **Given** uma unidade com Processos em elaboração, ativos, encerrados e cancelados, **When** a
   pessoa abre a página sem parâmetros, **Then** a aba "Em andamento" está marcada e só os Processos
   em elaboração ou ativos aparecem.
2. **Given** um Processo ativo cujos Editais estão todos encerrados, **When** a pessoa abre "Em
   andamento", **Then** ele aparece: Edital encerrado ainda convoca.
3. **Given** um Processo encerrado com um Edital ainda publicado (caso anterior à regra de 28/09),
   **When** a pessoa abre "Em andamento", **Then** ele aparece ali, com o selo "Encerrado", e não em
   "Encerrados".
4. **Given** 61 Processos em andamento, **When** a pessoa abre a aba, **Then** lê "61 Processos,
   mostrando 1–20", vê 20 Processos e uma navegação para a página seguinte.
5. **Given** a pessoa na página 2 de "Em andamento", **When** clica em "Cancelados", **Then** vai para
   a página 1 de "Cancelados".
6. **Given** a pessoa na página 3, **When** abre um Processo e volta pelo navegador, **Then** encontra
   a mesma aba e a mesma página.

---

### User Story 2 — A faixa não depende da aba, da busca nem da página (Priority: P1)

Quem julga recursos abre a aba "Cancelados", procura um Processo antigo e vai para a página 3. A
faixa "Ações disponíveis para você" no topo continua dizendo "Decidir recursos (1)" sobre o Edital de
um Processo **encerrado**, que não está em nenhuma das linhas mostradas.

**Why this priority**: é o invariante que torna o recorte seguro. O domínio ainda aceita recurso com o
Processo final, e a revisão confirmou contra PostgreSQL que a faixa o oferece. Se a faixa passasse a
ler só a página, o recorte esconderia trabalho.

**Independent Test**: com um recurso aguardando decisão num Edital de Processo encerrado e um Edital
em elaboração na página 2, conferir a faixa nas quatro abas, numa busca e em duas páginas.

**Acceptance Scenarios**:

1. **Given** um recurso aguardando decisão num Edital de Processo encerrado, **When** quem julga abre
   "Em andamento", **Then** a faixa mostra "Decidir recursos (1)".
2. **Given** o mesmo cenário, **When** a pessoa troca de aba, busca ou muda de página, **Then** a faixa
   mostra os mesmos itens, na mesma ordem, com o mesmo total.
3. **Given** um Edital em elaboração cujo Processo cai na página 2, **When** quem elabora abre a
   página 1, **Then** a faixa mostra "Continuar a elaboração" sobre ele.

---

### User Story 3 — Achar qualquer Processo pela busca, de qualquer aba (Priority: P1)

Um gestor precisa do Edital 90/2026, que foi cancelado há um ano. Ele está em "Em andamento", digita
"90/2026" no campo de busca e encontra o Processo, com o selo "Cancelado" ao lado. Uma frase diz que
a busca procurou em todas as situações, e oferece voltar.

**Why this priority**: o recorte padrão só é aceitável se nada ficar difícil de achar. A busca que
respeitasse a aba faria o gestor adivinhar a situação antes de procurar.

**Independent Test**: com Processos nas três situações, buscar a partir de "Em andamento" por
"N/AAAA", por número, por parte do título e por código, e conferir resultados, ordem e frase.

**Acceptance Scenarios**:

1. **Given** um Processo cancelado com o Edital 90/2026, **When** a pessoa busca "90/2026" a partir de
   "Em andamento", **Then** ele aparece, com o selo "Cancelado".
2. **Given** Editais 90/2025 e 90/2026, **When** a pessoa busca "90/2026", **Then** só o de 2026
   aparece; **When** busca "90", **Then** os dois aparecem.
3. **Given** resultados em andamento e cancelados, **When** a busca responde, **Then** os em andamento
   vêm primeiro, depois os encerrados, depois os cancelados, e nenhuma aba fica marcada.
4. **Given** uma busca com resultados fora de "Em andamento", **When** a página responde, **Then** uma
   frase diz quantos resultados há, que a busca é em todas as situações, quantos estão encerrados ou
   cancelados, e oferece "Limpar a busca".
5. **Given** um Processo de outra unidade com o mesmo número, **When** a pessoa busca, **Then** ele
   não aparece.
6. **Given** uma busca sem resultado, **When** a página responde, **Then** diz que nada foi encontrado
   em nenhuma situação, mantém o texto no campo e oferece "Limpar a busca".

---

### User Story 4 — A linha diz o que o Processo e o Edital são, e não o que fazer (Priority: P2)

Quem elabora lê a lista e não encontra mais "Nenhuma ação disponível para seus papéis" nem
contadores zerados. Cada Processo é uma linha (título, código, situação e, para quem gere, os links
Comissão e Alocação por Etapa). Cada Edital é uma linha (número, título quando difere, situação e a
marca da Retificação em curso). O que fazer está na faixa, e todos os atos continuam no detalhe.

**Why this priority**: é a decisão do usuário (variante V1). Ela tira o ruído e a densidade de 236 para
82 pixels por Processo. É P2 porque o recorte e a busca já reduzem a página sem ela.

**Independent Test**: abrir a lista com cada papel e conferir que nenhuma linha traz ação de Edital,
contador ou "Nenhuma ação", e que os acessos ao detalhe, a situação e a marca da Retificação estão
lá.

**Acceptance Scenarios**:

1. **Given** qualquer papel, **When** a pessoa abre a lista, **Then** nenhuma linha de Edital traz
   ação, contador, ato desabilitado ou "Nenhuma ação disponível".
2. **Given** um Edital com Retificação em revisão, **When** a pessoa abre a lista, **Then** a linha
   dele traz a marca "Retificação em revisão · aguarda quem homologa", com link.
3. **Given** quem gere o Processo e não integra a comissão, **When** abre a lista, **Then** a linha do
   Processo traz os links Comissão e Alocação por Etapa.
4. **Given** um Edital cujo título é igual ao do Processo, **When** a pessoa abre a lista, **Then** a
   linha do Edital mostra o número e a situação, sem repetir o título.
5. **Given** a tela a 375 px, **When** a pessoa a abre, **Then** nada rola de lado.

---

### User Story 5 — A faixa diz, antes dos itens, o que ela não cobre (Priority: P2)

A pessoa que conduz a convocação abre a gestão. Logo abaixo do título da faixa, antes dos itens, lê
que a faixa cobre atos de Edital e de Retificação, recursos e avaliações, e que classificação,
sorteio, resultado, convocação, documentos e formalização, Requerimento de Matrícula, avisos e
encerramento ficam em "O que fazer agora", no detalhe de cada Edital. Sem nada na faixa para ela, a
frase vazia diz o mesmo.

**Why this priority**: a faixa é uma fila parcial que se apresenta como completa. Corrigir o texto
custa uma constante e um template, e reduz o risco de quem conclui que não há nada a fazer.

**Independent Test**: abrir a lista com um papel que tem itens e com um que não tem, e conferir a
posição e o conteúdo das duas frases.

**Acceptance Scenarios**:

1. **Given** uma pessoa com itens na faixa, **When** abre a lista, **Then** a nota de cobertura vem
   logo depois do título e antes do primeiro item, e nomeia todas as famílias de fora.
2. **Given** uma pessoa sem itens, **When** abre a lista, **Then** a frase vazia nomeia as mesmas
   famílias, a partir da mesma fonte.

---

### User Story 6 — A página custa o mesmo com 10 ou com 500 Processos, para todo papel (Priority: P3)

Quem exporta para matrícula abre a gestão numa unidade com 700 Editais, e a página responde com o
mesmo número de consultas que numa unidade com 7.

**Why this priority**: hoje é o único papel cujo custo cresce com o acervo. Com a linha sem ações, a
pergunta que custava por Edital deixa de ser feita na lista. O teste que prende isso para todo papel
é o que impede a regressão.

**Independent Test**: medir as consultas da lista com 3, 30 e 300 Editais para cada papel do sistema,
inclusive quem exporta para matrícula com Editais que declaram Requerimento, em duas abas e duas
páginas.

**Acceptance Scenarios**:

1. **Given** 3, 30 e 300 Editais na unidade, **When** cada papel abre a lista, **Then** o número de
   consultas é o mesmo nos três tamanhos.
2. **Given** o mesmo acervo, **When** a pessoa troca de aba, busca ou muda de página, **Then** o número
   de consultas não muda.

---

### Edge Cases

- **Processo sem Edital**: aparece na aba da sua situação, com "Nenhum Edital neste Processo."
- **Processo em elaboração sem Edital**: em "Em andamento".
- **Processo cancelado com Edital em elaboração ou publicado** (anterior à regra de 28/09): em "Em
  andamento", com o selo "Cancelado" (FR-4301).
- **Aba sem Processo**: a aba aparece com zero, e a lista diz "Nenhum Processo nesta situação."
- **Unidade sem nenhum Processo**: as abas aparecem com zero; o estado vazio de hoje continua.
- **Busca só com espaços**: é tratada como ausência de busca, e a aba volta a valer.
- **"90/" ou "/2026"**, ou uma barra com ano de menos de quatro dígitos: não são "N/AAAA", e se buscam
  como texto.
- **Busca por "PS-DEMO" ou por parte do código**: casa o código do Processo.
- **Busca que casa o título de um Edital, e não o do Processo**: o Processo aparece, com **todos** os
  seus Editais; a busca escolhe Processos, e não esconde Edital de dentro deles.
- **Página além da última**: mostra a última. **Página inválida** (texto, zero, negativa): mostra a
  primeira. **Aba inválida**: cai em "Em andamento".
- **Busca com página**: a paginação vale sobre os resultados da busca, e os links de página preservam a
  busca.
- **Aba trocada durante uma busca**: a busca é limpa e a aba é aplicada.
- **Processo com muitos Editais**: não se divide entre páginas, e não há limite de Editais por linha.
- **Processo que muda de situação entre duas páginas** (outra pessoa o encerra): pode aparecer duas
  vezes ou nenhuma na navegação. É o comportamento comum de paginação por deslocamento, e o detalhe
  continua a fonte.
- **Pessoa sem papel nenhum**: continua lendo "Sem permissões"; as abas e a busca funcionam sobre o que
  o escopo dela alcança.
- **Pessoa que atua em mais de uma unidade**: vê a unidade da sessão ("Atuando em"); a busca não
  atravessa unidades.
- **Retificação parada por desfecho**: a marca continua dizendo "não pode mais prosseguir".

## Requirements *(mandatory)*

### Functional Requirements

#### O recorte

- **FR-4300**: A lista MUST abrir na aba "Em andamento" quando a pessoa chega sem parâmetro de aba
  nem de busca.
- **FR-4301**: "Em andamento" MUST reunir todo Processo da unidade cuja situação não seja Encerrado
  nem Cancelado, **e também** todo Processo encerrado ou cancelado que tenha algum Edital fora de
  Encerrado e Cancelado. O recorte MUST NOT usar a situação do Edital para excluir Processo, nem
  data alguma.
- **FR-4302**: "Encerrados" MUST reunir os Processos encerrados cujos Editais estão todos encerrados
  ou cancelados; "Cancelados", os cancelados nas mesmas condições; "Todos", a unidade inteira. As três
  primeiras abas MUST particionar a unidade: cada Processo está em exatamente uma.
- **FR-4303**: Cada aba MUST mostrar quantos **Processos** ela reúne, independentemente da busca e da
  página. A aba aberta MUST ser identificada por texto acessível, e não só por cor.
- **FR-4304**: O selo da linha do Processo MUST dizer a situação real dele, também quando o recorte o
  põe em "Em andamento" por causa de um Edital (FR-4301).

#### A busca

- **FR-4305**: A lista MUST oferecer um campo de busca, com rótulo visível, que procura em **todas**
  as situações da unidade, qualquer que seja a aba aberta.
- **FR-4306**: A busca MUST encontrar o Processo pelo título, pelo código, pelo título de qualquer
  Edital dele e pelo número de qualquer Edital dele. "N/AAAA" MUST casar número **e** ano; "N" sozinho
  MUST casar o número em qualquer ano. A busca MUST ignorar maiúsculas e minúsculas e os espaços nas
  pontas.
- **FR-4307**: A busca MUST NOT encontrar Processo fora da unidade da sessão.
- **FR-4308**: Os resultados MUST vir na ordem das abas: em andamento, depois encerrados, depois
  cancelados. Dentro de cada grupo, MUST valer a mesma ordem estável das abas: do mais recente ao mais
  antigo.
- **FR-4309**: Com busca, nenhuma aba MUST ficar marcada como aberta, e uma frase MUST dizer, antes
  dos resultados:
  - quantos Processos a busca encontrou;
  - que ela procurou em todas as situações;
  - quantos dos encontrados estão encerrados ou cancelados, quando houver algum.

  A frase MUST oferecer "Limpar a busca", que volta a "Em andamento".
- **FR-4310**: Busca sem resultado MUST dizer que nada foi encontrado em nenhuma situação, manter o
  texto no campo e oferecer "Limpar a busca".

#### A paginação e o endereço

- **FR-4311**: A lista MUST mostrar no máximo 20 Processos por página. Os Editais de um Processo MUST
  NOT se dividir entre páginas.
- **FR-4312**: Acima dos Processos, uma frase MUST dizer o total do recorte (ou da busca) e o intervalo
  mostrado ("61 Processos, mostrando 1–20"). A navegação entre páginas MUST aparecer só quando houver
  mais de uma, com anterior, seguinte e a página atual.
- **FR-4313**: A aba, a busca e a página MUST ficar no endereço da página, de modo que o voltar do
  navegador, um link copiado e uma página recarregada mostrem o mesmo recorte.
- **FR-4314**: Trocar de aba MUST voltar à página 1 e limpar a busca. Uma nova busca MUST voltar à
  página 1. Os links de página MUST preservar a aba ou a busca.
- **FR-4315**: Aba inválida MUST cair em "Em andamento"; página inválida, na primeira; página além da
  última, na última. Nenhum desses casos MUST responder erro.
- **FR-4316**: Os links da barra lateral e da trilha para a lista MUST levar ao padrão (FR-4300). A
  lista MUST NOT guardar o recorte em sessão.

#### A linha (variante V1)

- **FR-4317**: A linha do Processo MUST trazer:
  - o título, com link para o detalhe;
  - o código;
  - o selo da situação;
  - o vínculo da pessoa com a comissão, quando houver;
  - para quem gere o Processo, os links Comissão e Alocação por Etapa, como hoje.
- **FR-4318**: A linha de cada Edital MUST trazer:
  - o número e o ano, com link para o detalhe;
  - o título, só quando difere do título do Processo;
  - o selo da situação;
  - a marca de cada Retificação em curso, com a situação dela e quem ela aguarda (FR-2706 da `103`;
    FR-2817, FR-2821 e FR-2822 da `104`).
- **FR-4319**: A lista MUST NOT apresentar ação de Edital, contador de inscrições ou de recursos, ato
  desabilitado nem a frase "Nenhuma ação disponível para seus papéis". Os atos continuam no detalhe do
  Edital, com o conjunto, os desabilitados e os motivos da `007` (FR-023, FR-024).
- **FR-4320**: A lista MUST NOT ser tabela, nem ter cabeçalho de colunas. A 375 px, a linha do Edital
  pode omitir o título, e MUST NOT rolar de lado.
- **FR-4321**: O resumo "Editais por situação" e o total "Editais no total" MUST sair da página. As
  abas contam no nível da página, que é o Processo (FR-4303).
- **FR-4322**: O subtítulo MUST nomear a unidade pelo nome do registro de Unidades (`110`), e não pelo
  código do escopo.

#### A faixa

- **FR-4323**: A faixa "Ações disponíveis para você" MUST ser derivada de todos os Editais da unidade,
  independentemente da aba, da busca e da página: os mesmos itens, na mesma ordem, com o mesmo total,
  em toda combinação delas.
- **FR-4324**: A faixa MUST dizer o que cobre e o que não cobre **logo depois do título e antes do
  primeiro item**. A frase MUST nomear como fora da faixa:
  - classificação;
  - sorteio;
  - resultado;
  - convocação;
  - documentos e formalização;
  - Requerimento de Matrícula;
  - avisos aos candidatos;
  - encerramento.

  Ela MUST dizer também que essas famílias ficam em "O que fazer agora", no detalhe de cada Edital
  (`127`). Este requisito emenda a FR-2812 da `104`, que nomeava três famílias e punha a frase depois
  dos itens.
- **FR-4325**: Sem item na faixa, a frase vazia MUST nomear as mesmas famílias, a partir da mesma fonte
  da FR-4324, sem número e sem caixa (FR-2808 da `104`).
- **FR-4326**: O conteúdo, a ordem, o título, o limite de cinco itens e o "Mostrar os outros" da faixa
  MUST continuar os da `104` (FR-2807 a FR-2811 e FR-2813).

#### O custo

- **FR-4327**: O número de consultas da lista MUST NOT crescer com o número de Processos ou de Editais
  da unidade, nem mudar com a aba, a busca ou a página, para **todo** papel do sistema, inclusive
  quem exporta para matrícula e quem julga recursos.
- **FR-4328**: O que a lista precisar saber por Edital MUST ser lido de uma vez, para a página ou para
  a unidade, e nunca uma consulta por Edital. Em particular, se a lista ainda precisar saber se um
  Edital declara Requerimento de Matrícula, MUST lê-lo em lote, pela versão vigente de todos os
  Editais de uma vez.

#### Compatibilidade

- **FR-4329**: A garantia da FR-023 da `007` (um só conjunto de ações por Edital, e a ausência derivada
  dele) MUST continuar no detalhe do Edital. Como a lista deixa de apresentar ações, a comparação entre
  lista e detalhe MUST ser substituída por duas garantias:
  - a lista não apresenta ação alguma;
  - todo ato de Edital que a faixa nomeia para uma pessoa (elaborar, submeter, homologar, publicar) o
    detalhe do mesmo Edital também oferece a ela.

### Experiência

- **UX-270**: As abas MUST ser uma navegação, com a aba aberta marcada como a página atual para leitor
  de tela e por um traço visível que não depende de cor. A contagem MUST fazer parte do nome acessível
  de cada aba.
- **UX-271**: A busca MUST ter rótulo visível ("Buscar em todas as situações"), aceitar Enter e ter um
  botão. O texto buscado MUST permanecer no campo depois da resposta.
- **UX-272**: A ordem de leitura MUST ser: faixa, "Novo Processo Seletivo", abas, busca, a frase do
  recorte ou da busca, os Processos, a paginação. Dentro de cada Processo, a linha dele antes das linhas
  dos Editais.
- **UX-273**: A frase da busca (FR-4309, FR-4310) MUST vir antes dos resultados e ser alcançável por
  teclado, com "Limpar a busca" como link.
- **UX-274**: Os selos de situação, a marca da Retificação e o vínculo com a comissão MUST continuar
  ditos por texto, e não só por cor (FR-2708 da `103`).

### Key Entities

Nenhuma entidade nova. A spec lê o que existe:

- **Processo Seletivo**: título, código, situação (Em elaboração, Ativo, Encerrado, Cancelado), unidade
  e data de criação.
- **Edital**: número, ano, título e situação, e as Retificações em curso.
- **Unidade** (`110`): o nome, para o subtítulo.
- **Objeto de trabalho** (`104`): o item da faixa, derivado como hoje.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1310**: Numa unidade com 200 Processos, dos quais 60 em andamento, a página padrão de quem
  gere mede no máximo **3,5 telas** de 900 px no computador e **5 telas** a 375 px. A revisão mediu
  3,1 e 4,6 na maquete, contra 59 e 101 hoje.
- **SC-1311**: Todo Processo da unidade é encontrado por uma única busca pelo "N/AAAA" de qualquer
  Edital dele, a partir de qualquer aba: 100% dos casos do teste, nas três situações.
- **SC-1312**: A faixa é idêntica (itens, ordem e total) nas quatro abas, numa busca e em duas páginas,
  para cada papel do teste: zero diferenças.
- **SC-1313**: O número de consultas da lista é o mesmo com 3, 30 e 300 Editais, e entre abas e
  páginas, para cada papel do sistema: crescimento zero. Hoje, quem exporta para matrícula cresce duas
  consultas por Edital.
- **SC-1314**: A lista não mostra nenhuma vez "Nenhuma ação disponível" nem contador zerado, para
  nenhum papel. Hoje são 181 e 227 numa unidade de 211 Processos.
- **SC-1315** *(validação humana)*: Em sessão com duas pessoas da equipe, de papéis diferentes, cada
  uma acha um Processo cancelado indicado só pelo número do Edital, sem ajuda, em menos de 30 segundos.
  Nenhuma conclui pela faixa que não há convocação ou resultado pendente quando há.

## Assumptions

- **A `127` está na `main`.** O cartão "O que fazer agora" do detalhe do Edital nomeia as providências
  por papel de sorteio, classificação, resultado e convocação, e é para ele que a nota de cobertura
  aponta (FR-4324).
- **A busca não ignora acentos.** "matematica" não casa "Matemática". Ignorar acentos no banco pediria
  uma extensão do PostgreSQL, e portanto migration, que esta spec não faz. Se a validação pedir, é
  evolução separada.
- **A ordem dentro de cada aba é a de hoje**, do Processo criado mais recentemente ao mais antigo, com
  desempate estável.
- **20 Processos por página** foi validado pela densidade medida (seção 5 da revisão), e não por
  pesquisa com pessoas.
- **Uma unidade por sessão.** Quem atua em mais de uma troca pela "Atuando em" (`109`), e a lista
  segue a unidade da sessão.
- **O detalhe do Edital continua oferecendo** "Inscrições recebidas", "Recursos aguardando decisão",
  "Retificar", "Encerrar", "Cancelar" e "Exportar para matrícula". Quem usava esses atalhos na lista
  passa a dar um clique a mais.
- **Os Processos em andamento parados** (ativos com todos os Editais encerrados e nada a fazer) ficam em
  "Em andamento" até alguém os encerrar. É a limitação conhecida: a busca e a paginação a contêm, e um
  sinal de encerramento é da Frente B.

## Compatibilidade com regras anteriores

| Requisito | Da | O que muda |
|---|---|---|
| FR-1049 (ordem das ações na coluna) | `057` | **Substituído** pela FR-4319: não há coluna |
| FR-1050 (contador zero esmaecido) | `057` | **Substituído** pela FR-4319 |
| FR-2812 (o que a faixa não cobre) | `104` | **Emendado** pela FR-4324: todas as famílias, antes dos itens |
| FR-2814 (ato da Retificação na coluna) | `104` | **Substituído** pela FR-4319: o ato fica na faixa; a marca, na linha (FR-4318) |
| FR-2815 ("Conferir e submeter / publicar" na lista) | `104` | **Substituído** pela FR-4319: a faixa e o detalhe continuam com as frases |
| FR-2816 (ato que a segregação recusaria, desabilitado na lista) | `104` | **Substituído** pela FR-4319: continua no detalhe |
| FR-2818 (contagens da coluna lidas para a página) | `104` | **Sem objeto**: a coluna sai; a faixa continua lendo em lote (FR-4328) |
| FR-023 (um só conjunto de ações; a comparação lista × detalhe) | `007` | **Mantido no detalhe**; a comparação muda de forma (FR-4329) |
| FR-2817 (situação do Edital e da Retificação em lugares distintos) | `104` | **Mantido** (FR-4318) |
| FR-2706 (a marca da Retificação na linha) | `103` | **Mantido** na forma que a FR-2817 da `104` lhe deu: a marca diz a situação e quem age a seguir; o ato da pessoa, que a `104` levou para a coluna, fica na faixa |
| FR-2707 (Retificações em curso lidas sem custo por Edital) | `103` | **Mantido**, agora para os Editais da página (FR-4328) |
| FR-1740 e FR-1741 (só "Novo Processo Seletivo" no topo) | `077` | **Mantidos** |

A revogação não apaga os requisitos das specs anteriores, que são o registro de quando e por que eles
valeram. Os testes que os prendem mudam com esta feature, e o relatório dela os lista.

## Decisões

### D-001 — O recorte é pelo Processo, e o Edital não final puxa para "Em andamento"

O critério de "concluído" é a situação do **Processo**, e nunca a do Edital nem data alguma: Edital
encerrado ainda convoca, recebe documento e recurso (seção 7 da revisão, 25 casos contra PostgreSQL).
O Processo final com Edital não final, que existe no acervo anterior a 28/09, vai para "Em andamento"
(FR-4301). Assim o recorte fica estritamente mais seguro que o critério puro, e a regra não depende de
conferir o banco de produção. É a quinta decisão da revisão.

### D-002 — Quatro abas, e os cancelados à parte

"Em andamento", "Encerrados", "Cancelados" e "Todos". Encerrar e cancelar não são sinônimos
(`processos/domain/finalizacao.py`, FR-005 e FR-006 da `001`): juntar as duas abas misturaria conclusão
regular e interrupção. É a segunda decisão da revisão, na alternativa recomendada.

### D-003 — A linha só diz fatos (variante V1)

Decidida pelo usuário em 06/11/2026. A coluna "O que posso fazer" sai da lista. A linha fica com a
situação, a Retificação em curso e os acessos ao detalhe. A outra variante medida punha na linha o ato
da faixa sobre cada Edital. Ela foi descartada porque um Edital publicado sem link pareceria não pedir
nada, quando pode ter convocação vencida ou resultado a divulgar, que a faixa não cobre. A linha
passaria a reproduzir a incompletude da faixa no inventário inteiro. Os requisitos que isso substitui
estão em *Compatibilidade*.

### D-004 — A busca ignora a aba

Buscar dentro da aba obrigaria a pessoa a adivinhar a situação do que procura, e é justamente o
cancelado de um ano atrás que se procura pelo número. Por isso a busca procura em tudo, desmarca a aba
e diz isso numa frase (FR-4309). "N/AAAA" se trata à parte porque é como o Edital é citado. A busca da
Visão Geral, que só casa o número como texto, não o trata.

### D-005 — 20 por página, no endereço, sem memória em sessão

Com a linha compacta, 20 Processos ocupam 3,1 telas, e 30 ocupariam 4,0, com o "Próxima" longe demais
da faixa. O endereço basta para o voltar do navegador. Memória em sessão mudaria o padrão em silêncio
para quem clica em "Processos Seletivos" esperando o começo.

### D-006 — A faixa lê a unidade, e a lista não esconde trabalho

A faixa é o único lugar da página que diz trabalho, e o recorte não pode alcançá-la (FR-4323). A
revisão conferiu contra PostgreSQL o caso que a decisão 021 da `127` levantava. Com o Processo
encerrado ou cancelado, a faixa ainda oferece "Decidir recursos" a quem julga, em todas as situações,
inclusive com o Edital cancelado, em que o detalhe não tem andamento. O recurso é o único ato com
providência que o domínio aceita nesse estado. A designação de formalização, também aceita, não é
providência nem da faixa nem da `127`, e se alcança pela aba ou pela busca.

A divergência entre o texto daquela decisão e o comportamento é o achado A-6 da revisão, e não é desta
spec. A lista segue o domínio: se o recurso no Processo final vier a ser recusado (A-1, A-2), a faixa
deixa de oferecê-lo, e a lista não muda.

### D-007 — O custo do exportador se resolve tirando a pergunta da linha, e o teste prende todo papel

O custo que crescia com o acervo vinha de a coluna perguntar, Edital a Edital, se ele declara
Requerimento de Matrícula, para oferecer "Exportar para matrícula". Sem a coluna, a lista não faz mais
essa pergunta, e o custo sai por construção. A forma em lote (FR-4328) foi prototipada (de 451 para 11
consultas com 249 Editais, sem divergência) e fica como regra para o que a lista vier a perguntar por
Edital. O que impede a regressão é o teste da FR-4327, que mede **todo** papel. O teste de escala da
`104` media quatro, e nenhum deles exportava.

### D-008 — O que a página não decide

A lista não sugere encerrar, não encerra, não arquiva e não muda a confirmação de "Encerrar Processo".
Encerrar continua sendo ato manual do gestor, no detalhe do Processo, como hoje. A advertência das
providências em aberto nessa confirmação é a décima decisão da revisão, e o usuário a quer antecipada
em separado. Ela reduz o risco de cortar o convocado no meio do prazo, mas não o elimina, e impedir o
encerramento seria outra decisão de domínio.
