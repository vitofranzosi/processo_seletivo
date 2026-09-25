# Feature Specification: A hierarquia do detalhe do Perfil

**Feature Branch**: `claude/spec-processos-seletivos-visao-395a64`

**Created**: 2026-09-21

**Status**: Draft

**Input**: Revisão de UI/UX de 21/09, feita **sobre a `041` já funcionando**: *"quando expande,
parece que uma segunda tabela independente foi inserida no meio da primeira"*.

> **Faixa de identificadores.** Abre em **FR-622** e **SC-222**. Teto medido em 2026-09-21:
> `FR-621` / `SC-221`. Nenhum `UX-` é definido.

> **Teto proporcional, e ele é apertado de propósito.** **Uma** história e **dez** requisitos. Esta
> feature **não muda regra de negócio nenhuma**: os números, as fontes, as fórmulas e os
> denominadores são os da `041`. O que muda é a **forma** — e uma spec de polish que crescer vira
> "melhorar a UX da Visão Geral", que não é escopo, é intenção.

---

## 1. O problema, medido

A `041` resolveu o **modelo informacional**: o Perfil aparece, com vagas, demanda e razão próprias.
Ela não resolveu a **hierarquia perceptiva**.

Medido na tela, em 21/09:

| | |
|---|---|
| Largura da tabela filha | **781 px** |
| Largura da tabela principal | **797 px** — a filha ocupa **98%** do pai |
| Cabeçalho filho | `12,16 px` · peso `600` |
| Cabeçalho principal | `13,12 px` · peso `600` — praticamente a mesma força |

**Com 98% da largura e a mesma espessura tipográfica, a região expandida não tem como ler como
subordinada.** Ela lê como irmã. O olho precisa reaprender a grade a cada expansão, e volta
bruscamente ao próximo Edital.

**Há também duplicação de ênfase.** O Edital diz *"1 de 2 Perfis sem nenhuma inscrição"* e o Perfil,
logo abaixo, repete *"Encerrou sem nenhuma inscrição submetida"*. Semanticamente correto; visualmente
pesado. **O agregado deve resumir, e o detalhe explicar** — não os dois dizerem a mesma frase.

**E a tabela filha carrega peso que não precisa carregar.** *Cadastro de reserva* é coluna, e é
atributo **caracterizador** do Perfil — não métrica que alguém compara verticalmente. Ocupando
coluna, ela alarga a tabela e reforça a leitura de "planilha dentro de planilha".

---

## 2. O que esta feature NÃO é

- **Não redesenha a `041`.** A arquitetura — segunda `<tr>`, `<details>` dentro do `<td>`, marcas
  por Perfil, filtro de atenção — fica como está.
- **Não reabre a `041`.** Ela está fechada e verde. O que muda aqui é representação, e a `SC-217`
  dela é substituída por escrito (`FR-629`).
- **Não introduz JavaScript.** O ganho visual não compensa trocar um mecanismo nativo por código.
- **Não cria renderização especial para um Perfil.** Duas gramáticas para a mesma informação é o que
  a `041` recusou, e o incômodo com o caso de um Perfil é **sintoma do peso da tabela filha** — que
  esta feature corrige.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O detalhe lê como aprofundamento da linha, e não como outra tabela (Priority: P1) 🎯

Quem coordena expande um Edital e **continua percebendo que está na tabela de Editais** — agora com
uma linha aberta. Não entrou em outro lugar.

**Why this priority**: é a feature inteira. Não há segunda história.

**Independent Test**: expandir um Edital e verificar que a região filha é visivelmente recuada e
mais estreita que a principal, com o cabeçalho mais discreto e uma régua ligando-a ao Edital acima.

**Acceptance Scenarios**:

1. **Given** um Edital expandido, **When** a região filha é medida, **Then** ela é **mais estreita**
   que a tabela principal e visivelmente recuada.
2. **Given** a região filha, **When** o cabeçalho dela é comparado ao da principal, **Then** ele é
   tipograficamente **menos dominante**.
