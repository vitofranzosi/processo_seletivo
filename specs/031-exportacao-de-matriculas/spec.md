# Feature Specification: Exportação de matrículas — o que já foi declarado, no formato que o Registro Acadêmico lê

**Feature Branch**: `claude/spec-031-exportacao-de-matriculas`

> **A numeração é `031` porque é o próximo número livre.** Varredura de 17/09/2026 nas worktrees
> desta máquina e na `main`: a maior pasta é `030`. O número virá de `--number 31`, e não da pasta.

> **Os identificadores continuam a faixa global.** Teto medido no mesmo dia, em todas as worktrees,
> **inclusive nas que têm trabalho não comitado** — `FR-432`, `SC-142`, `UX-059`. Esta spec abre em
> `FR-433`, `SC-143`, `UX-060`. As **decisões** reiniciam em `D-001`, porque são lidas dentro da
> feature que as produziu.

**Created**: 2026-09-17

**Status**: Draft — **bloqueada para implementação** por uma verificação externa (§5 e `Q-1`). A
redação está completa; o que falta não é decisão de produto, é uma resposta do Registro Acadêmico
que custa uma hora e não depende deste repositório.

**Input**: o contrato de saída da `029`
([contrato-de-saida.md](../029-requerimento-de-matricula/contrato-de-saida.md)), a inspeção da
planilha `Import_LIBB_58_78-2026.xlsx` — aba `Import_ModeloCefor`, 34 cabeçalhos em `A1:AH1`, uma
linha de exemplo em `A2:AH2`, 13 comentários de cabeçalho, tudo armazenado como texto com formato
`@` — e a medição das divergências contra o código, registrada na §6.

---

## 1. Visão

O que o candidato declarou no Requerimento de Matrícula sai deste sistema **no formato que o
Registro Acadêmico importa**, sem redigitação e sem planilha montada à mão.

A `029` coletou 21 das 34 colunas e **proibiu a exportação** (`FR-404`). Esta spec revoga aquela
proibição — e a revoga pelo motivo que a criou: a proibição existia porque **nenhuma conversão podia
ser inventada** antes de alguém medir de onde cada coluna sairia. O contrato de saída mediu. Agora
há o que exportar, e há oito colunas que este sistema legitimamente não tem.

## 2. Problema

Hoje a passagem da seleção para a matrícula é **redigitação**. Alguém lê o dossiê de cada convocado
e preenche uma planilha, linha por linha, com dado que o sistema já guarda em coluna. O erro de
digitação aparece depois da matrícula, no Registro Acadêmico, com a pessoa no meio.

**O risco não é o trabalho, é o erro silencioso.** Uma planilha montada à mão preenche toda coluna,
porque a pessoa que a monta tenta ser prestativa: sem código de curso, ela escreve o que parece
certo; sem faixa per capita, ela converte a faixa familiar de cabeça. Nada nesse fluxo distingue
*"este dado foi declarado"* de *"este dado foi deduzido por alguém às pressas"*.

## 3. Motivação

**Exportar é mais seguro do que redigitar — desde que a exportação saiba dizer "não sei".** É essa a
diferença que justifica a feature: uma coluna vazia gerada por regra é uma afirmação verificável de
ausência; uma coluna preenchida por dedução humana é indistinguível de dado declarado.

## 4. Atores

| Quem | Papel nesta feature |
|---|---|
| Quem conduz o processo | pede o arquivo de um Edital, lê o que saiu vazio e por quê |
| Registro Acadêmico | consome o arquivo; **não** é usuário deste sistema |
| Candidato | não age nesta feature — ele já declarou na `029` |

## 5. Pré-condições

**Uma delas não é deste repositório, e é bloqueante.** As demais já estão satisfeitas.

| Pré-condição | Situação |
|---|---|
| A `029` mesclada, com requerimentos enviados | ✅ `main`, desde 17/09/2026 |
| O contrato de saída versionado (`FR-403`) | ✅ 34 colunas mapeadas |
| Resultado com convocados | ✅ a convocação já existe |
| **O importador aceita célula vazia nas oito colunas da `D-001`** | ❌ **não verificado** (`Q-1`) |

