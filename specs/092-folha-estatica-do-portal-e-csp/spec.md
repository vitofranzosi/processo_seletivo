# Feature Specification: A folha do portal em arquivo, e o portal sob a política de segurança de conteúdo

**Feature Branch**: `claude/hungry-swirles-ac1f38`, sobre a branch do PR #308 (`091`) em `2615b738`,
ainda não mergeada em 18/10/2026

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: o passo do portal que a `091` deixou registrado (a decisão 007 e o R-007 de
`specs/091-folha-por-area-e-csp/`): levar a folha própria do portal do candidato, que viaja num
`<style>` de ≈ 67 KB em cada página, para arquivo estático; tirar o último atributo `style=""` do
portal; repontar e provar os guardiões que leem essa folha; e então passar o portal — e o protótipo do
painel de dúvidas, que serve a página do portal — do modo de observação ao modo de recusa da política
de segurança de conteúdo. Sem mudança visual, sem regra de negócio, sem dependência nova.

> **Faixa de identificadores.** Esta spec usa FR-2130 a FR-2145 e SC-820 a SC-826, acima da faixa
> reservada à `091` (FR-2090–2129, SC-810–819). Nenhum dos dois aparecia na `main` (`69c6ac1c`) nem
> na branch do PR #308 em 18/10/2026; o maior FR da `091` é FR-2116, o maior SC, SC-817.

---

## Por que esta feature existe

**O portal é a metade do sistema que ficou fora da barreira.** A `091` ligou a política que recusa
estilo e script embutidos sob `/gestao/`; no portal ela ficou em observação — o navegador acusa no
console o que recusaria, sem recusar —, porque o portal tem a folha inteira dentro do documento, e a
recusa o deixaria sem desenho (a decisão 007 da `091`). É o portal que o candidato abre, sem identificação
nenhuma na vitrine, e é nele que aparecem textos escritos por terceiros: o conteúdo publicado do
Edital, os nomes da lista de resultado, as instruções de cada documento.

**E a folha pesa em cada página.** Os ≈ 67 KB do `<style>` vão em toda resposta do portal, sem cache:
a vitrine, cada passo da inscrição, cada fragmento de página inteira. Na rede móvel de quem se inscreve
pelo celular, é o maior pedaço de cada página.

**O que não muda, e não se negocia aqui:** nenhum pixel de nenhuma tela do portal, impressa ou não;
nenhuma regra de negócio, permissão, endereço de tela, view, consulta ao banco, texto ou conteúdo
normativo. A folha não se reorganiza: sai do documento como está, na mesma ordem (D-001).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O candidato vê o mesmo portal, agora sob a barreira (Priority: P1)

A candidata abre a vitrine, entra na área, abre a inscrição em rascunho com a barra de documentos, o
acompanhamento, o comprovante e o resultado. Cada tela é idêntica à de ontem, a 1280 e a 375 px. Se
alguém conseguisse plantar um estilo ou um script num texto que o portal exibe, o navegador se
recusaria a aplicá-lo — como já recusa na gestão.

**Why this priority**: é a razão do passo — a barreira no canal do candidato —, com a condição de que
nada muda de aparência.

**Independent Test**: capturar as telas do portal antes e depois e comparar; ler as violações da
política de cada uma no navegador; ler o cabeçalho das respostas.

**Acceptance Scenarios**:

1. **Given** cada tela do inventário do portal, **When** capturada antes e depois a 1280 e a 375 px,
   **Then** as duas imagens só diferem no ruído conhecido, nenhuma estoura a largura e nenhuma muda de
   `status`.
2. **Given** a barra de documentos de um rascunho com nenhum, parte e todos os documentos enviados,
   **When** capturada antes e depois, **Then** a largura preenchida é a mesma.
3. **Given** uma resposta HTML do portal, **When** se lê o cabeçalho, **Then** ela traz a política em
   modo de recusa, e não em modo de observação.
4. **Given** qualquer tela do inventário do portal, **When** aberta no navegador, **Then** nenhuma
   violação da política é registrada.

---

### User Story 2 — Quem mantém o portal continua protegido pelos mesmos guardiões (Priority: P1)

O desenvolvedor acrescenta, por engano, uma largura em pixels na folha do portal, uma regra que
esconde o foco, ou uma classe sem regra. Os testes que reprovavam o engano quando a folha estava no
modelo continuam reprovando com ela num arquivo estático. E quem escreve um `<style>` ou um
`style=""` num modelo do portal vê um teste reprovar antes de o navegador recusar.

**Why this priority**: a `089` e a `091` mostraram que mover a folha deixa afirmações negativas
passando sem examinar nada; aqui se move a folha do outro canal.

**Independent Test**: para cada guardião que lê a folha do portal, plantar no arquivo novo uma
violação da regra dele e ver o teste reprovar.

**Acceptance Scenarios**:

