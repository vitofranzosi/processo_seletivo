# Feature Specification: Duplicar Perfil

**Feature Branch**: `claude/busy-wing-3e9314`

**Created**: 2026-09-25

**Status**: Draft

**Input**: Decisão do usuário em 25/09/2026 — esta é a próxima spec, **antes** do recorte documental.
Evidência: o [estudo de esforço de 21/09](../../doc/estudo-esforco-de-cadastro-2026-09-21.md), §4,
§6.2, §6.4, §8 e §13 (*"E1 — Reaproveitamento dentro do Edital"*).

> **Faixa de identificadores.** Abre em **FR-634** e **SC-230**. Teto medido em 2026-09-25 em todas
> as worktrees (`git worktree list`) **e** em todas as branches remotas: `FR-633` / `SC-229` /
> `UX-066`. **Nenhum `UX-` é definido.** As **decisões** reiniciam em `D-001`.

> **Teto proporcional.** **Uma** história comprometida. Esta feature acrescenta **uma** operação de
> autoria de rascunho — duplicar — e não muda regra de negócio nenhuma: o que a cópia contém é o que
> a origem já continha, e toda validação que a origem atravessa a cópia atravessa igual. As
> variações do mesmo mecanismo ficam **fora**, por decisão do usuário (§4).

## Clarifications

### Session 2026-09-25

- Q: *Aplicar estas Modalidades a todos os Perfis* e *aplicar este marco aos demais* entram nesta
  spec? → A: **Não.** A `043` é só duplicar Perfil. As duas são **propagação em massa** — mudar
  estruturas que já existem —, com semântica e regra de conflito próprias, e merecem specs
  próprias. Ficam registradas como trabalho futuro (§5), e não como resolvidas aqui.
- Q: Documentos Exigidos recortados pelo Perfil de origem, ou por Modalidade dele, são copiados? →
  A: **Não.** Duplicar atua sobre o Perfil e sobre o que estruturalmente pertence a ele; uma ação da
  etapa Perfis não produz, de forma implícita, registro na etapa de Documentos. A tela avisa quantos
  documentos ficaram restritos à origem (`FR-645`). Multiplicar as linhas que o estudo já achou
  excessivas cristalizaria uma solução ruim para o problema documental, que tem decisão própria.

---

## 1. O problema, medido

**A etapa de Perfis custa por Perfil, e o custo é quase todo repetição.**

No Edital 140/2025 (16 Perfis, 64 Modalidades), a etapa de Perfis custou **~530 interações**, das
quais **~430 sem informação nova** — quatro em cada cinco (estudo §4, §6.2). Entre um Perfil e o
seguinte mudam **2 de ~33 campos**: Código e Localidade. Onze dos dezesseis compartilham até a
denominação; as quatro Modalidades, com percentual e fundamento, são idênticas nos dezesseis; carga
horária e remuneração, idem; sete das oito linhas de requisito, idem.

**A curva é estritamente linear, e nada a dobra** (estudo §8):

| Perfis | Campos | Sem informação nova |
|---:|---:|---:|
| 1 | 33 | 0 |
| 16 *(140/2025, medido)* | ~530 | ~430 |
| 66 *(certame multicampi, projeção)* | ~2.200 | ~1.900 |

**Não é capacidade escondida.** O estudo varreu o código (§6.4): os fragmentos de Perfil,
Modalidade e marco só criam linhas **vazias**. O produto tem reuso de Edital inteiro (`023`) e
nenhum reuso de parte — e como o reuso entre Editais exige origem publicada, **a primeira oferta de
cada família é sempre composta do zero** (estudo §13, E3). Nada entregue até o PR #166 reduziu essa
curva.

**Estimativa, não medida, que orienta os critérios de sucesso.** Com *Duplicar Perfil* e ~6
interações por cópia (duplicar, Código, Localidade, confirmar e dois ajustes), os 16 Perfis do
140/2025 cairiam de ~530 para **~120** interações: ~33 para o primeiro, ~6 para cada um dos quinze
seguintes. A curva continua linear — mas a inclinação cai de ~33 para ~6, e os 66 Perfis do
multicampi, de ~2.200 para ~430.

