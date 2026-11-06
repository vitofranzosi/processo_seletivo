# Tasks: A convocação segue o canal

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [contracts/](contracts/)

Os três incrementos saem num PR só, por decisão do usuário em 06/11/2026. A ordem é a do plano: A → B →
C. `[P]` marca tarefa sem dependência de arquivo com a anterior.

## Fase 1 — Incremento A: visibilidade (US1, FR-3981 a FR-3990)

- [x] T001 `visiveis_ao_candidato`, `visivel_ao_candidato`, `forma_do_perfil` e
  `ha_convocacao_visivel_no_recorte` em `convocacao/application/selectors.py` (R-001, R-002, R-003);
  `comunicar.forma_declarada` passa a ler de `forma_do_perfil`
- [x] T002 `vigentes_por_inscricao` escolhe a vigente mais recente entre as visíveis (FR-1100 da `059`)
- [x] T003 `chamada_em_aberto` só devolve a visível (FR-3986, D-003, R-004)
- [x] T004 Tela da convocação: *houve convocação* só com visíveis (FR-3984); sem leitura na trilha
  (FR-3983)
- [x] T005 Envio de documento e arquivo apresentado recusam com `nao_encontrado()` (FR-3985, R-005)
- [x] T006 [P] Testes de seletor: forma × comunicação, cadeia de três, forma trocada, forma não
  declarada, desfecho antes da publicação (D-002)
- [x] T007 [P] Testes de view nas sete superfícies, em K-pub, K-msg e depois do registro (SC-1201 a
  SC-1203), e o recorte só de invisíveis
- [x] T008 [P] Contagem de consultas da lista e do acompanhamento com K-pub (SC-1204)
- [x] T009 Testes existentes que prendiam a redação ou o desenho antigo, revistos citando a `125`
  (nenhum dependia de ver a convocação em K-pub)

## Fase 2 — Incremento B: aviso e prévia (US2, FR-3991 a FR-3997)

- [x] T010 Aviso *"Este texto será mostrado ao candidato."* nos sete campos, ligado por
  `aria-describedby`; rótulo *"O candidato lerá este fundamento"* no derivado (FR-3991, FR-3992)
- [x] T011 `_conferir_o_texto.html`, só com classes que a folha da gestão já tem (FR-3993 a FR-3995)
- [x] T012 Etapa de conferência nos seis POSTs da condução, com o texto composto pela mesma função do
  ato, o número do alcance e o resumo do texto (R-006, FR-3996)
- [x] T013 O complemento composto na prévia da correção da `120` (FR-3997)
- [x] T014 [P] Testes: aviso, passo com e sem texto, número no lote, alcance mudado, texto
  divergente, volta preservada, texto do portal igual ao da prévia (SC-1205 a SC-1207)

## Fase 3 — Incremento C: vocabulário (US3, FR-3998 a FR-4004)

- [x] T015 `convocacao/domain/vocabulario_do_canal.py` (R-007)
- [x] T016 Portal: `comunicacao_de`, os três templates, `PRAZO_NAO_INICIADO` por canal e
  `linha_da_substituida` (D-005, D-006, D-008)
- [x] T017 Gestão: `convocacao.html`, `_resultado_da_comunicacao.html`,
  `_vencimento_da_convocacao.html`, `_correcao_da_convocacao.html`, `convocacao_historico.html`
  (FR-4000, D-007)
- [x] T018 Recusas e texto da trilha por canal (FR-4001, R-008)
- [x] T019 [P] Varredura nas duas formas (FR-4004, SC-1208); testes que prendiam a redação antiga

## Fase 4 — Fechamento

- [x] T020 `rastreabilidade.md`: uma linha por `FR-`, `SC-` e caso-limite
- [x] T021 Verificação no navegador, sem nome real (`verificacao.md`); as capturas ficaram na sessão,
  e não no repositório
- [x] T022 `make lint check test-pg`; README com o estado da implementação
