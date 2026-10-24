# Feature Specification: Relatório do Edital — acompanhamento e encerramento, para quem não opera a seleção

**Feature Branch**: `claude/gps-executive-closure-report-2d9457`, sobre a `main` em `5a08f409`

**Created**: 2026-10-24

**Status**: Implementada em 24/10/2026, por autorização do usuário (concepção da maquete v2 aprovada
com os ajustes de precisão desta spec), revisada por code review no mesmo dia (dez achados, todos
corrigidos). PR aberto em 24/10/2026; o merge é do usuário. A SC-932 — conversa com destinatários
reais — fica aberta.

**Input**: pedido do usuário de 24/10/2026 — *"Aprovo a concepção geral da v2 como referência do
MVP"* —, condicionado a seis ajustes de precisão (pessoas, concorrência por vaga, convocações e vagas,
encerramento e acompanhamento, documentos oficiais, privacidade). A investigação que precede esta spec
está em [`doc/estudo-relatorio-de-execucao-do-edital-2026-10-24.md`](../../doc/estudo-relatorio-de-execucao-do-edital-2026-10-24.md),
na [rodada 2](../../doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/rodada-2.md) e na
[maquete v2](../../doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/maquete-v2.pdf).

> **Faixa de identificadores.** Esta spec abre em **FR-2513** e **SC-932**. Teto medido em 24/10/2026
> em `specs/` de **todas as worktrees desta máquina** e na `main`: `FR-2512`, `SC-931`, `UX-222`, da
> `098`. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-592 da `040`"); decisão de outra feature, pelo assunto e pela feature, porque `D-` aqui é só desta.

---

## Por que esta feature existe

**Quem responde pela seleção na instituição não opera o GPS, e quem opera não tem como lhe responder
de uma vez.** Os fatos do ciclo de um Edital — vagas, inscrições, etapas, resultados, ocupação,
convocações, recursos e retificações — estão em sete telas da gestão, com quatro portas de acesso
diferentes, e nenhuma leitura os reúne. A direção do campus, a direção de ensino e as coordenações não
têm papel no sistema.

**O encerramento existe, e não quer dizer o que parece.** `Edital.Status.ENCERRADO` é ato motivado e
auditado, mas o único efeito dele é parar as inscrições: recurso, convocação, desfecho e apuração
continuam sendo gravados depois, e o ato não confere pendência alguma. A maquete v2 demonstrou os dois
pelo sistema: um Edital encerrado com convocação no prazo de resposta, e um aceite registrado no dia
seguinte ao encerramento. Um relatório que se dissesse "de encerramento" por ler o estado afirmaria uma
conclusão que o estado não garante.

**Os números existem; o que falta é dizê-los com precisão a quem não conhece o sistema.** A `040` já
definiu indicadores, denominadores e as grafias de ausência; o portal já tem rótulos em linguagem
simples para o candidato (`063`). Esta feature os reúne por Edital, num documento.

### O que existe e é reaproveitado

| Peça | Onde |
|---|---|
| Vagas do conteúdo vigente; contagem de inscrições por Perfil; razão com numerador recortado | `interface/visao_geral.py` (`vagas_do_conteudo`, `contagens_por_edital`, `_razao`) |
| Série diária de envios | `interface/supervisao.py` (`serie_do_edital`) |
| Desfecho do Edital e a data do ato | `processos/application/selectors.py` (`desfechos`) |
| Resultado vigente por marco e lista | `divulgacao/application/selectors.py` (`vigente_do_marco`) |
| Ocupação por recorte, com obsolescência | `ocupacao/application/selectors.py` (`recortes_do_marco`) |
| Atos publicados e o que cada Retificação alterou | `publicacoes/application/selectors.py` (`atos_publicados`), `publicacoes/domain/alteracoes.py` |
| Rótulos simples de desfecho de convocação e de decisão de recurso | `portal/situacao.py` (`DESFECHOS`), `recursos/application/selectors.py` (`ESPECIES`) |
| Motor de PDF determinístico, com links e marcadores | `publicacoes/infrastructure/pdf.py` |
| Registro de auditoria | `auditoria/application.py` (`record_event`) |

