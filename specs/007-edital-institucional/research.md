# Fase 0 — Pesquisa e decisões

**Feature**: 007 — Edital Institucional | **Data**: 2026-08-30

Nenhum `NEEDS CLARIFICATION` restou do `/speckit-clarify`. Este documento registra as decisões de
desenho que o plano tomou, e — o que importa mais — **as alternativas recusadas e por quê**, para
que a implementação não as reabra.

---

## D-001 — Onde vive a formatação humana

**Decisão**: um módulo próprio, `publicacoes/infrastructure/humano.py`, chamado pelo compositor.

**Racional**: FR-001 declara que a formatação humana é responsabilidade exclusiva da materialização.
Uma regra que vive espalhada por três pontos do compositor é uma convenção; uma regra que vive num
módulo nomeado é verificável por teste e visível em diff. A revisão externa desta spec mostrou que a
fronteira canônica é fácil de atravessar por descuido — o módulo é a resposta barata a isso.

**Alternativas recusadas**:

- *Formatar no snapshot.* Viola FR-001 e P-002, e custaria o hash, a reprodutibilidade e o
  endereçamento da Retificação de uma vez.
- *Formatar no serializer da forma publicada.* Mesma violação, um passo mais discreta: a forma
  publicada é conteúdo canônico, não apresentação.
- *Filtro de template Django.* Não serve: o documento é PDF composto em Python, não HTML.
- *`django.utils.formats` com `L10N`.* Traria dependência de configuração de locale e de estado
  global do processo para uma regra que precisa ser determinística — o mesmo documento tem de sair
  igual em qualquer ambiente. Três linhas de `str` resolvem sem essa superfície.

---

## D-002 — O estado do Evento sai; não é traduzido

**Decisão**: `Situação: PLANEJADO` deixa de ser composto. Não recebe mapa de tradução.

**Racional**: existe um precedente de tradução no próprio compositor — `RESERVA`
(`pdf.py:37-41`) traduz `reserveType` para "limitado", "ilimitado", "não há". A tentação é imitá-lo.
Mas os dois casos são diferentes: o tipo de cadastro reserva **descreve a vaga** e interessa ao
candidato; o estado do Evento **descreve a execução do certame** e é informação de gestão. Um Edital
publicado não diz que suas inscrições estão "planejadas" — ele as anuncia.

**Alternativa recusada**: *mapa `PLANEJADO → "Planejado"`.* Produziria um documento gramaticalmente
correto que continua dizendo ao candidato algo que não é matéria de Edital, e criaria um mapa a
manter para sempre.

---

## D-003 — A identificação institucional do Processo entra na raiz do snapshot

**Decisão**: a raiz ganha `processoCode` e `processoTitle`, chaves planas ao lado de `processoId`.

**Racional**: verificado que a raiz leva `schemaVersion`, `editalId`, `processoId`, `number`,
`year`, `title`, `description` e as quatro coleções (`publish_edital.py:142-154`), e que
`render_edital_pdf` é função pura do snapshot. Sem o campo, o documento não tem como nomear o
Processo — foi a contradição que a revisão da spec encontrou. Com ele, o snapshot passa a bastar
para compor o documento sem consultar o banco, que é o que a Constituição pede da cadeia "dados
estruturados → versão homologada → PDF".

O dado já está carregado: `_locked_edital` faz `select_related("processo")`
(`publish_edital.py:158-163`). Não há consulta adicional.

**Alternativas recusadas**:

- *Objeto aninhado `"processo": {...}`.* Criaria o caminho `/processo/title`, que **parece** uma
  sub-entidade retificável e não é. Chaves planas mantêm a raiz plana, como `editalId` já é.
- *O renderizador consulta o Processo pelo `processoId`.* Quebraria a pureza da função de
  renderização e faria o documento depender do estado atual do banco, não do conteúdo publicado —
  exatamente o que a imutabilidade da Publicação existe para impedir.
- *Manter o UUID e apenas movê-lo para um rodapé técnico.* Contraria a instrução de não expor
  identificador ao candidato; apenas desloca o problema.

### D-003.1 — A identidade da raiz passa a ser protegida (revisão desta decisão)

