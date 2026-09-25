# Diário operacional — estudo de esforço de cadastro

Ambiente: worktree `edital-registration-ux-study-1291e7`, banco `ps_ux_edital` vazio (33/33 tabelas
append-only protegidas), servidor em :8043, identidade `joana.operadora` com papéis
**Elaborador + Gestor**.

> **Nota de 25/09, na revisão.** Os cinco Editais são reais e já encerrados; para publicá-los foi
> preciso falsear a data de encerramento das inscrições. Carga retroativa não é caminho suportado
> ([decisão](decisao-sem-carga-retroativa.md)). O que aqui decorre só disso — o IMPEDE de inscrições
> encerradas, a data falsa no PDF do 140/2025, a Loteria Federal declarada para Editais anteriores à
> D-G3 — é artefato do método, não achado do produto.

## Caso A — Edital 78/2026 (Libras Iniciante A1, vagas remanescentes)

### A0. Identificar-se
- Tela: seletor de identidade. Papéis listados **pela string técnica da capacidade**
  (`edital:elaborar`, `processo:criar`). Para cadastrar de ponta a ponta é preciso marcar **dois**
  papéis; nada na tela diz isso. Ambiguidade — o operador descobre por tentativa.

### A1. Criar Processo Seletivo  (/gestao/processos/criar)
- Campos: Identificação institucional*, Título* (Processo), Número*, Ano*, Título do Edital*, Descrição.
- **Ambiguidade forte**: o Edital 78/2026 não nomeia nenhum "Processo Seletivo". O operador precisa
  *inventar* duas strings (identificação + título do Processo) que não existem no documento-fonte.
- **Redundância induzida**: "Título" (Processo) e "Título do Edital" acabam iguais num Edital único —
  digitados duas vezes. 4 dos 5 editais da amostra são Edital único.
- Ano vem pré-preenchido com 2026. Bom default.
- 1 tela, 5 campos, 1 objeto criado (na verdade 2: Processo + Edital).

### A2. Perfis de Vaga
Quadro 2 do Edital: Turma 1 (21 vagas, 09h-11h) e Turma 2 (40 vagas, 13h-15h), ambas "Público
externo". §6.10: "para cada código de vaga, análise dos documentos de até 30 suplentes".

- Formulário por Perfil: 13 campos + 2 coleções aninhadas (Modalidades, Fatos).
- **Colisão de vocabulário**: o Edital chama de "Perfil da Vaga" a *coluna* que diz "Público
  externo"; o sistema chama de "Perfil de Vaga" a *linha inteira* (turma). Mesmo termo, dois
  referentes. O operador tem de decidir sozinho.
- **Campos do domínio errado**: `Remuneração` e `Atribuições` ("O que a pessoa fará") são conceitos
  de vínculo de trabalho aplicados a uma vaga de aluno. Nos 3 editais de curso ficam vazios; o
  operador precisa concluir que não se aplicam.
- **Sem destino óbvio** para "Dias e horários das aulas" (coluna do Quadro 2). Coube em `Descrição`
  — que é `<input>` de uma linha, enquanto `Atribuições` é `<textarea>`. Inconsistência.
- **Sem duplicar Perfil**: "Acrescentar Perfil" nasce em branco. Dos 13 campos, 11 são idênticos
  entre Turma 1 e Turma 2. Redigitação integral.
- **BLOQUEIO DURO (Classe A)** — `validacao.js`, `campo()`:
  `linha.querySelector('[name$="-reserveType"]')` devolve o **primeiro** radio do grupo (o `NONE`),
  e `texto()` lê `.value` dele. Falta `:checked`. Resultado: `tipo` é **sempre** `"NONE"`.
  Consequência observada: escolher "Cadastro reserva limitado" e informar o limite marca
  `setCustomValidity("Cadastro Reserva inexistente não admite limite…")` e o `submit` é cancelado
  por `reportValidity()`. **Não é possível salvar Perfil com cadastro reserva limitado pela
  interface.** Verificado: `form.checkValidity() === false` nos dois Perfis.
  Espelho do mesmo defeito: "LIMITED exige um limite" nunca dispara — limite em branco passa.

  **O impasse é total.** Verificado nos dois sentidos:
  - limite preenchido → cliente bloqueia: "Cadastro Reserva inexistente não admite limite."
  - limite vazio → servidor recusa: "Cadastro Reserva limitado exige limite não negativo."
  As três opções são NONE / LIMITED / UNLIMITED. **LIMITED é inalcançável pela interface.**
  O operador só sai declarando "não há" ou "ilimitado" — os dois contradizem o §6.10 do Edital.
  Escolhido "ilimitado" para prosseguir; a informação "até 30 suplentes por código de vaga"
  **fica de fora do Edital publicado**.

- **Ponto positivo forte**: a tela preservou tudo que eu havia digitado e ofereceu
  "Restaurar o que eu havia digitado / Descartar", com data e hora, avisando que o rascunho local
  não chegou ao servidor. Recuperação de erro bem resolvida.

### A3. Cronograma
Anexo I do Edital: 11 linhas, cada uma com **um rótulo e uma data** (duas com intervalo).

