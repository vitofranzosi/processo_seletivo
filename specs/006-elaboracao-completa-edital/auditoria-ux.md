# Onde o Edital trava

**Auditoria de interface — Processos Seletivos Cefor/Ifes**

Um Edital completo foi elaborado, submetido, homologado e publicado pela interface, por dois
atores. O que se viu no caminho — e o que ainda não chega ao usuário.

| | |
|---|---|
| **Escopo** | jornada de autoria, ponta a ponta |
| **Método** | percurso real no navegador, a 1280px e a 375px |
| **Base** | feature `006 — Elaboração Completa do Edital`, recém-integrada |
| **Data** | 30/08/2026 (achado 26 acrescentado na correção da `006.1`) |

**Placar:** 4 impedem · 9 atrapalham · 13 ajustes · 6 acertos

*Achados 27 a 29 foram registrados durante a `007` e estão ao fim do documento.*

As capturas de tela numeradas de 01 a 17 acompanham este relatório e seguem a ordem do percurso.

---

## O percurso

Cada linha é uma tela atravessada de verdade, na ordem.

| # | Tela | Observação |
|---|---|---|
| 01 | Identificar-se | Sem atrito. A lista de permissões por papel é honesta. |
| 02 | Painel | A ação de criar está visível com a lista cheia, como devia. |
| 03 | Criar Processo | Campo “Ano” quebrado; ajuda desatualizada. Achados 14 e 15. |
| 04 | Detalhe do Processo | Destaca o impedimento de cancelar; não oferece elaborar. Achado 25. |
| 05 | Assistente 1/6 · Identificação | A pendência aparece na etapa que a resolve. Acerto. |
| 06 | Assistente 2/6 · Perfis | Campos próprios funcionam. Remoção sem rede. Achados 13 e 21. |
| 07 | Assistente 3/6 · Cronograma | A ordem chega ao banco. Botões inertes nas pontas. Achados 18 e 19. |
| 08 | Assistente 4/6 · Etapas | Select truncado e sem as datas que promete. Achado 22. |
| 09 | Assistente 5/6 · Conteúdo | Dois parágrafos digitados; um só sai no documento. Achado 01. |
| 10 | Assistente 6/6 · Revisão | Resume metade do Edital. Achado 02. |
| 11 | Prévia | Documento correto. Chega como download, não como tela. Achado 05. |
| 12 | Submeter · Homologar · Publicar | Consequências ditas antes. UUID digitado à mão. Achados 06 e 12. |
| 13 | Detalhe publicado | Documento por ato, nenhum “vigente”. Oferece Retificar e nega na linha seguinte. Achados 07 e 08. |
| 14 | Retificação | Comentário de código na tela; sem cotas, etapas ou seções. Achados 03 e 04. |
| 15 | Auditoria | Oito atos; quatro deles idênticos e indistinguíveis. Achado 10. |

---

## Impede

> Produz documento errado, decisão sem base, ou caminho que não termina em lugar nenhum.
> São quatro, e três deles são lacunas da entrega recém-integrada.

### 01 · Os parágrafos que a pessoa escreve somem do documento

Digitei duas frases separadas por linha em branco na seção “Dos Recursos”. O banco guardou a
quebra; o documento imprimiu um bloco corrido. O compositor quebra o texto por palavra e descarta
toda a estrutura de espaço em branco antes de paginar.

As seções textuais são o *único* texto livre do produto — é onde mora a redação normativa que
ninguém mais escreve por você. Perder parágrafo ali não é cosmético: um Edital com prazo recursal e
regra de fundamentação num parágrafo só muda de leitura.

- **Verificado:** 2 parágrafos gravados → 1 parágrafo no PDF
- **Onde:** `publicacoes/infrastructure/pdf.py`, `_quebrar()`
- **Corrigir:** quebrar o texto em parágrafos antes de paginar e compor cada um com espaço entre
  eles. É a mesma função, um `split` a mais.

### 02 · A tela de Revisão resume metade do Edital

A última etapa antes de submeter mostra Perfis e Cronograma. Não mostra Etapas de Avaliação, não
mostra as modalidades de reserva com seus percentuais, não mostra o conteúdo textual. Eram
exatamente as três coisas que a entrega acabou de criar.

