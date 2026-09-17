# Feature Specification: Requerimento de Matrícula — o que a vaga exige, perguntado uma vez

**Feature Branch**: `claude/spec-requerimento-matricula-c09145`

> **A numeração é `029` porque é o próximo número livre.** A varredura de 16/09/2026 percorreu as
> nove worktrees desta máquina: a maior pasta é `028`, em quatro delas, e nenhuma tem `029`. O
> número virá de `--number 29`, e não da pasta.

> **Os identificadores continuam a faixa global**, política aberta pela `024` e confirmada pela
> `025`, `027` e `028`. Teto medido em todas as worktrees antes de escrever — `FR-367`, `SC-119`,
> `UX-051` —, e esta spec abre em `FR-368`, `SC-120`, `UX-052`. As **decisões** reiniciam em
> `D-001`, porque são lidas dentro da feature que as produziu; decisões de outras features são
> citadas pelo que dizem, nunca pelo número.

**Created**: 2026-09-16 · **Revisada**: 2026-09-16, após revisão crítica

**Status**: Draft — clarificações **resolvidas** em 16/09/2026 (§23). Nada bloqueia o
`/speckit-plan`.

**Input**: o Requerimento de Matrícula real (Anexo II do Edital 77/2026), a planilha de importação
do Registro Acadêmico (`Import_LIBB_58_78-2026`, com os comentários de célula escritos por ele), os
Editais 46, 57, 58, 69, 77 e 78 de 2026, e a investigação registrada em
[`doc/descoberta-029-requerimento-de-matricula.md`](../../doc/descoberta-029-requerimento-de-matricula.md),
cuja §0 guarda a proveniência das evidências e a política de redação dos dados pessoais da amostra.

---

## 1. Visão

O candidato que conquistou — ou que pode vir a ocupar — uma vaga entrega, **dentro do sistema e em
dados estruturados**, o que o vínculo acadêmico exige e o sistema ainda não sabe. Nada do que ele já
informou é perguntado de novo.

> **A frase que governa:** *seleção e matrícula não são o mesmo momento administrativo, e um dado de
> matrícula não vira dado de seleção por hoje ser pedido na inscrição.*

> **E a frase que mantém o corte:** esta feature **não matricula ninguém**. Ela prepara o dado. Quem
> defere, indefere, regulariza e cancela matrícula é a convocação, e isso já existe.

## 2. Problema

O Requerimento de Matrícula é hoje um PDF. O Edital 77/2026 o exige no item 5.4:

> *"g) **Requerimento de Matrícula – Anexo II (devidamente preenchido)**, incluindo a marcação do
> termo de veracidade ao final do anexo (…). O preenchimento incompleto e/ou incorreto das
> informações solicitadas implicará no indeferimento do candidato, não cabendo recurso."*

Baixar, preencher à mão, assinar, digitalizar, anexar. O sistema recebe um arquivo opaco, e o
Registro Acadêmico **transcreve** o arquivo para uma planilha de 34 colunas. Três consequências,
todas medidas nos artefatos reais:

1. **O candidato redigita o que já informou.** Nome, CPF, e-mail e curso já estão no sistema — o
   e-mail, inclusive, com controle provado.
2. **A transcrição erra.** Na única linha preenchida da planilha da amostra, a coluna `RG` repete,
   dígito a dígito, o CPF da candidata (células `Q2` e `G2`).
3. **O dado não é consultável.** Nem pela pessoa, que não consegue reler o que declarou, nem pelo
   sistema, que não consegue compor a saída sem alguém abrir o PDF.

E há um problema anterior a todos: **das informações que o Requerimento cobra, oito não têm destino
nenhum** — nem coluna na planilha, nem cláusula de Edital que as consuma. Foto, tipo sanguíneo,
número de filhos, profissão, condição de aluno trabalhador, com quem reside, número de pessoas do
domicílio e telefone residencial.

## 3. Motivação

O objetivo declarado do produto é, ao fim do certame, **compor** os dados da matrícula a partir do
que o sistema já sabe. Isso é impossível enquanto a maior fonte desses dados for um PDF. Esta
feature é o degrau que torna a composição possível — e é ela que decide, campo a campo, o que o
sistema passa a saber e o que ele recusa saber.

## 4. Atores

| Ator | O que faz | Canal |
|---|---|---|
| **Candidato** | preenche, revisa, aceita a declaração, envia e reconsulta o próprio requerimento | Área do Candidato |
| **Quem elabora o Edital** | declara se há requerimento, em que momento, e escreve o texto da declaração | interface administrativa |
| **Quem conduz o certame** | lê o requerimento de uma inscrição no dossiê dela | interface administrativa |

O Registro Acadêmico **não é ator desta feature**: ele consome a saída, que é de outra.

## 5. Pré-condições

- Edital publicado, com a declaração do requerimento e o texto da declaração no conteúdo publicado.
- Inscrição existente para a pessoa.
- No momento *na convocação*: chamada **em aberto** para aquela Inscrição (§6, D-004).

## Clarifications

### Session 2026-09-16

- Q: O sistema deve perguntar alguma coisa sobre renda ao candidato, e em que forma? (Q-6) → A:
  **Sim, e em faixas de salário mínimo** — o formulário em uso já pergunta exatamente nas sete
  faixas do Registro Acadêmico (*até 0,5*; *acima de 0,5 até 1*; *acima de 1 até 1,5*; *acima de
  1,5 até 2,5*; *acima de 2,5 até 3,5*; *acima de 3,5*; *não declarada*). **Não há conversão a
  fazer**: a faixa coletada é a faixa exportada. O comentário da planilha, que fala em reais *"por
  pessoa"*, descreve uma prática anterior.
- Q: O rótulo "Renda Familiar" dessa lista significa a renda por pessoa, ou a soma da família
  inteira? (Q-6) → A: **A soma da família inteira** — confirmado por quem opera o formulário. Como
  a coluna de destino é `RENDA_PER_CAPITA_PNP`, e as sete faixas são, na origem, as faixas **per
  capita** da Plataforma Nilo Peçanha, o processo atual escreve um total no lugar de um per capita.
  É defeito confirmado do processo, e não divergência de redação: uma família de quatro pessoas com
  2 salários mínimos de renda total é hoje registrada três faixas acima do que deveria.
- Q: O que o requerimento deve perguntar sobre renda, sabendo que o destino é por pessoa e o
  formulário atual pergunta o total? (FR-381, FR-382) → A: **Manter o total**, como o formulário faz
  hoje. O requerimento coleta a faixa da **renda familiar total** em salários mínimos, e a
  divergência com a coluna per capita de destino **não é corrigida por esta feature**: ela é
  registrada como achado e segue para quem define o formato de importação.
  *Alternativas apresentadas e recusadas*: perguntar a faixa **por pessoa**, com a conta explicada
  no campo; e perguntar renda total em reais mais o número de membros da família, deixando o sistema
  dividir. A primeira mudaria a pergunta que a instituição faz hoje; a segunda passaria a guardar o
  valor exato da renda. **A decisão é de governança, e foi tomada por quem opera o processo.**
  *Consequência aceita, e ela é a razão do R-7*: não existe caminho aritmético do que se coleta para
  o que a coluna significa — dividir uma faixa por um número não produz uma faixa.
- Q: O sistema deve passar a registrar nome social e identidade de gênero como dados próprios do
  candidato? (FR-381, Q-8) → A: **Não nesta feature — vira spec própria**, com a lacuna registrada e
  o alcance nomeado: identidade, comprovante de inscrição, relação de habilitados, resultado
  divulgado e convocação. *(Resposta retificada na mesma sessão: a primeira foi "sim, nesta feature",
  e a retificação prevaleceu. Os requisitos que a primeira resposta havia criado foram removidos, e
  não sobrou campo, tela nem critério de aceite falando de nome social.)*
  *A razão que a retificação preserva*: tratar a pessoa pelo nome social numa tela e pelo nome civil
  na seguinte é pior do que ainda não tratá-la — e o alcance certo atravessa superfícies que esta
  feature não governa.
