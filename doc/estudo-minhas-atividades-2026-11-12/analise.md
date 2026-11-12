# Análise: o GPS orientado ao trabalho de cada pessoa

Os caminhos de código são relativos a `backend/processo_seletivo/`. "A" é `interface/andamento.py`,
"P" é `interface/providencias.py` e "T" é `interface/trabalho.py`. A validação citada como V-n está
em [`validacao/`](validacao/README.md).

---

## A. Diagnóstico do estado atual

### O que já existe

O GPS tem **três leituras** do trabalho, e nenhuma é um motor de tarefas. Todas são derivação de
leitura: não guardam estado, não concedem permissão e não praticam ato.

| Leitura | Pergunta que responde | Escopo | Decide "seu" por | Onde aparece |
|---|---|---|---|---|
| **Faixa da 104** (`T`, `do_ator`) | o que eu posso fazer, entre Editais | a unidade inteira | papel e permissão (Edital, Retificação, recursos); pessoa só na avaliação | topo da Lista (`views.lista`, `views.py:285-376`) e página do Processo (147) |
| **Andamento da 127** (`A`, `do_edital`) | o que está em aberto neste Edital, e de quem é | um Edital | `Alcance.de` + `e_sua` (`A:1700-1724`, `A:2708-2722`) | "O que fazer agora", dentro do Centro de Controle (136/138) |
| **Minhas Etapas** (`views.py:12090`) | onde eu avalio | as alocações da pessoa | `AlocacaoEtapa` | página própria; a Mesa do avaliador |

**A faixa da 104 é a área de "atividades designadas" do pedido.** O nome é "Ações disponíveis para
você", na Lista, e mostra cinco itens antes de "Mostrar os outros". Ela cobre quatro naturezas:
- Edital: continuar a elaboração, homologar, conferir e publicar;
- Retificação, pelo ato principal;
- recursos a julgar;
- avaliação pendente.

Ela foi desenhada para ser barata. O número de consultas não cresce com o número de Editais (FR-2806
da 104, guardado por `tests/performance/test_trabalho_em_escala.py`).

**O andamento da 127 já é a fonte de verdade das providências depois da publicação.** Cada célula
vem de uma função que já decide a tela do ato: `previa.recortes_do_marco`,
`conducao_do_marco.indicador_do_marco`, `prontidao.panorama_da_etapa`, `leitura_do_recorte`,
`publicabilidade.aferir` e `formalizacao.passagem`. O teste de coerência prende a derivação à tela
(`tests/interface/test_andamento_coerencia.py`, SC-1230): toda providência "sua" leva a uma tela que
oferece o ato, e toda espera diz na tela a mesma razão. Cada providência já tem:
- o ato, em linguagem do operador ("Convocar 3 titulares");
- onde: Perfil e lista;
- o responsável, por papel;
- se é da pessoa (`sua`);
- a razão da espera;
- `ate`;
- a URL com âncora até o ponto exato da tela (139), e a volta ao Centro.

**O Centro de Controle já separa "o Edital" de "você".** Ele tem oito macrofases, com várias acesas
ao mesmo tempo e sem "fase atual" (D-003 da 136). O "Onde estamos" conta as suas, as de outros, as
que aguardam e as impedidas (`centro.onde_estamos`). E o destaque só aparece quando há uma única
providência sua (`centro.destaque`).

### Onde estão as lacunas

1. **A faixa não alcança o trabalho da comissão depois da publicação.** `FORA_DA_FAIXA` (`T:47-51`)
   nomeia oito famílias: classificação, sorteio, resultado, convocação, documentos e formalização,
   Requerimento de Matrícula, avisos e encerramento. Estão fora por uma razão de custo, e não de
   produto: elas dependem do conteúdo publicado de cada Edital (D-002 da 104). A 129 chamou a
   ampliação de **Frente B**, ainda sem dono: "agregá-la sobre a unidade exige uma leitura em lote
   que ainda não existe". A 127 recusou rodar a derivação por linha da Lista (D-005) pelo mesmo
   motivo. Medido: a presidência tem **20 atos seus em 11 Editais, e a faixa mostra zero** (V-1).

