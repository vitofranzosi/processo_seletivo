# Feature Specification: Destinação da vaga reservada sem ocupante

**Feature Branch**: `claude/elegant-robinson-e66ed2`, sobre a `main` em `ef568113` (depois do #477)

**Created**: 2026-11-11

**Status**: Draft para revisão — as dez perguntas foram respondidas pelo usuário em 11/11/2026 e
viraram as decisões D-005 a D-014. A D-016 foi aprovada por ele em 11/11/2026. **A D-015 — a
condição da reversão por saldo — está em aberto**: o confronto com as cláusulas do 57/2026 e do
35/2026, pedido por ele, está na própria D-015, e a regra não fecha sem a escolha dele.

**Input**: *"Escrever a spec para a destinação da vaga de cota sem concorrente. Não adote reversão
automática nem declare a vaga não preenchida por padrão. Levante o que o sistema já permite e proponha
uma spec para aplicar a destinação prevista no Edital, com fundamento e registro explícitos. Traga os
casos que exigem minha decisão antes de fechar a regra."* A orientação entre aspas é do usuário,
literal; o restante do pedido veio da sessão que coordena os achados do estudo. As respostas dele às
dez perguntas, de 11/11/2026, estão em *Decisões* e pediram ainda: *"Atualize os requisitos, cenários
e revisões das specs afetadas. Confirme por teste os comportamentos levantados apenas pela leitura do
código."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de seis mil e trezentos a seis mil trezentos e quarenta e nove;
> - os critérios de dois mil e cem a dois mil cento e dezenove;
> - os requisitos de experiência de seiscentos a seiscentos e dezenove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`. As perguntas da primeira
> versão, numeradas de um a dez, foram respondidas e viraram as decisões `D-005` a `D-014`, na mesma
> ordem.
>
> A reserva está nas notas compartilhadas das sessões do estudo, ao lado das da `152`, da `153` e da
> `154`, que mexem em convocação e documentos e não em ocupação.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-246 da `016`"); decisão de outra feature, pelo assunto, nunca pelo identificador.
>
> **Origem.** O
> [estudo da jornada final de 11/11/2026](../../doc/estudo-jornada-final-2026-11-11/index.html)
> (PR #472), achados 02 e 16 do inventário, sobre o cenário de treinamento C09 da `134`
> (Edital SIM09/2026). No estudo os achados levam o prefixo dos requisitos de experiência; aqui eles
> se escrevem "achado 02" e "achado 16", para que a varredura de citações não os leia como requisitos
> desta spec. O #477 já tirou da tela a sugestão do ato recusado; a regra, ele deixou para cá.

## Esta entrega

*(Acrescentada em 12/11/2026, na redução da implementação à entrega mínima aprovada pelo usuário.)*
A implementação completa — todos os requisitos abaixo, menos o incremento F, bloqueado pela D-015 —
está preservada na branch `claude/155-destinacao-completa` e na tag `155-destinacao-completa`, ambas
no repositório remoto. Esta entrega leva só o recorte abaixo; o resto é a **próxima entrega**, e os
requisitos dela estão marcados *(próxima entrega)* ao lado do identificador, sem redação apagada.

**Entra:**
- **a)** a situação da vaga sem quem a ocupe, dita igual na ocupação, no Centro e na convocação
  (FR-6300 a FR-6304, UX-600, UX-602), e a declaração de vaga não preenchida, no Edital silente e na
  linha geral, com a coluna `nao_preenchidas` da apuração e a causa de obsolescência dela (FR-6320 a
  FR-6327);
- **b)** os impedimentos (FR-6306, FR-6307); a tabela nova append-only, por gatilho e por privilégio;
  a conferência assinada, o fundamento obrigatório, a trilha e a permissão da comissão (FR-6341,
  FR-6342, FR-6344); e o desfazimento da declaração, com o impedimento dito no lugar do botão quando
  há chamada dependente (FR-6334 a FR-6336).

**Fica para a próxima:** o ato "Destinar à ampla concorrência" e o desfazimento dele (FR-6308 a
FR-6314); a emissão que deixa de mover vaga (FR-6315, FR-6316); a passagem entre cotas (FR-6317 a
FR-6319, UX-603); a lista vazia e o sorteio sem relação (FR-6328 a FR-6333); a página pública, o
relatório e o fundamento na chamada (FR-6337 a FR-6340); as prévias (FR-6343); e, bloqueada pela
D-015, a condição do saldo (FR-6305).

**Onde o Edital declara a reversão, a regra é a de antes da `155`.** A apuração da lista reservada
continua cedendo a vaga à ampla, nas duas espécies, como a `016` a escreveu. Onde ela não cede — a
V-1 da [verificação](verificacao-do-levantamento.md), por esgotamento, em que a ordem ainda conta
quem desistiu —, a tela diz a situação, a regra e o próximo passo, sem botão, e a declaração de não
preenchida continua recusada (FR-6327).

## Por que esta feature existe

No C09, o Perfil "Professor de Informática" publica quatro vagas: três na ampla concorrência e uma
na cota PPP. As seis inscrições são todas da ampla. **Ninguém concorre pela PPP.**

1. **A vaga da cota não vai a lugar nenhum** (achado 02, prioridade crítica). A apuração da PPP dá
   "0 de 1, 1 a ocupar". Antes do #477, o "O que fazer agora" mostrava "Pedir a faixa seguinte" como a
   próxima ação, para a presidência e para o Gestor — e o comando recusava: *"o Edital não publicou
   que admite continuação além da faixa"*. Hoje o Centro diz "Ocupar a vaga — impedida", com a razão.
   É honesto, e é um beco: **nenhum ato leva a vaga a algum lugar**, a fase Vagas nunca fecha, e a
   equipe não sabe se a vaga se perde, reverte à ampla ou exige Retificação.
2. **Antes de chegar ali, a lista vazia pediu três atos sem efeito** (achado 16, prioridade média):
   emitir a ordem vazia, emitir o corte vazio e — pelo Publicador — publicar o resultado vazio. Os três
   continuam pendentes no Centro até serem praticados, em todo Edital com cota sem inscrito.

O C09 não declara reversão. Mas o defeito não é do cenário: o levantamento abaixo mostra que, mesmo
nos Editais que declaram, há casos frequentes em que a destinação declarada não chega a ser aplicada,
e que a única destinação que o sistema sabe aplicar acontece **dentro** de outro ato, sem ser
confirmada como tal.

## Levantamento: o que o sistema já faz

### Implementado

| # | O quê | Onde | Como funciona hoje |
|---|---|---|---|
| I-1 | **Reversão de cota declarada no Perfil** | `016`; `ocupacao/domain/reversao.py` | O passo Perfis pergunta "Reverter vaga reservada não preenchida para a ampla concorrência", com três respostas: *Não* (vazio), *Só quando a lista reservada esgota* (por esgotamento) e *A quantidade que ficou sem preencher* (por saldo). A espécie é conteúdo publicado (FR-249 e FR-250 da `016`); declarar sem espécie é recusado na publicação (FR-251 da `016`). |
| I-2 | **A ausência de declaração não reverte** | `016`, decisão "ausência de declaração significa não move" | Edital que não declara reversão não reverte, e Edital que não declara remanejamento entre Perfis não remaneja (FR-245 da `016`). O 57/2026 (4.5) proíbe por escrito o remanejamento entre cursos, e é a prova citada no código de que inferir seria errado. |
| I-3 | **Destino único: a linha geral do mesmo Perfil** | FR-246 e FR-247 da `016` | A reversão move quantidade da linha da Modalidade para a linha geral, nunca para outro Perfil nem para outra Modalidade; a soma por recorte se preserva. |
| I-4 | **O movimento nasce dentro da apuração da reservada** | `ocupacao/application/emissao.py`, `movimento.py` | Ao emitir a apuração de uma lista reservada, o cálculo decide se a cota cede, gera o movimento e o grava **na mesma transação**, com a causa ("Vagas reservadas não preenchidas: 1 de 1"). É o único lugar do código que cria movimento de vaga. A tela mostra o movimento **depois**; antes, o botão é o mesmo "Emitir a apuração" de qualquer recorte, sem dizer que vai ceder vaga. |
| I-5 | **O desfecho de convocação não move vaga** | FR-885 da `050`, FR-270 da `019`; `convocacao/application/desfechar.py::apuracao_seguinte` | Quando a apuração seguinte de um desfecho cederia vaga, ela não é gravada, e o ato devolve a pendência *"emita-a na ocupação, onde o movimento é ato próprio"*. |
| I-6 | **A apuração da ampla fica obsoleta, com causa** | FR-263 da `016` | Recebida a vaga, a ampla mostra a apuração vigente como obsoleta por "um movimento de vaga alcançou este recorte depois dela", e o número novo sai na emissão seguinte. |
| I-7 | **Concorrência concomitante não é movimento** | FR-252 e FR-253 da `016` | Quem ocupa pela ampla não conta na reservada, e a vaga reservada continua na reserva. |
| I-8 | **Vaga acrescida e o desfazimento** | `097` | Vaga que chega de fora do Edital entra por ato com motivo, e se corrige pelo ato contrário, que cita o que desfaz. É o modelo de correção sem apagar que esta spec reaproveita (D-012). |
| I-9 | **A ordem de universo vazio é ato** | FR-4205 da `128`; `135` | No marco por pontuação, a ordem da lista sem inscrito se emite e declara que ninguém concorreu; a `135` decidiu mantê-la como providência, e a providência diz que ninguém concorre (FR-4671 e FR-4672 da `135`). Depois dela vêm o corte e a publicação do resultado, e só então a apuração. |
| I-10 | **A tela não sugere o ato que o comando recusa** | #477 | Sem continuação publicada, o Centro diz "Ocupar a vaga — impedida" e a ocupação mostra a razão no lugar do botão. |

### Declarado pelo Edital e não aplicado

| # | O caso | Por quê |
|---|---|---|
| N-1 | **Sorteio com lista reservada vazia, reversão declarada** | A relação vazia é recusada (*"não existe universo a comprometer"*), e sem relação não há corte nem apuração. Como o movimento só nasce na apuração (I-4), **nenhuma espécie de reversão chega a ser consultada** — nem a por saldo. É o achado registrado na `098`, [`doc/achado-reservada-vazia-nao-reverte.md`](../../doc/achado-reservada-vazia-nao-reverte.md), que esperava decisão do usuário. |
| N-2 | **Por esgotamento, com autodeclarados que ocupam pela ampla** | "Há quem ocupar" conta toda posição da ordem, inclusive a de quem já ocupa pela ampla e nunca ocupará a reserva. Uma reservada assim nunca esgota. É a pendência da `095` ("há quem ocupar conta quem ocupa pela ampla") e o Q4 do estudo do Edital 35. Medido no caminho oficial (V-4 da [verificação](verificacao-do-levantamento.md)). |
| N-3 | **Por esgotamento, depois de desistência ou inabilitação de todos** | Quem saiu por desfecho, ou não habilitou, continua com posição na ordem, e por isso conta como "quem ocupar" enquanto as ocupadas caem. A reserva em que ninguém mais pode ocupar não esgota. **Medido** (V-1 e V-2 da [verificação](verificacao-do-levantamento.md)). |
| N-6 | **Por saldo, a vaga reaberta com a fila da reserva ainda cheia** | Depois de uma desistência, a apuração seguinte cede a vaga à ampla **mesmo com autodeclarados habilitados na faixa da reserva**, que a fila chamaria. A desistência derruba as ocupadas, e o saldo não olha a faixa. **Medido** (V-3 da [verificação](verificacao-do-levantamento.md)); é parente da pendência da `095` sobre a faixa da reservada. |
| N-4 | **Remanejamento entre cotas antes da ampla** | Três Editais do Cefor (140/2025, 10.5.1; 173/2025, 9.5.1; 90/2026, 11.3) mandam, pelo Decreto nº 12.536/2025, que a vaga de uma submodalidade de PPIQ sem habilitado vá às demais submodalidades e, persistindo a ausência, à ampla. O 33/2026 do IFFluminense (Anexo 7) declara uma ordem completa entre oito cotas da Lei nº 12.711/2012. O conteúdo estruturado só sabe dizer "reverte à linha geral" (I-3): a ordem entre cotas não tem onde ser declarada. |
| N-5 | **A faixa sem continuação, na ampla que recebeu a vaga** | A vaga revertida chega à ampla. Se a fila da ampla também acabou e o Edital não publicou continuação (como no C09 e no 14/2026), a vaga troca um beco por outro. |

### O que falta

| # | O que falta | Consequência hoje |
|---|---|---|
| F-1 | **Um ato próprio de destinação**, separado da apuração, com conferência antes, fundamento e registro | A reversão acontece como efeito de "Emitir a apuração" (I-4). Quem emite não confirma que está cedendo vaga, e quem lê depois só vê o movimento. |
| F-2 | **Um ato que declare a vaga não preenchida**, para o Edital que manda isso ou que não diz nada | A vaga fica "a ocupar" para sempre, e a fase não fecha. O 46/2026 (cursos técnicos) prevê que vagas não ocupadas *"a critério do Campus"* sejam preenchidas por "Edital de vagas não preenchidas"; o corpus tem Editais de vagas remanescentes (77/2026, 78/2026, 158/2024). Sem o fato registrado, o Edital seguinte não tem de onde partir. |
| F-3 | **Um momento a partir do qual a ausência é definitiva** | O achado da `098` já perguntava: o fim das inscrições, o congelamento das relações ou o fim da fila. |
| F-4 | **A lista vazia sem os três atos sem efeito** | Achado 16. |
| F-5 | **Um destino entre cotas** | N-4. |

### O que os Editais do corpus declaram

| Edital | Cláusula | Leitura |
|---|---|---|
| 28/2026 e 149/2024 (pós-graduação, Cefor) | 4.3: *"havendo ausência de candidatos aprovados na reserva … o quantitativo de vagas será destinado para a respectiva vaga de ampla concorrência"* | por esgotamento, à ampla, em cada polo |
| 57/2026 e 35/2026 (aperfeiçoamento e pós, Cefor) | 4.3: *"na hipótese do não preenchimento total das vagas … o quantitativo … será destinado para a respectiva ampla concorrência"*; 57/2026, 4.5: *"não haverá remanejamento de vagas remanescentes entre os cursos"* | por saldo, à ampla; nunca entre Perfis |
| 173/2025 (cadastro de reserva) | 9.5.1: cascata entre subgrupos de PPIQ e, depois, ampla (Decreto nº 12.536/2025); 9.5.6: ausência de aprovados na reserva vai à ampla. Cita a Lei nº 12.990/2014 (9.2) ao lado da Lei nº 15.142/2025 (9.4) | cascata entre cotas, depois à ampla |
| 140/2025 e 90/2026 (tutoria) | 10.5.1 e 11.3: a mesma cascata entre submodalidades de PPIQ, depois à ampla | cascata entre cotas, depois à ampla |
| 46/2026 (técnicos integrados) | base legal na Lei nº 12.711/2012 alterada pela Lei nº 14.723/2023; vagas não ocupadas, esgotadas as listas, *"a critério do Campus"* por Edital de vagas não preenchidas ou listas de outro curso do Campus | não preenchida, com destino posterior fora do Edital |
| 33/2026 (IFFluminense) | Anexo 7, "Redirecionamento das vagas entre cotas": ordem completa entre oito cotas | cascata entre cotas, declarada em anexo |
| Os demais do corpus (FIC 58/2026, 59/2026, 77/2026, 78/2026; chamadas 69/2026, 73/2026, 76/2026; entre outros) | nada sobre a vaga reservada não preenchida | silentes |

**A lei, como o corpus a cita.** Os Editais citam a Lei nº 12.711/2012 (com a Lei nº 14.723/2023 e o
Decreto nº 7.824/2012) para cursos, e a Lei nº 15.142/2025 com o Decreto nº 12.536/2025 para
seleção de pessoal; um deles ainda cita a Lei nº 12.990/2014 ao lado da Lei nº 15.142/2025. Esta spec
**não interpreta lei**: o que o sistema aplica é o que o Edital publicou. Onde o Edital é silente e a
lei teria algo a dizer, nenhum texto escrito no ato a substitui para mover a vaga (D-006).

## O que esta spec cobre, e o que fica fora

**Cobre:**
- a leitura da situação da vaga sem quem a ocupe, dita igual no Centro, na ocupação e na convocação;
- as condições dos dois gatilhos publicados — por esgotamento e por saldo —, cada um com a sua, e os
  impedimentos comuns (resultado provisório, recurso, chamada em curso);
- o ato que destina à ampla a vaga que o Edital manda reverter, com "Confira antes", fundamento,
  quantidade e registro, separado da apuração;
- a limitação dita quando o Edital manda passar antes por outras cotas;
- o Edital silente, sem reversão por padrão;
- a declaração fundamentada de vaga não preenchida, na reserva e na ampla, nunca automática;
- a lista vazia, no marco por pontuação (um gesto) e no sorteio (sem apuração artificial);
- a correção por ato contrário, e o impedimento dito quando há chamada dependente;
- a destinação na página pública da seleção e no relatório do Edital;
- as revisões das specs afetadas: a `016`, a `050`, a `095`, a `098` e a `135`.

**Fica fora:**
- a **passagem entre cotas** em si — a ordem dos destinos intermediários, como se declara e como se
  aplica. Tem spec própria, encaminhada em
  [`doc/encaminhamento-passagem-entre-cotas.md`](../../doc/encaminhamento-passagem-entre-cotas.md)
  (D-008). Aqui entra só a declaração de que ela existe, para que a destinação direta seja recusada;
- o remanejamento entre Perfis: o 57/2026 o proíbe, e a FR-246 da `016` continua;
- o destino da vaga não preenchida **fora** do Edital — Edital de vagas remanescentes, vaga acrescida
  noutro Edital pela `097`: o fato registrado aqui é o ponto de partida, e o ato de lá continua o de lá;
- um documento PDF da destinação (D-013);
- a pendência da `095` sobre a faixa da reservada que conta quem ocupa pela ampla: o corte continua
  como está, e a D-015 só decide quando há saldo reversível;
- o recurso contra o indeferimento da convocação, que a `115` deixou fora: enquanto ele não existir, o
  desfecho excludente é definitivo para esta spec.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A presidência destina a vaga que o Edital manda reverter (Priority: P1)

O Perfil declara reversão. A condição do gatilho publicado está cumprida e nada a impede. A
presidência vê, na ocupação e no Centro, *"1 vaga da PPP sem quem a ocupe. O Edital declara: «As
vagas reservadas … que não forem preenchidas passam para a ampla concorrência»"*, e o ato "Destinar à
ampla concorrência". O "Confira antes" mostra origem, destino, quantidade, a frase publicada, a versão
do Edital e o efeito na ampla. Confirmado, a reserva passa a "0 a ocupar — 1 destinada à ampla em
11/11, por …", e a ampla mostra a apuração obsoleta pelo movimento, com o caminho para emitir a
seguinte e chamar a próxima da fila.

**Why this priority**: é o caso em que o Edital já disse o que fazer, e hoje a vaga só chega à ampla
como efeito da apuração da reservada, sem confirmação — e, por saldo, chega cedo demais (N-6).

**Independent Test**: um Perfil com reversão por saldo, 1 vaga PPP e a condição da D-015 cumprida: o ato produz um registro com fundamento e quantidade, a soma das vagas efetivas
do Perfil não muda, e uma segunda confirmação idêntica não produz outro registro.

**Acceptance Scenarios**:

1. **Given** reversão por saldo e 1 vaga PPP com a condição da D-015 cumprida, **When** a
   presidência abre a ocupação, **Then** a tela diz a situação, a frase publicada e o ato, e nenhum
   outro ato para aquela vaga.
2. **Given** o mesmo estado, **When** a presidência confirma, **Then** fica registrado quem, quando, a
   origem, o destino, a quantidade, o gatilho, a declaração do Edital lida e a versão dela, e a ampla
   mostra a causa da obsolescência.
3. **Given** reversão por saldo e o ocupante da PPP desistiu, com outros dois autodeclarados
   habilitados na ordem da reserva, **When** a apuração seguinte é emitida, **Then** nada é cedido, e a
   tela leva à chamada do autodeclarado seguinte — o oposto do que acontece hoje (V-3), e o que o item
   8.8 do 57/2026 e do 35/2026 manda. Vale nas opções A1 e A2 da D-015; a opção B o inverte.
4. **Given** reversão por esgotamento e uma pessoa da reserva com chamada em curso, **When** a
   presidência abre a ocupação, **Then** o ato não é oferecido, e a tela diz qual chamada o impede.
5. **Given** a apuração da reservada emitida antes da `155`, que já cedeu a vaga, **When** a
   presidência abre a ocupação, **Then** a vaga aparece como já destinada, citando aquele movimento, e
   nenhum ato novo a destina de novo.

---

### User Story 2 — O Edital silente: a vaga não some, e o sistema não decide (Priority: P1)

O caso do C09. O Perfil não declara reversão. A tela diz *"1 vaga da PPP sem quem a ocupe. Este Edital
não declara o que acontece com a vaga reservada não preenchida."*, e oferece dois caminhos
explícitos: retificar o Edital para declarar a reversão, quando a fase admite, ou declarar a vaga não
preenchida com fundamento escrito. Nenhum texto escrito no ato move a vaga.

**Why this priority**: é o caso do achado 02, e o mais comum do corpus.

**Independent Test**: no C09, a vaga PPP sai de "impedida" para um estado final registrado por ato
com fundamento, e nenhum movimento de vaga é gravado sem reversão declarada no Edital.

**Acceptance Scenarios**:

1. **Given** o C09 com o resultado definitivo divulgado, **When** a presidência abre o Centro, **Then**
   a providência da PPP diz que o Edital não declara destinação e mostra os dois caminhos, e não "Pedir
   a faixa seguinte" nem "Destinar à ampla".
2. **Given** o mesmo estado, **When** a presidência declara a vaga não preenchida sem fundamento,
   **Then** o comando recusa e pede o fundamento.
3. **Given** a declaração feita com fundamento, **When** a presidência volta ao Centro, **Then** a fase
   Vagas não tem mais providência para a PPP, e o registro diz quem, quando e por quê.
4. **Given** o fundamento escrito cita uma lei que manda reverter, **When** a presidência procura um
   ato que mova a vaga com esse fundamento, **Then** não há: o caminho é a Retificação.
5. **Given** o Edital retificado para declarar reversão por saldo, **When** a presidência volta à
   ocupação, **Then** a vaga passa ao caso da US1, lida a versão retificada.

---

### User Story 3 — A condição de cada gatilho, com os casos que hoje erram (Priority: P1)

A presidência confia no que a tela diz porque a condição é a do gatilho publicado e os casos de
fronteira estão cobertos: ocupação pela ampla, desistência, eliminação e inabilitação, recurso e
chamada em curso.

**Why this priority**: os três defeitos medidos (V-1 a V-4) são deste grupo, e um deles tira vaga de
cotista (V-3).

**Independent Test**: os cenários abaixo, um por caso, no caminho oficial.

**Acceptance Scenarios**:

1. **Given** por esgotamento e o único autodeclarado ocupa a ampla com aceite registrado, **When** a
   presidência abre a ocupação da PPP, **Then** a destinação é oferecida (hoje não é: V-4).
2. **Given** por esgotamento e o único autodeclarado ocupa a ampla sem aceite registrado — titular da
   apuração ou com chamada sem desfecho —, **When** a presidência abre a ocupação da PPP, **Then** a destinação não é oferecida, e a tela diz
   que a ocupação pela ampla ainda pode mudar.
3. **Given** por esgotamento e todos os autodeclarados desistiram, **When** a apuração seguinte é
   emitida, **Then** a destinação é oferecida (hoje não é: V-1).
4. **Given** por esgotamento e todos os autodeclarados foram eliminados ou inabilitados, sem prazo
   recursal aberto nem recurso pendente, **When** a presidência abre a ocupação, **Then** a destinação é
   oferecida (a inabilitação hoje impede: V-2).
5. **Given** o mesmo, com o prazo recursal da eliminação aberto, **When** a presidência abre a
   ocupação, **Then** a destinação não é oferecida, e a tela diz até quando cabe recurso.
6. **Given** o resultado do marco ainda preliminar, **When** a presidência abre a ocupação, **Then** a
   destinação não é oferecida em nenhum dos dois gatilhos.
7. **Given** por esgotamento, a faixa da reserva sem ninguém, mas autodeclarados fora dela e o Edital
   admitindo continuação, **When** a presidência abre a ocupação, **Then** a destinação não é oferecida,
   e o caminho é a faixa seguinte. **O mesmo por saldo depende da D-015**: nas opções A1 e A2, também
   não é oferecida enquanto a chamada de suplentes estiver aberta.

---

### User Story 4 — O Edital manda passar antes por outras cotas (Priority: P2)

O Perfil declara que a vaga reservada não preenchida passa antes por outras cotas, na ordem do Edital
(o Decreto nº 12.536/2025, no 173/2025). O GPS ainda não representa essa ordem. A tela diz isso, sem
oferecer a destinação direta à ampla nem a declaração de não preenchida, e diz que a ordem entre cotas
é trabalho encaminhado.

**Why this priority**: sem ela, um Perfil desses seria destinado direto à ampla, contra o Edital.

**Independent Test**: um Perfil com a declaração de passagem entre cotas e uma vaga PPI sem quem a
ocupe: nenhum ato de destinação é aceito, e a tela diz a limitação.

**Acceptance Scenarios**:

1. **Given** a declaração de passagem entre cotas, **When** a presidência abre a ocupação, **Then** a
   tela diz que o Edital manda passar por outras cotas antes da ampla e que o GPS ainda não aplica essa
   ordem.
2. **Given** o mesmo, **When** alguém pede a destinação à ampla pelo comando, **Then** o comando recusa,
   com a mesma razão.
3. **Given** um Perfil já publicado com reversão direta e um Edital cujo texto manda a cascata,
   **When** a presidência abre o "Confira antes" da destinação, **Then** a tela lembra que, se o Edital
   manda passar antes por outras cotas, o caminho é retificar a declaração, e não confirmar.

---

### User Story 5 — A lista vazia não pede três atos sem efeito (Priority: P2)

No marco por pontuação, a lista PPP em que ninguém concorre pede hoje ordem, corte e publicação
(achado 16). A presidência registra, num gesto com conferência, que ninguém concorreu; a lista entra na
publicação do resultado do marco junto das outras, como "ninguém concorreu", sem linha de candidato.
No sorteio, a lista reservada sem relação por falta de autodeclarado não precisa de apuração: a
ausência é lida na relação definitiva.

**Why this priority**: tira três passos de todo Edital com cota sem inscrito; o crítico é a US1 a US3.

**Independent Test**: no C09, as confirmações dedicadas à lista PPP caem de três para uma, os registros
normativos de hoje continuam legíveis, e nenhum registro de classificação ou resultado nomeia
candidato.

**Acceptance Scenarios**:

1. **Given** a lista PPP em que ninguém concorre, **When** a presidência abre a ordenação, **Then** a
   providência diz que ninguém concorre e oferece o gesto, com a conferência do que ele registra.
2. **Given** o gesto confirmado, **When** o Publicador publica o resultado do marco, **Then** a lista
   PPP aparece nele como "ninguém concorreu", sem publicação à parte e sem linha de candidato.
3. **Given** um marco por sorteio com a relação da ampla congelada e nenhum autodeclarado PPI nela,
   **When** a presidência abre a ocupação, **Then** a PPI aparece com a destinação disponível pela
   condição do gatilho, sem apuração.
4. **Given** um marco por sorteio com as relações ainda não congeladas, **When** a presidência abre a
   ocupação, **Then** a PPI aparece como "relação não congelada", e não como lista vazia.

---

### User Story 6 — A destinação errada se corrige, e a que não se corrige é dita (Priority: P3)

A presidência destinou a vaga por engano. Enquanto nenhuma chamada depender da destinação, ela pratica
o ato contrário, com motivo, que cita o que desfaz. Se já houver chamada, o pedido é recusado, a tela
diz quais chamadas dependem dela e o que cada uma precisa antes, e o pedido recusado fica na trilha.

**Why this priority**: raro, mas sem ele o erro de um clique só se corrige por Retificação, ou some.

**Independent Test**: destinar, desfazer e conferir que os dois registros existem e as vagas voltaram;
destinar, chamar alguém da ampla, pedir o desfazimento e conferir a recusa com as chamadas nomeadas e o
registro na trilha.

**Acceptance Scenarios**:

1. **Given** uma destinação sem chamada dependente, **When** a presidência a desfaz com motivo,
   **Then** os dois registros ficam, e a origem volta a ter a vaga a ocupar.
2. **Given** uma destinação e uma chamada da ampla para a vaga destinada, **When** a presidência pede o
   desfazimento, **Then** o comando recusa, a tela nomeia a chamada e diz que ela precisa do seu
   desfecho antes, e a trilha registra o pedido, a recusa e as chamadas nomeadas.

---

### User Story 7 — O candidato vê para onde a vaga foi (Priority: P3)

Na página pública da seleção e no relatório do Edital, a destinação aparece com origem, destino,
quantidade e fundamento: *"1 vaga reservada à PPP foi destinada à ampla concorrência em 11/11/2026,
conforme o item 4.3 do Edital (a quantidade não preenchida)."*

**Why this priority**: transparência pedida pelo usuário; depende das US1 e US2.

**Independent Test**: depois de uma destinação e de uma declaração de não preenchida, a página pública
da seleção e o relatório mostram as duas, com os quatro dados, sem documento PDF novo.

**Acceptance Scenarios**:

1. **Given** uma destinação registrada, **When** alguém abre a página pública da seleção sem login,
   **Then** vê origem, destino, quantidade e fundamento, e nenhum nome de candidato.
2. **Given** a destinação desfeita, **When** alguém abre a mesma página, **Then** vê as duas, a segunda
   citando a primeira.

---

### Edge Cases

- **Por saldo com parte da reserva ocupada**: 2 vagas PPP, 1 ocupada e a condição da D-015 cumprida
  para a outra. O ato destina 1, e nunca mais que o saldo.
- **Duas confirmações simultâneas**: um registro só; a segunda é recusada por falta de saldo.
- **Movimento antigo e destinação nova**: a vaga que a apuração já cedeu antes da `155` conta como
  destinada, e o saldo sai das efetivas líquidas dela; nenhum caminho a destina de novo.
- **Retificação do quadro depois da destinação**: a destinação não é reescrita; fica lida contra a
  versão que citou, e a apuração mostra a obsolescência pela causa do quadro retificado, como hoje.
- **Retificação da declaração depois da destinação**: a destinação fica, com a versão que citou; a
  nova declaração vale para o que ainda não foi destinado.
- **Perfis diferentes**: a destinação nunca alcança outro Perfil (FR-246 da `016`).
- **Edital encerrado**: nenhum ato desta spec é oferecido; a vaga que ficou "a ocupar" aparece no
  relatório como tal.
- **Lista em que ninguém concorre porque todos foram eliminados numa Etapa anterior**: não é lista sem
  inscrito (FR-4672 da `135`); o gesto da lista vazia diz "ninguém concorre", e a eliminação, com o
  prazo recursal dela, entra nos impedimentos da destinação.
- **Ator sem permissão**: a recusa é a de qualquer ato da comissão sobre o Processo; a tela não oferece
  o ato a quem não pode praticá-lo, e diz de quem ele é.

## Requirements *(mandatory)*

### Functional Requirements

**A leitura da situação**

- **FR-6300**: O sistema MUST reconhecer, por recorte, a **vaga sem quem a ocupe**: a condição do
  gatilho publicado cumprida (FR-6304 e FR-6305) e nenhum impedimento (FR-6306); sem reversão
  declarada, as mesmas condições da reversão por esgotamento.
- **FR-6301**: Para cada vaga assim, o Centro, a ocupação e a convocação MUST dizer a mesma situação,
  derivada de uma conta só: a quantidade, o recorte, e a destinação que o Edital declara — com a frase
  publicada e a versão —, ou a passagem entre cotas que ele declara, ou que ele não declara nenhuma.
- **FR-6302**: A tela MUST oferecer só os atos que o comando aceitaria naquele estado, e MUST NOT
  oferecer "Pedir a faixa seguinte" onde o Edital não publicou continuação (o que o #477 já faz).
- **FR-6303**: Quando um ato desta spec não é oferecido, a tela MUST dizer a razão — qual impedimento,
  com a data em que ele pode acabar quando houver — e de quem é o próximo passo.

**A condição de cada gatilho e os impedimentos**

- **FR-6304**: Na reversão **por esgotamento**, a condição MUST ser não haver, na ordem vigente da
  reserva, ninguém que ainda possa ocupar a vaga por ela. Ainda pode ocupar quem tem posição, não saiu
  por desfecho excludente, não ocupa pela ampla com aceite registrado e é alcançável — dentro da faixa
  vigente, ou fora dela quando o Edital admite continuação.
- **FR-6305** *(próxima entrega)* *(depende da D-015)*: Na reversão **por saldo**, a condição MUST ser a que a D-015
  fixar, fundamentada nas cláusulas do Edital, e MUST NOT ser a faixa vigente só porque ela existe no
  sistema. Em qualquer opção, a vaga MUST ser de quem ainda pode ocupá-la pela reserva enquanto a
  chamada de suplentes daquela lista estiver aberta, como mandam os itens 8.8 e 8.11 a 8.13 do
  35/2026 e os correspondentes do 57/2026 — salvo a opção B.
- **FR-6306**: Nos dois gatilhos, a destinação MUST ser impedida enquanto: o resultado do marco não
  for definitivo; houver prazo recursal aberto ou recurso pendente sobre o marco, ou sobre a eliminação
  ou a inabilitação de alguém da ordem da reserva; houver chamada em curso para a reserva; alguém da
  reserva ocupar a ampla sem aceite registrado; ou a apuração vigente da reserva estiver
  obsoleta.
- **FR-6307**: As condições da FR-6304 e da FR-6305 MUST continuar distintas: nenhuma leitura MUST
  aplicar a um gatilho a condição do outro.

**O ato de destinação à ampla**

- **FR-6308** *(próxima entrega)*: A reversão declarada pelo Perfil MUST ser aplicada por ato próprio, "Destinar à ampla
  concorrência", praticado por quem pode emitir a apuração do recorte, e MUST NOT ser efeito de nenhum
  outro ato.
- **FR-6309** *(próxima entrega)*: Antes da confirmação, o sistema MUST mostrar origem, destino, quantidade, o gatilho, a
  frase da reversão publicada, a versão do Edital e o efeito na ampla, e MUST lembrar que, se o Edital
  manda passar antes por outras cotas, o caminho é retificar a declaração.
- **FR-6310** *(próxima entrega)*: O ato MUST registrar ator, instante, origem, destino, quantidade, gatilho, a declaração
  do Edital lida e a versão dela, a apuração vigente lida e a correlação.
- **FR-6311** *(próxima entrega)*: A quantidade destinada MUST NOT exceder o saldo; a soma das vagas efetivas por recorte
  do Perfil MUST ser a mesma antes e depois (como a FR-247 da `016`); e a quantidade publicada MUST NOT
  mudar.
- **FR-6312** *(próxima entrega)*: O ato MUST ser recusado, com a razão dita, sem reversão declarada, com a passagem entre
  cotas declarada, com a condição do gatilho não cumprida, com impedimento ou sem saldo.
- **FR-6313** *(próxima entrega)*: Destinada a vaga, a apuração vigente da ampla MUST aparecer obsoleta pela causa do
  movimento posterior (FR-263 da `016`), e o Centro MUST levar à emissão seguinte da ampla.
- **FR-6314** *(próxima entrega)*: Duas confirmações do mesmo ato, simultâneas ou repetidas, MUST produzir um registro só.

**A apuração deixa de mover vaga**

- **FR-6315** *(próxima entrega)*: A emissão da apuração MUST NOT gravar movimento de vaga; a apuração da reserva MUST
  informar a ocupação e, cumprida a condição, que a destinação está disponível.
  *Até o incremento F, que espera a D-015, a emissão continua a mover vaga sob a declaração por saldo,
  como antes da `155`: é a parada da parte que a decisão governa, e não regra adotada (R-010 da
  pesquisa).*
- **FR-6316** *(próxima entrega)*: Os movimentos já gravados pela emissão da apuração MUST continuar legíveis e válidos,
  com a mesma causa, e MUST contar como destinação feita: o saldo MUST sair das efetivas líquidas
  deles, e nenhum ato MUST destinar outra vez a vaga que eles já cederam.

**A passagem entre cotas: a limitação**

- **FR-6317** *(próxima entrega)*: O passo Perfis MUST admitir uma terceira resposta à pergunta da reversão: *"Passa antes
  por outras cotas, na ordem do Edital"*, conteúdo publicado e retificável como as outras duas (FR-249
  e FR-250 da `016`), com frase própria no documento do Edital. Os Editais já publicados MUST
  continuar lidos pela declaração que publicaram; a troca para a terceira resposta MUST ser por
  Retificação.
- **FR-6318** *(próxima entrega)*: Com essa resposta, nenhum ato desta spec MUST mover a vaga, declará-la não preenchida
  ou presumir a ordem entre cotas; a tela MUST dizer que o Edital manda passar por outras cotas antes da ampla e que o GPS
  ainda não aplica essa ordem.
- **FR-6319** *(próxima entrega)*: A passagem entre cotas MUST continuar sem aplicação até a spec própria
  ([encaminhamento](../../doc/encaminhamento-passagem-entre-cotas.md)).

**O Edital silente**

- **FR-6320**: Sem reversão declarada, o sistema MUST NOT destinar a vaga à ampla por nenhum caminho,
  e nenhum texto escrito num ato MUST substituir a declaração publicada para mover a vaga.
- **FR-6321**: Sem reversão declarada, a tela MUST dizer *"Este Edital não declara o que acontece com
  a vaga reservada não preenchida"* e oferecer dois caminhos: a Retificação que declara a reversão,
  quando a fase do Edital a admite, e a declaração de vaga não preenchida.
- **FR-6322** *(nesta entrega, a vaga passa à reversão aplicada pela apuração, pela regra de antes da `155`; o ato próprio, na próxima)*: Retificado o Edital para declarar a reversão, a vaga MUST passar ao caso da destinação
  à ampla, lida a versão retificada.

**A vaga não preenchida**

- **FR-6323**: O sistema MUST permitir declarar a vaga **não preenchida** por ato próprio, com
  fundamento escrito obrigatório, sob as condições e os impedimentos da FR-6300, e MUST NOT fazê-lo por
  padrão, por prazo ou por efeito de outro ato.
- **FR-6324**: A declaração MUST valer para recorte reservado sem reversão declarada e para a linha
  geral sem ninguém que ainda possa ocupá-la, inclusive a que recebeu vaga destinada.
- **FR-6325**: A declaração MUST registrar ator, instante, recorte, quantidade, fundamento e a versão
  do Edital, e MUST NOT exceder o saldo do recorte.
- **FR-6326** *(nesta entrega, na ocupação e no histórico do recorte; o relatório e a página pública, na próxima)*: Declarada, a vaga MUST deixar de contar como "a ocupar" e MUST aparecer como "não
  preenchida" na ocupação, no histórico do recorte, no relatório e na página pública; a quantidade
  publicada MUST continuar a mesma.
- **FR-6327**: Onde a reversão declarada é aplicável, ou onde o Edital manda a passagem entre cotas, a
  declaração MUST ser recusada, dizendo o que o Edital manda.

**A lista vazia**

- **FR-6328** *(próxima entrega)*: No marco por pontuação, a lista em que ninguém concorre MUST poder ser levada, num gesto
  com uma conferência, à ordem vazia e ao corte vazio — os dois registros de hoje, sem perder nenhum.
- **FR-6329** *(próxima entrega)*: Nenhum registro do gesto MUST conter linha de classificação ou de resultado de
  candidato: a ordem e o corte registram que ninguém concorreu, e nada além.
- **FR-6330** *(próxima entrega)*: A lista vazia MUST entrar na publicação do resultado do marco junto das outras listas,
  dita como "ninguém concorreu", e MUST NOT exigir publicação própria.
- **FR-6331** *(próxima entrega)*: A conferência do gesto MUST continuar a dizer que a ordem vazia declara que ninguém
  concorreu (FR-4672 da `135`).
- **FR-6332** *(próxima entrega)*: No sorteio, a lista reservada sem relação por falta de autodeclarado MUST dispensar a
  apuração, desde que a ausência esteja comprovada na relação definitiva pertinente — a relação da
  ampla congelada no marco, sem nenhuma inscrição daquela Modalidade.
- **FR-6333** *(próxima entrega)*: A ausência de registro MUST NOT ser lida como lista vazia: relação não congelada,
  inscrições ainda não encerradas ou dado que falta MUST aparecer como o que são, e o ato MUST NOT ser
  oferecido.

**A correção**

- **FR-6334** *(nesta entrega, só a declaração de não preenchida; a destinação, na próxima)*: A destinação e a declaração de não preenchida MUST poder ser desfeitas por ato contrário,
  com motivo, que cita o ato que desfaz, enquanto nenhuma chamada depender delas.
- **FR-6335** *(nesta entrega, para a declaração de não preenchida)* *(redação de 12/11/2026, pelo pedido do usuário na revisão do #495)*: Com chamada
  dependente, a tela MUST mostrar o impedimento no lugar da ação de desfazer — nomeando cada chamada
  e o que ela precisa antes (o desfecho dela) — e MUST NOT oferecer a ação. O comando MUST recusar o
  desfazimento pedido mesmo assim, por qualquer caminho, e a trilha MUST registrar o pedido, a
  recusa e as chamadas nomeadas.

  > **Redação anterior, preservada:** "Com chamada dependente, o desfazimento MUST ser recusado; a
  > tela MUST nomear cada chamada e dizer o que ela precisa antes (o desfecho dela); e a trilha MUST
  > registrar o pedido, a recusa e as chamadas nomeadas." A primeira implementação a lia como
  > obrigando a tela a deixar a ação disponível, para que a recusa fosse registrada; o usuário
  > recusou essa leitura: ação oferecida só para ser negada contraria a FR-6302.
- **FR-6336** *(nesta entrega, para a declaração de não preenchida)*: O ato e o desfazimento MUST continuar ambos legíveis; nada MUST ser apagado ou
  reescrito.

**A publicidade**

- **FR-6337** *(próxima entrega)*: A página pública da seleção MUST mostrar cada destinação e cada declaração de não
  preenchida, com origem, destino (ou "não preenchida"), quantidade e fundamento, e MUST NOT mostrar
  nome nem protocolo de candidato.
- **FR-6338** *(próxima entrega)*: O relatório do Edital MUST mostrar os mesmos dados, e os desfazimentos citando o que
  desfazem.
- **FR-6339** *(próxima entrega)*: Esta entrega MUST NOT exigir documento PDF novo.
- **FR-6340** *(próxima entrega)*: A chamada de quem ocupa uma vaga destinada à ampla MUST citar a destinação no
  fundamento.

**Registro, permissão e equivalência**

- **FR-6341**: Todo ato desta spec MUST exigir a mesma permissão e o mesmo escopo da emissão da
  apuração, MUST ser negado por padrão a quem não os tem, e MUST entrar na trilha com correlação.
- **FR-6342**: Todo ato desta spec MUST ser reproduzível: relido depois, MUST devolver a quantidade, a
  condição e a declaração que leu, e não as de hoje.
- **FR-6343** *(próxima entrega)*: A prévia da classificação e a do sorteio (`095`, `098`) MUST fazer a conta das FR-6304 e
  FR-6305 e mostrar o que a destinação faria, e a equivalência delas com o caminho oficial MUST
  continuar verificada.
- **FR-6344**: As telas e os registros desta spec MUST NOT dizer que alguém foi convocado, aceitou ou
  se matriculou (como a FR-258 da `016`).

### Requisitos de experiência

- **UX-600**: A frase da situação MUST nomear a lista, a quantidade e o que o Edital declara, em
  palavras, sem código de espécie nem identificador.
- **UX-601** *(nesta entrega, a conferência da declaração de não preenchida e do desfazimento dela)*: O "Confira antes" da destinação, da declaração de não preenchida e do gesto da lista
  vazia MUST seguir o da emissão (#467), com o efeito dito por extenso.
- **UX-602**: No Centro, a providência da vaga sem quem a ocupe MUST ter um ato por caminho, e a
  "impedida" do #477 MUST dar lugar ao impedimento nomeado ou ao caminho disponível.
- **UX-603** *(próxima entrega)*: A limitação da passagem entre cotas MUST ser dita como limite do GPS, e não do Edital
  nem da comissão.

### Key Entities

- **Destinação de vaga**: ato append-only que leva quantidade de um recorte reservado à linha geral do
  mesmo Perfil, com gatilho, declaração e versão do Edital lidas, apuração lida, ator e instante. O
  movimento de vaga da `016` é o candidato natural para guardá-la; a escolha é do plano.
- **Declaração de vaga não preenchida**: ato append-only que tira quantidade do "a ocupar" de um
  recorte sem a mover, com fundamento escrito, ator e instante.
- **Desfazimento**: ato contrário que cita o que desfaz.
- **Pedido de desfazimento recusado**: entrada de trilha com as chamadas dependentes nomeadas.
- **Declaração da passagem entre cotas**: a terceira resposta à pergunta da reversão no Perfil.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2100**: No C09, a vaga PPP sai de "Ocupar a vaga — impedida" para um estado final registrado
  com **uma** confirmação, e o Centro não mostra mais providência na fase Vagas para aquela lista.
- **SC-2101**: Em nenhum dos 15 cenários de treinamento a tela oferece, para vaga reservada, um ato
  que o comando recusa.
- **SC-2102**: Toda destinação e toda declaração de não preenchida têm fundamento, quantidade, ator,
  instante e versão do Edital no registro: 100%, conferido por teste.
- **SC-2103**: Nenhum movimento de vaga nem declaração de não preenchida nasce sem confirmação própria:
  zero, conferido varrendo os caminhos de gravação.
- **SC-2104** *(próxima entrega)*: Os cenários V-1 a V-4 da [verificação](verificacao-do-levantamento.md) passam a dar o
  resultado da US3: destinação oferecida em V-1, V-2 (sem recurso) e V-4 (com aceite); e os cenários
  S-1 a S-4 dão o resultado da opção da D-015 escolhida.
- **SC-2105** *(próxima entrega)*: Num Edital com cota sem inscrito no marco por pontuação, as confirmações dedicadas à
  lista vazia caem de três para uma, e nenhuma linha de candidato é registrada para ela.
- **SC-2106** *(próxima entrega)*: A soma das vagas efetivas por recorte de um Perfil é a mesma antes e depois de toda
  destinação e todo desfazimento.
- **SC-2107** *(próxima entrega)*: Num Perfil com a passagem entre cotas declarada, zero atos de destinação aceitos.
- **SC-2108** *(a página pública, na próxima entrega)*: Num roteiro com a presidência de treinamento, a pessoa responde corretamente, sem
  ajuda, o que aconteceu com a vaga PPP do C09 e por quê, lendo só a ocupação; e um leitor sem login
  diz, pela página pública, para onde a vaga foi.

## Assumptions

- O ato é da presidência ou de quem pode emitir a apuração do recorte; não há papel novo.
- A Retificação que declara a reversão já é admitida como acréscimo pelo catálogo; se a fase do Edital
  a impedir depois do resultado, a tela diz isso, e o caminho que sobra é a declaração de não
  preenchida.
- O recurso contra o indeferimento da convocação não existe (`115`); quando existir, o prazo dele entra
  nos impedimentos da FR-6306.
- O C09 é o cenário de referência; o plano acrescenta à `134` um cenário com reversão declarada, um de
  sorteio com reserva vazia e um com a passagem entre cotas declarada, se não houver.
- O estado de partida é o do #477; nada aqui o refaz.

## Compatibilidade com regras anteriores

As revisões abaixo foram feitas nas próprias specs, com a redação anterior preservada, e vigoram com a
implementação desta. **Nesta entrega vigoram só as que não dependem do adiado**; as marcadas
*(próxima entrega)* vigoram com a entrega que as implementa, e até lá a regra anterior continua (ver
[Esta entrega](#esta-entrega)).

| Regra | O que acontece |
|---|---|
| FR-245, FR-246 e FR-251 da `016` | continuam |
| FR-248 da `016` (o registro da reversão) | *(próxima entrega)* **revista**: a reversão é ato próprio, com fundamento (FR-6308, FR-6310) |
| FR-249 da `016` (as espécies) | *(próxima entrega)* **revista**: a terceira resposta, a passagem entre cotas, sem aplicação (FR-6317) |
| A emissão da apuração que move vaga | *(próxima entrega)* deixa de mover (FR-6315); os movimentos gravados ficam (FR-6316) |
| FR-885 da `050` (o desfecho não move vaga) | *(próxima entrega)* **revista**: a tela leva à destinação, e não à emissão na ocupação |
| FR-270 da `019` | continua |
| FR-2327 e FR-2328 da `095`, e a pendência sobre "há quem ocupar" | *(próxima entrega)* **revistas** e **respondida**: a prévia mostra o que a destinação faria, com as condições das FR-6304 e FR-6305 |
| FR-2507 da `098` e o achado da reservada vazia | *(próxima entrega)* **revista** e **respondido** (FR-6332, FR-6333) |
| FR-4671 e FR-4672 da `135` | *(próxima entrega)* **revistas**: a providência da lista vazia leva ao gesto (FR-6328) |
| FR-4678 da `135` | *(só na branch preservada)* a revisão proposta em 12/11, na implementação, ficou com a publicação conjunta em `claude/155-destinacao-completa`, pendente da revisão do usuário; a redação da `135` continua a da `main` |
| FR-4205 da `128` | continua: a ordem vazia é registrada — no gesto, na próxima entrega |
| A recusa da relação vazia no sorteio | continua |
| A pendência da `095` sobre a faixa da reservada | continua aberta (fora) |

## Decisões

### D-001 — Nenhum caminho move vaga sem ato próprio

*Da orientação do usuário, 11/11/2026: "não adote reversão automática".*

Todo efeito desta spec sobre a quantidade de um recorte — destinar, declarar não preenchida, desfazer
— nasce de um ato que alguém confirma depois de ver o efeito. O gatilho por estado (a vaga reverte
sozinha quando a lista esgota) é a "reversão automática" que a orientação exclui. A D-005 estende a
regra ao caminho antigo, o da apuração.

### D-002 — O sistema aplica o que o Edital declara, e não infere

Herdada da decisão da `016` de que ausência de declaração não move. A destinação à ampla só existe
onde o Perfil publicado a declara, e a condição é a da espécie declarada. A lei citada pelo Edital
fundamenta a cota e não a calcula, como a `016` já fixou para o percentual.

### D-003 — A vaga não preenchida é fato registrado, e não zero

A vaga que ninguém ocupa e que não vai a lugar nenhum precisa existir como registro: é dela que parte
o Edital de vagas remanescentes, e é ela que o relatório e a página pública mostram. Por isso a
declaração é ato com fundamento, e a quantidade publicada não muda.

### D-004 — Uma conta só para as três telas

A situação da vaga sem quem a ocupe é derivada num lugar e lida pelo Centro, pela ocupação e pela
convocação, como o #477 fez para a vaga reaberta. Duas contas divergiriam na primeira regra nova.

### D-005 — A destinação é ato separado da apuração

*Decisão do usuário, 11/11/2026 (primeira pergunta, opção a).* *"A apuração informa a ocupação; a
destinação exige ato explícito, com «Confira antes», fundamento e quantidade. Preserve os atos
anteriores e impeça contabilização duplicada."* Os movimentos que a apuração gravou antes da `155`
continuam válidos e contam como destinação feita (FR-6316).

### D-006 — No Edital silente, nenhuma reversão por padrão

*Decisão do usuário, 11/11/2026 (segunda pergunta, opção a).* Os caminhos são a Retificação, quando
cabível, e a declaração fundamentada de vaga não preenchida. *"Texto livre não pode substituir a
autorização normativa para mover a vaga."*


*Reafirmada pelo usuário em 11/11/2026, numa segunda mensagem em que ele pediu que não se aplicasse aprovação geral às recomendações da spec:* *"Nos demais pontos, mantenha as respostas anteriores, inclusive que fundamento escrito não substitui autorização normativa para reverter."*

### D-007 — Esgotamento é ninguém mais que possa ocupar pela reserva

*Decisão do usuário, 11/11/2026 (terceira pergunta).* Conta quem ainda pode ocupar pela lista
reservada; a pendência da `095` sobre quem ocupa pela ampla é decidida aqui, com cenários para
ocupação pela ampla, desistência e eliminação. *"Situações ainda reversíveis por recurso ou chamadas
pendentes não devem produzir esgotamento definitivo."* A inabilitação (V-2) é tratada como eliminação.


*Reafirmada pelo usuário em 11/11/2026, numa segunda mensagem em que ele pediu que não se aplicasse aprovação geral às recomendações da spec:* *"Incluir nesta entrega o caso de quem ocupa pela ampla e a pendência da 095, com os respectivos cenários. Recursos e chamadas pendentes precisam ser considerados antes de afirmar esgotamento."*

### D-008 — A passagem entre cotas tem spec própria, e a 155 mostra a limitação

*Decisão do usuário, 11/11/2026 (quarta pergunta).* A `155` não oferece destinação direta à ampla onde
o Edital exige destinos intermediários. O trabalho fica encaminhado em
[`doc/encaminhamento-passagem-entre-cotas.md`](../../doc/encaminhamento-passagem-entre-cotas.md). Como a
tela fica sabendo que o Edital os exige é a D-016.


*Reafirmada pelo usuário em 11/11/2026, numa segunda mensagem em que ele pediu que não se aplicasse aprovação geral às recomendações da spec:* *"Passagem entre cotas fica em spec própria, já encaminhada. Enquanto não estiver representada, impedir reversão direta à ampla quando o Edital exigir destinos intermediários."*

### D-009 — Cada gatilho com a sua condição, e impedimentos comuns

*Decisão do usuário, 11/11/2026 (quinta pergunta), com a correção dele:* a `016` distingue esgotamento
de saldo, e exigir lista esgotada para os dois mudaria a regra. Por esgotamento, ausência de pessoas
ainda elegíveis (FR-6304); por saldo, a condição própria (FR-6305, lida pela D-015). Os impedimentos —
resultado provisório, recurso, chamada em curso — são comuns (FR-6306), sem fundir os gatilhos.


*Reafirmada pelo usuário em 11/11/2026, numa segunda mensagem em que ele pediu que não se aplicasse aprovação geral às recomendações da spec:* *"Preservar a diferença entre reversão por saldo e por esgotamento. «Ninguém mais pode ser chamado» não pode virar condição universal das duas modalidades."* É contra esta frase que a D-015 precisa ser conferida.

### D-010 — A lista vazia num gesto, sem candidato fabricado

*Decisão do usuário, 11/11/2026 (sexta pergunta, opção a).* Um gesto com conferência, os registros
necessários preservados, a lista na publicação conjunta, e nenhuma classificação ou resultado de
candidato inexistente.

### D-011 — Sorteio sem concorrente dispensa apuração, com ausência comprovada

*Decisão do usuário, 11/11/2026 (sétima pergunta, opção a).* *"Ausência de registro não significa
lista vazia."* A prova é a relação definitiva pertinente (FR-6332).


*Reafirmada pelo usuário em 11/11/2026, numa segunda mensagem em que ele pediu que não se aplicasse aprovação geral às recomendações da spec:* *"Dispensar apuração artificial somente quando a ausência de concorrentes estiver comprovada na relação definitiva pertinente. Ausência de registro não significa lista vazia."*

### D-012 — Correção por ato contrário, e o impedimento dito

*Decisão do usuário, 11/11/2026 (oitava pergunta, opção a).* Com chamada dependente, nada se desfaz
em silêncio: a tela explicita o impedimento e a trilha registra o tratamento que os atos dependentes
pedem (FR-6335).

### D-013 — A destinação é pública, sem PDF novo

*Decisão do usuário, 11/11/2026 (nona pergunta, com a página pública incluída).* Página pública da
seleção e relatório, com origem, destino, quantidade e fundamento.


*Reafirmada pelo usuário em 11/11/2026, numa segunda mensagem em que ele pediu que não se aplicasse aprovação geral às recomendações da spec:* *"Mostrar a destinação também na página pública da seleção, com origem, destino, quantidade e fundamento, sem exigir PDF novo."*

### D-014 — A ampla também esgotada admite a declaração de não preenchida

*Decisão do usuário, 11/11/2026 (décima pergunta, opção a).* Sob as mesmas verificações, nunca
automaticamente.

### D-015 — Quando há saldo reversível *(em aberto: a escolha é do usuário)*

**Estado.** A primeira leitura desta spec — *"o saldo é o que a faixa da reserva não preenche"* — foi
devolvida pelo usuário em 11/11/2026: *"O teste comprova o comportamento atual; sozinho, não demonstra
qual destinação o Edital autoriza. […] Não transforme a faixa em critério normativo universal apenas
porque ela existe no sistema."* Ele pediu o confronto com as cláusulas publicadas do 57/2026 e do
35/2026, que declaram reversão por saldo. O confronto está abaixo, e **não sustenta a faixa**. Os
cenários reproduzíveis estão na [verificação](verificacao-do-levantamento.md), S-1 a S-4.

**As cláusulas.** Os dois Editais têm a mesma redação; a numeração do 57/2026 vem primeiro, a do
35/2026 entre parênteses.

| Pergunta | O que os Editais dizem | Leitura |
|---|---|---|
| Quando há saldo reversível | 4.3 (4.3): *"Na hipótese do não preenchimento total das vagas destinadas às ações afirmativas (PPI e PcD), o quantitativo de vagas será destinado para a respectiva ampla concorrência."* | O gatilho é o **não preenchimento**, e não a ausência de aprovados (que é a redação do 28/2026). O texto não diz quando o não preenchimento se apura. |
| Como a vaga se preenche antes disso | 8.3 (8.3): indeferido o sorteado, *"haverá a análise da documentação do próximo candidato classificado, respeitando-se a ordem do sorteio, até que se preencha o número total de vagas"*. 8.6 (8.6): sem deferimento, *"a vaga será disponibilizada para o próximo candidato habilitado"*. | O preenchimento percorre a **ordem**, um a um, até as vagas. Nenhuma das duas cláusulas para numa faixa. |
| Desistência com candidatos ainda disponíveis | 8.8 (8.8): *"Caso um candidato sorteado em vaga reservada desista de realizar o curso, a vaga será preenchida pelo candidato autodeclarado sorteado e classificado imediatamente após este"*. 8.12 (8.11): *"haverá chamada de suplentes dos próximos candidatos habilitados, conforme a ordem de classificação do sorteio"*. | A vaga reaberta é do **autodeclarado seguinte**. Reverter nesse momento contraria o 8.8 — é o que o sistema faz hoje (V-3). |
| Habilitados dentro e fora da faixa vigente | 8.13 (8.12): *"haverá a análise dos documentos de até 20 (vinte) [15 (quinze), no 35] suplentes para chamada imediata"*. 8.14.1 (8.13.1): *"A chamada de suplentes será realizada conforme o interesse da administração, levando em consideração a necessidade e disponibilidade de vagas."* 10.2 (10.2): a administração *"poderá"* chamar os indeferidos para regularizar. | Os 20 (15) são **capacidade de análise para a chamada imediata**, e não limite de quem pode ocupar: quem está além deles continua na ordem, e a chamada de suplentes os alcança. O que encerra a chamada é decisão da administração, e não a faixa. |

**O que o confronto sustenta.** A faixa vigente não tem apoio no texto. O que distingue o saldo do
esgotamento, nestes dois Editais, é o **motivo** do não preenchimento: a vaga pode deixar de ser
preenchida porque a ordem da reserva acabou (que é também o esgotamento), ou porque a administração
encerrou a chamada de suplentes daquela lista, com gente ainda na ordem (8.14.1). Só o saldo admite o
segundo motivo. O esgotamento do 28/2026 (*"havendo ausência de candidatos aprovados na reserva"*) não
o admite: enquanto houver aprovado, não há ausência.

**As opções.**

| Opção | Saldo reversível quando | Após desistência com autodeclarado disponível | Distingue de esgotamento? | Fundamento |
|---|---|---|---|---|
| **A2 (recomendada)** | a ordem da reserva não tem mais quem possa ocupar (FR-6304), **ou** a chamada de suplentes daquela lista foi encerrada por ato próprio, com fundamento no item do Edital que dá a decisão à administração | o autodeclarado seguinte é chamado; nada é cedido enquanto a chamada estiver aberta | sim, pelo segundo motivo | 4.3, 8.3, 8.6, 8.8, 8.12 a 8.14.1 do 57/2026 e os correspondentes do 35/2026 |
| A1 | só quando a ordem da reserva não tem mais quem possa ocupar | o mesmo | não, nestes Editais: as condições coincidem, e a diferença fica só na declaração | 4.3, 8.3, 8.6, 8.8, 8.12 |
| B | como a `016` faz hoje: a cada apuração, a vaga não ocupada naquele momento | a vaga vai à ampla (V-3) | sim | a definição da `016` (*"ainda que a lista tenha gente"*); **contraria o 8.8** |
| C | a primeira leitura desta spec: ninguém da faixa vigente pode ocupar | o autodeclarado da faixa é chamado; o de fora dela, não | sim, pela faixa | nenhum: as cláusulas não falam de faixa |

**Um exemplo, o mesmo para as quatro.** Um Perfil com reversão por saldo, como o 57/2026, e 2 vagas
na PPI. A ordem sorteada da PPI tem quatro autodeclarados habilitados: A e B nas vagas; C entre os
suplentes analisados para chamada imediata (8.13), dentro da faixa vigente; D depois deles, fora da
faixa. A desiste.

| Opção | Depois da desistência de A | Se C também desistir |
|---|---|---|
| **A2** | C é chamado (8.8); nada vai à ampla | D é chamado pela chamada de suplentes (8.14.1). A vaga só vai à ampla quando a ordem acabar, **ou** quando a administração encerrar a chamada de suplentes da PPI por ato próprio, citando o item |
| A1 | C é chamado; nada vai à ampla | D é chamado. A vaga só vai à ampla quando a ordem acabar; a administração não tem como encerrar a chamada antes disso |
| B | a vaga vai à ampla na apuração seguinte, e C nunca é chamado | — |
| C | C é chamado, porque está na faixa | a vaga vai à ampla, e D, que a ordem alcançaria, não é chamado |

**Recomendação: A2.** É a única que guarda a diferença entre as duas espécies com apoio no texto. O
encerramento da chamada de suplentes seria um ato a mais, com "Confira antes", fundamento — o item do
Edital — e registro, e os impedimentos da FR-6306 continuariam valendo. Com A1, a FR-6305 passa a
remeter à FR-6304; com B, a US1.3, a US3.7 e a medição V-3 ficam como hoje; com C, a FR-6305 volta à
redação da primeira leitura.

**Os requisitos que sustentam o resultado esperado** (A1 ou A2): FR-6304 (quem ainda pode ocupar),
FR-6306 (a chamada em curso impede), FR-6307 (as espécies não se fundem), FR-6308 a FR-6310 (o ato
com fundamento) e, só na A2, o ato de encerramento da chamada de suplentes, que ganha requisito
próprio quando a opção for escolhida.

### D-016 — O Edital declara a passagem entre cotas como terceira resposta

*Proposta desta spec, aprovada pelo usuário em 11/11/2026:* *"D-016 aprovada: inclua a declaração
«Passa antes por outras cotas, na ordem do Edital». Ela deve impedir a reversão direta à ampla e
explicar a limitação atual. Não executa movimentos nem presume a ordem entre cotas. Preserve a leitura
dos Editais já publicados; alterações posteriores seguem por Retificação."*

Para recusar a reversão direta onde o Edital exige destinos intermediários, a tela precisa saber que
ele os exige, e o único lugar confiável é o conteúdo publicado. Ler o texto livre do Edital, ou o
fundamento normativo da Modalidade, seria casar nome por escrito, que a `016` e a `025` recusaram. A
terceira resposta entra na pergunta que já existe (FR-6317), sem campo novo e sem a ordem dos destinos,
que é da spec própria. Custo aceito: a frase no documento do Edital e a entrada no catálogo de
Retificação, herdadas das outras duas respostas.

## Achados fora do escopo (registro)

- **Um Edital do corpus cita a Lei nº 12.990/2014 ao lado da Lei nº 15.142/2025**; se a citação ainda é
  a correta é questão do Edital, não do sistema.
- **A faixa da reservada que conta quem ocupa pela ampla** (pendência da `095`) continua aberta. A
  D-015, em qualquer opção, não muda o tamanho da faixa.