**Por que a última bloqueia.** Toda a forma desta feature depende dela. Se o importador recusar
`COD_CURSO` vazio, o arquivo gerado não serve para nada, e isso se descobre **depois da matrícula**.
A verificação custa duas linhas sintéticas enviadas ao importador real — e responde, de uma vez, as
três perguntas mais caras desta spec.

## 6. Decisões fechadas antes do planejamento

### D-001 — Dado que este sistema não possui sai **vazio**, nunca deduzido

Decisão do usuário, 17/09/2026. Oito colunas saem vazias porque o valor é **externo a este
sistema** — vocabulário do sistema acadêmico, ou dado que a `029` decidiu não coletar:

| Coluna | Por que é externa |
|---|---|
| `COD_CURSO`, `COD_TURNO`, `COD_POLO` | vocabulário do sistema acadêmico, que este sistema não conhece |
| `COD_NACIONALIDADE` | este sistema guarda texto livre; o destino pede código, sem tabela de correspondência |
| `TITULO_ELE`, `ZONA_ELE`, `SECAO_ELE` | a `029` decidiu **não coletar** (`FR-382`, `Q-4` da `029`) |
| `RENDA_PER_CAPITA_PNP` | ver `D-002` |

**A consequência de escopo é grande, e é o que essa decisão comprou:** não há configuração de
códigos por oferta, não há tabela oficial de nacionalidade, não há cadastro de turno nem de polo.
Um subsistema inteiro de configuração sai do escopo porque a resposta certa é a célula vazia.

### D-002 — A faixa de renda não é convertida, porque os limites coincidirem não as torna a mesma coisa

`RENDA_PER_CAPITA_PNP` sai **vazia**, e esta decisão precisa da tabela ao lado para ser entendida:

| Este sistema — soma da família (`FR-412`) | Destino — por pessoa |
|---|---|
| Até 0,5 · 0,5–1 · 1–1,5 · 1,5–2,5 · 2,5–3,5 · acima de 3,5 | os mesmos cortes, com outro denominador |

**Os limites são idênticos, e é exatamente por isso que o mapeamento direto é tentador.** Muda o
denominador. O número de pessoas do domicílio nunca foi coletado, e dividir uma faixa por um número
que não se tem não produz uma faixa. A divergência já estava nomeada na `029` (o `R-7` daquela spec); aqui ela
vira a instrução de emitir vazio.

### D-003 — `AC` sai da **ausência** de Modalidade, e as cotas saem do código do Edital

`Inscricao.modality_id` é anulável, e **nulo é ampla concorrência** — não é falta de dado. O destino
chama isso de `AC`. A correspondência *ausência → `AC`* é a única desta feature que é derivação
legítima, e não invenção: ela traduz o mesmo fato.

Para as demais, `COD_FORMA_INGRESSO` recebe `ModalidadeConcorrencia.code` **como o Edital o
escreveu**. Esse campo é texto livre digitado por quem redige, e certames já publicados podem trazer
grafia que o destino não conhece — o próprio `seed_demo` escreve `PPP` onde o comentário da planilha
prevê `PPI`. **A exportação não corrige a grafia**: o código publicado é ato imutável, e reescrevê-lo
na saída faria o arquivo discordar do Edital. Grafia desconhecida é relatada (`FR-441`), não trocada.

**E a grafia divergente não é hipótese.** O `seed_demo` deste repositório declara a Modalidade
`PPP` — *"Pessoas pretas, pardas e indígenas"*, fundada na Lei 12.990/2014 — onde o comentário da
planilha prevê `PPI`. Duas letras de diferença, o mesmo instituto jurídico, e nenhuma das duas
pontas sabe da outra.

### D-004 — `ESTADO_CIVIL` é flexionado por tabela explícita, e isso não é bloqueio

