# Rastreabilidade — 037, os quatro becos que o sistema já conhece

**Quando**: 19/09/2026. **Base da implementação**: `23bf70e`. **Integrada e medida contra**: a `main`
`0c96283`, que traz a `036`.

O "antes" está em [antes-dos-quatro-becos.md](antes-dos-quatro-becos.md); o desfecho do percurso que
decidiu metade da `US2`, em [achado-do-ach-02.md](achado-do-ach-02.md).

---

## O que o percurso da `T011` decidiu

**Saída (a): há o que fechar.** O Gestor da reauditoria segue o caminho até os Perfis, chega à
etapa, e encontra *"Somente leitura. Você não tem a permissão `edital:elaborar`"*. Uma permissão o
impede, e a `T015` foi executada — a condução do `ACH-02` existe.

**E a medição corrigiu a auditoria nas duas metades.** *"O que falta"* já era dito **e já levava à
etapa**, e *"falta papel"* já era indicado — o que não era dito, e é só isso, é **a quem pedir**.
Duas observações que o percurso produziu e que ficaram **registradas como achado, não como escopo**:
a faixa de somente leitura mostra o codename `edital:elaborar` em vez da permissão em português, e a
tela do Edital exibe a pendência sem caminho nenhum.

**E uma terceira, que só um percurso acharia**: dita por item, a condução saía **três vezes
seguidas** na Revisão. Passou a ser dita **uma vez** para a lista, e há caso prendendo isso
(`test_a_conducao_e_dita_uma_vez_para_a_lista_inteira`). Nenhum teste teria reclamado disso: cada
uma das três estava correta.

---

## Uma linha por requisito

### O caminho até o corte (`US1`)

| Requisito | Onde | Prendido por |
|---|---|---|
| `FR-538` o destino do corte não pende mais da regra | `interface/views.py::_destinos_do_marco` | `test_destinos_do_edital.py::test_o_marco_sem_regra_de_corte_passa_a_oferecer_o_destino` e `…_com_regra_de_corte_continua_oferecendo_o_destino` |
| `FR-539` a tela não é reescrita | nada mudou em `classificacao/application/corte.py` | `test_corte.py::test_o_marco_sem_regra_mostra_a_recusa_e_nao_pagina_inexistente` — **asserção literal** da frase do domínio |
| `FR-539a` o caminho depende de qual recusa é | `interface/views.py::_caminho_da_recusa_do_corte` + `corte.html` | `test_corte.py::test_o_marco_sem_regra_recebe_o_caminho_da_regra_e_nao_o_da_classificacao` **e** `…_com_regra_e_sem_ordem_continua_indo_para_a_classificacao` — a contraprova da `T010` |
| `FR-539b` o alcance é o de **retificar** | `_caminho_da_recusa_do_corte` → `acoes.pode_retificar` | `test_corte.py::test_quem_nao_alcanca_a_retificacao_recebe_a_frase_e_nao_o_caminho` |
| `FR-540` o destino continua pendendo da **classificação** | `_destinos_do_marco`, dentro de `if pode_classificar` | `test_destinos_do_edital.py::test_quem_nao_alcanca_a_classificacao_nao_recebe_o_destino_do_corte` |

### Os dois bloqueios que calavam (`US2`)

