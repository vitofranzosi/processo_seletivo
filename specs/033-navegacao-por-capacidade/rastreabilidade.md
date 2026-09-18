# Rastreabilidade — 033 · Navegação por capacidade

Três tabelas, e a terceira é a que esta feature precisava ter. As duas primeiras são o de sempre —
um requisito por linha, com o teste que o prende. A terceira lista **todo teste alterado**, com o
motivo: é o que separa corrigir a gramática de afrouxar autorização, e sem ela o revisor teria de
inferir a diferença lendo o diff.

Caminhos relativos a `backend/`.

## Requisitos funcionais

| Requisito | Onde vive | Teste que o prende |
|---|---|---|
| **FR-473** · a tela oferece o que **aquele** ator alcança | `interface/views.py::_marcos_publicados`, `_destinos_do_marco` | `tests/interface/test_destinos_do_edital.py::test_quem_preside_e_publica_ve_a_uniao_sem_repetir` |
| **FR-474** · quem publica vê marcos e atos, com o caminho até a divulgação | `_destinos_do_marco`; `classificacao/…/selectors.py::atos_vigentes_por_marco` | `…::test_o_publicador_puro_ve_o_caminho_ate_a_divulgacao` |
| **FR-475** · a presidência não perde destino nenhum | idem | `…::test_a_presidencia_sem_publicar_nao_perde_destino_nenhum` · `…::test_a_auditoria_continua_lendo_o_que_lia` |
| **FR-476** · nenhuma tela oferece o que o ator não alcança | idem | `…::test_o_publicador_puro_nao_ve_o_que_nao_e_dele` · `…::test_quem_julga_recursos_continua_sem_ver_o_bloco` · `…::test_quem_nao_alcanca_nada_nao_ve_o_bloco` · `…::test_marco_sem_ato_emitido_nao_oferece_divulgacao` |
| **FR-477** · texto que instrui vale para quem o lê | `templates/interface/ordenacao.html`; `views.py::ordenacao` (`pode_divulgar`) | `tests/interface/test_publicar_resultado.py::test_a_tela_de_ordenacao_diz_de_quem_e_o_ato_de_divulgar` |
| **FR-478** · recusa por capacidade é explicada | as quatro portas em `interface/views.py` | `tests/authorization/test_gramatica_da_recusa.py::test_quem_nao_satisfaz_base_nenhuma_le_a_recusa_e_nao_o_inexistente` |
| **FR-479** · ponto único, e o conjunto vem de quem chama | `seguranca/application/authorization.py::require_authorization_base` | `…::test_a_recusa_nomeia_as_duas_bases_que_teriam_servido` · `tests/test_gramatica_das_portas.py::test_toda_porta_decide_a_autorizacao_pelo_ponto_unico` |
| **FR-480** · "não encontrado" só para inexistente e outro escopo | as seis portas | `…::test_escopo_alheio_e_inexistente_mesmo_para_quem_tem_a_capacidade` · `…::test_escopo_alheio_e_inexistente_tambem_no_marco_e_na_divulgacao` · `tests/authorization/test_distribuicao.py::test_escopo_institucional_divergente_e_inexistente` |
| **FR-481** · a recusa nomeia o que falta e diz que nada mudou | `frase_da_recusa`; `interface/recusa.html` | `…::test_a_recusa_nomeia_as_duas_bases_que_teriam_servido` |
| **FR-482** · a verificação continua no servidor | — (nada mudou; o requisito é de não-regressão) | `…::test_a_url_montada_a_mao_recebe_a_mesma_recusa_que_a_tela` |
| **FR-483** · nenhuma capacidade nova, nenhuma regra afrouxada | — | a tabela de testes alterados, abaixo · `tests/interface/test_marco_removido.py::test_nenhuma_permissao_se_alargou_para_resolver_navegacao` |
| **FR-484** · a tela sem ação nomeia a capacidade que resolve | `templates/interface/ato_ordenacao.html` | `tests/interface/test_publicar_resultado.py::test_a_tela_do_ato_nomeia_a_capacidade_que_resolve` |
| **FR-485** · quando falta vínculo, nomeia o vínculo — e não um papel | `templates/interface/ordenacao.html`; `views.py` (`BASE_DA_PRESIDENCIA`) | `…::test_onde_a_tela_aceita_duas_bases_a_frase_nomeia_as_duas` |
| **FR-486** · uma formulação só | `frase_da_recusa`; os três templates | `tests/test_gramatica_das_portas.py::test_toda_tela_que_manda_pedir_usa_a_formulacao_canonica` · `…::test_nenhuma_tela_inventa_uma_segunda_redacao` |
| **FR-487** · o filtro por escopo na própria consulta | as seis portas | `…::test_escopo_alheio_e_inexistente_mesmo_para_quem_tem_a_capacidade` · `tests/test_gramatica_das_portas.py::test_toda_porta_filtra_o_escopo_na_propria_consulta` |
| **FR-488** · separar escopo de base antes de mudar a gramática | `views.py::_etapa_para_distribuir` | `…::test_na_distribuicao_o_escopo_alheio_continua_inexistente_e_a_falta_de_vinculo_nao` |
| **FR-489** · a frase diz a verdade **daquela chamada** | `_edital_para_classificar`, `_edital_para_publicar` | `…::test_a_porta_do_marco_diz_coisas_diferentes_nos_seus_dois_modos` · `…::test_a_porta_da_divulgacao_diz_coisas_diferentes_nos_seus_dois_modos` |

