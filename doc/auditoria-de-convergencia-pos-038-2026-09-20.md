# Auditoria de convergência e maturidade operacional pós-`038`

**Data:** 2026-09-20
**Contra:** `main` em `b2e8aa8` — worktree sincronizada, `0 0` de divergência com `origin/main`
**Banco:** `ps_conv_038`, isolado; suíte em `ps_conv_038_suite`
**Método:** percurso pela interface primeiro; código e spec só para distinguir defeito de regra

> **A pergunta central.** Depois da `029`–`038`, alguém assume um Processo em qualquer ponto do
> ciclo, entende o que aconteceu, identifica o que precisa acontecer agora e o conduz até o fim sem
> conhecer a arquitetura interna?
>
> **A pergunta da `038`.** O Painel deixa ver o Processo vivo, ou reuniu parte dos sinais de fluxos
> que continuam fragmentados?

---

## 1. Veredito de prontidão operacional

**Pronto apenas para piloto controlado.**

O produto conduz um certame inteiro. Percorri publicação, inscrição, alocação, distribuição,
consolidação, classificação, sorteio, divulgação, recurso (interposição e admissibilidade),
ocupação, convocação e exportação para matrícula — **sem sair da interface e sem ler spec para saber
onde clicar**. Isso não era verdade em 02/09 e passou a ser.

O que impede a operação institucional não é o certame não correr. É que **a superfície que a `038`
criou para vigiar o certame ainda não é confiável como instrumento de condução**: ela afirma
ausência que não mediu, oferece caminho que não abre, e aponta 60% das vezes para um ato que não
resolve o que ela reporta.

### Condicionantes

| # | Condicionante | Achado |
|---|---|---|
| C1 | A frase de ausência da região **Atenção** precisa parar de afirmar fato global a partir de leitura parcial | `N-01` (S3) |
| C2 | Recurso **aguardando admissibilidade** precisa produzir sinal — hoje metade do ciclo do recurso é invisível | `N-02` (S3) |
| C3 | O link *"Abrir a Supervisão"* precisa da mesma guarda que o botão vizinho já tem | `N-03` (S2, regressão) |
| C4 | Os 9 sinais sem caminho precisam dizer **a quem pedir**, como o Edital já diz | `N-04` (S2) |
| C5 | `UX-001` e `UX-002` não devem encaminhar à Retificação enquanto ela não alcançar os campos que os causam | `N-05` (S2) |
| C6 | `schedule.status` está declarado `derivado()` e **nada o deriva** | `N-06` (S2) |
| C7 | Autenticação institucional real (o seletor de identidade é demonstração declarada) | herdado |

Nenhuma dessas é bloqueio de integridade, direito do candidato ou auditabilidade. **Não encontrei
S4.** Encontrei, medido, o oposto: as duas camadas de imutabilidade estão de pé (`33 de 33` tabelas
append-only sem `UPDATE`/`DELETE` para o runtime) e nada publicado foi reescrito em nenhum percurso.

---

## 2. Ambiente e protocolo

| | |
|---|---|
| Branch | `claude/auditoria-convergencia-038-b50711`, idêntica a `origin/main` |
| Commit | `b2e8aa8` (merge da `#150`) |
| `037` mesclada | ✅ `#144` |
| `038` mesclada | ✅ `#149`, mais o fix `32cd6d9` dos casos-limite |
| Feature posterior | **nenhuma** — `specs/` termina em `038-painel-de-conducao` |
| Migrations | `migrate --check` limpo; 20 apps aplicados |
| Append-only | `Papéis provisionados. 33 de 33 tabelas append-only estão sem UPDATE nem DELETE para o runtime.` |
| `make lint` | ✅ `ruff check` + `ruff format --check` |
| `make check` | ✅ sem `makemigrations` pendente |
| **Suíte PostgreSQL** | **7478 passaram · 1 falhou · 11 puladas · 744 s** |
| Seletores | `INTERFACE_SELETOR_IDENTIDADE` e `PORTAL_IDENTIDADE_DEMO`, só os necessários |

### A falha da suíte não é regressão

`tests/integration/identidade/test_adicionar_credencial.py::test_adicionar_pede_codigo_e_nao_pede_cpf`
falhou porque o token CSRF sorteado continha a sequência `CPF`:

```
assert 'CPF' not in '<!DOCTYPE h...>'
'CPF' is contained here:  B8z98O9yIGCPF">
```

A asserção é substring sobre o corpo inteiro. Reexecutada isolada: **9 passaram**. É **teste
instável**, não defeito de produto — mas é defeito de teste, e da mesma família que
`varredura-le-o-comentario`.

### Duas contagens do `CLAUDE.md` estão vencidas

| `CLAUDE.md` diz | Medido hoje |
|---|---|
| tabelas append-only: "eram 18, são **31**" | **33** (a `037` já corrigira para 33 em `b5aecba`) |
| suíte contra PostgreSQL: "**5402** passando e **2** pulados" | **7478** e **11** |

Os 11 pulados são benignos: 1 é o E2E deliberado contra a Caixa (`SORTEIO_E2E_FONTE_REAL`), 10 são
casos parametrizados de `test_vocabulario_da_composicao.py` que se pulam quando o par
*termo × template* não existe.

### Custo de consulta, medido

| Página | 3 Editais publicados | 0 publicados |
|---|---|---|
| Processo (gestor) | **64** consultas | 11 |
| Supervisão (gestor) | **61** consultas | 8 |

**Linear, ~17 consultas por Edital publicado.** Proporcional — não quadrático. Mas um Processo de 20
Editais projeta ~350 consultas por leitura de painel, e isso merece medição antes de um Processo
grande, não depois.

### O que esta auditoria NÃO fez

- **Não validou o sistema de destino do Registro Acadêmico.** Ele não está disponível aqui. A
  importação, a validação no destino e a reexportação ficam **`[NÃO REAUDITADO]`**.
- **Não percorreu o Cenário A desde o zero absoluto** (criar Processo → compor → publicar à mão). Usei
  o `seed_demo`, que percorre os mesmos *commands* da API com atores distintos, e operei da
  publicação em diante. A composição de origem fica `[HERDADO DE AUDITORIA ANTERIOR]`.
- **Não testou múltiplos polos com uma família real da amostra** (Cenário D). Os Editais de amostra
  estão em `~/Downloads`, fora do repositório. O que medi do Cenário D é estrutural, não de percurso.
- **Não reexecutou** os 17 `AX` de 15/09 — a varredura de 19/09 o fez, e nada em `editais/models`
  mudou desde então.
- Uma fonte citada no briefing — `doc/relatorio-longitudinal-produto-001-a-037-2026-09-19.md` — **não
  existe** no repositório. O documento de 19/09 é `varredura-dos-dezessete-2026-09-19.md`, e foi esse
  que usei.

---

## 3. Evolução longitudinal

| Marco | O que mudou de fato |
|---|---|
| **02/09** | E2E funcional; produto ainda sem auditoria de UX |
| **13/09** | primeira auditoria de UX; encontrabilidade e fluxo baixos |
| **16/09** | 60+ achados nomeados; sete raízes estruturais (`E-1`…`E-7`); visão global **5** |
| **18–19/09** | `030`–`037` entram; 5 das 7 raízes fecham; os seis `P0` zeram; cinco decisões de governança são tomadas e **criam quatro specs** |
| **pós-`038`** | o painel existe, concorda com a Supervisão, e **os quatro sinais novos funcionam** — mas a região que os abriga é pouco acionável |

**Mudança de cobertura que afeta as notas.** As auditorias anteriores mediram o painel como
*ausência*. Esta é a primeira que o mede como *superfície em uso* — produzindo cada um dos quatro
estados, abrindo cada destino, resolvendo um deles e conferindo o desaparecimento. Notas que antes
diziam "não existe" agora dizem "existe e faz X"; a queda de expectativa em relação à projeção vem
disso, não de regressão.

---

