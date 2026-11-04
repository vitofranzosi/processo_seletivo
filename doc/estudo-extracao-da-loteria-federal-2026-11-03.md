# Validação preventiva da extração da Loteria Federal — diagnóstico e prova de conceito

**Data**: 03/11/2026 · **Base**: `main` em `83cd5863` · **Natureza**: investigação. Nenhum código de
produto, migration, dependência ou spec foi alterado. A POC e as respostas gravadas da Caixa estão em
[`estudo-extracao-da-loteria-federal-2026-11-03/`](estudo-extracao-da-loteria-federal-2026-11-03/).

Os caminhos de código são relativos a `backend/processo_seletivo/`, e os de teste a `backend/tests/`.
Os identificadores `FR-`, `D-` e `SC-` citados são de specs existentes. Os critérios propostos aqui
usam `CA-` e as decisões pendentes `Q`, para não colidir com a varredura de
`test_citacoes_de_requisito.py` quando esta proposta virar spec.

> **Governança.** Este documento registra fatos medidos e uma recomendação. Os achados laterais
> (seção 8) não viram escopo por estarem escritos aqui. Priorizar é do usuário.

---

## 0. Em uma página

**Pergunta principal — é possível impedir automaticamente que se configure uma extração já
realizada?** **Sim, com uma chamada à Caixa e sem inferência.** O endpoint principal devolve o último
concurso realizado (`numero`, `dataApuracao`). Um número menor ou igual a ele já foi realizado, e a
consulta por número devolve a data em que foi. É fato publicado pela fonte, e não estimativa.

**A outra metade — incompatível com o congelamento — também já tem regra.** A `102` (mergeada em
30/10) recusa na publicação a extração cuja **data declarada** não é posterior ao fim das inscrições.
Ela confia na data que quem compôs digitou, e nada confere essa data contra o número do concurso.

**Pergunta secundária — até onde se confirma uma extração futura?** **Só até "ainda não realizada".**
Medido em 03/11/2026:

- a API devolve **HTTP 500** para qualquer concurso não realizado: o seguinte (6115) e o 9999 do mesmo
  jeito, e também o 0 e o −1;
- `dataProximoConcurso` vem **vazio** no último concurso, e só aparece preenchido nos anteriores,
  depois do fato;
- o calendário oficial é um **PDF mensal** em `caixa.gov.br`, atrás de proteção antirrobô. Por script
  ele responde com redirecionamento em laço;
- as mudanças de calendário saem em **comunicados em prosa**. A extração 6106, prevista para 04/10,
  foi antecipada para 03/10 por causa da eleição, e a página de cronograma que o comunicado cita
  devolve 404.

Número → data prevista **não é verificável por máquina** de forma estável. A data futura continua
sendo declaração humana, e só se confirma quando a extração acontece.

**O fluxo atual aceita o concurso de 2015 até o dia do sorteio** (seção 1.3, confirmado executando o
código). `occurrence` é texto livre e `occurrenceAt` é outro campo, independente dele. A composição
confere a forma, e a publicação confere só a data. A Caixa só é consultada na observação, no dia do
sorteio, quando a recusa já exige Retificação **e** sucessão da relação.

**Menor conjunto de mudanças que evita os dois incidentes:**

1. **Concurso no mesmo dia do fim das inscrições (Edital 72/2026):** já resolvido pela `102`. Nada a
   fazer, salvo a dependência da data declarada, que o item 3 mitiga.
2. **Forma do concurso conferida na gravação, sem rede.** Para a Loteria Federal, só inteiro positivo.
   Hoje `6106-9` (a grafia do próprio comunicado da Caixa) e `Concurso 6115` passam na composição, e a
   API recusa os dois com HTTP 400 no dia do sorteio.
3. **Conferência "já realizado?" na submissão e na publicação do Edital, e na Retificação que mexe no
   método.** A rede fica fora da transação, como `observar_ocorrencia` já faz. O resultado entra puro na
   validação, como `publica_so_a_data` já entra:
   - **realizado** é impeditivo, e a mensagem diz a data;
   - **não realizado** passa, e a mensagem diz o último concurso e a distância;
   - **Caixa sem responder** gera advertência, e o "não conferido" fica na trilha.

Sem migration, sem papel novo e sem dependência nova. A garantia de integridade continua onde está, na
precedência sobre o congelamento, que não depende de rede para valer.

---

## 1. O fluxo atual, reconstituído pelo código

### 1.1 Onde o operador informa o concurso

