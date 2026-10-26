"""Semeia o banco de demonstração do relatório consolidado (100) com Editais de natureza diferente.

Uso, a partir de `backend/`, num banco preparado por `make preparar DB_NAME=<banco>`:

    set -a; source .env; set +a
    DB_NAME=<banco> uv run python manage.py shell < \
        ../doc/estudo-relatorio-consolidado-de-gestao-2026-10-24/roteiro/semear_demonstracao.py

Cada Edital passa pelos comandos da aplicação, com o relógio na data de cada ato (o cenário
coerente da `099`, parametrizado pela `100`): publicação, Retificação de prorrogação, inscrições,
avaliação, resultados, recursos, apuração, convocações e desfecho. Os títulos e os perfis mudam de
um Edital a outro; os números do relatório saem do GPS, e nenhum é digitado. Os candidatos são
fictícios e os mesmos em todos os Editais — como acontece de verdade, e é por isso que o relatório
conta inscrições, e não pessoas.
"""

from tests.fixtures.relatorio import dia, montar_cenario

EDITAIS = (
    # número, final, publicação, extras, (Processo, assunto do Edital), perfis, o que demonstra
    (
        "62",
        "sem-pendencia",
        dia(10, 2, 9),
        {},
        ("Seleção de Tutores a Distância 2026/1", "Tutores a distância — Licenciatura em Letras"),
        {
            "prof": ("Tutor a distância — Polo Vila Azul", "Polo Vila Azul"),
            "tec": ("Tutor — cadastro de reserva", "Polos Serra Alta e Rio Claro"),
        },
        "encerrado sem providência",
    ),
    (
        "64",
        "pendente",
        dia(20, 3, 9),
        {"tecnicos": 3},
        (
            "Seleção de Professores Formadores 2026",
            "Professores formadores — Especialização em Educação Profissional",
        ),
        {
            "prof": ("Formador — Didática da Educação Profissional", "Cefor, a distância"),
            "tec": ("Formador — cadastro de reserva", "Cefor, a distância"),
        },
        "convocação no prazo; Perfil pequeno (supressão complementar)",
    ),
    (
        "63",
        "cancelado",
        dia(15, 4, 9),
        {"maximo": 4},
        ("Seleção de Tutores — Pedagogia 2026", "Tutores a distância — Pedagogia"),
        {
            "prof": ("Tutor a distância — Polo Mangue Seco", "Polo Mangue Seco"),
            "tec": ("Tutor — cadastro de reserva", "Polo Mangue Seco"),
        },
        "cancelado: fora de todo número",
    ),
    (
        "65",
        "aberto",
        dia(5, 5, 9),
        {"maximo": 4},
        ("Bolsistas de Apoio Técnico 2026", "Bolsista de apoio técnico ao laboratório"),
        {
            "prof": ("Bolsista — Laboratório de Produção", "Cefor"),
            "tec": ("Bolsista — cadastro de reserva", "Cefor"),
        },
        "Edital pequeno, sem resultado: fora dos números não públicos",
    ),
    (
        "67",
        "pendente",
        dia(25, 5, 9),
        # Escala 10: 362 inscrições. Entre 2 e 9, as notas distintas do cenário ficam todas
        # abaixo de 6 e ninguém chega à segunda etapa.
        {"escala": 10, "vagas_tec": 4},
        (
            "Especialização em Informática na Educação 2026",
            "Ingresso discente — Especialização em Informática na Educação",
        ),
        {
            "prof": ("Cursista — Polo Vila Azul", "Polo Vila Azul"),
            "tec": ("Cursista — Polo Serra Alta", "Polo Serra Alta"),
        },
        "procura alta; vagas de um polo ainda não apuradas",
    ),
    (
        "66",
        "sem-pendencia",
        dia(12, 6, 9),
        {"tecnicos": 0},
        ("Seleção de Designer Instrucional 2026", "Designer instrucional e ilustrador"),
        {
            "prof": ("Designer instrucional", "Cefor"),
            "tec": ("Ilustrador — cadastro de reserva", "Cefor"),
        },
        "Perfil sem inscrição: sem pendência perpétua",
    ),
    (
        "61",
        "pendente",
        None,
        {},
        ("Processo Seletivo Simplificado 2026/2", None),
        {},
        "2º semestre: convocação no prazo e registro posterior",
    ),
)

for numero, final, publicado_em, extras, titulo, perfis, caso in EDITAIS:
    cenario = montar_cenario(
        final=final, numero=numero, publicado_em=publicado_em, titulo=titulo, perfis=perfis, **extras
    )
    print(f"{cenario.edital} — {cenario.edital.status} — {caso}")
