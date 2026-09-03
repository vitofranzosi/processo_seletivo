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
- Participante nasce do universo de inscrições `SUBMETIDA` do Edital. A partir da segunda Etapa, e
  somente depois que a anterior produzir Resultado, esta feature acrescenta a consequência dela,
  definida em D-003;
- Avaliação possui apenas `RASCUNHO` e `CONCLUIDA`, com pontuação total e parecer. Critérios,
  itens e barema estruturado não existem no domínio e não são pressupostos aqui;
- a quantidade prevista e a pontuação máxima já são conteúdo publicado da Etapa, na versão
  canônica 5. A 013 lê esse conteúdo e não cria novo incremento normativo;
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
`evaluations_per_registration == 1`. A pontuação consolidada é exatamente o total da única
Avaliação elegível, sem média, arredondamento ou ponderação. Etapa que preveja mais de uma avaliação
fica em impedimento explícito: “o Edital prevê N avaliações, mas não declara como combiná-las”.

Uma regra de combinação para múltiplas avaliações exigirá incremento canônico próprio — forma
publicada, validação, elaboração, documento e Retificação — e pertence a uma evolução posterior.

### D-002 — Consolidar fecha as entradas da decisão

`ResultadoEtapa` é uma consequência administrativa imutável. Depois que existe para uma inscrição
e Etapa, a Avaliação que o fundamentou não pode ser reaberta nem tornada inelegível. A reabertura é
recusada por inteiro, antes de qualquer efeito, nomeando o Resultado que protege a Avaliação.

A V1 não oferece anulação nem reconsolidação. Aceitar mudança da entrada e conservar Resultado
desatualizado seria uma anulação silenciosa; aceitar mudança automática do Resultado apagaria a
autoria do ato original. Ambas ficam fora.

**O que essa porta fechada custa, dito por extenso.** Sem anulação, um Resultado fundado em
Avaliação depois reconhecida como defeituosa — erro material, conflito de interesse descoberto
tarde — não tem remédio dentro do sistema na V1. A spec aceita esse custo e não o disfarça: a
consolidação é ato deliberado da presidência sobre uma Etapa que ela considera encerrada, e não
efeito automático da última conclusão.

**O que ela não pode custar é o registro do fato.** O Impedimento da 012 existe para que a razão
fique escrita, ancorada na pessoa e na inscrição justamente para sobreviver a reorganização
administrativa. Recusar o registro seria o sistema se recusar a saber, e no caso que mais importa —
descobrir tarde que quem avaliou não podia — a recusa apagaria a única prova de que se descobriu.
Por isso o que é recusado é a **inativação da Avaliação fonte**, e não o impedimento: ele é sempre
registrável, alcança tudo o que pode alcançar, e o que ele deixa de alcançar é nomeado no desfecho.

### D-003 — Eliminação altera o conjunto da Etapa seguinte

A 013 não deixará a tela da Etapa seguinte contar quem a Etapa anterior eliminou.

- Na primeira Etapa, participam todas as inscrições submetidas do Edital.
- **O filtro de progressão só vigora depois que a Etapa anterior começa a produzir Resultado.**
  Enquanto a Etapa imediatamente anterior não possuir nenhum Resultado, a Etapa seguinte conserva
  integralmente o conjunto da 012 — todas as inscrições submetidas —, e a distribuição continua
  podendo ser preparada antes de a Etapa anterior fechar. É esse gate que impede a 013 de quebrar
  o que hoje funciona: sem ele, Etapa anterior de leitura múltipla, que D-001 não consolida, deixaria
  a Etapa seguinte permanentemente sem participantes, e nenhum Edital de segunda leitura passaria
  da primeira Etapa.
- A partir do primeiro Resultado da Etapa anterior, participa a inscrição submetida que possua
  Resultado `HABILITADA` nela, segundo a ordem publicada vigente.
