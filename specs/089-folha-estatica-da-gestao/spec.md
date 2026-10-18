# Feature Specification: A folha comum da gestão em arquivo estático, sem mudar regra nenhuma

**Feature Branch**: `claude/folha-estatica-089-1fcd9d`, sobre a `main` em `46c374cc`, com o PR #305
(`088`), que acrescentou uma regra `@media print` à mesma folha

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: passo 1 de três, aprovado pelo usuário em 18/10/2026, depois de a etapa 4 do redesign da
gestão terminar a modernização tela a tela (`075` a `088`): mover a folha de estilo comum da gestão para
fora do HTML, sem mudar nada do que se vê, pelo peso das páginas e para permitir uma política de
segurança de conteúdo (CSP) no futuro. Os passos 2 (os estilos por página) e 3 (ligar a CSP) ficam fora.

> **Faixa de identificadores.** Esta spec usa FR-2030 a FR-2043 e SC-790 a SC-795, da faixa reservada
> a ela (FR-2030–2059, SC-790–799). Nenhum dos dois aparecia na `main` (`c97ff8af`) nem na branch do
> PR #305 em 18/10/2026; a faixa da `088` termina antes desta.

---

## Por que esta feature existe

**Toda página da gestão carrega a folha inteira, de novo, sem cache.** Medido em 18/10/2026 na `main`
`c97ff8af`: o modelo comum da gestão tem 1.561 linhas, 1.471 delas dentro de um bloco de estilo — os
tokens de cor e medida e ~930 regras, entremeadas por 162 comentários de modelo. Os comentários não
saem na resposta; as regras saem, **53.383 bytes** delas, em toda resposta HTML de `/gestao/`. Como
estão dentro do HTML, o navegador não as guarda: abrir dez telas é baixar a mesma folha dez vezes.

**O peso já mandou no desenho de uma tela.** A Distribuição é a página mais pesada do sistema, e um
guardião de desempenho a prende abaixo de 120.000 bytes. Ela chegou a 116 bytes do teto em 30/09; a
`040` precisou inventar um ponto de extensão — o estilo "daquela página, e não de todas" — porque 4 KB
de regras de uma tela só a fizeram estourar; e um comentário da própria folha registra que, escrito
como comentário de CSS, ele mesmo estourou o teto em 40 bytes. Metade do orçamento da tela mais pesada
é a folha que todas as outras já baixaram.

**Folha dentro do HTML impede a CSP.** Uma política de segurança de conteúdo que recuse estilo embutido
é a defesa padrão contra injeção de estilo e de marcação; ela não pode ser ligada enquanto a folha
principal da gestão for embutida. Este passo não liga a política; tira do caminho o maior obstáculo.

**O que não muda, e não se negocia aqui:** nenhuma regra de estilo — seletor, propriedade, valor ou
ordem. Nenhum pixel de nenhuma tela. Nenhuma regra de negócio, permissão, endereço de tela, view,
consulta ao banco, texto ou conteúdo normativo. Os estilos por página — os cinco parciais de estilo e o
bloco de estilo das 30 telas que o usam — ficam onde estão. A folha própria do portal do candidato fica
onde está; só os tokens, que ela divide com a gestão, saem.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem trabalha na gestão vê as mesmas telas, mais leves (Priority: P1)

A avaliadora abre a lista de Processos, depois Minhas Etapas, depois a Distribuição de uma etapa com
centenas de inscrições. Cada tela é idêntica à de ontem, pixel a pixel, com a barra expandida ou
recolhida, a 1280 e a 375 px. Da segunda tela em diante, a folha comum não é baixada de novo: o
navegador a reaproveita, e cada resposta traz só o HTML da tela.

**Why this priority**: é a razão do passo — o peso — com a condição que o usuário pôs: nada muda de
aparência.

**Independent Test**: refazer o inventário visual de todas as telas da gestão antes e depois e
comparar pixel a pixel; medir o tamanho das respostas HTML e o que o navegador transfere da folha na
segunda tela.

