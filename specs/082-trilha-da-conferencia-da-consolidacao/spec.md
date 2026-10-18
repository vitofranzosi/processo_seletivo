# Feature Specification: A trilha da conferência da consolidação no cabeçalho de contexto

**Feature Branch**: `claude/interesting-sammet-da84d5`, sobre a `main` em `cf6d7372`, que traz da `075`
à `080`

**Created**: 2026-10-17

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: achado da [`081`](../081-achados-das-revisoes-077-079/spec.md), registrado na pesquisa dela
(PR 298, ainda aberto em 17/10/2026): "a conferência da consolidação ainda tem a trilha no conteúdo".
É a tela que "Consolidar as selecionadas" e "Consolidar as N prontas" abrem a partir da Distribuição
de uma Etapa — a declaração do alcance, antes do ato. A [`080`](../080-telas-filhas-da-distribuicao/spec.md)
levou ao cabeçalho a trilha das outras telas que se abrem dali, e esta ficou de fora: é a resposta a
um envio, não está no inventário visual, e a `080` não a listou entre as filhas.

> **Faixa de identificadores.** Esta spec abre em FR-1840 e SC-720, acima da faixa da `081` (PR 298),
> medida com quatro dígitos na `main` e nos PRs abertos em 17/10/2026.

---

## Por que esta feature existe

**Na conferência do maior ato da Etapa, o caminho volta para dentro do conteúdo.** Desde a `080`, a
Distribuição e as seis telas que se abrem dela dizem no cabeçalho *GPS › Processos Seletivos ›
PS-DEMO-2026 › Alocação por Etapa › Prova objetiva*, com a tela no fim. Ao apertar "Consolidar as
selecionadas", a presidência chega à conferência e o cabeçalho volta a dizer só *GPS › Processos
Seletivos*; o caminho reaparece numa segunda linha, no conteúdo, e reaparece mais curto:
*Processos Seletivos › Prova objetiva › Conferir*, sem o Processo nem a Alocação por Etapa. **Medido
em 17/10/2026**: das sete telas que se abrem da Distribuição, só esta não leva ao Processo nem à
Alocação pela trilha, e só esta diz o caminho no conteúdo.

**É a conferência da retirada com outro ato.** As duas são a página que declara o alcance antes de um
ato que não se desfaz, as duas se abrem por um botão da Distribuição e voltam a ela por "Cancelar e
voltar". Desde a `080`, a da retirada termina em *Prova objetiva › Conferir* no cabeçalho; a da
consolidação, não.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel —
presidir é vínculo com a comissão, e não papel — ou fluxo. Nenhum endereço, nenhuma view, nenhum
conteúdo normativo. O botão que consolida continua com o rótulo, o desenho de perigo, o lugar e as
frases que o precedem; o alcance declarado, a tabela, o que fica de fora e "Cancelar e voltar" não
mudam. Nenhuma tela fora desta.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, também antes de consolidar (Priority: P1)

A presidente marca três inscrições prontas na Distribuição da Prova objetiva e aperta "Consolidar as
selecionadas". No topo, o cabeçalho diz *GPS › Processos Seletivos › PS-DEMO-2026 › Alocação por
Etapa › Prova objetiva › Conferir* — a trilha da Distribuição, com "Conferir" no fim —, e cada nível
acima leva a ele. O conteúdo começa por "Confira antes de consolidar". O mesmo quando ela chega por
"Consolidar as N prontas".

**Why this priority**: é o que a `080` fez nas outras seis telas que se abrem da Distribuição; sem
isso, o fluxo da presidência perde o caminho justamente na tela do ato que não se desfaz.

**Independent Test**: na conferência, aberta pela seleção e pelo alcance de todas as prontas, o
caminho está no cabeçalho de contexto, com um link por nível acima da tela e "Conferir" como página
atual; o conteúdo não tem trilha; a página tem uma trilha só; nada foi consolidado.

**Acceptance Scenarios**:

1. **Given** a Distribuição de uma Etapa e inscrições selecionadas, **When** a presidência aperta
   "Consolidar as selecionadas", **Then** o cabeçalho mostra *GPS › Processos Seletivos › código do
   Processo › Alocação por Etapa › nome da Etapa › Conferir*, com os quatro níveis do meio como links,
   e o conteúdo começa pelo título.
2. **Given** a Distribuição de uma Etapa com inscrições prontas, **When** a presidência aperta
   "Consolidar as N prontas", **Then** a trilha é a mesma.
3. **Given** a conferência aberta, **When** a presidência lê o alcance, **Then** o título, a linha da
   Etapa e do Edital, a explicação do ato, o que será consolidado, o que ficará de fora, o botão que
   consolida e "Cancelar e voltar" são os de antes, na mesma ordem.

