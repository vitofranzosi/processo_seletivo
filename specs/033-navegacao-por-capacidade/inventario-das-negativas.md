# Inventário das negativas de `interface/views.py` — T003

**Método**: varredura de AST de `backend/processo_seletivo/interface/views.py`, em 18/09/2026. Cada
`raise Http404` foi localizado, a função que o contém foi identificada pela árvore, e a classificação
saiu do **`if` que guarda o `raise`** — não da leitura da definição da função, que é o que produziu os
três erros de medição anteriores.

**Nenhuma repartição prévia foi assumida.** Nem "4 e 71", nem "5 e 70". O que está abaixo foi contado.

## O que a varredura contou

| Medida | Valor |
|---|---|
| `raise Http404` | **75** |
| Funções distintas que os contêm | **59** |
| Dessas, que recebem `request` | **53** |

## A repartição, que é o que esta tarefa existe para produzir

| Classe | Quantos | Esta feature toca? |
|---|---|---|
| Propagação de 404 que o **domínio** declarou, depois de a porta já ter autorizado | **23** | não |
| **Escopo institucional ∪ objeto inexistente** — indistinguíveis porque a consulta filtra por escopo | **22** | não — é a invariante que a `FR-487` fixa |
| **Objeto inexistente** puro | **17** | não |
| **Recusa de autorização** | **11** | **sim — é a superfície** |
| Estado do agregado, não autorização | **1** | não |
| Não autenticado | **1** | não |

### As 11 recusas de autorização, e onde elas moram

**Quatro** são as portas que `spec.md` e `plan.md` já nomeiam:

| Linha | Porta | O que pergunta |
|---|---|---|
| 3611 | `_processo_para_gerir` | base composta |
| 3848 | `_etapa_para_distribuir` | base composta — **e escopo no mesmo `if`** |
| 4818 | `_edital_para_classificar` | base composta **ou** auditoria, conforme o modo |
| 6126 | `_etapa_para_auditar` | base composta **ou** auditoria |

**Sete não estão descritas em lugar nenhum dos artefatos** — e é sobre elas que a `T004` para:

| Linha | Função | O que recusa | Onde a decisão mora |
|---|---|---|---|
| 331 | `criar_edital` | capacidade `edital:criar`, nomeada | na view |
| 1011 | `anexo_do_rascunho` | conjunto de **três** capacidades, cada uma suficiente | na view |
| 1269 | `reaproveitar` | capacidade `edital:elaborar`, nomeada | na view |
| 3395 | `supervisao` | **base composta** — `pode_supervisionar` devolve literalmente `pode_gerir_comissao` | na view |
| 6269 | `minha_etapa` | **base composta** — alocação na Etapa **ou** gestão da comissão | na view |
| 4401 | `inscricao_da_mesa` | vínculo de **Atribuição** | em `avaliacoes/application/mesa.py::_autorizar` |
| 4624 | `documento_da_mesa` | vínculo de **Atribuição** | idem |

**As duas portas já corretas não aparecem nesta lista, e é o esperado**: `_edital_para_publicar` e
`_peca_para_julgar` recusam por capacidade com **403**, não com `Http404`. Os `raise Http404` que elas
contêm (5834 e 6459) são escopo institucional, e ficam como estão.

`_ato_para_publicar` (5841) também não aparece: ela não recebe ator e busca o ato dentro de um Edital
já autorizado. O 404 dela é objeto inexistente, como `research.md` já dizia.

## As sete, uma a uma — por que não são descuido

Nenhuma delas improvisou por falta de cuidado. **Cada uma justifica o 404 no próprio comentário**, e
três invocam doutrina de spec anterior:

- `criar_edital`: *"distinguir 'não existe' de 'você não pode' diria a quem não alcança que o Processo
  existe"*.
- `anexo_do_rascunho`: *"A recusa é 404, e não 403: dizer 'existe, mas você não pode' já entregaria
  que existe"*.
- `supervisao`: *"Tudo o que o ator não alcança responde a mesma coisa que um Processo inexistente
  responderia"* — e cita requisito e critério da `022` por identificador.
- `minha_etapa`: *"A mesma resposta para Etapa não alocada, de outro Processo ou de outro escopo: a
  existência não é enumerável por quem não tem acesso"*.
- `mesa._autorizar`: *"Inscrição de outro avaliador, alocação removida, escopo divergente ou inscrição
  que não existe: uma resposta só"*.