- Q: O e-mail que o Registro Acadêmico recebe deve ser o da conta do candidato, ou o requerimento
  precisa perguntar um e-mail próprio para a matrícula? (FR-378, Q-3) → A: **O da conta, sempre.**
  Nenhum campo novo: é o único endereço cujo controle a pessoa provou, porque recebeu nele o código
  de acesso. O requerimento o exibe e oferece o caminho de *Conta*, onde trocá-lo passa por
  verificação. Exportar um endereço não verificado seria mandar ao curso justamente o que ninguém
  confirmou.
- Q: O Requerimento assinado em papel pode deixar de ser exigido quando o candidato preencher e
  aceitar a declaração dentro do sistema? (FR-395, Q-2) → A: **O Edital decide, caso a caso.** A
  feature não remove nem mantém o Anexo: quem elabora continua declarando os Documentos Exigidos, e
  retira o Anexo assinado quando a validação institucional daquele certame permitir. O sistema MUST
  NOT exigir o documento por conta própria nem impedir que ele seja exigido.

---

## 6. Decisões fechadas antes do planejamento

### D-001 — É feature própria, e não extensão da inscrição

A Inscrição é o ato pelo qual alguém **disputa** a vaga, e por isso o projeto a congela na submissão
— `Inscricao.save` recusa toda alteração posterior, e não existe retificação de inscrição. O
Requerimento é o ato pelo qual alguém **habilita o vínculo** que a disputa lhe deu.

Estender a Inscrição não é uma opção pior: é impossível nos dois cenários em que a coleta acontece
depois do resultado, porque ali a Inscrição já está congelada — o campo existiria exatamente onde
não poderia ser preenchido. E guardar dado de matrícula dentro da Inscrição diria, na estrutura, que
ele é dado de seleção, que é a confusão que esta feature existe para desfazer.

### D-002 — O escopo "alunos" vem da declaração do Edital, e não de uma taxonomia nova

O sistema **não distingue** hoje Editais de alunos dos demais: não há natureza no `ProcessoSeletivo`
nem no `Edital`. Criar essa taxonomia agora seria inventar um eixo classificatório que nenhuma outra
feature consome, e que passaria a exigir significado normativo, classificação de mutabilidade e
conferência própria.

A declaração do requerimento **é** o recorte: um Edital de tutores, bolsistas ou servidores
simplesmente não a declara, e nele a capacidade não existe — não fica escondida, não fica
desabilitada, não existe.

**Alternativa recusada:** `natureza ∈ {ALUNOS, SERVIDORES, BOLSISTAS, …}` no Processo Seletivo.
Registrada em Q-1, para quando existir consumidor — relatório institucional, por exemplo — que a
exija.

### D-003 — Dois momentos declaráveis, ausência é o terceiro fato, e nenhum é inventado

Os Editais reais escrevem três coisas diferentes:

| Edital | O que diz | Momento |
|---|---|---|
| 77/2026 (5.4.g), 58/2026 (5.4.h) | Requerimento entre os documentos da inscrição | na inscrição |
| 69/2026 (item i) | *"Preenchimento do Requerimento de matrícula, que será fornecido **no ato da matrícula presencial**"* | na convocação |
| 46/2026 (item 27 do cronograma) | *"Requerimento de matrícula — **conforme cronograma do Campus**"*, depois da homologação do resultado final | na convocação |

O terceiro caso **não é um terceiro momento**: quem é aprovado dentro das vagas e vai ao campus
matricular-se é, no vocabulário deste sistema, quem foi **convocado para vaga inicial** — espécie
que a convocação já tem.

**São dois valores declaráveis, e não três.** *Não exigido* não é um valor: é a **ausência de
declaração**, que é a grafia que este repositório já usa para a forma de convocação e para a espécie
de reversão de cota — *não declarado* nunca significa *"faz do jeito comum"*. Duas formas de dizer o
mesmo fato seriam a contradição.

**A ausência tem duas grafias, uma por camada, e elas não se misturam**: na coluna do banco é `""`,
como `especie_de_reversao` e `forma_de_convocacao`; no conteúdo publicado é **`null` com a chave
presente**, como `vacancyReversion` e `callForm`. A primeira redação desta spec mandava **omitir** a
chave no snapshot, e isso contrariava o emissor — a correção veio da auditoria de 16/09/2026.

Fica declarado como **limite, e não como escopo diferido**: um Edital que abra o requerimento a
todos os classificados **sem chamada individual** exigirá um valor novo e um incremento próprio.
Nenhum dos seis Editais lidos faz isso.

### D-004 — O gatilho é a chamada **em aberto**, e "vigente" seria o gatilho errado

*Classificado* diz que a pessoa foi ordenada; não diz que ela pode ocupar vaga. Usar classificação
como gatilho abriria o requerimento para quem está em 300º lugar de 30 vagas.

Mas **vigente também não serve**, e a distinção está escrita na própria feature de convocação:
vigente é *"a que ninguém sucedeu"*, e uma convocação **concluída por desfecho continua vigente**.
O código a nomeia em `_em_aberto_da_pessoa`, com a lição registrada: *"uma convocação com desfecho
está concluída: a pessoa respondeu, ou a Administração concluiu por ela"* — e foi justamente
confundir as duas que produziu um beco numa versão anterior daquela feature.

O gatilho desta é, portanto, **chamada em aberto**: convocação vigente **sem desfecho**. É o fato
que diz *"há vaga, ela é sua, e você ainda não respondeu"*. Fechado o desfecho, o preenchimento
encerra e a leitura permanece.

**A suplência passa a funcionar sem uma linha de exceção**: o suplente chamado três semanas depois
recebe o requerimento pelo mesmo caminho do primeiro colocado, porque a chamada dele também nasce em
aberto.

### D-005 — Cópia para a frente, nunca escrita para trás

É a política desta feature para todo dado mutável — endereço, telefone, estado civil, documento.

O rascunho **nasce preenchido** com o que a pessoa declarou no último requerimento **enviado** da
mesma identidade. O que ela edita é **este** requerimento. Nada do que ela faz aqui altera a
identidade, a inscrição, ou qualquer requerimento anterior.

**As alternativas foram consideradas e recusadas, nesta ordem.** *Endereço na identidade*: um
endereço global mutável faria o requerimento de 2024 passar a dizer, em silêncio, onde a pessoa mora
hoje — e a Constituição exige o passado reproduzível. *Endereço na inscrição*: ela congela na
submissão, e nos cenários de coleta posterior o campo seria inalcançável. *Atual + snapshot*:
**adiado, e não recusado por princípio** — a distinção importa, e a primeira redação desta decisão a
errou.

**O padrão é legítimo e o repositório já o pratica**: a `Inscricao` copia nome, CPF e e-mail da
identidade na submissão e os congela; o `ValorDeFato` congela; a `SituacaoDivulgada` congela. A regra
que o torna seguro está escrita em código há muito tempo — **a identidade guarda o corrente, o ato
guarda o que valia no dia**. Dizer que seriam "dois lugares para o mesmo dado" era argumento mais
forte do que os fatos sustentam.

**O que sustenta o adiamento são três coisas concretas** (decisão do usuário, 16/09/2026):

1. **Hoje o requerimento é o único consumidor.** Um endereço corrente na identidade só passa a pagar
   quando existir um segundo — correspondência, notificação, leitura territorial —, e nenhum existe.
2. **A cópia-para-a-frente já entrega o ganho**: quem já se matriculou antes **confere** o endereço,
   e não o redigita. É o mesmo resultado, sem tocar em estrutura alheia.
3. **A identidade é território da `010`.** Migration em `identidade`, a tela *Meus dados* estendida e
   uma política de congelamento por campo — o CPF já tem a dele — formam jornada própria, e uma
   feature não absorve o escopo da outra.

**A data de nascimento é o caso mais forte para promover, e é por isso que adiá-la custa pouco**: ela
**não muda**. Não existe "versão de 2024" de uma data de nascimento, então promovê-la depois é
*backfill* trivial — copia-se do requerimento mais recente, sem ambiguidade e sem perda. Poucas
decisões desta spec têm saída tão barata.