### Edge Cases

- **Nada a consolidar.** Quando nenhuma das selecionadas está em condição, a tela continua sem o
  botão, com a frase que diz por quê e "Cancelar e voltar"; só a trilha sobe.
- **Pedido recusado antes da conferência.** Seleção vazia ou Etapa bloqueada continuam voltando à
  Distribuição com a mensagem lá; não há conferência, e portanto não há trilha nova.
- **Trilha longa no celular.** São seis níveis, e o nome da Etapa pode ser longo. A 375 px a trilha
  quebra a linha dentro do cabeçalho; nem ela nem "Trocar identidade" estouram a largura, e a tabela
  do alcance continua rolando dentro da própria moldura.
- **Quem não preside.** A porta é a da gestão da comissão, como antes: quem não preside recebe a
  resposta uniforme e nunca vê a conferência. A trilha não concede nem esconde acesso.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando a Etapa e o Edital.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1840**: Na conferência da consolidação, o cabeçalho de contexto MUST mostrar a trilha da tela,
  como navegação nomeada, com a mesma abertura das telas da `077` à `080`: o produto, cada nível acima
  da tela como link, e a própria tela como a página atual (`FR-1800` da `080`).
- **FR-1841**: Os níveis acima da tela MUST ser os da trilha da Distribuição — Processos Seletivos, o
  Processo, a Alocação por Etapa e a Etapa —, e o rótulo da página atual MUST ser "Conferir", o que a
  tela já mostrava, como na conferência da retirada.
- **FR-1842**: A trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma trilha só, e o
  conteúdo MUST começar pelo título.
- **FR-1843**: A trilha MUST ser a mesma quando a conferência se abre pela seleção e quando se abre
  pelo alcance de todas as prontas.
- **FR-1844**: O botão que consolida MUST continuar com o rótulo, o desenho de perigo, o lugar e as
  frases que o precedem, e MUST NOT ganhar o desenho de ação principal; o alcance declarado, o que
  fica de fora e "Cancelar e voltar" MUST continuar os mesmos. Abrir a conferência MUST NOT consolidar
  nada.
- **FR-1845**: A 375 e a 1280 px, a trilha do cabeçalho MUST caber na largura, quebrando a linha
  quando precisar, e "Trocar identidade" MUST continuar alcançável; a página MUST passar pelos
  guardiões de acessibilidade, larguras e folha que já varrem a gestão.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — A trilha é a da Distribuição, com "Conferir" no fim

A mesma regra que a `080` deu às filhas (a decisão 001 da `080`): a trilha de uma tela que se abre da
Distribuição é a da Distribuição, com a tela no fim. "Conferir" é o rótulo que a tela já usava, e o
que a conferência da retirada e a da inclusão na comissão usam.

### D-002 — Nada além da trilha

A conferência poderia ganhar outras coisas que as filhas ganharam na `080` — mas nenhuma se aplica:
ela não tem mensagens de um envio anterior (o erro do pedido volta à Distribuição), não tem filtro, e
já tem título por região ("O que será consolidado", "O que ficará de fora"). O botão que consolida
fica como está, pelo pedido; a `081` decidiu o desenho dos dois botões que abrem esta tela, e não o
do que confirma.

## Success Criteria *(mandatory)*

- **SC-720**: Na conferência, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto,
  e cada nível acima da tela está a **um** clique.
- **SC-721**: Das sete telas que se abrem da Distribuição, as que levam ao Processo e à Alocação por
  Etapa pela trilha passam de **seis** para **sete**.
- **SC-722**: A 375 e a 1280 px, a conferência **não** estoura a largura, aberta pela seleção e pelo
  alcance de todas as prontas.
- **SC-723**: A suíte contra PostgreSQL continua sem falhas.

## Assumptions

- A conferência não está no inventário visual: ela é a resposta a um envio, e o inventário só abre
  telas pelo endereço. É provada pelos testes e no navegador, como a conferência da retirada na `080`;
  as telas do inventário não mudam, porque nenhum outro template é tocado.
- O guardião da abertura da trilha que a `081` traz (`test_toda_trilha_do_cabecalho_abre_com_a_mesma_navegacao`)
  varre todos os templates; quando o PR 298 entrar, ele alcança esta tela também, e ela já tem a
  abertura que ele confere. Os identificadores da `081` não são citados aqui: até o merge, eles não
  existem na `main`, e a varredura de citações reprovaria.
- O produto no começo da trilha é a sigla GPS, como da `076` à `080`.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