## Critérios de sucesso

| Critério | Como se verifica | Resultado |
|---|---|---|
| **SC-164** · zero URLs digitadas | `tests/interface/test_publicar_resultado.py::test_o_caminho_oferecido_ao_publicador_puro_abre_a_divulgacao` — o caminho é **lido da página**, e não montado pelo teste | ✅ |
| **SC-165** · nenhuma porta desta feature responde "não encontrado" a recusa de autorização, **por varredura** | `tests/test_gramatica_das_portas.py::test_nenhuma_porta_responde_inexistente_para_recusa_de_autorizacao` + o detector de novidade | ✅ · recortado às portas desta feature pela decisão da `T004` |
| **SC-166** · 100% das recusas nomeiam o que resolve | mesma varredura, e `test_toda_porta_decide_a_autorizacao_pelo_ponto_unico` | ✅ |
| **SC-167** · nenhum dos seis papéis vê caminho que não abre | percurso pela interface, cenários 1–3 do quickstart | ver *Cenários percorridos* |
| **SC-168** · o conjunto de pares (ator, tela) é idêntico | a tabela de testes alterados, lida caso a caso | ✅ · zero removidos, zero que passaram a esperar sucesso |

## Testes alterados — a tabela que esta feature precisava ter

**A regra foi uma só, e não teve exceção**: trocar o **status esperado**, de `404` para `403`.
A asserção de **quem entra** ficou idêntica em todos os casos, e nenhum deles passou a esperar
sucesso onde esperava recusa. A conferência foi feita **caso a caso** e por comparação mecânica
entre o "antes" registrado em `T002` e o estado depois — não pela contagem, que é o modo de falha
que o cenário 4 do quickstart existe para pegar.

**Zero casos removidos. Zero casos que passaram a esperar sucesso.**

Quatro mudaram de nome, e só porque o nome **afirmava a doutrina antiga**.

| Arquivo · caso | O que mudou | Por quê |
|---|---|---|
| `authorization/test_distribuicao.py::test_quem_apenas_atua_na_etapa_nao_distribui` | 404 → 403 | João é do mesmo escopo e não tem base; a recusa é sobre ele |
| `…::test_quem_nao_tem_vinculo_nenhum_recebe_inexistente` → `…_recebe_a_recusa_explicada` | 404 → 403 · **renomeado** | o nome afirmava o `ACH-35` como doutrina |
| `…::test_a_distribuicao_por_post_tambem_e_recusada` | 404 → 403 | mesma porta, pelo POST; `Atribuicao.objects.count() == 0` intacta |
| `…::test_escopo_institucional_divergente_e_inexistente` | **nada** | é a contenção da mudança acima: prova que escopo e base foram separados (`FR-488`) |
| `authorization/test_classificacao.py::test_auditoria_consulta_e_nao_emite` | 404 → 403 no POST | emitir chama a porta com `somente_gestao`, e ali auditoria não é base |
| `…::test_sem_base_recebe_404_uniforme` → `…::test_sem_base_recebe_a_recusa_explicada` | 404 → 403 (×2) · **renomeado** | o nome trazia o número da doutrina antiga |
| `…::test_fato_usado_no_desempate_so_aparece_para_gestao_e_auditoria` | 404 → 403 | **a asserção que importa não mudou**: o valor de desempate continua não aparecendo |
| `authorization/test_consulta_de_resultado.py::test_quem_nao_tem_nada_recebe_a_resposta_uniforme` → `…_recebe_a_recusa_explicada` | 404 → 403 · **renomeado** | idem |
| `…::test_a_auditoria_le_o_resultado_e_nao_alcanca_a_ocorrencia` | 404 → 403 (×2) | Íris acabou de ler o Resultado: ela **já sabe** que a Etapa existe |
| `…::test_quem_nao_tem_nada_recebe_a_uniforme_na_ocorrencia` → `…_recebe_a_recusa_explicada_na_ocorrencia` | 404 → 403 · **renomeado** | idem |
| `…::test_a_auditoria_nao_ganha_o_botao_de_consolidar` | `in (302, 404)` → **`== 403`** | **corrigido duas vezes.** A primeira escrita alargou para `in (302, 403, 404)`, e alargar um conjunto aceito é enfraquecer a asserção — foi a conferência caso a caso que pegou |
| `authorization/test_mesa_por_post.py` · 4 casos parametrizados | status por caso: 403 no mesmo escopo, **404 de outra unidade** | a lista passou a carregar o esperado por caso, em vez de um número só; as rotas de **avaliar** continuam 404 e ficaram fora |
| `acceptance/test_comissao_e_alocacao.py::test_o_percurso_completo…` | 404 → 403 numa linha | a de `comissao`; as de `minha-etapa` continuam 404, e por razão diferente |
| `interface/test_caminho_ate_a_mesa.py::test_quem_nao_gere_nao_recebe_o_elo` | 404 → 403 | a rota `alocacoes` passa pela porta da gestão |
| `interface/test_oferta_da_comissao.py::test_quem_nao_gere_nao_recebe_a_oferta_no_painel` | 404 → 403 | as duas asserções de que o link **não aparece** ficaram idênticas |
| `interface/test_trilha_da_012.py::test_quem_nao_preside_nem_audita_nao_alcanca_a_trilha` | 404 → 403 | João trabalha na Etapa: ele já sabe que ela existe |
| `interface/test_conclusoes_preservadas.py` · 2 casos | 404 → 403 | a conclusão continua `CONCLUIDA` — a asserção de efeito não mudou |
| `interface/test_marco_removido.py::test_nenhuma_permissao_se_alargou_para_resolver_navegacao` | 404 → 403 (×2) | **é o caso que mais importa**: ele afirma que a `033` não alargou porta nenhuma, e continua afirmando |
| `…::test_o_endereco_que_nao_abre_responde_institucionalmente` | 404 → 403 · e o título | o que ele prende é **de quem é a página** — produto, nunca a de depuração do Django |
| `interface/test_publicacoes_do_marco.py::test_o_caminho_para_o_ato_de_origem_nao_aparece_a_quem_nao_tem` | 404 → 403 | a asserção de que o caminho **não aparece** ficou idêntica |