**Três delas misturam escopo e autorização na mesma resposta de propósito** — `supervisao`,
`minha_etapa` e `mesa._autorizar` —, que é a mesma estrutura que a `FR-488` manda separar na porta da
distribuição. Separá-las é trabalho da mesma natureza, e não está em tarefa nenhuma.

**E `mesa._autorizar` tem um argumento próprio a favor do 404 uniforme**: o que ela esconde é a
inscrição **de outro avaliador**. Distinguir ali aproxima o oráculo de enumeração que a `R-8` do
`research.md` reconhece como legítimo no canal do candidato.

## O veredito da T004

**A superfície medida é maior do que a que os artefatos descrevem.** A `spec.md` diz, em *Assumptions*,
que *"se o inventário encontrar recusa de autorização fora das portas já identificadas, o tamanho da
feature mudou — e isso é conversa de escopo com quem governa o backlog, não decisão de quem
implementa."*

Ele encontrou **sete**.

**A decisão, de 2026-09-18, foi manter o escopo nas quatro portas.** Ela é de quem governa o backlog,
e não de quem implementa. O que a decisão pesou:

- **Nenhuma das sete é descuido**, e três citam doutrina de spec anterior por identificador.
  Corrigi-las contradiria a `022` — o que é conversa de spec, não de implementação.
- **Três misturam escopo e vínculo na mesma resposta.** Cada uma é o mesmo trabalho que a `FR-488`
  manda fazer na porta da distribuição, e nenhuma tem tarefa que o descreva.
- **`mesa._autorizar` tem argumento próprio a favor do 404 uniforme**, e ele não é fraco.

**O que muda nos artefatos, e só isso:** a `SC-165` passa a se recortar às portas desta feature — o
mesmo recorte que a `FR-476` já praticava, e pela mesma razão. A `T030` fecha sem código, entregando
este registro. As sete ficam aqui, nomeadas, para a spec que as tratar.

---

## A tabela inteira — as 75, e a âncora do detector

Esta tabela é o registro de que trata a `T038`. O detector não a lê por número de linha, que muda a
cada edição: ele refaz a varredura e compara o conjunto de pares **(função, classe)**. Um
`raise Http404` novo numa função que já está aqui não acorda ninguém; **um numa função que não está
reprova**, e obrigar quem o escreveu a classificá-lo é o ponto.

