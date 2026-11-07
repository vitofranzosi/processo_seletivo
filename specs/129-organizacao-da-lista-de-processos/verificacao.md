# Verificação: A organização da lista de Processos Seletivos (129)

Feita em 06/11/2026, na branch `claude/interesting-antonelli-d15d99`, sobre a `main` em `ffde747b`.

## A análise cruzada (spec × plano × tarefas)

`/speckit-analyze` antes de implementar: os 30 requisitos funcionais, os 5 de experiência e 5 dos 6
critérios cobertos por tarefa, por intervalo ou por citação direta. O SC-1315 é validação com pessoas, e
fica pendente (abaixo). Duas lacunas de teste foram corrigidas no `tasks.md` antes de implementar: o
subtítulo pela Unidade (FR-4322) e a ordem de leitura (UX-272) ganharam caso em T007. Nenhum conflito
com a Constituição; nenhuma ambiguidade aberta.

## Suíte

`make lint check test-pg` com `DB_NAME=ps_129`, 4 workers, sem os grupos opcionais `assistente` e
`navegador` (por isso 21 pulados, e não 12: os do vocabulário, a recusa por vendor, o E2E da Caixa, o
tokenizer e os dois arquivos de jornada no navegador, entre outros).

| Rodada | Resultado |
|---|---|
| 1ª, com a implementação e os testes que a tarefa já previa ajustados | **17115 passando, 21 pulados, 5 falhas** (805s) — as cinco liam a coluna ou a tabela que saíram, e estão na tabela abaixo |
| depois da revisão independente | os arquivos da feature e os guardiões, verdes; lint verde |
| 2ª, depois de sincronizar com a `main` (com a `130`, #421) | **17154 passando, 21 pulados, sem falha** (749s); `make lint check` verde; `makemigrations --check`: *No changes detected* |

O merge com a `main` teve dois conflitos de texto, nas linhas da `129` e da `130` do README e nas
entradas `lista-129` e `advertencia-130` do `.claude/launch.json`; ficaram os dois lados.
`tests/performance/test_trabalho_em_escala.py` (a medida da `104`) passou sem mudança (T022).

## Os testes que mudaram (Compatibilidade da spec)

| Teste | O que prendia | O que passou a afirmar |
|---|---|---|
| `test_acoes.py::test_listagem_e_detalhe_nao_divergem` | o conjunto da coluna igual ao do detalhe (FR-023 da `007`) | substituído por `test_a_lista_nao_apresenta_acao_de_edital` (todo papel) e `test_o_ato_de_edital_que_a_faixa_nomeia_o_detalhe_tambem_oferece` (FR-4329) |
| `test_acoes.py::test_cancelar_aparece_na_listagem_para_quem_pode` | "Cancelar" na coluna | substituído pelos mesmos dois: "Cancelar" continua no detalhe, que os casos de `test_acoes.py` sobre o detalhe já prendem |
| `test_polish_da_057.py` (T1: frequentes primeiro, contador esmaecido) | FR-1049 e FR-1050 | `test_a_lista_nao_tem_mais_a_coluna_nem_o_contador_da_linha`: o partial, a regra e `acoes.da_linha` não voltam |
| `test_lista.py::test_a_contagem_diz_o_que_ela_conta` | "Editais no total" | as abas contam Processos e o resumo por Edital saiu (FR-4321) |
| `test_lista.py::test_acoes_seguem_a_permissao_de_quem_olha` | "Retificar" para quem elabora e "Encerrar" para quem gere, na linha | a permissão decide o caminho de quem gere (Comissão); nenhum ato de Edital na linha |
| `test_lista.py::test_estrutura_acessivel_da_lista` | `scope="col"`, `scope="row"` e `<caption>` da tabela | sem tabela; a navegação das abas nomeada e a busca com rótulo |
| `test_acoes_disponiveis.py::test_c_a_devolvida_se_reconhece_e_a_reenviada_tambem` | a marca "Retificação devolvida" sem "aguarda" para quem age | a marca diz "· aguarda" também a quem age (R-9) |
| `test_acoes_disponiveis.py::test_d_a_lista_nao_oferece_submeter_que_a_validacao_pode_recusar` | "Conferir e submeter" na linha | nenhum dos dois na lista; o detalhe desabilita "Submeter" |
| `test_acoes_disponiveis.py::test_d_quem_submeteu_e_homologou_nao_ve_publicar_como_acao` | "Publicar" desabilitado com o motivo na linha (FR-2816) | o mesmo, no detalhe |
| `test_acoes_disponiveis.py::test_a_coluna_tem_o_ato_e_nao_diz_nenhuma_acao` | o ato da Retificação na coluna (FR-2814) | `test_a_linha_tem_a_marca_e_o_ato_fica_na_faixa` |
| `test_acoes_disponiveis.py::test_os_recursos_que_aguardam_decisao_sao_um_item_por_edital` | "Recursos aguardando decisão (1)" na linha | o contador saiu da lista; o item da faixa continua |
| `test_acoes_disponiveis.py::test_cada_item_da_faixa_e_um_link_so_com_o_ato_no_nome` | o recorte da faixa até a nota, que ficava no fim | até o fim da seção, porque a nota subiu (FR-4324) |
| `test_polish_da_058.py::test_a_tabela_mora_na_moldura` | a tabela da lista dentro de `.rolavel-no-estreito` (FR-1071 da `058`) | o caso da lista sai: não há tabela (FR-4320); o da Condução do marco fica |
| `test_hardening_pos_auditoria.py::test_lista_abre_o_edital_pelo_numero_e_pelo_titulo` | dois links para o detalhe (número e título) | o número é o link, e só ele: o título aparece só quando difere, e dois links para o mesmo destino seriam uma parada de teclado a mais |
| `test_hardening_pos_auditoria.py::test_a_acao_de_recursos_conta_so_as_pecas_que_aguardam_decisao` | "Recursos aguardando decisão (N)" na linha e no detalhe | na lista, o número é o da faixa ("Decidir recursos (N)", e sem item quando zero); no detalhe, o mesmo de antes |
| `test_jornada_da_retificacao.py::test_a_criar_retomar_editar_submeter_homologar_e_publicar` | a marca sem "aguarda" para quem age | a marca com "· aguarda quem elabora/homologa/publica" (R-9) |
| `integration/interface/test_inscricoes_recebidas.py::test_a_acao_do_edital_conta_apenas_as_inscricoes_enviadas` | "Inscrições recebidas (1)" na linha da lista | o mesmo, no detalhe do Edital, onde a ação continua |
| `gestao/telas.css` (as regras `.processo table th:nth-child(…)`) | as larguras das colunas da tabela da lista | saíram com a tabela; as regras do cartão do Processo passaram para `telas/lista.css`, a única tela que o desenha |

## No navegador

Banco descartável `ps_129_demo` (`migrate`, `semear_unidades`, `seed_demo`) com mais 198 Processos
montados direto no banco, pelo helper `tests/fixtures/lista_de_processos.py`: **200 Processos** e 209
Editais — 61 em andamento (um deles, antigo e em elaboração, cai na página 3), 120 encerrados e 19
cancelados, um deles com o Edital 90/2026. Runserver da entrada `lista-129` do `.claude/launch.json`.
O "antes" é o da revisão de 06/11: `doc/estudo-pagina-processos-seletivos-2026-11-06/atual-volume/`.

| Conferido | Resultado | Captura |
|---|---|---|
| Gestor, padrão, 1280 × 900 | "Em andamento (61)" marcada com traço; "61 Processos, mostrando 1–20."; **2 853 px, 3,17 telas** (SC-1310: ≤ 3,5) | `capturas/gestor-padrao-1280.jpg` |
| Gestor, padrão, 375 px | **4 454 px, 4,95 telas de 900 px** (SC-1310: ≤ 5); `scrollWidth` = 375, nada rola de lado; o título do Edital some | `capturas/gestor-topo-375.jpg`, `capturas/gestor-lista-375.jpg` |
| Busca "90/2026" a partir de "Em andamento" | o cancelado, com o selo; nenhuma aba marcada; a frase com "1 está encerrado ou cancelado" e "Limpar a busca"; o termo no campo | `capturas/busca-90-2026-1280.jpg` |
| `?situacao=cancelados&pagina=2` | a última página que existe ("19 Processos, mostrando 1–19.") | `capturas/aba-cancelados-1280.jpg` |
| Elaboradora, página 1 | a faixa com 12 itens, entre eles o Edital do Processo que está na página 3; a nota de cobertura antes do primeiro item | `capturas/elaborador-faixa-1280.jpg` |
| Console | nenhuma mensagem, nenhuma violação de CSP | — |

**A primeira medida reprovou o SC-1310**, e o desenho foi corrigido: com o cartão herdado da tabela (1rem
de respiro, título a 1,15rem, 1,25rem entre cartões), cada Processo media 149 px e a página, 4,17 telas
no computador e 6,5 no celular. O cartão ficou compacto em `telas/lista.css`: 104 px por Processo, com
1,2 Edital em média na amostra.

**Consultas da lista no mesmo banco** (`CaptureQueriesContext`, por papel, nas combinações padrão,
página 2, "Encerrados" e busca "90/2026"): **9** para todo papel de `PAPEIS`, **10** para quem julga
recursos (a contagem dos recursos da faixa) e para todos os papéis juntos — iguais nas quatro
combinações. Antes, quem exporta para matrícula pagava duas consultas por Edital publicado (revisão de
06/11, seção 6).

## A revisão independente

Um subagente leu o diff sem o raciocínio da implementação, e rodou os testes da feature e os guardiões
de CSP, estáticos, acessibilidade, larguras, citações e vocabulário (2319 passando, 10 pulados). Três
achados, todos corrigidos:

| Achado | Correção | Teste |
|---|---|---|
| "N/AAAA" somava o texto ao número: "90/2026" trazia o Processo do Edital 190/2026, cujo título cita "190/2026" — e é assim que a elaboração costuma intitular | "N/AAAA" passou a ser só identificador (R-2 revista); "N" sozinho continua número **e** texto, como a FR-4306 manda | `test_recorte_dos_processos.py::test_a_busca_por_numero_e_ano` |
| `?busca=%00` respondia 500: o PostgreSQL recusa o NUL em texto | o NUL sai do termo na leitura do endereço | `test_lista_de_processos.py::test_busca_sem_espacos_nas_pontas_e_cortada`; `test_organizacao_da_lista.py::test_a_busca_vazia_a_partir_de_uma_aba_volta_a_ela_e_o_nul_nao_derruba` |
| os Editais da unidade se filtravam pela cópia do escopo no Edital, e a lista pelo escopo do Processo: um Edital legado com cópia divergente sumiria da linha | o filtro passou a ser `processo__institution_scope`, como a leitura antiga por `processo.editais` | leitura de `editais_da_unidade` |

E uma observação, também tratada: a busca vazia enviada de outra aba caía em "Em andamento", porque o
formulário não levava a aba. Agora leva, num campo oculto, e a busca só com espaços volta à aba aberta
(Edge Cases).

O defeito do NUL existe também na busca da Visão Geral (`visao_geral.py`), que esta feature não toca.

## Pendências para o usuário

- **SC-1315 (validação humana).** Duas pessoas da equipe, de papéis diferentes, acham um Processo
  cancelado só pelo número do Edital, sem ajuda, em menos de 30 segundos; nenhuma conclui pela faixa que
  não há convocação ou resultado pendente quando há.
- **A busca não ignora acentos** (Assumptions): "matematica" não acha "Matemática".