- Resultado `ELIMINADA` exclui a inscrição das Etapas seguintes.
- Com o filtro vigente, ausência do Resultado anterior mantém a inscrição em “aguardando Etapa
  anterior”; ela não conta como participante pronta, não pode ser distribuída e não concede acesso
  por Atribuição que tenha sido criada antecipadamente. Atribuição criada enquanto o filtro estava
  dormente é preservada e volta a autorizar quando o Resultado habilitador existir.

**Como isso é verificado.** A 012 fechou a cadeia de autorização em duas condições e manteve o
impedimento fora dela por uma razão de escala: somá-lo custaria uma verificação por linha em toda
listagem, e ela protege essa invariante agindo na escrita, nunca na leitura. A progressão não
reabre essa porta. O conjunto habilitador da Etapa anterior é resolvido **uma vez por listagem** —
como a 011 já faz com as Etapas autorizadas — e a cadeia individual ganha uma verificação de par
apenas na rota de item. Nenhuma listagem da 013 ou da 012 passa a decidir autorização linha a linha.

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
Resultado**: caráter eliminatório, nota mínima, quantidade de avaliações e pontuação máxima.
Ausência de quantidade equivale a `1`; ausência de máxima equivale a “não declarada”, conforme os
leitores herdados da 012.

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
   mesma pessoa, **When** a presidência o registra, **Then** o impedimento é criado, as demais
   Atribuições são inativadas, a fonte é preservada e o desfecho nomeia o Resultado que a protege.

### Edge Cases

- Nota exatamente igual à mínima habilita; comparação decimal não arredonda o valor.
- Etapa eliminatória sem nota mínima não possui regra suficiente e não pode ser consolidada.
- Etapa não eliminatória materializa total e `HABILITADA`; eventual nota mínima não elimina.
- Zero ou mais de uma Avaliação elegível quando a regra prevê uma é inconsistência explícita; o
  sistema não escolhe uma linha nem consolida silenciosamente.
- Retificação que altera outro trecho do Edital não impede consolidação; alteração normativa da
  própria Etapa impede enquanto não houver Resultado e não reescreve Resultado já existente.
- Retificação que remove a Etapa antes da consolidação torna a operação indisponível; remoção
  posterior não apaga Resultados históricos.
- Com o filtro de progressão vigente, Resultado anterior ausente impede progressão; Resultado
  anterior eliminado não é tratado como pendência.
- Mudança de ordem publicada antes da consolidação recalcula qual é a Etapa anterior; Resultados já
  materializados permanecem históricos e não são reinterpretados.
- Um impedimento que alcança várias Atribuições é registrado, inativa as que pode e preserva
  nominalmente as que fundamentam Resultado; a confirmação e o desfecho distinguem as duas listas.
- Etapa anterior sem nenhum Resultado — porque prevê mais de uma avaliação, ou porque a consolidação
  ainda não começou — não bloqueia a Etapa seguinte: o filtro de progressão está dormente e a
  distribuição segue como na 012.
- Retificação que corrige nome, cronograma, peso ou caráter classificatório da Etapa não cria
  incompatibilidade, porque nenhum deles altera a pontuação ou a consequência desta feature.
- Dois lotes concorrentes sobre a mesma inscrição produzem no máximo um Resultado; o perdedor
  recebe desfecho explícito, sem evento duplicado.

## Requirements *(mandatory)*

### Functional Requirements

#### Participação e prontidão

- **FR-001**: A primeira Etapa DEVE considerar como participantes exatamente as inscrições
  submetidas do Edital.
- **FR-002**: Toda leitura da quantidade prevista DEVE usar o leitor único herdado da 012, com o
  significado que a §1 registra; a 013 NÃO DEVE duplicar padrão ou configuração.
- **FR-003**: Etapa posterior cuja Etapa imediatamente anterior já possua ao menos um Resultado
  DEVE considerar participante somente inscrição submetida com Resultado `HABILITADA` nela, pela
  ordem publicada vigente. Enquanto a Etapa anterior não possuir nenhum Resultado, a Etapa posterior
  DEVE conservar o conjunto da 012 — todas as inscrições submetidas.
