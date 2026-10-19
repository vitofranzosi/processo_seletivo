# Implementation Plan: As telas filhas da Distribuição e a auditoria da comissão, quarto incremento

**Branch**: `claude/telas-filhas-da-distribuicao-ea155a` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em seis templates. A trilha sobe ao cabeçalho de contexto em Impedimentos, Registrar
ocorrência, Resultados, Conclusões preservadas, na conferência da retirada e — no modelo de página
que as três auditorias dividem — na Trilha da avaliação e na Auditoria da comissão, pelo bloco que a
`077` criou; a Auditoria do Edital fica com o cabeçalho da `076`. Em Registrar ocorrência e nas
Conclusões preservadas, as mensagens do último envio sobem para logo abaixo do título; Impedimentos
ganha a seção "Registrar um impedimento"; "Filtrar" ganha o desenho de ação principal nas três
consultas. Nenhuma migration, nenhuma permissão, nenhum endereço, nenhuma view, nenhuma regra na folha
comum, nenhuma classe nova.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. Templates apenas, e as seis views já entregam o
Processo, o Edital e a Etapa que a trilha lê — nenhuma consulta a mais. A linha de base visual é o
inventário refeito em 17/10 sobre `fbe5bba3`, no banco `ps_inventario_080` (cópia do
`ps_inventario_telas`), nos dois estados da barra, guardado em
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/`. Ele difere de `depois-da-079/` só
em `auditoria-comissao` e `aviso`, e por dado, não por código: o percurso da `079` gravou duas
alocações depois da captura dela, e o aviso tem a hora da leitura; nenhum arquivo de
`backend/processo_seletivo/` mudou desde o merge da `079` (PR 294). A decisão de cada mudança e as
alternativas descartadas estão em [research.md](research.md). Não há entidade nem contrato externo:
`data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda de sentido; cada região continua
  saindo das mesmas variáveis da view, e cada link da trilha leva a uma tela que já condiciona o
  acesso. A trilha não oferece nem esconde nível conforme quem lê (D-003).
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam como página atual, e
  os níveis acima são os da Distribuição (D-001).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. Os requisitos da `077`, da `078` e da `079` que fixavam as filhas
  com o cabeçalho da `076` são anotadas como emendadas.
- **Simplicidade (V)**: blocos de template e regiões que trocam de lugar. Nenhum script, nenhuma
  classe nova, nenhuma regra nova na folha.
- **Completude de jornada (VI)**: o percurso é provado no navegador a 1280 e a 375 px, pelo
  teclado, e o inventário inteiro é refeito nos dois estados da barra e comparado campo a campo e
  pixel a pixel.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/impedimentos.html` | o bloco `caminho_do_contexto` com a trilha; a seção "Registrar um impedimento" (R-001, R-004) |
| `ocorrencia.html` | o bloco com a trilha; o erro e o resultado logo depois do título (R-001, R-003) |
| `resultados.html` | o bloco com a trilha (R-001) |
| `conclusoes.html` | o bloco com a trilha; o erro e o resultado da reabertura logo depois do título; "Filtrar" como `botao` (R-001, R-003, R-005) |
| `distribuicao_remover_confirmar.html` | o bloco com a trilha, terminando em Conferir (R-001) |
| `auditoria.html` | o bloco com a trilha da avaliação ou da comissão, e o da `076` para a do Edital, que mantém a trilha no conteúdo; "Filtrar" como `botao` nas duas consultas (R-001, R-002, R-005) |
| `specs/077-*`, `078-*`, `079-*` (spec e rastreabilidade) | `FR-1748`, `FR-1769` e `FR-1782` anotadas como emendadas pela `080` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-080/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas das telas do escopo |

## Testes que mudam, e por quê

Ver o R-006 da pesquisa. Testes novos em `tests/interface/test_telas_filhas_da_distribuicao.py`.

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px, pelo teclado; o inventário refeito com `BARRA=expandida` e
`BARRA=recolhida`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes.
