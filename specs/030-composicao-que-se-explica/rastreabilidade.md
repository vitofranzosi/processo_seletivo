# Rastreabilidade — 030 · A composição que se explica

Cada requisito, onde foi feito e onde é verificado. É o Princípio V: um requisito sem linha aqui é
um requisito que ninguém sabe se entrou.

Caminhos relativos a `backend/`. Abreviações dos arquivos de teste:

| Apelido | Arquivo |
|---|---|
| `forma` | `tests/unit/editais/test_forma_da_ordem.py` |
| `round-trip` | `tests/interface/test_round_trip_do_rascunho.py` |
| `compor` | `tests/interface/test_compor_classificacao.py` |
| `escolha` | `tests/interface/test_campos_que_a_escolha_governa.py` |
| `quadro` | `tests/interface/test_compor_quadro.py` |
| `acessibilidade` | `tests/interface/test_acessibilidade_da_classificacao.py` |
| `derivacao` | `tests/integration/editais/test_derivacao_nao_alcanca_o_declarado.py` |
| `distribuicao` | `tests/interface/test_distribuicao.py` |
| `vocabulario` | `tests/test_vocabulario_da_composicao.py` |
| `metodo` | `tests/interface/test_metodo_do_marco.py` |
| `comum` | `tests/integration/editais/test_metodo_comum.py` |
| `congelado` | `tests/integration/sorteios/test_metodo_nao_e_escolha.py` |
| `mutabilidade` | `tests/integration/editais/test_mutabilidade_do_metodo_de_sorteio.py` |
| `contrato` | `tests/contract/test_mutabilidade.py` |
| `tela-do-contrato` | `tests/interface/test_campos_vem_do_contrato.py` |
| `remocao-js` | `tests/javascript/remocao.test.js` |

---

## A pergunta de entrada e a revelação progressiva

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-413** — perguntar primeiro como a ordem é produzida | `editais/models/perfis.py::MarcoClassificatorio.FormaDaOrdem` e o campo `forma_da_ordem`; `interface/templates/interface/_marco.html`, o `select` `-orderProduction` antes de qualquer campo | `compor::test_a_pergunta_de_entrada_vem_antes_de_qualquer_campo_do_marco`, `forma::test_a_forma_declarada_viaja_ate_o_conteudo_publicado`, `::test_a_forma_nao_declarada_nao_vira_padrao_no_modelo` |
| **FR-414** — método do sorteio só quando a ordem nasce de sorteio | `editais/domain/marcos.py::ordena_por_sorteio`; o `{% if marco\|ordena_por_sorteio %}` de `_marco.html`; `interface/views.py::fragmento_marco_recomposto` | `escolha::test_o_cartao_de_sorteio_traz_o_metodo_e_o_de_pontuacao_nao`, `tests/interface/test_hardening_pos_auditoria.py::test_o_bloco_do_sorteio_so_existe_para_quem_sorteia` |
| **FR-415** — combinação e normalização só com duas ou mais Etapas | `marcos.py::pergunta_a_combinacao`; o `{% if marco\|pergunta_a_combinacao %}` de `_marco.html` | `escolha::test_a_combinacao_some_com_uma_etapa_e_volta_com_duas` |
| **FR-416** — com uma Etapa, a tela declara o que a combinação produz | `marcos.py::REGRA_DE_ETAPA_UNICA` (derivação do marco novo), `::combinacao_efetiva` (que **não** sobrescreve o declarado), `::pontuacao_combinada_e_a_da_etapa` (qual das duas frases é verdadeira); o `<p class="declaracao-derivada">` de `_marco.html` | `escolha::test_a_combinacao_some_com_uma_etapa_e_volta_com_duas` |
| **FR-417** — ampla concorrência e reversão só depois da primeira Modalidade | `interface/templates/interface/_perfil.html`, o `{% if perfil.modalidades %}` | `quadro::test_sem_modalidade_a_tela_nao_pergunta_qual_e_a_ampla_nem_a_reversao`, `::test_a_primeira_modalidade_faz_as_duas_perguntas_aparecerem` |
| **FR-418** — o declarado não se perde, e não some em silêncio | os `<input type="hidden">` de `_marco.html` e de `_perfil.html`; `publicacoes/application/publish_edital.py::_metodo_publicado`, a fronteira do outro lado | `round-trip::test_o_metodo_declarado_some_da_tela_e_continua_no_envio`, `::test_o_metodo_guardado_reaparece_quando_a_forma_volta_a_ser_sorteio`, `::test_gravar_outra_etapa_nao_apaga_a_forma_da_ordem`, `forma::test_o_metodo_escondido_pela_troca_de_forma_nao_alcanca_o_publicado`, `quadro::test_o_que_foi_declarado_sobrevive_a_remocao_da_ultima_modalidade` |

