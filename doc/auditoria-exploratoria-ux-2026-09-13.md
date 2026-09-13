# Auditoria exploratória de UX ponta a ponta — 2026-09-13

Percurso completo do produto pelo navegador, em banco próprio (`ps_auditoria_e2e`, porta 8033),
alternando entre operador novato, presidência, avaliador, julgador de recurso e candidato. Um
Processo Seletivo foi criado do zero e conduzido até o resultado sucedido por recurso; os três
Editais da demonstração oficial foram usados para os cenários de sorteio, modalidades e avaliação
em várias Etapas.

A pergunta que governa o documento não é "o sistema faz?", e sim **"o operador entende o que
fazer?"**. Onde foi preciso abrir código ou spec para compreender algo que a tela deveria ter
dito, está registrado.

---

## 1. Resumo executivo

> **Quão perto o sistema está de permitir que alguém compreenda e execute um Processo Seletivo
> completo sem treinamento intensivo?**

**Perto, e mais perto do que o conjunto de defeitos sugere.** Executei o ciclo inteiro — concepção,
elaboração, submissão, homologação, publicação, retificação, inscrição real de candidato,
constituição de comissão, alocação, distribuição, avaliação, consolidação, classificação,
publicação de resultado preliminar, recurso interposto, admitido e deferido, sucessão do ato e
republicação — **sem consultar spec nenhuma para operar as telas**. Consultei código quatro vezes,
e três delas para confirmar uma suspeita, não para descobrir o caminho.

O produto tem um padrão de comunicação genuinamente raro: atos consequentes têm página própria
("O que este ato provoca"), negativas explicam quem é aguardado, e a publicação de resultado é
precedida de uma prévia que mostra exatamente o que o público verá. Esse padrão é o ativo mais
valioso do sistema e deveria governar o resto.

O que separa o produto da meta são **três falhas estruturais**, não uma lista de polimento:

1. **A oferta publica um número de vagas que o sistema não consegue usar.** "Vagas imediatas" e
   "Quadro de vagas" são duas caixas no mesmo cartão; preencher a primeira publica "2 vagas
   imediatas" no portal e no PDF, e deixar a segunda vazia desliga ocupação e convocação. Os
   **quatro** Editais deste ambiente — inclusive os três da demonstração escrita pela equipe —
   estão nessa condição. Duas features inteiras (016 e 019) ficam inertes.
2. **A camada de microcópia que explicaria as decisões difíceis não chega ao operador que
   enxerga.** Na etapa de Classificação, 17 das 18 dicas de consequência estão em `.oculto`
   (sr-only) sem equivalente visível. O texto existe, é bom, e é invisível.
3. **O modelo que a interface ensina não é o que ela permite.** A tela de criação diz "o Processo
   reúne Editais"; não existe rota para criar o segundo Edital de um Processo.

| Dimensão | Nota | Por quê |
|---|---:|---|
| Clareza conceitual | **6** | Processo/Edital, publicação, retificação e sucessão são ensinados muito bem. "Marco classificatório", "impedimento", "consolidar", "faixa", "providência a jusante" não. |
| Encontrabilidade | **5** | Comissão, alocação e mesa do avaliador são E0. Recursos é E4 (sem link algum), "publicar resultado" é E2/E3, "segundo Edital do Processo" é inexistente. |
| Previsibilidade | **4** | Quadro de vagas, vínculo Etapa↔Evento, segregação de funções e prazo recursal só se revelam depois. Em compensação, a modalidade do candidato muda os documentos na hora. |
| Fluxo ponta a ponta | **7** | O caminho existe inteiro e eu o percorri. Quebra em três pontos: etapa 7 sem navegação, publicar resultado fora do marco, recursos sem porta. |
| Organização do trabalho | **8** | Comissão, alocação e distribuição são o melhor bloco do produto. Falta só nome do candidato na distribuição e aviso ao remover membro. |
| Experiência do candidato | **8** | Inscrição, comprovante, acompanhamento, versão aceita e recurso são exemplares. Falta o número de vagas por modalidade e o prazo recursal junto do resultado. |
| Avaliação | **7** | "Minha Mesa" é uma mesa de verdade. Falta o Edital ao lado e o campo Parecer está mal explicado. |
| Resultado / publicação | **8** | A prévia de publicação é a melhor tela do sistema. O acesso a ela é o problema. |
| Recuperação de erros | **7** | Devolver para elaboração, revogar homologação, reabrir avaliação, atribuições órfãs, sucessão de ato. Quase tudo é recuperável — e quase nada é confirmado antes. |
| Visão global | **3** | A Supervisão, com resultado publicado e recurso no prazo, não menciona nem um nem outro. |

**Não faço média.** As notas 8 e a nota 3 convivem porque o produto é forte em *cada* tela e fraco
em *entre* telas.

---

## 2. O teste de ponta a ponta

| Cenário | Edital | Variáveis cobertas | Como foi montado |
|---|---|---|---|
| **1 — Seleção simples** | 90/2026 (criado do zero) | 1 perfil, 2 vagas, 1 Etapa pontuada classificatória, 1 documento, 1 marco, desempate declarado, recurso em 3 dias corridos | Interface, do botão "Novo Processo Seletivo" até o resultado sucedido |
| **2 — Análise / classificação** | 51/2026 (seed) | 2 perfis, 3 Etapas, comissão, eliminação em Etapa anterior, participante sem pontuação | Leitura das telas de classificação, resultados e ocupação |
| **3 — Sorteio** | 26/2026 (seed) | método publicado, ocorrência externa, relação congelada, semente, manifesto, verificação pública | Telas de gestão e o verificador público |
| **4 — Modalidades / reserva** | 01/2026 (seed) | AC + PPP, anexo-modelo, documento condicionado à modalidade, retificação com vigência futura | Inscrição real de candidato com troca de modalidade |
| **5 — Curso / cursista** | amostra real (doc/) | perfil = turma; 58, 59, 77, 78, 158 | Não montado no sistema — avaliado pela leitura da amostra |
| **6 — Outra família** | 69/2026 (amostra real) | chamada pública de remanescentes, reclassificação, impugnação sem recurso, entrega presencial | Não montado — avaliado pela leitura da amostra |

**Executado de verdade no cenário 1:** criação do Processo, 9 etapas do assistente, 2 tentativas de
erro deliberado, submissão, homologação, bloqueio de segregação de funções, publicação por segunda
pessoa, **três Retificações** publicadas, inscrição de dois candidatos pela interface (código por
e-mail, dados pessoais, upload de PDF, declarações, comprovante), comissão de 3 pessoas, alocação,
distribuição proposta pelo sistema, 6 avaliações concluídas por 2 avaliadores, consolidação,
emissão da ordem com empate residual, publicação do resultado preliminar, recurso interposto pelo
candidato, admitido e deferido com correção de pontuação, sucessão do ato de classificação,
republicação, e a recusa correta de publicar como definitivo dentro do prazo recursal.

**Sem cobertura:**

- **Ocupação e convocação** (specs 016 e 019). Não por falta de tentativa: nenhum dos quatro
  Editais tem quadro de vagas, e sem ele não há o que apurar nem quem convocar. Ver fricção #1.
- **Cenários 5 e 6** não foram montados no sistema. A amostra real
  ([`avaliacao-de-capacidade-editais-2026-09-12.md`](avaliacao-de-capacidade-editais-2026-09-12.md))
  mostra que a família dominante é **discente/curso com sorteio**, e que em 59/2026 e 78/2026 **o
  código de vaga é a turma**. O modelo generaliza; a linguagem da tela, não — ver lacuna
  conceitual "Perfil de Vaga".
- **Divergência entre avaliações** (mais de uma avaliação por inscrição). O campo existe
  ("Avaliações por inscrição"), mas nenhum Edital do ambiente o usa.