### O que esta spec cobre, e o que fica fora

| Cobre | Fora |
|---|---|
| Uma página de gestão por Edital com a camada executiva, e o PDF com a camada executiva e o anexo técnico | Relatório por Processo e comparação entre Editais (a série é da `040`) |
| Espécie derivada: acompanhamento, encerramento ou interrupção | Estado novo, transição nova, bloqueio de ato — inclusive conferir pendência ao encerrar (D-007) |
| Visão geral escrita por regras verificáveis | Texto por modelo de linguagem; juízo, causa ou recomendação |
| Emissão registrada na auditoria, numerada e com o resumo do arquivo | Guarda dos bytes de cada emissão (D-005) |
| Links para a página pública da seleção e para cada resultado | Relação nominal de candidatos |
| Privacidade por desenho: fato não público só por Perfil | Supressão de célula |

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Entender a seleção sem conhecer o sistema (Priority: P1) 🎯 MVP

A presidência da comissão, ou a gestão, abre o Edital e pede o relatório. A primeira página diz, em
linguagem simples, o que foi oferecido, quanta procura houve, o que saiu, e o que ainda falta. Ela
baixa o PDF e o envia à direção, que entende a seleção sem precisar de explicação.

**Why this priority**: é o problema verificado e o valor aprovado; sem ela, a feature não existe.

**Independent Test**: com o cenário coerente do estudo (Edital 61/2026), abrir o relatório e
baixar o PDF; conferir que a primeira página tem identificação, as duas situações, a visão geral, os
indicadores e os pontos de atenção, e que nenhum termo interno aparece nela.

**Acceptance Scenarios**:

1. **Given** um Edital com resultado definitivo e convocações, **When** a presidência abre o
   relatório, **Then** a página mostra a visão geral, os seis indicadores com a base escrita embaixo,
   e os pontos de atenção, e oferece "Baixar PDF".
2. **Given** a mesma página, **When** a presidência baixa o PDF, **Then** o arquivo traz a camada
   executiva nas primeiras páginas e o anexo técnico depois, com o instante dos dados em toda página.
3. **Given** um Perfil só com cadastro de reserva, **When** o relatório é gerado, **Then** as
   inscrições por vaga daquele Perfil dizem "não se aplica" e nunca 0 nem infinito.

---

### User Story 2 — Saber se a seleção terminou, e não só se o Edital foi encerrado (Priority: P1)

Quem lê vê duas situações distintas: a do Edital no GPS e a das providências que o GPS acompanha. O
título diz se o relatório é de acompanhamento ou de encerramento, por regra conhecida, e o de
encerramento não afirma o que o GPS não acompanha.

**Why this priority**: é o achado central do estudo e o ajuste D do usuário.

**Independent Test**: gerar o relatório em três estados do mesmo cenário — com inscrições abertas,
encerrado com convocação no prazo, e encerrado depois de toda resposta — e conferir a espécie, as
pendências e os registros posteriores ao encerramento.

**Acceptance Scenarios**:

1. **Given** o Edital encerrado com uma convocação no prazo de resposta, **When** o relatório é
   gerado, **Then** ele é *de acompanhamento*, diz "Encerrado em DD/MM" como situação no GPS e
   "1 convocação aguardando resposta, até DD/MM" como situação das providências.
2. **Given** o Edital encerrado sem nenhuma pendência registrada, **When** o relatório é gerado,
   **Then** ele é *de encerramento*, e diz que não há providência pendente **registrada no GPS** e que
   atividades que o GPS não acompanha, como a matrícula, não estão refletidas nele.
3. **Given** um ato registrado depois do encerramento, **When** o relatório é gerado, **Then** os
   pontos de atenção dizem quantos registros houve depois do encerramento, e de que tipo.
4. **Given** um Edital cancelado, **When** o relatório é gerado, **Then** ele é *de interrupção*, e
   diz o cancelamento e a data.

