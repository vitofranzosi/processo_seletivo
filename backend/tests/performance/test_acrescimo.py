"""O custo da vaga acrescida não cresce com os acréscimos do recorte (097, `SC-924`).

**Contagem de consultas, e não relógio.** O que se cobra é a forma: a leitura, a conferência e o ato
leem os acréscimos de uma vez, e uma consulta por acréscimo — o laço que abre o registro citado por
cada desfazimento, por exemplo — faria o custo crescer a cada matrícula que o Edital regular perde.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.ocupacao.application.acrescimo import (
    acrescentar_vagas,
    previa_do_acrescimo,
)
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import AcrescimoDeVagas
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.convocacao import habilitar_na_etapa_governada
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.performance, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def reserva(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    edital, _, inscricoes = montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-097-escala",
        geral=0,
        reserva="UNLIMITED",
    )
    habilitar_na_etapa_governada(edital, inscricoes[:3])
    return edital


def gravar(edital, quantos):
    """`quantos` acréscimos, cada um com um desfazimento parcial — o pior caso da leitura."""
    versao = effective_version(edital_id=edital.id)
    for _ in range(quantos):
        acrescimo = AcrescimoDeVagas.objects.create(
            edital=edital,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            especie=nomes.ACRESCIMO,
            quantidade=2,
            origem="Edital Multicampi nº 20/2026",
            fundamento="Vaga não preenchida",
            versao=versao,
            registrado_por="teste",
            registrado_em=timezone.now(),
        )
        AcrescimoDeVagas.objects.create(
            edital=edital,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            especie=nomes.DESFAZIMENTO,
            quantidade=1,
            fundamento="Engano",
            desfaz=acrescimo,
            versao=versao,
            registrado_por="teste",
            registrado_em=timezone.now(),
        )


def consultas(funcao):
    with CaptureQueriesContext(connection) as ctx:
        funcao()
    return len(ctx.captured_queries)


def test_a_previa_custa_o_mesmo_com_um_e_com_dez(reserva):
    edital = reserva
    previa = lambda: previa_do_acrescimo(  # noqa: E731
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, quantidade=1
    )
    gravar(edital, 1)
    com_um = consultas(previa)
    gravar(edital, 9)

    assert consultas(previa) == com_um


def test_a_tela_custa_o_mesmo_com_um_e_com_dez(client, seletor_ligado, reserva):
    edital = reserva
    identificar(client, "carlos", ["gestor"])
    abrir = lambda: client.get(reverse("interface:ocupacao", args=[edital.id, MARCO]))  # noqa: E731
    gravar(edital, 1)
    com_um = consultas(abrir)
    gravar(edital, 9)

    assert consultas(abrir) == com_um


def test_o_ato_custa_o_mesmo_com_um_e_com_dez(reserva, gestor):
    edital = reserva

    def ato(chave):
        leitura = previa_do_acrescimo(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, quantidade=1
        )["assinatura"]
        return consultas(
            lambda: acrescentar_vagas(
                actor=gestor,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=PROFILE_ID,
                marco_id=MARCO,
                quantidade=1,
                origem="Edital Multicampi nº 20/2026",
                fundamento="Vaga não preenchida",
                leitura_confirmada=leitura,
                idempotency_key=chave,
                correlation_id="teste-097-escala",
            )
        )

    # **A primeira vez emite a primeira apuração, e as seguintes a sucedem**: são caminhos de custo
    # diferente, e comparar os dois mediria a sucessão, e não os acréscimos.
    ato("097-escala-0")
    gravar(edital, 1)
    com_um = ato("097-escala-1")
    gravar(edital, 9)
    com_dez = ato("097-escala-10")
    gravar(edital, 10)

    assert ato("097-escala-20") == com_dez == com_um
