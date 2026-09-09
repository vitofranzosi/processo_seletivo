# 021 — Sorteio público auditável

Prompt do `/speckit-specify`. Escrito em 08/09/2026 a partir de uma proposta de feature e revisado
no mesmo dia contra o código em `9ab8013` — a primeira revisão trouxe as seis correções da §"O que
a revisão corrigiu", e a segunda desfez um erro factual sobre `AtoDeOrdenacao`, inverteu a relação
entre compromisso e ato, e fechou seis das oito decisões. Base registrada em
[`descoberta-escopo-sorteio-e-anexos.md`](../descoberta-escopo-sorteio-e-anexos.md) §Parte 1.

**Frase que governa:**

> Publicada e congelada a relação que constitui o universo, uma ocorrência futura e previamente
> determinada de fonte pública externa fixa a semente; com o manifesto público, qualquer pessoa
> reproduz a mesma ordem.

**E a frase que mantém o corte:**

> Sorteio não habilita, não elimina e não ocupa vaga. Ele **constitui uma ordem completa** sobre a
> relação congelada; corte, cotas, progressão e convocação **consomem** essa ordem.

## A PRÁTICA QUE ESTA FEATURE SUBSTITUI, NAS PALAVRAS DOS PRÓPRIOS EDITAIS

Os quatro repetem a mesma cláusula (77 6.2; 57 8.2; 28 8.2; 76 5.2): o software é de terceiro, e a
garantia oferecida ao cidadão é uma linha no rodapé —

> Para fins de auditoria, observar o campo "Semente utilizada: xxxxxxxxxxxxx", localizado ao fim da
> página do sorteio. Ela é que garante a aleatoriedade do processo.

Uma semente cuja lista de entrada ninguém publicou canonicamente, num software que a instituição não
controla, exibida depois do fato. É contra isto que a feature se mede — não contra a ausência de
sorteio.

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- `doc/descoberta-escopo-sorteio-e-anexos.md` §"Parte 1 · Sorteio" — as três formas A, B e C, e o
  que a leitura inicial errou. É o documento que impede esta spec de repetir premissa
- `doc/avaliacao-de-capacidade-editais-2026-09-08.md` — o sorteio é o bloqueio de maior alcance,
  4 dos 7; e o que **não** é dele
- `doc/achados-editais-externos.md` — os Editais são EVIDÊNCIA, nunca especificação
- `backend/processo_seletivo/classificacao/models.py:18` — `AtoDeOrdenacao`: **não tem `origem`**.
  Tem `versao`, `universo`, `ato_anterior` e `motivo_da_sucessao`
- `backend/processo_seletivo/classificacao/application/calculo.py:244` — `_resumo_do_universo`, que
  é montado **na emissão**: resumo da entrada, e não compromisso anterior a ela
- `backend/processo_seletivo/classificacao/application/reproducao.py` — o contrato de reprodução, e
  a frase que esta spec herda: *"A posição gravada nunca é usada como entrada do motor"*
- `backend/processo_seletivo/classificacao/application/emissao.py:45-95` — prévia livre,
  `confirmacao_do_calculo` por assinatura e idempotência por chave. **A máquina existe; o que muda
  aqui é quando a prévia deixa de ser legítima**
- `backend/processo_seletivo/classificacao/domain/combinacao.py:131` — marco só de portas devolve
  pontuação **nula**, e os critérios publicados é que particionam o grupo
- `backend/processo_seletivo/classificacao/domain/desempate.py` — os três tipos de critério
- `backend/processo_seletivo/divulgacao/models.py:43` — `PublicacaoResultado` **exige** um
  `AtoDeOrdenacao`: não há hoje onde publicar uma relação que não seja ordem
- `backend/processo_seletivo/resultados/models.py:46` — `Origem`, e a docstring da `013` que deixou
  a porta aberta ao sorteio
- `backend/processo_seletivo/shared/canonical.py` — `canonical_bytes` e `canonical_sha256`: a chave
  do sorteio **não inventa serialização**
- `.specify/memory/constitution.md` §VI — a capacidade precisa ser observável pelo canal do ator

## A INVERSÃO QUE ORGANIZA A FEATURE

O erro que a segunda revisão desfez vale mais que qualquer decisão desta spec:

```
ERRADO   o universo do AtoDeOrdenacao serve de compromisso
         → o ato é append-only e nasce na emissão; ele não prova nada sobre o instante
           anterior à semente

CERTO    Publicação da relação de habilitados        ← compromisso, anterior à semente
                     ↓ identidade + resumo, imutáveis
         AtoDeOrdenacao constituído por sorteio      ← resultado, posterior à semente
```

**A relação publicada é o compromisso temporal; o ato é o resultado dele.** É por isso que não é
preciso criar `LoteDeSorteio` — não porque o `universo` do ato já resolva, mas porque a relação
publicada assume esse papel, e o ato passa a citá-la por identidade e resumo.

## O QUE A REVISÃO CORRIGIU NA PROPOSTA DE ORIGEM

Seis pontos. Nenhum invalida a proposta; todos mudam o que a spec pode prometer.

**1 · O sorteio não conduz nenhum dos quatro Editais até o fim.** Ele remove o **primeiro e maior**
bloqueio de 77, 76, 57 e 28. O 77 manda analisar a documentação até o limite de vagas e parar
quando elas se preencherem — regra de parada por ocupação, que é `014`/`016`. Prometer "quatro
Editais desbloqueados" é o erro que a descoberta de escopo já registrou.

**2 · "Sorteio não é classificação" está certo como princípio e não decide onde a ordem entra.** A
descoberta registrou três formas, e duas delas custam mais do que a leitura inicial supunha:

```
A · Resultado individual   ResultadoEtapa por inscrição, e o marco ordena
                           custo: o número sorteado teria de ser pontuação, com o sentido
                           invertido — o sistema decidindo o que o número significa

B · Ordem coletiva         AtoDeOrdenacao constituído por sorteio, e não computado a partir
                           de Etapas
                           custo: AtoDeOrdenacao NÃO tem `origem` — B exige discriminador
                           novo, estratégia de constituição e proveniência própria na
                           reprodução

C · Critério de desempate  marco só de portas devolve pontuação nula, e um critério
                           publicado particiona o grupo
                           custo: falta o veículo do valor E o alcance é parcial
```

O veículo, em C, não existe: os três tipos são `MAIOR_PONTUACAO_NA_ETAPA`, `MAIOR_VALOR_DE_FATO` e
`MENOR_VALOR_DE_FATO`, e `FatoDeclarado` é, por docstring, *"um fato que o Edital exige do
candidato"* — a ordem sorteada não é declarada por ninguém, é produzida pelo sistema. E o alcance é
parcial: **critério de desempate só ordena dentro de grupo já empatado.** Onde houver pontuação
principal, C só representa sorteio integral se alguém fabricar um marco em que todos empatem.

**3 · A transmissão ao vivo impede reexecutar, não impede escolher.** Nada impede ensaiar fora do ar
e digitar ao vivo a semente já escolhida. Só fecha essa porta a semente que não é do operador.

**4 · Recurso contra a relação de habilitados não vem junto.** Publicar a relação e admitir recurso
contra ela são duas capacidades. A segunda é a P-4, que a `018` excluiu, e o 76/2026 não prevê
recurso nenhum.

**5 · O `universo` do `AtoDeOrdenacao` não substitui o compromisso** — ver §"A inversão". Ele é
resumo da entrada montado na emissão, e o padrão de proveniência que esta spec herda; não é prova
de anterioridade.

**6 · Não há onde publicar a relação.** `PublicacaoResultado` exige um `AtoDeOrdenacao`
(`divulgacao/models.py:43`). Relação numerada não é ordem, e por isso ela **é artefato novo**. O
prompt da `020` já registrou que a relação de inscritos é universal — o 73/2026 a publica sem haver
sorteio nenhum —, e o recorte desta spec é a relação **enquanto compromisso do sorteio**, não o
artefato universal.

## O QUE ESTA SPEC JÁ RECEBE TOMADO

### T-1 · Sortear o universo inteiro, nunca "as 40 vagas"

A ordem é completa e histórica. Desistência não gera sorteio novo: a ordem permanece, e quem a
consome decide o que fazer com ela.

### T-2 · Ato institucional único, computação livre

"Execução única" no sentido literal contradiz a reprodutibilidade — o algoritmo **precisa** poder
ser executado indefinidamente por terceiros. O que é único é o ato:

> Para a mesma relação congelada, a mesma ocorrência da fonte, a mesma versão do algoritmo e o
> mesmo recorte, existe no máximo **um ato raiz**. Recalcular é livre; emitir outra ordem não é.

