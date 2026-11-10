# Research: O barema da Etapa (146)

Investigação de 10/11/2026 sobre a `main` em `d184fcee`. Caminhos de código relativos a
`backend/processo_seletivo/`.

## 1. O pedido

Investigar se o GPS suporta barema (análise de títulos, formação, experiência), identificar o que já
existe, e especificar a menor evolução que leve um processo real de títulos da configuração à
classificação. Diretrizes: reutilizar modelos, serviços, telas e fluxos; não criar segundo mecanismo
de classificação nem de recursos; nada de motor de regras, DSL, biblioteca de baremas, versionamento
próprio, dupla avaliação ou distribuição automática; preservar multiunidade e os processos por
sorteio. Cinco cenários de validação: títulos (10/6/3), experiência (2 por ano até 10), avaliação e
revisão, processo sem barema, configuração compartilhada entre vagas. Autorizado só documentação.

## 2. Diagnóstico do código

### A matriz

| Capacidade | Já existe? | Evidência no código | O que falta |
|---|---|---|---|
| Critérios de avaliação | **Não** | `EtapaAvaliacao` (`editais/models/etapas.py`) tem forma, mínima, máxima, peso, caráter e avaliações por inscrição — nenhum critério. A `013` diz por escrito: "critérios, itens e barema estruturado não existem no domínio". "Critério de Avaliação" é termo da Constituição (Princípio I) sem entidade | A coleção de critérios na Etapa, publicada |
| Pontuação e limites | **Sim, no total** | `avaliacoes/domain/pontuacao.py`: `normalizar` (forma `decimal(7,4)`, não negativa) e `validar` (máxima publicada, cobrada na conclusão); `ck_etapa_maximum_score_positiva` | Limite por critério e soma; a máxima da Etapa passa a derivar dos critérios |
| Comprovação documental | **Sim** | `DocumentoExigido` (`editais/models/documentos.py`), obrigatório ou facultativo, por Perfil e modalidade; `DocumentoSubmetido` (`inscricoes/models.py:329`), um PDF por requisito, imutável depois do envio; envio em `inscricoes/application/rascunho.py:467` | Só o vínculo critério → documento, para a Mesa mostrar a evidência ao lado do critério |
| Avaliação pela comissão | **Sim, com um campo** | Mesa: `interface/views.py:7079` (`inscricao_da_mesa`), `mesa_inscricao.html` com documentos em painel ao lado e um campo `pontuacao`; `avaliacoes/application/avaliacao.py` (`gravar`, `concluir`, `reabrir`); `ConclusaoAvaliacao` append-only; gatilho `avaliacao_concluida_imutavel` (`avaliacoes/migrations/0004`) | A ficha por critério no formulário; o detalhamento gravado |
| Consolidação da nota | **Sim, por cópia** | `resultados/application/consolidacao.py:340-372` copia `Avaliacao.pontuacao` para `ResultadoEtapa.pontuacao`; a `013` decidiu "consolidação é cópia, e não cálculo"; prontidão em `resultados/application/prontidao.py` | Nada — recebe o total |
| Classificação | **Sim** | `classificacao/application/calculo.py` lê `ResultadoEtapa.vigentes`; `combinacao.combinar` (soma ou média ponderada); `desempate.py`; `emissao.emitir_ordem`; publicação em `divulgacao/application/publicar.py` | Nada. Desempate por critério (L-3) fica fora |
| Recursos | **Sim, com duas vias de alterar nota** | `recursos/application/julgar.py`: correção fixada (`_superar`, Resultado sucessor com `origem=RECURSO`) e reavaliação determinada (nova avaliação, consolidada como sucessora); vedação de piora; ordem desatualizada detectada por `classificacao/domain/universo.py` | Na correção fixada, o detalhamento — senão o total diverge da parcela que o candidato vê |
| Auditoria | **Sim** | `avaliacoes/application/trilha.py` (`auditar`, sem nota na trilha); reabertura com motivo e ato administrativo; `ConclusaoAvaliacao` preserva o que foi concluído antes de cada reabertura | Nada |
| Publicação e congelamento | **Sim** | `publish_edital.py::_stages`; `SCHEMA_VERSION = 20` (`shared/canonical.py`); elevação por degraus (`publicacoes/domain/elevacao.py`); Retificação por contrato de mutabilidade (`editais/domain/mutabilidade.py`) | Degrau 21 com `criteria`; o par no contrato |
| Retificação depois de avaliar | **Sim, a jusante** | Concluir recusa `versao_mudou` (`avaliacao.py:243`); `resultados/domain/compatibilidade.py::CAMPOS_COMPARADOS` bloqueia consolidar conclusão sob norma divergente | O barema entre os campos comparados |
| Multiunidade e permissão | **Sim** | Mesa: `institution_scope` na view e `pode_avaliar_inscricao` (`avaliacoes/domain/autorizacao.py:43`); elaboração e Retificação pelas permissões do Edital | Nada |
| Acompanhamento da comissão | **Sim** | Distribuição (`interface/views.py:6921`, `distribuicao.html`): atribuídas e concluídas por avaliador, pendências | Nada |
| O que o candidato vê | **Sim, o total** | `portal/templates/portal/acompanhamento.html:139-185` via `resultados/application/selectors.py::resultados_visiveis`; parecer em desfavorável | O detalhamento sob a nota |
| PDF do Edital | **Sim, a Etapa** | `publicacoes/infrastructure/pdf.py::_etapas` e `frase_da_etapa` imprimem caráter, peso, mínima, máxima | A tabela do barema |

