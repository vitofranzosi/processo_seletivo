# Verificação: Gestão de acessos pela interface

Registro do que foi executado, onde, e do que falta. Separado em três: o que esta sessão rodou, o
que o CI rodou, e o que está pendente.

## A dependência, conferida antes de especificar (30/10/2026)

| Item | Achado |
|---|---|
| PR #345 (`106`) | aberto, sem revisão; CI verde (`test` e `compose`) em `8af15129` |
| Achado 1 — o retorno exigia `estado`, e o OIDC devolve `state` | **corrigido** em `8af15129`; regressão em `test_entrada_institucional.py::test_o_retorno_le_o_state_do_protocolo_e_nao_o_nome_interno` e `::test_o_adaptador_pode_dizer_onde_o_estado_volta` |
| Achado 2 — dois primeiros administradores institucionais simultâneos | **corrigido** em `8af15129`; regressão em `test_concorrencia.py::test_duas_primeiras_administracoes_simultaneas_gravam_uma_so` |

Os dois testes de regressão passam nesta branch (`SC-1015`). Nenhum requisito da `106` foi reaberto.

## O que esta feature muda na `106`, e por quê

| Mudança | Motivo |
|---|---|
| `conceder` recusa pessoa inativa (`pessoa_indisponivel`, 409) | `D-011`; única mudança de regra (`FR-3134`) |
| `tests/fixtures/provedor_simulado.py`: endereço de autorização variável e `redirect_uri` na ida | `D-013`; código de teste. Nenhum teste dependia do endereço |
| `test_entrada_institucional.py::test_a_revogacao_vale_na_requisicao_seguinte`: o destino passa de `identificar` a `sem-acesso` | **mudança deliberada**, e não regressão: é a lacuna que a `106` listou (FR-3101 desta). O que o caso prova — recusa, nada gravado, sem ator — continua igual, e o comentário no teste o diz |
| `test_configuracao_producao.py::test_seletor_ao_lado_do_provedor_continua_recusado`: a carga com provedor declara os prazos | **mudança deliberada**: produção com provedor passa a exigir os prazos (FR-3124). Sem eles, a recusa viria pelo prazo, e o caso deixaria de provar que é o seletor que recusa |
| Listas literais que crescem com a feature: `MODULOS_DE_VIEW` (`test_gramatica_das_portas.py`) e o inventário de negativas da `033`; `QUEM_CARREGA` (`test_folha_estatica.py`) | os guardiões existem para crescer junto, e nenhum resultado esperado mudou |

A sessão institucional ganhou uma chave própria para o prazo (`interface_prazo_institucional`), e
não campos na identidade: o teste da `106` que fixa a forma da identidade na sessão continua
intocado.

## O que esta sessão executou

Ambiente: macOS, PostgreSQL local, `DB_NAME=ps107` exclusivo, grupos `dev`, `assistente` e
`navegador` instalados, Chromium 1248 do Playwright 1.64.1.

| Execução | Resultado |
|---|---|
| `make lint check test-pg`, 4 workers, sobre a árvore antes do README da `107` | `ruff check` e `ruff format --check` verdes; `check` e `makemigrations --check` sem mudança; **13758 passando, 12 pulados, 1 falha** em 612s — a falha era o guardião do README, que ainda não listava a `107`; corrigida em seguida |
| A suíte final, sobre o commit entregue | ver §Rodada final |
| `tests/navegador` sem o grupo `navegador` | 1 pulado, "sem o grupo opcional navegador" |
| `make test-navegador NAVEGADOR_VISIVEL=0 NAVEGADOR_CAPTURAS=…` | 5 passando; sete capturas, conferidas a olho (confirmação, histórico, busca, tela sem acesso, troca de unidade, administração, sessão encerrada) |
| `tests/seguranca/test_concorrencia_das_telas.py` com a trava da pessoa removida à mão, numa cópia descartável | a concessão concorrente **reprova** (`['gravado', 'gravado']`); a revogação concorrente passa mesmo sem a trava, porque a unicidade do banco recusa a segunda — é essa a garantia, e o teste a prende |

**Contagem de pulados.** Com os três grupos, 12 — os mesmos 12 da `106` no CI. Sem o `navegador`,
13 (o pulado do módulo inteiro, medido acima); sem ele e sem o `assistente`, 14 — derivado das duas
contagens, e não medido.

**Não executado nesta sessão**: o `make test-navegador` **com a janela aberta** (`FR-3132`) — o
comando é o mesmo, com `slow_mo` e `headless=False`, e não foi aberto na tela do usuário; e o
ambiente containerizado.

## Rodada final

Sobre `6f9b39c7` — o código deste PR; o commit seguinte só acrescenta este registro.

