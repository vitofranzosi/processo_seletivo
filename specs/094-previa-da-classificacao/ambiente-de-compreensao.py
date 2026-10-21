"""O Edital de demonstração da validação de compreensão da 094, na interface real.

Um rascunho do Processo PS-2026-094 — três Etapas (Prova objetiva, Entrevista, Análise documental),
um Perfil com quadro de vagas e dois fatos declarados, e dois marcos pela pontuação: a
"Classificação para a entrevista", que corta para a Entrevista, e a "Classificação final", que corta
para a Análise documental com o alvo do quadro. É a forma dos Editais de tutoria da amostra, e é
nela que as respostas de `roteiro-de-compreensao.md` foram calculadas.

**Pelo caminho dos testes da interface, e não por fora**: cada etapa é um POST no formulário da
composição, como o elaborador faria. Rodar de novo regrava o mesmo rascunho — a idempotência do
Processo e as identidades fixas garantem — e desfaz o que a sessão anterior tiver mexido.

    cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_094_ui ... uv run python manage.py shell \
        < ../specs/094-previa-da-classificacao/ambiente-de-compreensao.py

As variáveis completas estão em `quickstart.md`, seção 2.
"""

from django.conf import settings
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]
settings.INTERFACE_SELETOR_IDENTIDADE = True

from processo_seletivo.processos.models import Edital  # noqa: E402
from tests.interface.conftest import identificar  # noqa: E402
from tests.interface.test_compor import eventos, perfis  # noqa: E402

PERFIL = "aaaaaaaa-0000-4000-8000-00000000e001"
PROVA, ENTREVISTA, ANALISE = (
    "aaaaaaaa-0000-4000-8000-0000000094e1",
    "aaaaaaaa-0000-4000-8000-0000000094e2",
    "aaaaaaaa-0000-4000-8000-0000000094e3",
)
EVENTO = "aaaaaaaa-0000-4000-8000-00000000e002"
FATO_EXP, FATO_NASC = "aaaaaaaa-0000-4000-8000-0000000094f1", "aaaaaaaa-0000-4000-8000-0000000094f2"

api = APIClient()
r = api.post(
    "/api/v1/admin/processos",
    {
        "institutionalCode": "PS-2026-094",
        "title": "Processo Seletivo de Tutores EaD 2026",
        "firstEdital": {"number": "94", "year": 2026, "title": "Seleção de tutores a distância"},
    },
    format="json",
    HTTP_AUTHORIZATION="Bearer gestor-a|cefor|processo:criar,processo:ativar,edital:criar",
    HTTP_IDEMPOTENCY_KEY="demo-previa-094-0001",
    HTTP_X_CORRELATION_ID="demo-094",
)
assert r.status_code in (200, 201), r.content
edital = Edital.objects.filter(processo__institutional_code="PS-2026-094").get()

c = Client()
identificar(c, "ana.elaboradora", ["elaborador"])


def post(etapa, dados):
    resposta = c.post(reverse("interface:compor-etapa", args=[edital.id, etapa]), dados)
    assert resposta.status_code == 302, resposta.content.decode()[:3000]