| Requisito | Onde | Prendido por |
|---|---|---|
| `FR-541` o aviso nomeia a ação e a permissão | `detalhe.html` + `views.py::CONDUCAO_DA_RETIFICACAO` | `test_conducao_dos_bloqueios.py::test_o_aviso_nomeia_a_acao_e_a_permissao_para_quem_nao_pode_retificar` |
| `FR-541a` derivada **uma vez** | `interface/acoes.py::pode_retificar`, consultada por `_navegacao`, pelo aviso e pela tela do corte | os casos de `FR-541b` e `FR-539b` — divergir quebra os dois |
| `FR-541b` o aviso cala quando a ação está oferecida | `views.py::detalhe` (`conducao_do_imutavel`) | `test_conducao_dos_bloqueios.py::test_quem_pode_retificar_recebe_o_caminho_e_o_aviso_cala` |
| `FR-541c` condução é prosa, não ação desabilitada | `detalhe.html` — a lista não mudou | `test_conducao_dos_bloqueios.py::test_retificar_nao_virou_botao_desabilitado_com_motivo` |
| `FR-542` a pendência diz a quem pedir | `views.py::_pendencias` (`ator`) + `_pendencias.html` | `test_conducao_dos_bloqueios.py::test_quem_nao_pode_compor_le_a_quem_pedir` e `…_alcanca_tambem_a_etapa_em_que_a_pendencia_mora` |
| `FR-544` **só há a quem pedir onde alguém pode compor** | `views.py::falta_permissao_para_compor` — e **não** a negação de `pode_compor` | `test_conducao_dos_bloqueios.py::test_edital_publicado_nao_manda_pedir_a_ninguem`, `…_nem_a_quem_nao_tem_a_permissao` e `test_em_elaboracao_a_conducao_depende_so_da_permissao` |
| `FR-542a` a condução nasce **na tela**, não na mensagem normativa | `_pendencias`/`_pendencias.html`; `editais/domain/validation.py` **intocado** | `test_conducao_dos_bloqueios.py::test_quem_pode_compor_nao_recebe_a_frase_de_pedir` |
| `FR-542b` percorrer antes de prometer | [achado-do-ach-02.md](achado-do-ach-02.md) | o próprio documento — é o `SC-195` |
| `FR-543` produzida pelo mecanismo único | `seguranca/application/authorization.py` | `test_gramatica_das_portas.py::test_as_conducoes_produzidas_seguem_a_formulacao_canonica` |
| `FR-543a` a forma **cheia** | `authorization.py::_peca_a` (`que=`) | `test_frase_da_recusa.py::test_a_recusa_aceita_a_oracao_do_ato` e a asserção de `" que "` no guardião |
| `FR-543b` nomeia a permissão, nunca uma pessoa | as duas frases saem de `Base.a_quem` | `test_gramatica_das_portas.py::test_nenhuma_conducao_produzida_nomeia_pessoa` e `test_conducao_dos_bloqueios.py::test_nenhuma_conducao_nomeia_pessoa` |
| `FR-543c` o mecanismo **ampliado** | `authorization.py::frase_da_recusa(…, que=)` | `test_frase_da_recusa.py` (10 casos) |
| `FR-543d` duas situações de fala, um só *a quem pedir* | `authorization.py::frase_do_aviso` + `_peca_a` compartilhado | `test_frase_da_recusa.py::test_o_aviso_nunca_abre_com_esta_operacao` e `…as_duas_formas_nomeiam_o_destinatario_do_mesmo_jeito` |
| `FR-544` quem pode recebe o caminho | já era entregue por `acoes.do_edital`; o que entrou foi o silêncio | `test_conducao_dos_bloqueios.py::test_quem_pode_retificar_recebe_o_caminho_e_o_aviso_cala` |

### A régua do vencido (`US3`)

| Requisito | Onde | Prendido por |
|---|---|---|
| `FR-545` havendo término, vence quem terminou | `editais/domain/calendario.py::vencido` | `test_calendario.py::test_evento_em_curso_nao_vence`; `test_cronograma_vencido.py::test_periodo_em_curso_nao_adverte_e_continua_sem_impedir`; `test_selo_do_cronograma.py::test_periodo_em_curso_conclui_a_etapa` |
| `FR-546` não havendo, vence quem começou | o `if termino is not None` | `test_calendario.py::test_termino_ausente_nao_vence_por_si` (já existia) e `test_selo_do_cronograma.py::test_evento_pontual_no_passado_continua_mantendo_a_etapa_pendente` |
| `FR-546a` o instante muda **no mesmo ato** | `calendario.py::instante_vencido` deriva de `vencido` | `test_calendario.py::test_evento_em_curso_nao_nomeia_instante_nenhum` |
| `FR-547` a régua continua **única** | um módulo, dois consumidores — nenhum ganhou cópia | conferido no diff: `interface/views.py:828` e `editais/domain/validation.py:2004` continuam importando `vencido` |
| `FR-548` advertência, e nunca recusa | `validation.py::_eventos_vencidos` intocado | `test_cronograma_vencido.py::test_periodo_encerrado_impede_a_publicacao` e `…_os_achados_que_ja_existiam_sobre_o_periodo_nao_mudam` (existentes, **não alterados**) |
| `FR-549` a frase nomeia o término quando os dois passaram | `instante_vencido` mantém a precedência | `test_calendario.py::test_com_os_dois_vencidos_a_mensagem_nomeia_o_termino` e `test_cronograma_vencido.py::test_um_achado_por_evento_e_nao_um_por_instante` (existentes) |
| `FR-549a` concordância de **desfecho** | `portal/leitura.py` **intocado** | `test_cronograma_publico.py::test_o_periodo_em_curso_e_acontecendo_agora_dos_dois_lados` |

