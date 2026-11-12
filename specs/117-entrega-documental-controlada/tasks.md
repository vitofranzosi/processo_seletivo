# Tasks: Entrega documental controlada ao setor da formalização

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md),
[quickstart.md](quickstart.md)

**Pré-condição cumprida em 04/11**: a `115` está na `main` (PR #369, merge `f563b5a3`), e o desenho foi
aprovado. A implementação pode começar.

**Testes**: incluídos, contra PostgreSQL.

Formato: `[ID] [P?] [História] Descrição`. `[P]` = arquivos distintos, sem dependência pendente.

## Fase 1: Preparação

- [X] T001 Confirmar a `main` com a `115` e CI verde; rodar `manage.py migrate --check`
- [X] T002 Aplicar a revisão **aprovada** da FR-069 em `specs/009-inscricao-simples-documentos/spec.md` e da FR-3606 em `specs/115-documentos-na-convocacao/spec.md`, com o texto da D-016 e a nota *"revista pela `117` em ‹data›, por decisão do usuário de 04/11/2026"*; rodar `tests/test_citacoes_de_requisito.py`
- [X] T003 Criar o app `backend/processo_seletivo/formalizacao/`, registrá-lo em `INSTALLED_APPS` e atualizar o guardião de contagem de migrations por app

## Fase 2: Fundação

- [X] T004 Modelos das quatro tabelas em `formalizacao/models.py`, com as constraints do data-model (motivo não vazio; resultado `COMPLETO`/`PARCIAL`; hash não vazio; autodesignação)
- [X] T005 Migration `0001_inicial` com gatilhos append-only; as quatro tabelas em `TABELAS_APPEND_ONLY`; `M` de 49 para 53 em `CLAUDE.md` e `AGENTS.md`
- [X] T006 [P] `formalizacao/domain/nomes.py`: capacidade `formalizacao:acessar`, códigos de recusa, situações, resultados, operações da trilha com rótulos e classe da trava
- [X] T007 [P] Papel `formalizacao` em `PAPEIS` e `DESCRICOES` (`interface/identidade.py`) e teste de grafia (FR-3661)
- [X] T008 `ArquivoIndisponivel` em `portal/arquivos.py`; 409 e evento `ARQUIVO_INDISPONIVEL` nas views de documento da inscrição, da mesa e da convocação (FR-3695)
- [X] T009 [P] Regressão da T008 em `tests/interface/test_arquivo_indisponivel.py`: nenhuma das três views responde 500
- [X] T010 [P] `formalizacao/domain/caminhos.py` e testes em `tests/unit/formalizacao/test_caminhos.py`, com nomes hostis: `../x`, `CON`, controle, 300 caracteres, colisões depois da normalização, vazio (FR-3712, SC-1114)

## Fase 3: US1 — Definição dos documentos (P1)

- [X] T011 [US1] `formalizacao/application/definir.py`: base de gerir comissão, requisitos das versões publicadas, motivo obrigatório, versão nova, histórico com diferença, evento (FR-3653 a FR-3656, FR-3711)
- [X] T012 [US1] Tela *Documentos para a formalização* na condução: lista sem marcação, avisos de recorte por modalidade e de momento da inscrição, histórico (FR-3658, FR-3711)
- [X] T013 [P] [US1] `tests/integration/formalizacao/test_definicao.py`: vazia por padrão, motivo recusado se vazio, versões, avisos, histórico visível à condução e ao auditor e recusado ao setor, snapshot, hash e PDF intactos (FR-3657, FR-3660)

## Fase 4: US2 — Acesso (P1)

- [X] T014 [US2] `formalizacao/domain/autorizacao.py`: `pode_acessar` → `ok`, `404` ou `403(papel)` (FR-3664, FR-3666)
- [X] T015 [US2] `formalizacao/application/designar.py`: `acesso:gerir`, papel vigente, sem autodesignação, Perfis, `select_for_update`, trilha da unidade e do Edital (FR-3662, FR-3663, FR-3668)
- [X] T016 [US2] Seção *Editais da formalização* em `interface/acessos.py`; leitura das designações na condução (FR-3668)
- [X] T017 [P] [US2] `tests/integration/formalizacao/test_acesso.py`: sem papel, autodesignação, presidência recusada, revogação, papel revogado corta todas, suspensão, Perfis, concorrência, append-only por gatilho (FR-3667)

## Fase 5: US3 — Página e consulta (P1)

- [X] T018 [US3] `formalizacao/application/conjunto.py`: seletor único em lote, convocação e inscrição, deduplicação, situações e última exportação (FR-3669 a FR-3674)
- [X] T019 [P] [US3] `tests/unit/formalizacao/test_conjunto.py`:
  - aceite, regularização;
  - desfecho e convocação sucedidos;
  - duas chamadas;
  - não se aplica, não apresentado, não conferido;
  - inscrição e aproveitamento;
  - versão da definição.
- [X] T020 [US3] `interface/views_formalizacao.py`: lista de Editais, página, visualizar e baixar com nome normalizado e eventos; módulo em `MODULOS_DE_VIEW`; templates, `interface/telas/formalizacao.css`, `Secao` na barra e seletor de Perfil (FR-3675 a FR-3681)
- [X] T021 [US3] Linhas novas em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`
- [X] T022 [P] [US3] `tests/interface/test_permissoes_da_formalizacao.py`: a matriz inteira, por URL e POST, inclusive o histórico da definição (SC-1104)
- [X] T023 [P] [US3] `tests/interface/test_vocabulario_da_formalizacao.py`: termos vedados e 375 px (FR-3680, SC-1112)

## Fase 6: US4 — Verificação e exportação (P1)

- [X] T024 [US4] `formalizacao/infrastructure/pacote.py`: `ZIP_STORED` em `TemporaryFile`, entradas a partir da T010, hash numa leitura, `manifesto.csv` com BOM e neutralização (FR-3686 a FR-3688, FR-3690, FR-3713)
- [X] T024a [US4] `formalizacao/application/comprovante.py`: `emitir` e `conferir` com `django.core.signing` (sal próprio, `max_age` de 15 min, vínculo ao ator e à unidade) e o resumo canônico do conteúdo verificado, com incluídas, excluídas e motivos (FR-3689a, FR-3689b)
- [X] T025 [US4] `formalizacao/application/exportar.py`:
  - `compor_e_ler`: uma leitura por arquivo, com incluídas e excluídas;
  - `verificar`: limite antes de ler, trava de transação, resultado, comprovante, evento;
  - `montar`: comprovante conferido antes de ler, autorizações revalidadas, trava, releitura de todas as pessoas (inclusive excluídas) na mesma passagem da montagem, resumo comparado, *verificação defasada*, atomicidade por pessoa, manifesto com incluídas e não incluídas, registro antes da resposta;
  - exceção → rollback, fechamento do temporário e *exportação interrompida* em transação própria.
  
  Cobre as FR-3682 a FR-3698 e a FR-3714.
- [X] T026 [US4] Views e templates: a tela da verificação, com o resultado no topo, os excluídos com o motivo e o botão com N pessoas e *parcial*; o download; a exportação por pessoa, com a página de falha; o histórico (FR-3679); a configuração `EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB`
- [X] T027 [P] [US4] `tests/integration/formalizacao/test_exportacao.py`:
  - completo e parcial;
  - nome `-parcial`;
  - manifesto com excluídos;
  - SHA-256 (SC-1107);
  - determinismo (SC-1108);
  - verificação defasada por desfecho, por designação (revogada e concedida de novo), por definição, por arquivo trocado, por excluído restaurado e por motivo trocado (FR-3689b, SC-1113);
  - recorte;
  - POST forjado;
  - pessoa única completa e com falha;
  - nenhuma pré-seleção.
- [X] T028 [P] [US4] `tests/integration/formalizacao/test_ciclo_de_vida.py`: nenhum arquivo remanescente e trava livre depois de sucesso, recusa, exceção injetada e cliente desconectado; a conexão fechada libera a trava; o registro está ausente quando a montagem não comita (SC-1106, FR-3692, FR-3714)
- [X] T029a [P] [US4] `tests/integration/formalizacao/test_comprovante.py`, em que todos recusam **sem ler arquivo**:
  - adulterado (um byte trocado);
  - fabricado (resumo SHA-256 simples sem assinatura; assinado com outro sal);
  - expirado (tempo congelado além de 15 min);
  - emitido para outro servidor ou outra unidade;
  - apresentado depois da revogação do papel (403) e da designação (404).
  
  O reuso dentro da validade gera uma segunda exportação registrada (FR-3689a, SC-1113).
- [X] T029 [P] [US4] `tests/integration/formalizacao/test_concorrencia.py`: a segunda verificação ou montagem do mesmo servidor é recusada; a de outro servidor não (FR-3692)

## Fase 7: US5 — Falhas (P1)

- [X] T030 [US5] `tests/integration/formalizacao/test_falhas.py`:
  - ausente e divergente na verificação e na montagem;
  - todos falhando: sem botão e sem registro;
  - limite antes de ler;
  - página de exceção.
  
  Cobre a SC-1105 e as FR-3691, FR-3694 a FR-3698 e FR-3714.
- [X] T031 [P] [US5] Logs capturados nas falhas sem nome, CPF ou nome de arquivo (FR-3703)

## Fase 8: Acabamento

- [X] T032 Fixture `montar_cenario_da_formalizacao` em `tests/fixtures/formalizacao.py`, com injeção de exceção na montagem
- [X] T033 [P] `tests/performance/test_exportacao_de_formalizacao.py`: consultas constantes com 5 e 45 pessoas; verificação e montagem do Cenário A **medidas e relatadas em separado**, menos de 30 s cada, no CI. Sem medir transferência, que é da VM (SC-1111)
- [X] T034 [P] `tests/navegador/test_jornada_da_formalizacao.py`: Cenários A, E e F (verificação parcial antes do download)
- [X] T035 Rótulos das operações em `trilha_do_edital` e na trilha da unidade (FR-3699, FR-3702)
- [X] T036 Em `doc/implantacao-em-producao-ubuntu.md`: o limite configurável e o roteiro de validação de capacidade da §5.4 do diagnóstico, para a TI. Sem presumir buffering do nginx
- [X] T037 `rastreabilidade.md` (FR-3653 a FR-3714, SC-1101 a SC-1114) e `verificacao.md`; README
- [X] T038 `cd backend && make lint check test-pg`, com o grupo `navegador`
- [X] T039 Demonstração do quickstart com capturas a 1280 px e a 375 px

## Fora da implementação (homologação)

- [ ] H01 Validação de capacidade na VM, pela TI (homologação, item 5): verificação, montagem e transferência medidas em separado; ajustar o limite de produção ao que a medição sustentar
- [ ] H02 Exportação real por um servidor do setor (homologação, item 4)
- [ ] H03 Aviso de privacidade do Edital, pela área de proteção de dados

## Dependências

- **Fase 1 → Fase 2 → US1 e US2**, que podem andar em paralelo.
- **US3** depende de US1 e US2. **US4** depende de US3 e da T010. **US5** depende de US4.
- **Primeiro corte demonstrável**: Fases 1 a 5 (Cenário B). O Cenário A exige a US4.

## Revisão de 12/11/2026 — a presidência também designa (D-025)

- [X] T040 Revisão explícita da D-013, da FR-3663, da FR-3668, da US2 (cenário 4) e da matriz, com a redação anterior preservada; D-025, seção J (FR-6700 a FR-6708, UX-700 a UX-702) e SC-2200 a SC-2204. Na `153`: D-006, US2, FR-6108 e FR-6111
- [X] T041 `pode_designar` em `formalizacao/domain/autorizacao.py`; `designar`, `revogar` e `pessoas_com_o_papel` passam por ele, com a base na trilha (FR-6700 a FR-6707)
- [X] T042 [US2] A seção "Quem acessa os documentos" da definição designa e revoga, com dois POST novos em `interface/views_formalizacao.py`; linha nova no inventário da `033` (UX-700 a UX-702)
- [X] T043 [P] O andamento e a advertência do encerramento seguem o predicado (FR-6708)
- [X] T044 `test_a_presidencia_nao_designa` vira a prova da regra e dos limites; casos da tela; `test_passagem_ao_setor.py` atualizado (SC-2200 a SC-2204)
- [ ] T045 `rastreabilidade.md` e `verificacao.md`
- [ ] T046 `cd backend && make lint check test-pg`, e verificação no navegador com dados sintéticos

**Dependências da revisão:** T040 → T041 → T042 e T043, em paralelo → T044 → T045 → T046.
