# Feature Specification: Polish — os resíduos dos três lotes

**Feature Branch**: `claude/residuos-polish-c7ef91`

**Created**: 2026-10-01

**Status**: Draft

**Input**: o prompt de sessão autônoma `doc/prompt/058-polish-residuos.md`, escrito em 01/10/2026 a
partir da reavaliação do polish (`doc/reavaliacao-polish-ui-2026-10-01.md`). É o fecho da série da
auditoria de polish de 30/09, depois da `055` (folha e componentes), da `056` (assistente de
composição) e da `057` (telas de operação), as três já na `main`.

> **Faixa de identificadores.** Abre em **FR-1069**, **SC-411** e **UX-143**. O teto medido em
> 01/10/2026 em todas as worktrees, com quatro dígitos, era FR-1068, SC-410 e UX-142 — todos da
> `057`, já mergeada. As decisões desta spec nascem em `D-001` e moram no [research.md](research.md);
> as dez decisões que o prompt trouxe fechadas (1ª a 10ª) são **entrada**, e o research as
> registra como "decisões recebidas" (1ª a 10ª) sem reaproveitar a numeração delas.

**A frase que governa:**

> O que já foi decidido para uma tela vale para a tela vizinha que ficou de fora, e nenhuma ação fica
> fora de alcance em tela estreita.

**E a frase que mantém o corte:**

> Só os resíduos listados na reavaliação. Nada de auditoria nova, nada de padrão novo: cada item
> reaplica uma decisão que já está na `main`.

---

## Por que esta feature existe

A reavaliação de 01/10 repetiu as medidas da auditoria depois dos três lotes. Dos 24 achados, 19
estão atendidos e 5 parciais; e ela viu o que a auditoria não tinha visto:

- **No Processo, "O que fazer agora" tem as ações irreversíveis preenchidas.** "Encerrar Processo"
  é verde cheio e "Cancelar Processo" é vermelho cheio, os dois ativos, logo acima do aviso de que
  estão impedidos — o mesmo defeito que a `057` corrigiu no Detalhe do Edital.
- **A 375 px, as ações da Lista de Editais ficam inalcançáveis.** A tabela de cada Processo passa da
  largura do cartão, e o cartão recorta o que sobra, sem rolagem: a coluna "O que posso fazer" some.
  Na Condução do marco, a tabela "Recortes deste marco" empurra a página inteira para 486 px.
- **A mesma decisão, esquecida na tela vizinha:** a Matrículas põe o título e a nota lado a lado,
  como a Ocupação punha antes da `055`; a coluna de resultado dos Resultados fica à esquerda, porque
  a regra de coluna numérica não a alcança; plurais com parênteses ("consolidada(s)", "linha(s)")
  sobram em telas que o F8 não nomeava; os campos numéricos das Etapas mostram "2,0000".
- **Dois desalinhamentos menores:** na Revisão, cada bloco de rótulos tem a sua largura, e os
  valores começam em posições diferentes; o motivo que sucede um ato é área de texto de três linhas
  na Ordenação e no Corte, e campo de uma linha na Ocupação e no Sorteio.
- **Uma inconsistência na documentação:** a decisão 003 da `056` diz 48 rem, e a folha usa 60.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — No Processo, os atos irreversíveis não são os mais fortes (Priority: P1)

Quem abre um Processo Ativo vê, em "O que fazer agora", Encerrar e Cancelar separados, por último,
contornados e marcados como irreversíveis — como no Detalhe do Edital.

**Why this priority**: é a tela de entrada do Processo, e hoje os dois únicos botões preenchidos do
cartão são os dois gestos irreversíveis, justamente quando estão impedidos.

**Independent Test**: abrir o Processo Ativo do seed com `ana.gestora` a 1280 × 900 e contar os
atos preenchidos, a posição e o desenho de Encerrar e Cancelar, e o destino de cada link.

**Acceptance Scenarios**:

1. **Given** um Processo Ativo, **When** "O que fazer agora" é aberto por quem tem todos os papéis,
   **Then** nenhum ato do Processo é preenchido, e Encerrar e Cancelar vêm num grupo próprio,
   contornados, cada um com o marcador "irreversível".