Quem submete está declarando que leu. O percentual de cota é a informação mais sensível do
documento e é a que não aparece — nem no card de Perfis, que mostra só código, nome e vagas.

- **Onde:** `interface/templates/interface/compor_revisao.html` — dois cards, quatro coleções
- **Corrigir:** um card por coleção, no mesmo padrão dos dois que já existem. As modalidades entram
  como linha dentro do card de Perfis, com percentual e fundamento.

### 03 · A Retificação não alcança nada do que a entrega criou

A tela de Retificação oferece título, descrição, campos do Perfil e campos dos Eventos. Não oferece
modalidades, não oferece Etapas de Avaliação, não oferece as seções textuais — e diz
explicitamente, ao acrescentar um Perfil, que “Modalidades de Concorrência ainda não são definidas
por aqui”.

O motor aceita todas elas: os caminhos `/stages/id=…`, `/sections/id=…/content` e
`…/normativeRule/percentage` são endereçáveis e têm teste. O que falta é a tela. Na prática,
corrigir uma cota errada depois de publicado exige chamada de API — e a Constituição do projeto
proíbe considerar pronta uma jornada que dependa de canal alheio ao ator.

- **Onde:** `interface/retificacao.py` — campos editáveis param em `profiles` e `schedule`
- **Corrigir:** estender a composição por diferença às três coleções. É o mesmo mecanismo, com mais
  grupos de campos — nenhuma gramática nova.

### 04 · Um comentário de código está impresso na tela de Retificação

Logo abaixo do box “Como funciona”, o usuário lê:

> `{# As referências dos campos só significam alguma coisa contra o conteúdo que as gerou; sem esta
> linha, uma Publicação no intervalo faria a mesma referência apontar para outro item. #}`

É um comentário de template de duas linhas — e a sintaxe do Django só comenta uma.

O detalhe que dói: existe um teste escrito para exatamente esta classe de defeito, com a explicação
no próprio docstring. Ele roda contra as etapas do assistente e não contra a tela de Retificação,
que ficou fora da lista.

- **Onde:** `interface/templates/interface/retificar.html:49-50`; o teste em
  `tests/interface/test_estaticos.py` cobre 4 telas de 12
- **Corrigir:** trocar por `{% comment %}` e ampliar a parametrização do teste para todas as telas
  renderizadas, não só as do assistente.

---

## Atrapalha

> Não impede a tarefa, mas cobra um preço em cada volta: caminho que não termina, informação que
> falta na hora da decisão, esforço que a máquina poderia poupar.

### 05 · A prévia é um arquivo baixado, não uma tela

“Visualizar Edital” devolve um PDF que o navegador trata como download. O ciclo prometido — olhar,
voltar, continuar editando — vira: baixar, achar na pasta, abrir em outro aplicativo, voltar ao
navegador. Não há “voltar”: há um arquivo em Downloads.

É a ação que mais muda a percepção do produto, e a que tem mais atrito por unidade de valor.

- **Corrigir:** abrir numa tela própria com o PDF embutido e um “Voltar para a Revisão” visível — o
  que também dá lugar para a moldura de prévia fora do documento.

### 06 · Nenhuma tela de confirmação oferece ver o documento

Submeter diz que “o conteúdo atual é congelado”. Publicar diz que “o Edital torna-se público e
imutável”. Nos dois casos, o documento em questão não está a um clique — é preciso sair da
confirmação, voltar à Revisão e baixar o arquivo.

São os três momentos de maior consequência do sistema, e os únicos em que ver o conteúdo não é
oferecido.

- **Corrigir:** um link “Ver o documento” ao lado de cada confirmação.

### 07 · “Retificar” abre inteiro para quem não pode retificar

Entrei como homologador e publicador — sem a permissão de elaborar Retificações. O detalhe do
Edital publicado ofereceu “Retificar”, e a tela abriu completa: conteúdo vigente, todos os campos,
botão de acrescentar Perfil, campo de justificativa. A recusa só existe no envio.

Não há vazamento — o conteúdo vigente já é visível a quem alcança o Edital. O problema é o caminho:
a pessoa preenche tudo e descobre no fim. É o mesmo padrão que o produto combate em outros lugares,
e bem.

- **Onde:** `interface/views.py`, `retificar()` — a checagem de permissão está dentro do ramo POST;
  e `detalhe.html` renderiza o link sem checar permissão
