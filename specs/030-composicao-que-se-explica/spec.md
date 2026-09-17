# Feature Specification: A composição que se explica

**Feature Branch**: `030-composicao-que-se-explica`

**Created**: 2026-09-16

**Status**: Draft

**Input**: Reauditoria exploratória de UX de 2026-09-16 —
[doc/auditoria-exploratoria-ux-2026-09-16.md](../../doc/auditoria-exploratoria-ux-2026-09-16.md) —,
achados ACH-04, ACH-05, ACH-09, ACH-10, ACH-16, ACH-36 e ACH-61.

## Por que esta feature existe

A reauditoria percorreu os seis cenários pelo navegador e concluiu que o produto **elabora e publica
com rigor**, mas que o primeiro contato com a composição é caro. O gargalo não é falta de
explicação — a prosa deste sistema é precisa e abundante. O gargalo é que **a explicação está sendo
usada para justificar perguntas que não precisavam ser feitas**.

A medida é direta: para o Edital mais simples da amostra — um Perfil, três vagas, uma Etapa, sem
cota —, a etapa 5 do assistente abre **28 controles**, entre eles duas decisões que são
matematicamente vazias quando há uma única Etapa e duas obrigatórias sem valor padrão.

Esta especificação **não inventa um padrão novo**. Ela aplica ao **marco classificatório** e ao
**Perfil de Vaga** o padrão que o produto já domina na **Etapa de Avaliação**, onde escolher a forma
de conclusão vem com a consequência escrita antes: *"A pontuada publica nota e não publica rótulos;
a decisória publica os rótulos do resultado e não publica nota."*

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compor o marco do Edital simples sem consultar ajuda (Priority: P1)

Um servidor que recebeu a tarefa de cadastrar um Edital simples — um Perfil, três vagas, uma Etapa
de análise curricular, sem cota — chega à etapa de Classificação. Ele responde **uma** pergunta
sobre como a ordem daquele marco é produzida e preenche apenas o que essa resposta torna relevante.
Ele não é levado a decidir arredondamento sem saber o que arredonda, nem a inventar um código para
um objeto cujo nome acabou de ler pela primeira vez.

**Why this priority**: é o ponto onde a auditoria observou a primeira hesitação real, e é o caso
mais comum da amostra. Entregue sozinho, já reduz o custo do primeiro contato para a maioria dos
Editais.

**Independent Test**: montar o Edital canônico de três vagas até o fim da etapa de Classificação,
sem abrir o disclosure de ajuda, contando os controles apresentados.

**Acceptance Scenarios**:

1. **Given** um Edital com um Perfil e uma Etapa classificatória, **When** o elaborador acrescenta um
   marco, **Then** o sistema pergunta primeiro **como a ordem é produzida** e apresenta apenas os
   campos pertinentes à resposta.
2. **Given** um marco cuja ordem nasce da pontuação e que enumera **uma única** Etapa, **When** o
   elaborador compõe o marco, **Then** o sistema **não pergunta** como as pontuações se combinam nem
   qual normalização aplicar, e **declara** que com uma Etapa a pontuação combinada é a dela.
3. **Given** um marco recém-acrescentado, **When** o elaborador o vê pela primeira vez, **Then**
   casas decimais e arredondamento já vêm preenchidos com valor padrão editável.
4. **Given** um Perfil sem nenhuma Modalidade de Concorrência declarada, **When** o elaborador o
   compõe, **Then** o sistema **não apresenta** as perguntas sobre qual Modalidade é a ampla
   concorrência nem sobre reversão de vaga reservada.

---

### User Story 2 - Entender o conceito no ponto em que a decisão é tomada (Priority: P2)

O mesmo servidor encontra as palavras **marco classificatório**, **consolidar**, **recorte**,
**geração** e **faixa**. Cada uma aparece acompanhada do que significa, na tela onde a decisão
acontece — e não num glossário, num manual ou numa tela posterior de confirmação.

**Why this priority**: sem isto, a redução de perguntas da história 1 deixa o operador rápido e
ainda inseguro. Depende da 1 para não competir com ela por espaço na tela.

**Independent Test**: percorrer as telas de Classificação, Distribuição, Corte e Ocupação
verificando que cada termo do domínio interno tem definição visível no primeiro uso.

**Acceptance Scenarios**:

1. **Given** a tela de distribuição de uma Etapa, **When** o presidente vê a ação de consolidar,
   **Then** a tela declara o que a consolidação produz **antes** de ele acionar a ação.
2. **Given** a etapa de Classificação, **When** o elaborador lê o que é um marco, **Then** a tela
   explica **por que** a Etapa pertence ao Edital e a ordem pertence ao Perfil.
3. **Given** as telas de corte e de ocupação, **When** o operador encontra os termos **recorte**,
   **geração** e **faixa**, **Then** cada um aparece definido no primeiro uso da tela.

---

### User Story 3 - Compor um Edital de muitos Perfis sem repetir a mesma declaração (Priority: P3)