### D-006 — Nome, CPF e e-mail não são campos deste formulário

Os três já existem e têm dono. Nome e CPF são o núcleo da identidade e têm tela própria — *Meus
dados* —, com a regra de que o CPF congela na primeira inscrição enviada. O e-mail é **credencial
com controle provado**, e tem a tela *Conta*.

Aqui eles aparecem como **informação**, com o caminho para o lugar onde se corrigem — nunca como
campo desabilitado sem explicação.

**O limite desta decisão está em Q-3**, e ele é bloqueante: o Edital 77 (9.3) fala do e-mail
*"informado no requerimento de matrícula"*. Se a operação confirmar que o endereço da matrícula pode
ser outro que o da credencial, o modelo ganha **um** campo de contato — e a decisão precisa vir
antes do plano, não depois.

### D-007 — Enviado não muda; correção é sucessão, e quem a autoriza é a chamada em aberto

Enviado, o requerimento é peça de ato administrativo: a análise documental o lê, e o indeferimento
se funda nele. Alterá-lo reescreveria o que fundamentou uma decisão já tomada.

**Mas proibir a correção sem mais nada abre um beco que um Edital real percorre.** O 77/2026 (8.2)
convoca *"os candidatos que tiveram a solicitação de matrícula indeferida (…) para regularizar a sua
situação de indeferimento"* — e a causa do indeferimento pode ser, literalmente, *"o preenchimento
incompleto e/ou incorreto"* do requerimento (5.4.g). Uma pessoa convocada para corrigir precisa
poder corrigir.

Por isso a correção é **sucessão**, e não edição: um requerimento novo sucede o anterior, o anterior
permanece íntegro e legível, e a cadeia diz em que ordem os fatos aconteceram. É a forma que este
sistema já usa cinco vezes — no resultado da etapa, no ato de ordenação, no corte, na apuração e na
própria convocação —, e por isso não é mecanismo novo: é o mecanismo da casa.

**O que a limita é a autorização**: o sucessor só nasce onde há **chamada em aberto** para aquela
Inscrição. Sem isso, seria edição com outro nome. E é essa mesma porta que atende, sem regra extra,
o risco do dado envelhecido da coleta antecipada (R-2): convocada meses depois, a pessoa confere o
que declarou e sucede, se algo mudou.

### D-008 — Código IBGE sim, coordenadas não

O código IBGE do município é identificação territorial **estável**, cabe em sete caracteres, é
obtido no momento da coleta e não se recalcula depois com a mesma confiabilidade — o CEP pode mudar
de faixa, e a pessoa pode mudar de endereço.

Latitude e longitude **não entram**. Elas são recalculáveis a qualquer momento a partir do CEP, que
fica guardado; exigiriam campos de fonte e de qualidade para não mentir; e não têm consumidor
nenhum, porque todo relatório territorial está declarado fora de escopo. Guardar estrutura antes de
existir a regra que a consome é o que este repositório já recusou ao modelar os campos descritivos
do Perfil.

**E, quando existirem, não serão a casa de ninguém:** a coordenada associada a um CEP pode
representar o logradouro, o centro da localidade, um estabelecimento ou o município inteiro. O
domínio a trata como **referência territorial aproximada do CEP**, e nenhuma tela pode dizer
"residência".

### D-009 — Enriquecimento é auxiliar, e o domínio não conhece fornecedor

O domínio declara uma porta: *dado um CEP, um serviço de referência devolve logradouro, bairro,
município, UF e código IBGE, ou não devolve nada*. `OpenCEP`, `gpfconfea/banco-ceps` ou qualquer
outro são implementações dessa porta, e nenhum nome aparece em regra de negócio.

**Base local é a recomendação**, com a razão escrita: consultar serviço de terceiro em tempo real
transmitiria continuamente o CEP de candidatos identificados para fora da instituição, o que a
minimização do Princípio III desaconselha; e uma base carregada por comando é reprodutível, não cai
e não muda sob os pés de um certame em curso. Qual base e com que periodicidade é decisão do plano.

### D-010 — O contrato de saída é documento, não código

Esta feature escreve o mapa *campo de saída → origem* de cada coluna do formato atual, e o mantém
verificado contra os campos que ela coleta. Ela **não** gera planilha, não valida layout e não fala
com o sistema acadêmico.

### D-011 — O texto da declaração é norma do Edital, e tem autor

A declaração de veracidade não pode ser literal de código: ela varia entre Editais, é o que a pessoa
assina, e é o que fundamenta o cancelamento por informação falsa. Logo, ela é **conteúdo publicado**
— escrita na elaboração, publicada com o Edital, corrigível por Retificação como todo texto
normativo, e alcançada pelo contrato de mutabilidade.

**E é por isso que o aceite guarda o resumo criptográfico do texto exibido**: retificada a
declaração depois, o que a pessoa leu continua reconstituível. Sem autoria declarada não haveria
origem para o texto, e o resumo seria resumo de nada.

## 7. Escopo

- Declaração, pelo Edital, de que há requerimento, em que momento, e com que texto de veracidade.
- A abertura do requerimento pelo gatilho do momento declarado.
- O preenchimento em dados estruturados, pré-preenchido com o que o sistema já sabe.
- O endereço estruturado, com enriquecimento por CEP e degradação.
- A declaração de veracidade e o registro auditável do aceite.
- O envio, a imutabilidade depois dele, e a sucessão autorizada por chamada em aberto.
- A reconsulta pelo candidato e a leitura no dossiê da inscrição por quem conduz.
- O contrato de saída documentado.

## 8. Fora de escopo

Criação de matrícula no sistema acadêmico · integração com o sistema acadêmico · geração da planilha
de importação · análise do requerimento pelo Registro Acadêmico · deferimento e indeferimento —
**já são desfechos da convocação** · pagamento · assinatura digital certificada, ICP-Brasil ou
assinatura eletrônica externa · dashboard geográfico, mapas, heatmaps, cálculo de distância, GIS ·
geocodificação de precisão residencial · workflow engine · form builder · notificações de convocação
— são da feature de convocação · códigos institucionais do sistema acadêmico (curso, turno, polo,
nacionalidade) · taxonomia de natureza do Processo Seletivo.

## 9. User Scenarios & Testing *(mandatory)*

### User Story 1 — O candidato entrega, na inscrição, só o que falta (Priority: P1)

Num Edital que declara a coleta *na inscrição*, a pessoa abre o requerimento pela Área do Candidato,
encontra o que o sistema já sabe apresentado como informação, completa o que falta, aceita a
declaração e envia — e a inscrição só se submete depois disso.

**Why this priority**: é o caso da maioria da amostra — o 77 e o 58 —, e é o que substitui o PDF
preenchido à mão. Entregue sozinha, já elimina a transcrição manual para aqueles certames.

**Independent Test**: publicar um Edital com a declaração *na inscrição*, preencher e enviar o
requerimento pela Área do Candidato, e conferir que nome, CPF, e-mail, curso, modalidade e protocolo
não aparecem como campo em tela nenhuma.

**Acceptance Scenarios**:

1. **Given** um Edital que declara a coleta na inscrição e um rascunho de inscrição aberto,
   **When** o candidato abre o requerimento, **Then** vê seus dados conhecidos como informação, com
   o caminho para corrigi-los, e apenas os campos faltantes como entrada.
2. **Given** o requerimento não enviado, **When** o candidato tenta submeter a inscrição, **Then** a
   recusa é anunciada **antes** da tentativa, na tela da inscrição.
3. **Given** o requerimento preenchido sem aceite da declaração, **When** ele olha a tela,
   **Then** ela **já diz** que o envio depende do aceite — antes de qualquer tentativa; e, **When**
   um envio chega assim mesmo, por caminho que não passe pela tela, **Then** a aplicação o recusa e
   diz o motivo em palavras. *São duas camadas e não duas versões da mesma: o anúncio é da `SC-128`,
   a recusa é da `FR-394`, e uma não substitui a outra.*

---

### User Story 2 — O convocado entrega os dados quando a vaga é dele (Priority: P1)