3. **Given** um Perfil, **When** ele é lido, **Then** código, localidade e cadastro de reserva estão
   na **identidade** dele — e nenhum ocupa coluna.
4. **Given** as colunas da região filha, **When** enumeradas, **Then** são apenas métricas
   comparáveis: vagas, submetidas, em preenchimento, inscrições por vaga e atenção.
5. **Given** um Edital com Perfil sem procura, **When** as duas granularidades são lidas, **Then** o
   Edital **resume** com o denominador e o Perfil usa **rótulo curto** — a mesma frase não aparece
   duas vezes.
6. **Given** o controle de expansão, **When** lido, **Then** ele nomeia a **ação** e a
   **quantidade**, e não parece controle solto.
7. **Given** a expansão, **When** operada só por teclado, **Then** ela continua abrindo e fechando —
   **nenhum JavaScript** foi introduzido.

### Edge Cases

- **Edital de um Perfil só** — a região filha continua sendo a mesma, e agora é leve o bastante para
  uma linha não incomodar. **Sem renderização alternativa.**
- **Perfil sem código, sem localidade e sem reserva** — a linha de identidade **some inteira**, e
  não se escreve *"não informado"*. *Faltando só **parte** dos três, a linha existe com o que há:
  um Perfil sem código e sem localidade mas **com** reserva ainda escreve "CR ilimitado".*
- **Perfil sem cadastro de reserva** — **nada** é escrito, e a ausência do metadado é a
  representação (`FR-626`). Dizer *"não há"* em toda linha é o ruído que esta feature remove.
- **Leitor de tela** — a tabela filha continua tendo nome, ainda que ele não seja desenhado.

---

## Requirements *(mandatory)*

- **FR-622**: A expansão MUST continuar sendo `<details>`/`<summary>`, com o comportamento nativo de
  teclado e de estado. **Nenhum JavaScript** MUST ser introduzido para expandir, recolher ou
  animar.
- **FR-623**: A **região filha** — a segunda linha do grupo, com tudo o que ela contém — MUST ler
  como **subordinada** à linha do Edital. Em largura que
  comporte a tabela principal **sem adaptação**, ela MUST ser recuada e **mais estreita** que a
  principal. Em **viewport estreito**, o parentesco MUST permanecer perceptível por recuo, régua,
  borda ou outro recurso que **não comprometa a leitura das métricas**. *A medida de 98% foi feita
  no desktop; transformá-la em invariante de qualquer largura faria a feature sacrificar o telefone
  para satisfazer o monitor — e lá a tabela já rola dentro da moldura.* A régua e o recuo são meio,
  e não fim: o que se exige é o parentesco perceptível.
- **FR-624**: O cabeçalho da **tabela da região filha** MUST ser tipograficamente **menos
  dominante** que o da tabela principal.
- **FR-625**: O nome acessível da tabela filha MUST permanecer no documento e MUST NOT ser
  desenhado. *Removê-lo deixaria uma tabela anônima dentro de outra; mantê-lo à vista repete o que
  a linha acima já diz.*
- **FR-626**: Código, localidade e cadastro de reserva MUST integrar a **identidade** do Perfil, e
  MUST NOT ocupar coluna. **Havendo** cadastro de reserva, a espécie MUST ser dita — *limitado* com
  o seu limite, ou *ilimitado*. **A ausência do metadado representa que não há**, e o texto
  *"não há"* MUST NOT ser escrito.

  *A redação anterior exigia as **três** espécies "distinguíveis" e, no caso-limite, mandava não
  escrever a terceira — as duas coisas não são compatíveis. A saída não é voltar a escrever
  "não há" em toda linha: é dizer com precisão que a ausência **é** a representação, que é a grafia
  que este repositório já usa em `especie_de_reversao` e em `requerimento_momento`.*
- **FR-627**: Além da coluna de **identidade** do Perfil, a **tabela da região filha** MUST ter
  **somente cinco** colunas, todas de leitura comparável: vagas imediatas, submetidas, em
  preenchimento, inscrições por vaga e atenção. *São seis colunas na tela. Uma redação anterior
  dizia "as colunas MUST ser apenas métricas", e autorizava a leitura de que o Perfil deixara de ser
  coluna; outra atribuía colunas à **região**, quando quem as tem é a tabela dentro dela.*
