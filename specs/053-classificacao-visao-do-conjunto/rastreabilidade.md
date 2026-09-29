# Rastreabilidade — 053 · Classificação: a visão do conjunto e um Perfil por vez

**Frase que governa**: *a etapa mostra o conjunto e um Perfil por vez, e envia exatamente o que enviava.*

Cada linha aponta o lugar do código e o que o prende. **TC** = `tests/interface/test_visao_da_classificacao.py`;
**TJC** = `tests/javascript/classificacao.test.js`; **TV** = `tests/interface/test_visao_dos_perfis.py`
(da `052`); **NAV** = verificado no navegador real, no preview, pelo roteiro de
[quickstart.md](quickstart.md), numerado como lá — o que o shim de DOM não reproduz (foco, `hidden`,
`details`, validação nativa, fragmento do endereço), medido em 29/09/2026 a 1280×900 e a 375×812,
com os números na seção 2. **Leitura do diff** é promessa negativa, que se confere lendo a mudança.

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-960** | `compor_classificacao.html`: `<legend>` por `legenda_do_perfil` (o filtro da `052`) | TC `test_o_cartao_do_perfil_se_identifica_e_carrega_o_que_a_linha_le`; NAV 9 (*"Perfil DOC-INFO — Campus Serra"*) |
| **FR-961** | `vista-do-conjunto.js`: `montarTabela` (só com mais de um), `mostrar` (um só sempre à vista); `classificacao.js`: uma linha por `fieldset.perfil` | TJC `o Perfil sem marco tem linha…`, `dois marcos são dois blocos por coluna…`; NAV 1, 9 (7 → 2 → 1) e 10 |
| **FR-962** | `classificacao.js`: `colunas`, `lerMarco`, `resumo`; `vista-do-conjunto.js`: `preencherCelula` (um bloco por marco) | TJC `a linha de um marco diz o que o operador compara…`, `dois marcos são dois blocos…`, `sob sorteio, a forma diz o método`, `os critérios saem pela ordem…`; NAV 1 e 10 |
| **FR-963** | `vista-do-conjunto.js`: `aoDigitar` e o observador → `atualizar`; frases em `data-resumo-*` (`_marco.html`, `_criterio.html`) | TC `test_as_frases_curtas_da_linha_moram_no_template`, `test_o_bloco_do_metodo_do_marco_de_sorteio_diz_as_tres_frases`; NAV 2 (o prazo e a forma da ordem mudam na linha, sem envio); leitura do diff: nenhuma regra calculada |
| **FR-964** | `origens.origem_dos_marcos` (sobre `gesto_do_marco` e `frase_do_gesto`, da Revisão); `data-origem` | TC `test_o_marco_aplicado_diz_de_onde_veio_com_a_frase_da_revisao`, `test_editado_e_gravado_depois_o_marco_deixa_de_ser_do_gesto`; NAV 2 (editado e salvo → *"—"*) e 3 |
| **FR-965** | `views`: `_pendencias_por_perfil` (da `052`) sobre `_pendencias_da_etapa(…, "classificacao")`; `data-pendencias`; `situacao` no comum | TC `test_a_pendencia_do_marco_vai_ao_bloco_da_etapa_e_a_linha_do_perfil`; TJ da `052` `a situação são dois fatos, em texto`; NAV 7 |
| **FR-966** | `compor_classificacao.html`: bloco `_pendencias.html` com `pendencias_aqui` | TC `test_a_pendencia_do_marco_vai_ao_bloco…`, `test_a_etapa_vem_na_ordem_pendencias_tabela_metodo_cartoes`; NAV 7 |
| **FR-967** | `views._marcos_alterados`, `_impressao_dos_marcos`; `data-nao-salvo`; na tela, `alterado` e `trazCampoDoFormulario` do comum | TC `test_a_devolucao_sem_mudanca_nao_acusa_perfil_nenhum` (o guardião), `test_a_devolucao_acusa_so_o_perfil_mudado`, `test_criterio_mudado_e_marco_novo_acusam_o_perfil_deles`, `test_marco_removido_na_tela_acusa_o_perfil`; NAV 3 e 6 (prévia e cancelamento: só a origem acusa), 8 |
| **FR-968** | `vista-do-conjunto.js` só alterna `hidden` (R-001 da `052`) | TV `test_o_script_nao_cria_remove_nem_renomeia_campo`, agora parametrizado nos três scripts; NAV 2 (os sete gravados pelo mesmo envio) |
| **FR-969** | `vista-do-conjunto.js`: `abrir`, título *"Editando …"*, `aria-current` | NAV 2 (*"Editando DOC-INFO-02 — Campus Aracruz"*) |
| **FR-970** | `vista-do-conjunto.js`: `vizinho`, `voltarALista` (botões `type=button`) | TV `test_o_script_nao_cria…` (nenhum envia); NAV 2 |
| **FR-971** | `vista-do-conjunto.js`: `cartaoAAbrir`, `recusadoAoCarregar` (o resumo da recusa primeiro), `lembrar`; `salvo`/`aplicado` descartam o fragmento | TJ da `052` (precedência); NAV 2 (depois de salvar, nenhum), 5 (a recusa venceu o fragmento), 6 (o cancelamento reabriu o 4º) |
| **FR-972** | `vista-do-conjunto.js`: `invalid` em captura, abrindo o cartão e o `details` fechado | NAV 4 — no Chrome: código do marco, alvo do critério e prazo negativo dentro do bloco fechado; abriu, focou, não enviou |
| **FR-973** | `perfis.validate_classification_milestones` com `campo` e `identidade`; `views._recusa` → `_ancora_na_classificacao` | TC `test_a_recusa_do_marco_aponta_um_elemento_da_tela_devolvida` (3 casos), `test_a_ordem_repetida_aponta_o_segundo_criterio`; NAV 5 (o link levou ao campo) |
| **FR-974** | `#visao-da-classificacao` vazio e oculto; nenhum `hidden` no servidor | TC `test_sem_script_a_etapa_e_a_de_sempre` |
| **FR-975** | o observador do comum, sobre a lista inteira (`subtree`) | NAV 2 (a reconstrução pela forma da ordem), 10 (*Acrescentar marco*) |
| **FR-976** | leitura do diff: o gesto da `051` não foi tocado; a linha lê o resultado | TC `test_o_marco_aplicado_diz_de_onde_veio…`; NAV 3 (prévia no alto, origem reaberta abaixo; confirmada → tabela, nenhum aberto, origem nas 5 alcançadas) |
| **FR-977** | `compor_classificacao.html`: o `details` do método entre a tabela e os cartões | TC `test_a_etapa_vem_na_ordem_pendencias_tabela_metodo_cartoes`; leitura do diff: o bloco é o mesmo |
| **FR-978** | leitura do diff: nenhuma rota, gravação ou gesto tocado; a validação do marco só ganhou metadado | `test_aplicar_a_todos.py` e `test_padroes_da_composicao.py` sem mudança (seção 4) |
| **FR-979** | `compor_classificacao.html`: `data-rascunho`, `data-lista`, `rascunho.js`; `rascunho.js`: lista múltipla por opção | `test_rascunho_local.py` (a Classificação na lista das etapas; `test_a_lista_de_escolha_multipla_e_guardada_opcao_por_opcao`); TC `test_a_restauracao_devolve_os_marcos_e_diz_que_nao_foram_salvos`; NAV 8 |
| **UX-123** | `vista-do-conjunto.js`: `caption` com o número, `th[scope=col]`, `th[scope=row]` | NAV 11 (10 de coluna, 7 de linha, *"Classificação dos Perfis deste Edital (7)"*) |
| **UX-124** | `vista-do-conjunto.js`: *Editar* + código em `span.oculto` | NAV 11 (*"Editar DOC-INFO-03"*) |
| **UX-125** | *"Em edição"* visível e `aria-current`; situação e origem em texto | TJC `a origem é a frase que o servidor mandou`; NAV 2 e 11 |
| **UX-126** | `vista-do-conjunto.js`: foco no título ao abrir, no *Editar* ao voltar | NAV 2 |
| **UX-127** | ordem de `compor_classificacao.html` | TC `test_a_etapa_vem_na_ordem_pendencias_tabela_metodo_cartoes` |
| **UX-128** | `_estilo_da_vista.html`: `.tabela-rolavel` com `position:relative` | TC `test_sem_script_a_etapa_e_a_de_sempre` (a regra na página); NAV 12 |
| **UX-129** | leitura do diff: dentro do cartão, só atributos `data-` | `test_nenhum_cartao_do_assistente_carrega_ajuda_visivel` (`test_medida_dos_campos.py`) e `test_acessibilidade_da_classificacao.py`, sem mudança |