- **Corrigir:** condicionar o link à permissão, como a listagem já faz, e mostrar a tela em leitura
  para quem não pode elaborar.

### 08 · O mesmo cartão oferece uma ação e diz que não há ação

No detalhe do Edital publicado, “O que fazer agora” lista o botão Retificar e, imediatamente
abaixo, a frase “Nenhum ato disponível para seus papéis nesta situação”. As duas coisas são
renderizadas por regras diferentes que não se falam.

- **Onde:** `interface/templates/interface/detalhe.html` — lista fixa + bloco `{% empty %}`
- **Corrigir:** um único conjunto de ações, montado no mesmo lugar, com a mensagem de vazio
  derivada dele.

### 09 · O detalhe oferece “Submeter” sabendo que será recusado

Num Edital recém-criado, o cartão de ações oferece “Submeter para revisão” enquanto o cartão logo
abaixo mostra dois erros marcados **IMPEDE**. A tela de confirmação já sabe prever a recusa e
esconde o botão nessa situação; o detalhe tem a mesma informação e não a usa.

- **Onde:** `interface/views.py` — `recusa_certa` existe em `praticar_ato`, não em `detalhe`
- **Corrigir:** reaproveitar a mesma previsão no detalhe — desabilitar com o motivo ao lado, em vez
  de esconder.

### 10 · A auditoria registra quatro edições idênticas

A trilha do Edital mostra “Alteração do rascunho · Em elaboração → Em elaboração” quatro vezes
seguidas, com carimbos de minuto em minuto. Foram Perfis, Cronograma, Etapas e Conteúdo — e nada
distingue uma da outra.

A trilha existe para responder questionamento. “Alguém mexeu no rascunho quatro vezes” não responde
nenhum. O sistema sabe qual etapa foi salva; a informação é descartada na gravação.

Contraste: “Alteração da identificação” aparece nomeada, porque tem ato próprio.

- **Corrigir:** registrar qual coleção mudou junto do evento de auditoria.

### 11 · Nenhum campo obrigatório é marcado como obrigatório

Em todo o produto não há asterisco, nem etiqueta, nem qualquer marca visual separando o campo
exigido do opcional. “Fundamento da homologação” é obrigatório e não avisa; a versão do fundamento
normativo passa a ser obrigatória quando você preenche o fundamento, e isso está explicado em prosa
numa linha de ajuda.

Descobre-se falhando. Em formulários longos, falhar significa rolar de volta procurando qual campo
o servidor recusou.

- **Corrigir:** marcar o obrigatório na etiqueta e concentrar a recusa num resumo com âncora para
  cada campo.

### 12 · Publicar exige digitar um UUID à mão

O campo “Identificador da autoridade” pede um identificador institucional em formato UUID, com um
exemplo de trinta e seis caracteres como dica. Não há busca, não há lista, não há memória da
autoridade usada da última vez — e nome e cargo são redigitados a cada publicação.

É o campo mais hostil do produto, no ato de maior consequência. Na prática, alguém vai manter esse
número num bloco de notas.

- **Corrigir:** um seletor de autoridades conhecidas, ainda que a lista comece pequena e
  configurável. O UUID deixa de ser digitado.

### 13 · Remover apaga sem perguntar e sem desfazer

“Remover este Perfil” elimina imediatamente a linha e tudo dentro dela: requisitos, modalidades,
fundamentos, percentuais. Não há confirmação, não há desfazer, e o botão fica a poucos pixels de
“↓ Descer”.

O produto é cuidadoso com atos irreversíveis de domínio e descuidado com a perda de trabalho não
enviado, que é a que acontece todo dia.

- **Corrigir:** confirmar quando a linha tem conteúdo, ou oferecer desfazer por alguns segundos.
  Afastar o destrutivo dos botões de ordem.

---

## Ajusta

> Correções pontuais. Baratas, visíveis, e várias delas resíduo da entrega que acabou de sair.

### 14 · O campo “Ano” não recebe estilo nenhum

Na criação do Processo, “Ano” fica com a aparência padrão do navegador — 22px de altura, fonte de
13px, borda entalhada — ao lado de campos de 39px e 16px. A regra de CSS cobre `input[type=text]` e
nada mais. No mesmo formulário, a classe `curto` também não tem efeito, porque só existe dentro do
agrupamento do assistente: “Número” ocupa a largura inteira contra a intenção declarada no template.