## 4. Matriz de fechamento dos achados

| Achado | Estado | Evidência de hoje |
|---|---|---|
| **`ACH-25` / `E-6` — visão global** | **PARCIAL** | O painel existe e lê a mesma derivação da Supervisão. Mas nenhum papel vê o Processo inteiro, 60% dos sinais do gestor não têm caminho, e recurso novo, sorteio e matrícula ficam fora. **Não fechou** — ver §6 |
| Navegação por capacidade (`033`) | **FECHADO** | `[MEDIDO]` A lista de Processos mostra "O QUE POSSO FAZER" por papel; o julgador vê *Recursos recebidos (1)* e o gestor vê *Inscrições recebidas (7)* no mesmo lugar |
| **Sete recusas fora das portas** | **ABERTO / GOVERNANÇA** | `[MEDIDO]` `criar_edital`, `reaproveitar` e `supervisao` **continuam 404**. A `D-G2` de 19/09 decidiu **403** para as três. A spec não foi escrita — ela entra depois da `038` |
| Condução do corte | **FECHADO** | `[HERDADO]` + `[MEDIDO]` o marco declara corte ou declara que não governa Etapa; o aviso do `66/2026` diz exatamente isso |
| Período em curso tratado como vencido (`ACH-08`) | **FECHADO na validação** / **DESLOCADO para o painel** | `calendario.py::vencido` corrigiu a régua na `037` (`FR-545/546`). Mas a `038` reintroduziu custo adjacente: `UX-002` marca o período **em curso** como condição de Atenção, permanentemente — ver `N-06` |
| Peso aparentemente opcional | **FECHADO** | `[HERDADO]` a `037` o tirou; `D-G4` encerrou a pergunta sem criar trabalho |
| **`E-4` — fontes normativas sem confronto** | **ABERTO** | `[MEDIDO]` o `66/2026` exibe *"A linha da modalidade 'PPP' declara 10 vaga(s), e o percentual publicado (20%) sobre 40 daria 8"* — confronto **dentro** da linha. `AX-7` (duas linhas citando a mesma lei com percentuais diferentes) continua sem conferência |
| **`E-3` — duas gramáticas da Retificação** | **ABERTO** | `[NÃO REAUDITADO a fundo]` nada tocou o renderizador desde 16/09 |
| **`ACH-60` — trabalho sem Perfil/polo** | **ABERTO** | `[MEDIDO]` `distribuicao.html` tem **zero** ocorrências de Perfil, polo ou modalidade como filtro; a alocação é matriz `Etapa × avaliador`, 9 colunas para 3 Editais |
| **Recurso sem prova** | **ABERTO** | `[MEDIDO]` a tela `/selecoes/.../recorrer` tem um `select` de objeto e um `textarea`. **Nenhum campo de anexo** |
| Parecer do candidato | **FECHADO** | `[MEDIDO]` o acompanhamento mostra *"Habilitada · pontuação 8 — a Etapa não tem caráter eliminatório"* por Etapa |
| Ordem por recorte | **FECHADO** | `[MEDIDO]` a ocupação lista *Ampla concorrência (linha geral)* e *PPP* separadamente, cada uma com publicadas/ocupadas/faltam |
| **Sorteio executável** | **FECHADO** | `[MEDIDO]` ver §5, Cenário C — os nove passos são distinguíveis na tela |
| Ocupação, convocação e suplência | **FECHADO** | `[MEDIDO]` apuração, convocação e requerimento existem e concordam |
| **Retificação sem Modalidade** | **ABERTO** | `[MEDIDO]` `SECOES_QUE_ACRESCENTAM = {perfis, cronograma, anexos}`. A tela diz, com todas as letras: *"Modalidades de Concorrência ainda não são definidas por aqui."* A `D-G5` decidiu que passa a acrescentar; a spec não existe |
| Matrícula e exportação | **FECHADO no que sai** / **`[NÃO VALIDADO]` no destino** | `[MEDIDO]` ver §13 |
| Prática institucional do sorteio | **GOVERNANÇA** | `D-G3` decidiu declarar fonte pública externa; a spec não foi escrita. O produto já suporta o modelo forte |
| **`ACH-27` — contadores concorrentes** | **PARCIAL / DESLOCADO** | `[MEDIDO]` Processo e Supervisão **concordam** — ganho real. Mas a tela de distribuição tem 9 mosaicos e **um deles contradiz a própria lista** — ver `N-07` |
| Condução do Processo pela `038` | **PARCIAL** | ver §6 e §9 |
| `AX-1` — sentido do desempate não retificável | **ABERTO** | `[CONFIRMADO POR CÓDIGO]` `CAMPOS_CRITERIO = [("order", …)]`; `type` fora |
| `AX-2`…`AX-17` | **ABERTOS** (11 medidos, 3 prováveis, 3 de percurso) | `[HERDADO]` varredura de 19/09; nada em `editais/models` mudou desde |

---

## 5. Jornadas atuais

| Cenário | Estado | O que decide a marca |
|---|---|---|
| **A — seleção simples completa** | 🟡 | Percorrível de ponta a ponta. Exige sair do fluxo **três vezes**: da página do Processo para o Edital (os avisos de validação não sobem ao painel), do Edital para a lista de marcos, e do sinal de avaliação para a alocação — porque a distribuição sozinha não resolve quando não há ninguém alocado |
| **B — modalidades e reservas** | 🟡 | Ampla, PPP, quadro por recorte, ocupação por lista: tudo coerente. **Duas armadilhas**: o Edital admite uma Modalidade *"AC — Ampla concorrência"* **e** uma *"linha geral do quadro"* como duas grafias da mesma coisa; e **acrescentar Modalidade a Edital publicado é impossível**, com a tela declarando isso honestamente e sem oferecer alternativa |
| **C — sorteio** | 🟢 | O melhor artefato do produto. Os nove passos são nomeados e distinguíveis numa tela só — ver abaixo |
| **D — polos / turmas** | 🔴 | `[INFERÊNCIA ESTRUTURAL, não de percurso]` Polo é atributo do Perfil, não eixo próprio (`AX-6`). A alocação é `Etapa × avaliador` sem recorte; a distribuição não filtra por Perfil nem polo (`ACH-60`). Num Edital de 7 polos a matriz tem 21 colunas e nenhuma comissão local encontra só o que é dela |
| **E — Processo vivo pós-`038`** | 🟡 | Ver §6 |
| **F — Retificação e recuperação** | 🟡 | A Retificação é excelente no que alcança e **honesta no que não alcança** — cada campo bloqueado explica por quê. Mas o conjunto do que não alcança inclui exatamente o que dois dos sinais do painel reportam |

### Cenário C, detalhado — porque é o padrão a preservar

Uma tela só, e os nove passos legíveis sem manual:

| Passo | Como aparece |
|---|---|
| método | `IFES-SORTEIO-SHA256-v1`, com resumo `b85fb26a…` |
| fonte | *Fonte da semente — Fonte de demonstração* |
| ocorrência | `5966`, com **material bruto observado** `12345 67890 11223 44556 77889` |
| derivação | *"Concurso 5966: a extração de sábado imediatamente anterior à data publicada do sorteio."* |
| normalização | *"Os cinco números sorteados, na ordem dos prêmios, separados por espaço."* |
| contingência | *"Não havendo extração na data prevista, vale a extração seguinte da mesma fonte."* |
| congelamento | *"Relação congelada em 20/09 por paulo.presidente, com 7 participantes. Resumo `8b40ffde…`"* |
| execução | *"Sorteio realizado … Semente … manifesto `d2649209…`"* |
| verificação | *"Ver no canal público"* / *"Verificar no canal público"* |

E a distinção que mais custa a explicar em papel está escrita na tela: *"o universo é comprometido
**antes** de a semente existir"*.