post(
    "perfis",
    perfis(
        **{
            "perfil-0-code": "TUTOR-EAD",
            "perfil-0-name": "Tutor a distância",
            "perfil-0-immediateVacancies": "10",
            "perfil-0-reserveLimit": "20",
            "fato-0-0-id": FATO_EXP,
            "fato-0-0-code": "EXPERIENCIA",
            "fato-0-0-label": "Meses de experiência em EaD",
            "fato-0-0-type": "INTEIRO",
            "fato-0-1-id": FATO_NASC,
            "fato-0-1-code": "NASCIMENTO",
            "fato-0-1-label": "Data de nascimento",
            "fato-0-1-type": "DATA",
            "linha-0-0-id": "aaaaaaaa-0000-4000-8000-0000000094c0",
            "linha-0-0-modalityId": "",
            "linha-0-0-immediateVacancies": "9",
            "linha-0-1-id": "aaaaaaaa-0000-4000-8000-0000000094c1",
            "linha-0-1-modalityId": "aaaaaaaa-0000-4000-8000-00000000e031",
            "linha-0-1-immediateVacancies": "",
            "linha-0-2-id": "aaaaaaaa-0000-4000-8000-0000000094c2",
            "linha-0-2-modalityId": "aaaaaaaa-0000-4000-8000-00000000e032",
            "linha-0-2-immediateVacancies": "1",
        }
    ),
)
post("cronograma", eventos(**{"evento-0-endAt": "2026-12-20T23:59"}))
post(
    "etapas",
    {
        "etapa-0-id": PROVA,
        "etapa-0-name": "Prova objetiva",
        "etapa-0-order": "1",
        "etapa-0-weight": "1",
        "etapa-0-classificatory": "on",
        "etapa-0-eliminatory": "on",
        "etapa-0-minimumScore": "50",
        "etapa-0-scheduleEventId": EVENTO,
        "etapa-1-id": ENTREVISTA,
        "etapa-1-name": "Entrevista",
        "etapa-1-order": "2",
        "etapa-1-weight": "2",
        "etapa-1-classificatory": "on",
        "etapa-1-scheduleEventId": "",
        "etapa-2-id": ANALISE,
        "etapa-2-name": "Análise documental",
        "etapa-2-order": "3",
        "etapa-2-weight": "1",
        "etapa-2-eliminatory": "on",
        "etapa-2-scheduleEventId": "",
    },
)
B0, B1 = f"marco-{PERFIL}-0", f"marco-{PERFIL}-1"
C0, C1 = f"criterio-{PERFIL}-0", f"criterio-{PERFIL}-1"
post(
    "classificacao",
    {
        "perfil_id": PERFIL,
        f"{B0}-id": "aaaaaaaa-0000-4000-8000-0000000094a1",
        f"{B0}-code": "PROVA",
        f"{B0}-name": "Classificação para a entrevista",
        f"{B0}-orderProduction": "POR_PONTUACAO",
        f"{B0}-stages": PROVA,
        f"{B0}-operation": "SOMA_PONDERADA",
        f"{B0}-normalization": "NENHUMA",
        f"{B0}-scale": "2",
        f"{B0}-mode": "MEIO_PARA_CIMA",
        f"{C0}-0-id": "aaaaaaaa-0000-4000-8000-0000000094d1",
        f"{C0}-0-order": "1",
        f"{C0}-0-type": "MAIOR_VALOR_DE_FATO",
        f"{C0}-0-target": FATO_EXP,
        f"{C0}-0-whenMissing": "ULTIMO_NO_CRITERIO",
        f"{B0}-cutTargetKind": "FIXED",
        f"{B0}-cutTargetCount": "30",
        f"{B0}-cutSurplusCount": "10",
        f"{B0}-cutTieOutcome": "ADMITS_SURPLUS",
        f"{B0}-cutGovernedStage": ENTREVISTA,
        f"{B0}-cutContinuation": "ALLOWED",
        f"{B1}-id": "aaaaaaaa-0000-4000-8000-0000000094a2",
        f"{B1}-code": "FINAL",
        f"{B1}-name": "Classificação final",
        f"{B1}-orderProduction": "POR_PONTUACAO",
        f"{B1}-stages": [PROVA, ENTREVISTA],
        f"{B1}-operation": "SOMA_PONDERADA",
        f"{B1}-normalization": "NENHUMA",
        f"{B1}-scale": "2",
        f"{B1}-mode": "MEIO_PARA_CIMA",
        f"{C1}-0-id": "aaaaaaaa-0000-4000-8000-0000000094d2",
        f"{C1}-0-order": "1",
        f"{C1}-0-type": "MAIOR_PONTUACAO_NA_ETAPA",
        f"{C1}-0-target": ENTREVISTA,
        f"{C1}-0-whenMissing": "ULTIMO_NO_CRITERIO",
        f"{C1}-1-id": "aaaaaaaa-0000-4000-8000-0000000094d3",
        f"{C1}-1-order": "2",
        f"{C1}-1-type": "MENOR_VALOR_DE_FATO",
        f"{C1}-1-target": FATO_NASC,
        f"{C1}-1-whenMissing": "ULTIMO_NO_CRITERIO",
        f"{B1}-cutTargetKind": "FROM_VACANCY_TABLE",
        f"{B1}-cutSurplusCount": "10",
        f"{B1}-cutTieOutcome": "ADMITS_SURPLUS",
        f"{B1}-cutGovernedStage": ANALISE,
        f"{B1}-cutContinuation": "ALLOWED",
    },
)
print("edital", edital.id)
print(f"http://localhost:8095/gestao/editais/{edital.id}/compor/classificacao")