- **Medido:** 22px/13.3px/2px inset contra 39px/16px/1px solid dos vizinhos
- **Corrigir:** estender o seletor aos demais tipos de campo, ou usar o mesmo agrupamento do
  assistente nesta tela.

### 15 · A ajuda diz que a descrição não pode mais ser alterada

Sob o campo Descrição, na criação: “Depois da criação não há ato que a altere”. Deixou de ser
verdade nesta entrega — título e descrição passaram a ser editáveis enquanto o Edital está em
elaboração, e a etapa de Identificação existe justamente para isso.

- **Onde:** `interface/templates/interface/processo_criar.html`

### 16 · “Compor Perfis e Cronograma” virou nome antigo

O botão do detalhe ainda promete duas etapas. O assistente tem seis: Identificação, Perfis,
Cronograma, Etapas de Avaliação, Conteúdo e Revisão.

- **Corrigir:** “Elaborar o Edital”.

### 17 · A confirmação de ato mostra a chave interna

Depois de submeter, a faixa verde diz “Ato registrado: submeter.”; depois de publicar, “Ato
registrado: publicar.”. O rótulo humano existe — a trilha de auditoria escreve “Submissão para
revisão” e “Publicação” corretamente na tela ao lado.

### 18 · Subir na primeira linha não faz nada, e não diz nada

Todas as linhas ordenáveis mostram ↑ Subir e ↓ Descer, inclusive nas pontas onde a operação é
impossível. Cliquei em Subir na primeira linha: nada muda, nada é dito, o botão não está
desabilitado.

- **Verificado:** ordem antes e depois idênticas, sem retorno visual

### 19 · A posição de cada linha é invisível

A ordem é o dado que se está editando, e é o único que não aparece: fica num campo oculto. Toda
linha se anuncia como “EVENTO DO CRONOGRAMA”, igual à anterior. O documento imprime
“1. Inscrições”; o editor, não.

- **Corrigir:** numerar a legenda de cada linha — “Evento 2 de 3”.

### 20 · “Rascunho salvo” aparece na etapa seguinte

Salvar com “Avançar” grava a etapa atual e navega para a próxima, onde a mensagem de sucesso é
exibida. Lê-se como se a etapa recém-aberta é que tivesse sido salva.

### 21 · Uma norma real serve de exemplo na modalidade errada

Os campos de fundamento e versão trazem como dica “Lei 12.990/2014” e “2014-06-09”. Numa linha de
Ampla Concorrência, isso é uma citação legal específica — a lei de cotas — aparecendo, em cinza,
exatamente onde vai o fundamento daquela modalidade.

- **Corrigir:** dica genérica de formato, não uma norma que existe.

### 22 · O vínculo com Evento esconde justamente a data

A Etapa se vincula a um Evento para herdar as datas — é o que a ajuda promete. A lista mostra
“tipo — descrição”, corta no meio por falta de largura, e não mostra data nenhuma. Para saber que
datas está herdando, é preciso voltar ao Cronograma.

- **Corrigir:** “Prova didática · 10/04/2027 14:00” como texto da opção.

### 23 · Eliminatória e Classificatória são duas caixas soltas

As duas marcações não têm rótulo de grupo. Visualmente flutuam desalinhadas ao lado de Peso e Nota
mínima; para leitor de tela, são duas caixas sem o conceito que as une.

- **Corrigir:** agrupar sob “Caráter”, com legenda.

### 24 · A etapa Conteúdo nasce “concluída” sem ter sido aberta

Num Edital recém-criado, o passo 5 já aparece marcado como concluído — porque as seções nascem com
texto padrão e, tecnicamente, nada falta. Para quem olha, o sistema afirma que a pessoa fez algo que
ela não fez. E o marcador verde fica visualmente igual ao da etapa atual.

- **Corrigir:** um terceiro estado — “pronta para revisar” — distinto de concluída e de pendente.

### 25 · Criado o Processo, o próximo passo não é oferecido

A tela seguinte à criação destaca, em amarelo, por que o cancelamento do Processo está impedido —
uma ação que ninguém tentou. Elaborar o Edital, que é o motivo de tudo, só existe como um link
discreto no número do Edital, no cartão ao lado.

- **Corrigir:** “Elaborar o Edital 12/2027” como ação primária; o impedimento de cancelar pertence à
  tela de cancelar.