---

## 2. O que esta feature NÃO é

- **Não é mover conteúdo para o nível do Edital** (estudo §13, E2). Modalidades, requisitos,
  critérios de desempate, carga horária e remuneração continuam **declarados por Perfil**, e o
  conteúdo publicado continua por Perfil. A Constituição fixa que *"Cotas DEVEM ser definidas por
  Perfil"*; esta feature não a tensiona.
- **Não é o recorte documental.** A pergunta de como declarar "documento de todo candidato PcD" está
  em [doc/decisao-recorte-documental.md](../../doc/decisao-recorte-documental.md), aberta, e fica lá.
- **Não reduz o documento publicado.** O PDF do 140/2025 continua com a repetição por Perfil (34
  tabelas em 27 páginas). Esta feature barateia **escrever** a repetição, e não a elimina — o que a
  eliminaria é E2.
- **Não é Retificação.** Duplicar é autoria de rascunho: só existe enquanto o Edital está em
  elaboração. Acrescentar Perfil a Edital publicado continua sendo o que a Retificação já faz, pelo
  caminho dela.
- **Não é canal novo.** A API de rascunho já aceita qualquer carga, e quem grava por ela pode copiar
  o que quiser; o que falta é a operação na **interface** de quem compõe.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Duplicar um Perfil e mudar só o que muda (Priority: P1) 🎯 MVP

Quem compõe o Edital acabou de preencher o Perfil LP01 — tutor de Letras, polo de Vitória, quatro
Modalidades com percentual e fundamento, quadro de vagas, requisitos, carga horária, remuneração,
atribuições, fatos declarados e o marco de classificação com três critérios de desempate. O próximo
Perfil, LP02, é o mesmo tutor em outro polo.

Na etapa Perfis, junto ao cartão do LP01, a pessoa aciona **Duplicar**. O sistema pergunta o
**Código** e a **Localidade** do Perfil novo, e só isso. Ela informa `LP02` e `Serra`. Aparece,
logo abaixo do LP01, um cartão LP02 com tudo o que o LP01 tinha, e o foco vai para ele. Se o LP02
tiver alguma diferença — uma linha de requisito, uma quantidade —, ela a ajusta ali. Repete a partir
do LP02 para chegar ao LP03, e assim até o LP16. Grava a etapa uma vez, como sempre gravou.

**Why this priority**: é a única mudança que muda a **ordem de grandeza** do esforço em Editais
multipolo, que são quatro dos cinco da amostra (estudo §13, E1). Sem ela, o custo da §8 é pago a
cada família.

**Independent Test**: compondo pela interface um Edital com um Perfil completo — Modalidades com
ampla concorrência declarada, quadro com linhas reservadas, fatos declarados e marco com critério de
desempate que cita fato —, duplicar três vezes, gravar, submeter, homologar e publicar. O documento
publicado traz quatro Perfis com o conteúdo da origem e os Códigos e Localidades informados, e
nenhum identificador de um Perfil aparece no conteúdo de outro.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração com o Perfil LP01 completo na tela, **When** quem compõe
   aciona *Duplicar* no LP01 e informa Código `LP02` e Localidade `Serra`, **Then** surge um Perfil
   LP02 imediatamente após o LP01, com todos os campos do LP01 exceto Código e Localidade, e o foco
   passa para ele.
2. **Given** o LP02 recém-duplicado, **When** quem compõe grava a etapa, **Then** os dois Perfis são
   gravados, o LP01 fica exatamente como estava, e o LP02 tem identidade própria em tudo o que
   possui: Perfil, Modalidades, regra normativa, linhas do quadro, fatos declarados, marcos e
   critérios de desempate.
3. **Given** o LP01 com uma Modalidade declarada como ampla concorrência e linhas reservadas no
   quadro, **When** ele é duplicado, **Then** no LP02 a ampla concorrência declarada é a Modalidade
   **do LP02** correspondente, e cada linha reservada do LP02 aponta a Modalidade **do LP02**
   correspondente — nunca uma do LP01.