| Passo | Onde | O que se grava ou confere |
|---|---|---|
| Composição | `interface/templates/interface/_marco.html:393` (método do marco), `compor_classificacao.html:144` (método comum) | `occurrence`: **texto livre**, placeholder `5900`. `occurrenceAt`: escolhido entre os Eventos do Cronograma ou digitado em RFC 3339 (`interface/forms.py:380`) |
| Gravação do rascunho | `editais/domain/perfis.py:542` `_validar_metodo_de_sorteio` | Os sete campos presentes, fonte do vocabulário, `occurrenceAt` legível e com fuso (`:685`), e a ocorrência **terminando em número** (`:746`, `substituicao.derivavel`) |
| Submissão e publicação | `publicacoes/application/publish_edital.py:496` e `:724` → `editais/domain/validation.py:2374` `_extracao_inviavel` | Impeditivo se 00h00 do dia de `occurrenceAt` ≤ fim das inscrições (`102`, FR-2650 a FR-2653). **Lê a data declarada, nunca o número** |
| Retificação | `publicacoes/application/retificacoes.py:723`, `:811` | Mesma regra, como advertência (FR-2656). `drawMethod/occurrence` e `occurrenceAt` são retificáveis (`editais/domain/mutabilidade.py:217`, `:374`) |
| Tela do sorteio, antes de congelar | `sorteios/application/previa.py:216` | Aviso se congelar a partir de agora condena a extração **declarada** (FR-2659). O botão continua disponível |
| Congelamento (publicar relação) | `sorteios/application/relacao.py:69`, `:77` | Exige método completo e inscrições encerradas, e grava `metodo_hash`. **Não consulta a fonte** |
| Observação | `sorteios/application/ocorrencia.py` | Primeira e única ida à Caixa. Grava `OcorrenciaDaFonte` (append-only, única por `(fonte, referência)`, `sorteios/models.py:176`) com `ocorrida_nao_antes_de` = 00h00 de `dataApuracao` |
| Constituição | `sorteios/application/sorteio.py:229` | Recusa se `ocorrida_nao_antes_de` ≤ congelamento (`occurrence_precedes_freeze`), e a mensagem manda retificar e suceder (FR-2662) |

### 1.2 Quando a configuração se torna definitiva, e o que protege depois

- **Na publicação do Edital** o método vira norma publicada. Daí em diante, mudá-lo é Retificação.
- **No congelamento** a relação grava o `metodo_hash` da versão que cita
  (`sorteios/domain/metodo.py:76` `conferir_compromisso`). Uma Retificação posterior **não** muda o
  método sob o qual aquela relação se comprometeu, e o sorteio confere o hash.
- **Na observação** o material bruto fica gravado em linha append-only. Uma segunda observação devolve
  a mesma linha (`ocorrencia.py:61`), e uma correção posterior da Caixa não reescreve nada.
- **Na constituição** a ordem deriva de relação, ocorrência e método já fixados, e o `Sorteio` também
  é append-only.

**A integridade da referência depois de publicada já está garantida**, e por duas camadas que não
dependem da Caixa estar no ar: o hash do método na relação e a precedência medida pela data que a
fonte publicou. O que falta é **prevenção**: avisar no dia da composição, e não no dia do sorteio.

### 1.3 Como um concurso de anos antes é aceito hoje — confirmado executando o código

Script em `scratchpad`, contra o código da `main`, sem rede e sem banco. A resposta da Caixa usada é
a gravada em 03/11:

```
1. composição: método com concurso 5000 e data 06/12/2026 ACEITO
2. publicação (102): inviavel = False -> nenhum achado
3. observação: material True não antes de 2015-08-26 00:00:00-03:00 | sorteio recusa (<= congelamento)? True
4. concurso ainda não realizado (HTTP 500): indisponivel= False falha_de_acesso= True
5. forma '6106-9' derivável: True -> seguinte 6106-10
```

O caminho é este:

1. O concurso `5000` com `occurrenceAt` em 06/12/2026 passa na gravação, porque termina em número.
2. Passa também na publicação: a `102` lê a data, e a data é posterior ao fim das inscrições.
3. A relação é congelada normalmente.
4. No dia do sorteio, a observação busca o 5000. A Caixa devolve `dataApuracao: 26/08/2015`, e a linha
   é gravada para sempre.
5. A constituição recusa por precedência.

A saída exige Retificação **e** relação nova, com o cronograma publicado já correndo.

**Origem provável do número antigo.** O reaproveitamento copia o método inteiro, número e data
(`editais/domain/reaproveitamento.py:156` para o marco, `:327` para o método comum). Com o Cronograma
atualizado, a `102` cobra a data antiga, e quem compõe corrige a data, escolhendo o Evento novo no
seletor. O número não é cobrado por nada e fica o do Edital de origem. Não há no repositório registro
do incidente que confirme essa origem; a digitação errada percorre o mesmo caminho.