Num Edital que declara a coleta *na convocação*, a pessoa se inscreve com o mínimo, participa da
seleção e só encontra o requerimento quando há chamada em aberto para ela — seja a primeira chamada,
seja a suplência semanas depois.

**Why this priority**: é o caso do 69 e do 46, e é o que realiza a fronteira entre seleção e
matrícula: quem não chega à vaga não entrega dado de vínculo.

**Independent Test**: convocar uma pessoa para vaga inicial e outra por suplência, e verificar que o
requerimento abre para as duas pelo mesmo caminho, sem passo administrativo próprio.

**Acceptance Scenarios**:

1. **Given** um Edital que declara a coleta na convocação e nenhuma chamada, **When** o candidato
   abre sua área, **Then** lê *"ainda indisponível"*, distinto de *"este certame não pede
   requerimento"*.
2. **Given** uma chamada em aberto, **When** ele abre a área, **Then** o requerimento está
   disponível e preenchível.
3. **Given** uma chamada já desfechada, **When** ele abre a área, **Then** o requerimento é legível
   e não é preenchível.
4. **Given** um suplente convocado depois de uma desistência, **When** ele abre a área, **Then** o
   requerimento abre exatamente como abriu para o primeiro convocado.

---

### User Story 3 — Quem elabora declara a exigência, o momento e o texto (Priority: P2)

Na elaboração do Edital, quem compõe declara que aquele certame exige Requerimento de Matrícula, em
que momento ele é coletado, e escreve o texto da declaração de veracidade que o candidato aceitará.

**Why this priority**: sem ela nenhuma das duas primeiras existe — mas ela não entrega valor
sozinha, e por isso não é P1.

**Independent Test**: compor um Edital com a declaração, publicá-lo, e ler no conteúdo publicado o
momento e o texto.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração, **When** quem compõe declara o momento e escreve o texto,
   **Then** os dois entram no conteúdo publicado na publicação.
2. **Given** um Edital sem a declaração, **When** ele é publicado, **Then** nenhum requerimento
   existe naquele certame, por caminho nenhum.
3. **Given** um Edital publicado com a declaração, **When** alguém retifica o texto, **Then** a
   Retificação é admitida e os aceites anteriores continuam reconstituíveis.

---

### User Story 4 — Quem conduz lê o que a pessoa declarou (Priority: P2)

Quem conduz o certame abre o dossiê de uma inscrição e lê o requerimento dela, estruturado, sem
abrir PDF nenhum.

**Why this priority**: é o que fecha a jornada institucional — o dado estruturado que ninguém lê
continua sendo um PDF com outro nome.

**Independent Test**: abrir o dossiê de uma inscrição com requerimento enviado e ler os campos e o
instante do envio.

**Acceptance Scenarios**:

1. **Given** uma inscrição com requerimento enviado, **When** quem tem a permissão de consulta abre
   o dossiê, **Then** lê os campos declarados e quando foram declarados.
2. **Given** um ator sem a permissão, **When** ele tenta a mesma leitura, **Then** a recusa não
   revela que o requerimento existe.

---

### User Story 5 — Quem foi convocado para regularizar corrige o que declarou (Priority: P3)

A pessoa teve a matrícula indeferida por preenchimento incorreto, é convocada para regularizar, e
corrige o que estava errado — sem que o requerimento anterior seja apagado ou reescrito.

**Why this priority**: é cláusula expressa do 77/2026 (8.2) e o único caminho de correção que esta
feature admite. Fica em P3 porque depende das duas primeiras e alcança uma minoria dos casos.

**Independent Test**: registrar indeferimento, convocar para regularizar, submeter o requerimento
sucessor, e ler o anterior intacto.

**Acceptance Scenarios**:

1. **Given** um requerimento enviado e uma chamada em aberto para regularizar, **When** o candidato
   corrige e envia, **Then** nasce um sucessor, o anterior permanece legível, e o vigente é o novo.
2. **Given** um requerimento enviado e **nenhuma** chamada em aberto, **When** o candidato tenta
   corrigir, **Then** é recusado — e a tela diz que a correção depende de convocação.
3. **Given** um sucessor já criado, **When** alguém tenta criar um segundo sucessor do mesmo
   requerimento, **Then** a restrição de banco recusa.

---

### Jornada ponta a ponta *(Princípio VI)*

Compor um Edital com a declaração *na convocação* e o texto de veracidade → publicá-lo → o candidato
se inscreve → a comissão avalia, o resultado é divulgado e a vaga é apurada → a pessoa é convocada →
o requerimento abre na Área do Candidato → ela confere o conhecido, completa o faltante, aceita e
envia → quem conduz abre o dossiê e lê o que ela declarou. **Sem shell, sem banco e sem canal
alheio ao ator de cada passo.**

### Edge Cases

- **Convocação sucedida por outra** — o gatilho lê a vigente, e a sucedida não abre nada.
- **Prazo da convocação vencido, sem desfecho** — o requerimento continua em aberto: quem decide a
  consequência do prazo é a convocação, e duas contagens do mesmo prazo divergiriam.
- **Desfecho registrado com requerimento em rascunho** — o rascunho permanece, legível e não
  enviável; ele não vira lixo nem some.
- **Duas chamadas da mesma pessoa em recortes diferentes** — o requerimento é da Inscrição, e a
  Inscrição é de um Perfil só; não há ambiguidade.
- **Retificação do Edital entre o aceite e a leitura** — o texto lido continua reconstituível pelo
  resumo guardado.
- **CEP de faixa nova, ausente da base** — degradação da FR-390; é caminho normal, e não erro.
- **Pessoa sem filiação paterna declarável** — envio conclui.
- **Edital que declara momento e não declara texto** — publicação recusada: aceite sem texto seria
  aceite de nada.

## 10. Regras de negócio

### 10.1 A declaração do Edital

- **FR-368**: O conteúdo publicado do Edital MUST poder declarar o momento da coleta do requerimento
  com exatamente um de **dois** valores — *na inscrição* ou *na convocação* —, e MUST NOT existir um
  terceiro valor com o sentido de "não exigido": duas grafias do mesmo fato são a contradição que
  esta regra evita.
  **A chave MUST estar sempre presente no conteúdo publicado, e `null` MUST significar que aquele
  Edital não exige requerimento.** Não é omissão: é a grafia que o emissor já pratica em
  `vacancyReversion` — objeto quando declarado, `null` quando não — e em `callForm`. Omitir a chave
  faria o mesmo fato ter duas formas conforme o Edital, que é justamente o que esta regra proíbe.
- **FR-369**: A declaração MUST ser do Edital, e não do Perfil: o requerimento é o mesmo conjunto
  institucional para todo Perfil do certame, e repartir por Perfil criaria configuração sem caso.
- **FR-370**: O contrato de mutabilidade MUST classificar os campos novos. A classificação proposta
  é **não retificável** para o momento da coleta — mudá-lo depois da publicação ou invalida inscrição
  submetida, ou passa a cobrar dado de quem já cumpriu o que o Edital pedia — e **retificável** para
  o texto da declaração, que é texto normativo como os demais.
- **FR-371**: Em Edital que não declara requerimento, o sistema MUST NOT criar, exibir ou aceitar
  requerimento por caminho nenhum, inclusive por acesso direto ao endereço.
- **FR-407**: O texto da declaração de veracidade MUST ser escrito na elaboração do Edital, pela
  permissão de elaboração já existente, e MUST integrar o conteúdo publicado. A publicação de um
  Edital que declara o momento e não tem o texto MUST ser recusada como erro impeditivo pela
  conferência de conteúdo que a publicação já executa.

### 10.2 Disponibilidade

- **FR-372**: Declarado *na inscrição*, o requerimento MUST ficar disponível a partir da abertura do
  rascunho da inscrição, e a submissão da inscrição MUST exigi-lo enviado.
- **FR-373**: Declarado *na convocação*, o requerimento MUST ficar disponível quando existir, para
  aquela Inscrição, convocação vigente **sem desfecho registrado** — qualquer que seja a espécie:
  vaga inicial, suplência ou regularização. Convocação vigente **com** desfecho MUST NOT abrir nem
  manter aberto o preenchimento.