**Decisão revista**: os campos de identidade da raiz — `editalId`, `processoId`, `processoCode`,
`processoTitle`, `schemaVersion` — deixam de ser endereçáveis por Retificação.

**Por que a decisão mudou.** A primeira redação registrou a exposição como limite herdado e não a
corrigiu. A revisão externa mostrou que o argumento não fecha: a exposição é anterior, mas **é esta
feature que a ativa**. Até aqui, `/processoId` era um UUID que nada identificava para quem lê; a
partir de FR-004, `processoTitle` é o nome que o documento publicado dá ao Processo. Uma Retificação
faria o Edital nomear outro Processo — e o princípio II não estaria atendido, apenas declarado.

Herdar uma exposição é aceitável. Ativá-la e deixá-la aberta não é.

**Por que não é alterar a gramática (P-005).** `colecoes.py` é o registro declarativo das regras de
endereçamento, e já contém `LISTAS_DE_CONTROLE`, consultado por `_recusar_controle_interno`
(`publicacoes/domain/changes.py:167-173`). A correção é **um segundo conjunto declarado** no mesmo
módulo e **uma condição a mais na recusa que já existe** — a mesma via de extensão que a `006` usou
ao declarar `/stages` e `/sections`. Nenhum caminho novo, nenhum operador novo, nenhuma forma nova.

**Escopo da proteção, e o que fica fora.** Protegidos: os cinco campos de identidade e metadado.
Fora, deliberadamente: `title` e `description`, que são retificáveis por desenho e a tela já oferece;
e `number` e `year`, que são identidade e já são impressos no cabeçalho desde antes desta feature —
não são ativados por ela, e uma Retificação que corrija erro de numeração é discussão legítima que
esta feature não precisa resolver. **Fica registrado como questão aberta, não como tarefa.**

**Alternativa recusada**: *validação pós-aplicação comparando o conteúdo consolidado com a
Publicação-base.* Recusaria mais tarde, com mensagem pior, e duplicaria em outro lugar uma regra que
o registro declarativo já sabe expressar.

---

## D-004 — Autoridades signatárias: catálogo declarado, não entidade

**Decisão**: `publicacoes/domain/autoridades.py`, tupla declarada com chave estável, nome, cargo e o
identificador institucional que `Publicacao.signatory_id` já exige, no mesmo padrão de
`editais/domain/secoes.py`. O identificador nunca é digitado, exibido ao operador nem impresso.

**Racional**: o achado da auditoria era estreito — "publicar exige digitar um UUID à mão". A resposta
proporcional é oferecer uma escolha, não construir um cadastro. O catálogo declarado dá o que se
precisa (escolha, sem digitação, revisável em diff, sem migration) e não traz o que não se precisa
(entidade, tela, permissão, ciclo de vida, migração de dados). O mesmo argumento que a `006` usou
para o catálogo de seções vale aqui, e usar o mesmo padrão duas vezes é o que o torna um padrão.

Autoridade retirada do catálogo não afeta Publicação já praticada: a Publicação **já persiste** nome,
cargo e identificador no ato, e esse registro é imutável.

**Alternativas recusadas**:

- *Entidade com tela de gestão.* Feature dentro da feature: modelo, migration, tela, permissão,
  desativação, e a pergunta de o que fazer com autoridade desativada que já assinou.
- *Configuração por `settings` ou variável de ambiente.* A mesma instalação em dois ambientes
  assinaria com listas diferentes, e a lista sairia do diff revisável.
- *Integração com diretório institucional.* Fora de escopo declarado.

---

## D-005 — "Concluída" é gravada, não visitada

**Decisão**: a etapa do assistente é "pronta para revisar" enquanto nunca foi gravada, e "concluída"
depois da primeira gravação.

**Racional**: o sinal já existe e não custa nada. `SecaoEdital` só tem linha depois da primeira
edição — ausência de linha significa "texto padrão do catálogo", como a `006` declarou
(`publish_edital.py:64-72`). Logo `edital.secoes.exists()` responde exatamente "esta etapa já foi
gravada", sem estado novo.

