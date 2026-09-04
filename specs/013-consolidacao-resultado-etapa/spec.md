# Feature Specification: Consolidação do Resultado da Etapa

**Feature Branch**: `claude/spec-013-consolidacao-resultado-a0665b`

**Created**: 2026-09-02

**Status**: Draft

**Input**: Consolidar as avaliações concluídas em um Resultado por inscrição e Etapa, com
prontidão visível, consequência eliminatória, operação em lote, proveniência e progressão para a
Etapa seguinte, sem inventar uma regra de combinação que o Edital não publicou.

## 1. O que a 012 entregou, e que a 013 herda como contrato

A 012 encerrou a organização e a execução da avaliação. Esta feature começa depois dela e não
redefine seus conceitos:

- `avaliacoes_previstas(etapa)` é a única leitura da quantidade normativa; ausência significa uma
  avaliação por inscrição;
- `avaliacoes_elegiveis(...)` entrega somente Avaliações concluídas sob Atribuição ativa, cada uma
  com autoria, instante e Versão Consolidada; `avaliacoes_inelegiveis(...)` explica, com ato, autor
  e motivo, o que saiu desse conjunto;
- `resumo_da_etapa(...)` já agrega inscrições submetidas, cobertura e conclusões; a prontidão da
  013 é um acréscimo a esse resumo, não um segundo painel concorrente;
- Participante nasce do universo de inscrições `SUBMETIDA` do Edital. A partir da segunda Etapa,
  esta feature subtrai quem foi eliminado em Etapa anterior e, depois que a imediatamente anterior
  produzir Resultado, exige habilitação nela — as duas regras de D-003;
- Avaliação possui apenas `RASCUNHO` e `CONCLUIDA`, e conclui em **uma de duas formas** publicadas
  pela Etapa: `PONTUADA`, com pontuação total, ou `DECISORIA`, com sentido `FAVORAVEL` ou
  `DESFAVORAVEL` (012, D-008). Nas duas há parecer, e a forma sob a qual se concluiu fica gravada na
  própria conclusão. Critérios, itens e barema estruturado não existem no domínio e não são
  pressupostos aqui;
- a quantidade prevista, a pontuação máxima, a forma da conclusão e os rótulos da forma decisória são
  conteúdo publicado da Etapa, na versão canônica 6. A 013 lê esse conteúdo e **não cria incremento
  normativo próprio** — nem o primeiro nem o segundo são dela;
- reabertura e impedimento preservam o histórico, mas hoje podem substituir ou retirar uma
  conclusão do conjunto elegível. A 013 fecha essa porta quando a conclusão já produziu Resultado —
  sem impedir que o impedimento seja registrado, conforme D-002.

> As avaliações de uma inscrição existem, têm autoria e são confiáveis; falta transformá-las em
> consequência.

## 2. Decisões fechadas antes do planejamento

### D-001 — A V1 não inventa média

A Etapa declara quantas avaliações são previstas e qual é a pontuação máxima, mas não declara como
combinar duas ou mais avaliações. Peso da Etapa não é peso entre avaliadores, e média aritmética
não é regra implícita.

Por isso, a V1 consolida somente Etapa cuja leitura normativa resulte em
`evaluations_per_registration == 1`. **A consolidação é cópia, e não cálculo**: na forma pontuada, a
pontuação consolidada é exatamente o total da única Avaliação elegível, sem média, arredondamento ou
ponderação; na forma decisória, o sentido consolidado é exatamente o sentido dela. A recusa de
inventar regra de combinação vale igual nas duas — dois sentidos opostos são tão insolúveis quanto
duas notas diferentes, e por isso o impedimento é o mesmo. Etapa que preveja mais de uma avaliação
fica em impedimento explícito: “o Edital prevê N avaliações, mas não declara como combiná-las”.

Uma regra de combinação para múltiplas avaliações exigirá incremento canônico próprio — forma
publicada, validação, elaboração, documento e Retificação — e pertence a uma evolução posterior.

### D-002 — Consolidar fecha as entradas da decisão

`ResultadoEtapa` é uma consequência administrativa imutável. Depois que existe para uma inscrição
e Etapa, a Avaliação que o fundamentou não pode ser **reaberta**: reabrir muda a conclusão, e mudar
a conclusão tornaria o Resultado uma afirmação sobre uma pontuação — ou sobre um deferimento — que
não existe mais. A reabertura é
recusada por inteiro, antes de qualquer efeito, nomeando o Resultado que protege a Avaliação.

A V1 não oferece anulação nem reconsolidação. Aceitar mudança da entrada e conservar Resultado
desatualizado seria uma anulação silenciosa; aceitar mudança automática do Resultado apagaria a
autoria do ato original. Ambas ficam fora.

**O que essa porta fechada custa, dito por extenso.** Sem anulação, um Resultado fundado em
Avaliação depois reconhecida como defeituosa — erro material, conflito de interesse descoberto
tarde — não tem remédio dentro do sistema na V1. A spec aceita esse custo e não o disfarça: a
consolidação é ato deliberado da presidência sobre uma Etapa que ela considera encerrada, e não
efeito automático da última conclusão.

**O impedimento, porém, não é recusado nem aparado — ele se aplica por inteiro.** O Impedimento da
012 existe para que a razão fique escrita, e ele produz efeito inativando a Atribuição, que é o que
a cadeia de autorização consulta. Preservar a Atribuição que fundamentou um Resultado, como uma
redação anterior desta decisão previa, deixaria a pessoa **declarada impedida com acesso mantido**
à inscrição e aos documentos dela: a autorização não pergunta por impedimento, ela depende de o
impedimento ter inativado a Atribuição. Seria proteger a proveniência de um Resultado ao custo de
manter aberta a porta que o impedimento existe para fechar.