- **FR-374**: **Do prazo, e só dele.** O vencimento do prazo da convocação MUST NOT, por si,
  encerrar o preenchimento, fechar a leitura nem apagar o que houver: quem decide a consequência do
  prazo é a convocação, e duas contagens do mesmo prazo divergiriam. Chamada vencida **sem** desfecho
  continua em aberto; o que a encerra é o desfecho, cujo efeito a FR-411 descreve.
- **FR-375**: Havendo convocação sucedida por outra, o gatilho MUST ser lido da vigente.
- **FR-376**: MUST existir no máximo uma **raiz** de requerimento por Inscrição, e no máximo um
  sucessor por requerimento — as duas por restrição de banco. Vigente é o requerimento que ninguém
  sucedeu.
- **FR-411**: **Do desfecho, e só dele.** Registrado o desfecho — qualquer das sete espécies —, o
  preenchimento MUST encerrar; o requerimento MUST permanecer legível no estado em que estava; e um
  rascunho não enviado MUST NOT ser apagado nem convertido em enviado. É a FR-374 vista do outro
  lado: lá o prazo não encerra nada, aqui o desfecho encerra a escrita e preserva a leitura.

### 10.3 O candidato informa uma vez

- **FR-377**: O rascunho MUST nascer pré-preenchido com o que consta no requerimento **enviado** mais
  recente da mesma identidade, quando houver, por **cópia** — e a edição MUST NOT alcançar aquele
  requerimento.
- **FR-378**: Nome, CPF e e-mail MUST ser apresentados como informação já conhecida, com o caminho
  para onde se corrigem, e MUST NOT ser campos deste formulário. O endereço exportado MUST ser o
  da credencial principal, e o requerimento MUST NOT ter campo de e-mail próprio: um segundo
  endereço teria autoridade ambígua e chegaria ao curso sem verificação alguma.
- **FR-379**: O telefone celular MUST nascer pré-preenchido com o telefone da Inscrição, e MUST ser
  confirmável ou corrigível — o da Inscrição congelou na submissão e pode ter meses.
- **FR-380**: Perfil, modalidade de concorrência, protocolo e Edital MUST ser apresentados como
  derivados, e MUST NOT ser perguntados.

### 10.4 O que é coletado, e o que é recusado

- **FR-381**: O requerimento MUST coletar, e apenas: data de nascimento; município e UF de
  nascimento; nacionalidade; sexo; cor/raça; estado civil; nome da mãe; nome do pai; número,
  órgão emissor e data de expedição do documento de identidade; telefone celular; necessidade
  educacional específica; a faixa de renda familiar da FR-412; e o endereço da FR-386.
- **FR-382**: O sistema MUST NOT coletar foto, tipo sanguíneo, número de filhos, profissão, condição
  de aluno trabalhador, com quem reside, número de pessoas do domicílio nem telefone residencial —
  **oito informações**, nenhuma com destino na saída ou cláusula de Edital que a consuma, e coletar
  sem finalidade identificada contraria a minimização.
  **Nome social e identidade de gênero não estão nesta lista, e a diferença importa**: eles não são
  recusados por falta de finalidade — são **adiados**, porque o alcance certo deles atravessa
  identidade, comprovante, relação de habilitados, resultado e convocação, e nenhuma dessas
  superfícies é governada por esta feature (§25).
- **FR-383**: Cor/raça MUST oferecer as cinco categorias do IBGE — branca, preta, parda, amarela e
  **indígena** — mais *não declarada*. O destino atual não tem *indígena*, e a ausência é achado a
  tratar na composição da saída, jamais uma categoria a suprimir na coleta.
- **FR-384**: A filiação MUST ser coletada em dois campos nomeados, e a ausência de um deles MUST ser
  declarável sem impedir o envio.
- **FR-385**: A necessidade educacional específica MUST ser dado próprio, distinto da modalidade de
  concorrência para pessoa com deficiência: aquela é cota com comprovação e análise; esta é
  informação de acolhimento, e confundi-las faria uma contradizer a outra.
- **FR-386**: O endereço MUST ser estruturado em CEP, logradouro, número, complemento, bairro,
  município, UF e código IBGE do município — e MUST NOT existir como bloco de texto.
- **FR-412**: O requerimento MUST coletar a renda familiar como **faixa**, nas sete opções que o
  formulário institucional já usa — *até 0,5*; *acima de 0,5 até 1*; *acima de 1 até 1,5*; *acima de
  1,5 até 2,5*; *acima de 2,5 até 3,5*; *acima de 3,5*; *não declarada* —, expressas em salários
  mínimos e medindo a **soma da família**, e MUST NOT coletar o valor da renda nem o número de
  membros da família. O rótulo do campo MUST dizer por extenso o que a faixa mede, para que a
  divergência do R-7 não se propague por ambiguidade de redação.

### 10.5 Enriquecimento por CEP

- **FR-387**: O CEP MUST ser guardado normalizado, em forma única.
- **FR-388**: O código IBGE MUST ser preenchido pelo enriquecimento quando conhecido, e MUST NOT ser
  digitável pelo candidato.
- **FR-389**: O acesso ao serviço de referência MUST ser uma porta do domínio, e o domínio MUST NOT
  nomear fornecedor.
- **FR-390**: Indisponibilidade, ausência do CEP na base ou resposta incompleta MUST NOT impedir o
  preenchimento, o envio, a inscrição nem a matrícula; nesse caso todos os campos de endereço —
  inclusive município e UF — MUST ficar editáveis, **à exceção do código IBGE**, que MUST permanecer
  não digitável e MUST ficar vazio. A exceção é dita aqui porque a FR-386 conta o código IBGE entre
  os campos de endereço, e sem ela esta regra mandaria abrir justamente o campo que a FR-388 proíbe
  digitar — contradição que só apareceria na implementação.
- **FR-391**: O sistema MUST NOT coletar latitude e longitude, e nenhuma tela ou registro MUST
  afirmar que uma coordenada derivada de CEP é a residência da pessoa.

### 10.6 Declaração e aceite

- **FR-392**: O texto exibido MUST ser o do conteúdo publicado vigente no momento da exibição, e
  MUST NOT ser literal de código.
- **FR-393**: O envio MUST registrar a versão consolidada vigente no aceite, o resumo criptográfico
  do texto exatamente como exibido, o instante e a identidade que aceitou.
- **FR-394**: Sem aceite registrado, o estado *enviado* MUST NOT ser alcançável — e a garantia MUST
  estar no banco, como já está para a Inscrição submetida.
- **FR-395**: A convivência com o Requerimento em papel MUST ser decidida **pelo Edital**, e não por
  esta feature. O sistema MUST NOT remover por conta própria o Documento Exigido em que o Anexo hoje
  consiste, MUST NOT exigi-lo implicitamente quando o Edital não o declarar, e MUST NOT condicionar
  o envio do requerimento estruturado ao envio dele. Se o aceite eletrônico substitui a assinatura
  perante o Registro Acadêmico é validação normativa daquele certame, e quem elabora a exerce
  declarando — ou deixando de declarar — o documento.

### 10.7 Imutabilidade, sucessão, auditoria e privacidade

- **FR-396**: Requerimento em estado *enviado* MUST NOT ser alterado nem excluído — nem pela
  aplicação, nem por comando de manutenção, nem por quem tenha privilégio. A garantia MUST ser de
  **gatilho de banco condicional ao estado**, e não apenas de guarda na gravação: a imutabilidade
  aqui é condicional, e a própria política de privilégios do projeto registra que imutabilidade
  condicional ao estado não cabe em privilégio de tabela e *"só a trigger consegue expressar"*. A
  guarda na aplicação permanece como primeira camada, nunca como a única.
- **FR-408**: Um requerimento sucessor MUST ser admitido somente quando existir chamada em aberto
  para aquela Inscrição, e MUST citar a convocação que o autorizou. Fora disso, MUST ser recusado.
