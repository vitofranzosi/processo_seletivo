# Contrato: inventário das rotas do não publicado

**O guardião lê esta tabela** (`tests/test_rotas_do_nao_publicado.py`, `D-008`, FR-3525). Toda rota
de `interface/urls.py` que recebe `processo_id`, `edital_id` ou `retificacao_id`, e todo fragmento,
tem de ter uma linha aqui. A primeira coluna é o `name` da rota, entre crases; a segunda é a classe.

Medido em 01/11/2026 sobre `32097602`. Rota nova sem linha reprova a suíte.

## As classes

| Classe | O que a rota faz com Edital não publicado ou Retificação em curso | Porta exigida |
|---|---|---|
| **C** | Exibe conteúdo (vocabulário da spec) | `_edital_para_ler(exige=CONTEUDO)` ou `_retificacao_para_ler(exige=CONTEUDO)` |
| **E** | Exibe a existência, e o conteúdo só a quem o tem (o detalhe reduzido, a lista, o Processo) | a regra em lote, ou `_edital_para_ler(exige=EXISTENCIA)` / `_processo_para_ler` |
| **P** | Só opera sobre Edital publicado; diante do não publicado recusaria por estado, e o estado não pode vazar | `_edital_para_ler(exige=EXISTENCIA)` antes de qualquer conferência de estado (FR-3527) |
| **B** | Base própria **mais estrita** que a existência: só passa quem já a tem (a tabela diz por quê) | nenhuma nova; a matriz prende o motivo |
| **A** | A trilha de auditoria (`D-005`) | a de hoje |
| **F** | Não lê Edital, Retificação nem Processo | nenhuma |

O guardião confere duas coisas: a linha existe; e, nas classes **C**, **E** e **P**, a função da
view (ou a que ela delega) chama a porta exigida.

## Processo

| Rota | Classe | Nota |
|---|---|---|
| `processo-detalhe` | E | Omite Editais não publicados; Processo sem nenhum alcançável e sem vínculo → 404 (FR-3513) |
| `processo-ato` | E | Idem, na lista de Editais pendentes do GET |
| `supervisao` | E | Já recusa sem `pode_supervisionar`; o pulso não pode contar Edital não publicado a quem não tem a existência |
| `edital-criar` | B | `edital:criar` — só o gestor, que tem `rascunho:ler` |
| `comissao` | B | `pode_gerir_comissao` — gestor ou presidência, ambos com a existência |
| `alocacoes` | B | Idem; `editais_alocaveis` lista Editais do Processo a quem já tem a existência deles |
| `auditoria-comissao` | B | Auditoria da comissão; quem a abre tem `auditoria:consultar` ou preside |

## Edital — conteúdo e fluxo

| Rota | Classe | Nota |
|---|---|---|
| `detalhe` | E | Detalhe reduzido a quem só tem a existência (FR-3509); seção de Retificações em curso só com o conteúdo dela (FR-3510) |
| `compor` | C | Redireciona; a porta vem antes, para o redirecionamento não confirmar a existência |
| `compor-etapa` | C | GET e POST, em leitura e em edição (FR-3511, EC-5) |
| `reaproveitar` | C | Hoje recusa sem `edital:elaborar`; a porta vem antes |
| `previa` | C | A porta antes do 409 de estado (EC-4) |
| `previa-documento` | C | Idem |
| `anexos` | C | POST; o comando confere `edital:elaborar` depois |
| `anexo-arquivo` | C | Substitui `LEITURA_DO_RASCUNHO` (FR-3507, P-2) |
| `ato` | C | Edital não publicado: conteúdo. Edital publicado (encerrar, cancelar): a regra devolve `CONTEUDO` a todo ator do escopo, e os atos seguem conferindo a própria capacidade |
| `retificar` | E | Edital publicado; a lista das Retificações em curso só com o conteúdo delas (FR-3512) |
| `auditoria` | A | `D-005` |

## Edital — só publicado