---

### User Story 3 — Conferir números, documentos e regras (Priority: P2)

A equipe e o controle interno leem o anexo técnico: etapas por Perfil, classificação por lista,
recursos, cronograma previsto, retificado e registrado, a definição de cada número, o que o GPS não
registra, e os documentos oficiais com o resumo de integridade. Os links levam à página pública da
seleção e a cada resultado.

**Why this priority**: sustenta a confiança no documento; não é o que a direção lê primeiro.

**Independent Test**: cada número do anexo coincide com o da tela dona; cada documento listado tem o
resumo igual ao do arquivo publicado; os links do PDF apontam para endereços públicos do portal.

**Acceptance Scenarios**:

1. **Given** o relatório de um Edital com resultados publicados, **When** o anexo é lido, **Then** cada
   documento aparece com data e resumo SHA-256, e o texto explica que o resumo confere a integridade
   do arquivo e não, sozinho, a oficialidade.
2. **Given** o PDF aberto num leitor, **When** se clica no endereço da página pública ou de um
   resultado, **Then** o leitor abre o endereço.

---

### User Story 4 — Emissão rastreável (Priority: P2)

Cada PDF baixado fica registrado: quem, quando, com dados de que instante, e o resumo do arquivo. O
documento diz o número da emissão.

**Why this priority**: o PDF sai do sistema; sem rastro, não há como saber qual versão circula.

**Independent Test**: baixar o PDF duas vezes e conferir dois eventos na trilha, com resumos dos
bytes entregues, e "emissão nº 1" e "nº 2" nos documentos.

**Acceptance Scenarios**:

1. **Given** um Edital sem emissão anterior, **When** o PDF é baixado, **Then** a trilha ganha um
   evento com o resumo do arquivo, e o documento diz "emissão nº 1".
2. **Given** os mesmos fatos e o mesmo instante de referência, **When** o documento é composto duas
   vezes, **Then** os bytes são idênticos.

---

### Edge Cases

- **Edital publicado e com inscrições abertas.** Relatório de acompanhamento; inscrições marcadas como
  parciais; etapas, resultados, convocações e recursos dizem "ainda não disponível".
- **Edital em elaboração, em revisão ou homologado.** A ação não é oferecida; acesso direto recusa com
  a frase de quando o relatório fica disponível.
- **Marco sem resultado publicado.** Conta como pendência; a linha diz "ainda não divulgado".
- **Lista reservada sem inscrição e sem ato.** Não é pendência — não há o que divulgar —; a vaga dela
  aparece como "não apurada", e não como vaga sem ocupante.
- **Apuração vigente desatualizada.** "Apuração desatualizada" no lugar do número, e conta como
  pendência.
- **Convocação com prazo vencido e sem desfecho.** É pendência — "prazo encerrado sem registro de
  resposta" — e não "não atendida": o não atendimento só existe quando a comissão o registra.
- **Resultado preliminar sucedido pelo definitivo.** Conta só o vigente; o anexo diz que houve
  substituição.
- **Ato de ordenação sucedido.** O relatório usa o vigente; não reconstitui o anterior.
- **Perfil com menos de cinco inscrições enviadas.** Os fatos não públicos daquele Perfil (eliminações,
  ocorrências, recursos, convocações, rascunhos) são omitidos com a frase "detalhe omitido: menos de
  5 inscrições neste perfil" (D-006).
- **Mesma pessoa em dois Perfis.** Totais do Edital contam inscrições; o anexo diz quantos cadastros de
  candidato distintos há, sem chamá-los de pessoas.
- **Retificação que o leitor de alterações não sabe descrever.** Aparece com data e justificativa, e
  "alteração não descrita automaticamente".
- **Edital sem Retificação, sem recurso ou sem convocação.** A seção diz "nenhuma", em vez de sumir —
  zero produzido por fonte é afirmação válida (`040`, §13).
- **Registro gravado enquanto o relatório é lido.** A leitura inteira vê o banco num instante só; o
  registro novo entra na emissão seguinte.