- **FR-004**: Com o filtro de progressão vigente, inscrição eliminada ou aguardando Resultado
  anterior NÃO DEVE ser distribuível, contabilizada como participante nem acessível na Mesa da Etapa
  posterior. A verificação DEVE ser feita por conjunto — o conjunto habilitador da Etapa anterior é
  resolvido uma vez por listagem — e NUNCA por linha, preservando a invariante de escala herdada da
  012; a rota individual continua verificando o par diretamente.
- **FR-005**: A prontidão DEVE consumir o conjunto elegível herdado da 012; Avaliação inelegível
  NÃO PODE ser escolhida por filtro alternativo, e seu motivo continua consultável pelo contrato
  herdado.
- **FR-006**: A visão existente da organização DEVE ser acrescida, e não duplicada, com totais de
  participantes, aguardando anterior, eliminadas anteriormente, pendentes, prontas, consolidadas e
  impedidas por motivo.
- **FR-007**: As contagens da mesma Etapa DEVEM formar uma partição verificável, sem inscrição em
  dois estados de prontidão nem divergência entre resumo e detalhe filtrado.
- **FR-008**: Regra disponível exige Etapa vigente de leitura única e, quando eliminatória, nota
  mínima declarada.
- **FR-009**: Cada impedimento de prontidão DEVE ter mensagem acionável: avaliação ausente,
  avaliação excedente, incompatibilidade normativa, Resultado anterior ausente, eliminação
  anterior, regra de combinação ausente ou Resultado já existente.

#### Compatibilidade e regra de consolidação

- **FR-010**: Compatibilidade DEVE comparar semanticamente os campos enumerados em D-005, tratando
  os significados legados de ausência conforme a 012, e NÃO a identidade da Versão Consolidada.
- **FR-011**: Avaliação cuja versão não contém a Etapa, ou cuja Etapa diverge da vigente em campo
  comparado, NÃO PODE produzir Resultado.
- **FR-012**: Na V1, Etapa que preveja mais de uma avaliação por inscrição DEVE ser impedida por
  inteiro, nomeando a quantidade publicada e a ausência de regra de combinação.
- **FR-013**: A pontuação consolidada DEVE ser cópia exata da pontuação da única Avaliação elegível,
  sem média, peso, arredondamento ou edição pela presidência.
- **FR-014**: Etapa eliminatória DEVE produzir `ELIMINADA` somente quando a pontuação for menor que
  a mínima publicada; em todos os demais casos alcançáveis, DEVE produzir `HABILITADA`.

#### Lote e idempotência

- **FR-015**: A presidência DEVE consolidar uma ou várias inscrições em um único lote confirmado,
  sob o mesmo invólucro transacional e idempotente que a 012 já aplica aos atos da comissão, com
  chave obrigatória.
- **FR-016**: O lote DEVE criar Resultados para itens válidos e declarar, para cada item inválido,
  a recusa específica; erro sobre o pedido inteiro DEVE impedir qualquer criação.
- **FR-017**: O desfecho DEVE declarar criadas, recusas e motivos na mesma forma já usada pelos
  atos em lote da 012, e ficar preservado junto ao registro de idempotência, de modo que a repetição
  o devolva por inteiro em vez de um vazio.
- **FR-018**: Cada Resultado criado no lote DEVE gerar exatamente um evento de auditoria; reenviar
  o mesmo ato não cria Resultado nem evento novo e devolve o desfecho original.
- **FR-019**: Mesma chave com conteúdo diferente DEVE produzir conflito; chave diferente sobre par
  já consolidado DEVE recusar o item como já consolidado, sem tratar a tentativa como sucesso.
- **FR-020**: O lote DEVE ser atomicamente protegido contra duas consolidações concorrentes do
  mesmo par inscrição+Etapa.

#### Resultado e proveniência

- **FR-021**: DEVE existir no máximo um `ResultadoEtapa` por inscrição e Etapa, inclusive sob
  concorrência e qualquer número de reenvios.
- **FR-022**: O Resultado DEVE materializar pontuação consolidada, consequência, Avaliação fonte,
  instante e identidade de quem consolidou.