2. **Given** um Processo em elaboração, **When** o cartão é aberto, **Then** "Ativar Processo"
   continua secundário, e Cancelar vem à parte, por último, contornado.
3. **Given** um Processo com Editais pendentes, **When** o cartão é aberto, **Then** o aviso de
   impedimento continua depois dos atos, e cada link leva ao mesmo lugar de antes.

---

### User Story 2 — A 375 px, toda ação da Lista se alcança (Priority: P1)

Quem abre a Lista de Editais ou a Condução do marco no celular rola a tabela na horizontal, dentro
de uma moldura, e alcança todas as ações; a página não rola de lado.

**Why this priority**: é o único defeito da série em que uma ação fica inalcançável.

**Independent Test**: com o viewport a 375 px, medir a largura de rolagem do documento e, na Lista,
comparar a largura de rolagem de cada moldura com a borda direita do último botão dela.

**Acceptance Scenarios**:

1. **Given** a Lista a 375 px, **When** medida, **Then** o documento tem 375 px de largura de
   rolagem, e a moldura de cada Processo rola até depois do último botão de ação.
2. **Given** a Condução de um marco a 375 px, **When** medida, **Then** o documento tem 375 px de
   largura de rolagem, e a tabela dos recortes rola dentro da sua moldura.
3. **Given** a Lista e a Condução a 1280 px, **When** abertas, **Then** nenhuma moldura rola, e a
   tela é a de antes.
4. **Given** a Alocação a 1280 px, **When** a página rola, **Then** o cabeçalho da matriz continua
   fixo.

---

### User Story 3 — A mesma decisão na tela vizinha (Priority: P2)

Matrículas, Resultados e as telas com plural entre parênteses adotam o que a `055` e a `057` já
decidiram para as vizinhas.

**Independent Test**: abrir Matrículas e Resultados a 1280 × 900 e medir a posição do título, da
nota e de cada célula da coluna de resultado; buscar "(s)" no texto visível das telas tocadas.

**Acceptance Scenarios**:

1. **Given** a Matrículas, **When** aberta, **Then** o título "O que sairá vazio, e por quê", a nota
   e a lista se empilham, e nenhum filho da seção fica ao lado de outro.
2. **Given** os Resultados de uma Etapa pontuada, **When** abertos, **Then** a nota fica à direita
   da célula; numa decisória, o rótulo ("favorável") fica à esquerda; "não avaliada", também.
3. **Given** a Distribuição, a Matrículas, o Recurso, a Ocupação e o histórico da Ocupação, **When**
   abertos, **Then** nenhum texto composto para a tela traz "(s)": a palavra vem no número dela.

---

### User Story 4 — O valor das Etapas como uma pessoa o escreve (Priority: P2)

Quem abre a etapa Etapas do assistente vê "2" no Peso e "6" na Nota mínima, e não "2,0000".

**Independent Test**: abrir a etapa Etapas do Edital 76/2027, ler o valor dos três campos numéricos,
salvar o rascunho e comparar o que ficou gravado com o que estava gravado antes.

**Acceptance Scenarios**:

1. **Given** uma Etapa com Peso 2 e Nota mínima 6, **When** a etapa é aberta, **Then** os campos
   mostram "2" e "6".
2. **Given** a mesma etapa, **When** "Salvar rascunho" é acionado sem nada mudar, **Then** o
   rascunho gravado é idêntico ao de antes da feature.
3. **Given** uma Pontuação máxima com casa decimal significativa (87,5), **When** a etapa é
   aberta, **Then** o campo mostra 87,5, sem arredondar.

---

### User Story 5 — Na Revisão e nos motivos, o mesmo desenho (Priority: P3)

Na Revisão, os valores começam na mesma coluna em todos os blocos. O motivo que sucede um ato tem o
mesmo controle, e a mesma largura, na Ordenação, no Corte, na Ocupação e no Sorteio.

**Independent Test**: medir, na Revisão do 76/2027, o x do primeiro valor de cada bloco; medir o
controle e a largura do motivo nas quatro telas.

