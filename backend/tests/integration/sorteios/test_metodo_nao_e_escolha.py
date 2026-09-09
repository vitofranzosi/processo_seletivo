"""O sorteio consome o método que a relação comprometeu — e não recebe método (FR-067, D-014).

**A fresta que este arquivo fecha.** Relação e método chegavam ao ato como escolhas independentes.
Como métodos diferentes apontam ocorrências diferentes — logo, sementes diferentes —, a comissão
podia declarar vários, esperar a semente de cada um e escolher o conveniente. Fechar a escolha da
relação sozinha não bastava.
"""

import inspect

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados, Sorteio
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

# **Este arquivo usava `5930` onde o Edital declara `5900`, e passava.** Era o sintoma do defeito
# que a revisão encontrou: a ocorrência chegava por identidade, e fonte e referência nunca eram
# comparadas com o método congelado. Agora o comando recusa, e a fixture usa a declarada.

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def test_o_comando_do_sorteio_nao_tem_parametro_de_metodo():
    """A assinatura é a garantia: não há por onde passar um método (FR-067)."""
    parametros = set(inspect.signature(constituir_sorteio).parameters)

    assert "metodo" not in parametros
    assert "metodo_hash" not in parametros
    assert "drawMethod" not in parametros
    assert "relacao_id" in parametros, "o método vem por ela, e só por ela"


def test_o_sorteio_grava_o_metodo_que_a_relacao_comprometeu(certame):
    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="metodo-relacao",
            correlation_id="teste-021",
        )["relacao"]
    )
    ocorrencia = OcorrenciaDaFonte.objects.get(
        pk=observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="metodo-ocorrencia",
            correlation_id="teste-021",
            fonte_externa=FonteDeTeste(),
        )["ocorrencia"]
    )

    declarado = constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao.id,
        ocorrencia_id=ocorrencia.id,
        idempotency_key="metodo-sorteio",
        correlation_id="teste-021",
    )

    sorteio = Sorteio.objects.get(pk=declarado["sorteio"])
    assert sorteio.metodo_hash == relacao.metodo_hash == canonical_sha256(METODO)


def test_o_sorteio_e_recusado_quando_a_versao_citada_nao_contem_o_metodo_comprometido(certame):
    """O universo se comprometeu com um método, e é aquele que roda (FR-067)."""
    from processo_seletivo.sorteios.domain.metodo import conferir_compromisso

    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="divergente-relacao",
            correlation_id="teste-021",
        )["relacao"]
    )

    with pytest.raises(DomainError, match="draw_method_mismatch"):
        conferir_compromisso(
            relacao.versao.content,
            perfil_id=relacao.perfil_id,
            marco_id=relacao.marco_id,
            metodo_hash="f" * 64,
        )


def test_a_relacao_congelada_continua_citando_o_metodo_de_entao(certame, api_client):
    """Retificar o método vale para o que vier; não alcança relação já congelada (D-013)."""
    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="retificado-relacao",
        correlation_id="teste-021",
    )
    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])
    resumo_de_entao = relacao.metodo_hash

    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        certame["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={certame['perfil']}"
                    f"/classificationMilestones/id={certame['marco']}/drawMethod/substitutionRule"
                ),
                "operation": "REPLACE",
                "newValue": {
                    "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
                    "text": "vale a extração da semana seguinte",
                },
            }
        ],
    )

    relacao.refresh_from_db()
    assert relacao.metodo_hash == resumo_de_entao, "a relação congelada não muda de método"