Logo: o impedimento registra, inativa tudo o que alcança — inclusive a Atribuição da Avaliação
fonte — e **não toca o Resultado**, que é histórico e permanece. O que muda é a leitura da
proveniência: um Resultado cuja fonte foi depois alcançada por impedimento **exibe esse fato ao
lado da decisão**, porque quem consulta precisa saber que a origem foi contestada depois. A
invariante correspondente deixa de dizer "a fonte continua elegível" e passa a dizer **"a fonte era
elegível quando consolidada"**, que é o que de fato se afirma sobre um ato passado.

O impedimento superveniente é, assim, o único caminho pelo qual a V1 registra que um Resultado
nasceu de origem contestada. Ele não o corrige — corrigir exige anulação, que é feature posterior —
mas impede que a contestação fique invisível.

### D-003 — Eliminação altera o conjunto da Etapa seguinte

A 013 não deixará a tela da Etapa seguinte contar quem a Etapa anterior eliminou.

São **duas regras distintas**, e confundi-las foi o defeito de uma redação anterior. Uma é
absoluta; a outra é que depende do gate.

**Regra 1 — a eliminação é definitiva, e alcança todas as Etapas seguintes.** Inscrição com
Resultado `ELIMINADA` em **qualquer** Etapa anterior — não apenas na imediatamente anterior — está
fora de todas as posteriores, sempre, sem gate e sem exceção. Uma eliminação conhecida não deixa de
ser conhecida porque a Etapa intermediária ainda não foi consolidada: eliminada na Etapa 1, a
inscrição não reaparece na Etapa 3 enquanto a Etapa 2 não fecha.

**Regra 2 — a exigência de habilitação vale sobre a Etapa imediatamente anterior, e só depois que
ela começa a produzir Resultado.** É aqui, e somente aqui, que o gate incide:

- Na primeira Etapa, participam todas as inscrições submetidas do Edital.
- Enquanto a Etapa imediatamente anterior não possuir nenhum Resultado, a Etapa seguinte conserva
  o conjunto da 012 — todas as submetidas, menos as eliminadas pela Regra 1 —, e a distribuição
  continua podendo ser preparada antes de a Etapa anterior fechar. É esse gate que impede a 013 de
  quebrar o que hoje funciona: sem ele, Etapa anterior de leitura múltipla, que D-001 não consolida,
  deixaria a Etapa seguinte permanentemente sem participantes, e nenhum Edital de segunda leitura
  passaria da primeira Etapa.
- A partir do primeiro Resultado da Etapa anterior, participa a inscrição submetida que possua
  Resultado `HABILITADA` nela, segundo a ordem publicada vigente.
- Com a exigência vigente, ausência do Resultado anterior mantém a inscrição em “aguardando Etapa
  anterior”; ela não conta como participante pronta, não pode ser distribuída e não concede acesso
  por Atribuição que tenha sido criada antecipadamente. Atribuição criada enquanto a exigência
  estava dormente é preservada e volta a autorizar quando o Resultado habilitador existir.

A assimetria é deliberada: exigir habilitação é uma condição que o sistema ainda não tem como
avaliar antes da consolidação, e por isso espera; reconhecer eliminação é um fato que ele já tem, e
esperar por ele seria descartá-lo.

**Como isso é verificado.** A 012 fechou a cadeia de autorização em duas condições e manteve o
impedimento fora dela por uma razão de escala: somá-lo custaria uma verificação por linha em toda
listagem, e ela protege essa invariante agindo na escrita, nunca na leitura. A progressão não
reabre essa porta. Os dois conjuntos — as eliminadas em Etapas anteriores e as habilitadas na
imediatamente anterior — são resolvidos **uma vez por listagem**, como a 011 já faz com as Etapas
autorizadas, e a cadeia individual ganha uma verificação de par apenas na rota de item. Nenhuma
listagem da 013 ou da 012 passa a decidir autorização linha a linha.

A superfície alcançada é maior que a organização da Etapa, e precisa estar dita: a distribuição, a
Mesa do avaliador, a inscrição como instrumento de trabalho, a entrega de documento e a navegação
“próxima pendente” consultam o mesmo conjunto. Deixar qualquer uma de fora manteria aberta uma porta
para inscrição eliminada, e uma delas — “próxima pendente” — entregaria a inscrição sem que ninguém
pedisse por ela.

Essa progressão não é classificação global: não ordena pessoas, não aplica pesos entre Etapas, não
distribui vagas e não publica resultado. É somente a consequência local do Resultado anterior.
Atribuições e Avaliações eventualmente registradas antes de a consequência ser conhecida são
preservadas como histórico; não autorizam trabalho nem integram consolidação enquanto a inscrição
estiver fora do conjunto.

### D-004 — Prontidão é um delta sobre a organização existente

A presidência continua usando uma única visão da Etapa. O resumo existente ganha contagens de
participantes, aguardando progressão, eliminadas anteriormente, Resultados existentes, prontas para
consolidar e impedidas por motivo. Cobertura, conclusão, elegibilidade, compatibilidade normativa e
regra disponível são dimensões da mesma população e precisam fechar aritmeticamente.

Não nasce um “painel de Resultado” paralelo que conte a Etapa por regra diferente.

### D-005 — Compatibilidade é da norma, não da linha de versão

Versões Consolidadas diferentes podem descrever a mesma regra da Etapa. A compatibilidade compara
o conteúdo normativo da Etapa que governou a Avaliação com o conteúdo vigente no momento da
consolidação, e não a identidade da Versão Consolidada.

Para a mesma identidade de Etapa, são comparados semanticamente **os campos que podem mudar o
Resultado**: forma da conclusão, caráter eliminatório, nota mínima, quantidade de avaliações e
pontuação máxima. Ausência de quantidade equivale a `1`; ausência de máxima equivale a “não
declarada”; ausência de forma equivale a `PONTUADA`, conforme os leitores herdados da 012.

**A forma entra na comparação, e é o campo mais grave dela.** Uma Retificação que trocasse
`PONTUADA` por `DECISORIA` sem ser detectada faria a 013 fundamentar Resultado numa conclusão cuja
espécie a norma vigente já não admite — não uma nota fora do limite novo, mas uma nota onde a norma
não prevê nota nenhuma. **Os rótulos ficam de fora**, pelo mesmo critério que mantém o nome fora:
trocar "Deferido" por "Deferido(a)" não altera consequência alguma, e compará-los faria correção de
redação bloquear consolidação pendente.

