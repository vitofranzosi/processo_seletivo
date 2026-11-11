# Pesquisa: publicação e homologação das inscrições

**Feature**: [spec.md](spec.md) · **Data**: 2026-11-11 · **Base**: `main` em `d3e98a89`

Este documento é o **diagnóstico** que o pedido exigiu antes de qualquer proposta. Ele responde, com
o código, às dez perguntas do §2 do pedido e às dez questões do §7, que a spec decide em
`D-001` a `D-010` — na mesma ordem do pedido. Caminhos relativos a `backend/processo_seletivo/`.

## 1. O pedido, resumido

Permitir que o GPS conduza, quando o Edital prevê, três atos sobre as inscrições — a **relação de
inscrições recebidas**, o **resultado preliminar da análise das inscrições** e a **homologação das
inscrições** —, qualquer que seja a forma de classificação, aproveitando publicação, recurso,
cronograma e prévia existentes, sem motor de workflow, sem estado persistido derivável e sem acoplar
a relação de inscritos ao congelamento do sorteio.

## 2. O que existe hoje — as dez perguntas do diagnóstico

### 2.1 As specs que registraram a lacuna

| Onde | O que diz |
|---|---|
| `specs/021-sorteio-publico-auditavel/spec.md` (decisão sobre a relação de habilitados; *Assumptions*; *Out of Scope*) | A relação de habilitados entra **enquanto compromisso do sorteio**; *"a relação de inscritos que todo Edital publica é artefato universal, e é outra feature"*; recurso contra ela fora |
| `specs/020-anexos-do-edital/spec.md`, *Out of Scope* | *"Relação de inscritos publicada"* e comunicados complementares: figura que o sistema não tem |
| `specs/067-correcoes-de-norma-do-edital/spec.md`, cenário B | O Cronograma real tem recurso *"contra a homologação das inscrições"*, ato *"que o sistema não modela como marco"* |
| `specs/009-inscricao-simples-documentos/spec.md`, FR-070 | A tela "Inscrições recebidas" **não** mostra deferimento, indeferimento nem homologação — a 009 termina em "recebido e consultável" |
| `specs/017-publicacao-de-resultados/spec.md`, decisões sobre o objeto publicável e sobre homologação de resultado | Só o ato de ordenação é publicável; publicar o resultado de uma Etapa *"começa por uma feature que constitua esse ato"*; homologação, se vier, é *"mais uma publicação na mesma cadeia"* |
| `doc/estudo-relatorio-de-execucao-do-edital-2026-10-24.md` | *"Homologação de inscrição: não existe como ato nem como estado"*; *"Não substituir por submetidas"* |
| `doc/estudo-classificacao-demonstrativa-2026-11-07.md` | O caso real contornou com **uma Etapa decisória "Análise dos requisitos"**; *"Publicar o resultado de uma Etapa sozinha"* ausente |

### 2.2 Modelos, serviços e telas reaproveitáveis

| Peça | Onde | Reaproveitamento |
|---|---|---|
| `Inscricao` (`RASCUNHO`/`SUBMETIDA`) | `inscricoes/models.py:23` | o universo — "recebida" **é** `SUBMETIDA` |
| `EtapaAvaliacao.forma = DECISORIA`, rótulos publicados | `editais/models/etapas.py:51-54`, `avaliacoes/domain/formas.py` | **a análise das inscrições** — Deferido/Indeferido já é rótulo publicado (o `seed_demo` tem "Análise documental") |
| Mesa, distribuição, consolidação | `avaliacoes/`, `resultados/application/consolidacao.py` | a conferência individual, com motivo, sem tela nova |
| `ResultadoEtapa` (`HABILITADA`/`ELIMINADA`, `motivo`, sucessão) | `resultados/models.py:41` | a decisão por inscrição, append-only, com proveniência |
| Ocorrência (eliminação por fato) | `resultados/application/ocorrencia.py` | "não cumpriu requisito" sem avaliação |
| `Recurso.resultado_atacado`, julgar, superar | `recursos/` | o recurso contra o indeferimento **já existe** |
| `resultados_visiveis` | `resultados/application/selectors.py:170` | o titular vê o próprio resultado e motivo — falta só o **fato autorizador** |
| Receita da divulgação (`PublicacaoResultado`) | `divulgacao/application/publicar.py` | o padrão do ato: permissão, trava, idempotência, prévia assinada, autoridade, bytes canônicos, PDF gravado, trilha |
| `Composicao`/`render_documento` | `publicacoes/infrastructure/pdf.py` | o PDF do ato, sem biblioteca nova |
| `contexto_do_ato` | `publicacoes/application/contexto_do_ato.py:83` | autoridade signatária e unidade congeladas |
| `recusa_por_inscricoes_em_curso` | `avaliacoes/domain/conjunto.py:68` | nada se publica com o período correndo |