2. **"Seu" é decidido por base de autorização, e não por designação.** Hoje há três situações:
   - quem conduz é a presidência do Processo ou quem tem `comissao:gerir`
     (`comissoes/domain/autorizacao.py:81-97`);
   - quem publica e quem julga são papéis da unidade;
   - só a avaliação (`AlocacaoEtapa` + `Atribuicao`), a conferência (`AlocacaoAConferencia`, 115) e a
     formalização (`DesignacaoParaFormalizacao`, 117) são decididas por pessoa.

   **Todas essas designações concedem a base para o ato.** Nenhuma é só informativa.

3. **A permissão sistêmica não se distingue do vínculo.** Para o Gestor, tudo é "seu" (V-4: 22 atos
   em 12 Editais). O dado que separaria os dois casos já existe: `pode_gerir_comissao` devolve a base
   (`PERMISSAO_SISTEMICA` ou `BASE_PRESIDENCIA`). Mas `Alcance.conduz` reduz isso a um booleano.

4. **Não há prazo da comissão.** `ate` é o fim de uma espera: fim das inscrições, extração, fim do
   prazo de recurso, prazo de resposta do candidato. Não há data até a qual a comissão deva agir, e
   a derivação não lê o cronograma (`agenda.py` lê, mas só como projeção: D-006 da 101) (V-5).

5. **Alguns atos existem como acesso, e não como providência.** Não viram célula da derivação, e por
   isso não entrariam numa visão pessoal:
   - a publicação das inscrições (148) e a das convocações (149, que o Centro só *liga*: FR-5737);
   - os avisos aos candidatos (066);
   - o Requerimento de Matrícula;
   - o encerramento (a fase Conclusão nunca diz "pode encerrar", de propósito).

6. **A navegação é o que custa, e não a falta de funcionalidade.** Hoje a presidência faz este
   percurso, que o guia da equipe ensina:

   > Minhas Etapas → Processo → Edital → "O que fazer agora" → ato

   Para saber o que fazer, ela abre cada um dos 11 Editais.

### Resposta às questões 1 a 3 do pedido

- **O GPS já tem os elementos?** Quase todos. A derivação, a marca SUA, os acessos diretos, a volta
  ao Centro, a regra de agrupamento, os testes de coerência e as bases por pessoa já existem. Faltam
  duas coisas: a **leitura entre Editais** do que a 127 já deriva, e a **separação entre base por
  vínculo e base sistêmica**.
- **Qual é o problema principal?** A fragmentação da navegação, para quem conduz. Não é ausência de
  funcionalidade. A orientação existe, mas mora um Edital por vez.
- **A área atual pode assumir esse papel?** Sim. A faixa da 104 é o lugar, e a Frente B é o
  incremento previsto. Ela não precisa ser reconstruída: precisa ler a 127 para as famílias que hoje
  manda "para o detalhe de cada Edital".

---

## B. Mapa das atividades operacionais

As colunas dizem quando a atividade surge, quem tem a base para ela, de onde vem o estado e para onde
leva. **"Natureza"** é o identificador da derivação, quando houver.
- **Executável**: é ato de alguém no GPS.
- **Espera**: é uma condição do mundo, e ninguém age.
- **Acesso**: é um ato que existe, mas não é providência derivada.

