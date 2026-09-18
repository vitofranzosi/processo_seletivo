# Reavaliação da reauditoria de UX — 18/09/2026

Este documento **não é uma auditoria nova**. É a medição do que andou desde a
[reauditoria exploratória de 16/09/2026](auditoria-exploratoria-ux-2026-09-16.md), feita contra o
código que está na `main`, para servir de linha de base à próxima auditoria.

A pergunta que a reauditoria governou continua sendo a mesma:

> **Uma pessoa consegue compreender, configurar, executar e acompanhar um Processo Seletivo completo
> sem precisar dominar previamente a arquitetura interna do sistema?**

---

## 1. Protocolo e baseline

| Item | Valor |
|---|---|
| Linha de base | `5f37eec` — o commit que a reauditoria de 16/09 auditou |
| Estado medido | `9539376` (`main`), com `029` e `030` mergeadas |
| Código que entrou desde a linha de base | **PR #123 (`029`)** e **PR #124 (`030`)**. Mais nada |
| Artefatos que entraram sem código | **PR #125/#127 (`031`)** e **PR #126 (`032`)** — spec, plan e tasks |
| Verificação executada | `make lint check test-pg` → **6880 passando, 12 pulados**; `ruff check` e `ruff format --check` limpos; `makemigrations --check` sem mudanças |
| Medição pela interface | `runserver` na porta 8032, banco exclusivo `reauditoria_0918`, preparado com `make preparar` (31 de 31 tabelas append-only protegidas) |
| Navegador | Browser pane do Claude Desktop |

### Taxonomia de evidência

| Marca | Significado |
|---|---|
| `[UI]` | medido na interface rodando, nesta sessão |
| `[CÓDIGO]` | lido na fonte, nesta sessão |
| `[PROJEÇÃO]` | efeito esperado da `032`, que ainda não existe como código |
| `[NÃO REAUDITADO]` | superfície que a auditoria de 16/09 nunca viu |

### Limitações desta reavaliação

1. **Não houve percurso ponta a ponta.** Os seis cenários da reauditoria não foram reencenados. O
   que se mediu foi o **delta**: o que cada achado afirma, contra o código e as telas de hoje.
2. **A `032` é projeção.** Ela está na `main` como spec, plan e tasks — não como comportamento.
   Toda linha marcada `[PROJEÇÃO]` é leitura de requisito, não observação.
3. **A `029` acrescentou superfície que ninguém auditou.** O Requerimento de Matrícula é jornada
   nova do candidato, e nenhuma nota abaixo a cobre. Onde isso importa, está marcado.

---

## 2. Resumo executivo

**A `030` fez muito bem exatamente aquilo a que se propôs, e a pilha de prioridades da auditoria
continua de pé.**

Das 39 linhas do backlog priorizado, **5 fecharam e 2 ficaram parciais**. Dos **6 achados P0**,
nenhum. Dos **9 P1**, um. As três falhas **S4** — publicar Edital sem marco, publicar sorteio sem o
método no documento, publicar reserva de vagas sem via de apuração — estão exatamente onde estavam,
e foram reconferidas no código.

Três frases resumem o estado:

- **A composição passou de cara a barata, e isso é verificável em número.** O cartão do marco pedia
  7 respostas na chegada e não tinha padrão nenhum; hoje apresenta 6 controles, **4 já preenchidos**,
  e restam **2 perguntas**: como a ordem é produzida e quais Etapas entram.
- **Os conceitos deixaram de chegar sem apresentação.** "Consolidar", "marco", "recorte", "geração" e
  "faixa" têm definição no ponto de uso, e a assimetria que ninguém explicava — a Etapa pertence ao
  Edital, o marco pertence ao Perfil — está escrita na tela onde a decisão acontece.
- **A cauda do certame não se mexeu.** Convocação e suplência continuam inalcançáveis, a reserva
  continua sem apuração, o sorteio continua sem execução, e quem pode publicar resultado continua sem
  caminho até a ação.

O diagnóstico central da reauditoria — *o sistema elabora e publica bem, e cede na condução* —
**ficou mais verdadeiro, não menos**. A elaboração melhorou; a condução não. O desequilíbrio aumentou.

---

## 3. Notas (0–10)