- Formulário por Evento: Tipo*, Descrição*, Onde acontece, Início* (`datetime-local`), Término.
- **Duplicação induzida**: o Anexo I traz **um** rótulo por linha; o formulário exige **dois**
  campos obrigatórios (Tipo e Descrição). No evento "Início do curso" digitei a mesma string duas
  vezes. Não há vocabulário controlado de Tipo — é texto livre, sem `datalist`. Consequência:
  o sistema não sabe qual Evento é o sorteio, qual é o prazo recursal.
- **`datetime-local` para data publicada sem hora**: 10 dos 11 eventos do Anexo I têm só data.
  O operador inventa `00:00` (e `23:59` para fim de período). A hora inventada vai para o documento.
- **Linhas só se acrescentam ao fim**; reordenar é `↑`/`↓` um passo por clique. Não há inserir
  no meio, nem arrastar, nem colar uma tabela.
- 11 × 1 clique para criar a linha + ~30 campos preenchidos. Cada clique em "Acrescentar Evento"
  empurra o botão para baixo — em viewport real (~800px) é rolar até o fim a cada linha.
- **Sem painel "Como preencher estes campos"** nesta etapa, ao contrário de Perfis. As ajudas
  ("Vazio para evento pontual", "Sala, endereço, canal de transmissão ou página") estão em
  `<span class="oculto">` — só leitor de tela as recebe. Operador vidente nunca as vê.
- Campo `Descrição` é `<input>` de uma linha e trunca visualmente textos do Anexo I
  ("Resultado Preliminar (após análi…").
- **Ponto positivo**: remover linha preenchida pede confirmação que **conta o que se perde** —
  "Isto descarta 3 campos preenchidos, e não pode ser desfeito."

- **Achado de visibilidade de progresso**: ao avançar, a etapa 3 ficou **PENDENTE** sem dizer por
  quê. O motivo só aparece ao voltar para dentro dela:
  > "Esta etapa fica pendente enquanto o Cronograma carregar Evento cuja data já passou — 11 deles
  > agora. Corrigir as datas abaixo é o que a conclui; o sistema não as altera nem as sugere."
  Hoje é 21/09/2026 e o Edital 78/2026 corre de 05/08 a 14/09/2026 — **todo o cronograma é
  passado**. Cadastro retroativo (ou elaboração que se estende por semanas) deixa a etapa
  permanentemente incompleta. São AVISO, não IMPEDE — mas o indicador de progresso não distingue
  "esqueci algo" de "sei e aceito".

### A4. Etapas de Avaliação
- Campos: Nome*, Evento do Cronograma, Pontuada/Decisória, (Nota mínima, Pontuação máxima) ou
  (Rótulo favorável, Rótulo desfavorável), Peso, Avaliações por inscrição, Caráter (Elim./Class.).
- Positivo: "Valem para todos os Perfis deste Edital" — sem repetição por Perfil.
- **Seletor de Evento ambíguo**: as opções são rotuladas `Tipo · data`. Neste Edital isso produz
  **duas opções literalmente idênticas duas vezes**: "Publicação · 04/09/2026 00:00" e
  "Resultado · 14/09/2026 00:00". A `Descrição`, único campo que as distingue, não entra no rótulo.
  Na etapa **Inscrição** o mesmo seletor usa `Tipo · data — Descrição` e não é ambíguo.
  Dois seletores da mesma coisa, dois rótulos, e o ambíguo é o que escolhe vínculo de Etapa.
- **Campo obrigatório que não se anuncia**: "Rótulo do resultado favorável/desfavorável" não tem
  `*` nem `required`, e os campos opcionais do mesmo cartão dizem "(opcional)" no rótulo. Pela
  convenção do próprio cartão, eles parecem opcionais — e IMPEDEM a submissão.
- **Mensagem de impedimento com caminho interno**:
  > IMPEDE A Etapa decisória deve publicar os rótulos do resultado em
  > `/stages/id=3338c19f-7b61-4f99-bd4c-9fef0490721c/rotuloFavoravel`.
  UUID e nome de campo em inglês. É o ponto mais claro em que a interface exige do operador o
  modelo interno.

### A5. Classificação
- **Marco é por Perfil**: o §6 do Edital declara o sorteio **uma vez**; o sistema pede **um marco
  por Turma**, com Código, Denominação, Casas decimais, Arredondamento, Recurso, Método, Regra de
  corte e Critérios de desempate — tudo em duplicata. A tela justifica bem *por que* o marco é do
  Perfil; não oferece "aplicar aos demais".
- **Divulgação progressiva incompleta**: o cartão promete "A resposta governa o que este cartão
  pergunta em seguida". Escolhido "Por sorteio", **"Casas decimais *" e "Arredondamento *" seguem
  visíveis e obrigatórios** — com a ajuda "Aplicado uma vez, sobre a pontuação combinada", ao lado
  do texto do próprio sistema dizendo "não há pontuação a combinar". O operador inventa valores
  para um conceito que o Edital não tem. Mesmo padrão em "Alvo", que continua visível com a regra
  de corte definida como "Quantas vagas o quadro publicar".