A unicidade é sobre a tupla inteira, e é o que mantém a anulação legal: o sucessor nasce de outra
relação e de outra ocorrência, e por isso não colide com o anterior. Uma unicidade escrita só sobre
o recorte proibiria o caminho de anulação que esta mesma spec desenha.

### T-3 · Não existe prévia depois que a semente é conhecida

Obter a semente, calcular e constituir o ato formam **um comando atômico e idempotente**. O fluxo da
`015` — calcular, conferir a assinatura, confirmar e emitir (`emissao.py:45-95`) — não pode ser
herdado literalmente: ele admite calcular várias vezes antes de decidir emitir, e isso, depois da
semente, é o ensaio que a feature existe para impedir. A idempotência por chave já existe e é
reaproveitada; o que sai é a prévia descartável.

### T-4 · O algoritmo é conteúdo normativo publicado e versionado

Trocá-lo é evento da classe da Retificação, e não deploy. Vale igual para a **regra de fallback** da
fonte da semente: se ela viver em `settings`, a comissão troca a fonte por deploy.

### T-5 · A chave por participante, e não o embaralhador da linguagem

`random.shuffle` acopla a prova à implementação de uma versão de um runtime. A spec congela a forma
exata — ver §"A forma da chave".

### T-6 · O universo é projeção, não digitação

A relação **não** aceita inclusão, exclusão ou numeração manual arbitrária: é projeção de fatos
oficiais já existentes — inscrições submetidas e resultados vigentes aplicáveis. Correção posterior
segue a cadeia, e nunca a edição:

```
resultado ou inscrição é sucedido
      ↓
nova relação publicada
      ↓
nova ocorrência futura da fonte
      ↓
novo ato de sorteio
```

Semente conhecida sobre relação que mudou **não se reutiliza**.

### T-7 · Manifesto, verificador público e vetores de teste no repositório

É o que transforma reprodutibilidade em auditabilidade de terceiro. Sem CPF, sem UUID interno e sem
dado privado no pacote público.

### T-8 · A transmissão é evidência, não garantia

O canal continua sendo o YouTube, e integrá-lo não é capacidade desta feature. O sistema entrega uma
tela que valha a transmissão e uma verificação que sobreviva ao vídeo.

## AS DECISÕES FECHADAS

| | Decisão | Escolha |
|---|---|---|
| **D-1** | Onde a ordem entra | **B** — `AtoDeOrdenacao` constituído por sorteio, com discriminador de origem, estratégia de constituição e proveniência própria na reprodução. A e C ficam recusadas **por escrito**, com os custos acima |
| **D-2** | A relação de habilitados entra? | **Sim** — publicada e congelada, ela é o compromisso do universo. Fora: recurso contra ela (P-4) e a relação de inscritos como artefato universal |
| **D-3** | Semente | **Ocorrência futura, previamente determinada, de fonte pública externa** — com fallback mecânico. Compromisso publicado pela própria comissão fica **recusado**: conhecendo o universo, ela mói sementes e publica o resumo da conveniente |
| **D-4** | Identificador na chave | **Número público da relação**, em representação canônica. É o que os Editais já fazem: *"cada candidato receberá um número para o sorteio, a ser publicado na respectiva listagem"* (77, 6.4; 57, 8.4) |
| **D-5** | Empate de chave | **Número público crescente**, com vetor de teste que o prova |
| **D-6** | Recorte do sorteio | **Recorte de vaga × lista de concorrência** — fechada pela leitura dos quatro Editais, §abaixo |
| **D-7** | Corte e progressão | **Fora.** E a spec diz na frase de valor que o 77 não fecha por aqui |

## D-6, FECHADA PELA LEITURA DOS QUATRO EDITAIS

A hipótese era **um sorteio por Perfil**, com modalidade seguindo como atributo da posição. Os
quatro Editais a desmentem, e a cláusula é a mesma, palavra por palavra, no 57 (8.7) e no 28 (8.7):

> todos os candidatos (inclusive os cotistas) participem do sorteio da ampla concorrência e em
> sequência haverá o sorteio das reservas de vaga

São **sorteios distintos**, e não um sorteio filtrado depois. Os cronogramas confirmam: a relação de
habilitados e a classificação preliminar são publicadas *"(AMPLA CONCORRÊNCIA, PPI e PcD)"* — três
relações e três ordens, e o número que cada candidato recebe é *"publicado na respectiva listagem"*.
O cotista aparece em duas delas, com posição independente em cada.