### Dois arquivos não-teste alterados por causa da `FR-486`

| Arquivo | O que mudou | Quem pegou |
|---|---|---|
| `templates/interface/ato_ordenacao.html` | *"Peça a alguém com **essa** permissão"* → *"…com a permissão de publicar resultado"* | a varredura da `T039`, sobre texto que **eu** tinha acabado de escrever |
| `templates/interface/lista.html` | *"**Solicite** acesso a quem administra"* → *"**Peça** acesso a quem administra"* | a mesma varredura · era segunda gramática **pré-existente**: `recusa.html` já dizia "peça" para o mesmo pedido |

## O que a verificação encontrou, e não estava previsto

Três portões pegaram defeito real, e nenhum deles teria aparecido na revisão de código:

1. **A contraprova do escopo** (`test_a_capacidade_certa_no_escopo_certo_continua_abrindo`) reprovou
   porque a rota do marco recebeu um identificador de Etapa no lugar do marco. Todos os casos de
   escopo estavam verdes — eles recusavam, e recusavam pelo motivo errado.
2. **A conferência caso a caso da `T032`** pegou o `in (302, 403, 404)` descrito acima.
3. **A varredura da `T039`** pegou as duas frases da tabela anterior.

## O detector disparou antes de a feature entrar

Vale registrar porque é a única evidência que existe de que a `SC-165` sobrevive ao dia seguinte.

Ao integrar a `main` — que trazia a `031` —, a `T038` reprovou a suíte: `exportar_matriculas`
respondia "não encontrado" e não estava no inventário. **Ela está certa**: a consulta filtra por
escopo institucional, e a autorização vai por `require_permission`, que responde 403. Foi
classificada e o verde voltou.

O caso é pequeno e é o ponto inteiro. O detector **não julga a gramática** — ele obriga alguém a
olhar. Uma porta escrita com a gramática antiga teria entrado pela mesma via, e a diferença é que
alguém teria de escrever no inventário que ela responde 404 a recusa de autorização. Sem isso, a
`SC-165` valeria para 18/09/2026 e para mais nenhum dia.

## Cenários percorridos

| Cenário | Como foi verificado |
|---|---|
| **1** · o Publicador puro chega à divulgação | automatizado, nos dois sentidos: `test_destinos_do_edital.py` (8 casos, um por papel) e `test_publicar_resultado.py::test_o_caminho_oferecido_ao_publicador_puro_abre_a_divulgacao`, que **lê o caminho da própria página** em vez de montá-lo |
| **2** · a recusa se explica | automatizado: `test_gramatica_da_recusa.py`, 21 casos, com as quatro contraprovas do quickstart — outro escopo, identificador inexistente, URL montada à mão e o 404 uniforme do portal |
| **3** · quem trava sabe a quem pedir | automatizado: os quatro casos de `test_publicar_resultado.py`, com as duas contraprovas de `FR-485` puxando para lados opostos |
| **4** · nada foi afrouxado | **caso a caso**, por comparação mecânica com o "antes" da `T002` — ver a tabela de testes alterados |

**`SC-167` não foi percorrida à mão pela interface, e isso é uma lacuna declarada, não uma
equivalência.** O que a `T035` pede é entrar pelos seis papéis do seletor de identidade e olhar; o
que existe é a mesma matriz verificada por teste, papel a papel, nos dois sentidos — nenhum vê
caminho que não abre, e nenhum deixa de ver um que abria. A diferença entre as duas coisas é real:
o teste lê o `href` do bloco de classificação, e o olho humano lê a tela inteira.
