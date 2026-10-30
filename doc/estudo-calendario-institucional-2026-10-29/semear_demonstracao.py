"""Semeia um banco de demonstração para a Agenda dos Editais (101). Dados fictícios.

Uso, a partir de `backend/`, num banco preparado (`make preparar DB_NAME=ps_demo_101`):

    DB_NAME=ps_demo_101 DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py shell \
      < ../doc/estudo-calendario-institucional-2026-10-29/semear_demonstracao.py

Sete Editais publicados pelo canal administrativo — o mesmo ciclo dos testes —, com as datas relativas
ao dia em que roda: um dia, daqui a 16 dias, concentra seis marcos de cinco Editais e uma prova
cancelada; um período atravessa três meses; um Edital tem Retificação publicada que só vigora
daqui a seis dias. Nada aqui é dado de pessoa real.
"""

from rest_framework.test import APIClient

from tests.fixtures.agenda import em, evento, publicar
from tests.fixtures.autoridades import garantir_o_cefor
from tests.fixtures.publicacao import create_retification, publish_retification

garantir_o_cefor()
cliente = APIClient()
gestor = {
    "HTTP_AUTHORIZATION": "Bearer gestor-demo|cefor|processo:criar,processo:ativar,edital:criar",
    "HTTP_X_CORRELATION_ID": "demonstracao-101",
}

CENARIO = {
    101: (
        "Professor substituto de Matemática",
        [
            ("Período de inscrições", em(1), em(12, 18), {"isRegistrationPeriod": True}),
            ("Prova escrita", em(16, 9), None, {"location": "Campus Vitória, sala 12"}),
            ("Resultado preliminar", em(22, 14), None, {}),
            ("Resultado final", em(30, 14), None, {}),
        ],
    ),
    102: (
        "Tutores a distância — Letras",
        [
            ("Período de inscrições", em(-5), em(8, 18), {"isRegistrationPeriod": True}),
            ("Análise documental", em(10), em(14, 18), {}),
            ("Resultado preliminar da análise", em(16, 14), None, {}),
            ("Prazo previsto para recurso", em(17), em(18, 18), {}),
        ],
    ),
    103: (
        "Mediadores presenciais",
        [
            ("Período de inscrições", em(3), em(16, 18), {"isRegistrationPeriod": True}),
            ("Entrevistas", em(16, 14), None, {"location": "Sala virtual da comissão"}),
            ("Prova prática", em(16, 15), None, {"status": "CANCELADO"}),
            ("Resultado final", em(23, 14), None, {}),
        ],
    ),
    104: (
        "Bolsistas de extensão",
        [
            ("Período de inscrições", em(5), em(9, 18), {"isRegistrationPeriod": True}),
            ("Sorteio público", em(16, 10), None, {"location": "Auditório do Cefor"}),
            ("Resultado do sorteio", em(17, 14), None, {}),
        ],
    ),
    105: (
        "Especialização em Docência",
        [
            ("Período de seleção", em(-10), em(45, 18), {}),
            ("Resultado final", em(46, 14), None, {}),
        ],
    ),
    106: (
        "Técnico de laboratório",
        [
            ("Período de inscrições", em(8), em(20, 18), {"isRegistrationPeriod": True}),
            ("Prova objetiva", em(23, 9), None, {}),
        ],
    ),
    107: (
        "Coordenador de polo",
        [
            ("Período de inscrições", em(2), em(6, 18), {"isRegistrationPeriod": True}),
            ("Entrevistas", em(16, 10), None, {}),
            ("Resultado final", em(19, 14), None, {}),
        ],
    ),
}

publicados = {}
for numero, (titulo, eventos) in CENARIO.items():
    cronograma = [
        evento(numero, ordem, nome, inicio, fim, **extra)
        for ordem, (nome, inicio, fim, extra) in enumerate(eventos)
    ]
    carga = {"firstEdital": {"year": 2026, "title": titulo}}
    publicados[numero] = publicar(cliente, gestor, carga, numero, cronograma, titulo=titulo)
    print(f"Edital {numero}/2026 publicado: {titulo}")

prova = evento(106, 1, "x", em(0))["id"]
retificacao = create_retification(
    cliente,
    publicados[106],
    [
        {
            "targetPath": f"/schedule/id={prova}/startAt",
            "operation": "REPLACE",
            "newValue": em(25, 9).isoformat(),
        }
    ],
    effective_at=em(6, 0).isoformat(),
    suffix="demo",
)
publish_retification(cliente, retificacao, suffix="demo")
print("Retificação do Edital 106/2026 publicada, com vigência futura.")
