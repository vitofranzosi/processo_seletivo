# Tasks: Prevenção de erro nos atos irreversíveis da convocação

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md), [quickstart.md](quickstart.md)

**Testes**: pedidos pela spec. Cada critério de sucesso tem caso automatizado, e a Constituição (V)
exige a rastreabilidade. Os caminhos são relativos à raiz do repositório.

**Convenções do repositório que estas tarefas pressupõem**:

- Lint é `ruff check` **e** `ruff format --check`.
- Toda classe citada num template precisa de regra na folha.
- Folha sem `}}` nem `%}`.
- Sem `style=`, `<style>`, `<script>` nem `onclick=` no template.
- Um `DB_NAME` próprio por worktree.

## Phase 1: Setup

- [ ] T001 Preparar a worktree: `uv sync --extra dev`, `.env` copiado do exemplo, `DB_NAME` próprio, e `make test-pg` verde na `main` antes de qualquer mudança. Ver o CLAUDE.md, *Subir o ambiente*.

## Phase 2: Foundational (bloqueia as histórias 2 e 5)

- [ ] T002 [P] Criar `backend/processo_seletivo/convocacao/domain/desfechos_cabiveis.py` com os predicados puros da R-005.
  - Um predicado por guarda: compatibilidade com a espécie da chamada (`DESFECHOS_POR_ESPECIE`), não atendimento prematuro (mesma regra de `prazo.decorrido` e do canal), inércia sem ocupação, inércia sem atestado e inclusão com obrigatório por conferir.
  - Cada um devolve `None` ou `(codigo, frase, a_partir_de)`, com as frases **literais** que `desfechar.py` usa hoje.
  - Mais `cabiveis(...)`, que devolve `(cabem, ainda_nao)` na ordem de `ESPECIES_DE_DESFECHO` (FR-5835 a FR-5837, FR-5839).
  - Mais `exige_ciencia_do_prazo(...)` (R-002) e `admite_inercia(especie_da_chamada)`.
- [ ] T003 [P] Testes de domínio em `backend/tests/unit/convocacao/test_desfechos_cabiveis.py`, sem banco.
  - A tabela espécie da chamada × prazo (sem envio, em curso, sem vencimento, decorrido) × atestado × ocupação × pendências.
  - As frases iguais às das recusas.
  - `exige_ciencia_do_prazo` nos casos da R-002.
- [ ] T004 Fazer as guardas de `backend/processo_seletivo/convocacao/application/desfechar.py` levantarem `DomainError` a partir dos predicados da T002, sem mudar ordem, código, HTTP nem frase.
  - Rodar `backend/tests/integration/convocacao/` e o inventário de recusas antes de seguir.
  - Depende de T002.
- [ ] T005 [P] Acrescentar `CIENCIA_DO_PRAZO_EM_CURSO = "ciencia_do_prazo_em_curso"` em `backend/processo_seletivo/convocacao/domain/nomes.py`, com o comentário do porquê (D-003).

## Phase 3: User Story 1 — o atalho só onde há pendência (P1) 🎯 MVP

**Goal**: o atalho aparece só com pendência registrada, ou com obrigatório não apresentado depois do vencimento por quem apresentou algo. Com nada apresentado e o prazo vencido, o cartão aponta o não atendimento.

**Independent Test**: C11 — Alice sem atalho; Bernardo com pendência e o atalho citando só o pendente; um convocado vencido sem envio com o passo apontando o não atendimento (quickstart §1).

- [ ] T006 [P] [US1] Em `backend/processo_seletivo/convocacao/application/documentos.py`, acrescentar as leituras do data-model, sem consulta nova (R-003, R-006):
  - `ItemLido.apresentado_pela_pessoa`: alguma apresentação **da chamada** com arquivo;
  - `LeituraDocumental.houve_apresentacao`;
  - `motivos_do_atalho(*, prazo_decorrido)`;
  - `aguardando_conferencia`;
  - `fundamento_do_atalho(*, prazo_decorrido)`.

  Conferir que as apresentações já vêm no `prefetch` de `leituras_por_chamada`.