### O rótulo do peso (`US4`)

| Requisito | Onde | Prendido por |
|---|---|---|
| `FR-550` o rótulo declara a condição | `_etapa.html` | `test_peso_no_momento_de_enumerar.py::test_o_rotulo_do_peso_declara_a_condicao` e `test_medida_dos_campos.py::test_o_campo_que_admite_vazio_se_diz_opcional` |
| `FR-551` o cartão nomeia as Etapas sem peso | `views.py::_etapas_e_fatos_do_edital` (`tem_peso`), filtro `enumeradas_sem_peso`, `_marco.html` | `test_peso_no_momento_de_enumerar.py`, 6 casos |
| `FR-551a` nenhum controle novo | um campo na lista, e um `<span>` no cartão | contagem do `_marco.html` **antes e depois**: 27 `input`, 15 `select`, 0 `textarea`, 2 `button` |
| `FR-552` o peso continua da Etapa | nenhuma migration | `manage.py makemigrations --check` → *No changes detected* |

### O que esta feature não faz

| Requisito | Como se confere |
|---|---|
| `FR-553` nenhuma decisão de autorização, nenhum aceite ou recusa de ato | o diff não toca `require_permission`, `require_authorization_base` nem `raise DomainError` algum; as duas únicas leituras de permissão que apareceram — `pode_retificar` e `pode_compor` — são **a mesma expressão que já existia**, movida para função nomeada. `test_frase_da_recusa.py::test_a_recusa_de_uma_base_continua_palavra_por_palavra` prende que as recusas de hoje não mudaram uma vírgula |
| `FR-554` nenhuma ajuda instrucional nova nos cartões | **lida junto com a `FR-554a`**, como o portão manda. O que entrou no cartão do marco é aviso derivado do estado: existe só enquanto há Etapa enumerada sem peso, e some quando o peso é declarado — `test_declarar_o_peso_some_com_a_cobranca` é a prova disso, e é o que distingue as duas espécies. Microcópia que ensina continua em `_como_preencher_o_marco.html`, intocado |
| `FR-554a` a distinção, escrita | o comentário do `_marco.html` a registra, e o caso acima a verifica |
| `FR-555` nada reescrito, nada apagado | nenhuma migration, nenhum `delete`, nenhum comando novo; o conteúdo publicado dos dois Editais do percurso continua legível |

### O identificador que foi reservado e não foi gasto

| Requisito | Como se confere |
|---|---|
| `UX-062` | **Reservado e não usado.** A faixa da spec abre em `FR-538`, `SC-188` e `UX-062`, e a numeração de experiência foi reservada por disciplina — esta feature **não escreveu requisito `UX-` algum**. Os quatro becos mudam onde a informação é avaliada e quando ela é dita; nenhum deles cria promessa de experiência que já não estivesse escrita como `FR-`. O número segue livre para a feature seguinte, e esta linha existe para que a matriz não o perca de vista |

---

## Uma linha por critério de sucesso