- **FR-409**: O sucessor MUST nascer copiando o conteúdo do antecessor, e o antecessor MUST
  permanecer íntegro e legível. A sucessão MUST NOT apagar, sobrescrever ou ocultar o que foi
  declarado antes.
- **FR-410**: A Área do Candidato MUST oferecer *conferir e atualizar* quando houver, ao mesmo
  tempo, requerimento enviado e chamada em aberto — e MUST NOT criar sucessor quando nada mudar.
- **FR-397**: O envio MUST gravar auditoria com quem enviou, para qual Inscrição, para qual Edital,
  quando, o que foi declarado, qual declaração foi aceita, sob qual versão e — havendo — qual
  requerimento ele sucede e sob autorização de qual convocação.
- **FR-398**: Nenhuma gravação desta feature MUST escrever em `CandidateIdentity`, em `Inscricao`,
  em `ValorDeFato` ou em requerimento anterior.
- **FR-399**: O requerimento MUST ser acessível ao próprio titular, e a recusa a quem não é titular
  MUST ser indistinguível de recurso inexistente.
- **FR-400**: A leitura por quem conduz MUST exigir a permissão de consulta de inscrição, no dossiê
  da inscrição — e MUST NOT ter listagem própria do conjunto de requerimentos de um Edital, que
  seria uma superfície nova sobre dado pessoal sem jornada que a peça.
- **FR-401**: Cor/raça, necessidade específica, filiação, documento e endereço MUST NOT aparecer em
  URL, em log, em mensagem de erro nem em qualquer superfície pública, e MUST NOT entrar em
  resultado divulgado.

### 10.8 Documentos e contrato de saída

- **FR-402**: Esta feature MUST NOT pedir reenvio de documento que a Inscrição já recebeu, e MUST
  NOT criar um segundo acervo de documentos: documento específico de matrícula continua sendo
  Documento Exigido do Edital.
- **FR-403**: A feature MUST manter, como artefato versionado, o mapa *campo de saída → origem* de
  cada coluna do formato usado pelo Registro Acadêmico, e MUST declarar como questão aberta —
  jamais inventar — todo campo sem fonte identificada.
- **FR-404**: A feature MUST NOT produzir planilha, arquivo de importação ou chamada a sistema
  acadêmico.

### 10.9 Área do Candidato

- **FR-405**: A Área do Candidato MUST apresentar o requerimento em cinco estados: *não aplicável*,
  *ainda indisponível*, *disponível*, *em preenchimento* e *enviado* — e MUST distinguir *"este
  certame não pede requerimento"* de *"ainda não chegou a sua vez"*, pela mesma razão que a tela de
  convocação distingue as duas ausências dela.
- **FR-406**: Enviado, o requerimento MUST continuar legível pelo candidato, mostrando exatamente o
  que o sistema recebeu, sem redigitação e sem reenvio.

## 11. Modelo de domínio

**Uma entidade, `RequerimentoDeMatricula`, com uma raiz por Inscrição e cadeia de sucessão.**

| Grupo | Campos |
|---|---|
| Vínculo e estado | `inscricao` (`PROTECT`), `status`, `disponibilizado_em`, `enviado_em`, `revision`, `created_at` |
| Sucessão | `requerimento_anterior` (self, nulo, `PROTECT`), `convocacao_autorizadora` (nula, `PROTECT`) |
| Pessoa | `data_de_nascimento`, `municipio_natal`, `uf_natal`, `nacionalidade`, `sexo`, `cor_raca`, `estado_civil`, `nome_da_mae`, `nome_do_pai` |
| Documento | `rg`, `rg_orgao_emissor`, `rg_expedido_em` |
| Contato | `telefone_celular` |
| Acolhimento | `necessidade_especifica` |
| Renda | `renda_familiar_faixa` — lista fechada de sete valores, medindo a soma da família |
| Endereço | `cep`, `logradouro`, `numero`, `complemento`, `bairro`, `municipio`, `uf`, `codigo_ibge`, `endereco_conferido_por_referencia` |
| Aceite | `versao_aceita` (`PROTECT`), `declaracao_hash`, `declaracao_aceita_em` |

**Uma tabela, e não três.** O endereço não tem ciclo de vida próprio, não é lista e não é
compartilhado com ninguém: uma entidade `Endereco` acrescentaria identidade e junção a um objeto que
nunca é endereçado sozinho. É a recusa que a feature de convocação escreveu sobre a vaga individual
e a de resultado sobre a ocorrência — a entidade nasce quando nasce a regra que a consome.

**Nenhum campo livre e nenhum JSON.** O conjunto é institucional e estável: o 46, o 58, o 69, o 77 e
o 78 pedem os mesmos dados. Diferença pequena entre Editais não justifica construtor de formulário —
é a mesma recusa que o Documento Exigido já registra ao admitir só Perfil e modalidade como
restrição, *"e é essa recusa que separa isto de um construtor de formulários"*.

**Restrições de banco exigidas** — uma raiz por Inscrição (parcial, sobre `requerimento_anterior`
nulo); um sucessor por requerimento (parcial, sobre não nulo); sucessor exige convocação
autorizadora; *enviado* exige instante e aceite; e o gatilho condicional da FR-396, que recusa
`UPDATE` e `DELETE` sobre linha em *enviado*.

**Não entra nas tabelas append-only**, e a razão é a mesma que exclui `Inscricao` e `Retificacao`: a
linha muda legitimamente enquanto é rascunho, e privilégio de tabela não sabe ler estado. É
exatamente por isso que a FR-396 exige **gatilho**, e não só privilégio.

## 12. Estados e transições

| Estado | Persistido? | Como é sabido |
|---|:--:|---|
| Não aplicável | não | o Edital não declara requerimento |
| Ainda indisponível | não | declara, e o gatilho do momento não ocorreu |
| Disponível | não | gatilho ocorreu e não há linha vigente |
| Em preenchimento | **sim** | linha vigente em `RASCUNHO` |
| Enviado | **sim** | linha vigente em `ENVIADO` |

Transições: *disponível → em preenchimento* ao primeiro salvamento; *em preenchimento → enviado* no
envio com aceite; *enviado → em preenchimento de um sucessor*, e só sob chamada em aberto (FR-408).
**Não há outra**, e nenhuma volta sobre a mesma linha.

Os três primeiros estados não são coluna, de propósito: são a ausência de linha vigente lida contra
a configuração, que é como a ocupação e a convocação já derivam vigência.

## 13. Autorização

| Quem | O quê | Como |
|---|---|---|
| Candidato titular | preencher, enviar, suceder e reler o próprio | titularidade da Inscrição |
| Quem conduz | ler no dossiê da Inscrição | permissão de consulta de inscrição, já existente |
| Quem elabora | declarar exigência, momento e texto | permissão de elaboração do Edital, já existente |

**Nenhuma permissão nova.** O candidato não é ator institucional — ele possui a Inscrição, e é dela
que a titularidade é conferida.

## 14. UX

- **UX-052**: O requerimento MUST aparecer como um cartão na área da Inscrição, com o estado dito em
  palavras e sem ajuda visível no cartão — a microcópia de preenchimento mora no *como preencher* da
  tela de preenchimento.
- **UX-053**: A tela MUST separar visualmente *o que o sistema já sabe* de *o que falta você
  informar*, e MUST dizer de onde veio cada dado já conhecido.
- **UX-054**: O bloqueio MUST ser anunciado **antes** da tentativa: no momento *na inscrição*, a
  tela da inscrição diz que o envio dela depende do requerimento — e não descobre isso no clique.
- **UX-055**: Ao reconhecer o CEP, a tela MUST dizer o que foi preenchido automaticamente e MUST
  permitir corrigir logradouro, número, complemento e bairro; não reconhecendo, MUST dizer que não
  foi possível consultar, sem culpar quem digitou, e abrir todos os campos.
- **UX-056**: A declaração MUST ser apresentada por extenso, com o aceite num ato explícito, e o
  texto MUST ser o do Edital.
- **UX-057**: Depois do envio, a tela MUST mostrar o que foi recebido e o instante, sem campo
  editável — a mesma conferência que a inscrição enviada já oferece.
