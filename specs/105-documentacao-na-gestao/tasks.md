# Tasks: A Visão do Sistema dentro da gestão

**Input**: [spec.md](spec.md), [plan.md](plan.md). Caminhos relativos à raiz do repositório.

- [X] T001 Rotas `documentacao` e `documentacao-arquivo` em `backend/processo_seletivo/interface/urls.py`, com barra no fim (FR-2902)
- [X] T002 `visao_do_sistema` em `backend/processo_seletivo/interface/documentacao.py`: identidade, lista literal com tipo, bytes na resposta (FR-2902, FR-2903, D-002, D-003)
- [X] T003 Grupo "Ajuda" e item "Documentação do Sistema" em `backend/processo_seletivo/interface/navegacao.py`; símbolo `i-livro` no sprite do `base.html` (FR-2901)
- [X] T004 Manual sem conteúdo embutido: `assets/iniciar.js`, classe `simbolos-do-manual`, `assets/icone.svg` em `docs/visao-sistema/` (FR-2904)
- [X] T005 Link "Voltar" relativo no pé da barra do manual, com regra em `docs/visao-sistema/assets/style.css` (FR-2905)
- [X] T006 `docs/visao-sistema/` no `Dockerfile` e montado só para leitura no `compose.yaml` (FR-2906)
- [X] T007 `interface/documentacao.py` em `MODULOS_DE_VIEW` de `backend/tests/test_gramatica_das_portas.py`, e a linha da negativa no inventário da `033`
- [X] T008 Testes em `backend/tests/interface/test_documentacao_do_sistema.py`; grupos esperados em `test_shell_da_gestao.py` (SC-991, SC-992, SC-993)
- [X] T009 Linha da `105` na tabela de incrementos do `README.md`
