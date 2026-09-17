# Diário de execução — Reauditoria exploratória UX (2026-09-16)

## Baseline

| Item | Valor |
|---|---|
| Commit (completo) | `5f37eecf63178b17153df4542cf619b868683d82` |
| Commit (abreviado) | `5f37eec` |
| Branch | `claude/reauditoria-processos-seletivos-de81a1` |
| Working tree no início | limpo |
| Data/hora de início | 2026-09-16 14:40 (-03) |
| Execução | nativa (`make runserver` via preview do harness) |
| Banco | PostgreSQL local, banco exclusivo `ps_reaudit_20260916` |
| Preparação | `make preparar` → **31 de 31 tabelas append-only protegidas**; `migrate --check` sem pendências |
| Porta | 8040 (`http://localhost:8040`) |
| Navegador | Browser pane do Claude Desktop (Chromium) |
| Viewport principal | desktop (pane); móvel 375px no portal |
| Identidade | seletor de identidade (`INTERFACE_SELETOR_IDENTIDADE=true`), portal demo (`PORTAL_IDENTIDADE_DEMO=true`) |
| Origem dos dados | Cenário 1 criado **do zero pela interface**; demais declarados por cenário |
| Alteração de working tree | apenas `.claude/launch.json` (entrada de preview acrescentada, sem tocar nas existentes) |

## Registro incremental

### Cenário 1 — Fase A (Concepção) — Persona A (novato), ator `ana.gestora` (Gestor)

**Estado inicial:** banco vazio, nenhum Processo.

1. `GET /` → consulta pública ("Seleções abertas"). Nenhum caminho visível para a interface
   administrativa. O único "Entrar" do cabeçalho leva a `/selecoes/acesso`, que é o portal do
   **candidato** (código por e-mail). **[UI]** Foi necessário consultar o README para saber que a
   gestão fica em `/gestao/`. → **ACH-01**, E4.
2. `GET /gestao/` → seletor de identidade. Papéis descritos por **strings de permissão**
   (`edital:elaborar`, `retificacao:submeter`…). Andaime de demonstração — não existe em produção.
   Observação, não defeito de produto. Frase relevante: "nenhum deles concede presidência nem
   avaliação" — primeiro sinal de que há **dois eixos de autorização** (papel institucional ×
   vínculo de comissão).
3. Entrei como `ana.gestora` com o papel **Gestor** — escolha natural, pois é onde está
   `processo:criar`.
4. `/gestao/` → botão **Novo Processo Seletivo** imediatamente visível. Encontrabilidade **E0**.
5. `/gestao/processos/criar` → a tela **ensina o conceito no momento da decisão**: "Um Processo
   Seletivo nasce com o primeiro Edital… o Processo reúne Editais que podem ter cronogramas
   próprios, e nenhum Edital existe sem ele." Responde a pergunta que eu havia registrado antes de
   clicar. → **PADRÃO A PRESERVAR (PP-01)**.
6. Criado: Processo `PS 01/2026` "Seleção de Tutores a Distância" + Edital `01/2026`.
   Dados **fictícios**, criados **pela interface**.
7. Tela do Processo: trilha `Em elaboração → Ativo → Encerrado` com "SITUAÇÃO ATUAL"; painel
   **"O que fazer agora"** dizendo *"Aguardando quem elabora para compor o Edital 01/2026"*;
   "Cancelar Processo" com selo `IRREVERSÍVEL` e bloqueio **anunciado antes da tentativa**, que ao
   expandir nomeia a causa e **linka o objeto responsável**. → **PP-02, PP-03**.
8. Tela do Edital: trilha de 5 estados, painel **"Quem atuou"** (Elaborou/Homologou/Publicou, todos
   "ainda não"), e **"Validação do conteúdo"** já listando `IMPEDE Ao menos um Perfil é
   obrigatório`, `IMPEDE Ao menos um Evento é obrigatório`, `AVISO Nenhum Evento… período de
   inscrições`. Pendências antecipadas, não descobertas na publicação. → **PP-04**.
9. **Bloqueio observado:** como Gestor não existe nenhum controle para criar Perfil ou Evento — as
   duas pendências que a própria tela declara. O painel nomeia o papel que falta ("quem elabora"),
   mas não diz ao ator que **ele** não é esse papel, nem oferece próximo passo. → **ACH-02**.

### Cenário 1 — Fase B (Estrutura da oferta) — ator `bruno.elaborador` (Elaborador)

Troquei de identidade porque o sistema pediu ("Aguardando quem elabora"). Como Elaborador a
listagem de `/gestao/` muda de forma: ganha contadores e uma coluna **"O QUE POSSO FAZER"** com as
ações permitidas ao ator. → **PP-05**.

**Assistente de composição:** 9 etapas numeradas com estado próprio
(`ETAPA ATUAL` / `CONCLUÍDA` / `PENDENTE` / `PRONTA PARA REVISAR`). Responde "onde estou" e "o que
falta" sem que eu precise perguntar. → **PP-06**.

Anomalia de ordem notada já na primeira tela: a etapa **8 (Conteúdo)** aparece `PRONTA PARA
REVISAR` enquanto 2–7 estão `PENDENTE`, num Edital recém-criado e vazio. A numeração sugere
sequência; o estado contradiz. → **ACH-03** (a investigar).