**Dois incidentes, uma lacuna.** O Edital 72/2026 declarou 6113 em 28/10, e a Caixa confirma que o
6113 foi em 28/10/2026: número e data eram coerentes, e o defeito era o cronograma, hoje coberto pela
`102`. O concurso antigo é o caso inverso, com data plausível e número errado. **A lacuna comum é que
número e data são declarados separadamente e nada os cruza com a fonte antes do sorteio.**

### 1.4 O que já existe, e o que falta

| Proteção | Existe? | Onde |
|---|---|---|
| Método completo, fonte e regras de vocabulário fechado | sim | `perfis.py:542` |
| Referência termina em número | sim | `perfis.py:746` |
| Referência que a **Caixa** aceita (inteiro) | **não** | — |
| Data declarada posterior ao fim das inscrições | sim, na publicação | `validation.py:2374` (102) |
| Número declarado ainda não realizado | **não** | — |
| Número coerente com a data declarada | **não**, e não é verificável por máquina (seção 3) | — |
| Aviso antes de congelar | sim, pela data declarada | `previa.py:216` |
| Recusa no sorteio por precedência real | sim | `sorteio.py:229` |
| Método imutável sob a relação congelada | sim | `metodo_hash` |
| Divergência entre data realizada e declarada | **não é dita** | — |

**As telas e operações que precisam da mesma regra** são as que já compartilham a da `102`, e pelo
mesmo motivo (FR-2650): revisão da composição (`interface/views.py:1144`), submissão e publicação
(`publish_edital.py:496`, `:724`), Retificação (`retificacoes.py:723`, `:811`), tela do sorteio antes
de congelar (`previa.py:216`) e, para a forma, a gravação do rascunho (`perfis.py`).

---

## 2. A API da Caixa, medida

Todas as chamadas foram feitas em **03/11/2026, entre 21:54 e 22:03 UTC** (18:54 a 19:03 em
Brasília), com `curl` sem cabeçalho próprio e 2 s entre chamadas. Foram 24 chamadas ao todo, e nenhum
bloqueio foi observado na API. A forma de chamar do adaptador (`urllib`, sem User-Agent) foi conferida
à parte e recebeu o mesmo 200 e o mesmo 500. Os corpos, recortados, estão em `respostas/`.

Base: `https://servicebus2.caixa.gov.br/portaldeloterias/api/federal`

| # | Caso | URL | HTTP | Corpo relevante | Interpretação |
|---|---|---|---|---|---|
| 1 | Último | `/federal` | 200 | `numero 6114`, `dataApuracao 01/11/2026`, `numeroConcursoProximo 6115`, `dataProximoConcurso ""`, 5 bilhetes | Fato: o último realizado é o 6114. O próximo **número** é anunciado, e a **data não** |
| 2 | Anterior | `/federal/6113` | 200 | `28/10/2026`, `dataProximoConcurso 01/11/2026` | Realizado. A data do seguinte aparece só depois que ele acontece |
| 3 | Anos antes | `/federal/5000` | 200 | `26/08/2015`, local "Caminhão da Sorte" | Realizado, com data |
| 3b | Primeiro | `/federal/1` | 200 | `15/09/1962` | O histórico inteiro está disponível |
| 3c | Âncora do E2E | `/federal/6098` | 200 | `06/09/2026` | Confere com `doc/achado-fonte-real-do-sorteio-sem-gatilho.md` |
| 3d | Antecipado | `/federal/6106` | 200 | `03/10/2026` | O comunicado previa 04/10. A API registra o que aconteceu |
| 4 | Seguinte | `/federal/6115` | **500** | `"Ocorreu um erro inesperado."`, com 404 interno em `exceptionMessage` | **Não distingue** "ainda não" de erro |
| 5 | Alguns à frente | `/federal/6118`, `/6200` | **500** | idem, 404 interno | idem |
| 6 | Muito distante | `/federal/9999` | **500** | idem, 404 interno | idem |
| 6b | Fora da faixa | `/federal/99999` | **500** | idem, **412** interno | idem |
| 7 | Zero e negativo | `/federal/0`, `/-1` | **500** | idem, 404 interno | Mesma resposta de um futuro válido |
| 7b | Texto | `/federal/abc` | 400 | `BuscarConcurso(Int32)` sem parâmetro | Só inteiro é aceito |
| 7c | Com dígito | `/federal/6106-9` | 400 | idem | **A grafia do comunicado da Caixa não serve à API** |
| 7d | Zeros à esquerda | `/federal/006114` | 200 | o 6114 | Normalizável |
| 7e | Decimal | `/federal/6114.0` | 404 | página HTML do IIS | Outro servidor responde, e com HTML |
| 8 | Outras rotas | `/home/ultimos-resultados` | 500 | erro genérico | Indisponível nesse momento |
| 8b | | `/federal/proximoConcurso` | 400 | tratado como número | Não existe |
| 8c | | `/resultados/federal` | 404 | | Não existe |

