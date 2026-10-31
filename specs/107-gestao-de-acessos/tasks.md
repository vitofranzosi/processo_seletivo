# Tasks: Gestão de acessos pela interface

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/telas-e-rotas.md](contracts/telas-e-rotas.md). Caminhos relativos a `backend/`.

## Fase 1 — Núcleo

- [x] T001 `seguranca/relogio.py`: `agora()`, o instante que os testes fixam (D-009)
- [x] T002 `seguranca/application/acessos.py`: `buscar_pessoas`, `historico`, `administradores_por_unidade`, `vigentes_da_pessoa`, `pessoa_institucional`; recusa de pessoa inativa em `conceder` (D-005, D-011)
- [x] T003 `interface/identidade.py`: a resolução lê os vínculos da pessoa uma vez e guarda a pessoa; `escopos_do_ator`, `nome_do_ator` (D-006, D-008)
- [x] T004 [P] Testes da camada: busca (piso, teto, ator fora, inativo fora, escopo exigido), histórico por unidade, pessoa inativa recusada — pela tela, em `tests/seguranca/test_telas_de_acesso.py` (convergência: o arquivo próprio da camada não foi criado, e os casos de busca e histórico ficaram com os da tela, que exercitam a mesma função)

## Fase 2 — Sessão com prazo (US5)

- [x] T005 Prazos na sessão: `entrada_em`, `atividade_em`, término com `SAIDA` e motivo, marca para a página de acesso, cabeçalho de requisição automática (D-009)
- [x] T006 `config/settings/base.py` e `production.py`: os dois prazos; produção recusa sem eles quando há provedor (D-010)
- [x] T007 [P] Testes: `tests/seguranca/test_sessao_com_prazo.py`; casos novos em `tests/test_configuracao_producao.py`

## Fase 3 — Telas (US1 a US4)

- [x] T008 `pedir_identificacao` desvia para `sem-acesso`; view e `sem_acesso.html` (D-007)
- [x] T009 `base.html`: nome, iniciais do nome, seletor de unidade; `identificar.html`: nome e motivo do término (D-008)
- [x] T010 `interface/acessos.py`: os dois níveis e as views de lista, conceder e revogar (D-002 a D-004)
- [x] T011 Templates `acessos.html`, `acessos_conceder.html`, `acessos_confirmar.html`; folha `interface/telas/acessos.css`
- [x] T012 `navegacao.py` e o sprite: "Acessos da unidade" e "Administração de acessos"
- [x] T013 `urls.py`; `MODULOS_DE_VIEW` e o inventário de negativas da `033` (D-014)
- [x] T014 [P] Testes de cliente: `tests/seguranca/test_telas_de_acesso.py` (jornadas, autoconcessão, outra unidade, busca sem termo, demonstração recusada, revogação com sessão aberta, comissão)
- [x] T015 [P] Concorrência pela tela e privilégios da runtime: `tests/seguranca/test_concorrencia_das_telas.py` e `tests/seguranca/test_privilegios_das_telas.py` (arquivo próprio, e não casos no da `106`)

## Fase 4 — Navegador (FR-3131 a FR-3133)

- [x] T016 `pyproject.toml`: grupo `navegador`; `tests/fixtures/provedor_simulado.py`: endereço de autorização e `redirect_uri` (D-012, D-013)
- [x] T017 `tests/navegador/provedor.py` e `conftest.py`: a página do provedor, o navegador, `NAVEGADOR_VISIVEL`
- [x] T018 `tests/navegador/test_jornadas_de_acesso.py`: US1 a US5, preparação → ações → verificações
- [x] T019 `Makefile` (`test-navegador`) e `.github/workflows/backend.yml` (grupo e Chromium)

## Fase 5 — Documentação e verificação

- [x] T020 `quickstart.md`: o roteiro manual da homologação e o roteiro do navegador
- [x] T021 `doc/ativacao-do-sso-institucional.md` e `doc/homologacao-com-o-seletor-de-demonstracao.md`: o que saiu da lista de pendências; `AGENTS.md`: o grupo `navegador` e os pulados
- [x] T022 `rastreabilidade.md` e `verificacao.md`
- [x] T023 `make lint check test-pg`; CI do commit final (ver a verificação)

## Incremento 2 — implementado

- [x] T024 Modelos `SuspensaoDePessoa` e `ReativacaoDePessoa`, migration `seguranca/0002`, gatilhos, `TABELAS_APPEND_ONLY` (44 → 46) e guardiões de contagem (D-016)
- [x] T025 `suspender` e `reativar` na camada de aplicação, com a trava da pessoa, a troca do hash da sessão e a trilha (D-015, D-016)
- [x] T026 A entrada recusa a pessoa suspensa com a frase de acesso suspenso; a busca e a concessão a recusam (FR-3140, FR-3141)
- [x] T027 A seção de suspensão e reativação em "Administração de acessos", com as duas confirmações; a marca de suspensa em "Acessos da unidade" (D-017)
- [x] T028 Comandos `suspender_pessoa` e `reativar_pessoa` (D-017)
- [x] T029 Comandos `retirar_administracao_institucional` e `substituir_administracao_institucional`; a salvaguarda do último, confirmada pelo usuário (D-018, P5)
- [x] T030 O filtro `nome_de_pessoa` e os templates que exibem autor (D-019)
- [x] T031 [P] Testes de cliente, concorrência e privilégios do incremento 2
- [x] T032 [P] A jornada de suspensão e reativação no navegador
- [x] T033 Documentação, rastreabilidade e verificação do incremento 2

## Dependências

Incremento 1: T001–T003 antes de tudo. T005 depende de T003. T008–T013 dependem de T002 e T003. T018 depende das
fases 2 e 3. T022 e T023 por último.

Incremento 2: T024 antes de tudo; T025 antes de T026–T029; T030 é independente; T031–T033 por último.