**Uma divergência normativa, não textual.** O recorte que o sorteio usou é *"Todos os inscritos do
recorte de vaga (sem lista de concorrência)"*, enquanto as Modalidades *AC* e *PPP* aparecem logo
abaixo com **"Nenhuma inscrição submetida declarou esta lista de concorrência"**. O mesmo Edital
carrega, portanto, três nomes para duas coisas: a Modalidade *AC* declarada e sem vagas, a linha
geral do quadro com 30 vagas, e o recorte nulo que o sorteio efetivamente ordenou. Nada confronta os
três. **É `E-4` em estado puro, e não é problema de texto.**

---

## 6. O Processo vivo depois da `038`

### O que passou a ser visível

Abri a página do Processo **antes** de visitar qualquer Edital. Respondi, sem sair dela:

| Pergunta | Resposta obtida | De onde |
|---|---|---|
| quantas inscrições foram recebidas | **12** no Processo; 0 / 7 / 5 por Edital | Pulso |
| quais são os próximos marcos | três por Edital, com data e declaração | Próximos marcos |
| onde há avaliação parada | 5 Etapas, com medida `7 de 7` e `2 de 5` | Atenção |
| onde existe ordem sem ocupação | *Sorteio público, 66/2026* | Atenção |
| onde existe ato emitido sem divulgação | *ato de ordenação vigente do marco Sorteio público, 66/2026* | Atenção — **só para quem publica** |
| onde existe recurso que já pode ser julgado | *Há recurso aguardando julgamento no Edital 91/2026 com membro da comissão desimpedido* | Atenção — **só para quem julga** |
| qual Edital precisa de atenção | ❌ **não respondida** — a região é lista plana de 15 linhas, sem agregação por Edital |
| o que o painel não mostra | ❌ **não declarado** |

### Processo e Supervisão concordam — confirmado, e é o maior acerto da feature

`[CONFIRMADO POR CÓDIGO]` Existe **uma** derivação: `interface/supervisao.py`. As duas views a
importam do mesmo módulo e chamam as mesmas funções:

```
views.py:3585   "pulso": supervisao_do_processo.pulso(processo),        # página do Processo
views.py:3657   "pulso": supervisao_do_processo.pulso(processo),        # Supervisão
```

`[MEDIDO AGORA]` Li as duas superfícies em sequência, com o mesmo ator:

- números idênticos — `12 / 0 / 12`, e `0 / 7 / 5` por Edital;
- **frases idênticas**, palavra por palavra, nas 15 linhas de Atenção;
- **ordenação idêntica** — espécie, depois Edital, depois alvo;
- nenhuma consulta duplicada: a página do Processo lê `alcance` uma vez e o passa a `sinais`.

**Uma divergência de forma, não de valor.** O mesmo prazo do `41/2026` sai como *"Faltam 19 dias"*
no portal, *"Encerra em 2 semanas, 5 dias"* na Supervisão e apenas como data na página do Processo.
Três renderizações do mesmo número. **Divergência textual, S0.**

### Quais estados são acionáveis — a medição que decide a nota

`[MEDIDO AGORA]`, com `carla.gestora` (papel Gestor, o perfil que conduz):

| | |
|---|---|
| sinais exibidos | **15** |
| **com caminho** | **6** — 5 × *Abrir a distribuição da Etapa*, 1 × *Abrir a ocupação do marco* |
| **sem caminho nenhum** | **9** — 6 × `UX-001`, 3 × `UX-002` |

Os 9 aparecem como frases soltas: *"A Etapa Análise de títulos, do Edital 41/2026, está sem marco no
cronograma."* Sem link, **e sem dizer a quem pedir**.

Acrescentando o papel Elaborador ao mesmo ator, os 15 ganham caminho. E aí começa o segundo
problema — ver `N-05`.

### O que ainda permanece fora

| Fora do painel | Impacto **demonstrado** |
|---|---|
| **Recurso aguardando admissibilidade** | ❗ **Não é ausência planejada — é buraco.** Interpus `REC-2026-VYN6GNTG` às 00h37 e o painel **não mudou em nenhuma superfície, para nenhum papel**. Só depois de eu admiti-lo é que `UX-064` disparou. A admissibilidade é o passo com prazo, e é o único que ninguém vê |
| **Sorteio** | Ausência declarada. **Impacto real, mas menor**: o `66/2026` estava congelado, com ocorrência observada e sorteado, e o painel disso só disse *"7 recebidas"*. Um sorteio congelado e não executado, ou com a data publicada vencida e a ocorrência não observada, não produz sinal algum |
| **Matrícula** | Ausência declarada. **Impacto baixo hoje**: o `91/2026` tem 1 convocado e 1 requerimento, e a exportação é encontrável pelo Edital. Vira risco quando houver dezenas de convocados com requerimentos parciais |
| **Avisos de validação do Edital** | ❗ O `66/2026` exibe dois avisos na sua própria página — *marco sem regra de corte*, *PPP declara 10 e o percentual daria 8* — que **nunca chegam à Atenção**. São duas superfícies de problema que não se juntam |

### `ACH-25` / `E-6` fechou?

**Não. Reduziu.**

Fechou: a mesma verdade em duas superfícies; quatro estados da cauda ganharam sinal; o Pulso alcança
quem alcança o Processo.

Não fechou: **nenhum papel vê o Processo inteiro** (o gestor vê 15 e não vê o ato por divulgar; o
publicador vê 1 e não vê as 15); **60% do que o gestor vê não é acionável por ele**; o recurso recém-
interposto é invisível; os avisos do Edital não sobem; e a região não diz o que não está mostrando.

### Nota de visão global

| | |
|---|---|
| 16/09 | 5 |
| 18/09 | 5 |
| `[PROJ. 19/09]` pós-`038` | **8** |
| **20/09, medido** | **6** |

**Não repito o 8 por deferência.** O briefing condiciona o 8 a *"compreender a condução real sem
divergência com a Supervisão e sem reconstrução manual relevante"*. A primeira metade se cumpriu — e
é um ganho genuíno. A segunda não: para saber qual Edital precisa de atenção eu tive de contar
linhas de uma lista plana; para saber se havia ato por divulgar tive de **trocar de identidade**;
para ver os avisos de composição tive de abrir cada Edital. Isso é reconstrução manual, e é
relevante.

**6, e não 5**, porque a superfície existe, as duas leituras concordam de verdade e quatro estados
que eram invisíveis passaram a ter nome, medida e destino.

---

## 6-bis. Notas atuais (0–10)

**Não se tira média.** A forma do produto continua sendo 9 na avaliação e 6 na visão global, e essa
distância é informação, não ruído.