4. **Given** um marco do LP01 com critério de desempate que cita um fato declarado do LP01 e que
   ordena Etapas do Edital, **When** ele é duplicado, **Then** o critério do LP02 cita o fato
   **do LP02** correspondente, e as Etapas citadas continuam sendo as mesmas Etapas do Edital.
5. **Given** o LP01 com edições digitadas e ainda não gravadas, **When** ele é duplicado, **Then** a
   cópia traz o que está **na tela**, e não o que estava gravado.
6. **Given** o LP02 duplicado e não gravado, **When** quem compõe o remove antes de gravar, ou sai
   da etapa sem gravar, **Then** o LP01 gravado permanece intacto.
7. **Given** o LP02 duplicado e não gravado, **When** quem compõe o duplica de novo para chegar ao
   LP03, **Then** o LP03 nasce do LP02 com as mesmas garantias — duplicar não exige gravar antes.
8. **Given** um Perfil com Código `LP01` na tela, **When** quem compõe tenta duplicar informando
   Código `LP01`, ou Código vazio, **Then** a cópia não é criada e a tela diz por quê, no campo.
9. **Given** um Edital que a pessoa lê mas não pode compor — por falta de permissão ou porque saiu
   da elaboração —, **When** ela abre a etapa Perfis, **Then** *Duplicar* não é oferecido, e a
   operação pedida diretamente é recusada.
10. **Given** o LP01 gravado com dois Documentos Exigidos recortados por ele — um pelo Perfil, outro
   pela Modalidade PcD dele —, **When** ele é duplicado, **Then** nenhum Documento Exigido é criado,
   e junto à cópia a tela diz que **2** documentos restritos à origem não foram replicados.

---

### Edge Cases

Estes são requisitos — nenhum deles tem identificador, e por isso a rastreabilidade do plano deve
cobri-los um a um, como os `FR-`.

- **Marco com identidade derivada da origem.** O marco nasce com código e denominação derivados do
  Perfil (`FR-420` da `030`): o marco do LP01 chama-se `LP01`. Copiado ao pé da letra, o LP02 teria
  um marco `LP01`. Tratado em `FR-644` e `D-004`.
- **Perfil sem Modalidade, sem marco ou sem fato.** Duplica; a cópia não tem o que a origem não
  tinha.
- **Perfil sem ampla concorrência declarada.** A cópia também não declara nenhuma — `nenhuma` não é
  referência a remapear.
- **Origem com erro de regra na tela** (por exemplo, percentual acima de 100 numa Modalidade, ou
  limite de Cadastro Reserva em reserva ilimitada). Duplicar copia o que está digitado, inclusive o
  erro; a recusa acontece na gravação, como para qualquer Perfil, apontando o campo do Perfil em que
  ele está.
- **Origem com valor ilegível na tela** (por exemplo, `dez` no campo de vagas). É outro caso: o
  valor não chega a ser lido, e não há o que copiar. Duplicar **recusa**, no diálogo, dizendo que o
  Perfil de origem tem campo que precisa ser corrigido antes — e nenhum cartão é criado.
- **Código informado que colide com Perfil ainda não gravado.** A colisão é conferida contra os
  Perfis **na tela**, e não só contra os gravados; a gravação continua recusando Código repetido
  no Edital, que é a autoridade final.
- **Documentos Exigidos de escopo "Todos os Perfis".** Valem para a cópia sem cópia nenhuma — é o
  escopo deles.
- **Documentos Exigidos recortados pelo Perfil de origem**, ou por uma Modalidade dele. Não são
  copiados, e a tela diz quantos são (`FR-645`). A contagem é a dos documentos **gravados**: os
  documentos são da etapa de Documentos, e Perfil ainda não gravado não tem documento recortado
  por ele — a contagem é zero, e o aviso não aparece.
- **Campos que nenhuma etapa desenha** (informação de classificação e de convocação, que só chegam
  por API). Não são copiados — `FR-643`.
- **Etapa de Documentos antes de gravar.** O Perfil duplicado e não gravado ainda não aparece como
  escolha de recorte na etapa de Documentos; aparece depois de gravado, como qualquer Perfil
  acrescentado.
