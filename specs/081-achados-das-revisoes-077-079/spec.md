# Feature Specification: Os achados das revisões da 077 e da 079

**Feature Branch**: `claude/achados-077-079-b4f1f5`, sobre a `main` em `cf6d7372`, que traz da `075` à
`080`

**Created**: 2026-10-17

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: os achados que as revisões da [`077`](../077-telas-de-uso-diario/spec.md) e da
[`079`](../079-telas-da-presidencia/spec.md) registraram e não corrigiram. Incremento pequeno, sem tela
nova: cada achado sai daqui com destino explícito — corrigido, com requisito e teste, ou registrado
como decisão, com o motivo. A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito em 17/10/2026
sobre `cf6d7372`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec abre em FR-1820 e SC-710, acima da faixa da `080`
> (FR-1811, SC-705), medida em todas as worktrees e branches em 17/10/2026.

---

## Por que esta feature existe

**Na Distribuição, as duas ações sobre a seleção pesam o mesmo, e só uma delas se desfaz.** Abaixo da
tabela das inscrições, "Distribuir as selecionadas" e "Consolidar as selecionadas" são dois botões
cheios, lado a lado, sobre as mesmas caixas marcadas. Distribuir é rotina — a atribuição se retira na
mesma tela. Consolidar começa o ato que transforma avaliações em Resultado da Etapa, que é imutável. A
frase antes deles diz isso (`FR-422` da `030`), mas o desenho diz o contrário: que são duas ações da
mesma natureza. No detalhe do Processo, os atos que não se desfazem já têm outro desenho — o
secundário, com a marca "irreversível" ao lado.

**Na Alocação, o aviso chama o ato pelo nome da tela vizinha.** Sem presidência designada, a tela diz
"Designe a presidência antes de distribuir." A tela é a Alocação por Etapa; distribuir é o que se faz
na Distribuição, a tela seguinte. A `079` trocou o botão de "Salvar distribuição" para "Salvar
alocação" pela mesma razão (R-004 da `079`) e deixou o aviso, porque um teste o guardava como frase.

**Três módulos de teste importam uma fixture de um quarto.** Os testes da `077`, da `079` e da `080`
trazem o `cenario` do módulo de acessibilidade da `012`, com um `noqa` no import e outro em cada uso,
porque o parâmetro da função sombreia o nome importado. A suíte já tem a regra escrita (em
`tests/fixtures/corte.py`): a função mora no apoio comum, e cada módulo declara a fixture dele.

**Os outros sete achados não pedem código novo aqui** — três já foram corrigidos por incrementos
seguintes, dois contrariam requisito escrito, e dois pedem ferramenta que o projeto não tem ou não
quer mudar. Cada um tem a sua decisão abaixo, com o motivo.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel ou
fluxo. Nenhum endereço, nenhuma view, nenhuma mensagem de domínio. Nenhum rótulo de ação. Nenhuma
dependência nova. Nenhuma tela fora da Distribuição e da Alocação.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O que não se desfaz não pesa como a rotina (Priority: P1)

A presidente marca três inscrições na Distribuição. Abaixo da tabela, "Distribuir as selecionadas" é o
botão cheio; "Consolidar as selecionadas" vem ao lado com o desenho secundário — contornado, da mesma
altura — e, junto dele, a marca "irreversível". A frase que explica a consolidação continua antes dos
dois.

**Why this priority**: é o único achado com risco de ato errado. O clique leva à conferência, e não ao
ato; mas é o desenho do botão que diz, antes da conferência, que este caminho não tem volta.

**Independent Test**: na Distribuição com inscrições, "Distribuir as selecionadas" tem o desenho de
ação principal; "Consolidar as selecionadas" tem o desenho secundário e a marca "irreversível" logo
depois; a frase da `FR-422` da `030` continua antes dos dois; o destino, o nome e o valor do botão não
mudam.

**Acceptance Scenarios**:

1. **Given** a Distribuição de uma Etapa com inscrições, **When** a página abre, **Then** "Consolidar
   as selecionadas" tem o desenho secundário, com a mesma altura de "Distribuir as selecionadas", e a
   marca "irreversível" logo depois dele.
2. **Given** a mesma tela, **When** a presidente aperta "Consolidar as selecionadas", **Then** a
   conferência de dois passos abre como antes.
3. **Given** a Distribuição a 375 px, **When** a página abre, **Then** os dois botões e a marca cabem
   na largura, quebrando a linha se preciso.
4. **Given** a Distribuição com inscrições prontas, **When** a página abre, **Then** "Consolidar as N
   prontas" tem o mesmo desenho e a mesma marca, e nenhum botão cheio leva à consolidação.