**Campos que parecem úteis e não são:**

- `ultimoConcurso` é `true` em **todas** as respostas, inclusive a de 1962.
- `indicadorConcursoEspecial` é `1` em todas, inclusive a 6104 (27/09, "Enricou", com prêmio de
  R$ 1,35 mi). Extração especial não se identifica pela flag.
- `dataProximoConcurso` só vem preenchido em concurso cujo seguinte já aconteceu.

**Tempo.** De 0,12 a 0,69 s por chamada. O adaptador usa 10 s e 3 tentativas
(`SORTEIO_FONTE_TIMEOUT_SEGUNDOS`, `SORTEIO_FONTE_TENTATIVAS`).

**Bloqueio.** As respostas trazem cookies `__uzma`/`__uzmb`, típicos de gerenciador de robôs. A API
respondeu normalmente. O site institucional (`caixa.gov.br`), não: o PDF do cronograma, a página de
comunicados e a home das loterias devolvem 302 para o próprio endereço quando a chamada vem de script.

**O que não foi medido.** Indisponibilidade real da API. Não houve queda durante a sessão, e
provocá-la não cabe. Timeout e corpo inesperado estão na POC como respostas simuladas.

---

## 3. A confirmação de concursos futuros

| Estado | Como se sabe | Fonte | Confiável para decidir? |
|---|---|---|---|
| Comprovadamente realizado | `numero ≤ último` e a consulta devolve data e bilhetes | API | **Sim** |
| Anunciado como próximo | `numero == numeroConcursoProximo` do último | API | Sim quanto ao número; **não diz a data** |
| Futuro com data oficial | Cronograma mensal em PDF e comunicados | `caixa.gov.br` | **Não por máquina**: PDF atrás de proteção antirrobô, prosa, mudanças avulsas e link oficial quebrado |
| Futuro só pela sequência | `numero > último` | API | Não. Diz só "ainda não realizado" |
| Desconhecido | 5xx no endpoint principal, timeout, corpo de outra forma | — | Não. **Nunca vira "válido"** |

**Mudanças de calendário só se descobrem lendo comunicado.** A página de comunicados, lida no
navegador em 03/11, registra:

- a mudança dos sorteios de sábado para domingo, às 11h, desde 19/07/2026;
- a antecipação da extração 6106 de 04/10 para 03/10, pela eleição;
- a operação de julho sem venda de bilhetes, com os sorteios mantidos;
- a página `regrassorteios.aspx`, que o próprio comunicado indica para consultar o cronograma e que
  devolve 404.

A Caixa também redefine o dia quando a extração cai num feriado, e escreve a extração com dígito
verificador (`6106-9`).

**Seleção assistida de extrações futuras confirmadas não é viável hoje.** Ela exigiria extrair datas
de PDF protegido e de comunicados em prosa. É *scraping* frágil numa operação normativa. Uma "seleção"
dos próximos números sem data não acrescenta confirmação nenhuma ao campo atual, e sugere uma que não
existe.

**O que se pode dizer ao operador com honestidade:** "o concurso N ainda não foi realizado; o último
realizado é o L, em D; o declarado está N − L concursos adiante e a data declarada X dias depois;
confira no calendário oficial". Ele vê a distância e julga, e o sistema não estima.

---

## 4. As regras de negócio, e o instante de cada uma

| Condição | Verificável? | Instante | Severidade proposta |
|---|---|---|---|
| Forma aceita pela fonte (inteiro, para a Loteria Federal) | sim, local | **Gravação do rascunho** | Recusa (é forma, como a da `035`) |
| Extração ainda não realizada | sim, pela API | **Submissão, publicação e Retificação** que altera o método | Impeditivo; advertência se a Caixa não responder |
| Data declarada posterior ao fim das inscrições | sim, local | Publicação (já existe, `102`) | Impeditivo (já é) |
| Número coerente com a data declarada | **não** (seção 3) | — | Mensagem informativa com a distância |
| Ainda não realizada no congelamento | sim, pela API | **Tela do sorteio / congelamento** | Aviso ou recusa: decisão `Q2` |
| Realizada depois do congelamento | sim, pela data publicada | Constituição | Recusa (já é, `sorteio.py:229`) |
| Realizada na data declarada | sim, depois do fato | Observação | Informativo: adiamento ou antecipação |
| Alteração posterior não muda a semente | sim | Congelamento e constituição | Já garantido (`metodo_hash`, append-only) |

