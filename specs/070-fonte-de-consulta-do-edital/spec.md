# Feature Specification: A fonte de consulta do Edital vigente — respostas com versão, origem e limites, para o futuro assistente de dúvidas (Fase A)

**Feature Branch**: `claude/audit-edital-assistant-a8f915` — worktree sobre a `main` `a79ce463` (PR #273),
que já tem a `066`, a `067` e a `068`.

**Created**: 2026-10-12

**Status**: Draft

**Input**: a [auditoria do assistente de dúvidas do Edital, de 12/10/2026](../../doc/auditoria-assistente-de-duvidas-do-edital-2026-10-12.md),
o [achado do documento ligado que não contém a versão vigente](../../doc/achado-documento-ligado-nao-contem-a-versao-vigente.md),
e as decisões do responsável pelo produto sobre ela, de 12/10/2026, citadas aqui como 1º a 8º:

1. **Uma spec só para a Fase A.**
   - **O escopo:** a fonte confiável de consulta do futuro assistente, com referências rastreáveis e
     respostas determinísticas às perguntas sugeridas. A validação é interna, de início.
   - **O objetivo final continua sendo o assistente conversacional dentro da página do Edital.**
     Esta fase prepara essa integração. Ela **não** cria:
     - produto independente de FAQ;
     - plataforma genérica de IA;
     - interface pública prematura.
2. **O piloto com LLM e a disponibilização pública são fases posteriores** (ver
   [Fases posteriores](#fases-posteriores)).
3. **Cartões de referência**, cada um com:
   - a informação utilizada;
   - a identificação da versão vigente;
   - os links disponíveis para conferência.

   Sem leitura integral do Edital em HTML nesta fase. Os cartões distinguem expressamente três
   coisas: o texto literal preservado na fonte publicada, o dado estruturado da versão vigente e a
   explicação produzida a partir deles. **Frase recomposta pelo código não é citação literal do PDF.**
   A compatibilidade com a decisão da `069` é conferida em
   [Compatibilidade com a 069](#compatibilidade-com-a-069).
4. **Canal de atendimento.**
   - O canal informado no Edital tem prioridade.
   - O canal configurado na implantação é alternativa só quando o Edital não traz canal específico.
   - Entre instruções contraditórias, o sistema não escolhe: registra a inconsistência para revisão.
   - A cláusula de esclarecimentos "exclusivamente" por um canal é questão a resolver antes da
     abertura pública do assistente nos Editais afetados. Ela **não** bloqueia a preparação interna.
5. **Pontos obrigatórios:**
   - a versão vigente determinada a cada consulta, inclusive com Retificação de vigência futura;
   - resposta e referências da mesma versão;
   - nada de rascunho, nem de dado administrativo que não represente o conteúdo publicado vigente;
   - nada respondido só com base no histórico quando a versão mudou;
   - condições e exceções preservadas, inclusive as que estão em descrição de Evento;
   - informação ausente, ambígua e conflitante distinguidas;
   - perguntas que dependem de anexo reconhecidas e encaminhadas à fonte pertinente;
   - vagas de ampla concorrência representadas corretamente;
   - a matriz de avaliação da auditoria reaproveitada, nos casos pertinentes à Fase A.
6. **O link "Edital completo" só vira referência depois de reproduzida a divergência.**
   - **Reproduzida em 12/10/2026:** ver o achado.
   - A correção dele é **dependência explícita** da abertura pública, e não escopo desta feature.
7. **A Fase A não chama modelo nenhum.** A futura integração deve permitir isolar a inferência da
   capacidade que atende às páginas públicas, sem antecipar agora infraestrutura desnecessária.
8. **Nesta rodada, só a spec e o checklist.** Nenhuma decisão de outra spec é alterada.

> **Faixa de identificadores.** Esta spec abre em **FR-1410**, **SC-530** e **UX-200**, e as
> decisões nascem em `D-001`.
>
> **O teto medido.** Em 12/10/2026, na `main`, em todas as worktrees e nos PRs abertos (nenhum),
> o teto é o da `069`: mil e quatrocentos para os requisitos funcionais, quinhentos e vinte e quatro
> para os critérios de sucesso, cento e noventa e três para a experiência. A `069` está aberta em
> outra worktree, sem commit, e ainda pode crescer: por isso a folga de nove números.
>
> **A pasta.** O número `070` é o seguinte livre em todas as worktrees.

**A frase que governa:**

> Cada resposta diz de qual versão do Edital ela vem, de qual ato publicado vem cada informação, e o
> que é texto do Edital, o que é dado e o que é explicação — e nunca diz mais do que o Edital
> publicado diz.

---

## Por que esta feature existe

### O objetivo, e por que ele começa sem modelo

O objetivo é um assistente na página de cada seleção: o visitante pergunta e recebe uma explicação
em linguagem simples, com as fontes oficiais. A auditoria concluiu que o modelo de linguagem é a
parte **menos** garantida desse assistente:

- ele pode errar uma data;
- pode omitir uma exceção;
- pode citar uma versão que já não vale.

O que impede esses erros de chegarem ao visitante não é o modelo. É a fonte que ele recebe e a
conferência do que ele devolve. Esta fase constrói essa fonte e a prova **sem** modelo, com
respostas que o próprio sistema monta a partir do Edital publicado. Ela serve a três coisas:

- o setor de seleção valida, Edital a Edital, o que o assistente poderá dizer;
- as perguntas sugeridas passam a ter resposta exata, que continua funcionando quando o modelo
  estiver fora do ar;
- o piloto com o modelo herda uma fonte já conferida, e não a constrói no mesmo passo em que avalia
  o modelo.

### O que a auditoria encontrou, e esta feature trata

Verificado no código em 12/10/2026, e citado na auditoria com caminho e linha.

| Achado | Consequência para uma resposta |
|---|---|
| O conteúdo vigente existe, imutável e com início de vigência — a versão consolidada —, e a página pública já o lê | Não é preciso fonte nova: é preciso **lê-la direito** |
| As frases que o PDF imprime sobre corte, desempate, recurso e sorteio **não estão** no conteúdo publicado; são recompostas pelo código de cada momento | Mostrar a frase de hoje como "o que o PDF diz" pode afirmar o que o documento publicado não diz |
| A versão vigente muda **sem ato novo** quando chega a vigência de uma Retificação já publicada | A versão tem de ser determinada a cada consulta, pelo instante, e não por evento de publicação |
| O documento que a página pública chama de "Edital completo" pode não conter uma Retificação em vigor — **reproduzido** (achado) | Esse link não pode ser referência |
| As vagas de ampla concorrência estão na linha do quadro **sem** modalidade; uma modalidade "AC" declarada pode não ter linha | Uma leitura ingênua responde "zero vagas de ampla concorrência" |
| Há regras dentro da descrição de Evento ("isenção de taxa até o 5º dia") e condições dentro das instruções de documento | Resposta que use só a data ou só o nome omite a condição |
| Os anexos são arquivos que o sistema nunca lê, e a pontuação da prova de títulos do 92/2026 está num deles | A resposta precisa saber que o detalhe está ali, e dizer isso |
| O canal de dúvidas de cada Edital é texto livre — às vezes "exclusivamente pelo e-mail …" — e o canal da implantação não aparece na página da seleção | Encaminhar exige achar o canal certo, e não escolher entre dois |
| A numeração impressa é posicional e muda quando uma Retificação esvazia uma seção | "Item 11.1" não serve de referência |

---

## O que esta fase entrega, e o que fica para depois

### O que poderá ser validado ao concluir a Fase A

1. **Respostas às perguntas sugeridas.** Para qualquer Edital publicado, o setor de seleção confere,
   na gestão, a resposta a cada pergunta sugerida que se aplica a ele. Cada resposta traz o tipo, a
   explicação, os cartões de referência e a versão.
2. **Versão certa no instante.** A resposta é a da versão vigente no instante consultado, inclusive
   antes e depois da fronteira de uma Retificação de vigência futura, e avisa quando a versão mudou
   desde a consulta anterior.
3. **Natureza e origem de cada informação.** Cada cartão diz se é texto do Edital, dado ou explicação.
   Cada texto e cada dado leva ao documento do ato publicado que o fixou, e nenhum leva a documento
   chamado "Edital completo".
4. **Os limites aparecem como limites.** Ausente, dependente de leitura, conflitante e "detalhe em
   anexo" aparecem como tais, e nenhum vira afirmação.
5. **O canal de atendimento** de cada Edital, e os pontos para revisão antes da abertura pública:
   - canais contraditórios;
   - cláusula de exclusividade;
   - anexo citado que não existe;
   - Retificação futura;
   - documento de origem incompleto.
6. **A matriz da auditoria** nos casos pertinentes, rodando sobre Editais que reproduzem o corpus.
7. **A cobertura:** todo campo do conteúdo publicado alcançado por alguma resposta, ou excluído com o
   motivo.
8. **Nenhuma chamada a modelo nem a serviço externo.**

### O que continuará pendente para o piloto com LLM (Fase B)

- **Confirmar o modelo e a GPU:** identificador exato, quantização, servidor e API de inferência,
  janela de contexto, memória livre na L4, serviços que a compartilham, rede e operação (§3.3 da
  auditoria).
- **A pergunta livre:** montagem do contexto a partir das mesmas unidades desta fase, saída
  estruturada e a conferência pela aplicação — citações só entre os cartões enviados, números e
  datas presentes nas fontes citadas, abstenção quando a conferência falha.
- **Os casos da matriz que só existem com pergunta livre:** outro Edital, decisão individual,
  situação individual, indução a inventar, instrução escondida na fonte, pressão por certeza,
  indisponibilidade e limite. Cada caso roda várias vezes.
- **Medições:** latência, concorrência, impacto sobre os outros serviços da GPU e sobre o portal.
- **Isolamento da inferência** em relação aos workers que servem as páginas públicas.
- **O registro integral de perguntas e respostas do piloto**, com participantes identificados e prazo
  de retenção.
- **Editais reais** compostos no sistema para o piloto.

### O que continuará pendente para a disponibilização pública (Fase C)

- A entrada "Tire suas dúvidas sobre este edital" na página da seleção e a rota pública.
- O texto que declara a natureza não oficial das respostas, aprovado institucionalmente.
- **A correção do [achado](../../doc/achado-documento-ligado-nao-contem-a-versao-vigente.md)**, por uma
  das opções registradas nele. A escolha é do usuário e cabe numa spec própria.
- **A resolução da cláusula de exclusividade** em cada Edital afetado, antes de abrir o assistente
  nele.
- **A validação institucional da LGPD:** perguntas digitadas podem conter dado pessoal.
- **Operação:**
  - limite de uso por origem e teto global de chamadas;
  - estados de carregamento, indisponibilidade e limite;
  - liberação Edital a Edital;
  - registros operacionais mínimos;
  - saída escapada e política de conteúdo da página.
- O canal de atendimento visível também na página da seleção.

---

## User Scenarios & Testing *(mandatory)*

O ator desta fase é a **equipe do setor de seleção**, na gestão: quem conhece os Editais e
responde às dúvidas dos candidatos pelo canal oficial. Ela confere o que o assistente poderá dizer
antes de qualquer abertura ao público. O candidato não vê nada desta fase.

### User Story 1 — A equipe confere a resposta a uma pergunta sugerida, com a versão e as fontes (Priority: P1)

Na página de um Edital publicado, na gestão, a pessoa abre a conferência das respostas do
assistente. Vê as perguntas sugeridas que se aplicam àquele Edital, escolhe uma — e, quando a
pergunta pede, o Perfil e a lista de concorrência, entre os do próprio Edital — e lê a resposta.

A resposta traz:

- a versão em que se baseia;
- o tipo, em palavras;
- uma explicação curta;
- os cartões de referência, cada um rotulado como texto do Edital, dado ou explicação, com o ato de
  onde veio e o link para o documento desse ato.

**Why this priority**: é a fonte de consulta funcionando de ponta a ponta, e a forma pela qual o setor
valida o que o assistente vai dizer.

**Independent Test**: publicar o Edital 91/2026 do corpus pelo fluxo real, pedir "Que documentos
preciso enviar?" para o Perfil `INF-BJN` e a lista PcD, e conferir:

- os documentos comuns e o laudo médico, com as instruções literais;
- os textos de inscrição e de verificação da autodeclaração, inteiros;
- a versão;
- o link de cada cartão para o documento do ato de origem.

**Acceptance Scenarios**:

1. **Given** o 91/2026 publicado e retificado (v2), **When** se pede "Quantas vagas há neste Perfil?"
   para `INF-BJN`, **Then** a resposta diz 45 — 33 de ampla concorrência, 10 PPI e 2 PcD.
   - O cartão de dado das vagas leva ao documento **da Retificação**, que fixou o 45.
   - O cartão das linhas não alteradas leva ao documento da publicação original.
2. **Given** o mesmo Edital, **When** se pede a mesma pergunta para `INF-IUN`, **Then** a ampla
   concorrência aparece com 28 vagas, e nenhuma lista aparece com zero só por ter uma modalidade
   "AC" declarada sem linha no quadro.
3. **Given** o 92/2026, **When** se pede "Como será a seleção?" para um Perfil, **Then**:
   - a resposta traz as Etapas e os critérios de desempate em cartões de dado, na ordem — menor data
     de nascimento, maior experiência em tutoria, maior pontuação na prova de títulos —, com a regra
     de quem não tem o valor;
   - traz um aviso de que o detalhe da prova de títulos está no Anexo IV, com o link ao anexo;
   - não traz nenhum número de pontuação que o conteúdo publicado não tenha.
4. **Given** qualquer resposta, **When** se examinam os cartões, **Then** nenhum apresenta como "texto
   do Edital" uma frase que o compositor do PDF gera — corte, desempate, recurso, sorteio, teto,
   reversão —, e nenhum identifica seção pelo número impresso.

---

### User Story 2 — A resposta é sempre a da versão vigente no instante, e nunca mistura versões (Priority: P1)

Cada consulta determina de novo a versão vigente. A resposta inteira — explicação, cartões, situação
de calendário — sai de uma versão só, lida uma vez.

- Se o Edital tem Retificação publicada com vigência futura, a resposta usa a versão vigente e diz o
  que muda e quando, para o que ela cita.
- Se a versão mudou desde a consulta anterior, a resposta começa por esse aviso e não reaproveita
  nada da anterior.

Para validar sem esperar o calendário, a equipe pode consultar num instante de referência escolhido.

**Why this priority**: a versão errada é o erro mais grave que um assistente de Edital pode cometer, e
o único que o visitante não tem como perceber.

**Independent Test**: publicar o 01/2026 do corpus com as duas Retificações — a segunda vigente a
partir de 26/10/2026 — e pedir "Até quando posso me inscrever?" em 20/10 e em 27/10.

**Acceptance Scenarios**:

1. **Given** o 01/2026 com a v3 publicada e vigente a partir de 26/10/2026, **When** se consulta em
   20/10/2026, **Then** a resposta diz que as inscrições vão até 31/10/2026, pela versão vigente, e
   acrescenta que uma Retificação já publicada prorroga o término para 10/11/2026 a partir de
   26/10/2026.
2. **Given** o mesmo Edital, **When** se consulta em 27/10/2026, **Then** a resposta diz 10/11/2026 e
   identifica a versão vigente desde 26/10/2026.
3. **Given** uma consulta feita sobre a versão anterior, **When** a pessoa consulta de novo depois da
   fronteira, sem nenhum ato novo publicado naquele dia, **Then**:
   - a resposta começa pelo aviso de que o Edital mudou, com o ato e a data de vigência;
   - a resposta anterior é identificada como da versão anterior;
   - nada dela é reaproveitado.
4. **Given** uma Retificação em elaboração, ou homologada e não publicada, que muda as vagas, **When**
   se consulta, **Then** as vagas são as da versão vigente, e nada da Retificação pendente aparece.
5. **Given** um Edital ainda não publicado, **When** se tenta consultar, **Then** não há consulta, e a
   tela diz que só Edital publicado tem respostas.

---

### User Story 3 — O que o Edital não diz, diz em texto que o sistema não interpreta, ou diz de modos diferentes aparece como tal (Priority: P1)

Uma resposta nunca vira afirmação quando o dado não sustenta.

- **Ausente.** O Edital não trata do assunto, e a resposta diz que o Edital não informa — sem
  transformar silêncio em proibição.
- **Depende da leitura.** O assunto está só em texto, ou em fontes de naturezas diferentes. A
  resposta mostra todas, inteiras, e diz que o sistema não as concilia.
- **Conflitante.** O sistema compara duas fontes e elas divergem. A resposta mostra as duas e não
  escolhe.
- **Detalhe em anexo.** A resposta leva ao anexo e diz que o sistema não lê o conteúdo dele.

**Why this priority**: é a garantia que o modelo da fase seguinte não dá sozinho, e o que a auditoria
chamou de abstenção adequada.

**Independent Test**: os casos `CA-10`, `CA-11`, `CA-13`, `CA-14` e `CA-15` da auditoria, sobre o corpus.

**Acceptance Scenarios**:

1. **Given** um Edital cujo marco nada declara sobre recurso, sem seção de recursos e sem Evento que
   fale de recurso, **When** se pede "Posso recorrer? Em que prazo?", **Then**:
   - o tipo é "O Edital não informa";
   - a resposta **não** diz que não cabe recurso;
   - a resposta indica o canal de atendimento.

   *Emenda de 12/10/2026, durante a implementação.* A versão anterior deste cenário usava o
   `TEC-LAB` do 01/2026. Esse Perfil não declara recurso e o Edital não tem seção de recursos, mas o
   cronograma tem o Evento "Resultado final e abertura do prazo recursal". Pelo `R-014`, ele é
   fonte sobre recurso, e a resposta certa ali é "Depende da leitura do Edital": dizer "não informa"
   esconderia o texto. O `TEC-LAB` passou ao cenário 1a; o caso de ausência pura usa conteúdo
   sintético.
1a. **Given** o 01/2026, **When** se pede a mesma pergunta para `TEC-LAB`, **Then** o tipo é "Depende
   da leitura do Edital", a resposta mostra o Evento "Resultado final e abertura do prazo recursal"
   inteiro, **não** diz que não cabe recurso e indica o canal.
2. **Given** o 91/2026, **When** se pede a mesma pergunta para `INF-BJN`, **Then** o tipo é "Depende
   da leitura do Edital", e a resposta mostra, inteiros, os três:
   - o dado do marco: recurso contra "Classificação por sorteio eletrônico", em 2 dias corridos;
   - o texto da seção "Dos Recursos", que trata de recurso contra o resultado preliminar da análise
     documental;
   - o Evento "Prazo para interposição de recurso".

   Sem escolher entre eles.
3. **Given** o 01/2026, **When** se pede "Até quando posso me inscrever?", **Then** o cartão do Evento
   traz a descrição literal — "Inscrições pelo sistema, com isenção de taxa até o 5º dia." —, e a
   explicação não diz nada sobre taxa que o texto não diga.
4. **Given** o 92/2026 depois da Retificação que esvaziou a seção de atendimento à pessoa com
   deficiência, **When** se pede "Que documentos preciso enviar?" com a lista PcD, **Then** a
   resposta não traz o texto retirado e não afirma que o atendimento deixou de existir.

---

### User Story 4 — O canal de atendimento vem do Edital, e as contradições ficam para revisão (Priority: P2)

"Onde tiro dúvidas?" responde com o canal que o Edital informa, no parágrafo literal em que ele
aparece.

- **Sem canal no Edital:** a resposta usa o canal configurado na implantação, dito como canal
  institucional.
- **Dois canais diferentes no Edital:** a resposta mostra os dois e não escolhe.
- **O mesmo parágrafo restringe as dúvidas a um canal** ("exclusivamente"): a resposta mostra o canal
  normalmente.

Nos dois últimos casos, o Edital ganha um **ponto para revisão** antes da abertura pública.

**Why this priority**: encaminhar ao atendimento é a saída de toda resposta que não se sustenta; ela
precisa estar certa. Mas não impede a validação das demais perguntas.

**Independent Test**: o 91/2026 (um canal, com "exclusivamente"), o 92/2026 (um canal) e um Edital de
teste com dois canais diferentes.

**Acceptance Scenarios**:

1. **Given** o 91/2026, **When** se pede "Onde tiro dúvidas?", **Then**:
   - a resposta traz o e-mail do Edital no parágrafo literal da seção "Disposições Preliminares";
   - os pontos para revisão do Edital listam a cláusula de exclusividade, como questão a resolver
     antes da abertura pública.
2. **Given** um Edital cujas seções trazem dois e-mails diferentes para dúvidas, **When** se pergunta,
   **Then** o tipo é "Fontes divergentes", os dois parágrafos aparecem inteiros, nenhum é escolhido, e
   a divergência está nos pontos para revisão.
3. **Given** um Edital sem canal nas seções, **When** se pergunta, **Then** a resposta traz o canal da
   implantação, rotulado como canal institucional, e não como canal do Edital.

---

### User Story 5 — A equipe vê, por Edital, o que precisa ser revisto antes da abertura pública (Priority: P2)

Na mesma tela, um bloco lista os pontos para revisão da versão vigente:

- canais contraditórios;
- cláusula de exclusividade do canal de dúvidas;
- anexo citado no texto que não está entre os anexos publicados;
- Retificação publicada com vigência futura;
- documento de origem da versão vigente que não contém todos os atos dela — o caso do achado.

Nada disso é corrigido aqui: é a lista do que o setor resolve, por Retificação ou por decisão
institucional, antes de o assistente abrir naquele Edital.

**Why this priority**: transforma a validação interna em critério de prontidão por Edital, que é o
que a abertura pública vai precisar.

**Independent Test**: os três Editais do corpus e os dois cenários do achado.

**Acceptance Scenarios**:

1. **Given** um Edital nas condições do cenário 1 do achado, **When** se abre a conferência,
   **Then** os pontos para revisão dizem que o documento de origem da versão vigente não contém todos
   os atos dela, e quais faltam.
2. **Given** um Edital sem nenhuma das condições, **When** se abre a conferência, **Then** o bloco diz
   que não há ponto para revisão.

---

### Edge Cases

- **Edital cancelado ou encerrado.** A consulta continua possível. A situação de calendário diz o
  desfecho, que prevalece sobre o período ("não está em curso"), como na página pública.
- **Duas Retificações com vigências fora da ordem de publicação.** A versão vigente segue a ordem de
  vigência, e o cartão de cada valor aponta o ato que o fixou nessa ordem.
- **Conteúdo publicado num esquema anterior.** Campo ausente é "não informado", e nunca valor
  inventado; o conteúdo publicado não é convertido.
- **Perfil sem modalidade.** A pergunta de documentos oferece só a ampla concorrência.
- **Perfil só de cadastro de reserva** (zero vagas imediatas). A resposta de vagas diz o cadastro de
  reserva, limitado ou ilimitado, sem afirmar "zero vagas" como se fosse ausência de oferta.
- **Documento com instrução condicional** ("apenas PcD") e marcado como não obrigatório. A instrução
  sai literal; a explicação não converte a condição em regra.
- **Anexo vinculado ao documento por dado**, e não por texto. O cartão do anexo sai pelo vínculo, sem
  depender de o texto citá-lo.
- **Texto que cita "Anexo IV" e o Edital não tem anexo com esse rótulo.** Nenhum cartão inventado;
  ponto para revisão.
- **Seção textual vazia ou retirada por Retificação.** Não aparece, e nada se afirma a partir da
  ausência dela.
- **Numeração digitada no texto** ("11.1 Os recursos…"). Sai como está, porque é texto do Edital, e o
  cartão identifica a seção pelo título.
- **Instante de referência anterior à primeira publicação.** Não há versão vigente; a tela diz isso.
- **Instante futuro.** Só os atos já publicados são considerados; nada é antecipado.
- **O mesmo canal em dois parágrafos.** É um canal só, e não há divergência.
- **Recurso negado expressamente pelo marco.** É dado declarado: a resposta mostra a negativa como o
  Edital a declara, e isso não é "O Edital não informa".

---

## Requirements *(mandatory)*

### Functional Requirements

#### A versão e as fontes

- **FR-1410**: A consulta MUST determinar a versão vigente no instante consultado — por padrão, o
  momento da consulta — pela mesma regra que a página pública usa. Uma Retificação publicada com
  vigência futura MUST NOT ser aplicada antes do início da vigência dela.
- **FR-1411**: Tudo o que uma resposta contém MUST derivar de uma única versão e de um único instante,
  lidos uma vez para a resposta inteira: explicação, cartões e situação de calendário. A resposta
  MUST identificar essa versão:
  - a data da publicação original;
  - as datas das Retificações aplicadas;
  - a data de início da vigência da versão;
  - um identificador curto da versão, que permita conferir o conteúdo.
- **FR-1412**: As fontes da consulta MUST ser só estas:
  - o conteúdo consolidado da versão vigente;
  - os dados e documentos das publicações que essa versão aplica;
  - os atos de encerramento ou cancelamento registrados até o instante;
  - o canal de atendimento configurado na implantação.

  A consulta MUST NOT ler:
  - rascunho;
  - Retificação não publicada;
  - os registros de elaboração do Edital, que depois da publicação guardam o estado do dia da
    publicação, e não o vigente;
  - resultado, inscrição ou qualquer dado de candidato.
- **FR-1413**: Edital sem publicação MUST NOT ter consulta.
- **FR-1414**: Quando houver Retificação publicada com vigência futura, a resposta MUST:
  - usar a versão vigente;
  - dizer que há Retificação publicada, com a data de vigência;
  - para cada conteúdo citado que essa Retificação altera, dizer o valor que passará a valer e desde
    quando.

  Ato não publicado MUST NOT ser antecipado.
- **FR-1415**: A consulta MAY informar a versão em que a consulta anterior se baseou. Quando ela
  diferir da vigente — inclusive quando nenhuma publicação nova aconteceu e só a fronteira de
  vigência passou —, a resposta MUST:
  - começar pelo aviso de mudança;
  - identificar os atos que separam as duas versões;
  - não reaproveitar nada da resposta anterior.
- **FR-1416**: A consulta MUST aceitar conteúdo publicado em qualquer versão de esquema, sem converter
  o conteúdo publicado e sem atribuir valor a campo ausente: campo ausente é informação não declarada.

#### As perguntas sugeridas

- **FR-1417**: As perguntas MUST ser as do catálogo fechado abaixo. Cada uma MUST ser oferecida só
  quando o Edital tem conteúdo para ela, conforme a coluna "Oferecida quando".

  | Código | Pergunta | Parâmetros | Oferecida quando |
  |---|---|---|---|
  | `P-01` | Até quando posso me inscrever? | — | há Evento de período de inscrições |
  | `P-02` | Quais são as próximas datas? | — | o cronograma tem Evento |
  | `P-03` | Quantas vagas há neste Perfil? | Perfil | sempre |
  | `P-04` | Quais são os requisitos deste Perfil? | Perfil | o Perfil ou o Edital declara requisito |
  | `P-05` | Que documentos preciso enviar? | Perfil e lista de concorrência | há documento exigido |
  | `P-06` | Posso me inscrever em mais de um Perfil? | — | o Edital tem mais de um Perfil |
  | `P-07` | Como será a seleção? | Perfil | o Perfil declara marco ou o Edital declara Etapa |
  | `P-08` | Posso recorrer? Em que prazo? | Perfil | sempre |
  | `P-09` | Como funciona o sorteio? | Perfil | o Perfil tem marco por sorteio |
  | `P-10` | Como serei convocado? | Perfil | sempre |
  | `P-11` | Onde tiro dúvidas? | — | sempre |
  | `P-12` | Onde estão o Edital e os anexos? | — | sempre |

- **FR-1418**: Os parâmetros MUST ser escolhidos entre os do próprio Edital, na versão vigente:
  - Perfil, pelo código e pelo nome;
  - lista de concorrência: a ampla concorrência e as modalidades do Perfil.
- **FR-1419**: A Fase A MUST NOT receber pergunta em texto livre.
- **FR-1420**: Cada pergunta MUST ter uma tabela fixa e declarada das seções textuais pertinentes
  (`D-007`). Toda seção pertinente preenchida na versão vigente MUST acompanhar a resposta, inteira,
  como texto do Edital.

#### As respostas

- **FR-1421**: Toda resposta MUST declarar um tipo, entre cinco:

  | Tipo | Quando |
  |---|---|
  | **Respondida pelos dados** | os dados estruturados determinam a resposta |
  | **O Edital não informa** | nenhuma fonte trata do assunto |
  | **Depende da leitura do Edital** | o assunto está só em texto que o sistema não interpreta, ou em fontes de naturezas diferentes que o sistema não concilia |
  | **Fontes divergentes** | duas fontes que o sistema compara divergem (`FR-1424`) |
  | **Detalhe em anexo** | o detalhe pedido está num anexo |

  Avisos MAY acompanhar qualquer tipo: Retificação futura, desfecho, detalhe em anexo.
- **FR-1422**: "O Edital não informa" MUST NOT ser expresso como negativa ("não cabe", "não há",
  "não é permitido"). Negativa MUST aparecer só quando o Edital a declara, e então como dado
  declarado.
- **FR-1423**: Em "Depende da leitura do Edital", a resposta MUST:
  - mostrar todas as fontes que tratam do assunto, inteiras;
  - dizer que o sistema não as concilia;
  - indicar o canal de atendimento.
- **FR-1424**: "Fontes divergentes" MUST se limitar às comparações que esta spec declara — na Fase A,
  só os canais de atendimento (`FR-1440`). Em divergência, a resposta MUST mostrar todas as fontes e
  MUST NOT escolher uma.
- **FR-1425**: A explicação MUST ser em linguagem simples e conter só valores presentes nos cartões da
  mesma resposta. Ela MUST NOT concluir sobre elegibilidade, deferimento, classificação, aceitação de
  documento ou situação de qualquer pessoa. Quando a pergunta tocar uma dessas decisões, a explicação
  MUST dizer que a decisão não é tomada pela consulta, e citar quem decide só se o Edital o declarar.
- **FR-1426**: Quando a resposta usar uma entidade que tem texto livre associado, esse texto MUST
  acompanhá-la inteiro, literal, sem resumo nem corte. São os casos:
  - a descrição e o local do Evento;
  - as instruções do documento;
  - os requisitos;
  - o fundamento da modalidade;
  - os textos de normalização e de substituição do sorteio.
- **FR-1427**: As vagas de ampla concorrência MUST ser as da linha do quadro sem modalidade. Uma
  modalidade declarada com nome ou código de ampla concorrência e sem linha própria no quadro MUST
  NOT aparecer como lista com zero vagas.
- **FR-1428**: Vagas imediatas, cadastro de reserva (nenhum, limitado com o limite, ilimitado) e
  reversão de vagas MUST sair dos dados declarados. Perfil só de cadastro de reserva MUST NOT ser
  descrito como Perfil sem oferta.
- **FR-1429**: A situação de calendário — o que está aberto, em andamento, por vir ou encerrado —
  MUST:
  - ser calculada no instante da consulta, pelas datas da versão vigente e pelo desfecho registrado
    até ele, com a mesma regra da página pública;
  - dizer o instante;
  - deixar o desfecho prevalecer sobre o período.
- **FR-1430**: Anexos.
  - Documento vinculado a anexo por dado MUST trazer o cartão do anexo, com rótulo e link.
  - Texto pertinente que cite um anexo pelo rótulo ("Anexo IV") MUST trazer o cartão do anexo
    publicado de mesmo rótulo, com o aviso de que o sistema não lê o conteúdo dele.
  - Citação sem anexo correspondente MUST virar ponto para revisão (`FR-1443`).
  - A resposta MUST NOT afirmar nada sobre o conteúdo de um anexo.
- **FR-1431**: Seções MUST ser identificadas pelo título. MUST NOT ser identificadas pelo número com
  que saem no documento, que é posicional e muda entre versões. Numeração digitada dentro do texto
  sai como está, porque é texto do Edital.

#### Os cartões de referência

- **FR-1432**: Cada cartão MUST ter exatamente uma natureza, rotulada em palavras:
  - **Texto do Edital**;
  - **Dado da versão vigente**;
  - **Explicação**.
- **FR-1433**: "Texto do Edital" MUST conter só texto preservado literalmente no conteúdo publicado,
  idêntico a ele, inteiro, com a identificação de onde está: seção pelo título, Perfil, Evento,
  documento ou modalidade.
- **FR-1434**: Frase que o compositor do documento gera a partir de dado — corte, desempate,
  arredondamento, recurso, sorteio, teto, Requerimento, reversão, títulos de grupo — MUST NOT ser
  apresentada como "Texto do Edital" nem como citação do PDF. A regra correspondente MUST aparecer
  como dado. A resposta MAY dizer em que seção do documento a regra é expressa, pelo título.
- **FR-1435**: "Dado da versão vigente" MUST mostrar o valor publicado, com o nome do campo na
  linguagem do domínio, datas na zona temporal institucional e números sem arredondamento que o
  Edital não declare.
- **FR-1436**: "Explicação" MUST se declarar produzida pelo sistema a partir dos cartões da resposta, e
  não texto do Edital.
- **FR-1437**: Cada cartão de texto e de dado MUST indicar o ato publicado de onde vem o conteúdo:
  - a publicação original, quando nunca alterado;
  - a Retificação que o fixou, quando alterado.

  O cartão MUST levar ao documento desse ato. Nenhum cartão MUST levar a documento apresentado como
  "Edital completo" ou como o documento da versão vigente (`D-004`).
- **FR-1438**: Os links de conferência MUST ser só estes:
  - o documento do ato de origem;
  - o anexo publicado;
  - o trecho da página pública da seleção em que a mesma informação aparece, quando existir: vagas do
    Perfil, cronograma, Edital e documentos.

  A Fase A MUST NOT compor leitura integral do Edital em HTML.

#### O canal de atendimento

- **FR-1439**: O canal do Edital MUST ser o contato — e-mail, endereço eletrônico ou telefone — que
  aparece em parágrafo de seção textual que trate de dúvidas, esclarecimentos ou atendimento. A lista
  fechada de termos é decidida no plano. Havendo um único canal distinto, a resposta MUST trazê-lo
  com o parágrafo literal.
- **FR-1440**: Havendo mais de um canal distinto, a resposta MUST:
  - ser do tipo "Fontes divergentes";
  - mostrar todos os parágrafos;
  - não escolher;
  - gerar ponto para revisão.

  O mesmo canal em parágrafos diferentes MUST contar como um.
- **FR-1441**: Sem canal no Edital, a resposta MUST trazer o canal configurado na implantação,
  rotulado como canal institucional, e não como canal do Edital. Sem nenhum dos dois, MUST dizer que
  não há canal informado.
- **FR-1442**: Parágrafo de canal que restrinja as dúvidas a ele — "exclusivamente", "somente",
  "unicamente" ou "apenas" — MUST:
  - gerar ponto para revisão, identificado como questão a resolver antes da abertura pública do
    assistente naquele Edital;
  - não alterar nem bloquear a consulta da Fase A.

#### Os pontos para revisão

- **FR-1443**: A consulta MUST oferecer, por Edital, os pontos para revisão da versão vigente:
  - canais divergentes (`FR-1440`);
  - cláusula de exclusividade (`FR-1442`);
  - anexo citado sem anexo publicado correspondente (`FR-1430`);
  - Retificação publicada com vigência futura;
  - documento da publicação de origem da versão vigente que não contém todos os atos aplicados nela —
    detectado e nomeado, sem correção ([achado](../../doc/achado-documento-ligado-nao-contem-a-versao-vigente.md)).
- **FR-1444**: Os pontos para revisão MUST ser derivados do conteúdo e dos atos, na leitura. MUST NOT
  ser gravados, marcados como resolvidos ou dispensados no sistema. Eles mudam só quando a versão
  muda (`D-006`).

#### O canal desta fase e a integração futura

- **FR-1445**: A consulta MUST estar só na gestão, para quem alcança o Edital nela, com o mesmo alcance
  e a mesma negativa da página do Edital na gestão (`D-010`).
  - A tela MUST dizer que é validação interna e que nada dela é visto por candidatos.
  - A Fase A MUST NOT ter rota pública nem API pública.
- **FR-1446**: A mesma entrada — Edital, instante, pergunta, parâmetros e versão anterior informada —
  MUST produzir a mesma resposta, independentemente da tela que a pede e do estado da sessão.
- **FR-1447**: A Fase A MUST NOT chamar modelo de linguagem nem serviço externo. Também MUST NOT criar
  fila, worker, servidor ou rota para inferência.
- **FR-1448**: A consulta MUST poder ser executada fora da requisição da tela que a exibe, sem
  depender de sessão, para que a fase seguinte possa isolá-la, junto da inferência, da capacidade que
  serve as páginas públicas.
- **FR-1449**: A Fase A:
  - MUST NOT gravar nada: nem resposta, nem pergunta, nem ponto para revisão, nem cópia ou índice do
    conteúdo;
  - MUST NOT receber texto livre;
  - MUST NOT tratar dado pessoal.

#### A validação

- **FR-1450**: Os casos da matriz da auditoria pertinentes à Fase A MUST ser mantidos como casos
  verificáveis. São eles: `CA-01` a `CA-19`, `CA-27`, `CA-28` e `CA-29`, com os ajustes da tabela
  abaixo.

  Os casos rodam em duas camadas:

  - **Conteúdo.** O que depende só do conteúdo publicado roda sobre o conteúdo publicado dos Editais
    01, 91 e 92/2026 do corpus (`docs/libras/editais/*/fonte/`). Esse conteúdo foi publicado pelo
    fluxo real em 11/10/2026, e entra no teste como cópia versionada, sem banco.
  - **Banco.** O que depende de versão, fronteira de vigência, origem, desfecho ou Retificação não
    publicada roda sobre Editais publicados pelo fluxo real em ambiente de teste. Eles reproduzem
    esse corpus quando o conteúdo dele passa pelo fluxo; quando não passa, são Editais mínimos que
    reproduzem o fato de cada caso.

  Os casos que o corpus não tem — Edital com dois canais e Edital cancelado — usam Editais de teste
  próprios.

  | Caso | Na Fase A, pela pergunta |
  |---|---|
  | `CA-01`, `CA-03` | `P-03` |
  | `CA-02`, `CA-14`, `CA-17`, `CA-28`, `CA-29` | `P-01` |
  | `CA-04`, `CA-05`, `CA-06`, `CA-07`, `CA-15` | `P-05`; o critério é o texto pertinente inteiro no cartão |
  | `CA-08`, `CA-09`, `CA-13` | `P-07` |
  | `CA-10`, `CA-11` | `P-08` |
  | `CA-12` | `P-09` |
  | `CA-16` | qualquer resposta com seção: título, e não número |
  | `CA-18`, `CA-19` | `FR-1415` |
  | `CA-27` | `P-11` |

- **FR-1451**: A tela de conferência MUST permitir escolher um instante de referência, passado ou
  futuro, rotulado como tal, para validar fronteiras de vigência. Instante futuro MUST considerar só
  atos já publicados.

### Experiência

- **UX-200**: As três naturezas de cartão MUST se distinguir pelo rótulo em palavras, e não só por
  cor, ícone ou posição.
- **UX-201**: A identificação da versão MUST vir no topo da resposta. O aviso de mudança de versão
  MUST vir antes de qualquer conteúdo.
- **UX-202**: O tipo da resposta MUST vir em palavras, logo depois da versão.
- **UX-203**: Os pontos para revisão MUST ficar num bloco próprio, separado das respostas, com a
  explicação de que são questões a resolver antes da abertura pública.
- **UX-204**: A tela MUST:
  - funcionar com teclado e leitor de tela, com controles nativos e rótulos ligados;
  - anunciar a resposta nova;
  - caber em 375 px de largura sem rolagem horizontal;
  - abrir os cartões longos sob demanda, sem truncar o texto.
- **UX-205**: A tela MUST dizer que é validação interna das respostas do futuro assistente, e que nada
  dela é exibido a candidatos.

### Key Entities

- **Consulta**: Edital, instante, pergunta do catálogo, parâmetros e, opcionalmente, a versão da
  consulta anterior. Não é gravada.
- **Versão consultada**: a versão consolidada vigente no instante, com a publicação original, as
  Retificações aplicadas, o início da vigência e o identificador curto.
- **Pergunta sugerida**: entrada do catálogo fechado, com parâmetros, condição de oferta e seções
  pertinentes.
- **Resposta**: tipo, avisos, explicação e cartões, todos da mesma versão consultada.
- **Cartão de referência**: natureza (texto do Edital, dado da versão vigente ou explicação),
  conteúdo, localização no Edital, ato de origem e links de conferência.
- **Ponto para revisão**: condição detectada na versão vigente, com as fontes que a mostram. Derivado,
  não gravado.
- **Canal de atendimento**: o do Edital, com o parágrafo de origem, ou o institucional da implantação.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-530**: Os 22 casos de `FR-1450` passam, cada um na camada que a `FR-1450` lhe atribui, em cada
  versão e instante que o caso define. 100% deles.
- **SC-531**: Numa varredura de todas as perguntas aplicáveis, com todos os parâmetros, sobre os três
  Editais do corpus, em instantes antes e depois de cada fronteira de vigência, 100% das respostas têm
  todos os cartões e a explicação na mesma versão identificada.
- **SC-532**: Com uma Retificação em elaboração e outra homologada e não publicada sobre o mesmo
  Edital, nenhuma resposta muda. Zero diferenças.
- **SC-533**: 100% dos campos do conteúdo publicado aparecem em ao menos uma resposta do catálogo, ou
  constam de uma lista de excluídos com o motivo. Um campo novo, de feature futura, faz essa conferência
  falhar até ser classificado.
- **SC-534**: 100% dos cartões "Texto do Edital" são idênticos ao texto do conteúdo publicado. Zero
  frases geradas pelo compositor do documento aparecem rotuladas como "Texto do Edital".
- **SC-535**: Zero cartões levam a documento apresentado como "Edital completo". 100% dos links de
  documento levam ao documento de um ato que contém o valor citado. Isso é conferido nos dois cenários
  do achado.
- **SC-536**: Zero chamadas a modelo de linguagem ou a serviço externo durante a varredura do `SC-531`.
- **SC-537**: Para o maior Edital do corpus, a resposta aparece em até 2 segundos em 95% das consultas.
- **SC-538**: Uma pessoa do setor de seleção, pela gestão, sem banco nem shell:
  - escolhe um Edital publicado;
  - confere as respostas a todas as perguntas que se aplicam a ele;
  - segue cada link de cartão até o documento ou anexo;
  - lê os pontos para revisão.

  É o cenário demonstrável do princípio VI.
- **SC-539**: Nos Editais com canais divergentes ou cláusula de exclusividade, 100% dessas condições
  aparecem nos pontos para revisão, e nenhuma resposta escolhe um dos canais.

---

## Fases posteriores

O assistente é uma sequência de três fases. Esta spec é a primeira. As outras duas ficam
**registradas aqui** e na auditoria, e não especificadas.

| Fase | O que entrega | Depende de |
|---|---|---|
| **A — Fonte de consulta confiável** (esta spec) | Respostas determinísticas, com versão, natureza e origem, validadas internamente | — |
| **B — Piloto interno com o LLM local** | Pergunta livre sobre a mesma fonte, com a conferência da saída pela aplicação; avaliação com a matriz completa e medições na L4 | A concluída; confirmação do modelo e da GPU |
| **C — Interface pública e operação** | A entrada na página da seleção, os limites, os estados e a operação | B aprovada pelos limiares decididos; correção do achado; LGPD; texto de natureza não oficial; cláusulas de exclusividade resolvidas por Edital |

As listas de pendências de B e de C estão em
[O que esta fase entrega, e o que fica para depois](#o-que-esta-fase-entrega-e-o-que-fica-para-depois).

## Compatibilidade com a 069

A `069` está aberta em outra worktree, sem commit nem PR em 12/10/2026, e reescreve o Edital em PDF
em linguagem simples. As decisões dela citadas abaixo são as do cabeçalho daquela spec, pela ordem.

| Decisão da `069` | Efeito nesta spec |
|---|---|
| 1ª — linguagem simples no próprio ato; "não há versão complementar" | **Compatível.** Esta fase não compõe versão do Edital: não há leitura integral nem documento novo. A resposta é um recorte por pergunta, interno, com cartões que levam ao documento oficial |
| 10ª — LLM, portal, HTML→PDF e versão complementar fora do escopo dela | **Sem sobreposição.** O que ela exclui é o que esta fase e as seguintes tratam, e vice-versa |
| A reescrita das frases geradas | **Sem dependência.** Esta fase não reproduz as frases do compositor (`FR-1434`, `D-003`): mostra dados e explicação própria |
| Os achados herdados por ela (comprovante exigido só de um Perfil; sorteio condicionado no texto) | **Reproduzidos como declarados** nos casos `CA-07` e `CA-12`, sem correção — como ela também faz |

**Conflito remanescente, registrado e não resolvido.** Quando a `069` for publicada, o mesmo Edital
terá duas redações simples para a mesma regra:

- a do documento oficial, escrita pela `069`;
- a da explicação desta fase.

As duas dizem o mesmo valor, porque esta fase só usa valores dos cartões, mas podem usar palavras
diferentes. A revisão do vocabulário das explicações contra o da `069` entra como tarefa quando a
`069` for mergeada. Não é decisão desta spec alterar a dela.

---

## Decisões

### D-001 — A validação é interna, na gestão, e não há rota pública

**Decisão.** A consulta mora na gestão, no alcance da página do Edital. O ator é o setor de seleção.

**Por quê.** É o 1º do usuário: nada de interface pública prematura. E o princípio VI se cumpre pelo
canal desse ator: o setor faz algo novo, que é conferir o que o assistente vai dizer.

**Alternativa descartada.** Uma rota pública escondida atrás de uma chave: seria interface pública
com outro nome.

### D-002 — Catálogo fechado de perguntas, parâmetros do próprio Edital, nenhum texto livre

**Decisão.** Doze perguntas (`FR-1417`), oferecidas pelo conteúdo, com parâmetros escolhidos de
listas.

**Por quê.** Determinismo exige entrada fechada.

**Alternativa descartada.** Classificar texto livre por palavra-chave para cair numa pergunta. É
interpretação de linguagem sem modelo, e erraria em silêncio. A pergunta livre é a Fase B.

### D-003 — Três naturezas de cartão, e a explicação é do sistema

**Decisão.** Texto do Edital, dado e explicação. A explicação é escrita por esta feature, a partir só
dos valores dos cartões, e não reaproveita as frases do compositor do documento.

**Por quê.** As frases do compositor não estão no conteúdo publicado e mudam com o código. Apresentá-las
como texto do Edital afirmaria sobre o documento o que ele pode não dizer.

**Alternativa descartada.** Usar as frases do compositor como explicação, que amarraria esta fase à
reescrita da `069`.

### D-004 — A referência leva ao documento do ato que fixou o conteúdo, e nunca ao "Edital completo"

**Decisão.** Cada valor é ligado à publicação que o produziu: a original, ou a Retificação que o
alterou por último na ordem de vigência.

**Por quê.** O documento de um ato contém sempre os valores que esse ato fixou, porque é composto da
base dele mais as alterações dele. Já o documento da publicação de origem da versão vigente pode não
conter todos os atos — reproduzido no achado.

**O que fica de fora.** A correção do link "Ler o Edital completo (PDF)" da página pública. É
dependência da Fase C, e não escopo daqui (6º do usuário).

### D-005 — O canal é o do Edital; o institucional só na falta; a divergência não se resolve

**Decisão.** É o 4º do usuário, transcrito em `FR-1439` a `FR-1442`.

**Por quê o sistema não escolhe.** Escolher entre dois canais declarados é interpretar o ato, e o
erro mandaria a dúvida para o lugar errado.

### D-006 — Nada é gravado

**Decisão.** Respostas e pontos para revisão são derivados do conteúdo imutável, dos atos e do
instante.

**Por quê.** O conteúdo não muda, e uma derivação dele não envelhece. Gravar seria criar uma segunda
fonte editorial, o que o princípio II proíbe.

**O custo.** Ponto para revisão não pode ser marcado como resolvido aqui; ele some quando a
Retificação ou a decisão institucional muda a versão. Se a Fase C precisar de registro de prontidão
por Edital, ele nasce lá, com motivo e autoria.

### D-007 — A pertinência entre pergunta e seção é uma tabela declarada

**Decisão.** A tabela inicial está abaixo. O plano a revisa com o setor, e qualquer mudança é
alteração desta spec.

| Pergunta | Seções pertinentes, pela chave do catálogo |
|---|---|
| `P-01` | `inscricao` |
| `P-03` | `publico-alvo` |
| `P-04` | `requisitos-gerais`, `publico-alvo` |
| `P-05` | `inscricao`; com lista de concorrência que não seja a ampla, também `verificacao-autodeclaracao` e `atendimento-pcd` |
| `P-06` | `inscricao` |
| `P-07` | `classificacao` |
| `P-08` | `recursos` |
| `P-09` | `classificacao` |
| `P-10` | `convocacao`, `matricula` |
| `P-11` | as seções em que o canal for encontrado (`FR-1439`) |

**Por quê declarada, e não calculada.** Escolher seção por semelhança de texto é interpretar. Errar
para mais mostra texto a mais; errar para menos omitiria ressalva. A tabela erra para mais.

### D-008 — Divergência só onde o sistema compara

**Decisão.** Na Fase A, a única comparação é entre canais. Fontes de naturezas diferentes sobre o
mesmo assunto — o recurso do 91/2026 — são "Depende da leitura do Edital", e não "Fontes
divergentes".

**Por quê.** Afirmar divergência entre um dado e um parágrafo exigiria interpretar o parágrafo.

### D-009 — Instante de referência só na validação interna

**Decisão.** A tela de conferência aceita um instante escolhido.

**Por quê.** Validar uma fronteira de vigência não pode depender de esperar o calendário.

**O que não se decide aqui.** Nas fases seguintes, o visitante consulta sempre no instante presente;
isso é decisão delas.

### D-010 — O alcance da tela é o da página do Edital, sem capacidade nova

**Decisão.** A tela é alcançável por quem tem identidade da gestão no escopo institucional do
Edital, exatamente como a página do Edital (`interface/views.py`, `detalhe`). Fora do escopo, a mesma
negativa (404). Nenhuma capacidade nova é criada.

**Por quê.**

- **Negar por padrão continua valendo.** Sem identidade, a tela redireciona. Fora do escopo,
  recusa. O que muda é que, dentro do escopo, não se pede uma capacidade a mais.
- **A tela só lê conteúdo já público.** O conteúdo publicado e os documentos dos atos já estão no
  portal e na API pública, para qualquer pessoa. Uma capacidade para ler, na gestão, o que o portal
  mostra a todos protegeria o que não precisa de proteção.
- **Não grava nada nem pratica ato** (`FR-1449`). O princípio III exige autorização específica para
  criar, editar, revisar, homologar, publicar, retificar, cancelar, avaliar, julgar e divulgar. Nada
  disso acontece aqui.
- **É o precedente da página do Edital**, que mostra o mesmo conteúdo e os mesmos documentos com o
  mesmo alcance.

**O custo.** Qualquer pessoa da gestão, no escopo, vê os pontos para revisão de um Edital, inclusive
o documento de origem incompleto. Isso é informação sobre atos públicos, e não dado pessoal.

**Quando revisitar.** Se a Fase B passar a mostrar perguntas digitadas ou registros do piloto, isso é
dado de pessoas, e pede capacidade própria. A decisão é dela.

**Alternativa descartada.** Uma capacidade de leitura (`duvidas:conferir`) dada aos papéis do setor.
É mais um papel a manter, para ler o que é público.

---

## Assumptions

- **Os Editais do corpus são simulados.** Eles reproduzem o conteúdo publicado pelos roteiros do
  estudo de Libras e da auditoria do PDF. Editais reais entram no piloto (Fase B).
- **O alcance da tela é o da página do Edital na gestão** (`D-010`). Não há permissão nova: é leitura
  de conteúdo já público, por quem já o vê. A negativa nova, o 404 fora do escopo, entra no inventário
  de negativas.
- **A tabela de termos de dúvida e de exclusividade é fechada e pequena.** Falso positivo vira ponto
  para revisão a mais; falso negativo vira canal institucional no lugar do do Edital. Os dois são
  visíveis na validação.
- **A zona temporal é a institucional**, como em todo o sistema.
- **Sem dado pessoal.** Nenhuma pergunta digitada e nenhuma leitura de inscrição ou resultado. A LGPD
  não tem tratamento novo a avaliar nesta fase; a avaliação da Fase C continua necessária.
- **O desempenho é o de uma leitura da página do Edital.** O maior Edital do corpus tem algumas
  dezenas de milhares de caracteres de conteúdo.