| Fase | Atividade | Surge quando | Base (quem pode) | Origem do estado | Destino | Tipo |
|---|---|---|---|---|---|---|
| Elaboração | Continuar a elaboração | Edital EM_ELABORACAO | Elaborador | `T._do_edital`, `acoes.PROXIMO_RESPONSAVEL` | edição do Edital | executável |
| Elaboração | Homologar | EM_REVISAO | Homologador, com segregação | idem | detalhe | executável |
| Elaboração | Conferir e publicar | HOMOLOGADO | Publicador, com segregação (`impede_por_segregacao`) | idem | detalhe | executável |
| Publicação | Agir na Retificação | Retificação em curso | o papel do ato principal | `atos_retificacao.proximo_passo` | Retificação | executável |
| Inscrições | Inscrições recebidas | período aberto | candidato | `periodo.estado` | — | espera (`ate` = fim) |
| Inscrições | Publicar/homologar as inscrições | 148 | Publicador | `inscricoes_publicadas.py` | publicação das inscrições | **acesso** |
| Encerramento das inscrições | Alocar e distribuir (`distribuir`) | fim das inscrições, com inscrição sem avaliador suficiente | presidência | `prontidao.panorama_da_etapa` | distribuição da Etapa | executável |
| Avaliação | Avaliar (`avaliar`) | inscrição atribuída e pendente | **membro alocado** | `carga_nas_etapas`, `Atribuicao` | Mesa do avaliador | executável |
| Avaliação | Consolidar / reavaliar (`consolidar`, `reavaliar`) | avaliações prontas, ou recurso deferido | presidência | `resumo_da_etapa` | consolidação | executável |
| Sorteio | Congelar a relação (`relacao`) | fim das inscrições e habilitação, se houver | presidência | `previa.recortes_do_marco` | jornada do sorteio (142) | executável |
| Sorteio | Observar a extração (`semente`) | depois de `occurrenceAt` | presidência | idem | jornada do sorteio | espera, depois executável |
| Sorteio | Sortear (`sorteio`) | semente observada | presidência | idem | jornada do sorteio | executável |
| Classificação | Emitir a ordem (`ordem`) | Etapas que a ordem lê, concluídas | presidência | `conducao_do_marco.indicador_do_marco` | ordem do marco | executável |
| Classificação | Ordem de lista sem concorrente | universo vazio depois da progressão (135) | presidência | idem, `lista_vazia` | ordem do marco | executável |
| Classificação | Emitir o corte e apurar (`corte`, `apuracao`) | ordem vigente; espera o prazo de recurso, se houver | presidência | `publicabilidade.aferir` | corte e apuração | espera, depois executável |
| Resultados | Publicar o preliminar ou o definitivo (`resultado`) | ato publicável; o definitivo espera a janela de recurso | Publicador (`resultado:publicar`) | `publicabilidade.aferir` | publicação do resultado | espera, depois executável |
| Recursos | Julgar recursos (`recurso`) | recurso admitido | Julgador, menos os impedidos (`recursos/domain/elegibilidade.py`) | `T._dos_recursos` | recursos do Edital | executável |
| Recursos | Instruir e cumprir decisão | recurso deferido | presidência | recursos, reavaliar | instrução e reavaliação | executável |
| Convocação | Convocar titulares (`convocacao`) | resultado definitivo divulgado | presidência | `leitura_do_recorte` e prévias | convocação do recorte | executável |
| Convocação | Resposta do convocado | convocação comunicada | candidato | `Convocacao.vencimento` | — | espera (`ate` = prazo do candidato) |
| Convocação | Publicar as convocações | convocação comunicada | presidência | 149 | publicação das convocações | **acesso** |
| Documentos | Conferir documentos (`conferir`) | documento entregue | presidência ou **membro alocado à conferência** (`pode_conferir_documentos`) | `leitura_do_recorte` | conferência do convocado | executável |
| Novas chamadas | Desfechar e chamar o sucessor | prazo vencido ou desfecho | presidência | `convocacao` e vagas (141, 155) | convocação | executável |
| Novas chamadas | Destinar a vaga não preenchida | vaga sem concorrente (155) | presidência | `impedimentos[]` | destinação da vaga | executável |
| Conclusão | Disponibilizar ao setor (`formalizacao`) | convocados aptos | presidência ou acessos (definir/designar); **setor designado** (exportar) | `formalizacao.passagem` | formalização (153) | executável |
| Conclusão | Avisos, Requerimento de Matrícula | conforme o Edital | presidência, Publicador | 066 e o Requerimento | telas próprias | **acesso** |
| Conclusão | Encerrar o Edital e o Processo | decisão do gestor | Gestor | `pendencias_do_edital` (advertência) | encerramento | **acesso**, de propósito |