O destino escreve `Casada`; este sistema guarda `CASADO` e exibe `Casado(a)`. São 4 estados civis × 2
sexos = **8 strings**, escritas nesta spec (§10.4) e verificadas por teste. `SEXO` é binário dos dois
lados, de modo que a flexão é total — não há caso sem resposta.

### D-005 — O arquivo é gerado, nunca copiado do modelo

O binário da amostra carrega formatação residual até `AT1000` e componentes de extensão do Excel que
leitores estritos rejeitam. A saída é um `.xlsx` **construído**, com uma aba, 34 cabeçalhos e as
linhas de dados — e nada mais.

### D-006 — A linha de exemplo da planilha não entra no repositório, em forma nenhuma

`A2:AH2` contém dados de uma pessoa real. Ela não vira fixture, nem exemplo em documentação, nem
caso de teste. A varredura `backend/tests/test_sem_dado_pessoal_da_amostra.py`, que a `029` criou,
já guarda essa promessa e alcança os arquivos desta feature por `glob`.

## 7. Escopo

- Gerar o arquivo de importação de um Edital, para a população escolhida.
- Emitir as 34 colunas na ordem e na grafia exatas do destino, todas como texto.
- Relatar, junto do arquivo, o que saiu vazio e por quê.
- Recusar a geração quando um valor teria de ser **inventado**.
- Registrar quem gerou, quando, de qual versão do resultado e com qual versão dos mapeamentos.

## 8. Fora de escopo

- **Importar** no sistema acadêmico, ou chamá-lo por interface programática. O arquivo é entregue a
  uma pessoa.
- Cadastrar códigos de curso, turno, polo ou nacionalidade (`D-001`).
- Corrigir a grafia de Modalidade de Editais publicados (`D-003`).
- Coletar título, zona e seção eleitorais. Reabrir é `Q-4` da `029`, e continua não bloqueante.
- Alterar qualquer coisa no Requerimento. Esta feature **lê**.

## 9. User Scenarios & Testing *(mandatory)*

### User Story 1 — O arquivo de um Edital, sem redigitar nada (Priority: P1)

Quem conduz abre o Edital, escolhe a população, e recebe um `.xlsx` com uma linha por pessoa,
pronto para o importador.

**Why this priority**: é a feature. Sem ela, nada muda para ninguém.

**Independent Test**: gerar para um Edital com convocados e abrir o arquivo — 34 colunas, na ordem,
tudo texto, dados a partir da linha 2.

**Acceptance Scenarios**:

1. **Given** um Edital com três convocados de requerimento enviado, **When** quem conduz gera o
   arquivo, **Then** ele tem 3 linhas de dados e nenhuma linha de exemplo.
2. **Given** um convocado de ampla concorrência, **When** o arquivo é gerado, **Then**
   `COD_FORMA_INGRESSO` traz `AC`, derivado da ausência de Modalidade (`D-003`).
3. **Given** um CPF que começa por zero, **When** o arquivo é aberto, **Then** o zero inicial está lá.

---

### User Story 2 — O que saiu vazio, dito antes de alguém perguntar (Priority: P1)

Junto do arquivo, quem conduz recebe o **relatório de lacunas**: quais colunas saíram vazias, para
quantas pessoas, e por qual motivo.

**Why this priority**: é o que impede a lacuna de virar preenchimento manual às pressas. Sem o
relatório, quem receber o arquivo vai completar as células vazias — e o erro volta pela porta que a
feature existe para fechar.

**Independent Test**: gerar e conferir que o relatório nomeia as oito colunas da `D-001` com a razão
de cada uma.

**Acceptance Scenarios**:

1. **Given** qualquer geração, **When** o relatório é lido, **Then** `COD_CURSO` aparece como
   *"vocabulário do sistema acadêmico — preencher no destino"*, e não como erro.
2. **Given** um convocado que declarou cor **indígena**, **When** o relatório é lido, **Then** ele
   nomeia a pessoa e diz que o destino não comporta o valor declarado (`FR-438`).

