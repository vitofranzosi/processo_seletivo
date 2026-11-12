# Feature Specification: Destinação da vaga reservada sem ocupante

**Feature Branch**: `claude/elegant-robinson-e66ed2`, sobre a `main` em `ef568113` (depois do #477)

**Created**: 2026-11-11

**Status**: Draft — **a regra não fecha sem as respostas do usuário** às dez perguntas da seção
*Perguntas ao usuário*. Os requisitos que dependem de uma delas dizem qual.

**Input**: *"Escrever a spec para a destinação da vaga de cota sem concorrente. Não adote reversão
automática nem declare a vaga não preenchida por padrão. Levante o que o sistema já permite e proponha
uma spec para aplicar a destinação prevista no Edital, com fundamento e registro explícitos. Traga os
casos que exigem minha decisão antes de fechar a regra."* A orientação entre aspas é do usuário,
literal; o restante do pedido veio da sessão que coordena os achados do estudo.

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de seis mil e trezentos a seis mil trezentos e quarenta e nove;
> - os critérios de dois mil e cem a dois mil cento e dezenove;
> - os requisitos de experiência de seiscentos a seiscentos e dezenove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`; as perguntas ao usuário são
> `P-1` a `P-10`, e quando respondidas viram decisões numeradas a partir da última.
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
| I-8 | **Vaga acrescida e o desfazimento** | `097` | Vaga que chega de fora do Edital entra por ato com motivo, e se corrige pelo ato contrário, que cita o que desfaz. É o modelo de correção sem apagar que esta spec reaproveita (P-8). |
| I-9 | **A ordem de universo vazio é ato** | FR-4205 da `128`; `135` | No marco por pontuação, a ordem da lista sem inscrito se emite e declara que ninguém concorreu; a `135` decidiu mantê-la como providência, e a providência diz que ninguém concorre (FR-4671 e FR-4672 da `135`). Depois dela vêm o corte e a publicação do resultado, e só então a apuração. |
| I-10 | **A tela não sugere o ato que o comando recusa** | #477 | Sem continuação publicada, o Centro diz "Ocupar a vaga — impedida" e a ocupação mostra a razão no lugar do botão. |

### Declarado pelo Edital e não aplicado

| # | O caso | Por quê |
|---|---|---|
| N-1 | **Sorteio com lista reservada vazia, reversão declarada** | A relação vazia é recusada (*"não existe universo a comprometer"*), e sem relação não há corte nem apuração. Como o movimento só nasce na apuração (I-4), **nenhuma espécie de reversão chega a ser consultada** — nem a por saldo. É o achado registrado na `098`, [`doc/achado-reservada-vazia-nao-reverte.md`](../../doc/achado-reservada-vazia-nao-reverte.md), que esperava decisão do usuário. |
| N-2 | **Por esgotamento, com autodeclarados que ocupam pela ampla** | "Há quem ocupar" conta toda posição da ordem, inclusive a de quem já ocupa pela ampla e nunca ocupará a reserva. Uma reservada assim nunca esgota. É a pendência da `095` ("há quem ocupar conta quem ocupa pela ampla") e o Q4 do estudo do Edital 35. |
| N-3 | **Por esgotamento, depois de desistência ou indeferimento de todos** | Pela leitura de `reversao.ha_quem_ocupar`, quem saiu por desfecho continua com posição na ordem, e por isso conta como "quem ocupar" enquanto as ocupadas caem. A reserva em que todos desistiram não esgota. **A verificar por teste no plano**: o estudo não exercitou este caminho. |
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
lei teria algo a dizer, quem decide é a comissão, com fundamento — ou o usuário, nesta spec (P-2).

## Perguntas ao usuário

As dez perguntas abaixo decidem a regra. Cada uma diz as opções, o custo de cada uma e a recomendação
desta spec, que **não está adotada**. Os requisitos que dependem de uma delas estão marcados.

### P-1 — A reversão que nasce dentro da apuração (I-4) continua?

O pedido diz *"não adote reversão automática"*. A de hoje não é automática no sentido estrito — nasce
de um ato de quem emite a apuração —, mas o ato não diz que vai ceder vaga, e quem o pratica não
confirma a cessão.

| Opção | O que acontece | Custo |
|---|---|---|
| **(a)** A apuração deixa de mover vaga; a destinação é sempre o ato desta spec | Uma regra só para os dois casos (lista que apura e lista vazia). A apuração da reservada passa a dizer "1 a ocupar — destinação disponível", e a ampla só muda quando alguém pratica a destinação. | Muda um comportamento mergeado da `016`, com emenda registrada; Editais em andamento que já reverteram ficam como estão (nada se reescreve). |
| (b) A apuração continua movendo; o ato novo só existe onde a apuração não roda | Menor mudança. | Duas portas para o mesmo efeito, uma confirmada e outra não. |
| (c) A apuração continua movendo, mas o "Confira antes" da emissão passa a dizer que vai ceder vaga | Sem ato novo para o caso que já funciona. | Não resolve a lista que não apura (N-1). |

**Recomendação: (a).** É a leitura direta da orientação, e a `050` já tirou o movimento do desfecho
pelo mesmo motivo (I-5).

### P-2 — O Edital que não declara destinação nenhuma

C09 e a maior parte do corpus. A orientação exclui declarar a vaga não preenchida **por padrão**.

| Opção | O que a tela oferece | Custo |
|---|---|---|
| **(a)** Dois caminhos, ambos explícitos: retificar o Edital para declarar a reversão (já admitido como acréscimo — `vacancyReversion` é retificável) e então destinar; ou declarar a vaga não preenchida, com fundamento escrito | O sistema nunca reverte sem declaração publicada; a comissão escolhe e responde pela escolha. | A Retificação depois do resultado precisa ser admitida pela fase do Edital; o plano confere. |
| (b) Também admitir a reversão à ampla sem Retificação, com o fundamento legal citado pela comissão no próprio ato | Mais rápido. | O sistema passa a aplicar destinação que o Edital publicado não tem, por fundamento externo declarado — contraria a decisão da `016` de que ausência não move. |
| (c) Nenhum ato; a situação é dita e a vaga fica aberta até o encerramento do Edital | Nada novo. | É o beco de hoje, com texto melhor. |

**Recomendação: (a).**

### P-3 — Quem conta como "há quem ocupar" na reversão por esgotamento

Três situações em que a lista tem inscritos e ninguém mais pode ocupar a vaga reservada:

1. todos **eliminados** — sem posição na ordem (hoje, pela leitura do código: esgota);
2. todos **saíram por desfecho** — desistência, não atendimento, indeferimento (hoje, pela leitura do
   código: não esgota; N-3);
3. todos **ocupam pela ampla** (hoje: não esgota; N-2).

| Opção | Leitura |
|---|---|
| **(a)** Conta só quem ainda pode ser chamado para a reserva: com posição, sem desfecho excludente e sem ocupar pela ampla | Os três casos esgotam. Responde também a pendência da `095` sobre a concomitância. |
| (b) Como hoje | Os casos 2 e 3 nunca esgotam. |
| (c) (a) para os casos 1 e 2, e o 3 fica para a decisão da `095` | Separa a concomitância, que tem estudo próprio. |

**Recomendação: (a)**, se o usuário aceitar decidir aqui a pendência da `095`; senão, (c).

### P-4 — Remanejamento entre cotas (N-4)

| Opção | O que muda | Custo |
|---|---|---|
| **(a)** Fora desta spec; registrado como achado. Edital com cascata no texto é tratado como silente para a parte da cascata (P-2) | Nada no conteúdo publicado. | Os três Editais do Cefor do corpus que a declaram não ganham a cascata. |
| (b) Nesta spec: o Perfil passa a declarar, por Modalidade, a ordem dos destinos antes da ampla | Atende o Decreto nº 12.536/2025 e a Lei nº 12.711/2012 como os Editais os escrevem. | Campo normativo novo: elevação de versão canônica, PDF, catálogo de Retificação, prévia da `095`/`098`. É o dobro desta spec. |
| (c) Nesta spec, sem campo novo: a comissão escolhe, no ato, a Modalidade de destino, citando o item do Edital | Rápido. | O sistema aplica destino que o conteúdo estruturado não declara. |

**Recomendação: (a)**, com spec própria para (b) quando houver Edital real que a use no GPS.

### P-5 — A partir de quando a destinação é oferecida

| Opção | Momento |
|---|---|
| **(a)** Quando o resultado do marco é definitivo e a ordem vigente da reservada não tem ninguém que ainda possa ser chamado (pela leitura da P-3); para o sorteio, quando as relações do marco estão congeladas e a da reservada não existe por falta de inscrito | O primeiro momento em que a ausência não muda mais por recurso. |
| (b) Só depois do fim do prazo de convocação da ampla | Mais tarde; protege contra recurso tardio. |
| (c) A qualquer momento depois do fim das inscrições, a critério da comissão | Mais cedo; arrisca destinar vaga que um recurso devolveria à cota. |

**Recomendação: (a).** Em todos os casos o ato é explícito: o momento só decide quando ele aparece.

### P-6 — A lista vazia no marco por pontuação: os três atos (achado 16)

A `135` decidiu que a ordem vazia é ato normativo e continua providência.

| Opção | O que muda | Custo |
|---|---|---|
| **(a)** Um gesto só, "Registrar que ninguém concorreu por esta lista", que pratica a ordem vazia e o corte vazio na mesma confirmação, e leva a lista à próxima publicação do resultado do marco junto das outras | Os três registros continuam existindo; o operador confirma uma vez, e o Publicador não publica um resultado só para a lista vazia. | O plano confere se a publicação do resultado admite várias listas num ato. |
| (b) Um ato novo, "ninguém concorreu", que substitui ordem, corte e resultado | Um registro em vez de três. | Muda a decisão da `135` e todas as leituras que esperam ordem vigente. |
| (c) Como hoje | Nada. | O achado 16 continua. |

**Recomendação: (a).**

### P-7 — A lista reservada vazia no sorteio (N-1)

| Opção | O que muda |
|---|---|
| **(a)** A destinação lê a ausência de relação diretamente — não precisa de apuração (decorre da P-1 (a)) | Nada no sorteio. A relação vazia continua recusada, e o "Não se aplica" da `126` continua. |
| (b) A relação vazia passa a ser publicável, e a lista segue o caminho comum até a apuração | Responde a primeira pergunta do achado da `098`. Mexe no sorteio e na prévia. |
| (c) Uma apuração de lista sem ordem ("0 de 1") | Responde a segunda pergunta do achado da `098`. |

**Recomendação: (a).** Se a P-1 for (b) ou (c), a recomendação passa a (c).

### P-8 — A destinação se corrige?

| Opção | Regra |
|---|---|
| **(a)** Por ato contrário, com motivo, que cita a destinação que desfaz — como o desfazimento da vaga acrescida (`097`) —, **só enquanto a vaga destinada não tiver chamada** | Erro de operação tem conserto; vaga que já chamou alguém não volta. |
| (b) Nunca: destinação é definitiva | Mais simples; erro só por Retificação ou fora do sistema. |
| (c) Por ato contrário a qualquer tempo | Desfaz chamada já feita — não recomendado. |

**Recomendação: (a).**

### P-9 — A destinação é publicada?

| Opção | Onde aparece |
|---|---|
| **(a)** Registro do ato com trilha, visível na ocupação, no histórico do recorte e no relatório do Edital (`099`); a chamada de quem ocupa a vaga revertida cita a destinação no fundamento | Sem documento público novo. |
| (b) Também na página pública da seleção e no documento da próxima publicação de convocados (`149`) | Transparência ao candidato da cota. |

**Recomendação: (a)**, e (b) em spec própria se a comissão quiser publicar.

### P-10 — A ampla que recebe a vaga e também não tem mais quem chamar (N-5)

| Opção | Regra |
|---|---|
| **(a)** A declaração de vaga não preenchida vale para a linha geral também, com o mesmo ato e o mesmo fundamento escrito | Fecha o beco do outro lado. Estende o ato à ampla. |
| (b) Só para a reservada; a ampla esgotada fica como achado | Escopo menor. |

**Recomendação: (a)**, porque a vaga revertida que não acha ocupante é o mesmo problema do C09, uma
lista adiante.

## O que esta spec cobre, e o que fica fora

**Cobre:**
- a leitura da situação da vaga reservada sem quem a ocupe, dita igual no Centro, na ocupação e na
  convocação;
- o ato de destinação que aplica a reversão declarada pelo Edital, com conferência antes, fundamento e
  registro;
- o ato que declara a vaga não preenchida, nunca por padrão;
- o Edital silente (P-2);
- a lista vazia, no marco por pontuação (P-6) e no sorteio (P-7);
- a correção da destinação (P-8).

**Fica fora:**
- a cascata entre cotas, salvo resposta (b) ou (c) à P-4;
- o remanejamento entre Perfis: o 57/2026 o proíbe, e a FR-246 da `016` continua;
- o destino da vaga não preenchida **fora** do Edital — Edital de vagas remanescentes, vaga acrescida
  noutro Edital pela `097`: o fato registrado aqui é o ponto de partida, e o ato de lá continua o de lá;
- a publicação da destinação em documento público, salvo resposta (b) à P-9;
- a concorrência concomitante no corte e na fila (estudos de 05/11 e 07/11), salvo o que a P-3 (a)
  decidir;
- qualquer mudança no que a apuração conta, além do que a P-1 e a P-3 decidirem.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A presidência destina a vaga que o Edital manda reverter (Priority: P1)

O Perfil declara reversão (por saldo ou por esgotamento). A lista reservada não tem quem ocupe a vaga.
A presidência vê, na ocupação e no Centro, *"1 vaga da PPP sem quem a ocupe. O Edital, no Perfil,
declara: «As vagas reservadas … que não forem preenchidas passam para a ampla concorrência»"*, e o
ato "Destinar à ampla concorrência". O "Confira antes" mostra origem, destino, quantidade, a frase
publicada e a versão do Edital. Confirmado, a reserva passa a "0 a ocupar — 1 destinada à ampla em
11/11, por …", e a ampla mostra a apuração obsoleta pelo movimento, com o caminho para emitir a
seguinte e chamar a próxima da fila.

**Why this priority**: é o caso em que o Edital já disse o que fazer, e hoje a vaga só chega à ampla
quando a apuração da reservada roda — e sem confirmação.

**Independent Test**: um Perfil com reversão por saldo, 1 vaga PPP, lista PPP com ordem emitida e
ninguém a chamar: o ato produz um registro com fundamento, a soma das vagas por recorte não muda, e
uma segunda confirmação idêntica não produz outro registro.

**Acceptance Scenarios**:

1. **Given** reversão por saldo declarada e 1 vaga PPP sem quem ocupar, **When** a presidência abre a
   ocupação, **Then** a tela diz a situação, a frase publicada e o ato disponível, e nenhum outro ato
   para aquela vaga.
2. **Given** o mesmo estado, **When** a presidência confirma a destinação, **Then** fica registrado
   quem, quando, a origem, o destino, a quantidade, a causa e a versão do Edital lida, e a ampla mostra
   a causa da obsolescência.
3. **Given** reversão por esgotamento e uma pessoa ainda chamável na reserva, **When** a presidência
   abre a ocupação, **Then** o ato não é oferecido, e a tela diz por quê (há quem ocupar).
4. **Given** o ato já praticado, **When** alguém tenta de novo, **Then** o comando recusa dizendo que
   não há saldo a destinar.

---

### User Story 2 — O Edital silente: a vaga não some, e o sistema não decide (Priority: P1)

O caso do C09. O Perfil não declara reversão. A tela diz *"1 vaga da PPP sem quem a ocupe. Este
Edital não declara o que acontece com a vaga reservada não preenchida."*, e oferece os caminhos da
resposta à P-2 — na recomendação, retificar o Edital para declarar, ou declarar a vaga não
preenchida com fundamento escrito.

**Why this priority**: é o caso do achado 02, e o mais comum do corpus.

**Independent Test**: no C09, a vaga PPP sai do estado "impedida" para um estado final registrado,
por ato com fundamento, sem nenhum registro gerado sem confirmação.

**Acceptance Scenarios**:

1. **Given** o C09 com o resultado definitivo divulgado, **When** a presidência abre o Centro, **Then**
   a providência da PPP diz que o Edital não declara destinação e mostra os caminhos, e não "Pedir a
   faixa seguinte" nem "Destinar à ampla".
2. **Given** o mesmo estado, **When** a presidência declara a vaga não preenchida sem escrever o
   fundamento, **Then** o comando recusa e pede o fundamento.
3. **Given** a declaração feita com fundamento, **When** a presidência volta ao Centro, **Then** a
   fase Vagas não tem mais providência para a PPP, e o registro diz quem, quando e por quê.
4. **Given** o Edital retificado para declarar reversão por saldo, **When** a presidência volta à
   ocupação, **Then** a vaga passa ao caso da US1.

---

### User Story 3 — A lista vazia não pede três atos sem efeito (Priority: P2)

No marco por pontuação, a lista PPP sem inscrito pede hoje ordem, corte e publicação (achado 16). Com
a resposta à P-6, a presidência registra, num gesto, que ninguém concorreu; a lista entra na
publicação do resultado do marco junto das outras; e a destinação fica disponível pela P-5.

**Why this priority**: tira três passos do caminho de todo Edital com cota sem inscrito, mas o
problema crítico é a US1 e a US2.

**Independent Test**: no C09, da emissão da ordem da ampla até a destinação da PPP, o número de
confirmações dedicadas à lista PPP cai de três para uma, e os registros normativos de hoje continuam
legíveis.

**Acceptance Scenarios**:

1. **Given** a lista PPP sem inscrito, **When** a presidência abre a ordenação, **Then** a providência
   diz que ninguém concorre e oferece o gesto único.
2. **Given** o gesto confirmado, **When** o Publicador publica o resultado do marco, **Then** a lista
   PPP aparece nele como "ninguém concorreu", sem publicação à parte.
3. **Given** um marco por sorteio com a reservada vazia e as relações congeladas, **When** a
   presidência abre a ocupação, **Then** a vaga reservada aparece com a destinação disponível pela
   P-7, e não "corte não emitido" para sempre.

---

### User Story 4 — A destinação errada se corrige por outro ato (Priority: P3)

Pela resposta à P-8. A presidência destinou a vaga por engano (o Edital foi retificado, ou havia
recurso pendente). Enquanto a vaga destinada não tiver chamada, ela pratica o ato contrário, com
motivo, que cita o que desfaz; a vaga volta ao recorte de origem.

**Why this priority**: raro, mas sem ele o erro de um clique só se corrige por Retificação.

**Independent Test**: destinar, desfazer, e conferir que os dois registros existem, que as vagas por
recorte voltaram ao de antes e que, com uma chamada na vaga destinada, o desfazimento é recusado.

**Acceptance Scenarios**:

1. **Given** uma destinação sem chamada na vaga, **When** a presidência a desfaz com motivo, **Then**
   os dois registros ficam, e a origem volta a ter a vaga a ocupar.
2. **Given** uma destinação em que a ampla já chamou alguém para a vaga, **When** a presidência tenta
   desfazê-la, **Then** o comando recusa e diz qual chamada a ocupa.

---

### Edge Cases

- **Reversão por saldo com parte da reserva ocupada**: 2 vagas PPP, 1 ocupada e ninguém mais chamável.
  O ato destina 1, e nunca mais que o saldo.
- **Reversão por esgotamento com alguém ainda chamável**: o ato não é oferecido; a tela diz quantos
  ainda podem ser chamados.
- **Recurso pendente no marco**: o ato não é oferecido antes do resultado definitivo (P-5 (a)).
- **Retificação do quadro depois da destinação**: a destinação não é reescrita; ela fica lida contra a
  versão que citou, e a apuração mostra a obsolescência pela causa do quadro retificado, como hoje.
- **Duas confirmações simultâneas**: produzem um registro só; a segunda é recusada por falta de saldo.
- **Edital que declara a cascata entre cotas só no texto** (P-4 (a)): o sistema o trata como silente
  para a cascata, e a tela diz que a ordem entre cotas não está declarada no conteúdo do Edital.
- **Perfis diferentes**: a destinação nunca alcança outro Perfil (FR-246 da `016`), nem com
  fundamento escrito.
- **Edital encerrado**: a destinação não é oferecida depois do encerramento; a vaga que ficou "a
  ocupar" aparece no relatório do Edital como tal.
- **Ampla esgotada que recebeu a vaga**: pela P-10.
- **Ator sem permissão**: a recusa é a de qualquer ato da comissão sobre o Processo; a tela não
  oferece o ato a quem não pode praticá-lo, e diz de quem ele é.

## Requirements *(mandatory)*

### Functional Requirements

**A leitura da situação**

- **FR-6300**: O sistema MUST reconhecer, por recorte reservado, a **vaga sem quem a ocupe**: saldo a
  ocupar maior que zero e ninguém que ainda possa ser chamado para a reserva, pela leitura da P-3, no
  momento da P-5.
- **FR-6301**: Para cada vaga assim, o Centro, a ocupação e a convocação MUST dizer a mesma situação,
  derivada de uma conta só: a quantidade, o recorte, a destinação que o Edital declara — com a frase
  publicada e a versão — ou que ele não declara nenhuma.
- **FR-6302**: A tela MUST oferecer só os atos que o comando aceitaria naquele estado, e MUST NOT
  oferecer "Pedir a faixa seguinte" onde o Edital não publicou continuação (o que o #477 já faz, e
  que esta spec mantém).
- **FR-6303**: Quando o ato não é oferecido por haver quem ocupar, por recurso pendente ou por falta de
  permissão, a tela MUST dizer qual das três razões, e de quem é o próximo passo.

**O ato de destinação à ampla**

- **FR-6304**: A reversão declarada pelo Perfil MUST ser aplicada por ato próprio, "Destinar à ampla
  concorrência", praticado por quem pode emitir a apuração do recorte, e MUST NOT ser efeito de
  nenhum outro ato (P-1).
- **FR-6305**: Antes da confirmação, o sistema MUST mostrar origem, destino, quantidade, a frase da
  reversão publicada, a versão do Edital e o efeito na ampla.
- **FR-6306**: O ato MUST registrar ator, instante, origem, destino, quantidade, causa (lista vazia,
  esgotada ou saldo), a declaração do Edital lida e a versão dela, e a correlação.
- **FR-6307**: A quantidade destinada MUST NOT exceder o saldo do recorte de origem, e a soma das
  quantidades por recorte MUST ser a mesma antes e depois (como a FR-247 da `016`).
- **FR-6308**: O ato MUST ser recusado, com a razão dita, quando o Perfil não declara reversão, quando
  há quem ocupar sob a espécie declarada, quando o resultado do marco não é definitivo ou quando não há
  saldo.
- **FR-6309**: A quantidade **publicada** MUST NOT mudar por destinação; muda a efetiva, como já muda
  pelo movimento da `016`.
- **FR-6310**: Destinada a vaga, a apuração vigente da ampla MUST aparecer obsoleta pela causa do
  movimento posterior, como hoje (FR-263 da `016`), e o Centro MUST levar à emissão seguinte da ampla.
- **FR-6311**: Duas confirmações do mesmo ato, simultâneas ou repetidas, MUST produzir um registro só.

**A apuração deixa de mover vaga** *(depende da P-1)*

- **FR-6312**: Com a resposta (a) à P-1, a emissão da apuração MUST NOT gravar movimento de vaga; a
  apuração da reservada com saldo MUST dizer que a destinação está disponível.
- **FR-6313**: Os movimentos já gravados pela emissão da apuração MUST continuar legíveis e válidos
  como estão, com a mesma causa; nenhum MUST ser reescrito.

**O Edital silente** *(depende da P-2)*

- **FR-6314**: Sem reversão declarada, o sistema MUST NOT destinar a vaga à ampla por nenhum caminho
  desta spec, salvo resposta (b) à P-2.
- **FR-6315**: Sem reversão declarada, a tela MUST dizer *"Este Edital não declara o que acontece com
  a vaga reservada não preenchida"* e oferecer os caminhos da resposta à P-2 — na recomendação, a
  Retificação que declara a reversão e a declaração de vaga não preenchida.
- **FR-6316**: Retificado o Edital para declarar a reversão, a vaga MUST passar ao caso da destinação
  à ampla, lida a versão retificada.

**A vaga não preenchida**

- **FR-6317**: O sistema MUST permitir declarar a vaga **não preenchida** por ato próprio, com
  fundamento escrito obrigatório, e MUST NOT fazê-lo por padrão, por prazo ou por efeito de outro ato.
- **FR-6318**: A declaração MUST registrar ator, instante, recorte, quantidade, fundamento e a versão
  do Edital, e MUST NOT exceder o saldo do recorte.
- **FR-6319**: Declarada, a vaga MUST deixar de contar como "a ocupar", MUST aparecer como "não
  preenchida" na ocupação, no histórico do recorte e no relatório do Edital, e a quantidade publicada
  MUST continuar a mesma.
- **FR-6320**: Onde o Perfil declara reversão e ela é aplicável, a declaração de não preenchida MUST
  ser recusada, dizendo que o Edital manda destinar à ampla.
- **FR-6321**: Com a resposta (a) à P-10, a declaração MUST valer também para a linha geral; com (b),
  só para recorte reservado.

**A lista vazia** *(depende da P-6 e da P-7)*

- **FR-6322**: No marco por pontuação, a lista reservada sem inscrito MUST poder ser levada, num gesto
  com uma confirmação, à ordem vazia e ao corte vazio — os dois registros de hoje, sem perder nenhum.
- **FR-6323**: A lista vazia MUST entrar na publicação do resultado do marco junto das outras listas,
  dita como "ninguém concorreu", e MUST NOT exigir publicação própria.
- **FR-6324**: O gesto MUST continuar a dizer, antes da confirmação, que a ordem vazia declara que
  ninguém concorreu, como a providência da `135` já diz (FR-4672 da `135`).
- **FR-6325**: No sorteio, com as relações do marco congeladas e a reservada sem relação por falta de
  inscrito, a destinação (ou a declaração de não preenchida) MUST ser oferecida sem apuração da
  reservada (P-7 (a)).

**Quem conta como "há quem ocupar"** *(depende da P-3)*

- **FR-6326**: Sob a reversão por esgotamento, "há quem ocupar" MUST contar só quem a resposta à P-3
  admitir; na recomendação, quem tem posição na ordem da reserva, não saiu por desfecho excludente e
  não ocupa pela ampla.
- **FR-6327**: A prévia da classificação e a do sorteio (`095`, `098`) MUST fazer a mesma conta da
  FR-6326, e a equivalência delas com o caminho oficial MUST continuar verificada.

**A correção** *(depende da P-8)*

- **FR-6328**: A destinação MUST poder ser desfeita por ato contrário, com motivo, que cita a
  destinação que desfaz, enquanto nenhuma chamada ocupar a vaga destinada; depois disso, o desfazimento
  MUST ser recusado, dizendo qual chamada a ocupa.
- **FR-6329**: Destinação e desfazimento MUST continuar ambos legíveis; nada MUST ser apagado ou
  reescrito.

**Registro e permissão**

- **FR-6330**: Todo ato desta spec MUST exigir a mesma permissão e o mesmo escopo da emissão da
  apuração, MUST ser negado por padrão a quem não os tem, e MUST entrar na trilha com correlação.
- **FR-6331**: Todo ato desta spec MUST ser reproduzível: relido depois, MUST devolver a quantidade, a
  causa e a declaração que leu, e não as de hoje.
- **FR-6332**: A chamada de quem ocupa uma vaga destinada à ampla MUST citar a destinação no
  fundamento.
- **FR-6333**: As telas e os registros desta spec MUST NOT dizer que alguém foi convocado, aceitou ou
  se matriculou (como a FR-258 da `016`).

### Requisitos de experiência

- **UX-600**: A frase da situação MUST nomear a lista, a quantidade e o que o Edital declara, em
  palavras, sem código de espécie nem identificador.
- **UX-601**: O "Confira antes" da destinação e da declaração de não preenchida MUST seguir o da
  emissão (#467), com o efeito na ampla dito por extenso.
- **UX-602**: No Centro, a providência da vaga sem quem a ocupe MUST ter um ato só por caminho, e a
  "impedida" do #477 MUST desaparecer onde houver caminho.

### Key Entities

- **Destinação de vaga**: ato append-only que leva quantidade de um recorte reservado à linha geral do
  mesmo Perfil, com causa, declaração e versão do Edital lidas, ator e instante. O movimento de vaga da
  `016` é o candidato natural para guardá-la; a escolha é do plano.
- **Declaração de vaga não preenchida**: ato append-only que tira quantidade do "a ocupar" de um
  recorte sem a mover, com fundamento escrito, ator e instante.
- **Desfazimento da destinação**: ato contrário que cita o que desfaz (P-8).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2100**: No C09, a vaga PPP sai de "Ocupar a vaga — impedida" para um estado final registrado
  com **uma** confirmação, e o Centro não mostra mais providência na fase Vagas para aquela lista.
- **SC-2101**: Em nenhum dos 15 cenários de treinamento a tela oferece, para vaga reservada, um ato
  que o comando recusa.
- **SC-2102**: Toda destinação e toda declaração de não preenchida têm fundamento, ator, instante e
  versão do Edital no registro: 100% dos registros, conferido por teste.
- **SC-2103**: Nenhum registro de movimento ou de não preenchida nasce sem confirmação própria: zero,
  conferido varrendo os caminhos de gravação.
- **SC-2104**: Num Edital com cota sem inscrito no marco por pontuação, o número de confirmações
  dedicadas à lista vazia cai de três para uma (P-6 (a)).
- **SC-2105**: A soma das vagas efetivas por recorte de um Perfil é a mesma antes e depois de toda
  destinação e todo desfazimento.
- **SC-2106**: Num roteiro com a presidência de treinamento, a pessoa responde corretamente, sem ajuda,
  o que aconteceu com a vaga PPP do C09 e por quê, lendo só a ocupação.

## Assumptions

- O ato é da presidência ou de quem pode emitir a apuração do recorte; não há papel novo.
- A Retificação que declara a reversão já é admitida como acréscimo pelo catálogo; se a fase do Edital
  a impedir depois do resultado, o plano registra e a P-2 volta ao usuário.
- O C09 é o cenário de referência; o plano acrescenta à `134` um cenário com reversão declarada e um
  de sorteio com reserva vazia, se não houver.
- O estado de partida é o do #477; nada aqui o refaz.
- As três respostas que esta spec recomenda e mais mudam o código são a P-1 (a), a P-3 (a) e a P-6
  (a); a estimativa de esforço do plano parte delas.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| FR-245 a FR-251 da `016` (declaração da reversão) | continuam; esta spec só muda **quando** a reversão se aplica |
| A emissão da apuração que move vaga (I-4) | muda pela P-1 (a), com emenda registrada na `016` no PR da implementação; os movimentos gravados ficam (FR-6313) |
| FR-246 da `016` (nunca outro Perfil) | continua |
| FR-885 da `050` e FR-270 da `019` (o desfecho não move vaga) | continuam; a pendência que o desfecho devolve passa a levar ao ato desta spec |
| FR-4205 da `128` e a decisão da `135` sobre a ordem vazia | continuam: a ordem vazia é registrada, agora no gesto da FR-6322 |
| A recusa da relação vazia no sorteio | continua (P-7 (a)) |
| A pendência da `095` sobre a concomitância em "há quem ocupar" | respondida aqui só com a P-3 (a) |
| O achado da `098` sobre a reservada vazia | respondido pela P-7 |

## Decisões

### D-001 — Nenhum caminho novo move vaga sem ato próprio

*Da orientação do usuário, 11/11/2026: "não adote reversão automática".*

Todo efeito desta spec sobre a quantidade de um recorte — destinar, declarar não preenchida, desfazer
— nasce de um ato que alguém confirma depois de ver o efeito. A alternativa recusada é o gatilho por
estado (a vaga reverte sozinha quando a lista esgota), que é a "reversão automática" que a orientação
exclui. O que acontece com o caminho **antigo**, o da apuração, é a P-1.

### D-002 — O sistema aplica o que o Edital declara, e não infere

Herdada da decisão da `016` de que ausência de declaração não move. A destinação à ampla só existe
onde o Perfil publicado a declara, e a espécie é a declarada. A lei citada pelo Edital fundamenta a
cota e não a calcula, como a `016` já fixou para o percentual.

### D-003 — A vaga não preenchida é fato registrado, e não zero

A vaga que ninguém ocupa e que não vai a lugar nenhum precisa existir como registro, e não como a
ausência de um número: é dela que parte o Edital de vagas remanescentes, e é ela que o relatório do
Edital mostra. Por isso a declaração é ato com fundamento, e a quantidade publicada não muda.

### D-004 — Uma conta só para as três telas

A situação da vaga sem quem a ocupe é derivada num lugar e lida pelo Centro, pela ocupação e pela
convocação, como o #477 fez para a vaga reaberta. Duas contas divergiriam na primeira regra nova.

## Achados fora do escopo (registro)

- **A cascata entre cotas** (N-4) tem demanda real em três Editais do Cefor e no 33/2026 do
  IFFluminense; fica para spec própria pela P-4 (a).
- **Um Edital do corpus cita a Lei nº 12.990/2014 ao lado da Lei nº 15.142/2025**; se a citação
  ainda é a correta é questão do Edital, não do sistema.