## Padrões e derivação

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-419** — padrão editável de casas decimais e arredondamento | `marcos.py::ARREDONDAMENTO_PADRAO`; `interface/views.py::_marco_novo` | `compor::test_o_marco_novo_nasce_com_arredondamento_e_identidade` |
| **FR-420** — código e denominação derivados do Perfil | `marcos.py::identidade_derivada`; `views.py::_marco_novo` | `compor::test_o_marco_novo_nasce_com_arredondamento_e_identidade`, `::test_o_codigo_derivado_desempata_quando_o_perfil_ja_tem_marco` |
| **FR-421** — padrão e derivação não alcançam o declarado, nem em Retificação | `_marco_novo` só é chamado pelo fragmento que **cria** a linha; `interface/retificacao.py::campos_editaveis` lê o publicado e não completa nada | `derivacao::test_o_padrao_nao_reescreve_o_arredondamento_declarado`, `::test_a_retificacao_nao_ve_o_padrao_chegar_por_conta_propria`, `::test_a_derivacao_da_identidade_nao_alcanca_marco_que_ja_tem_codigo`, `::test_a_retificacao_nao_acrescenta_marco_e_por_isso_nao_deriva_nada` |

## O conceito nomeado onde a decisão acontece

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-422** — o que a consolidação produz, antes da ação | `interface/templates/interface/distribuicao.html`, o `<p class="definicoes">` ao lado dos botões | `distribuicao::test_a_tela_declara_o_que_a_consolidacao_produz_antes_da_acao` |
| **FR-423** — por que a Etapa é do Edital e a ordem é do Perfil | `compor_classificacao.html`, o `<p class="definicoes">` do passo | `distribuicao::test_a_tela_declara_o_que_a_consolidacao_produz_antes_da_acao` é do irmão; este é lido por `vocabulario` sobre `compor_classificacao.html` e pela varredura de ajuda visível em `acessibilidade::test_nenhum_cartao_de_composicao_traz_ajuda_visivel` |
| **FR-424** — recorte, geração e faixa definidos no primeiro uso de cada tela | `<dfn>` nas dez telas: `compor_classificacao`, `compor_perfis`, `corte`, `corte_historico`, `ordenacao`, `ocupacao`, `ocupacao_historico`, `sorteio`, `convocacao`, `convocacao_historico` | `vocabulario::test_o_termo_usado_pela_tela_se_define_no_primeiro_uso` (30 casos, um por tela e termo) |
| **FR-425** — linguagem ubíqua, sem termo novo | revisão das definições de FR-422 a FR-424; "Resultado da Etapa" no lugar de "Resultado oficial" | `distribuicao::test_a_tela_declara_o_que_a_consolidacao_produz_antes_da_acao` (afirma o termo do domínio), mais os irmãos `test_vocabulario_do_corte`, `test_vocabulario_da_ocupacao`, `test_vocabulario_da_convocacao` |