**Alternativa recusada**: *marcar por visita.* Exigiria persistir "esta pessoa abriu esta etapa", por
Edital e por pessoa — estado novo, sem valor normativo, que ainda por cima afirmaria revisão onde
houve apenas exibição. É mais caro e diz algo menos verdadeiro.

---

## D-006 — Um conjunto de ações, três lugares fundidos

**Decisão**: `interface/acoes.py` passa a ser o único lugar que responde "o que se pode fazer com
este Edital, e o que não se pode e por quê".

**Racional**: os achados 07, 08 e 09 têm uma causa só, e é dispersão. Hoje existem
`ACOES_POR_SITUACAO` (`views.py:61-67`, usado pela listagem, e que **já conhece** a permissão
`retificacao:elaborar`), `atos.disponiveis` (usado pelo detalhe), e um `<li>` fixo com `Retificar`
no template (`detalhe.html:74`) fora dos dois. O `{% empty %}` observa apenas `atos`
(`:86-94`) — daí o cartão que oferece uma ação e diz que não há ação.

A previsão de recusa não precisa nascer: `atos.impedimento` e `_pendencias` já existem e já são
calculadas no `detalhe`. `praticar_ato` já as combina em `recusa_certa` (`views.py:849-861`). O que
falta é usar a mesma combinação onde o ato é **oferecido**, e não só onde é confirmado.

**Alternativa recusada**: *corrigir cada achado no seu lugar.* Três correções pontuais deixariam as
três fontes de verdade de pé, e a próxima ação criada voltaria a divergir.

---

## D-007 — Renumerar o catálogo de seções é seguro

**Decisão**: as três seções novas entram nas posições que FR-008 fixa, renumerando o `order` das
existentes.

**Racional**: a identidade de uma seção é `uuid5(NAMESPACE, f"{edital_id}:{key}")`
(`editais/domain/secoes.py`), derivada da **chave**, não da ordem. Renumerar não move identidade,
não quebra endereçamento e não invalida Retificação por identidade. O que muda é `order` dentro do
conteúdo publicado — e Editais publicados na versão 2 já estarão irretificáveis por versão canônica,
o que a precondição de implantação cobre.

**Alternativa recusada**: *acrescentar as três no fim para não renumerar.* Produziria um Edital cuja
apresentação vem depois das disposições finais. A ordem das seções **é** conteúdo normativo, e a
`006` decidiu deliberadamente que o documento a respeita.

---

## D-008 — O que **não** entra, tendo sido considerado

Registrado para que a implementação não os reabra:

| Considerado | Recusado porque |
|---|---|
| Proteger `number` e `year` da raiz na Retificação | Identidade já impressa antes desta feature e **não ativada** por ela; correção de numeração é discussão legítima. Questão aberta, registrada em D-003.1 |
| Mapa de tradução para o estado do Evento | D-002 |
| Objeto `processo` aninhado no snapshot | D-003 |
| Entidade de Autoridade Signatária | D-004 |
| Rastrear visita de etapa | D-005 |
| Diff de conteúdo na auditoria | FR-043 proíbe: registra-se a área, não a diferença |
| Estruturar `compensation` como objeto de moeda | FR-013 proíbe; um Edital descreve remuneração em prosa |
| Busca e filtro no painel | Limitação estrutural registrada, fora de escopo |
| Recolher seções longas do assistente | Limitação estrutural registrada, fora de escopo |

---

## Riscos

| Risco | Mitigação |
|---|---|
| A fixture de bytes é regenerada nas duas entregas que alteram a composição | **Não é desperdício, é consequência de FR-018**: a entrega 1 chega sem esperar o incremento canônico, e uma fixture desatualizada entre as duas seria suíte vermelha na `main`. FR-006 foi corrigido para dizer isso; o script existe desde a `006` |
| Renumerar `order` das seções passar despercebido em algum teste que fixe números | O contrato de forma canônica v3 declara a ordem final; a suíte compara contra ele |
| A unificação de ações regredir uma ação hoje oferecida | Teste por situação × papel, cobrindo as cinco situações de `ACOES_POR_SITUACAO` |
| A tela de Retificação em leitura vazar campo editável | Teste de interface com ator sem `retificacao:elaborar`, verificando ausência de campo e de envio |