**Por que publicação, e não só composição.** O rascunho não é ato: conferir ali é feedback e não
garantia, e a Caixa fora do ar não pode impedir gravar. A publicação é o momento em que o número vira
norma pública, e é a última chance antes de alguém congelar sob ele. A submissão confere de novo,
como já faz com o cronograma (`028`, FR-358).

**A indisponibilidade da Caixa no instante da publicação** gera advertência, nunca confirmação:

1. **Advertência, com o motivo** ("a Caixa não respondeu", ou "respondeu HTTP 500"). Ela não impede
   publicar.
2. **A trilha registra a conferência**, feita ou não feita, no `reason` do evento de publicação já
   existente: o resultado, o último concurso observado e o instante. Não exige tabela nova.
3. **A conferência se repete na tela do sorteio, antes do congelamento.** Ali o fato decide, e não a
   previsão.
4. **Se mesmo assim passar**, a recusa no sorteio continua valendo, como hoje. Uma Caixa fora do ar
   **não piora** nada em relação a hoje.

Recusar a publicação por queda de terceiro trocaria um erro evitável por um ato legal com prazo preso
a um serviço que o Ifes não controla. E exigiria um processo paralelo de "ciência" que o GPS não tem.
Não há papel novo: quem já pode publicar publica, e a advertência fica no mesmo lugar das outras.

---

## 5. Experiência do operador

### A. Campo atual com validação automática — **recomendada**

- O campo continua, e o rótulo passa a dizer o que se espera: "Número do concurso (só o número, como
  6115)".
- Na gravação, uma recusa de forma diz o que está errado: "`6106-9`: informe o concurso sem o dígito
  verificador — 6106".
- Na revisão e na publicação aparece um destes três desfechos, com as mensagens da POC (seção 6.2):
  - o concurso já realizado, com a data, recusa;
  - o concurso não realizado é informado, com o último realizado e a distância;
  - a Caixa sem responder gera advertência.
- Custo: um método novo no adaptador, uma função pura, um achado novo, resolvido fora da transação em
  três chamadores, e uma linha na trilha.
- Confiabilidade: depende da API só para **prevenir**. A integridade não depende dela.

### B. Seleção assistida de extrações futuras — **não viável hoje**

- Exigiria número → data previsto de fonte máquina-legível. Ela não existe (seção 3).
- Construí-la sobre o PDF ou os comunicados acrescentaria *scraping*, proteção antirrobô e prosa à
  operação normativa, e precisaria de manutenção a cada mudança de layout.
- Uma lista "próximos concursos" só com números aparentaria confirmação sem ter nenhuma.

### A+ (opcional): sugestão do número a partir da data

Não se recomenda: estimar o número pela data é exatamente a inferência por dia da semana que a
investigação exclui, e a antecipação da 6106 mostra o custo.

**O que o operador entende, em cada caso** (pedido da tarefa):

| Ele precisa saber | Onde a mensagem diz |
|---|---|
| Qual concurso está selecionando | Número normalizado, ecoado na mensagem |
| Quando a extração ocorrerá | A data **declarada**, dita como declarada. A Caixa não a confirma, e a mensagem diz isso |
| Se é compatível com o congelamento | Achado da `102`, que já existe |
| Por que foi recusada | "já realizado em DD/MM/AAAA" ou "forma que a Caixa não aceita" |
| O que corrigir | "declare um concurso posterior ao L, de D, que ocorra depois do fim das inscrições" |

---

## 6. Prova de conceito

### 6.1 O que ela é

[`conferencia.py`](estudo-extracao-da-loteria-federal-2026-11-03/conferencia.py) usa só a biblioteca
padrão e tem três partes:

- `situacao(referencia)` faz no máximo duas chamadas e devolve `REALIZADA`, `NAO_REALIZADA`,
  `DESCONHECIDA` ou `FORMA_INVALIDA`;
- `conferir(situacao, declarada_em)` é pura e devolve recusa, advertência ou conferida, com a
  mensagem;
- `conferir_realizacao(...)` é o aviso de adiamento ou antecipação, para o dia do sorteio.

[`test_conferencia.py`](estudo-extracao-da-loteria-federal-2026-11-03/test_conferencia.py) tem 39
casos, todos sobre as respostas gravadas e sem rede:

```
cd backend && uv run pytest -p no:django -p no:cacheprovider \
    ../doc/estudo-extracao-da-loteria-federal-2026-11-03/test_conferencia.py
39 passed in 0.04s
```

Ao vivo, em 03/11/2026 às 19:03 (Brasília):

