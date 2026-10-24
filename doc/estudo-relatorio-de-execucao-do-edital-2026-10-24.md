# Relatório executivo de encerramento — avaliação de viabilidade e proposta de spec

Levantamento feito em **24/10/2026** sobre a `main` em `5a08f409`, a partir da proposta do usuário
*"GPS — Avaliação de viabilidade e proposta de especificação: Relatório Executivo de Encerramento do
Processo Seletivo"*.

> **Implementação (24/10/2026).** Com a v2 aprovada e os ajustes de precisão, a feature virou a spec
> [`099-relatorio-do-edital`](../specs/099-relatorio-do-edital/spec.md) e foi implementada. Os PDFs
> gerados pelo código estão em
> [`relatorio-de-acompanhamento.pdf`](estudo-relatorio-de-execucao-do-edital-2026-10-24/relatorio-de-acompanhamento.pdf)
> e [`relatorio-de-encerramento.pdf`](estudo-relatorio-de-execucao-do-edital-2026-10-24/relatorio-de-encerramento.pdf).

> **Rodada 2 (24/10/2026).** Depois da avaliação da maquete v1, a comunicação executiva, a
> terminologia e o cenário foram revistos em
> [`rodada-2.md`](estudo-relatorio-de-execucao-do-edital-2026-10-24/rodada-2.md), com a
> [maquete v2](estudo-relatorio-de-execucao-do-edital-2026-10-24/maquete-v2.pdf). A §6 deste
> estudo foi **substituída** por
> [`spec-proposta-v2.md`](estudo-relatorio-de-execucao-do-edital-2026-10-24/spec-proposta-v2.md).
> O restante fica como registro da rodada 1.

> **Não abre spec, não cria requisito e não decide nada.** Os identificadores deste documento
> (`R-`, `CA-`, `Q-`) são locais e provisórios, e de propósito não usam `FR-`/`SC-`/`D-`: a
> numeração real nasce no `/speckit-specify --number N`, se o usuário decidir avançar. As decisões
> de produto estão reunidas na §8 e são do usuário.

---

## 0. Em uma página

**A hipótese chega tarde no domínio e cedo no produto.**

- **Tarde no domínio**: o encerramento formal já existe. Edital e Processo têm estado `ENCERRADO`,
  alcançado por ato motivado, auditado e append-only (`processos/application/finalizacao.py`), e o
  Processo só encerra com todos os Editais em estado final (RC-118, decisão de 28/09). Um "módulo de
  encerramento" (Alternativa C) reconstruiria uma máquina de estados que já está lá.
- **Cedo no produto**: não encontrei no repositório nenhum certame real conduzido de ponta a ponta
  pelo GPS — o teste operacional assistido do 28/2026 ainda espera quem o faça (`DP-18`), e não há
  carga retroativa de Edital (decisão registrada em `doc/decisao-sem-carga-retroativa.md`). **Hoje
  não existe um único Edital encerrado com dados reais sobre o qual o relatório pudesse ser gerado,
  nem um destinatário que já tenha pedido por ele.**

**Quatro fatos do código decidem o desenho:**

1. **Tudo o que se quer contar pende do Edital, não do Processo.** Inscrição, ordenação, resultado
   divulgado, ocupação e convocação têm FK para `Edital`; o `ProcessoSeletivo` não tem data, vaga
   nem prazo. A unidade do relatório é o **Edital**; o do Processo é a reunião dos Editais dele.
2. **Encerrado não congela.** O único efeito do estado do Edital sobre os atos é parar o
   recebimento de inscrições (`inscricoes/domain/periodo.py`, `ESTADOS_QUE_RECEBEM`).
   `ensure_edital_accepts_changes` só é chamado pela própria finalização. Recurso, suplência,
   desfecho de convocação, nova apuração e nova publicação de resultado continuam gravando depois do
   encerramento. Um relatório "de encerramento" pode envelhecer no dia seguinte.
3. **Encerrar o Edital não confere nada.** `ensure_edital_can_be_closed` exige só `PUBLICADO`; a
   tela de confirmação calcula pendências apenas para submeter e publicar. Encerra-se Edital com
   recurso aguardando julgamento, apuração obsoleta ou convocação em curso.
4. **A camada de indicadores já foi especificada.** A `040` definiu catorze indicadores com
   fórmula, denominador, fonte e momento de confiabilidade (§9), e as quatro grafias de ausência
   (§13). A camada de resultado — indicadores 7 a 13 — está **registrada e não entregue**
   (`D-011` daquela spec). Um relatório de execução é, em boa parte, essa camada lida por Edital.

**Recomendação: experimentar, não implementar ainda.** Validar a demanda com uma maquete feita sobre
o certame de demonstração e mostrada a três a cinco destinatários reais; se passar no critério da
§7.1, entregar primeiro a **página de execução do Edital**, com o PDF como a mesma leitura impressa
(Alternativa D com o conteúdo de B), sem estado novo, sem tabela nova e sem fila. O módulo de
encerramento (C) fica descartado como está formulado; o que dele sobrevive — conferir pendências
antes de encerrar — é achado sobre a `001`, e não escopo do relatório.

---

## 1. Diagnóstico do GPS atual

### 1.1 O ciclo de vida, como o código o representa

