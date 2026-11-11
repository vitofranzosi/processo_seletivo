# Tasks: A publicação das convocações no GPS (149)

**Input**: [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md),
[plan.md](plan.md). Caminhos relativos a `backend/`.

## Fase 1 — O ato

- [x] T001 Modelos `PublicacaoDeConvocados`, `ConvocacaoPublicada`, `DocumentoDaPublicacaoDeConvocados` em `processo_seletivo/convocacao/models.py` (FR-5707, FR-5710)
- [x] T002 Migration `convocacao/0007` com gatilhos append-only e de coerência; as três em `TABELAS_APPEND_ONLY`; contagens do guardião de migrations (FR-5710)
- [x] T003 Domínio `convocacao/domain/publicacao.py`: efeito de cada linha, motivos de fora, composição do conteúdo, assinatura (FR-5702, FR-5704–FR-5706, FR-5708, FR-5712–FR-5717)
- [x] T004 `convocacao/application/publicar.py`: prévia do Edital por recortes, em consultas fixas (FR-5701, FR-5728, FR-5736)
- [x] T005 Comando `publicar_convocados`: trava, idempotência, assinatura, declaração, autoridade, número, comunicações, vínculos, documento, trilha (FR-5701–FR-5711)
- [x] T006 `convocacao/infrastructure/documento.py`: o PDF no compositor comum (FR-5710, FR-5713)
- [x] T007 Testes de integração do ato: os efeitos, o prazo, as recusas, a idempotência, a correção, a sucessão (SC-1851–SC-1858, SC-1864)
- [x] T008 Testes de imutabilidade contra PostgreSQL (FR-5707, FR-5710)

## Fase 2 — O público

- [x] T009 Leituras `convocacao/application/publicacoes.py`: da seleção, da página, do candidato (FR-5719–FR-5721, FR-5725)
- [x] T010 Portal: rotas `convocacoes/<id>/` e `documento.pdf`, página `convocados.html` (FR-5718–FR-5720, FR-5724)
- [x] T011 Seção *Convocações* na página da seleção (FR-5721–FR-5724)
- [x] T012 Área do candidato: *"Publicada em"* leva à publicação (FR-5725, FR-5726)
- [x] T013 Testes do portal: acesso sem sessão, privacidade, consistência, consultas fixas (SC-1859–SC-1862, SC-1865)

## Fase 3 — A gestão

- [x] T014 Página *Publicação das convocações* do Edital, GET com prévia e POST de confirmação (FR-5727–FR-5730, FR-5732)
- [x] T015 Tela do recorte: *"Publicar no GPS"*, a alternativa externa nomeada e o cartão da convocação publicada (FR-5731)
- [x] T016 Folhas de estilo da gestão e do portal; guardiões de classe, vocabulário e inventário de negativas
- [x] T017 Testes da gestão: porta, prévia sem gravação, confirmação, recusa (SC-1858, SC-1859, SC-1864)

## Fase 4 — Verificação

- [x] T018 Regressões: `emitir_pendentes`, visibilidade da `125`, avisos da `066` com a publicação nativa (FR-5733–FR-5735, SC-1861)
- [x] T019 Navegador real: capturas da gestão e do portal em 375, 1280 e 1920 px (SC-1863)
- [x] T020 `make lint check test-pg`; `CLAUDE.md` (o `M` do provisionamento); quickstart; PR