- [ ] T007 [P] [US1] Em `backend/processo_seletivo/convocacao/domain/documentos.py`, criar `fundamento_do_atalho(pendentes, nao_apresentados)`, irmã de `fundamento_das_pendencias`. Ela cita o pendente com o motivo e o não apresentado com "não apresentado no prazo" (FR-5801).
- [ ] T008 [US1] Em `_documentos_por_linha` de `backend/processo_seletivo/interface/views.py`, levar a cada linha `motivos_do_atalho`, `fundamento_do_atalho` e `aguardando_conferencia`, com `prazo_decorrido` lido pela regra de `documentos.prazo_decorrido` da vigente.
  - Medir antes e depois o número de consultas da tela da convocação: não pode subir.
  - Depende de T006 e T007.
- [ ] T009 [US1] Em `backend/processo_seletivo/interface/templates/interface/convocacao.html`, condicionar o atalho a `linha.documentos.motivos_do_atalho` e pré-preencher com `fundamento_do_atalho` (FR-5800, FR-5801).
  - Nos dois formulários de indeferimento, a frase dos aguardando conferência (FR-5802).
  - Atualizar o comentário do template, que diz "só aparece onde há pendência".
- [ ] T010 [US1] Em `backend/processo_seletivo/interface/conducao_da_convocacao.py`, o passo `VENCIDA` ganha a frase e o caminho da FR-5809 e do UX-535 quando a chamada pede documento e `houve_apresentacao` é falso. O código continua `VENCIDA`, para não mudar a precedência dos passos da `143`.
- [ ] T011 [US1] Testes em `backend/tests/interface/test_indeferimento_pelas_pendencias.py`: os seis cenários de aceitação da história 1, o caso do só facultativo apresentado e o do aproveitado da inscrição que não conta (D-011). Cobre SC-1900 e SC-1910.

## Phase 4: User Story 2 — indeferir no prazo pede ciência (P1)

**Goal**: com o prazo em curso e obrigatório não atendido, o indeferimento — atalho ou desfecho geral — mostra o vencimento e exige a marca, conferida pelo comando e registrada na trilha.

**Independent Test**: quickstart §1, passos 2 e 3.

- [ ] T012 [US2] Em `backend/processo_seletivo/convocacao/application/desfechar.py`:
  - `desfechar(..., ciencia_do_prazo=False)`;
  - guarda `_recusar_indeferimento_sem_ciencia`, logo depois de `_recusar_inercia_sem_ocupacao`, pelo predicado `exige_ciencia_do_prazo`. Recusa 422 com `CIENCIA_DO_PRAZO_EM_CURSO`, campo `ciencia_do_prazo` (FR-5805);
  - em `auditar_desfecho`, a frase da ciência no `reason` e `detalhe={"cienciaDoPrazo": {...}}` (FR-5806, R-001).

  A leitura documental e o envio são lidos sob a trava que a inclusão já usa. Depende de T002, T004 e T005.
- [ ] T013 [US2] Em `desfechar_view` (`backend/processo_seletivo/interface/views.py`):
  - levar `ciencia_do_prazo=POST.get("ciencia_do_prazo") == "1"`;
  - na recusa, gravar `recusa_do_desfecho` na sessão (convocação, espécie, fundamento, atestado, ciência, frase), e a tela da convocação o consome ao renderizar, reabrindo o `<details>` da linha preenchido (FR-5805, R-009);
  - `_texto_do_desfecho` devolve a frase do prazo para a conferência do texto (FR-5807, R-010).
- [ ] T014 [US2] Em `convocacao.html`, o aviso do prazo e a marca de ciência, imediatamente antes do botão (UX-532):
  - no atalho, quando `linha.exige_ciencia_do_prazo`;
  - no desfecho geral, com "Exigida se o desfecho for indeferimento", sem script (contracts/telas.md);
  - sem vencimento, a frase da FR-5804.

  Em `_conferir_o_texto.html`, a frase do prazo acima do botão (FR-5807). Regras na folha `backend/processo_seletivo/interface/static/interface/telas/convocacao.css` para toda classe nova.
- [ ] T015 [US2] Testes, no mesmo arquivo da T011 ou em `backend/tests/integration/convocacao/test_ciencia_do_prazo.py`:
  - os cinco cenários da história 2;
  - os dois caminhos;
  - convocação sem vencimento e ainda não comunicada;
  - recusa sem gravar e com o fundamento devolvido;
  - a trilha com o `detalhe`;
  - a marca viajando pela conferência do texto.

  Cobre SC-1901.

