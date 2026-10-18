# Implementation Plan: Os achados das revisões da 077 e da 079

**Branch**: `claude/achados-077-079-b4f1f5` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

Dois templates, uma regra na folha comum e o apoio de teste. Na Distribuição, "Consolidar as
selecionadas" passa ao desenho secundário com a marca "irreversível" — o desenho que os atos do
Processo já têm —, e "Distribuir as selecionadas" fica como ação principal. Na Alocação, o aviso diz
"antes de alocar". A montagem do `cenario` da presidência sai do módulo de teste da `012` para
`tests/fixtures/mesa.py`, cada módulo declara a própria fixture, e um guardião confere a abertura da
trilha em todos os templates que a sobrescrevem. Os outros sete achados ficam como decisão, na spec. Nenhuma migration, nenhuma permissão, nenhum
endereço, nenhuma view, nenhuma mensagem de domínio.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. A linha de base visual é o inventário refeito em
17/10 sobre `cf6d7372`, no banco `ps_inventario_081` (cópia do `ps_inventario_080`), nos dois estados
da barra, guardado em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/antes/`; pelo
`medidas.py`, ele não difere em nada de `depois-da-080/`. A decisão de cada mudança e as alternativas
descartadas estão em [research.md](research.md). Não há entidade nem contrato externo:
`data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda; os dois botões continuam saindo
  das mesmas variáveis, com o mesmo destino, e o aviso com a mesma condição.
- **Linguagem ubíqua (I)**: "alocar" é o ato da Alocação por Etapa, e "distribuir" o da Distribuição;
  o aviso passa a usar o da própria tela, como o botão desde a `079`.
- **Imutabilidade (II)**: a marca "irreversível" diz, antes da conferência, que a consolidação
  produz ato que não se corrige; nada no ato muda.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`; cada achado tem destino na tabela de decisões da spec.
- **Simplicidade (V)**: classes que já existem — `botao secundario` e `marca-irreversivel` —, e uma
  regra na folha comum para a marca não esticar em linha flexível. Nenhum script.
- **Completude de jornada (VI)**: a Distribuição é vista no navegador a 1280 e a 375 px, e o
  inventário inteiro é refeito nos dois estados da barra.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/distribuicao.html` | as duas consolidações — "Consolidar as selecionadas" e "Consolidar as N prontas" — com `botao secundario` e a marca "irreversível" logo depois, que descreve o botão por `aria-describedby` (R-001, R-007) |
| `interface/templates/interface/base.html` | `align-self:center` na própria `.marca-irreversivel`, para ela não esticar até a altura do botão em linha flexível (R-002) |
| `interface/templates/interface/alocacoes.html` | "Designe a presidência antes de alocar." (R-003) |
| `tests/fixtures/mesa.py` | `montar_cenario_da_presidencia`, o corpo do `cenario` de `test_acessibilidade_da_012.py`, composto sobre `montar_banca`, que ganha `com_documentos` (R-004) |
| `tests/interface/test_telas_de_uso_diario.py`, `test_telas_da_presidencia.py`, `test_telas_filhas_da_distribuicao.py`, `test_acessibilidade_da_012.py` | cada um declara a fixture `cenario`, que chama a montagem; sem o import e sem os `noqa` (R-004) |
| `tests/interface/test_achados_das_revisoes.py` (novo) | os testes desta feature, inclusive os dois guardiões (R-004, R-005) |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-081/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas da Distribuição e da Alocação |

## Testes que mudam, e por quê

Ver o R-006 da pesquisa.

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px; o inventário refeito com `BARRA=expandida` e `BARRA=recolhida`,
comparado por `comparar.py` e por `medidas.py` com o de antes.
