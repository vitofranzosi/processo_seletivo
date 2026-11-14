# Tasks: A verificação da autodeclaração por vídeo, só em desenvolvimento

**Input**: Design documents from `specs/166-verificacao-por-video/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: sim, contra PostgreSQL, como em toda feature deste repositório. Os caminhos são relativos a
`backend/`. **Nenhum vídeo real**: os arquivos são gerados pela suíte (T-007).

**Organization**: por história. A US1 (admissão) é a fundação das demais; a US2 (candidato) precede a
US3 e a US4 (comissão), que leem o vídeo; a US5 sai da US2; a US6 e a US7 são independentes.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Banco de teste próprio da worktree (`DB_NAME=gps_166`), `uv sync --extra dev`, e `manage.py migrate --check` limpo antes de mexer

---

## Phase 2: Foundational

- [ ] T002 A chave `VERIFICACAO_POR_VIDEO` (padrão `false`), `VERIFICACAO_POR_VIDEO_LIMITE_BYTES` (64 MiB) e `VERIFICACAO_POR_VIDEO_RETENCAO_DIAS` (sem valor) em `config/settings/base.py`; `test.py` a liga; `production.py` a recusa por `_exigir`, com teste em `tests/test_configuracao_producao.py` (FR-7100, FR-7101, FR-7146, SC-2376)
- [ ] T003 [P] Domínio puro `processo_seletivo/verificacao/domain/conteiner.py` (assinatura e duração de MP4 e WebM), `roteiro.py` (a versão e os quatro passos, o teto de 180 s, a conferência das marcas), `intervalo.py` (o cabeçalho `Range`) e `admissao.py` (`videoOption`: ler, publicar, `admite_video(etapa)`), com testes em `tests/unit/verificacao/` sobre arquivos gerados à mão (FR-7112, FR-7113, FR-7120, FR-7131, T-003)
- [ ] T004 App `verificacao` com os cinco modelos de `data-model.md` e `verificacao/migrations/0001_inicial.py` com os quatro gatilhos append-only; `INSTALLED_APPS`; `TABELAS_APPEND_ONLY` (61 → 65); a contagem por app e os gatilhos em `tests/migrations/test_migrations.py`; testes dos gatilhos em `tests/integration/verificacao/test_append_only.py` (FR-7121, FR-7143, FR-7148, FR-7151)
- [ ] T005 [P] Guardião da R-19 em `tests/test_sem_inferencia_sobre_o_video.py`: nenhuma dependência de visão computacional, reconhecimento facial ou transcrição no `pyproject.toml` nem no `uv.lock`, e nenhum import delas no código (FR-7150)

---

## Phase 3: User Story 1 — Quem elabora admite o vídeo (P1) 🎯 MVP

- [ ] T006 [US1] Coluna `admite_video` em `editais/models/etapas.py` e `editais/migrations/0032_admite_video.py`; `videoOption` no `StageSerializer`, em `validate_stage` e em `replace_draft` (D-001)
- [ ] T007 [US1] Degrau 25: `SCHEMA_VERSION`, `DEGRAUS[25] = {"videoOption": False}`, `_stages` da publicação, `("stages","videoOption"): retificavel()`, o rótulo de `alteracoes.py`, a cobertura de `duvidas/domain/cobertura.py` (FR-7102)
- [ ] T008 [US1] As recusas impeditivas de `contracts/recusas.md` em `editais/domain/validation.py` (publicação e Retificação), e `video_ja_recebido` na Retificação (FR-7103, FR-7104, FR-7105)
- [ ] T009 [US1] A composição: o campo em `interface/forms.py` e `_etapa.html`, desabilitado com a razão quando a chave está desligada; a Revisão e a Retificação o mostram; o documento anuncia a opção na descrição da Etapa (`pdf.py`, `apresentacao.py`) (FR-7106, UX-770)
- [ ] T010 [P] [US1] Testes: `tests/unit/editais/test_video_na_publicacao.py` (as cinco recusas), `tests/interface/test_composicao_do_video.py` (o campo, a razão, o documento) e os guardiões que o campo atravessa (elevação, campos do contrato, etapas)

---

## Phase 4: User Story 2 — O candidato grava, revisa e envia (P1)

- [ ] T011 [US2] `verificacao/application/disponibilidade.py`: o estado do meio da inscrição na Etapa (`INDISPONIVEL`, `PODE_GRAVAR`, `RECEBIDO`, `EM_ANALISE`, `ENCAMINHADA`, `AO_VIVO`), o vídeo vigente e `em_modo_video(edital, etapa_id, inscricao_ids)` numa consulta (FR-7107, FR-7144, FR-7145, D-004)
- [ ] T012 [US2] `verificacao/application/envio.py`: iniciar, receber parte, consultar, concluir — titularidade, período (com a hora de tolerância), trava da inscrição, conferência de tamanho, contêiner, duração, marcas e resumo, o arquivo final no armazenamento privado, o evento `VIDEO_DA_VERIFICACAO_RECEBIDO`, a troca antes da abertura e a recusa depois (FR-7108 a FR-7126, FR-7152)
- [ ] T013 [US2] `politica_com_midia_local()` em `shared/politica_de_conteudo.py` e o cabeçalho `Permissions-Policy` só na página de gravação (FR-7117, T-004)
- [ ] T014 [US2] `portal/verificacao.py` (views), as rotas em `portal/urls.py`, o template `portal/verificacao.html` (escolha, acolhimento, maioridade, câmera, gravação, revisão, envio), `portal/verificacao_comprovante.html`, o cartão no acompanhamento, `portal/static/portal/gravacao.js` e as regras em `portal.css` (FR-7108 a FR-7116, FR-7123, FR-7145, UX-770 a UX-773)
- [ ] T015 [P] [US2] Testes de integração em `tests/integration/verificacao/test_envio.py`: partes, retomada, deslocamento errado, formato, duração, resumo divergente, maioridade, período, alcance, titularidade indistinguível, parecer concluído antes, envio concorrente (SC-2371, FR-7107 a FR-7126)
- [ ] T016 [P] [US2] Testes de interface em `tests/portal/test_verificacao_por_video.py`: a página com a CSP da exceção e a `Permissions-Policy`, as outras páginas sem elas, o cartão do acompanhamento por estado, a chave desligada (FR-7100, FR-7117, FR-7145, SC-2376)
- [ ] T017 [P] [US2] Teste JS em `tests/javascript/gravacao.test.js`: o descarte da tomada ao parar e recomeçar e à tela oculta, as marcas, a retomada do envio no deslocamento que o servidor devolve (FR-7111, FR-7115, FR-7119)

---

## Phase 5: User Story 5 — O titular vê o próprio vídeo, e troca (P2)

- [ ] T018 [US5] `verificacao/infrastructure/entrega.py` (intervalo, 206/416, tipo, `no-store`, `inline`) e `verificacao/application/abertura.py` (abrir: autorização, conferência do resumo, a `AberturaDoVideo`, o evento, a abertura na sessão; entregar: a abertura da sessão, sem evento) (FR-7127, FR-7130, FR-7131, D-007)
- [ ] T019 [US5] No portal: `POST video/abrir`, `GET video/<abertura>` e o `<video>` no comprovante (`portal/static/portal/assistir.js` só se preciso) (FR-7127)
- [ ] T020 [P] [US5] Testes em `tests/integration/verificacao/test_abertura.py`: `Range` (206, 416, sufixo), um evento por abertura com N pedidos, abertura alheia recusada, titular não encerra a troca, troca recusada depois da abertura da comissão, resumo divergente (SC-2372, FR-7124, FR-7127)

---

## Phase 6: User Story 3 — A comissão abre o vídeo e dá o parecer (P1)

- [ ] T021 [US3] `interface/verificacao.py`: `POST .../video/abrir` e `GET .../video/<abertura>` da Mesa, autorizados por `pode_avaliar_inscricao` (FR-7128 a FR-7131)
- [ ] T022 [US3] A Mesa: o vídeo no painel do documento (`_video_da_mesa.html`), os saltos por passo, ±10 s e 0,5× (`interface/static/interface/video_da_mesa.js`), os rótulos "Confirmo" e "Não dá para confirmar pelo vídeo" em modo vídeo (FR-7132, FR-7133, UX-774)
- [ ] T023 [US3] O gancho em `avaliacoes/application/avaliacao.concluir`: em modo vídeo, recusar `video_nao_aberto` sem abertura daquele membro, e exigir motivo no "Não dá para confirmar" (FR-7134)
- [ ] T024 [US3] As operações novas em `OPERACOES` e `OPERACOES_DA_AVALIACAO`, e as negativas novas no inventário da `033`
- [ ] T025 [P] [US3] Testes em `tests/integration/verificacao/test_mesa.py` e `tests/interface/test_video_na_mesa.py`: só o alocado com Atribuição abre (SC-2374), um evento por abertura, conclusão sem abertura recusada, rótulos, sem botão de baixar, às cegas mantido (FR-7128 a FR-7135)

---

## Phase 7: User Story 4 — O vídeo só confirma (P1)

- [ ] T026 [US4] O ramo da R-11 em `resultados/application/consolidacao._planejar` (recusa `ENCAMINHAR_AO_VIVO`, sem contagem) e a guarda `desfavoravel_pelo_video` no ato que grava o deliberado e na correção fixada do recurso (FR-7136 a FR-7139, D-006)
- [ ] T027 [US4] `verificacao/application/encaminhamento.py`: encaminhar (trava, unicidade, a linha, a reabertura da `012` de cada Avaliação, o evento; tudo ou nada) (FR-7140 a FR-7144, D-005)
- [ ] T028 [US4] A conferência mostra "Encaminhar à entrevista ao vivo" com a ação; a tela de confirmação com o alcance; as rotas em `interface/urls.py` (FR-7138, FR-7140)
- [ ] T029 [P] [US4] Testes em `tests/unit/verificacao/test_r11.py` (três regras × três e cinco pareceres pelo vídeo: zero desfavoráveis, SC-2373) e `tests/integration/verificacao/test_encaminhamento.py` (consolidação favorável, encaminhar, reabertura, deliberação ao vivo desfavorável, duplicado recusado, autor exposto recusa tudo, chamada direta recusada)

---

## Phase 8: User Story 6 — Retenção (P3)

- [ ] T030 [US6] `verificacao/application/retencao.py` e `verificacao/management/commands/eliminar_videos_da_verificacao.py`; a Mesa, o comprovante e a entrega dizem "arquivo eliminado em …" (FR-7146 a FR-7149, D-008)
- [ ] T031 [P] [US6] Testes em `tests/integration/verificacao/test_retencao.py`: sem prazo recusa e elimina zero (SC-2375); Edital não encerrado; dentro do prazo, com a data; sem `--confirmar` só lista; com prazo vencido elimina, registra e preserva o resumo

---

## Phase 9: User Story 7 — A porta do piloto (P3)

- [ ] T032 [US7] `doc/verificacao-por-video-porta-do-piloto.md`: o caminho P-0 → protocolo → Edital → PR revisado, o que a chave libera e o que não libera, a matriz de navegadores como critério (FR-7153, SC-2377)

---

## Phase 10: Polish

- [ ] T033 `rastreabilidade.md` com toda FR-, SC- e UX- desta spec; a entrada `verificacao-por-video-166` no `.claude/launch.json`; o `M` e a contagem de migrations no `CLAUDE.md` e no README, se citados
- [ ] T034 `make lint check` e as pastas tocadas contra PostgreSQL; depois `make test-pg` inteiro, uma vez, sem outra suíte no cluster
- [ ] T035 A jornada do candidato no navegador do painel, com fonte sintética: escolha → comprovante, queda no envio, 375 px, console sem violação (SC-2370); a Mesa abrindo o vídeo

## Dependencies

- T002–T005 antes de tudo; T006–T010 (US1) antes de T011 em diante, porque a disponibilidade lê `videoOption`.
- US2 (T011–T017) antes de US5, US3 e US4.
- T018 (entrega) antes de T021.
- T023 antes de T029; T026 antes de T027.
- US6 e US7 dependem só da fundação.

## Parallel Example

T003 e T005 em paralelo; dentro de cada história, os testes `[P]` em paralelo com as telas.

## Implementation Strategy

MVP = US1 + US2 (o candidato envia; o vídeo existe). Depois US5 e US3, depois US4 (a R-11), depois
US6, US7 e o polimento. A cada história, a pasta de testes dela contra PostgreSQL.