## 2. Critérios de sucesso

| Identificador | Como se mediu | Resultado |
|---|---|---|
| **SC-354** | NAV 1, 7 Perfis de um marco com 2 critérios, a 1280×900 | tabela a 785 px (primeira tela); **3.481 px** com um aberto, contra 12.530 (teto: um terço, 4.177); **1.791 px** com nenhum (teto: duas telas, 1.800) |
| **SC-355** | NAV 3, depois da confirmação | as 7 linhas à vista na tela que volta, com corte e origem: **zero cliques** e a tabela inteira em uma tela, contra abrir e ler sete cartões ao longo de 12 mil px |
| **SC-356** | NAV 4 | 3 de 3 no Chrome: campo obrigatório do marco, do critério, e campo inválido em bloco fechado |
| **SC-357** | TC `test_a_recusa_do_marco_aponta…` (3), `test_a_ordem_repetida…`; NAV 5 | 4 de 4 nos testes; o `id` apontado existe na tela devolvida, e o Perfil voltou aberto |
| **SC-358** | TV `test_o_script_nao_cria…` nos três scripts; TC `test_a_devolucao_sem_mudanca…` | por construção: nenhum campo criado, removido ou renomeado |
| **SC-359** | NAV 11 | cabeçalhos de linha e de coluna; nome com o código; linha em edição com texto visível |
| **SC-360** | seção 4 | nenhum teste da `030`, `043`, `051` ou do rascunho local mudou de resultado |

