# Decisões pendentes — o que só uma pessoa pode resolver (15/10/2026)

**Entregável F** da [auditoria de consolidação](../auditoria-de-consolidacao-2026-10-15.md). Base:
`main` @ `db428b30`. Cada decisão remete aos itens da [matriz](matriz-pendencias.md) que ela destrava.

Ficaram de fora as dúvidas de implementação que têm resposta convencional: elas estão na matriz com
"Precisa de decisão humana? não". Também ficaram de fora as decisões já tomadas que os documentos
ainda davam como abertas. Quatro casos:

- as perguntas Q1–Q9 da auditoria de UX, decididas na `072` (`specs/072-jornada-publica-do-portal/spec.md:63-73`);
- a Diretoria na Visão Geral (decidida em 21/09: `visao:consultar` no Gestor, sem papel novo);
- a premissa "sistema só local" de 14/10;
- a D-G2, decidida em 28/09 para entrar "junto com a preparação para produção".

**Quem decide.** Algumas decisões são do usuário, como responsável pelo produto. Outras são da
instituição: TI, encarregado de dados, Cefor, setor de correio. Nesse caso, cabe ao usuário levar a
pergunta, e a recomendação é sobre **como** levá-la.

---

## Bloco 0 — A decisão que ordena as outras

### DEC-01 · Quando haverá o primeiro certame real, e com qual Edital

- **Contexto.** O sistema existe só na máquina do responsável. Em 14/10 o usuário corrigiu a premissa
  das sessões: "não há implantação nem candidatos reais". Em 28/09 ele adiou o pedido de produção à
  TI ("não vejo relevância nisso neste momento", RC-124). O Edital mais citado como candidato a piloto é
  o 28/2026, que ordena por sorteio e tem heteroidentificação.
- **Problema.** Os seis P0 da matriz são todos **P0 para a implantação**: autenticação (GO-01),
  retenção (GO-19), TI e hospedagem (GO-22), correio (GO-25), autoridade e assinatura (ED-04) e
  aprovação das frases da `069` (ED-03). Sem data, nenhum deles anda, porque cada um depende de
  terceiros com prazo de semanas. O desenvolvimento local, enquanto isso, continua acumulando
  funcionalidade que ninguém de fora usou: nenhum item da matriz está **validado**.
- **Alternativas.**
  - **A.** Fixar agora uma janela-alvo (por exemplo, um semestre) e o Edital do piloto, e disparar em
    paralelo os pedidos institucionais das DEC-02 a DEC-05.
  - **B.** Seguir sem data, só com desenvolvimento local, até o produto "estar pronto".
  - **C.** Piloto-sombra: conduzir no sistema, em paralelo ao processo atual e sem valor legal, um
    certame real já em curso.
- **Impactos.** A custa só tempo de conversa agora, e transforma P0 latentes em trabalho com prazo. B
  é o caminho de hoje: preserva a liberdade de evoluir, mas adia toda validação e alonga o tempo até o
  primeiro uso. C produz evidência de uso sem depender de LDAP nem de retenção (o seletor de
  identidade basta num ambiente controlado), mas exige um certame real com datas futuras. A decisão
  de 25/09 proíbe carga retroativa.
- **Recomendação: A, com C como passo intermediário.** A lição mais repetida das sessões é que as
  decisões institucionais têm prazo longo e travam no fim. A validação com pessoas, por sua vez
  (DEC-14), não depende de produção e pode começar já.

---

## Bloco 1 — Decisões institucionais (o usuário leva; a instituição decide)

### DEC-02 · Autenticação da gestão: confirmar o provedor com a TI

- **Contexto.** Em 28/08 o usuário respondeu "LDAP" à pergunta sobre o login institucional (resposta
  literal da sessão `0b03a4b5`). A `002` registrou o portão (T056) e nada foi implementado. Sem o
  seletor de demonstração, `/gestao/` responde 503 (`interface/views.py:628-629`), e a API
  administrativa só tem o adaptador de desenvolvimento.