- **FR-628**: A atenção MUST ser dita **uma vez por granularidade**: o Edital **resume**, com o
  denominador de cada espécie; o Perfil usa **rótulo curto**. A mesma frase MUST NOT aparecer nas
  duas.
- **FR-629**: O controle de expansão MUST nomear a **ação** e a **quantidade**, e MUST NOT ser
  apresentado como controle solto.
- **FR-630**: Os controles de ordenação MUST separar **critério** de **direção**, e nenhuma opção de
  critério MUST embutir direção. *"Mais recentes" combinado com "Menor primeiro" significa "mais
  antigos", e ninguém lê isso.*
- **FR-631**: A **`SC-217` da `041` MUST ser explicitamente substituída**, citando o seu texto —
  *"as **três** espécies de cadastro de reserva são distinguíveis na tela, e a limitada diz o seu
  limite"*. O critério sucessor é a `SC-224`: a espécie deixa de ser coluna, passa à identidade, e
  **a que não tem reserva é representada pela ausência do metadado**.
- **FR-632**: A grade da tabela da região filha MUST ser **estável entre Editais**: a mesma coluna
  MUST ter a mesma largura em toda expansão do mesmo recorte. Texto secundário — identidade do
  Perfil, motivo de ausência, marca de parcialidade — MUST NOT determinar largura de coluna.
  *Cada expansão é uma `<table>` própria, e em layout automático cada uma se dimensiona contra o
  próprio conteúdo: medido, `Inscr./vaga` saiu com `192 px` num Edital e `78 px` no seguinte, porque
  num deles a frase "não se aplica: este Perfil não publica vaga imediata" caiu naquela célula. O
  efeito é a mesma coluna saltar ao rolar a página, e o número parar a `180 px` do próprio
  cabeçalho — o oposto de cinco colunas de leitura comparável, que é o que a `FR-627` quis.*
- **FR-633**: A **marca de atenção** da região filha MUST ser tipograficamente **menos dominante**
  que a marca do Edital. *A `FR-624` obrigou só o **cabeçalho**. Denominação, número e cabeçalho
  foram todos rebaixados, e a marca ficou idêntica à do Edital — mesma fonte, mesmo peso, mesma
  borda —, de modo que o elemento mais gritante da região filha passou a ser justamente o que
  menos deveria competir com a linha acima.*

---

## Success Criteria *(mandatory)*

- **SC-222**: **O critério que governa esta feature.** Quem expande um Edital continua percebendo
  que lê a **mesma linha do portfólio, aprofundada** — e não que entrou numa segunda tabela.
  Verificado por leitura humana no percurso, e sustentado pelas três medidas objetivas abaixo.
- **SC-223**: Em largura de desktop, a região filha é **mais estreita** que a tabela principal e o
  cabeçalho dela é **menor** — as duas medidas conferidas no navegador, contra os `98%` e a paridade
  tipográfica de hoje. Em largura de telefone, `documentElement.scrollWidth` continua **igual** a
  `clientWidth` — a página não rola para o lado —, e a tabela da região filha continua rolando
  **dentro** da moldura, como na `041`. *A redação anterior dizia "a leitura das métricas não
  piora", e não descrevia medição nenhuma.*
- **SC-224**: A tabela da região filha tem **uma** coluna de identidade e **cinco** de dado — seis ao todo —,
  e nenhuma delas é cadastro de reserva. Onde há reserva, a espécie e o limite aparecem na
  identidade; onde não há, **nada** é escrito.
- **SC-225**: **Zero** repetições da mesma frase de atenção nas duas granularidades.
- **SC-226**: **Zero** JavaScript novo, e a expansão continua abrindo por teclado.
- **SC-227**: **Zero** opções de critério de ordenação que embutam direção.
- **SC-228**: Num recorte com dois ou mais Editais expandidos, as larguras de coluna da tabela
  filha são **iguais** entre todas elas — conferido no navegador, contra as duas grades medidas
  hoje, que não coincidem em coluna nenhuma.
