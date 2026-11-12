# Tasks: Publicação e homologação das inscrições

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md)

Formato: `[ID] [P?] [História] Descrição`. `[P]` = arquivos distintos, sem dependência pendente.

## Fase A — O ato (US1, US5, base de US2 e US3)

- [X] T001 [US1] Modelos `PublicacaoDasInscricoes` e `InscricaoNaPublicacao` em `divulgacao/models.py`, com constraints de raiz, sucessor, natureza × Etapa, recurso, quantidade, e `save`/`delete` recusando alteração (FR-5406, FR-5425)
- [X] T002 [US1] Migration `divulgacao/0005` com gatilhos append-only e de coerência do sucessor; atualizar o guardião de contagem em `tests/migrations/test_migrations.py` (FR-5425, FR-5437)
- [X] T003 [US1] Acrescentar as duas tabelas a `TABELAS_APPEND_ONLY` e a contagem de `tests/seguranca/test_homologacao_preservada.py`; total no `CLAUDE.md` (FR-5425)
- [X] T004 [P] [US1] Projeção pura em `divulgacao/domain/inscricoes.py`: universo, situação por resultado vigente, ordem, agrupamento por Perfil, conteúdo público mínimo, divergência (FR-5404, FR-5410, FR-5419 a FR-5422, FR-5427)
- [X] T005 [P] [US1] Testes de unidade da projeção em `tests/unit/divulgacao/test_projecao_das_inscricoes.py`: ordem sem acento, contagem de indeferidas, nenhum dado pessoal além de nome e protocolo, divergência (SC-1702)
- [X] T006 [US1] Comando em `divulgacao/application/inscricoes.py`: `aferir`, `prever`, `assinatura_da_previa`, `publicar_das_inscricoes`, com permissão, trava, idempotência, recusas nomeadas, autoridade, bytes, linhas, PDF e trilha (FR-5400 a FR-5414, FR-5418, FR-5423, FR-5424, FR-5426, FR-5429 a FR-5431)
- [X] T007 [US1] PDF em `divulgacao/infrastructure/documento_das_inscricoes.py` pelo compositor de `pdf.py`, determinístico (FR-5424)
- [X] T008 [US1] Testes de integração em `tests/integration/divulgacao/test_publicacao_das_inscricoes.py`: recebidas, período em curso, Edital vazio, regressão, correção sem motivo, idempotência, prévia obsoleta, append-only no banco, homologação sem análise permitida e recusada (US1, US5, SC-1703, SC-1707)

## Fase B — Análise, recurso e homologação (US2, US3, US4)

- [X] T009 [US2] `resultados_visiveis` autoriza a Etapa do ato vigente da cadeia das inscrições (FR-5415)
- [X] T010 [US2] `_janelas_pertinentes` acrescenta a janela (ou a negativa) do preliminar para resultado da Etapa de análise (FR-5417)
- [X] T011 [US3] `recursos_pendentes_da_etapa` em `recursos/application/selectors.py` e uso na aferição da homologação (FR-5418)
- [X] T012 [US2] [US3] Jornada de ponta a ponta em `tests/integration/divulgacao/test_jornada_das_inscricoes.py`: preliminar → candidato vê motivo → recurso → correção → homologação recusada com recurso pendente → aceita depois → preliminar intacto byte a byte → divergência e sucessor (SC-1704, SC-1705, US4)
- [X] T013 [P] [US3] Teste da mesma fonte com o sorteio: o habilitado da relação pela Etapa de análise é o homologado (SC-1706, FR-5438)
- [X] T014 [P] Teste de compatibilidade: Edital só com Etapa pontuada atravessa consolidação e divulgação sem o ato; inscrição enviada continua imutável depois do ato (FR-5401, FR-5437, SC-1701)

## Fase C — Telas (US1 a US5)

- [X] T015 [US1] Tela da gestão "Publicações das inscrições": view, rota, template, folha; link na tela de Inscrições (FR-5432, FR-5433, UX-460 a UX-462, UX-465)
- [X] T016 [US1] Portal: página pública e PDF do ato, lista dos atos na página da seleção (FR-5428, UX-464)
- [X] T017 [US2] Bloco de situação do candidato: degraus recebida, deferida, indeferida, homologada, não homologada, com data e caminho ao ato (FR-5434 a FR-5436, UX-463)
- [X] T018 Testes de view e autorização: 403 sem capacidade, 404 fora do escopo, auditoria consulta e não publica, PRG, recusa com status; portal público sem conta; vocabulário da situação; CSP e classes com regra (FR-5429, SC-1708)

## Fase D — Validação e entrega

- [X] T019 Validação no navegador com telas reais nos sete cenários do pedido; capturas e roteiro em `verificacao.md` (SC-1700)
- [X] T020 [P] `quickstart.md` (operação mínima), `rastreabilidade.md`, linha no README, Visão do Sistema se aplicável
- [ ] T021 `make lint check test-pg`; PR

## Fase E — Revisão de 12/11/2026: a relação por lista de concorrência (D-011)

- [X] T022 Revisar a spec: D-009, FR-5419 a FR-5421, SC-1702 e o caso-limite do cotista, com a redação anterior preservada; D-011 com a evidência dos Editais do Ifes; P-2 respondida; FR-5439 a FR-5447, UX-466, UX-467, SC-1709 a SC-1711
- [X] T023 Projeção por lista em `divulgacao/domain/inscricoes.py` (`projetar` com `listas`, `grupos_publicados`, `tem_lista_reservada`, `FRASE_DAS_LISTAS`) e as listas pelos recortes em `application/inscricoes.py` (FR-5439 a FR-5444)
- [X] T024 [P] Documento, página pública e prévia da gestão por lista, lendo os dois formatos dos bytes (FR-5445 a FR-5447, UX-466)
- [X] T025 [P] Testes de unidade (listas, ordem, apontada, indeferida por lista, formato anterior, PDF) e de integração com Edital de PcD, PPI e a Modalidade apontada como a ampla (SC-1709 a SC-1711)
- [X] T026 Verificação no navegador e no PDF (`verificacao.md`, capturas 12 a 14); `rastreabilidade.md`, `research.md`, `data-model.md`
- [X] T026a A assinatura da prévia cita a versão: as listas saem dela (FR-5430)
- [X] T026b Desenho da revisão no `plan.md` (Fase E); `/speckit-analyze` com as correções I1 a I4 e B1 — FR-5430 revista, FR-5432 e US1/AC1 remetidas à FR-5445, UX-466, Status, `quickstart.md` e README —; `/speckit-converge` sem lacuna
- [X] T027 `make lint check test-pg`; PR — suíte verde em 12/11 (19155 passed, 24 skipped); PR #507