| Dimensão | 16/09 | Hoje | Pós-`032` | Justificativa do movimento |
|---|---|---|---|---|
| Clareza conceitual | 7 | **9** | 9 | `[UI]` Os cinco conceitos ganharam definição no primeiro uso de cada tela; a assimetria Etapa×marco está escrita na etapa de Classificação. Sobra o rótulo `Peso (opcional)` que vira impeditivo |
| Encontrabilidade | 7 | 7 | 7 | `[CÓDIGO]` `detalhe.html` não mudou uma linha desde a linha de base. As três falhas nomeadas seguem inteiras |
| Previsibilidade | 5 | **6** | **9** | Hoje: a pergunta de entrada declara o que ela governa, e três guardas novas de publicação entraram. `[PROJEÇÃO]` Pós-`032`: as três publicações inexecutáveis passam a ser recusadas ou avisadas |
| **Fluxo ponta a ponta** | **4** | **4** | **6** | Hoje: nada. `[PROJEÇÃO]` Pós-`032`: o cenário 1 desbloqueia — ver §6 |
| Generalização entre famílias | 7 | 7 | 7 | O modelo não mudou. O **custo de autoria** caiu muito: num Edital de 7 polos o método do sorteio passou de 7 declarações (98 campos) a 1 (9 campos) |
| Organização do trabalho | 7 | 7 | 7 | `ACH-60` intocado: alocação por Etapa, distribuição sem filtro por polo ou modalidade |
| Experiência do candidato | 8\* | 8\* | 8\* | \*`[NÃO REAUDITADO]` A `029` acrescentou o Requerimento de Matrícula. A nota é a mesma e está **menos evidenciada** do que estava |
| Avaliação | 9 | 9 | 9 | Intocado, e continua sendo o melhor artefato do produto |
| Resultado e publicação | 8 | 8 | **9** | `[PROJEÇÃO]` O documento passa a publicar o método do sorteio, que é o que falta para a verificação pública ter base normativa |
| Recuperação de erros | 7 | 7 | **8** | `[PROJEÇÃO]` O erro passa a aparecer **antes** da publicação, que é recuperação antes do dano — e publicação é ato imutável |
| Visão global | 5 | 5 | 5 | `ACH-25` e os oito contadores concorrentes, intocados |

**Não se tira média.** 9 na avaliação e 4 no fluxo ponta a ponta convivem, e continua sendo essa a
forma do produto.

**Duas dimensões moveram com a `030`. Duas outras movem com a `032`. Sete das onze não são tocadas
por nenhuma das duas.**

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

## 5. Os achados que continuam abertos

Reconferidos no código nesta sessão, um a um.

### Os três `S4`

| Achado | Onde se conferiu | Estado |
|---|---|---|
| `ACH-49` — publica Edital sem marco algum | `editais/domain/validation.py` não tem achado da família "Perfil sem marco" | 🔴 aberto |
| `ACH-50` — o documento omite a regra do sorteio | `publicacoes/infrastructure/pdf.py` imprime Combinação, Normalização, Arredondamento, Recurso, Corte e desempates. Nunca `orderProduction`, nunca `drawMethod` | 🔴 aberto, com a metade "afirma método falso" mitigada: um marco de sorteio pode não ter Etapa, e aí a linha de Combinação não sai |
| `ACH-47` — reserva publicada sem via de apuração | `classificacao/application/emissao.py` mantém `lista_id=None` e o comentário *"um ato computado é sempre o de ampla concorrência"* | 🔴 aberto |

### Os demais P0 e P1

| Achado | Estado | Conferência |
|---|---|---|
| `ACH-46` — convocação inalcançável sem corte | 🔴 | `detalhe.html` inalterado; o link do corte continua sob `{% if marco.cutRule %}` |
| `ACH-40` — publicador sem caminho até publicar resultado | 🔴 | nenhuma mudança de navegação em `interface/views.py` |
| `ACH-43` / `ACH-42` — o julgador sem a prova, o parecer sem chegar | 🔴 | intocados |
| `ACH-41` — duas datas-limite contraditórias | 🔴 | intocado |
| `ACH-51` — fonte da semente em texto livre | 🟡 | continua texto livre, mas agora em **um** lugar em vez de sete |
| `ACH-55` — método do sorteio em prosa, não computável | 🔴 | intocado |
| `ACH-60` — a organização do trabalho não conhece o Perfil | 🔴 | intocado |
| `ACH-16` — `Peso (opcional)` que impede | 🔴 | `_etapa.html` inalterado |
| `ACH-35` — negativa por vínculo vira 404 mudo | 🔴 | intocado |
| `ACH-39` / `ACH-31` / `ACH-45` — UUID e vocabulário de máquina nas telas de ato | 🔴 | intocados |

