"""RC-62: a Mesa recusa concluir avaliação de quem já tem Resultado na Etapa.

**Decidido pelo usuário em 28/09** (`doc/registro-pre-piloto-2026-09-28.md`, *O que foi
decidido*). Antes, a conclusão tardia passava: não alterava o Resultado, que é imutável, ficava
inelegível e deixava na trilha a avaliação dizendo uma coisa e o Resultado outra. O caso comum é o
deste arquivo — a presidência registra que alguém faltou, e o avaliador conclui depois.

**A exceção é a reavaliação determinada por recurso, ainda pendente** (018, `FR-066`, `FR-068`), e
ela está provada onde já estava: `tests/integration/resultados/test_reavaliacao.py`, em
`test_a_inscricao_e_distribuivel_e_avaliavel_pelas_operacoes_existentes` e no cumprimento que o
segue — os dois concluem sobre um par que tem Resultado vigente, e continuam passando.
"""

import pytest

from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    montado = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1262, codigo="1262"
    )
    montado["inscricoes"] = inscrever(montado["edital"], 2, primeiro=1)
    return montado


def test_depois_da_ocorrencia_a_conclusao_e_recusada_dizendo_o_caminho(cenario, gestor):
    faltante, presente = cenario["inscricoes"]
    distribuir_para(cenario, gestor, ["joao"], [faltante, presente], chave="lote-1262")
    registrar_ocorrencia(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[faltante.id],
        motivo="não compareceu",
        idempotency_key="o-1262",
        correlation_id="rc-62",
    )

    with pytest.raises(DomainError) as recusa:
        concluir_como(cenario, "joao", faltante, pontuacao="75")

    # O quê, por quê e o que fazer — e a inscrição nomeada, com o Resultado que a protege.
    assert recusa.value.code == "inscricao_ja_tem_resultado"
    assert recusa.value.status == 409
    assert (faltante.protocolo or str(faltante.id)) in recusa.value.detail
    assert "não mudaria o Resultado" in recusa.value.detail
    assert "o caminho é o recurso" in recusa.value.detail
    assert not Avaliacao.objects.filter(
        inscricao_id=faltante.id, estado=Avaliacao.Estado.CONCLUIDA
    ).exists()

    # Quem não tem Resultado na Etapa continua sendo avaliado como antes.
    avaliacao = concluir_como(cenario, "joao", presente, pontuacao="75")
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