**Nome, vínculo de cronograma, peso, caráter classificatório e ordem ficam de fora, de propósito.**
Nenhum deles altera a pontuação ou a consequência que esta feature produz: peso e caráter
classificatório pertencem à composição entre Etapas, que a §5 recusa; nome e cronograma são
descrição. Compará-los faria a correção de uma vírgula no nome da Etapa impedir toda consolidação
pendente e exigir que avaliações corretas voltassem à reabertura — bloqueio sem causa normativa, que
é o oposto do que esta decisão existe para evitar. A ordem é insumo da progressão de D-003, lida
sempre do conteúdo vigente, e não critério de compatibilidade: mudá-la muda qual é a Etapa anterior,
não a validade da Avaliação.

Mudanças fora dessa Etapa não criam incompatibilidade. Divergência em qualquer campo comparado
impede a consolidação daquela inscrição e indica que a Avaliação precisa voltar ao fluxo de
reabertura antes de produzir Resultado.

### D-006 — Resultado pendente é ausência, não estado gravado

`CONSOLIDADO` é a existência de `ResultadoEtapa`; `PENDENTE` é calculado para participante sem essa
linha. Não há coluna de workflow para duplicar um fato derivado. `HABILITADA` e `ELIMINADA`, por sua
vez, são a consequência materializada pelo ato e pertencem ao Resultado.

### D-007 — O lote herda o mecanismo já entregue

Consolidação usa o mesmo invólucro transacional e idempotente dos comandos da comissão, com chave
obrigatória, desfecho completo preservado e um evento de auditoria para cada Resultado criado. O
nome canônico do ato é `resultado:consolidar`. A autorização é a mesma da reabertura pela
presidência; não nasce papel, capacidade administrativa ou modelo paralelo.

### D-008 — O Resultado oficializa as duas formas de conclusão, e não infere consequência

*Contraparte, nesta spec, da D-008 da `specs/012`. As duas foram tomadas no mesmo movimento, em
03/09/2026: a 012 deixou de pressupor que avaliar produz número, e esta feature deixaria o fluxo
quebrado no meio se continuasse pressupondo que o Resultado é uma nota — o avaliador concluiria
"indeferido" e a Etapa nunca produziria consequência.*

**1 · O Resultado guarda a conclusão conforme a forma**, pela mesma estrutura e pelo mesmo motivo da
conclusão que o fundamenta: pontuação quando a fonte é pontuada, sentido quando é decisória, e a
forma na própria linha para que a verificação continue local. `ResultadoEtapa` é append-only por
privilégio e por trigger, e a migração tem a restrição de implantação que isso impõe.

**2 · A conferência de coerência com a fonte passa a comparar forma, pontuação e sentido — os três,
sempre.** Ela é o coração da garantia desta feature: o Resultado não é confiado à promessa da
aplicação. O que ela exige é que o Resultado afirme exatamente o que a Avaliação fonte afirmou, na
forma em que ela o afirmou.

**A comparação é incondicional, e não alterna por forma.** A primeira redação desta decisão dizia
"alterna", e estava errada por uma razão que só aparece no SQL: numa conclusão decisória os dois
lados da pontuação são nulos, e `IS DISTINCT FROM` resolve nulo contra nulo como **iguais** — uma
conferência que alternasse por forma aprovaria qualquer sentido em silêncio. Comparar os três
incondicionalmente é mais forte e mais simples: se as formas são iguais, alternar seria redundante;
se divergem, o primeiro teste já reprova.

**3 · A consequência é lida da forma, e nunca inferida.** Na forma pontuada, a regra atual permanece
intacta: Etapa eliminatória elimina abaixo da mínima, e Etapa sem caráter eliminatório materializa e
habilita. Na forma decisória, **em Etapa eliminatória**, `DESFAVORAVEL` produz `ELIMINADA` e
`FAVORAVEL` produz `HABILITADA`. O motivo exibível cita o rótulo que o Edital publicou — quem lê o
Resultado lê "Indeferido", e não `DESFAVORAVEL`.

**4 · Etapa decisória e não eliminatória não é consolidável, e a recusa diz por quê.** É o caso que
os três Editais não exercitam, e ele não tem resposta óbvia: um desfavorável que habilita é absurdo,
e um desfavorável que elimina aplica caráter eliminatório que o Edital não publicou. As duas saídas
que evitariam a recusa afirmariam norma que ninguém escreveu — fazer o sentido carregar a
consequência por si, ou exigir caráter eliminatório de toda Etapa decisória, proibindo na elaboração
o que um Edital poderia legitimamente publicar.

Por isso a resposta é a que esta spec já dá no caso simétrico:

```text
eliminatória, sem nota mínima  → regra insuficiente: não publicou o que a nota produz
decisória, não eliminatória    → regra insuficiente: não publicou o que o sentido produz
```

O impedimento é da **Etapa inteira**, como o outro, e aparece na prontidão antes que alguém tente
consolidar. Em uma frase: *recebi uma decisão desfavorável, e o Edital não publicou que ela elimina;
não posso inventar o efeito.* **Na forma decisória é o caráter eliminatório que dá consequência à
decisão** — o mesmo papel que ele já tem na forma pontuada, dito para a outra forma.

**5 · Nota mínima e pontuação máxima não se aplicam à forma decisória**, e a Etapa não as publica. A
recusa de FR-014 por "eliminatória sem nota mínima" passa a valer somente na forma pontuada: análise
documental eliminatória, decisória e sem nota mínima é normal nos Editais 35 e 57, e recusá-la seria
o sistema procurando um número que a norma nunca teve.

**6 · A progressão não muda.** `ELIMINADA` é `ELIMINADA`, qualquer que seja a forma que a produziu, e
D-003 continua valendo palavra por palavra. É o limite que mantém esta revisão estreita: generalizar
a 013 é ensiná-la a oficializar as duas conclusões que já existem, e não trazer classificação, vagas,
sorteio, recurso ou convocação para dentro dela.