- **Texto do Edital com caractere sem grafia no PDF.** A emissão recusa, como o Edital (achado de
  08/10), em vez de trocar por "?".

---

## Requirements *(mandatory)*

### Functional Requirements

#### Acesso e emissão

- **FR-2513**: O detalhe do Edital MUST oferecer a ação "Relatório do Edital" a quem alcança a porta
  da Supervisão do Processo dele (gestão do escopo ou presidência do Processo), quando o Edital está
  publicado, encerrado ou cancelado. Em outro estado a ação MUST aparecer indisponível, com o motivo.
- **FR-2514**: Edital inexistente ou de outra unidade MUST responder "não encontrado", sem distinguir
  os dois. Quem é da unidade e não tem a base MUST receber a recusa explicada da `033` — o que falta e
  a quem pedir —, e não "não encontrado" (SC-165 da `033`).
- **FR-2515**: A página do relatório MUST mostrar a camada executiva e o botão "Baixar PDF". Baixar
  MUST ser um envio de formulário, e não um link: é a emissão que fica registrada.
- **FR-2516**: Cada emissão MUST gravar um evento de auditoria com o Edital, o instante de referência,
  o ator, o número da emissão e o resumo SHA-256 dos bytes entregues.
- **FR-2517**: O número da emissão MUST ser a quantidade de emissões anteriores daquele Edital mais
  um, e o documento MUST dizê-lo ("emissão nº N").
- **FR-2518**: A resposta da página e a do PDF MUST ser privadas (sem armazenamento em cache
  compartilhado).

#### Instante e consistência

- **FR-2519**: Toda a leitura de um relatório MUST ver os dados de um instante só, tomado no início, e
  esse instante MUST aparecer como "dados até DD/MM/AAAA, HHhMM", no horário institucional, no topo da
  página e em toda página do PDF.
- **FR-2520**: Mesmos fatos e mesmo instante de referência MUST produzir o mesmo documento, byte a byte.
- **FR-2521**: O relatório MUST NOT reconstituir estado passado: ele relata o vigente no instante de
  referência, e o anexo MUST dizer que uma nova emissão pode trazer números diferentes.

#### Espécie e situações

- **FR-2522**: O relatório MUST mostrar duas situações distintas: a **situação no GPS** (o estado do
  Edital, e a data do ato quando houver desfecho) e a **situação das providências** (as pendências da
  FR-2524, ou "nenhuma providência pendente registrada no GPS").
- **FR-2523**: A espécie MUST ser derivada assim: **de interrupção** para Edital cancelado; **de
  encerramento** para Edital encerrado sem nenhuma pendência; **de acompanhamento** em qualquer outro
  caso. Nenhum estado novo é gravado.
- **FR-2524**: São pendências, no instante de referência: marco com ato emitido ou publicado sem
  resultado definitivo vigente em alguma lista; marco sem nenhum resultado publicado; recurso
  aguardando admissibilidade ou julgamento; reavaliação determinada por recurso ainda não concluída; providência pendente de marco; apuração vigente com causa
  de desatualização; convocação sem desfecho com prazo em curso; convocação sem desfecho com prazo
  encerrado.
- **FR-2525**: O relatório de encerramento MUST dizer, junto da espécie, que não há providência
  pendente **registrada no GPS** e que atividades que o GPS não acompanha, como a matrícula, não estão
  refletidas nele. MUST NOT dizer que a seleção foi concluída.
- **FR-2526**: Havendo desfecho do Edital, o relatório MUST contar os registros de auditoria do Edital
  com instante posterior ao ato de desfecho, agrupados por tipo de ato em linguagem simples, e MUST
  dizê-los nos pontos de atenção.

#### Visão geral e indicadores

- **FR-2527**: A visão geral MUST ser composta só de frases cuja condição é verdadeira no instante de
  referência, cada uma com fonte definida, e MUST NOT conter juízo, causa, previsão ou recomendação.