- **Rascunho local.** Se a gravação não chegar ao servidor, o rascunho local recupera da cópia
  **o mesmo** que recupera de qualquer Perfil acrescentado — e isso é menos do que parece: ele só
  restaura os campos do próprio Perfil, e não Modalidades, quadro nem fatos, de Perfil nenhum
  (`G-006`, lido no código em 25/09). A cópia não agrava a limitação; a torna mais cara, porque o
  valor dela está justamente no que o rascunho local não restaura. *Corrigido na escrita do plano:
  a primeira redação afirmava que as cópias voltavam inteiras.*
- **Marcos não aparecem na etapa Perfis.** Eles são da etapa Classificação, e a gravação da etapa
  Perfis os preserva do que está gravado. A cópia os leva sem desenhá-los, e diz quantos leva
  (`FR-650`); depois de gravada, eles se editam na Classificação como os de qualquer Perfil.
- **Fato removido da cópia antes de gravar**, sendo citado por critério de desempate de um marco
  que ela leva. A gravação recusa, como recusaria para qualquer Perfil — o critério apontaria fato
  que não existe.
- **Edital com muitos Perfis.** Com dezenas de cartões, a cópia aparece junto à origem e recebe o
  foco — quem duplica não precisa reencontrar o fim da página (estudo §8).

## Requirements *(mandatory)*

### A operação

- **FR-634**: Quem pode compor o Edital DEVE poder, na etapa Perfis do assistente de composição,
  criar um Perfil novo a partir de qualquer Perfil presente na tela — gravado ou ainda não gravado.
- **FR-635**: Ao duplicar, o sistema DEVE pedir o **Código** e a **Localidade** do Perfil novo, e
  NÃO DEVE criar a cópia sem Código, nem com Código igual ao de outro Perfil presente na tela. A
  recusa DEVE dizer o motivo junto ao campo. A **Localidade é opcional**, como no próprio Perfil:
  Editais de curso não a declaram (estudo §7), e vazia é vazia na cópia — nunca a da origem.
- **FR-636**: A cópia DEVE partir do que está **digitado** no Perfil de origem no momento de
  duplicar, e não do que está gravado. O que a etapa Perfis não desenha — os marcos
  classificatórios, que são da etapa Classificação — DEVE vir do que a origem tem gravado, ou, se a
  origem é ela mesma uma cópia ainda não gravada, do que ela recebeu da própria origem.
- **FR-637**: A cópia DEVE aparecer imediatamente após o Perfil de origem, e o foco DEVE passar para
  ela, com anúncio perceptível por leitor de tela. A operação DEVE ser alcançável por teclado.
- **FR-638**: Duplicar NÃO DEVE gravar nada por si. A cópia passa a existir no rascunho quando a
  etapa é gravada, como todo Perfil acrescentado; até lá, pode ser editada, duplicada de novo ou
  removida.

### O que a cópia contém

- **FR-639**: A cópia DEVE conter **todo** o conteúdo do Perfil de origem no contrato do rascunho
  — denominação, descrição, carga horária, remuneração, atribuições, requisitos, vagas
  imediatas, Cadastro Reserva e limite, forma de convocação e reversão de vagas, Modalidades com a
  regra normativa, a declaração de qual Modalidade é a ampla concorrência, as linhas do quadro de
  vagas, os fatos declarados e os marcos classificatórios com seus critérios de desempate —, exceto
  Código e Localidade, que vêm de `FR-635`, e os campos de `FR-643`. A completude DEVE ser conferida contra o contrato
  inteiro do Perfil, e não campo a campo escolhido: campo acrescentado ao Perfil no futuro e
  esquecido aqui DEVE reprovar a conferência.
- **FR-640**: Tudo o que a cópia contém e que tem identidade DEVE receber identidade **nova**:
  Perfil, Modalidades, regra normativa, linhas do quadro, fatos declarados, marcos e critérios de
  desempate. A linha geral do quadro DEVE ter a identidade derivada do Perfil **novo**, pela mesma
  regra que já a deriva para qualquer Perfil.
- **FR-641**: Referências **internas** ao Perfil DEVEM ser trocadas pela contraparte na cópia: a
  Modalidade declarada como ampla concorrência, a Modalidade apontada por cada linha reservada do
  quadro, e o fato citado por cada critério de desempate. Referência interna que não tenha
  contraparte na cópia DEVE fazer a operação falhar alto, e NÃO DEVE atravessar para a cópia
  apontando a origem.