**7 · O comportamento da forma pontuada é invariante de não regressão.** Todo Resultado hoje gravado
é pontuado, e nenhum deles muda de comportamento por causa desta revisão.

## 3. Problema

Hoje a presidência consegue distribuir, acompanhar e concluir avaliações confiáveis, mas precisa
copiar notas para fora do sistema para responder perguntas básicas: quais inscrições terminaram a
Etapa, qual foi o total, quem foi eliminado e quem pode seguir. Isso reabre exatamente o risco que
a Mesa eliminou: planilha sem regra reproduzível, seleção manual das avaliações e ausência de ato
identificável.

A feature deve permitir que a presidência reconheça a prontidão, consolide em lote e consulte o
Resultado de cada inscrição sem antecipar classificação, publicação ou recurso.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Enxergar a prontidão real da Etapa (Priority: P1)

Como presidente, quero ver na organização da Etapa quantas inscrições podem ser consolidadas e por
que as demais não podem, para corrigir pendências sem conferir avaliação por avaliação.

**Why this priority**: sem uma leitura confiável da prontidão, a presidência não sabe se o lote é
seguro nem qual ação antecede a consolidação.

**Independent Test**: preparar inscrições sem avaliação, com avaliação elegível, com versão
incompatível, aguardando Etapa anterior e já eliminadas; abrir a organização e conferir contagens,
filtros e motivos que particionam exatamente a população.

**Acceptance Scenarios**:

1. **Given** uma primeira Etapa de leitura única com inscrições submetidas em estados diferentes,
   **When** a presidência abre sua organização, **Then** o mesmo resumo já usado para cobertura
   mostra Resultados, prontas e impedidas por motivo, sem dupla contagem.
2. **Given** uma Etapa posterior, **When** há inscrições habilitadas, eliminadas e ainda sem
   Resultado anterior, **Then** apenas as habilitadas compõem participantes e as demais aparecem
   separadas pelo motivo correto.
3. **Given** uma Etapa que prevê duas avaliações, **When** a presidência consulta a prontidão,
   **Then** a Etapa inteira informa que a regra de combinação não foi publicada e nenhuma linha é
   apresentada como pronta.

---

### User Story 2 — Consolidar Resultados em lote (Priority: P1)

Como presidente, quero consolidar várias inscrições prontas em um ato confirmado, para transformar
as avaliações concluídas em consequência rastreável sem transcrever pontuações.

**Why this priority**: é a capacidade central da 013 e elimina a planilha que hoje produz o
resultado à margem do sistema.

**Independent Test**: selecionar num único envio inscrições prontas, pendentes e já consolidadas;
confirmar e verificar que as prontas recebem Resultado, as demais são recusadas com motivo e a
repetição da mesma chave devolve exatamente o desfecho original.

**Acceptance Scenarios**:

1. **Given** uma Etapa eliminatória de leitura única, nota mínima 60 e Avaliações elegíveis de 75,
   60 e 59, **When** a presidência consolida o lote, **Then** os totais são preservados exatamente
   e as consequências são, respectivamente, `HABILITADA`, `HABILITADA` e `ELIMINADA`.
2. **Given** um lote com duas inscrições prontas e uma sem conclusão elegível, **When** o ato é
   confirmado, **Then** dois Resultados são criados e uma recusa nomeia a conclusão ausente.
3. **Given** um lote já concluído, **When** o mesmo ator repete a mesma chave e conteúdo, **Then**
   recebe o desfecho original sem Resultado nem evento novo; conteúdo diferente com a mesma chave
   é conflito.

---

### User Story 3 — Prosseguir somente com quem foi habilitado (Priority: P2)

Como presidente, quero que a Etapa seguinte use os Resultados da anterior para definir seus
participantes, para que uma eliminação produza efeito operacional e não seja apenas um rótulo.

**Why this priority**: uma consequência que não altera o fluxo seguinte deixa a operação e a
proteção de dados em contradição com o Resultado registrado.

**Independent Test**: consolidar a primeira Etapa com uma inscrição habilitada e outra eliminada;
abrir a distribuição e a Mesa da segunda Etapa e comprovar que somente a habilitada pode ser
distribuída, contada e acessada.

**Acceptance Scenarios**:

1. **Given** Resultado anterior `HABILITADA`, **When** a segunda Etapa é organizada, **Then** a
   inscrição integra participantes e pode receber Atribuição.
2. **Given** Resultado anterior `ELIMINADA`, **When** se tenta distribuir ou abrir a inscrição na
   segunda Etapa, **Then** a operação é recusada sem revelar dados e a inscrição é contabilizada
   entre as eliminadas anteriormente.
3. **Given** uma Etapa anterior que já produziu Resultados, uma inscrição ainda sem o seu e uma
   Atribuição criada antecipadamente, **When** o avaliador abre a Mesa ou manipula o identificador
   da inscrição, **Then** não obtém acesso; o registro antecipado permanece preservado e volta a
   autorizar se o Resultado habilitador aparecer.

---

### User Story 4 — Consultar a decisão e sua origem (Priority: P2)

Como presidente ou auditor, quero consultar cada Resultado com a Avaliação, a regra, o autor e o
instante que o fundamentaram, para reconstruir a decisão sem recorrer a planilhas ou logs técnicos.

**Why this priority**: a consequência afeta direito do candidato e precisa ser demonstrável mesmo
depois de Retificações ou mudanças na comissão.

**Independent Test**: consolidar, publicar uma Retificação não retroativa e remover o avaliador da
comissão; consultar o Resultado e reproduzir total, consequência, fonte normativa e duas autorias.

**Acceptance Scenarios**:

1. **Given** um Resultado consolidado, **When** a presidência ou auditoria o consulta, **Then** vê a
   pontuação, consequência, Avaliação fonte, versão normativa, quem avaliou, quem consolidou e
   quando cada ato ocorreu.