### A resposta

**O barema é extensão, e não funcionalidade nova.** A lacuna é uma só, vista de três lados: a Etapa
não conhece as parcelas, a Avaliação não as registra, e quem vê o total (comissão, candidato,
julgador) não as vê. Tudo o que vem depois do total — Resultado, ordem, publicação, recurso,
reemissão — já existe e só precisa continuar recebendo o mesmo número.

### Os fluxos que não devem ser confundidos

A convocação tem sua própria entrega documental (`convocacao/models.py`: `ItemDaListaDaConvocacao`,
`ApresentacaoDeDocumento`, `ConferenciaDeDocumento`; momento `AT_CALL`), conferida por autorização
própria (`AlocacaoAConferencia`). Ela verifica requisito para ocupar vaga, e não pontua. O barema se
liga **só** aos Documentos Exigidos do momento da inscrição, que a Mesa já mostra.

## 3. O que os Editais da amostra pedem

Extraídos por `pdftotext -layout` dos PDFs de `~/Downloads`.

| Edital | Ficha | Forma das linhas | Observação |
|---|---|---|---|
| 14/2026 Orientador de TFC | Anexo IV, 100 pontos | Doutorado 20 (1); Mestrado 15 (1); Lato sensu 5 por certificado até 10; Curso de formação 15 (1); Docência EaD 1 por mês ou fração > 15 dias, até 40 | Entrevista (Anexo V) por faixas, cinco categorias com máxima — pontuação direta. Desempate por meses de docência |
| 140/2025 Tutor presencial | Anexo IV por curso, 100 | Mesma forma do 14 | **Tetos diferem por curso** (Doutorado 25 ou 20) |
| 90/2026 Tutor TADS | Anexo IV, 100 | Mesma forma | — |
| 173/2025 Designer educacional | Anexo IV, 100 | Experiência 5 por semestre até 30; Doutorado 25; Mestrado 20; Especialização 15; Aperfeiçoamento 10 | **Autopontuação vinculante**: "não sendo atribuída pontuação que exceda à informada pelo candidato" |

Em todos: a soma dos tetos é a máxima da Etapa; títulos aparecem como linhas independentes, sem
regra escrita de exclusividade; "só serão pontuados os títulos que excederem os exigidos no perfil"
é juízo da comissão; a comprovação vai num arquivo único.

## D-001

**O barema mora na Etapa** — uma coleção `criteria` dentro de `EtapaAvaliacao`, no molde dos critérios
de desempate dentro do marco classificatório (coleção aninhada, `id` preservado, ordem pela posição).

*Por que basta:* a Etapa já é do Edital e vale para todos os Perfis, então o cenário 5 (várias vagas,
mesmos critérios) se resolve sem cópia nem modelo. A pontuação já é validada contra a Etapa; o
resultado já é por Etapa.

*Descartadas:* no Perfil (multiplicaria a configuração no caso comum e anteciparia a decisão de
alcance da Etapa, P-5); biblioteca de baremas (sem caso que reuse entre Editais — o reaproveitamento
de Edital inteiro já copia); entidade "Barema" própria (seria um nível sem atributo).

## D-002

