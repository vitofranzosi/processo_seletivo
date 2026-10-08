"""A tela das autoridades da unidade (060, FR-1122, UX-149, UX-150).

Quem tem a permissão vê o caminho e a lista da própria unidade, em três grupos; quem não tem
recebe a recusa que nomeia a permissão — e não vê o caminho, que é a garantia que some sem
ninguém notar (`N-03` da 038).
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade
from tests.fixtures.autoridades import registrar_autoridade, registrar_unidade
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

URL = reverse("interface:autoridades")


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


def _hoje():
    return timezone.now().astimezone(ZONA).date()


def _cefor():
    return Unidade.objects.get(codigo="cefor")


def _visivel(corpo):
    return re.sub(r"<[^>]+>", " ", corpo)


def test_sem_a_permissao_a_recusa_nomeia_o_que_falta(client):
    identificar(client, "carla", ["publicador"])
    resposta = client.get(URL)

    assert resposta.status_code == 403
    assert "permissão de gerir as autoridades da unidade" in resposta.content.decode()


def test_o_caminho_so_aparece_para_quem_tem_a_permissao(client):
    identificar(client, "carla", ["publicador"])
    assert URL not in client.get(reverse("interface:lista")).content.decode()

    identificar(client, "gabriel", ["gestor"])
    assert URL in client.get(reverse("interface:lista")).content.decode()


def test_a_lista_separa_vigentes_futuras_e_encerradas_com_o_periodo(client):
    """UX-149."""
    hoje = _hoje()
    registrar_autoridade(_cefor(), cargo="Reitora em vigor", inicio=hoje - timedelta(days=10))
    registrar_autoridade(_cefor(), cargo="Reitora seguinte", inicio=hoje + timedelta(days=5))
    registrar_autoridade(
        _cefor(),
        cargo="Reitora anterior",
        inicio=hoje - timedelta(days=40),
        fim=hoje - timedelta(days=1),
    )
    identificar(client, "gabriel", ["gestor"])

    corpo = client.get(URL).content.decode()

    vigentes = corpo.index("Vigentes")
    futuras = corpo.index("A partir de")
    encerradas = corpo.index("Encerradas")
    assert vigentes < corpo.index("Reitora em vigor") < futuras
    assert futuras < corpo.index("Reitora seguinte") < encerradas
    assert encerradas < corpo.index("Reitora anterior")
    assert f"desde {(hoje - timedelta(days=10)).strftime('%d/%m/%Y')}" in corpo


def test_a_unidade_e_dita_pelo_nome_e_o_identificador_nao_aparece(client):
    """UX-150, FR-1117."""
    autoridade = registrar_autoridade(_cefor(), cargo="Reitora")
    identificar(client, "gabriel", ["gestor"])

    visivel = _visivel(client.get(URL).content.decode())

    assert "Centro de Referência em Formação e em Educação a Distância" in visivel
    assert str(autoridade.pk) not in visivel


def test_so_as_da_propria_unidade(client):
    registrar_autoridade(registrar_unidade("serra"), cargo="Diretor da Serra")
    identificar(client, "gabriel", ["gestor"])

    assert "Diretor da Serra" not in client.get(URL).content.decode()


def test_cadastrar_pela_tela(client):
    identificar(client, "gabriel", ["gestor"])

    resposta = client.post(
        URL,
        {
            "acao": "cadastrar",
            "chave_idempotencia": "ui-cadastro-0001",
            "cargo": "Diretora-Geral",
            "nome": "Maria Exemplo",
            "ato_de_nomeacao": "Portaria nº 1/2026",
            "inicio_vigencia": _hoje().isoformat(),
        },
    )

    assert resposta.status_code == 302
    assert resposta["Location"].endswith("?feito=cadastrar")
    autoridade = AutoridadeHabilitada.objects.get(nome="Maria Exemplo")
    assert (autoridade.unidade.codigo, autoridade.cadastrada_por) == ("cefor", "gabriel")


def test_a_recusa_volta_a_tela_com_o_erro(client):
    identificar(client, "gabriel", ["gestor"])

    resposta = client.post(
        URL,
        {
            "acao": "cadastrar",
            "chave_idempotencia": "ui-cadastro-0002",
            "cargo": "",
            "inicio_vigencia": _hoje().isoformat(),
        },
    )

    assert resposta.status_code == 422
    assert "Informe o cargo" in resposta.content.decode()


def test_data_invalida_e_recusada_sem_quebrar_a_tela(client):
    identificar(client, "gabriel", ["gestor"])
    resposta = client.post(
        URL,
        {
            "acao": "cadastrar",
            "chave_idempotencia": "ui-cadastro-0003",
            "cargo": "Reitora",
            "inicio_vigencia": "31/02/2026",
        },
    )
    assert resposta.status_code == 422


def test_encerrar_pela_tela_e_o_retroativo_recusado(client):
    autoridade = registrar_autoridade(_cefor(), cargo="Reitora", inicio=_hoje() - timedelta(days=9))
    identificar(client, "gabriel", ["gestor"])

    retroativo = client.post(
        URL,
        {
            "acao": "encerrar",
            "chave_idempotencia": "ui-encerrar-0001",
            "autoridade": str(autoridade.pk),
            "fim_vigencia": (_hoje() - timedelta(days=1)).isoformat(),
        },
    )
    assert retroativo.status_code == 422
    assert "não pode ser anterior a hoje" in retroativo.content.decode()

    encerrado = client.post(
        URL,
        {
            "acao": "encerrar",
            "chave_idempotencia": "ui-encerrar-0002",
            "autoridade": str(autoridade.pk),
            "fim_vigencia": _hoje().isoformat(),
        },
    )
    assert encerrado.status_code == 302
    autoridade.refresh_from_db()
    assert autoridade.fim_vigencia == _hoje()


def test_a_usada_nao_oferece_correcao_e_diz_por_que(client):
    usada = registrar_autoridade(_cefor(), cargo="Reitora", usada_em=timezone.now())
    identificar(client, "gabriel", ["gestor"])

    corpo = client.get(URL).content.decode()

    assert "Já usada em ato publicado" in corpo
    assert f'id="cargo-{usada.pk}"' not in corpo, "sem o formulário de correção"
    assert f'id="fim-{usada.pk}"' in corpo, "mas encerrar continua possível"


def test_autoridade_de_outra_unidade_responde_como_inexistente(client):
    da_serra = registrar_autoridade(registrar_unidade("serra"))
    identificar(client, "gabriel", ["gestor"])

    resposta = client.post(
        URL,
        {
            "acao": "encerrar",
            "chave_idempotencia": "ui-encerrar-0003",
            "autoridade": str(da_serra.pk),
            "fim_vigencia": _hoje().isoformat(),
        },
    )
    assert resposta.status_code == 404


def test_escopo_sem_unidade_registrada_diz_isso_e_nao_oferece_cadastro(client):
    from tests.interface.conftest import identificar as identificar_com_escopo

    identificar_com_escopo(client, "gabriel", ["gestor"], escopo="sem-unidade")
    corpo = client.get(URL).content.decode()

    assert "não é uma unidade registrada no sistema" in corpo
    assert 'value="cadastrar"' not in corpo