```
$ python3 -I conferencia.py 5000 2026-12-06
RECUSA draw_occurrence_already_drawn
O concurso 5000 da Loteria Federal já foi realizado, em 26/08/2015. A semente precisa vir de uma
extração que ainda não aconteceu quando a relação for congelada. O último concurso realizado é o
6114, de 01/11/2026: declare um concurso posterior a ele, que ocorra depois do fim das inscrições,
conferindo número e data no calendário oficial da Caixa.

$ python3 -I conferencia.py 6116 2026-11-08
CONFERIDA draw_occurrence_not_drawn_yet
Concurso 6116: ainda não realizado. O último realizado é o 6114, de 01/11/2026; o declarado está 2
concurso(s) adiante, e a data declarada, 08/11/2026, 7 dia(s) depois. A Caixa não publica a data de
concursos futuros: confira no calendário oficial que o concurso 6116 é o de 08/11/2026.
```

### 6.2 Por que a decisão sai do endpoint principal

A consulta pelo número não separa "ainda não" de "o serviço falhou": as duas são HTTP 500. O último
realizado separa. Com `N > último`, o concurso **não foi realizado no instante da consulta**, e isso é
fato. Com `N ≤ último`, ele foi, e a segunda chamada só acrescenta a data. Um 500 no endpoint
principal é `DESCONHECIDA`, e nada se afirma.

---

## 7. Pontos concretos de alteração (para a spec, não feitos)

| # | Arquivo | Mudança |
|---|---|---|
| 1 | `sorteios/infrastructure/fontes/__init__.py` | A porta `FonteExterna` ganha `situacao(referencia)` e `forma_da_referencia`. O padrão é `DESCONHECIDA` e sem forma própria, de modo que fonte sem suporte nunca afirma nada |
| 2 | `sorteios/infrastructure/fontes/loteria_federal.py` | Implementa as duas, com `ENDERECO_DO_ULTIMO` e a lógica da POC. `FonteDeTeste` e `FonteDeTesteSoData` respondem por tabela (`MATERIAL` já é o padrão), para o roteiro e a suíte sem rede |
| 3 | `sorteios/domain/` (junto de `viabilidade.py`) | `conferir(situacao, declarada_em)` pura, com o mesmo desenho de `limite_previsto` e `inviavel` |
| 4 | `editais/domain/perfis.py:746` | `_validar_forma_da_ocorrencia` pergunta também a forma da **fonte**. Desligada na Retificação de acervo, como a FR-514 já desliga a sexta guarda |
| 5 | `editais/domain/validation.py` (ao lado de `_extracao_inviavel`, `:2374`) | Achado novo `EXTRACAO_JA_REALIZADA`. `validate_for_publication` recebe `situacoes` resolvidas, como recebe `marcos_sorteados`, e marcos já sorteados não são conferidos |
| 6 | `publicacoes/application/publish_edital.py:496`, `:724` | Resolve as situações **antes** de `command_context()`, e grava a conferência no `reason` da trilha |
| 7 | `publicacoes/application/retificacoes.py:723`, `:811` | Idem, só quando o método muda |
| 8 | `interface/views.py:1144` | A revisão mostra o achado. A rede aqui pede timeout curto ou conferência sob demanda: `Q4` |
| 9 | `sorteios/application/previa.py:216` e/ou `relacao.py:77` | Conferência antes de congelar: `Q2` |
| 10 | `sorteios/application/ocorrencia.py` | Depois de observar, `conferir_realizacao` informa a divergência de data. Não decide nada |
| 11 | Templates do método | Rótulo e ajuda do campo; resultado da conferência junto do campo, na revisão |

**O que não muda:** a recusa por precedência (`sorteio.py:229`), o `metodo_hash`, as tabelas
append-only, o vocabulário de fontes, as permissões e os papéis. Não há migration.

---

## 8. Riscos e dependências externas — e um achado lateral

**Riscos da proposta**

- **A API muda de forma.** A conferência degrada para `DESCONHECIDA`, que gera advertência e não
  recusa. O teste de contrato E2E já existe e está desligado
  ([achado de 10/09](achado-fonte-real-do-sorteio-sem-gatilho.md)). Ligá-lo num gatilho agendado vale
  também para esta conferência.
- **A API fica fora por dias.** As publicações saem com advertência registrada, e a conferência na
  tela do sorteio e a recusa por precedência continuam. Nada fica pior que hoje.
- **Falso positivo de "realizado".** Exigiria o endpoint principal devolver um número **maior** que o
  real. Não foi observado. A regra recusa só o que a própria Caixa disse ter realizado.
