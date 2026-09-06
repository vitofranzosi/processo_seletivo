# Decisão 018 — o escopo institucional do Recurso

**Sessão de decisão conduzida em 06/09/2026**, sobre `0fdacd2` — a `main` com o PR #45 integrado.
**As sete decisões foram aprovadas pelo usuário em 06/09/2026**, na forma recomendada por este
documento. Nenhuma linha de código foi escrita, nenhuma migration foi criada, nenhuma spec
existente foi alterada e a SPEC 018 **não** foi aberta.

Este documento responde ao que a §10 de
[`descoberta-018-decisao-c-superacao-de-resultado.md`](descoberta-018-decisao-c-superacao-de-resultado.md)
deixou explicitamente aberto, mais as perguntas **A** e **B** da §14 do
[relatório da E2E-017](e2e/017-exploratoria/relatorio.md). São nove questões, e todas eram de
governança: a Constituição as reserva ao usuário, e nenhuma delas se decidia lendo código.

> **O que está aprovado é a §11**, e são sete decisões que fecham as nove questões — duas delas
> acompanham outras, e a §10 mostra por quê. As alternativas descartadas permanecem escritas de
> propósito: elas são a fundamentação da escolha, e é por elas que uma revisão futura saberá o que
> foi pesado e o que mudaria a conta.
>
> **Aprovar o escopo não autoriza implementação.** Nenhuma linha daqui vira requisito, tarefa ou
> migration antes de a SPEC 018 ser aberta, planejada e analisada pelo fluxo da Constituição.

---

## 0. O que já está fechado, e não volta a esta mesa

A decisão C está consolidada e esta sessão a **consome**, não a rediscute:

- `ResultadoEtapa` é superado por sucessor append-only — nunca alterado, anulado ou apagado;
- a decisão que fixa diretamente o resultado corrigido cria sucessor com origem **`RECURSO`**, que
  não cita Avaliação nenhuma;
- decisão e Resultado sucessor nascem **na mesma transação**;
- a decisão que ordena reavaliação **não** cria sucessor: quem o produz é a consolidação da nova
  Avaliação, depois.

Duas propriedades derivadas importam a quase todas as questões abaixo, e vale tê-las à mão:

1. **A cadeia a jusante reage sozinha.** Resultado novo entra no universo → `comparar()` emite
   `resultados_alterados` → o ato fica obsoleto → `aferir()`
   (`backend/processo_seletivo/divulgacao/domain/publicabilidade.py:102`) recusa a publicação e
   **nomeia o caminho** → ato sucessor → publicação sucessora → a Área do Candidato migra sozinha.
   Nada disso precisa ser construído.
2. **A correção é sempre ato humano autorizado.** A cascata é de **bloqueio**, não de recálculo
   (I-R6). Esta é a propriedade que sustenta as respostas às questões 7 e 8: onde falta um fato,
   o remédio do produto é impedir o ato seguinte, e não produzir um ato por conta própria.

---

## 1. Escopo objetivo — contra o que se recorre na V1

### O que hoje é fato

- **O Edital que o produto emite já promete recurso**, e promete um objeto específico: *"Caberá
  recurso contra os resultados divulgados, nos prazos do Cronograma"*
  (`backend/processo_seletivo/editais/domain/secoes.py:136`). Divulgado, hoje, só há
  **um** objeto: a `PublicacaoResultado` de um marco classificatório.
- **O objeto do recurso e o lugar do erro são eixos distintos.** A §4 da descoberta já mapeou os
  seis lugares onde o erro pode estar, e três deles são alcançados por remédios que a 015 e a 017
  **já entregam** (sucessor de ato, publicação sucessora, Retificação). Recorrer do resultado
  divulgado **não** evita a máquina da superação: um recurso cujo mérito é *"minha nota da Etapa 2
  está errada"* ataca a publicação e produz efeito no `ResultadoEtapa`.
- **`ResultadoEtapa` não é objeto de divulgação.** A 017 o pôs fora de escopo por decisão
  (D-002), e a FR-056 é explícita: existir `ResultadoEtapa` no banco não torna a informação
  pública. Quem foi eliminado antes do marco não vê **nada** — nem que houve resultado (E2E17-004).

Disso decorre o recorte real: a pergunta não é *"que tipo de erro a 018 corrige"* — a decisão C já
respondeu isso —, é **"que peça o candidato pode nomear ao recorrer"**.

### Alternativas

**1A — Objeto único: o resultado divulgado.**
Admite-se recurso contra a `PublicacaoResultado` vigente de um marco. O julgamento identifica onde
está o erro e aplica o remédio da §4 — superação do Resultado, sucessor de ato, publicação
sucessora ou encaminhamento normativo.

- *Jurídico:* é exatamente o que o Edital promete, sem ampliar nem restringir a promessa. O objeto
  é público, tem endereço estável, documento oficial e SHA-256 — a peça é inequívoca.
- *Operacional:* nenhuma tela nova de divulgação. O ciclo fecha nas superfícies que a E2E-017 já
  percorreu.
- *Técnico:* consome a decisão C inteira sem pré-requisito. Nenhuma elevação de `SCHEMA_VERSION`.
- *O custo, e ele é grave:* **quem foi eliminado antes do marco fica de fora do recurso**, porque
  não está no universo do ato e não vê nada de que recorrer. A 018 entregaria recurso exatamente a
  quem menos precisa dele, e reproduziria, dentro da feature de recurso, a injustiça que o
  E2E17-004 registrou. O produto passaria a prometer duas vezes o que continua não entregando.

**1B — Dois objetos: o resultado divulgado e o Resultado individual da Etapa.**
Admite-se recurso contra a publicação **e** contra o `ResultadoEtapa` vigente do par
Inscrição × Etapa. Exige resolver a visibilidade (questão 3), porque não se recorre do que não se
vê.

