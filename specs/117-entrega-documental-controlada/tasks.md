# Tasks: Entrega documental controlada ao setor da formalização

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md),
[quickstart.md](quickstart.md)

**Pré-condição**: as quatro pendências bloqueantes da spec estão resolvidas, e o PR #369 está na
`main`. Sem isso, nenhuma tarefa começa.

**Testes**: incluídos, contra PostgreSQL.

Formato: `[ID] [P?] [História] Descrição`. `[P]` = arquivos distintos, sem dependência pendente.

## Fase 1: Preparação

- [ ] T001 Confirmar a `main` com o PR #369 e CI verde; `manage.py migrate --check`
- [ ] T002 Aplicar a revisão aprovada da FR-069 em `specs/009-inscricao-simples-documentos/spec.md` e da FR-3606 em `specs/115-documentos-na-convocacao/spec.md`, com a nota de data e decisão (D-016)
- [ ] T003 Criar o app `backend/processo_seletivo/formalizacao/`, registrá-lo em `INSTALLED_APPS` e atualizar o guardião de contagem de migrations por app

## Fase 2: Fundação

- [ ] T004 Modelos das quatro tabelas em `formalizacao/models.py`, com as constraints do data-model
- [ ] T005 Migration `0001_inicial` com gatilhos append-only; as quatro tabelas em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`); `M` de 46 para 50 em `CLAUDE.md` e `AGENTS.md`
- [ ] T006 [P] `formalizacao/domain/nomes.py`: capacidade `formalizacao:acessar`, códigos de recusa, situações, resultados e operações da trilha com rótulos
- [ ] T007 [P] Papel `formalizacao` em `PAPEIS` e `DESCRICOES` (`interface/identidade.py`) e teste de grafia (FR-3661)
- [ ] T008 `ArquivoIndisponivel` em `portal/arquivos.py`; recusa 409 e evento `ARQUIVO_INDISPONIVEL` nas views de documento da inscrição, da mesa e da convocação (FR-3695)
- [ ] T009 [P] Regressão da T008 em `tests/interface/test_arquivo_indisponivel.py`: nenhuma das três views responde 500

## Fase 3: US1 — Definição dos documentos (P1)

- [ ] T010 [US1] `formalizacao/application/definir.py`: base de gerir comissão, requisitos das versões publicadas, motivo, versão nova, evento (FR-3653 a FR-3656)
- [ ] T011 [US1] Tela *Documentos para a formalização* na condução, com o aviso de recorte por modalidade (FR-3658)
- [ ] T012 [P] [US1] Testes em `tests/integration/formalizacao/test_definicao.py`: vazia por padrão, versões, quem pode, aviso, snapshot, hash e PDF intactos (FR-3657, FR-3660)

## Fase 4: US2 — Acesso (P1)

- [ ] T013 [US2] `formalizacao/domain/autorizacao.py`: `pode_acessar` → `ok`, `404` ou `403(papel)` (FR-3664, FR-3666)
- [ ] T014 [US2] `formalizacao/application/designar.py`: `acesso:gerir`, papel vigente, sem autodesignação, Perfis, `select_for_update`, trilha da unidade e do Edital (FR-3662, FR-3663, FR-3668)
- [ ] T015 [US2] Seção *Editais da formalização* na pessoa, em `interface/acessos.py`, e leitura das designações na condução (FR-3668)
- [ ] T016 [P] [US2] Testes em `tests/integration/formalizacao/test_acesso.py`: sem papel, autodesignação, presidência recusada, revogação, papel revogado corta todas, suspensão, Perfis, concorrência, append-only por gatilho (FR-3667)

## Fase 5: US3 — Página e consulta (P1)

- [ ] T017 [US3] `formalizacao/application/conjunto.py`: seletor único em lote, convocação e inscrição, deduplicação, situações e última exportação (FR-3669 a FR-3674)
- [ ] T018 [P] [US3] Testes do seletor em `tests/unit/formalizacao/test_conjunto.py`:
  - aceite, regularização, desfecho sucedido, convocação sucedida, duas chamadas;
  - não se aplica, não apresentado, não conferido;
  - documento da inscrição, aproveitamento, versão da definição.
- [ ] T019 [US3] `interface/views_formalizacao.py`: lista de Editais, página, visualizar e baixar com nome derivado e eventos; módulo em `MODULOS_DE_VIEW` (FR-3675 a FR-3678)
- [ ] T020 [US3] Templates, `interface/telas/formalizacao.css`, `Secao` na barra e seletor de Perfil (FR-3681)
- [ ] T021 [US3] Linhas novas em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`
- [ ] T022 [P] [US3] `tests/interface/test_permissoes_da_formalizacao.py`: a matriz inteira, por URL e POST (SC-1104)
- [ ] T023 [P] [US3] `tests/interface/test_vocabulario_da_formalizacao.py`: termos vedados e 375 px (FR-3680, SC-1112)