**Duas formas de pontuar, deduzidas de `pontos por unidade`.** Presente: o avaliador informa a
quantidade, e a parcela é `min(q × pontos, máxima)`. Ausente: o avaliador informa os pontos, de zero
à máxima.

*Por que basta:* cobre todas as linhas dos quatro Editais — valor fixo (quantidade 0 ou 1), por
certificado, por mês, por semestre — e a ficha de entrevista por faixas (direta). A contagem de meses
e de frações é juízo humano, e fica com o humano, que informa a quantidade.

*Descartadas:* campo de tipo (redundante com a ausência); faixas estruturadas (a faixa não restringe
nada que a máxima já não restrinja); grupos e exclusividade (nenhum Edital da amostra os escreve,
P-1); fórmulas.

## D-003

**A máxima da Etapa é a soma das máximas dos critérios**, mostrada pela tela e conferida na
publicação. Os quatro Editais fecham assim. Manter o campo `maximumScore` (em vez de derivá-lo só na
leitura) preserva tudo o que já o lê — `validar`, a compatibilidade, o PDF, a classificação — sem
mudança.

*Descartada:* teto da Etapa menor que a soma (nenhum Edital o pede).

## D-004

**O detalhamento é um JSON na linha que já existe**: `Avaliacao.criterios`, `ConclusaoAvaliacao.criterios`
e `DecisaoRecurso.criterios`, lista de `{criterionId, quantidade, pontos, parcela, justificativa}`.
O total continua em `pontuacao`.

*Por que basta:* o detalhamento é sempre lido e escrito junto com a conclusão, nunca consultado por
critério; a regra que o valida é do domínio (contra o conteúdo da versão), não do banco; e nenhuma
tabela nova entra na contagem das append-only. As duas tabelas que já guardam a conclusão e a decisão
já são protegidas.

*O cuidado:* o gatilho `avaliacao_concluida_imutavel` enumera colunas, e a coluna nova precisa entrar
na lista da função — senão a reabertura poderia reescrever o detalhamento junto.

*Descartada:* tabela `PontuacaoDeCriterio` (uma linha por critério × avaliação) — três tabelas novas
(rascunho, conclusão, decisão), gatilhos e contagem, para uma leitura que é sempre do conjunto.

## D-005

**Uma função de domínio calcula o total**, em `avaliacoes/domain/barema.py`: recebe o barema da
versão e o detalhamento, valida, aplica os limites e devolve parcelas e total em `decimal(7,4)`. A
Mesa e a correção fixada a chamam; o cliente nunca envia o total.

## D-006

**A mudança de barema depois de conclusões não ganha trava nova.** Concluir já recusa versão mudada;
consolidar já recusa conclusão sob norma divergente, desde que o barema entre em `CAMPOS_COMPARADOS`
(identidade, máxima e pontos por unidade; nome, descrição e documento são redação, como os rótulos).
É o tratamento que a máxima publicada já recebe.

*Descartada:* bloquear a Retificação do barema depois da primeira conclusão — seria regra nova sobre a
Retificação, que hoje não trava nenhum campo da Etapa por esse motivo.

## D-007

**A comprovação é o vínculo opcional a um Documento Exigido da inscrição.** Nada de upload por
critério: o candidato continua anexando um PDF por documento, e a Mesa continua abrindo o arquivo no
painel. O vínculo faz duas coisas — mostra ao candidato o que o documento comprova, e põe o "Abrir"
na linha do critério.

*Descartadas:* documento por critério (multiplicaria os envios para títulos que os Editais pedem num
arquivo só); flag "passível de pontuação" no documento (o vínculo já diz isso).

## D-008

**Justificativa obrigatória só no zero de documento apresentado** — o indeferimento, que é o caso
contra o qual o recurso se dirige. Redução parcial ("três certificados, reconheço dois") pede a
justificativa opcional e o parecer, que já existe. Exigir em toda redução pediria a expectativa do
candidato (P-4).

## D-009

**Três incrementos, cada um útil sozinho.** A — configurar, publicar, imprimir (o PDF sai com a
ficha). B — pontuar, consolidar, mostrar ao candidato (o total passa a ser provado). C — corrigir por
recurso com detalhamento. Antes do C, a correção fixada continua aceitando o total, e a tela do
candidato mostra, num Resultado de recurso, o total sem detalhamento e a frase "corrigido por
recurso" que já existe.