| Fase da proposta | Existe? | Como existe | Onde |
|---|---|---|---|
| Criação e configuração | ✅ | `ProcessoSeletivo` (`EM_ELABORACAO` → `ATIVO`), `Edital` com Perfis, Etapas, Cronograma, Modalidades | `processos/models.py`, `editais/models/` |
| Publicação e anexos | ✅ | `Publicacao` + `DocumentoPublicado` (PDF em coluna binária, SHA-256) + `VersaoConsolidada`; autoridade e unidade congeladas na linha | `publicacoes/models.py`, `publish_edital.py` |
| Retificação | ✅ | `Retificacao` com `justification` obrigatória; `AlteracaoNormativa` por caminho (`/schedule/id=…/endAt`), sem valor anterior (deduzido do `base_snapshot`); `ProvenienciaConteudo` | `publicacoes/models_retificacao.py` |
| Inscrições | ✅ | `Inscricao`: **só** `RASCUNHO` e `SUBMETIDA`; `submitted_at`, `profile_id`, `modality_id` | `inscricoes/models.py` |
| Homologação de inscrição | ❌ | **não existe como ato nem como estado.** `publicacoes.Homologacao` é a homologação da revisão do Edital | — |
| Cancelamento/desistência de inscrição | ❌ | não existe | — |
| Etapas de avaliação | ✅ | Etapa no snapshot (`content["stages"]`); `Avaliacao` (rascunho/concluída, reabrível); `ResultadoEtapa` append-only com `HABILITADA`/`ELIMINADA` e origem `AVALIACAO`/`OCORRENCIA`/`RECURSO`/`REGULARIZACAO` | `avaliacoes/`, `resultados/` |
| Conclusão de etapa | ❌ | **não há ato com instante.** Só o planejado no cronograma, ou o máximo de `consolidado_em` | — |
| Ausência em prova | ⚠️ | `ResultadoEtapa` de origem `OCORRENCIA` com motivo em **texto livre** — não há categoria "ausente" | `resultados/application/ocorrencia.py` |
| Classificação | ✅ | `AtoDeOrdenacao` por (Perfil, marco, lista) + `PosicaoNaOrdem`; `Corte` + `ItemDoCorte`; sorteio como origem | `classificacao/models.py` |
| Resultado publicado | ✅ | `PublicacaoResultado` `PRELIMINAR`/`DEFINITIVA` por marco e lista, sucessão, PDF guardado; `SituacaoDivulgada` só `CLASSIFICADA`/`SEM_POSICAO` | `divulgacao/models.py` |
| "Aprovado" | ❌ | o termo não existe no domínio, e a varredura de vocabulário o proíbe em telas de resultado | `tests/test_vocabulario_do_resultado.py` |
| Recursos | ✅ | `Recurso`, `JuizoDeAdmissibilidade`, `DecisaoRecurso` (`INDEFERIDO`, `CORRECAO_FIXADA`, `REAVALIACAO_DETERMINADA`, `PROVIDENCIA_A_JUSANTE`); situação **derivada** | `recursos/models.py`, `recursos/application/selectors.py` |
| Ocupação de vagas | ✅ | `ApuracaoDeOcupacao` (`publicadas`, `efetivas`, `ocupadas`; `faltando` é propriedade), com causas de obsolescência | `ocupacao/` |
| Convocação | ✅ | `Convocacao` (`VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR`) + `DesfechoDaConvocacao` (sete espécies) | `convocacao/models.py` |
| Requerimento de matrícula | ⚠️ | só onde o Edital declara `requerimento_momento` | `requerimentos/` |
| Matrícula efetivada | ❌ | **não existe, por decisão**: o sistema gera um `.xlsx` e guarda só o registro de que gerou (`GeracaoDeArquivo`) | `matriculas/models.py` |
| Cadastro de reserva por pessoa | ❌ | só a declaração do Perfil (`reserve_type`, `reserve_limit`) | `editais/models/perfis.py` |
| Encerramento | ✅ | Edital `PUBLICADO → ENCERRADO`; Processo `ATIVO → ENCERRADO` com Editais finais; `AtoAdministrativo` com motivo, autor e instante; `desfechos()` lê a data | `processos/domain/finalizacao.py`, `processos/application/selectors.py` |
| Suspensão / reabertura | ❌ | não existem estados para isso. Estados finais são terminais | `finalizacao.py` |

### 1.2 Como o sistema sabe que um processo terminou

Pelo **ato**, e só por ele. Não há derivação de "concluído" a partir de fatos — e isso está certo:
o domínio recusa declarar evento "concluído" (`editais/domain/cronograma.py` só aceita `PLANEJADO` e
`CANCELADO`), e a fase de um Evento é derivada do relógio (`editais/domain/fase_do_evento.py`).

Três consequências que a proposta não podia saber:

- **O ato não verifica a substância.** Encerrar o Edital exige `PUBLICADO` e nada mais. Não há
  conferência de resultado definitivo, de recurso pendente, de apuração obsoleta, de convocação com
  prazo em curso. A Supervisão, inclusive, **silencia** os sinais de trabalho pendente quando o
  Edital é encerrado (`interface/supervisao.py`, `EDITAL_PAROU_POR_ATO`), mas mantém o de recurso.
- **O ato não congela.** Depois de `ENCERRADO`, só as inscrições param. O resto do ciclo continua
  gravando. Não é defeito evidente — suplência depois do encerramento pode ser exatamente o que a
  instituição quer —, mas significa que **"encerrado" não é "fato consolidado"**.
- **Retificação depois do resultado** é possível enquanto o Edital está publicado, e ela não
  reescreve o relacional (`doc/decisao-mutabilidade-normativa.md`; memória do projeto
  *retificação não reescreve o relacional*). O que vale é a versão consolidada vigente em cada
  instante.

### 1.3 Superfícies que já agregam

| Superfície | Nível | O que mostra | Porta |
|---|---|---|---|
| Visão Geral (`040`/`041`) | escopo | Editais, vagas publicadas, submetidas, em preenchimento, inscrições por vaga, Perfis; quatro grafias de ausência | `visao:consultar` (só `gestor`) |
| Supervisão / Pulso (`022`/`038`) | Processo | submetidas e rascunhos por Edital, últimas 24 h, série diária, próximos marcos, oito sinais de atenção | `pode_supervisionar` (gestão ou presidência) |
| Detalhe do Processo | Processo | Pulso, Editais e situação, pendentes, atos, trilha | qualquer ator do escopo |
| Ocupação, Convocação | recorte | os quatro números por modalidade, convocados, desfechos | gestão/presidência; auditoria lê |
| Resultados da Etapa | Etapa | resultado por inscrição, paginado | presidência ou auditoria |
| Publicações do marco | marco | preliminar/definitivo, sucessão | `resultado:publicar` ou `auditoria:consultar` |
| Trilha do Edital | Edital | atos auditados | `auditoria:consultar` |

**Não existe** leitura que reúna, para um Edital, demanda + etapas + resultado + ocupação +
convocação + recursos + retificações. Os números existem, espalhados por sete telas com quatro
portas diferentes. **Esta é a lacuna real**, e ela é anterior a qualquer PDF.

A trilha do Edital (`auditoria/selectors.py`, `trilha_do_edital`) também **não reúne** publicação
de resultado, sorteio, ato de ordenação e corte — eles são auditados, mas fora dessa leitura.

### 1.4 Documentos e infraestrutura