- **FR-023**: A partir da Avaliação fonte, DEVE ser possível reproduzir a Versão Consolidada e os
  campos normativos que determinaram pontuação e consequência, sem usar regra atual no lugar da
  histórica.
- **FR-024**: Resultado, fonte e auditoria DEVEM distinguir autoria da Avaliação e autoria da
  consolidação.
- **FR-025**: `PENDENTE` e `CONSOLIDADO` NÃO DEVEM ser estados persistidos: são, respectivamente,
  ausência e existência do Resultado. `HABILITADA` e `ELIMINADA` são consequências persistidas.
- **FR-026**: Resultado criado NÃO PODE ser editado nem fisicamente excluído pela aplicação.

#### Fechamento das entradas

- **FR-027**: Reabertura de Avaliação que fundamenta Resultado DEVE ser recusada antes de qualquer
  mudança, mesmo com motivo, revisão e chave válidos.
- **FR-028**: Impedimento DEVE continuar sendo registrável mesmo quando alcança Avaliação que
  fundamenta Resultado. O que DEVE ser recusado é a inativação dessa Atribuição; as demais
  Atribuições alcançadas pelo mesmo ato são inativadas normalmente, e o desfecho DEVE nomear, uma a
  uma, as preservadas e o Resultado que as protege.
- **FR-029**: A confirmação do alcance do impedimento DEVE distinguir, antes do ato, o que será
  inativado do que será preservado por fundamentar Resultado.
- **FR-030**: A recusa de reabertura, e a preservação de Atribuição alcançada por impedimento, DEVEM
  identificar a inscrição, a Etapa e o Resultado protetor, sem expor pontuação a ator não
  autorizado.
- **FR-031**: Retificação posterior NÃO DEVE reescrever, recalcular nem invalidar Resultado já
  criado; anulação e reconsolidação ficam fora da V1.

#### Autorização, consulta e proteção de dados

- **FR-032**: Consolidar DEVE usar a mesma base de autorização contextual já aplicada à reabertura;
  o ato canônico é `resultado:consolidar`, sem papel novo.
- **FR-033**: A autorização DEVE ser reavaliada dentro do ato protegido, antes de reservar a chave
  e gravar Resultados.
- **FR-034**: Presidência DEVE consultar os Resultados do Processo; auditoria autorizada DEVE poder
  reconstruí-los sem adquirir poder de consolidar.
- **FR-035**: Identificador de Edital, Etapa, inscrição, Avaliação ou Resultado NÃO PODE conceder
  acesso; escopo institucional ou vínculo divergente recebe a resposta uniforme de recurso não
  encontrado.
- **FR-036**: Respostas com Resultado individual ou dados da inscrição NÃO DEVEM ser armazenáveis
  pelo navegador e NÃO DEVEM ampliar o acesso a documentos do candidato.
- **FR-037**: Auditoria DEVE registrar ator, base autorizadora, ato, Resultado, instante,
  correlação e chave de idempotência, sem copiar pontuação ou parecer para a trilha.

#### Não regressão e limites

- **FR-038**: A 013 NÃO DEVE criar incremento canônico, campo de elaboração, alteração de documento
  publicado nem nova regra de Retificação.
- **FR-039**: Distribuição e Mesa da primeira Etapa DEVEM conservar o comportamento da 012 para
  toda inscrição submetida; nas seguintes, o filtro de progressão de D-003 é acrescentado apenas
  depois do primeiro Resultado da Etapa anterior, e nada mais muda.
- **FR-040**: A 013 NÃO DEVE alterar conteúdo, estado ou autoria de Avaliação, Atribuição,
  Impedimento, Publicação ou Versão Consolidada existente.
- **FR-041**: Peso da Etapa, caráter classificatório e pontuação de outras Etapas NÃO DEVEM compor o
  total desta feature.
- **FR-042**: Nenhuma tela ou resposta da 013 DEVE afirmar colocação, aprovação final, ocupação de
  vaga, resultado preliminar/final publicado ou direito à convocação.

### Key Entities

