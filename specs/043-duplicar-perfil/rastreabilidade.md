# Rastreabilidade — Duplicar Perfil (043)

Requisito a requisito, e **caso-limite a caso-limite**: a seção *Edge Cases* da spec não tem
identificador, nenhuma ferramenta a cobra, e por isso ela tem tabela própria aqui. O guardião
`tests/test_citacoes_de_requisito.py` cobra cada identificador definido em `spec.md`.

**Caminhos relativos a `backend/`.** `duplicacao.py` é `processo_seletivo/editais/domain/duplicacao.py`;
`views.py` e `forms.py` são de `processo_seletivo/interface/`; os templates ficam em
`processo_seletivo/interface/templates/interface/`. `unit/…` é `tests/unit/editais/test_duplicacao.py`,
`interface/…` é `tests/interface/test_duplicar_perfil.py` e `autorizacao/…` é
`tests/authorization/test_duplicar_perfil.py`.

## Requisitos funcionais

| Requisito | Onde é executado | Onde é provado |
|---|---|---|
| **FR-634** | `_perfil.html` inclui `_duplicar_perfil.html` em todo cartão editável · `views.py::fragmento_perfil` passa `edital`/`editavel` ao cartão acrescentado | `interface/…::test_a_etapa_em_composicao_oferece_duplicar_em_cada_cartao` · `::test_o_cartao_acrescentado_tambem_oferece_duplicar` · `::test_duplicar_uma_copia_nao_gravada_leva_os_marcos_dela_remapeados_de_novo` |
| **FR-635** | `views.py::fragmento_perfil_duplicado` — Código obrigatório e sem colisão com a tela; `duplicacao.py` aplica Código e Localidade | `interface/…::test_codigo_vazio_ou_ja_na_tela_e_recusado_no_dialogo` · `::test_localidade_vazia_nao_e_recusa_e_nao_herda_a_da_origem` · `unit/…::test_codigo_e_localidade_sao_os_informados` · `::test_localidade_vazia_e_vazia_na_copia_e_nunca_a_da_origem` |
| **FR-636** | `views.py::fragmento_perfil_duplicado` lê a origem por `ler_perfis(request.GET)`; marcos do gravado ou do trânsito | `interface/…::test_a_copia_parte_do_digitado_e_os_marcos_do_gravado` · `::test_duplicar_uma_copia_nao_gravada_leva_os_marcos_dela_remapeados_de_novo` |
| **FR-637** | `_duplicar_perfil.html` (`hx-swap="afterend"`, `<details>`, `type="button"`) · `_perfil.html` (`autofocus`, `role="status"`) | `interface/…::test_sucesso_devolve_o_cartao_da_copia_com_indice_novo_foco_e_anuncio` · `::test_o_dialogo_tem_rotulos_botao_que_nao_submete_e_campos_fora_do_formulario` · foco no navegador: demonstração (T046) |
| **FR-638** | o fragmento é `GET` e não escreve | `interface/…::test_duplicar_nao_grava_nada` |
| **FR-639** | `duplicacao.py::duplicar_perfil` · `views.py::_reexibir_perfis` (fatos e reversão, R-012) e `_reexibir_modalidade` (Regra com identidade) | `interface/…::test_todo_campo_do_contrato_do_perfil_tem_categoria` · `::test_cada_categoria_faz_o_que_diz` · `unit/…::test_fora_identidades_codigo_localidade_e_marco_derivado_tudo_e_igual` · `interface/…::test_a_modalidade_sem_regra_da_copia_nasce_com_identidade_de_regra` · `::test_o_cartao_da_tela_e_o_da_recusa_tem_as_mesmas_chaves` |
| **FR-640** | `duplicacao.py` — `mapa_de_identidades`, `_com_identidades`, linha geral por `identidade_da_linha_geral` | `unit/…::test_tudo_o_que_a_copia_possui_tem_identidade_nova_e_distinta` · `::test_a_linha_geral_tem_a_identidade_derivada_do_perfil_novo` · `::test_duas_copias_da_mesma_origem_nao_partilham_identidade` · `::test_regras_sem_identidade_saem_com_identidades_distintas` |
| **FR-641** | `reaproveitamento.remapear`, reusado | `unit/…::test_a_ampla_concorrencia_declarada_aponta_a_modalidade_da_copia` · `::test_cada_linha_reservada_aponta_a_modalidade_da_copia_de_mesmo_codigo` · `::test_o_criterio_que_compara_fato_cita_o_fato_da_copia` · `::test_criterio_que_cita_fato_que_o_perfil_nao_declara_estoura` · `::test_linha_que_aponta_modalidade_de_outro_perfil_estoura` · `::test_nenhuma_identidade_interna_da_origem_sobrevive_em_posicao_alguma` |
| **FR-642** | `duplicacao.py` — o mapa estendido com a identidade das Etapas **do Edital** | `unit/…::test_as_etapas_do_edital_continuam_as_mesmas` · `::test_etapa_que_nao_e_do_edital_estoura_em_vez_de_atravessar` |
| **FR-643** | `duplicacao.py` remove `CAMPOS_SEM_TELA` | `unit/…::test_os_campos_sem_tela_nao_sao_copiados` · `interface/…::test_cada_categoria_faz_o_que_diz` (categoria *ausente*) |
| **FR-644** | `duplicacao.py::_marcos_da_copia` | `unit/…::test_marco_derivado_da_origem_e_derivado_de_novo_da_copia` · `::test_marco_escrito_a_mao_e_copiado_como_esta` · `::test_codigo_derivado_nao_colide_com_o_escrito_a_mao_da_propria_copia` · `::test_codigo_da_origem_mudado_na_tela_nao_torna_o_marco_gravado_escrito_a_mao` · `::test_denominacao_derivada_segue_a_denominacao_da_copia` · `::test_codigo_com_sufixo_que_o_desempate_nao_produz_e_escrito_a_mao` · `interface/…::test_codigo_corrigido_no_cartao_antes_de_gravar_leva_o_marco_derivado_junto` · `::test_codigo_corrigido_numa_copia_nao_gravada_vale_para_a_copia_dela` |
| **FR-645** | `views.py::_documentos_restritos_a` · anúncio em `_perfil.html` | `interface/…::test_os_avisos_dizem_quantos_marcos_e_quantos_documentos_nao_replicados` · `::test_origem_nao_gravada_nao_anuncia_documento_nenhum` · `::test_duplicar_nao_grava_nada` |
| **FR-646** | `duplicacao.py` trabalha sobre cópia profunda; o fragmento não grava | `unit/…::test_a_origem_nao_muda` · `interface/…::test_a_origem_fica_identica_nos_tres_desfechos` |
| **FR-647** | a cópia grava pelo caminho de sempre — `_gravar_etapa` → `replace_draft` | `interface/…::test_duas_copias_forjadas_com_o_mesmo_codigo_sao_recusadas_pela_gravacao` · `::test_origem_com_erro_de_regra_e_copiada_com_o_erro_e_a_gravacao_o_recusa` |
| **FR-648** | `views.py::fragmento_perfil_duplicado` — `edital` obrigatório, índice numérico, `_edital_do_fragmento`, `pode_compor`; `_origem_gravada` dentro do Edital; `_conferir_marcos_em_transito` na gravação | `autorizacao/…` (os sete casos) · `interface/…::test_marco_em_transito_que_cita_o_que_nao_e_do_edital_nem_do_perfil_e_recusado` · `interface/…::test_a_etapa_em_leitura_nao_oferece_duplicar` |
| **FR-649** | `pode_compor` exige Edital em elaboração; a Retificação desenha `_retificacao_perfil.html`, que não inclui o diálogo | `autorizacao/…::test_edital_fora_da_elaboracao_recebe_403_mesmo_de_quem_elabora` |
| **FR-650** | `forms.py::_marcos_do_perfil` · `views.py::_reexibir_perfis` e `_marcos_em_transito` · `_perfil.html` (campo oculto e anúncio) | `interface/…::test_perfil_novo_com_marcos_em_transito_grava_com_eles` · `::test_a_recusa_devolve_a_copia_com_os_mesmos_marcos_em_transito` · `::test_perfil_ja_gravado_que_carregue_o_campo_continua_com_os_marcos_gravados` · `::test_campo_em_transito_malformado_e_recusa_com_mensagem_e_nao_erro` · `::test_os_avisos_dizem_quantos_marcos_e_quantos_documentos_nao_replicados` |