## A ajuda ancorada, sem ajuda dentro do cartão

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-426** — o bloco de ajuda não aparece sem item a que se refira | `views.py::_ancora_do_primeiro_marco`; `compor_classificacao.html`, o invólucro `#ajuda-da-classificacao`; `_marco_acrescentado.html`, o `hx-swap-oob` | `compor::test_a_ajuda_da_etapa_nao_aparece_sem_marco_a_que_se_referir`, `::test_a_ajuda_chega_junto_com_o_primeiro_marco_acrescentado` |
| **FR-427** — cada item da ajuda leva ao campo que explica | `_como_preencher_o_marco.html`, os `<a href="#…">`; o `id` do `fieldset` em `_marco.html` | `compor::test_cada_item_da_ajuda_leva_ao_campo_que_explica` |
| **FR-428** — nenhuma ajuda visível dentro dos cartões, e o equivalente assistivo permanece | as duas últimas `.ajuda` de `_modalidade.html` viraram `.oculto`, com o texto no `como-preencher` de `compor_perfis.html` | `acessibilidade::test_nenhum_cartao_de_composicao_traz_ajuda_visivel`, `::test_o_equivalente_para_tecnologia_assistiva_permanece` |

## O método declarado uma vez

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-429** — método declarado uma vez e referenciado por cada marco | `processos/models.py::Edital.metodo_de_sorteio_comum`; `marcos.py::metodo_que_governa`, o ponto único de resolução; `sorteios/domain/metodo.py::metodo_declarado`, que delega; `compor_classificacao.html`, o bloco `edital-draw-*` | `metodo::test_o_metodo_comum_e_declarado_uma_vez_e_os_marcos_o_referenciam`, `::test_a_tela_oferece_o_metodo_comum_no_passo_da_classificacao`, `::test_gravar_outra_etapa_nao_apaga_o_metodo_comum`, `::test_o_fragmento_do_marco_sabe_do_metodo_comum`, `comum::test_o_marco_sem_metodo_proprio_referencia_o_comum`, `mutabilidade::test_o_metodo_comum_se_retifica_pelo_caminho_da_raiz`, `::test_a_retificacao_do_comum_alcanca_o_marco_que_o_referencia` |
| **FR-430** — divergência permitida e registrada explicitamente | a chave `drawMethod` sob o marco continua existindo; `_marco.html`, o resumo e a `declaracao-derivada` do bloco | `metodo::test_o_marco_divergente_registra_a_divergencia_no_conteudo_normativo`, `::test_o_cartao_diz_que_usa_o_comum_e_diz_quando_diverge`, `comum::test_o_metodo_comum_nao_reescreve_o_marco_no_banco` |
| **FR-431** — nada muda no conteúdo já publicado | a chave de raiz é **omitida** quando vazia em `publish_edital.py`; nenhum degrau de elevação foi acrescentado; a migration não percorre linha | `comum::test_o_edital_do_acervo_nao_ganha_chave_no_nivel_do_edital`, `::test_a_resolucao_devolve_o_metodo_literal_do_marco_do_acervo`, `::test_o_edital_sem_sorteio_nao_publica_a_chave`, `congelado::test_o_resumo_congelado_nao_muda_quando_o_edital_ganha_metodo_comum` |

## A Etapa que o sorteio não precisa ter

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-432** — sorteio sem Etapa é aceito; pontuação sem Etapa continua recusada | `marcos.py::exige_etapa`; `editais/domain/perfis.py::validate_classification_milestones` e `editais/domain/validation.py::_coerencia_dos_marcos`, os dois consumindo a mesma função; o `required` condicionado em `_marco.html` | `escolha::test_o_marco_de_sorteio_sem_etapa_e_aceito`, `::test_o_marco_de_pontuacao_sem_etapa_continua_recusado`, `::test_o_marco_que_nao_declara_a_forma_continua_exigindo_etapa`, `acessibilidade::test_o_marco_de_sorteio_nao_exige_etapa_na_tela` |

## Os critérios de sucesso

