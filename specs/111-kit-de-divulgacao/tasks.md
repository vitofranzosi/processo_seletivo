# Tasks: Kit de Divulgação do Edital

**Input**: Design documents from `specs/111-kit-de-divulgacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/kit.md](contracts/kit.md),
[revisao-critica.md](revisao-critica.md)

**Tests**: exigidos pela Constituição (princípio V) e pelo pedido de 31/10/2026, que quer a
especificação testável. **Em cada fase, o teste vem antes do código que ele prende**, e as tarefas de
teste o dizem. Caminhos relativos a `backend/`.

**Referência, e não código a copiar**: a [POC](../../doc/poc-kit-de-divulgacao-2026-10-31/) mostra as
regras e os cenários. A implementação reescreve sobre a estrutura do [plano](plan.md). Três leituras da
POC são **exatamente o que não se repete**: a proveniência pelo caminho exato, a soma de vagas sem
saneamento e a prorrogação só por data ([revisão](revisao-critica.md), achados 1, 10 e 11).

**Incrementos** (D-001):

- **A**: Phases 1 a 4. Ficha, textos, tela, porta e rastreio. Útil sozinho.
- **B**: Phase 5. A peça. Começa pela verificação do motor (T024), e só vai a produção com a P-3 e a
  P-4 respondidas.
- **C**: Phase 6. Pacote e galeria.

Cada incremento é um PR, revisto e mergeado antes do seguinte. **O merge é do usuário.** A
**atribuição do papel** a qualquer pessoa espera a P-1, a P-2 e a P-7.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo, porque toca arquivo diferente e não depende de tarefa incompleta.
- **[Story]**: US1 a US5 da [spec](spec.md).

---

## Phase 1: Setup

- [x] T001 Criar os pacotes `tests/integration/kit/__init__.py` e `tests/unit/kit/__init__.py`, e conferir que `.specify/feature.json` aponta para `specs/111-kit-de-divulgacao`

---

## Phase 2: Foundational (bloqueia as histórias)

- [x] T002 Mover, **sem mudar o corpo**, as três leituras da D-002, cada uma com os seus chamadores no mesmo commit:
  - `retificacoes_a_vigorar` de `processo_seletivo/interface/agenda.py` para `processo_seletivo/publicacoes/application/selectors.py`;
  - `_versoes` e a regra de prorrogação em linha de `fatos_do_edital` (`processo_seletivo/interface/relatorio_do_edital.py`) para `selectors.py`, como `versoes_original_e_vigente` e `prorrogacao(original, vigente)`. A regra é a de hoje, **literal**: término vigente posterior ao original, comparados como instantes;
  - `_retificacoes_publicadas` (a numeração por `published_at`) para `selectors.py`;
  - ~~`origens`/`acrescimos` para `publicacoes/domain/origem.py`~~ — não movidas: a ficha usa o `contexto()` da `070`, que o portal já importa (D-002, revisto na implementação).

  **Esta tarefa só move.** As suítes da agenda (`101`), do relatório (`099`) e da fonte de consulta
  (`070`) ficam verdes sem alteração de teste. É a prova de que nada mudou (FR-3405).

  **Teste de regressão, escrito antes de mover**, em
  `tests/unit/publicacoes/test_prorrogacao.py`. Ele prende a regra de hoje, que nenhuma suíte prende
  isoladamente: término posterior, igual e anterior; ausente de um lado; e **término adiado só na
  hora, no mesmo dia, que já conta como prorrogação**. A revisão atribuiu à regra um erro que era do
  texto da POC, que comparava só as datas. A regra não muda; quem passa a escrever a hora quando a
  data coincide é o texto do kit, na T007/T008 (FR-3417, EC-25).
- [x] T003 [P] Escrever a fixture dos cenários de referência em `tests/fixtures/kit.py`, a partir de `doc/poc-kit-de-divulgacao-2026-10-31/test_poc_kit.py`:
  - `publicar_do_corpus` com deslocamento em dias inteiros;
  - as variações pelo `mudar`: um Perfil, localidade ausente, sem período, caractere sem grafia, prorrogação só de hora, Perfil substituído inteiro;
  - o cancelado do piloto;
  - o período encerrado por `encerrar_inscricoes`;
  - o mesmo número em duas unidades, com a segunda unidade da `110`;
  - um caso por Edital, porque o 91/2026 repetido colide.
- [x] T004 [P] Acrescentar a capacidade `material:gerar` e o papel `comunicacao` em `processo_seletivo/interface/identidade.py` (`PAPEIS`, `DESCRICOES`), sem concedê-la a nenhum papel existente.
  - Atualizar `tests/seguranca/test_vinculos.py` (`len(PAPEIS)`), o ícone em `processo_seletivo/interface/demonstracao.py`, os comentários de "oito papéis" em `navegacao.py` e `acessos.py`, e decidir o `LIMIAR_DA_BUSCA` (9 ou a busca aparece), com o teste de `tests/interface/test_entrada_da_gestao.py`.
  - Teste novo em `tests/authorization/test_papel_da_comunicacao.py`: o papel carrega só a capacidade, e nenhum outro papel a tem (FR-3403, D-012).

**Checkpoint**: as suítes da `070`, da `099` e da `101` verdes; a fixture publica os 16 cenários.

---

## Phase 3: User Story 1 — Conferir e copiar os textos oficiais (P1) 🎯 MVP

**Goal**: a tela do kit com a conferência e os textos, para quem tem a capacidade.

**Independent Test**: 91/2026 prorrogado; a tela mostra o término vigente, a proveniência da
Retificação, as quatro localidades e uma legenda sem "abertas".

- [x] T005 [P] [US1] **Teste primeiro**: a ficha, em `tests/integration/kit/test_ficha.py`:
  - equivalência com o cartão da vitrine **e** com o contexto da página da seleção, no mesmo instante, em todos os cenários (FR-3407);
  - modo por cenário, inclusive a P-8 (FR-3410);
  - proveniência pela regra da `070`, com Perfil substituído inteiro, Evento substituído inteiro e Perfil acrescentado (FR-3408);
  - impressão: igual para dados iguais; sem instante, versão, host nem ordem; com identidade; versionada (FR-3411, FR-3448);
  - versão de vigência futura nunca aplicada (FR-3404, EC-8);
  - unidade por `do_ato`, inclusive Publicação sem sigla gravada (EC-17, EC-18);
  - vagas saneadas e reserva por `TIPOS_COM_RESERVA` (FR-3406);
  - termos da lista em valor oficial, apontados e não alterados (EC-26);
  - e os EC-2 a EC-7, EC-11 a EC-13 e EC-19.
- [x] T006 [US1] Implementar a ficha em `processo_seletivo/portal/ficha.py` (`Ficha`, `Oferta`, `Origem`, `ler`, `diferencas`), só sobre as leituras da T002 e as da tabela "O que existe" (FR-3404, FR-3406 a FR-3411, FR-3448; D-002 a D-004, D-018). Nenhuma importação de `interface/` além de `vagas_do_conteudo`
- [x] T007 [P] [US1] **Teste primeiro**: os textos, em `tests/unit/kit/test_textos.py`:
  - formas por modo (FR-3412, FR-3413);
  - datas absolutas com "horário de Brasília" (FR-3415);
  - neutro sem "inscri" nas frases (FR-3416);
  - prorrogação com as duas pontas e com a hora quando a data coincide (FR-3417, EC-25);
  - legenda com caminho curto e busca com a sigla, e mensagem com link (FR-3418, EC-24);
  - ressalva (FR-3419);
  - notas sem promessa de validade (FR-3421);
  - "em N localidades" só com localidade em todas (FR-3409);
  - total sempre como "N vagas em K opções" (FR-3425);
  - teto de quatro na legenda (FR-3425, EC-23);
  - e os EC-5, EC-6 e EC-12.
- [x] T008 [US1] Implementar `processo_seletivo/interface/kit_textos.py`: formas fechadas nomeadas, Markdown e texto simples (FR-3412 a FR-3421)
- [x] T009 [P] [US1] **Teste primeiro**: a varredura de vocabulário em `tests/test_vocabulario_do_kit.py`, sobre o material gerado em todos os cenários. Ela reprova frase fixa, composição e manchete; valor literal só é apontado. Usa a lista da FR-3414 e a `PROIBIDAS` do portal (FR-3414, FR-3416; D-017)
- [x] T010 [P] [US5] **Teste primeiro**: autorização em `tests/authorization/test_kit_de_divulgacao.py`:
  - sem a capacidade, recusa explicada;
  - outra unidade, 404;
  - inexistente, 404;
  - não publicado, 409 (EC-1);
  - a capacidade não abre ato nenhum, testado por ato;
  - a tela não mostra nada de Retificação em elaboração (FR-3402 a FR-3405).
- [x] T011 [US1] Tela GET em `processo_seletivo/interface/kit_de_divulgacao.py`:
  - porta na ordem do contrato (FR-3402);
  - a rota em `processo_seletivo/interface/urls.py`;
  - a ação em `processo_seletivo/interface/acoes.py`, decidida só pelo estado, só no detalhe (FR-3401);
  - o host local tratado pela `_host_local` (FR-3447, EC-28);
  - as linhas no `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`;
  - o módulo em `MODULOS_DE_VIEW` de `tests/test_gramatica_das_portas.py`.
- [x] T012 [US1] Template `processo_seletivo/interface/templates/interface/kit_de_divulgacao.html`, com a folha `processo_seletivo/interface/static/interface/telas/kit-de-divulgacao.css` e o script `processo_seletivo/interface/static/interface/kit-de-divulgacao.js`:
  - conferência com proveniência e os termos apontados;
  - textos com "Copiar";
  - as faixas da FR-3443;
  - a impressão conferida no formulário (FR-3446);
  - cópia por teclado com `aria-live` (FR-3420, FR-3444; D-015);
  - teste do script em `tests/javascript/kit-de-divulgacao.test.js`.
- [x] T013 [P] [US1] Testes da tela em `tests/interface/test_kit_de_divulgacao.py`:
  - ação visível só com a capacidade, e indisponível com motivo antes da publicação (FR-3401);
  - os três modos na tela (FR-3443);
  - resposta privada;
  - nenhum estilo ou script embutido (FR-3444);
  - exportações por formulário sem script (EC-22);
  - host local sem link (FR-3447).

**Checkpoint**: o incremento A já é útil para copiar textos.

---

## Phase 4: User Story 3 — Exportação e desatualização (P1)

- [x] T014 [P] [US3] **Teste primeiro**: a exportação, em `tests/integration/kit/test_exportacao.py`:
  - md e txt registram `EXPORTAR_MATERIAL` com o `detalhe` do data-model, `previous_state` igual ao atual e o rótulo legível (FR-3435, FR-3436);
  - abrir e copiar não registram;
  - o kit não grava nada além do evento (FR-3405);
  - prorrogação depois da exportação gera a faixa "de → para" (FR-3439);
  - duas exportações, antes e depois da Retificação: a primeira continua listada;
  - Retificação só de seção não gera faixa (EC-9);
  - Perfil retirado, acrescentado, renomeado e reordenado (EC-10);
  - Retificação a vigorar anunciada antes e acusada depois da vigência (FR-3440, EC-8);
  - desfecho depois da exportação gera "não deve mais circular" (FR-3445);
  - impressão de versão anterior (FR-3448);
  - Edital mudado entre a tela e a exportação gera 409 (FR-3446, EC-27);
  - sem exportação anterior, sem faixa (EC-20).
- [x] T015 [US3] Exportação md/txt em `processo_seletivo/interface/kit_de_divulgacao.py`:
  - POST, anexo, `nosniff`;
  - conferência da impressão;
  - `record_event`;
  - leitura das exportações pela consulta do data-model;
  - faixas de desatualização e de desfecho;
  - o rótulo em `OPERACOES` (`processo_seletivo/interface/views.py`) e a operação em `OPERACOES_QUE_NAO_CONTAM` (`processo_seletivo/interface/relatorio_trilha.py`).

  Cobre FR-3435, FR-3436, FR-3439 a FR-3442 e FR-3445 a FR-3448.
- [x] T016 [P] [US3] Estender `tests/test_trilha_legivel.py` para varrer também `processo_seletivo/interface/*.py` (D-005)

**Feito em 01/11/2026** (commit do incremento A): suíte completa contra PostgreSQL com 14392 passando e 15 pulados antes do ajuste do README; recorte do kit e dos guardiões tocados, 1682 passando; verificação pelo navegador como Comunicação no 91/2026 do corpus (conferência, cópia anunciada, faixa de desatualização, 375 px sem rolagem horizontal, console sem erro). **Ficaram fora do A, registrados**: na T003, os cenários de caractere sem grafia e de mesmo número em duas unidades (são da peça e da legenda com sigla, que já tem teste unitário); na T005, os casos de Perfil ou Evento substituído inteiro e de Perfil acrescentado, porque a ficha usa `origens()` e `contexto()` da `070` sem mudança, e a regra é testada lá (`tests/unit/duvidas/test_origem.py`, `test_casos_da_revisao.py`); e o EC-4 (P-8), que não se constrói mais pela interface desde a decisão de 28/09 sobre o RC-118 — o ramo do código existe e espera a resposta da P-8.

**Checkpoint A**: `make lint check test-pg` verde. Demonstração do [quickstart](quickstart.md) §A pela interface. PR do incremento A.

---

## Phase 5: User Story 2 — A peça (P1)

- [ ] T017 [P] [US2] Chave `KIT_DE_DIVULGACAO_PECA` em `config/settings/base.py` (desligada), `development.py` e `test.py` (ligada). Produção não a recusa. Teste em `tests/test_settings_do_kit.py` (FR-3432, EC-21; D-010)
- [ ] T018 [P] [US2] Pasta `processo_seletivo/interface/kit_ativos/` com o marcador declarado ("marcador — não é ativo oficial") e um `ORIGEM.md` que diz a pendência P-3 (FR-3432)
- [ ] T019 [P] [US2] Apelido público de `_quebrar` em `processo_seletivo/publicacoes/infrastructure/pdf.py`, sem renomear. As fixtures de contrato do PDF continuam verdes (D-009)
- [ ] T020 [P] [US2] **Teste primeiro**: a geometria e a composição, em `tests/unit/kit/test_peca.py`:
  - **geometria**: nenhuma caixa fora da área útil, nenhuma sobreposição, nenhuma palavra partida, corpo mínimo de 24 px, margem de 80 px; nos cenários e nos sintéticos da D-016 (FR-3428, FR-3429);
  - **coerência**: peça ⊂ ficha e peça ⊂ textos (FR-3423);
  - **título**: ordem dos títulos e nenhum truncamento (FR-3426, EC-13, EC-14);
  - **oferta**: teto de quatro, contagem, "N vagas em K opções" (FR-3425, EC-11, EC-12, EC-23);
  - **período e neutro** (FR-3424);
  - **caractere sem grafia** e texto desenhado igual ao medido (FR-3430, EC-15);
  - **endereço longo** (FR-3431, EC-16);
  - **texto alternativo** (FR-3433);
  - **espaço livre**: corpo desce 35% da folga (FR-3434).
- [ ] T021 [P] [US2] **Teste primeiro**: a manchete, em `tests/unit/kit/test_manchete.py`. A lista fechada é oferecida só quando nenhum título cabe, filtrada pela FR-3414; índice inválido gera 422 (FR-3427; D-013)
- [ ] T022 [P] [US2] **Teste primeiro**: o SVG exportado, em `tests/unit/kit/test_svg.py`. Fonte embutida, política do anexo e `nosniff`; aberto num navegador com a política, desenha com a Edital Sans (FR-3422, FR-3442; D-021)
- [ ] T023 [US2] Implementar `processo_seletivo/interface/kit_peca.py`:
  - modelo de caixas com `data-campo` (D-008);
  - serialização SVG com escape por nó e texto normalizado (D-009), com a fonte embutida (D-021);
  - as regras de título, manchete, período, oferta, rodapé, legibilidade, recusa, espaço livre e texto alternativo (FR-3422 a FR-3431, FR-3433, FR-3434).
- [ ] T024 [US2] Verificação do motor (D-007), registrada em `specs/111-kit-de-divulgacao/verificacao-do-motor.md`:
  - licença do `resvg-py` e das transitivas;
  - wheel e execução na imagem Linux de implantação;
  - fontes e caracteres dos cenários;
  - nenhum recurso externo;
  - mesmo PNG em duas execuções;
  - lote de 20.

  **Aprovado pelo usuário (P-4)**, fixar a versão em `pyproject.toml` e `uv.lock`. Reprovado, seguir a alternativa da D-007.
- [ ] T025 [US2] Prévia e exportação da peça em `processo_seletivo/interface/kit_de_divulgacao.py`:
  - GET `previa.png` com a impressão conferida, sem registro (D-014, FR-3446);
  - POST `exportar/png` e `exportar/svg` com os cabeçalhos do contrato (FR-3442);
  - o rasterizador em `processo_seletivo/interface/kit_pacote.py`;
  - testes em `tests/interface/test_kit_de_divulgacao.py`: cabeçalhos, chave desligada, recusa, host local.
- [ ] T026 [P] [US2] SVG de referência dos cenários em `tests/fixtures/kit_referencias/*.svg`, com um teste de igualdade em `tests/integration/kit/test_referencias.py`. Mudar o template muda o arquivo, e o diff é revisado (D-016)
- [ ] T027 [US2] Estender a varredura da T009 aos textos de cada nó da peça e às manchetes (FR-3414, FR-3416)

**Checkpoint B**: `make test-pg` verde; a peça ligada em desenvolvimento, com o marcador. PR do incremento B.

---

## Phase 6: User Story 4 — O pacote (P2)

- [ ] T028 [P] [US4] **Teste primeiro**: o pacote, em `tests/integration/kit/test_pacote.py`:
  - a mesma peça e os mesmos textos publicáveis em dois instantes diferentes;
  - o mesmo ZIP no mesmo instante de referência (FR-3438);
  - manifesto com os três instantes e sem "validade" (FR-3437);
  - ZIP sem peça quando a chave está desligada, a peça foi recusada ou o host é local (EC-21);
  - nenhum arquivo guardado (FR-3441).
- [ ] T029 [US4] Manifesto e ZIP em `processo_seletivo/interface/kit_pacote.py` (data fixa, ordem fixa), e a exportação `zip` na view (FR-3435, FR-3437, FR-3438)
- [ ] T030 [P] [US4] Roteiro da galeria em `backend/scripts/galeria_do_kit.py` (como `scripts/publicar_corpus_do_piloto.py`): publica os cenários de referência num banco descartável e grava a galeria e o ZIP de cada um, para a revisão da comunicação (SC-1054; D-016)

**Checkpoint C**: `make test-pg` verde. PR do incremento C.

---

## Phase 7: Polish e validação

- [ ] T031 Verificação pelo navegador: tela a 1280 e a 375 px, texto a 200%, teclado e leitor de tela na cópia e nas faixas, com capturas anexadas ao PR (FR-3444)
- [ ] T032 Medir a tela com prévia e o ZIP num lote de 20 no ambiente de implantação, e registrar em `verificacao-do-motor.md` (SC-1057)
- [ ] T033 **Do usuário e da comunicação**: fornecer os ativos oficiais e o manual (P-3). Em seguida, aplicá-los em `processo_seletivo/interface/kit_ativos/` com o `ORIGEM.md`, e atualizar os SVG de referência e a galeria
- [ ] T034 **Da comunicação**: aprovar o template sobre a galeria com a marca aplicada (SC-1054). Depois, a operação liga a chave em produção (P-6)
- [ ] T035 **Da comunicação**: conferir um Edital real montado pela interface (SC-1051, SC-1058)
- [ ] T036 Conferir a [matriz](rastreabilidade.md) contra o implementado; `make lint check test-pg`

---

## Dependencies & Execution Order

| Tarefa | Depende de |
|---|---|
| T002, T003, T004 | T001 |
| Phase 3 | Phase 2 (T002 antes de T006) |
| T006 | T005 |
| T008 | T006, T007 |
| T011 | T006, T008, T004, T010 |
| T012 | T011 |
| T015 | T011, T014 |
| Phase 5 | Checkpoint A |
| T023 | T019, T020, T021, T022 |
| T025 | T023, T024 |
| T026, T027 | T023 |
| Phase 6 | Checkpoint B (o ZIP sem peça só depende do A) |
| T034 | T033 |
| T035 | Checkpoint C |

**Paralelo, dentro de cada fase**: as tarefas marcadas [P] tocam arquivos diferentes. Duas suítes ao
mesmo tempo precisam de `DB_NAME` próprio.