- **Incompatibilidade de modelo (Classe C)**: o método do sorteio é vocabulário fechado —
  Algoritmo: `IFES-SORTEIO-SHA256-v1` (única opção); Fonte da semente: `Fonte de demonstração` |
  `Loteria Federal`. O §6.2 do Edital 78/2026 declara outra coisa: "O software usado pelo Cefor…
  sorteia aleatoriamente… observar o campo 'Semente utilizada' ao fim da página do sorteio" —
  semente **gerada e publicada pelo próprio sistema**, sem fonte externa. **Não há opção
  correspondente.** Para publicar, declarei Loteria Federal + 8 campos que o Edital não contém.
  Isso entra no documento gerado como norma.

### A6. Inscrição
- Positivo: período vem do Evento — "nada é digitado duas vezes".
- Positivo: documentos têm escopo "Todos os Perfis" — sem duplicação por Perfil.
- Positivo: "Obrigatório" já vem marcado.
- 7 documentos = 7 cliques + ~21 campos.
- Ambiguidade: o Anexo II (Requerimento de Matrícula) é, no Edital, um PDF que o candidato
  preenche e anexa; o sistema tem um "Requerimento de Matrícula" nativo. Nada orienta a escolha.

### A7. Anexos
- Exige upload de PDF. Os Anexos I/II/III do Edital original estão dentro do mesmo arquivo — o
  operador teria de recortá-los fora do sistema. Anexo I (Cronograma) já é nativo: publicá-lo como
  anexo duplicaria. Etapa sem "Salvar rascunho" (só Voltar/Avançar), ao contrário das demais.

### A8. Conteúdo
- **O conjunto e a ordem das seções são do sistema**: 12 seções fixas, 7 com texto livre,
  5 compostas automaticamente.
- Estrutura do Edital 78/2026 × estrutura do sistema:
  | Edital original | Onde coube |
  |---|---|
  | 1. Informações gerais sobre o curso | APRESENTAÇÃO |
  | Quadro 1 — Matriz curricular / ementa | **sem seção própria** → DISPOSIÇÕES PRELIMINARES |
  | 2. Público-alvo | REQUISITOS GERAIS |
  | 3. Requisitos para inscrição | Perfis (Requisitos) |
  | 4. Das vagas | PERFIS DE VAGA (automática) |
  | 5. Inscrição | DA INSCRIÇÃO + DOCUMENTOS (automática) |
  | 6. Do processo seletivo | CRITÉRIOS DE CLASSIFICAÇÃO |
  | 7. Recurso | DOS RECURSOS |
  | 8. Matrícula no curso | **sem seção própria** → DISPOSIÇÕES FINAIS |
  | 9. Certificado | **sem seção própria** → DISPOSIÇÕES FINAIS |
  | 10. Considerações finais | DISPOSIÇÕES FINAIS |
  | — | **DISPOSIÇÕES PRELIMINARES** (seção que o sistema acrescenta) |
  Três seções normativas do Edital não têm lugar e foram empilhadas em "DISPOSIÇÕES FINAIS",
  que passa a conter matrícula + certificado + disposições finais. A ordem de leitura muda.
- **Risco alto**: o texto padrão de CRITÉRIOS DE CLASSIFICAÇÃO afirma
  "A classificação observará a pontuação obtida nas Etapas de Avaliação, respeitados os pesos e as
  notas mínimas" — **falso para este Edital**, que classifica por sorteio. O sistema já sabe que o
  marco é `POR_SORTEIO` e mesmo assim entrega esse texto, sem aviso. Quem não reescrever publica
  uma regra que contradiz o próprio Edital.

### A9. Revisão
- **Positivo forte**: lista consolidada de IMPEDE/AVISO com link direto para o campo. É a melhor
  tela de visibilidade de progresso do fluxo.
- **Ruído**: 11 AVISOs de data passada, um por Evento, com o mesmo texto. Afogam os 3 IMPEDE reais.
- **IMPEDE que inviabiliza cadastro retroativo**:
  > "O período de inscrições encerrou em 03/09/2026 às 23:59. Publicado assim, o Edital não
  > receberá inscrição alguma — corrija a data do Evento na etapa Cronograma antes de publicar."
  Um Edital real cujo prazo já correu **não pode ser publicado no sistema sem falsear a data**.

### A10. Prévia / PDF gerado (8 páginas)

**Bem resolvido**: timbre do MEC/Ifes/Cefor, numeração de seções, rodapé "Página N de 8",
legendas de tabela ("Tabela 1 — Perfis de vaga"), lista de documentos em a)–g) igual ao original,
tabela de cronograma, seções sem conteúdo (Anexos) somem em vez de aparecerem vazias.

**A. Fidelidade semântica — três regras falsas ou contraditórias**

1. **"Cadastro reserva: ilimitado"** na Tabela 1, para as duas Turmas.
   O Edital original (§6.10) diz "análise dos documentos de até **30** suplentes **para cada código
   de vaga**". O documento gerado publica o oposto. Cadeia completa:
   `§6.10 do Edital → radio "limitado" + limite 30 → validacao.js bloqueia → operador escolhe
   "ilimitado" → PDF publica "ilimitado"`.