- **FR-2528**: A camada executiva MUST trazer seis indicadores, cada um com a base escrita embaixo:
  vagas imediatas; inscrições enviadas; inscrições por vaga; resultados definitivos publicados;
  vagas com inscrição classificada e habilitada; convocações aceitas.
- **FR-2529**: Inscrições por vaga MUST ser a soma das inscrições enviadas nos Perfis com vaga imediata
  dividida pela soma das vagas imediatas desses Perfis, com uma casa, e por Perfil a mesma razão.
  Perfil só de cadastro de reserva MUST dizer "não se aplica". O relatório MUST NOT dizer "candidatos
  por vaga".
- **FR-2530**: O relatório MUST NOT afirmar número de pessoas. O anexo MUST dizer quantos **cadastros
  de candidato** distintos têm inscrição enviada, com a definição: a mesma pessoa pode ter mais de um
  cadastro.
- **FR-2531**: "Vagas com inscrição classificada e habilitada" MUST somar as apurações vigentes e
  atualizadas, e MUST vir acompanhada de "não é matrícula". Recorte sem apuração MUST dizer "não
  apurada"; apuração desatualizada, "apuração desatualizada".
- **FR-2532**: Convocações MUST ser ditas pela cadeia: convocações realizadas, aceitas, aguardando
  resposta, com prazo encerrado sem registro, e os demais desfechos pelo rótulo simples. O aceite MUST
  ser dito "convocação aceita", e MUST NOT ser apresentado como vaga preenchida.
- **FR-2533**: Matrícula MUST aparecer só como fato não registrado pelo GPS.

#### Camada executiva

- **FR-2534**: Os pontos de atenção MUST trazer, nesta ordem e no máximo três itens, a diferença entre
  as duas situações, os registros posteriores ao desfecho e a ausência de matrícula; os demais itens
  MUST ir para o anexo.
- **FR-2535**: A tabela por Perfil de vaga MUST trazer, por Perfil, o nome cadastrado, a localidade,
  as vagas imediatas desdobradas por lista, as inscrições enviadas, as inscrições por vaga, as
  inscrições com classificação no resultado vigente, e a situação das vagas.
- **FR-2536**: A procura MUST ser mostrada por semana de envio, a contar do primeiro dia do período,
  com a semana do término original do prazo indicada quando houve prorrogação, e com a contagem de
  envios no período acrescentado. A tabela é a forma, e é o próprio equivalente textual: o motor de
  documento não desenha gráfico, e acrescentar a primitiva mudaria o escritor do Edital.
- **FR-2537**: Alterações e recursos MUST trazer cada Retificação com data, os campos alterados com o
  valor anterior e o novo quando legíveis, e a justificativa como registrada; e os recursos pelo total
  de apresentados, não admitidos, indeferidos, deferidos e aguardando.
- **FR-2538**: As datas principais MUST marcar cada data como publicação, registro no GPS, data
  prevista no Edital ou prazo, e MUST NOT dizer que um evento previsto aconteceu.
- **FR-2539**: Os documentos oficiais MUST ser referidos pelo endereço público da página da seleção e
  de cada resultado vigente, clicáveis no PDF, e a camada executiva MUST NOT trazer resumos SHA-256.

#### Anexo técnico

- **FR-2540**: O anexo MUST trazer, por Perfil e por Etapa do marco daquele Perfil, as inscrições
  avaliadas, habilitadas, eliminadas pela nota ou decisão e eliminadas por ocorrência registrada; e
  MUST NOT trazer número de presentes.
- **FR-2541**: O anexo MUST trazer, por lista de classificação, as inscrições com classificação no
  resultado vigente e as vagas publicadas, e MUST dizer que as listas não se somam.
- **FR-2542**: O anexo MUST trazer o cronograma em três colunas — previsto no Edital, após cada
  Retificação, e o ato registrado quando houver —, sem coluna de cumprimento.
