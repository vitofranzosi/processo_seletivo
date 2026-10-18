# Implementation Plan: As telas do Edital, quinto incremento

**Branch**: `claude/telas-do-edital-083-610769` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em doze templates. A trilha sobe ao cabeçalho de contexto, pelo bloco
`caminho_do_contexto` que a `077` criou e com o produto pelo parcial da `078`, em Novo Edital,
Retificar, no detalhe da Retificação e na conferência de cada ato, na Prévia, em Partir de um Edital
anterior e na conferência da troca, na Condução do marco e na conferência do gesto, na Prévia de
publicação, nos Resultados divulgados e — no ramo que faltava do modelo das três auditorias — na
Auditoria do Edital. Em Retificar e na Prévia de publicação, a recusa do último envio sobe para
logo abaixo do título; no detalhe da Retificação, "O que fazer agora" vem antes
da Vigência; em Partir de um Edital anterior, "Filtrar" e "Limpar" ganham o desenho das Inscrições.
Nenhuma migration, nenhuma permissão, nenhum endereço, nenhuma view, nenhuma regra na folha comum,
nenhuma classe nova.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. Templates apenas. As views entregam o Edital, e a
trilha lê o Processo a partir dele (`edital.processo_id` para o endereço, `edital.processo` para o
código) — o mesmo que o detalhe do Edital e a composição leem desde a `078`; a consulta a mais, onde a
view não traz o Processo junto, foi medida (R-002). A linha de base visual é o inventário refeito em
18/10 sobre `cf6d7372`, no banco `ps_inventario_083` (cópia do `ps_inventario_telas`), nos dois estados
da barra, guardado em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/`; ele é
idêntico, campo a campo, a `depois-da-080/`. A decisão de cada mudança e as alternativas descartadas
estão em [research.md](research.md). Não há entidade nem contrato externo: `data-model.md` e
`contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda de sentido; cada região continua
  saindo das mesmas variáveis da view, e cada link da trilha leva a uma tela que já condiciona o
  acesso. Os dois níveis que eram condicionais continuam com a mesma condição (D-003).
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam (D-001).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. A `FR-1803` da `080` e a `FR-1782` da `079`, que nomeavam a
  Auditoria do Edital entre as demais telas, são anotadas como emendadas.
- **Simplicidade (V)**: blocos de template e regiões que trocam de lugar. Nenhum script, nenhuma
  classe nova, nenhuma regra nova na folha.
- **Completude de jornada (VI)**: o percurso é provado no navegador a 1280 e a 375 px, pelo teclado,
  e o inventário inteiro é refeito nos dois estados da barra e comparado campo a campo e pixel a pixel.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/edital_criar.html` | o bloco `caminho_do_contexto` com a trilha (R-001) |
| `retificar.html` | o bloco com a trilha; as recusas logo depois do título (R-001, R-003) |
| `retificacao_detalhe.html` | o bloco com a trilha; "O que fazer agora" antes da Vigência (R-001, R-004) |
| `retificacao_confirmar.html` | o bloco com a trilha, terminando no ato (R-001) |
| `previa.html` | o bloco com a trilha (R-001) |
| `reaproveitar.html` | o bloco com a trilha; "Filtrar" como `botao` e "Limpar" como `acao` (R-001, R-005) |
| `reaproveitar_confirmar.html` | o bloco com a trilha, passando por Compor (R-001) |
| `marco.html` | o bloco com a trilha; o erro e o desfecho ficam depois dos termos (R-001, R-003) |
| `marco_conferir.html` | o bloco com a trilha, terminando em Conferir (R-001) |
| `previa_de_publicacao.html` | o bloco com a trilha, com o nível condicional; a recusa logo depois do título (R-001, R-003) |
| `publicacoes_do_marco.html` | o bloco com a trilha, com o nível condicional (R-001) |
| `auditoria.html` | o ramo do Edital no bloco; nenhuma trilha no conteúdo (R-001) |
| `specs/079-*`, `080-*` (spec e rastreabilidade) | `FR-1782` e `FR-1803` anotadas como emendadas pela `083` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-083/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas das telas do escopo |

## Testes que mudam, e por quê

Ver o R-006 da pesquisa. Testes novos em `tests/interface/test_telas_do_edital.py`.

## Verificação

`make lint check test-pg DB_NAME=ps_083`; o percurso do [quickstart](quickstart.md) no navegador, a
1280 e a 375 px, pelo teclado; o inventário refeito com `BARRA=expandida` e `BARRA=recolhida`,
comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes.