2. **O documento gerado se contradiz sobre o sorteio.** As seções 5.1 e 5.2 publicam
   "Fonte: Loteria Federal / Ocorrência: Concurso 5900 / Quando: 05/09/2026, às 20h / Semente: os
   dígitos dos cinco prêmios da extração"; a seção 7, escrita pelo operador a partir do §6.2 do
   Edital, publica "o software usado pelo Cefor… observar o campo 'Semente utilizada' ao fim da
   página do sorteio". **Duas normas incompatíveis no mesmo Edital.** A primeira não existe no
   documento original — foi o vocabulário fechado da tela de Classificação que a impôs.

3. **Horas inventadas viram norma**: "05/08/2026, **às 00h**" em 9 dos 11 eventos. O Anexo I
   original publica só a data. O `datetime-local` obrigatório produziu a hora, e o gerador a
   imprime como se fosse declarada.

**B. Completude — o que sumiu**
- **O total de 61 vagas** (§4.1 "será oferecido um total de 61 vagas"). A Tabela 1 não tem linha de
  total; a soma fica por conta do leitor.
- **A assinatura e a autoridade**: no original, o nome próprio de quem assina — "… — Diretora do Cefor,
  Portaria nº 797, de 08/04/2022", e o local/data "Vitória-ES, 05 de agosto de 2026".
  O documento gerado **não tem bloco de assinatura nenhum**. Um ato normativo sai sem quem o assina.
- Anexo III (Termo de Consentimento LGPD) é citado no texto da inscrição e não existe como anexo.

**C. Estrutura documental**
- A numeração **muda entre a tela e o documento**: a tela Conteúdo enumera 12 seções
  (1. APRESENTAÇÃO … 12. DISPOSIÇÕES FINAIS); o PDF traz a apresentação **sem número** e vai de
  "1. DISPOSIÇÕES PRELIMINARES" a "10. DISPOSIÇÕES FINAIS". O operador que revisar por número
  não encontra a seção.
- **Ordem de leitura invertida**: o original apresenta as vagas (§4) **antes** da inscrição (§5);
  o gerado põe DA INSCRIÇÃO (3) e DOCUMENTOS (4) **antes** de PERFIS DE VAGA (5).
- A matriz curricular caiu em "DISPOSIÇÕES PRELIMINARES" — semanticamente errado, e foi a única
  seção livre disponível.
- "DISPOSIÇÕES FINAIS" virou um empilhamento de três seções do original (matrícula, certificado,
  finais), com subtítulos em caixa alta improvisados pelo operador dentro do corpo.
- **Defeito de layout na Tabela 4 (Cronograma)**: a coluna "Nº" é estreita demais e o cabeçalho
  quebra em duas linhas — `N` / `º` na página 6 e **`ºN` invertido** na página 7. Os números 10 e
  11 quebram como `1`/`0` e `1`/`1`. A coluna Início quebra o ano: `05/08/2` / `026, às` / `00h`.

**D. Economia da informação — repetição criada pelo sistema**
- O bloco do método do sorteio (12 linhas) sai **duas vezes**, uma por Turma — e cada cópia começa
  dizendo "Método: **comum a este Edital**". O gerador sabe que é comum e imprime duas vezes.
- Os 5 Requisitos saem duas vezes; no original aparecem uma vez, no §3.
- "A convocação dos classificados será feita por publicação no endereço eletrônico do certame."
  sai duas vezes.
- O Código do Perfil aparece duplicado no rótulo: "Turma 1 — Público externo — Turma 1 (manhã)".
- Com 2 Perfis isso custa ~1 página. O Edital 140/2025 tem 14 polos.

---

## Adendo — conferência dos PDFs em duas passagens (22/09)

A primeira comparação foi só sobre o **texto** extraído (`pdftotext -layout`). Refiz sobre as
**páginas renderizadas** (`pdftoppm`, 110 e 300 dpi) e sobre uma conferência fato a fato. Três
resultados:

1. **Uma afirmação minha estava errada.** Eu disse que o cabeçalho "Nº" da Tabela 4 saía
   **invertido (`ºN`)** na página 7. Não sai: o `pdftotext` inverteu a ordem de leitura. Na página
   renderizada o cabeçalho está **cortado** pela borda da célula, estreita demais. Defeito real,
   descrição errada.

2. **Um defeito passou despercebido no texto.** As linhas **7 e 8** da Tabela 4 saem **sem filete
   horizontal entre elas** — "Resultado Preliminar" e "Período de recurso do resultado preliminar"
   ficam no mesmo bloco. A linha 9 tem filete normal. Só se vê na renderização.

3. **A completude precisava de método, não de leitura.** Conferência de 33 fatos normativos:
   **24 chegaram, 9 não**. Dos 9, **4 são do sistema** (total de 61 vagas, nome da autoridade,
   portaria, local e data) e **5 são erro meu de transcrição** — as citações legais do §1.1
   (Leis 10.098/2000, 10.436/2002, 13.146/2015; Decretos 5.626/2005, 9.656/2018), que deixei de
   copiar para a seção APRESENTAÇÃO.

   O quinto ponto é o mais importante e não estava no relatório original: **nada no fluxo percebeu
   a perda**. As seções de texto livre não têm conferência contra a fonte, e a Revisão não tem como
   saber que um parágrafo normativo sumiu — o sistema não conhece o documento de origem.

