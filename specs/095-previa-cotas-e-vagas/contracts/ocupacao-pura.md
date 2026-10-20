# Contrato: as duas decisões da ocupação, puras (D-005, R-003)

Funções do domínio da ocupação, sem banco, sem modelo, sem relógio. O caminho oficial e a prévia as
chamam; a igualdade com o comportamento de hoje é teste.

## `apuracao.ocupantes_pela_ampla`

```text
ocupantes_pela_ampla(
    *, progrediram_em_ordem, publicadas, movimentos_lidos=(), efeitos_lidos=(),
    empates_residuais=None, habilitadas=None,
) -> set[str]
```

- `efetivas = publicadas + recebidas − cedidas`, com os movimentos no formato de `apurar`.
- Devolve `ocupantes(titulares=titulares_iniciais(progrediram_em_ordem, efetivas, empates_residuais,
  habilitadas), efeitos_lidos=efeitos_lidos)` — **sem** `habilitadas` em `ocupantes`, como hoje
  (R-002). Mudar isso é decisão do usuário, e não desta extração.
- Levanta `EmpateNaFronteiraDoAlvo` como `titulares_iniciais` levanta.

**Quem chama**: `ocupacao/application/selectors.py::ocupantes_da_ampla`, que continua fazendo as
mesmas consultas (ordem, corte, habilitadas, linha, movimentos, efeitos) e passa a delegar a conta; e
`classificacao/application/previa.py`, com a faixa fictícia da ampla, `habilitadas` igual à faixa e
nenhum movimento nem efeito.

## `reversao.ha_quem_ocupar`

```text
ha_quem_ocupar(*, posicoes, ja_ocupadas) -> bool
```

- `sum(1 for posicao in posicoes if posicao is not None) > ja_ocupadas`.
- Conta **todas** as posições da ordem do recorte, inclusive de quem ocupa pela ampla e de quem está
  fora da faixa, como hoje (DP-2).

**Quem chama**: `ocupacao/application/movimento.py::ha_quem_ocupar`, que lê as posições do ato vigente
e devolve `False` sem ato, como hoje; e a prévia, com as posições da ordem fictícia do recorte.

## Garantia de igualdade

- Para todo cenário da linha de base (T003), `selectors.ocupantes_da_ampla` e
  `movimento.ha_quem_ocupar` devolvem, antes e depois da extração, o mesmo valor.
- O número de consultas de `_apurar`, de `ocupacao_selectors.recortes_do_marco` e da fila da
  convocação não muda.
- Nenhum teste existente de `tests/unit/ocupacao/`, `tests/integration/ocupacao/` e
  `tests/integration/convocacao/` muda.