| Rota | Classe | Nota |
|---|---|---|
| `duvidas` | P | Validação do assistente (070) |
| `assistente` | P | Piloto (071) |
| `assistente-nova` | P | Idem |
| `assistente-prototipo` | P | Protótipo (074), só local |
| `assistente-prototipo-perguntar` | P | Idem |
| `assistente-prototipo-sugestao` | P | Idem |
| `assistente-prototipo-nova` | P | Idem |
| `relatorio-do-edital` | P | Hoje recusa por estado (409) **depois** de `pode_gerir_comissao`; a porta vem antes |
| `relatorio-do-edital-pdf` | P | Idem |
| `exportar-matriculas` | P | O exportador não tem a existência |
| `inscricoes` | P | `inscricao:consultar` |
| `recursos` | P | O julgador não tem a existência |
| `avisos-do-edital` | P | `aviso:enviar` |
| `distribuicao` | P | Etapa de Edital publicado |
| `consolidar-resultados` | P | Idem |
| `registrar-ocorrencia` | P | Idem |
| `distribuicao-remover` | P | Idem |
| `impedimentos` | P | Idem |
| `reabrir-avaliacao` | P | Idem |
| `trilha-da-avaliacao` | P | Idem |
| `resultados-da-etapa` | P | Idem |
| `conclusoes-preservadas` | P | Idem |
| `ordenacao` | P | Marco de Edital publicado |
| `emitir-ordenacao` | P | Idem |
| `corte-historico` | P | Idem |
| `ato-de-ordenacao` | P | Idem |
| `corte` | P | Idem |
| `emitir-corte` | P | Idem |
| `continuar-corte` | P | Idem |
| `ocupacao` | P | Idem |
| `emitir-apuracao` | P | Idem |
| `causar-faixa` | P | Idem |
| `acrescentar-vagas` | P | Idem |
| `desfazer-acrescimo` | P | Idem |
| `ocupacao-historico` | P | Idem |
| `convocacao` | P | Idem |
| `convocar` | P | Idem |
| `convocar-titulares` | P | Idem |
| `nao-atendimento-dos-vencidos` | P | Idem |
| `emitir-pendentes` | P | Idem |
| `convocacao-historico` | P | Idem |
| `desfechar` | P | Idem |
| `comunicar-convocacao` | P | Idem |
| `sorteio` | P | Idem |
| `publicar-relacao-do-sorteio` | P | Idem |
| `observar-ocorrencia-do-sorteio` | P | Idem |
| `realizar-sorteio` | P | Idem |
| `anular-sorteio` | P | Idem |
| `previa-de-publicacao` | P | Idem |
| `publicar-resultado` | P | Idem |
| `publicacoes-do-marco` | P | Idem |
| `aviso-do-resultado` | P | Idem |
| `aviso-da-chamada` | P | Idem |
| `marco` | P | Idem |
| `gesto-do-marco` | P | Idem |
| `minha-etapa` | B | Alocação na Etapa, com 404 uniforme (inventário da `033`); só há Etapa alocada em Edital publicado |
| `mesa-inscricao` | B | Atribuição da inscrição; idem |
| `mesa-avaliacao-gravar` | B | Idem |

**Por que as rotas P recebem a porta em vez de ficarem como estão.** Elas não exibem conteúdo não
publicado, mas recusam o Edital não publicado **por estado** — um 409 ou um `DomainError` de
"Edital não publicado" que diz ao integrante, ao julgador e ao exportador que aquele identificador é
um Edital da unidade em preparação. A porta de existência, antes, transforma isso em "não
encontrado". Para Edital publicado ela não custa consulta além da que já lê as Publicações.

## Retificação

| Rota | Classe | Nota |
|---|---|---|
| `retificacao-detalhe` | C | FR-3512 |
| `retificacao-editar` | C | A porta antes da recusa de `retificacao:elaborar` |
| `retificacao-ato` | C | FR-3512 |

## Fragmentos

| Rota | Classe | Nota |
|---|---|---|
| `fragmento-etapa` | C | Lê o rascunho |
| `fragmento-documento` | C | Idem |
| `fragmento-perfil` | C | `_edital_do_fragmento`, por `?edital=` |
| `fragmento-perfil-duplicado` | C | Hoje 403 por `pode_compor`; a porta vem antes |
| `fragmento-marco` | C | `_edital_do_fragmento` |
| `fragmento-marco-recomposto` | C | Idem |
| `fragmento-previa-da-classificacao` | C | Idem; usa `edital_snapshot` |
| `fragmento-criterio` | C | Idem |
| `fragmento-previa-da-classificacao-fechar` | F | Fecha o painel |
| `fragmento-modalidade` | F | Não lê o Edital |
| `fragmento-quadro` | F | Idem |
| `fragmento-fato` | F | Idem |
| `fragmento-evento` | F | Idem |
| `fragmento-remover` | F | Idem |
| `fragmento-retificacao-perfil` | F | Lê só o conteúdo vigente, publicado |
| `fragmento-retificacao-evento` | F | Idem |
| `fragmento-retificacao-anexo` | F | Idem |
| `fragmento-retificacao-linha-do-quadro` | P | Recebe `edital_id`; Edital publicado |
| `fragmento-retificacao-modalidade` | P | Idem |
| `fragmento-retificacao-criterio` | P | Idem |

## Telas sem identificador que exibem Editais

Não entram no guardião, que seleciona por identificador na rota; entram na matriz da FR-3524.

| Rota | O que muda |
|---|---|
| `lista` | Filtro em lote (FR-3508, `D-006`) |
| `visao-geral` | A mesma regra (FR-3514) |
| `agenda` | Nada; teste prende que só há publicado (FR-3516) |
| `trilha-da-unidade` | Nada; não mostra Edital |
| `minhas-etapas` | Nada; só Etapa de Edital publicado |