5. **Given** o leitor de tela, **When** o foco chega a uma das duas consolidações, **Then** ele anuncia
   "irreversível" junto do rótulo.

---

### User Story 2 — A Alocação diz alocar (Priority: P2)

O gestor abre a Alocação por Etapa de um Processo cuja comissão ainda não tem presidência. O aviso diz
"Designe a presidência antes de alocar." e o link "Ir para a Comissão" continua ao lado.

**Why this priority**: microcópia; fecha a divergência que a `079` corrigiu só no botão.

**Independent Test**: na Alocação sem presidência, o aviso usa "alocar" e não "distribuir"; o papel
`status`, o link e a condição não mudam.

**Acceptance Scenarios**:

1. **Given** a Alocação de um Processo sem presidência, **When** a página abre, **Then** o aviso diz
   "Designe a presidência antes de alocar." e nenhum texto visível da tela diz "antes de distribuir".
2. **Given** a Alocação com presidência, **When** a página abre, **Then** não há aviso, como antes.

---

### User Story 3 — Uma fixture, um dono (Priority: P3)

Quem mantém a suíte muda o cenário da presidência num lugar só, a montagem no apoio comum dos
testes; cada módulo que o usa declara a própria fixture, nenhum o importa de outro módulo de teste,
e nenhum `noqa` esconde o nome sombreado.

**Why this priority**: não muda nada que alguém veja na tela; tira um acoplamento entre módulos de
teste que quebraria em silêncio quem mexesse no módulo da `012`.

**Independent Test**: um guardião varre os módulos de teste da interface e falha se algum importar o
`cenario`; os testes que o usam passam sem mudança de corpo.

**Acceptance Scenarios**:

1. **Given** os módulos de teste da interface, **When** o guardião os lê, **Then** nenhum importa o
   `cenario` de outro módulo.
2. **Given** os testes da `012`, da `077`, da `079` e da `080`, **When** a suíte roda, **Then** eles
   recebem o mesmo cenário de antes.

### Edge Cases

- **A marca no celular.** A 375 px, a linha das ações sobre a seleção quebra; a marca acompanha o
  botão que ela qualifica e não estica até a altura dele.
- **A marca para quem não a vê.** Quem chega ao botão pelo teclado ou pelo leitor de tela ouve a
  marca junto do rótulo, no foco (`FR-1827`), e não só ao percorrer a página linha a linha.
- **Distribuição sem inscrição.** Sem linhas, a tabela e os dois botões não aparecem, como antes.
- **"Consolidar as N prontas".** O botão da consolidação de todas as prontas, mais acima, está sozinho
  no formulário dele e leva à mesma conferência; tem o mesmo desenho e a mesma marca do de baixo
  (`FR-1828`), porque é o mesmo ato (D-006, emendada na revisão do PR).
- **A recusa do domínio.** Quem enviar a alocação à mão, sem presidência, recebe a recusa do domínio,
  que diz "antes de distribuir trabalho" e não muda (D-007).
- **Impressão.** A barra e o cabeçalho de contexto continuam fora do papel (`076`; D-002).
  *Substituído pela [`088`](../088-decisoes-da-etapa-4/spec.md) em 18/10/2026, por decisão do
  usuário*: a trilha do cabeçalho de contexto sai no papel; ficam fora só a barra e "Trocar
  identidade".

## Requirements *(mandatory)*

### Functional Requirements

#### As ações sobre a seleção, na Distribuição

- **FR-1820**: Na Distribuição, "Consolidar as selecionadas" MUST ter o desenho secundário — o mesmo
  dos atos que não se desfazem no detalhe do Processo —, com a altura de "Distribuir as selecionadas",
  e MUST ser seguido da marca "irreversível". "Distribuir as selecionadas" MUST continuar com o desenho
  de ação principal.
- **FR-1821**: O rótulo, o destino, o nome, o valor e o lugar de "Consolidar as selecionadas" MUST
  continuar os mesmos, e a frase que explica a consolidação (`FR-422` da `030`) MUST continuar antes
  dos dois botões. "Retirar as selecionadas" e as demais ações da tela MUST continuar com o desenho de
  antes, exceto "Consolidar as N prontas" (`FR-1828`).
- **FR-1827**: A marca "irreversível" MUST descrever o botão que qualifica para a tecnologia
  assistiva: quem chega a ele pelo teclado ou pelo leitor de tela MUST ouvir "irreversível" junto do
  rótulo. *Emenda da revisão do PR, 18/10/2026.*
- **FR-1828**: "Consolidar as N prontas" (e "Consolidar a inscrição pronta") MUST ter o mesmo desenho
  e a mesma marca de "Consolidar as selecionadas" — nenhum botão cheio da Distribuição MUST levar à
  consolidação —, com o mesmo rótulo, destino e lugar. *Emenda da revisão do PR, 18/10/2026.*