| Critério | Onde é verificado |
|---|---|
| **SC-138** — menos de 10 perguntas no marco do Edital canônico | `compor::test_o_marco_do_edital_canonico_pede_menos_de_dez_respostas` — **6 controles**, medidos também pela interface em 17/09/2026 |
| **SC-139** — nenhuma pergunta dedutível | `escolha::test_a_combinacao_some_com_uma_etapa_e_volta_com_duas` (as duas dedutíveis somem), `compor::test_o_marco_novo_nasce_com_arredondamento_e_identidade` (as três sem padrão nascem preenchidas) |
| **SC-140** — a regra do sorteio declarada uma vez | `metodo::test_o_metodo_comum_e_declarado_uma_vez_e_os_marcos_o_referenciam` |
| **SC-141** — cada termo definido no primeiro uso | `vocabulario::test_o_termo_usado_pela_tela_se_define_no_primeiro_uso` |
| **SC-142** — o conteúdo publicado antes da feature não muda | `forma::test_marco_que_nao_declara_a_forma_publica_o_conteudo_de_sempre`, `::test_o_metodo_do_marco_sem_forma_declarada_continua_publicado`, `comum::test_o_edital_do_acervo_nao_ganha_chave_no_nivel_do_edital` |

---

## O que a interface encontrou e a suíte não encontraria

Dois defeitos apareceram só ao percorrer a tela, e os dois ganharam teste depois:

| O que era | Onde se fechou |
|---|---|
| Escolher "por sorteio" abria *"Remover Marco classificatório? Isto descarta 6 campos preenchidos"*: `remocao.js` identificava a remoção pela dupla `hx-target="closest fieldset"` + `hx-swap="outerHTML"`, que a recomposição do cartão passou a ter. Um "não" cancelava a recomposição, e a tela não reagia à escolha. | `interface/static/interface/remocao.js`, a guarda de `BUTTON`; `remocao-js::"um campo que recompõe a própria linha não pede confirmação de remoção"` |
| O cartão recomposto dizia *"ainda não declarado"* sobre o método enquanto a tela, ao redor, dizia *"declarado"*: o contexto dos dois fragmentos não carregava `tem_metodo_comum`. | `views.py::fragmento_marco` e `::fragmento_marco_recomposto`; `metodo::test_o_fragmento_do_marco_sabe_do_metodo_comum` |

Nenhum dos dois é alcançável por teste de template: o primeiro vive no `htmx:confirm`, e o segundo
é diferença de **contexto** entre dois caminhos que renderizam o mesmo arquivo.

## O que mudou na suíte por causa desta feature

| | |
|---|---|
| Contagem de partida (17/09/2026) | 5765 passando, 2 pulados |
| Contagem final | **5866 passando, 12 pulados** |
| Casos novos | 111, e **nenhum removido** |
| Pulados novos | 10, todos de `vocabulario`: são os pares tela × termo em que a tela **não usa** aquele termo, e pular é a resposta certa — cobrar definição de palavra ausente seria pedir prosa que ninguém lê |
| Testes existentes que mudaram de forma | 8 — os dois guardiões de contagem de migration, o guardião de campos retificáveis (72 → 82), os três do cartão do marco em `test_hardening_pos_auditoria`, o da ajuda da lista em `test_medida_dos_campos` e o do payload de reaproveitamento |
| Migrations | **duas**: `editais/0021_forma_da_ordem` e `processos/0003_metodo_de_sorteio_comum`, ambas acrescentando coluna sem percorrer linha publicada |
| `makemigrations --check` | *No changes detected* |

**Depois do rebase sobre a `029`**: **6880 passando, 12 pulados**. O salto é dela — a `029` entrou
na `main` pelo PR #123 enquanto esta branch estava aberta —, e o que a conferência mede aqui é a
**convivência**: as duas features tocam `Edital`, o catálogo de mutabilidade, o snapshot e o
guardião de campos retificáveis, e nenhuma das duas perdeu nada.

A colisão que o Git não vê era a das migrations: `029` e `030` nasceram as duas como
`processos/0003`, e dois leaf nodes no mesmo app quebram qualquer `migrate`. A da `030` passou a
ser `0004_metodo_de_sorteio_comum`, dependendo de `0003_requerimento_de_matricula` — renumerada, e
não reescrita: nenhuma das duas foi aplicada em produção. Os campos retificáveis passaram de 72 a
**83**: um da `029` e dez da `030`.

**Os dois pulados de partida permanecem** e continuam sendo os deliberados: o que só roda fora do
PostgreSQL e o E2E contra o serviço real da Caixa, atrás de `SORTEIO_E2E_FONTE_REAL`.