---

### 26 · A recusa culpa o campo errado ao criar Processo

Criar um segundo Processo cujo primeiro Edital repita número e ano de **qualquer** outro Edital do
escopo falha com “Identificação institucional já utilizada”. A identificação está correta; o
conflito é do Edital.

`Edital` é único por `(escopo, número, ano)` — não por Processo — e
`create_process_with_first_edital` envolve os dois `create` num único `except IntegrityError` que
sempre devolve a mensagem do Processo. Quem recebe o erro corrige o campo que não tem problema.

- **Verificado:** encontrado ao montar a demonstração navegável da correção, com um Edital 21/2027
  já existente noutro Processo
- **Onde:** `processos/application/commands.py` — um `except` para dois `create`;
  `processos/models.py` — `uq_edital_scope_number_year`
- **Corrigir:** separar as duas criações no tratamento do erro e apontar o campo e a entidade
  responsáveis pelo conflito.

## O que está bem resolvido

> Vale registrar, porque são decisões deliberadas e incomuns — e porque nenhuma correção acima deve
> custá-las.

**A consequência vem antes do ato, escrita por extenso.** Publicar não pergunta “tem certeza?”.
Lista quatro consequências concretas: o Edital torna-se imutável, correções passam a exigir
Retificação, o documento é preservado com o hash do conteúdo, a Publicação entra na consulta
pública. É melhor do que a maioria dos sistemas corporativos faz.

**A segregação de funções é avisada antes da tentativa.** Quem elaborou e homologou sozinho é
informado de que não poderá publicar — no detalhe, antes de tentar — e o botão de confirmar some da
tela do ato. A regra não é revelada pela recusa.

**Cada pendência aponta para a etapa que a resolve.** “O Edital não possui descrição” aparece dentro
da etapa de Identificação, com âncora na seção certa. E, desde esta entrega, nenhuma pendência se
declara incorrigível quando existe caminho.

**O que ainda não foi enviado é dito com essas palavras.** “alterações ainda não enviadas”, ao lado
do botão salvar, mais a oferta de restaurar o preenchimento guardado no navegador. Distinguir o que
está na tela do que está no servidor é raro e aqui está explícito.

**A trilha de auditoria é legível por gente.** Ato, autor, transição de estado e o motivo citado
entre aspas — “Conferido pela comissão de seleção; conteúdo em conformidade com a minuta aprovada.”
Sem jargão de tabela.

**A 375px não há rolagem lateral.** O assistente reflui para duas colunas, o texto continua legível,
nenhum campo estoura. O foco de teclado tem contorno forte e visível em todo o produto. A base de
acessibilidade está de pé.

---

## Limitações estruturais

> Não são defeitos: são fronteiras do que o produto se propôs a ser até aqui. Valem como pauta, não
> como correção.

| Limitação | O que significa |
|---|---|
| **Escala do formulário** | Um Perfil com duas modalidades ocupa 3.200px no celular. Três Perfis passam de oito mil. Não há recolher, resumir nem navegar dentro da etapa. |
| **Texto sem estrutura** | As seções textuais aceitam um bloco corrido. Não há lista, item numerado ou ênfase — e um Edital real é feito de artigos e incisos. |
| **Nenhuma noção de passagem de bastão** | Submetido, o Edital fica “aguardando” sem dizer quem deve agir. Não há fila, aviso nem indicação de responsável. |
| **Sem busca nem filtro** | O painel lista tudo. Com algumas dezenas de Processos, encontrar um vira rolagem. |
| **Conjunto de seções fixo** | Decisão deliberada e registrada. Mas o primeiro Edital que precisar de uma seção a mais vai esbarrar nela. |
| **Autenticação ainda é um seletor** | A identidade é escolhida numa tela. O aviso está em todas as páginas, e nada aqui pode ir a produção antes disso mudar. |

---

## Por onde eu começaria

Uma sequência que compra mais confiança por hora gasta:

1. **Parágrafos no documento** (01) — é o único que produz Edital errado, e é uma tarde.
2. **Revisão completa** (02) — sem ela, ninguém revisa o que a entrega criou.
3. **O pacote de resíduos** (04, 15, 16, 17) — comentário na tela e textos desatualizados custam
   pouco e são o que mais barateia a percepção do produto.