**Variação por modalidade.** A sequência de cada Perfil sai da configuração
(`classificacao/domain/jornada.jornada()`), e não de uma lista fixa. Um Edital só de sorteio não tem
distribuir, avaliar nem consolidar. Um Edital sem recurso declarado não espera janela. Uma Etapa "sem
efeito" não gera ato (D-010 da 127). A derivação já trata isso: a visão pessoal só herda o que ela
emitir.

**Quando a atividade surge.** Antes da publicação, o trabalho é o da faixa da 104 (o bastão). Depois
dela, é o da 127, **progressivamente**: só vira providência o que está em aberto (PENDENTE, OBSOLETO,
AGUARDA, IMPEDIDO). O que é *Depois* fica fora do nível 1. Por isso a lista pessoal não mostraria
"dezenas de tarefas futuras".

---

## C. Comparação de alternativas

### A — Derivação pura: a visão pessoal é um filtro sobre o que já se deriva

A visão junta, para a pessoa, os objetos da 104 e as providências "suas" da 127 em cada Edital em que
ela tem base. Nada se guarda.

| Critério | Avaliação |
|---|---|
| Consistência | **Uma fonte só.** O ato feito no Centro, na tela do ato ou em qualquer outro lugar some da lista na leitura seguinte, porque a célula vira FEITO |
| Atividade que deixa de fazer sentido (Retificação, mudança de configuração) | some: a derivação relê a versão vigente |
| Dependência entre atividades | já modelada: *Depois* e *Aguarda*, com razão |
| Refazer legitimamente | já modelado: OBSOLETO (ordem vencida por recurso, por exemplo) é "a praticar" |
| Editais anteriores à funcionalidade | funcionam sem migração |
| Rastreabilidade | a do próprio ato: trilha, base e motivo. A lista não precisa de trilha porque não decide nada |
| Custo | linear no número de Editais (~77 a 130 consultas cada, V-6). É o problema real |
| Responsável nominal | só onde o domínio já designa: alocação, conferência, formalização |

### B — Tarefas persistidas

O sistema cria registros de tarefa, com responsável, estado e prazo.

- **Duplica a máquina de estados.** Cada ato precisaria abrir e fechar a tarefa, e qualquer caminho
  esquecido (o Centro, uma Retificação, uma correção da 120) a deixaria pendente para sempre. É o
  risco de "atividade falsa ou permanentemente pendente" do pedido, só que garantido.
- **Retificação e reaprovação de ordem** exigiriam invalidar tarefas, ou seja, uma segunda derivação
  só para corrigir a primeira.
- **Esbarra na Constituição.** Ou as tarefas seriam append-only (e o "concluir" vira evento), ou
  seriam a única tabela mutável do fluxo normativo.
- **O que ganharia:** prazo administrativo e atribuição livre. Os dois são decisões de governança,
  e não de modelo (ver D-3 e D-4).

**Não recomendada.**

### C — Híbrido: derivação para as providências, persistência só para a designação

As providências continuam derivadas. Persiste-se apenas "quem é o responsável pelo grupo X neste
Edital".

**O híbrido já existe.** `AlocacaoEtapa`, `Atribuicao`, `AlocacaoAConferencia` e
`DesignacaoParaFormalizacao` são a parte persistida, e cada uma *concede* a base para o ato. A questão
real é se deve existir **mais uma** designação, por grupo operacional. Há duas variantes, e as duas
são problemáticas:

- **C1, informativa (não concede nada).** "João é o responsável pelo sorteio", mas só a presidência
  sorteia. A lista de João mostraria um ato que ele não consegue praticar. A 127 já evita exatamente
  isso: a URL só existe quando o ato é seu (P:84, 97). O resultado seria a "atividade sua que você
  não pode fazer", ou um acompanhamento sem ação, que é o Trello que o pedido recusa.
- **C2, que concede.** "A condução do sorteio deste Edital é delegada a João". Isso é mudar a regra de
  autorização da comissão, hoje concentrada na presidência (`comando_de_comissao`). É decisão de
  governança, com trilha, revogação, segregação e efeito sobre a elegibilidade do julgador de
  recursos: quem avaliou, consolidou, emitiu ou publicou o ato atacado não o julga
  (`recursos/domain/elegibilidade.py`). Cabe numa spec de domínio própria, se a operação
  real pedir. Não cabe numa feature de UX.

### Síntese

| | A — derivação | B — tarefas | C1 — designação informativa | C2 — delegação com base |
|---|---|---|---|---|
| Simplicidade | alta | baixa | média | baixa |
| Consistência com o estado | **total** | frágil | total nas providências, ambígua no responsável | total |
| Manutenção | baixa: cada ato novo já entra pela 127 | alta | média | média |
| Rastreabilidade | a do ato | precisa de trilha própria | precisa de trilha própria | trilha de autorização |
| Experiência | boa para quem tem base; nada a configurar | configura e mantém | configura; mostra o que não se pode fazer | configura; distribui de verdade |
| Muda regra de domínio | não | não | não | **sim** |
| Complexidade relativa | P | G | M | G |

---

## D. Proposta de experiência

Há três perspectivas, que respondem a três perguntas diferentes, e cada uma tem um lugar. Os
wireframes estão em [`wireframes.html`](wireframes.html).

### Operador: "Seu trabalho", na Lista (wireframes 1 e 2)

A faixa "Ações disponíveis para você" deixa de excluir as oito famílias. Ela passa a mostrar também as
providências **suas por vínculo** dos Editais das comissões da pessoa. Três grupos:

1. **Para fazer agora.** Os itens PENDENTE e OBSOLETO cuja base é vínculo: presidência, alocação à
   Etapa, alocação à conferência, designação, ou o papel de julgar e publicar no caso dos recursos e
   do resultado. São cinco linhas antes de "Mais". **O mesmo ato em vários Editais vira uma linha**
   ("Emitir a ordem que declara que ninguém concorreu — 7 Editais"; V-3). Cada linha leva à URL com
   âncora que a 127 já produz, e a volta ao Centro (139) já existe.
2. **Em espera nos seus Editais.** É recolhido e só tem os AGUARDA. A data é dita pelo que ela é: "o
   prazo de recurso corre até 17/11", "o prazo do candidato corre até 12/12". **Nunca** "seu prazo"
   (V-5).
3. **Com outras pessoas, nos seus Editais.** Uma frase, e não uma lista: "no SIM05, Avaliar 5
   inscrições está com treino.avaliacao1". O detalhe fica no Centro.

Exemplos concretos, lidos dos cenários (V-1):
- **Presidência**, 12 linhas para 20 atos. Em primeiro lugar, a conferência dos documentos de três
  convocações (SIM12). Depois, a de uma (SIM11), convocar três titulares (SIM10), observar a extração
  (SIM07) e congelar a relação (SIM06).
- **Avaliador**, uma linha: "Avaliar 5 inscrições, Prova objetiva, SIM05". Em seguida, "Nas outras 10
  comissões, nada depende de você agora".
- **Gestor**: a faixa mostra o que é dele por papel (a 104 de hoje). Os 22 atos de condução que ele
  *pode* praticar ficam fora (D-2). O Centro de cada Edital continua mostrando-os como seus, porque lá
  a pergunta é outra.