### 2.3 Como o sistema determina a situação de uma inscrição

Persistido: **só** `RASCUNHO` e `SUBMETIDA` (`inscricoes/models.py:24-26`), por decisão expressa da 009
(FR-027: dois estados e nenhuma máquina genérica). Não existem *recebida*, *cancelada*, *deferida*,
*indeferida* nem *homologada* como estado. Cancelamento de inscrição não existe (fora do escopo da 009).

Derivado:

- **período** — `FUTURO`, `ABERTO`, `ENCERRADO`, `NAO_DESIGNADO` (`inscricoes/domain/periodo.py:51`);
- **progressão** — eliminada em Etapa anterior sai; a Etapa imediatamente anterior precisa ter
  habilitado (`resultados/application/prontidao.py`, `restringir_a_participantes`);
- **situação do candidato** — sete degraus da 063 (`portal/situacao.py:170`): desfecho da convocação,
  convocado, eliminado, aguardando chamada, aguardando definitivo, não classificado, inscrição enviada.

### 2.4 Persistido versus derivado — a consequência

`Inscricao` enviada é **imutável por gatilho** (`inscricao_enviada_imutavel`, `inscricoes/0007`, A-03). Nada
de deferida/homologada pode morar nela, e nem deve: a decisão já mora no `ResultadoEtapa` da Etapa
decisória, que é append-only e sucede por decisão de recurso. **Um estado "homologada" na inscrição
seria uma segunda resposta para a mesma pergunta.**

### 2.5 Conferência de inscrições e documentos

Antes da avaliação, a conferência existe **como Etapa decisória**: o avaliador abre a inscrição na
Mesa, vê os documentos (`ItemDaListaExigida`, a lista congelada no envio, 044) e conclui Deferido ou
Indeferido com motivo. A conferência documental da convocação (115/117/140) é outra coisa — é da
pessoa convocada, depois da classificação — e não se reaproveita aqui.

### 2.6 Recursos

Dois alvos, por chave estrangeira explícita e XOR (`recursos/models.py:58-88`): a `PublicacaoResultado`
ou o `ResultadoEtapa`. O segundo é **exatamente** o recurso contra o indeferimento. A interposição
exige que o resultado seja **visível** (`_recusar_se_invisivel`), e a janela vem dos marcos que
enumeram a Etapa (`_janelas_pertinentes`, `recursos/application/interpor.py:164`). Julgado com
correção fixada, nasce o sucessor do `ResultadoEtapa` com origem `RECURSO`; com reavaliação, nova
avaliação e nova consolidação. **Lacuna exata:** a Etapa de análise não está em marco nenhum, e então
o resultado dela nunca fica visível nem tem janela.

### 2.7 Cronograma

`EventoCronograma.type` é texto livre e **nada o lê** (`editais/models/cronograma.py:26-36`). O
Cronograma só **governa** o período de inscrições; datas de Etapa são *"informadas, e não aplicadas"*
(`avaliacoes/application/mesa.py:225-232`); a janela recursal é declaração do marco
(`appealWindow`), ancorada no instante do ato. Não há evento tipado para "homologação" ou "recurso
contra…" — e o cenário B da 067 mostra que os Editais reais os têm, com datas.

### 2.8 Documento, versão, publicação e retificação

Cada ato publicado é agregado próprio, append-only em três camadas (ORM, gatilho, privilégio
ausente), com bytes canônicos e resumo, PDF **gerado uma vez e gravado**, autoridade e unidade
congeladas. Corrigir é **suceder** — o anterior continua legível e diz que foi sucedido. Não há
`Publicavel` genérico, por decisão (017).

### 2.9 Inscrições, listas, habilitação e sorteio

A inscrição tem um Perfil e no máximo uma modalidade; a ampla inclui todos, a reservada filtra
(`editais/domain/recortes.py`). A `RelacaoDeHabilitados` projeta `SUBMETIDA` do Perfil, filtra a lista
e — **quando o método declara `qualifyingStageId`** — mantém só quem tem `HABILITADA` vigente naquela
Etapa (`sorteios/application/habilitacao.py`). Ela congela com o resumo do método, é recusada com
inscrições em curso e corrige-se por sucessão. **A homologação já pode alimentá-la, pelo mesmo
`ResultadoEtapa`**: basta o método apontar a Etapa de análise.

### 2.10 Impacto em Editais e dados existentes

Nenhum: o ato novo é **opcional e não exige configuração**. Editais publicados não mudam de conteúdo,
nenhuma migration percorre linha existente, nenhum leitor existente passa a exigir o ato. Quem já
usa Etapa decisória continua a usá-la; o ato só acrescenta a publicação coletiva dela.

## 3. As questões do §7 — onde cada uma se decide