| Dimensão | Últ. medida | **Agora** | `[PROJ.]` que havia | Movimento e confiança |
|---|---|---|---|---|
| **Clareza conceitual** | 9 (18/09) | **9** | 10 | **Não vai a 10.** `[MEDIDO]` O produto define os termos no primeiro uso, e isso se confirmou em todas as telas. Mas achei três lacunas novas: `7 de 7` sem unidade no painel, *"sem marco no cronograma"* sem consequência legível, e `cand:…` + UUIDs crus na tela do recurso. O bloqueio antigo — o rótulo *Peso (opcional)* — fica `[NÃO REAUDITADO]`. **Confiança alta** |
| **Encontrabilidade** | 8 | **8** | 8 | **Empate por compensação.** `[MEDIDO]` Três intenções chegaram a **E0** pelo painel (avaliação parada, ocupação pendente, ato por divulgar) — ganho real. Mas a intenção-título da feature, *"qual Edital precisa de atenção"*, é **E2**: lista plana de 15 linhas, sem agregação, e incompleta por papel. **Confiança alta** |
| **Previsibilidade** | 9 | **8** ⬇ | 9 | **Cai 1, e a causa é a feature nova.** `[MEDIDO]` *"Eu sei o que acontecerá depois desta escolha"* falha duas vezes na `038`: *Abrir a Supervisão* devolve 404 (`N-03`), e *Retificar o cronograma* abre uma tela sem o campo que o sinal reporta (`N-05`). **Confiança alta** |
| **Fluxo ponta a ponta** | 6 | **8** ⬆ | 9 | **Sobe 2, não 3.** `[MEDIDO]` Percorri a cauda inteira hoje. Não vai a 9 por duas razões: `N-02` — a admissibilidade do recurso é segmento invisível na condução — e porque **não executei um ato de instrução**, de modo que o fechamento da `036` fica `[NÃO REAUDITADO]` na execução. **Confiança média-alta** |
| **Generalização entre famílias** | 7 | **7** | 7 | `[INFERÊNCIA ESTRUTURAL]` O modelo não mudou; `AX-5` e `AX-6` seguem abertos. Não percorri família real de múltiplos polos. **Confiança média** |
| **Organização do trabalho** | 7\* | **7** | 7\* | **Mesma nota, agora medida e sem asterisco.** `[MEDIDO]` `distribuicao.html` tem **zero** filtros por Perfil, polo ou modalidade; a alocação é matriz `Etapa × avaliador`. `ACH-60` intocado. **Confiança alta** |
| **Experiência do candidato** | 8\* | **8** | 8\* | **Mesma nota, parcialmente medida.** `[MEDIDO]` O acompanhamento explica cada Etapa (*"a Etapa não tem caráter eliminatório"*), mostra o prazo recursal e o caminho para recorrer. Retido em 8 por: recurso **sem anexo de prova**, e a página pública do resultado não declara o prazo. O Requerimento de Matrícula segue `[NÃO REAUDITADO]` |
| **Avaliação** | 9 | **9** | 9 | `[MEDIDO]` Continua o melhor artefato operacional: prévia da distribuição, carga por avaliador, prontidão por inscrição, conclusões preservadas. Não vai a 10 por `N-07` — um dos nove mosaicos contradiz a lista abaixo dele. **Confiança alta** |
| **Resultado e publicação** | 9 | **9** | 9 | `[MEDIDO]` A prévia de publicação é exemplar: diz que nada foi gravado, o que acontece ao confirmar, que o ato não se despublica, e mostra a lista inteira. Não vai a 10 porque a página pública do resultado omite o prazo recursal. **Confiança alta** |
| **Recursos** | — (dimensão nova) | **7** | — | `[MEDIDO]` Interposição, protocolo, tempestividade, admissibilidade com motivo, e a explicação de que *"julgar não concede"* acesso à prova, com o ato a pedir nomeado. Retido em 7 por dois buracos: **sem anexo de prova** para o recorrente, e `N-02` — a fase de admissibilidade não existe na condução. **Confiança alta** |
| **Recuperação de erros** | 8 | **8** | 9 | **Não sobe.** `[MEDIDO]` A justificativa do 8 nomeava as sete recusas fora das portas; a `D-G2` decidiu 403 para três delas em 19/09 e **o código não executou a decisão** — `criar_edital`, `reaproveitar` e `supervisao` continuam 404. **Confiança alta** |
| **Visão global** | 5 | **6** ⬆ | **8** | **Sobe 1, não 3.** Ver §6. A superfície existe e as duas leituras concordam de verdade; mas a vista é parcial por papel sem se declarar parcial, 60% do que o gestor vê não é acionável por ele, e o recurso recém-interposto é invisível. **Confiança alta** |
| **Prontidão institucional** | — (dimensão nova) | **6** | — | `[MEDIDO + INFERÊNCIA]` O certame corre inteiro; as duas camadas de imutabilidade estão de pé (`33 de 33`); nada publicado foi reescrito. Retido em 6 por: autenticação real ausente, integração com o Registro Acadêmico `[NÃO VALIDADO]`, e a superfície de vigília ainda não confiável. **Confiança média-alta** |

**Três dimensões moveram; duas são novas; oito seguem onde estavam.** E o movimento não é todo para
cima: *previsibilidade* **cai**, e cai por causa da feature que acabou de entrar.

---

## 7. Coerência entre superfícies

| Fato | Superfícies | Classificação |
|---|---|---|
| inscrições recebidas | lista de Processos, painel, Supervisão, Edital — **todas 0/7/5** | ✅ coerente |
| Atenção | painel e Supervisão — **idênticas, frase a frase** | ✅ coerente |
| prazo restante do `41/2026` | *"Faltam 19 dias"* · *"Encerra em 2 semanas, 5 dias"* · só a data | **divergência textual** (S0) |
| prazo recursal | o portal do candidato diz *"Cabe recurso até 25/09 às 23h59"*; **a página pública do resultado não diz nada** | **divergência operacional** (S1) — quem lê só o resultado público não sabe que há prazo |
| problemas do Edital | *Atenção* do painel (9 espécies) × *Validação do conteúdo* do Edital (avisos da `032`) — **conjuntos disjuntos** | **divergência operacional** (S2) — `N-08` |
| cobertura de avaliação do `91/2026` | painel diz *"2 de 5 sem avaliador suficiente"*; a tela de destino diz *"1 eliminadas antes"* e lista **4** inscrições, das quais **1** sem avaliador | **divergência operacional** (S2) — `N-07` |
| ampla concorrência no `66/2026` | Modalidade *AC* declarada · linha geral do quadro (30 vagas) · recorte nulo que o sorteio usou | **divergência normativa** (S2) — `E-4` |
| estado declarado do Evento × relógio | `PLANEJADO` para sempre × posição real | **divergência de interpretação** (S2) — `N-06` |

---

## 8. Clareza conceitual — glossário observado

O produto define seus termos **no primeiro uso**, e isso é consistente. Colhido das telas, sem
consultar spec:

| Termo | Definição que a tela dá |
|---|---|
| **Recorte** | *"a lista em que a pessoa concorre — a ampla concorrência, ou uma Modalidade de Concorrência declarada"* |
| **Faixa** | *"o trecho da ordem que um ato publicou — do primeiro colocado ao último que o alvo alcançou"* |
| **Geração** | *"o conjunto de faixas emitido de uma vez"* / na exportação: *"o ato de montar o arquivo de uma população escolhida"* |
| **Consolidar** | *"transformar as avaliações concluídas de cada inscrição no Resultado da Etapa dela"* |
| **Apurar** | *"Abrir esta tela não apura nada. Os números vêm de atos já emitidos, e onde não há ato não há número."* |
| **Presidir** | *"presidir uma comissão não atribui trabalho de avaliação"* |

**Diferença entre significado inferido e real — onde ainda existe:**

- **"7 de 7"** ao lado de *"tem inscrição sem avaliador suficiente"*. Só no destino se descobre que é
  *inscrições sem cobertura* sobre *inscrições submetidas*. No painel é número sem unidade.
- **"sem marco no cronograma"**. Inferi "atrasada". O código é explícito que **não** é isso — *"nunca
  como atraso, espera ou progresso zero"* — mas a tela não diz o que é, e a frase fica sem
  consequência legível.
- **`cand:seed-f16bfa4b-02`** aparece como *"INTERPOSTO POR"* na tela do recurso, ao lado de três
  UUIDs crus. Identificador interno na cara de quem julga.
- O **seletor de identidade** lista permissões em vocabulário de código: `edital:elaborar`,
  `retificacao:submeter`. É demonstração, não produção — mas é a primeira tela que um novato vê.

**Foi necessário consultar código para entender algo que a interface deveria dizer?** Sim, quatro
vezes, e cada uma virou achado: (a) por que o publicador vê *"nenhuma condição de atenção"*; (b) por
que o recurso interposto não apareceu; (c) por que *"Abrir a Supervisão"* devolve 404; (d) por que
`UX-001`/`UX-002` não se resolvem na tela para onde apontam.

---

## 9. Encontrabilidade por intenção

