"""O README lista o que existe — e o que não é conferido, volta a ficar para trás.

A tabela de incrementos parou na `025` enquanto as specs chegavam à `048`, e a de módulos listava
sete dos vinte e um apps. A avaliação de 12/09 já tinha previsto: "enquanto nada o verificar, ele
volta". Nenhum dos dois é defeito de produto, e é justamente por isso que ninguém os pegava: quem
chega sem contexto lê o README primeiro, e lia um projeto de três semanas antes.

O que se confere é **presença**, e não a frase de cada linha: a descrição é escrita por gente, e
um teste que a prendesse viraria cópia da própria tabela.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
README = (RAIZ / "README.md").read_text(encoding="utf-8")


def test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos():
    pastas = sorted(p.name for p in (RAIZ / "specs").iterdir() if re.match(r"\d{3}", p.name))
    ausentes = [pasta for pasta in pastas if f"(specs/{pasta}/spec.md)" not in README]

    assert pastas, "a varredura não encontrou pasta nenhuma em specs/"
    assert not ausentes, f"incrementos fora da tabela do README: {ausentes}"


def test_todo_app_aparece_na_tabela_de_modulos():
    pacote = RAIZ / "backend" / "processo_seletivo"
    apps = sorted(
        p.name
        for p in pacote.iterdir()
        if p.is_dir() and (p / "__init__.py").exists() and not p.name.startswith("_")
    )
    ausentes = [app for app in apps if f"| `{app}` |" not in README]

    assert apps, "a varredura não encontrou app nenhum"
    assert not ausentes, f"módulos fora da tabela do README: {ausentes}"