| Critério | Como foi aferido |
|---|---|
| `SC-188` | **Percorrido pela interface**, sem shell e sem banco: marco sem regra de corte publicado, destino `corte` oferecido na tela do Edital, e a tela de destino lê *"Este marco não declara regra de corte…"* |
| `SC-189` | **Zero** bloqueios sem ação nomeada no cartão *"O que fazer agora"*: era **um** (o conteúdo imutável), e ele passou a nomear a ação e a permissão — ou a calar, para quem já tem o caminho |
| `SC-190` | A etapa do Cronograma de um Edital com inscrições **em curso** fecha **CONCLUÍDA** — medido na tela. Antes era impossível |
| `SC-191` | **Zero** divergências: o mesmo Evento é *"ACONTECENDO AGORA"* na página pública e não é acusado pela conferência da gestão, na mesma requisição |
| `SC-192` | O cartão do marco nomeia **Entrevista** no instante da seleção, e não nove etapas depois |
| `SC-193` | **Zero** controles acrescentados (contagem acima) e **zero** campos movidos de entidade (sem migration) |
| `SC-194` | **Zero** desfechos de ato e **zero** decisões de autorização alterados (ver `FR-553`) |
| `SC-195` | [achado-do-ach-02.md](achado-do-ach-02.md) — o desfecho está escrito, e é a saída (a) |

---

## Os cinco cenários do quickstart, percorridos

Tudo pela interface, em `http://localhost:8037` (banco `ps_037_percurso`, entrada `becos-037` do
`.claude/launch.json`). Nenhum passo por shell, banco ou relógio.

| Cenário | Passo | Desfecho |
|---|---|---|
| 1 | 1–3 | marco sem regra publicado; destino `corte` **oferecido**; a tela diz a recusa e oferece **Retificar o Edital para declarar a regra de corte** a quem a alcança |
| 1 | 4 | marco **com** regra e sem ordem: recusa diferente, e o caminho **continua** sendo *"Ir para a classificação deste recorte"* — a contraprova |
| 1 | 5 | `ana.gestora` (classifica, não retifica) lê *"A Retificação depende da permissão de retificar. Peça a alguém com a permissão de retificar que a proponha."* |
| 1 | 6 | **percorrido pela metade** — ver abaixo |
| 1 | 7 | `ana.elaboradora` não alcança a classificação: o bloco inteiro não lhe é oferecido |
| 2 | 1 | o percurso que decidiu a `US2` — [achado-do-ach-02.md](achado-do-ach-02.md) |
| 2 | 2 | `diego.publicador` lê a ação e a permissão ao lado de *"Conteúdo imutável"* |
| 2 | 3 | `ana.elaboradora` tem **Retificar** na lista e o aviso **cala** |
| 2 | 4 | **nenhuma ação nova**, e `Retificar` não virou botão desabilitado — quem não pode lê *"Nenhum ato disponível para seus papéis nesta situação."* |
| 3 | 1–3 | período de 18/09 a 30/09: etapa **CONCLUÍDA**, e a conferência não o acusa |
| 3 | 4 | a página pública diz **ACONTECENDO AGORA** sobre o mesmo Evento |
| 3 | 5 | Evento pontual de 10/09 sem término: **continua** vencido, e a frase nomeia o **início** |
| 3 | 6 | Evento de 01/09 a 05/09: vencido, e a frase nomeia o **término** |
| 4 | 1 | o rótulo lê *"Peso (opcional até um marco enumerar esta Etapa)"* |
| 4 | 2 | enumerada a Entrevista, o cartão diz *"Sem peso declarado: Entrevista."* **naquele momento** |
| 4 | 3 | declarado o peso, a cobrança **some** |
| 4 | 4 | Etapa sem peso que nenhum marco enumera: **nada** a acusa |
| 5 | 1–3 | contagem de controles idêntica; peso ainda da Etapa; sem migration; advertência continua advertência |

### O passo que não teve caminho inteiro, e a pergunta que ele deixou

**Cenário 1, passo 6 — o marco que ordena por sorteio.** A metade que dá para percorrer foi
percorrida: um marco `POR_SORTEIO` sem Etapa alguma foi composto pela interface, e o cartão dele diz
*"Regra de corte: este marco não corta"* e **não cobra peso** — que é o caso de borda da `US4`.