- **SC-229**: A marca de atenção da região filha é **menor** que a do Edital.

---

## Assumptions

### D-001 — o mecanismo não muda; o parentesco se resolve por desenho

A leitura mais direta do problema seria mover o controle para dentro da célula do Edital. **Ela custa
o mecanismo inteiro**: `<details>` e `<summary>` são indivisíveis — o resumo tem de estar dentro do
elemento que contém o conteúdo —, e um controle na linha 1 com conteúdo na linha 2 exigiria
JavaScript ou o truque do *checkbox*.

O que se perderia não é pouco: teclado nativo, o estado `open` que o leitor de tela anuncia, e zero
JavaScript numa base que não tem nenhum para isto.

**Recuo, régua e peso tipográfico entregam o parentesco sem trocar o mecanismo** — e é isso que a
`FR-623` exige, deixando o meio em aberto.

### D-002 — não há renderização especial para um Perfil

A `041` decidiu uma gramática só, e mantém-se. O incômodo com o Edital de um Perfil — *"uma tabela
inteira para uma linha"* — é **sintoma do peso da filha**, não do número de linhas: com cabeçalho
discreto, sem legenda desenhada e sem a coluna de reserva, uma linha custa duas alturas de texto.

**Corrigir o peso, e não acrescentar uma segunda renderização.**

### D-003 — a legenda fica invisível, e não removida

Ela é o **nome acessível** da tabela aninhada. Removê-la deixaria um leitor de tela diante de uma
tabela sem nome dentro de outra; mantê-la desenhada repete o que a linha logo acima já diz.

A base já tem a classe de ocultação acessível, e é ela que se usa.

### D-004 — o denominador fica, mesmo no resumo curto

*"1 Perfil sem procura"* é mais escaneável e abre exceção à regra que governa esta página inteira:
**todo número traz o denominador dito**. *"1 de 2 Perfis sem procura"* é igualmente curto e não abre
exceção.

No Perfil, o rótulo é curto sem prejuízo — ali o denominador é ele mesmo.

---

## Riscos e lacunas

| # | Lacuna | O que esta spec faz |
|---|---|---|
| **G-001** | *"Ler como subordinado"* é juízo perceptivo, e teste não o mede | A `SC-222` é humana, no percurso; a `SC-223` prende as **consequências** medíveis — largura menor e cabeçalho menor. Teste não substitui olhar, e fingir que substitui seria pior |
| **G-002** | A `SC-217` da `041` afirma a coluna de reserva **e** as três espécies explícitas | Substituída por escrito (`FR-631`), e o sucessor diz o que a ausência representa |
| **G-003** | O rótulo do controle muda entre aberto e fechado | Faz-se em CSS com dois rótulos e `details[open]`; **não** é motivo para JavaScript (`FR-622`) |

## Como saber que o plano saiu do problema

Esta feature muda **forma**, e nada além. Cinco sinais de que o planejamento deixou de resolver o
problema da `042` e passou a resolver outro:

- **JavaScript** para expandir, recolher, animar ou trocar rótulo — o `<details>` já faz, e o
  rótulo condicional é CSS (`FR-622`, `G-003`);
- um **componente de expansão novo**, em vez do que a `041` entregou;
- mudança de **fórmula, fonte, denominador ou consulta** — esta feature **não muda número nenhum**;
- **reestruturação da tabela principal**, que não é o problema: o que lê errado é a filha;
- uma **segunda renderização** para o caso de um Perfil (`D-002`).

*Registrado como sinal, e não como requisito: requisito que existe para impedir alguém de ler errado
outro requisito é nota de tarefa, e a `038` já decidiu isso por escrito.*

---

## Out of Scope

Ocupação, convocação, classificados e requerimentos — a evolução funcional do funil, que vem
**depois** desta. A série por ano. Qualquer indicador novo. Qualquer filtro novo. Qualquer mudança
em regra, fonte, fórmula ou denominador: esta feature **não muda número nenhum**.