- **Rede dentro de tela.** A revisão de composição é renderizada muitas vezes. Consultar a cada render
  é carga sobre a Caixa e latência para o usuário (`Q4`).
- **A data continua declarada.** Um número coerente com a sequência e uma data errada (por exemplo
  6116 declarado para 22/11, e a Caixa o realiza em 08/11) passam na publicação. O aviso antes de
  congelar (`Q2`) pega isso se o dia real cair antes do congelamento. Se cair depois, o sorteio vale
  com a extração real, e a data publicada no PDF fica errada sem mudar o resultado: é divergência
  documental, e o item 10 da seção 7 a torna visível.

**Achado lateral — o adaptador trata "concurso ainda não realizado" como falha de acesso.**
`urllib` levanta `HTTPError` para o 500 da Caixa, que é subclasse de `URLError`
(`loteria_federal.py:52`), e o desfecho é `falha_de_acesso`. Confirmado no item 4 da seção 1.3. As
consequências:

- o caminho `indisponivel` (200 sem bilhetes), que `test_falha_de_acesso_a_fonte.py:118` exercita,
  **não é o que a Caixa devolve** para extração que não houve;
- a guarda `occurrence_not_due_yet` (`ocorrencia.py:94`) nunca dispara com a fonte real;
- a cadeia de substituição (`OCORRENCIA_SEGUINTE_DA_MESMA_FONTE`) **nunca avança** com a fonte real:
  uma extração cancelada fica em "não foi possível falar com a Caixa" para sempre, e a mensagem
  diagnostica errado (rede, quando é ausência).

O lado é o seguro, porque nunca queima a extração declarada. Mas a regra de substituição publicada em
todo Edital é, na prática, inexecutável contra a Caixa. Distinguir "500 com 404 interno depois de
`occurrenceAt`" de falha de rede é decisão normativa, porque consome a cadeia append-only. Por isso
fica registrado, e não proposto.

---

## 9. Matriz de testes e critérios de aceite

Todos rodam com a fonte substituída: respostas gravadas em `respostas/`, `urlopen` substituído como
em `tests/unit/duvidas/test_adaptador_openrouter.py`, ou `FonteDeTeste` por tabela. **Nenhum depende
da Caixa.**

| # | Cenário | Dado | Esperado | Camada |
|---|---|---|---|---|
| CA-1 | Concurso histórico | `5000`, último 6114 | Publicação recusada, com "realizado em 26/08/2015" | domínio + publicação |
| CA-2 | Último realizado | `6114` | Recusada, com "01/11/2026" | domínio |
| CA-3 | Próximo anunciado | `6115` | Conferida, com "próximo anunciado" e uma chamada só | adaptador |
| CA-4 | Futuro sem data oficial | `6200` | Conferida, com a distância e "confira no calendário"; nunca diz "data confirmada" | domínio |
| CA-5 | Futuro "confirmado" | — | Não existe confirmação automática. O teste prova que **nenhuma** mensagem afirma data confirmada | domínio |
| CA-6 | Data antes do congelamento | `occurrenceAt` no dia do fim das inscrições | Impeditivo da `102` (já coberto em `tests/unit/editais/test_extracao_inviavel.py`) | domínio |
| CA-7 | Data fora do cronograma | `occurrenceAt` ≤ fim das inscrições | Idem ao CA-6. "Compatível com o Edital" além disso não é regra escrita (`Q5`) | — |
| CA-8 | Falha de conectividade | `URLError` ou timeout no endpoint principal | Advertência "não foi possível conferir… não confirma"; publica; trilha diz "não conferida" | adaptador + publicação |
| CA-9 | Erro do serviço | 500 ou 503 no principal; HTML no lugar de JSON; 200 sem bilhetes; data em outro formato; `numero` como texto | Advertência. Nunca recusa, nunca conferida | adaptador |
| CA-10 | Mudança de calendário | 6106 declarada em 04/10, realizada em 03/10 | Na observação: "realizou em 03/10/2026, 1 dia antes". A precedência decide como hoje | aplicação |
| CA-11 | Alteração depois do congelamento | Retificar `occurrence` com relação congelada | O sorteio usa o método do `metodo_hash` (já coberto). A Retificação confere o número novo | integração |
| CA-12 | Contornar o frontend | Chamar `publish_edital` direto com `5000` | Mesma recusa: a regra mora no domínio, e a interface só a mostra | integração |
| CA-13 | Armazenado × fonte | `OcorrenciaDaFonte` gravada, e a Caixa responde outra coisa depois | A linha gravada vale. Não há releitura (já coberto pela idempotência de `observar`) | integração |
| CA-14 | Forma | `6106-9`, `Concurso 6115`, `0`, `-1`, `6114.0` | Recusa na gravação, **sem chamada** | domínio |
| CA-15 | Normalização | `006114` | Tratado como 6114 | domínio |
| CA-16 | Carga | Qualquer conferência | No máximo duas chamadas, e uma quando não realizado | adaptador |
| CA-17 | Marco já sorteado | Retificação de Edital com sorteio feito | O marco sorteado não é conferido, porque a extração dele foi realizada por definição | domínio |
| CA-18 | Fonte de demonstração | `SORTEIO_FONTE_DE_DEMONSTRACAO` ligada | O roteiro local mostra recusa e conferida sem rede | quickstart |