**Acceptance Scenarios**:

1. **Given** a Revisão do 76/2027 a 1280 px, **When** medida, **Then** o primeiro valor de cada
   bloco de pares começa no mesmo x.
2. **Given** a Ocupação com apuração vigente, **When** o formulário de nova apuração é aberto,
   **Then** "Motivo da nova apuração" é área de texto de três linhas, na largura de leitura.
3. **Given** o Sorteio com relação congelada, **When** o formulário de relação nova é aberto,
   **Then** "Motivo da sucessão" é área de texto de três linhas, na largura de leitura.

---

### Edge Cases

Os casos-limite desta feature são requisitos, e estão escritos como tal abaixo — a seção de casos
de borda não entra na matriz de rastreabilidade, e nenhuma ferramenta a cobra:

- Processo em elaboração, Processo Cancelado ou Encerrado, e papel sem ato nenhum (**FR-1070**);
- Lista e Condução em tela larga, e a Alocação, que já tem moldura (**FR-1072**);
- coluna de resultado que mistura número e texto (**FR-1075**);
- plural cujo texto vai para ato, registro ou documento (**FR-1077**);
- campo vazio, casa decimal significativa e reexibição depois de recusa (**FR-1079**);
- rótulo mais longo que a coluna, e tela estreita na Revisão (**FR-1081**);
- o motivo de anulação do Sorteio, que não sucede ato (**FR-1083**).

---

## Requirements *(mandatory)*

### Functional Requirements

**Processo, "O que fazer agora" (R1)**

- **FR-1069**: Entre os atos do Processo em "O que fazer agora", nenhum MUST ser preenchido. Encerrar
  e Cancelar MUST vir por último, num grupo próprio depois de um filete, contornados em vermelho,
  cada um com o marcador "irreversível" — a regra que a `057` fixou para o Detalhe do Edital.
- **FR-1070**: "Ativar Processo" MUST continuar secundário, com a ajuda de sempre. Processo sem ato
  para o papel MUST continuar dizendo "Nenhum ato disponível para seus papéis nesta situação"; sem
  ato irreversível, não há grupo nem filete. O aviso de impedimento MUST continuar depois dos atos,
  e cada link MUST levar ao mesmo lugar de antes.

**375 px (R2)**

- **FR-1071**: Abaixo de 60 rem de janela, a tabela de cada Processo da Lista de Editais MUST ficar
  numa moldura com rolagem horizontal, no lugar do recorte silencioso; as células MUST NOT ser
  empilhadas. Todo botão de ação MUST ser alcançável por rolagem dentro da moldura, e o documento
  MUST NOT rolar na horizontal.
- **FR-1072**: A partir de 60 rem, a moldura MUST NOT rolar — a Lista e a Condução ficam como estão
  em tela larga. A moldura da Alocação MUST continuar como está, com o cabeçalho da matriz fixo ao
  rolar a página.
- **FR-1073**: A tabela "Recortes deste marco" da Condução MUST ganhar a mesma moldura, e a 375 px o
  documento MUST NOT rolar na horizontal.

**A mesma decisão na tela vizinha (R3, R4, R5)**

- **FR-1074**: Na Matrículas, a seção "O que sairá vazio, e por quê" MUST empilhar o título, a nota,
  a lista e a confirmação, como a Ocupação depois da `055`. Sem regra nova na folha.
- **FR-1075**: Na tabela dos Resultados, a célula de nota MUST alinhar à direita, pela regra de
  coluna numérica que já existe. Célula de texto — o rótulo da decisória, "não avaliada" — MUST
  ficar à esquerda: texto não vai à direita sozinho.