## Phase 5: User Story 3 — conferir antes de chamar uma pessoa (P1)

**Goal**: "Chamar uma pessoa da fila" e "Chamar para regularizar" passam pela conferência da `140`, com uma pessoa.

**Independent Test**: quickstart §2, passos 1 e 2.

- [ ] T016 [US3] Em `backend/processo_seletivo/convocacao/application/fluxo.py`, extrair `verificar_chamada(...)` das recusas de `backend/processo_seletivo/convocacao/application/convocar.py`, na ordem de hoje (R-004):
  - marco, espécie, ordem vigente, apuração, convocação vigente;
  - ordem ou regularização com precedência;
  - déficit;
  - espécie derivada;
  - vencimento passado.

  Ela devolve espécie, posição, anteriores (`fila.precedencia`) e o vencimento com a origem. `convocar` a chama sob a trava. A correção (`120`) fica no ramo dela. Rodar a suíte da convocação: nenhuma frase muda.
- [ ] T017 [US3] Em `fluxo.py`, criar `conferencia_da_chamada(...)`, fora da trava e depois de `ensure_processo_accepts_changes`. Ela compõe:
  - o fundamento com o complemento;
  - a mensagem, por `comunicar.previa_das_mensagens` com uma inscrição, ou a frase da publicação;
  - o prazo, por `_prazo_da_conferencia`;
  - os anteriores, para "passa à frente de";
  - na regularização, o Resultado indeferido, lido como `desfechar._suceder_o_resultado`.

  Devolve `{"recusa"}` quando o comando recusaria. Também `gesto_ja_concluido(*, actor, chave, operation=GESTO_TITULARES)` (FR-5811 a FR-5815, FR-5817).
- [ ] T018 [US3] Em `convocar_view` (`backend/processo_seletivo/interface/views.py`), fora do ramo `corrige`, trocar `conferencia_do_texto.exigir` pelas cinco etapas de `convocar_titulares_view` (FR-5810, FR-5816, FR-5818 a FR-5821, FR-5823):
  1. autorização;
  2. `etapa=confirmar` com a chave de `convocacao:convocar` concluída vai ao comando;
  3. composição;
  4. página;
  5. resumo igual vai ao comando.

  O resumo cobre pessoa, espécie, fundamento, mensagem e prazo.
- [ ] T019 [US3] Em `backend/processo_seletivo/interface/templates/interface/convocacao_conferir.html`, o modo de uma pessoa (R-008):
  - "Será convocada";
  - "Passa à frente de";
  - o Resultado da regularização;
  - o form em `interface:convocar` com os campos ocultos da chamada;
  - o botão nomeando a pessoa ("Convocar Davi e enviar 1 mensagem") (UX-530, FR-5845).

  Regras novas em `backend/processo_seletivo/interface/static/interface/telas/convocacao-conferir.css`.
- [ ] T020 [US3] Em `convocacao.html`, os botões da chamada individual e da regularização dizem "Conferir antes de convocar", e as ajudas do complemento dizem que nada é praticado nem enviado antes da conferência (FR-5822).
- [ ] T021 [US3] Testes em `backend/tests/interface/test_conferencia_da_chamada.py`. Cobre SC-1902, SC-1903, SC-1907 e SC-1909.
  - **Sem efeito**: a prévia não cria convocação, mensagem, trilha, chave reservada nem sessão.
  - **Confirmação**: ela pratica; um duplo POST produz uma convocação e uma mensagem; texto mudado volta à conferência.
  - **Recusas**: pessoa já convocada; precedência sem marca, recusada antes do botão.
  - **Regularização**: a chamada para regularizar passa pela mesma conferência.
  - **Publicação e autorização**: o canal de publicação, e quem não emite continua recusado.
  - **Mensagem**: a mostrada é igual à enviada, exceto o link.
- [ ] T022 [US3] Ajustar os helpers que postam a chamada individual: `backend/tests/interface/test_convocacao_em_fluxo.py`, `backend/tests/interface/test_conferencia_do_texto.py` (os casos da `125` sobre a chamada individual passam a falar da conferência nova) e os demais que o `grep "interface:convocar\""` achar em `backend/tests/`.

## Phase 6: User Story 4 — conferir antes de emitir o corte (P2)

**Goal**: emissão, sucessão e faixa seguinte passam por "Confira antes de emitir o corte".