- *Jurídico:* cobre a eliminação em Etapa eliminatória, que é o ato de maior consequência
  individual do certame — e o único contra o qual, hoje, não há nem notícia nem defesa.
- *Operacional:* a comissão passa a receber recursos em dois momentos do ciclo, e não só ao fim.
  Recurso sobre Etapa 1 chega antes de a Etapa 2 começar, que é quando ele custa menos a executar.
- *Técnico:* custo condicionado à alternativa escolhida na questão 3 — 3B custa um seletor e uma
  superfície; 3C custa uma feature de divulgação inteira.

**1C — Objeto único e estreito: só o cálculo do ato classificatório.**
Admite-se recurso apenas contra ordem, desempate, modalidade aplicada e universo considerado, cujo
remédio é o sucessor de ato que a 015 já entrega.

- *Jurídico:* recusa o recurso mais comum dos certames reais — o que contesta a nota — e contradiz
  a promessa impressa no Edital, que fala em resultados divulgados sem restringir o fundamento.
- *Técnico:* a origem `RECURSO` e as constraints de sucessão da decisão C **nasceriam sem uso na
  V1**. Construir a primitiva e não a consumir é o oposto do princípio VI.

### Decisão — aprovada em 06/09/2026

**1B, condicionada a 3B.** É a única que entrega recurso a quem o certame elimina cedo, e a única
que consome a decisão C por inteiro. Ela só é barata porque a questão 3 tem uma resposta barata: se
a visibilidade exigisse a divulgação formal de resultado por Etapa (3C), a escolha teria sido 1A com
o custo declarado.

**A SPEC 018 admite, portanto, dois objetos de recurso**: a `PublicacaoResultado` vigente de um
marco e o `ResultadoEtapa` vigente do par Inscrição × Etapa. O julgamento identifica onde está o
erro e aplica o remédio da §4 da descoberta — que continua sendo o mapa, e não muda por esta
decisão.

---

## 2. Legitimidade — quem pode recorrer

### O que hoje é fato

- **Titularidade não é autorização, e o produto já sabe disso.**
  `backend/processo_seletivo/inscricoes/domain/titularidade.py` responde *"este registro é dele?"*
  comparando `inscricao.identity_subject` com o `subject` da sessão do portal, e recusa com **404**
  — não 403 — porque *"dizer 'existe, mas não é seu' já entrega que existe"*.
- **O candidato prova o controle de um e-mail, e nada mais.** Não tem papel, não tem escopo, não
  atravessa `require_permission`, e a 010 removeu de propósito o provedor que deixava alguém
  declarar quem era (`backend/processo_seletivo/portal/identidade.py`).
- **Não existe representação no domínio.** Não há procuração, não há terceiro identificado, não há
  vínculo entre uma identidade e a inscrição de outra pessoa. `identity_subject` **é** a
  propriedade.
- **O que um terceiro consegue ver hoje** é a página pública: nome, protocolo, modalidade, posição
  e pontuação de quem foi classificado. É suficiente para nomear uma peça e um interessado.

### Alternativas

**2A — Somente o próprio candidato, titular da Inscrição.**
- *Jurídico:* o recurso administrativo é do interessado, e o titular é inequivocamente interessado.
  Não fecha nenhuma porta: impugnação de terceiro continua possível **fora** do produto, pelos meios
  que a instituição já usa.
- *Operacional:* nada muda no acesso. Quem recorre é quem entra com o próprio e-mail.
- *Técnico:* custo zero de autorização — `exigir_titularidade` já é a porta, e ela já existe.
- *Custo:* a impugnação por concorrente — comum em cotas e heteroidentificação — permanece um
  controle paralelo, exatamente o que o produto veio fechar.

**2B — Titular e terceiro interessado.**
- *Jurídico:* **exige contraditório**. Uma impugnação de terceiro que possa piorar a situação de
  alguém sem que esse alguém seja ouvido é indefensável. Contraditório exige notificar o impugnado
  e receber manifestação dele — e o produto **não tem comunicação ativa** (relatório da E2E-017,
  §1: *"ninguém é notificado"*). Sem notificação, o impugnado descobriria por acaso, se descobrisse.
- *Operacional:* dobra o fluxo — interposição, notificação, prazo de manifestação, manifestação,
  julgamento — e cria a superfície que hoje não existe em canal nenhum.
- *Técnico:* precisa de identidade de terceiro no portal (hoje só há candidato titular), de objeto
  nomeável por quem não é titular, e do canal de notificação. É uma feature própria, e maior que a
  018.

**2C — Titular e representante/procurador.**
- *Jurídico:* legítimo e às vezes necessário — mas o instrumento de mandato é documento a receber,
  validar e guardar, com dado pessoal de um terceiro que não é candidato (LGPD: nova finalidade,
  nova base).
- *Operacional:* alguém precisa conferir a procuração antes de admitir o recurso — passo humano
  novo, com sua própria decisão de admissibilidade.
- *Técnico:* nova entidade de representação, nova classe de documento, e a quebra da equação
  `identity_subject = titular` que sustenta toda a autorização do portal. **É a alteração de maior
  raio desta lista**, e não por causa do recurso.

### Decisão — aprovada em 06/09/2026

**2A para a V1.** Não porque terceiro e procurador sejam ilegítimos, mas porque cada um dos dois
arrasta uma capacidade que o produto ainda não tem — notificação num caso, representação no outro —
e nenhuma das duas é do escopo do recurso.

Duas notas para não fechar portas por omissão:

- **2A é coerente com a decisão da questão 6** e 2B não é: *non reformatio in pejus* protege
  quem recorre do próprio recurso, e a impugnação de terceiro é justamente o caminho legítimo pelo
  qual a situação de alguém piora. Adotar 2B sem contraditório seria adotar a piora sem defesa.