4. **Prévia como tela** (05) e **prévia nas confirmações** (06) — juntos, fecham o ciclo de olhar e
   voltar.
5. **Retificação alcançando cotas, etapas e seções** (03) — é a maior, e depende de decisão de
   produto sobre até onde a tela vai.

Os três primeiros itens são reparo da entrega recém-integrada. O quarto e o quinto são produto.

---

## Achados registrados durante a `007`

> Encontrados ao implementar, e **não corrigidos ali** — a trava da `007` diz que achar uma
> necessidade plausível durante a implementação não autoriza incluí-la (P-001). Ficam como insumo
> de priorização.

### 27 · ~~As recusas do servidor não sabem a que campo pertencem~~ — CORRIGIDO

FR-033 pede resumo de erros **com âncora para cada campo** e a mensagem junto do campo. As recusas
do cliente já fazem isso — `validacao.js` associa a mensagem ao controle e limpa a marcação ARIA
quando o campo é corrigido. As do servidor, não: `ProfileValidationError`, `ScheduleValidationError`
e `StageValidationError` carregam **mensagem e nada mais**.

A `007` entregou primeiro só o resumo focalizável e anunciado, e eu registrei a âncora por campo
como achado — **erradamente**. Revisão de código apontou que FR-033 é requisito aprovado *antes* da
implementação, não necessidade descoberta depois: registrá-lo aqui era reclassificar um débito como
descoberta. Corrigido na mesma feature.

A correção foi a que a revisão sugeriu e é pequena: as três exceções ganharam `campo` e `identidade`
**opcionais**, `DomainError` os propaga, e a interface os resolve para o `id` do controle daquela
linha. Regras que valem para a coleção inteira — "o Edital deve possuir ao menos um Perfil" —
continuam sem âncora, porque apontar um campo qualquer seria pior do que não apontar.

**Foram precisas duas voltas.** Na primeira, o `<span>` da recusa aparecia ao lado do controle mas
o controle não o referenciava: `role="alert"` anuncia a mensagem quando ela surge, e não cria
vínculo — quem volta ao campo depois não tem como saber que aquela mensagem lhe pertence. A segunda
volta acrescentou `aria-invalid` e a referência em `aria-describedby`, preservando a ajuda que já
existia, e levou a mesma estrutura à criação de Processo, onde as recusas ainda viravam uma frase
agregada ("Encurte: A, B.").

- **Onde:** `editais/domain/{perfis,cronograma,etapas}.py` — exceções sem identidade de campo
- **Consequência hoje:** numa recusa como "reserva limitada sem limite", a pessoa lê o resumo e
  procura a linha sozinha
- **Custo de corrigir:** dar às exceções de domínio um campo opcional de caminho, e propagá-lo pela
  interface. Pequeno, mas atravessa a fronteira domínio/interface

### 28 · `/number` e `/year` continuam endereçáveis por Retificação

A `007` protegeu os cinco campos de identidade da raiz — `editalId`, `processoId`, `processoCode`,
`processoTitle` e `schemaVersion` — porque passou a **depender** deles para o documento nomear o
Processo. `number` e `year` ficaram fora: são identidade e já eram impressos no cabeçalho antes
desta feature, e uma Retificação que corrija erro de numeração é discussão legítima.

Está registrado em `research.md` D-003.1 e tem teste que documenta o estado atual — se alguém
decidir protegê-los, é lá que a decisão aparece.

- **Pergunta de produto:** corrigir o número de um Edital publicado é Retificação, ou é outro ato?

### 29 · O rótulo do Evento no seletor de Etapa quase saiu vazio

Não é defeito do produto: é registro de método. Ao trocar o texto da opção de `tipo — descrição`
para incluir a data, o template passou a ler `evento.rotulo` e o campo **não chegou a ser criado**
em `forms.py` — um script de edição falhou antes de gravar e eu conferi só o template.

A suíte inteira continuou verde: nenhum teste olhava o texto da opção. O defeito apareceu no
navegador, com um `<option>` vazio — pior do que a lista truncada que existia antes.

- **Corrigido na própria `007`**, com teste que falha de verdade quando o defeito é reintroduzido
- **A lição:** um teste que verifica "o campo existe" não substitui um que verifica "o que o
  usuário lê". A demonstração navegável pegou o que 993 testes não pegaram