**Independent Test**: quickstart §2, passos 3 e 4.

- [ ] T023 [P] [US4] Em `backend/processo_seletivo/classificacao/application/emissao_do_corte.py`, criar `previa_da_continuacao(...)` com as recusas de `continuar_corte` fora da trava, devolvendo a proposta e a assinatura. `continuar_corte` passa a chamá-la e aceita `confirmacao_do_calculo=None`: quando vem, é conferida por `assinatura_da_proposta(proposta, geracao=vigente)` e recusa `calculo_divergente` (R-007, FR-5829, FR-5831). `causar_faixa_seguinte` não muda.
- [ ] T024 [US4] Em `emitir_corte_view` e `continuar_corte_view` (`backend/processo_seletivo/interface/views.py`), seguir o desenho de `emitir_ordenacao`: sem `confirmar=1`, responder `corte_confirmar.html` com:
  - a proposta e a assinatura recomposta;
  - `calculo_mudou`;
  - os avisos de espera e de reingresso (`_espera_do_corte`, `_reingressos_no_corte`);
  - o motivo.

  A recusa da prévia vai para a página só com a razão. Com `confirmar=1`, o comando de hoje (FR-5825 a FR-5833).
- [ ] T025 [US4] Criar `backend/processo_seletivo/interface/templates/interface/corte_confirmar.html`, a partir de `ordenacao_confirmar.html` e do quadro da faixa de `corte.html`:
  - o título "Confira antes de emitir o corte";
  - os números da faixa;
  - quem progride e quem fica fora, com causa;
  - o que acontece depois;
  - na sucessão, o motivo e "a geração vigente continua legível";
  - na faixa seguinte, as posições e as pessoas alcançadas;
  - "Cancelar e voltar" (FR-5826 a FR-5829, UX-531).

  Regras em `backend/processo_seletivo/interface/static/interface/telas/corte.css`.
- [ ] T026 [US4] Em `backend/processo_seletivo/interface/templates/interface/corte.html`, os botões "Conferir antes de emitir" e "Conferir a faixa seguinte". A faixa seguinte leva `confirmacao_do_calculo` só a partir da conferência.
- [ ] T027 [US4] Testes em `backend/tests/interface/test_conferencia_do_corte.py`. Cobre SC-1903 (corte e faixa) e SC-1904.
  - **Sem efeito**: a prévia não grava ato, trilha, chave nem sessão.
  - **Confirmação**: a emissão é praticada, e o duplo POST produz um ato só.
  - **Divergência**: o cálculo mudou entre a prévia e a confirmação.
  - **Sucessão e faixa seguinte**: a sucessão com motivo; a faixa seguinte com quantidade válida e com quantidade além do resto.
  - **Avisos e autorização**: os avisos se repetem, e a autorização é a de hoje.
- [ ] T028 [US4] Ajustar os helpers e casos que postam `emitir-corte` e `continuar-corte`: `backend/tests/integration/classificacao/test_faixa_seguinte.py`, `backend/tests/integration/classificacao/test_emissao_do_corte.py`, `backend/tests/interface/test_publicacao_de_convocados.py` e os que o `grep "emitir-corte\|continuar-corte"` achar.

## Phase 7: User Story 5 — o desfecho oferece o que cabe (P2)

**Goal**: o seletor lista só o que o comando aceitaria agora, e a nota diz o resto com a razão e a data.

**Independent Test**: quickstart §3, passo 1.

- [ ] T029 [US5] Em `backend/processo_seletivo/interface/views.py`, onde a tela monta as linhas (`leitura_do_recorte` e `_documentos_por_linha`), calcular `linha.desfechos = cabiveis(...)`.
  - Usar a ocupação de um `contexto_do_recorte` por recorte, os atestados, o envio, o vencimento e as pendências que a linha já tem.
  - Nenhuma consulta por linha (R-006). Medir o número de consultas da tela.
  - Depende de T002.
- [ ] T030 [US5] Em `convocacao.html`, gerar as opções do seletor de `linha.desfechos.cabem`, sem pré-escolha, e a nota "Ainda não cabem nesta chamada", uma linha por espécie (FR-5835 a FR-5839, UX-533).
  - Remover a nota antiga "Aceite e regularização são recusados enquanto faltar conferir", que passa a ser uma linha da nota nova.
  - Manter a lista de rótulos do seletor na varredura de vocabulário.
