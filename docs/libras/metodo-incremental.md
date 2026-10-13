# Método incremental: como incorporar um edital novo sem refazer o catálogo

O catálogo cresce por rodadas. Cada rodada lê editais novos, reconhece o que já está catalogado,
registra variações e cria unidade só quando a diferença justifica. Nada do que uma rodada anterior
registrou é apagado ou reescrito em silêncio.

> **Revisão da rodada 2 (2026-10-11).** O método da rodada 1 enunciava que mudança de sentido ou de
> condição é outra unidade, mas não o aplicava por inteiro: agrupava regras diferentes por ocuparem a mesma
> posição documental, e tratava diferenças só de redação como diferença de sentido. Esta versão explicita o
> critério (passo 4), acrescenta o contexto legal **antes** da decisão de equivalência (passo 0), as regras
> embutidas noutros trechos (passo 3), a tipagem das variáveis (passo 6) e a camada comunicativa (passo 10),
> e passa a apontar para as ferramentas versionadas em [`ferramentas/`](ferramentas/README.md).

> **Rodada 3 (2026-10-11).** O método foi aplicado pela primeira vez a editais reais, que não saem do sistema
> (28/2026 e 59/2026). O que muda está em *Edital escrito fora do sistema*, depois do passo 10. Nenhum passo
> anterior precisou mudar; 21 unidades mudaram de classificação pelo passo 4.

## 1. O modelo por trás do catálogo

Duas camadas, com funções diferentes:

```text
CAMADA DOCUMENTAL — controle de cobertura e rastreabilidade
unidade (função)         LIB-0093 — Empate no corte: todos os empatados progridem
  └─ texto (redação)     “Empate no corte: Havendo empate na última posição, progridem todos…”
       └─ ocorrência     92/2026 v1, linha E92-147, conteúdo 34bc1a9f…, compositor bbc8e04c

CAMADA COMUNICATIVA — preparação da tradução
narrativa (intenção)     “Como ocorre a classificação e quem pode progredir” — 92/2026
  └─ enunciado           CLA-92-05 · REGRA: seguem os 10 primeiros + 5 suplentes; empatados seguem
       └─ fontes         E92-146, E92-147 (linhas de cobertura) → LIB-0092, LIB-0093
            └─ tradução  (futura) solução e gravação validadas pelo profissional
```

- A **unidade** tem uma função e um sentido. A **ocorrência** amarra um texto a um ato publicado.
- A **narrativa** reúne o que o candidato precisa para uma decisão, vindo de qualquer seção; um mesmo
  trecho pode servir a mais de uma narrativa. O recorte documental **não** define o limite de um vídeo:
  esse limite é do profissional de Libras.
- A **tradução** — quando houver — se liga a enunciados e textos validados para contextos, e nunca só à
  unidade.

## 2. O procedimento

### Passo 0 — Identificar o tipo de certame e o contexto legal

Antes de comparar qualquer coisa: o certame é ingresso em curso, seleção de bolsistas, contratação
temporária, concurso? A obrigação de tradução completa do edital e das retificações em Libras existe por
norma explícita para ingresso e permanência em cursos (LBI, art. 30, VII); os demais tipos têm outras normas
([`auditoria-sistema.md`](auditoria-sistema.md), §13). **Frases iguais em certames de tipos diferentes podem
ter peso jurídico diferente**: o tipo entra no manifesto e condiciona toda equivalência.

### Passo 1 — Ler o edital novo

1. Obter, para cada Publicação, os **bytes do PDF** e o **conteúdo canônico** pela consulta pública
   (`historico`, `publicacoes/<id>`, `publicacoes/<id>/documento`; auditoria, §8) e guardar em `fonte/`.
2. Conferir que o SHA-256 do conteúdo canônico é o que o PDF imprime.
3. Registrar a **versão do compositor**. **Lacuna:** a Publicação não a grava; infere-se pela data de
   publicação contra o histórico de `publicacoes/infrastructure/pdf.py`, marcando a inferência.
4. Obter também os **anexos** (`/api/v1/public/anexos/<id>`): integram o edital e não estão no PDF.
5. Abrir o `manifesto.md` (modelo: qualquer um desta rodada), com o contexto legal do passo 0.

### Passo 2 — Fatiar o documento em linhas de cobertura

1. Definir uma **âncora** — o começo literal — para cada trecho e acrescentá-la a
   [`ferramentas/linhas.py`](ferramentas/linhas.py).
