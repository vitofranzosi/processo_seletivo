"""Semeia o banco de demonstração do relatório consolidado (100) com Editais do cenário coerente.

Uso, a partir de `backend/`, num banco preparado por `make preparar DB_NAME=<banco>`:

    set -a; source .env; set +a
    DB_NAME=<banco> uv run python manage.py shell < \
        ../doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/roteiro/semear_demonstracao.py

Cada Edital passa pelos comandos da aplicação, com o relógio na data de cada ato (a fixture da
`099`, parametrizada pela `100`). Os candidatos são fictícios e os mesmos em todos os Editais.
"""

from tests.fixtures.relatorio import dia, montar_cenario

EDITAIS = (
    # número, final, publicação, e o que o caso demonstra
    ("62", "sem-pendencia", dia(10, 2, 9), {}, "encerrado sem providência"),
    ("63", "cancelado", dia(15, 4, 9), {"maximo": 4}, "cancelado: fora de todo número"),
    ("64", "pendente", dia(20, 3, 9), {"tecnicos": 3}, "Perfil pequeno: supressão complementar"),
    ("65", "aberto", dia(5, 5, 9), {"maximo": 4}, "Edital pequeno: fora dos não públicos"),
    ("66", "sem-pendencia", dia(12, 6, 9), {"tecnicos": 0}, "Perfil sem inscrição: sem pendência"),
    ("61", "pendente", None, {}, "2º semestre: convocação no prazo e registro posterior"),
)

for numero, final, publicado_em, extras, caso in EDITAIS:
    cenario = montar_cenario(final=final, numero=numero, publicado_em=publicado_em, **extras)
    print(f"{cenario.edital} — {cenario.edital.status} — {caso}")