| Linha | Função | Recebe o ator | É uma das seis portas | Classe | Por quê |
|---|---|---|---|---|---|
| 337 | `criar_edital` | sim | não | recusa de autorização | capacidade `edital:criar`, nomeada · **fora dos seis helpers** |
| 939 | `anexos_acao` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo; fora de escopo e inexistente caem no mesmo `is None` |
| 978 | `anexos_acao` | sim | não | objeto inexistente | ação de formulário desconhecida |
| 1015 | `anexo_do_rascunho` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 1017 | `anexo_do_rascunho` | sim | não | recusa de autorização | conjunto `LEITURA_DO_RASCUNHO` — três capacidades, cada uma suficiente · **fora dos seis helpers** |
| 1020 | `anexo_do_rascunho` | sim | não | objeto inexistente | anexo inexistente dentro de Edital já autorizado |
| 1033 | `compor_etapa` | sim | não | objeto inexistente | chave de etapa fora do vocabulário da rota |
| 1036 | `compor_etapa` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 1264 | `reaproveitar` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 1275 | `reaproveitar` | sim | não | recusa de autorização | capacidade `edital:elaborar`, nomeada · **fora dos seis helpers** |
| 1280 | `reaproveitar` | sim | não | estado do agregado | situação do Edital, não autorização |
| 1742 | `fragmento_documento` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 1795 | `_edital_do_fragmento` | sim | não | não autenticado | fragmento HTMX não redireciona para identificar-se |
| 1798 | `_edital_do_fragmento` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 2085 | `fragmento_etapa` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 2161 | `fragmento_retificacao_linha_do_quadro` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 2164 | `fragmento_retificacao_linha_do_quadro` | sim | não | objeto inexistente | Edital sem versão base — ausência de conteúdo |
| 2200 | `fragmento_remover` | sim | não | objeto inexistente | alvo de remoção fora do formato da rota |
| 2239 | `_edital_com_previa` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 2343 | `detalhe` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 2496 | `praticar_ato` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo; e ato de vocabulário desconhecido |
| 2711 | `retificar` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 2874 | `_retificacao_do_ator` | sim | não | escopo institucional ∪ inexistente | `_retificacao_do_ator` filtra por `edital__institution_scope` |
| 3112 | `praticar_ato_retificacao` | sim | não | objeto inexistente | ato de vocabulário desconhecido |
| 3365 | `auditoria` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo |
| 3425 | `_processo_do_ator` | sim | não | escopo institucional ∪ inexistente | `_processo_do_ator` filtra por `institution_scope` |
| 3501 | `supervisao` | sim | não | recusa de autorização | base composta — `pode_supervisionar` **é** `pode_gerir_comissao` · **fora dos seis helpers** |
| 3523 | `praticar_ato_processo` | sim | não | objeto inexistente | ato de vocabulário desconhecido |
| 3652 | `exportar_matriculas` | sim | não | escopo institucional ∪ inexistente | consulta filtra por escopo; a autorização vem depois, por `require_permission` (403) · **acrescentada pela `031`, e detectada pela `T038`** |
| 3955 | `comissao` | sim | não | propagação de 404 do domínio | 404 que o domínio declarou, depois de a porta já ter autorizado |
| 4056 | `alocacoes` | sim | não | propagação de 404 do domínio | idem |
| 4106 | `_etapa_para_distribuir` | sim | sim | recusa de autorização | **porta `_etapa_para_distribuir`** — base composta **e escopo no mesmo `if`** (FR-488) |
| 4116 | `_etapa_para_distribuir` | sim | sim | objeto inexistente | Etapa fora do conteúdo vigente |
| 4166 | `impedimentos` | sim | não | propagação de 404 do domínio | idem |
| 4236 | `reabrir_avaliacao` | sim | não | propagação de 404 do domínio | idem |
| 4271 | `consolidar_resultados` | sim | não | propagação de 404 do domínio | idem |
| 4303 | `consolidar_resultados` | sim | não | propagação de 404 do domínio | idem |
| 4372 | `registrar_ocorrencia` | sim | não | propagação de 404 do domínio | idem |
| 4450 | `remover_atribuicao` | sim | não | propagação de 404 do domínio | idem |
| 4551 | `distribuicao` | sim | não | propagação de 404 do domínio | idem |
| 4648 | `_mesa_do_avaliador` | sim | não | escopo institucional ∪ inexistente | consulta filtra por `institution_scope` |
| 4663 | `inscricao_da_mesa` | sim | não | recusa de autorização | vínculo de **Atribuição**, decidido em `mesa._autorizar` e propagado como 404 · **fora dos seis helpers e fora de `views.py`** |
| 4825 | `_registrar_avaliacao` | sim | não | propagação de 404 do domínio | idem |
| 4886 | `documento_da_mesa` | sim | não | recusa de autorização | idem — `mesa._autorizar` · **fora dos seis helpers e fora de `views.py`** |
| 5083 | `_edital_para_classificar` | sim | sim | escopo institucional ∪ inexistente | **porta `_edital_para_classificar`** — consulta filtra por escopo |
| 5112 | `ordenacao` | sim | não | propagação de 404 do domínio | idem |
| 5287 | `_perfil_do_marco` | não | não | objeto inexistente | marco sem Perfil no conteúdo publicado |
| 5318 | `emitir_ordenacao` | sim | não | propagação de 404 do domínio | idem |
| 5381 | `emitir_ordenacao` | sim | não | propagação de 404 do domínio | idem |
| 5403 | `corte_historico` | sim | não | objeto inexistente | corte inexistente dentro de Edital já autorizado |
| 5471 | `_identidade_ou_404` | não | não | objeto inexistente | identificador que não é UUID |
| 5507 | `corte` | sim | não | propagação de 404 do domínio | idem |
| 5878 | `atestar_view` | sim | não | objeto inexistente | inscrição inexistente — a porta vem depois, na linha seguinte |
| 5944 | `_instante_ou_none` | não | não | objeto inexistente | instante que não se analisa |
| 6004 | `emitir_corte_view` | sim | não | propagação de 404 do domínio | idem |
| 6036 | `continuar_corte_view` | sim | não | propagação de 404 do domínio | idem |
| 6049 | `ato_de_ordenacao` | sim | não | objeto inexistente | ato inexistente dentro de Edital já autorizado |
| 6124 | `_edital_para_publicar` | sim | sim | escopo institucional ∪ inexistente | **porta `_edital_para_publicar`** — consulta filtra por escopo; a recusa por capacidade dela já é 403 |
| 6131 | `_ato_para_publicar` | não | não | objeto inexistente | `_ato_para_publicar` não recebe ator: não é porta |
| 6181 | `_renderizar_previa` | sim | não | propagação de 404 do domínio | idem |
| 6256 | `publicar_resultado` | sim | não | propagação de 404 do domínio | idem |
| 6417 | `_etapa_para_auditar` | sim | sim | escopo institucional ∪ inexistente | **porta `_etapa_para_auditar`** — consulta filtra por escopo |
| 6426 | `_etapa_para_auditar` | sim | sim | recusa de autorização | **porta `_etapa_para_auditar`** — base composta **ou** auditoria |
| 6557 | `minha_etapa` | sim | não | escopo institucional ∪ inexistente | consulta filtra por `institution_scope` |
| 6563 | `minha_etapa` | sim | não | recusa de autorização | base composta — alocação **ou** gestão · **fora dos seis helpers** |
| 6575 | `minha_etapa` | sim | não | objeto inexistente | Etapa fora do conteúdo vigente |
| 6714 | `recursos_do_edital` | sim | não | escopo institucional ∪ inexistente | `obter_edital` filtra por escopo; a autorização vem depois, por `require_permission` (403) |
| 6753 | `_peca_para_julgar` | sim | sim | escopo institucional ∪ inexistente | **porta `_peca_para_julgar`** — escopo; a capacidade vem depois, por `require_permission` (403) |
| 7013 | `sorteio` | sim | não | propagação de 404 do domínio | idem |
| 7120 | `publicar_relacao_do_sorteio` | sim | não | propagação de 404 do domínio | idem |
| 7176 | `observar_ocorrencia_do_sorteio` | sim | não | propagação de 404 do domínio | idem |
| 7211 | `realizar_sorteio` | sim | não | propagação de 404 do domínio | idem |
| 7243 | `anular_o_sorteio` | sim | não | propagação de 404 do domínio | idem |
| 5105 | `_recorte_pedido` | sim | não | objeto inexistente | **acrescentada pela `034`** — `?lista=` que não corresponde a Modalidade alguma do Perfil (`FR-499`). Recorte inexistente e recorte vazio são coisas diferentes: confundi-los esconde erro de digitação, e a `FR-492a` fez da ordem vazia um estado legítimo justamente para que a distinção exista. Não é escopo nem autorização — a porta do Edital já filtrou os dois antes |
| 1961 | `fragmento_perfil_duplicado` | sim | não | objeto inexistente | **acrescentada pela `043`** — pedido sem o parâmetro `edital`: não há Edital de que duplicar. O escopo vem **depois**, por `_edital_do_fragmento` (404, como a tela), e a autorização por `pode_compor`, que responde **403** — quem alcança o Edital e não o compõe já sabe que ele existe (`043`, R-006) |

---

## O que aconteceu depois da medição

**Os números acima são do dia da medição, 18/09/2026, e o arquivo não os reescreve** — ele
acrescenta. A repartição é o registro de uma leitura; apagá-la para manter o total em dia faria
perder justamente o que ela serve para explicar.

O que mudou desde então, e por quê:

| | |
|---|---|
| **75 → 72** | as quatro portas desta feature deixaram de decidir autorização com `raise Http404`: a decisão passou a `require_authorization_base`, e três dos pontos sumiram com ela. O de `_etapa_para_distribuir` não sumiu — ele **se dividiu**, e o que restou é o do escopo (`FR-488`) |
| **72 → 73** | a `031` acrescentou `exportar_matriculas` |

**A linha da `031` é o detector funcionando, e na primeira oportunidade real.** Ela não veio desta
feature: entrou pela `main`, no merge, e a `T038` reprovou a suíte pedindo que fosse classificada.
Ela está **certa** — a consulta filtra por escopo, e a autorização vai por `require_permission`, que
responde 403 —, e é exatamente por isso que o caso importa: o detector não julga a gramática, ele
obriga alguém a olhar. Uma porta com a gramática antiga teria entrado do mesmo jeito, e a diferença
é que agora alguém teria de dizer isso por escrito.