A outra metade — **abrir a tela do corte** desse marco e ler a recusa — **é inexequível sem um
sorteio real**: a ordem de um marco por sorteio não se emite pela tela de classificação; ela nasce
de relação publicada, ocorrência observada numa fonte externa e sorteio constituído. Sem ordem
emitida a recusa que a tela dá é *outra* (a da ordem ausente), e forçá-la por banco ou por relógio é
o que o protocolo proíbe. **Registrado, como a `034` fez.** O caso está coberto por
`test_corte.py::test_o_marco_que_ordena_por_sorteio_diz_que_nao_corta`, que monta o certame sorteado
inteiro e abre a tela.

**A pergunta que o caso de borda deixou em aberto — *a prosa serve ao marco por sorteio, ou precisa
de palavra própria?* — tem resposta: serve.** A frase fala do que o **Edital não publicou**
(*"o Edital não publicou quantos progridem"*), e não do que o marco calculou. Um marco por sorteio
sem regra de corte está exatamente nessa situação, e o caminho que ele recebe — a Retificação — é
onde a regra se declararia, sorteando-se ou pontuando-se. Palavra própria para o sorteio afirmaria
que a ausência ali tem causa diferente, e ela não tem.

---

## Uma linha por teste alterado, com o motivo

**`research.md` `R-4` previu quatro. São nove** — e o quinto ao nono não são surpresa de execução:
três estavam medidos no "antes" antes de a implementação começar, um apareceu ao rodar, e o nono é
automático.

| Caso | O que mudou | Por quê |
|---|---|---|
| `test_calendario.py::test_evento_em_curso_vence_pelo_inicio` → `…_nao_vence` | asserção invertida e **renomeado** | `FR-545`: o nome defendia o defeito |
| `test_calendario.py::test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro` → `…_nao_nomeia_instante_nenhum` | passa a afirmar `None`, e **renomeado** | `FR-546a`: sem isto, as duas funções do módulo discordariam |
| `test_cronograma_vencido.py::test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro` → `…_nao_produz_achado_nenhum` | afirma a **ausência** do achado, e **renomeado** | o mesmo, na conferência |
| `test_cronograma_vencido.py::test_periodo_em_curso_adverte_mas_nao_impede` → `…_nao_adverte_e_continua_sem_impedir` | `codigos == []`, e **renomeado** | a docstring já descrevia a intenção certa; a asserção prendia o comportamento errado |
| `test_destinos_do_edital.py::test_a_presidencia_sem_publicar_nao_perde_destino_nenhum` | lista esperada ganhou `corte` | o `certame` monta marco **sem** regra: a `FR-538` o alcança. O que o caso afirma — "nenhum a menos" — não mudou |
| `test_destinos_do_edital.py::test_quem_preside_e_publica_ve_a_uniao_sem_repetir` | idem | idem |
| `test_destinos_do_edital.py::test_a_auditoria_continua_lendo_o_que_lia` | idem | idem |
| `test_selo_do_cronograma.py::test_pendente_nao_impede_avancar_entre_etapas_nem_submeter` | **o arranjo**, não a asserção: ganhou um Evento pontual passado | o caso precisa de selo pendente **e** prazo aberto ao mesmo tempo, e isso deixou de caber num Evento só |
| `test_medida_dos_campos.py::test_o_campo_que_admite_vazio_se_diz_opcional[weight]` | a asserção passou de `"(opcional)"` literal para a **forma** do parêntese | `FR-550` manda escrever a ressalva, e o literal a proibia. **Este foi o que a suíte achou** — o arquivo não estava na lista da `R-4`, e a varredura por arquivo não o alcançaria: ele é parametrizado, e só o `weight` falha |

**E um nono que não é autoria.** `test_sem_dado_pessoal_da_amostra.py` parametriza **um caso por
arquivo varrido**, e os quatro arquivos novos sob `backend/` acrescentam quatro casos sozinhos —
703 antes, 707 depois. É contagem automática, e fica registrada para que a conta feche.