**Acceptance Scenarios**:

1. **Given** qualquer tela do inventário visual, nos dois estados da barra, a 1280 e a 375 px, **When**
   ela é capturada antes e depois, **Then** as duas imagens só diferem no ruído conhecido (hora,
   cursor, suavização de texto), nenhuma estoura a largura e nenhuma muda de `status`.
2. **Given** a Distribuição, a lista de Processos e Minhas Etapas, **When** a resposta HTML é medida
   antes e depois, **Then** cada uma diminui pelo menos o tamanho das regras comuns que deixou de
   carregar.
3. **Given** uma segunda tela da gestão aberta na mesma sessão do navegador, **When** a página carrega,
   **Then** a folha comum vem do cache do navegador, e não da rede.

---

### User Story 2 — Quem mantém a folha muda uma regra e vê a mudança, sem cache velho (Priority: P1)

O desenvolvedor muda uma cor na folha comum, recarrega a tela no servidor local e vê a cor nova — sem
reiniciar o servidor e sem limpar o cache do navegador. Depois de uma implantação, quem já tinha a
folha antiga recebe a nova na primeira página que abrir.

**Why this priority**: tirar a folha do HTML troca um problema (peso) por outro (cache velho), que já
custou uma medição errada na `053` com um script da interface. Sem isso o passo não se paga.

**Independent Test**: mudar o conteúdo da folha e conferir que o endereço com que a página a pede muda;
não mudar e conferir que o endereço é o mesmo.

**Acceptance Scenarios**:

1. **Given** o servidor local em execução, **When** a folha comum é editada e a página recarregada,
   **Then** a página pede a folha por um endereço novo e mostra a regra nova.
2. **Given** a mesma folha, sem edição, **When** duas páginas são abertas, **Then** as duas a pedem pelo
   mesmo endereço.
3. **Given** uma implantação nova com a folha mudada, **When** quem tinha a anterior em cache abre uma
   página, **Then** recebe a nova.

---

### User Story 3 — Quem mantém a folha continua protegido pelos mesmos guardiões (Priority: P1)

O desenvolvedor acrescenta, por engano, uma largura fixa em pixels ou uma classe sem regra na folha
comum — agora num arquivo estático. Os mesmos testes que reprovavam o engano quando a folha estava no
modelo continuam reprovando.

**Why this priority**: 23 arquivos de teste leem a folha como texto ou renderizada, e em 14 deles há
pelo menos uma verificação que, lendo o modelo depois da mudança, passaria sem examinar nada — o pior
defeito possível de uma mudança "sem mudança" (R-005 da pesquisa).

**Independent Test**: para cada guardião, plantar no arquivo estático uma violação da regra que ele
cobra e ver o teste reprovar; tirar a violação e ver passar.

**Acceptance Scenarios**:

1. **Given** cada guardião que lia a folha comum, **When** uma violação da regra dele é plantada na
   folha estática, **Then** ele reprova.
2. **Given** a página de uma tela, **When** o guardião que lê a folha renderizada a examina, **Then** ele
   examina os tokens, a folha comum e o estilo da página, na ordem em que o navegador os aplica.

---

### User Story 4 — A página de acesso, o portal e a página de erro continuam iguais (Priority: P2)

A pessoa que entra pela página de identificação da gestão, o candidato no portal e quem cai numa
página inexistente veem as mesmas cores e medidas de antes. Os tokens que as quatro páginas dividem
vêm de um arquivo só.

**Why this priority**: os tokens são a garantia de que a gestão e o portal não divergem de cor; movê-los
mal faria uma das bases perder a paleta inteira.

**Independent Test**: capturar antes e depois a página de identificação e duas telas do portal;
conferir que os tokens têm uma fonte só.

**Acceptance Scenarios**:

1. **Given** a página de identificação da gestão e duas telas do portal, **When** capturadas antes e
   depois a 1280 e a 375 px, **Then** só diferem no ruído conhecido.
2. **Given** o repositório, **When** se procura onde os tokens são definidos, **Then** há um lugar só.

### Edge Cases

- **A folha não carrega.** Se o arquivo estático não for servido (endereço errado, servidor sem o
  diretório), a gestão aparece sem estilo, mas utilizável: o HTML não depende da folha para funcionar,
  e as telas continuam com os estilos por página. O guia de implantação diz o que o servidor de
  produção precisa servir, e a lista de verificação da implantação confere a folha.
- **Tela com estilo próprio.** As regras do estilo por página continuam vindo depois da folha comum, e
  vencem os empates como hoje — a cascata não muda de ordem.
- **Impressão.** As regras de impressão da folha comum (`076` e `088`) continuam valendo: a barra não
  sai no papel, e a trilha do cabeçalho sai como a `088` decidiu.
- **Primeira visita.** A primeira página da sessão baixa a folha; o desenho não pisca sem estilo,
  porque a folha é carregada antes do corpo da página.
- **Página de identificação, antes da identidade.** A folha e os tokens são servidos sem exigir
  identidade: a página de entrada precisa deles antes de alguém se identificar.
- **Página de erro do servidor de produção.** A página de erro que o servidor da aplicação monta
  (endereço inexistente) também usa os tokens, e continua com eles.
- **Comentário que fala de comentário.** Um dos comentários da folha cita a sintaxe do comentário de
  CSS; ao virar comentário de CSS, ele não pode encerrar a si mesmo nem deixar a regra seguinte
  dentro de um comentário.
- **Duas sessões editando a folha.** Fora do escopo: o endereço versionado resolve cache velho, não
  conflito de edição.

## Requirements *(mandatory)*

### Functional Requirements

#### A folha sai do modelo

- **FR-2030**: As regras da folha comum da gestão MUST passar, na mesma ordem e sem mudança de
  seletor, propriedade ou valor, do bloco de estilo do modelo comum para um arquivo estático próprio
  da gestão.
- **FR-2031**: O modelo comum da gestão MUST carregar, no cabeçalho do documento, os tokens e depois a
  folha comum, como folhas externas, antes do estilo da página; o estilo da página MUST continuar no
  documento, depois das duas, para a ordem da cascata não mudar. O modelo MUST NOT conter regra da
  folha comum.
- **FR-2032**: Os tokens de cor e medida MUST ter uma fonte só, um arquivo estático; o parcial de
  modelo que os continha MUST sair. As quatro bases que os incluíam — a da gestão, a da página de
  acesso, a do portal e a página de erro — MUST carregá-los desse arquivo, antes de qualquer outra
  regra.
- **FR-2033**: Nenhum comentário explicativo da folha MUST se perder: cada um MUST ficar junto da regra
  que explica, como comentário do arquivo estático; o comentário que explica o ponto de extensão do
  estilo por página MUST ficar no modelo, junto do ponto de extensão.

#### Cache e versão

- **FR-2034**: O endereço pelo qual uma página pede a folha comum e os tokens MUST mudar quando o
  conteúdo do arquivo mudar, e MUST NOT mudar enquanto o conteúdo for o mesmo — no servidor local, sem
  reiniciá-lo, e em produção, a cada implantação.
- **FR-2035**: O mecanismo de versão MUST NOT exigir dependência nova nem passo novo de implantação além
  do que o guia de implantação já descreve, que MUST ser atualizado para servir o diretório dos tokens
  e para conferir a folha na lista de verificação.

#### O que fica

- **FR-2036**: Os cinco parciais de estilo da gestão e o bloco de estilo por página das telas que o usam
  MUST continuar como estão; a folha própria do portal e a da página de erro MUST continuar no
  documento, menos os tokens.
- **FR-2037**: A política de segurança de conteúdo MUST NOT ser ligada nesta feature; a pesquisa MUST
  registrar quantos atributos de estilo embutido restam nos modelos, por aplicação.

