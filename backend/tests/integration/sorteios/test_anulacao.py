"""Anular **é** constituir o sucessor — e não existe "refazer" (FR-052..FR-055).

**A diferença não é de palavra.** Refazer repetiria o cálculo sobre as mesmas entradas até o
resultado agradar; anular constitui um ato **novo**, com relação nova e ocorrência nova, e deixa o
anterior íntegro, legível e verificável. É por isso que o comando de anulação chama o de
constituição, e não um caminho próprio: se houvesse um caminho próprio, ele seria o refazer.
"""

import inspect

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application import sorteio as modulo_do_sorteio
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import anular_sorteio
from processo_seletivo.sorteios.application.verificacao import verificar
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio
from tests.unit.sorteios.test_manifesto import sorteado  # noqa: F401 — fixture compartilhada

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


class OutraExtracao:
    def observar(self, *, fonte, referencia):
        return Observacao(material_bruto="55555 44444 33333 22222 11111")


def _sucessor(certame, sorteio, *, motivo="Vício reconhecido na condução do ato."):
    """Relação nova, ocorrência nova, e o ato novo ligado ao anterior (FR-054)."""
    relacao_nova = publicar_relacao(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="anular-relacao",
        correlation_id="teste-021",
        motivo="Relação nova para o sorteio sucessor.",
    )["relacao"]
    ocorrencia_nova = observar_ocorrencia(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        fonte="Loteria Federal",
        referencia="5901",
        idempotency_key="anular-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=OutraExtracao(),
    )["ocorrencia"]
    return anular_sorteio(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        sorteio_anterior_id=sorteio.id,
        relacao_id=relacao_nova,
        ocorrencia_id=ocorrencia_nova,
        motivo=motivo,
        idempotency_key="anular-sorteio",
        correlation_id="teste-021",
    )


def _presidente():
    from tests.fixtures.sorteio import presidente

    return presidente()


def test_nao_existe_comando_de_refazer():
    """A ausência é a garantia: nenhum nome público do módulo repete um sorteio."""
    publicos = [nome for nome in dir(modulo_do_sorteio) if not nome.startswith("_")]

    for nome in publicos:
        assert "refazer" not in nome.lower()
        assert "reexecutar" not in nome.lower()
        assert "repetir" not in nome.lower()


def test_anular_delega_a_constituicao_e_nao_tem_caminho_proprio():
    """Se tivesse caminho próprio, ele seria o refazer que a FR-052 proíbe."""
    fonte = inspect.getsource(modulo_do_sorteio.anular_sorteio)

    assert "constituir_sorteio(" in fonte
    assert "Sorteio.objects.create" not in fonte
    assert "delete" not in fonte


def test_a_anulacao_exige_motivo(sorteado):  # noqa: F811
    certame, sorteio = sorteado

    with pytest.raises(DomainError, match="draw_annulment_reason_required"):
        _sucessor(certame, sorteio, motivo="   ")


def test_o_sucessor_nasce_de_relacao_nova_e_ocorrencia_nova(sorteado):  # noqa: F811
    certame, sorteio = sorteado

    declarado = _sucessor(certame, sorteio)

    novo = Sorteio.objects.get(pk=declarado["sorteio"])
    assert novo.sorteio_anterior_id == sorteio.id
    assert novo.relacao_id != sorteio.relacao_id
    assert novo.ocorrencia_id != sorteio.ocorrencia_id
    assert novo.motivo_da_anulacao


def test_os_dois_coexistem_e_o_anulado_continua_integro_e_verificavel(sorteado):  # noqa: F811
    certame, sorteio = sorteado

    _sucessor(certame, sorteio)

    assert Sorteio.objects.count() == 2
    anulado = Sorteio.objects.get(pk=sorteio.pk)
    assert verificar(anulado)["integro"] is True, "o ato anulado continua conferindo"
    assert anulado.manifesto_hash and anulado.semente_normalizada


def test_a_relacao_do_sorteio_anulado_permanece_legivel(sorteado):  # noqa: F811
    certame, sorteio = sorteado
    resumo_de_entao = sorteio.relacao.resumo

    _sucessor(certame, sorteio)

    anterior = RelacaoDeHabilitados.objects.get(pk=sorteio.relacao_id)
    assert anterior.resumo == resumo_de_entao
    assert anterior.sucessoras.exists(), "sucedida, e não apagada"