**Lição de método:** `pdftotext -layout` serve para conteúdo, não para layout; e "li os dois e
comparei" não é conferência de completude.

---

## Casos B a E — os outros quatro Editais (22/09)

Os quatro foram cadastrados pela interface e publicados. As anotações abaixo registram **o que
permanece verificável no artefato** — o PDF publicado, o PDF original e o banco — e não a narração
do percurso, que não foi escrita na hora.

| Edital | Id da publicação | Original | Gerado | Tabelas no gerado |
|---|---|---|---|---|
| 78/2026 | `0b00691f` | 11 pág. | 8 pág. | 4 |
| 149/2024 | `7575ff02` | 24 pág. | 17 pág. | 12 |
| 28/2026 | `d4bf0826` | 23 pág. | 16 pág. | 16 |
| 14/2026 | `493ad59e` | 17 pág. | 13 pág. | 16 |
| 140/2025 | `6066fb52` | 27 pág. | 27 pág. | 34 |

O gerado é mais curto que o original em quatro dos cinco casos, e a causa é sempre a mesma: **os
Anexos não entram**. O 140/2025 empata em 27 páginas *apesar* de perder onze anexos, porque a
repetição por Perfil consome a diferença (§E7).

### O reuso entre 149/2024 e 28/2026
O 28/2026 é a oferta seguinte do mesmo curso. Foi cadastrado por "Partir de um Edital anterior" a
partir do 149/2024 publicado. Dois registros que o artefato sustenta:

- **O reuso trouxe a estrutura e não trouxe o texto conferido.** O que veio pronto — Perfis,
  Modalidades, Etapas, marcos, documentos — é o que tem forma. O que veio *errado* é o que tem
  prosa: os códigos e as denominações dos marcos continuaram os da oferta anterior até serem
  reescritos um a um.
- **`cutGovernedStage` não é remapeado.** Os marcos herdados apontavam para Etapas do Edital de
  origem; o efeito aparece na Revisão como IMPEDE sem causa visível no cartão.

### O 14/2026 e a circularidade da regra de corte
Sete códigos de inscrição, e o sistema exigiu **catorze** marcos: a regra de corte de um marco
governa uma Etapa, e a Etapa alimenta o marco seguinte. A exigência é correta — é o invariante do
domínio —, mas o custo de digitação dobra sem que a tela explique por quê.

### O `<select multiple>` de "Etapas que entram na ordem"
Em todos os Editais com mais de um marco, este é o campo mais caro da composição. Clique simples
**reinicia** a seleção; `shift+seta` não estende; no macOS só `cmd+clique` acrescenta. Um operador
que não conhece a convenção do sistema operacional perde a seleção que já tinha feito e não recebe
aviso algum.

### A perda sistemática das citações legais — medida nos cinco
Conferência mecânica: extrair de cada original as leis, decretos e portarias citados e procurá-los
no documento gerado.

| Edital | Atos normativos distintos no original | Presentes no gerado |
|---|---|---|
| 149/2024 | 7 | **0** |
| 28/2026 | 7 | **0** |
| 78/2026 | 3 (do §1.1) | **0** |
| 14/2026 | 3 | 1 |
| 140/2025 | 13 | 11 |

Entre os perdidos do 149/2024 e do 28/2026 estão a **Lei 13.709 (LGPD)**, citada sete vezes no
original, e a **Lei 14.126/2021** (visão monocular), citada três. Nenhum deles cabe em campo
estruturado: todos moram nas seções de texto livre, que o operador redigita.

A diferença entre `0 de 7` e `11 de 13` é o achado. Os dois primeiros Editais foram transcritos
antes de eu adotar uma conferência fato a fato; o último, depois. **A fidelidade das seções de
texto livre depende inteiramente do cuidado do operador, e nada no fluxo a mede** — nem a
validação, nem a Revisão, nem a Publicação. O sistema não conhece o documento de origem.

---

## Caso E — Edital 140/2025 (cadastro de reserva de Tutores Presenciais, UAB)

O maior da amostra: **16 códigos de inscrição** (LP01–LP11 e TADS11–TADS15), dois cursos, quatro
modalidades de concorrência em cada código. Foi escolhido como caso de escala.

Partiu do 14/2026 publicado, por "Partir de um Edital anterior".

### E1. O que o reuso entregou, e a que custo

| | Veio do 14/2026 | Precisava | Trabalho |
|---|---|---|---|
| Perfis | 7 | 16 | renomear 7, criar 9 |
| Modalidades | 21 (3 × 7) | 64 (4 × 16) | renomear 21, criar 43 |
| Eventos do cronograma | 13 | 13 | reescrever descrição e data de 13 |
| Etapas de avaliação | 2 | 2 | renomear 1 e trocar a forma |
| Marcos classificatórios | 7 | 16 | renomear 7, criar 9 |
| Documentos exigidos | 6 | 15 | reescrever 6, criar 9 |
| Seções de texto livre | 7 (≈10.900 caracteres) | 7 (≈16.500) | **reescrever as sete** |

