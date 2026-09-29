"""A relação só se congela com o período de inscrições encerrado (021, US1, cenário 1).

**O achado** (`doc/achado-relacao-do-sorteio-congela-com-inscricoes-abertas.md`). No ensaio do
teste operacional de 27/09/2026, a relação de "Todos os inscritos" foi congelada às 18h57 de um
período que ia até 19h20. Quem se inscrevesse depois ficava fora do universo do sorteio, e a única
saída era um segundo ato público — a relação sucessora, com motivo escrito — para corrigir o
primeiro.

A `021` abre a US1 por *"Encerradas as inscrições, quem conduz o certame publica a relação"*, e o
cenário 1 parte de *"período encerrado"*. A regra é a que a distribuição já aplica, lida da mesma
função (`avaliacoes/domain/conjunto.py`): as duas partem do mesmo fato, o universo de inscrições.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.previa import recortes_do_marco
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.models import RelacaoDeHabilitados
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import encerrar_inscricoes
from tests.fixtures.sorteio import MARCO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def aberto(gestor, api_client, manager_headers, process_payload):
    """Um Edital de sorteio publicado com o período de inscrições **correndo**, e três inscritos."""
    return certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, periodo_aberto=True
    )["edital"]


def _publicar(edital, *, chave="relacao-periodo"):
    return publicar_relacao(
        actor=presidente(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-021-periodo",
    )


def test_congelar_com_o_periodo_correndo_e_recusado_e_diz_o_que_fazer(aberto):
    with pytest.raises(DomainError) as recusa:
        _publicar(aberto)

    assert recusa.value.code == "inscricoes_em_curso"
    assert recusa.value.status == 409
    detalhe = str(recusa.value.detail)
    assert "As inscrições ficam abertas até" in detalhe, "diz até quando esperar"
    assert "deixaria fora do sorteio quem se inscrever depois" in detalhe, "diz o que perderia"
    assert "publique-a depois do término" in detalhe, "diz o que fazer"
    assert "Antecipar o término publicado é ato de Retificação" in detalhe, "e a outra saída"
    assert not RelacaoDeHabilitados.objects.filter(edital=aberto).exists()


def test_a_tela_recebe_a_mesma_recusa_antes_do_clique(aberto):
    """A prévia carrega a recusa que a publicação levantaria — a mesma, da mesma função."""
    estado = recortes_do_marco(edital=aberto, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert estado["inscricoes_em_curso"] is not None
    assert estado["inscricoes_em_curso"].code == "inscricoes_em_curso"


def test_encerrado_o_periodo_a_relacao_se_congela(aberto, api_client):
    """A contraprova: a recusa espera o fechamento, e não impede o ato."""
    edital = encerrar_inscricoes(api_client, aberto, timezone.now() - timedelta(minutes=1))

    declarado = _publicar(edital)

    assert declarado["quantidade"] == 3
    assert (
        recortes_do_marco(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
            "inscricoes_em_curso"
        ]
        is None
    )