1. **Given** cada guardião que lia a folha do portal no modelo ou na página, **When** uma violação é
   plantada no arquivo estático, **Then** ele reprova.
2. **Given** um modelo do portal, **When** ganha um `<style>` ou um `style=""`, **Then** um guardião
   reprova.

---

### User Story 3 — O protótipo do painel e as páginas fora das duas áreas (Priority: P2)

A pessoa do piloto abre o protótipo do painel de dúvidas, que é a página pública da seleção servida
pela gestão, e a vê como hoje, agora sob a mesma recusa da gestão. Quem cai num endereço inexistente
fora da gestão e do portal vê a página de erro de hoje, também sob a recusa.

**Why this priority**: o protótipo era a exceção que a `091` precisou abrir na gestão; com o portal em
recusa, a exceção deixa de ter motivo.

**Independent Test**: capturar o protótipo e as páginas de erro antes e depois; ler o cabeçalho.

**Acceptance Scenarios**:

1. **Given** o protótipo do painel, **When** capturado antes e depois, **Then** só difere no ruído
   conhecido, e a resposta traz a política em recusa, sem violação no navegador.
2. **Given** um endereço inexistente fora de `/gestao/` e de `/selecoes/`, **When** a página de erro é
   servida, **Then** ela traz a política em recusa.

### Edge Cases

- **A folha não carrega.** O arquivo é conferido pela verificação de sistema da `089` antes de o
  serviço atender alguém; um arquivo citado e ausente é erro, e não `<link>` quebrado em silêncio.
- **Grafia que um guardião acusa.** A folha tem regras terminadas em `%}` e uma linha com `}}`; dentro
  do modelo elas passavam, num arquivo estático o guardião de sintaxe de modelo vazada as acusa (R-007
  da `091`). Ganham `;` antes da chave, ou a chave na linha seguinte — o navegador lê igual.
- **Barra de documentos sem documento obrigatório.** O percentual é 0, e a classe existe.
- **A página impressa.** O comprovante é salvo em PDF pelo navegador; as regras de impressão continuam
  valendo no papel como antes.
- **A página de falha de CSRF do framework.** Traz estilo embutido; em recusa ela aparece sem desenho,
  legível, como já acontece sob a gestão desde a `091`. Registrada, e não resolvida aqui.
- **O fragmento do htmx no portal.** A barra de documentos volta como fragmento a cada envio; ela leva
  a classe do percentual como a página inteira.
- **Página de depuração do servidor local.** Continua fora da política, e só ela (a decisão 010 da `091`).

## Requirements *(mandatory)*

### Functional Requirements

#### A folha do portal em arquivo

- **FR-2130**: A folha própria do portal MUST passar do documento a um arquivo estático, carregado
  pela base do portal depois dos tokens, com a versão do conteúdo no endereço, como as folhas da gestão.
- **FR-2131**: As regras MUST ir na mesma ordem, com o mesmo seletor, as mesmas declarações e a mesma
  condição de mídia; só MAY mudar a grafia que o navegador lê igual — `;` antes de `}` e a quebra de
  linha entre duas chaves —, e cada mudança MUST ser listada na pesquisa.
- **FR-2132**: Os comentários da folha MUST acompanhar as regras que explicam, como comentário de CSS.
- **FR-2133**: A verificação de sistema MUST conferir o arquivo antes de o serviço atender alguém.
- **FR-2134**: Nenhum modelo do portal MUST conter `<style>` nem atributo `style`.
- **FR-2135**: A largura da barra de documentos MUST vir de uma classe por percentual inteiro de 0 a
  100, com o mesmo valor aplicado que o atributo dava, na página inteira e no fragmento.

#### A política no portal

- **FR-2136**: Toda resposta HTML do sistema MUST trazer a política em modo de recusa — a gestão, o
  portal, a página pública da seleção e a página de erro fora das duas áreas (D-003).
- **FR-2137**: O modo de observação MUST deixar de existir: nenhuma resposta MUST trazer o cabeçalho de
  observação, e o protótipo do painel de dúvidas MUST receber a recusa como qualquer página sob a
  gestão.
- **FR-2138**: As exceções da `091` MUST continuar: a página de depuração do framework com `DEBUG`, e
  a resposta que não é HTML, ficam sem cabeçalho; a resposta que já traz política fica como está.

#### Os guardiões

- **FR-2139**: Todo teste que lia a folha do portal no texto do modelo ou na página renderizada MUST
  passar a ler o arquivo estático, ou a folha que a página aplica; nenhum MUST ficar mais fraco, e cada
  um MUST ser provado por mutação no arquivo novo.
- **FR-2140**: O arquivo novo MUST ser varrido pelo guardião de sintaxe de modelo da `089`.
- **FR-2141**: Os guardiões de estilo embutido da `091` MUST alcançar os modelos do portal.

#### O que não pode piorar