- **FR-642**: Referências para **fora** do Perfil DEVEM permanecer as mesmas: as Etapas de
  Avaliação que o marco ordena ou cita, a Etapa de habilitação do método de sorteio, e o método de
  sorteio comum do Edital. São do Edital, e a cópia é do mesmo Edital.
- **FR-643**: Os campos do Perfil que nenhuma etapa do assistente desenha NÃO DEVEM ser copiados,
  pela mesma razão pela qual o reuso de Edital inteiro (`023`) não os copia: entregariam à cópia
  conteúdo normativo que quem compõe não tem como revisar nem remover.
- **FR-644**: O código e a denominação de marco que coincidam com o que o sistema deriva do Perfil
  de origem DEVEM, na cópia, ser derivados do Perfil **novo** (`D-004`). Código e denominação de
  marco que quem compõe tenha escrito à mão DEVEM ser copiados como estão.
- **FR-645**: Duplicar NÃO DEVE criar, alterar nem remover Documento Exigido. Quando houver
  Documentos Exigidos recortados pelo Perfil de origem ou por uma Modalidade dele, a tela DEVE
  informar, junto à cópia, **quantos** são e que **não** foram replicados para ela. Documentos de
  escopo *"Todos os Perfis"* valem para a cópia sem cópia nenhuma, e não entram na contagem.

- **FR-650** *(acrescentada na escrita do plano, depois do achado `R-003`)*: Como os marcos não são desenhados na etapa Perfis, a cópia DEVE dizer **quantos**
  marcos leva e que eles se editam na etapa Classificação depois de gravada. Esses marcos DEVEM
  sobreviver a uma recusa da gravação: a tela que devolve o digitado DEVE devolver a cópia com eles.

### O que esta feature preserva

- **FR-646**: Duplicar NÃO DEVE alterar o Perfil de origem — nem o que está na tela, nem o que está
  gravado. Gravar a etapa com a cópia DEVE deixar a origem idêntica ao que seria gravado sem a
  cópia; remover a cópia ou sair sem gravar DEVE deixar o rascunho gravado intacto.
- **FR-647**: A cópia DEVE atravessar exatamente as mesmas validações de gravação, de Revisão e de
  publicação que qualquer Perfil. Duplicar NÃO DEVE criar caminho de gravação que as contorne.
- **FR-648**: A operação DEVE exigir a mesma autorização de compor o Edital — permissão de elaborar
  **e** Edital em elaboração —, verificada no servidor. Quem não pode compor NÃO DEVE ver a
  operação, e a operação pedida diretamente DEVE ser recusada. A operação NÃO DEVE ler nem devolver
  conteúdo de Edital que não seja o que está sendo composto.
- **FR-649**: O conteúdo de Edital publicado NÃO DEVE ser alcançado. Duplicar não existe em
  Retificação, e nenhum Edital publicado muda de conteúdo por causa desta feature.

### Key Entities

- **Perfil de Vaga**: a unidade que se duplica. Continua sendo a dona das Modalidades, do quadro de
  vagas, dos fatos declarados e dos marcos; nada muda de dono.
- **Perfil de origem**: o Perfil a partir do qual se duplica. Não guarda vínculo com a cópia depois
  dela: a cópia é um Perfil independente, e editar um não edita o outro (`D-005`).
- **Cópia**: um Perfil novo, com identidades novas, conteúdo igual ao da origem e Código e
  Localidade informados por quem duplica.

## Success Criteria *(mandatory)*

Interação conta como no estudo: cada clique, cada campo preenchido e cada escolha de *radio* ou
lista. O baseline é o do estudo, medido no 140/2025.

- **SC-230**: Recompondo pela interface a etapa Perfis do Edital 140/2025 — 16 Perfis, 64
  Modalidades, mesmo conteúdo do estudo —, o total de interações da etapa é **no máximo 150**,
  contra **~530** no baseline: redução de pelo menos 70%.