O reuso economizou a criação dos objetos; não economizou **campo nenhum de conteúdo**. Todo texto
que veio era do certame anterior.

### E2. O aviso do reuso nomeia o que não é o problema

O banner diz, em toda etapa:

> "Confira e atualize as informações desta oferta — **datas, vagas e prazos** são da oferta anterior
> até que alguém os revise."

Datas, vagas e prazos são justamente o que o operador *espera* ter de mudar. O que o banner não
nomeia é o que veio junto e ninguém espera: **10.900 caracteres de prosa normativa do Edital
14/2026**, incluindo "Professor Formador/Conteudista" e "CURSO FORMAÇÃO PARA ORIENTAÇÃO DE
TRABALHOS ACADÊMICOS FINAIS NA EAD". Um operador que confiar no banner publica o Edital de outro
certame com a capa deste.

### E3. Escalabilidade medida, não estimada

Para chegar de 7 a 16 Perfis completos, pela interface:

- **9 cliques** em "Acrescentar Perfil" — o botão fica no rodapé da lista e desce a cada inserção;
  não há criar-vários.
- **36 cliques** em "Acrescentar Modalidade" (4 × 9) — um por linha vazia, em nove lugares
  diferentes da página.
- **16 × 8 = 128** campos de texto de Perfil (código, denominação, localidade, descrição, carga
  horária, remuneração, requisitos, vagas imediatas).
- **64 modalidades × 2 a 5 campos = 272** campos.
- **16** escolhas de radio "Cadastro reserva ilimitado", **16** de forma de convocação, **16** de
  reversão de vaga, **16** de "qual é a modalidade da ampla concorrência".
- **64** linhas de quadro de vagas.

**≈ 530 interações numa única etapa do assistente.** As demais somam ~200. O Edital original diz
tudo isso em **uma tabela de uma página** (Anexo III) e em três parágrafos (itens 4.3 e 4.4).

Os requisitos são o caso mais claro. O Anexo III original tem **três blocos de requisito** para
onze códigos de Letras — um para LP01–LP03, um para LP04, um para LP05–LP11. O sistema pede o bloco
inteiro **por Perfil**: os mesmos oito itens, digitados onze vezes. Sete das oito linhas de cada
bloco são idênticas em todos os dezesseis Perfis.

### E4. O que o reuso trouxe errado e ninguém sinalizou

- **`immediateVacancies = 1`** em cada um dos 7 Perfis herdados, e **1 vaga na linha AC** de cada
  quadro. O 140/2025 é cadastro de reserva: não tem vaga imediata alguma. O número veio do certame
  anterior e nada o questiona.
- **Códigos e denominações dos marcos**: `TFC 01`…`TFC 07`, "Classificação final — Orientador de
  TFC — Pedagogia / Educação ou EJA". Sete marcos publicariam o nome de outro certame.
- **Regra de corte `quantidade fixa de 10`** nos sete marcos herdados — número do 14/2026.
- Ao trocar a regra para "Este marco não corta", o campo **Alvo continuou com `10`**. A tela não
  limpa o campo dependente; se o servidor o lesse, publicaria um alvo que a regra não usa. O mesmo
  acontece na Etapa: troquei "Com pontuação" por "Com decisão, sem nota" e a **Pontuação máxima
  continuou `100`**, sem aviso.

### E5. Os rótulos do quadro de vagas ficam velhos até salvar

Renomeei as Modalidades de `G1/G2/G3` para `AC/PPIQ/PcD` na mesma tela. O `<select>` do Quadro de
vagas, logo abaixo, continuou oferecendo **"G1 — Grupo 1 — Professores Concursados do Ifes lotados
no campus ofertante"**. O operador escolhe o recorte por um rótulo que já não existe. Depois de
salvar, a lista se corrige sozinha.

### E6. O documento exigido não sabe dizer "apenas para quem concorre como PcD"

O campo "Modalidade" do Documento exigido lista **64 opções** — uma por par *(Perfil, Modalidade)*:

```
LP01 — Tutor Presencial — Letras Português · PcD — Pessoas com Deficiência
LP02 — Tutor Presencial — Letras Português · PcD — Pessoas com Deficiência
… (mais catorze)
```

Não existe "todos os PcD". O item 5.5 do Edital condiciona **sete** documentos à modalidade (laudo
médico, autodeclaração PcD, autodeclaração étnico-racial, declaração indígena, declaração da Funai,
declaração quilombola, autodeclaração PTT). Expressá-los com fidelidade custa **7 × 16 = 112
linhas de documento** para dizer o que o Edital diz em cinco frases.

O que um operador faz — e o que eu fiz — é deixar "Todas as modalidades" e escrever a condição na
instrução. O preço aparece no PDF (§E7).

Duas condições do Edital não têm campo nenhum:
- **"candidatos do sexo masculino, maiores de 17/18 anos"** (certidão de alistamento / reservista);
- **"servidores do Ifes"** (declaração da chefia imediata).

