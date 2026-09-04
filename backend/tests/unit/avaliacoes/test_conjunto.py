"""Distribuir exige o conjunto de inscrições fechado (E2E-017).

A regra é pura — lê o conteúdo publicado e o instante, e nada mais —, e é aqui que ela se
verifica. O que a wiring nos dois caminhos de distribuição garante está em
`tests/integration/avaliacoes/test_conjunto_fechado.py`.
"""

from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.avaliacoes.domain.conjunto import (
    conjunto_fechado,
    recusa_por_inscricoes_em_curso,
)

AGORA = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.get_fixed_timezone(-180))


def cronograma(*, inicio, fim=None, designado=True):
    evento = {
        "id": "00000000-0000-0000-0000-000000000402",
        "type": "INSCRICAO",
        "startAt": inicio.isoformat(),
        "order": 1,
        "isRegistrationPeriod": designado,
    }
    if fim is not None:
        evento["endAt"] = fim.isoformat()
    return {"schedule": [evento]}


def test_periodo_aberto_recusa_e_diz_ate_quando():
    """A recusa precisa dizer quando o conjunto fecha: "não pode" sozinho não tem saída."""
    conteudo = cronograma(inicio=AGORA - timedelta(days=2), fim=AGORA + timedelta(days=3))

    recusa = recusa_por_inscricoes_em_curso(conteudo, AGORA)

    assert not conjunto_fechado(conteudo, AGORA)
    assert recusa is not None
    assert "07/09/2026" in str(recusa.detail)
    assert "sem avaliador quem se inscrever depois" in str(recusa.detail)


def test_periodo_aberto_sem_termino_recusa_sem_inventar_prazo():
    """Sem término declarado o Edital não fixou prazo, e o sistema não pode fixá-lo por ele."""
    conteudo = cronograma(inicio=AGORA - timedelta(days=2))

    recusa = recusa_por_inscricoes_em_curso(conteudo, AGORA)

    assert recusa is not None
    assert "não declarou término" in str(recusa.detail)


def test_periodo_futuro_recusa_porque_o_conjunto_sequer_comecou():
    conteudo = cronograma(inicio=AGORA + timedelta(days=1), fim=AGORA + timedelta(days=5))

    recusa = recusa_por_inscricoes_em_curso(conteudo, AGORA)

    assert recusa is not None
    assert "ainda não começou" in str(recusa.detail)


def test_periodo_encerrado_admite_distribuir():
    conteudo = cronograma(inicio=AGORA - timedelta(days=9), fim=AGORA - timedelta(days=1))

    assert conjunto_fechado(conteudo, AGORA)
    assert recusa_por_inscricoes_em_curso(conteudo, AGORA) is None


def test_sem_evento_designado_a_regra_nao_se_aplica():
    """Ausência de prazo não é prazo aberto: o Edital não recebe inscrição por este sistema."""
    conteudo = cronograma(inicio=AGORA - timedelta(days=2), designado=False)

    assert conjunto_fechado(conteudo, AGORA)
    assert recusa_por_inscricoes_em_curso(conteudo, AGORA) is None


@pytest.mark.parametrize("conteudo", [{}, {"schedule": []}, {"schedule": [{}]}])
def test_conteudo_sem_cronograma_nao_bloqueia(conteudo):
    assert recusa_por_inscricoes_em_curso(conteudo, AGORA) is None
