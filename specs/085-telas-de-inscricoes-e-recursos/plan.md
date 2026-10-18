# Implementation Plan: As telas de inscrições e de recursos, sétimo incremento

**Branch**: `claude/telas-de-inscricoes-085-f7ccd0` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em quatro templates, e uma junção em duas leituras. A trilha sobe ao cabeçalho de
contexto nas Inscrições, na Inscrição recebida, nos Recursos e no Recurso, pelo bloco que a `077`
criou, com o Processo entre a seção e o Edital, como no detalhe do Edital desde a `078`. Nas
Inscrições, a lista sem inscrição recebida passa ao estado vazio comum, e os rascunhos ganham região
nomeada. A tela de recusa fica fora (D-002 da spec). Nenhuma migration, nenhuma permissão, nenhum
endereço, nenhuma view, nenhuma regra na folha comum, nenhuma classe nova.

## Technical Context

Django 5 sobre PostgreSQL. Os Recursos e o Recurso já liam o Processo junto do Edital
(`obter_edital` e `_peca_para_julgar`); as Inscrições e a Inscrição recebida, não — as duas leituras
de `inscricoes/application/consulta.py` ganham a junção (D-003 da spec, R-002). A linha de base visual
é o inventário refeito em 18/10 sobre `cf6d7372`, no banco `ps_inventario_085` (cópia do
`ps_inventario_080`), nos dois estados da barra, guardado em
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/`. A decisão de cada mudança e as
alternativas descartadas estão em [research.md](research.md). Não há entidade nem contrato externo:
`data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda de sentido; cada região continua
  saindo das mesmas variáveis da view. Cada link da trilha leva a uma tela cuja porta é a da tela de
  origem ou mais larga (R-001), e o teste abre cada uma como quem julga.
- **Dado pessoal (LGPD)**: a trilha nomeia a inscrição e o recurso pelo protocolo, que a página já
  mostrava; o teste confere que o nome e o e-mail não estão nela.
- **Linguagem ubíqua (I)**: os rótulos são os que as telas já usavam como página atual.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`.
- **Simplicidade (V)**: blocos de template e uma junção. Nenhum script, nenhuma classe, nenhuma regra
  na folha.
- **Completude de jornada (VI)**: o percurso é provado no navegador a 1280 e a 375 px, pelo teclado,
  e o inventário inteiro é refeito nos dois estados da barra e comparado campo a campo e pixel a pixel.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/inscricoes.html` | o bloco `caminho_do_contexto` com a trilha; "Nenhuma inscrição recebida até agora." como `p.vazio`; a `section` dos rascunhos (R-001, R-003, R-004) |
| `inscricao_detalhe.html` | o bloco com a trilha, terminando no protocolo ou em "Em preenchimento" (R-001) |
| `recursos.html` | o bloco com a trilha (R-001) |
| `recurso.html` | o bloco com a trilha, terminando no protocolo do recurso (R-001) |
| `inscricoes/application/consulta.py` | `select_related("processo")` em `_edital_no_escopo`; `edital__processo` em `inscricao_para_consulta` (R-002) |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-085/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas das telas do escopo |

## Testes

Novos em `tests/interface/test_telas_de_inscricoes_e_recursos.py`. Um guardião da `076` passa das
Inscrições aos Avisos do Edital (R-005).

## Verificação

`make lint check test-pg DB_NAME=ps_085`; o percurso do [quickstart](quickstart.md) no navegador, a
1280 e a 375 px, pelo teclado; o inventário refeito com `BARRA=expandida` e `BARRA=recolhida`,
comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes.