- **Problema.** A resposta de 28/08 foi do usuário, não da TI. O adaptador precisa saber se o
  provedor é LDAP direto, autenticação no proxy (cabeçalho de usuário remoto), SSO ou outro.
  Também precisa saber como os grupos do diretório viram os oito papéis e quem concede os papéis
  (GO-05).
- **Alternativas.**
  - **A.** LDAP direto (bind e grupos).
  - **B.** Autenticação no proxy institucional, com o Django lendo o usuário remoto.
  - **C.** SSO federado (gov.br ou outro).
- **Impactos.** O desenho é o mesmo nas três: a fronteira já está isolada em `interface/identidade.py`
  ("quando o diretório for integrado, só este módulo muda"). Muda o esforço e a dependência da TI.
- **Recomendação.** Levar as três à TI junto com o pedido da DEC-01 e aceitar a que a TI suportar.
  Abrir a spec de autenticação só com a resposta em mãos. Matriz: GO-01 (com AV-01 e ED-05), GO-02,
  GO-03 e GO-05.

### DEC-03 · Pacote único ao encarregado de dados (LGPD)

- **Contexto.** Há validações de LGPD pendentes em cinco specs (`060`, `066`, `070`/`071` e `072`).
  Não existem RIPD, aviso de privacidade nem política de retenção. Em 01/09 o usuário condicionou o
  recebimento de dado real à política de retenção. A chave `AVISOS_AOS_CANDIDATOS` não tem trava em
  `production.py`: basta uma variável para ligar sem validação.
- **Problema.** São sete perguntas a um mesmo interlocutor:
  1. a tabela de prazos de retenção por categoria de dado (GO-19, com CA-03 e AV-02);
  2. o aviso de privacidade e o texto de finalidade de nome e CPF (CA-02, CA-04);
  3. a base legal dos avisos por e-mail (CA-05);
  4. o Requerimento com cor/raça e renda coletado na inscrição, de todos os inscritos (CA-07);
  5. a modalidade de cota ao lado do nome na publicação, o prazo de exposição e a indexação por
     buscadores (CA-06);
  6. os dados das autoridades signatárias (ED-04);
  7. os registros do piloto do assistente (AS-18).
- **Alternativas.**
  - **A.** Um pacote, numa reunião.
  - **B.** Uma pergunta por spec, à medida que cada uma for à produção.
- **Impactos.** B repete a mesma conversa cinco vezes e deixa a retenção, que é transversal, sem dono.
- **Recomendação: A.** Duas medidas baratas podem ir antes da resposta, porque são conservadoras e
  não decidem o mérito:
  - o `noindex` na publicação nominal de resultado;
  - uma trava de inicialização para `AVISOS_AOS_CANDIDATOS` em produção, que exija declaração
    explícita de validação.

  Ambas são alterações de código e ficam para aprovação posterior.

### DEC-04 · Cefor: como o ato é assinado e quem assina

- **Contexto.** Em 28/09 o usuário decidiu que o PDF gerado pelo sistema **é** o documento oficial do
  Edital. Os itens 4 e 5 da DP-20 (forma de assinatura e nome da autoridade) ficaram com o Cefor. Sem
  autoridade vigente cadastrada, nenhum Edital se publica (`060`), e o guia de implantação não manda
  cadastrá-la no go-live.
- **Alternativas.**
  - **A.** Assinatura eletrônica externa sobre o PDF do sistema.
  - **B.** Ato sem assinatura digital, com a autoridade identificada e a autenticidade dada pela
    publicação no sistema.
  - **C.** Assinatura em papel digitalizada.
- **Recomendação.** Levar a pergunta junto com a lista de autoridades a cadastrar. A escolha muda o
  que o PDF imprime no fecho, não o resto do sistema. Matriz: ED-04 (com GO-11 e GO-12).

### DEC-05 · Correio institucional, e o que o candidato vê quando o código não chega