**Contagem:** 5 fechados, 2 parciais, 32 abertos, de 39 linhas do backlog. **Dos 6 P0, zero.**

---

## 6. O que a `032` resolve — e o que ela não resolve

`[PROJEÇÃO]` — leitura dos requisitos `FR-457` a `FR-472`, não observação.

### Resolve

| Achado | Como |
|---|---|
| `ACH-49` | erro impeditivo para Perfil sem marco classificatório |
| `ACH-50` | o documento passa a declarar como a ordem nasce e a imprimir os sete campos do método; e marco que sorteia sem método publicável não publica |
| `ACH-46` | aviso que nomeia a cadeia inteira — sem corte não há geração, sem geração não há faixa, sem faixa não há convocação —, dito **no cartão, no momento da decisão**, e não só na Revisão |

### Não resolve, e diz isso por escrito

`ACH-47` sai **nomeado, não resolvido**. O aviso declara que aquele quadro não terá apuração por
recorte, e as duas ações que sempre falham somem das telas; a emissão de ordem por lista fica para
feature própria. A decisão de tratar por aviso e não por impedimento foi tomada com a amostra real na
mão: **57/2026, 28/2026 e 173/2025** declaram reserva em marco computado, e para eles a publicação é
a única parte da jornada que hoje funciona, porque a apuração por recorte já acontece fora do sistema.
Impedir retiraria o que funciona sem consertar o que não funciona.

### O efeito de segunda ordem, que é o mais valioso

**A `032` desbloqueia o cenário 1 da auditoria — e não por criar rota nenhuma.**

A cadeia do `ACH-46` depende de um elo opcional. O marco do cenário 1 declarou "este marco não
corta", e por isso a convocação ficou inalcançável. A `032` não toca em `detalhe.html`: o link do
corte continua condicionado a `cutRule`. O que ela faz é **fazer a pessoa declarar a regra**, avisando
onde a decisão é tomada. Um Edital simples composto depois da `032` chega à convocação.

É por isso que o fluxo ponta a ponta vai de 4 para 6, e não fica em 4.

### Uma recomendação que nasce dessa leitura

**Considerar tornar a `FR-461` impeditiva, e não aviso.**

A razão original para ser aviso era o marco que legitimamente não corta — o Edital 69/2026, que
sorteia, publica e convoca sem análise documental no meio. Mas a própria `032` já separa **ausência
de regra** de **regra que declara não governar Etapa alguma** (`FR-224` da `014`). Com essa distinção
no lugar, exigir que todo marco declare sua regra de corte — inclusive para dizer que ela não governa
nada — deixa de ter falso positivo.

Do jeito que está, alguém ignora o aviso e republica o mesmo beco, num Edital imutável. É decisão de
governança, e fica registrada aqui como tal.

---

## 7. Os problemas estruturais

| | Estado | Observação |
|---|---|---|
| **E-5** · a explicação desgrudou do campo | ✅ **resolvido** | `030` — `[UI]` a ajuda só existe com item a que se referir, e cada item leva ao campo que explica |
| **E-7** · a validação não pergunta se o Edital é executável | 🎯 **alvo da `032`** | Fecha 3 dos 4 achados que o compõem |
| **E-1** · a cauda do processo não fecha | 🟡 parcial pós-`032` | O cenário simples fecha; reserva e sorteio continuam abertos |
| **E-2** · autorização e navegação discordam | 🔴 intocado | `ACH-40`, `ACH-35` |
| **E-3** · duas gramáticas para o mesmo fato | 🔴 intocado | `ACH-39`, `ACH-31`, `ACH-45` |
| **E-4** · fontes normativas que ninguém confronta | 🔴 intocado | `ACH-41`, `ACH-13`, `ACH-18` |
| **E-6** · a visão global some com o Processo vivo | 🔴 intocado | `ACH-25` |

**Dois de sete resolvidos, um parcial, quatro intactos.**

---

## 8. O que evoluir de forma global

O produto está ficando **torto**. A elaboração passou de muito boa a excelente; a condução do
certame não se mexeu. Cada feature nova de composição aumenta a distância entre as duas metades.