- **Anexos com arquivo real** e Etapa decisória (rótulos Deferido/Indeferido).

---

## 3. Jornada real observada — cenário 1

```
Concepção            🟢 "Um Processo Seletivo nasce com o primeiro Edital. São conceitos
                        distintos: o Processo reúne Editais…" — a melhor frase do produto
Processo criado      🟡 "O que fazer agora" abre com o impedimento de CANCELAR e oferece
                        "Ativar Processo", que a publicação faz sozinha. O próximo passo real
                        (elaborar o Edital) está no cartão ao lado
Elaboração 1..9      🟡 9 etapas claras; a 5 (Classificação) despeja 30 controles, 10 deles de
                        sorteio, para uma seleção que não sorteia
                     🔴 as dicas de consequência da etapa 5 são invisíveis (sr-only)
                     🔴 etapa 7 (Anexos) não tem ‹ Voltar / Salvar / Avançar ›
Validação            🟢 IMPEDE / AVISO, com o que falta e o que só avisa
                     🔴 "Ir para Perfis de Vaga" leva à tela errada (o campo é da etapa 4)
Submissão            🟢 página "O que este ato provoca", com o estado seguinte nomeado
Homologação          🟢 mesma página; motivação obrigatória e registrada
Publicação           🟡 só aqui se descobre que quem elaborou e homologou não pode publicar
                     🟢 bloco vermelho "Este ato não pode ser desfeito", autoridade signatária
Portal público       🟢 "EM BREVE", vagas, requisitos, documentos que serão pedidos, cronograma
Retificação          🟢 tela de composição excelente (o que muda, e só o que muda)
                     🔴 ao sair dela vira `/schedule/id=…/endAt` e `2026-10-11T02:59:00+00:00`
                        na conferência e na publicação — A DATA MUDA DE DIA
Inscrição            🟢 3 passos, estado salvo, comprovante com protocolo, hash e versão aceita
Comissão             🟢 "nenhuma Etapa pode receber alocação enquanto ninguém responder"
Alocação             🟢 matriz pessoa × Etapa, com contadores
Distribuição         🟡 bloqueio correto ("as inscrições ainda estão abertas") revelado só ao
                        clicar, e sem dizer o que fazer
                     🟢 proposta por menor carga, com TEM HOJE / RECEBE / FICA COM
                     🔴 "6 com impedimento" quer dizer "sem avaliação concluída"
Avaliação            🟢 "Minhas Etapas" → "Minha Mesa" → "Próxima pendente"
                     🟡 "Parecer — É o parecer que responde a um recurso." (lido como opcional)
                     🔴 nenhum link para o Edital que se está aplicando
Consolidação         🔴 6 Resultados normativos criados em um clique, sem confirmação
Resultados da Etapa  🟢 CONCLUSÃO / ORIGEM / POR QUÊ / QUEM AVALIOU / QUEM CONSOLIDOU / VERSÃO
Classificação        🟢 proposta antes do ato, empate marcado, "Emitir é irreversível"
                     🔴 "Emitir ordem" também sem confirmação
Publicar resultado   🔴 o botão não está no marco: está atrás de "Consultar ato e proveniência"
                     🟢 a prévia é a melhor tela do sistema
Candidato acompanha  🟢 resultado por Etapa com o motivo, posição, "Recorrer de um resultado"
Recurso              🟢 prazo, tempestividade, protocolo, comprovante
                     🔴 a tela de Recursos da gestão não tem link de entrada nenhum
                     🔴 quem julga não vê o resultado, o parecer, o documento nem o Edital
Efeito do recurso    🟢 "O ato vigente está obsoleto… resultado superado por recurso" +
                        "Mudanças posição a posição" — exemplar
Sucessão             🟡 emitida com motivo; a tela não diz que a publicação ficou para trás
Republicação         🟢 "Este resultado foi sucedido… Ver o resultado vigente"
Resultado definitivo 🟡 oferecido na prévia e recusado ao confirmar (prazo recursal aberto)
Ocupação/convocação  🔴 "Não há quantidade declarada a apurar" — fim da linha
```

---

## 4. Top 10 fricções

### 1. O Edital publica um número de vagas que o sistema não consegue usar — **S4**

**Evidência.** No Perfil de Vaga há duas caixas de número: "Vagas imediatas" e, mais abaixo,
"Quadro de vagas › Ampla concorrência". Preenchi a primeira com 2 e deixei a segunda vazia. O
assistente marcou Perfis de Vaga como CONCLUÍDA; a etapa 9 disse "Nada pendente — o Edital pode ser
submetido"; a publicação não avisou nada; o portal público e o PDF publicaram **"2 vagas
imediatas"**; a classificação foi emitida e publicada. Em *Ocupação de vagas*:
"Este Edital não publicou quadro de vagas para este recorte. **Não há quantidade declarada a
apurar.**" Em *Convocação*: "Não há mais quem chamar dentro da faixa que o corte alcançou."

Não é erro de quem digita: **os três Editais da demonstração oficial (`seed_demo`) estão na mesma
condição** — 01/2026 (3 vagas), 26/2026 (40 vagas) e 51/2026 (2 vagas) mostram a mesma frase nos
três recortes. Quem escreveu o sistema caiu na mesma armadilha ao escrever a demonstração.

**Por que acontece.** O número que o Edital *publica* mora no Perfil; o número que a apuração *usa*
mora na linha do quadro. São dois campos porque o domínio precisa disso — a `025` decidiu que
quadro parcial é legítimo e que linha ausente nunca significa zero (D-006), e está certa. Mas a
interface coloca os dois no mesmo cartão, rotula um em português corrente e deixa o outro sem
explicação visível (a frase "Em branco: quantidade não declarada" é `.oculto`), e a validação só os
relaciona quando existe regra de corte derivada do quadro.

**Quem é afetado.** Todos. Persona A não sabe que há dois números; persona B acha que declarou as
vagas; o candidato lê um número que não governa nada; a presidência descobre no dia da convocação.

**Direção de solução.** Não é tooltip. **Duas decisões precisam virar uma.** Um Perfil sem
Modalidade declarada tem exatamente uma lista de concorrência: a linha geral do quadro deveria ser
*derivada* de "Vagas imediatas" e o bloco "Quadro de vagas" só aparecer quando o operador acrescenta
a primeira Modalidade — aí sim pedindo a repartição, com a soma conferida contra o total. Enquanto
isso não existir, a validação precisa de um AVISO explícito: *"Este Perfil publica 2 vagas imediatas
e não declara linha de quadro. Sem ela, a ocupação e a convocação não terão quantidade a apurar."*
E a etapa 9 (Revisão), que hoje exibe "2 vaga(s) imediata(s)" e nunca menciona o quadro, precisa
mostrar as duas coisas lado a lado.

---

### 2. "Partir de um Edital anterior" publica um cronograma vencido sem uma pendência — **S3**

**Evidência.** Criei o Edital 12/2027 a partir do 90/2026. Todas as etapas ficaram CONCLUÍDA. A
etapa 9 traz **uma única linha**: "AVISO O Edital não possui descrição." O Cronograma copiado diz
"Período de inscrição — Início: **13/09/2026** 08:00 · Término: **13/09/2026** 09:00": uma janela de
uma hora, do ano anterior, já vencida. Nada na validação fala de evento no passado, de ano divergente
do Edital, nem de janela de uma hora.

