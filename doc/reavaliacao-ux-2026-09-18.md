# Reavaliação da reauditoria de UX — 18/09/2026

Este documento **não é uma auditoria nova**. É a medição do que andou desde a
[reauditoria exploratória de 16/09/2026](auditoria-exploratoria-ux-2026-09-16.md), feita contra o
código que está na `main`, para servir de linha de base à próxima auditoria.

A pergunta que a reauditoria governou continua sendo a mesma:

> **Uma pessoa consegue compreender, configurar, executar e acompanhar um Processo Seletivo completo
> sem precisar dominar previamente a arquitetura interna do sistema?**

> **Este arquivo foi medido duas vezes no mesmo dia, e as duas leituras estão aqui.** A primeira, de
> manhã, mediu `9539376`: a `032` existia como spec, e tudo que se disse sobre ela era projeção. À
> tarde a `031`, a `032` e a `033` foram implementadas e mergeadas, e esta revisão mede `af97d4c`.
> **As projeções não foram apagadas** — elas viraram a §7, que confere uma a uma o que se previu
> contra o que se observou. Um relatório que reescreve a própria previsão depois do resultado perde
> a única coisa que a torna verificável.

---

## 1. Protocolo e baseline

| Item | Valor |
|---|---|
| Linha de base | `5f37eec` — o commit que a reauditoria de 16/09 auditou |
| Primeira medição (manhã) | `9539376`, com `029` e `030` mergeadas |
| **Estado medido agora** | **`af97d4c`** (`main`), com `029`, `030`, `031`, `032` e `033` mergeadas |
| Código que entrou desde a linha de base | PR #123 (`029`), #124 (`030`), **#130 (`031`)**, **#131 (`032`)**, **#132 (`033`)** e #133 (entradas do `launch.json`) |
| Verificação executada | `make lint check test-pg` no checkout principal → **7213 passando, 12 pulados, zero falhas** (11m15s); `ruff check`, `ruff format --check`, `manage.py check` e `makemigrations --check` limpos |
| Confirmação independente | a árvore de `af97d4c` é **idêntica** à de `37f45f3`, que é a cabeça em que o CI do #132 rodou verde — o que está na `main` é exatamente o que foi testado lá |
| Medição pela interface (manhã) | `runserver` na porta 8032, banco exclusivo `reauditoria_0918`, preparado com `make preparar` (31 de 31 tabelas append-only protegidas) |
| **Especificado e não implementado** | **`034` — ordem por recorte em marco computado** (PR #135, mergeada) e **`035` — sorteio executável** (PR #136, aberta). Nenhuma linha de código das duas |

### Taxonomia de evidência

| Marca | Significado |
|---|---|
| `[UI]` | medido na interface rodando |
| `[CÓDIGO]` | lido na fonte |
| `[SUÍTE]` | afirmado por teste que roda no CI |
| `[NÃO REAUDITADO]` | superfície que a auditoria de 16/09 nunca viu |

**A marca `[PROJEÇÃO]` voltou em 18/09 com endereço — a §13 — e em 19/09 aquele endereço virou
medição.** As features `029` a `033` são código, e tudo que se diz delas é medição. A `034` e a `035`
eram **artefato** quando este arquivo foi escrito; **foram implementadas, percorridas e mescladas no
dia seguinte**, e a §13 agora confronta o que se previu com o que aconteceu.

**A marca não ficou sem endereço: ela mudou de andar.** A §14 é a projeção nova — o que a `036` e a
`037` fecham —, e a §13 é o que se pode conferir contra ela quando as duas entrarem. É a terceira
rodada deste arquivo fazendo o mesmo movimento, e a §7 e a §13 mostram o que as duas anteriores
valeram.

**O que mais continua marcado como projeção** são as **colunas de nota** — a `Proj. manhã` e a
`[PROJ. 18/09]` das §3 e §10 —, porque remedi-las exige percorrer os seis cenários de novo, que é
uma reauditoria e não uma consequência de merge. A §13 diz, por escrito, o que foi medido e o que
não foi.

**Por que separar assim, em vez de misturar.** A primeira versão deste arquivo projetou o efeito da
`032`, e a §7 confere hoje o que aquelas projeções valeram — as quatro notas previstas bateram, e o
fluxo moveu por um motivo a mais do que se previu. É a única maneira de saber se a projeção seguinte
merece crédito, e ela só funciona se a projeção ficar separada da medição.

### Limitações desta reavaliação

1. **Não houve percurso ponta a ponta.** Os seis cenários da reauditoria não foram reencenados aqui.
   O que se mediu foi o **delta** — cada achado contra o código e as telas de hoje. Os percursos que
   existem são os dos quickstarts da `032` e da `033`, registrados nas rastreabilidades delas, e
   estão citados onde sustentam uma linha.
2. **A `029` e a `031` acrescentaram superfície que ninguém auditou.** O Requerimento de Matrícula e
   a exportação para o Registro Acadêmico são jornada nova, e nenhuma nota abaixo as cobre. Onde
   isso importa, está marcado.
3. **Auditoria de UX pelo navegador não substitui revisão de código.** Este relatório já registrou
   um defeito de autorização horizontal sem sintoma visível (§5.4), e a `033` encontrou sete recusas
   de autorização que nenhum artefato descrevia (§8). Nenhum dos dois apareceria em percurso.

---

## 2. Resumo executivo

**A prioridade nº 1 que este relatório apontou de manhã foi implementada no mesmo dia, junto com a
`032`, que já estava especificada — e o produto deixou de entortar na direção em que entortava.**

Das 39 linhas do backlog priorizado da auditoria, **7 fecharam e 6 ficaram parciais**. Dos **6
achados P0**, **três fecharam e dois ficaram parciais** — de manhã eram zero. Duas das três falhas
`S4` fecharam; a terceira (`ACH-47`) segue nomeada e não resolvida, e agora é a mais cara da lista.

**E as duas que faltam para fechar a cauda estão especificadas.** A `034` e a `035` cobrem os quatro
cenários que pararam — dois na convocação, dois na execução do sorteio. **Em 19/09 as duas foram
implementadas e mescladas**, e a **§13** deixou de projetar e passou a medir: os três critérios que
exigiam percurso pela interface foram cumpridos percorrendo.

Quatro frases resumem o estado:

- **Quem pode agir chega à ação.** O Publicador puro — capacidade de publicar resultado, nenhum
  vínculo de comissão — vai da tela do Edital até a divulgação **sem digitar URL**. Era o `ACH-40`,
  e ele tornava inexecutável a segregação de papéis que o próprio produto recomenda.
- **A negativa parou de se disfarçar de inexistência.** Nas portas desta família, recusa de
  autorização responde 403 nomeando **as bases que teriam servido naquela chamada**, e o 404 ficou
  para o que é de outro escopo institucional. Com uma ressalva importante, na §8.
- **O Edital inexecutável não passa mais pela publicação em silêncio.** Perfil sem marco e sorteio
  sem método publicável impedem; corte ausente e reserva sem via de apuração avisam, e avisam **no
  cartão, no momento da decisão**, não só na Revisão.
- **A cauda ainda não fecha para cota nem para sorteio.** A reserva continua sem apuração por
  recorte — e agora a tela **diz isso por escrito** —, e o sorteio continua sem execução.

O diagnóstico central da reauditoria era *o sistema elabora e publica bem, e cede na condução*.
**Ele mudou de forma.** A condução deixou de ser um problema de navegação e virou um problema de
cauda: o caminho existe, quem pode percorrê-lo chega ao fim dele, e o que falta é o ato do fim para
dois dos cinco cenários da amostra.

---

## 3. Notas (0–10)

> **A coluna *Pós-034+035* é a projeção de 18/09, e assim permanece.** Ela lê requisito, e não
> comportamento. As duas features entraram em 19/09 e a §13 mede o que elas fecharam — mas **as notas
> não foram remedidas**, porque isso exige percorrer os seis cenários outra vez. A coluna fica como
> previsão registrada, para ser conferida na próxima reauditoria.

| Dimensão | 16/09 | manhã | Proj. manhã | **Agora** | `[PROJ. 18/09]` pós-`034`+`035` | Justificativa do movimento até agora |
|---|---|---|---|---|---|---|
| Clareza conceitual | 7 | **9** | 9 | **9** | 9 | `[UI]` Os cinco conceitos ganharam definição no primeiro uso; a assimetria Etapa×marco está escrita na etapa de Classificação. A `032` levou *geração* a duas telas que não a usavam, e lá ela nasce definida. Sobra o rótulo `Peso (opcional)` que vira impeditivo |
| Encontrabilidade | 7 | 7 | 7 | **8** | 8 | `[CÓDIGO]` Das três falhas nomeadas, **uma fechou**: *publicar resultado (sem caminho)* era o `ACH-40`. O **link do corte continua condicional** e o período de inscrições segue intocado — por isso 8 e não 9 |
| Previsibilidade | 5 | **6** | 9 | **9** | 9 | Projeção confirmada. Os quatro achados de executabilidade entraram; cada um nomeia entidade, falta e a etapa em que a correção é feita |
| **Fluxo ponta a ponta** | **4** | **4** | 6 | **6** | **8** | Projeção confirmada, **e por um motivo a mais do que se previu** — ver §7 |
| Generalização entre famílias | 7 | 7 | 7 | **7** | 7 | O modelo não mudou. O custo de autoria caiu: num Edital de 7 polos o método do sorteio passou de 7 declarações (98 campos) a 1 (9 campos) |
| Organização do trabalho | 7 | 7 | 7 | **7\*** | 7\* | `ACH-60` intocado: alocação por Etapa, distribuição sem filtro por polo ou modalidade. \*`[NÃO REAUDITADO]` A `031` acrescentou a exportação para o Registro Acadêmico |
| Experiência do candidato | 8\* | 8\* | 8\* | **8\*** | 8\* | \*`[NÃO REAUDITADO]` O Requerimento de Matrícula da `029` continua sem auditoria de UX |
| Avaliação | 9 | 9 | 9 | **9** | 9 | Intocado, e continua sendo o melhor artefato do produto |
| Resultado e publicação | 8 | 8 | 9 | **9** | 9 | `[UI]` O documento imprime os sete dados do método do sorteio e declara como a ordem nasce; o marco que sorteia parou de afirmar combinação de pontuações que não existe |
| Recuperação de erros | 7 | 7 | 8 | **8** | **9** | O erro passa a aparecer **antes** da publicação — recuperação antes do dano, e publicação é ato imutável — e o 404 mudo fechou **nas portas**. Sete recusas fora delas seguem em 404: é por isso que não é 9 |
| Visão global | 5 | 5 | 5 | **5** | 5 | `ACH-25` e os oito contadores concorrentes, intocados |

**Não se tira média.** 9 na avaliação e 6 no fluxo ponta a ponta convivem, e continua sendo essa a
forma do produto — só que a distância entre as duas pontas encolheu pela primeira vez.

**Quatro dimensões moveram desde 16/09. Cinco das onze seguem intocadas.**

---

## 4. O que a `030` fechou — medido, não declarado

### 4.1 O cartão do marco, contado no DOM

`[UI]` Edital reaproveitado, um Perfil, marco novo, sem abrir disclosure nenhum:

| | Antes (`5f37eec`) | Hoje |
|---|---|---|
| Controles no cartão, total | **28** | **17** (27 se a ordem for por sorteio) |
| Controles na chegada, fora de bloco colapsado | **7** | **6** |
| Desses, já preenchidos | 0 | **4** |
| **Perguntas que restam** | **7** | **2** |

As duas que restam são *como a ordem deste marco é produzida* e *quais Etapas entram na ordem*.
Chegam preenchidos: casas decimais (`2`), arredondamento (`meio para cima`), código e denominação,
os dois derivados do Perfil e editáveis.

**Uma ressalva de leitura que o próprio relatório precisa registrar.** Os "28" da auditoria e os "6"
do critério `SC-138` **não medem a mesma coisa**. Contei o template antigo: ele emitia 28 controles
não-ocultos no total, dos quais 7 fora dos blocos colapsados. O critério da spec conta só o que está
visível na chegada. Comparando igual com igual, o ganho é **28 → 17** no total e **7 → 6** na
chegada — e **7 → 2** em respostas que faltam, que é a medida que importa para quem monta o Edital.
O ganho real é maior do que a contagem sugere; só não é 28 → 6.

### 4.2 Os achados que fecharam

| Achado | O que era | Estado |
|---|---|---|
| `ACH-10` | 28 controles; duas decisões vazias com uma Etapa; duas obrigatórias sem padrão | ✅ `[UI]` |
| `ACH-09` | a assimetria Etapa→Edital × marco→Perfil nunca explicada | ✅ `[UI]` — a frase está na tela |
| `ACH-36` | "consolidar" sem definição no ponto de uso | ✅ `[CÓDIGO]` — `<dfn>` ao lado do botão, na tela de distribuição |
| `ACH-04` | a explicação desgrudou do campo | ✅ `[UI]` — a ajuda só existe com marco na tela, e as 8 âncoras resolvem para os campos certos |
| `ACH-48` | o marco de sorteio exigia Etapa, contra a ajuda da própria tela | ✅ `[UI]` — o `*` sumiu, e a tela diz que o sorteio pode não ter Etapa alguma |

### 4.3 Os parciais

| Achado | O que fechou | O que ficou |
|---|---|---|
| `ACH-05` | "qual é a ampla concorrência" e "reversão de vaga reservada" só aparecem depois da primeira Modalidade | "como a convocação é comunicada" continua sendo perguntada na composição, e é decisão de fase muito posterior |
| `ACH-61` | o método do sorteio declarado **uma vez por Edital** em vez de uma por marco | A densidade da tela não caiu — os blocos continuam existindo, colapsados. E a etapa de Perfis com 7 polos (18.943 px, 399 controles) está intocada |

### 4.4 Um ganho que a auditoria não tinha achado

`[CÓDIGO]` A revisão da própria `030` encontrou o que a auditoria não viu: `_edital_do_fragmento`
filtrava o Edital por `pk`, sem ator e sem escopo. Quem soubesse o UUID lia, por qualquer fragmento
do assistente, as Etapas, os fatos declarados e — pela derivação nova — o código e a denominação dos
Perfis de um Edital de outra unidade. Fechado com a mesma autorização da tela.

É um lembrete de método: **auditoria de UX pelo navegador não substitui revisão de código**. O
defeito era de autorização horizontal e não tinha sintoma visível.

---

## 5. O que a `032` entregou — executabilidade antes de publicar

`[SUÍTE]` `[UI]` PR #131. Quatro achados da mesma família: o Edital chega à publicação sem que
ninguém pergunte se ele é **executável**, e publicação é ato imutável.

| Achado | Como fechou | Severidade |
|---|---|---|
| `ACH-49` — publica Edital sem marco algum | impeditivo `profile_without_milestone`, só no ato de publicação | S4 ✅ |
| `ACH-50` — o documento omite a regra do sorteio | o documento passou a declarar **como a ordem nasce** e a imprimir os sete campos do método; marco que sorteia sem método publicável **não publica** | S4 ✅ |
| `ACH-46` — convocação inalcançável sem corte | aviso que nomeia a cadeia inteira — sem corte não há geração, sem geração não há faixa, sem faixa não há convocação —, dito **no cartão, no momento da decisão** | P1 ✅ |
| `ACH-47` — reserva publicada sem via de apuração | **nomeado, não resolvido** — ver abaixo | S4 🟡 |

**Três decisões de desenho que valem registro:**

1. **Impeditivo só no ato de publicação.** Gravar rascunho inexecutável continua possível, e
   Retificação do acervo continua aceita. A regra nova não pode tornar irretificável um Edital que
   já está publicado — seria criar um estado de que não se sai.
2. **O aviso do corte distingue duas coisas que pareciam uma.** *Ausência de regra* e *regra que
   declara não governar Etapa alguma* deixaram de ser o mesmo caso. É o que faz o Edital 69/2026 —
   que legitimamente sorteia, publica e convoca sem análise no meio — sair limpo.
3. **A razão ocupa o lugar do botão, e não um `disabled`.** A auditoria encontrou três botões
   idênticos de ocupação, dos quais dois sempre falhavam. Onde a ação não pode existir, a tela diz
   **a causa** — não o sintoma, que é o que a pessoa já está vendo.

### `ACH-47` sai nomeado, e a tela admite isso por escrito

A emissão de ordem por lista em marco computado continua não existindo. O que mudou é que a tela de
ocupação deixou de oferecer a ação e passou a dizer: *"A ordem deste marco é emitida em lista única,
e por isso este recorte não recebe ordem própria… A apuração deste recorte acontece fora do
sistema."*

**É honesto e é uma admissão.** A decisão de tratar por aviso e não por impedimento foi tomada com a
amostra real na mão: 57/2026, 28/2026 e 173/2025 declaram reserva em marco computado, e para eles a
publicação é a única parte da jornada que hoje funciona, porque a apuração por recorte já acontece
fora do sistema. Impedir retiraria o que funciona sem consertar o que não funciona.

### A varredura contra a amostra real

A `032` varreu os doze Editais da
[avaliação de capacidade](avaliacao-de-capacidade-editais-2026-09-12.md), um a um, e a varredura é o
que sustenta a decisão acima em vez de repeti-la de memória:

- **Nenhum impedimento novo alcança a amostra real.** Os dois achados impeditivos não disparam em
  Edital nenhum dos doze — todos declaram marco, e todos os que sorteiam publicam o método.
- **Os três avisos de reserva são exatamente os três que a spec nomeia.**
- **O 69/2026 sai limpo**, e era o risco nomeado na tabela de riscos do plano.

---

## 6. O que a `033` entregou — navegação por capacidade

`[SUÍTE]` `[UI]` PR #132. O produto tem **dois eixos de autorização** e isso é correto: papel
institucional e vínculo de comissão. O defeito era que a **navegação** era montada por um eixo
enquanto as **permissões** eram conferidas pelo outro.

| Achado | Como fechou | Severidade |
|---|---|---|
| `ACH-40` — publicador sem caminho até publicar resultado | `_marcos_publicados` deriva **por destino**, e não por uma porta escolhida de antemão | **S3 / P0** ✅ |
| `ACH-35` — negativa por vínculo vira 404 mudo | `require_authorization_base`, ponto único de recusa por base composta, ao lado de `require_permission` | S2 / P1 ✅ |
| `ACH-38` — a presidência mandada divulgar trava sem saber a quem pedir | a tela do ato nomeia a capacidade que resolve, na formulação que a tela do Edital já praticava | S2 / P1 ✅ |

**O buraco era de vocabulário da camada de segurança.** `require_permission` sabe recusar **uma
capacidade nomeada**; não sabe expressar *"esta permissão **ou** aquele vínculo, cada um bastando
sozinho"*. Quatro portas perguntam exatamente isso, e as quatro improvisaram o mesmo `raise Http404`
— improvisaram igual porque o buraco era o mesmo.

Três invariantes que a feature fixou, e que valem mais do que os três achados:

- **O que protege o escopo institucional é o filtro na própria consulta**, não a ordem de avaliação.
  Objeto de outra unidade e objeto inexistente caem no mesmo `is None` e são indistinguíveis. Há
  teste que dá ao ator **a capacidade que a tela exige** para pegar quem remover esse filtro.
- **O conjunto de bases que teriam servido é de quem chama, não da porta.** Duas portas têm modo, e
  em cada uma o modo muda o conjunto aceito. Recusa que assuma conjunto fixo mente em metade das
  chamadas.
- **Uma formulação só.** A varredura que prende isso pegou uma segunda gramática **pré-existente**,
  em que uma tela dizia "Solicite" onde outra dizia "peça" para o mesmo pedido.

### O que a feature prometeu não mexer, e como se sabe que não mexeu

A recusa é superfície de segurança, e a feature **altera testes que passavam**. A mudança permitida
foi de um tipo só: trocar o status esperado, de 404 para 403.

| | |
|---|---|
| Casos removidos | **zero** |
| Casos que passaram a esperar sucesso onde esperavam recusa | **zero** |
| Casos com só o status alterado | **20** (4 renomeados, porque o nome afirmava a doutrina antiga) |
| Asserções sobre **quem entra** | intactas, conferidas uma a uma |

A conferência foi mecânica e caso a caso, contra um "antes" **versionado**, para que o revisor possa
refazê-la. A [rastreabilidade da feature](../specs/033-navegacao-por-capacidade/rastreabilidade.md)
traz uma linha por teste alterado, **com o motivo** — é o que separa corrigir gramática de afrouxar
autorização, e sem ela o revisor teria de inferir a diferença lendo o diff.

Ela também registra que a conferência caso a caso pegou um `in (302, 403, 404)` escrito durante a
própria feature: **alargar um conjunto aceito é enfraquecer a asserção**, e a contagem de testes
teria ficado idêntica.

---

## 7. As projeções da manhã, conferidas

Esta seção existe porque a primeira versão deste arquivo fez previsões, e um relatório que as apaga
depois do resultado não serve de linha de base para nada.

| O que se previu de manhã | O que se observou | Veredito |
|---|---|---|
| Previsibilidade 6 → 9 | 9 | ✅ |
| Resultado e publicação 8 → 9 | 9 | ✅ |
| Recuperação de erros 7 → 8 | 8, e por dois motivos em vez de um | ✅ |
| Fluxo ponta a ponta 4 → 6 | 6 | ✅ **com um motivo a mais** |
| `ACH-47` sai nomeado e não resolvido | exatamente isso, e a tela o diz por escrito | ✅ |
| "Navegação por capacidade é a melhor relação esforço/retorno que sobrou" | quatro arquivos de produção e quatro templates fecharam um P0 e dois P1 | ✅ |

**O motivo a mais, no fluxo.** A previsão era que a `032` desbloquearia o cenário 1 por fazer a
pessoa declarar a regra de corte — e desbloqueou. O que não estava previsto é que a `031` retiraria
a **redigitação** da passagem para a matrícula: 34 colunas preenchidas à mão, linha por linha, a
partir de dado que o sistema já guarda em coluna. A cauda **depois** da convocação ficou real no
mesmo dia em que a convocação deixou de ser um beco para o Edital simples.

**E uma correção que esta seção precisa carregar.** A primeira versão deste relatório afirmou, mais
cedo no mesmo dia, que a `032` era *"uma feature de previsibilidade, não de fluxo"*. Estava errado, e
a própria primeira versão já o corrigia: a cadeia do `ACH-46` depende de um elo opcional, e fazer a
pessoa declarar a regra é o que move o fluxo. Fica registrado porque o erro é instrutivo — uma
feature de validação moveu uma dimensão de **navegação**, e nenhum requisito dela diz isso.

---

## 8. A parada de escopo da `033` — sete recusas que ninguém tinha descrito

Esta é a descoberta mais importante das duas features, e ela **não é um defeito corrigido**: é um
defeito medido, dimensionado e deixado de fora por decisão registrada.

A `033` tinha um portão antes da implementação: inventariar as negativas de `interface/views.py` por
varredura de AST e **parar** se aparecesse recusa de autorização fora das portas descritas. O
[inventário](../specs/033-navegacao-por-capacidade/inventario-das-negativas.md) classificou as **75**
negativas pelo `if` que guarda cada uma — não pela leitura da definição da função, que foi o que
produziu três erros de medição nas versões anteriores da spec.

| Classe | Quantas |
|---|---|
| Propagação de 404 que o **domínio** declarou, depois de a porta já ter autorizado | 23 |
| Escopo institucional ∪ objeto inexistente — indistinguíveis porque a consulta filtra por escopo | 22 |
| Objeto inexistente puro | 17 |
| **Recusa de autorização** | **11** |
| Estado do agregado · não autenticado | 2 |

Das **11** recusas de autorização, **quatro** eram as portas que os artefatos descreviam. **Sete não
estavam descritas em lugar nenhum**: `criar_edital`, `anexo_do_rascunho`, `reaproveitar`,
`supervisao`, `minha_etapa` e as duas da mesa do avaliador, decididas fora de `views.py`.

**Nenhuma delas é descuido.** Cada uma justifica o 404 no próprio comentário, e três citam doutrina
de spec anterior por identificador — a `022` documenta que *"tudo o que o ator não alcança responde a
mesma coisa que um Processo inexistente responderia"*. E `mesa._autorizar` tem argumento próprio a
favor do 404 uniforme: o que ela esconde é a inscrição **de outro avaliador**, e distinguir ali
aproxima um oráculo de enumeração.

**A decisão foi manter o escopo nas quatro portas**, e recortar o critério de sucesso a elas.
Consequência honesta para este relatório: **o "404 mudo" não foi extinto como classe.** Três das
sete decidem escopo e vínculo na mesma resposta — que é exatamente o trabalho que a `033` fez na
porta da distribuição, e que nenhuma tarefa descrevia para elas.

### O guarda que sobrou, e que muda a postura de manutenção

A feature deixou um detector: a suíte reprova quando aparece `raise Http404` em função que não está
no inventário classificado. Ele **não julga a gramática** — obriga alguém a olhar.

Disparou na primeira oportunidade real, antes de a feature entrar: ao integrar a `main`, a `031`
trouxe uma view que responde "não encontrado" e não estava no inventário. Ela está **certa** — a
consulta filtra por escopo, e a autorização vai por `require_permission`, que responde 403. É o ponto
inteiro: uma porta escrita com a gramática antiga teria entrado pela mesma via, e a diferença é que
alguém teria de **escrever** que ela responde 404 a recusa de autorização.

Sem isso, o critério valeria para 18/09/2026 e para mais nenhum dia.

---

## 9. Os achados que continuam abertos

| Achado | Estado | Conferência |
|---|---|---|
| `ACH-47` — reserva publicada sem via de apuração | 🟡 **nomeado** | `[CÓDIGO]` a emissão por lista não existe; a tela diz que a apuração acontece fora do sistema |
| `ACH-55` — método do sorteio em prosa, não computável | 🔴 | intocado |
| `ACH-51` — fonte da semente em texto livre | 🟡 | continua texto livre, mas em **um** lugar em vez de sete |
| `ACH-46` — o link do corte continua condicional | 🟡 **parcial** | `[CÓDIGO]` a cadeia é explicada na composição e na ocupação, mas o destino do corte segue sob `if cutRule` — a parte (c) da melhoria 13.1 |
| `ACH-43` / `ACH-42` — o julgador sem a prova, o parecer sem chegar | 🔴 | intocados |
| `ACH-41` · `ACH-13` · `ACH-18` — fontes normativas que ninguém confronta | 🔴 | intocados |
| `ACH-60` — a organização do trabalho não conhece o Perfil | 🔴 | intocado |
| `ACH-25` — a visão global some com o Processo vivo | 🔴 | intocado |
| `ACH-16` — `Peso (opcional)` que impede | 🔴 | `_etapa.html` inalterado |
| `ACH-39` / `ACH-31` / `ACH-45` — UUID e vocabulário de máquina nas telas de ato | 🔴 | intocados |
| `ACH-02` — o gestor que criou o Edital não sabe o que falta nem a quem pedir | 🔴 | `[CÓDIGO]` |
| `ACH-30` — "Correções ocorrem por Retificação", sem a ação e sem dizer quem pode | 🔴 | `[CÓDIGO]` `detalhe.html:66`, inalterado |
| `ACH-01` — o caminho da raiz pública para a gestão | 🔴 | intocado |
| `ACH-08` — "Evento vencido" olha o início, não o término | 🔴 | intocado |

**Contagem, feita linha a linha contra a tabela do §16 da auditoria** — e não por achado, porque
seis linhas agrupam mais de um:

| | 16/09 | 18/09 manhã | **Agora** |
|---|---|---|---|
| Linhas fechadas | 0 | 5\* | **7** |
| Linhas parciais | 0 | 2\* | **6** |
| Linhas abertas | 39 | 32\* | **25** |
| **Dos 6 `P0`** | 0 | **0** | **3 fechados, 2 parciais, 1 aberto** |

\*A primeira versão deste arquivo contou **achados**, e não linhas; as duas contagens não batem
porque `ACH-09` não tem linha própria e `ACH-10/05` é uma linha só, hoje parcial. A contagem por
linha é a que se pode refazer contra a tabela da auditoria, e é a que fica.

As três linhas `P0` que fecharam são `ACH-49`, `ACH-50` e `ACH-40`. As duas parciais são `ACH-47`
(nomeado) e `ACH-46` (a cadeia é explicada, o link do corte continua condicional). A que segue
aberta é `ACH-43` — o julgador que decide sem a prova.

---

## 10. Os problemas estruturais

| | Estado | `[MEDIÇÃO 19/09]` pós-`034`+`035` | Observação |
|---|---|---|---|
| **E-5** · a explicação desgrudou do campo | ✅ **resolvido** | ✅ | `030` |
| **E-7** · a validação não pergunta se o Edital é executável | ✅ **resolvido** | ✅ | `032` — 3 dos 4 achados; `ACH-47` nomeado e deixado de fora por decisão |
| **E-2** · autorização e navegação discordam | ✅ **resolvido, com ressalva** | ✅ | `033` — `ACH-40`, `ACH-35` e `ACH-38` fechados; **sete recusas fora das portas mantêm a gramática antiga** (§8) |
| **E-1** · a cauda do processo não fecha | 🟡 **parcial** | **✅ resolvido** | o cenário simples fecha; reserva (`ACH-47`) e sorteio (`ACH-51`/`ACH-55`) seguem |
| **E-3** · duas gramáticas para o mesmo fato | 🔴 intocado | 🔴 | `ACH-39`, `ACH-31`, `ACH-45` |
| **E-4** · fontes normativas que ninguém confronta | 🔴 intocado | 🔴 | `ACH-41`, `ACH-13`, `ACH-18` |
| **E-6** · a visão global some com o Processo vivo | 🔴 intocado | 🔴 | `ACH-25` |

**Três de sete resolvidos** — um deles com ressalva registrada —, **um parcial, três intactos.** Eram
dois de manhã, e um dos dois era projeção.

`[MEDIÇÃO 19/09]` **Depois da `034` e da `035`, quatro de sete**, e o que fecha é o `E-1` — a cauda
que não fechava, e que era metade do diagnóstico central. **Não é mais leitura de requisito**: os
percursos das duas features atravessaram a convocação pelos três recortes e o sorteio do congelamento
à verificação pública. Os três que restam atravessaram **cinco** features sem serem tocados. Ver §13.

---

## 11. As melhorias do §13 da auditoria, uma a uma

| Melhoria | Estado |
|---|---|
| **13.3** navegação derivada da permissão | ✅ `033` |
| **13.7** executabilidade antes de publicar | ✅ `032` |
| **13.1** tornar a convocação alcançável | **2 de 3** — (a) a ocupação não oferece faixa onde não pode haver, e explica a cadeia ✅; (b) a etapa 5 declara que sem corte não há convocação ✅; **(c) o link do corte continua condicionado ao `cutRule`** ❌, e a `033` o declarou fora de escopo |
| **13.2** ato de instrução do recurso | 🔴 |
| **13.4** renderizador normativo único | 🔴 |
| **13.5** validação entre fontes normativas | 🔴 |
| **13.6** painel de condução do Processo vivo | 🔴 |
| **Quick win 1** — "peça a alguém" nos três bloqueios que calam | **1 de 3** — `ACH-38` fechou. `ACH-02` e `ACH-30` seguem |

---

## 12. O mapa da jornada

```
concepção 🟢 → configuração 🟡 → publicação 🟢 → inscrição 🟢 → comissão 🟢 →
avaliação 🟢 → consolidação 🟢 → classificação 🟢 → resultado preliminar 🟢 →
recursos 🟡 → resultado final 🟡 → convocação 🟡 → matrícula 🟢* → Retificação 🟢
```

| Trecho | 16/09 | 18/09 manhã | **Agora** | Nota |
|---|---|---|---|---|
| Achar a gestão | 🟡 | 🟡 | 🟡 | `ACH-01` |
| Compor Perfil | 🟡 | 🟡 | 🟡 | falta tirar "como a convocação é comunicada" da composição |
| Cronograma | 🟡 | 🟡 | 🟡 | `ACH-08` |
| Classificação (marco) | 🔴 | 🟡 | 🟡 | sobra o `Peso (opcional)` que impede |
| Distribuição | 🟢 | 🟢 | 🟢 | ganhou a definição de "Consolidar" ao lado do botão |
| **Classificação e divulgação** | 🟡 | 🟡 | **🟢** | o Publicador puro chega sem digitar URL |
| **Convocação / suplência** | ⛔ | ⛔ | **🟡** | alcançável em Edital bem composto; reserva sem apuração, não |
| **Matrícula** | — | — | **🟢\*** | \*`[NÃO REAUDITADO]` superfície nova, `029` + `031` |
| Recurso | 🟡 | 🟡 | 🟡 | `ACH-43` intocado |

`[MEDIÇÃO 19/09]` **Depois da `034` e da `035`**: a convocação vai de 🟡 a **🟢** — os três botões de
apurar a ocupação foram clicados e os três concluíram —, e o sorteio deixa de ser o fim da linha nos
cenários 3 e 5. O **recurso** continua 🟡, e é o único trecho de modelo de fluxo ainda quebrado — com
a `036` **em implementação** para fechá-lo. Ver §13.

---

## 13. `[MEDIÇÃO]` O que a `034` e a `035` fecharam — e o que a projeção acertou

**Esta seção era projeção até 19/09/2026.** As duas features foram implementadas, percorridas e
mescladas na `main`, e o texto abaixo substitui a leitura de requisito pela medição. **A projeção
anterior fica registrada no histórico deste arquivo**, pelo mesmo motivo que a §7 registra a da
manhã: o que vale saber não é que ela existiu, é onde ela errou.

### O que entrou, e quando

| | Spec | Implementação | Estado |
|---|---|---|---|
| **`034`** Ordem por recorte em marco computado | PR #135 | PR #138 | mesclada — `dd71d46` |
| **`035`** Sorteio executável | PR #136 | PR #139 | mesclada — `9fe57b6` |
| **`036`** Instrução do recurso | PR #140 | em curso | spec mesclada — `2beb2d9` |

A `036` não estava na projeção: ela nasceu depois, fecha o `ACH-43` e o `ACH-42`, e é **o último
`P0`** — o mesmo que esta seção previa que sobraria.

### A suíte, medida nas duas pontas

| Momento | Passando | Pulados |
|---|---|---|
| linha de base, antes da `034` | 7213 | 12 |
| depois da `034`, na worktree dela | 7284 | 11 |
| depois da `035`, na worktree dela | 7267 | 12 |
| **na `main`, com as duas** | **7343** | **11** |

**+130 casos**, e o pulado que virou executado é da `034` — não é soma de superfície nova, é um caso
que passou a poder rodar.

### O que a projeção acertou: a cauda fecha, e foi percorrida

**Não é inferência de requisito.** Os critérios que exigiam percurso pela interface foram cumpridos
percorrendo:

- **`SC-169`** — o Edital de quadro 7/1/2 vai da classificação à convocação **pelos três recortes**,
  pela interface administrativa, sem shell e sem banco;
- **`SC-170`** — os três botões *"Apurar a ocupação deste recorte"* foram clicados, e **os três
  concluíram**. Zero ações oferecidas que sempre falham;
- **`SC-176`** — os cenários 3 e 5 do sorteio chegam ao fim, **do congelamento à verificação
  pública**.

O problema estrutural `E-1` — *a cauda do certame não fecha* — fecha para as três famílias da
amostra real. **Quatro dos sete estruturais resolvidos**, como projetado.

### O que a projeção não viu: dois achados novos, nascidos do percurso

**1. A Retificação não acrescenta Modalidade de Concorrência.** A tela acrescenta Perfil, linha do
quadro, Evento e Anexo; cada Modalidade existente só oferece *"Remover do Edital"*. Metade do
cenário 5.2 da `034` ficou **inexequível pela interface**, e foi registrada como tal — com a metade
que a interface alcança percorrida. Consequência prática: um Perfil que declara cotas e não aponta a
ampla **não recebe inscrição de não-cotista**, e não há como corrigi-lo por Retificação.

**2. O que a ressalva 1 dizia era menor do que o que ela é.** A projeção lera **quatro** Editais de
sorteio; a varredura da `035` leu **dez** — toda a amostra que sorteia, incluindo os dois anteriores
a 2026.

**Dez de dez não declaram ocorrência de fonte externa.** Todos publicam a semente **depois**, e a
cláusula é a mesma palavra por palavra: *"Semente utilizada: xxxxxxxxxxxxx"*, ao fim da página do
sorteio. Não é omissão de alguns Editais — **é a prática inteira**.

A diferença entre *"o sorteio funciona"* e *"o sorteio do Cefor funciona"* continua sendo pergunta de
governança, e agora está medida em dez casos em vez de quatro. **A `035` a registrou e não a
respondeu**, que é o que ela devia fazer.

### As três ressalvas, conferidas uma a uma

| Ressalva de 18/09 | Desfecho |
|---|---|
| **1.** os Editais reais não usam o modelo do sorteio | **confirmada, e maior**: 10 de 10, não 4 de 4 |
| **2.** verificação pública passa a fechar, mas é projeção | **percorrida** — `SC-176`, do congelamento à verificação |
| **3.** o portão da `034` pode reabrir o escopo | **fechou limpo** — `SC-169` a `SC-175` cumpridos, nenhuma migration |

### O que continua sendo projeção, e fica marcado como tal

**As notas não foram remedidas.** *Fluxo ponta a ponta 6 → 8* e *Recuperação de erros 8 → 9* eram
leitura desta seção, e reconferi-las exige **percorrer os seis cenários de novo**, que é uma
reauditoria e não uma consequência de merge. O que está medido é que os cenários bloqueados
**destravaram**; o quanto isso vale na escala das notas, não.

**O gargalo mudou de lugar, e isso está medido:** não é mais a cauda. Com a `036` em implementação, o
que resta são bordas — a microcópia que cala, o link do corte que some, o `Peso (opcional)` que
impede — e **a visão global**, que continua em **5** e é a nota mais baixa por margem larga.

### Uma nota de ambiente, porque ela mudou o método

Entre 18 e 19/09 a CI do repositório **falhava em 2–4 segundos sem listar passo algum** — faturamento,
não código —, e as três features foram validadas **localmente**, com a suíte inteira contra
PostgreSQL. Em 19/09 a CI **voltou**: o job `test` fecha verde em ~24 minutos. Fica registrado porque
a `034`, a `035` e a `036` foram mescladas sob dois regimes de verificação diferentes, e quem
auditar os merges precisa saber qual valia em cada um.

---

## 14. `[PROJEÇÃO]` O que a `036` e a `037` fecham

**Nada nesta seção é medição.** A `036` está em implementação; a `037` é spec num PR aberto. O que se
diz aqui é leitura de requisito, e fica registrado pela mesma razão que a §13 registra a projeção
anterior: **é a única maneira de saber se a projeção seguinte merece crédito.**

A ordem suposta é `036` → `037`, que é a da fila.

### O titular: os seis `P0` fecham

É a primeira vez desde 16/09.

| | 16/09 | **hoje, medido** | `[PROJ.]` pós-`036` | `[PROJ.]` pós-`037` |
|---|---|---|---|---|
| `P0` fechados | 0 | **4** | 5 | **6** |
| `P0` parciais | 0 | 1 — `ACH-46` | 1 | **0** |
| `P0` abertos | 6 | 1 — `ACH-43` | 0 | **0** |

A `036` fecha o `ACH-43`, o último aberto, e o `ACH-42` junto. A `037` fecha a parte **(c)** do
`ACH-46` — o único trecho parcial que resta — mais `ACH-30`, `ACH-08`, `ACH-16` e o que sobrar do
`ACH-02`, que a medição da `037` já encontrou **meio fechado**.

### E o número que **não** se move: quatro de sete

**Nenhuma das duas fecha raiz estrutural nova.**

| Raiz | hoje | `[PROJ.]` pós-`037` |
|---|---|---|
| `E-1` a cauda não fecha | ✅ medido | ✅ |
| `E-2` autorização e navegação discordam | ✅ com ressalva | ✅ com a **mesma** ressalva |
| `E-5` a explicação desgrudou do campo | ✅ | ✅ |
| `E-7` a validação não pergunta se é executável | ✅ | ✅ |
| `E-3` duas gramáticas para o mesmo fato | 🔴 | 🔴 |
| `E-4` fontes normativas que ninguém confronta | 🔴 | 🔴 |
| `E-6` a visão global some com o Processo vivo | 🔴 | 🔴 |

**Zerar os `P0` sem mover o estrutural é o achado mais útil desta projeção.** Os `P0` que restavam
eram sintomas de raízes **já fechadas**. O que sobra são três raízes inteiras, e **nenhuma delas tem
`P0` para forçá-la na fila** — que é exatamente como uma raiz atravessa sete features sem ser tocada.

### As notas: uma sobe, uma vira a primeira 10, e a mais óbvia não se move

| Dimensão | Agora | `[PROJ.]` pós-`037` | Por quê |
|---|---|---|---|
| **Fluxo ponta a ponta** | 6 | **9** | 8 pela cauda — já percorrida —, e +1 pela `036`. A projeção de 18/09 dizia que não ia a 9 *"porque o recurso continua sendo decidido sem a prova"*, e é isso que a `036` fecha |
| **Clareza conceitual** | 9 | **10** | a justificativa do 9 termina em *"sobra o rótulo `Peso (opcional)` que vira impeditivo"*, e a `037` é a feature que o tira. **Seria a primeira 10 do produto** |
| **Encontrabilidade** | 8 | **8** | a justificativa nomeia **dois** bloqueios — o link do corte **e** o período de inscrições editado em dois lugares. A `037` tira um; o outro é `E-4` |
| **Recuperação de erros** | 8 | **9** | sobe pela cauda. As **sete recusas fora das portas** seguem em 404 por decisão registrada, e é o que impede o 10 |
| **Visão global** | 5 | **5** | `ACH-25` intocado |

**A `037` — a mais barata da fila — move uma nota, e não é a que ela parece mover.** Ela tira o
último obstáculo da *clareza conceitual* e não tira o da *encontrabilidade*, que é onde ela age.

### O que sobra, e não é o que parece

Zerados os `P0`, a fila deixa de ser sobre a espinha do produto. Sobram três coisas, e **só uma está
no backlog como achado**:

**1. A visão global.** Continua em **5**, e passa a ser a pior nota por **quatro pontos** de margem.
Terá atravessado **seis** features sem ser tocada.

**2. As duas raízes normativas.** `E-3` — o renderizador único das telas de ato — e `E-4` — o
confronto entre fontes. Nenhuma tem `P0`, e as duas produzem **contradição silenciosa**, que é a
espécie de defeito que este produto menos consegue ver sozinho.

**3. As perguntas de governança que as features registraram e não responderam.** É a categoria que
nenhuma contagem de achados enxerga:

| Pergunta | Quem a registrou |
|---|---|
| os **dez de dez** Editais de sorteio não declaram ocorrência de fonte externa | `035` |
| a `FR-461` deve virar impeditiva? — registrada **duas** vezes | `032`, e este arquivo |
| o peso deve ser do par marco×Etapa, e não da Etapa? | `037`, `D-003` |
| as **sete recusas** fora das portas: corrigir, ou ratificar o 404 uniforme? | `033`, §8 |
| a Retificação não acrescenta Modalidade — e um Perfil de cotas sem ampla não recebe inscrição de não-cotista | `034`, no percurso |

**Cinco decisões de governança, e nenhuma delas é um defeito.** Depois da `037`, elas passam a ser o
**maior bloco de trabalho não endereçado do produto** — maior que os achados abertos que restam.

### A resposta à pergunta que governa

| | |
|---|---|
| **hoje, medido** | sim para as três famílias da amostra real; o recurso decide **sem a prova** |
| `[PROJ.]` **pós-`037`** | **sim, do começo ao fim, para as três famílias — inclusive o recurso**, com a prova para quem julga e o parecer chegando a quem foi avaliado |

**O que passa a faltar não é o certame correr. É ver o certame correndo.**

---

## 15. O que evoluir de forma global

**O produto parou de entortar.** A elaboração continua excelente, e a condução andou pela primeira
vez desde a auditoria.

**As duas primeiras prioridades desta lista foram entregues** — a `034` e a `035` —, e a §13 mede o
que elas fecharam. **As duas seguintes também saíram do papel**, e por isso esta lista foi remontada
em 19/09:

| Era | Virou |
|---|---|
| 1. ordem por lista em marco computado | ✅ `034`, mesclada |
| 2. sorteio executável | ✅ `035`, mesclada |
| 3. o resto da 13.1 e os "peça a alguém" | 📄 `037`, spec em PR aberto |
| — | 📄 `036` instrução do recurso, **implementação em curso** |

**A `036` não estava nesta lista** — ela estava em *"o que eu não faria agora"*, por ser menos urgente
que a cauda. Com a cauda fechada, a ordem se inverteu: ela passou a ser o último `P0` e foi escrita
antes das outras. **O registro fica porque a inversão foi certa e a lista estava errada**: uma
prioridade calculada contra um gargalo some junto com o gargalo.

**O que a §14 projeta muda o sentido desta lista.** Fechada a `037`, **os seis `P0` acabam** — e o
que resta não tem `P0` nenhum para forçá-lo na fila. A partir daí a prioridade deixa de ser dada
pela severidade dos achados e passa a ser **escolha de governança**, que é uma situação nova para
este backlog.

Na ordem em que eu investiria **agora**:

**1. O painel de condução do Processo vivo (`E-6`).** A **visão global continua em 5**, e passa a ser
a nota mais baixa por margem larga. O sistema já calcula todos os estados; eles só não estão
reunidos — e é exatamente quando o certame passa a correr de ponta a ponta que a falta dói mais.
**Cinco** features atravessaram este relatório sem tocá-la, e é agora o item mais antigo da fila sem
dono.

**2. As sete recusas do inventário (§8).** Como spec que **decide**, com o inventário pronto servindo
de entrada — três delas contradizem a `022` por identificador, e uma tem argumento próprio a favor do
404 uniforme.

**5. A validação cruzada entre fontes normativas (`E-4`).** Ataca uma classe inteira de contradições
silenciosas.

**6. A derivação de recortes do sorteio.** Achado registrado pela `034`, e a razão de ele não estar
mais acima é a que a decisão dela nomeia: a `021` tem relações publicadas, verificadores e **cadeias
históricas** por lista, e retirar o recorte excedente obriga a definir como os atos já emitidos nele
continuam alcançáveis.

**O que eu não faria agora:** o renderizador normativo único das telas de ato (`E-3`). Continua
legítimo e continua menos urgente que tudo acima.

### Uma decisão de governança que continua aberta

**Considerar tornar a `FR-461` impeditiva, e não aviso.**

A razão original para ser aviso era o marco que legitimamente não corta — o Edital 69/2026. Mas a
`032` **já separa** ausência de regra de regra que declara não governar Etapa alguma, e a varredura
contra os doze Editais confirmou que só o 173/2025 dispararia. Com a distinção no lugar, exigir que
todo marco declare sua regra de corte — inclusive para dizer que ela não governa nada — deixa de ter
falso positivo.

Do jeito que está, alguém ignora o aviso e republica o mesmo beco, num Edital imutável. É decisão de
governança, e fica registrada aqui como tal pela segunda vez.

---

## 16. Para a próxima spec

| Item | Valor medido em **19/09/2026**, em **todas as onze worktrees**, depois da `037` |
|---|---|
| Teto de `FR-` | **FR-555** |
| Teto de `SC-` | **SC-195** |
| Teto de `UX-` | **UX-061** — a `034`, a `035`, a `036` e a `037` não abriram `UX-` nenhum |
| Próxima faixa livre | **FR-556**, **SC-196**, **UX-062** |
| Próxima pasta livre | `specs/038-…` |

**A medição de 18/09 dizia FR-521, e ficou 34 identificadores atrasada em um dia.** Três specs
entraram no intervalo. É a razão do parágrafo abaixo, e não um detalhe de manutenção deste arquivo.

**Meça de novo na hora de escrever.** O teto acima vale para o instante desta medição, e este projeto
já produziu **duas** colisões de faixa por medir só a árvore local — a `030` contra a `029`, e a `032`
quase contra uma `031` que vivia numa worktree sem branch remota. O teste de citações **não acusa**
colisão: ele resolve contra a união das specs, não contra a unicidade delas.

### Duas lições de método que as duas features deixaram

1. **Meça, não estime.** A spec da `033` passou por três medições erradas da própria superfície,
   cada uma "corrigindo" a anterior, e todas as três vieram de **ler definições de função**. O erro
   só parou quando a medição virou varredura de AST — e a terceira versão errada tinha feito uma
   história inteira apontar para a porta errada, de modo que ela não poderia satisfazer o próprio
   teste de aceitação.
2. **Conferência por contagem não é conferência.** A `033` alterou 20 casos de teste. Um deles teria
   passado despercebido por qualquer leitura agregada: a asserção continuava existindo, o número não
   mudava, e o conjunto aceito tinha sido alargado. Só a leitura **caso a caso** pega isso.

---

## 17. Fechamento — a pergunta que governa

**O que mudou na resposta.** Uma pessoa que chega hoje ao sistema compõe o marco classificatório sem
precisar dominar o modelo interno; é avisada, **na etapa em que decide**, de que um Edital sem regra
de corte não convoca; e, se tem a permissão de publicar o resultado, **chega até a ação pela tela**,
sem precisar montar URL nem pertencer à comissão. Quando algo lhe é recusado, ela lê **o que falta e
a quem pedir**, em vez de um "não encontrado".

**O que não mudava, em 18/09.** A reserva de vagas seguia sem apuração por recorte — já com a tela
dizendo isso em voz alta — e o sorteio seguia sem execução. Eram os dois cenários da amostra real que
não fechavam, e a resposta à pergunta que governa era: **sim, para o Edital simples, do começo ao
fim, por quem tem a permissão de cada ato; ainda não, para cota e para sorteio.**

`[MEDIÇÃO 19/09]` **As duas entraram, e foram percorridas.** A `034` e a `035` estão na `main`, e os
critérios que exigiam percurso pela interface foram cumpridos percorrendo — a convocação pelos três
recortes, e o sorteio do congelamento à verificação pública. A resposta passa a ser **sim para as
três famílias da amostra real**: pontuada com cota, sorteio com cota e curso FIC.

**Com duas ressalvas que a §13 desenvolve, e uma delas cresceu.** O recurso continua sendo decidido
sem a prova — a `036` está **em implementação** para fechá-lo, e é o último `P0`. E o sorteio roda
**no modelo do sistema**, que não é o que os Editais do Cefor declaram: a varredura subiu de quatro
para **dez** Editais, e são **dez de dez** que não declaram ocorrência de fonte externa, todos
publicando a semente depois, com a mesma cláusula palavra por palavra. Não é omissão de alguns — **é
a prática inteira**, e a pergunta de governança segue registrada e sem resposta.

**A pergunta seguinte já não é sobre a cauda.** É se quem conduz um Processo vivo consegue ver onde
ele está — a visão global continua em **5**, e é a última nota que a auditoria deu e que **cinco**
features atravessaram sem tocar.

`[PROJEÇÃO]` **E depois da `036` e da `037` ela fica sozinha.** Com os seis `P0` fechados, a visão
global passa a ser a pior nota por **quatro pontos** de margem, e o maior bloco de trabalho não
endereçado do produto deixa de ser defeito: passam a ser **cinco perguntas de governança** que as
features registraram e não responderam. A §14 as lista. **Nenhuma delas se resolve escrevendo
código.**

Essa é a próxima linha de base.