Na ordem em que eu investiria:

**1. Navegação derivada da capacidade (`E-2`).** A melhor relação esforço/retorno que sobrou. Quem
tem `resultado:publicar` não chega à ação; a negativa por vínculo cai num 404 mudo. Dois achados
P0/P1 com causa única, e a correção não toca domínio nenhum.

**2. Emissão de ordem por lista em marco computado (`ACH-47`).** O `S4` que a `032` deliberadamente
deixa nomeado. Três Editais da amostra real dependem dele, e a decisão de governança já está tomada —
falta a feature.

**3. Sorteio executável (`ACH-55` + `ACH-51`).** Fecha os cenários 3 e 5 de uma vez. A causa é dupla:
a derivação da ocorrência não é computável, e a fonte da semente é texto livre onde o valor é criado.
A `032` leva o método ao documento; sem estes dois, o documento descreve um sorteio que não roda.

**4. Validação cruzada entre fontes normativas (`E-4`).** Ataca uma classe inteira de contradições
silenciosas, e não um caso. É a irmã natural da `032`: mesma tela, mesma família de achados.

**5. Painel de condução do Processo vivo (`E-6`).** O sistema já calcula todos os estados; eles só
não estão reunidos. É o que devolve visão global exatamente quando o Processo passa a existir.

**O que eu não faria agora:** o renderizador normativo único das telas de ato (`E-3`) e a instrução do
recurso (`ACH-43`/`ACH-42`). Os dois são legítimos e os dois são menos urgentes que a cauda que não
fecha.

---

## 9. Para a próxima spec

| Item | Valor medido em 18/09/2026 |
|---|---|
| Teto de `FR-` em todas as worktrees | **FR-472** |
| Teto de `SC-` em todas as worktrees | **SC-163** |
| Teto de `UX-` | **UX-061** |
| Próxima faixa livre | **FR-473**, **SC-164** |
| Próxima pasta livre | `specs/033-…` |

**Meça de novo na hora de escrever.** O teto acima vale para o instante desta medição, e este projeto
já produziu **duas** colisões de faixa por medir só a árvore local — a `030` contra a `029`, e a `032`
quase contra uma `031` que vivia numa worktree sem branch remota. O teste de citações **não acusa**
colisão: ele resolve contra a união das specs, não contra a unicidade delas.

### Sobre escrever a spec seguinte em paralelo à implementação da `032`

É prática corrente neste projeto, e o risco não é o paralelismo — é a escolha do tema.

| Candidata | Paralelo com a `032`? | Por quê |
|---|---|---|
| Navegação por capacidade (`E-2`) | ✅ melhor escolha | O plano da `032` declara que ela **não** toca `interface/views.py`; a navegação vive lá e em `detalhe.html` |
| Painel de condução (`E-6`) | ✅ | Superfície nova, quase sem interseção |
| Sorteio executável (`ACH-55`/`51`) | 🟡 | Toca `_marco.html`, que a `032` edita |
| Validação cruzada (`E-4`) | ⛔ | Mora em `editais/domain/validation.py`, o arquivo que as três histórias da `032` editam |
| Emissão por lista (`ACH-47`) | ⛔ | Não é conflito de arquivo, é de premissa: o aviso da `FR-470` existe **porque** a emissão por lista não existe |

---

## 10. Fechamento — a pergunta que governa

**O que mudou na resposta.** Uma pessoa que chega hoje ao sistema compõe o marco classificatório sem
precisar dominar o modelo interno: a tela pergunta o que o objeto é antes de pedir como ele funciona,
e explica a assimetria que antes era um fato a decorar. Esse trecho — que era o `🔴` da jornada —
passou a `🟡`.

**O que não mudou.** A pessoa continua sem conseguir **executar e acompanhar** um Processo Seletivo
completo. Convocação e suplência seguem inalcançáveis, a reserva de vagas segue sem apuração, o
sorteio segue sem execução, e quem tem a permissão de publicar o resultado segue sem caminho até a
ação.

**A `032` fecha três dos quatro achados que compõem o `E-7`, e desbloqueia o cenário mais comum da
amostra.** Depois dela, a resposta à pergunta que governa deixa de ser *"quase, e trava na cauda"* e
passa a ser *"sim, para o Edital simples; ainda não, para cota e para sorteio"*.

Essa é a próxima linha de base.