---

### User Story 3 — A geração que se recusa a mentir (Priority: P1)

Quando uma coluna exigiria valor inventado, a geração **para** e diz o que falta.

**Why this priority**: é a garantia que separa esta feature de uma planilha feita à mão. E é P1, e
não P3, porque uma exportação que aproxima é **pior** do que redigitar: ela erra com autoridade.

**Independent Test**: gerar para um Edital cuja Modalidade tem grafia desconhecida e verificar que
nada é gerado.

**Acceptance Scenarios**:

1. **Given** uma Inscrição sem requerimento enviado na população escolhida, **When** a geração é
   pedida, **Then** ela é recusada e a recusa nomeia a pessoa.
2. **Given** um requerimento em rascunho, **When** a geração é pedida, **Then** ele **não** entra no
   arquivo — ninguém declarou aquilo.

---

### User Story 4 — O mesmo arquivo, duas vezes (Priority: P2)

Gerar de novo, do mesmo resultado, produz o mesmo conteúdo.

**Why this priority**: sem isso, duas pessoas gerando no mesmo dia obtêm arquivos diferentes e
ninguém sabe qual foi importado.

**Independent Test**: gerar duas vezes sem mudança no meio e comparar o conteúdo célula a célula.

---

### Edge Cases

- **Requerimento sucedido entre duas gerações**: o arquivo traz o **vigente** no instante da
  geração, e o registro de auditoria guarda qual era.
- **Convocado sem requerimento porque o Edital não o exige**: a população fica vazia, e a geração é
  recusada com essa frase — não com um arquivo de zero linhas.
- **`NÚMERO` com `S/N`**: sai como texto, sem tentativa de virar número.
- **Nome com acento e cedilha**: preservado; o cabeçalho `ENDEREÇO` também é acentuado e sai
  exatamente assim.

## 10. Regras de negócio

### 10.1 A população

- **FR-433**: A geração MUST exigir a escolha explícita de uma população — os convocados de uma
  chamada, ou o conjunto de um resultado — e MUST NOT ter população padrão implícita.
- **FR-434**: A geração MUST incluir **apenas** requerimentos com status *enviado*, e MUST NOT
  incluir rascunho: rascunho não é declaração.
- **FR-435**: Quando alguém da população não tem requerimento enviado, a geração MUST ser recusada,
  nomeando quem falta — e MUST NOT gerar o arquivo com a linha faltando.

### 10.2 O formato físico

- **FR-436**: O arquivo MUST ser `.xlsx` com **uma** aba chamada `Import_ModeloCefor`, 34 cabeçalhos
  em `A1:AH1` na grafia e na ordem do destino — acentos inclusive — e dados a partir da linha 2.
- **FR-437**: Todas as 34 células de dado MUST ser emitidas como **texto**, com formato `@`,
  inclusive datas, CPF, RG, CEP e códigos: é o que preserva zero à esquerda e impede o Excel de
  reinterpretar `dd/mm/aaaa` como número serial. Datas MUST sair em `dd/mm/aaaa` sem depender do
  idioma do servidor.

### 10.3 O que sai vazio, e o que interrompe

- **FR-438**: As oito colunas da `D-001` MUST sair vazias, e a geração MUST NOT deduzir valor para
  nenhuma delas.
- **FR-439**: A geração MUST produzir um **relatório de lacunas** junto do arquivo, nomeando cada
  coluna vazia, a razão e a quantidade de linhas afetadas.
- **FR-440**: Quando o valor declarado não tem correspondente no destino — o caso conhecido é a cor
  **indígena** (`R-1`) —, a coluna MUST sair vazia e o relatório MUST nomear a pessoa e o valor
  declarado. A exportação MUST NOT substituir por valor próximo.
- **FR-441**: Quando o `code` da Modalidade não está entre os que o destino reconhece, a geração
  MUST ser recusada e MUST nomear o código e o Edital — e MUST NOT reescrever a grafia publicada
  (`D-003`).

