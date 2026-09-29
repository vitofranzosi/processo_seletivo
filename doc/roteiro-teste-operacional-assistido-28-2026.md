# Roteiro do teste operacional assistido — o 28/2026 composto por uma pessoa do setor

**Passo 0,5** da ordem adotada em 27/09, que a
[`DP-18`](decisoes-pendentes-da-consolidacao.md#dp-18--quem-faz-o-teste-operacional-e-quando)
descreve. **Preparado e ensaiado em 27/09/2026** contra a `main` em `f6efe0dd`, que já traz o passo 0.
**Quem faz e quando continua em aberto**: é a pergunta da `DP-18`, e este documento não a responde.

**Fontes.** O protocolo é o da `DP-18`. A comparação é a da
[§F da reavaliação de 27/09](reavaliacao-pos-consolidacao-2026-09-27.md#f-comparação-por-cenários), com
a conta etapa a etapa do [anexo A, §3.2](reavaliacao-pos-consolidacao-2026-09-27/anexo-A-composicao.md)
e a estrutura do Edital no [anexo E](reavaliacao-pos-consolidacao-2026-09-27/anexo-E-estrutura-dos-editais.md).
O PDF é o do Edital 28/2026 retificado em 24/08/2026, que fica fora do repositório. Nenhum dado
pessoal dele foi copiado para cá.

> **O que o teste mede.** Na reavaliação de 27/09, só dois números de esforço são medidos. Os demais,
> entre eles os ~250–310 interações do 28/2026, são **estimativas por custo unitário**. O teste põe um
> número medido ao lado da estimativa, etapa por etapa, antes das specs estruturais do passo 1 em
> diante. E mede o que a estimativa não alcança: onde a pessoa hesita, volta ao PDF ou erra e só
> descobre depois.

---

## 1. O ambiente

### 1.1 Banco próprio e servidor

Banco vazio e **exclusivo do teste**. Vazio porque, com outro Edital publicado no banco, o
*"Partir de um Edital anterior"* da Identificação teria de onde partir, e o teste mede a primeira
oferta de uma família, que [sempre se compõe do zero](decisao-sem-carga-retroativa.md). Exclusivo porque uma suíte
ou outra sessão no mesmo banco muda o que a tela mostra.

A partir de `backend/`, na execução nativa. A primeira linha só é precisa numa worktree nova:

```bash
uv sync --extra dev
```

No macOS com PostgreSQL do Homebrew, `createdb` falha sem `LC_ALL`:

```bash
LC_ALL=C createdb ps_teste_operacional_28
```

Os papéis e as migrations, com papéis próprios do teste para não disputar os de outra sessão:

```bash
make preparar DB_NAME=ps_teste_operacional_28 POSTGRES_USER=$USER POSTGRES_PASSWORD= DB_MIGRATION_USER=pto28_owner DB_MIGRATION_PASSWORD=pto28 DB_RUNTIME_USER=pto28_runtime DB_RUNTIME_PASSWORD=pto28
```

A saída tem de terminar em **`34 de 34 tabelas append-only`**. Se o primeiro número vier `0`, a segunda
passada do `provisionar` não rodou (ver o [CLAUDE.md](../CLAUDE.md)).

O servidor, pelo papel de execução, com o seletor de identidade e o portal de demonstração ligados:

```bash
LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_teste_operacional_28 DB_RUNTIME_USER=pto28_runtime DB_RUNTIME_PASSWORD=pto28 INTERFACE_SELETOR_IDENTIDADE=true PORTAL_IDENTIDADE_DEMO=true ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos-pto28 uv run python manage.py runserver 8050
```

Abra por **`http://localhost:8050`**, e nunca por `127.0.0.1`, que o padrão de `ALLOWED_HOSTS` recusa.
O portal de demonstração e a raiz de arquivos só servem à parte 2; na parte 1 não atrapalham.

**No compose** o caminho é `docker compose up --build`, e o `.env.example` já liga o seletor. Serve
numa máquina dedicada ao teste. Numa máquina de desenvolvimento, prefira o banco próprio acima: o do
compose é o mesmo de todo dia.

### 1.2 A identidade e o papel

O observador se identifica **antes** de entregar a tela, em `/gestao/identificar`, e a pessoa recebe a
sessão aberta em `/gestao/`:

| Campo | Valor |
|---|---|
| Identificador | `operador.teste` |
| Papéis | **Elaborador** e **Gestor** |

- **Os dois papéis são necessários.** O Gestor cria o Processo e o Edital (`processo:criar`,
  `edital:criar`), e o Elaborador compõe e submete. Com um só, a pessoa para na primeira tela.
- **O seletor fica fora da medição.** Ele só existe fora de produção e será trocado pela autenticação
  institucional. O estudo de 21/09 mediu o atrito dele (os papéis aparecem sem dizer quais são
  precisos), e medir de novo seria medir um artefato de demonstração.
- **Homologar e publicar não entram.** A segregação exige outras pessoas, e trocar de identidade no
  seletor também seria artefato. A medição termina no **Submeter para revisão**.

### 1.3 As datas

**Não há cadastro retroativo de Edital** ([decisão de 25/09](decisao-sem-carga-retroativa.md)): as
inscrições do PDF encerraram em 06/05/2026, e o sistema recusa, com razão, publicar Edital que não
receberá inscrição. O teste compõe **a oferta seguinte**, com a mesma estrutura:

> **O Edital 28/2027: as mesmas datas do PDF, um ano depois.**

É a única frase que o observador diz sobre o cenário. Somar um ano mantém dia e mês iguais aos do PDF,
e a conversão é uma só, a mesma em todos os 18 Eventos. O preço é o dia da semana: 08/05, 12/06 e
03/07 de 2027 caem num sábado. O sistema não recusa data de fim de semana, e o teste não mede isso.

Com o ano de 2027 no Processo, os Eventos não disparam o aviso de ano divergente. Se a pessoa digitar
2026 no Processo, o aviso aparece, e isso é dado do teste: anote como **recuperação de erro**.

### 1.4 Antes de a pessoa chegar

- [ ] `make preparar` terminou em `34 de 34`, e `/gestao/` abre com *"Nenhum Processo Seletivo"*.
- [ ] A sessão está identificada como na §1.2, e a tela parada em `/gestao/`.
- [ ] O PDF do 28/2026 está aberto em outra janela, **do jeito que o setor o recebe**: o arquivo
      inteiro, sem os anexos recortados. Os Anexos II a VI estão nas páginas 17–18, 19, 20, 21 e
      22–23; recortá-los é trabalho que o setor faz fora do sistema, e o tempo dele se anota à parte
      (§3.3).
- [ ] Gravação de tela e de áudio, **com o consentimento da pessoa**. Contar interações ao vivo não
      funciona: a contagem sai da gravação, depois.
- [ ] Relógio visível para o observador, e a ficha da §3 impressa ou aberta.
- [ ] O cartão de respostas de domínio (§2.2) à mão, e só ele.

---

## 2. O que a pessoa recebe

**O PDF do 28/2026, a tela aberta e uma frase:** *"Componha o Edital 28/2027: as mesmas datas deste
PDF, um ano depois. Quando achar que terminou, submeta para revisão."*

**Nenhuma instrução sobre o sistema.** Nem tour, nem ajuda, nem o nome das etapas. A dúvida é o dado.

Um pedido, que não é instrução sobre o sistema: **que ela pense em voz alta** — o que está procurando,
o que esperava encontrar. Sem isso, a hesitação só aparece como silêncio na gravação, e silêncio não
se classifica.

### 2.1 O que o observador responde

| A pergunta é sobre | O observador | Anota como |
|---|---|---|
| o sistema (*"onde fica…?"*, *"o que é este campo?"*, *"posso deixar em branco?"*) | *"Faça como faria sozinha. Eu não posso ajudar."* | **hesitação**, com a pergunta literal |
| o Edital, e o PDF responde | *"Está no Edital."* | **consulta externa** |
| o Edital, e o PDF **não** responde | lê a resposta do cartão (§2.2), e nada além dela | **consulta externa**, com o número do cartão |

A regra da coluna do meio é a mais difícil de cumprir: *"posso deixar em branco?"* é pergunta sobre o
sistema, e a resposta é o silêncio.

**Se a pessoa travar.** A `DP-18` não trata do caso, e ele precisa de decisão antes do teste. A
proposta: depois de **10 minutos** no mesmo ponto sem avanço, o observador pergunta se ela quer seguir
ou parar ali. Se seguir e continuar travada, ele dá a menor informação que destrava, anota como
**intervenção** — uma quinta marca, fora das quatro categorias — e a etapa sai da comparação com a
estimativa. Travar é o dado mais forte do teste, e ele não pode se perder numa ajuda sem registro.

### 2.2 O cartão de respostas de domínio

O que o PDF não diz, ou diz errado, e o setor resolveria perguntando à chefia. As respostas são
**fixas**, para que duas pessoas testadas recebam a mesma informação. A origem de cada lacuna está no
[anexo E](reavaliacao-pos-consolidacao-2026-09-27/anexo-E-estrutura-dos-editais.md).

| # | A pergunta provável | A resposta, na íntegra |
|---|---|---|
| D1 | A inscrição começa em 2025? (Anexo I, linha 2) | *"É erro de digitação. O ano é o mesmo dos outros Eventos."* |
| D2 | O resultado dos recursos é em 2025? (Anexo I, linha 10) | *"É erro de digitação. O ano é o mesmo dos outros Eventos."* |
| D3 | Qual é a fonte da semente do sorteio? (o item 8.2 fala do software e da semente, e não diz de onde ela vem) | *"A Loteria Federal. Vale o concurso 6150; se ele não sair, o concurso seguinte."* |
| D4 | O que é o item 9.13? (Anexo I, linha 8) | *"Não existe. É erro de remissão: vale a análise documental do item 8."* |
| D5 | Onde fica o quadro 2 do item 4.5? (item 4.2.3) | *"É o quadro do item 4.4."* |
| D6 | "Até 15 suplentes por código de vaga": código é o polo ou o polo em cada Modalidade? | *"Cada polo em cada Modalidade."* |
| D7 | Quando é a verificação de PcD? | *"O Edital não marca data. Fica fora do cronograma."* |
| D8 | Que horas são os Eventos sem hora? | *"O Edital não diz. Use o horário que o setor usaria."* |

O concurso de D3 é fictício, porque a data é de 2027. O número serve ao sistema, que exige uma
referência terminada em número.

---

## 3. A ficha de observação

### 3.1 As quatro categorias

As da `DP-18`, com a quinta marca da §2.1:

| Marca | Categoria | O que é | Exemplo esperado no 28/2026 |
|---|---|---|---|
| **R** | Repetição | "já fiz isso" — digitar de novo o que já está no sistema | corrigir a Denominação de cada cópia de polo |
| **H** | Hesitação | "não sei qual escolher" — parar diante de uma escolha | *"Qual delas é a ampla concorrência"*, com a Modalidade AC declarada |
| **C** | Consulta externa | voltar ao PDF ou perguntar a alguém | a fonte da semente (D3) |
| **E** | Recuperação de erro | "configurei e só descobri depois" | o instante da ocorrência recusado ao gravar |
| **I** | Intervenção | o observador destravou (§2.1) | — |

A repetição mede esforço mecânico. As outras três, carga cognitiva. **Uma ocorrência leva uma marca
só**, a da causa: voltar ao PDF porque a tela pede um dado que o Edital tem é **C**; voltar ao PDF
porque não se entendeu o campo é **H**, e a volta ao PDF é o sintoma.

**Voltas entre etapas** ganham linha própria, com o motivo. Uma volta de Inscrição para Anexos e de
Anexos para Inscrição, para ligar o modelo ao documento, é **R** (a ordem do assistente a provocou); uma
volta da Revisão para a Classificação, para conferir o marco, tem como causa o
[achado da Revisão](achado-revisao-nao-mostra-a-classificacao.md), e isso vai escrito. *O achado foi
corrigido em 27/09: se o teste rodar sobre uma `main` que já tem a correção, a Revisão mostra a
Classificação, e uma volta dessas passa a ter outra causa, que vai escrita.*

### 3.2 A unidade de interação

A mesma do anexo A, §1, do estudo de 21/09 e da `043`: **um clique em botão, um campo preenchido, uma
escolha de rádio ou de `select`.** Rolar a página, abrir um `details` de ajuda e ler não contam; o tempo
deles aparece no relógio. Um campo apagado e redigitado conta duas vezes, e a segunda leva a marca
**E**.

A contagem sai da gravação, etapa por etapa. Ao vivo, o observador anota só **a hora** de entrada em cada
etapa e **as ocorrências** — a gravação dá o resto.

### 3.3 A ficha, por etapa

Uma folha por etapa do assistente, na ordem dele. A etapa 0 é a criação do Processo, que vem antes do
assistente; a 10 é o ato de submeter.

| # | Etapa | Entrada (hh:mm) | Saída (hh:mm) | Minutos | Interações | Voltas a ela |
|---:|---|---|---|---:|---:|---:|
| 0 | Criação do Processo e do Edital | | | | | |
| 1 | Identificação | | | | | |
| 2 | Perfis de Vaga | | | | | |
| 3 | Cronograma | | | | | |
| 4 | Etapas de Avaliação | | | | | |
| 5 | Classificação | | | | | |
| 6 | Inscrição | | | | | |
| 7 | Anexos | | | | | |
| 8 | Conteúdo | | | | | |
| 9 | Revisão | | | | | |
| 10 | Submeter | | | | | |
| — | **Fora do sistema** (recortar os anexos, ler o PDF sem tela) | | | | — | — |
| | **Total** | | | | | |

E, para cada etapa, o registro das ocorrências:

| Hora | Marca | O que aconteceu, com as palavras da pessoa quando houver | Como se resolveu | Custo (min · interações) |
|---|---|---|---|---|
| | | | | |

**E na Classificação, uma linha a mais**: a ordem que a pessoa seguiu. A estimativa se divide em duas —
**linear** (os 7 polos duplicados na etapa Perfis, e depois um marco por polo) e **invertida** (o marco
do primeiro polo composto antes de duplicá-lo) —, e a medição só se compara com uma delas. Se a pessoa
descobrir o fluxo invertido sozinha, é dado; se não descobrir, também.

---

## 4. A comparação prevista

A conta de cada linha é a do [anexo A, §3.2](reavaliacao-pos-consolidacao-2026-09-27/anexo-A-composicao.md).
A coluna "21/09" é a estimativa do estudo de esforço, que também não foi medida para o 28/2026. A
coluna "Pontos previstos" lista o que o ensaio da §6 encontrou e **a estimativa não contou**; é onde
olhar primeiro se a medida divergir.

| # | Etapa | Conta do anexo A | Estimado hoje | 21/09 | **Medido** | Diferença | Pontos previstos (§6.2) |
|---:|---|---|---:|---:|---:|---:|---|
| 0–1 | Criação + Identificação | 6 + 1 | 7 | ~7 | | | P1 |
| 2 | Perfis de Vaga | polo 1 ≈ 30; 6 cópias × 4 | ~55 | ~215 | | | P2, P3, P4 |
| 3 | Cronograma | 18 × ~4,5 | ~80 | ~80 | | | P5 |
| 4 | Etapas de Avaliação | 3 × ~8 | ~24 | ~24 | | | P6 |
| 5 | Classificação | comum 9 + 7 marcos × ~9 (linear) · 9 + 9 (invertido) | ~72 · ~18 | ~80 | | | P7, P8, P9 |
| 6 | Inscrição | 1 + 12 × ~4 | ~49 | ~49 · ~170 fiel | | | P10, P11, P12 |
| 7 | Anexos | 5 × 3 | 15 | 0 | | | P10 |
| 8 | Conteúdo | ~8 | ~8 | ~8 | | | P13 |
| 9 | Revisão | ~6 | ~6 | ~6 | | | P14 |
| 10 | Submeter | parte dos ~9 atos | ~2 | — | | | — |
| | **Total** | | **~250–310** | **~390–480** | | | |

**Três cuidados ao ler a coluna medida.**

- **A soma do anexo A inclui os três atos** (~9); aqui só o submeter entra, e a linha 10 já desconta.
  Os ~250–310 do anexo são "sem anexos"; com os anexos, some 15 aos dois lados.
- **A Classificação compara com um ramo só**, o que a pessoa seguiu (§3.3).
- **Minutos não têm estimativa.** A reavaliação não estimou tempo de composição, e o teste é o
  primeiro número de tempo do 28/2026. Registre-o sem comparação.

O resultado vai num documento próprio, ao lado deste, com a tabela preenchida e as fichas. Este roteiro
não se reescreve: se o teste mostrar que algo aqui estava errado, o resultado diz o quê.

---

## 5. A segunda parte, opcional: um marco com poucas inscrições

A `DP-18` põe a operação depois da composição: *"um marco com poucas inscrições montadas à mão, porque
o `seed_demo` não produz o certame"*. É opcional, e mede outra coisa: não o tamanho do Edital, mas **o
laço por recorte** do [anexo B](reavaliacao-pos-consolidacao-2026-09-27/anexo-B-operacao.md) — um polo do
28/2026 tem três recortes, e cada ato do marco se repete três vezes.

Não dá para operar o Edital da parte 1: as inscrições dele abrem em 2027. A parte 2 usa **um Edital
reduzido, com a estrutura de um polo do 28/2026 e datas em minutos**, que o observador prepara antes.

### 5.1 A preparação (o observador, antes, fora da medição)

Custa ~25 minutos de trabalho e ~30 de espera. O servidor é o da §1.1: o portal de demonstração e a
raiz de arquivos já estão ligados nele. Pode ser o mesmo banco da parte 1.

**1. O Edital reduzido.** Identificado como Elaborador e Gestor, crie um Processo novo e componha:

| Etapa | O quê |
|---|---|
| Perfis | **1 polo**, 4 vagas imediatas; AC, PPI (25%) e PcD (5%), a AC declarada como a ampla; quadro **2 + 1 + 1**; reversão *"só quando a lista reservada esgota"*; convocação por publicação |
| Cronograma | Publicação e **período de inscrições** que termine **~25 minutos** depois da publicação; depois dele a relação, o sorteio e o resultado, na mesma tarde |
| Etapas | só a Análise documental, decisória e eliminatória, ligada a um Evento posterior ao sorteio |
| Classificação | método comum com a **Fonte de demonstração** (ela só existe em desenvolvimento e responde sem rede); ocorrência `6150`; instante = término das inscrições **+ 5 minutos**, em RFC 3339 com fuso; o marco por sorteio com corte no quadro, **1 suplente**, *"a faixa para no alvo"*, a Análise documental como Etapa alimentada e sem recurso |
| Inscrição | 3 documentos: identidade para todos, autodeclaração no recorte PPI, laudo no recorte PcD |

**Por que a Fonte de demonstração, e não a Loteria Federal:** a Loteria exige um concurso já realizado
depois do instante declarado e acesso à rede. O sorteio da parte 2 precisa acontecer na mesma tarde.

**2. Publicar.** *Submeter* como Elaborador. **Saia** (`/gestao/sair`) e identifique-se como outra
pessoa, só com Homologador, e homologue com um motivo. Saia de novo e, como uma terceira, só com
Publicador, publique com a autoridade signatária. Trocar de identidade **sem sair antes** não funciona:
com a sessão aberta, `/gestao/identificar` não mostra o formulário.

**3. A comissão.** Como Gestor, na página do Processo: *Comissão* → incluir `operador.teste` como
**Presidente** e confirmar; *Alocação por Etapa* → *"todos"* na coluna da Análise documental. A pessoa
do teste vai ser, ao mesmo tempo, quem conduz e quem avalia — num marco de cinco inscrições, a banca
é ela.

**4. As inscrições.** Numa **janela anônima**, para não misturar a sessão do candidato com a da gestão,
em `/selecoes/`: cinco pessoas fictícias, **3 em ampla concorrência, 1 PPI e 1 PcD**. Para cada uma:
*Inscrever-se nesta vaga* → e-mail `@exemplo.test` → o **código de acesso sai no terminal do
`runserver`** → nome e CPF fictícios (com dígitos verificadores válidos, que o portal confere) →
Modalidade, telefone, um PDF qualquer por documento → *Revisar* → as duas declarações → *Enviar*.
Leva ~2 minutos por pessoa. Nenhum nome, e-mail ou CPF real.

**5. Esperar o período terminar.** Não comece antes — ver o
[achado da relação](achado-relacao-do-sorteio-congela-com-inscricoes-abertas.md): o sistema deixava
congelar o universo do sorteio com as inscrições abertas, e a pessoa podia fazê-lo sem saber. *Corrigido
em 27/09: sobre uma `main` com a correção, a tela do sorteio diz até quando esperar e não oferece o
botão.*

**6. Entregar.** Saia, identifique-se como `operador.teste` com **Gestor** e **Publicador**, e pare em
`/gestao/`. O Gestor conduz os atos da comissão (sorteio, emissão, corte, apuração, convocação); o
Publicador divulga, porque divulgar é capacidade própria e não efeito de emitir.

### 5.2 O que a pessoa recebe

**A frase:** *"As inscrições do polo terminaram. Conduza o marco até convocar quem ocupa as vagas."* E
o PDF do 28/2026, que é onde estão as regras do sorteio (item 8) e da concomitância (8.7 a 8.9). O
resto da §2 vale igual, e o cartão de domínio ganha uma linha:

| # | A pergunta provável | A resposta, na íntegra |
|---|---|---|
| D9 | Este Edital tem um polo só? | *"É um recorte do 28 para o teste: um polo, quatro vagas, cinco inscritos."* |

### 5.3 O percurso ensaiado, e a comparação

A ordem em que o ensaio de 27/09 operou o marco, pela tela. As estimativas são as unidades do anexo B
(§6, §7, §9 e a conta do 28/2026 em §15.2), aplicadas a **um polo e três recortes**.

| # | Operação | Onde se entra | Unidade (anexo B) | Aqui | **Medido** | Pontos previstos |
|---:|---|---|---|---:|---:|---|
| 1 | Publicar e congelar a relação | página do Edital → o marco → tela do sorteio | por recorte | 3 | | Q1, Q2 |
| 2 | Observar a ocorrência | tela do sorteio | por marco | 1 | | — |
| 3 | Realizar o sorteio | tela do sorteio | por recorte | 3 | | — |
| 4 | Publicar a classificação preliminar | *"Publicar a classificação deste sorteio"*: natureza, autoridade, confirmar | por recorte, ~2 cliques | 3 (~6) | | — |
| 5 | Emitir o corte | página do Edital → *corte*, recorte a recorte | por recorte | 3 | | — |
| 6 | Distribuir a Análise documental | *Alocação por Etapa* → a Etapa → *Propor* e confirmar | 2 por Etapa | 2 | | Q3 |
| 7 | Avaliar | *Minhas Etapas* → a Etapa → cada inscrição → sentido, parecer no desfavorável, *Concluir* | por inscrição da faixa | 4 | | — |
| 8 | Consolidar | a Etapa → *"Consolidar as N prontas"* → confirmar | por rodada | 1 | | — |
| 9 | Apurar a ocupação | página do Edital → *ocupação*, recorte a recorte | por recorte | 3 | | Q4 |
| 10 | Convocar os titulares | página do Edital → *convocação*: inscrição, espécie, vencimento, fundamento | por pessoa, com texto | 3 | | Q5 |

A coluna "Aqui" conta **atos**, e não interações: o anexo B conta atos, e é com ele que a medida se
compara. A ficha da §3 serve sem mudança — uma linha por operação no lugar de uma por etapa do
assistente —, e a unidade de interação continua sendo a da §3.2, para que as duas partes somem.

**O que ficou fora do ensaio, e pode aparecer:** a publicação do resultado depois da Análise
documental (a ocupação não a exigiu), comunicar e registrar o desfecho da convocação, a faixa seguinte,
a reversão da vaga PPI (Q4), recurso e exportação. Se a pessoa for por esses caminhos, a ficha registra
igual; só não há ensaio que diga o que esperar.

### 5.4 Os pontos previstos da parte 2

| # | Operação | O que acontece | Marca provável |
|---|---|---|---|
| Q1 | Relação | A tela do sorteio lista **quatro** recortes: *"Todos os inscritos"* e as três Modalidades. O de *"Ampla concorrência (AC)"* tem só quem **declarou** AC, e o item 8.7 manda sortear a ampla com todos. É o RC-73, já conhecido: o recorte certo é o primeiro, e o quarto sobra | H |
| Q2 | Relação | Congelar com o período aberto era aceito ([achado](achado-relacao-do-sorteio-congela-com-inscricoes-abertas.md), corrigido em 27/09: agora a tela recusa e diz até quando esperar). Não acontece se a parte 2 começar depois do término, como manda a §5.1 | E |
| Q3 | Distribuição | Depois da consolidação, nem a página do Processo, nem a do Edital, nem *Minhas Etapas*, nem a Supervisão tinham link para a distribuição; a porta encontrada no ensaio foi a *Alocação por Etapa* | H |
| Q4 | Ocupação | O inscrito PPI sorteado dentro das vagas da ampla ocupa a ampla (item 8.8), e a PPI fica com **déficit 1** e ninguém na fila. O Edital manda reverter (4.3); a tela oferece *"Pedir a faixa seguinte com este déficit"*. O ensaio parou aqui | H |
| Q5 | Convocação | O vencimento é digitado (o sistema não conta dias úteis) e o fundamento é obrigatório, a cada pessoa | R |

---

## 6. O ensaio de 27/09

### 6.1 O que se verificou

O pedido era conferir que **a estrutura do 28/2026 se compõe até a Revisão sem bloqueio que não seja
do Edital**. Compôs.

No banco da §1.1, com a identidade da §1.2, o Edital 28/2027 foi composto pela tela, etapa a etapa, na
ordem do assistente e pelo fluxo linear:

| Etapa | O que ficou gravado |
|---|---|
| Perfis | 7 polos, o primeiro composto e os outros 6 **duplicados** dele; cada um com AC, PPI (25%) e PcD (5%), a AC declarada como a ampla, reversão *"só quando a lista reservada esgota"*, convocação por publicação e o quadro 28 + 10 + 2 |
| Cronograma | os 18 Eventos do Anexo I, com o ano de 2027 |
| Etapas | Habilitação para o sorteio, Análise documental e Verificação da autodeclaração — as três decisórias e eliminatórias |
| Classificação | o método comum do sorteio (Loteria Federal, concurso 6150) e 7 marcos por sorteio, cada um com corte no quadro de vagas, 15 suplentes, *"a faixa para no alvo"*, a Análise documental como Etapa alimentada e sem recurso |
| Inscrição | o período no Evento 2 e 12 documentos: 7 para todos (o militar facultativo, com instrução), 3 no recorte transversal PPI (os dois de indígenas facultativos) e 2 no PcD |
| Anexos | 5 PDFs, os Anexos II a VI, quatro ligados como modelo do documento |

A Revisão respondeu **"Nada pendente — o Edital pode ser submetido."**: nenhum IMPEDE, nenhum AVISO.
A prévia do documento, gerada da mesma tela, traz os 7 Perfis, o quadro, os marcos com o sorteio, o
corte e o recurso.

**A parte 2 também foi ensaiada**, além do que o pedido cobria, porque um passo a passo que trava no
terceiro passo desperdiça a sessão com a pessoa do setor. O Edital reduzido da §5.1 foi composto,
publicado com três identidades, recebeu cinco inscrições pelo portal e foi operado até a primeira
convocação: três relações, a ocorrência observada, três sorteios, três classificações preliminares
publicadas, três cortes, quatro análises (uma indeferida), a consolidação num gesto, três apurações e
uma convocação praticada.

**O ensaio não é medida.** Os campos foram preenchidos por script no navegador, pelo mesmo formulário e
pelo mesmo `POST` da tela, mas sem o olhar de quem não conhece o sistema. Ele prova que o caminho existe
e onde ele tem atrito, e não quanto custa.

### 6.2 Os pontos previstos

O que o ensaio encontrou no caminho e a estimativa do anexo A não conta. **Não são bloqueios**: todos
têm saída pela tela. São os lugares onde a ficha provavelmente vai registrar alguma coisa, e o observador
não os menciona à pessoa.

| # | Etapa | O que acontece | Marca provável |
|---|---|---|---|
| P1 | Criação | O Processo pede *Identificação institucional* e *Título*, que o Edital não nomeia (estudo de 21/09, §7.1) | H |
| P2 | Perfis | A cópia leva a **Denominação da origem**: as 6 cópias nascem *"… Polo Bom Jesus do Norte"* e cada uma se corrige à mão, **+6** interações | R |
| P3 | Perfis | *"Qual delas é a ampla concorrência"*, a reversão e a forma de convocar **só aparecem depois de gravar** o Perfil com as Modalidades: antes disso são campos ocultos | H |
| P4 | Perfis | Ao aparecer o quadro, a linha geral vem com o total (40), e não com a ampla (28). Deixada assim, a soma dá 52 contra 40, e o aviso só vem ao gravar | E |
| P5 | Cronograma | Campo de data **com hora** para Evento que o PDF publica só com a data (D8), e Tipo e Descrição obrigatórios para uma linha só do Anexo I | H |
| P6 | Etapas | A Habilitação é triagem de completude. Ela não aparece em *"Etapa que habilita a participar do sorteio"*, que só lista Etapa classificatória; e o portal já recusa inscrição sem os documentos obrigatórios (anexo B, §6). Compor a Etapa ou não é escolha que o PDF não resolve | H |
| P7 | Classificação | A fonte da semente não está no PDF (D3) | C |
| P8 | Classificação | *"Quando a ocorrência acontece"* só aceita RFC 3339 com fuso (`2027-05-08T19:00:00-03:00`), e a recusa só vem ao gravar. Já registrado como E-22 na [descoberta do rito do sorteio](descoberta-rito-do-sorteio-2026-09-10.md) | E |
| P9 | Classificação | O recurso do Edital é contra a análise documental e a verificação, e não contra o sorteio; o marco pergunta *"admite, não admite ou não declara"* | H |
| P10 | Inscrição e Anexos | O **modelo** do documento é um Anexo, e a etapa Anexos vem **depois** da Inscrição: ligar os 4 modelos exige voltar, **+4** interações e duas navegações | R |
| P11 | Inscrição | Documento militar "para o sexo masculino" e os dois de indígenas, dentro de PPI, são condição sobre o candidato, que continua sem forma: viram facultativos com instrução ([decisão do recorte documental](decisao-recorte-documental.md), D2) | H |
| P12 | Inscrição | O Anexo II é o Requerimento de Matrícula, e a etapa oferece também o **Requerimento de Matrícula do sistema** (`029`), no ato da inscrição ou na convocação. Qual dos dois o Edital pede? | H |
| P13 | Conteúdo | A seção *"Critérios de Classificação"* nasce dizendo que a classificação observa **a pontuação** das Etapas, num Edital em que todo marco é por sorteio. Passa se ninguém ler | E |
| P14 | Revisão | A conferência *"O que será congelado"* **não mostra a Classificação** — nem o método do sorteio, nem os marcos. Só a prévia do PDF mostra ([achado](achado-revisao-nao-mostra-a-classificacao.md)) | — (causa de volta) |

### 6.3 Bloqueios

**Nenhum, nas duas partes.** A única recusa do percurso foi a de P8, que é do contrato do campo e tem
a correção escrita na própria mensagem.

Dois achados saíram do ensaio. Nenhum bloqueia, os dois estão registrados e nenhum foi corrigido:

- [A Revisão não mostra a Classificação](achado-revisao-nao-mostra-a-classificacao.md) que a submissão
  congela — nem o método do sorteio, nem os marcos. O guardião dela só compara coleções-raiz em lista.
- [A relação do sorteio se congela com o período de inscrições aberto](achado-relacao-do-sorteio-congela-com-inscricoes-abertas.md):
  a `021` põe o término no *Given*, e nada o exige; a distribuição, sobre o mesmo universo, recusa.
  *Decidido e corrigido em 27/09: a publicação da relação recusa como a distribuição.*

### 6.4 O que o ensaio deixou no banco

O banco `ps_teste_operacional_28` ficou com os dois Processos do ensaio: o 28/2027 em elaboração e o
Edital reduzido da parte 2, **publicado**. **Para o teste, use um banco novo** — com um Edital publicado
no banco, o *"Partir de um Edital anterior"* tem de onde partir, e a §1.1 existe para impedir isso.
Os comandos da §1.1 servem com outro `DB_NAME`; os papéis `pto28_*` são do cluster e podem ser
reaproveitados.
