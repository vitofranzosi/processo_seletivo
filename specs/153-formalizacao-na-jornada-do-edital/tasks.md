# Tasks: A formalização na jornada guiada do Edital (153)

**Input**: [spec.md](spec.md), [plan.md](plan.md)

- [x] T001 Ajustar a FR-6104 e a FR-6108 da spec ao que as respostas e o plano fixaram, e as revisões
  da tabela "Compatibilidade" nos arquivos de origem (FR-4716 da `136`, FR-4082 da `127`, FR-3534 da
  `113`, FR-4351 da `130`).
- [x] T002 `formalizacao/application/passagem.py`: `Passagem` e `da_passagem`, com testes de
  integração da classificação (FR-6100 a FR-6107, FR-6130; SC-1951).
- [x] T003 `interface/andamento.py`: a natureza, os papéis, `_providencias_da_formalizacao` e
  `Andamento.formalizacao` (FR-6108 a FR-6114, FR-6116, FR-6117).
- [x] T004 `interface/centro.py`: a fase da natureza nova (FR-6115) e o bloco da Conclusão, com o
  template e a folha (FR-6118 a FR-6123; UX-560 a UX-563).
- [x] T005 Relatório: o tipo em `pendencias_do_edital.py`, `Pendencia.detalhe`, `fatos_do_edital`,
  `texto_da_pendencia`, `redigir_pendencias` e o consolidado (FR-6127).
- [x] T006 Encerramento: `DA_099`, o `Item` com o caminho e a frase (FR-6124 a FR-6126, FR-6128).
- [x] T007 Testes de tela: Centro por papel, encerramento do Edital e do Processo, relatório e a
  varredura de palavras (SC-1950 a SC-1956).
- [x] T008 `make lint check test-pg`; as telas no navegador com o cenário C12 (pessoas aptas em poucos passos); `rastreabilidade.md`.