2. Rodar `python3 docs/libras/ferramentas/gerar.py`: o corte confere que a concatenação dos trechos
   reproduz o texto inteiro, e falha se uma âncora não casar.
3. O corte serve à **cobertura**. Ele é documental, guiado pela forma do português, e não decide como a
   tradução se organiza.

### Passo 3 — Identificar a unidade de cada linha

1. **Texto fixo do sistema (origem C):** procurar a constante na *Fonte* das unidades.
2. **Estrutura gerada (A e B):** pela posição e pela forma.
3. **Texto livre (D):** comparar com os textos catalogados da mesma família, e depois por função.
4. **Procurar regras embutidas noutros trechos**: descrições de Evento, nomes de documento, instruções.
   Nesta rodada, três estavam em descrições de Evento (isenção de taxa, LIB-0152; abertura de prazo
   recursal, LIB-0153; antecedência da convocação, LIB-0147). A linha recebe a unidade principal e as
   regras embutidas como unidades adicionais (`extras` em `linhas.py`).

### Passo 4 — Comparar com o catálogo: mesma unidade ou outra?

Decompor cada ocorrência em **destinatário, modalidade normativa (obrigação, possibilidade, proibição),
condição, ação, consequência, prazo e alcance**, e comparar com as ocorrências já catalogadas.

| O que muda entre as ocorrências | Decisão |
|---|---|
| destinatário, modalidade normativa, condição ou consequência | **outra unidade**, com *Relação* para a parecida — ex.: experiência “no magistério”, “no magistério superior”, “no ensino básico ou superior, ou vinculação a pós-graduação” (LIB-0139, LIB-0141, LIB-0142); canal de dúvidas exclusivo × facultativo (LIB-0127, LIB-0151) |
| só valores (datas, números, nomes) | mesma unidade, `PARAMETRIZÁVEL`; conferir se a variável é **de valor** ou **de condição** (passo 6) |
| só a redação, com o mesmo efeito aparente | mesma unidade, `SEMELHANTE`, **equivalência a confirmar** com a área e o profissional — ex.: “pela internet, no endereço do certame” × “pelo sistema de inscrições” (LIB-0031) |
| nada | `EXATA` |

**Os dois erros que este passo evita**, ambos cometidos na rodada 1: agrupar regras diferentes porque ocupam
a mesma posição no documento, e separar comunicações equivalentes porque foram escritas de outro modo. A
redação, sozinha, não resolve nenhum dos dois: a pergunta é sobre efeito, e a resposta pode depender da área.

### Passo 5 — Registrar as ocorrências

Acrescentar a linha em `linhas.py` e regenerar: as *Referências* das unidades se atualizam. **Linhas
antigas não se alteram.**

### Passo 6 — Registrar as variações e tipar as variáveis

- **Variável de valor** muda o dado (a data, o número de vagas). **Variável de condição** muda a regra
  (eliminatória ou não, admite recurso ou não, a Etapa para onde se progride). Em `unidades.py`, a de
  condição leva o prefixo `condição:`. Reaproveitar com variável de condição diferente não é reaproveitar.
- Redação nova com o mesmo efeito: novo *Texto N* (gerado das ocorrências) e nota no *Histórico*.

### Passo 7 — Criar ou desdobrar unidades

- Criar quando a função não existe, ou existe com outro destinatário, modalidade, condição ou consequência.
- **Desdobrar** quando se descobre que uma unidade agrupava regras diferentes: a unidade original fica,
  riscada, com `status="desdobrada"`, as ocorrências que tinha e as sucessoras (`desdobrar()` e `filha()` em
  `unidades.py`); as linhas passam às sucessoras.
- O identificador novo é o próximo livre em [`ferramentas/ids.py`](ferramentas/ids.py). **Nunca se
  reaproveita nem se renumera.**

### Passo 8 — Preservar histórico e decisões

Toda correção vai para o *Histórico* da unidade (`corrigir()` em `unidades.py`), com data e rodada. Decisões
humanas (sinal, limite de vídeo, paráfrase aprovada, equivalência confirmada) se registram na unidade e, se
de termo, na terminologia. O estado de cada versão do catálogo se guarda em `ferramentas/referencia/`.

### Passo 9 — Gerar o pacote do edital

