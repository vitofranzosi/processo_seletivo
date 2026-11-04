---
description: "Tarefas da 119 — templates de divulgação por família e formato"
---

# Tasks: Templates de Divulgação por Família e Formato

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/kit.md](contracts/kit.md), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — teste geométrico, de vocabulário, de determinismo, de referência byte
a byte e de origem dos ativos (FR-3822, FR-3824, FR-3826, FR-3827, SC-1131–SC-1134, SC-1138). Cada
teste é escrito antes da implementação que ele cobre e falha primeiro.

**Organização**: por incremento (D-001), e dentro dele por história. Os caminhos são relativos à
raiz do repositório; `kit/` abrevia `backend/processo_seletivo/interface/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1–US5)

---

## Phase 1: Setup

**Purpose**: o lugar das peças novas, sem mudar comportamento.

- [ ] T001 Criar o pacote `backend/processo_seletivo/interface/kit_familias/__init__.py` com o registro vazio e o módulo `backend/processo_seletivo/interface/kit_formatos.py` com os três formatos da FR-3801 (data-model §Formato; D-007 para o banner)
- [ ] T002 [P] Criar `backend/processo_seletivo/interface/kit_ativos/fontes/ORIGEM.md` com o formato do registro de fonte (arquivo, família tipográfica, licença OFL, origem, resumo SHA-256), seguindo o `kit_ativos/ORIGEM.md` da `111` (FR-3823, FR-3826)
- [ ] T003 [P] Acrescentar `KIT_DE_DIVULGACAO_TEMPLATES` em `backend/config/settings/base.py` (lista vazia lida do ambiente), `development.py` e `test.py` (todos), e o caso correspondente em `backend/tests/test_settings_do_kit.py` (D-010, FR-3808)

---

## Phase 2: Foundational — Incremento 1: motor generalizado (US4) 🧱

**Goal**: formato, família e template como dados; a peça da `111` vira a Institucional sem mudar um
byte (FR-3801–FR-3804, FR-3823, FR-3827, SC-1133).

**Independent Test**: `uv run pytest tests/unit/kit tests/integration/kit/test_referencias.py` verde
**sem** regravar nada em `backend/tests/fixtures/kit_referencias/`.

**⚠️ CRITICAL**: nenhuma família nova antes desta fase fechar.

### Testes

- [ ] T004 [P] [US4] Em `backend/tests/unit/kit/test_formatos.py`: tamanho, margem, zonas reservadas, corpo mínimo e chamada à ação de cada formato (FR-3801, FR-3819)
- [ ] T005 [P] [US4] Em `backend/tests/unit/kit/test_familias.py`: toda família registrada declara os campos do data-model, toda caixa tem corpos ≥ mínimo do formato, só `contato` e `titulo` podem omitir, e todo ativo citado existe (FR-3802, FR-3803)
- [ ] T006 [P] [US4] Em `backend/tests/unit/kit/test_fontes_do_kit.py`: cada fonte do kit tem resumo igual ao do `ORIGEM.md`, cobre o repertório da `grafia`, e a recusa por caractere sem grafia nomeia caractere e fonte (FR-3823, EC-13)
- [ ] T007 [US4] Em `backend/tests/integration/kit/test_referencias.py`: o identificador do template da Institucional continua `feed-1080x1350 · 1` e os SVG de referência saem idênticos pelo motor generalizado (FR-3804, SC-1133)

### Implementação

- [ ] T008 [US4] Criar `backend/processo_seletivo/interface/kit_fontes.py`: métrica e subconjunto por fonte livre sobre o leitor TrueType de `publicacoes/infrastructure/fonte.py`, sem alterar este; a Edital Sans entra como a primeira fonte do kit (D-005)
- [ ] T009 [US4] Declarar as classes imutáveis `Familia`, `Variante`, `Imagem`, `Template`, `Caixa` e o registro com `familias_da_unidade(codigo)` e `liberados()` em `backend/processo_seletivo/interface/kit_familias/__init__.py` (data-model; FR-3805, FR-3808)
- [ ] T010 [US4] Criar `backend/processo_seletivo/interface/kit_familias/institucional.py` reproduzindo as constantes de `kit_peca.py` (cores, faixas, corpos, recaídas, marca, rodapé) como declaração (D-002, FR-3804)
- [ ] T011 [US4] Refatorar `backend/processo_seletivo/interface/kit_peca.py` para compor a partir de `(ficha, template, escolha)`: medida pela `kit_fontes`, caixas pela declaração, recusa por template, e serialização SVG com fontes, ativos, `clipPath` e imagens da família (D-004, D-006, FR-3803, FR-3824, FR-3827). `compor(ficha, manchete=...)` continua existindo para a Institucional
- [ ] T012 [US4] Fazer `backend/processo_seletivo/interface/kit_pacote.py` passar ao rasterizador as fontes da família do template, sem fontes do sistema (D-005)
- [ ] T013 [US4] Rodar a suíte do kit e conferir `git status backend/tests/fixtures/kit_referencias/` limpo; registrar o resultado no PR do incremento 1 (SC-1133)

**Checkpoint**: PR do incremento 1. A peça de produção não mudou.

---

## Phase 3: Incremento 2a — ficha versão 2 e textos (US2, P1)

**Goal**: carga horária e contato na ficha, nos textos, na conferência e na desatualização, sem
alarme falso (FR-3809–FR-3813, SC-1139).

**Independent Test**: os casos de US2 da spec, mais exportações versão 1 sem faixa.

### Testes

- [ ] T014 [P] [US2] Em `backend/tests/integration/kit/test_ficha.py`: carga horária literal, aparada, vazia em parte das ofertas (EC-2); contato do cadastro da unidade do ato, vazio sem substituto (FR-3809, FR-3810)
- [ ] T015 [P] [US2] Em `backend/tests/integration/kit/test_exportacao.py`: exportação v1 sem faixa depois da v2 (EC-14, SC-1139); atendimento alterado depois de exportação v2 acende "contato: antes → agora" (EC-15, FR-3811)
- [ ] T016 [P] [US2] Em `backend/tests/unit/kit/test_textos.py`: legenda e texto para mensagens com carga horária e contato quando declarados, e a conferência peça ⊂ textos cobrindo os dois (FR-3813)
- [ ] T017 [P] [US2] Em `backend/tests/interface/test_kit_de_divulgacao.py`: a conferência mostra a carga horária com o ato e o contato com a origem "cadastro da unidade" (FR-3812)

### Implementação

- [ ] T018 [US2] Em `backend/processo_seletivo/portal/ficha.py`: `Oferta.carga_horaria`, `Ficha.contato`, `_campos` versão 2, `impressao_v1`, `VERSAO_DA_IMPRESSAO = 2`, e a comparação por versão em `desatualizacoes` (D-009)
- [ ] T019 [US2] Em `backend/processo_seletivo/portal/ficha.py`: a origem da carga horária pela regra da proveniência, e a do contato como "cadastro da unidade" (FR-3812)
- [ ] T020 [US2] Em `backend/processo_seletivo/interface/kit_textos.py` e `kit_peca.py` (`fora_dos_textos`): carga horária e contato nos textos e na conferência automática (FR-3813)
- [ ] T021 [US2] Na tela `backend/processo_seletivo/interface/templates/interface/kit_de_divulgacao.html`: as linhas da conferência e os rótulos legíveis dos campos novos na faixa de desatualização

**Checkpoint**: a Institucional não muda de desenho; a desatualização já entende os campos novos.

---

## Phase 4: Incremento 2b — escolha em listas fechadas (US3, P1)

**Goal**: família, variante, imagem e formato escolhidos em listas fechadas, validados no servidor,
pré-escolhidos pela última exportação e registrados (FR-3805–FR-3808, FR-3828, FR-3830).

**Independent Test**: os cenários de US3 da spec e o envio forjado.

### Testes

- [ ] T022 [P] [US3] Em `backend/tests/authorization/test_kit_de_divulgacao.py`: família de outra unidade, variante, imagem ou formato fora da lista → 400 sem registro (EC-9); template não liberado → 409 sem registro (EC-7); Edital de unidade sem família → só a Institucional (EC-1)
- [ ] T023 [P] [US3] Em `backend/tests/interface/test_kit_de_divulgacao.py`: pré-escolha pela última exportação; imagem retirada do banco cai na primeira, com o motivo (EC-8); formulário funciona sem script (FR-3806, FR-3830)
- [ ] T024 [P] [US3] Em `backend/tests/integration/kit/test_exportacao.py`: o `detalhe` do evento leva família, versão, variante, formato da peça, template, versão e imagem com resumo; trocar de família não acende faixa (FR-3828)

### Implementação

- [ ] T025 [US3] Em `backend/processo_seletivo/interface/kit_de_divulgacao.py`: ler e validar a escolha (`familia`, `variante`, `imagem`, `formato_da_peca`, `manchete`) contra as listas do instante; pré-escolha pelo evento mais recente; recusa 400 com a frase do contrato (D-008, D-012, contracts/kit.md)
- [ ] T026 [US3] No mesmo arquivo: `previa` e `exportar` por `formato_da_peca`; o `detalhe` acrescido (FR-3828); motivo "em aprovação pela comunicação" para template não liberado (FR-3808)
- [ ] T027 [US3] Na tela `kit_de_divulgacao.html` e na folha da tela: o formulário de escolha (rádios nativos, imagem com a descrição aprovada), uma prévia por formato com o alternativo e os botões, e as faixas "o título oficial não coube em" e "o contato não coube em" (FR-3818, FR-3820, FR-3830); estilo só por arquivo (CSP), leitura a 375 px
- [ ] T028 [US3] Conferir `backend/tests/test_gramatica_das_portas.py`, que varre `kit_de_divulgacao.py`: todo `Http404` novo da prévia (escolha fora da lista, template não liberado) ganha linha no inventário da `033`; o 400 da exportação vai por `DomainError`, como as recusas da `111` (contracts/kit.md)

**Checkpoint**: a escolha funciona com a Institucional sozinha na lista.

---

## Phase 5: Incremento 2c — Pós Lato Sensu nos três formatos (US1, P1) 🎯 MVP

**Goal**: a primeira família da comunicação em post, story e banner (FR-3814–FR-3825, SC-1131,
SC-1132, SC-1134).

**Independent Test**: o Independent Test e os cenários de US1 da spec.

### Testes

- [ ] T029 [P] [US1] Em `backend/tests/unit/kit/geometria.py` e `test_peca.py`: a verificação por template — área útil, zonas reservadas do story, sobreposição entre textos e com imagem e ativos (D-011), corpo mínimo, palavra partida — sobre todos os cenários de referência da `111` e da spec 17–25 e os casos no limite (FR-3822, FR-3824, SC-1132, EC-3, EC-5, EC-6)
- [ ] T030 [P] [US1] Em `backend/tests/test_vocabulario_do_kit.py`: iterar sobre todas as famílias registradas e todas as frases fixas e variantes, com a lista da FR-3414 da `111` e os termos da FR-3814 (D-013, SC-1131)
- [ ] T031 [P] [US1] Em `backend/tests/unit/kit/test_peca.py`: período nas formas fechadas, com ano, hora e início (FR-3815, EC-10, EC-16, EC-17); número em todo formato (FR-3816); "Nome — carga horária" (FR-3817); título resolvido por formato e manchete só onde nenhum oficial cabe (FR-3818, EC-18); chamada à ação e busca por formato (FR-3819); contato omitido com aviso (FR-3820, EC-4); selo da versão em todo formato (FR-3821)
- [ ] T032 [P] [US1] Em `backend/tests/unit/kit/test_svg.py`: determinismo por template, variante, imagem e manchete (FR-3827, SC-1134); contraste AA pelas cores declaradas de cada caixa (FR-3822); alternativo por formato com a descrição da imagem (FR-3825)
- [ ] T033 [P] [US1] Em `backend/tests/unit/kit/test_ativos_do_kit.py`: todo ativo usado por família consta do `ORIGEM.md` dela, com licença e resumo conferido, e nenhuma imagem passa de 400 kB (FR-3826, SC-1138)
- [ ] T034 [P] [US1] Em `backend/tests/integration/kit/test_ficha.py` ou `test_exportacao.py`: modo sem material e host local não geram formato nenhum de família nenhuma (EC-11, EC-12)

### Implementação

- [ ] T035 [US1] Versionar os subconjuntos da Poppins em `backend/processo_seletivo/interface/kit_ativos/fontes/` com o registro no `ORIGEM.md` (FR-3823)
- [ ] T036 [US1] Versionar os ativos da família em `backend/processo_seletivo/interface/kit_ativos/pos-lato-sensu/` — padrão em chevron, balão, barras decorativas, rodapé — com `ORIGEM.md`; as imagens do banco só depois da P-1, reduzidas como na D-006 (FR-3807, FR-3826)
- [ ] T037 [US1] Declarar `backend/processo_seletivo/interface/kit_familias/pos_lato_sensu.py`: paleta, fontes, frases, unidade Cefor, banco e os três templates a partir dos arquivos `Editais Pós Lato Sensu - {Posts,Story,Site}` (FR-3802, FR-3803, FR-3814)
- [ ] T038 [US1] Gravar as referências em `backend/tests/fixtures/kit_referencias/pos-lato-sensu/{post,story,banner}/` e o caso que as compara em `backend/tests/integration/kit/test_referencias.py`
- [ ] T039 [US1] Em `backend/processo_seletivo/interface/kit_pacote.py`: o ZIP leva a peça de cada formato liberado da família, com o alternativo; o recusado vai no manifesto com o motivo (FR-3829; depende do incremento C da `111` mergeado)
- [ ] T040 [US1] Medir no ambiente de implantação a tela com três prévias e o ZIP num lote de 20, e registrar em `specs/119-templates-de-divulgacao/verificacao.md` (SC-1137)

**Checkpoint**: PR do incremento 2 (fases 3 a 6). US1–US3 verificáveis de ponta a ponta.

---

## Phase 6: Incremento 2d — galeria por template (US5, P2)

**Goal**: a comunicação aprova cada template sobre a galeria (FR-3831, SC-1135).

**Independent Test**: a galeria da Pós Lato Sensu mostra os três formatos em todos os cenários, com
recusa e motivo.

- [ ] T041 [US5] Em `backend/scripts/galeria_do_kit.py`: `--familia` e `--formato`; para cada template liberável, todos os cenários de referência (os 16 da `111` e os 17–25 desta spec) e os casos no limite, com a recusa e o motivo (FR-3831)
- [ ] T042 [US5] Publicar a galeria da Pós Lato Sensu para a comunicação e registrar a aprovação, ou os ajustes pedidos, em `specs/119-templates-de-divulgacao/verificacao.md` (SC-1135; validação humana)

---

## Phase 7: Incremento 3 — as demais famílias, uma por PR

Cada família segue o mesmo roteiro das T035–T038 e T042: fontes, ativos com origem, declaração,
referências, galeria e aprovação. Nenhuma toca o motor; se precisar, o ajuste do motor é tarefa
própria, com as referências das famílias anteriores intactas.

- [ ] T043 [US1] **3a — FIC**: Archivo Black, Barlow Semi Condensed, Space Mono; selo de prorrogação como faixa; bloco de contato (EC-4); três ofertas com carga horária (cenários 18, 19); `backend/processo_seletivo/interface/kit_familias/fic.py` e ativos em `kit_ativos/fic/`
- [ ] T044 [US1] **3b — Libras**: Unbounded e a substituta da Helvetica Neue (espera a P-2); recorte em círculo; `kit_familias/libras.py` e `kit_ativos/libras/`
- [ ] T045 [US1] **3c — UAB/bolsista**: Anton e Poppins; chamada fixa "Seleção de bolsista" aprovada; `kit_familias/uab.py` e `kit_ativos/uab/`
- [ ] T046 [US1] **3d — Aperfeiçoamento**: Unbounded, Lexend, Poppins; foto com clipe; `kit_familias/aperfeicoamento.py` e `kit_ativos/aperfeicoamento/`
- [ ] T047 [US1] **3e — Internos**: variantes `servidores` e `estudantes` (EC-19, cenário 23); recorte em losango; substituta da Helvetica Neue (P-2); `kit_familias/internos.py` e `kit_ativos/internos/`
- [ ] T048 [US1] **3f — TMD**: Archivo Black e a substituta da Helvetica Neue (P-2); ilustração plana sem banco de fotos (EC-20); `kit_familias/tmd.py` e `kit_ativos/tmd/`

---

## Phase 8: Polish & Cross-Cutting

- [ ] T049 [P] Atualizar a linha da `119` no `README.md` a cada incremento mergeado, e o `CLAUDE.md` se a suíte ganhar pulados ou a liberação ganhar armadilha
- [ ] T050 [P] Confirmar com `git diff` que nenhum arquivo do fluxo de publicação, de Retificação ou de `publicacoes/infrastructure/fonte.py` mudou, e que não há migration (FR-3832)
- [ ] T051 Rodar `cd backend && make lint check test-pg` antes de cada PR
- [ ] T052 Validação humana do SC-1136 com uma pessoa da comunicação, registrada em `verificacao.md`

---

## Dependencies & Execution Order

- **Setup (T001–T003)** → **Incremento 1 (T004–T013)** → tudo o mais.
- **Incremento 2**: a fase 3 (ficha) e a fase 4 (escolha) podem andar em paralelo; a fase 5 depende
  das duas; a T039 e a fase 6 dependem do incremento C da `111` na `main`.
- **Incremento 3**: cada família depende do incremento 2 e das suas pendências (P-1 para imagens;
  P-2 para Libras, Internos e TMD). As famílias são independentes entre si, mas seguem uma por PR, na
  ordem da Phase 7.
- **Liberação**: template a template, pela operação, depois da aprovação (SC-1135, P-4); banner
  depois da P-3.

### Parallel Opportunities

- T002 e T003; T004, T005 e T006.
- Os testes de cada fase marcados [P].
- Fase 3 e fase 4 inteiras, em worktrees separadas, sem tocar o mesmo arquivo de view.

### Parallel Example: fase 5

```text
T029 geometria por template    T030 vocabulário sobre o registro
T031 regras de composição      T032 determinismo e contraste
T033 origem dos ativos         T034 sem material e host local
```

## Cobertura

| Spec | Tarefas |
|---|---|
| FR-3801 | T001, T004 |
| FR-3802, FR-3803 | T005, T009, T037 |
| FR-3804 | T007, T010, T013 |
| FR-3805, FR-3806 | T022, T023, T025 |
| FR-3807 | T036, T027 |
| FR-3808 | T003, T022, T026 |
| FR-3809, FR-3810, FR-3811 | T014, T015, T018 |
| FR-3812 | T017, T019 |
| FR-3813 | T016, T020 |
| FR-3814 | T030, T037 |
| FR-3815–FR-3821 | T031 |
| FR-3822, FR-3824 | T029, T032 |
| FR-3823 | T006, T008, T035 |
| FR-3825, FR-3827 | T032 |
| FR-3826 | T033, T036 |
| FR-3828 | T024, T026 |
| FR-3829 | T039 |
| FR-3830 | T023, T027 |
| FR-3831 | T041 |
| FR-3832 | T050 |
| SC-1131 | T030 |
| SC-1132 | T029 |
| SC-1133 | T007, T013 |
| SC-1134 | T032 |
| SC-1135 | T042 |
| SC-1136 | T052 |
| SC-1137 | T040 |
| SC-1138 | T033 |
| SC-1139 | T015 |
| EC-1, EC-7, EC-9 | T022 |
| EC-2 | T014 |
| EC-3, EC-5, EC-6 | T029 |
| EC-4, EC-10, EC-16, EC-17, EC-18 | T031 |
| EC-8 | T023 |
| EC-11, EC-12 | T034 |
| EC-13 | T006 |
| EC-14, EC-15 | T015 |
| EC-19 | T047 |
| EC-20 | T048 |

## Implementation Strategy

1. **Incremento 1** isolado, num PR: a prova é a referência byte a byte.
2. **Incremento 2** num PR: ficha, escolha, Pós Lato Sensu e galeria. É o MVP: a comunicação já gera
   os três formatos de uma família, e a aprovação começa.
3. **Incremento 3**: uma família por PR, liberada na produção só depois da aprovação dela.