- **UX-058**: Nenhuma tela desta feature MUST usar *deferido*, *indeferido*, *homologado* ou
  *matrícula efetivada*: esses fatos são da convocação, e afirmá-los aqui prometeria ao candidato um
  desfecho que esta feature não decide. A proibição MUST ser verificada por varredura, como a
  feature de ocupação já faz com o vocabulário dela.
- **UX-059**: Havendo sucessão, a tela MUST dizer que existe uma versão anterior e MUST dar acesso a
  ela — corrigir não é apagar, e a pessoa precisa poder ver o que declarou antes.

## 15. Reaproveitamento de dados

| Informação | Origem | O usuário |
|---|---|---|
| Nome, CPF | identidade | visualiza |
| E-mail | credencial provada | visualiza |
| Telefone | inscrição | confirma ou corrige |
| Perfil, modalidade, protocolo, Edital | inscrição e conteúdo publicado | visualiza |
| Endereço, filiação, documento, nascimento | requerimento anterior, quando houver | confere e corrige |
| Município, UF, código IBGE | referência de CEP | confirma |
| Data do requerimento | instante do envio | nada |
| Demais campos | — | informa pela primeira vez |

## 16. Relação com as features vizinhas

**Inscrição e documentos** — o requerimento lê a Inscrição e não a escreve. Nenhum documento é
reexigido por mudança de fase.

**Área do Candidato** — é o canal, e ganha um cartão e uma tela. Nome, CPF e e-mail continuam nas
telas que já os governam.

**Classificação e resultado** — **nenhuma relação de gatilho**. Estar classificado não abre o
requerimento (D-004), e o requerimento não entra em pontuação, ordem, corte ou desempate.

**Ocupação de vagas** — nenhuma. Uma vaga continua ocupada ou não pelos desfechos da convocação,
tenha o requerimento sido enviado ou não. **Requerimento não é condição de ocupação**, e torná-lo
condição mudaria a contagem de outra feature por efeito colateral.

**Convocação** — dependência de **leitura, num sentido só**: o requerimento pergunta se há chamada
em aberto. Ele não convoca, não registra desfecho, não defere e não cancela.

**Comissão e avaliação** — nenhuma. O requerimento não é avaliado nesta feature.

**Elaboração, publicação e contrato de mutabilidade** — governam a feature: os campos novos do
Edital são compostos, conferidos na publicação e classificados no contrato (FR-370, FR-407).

## 17. Auditoria

O envio grava, pelos mecanismos que já existem: quem, para qual Inscrição, para qual Edital, quando,
o que foi declarado, qual declaração, sob qual versão consolidada e, havendo, o que ele sucede e sob
autorização de qual convocação. Nada de event sourcing e nada de histórico de versões do rascunho —
o rascunho é rascunho, e o que vira peça de ato é o envio.

## 18. Privacidade

Cor/raça e necessidade específica são dados sensíveis; filiação, documento e endereço são dados
pessoais comuns cujo acesso é restrito ao titular e a quem conduz o certame. A minimização aparece
como **recusa escrita** na FR-382: oito informações do formulário atual não são coletadas por não
terem finalidade demonstrada. A renda é coletada, e em **faixa** (FR-412) — a forma menos granular
que serve à finalidade. A base local de CEP (D-009) evita transmitir continuamente endereço de
candidato identificado para terceiros. Dados geográficos, enquanto associados a alguém identificado,
continuam sendo dados pessoais — e a leitura agregada futura deve preferir município, cluster e
indicador a ponto individual.

**A regra alcança a própria documentação desta feature**: a amostra real usada na investigação é de
uma pessoa identificável, e nenhum valor dela é reproduzido em spec, descoberta ou teste. A §0 da
descoberta registra a política e a proveniência.

## 19. Contrato futuro para a exportação

`identidade + inscrição + requerimento + resultado + oferta + configuração institucional = linha
exportável`.

**Requerimento ≠ linha da planilha.** Das 34 colunas do formato atual, o requerimento responde por
16; oito são derivadas de resultado, oferta e protocolo; **cinco não têm fonte no sistema** —
`COD_CURSO`, `COD_TURNO`, `COD_POLO`, `COD_NACIONALIDADE` e a correspondência de
`COD_FORMA_INGRESSO`; três dependem de decisão do Registro Acadêmico — título, zona e seção
eleitorais; e uma é contradição aberta — `RENDA_PER_CAPITA_PNP`. O mapa completo, com a evidência de
cada linha, está na descoberta desta feature e é o artefato que a FR-403 manda manter.

**`RENDA_PER_CAPITA_PNP` deixou de ser campo sem fonte e passou a ser campo com fonte divergente.**
A origem está declarada — a faixa da FR-412 —, e a divergência também: o que se coleta é a soma da
família, e o que a coluna significa é o valor por pessoa. O contrato de saída MUST registrar as duas
coisas lado a lado, sem conversão inventada, porque conversão não existe (R-7).

## 20. Critérios de aceite

- **SC-120**: Em Edital que declara a coleta *na inscrição*, um candidato conclui o preenchimento
  informando **apenas** os campos que o sistema não conhece — nome, CPF, e-mail, curso, modalidade e
  protocolo não aparecem como campo em tela nenhuma.
- **SC-121**: Em Edital que declara *na convocação*, o requerimento é inacessível antes da chamada e
  acessível depois dela, sem intervenção manual.
- **SC-122**: Um suplente convocado três semanas depois do primeiro chamado recebe o requerimento
  pelo mesmo caminho, sem exceção de código e sem passo administrativo próprio.
- **SC-123**: Em Edital que não declara requerimento, não existe rota, cartão nem registro de
  requerimento — verificado inclusive por acesso direto ao endereço.
- **SC-124**: Um candidato com requerimento enviado em certame anterior encontra endereço, filiação e
  documento já preenchidos, e editá-los não altera o requerimento anterior — verificado lendo o
  anterior depois da edição.
- **SC-125**: Com o serviço de referência de CEP indisponível, o requerimento é preenchido e enviado
  por completo, com município e UF digitados e código IBGE vazio.
- **SC-126**: Com CEP reconhecido, município, UF e código IBGE chegam preenchidos sem digitação.
- **SC-127**: Uma tentativa de alterar ou excluir requerimento enviado é recusada pela tela, pela
  aplicação **e pelo gatilho de banco** — este último verificado com a role de runtime real, por
  `UPDATE` e por `DELETE` diretos, como os testes de append-only do projeto já fazem.
- **SC-128**: O envio sem aceite da declaração é recusado, e a recusa é anunciada antes da tentativa.
- **SC-129**: O registro do aceite permite reconstituir o texto exato que a pessoa leu, ainda que o
  Edital tenha sido retificado depois.
- **SC-130**: Nenhuma gravação desta feature alcança identidade, inscrição ou requerimento anterior —
  verificado por teste que conta gravações.
- **SC-131**: O acesso ao requerimento de outra pessoa é indistinguível de requerimento inexistente.
- **SC-132**: A varredura de vocabulário não encontra *deferido*, *indeferido*, *homologado* nem
  *matrícula efetivada* nas telas desta feature.
- **SC-133**: O mapa *campo de saída → origem* cobre as 34 colunas do formato atual, e cada uma tem
  origem declarada ou questão aberta nomeada — verificado por teste sobre o artefato.
- **SC-134**: Registrado o desfecho da chamada, o preenchimento encerra e a leitura permanece —
  verificado para as sete espécies de desfecho.
- **SC-135**: Convocado para regularizar, o candidato envia um sucessor; o anterior continua legível
  e a cadeia diz qual é o vigente. Sem chamada em aberto, a mesma tentativa é recusada.
- **SC-136**: Um Edital que declara o momento e não tem texto de declaração não publica — a
  conferência de conteúdo o acusa como erro impeditivo.
- **SC-137**: Nenhum artefato desta feature — spec, descoberta, teste ou fixture — contém dado
  pessoal da amostra real, verificado por varredura sobre os identificadores conhecidos.