**Por que acontece.** O reaproveitamento copia o conteúdo normativo inteiro, inclusive datas — e
avisa isso muito bem, em prosa, na tela de composição ("Datas, vagas e prazos são da oferta anterior
até que alguém os revise"). Mas o *estado* das etapas não reflete o aviso: o Cronograma nasce
CONCLUÍDA, e a validação de publicabilidade não conhece "data no passado".

**Quem é afetado.** Exatamente a persona para quem a feature foi construída. A amostra real mostra
que "o 78 é o 59 com quatro alterações — título, uma frase, as quantidades e **o cronograma
inteiro**": trocar o cronograma é o trabalho principal do reaproveitamento, e é o que o sistema não
cobra.

**Direção de solução.** O Edital que nasce de outro deveria nascer com **Cronograma PENDENTE**,
não CONCLUÍDA, e a validação deveria ter um AVISO para evento cujo término já passou e um IMPEDE
para período de inscrições que se encerra antes da publicação. Custo baixo, e fecha o caso de uso
mais comum da amostra.

---

### 3. A microcópia que explicaria as decisões difíceis é invisível para quem enxerga — **S3, sistêmico**

**Evidência.** `base.html:157` define `.oculto { position:absolute; width:1px; height:1px;
clip-path: inset(50%) }` — o *screen-reader only* do projeto, usado corretamente em `<caption>` e
rótulos de tabela. O assistente usa a mesma classe para **toda dica de campo**, com o equivalente
visível sendo o `placeholder`. Onde o controle é `<select>` (ou input sem placeholder), não há
equivalente nenhum. Na etapa 5 (Classificação), **17 das 18 dicas** estão nessa situação:

- "Não há padrão: sem esta declaração o Edital não publica." (empate na última posição)
- "Sem corte, a Etapa seguinte recebe todos os habilitados, como hoje."
- "Só Etapas classificatórias."
- "Não declarar e negar são coisas diferentes…" (recurso)
- "Ela é declarada, e nunca deduzida das Etapas que este marco enumera."

No Perfil, quatro casos — e são as quatro decisões mais difíceis da tela: qual Modalidade é a ampla
concorrência, reversão de vaga reservada, forma de convocação ("**Sem esta declaração o sistema
recusa convocar**") e a linha do quadro de vagas.

**Por que acontece.** Uma decisão única de template, tomada por acessibilidade, que remove a camada
explicativa de quem lê com os olhos.

**Direção de solução.** É o **maior retorno por linha alterada do produto inteiro**: a prosa já
existe e é excelente. Renderizar a dica como texto auxiliar visível sempre que o controle não tiver
placeholder equivalente — e manter o `aria-describedby`. Não é "adicionar explicação": é parar de
escondê-la.

---

### 4. Um Processo não recebe um segundo Edital pela interface — **S3, estrutural**

**Evidência.** `edital:criar` é capacidade do Gestor, anunciada no seletor de identidade, existe no
domínio e na API. Não há rota em `interface/urls.py`. O cartão "Editais (N)" da página do Processo é
lista somente-leitura. O único caminho de criação é "Novo Processo Seletivo", que cria um Processo
*e* seu primeiro Edital.

**Por que é grave.** A tela de criação ensina literalmente o contrário — "o Processo reúne Editais
que podem ter cronogramas próprios, e nenhum Edital existe sem ele" — e a demonstração exibe um
Processo com três Editais. O operador aprende o modelo e não consegue reproduzi-lo. Na prática, ou
se usa a API, ou cada Edital vira um Processo — e aí o Processo deixa de significar o que a tela
disse.

**Efeito colateral.** "Partir de um Edital anterior" só é alcançável criando também um Processo
novo. A feature 023 nasceu do caso "o 78 é o 59 com quatro alterações" — dois Editais do mesmo
certame —, e é justamente esse caso que a navegação não permite.

**Direção de solução.** Um botão "Novo Edital neste Processo" no cartão Editais, levando ao mesmo
formulário sem os campos do Processo. É a menor mudança desta lista com o maior efeito conceitual.

---

### 5. Quem julga recurso não tem porta de entrada nem contexto — **S3**

**Evidência.** `/gestao/editais/<id>/recursos` existe e é uma boa tela. `grep 'interface:recursos'`
encontra duas referências: o próprio formulário de filtro e a migalha do detalhe. **Nada linka para
ela** — nem a página do Edital (com `recurso:julgar` no ator), nem a do Processo, nem a Supervisão,
nem o cabeçalho. O avaliador tem "Minhas Etapas" no topo de todas as páginas; o julgador não tem
equivalente.

E, chegando lá, a tela do recurso traz a peça, a fundamentação e quatro UUIDs — e **nenhum link**
para o resultado atacado, para a avaliação e o parecer que produziram a nota, para o documento
enviado ou para o Edital. Zero texto de ajuda. Julguei "a nota não considerou o último período" sem
poder abrir o histórico escolar nem o parecer do avaliador.

**Direção de solução.** "Minhas Etapas" deveria ser "Meu trabalho" e listar também os recursos
pendentes de quem tem `recurso:julgar`, com prazo. E a tela do recurso precisa do objeto ao lado:
link para o resultado divulgado, para a avaliação da Etapa alcançada (com parecer) e para os
documentos da inscrição.

---

### 6. A etapa "Classificação" cobra 30 decisões para a seleção mais simples — **S3**

**Evidência.** Um Perfil, uma Etapa, duas vagas. "Acrescentar marco" abre um bloco de 1376px e 30
controles: método do sorteio (10 campos, com a instrução "Deixe tudo em branco se este marco não
sorteia"), regra de corte (6), recurso (4), combinação e normalização (2 — que com uma Etapa só
produzem resultado idêntico), casas decimais e arredondamento **obrigatórios e sem padrão**, e
critérios de desempate.

**Por que acontece.** "Marco classificatório" acumula seis responsabilidades independentes:
combinar notas, arredondar, declarar recurso, declarar sorteio, cortar/progredir e desempatar.

**Direção de solução.** Progressive disclosure com uma pergunta de entrada: *"Como a ordem deste
marco é produzida? Pela pontuação das Etapas · Por sorteio"*. O bloco do sorteio só aparece na
segunda; "Regra de corte" só aparece quando a resposta a "Quantos progridem" deixa de ser "Este
marco não corta"; combinação e normalização só aparecem com duas ou mais Etapas enumeradas; casas
decimais ganham padrão 2 e arredondamento padrão "meio para cima".

---

### 7. A Retificação vira JSON Pointer e UTC exatamente onde é conferida — **S3**

**Evidência.** Na composição: "Evento 1 — Período de inscrição | Início | 20/09/2026 08:00 →
13/09/2026 08:00". Na tela da Retificação, na de homologação e **na tela irreversível de Publicar
Retificação**:

```
CAMINHO  /schedule/id=1705f922-7fbe-4f03-abd4-d4df14cc3268/endAt
ANTES    2026-10-11T02:59:00+00:00      DEPOIS   2026-09-13T13:00:00+00:00
```

O operador digitou **10/10/2026 23:59** (Brasília, como o Cronograma declara). Quem assina lê
**11 de outubro**. O `interface/retificacao.py` abre com a razão pela qual isso não pode acontecer
— "Quem elabora um Edital tem um problema administrativo, não um problema de representação
(FR-019)" —, e a 004/SC-004 verifica a tela de composição. A tela de *conferência* ficou de fora.

**Direção de solução.** O renderizador humano **já existe**: a página pública do Edital mostra
"ALTERADO — Evento do cronograma 'Inscrições pelo portal do candidato' — Início". Reaproveitá-lo nas
três telas internas, e formatar instantes na zona institucional. (No caminho, a página pública ganha
o que lhe falta: o valor antigo e o novo, não só o nome do campo.)

---

### 8. "Impedimento" quer dizer duas coisas na mesma tela — **S3**

**Evidência.** Na tela *Distribuir*, com zero conflitos registrados, o contador diz "**6 com
impedimento**". O que existe é "ainda não há avaliação concluída para esta inscrição"
(`prontidao.py:54`, `IMPEDIDA` = impedida de **consolidar**). Dois cliques ao lado, o botão
"Impedimentos" abre "Quem está impedido" — o impedimento do domínio, conflito de interesse do
avaliador — e diz "Nenhuma avaliação foi tirada do conjunto elegível nesta Etapa".

A leitura natural da presidência é "os seis candidatos têm impedimento com a banca".

Ao lado, quatro contadores marcam 6 ao mesmo tempo — "todas", "sem nenhum avaliador", "sem avaliador
suficiente", "com avaliação pendente" —, sem que a diferença entre os dois do meio seja visível.

**Direção de solução.** Renomear o estado de prontidão para o que ele é: "**não consolidável ainda**"
ou "aguardando avaliação". E colapsar os contadores que se sobrepõem: cobertura (0 de 6 atribuídas)
e conclusão (0 de 6 concluídas) são duas perguntas, não quatro.

---

### 9. Atos operacionais irreversíveis acontecem em um clique — **S2/S3**

**Evidência.** "Consolidar as selecionadas" criou 6 Resultados de Etapa normativos sem
confirmação. "Emitir ordem" — sob um texto que diz "Emitir é irreversível… grava um ato imutável" —
executou em um clique. "Remover da comissão" removeu uma avaliadora com 3 avaliações consolidadas
que alimentavam a classificação publicada, com a mensagem verde "Membro removido da comissão."

Compare com Submeter / Homologar / Publicar / Encerrar / Cancelar do Edital, que têm página própria
com "O que este ato provoca".

**E, emitido o sucessor da classificação, a tela do marco não menciona publicação em momento
algum** — enquanto a página pública continuava dizendo "Este é o resultado vigente" com a ordem
antiga.

**Direção de solução.** Estender o padrão que o produto já tem aos atos operacionais, e acrescentar
ao marco o estado que falta: *"Ato vigente emitido às 09:49. A divulgação pública ainda é a de
09:44 — [Publicar este ato]"*.

---

### 10. Os bloqueios são corretos e chegam tarde — **S2, padrão**

Três ocorrências do mesmo padrão:

- **Distribuir**: o painel inteiro fica ativo, e só ao clicar "Propor distribuição" aparece
  "As inscrições ficam abertas até 10/10/2026 às 23:59. Distribuir agora deixaria sem avaliador quem
  se inscrever depois." A mensagem é ótima e não diz o que fazer (o único caminho é Retificar o
  término; "Encerrar" é outro ato, irreversível e mais amplo).
- **Publicar resultado definitivo**: a prévia oferece "Resultado definitivo"; ao confirmar, 422 —
  "O prazo recursal deste marco ainda está aberto: ele se encerra em 16/09/2026 às 23h59." O bloco
  "Verificação de publicabilidade", na mesma prévia, é o lugar dessa frase.
- **Segregação de funções**: quem elaborou e homologou só descobre que não pode publicar na tela de
  publicação. Nem "Submeter" nem "Homologar" mencionam a consequência.

A tela de Comissão faz o oposto, e faz certo: *"Esta comissão ainda não tem presidente. Constituir
sem presidência é permitido, mas nenhuma Etapa pode receber alocação enquanto ninguém responder pelo
trabalho distribuído."* — o impedimento anunciado antes da tentativa. **Esse é o padrão a
generalizar.**

---

## 5. Lacunas conceituais

| Conceito | Como o sistema apresenta | Como o usuário provavelmente interpreta | Problema |
|---|---|---|---|
| **Vagas imediatas** vs **linha do quadro** | duas caixas de número no mesmo cartão; a segunda sem rótulo explicativo visível | "já informei as vagas ali em cima" | D3 — a duplicação é do produto, não do domínio |
| **Marco classificatório** | etapa 5 do assistente, "Onde a ordem entre participantes é produzida" | "não sei o que é um marco" | D2 — conceito legítimo, nome inventado |
| **Marco** (Supervisão) | "Próximos marcos"; "a Etapa está sem marco no cronograma" | confunde com o marco classificatório | D3 — colisão de nomes entre telas |
| **Etapa** | rótulo do passo do assistente ("ETAPA ATUAL") e objeto do domínio ("Etapas de Avaliação") | ambiguidade no mesmo cabeçalho | D3 |
| **Impedimento** | contador "6 com impedimento" e tela "Quem está impedido" | "seis candidatos têm conflito com a banca" | D3 — dois sentidos a dois cliques |
| **Ampla concorrência** | "Qual delas é a ampla concorrência" + "Ampla concorrência (linha geral do quadro)" + Modalidade "Ampla concorrência (AC)" | três coisas com o mesmo nome | D2 — o domínio tem a ambiguidade; a tela a amplifica |
| **Consolidar** | botão, sem nenhuma explicação na tela | "salvar?" | D2 |
| **Providência a jusante** | espécie de decisão de recurso | incompreensível | D3 — jargão de engenharia |
| **Faixa / alvo / excedente** | regra de corte | vocabulário sem tradução | D1/D2 — conceito do domínio, nomes do produto |
| **Prontidão** | coluna da distribuição | — | D3 |
| **Perfil de Vaga** | "Denominação, Localidade, Atribuições, Carga horária, Remuneração, Requisitos" | vocabulário de emprego | D2 — na amostra real a família dominante é curso, e **o código de vaga é a turma**; "Atribuições" e "Remuneração" não existem ali. O portal público já diz "Cargo **ou curso**"; a composição, não |
| **Função** (presidente/membro) vs **papel** (elaborador, gestor…) | duas listas diferentes, em telas diferentes | "por que presidir não é um papel?" | D1, e o sistema **ensina bem**: "presidir uma comissão não atribui trabalho de avaliação" |
| **Emitir** vs **Publicar** | atos distintos, em telas distintas | "já publiquei quando emiti?" | D1 com apresentação D3 — a distinção é do domínio, a separação física das telas é do produto |

---

## 6. Mapa de encontrabilidade

| Intenção | Onde procurei | Onde estava | Esforço |
|---|---|---|---|
| Chegar à área administrativa | "Entrar", no portal público | `/gestao/`, sem link a partir do portal | **E4** |
| Criar um processo seletivo | botão na página inicial da gestão | exatamente ali | E0 |
| Preencher o Edital (só com papel Gestor) | página do Edital | não existe para esse papel; a tela diz "Aguardando quem elabora" e não diz quem é | **E4** |
| Abrir um Edital a partir da lista inicial | o número do Edital na tabela | é texto puro; só há link em Processo → número | **E2** |
| Definir o período de inscrições | etapa 3, Cronograma | etapa 6, Inscrição | **E2** |
| Corrigir "Etapa sem peso declarado" | o botão "Ir para Perfis de Vaga" da pendência | etapa 4, Etapas de Avaliação | **E3** |
| Publicar o resultado | página do marco (Classificação final) | página do *ato*, atrás de "Consultar ato e proveniência" | **E2/E3** |
| Ver os recursos recebidos | página do Edital, Supervisão, cabeçalho | `/gestao/editais/<id>/recursos`, sem link algum | **E4** |
| Criar o Edital do ano seguinte no mesmo Processo | cartão "Editais (N)" do Processo | não existe | **E4** |
| Saber quantas vagas faltam | página do Edital | link "ocupação", ao lado do marco | E1 |
| Montar a comissão | aba "Comissão" do Processo | ali | E0 |
| Dizer quem avalia esta Etapa | "Alocação por Etapa" | ali | E0 |
| Encontrar o trabalho que me foi atribuído | "Minhas Etapas", no cabeçalho | ali | E0 |
| Preparar o sorteio | página do Edital | sob a seção "Classificação" | E1 |
| Corrigir uma publicação | página do Edital | botão "Retificar" | E0 |

---

## 7. Pontos de imprevisibilidade

Configurações cujo efeito só aparece etapas — às vezes semanas — depois:

| Decisão | Onde é tomada | Onde o efeito aparece |
|---|---|---|
| Linha do quadro de vagas em branco | etapa 2 | na Ocupação, depois do resultado publicado |
| "Como a convocação é comunicada" = não declarado | etapa 2 | ao tentar convocar ("o sistema recusa convocar") |
| "Peso" deixado vazio (a tela diz **opcional**) | etapa 4 | na etapa 9, como IMPEDE |
| Etapa sem vínculo a Evento do Cronograma | etapa 4 (dica neutra) | na Supervisão, como "Atenção", com o Edital já imutável |
| Nenhum Evento designado como período de inscrições | etapa 3 (AVISO sem destino) | o Edital publica e nunca recebe inscrição |
| "Admite recurso, no prazo de N dias" | etapa 5 | impede publicar como definitivo, dias depois |
| Elaborar **e** homologar a mesma revisão | atos 1 e 2 | no ato 3, publicação |
| Datas herdadas do Edital de origem | reaproveitamento | no portal, com a inscrição vencida |
| Critério de desempate que aponta a mesma Etapa da nota | etapa 5 | "Empate residual" na classificação, sem explicação |

---

## 8. Complexidade desnecessária

- **"Ativar Processo"** — a publicação do primeiro Edital ativa sozinha
  (`publish_edital.py:737`, "Ativação derivada da publicação do primeiro Edital do Processo"). O
  botão aparece como se fosse o próximo passo. **Eliminar.**
- **Método do sorteio (10 campos)** num marco que não sorteia. **Só quando necessário.**
- **Regra de corte (6 campos)** num marco que não corta. **Só quando necessário.**
- **"Como as pontuações se combinam" e "Normalização"**, obrigatórios, com uma Etapa só — as duas
  opções produzem o mesmo número. **Inferir.**
- **Casas decimais e Arredondamento**, obrigatórios e sem padrão ("Escolha o arredondamento").
  **Padrões seguros: 2 e meio-para-cima.**
- **"Chave" do documento exigido** — identificação estável, "sem espaços", inventada à mão.
  **Derivar do nome, com override.**
- **Coluna MODALIDADE = "Não declarada"** em todas as linhas de um Edital sem modalidades.
  **Ocultar a coluna.**
- **Interstício "Tudo certo / Você pode continuar a inscrição que começou"** — um clique sem
  informação nova, que nem nomeia a seleção. **Eliminar.**
- **Três seletores de modalidade** (ampla concorrência, reversão, convocação) exibidos com zero
  Modalidades declaradas. **Só quando houver a primeira.**

---

## 9. Problemas estruturais

Não se resolvem com polimento:

1. **O número de vagas tem duas fontes** (fricção #1). É modelo, não cosmética.
2. **O Processo não recebe um segundo Edital** (fricção #4). Arquitetura da informação: o objeto
   que a interface ensina não tem operação de crescimento.
3. **A camada explicativa é invisível por decisão de template** (fricção #3). Um `.oculto` decide
   se o produto ensina ou não.
4. **O roteamento de pendências não conhece a etapa 5.** `DESTINO_DA_PENDENCIA`
   (`interface/views.py:461`) não tem entrada para `classificacao`; como todo marco vive sob
   `/profiles/…/milestones/…`, o fallback manda **toda** pendência de marco para "Perfis de Vaga" —
   a etapa mais complexa do assistente é a única inalcançável pelo caminho que existe para responder
   "onde conserto isto?".
5. **A conferência da Retificação usa a representação, e não o domínio** (fricção #7).
6. **A retificação alcança cerca de 40% do que publica, e não declara o que fica de fora.**
   O anexo 16 mede: 38 de 98 campos no Edital com mais conteúdo. `interface/retificacao.py` exclui de propósito
   `stages`, `operation`, `targetKind`, `governedStage`, `continuation`, o tipo do fato — cada uma
   com justificativa escrita no código ("Retificações assim são possíveis pela API"). A tela promete
   "Altere os campos que precisam mudar" e não diz nada disso. Quem procurar "arredondamento",
   "prazo de recurso" ou "método do sorteio" varre a página e conclui que o sistema esqueceu.
   **E `requirements` do Perfil não está lá e não tem justificativa** (`CAMPOS_PERFIL`,
   `retificacao.py:51`) — é conteúdo publicado (`publish_edital.py:203`), é o que decide quem pode
   participar, e só se corrige por API. O teste-guardião
   (`tests/contract/test_retificacoes_api.py:101`) cobre só `CAMPOS_ETAPA`.
7. **A visão global não vê o processo.** A Supervisão, com resultado preliminar publicado e um
   recurso dentro do prazo, mostra inscrições, cronograma e um "Atenção" sobre Etapa sem marco. Não
   menciona classificação, resultado, publicação nem recurso. E a trilha de auditoria está repartida
   em cinco telas sem linha do tempo única.
8. **A ação mais consequente do certame mora numa tela de auditoria.** "Publicar resultado" está na
   página "Ato de classificação", dominada por tabelas de UUID, alcançada por um link que se lê como
   consulta ("Consultar ato e proveniência").

---

## 10. Quick wins

Pequenos, seguros, sem mexer em regra de negócio:

1. Renderizar as dicas `.oculto` como texto auxiliar visível quando o controle não tiver placeholder
   equivalente. *(Uma alteração de template; recupera a camada explicativa inteira.)*
2. Acrescentar `"classificacao"` a `DESTINO_DA_PENDENCIA` e uma entrada específica para
   `…/milestones/…/stages` apontando para `etapas`.
3. Acrescentar `"documentRequirements"` e `"attachments"` a `ORIGEM` (`forms.py:633`) e ao dicionário
   de `revisao.py:164` — hoje a Revisão e a etapa 8 dizem "Composta a partir de **attachments**".
4. Dar à etapa 7 (Anexos) a navegação ‹ Voltar / Salvar rascunho / Avançar › que todas as outras têm.
5. Tornar o número e o título do Edital um link na lista da página inicial.
6. Link "Recursos" na página do Edital para quem tem `recurso:julgar`, e os recursos pendentes em
   "Minhas Etapas".
7. Botão "Publicar resultado" na própria página do marco, ao lado de "Emitir ordem".
8. Corrigir o texto sob "Revisar inscrição", que continua dizendo "depois de anexar o documento que
   falta" com o documento já anexado e o banner verde ao lado.
9. Formatar instantes na zona institucional nas telas de Retificação (hoje `+00:00`).
10. Remover "Ativar Processo" do painel do Processo (a publicação já ativa).
11. Padrões para "Casas decimais" (2) e "Arredondamento" (meio para cima).
12. Uniformizar a apresentação de nota: "8,0000" e "8,00" aparecem na mesma página do candidato.
13. Mover o prazo recursal para a página pública do resultado e para "Acompanhar" — hoje só aparece
    dentro de "Recorrer".
14. Preencher "Concorrência:" no e-mail de confirmação, que hoje sai com o rótulo e sem valor.

---

## 11. Melhorias estruturais

### 11.1 Uma única declaração de vagas

**Problema raiz:** duas fontes para o mesmo número (fricção #1).
**Mudança:** a linha geral do quadro passa a ser derivada de "Vagas imediatas" enquanto o Perfil não
tiver Modalidade; ao acrescentar a primeira Modalidade, o bloco "Quadro de vagas" aparece com a
linha geral já preenchida e pede a repartição, conferindo a soma.
**Fluxos afetados:** composição, retificação, ocupação, convocação, portal.
**Risco:** médio — mexe em conteúdo publicado; exige migração de leitura para Editais antigos.
**Impacto:** destrava as features 016 e 019, hoje inertes em 100% dos Editais do ambiente.
**Por que é melhor que instruir:** a instrução já existe e está escondida; mesmo visível, continuaria
pedindo que o operador digite o mesmo número duas vezes e entenda por quê.

### 11.2 O marco classificatório revelado por perguntas

**Problema raiz:** seis responsabilidades num objeto e numa tela (fricção #6).
**Mudança:** uma pergunta de entrada ("pela pontuação das Etapas · por sorteio") e disclosure
progressivo para corte, recurso e desempate.
**Risco:** baixo — é apresentação; o conteúdo publicado não muda.
**Impacto:** a seleção mais simples passa de 30 controles para cerca de 8.

### 11.3 "Meu trabalho" no lugar de "Minhas Etapas"

**Problema raiz:** cada papel operacional precisa de uma fila, e só o avaliador tem uma (fricções
#5 e #9).
**Mudança:** a mesma tela lista, conforme o ator: Etapas alocadas, recursos a admitir/julgar com
prazo, Editais aguardando homologação ou publicação, marcos com ato emitido e não divulgado,
atribuições órfãs.
**Risco:** baixo.
**Impacto:** resolve a porta de entrada dos recursos, a divergência ato↔publicação e o "não sei o
que está pendente" da §25.

### 11.4 O Edital como objeto que cresce dentro do Processo

**Problema raiz:** fricção #4.
**Mudança:** "Novo Edital neste Processo" no cartão Editais; "Partir de um Edital anterior"
oferecido ali mesmo.
**Risco:** baixo — a capacidade e o comando já existem.
**Impacto:** o modelo que a interface ensina passa a ser operável.

### 11.5 Um renderizador de alteração normativa, usado em todo lugar

**Problema raiz:** fricção #7.
**Mudança:** o renderizador humano que a página pública já usa passa a servir a tela da Retificação,
a de homologação e a de publicação; e ganha o par antes/depois que hoje só a versão técnica tem.
**Risco:** baixo.
**Impacto:** quem assina o ato irreversível lê a data certa.

---

## 12. O que NÃO fazer

- **Não** colocar tooltip no "Quadro de vagas". O problema é haver dois números para a mesma
  pergunta.
- **Não** escrever um manual do "marco classificatório". O problema é o objeto acumular seis
  responsabilidades numa tela só.
- **Não** criar um onboarding para a etapa 5. Ela precisa encolher, não ser narrada.
- **Não** resolver a invisibilidade das dicas com um ícone "?". As dicas já estão escritas e no
  lugar certo — falta deixá-las visíveis.
- **Não** criar um dashboard novo para a visão global. A Supervisão já existe e já é o lugar; o que
  falta é ela enxergar classificação, resultado e recurso.
- **Não** citar Editais externos na microcópia do operador. "O 77/2026 admite — 'até que se
  preencha'; o 14/2026 não", "Nos quatro Editais de sorteio lidos…", "por exemplo, o 8.2 do Edital
  77/2026" e "Numa banca grande, achar uma pessoa não pode depender de rolar" são justificativa de
  projeto, e pertencem à spec. O operador precisa saber o que a escolha provoca, não por que ela
  existe.
- **Não** transformar o 404 de autorização em explicação detalhada. A recusa silenciosa é postura de
  segurança deliberada; o que falta é a tela irmã, que já explica bem, ser alcançada primeiro.

---

## 13. Padrões que devem ser preservados

1. **A página de ato.** "O que este ato provoca", em bullets, com o estado seguinte nomeado, e
   bloco vermelho "Este ato não pode ser desfeito" quando é o caso.
2. **A prévia de publicação de resultado.** Prévia que não grava, verificação de publicabilidade,
   consequências, natureza preliminar/definitiva com padrão seguro, autoridade signatária e **a
   lista exata que o público verá**. É a melhor tela do produto.
3. **"Quem atuou"** no Edital — elaborou / homologou / publicou, com nome e instante.
4. **A validação IMPEDE / AVISO**, com a distinção entre o que barra e o que só avisa.
5. **O impedimento anunciado antes da tentativa**, como na tela de Comissão.
6. **As negativas que ensinam**: "Você chegou aqui pela gestão da comissão, e não por atribuição";
   "presidir uma comissão não atribui trabalho de avaliação"; "A operação não é permitida… Nenhuma
   alteração foi feita."
7. **A proposta de distribuição** com TEM HOJE / RECEBE / FICA COM e "nada foi gravado ainda".
8. **"Resultados da Etapa"**: CONCLUSÃO / ORIGEM / SITUAÇÃO / POR QUÊ / QUEM AVALIOU / QUEM
   CONSOLIDOU / VERSÃO DO EDITAL, com "Habilitada significa exatamente uma coisa".
9. **"O ato vigente está obsoleto"** + "Mudanças posição a posição". Melhor resposta do produto à
   pergunta causal do recurso.
10. **O versionamento público**: "Este resultado foi sucedido… Ver o resultado vigente"; "Este Edital
    foi retificado… veja o que mudou"; "Sua inscrição continua valendo sob a versão que você
    aceitou".
11. **O comprovante de inscrição**: protocolo, código de verificação, SHA-256 por arquivo, **versão
    do Edital aceita** e "O recebimento não implica deferimento".
12. **"Verificar este sorteio"**: cinco conferências nomeadas em português, manifesto JSON e
    verificador independente com a linha de comando pronta.
13. **A modalidade que muda os documentos na hora**, com "A escolha decide quais documentos serão
    pedidos a você".
14. **"Partir de um Edital anterior"**: "O que vem junto" / "O que não vem" lado a lado, e a coluna
    "O QUE TRAZ".
15. **A tela de Retificação**: "Como funciona", IR PARA com contagem, "Só o que eu alterei", e a
    tabela ONDE / CAMPO / VIGENTE HOJE / PASSARÁ A SER.

---

## 14. Backlog priorizado

**O que P0 significa aqui:** risco operacional — o certame pode sair errado, e o erro só aparece
quando já não há como desfazê-lo. Não é "primeira leva de trabalho". Por esse critério, P0 são
três, e não quatro: a microcópia invisível é S3 de altíssimo retorno, mas não põe um Edital
publicado numa situação sem saída, e por isso desce para P1. O item de Recursos é P0 **porque a
`018` está entregue** (140 de 140 tarefas, integrada na `main`): o fluxo de recurso é operacional,
e um fluxo operacional sem porta de entrada é risco, não atrito.

| Prio | Achado | Tipo | Sev. | Esforço | Impacto | Recomendação |
|---|---|---|---|---|---|---|
| **P0** | Quadro de vagas vazio desliga ocupação e convocação | modelo | S4 | M/G | altíssimo | Derivar a linha geral de "Vagas imediatas"; até lá, AVISO na validação e o quadro na Revisão |
| **P0** | Reaproveitamento publica cronograma vencido | estados | S3 | P | alto | Cronograma nasce PENDENTE; AVISO para evento no passado; IMPEDE para inscrição já encerrada |
| **P0** | Recursos sem porta de entrada | encontrabilidade | S3 | P | alto | Link no Edital e fila em "Minhas Etapas" |
| **P1** | Dicas de consequência invisíveis (`.oculto` sem placeholder) | feedback | S3 | P | **altíssimo** | Renderizar como texto auxiliar visível — maior retorno por linha do backlog |
| **P1** | Processo não recebe segundo Edital | arq. informação | S3 | P/M | alto | "Novo Edital neste Processo" |
| **P1** | Pendência de marco roteada para a tela errada | consequência | S3 | P | alto | `classificacao` em `DESTINO_DA_PENDENCIA` |
| **P1** | JSON Pointer e UTC na conferência da Retificação | nomenclatura | S3 | P/M | alto | Reaproveitar o renderizador público; zona institucional |
| **P1** | Julgador não vê o objeto do recurso | contexto | S3 | M | alto | Links para resultado, avaliação, documentos e Edital |
| **P1** | "Publicar resultado" fora da tela do marco | encontrabilidade | S3 | P | alto | Botão no marco + estado "emitido e não divulgado" |
| **P1** | "Impedimento" com dois sentidos | nomenclatura | S3 | P | alto | Renomear o estado de prontidão |
| **P1** | Retificação alcança ~40% dos campos publicados | capacidade | S3 | M | alto | Inventário do anexo antes de codificar campo a campo |
| **P1** | Marco classificatório com 30 controles | densidade | S3 | M | alto | Disclosure por "como a ordem é produzida" |
| **P2** | Atos operacionais sem confirmação | feedback | S2 | P/M | médio | Estender a página de ato a consolidar, emitir e remover membro |
| **P2** | Bloqueios revelados só na tentativa | feedback | S2 | P | médio | Anunciar antes, como faz a tela de Comissão |
| **P2** | Supervisão não vê resultado nem recurso | visão global | S2 | M | médio | Acrescentar classificação, publicação e recursos ao Pulso |
| **P2** | Retificação não declara o que não alcança | estados | S2 | P | médio | Nota explícita nos blocos com campos fora do alcance |
| **P2** | Etapa 7 sem navegação do assistente | consistência | S2 | P | médio | Acrescentar ‹ Voltar / Salvar / Avançar › |
| **P2** | Segregação de funções revelada só ao publicar | consequência | S2 | P | médio | Avisar em "Homologar" |
| **P2** | Distribuição sem nome do candidato | contexto | S2 | P | médio | Nome ao lado do protocolo |
| **P2** | Candidato não vê vagas por modalidade | contexto | S2 | P/M | médio | Quadro por lista na página pública (depende de P0 #1) |
| **P2** | "Parecer — É o parecer que responde a um recurso" | nomenclatura | S2 | P | médio | "Registre o que fundamenta a pontuação. É o que responderá a um eventual recurso." |
| **P2** | Mesa sem link para o Edital | contexto | S2 | P | médio | Link para a versão vigente |
| **P2** | "Empate residual" sem explicação | feedback | S2 | P | médio | Nomear o critério esgotado |
| **P2** | CONCLUÍDA significa "apertei Avançar" | estados | S2 | M | médio | Refletir a validação no selo da etapa |
| **P3** | `attachments` / `documentRequirements` em inglês | nomenclatura | S1 | P | baixo | Completar os dois dicionários |
| **P3** | Edital não abre da lista inicial | encontrabilidade | S1 | P | médio | Tornar número e título links |
| **P3** | Interstício "Tudo certo" | densidade | S1 | P | baixo | Eliminar |
| **P3** | Texto obsoleto sob "Revisar inscrição" | feedback | S1 | P | baixo | Corrigir a condição |
| **P3** | Prosa de projeto e Editais externos na microcópia | nomenclatura | S1 | P | baixo | Mover para a spec |
| **P3** | Contadores redundantes na distribuição | densidade | S2 | P | baixo | Colapsar em cobertura e conclusão |
| **P3** | "Ativar Processo" | config. desnecessária | S2 | P | baixo | Remover |
| **P3** | Formatação de nota (8,0000 / 8,00) | cosmético | S0 | P | baixo | Uniformizar |
| **P3** | "Etapa" nomeia passo e objeto | nomenclatura | S1 | P | baixo | "Passo 4 de 9" no assistente |
| **P3** | Trilha de auditoria em cinco telas | visão global | S2 | M | médio | Linha do tempo única do certame |

---

## 15. Fechamento

### 1. Quais partes uma pessoa consegue hoje compreender apenas usando o sistema?

- **A diferença entre Processo e Edital**, ensinada em uma frase na tela que os cria.
- **O ciclo de vida do Edital** — o stepper, "Quem atuou" e "O que fazer agora" tornam
  elaboração → revisão → homologação → publicação legível sem explicação externa.
- **Que publicar é ato imutável e que a correção é Retificação.** Dito na publicação, repetido no
  Edital publicado, demonstrado na tela de Retificação e visível ao candidato.
- **A organização do trabalho da comissão.** Função e alocação se distinguem sozinhas, e a frase
  "presidir uma comissão não atribui trabalho de avaliação" fecha a questão.
- **A mesa do avaliador.** Fila, situação, próxima pendente, conclusão.
- **O efeito de um recurso sobre a classificação**, graças a "O ato vigente está obsoleto" e à
  tabela de mudanças posição a posição.
- **A jornada inteira do candidato**, incluindo a ideia difícil de que a inscrição vale sob a versão
  aceita.

### 2. Em quais partes é preciso conhecer previamente como o sistema foi pensado?

- **Que "Vagas imediatas" e "Quadro de vagas" são coisas diferentes**, e que só a segunda alimenta
  ocupação e convocação.
- **Que o período de inscrições se designa na etapa 6**, e não no Cronograma.
- **Que "marco classificatório" é onde moram desempate, corte, recurso e método do sorteio.**
- **Que "emitir a ordem" não publica nada**, e que publicar é outro ato, em outra tela.
- **Que existe uma tela de Recursos** — não há link para ela.
- **Que "impedimento", no contador, não é conflito de interesse.**
- **Que a Retificação não alcança alguns campos**, e quais.
- **Que um Processo não pode receber um segundo Edital pela interface**, apesar de a interface
  ensinar o contrário.

### 3. Em quais partes a dificuldade pertence legitimamente ao domínio? (D1)

- **Segregação de funções.** Que elaborar, homologar e publicar sejam atos de pessoas diferentes é
  norma, não produto — e o sistema já explica muito bem *que* é assim.
- **Preliminar vs definitivo, e o prazo recursal.** Não publicar definitivo com prazo aberto é regra
  legal.
- **Eliminatória e classificatória como caracteres independentes.**
- **Quadro parcial e "linha ausente nunca é zero".** A decisão D-006 da `025` é correta; o que não é
  do domínio é ter duas caixas de número no mesmo cartão.
- **Ampla concorrência ter duas grafias** (recorte geral e Modalidade declarada). A ambiguidade
  existe nos Editais reais.
- **Admissibilidade separada de mérito no recurso.**
- **A ideia de "universo comprometido antes da semente"**, no sorteio — irredutível, e muito bem
  apresentada.

### 4. Quais mudanças fariam o sistema ensinar seu próprio modelo durante o uso?

1. **Tornar visível a microcópia que já existe.** O produto escreveu excelentes frases de
   consequência e as escondeu. Só isso já muda o caráter do assistente.
2. **Anunciar o impedimento antes da tentativa**, como a tela de Comissão faz. A frase "nenhuma
   Etapa pode receber alocação enquanto ninguém responder pelo trabalho distribuído" ensina a
   relação comissão→alocação melhor do que qualquer glossário.
3. **Fazer o estado dizer o que falta.** "Ato vigente emitido às 09:49; a divulgação pública ainda é
   a de 09:44" ensina a diferença entre emitir e publicar no momento em que ela importa.
4. **Perguntar antes de mostrar.** "Como a ordem deste marco é produzida?" ensina o que é um marco
   melhor do que 30 campos.
5. **Deixar o "Ir para" acertar o alvo.** Uma pendência que leva ao campo certo ensina a relação
   entre marco e Etapa sem uma palavra a mais.

### 5. Onde um servidor novo travaria amanhã?

Em ordem de probabilidade:

1. **No acesso.** O portal público não leva à gestão. Ele precisa da URL.
2. **Na etapa 5.** Abre "Acrescentar marco", vê o bloco do sorteio e o da regra de corte numa
   seleção que não sorteia nem corta, e para para perguntar.
3. **Em "Casas decimais" e "Arredondamento"**, obrigatórios, sem padrão e sem explicação visível.
4. **Na pendência do peso**, que o manda para a tela errada.
5. **No quadro de vagas** — e este é o pior: ele **não trava**. Publica, recebe inscrições, avalia,
   classifica, divulga o resultado, e trava só no dia de convocar, com o Edital imutável.
6. **Ao precisar do segundo Edital do certame.**
7. **Quando o primeiro recurso chegar**, e não houver por onde vê-lo.

---

## As cinco mudanças que mais aproximariam o produto de "não precisar de manual"

1. **Tornar visíveis as dicas de consequência que já estão escritas** (`.oculto` sem placeholder
   equivalente). Uma alteração de template devolve ao operador a camada explicativa inteira do
   assistente — e é o maior retorno por linha do produto.
2. **Unificar a declaração de vagas.** Enquanto "2 vagas imediatas" e "linha do quadro" forem duas
   perguntas, o operador continuará publicando um número que o sistema não usa — como aconteceu nos
   quatro Editais deste ambiente, inclusive nos três escritos pela equipe.
3. **Revelar o marco classificatório por perguntas, não por formulário.** "Pela pontuação das Etapas
   ou por sorteio?" ensina o conceito e elimina dois terços dos campos.
4. **Dar a cada papel uma fila de trabalho.** "Minhas Etapas" resolveu isso para o avaliador e
   provou que funciona; o julgador de recursos, quem homologa, quem publica e quem emitiu um ato
   ainda não divulgado precisam do mesmo.
5. **Anunciar o bloqueio antes da tentativa, em todo lugar.** O produto já sabe fazer — a tela de
   Comissão é a prova. Generalizar esse padrão para distribuição, publicação definitiva, segregação
   de funções e cronograma reaproveitado transformaria a maior parte das surpresas deste relatório
   em avisos oportunos.

---

## 16. Anexo — campos publicados × campos que a Retificação alcança

A §9.6 registrou que a tela de Retificação não declara o que não alcança. Este anexo mede o
tamanho disso, porque a pergunta normativa — *depois de publicado, tudo o que pode legitimamente
precisar de correção tem caminho de Retificação **pela interface**?* — não se responde por
impressão.

**Método.** Para cada Edital publicado do ambiente, enumerei todo campo escalar do conteúdo
canônico vigente (o mesmo que `publish_edital.py` grava) e comparei com o conjunto de caminhos que
`interface.retificacao.campos_editaveis()` oferece sobre aquele mesmo conteúdo. Identidades foram
colapsadas (`id=*`) para comparar forma, não instância.

| Edital | Campos publicados | Alcançados pela tela | Cobertura |
|---|---:|---:|---:|
| 26/2026 — sorteio, com método declarado | **98** | **38** | 39% |
| 01/2026 — 2 perfis, 2 modalidades, 2 anexos | 96 | 42 | 44% |
| 51/2026 — 2 perfis, 3 Etapas | 87 | 38 | 44% |
| 90/2026 — o do percurso | 81 | 34 | 42% |

O docstring de `campos_editaveis` diz: *"Cobre tudo o que o conteúdo publicado carrega e a
gramática endereça."* No Edital com mais campos, cobre **38 de 98** — e a cobertura fica entre 39%
e 44% nos quatro.

### O que fica de fora com razão

Nem toda diferença é lacuna. Estes casos são legítimos e o código os documenta:

- **Identidade e derivados** — `id`, `key` do documento, `order` de evento, seção e Etapa,
  `status` operacional, `processoCode` e `processoTitle` (são do Processo, não do Edital),
  `artifactHash` (derivado dos bytes), `schemaVersion`.
- **Título das seções** — o catálogo é fixo, e divergência é recusada pela verificação de
  topologia.
- **Tipo do fato declarado** — trocá-lo reinterpretaria valor já congelado.
- **Objeto ausente no conteúdo** (`cutRule: None`, `drawMethod: None`, `vacancyReversion: None`,
  `normativeRule: None`) — endereçar caminho inexistente é recusado, e criar a declaração é
  acréscimo, não alteração. **Tem consequência:** o que não foi declarado na publicação não passa
  a existir por Retificação pela tela. O próprio módulo registra essa lição para `callForm` —
  *"o primeiro Edital publicado com a forma declarada nasceria irretificável nela"* — e ela vale
  igualmente para a regra de corte, o método do sorteio e a reversão.

### O que fica de fora sem justificativa escrita

São campos de norma, que o candidato lê ou que governam o cálculo, ausentes das listas `CAMPOS_*`
sem nenhum comentário explicando a ausência — ao contrário de todas as exclusões deliberadas do
módulo, que a documentam:

| Caminho | O que é | Por que pesa |
|---|---|---|
| `/profiles/…/requirements/[]` | os requisitos de participação | decide **quem pode concorrer**; é o que a página pública exibe sob REQUISITOS |
| `/profiles/…/description` | descrição do Perfil | o candidato lê antes de escolher a vaga |
| `/profiles/…/reserveType` | há cadastro reserva, e se é limitado | o portal publica "com cadastro reserva"; só o *limite* é retificável, não a espécie |
| `/profiles/…/classificationMilestones/…/appealWindow/{admits,durationDays,unit}` | **o prazo recursal publicado** | um Edital que publicou 3 dias e devia publicar 5 não se corrige pela tela |
| `…/rounding/{mode,scale}` | arredondamento e casas decimais | muda posição na ordem |
| `…/operation`, `…/normalization` | como as pontuações se combinam | muda a pontuação combinada |
| `…/stages/[]` | quais Etapas entram na ordem | muda o universo do cálculo |
| `…/tiebreakers/…/{whenMissing, parameters/stageId}` | o critério de desempate em si | só a **ordem** dos critérios é retificável; o critério, não |
| `/schedule/…/location` | onde o evento acontece | é o local da prova — e a `021`, cenário 3, tem como critério de aceitação *"uma Retificação altera o local de um evento"* |
| `/schedule/…/isRegistrationPeriod` | qual Evento é o período de inscrições | publicar o Edital com o Evento errado designado não se conserta pela tela |
| `/stages/…/scheduleEventId` | o vínculo Etapa ↔ Evento | é o que a Supervisão cobra como "Atenção" depois de publicado |
| `/maxInscricoesPorCandidato` | teto de inscrições por pessoa | norma publicada |
| `/profiles/…/competitionModalities/…/normativeRule/{effectiveFrom, rounding/modo}` | vigência e arredondamento do fundamento da reserva | norma publicada |

### Um precedente que o próprio módulo já criou

A justificativa escrita para manter `stages` e `operation` fora é que *"retificá-las por caixa de
texto publicaria regra que o cálculo não interpreta"*. Ela era verdadeira quando o único tipo
disponível era texto — e deixou de ser: `cutRule/tieOutcome` e `callForm` entraram depois como
`REFERENCIA`, *"porque são dois valores fechados, e a referência os oferece conferindo a escolha
contra a lista"*. `operation`, `normalization`, `rounding/mode`, `appealWindow/unit`,
`tiebreakers/whenMissing` e `reserveType` são exatamente da mesma natureza. O obstáculo original
já caiu; a exclusão sobreviveu a ele.

### O que isto sugere para a spec

Não codificar campo a campo. A pergunta a fechar primeiro é normativa, não técnica: **de tudo que
o conteúdo publica, o que pode legitimamente precisar de correção administrativa?** O inventário
acima é a entrada dessa conversa — e o teste-guardião que hoje existe só para `CAMPOS_ETAPA`
(`tests/contract/test_retificacoes_api.py:101`) é a forma natural de a resposta não se perder:
um teste que compare a forma publicada com a forma alcançável e falhe quando nascer um campo novo
sem decisão.