**Ordem.** Primeiro OBSOLETO, porque algo vigente ficou para trás. Depois PENDENTE, na ordem da
jornada, como `providencias.ordenar` já faz. Entre Editais, ordena-se pelo Edital mais antigo, e não
por `ate`: `ate` não é prazo de quem age.

**Coerência com o Centro.** A visão pessoal **não tem regra própria**. Uma linha só existe se a mesma
célula está com a marca SUA no Centro daquele Edital. O teste de coerência da 127 (SC-1230) passa a
valer também para ela.

### Presidência: "Quem faz o quê", no Centro do Edital (wireframe 3)

Fica no Centro, e não na lista pessoal: a pergunta é "o que falta **neste** Edital e com quem está".
É um bloco recolhido abaixo das providências, visível a quem consulta (`ve_a_matriz`). Para cada
grupo de trabalho em aberto ou próximo, ele diz quem tem a base hoje:
- presidência;
- os alocados à Etapa, com a carga de cada um, que `carga_nas_etapas` já calcula;
- os alocados à conferência, ou **"ninguém alocado"**, com o caminho para alocar;
- os designados para a formalização;
- os papéis da unidade (Publicador, Julgador).

Isso responde "há atividade importante sem responsável?" **sem cadastro novo**. O caso que importa é
a conferência sem alocação, que recai sobre a presidência. Atraso não se mostra, porque não existe
prazo da comissão (lacuna 4). O que existe é "parado há N dias", e isso exigiria `desde`, que a
derivação não tem depois da publicação. Fica para depois.

### Quem participa de vários Editais

A faixa já é entre Editais por construção. Os cenários são o caso de prova: a presidência preside
onze comissões, e cada avaliador é membro de onze.

### Integração com o Centro de Controle

| | Centro de Controle | Seu trabalho |
|---|---|---|
| Pergunta | o que está acontecendo com este Edital | o que eu preciso fazer, em todos |
| Escopo | um Edital, todos os papéis | uma pessoa, todos os Editais dela |
| Mostra de outros | sim, por papel | uma frase |
| Mostra o futuro | fases, *Depois* | não |
| Fonte | `andamento.do_edital` | **a mesma**, filtrada |

---

## E. Recomendação

**A alternativa A: a derivação que já existe, lida entre Editais, na faixa que já existe.** É a Frente
B da 129, com duas regras que a validação mostrou serem necessárias:
1. "seu" passa a ser **por vínculo** (V-4);
2. o mesmo ato **agrupa entre Editais** (V-3).

A hipótese do pedido se confirma, com uma correção importante. O problema **não** é a falta de um
módulo de tarefas: é a falta de uma visão pessoal das providências que o GPS já identifica. Mas
"atribuir responsáveis por grupos operacionais" **não** é o atalho barato que parecia:
- no GPS de hoje, quem conduz é a presidência;
- as designações que existem concedem a base para o ato;
- uma designação que não concede nada mostraria às pessoas um trabalho que elas não podem fazer.

A distribuição de trabalho que existe de verdade já tem mecanismo, e a visão pessoal só precisa lê-la:
- **avaliação**: alocação e distribuição;
- **conferência documental**: alocação à conferência, que nenhum cenário usa ainda;
- **formalização**: designação;
- **recursos e resultado**: papéis da unidade.

Há também um fato do contexto. A equipe inicial é de duas ou três pessoas, que acumulam papéis. Para
ela, o ganho está quase todo em "Seu trabalho" da presidência, e quase nada em distribuir.

---

## F. MVP recomendado

**Entra agora: "Seu trabalho" para quem tem vínculo de comissão.**
- A faixa da Lista acrescenta, aos objetos da 104, as providências suas por vínculo da 127. A leitura
  se limita aos Editais publicados dos Processos em que a pessoa é membro ativo.