- **FR-2543**: O anexo MUST listar os documentos publicados com data e resumo SHA-256, e MUST dizer que
  o resumo permite conferir que um arquivo tem o mesmo conteúdo do registrado no GPS, e não comprova
  sozinho a publicação oficial, cuja referência é a página pública da seleção.
- **FR-2544**: O anexo MUST definir cada número do relatório (fonte, unidade de contagem, limitação),
  listar o que o GPS não registra, e explicar a espécie e a emissão.

#### Linguagem

- **FR-2545**: Os rótulos de desfecho de convocação e de decisão de recurso MUST vir dos rótulos
  simples que o produto já mostra ao candidato, com uma exceção dita: o aceite é "convocação aceita".
- **FR-2546**: A camada executiva MUST NOT usar "aprovado", "vaga ocupada", "participaram", "marco",
  "corte", "pessoas" nem "candidatos por vaga"; o relatório inteiro MUST NOT usar "aprovado".
- **FR-2547**: O nome de cada Perfil, Etapa, marco e modalidade MUST ser o publicado no Edital vigente.
  Texto livre do Edital MUST NOT decidir situação dita pelo relatório.
- **FR-2548**: Seção sem fato produzido MUST dizer a ausência com a grafia da `040` (não se aplica,
  ainda não disponível, não publicado, parcial) ou "não registrado pelo GPS", e nunca 0 no lugar de
  fato inexistente.

#### Dados pessoais

- **FR-2549**: O relatório MUST NOT conter nome, CPF, e-mail, telefone, protocolo ou identificador de
  candidato.
- **FR-2550**: Fatos públicos por ato (vagas e classificação publicada) MAY ser desdobrados por lista
  de concorrência; fatos não públicos (eliminação, ocorrência, recurso, convocação, ocupação,
  rascunho) MUST aparecer só por Perfil, sem cruzar com modalidade.
- **FR-2551**: Em Perfil com menos de cinco inscrições enviadas, os fatos não públicos MUST ser
  omitidos com a frase de D-006, e os totais do Edital MUST continuar contando-os.

#### Forma

- **FR-2552**: O PDF MUST ter, em toda página, a identificação do Edital, o instante dos dados, a
  natureza gerencial e a paginação; e marcadores de navegação para as seções.
- **FR-2553**: A página MUST seguir a política de conteúdo vigente (estilo e script só por arquivo),
  ter tabelas com cabeçalho associado, e não exigir rolagem horizontal do corpo a 375 px.

### Key Entities

- **Relatório do Edital**: leitura derivada, não persistida — instante de referência, espécie, duas
  situações, frases da visão geral, indicadores, pendências, registros posteriores, seções do anexo.
- **Emissão**: evento de auditoria — Edital, instante de referência, ator, número, resumo SHA-256.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-932**: Em conversa com ao menos três destinatários de fora da operação, cada um diz, só com a
  primeira página, o que foi oferecido, o que saiu e o que ainda falta, sem ajuda.
- **SC-933**: Em todo relatório gerado nos testes, cada número coincide com o da regra e da fonte que
  a tela de gestão correspondente usa (zero divergência).
- **SC-934**: Nenhum relatório gerado nos testes contém nome, CPF, e-mail ou protocolo de candidato do
  banco de teste, nem fato não público cruzado com modalidade.
- **SC-935**: A espécie é a esperada em 100% dos estados de teste: inscrições abertas, encerrado com
  pendência, encerrado sem pendência, cancelado.
- **SC-936**: Gerar o relatório faz o mesmo número de leituras ao banco com dez vezes mais inscrições.
- **SC-937**: Toda emissão deixa um evento na trilha com o resumo dos bytes entregues, e duas
  composições com os mesmos fatos e o mesmo instante são idênticas.
- **SC-938**: Pelo navegador, a gestão abre o relatório do Edital e baixa o PDF sem manipular banco
  nem shell (cenário demonstrável da Constituição, princípio VI).

## Assumptions

- **Os destinatários recebem o PDF de quem conduz.** Não há papel novo nem acesso da direção ao GPS
  no MVP (D-003).
