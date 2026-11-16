# Rastreabilidade — 177 · A composição das telas da inscrição no portal

**Frase que governa**: *a composição muda a largura, a ordem do começo e o peso das ações; o que as
telas sabem e dizem continua o mesmo.*

Caminhos de código relativos a `backend/processo_seletivo/portal/`. As abreviações:

- **CT** — `tests/portal/test_composicao_das_telas_da_inscricao.py`
- **LC** — `tests/performance/test_lista_com_convocacao.py` (o laço da lista sem consulta)
- **G** — os guardiões de folha, de larguras e de acessibilidade (`tests/interface/test_larguras.py`,
  `test_folha_estatica.py`, `test_acessibilidade_do_portal.py`, `test_politica_de_conteudo.py`)
- **cap** — `specs/177-composicao-das-telas-da-inscricao/capturas/` (antes e depois, com `medidas.json`
  de cada lado: margens, bordas dos blocos, rolagem horizontal e altura das ações, a 320, 375, 768,
  1280, 1440 e 1920 px)
- **humano** — validação com a equipe, pendente

---

## Requisitos funcionais

| Requisito | Onde | Prova |
|---|---|---|
| FR-8100 | `templates/portal/inscricoes.html`, `inscricao_enviada.html`, `acompanhamento.html` (`.jornada .jornada-da-inscricao`) | CT `test_a_lista_fica_na_coluna_da_jornada`, `test_minha_inscricao_comeca…`, `test_acompanhar_comeca…`; cap |
| FR-8101 | `.jornada` (174) | cap: margens iguais a 1280, 1440 e 1920 px |
| FR-8102 | `static/portal/portal.css`, seção da 177 (`max-width:none` nos blocos) | CT `test_os_blocos_vao_a_borda_da_coluna`; cap: bordas iguais |
| FR-8103 | os três templates (um `.principal` por tela ou por cartão) | CT `test_cada_cartao_tem_um_botao_cheio`, `test_minha_inscricao_tem_a_grade…`, `test_ver_o_que_enviei_e_secundario`; cap: altura das ações |
| FR-8104 | `.jornada-da-inscricao p{max-width:var(--leitura)}`; `main>p` mantida | CT `test_a_medida_de_leitura_continua_no_paragrafo_da_coluna`; G `test_o_texto_corrido_do_portal_tem_medida_propria` |
| FR-8105 | `inscricoes.html`; `views._item_da_lista` | CT `test_o_titulo_do_cartao_e_o_processo…`, `test_a_ordem_do_cartao…` |
| FR-8106 | `views._prazo_do_cartao` (o período lido uma vez em `_item_da_lista`), `_passo_pendente_na_lista` (devolve o `Passo`) | CT `test_o_rascunho_aberto_diz_o_prazo_do_envio`, os testes da regra pura, `test_o_cartao_diz_o_mesmo_prazo_que_o_acompanhamento_com_e_sem_providencia`; LC |
| FR-8107 | `inscricoes.html` (`.selo-da-inscricao`) | CT `test_a_situacao_e_selo_com_a_marca_e_a_palavra` |
| FR-8108 | seção da 177, `.minhas-inscricoes a.principal` | CT `test_a_acao_do_cartao_tem_a_largura_do_rotulo_na_tela_larga`; cap |
| FR-8109 | `inscricoes.html` (`.comeco-da-lista`, `.acesso-a-conta`) | CT `test_o_acesso_a_conta_sai_do_subtitulo` |
| FR-8110 | `templates/portal/_comeco_da_inscricao.html`; `views._conferencia` e `acompanhamento` (`selecao` e `perfil_da_inscricao` da vigente) | CT `test_minha_inscricao_comeca_pela_trilha_e_pelo_perfil`, `test_acompanhar_comeca_pela_trilha_e_pelo_perfil`, `test_minha_inscricao_e_acompanhar_dizem_o_mesmo_perfil_depois_da_retificacao` |
| FR-8111 | `acompanhamento.html` (sem prazo no começo; "Sua situação" primeiro) | CT `test_acompanhar_comeca_pela_trilha_e_pelo_perfil` |
| FR-8112 | `inscricoes.html` (`_mensagens` depois do começo) | leitura do template; as outras duas telas não têm mensagem de retorno |
| FR-8113 | `acompanhamento.html` | CT `test_ver_o_que_enviei_e_secundario` |
| FR-8114 | `acompanhamento.html` (ordem intocada) | CT `test_acompanhar_mantem_a_ordem_dos_blocos` |
| FR-8115 | `inscricao_enviada.html` (`dl.campos.campos-em-grade`); seção da 177 | CT `test_minha_inscricao_tem_a_grade_e_um_botao_cheio`; cap a 375 e a 1280 px |
| FR-8116 | `inscricao_enviada.html` (`.acoes-da-tela`) | CT `test_minha_inscricao_tem_a_grade_e_um_botao_cheio` |
| FR-8117 | `inscricao_enviada.html` (`.situacao-e-protocolo`) | CT `test_minha_inscricao_tem_a_grade_e_um_botao_cheio` |
| FR-8118 | nenhuma rota, nenhuma frase de `situacao.py` muda | `tests/portal`, `tests/integration/portal` e `tests/unit/portal` sem mudança |
| FR-8119 | toda regra nova sob `.jornada-da-inscricao`, ou com classe nova | G; `tests/interface` sem mudança |
| FR-8120 | frases novas: D-002 a D-006 | as varreduras de vocabulário do portal sem mudança |
| FR-8121 | sem estilo nem script nos templates; classes novas com regra | G `test_politica_de_conteudo.py`, `test_acessibilidade_do_portal.py` |
| FR-8122 | cap | cap |

## Critérios de sucesso

| Critério | Prova |
|---|---|
| SC-2800 | cap `medidas.json`: coluna com margens iguais (288/288, 368/368, 608/608) |
| SC-2801 | cap `medidas.json`: todo bloco de primeiro nível com as bordas da coluna; só os parágrafos param na medida |
| SC-2802 | cap `medidas.json`: `rolagem_horizontal` falso nas seis larguras |
| SC-2803 | CT; cap |
| SC-2804 | cap `medidas.json`: ações com 50 px ou mais; na tela larga, 176 a 203 px num cartão de 704 |
| SC-2805 | cap: `minha-inscricao-1280.jpg` e `minha-inscricao-375.jpg` |
| SC-2806 | LC (zero consultas no laço) |
| SC-2807 | cap `medidas.json`: parágrafo mais largo de 685 px (68ch) |
| SC-2808 | cap |

## Requisitos de experiência

| Requisito | Prova |
|---|---|
| UX-950 | cap a 320 e a 375 px; seção da 177 (`@media (max-width:39.99rem)`) |
| UX-951 | cap a 1440 e a 1920 px |
| UX-952 | CT `test_a_situacao_e_selo_com_a_marca_e_a_palavra` |
| UX-953 | `_comeco_da_inscricao.html` (`nav aria-label="Onde você está"`) |
