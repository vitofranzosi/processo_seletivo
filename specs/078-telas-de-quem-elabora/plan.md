# Implementation Plan: As telas de quem elabora, segundo incremento

**Branch**: `claude/festive-tereshkova-9a826c` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

Duas frentes de apresentação. Na folha comum, as molduras que rolam passam a ser referência de
posição e o `fieldset` passa a poder encolher — as duas causas latentes que a `077` registrou —, e
as três regras pontuais que ela pôs para elas saem das telas. Nas telas de quem elabora — o detalhe
do Processo, o do Edital e as nove etapas da composição —, a trilha sobe ao cabeçalho de contexto
pelo bloco que a `077` criou, "O que fazer agora" vem antes do resto, e os Editais do Processo viram
a tabela da lista, com o estado vazio comum. Nenhuma migration, nenhuma permissão, nenhum endereço,
nenhuma view.

**O escopo cabe num PR.** O pedido mandava propor o corte da composição para um terceiro incremento
se o escopo ficasse grande. Não ficou: as nove etapas herdam a trilha de um arquivo só,
`compor_base.html`, e o resto da composição já está no padrão — a navegação das etapas, o título, a
linha da situação e o estado vazio comum. O diff toca três templates de tela, uma moldura de
template, três folhas de tela e a folha comum.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. Templates e a folha inline do `base.html`. A
linha de base visual é o inventário no estado `depois-da-077`
(`doc/inventario-visual-da-gestao-2026-10-16/depois-da-077/resultados.json`, barra expandida, e
`depois-da-077/recolhida/resultados.json`), reproduzido em 17/10 sobre `a41b67c0` sem diferença
nenhuma, no banco `ps_inventario_telas`. A medição das causas latentes, a decisão de cada mudança e
as alternativas descartadas estão em [research.md](research.md). Não há entidade nem contrato
externo: `data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda; cada região continua saindo das
  mesmas variáveis da view, e cada link da trilha leva a uma tela que já condiciona o acesso.
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam — Processos
  Seletivos, o código do Processo, "Edital n/a", Compor. A frase do estado vazio é a da lista.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. As duas FRs da `077` que esta feature emenda (`FR-1745` e
  `FR-1748`) ficam anotadas lá, como a `077` fez com a `FR-1713` da `076`.
- **Simplicidade (V)**: duas regras na folha comum, três removidas das telas, blocos de template,
  regiões que trocam de lugar. Nenhum script, nenhuma classe nova.
- **Completude de jornada (VI)**: o percurso de quem elabora é provado no navegador a 1280 e a
  375 px, e o inventário inteiro é refeito nos dois estados da barra e comparado tela a tela, com as
  capturas também comparadas pixel a pixel com as de antes.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/base.html` | `position:relative` para as molduras que rolam, ao lado de `.tabela-rolavel{overflow-x:auto}`; `min-width:0` na regra de `fieldset` (R-002; FR-1760, FR-1761) |
| `conclusoes.html`, `reaproveitar.html`, `compor_anexos.html` | sem as regras pontuais da `077` para as duas causas (FR-1762) |
| `processo_detalhe.html` | o bloco `caminho_do_contexto` com a trilha; a `div.colunas` antes de "Onde cada Edital está", com "O que fazer agora" em primeiro; os Editais em tabela; o estado vazio comum (R-003, R-004, R-005) |
| `detalhe.html` | o bloco com a trilha; "O que fazer agora" antes de "Quem atuou" (R-003, R-004) |
| `compor_base.html` | o bloco com a trilha, com o Processo entre a seção e o Edital (R-004) |
| `specs/077-telas-de-uso-diario/spec.md` e `rastreabilidade.md` | `FR-1745` e `FR-1748` anotadas como emendadas pela `078` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-078/` | o inventário refeito nos dois estados da barra, a comparação e as capturas das telas que mudaram |

## Testes que mudam, e por quê

Ver o R-006 da pesquisa. Testes novos em `tests/interface/test_telas_de_quem_elabora.py`: as duas
regras na folha comum e as três pontuais fora das telas; a trilha no cabeçalho, e só uma, no Processo,
no Edital e em toda etapa da composição; a ordem das regiões nas duas telas; a tabela dos Editais e
o estado vazio.

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px, só pelo teclado; o inventário refeito com `BARRA=expandida` e
`BARRA=recolhida`, comparado por `comparar.py` com `depois-da-077/`, e as capturas comparadas pixel a
pixel com as de antes, tiradas no mesmo dia, no mesmo banco.