| Eu quero… | Eu procuraria em… | Onde estava | Nota | 13/09 → 16/09 |
|---|---|---|---|---|
| saber qual Edital precisa de atenção | painel do Processo | lista plana de 15 linhas, sem agregação por Edital; e **incompleta** por papel | **E2** | era E4 |
| encontrar avaliações pendentes | painel | *Abrir a distribuição da Etapa*, direto | **E0** | era E2 |
| julgar um recurso | painel | ❌ no painel só depois de admitido. Mas a **lista de Processos** mostra *"Recursos recebidos (1)"* ao julgador | **E1** | era E2 |
| publicar um ato já emitido | painel | sinal `UX-066` com caminho — **para quem tem `resultado:publicar`** | **E0** | era E4 (`ACH-40`) |
| ocupar vagas de uma ordem pronta | painel | sinal `UX-065` com caminho | **E0** | era E2 |
| preparar ou executar um sorteio | painel | ❌ Edital → marco. O painel não fala de sorteio | **E2** | era E2 |
| convocar | Edital | marco → ocupação → convocação | **E2** | era E2 |
| acompanhar matrícula | painel | ❌ Edital → *Exportar para matrícula* | **E2** | igual |
| corrigir uma publicação | Edital | *"Peça a alguém com a permissão de retificar que a proponha."* | **E0** | era E1 |
| **acrescentar Modalidade** | Retificação | *"Modalidades de Concorrência ainda não são definidas por aqui."* — honesto, e **sem saída** | **E4** | igual |
| saber qual prazo vence primeiro | painel | *Próximos marcos* por Edital, **sem ordenação global entre Editais** | **E2** | era E3 |
| entender por que uma ação não está disponível | a própria tela | as telas explicam, e nomeiam a permissão que falta | **E0** | era E2 |

**Movimento real:** quatro intenções subiram (três para E0). Duas continuam em E2 porque o painel
não as cobre. Uma continua em E4 e é decisão pendente, não defeito de interface.

---

## 10. Organização do trabalho

**O que funciona.** A mesa do avaliador, a distribuição e a consolidação continuam os melhores
artefatos do produto. A proposta de distribuição mostra *"7 atribuições em 7 inscrições, distribuídas
por menor carga … nada foi gravado ainda"* com a tabela **tem hoje / recebe / fica com**. A
presidência é verificada contra o vínculo, não contra papel, e a tela diz isso.

**O que não funciona — `ACH-60`, intocado.**

| Evidência | Medida |
|---|---|
| filtro por Perfil, polo ou modalidade na distribuição | **zero ocorrências** em `distribuicao.html` |
| eixo da alocação | `Etapa × avaliador` — 9 colunas para 3 Editais, com rolagem horizontal já em 1024px |
| como o polo existe | atributo `locality` do Perfil (`"Campus Serra"`), não eixo próprio (`AX-6`) |

Consequência para o Cenário D, com 7 polos: 21 colunas na matriz; nenhuma comissão local consegue
receber só o seu recorte; a presidência enxerga o todo porque **só existe o todo**.

Um acerto que não deve se perder: a página *Minhas Etapas* do presidente diz
*"Você não possui Etapas atribuídas — presidir uma comissão não atribui trabalho de avaliação"* e
encaminha a *Gerir comissão* e *Alocação por Etapa*. Ausência honesta com continuação.

---

## 11. Autorização, recusas e dados pessoais

### Recusas medidas hoje

| Alvo | julgador | auditor | gestor | elaborador | Classificação |
|---|---|---|---|---|---|
| `criar_edital` | 404 | 404 | 200 | 404 | ❗ deveria ser **403** (`D-G2`) |
| `reaproveitar` | 404 | 404 | **404** | 404 | ❗ deveria ser **403** (`D-G2`) |
| `supervisao` | 404 | 404 | 200 | 404 | ❗ deveria ser **403** (`D-G2`) — **e é oferecida como link** |
| `auditoria` | 403 | 200 | 403 | 403 | ✅ capacidade sobre objeto conhecido |
| `matriculas` | 403 | 403 | 403 | 403 | ✅ negar por padrão; papel próprio |
| `recursos` | 200 | 403 | 403 | 403 | ✅ |
| `inscricoes` | 403 | 403 | 200 | 403 | ✅ dado pessoal por permissão própria |

**Taxonomia aplicada:** as quatro linhas ✅ são *falta de capacidade sobre objeto conhecido*, e
respondem 403 — correto. As três ❗ também são objeto conhecido (o ator está olhando o Processo) e
respondem 404. **A decisão `D-G2` de 19/09 já corrigiu isso no papel; o código não a executou.**

**Não recomendo trocar 404 por 403 em bloco.** As quatro recusas que a `D-G2` mandou manter em 404 —
`anexo_do_rascunho`, `minha_etapa`, `inscricao_da_mesa`, `documento_da_mesa` — protegem vínculo
enumerável, e continuam certas. `[NÃO REAUDITADO]` individualmente: exigem objetos que este percurso
não produziu.

### Dados pessoais

`[MEDIDO]` Contraprova com atores distintos:

- `matricula:exportar` **não** é concedida a nenhum papel existente. O gestor, que tem
  `inscricao:consultar`, recebe **403** na exportação. A distinção *"ler um dossiê por vez e baixar o
  conjunto inteiro são atos distintos"* está executada, não só escrita.
- A lista pública do resultado *"nomeia apenas quem recebeu posição; quem não recebeu vê a própria
  situação dentro da inscrição"* — verificado na prévia de publicação.
- O acesso do candidato responde *"Se este endereço **puder ser utilizado**, enviaremos um código"* —
  sem enumeração de e-mail.

**Um vazamento menor, não de dado pessoal mas de arquitetura:** a tela do recurso exibe
`cand:seed-f16bfa4b-02` e três UUIDs crus a quem julga.

---

## 12. Top 10 fricções atuais

Agrupadas por causa, não por sintoma. Achados fechados não reaparecem.

| # | Fricção | Sev | Causa |
|---|---|---|---|
| **N-01** | *"Nenhuma condição de atenção neste Processo"* afirma ausência global a partir de leitura parcial | **S3** | a frase é absoluta; a computação é relativa ao leitor |
| **N-02** | Recurso **aguardando admissibilidade** não produz sinal em nenhuma superfície | **S3** | `sinais_do_recurso` filtra só `AGUARDANDO_JULGAMENTO` |
| **N-03** | *"Abrir a Supervisão"* é oferecido a todo papel e devolve 404 a todos menos o gestor | **S2** | regressão de `32cd6d9` — a guarda existe na linha 20 e falta na 64 |
| **N-04** | 9 de 15 sinais do gestor não têm caminho **nem dizem a quem pedir** | **S2** | o padrão *"Peça a alguém…"* da `037` está no Edital e não no painel |
| **N-05** | `UX-001` e `UX-002` encaminham à Retificação, que **não alcança** os campos que os causam | **S2** | `stages.scheduleEventId` é `estrutural()`; `schedule.status` é `derivado()` |
| **N-06** | `schedule.status` é declarado *derivado* e **nada o deriva** | **S2** | fica `PLANEJADO` para sempre → um `UX-002` permanente por Edital |
| **N-07** | *"2 de 5 sem avaliador suficiente"* conta inscrição eliminada na Etapa anterior | **S2** | a mesma tela a separa em *"1 eliminadas antes"* e a exclui da lista |
| **N-08** | Avisos de *Validação do conteúdo* do Edital não chegam à *Atenção* do painel | **S2** | duas superfícies de problema sem junção |
| **N-09** | Identificadores internos na tela do recurso (`cand:…`, UUIDs) | **S1** | vocabulário de arquitetura exposto |
| **N-10** | Exportação: submeter sem escolher o conjunto recarrega a página **sem mensagem** | **S1** | validação sem retorno |

**Fora da lista, por serem de ferramenta e não de produto:** `seed_demo --numero` com 3 dígitos
quebra (monta UUID por interpolação — `'00000000-0000-0000-00101-…' não é um UUID válido`); e o teste
instável da §2.

### Evidência dos três primeiros

