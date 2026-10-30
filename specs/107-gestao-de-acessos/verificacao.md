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

Preenchida depois da última execução, sobre o commit que vai ao PR.

## CI

Preenchido depois do push.

## O que depende de fora deste repositório

- **A conexão real** com o provedor do Ifes: nada aqui fala com AD, LDAP, OIDC ou SAML. As jornadas
  provam a aplicação, com o adaptador simulado; o adaptador real precisa dos próprios testes contra
  um provedor de homologação (`doc/ativacao-do-sso-institucional.md`, §2).
- **As decisões P1 a P4** da spec e as três propostas da `106`.
- **Abrir a gestão em produção**: não foi feito, nem é desta feature.

## Observações sem ação

- O link "Trocar identidade" do topo da moldura (`076`) aparece também na sessão institucional, e
  leva à página de acesso, que oferece "Continuar como…". Não é defeito; a frase é da demonstração.
  Registrado, não alterado.
- A análise de consistência entre spec, plano e tarefas foi feita à mão, depois das tarefas: todo
  `FR-` e `SC-` tem tarefa e teste ([rastreabilidade](rastreabilidade.md)), toda `D-` citada existe
  no [research](research.md). O `/speckit-analyze` não foi executado.
