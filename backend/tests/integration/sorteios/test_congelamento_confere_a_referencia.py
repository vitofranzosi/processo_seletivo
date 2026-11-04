"""O congelamento confere o concurso declarado na Caixa (116, US2, FR-3636, FR-3637).

**O comando confere, e não só a prévia** (5ª decisão do usuário): congelar é append-only, e a
relação congelada sob concurso já realizado nunca sorteia. O Edital é publicado com a Caixa da
suíte dizendo "ainda não realizado", e a Caixa muda de resposta antes do congelamento — o cenário C.
"""

import copy
from datetime import date, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.relacao import PUBLICAR, publicar_relacao
from processo_seletivo.sorteios.domain import conferencia as dominio
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados
from tests.fixtures.legado import antes_da_116
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

LF = "Loteria Federal"


def _metodo(ocorrencia="6115"):
    metodo = copy.deepcopy(METODO)
    metodo.update(
        {
            "source": LF,
            "occurrence": ocorrencia,
            "occurrenceAt": (timezone.now() + timedelta(days=10)).isoformat(),
        }
    )
    return metodo


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, caixa):
    montado = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=_metodo()
    )
    caixa.zerar()
    return montado


def _congelar(certame, *, chave="congelar-116", motivo=""):
    return publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key=chave,
        correlation_id="teste-116",
        motivo=motivo,
    )


def _registro(relacao_id):
    return RegistroAuditoria.objects.get(operation=PUBLICAR, aggregate_id=relacao_id)


def test_realizado_no_congelamento_e_recusado_sem_gravar_relacao(certame, caixa):
    """Cenário C: publicado sob "ainda não realizado", realizado antes do congelamento."""
    caixa.usar_gravacao().realizado_ate(6115, date(2026, 11, 5))

    with pytest.raises(DomainError) as recusa:
        _congelar(certame)

    assert recusa.value.code == "draw_occurrence_already_drawn"
    assert recusa.value.status == 409
    for parte in ("Não é possível congelar", "6115", "05/11/2026", "retifique", "só então"):
        assert parte in recusa.value.detail
    assert not RelacaoDeHabilitados.objects.filter(edital=certame["edital"]).exists()
    assert caixa.chamadas_ao_ultimo == 1


def test_congela_com_o_registro(certame, caixa):
    caixa.usar_gravacao()

    declarado = _congelar(certame)

    assert "advertencias" not in declarado
    (registro,) = _registro(declarado["relacao"]).detalhe["conferenciaDaReferencia"]
    assert (registro["referencia"], registro["situacao"]) == ("6115", dominio.AINDA_NAO_REALIZADO)
    assert registro["decisao"] == "PROSSEGUIU"
    assert registro["ultimo"] == 6114
    assert caixa.chamadas_ao_ultimo == 1


def test_inconclusivo_congela_e_devolve_a_advertencia(certame, caixa):
    caixa.fora_do_ar(dominio.SEM_CONEXAO)

    declarado = _congelar(certame)

    (advertencia,) = declarado["advertencias"]
    assert "não foi possível falar com a Caixa" in advertencia
    assert "A relação foi publicada." in advertencia
    (registro,) = _registro(declarado["relacao"]).detalhe["conferenciaDaReferencia"]
    assert (registro["conclusiva"], registro["decisao"]) == (False, "PROSSEGUIU_COM_ADVERTENCIA")


def test_com_a_declarada_indisponivel_a_conferencia_se_cala(certame, caixa):
    """A substituta é a da vez, e não tem instante publicado: como a `102` faz (FR-3636)."""
    OcorrenciaDaFonte.objects.create(
        fonte=LF,
        referencia="6115",
        indisponivel=True,
        evidencia="Concurso 6115: sem extração publicada.",
        observada_em=timezone.now(),
        observada_por="maria",
    )
    caixa.usar_gravacao().realizado_ate(6115, date(2026, 11, 5))

    declarado = _congelar(certame)

    assert declarado["relacao"]
    assert caixa.chamadas == 0
    assert _registro(declarado["relacao"]).detalhe is None


def test_forma_do_acervo_congela_com_advertencia(
    gestor, api_client, manager_headers, process_payload, caixa
):
    """`Concurso 6100` foi publicado antes desta feature: adverte, e não recusa (D-005)."""
    # O acervo: publicado quando a forma da Loteria Federal ainda não era conferida (FR-3720).
    with antes_da_116():
        acervo = certame_de_sorteio(
            gestor, api_client, manager_headers, process_payload, metodo=_metodo("Concurso 6100")
        )
    caixa.zerar()

    declarado = _congelar(acervo)

    (advertencia,) = declarado["advertencias"]
    assert '"Concurso 6100"' in advertencia
    assert "Retifique o método antes do dia do sorteio" in advertencia
    assert caixa.chamadas == 0


def test_a_caixa_muda_a_resposta_e_nada_gravado_muda(certame, caixa):
    """Cenário H: a conferência só vale no ato em que roda; o que foi gravado não se reconfere."""
    caixa.usar_gravacao()
    relacao = RelacaoDeHabilitados.objects.get(pk=_congelar(certame)["relacao"])
    gravada = (relacao.resumo, relacao.metodo_hash, relacao.quantidade)

    caixa.realizado_ate(6115, date(2026, 11, 5))

    relacao.refresh_from_db()
    assert (relacao.resumo, relacao.metodo_hash, relacao.quantidade) == gravada
    assert RelacaoDeHabilitados.objects.filter(edital=certame["edital"]).count() == 1
    # A sucessão é outro congelamento, e confere de novo: agora ela recusa.
    with pytest.raises(DomainError) as recusa:
        _congelar(certame, chave="suceder-116", motivo="Inscrição homologada depois.")
    assert recusa.value.code == "draw_occurrence_already_drawn"


def test_a_repeticao_nao_consulta_de_novo(certame, caixa):
    primeiro = _congelar(certame)
    repetido = _congelar(certame)
    assert repetido == primeiro
    assert caixa.chamadas_ao_ultimo == 1