### 10.4 As conversões que existem

- **FR-442**: `ESTADO_CIVIL` MUST ser flexionado conforme `SEXO`, por esta tabela e por nenhuma
  outra regra:

| | Masculino | Feminino |
|---|---|---|
| `SOLTEIRO` | Solteiro | Solteira |
| `CASADO` | Casado | Casada |
| `DIVORCIADO` | Divorciado | Divorciada |
| `VIUVO` | Viúvo | Viúva |

- **FR-443**: `COD_FORMA_INGRESSO` MUST receber `AC` quando a Inscrição não tem Modalidade, e o
  `code` publicado quando tem (`D-003`).
- **FR-444**: `CEP` MUST sair com hífen, `CPF` e `CELULAR` sem pontuação — a forma de cada um é a do
  destino, e não a da coluna deste sistema.
- **FR-445**: Cada uma das 34 colunas MUST ter serializador próprio, com origem, transformação e
  comportamento na ausência declarados. A exportação MUST NOT aplicar `legivel()` genericamente:
  aquela função serve à leitura humana das duas telas da `029`, e o destino não é uma delas.

### 10.5 Reprodutibilidade e registro

- **FR-446**: Duas gerações da mesma população, sem alteração entre elas, MUST produzir conteúdo
  idêntico, com linhas em ordem determinística.
- **FR-447**: Toda geração MUST registrar Edital, população, quantidade de linhas, autor, instante e
  a versão dos mapeamentos usados — e o registro MUST ser append-only, como os demais atos.
- **FR-448**: `CLASSIF_CURSO_FINAL` MUST vir de fonte declarada, e MUST NOT vir do índice da linha
  no arquivo. Qual fonte é `Q-2`.

### 10.6 O que esta feature não faz

- **FR-449**: A exportação MUST NOT alterar requerimento, inscrição, resultado ou Edital. É leitura.
- **FR-450**: A exportação MUST NOT chamar o sistema acadêmico por interface programática.

## 11. Autorização

| Quem | O quê | Como |
|---|---|---|
| Quem conduz | gerar o arquivo de um Edital sob seu escopo | **permissão nova**: `matricula:exportar` |

**Aqui há permissão nova, e a razão é o conteúdo.** O arquivo reúne, numa linha só, CPF, RG,
filiação e endereço de cada convocado — é o artefato mais concentrado de dado pessoal que este
sistema produz. Quem lê o dossiê de uma Inscrição vê uma pessoa por vez, e a permissão existente
autoriza isso. Baixar o conjunto inteiro é outro ato, e por isso é outra permissão (Princípio III).

## 12. UX

- **UX-060**: O arquivo e o relatório de lacunas MUST chegar juntos, e a tela MUST mostrar o resumo
  das lacunas **antes** do download — depois dele, ninguém lê.
- **UX-061**: A recusa MUST dizer o que falta e de quem, em vez de *"não foi possível gerar"*.

## 13. Critérios de aceite

- **SC-143**: Um Edital com convocados gera arquivo que o importador real aceita — verificado
  **contra o importador**, e não contra a leitura da planilha.
- **SC-144**: Um CPF iniciado por zero, uma data e um CEP sobrevivem à ida e volta pelo Excel sem
  perder zero, virar número serial ou trocar de formato.
- **SC-145**: As oito colunas da `D-001` saem vazias, e o relatório nomeia as oito com a razão de
  cada uma.
- **SC-146**: Um convocado que declarou cor indígena gera arquivo com `COR` vazia e relatório que o
  nomeia — verificado como caso próprio, e não como efeito colateral.
- **SC-147**: Uma Modalidade com grafia desconhecida recusa a geração inteira, e a mensagem traz o
  código e o Edital.
- **SC-148**: Duas gerações seguidas produzem arquivos idênticos célula a célula.
- **SC-149**: Um rascunho na população não entra no arquivo, e a geração é recusada por falta de
  declaração.