E uma terceira revela um vão no modelo: o item 10.5 convoca por **submodalidade** —
`PPIQ (Pretos/Pardos)`, `PPIQ (Indígenas)`, `PPIQ (Quilombolas)` — e o item 10.5.1 declara a
cascata de reversão entre elas. Modalidade de Concorrência é plana: PPIQ é uma só.

### E7. Edital original × documento gerado

Baixei `/api/v1/public/publicacoes/6066fb52…/documento`. **27 páginas, 34 tabelas.**

**Acertos.** Timbre MEC/Ifes/Cefor; numeração de seções; rodapé com número de página e prefixo do
SHA-256; bloco de Autoridade Signatária; **a lista de documentos exigidos sai em a)–o), com a
mesma estrutura do original**; o texto de reversão ("Havendo ausência de candidatos aprovados na
reserva de vagas, o quantitativo será destinado à respectiva ampla concorrência") e o de recurso
("Caberá recurso no prazo de 2 (dois) dias corridos") são gerados corretamente a partir dos campos.

**A. Fidelidade semântica**

1. **Nove documentos obrigatórios são publicados como `(facultativo)`.** O laudo médico do
   candidato PcD, as três declarações de PPIQ, a autodeclaração PTT, a declaração da chefia e o
   documento militar saem todos marcados assim. Não são facultativos: são **obrigatórios sob
   condição**. O campo é booleano, e as duas escolhas erram — marcar exige de todo mundo, desmarcar
   publica como dispensável. Não há resposta certa na tela.

2. **Horas inventadas viram norma**: "19/11/2025, **às 00h**" em 11 dos 13 eventos e em
   "Realização" das duas Etapas. O Anexo II original publica só a data. O `datetime-local`
   obrigatório produz a hora e o gerador a imprime como se tivesse sido declarada.

3. **Uma data falseada fica visível no documento.** Para vencer o IMPEDE de "período de inscrições
   encerrado" tive de mover o fim das inscrições de 22/10/**2025** para 22/10/**2026**. O documento
   publica um cronograma em que as inscrições terminam **um ano depois** de abertas e **um mês
   depois** do resultado final. Não é erro de quem digita, nem defeito da regra: é o preço de
   publicar um Edital já encerrado — artefato do método.

4. **O quadro de vagas publicado é degenerado.** As dezesseis Tabelas de quadro têm **uma linha
   só** — "Ampla concorrência | 0" — enquanto a tabela de Modalidades ao lado publica 5%, 30% e
   25%. O leitor vê percentuais de nada. A causa é de domínio: o sistema amarra convocação a
   quantidade publicada, e cadastro de reserva não tem quantidade.

**B. Completude — o que não chegou**

- **A tabela de ordem de convocação do item 10.5 — 50 posições.** Não existe objeto para ela. Pior:
  o texto que eu escrevi a cita ("respeitando a ordem apresentada na tabela do item 10.5 do
  Edital") e **o documento gerado não tem item 10.5**. A publicação remete a uma tabela que ela
  própria não contém.
- **Os onze Anexos.** O gerado cita `ANEXO I` a `ANEXO XI` e **não publica nenhum**. Quem lê não
  alcança a Ficha de Avaliação, o Requerimento de Inscrição nem qualquer autodeclaração — sem os
  quais não há inscrição possível. (Ressalva honesta: o navegador desta sessão não envia arquivo, e
  por isso não testei o upload. O que o estudo mede é outra coisa: os Anexos do 140/2025 existem
  **dentro** do PDF-fonte, e o sistema os quer como PDFs separados — a extração é trabalho manual
  que o fluxo não reconhece.)
- **Nome e portaria da autoridade.** O original assina com o nome próprio de quem ocupa o cargo,
  seguido de "Diretora do Cefor — Portaria nº 797, de 08 de abril de 2022". O gerado publica só o
  cargo:
  "Diretora do Cefor / Diretora-Geral do Centro de Referência…". Autoridade Signatária é um papel,
  não uma pessoa; o ato administrativo que a investe não tem onde morar.
- **Local e data** ("Vitória (ES), 07 de outubro de 2025").
- **Duas das treze citações normativas** (a Lei 14.126/2021 entre elas).

**C. Estrutura documental**

O original tem **15 seções numeradas**; o gerado tem **10**. As seções do original que não têm
campo — FUNÇÕES, VAGAS, CLASSIFICAÇÃO FINAL, CONVOCAÇÃO, DA MOBILIDADE ENTRE PERFIS, CURSO DE
FORMAÇÃO, VINCULAÇÃO À UAB, DO PRAZO DE VALIDADE — viram **parágrafos em caixa alta dentro de
outra seção**, na mesma fonte e no mesmo corpo do texto. A hierarquia do documento normativo
desaparece: oito títulos de primeiro nível passam a ser linhas de texto.

**D. Defeitos de renderização — Tabela 34 (Cronograma), páginas 24 e 25**

Conferidos na página renderizada a 150 dpi, não no texto extraído:

1. **O cabeçalho `Nº` está cortado**: a coluna cabe em pouco mais de um caractere e o `º`
   transborda a borda. É o mesmo defeito da Tabela 4 do 78/2026 — não uma inversão de leitura do
   `pdftotext`.
2. **Os números 10 a 13 quebram em duas linhas**: `1`/`0`, `1`/`1`, `1`/`2`, `1`/`3`.
3. **As linhas 6 e 7 saem sem filete horizontal entre elas.** Agora dá para caracterizar a regra:
   o filete some entre linhas consecutivas cujas células vizinhas têm **o mesmo valor** — aqui, as
   duas com `—` em Término e em Onde. Dois eventos distintos, com datas iguais, viram um bloco só.
   É o mesmo defeito do 78/2026, e não é aleatório.

   > **Correção de 25/09.** A regra caracterizada acima está errada. Nos dois casos a primeira
   > linha do par é a que a quebra de página levou para a página seguinte: o gerador anotava o
   > início dela antes da quebra, a quebra recomeçava o quadro sem ele, e a linha ficava fora da
   > grade. As células iguais eram coincidência.
4. **As datas quebram no meio do número**: `26/11/2` / `025, às` / `00h`. A coluna não comporta
   `dd/mm/aaaa, às HHh`.

**E. Economia da informação**

| | Original | Gerado |
|---|---|---|
| Quadro de perfis | 1 tabela, ~1 página (Anexo III) | 33 tabelas, ~13 páginas |
| Requisitos | 3 blocos para 16 códigos | 16 blocos, 7 das 8 linhas idênticas |
| Modalidades e percentuais | 2 parágrafos (itens 4.3 e 4.4) | 16 tabelas idênticas |
| Cronograma | 1 tabela, 1 página | 1 tabela, 2 páginas, ilegível |

O gerado gasta **metade do documento** dizendo dezesseis vezes o que o original diz uma vez. Não é
excesso de zelo do gerador: é o modelo relacional aflorando na página. O Perfil é a unidade, então
tudo que é do certame é reimpresso por Perfil.

### E8. O que o sistema faz bem, e que só apareceu nesta escala

- **O marco novo nasce preenchido** com o código e a denominação do Perfil ("LP08", "Classificação
  final — Tutor Presencial / Supervisor de Estágio — Letras"). Poupa dois campos por marco e acerta
  a convenção.
- **`scheduleEventId` foi remapeado**: as Etapas herdadas do 14/2026 apontavam para eventos de lá e
  vieram apontando para os eventos novos, na posição correspondente. Onde o reuso remapeia, ele
  remapeia bem.
- **Rascunho não enviado é detectado e oferecido de volta.** Ao voltar a uma etapa depois de um
  envio que não completou, a tela anuncia: *"Há preenchimento não enviado neste navegador de
  22/09/2026, 23:29:26. Ele não chegou ao servidor"*, com **Restaurar o que eu havia digitado** e
  **Descartar**. Ao lado do botão de salvar aparece *"alterações ainda não enviadas"*. É a melhor
  prevenção de perda do fluxo.
- **A etapa Cronograma explica por que fica PENDENTE**, no próprio cartão: *"Esta etapa fica
  pendente enquanto o Cronograma carregar Evento cuja data já passou — 13 deles agora. Corrigir as
  datas abaixo é o que a conclui; o sistema não as altera nem as sugere."* (No 78/2026 anotei que o
  motivo não aparecia; aparece — na etapa, não na tela seguinte.)
- **A segregação por pessoa funciona e se explica**: ao homologar, a tela avisa *"Depois de
  homologar, você não poderá publicar esta revisão. Você a elaborou, e publicar exige que ao menos
  outra pessoa autorizada tenha participado."* Publiquei como `carlos.publicador`.

### E9. A Revisão nesta escala

**54 AVISOs e 1 IMPEDE**, em quatro famílias:

| Quantos | Família |
|---|---|
| 16 | "O Perfil X publica 0 vaga(s) imediata(s) e reparte 0 no quadro" |
| 16 | "O marco X não declara regra de corte" |
| 13 | "O Evento Y começou em … que já passou" |
| 9 | "O Perfil X … não declara qual delas é a da ampla concorrência" |
| 1 | **IMPEDE** — período de inscrições encerrado |

O único item que impede a publicação está **soterrado sob 54 avisos**, e 45 deles são a mesma frase
repetida por Perfil ou por Evento. A lista é ordenada por objeto, não por severidade. Corrigido o
IMPEDE, sobraram 44 avisos que o Edital publica assim mesmo.

No primeiro carregamento da etapa Cronograma, logo após o reuso, foram **25 avisos de uma vez**:
12 de "data já passou" e 13 de "é de 2026, e o Edital é de 2025". Nenhum deles é sobre conteúdo —
todos são consequência de o reuso copiar as datas da oferta anterior.

### E10. Atos

`Submeter` → `Homologar` (com **Fundamento da homologação** obrigatório — campo que não se anuncia
como obrigatório até o envio falhar em silêncio) → troca de identidade → `Publicar` com escolha da
Autoridade Signatária. Publicado às 23:32 de 22/09/2026 por `carlos.publicador`.