## 3. Casos-limite

| Caso | O que o prende |
|---|---|
| Perfil sem marco | TJC `o Perfil sem marco tem linha, e diz que não tem`; TC `test_o_cartao_do_perfil…` (a pendência *profile_without_milestone* vai à linha) |
| Perfil com dois marcos | TJC `dois marcos são dois blocos por coluna…`; NAV 10 |
| Marco sem código | TJC `o marco recém-acrescentado, ainda sem código, aparece` |
| Critério sem alvo escolhido | TJC `os critérios saem pela ordem…, e o sem alvo diz só o sentido`; NAV 4 (*"1º maior nota em;"*) |
| Pendência de Perfil alterado | TJ da `052` `a situação são dois fatos`; NAV 8 (*"1 pendência · alterado — não salvo"*) |
| Origem de marco alterado | NAV 2 (origem e *"alterado"* juntos, antes de salvar) |
| Perfil com dois marcos e origem | leitura do código: `gesto_do_marco` exige um marco só, a regra da Revisão |
| Envio que volta sem gravar | NAV 3 e 6 (prévia e cancelamento), 5 (recusa), 8 (restauração) |
| Salvar com um Perfil aberto | NAV 2 — volta com nenhum aberto e o endereço limpo |
| Endereço que aponta o título da etapa | `recusadoAoCarregar` e `alvoDoEndereco` só consideram alvo dentro da lista (leitura do código) |
| Sem script | TC `test_sem_script_a_etapa_e_a_de_sempre` |
| Tela estreita | NAV 12 (375 px: página 375, tabela 1.086 dentro de 327) |
| Edital que não está em elaboração | leitura do diff: a vista não depende de `editavel`; o rascunho local só para quem compõe (`test_tela_somente_leitura_nao_guarda_rascunho`) |
| Mais de mil campos | fora do escopo (`DP-21`); leitura do diff: nenhum campo a mais no envio |

## 4. Verificação

`make lint check`: verde. `make test-pg DB_NAME=ps_053`, em 29/09/2026: **8822 passando, 11 pulados**
(os onze deliberados do `AGENTS.md`), zero falhas, em 866 s. Entre eles, sem mudança, as suítes da `030`
(`test_acessibilidade_da_classificacao.py`, `test_medida_dos_campos.py`), da `043`
(`test_duplicar_perfil.py`), da `051` (`test_aplicar_a_todos.py`, `test_padroes_da_composicao.py`) e
do rascunho local (`rascunho.test.js`) — a `SC-360`. Dois testes anteriores mudaram, e pela razão
escrita neles: `test_compor_classificacao.py` prendia a tag do formulário fechada, e ela ganhou os
atributos do rascunho (`FR-979`); `test_visao_dos_perfis.py` varria só o `perfis.js`, e passou a
varrer os três scripts (R-001).