- **Se a representação vier depois**, a forma natural é a interposição **registrada pela
  instituição**, com identificação do representante e do instrumento no próprio ato — e não login
  delegado. Delegar sessão apagaria a autoria, que é o que a trilha existe para provar.

---

## 3. Visibilidade — a decisão B

> *Qual fato institucional autoriza mostrar ao candidato o seu Resultado individual da Etapa?*

### O que hoje é fato

- A Área do Candidato lê `SituacaoDivulgada`, e só existe linha para quem estava **no universo do
  ato** (`backend/processo_seletivo/divulgacao/application/selectors.py:87`, filtrando
  `publicacao__sucessoras__isnull=True`).
- **FR-056 da 017** é a regra vigente: nada de resultado aparece antes da publicação; existir
  `ResultadoEtapa` no banco não torna a informação pública.
- **O marco enumera suas Etapas na norma publicada.** `marco["stages"]` é conteúdo normativo, lido
  por `backend/processo_seletivo/classificacao/domain/universo.py:26` e por
  `combinacao.py:109`. Isso é decisivo: existe um fato **normativo** — e não derivado de quem
  entrou no universo — que liga um marco publicado às Etapas que ele conta.
- **O que Helena viu**, no cenário da E2E-017: "✓ Inscrição enviada" e o cronograma. Nem o
  Indeferimento da Etapa 1, nem que houve resultado, nem que o processo avançou.

### Alternativas

**3A — Nada muda: só quem está no universo vê alguma coisa.**
- *Jurídico:* o silêncio absoluto sobre um ato que eliminou a pessoa é o oposto da motivação dos
  atos administrativos. O `motivo` do Resultado existe, é obrigatório por constraint
  (`ck_resultado_motivo_presente`) e é escrito para ser lido — *"pontuação inferior à nota mínima
  da Etapa (45,0000 < 60,0000)"* — e ninguém o lê.
- *Operacional:* o eliminado cedo continua a procurar a instituição por fora.
- *Técnico:* custo zero, e fecha a questão 1 na alternativa 1A.

**3B — O fato autorizador é a publicação vigente do marco que enumera aquela Etapa.**
Havendo `PublicacaoResultado` **vigente** de um marco do Perfil da Inscrição, e enumerando o marco
a Etapa N, o titular passa a ver, **dentro da própria inscrição**, o seu `ResultadoEtapa` **vigente**
da Etapa N: consequência, motivo e — quando a forma a tiver — pontuação. Não é divulgação pública,
não é ato novo, não nomeia terceiros.

- *Jurídico:* o fato autorizador é um **ato administrativo que já existe**, já tem autoridade
  (`resultado:publicar`), autor, instante e documento. A instituição já decidiu tornar público o
  resultado daquele marco; mostrar ao titular o insumo individual do próprio marco não amplia a
  decisão dela — dá a ela o alcance que a motivação exige. E é acesso do titular ao próprio dado,
  que a LGPD favorece, e não divulgação de dado alheio.
- *Operacional:* **alcança quem ficou fora do universo**, e é essa a propriedade que a torna a
  resposta certa. Helena pertence ao Perfil, o marco do Perfil foi publicado, o marco enumera a
  Etapa 1, e ela passa a ver o próprio Indeferimento com o motivo escrito. Fecha o E2E17-004 pela
  raiz, e não pelo aviso genérico que o relatório sugeria como mínimo.
- *Técnico:* um seletor com dois filtros — publicação vigente do marco, Etapa enumerada — e uma
  superfície no portal. **Nenhuma migration, nenhum `SCHEMA_VERSION`, nenhum conteúdo publicado
  novo.** Ajusta FR-056 sem contradizê-la: continua sendo a publicação que abre a porta; o que muda
  é a largura da porta.
- *Cuidado a registrar:* o que se mostra é o **vigente**, sempre, e a superação precisa ser
  explicável a quem a recebe — *"a sua nota mudou porque o seu recurso foi deferido"* — porque
  mostrar sem explicar transforma a correção em erro aparente.

**3C — O Resultado da Etapa vira objeto próprio de divulgação.**
Ato de divulgação por Etapa, com autoridade, natureza, documento e endereço próprios.
- *Jurídico:* a forma mais completa, e a que alguns Editais realmente praticam (resultado
  preliminar por etapa).