**Etapa 2 — Perfis de Vaga.** Definição boa e no lugar certo: "Cada Perfil é uma oportunidade do
Edital, com requisitos, vagas e modalidades próprios." O disclosure "Como preencher estes campos"
traz sete blocos conceituais densos — e aparece com **0 Perfis na tela**, isto é, explica campos
que ainda não existem. Usa vocabulário do produto ("Fatos exigidos do candidato", "lista
reservada") e uma frase que um novato não decifra: *"Percentuais de modalidades distintas não
somam cem por cento."* → **ACH-04**.

O formulário de um Perfil pede, de uma vez: código, denominação, localidade, descrição, carga
horária, remuneração, atribuições, requisitos, vagas imediatas, tipo de cadastro reserva,
modalidades de concorrência, **qual delas é a ampla concorrência**, **reversão de vaga reservada** e
**como a convocação é comunicada**. As três últimas são decisões de fases muito posteriores
(quadro de vagas, ocupação, convocação) cobradas na composição do Perfil, e duas delas só fazem
sentido se houver reserva declarada — que aqui não há. → **ACH-05**.

Perfil criado (fictício): `TUT-EAD` "Tutor a Distância", Vitória, 3 vagas imediatas, sem cadastro
reserva, sem modalidades. **Deixei `Como a convocação é comunicada` no default "Não declarado"**
de propósito, para descobrir em que momento essa omissão se manifesta (§12).

Nota lateral **[CÓDIGO/SPEC]**: os campos do formulário têm `name` em inglês (`duties`,
`requirements`, `reserveType`, `generalCompetitionModalityId`, `vacancyReversion`, `callForm`) num
projeto cuja convenção declarada é "tudo em português". Invisível ao usuário; registrado por
consistência. → **ACH-06** (S0).

**Etapa 3 — Cronograma.** Campo `Tipo` é **texto livre** sem vocabulário sugerido. Bom: "as datas
usam o horário de Brasília" — nenhum vazamento de UTC. Criei 4 Eventos: Inscrições
(16/09 00:00 → 30/09 23:59), Resultado preliminar (05/10), Recursos (06/10 → 07/10), Resultado
final (10/10).

Dois achados aqui:

- **ACH-07** — Ao avançar, a mensagem dizia *"Rascunho salvo — Cronograma"* e **na mesma tela** a
  etapa 3 aparecia `PENDENTE` (as etapas 1 e 2 tinham ficado `CONCLUÍDA`). A causa só é legível
  **dentro** da etapa 3, para onde é preciso voltar sem nenhum sinal de que há algo a ler.
- **ACH-08** — A causa, quando lida, é excelente em forma: *"Esta etapa fica pendente enquanto o
  Cronograma carregar Evento cuja data já passou — 1 dele agora. Corrigir as datas abaixo é o que a
  conclui; o sistema não as altera nem as sugere."* Mas o Evento acusado é o **período de
  inscrições que está em curso**: começou hoje às 00:00 e termina em 30/09. Um período aberto é
  tratado como data vencida. Consequência: um Edital legítimo — inscrições abrindo no próprio dia
  da publicação — **não consegue ter a etapa 3 concluída**. É `AVISO`, não `IMPEDE`, mas polui a
  trilha de progresso permanentemente.

**Etapa 4 — Etapas de Avaliação.** Duas decisões muito bem desenhadas:
- "Evento do Cronograma: vincular a Etapa a um Evento traz as datas de lá; não há data para digitar
  aqui." → elimina declaração dupla. **PP-07**.
- Forma de conclusão (`Com pontuação` × `Com decisão, sem nota`) declara a consequência **antes** da
  escolha: "A pontuada publica nota e não publica rótulos; a decisória publica os rótulos do
  resultado e não publica nota." **PP-08**.
Os rótulos do resultado só aparecem ao escolher "decisória" — progressive disclosure correto.
`Caráter` são dois checkboxes independentes: é possível salvar uma Etapa **nem eliminatória nem
classificatória**. Anotado para o teste de configuração contraditória (§20).

Etapa criada: "Análise Curricular", pontuada, nota mínima 40, máxima 100, eliminatória e
classificatória, **peso deixado vazio** (o campo diz `Peso (opcional)` / "Vazio: a Etapa não
pondera").

**Etapa 5 — Classificação (marcos classificatórios).** A tela mais densa do assistente. Conceito
novo e inteiramente do produto: **"marco classificatório"** — "Onde a ordem entre participantes é
produzida. Um Perfil sem marco não classifica." Assimetria de modelo: Etapas pertencem ao **Edital**,
marcos pertencem ao **Perfil**, e nada na interface explica por que os dois eixos são diferentes.
→ **ACH-09**.

Contei **28 controles** num único marco, para um Edital de 3 vagas e 1 Etapa. Entre eles, dois
obrigatórios que são matematicamente vazios quando há uma única Etapa: `Como as pontuações se
combinam` (soma × média ponderada) e `Normalização` (nenhuma × dividir pela soma dos pesos). Somam-se
`Casas decimais` e `Arredondamento`, obrigatórios e sem default. → **ACH-10**.

Ponto muito bom em contrapartida: os blocos colapsados exibem **o estado atual ao lado do título** —
"nada declarado", "este marco não sorteia", "este marco não corta". O default é legível sem abrir.
→ **PP-09**. (Defeito menor: esse resumo não acompanha a escolha feita no mesmo carregamento —
marquei "Admite recurso" e o resumo continuou "nada declarado". → **ACH-11**, S0/S1.)

Critérios de desempate oferecem três tipos: maior pontuação numa Etapa, maior/menor valor de um
**fato declarado**. Não há desempate por **maior idade** — praticamente obrigatório em edital
público brasileiro — a não ser modelando-o como fato autodeclarado pelo candidato. → **ACH-12**
(a confirmar na Fase 2). Microcópia excelente no tratamento da ausência: *"Precisa ser declarado: o
silêncio não vira zero nem último lugar."* → **PP-10**.

Marco criado: `CLASS-TUT` "Classificação Final", 2 casas, meio para cima, soma ponderada, sem
normalização, **admite recurso em 2 dias corridos**, sem corte, 1 critério de desempate.

**Etapa 6 — Inscrição.** É **aqui** que se designa qual Evento é o período de inscrições. Mas o
AVISO que aparece na tela do Edital e na etapa 6 diz *"Nenhum Evento do Cronograma está **marcado**
como período de inscrições"* — o verbo manda procurar no Cronograma (etapa 3), onde a marcação não
existe. → **ACH-13**, E2.
Boa consequência declarada: "Sem Evento designado, o Edital é publicado normalmente e apenas não
recebe inscrições."
Documentos exigidos pedem uma **"Chave"**: "Identificação estável, sem espaços. É por ela que o
sistema reconhece o documento entre uma versão do Edital e a seguinte." O operador precisa inventar
um identificador técnico e entender versionamento para preencher um campo obrigatório. → **ACH-14**.
Placeholders ensinam pelo exemplo (`ex.: diploma`, `ex.: Frente e verso, em arquivo único.`).
→ **PP-11**.
Criados: `diploma` (Diploma de graduação) e `curriculo` (Currículo), ambos obrigatórios, todos os
Perfis.

**Etapa 7 — Anexos.** "Este Edital ainda não publica anexo nenhum. **É legítimo**: nem todo Edital
fornece formulário próprio." Declarar que o vazio é válido evita ansiedade de pendência.
→ **PP-12**. Mas a etapa permanece marcada `PENDENTE` na trilha — o estado contradiz a própria
frase. → **ACH-15**.

**Etapa 8 — Conteúdo.** Separa seções **redigidas** (redação institucional padrão) de seções
**compostas automaticamente**, e cada composta linka para a origem do dado ("Ir para Perfis de
Vaga"), dizendo "corrigi-las é corrigir o dado que as origina". Resolve "onde eu conserto isto".
→ **PP-13**. Isso também explica **ACH-03**: a etapa 8 nasce `PRONTA PARA REVISAR` porque a redação
padrão já existe. Semanticamente correto; confuso só no primeiro contato, por contraste com os
`PENDENTE` vizinhos. Rebaixado a S1.

**Etapa 9 — Revisão.** Excelente: "O que falta para submeter" (IMPEDE/AVISO **com link direto para
corrigir**) + "O que será congelado na submissão", lido do próprio conteúdo normativo.
→ **PP-14, PP-15**.

**ACH-16 (forte).** Surgiu aqui um IMPEDE novo: *"O marco enumera uma Etapa sem peso declarado.
Quem enumera declara o peso: ausência não é equivalência, e o cálculo não a interpreta."*
Na etapa 4 o campo se chama **`Peso (opcional)`** e diz "Vazio: a Etapa não pondera". O campo é
opcional **só enquanto a Etapa não for enumerada por um marco** — decisão tomada na etapa 5,
**depois**. O rótulo "(opcional)" é condicionalmente falso, e a contradição só aparece na etapa 9.

**Correção do IMPEDE.** O link "Ir para Etapas de Avaliação" levou à etapa certa **e o IMPEDE
reapareceu lá**, no contexto de correção. → **PP-16**. Preenchi peso = 1.
Detalhe menor: a nota mínima que digitei como `40` reexibe como **`40.0000`** — precisão interna
(Decimal) vazando no campo do formulário. → **ACH-17** (S1).

**Prévia do Edital.** Microcópia que desarma o medo de agir: *"Isto não é o documento publicado…
Nada foi registrado por abrir esta tela: nenhuma Publicação, Revisão ou documento foi criado."*
→ **PP-17**. O PDF traz, em **todas** as páginas, a tarja `PRÉVIA — documento em elaboração, sem
valor de publicação`. → **PP-18**.

**ACH-18.** A numeração das seções **na tela de composição não é a do documento**. Na tela:
1 Apresentação, 2 Disposições Preliminares … 8 Critérios de Classificação, 9 Cronograma, 11 Anexos,
12 Disposições Finais. No PDF gerado: a apresentação é texto de abertura **sem número**, e a
numeração corre 1 Disposições Preliminares … 7 Critérios de Classificação, 8 Cronograma,
10 Disposições Finais — com **Anexos omitido** por estar vazio. Tudo fica deslocado em 1. Duas
pessoas conversando sobre "a seção 8" falam de coisas diferentes conforme olhem a tela ou o PDF — e
Retificação endereça seções.

### Cenário 1 — Fase C (Conferência e publicação normativa)

**Submissão.** Página de confirmação dedicada, com **"O que este ato provoca"** em três frases
("o conteúdo atual é congelado…", "não pode mais ser editado por este formulário", "fica registrada
em seu nome na auditoria") e **"Depois deste ato, o Edital fica aguardando quem homologa"**.
É ato administrativo consciente, não botão. → **PP-19**.
Após submeter, "Quem atuou" passa a exibir `bruno.elaborador · 16/09/2026 14:54`. → **PP-20**.

**Teste de segregação de funções (§20).** Reentrei como **`bruno.elaborador` acrescentando o papel
Homologador** — o mesmo indivíduo que consta em "Elaborou e submeteu".
- Na tela do Edital o painel passou a dizer *"O próximo ato é seu: homologar a revisão submetida"*,
  com o botão habilitado, **sem nenhuma menção** de que homologar consumiria a possibilidade de
  publicar. → **ACH-19** (S1).
- Ao abrir a tela de Homologar, a advertência aparece, e é exemplar: *"Depois de homologar, você não
  poderá publicar esta revisão. Você a elaborou, e publicar exige que ao menos outra pessoa
  autorizada tenha participado. Homologar é permitido; a publicação precisará de outra autoridade."*
  Bloqueio anunciado **antes** da tentativa, com a regra explicada e o que continua permitido.
  → **PP-21**.
- `Fundamento da homologação` é obrigatório e vai para a auditoria e para o ato. → **PP-22**.
- Homologado. O painel passou a: *"Você não poderá publicar este Edital. Você elaborou e homologou
  esta revisão; ao menos outra pessoa autorizada precisa participar. **Peça a alguém com a permissão
  de publicar que conclua o ato.**"* — o bloqueio **diz o que fazer**. → **PP-23**.
  Isso reforça **ACH-02**: o padrão "explique o bloqueio e indique o próximo passo humano" existe e
  é bom; ele simplesmente **não foi aplicado** na tela onde o Gestor sem papel de elaborador trava.
- Existe **Revogar homologação** — recuperação disponível antes de publicar. → **PP-24**.

Regra de segregação confirmada pela interface: o arco elaborar→homologar→publicar exige **ao menos
duas pessoas distintas**, não três.

**Publicação.** Tela exemplar: título **"Este ato não pode ser desfeito"** com quatro consequências
concretas — torna-se público e imutável; correções só por Retificação com novo fluxo de aprovação;
o documento é gerado e preservado **com o hash do conteúdo homologado**; passa a constar da consulta
pública. Exige **Autoridade Signatária** (Reitora / Pró-Reitor / Diretora do Cefor), conceito
separado de "quem operou o clique". → **PP-25, PP-26**. A resposta do §18 é afirmativa: a publicação
é apresentada como ato administrativo consciente.

Publicado às 14:56 por `diego.publicador`, signatária Diretora do Cefor. Depois disso:
"Nenhum ato disponível para seus papéis nesta situação" (a ausência é explicada, não silenciosa) e
o bloco "Documentos publicados" com a ressalva conceitualmente precisa — e difícil — de que
*"a vigência é da versão consolidada, que não tem documento próprio… então nenhum destes é o
'documento vigente'"*. → **ACH-20** (D1/D2, densidade).

### Cenário 1 — Fase D (Inscrição) — Persona E (candidata), `maria.candidata@exemplo.test`

Dados **inteiramente fictícios**. CPF `111.444.777-35` (CPF de teste notório).

**Descoberta.** A raiz pública lista a seleção com filtros por situação (incluindo a opção honesta
"Sem inscrição por aqui"), por cargo/curso e ordenação. O cartão traz `ABERTA`, as vagas e
**"Faltam 14 dias"**. → **PP-27**.
Na página da oferta: requisitos, atribuições, carga horária, remuneração, "2 documentos que serão
pedidos", "Inscrever-se exige identificação por e-mail", link para o Edital em PDF e um Cronograma
com o marcador **"ACONTECENDO AGORA"**. → **PP-28**.

**ACH-08 confirmado como inconsistência real entre superfícies:** o mesmo Evento que a gestão
acusa como *"começou em 16/09/2026 às 00:00, que já passou"* o portal exibe corretamente como
*"Inscrições abertas desde 16/09/2026 … Faltam 14 dias"* e *"ACONTECENDO AGORA"*. Um período em
curso é lido como vencido de um lado e como aberto do outro.

**ACH-21** — Observação no publicado: **Requisitos** viraram lista e **Atribuições** viraram
parágrafo corrido. A diferença decorre de microcópias distintas na composição ("Um requisito por
linha" × "Uma linha em branco separa parágrafos"), mas só se descobre **no documento já publicado** —
e a partir daí só se corrige por Retificação. (S1)

**Identificação.** Código por e-mail, sem senha. A tela não revela se o endereço existe ("Se este
endereço **puder ser utilizado**, enviaremos um código") e há cooldown de reenvio. → **PP-29**.
O `?destino=` preserva a intenção. **ACH-22** (S1): ainda assim, depois de identificar-se e
preencher "Seus dados", a candidata é devolvida à **página da vaga** e precisa clicar
"Inscrever-se" outra vez — a intenção original não é retomada sozinha.

**Preenchimento.** Stepper de 3 etapas com progresso; contador "Faltam 2 de 2 documentos
obrigatórios" com link "Ver quais"; e a garantia que desarma o medo de perder trabalho:
*"Seus dados e arquivos ficam guardados enquanto as inscrições estiverem abertas. Você pode sair e
voltar quantas vezes precisar."* → **PP-30**. Cada upload devolve nome do arquivo, timestamp,
"Substituir ou remover", barra e contador — e a frase de rodapé chega a concordar no singular
("o documento que falta"). → **PP-31**.

**Revisão.** "Editar" por bloco, duas declarações obrigatórias e
*"Depois de enviada, a inscrição não pode ser alterada."* → **PP-32**.
**ACH-23** (S1/S2): a declaração *"Declaro ter lido e estar de acordo com o Edital e os atos
vigentes"* **não linka o Edital nesta tela** — declara-se a leitura de um documento que não está ao
alcance no momento da declaração. Tentativa de enviar sem marcar cai na validação nativa do
navegador ("Marque esta caixa se deseja continuar"), genérica e não anunciada antes. (S0/S1)

**Comprovante.** Protocolo `INS-2026-WU3PBBC5`, código de verificação, SHA-256 por documento **com
instrução de conferência** (`shasum` / `certutil`), hash do próprio PDF, e duas frases decisivas:
*"O recebimento não implica deferimento"* e **"Versão do Edital: vigente desde 16/09/2026 às
14h56"** — a candidata sabe a que versão aderiu. → **PP-33, PP-34, PP-35**.
**ACH-24** (a verificar): "Este comprovante fica disponível **enquanto as inscrições deste Processo
Seletivo estiverem sob análise**" sugere indisponibilidade futura de um documento que o candidato
pode precisar depois.

**Responsividade (§26).** Portal a 375px: stepper adaptado, tipografia legível,
`scrollWidth == clientWidth` (sem overflow horizontal). → **PP-36**.

**Retorno e acompanhamento (§14).** "Minhas inscrições" lista com protocolo e situação; a tela da
inscrição traz o que foi enviado, com Visualizar/Baixar por documento e "Baixar comprovante"; e
`/acompanhamento` separa **"Sua participação"** (linha do tempo individual) de **"Cronograma do
processo"** (geral). A distinção individual × geral existe e é legível. → **PP-37**.

Mais três inscrições criadas pelo portal, com dados fictícios: `joao.candidato` (João Pedro de
Testes), `ana.candidata` (Ana Clara de Testes), `carlos.candidato` (Carlos Eduardo de Testes).
Total: **4 inscrições submetidas**.

> **Limitação de ferramenta declarada:** a automação do painel não expõe seletor de arquivo. Os PDFs
> foram construídos no próprio formulário da página (DataTransfer) e **submetidos pelo botão real do
> formulário**. O caminho do produto foi o mesmo; apenas a escolha do arquivo no disco não passou
> pelo diálogo do sistema operacional.

### Cenário 1 — Fase E (Organização do trabalho) — Persona C (presidência), `ana.gestora` (Gestor)

Ao publicar, o Processo passou sozinho a **Ativo**, cumprindo o que a tela havia anunciado
("Publicar o primeiro Edital deste Processo já o ativa"). Consequência prometida e cumprida.
→ **PP-38**.

**ACH-25** (§25, visão global) — Com o Processo ativo e 4 inscrições recebidas, o painel **"O que
fazer agora"** da tela do Processo oferece apenas **Encerrar Processo** e **Cancelar Processo**,
ambos `IRREVERSÍVEL`. Nada sobre quantas inscrições chegaram, comissão a compor ou avaliação a
organizar. O painel que orientava durante a elaboração some justamente quando o Processo está vivo,
e no lugar dele restam duas ações destrutivas.

**Comissão.** Encontrabilidade **E0** (aba "Comissão" na tela do Processo).
- Dependência anunciada **antes** de morder: *"Esta comissão ainda não tem presidente. Constituir
  sem presidência é permitido, mas nenhuma Etapa pode receber alocação enquanto ninguém responder
  pelo trabalho distribuído."* → **PP-39**.
- Honestidade sobre a limitação real: *"O identificador não é verificado pelo sistema… é ele — e não
  o nome — que dá acesso à pessoa."* → **PP-40**.
- **Passo de conferência dedicado** ("Confira antes de incluir" / "O que será gravado"), com a
  consequência do erro escrita: *"a pessoa constará da comissão e nunca conseguirá acessar as Etapas
  dela"*. → **PP-41**.
- Inclusão em lote com tabela de conferência, coluna `situação` por linha e a regra de duplicata
  explicada ("Quem já integra a comissão é ignorado — não impede as demais"). → **PP-42**.

Comissão constituída (fictícia): `paula.presidente` (Presidente), `rafael.avaliador`,
`sofia.avaliadora`.

**Alocação por Etapa.** Matriz avaliador × Etapa, contadores no topo ("1 Etapa com equipe / 0 sem
ninguém / 1 de 3 sem nenhuma Etapa"), atalhos "Todos · Nenhum" por coluna e `aria-label` completo em
cada célula ("Rafael Avaliador de Testes em Análise Curricular, Edital 01/2026"). → **PP-43, PP-44**.
Rafael e Sofia alocados; a presidência deliberadamente **não** alocada, para ver se consolidar exige
alocação.

**Distribuição — BLOQUEIO LEGÍTIMO E BEM EXPLICADO.**

> *"Ainda não é possível distribuir esta Etapa. As inscrições ficam abertas até 30/09/2026 às 23:59.
> Distribuir agora deixaria sem avaliador quem se inscrever depois. Antecipar o término publicado é
> ato de Retificação; encerrar o Edital é outro ato, mais amplo e irreversível."*

Explica a razão, a consequência e **as duas saídas legítimas**, nomeando o custo de cada uma.
→ **PP-45**. É o melhor bloqueio que vi no produto.

**ACH-26** (ordem de decisão, §11) — Ainda assim, essa dependência **não é dita onde a decisão é
tomada**. Quem preenche o Cronograma (etapa 3) não é avisado de que a data de término das inscrições
governará quando a avaliação pode começar; descobre-se só aqui, com o Edital já publicado e a
correção custando uma Retificação.

**ACH-27** (densidade, §26) — A tela empilha oito contadores, vários com o mesmo valor e nomes
quase sinônimos: `4 todas`, `4 sem nenhum avaliador`, `4 sem avaliador suficiente`, `4 com avaliação
pendente`, e ainda `0 prontas para consolidar / 4 ainda não consolidáveis / 0 já consolidadas`. A
distinção entre "sem nenhum avaliador" e "sem avaliador suficiente" é real, mas não é legível no
primeiro contato.

Ponto forte na mesma tela: *"O sistema propõe uma distribuição… e mostra a proposta inteira antes de
gravar. A decisão continua sendo sua: nada acontece sem a sua confirmação."* → **PP-46**.

**Decisão de caminho:** sigo pela via que o próprio bloqueio indica — **Retificação** antecipando o
término das inscrições. Isso cumpre a Fase L (obrigatória) e desbloqueia as Fases F–K.

### Cenário 1 — Fase L (Retificação) — `bruno.elaborador` (Elaborador)

**ACH-28** (S2) — Na tela do Edital **já publicado**, o aviso *"Você não poderá publicar este
Edital. Você elaborou e homologou esta revisão; ao menos outra pessoa autorizada precisa participar.
Peça a alguém com a permissão de publicar que conclua o ato."* **continua sendo exibido**, embora o
Edital tenha sido publicado por `diego.publicador` às 14:56. É uma mensagem de bloqueio obsoleta,
sobre um ato que já foi concluído, num Edital cujo estado é `Publicado`.

**ACH-29** (S1) — O `AVISO` sobre a data do Evento que "já passou" também persiste **depois da
publicação**, onde não há mais nada a fazer a respeito.

**ACH-30** (S1/S2) — Para o ator com papel **Gestor**, a tela do Edital publicado diz "Correções
ocorrem por Retificação" mas **não oferece a ação nem diz quem pode fazê-la**. A ação "Retificar" só
aparece para quem tem `retificacao:elaborar`. Repete-se o padrão do **ACH-02**.

**A tela de Retificação.** Muito bem construída:
- "Altere os campos que precisam mudar. **O que você não tocar permanece como está.**" → modelo
  mental correto na primeira frase. → **PP-47**.
- "Como funciona": explica Alteração Normativa, o efeito de "Remover do Edital" e fecha com
  **"Nada muda para o público até a Retificação ser publicada."** → **PP-48**.
- Navegação "IR PARA" com contador por seção, busca e filtro **"Só o que eu alterei"**. → **PP-49**.
- Cada seção traz um disclosure **"O que não se corrige por Retificação nesta seção"** — nomeia
  explicitamente o que é imutável, em vez de apenas omitir os campos. → **PP-50**.
- Vigência: "Vazio significa vigorar na Publicação. Data futura significa que o conteúdo atual
  continua valendo até lá." → **PP-51**.

**PP-52 — a conferência prévia funcionou de verdade.** Ao clicar em "Ver o que vai mudar", a tabela
acusou **2** alterações quando eu pretendia 1: o texto da justificativa havia caído no campo
**Local do Evento 1**. *(Apuração honesta: a causa foi **erro da minha automação** — clique por
referência em elemento fora do viewport —, não do produto.)* O valor está no episódio: a prévia
exibiu `Local | — | <texto>` e **impediu que uma Alteração Normativa indevida entrasse no Edital**.
É a demonstração prática da função da tela.
**[HIPÓTESE DE PESQUISA]** A página de Retificação é muito longa e mistura campos de uma linha com a
justificativa no rodapé; digitar no campo errado parece plausível também para um humano, mas isso
exigiria validação com usuários reais — não observei um humano cometendo o erro.

**O diff normativo é exemplar.** "O que vai mudar (1)": `Evento 1 — Inscrições | Término |
~~30/09/2026 23:59~~ | 16/09/2026 15:00`, com o valor antigo riscado e o novo destacado. Nome de
Evento, nome de campo e datas em horário local. Nenhum identificador técnico. → **PP-53**.

**ACH-31 (S2) — vazamento de estrutura técnica no ato criado.** A mesma alteração, na tela da
Retificação já criada, aparece assim:

```
Evento do cronograma "Período de inscrições pelo portal do candidato"
Término
/schedule/id=f15da77c-2b40-470d-abbb-5aa75f2a9f36/endAt
REPLACE | 30/09/2026 23:59 | 16/09/2026 15:00
```

Vazam para o operador: **o caminho de endereçamento normativo**, o **UUID** do Evento, o nome do
campo **em inglês** (`endAt`) e a operação como vocabulário de máquina (**`REPLACE`**). O contraste é
o que torna o achado nítido: a **prévia** do mesmo dado é impecável, e a tela do **ato** — a que fica
registrada — é a que exibe o endereço interno. *(A verificar: se isso alcança a consulta pública.)*

**ACH-32 (S2) — ruído severo na tela de Retificação.** Ela expõe todos os campos de todas as
entidades, inclusive o bloco inteiro de **sorteio** num Edital que não sorteia, com identificadores
de máquina como opções visíveis de select: `IFES-SORTEIO-SHA256-v1`, `DIGITOS_EM_SEQUENCIA`,
`TEXTO_LITERAL`, `OCORRENCIA_SEGUINTE_DA_MESMA_FONTE`.

**ACH-33** — A Retificação lista as seções como `SEÇÃO 8 — Critérios de Classificação`,
`SEÇÃO 10 — Dos Recursos`, `SEÇÃO 12 — Disposições Finais`, pulando as compostas. É a numeração da
**tela de composição**, não a do **documento publicado** (onde são 7, 9 e 10). Agrava **ACH-18**,
porque é na Retificação que o endereçamento de seção mais importa.

**ACH-34 (relevante para o modelo)** — Na Retificação, o Evento tem o campo **"É o período de
inscrições: Sim/Não"**, que **não existe** na composição do Cronograma (etapa 3), onde a designação
é feita na etapa 6 (Inscrição). O mesmo fato normativo é editado em lugares e formas diferentes
conforme a superfície. Confirma e amplia **ACH-13**.

**Fluxo da Retificação (atores distintos).** `bruno.elaborador` criou e submeteu →
`carla.homologadora` homologou (com fundamento obrigatório) → `diego.publicador` publicou às 15:13,
signatária Diretora do Cefor. A tela de publicação da Retificação repete o padrão do Edital e
acrescenta a garantia decisiva: **"A Publicação original e as versões anteriores continuam
preservadas e consultáveis."** → **PP-54**.

**PP-55 — o seletor de identidade passou a ensinar o modelo.** Depois que a comissão existiu, a
tela de identificação ganhou sozinha uma seção **"Quem tem trabalho de comissão neste ambiente"**,
listando `paula.presidente · preside PS 01/2026`, `rafael.avaliador · integra … 1 Etapa alocada`, e
explicando a distinção que eu vinha tentando montar desde o início:
*"Presidir e avaliar **não são papéis** — vêm do vínculo com a comissão."*
*(Ressalva: é andaime de demonstração; em produção essa explicação não existirá, e o duplo eixo de
autorização continuará sem lugar onde se aprender.)*

**ACH-31 delimitado — o vazamento é só da interface administrativa.** O mesmo fato normativo
aparece em três lugares:

| Superfície | Como aparece |
|---|---|
| Prévia da Retificação (gestão) | `Evento 1 — Inscrições \| Término \| ~~30/09/2026 23:59~~ → 16/09/2026 15:00` — limpo |
| **Tela do ato (gestão)** | `/schedule/id=f15da77c-…/endAt` + **`REPLACE`** — **vaza** |
| Consulta pública | **`ALTERADO`** — Evento do cronograma "Período de inscrições…" — Término — limpo |

A tradução para linguagem normativa **existe** (o público diz `ALTERADO`); ela apenas não foi
aplicada na tela interna, que é justamente a que fica registrada para o operador. Como não alcança
candidato nem cidadão, **rebaixo ACH-31 de S3 para S2**.

**Efeito público da Retificação (§14).** A página da seleção passou a `ENCERRADA`, "Inscrições
encerradas em 16/09/2026", o Cronograma marcou ✓ no Evento cumprido, e apareceu o aviso:
*"Este Edital foi retificado. O que você lê nesta página é o conteúdo vigente desde 16/09/2026 —
veja o que mudou."*, com o bloco "Edital e documentos" listando **Retificação 16/09/2026**,
**O que mudou (1)** e **Edital de abertura 16/09/2026**. O candidato percebe a Retificação, lê a
justificativa e alcança as duas versões. → **PP-56, PP-57**.

Verificado também que a sessão do **portal** é independente da sessão da **gestão** (o portal seguia
como `Carlos Eduardo de Testes` enquanto a gestão estava em `diego.publicador`). Não há vazamento
entre superfícies.

### Cenário 1 — Fase F (Avaliação) — Persona D, `rafael.avaliador` e `sofia.avaliadora`

**404 confirmado como autorização, não rota quebrada.** Como `diego.publicador` (sem vínculo de
comissão) a URL de distribuição devolveu **404** — mas a própria página de debug mostra que a URL
*casou* com o padrão. Com `paula.presidente` a mesma URL abre normalmente. Regra do projeto
confirmada na prática.
**ACH-35 (S2)** — Ainda assim, essa negativa é a **única do produto que não se explica**. Em todo o
resto o sistema diz "Nenhum ato disponível para seus papéis nesta situação" ou explica o bloqueio e
indica o próximo passo; aqui devolve um 404 seco (em desenvolvimento, a página de debug do Django
com a lista completa de rotas internas). É inconsistente com o padrão que o próprio produto adota.

**Distribuição.** Com as inscrições encerradas pela Retificação, o bloqueio desapareceu sozinho.
A proposta automática é excelente: *"4 atribuições em 4 inscrições, distribuídas por menor carga.
**Confira antes de confirmar — nada foi gravado ainda.**"*, com a tabela
`AVALIADOR | TEM HOJE | RECEBE | FICA COM` → `Rafael 0 +2 2`, `Sofia 0 +2 2`. Antes, delta e depois
na mesma linha. → **PP-58**. Confirmada: "4 atribuídas".
A presidência distribui **sem estar alocada** à Etapa — coerente com "presidir ≠ avaliar".

**A mesa do avaliador.** Entrando como `rafael.avaliador`, o sistema cai **direto em "Minhas
Etapas"**: "As Etapas em que você tem atribuição", com o vínculo ("Comissões que você integra") e um
cartão por Etapa com **"2 pendentes"**, barra de progresso e "0 de 2 avaliações concluídas".
Encontrabilidade **E0 sem nenhuma exploração**. → **PP-59**.
Dentro: **"Minha Mesa"** — `2 no total / 2 não iniciadas / 0 em rascunho / 0 concluídas` — mais
`SUA SITUAÇÃO: Alocado nesta Etapa` e `CARÁTER: Eliminatória e classificatória`. A resposta ao §15 é
clara: **é mesa de trabalho, não um conjunto de páginas administrativas**. → **PP-60**.

**A tela de avaliação é o melhor artefato do produto.** Reúne:
- **CPF mascarado** (`***.982.247-**`) na tela de trabalho — minimização de dado pessoal. → **PP-61**.
- Rastreio real de leitura: **"0 de 2 abertos por você"** → depois de abrir, **"2 de 2 abertos por
  você"**, com selo `aberto` em cada documento. → **PP-62**.
- Aviso antes do erro mais provável do domínio: *"Você ainda não abriu nenhum documento desta
  inscrição."* (aviso, não impedimento — o sistema registra em vez de decidir). → **PP-63**.
- A regra aplicável à vista: "Máxima publicada: 100. Nota mínima: 40."
- O parecer explicado pela sua **finalidade futura**: *"É o que responderá a um eventual recurso."*
  → **PP-64**.
- Rascunho (`Salvar sem concluir`) × conclusão, e **"Próxima pendente — inscrição INS-…"** para
  trabalho em volume. → **PP-65**.

**Caminhos errados testados (§20):**
- Concluir sem pontuação → recusado com `"Informe a pontuação."` (mensagem da aplicação).
- Pontuação 30 (abaixo do mínimo 40) sem parecer → recusado com a **melhor mensagem do sistema**:
  *"Esta Etapa é eliminatória e a pontuação ficou abaixo da nota mínima: o parecer é obrigatório,
  **porque é ele que responde a um recurso**."* Explica a regra e o fundamento. → **PP-66**.
- Detalhe refinado de foco: *"Você abriu documento desta inscrição — por isso o cursor começa aqui."*
  → **PP-67**.

Ao concluir, o sistema **avança sozinho para a próxima pendente** e confirma o ato anterior
("Avaliação da inscrição INS-… concluída. Esta é a próxima pendente da sua Mesa"), e ao final:
"Não há mais inscrições pendentes suas nesta Etapa." → **PP-68**.
A avaliação concluída vira leitura (nota, timestamp, parecer) com a recuperação nomeada:
**"Para alterar, a reabertura é ato da presidência, com motivo registrado."** → **PP-69**.

**Avaliações registradas (fictícias):** João Pedro `30` (abaixo do mínimo), Ana Clara `85`,
Carlos Eduardo `78`, Maria Aparecida `92`.

### Cenário 1 — Fase G (Consolidação e classificação) — `paula.presidente`

**ACH-36 (S2, D2/D3)** — **"Consolidar"** é o conceito que faz a ponte entre avaliação individual e
resultado da Etapa, e **não é definido em nenhum lugar da tela de distribuição**, onde o botão vive.
Compare com "Perfil de Vaga" e "marco classificatório", que ganham uma frase no ponto de uso.

**PP-70 — a melhor resposta do sistema ao §16.** A tela "Confira antes de consolidar" abre com a
definição, no momento exato do ato: *"O Resultado nasce do cálculo que o Edital publica: a pontuação
é cópia da avaliação e a consequência sai da regra. Não há desfazer — corrigir um Resultado
consolidado é ato de outra espécie."* E a tabela traz uma coluna **POR QUÊ** com a regra aplicada e
os números:

| INSCRIÇÃO | PARTICIPANTE | CONSEQUÊNCIA | POR QUÊ |
|---|---|---|---|
| INS-…WU3PBBC5 | Maria Aparecida | Habilitada | pontuação igual ou superior à nota mínima (92 ≥ 40) |
| INS-…QNU4ZPQZ | João Pedro | **Eliminada** | pontuação inferior à nota mínima (30 < 40) |

A pergunta "o operador entende por que aquela pessoa chegou àquela situação?" é respondida
**afirmativamente e sem esforço**. (Senão menor: `92,0000`, repetindo **ACH-17**.)

**Classificação.** A tela distingue cálculo de ato desde a primeira linha: *"Ainda não existe ato
emitido para este marco. **A lista abaixo é uma proposta calculada agora.**"* → **PP-71**.
E antes de emitir: *"O sistema recalcula sob trava e grava um ato imutável; **esta tela não envia
posição, pontuação nem desempate**."* — desarma o receio de emitir a partir de uma tela defasada.
→ **PP-72**.
Duas tabelas — com posição e **sem posição, com MOTIVO** —, e após a emissão: histórico de atos,
campo "Motivo da sucessão" para uma nova ordem, e a separação explícita entre emitir e divulgar:
*"Este ato ainda não foi divulgado. **O público não lê esta ordem enquanto a publicação não
acontecer.**"* → **PP-73, PP-74**.

Ordem emitida às 15:19 por `paula.presidente`: 1º Maria (92), 2º Ana Clara (85), 3º Carlos (78);
João Pedro sem posição (eliminado).

**ACH-37 (S1/S2, E2)** — A instrução diz que a divulgação "sai de lá — em **Consultar ato e
proveniência**". O rótulo do link anuncia *consulta*, não uma ação de publicação; a ação de divulgar
mora atrás de um nome que não a sugere.

**ACH-38 (S1/S2)** — Seguida a instrução, a presidência chega ao ato e lê: **"Você não tem ação
disponível sobre este ato."** Divulgar exige `resultado:publicar`, que é do Publicador. O caminho
indicado termina em beco para o ator que foi mandado segui-lo, e **sem a frase "peça a alguém com a
permissão de publicar"** que o produto usa tão bem no Edital (**PP-23**). Terceira ocorrência do
mesmo padrão — ver **ACH-02** e **ACH-30**.

**ACH-39 (S2) — a tela menos legível do produto.** "Ato de classificação" é composta quase
integralmente de identificadores opacos: o título é `Ato c818be37-…`; a Proveniência lista o UUID de
Processo, Edital, Perfil, Marco e Versão normativa; e a tabela **"Resultados que entraram na ordem"**
tem **quatro colunas inteiras de UUID** (RESULTADO, INSCRIÇÃO, ETAPA, VERSÃO) sem uma única coluna
legível — não há nome de participante nem nome de Etapa. O desempate aparece como
`MAIOR_PONTUACAO_NA_ETAPA · e8e3ebd5-…`. O rastro por identificador é legítimo e necessário; o que
falta é a **tradução ao lado dele**, que o produto faz bem em todas as outras telas.

**ACH-40 (S3) — divulgar resultado exige papel *e* vínculo de comissão, e isso não é dito.**
Sequência observada:
- `diego.publicador` (papel **Publicador**, `resultado:publicar`) → a URL do ato devolve **404**, e a
  tela do Edital **nem exibe o bloco "Classificação"**. Nenhum caminho.
- `paula.presidente` (vínculo de comissão, sem `resultado:publicar`) → "Você não tem ação disponível
  sobre este ato."
- `paula.presidente` **+ papel Publicador** → **"Publicar resultado" aparece.**

Conclusão pela interface: divulgar o resultado de um marco exige **simultaneamente** o papel
`resultado:publicar` **e** vínculo com a comissão do Processo. Isso não está declarado em lugar
nenhum — e o seletor de identidade afirma o contrário ao listar `resultado:publicar` sob "Publicador".
Consequências: (a) uma instituição que designe um publicador institucional **fora** da banca não
consegue divulgar resultado algum; (b) o contorno é incluí-lo na comissão, o que distorce a
composição registrada da banca; (c) a negativa é um **404 mudo**, sem a frase "peça a alguém com a
permissão de…" que o produto usa tão bem (**PP-23**). *(A confirmar na Fase 2 se é deliberado; ainda
que seja, a comunicação falha.)*

### Cenário 1 — Fase H (Resultado preliminar)

**PP-75** — A tela "Publicar resultado" faz uma **verificação de publicabilidade** explícita:
*"nada impede esta divulgação. O ato é o vigente do marco, e a norma e o universo não mudaram desde a
emissão."* — confere a coerência entre o momento da emissão e o da divulgação.
**PP-76** — "O que acontece ao confirmar" inclui uma **decisão de privacidade explicada**:
*"A lista pública nomeia apenas quem recebeu posição; quem não recebeu vê a própria situação dentro
da inscrição."* O eliminado **não é exposto publicamente**.
**PP-77** — Natureza `Preliminar` × `Definitivo` com a regra declarada: *"Um resultado definitivo não
é sucedido por um preliminar."* Mais autoridade signatária e prévia da lista pública.
Nota técnica: o formulário carrega `chave_idempotencia` e `confirmacao_da_previa` — proteção contra
dupla submissão e contra divergência entre prévia e confirmação (§20, "repetir uma operação
sensível"). → **PP-78**.

Resultado **preliminar** publicado às 15:22, signatária Diretora do Cefor.
Página pública anônima: "Este é o resultado vigente deste marco", data, autoridade, lista e
**PDF oficial**. → **PP-79**.

**Acompanhamento do candidato classificado (Carlos, 3º).**
- **PP-80 (excelente)** — *"Este Edital foi atualizado após sua inscrição. **Sua inscrição continua
  valendo sob a versão que você aceitou.**"* Resolve, em duas frases, a insegurança jurídica do
  candidato diante de uma Retificação.
- **PP-81** — "Resultado das etapas → Análise Curricular: **Habilitada · pontuação 78**" com o motivo
  ("78,0000 ≥ 40,0000"), e "Classificação Final → Resultado preliminar → **3º lugar**".
- **PP-82** — *"Cabe recurso contra este resultado até 18/09/2026 às 23h59"* com o botão
  **"Recorrer de um resultado"**. Prazo calculado e oferecido no lugar certo.

**ACH-41 (S3) — duas datas-limite contraditórias na mesma tela.** O candidato lê, na mesma página:

> "Cabe recurso contra este resultado até **18/09/2026** às 23h59."  (janela do marco: 2 dias da divulgação)
> Cronograma: "Prazo para interposição de recursos … **06/10/2026 – 07/10/2026**"

São duas fontes normativas do mesmo prazo — a **janela recursal declarada no marco** e o **Evento do
Cronograma** — e o sistema **não as confronta em momento algum**: nem na composição, nem na
"Validação do conteúdo" do Edital, nem na publicação do resultado. Um candidato que confie no
Cronograma publicado **perde o prazo real** por 18 dias.
*(Honestidade metodológica: a configuração incoerente foi minha, ao antecipar a divulgação sem mexer
no Cronograma. O achado não é o meu erro — é que **produzir essa contradição é trivial e o sistema
nunca a sinaliza**, nem ao operador nem ao candidato. Ecoa o achado já conhecido do projeto de que
checklist e testes de citação ficam verdes com regras incompatíveis.)*

**ACH-17 chega ao candidato** — o motivo exibido ao público repete a precisão interna:
"78,0000 ≥ 40,0000", enquanto a lista publicada usa corretamente `78,00`.

**Acompanhamento do candidato eliminado (João Pedro).** Vê "Análise Curricular — **Eliminada ·
pontuação 30**" com o motivo, "Você não foi classificado neste marco" e o recurso oferecido no lugar
certo. A situação individual é clara.

**ACH-42 (S3) — o parecer não chega ao candidato.** O portal **não exibe em nenhuma tela** o parecer
fundamentado da avaliação. Verifiquei `/acompanhamento` e `/inscricoes/<id>/`: a única ocorrência da
palavra "parecer" no HTML é o verbo dentro de um comentário de CSS. O candidato sabe **a nota e a
regra** (`30 < 40`), mas não **a motivação** — que no caso era "o currículo não comprova os 6 meses
de experiência". Ele precisa recorrer adivinhando o fundamento, embora o sistema tenha dito ao
avaliador que o parecer "é o que responderá a um eventual recurso". Lacuna de contraditório.

**Fase I — Recurso.** A interposição é boa: o candidato escolhe **o que** contesta (Classificação
Final ou Análise Curricular), cada opção com seu prazo, e lê "Este texto vai para quem julgar o seu
recurso". → **PP-83**. Protocolado `REC-2026-WCHKBXAM`, com situação "Aguardando análise de
admissibilidade", objeto em linguagem do candidato e **"Dentro do prazo"**. → **PP-84**.

**PP-85** — Para o julgador, a coluna "O QUE POSSO FAZER" da listagem passa a exibir
**"Recursos recebidos (1)"**, com contador: o trabalho é encontrado na primeira tela, sem exploração.
A caixa tem filtro por situação e coluna de **tempestividade**. → **PP-86**.

**ACH-43 (S4) — o julgador não tem acesso ao que julga.** A tela do recurso declara, textualmente:

> *"Para abrir o resultado atacado, a avaliação que o produziu e os documentos da inscrição é preciso
> presidir este Processo, ter a permissão de auditoria ou a de consultar inscrições. **Julgar não as
> concede.**"*

O papel **Julgador de recursos** (`recurso:julgar`) — criado para essa função — **não** dá acesso ao
parecer nem aos documentos. No caso concreto, a razão do recurso era *"o currículo comprova, na
página 2, contrato de tutoria de 8 meses"*: uma alegação **verificável apenas no documento que o
julgador não pode abrir**. Ele decide com um resumo de uma linha (`ELIMINADA · 30,0000`).
É a resposta negativa à pergunta do §19. O contorno — acumular papéis de presidência/auditoria/
consulta — desfaz a segregação que a própria arquitetura tenta preservar.
*(Crédito onde é devido: o sistema **declara** o bloqueio com clareza exemplar. O defeito está no
desenho de autorização, não na comunicação.)*

**ACH-44 (S1)** — Deslize de persona: o objeto atacado aparece como **"o meu resultado da Análise
Curricular"** — texto em primeira pessoa do candidato — na listagem e na tela do julgador.
**ACH-45 (S1/S2)** — Repete-se o vazamento do **ACH-39**: `INTERPOSTO POR:
cand:19421183ce52413fa51515cf3ffba8d1` (em vez do nome, que aparece logo abaixo), `IDENTIDADE DO
OBJETO` e `VERSÃO CONSOLIDADA CITADA` como UUIDs nus.

**Julgamento.** Quatro espécies de decisão, com vocabulário de domínio correto: `Indeferir`,
`Deferir fixando a correção`, `Deferir determinando reavaliação`, `Deferir determinando providência
a jusante`. → **PP-87**. Admissibilidade e mérito são atos separados, cada um com motivo próprio e
autoria registrada. → **PP-88**.
Decidido: deferido com correção fixada em 88 pontos. **E aqui o ACH-43 deixa de ser hipótese**: fixei
uma pontuação sem nunca ter podido abrir o currículo que a fundamenta.

**PP-89 — a relação causal decisão → resultado é explícita:**
`RESULTADO ATACADO: ELIMINADA · 30,0000` → `SUCESSOR: HABILITADA · 88,0000` →
`MOTIVO DA SUPERAÇÃO: Resultado corrigido em cumprimento da decisão no recurso REC-2026-WCHKBXAM`.
A pergunta do §19 é respondida afirmativamente.

**PP-90 — o melhor artefato do sistema.** Ao voltar ao marco, sem nenhuma ação minha:

> **"O ato vigente está obsoleto"** — "A norma ou o universo atual produzem uma proposta diferente.
> **O ato continua vigente e produzindo efeito até que um sucessor seja emitido.**"
> "Os Resultados oficiais do universo mudaram: **resultado superado por recurso**."

com um **diff de classificação posição a posição**:

| INSCRIÇÃO | NO ATO | PONT. NO ATO | AGORA | PONT. AGORA |
|---|---|---|---|---|
| Carlos | 3º | 78 | **4º** | 78 |
| Ana Clara | 2º | 85 | **3º** | 85 |
| João Pedro | Sem posição (30 < 40) | — | **2º** | 88 |

Detecta a obsolescência, nomeia a causa, preserva o efeito do ato vigente e mostra o delta **antes**
de emitir. Nova ordem emitida com motivo; histórico registra "sucede o ato de 15:19".

**PP-91** — Emitida a nova ordem, o sistema avisa que **a publicação ficou para trás**:
*"A divulgação pública ficou para trás. O que está público é resultado preliminar, de 16/09/2026
15:22, e corresponde a uma ordem anterior."* Detecta a defasagem entre ato vigente e o que o público
lê — exatamente o §18.

**PP-92 — bloqueio de domínio correto na Fase J.** Ao tentar publicar como **definitivo**:
*"Este marco ainda não pode ser publicado como definitivo. **O prazo recursal deste marco ainda está
aberto: ele se encerra em 18/09/2026 às 23h59.** Aguarde o encerramento, ou publique como resultado
preliminar."* Regra correta, data exata, duas saídas.
→ **Fase J fica `BLOQUEADA` por regra legítima**: alterar o relógio é proibido pelo protocolo desta
auditoria. Publiquei então uma **segunda divulgação preliminar**, sucedendo a primeira.

**PP-93** — Histórico de divulgações com `Vigente` / `Sucedida`, ambas consultáveis, e a página
pública antiga, **no mesmo endereço estável**, passa a dizer: *"Este resultado foi sucedido. Ele
permanece consultável como registro do que foi divulgado em 16/09/2026, e não é mais o que vale.
Ver o resultado vigente"*. Link permanente que não mente.

### Cenário 1 — Fase K (Ocupação e convocação) — **BLOQUEADA**

**PP-94** — "Abrir esta tela não apura nada. Os números abaixo vêm de atos já emitidos, e onde não há
ato não há número." O princípio "ler não produz efeito" é consistente em todo o produto.
Apuração emitida: `Publicadas 3 · Efetivas 3 · Ocupadas 0 · A ocupar 3`.

**ACH-46 (S3) — beco na convocação, com mensagem não acionável.** Ao clicar em "Pedir a faixa
seguinte com este déficit":

> *"Não foi possível apurar: **Não há geração vigente neste recorte: emita o corte antes de
> continuá-lo.**"*

Três problemas somados:
1. **Vocabulário inteiramente interno** — "geração", "recorte", "corte", "continuá-lo" numa só frase;
   nenhum desses termos é definido em qualquer tela percorrida.
2. **Instrução não acionável** — meu marco foi declarado **"este marco não corta"**, que é a
   configuração natural de um Edital de 3 vagas com uma única Etapa e sem fase seguinte. A mensagem
   manda emitir algo que o Edital não prevê.
3. **Sem caminho** — varri todos os links de `main` na tela do Edital: não existe nenhuma rota de
   "corte", "faixa" ou "convocação" acessível. O único caminho oferecido é o botão que falha.

Consequência: **a Fase K não é executável pela interface** para este Edital. A convocação —
e portanto a suplência — fica inalcançável sem Retificar o Edital para declarar uma regra de corte
artificial.
*(Observação: a escolha que eu havia deixado deliberadamente aberta — `Como a convocação é
comunicada = Não declarado` — **nunca chegou a se manifestar**, porque o fluxo trava antes. O aviso
da composição ("Sem esta declaração o sistema recusa convocar") estava correto, mas o bloqueio que
aparece é outro.)*

---

## Fase 2 — confirmação técnica

> Consultei código e specs **somente depois** de registrar a observação pela interface, e apenas
> para distinguir bug de regra de negócio. Três dos quatro pontos mudaram de diagnóstico — registro
> as correções.

### (a) ACH-46 — convocação bloqueada: **confirmado, e a causa é de interface**

- `classificacao/application/emissao_do_corte.py:162` — a mensagem vem de `continuar_corte`, que é a
  emissão da **faixa seguinte** e exige `geracao_vigente`. Regra legítima.
- `interface/templates/interface/detalhe.html:146` — o link para a tela de corte só é renderizado
  **`{% if marco.cutRule %}`**. Meu marco declarou "este marco não corta", então a tela existe
  (rota `interface:corte`) mas **nunca aparece**.
- `convocacao/application/convocar.py:8` — *"Ela lê a faixa que o corte vigente…"*: a convocação
  depende da faixa, que depende do corte.

**Cadeia:** sem `cutRule` → sem tela de corte → sem geração → sem faixa → **sem convocação**.
O defeito não é a regra; é a tela de ocupação **oferecer "Pedir a faixa seguinte"** num recorte onde
isso é impossível, e responder com uma instrução que aponta para uma tela que a interface não expõe.
Agrava-se porque a ajuda da etapa 5 declara outra consequência para a ausência de corte —
*"sem ele, o marco não corta e a Etapa seguinte recebe todos os habilitados"* — e **silencia** a que
de fato importa: **sem regra de corte não há convocação**. Consequência invisível no ponto da
decisão (§12). **Mantido S3, confiança alta.**

### (b) ACH-43 — julgador sem acesso: **é regra deliberada, não bug — diagnóstico reclassificado**

`specs/018-recursos-e-superacao-de-resultados/spec.md`:
- **FR-102**: "A fundamentação do recurso e a motivação da decisão MUST ser acessíveis ao titular,
  **à autoridade julgadora** e à auditoria autorizada, e a mais ninguém."
- **FR-105**: "Respostas com Resultado individual, fundamentação ou decisão MUST NOT … **ampliar o
  acesso a documentos do candidato**."

A restrição é **proteção de dados escrita como requisito**. Portanto **não é defeito de
implementação**, e retiro a leitura de "falha de autorização".
O que permanece é um problema de **modelo de fluxo**: o produto protege o documento restringindo o
julgador, mas **não oferece nenhum ato de instrução do recurso** — não há como a presidência juntar
ao processo, para aquele julgador e aquele recurso, o extrato da avaliação e a peça contestada. O
resultado prático é o dilema observado: ou o julgador acumula papéis (desfazendo a proteção que a
FR-105 quer), ou decide sem ver a prova. **Reclassificado de S4 para S3**, como lacuna de fluxo.

### (c) ACH-42 — parecer não chega ao candidato: **tensão real com a própria spec**

`specs/012-mesa-de-avaliacao/spec.md:369` justifica a obrigatoriedade do parecer assim:
> "o desfavorável é justamente o caso em que **o candidato mais precisará da fundamentação para
> recorrer**, e é contra o parecer que o recurso responderá."

A intenção declarada é que a fundamentação sirva ao candidato — e no portal ela **não aparece**.
Não achei requisito que a exponha ao titular. **Mantido S3**, agora com a observação de que o
produto **contraria a razão que ele próprio registrou** para exigir o parecer.

### (d) ACH-40 — publicação do resultado: **eu estava errado; achado corrigido**

`interface/views.py:5594` (`_edital_para_publicar`) exige **apenas** `resultado:publicar`, e o
comentário é explícito: *"Sem a capacidade é 403, e não 404, inclusive para quem preside a
comissão"*. O 404 que eu havia atribuído à publicação vinha de outra view — `ato_de_ordenacao`
(linha 5545), que usa `_edital_para_classificar` (presidência ou auditoria).

**Reteste decisivo:** entrei como `diego.publicador` (Publicador puro, sem comissão) e abri
`/marcos/<id>/atos/<id>/publicar` diretamente → **a tela abre normalmente**.

**Portanto: divulgar resultado NÃO exige vínculo de comissão.** O achado se reformula, e continua
válido: **quem tem `resultado:publicar` não tem nenhum caminho de navegação até a ação**.
- A tela do Edital não exibe o bloco "Classificação" para esse ator.
- O único caminho que o sistema indica — *"sai de Consultar ato e proveniência"* — é uma tela que
  ele **não pode abrir** (404).
A permissão existe, a tela funciona, e a navegação não conecta as duas. **Causa: encontrabilidade,
não autorização. Mantido S3** (o fluxo é inexecutável na prática justamente na configuração de
papéis segregada que o produto propõe).

---

## Fase 3 — regressão contra a auditoria de 13/09/2026

> Li `doc/auditoria-exploratoria-ux-2026-09-13.md` **somente aqui**, depois de fechada a exploração
> independente. Retestei o Top 10 pelo navegador, com o ator correto.

**Reteste do achado 4 (segundo Edital):** a tela do Processo agora traz **"Novo Edital neste
Processo"** → `/gestao/processos/<id>/editais/criar`, com formulário sem os campos do Processo.
Criei o **Edital 02/2026** no mesmo Processo pela interface. **RESOLVIDO.**

**Reteste do achado 3 (microcópia invisível) — atenção ao diagnóstico.** Inspecionei o DOM da etapa
2 do Edital 02/2026: **as dicas continuam `.oculto`**, com `offsetWidth` de 0–1px, incluindo
exatamente as que a auditoria anterior nomeou:

| texto ainda `.oculto` | largura |
|---|---|
| "O que a pessoa fará. Uma linha em branco separa parágrafos…" | 1px |
| "Um requisito por linha." | 1px |
| "Quantas pessoas o cadastro comporta…" | 0px |
| "A declarada não recebe linha no quadro…" | 1px |
| "Declarar a reversão exige quadro de vagas publicado…" | 1px |
| **"Sem esta declaração o sistema recusa convocar…"** | 1px |

**Mas o texto deixou de ser inacessível a quem enxerga**: as mesmas frases passaram a compor o
disclosure visível **"Como preencher estes campos"**, no topo da etapa — foi lá que as li na Fase 1,
sem saber que eram as mesmas. A correção adotada **moveu a explicação para um bloco coletivo** em vez
de renderizá-la junto ao campo.
→ **PARCIALMENTE RESOLVIDO**, e a escolha é deliberada (há decisão registrada do usuário de que
ajuda visível não vai para os cartões). O custo que sobra é o do **ACH-04**: a explicação está longe
do campo que explica, e aparece antes de existir qualquer cartão na tela. Não recomendo desfazer a
decisão; recomendo aproximar sem violá-la.

**Reteste dos demais itens do Top 10 anterior** (detalhamento e evidências na seção 5 do relatório
`doc/auditoria-exploratoria-ux-2026-09-16.md`):

| # | Achado anterior | Estado |
|---|---|---|
| 1 | Vagas publicadas ≠ linha do quadro (S4) | **RESOLVIDO** |
| 2 | Reaproveitamento publica cronograma vencido (S3) | **PARCIALMENTE RESOLVIDO** / reaproveitamento **NÃO RETESTADO** |
| 3 | Microcópia invisível (S3) | **PARCIALMENTE RESOLVIDO** |
| 4 | Sem segundo Edital no Processo (S3) | **RESOLVIDO** |
| 5 | Julgador sem porta nem contexto (S3) | **PARCIALMENTE RESOLVIDO** |
| 6 | 30 decisões na Classificação (S3) | **PARCIALMENTE RESOLVIDO** |
| 7 | Retificação em JSON Pointer e UTC (S3) | **PARCIALMENTE RESOLVIDO** |
| 8 | "Impedimento" com dois sentidos (S3) | **RESOLVIDO** (nomenclatura) / contadores **PERSISTENTE** |
| 9 | Atos operacionais em um clique (S2/S3) | **RESOLVIDO** |
| 10 | Bloqueios corretos que chegam tarde (S2) | **RESOLVIDO** em 2 de 3 ocorrências |

Nenhuma **regressão** identificada: não encontrei comportamento pior que o documentado em 13/09.

---

## Encerramento

- Fim da execução: 2026-09-16, ~15:40 (-03).
- Artefatos: este diário e `doc/auditoria-exploratoria-ux-2026-09-16.md`.
- Nada foi apagado: nenhuma Publicação, Retificação, resultado ou registro de auditoria foi removido.
- Working tree: alterado apenas em `.claude/launch.json` (entrada de preview), revertido ao fim.

---

# Sessão 2 — Cenários 3 e 4 (2026-09-16, 16:00–17:00 -03)

Mesmo commit `5f37eec`, mesmo banco `ps_reaudit_20260916`, servidor reaberto na porta 8040.

## Cenário 4 — Modalidades, reservas e regras diferenciadas — **EXECUTADO**

**Montagem (pela interface):** Edital **02/2026** no mesmo Processo `PS 01/2026`.
Perfil `PROF-MAT` "Professor Formador de Matemática", **10 vagas imediatas**, três Modalidades de
Concorrência — `AC` Ampla Concorrência, `PCD` Pessoas com Deficiência (5%, Lei 13.146/2015 art. 34),
`PPP` Pessoas Negras (pretas e pardas) (20%, Lei 12.990/2014 art. 1º) —, quadro repartindo
**7 / 1 / 2**, 3 documentos (um geral, um só de PcD, um só de PPP), 1 Etapa pontuada, e — desta vez —
**regra de corte declarada** (`FROM_VACANCY_TABLE`), para poder testar a convocação.

### O que está muito bem resolvido

**PP-95 — os AVISOS pedidos pela auditoria anterior existem, com a redação proposta.** Ao salvar o
Perfil com modalidades e quadro incompleto:
> *"O Perfil 'PROF-MAT' declara 3 Modalidade(s) e não declara qual delas é a da ampla concorrência.
> Enquanto não declarar, todas contam como lista reservada e o quadro precisa de linha para cada
> uma."*
> *"O Perfil 'PROF-MAT' publica 10 vaga(s) imediata(s) e reparte 10 no quadro. Sem linha no quadro:
> … — **a ocupação e a convocação não terão quantidade a apurar nesse(s) recorte(s)**."*

**PP-96 — a armadilha das duas grafias é administrada.** Enquanto AC não é declarada como a ampla
concorrência, o quadro exibe **duas linhas** chamadas "Ampla concorrência" (a linha geral e a
modalidade AC). O texto desambigua ("Esta é a linha da ampla concorrência: o recorte de que todos os
inscritos participam"), e **ao declarar AC a linha duplicada desaparece sozinha** e o aviso se
reajusta. O modelo e a UI acompanham.

**PP-97 — validação aritmética do quadro.** Com 7+1+5 contra 10 vagas:
`IMPEDE O quadro de vagas do Perfil 'PROF-MAT' soma 13 e o Perfil declara 10 vagas imediatas —
excesso de 3.`

**PP-98 — conferência contra o percentual normativo, sem impor.**
> *"A linha da modalidade 'PPP' declara 5 vaga(s), e o percentual publicado na Regra Normativa (20%)
> sobre 10 vagas daria 2. **A quantidade declarada é a que vale.**"*
Confere a conta e respeita a quantidade publicada — correto, porque arredondamento de reserva varia.

**PP-99 — a modalidade governa os documentos, e isso é dito antes.** Na inscrição:
> *"Escolha como você concorre nesta vaga. **A escolha decide quais documentos serão pedidos a você.**"*
Escolhida PcD: *"Escolha guardada. **A lista de documentos foi atualizada**"*, contador de 1→2 e o
**Laudo médico** aparece.

**PP-100 — troca de modalidade com perda anunciada e nomeada.** Ao mudar de PcD para AC com o laudo
já enviado, o sistema **interrompe** com tela dedicada:
> **"Mudar de modalidade descarta documentos"** — "Estes documentos deixam de ser exigidos na
> modalidade escolhida e serão removidos: **Laudo médico — laudo-bianca.pdf**"
> [Confirmar e descartar] [Voltar sem mudar]
"Voltar sem mudar" preservou tudo (verificado: modalidade PcD, laudo intacto, 2 de 2).

**PP-101** — A concorrência consta do **comprovante** e da revisão; a tela do **avaliador** mostra
"Professor Formador de Matemática — **Ampla Concorrência**"; a **Ocupação** enumera os três recortes,
cada um com sua quantidade publicada e sua própria ação.

**PP-102 — o Edital publicado está correto.** Verificado no PDF: Tabela 1 (Quadro de vagas) com
`Ampla concorrência 7`, `Pessoas com Deficiência (PCD) 1`, `Pessoas Negras (pretas e pardas) (PPP) 2`;
Tabela 2 (Modalidades) com percentual e fundamento; e a seção de documentos **agrupada por
modalidade** ("Dos candidatos concorrentes na modalidade Pessoas Negras (pretas e pardas):").

> **Falso positivo que eu quase reportei — registrado por honestidade.** Minha primeira extração do
> PDF indicou que os rótulos de PCD e PPP estavam **ausentes** das tabelas, o que eu classifiquei
> como S4. Ao verificar `_texto_pdf` (`publicacoes/infrastructure/pdf.py:355`), o escape de
> parênteses está **correto** (`(` → `\(`). O defeito era do **meu regex**, que parava no `)`
> escapado. Refeita a extração respeitando o escape, os três rótulos aparecem. **Não há defeito.**

### ACH-47 (S4) — o sistema aceita, publica e não consegue executar a reserva de vagas

**Evidência [UI].** Com o quadro 7/1/2 publicado, 4 inscrições (1 AC+1 AC, 1 PcD, 1 PPP) avaliadas e
consolidadas:

1. **Classificação** produziu **uma ordem única**, com a modalidade apenas como coluna:
   `1º Diana (AC) 90 · 2º Caio (PPP) 85 · 3º Elias (AC) 70 · 4º Bianca (PcD) 60`.
   A tela **ignora `?lista=`** — testei: devolve os mesmos 4 participantes.
2. **Corte** do recorte geral: "Alvo apurado **7** — lido da linha do quadro de vagas deste recorte".
   Mas `corte?lista=<PCD>` responde: **"Este recorte não tem ordem emitida: não há o que cortar."**
   E a tela de corte **não oferece navegação** entre recortes (nenhum link, nenhum seletor).
3. **Ocupação** exibe os três recortes e um botão **"Apurar a ocupação deste recorte"** em cada um —
   mas o de PcD falha: **"Não foi possível apurar: Este recorte não tem ordem vigente: não há
   ocupação a apurar."**

**Causa confirmada [CÓDIGO]** — `classificacao/application/emissao.py:58-63`:
> *"um marco de cotas tem uma raiz por lista de concorrência … Um ato computado é **sempre** o de
> ampla concorrência — **só o sorteio emite por lista** —, e é isso que a coluna nula afirma."*
> `lista_id=None`

É **decisão de escopo deliberada**: ordem por lista existe apenas no **sorteio** (spec 021, D-006);
a classificação **por pontuação** (015) emite só para a ampla concorrência.

**Por que continua sendo S4.** A interface não comunica isso em ponto algum do caminho. Ela deixa
declarar as modalidades, **valida a soma do quadro**, **publica a reserva no Edital** (ato normativo,
com fundamento legal), **recebe e identifica** inscrições por modalidade, e só no fim oferece três
botões idênticos e igualmente habilitados, dois dos quais **sempre falham** — com uma mensagem que
nomeia o sintoma ("não tem ordem vigente") e não a causa ("ordem por lista só existe em marco de
sorteio").

O resultado prático: **um Edital pontuado com reserva de vagas publica cotas que o sistema não tem
como apurar nem convocar**. As vagas reservadas ficam sem via de ocupação, e nada avisou o operador
enquanto ainda era possível corrigir (antes da publicação).

Mesmo padrão de forma do **ACH-46**: ação oferecida onde é impossível, e mensagem que não diz o que
fazer.


## Cenário 3 — Sorteio — **PARCIALMENTE EXECUTADO**

**Montagem:** Edital **03/2026** no mesmo Processo, Perfil `EXT-GE` "Curso de Extensão em Gestão
Escolar", 5 vagas, **zero Etapas de avaliação** (sorteio puro, como a própria ajuda descreve), 2
Eventos (inscrições + sessão pública de sorteio), e marco `SORT-EXT` "Sorteio Público" com o bloco
do método preenchido por inteiro.

### O bloco do método do sorteio é conceitualmente completo

Cobre todo o §17: **Algoritmo e versão**, **Fonte pública externa da semente**, **Ocorrência que
fixará a semente**, **Quando a ocorrência acontece**, **Como a ocorrência decorre da data
programada**, **Regra de normalização** (+ como será publicada), **Regra de substituição**
(+ como será publicada) e **Etapa que habilita a participar do sorteio**. → **PP-103**.
A ajuda é precisa e nomeia o custo: *"Declarado aqui, o método é **conteúdo publicado do Edital**:
alterá-lo depois exige Retificação, e nunca implantação de software."* → **PP-104**.

### ACH-48 (S3) — a validação proíbe exatamente o sorteio que a ajuda descreve

Ao salvar um marco de sorteio num Edital **sem Etapas**, o sistema recusa:

> *"Um marco classificatório deve enumerar ao menos uma Etapa: sem Etapa não há pontuação a
> combinar, e a ordem não sai."*

Mas a ajuda **da mesma tela** diz o oposto:

> *"Na prática, o sorteio costuma vir antes da análise documental: quando é o caso, **não há Etapa
> que habilite a participar, e entram todas as inscrições submetidas do recorte**."*

E o campo "Etapa que habilita a participar do sorteio" oferece, como única opção,
**"Nenhuma — entram todas as inscrições submetidas"**.

A interface **descreve, oferece e documenta** o sorteio sem Etapas, e a validação o **proíbe**. Para
compor um sorteio puro — o caso que a própria ajuda chama de mais comum — é preciso inventar uma
Etapa de avaliação fictícia só para satisfazer a regra.
*(Crédito: a mensagem de recusa é clara, preserva o que foi digitado ("O que você digitou foi
preservado abaixo") e a tela ainda explica "Nenhuma Etapa foi publicada como classificatória". O
defeito é a **contradição entre a regra e a ajuda**, não a comunicação.)*

> **Segundo falso positivo meu, registrado.** Minha primeira leitura da tela captou apenas
> `"Não foi possível salvar:"` e eu anotei "mensagem de erro vazia". Errado: o motivo está numa
> `<ol>` logo abaixo, que meu extrator de texto não pegou. **A mensagem é boa.**

### ACH-49 (S4) — publiquei um Edital cujo Perfil não tem marco algum, e nada avisou

Sequência real desta auditoria:
1. Preenchi o marco de sorteio do Edital 03/2026 e cliquei "Avançar". O **salvamento falhou**
   (ACH-48) e a página permaneceu na etapa 5 — que é o comportamento correto.
2. **Eu não percebi**, porque os campos continuavam preenchidos na tela ("O que você digitou foi
   preservado abaixo") e o passo seguinte da composição estava acessível.
3. Compus o resto, e a **Revisão não acusou nada**: `IMPEDE: []`, `AVISO` apenas sobre a data do
   Evento.
4. **Submeti, homologuei e publiquei.** Verificado no snapshot canônico:
   `classificationMilestones` = `[]`. No relacional, só existem `CLASS-TUT` e `CLASS-MAT`.
5. O **PDF publicado não tem a seção "Marcos classificatórios"** nem qualquer menção ao algoritmo,
   à Loteria Federal ou à semente — só o título, a descrição e o Evento do cronograma.

Resultado: **o Edital 03/2026 está publicado, é imutável, anuncia-se como "Sorteio público" e não
contém regra classificatória alguma.** Ninguém pode ser classificado por ele, e a correção exige
Retificação.

A tela de composição **afirma** a regra em prosa — *"Um Perfil sem marco não classifica"* — e a
**validação de publicabilidade não a aplica**: não há `IMPEDE` nem `AVISO` para Perfil sem marco,
embora existam `IMPEDE` para "ao menos um Perfil" e "ao menos um Evento".

É a mesma classe do achado nº 1 da auditoria anterior (S4, "o Edital publica um número de vagas que
o sistema não consegue usar"), agora no marco: **o Edital publica uma seleção que o sistema não tem
como executar**, e a validação silencia.

### Execução do sorteio — Edital 04/2026 (contorno declarado)

Para chegar ao sorteio foi preciso **contornar o ACH-48**: criei uma Etapa artificial
("Confirmação de inscrição", classificatória, peso 1, máxima 1) só para satisfazer a exigência de
"enumerar ao menos uma Etapa". É o que um operador real faria, e o registro disso é parte do achado.

Duas recusas no caminho, **ambas bem redigidas**:
- *"Um marco classificatório deve enumerar ao menos uma Etapa…"* (ACH-48)
- *"O instante da ocorrência deve declarar o fuso: sem ele, o mesmo texto designaria momentos
  diferentes conforme quem lê, e a fronteira entre 'ainda não' e 'não haverá' mudaria de lugar."*
  → **PP-105**: disciplina anti-UTC aplicada ao dado normativo, com o porquê.

> **Terceiro falso positivo meu.** Anotei "campo de instante sem exemplo de formato". Errado: o campo
> **tem placeholder** — `2026-11-20T20:00:00-03:00`. Minha automação escreveu por cima do valor e o
> placeholder nunca apareceu. Registro como limitação do meu método: **preencher por script contorna
> as affordances visuais** e gera falso positivo. Os três falsos positivos desta sessão têm essa
> mesma origem.

### ACH-50 (S4) — o Edital publica o método de classificação **errado** e omite a regra do sorteio

Marco `SORT-X` "Sorteio Público" salvo, com algoritmo, fonte, ocorrência, derivação, normalização e
substituição todos declarados. Edital 04/2026 publicado. O que o **documento normativo** imprime na
seção "Marcos classificatórios":

```
SORT-X  Sorteio Público
Combinação:      soma ponderada da Etapa Confirmação de inscrição (peso 1)
Normalização:    nenhuma
Arredondamento:  sem casas decimais, truncamento
```

Duas falhas somadas:
1. **Omissão integral da regra do sorteio.** Varri as 100+ strings do PDF: não há
   `IFES-SORTEIO-SHA256-v1`, nem `Loteria Federal`, nem "semente", nem a regra de normalização, nem
   a de substituição, nem a ocorrência. **Nada do que torna um sorteio auditável é publicado.**
2. **Afirmação falsa.** O Edital declara que a ordem sai de *"soma ponderada da Etapa Confirmação de
   inscrição (peso 1)"* — quando ela sairá de **sorteio**. O documento descreve um método que não é
   o que será aplicado.

Isso contradiz frontalmente a ajuda da própria tela:
> *"Declarado aqui, o método é **conteúdo publicado do Edital**: alterá-lo depois exige Retificação,
> e nunca implantação de software."*

O método é tratado como conteúdo normativo **internamente** (está no snapshot, exige Retificação),
mas **não chega ao documento que o candidato lê**. Sem algoritmo e sem fonte da semente publicados,
a verificação pública do sorteio não tem base normativa — e o §17 ("como explicar o resultado a
terceiros") fica sem resposta.

### A tela de execução do sorteio é excelente — e responde quase todo o §17

`/gestao/editais/<id>/marcos/<id>/sorteio`. O link do marco **roteia pelo tipo**: marco de sorteio
não abre a tela de ordenação. → **PP-106**.

- **"Método declarado no Edital"** exibe, por extenso: Algoritmo `IFES-SORTEIO-SHA256-v1`, Fonte da
  semente `Loteria Federal`, Ocorrência, Derivação, Normalização, **"Se a ocorrência faltar"** — e um
  **"Resumo do método"** com hash SHA-256 (`a8371bcc…`). → **PP-107**.
- **Separação entre norma e execução, explícita:** *"Este método é conteúdo publicado do Edital.
  Alterá-lo é uma Retificação, e não uma decisão desta tela: quem elabora Retificações é quem pode
  alterá-lo."* → **PP-108**.
- **A ordem correta declarada no subtítulo:** *"o universo é comprometido antes de a semente
  existir"* — congelar a população antes de conhecer a semente é a garantia central de um sorteio
  auditável, e está dita em sete palavras. → **PP-109**.
- **Recusa por princípio, quando a fonte falha:** *"A ocorrência declarada e todas as substitutas
  previstas pela regra publicada estão indisponíveis. **Prosseguir exige Retificação que declare
  outro método: o sistema não escolhe fonte por conta própria, e continuar tentando seria
  escolher.**"* → **PP-110**. É o melhor exemplo do princípio "o sistema não decide por você".
- **Recortes:** "Todos os inscritos do recorte de vaga (sem lista de concorrência)" — confirma pela
  interface o que o código dizia: **o sorteio é emitido por lista**, ao contrário da classificação
  computada (ACH-47).

**Contraste que agrava o ACH-50:** a tela de gestão mostra o método **inteiro e bem formatado**; o
Edital publicado **não publica nada disso**. A informação existe, está organizada, e simplesmente não
chega ao documento que o candidato lê.

### ACH-51 (S3) — a fonte da semente é texto livre, e o sistema só aceita dois nomes exatos

**Evidência [CÓDIGO]** — `sorteios/infrastructure/fontes/__init__.py:83-92`:
```python
FONTES = {
    "Loteria Federal": …,
    "Fonte de demonstração": …,
}
```
e `fonte_declarada()` levanta `draw_source_not_supported` para qualquer outro nome.

**Evidência [UI]** — na composição (etapa 5), "Fonte pública externa da semente" é **campo de texto
livre**: sem lista, sem sugestão, sem validação no preenchimento. Na **Retificação**, o mesmo campo é
um **select** com exatamente as duas opções.

A lista fechada existe e é conhecida pelo sistema — ela só **não é oferecida onde o valor é criado**.
Qualquer variação ("Loteria Federal da Caixa", "loteria federal") produz um Edital **publicado e
imutável** cuja fonte o sistema não consegue executar, e a descoberta acontece **no dia do sorteio**,
quando a correção já custa Retificação. No meu caso funcionou por acaso: digitei o nome exato.

Mesmo padrão do ACH-46 e do ACH-47: um valor crítico é criado **sem** as restrições que o sistema
aplicará depois.

### Estado final do Cenário 3 — **PARCIALMENTE EXECUTADO / BLOQUEADO**

Executado: composição do método, publicação, roteamento por tipo de marco, leitura da tela de
sorteio, recusa por fonte indisponível.
**Não executado:** congelamento do universo, obtenção da semente, execução, ordem sorteada, manifesto,
verificação pública, transformação em classificação, suplência.
**Motivos — ambos legítimos, nenhum contornado:**
1. **Sem população**: o prazo de inscrições que eu mesmo declarei (16:45) venceu antes de eu inscrever
   candidatos; a oferta passou a "CONSULTA".
2. **Fonte externa indisponível**: a Loteria Federal não é alcançável neste ambiente, e o sistema
   **recusa escolher outra fonte** — corretamente. O projeto mantém o E2E contra o serviço real atrás
   da chave `SORTEIO_E2E_FONTE_REAL`, desligada por padrão.

Executar o sorteio de ponta a ponta exigiria declarar **"Fonte de demonstração"** no Edital — o que eu
só descobri **lendo o código**, e é exatamente o **ACH-51**.


---

## Encerramento da sessão 2

- Fim: 2026-09-16, ~17:00 (-03).
- Editais criados nesta sessão, todos pela interface: **02/2026** (modalidades, publicado + 1
  Retificação), **03/2026** (sorteio sem marco — publicado assim, ver ACH-49), **04/2026** (sorteio
  com marco, publicado).
- Inscrições criadas: `bianca`, `caio`, `diana`, `elias` (dados fictícios; CPFs de teste válidos).
- Nada apagado: nenhuma Publicação, Retificação, resultado ou registro de auditoria foi removido.
- Working tree: apenas `.claude/launch.json` alterado durante a execução, revertido ao fim.
- Banco `ps_reaudit_20260916` preservado para reprodução.

### Balanço de honestidade desta sessão

Três **falsos positivos** meus foram descartados antes de virarem achado — todos com a mesma causa:
preencher formulários por script contorna as affordances visuais do produto (placeholder, mensagem
em lista, escape de PDF). Estão registrados no relatório, na seção 17. A diferença entre um S4 real e
um artefato de ferramenta é precisamente o que esta auditoria precisa acertar, e por isso cada um foi
verificado no código antes de ser aceito ou descartado.

---

# Sessão 3 — Cenários 5 e 6 (2026-09-16, 18:00–19:00 -03)

Mesmo commit `5f37eec`, mesmo banco. Famílias escolhidas **a partir da amostra real** em `~/Downloads`
(101 PDFs), conforme o protocolo manda para o cenário 6.

## Cenário 5 — Curso/formação — **EXECUTADO**

**Referências reais usadas:** `EDITAL UNIFICADO Nº 57/2026 — CURSOS DE APERFEIÇOAMENTO DO CEFOR`
(dois cursos, 80 vagas cada, AC 56 / PcD 4 / PPI 20, sorteio eletrônico) e
`EDITAL Nº 78/2026 — VAGAS REMANESCENTES … LIBRAS INICIANTE A1` (duas turmas, 21 e 40 vagas).

**Montado no sistema:** Edital `78/2026`, duas turmas como **dois Perfis** (`TURMA-1` 21 vagas,
`TURMA-2` 40 vagas), três modalidades por turma (AC/PcD/PPI) com fundamento normativo, quadros
`15+1+5=21` e `28+2+10=40`, reversão "a quantidade que ficou sem preencher", dois **marcos de
sorteio**, 1 documento, 2 inscrições (Elias/AC e Bianca/PcD). Publicado.

### ACH-52 (S2) — "Perfil de Vaga" é do domínio, mas o que varia é a **turma**

**Evidência documental.** O Edital 78/2026 usa literalmente a expressão no quadro:

```
Código de vaga | Perfil da Vaga   | Quantidade | Dias e horários das aulas
Turma 1        | Público externo  | 21         | Segundas e quintas, 09h às 11h
Turma 2        | Público externo  | 40         | Segundas e quintas, 13h às 15h
```

O termo **"Perfil da Vaga" existe no domínio** — não é invenção do produto, e isso responde
positivamente à primeira pergunta do cenário. **Mas**, no Edital real, o *perfil* é o **público**
("Público externo"), idêntico nas duas linhas, e o que distingue as ofertas é a **turma** (horário).

No sistema, o Perfil de Vaga é a unidade que carrega vagas, quadro e modalidades. Para representar
duas turmas é preciso criar **dois Perfis cujo "perfil" é o mesmo**, e pôr o horário na
**Descrição**, que é texto livre. Verifiquei os campos disponíveis: existem `workload` (carga
horária), `compensation` (remuneração) e `duties` (atribuições) — vocabulário de **vaga de
trabalho** — e **não existem** `turma`, `horário`, `polo` nem `modalidade de ensino`.

Consequências observadas no portal publicado:
- A oferta é apresentada sob o cabeçalho **"Vagas"**, com o botão **"Inscrever-se nesta vaga"** —
  para um curso, "vaga" é aceitável (o próprio Edital fala em "vagas remanescentes"), mas
  "Atribuições" e "Remuneração" ficariam sem sentido se preenchidos.
- A carga horária do **curso** (60h) só caberia no campo de carga horária da **jornada**.

Não é impedimento: o cenário foi executado inteiro. É **artificialidade de modelagem** — o Perfil é
modelado para vaga de trabalho e o curso o reinterpreta.

### ACH-53 (S2) — o portal rotula o Edital com o título do **Processo**

A página pública do Edital 78/2026 (curso de Libras) tem como título
**"Seleção de Tutores a Distância"** — o nome do Processo `PS 01/2026`, ao qual eu anexei todos os
Editais. O objeto real do Edital aparece só na descrição.

A tela de criação **incentiva** reunir Editais num Processo ("o Processo reúne Editais que podem ter
cronogramas próprios"), e o Cefor publica Editais unificados anuais. Quando o Processo reúne objetos
diferentes, o portal os rotula a todos pelo nome do Processo.

### O que a família de curso revelou de bom

- **PP-111** — A opção de reversão **"A quantidade que ficou sem preencher"** corresponde
  literalmente à cláusula 4.3 do Edital 57 ("na hipótese do não preenchimento total das vagas
  destinadas às ações afirmativas, o quantitativo será destinado à respectiva ampla concorrência").
  Correspondência exata com o domínio.
- **PP-112** — Os quadros por turma aceitaram o arredondamento real das cotas (5% de 21 → 1;
  25% de 21 → 5) sem reclamar, e conferiram as somas.
- **PP-113 — o sorteio resolve cotas, e é aqui que a família real vive.** A tela do sorteio da
  Turma 1 apresentou **quatro recortes**, cada um com universo projetado e congelamento próprio:
  `Todos os inscritos (sem lista)` 2 · `AC` 1 · `PcD` 1 · `PPI` 0.
  Isso confirma pela interface o que o código dizia (**ACH-47**): ordem por lista existe **no
  sorteio**, não na classificação pontuada — e a família dominante do Cefor é justamente
  **sorteio + cotas**. Isso **reduz a frequência provável do ACH-47**, sem reduzir sua gravidade.
- **PP-114 — congelamento do universo, completo.** "Relação congelada em 16/09/2026 18:14 por
  paula.presidente, com 2 participantes. **Resumo c738902…** **Ver no canal público**", com o
  **número de cada participante** — exatamente o que o Edital real exige ("Cada candidato receberá um
  número para o sorteio, a ser publicado na respectiva listagem"). Substituir a relação exige
  **motivo escrito**: *"A relação publicada é o compromisso do universo. Substituí-la sem razão
  escrita apagaria o compromisso sem que ninguém respondesse por isso."*

### ACH-54 (S2) — a tela do sorteio oferece congelar um recorte sem vagas

Declarada uma modalidade `AC` **como** a ampla concorrência, sua linha sai do quadro (a quantidade
passa à linha geral). Mas a tela de sorteio continua listando o recorte **"Ampla Concorrência (AC)"**
com seu próprio botão "Publicar e congelar a relação" — um recorte **sem vagas**, cujo sorteio não
serve para nada, e nada na tela o diz.
*(Crédito: a colisão de **nomes** já foi tratada — há comentário em `previa.py:35-42` explicando que
o rótulo do recorte sem lista virou "Todos os inscritos…" exatamente por isso. O que falta é dizer
quantas vagas cada recorte tem.)*

### ACH-55 (S3) — o método do sorteio pede prosa e precisa de dado; o sorteio fica inexecutável

Preenchi `Ocorrência que fixará a semente` e `Como a ocorrência decorre da data programada` em
**prosa** — que é como um Edital se escreve e o que os rótulos pedem — e usei a
**"Fonte de demonstração"**. Resultado na tela do sorteio:

> *"A ocorrência declarada e todas as substitutas previstas pela regra publicada estão indisponíveis.
> Prosseguir exige Retificação que declare outro método…"*

**Causa [CÓDIGO]** — `sorteios/application/previa.py:96-108`: a tela só oferece
"Observar a ocorrência X na fonte" quando `substituicao.proxima_a_observar(metodo, …)` consegue
**derivar** uma referência; quando ela levanta `DomainError`, a tela cai na mensagem acima.
A `FonteDeTeste` (`loteria_federal.py:142-162`) devolve material para **qualquer** referência exceto
a string `"indisponivel"` — ou seja, **não foi a fonte que falhou**: foi a derivação da referência a
partir do que declarei.

Três problemas somados:
1. Os campos são **texto livre em prosa**, mas o sistema precisa deles como **dado computável**.
2. **Nada valida na composição** — o Edital foi submetido, homologado e publicado sem uma palavra.
3. A mensagem **atribui a falha à fonte externa** e prescreve **Retificação**, quando a causa está na
   declaração e a mensagem não diz o que corrigir.

Mesma família do **ACH-51**: valor crítico criado sem as restrições que o sistema aplicará depois.

## Cenário 6 — Outra família: chamada de propostas — **PARCIALMENTE EXECUTADO**

**Família escolhida da amostra real:** `EDITAL Nº 1122/2026 (IFNMG) — CHAMADA PÚBLICA PARA SELEÇÃO DE
EXPERIÊNCIAS EXITOSAS` para a 50ª Reditec. Escolhida por ser a mais distante do eixo "pessoa concorre
a vaga", que os cenários 1 a 5 já cobriram — aqui seleciona-se **proposta**, não pessoa.

**Estrutura real, extraída do Edital:**
- **11 eixos temáticos** (a–k); a proposta é inscrita **em um eixo**.
- **20 propostas** selecionadas, com **quantidade por eixo**; as **5 primeiras de cada eixo** são
  apresentadas nos palcos.
- Submissão feita pela **reitoria da unidade**, não pelo autor.
- Avaliação por **quatro critérios com pontuação máxima própria**: Potencial de aplicabilidade e
  replicação (30), Impactos (30), Aderência ao eixo temático (20), Organização e clareza (20).
- **Ajuste regional (item 6.6.2–6.6.3):** *"Após a classificação geral por pontuação, será verificada
  a distribuição regional das propostas selecionadas. Caso uma ou mais regiões não estejam
  representadas … o ajuste ocorrerá mediante a substituição da(s) proposta(s) selecionada(s) com
  menor pontuação geral pela(s) proposta(s) mais bem classificada(s) da(s) região(ões) ainda não
  contemplada(s)."*
- Desclassificação → convoca a próxima **da respectiva área temática**.

### O que o modelo representa bem

| Elemento do Edital | Mapeamento | Veredito |
|---|---|---|
| Eixo temático com quantidade própria | **Perfil de Vaga** por eixo, com vagas imediatas | **representável** — é o mesmo padrão das turmas (ACH-52) |
| "5 primeiras de cada eixo vão ao palco" | **regra de corte** `FIXED` = 5 por marco do eixo | **representável** |
| Documentos da submissão | Documentos exigidos | **representável** |
| Recurso e resultado | marco com janela recursal | **representável** |
| Prazo, publicação, retificação | idênticos aos demais | **representável** |

### ACH-56 (S2) — não há critérios de avaliação com pontuação própria

**Evidência [UI].** A Etapa de Avaliação declara **uma** `Pontuação máxima` e **uma** `Nota mínima`,
e a mesa do avaliador (cenário 1) oferece **um único campo de pontuação** mais um parecer em texto.
Não há grade de critérios nem subpontuação.

Para representar "Aderência ao eixo: 20 / Impactos: 30 / …", o Edital teria de virar **quatro Etapas
de Avaliação**, cada uma com sua pontuação máxima e peso — o que funciona aritmeticamente (o marco
soma ponderada), mas **distorce o modelo**: "Etapa" no domínio é uma **fase pela qual o candidato
passa** ("As fases pelas quais os candidatos passam, na ordem em que ocorrem"), e aqui as quatro
seriam **dimensões de um mesmo julgamento**, feitas pelo mesmo avaliador, no mesmo ato. O avaliador
teria quatro itens na Mesa para **uma** proposta.

### ACH-57 (S3) — o ajuste regional não é representável, e nem o insumo existe

O ajuste regional **não é** cota, desempate, corte nem suplência: é uma **correção pós-classificação
por representatividade**, que **substitui** um já classificado por outro de região não contemplada.

Verifiquei o insumo: um **"fato exigido do candidato"** aceita apenas dois tipos —
**`Data`** e **`Número inteiro`**. A **região** é um valor **categórico**, e portanto **não pode
sequer ser declarada** como fato. Sem o insumo, não há como escrever a regra nem como o sistema
aplicá-la.

O mais próximo que o modelo oferece é a **reversão de vaga reservada**, que é outra coisa: move
quantidade **não preenchida** de uma lista para a ampla, e não substitui alguém já classificado.

**Veredito honesto:** esta parte do Edital **não é representável**, e a apuração teria de ser feita
fora do sistema e o resultado lançado como ato — o que o produto, corretamente, não oferece.

### ACH-58 (S2) — o inscrito é sempre uma pessoa física

Toda a jornada do portal é construída sobre **pessoa**: identificação por e-mail, `Nome completo` e
**CPF obrigatório**, comprovante nominal, "Minhas inscrições", CPF mascarado na mesa do avaliador.
No Edital 1122, quem submete é a **reitoria da unidade** e o objeto é uma **proposta com título**.

Seria possível operar com o CPF do servidor que submete, mas então: o comprovante nomeia a pessoa e
não a proposta; a lista pública divulga nomes de pessoas e não títulos; e a "inscrição" não tem onde
guardar o título do trabalho — não há campo de texto do candidato além dos documentos anexados.

**Declaração de cobertura:** deste cenário eu **montei e verifiquei** o mapeamento de eixos, critérios
e fatos pela interface, e **não montei** o Edital completo — não havia o que ganhar em publicá-lo,
já que os dois pontos decisivos (critérios com pontuação e ajuste regional) estavam determinados.
Classifico como **PARCIALMENTE EXECUTADO**, com as três afirmações acima verificadas na interface.

### Correção retroativa — ACH-12 (desempate por maior idade) **estava impreciso**

Na primeira sessão registrei que "não há desempate por maior idade — só modelando-o como fato
autodeclarado". Verificado agora: o fato aceita o tipo **`Data`**, então declarar
`data-de-nascimento` e usar o critério **"Menor valor de um fato declarado"** resolve o desempate
etário de forma direta. O mecanismo **existe e é adequado**; permanece apenas a ressalva de que o
valor é **autodeclarado** pelo candidato, e não conferido. **ACH-12 rebaixado para observação.**

---

## Encerramento da sessão 3

- Fim: 2026-09-16, ~19:00 (-03).
- Editais criados: **78/2026** (curso, duas turmas, cotas, dois marcos de sorteio) — publicado.
- Inscrições: Elias (AC) e Bianca (PcD) na Turma 1; relação do recorte geral **congelada**.
- Nada apagado. Working tree: só `.claude/launch.json`, revertido ao fim.

---

# Sessão 4 — Correção do Cenário 6 (2026-09-16, ~19:15 -03)

## Erro reconhecido

Na sessão 3 escolhi, para o cenário 6, o **Edital IFNMG 1122/2026** (chamada de experiências
exitosas para a Reditec). **Escolha errada**, apontada pelo usuário: é de **outra instituição**
(IFNMG, não Ifes/Cefor) e não é processo seletivo de pessoas ou de alunos — é chamada de trabalhos
para um evento. O PDF estava em `~/Downloads`, mas **não integra a amostra do projeto**.

O protocolo pedia "outra família significativamente diferente **presente na amostra real de Editais
do projeto**", e eu não verifiquei se o arquivo pertencia a ela antes de usá-lo.

**Consequência:** os achados `ACH-57` (ajuste regional) e `ACH-58` (inscrito não-pessoa) **são
descartados** — descreviam um Edital fora do contexto. O `ACH-56` (critérios com pontuação própria)
**sobrevive**, e é revalidado abaixo contra um Edital legítimo.

## A amostra real do projeto

`doc/avaliacao-de-capacidade-editais-2026-09-12.md` §"Por Edital — a amostra inteira" cataloga onze
Editais do Cefor/Ifes: **58, 59, 69, 77, 78, 158, 57, 28, 173, 14, 76** — e registra que o
**46/2026 (técnicos integrados) está "fora do alvo por decisão"**.

Cobertura das famílias pelos meus cenários:
- **1** → seleção de pessoal com análise pontuada (família do 173/2025, 146/2025)
- **5** → curso FIC com turmas, cotas e sorteio (família do 58/59/77/78/158/57)
- **6** → precisa ser outra coisa.

Considerei **28/2026** (pós-graduação, 7 polos × 3 modalidades, 280 vagas) e **14/2026**
(Orientador de TFC). Escolhi o **14/2026**: o 28 usa o mesmo mecanismo do cenário 5 (sorteio +
cotas), variando só a estrutura de oferta, enquanto o 14 é **computado**, com **barema**, **duas
etapas** e **grupos em cascata** — nenhum deles tocado pelos cenários anteriores. O próprio
documento do projeto o chamava de "a medida da distância".

## Cenário 6 (refeito) — Orientador de TFC, Edital 14/2026 — **PARCIALMENTE EXECUTADO**

**Estrutura real, extraída do PDF:**
- **Três grupos**, escolhidos pelo candidato no ato da inscrição: Grupo 1 (concursados do Ifes
  lotados no campus ofertante), Grupo 2 (concursados de outros campi), Grupo 3 (externos).
  *"serão publicadas três listas de inscritos, uma para cada grupo"*.
- **Cascata, não cota** (itens 3.1, 6.1, 6.6): convocam-se **prioritariamente** os do Grupo 1 mais
  bem classificados, **até 10 por código de inscrição**; *"caso o número de classificados deste grupo
  seja menor que 10 (dez) candidatos por código de inscrição, serão convocados … Grupo 2 e …
  Grupo 3, conforme classificação na Prova de Títulos"*.
- **Duas etapas**, ambas eliminatórias e/ou classificatórias: **Prova de Títulos** e **Entrevista**.
- **Barema**: `ANEXO IV – FICHA DE AVALIAÇÃO` com *"os títulos, suas pontuações e o limite máximo de
  pontos"*; `ANEXO V` com os critérios da Entrevista e a pontuação de cada um.
- **Autopontuação**: o Anexo IV tem coluna *"EXPECTATIVA DE PONTUAÇÃO PELO CANDIDATO"*.
- **Código de inscrição** como terceira dimensão (o alvo é "10 por código").

**Montado no sistema:** Edital `14/2026`, Perfil `TFC-GESTAO-EPT` com 10 vagas, três grupos como
**Modalidades de Concorrência**, e as duas Etapas com peso 1 e máxima 100.

### ACH-59 (S3) — grupo de prioridade não é modalidade, e o sistema empurra para a resposta errada

Modelar os grupos como modalidades é o mapeamento natural (o candidato **opta** por um, como opta por
uma cota). O sistema então exige repartir as vagas, e avisa:

> *"O Perfil 'TFC-GESTAO-EPT' declara 3 Modalidade(s) e não declara qual delas é a da ampla
> concorrência…"*
> *"…publica 10 vaga(s) imediata(s) e reparte 10 no quadro. Sem linha no quadro: Grupo 1…, Grupo 2…,
> Grupo 3 — **a ocupação e a convocação não terão quantidade a apurar nesse(s) recorte(s)**."*

Mas o Edital **não reparte**: há **10 vagas por código**, e os grupos definem **ordem de chamada**.
As três saídas disponíveis são todas falsas:

| Saída | O que o Edital passaria a afirmar |
|---|---|
| Repartir (ex. 10/0/0) | que os Grupos 2 e 3 **não têm vaga** — falso |
| Deixar as linhas vazias | ocupação e convocação **sem quantidade a apurar** (o próprio aviso) |
| Declarar G1 como ampla concorrência | que G2 e G3 são **reservas com quantidade própria** — falso |

Nenhuma representa *"prioridade em cascata, sem reserva de quantidade"*.
**Honestidade:** esta é **pendência já conhecida e registrada** pelo projeto — a tabela do
`avaliacao-de-capacidade-editais-2026-09-12.md` lista, na coluna "O que falta depois" do 14/2026,
exatamente **"cascata Grupo 1→2→3 (016/019)"**. Não é achado novo; o que acrescento é **como ela se
manifesta na composição**: o operador não recebe um "não dá", recebe **dois avisos que o empurram a
declarar uma repartição que o Edital não tem**.

### ACH-56 revalidado (S2) — barema não é representável

Verificado na interface, no Edital 14/2026: a Etapa de Avaliação expõe exatamente onze campos —
`name, scheduleEventId, forma, minimumScore, maximumScore, rotuloFavoravel, rotuloDesfavoravel,
weight, evaluationsPerRegistration, eliminatory, classificatory` — e **nenhum** de critério, item ou
limite por item. A Mesa do avaliador (cenário 1) oferece **um** campo de nota e um parecer.

O barema do Anexo IV (títulos com pontuação e **limite máximo por item**) e o do Anexo V (critérios
da entrevista) só cabem como **Anexo PDF**: o avaliador lança **a soma**, e o sistema não guarda nem
confere a composição. A **autopontuação do candidato** não tem onde ser declarada.
Também aqui o projeto já registra: **"barema (D-4)"** e, no 173/2025, **"autopontuação (P-7)"**.

### O que o 14/2026 mostrou que o modelo faz bem

- **Duas Etapas com peso**, ambas eliminatórias e classificatórias, combinadas por soma ponderada no
  marco: representável sem violência.
- **Alvo fixo de 10**: a regra de corte `FIXED` cobre exatamente o "10 por código".
- **Código de inscrição**: mapeia para **Perfil**, como turma e eixo — o mesmo padrão do ACH-52.

### Achados descartados por virem do Edital errado

- **ACH-57 (ajuste regional)** — descartado. Era regra do IFNMG.
- **ACH-58 (inscrito não-pessoa)** — descartado. No contexto do Cefor o inscrito **é** pessoa física,
  e o modelo está adequado.
- **Permanece válida** a observação factual que sustentou a correção do **ACH-12**: um *fato exigido
  do candidato* aceita apenas os tipos **`Data`** e **`Número inteiro`** — verificado na interface.

---

# Sessão 5 — Cenário 6 (b): Edital 28/2026, pós-graduação com 7 polos

A pedido do usuário, executei **também** o 28/2026 — a outra família que eu havia considerado e
descartado. Ela acrescenta o que nenhum cenário tocou: **polo** e **escala**.

**Estrutura real:** Pós-Graduação Lato Sensu em Informática na Educação, EaD, 480h, **280 vagas em
7 polos** (Bom Jesus do Norte, Iúna, Montanha, Piúma, Santa Leopoldina, São Mateus, Vargem Alta),
cada polo com **AC 28 / PcD 2 / PPI 10 = 40**. Reversão **por polo** (item 4.3). Concorrência
concomitante (4.3.1). Seleção por **sorteio**. E **verificação da autodeclaração** pela **CLVA do
campus** (videoconferência para pretos e pardos, análise documental para indígenas), com recurso
para a **CPVA institucional** (itens 6.1–6.4).

**Montado e publicado pela interface:** Edital `28/2026`, 7 Perfis (polos) × 3 modalidades = **21
modalidades e 21 linhas de quadro**, 7 marcos de sorteio, 1 Etapa, 1 documento. Submetido,
homologado por `carla.homologadora` e publicado por `diego.publicador`.

### ACH-60 (S3) — a organização do trabalho não conhece o Perfil

Este é o achado central do 28/2026, e ele é verificável em duas telas:

- **Alocação por Etapa**: a matriz tem uma coluna **por Etapa** — "Análise documental dos sorteados
  28/2026", "… 78/2026", "Análise Curricular 01/2026" etc. **Não há recorte por Perfil.** Com 7
  polos e uma Etapa, quem for alocado recebe inscrições **dos sete polos**.
- **Distribuir**: os filtros são **Cobertura** (todas / sem avaliador / sem avaliador suficiente /
  completas / com avaliação pendente) e **Avaliador**. **Não há filtro por Perfil nem por
  modalidade**, e a tabela de inscrições não traz coluna de Perfil (já registrado no cenário 4 para
  modalidade; agora se estende ao Perfil).

Consequência para este Edital: a presidência distribuiria **280 inscrições sem saber, na tela, de
qual polo cada uma é** — e sem poder separar o que cabe à comissão local de cada campus.

**E a CLVA não tem representação.** A Comissão é **única por Processo** (`/processos/<id>/comissao`);
não há comissão por Edital, por Perfil ou por polo. A **CPVA** — instância recursal institucional,
distinta da comissão do certame — também não tem lugar: o julgamento de recurso é papel institucional
único (`recurso:julgar`). *(Pendência já registrada pelo projeto como "heteroidentificação (L-2 +
spec própria)" para os Editais 57, 28 e 173.)*

### ACH-61 (S2) — a escala da composição, medida

| Tela | Medida |
|---|---|
| Etapa 2 (Perfis), 7 polos × 3 modalidades | **18.943 px** de altura, **399 controles**, **14 avisos** simultâneos |
| Etapa 2 depois de preenchida | 17.042 px, 378 controles |
| Etapa 5 (Classificação), 7 marcos de sorteio | 6.238 px, 237 controles |
| Método do sorteio | **98 campos** preenchidos para declarar **7 vezes a mesma regra** |

O método do sorteio é, no Edital real, **um só**: mesmo algoritmo, mesma fonte, mesma ocorrência,
para os sete polos. No sistema ele mora no **marco**, que é **por Perfil** — então é declarado sete
vezes. Além do custo, isso cria um risco de integridade: **sete declarações independentes da mesma
regra**, e qualquer divergência de digitação produziria métodos diferentes no mesmo Edital.

### O que o 28/2026 mostrou que o modelo faz bem

- **PP-115** — Os 7 polos × 3 modalidades foram declarados, validados e publicados **sem um único
  IMPEDE**: os 21 quadros fecham (28+2+10=40 por polo), a reversão por polo é declarável, e os 14
  avisos iniciais desapareceram à medida que declarei a ampla concorrência e as quantidades.
- **PP-116** — O **portal escala bem**: as 7 ofertas cabem em 2.728 px, cada uma com seu polo, sua
  localidade, suas concorrências e suas 40 vagas. A página pública é o oposto da tela de composição.
- **PP-117** — A recusa por estado, quando tentei publicar sem homologar: *"Este ato não cabe na
  situação atual. Ele só é admitido a partir de Homologado, e a situação hoje é Em revisão. **Nada
  foi alterado.**"*

### Confirmações de achados anteriores, agora em terceira ocorrência

- **ACH-53** — a página pública do Edital 28/2026 tem como título **"Seleção de Tutores a
  Distância"**, o nome do Processo. Terceira ocorrência (01, 78 e 28).
- **A repartição não chega ao candidato** — cada oferta exibe "40 vagas imediatas" e a lista de
  concorrências, **sem as quantidades** (28/2/10). O candidato PcD do polo de Iúna não sabe que há
  2 vagas para ele. Quarta ocorrência do mesmo padrão.
- **O total do Edital não é somado** — as 280 vagas só aparecem porque eu as escrevi na descrição.

### Comparação entre as duas famílias do cenário 6

| | **14/2026** Orientador de TFC | **28/2026** Pós-graduação, 7 polos |
|---|---|---|
| Mecanismo | computado, duas Etapas com peso | sorteio por recorte |
| O que o modelo **não** representa | **barema** (ACH-56) e **cascata de grupos** (ACH-59) | **comissão local por polo** (ACH-60) e **heteroidentificação** |
| O que ele representa bem | duas Etapas com peso; alvo fixo `FIXED`; código → Perfil | 21 recortes; reversão por polo; sorteio por lista; portal |
| Custo escondido | — | **escala da composição** (ACH-61) |

As duas famílias caem no mesmo ponto do arco — a **organização do trabalho e a execução**, não a
elaboração. Nenhuma delas falha em publicar; ambas falham em **conduzir**.