- **SC-150**: A geração sem `matricula:exportar` é recusada, inclusive por acesso direto ao endereço.
- **SC-151**: Nenhum arquivo desta feature contém dado da linha de exemplo da planilha — verificado
  pela varredura que a `029` já mantém (`D-006`).

## 14. Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| **`R-1` — o destino não comporta *indígena*** | quem se declarou indígena chega ao Registro Acadêmico sem cor, ou com cor errada | `FR-440`: vazio e relatório nominal. **Corrigir de verdade exige mudar o domínio do destino** |
| `R-1b` — a contradição é interna ao destino | a Modalidade de cota **nomeia** indígenas (`PPP`, Lei 12.990/2014), e a coluna `COR` do mesmo arquivo não os comporta | nenhuma, deste lado: a incoerência é do formato de destino, e é material para a conversa de `Q-1` |
| `R-2` — o importador recusar célula vazia | a feature inteira não serve | `Q-1`, verificado **antes** de escrever código |
| `R-3` — grafia de Modalidade divergente em Editais antigos | geração recusada para certames já encerrados | `FR-441` recusa e nomeia; a correspondência é decisão de quem opera, por Edital |
| `R-4` — o arquivo circular por e-mail | o artefato mais concentrado de dado pessoal fora do sistema | `UX-060` e a permissão própria reduzem; **não eliminam** |

## 15. Questões abertas

- **Q-1** — **O importador aceita célula vazia nas oito colunas da `D-001`?** *(Bloqueante: §5.)*
  Custa duas linhas sintéticas enviadas ao importador real, e responde também `Q-3` e `R-1`.
- **Q-2** — `CLASSIF_CURSO_FINAL` é a classificação no curso ou a numeração das linhas? O nome e o
  comentário do Registro Acadêmico discordam, e a planilha não desempata — vem pré-preenchida de `1`
  a `35`, com o comentário mandando continuar a sequência. *(Bloqueante para a coluna, não para a
  feature.)* Herdada da `Q-7` da `029`.
- **Q-3** — **O Registro Acadêmico aceita um protocolo opaco?** `INSC` traz `117817` na amostra; o
  protocolo deste sistema é `INS-2026-K7M4Q2PX`, **deliberadamente sem sequência**, porque um número
  corrido diria quantas inscrições existem. Não é divergência de formato a normalizar: torná-lo
  sequencial desfaria uma decisão de domínio. *(Bloqueante para a coluna.)*
- **Q-4** — O comentário de `IDENTIDADE_DATA` na planilha chama a coluna de *"data de nascimento"*,
  por erro de cópia. Confirmar com o Registro Acadêmico antes de tratar os comentários como fonte.
  *(Não bloqueante: o cabeçalho é inequívoco.)*
- **Q-5** — `NECESSIDADES_ESPECIAIS` é texto livre aqui (`TextField`) e traz `NENHUMA` na amostra.
  Há vocabulário fechado no destino? *(Não bloqueante: texto livre passa.)*

## 16. Dependências

**Reais e de leitura** — o Requerimento de Matrícula (`029`), a convocação (população), a
classificação (`Q-2`), a identidade (nome, CPF, e-mail), a oferta (`NOME_POLO`).

**Externa e bloqueante** — a confirmação do Registro Acadêmico sobre célula vazia (`Q-1`).

**Declarada e não construída** — o cadastro de códigos institucionais. A `D-001` a dispensa desta
feature; se um dia o Registro Acadêmico exigir os códigos preenchidos, ela volta como spec própria.

## 17. Correção a fazer na `029`

O contrato de saída cita `Q-3` como justificativa das colunas `COD_CURSO`, `COD_TURNO` e `COD_POLO`.
Mas `Q-3` na spec da `029` é *"e-mail da matrícula"*, **resolvida em 16/09/2026**, e nenhuma questão
aberta daquela spec cobre os códigos institucionais. A citação aponta para pergunta resolvida sobre
outro assunto. Esta feature substitui aquela justificativa pela `D-001`, e o contrato de saída deve
passar a citá-la.