## Critérios de aceite

| Critério | Onde é provado |
|---|---|
| **SC-230** | medição pela interface, [quickstart.md](./quickstart.md) §4 — registrada abaixo |
| **SC-231** | idem |
| **SC-232** | `interface/…::test_tres_copias_gravadas_nao_partilham_identidade_nem_referencia` (conteúdo canônico) · demonstração (publicado) |
| **SC-233** | `interface/…::test_tres_copias_gravadas_nao_partilham_identidade_nem_referencia` · `unit/…::test_fora_identidades_codigo_localidade_e_marco_derivado_tudo_e_igual` |
| **SC-234** | `interface/…::test_a_origem_fica_identica_nos_tres_desfechos` |
| **SC-235** | demonstração pela interface, [quickstart.md](./quickstart.md) §3 — registrada abaixo |
| **SC-236** | `interface/…::test_os_avisos_dizem_quantos_marcos_e_quantos_documentos_nao_replicados` · `::test_duplicar_nao_grava_nada` |

## Casos-limite

| Caso-limite da spec | Onde é provado |
|---|---|
| Marco com identidade derivada da origem | `unit/…::test_marco_derivado_da_origem_e_derivado_de_novo_da_copia` |
| Perfil sem Modalidade, sem marco ou sem fato | `unit/…::test_perfil_sem_modalidade_sem_marco_e_sem_fato_duplica_so_com_a_linha_geral` |
| Perfil sem ampla concorrência declarada | `unit/…::test_perfil_sem_ampla_declarada_continua_sem_declarar` |
| Origem com erro de regra na tela | `interface/…::test_origem_com_erro_de_regra_e_copiada_com_o_erro_e_a_gravacao_o_recusa` |
| Origem com valor ilegível na tela | `interface/…::test_origem_com_valor_ilegivel_e_recusada_no_dialogo` |
| Código que colide com Perfil ainda não gravado | `interface/…::test_codigo_vazio_ou_ja_na_tela_e_recusado_no_dialogo[NOVO-NA-TELA-…]` |
| Documentos de escopo *Todos os Perfis* | `interface/…::test_os_avisos_dizem_quantos_marcos_e_quantos_documentos_nao_replicados` (o terceiro documento não conta) |
| Documentos recortados pela origem | idem · `::test_origem_nao_gravada_nao_anuncia_documento_nenhum` |
| Campos que nenhuma etapa desenha | `unit/…::test_os_campos_sem_tela_nao_sao_copiados` |
| Etapa de Documentos antes de gravar | comportamento anterior, sem código novo: a etapa lê os Perfis gravados. Registrado, não testado aqui |
| Rascunho local (`G-006`) | registrado, **não corrigido** — limitação anterior (`R-008`). A restauração pede o fragmento sem `edital`, e o cartão restaurado nasce sem o diálogo |
| Marcos não aparecem na etapa Perfis | `interface/…::test_os_avisos_dizem_quantos_marcos_e_quantos_documentos_nao_replicados` (anúncio) · `::test_perfil_gravado_nao_emite_o_campo_em_transito` |
| Fato removido da cópia antes de gravar | a gravação recusa pela validação de sempre; coberto por `FR-647` e verificado na demonstração |
| Edital com muitos Perfis | `interface/…::test_o_orcamento_de_consultas_nao_cresce_com_o_numero_de_perfis` (16 Perfis) · posição e foco na demonstração |

