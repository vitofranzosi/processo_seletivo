# Tasks: A publicação das convocações no GPS (148)

**Input**: [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md),
[plan.md](plan.md). Caminhos relativos a `backend/`.

## Fase 1 — O ato

- [x] T001 Modelos `PublicacaoDeConvocados`, `ConvocacaoPublicada`, `DocumentoDaPublicacaoDeConvocados` em `processo_seletivo/convocacao/models.py` (FR-5407, FR-5410)
- [x] T002 Migration `convocacao/0007` com gatilhos append-only e de coerência; as três em `TABELAS_APPEND_ONLY`; contagens do guardião de migrations (FR-5410)
- [x] T003 Domínio `convocacao/domain/publicacao.py`: efeito de cada linha, motivos de fora, composição do conteúdo, assinatura (FR-5402, FR-5404–FR-5406, FR-5408, FR-5412–FR-5417)
- [x] T004 `convocacao/application/publicar.py`: prévia do Edital por recortes, em consultas fixas (FR-5401, FR-5428, FR-5436)
- [x] T005 Comando `publicar_convocados`: trava, idempotência, assinatura, declaração, autoridade, número, comunicações, vínculos, documento, trilha (FR-5401–FR-5411)
- [x] T006 `convocacao/infrastructure/documento.py`: o PDF no compositor comum (FR-5410, FR-5413)
- [x] T007 Testes de integração do ato: os efeitos, o prazo, as recusas, a idempotência, a correção, a sucessão (SC-1701–SC-1708, SC-1714)
- [x] T008 Testes de imutabilidade contra PostgreSQL (FR-5407, FR-5410)

## Fase 2 — O público

- [x] T009 Leituras `convocacao/application/publicacoes.py`: da seleção, da página, do candidato (FR-5419–FR-5421, FR-5425)
- [x] T010 Portal: rotas `convocacoes/<id>/` e `documento.pdf`, página `convocados.html` (FR-5418–FR-5420, FR-5424)
- [x] T011 Seção *Convocações* na página da seleção (FR-5421–FR-5424)
- [x] T012 Área do candidato: *"Publicada em"* leva à publicação (FR-5425, FR-5426)
- [x] T013 Testes do portal: acesso sem sessão, privacidade, consistência, consultas fixas (SC-1709–SC-1712, SC-1715)

## Fase 3 — A gestão

- [x] T014 Página *Publicação das convocações* do Edital, GET com prévia e POST de confirmação (FR-5427–FR-5430, FR-5432)
- [x] T015 Tela do recorte: *"Publicar no GPS"*, a alternativa externa nomeada e o cartão da convocação publicada (FR-5431)
- [x] T016 Folhas de estilo da gestão e do portal; guardiões de classe, vocabulário e inventário de negativas
- [x] T017 Testes da gestão: porta, prévia sem gravação, confirmação, recusa (SC-1708, SC-1709, SC-1714)

## Fase 4 — Verificação

- [x] T018 Regressões: `emitir_pendentes`, visibilidade da `125`, avisos da `066` com a publicação nativa (FR-5433–FR-5435, SC-1711)
- [x] T019 Navegador real: capturas da gestão e do portal em 375, 1280 e 1920 px (SC-1713)
- [x] T020 `make lint check test-pg`; `CLAUDE.md` (o `M` do provisionamento); quickstart; PR