- **Contexto.** O e-mail é o único fator de acesso do candidato. O sistema só faz STARTTLS (587), e a
  porta 465 depende do setor de correio. A falha de envio do código vira só log, por desenho: o
  candidato vê a mensagem neutra e não entra. Na `main`, `EMAIL_HOST` vazio passa na inicialização; a
  recusa está no PR #283, aberto.
- **Problema.** Há uma decisão institucional (servidor, porta, redundância, monitoramento) e uma de
  produto: mostrar ou não ao candidato que o envio falhou. A mensagem neutra existe para não revelar
  se um e-mail está cadastrado.
- **Alternativas de produto.**
  - **A.** Manter a mensagem neutra e monitorar a fila.
  - **B.** Dizer "não conseguimos enviar agora, tente em alguns minutos" quando o servidor recusa, sem
    revelar cadastro.
- **Recomendação.** Perguntar ao correio pelo checklist §25 do guia. No produto, B, que preserva a
  privacidade porque responde igual para qualquer endereço. Matriz: GO-25 (com AS-23 e CA-16).

---

## Bloco 2 — Decisões de produto (do usuário)

### DEC-06 · Qual documento a página oferece como "Edital completo" depois de uma Retificação

- **Contexto.** "Ler o Edital completo (PDF)" liga ao documento da publicação de origem da versão
  vigente (`portal/views.py:151`). Quando há Retificação de vigência futura, ou base anterior, esse
  PDF pode não conter uma Retificação em vigor. O defeito foi reproduzido em 12/10. No percurso de
  15/10, a página listava duas "Retificação 15/10/2026", uma "vigente desde 30/10/2026" (PV-05).
- **Alternativas** (`doc/achado-documento-ligado-nao-contem-a-versao-vigente.md`):
  - **A.** A página diz quais atos o documento contém e lista os demais em vigor, sem chamá-lo de
    "completo". Só leitura.
  - **B.** Recusar Retificação cuja base não contenha todos os atos que vigorarão junto.
  - **C.** Um documento por versão consolidada.
  - **D.** O documento da Retificação composto sobre o conteúdo da data de vigência.
- **Impactos.** O PDF é o ato oficial: B, C e D mexem no que se publica, e A só no que a página diz.
- **Recomendação: A agora, como spec curta**, junto com o "o que mudou" no consolidado (aPDF-ED-06).
  A escolha entre B, C e D fica para quando houver uma Retificação real de vigência futura. Matriz:
  ED-06 (com CA-08 e AS-05) e PV-05.

### DEC-07 · Retificação que acrescenta ou remove documento exigido: o que vale para quem já se inscreveu

- **Contexto.** Em 03/09 o usuário chamou de P0 a Retificação de documentos exigidos. Metade foi
  feita: a `044` grava a lista exigida em cada inscrição, o que dá a base para a regra.
- **Alternativas.**
  - **A.** A mudança vale só para quem se inscreve depois.
  - **B.** Vale para todos, e quem já enviou ganha prazo para complementar.
  - **C.** A Retificação de documento exigido só é aceita antes da primeira inscrição enviada.
- **Recomendação.** A, que é a leitura mais segura de direito adquirido e a mais barata, com a tela
  dizendo isso a quem retifica. B só se o setor apontar caso real. Matriz: ED-08.

### DEC-08 · Reabilitado por recurso antes do marco: deve alcançar o corte?

- **Contexto.** Quando um recurso reabilita alguém eliminado numa Etapa anterior à última do marco, a
  ordem fica obsoleta, mas o corte não acusa reingresso. O achado reproduziu o caso em 07/10, e a
  escolha está com o usuário desde então.
- **Alternativas** (`doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md:112-145`):
  - **A.** Alargar a pergunta a quem o ato excluiu.
  - **B.** O corte delega à ordem (`estado_do_marco`).
  - **C.** Manter, e a tela do corte aponta para a ordem obsoleta.