---

## 10. Recomendação e elementos para a spec

**Recomendação: alternativa A, em um MVP de três peças:**

1. forma da referência por fonte, conferida na gravação (CA-14, CA-15);
2. conferência "já realizado?" na submissão e na publicação, e na Retificação que muda o método
   (CA-1 a CA-4, CA-8, CA-9, CA-12, CA-16, CA-17);
3. a conferência gravada no `reason` da trilha de publicação.

As duas primeiras fecham o incidente do concurso antigo e a grafia `6106-9`. O do Edital 72 já está
fechado pela `102`. A terceira dá lastro: o que a Caixa disse, e quando.

**Para uma segunda etapa**, cada uma com decisão própria:

- conferência antes de congelar (`Q2`);
- aviso de divergência de data na observação (CA-10);
- o achado lateral da seção 8;
- o gatilho agendado do E2E.

**Decisões que só o usuário toma:**

- **Q1.** Caixa sem responder na publicação: advertência (recomendada) ou impeditivo com nova
  tentativa?
- **Q2.** Concurso já realizado no momento de congelar: aviso (como a FR-2659 decidiu para a
  previsão) ou recusa? Aqui é fato e não previsão, e a relação congelada é append-only, o que pesa a
  favor da recusa.
- **Q3.** Na Retificação, concurso realizado num marco ainda não sorteado: impeditivo (a Retificação
  está **introduzindo** o erro) ou advertência (como a `102` fez, para não fechar a saída)? Recomenda-se
  impeditivo só quando a própria Retificação altera `occurrence`.
- **Q4.** Na revisão da composição, consultar a cada render, sob demanda (botão "conferir na Caixa")
  ou só na submissão?
- **Q5.** "Compatível com o cronograma e as disposições do Edital" vai além de "depois do fim das
  inscrições"? Por exemplo, antes da data de divulgação do resultado preliminar. Hoje não há regra
  escrita; criar uma é norma nova.
- **Q6.** O achado lateral da seção 8 entra em alguma spec, e em qual?

**Elementos para a spec:**

| Elemento | Conteúdo |
|---|---|
| Escopo | Conferência preventiva do número da extração, sem tocar a garantia de integridade existente |
| Fora do escopo | Confirmação automática de data futura; seleção assistida; novas fontes; mudança na regra de substituição |
| Atores | Quem compõe (gravação), quem submete e publica (publicação), quem retifica. Sem papel novo |
| Entidades | Nenhuma nova. A situação da referência é valor transitório, e o registro vai na trilha existente |
| Dependências | API pública da Caixa (`/federal`, `/federal/{n}`), já usada pelo adaptador |
| Specs relacionadas | `021` (FR-013, FR-015, FR-016, FR-077), `035` (FR-512 a FR-516, forma), `102` (FR-2647 a FR-2665, viabilidade), `028` (FR-341, FR-358, instante do ato) |
| Critérios de aceite | CA-1 a CA-18 acima |
| Sucesso mensurável | Nenhum Edital publicado com concurso que a Caixa já registrava como realizado no instante da publicação, conferível pela trilha |

---

**Fontes externas consultadas**

- API: `servicebus2.caixa.gov.br/portaldeloterias/api/federal` — as chamadas da seção 2.
- [Comunicados importantes — Loterias CAIXA](https://www.caixa.gov.br/loterias/comunicados-importantes/Paginas/default.aspx),
  lidos no navegador em 03/11/2026.
- [Página da Loteria Federal](https://loterias.caixa.gov.br/Paginas/Federal.aspx): extrações
  regulares e a regra do feriado.
- Cronogramas mensais em PDF, como
  [setembro de 2026](https://www.caixa.gov.br/Downloads/caixa-loterias/Cronograma_09_Setembro_2026.pdf)
  e [julho de 2026](https://www.caixa.gov.br/Downloads/caixa-loterias/Cronograma_07_Julho_2026.pdf):
  achados pela busca. O de novembro não foi lido, porque o download exige aprovação e, por script, a
  proteção antirrobô responde com redirecionamento em laço.