**`N-01`** · Cenário E · persona **publicador** · página do Processo `PS-CONV-A`.
Estado inicial: 16 condições de atenção existem (15 + o ato por divulgar). Ação: divulguei o ato do
*Sorteio público* do `66/2026`. Comportamento: a região passou a exibir
**"Nenhuma condição de atenção neste Processo."** Contraprova: no mesmo instante, `carla.gestora`
(Gestor) via **15 condições** na mesma página. Consequência: quem publica conclui que o certame está
em dia. Recuperação: nenhuma pela interface — a pessoa teria de assumir outro papel para descobrir.
Medido também fora do navegador, papel a papel: `frase_nenhuma` é `True` **apenas** para o publicador;
para elaborador, homologador e exportador — que alcançam **zero** espécies — a região corretamente
não aparece. O fix `32cd6d9` fechou o caso de zero espécies e **deixou aberto o de "alcança ao menos
uma, e nenhuma delas dispara"**.

**`N-02`** · Cenário E · persona **candidato → gestor/julgador**.
Estado inicial: resultado preliminar divulgado no `91/2026`, prazo recursal aberto até 25/09.
Ação: interpus recurso como Bruno Costa às 00h37 — `REC-2026-VYN6GNTG`, *"Aguardando análise de
admissibilidade"*, *"Dentro do prazo"*. Expectativa: o Processo vivo passa a mostrar trabalho novo.
Comportamento: **zero sinais novos**, para gestor, julgador, auditor e publicador. Só depois de eu
admiti-lo o `UX-064` apareceu. Consequência: a peça com prazo fica invisível exatamente na fase em
que o prazo corre. Recuperação: existe e é boa — a lista de Processos mostra *"Recursos recebidos
(1)"* ao julgador. Mas não é o painel, e é o painel que a feature criou para isso.

**`N-03`** · qualquer cenário · personas **auditor, publicador, julgador, elaborador**.
Estado inicial: na página do Processo, que abre para todos eles. Ação: seguir *"Abrir a Supervisão"*.
Comportamento: **404**. Contraprova: `gestor` → 200. Código:
`processo_detalhe.html:20` envolve o botão *Supervisão* em `{% if pode_gerir_comissao %}`;
`processo_detalhe.html:64` repete o mesmo destino **sem guarda**, dentro de `{% if pulso %}` — e o
fix `32cd6d9` tornou `pulso` sempre presente. Consequência: o beco que a `033` e a `037` gastaram
duas features removendo reapareceu na tela nova.

---

## 13. Matrícula e Registro Acadêmico

**O que medi.** `91/2026` → *Exportar para matrícula*, como `elias.exportador`.

A tela é o melhor exemplar de **ausência honesta** do produto. Cada coluna que sairá vazia é
nomeada, contada e **explicada por natureza da lacuna**:

| Coluna | Razão declarada |
|---|---|
| `RENDA_PER_CAPITA_PNP` | *"a faixa da renda somada da família … num campo que o destino define como renda por pessoa. Os limites coincidem e os denominadores não … O desvio é sempre para cima"* |
| `CLASSIF_CURSO_FINAL` | *"O destino não diz se a coluna é a classificação no curso ou a numeração das linhas"* |
| `COD_CURSO`, `COD_TURNO`, `COD_POLO` | *"Vocabulário do sistema acadêmico, que este sistema não conhece"* |
| `COR` | *"A exportação não substitui por valor próximo"* — e nomeia: *Ana Silva declarou «Indígena»* |
| `NOME_PAI`, `COMPLEMENTO` | *"Não declarado no Requerimento de Matrícula"* |

| Verificação | Resultado |
|---|---|
| valores inventados | ❌ nenhum — e a recusa de substituir por valor próximo é explícita |
| desconhecidos vazios | ✅ e explicados, um a um |
| resultado, convocação e matrícula concordam | ✅ 1 convocado, 1 requerimento, 1 linha |
| o Registro Acadêmico entende o que fazer | ✅ o resumo é a instrução |
| retenção | ✅ *"O arquivo não fica guardado… é montado, entregue e descartado"* |
| "exportar tudo" | ✅ não existe |
| **importação / validação no destino / reexportação** | ⛔ **`[NÃO VALIDADO]` — sistema de destino indisponível** |
| rastreabilidade da versão exportada | ✅ registro de quem gerou, quando, quantas linhas |
| o Processo vivo mostra essa fase | ❌ não |

**Risco operacional da ausência no painel da `038`: baixo hoje, crescente.** Com 1 convocado, o
Edital é o lugar natural. Com 40 convocados e requerimentos parciais, "quantos ainda não enviaram"
passa a ser pergunta de condução — e hoje não tem onde ser feita.

---

## 14. Regressões e problemas deslocados

**Uma regressão, confirmada:**

- **`N-03`** — `32cd6d9` abriu a página do Processo a quem não passa por `pode_supervisionar`, sem
  estender a guarda ao segundo link para a Supervisão. Antes do fix, esses atores não recebiam a
  região; agora recebem, com um link morto.

**Dois problemas deslocados:**

- **`ACH-08`** — a régua de "vencido" foi corrigida na `037` (`calendario.py::vencido`, `FR-545/546`),
  e a composição parou de chamar de vencido o período em curso. Mas o **painel da `038`** passou a
  exibir o período em curso como condição de *Atenção* (`UX-002`), permanentemente e sem conserto. O
  custo mudou de superfície. **Não é a mesma falha** — e por isso `ACH-08` fica `FECHADO` com o custo
  novo registrado como `N-06`, não como regressão dele.
- **`ACH-27`** — os contadores concorrentes saíram da relação Processo↔Supervisão (ganho real e
  medido) e reaparecem **dentro** da tela de distribuição, onde 9 mosaicos convivem e um contradiz a
  lista logo abaixo (`N-07`).

**Nenhuma outra regressão encontrada.** Verifiquei, feature a feature de `029` a `038`: nenhum
conteúdo publicado foi reescrito; nenhuma permissão nova foi concedida por efeito colateral (o
`matricula:exportar` continua isolado, e o `recurso:julgar` também); nenhum dado pessoal apareceu
fora de quem tem permissão própria; nenhum cálculo foi duplicado — ao contrário, a `038` **removeu**
uma duplicação ao fazer as duas superfícies lerem `pulso` e `sinais` do mesmo módulo.

---

## 15. Padrões excelentes a preservar

1. **A prévia antes do ato irreversível.** *"Esta é uma prévia: nada foi gravado."* + *o que acontece
   ao confirmar* + a lista inteira do que será publicado. Repetida na distribuição
   (*"nada foi gravado ainda"* com tem hoje/recebe/fica com) e na exportação.
2. **A ausência honesta.** *"Ocupação ainda não apurada"*, *"Nenhuma inscrição submetida declarou esta
   lista"*, *"Este Edital ainda não publica nada aqui"*, e o relatório de colunas vazias da
   exportação. **Este é o padrão mais forte do produto** — e é exatamente o que `N-01` quebra.
3. **O comentário que registra a decisão e o custo.** `supervisao.py` explica por que a supressão é
   silenciosa, por que não existe `gravidade`, por que o rótulo do destino diz o que se encontra e
   não o que se faz. É documentação que não envelhece porque mora ao lado do código.
4. **Dizer a quem pedir.** *"A instrução depende da permissão de gerir a comissão ou da presidência —
   cada uma basta sozinha. Peça a alguém com a permissão de gerir a comissão…"* Nomeia a capacidade
   **e** o ato. Precisa alcançar o painel.
5. **A tela do sorteio.** Nove conceitos difíceis numa página, sem manual.
6. **A recusa que explica.** *"Julgar não as concede."* / *"Os parâmetros da cota mudam por
   versionamento da regra normativa, e não por correção do texto publicado."*
7. **Papel próprio para dado sensível.** `matricula:exportar` e `recurso:julgar` não penduram em
   nenhum papel existente, e a razão está escrita no código.

---

## 16. Decisões de governança

