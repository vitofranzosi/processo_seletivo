"""A suíte nunca chama a Caixa (116, FR-3651, SC-1099).

O vigia é a fixture *autouse* `caixa`, de `tests/conftest.py`. Este arquivo prova as duas camadas:
a conferência ouve a Caixa da suíte, e a conexão de verdade é recusada mesmo com o adaptador real
de volta.
"""

import os
import urllib.request
from datetime import UTC, datetime

import pytest

from processo_seletivo.sorteios.domain import conferencia as dominio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

pytestmark = pytest.mark.skipif(
    bool(os.environ.get("SORTEIO_E2E_FONTE_REAL")),
    reason="Com o E2E da fonte real ligado, a conexão com a Caixa é permitida de propósito.",
)

AGORA = datetime(2026, 11, 3, 22, 3, tzinfo=UTC)


def test_a_conexao_com_a_caixa_e_recusada():
    with pytest.raises(pytest.fail.Exception, match="FR-3651"):
        urllib.request.urlopen(
            "https://servicebus2.caixa.gov.br/portaldeloterias/api/federal", timeout=1
        )


def test_o_adaptador_real_tambem_nao_chega_a_caixa(caixa):
    """Restaurar o adaptador sem dizer o que ele ouve não abre a porta: a recusa vem do vigia."""
    caixa.pela_rede()
    with pytest.raises(pytest.fail.Exception, match="FR-3651"):
        LoteriaFederal().consultar_ultimo()


def test_o_padrao_responde_ainda_nao_realizado_ao_que_a_suite_declara(caixa):
    """`5900`, `5901` e `6113` estão em dezenas de casos; nenhum vira "realizado" (plan, §8)."""
    situacoes = LoteriaFederal().conferir_referencias(
        ["5900", "5901", "6113", "9999"], fonte="Loteria Federal", agora=AGORA
    )
    assert {situacao.estado for situacao in situacoes.values()} == {dominio.AINDA_NAO_REALIZADO}
    assert caixa.chamadas_ao_ultimo == 1
    assert caixa.chamadas_por_numero == []
