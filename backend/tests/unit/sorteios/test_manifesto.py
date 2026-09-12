"""O manifesto é derivado, estável e sem dado pessoal indevido (FR-042..FR-044, R-007, SC-007)."""

import pytest

from processo_seletivo.shared.canonical import canonical_bytes
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.application.verificacao import manifesto_publicado
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import Sorteio
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def sorteado(gestor, api_client, manager_headers, process_payload):
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload, quantos=4)
    relacao_id = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="manifesto-relacao",
        correlation_id="teste-021",
    )["relacao"]
    ocorrencia_id = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="manifesto-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]
    declarado = constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao_id,
        ocorrencia_id=ocorrencia_id,
        idempotency_key="manifesto-sorteio",
        correlation_id="teste-021",
    )
    return certame, Sorteio.objects.get(pk=declarado["sorteio"])


def test_dois_downloads_produzem_bytes_identicos(sorteado):
    """Regra 4 do contrato: nada de vigente é lido, então nada muda entre dois downloads."""
    _certame, sorteio = sorteado

    primeiro = canonical_bytes(manifesto_publicado(sorteio))
    segundo = canonical_bytes(manifesto_publicado(sorteio))

    assert primeiro == segundo


def test_o_manifesto_traz_o_que_o_contrato_exige(sorteado):
    _certame, sorteio = sorteado

    manifesto = manifesto_publicado(sorteio)

    assert manifesto["manifestVersion"] == 1
    assert manifesto["drawId"] == str(sorteio.id)
    assert manifesto["relation"]["relationHash"] == sorteio.relacao.resumo
    assert manifesto["method"]["methodHash"] == sorteio.metodo_hash
    assert manifesto["seed"]["normalized"] == sorteio.semente_normalizada
    assert len(manifesto["participants"]) == sorteio.relacao.quantidade
    assert manifesto["manifestHash"] == sorteio.manifesto_hash


def test_os_participantes_saem_ordenados_por_numero_publico(sorteado):
    """Regra 2: quem confere lê a **entrada**, e não o resultado."""
    _certame, sorteio = sorteado

    numeros = [p["publicNumber"] for p in manifesto_publicado(sorteio)["participants"]]

    assert numeros == sorted(numeros)


def test_o_manifesto_nao_traz_cpf_nome_protocolo_nem_identificador_interno(sorteado):
    """FR-044 e SC-007: o participante é identificado por número público, e só."""
    certame, sorteio = sorteado

    bruto = canonical_bytes(manifesto_publicado(sorteio)).decode("utf-8")

    for inscricao in certame["inscricoes"]:
        assert str(inscricao.id) not in bruto
        assert inscricao.cpf_normalizado not in bruto
        assert inscricao.nome not in bruto
        assert inscricao.protocolo not in bruto
    for participante in manifesto_publicado(sorteio)["participants"]:
        assert sorted(participante) == ["key", "position", "publicNumber"]


def test_o_resumo_do_manifesto_cobre_o_objeto_sem_o_proprio_campo(sorteado):
    from processo_seletivo.sorteios.domain.manifesto import resumo_do_manifesto

    _certame, sorteio = sorteado
    manifesto = manifesto_publicado(sorteio)

    assert resumo_do_manifesto(manifesto) == manifesto["manifestHash"]