| Decisão | Estado hoje | O que falta |
|---|---|---|
| **`D-G1`** — `FR-461` impeditiva | **não executada** | o aviso *"o marco SORTEIO não declara regra de corte"* continua aviso no `66/2026` |
| **`D-G2`** — fronteira 403/404 | **não executada** | medido: as três recusas continuam 404 |
| **`D-G3`** — sorteio com ocorrência externa | **não executada**; produto já suporta o modelo forte | a regra do **reaproveitamento** é a parte não óbvia: o `66/2026` reaproveitado herdaria a cláusula antiga |
| **`D-G4`** — peso é da Etapa | **encerrada**, sem trabalho | — |
| **`D-G5`** — Retificação acrescenta Modalidade | **não executada** | medido: `SECOES_QUE_ACRESCENTAM = {perfis, cronograma, anexos}`; a tela declara a ausência |
| **Organização por Perfil/polo** | **pergunta aberta**, não decidida | `AX-6` + `ACH-60`. Não há decisão registrada sobre polo virar eixo |
| **Responsabilidade no painel** | **decidida pela `038`, e a decisão se sustenta** | ver abaixo |

### Responsabilidade — a decisão da `038` está certa

A `038` decidiu não nomear pessoa responsável porque o produto não relaciona identidade concreta a
papel operacional. `[MEDIDO]` Nenhuma das 16 mensagens nomeia pessoa; a mais próxima diz
*"com membro da comissão desimpedido para julgá-lo"* — uma **propriedade do conjunto**, não um nome.

**Informar estado e destino é suficiente?** Para os 6 sinais que têm caminho, sim. Para os 9 que não
têm, **não** — mas o que falta não é o nome da pessoa: é **a capacidade a pedir**, que o produto
conhece e já sabe redigir em outra tela. `N-04` é o achado; modelar responsabilidade individual
seria inventar certeza que não existe.

**Existe evidência para modelar responsabilidade?** Não encontrei. E há contraevidência: a
presidência não é papel — vem do vínculo com a comissão —, e a equipe inicial de 2–3 pessoas acumula
papéis, de modo que "o responsável" seria frequentemente a mesma pessoa em três linhas. **Manter a
decisão.**

---

## 17. Problemas estruturais restantes

| Raiz | Estado | Medição |
|---|---|---|
| `E-1` cauda não fecha | ✅ | percorrida hoje |
| `E-2` autorização × navegação | ⚠️ **reaberta em um ponto** | `N-03` — a `038` criou um caminho que a autorização recusa |
| `E-5` explicação desgrudada do campo | ✅ | os campos bloqueados da Retificação explicam-se no lugar |
| `E-7` validação sem executabilidade | ✅ | os avisos do `66/2026` nomeiam entidade, falta e etapa |
| **`E-6` visão global** | 🟡 **parcial** | §6 — reduziu, não fechou |
| **`E-3` duas gramáticas normativas** | 🔴 | `[NÃO REAUDITADO a fundo]` nada mudou desde 16/09 |
| **`E-4` fontes sem confronto** | 🔴 | `[MEDIDO]` três nomes para duas coisas no `66/2026`; e `N-06` é um caso novo da mesma doença — **um campo declarado derivado que nada deriva, e um sinal que compara o valor obsoleto com o relógio** |
| **organização por recorte** | 🔴 | `ACH-60` + `AX-6`, intocados |

**A observação desta auditoria sobre `E-4`:** ela deixou de ser só "duas fontes que ninguém
confronta" e ganhou uma terceira forma — **uma fonte que deveria ser derivada e não é, e um
confronto que existe e não pode ser resolvido**. `N-05` e `N-06` são `E-4` vista do lado da condução.

---

## 18. Prontidão de produção

| Dimensão | Estado |
|---|---|
| **identidade real** | ⛔ o seletor é demonstração, e a própria tela diz: *"Esta interface não pode ser usada em produção antes da autenticação real."* Produção recusa subir com as variáveis ligadas |
| **armazenamento privado** | ✅ documentos por rota autorizada; a exportação não guarda arquivo |
| **retenção** | ✅ declarada para a exportação; ⚠️ não auditei retenção de documentos de inscrição |
| **observabilidade** | ⚠️ log estruturado JSON existe (`{"level": "WARNING", "logger": "django.request"…}`); não há métrica de condução |
| **recuperação** | ✅ o modelo é sucessão de atos, não edição. Nada se despublica; corrige-se por ato sucessor |
| **integrações** | ⚠️ Registro Acadêmico `[NÃO VALIDADO]`; fonte do sorteio tem E2E real atrás de flag |
| **operação cotidiana** | ⚠️ **é aqui que está o gargalo** — a superfície de vigília é a `038`, e §6 diz o quanto dela é confiável |
| **custo de consulta** | ⚠️ ~17 consultas por Edital publicado, linear; medir antes de um Processo grande |

---

## 19. Backlog priorizado

**Correção** (cabem em uma varredura só, e são a mesma família):
`N-03` guarda do link · `N-10` mensagem ausente · `N-09` identificadores internos ·
`seed_demo --numero` · o teste instável do CSRF.

**Correção com decisão embutida:**
`N-01` a frase de ausência · `N-04` dizer a quem pedir no painel · `N-07` o contador que inclui
eliminados.

**Estrutural:**
`N-05` + `N-06` — o par *campo derivado que nada deriva* + *sinal que encaminha a quem não resolve*.
Não se conserta acrescentando campo à Retificação: o contrato de mutabilidade está **certo** ao
chamar `status` de derivado. O conserto é derivar.

**Decisão institucional** (já tomadas, não executadas): `D-G1`, `D-G2`, `D-G3`, `D-G5`.

**Pesquisa:** polo como eixo (`AX-6`/`ACH-60`) — precisa de Edital real de múltiplos polos antes de
qualquer abstração.

**Integração:** validação ponta a ponta com o Registro Acadêmico.

**Melhoria estrutural:** `E-3` e `E-4`.

**Polish:** as três renderizações do prazo restante; o prazo recursal ausente da página pública.

---

## 20. Próximos três investimentos

**1. Fechar a `038` — não ampliá-la.**
`N-01`, `N-02`, `N-03`, `N-04`. São quatro defeitos de uma feature recém-entregue, e três deles são
pequenos. **`N-02` é o único que pede decisão**: se recurso aguardando admissibilidade vira espécie
nova ou se `UX-064` passa a cobrir as duas situações. Sem isso, a feature que existe para mostrar o
Processo vivo esconde a peça com prazo e mente para quem enxerga pouco.

**2. Derivar o que está declarado derivado.**
`N-06`, e com ele `N-05` some sozinho: derivado o `status`, `UX-002` só dispara em contradição real,
e deixa de encaminhar a uma tela que não a resolve. É a menor mudança do backlog com o maior efeito
sobre a razão sinal/ruído do painel — e ataca `E-4` num ponto onde ela já é executável.

**3. `D-G5` — Retificação que acrescenta Modalidade.**
É a única coisa na lista que descreve **um Edital publicado sem conserto possível**. A reavaliação de
19/09 já registrara que, pela severidade, era a coisa mais grave da fila, e a escolha de fazer o
painel antes foi consciente. O painel foi feito. **É a vez dela.**

**Não recomendo outro painel.** O problema da `038` não é falta de superfície — é que a superfície
existente não é acionável nem honesta sobre o que não mostra. Acrescentar sorteio e matrícula a uma
região onde 60% das linhas já não levam a lugar nenhum pioraria a relação sinal/ruído.

---

## 21. O que não fazer

- **Não acrescentar `scheduleEventId` e `status` aos campos da Retificação.** Seria o remédio óbvio
  para `N-05`, e mascararia `N-06`: o contrato de mutabilidade está certo ao chamá-los de estrutural
  e derivado. Retificar um campo derivado é gravar à mão o que devia ser calculado.
- **Não trocar 404 por 403 em bloco.** A `D-G2` já disse por quê, e as quatro que ficam em 404 estão
  certas.