2. **Given** a Avaliação fonte de um Resultado, **When** a presidência tenta reabri-la, **Then** o
   ato é recusado antes de alterar qualquer registro e a mensagem identifica o Resultado protetor.
3. **Given** um impedimento que alcança a Avaliação fonte de um Resultado e outras Atribuições da
   mesma pessoa, **When** a presidência o registra, **Then** o impedimento é criado, **todas** as
   Atribuições alcançadas são inativadas, a pessoa perde acesso a todas elas, o Resultado permanece
   com pontuação e consequência intactas, e a consulta dele passa a exibir a contestação
   superveniente.

### Edge Cases

- Nota exatamente igual à mínima habilita; comparação decimal não arredonda o valor.
- Etapa **pontuada** eliminatória sem nota mínima não possui regra suficiente e não pode ser
  consolidada; a mesma ausência numa Etapa decisória é normal, e não impede nada.
- Etapa pontuada não eliminatória materializa total e `HABILITADA`; eventual nota mínima não elimina.
- Etapa **decisória** não eliminatória não possui regra suficiente e não pode ser consolidada: o
  Edital não publicou o que o sentido desfavorável produz, e o sistema não infere o efeito (D-008).
- Etapa decisória eliminatória consolida `DESFAVORAVEL` como `ELIMINADA` e `FAVORAVEL` como
  `HABILITADA`, e o motivo exibível usa os rótulos publicados, nunca o enum interno.
- Zero ou mais de uma Avaliação elegível quando a regra prevê uma é inconsistência explícita; o
  sistema não escolhe uma linha nem consolida silenciosamente.
- Retificação que altera outro trecho do Edital não impede consolidação; alteração normativa da
  própria Etapa impede enquanto não houver Resultado e não reescreve Resultado já existente.
- Retificação que remove a Etapa antes da consolidação torna a operação indisponível; remoção
  posterior não apaga Resultados históricos.
- Com a exigência de habilitação vigente, Resultado anterior ausente impede progressão; eliminação
  anterior não é tratada como pendência, e vale mesmo quando a exigência está dormente.
- Mudança de ordem publicada antes da consolidação recalcula qual é a Etapa anterior; Resultados já
  materializados permanecem históricos e não são reinterpretados.
- Um impedimento que alcança várias Atribuições é registrado e aplicado a todas, inclusive à que
  fundamenta Resultado; o desfecho nomeia os Resultados cuja fonte passou a ser contestada.
- Inscrição eliminada na Etapa 1 não reaparece na Etapa 3 porque a Etapa 2 ainda não produziu
  Resultado: a eliminação vale para todas as posteriores, e o gate incide apenas sobre a exigência
  de habilitação na imediatamente anterior.
- Etapa anterior sem nenhum Resultado — porque prevê mais de uma avaliação, ou porque a consolidação
  ainda não começou — não bloqueia a Etapa seguinte: a exigência de habilitação fica dormente e a
  distribuição segue como na 012, exceto pelas eliminadas em Etapas anteriores, que continuam fora.
- Retificação que corrige nome, cronograma, peso, caráter classificatório ou os rótulos da forma
  decisória não cria incompatibilidade, porque nenhum deles altera a conclusão ou a consequência
  desta feature.
- Retificação que troca a **forma** da Etapa depois de conclusões gravadas cria incompatibilidade e
  impede consolidar aquelas conclusões: a conclusão histórica continua íntegra e interpretável sob a
  forma que a governou, e é a consequência — não o registro — que fica retida (012, EC-021).
- Dois lotes concorrentes sobre a mesma inscrição produzem no máximo um Resultado; o perdedor
  recebe desfecho explícito, sem evento duplicado.

## Requirements *(mandatory)*

### Functional Requirements

#### Participação e prontidão

- **FR-001**: A primeira Etapa DEVE considerar como participantes exatamente as inscrições
  submetidas do Edital.
- **FR-002**: Toda leitura da quantidade prevista DEVE usar o leitor único herdado da 012, com o
  significado que a §1 registra; a 013 NÃO DEVE duplicar padrão ou configuração.
- **FR-003**: Inscrição com Resultado `ELIMINADA` em QUALQUER Etapa anterior pela ordem publicada
  vigente NÃO DEVE participar de nenhuma Etapa posterior, independentemente de a Etapa
  imediatamente anterior já possuir Resultado.
- **FR-004**: Etapa posterior cuja Etapa imediatamente anterior já possua ao menos um Resultado DEVE
  exigir, além disso, Resultado `HABILITADA` nessa Etapa imediatamente anterior. Enquanto ela não
  possuir nenhum Resultado, a Etapa posterior DEVE conservar o conjunto da 012 — todas as inscrições
  submetidas — menos as excluídas por FR-003.
- **FR-005**: Inscrição excluída por FR-003 ou por FR-004 NÃO DEVE ser distribuível, contabilizada
  como participante, listada na Mesa, acessível na inscrição de trabalho, alcançável na entrega de
  documento nem oferecida pela navegação de próxima pendente.
- **FR-006**: A verificação de FR-003 e FR-004 DEVE ser feita por conjunto — ambos resolvidos uma
  vez por listagem — e NUNCA por linha, preservando a invariante de escala herdada da 012; a rota
  individual continua verificando o par diretamente, onde uma consulta a mais não é gargalo.
- **FR-007**: Tentativa de distribuir inscrição excluída por FR-003 ou FR-004 DEVE ser tratada como
  erro sobre o pedido, e não como recusa de linha, pela mesma classificação que a 012 já aplica a
  inscrição não submetida.
- **FR-008**: A prontidão DEVE consumir o conjunto elegível herdado da 012; Avaliação inelegível
  NÃO PODE ser escolhida por filtro alternativo, e seu motivo continua consultável pelo contrato
  herdado.
- **FR-009**: A visão existente da organização DEVE ser acrescida, e não duplicada, com totais de
  participantes, aguardando anterior, eliminadas anteriormente, pendentes, prontas, consolidadas e
  impedidas por motivo.