- **Recomendação: B.** A ordem já acusa a reabilitação, e delegar evita uma segunda regra que diga o
  mesmo. Spec curta, numa faixa de FR atual: a faixa FR-1166, que o achado sugere, já foi usada pela
  `063`. Matriz: AV-04.

### DEC-09 · Que famílias de Edital entram no alvo (DP-10) e o alcance da Etapa por Perfil (DP-08, item 3)

- **Contexto.** A DP-10 está aberta desde 26/09. Ela cobre barema estruturado, heteroidentificação,
  cascata de grupos e submodalidades. Hoje o barema é apurado fora do sistema, por decisão de 04/09,
  e o Edital previsto para o piloto tem heteroidentificação.
- **Alternativas.**
  - **A.** Decidir família a família, com o Edital do piloto na mão, e só o que ele usa entra.
  - **B.** Declarar todas fora do piloto e documentar o procedimento externo de cada uma.
  - **C.** Especificar as quatro agora.
- **Recomendação: A**, coerente com o princípio VI da Constituição: o alvo vem da jornada real. Se o
  piloto não tiver data (DEC-01), B, com o procedimento externo escrito no manual (`G-03`). Matriz:
  ED-10 (com AV-05 e AV-35) e ED-09 (com AV-13).

### DEC-10 · Acessibilidade do ato oficial

- **Contexto.** O PDF oficial sai sem marcação para leitor de tela, e as seções de texto do Edital só
  existem nele: o portal mostra a parte estruturada, não o texto.
- **Alternativas.**
  - **A.** PDF marcado (tags).
  - **B.** O ato também em HTML acessível, publicado junto e com o mesmo conteúdo.
  - **C.** Manter e oferecer atendimento sob demanda.
- **Recomendação: B.** O portal já renderiza HTML e a `069` já organiza o texto por perguntas. A marca
  no PDF pode vir depois. É decisão porque muda o que se publica: dois artefatos do mesmo ato. Matriz:
  ED-11 e CA-09.

### DEC-11 · Nome social: quando abrir a spec prometida em 16/09

- **Contexto.** Em 16/09 o usuário decidiu que o nome social viraria spec própria. Ela nunca foi
  aberta, e o nome civil aparece em listas públicas e na convocação.
- **Alternativas.**
  - **A.** Abrir antes do piloto.
  - **B.** Abrir depois e atender por procedimento manual no piloto.
- **Recomendação.** Pedir ao jurídico se o Decreto 8.727/2016 alcança o certame. Esta auditoria não
  conferiu a fonte. Se alcançar, A. Matriz: CA-19.

### DEC-12 · Requerimento de Matrícula pedido "na inscrição" bloqueia o envio?

- **Contexto.** A FR-372 tornou o Requerimento obrigatório para enviar a inscrição quando o Edital o
  pede no ato da inscrição. Foi decidida pelo agente, sem pergunta ao usuário. Em Edital por sorteio,
  isso coleta cor/raça, renda e filiação de todos os inscritos, inclusive dos que nunca serão chamados.
- **Alternativas.**
  - **A.** Manter.
  - **B.** O Requerimento passa a não bloquear o envio.
  - **C.** A composição desaconselha "na inscrição" em Edital por sorteio.
- **Recomendação: C, e B se o encarregado (DEC-03) apontar excesso de coleta.** Matriz: CA-07.

### DEC-13 · O formato do manual

- **Contexto.** A arquitetura do manual (HTML, 31 capítulos, 89 capturas, 25 sessões) foi aprovada em
  08/09. Desde o piloto editorial, nenhuma sessão de produção rodou. Enquanto isso, a Visão do Sistema
  (`docs/visao-sistema/`) virou o material de uso mais completo, revisado por ciclos e atualizado até
  a `072` nesta auditoria. Os dois documentos não se citavam.