#### Os guardiões

- **FR-2038**: Todo teste que lia a folha comum ou os tokens — como texto, no modelo, ou na página
  renderizada — MUST passar a ler o arquivo estático, ou, quando lia a página renderizada, a página
  mais as folhas que ela carrega, na ordem em que são aplicadas. Nenhum MUST ficar mais fraco: cada um
  MUST ser provado por mutação — uma violação da regra dele plantada no arquivo estático MUST
  reprová-lo.
- **FR-2039**: Os testes que, depois da mudança, leriam texto de comentário que antes não liam MUST
  continuar examinando o que examinavam antes — só as regras, quando liam só regras.
- **FR-2040**: O guardião de peso da Distribuição MUST continuar com o teto de 120.000 bytes; a pesquisa
  MUST registrar o tamanho da resposta HTML da Distribuição e de mais duas telas antes e depois, e o
  tamanho da folha comum e dos tokens.

#### O que não pode piorar

- **FR-2041**: Nenhuma variante do inventário visual MUST mudar de aparência além do ruído conhecido,
  deixar de carregar, mudar de `status` ou passar a estourar a 375 ou a 1280 px, com a barra expandida
  e com ela recolhida; o mesmo MUST valer para a página de identificação da gestão e duas telas do
  portal.
- **FR-2042**: As regras de impressão da folha comum MUST continuar valendo no papel como antes.
- **FR-2043**: Os arquivos estáticos da folha comum e dos tokens MUST NOT conter sintaxe de modelo:
  ao sair do modelo, eles deixam de passar pela renderização, e o guardião que varria a página
  renderizada atrás de sintaxe vazada não os alcança.

### Key Entities

Nenhuma. Só apresentação e entrega de arquivos estáticos.

## Decisões

### D-001 — Os tokens viram arquivo estático, e o parcial sai

O parcial de tokens era incluído dentro do bloco de estilo de quatro páginas. Ficar com ele como fonte
e gerar o estático a partir dele exigiria um passo de geração e um teste de que os dois estão iguais —
duas cópias do mesmo dado, com um guardião para impedir que divirjam. Sai o parcial; o arquivo estático
é a fonte única, com o comentário do parcial no topo. As quatro páginas o carregam por folha externa.
Como o diretório comum de modelos não pertence a aplicação nenhuma, o diretório comum de estáticos
também não, e é declarado do mesmo jeito.

### D-002 — Os comentários vão como comentário de CSS, junto da regra

Duas saídas: comentário de CSS no arquivo, ou a documentação. A documentação separaria a explicação da
regra que ela explica — o contrário da convenção do repositório, de comentário que registra a decisão
onde a decisão está. Com a folha fora do HTML, o argumento que fazia os comentários serem de modelo —
"comentário de CSS viaja em toda página" — deixa de valer: o arquivo viaja uma vez e fica no cache. O
custo é o tamanho do arquivo, que dobra (≈ 53 KB de regras e ≈ 52 KB de comentário), pago na primeira
visita. O comentário que afirmava o argumento antigo fica, com uma linha que registra a mudança. O que
explica o ponto de extensão do estilo por página fica no modelo, porque o ponto de extensão fica lá.

### D-003 — A versão é o resumo do conteúdo, no endereço

O endereço da folha leva um parâmetro com o resumo criptográfico do conteúdo do arquivo. O resumo é
memorizado pelo arquivo, pela data e pelo tamanho dele: a página só relê a folha quando ela mudou — no
servidor local, a edição ganha endereço novo sem reiniciar; em produção, a folha da implantação nova
ganha endereço novo, e cada pedido custa só a consulta à data do arquivo. Como o endereço muda com o
conteúdo, o servidor de produção pode mandar o navegador guardar a folha sem revalidá-la. Uma folha que
falta é recusada pela verificação de sistema do framework, antes de o serviço atender alguém. Descartado: o armazenamento com manifesto do
próprio framework, que exige coletar os estáticos num diretório na implantação — o guia de produção
serve os diretórios de estáticos da release diretamente, sem coleta, e a coleta é uma lacuna aberta do
guia; fechá-la é mudar a implantação, e não mover uma folha. Descartado também o número da versão do
sistema: muda a cada implantação, mesmo quando a folha não mudou, e descarta o cache sem motivo.