- **FR-010**: As contagens da mesma Etapa DEVEM formar uma partição verificável, sem inscrição em
  dois estados de prontidão nem divergência entre resumo e detalhe filtrado.
- **FR-011**: Regra disponível exige Etapa vigente de leitura única e, quando eliminatória, nota
  mínima declarada.
- **FR-012**: Cada impedimento de prontidão DEVE ter mensagem acionável: avaliação ausente,
  avaliação excedente, incompatibilidade normativa, Resultado anterior ausente, eliminação
  anterior, regra de combinação ausente ou Resultado já existente.

#### Compatibilidade e regra de consolidação

- **FR-013**: Compatibilidade DEVE comparar semanticamente os campos enumerados em D-005, tratando
  os significados legados de ausência conforme a 012, e NÃO a identidade da Versão Consolidada.
- **FR-014**: Avaliação cuja versão não contém a Etapa, ou cuja Etapa diverge da vigente em campo
  comparado, NÃO PODE produzir Resultado.
- **FR-015**: Na V1, Etapa que preveja mais de uma avaliação por inscrição DEVE ser impedida por
  inteiro, nomeando a quantidade publicada e a ausência de regra de combinação.
- **FR-016**: A conclusão consolidada DEVE ser cópia exata da conclusão da única Avaliação elegível
  — a pontuação na forma pontuada, o sentido na forma decisória —, sem média, peso, arredondamento,
  conversão entre formas ou edição pela presidência.
- **FR-017**: Etapa **pontuada** eliminatória DEVE produzir `ELIMINADA` somente quando a pontuação
  for menor que a mínima publicada; em todos os demais casos alcançáveis, DEVE produzir `HABILITADA`.
- **FR-046**: Etapa **decisória** eliminatória DEVE produzir `ELIMINADA` para `DESFAVORAVEL` e
  `HABILITADA` para `FAVORAVEL`, e o motivo registrado DEVE nomear o rótulo publicado pela Etapa.
- **FR-047**: Etapa decisória **não** eliminatória DEVE ser impedida por inteiro, por regra
  insuficiente, nomeando que o Edital não publicou o efeito do sentido desfavorável (D-008). O
  sistema NÃO PODE inferir a consequência, nem tratando `DESFAVORAVEL` como eliminação nem exigindo
  caráter eliminatório de toda Etapa decisória.
- **FR-048**: A recusa por "eliminatória sem nota mínima" DEVE valer somente na forma pontuada.
  Etapa decisória eliminatória e sem nota mínima é consolidável, e recusá-la seria procurar um número
  que a norma nunca teve.
- **FR-049**: O Resultado DEVE registrar a forma sob a qual foi consolidado, e a conferência de
  coerência com a Avaliação fonte DEVE comparar **forma, pontuação e sentido — os três,
  incondicionalmente**, e não alternar por forma. A conferência é do banco, e não da aplicação.
  Alternar aprovaria qualquer sentido na forma decisória, porque a comparação de pontuação entre dois
  nulos resolve como igualdade.

#### Lote e idempotência

- **FR-018**: A presidência DEVE consolidar uma ou várias inscrições em um único lote confirmado,
  sob o mesmo invólucro transacional e idempotente que a 012 já aplica aos atos da comissão, com
  chave obrigatória.
- **FR-019**: O lote DEVE criar Resultados para itens válidos e declarar, para cada item inválido,
  a recusa específica; erro sobre o pedido inteiro DEVE impedir qualquer criação.
- **FR-020**: O desfecho DEVE declarar criadas, recusas e motivos na mesma forma já usada pelos
  atos em lote da 012, e ficar preservado junto ao registro de idempotência, de modo que a repetição
  o devolva por inteiro em vez de um vazio.
- **FR-021**: Cada Resultado criado no lote DEVE gerar exatamente um evento de auditoria; reenviar
  o mesmo ato não cria Resultado nem evento novo e devolve o desfecho original.
- **FR-022**: Mesma chave com conteúdo diferente DEVE produzir conflito; chave diferente sobre par
  já consolidado DEVE recusar o item como já consolidado, sem tratar a tentativa como sucesso.
- **FR-023**: O lote DEVE ser atomicamente protegido contra duas consolidações concorrentes do
  mesmo par inscrição+Etapa.

#### Resultado e proveniência

- **FR-024**: DEVE existir no máximo um `ResultadoEtapa` por inscrição e Etapa, inclusive sob
  concorrência e qualquer número de reenvios.
- **FR-025**: O Resultado DEVE materializar a conclusão consolidada conforme a forma, a
  consequência, a Avaliação fonte, o instante e a identidade de quem consolidou.
- **FR-026**: A partir da Avaliação fonte, DEVE ser possível reproduzir a Versão Consolidada e os
  campos normativos que determinaram pontuação e consequência, sem usar regra atual no lugar da
  histórica.
- **FR-027**: Resultado, fonte e auditoria DEVEM distinguir autoria da Avaliação e autoria da
  consolidação.
- **FR-028**: `PENDENTE` e `CONSOLIDADO` NÃO DEVEM ser estados persistidos: são, respectivamente,
  ausência e existência do Resultado. `HABILITADA` e `ELIMINADA` são consequências persistidas.
- **FR-029**: Resultado criado NÃO PODE ser editado nem fisicamente excluído pela aplicação.

#### Fechamento das entradas

- **FR-030**: Reabertura de Avaliação que fundamenta Resultado DEVE ser recusada antes de qualquer
  mudança, mesmo com motivo, revisão e chave válidos.
- **FR-031**: Impedimento DEVE ser registrado e aplicado integralmente mesmo quando alcança
  Avaliação que fundamenta Resultado, inativando também essa Atribuição. Nenhuma Atribuição
  alcançada permanece ativa por existir Resultado.
- **FR-032**: O Resultado alcançado por impedimento superveniente NÃO DEVE ser alterado, recalculado
  nem invalidado; o desfecho do ato e a consulta do Resultado DEVEM declarar quais Resultados
  tiveram sua fonte contestada depois de consolidados.