Um Edital com sete polos declara **uma** regra de sorteio — o mesmo algoritmo, a mesma fonte, a
mesma ocorrência — e não sete. O elaborador declara o método uma vez e cada marco o referencia.

**Why this priority**: afeta os Editais grandes da amostra, que são minoria em número e maioria em
vagas. É também o único item desta spec que altera onde um dado normativo mora, e por isso carrega
mais risco que os anteriores.

**Independent Test**: compor um Edital com sete Perfis e marcos de sorteio, contando quantas vezes a
mesma regra precisa ser declarada.

**Acceptance Scenarios**:

1. **Given** um Edital com mais de um marco que ordena por sorteio, **When** o elaborador declara o
   método, **Then** ele o declara **uma vez** e cada marco o referencia.
2. **Given** um Edital em que um marco precise de método distinto dos demais, **When** o elaborador
   compõe esse marco, **Then** o sistema permite que ele divirja do método comum, e o registra como
   divergência explícita.

---

### Edge Cases

- Um marco de sorteio **não enumera Etapa** (o sorteio precede a análise documental). A pergunta de
  entrada precisa tornar isso possível sem exigir uma Etapa artificial — hoje a validação a exige,
  contradizendo a própria ajuda da tela.
- Um Perfil ganha a **primeira** Modalidade depois de o marco já estar composto: as perguntas que
  estavam ocultas passam a ser pertinentes e precisam aparecer sem que o já declarado se perca.
- Um marco **deixa** de ordenar por sorteio e passa a ordenar por pontuação, ou o contrário: o que
  foi declarado para a forma anterior não pode desaparecer em silêncio.
- Um Edital existente, composto antes desta feature, é **retificado**: os valores já declarados
  prevalecem sobre qualquer padrão novo.
- A quantidade de Etapas enumeradas passa de uma para duas: combinação e normalização deixam de ser
  dedutíveis e precisam ser perguntadas, sem invalidar o que o marco já publicava.

## Requirements *(mandatory)*

### Functional Requirements

#### A pergunta de entrada e a revelação progressiva

- **FR-413**: O sistema DEVE, ao acrescentar um marco classificatório, perguntar primeiro **como a
  ordem daquele marco é produzida**, com as alternativas disponíveis no domínio, antes de apresentar
  qualquer campo sobre o funcionamento do marco.
- **FR-414**: O sistema DEVE apresentar os campos do método de sorteio **somente** quando a resposta
  a FR-413 indicar que a ordem nasce de sorteio.
- **FR-415**: O sistema DEVE apresentar as declarações de combinação de pontuações e de normalização
  **somente** quando o marco enumerar **duas ou mais** Etapas.
- **FR-416**: Quando o marco enumerar exatamente **uma** Etapa, o sistema DEVE declarar, em texto
  visível, que a pontuação combinada é a daquela Etapa, e NÃO DEVE perguntar combinação nem
  normalização.
- **FR-417**: O sistema DEVE apresentar as declarações sobre qual Modalidade é a da ampla
  concorrência e sobre reversão de vaga reservada **somente** depois de o Perfil declarar ao menos
  uma Modalidade de Concorrência.
- **FR-418**: O sistema DEVE preservar o que já foi declarado quando uma resposta anterior muda e
  torna outros campos pertinentes ou impertinentes, e NÃO DEVE descartar declaração em silêncio.

#### Padrões e derivação

- **FR-419**: O sistema DEVE oferecer valor padrão editável para casas decimais e para arredondamento
  do marco, e esse padrão DEVE corresponder ao praticado nos Editais de referência do projeto.
- **FR-420**: O sistema DEVE derivar o código e a denominação iniciais do marco a partir do Perfil a
  que ele pertence, mantendo ambos editáveis pelo elaborador.
- **FR-421**: Valor padrão e valor derivado NÃO DEVEM ser aplicados a conteúdo já declarado de Edital
  existente, inclusive durante Retificação.

#### O conceito nomeado onde a decisão acontece

- **FR-422**: O sistema DEVE apresentar, na tela onde a ação de consolidar é oferecida, o que a
  consolidação produz — antes de a ação ser acionada.
- **FR-423**: O sistema DEVE explicar, na etapa de Classificação, por que a Etapa de Avaliação
  pertence ao Edital enquanto a ordem classificatória pertence ao Perfil de Vaga.
- **FR-424**: O sistema DEVE apresentar definição visível, no primeiro uso de cada tela, para os
  termos **recorte**, **geração** e **faixa**.
- **FR-425**: As definições exigidas por FR-422 a FR-424 DEVEM usar a linguagem ubíqua do projeto e
  NÃO DEVEM introduzir termo novo para conceito já nomeado.

#### A ajuda ancorada, sem ajuda dentro do cartão

- **FR-426**: O bloco de ajuda de uma etapa NÃO DEVE ser apresentado enquanto não existir ao menos um
  item ao qual ele se refira.
- **FR-427**: O sistema DEVE permitir navegar de cada item do bloco de ajuda para o campo que ele
  explica.