- **SC-231**: No mesmo percurso, cada Perfil criado por duplicação custa em média **no máximo 8**
  interações, contra **~33** por Perfil no baseline.
- **SC-232**: No conteúdo publicado do Edital recomposto, **zero** identidades compartilhadas entre
  Perfis, e **zero** referências de um Perfil apontando Modalidade ou fato de outro.
- **SC-233**: No mesmo conteúdo publicado, cada Perfil criado por duplicação difere do Perfil de
  origem **somente** em identidades, no Código e na Localidade informados, nos campos que quem
  compõe editou depois, e no código e denominação derivados do marco (`FR-644`).
- **SC-234**: Nos três desfechos — duplicar e gravar, duplicar e remover a cópia antes de gravar,
  duplicar e sair sem gravar —, o conteúdo gravado do Perfil de origem é **idêntico** ao que seria
  sem a duplicação.
- **SC-235**: O cenário da User Story 1 é executado de ponta a ponta pela interface administrativa —
  compor, duplicar, gravar, submeter, homologar e publicar —, sem banco, shell ou API.
- **SC-236**: Duplicar e gravar deixa o número de Documentos Exigidos do Edital **inalterado**, e,
  com a origem recortada por *n* documentos, o aviso da cópia diz **exatamente** *n*.

## Assumptions

### D-001 — a cópia nasce na tela, e só existe depois de gravada

Duplicar entrega um cartão, como *Acrescentar Perfil* já entrega. A alternativa — gravar a cópia no
ato — daria duas maneiras de um Perfil entrar no rascunho, e a gravação por substituição do
rascunho inteiro apaga o que não for reenviado: uma cópia gravada no servidor e ausente do
formulário seguinte seria apagada pela gravação seguinte da própria etapa. Nascer na tela mantém um
só caminho de gravação, e o operador pode desistir removendo o cartão.

O custo é o de todo Perfil acrescentado: não gravado, some ao sair. O rascunho local cobre a falha
de envio **só em parte** — ele não traz de volta Modalidades, quadro nem fatos de Perfil nenhum
(`G-006`) —, e numa queda de conexão a cópia volta sem o que a tornava útil. *Corrigido na análise
de consistência: a primeira redação dizia que ele cobria a perda.*

### D-002 — copia-se o que está digitado

Quem duplica acabou de ler o cartão, e espera que a cópia seja **aquele** cartão. Copiar o gravado
faria a cópia divergir, em silêncio, do que está na tela ao lado — e é a mesma razão pela qual o
cartão do marco já se recompõe a partir do formulário, e não do banco (`030`).

### D-003 — Código e Localidade são pedidos no ato de duplicar

São os dois campos que mudam entre Perfis irmãos (estudo §6.2). Pedi-los **antes** de a cópia
existir resolve três coisas de uma vez: a cópia nunca nasce com Código colidindo — o que a gravação
recusaria para o Edital inteiro —; ela nunca nasce afirmando a Localidade da origem, que é o dado
que mais facilmente passaria despercebido numa revisão de dezesseis cartões iguais; e o marco pode
nascer com identidade derivada do Código certo (`D-004`).

A alternativa descartada é copiar com Código vazio ou com sufixo (`LP01-2`) e deixar o operador
corrigir depois: custa o mesmo número de campos, e publica `LP01-2` quando alguém esquece.

A **denominação** não é pedida: é igual em onze dos dezesseis Perfis do 140/2025, e pedi-la
custaria uma interação em cada cópia para mudar cinco.

### D-004 — o marco derivado é derivado de novo

O marco nasce com código igual ao do Perfil e denominação *"Classificação final — ⟨denominação do
Perfil⟩"* (`FR-420` da `030`). Copiado literalmente, o LP02 publicaria um marco `LP01`.

A `FR-421` da `030` proíbe aplicar valor derivado a conteúdo **já declarado**. A cópia não é
conteúdo declarado: é conteúdo novo, nascendo agora — exatamente o caso em que a `FR-420` manda
derivar. O que a `FR-421` protege continua protegido: marco cujo código ou denominação quem compõe
escreveu à mão é copiado como está, porque ali há decisão, e não derivação.

### D-005 — a cópia não guarda vínculo com a origem