## Achados desta implementação

- **R-012** — a reexibição após recusa perdia fatos e reversão, para qualquer Perfil. **Corrigido**,
  porque a cópia passa pelo mesmo caminho: `interface/…::test_a_recusa_devolve_os_fatos_e_a_reversao_digitados`.
- **`cutRule.governedStage` no reuso da `023`** — não remapeado. **Não** corrigido aqui; foi
  corrigido à parte no #169. Depois do merge, a duplicação passa a recusar Etapa governada que não
  seja do Edital, como as demais referências:
  `unit/…::test_etapa_governada_que_nao_e_do_edital_estoura`.

## Medição e demonstração

Feitas em 25/09/2026, pela interface, no servidor de demonstração `duplicar-043` (banco
`ps_043_demo`, porta 8044), com o código desta branch.

### Demonstração de ponta a ponta — `SC-235`

Edital 43/2027, composto do zero pelo navegador: LP01 com Modalidades AC e PCD, ampla declarada,
quadro 4 + 1, fato `EXPERIENCIA`; marco `LP01` derivado, pela pontuação, com critério pelo fato e
prazo recursal de 2 dias; um Documento Exigido restrito ao LP01. Na etapa Perfis:

1. Duplicar com Código `LP01` → recusa **no campo**, foco no Código, nenhum cartão.
2. Duplicar como `LP02` / Serra → cartão logo abaixo, foco no Código dele, anúncio: *"Leva 1 marco
   de classificação… 1 documento exigido restrito a LP01 não foi replicado para este Perfil."*
   Campos do diálogo fora de `form.elements` (conferido no navegador).