```
77/2026   perfil único, sem cotas                     1 ordem
76/2026   polos com cadastro de reserva, sem cotas    1 ordem por polo — e ver a ressalva
57/2026   2 cursos × (AC, PPI, PcD)                   3 ordens por curso
28/2026   7 polos × (AC, PPI, PcD)                    3 ordens por polo — 21 no certame
```

A ressalva é do 76, e vale registrar porque a spec vai encontrá-la: ele **não declara o seu próprio
recorte**. Diz "sorteio para classificação do cadastro de reserva", num evento só, com as vagas
distribuídas por polo — e o texto afirma seis polos onde o quadro lista cinco. O sistema não pode
inferir recorte de quadro: onde o Edital não declara, quem elabora declara na composição.

**D-6 fecha assim: o recorte do sorteio é (recorte de vaga × lista de concorrência), e o Edital
declara quais listas existem.** Onde não há cota, há uma lista só — a ampla concorrência — e o
recorte degenera no Perfil, que é por que a hipótese parecia funcionar em 77 e 76.

**A consequência é estrutural, e está verificada:** `uq_ato_raiz_por_marco`
(`classificacao/models.py:44`) é única por `(edital, perfil_id, marco_id)` entre atos raiz. Três
listas sobre o mesmo Perfil e o mesmo marco **colidem hoje**. As duas saídas:

```
um marco por lista        custo: triplica declaração que o Edital faz uma vez — a janela
                          recursal é do marco (018), e os cronogramas publicam um período
                          de recurso só, "(AMPLA CONCORRÊNCIA, PPI e PcD)"

lista como dimensão       custo: mexe na identidade do ato e na constraint
do ato                    — mas é o que o Edital de fato declara
```

*Recomendação:* a segunda. É a que não inventa marco onde o Edital não criou ponto novo do certame.

E o que **não** entra por causa disso: as cláusulas 8.8 e 8.9 — cotista sorteado dentro das vagas nas
duas listas fica na de ampla concorrência, e a vaga reservada passa ao próximo autodeclarado — são
**ocupação**, `016`. O sorteio produz as ordens; a interação entre elas é de quem as consome. Isto é
a frase que mantém o corte, aplicada ao caso mais tentador de violá-la.

## A QUE CONTINUA ABERTA

**D-8 · Local e canal do evento (L-6).** A leitura reforçou a lacuna sem fechá-la. O 76 publica uma
coluna **LOCAL** por evento — *"Canal do Ifes/Cefor no Youtube"*, *"Página da chamada pública"* —, o
77 marca o salão de reuniões e o canal em prosa, e 57 e 28 chegam a criar um **evento próprio** só
para o link da transmissão, que é o Cronograma sendo usado como campo que ele não tem. **Não é um campo opcional
inócuo:** conteúdo publicado novo eleva `SCHEMA_VERSION` para 10 e exige degrau em
`publicacoes/domain/elevacao.py`. É lacuna de **autoria**, da linhagem do Cronograma, e não do
domínio do sorteio — incluí-la mistura linhagens em troca de uma seção melhor. Decisão de escopo,
com o preço à vista.

## A FORMA DA CHAVE

Não basta "SHA-256 por participante". A spec congela isto, e publica vetores normativos:

```
key = SHA-256(canonical_bytes({
    "domain":       "processo-seletivo/sorteio/v1",
    "relationHash": <resumo canônico da relação congelada>,
    "drawScopeId":  <identidade do recorte: vaga × lista de concorrência (D-6)>,
    "seed":         <semente normalizada>,
    "publicNumber": <número público do participante na relação>
}))
```

- ordenação pelo **digest binário completo**, crescente;
- colisão desempatada pelo **número público crescente** (D-5);
- **nenhum** identificador ou valor escolhido pelo operador depois do congelamento entra na chave;
- `relationHash` separa sorteios distintos que porventura recebam a mesma semente;
- `canonical_bytes` é o de `shared/canonical.py` — a serialização não é reinventada aqui;
- os vetores publicam entrada, bytes canônicos, digest e ordem esperada.

E o protocolo da semente fixa, **antes do congelamento**: qual fonte; qual ocorrência, rodada ou
instante; como a ocorrência deriva da data programada; a representação exata dos bytes; a regra de
normalização; o tratamento de indisponibilidade, atraso, bifurcação ou dado inválido; e qual
ocorrência futura substitui a original **sem escolha humana**.

