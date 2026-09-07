# Descoberta de escopo — sorteio e anexos do Edital

Duas capacidades apontadas como candidatas a próximas features depois da leitura dos sete Editais
anexos ([`avaliacao-de-capacidade-editais-2026-09-07.md`](avaliacao-de-capacidade-editais-2026-09-07.md)),
e o que a revisão dessa proposta encontrou.

> **Não cria requisito e não decide prioridade.** O que se registra é o **tamanho real** das duas
> capacidades, as decisões que uma spec terá de tomar, e os pontos em que a leitura inicial estava
> errada. Priorizar é do usuário.

## Por que existe

A avaliação dos sete Editais registrou achados. A conversa seguinte propôs uma ordem — anexos
primeiro, sorteio depois — e a revisão dessa proposta mostrou que **"sorteio" não é uma feature: é
uma descoberta de escopo**, e que "anexos" nomeia duas coisas de custos muito diferentes. Registrar
isso aqui é o que impede a proposta de virar premissa por repetição.

---

## Parte 1 · Sorteio

### O que a leitura inicial errou

**"O sorteio torna o 77/2026 integralmente conduzível" é falso**, e contradiz o próprio relatório,
que lista o 77 na linha de corte/progressão da `014`. O 77 manda analisar a documentação até o
limite de vagas, substituir o indeferido pelo próximo sorteado e **parar quando as vagas se
preencherem**. Analisar todos os sorteados não é degradação aceitável: produz uma lista que não é a
que o Edital descreve, e a regra de parada é ocupação, não corte.

A formulação que se sustenta: o sorteio **remove o primeiro e maior bloqueio** do 77; a condução
integral ainda depende da progressão. Se a progressão entrar no recorte da feature, o 77 pode ser o
primeiro vertical completo — o que é escolha de escopo, e não consequência.

O mesmo vale, com mais itens, para 57 e 28: além da `016`, corte e progressão; e o 57 ainda exige
heteroidentificação e segunda instância.

### Onde o sorteio encaixa: três formas, nenhuma decidida

A afirmação categórica de que o ponto de extensão "não é `ResultadoEtapa.Origem`" **conflita com
decisões registradas**:

- a `013`, ao justificar por que não criou constraint sobre a consequência da Ocorrência, escreveu
  que *"o sorteio e a verificação de reserva de vaga, **que a 013 vai hospedar depois**, produzem
  desfecho favorável por caminho que não é avaliação"* — a porta ficou aberta de propósito;
- a `015`, no *Out of Scope*, formulou o bloqueio como ausência de **Resultado**: *"Não há Resultado
  de sorteio para ordenar"*.

O que a leitura do código de fato estabelece é mais estreito: **`Origem.SORTEIO` sozinha não
ordena.** Ordenar pelo número sorteado como se fosse pontuação exige inverter o sentido do número,
porque o motor agrupa por pontuação e ordena do maior para o menor
(`classificacao/domain/desempate.py`) — e inverter seria o código decidindo o que o número
significa.

Há **três** formas candidatas, e a spec terá de escolher entre elas:

```
A · Resultado individual     o sorteio produz ResultadoEtapa por inscrição, e o marco ordena
                             custo: exige que o número sorteado seja pontuação, com o sentido
                             invertido — ou que o marco ganhe direção

B · Ordem coletiva           AtoDeOrdenacao ganha uma segunda origem: ordem constituída por
                             sorteio, e não computada a partir de Etapas
                             custo: mexe na abstração central da 015

C · Critério de desempate    marco só de portas devolve pontuação nula — todos num grupo — e um
                             critério publicado "ordem sorteada" o particiona
                             custo: o menor; nada muda em AtoDeOrdenacao
```

A forma **C** merece exame antes das outras duas, por três razões verificáveis: um marco composto
só de portas já devolve pontuação nula e não zero, com o comentário registrando que *"todos os que
passaram pelas portas começam no mesmo grupo, e os critérios publicados é que podem
particioná-lo"*; o desempate já ordena nas duas direções, por tipo de critério; e a `015` **já viu
essa forma** — "desempate por sorteio executado dentro do sistema" está no *Out of Scope* dela, na
linha seguinte à do próprio sorteio.