- **PDF**: motor próprio, sem dependência (`publicacoes/infrastructure/pdf.py`, 5,5 mil linhas).
  `render_documento` é genérico — paginação "Página N de M", brasão, cabeçalho institucional da
  Unidade, saída determinística — e já serve a três documentos: Edital, resultado divulgado
  (`divulgacao/infrastructure/documento.py`) e comprovante de inscrição
  (`inscricoes/infrastructure/comprovante_pdf.py`, gerado sob demanda e **não** guardado). Há
  `_tabela`, `_integridade` (imprime SHA-256) e `MARCA_DE_PREVIA` (marca d'água).
- **Armazenamento**: atos guardam os bytes em `BinaryField`. Arquivo gerencial não tem precedente de
  guarda: o `.xlsx` de matrícula é efêmero e só deixa `GeracaoDeArquivo`.
- **Assíncrono**: não há fila. Tudo é síncrono, ou management command com timer
  (`despachar_avisos`).
- **Unidade (`060`)**: `nome`, `sigla`, `cabecalho`, `local`. Sem campus, endereço ou logotipo
  próprio.
- **Exportação**: só o `.xlsx` de matrícula. Nenhum CSV.
- **Dependências**: Django, DRF, psycopg, openpyxl; acrescentar exige justificativa escrita
  (`backend/pyproject.toml`).

### 1.5 Autorização

Oito papéis literais em `interface/identidade.py` (`PAPEIS`). **Não há papel de leitura gerencial**,
e o próprio código diz que um papel de Diretoria "é decisão institucional, não técnica", pendente na
`040`. `visao:consultar` foi dado só ao `gestor`. Presidência de comissão é vínculo, não papel.

**Os destinatários da proposta — diretor-geral, diretor de ensino, coordenadores — não são usuários
do GPS.** Esse é o argumento mais forte a favor de um PDF, e não a estética: é o único veículo que
chega a quem não tem papel no sistema.

---

## 2. Avaliação crítica da oportunidade

### 2.1 Que problema resolveria

| Hipótese de problema | Evidência no repositório | Juízo |
|---|---|---|
| Quem conduz precisa consolidar à mão para prestar contas à direção | **nenhuma** — não há registro de pedido, de modelo de relatório usado hoje, nem de destinatário | **não validada** |
| Os números do Edital estão espalhados e ninguém os vê juntos | **forte** — sete telas, quatro portas (§1.3); a `040` já mediu a ausência do nível acima | **real**, e independe de PDF |
| Falta formalizar o encerramento | **fraca** — o ato existe, motivado e auditado | **já atendida**; o que falta é o ato conferir algo (§1.2) |
| A direção precisa de um documento para decidir | **nenhuma** — que decisão? oferta do próximo ano, reforço de comissão, revisão de critério? | **não validada**; é a pergunta central da validação |
| Auditoria/controle externo pede o histórico | **parcial** — tudo é append-only e auditado, mas a trilha do Edital não reúne os atos de resultado | o valor estaria em **referências verificáveis**, não em narrativa |

### 2.2 Para quem

Por ordem de plausibilidade:

1. **Presidência e gestão do Processo** — usuários reais do GPS, que hoje montariam a resposta a
   "como foi o 28/2026?" abrindo sete telas. É a persona com dor demonstrável, e é servida pela
   **página**, não pelo PDF.
2. **Direção do campus e de ensino** — destinatários do documento. Valor plausível para planejar a
   oferta seguinte (procura por Perfil, vagas não ocupadas), **não demonstrado**.
3. **Coordenadores de curso/programa** — interessados no recorte do seu Perfil. Hoje o Perfil não
   tem vínculo com curso, e `locality` é texto livre: o recorte só existe se o Perfil for o curso.
4. **Controle interno/auditoria** — valor nas referências (hashes, datas, atos), não nos gráficos.

### 2.3 PDF, painel, ou formalização?

**O valor está na consolidação; o PDF é o canal para quem está fora do sistema; a formalização já
existe.** Separando:

- A **consolidação** é útil já a quem conduz, sem nenhuma demanda externa a validar. Se ela for
  feita como leitura derivada (sem estado novo), o custo de manutenção é o de uma tela.
- O **PDF** só se paga se houver destinatário que o leia. Ele não acrescenta dado, e acrescenta três
  riscos: envelhece (§1.2), sai do controle de acesso, e parece ato oficial.
- A **formalização** acrescentaria estado e transição a um domínio que já tem os dois. O que de fato
  faltaria a um encerramento confiável é conferência de pendências antes do ato — e isso é achado
  sobre a `001`, que o usuário pode querer ou não, e não justificativa para um módulo.

### 2.4 Evolução natural ou complexidade excessiva?

**Evolução natural, se for leitura; complexidade excessiva, se for módulo.** O critério da casa é
o da `022`: *"A necessidade de persistir estado novo durante a implementação é indício de violação de
fronteira."* Um relatório que precise de tabela de snapshot, fila, estado `EM_EMISSAO` ou versionamento
próprio violou essa fronteira.

### 2.5 Hipóteses não validadas

- H1. Alguém hoje produz, à mão, um relatório de encerramento de processo seletivo no Cefor.
- H2. A direção leria um documento de 3–6 páginas sobre um Edital e mudaria alguma decisão por ele.
- H3. Os destinatários preferem documento a acesso de leitura ao sistema.
- H4. O conteúdo útil é o agregado; ninguém precisa da relação nominal no relatório.
- H5. O relatório é por Edital (e não por Processo, nem por ano, nem por curso).

### 2.6 Como validar antes de investir

**Validação barata, sem código de produto** (proposta; a execução é decisão do usuário):

1. Rodar o `seed_demo` e conduzir o Edital de demonstração até o resultado definitivo e a ocupação
   (o percurso já está documentado na memória do projeto: *seed_demo convoca Ana Silva*, *mesa com
   documentos no demo*).
2. Montar **à mão** uma maquete de 3–5 páginas com o conteúdo do MVP (§7), lendo as telas donas —
   o próprio esforço de montagem é a medição da dor de H1.
3. Mostrar a maquete a 3–5 destinatários reais (no Cefor, a equipe é de 2–3 pessoas; incluir a
   direção) com quatro perguntas: *o que você faria com isto? o que falta? o que sobra? em que
   momento você queria receber?*
4. Perguntar à equipe do setor como respondem hoje a "como foi o processo X?" — e-mail, planilha,
   relatório de gestão anual, nada.

O critério de passagem está na §7.1.

### 2.7 A maquete (24/10/2026)

Os passos 1 e 2 estão feitos. A maquete está em
[`estudo-relatorio-de-execucao-do-edital-2026-10-24/maquete.pdf`](estudo-relatorio-de-execucao-do-edital-2026-10-24/maquete.pdf).
São quatro folhas de relatório e uma de condução da conversa, com o mesmo conteúdo em `maquete.html`.
Ela foi montada sobre o Edital 51/2026 de um banco próprio semeado com `seed_demo --dias-atras 20`. O
ciclo foi completado pelos comandos da aplicação: recurso julgado, resultado definitivo, encerramento
e um desfecho de convocação gravado depois do encerramento. Os números saíram das mesmas funções que
as telas usam. Os roteiros estão em `roteiro/`.

**O passo 2 não mediu H1.** Os números foram lidos por roteiro, e não pelas telas, de modo que o
tempo de montagem não diz quanto custaria à mão. Essa medição continua sendo da pessoa do setor.

**O que a montagem confirmou, no dado e não só no código:**

- **§1.2, encerrado não congela.** O sistema aceitou o desfecho de convocação três dias depois do
  encerramento, e o desfecho emitiu uma apuração nova. Os dois aparecem na trilha do Edital depois
  do `ENCERRAR`.
- **§1.2, encerrar não confere.** O Edital encerrou com a vaga reservada (PPP) nunca apurada e com o
  marco do cadastro de reserva sem resultado divulgado.
- **§3.F, ausência não é zero.** A vaga PPP sai *"não apurada"*. Escrever "1 vaga não preenchida"
  afirmaria o que nenhum ato produziu.
- **§3.B, pessoas distintas.** O semeador usa o mesmo CPF para as cinco inscrições, e a contagem
  daria 1. É o defeito do indicador 14 da `040`, materializado.

**O que a montagem acrescentou:**

- A trilha do Edital (`trilha_do_edital`) **não traz o recurso** interposto e julgado, além das
  publicações de resultado que a §1.3 já apontava. A linha do tempo da folha 2 precisou de cada fonte
  lida à parte.
- `recursos_do_edital` + `resumo` devolvem **nome e protocolo do candidato**. O relatório precisa de
  uma contagem própria por espécie, e não do reuso da listagem (R-18).
- `serie_do_edital` só conta envios **dentro do período declarado**. Na demonstração, as inscrições
  foram gravadas fora dele e a série sai vazia. Num certame real isso não ocorre pelo canal do
  candidato, mas o gráfico não deve ser a única forma de dizer o total.
- **Custo**: a leitura inteira fez 115 consultas em 0,12 s, num Edital de 5 inscrições e 2 Perfis.
  Ainda não há medição com volume (RNF-01).
- Com limiar em menos de 3, a supressão (Q-06) apagaria **nove células** da maquete, entre elas
  todas as de recurso e de convocação. A maquete as mostra com `*` para que o destinatário opine
  sobre a perda.

---

## 3. Matriz de viabilidade dos indicadores

Legenda de **disponibilidade**: **E** existe e reutiliza · **P** existe parcialmente · **D**
derivável com segurança · **N** exige registro novo · **X** inviável ou sem sentido hoje.

A unidade de análise é a **inscrição**, salvo indicação. Contagens são `DISTINCT inscricao` sempre
que o mesmo fato possa aparecer em mais de um recorte (ampla e reservada) ou em mais de uma chamada.

### A. Identificação

| Informação | Fonte | Disp. | Confiab. | Esforço | Observação |
|---|---|---|---|---|---|
| Instituição e Unidade | `Publicacao.unidade_*` (congelado na publicação) ou `Unidade` | E | alta | baixo | usar o congelado do primeiro ato, como o PDF do Edital |
| Processo (código, título) | `ProcessoSeletivo` | E | alta | baixo | — |
| Edital (nº/ano, título) | `Edital` | E | alta | baixo | — |
| Autoridade signatária | `Publicacao.signatory_*` | E | alta | baixo | é registro, não assinatura |
| Presidência da comissão | `MembroComissao` `PRESIDENTE` ativo | P | média | baixo | é nominal; pode ter mudado ao longo do certame (`inativado_em`) — **Q-07** |
| "Modalidade do processo" (ingresso, bolsista, servidor…) | — | X | — | — | **não há taxonomia**, e o modelo recusa criá-la por escrito |
| Campus / curso / programa | `PerfilVaga.locality`, nome do Perfil | P | baixa | — | texto livre; só vale se o Perfil *for* o curso |
| Período de realização | 1ª `Publicacao.published_at` → instante do `AtoAdministrativo` de desfecho | D | alta | baixo | é o período **do ato ao ato**, não "da execução" |
| Situação final e data | `desfechos()` | E | alta | baixo | `None` na data quando o ato não é encontrado: dizer sem data, não inventar |
| Instante de referência do relatório | relógio da emissão | D | alta | baixo | **obrigatório**, por causa de §1.2 |

### B. Sumário executivo

| Indicador | Fórmula | Fonte | Disp. | Confiab. | Limitação |
|---|---|---|---|---|---|
| Vagas imediatas publicadas | `Σ profiles[].immediateVacancies` da versão vigente | `VersaoConsolidada.content`; `visao_geral.vagas_do_conteudo` | E | alta | Perfil só com CR tem 0 legítimo |
| Cadastro de reserva | espécie e limite por Perfil | idem | E | alta | `UNLIMITED` não tem número |
| Inscrições submetidas | `COUNT(status=SUBMETIDA)` | `Inscricao`; `visao_geral.contagens_por_edital` | E | muito alta (CHECK) | — |
| Rascunhos não enviados | `COUNT(status=RASCUNHO)` | idem | E | alta | **não é "inscrição iniciada"**: é rascunho que existe; não há data de abandono |
| Pessoas distintas | `COUNT(DISTINCT cpf_normalizado)` das submetidas | `Inscricao` | P | média | CPF declarado, não provado, não único (indicador 14 da `040`, pendente de decisão do usuário) |
| Inscrições por vaga | `Σ submetidas em Perfis com vaga ÷ Σ vagas` | derivado (`040` #6) | D | alta | "não se aplica" sem vaga imediata; nunca média de razões |
| Inscrições homologadas | — | — | **X** | — | o ato não existe. **Não substituir por "submetidas"** |
| Etapas configuradas | `len(stages)` da versão vigente, por Perfil | snapshot | E | alta | Perfis podem ter etapas distintas: dizer por Perfil |
| Retificações publicadas | `COUNT(Retificacao status=PUBLICADA)` | `publicacoes` | E | alta | — |
| Resultados definitivos divulgados | marcos com `PublicacaoResultado` `DEFINITIVA` vigente ÷ marcos declarados | `divulgacao.vigente_do_marco` | D | alta | é a resposta honesta a "o resultado saiu?" |
| Classificados | — | — | **P** | — | ver F; o número existe **por marco**, e somar marcos dupla-conta |
| Duração | desfecho − 1ª publicação, em dias | D | alta | — | só com desfecho; antes, "em execução há N dias" |

### C. Cronograma planejado × retificado × realizado

| Informação | Fonte | Disp. | Confiab. | Observação |
|---|---|---|---|---|
| Cronograma original | `schedule` da 1ª `VersaoConsolidada` | E | alta | — |
| Cronograma vigente | `schedule` da versão vigente | E | alta | — |
| Alterações de prazo | `AlteracaoNormativa` com `target_path` em `/schedule/…`, por Retificação; anterior lido do `base_snapshot` | D | alta | **não existe função pronta** de diff de cronograma entre versões; `interface/views.py::_alteracoes_legiveis` é o precedente |
| Evento cancelado | `status=CANCELADO` no snapshot | E | alta | — |
| Data **efetiva** de um evento | — | **X** em geral | — | o domínio não registra execução de evento, e recusa "concluído" como entrada |
| Realizado, onde há ato | 1º/último `submitted_at`; `PublicacaoResultado.publicado_em`; `Sorteio.executado_em`; `max(ResultadoEtapa.consolidado_em)` por Etapa | D | alta para o ato; **baixa como "data da etapa"** | o que se mostra é *"primeira/última consolidação"*, nunca *"a etapa terminou em"* |
| Atraso / antecipação | — | **X** | — | comparar o planejado com o primeiro ato correlato é inferência: a proposta pede, com razão, que não se faça |

**Proposta**: tabela de três colunas — *previsto originalmente*, *previsto após retificação* (com a
Retificação que alterou), *ato registrado* (só quando existir ato correlato, com o nome do ato).
Nenhuma coluna de "cumprido".

### D. Inscrições e participação

| Informação | Fonte | Disp. | Observação |
|---|---|---|---|
| Série diária de envios | `interface/supervisao.py::serie_do_edital` | E | é fluxo; o PDF a mostra como gráfico de barras com tabela equivalente |
| Por Perfil e modalidade | `inscricoes/application/consulta.py::_contagens` (privada) | E | tornar pública ou extrair — não duplicar |
| Inscrições para Perfil retirado por Retificação | `visao_geral._fora_do_quadro` | E | raro, mas existe |
| Canceladas / indeferidas | — | **X** | estados inexistentes |
| Por campus | — | **X** | sem dimensão |

### E. Execução das etapas

Por Etapa, na ordem do snapshot, por Perfil:

| Informação | Fonte | Disp. | Observação |
|---|---|---|---|
| Nome, ordem, caráter, peso, forma | `content["stages"]` | E | nomes reais do Edital, nunca genéricos |
| Inscrições que participaram | `resultados/application/prontidao.py::panorama_da_etapa` + `contagens` | E | `participantes`, `eliminadas_antes`, `consolidadas`… |
| Habilitadas / eliminadas | `ResultadoEtapa.vigentes` por `consequencia` | E | — |
| Eliminadas por ocorrência | `origem=OCORRENCIA` | P | **sem categoria**: não dizer "ausentes", dizer "eliminadas por ocorrência registrada" |
| Reabilitadas por recurso | `resultados/application/selectors.py::reabilitadas_por_recurso` | E | — |
| Corte (progrediram / fora da faixa) | `ItemDoCorte` do corte vigente | E | inclui `excedente_por_empate` |
| Primeira e última consolidação | `min/max(consolidado_em)` | D | ver C |
| Avaliações reabertas | `ConclusaoAvaliacao` | E | indicador operacional; **Q-05** se entra |

**Risco de simplificação indevida**: "eliminado na etapa 2" num Edital com marcos intermediários e
corte depende do marco. A seção deve dizer o que o Edital declarou (eliminatória, classificatória,
regra de corte) **lendo do snapshot**, como o PDF do Edital já faz, e nunca parafrasear.

### F. Resultado consolidado

| Informação | Fórmula / fonte | Disp. | Limitação |
|---|---|---|---|
| Marcos e a natureza vigente de cada um | `divulgacao.vigente_do_marco` | E | — |
| Inscrições classificadas em resultado divulgado | `COUNT(DISTINCT inscricao)` em `SituacaoDivulgada CLASSIFICADA` da publicação **vigente**, **por marco** | E | a `040` §9.1: somar marcos dupla-conta; o rótulo nunca é "classificados" sem o marco |
| Sem posição | idem `SEM_POSICAO` | E | — |
| Aprovados | — | **X** | termo inexistente e proibido pela varredura |
| Vagas publicadas / efetivas / ocupadas / faltando | `ocupacao_do_recorte` (vigente) | E | "ocupada" = **titular habilitado**, não matriculado; apuração pode estar **obsoleta** (`causas_de_obsolescencia`) — o relatório deve dizê-lo |
| Convocações por espécie | `Convocacao` raiz vigente | E | `DISTINCT inscricao`; chamadas repetidas |
| Desfechos por espécie | `DesfechoDaConvocacao` vigente | E | — |
| Requerimentos enviados | `RequerimentoDeMatricula` `enviado_em` | P | só onde o Edital declarou |
| Matrículas efetivadas | — | **X** | proibido pela `040` (`FR-592`); dizer a ausência |
| Vagas não preenchidas | `faltando` da apuração vigente | D | só com apuração **vigente e não obsoleta**; senão "não apurado" |

### G. Edital, retificações e documentos

| Informação | Fonte | Disp. | Observação |
|---|---|---|---|
| Edital original e cada Retificação, com datas | `publicacoes/application/selectors.py::atos_publicados` | E | `publicado_em`, `vigente_desde` |
| Justificativa de cada Retificação | `Retificacao.justification` | E | texto do servidor; já é público no PDF da Retificação? — **conferir antes da spec** |
| O que mudou | `publicacoes/domain/alteracoes.py::alteracoes_legiveis` (sem valores) | E | lista campos, não interpreta |
| Impacto em resultados | — | **X** | inferência; não fazer |
| Documentos oficiais com hash | `DocumentoPublicado.document_hash`, `DocumentoDoResultado.documento_hash` | E | é a seção de referências para auditoria |

### H. Recursos e intercorrências

| Informação | Fonte | Disp. | Observação |
|---|---|---|---|
| Recursos interpostos, por objeto (marco ou etapa) | `recursos_do_edital` | E | — |
| Por situação | `_situacao` derivada | E | inadmitidos, aguardando, decididos |
| Por espécie de decisão | `DecisaoRecurso.especie` | E | **"deferido" não é valor**; mostrar as quatro espécies |
| Pendentes no instante de referência | `recursos_pendentes_do_marco`, `providencias_pendentes_do_marco` | E | vai para "pendências conhecidas" |
| Sorteios executados / anulados | `Sorteio`, `motivo_da_anulacao` | E | — |
| Atos sucedidos (reemissão de ordem, corte, resultado) | cadeias `*_anterior` com `motivo_da_sucessao` | E | é o mais próximo de "alteração de resultado" que o domínio sabe |
| Ocorrências genéricas | — | **X** | não há registro de ocorrência do certame |
| Regularidade / qualidade do processo | — | **X** | juízo, não fato; fora |

### I. Encerramento

| Informação | Fonte | Disp. | Observação |
|---|---|---|---|
| Data e autor do ato | `AtoAdministrativo` | E | autor é `actor_subject` |
| Motivo do ato | `AtoAdministrativo.reason` | E | a página **pública** não o mostra (`047`, FR-764); no relatório interno é **Q-04** |
| Pendências conhecidas | recursos pendentes, providências pendentes, apuração obsoleta, convocação com prazo em curso, marco sem definitivo | D | reuso dos sinais da Supervisão; é o item mais útil a quem encerra |
| Fatos posteriores ao encerramento | atos com instante > desfecho | D | consequência direta de §1.2; o relatório os conta e diz |
| Referências | lista de documentos com hash e endereço público | E | — |

---

## 4. Alternativas

| | A — Exportação simples | B — Relatório estruturado | C — Módulo de encerramento | D — Painel de execução + PDF |
|---|---|---|---|---|
| **Valor** | baixo: tabelas sem leitura; repete as telas | médio-alto, **se** houver destinatário | alto só se a instituição quiser um rito novo — não há evidência | alto para quem conduz (dor real); o PDF estende a quem está fora |
| **Aderência** | média: não há exportação de listas, e criá-la abriria a questão de dado pessoal | alta, se derivar | **baixa**: duplica a máquina de estados da `001`, contraria a regra da `022` sobre estado novo | **alta**: é o padrão da `040` (página com quatro ausências) aplicado ao Edital |
| **Dependências** | nenhuma | `pdf.py`, selectors existentes | migrations, tabela append-only (M sobe), estados, permissões | `pdf.py`, selectors existentes; a camada de resultado da `040` |
| **Complexidade** | baixa | média | alta | média — o PDF é a mesma leitura impressa |
| **Riscos** | "exportação indiscriminada"; dado pessoal | parecer ato; envelhecer; segunda derivação dos números | burocratizar; duplicar o ato; snapshot que diverge do vivo | segunda derivação, se não compartilhar o módulo de leitura com a `040` |
| **Evolução** | beco | → D | — | → Processo (reunião dos Editais) → série histórica pela `040` |

**Combinação recomendada**: **D com o conteúdo de B**, numa ordem que não exige o PDF para
entregar valor — página primeiro, PDF da mesma leitura depois. De C, aproveita-se apenas a
**conferência de pendências** como conteúdo da página (§3.I), sem bloquear ato nenhum.

---

## 5. Recomendação

**Experimentar** — e, se a validação passar, implementar D enxuto. Em ordem:

1. **Agora (sem código de produto)**: a validação da §2.6. Custo: uma maquete e cinco conversas.
2. **Registrar dois achados**, sem atribuir escopo (governança é do usuário):
   - *Encerrar o Edital não confere pendência alguma* (§1.2);
   - *Encerrado não congela o ciclo; só o recebimento para* (§1.2) — com a pergunta de produto se
     isso é o desejado.
3. **Se a validação passar**: a spec da §6, MVP da §7.
4. **Se não passar**: descartar o PDF e manter só a página — que atende a dor de quem conduz e
   completa a camada de resultado que a `040` deixou registrada.

**Por que não implementar já**: não há certame real encerrado no sistema, nem destinatário que
tenha pedido. A Constituição (VI) exige cenário demonstrável por usuário real, e diz que o backlog
deriva das jornadas, não do que parece interessante. A própria proposta pede isso.

**Por que não adiar indefinidamente**: o primeiro certame real a encerrar no GPS vai produzir a
pergunta "como foi?" — e hoje a resposta exige sete telas. A página custa pouco se for leitura.

---

## 6. Proposta de spec

### 6.1 Nome e objetivo

**Relatório de execução do Edital** — e não "de encerramento". Três razões: (i) o relatório não é o
ato de encerramento, e o nome não deve sugerir que seja; (ii) ele é útil antes do desfecho (o
Edital em execução) e depois (o encerrado e o cancelado); (iii) "encerramento" já é termo do domínio
com significado preciso (`Edital.Status.ENCERRADO`), e a Constituição (I) proíbe dois sentidos para
um termo. *Nome provisório — **Q-01**.*

Objetivo: dar a quem conduz um Edital, e a quem ela presta contas, uma leitura única e verificável
do que aconteceu no certame — dimensão, procura, etapas, resultado, ocupação, retificações e
recursos —, **derivada inteiramente de fatos já registrados**, com cada ausência dita como
ausência e cada número rastreável à tela dona.

### 6.2 Problema e hipótese de valor

Problema: os fatos do ciclo de um Edital estão em sete telas com quatro portas; não há leitura que
os reúna, e quem não é usuário do GPS não tem acesso a nenhuma delas.

Hipótese: uma página de execução reduz a montagem manual de uma resposta à direção, e o PDF dela
basta como documento de prestação de contas interna — **a validar pela §7.1**.

### 6.3 Personas e situações de uso

| Persona | Situação | Canal |
|---|---|---|
| Presidência / gestão do Processo | antes de encerrar: "o que falta?"; depois: "como foi?" | página |
| Direção do campus / ensino | planejar a oferta seguinte; prestar contas | PDF recebido |
| Coordenação do curso (quando o Perfil é o curso) | procura e ocupação do seu Perfil | PDF recebido |
| Auditoria | conferir documentos e atos | página (auditor) e seção de referências |

### 6.4 Escopo e exclusões

**Dentro**: uma página por Edital; o PDF da mesma leitura; a reunião por Processo como lista dos
relatórios dos Editais (Evolução 2).

**Fora**: estado ou transição nova; bloqueio de ato; texto gerado por IA; juízo sobre regularidade
ou qualidade; relação nominal; inferência de atraso; "aprovados"; matrícula efetivada; série
histórica entre Editais (é da `040`); exportação de listas.

### 6.5 Requisitos funcionais (provisórios)

**Leitura e fonte única**

- **R-01**: O relatório MUST derivar todo número de fato registrado, por um único módulo de leitura,
  consumido pela página e pelo PDF. Nenhum número MUST ser recalculado de forma própria quando a
  tela dona já o calcula: o módulo chama o selector dela.
- **R-02**: O relatório MUST declarar o **instante de referência** — o da leitura — no topo e em
  cada página do PDF.
- **R-03**: O relatório MUST NOT persistir estado próprio. A emissão do PDF MUST gerar um evento de
  auditoria (`record_event`) com o Edital, o instante de referência, o ator e o SHA-256 dos bytes.
  *Sem tabela nova: o precedente é a `GeracaoDeArquivo`, mas a trilha basta enquanto ninguém
  precisar listar emissões numa tela.*
- **R-04**: Indicadores sem fonte MUST aparecer com uma das quatro grafias de ausência da `040`
  (§13) — *não se aplica*, *ainda não disponível*, *não publicado*, *parcial* — acrescidas de uma
  quinta, **não registrado pelo sistema** (para homologação, matrícula, presença), que diz que o
  GPS não controla o fato. Falha de leitura MUST interromper a emissão, e nunca virar ausência.

**Conteúdo**

- **R-05**: Identificação (§3.A), com situação e data do desfecho por `desfechos()`.
- **R-06**: Sumário de no máximo seis números, cada um com o denominador dito: vagas publicadas,
  submetidas, inscrições por vaga, marcos com resultado definitivo, vagas ocupadas na apuração
  vigente, retificações publicadas.
- **R-07**: Cronograma em três colunas — original, após retificação (com a Retificação), ato
  registrado — sem coluna de cumprimento.
- **R-08**: Inscrições por Perfil e modalidade, e a série diária.
- **R-09**: Por Perfil e Etapa, na ordem e com os nomes do snapshot: participantes, habilitadas,
  eliminadas (separando as por ocorrência), reabilitadas por recurso; o corte quando houver.
- **R-10**: Por marco: natureza vigente, inscrições classificadas e sem posição **naquele marco**,
  nunca somadas entre marcos.
- **R-11**: Por recorte apurado: publicadas, efetivas, ocupadas, faltando, e a obsolescência quando
  houver. "Ocupada" MUST ser explicada como titular habilitado.
- **R-12**: Convocações por espécie e desfechos por espécie, contando inscrições distintas.
- **R-13**: Recursos por objeto, situação e espécie de decisão.
- **R-14**: Retificações com data, justificativa e os campos alterados (`alteracoes_legiveis`),
  sem interpretação de impacto.
- **R-15**: **Pendências conhecidas** no instante de referência: recursos e providências
  pendentes, apurações obsoletas, convocações com prazo em curso, marcos sem resultado definitivo.
- **R-16**: **Fatos posteriores ao desfecho**: quando houver ato com instante posterior ao
  encerramento, o relatório MUST contá-los e dizê-lo.
- **R-17**: Referências: cada documento publicado (Edital, Retificações, resultados) com data,
  endereço público e SHA-256.

**Dado pessoal**

- **R-18**: O relatório MUST NOT conter nome, CPF, protocolo, e-mail ou qualquer identificador de
  candidato. Onde a relação nominal importa, MUST remeter ao resultado publicado (R-17).
- **R-19**: Célula com contagem entre 1 e N (N a decidir, **Q-06**) em recorte que combine
  modalidade de cota e etapa MUST ser suprimida ou agregada, para que o número não identifique
  candidato de grupo pequeno.

**Acesso e forma**

- **R-20**: A página e o PDF MUST seguir a porta `pode_supervisionar` (gestão ou presidência do
  Processo), com recusa em 404 uniforme e linha no inventário de negativas da `033`. Leitura pelo
  `auditor`: **Q-03**.
- **R-21**: O PDF MUST trazer, em todas as páginas, a marca *"Relatório gerencial — não é ato
  administrativo nem substitui as publicações oficiais"*, e MUST NOT trazer bloco de autoridade
  signatária nem fecho "Local, data" de ato.
- **R-22**: Disponível para Edital `PUBLICADO`, `ENCERRADO` ou `CANCELADO`. Antes do desfecho, o
  título MUST dizer *"em execução"*.

### 6.6 Requisitos não funcionais

- **RNF-01**: Número de consultas constante em relação ao número de inscrições (orçamento por
  `CaptureQueriesContext`, como `tests/performance/test_visao_institucional.py`). Cresce no máximo
  com Perfis × marcos × recortes.
- **RNF-02**: Síncrono. Sem fila: um Edital do porte real (centenas a poucos milhares de inscrições)
  não justifica worker, e a Constituição (V) exige necessidade demonstrável.
- **RNF-03**: PDF por `render_documento` e `_tabela` de `pdf.py`, sem dependência nova; gráfico de
  barras desenhado pelo próprio motor, com tabela equivalente (acessibilidade e varreduras).
- **RNF-04**: Saída determinística para o mesmo instante de referência e os mesmos fatos (o motor
  já é determinístico); o SHA-256 da auditoria identifica o que foi emitido.
- **RNF-05**: Página dentro da CSP (`style-src 'self'`), folha própria em `interface/telas/`,
  vocabulário conferido pelas varreduras existentes.

### 6.7 Regras de negócio

1. **Zero é afirmação**: só se escreve 0 quando a fonte produziu 0 (`040` §13).
2. **Inscrição não é pessoa**: toda contagem é de inscrições, salvo o indicador de pessoas, que fica
   fora do MVP (pendente na `040`).
3. **Marco não se soma**: classificação é por marco e lista.
4. **Razão não é média de razões**: `Σ numerador ÷ Σ denominador`, numerador recortado aos Perfis
   com vaga.
5. **O relatório não reescreve o Edital**: regras de etapa e de corte são lidas do snapshot e
   ditas como o Edital as declarou.
6. **Vigente é a linha sem sucessor** no instante da leitura. O relatório não reconstrói o passado
   ("como estava em T"): emite o presente e o data. *Reconstrução por instante é possível — tudo é
   append-only com instante — mas exigiria reescrever cada selector com corte temporal; fica
   registrada como evolução sem obrigação.*

### 6.8 Estrutura sugerida do documento

```text
Capa            Unidade · Processo · Edital nº/ano · situação · instante de referência · marca gerencial
1. Em resumo    seis números com denominador · pendências conhecidas (se houver) · fatos pós-desfecho
2. Linha do tempo  cronograma em três colunas · atos publicados com data
3. Procura      por Perfil e modalidade · série diária (barras + tabela)
4. Etapas       por Perfil: tabela Etapa × (participantes, habilitadas, eliminadas, por ocorrência, reabilitadas)
5. Resultado    por marco: natureza, classificadas, sem posição · ocupação por recorte · convocações e desfechos
6. Retificações data · justificativa · campos alterados
7. Recursos     por objeto, situação e espécie
8. Referências  documentos oficiais com SHA-256 e endereço · o que o sistema não registra (lista fixa)
```

Camada executiva: capa + §1 (uma página). Camada analítica: §2–§8. **Um documento só**, com a
primeira página autossuficiente: dois níveis de relatório dobrariam a derivação.

### 6.9 Fluxo

1. No detalhe do Edital (`interface/acoes.py`), ação *Relatório de execução*, oferecida a quem
   alcança a porta (padrão de `Acao`: motivo vazio = disponível).
2. A página abre com o instante de referência e as pendências no topo.
3. *Baixar PDF* gera o documento da mesma leitura, registra a emissão na auditoria e responde com
   `Content-Disposition: attachment` e cabeçalho de resposta privada (`marcar_como_privada`).
4. No detalhe do Processo, a lista dos Editais com link para o relatório de cada um (Evolução 2).

### 6.10 Critérios de aceitação

- **CA-01**: Para o Edital de demonstração conduzido até a ocupação, cada número do relatório é
  igual ao da tela dona correspondente (teste que lê as duas fontes).
- **CA-02**: Edital sem resultado divulgado mostra *"ainda não disponível"* nas seções de
  resultado, e nunca 0.
- **CA-03**: Edital com dois marcos: classificadas aparecem por marco, e nenhum total as soma.
- **CA-04**: Edital encerrado com recurso aguardando julgamento lista o recurso em pendências.
- **CA-05**: Convocação registrada depois do encerramento aparece em *fatos posteriores ao
  desfecho*.
- **CA-06**: O PDF não contém nome, CPF nem protocolo de candidato do banco de teste (varredura
  pelo texto extraído).
- **CA-07**: Ator sem a porta recebe 404; a recusa consta do inventário da `033`.
- **CA-08**: A emissão do PDF grava um evento de auditoria com o SHA-256 dos bytes entregues.
- **CA-09**: O número de consultas não muda entre um Edital com 10 e com 1 000 inscrições.
- **CA-10**: Retificação que alterou prazo aparece na coluna *após retificação* com a Retificação
  nomeada, e a original permanece na primeira coluna.

### 6.11 Casos de teste a acrescentar

Unidade: cada grafia de ausência; razão com Perfil só de CR; soma por marco recusada. Integração:
CA-01 a CA-05 e CA-10 sobre fixtures de certame completo (o `levar_a_publicacao` dos testes e os
cenários de convocação). Autorização: CA-07. Desempenho: CA-09. Conteúdo: CA-06, varredura de
vocabulário com o template novo na lista literal (memória: *a varredura tem lista literal; tela
nova escapa em silêncio*).

### 6.12 Dependências

- A camada de resultado da `040` (indicadores 7–13): **compartilhar o módulo de leitura**. Se a
  `040` for completada primeiro, o relatório consome; se o relatório vier primeiro, a `040` passa a
  consumir dele. Duas derivações seriam o defeito que `FR-582` da `040` existe para impedir.
- `inscricoes/application/consulta.py::_contagens`, hoje privada.
- Uma função de diff de cronograma entre versões consolidadas (não existe).

### 6.13 Riscos e questões pendentes

| Risco | Aplica-se aqui? | Mitigação |
|---|---|---|
| Ausência de histórico | **sim**: nenhum certame real; sem carga retroativa | validar com o demo; o primeiro uso real será o primeiro encerramento |
| Cronograma sem execução efetiva | **sim** | R-07: três colunas, sem "cumprido" |
| Resultado sujeito a alteração | **sim**, e depois do encerramento também | R-02, R-15, R-16 |
| Modalidades de seleção diferentes | **parcial**: não há taxonomia; Perfis de CR, com ou sem requerimento | seções não aplicáveis se dizem "não se aplica" |
| Múltiplas ofertas | **sim**: vários Perfis e listas | tudo por Perfil e recorte |
| Desempenho | baixo, se seguir RNF-01 | orçamento de consultas |
| Indicador enganoso | **alto**: "classificados", "ocupadas", "inscrições por vaga" | rótulos do domínio, denominadores ditos, R-10, R-11 |
| Dado pessoal | médio: agregados pequenos | R-18, R-19 |
| PDF fora do sistema | **alto**: não há como revogar um arquivo enviado | R-21, R-02, sem nominal; o hash permite conferir |
| Parecer ato oficial | médio | R-21; sem autoridade nem fecho |
| Baixa demanda | **desconhecido** | §2.6 antes de tudo |
| Manutenção | médio: cada feature nova do ciclo pede uma linha no relatório | o relatório lê selectors das donas; não reimplementa |

---

## 7. MVP

### 7.1 Critério para começar (portão da validação)

Avançar se **pelo menos dois** forem verdadeiros depois da §2.6:

- ao menos dois destinatários de fora do GPS dizem em que decisão usariam o documento;
- a equipe do setor descreve um relatório que já faz hoje à mão, ou um pedido recorrente da direção;
- montar a maquete à mão levou mais de uma hora sobre o Edital de demonstração.

Se nenhum for verdadeiro: **só a página**, sem PDF.

### 7.2 Escopo do MVP

- Página de execução por Edital, com as seções 1, 2 (só cronograma original × vigente e atos
  publicados), 3, 5 e 8 da estrutura; seções 4, 6 e 7 como contagens simples, sem detalhamento.
- PDF da mesma leitura, com a marca gerencial e o evento de auditoria.
- Porta `pode_supervisionar`. Sem papel novo.
- Sem reunião por Processo, sem série, sem diff detalhado de cronograma.

### 7.3 Evolução 2

Diff de cronograma em três colunas; detalhamento de etapas por Perfil; reunião por Processo;
leitura por `auditor`; papel de leitura para Direção, se a §8 o decidir.

### 7.4 Evolução futura

Reconstrução "como estava em T"; comparação entre Editais e séries (pela `040`, não aqui);
registro de emissões em tabela própria, se alguém precisar listá-las.

### 7.5 Critérios de sucesso do MVP

- Nos três primeiros Editais reais encerrados no GPS, a presidência usa o relatório para responder
  à direção, sem planilha paralela (pergunta direta após o uso).
- Zero divergência entre relatório e telas donas (CA-01 na suíte).
- Zero ocorrência de dado nominal (CA-06).
- Nenhum destinatário lê o relatório como ato oficial (pergunta direta após o uso).

---

## 8. Questões que exigem decisão humana

| # | Pergunta | Opções | Por que importa |
|---|---|---|---|
| **Q-01** | Nome: "de encerramento" ou "de execução"? | encerramento · execução · outro | encerramento já é termo do domínio |
| **Q-02** | Validar antes (§2.6) ou especificar já? | validar · especificar | não há demanda nem dado real |
| **Q-03** | Quem gera e quem lê? | gestão + presidência · + auditor · papel novo de Direção | a `040` já deixou o papel de Direção pendente |
| **Q-04** | O motivo do ato de encerramento entra no relatório interno? | sim · não | a página pública o omite por decisão (`047`) |
| **Q-05** | Avaliações reabertas e atos sucedidos entram? | sim · só contagem · não | são operacionais; podem ser lidos como falha |
| **Q-06** | Limiar de supressão de contagens pequenas | 0 (sem) · <3 · <5 | grupo pequeno de cota é reidentificável |
| **Q-07** | Nomear servidores (presidência, autoridade)? | sim · só cargo · não | servidor em ato público é publicidade; em documento gerencial, é escolha |
| **Q-08** | O PDF pode sair do Ifes? | só interno · também externo | muda a marca e a política de distribuição |
| **Q-09** | Encerrar o Edital deve conferir pendências? | não · avisar · bloquear | achado sobre a `001`, não do relatório |
| **Q-10** | Encerrado deve congelar recursos e convocações? | não (como hoje) · sim · parcialmente | define se "relatório de encerramento" pode ser definitivo |
| **Q-11** | Unidade do relatório | Edital · Processo · ambos | tudo pende do Edital |
| **Q-12** | Pessoas distintas entra? | não · sim, com a ressalva do CPF | já pendente na `040` (indicador 14) |

---

## Encerramento — recomendação e trade-offs

**Recomendação: experimentar, com portão.** Validar com maquete e destinatários reais; passando,
entregar a página de execução do Edital com o PDF como a mesma leitura impressa, sem estado novo,
compartilhando a derivação com a camada de resultado da `040`. Descartar o módulo de encerramento
como está formulado, e registrar os dois achados sobre o ato de encerrar.

**Trade-offs principais:**

- **Página × PDF**: a página serve quem tem a dor comprovada e não envelhece; o PDF alcança quem
  está fora do sistema, mas envelhece, sai do controle de acesso e parece ato. A ordem proposta
  entrega o primeiro sem apostar no segundo.
- **Ao vivo × fotografia**: emitir o presente datado é simples e honesto; reconstruir o passado é
  possível com os dados append-only, mas custa reescrever selectors. O hash na auditoria cobre a
  necessidade de provar o que foi emitido.
- **Estado formal × sob demanda**: amarrar o relatório ao `ENCERRADO` não acrescenta garantia
  nenhuma, porque o estado não congela os fatos. Sob demanda, com instante de referência,
  pendências e fatos posteriores ditos, é mais verdadeiro.
- **Completude × honestidade**: metade do que a proposta lista (homologação, aprovados, matrícula,
  atraso, campus) não tem fonte. O relatório fica mais curto do que a proposta imagina — e é isso
  que o torna confiável.