## 21. Riscos

- **R-1 — O dado coletado e nunca usado.** Enquanto a exportação não existir, o requerimento produz
  dado que ninguém consome. Mitigação: o contrato de saída (FR-403) e a recusa da FR-382 mantêm o
  conjunto pequeno e justificado.
- **R-2 — Dado velho na matrícula.** Coleta antecipada mais dado mutável mais envio imutável.
  Mitigado pela sucessão sob chamada em aberto (D-007) e pela oferta de *conferir e atualizar*
  (FR-410); mitigação adicional disponível ao Edital: declarar *na convocação*.
- **R-3 — O PDF que nunca sai.** Decidido em 16/09/2026 que a retirada do Anexo assinado é ato de
  cada Edital. O risco que isso deixa de pé: **nenhum Edital exerce a decisão**, e a pessoa passa a
  preencher a tela *e* imprimir, assinar, digitalizar e anexar o mesmo conteúdo — pior que hoje. A
  mitigação não é técnica: é a composição do primeiro Edital que declarar requerimento, e o texto de
  ajuda da etapa de Documentos Exigidos MUST dizer, para quem elabora, que o Anexo passou a ser
  opcional quando há requerimento estruturado.
- **R-4 — A categoria que o destino não aceita.** *Indígena* é coletável aqui e não tem valor no
  formato do Registro Acadêmico. O problema é da composição da saída, e o achado precisa chegar a
  quem define o formato.
- **R-5 — Base de CEP desatualizada.** CEP novo não reconhecido cai na degradação da FR-390, que é o
  caminho normal e não um erro.
- **R-6 — A sucessão virar edição disfarçada.** Se a autorização da FR-408 afrouxar, o requerimento
  deixa de ser peça estável de ato administrativo. A guarda é a chamada em aberto, e ela é
  verificada por SC-135.

- **R-7 — A coluna de renda continua significando outra coisa que o dado coletado.** Decidido em
  16/09/2026 manter a pergunta atual (soma da família) para uma coluna definida como per capita. O
  indicador que alimenta a Plataforma Nilo Peçanha segue, portanto, medindo outra coisa — e **não há
  conversão possível**, porque dividir uma faixa por um número não produz uma faixa. A feature não
  esconde nem corrige: ela nomeia, no contrato de saída (§19) e no rótulo do campo (FR-412). Corrigir
  é decisão de quem define o formato de importação, e exige mudar a pergunta ou a coluna.
## 22. Questões abertas

- **Q-1** — O sistema deve passar a classificar a natureza do Processo Seletivo? Hoje a declaração do
  requerimento basta (D-002). Reabrir quando existir consumidor institucional. *(Não bloqueante.)*
- **Q-4** — Título, zona e seção eleitorais: coletar no requerimento, ou o Registro Acadêmico segue
  transcrevendo da certidão de quitação? *(Não bloqueante: hoje não são coletados, e a saída os
  registra como sem fonte.)*
- **Q-5** — Além da convocação para regularizar, há outra hipótese em que um requerimento enviado
  deva ser reaberto — e por quem? A D-007 fecha a única hipótese que a amostra sustenta. *(Não
  bloqueante.)*
- **Q-7** — `CLASSIF_CURSO_FINAL` é a classificação no curso ou a ordem das linhas do arquivo? O nome
  e o comentário do Registro Acadêmico discordam. *(Não bloqueante: é campo da exportação.)*
- **Q-10** — **O texto da declaração não aparece no Edital publicado.** O renderizador compõe
  coleções, e campo de raiz não é renderizado — precedente: `maxInscricoesPorCandidato` também não
  aparece. Quem lê o PDF do Edital não vê a declaração que terá de aceitar, embora ela seja norma
  daquele certame. Levar a declaração ao documento é decisão de produto, e fica registrada como
  **limite**, não como esquecimento. *(Não bloqueante: o texto é exibido por extenso na tela em que
  se aceita, e o aceite guarda o resumo do que foi exibido.)*
- **Q-9** — Foto: tem finalidade institucional? Nenhum artefato a consome, e por isso ela não é
  coletada. *(Não bloqueante.)*

## 23. Clarificações — resolvidas em 16/09/2026

As quatro decisões que mudavam modelo ou escopo foram respondidas na sessão de clarificação, e os
requisitos já as incorporam. **Nenhuma permanece bloqueante.** O registro fica na §*Clarifications*,
e o resumo é este:

| Era | Resposta | O que mudou |
|---|---|---|
| **Q-6** — regra da renda | coletar a faixa do **total** da família, como o formulário já faz | `FR-412` nasce, `FR-382` encolhe para oito, e a divergência com a coluna per capita vira `R-7` e §19 |
| **Q-2** — assinatura em papel | **cada Edital decide** retirar o Anexo | `FR-395` reescrita; `R-3` passa a ser "nenhum Edital exerce a decisão" |
| **Q-8** — nome social | **não nesta feature**, vira spec própria com alcance nomeado | `FR-382` distingue recusa de adiamento; §25.6 nomeia as cinco superfícies |
| **Q-3** — e-mail da matrícula | **o da conta**, sempre | `FR-378` fecha a questão e proíbe campo próprio |

## 24. Dependências

**Reais e de leitura** — a convocação (gatilho, FR-373; autorização da sucessão, FR-408), a
inscrição (titularidade e pré-preenchimento), o conteúdo publicado (declaração, momento e texto), a
conferência de conteúdo da publicação (FR-407), o contrato de mutabilidade (FR-370), a Área do
Candidato (canal).

**Declaradas e não construídas** — códigos institucionais de curso, turno, polo e nacionalidade; a
tabela de correspondência modalidade → forma de ingresso; a regra de faixa de renda. As três são da
exportação, e nenhuma bloqueia esta feature.

**Não é dependência** — ocupação de vagas: o requerimento não muda contagem nenhuma.

## 25. Consequências para features futuras

1. **A exportação nasce possível** — passa a ter origem única e estruturada para 16 das 34 colunas, e
   uma lista nomeada do que ainda falta.
2. **O endereço estruturado abre a leitura territorial** — município e código IBGE preservados por
   requerimento permitem, depois, inscritos por município e alcance de polo, sem que esta feature
   construa relatório nenhum.
3. **Os códigos institucionais viram incremento próprio** — curso, turno e polo como dados da oferta,
   e não texto livre em `locality`.
4. **A retirada do Anexo em papel é decisão de cada Edital**, e é a economia mais visível da
   feature — realizada no dia em que o primeiro certame deixar de declarar o documento.
5. **Se um Edital abrir matrícula sem chamada individual**, um terceiro momento nasce ali, com o caso
   que o justifique.
6. **Nome social e identidade de gênero ficam como lacuna conhecida, e são spec própria.** Decidido
   em 16/09/2026 não coletá-los aqui, e o alcance que a spec futura precisa cobrir está nomeado:
   **identidade** — onde o nome civil já mora e onde o social provavelmente deve morar —,
   **comprovante de inscrição**, **relação de habilitados**, **resultado divulgado** e
   **convocação**. Cada uma dessas superfícies tem de decidir nominalmente qual nome exibe, porque
   três delas são públicas e duas são peça de ato administrativo. Coletar o campo antes dessa
   decisão trataria a pessoa pelo nome social numa tela e pelo nome civil na seguinte — que é a
   razão escrita da recusa, e não falta de prioridade.
7. **O núcleo da identidade cresce, e esta feature nomeia o que ele deve receber.** Decidido em
   16/09/2026 **não** promover agora, e registrado como evolução natural: **data de nascimento** —
   imutável, e por isso o candidato a promoção mais seguro — e **nome social**, que a `Q-8` já
   apontou para lá. O **endereço corrente** entra quando existir o segundo consumidor; enquanto for
   só o requerimento, a cópia-para-a-frente basta. Os três cabem num incremento só, com a tela
   *Meus dados* como jornada — e, quando ele vier, **o requerimento continua guardando o seu
   snapshot**: a identidade passa a ser a origem do pré-preenchimento, nunca a fonte do que o ato
   declarou (`D-005`).