Provavelmente há **dois artefatos distintos** em jogo — o resultado individual que governa
progressão, e a ordem coletiva —, e a escolha entre A, B e C é justamente a de quantos deles
existem.

### Correção factual

`peso_da_etapa` **não** recusa peso ausente em Etapa decisória. `e_porta` descarta a Etapa
decisória antes da validação do peso, e o comentário no código diz o motivo: *"Porta não soma e não
exige peso: cobrar peso de quem não é parcela seria cobrar a declaração de um número que a regra
não usa"* (`classificacao/domain/combinacao.py`).

### Transparência: o que a semente resolve e o que não resolve

Semente publicada, algoritmo versionado e hash canônico da lista de entrada tornam o sorteio
**reproduzível**. Não o tornam **auditável**: nada nisso impede o operador de testar várias
sementes e publicar a combinação conveniente.

**A garantia atual desses Editais não é a semente — é a transmissão pública ao vivo.** Os quatro
Editais de sorteio da amostra transmitem no YouTube, com dois servidores presentes e gravação
publicada. Um sistema que passe a sortear não está reproduzindo essa garantia: está **substituindo**
uma garantia social por uma criptográfica.

A proposta de **manter o rito e trocar apenas o software** — sortear ao vivo, transmitindo a tela do
próprio sistema — preserva a garantia em vez de substituí-la, e melhora o que existe hoje: a
audiência passa a ver o universo congelado, a semente e o resultado produzidos numa tomada só, em
vez de um campo "Semente utilizada" no rodapé de um software de terceiro cuja lista de entrada
ninguém publicou canonicamente.

Com uma ressalva que a spec precisa resolver: **a transmissão impede reexecutar, não impede
escolher.** Nada impede ensaiar fora do ar e digitar ao vivo a semente já escolhida. O que fecha
essa porta é a semente **não ser do operador** — origem pública e imprevisível posterior ao
congelamento do universo, ou compromisso publicado antes. Transmitir sem isso transmite a execução,
não a lisura.

Fica registrado também que **transmitir não é capacidade do sistema**: o canal continua sendo o
YouTube. O que a feature precisa entregar é uma tela que valha a transmissão, e uma verificação
pública posterior que qualquer pessoa execute por conta própria.

### Decisões que a spec terá de tomar

- como a semente é obtida ou comprometida antes do sorteio;
- a ordenação canônica da lista de entrada;
- o algoritmo exato de embaralhamento, e sua versão — que passa a ser **conteúdo normativo
  publicado**, não detalhe de implementação: trocá-lo depois é evento da classe da Retificação, e
  não deploy;
- como evitar viés na conversão dos números aleatórios;
- quais artefatos são publicados antes e quais depois.

### O artefato novo que o sorteio arrasta

Os quatro Editais publicam, dois dias antes, **a relação dos habilitados a participar do sorteio,
com o número de cada candidato**. Sem ela não há o que sortear em público nem como reproduzir
depois.

Ela **não é** a P-4. Publicar a relação e admitir recurso contra ela são duas capacidades: a P-4
registra a segunda, e só quando o Edital a prevê — o 76, por exemplo, não prevê recurso nenhum.

### Pacote mínimo

```
relação de habilitados + numeração
      ↓
sorteio auditável (semente comprometida, algoritmo publicado, execução ao vivo)
      ↓
ato de ordenação
      ↓
corte e progressão da análise documental          ← sem isto, o 77 não fecha
```

---

## Parte 2 · Anexos

### A intenção, dita por inteiro

O que se quer é o ciclo completo, e ele é o que os sete Editais fazem:

```
elaboração    o autor inclui no Edital o documento que o candidato precisará devolver
     ↓
publicação    o anexo viaja com o Edital, sob a mesma vigência e a mesma Retificação
     ↓
inscrição     o candidato baixa, preenche, anexa
     ↓
avaliação     a banca lê e conclui — defere ou indefere
```