## O que a revisão encontrou, e onde cada achado se fechou

Sete achados, revisados sobre o diff não commitado. Cinco fechados no código, um revertido por
exceder o que a spec autoriza, e dois que são decisão de spec.

| Achado | Onde se fechou |
|---|---|
| **P1 · Fragmentos liam Edital de outro escopo.** `_edital_do_fragmento` filtrava por `pk` e pronto — sem `ator_da_sessao`, sem `obter_edital`, sem escopo. Quem conhecesse o UUID lia Etapas, fatos declarados e — desde a derivação da identidade do marco — código e denominação dos Perfis. Vale para **todos** os fragmentos do assistente, e não só para os dois desta feature. | `views.py::_edital_do_fragmento`, a mesma autorização da tela; `tests/interface/test_compor.py::test_fragmento_de_edital_de_outro_escopo_responde_404` (varre cinco fragmentos), `::test_fragmento_sem_identidade_nao_le_edital_nenhum`, `::test_o_fragmento_sem_o_parametro_continua_desenhando_listas_vazias` |
| **P1 · Método comum retificado não era conferido.** `_coerencia_do_metodo_de_sorteio` olhava só os marcos. Uma Retificação que removesse `/drawMethod/substitutionRule` da raiz publicava — e devolvia à mesa, no dia da indisponibilidade, a escolha da ocorrência de todos os marcos que referenciam o comum, por um ato só. | `validation.py::_coerencia_do_metodo_de_sorteio`, agora reusando `validate_common_draw_method`; `forma::test_o_metodo_comum_pela_metade_impede_a_publicacao`, `::test_o_metodo_comum_inteiro_publica` |
| **P1 · `orderProduction` retificável admitia contradição.** Trocar só a forma da ordem por Retificação deixava o `drawMethod` do marco onde estava: norma publicada dizendo, no mesmo objeto, que a ordem nasce da pontuação e que o sorteio tem fonte e regra de substituição. A projeção de `edital_snapshot` não alcança a Retificação. | `validation.py::_coerencia_da_forma_da_ordem` — recusa que nomeia a saída, que é alterar os dois no mesmo ato; `forma::test_pontuacao_com_metodo_declarado_impede_a_publicacao`, `::test_o_marco_do_acervo_com_metodo_e_sem_forma_declarada_continua_publicando` |
| **P2 · A recusa apagava o método comum digitado.** A validação acontece antes da gravação, e a reexibição lia o Edital do banco: quem esquecia um dos nove campos recebia os outros oito em branco. | `views.py`, o contexto lê `request.POST` quando há recusa; `metodo::test_a_recusa_do_metodo_comum_nao_apaga_o_que_foi_digitado` |
| **P2 · A tela mandava criar Etapa para um sorteio que pode não ter nenhuma.** O aviso do passo dizia "declare ao menos uma antes de compor" e o cartão repetia "volte ao passo Etapas de Avaliação" — contra a FR-432, e contra a ajuda do método no mesmo cartão. | `compor_classificacao.html` e `_marco.html`, as duas frases distinguindo as formas; `escolha::test_a_tela_nao_manda_criar_etapa_para_o_marco_que_sorteia`, `::test_o_aviso_da_etapa_ausente_reconhece_o_marco_de_sorteio` |
| **P2 · `test_round_trip_do_rascunho.py` perdeu oito regressões.** O arquivo **já existia** desde a `014`, e foi sobrescrito em vez de estendido. Sumiram as proteções de período de inscrições, estado do Cronograma, conteúdo normativo do Perfil, janela recursal, regra de corte, quadro de vagas e preservação de marcos ao regravar Perfis. | Arquivo restaurado de `HEAD`; os três casos da `030` foram **acrescentados** ao fim, com constantes próprias. São 11, e não 3 |
| **Contrato · `{}` contra `null`.** `contracts/conteudo-normativo.md` grafava `{ }` para "referencia o comum"; o código publica `null`. | O **artefato** foi corrigido: a versão 10 já fixou `null` para método não declarado, e `{}` seria uma segunda grafia da mesma ausência — o modo de falha que `publicacoes/domain/elevacao` recusa por escrito |