- [ ] T031 [US5] Testes. Cobre SC-1905 e SC-1906.
  - Em `backend/tests/interface/test_desfecho_cabivel.py`: os cinco cenários da história 5 e o C09 de Alice (4 opções, 2 na nota, "Regularização" ausente).
  - No mesmo arquivo, o oráculo da SC-1906: para cada combinação montada no banco, toda espécie oferecida passa pelas guardas do comando, e toda não oferecida é recusada.

## Phase 8: User Story 6 — o atestado só onde a inércia cabe (P3)

**Goal**: "Atestar fato externo" só nas chamadas para vaga.

**Independent Test**: quickstart §3, passo 2.

- [ ] T032 [US6] Levar `linha.admite_atestado = admite_inercia(especie)` e condicionar o `<details>` do atestado em `convocacao.html` a ele (FR-5840). Os rótulos dos fatos não mudam (FR-5841, D-010).
- [ ] T033 [US6] Testes: o gesto ausente na chamada para regularizar e presente nas duas outras, no mesmo arquivo da T031.

## Phase 9: Polish & Cross-Cutting

- [ ] T034 Criar `specs/152-prevencao-nos-atos-irreversiveis/rastreabilidade.md` com uma linha para todo identificador em negrito da spec: FR-5800 a FR-5809, FR-5810 a FR-5823, FR-5825 a FR-5833, FR-5835 a FR-5841, FR-5845, FR-5846, SC-1900 a SC-1910, UX-530 a UX-535, e os casos-limite.
  - Os números reservados e não usados da faixa ficam declarados como tal.
  - A FR-5846 (compatibilidade) se prova pela suíte existente verde.
- [ ] T035 Atualizar a linha da `152` no `README.md`: implementada, com o PR.
- [ ] T036 `cd backend && make lint check test-pg`, com `DB_NAME` próprio. Os pulados conferidos contra a medição do CLAUDE.md.
- [ ] T037 Verificação no navegador pelo [quickstart](quickstart.md), a 1440 e a 375 px, sem violação de CSP no console (SC-1908). Capturas no PR.
- [ ] T038 [P] Registrar em `specs/152-prevencao-nos-atos-irreversiveis/verificacao.md` os achados vistos na implementação, sem resolvê-los:
  - a faixa seguinte da ocupação, que emite num clique (R-007);
  - a inércia de quem aceitou, sem gesto na tela (spec, *Achados registrados*).
- [ ] T039 Atualizar `docs/visao-sistema/index.html`, se a seção da convocação descrever os gestos que mudaram.

## Dependencies & Execution Order

- **Setup (T001)** antes de tudo.
- **Foundational**:
  - T002, T003 e T005 são paralelas;
  - T004 depende de T002;
  - a fase bloqueia US2 (T012) e US5 (T029).
- **Histórias**:
  - **US1** depende só de T001; o MVP.
  - **US2** depende da Foundational e compartilha `convocacao.html` com US1. Faça US1 antes de US2, ou combine os dois templates numa tarefa só.
  - **US3** e **US4** são independentes de tudo o mais e entre si: a convocação e o corte, arquivos diferentes, exceto `views.py`.
  - **US5** depende da Foundational. **US6** depende de T002.
- **Polish** por último. T034 pode começar cedo e crescer com as fases.

`views.py` é tocado por US1, US2, US3, US4 e US5, em funções diferentes. Com mais de uma pessoa ou
sessão, trabalhe em branches e integre por merge, e não em paralelo na mesma árvore.

## Parallel Example

```text
# Foundational, juntas:
T002 desfechos_cabiveis.py   T003 test_desfechos_cabiveis.py   T005 nomes.py

# Depois da Foundational, em branches separadas:
US3 (T016–T022, convocação)   US4 (T023–T028, corte)
```

## Implementation Strategy

1. **MVP**: T001 e US1 (T006–T011). Isso tira o atalho de Alice, que é o achado de prioridade alta.
2. US2, sobre a Foundational: a ciência fecha o achado 04.
3. US3 e US4: o achado 08. Podem ir em PRs separados, um para a convocação e outro para o corte.
4. US5 e US6: o achado 12.
5. Polish e verificação no navegador.

Cada passo deixa a suíte verde e é mergeável sozinho.