- **Não silenciar `UX-001` e `UX-002`** para limpar o painel. Eles reportam fato verdadeiro sobre
  conteúdo publicado. O defeito é o encaminhamento, não a detecção.
- **Não transformar os avisos de validação do Edital em sinais de Atenção sem decidir a fronteira.**
  São de naturezas diferentes — um é "a composição tem imperfeição", o outro é "há trabalho parado".
  Juntá-los sem critério produziria a lista plana de 25 linhas.
- **Não modelar responsável individual** para preencher a lacuna de `N-04`. O que falta é a
  capacidade a pedir, e o produto já sabe dizê-la.
- **Não abstrair polo** antes de ter o Edital real de múltiplos polos na mão.
- **Não tratar teste verde como fluxo compreensível.** 7478 testes passam, e as quatro coisas que
  achei no painel passam por todos eles.

---

## 22. Fechamento

**1. Quais partes do Processo uma pessoa compreende apenas usando o sistema?**
Quase todas. Composição, publicação, inscrição, alocação, distribuição, consolidação, classificação,
**sorteio inteiro**, divulgação, ocupação, convocação, exportação para matrícula, e o ciclo do
recurso do lado do candidato. Cada tela define seus termos no primeiro uso.

**2. Onde ela ainda precisa conhecer a arquitetura interna?**
Em quatro pontos, e todos são achados: por que o painel diz que não há nada quando há; por que o
recurso que acabou de chegar não aparece; por que um link oferecido devolve 404; e por que dois
terços dos sinais apontam para um ato que não os resolve. Some-se a exposição de
`cand:…` e UUIDs crus a quem julga.

**3. Onde a dificuldade pertence legitimamente ao domínio?**
Na imutabilidade da publicação e na Retificação como único caminho de correção. Na separação entre
emitir ordem e divulgá-la. Na distinção entre comprometer o universo e derivar a semente. Nenhuma
dessas é problema de interface — e o produto as ensina bem.

**4. É possível assumir um Processo já em andamento?**
**Sim, com uma condição que hoje não é dita:** é preciso acumular papéis. Medido — o gestor vê 15
sinais e não vê o ato por divulgar; o publicador vê 1 e não vê os 15. Nenhum papel isolado enxerga o
Processo inteiro, e **nenhuma tela avisa que a vista é parcial**.

**5. A página do Processo permite identificar a próxima ação?**
**Parcialmente.** Para avaliação, ocupação e divulgação, sim e bem — nome, medida e destino. Para
cronograma e Etapas, não: a frase não tem consequência, e quando tem caminho o caminho não resolve.
Para "qual Edital precisa de atenção", não: é lista plana sem agregação.

**6. Processo e Supervisão apresentam a mesma verdade?**
**Sim.** Uma derivação, um módulo, duas views que o leem. Números, frases e ordenação idênticos,
medidos lado a lado. **É a promessa mais bem cumprida da `038`.**

**7. A `038` fechou `ACH-25`/`E-6` ou apenas reduziu o problema?**
**Reduziu.** Fechou a divergência entre superfícies e deu nome, medida e destino a quatro estados
que eram invisíveis. Não fechou a condução: a vista é parcial por papel e não se declara parcial, a
maioria do que mostra não é acionável por quem conduz, e o recurso recém-interposto continua
invisível. **Visão global: 5 → 6, não 8.**

**8. Sorteio e matrícula precisam entrar na condução global?**
**Ainda não — e a ausência não é o problema que parece.** Demonstrei o impacto: o sorteio já tem uma
tela que conta a viagem inteira, e a matrícula, com um convocado, é encontrável pelo Edital. O buraco
real da cauda **não é sorteio nem matrícula — é a admissibilidade do recurso**, que a `038` achou que
cobria e não cobre. Corrigir isso vale mais do que as duas ausências planejadas juntas.

**9. As melhorias `029`–`038` fecharam problemas ou os deslocaram?**
**Fecharam, majoritariamente.** Cinco das sete raízes estruturais, os seis `P0`, a cauda inteira, a
prova do recurso, o sorteio executável. **Dois deslocamentos**, ambos nomeados: `ACH-08` mudou de
superfície e `ACH-27` mudou de tela. **Uma regressão**, pequena e localizada: `N-03`.

**10. Quais riscos impedem operação institucional?**
Nenhum de integridade, direito do candidato, publicação ou auditabilidade — as duas camadas de
imutabilidade estão de pé e nada publicado foi reescrito. O que impede é **autenticação real** e a
**confiabilidade da superfície de vigília**: um instrumento de condução que declara "nada a fazer"
sem ter olhado tudo é pior que não ter instrumento, porque produz confiança.

**11. Qual é a principal qualidade do produto?**
**A honestidade do que ele não sabe.** O relatório de colunas vazias da exportação, o
*"Ocupação ainda não apurada"*, o *"Modalidades de Concorrência ainda não são definidas por aqui"*, o
*"Abrir esta tela não apura nada"*. Nenhum outro produto administrativo que eu conheça recusa
preencher uma célula e explica por quê, nomeando a pessoa e o valor declarado.

**12. Qual é a principal fragilidade?**
**A superfície que vigia o certame ainda não se aplica o próprio padrão de honestidade.** A `038`
herdou tudo do produto — a derivação única, a supressão por menor privilégio, o rótulo que diz o que
se encontra — menos a regra de ouro: dizer o que não sabe.

**13. Qual deve ser o próximo investimento?**
Fechar a `038`. É pequeno, é da feature recém-entregue, e sem ele os dois investimentos seguintes
serão medidos por um instrumento que não é confiável.

---

### As cinco evidências sobre a meta de não precisar de manual

1. **A favor.** A tela do sorteio ensina nove conceitos de auditabilidade — congelamento, ocorrência,
   derivação, normalização, manifesto, verificação — em uma página, sem nota de rodapé. *"O universo é
   comprometido antes de a semente existir."*
2. **A favor.** O relatório de colunas vazias da exportação não inventa nenhum valor, explica cada
   lacuna pela sua natureza, e chega a nomear a pessoa: *Ana Silva declarou «Indígena»*, e o formato
   de destino não comporta.
3. **A favor.** A tela do recurso diz que julgar não concede acesso à prova, nomeia a permissão que
   falta e o ato a pedir: *"Peça a alguém com a permissão de gerir a comissão ou a quem preside este
   Processo que a pratique."*
4. **Contra.** Um publicador vê **"Nenhuma condição de atenção neste Processo"** enquanto quinze
   condições existem — e nada na tela permite suspeitar disso. Foi preciso ler `supervisao.py` para
   entender.
5. **Contra.** Um recurso tempestivo, interposto e protocolado, não mudou **nada** em nenhuma
   superfície de condução até ser admitido. A feature criada para mostrar o Processo vivo não mostrou
   a única coisa que tinha acabado de acontecer nele.

---

### Recomendação final

> **Executar piloto controlado**, com as condicionantes `C1`–`C7` da §1.

**Justificativa.** O certame corre inteiro e é compreensível sem manual em quase toda a sua extensão
— isso não era verdade há dezoito dias e é uma mudança de patamar, não um ajuste. O que não está
pronto é a **operação desassistida**: a superfície que a instituição usaria para vigiar vários
certames ao mesmo tempo ainda afirma mais do que mediu.

Um piloto com **um Processo, dois ou três Editais e uma pessoa acumulando papéis** — que é
exatamente a configuração da equipe inicial — **não encontra nenhum dos quatro defeitos do painel**,
porque quem acumula papéis vê tudo e não recebe a frase falsa. É por isso que o piloto é seguro, e é
por isso que ele **não serve de prova** para a operação institucional: a segregação de funções, que é
o que a operação institucional exige, é justamente o que expõe `N-01` e `N-04`.

**Condição de saída do piloto para operação institucional:** `C1`–`C5` fechadas, autenticação real
integrada, e uma medição de custo de consulta num Processo de dez ou mais Editais.