### Os dois gates da segunda revisão

| Gate | Onde se fechou |
|---|---|
| **G1 · Marco novo publicava sem declarar a forma.** `data-model.md` e o contrato do payload exigem a declaração em marco novo; o serializer aceitava a ausência, o `draft` gravava `""` e o snapshot publicava sem a chave. Regra normativa dependendo do `required` da tela contraria o princípio IV. | `validation.py::_forma_da_ordem_declarada`, impeditivo **só** em `ATO_DE_PUBLICACAO` — o rascunho continua podendo estar pela metade, e a Retificação do acervo continua aceitando a ausência. Vinte e quatro construtores de marco nas fixtures passaram a declarar a forma. `forma::test_publicar_marco_sem_declarar_a_forma_e_recusado` prende as duas metades |
| **G2 · FR-416 era incondicional.** A implementação já tratava o acervo — a frase muda quando a combinação declarada não devolve a nota da Etapa —, e a spec não previa a exceção. | `spec.md`: a FR-416 passou a separar o marco novo (o sistema deriva a combinação que torna a frase verdadeira) do marco do acervo (o sistema preserva o declarado e declara o que ele aplica), e ganhou o cenário de aceitação **2-bis**. `escolha::test_o_marco_do_acervo_nao_tem_a_combinacao_transformada` |

**O que a segunda revisão mudou na leitura de SC-142.** Os três testes que provavam "o acervo
publica o conteúdo de sempre" montavam o acervo **publicando** um rascunho sem a chave — caminho
que G1 tornou ilegal, e com razão. O acervo, de verdade, é uma linha com `""`: é o que a migration
deixou, e é assim que eles passaram a montá-lo.

### Um achado que reverti, e por quê

**A primeira tentativa recusava na gravação do rascunho**, e derrubou 759 testes: tornava ilegal
todo payload que o repositório já produz, e com ele todo cliente de API existente. Reverti e
registrei o achado.

A revisão seguinte apontou o lugar certo — a **publicação**, e não a gravação —, e é onde ele está
fechado agora (G1, acima). O rascunho continua podendo estar pela metade, como `cutRule`,
`drawMethod` e `appealWindow` já podem; o que não pode estar pela metade é o Edital publicado.
O custo foi declarar a forma em vinte e quatro construtores de marco das fixtures, e ele é honesto:
uma fixture que publica marco está autorando conteúdo normativo, e conteúdo normativo declara.

## Duas interpretações que não são requisito, e a decisão é do usuário

A **FR-424** manda definir o termo no primeiro uso de *cada tela*; a **FR-428** proíbe ajuda visível
dentro dos cartões de composição. `_marco.html` usa **recorte** e **faixa**; `_perfil.html` usa
**recorte**. A implementação leu o cartão como fragmento, e não como tela: os termos dele se definem
no `como-preencher` da etapa que o contém — `compor_classificacao.html` e `compor_perfis.html`.

É interpretação, e não requisito. Se ela não for a pretendida, a saída é emendar a FR-424 para dizer
"de cada etapa do assistente" em vez de "de cada tela". Nenhum teste pegaria a diferença: checklist,
analyze e citações ficam verdes com as duas leituras.

**A segunda é a FR-416 sobre o acervo.** Ela manda declarar, em texto visível, que com uma Etapa a
pontuação combinada é a dela. Isso é verdade para o marco novo — a derivação usa média ponderada,
que devolve a nota qualquer que seja o peso — e **não** é verdade para um marco antigo que declarou
soma ponderada sobre uma Etapa de peso diferente de 1: ali a pontuação publicada é `nota × peso`.

A implementação não mente: `marcos.pontuacao_combinada_e_a_da_etapa` decide qual das duas frases a
tela escreve, e a segunda diz "este marco combina como o Edital já declarou". Mas a FR-416, como
está escrita, não prevê a exceção — ela diz "o sistema DEVE declarar que a pontuação combinada é a
daquela Etapa", sem ressalva. Emendá-la para nomear o caso, ou decidir transformar o marco antigo,
é decisão de spec.