3. Duplicar o **LP02 ainda não gravado** como `LP03` / Cariacica → marco `LP03`, critério apontando
   o fato do próprio LP03, e nenhum anúncio de documento (origem não gravada).
4. Gravar uma vez; na Classificação, três marcos `LP01`/`LP02`/`LP03`, cada um citando o próprio
   fato, prazo de 2 dias em todos.
5. Submeter (ana.elaboradora), homologar (hugo.homologador), publicar (paula.publicadora, Diretora do
   Cefor). **Publicado.**

Conferência do conteúdo **publicado** (`VersaoConsolidada`): 3 Perfis, 9 identidades cada, **0**
partilhadas, **0** referências de um Perfil a identidade de outro; LP02 e LP03 iguais ao LP01 fora
identidades, Código, Localidade e código do marco — **`SC-232` e `SC-233` no publicado**.

**Achado da demonstração, corrigido**: depois de uma cópia bem-sucedida, o diálogo da origem ficava
aberto com a recusa anterior e o Código da cópia. A resposta de sucesso passou a trocá-lo, fora de
banda, por um diálogo fechado e vazio —
`interface/…::test_o_sucesso_devolve_o_dialogo_da_origem_fechado_e_vazio_fora_de_banda`.

### Medição contra o baseline — `SC-230`, `SC-231`

Edital 140/2027 (réplica da etapa Perfis do 140/2025): **16 Perfis, 64 Modalidades, 48 Regras**,
conferidos no banco depois da gravação. Unidade do estudo: clique, campo preenchido, escolha.

| Passo | Interações |
|---|---:|
| LP01 inteiro: *Acrescentar Perfil* (1), 4 × *Acrescentar Modalidade* (4), 8 campos do Perfil, Cadastro Reserva (1), 17 campos de Modalidade (AC 2; PPIQ, PcD, PTT 5 cada), forma de convocação (1), gravar (1), ampla concorrência (1) | **34** |
| 15 duplicações × (abrir, Código, Localidade, *Criar a cópia*) | **60** |
| Ajustes onde o Anexo III diverge: LP04 requisitos (1); LP05 denominação e requisitos (2); TADS11 denominação, descrição e requisitos (3) | **6** |
| Gravar a etapa | **1** |
| **Total da etapa Perfis** | **101** |

- **`SC-230`**: **101** interações, contra **~530** no baseline — redução de **81%** (critério: ≤ 150). ✅
- **`SC-231`**: **4,4** interações por Perfil duplicado em média (66 / 15), contra **~33** (critério:
  ≤ 8). ✅ A estimativa da spec era ~6.
- O primeiro Perfil custou **34** — o mesmo que o estudo mediu por Perfil (~33): a feature não
  barateia o primeiro, e não prometia.
- **Não medido aqui**: a economia na etapa Classificação (`R-011`). Esta recomposição não compôs
  marcos; na demonstração acima, os dois marcos copiados chegaram sem nenhuma interação.