### D-004 — O estilo por página fica num bloco de estilo, depois das folhas externas

O ponto de extensão da `040` continua no documento, num bloco de estilo que só tem ele. A ordem do
documento — tokens, folha comum, estilo da página — é a ordem da cascata de antes. Os parciais de estilo
e os blocos das 30 telas ficam como estão; levá-los para arquivos é o passo 2, e a CSP, o passo 3.

### D-005 — Os guardiões leem o que o navegador aplica

Um guardião que lia a folha renderizada passa a montar a mesma coisa que o navegador monta: as folhas
externas que a página carrega, na ordem, mais o estilo do documento. Um guardião que lia o modelo como
texto passa a ler o arquivo estático. Na folha montada a partir da página, os comentários das folhas externas
ficam de fora: a folha renderizada de antes não os tinha, porque os de modelo não saem na resposta, e
o guardião continua lendo o mesmo texto. Quem lia o modelo como texto já via a prosa dos comentários, e
continua vendo — a exposição é a mesma. Uma afirmação negativa nunca pode passar por ler o lugar
errado: por isso cada guardião é provado por mutação, e não só pela suíte verde.

### D-006 — O teto da Distribuição fica

O teto de 120.000 bytes protege a tela com mais linhas. Com a folha fora, a resposta da Distribuição cai
≈ 53 KB, e o teto passa a sobrar; baixá-lo é decisão de produto e fica fora. A pesquisa registra que,
fora do HTML, o crescimento da folha comum deixa de ser cobrado por esse teto — o achado vai para o
usuário decidir se a folha ganha teto próprio.

## Success Criteria *(mandatory)*

- **SC-790**: Refeito o inventário visual nos dois estados da barra, **zero** variantes diferem pixel a
  pixel além do ruído conhecido, **zero** estouram, e **nenhuma** muda de `status`; o mesmo na página
  de identificação e em duas telas do portal.
- **SC-791**: Cada resposta HTML da gestão diminui **pelo menos 50.000 bytes**, medidos na Distribuição,
  na lista de Processos e em Minhas Etapas.
- **SC-792**: Da segunda tela da gestão em diante, numa mesma sessão do navegador, a folha comum
  transfere **zero** bytes de conteúdo — só a revalidação do cache.
- **SC-793**: **Todos** os 23 arquivos de guardião que liam a folha comum ou os tokens reprovam diante de uma violação
  plantada no arquivo estático, um a um.
- **SC-794**: A suíte contra PostgreSQL continua sem falhas.
- **SC-795**: O modelo comum da gestão passa de 1.471 linhas de estilo para **zero** regras da folha
  comum; o único estilo que lhe resta é o ponto de extensão por página.

## Assumptions

- A folha comum é o conteúdo do bloco de estilo do modelo comum da gestão: os tokens, as regras e os
  comentários entre eles. O ponto de extensão do estilo por página não é a folha comum.
- A folha e os tokens não são sigilosos: são servidos a quem não se identificou, como os scripts da
  interface já são.
- O inventário visual de 16/10 (`doc/inventario-visual-da-gestao-2026-10-16/`), com as ferramentas de
  captura, comparação e medida, é a linha de base; "ruído conhecido" é o que duas capturas do mesmo
  código já diferem.
- A tela mais estreita considerada é a de 375 px, como no inventário.
- O guia de implantação em produção é recomendação, não configuração versionada; atualizá-lo é a forma
  de "mudar a implantação" que esta feature exige.