#### A microcópia da Alocação

- **FR-1822**: Na Alocação por Etapa sem presidência, o aviso MUST dizer "Designe a presidência antes
  de alocar.", com o mesmo papel para o leitor de tela, o mesmo link para a Comissão e a mesma
  condição.

#### O apoio dos testes

- **FR-1823**: O cenário da presidência usado pelos testes da `012`, da `077`, da `079` e da `080` MUST
  ter uma montagem só, no apoio comum dos testes, composta sobre a banca que o apoio já monta, com
  código e chaves derivados do `seed`; e nenhum módulo de teste MUST importar a fixture dele de outro
  módulo de teste — de nenhum dos módulos que a declaram.
- **FR-1824**: Toda tela que sobrescreve a trilha do cabeçalho de contexto MUST abri-la com a mesma
  navegação nomeada — o mesmo rótulo e a mesma classe —, verificada por guardião em todos os
  templates, e não só nos que os testes de tela abrem.

#### O que não pode piorar

- **FR-1825**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só a Distribuição
  MUST mudar de largura ou de altura (a Alocação do inventário tem presidência, e o aviso não aparece).
- **FR-1826**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  folha que já varrem a gestão — toda classe com regra na folha, todo botão de envio com classe — e
  pelo teto de tamanho da Distribuição.

### Key Entities

Nenhuma. Só apresentação, microcópia e apoio de teste.

## Decisões

O destino de cada um dos dez achados, na ordem em que foram registrados.

| Achado | Origem | Destino |
|---|---|---|
| Landmark de trilha sem link na lista e em Minhas Etapas | revisão do PR da `077` | D-001 — não corrigido, contraria a `FR-1746` |
| A trilha da Mesa não sai na impressão | revisão do PR da `077` | D-002 — não corrigido, contraria caso-limite escrito |
| Fixture `cenario` importada de outro módulo | revisão do PR da `077` | corrigido — `FR-1823` |
| Abertura da trilha copiada nos templates | revisão do PR da `077` | em parte pela `078`; o resto, guardião — `FR-1824`, D-003 |
| Correção geral na folha comum | revisão do PR da `077` | D-004 — já corrigido pela `078` |
| O teste das correções confere texto, não largura | revisão do PR da `077` | D-005 — não corrigido, pede navegador no CI |
| Dois botões cheios sobre a seleção, um irreversível | pesquisa da `079` | corrigido — `FR-1820`, `FR-1821`, `FR-1827`, `FR-1828`; D-006 |
| O aviso "antes de distribuir" da Alocação | pesquisa da `079` | corrigido — `FR-1822`; D-007 |
| As filhas da Distribuição com a trilha no conteúdo | pesquisa da `079` | D-008 — já corrigido pela `080` |
| O `comparar.py` não compara altura | pesquisa da `079` | D-009 — fica, o `medidas.py` cobre |

### D-001 — O landmark da trilha na lista e em Minhas Etapas fica

Na lista de Processos e em Minhas Etapas, a trilha do cabeçalho é uma navegação nomeada sem nenhum
link: o produto, em texto, e a própria tela. A revisão da `077` apontou que quem pula por landmarks
encontra uma região de navegação que não leva a lugar nenhum. Corrigir pede uma de duas coisas: tirar
a navegação nomeada dessas duas telas — o que a `FR-1746` da `077` exige ("como navegação nomeada")
nas quatro telas dela —, ou dar ao produto um destino, que nenhuma spec definiu e que, para quem só
avalia, não pode ser a lista. As duas são decisão de produto. **Pergunta ao usuário.**

*Respondida em 18/10/2026*: o usuário decidiu que o landmark fica até haver autenticação; a
[`088`](../088-decisoes-da-etapa-4/spec.md) registra a decisão, sem código.

### D-002 — A trilha continua fora do papel