- **Alternativas.**
  - **A.** Retomar as 25 sessões como planejadas.
  - **B.** A Visão do Sistema como base de referência, mais o que só o manual tem: as trilhas por
    papel, as tarefas e as capturas. As sessões de capítulo-a-capítulo caem.
  - **C.** Adiar o manual até o piloto, e escrevê-lo com quem opera.
- **Recomendação: C, com a preparação de B.** Um manual de operação escrito antes de alguém operar
  mede o sistema contra si mesmo. As trilhas por papel (Parte 3) podem ser escritas antes, porque são
  curtas e só roteiam. Matriz: GO-43 e GO-44.

### DEC-14 · Quem valida com pessoas, e quando

- **Contexto.** Nenhum dos 172 itens da matriz está **implementado e validado**. As validações
  pendentes têm a mesma forma:
  - o teste operacional assistido da elaboração e da condução (DP-18 / GO-31);
  - o percurso com cinco pessoas da jornada pública (SC-605 / CA-01) e a jornada completa do
    candidato (CA-15);
  - leitor de tela e ASES (CA-14);
  - o sorteio com a comissão (AV-07);
  - a revisão do setor das respostas da `070` (AS-01) e a sessão do piloto da `071` (AS-09);
  - a aprovação das frases da `069` (ED-03).
- **Alternativas.**
  - **A.** Uma semana de validação, com pauta única e o banco de demonstração preparado.
  - **B.** Uma validação por spec, quando houver oportunidade.
- **Recomendação: A.** O banco desta auditoria (`ps_aud1015`) mostrou que o `seed_demo` sobe em
  segundos e cobre os quatro estados de Edital. A decisão é de pessoas e datas, não de código.

### DEC-15 · Ratificar o que o agente decidiu sozinho

- **Contexto.** A auditoria recuperou decisões que entraram em specs sem pergunta ao usuário. Entre
  elas: o impeditivo `registration_period_cancelled`; seis reclassificações da matriz da `026`; a
  leitura estreita da decisão 001 da `044`; e a FR-372 (DEC-12). Todas estão listadas no ED-47 e na
  rastreabilidade histórica.
- **Recomendação.** Uma leitura de 20 minutos da lista, com "mantém" ou "revê" por linha.

### DEC-16 · Decisões de governança de specs, antigas e de baixo custo

- **DP-12, o campo `Status`.** 63 das 74 specs dizem "Draft", inclusive as mergeadas.
  Recomendação: abolir o campo e deixar o README, que já é conferido por teste, como fonte do estado.
- **DP-08, item 1: encerrar a `039`.** A spec nunca foi implementada; a Modalidade continua dentro do
  Perfil. Recomendação: encerrar como "registro de decisão, sem implementação".
- **DP-09: recurso sem prova nova.** Recomendação: manter (status quo).
- **DP-11: a comissão vê só o seu Perfil ou polo?** Recomendação: decidir no ensaio da DEC-14, com a
  comissão.
- **DP-15: um documento público por marco.** Recomendação: formalizar a opção A, que é a praticada.

---

## Bloco 3 — Ações que só o usuário pode fazer (não são decisões estratégicas)

| Ação | Por quê | Item |
|---|---|---|
| Conferir no painel do OpenRouter que a chave exposta numa captura em 14/10 foi revogada | Custo indevido até o limite da chave; correção de um minuto | GO-09 |
| Autorizar o commit e o push da `074` na própria branch, sem merge | Spec, código e testes existem só numa worktree local sem commit; uma remoção com `--force` apaga tudo | GO-46 |
| Copiar os vídeos (~21 GB) para fora das worktrees | Fora de qualquer versionamento | GO-47 |
| Revisar e decidir o merge do PR #283 (`073`) | CI verde, mas o GitHub o marca como conflitante; o merge é do usuário | GO-26 |
| Escolher a redação do reenvio da convocação ("contado do primeiro envio, em …") | O texto atual sugere prazo novo; corrigir emenda a UX-038 e três guardiões | CA-23 |