Editar a origem depois não propaga para a cópia. Propagação seria *"aplicar a todos"* — outra
operação, com outra pergunta (qual das divergências vence), e fora desta história (§4).

### D-006 — nenhum registro de "duplicado de"

A cópia não registra de qual Perfil veio. A proveniência não tem efeito normativo — o Edital
publica os Perfis, e não a maneira como foram digitados —, e a autoria do rascunho já é registrada
pela gravação da etapa.

---

## 4. O recorte — decidido pelo usuário em 25/09

O estudo nomeia três operações do mesmo mecanismo (§13, E1): *duplicar Perfil*, *aplicar estas
Modalidades a todos os Perfis* e *aplicar este marco aos demais*. Esta spec compromete **só a
primeira**, e a distinção é conceitual, não de tamanho:

- **duplicar Perfil** cria uma estrutura **nova** a partir de outra — não há destino a preservar, e
  a única pergunta é o remapeamento;
- **aplicar a todos** propaga uma alteração para estruturas **que já existem** — e a pergunta
  central passa a ser o que acontece com o que o destino já declarava.

São problemas relacionados, e não a mesma operação. Esta spec entrega a primitiva segura — cópia
com identidades novas e referências remapeadas —, e o que ela ensinar serve à propagação depois,
sem misturar as responsabilidades.

## Riscos e lacunas

| # | Lacuna | Consequência | O que esta spec faz |
|---|---|---|---|
| **G-001** | Uma Modalidade errada no Perfil de origem é copiada quinze vezes | o erro se multiplica na mesma proporção em que o esforço cai, e se corrige Perfil a Perfil | nada além da Revisão de sempre; é o caso que a propagação em massa resolveria (§5, `TF-1`) |
| **G-002** | A curva continua linear | 66 Perfis ainda custam ~430 interações | registra; o que a dobra é E2, fora daqui |
| **G-003** | O documento publicado continua repetindo por Perfil | 34 tabelas no 140/2025 | fora de escopo (§2) |
| **G-004** | Duas pessoas compondo o mesmo Edital ao mesmo tempo | a gravação por substituição já tem esse risco hoje, com ou sem cópia | não o amplia: duplicar não grava (`D-001`) |
| **G-005** | A repetição da etapa de Documentos continua | 112 linhas para 7 documentos no 140/2025 | não a multiplica (`FR-645`), e não a reduz (§5, `TF-2`) |
| **G-006** | O rascunho local restaura só os campos do próprio Perfil — nunca Modalidades, quadro ou fatos —, para qualquer Perfil acrescentado | numa queda de conexão, a cópia volta sem o que a tornava útil | registra; é limitação anterior, e corrigi-la é escopo de outra feature |

## 5. Trabalho futuro — o que a `043` explicitamente **não** resolve

Registrado em separado para que nenhuma das duas lacunas desapareça no histórico como se esta spec
a tivesse fechado. Nenhuma é prioridade decidida: são candidatas a specs posteriores, e a ordem é
do usuário.

- **TF-1 — Propagação em massa.** *Aplicar estas Modalidades a todos os Perfis* e *aplicar este
  marco aos demais Perfis* (estudo §13, E1). Cobre o que duplicar não cobre: o Edital cujos Perfis
  já existem quando a regra comum é decidida, e a correção de uma Modalidade depois de duplicada
  quinze vezes (`G-001`). Pergunta própria, que esta spec não responde: o que acontece com o que o
  Perfil de destino já declarava — sobrescrever, acrescentar ou recusar.
- **TF-2 — Redução da repetição documental.** Uma forma adequada de declarar ou aplicar um
  Documento Exigido a vários Perfis ou Modalidades (estudo §5.9 e §13, E6). A decisão está em
  [doc/decisao-recorte-documental.md](../../doc/decisao-recorte-documental.md), **aberta**. A `043`
  apenas não a agrava.

## Out of Scope

Mover conteúdo para o nível do Edital (E2). Recorte transversal de documento. Duplicar em
Retificação. Duplicar Edital, Etapa, Evento ou Documento. Propagar edição da origem para a cópia.
Edição em lote. Colar tabela. Reordenar Perfis por arrastar.