- **FR-033**: A recusa de reabertura DEVE identificar a inscrição, a Etapa e o Resultado protetor,
  sem expor pontuação a ator não autorizado; a mesma exigência vale para a declaração de
  impedimento superveniente.
- **FR-034**: Retificação posterior NÃO DEVE reescrever, recalcular nem invalidar Resultado já
  criado; anulação e reconsolidação ficam fora da V1.

#### Autorização, consulta e proteção de dados

- **FR-035**: Consolidar DEVE usar a mesma base de autorização contextual já aplicada à reabertura;
  o ato canônico é `resultado:consolidar`, sem papel novo.
- **FR-036**: A autorização DEVE ser reavaliada dentro do ato protegido, antes de reservar a chave
  e gravar Resultados.
- **FR-037**: Presidência DEVE consultar os Resultados do Processo; auditoria autorizada DEVE poder
  reconstruí-los sem adquirir poder de consolidar.
- **FR-038**: Identificador de Edital, Etapa, inscrição, Avaliação ou Resultado NÃO PODE conceder
  acesso; escopo institucional ou vínculo divergente recebe a resposta uniforme de recurso não
  encontrado.
- **FR-039**: Respostas com Resultado individual ou dados da inscrição NÃO DEVEM ser armazenáveis
  pelo navegador e NÃO DEVEM ampliar o acesso a documentos do candidato.
- **FR-040**: Auditoria DEVE registrar ator, base autorizadora, ato, Resultado, instante,
  correlação e chave de idempotência, sem copiar pontuação, sentido ou parecer para a trilha — os
  três são conteúdo do juízo, e não registro de que houve juízo (012, FR-054).

#### Não regressão e limites

- **FR-041**: A 013 NÃO DEVE criar incremento canônico, campo de elaboração, alteração de documento
  publicado nem nova regra de Retificação.
- **FR-042**: Distribuição e Mesa da primeira Etapa DEVEM conservar o comportamento da 012 para
  toda inscrição submetida; nas seguintes, acrescentam-se apenas a exclusão por eliminação anterior
  e, depois do primeiro Resultado da Etapa imediatamente anterior, a exigência de habilitação. Nada
  mais muda, e a distribuição, a Mesa, a inscrição de trabalho, o documento e a próxima pendente
  conservam todo o resto do comportamento da 012.
- **FR-043**: A 013 NÃO DEVE alterar conteúdo, estado ou autoria de Avaliação, Atribuição,
  Impedimento, Publicação ou Versão Consolidada existente.
- **FR-044**: Peso da Etapa, caráter classificatório e conclusões de outras Etapas NÃO DEVEM compor
  o Resultado desta feature.
- **FR-050**: Nenhum comportamento da forma pontuada DEVE mudar por causa desta revisão. A
  demonstração é por **identidade de teste**: todo teste que existia antes continua existindo e
  passando, e as únicas asserções alteradas são as que fixam o literal da versão canônica ou a forma
  do conteúdo publicado, enumeradas uma a uma na entrega. Exigir contagem total idêntica seria exigir
  que a revisão não fosse testada (012, FR-124).
- **FR-045**: Nenhuma tela ou resposta da 013 DEVE afirmar colocação, aprovação final, ocupação de
  vaga, resultado preliminar/final publicado ou direito à convocação.

### Key Entities

- **ResultadoEtapa**: consequência imutável de consolidar a Avaliação elegível de uma inscrição em
  uma Etapa; é único por esse par e registra a forma, a conclusão exata que ela exige — pontuação ou
  sentido —, `HABILITADA` ou `ELIMINADA`, fonte, autoria e instante.
- **Avaliação fonte**: única Avaliação concluída e elegível consumida pela V1; preserva autoria,
  parecer, a conclusão na forma sob a qual foi feita e a Versão Consolidada que a governou.
- **Participação na Etapa**: conjunto derivado das inscrições submetidas, menos as eliminadas em
  qualquer Etapa anterior e, quando a imediatamente anterior já produziu Resultado, menos as que não
  possuem `HABILITADA` nela. Não é entidade persistida.
- **Prontidão**: classificação derivada de cada participante quanto à existência, elegibilidade e
  compatibilidade da Avaliação, disponibilidade da regra e existência do Resultado.
- **Desfecho do lote**: resposta persistida da operação idempotente, com itens criados e recusas;
  não substitui os Resultados individuais.

## 4. Invariantes observáveis

1. Nenhuma inscrição+Etapa possui dois Resultados.
2. Todo Resultado possui exatamente uma Avaliação fonte, que **era elegível no instante da
   consolidação** e continua reproduzível. Impedimento posterior pode retirá-la do conjunto elegível
   corrente sem alterar o Resultado, e nesse caso o fato é declarado junto dele.
3. A soma dos estados de prontidão é igual ao total de participantes da Etapa.
4. Toda inscrição apresentada como pronta pode ser consolidada se o estado não mudar entre
   apresentação e confirmação; se mudar, recebe recusa explícita e nenhum dado obsoleto vale.
5. Toda eliminação impede participação posterior, sem apagar trabalho já registrado.
6. Toda linha criada em lote tem um evento; repetição tem zero linhas e zero eventos adicionais.
7. Resultado existente é histórico: Retificação ou mudança de comissão não troca sua regra nem
   suas autorias.

## 5. Out of Scope

- combinação de duas ou mais avaliações, média, mediana, soma, descarte, quórum, divergência e
  desempate;
- novo campo normativo para regra de combinação; isso inclui esquema, elaboração, documento e
  catálogo de Retificação;
- barema estruturado, pontuação por critério ou item e limites por item;
- ponderação entre Etapas, classificação global, ordenação, critérios de empate, vagas, cotas,
  cadastro reserva e convocação;
- resultado preliminar ou final, publicação e consulta pelo candidato ou pelo público;
- recurso, anulação, correção ou reconsolidação de Resultado;
- desistência, cancelamento ou retirada de inscrição;
- exportação de Resultados ou acesso em lote a documentos de candidatos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para uma Etapa com até 1.000 inscrições, a presidência obtém em uma única visão totais
  e detalhes filtráveis que particionam 100% da população por progressão e prontidão.