**Dois terços do ciclo já existem.** Anexar existe desde a `009`: o candidato envia um arquivo por
`DocumentoExigido`, validado como PDF pelo conteúdo, em armazenamento privado, com hash e
congelamento no envio. Avaliar existe desde a `012`/`013`: Etapa decisória, rótulos publicados pelo
próprio Edital — "Deferido"/"Indeferido" —, mesa de avaliação e `ResultadoEtapa`. A banca já abre
*documento exigido → documento apresentado*.

**O que falta é a primeira perna**: o Edital não sabe carregar o documento. Hoje ele exige o anexo e
manda o candidato a um anexo que o documento publicado não contém.

### A bifurcação que "anexo com campos" esconde

```
1 · anexo como arquivo        o autor sobe o arquivo; o candidato baixa, preenche, assina,
                              digitaliza e anexa; a banca lê. O sistema nunca lê os campos.

2 · formulário com campos     o autor declara campos; o candidato preenche dentro do sistema;
    que o sistema conhece     o sistema gera o documento preenchido.
```

**A forma 1 é a que fecha o ciclo, e é a que os Editais praticam.** Requerimento de inscrição,
autodeclaração étnico-racial, declaração de pertencimento, declaração da chefia imediata,
procuração, termo LGPD: todos são preenchidos fora, assinados, digitalizados e devolvidos. A banca
defere lendo o que foi devolvido, e é isso que ela já faz.

**A forma 2 colide com uma recusa registrada.** A `009` recusou a expressão condicional no
`DocumentoExigido` com esta frase: *"não há quinta forma, não há operador e não há expressão — e é
essa recusa que separa isto de um construtor de formulários"*. A forma 2 é o construtor de
formulários por outro caminho.

### O teste que o próprio projeto já formulou

A `015` resolveu essa mesma tensão quando criou `FatoDeclarado`, e a docstring dele é o critério:

> **Não é construtor de formulário** — a recusa da `009` era de configuração de tela. Isto é
> conteúdo normativo: o campo existe porque **uma regra publicada o consome**.

O teste, portanto: **um campo do anexo só é legítimo quando uma regra publicada o consome.** Onde
consome, ele já tem casa — `FatoDeclarado` — e não precisa de anexo estruturado. Onde não consome,
o campo é tela, e o arquivo basta.

Aplicando o teste à amostra, há **um** caso real de campo que uma regra consome: a coluna
*"EXPECTATIVA DE PONTUAÇÃO PELO CANDIDATO"* das fichas do 14 e do 173 — e no 173 ela é
**vinculante**, porque o Edital determina que não se atribua pontuação que exceda a informada pelo
candidato (P-7). Esse campo pertence ao **barema** (D-4 da `015`) e à P-7, não à feature de anexos.
Mantê-lo fora é o que impede a feature de anexos de inchar até virar a feature de baremas.

### O que a forma 1 ainda exige

Não é trivial, e chamá-la de "barata" precisa de ressalva. `DocumentoPublicado` já dá bytes e hash
append-only, mas restam decidir: o vínculo com Publicação e versão; a substituição do anexo por
Retificação; o download público; e se o anexo **integra** o PDF do Edital ou apenas o **acompanha**.

### A ressalva sobre publicar quadro e ficha como binário

O caminho incremental — publicar qualquer anexo como arquivo imutável e deixar a representação
estruturada para depois — é legítimo, e é mais limpo do que separar por natureza desde já.

Ele é seguro para os **formulários** e caro para o **quadro de vagas**, e a razão é a
imutabilidade: conteúdo publicado não se remodela. O Edital que publicar o quadro como binário fica
assim para sempre. Não é migração adiada — é **bifurcação do acervo** entre Editais com quadro
legível por máquina e Editais sem, permanente, e a `016` depois só alcança a metade nova.

Vale como escolha consciente. Não vale como consequência não vista.

---

## O que continua aberto

| Questão | Onde se decide |
|---|---|
| A, B ou C — onde a ordem sorteada entra | spec do sorteio |
| Se a progressão da análise documental entra no recorte do sorteio | spec do sorteio |
| Origem e compromisso da semente | spec do sorteio |
| Se o anexo integra ou acompanha o PDF do Edital | spec dos anexos |
| Se o quadro de vagas segue pelo caminho binário ou espera a forma estruturada | precede as duas |