### Os vizinhos permaneceram

| Arquivo | Antes | Depois | Dos quais novos |
|---|---|---|---|
| `test_destinos_do_edital.py` | 10 | 13 | 3 |
| `test_corte.py` | 13 casos (15 execuções) | 18 casos (20 execuções) | 5 |
| `test_selo_do_cronograma.py` | 11 | 13 | 2 |
| `test_calendario.py` | 14 | 14 | 0 (dois renomeados) |
| `test_cronograma_vencido.py` | 29 | 29 | 0 (dois renomeados) |

**Conferido por coleta, e não por contagem de `def`**: os oito arquivos alterados coletavam **149**
execuções e passaram a coletar **163**; os três arquivos novos coletam **27**. Nenhum caso
desapareceu sem substituto nomeado.

---

## A contagem final

São **duas** medições, e as duas importam. A primeira responde *"a feature funciona?"*; só a
segunda responde *"ela pode entrar?"* — e foi a que faltava na primeira leitura deste trabalho.

### Na base isolada `23bf70e`, sem a `036`

| | Antes | Depois |
|---|---|---|
| passando | **7343** | **7388** |
| pulados | **11** | **11** |

**+45 execuções**, e elas fecham: **41** casos escritos por esta feature — 14 acrescentados aos oito
arquivos existentes e 27 nos três novos — mais **4** que `test_sem_dado_pessoal_da_amostra.py`
gerou sozinho, um por arquivo novo.

### Integrada à `main` `0c96283`, **que é o que o PR propõe**

```
$ cd backend && make lint check test-pg
uv run ruff check .          → All checks passed!
uv run ruff format --check . → 1132 files already formatted
uv run python manage.py check → System check identified no issues (0 silenced).
uv run python manage.py makemigrations --check --dry-run → No changes detected
================= 7454 passed, 11 skipped in 712.90s (0:11:52) =================
```

| | `main` sozinha | Integrada |
|---|---|---|
| coletados | **7417** | **7465** |
| passando | — | **7454** |
| pulados | — | **11** |

**+48 sobre a `main`**: os 41 da feature, as **3 regressões** que a revisão motivou, e os 4 do
guardião por arquivo. **Os 11 pulados são os mesmos** nas duas medições e na `main`: esta feature
não acrescentou pulo nenhum, e não destravou nenhum.

**Nenhuma migration**: integrada, o `make preparar` fecha em **`33 de 33`** tabelas append-only — o
mesmo que a `main` sozinha fecha, porque a 33ª é a da `036` —, e o `makemigrations --check` não
detecta mudança.

### Os dois que a suíte achou, e a varredura por arquivo não acharia

Duas correções entraram **depois** do primeiro `make test-pg` completo, e nenhuma delas seria
encontrada relendo os arquivos que esta feature tocou:

1. **`test_medida_dos_campos.py::test_o_campo_que_admite_vazio_se_diz_opcional[weight]`** — prendia
   o literal `(opcional)`, e a ressalva que a `FR-550` manda escrever fecha o parêntese mais
   adiante. O arquivo não está na lista da `R-4`, e o caso é **parametrizado**: só o `weight`
   reprova, e o nome do caso não menciona peso.
2. **`test_citacoes_de_requisito.py::test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature`**
   — cobra linha nesta matriz para **todo** identificador que a spec põe em negrito, e isso alcança
   o `UX-062` do cabeçalho *"Faixa de identificadores"*, que é reserva de numeração e não requisito.
   A correção foi a linha acima; **despromover o negrito da spec** teria sido reescrever artefato de
   outra feature para calar um guardião.

**É a razão de o portão mandar rodar a suíte inteira, e não os arquivos tocados.**

---

## O que a revisão achou depois, e o que foi feito

A primeira leitura externa deste trabalho encontrou quatro coisas. **Três procedem e foram
corrigidas**; uma estava desatualizada. Ficam aqui porque o valor delas é o registro.

### 1. A condução confundia falta de permissão com estado não editável — **corrigido**