O cabeçalho de contexto não sai na impressão (`076`). Desde a `077`, a trilha mora nele, e a da Etapa
e da inscrição da Mesa deixou de ser impressa — e, depois da `078` à `080`, a de outros treze templates.
A `077` aceitou a perda por escrito, no caso-limite "Impressão", e a `076` também ("A barra e o caminho
não saem no papel"). Imprimir a trilha reabre essas duas decisões, para todas as telas de uma vez. É
decisão de produto. **Pergunta ao usuário.**

*Respondida em 18/10/2026*: o usuário aprovou imprimir a trilha, e a
[`088`](../088-decisoes-da-etapa-4/spec.md) o executa.

### D-003 — A abertura da trilha continua escrita em cada tela, e um guardião a confere

A `078` tirou das telas a parte mais frágil da abertura — a sigla e o nome do produto, que hoje vêm de
um parcial com guardião (`test_o_produto_da_trilha_tem_uma_fonte_so`). Resta a navegação em volta, com
o rótulo e a classe, em dezessete templates. Um parcial do Django não envolve conteúdo, e um bloco
interno no `base.html` pediria editar as dezessete telas de uma vez — o oposto do incremento pequeno — ou
uma tag de template nova, que é código Python fora do escopo. O defeito que a revisão descreveu é
esquecer uma tela ao trocar o rótulo ou a classe; o guardião da `FR-1824` faz esse esquecimento
reprovar a suíte.

### D-004 — A correção geral na folha comum já foi feita

A `077` corrigiu tela a tela os estouros cuja causa era comum — a moldura que rola sem posição, com um
elemento absoluto dentro, e o `fieldset` que não encolhe —, e a revisão apontou a causa latente. A
`078` levou as duas regras à folha comum e retirou as três pontuais (`FR-1760` a `FR-1762` da `078`).
Nada a fazer aqui.

### D-005 — O teste das correções continua conferindo o texto

`test_cada_correcao_vale_so_na_sua_tela` confere que a regra está na folha da tela, e não que a página
cabe em 375 px. Provar largura pede um motor de layout no CI — um navegador, que é dependência nova —,
e o projeto prova largura pelo inventário visual, refeito a cada incremento e guardado no repositório.
Depois da `078`, o teste cobre uma regra só, a do sorteio. Fica como está.

### D-006 — "Consolidar as N prontas" tem o desenho de "Consolidar as selecionadas"

*Emendada na revisão do PR, em 18/10/2026.* A primeira versão deixava este botão com o desenho de ação
principal: ele está sozinho no formulário dele e leva à mesma conferência de dois passos, e a regra da
`080` (a decisão 005 da `080`) admite o desenho principal para o que leva à conferência. A revisão
apontou o custo: o mesmo ato passava a ter dois desenhos na mesma página — cheio e sem aviso no alto,
contornado e marcado embaixo —, e o desenho dizia que a consolidação em lote era menos grave que a da
seleção. Os dois têm agora o desenho secundário e a marca (`FR-1828`). A decisão da `080` continua
valendo para as telas dela; o ato irreversível, na conferência, não muda aqui.

### D-007 — A recusa do domínio continua dizendo "distribuir trabalho"

A camada de aplicação recusa a alocação sem presidência com "Designe a presidência antes de
distribuir trabalho.". É mensagem de domínio, devolvida também pela API, e o escopo deste incremento é
apresentação. Na tela, ela só aparece para quem enviar o formulário à mão: o botão não existe sem
presidência (`FR-1790` da `079`). Fica registrada.

### D-008 — As filhas da Distribuição já têm a trilha no cabeçalho

Corrigido pela `080` (`FR-1800` a `FR-1802` da `080`). Nada a fazer aqui.

### D-009 — O `comparar.py` continua sem altura

A própria `079` escreveu o `medidas.py`, que compara largura, altura, título e `h1` variante a
variante, e deixou o `comparar.py` como estava porque outras features citam a saída dele. A `080` e
esta usam os dois. Fica como está.

## Success Criteria *(mandatory)*

- **SC-710**: Dos dez achados registrados nas revisões da `077` e da `079`, **dez** têm destino escrito
  nesta spec — corrigido, com requisito e teste, ou decisão, com motivo.
- **SC-711**: Na Distribuição, os botões cheios sobre a seleção passam de **dois** para **um**, os
  botões cheios que levam à consolidação passam de **dois** para **zero**, e as duas consolidações
  passam a ter a marca "irreversível", anunciada com o botão.
- **SC-712**: Na Alocação, os textos visíveis que chamam o ato da tela de "distribuir" passam de
  **um** para **zero**.
- **SC-713**: Os módulos de teste que importam o `cenario` de outro módulo passam de **três** para
  **zero**.
- **SC-714**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, **nenhuma**
  muda de `status`, e só a Distribuição muda de medida, nos dois estados da barra.
- **SC-715**: A suíte contra PostgreSQL continua sem falhas.

## Assumptions

- Os "seis achados da revisão" da `077` são os seis marcados como não corrigidos no relatório da revisão
  do PR 292; os outros dois da mesma revisão — a Etapa aberta pela gestão e a `FR-1713` da `076` —
  foram corrigidos na própria `077`.
- Os achados da `079` são os quatro da seção "Achados registrados, fora do escopo" da pesquisa dela.
- O desenho secundário e a marca "irreversível" são os que o detalhe do Processo já usa nos atos que
  não se desfazem; nenhum desenho novo é criado.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
