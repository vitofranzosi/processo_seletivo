"""Negar por padrão: quem convoca precisa de permissão explícita e de escopo (019, `FR-271`).

**A mesma resposta para tudo que o ator não alcança.** Recusar com *"existe, mas você não pode"* já
entregaria que existe — e o que existe aqui é quem está sendo chamado para uma vaga. A recusa é
`404` em todos os casos, e é a decisão que a `011` tomou por escrito (`D-017`).

**A autoridade é consumida, e não inventada.** Convocar usa a mesma base da emissão da ordem, do
corte e da apuração: nenhum Edital da amostra distingue quem convoca de quem publica o resultado, e
uma capacidade nova aqui inventaria uma distinção que a norma não tem.
"""

import pytest

from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.convocacao import convocar

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def alguem(cenario):
    """Quem o cenário permitiria convocar — para que a recusa seja de autorização, e não de fila."""
    from processo_seletivo.convocacao.application import selectors
    from tests.fixtures.corte import MARCO
    from tests.fixtures.edital import PROFILE_ID

    edital, _, _ = cenario
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return contexto["fila"][0]


def test_o_gestor_da_comissao_convoca(cenario, gestor, alguem):
    """O caminho positivo, para que as recusas abaixo não passem por acidente.

    **Sem este teste, um erro de cenário faria os quatro seguintes verdes pela razão errada**: eles
    conferem que um `404` acontece, e `404` também é o que um cenário quebrado produz.
    """
    edital, _, _ = cenario

    assert convocar(edital, gestor, alguem, idempotency_key="autorizado")


def test_ator_sem_permissao_nenhuma_recebe_404(cenario, sem_nada, alguem):
    edital, _, _ = cenario

    with pytest.raises(DomainError) as erro:
        convocar(edital, sem_nada, alguem, idempotency_key="sem-permissao")

    assert erro.value.code == "not_found"
    assert erro.value.status == 404


def test_ator_com_outra_permissao_recebe_404(cenario, auditor, alguem):
    """**Consultar a auditoria não autoriza convocar**, e a recusa não diz qual permissão falta.

    Dizer qual faltou é um mapa para quem está tentando descobrir o que existe.
    """
    edital, _, _ = cenario

    with pytest.raises(DomainError) as erro:
        convocar(edital, auditor, alguem, idempotency_key="outra-permissao")

    assert erro.value.code == "not_found"


def test_ator_de_outro_escopo_institucional_recebe_404(cenario, alguem):
    """**Escopo é verificado, e não só permissão** (Princípio III).

    Um gestor de outra instituição tem a permissão certa e não tem nada a ver com este Processo. É
    o caso que uma verificação só por permissão deixaria passar inteiro.
    """
    edital, _, _ = cenario
    de_fora = ator_institucional("carlos", "comissao:gerir", escopo="outra-instituicao")

    with pytest.raises(DomainError) as erro:
        convocar(edital, de_fora, alguem, idempotency_key="outro-escopo")

    assert erro.value.code == "not_found"


def test_ator_ausente_recebe_404(cenario, alguem):
    """Nenhum caminho desta feature convoca sem ator — nem por chamada interna."""
    edital, _, _ = cenario

    with pytest.raises(DomainError) as erro:
        convocar(edital, None, alguem, idempotency_key="sem-ator")

    assert erro.value.code == "not_found"


def test_a_recusa_de_autorizacao_nao_grava_convocacao(cenario, sem_nada, alguem):
    """**Negar por padrão inclui não deixar rastro do que foi tentado no agregado.**

    A trilha de segurança registra a tentativa; a tabela de convocações não pode ter linha nenhuma,
    porque uma convocação gravada e depois recusada seria um ato praticado sem autoridade.
    """
    from processo_seletivo.convocacao.models import Convocacao

    edital, _, _ = cenario

    with pytest.raises(DomainError):
        convocar(edital, sem_nada, alguem, idempotency_key="nao-grava")

    assert not Convocacao.objects.filter(edital=edital).exists()