- **FR-1076**: Os plurais com parênteses compostos para a tela em `distribuicao.html`
  ("consolidada(s)", "recusada(s)"), `matriculas.html` ("linha(s)"), `recurso.html` ("ato(s) de
  instrução"), `ocupacao.html` e `ocupacao_historico.html` ("Reversão de cota: N vaga(s)") e
  `compor_base.html` ("vaga(s) imediata(s) do Perfil") MUST passar a escrever a palavra no número
  dela, pelo filtro de plural que já existe.
- **FR-1077**: Antes de cada troca, o texto MUST ser conferido: se ele vai para ato, registro ou
  documento, MUST ficar como está e entrar no achado do F8. O teste que prende a grafia de
  `compor_base.html` MUST ser reescrito para a grafia nova sem mudar o que verifica.

**Etapas (R6)**

- **FR-1078**: Na etapa Etapas do assistente, Peso, Nota mínima e Pontuação máxima MUST mostrar o
  valor sem zeros à direita ("2", "6", "87,5"), sem arredondar.
- **FR-1079**: O rascunho gravado depois de "Salvar rascunho" MUST ser idêntico ao gravado antes da
  feature, no mesmo banco; se não for, o item MUST sair do lote e ficar registrado com a medida.
  Campo vazio MUST continuar vazio, e a reexibição depois de recusa MUST continuar devolvendo o que
  a pessoa digitou.

**Os dois desalinhamentos (R7, R8)**

- **FR-1080**: Na Revisão, a coluna de rótulos MUST ter a mesma largura em todos os blocos de pares,
  com valor fixo em rem, de modo que os valores comecem no mesmo x.
- **FR-1081**: O rótulo mais longo que a coluna MUST quebrar dentro dela, e em tela estreita a
  coluna MUST NOT empurrar o valor para fora do cartão.
- **FR-1082**: O "Motivo da nova apuração" da Ocupação e o "Motivo da sucessão" do Sorteio MUST usar
  o mesmo controle e a mesma largura do motivo da Ordenação e do Corte: área de texto de três
  linhas, na largura de leitura. O nome do campo, a obrigatoriedade e a ajuda MUST NOT mudar.
- **FR-1083**: O "Motivo da anulação" do Sorteio MUST ficar como está: ele não sucede ato, e não é
  o motivo de que a reavaliação fala.

**Documentação dos lotes (R9)**

- **FR-1084**: A decisão 003 do `research.md` da `056` MUST dizer 60 rem, o valor da folha. A descrição do
  PR 246 MUST NOT ser editada. O total da suíte completa MUST ir para a `verificacao.md` desta spec.

**Limites do lote**

- **FR-1085**: Para cada tela tocada, a lista de destinos de ação por papel — `href` de todo link do
  conteúdo, `action` de todo formulário, `formaction` e `name=value` de todo botão de envio — MUST
  ser idêntica antes e depois, medida com `ana.gestora` e `joana.avaliadora`.
- **FR-1086**: O envio de "Salvar rascunho" de cada etapa tocada do assistente MUST ter as mesmas
  chaves e os mesmos valores antes e depois, com uma exceção: na etapa Etapas, os valores de Peso,
  Nota mínima e Pontuação máxima MAY mudar de grafia ("2.0000" para "2") desde que designem o mesmo
  número — a prova para eles é a de **FR-1079**.
- **FR-1087**: A feature MUST NOT acrescentar ação, remover ação, mudar permissão, criar view nem
  mudar o domínio, nem o que se grava; MUST NOT mudar texto de interface além dos plurais de
  **FR-1076**; MUST NOT tocar o PDF nem os textos que gravam ato.
- **FR-1088**: Toda classe nova MUST ter regra na folha; `max-width` só em rem, ch, % ou token. O
  HTML da tela de distribuição MUST continuar abaixo de 120.000 caracteres, com o tamanho antes e
  depois registrado.

### Requisitos de experiência

- **UX-143**: O mesmo conceito MUST ter o mesmo desenho em telas vizinhas: o mesmo peso para o ato
  irreversível, o mesmo controle para o motivo, o mesmo alinhamento para o número.
- **UX-144**: Em tela estreita, o que não cabe MUST rolar dentro de uma moldura visível, e não ser
  recortado em silêncio: nenhuma ação fica fora de alcance.

### Key Entities

Não há entidade de domínio nova nem alterada. Os elementos são desenhos da gestão:

- **Ato do Processo**: Ativar, Encerrar, Cancelar — o conjunto que a tela já recebe.
- **Moldura de rolagem**: o contêiner que rola na horizontal abaixo de 60 rem.
- **Par rotulado** da Revisão, **motivo de sucessão**, **campo numérico da Etapa**.

---

## Success Criteria *(mandatory)*

Medidos no banco `ps_058_polish` (cópia de `ps_polish_audit`, o banco da auditoria), a 1280 × 900
salvo onde se diz 375 px, antes e depois; a tabela vai para [verificacao.md](verificacao.md).

### Measurable Outcomes

- **SC-411**: No Processo Ativo do seed, nenhum ato do Processo preenchido (antes: 2); Encerrar e
  Cancelar à parte, contornados, com "irreversível"; os destinos dos links iguais.
- **SC-412**: A Lista de Editais a 375 px tem o documento com 375 px de largura de rolagem, e cada
  moldura rola ao menos até a borda direita do seu último botão (antes: botões recortados, sem
  rolagem).
- **SC-413**: A Condução a 375 px tem o documento com 375 px de largura de rolagem (antes: 486).
- **SC-414**: A Alocação a 1280 px continua com o cabeçalho fixo ao rolar a página.
- **SC-415**: Na Matrículas, a nota da seção começa abaixo do título, e nenhum filho fica ao lado de
  outro (antes: a nota em x = 268, ao lado do título).
- **SC-416**: Nos Resultados, as notas à direita da célula e os textos à esquerda.
- **SC-417**: Nenhum "(s)" no texto visível das telas tocadas, salvo os registrados como texto que
  grava.
- **SC-418**: Na etapa Etapas, os campos mostram "2" e "6" (antes: "2.0000", "6.0000"), e o rascunho
  gravado é idêntico — ou o item sai, registrado com a medida.
- **SC-419**: Na Revisão do 76/2027, o primeiro valor de cada bloco de pares começa no mesmo x
  (antes: x diferentes entre DOC-INFO e TEC-LAB).
- **SC-420**: O motivo de sucessão tem o mesmo controle e a mesma largura nas quatro telas (antes:
  campo de uma linha de 1.232 px na Ocupação).
- **SC-421**: As listas de destinos de ação por papel e o envio de "Salvar rascunho" das etapas
  tocadas são idênticos antes e depois, com a exceção de **FR-1086**.
- **SC-422**: A suíte (`make lint check test-pg`) fica verde, o total vai para a `verificacao.md`, e
  o HTML da distribuição continua abaixo de 120.000 caracteres, com o tamanho antes e depois.
- **SC-423**: Nenhuma divergência entre o `research.md` da `056` e a folha sobre o limiar do grupo
  de ações.

### O que esta feature não cobre, deliberadamente

- a marca "CPF repetido" das Inscrições (decisão do usuário em 01/10);
- o cartão de Evento do Cronograma (a geometria não comporta);
- o ganho menor do glossário (a faixa visível é decisão);
- os textos que gravam ato (`objeto_legivel`, `validation.py`, `ocupacao.html` l. 207);
- a ação cheia com contador zero no Detalhe do Edital (observação da reavaliação, sem proposta).

Se um requisito acima prometer isso, está prometendo outra feature.

---

## Assumptions

- A medição "antes" é feita sobre `c4866e19` (a `main` com a reavaliação), no banco
  `ps_058_polish`, antes de qualquer template ou folha mudar.
- "Idêntica" na lista de ações (**FR-1085**) segue a decisão 017 da `057`; o envio (**FR-1086**) segue as
  decisões 005 e 015 da `056` — pares de chave e valor, sem o token de CSRF e com o `ruleId` mascarado.
- "Rascunho gravado" (**FR-1079**) é o estado persistido das Etapas do Edital depois de "Salvar
  rascunho" — as linhas das Etapas e o que o salvamento registra —, lido no banco antes e depois.
- As medidas são do `getBoundingClientRect` e de `scrollWidth` na página renderizada no navegador do
  aplicativo; as de 375 px, com o viewport emulado, medindo também `innerWidth`.
- Meta numérica fora de alcance dentro do escopo não amplia o escopo: o valor alcançado e a
  justificativa vão para o `verificacao.md`.