`manifesto.md`, `retificacoes.md` (escritos à mão); `cobertura.md`, `roteiro-producao.md`,
`oportunidades-reuso.md` (gerados); `fonte/`. Rodar `medir.py` e registrar as métricas em
[`viabilidade.md`](viabilidade.md) **como nova medição datada**, marcando a anterior com a versão do
catálogo a que pertence.

### Passo 10 — Atualizar a camada comunicativa

1. Para cada intenção prototipada, escrever em [`ferramentas/narrativas.py`](ferramentas/narrativas.py) os
   enunciados do edital novo, com as fontes (linhas de cobertura), as ambiguidades para a área e as
   perguntas de verificação.
2. Rodar `narrar.py`: ele recusa fonte inexistente e liga toda linha do edital a ao menos uma intenção.
3. Separar **variantes** sempre que o objeto, o destinatário ou o Perfil mudem a regra: recurso contra o
   sorteio e recurso contra a análise documental não se fundem em “o recurso do edital”.
4. Avaliar o reaproveitamento em três níveis — roteiro, solução tradutória, gravação — sem converter
   repetição de texto em estimativa de economia ([`camada-comunicativa.md`](camada-comunicativa.md)).

### Edital escrito fora do sistema

O caminho é o mesmo, com cinco diferenças, todas encontradas na rodada 3:

1. **Fonte.** Não há conteúdo canônico nem hash impresso. O hash é o do **arquivo** publicado
   (`corpus.py`, campo `real`), e o manifesto diz de onde a cópia veio e quando.
2. **Versão.** O órgão costuma publicar só a versão consolidada (“retificado em …”), sem marca do que mudou.
   Registrar qual versão se inventariou, **baixar os atos** e reconstruir, linha a linha, o que cada um muda. **Não
   presumir que a consolidada é a soma dos atos**: no 28/2026 e no 59/2026 ela não era (rodada 4). Fontes úteis para a
   versão original: o “Onde lê-se” das Retificações e os anexos publicados à parte, que podem ser os de antes. Para
   cada arquivo, registrar origem, data de consulta, bytes, SHA-256 e a data de geração do PDF.
3. **Texto em imagem.** Cabeçalhos institucionais podem ser imagem e não saem do `pdftotext`. Listar as imagens de
   cada página (`pdfimages -list`), renderizar cada uma e transcrevê-la em `IMAGENS` (`linhas.py`), com **três
   registros separados**: a transcrição fiel, linha a linha; a normalização, que é a mesma de toda linha e é a que entra
   na comparação; e a avaliação de equivalência, à parte. **A transcrição nunca se ajusta para casar com o catálogo.**
   Imagem repetida em outra página tem linha própria (`depois_de`), com id `<edital>-NNNa`, para não renumerar as
   linhas já citadas.
4. **Defeitos do original.** Remissões quebradas, datas impossíveis, contradições: **registrar, não corrigir**.
   Vão para a nota da linha, para a tabela do manifesto e, quando afetam o que o candidato faz, para as
   ambiguidades da narrativa, com a resposta esperada dizendo que o edital diz as duas coisas.
5. **Tradução existente.** Antes de tudo, procurar se o órgão já publicou o edital em Libras, e registrar os
   metadados — data, duração — e **a versão que ele traduz**, ou a incerteza sobre ela. O que se pode observar sem
   profissional é só o que o vídeo mostra por escrito (no caso dos vídeos do Cefor, o rótulo de seção na tela). A
   tradução não se avalia, e o vídeo não se baixa, recorta nem republica, sem autorização e sem profissional.
   Diferença entre o vídeo e um texto posterior a ele **não é omissão**.

E uma diferença de leitura: nos editais reais, a origem de toda linha é o documento (**R** na matriz), e as
unidades novas nascem com origem **D**. A comparação útil é dupla — contra os simulados (o texto do sistema
reaparece?) e contra os outros reais (o texto da casa se repete?) —, e as duas se medem separadas
(`medir.py`).

## 3. Retificações

Uma Retificação é ato novo sobre o mesmo Edital, publicado como **o Edital inteiro consolidado**
(auditoria, §7). Traduzir só o trecho alterado **não basta**.

### 3.1 Como processar

1. Comparar o consolidado com o original, linha a linha, texto e página
   (`ferramentas/comparar_retificacoes.py`, ou diferença de texto quando a numeração muda).
2. Separar em quatro grupos:

| Grupo | Exemplo nesta rodada | Consequência |
|---|---|---|
| **Texto alterado** | vagas do INF-BJN 40 → 45 (91); fim das inscrições (91 e 01) | nova ocorrência; tradução ou gravação da variável |
| **Texto igual, efeito alterado** | corte “até o número de vagas ofertadas no recorte” com mais vagas (91); corte fixo em 2 diante de 3 vagas (01) | a tradução do trecho pode continuar fiel e ficar desatualizada, se tiver explicitado o valor; ou continuar certa, se tiver remetido às tabelas — o que muda é a manutenção |
| **Só numeração ou página** | oito seções renumeradas e subitens digitados que não acompanham (92); quebras de página (01) | toda referência por número ou por página precisa ser revista |
| **Marca de consolidação** | as quatro Retificações | ocorrência nova de LIB-0126 |

3. Seguir as *Dependências* das unidades alteradas — os tipos encontrados: **valor derivado** (LIB-0029),
   **remissão por número** (LIB-0019, LIB-0149), **remissão por nome** (LIB-0031), **regra dita duas vezes**
   (LIB-0047 e LIB-0025; LIB-0110 e LIB-0034), **anáfora** (LIB-0093, LIB-0123), **alcance** (LIB-0023) — e os
   **enunciados das narrativas** que citam as linhas alteradas.
4. Escrever o `retificacoes.md`: o ato, as alterações, os quatro grupos, o roteiro específico e a
   rastreabilidade.

### 3.2 O que uma Retificação pode fazer

- **Alterar** o valor de uma ocorrência; a antiga continua valendo para a versão antiga.
- **Invalidar um reaproveitamento**: trecho igual com efeito diferente, ou que carrega número.
- **Exigir tradução nova**: texto livre retificado; a justificativa do ato.
- **Retirar uma cláusula**: a seção de atendimento à pessoa com deficiência sai do 92/2026. A retirada se
  comunica **sem concluir que o direito deixou de existir**: o que a lei garante não depende da cláusula
  (auditoria, §13.3).
- **Ter vigência futura**: dois documentos publicados, um vigente (01/2026, v3).

### 3.3 Rastreabilidade das versões

Cada tradução guarda Publicação, hash do conteúdo e hash do documento. A tradução do original não se apaga.
Trecho reaproveitado entre versões só com o registro das duas ocorrências e a conferência de efeito.

## 4. Mudança do compositor

O texto fixo do sistema muda quando uma spec muda o `pdf.py` (49 commits desde 28/08/2026). A cada rodada,
listar os commits de `pdf.py` e `vocabulario_da_regra.py` desde a anterior e conferir as constantes citadas na
*Fonte* das unidades. Texto e sentido mudaram: unidade nova, e a antiga “válida até <commit>”. Só a redação:
*Texto N* novo, com o commit. Editais publicados antes continuam com o texto antigo.

## 5. Lista de conferência de uma rodada

- [ ] Tipo de certame e contexto legal no manifesto (passo 0).
- [ ] Edital real: versão inventariada, atos posteriores **lidos e reconstruídos**, texto em imagem em três registros,
      defeitos do original e tradução em Libras já publicada, com a versão que ela traduz.
- [ ] Narrativas: pendência no enunciado e estado em cada pergunta; nenhuma pergunta com pendência tem gabarito fechado.
- [ ] Métricas: conjunto comparado, denominador e limites escritos ao lado de cada número; nenhuma conclusão de
      tradução ou gravação tirada de coincidência literal.
- [ ] Fontes e anexos guardados, hashes conferidos; versão do compositor registrada ou inferida.
- [ ] `gerar.py` sem avisos: cobertura integral, classificações coerentes.
- [ ] Regras embutidas procuradas em descrições de Evento e instruções.
- [ ] Cada diferença classificada por destinatário, modalidade, condição e consequência — não pela letra.
- [ ] Equivalências `SEMELHANTE` levadas à área; nenhuma tratada como confirmada sem registro.
- [ ] Variáveis tipadas (valor × condição).
- [ ] Unidades novas ou desdobradas justificadas; ocorrências antigas intocadas.
- [ ] Retificações processadas pelos quatro grupos, inclusive nas narrativas.
- [ ] `narrar.py` sem erros; toda linha ligada a uma intenção.
- [ ] Métricas datadas, com a versão do catálogo.