| Execução | Resultado |
|---|---|
| `make lint check test-pg`, 4 workers, `DB_NAME=ps107` | lint e `check` verdes; **13758 passando, 12 pulados, 1 falha**, em 727s |
| A falha: `tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem` | é o teste de tempo que o `AGENTS.md` registra como oscilante sob 4 workers (*Um teste de tempo oscila sob carga*). Isolado, **5 de 5 passaram** nesta branch. A `107` não toca a ocupação nem as telas dela |

Na primeira rodada, sobre a árvore anterior ao README, o mesmo teste passou e a falha foi a do
README. As duas rodadas somam 13758 passando; nenhuma falha se repetiu.

## CI

O CI do PR (#346) roda `uv sync` com os três grupos, instala o Chromium e roda a suíte com 4
workers, e por isso executa também as jornadas do navegador. O resultado do commit final fica no
próprio PR; a verificação desta sessão não o substitui.

## As decisões de 30/10, depois da entrega

O usuário respondeu P1 a P4 e as três propostas da `106` (spec, §Decisões do usuário). Nenhum código
de comportamento mudou com elas: o incremento 1 já exigia os prazos declarados em produção, que é o
que a P4 manda; mudaram os comentários e as mensagens que chamavam 8 h e 30 min de proposta, e o
roteiro de ativação passou a declarar os dois valores. O incremento 2 foi especificado, e **não
implementado**. Executado depois das edições: `ruff check`, `ruff format --check`, e os guardiões de
citação, do README, da configuração de produção e do prazo da sessão (83 passando).

## Incremento 2 — implementado depois do "sim, implementar" do usuário

**O que muda no banco**: a migration `seguranca/0002` cria `SuspensaoDePessoa` e
`ReativacaoDePessoa`, append-only nas duas camadas; `TABELAS_APPEND_ONLY` passa de 44 a **46**. Dois
guardiões sobem junto, com o motivo no comentário: `test_homologacao_preservada.py::
test_as_tabelas_append_only_anteriores_continuam_todas` (as cinco últimas e o total) e
`TRIGGERS_POR_APP` de `migrations/test_migrations.py` (os dois gatilhos novos). O
`test_database_permissions.py`, parametrizado pela lista, passa a provar as duas tabelas novas sem
mudança.

**O nome nas demais telas**: 41 exibições de autor em 24 templates passaram pela tag
`nome_de_pessoa`; ficaram com o identificador, de propósito, os valores de filtro e de atributo, a
confirmação da comissão (que mostra o identificador como será gravado), o identificador digitado
em Impedimentos e o seletor da demonstração. O guardião
`test_nome_nas_telas.py::test_nenhum_template_mostra_o_autor_sem_a_tag` prende a regra.

| Execução | Resultado |
|---|---|
| `make lint check test-pg`, 4 workers, `DB_NAME=ps107` | lint e `check` verdes; **13814 passando, 12 pulados, nenhuma falha**, em 606s |
| `tests/navegador` com capturas | 6 passando; as confirmações de suspensão e de reativação conferidas a olho |
| Concorrência da suspensão com a trava da pessoa removida à mão, numa cópia descartável | reprova (`['gravado', 'gravado']`); com a trava, passa |
| Substituição com falha forçada entre a revogação e a concessão | nenhuma das duas fica (`SC-1019`) |

**A salvaguarda da retirada da última administração institucional** (`D-018`) foi implementada como
salvaguarda técnica, anunciada ao usuário antes de implementar e revogável por ele: não proíbe nada,
só pede `--sem-administracao`.

## O que depende de fora deste repositório

- **A conexão real** com o provedor do Ifes: nada aqui fala com AD, LDAP, OIDC ou SAML. As jornadas
  provam a aplicação, com o adaptador simulado; o adaptador real precisa dos próprios testes contra
  um provedor de homologação (`doc/ativacao-do-sso-institucional.md`, §2).
- **A decisão sobre a retirada do último administrador institucional**, que as respostas de 30/10
  não cobrem; até lá, a salvaguarda técnica (`D-018`).
- **Abrir a gestão em produção**: não foi feito, nem é desta feature.

## Observações sem ação

- O link "Trocar identidade" do topo da moldura (`076`) aparece também na sessão institucional, e
  leva à página de acesso, que oferece "Continuar como…". Não é defeito; a frase é da demonstração.
  Registrado, não alterado.
- A análise de consistência entre spec, plano e tarefas foi feita à mão, depois das tarefas: todo
  `FR-` e `SC-` tem tarefa e teste ([rastreabilidade](rastreabilidade.md)), toda `D-` citada existe
  no [research](research.md). O `/speckit-analyze` não foi executado.