- **FR-428**: O sistema NÃO DEVE apresentar texto de ajuda visível dentro dos cartões de composição,
  preservando a decisão já tomada pelo projeto; o equivalente textual para tecnologia assistiva DEVE
  ser mantido.

#### O método declarado uma vez

- **FR-429**: O sistema DEVE permitir que o método de sorteio seja declarado uma única vez para o
  Edital e referenciado por cada marco que ordena por sorteio.
- **FR-430**: O sistema DEVE permitir que um marco declare método divergente do comum do Edital, e
  DEVE registrar essa divergência de forma explícita no conteúdo normativo.
- **FR-431**: A mudança introduzida por FR-429 NÃO DEVE alterar o conteúdo normativo já publicado de
  Editais existentes.

### Key Entities

- **Marco classificatório**: regra que produz a ordem entre participantes de um Perfil de Vaga.
  Ganha, nesta feature, uma **forma de produção da ordem** declarada explicitamente — o que hoje é
  inferido pela presença ou ausência do bloco de método de sorteio.
- **Método de sorteio**: conjunto normativo que torna o sorteio auditável. Passa a poder pertencer ao
  **Edital**, referenciado pelos marcos, em vez de ser declarado por marco.
- **Perfil de Vaga**: permanece como está. Muda apenas **quando** suas declarações sobre ampla
  concorrência e reversão são apresentadas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-138**: Compor o marco do Edital canônico — um Perfil, três vagas, uma Etapa classificatória,
  sem Modalidade — exige responder **menos de 10 perguntas**, contra os 28 controles apresentados
  hoje.
- **SC-139**: Nenhuma pergunta apresentada ao elaborador na composição de um marco tem resposta
  **dedutível** do que ele já declarou.
- **SC-140**: Compor um Edital com sete Perfis que ordenam por sorteio exige declarar a regra do
  sorteio **uma vez**, contra as sete de hoje.
- **SC-141**: Cada termo do vocabulário interno usado na composição e na condução — marco
  classificatório, consolidação, recorte, geração, faixa — tem definição visível no primeiro uso da
  tela em que aparece.
- **SC-142**: Um Edital composto antes desta feature mantém, após ela, exatamente o mesmo conteúdo
  normativo publicado.

## Assumptions

- **Os valores padrão de FR-419 são os praticados na amostra**: duas casas decimais e arredondamento
  meio para cima, observados nos Editais de referência do projeto. Se a amostra indicar outro
  padrão, o requisito segue válido e o valor muda.
- **A decisão de não levar ajuda visível para dentro dos cartões permanece.** Esta spec a respeita e
  ataca a distância entre ajuda e campo por ancoragem, não por realocação.
- **A linguagem ubíqua não muda.** Nenhum conceito é renomeado; o que muda é onde e quando ele é
  apresentado. "Perfil de Vaga" em particular permanece — a auditoria confirmou que o termo é do
  domínio, e aparece nos Editais reais do Cefor.
- **A contagem de perguntas de SC-138 considera controles efetivamente apresentados** ao elaborador
  na composição de um marco, excluindo os que permanecem ocultos por não serem pertinentes.

## Out of Scope

Os itens abaixo vieram da mesma auditoria e **não** pertencem a esta feature. Registrá-los aqui é
insumo de priorização, não priorização — a ordem é do usuário.

- **Executabilidade do Edital** — impedir que se publique Edital que o sistema não consegue executar
  (Perfil sem marco, sorteio sem método publicado, reserva sem via de apuração), e confrontar fontes
  normativas entre si. É a spec de maior severidade da auditoria, e é independente desta.
- **Navegação derivada da capacidade** e a recusa que explica — inclusive o 404 sem mensagem.
- **Renderizador normativo único** nas telas de ato, homologação e publicação.
- **Instrução do recurso** e acesso do titular à motivação do resultado.
- **Trabalho por recorte** — alocação e distribuição que conheçam Perfil e Modalidade.
- **Corte, ocupação e convocação** — a cauda do processo.
- **Barema com pontuação por critério** e **cascata de grupos de prioridade**: dependem de decisão de
  governança ainda não tomada.
- **Perfil de Vaga como vaga de trabalho** (carga horária, remuneração, atribuições) e ausência de
  turma, polo e horário: é questão de modelo, não de composição.

## Conformidade com a Constituição

- **Princípio I — Linguagem Ubíqua**: a feature não cria nem renomeia conceito; torna visível, no
  ponto de uso, o significado dos que já existem. FR-425 impede que a solução introduza termo novo.
- **Princípio VI — Completude de Jornada**: a capacidade entregue é observável na jornada de quem
  elabora, pela interface administrativa, e demonstrável de ponta a ponta — compor um Edital
  completo respondendo menos perguntas, sem recurso a shell, banco ou canal alheio.
- **Princípio V — Simplicidade**: a feature **remove** perguntas em vez de acrescentar explicação, e
  seu critério de aceitação é uma contagem que só cai.
- **Integridade normativa**: FR-421, FR-431 e SC-142 garantem que nada do já publicado se altera.