- **O instante de referência é o da leitura.** O relatório não aceita data passada.
- **A circulação do PDF é interna à instituição.** A marca gerencial e o instante dos dados em toda
  página são a defesa contra o uso fora de contexto; o PDF não é ato.
- **O cenário coerente do estudo é a base dos testes de integração**, como fixture, executado pelos
  commands da aplicação com o relógio na data de cada ato.
- **O volume real é de centenas a poucos milhares de inscrições por Edital.** Medido no estudo: a
  leitura completa fez 145 consultas com 38 e com 362 inscrições.

## Decisões

### D-001 — Um documento, duas camadas, uma derivação

A camada executiva e o anexo técnico vêm da mesma leitura, e a página e o PDF também. Dois relatórios
— um para a direção, outro para a equipe — seriam duas derivações dos mesmos números, que podem
divergir, e duas emissões a auditar.

### D-002 — A espécie é derivada; "encerramento" não diz "concluído"

O título diz acompanhamento, encerramento ou interrupção por regra (FR-2523), e o de encerramento diz
o limite do que o GPS acompanha (FR-2525). Decisão do usuário de 24/10/2026: *"A ausência de pendências
conhecidas no GPS não deve ser comunicada como comprovação de conclusão de atividades externas"*.

### D-003 — A porta é a da Supervisão, e não há permissão nova

Quem conduz o Processo — gestão do escopo ou presidência — é quem precisa responder e quem já lê
todos os números do relatório nas telas donas. Uma permissão de leitura gerencial ou um papel de
Direção ficam para quando houver destinatário com acesso ao sistema; a pendência é a mesma da `040`.

### D-004 — Inscrição, cadastro e pessoa são coisas diferentes, e o relatório só conta as duas primeiras

O cadastro de candidato é único por e-mail confirmado, não por pessoa, e o CPF é declarado, não
comprovado. Decisão do usuário de 24/10/2026 (ajustes A e B): o relatório não afirma pessoas, e fala
em **inscrições por vaga**. O anexo diz os cadastros distintos, com a definição.

### D-005 — A emissão guarda o resumo, e não os bytes

O evento de auditoria com o resumo SHA-256 prova o que foi emitido sem tabela nova. Guardar os bytes
só se justificaria se alguém precisasse baixar uma emissão antiga; fica como evolução.

### D-006 — Fato não público só por Perfil, e omitido em Perfil com menos de cinco inscrições

Ocultar célula não protege: o número volta por diferença entre totais. Por isso o desenho evita
o cruzamento em vez de esconder o resultado dele: fato público por ato — vagas, classificação
publicada — pode ser desdobrado por lista; fato não público — eliminação, ocorrência, recurso,
convocação, ocupação, rascunho — só por Perfil. A convocação para uma vaga reservada única, dita por
lista, apontaria a pessoa da primeira posição publicada. Em Perfil com menos de cinco inscrições, o
detalhe não público some com a frase *"detalhe omitido: menos de 5 inscrições neste perfil"*. O limiar é
revisável pelo usuário e pelo encarregado de dados.

### D-007 — Conferir pendência ao encerrar fica fora

Encerrar o Edital continua sem conferir pendência, e o encerrado continua admitindo atos. É achado
registrado no estudo; mudá-lo é regra de negócio da `001`, e a decisão é do usuário. O relatório
funciona em qualquer das escolhas.

### D-008 — "Perfil de vaga", com o nome cadastrado

O cabeçalho diz "Perfil de vaga" e a linha diz o nome do Perfil como publicado ("Professor de
Informática"). "Oferta" foi recusada na `040` como segundo nome para o mesmo conceito, e o princípio I
da Constituição o proíbe; o nome cadastrado já é o termo do Edital.

## Pendências do usuário

- **SC-932** espera a conversa com destinatários reais.
- **D-006**: o limiar de cinco inscrições pede manifestação do encarregado de dados.
- **D-007**: conferir pendência antes de encerrar o Edital.
- **D-003**: leitura pelo auditor e papel de Direção.