- **SC-002**: Um único envio consolida até 1.000 inscrições prontas e devolve o total criado, o
  total recusado e o motivo de 100% das recusas, sem interação por inscrição.
- **SC-003**: Em todos os Resultados V1, a conclusão consolidada é idêntica à da única Avaliação
  fonte, na forma dela; não existe caso de arredondamento, média, conversão entre formas ou edição
  manual.
- **SC-004**: 100% das inscrições abaixo da mínima em Etapa pontuada eliminatória ficam `ELIMINADA`,
  e nota igual ou superior fica `HABILITADA`.
- **SC-012**: 100% das inscrições com sentido desfavorável em Etapa decisória eliminatória ficam
  `ELIMINADA`, e as com sentido favorável ficam `HABILITADA`; o motivo de cada uma nomeia o rótulo
  publicado.
- **SC-013**: Etapa decisória e não eliminatória produz zero Resultados, e a prontidão exibe a frase
  que diz por que ela não é consolidável.
- **SC-014**: Etapa decisória eliminatória sem nota mínima consolida normalmente — a ausência do
  número não impede nada nessa forma.
- **SC-015**: Nenhum Resultado da forma pontuada muda de conclusão, consequência ou motivo por causa
  desta revisão, e todo teste de consolidação que existia antes continua existindo e passando.
- **SC-005**: Depois de uma eliminação, a inscrição aparece zero vezes entre participantes,
  distribuição, Mesa, inscrição de trabalho, entrega de documento e próxima pendente de **toda**
  Etapa seguinte, inclusive das que ainda não têm Resultado na Etapa que as precede.
- **SC-006**: Repetir um lote concluído produz zero Resultados e zero eventos adicionais e devolve
  um desfecho idêntico ao original.
- **SC-007**: Para qualquer Resultado consultável, presidência ou auditoria identifica em uma única
  jornada quem avaliou, quem consolidou, quando, sob qual versão e por qual regra a consequência
  foi obtida.
- **SC-008**: Nenhuma tentativa de reabertura ou impedimento altera a conclusão ou a consequência de
  um Resultado: 100% das reaberturas são recusadas sem efeito algum, e 100% dos impedimentos são
  registrados e aplicados por inteiro, com o Resultado preservado e o fato declarado junto dele.
- **SC-009**: Depois de registrado impedimento superveniente, a pessoa impedida acessa zero
  inscrições alcançadas — inclusive a que fundamenta Resultado — na Mesa, na inscrição de trabalho e
  na entrega de documento.
- **SC-010**: Etapa que prevê mais de uma avaliação produz zero Resultados na V1 e mostra, em todos
  os casos, a razão normativa do impedimento.
- **SC-011**: A jornada demonstrável é executada pela interface administrativa: presidente abre a
  Etapa, confere prontidão, consolida um lote, consulta Resultados e vê somente habilitadas na
  Etapa seguinte, sem banco, shell ou chamada manual.

## Assumptions

- A ordem publicada vigente representa a progressão entre Etapas; a primeira posição não exige
  Resultado anterior.
- A V1 atende Editais cuja operação real usa uma avaliação por inscrição. Edital que exige segunda
  leitura continua integralmente avaliável na 012 — inclusive nas Etapas seguintes, porque o filtro
  exigência de habilitação só vigora depois do primeiro Resultado —, mas não é consolidável até que
  uma regra de combinação seja publicada.
- A consolidação é executada quando a presidência considera a Etapa encerrada. A V1 não oferece
  remédio interno para Resultado fundado em Avaliação depois reconhecida como defeituosa: o fato
  fica registrado pelo impedimento superveniente e declarado junto do Resultado, mas corrigir o
  Resultado depende da anulação, que é feature posterior.
- Nota mínima é a única regra estruturada disponível para eliminação **por pontuação**; o sentido
  desfavorável em Etapa decisória eliminatória é a segunda regra estruturada de eliminação, e ela
  chega pela forma, não pelo número. Texto livre do Edital não é interpretado automaticamente em
  nenhuma das duas.
- `HABILITADA` significa apenas que a inscrição pode seguir para a próxima Etapa. Não significa
  aprovação, classificação ou direito a vaga.
- A identidade institucional confiável e as restrições de acesso a dados reais continuam sendo
  gates de implantação herdados.

## 6. Dependências e direção para o planejamento

O plano DEVE começar pelos contratos existentes, não por novos seletores concorrentes. Os nomes
concretos, que os requisitos deliberadamente não carregam, são estes: `avaliacoes_previstas` e
`pontuacao_maxima` para a leitura normativa da Etapa, aos quais a revisão de D-008 acrescenta a
leitura da forma e dos rótulos publicados — que vive na 012 e é herdada, e não reescrita aqui; `avaliacoes_elegiveis` e
`avaliacoes_inelegiveis` para o conjunto que fundamenta o Resultado e para o que ficou de fora;
`resumo_da_etapa` e `inscricoes_da_etapa` para a prontidão de D-004; `comando_de_comissao(...,
idempotency_key)` para o invólucro do lote, `resultado_declarado(...)` para a forma do desfecho e o
`result_payload` do registro de idempotência para preservá-lo. Deve provar a proteção de reabertura
e impedimento no mesmo limite transacional que cria ou encontra o Resultado.

Ordem de fatias sugerida:

| Slice | Entrega observável |
|---|---|
| **S0** | O resumo existente passa a explicar participação, prontidão e impedimentos |
| **S1** | Uma inscrição pronta produz Resultado imutável e reproduzível |
| **S2** | A presidência confirma lote idempotente com desfecho e auditoria por item |
| **S3** | Consulta histórica e progressão para a Etapa seguinte fecham a jornada |

O plano não deve introduzir média “temporária”, versão de esquema 6, estado `PENDENTE`, segundo
painel, papel de Resultado, reconsolidação nem verificação de autorização por linha. Se qualquer um
parecer necessário, a decisão volta à spec antes de virar implementação.