- *Operacional/técnico:* é uma feature inteira, que a 017 excluiu por decisão (D-002: *"Publicação
  de `ResultadoEtapa` e qualquer abstração genérica de publicável"*). Reabri-la dentro da 018 faria
  a 018 conter duas features.

### Decisão — aprovada em 06/09/2026

**3B.** É o fato mais barato que é verdadeiro: a autorização vem de um ato que já existe, o
alcance inclui quem foi eliminado cedo, e o custo é um seletor e uma tela. É também o que torna
**1B** viável — e, com isso, o par (1B, 3B) é a combinação que entrega recurso a todos os
candidatos do Perfil, e não só aos que chegaram ao fim.

**Consequência para a 017:** a FR-056 continua verdadeira no que ela protege — é a publicação que
abre a porta, e existir `ResultadoEtapa` no banco continua não tornando nada público. O que muda é
a largura da porta, e quem a alarga é a SPEC 018, no seu próprio texto. Esta decisão **não**
retroage sobre a 017, que permanece como está.

**Sobre a hipótese de A e B compartilharem primitiva** (§14 do relatório): a verificação foi feita
e a resposta é **não**. B se ancora num fato que **já existe** — a publicação vigente do marco.
A definitividade (questão 8) se ancora em fatos que **ainda não existem** — prazo encerrado e
inexistência de recurso pendente. São marcos temporais distintos, e tratá-los como um só teria
adiado B até que o prazo estruturado existisse, sem necessidade nenhuma.

---

## 4. Prazo — o que abre e o que fecha a janela recursal

### O que hoje é fato

- **Não existe prazo recursal estruturado.** A seção "Dos Recursos" é textual, e
  `EventoCronograma.type` é `CharField` livre, sem validação. O próprio modelo registra por que não
  se deve inferir dali: *"inferir o período dali seria decidir uma regra de direito lendo o que
  alguém digitou"* (`backend/processo_seletivo/editais/models/cronograma.py:32-36`).
- **Existe precedente exato de marca estrutural**: `is_registration_period`, um booleano no Evento
  com `UniqueConstraint` parcial por Cronograma (`cronograma.py:37` e
  `uq_evento_periodo_de_inscricoes`).
- **Conteúdo normativo novo tem preço conhecido**: `SCHEMA_VERSION` é **7**
  (`backend/processo_seletivo/shared/canonical.py:73`), e cada degrau exige uma entrada em
  `publicacoes/domain/elevacao.py` declarando **o que a ausência significa** nos Editais anteriores
  — a `DEGRAUS_DE_PERFIL`/`DEGRAUS_DA_RAIZ` do degrau 7 é o molde.
- **A 017 já decidiu o que fazer sem prazo declarado**, e decidiu bem: *"Publicação preliminar cujo
  Edital não declara prazo de recurso: não se inventa prazo nem botão"* (FR-055 e Edge Cases).
- **A E2E-017 mostrou o modo de falha de marca booleana em Evento**: no E2E17-001, a marca do
  período de inscrições era apagada em silêncio por gravação posterior do assistente. Marca em
  Evento é forma que já falhou uma vez neste produto.

### Por que texto livre não pode virar regra

Três razões, e cada uma sozinha basta:

1. **`type` não é validado por nada.** Ler regra de direito de um campo que aceita qualquer string
   é decidir por digitação.
2. **O princípio II exige reprodutibilidade.** O estado normativo vigente em qualquer instante deve
   ser reproduzível; uma janela inferida por heurística de texto responde coisas diferentes conforme
   a heurística evolua, sobre o mesmo conteúdo publicado e o mesmo hash.
3. **A recusa tem de ser defensável.** Recusar um recurso por intempestividade é ato que restringe
   direito. Fundamentá-lo em *"o Evento cujo `type` continha a palavra recurso"* é indefensável na
   primeira contestação.

### Estrutura normativa mínima

Qualquer alternativa que compute o prazo precisa, no mínimo, declarar:

1. **que há recurso admitido** naquele marco — e não em geral no Edital;
2. **quanto dura** a janela, e em que unidade (dias corridos ou úteis);
3. **de que instante ela conta** — o fato âncora;
4. **em que zona temporal** o dia vira — o princípio II exige a zona institucional, não a do
   servidor;
5. **o que a ausência significa** nos Editais publicados antes do degrau.

### Alternativas

**4A — Janela declarada por marco, ancorada na publicação.**
O conteúdo publicado do marco ganha a declaração da janela (admite recurso, duração, unidade). A
janela **abre** no instante de publicação da `PublicacaoResultado` vigente daquele marco — instante
que o sistema já grava e já exibe — e **fecha** ao fim da duração declarada, na zona institucional.
- *Jurídico:* o prazo conta do ato que o candidato pode conhecer, que é a regra geral do processo
  administrativo. E funciona na sucessão: publicada uma sucessora que altera a ordem, a janela conta
  da nova — que é o resultado correto, porque contra o conteúdo novo ninguém recorreu ainda.
- *Operacional:* o elaborador declara uma duração, não datas. Publicação atrasada não produz prazo
  vencido antes de existir, que é o modo de falha mais comum dos cronogramas reais.
- *Técnico:* degrau 8 em `elevacao.py` (ausência = janela não declarada), elevação de
  `SCHEMA_VERSION` para 8, campos de escrita no assistente e no catálogo de Retificação, e uma
  função de contagem com a zona institucional. **O maior custo técnico das nove questões.**

**4B — Evento de Cronograma marcado (`is_appeal_period`).**
Espelha `is_registration_period`: booleano no Evento, com `start_at`/`end_at` explícitos.
- *Jurídico:* datas absolutas descolam-se do ato. Publicado o resultado depois da data marcada, a
  janela nasce vencida e a instituição precisa de Retificação para corrigir um prazo que só existiu
  no papel.
- *Operacional:* um Edital com vários marcos precisa de várias janelas, e a unicidade teria de ser
  por `(cronograma, marco)` — o que obriga o Evento a **referenciar o marco**, coisa que
  `EventoCronograma` não faz hoje e que a torna menos parecida com o precedente do que parece.
- *Técnico:* custo comparável ao de 4A, com o modo de falha do E2E17-001 já demonstrado neste
  produto para marca booleana em Evento.

**4C — Nada estruturado: o prazo continua texto, e o limite é humano.**
A interposição permanece aberta enquanto a publicação for vigente; a tempestividade é decidida na
**admissibilidade**, por quem julga, com motivo escrito.
- *Jurídico:* honesto e auditável — a recusa por intempestividade passa a ser ato motivado de uma
  autoridade, e não regra inventada pelo sistema. É como o produto já trata o que não sabe.
- *Operacional:* alguém precisa julgar tempestividade caso a caso; e o candidato não vê, no
  produto, até quando pode recorrer.
- *Técnico:* custo zero. **Mas fecha uma porta na questão 8:** sem prazo computável, "definitiva"
  nunca poderá ser justificada por *"o prazo acabou"*.

### Decisão — aprovada em 06/09/2026

**4A, com o comportamento de 4C como degradação declarada.** Ou seja: o Edital que declarar a
janela tem o prazo computado, exibido ao candidato e verificado na interposição; o Edital que não
declarar mantém a interposição aberta e a tempestividade como juízo de admissibilidade motivado.
Esta é a forma que o produto já usa em toda parte — computa o que a norma declarou, e recusa-se a
inventar o que ela não declarou (FR-055 da 017 dita como comportamento).

**Se o custo do degrau 8 for considerado alto para a V1**, 4C é aceitável **desde que** a questão 8
seja respondida com 8B, que não depende do prazo computável. O que não é aceitável é 4C com uma
definitividade que afirme prazo encerrado sem ter como sabê-lo — seria o E2E17-005 de novo, com
mais passos.

---

## 5. Julgamento — quem decide, e quem não pode decidir

### O que hoje é fato

- **A Constituição nomeia "julgamento de recurso" entre as operações que exigem autorização
  específica** (Princípio III). Não é interpretação: está escrito.
- **Não existe permissão de julgamento.** O mapa de papéis tem `edital:*`, `retificacao:*`,
  `resultado:publicar`, `inscricao:consultar`, `processo:*`, `comissao:gerir` e
  `auditoria:consultar` (`backend/processo_seletivo/interface/identidade.py`). A presidência **não
  é papel** — é vínculo, verificado objeto a objeto.
- **A 017 já resolveu o caso simétrico, e resolveu por capacidade.** A D-004 separa constituir de
  divulgar: *"proíbe-se que a autorização para publicar **derive** de ter emitido"*. `resultado:publicar`
  é capacidade no mapa, e não consequência da autoria.
- **A comissão é uma só, com duas funções** — `PRESIDENTE` e `MEMBRO`
  (`backend/processo_seletivo/comissoes/models.py`). Não há comissão recursal, e não há tipo de
  comissão.
- **O `Impedimento` existe**, ancorado em pessoa × inscrição (`uq_impedimento_pessoa_inscricao`), e
  a 012 o deixou **fora** da cadeia de autorização de propósito: consultá-lo custaria uma
  verificação por linha em toda listagem. **Julgamento é ponto único, não listagem** — o custo que
  a 012 recusou não se coloca aqui.
- **O autor de cada ato está gravado**: `avaliacao.concluida_por`, `resultado.consolidado_por`,
  `ato.emitido_por`. As quatro consultas de impedimento são diretas.

### Alternativas

**5A — Julga a presidência da comissão, por vínculo.**
- *Jurídico:* em comissões pequenas, a presidência frequentemente avaliou. Julgar recurso contra a
  própria avaliação — ou contra a consolidação que ela mesma praticou — é vício de imparcialidade
  que nenhum motivo escrito conserta.
- *Operacional:* nenhuma configuração nova; funciona no dia um.
- *Técnico:* reaproveita `comissao:presidir`. Custo mínimo, e concentração máxima.

**5B — Capacidade sistêmica nova `recurso:julgar`, com impedimento que bloqueia.**
Quem julga detém a capacidade no mapa de papéis — podendo ser a presidência, mas **não por ser**
presidência. E é impedido de julgar quem: concluiu a Avaliação fonte; consolidou o Resultado
atacado; emitiu o ato atacado; ou tem `Impedimento` registrado para aquela inscrição.
- *Jurídico:* é a leitura literal do Princípio III, e reaplica a arquitetura que a 017 escolheu
  para o caso simétrico. O impedimento **bloqueia**, e não apenas declara — porque decisão de quem
  está impedido é decisão viciada, e declará-lo depois repete o padrão do E2E17-005: um ato que
  afirma o que não tem.
- *Operacional:* a instituição precisa conceder o papel a alguém. Em comissão pequena, o
  impedimento pode não deixar ninguém elegível — e a saída é institucional, não técnica: sendo
  capacidade do mapa, ela é concedida a quem está fora da comissão (autoridade signatária,
  direção). Foi exatamente assim que `resultado:publicar` resolveu o mesmo aperto.
- *Técnico:* uma permissão no mapa, quatro consultas pontuais na porta do comando, e o
  `Impedimento` finalmente lido em algum lugar da cadeia de autorização.

**5C — Comissão recursal própria.**
Segunda comissão, com composição, alocação e telas próprias.
- *Jurídico:* é a forma mais fiel aos certames de grande porte, e nenhum dos Editais lidos a impõe.
- *Operacional:* mais um ato de constituição antes de julgar o primeiro recurso.
- *Técnico:* entidade nova, fluxo de composição novo, telas novas. O Princípio V pede a solução
  mais simples que preserve os requisitos, e 5B preserva todos.

### Decisão — aprovada em 06/09/2026

**5B**, com o impedimento bloqueando. E uma nota de escopo: **o impedimento recursal é o mesmo
conceito do `Impedimento` da 012** — "esta pessoa não decide sobre esta inscrição" — ampliado do
avaliar para o julgar. Criar um segundo conceito ao lado dele seria a linguagem ubíqua se partindo
em dois pelo canal em que a pergunta é feita, que é o que o Princípio I proíbe.

---

## 6. *Non reformatio in pejus*

### O que hoje é fato

- **O modelo não restringe nada.** Nenhuma constraint em `ResultadoEtapa` impede que o sucessor
  seja pior que o superado.
- **A 013 registra o precedente de como tratar isto:** ao decidir não transformar em constraint que
  a Ocorrência sempre elimina — *"que atos a V1 permite é política"*.
- **A Lei 9.784/99, art. 64, parágrafo único**, admite o agravamento em recurso administrativo,
  **desde que o interessado seja cientificado para formular alegações antes da decisão**. Muitos
  Editais o vedam expressamente; a lei o condiciona.
- **O produto não tem comunicação ativa.** Nenhum canal notifica ninguém (relatório da E2E-017,
  §1). Cientificar previamente, hoje, é impossível dentro do produto.

### O que "piorar" precisa significar

Duas grandezas, e uma exclusão que evita confusão futura:

- **consequência** — `HABILITADA` virar `ELIMINADA`;
- **pontuação** — nota do sucessor menor que a do superado;
- **e não a posição.** O deferimento do recurso de outra pessoa pode empurrar o recorrente para
  baixo na ordem. Isso **não** é *reformatio in pejus*: a garantia protege quem recorre do efeito
  do **próprio** recurso sobre o **próprio** objeto, e não do efeito dos atos alheios sobre a
  classificação. Dizer o contrário congelaria a ordem inteira ao primeiro recurso.

### Alternativas

**6A — Vedado piorar, na V1.**
O julgamento que concluir por situação pior que a vigente resulta em **indeferimento**: o Resultado
vigente permanece, e nenhum sucessor nasce. Erro em desfavor do candidato descoberto no julgamento
é matéria de revisão de ofício — ato próprio, com sua própria motivação —, e não efeito do recurso
dele.
- *Jurídico:* compatível com a lei (que faculta o agravamento, não o impõe) e com a prática da
  maioria dos Editais. Remove o efeito dissuasório: ninguém deixa de recorrer com medo.
- *Operacional:* simples de explicar em uma frase, na tela e no Edital.
- *Técnico:* verificação no comando de julgamento, comparando consequência e pontuação do sucessor
  com as do superado. **Regra de política, e por isso no comando e no teste — não em constraint**:
  o esquema precisa continuar admitindo o sucessor pior, porque a instituição pode adotar 6B depois
  e porque a revisão de ofício produzirá exatamente esse sucessor.

**6B — Permitido piorar, com contraditório prévio.**
- *Jurídico:* é a forma que a lei desenha, e a mais completa.
- *Operacional/técnico:* **não é implementável na V1.** Exige cientificar o recorrente e receber
  manifestação antes de decidir, e o canal não existe. Sem ele, 6B degenera em 6C.

**6C — Permitido piorar, sem contraditório.**
- *Jurídico:* indefensável. Nomeada aqui apenas para que a omissão não a produza por acidente: é o
  que se obtém adotando 6B sem construir a notificação.

### Decisão — aprovada em 06/09/2026

**6A**, com uma trava que a torna íntegra: **a vedação alcança também o sucessor produzido pela
reavaliação ordenada no recurso**. Sem isso, 6A é contornável pelo caminho mais curto — basta
ordenar reavaliação em vez de fixar a nota, e a piora entra pela porta de trás com origem
`AVALIACAO`. A reavaliação que produzir resultado pior que o superado é registrada, e não
consolidada como sucessor: quem consolidaria estaria executando, por outro caminho, a decisão que
6A veda.

---

## 7. Progressão retroativa — a Etapa seguinte já encerrada

### O que hoje é fato

- **Não existe Etapa "encerrada".** Não há estado, não há ato de encerramento, não há coluna.
  Participação e prontidão são **derivadas**, por inscrição, dos Resultados vigentes
  (`backend/processo_seletivo/resultados/application/prontidao.py`). Uma Etapa está terminada
  porque todos têm Resultado, e não porque alguém a fechou.
- **A superação devolve a inscrição ao conjunto sozinha.** Removida a eliminação vigente, o
  `~Exists` da regra 1 deixa de excluí-la e ela reaparece como `PENDENTE` na Etapa seguinte — na
  Mesa, na distribuição, na prontidão e nos números do painel.
- **Distribuir, avaliar e consolidar tardiamente já existem.** Nenhuma operação nova é necessária
  para executar a progressão retroativa.
- **O ato de ordenação percebe.** Passando ela a participar, o conjunto de `stageResults` do
  recálculo difere do gravado, `comparar()` emite `resultados_alterados` e a publicação é recusada
  com caminho nomeado.
- **Nenhuma vaga está ocupada.** Convocação, aceite, posse e matrícula são da 019, que não existe.
  **Este é o momento mais barato da vida do produto para admitir progressão retroativa** — depois da
  019, ela disputa vaga com quem já foi convocado.

### Alternativas

**7A — Efeito pleno, automático.**
A inscrição reabilitada reentra como `PENDENTE` em todas as Etapas seguintes e segue o fluxo normal.
- *Jurídico:* é o que restitui o candidato ao estado em que estaria se o erro não tivesse ocorrido,
  que é a finalidade do deferimento. Qualquer coisa menos que isso torna o deferimento simbólico.
- *Operacional:* **é o item de maior consequência da lista.** Uma Etapa que todos consideravam
  terminada volta a ter linha pendente; a comissão precisa distribuir, avaliar e consolidar; e
  ninguém é avisado. Sem sinalização, isso é descoberto por acaso.
- *Técnico:* nada a construir para o efeito. O trabalho é de **aviso**, não de mecanismo.

**7B — Efeito limitado à Etapa do recurso, salvo decisão expressa em contrário.**
- *Jurídico:* reconhece o erro e nega a consequência dele. Precisa de fundamento que os Editais
  lidos não dão.
- *Técnico:* **mais caro do que parece, e potencialmente desonesto.** Progressão é derivada do
  Resultado vigente; limitar o efeito exigiria ou um sinalizador na decisão que a prontidão
  consultasse — a segunda fonte que o Princípio II proíbe, e exatamente a forma pela qual a
  alternativa 3 da decisão C foi descartada —, ou um Resultado por Ocorrência na Etapa seguinte
  declarando a não participação. O segundo caminho é representável, mas o vocabulário de
  `Consequencia` só tem `HABILITADA` e `ELIMINADA`: registrar-se-ia "eliminada" numa Etapa que a
  pessoa nunca fez. **O registro passaria a afirmar algo falso**, que é o motivo pelo qual a §1.2 da
  decisão C recusou a Avaliação sintética.

**7C — Efeito pleno, com impedimento de publicação enquanto houver pendência reaberta.**
7A mais uma recusa: enquanto existir inscrição reabilitada por recurso e ainda `PENDENTE` numa Etapa
que o marco enumera, a publicação daquele marco é **impedida**, com motivo nomeado.
- *Jurídico:* impede que a instituição divulgue como definitiva uma ordem que omite quem teve o
  direito reconhecido. É a lição do E2E17-005 aplicada preventivamente.
- *Operacional:* a recusa é o aviso. Quem tenta publicar descobre, na hora, o que falta — e o
  produto já sabe recusar assim, nomeando o caminho.
- *Técnico:* mais um código de impedimento em
  `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`, ao lado de
  `publication_act_stale`. A máquina existe inteira; acrescenta-se um degrau.

### Decisão — aprovada em 06/09/2026

**7A com a guarda de 7C**, e três avisos operacionais que não são decoração:

1. **na Mesa e no painel da Etapa**, a linha reaberta é nomeada como tal — *"reabilitada por recurso
   deferido em DD/MM"* — e não aparece como uma pendência qualquer que ninguém explica;
2. **na tela do marco**, a divergência de obsolescência diz a causa certa: participante reingressou,
   e não apenas "resultados alterados";
3. **na prévia de publicação**, o impedimento de 7C, com o caminho a seguir.

**7B fica registrada como possível, e fora da V1**: limitar o efeito é decisão que a instituição
pode tomar por ato próprio, e representá-la honestamente exige vocabulário que o domínio não tem.
Inventá-lo dentro da 018 seria fazer a 018 conter uma segunda decisão de domínio.

---

## 8. Definitividade — a decisão A

> *Qual fato institucional torna uma publicação definitiva?*

### O que hoje é fato

- **É escolha livre de um `<select>`.** `publicar_resultado` valida que a natureza está entre as
  declaradas e que não há regressão `DEFINITIVA → PRELIMINAR`, e nada mais (E2E17-005). Na
  auditoria, P2 foi publicada como definitiva imediatamente após P1 preliminar, sem prazo decorrido
  e sem qualquer outro ato.
- **A 017 separou definitiva de homologada de propósito** (D-003): são duas naturezas, e homologação
  de resultado não foi implementada. Definitividade **não** é homologação.
- **`aferir()` é o lugar onde a verificação cabe**, e hoje ela não conhece a natureza — o comando
  decide a natureza depois. Verificar definitividade exige que a aferição passe a receber a natureza
  pretendida.

### Os fatos candidatos

1. **o prazo recursal encerrou** — depende da questão 4; indisponível quando não declarado;
2. **não há recurso pendente** sobre o marco — `INTERPOSTO`/`ADMITIDO` ainda não julgados;
3. **não há reavaliação determinada e não concluída** — o estado intermediário legítimo do
   caminho (b) da §1.3 da decisão C;
4. **o ato não está obsoleto** — a 017 já verifica.

### Alternativas

**8A — Nada muda: a natureza continua sendo escolha do publicador.**
- Construir a entidade Recurso e não consumir o fato que ela produz seria deixar o E2E17-005 aberto
  tendo em mãos, pela primeira vez, o que fecha metade dele. Descartada por isso.

**8B — Verificar os fatos 2 e 3; o prazo é verificado quando computável e declarado quando não.**
Enquanto houver recurso pendente ou reavaliação determinada e não concluída sobre o marco, a
publicação **`DEFINITIVA` é impedida** — a `PRELIMINAR` continua livre. Havendo janela estruturada
(4A), a janela aberta também impede. Não havendo, o publicador **declara**, no próprio ato, que o
prazo se encerrou — declaração com autor, instante e texto, gravada na publicação.
- *Jurídico:* converte a afirmação sem lastro em ato com dois fatos verificados e um fato declarado
  sob responsabilidade nominal. Declaração registrada e auditável é coisa diferente de uma opção de
  `<select>`.
- *Operacional:* o publicador não precisa saber se há recurso pendente — o sistema recusa e diz
  qual. É a mesma ergonomia da recusa por ato obsoleto, que a E2E-017 aprovou.
- *Técnico:* natureza pretendida chega a `aferir()`; dois `Exists` sobre a entidade Recurso;
  um campo de declaração na publicação. **Degrada corretamente** para Editais publicados antes do
  degrau 8, que nunca declararam janela e não podem ser punidos por isso.

**8C — Exigir os três fatos verificados; sem prazo estruturado não há publicação definitiva.**
- *Jurídico:* o mais rigoroso, e injusto com o passado: todo Edital anterior ao degrau 8 ficaria
  permanentemente impedido de ter resultado definitivo, por não declarar o que não existia para ser
  declarado. É a mesma classe de problema que `elevacao.py` foi escrito para evitar.

### Decisão — aprovada em 06/09/2026

**8B.** É a única que fecha o E2E17-005 sem inventar regra a partir de texto livre e sem punir o
conteúdo já publicado.

### 9 embutida — como se chama a definitiva que corrige uma definitiva

Recurso deferido depois de uma publicação já definitiva: `DEFINITIVA → PRELIMINAR` é proibida, e a
sucessora só pode ser outra definitiva. Três formas:

- **9A — a segunda definitiva basta, sem vocabulário novo.** A cadeia já diz que sucedeu, e o
  `motivo_da_sucessao` do ato de origem diz por quê. Custo zero; o leitor precisa percorrer a cadeia
  para saber que houve retificação.
- **9B — natureza nova `DEFINITIVA_RETIFICADA`.** Nomeia o ato no título e no PDF. Custo: terceiro
  valor no enum, a regra de não regressão passa a ter três pares a decidir,
  `uq_publicacao_por_ato_natureza` ganha um valor, e toda leitura de natureza muda.
- **9C — uma natureza só, e o nome vem do fato.** Mantém `DEFINITIVA`; a definitiva que sucede outra
  definitiva **exibe a causa em destaque** — *"Resultado definitivo, retificado em DD/MM em razão do
  julgamento do recurso R"* —, texto derivado da cadeia e do motivo, e não de coluna nova.

**Decisão — aprovada em 06/09/2026: 9C.** É o idioma do projeto — vigência e natureza derivam da cadeia, e não de estado
duplicado (é a razão pela qual `ResultadoEtapa` não ganha coluna de vigência). E resolve, de
carona, a oportunidade nº 3 do relatório da E2E-017: hoje P1 diz que foi sucedida e P2 não diz que é
a vigente.

---

## 10. Como as nove se encaixam

```text
Q1 escopo ──requer──▶ Q3 visibilidade        (1B só é viável com 3B ou 3C)
Q2 legitimidade ──coerência──▶ Q6 pejus      (2B sem contraditório contradiz 6A)
Q4 prazo ──habilita──▶ Q8 definitividade     (o fato 1 só existe com 4A)
Q5 julgamento ── independente
Q7 retroativa ──usa──▶ a guarda de publicação, que Q8 também usa
Q8 definitividade ──▶ Q9 nome da retificação (a forma segue o que a natureza afirma)
```

Duas questões não precisam de resposta própria: **Q3 acompanha Q1** (cada opção de escopo já diz de
que visibilidade ela depende) e **Q9 acompanha Q8** (o nome segue o que a definitividade afirma). Por
isso a §11 tem sete decisões, e não nove.

---

## 11. As sete decisões

**Aprovadas em 06/09/2026**, todas na forma recomendada. A coluna das alternativas preserva o que
foi descartado: é a fundamentação da escolha, e é por ela que uma revisão futura saberá o que
mudaria a conta.

| # | Questão | Alternativas consideradas | Decidida |
|---|---|---|---|
| **1** | **Contra o que se recorre na V1** | **(a)** só o resultado divulgado — e quem foi eliminado antes do marco fica sem recurso · **(b)** o resultado divulgado **e** o Resultado individual da Etapa, com a visibilidade de 3B · **(c)** só o cálculo do ato classificatório | **(b)** |
| **2** | **Quem pode recorrer** | **(a)** só o titular da Inscrição · **(b)** também terceiro interessado (exige notificação, que não existe) · **(c)** também procurador (exige representação no domínio) | **(a)** |
| **3** | **Prazo recursal** | **(a)** janela declarada por marco, contada da publicação vigente — custa o degrau 8 e `SCHEMA_VERSION` 8 · **(b)** evento de cronograma marcado, com datas absolutas · **(c)** nada estruturado; tempestividade é juízo de admissibilidade | **(a)**, degradando para (c) quando o Edital nada declarar |
| **4** | **Quem julga** | **(a)** a presidência, por vínculo · **(b)** capacidade nova `recurso:julgar`, com impedimento que **bloqueia** quem avaliou, consolidou ou emitiu · **(c)** comissão recursal própria | **(b)** |
| **5** | **O recurso pode piorar a situação de quem recorreu** | **(a)** não, na V1 — e a vedação alcança também a reavaliação ordenada · **(b)** sim, com contraditório prévio (inviável sem notificação) · **(c)** sim, sem contraditório | **(a)** |
| **6** | **Progressão retroativa** | **(a)** efeito pleno, com impedimento de publicação enquanto houver pendência reaberta e avisos nomeados na Mesa, no marco e na prévia · **(b)** efeito limitado à Etapa do recurso, salvo decisão expressa · **(c)** efeito pleno, sem guarda | **(a)** |
| **7** | **O que torna uma publicação definitiva** | **(a)** nada muda — segue sendo escolha do publicador · **(b)** impedida enquanto houver recurso pendente ou reavaliação não concluída; prazo verificado quando computável e **declarado** quando não; e a definitiva que corrige outra é nomeada pela causa, sem natureza nova · **(c)** exigir prazo estruturado sempre, sem publicação definitiva para Editais anteriores | **(b)** |

**A única decisão com custo de esquema é a 3**: janela recursal é conteúdo normativo novo, e por
isso arrasta o degrau 8 em `publicacoes/domain/elevacao.py`, a elevação de `SCHEMA_VERSION` para 8,
a escrita no assistente e a entrada no catálogo de Retificação. As outras seis não tocam conteúdo
publicado. É o item a dimensionar primeiro no plano da 018 — e o único que, se a 018 precisar ser
fatiada, tem por onde ser adiado sem desmontar as demais: sem ele, a tempestividade continua sendo
juízo de admissibilidade, que é a degradação que a própria decisão 3 declara.

---

## 12. O que este documento não faz

- **Não abre a SPEC 018 e não a autoriza.** Aprovado o escopo, o passo seguinte é
  `speckit-specify`, e depois o fluxo da Constituição — clarificação, plano, tarefas, análise de
  consistência. Nenhuma linha daqui é requisito antes disso.
- **Não desenha o fluxo do recurso.** Estados, telas, formulário de interposição, anexos, contrato
  de API e trilha são da SPEC 018. O que está decidido é o escopo, e não a sua forma.
- **Não reabre a decisão C.** As três escolhas da §1 da descoberta são insumo, e foram consumidas
  como tal.
- **Não altera spec existente.** A 013 continua registrando recurso e reconsolidação como fora de
  escopo; a 017 continua com `ResultadoEtapa` fora da divulgação e com a FR-056 como está. A
  decisão 1 amplia a visibilidade **na SPEC 018**, pelo texto dela — não por este documento, e não
  retroativamente.
- **Não escreveu código, migration nem teste.**