## Fase 6: US4 — Exportação (P1)

- [ ] T024 [US4] `formalizacao/infrastructure/pacote.py`: `ZIP_STORED` em `TemporaryFile`, entradas determinísticas, hash numa leitura, pasta normalizada (FR-3686, FR-3688, FR-3690)
- [ ] T025 [US4] `formalizacao/application/exportar.py`: alcances, recusa inteira por id fora do alcance, prévia com existência e tamanhos, assinatura, limite, trava consultiva, atomicidade por pessoa, manifesto, resultado, registro e evento (FR-3682 a FR-3698)
- [ ] T026 [US4] Views e templates da prévia, da confirmação, da exportação por pessoa e do resultado; histórico (FR-3679); configuração `EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB`
- [ ] T027 [P] [US4] `tests/integration/formalizacao/test_exportacao.py`:
  - estrutura e manifesto;
  - SHA-256 (SC-1107);
  - determinismo (SC-1108);
  - prévia defasada;
  - recorte e seleção forjada;
  - pessoa;
  - nenhuma pré-seleção.
- [ ] T028 [P] [US4] `tests/integration/formalizacao/test_temporarios.py`: nada remanescente, com sucesso, recusa e exceção injetada (SC-1106)
- [ ] T029 [P] [US4] `tests/integration/formalizacao/test_concorrencia.py`: segunda exportação do mesmo servidor recusada (FR-3692)

## Fase 7: US5 — Falhas (P1)

- [ ] T030 [US5] `tests/integration/formalizacao/test_falhas.py`:
  - ausente;
  - divergente;
  - todos falhando, com resultado sem pacote;
  - limite antes de ler;
  - resultado na tela.
  
  Cobre a SC-1105 e as FR-3691, FR-3694 a FR-3698.
- [ ] T031 [P] [US5] Logs capturados nas falhas sem nome, CPF ou nome de arquivo (FR-3703)

## Fase 8: Acabamento

- [ ] T032 Fixture `montar_cenario_da_formalizacao` em `tests/fixtures/formalizacao.py`, sobre as da `115`
- [ ] T033 [P] `tests/performance/test_exportacao_de_formalizacao.py`: consultas constantes com 5 e 45 pessoas; Cenário A em menos de 30 s (SC-1111)
- [ ] T034 [P] `tests/navegador/test_jornada_da_formalizacao.py`: Cenários A e E
- [ ] T035 Rótulos das operações em `trilha_do_edital` e na trilha da unidade (FR-3699, FR-3702)
- [ ] T036 Nota do limite e do buffer do nginx em `doc/implantacao-em-producao-ubuntu.md`
- [ ] T037 `rastreabilidade.md` (FR-3653 a FR-3710, SC-1101 a SC-1112) e `verificacao.md`; README
- [ ] T038 `cd backend && make lint check test-pg`, com o grupo `navegador`
- [ ] T039 Demonstração do quickstart com capturas a 1280 px e a 375 px

## Dependências

- **Fase 1 → Fase 2 → US1 e US2**, que podem andar em paralelo.
- **US3** depende de US1 e US2. **US4** depende de US3. **US5** depende de US4.
- **Primeiro corte demonstrável**: Fases 1 a 5, que atendem o Cenário B. O Cenário A exige a US4.