## O QUE JÁ EXISTE E NÃO DEVE SER REINVENTADO

- **Integridade e resumo canônico** (`shared/canonical.py`).
- **Trilha append-only** (`auditoria`): ator, ato, estados, motivo e correlação.
- **Sucessão de ordem com motivo** (`AtoDeOrdenacao.ato_anterior`): a anulação do sorteio é isso.
- **O contrato de reprodução** (`reproducao.py`) — mas **não** o mecanismo: a implementação atual
  busca `stageResults`, combina pontuações e aplica desempates, e não entende sorteio. A `021`
  preserva o contrato e acrescenta estratégia própria para atos constituídos por sorteio; não finge
  que `reproduzir_ato` já conhece essa proveniência.
- **Idempotência por chave** (`emissao.py`), com a ressalva da T-3.
- **Publicação de ordem e sua natureza** (`divulgacao`).
- **Portal público e consulta temporal**: o verificador é uma tela a mais, não um sistema à parte.

## FORA DE ESCOPO — cada um é feature própria

- **Ocupação de vagas, cotas, remanejamento e concorrência concomitante** (`016`);
- **Convocação, chamada e suplência** (`019`);
- **Corte e progressão entre Etapas** (`014`) — D-7;
- **Recurso ou impugnação contra a relação de habilitados** (P-4);
- **Relação de inscritos como artefato universal de todo Edital**;
- **Heteroidentificação** e **aplicabilidade da Etapa** (L-2);
- **Integração com API de transmissão**;
- **Prova objetiva e importação de notas de fora** — é o outro mecanismo ausente, e não é este.

## O TESTE QUE A SPEC PRECISA PASSAR

Descrever, sem lacuna, o ciclo do **77/2026** até a ordem publicada — e **parar ali**, dizendo por
que para:

1. encerradas as inscrições, a comissão publica a relação de habilitados — uma só, porque o 77 não
   tem cota; onde há, é uma **por lista de concorrência** (D-6) —, numerada, projetada dos fatos
   oficiais e com resumo canônico;
2. a relação é **congelada**, e o congelamento é o compromisso: quantidade, números públicos e
   resumo;
3. o método já está declarado — algoritmo, versão, recorte, fonte da semente, ocorrência, fallback e
   regra de ordenação — e não muda em silêncio;
4. a semente vem da ocorrência declarada, **posterior** ao congelamento;
5. obter a semente, calcular e constituir o ato acontecem **num comando só**, com a tela
   transmitida, e produzem a ordem **de todos** os participantes;
6. o resultado é selado e publicado, com manifesto e ordem completa;
7. **um terceiro reproduz a ordem por conta própria**, com SHA-256 e os dados públicos, sem depender
   do vídeo e sem falar com o Ifes;
8. anulado o sorteio, nasce outro — nova relação, nova ocorrência — ligado ao primeiro e com motivo,
   e o primeiro continua legível.

E mais sete, que a revisão acrescentou e que valem tanto quanto os oito:

9. duas requisições concorrentes produzem **exatamente um** ato;
10. fonte indisponível **não** habilita digitação manual da semente;
11. alteração da relação depois da ocorrência **invalida** aquela ocorrência para o novo sorteio;
12. manifesto adulterado é detectado;
13. o verificador recalcula **a partir das entradas**, e nunca das posições publicadas — que é a
    frase que `reproducao.py` já carrega, estendida a esta proveniência;
14. nenhum CPF, UUID interno ou dado privado aparece no manifesto;
15. duas implementações independentes — Python e JavaScript, por exemplo — reproduzem os mesmos
    vetores;
16. um cotista aparece em **duas** ordens — a de ampla concorrência e a da sua reserva — com posição
    independente em cada, e cada lista tem o seu próprio ato raiz (D-6).

O passo 7 é o emblemático: é ele que separa esta feature de um sorteador com semente no rodapé. O
passo 8 é o que impede que "refazer" seja um botão. O 13 é o que impede o verificador de provar a si
mesmo.

E o que o teste **não** cobre, deliberadamente: quem ocupa as 39 vagas do 77, quem é suplente e até
onde a análise documental desce. Isso é `014` e `016`, e a spec que prometer isso está prometendo
outra feature.