| Pedido | Decisão | Resposta curta |
|---|---|---|
| 1 — entidades próprias × publicações existentes | `D-001` | um agregado, três naturezas; nada de `Publicavel` |
| 2 — cronograma sem configuração nova | `D-002` | o Evento escolhido no ato, congelado; período de inscrições como trava |
| 3 — recurso contra a análise preliminar | `D-003` | o mecanismo atual, contra o `ResultadoEtapa`; duas adaptações |
| 4 — consolidar depois dos recursos | `D-004` | projeção dos vigentes; três pendências impedem |
| 5 — homologação × `RelacaoDeHabilitados` | `D-005` | mesma fonte, nenhum acoplamento |
| 6 — snapshot, versão e retificação | `D-006` | bytes congelados + linhas; sucessão com motivo; divergência derivada |
| 7 — Editais sem deferimento individual | `D-007` | só a relação de recebidas, ou homologação sem análise |
| 8 — unidade e compatibilidade | `D-008` | escopo institucional, capacidade existente, nada obrigatório |
| 9 — vagas, listas e modalidades | `D-009` | por Perfil; a lista não divide a inscrição |
| 10 — o que é público | `D-010` | protocolo e nome de quem consta; indeferida só contada |

## 4. Alternativas descartadas

| Alternativa | Por que não |
|---|---|
| Estado `HOMOLOGADA`/`DEFERIDA` na `Inscricao` | contradiz a 009 (dois estados), esbarra no gatilho da enviada e duplica o `ResultadoEtapa` |
| Reusar `RelacaoDeHabilitados` como relação universal | exige marco e método de sorteio, numera para sortear e congela o universo do sorteio — a 021 recusou o universal pelo mesmo motivo |
| Publicar a análise por um marco de classificação | dá semântica de ordem a uma decisão binária, e um "resultado" com posições de quem foi deferido |
| Aviso complementar (066) como veículo | o aviso aponta para um ato, e não é o ato; e é e-mail, não publicação |
| `Publicavel` genérico | a 017 o recusou; o custo é o mesmo agregado com mais indireção |
| Tipar `EventoCronograma.type` | todo Cronograma publicado tem texto livre; a migração reinterpretaria conteúdo normativo publicado |
| `appealWindow` na Etapa | campo normativo novo na composição, no snapshot, na Retificação e no PDF — para uma única Etapa por Edital |
| Capacidade nova `inscricoes:publicar` | mesmo titular (publicador) e mesma autoridade; separaria permissão sem separar responsabilidade (`P-4`) |

## 5. Riscos medidos

| Risco | Tratamento |
|---|---|
| "Homologação" já nomeia o ato sobre o Edital | sempre qualificada — "homologação **das inscrições**" — em código, tela e documento (`D-001`) |
| Publicar com inscrições chegando | recusa com o período em curso (`recusa_por_inscricoes_em_curso`) |
| Resultado muda depois da homologação | a divergência é derivada e mostrada; o ato não muda; corrige-se publicando sucessor com motivo |
| Concorrência entre duas abas | trava do Processo, idempotência, prévia assinada e unicidade de raiz/sucessor no banco |
| Recurso aberto contra resultado já homologado | a homologação é impedida enquanto há recurso pendente, reavaliação pendente ou prazo correndo |

## 6. Decisões tomadas durante a implementação

| Ponto | Decisão | Por quê |
|---|---|---|
| Consultas de `resultados_visiveis` | de 3 para 4 (e de 1 para 2 sem publicação) | o segundo fato autorizador mora noutra tabela; a consulta é uma e constante — não cresce com marcos nem com atos (`tests/performance/test_resultado_da_etapa.py`) |
| Vocabulário da função pura da situação | a view traduz recebida/deferida/indeferida para recebida/aceita/não aceita antes de chamá-la | a varredura do requerimento (UX-058) lê `portal/situacao.py`, e o topo não usa o vocabulário do deferimento |
| Perfil sem inscrição | aparece no ato, com "Nenhuma inscrição … neste Perfil" | achado da validação: num Edital de dois Perfis, o segundo sumia |
| Prazo de recurso | do instante da publicação ao término do Evento | a âncora no ato é a regra da `018` — publicação atrasada não nasce com prazo vencido; o término é o que o Cronograma publica |

## 7. Trabalhos futuros (registrados, não escopo)

- "Minhas inscrições" continua dizendo "Inscrição enviada" depois do ato; a situação mora no
  acompanhamento, a um clique.
- O cartão "Resultado das etapas" diz "Eliminada" para a análise, enquanto o topo diz "não aceita":
  o vocabulário do cartão é o da `063` para toda Etapa.
- Aviso por e-mail ao publicar (P-5): uma origem nova nos avisos da `066`.
- Informar na tela da relação do sorteio se a homologação das inscrições já foi publicada —
  informação, nunca trava (D-005).