`conduzir` saía de `not pode_compor(edital, ator)`, e `pode_compor` reúne **estado e permissão**.
Negado inteiro, o predicado punha no mesmo ramo duas negativas que pedem respostas opostas:

| Por que não pode | Há a quem pedir? | O que a tela fazia |
|---|---|---|
| em elaboração, e falta a permissão | **sim** | certo |
| saiu da elaboração | **não** — ninguém compõe por ali | **mandava pedir assim mesmo** |

Reproduzido: num Edital **publicado** com advertência corrigível, `ana.elaboradora` — que **tem**
`edital:elaborar` — lia *"Peça a alguém com a permissão de elaborar o Edital que a faça."* Duas
falsidades numa frase: nomeia como solução uma permissão que não abre aquele estado, e a oferece a
quem já a detém. É o que a `FR-544` proíbe, e é a razão de a `D-002` dizer que condução depende de
quem lê **e** do que o estado admite.

**O mais caro do achado é que o comentário estava certo.** O docstring de `pode_compor` dizia, com
todas as letras, *"Edital que saiu da elaboração não se compõe por ninguém, e mandar pedir ali seria
prometer um caminho que não existe para pessoa alguma"* — e a linha ao lado fazia exatamente isso.
Prosa correta não prende comportamento.

A pergunta virou função própria, `falta_permissao_para_compor`, com a tabela acima escrita nela. As
**três** regressões novas foram conferidas contra o código antigo: as duas do estado publicado
reprovam sem a correção, e a terceira impede que a correção seja *"cale sempre"*.

### 2. A branch estava oito commits atrás da `main` — **integrado**

A `036` entrou em `0c96283` **durante** esta implementação, e o diff não aplicava limpo. Dois
conflitos, os dois reais:

- **`interface/views.py`** — a `036` moveu `BASE_DE_GESTAO_DA_COMISSAO` e
  `BASE_DA_PRESIDENCIA_DO_PROCESSO` para um módulo compartilhado (o ato de instrução também as
  pergunta) e passou a importar `frase_da_recusa`. Resolvido mantendo a mudança de casa da `036` e
  as constantes da `037`, com as **duas** frases importadas.
- **`.claude/launch.json`** — a `036` ocupou **8037 e 8038**. A entrada `becos-037` passou para
  **8039**, sobre a versão da `main` para que nenhuma entrada se perdesse.

### 3. A evidência era da branch isolada — **remedida**

O `antes` foi medido em `23bf70e` e continua sendo o "antes" correto **daquela base**; o que faltava
era a medição do **conjunto integrado**, e ela está abaixo. A afirmação de que *"a 32ª tabela veio da
`036`, que já está na `main`"* — herdada do portão 2 do `tasks.md` — **era falsa**, e os dois
documentos foram corrigidos: são **32 sem a `036`** e **33 com ela**, medidos nos dois estados.

### 4. "A implementação está sem commit" — **não procedia**

O trabalho estava commitado em `2302d23` e publicado no PR desde antes da revisão; a leitura foi
feita sobre um instantâneo anterior. Fica registrado para que a discrepância não volte como dúvida.

---

## O achado da integração — registrado, e corrigido a pedido

**A `036` criou uma quinta ocorrência renderizada da frase, e escolheu a forma de recusa para uma
tela onde ninguém tentou nada.** `recurso.html` imprimia, num parágrafo informativo — *"Nada foi
instruído neste recurso…"* —, o resultado de `frase_da_recusa(BASES_DA_GESTAO_DA_COMISSAO)`, que
abre com **"Esta operação depende de…"**. É exatamente a situação de fala que a `FR-543d` separa:
não houve operação a recusar.

Foi **registrado primeiro e corrigido depois**, por decisão de quem governa o backlog — a tela é de
outra feature, especificada e mesclada nos termos dela, e a `FR-543d` obriga esta feature a
distinguir as duas formas **no mecanismo**, não a reescrever chamadas alheias por conta própria.