- O agrupamento entre Editais pelo mesmo ato, e os três grupos (agora, em espera, com outros).
- A faixa carrega à parte da Lista, para que a Lista continue com o custo constante da FR-2806. A
  faixa tem orçamento próprio por Edital, como `test_andamento_em_escala.py` já mede.
- **Edital que não pôde ser lido se diz.** `do_edital` engole a exceção e devolve `None`, para não
  derrubar o detalhe. Numa lista pessoal, isso seria um falso "nada a fazer". A faixa deve dizer
  "1 Edital não pôde ser lido agora", com o link.
- `trabalho.do_ator` é chamado uma vez e passado a cada `do_edital` (V-6).
- O teste de coerência (SC-1230) é estendido à faixa, e os textos fixados de `FORA_DA_FAIXA` são
  revistos.

**Como se valida.** Com os cenários C04 a C15 e uma comissão real, pela tarefa: "sem abrir nenhum
Edital, diga o que você tem a fazer e faça o primeiro". O êxito é medido contra o percurso de hoje
(Minhas Etapas → Processo → Edital), pelo método de tarefas medidas do estudo do Centro (`05-avaliacao-comparativa.md`).

**Fica para depois, nesta ordem:**
1. **"Quem faz o quê" no Centro** (wireframe 3). Antes disso, os cenários precisam de alocação à
   conferência, designação de formalização e um recurso interposto (V-8).
2. **Publicador e Julgador entre todos os Editais da unidade** (V-7). É o caso sem fronteira de
   comissão, e pede a leitura em lote ou uma pré-seleção barata dos Editais com publicabilidade
   aberta.
3. **Os atos que hoje são só acesso** como providência: publicação das inscrições e das convocações,
   avisos, Requerimento. Cada um precisa de uma célula na 127, e não de um caso especial na faixa.
4. **"Parado há N dias"**, que pede `desde` nas células.

**Não entra:** tarefa persistida, prazo administrativo inventado, contador na barra lateral, página
inicial nova, notificação, delegação de condução (D-3).

---

## G. Impactos e riscos

| Área | Impacto | Risco e mitigação |
|---|---|---|
| `trabalho.py` / faixa | deixa de ser "sem conteúdo do Edital"; muda a nota de cobertura | os testes `test_organizacao_da_lista.py:382-404` e `test_trabalho_em_escala.py` fixam o texto e o custo. Revê-los é parte da spec, e não efeito colateral |
| `andamento.py` | `Alcance` precisa guardar **a base** de `conduz` (vínculo × sistêmica). Não muda regra: só expõe o que `pode_gerir_comissao` já devolve | o Centro continua tratando as duas como suas. A diferença vale só na faixa |
| Custo | ~77 a 130 consultas por Edital da pessoa (V-6) | carregar à parte; limitar aos Processos com vínculo; medir com 30 Editais. O caso Publicador (V-7) fica fora do MVP por isso |
| Segurança | nenhuma permissão nova; a URL só existe quando o ato é seu (P:84, 97), e a tela do ato reverifica | a faixa nunca é porta: o comando sempre passa por `comando_de_comissao` e pelos predicados |
| Consistência | uma fonte só; o ato feito em qualquer lugar some na leitura seguinte | falso vazio quando `do_edital` falha. Mitigado: o Edital não lido se diz |
| Processo encerrado | `Alcance.ativo` falso: nada é seu | o esperado (D-021 da 127) |
| Vocabulário | "Seu trabalho" no lugar de "Ações disponíveis para você" | a troca de nome espera validação com pessoas (D-007 da 104). O MVP pode manter o nome |
| Decisões anteriores | revisita a D-002 da 104 (cobertura) e a D-005 da 127 (custo por Edital); respeita a D-001 da 104 (nenhuma página nova) | a decisão é do usuário (D-1) |
| Manutenção | todo ato novo que entra na 127 aparece na faixa sem código novo | é o ganho. O custo é que um defeito de derivação passa a aparecer em dois lugares, mas o teste de coerência é o mesmo |