- **FR-2142**: Nenhuma tela do inventário do portal, nem o protótipo do painel, nem as bases da `089`
  MUST mudar de aparência além do ruído conhecido, deixar de carregar, mudar de `status` ou passar a
  estourar a 375 ou a 1280 px.
- **FR-2143**: As regras de impressão do portal MUST continuar valendo no papel como antes.
- **FR-2144**: A pesquisa MUST registrar o tamanho da resposta HTML de telas do portal antes e depois.
- **FR-2145**: Nenhuma regra de negócio, permissão, endereço, view, consulta ou texto MUST mudar.

### Key Entities

Nenhuma. Só apresentação, entrega de arquivo estático e um cabeçalho de resposta.

## Decisões

### D-001 — Um arquivo, e não um por área

A `091` dividiu a folha da gestão por área porque ela tinha 1.471 linhas em ordem de chegada, com
regras repetidas, e a divisão pedia a prova de ordem inteira do R-003 dela. A do portal não foi pedida
dividida, e dividir a obrigaria à mesma prova sem ganho para quem pediu: o motivo do passo é a
política, e a política só precisa da folha fora do documento. A folha vai a um arquivo só,
`portal/static/portal/portal.css`, na ordem de hoje. Dividi-la é um passo possível, registrado.

### D-002 — O mesmo texto, salvo a grafia que o guardião acusa

Mover sem reescrever é o que torna a prova barata: as regras que o navegador lê antes e depois são as
mesmas, na mesma ordem, e a comparação regra a regra (`estilos.py`) dá o mesmo resultado. As únicas
mudanças são as de grafia que o guardião de sintaxe de modelo vazada acusaria num arquivo estático
(`%}` e `}}`), resolvidas como a `091` resolveu as da visão geral.

### D-003 — Recusa em todo HTML, e não só sob `/selecoes/`

A `091` decidia pelo caminho: recusa sob `/gestao/`, observação no resto. Acrescentar `/selecoes/` à
lista deixaria em observação o que não é nem gestão nem portal — hoje, só a página de erro de um
endereço inexistente na raiz, que já não tem estilo embutido. Toda área nova nasceria em observação, e
alguém precisaria lembrar de incluí-la: é o contrário de negar por padrão. Com o portal fora do
documento, não sobra HTML do sistema com estilo embutido; a política vale em recusa para toda resposta
HTML, e o modo de observação sai, com a marca que o protótipo usava. As exceções da `091` ficam:
depuração com `DEBUG`, resposta que não é HTML, e resposta que já declara a sua.

### D-004 — A barra de documentos pela classe de percentual, no arquivo do portal

A `091` deu às duas medidas calculadas da gestão uma classe por valor inteiro, de 0 a 100 (a decisão
005 dela). A barra do portal é a terceira, e o valor vem do mesmo `widthratio`, que dá inteiro de 0 a 100
— `recebidos` nunca passa de `total`, e com `total` zero ele dá 0. As classes vão no arquivo do portal,
e não reaproveitam as de Minhas Etapas: o portal não carrega folha da gestão, e não deve carregar.

## Success Criteria *(mandatory)*

- **SC-820**: Refeito o inventário do portal, **zero** variantes diferem pixel a pixel além do ruído
  conhecido, **zero** estouram, **nenhuma** muda de `status`; o mesmo nas bases da `089` e no
  protótipo do painel; e as regras aplicadas, como conjunto, são as mesmas em todas.
- **SC-821**: **Zero** `<style>` e **zero** atributos `style` em todos os modelos do sistema.
- **SC-822**: Abertas no navegador todas as telas do inventário do portal, as bases e o protótipo, o
  console registra **zero** violações da política, com ela em recusa.
- **SC-823**: **Todos** os guardiões que liam a folha do portal reprovam diante de uma violação
  plantada no arquivo novo, um a um.
- **SC-824**: A suíte contra PostgreSQL continua sem falhas.
- **SC-825**: Cada resposta HTML de página inteira do portal diminui pelo menos 60 KB — a folha que
  deixou de viajar nela.
- **SC-826**: **Nenhuma** resposta HTML do sistema traz o cabeçalho de observação.

## Assumptions

- A base é a branch do PR #308 (`091`), ainda aberto: sem ela não há política, folha por área nem a
  tag `estatico` nas condições que este passo usa. Se o PR #308 mudar antes do merge, esta branch se
  atualiza a partir dele.
- O inventário do portal é feito pelas rotas que se alcançam seguindo os links da vitrine e da área de
  seis candidatas do seed do inventário, mais três rascunhos preparados para mostrar a barra de
  documentos em 0%, 50% e 100%; a lista sai da passada de antes e é reusada na de depois.
- "Ruído conhecido" é o que duas capturas do mesmo código, em bancos copiados do mesmo modelo, já
  diferem.
- A página de falha de CSRF do framework sem desenho em recusa é aceitável, como a `091` aceitou sob a
  gestão; trocá-la por uma página do sistema é passo possível.