- **ResultadoEtapa**: consequência imutável de consolidar a Avaliação elegível de uma inscrição em
  uma Etapa; é único por esse par e registra pontuação exata, `HABILITADA` ou `ELIMINADA`, fonte,
  autoria e instante.
- **Avaliação fonte**: única Avaliação concluída e elegível consumida pela V1; preserva autoria,
  parecer, pontuação, conclusão e Versão Consolidada que a governou.
- **Participação na Etapa**: conjunto derivado de inscrições submetidas e, depois da primeira
  Etapa, do Resultado habilitador imediatamente anterior. Não é entidade persistida.
- **Prontidão**: classificação derivada de cada participante quanto à existência, elegibilidade e
  compatibilidade da Avaliação, disponibilidade da regra e existência do Resultado.
- **Desfecho do lote**: resposta persistida da operação idempotente, com itens criados e recusas;
  não substitui os Resultados individuais.

## 4. Invariantes observáveis

1. Nenhuma inscrição+Etapa possui dois Resultados.
2. Todo Resultado possui exatamente uma Avaliação fonte, e ela continua elegível e reproduzível.
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
- **SC-003**: Em todos os Resultados V1, a pontuação consolidada é idêntica à da única Avaliação
  fonte; não existe caso de arredondamento, média ou edição manual.
- **SC-004**: 100% das inscrições abaixo da mínima em Etapa eliminatória ficam `ELIMINADA`, e nota
  igual ou superior fica `HABILITADA`.
- **SC-005**: Depois de uma eliminação, a inscrição aparece zero vezes entre participantes,
  distribuição e Mesa de qualquer Etapa seguinte.
- **SC-006**: Repetir um lote concluído produz zero Resultados e zero eventos adicionais e devolve
  um desfecho idêntico ao original.
- **SC-007**: Para qualquer Resultado consultável, presidência ou auditoria identifica em uma única
  jornada quem avaliou, quem consolidou, quando, sob qual versão e por qual regra a consequência
  foi obtida.
- **SC-008**: Nenhuma tentativa de reabertura ou impedimento modifica a Avaliação fonte de um
  Resultado: 100% das reaberturas são recusadas sem efeito algum, e 100% dos impedimentos são
  registrados preservando a fonte e nomeando o Resultado que a protege.
- **SC-009**: Etapa que prevê mais de uma avaliação produz zero Resultados na V1 e mostra, em todos
  os casos, a razão normativa do impedimento.
- **SC-010**: A jornada demonstrável é executada pela interface administrativa: presidente abre a
  Etapa, confere prontidão, consolida um lote, consulta Resultados e vê somente habilitadas na
  Etapa seguinte, sem banco, shell ou chamada manual.

## Assumptions

- A ordem publicada vigente representa a progressão entre Etapas; a primeira posição não exige
  Resultado anterior.
- A V1 atende Editais cuja operação real usa uma avaliação por inscrição. Edital que exige segunda
  leitura continua integralmente avaliável na 012 — inclusive nas Etapas seguintes, porque o filtro
  de progressão só vigora depois do primeiro Resultado —, mas não é consolidável até que uma regra
  de combinação seja publicada.
- A consolidação é executada quando a presidência considera a Etapa encerrada. A V1 não oferece
  remédio interno para Resultado fundado em Avaliação depois reconhecida como defeituosa: o fato
  continua registrável, e a correção depende da anulação, que é feature posterior.
- Nota mínima é a única regra estruturada disponível para eliminação por pontuação; texto livre do
  Edital não é interpretado automaticamente.
- `HABILITADA` significa apenas que a inscrição pode seguir para a próxima Etapa. Não significa
  aprovação, classificação ou direito a vaga.
- A identidade institucional confiável e as restrições de acesso a dados reais continuam sendo
  gates de implantação herdados.

## 6. Dependências e direção para o planejamento

O plano DEVE começar pelos contratos existentes, não por novos seletores concorrentes. Os nomes
concretos, que os requisitos deliberadamente não carregam, são estes: `avaliacoes_previstas` e
`pontuacao_maxima` para a leitura normativa da Etapa; `avaliacoes_elegiveis` e
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