| | A frase |
|---|---|
| antes | *"**Esta operação** depende da permissão de gerir a comissão ou da presidência deste Processo — cada uma basta sozinha. Peça a alguém com a permissão de gerir a comissão ou a quem preside este Processo."* |
| depois | *"**A instrução** depende da permissão de gerir a comissão ou da presidência deste Processo — cada uma basta sozinha. Peça a alguém com a permissão de gerir a comissão ou a quem preside este Processo **que a pratique**."* |

**A troca não cria segunda formulação, e é isso que a torna admissível.** As duas formas
compartilham a construção do *a quem pedir*: o texto depois de "Peça" é **idêntico**, letra por
letra, salvo a oração do ato que a `FR-543a` exige. O que muda é o sujeito da primeira oração — que
é justamente o que a `FR-543d` separou. A `FR-486` continua de pé.

**E ela cabe nas palavras da própria `036`.** A `FR-532` daquela feature pede *"o que falta e a quem
pedir, na formulação que o produto já pratica"* — as **duas** metades. A forma anterior entregava a
segunda e abria nomeando um ato que não houve; a nova entrega as duas.

**Com rede, e no teste que é dono da tela.** `test_proveniencia_do_recurso.py::test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta`
já afirmava as bases; passou a afirmar também a abertura, a oração do ato e a **ausência** de *"Esta
operação"* naquele parágrafo. Conferido contra o código antigo: reprova sem a correção.

### As três que sobravam — corrigidas a pedido, e uma delas não era só a oração

A varredura de todas as ocorrências renderizadas — **sensível a maiúscula e minúscula**, porque a
primeira passagem só olhou `Peça` com maiúscula e escondeu quatro — achou **nove** frases que mandam
pedir. Seis diziam **o que** se pede; três não. As três foram fechadas:

| Onde | Antes | Depois |
|---|---|---|
| `ordenacao.html` · divulgação | *"…peça a alguém com a permissão de publicar resultado."* | *"…**que o divulgue**."* |
| `ordenacao.html` · emissão | prosa à mão que **reproduzia o mecanismo** | produzida por `frase_do_aviso`, com *"**que a emita**"* |
| `recusa.html` | *"peça a quem administra o sistema no Cefor."* | *"peça **acesso** a quem administra…"* |

**A do meio não era falta de oração — era uma segunda formulação.** A tela escrevia à mão
*"Emitir a ordem deste marco depende da permissão de gerir a comissão ou da presidência deste
Processo — cada uma basta sozinha"* e, abaixo, *"Peça a quem tem a permissão, ou a quem preside."*
O primeiro período é, palavra por palavra, o que `frase_do_aviso` produz das mesmas bases; o segundo
é uma redação alheia ao mecanismo, que larga a oração do ato **e** encurta o destinatário. É o que a
`FR-486` existe para não deixar nascer, com o agravante de ser indistinguível da forma canônica até
alguém melhorar uma das duas.

A frase passou a vir da view. **O que continua escrito na tela é o que o mecanismo não sabe**: que a
presidência não é papel, e vem da composição da comissão — explicação sobre a natureza da base, e
não formulação do pedido (`FR-485`).

**A da `recusa.html` não ganhou oração de ato, e a razão é de domínio.** *"Quem administra o sistema
no Cefor"* não é permissão nem papel do modelo: não sai do mecanismo, e inventar-lhe um *"que o
conceda"* criaria uma **terceira** maneira de pedir o que `lista.html` já pede de outra. Ela foi
igualada à irmã — *"peça **acesso** a quem administra o sistema"* —, que é a forma que o guardião da
gramática documenta como cheia: o objeto do pedido entre o verbo e o destinatário.

**Com rede, no teste dono de cada tela.** `test_publicar_resultado.py::test_onde_a_tela_aceita_duas_bases_a_frase_nomeia_as_duas`
já afirmava as duas bases; passou a afirmar a frase do mecanismo, a oração do ato, a **ausência** da
redação à mão, e que a explicação sobre a natureza da base continua na tela.

**O saldo: nove de nove frases renderizadas dizem, agora, a quem pedir e o quê.**
