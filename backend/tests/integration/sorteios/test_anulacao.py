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
from tests.fixtures.sorteio import METODO
from tests.unit.sorteios.test_manifesto import sorteado  # noqa: F401 — fixture compartilhada

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


class OutraExtracao:
    def observar(self, *, fonte, referencia):
        from django.utils import timezone

        return Observacao(
            material_bruto="55555 44444 33333 22222 11111", ocorrida_nao_antes_de=timezone.now()
        )


def _sucessor(certame, api_client, sorteio, *, motivo="Vício reconhecido na condução do ato."):
    """Relação nova, ocorrência nova, e o ato novo ligado ao anterior (FR-054).

    **A ocorrência nova exige Retificação, e isso não é burocracia acidental.** O Edital declara
    *qual* extração fixa a semente; um sucessor que usasse outra extração sem a norma dizê-lo
    estaria escolhendo a extração — que é a mesma fresta que a feature fecha em todos os outros
    lugares. Anular um sorteio público é ato normativo, e redizer sob que ocorrência ele se refaz é
    parte do ato.

    O efeito colateral é a garantia mais forte que esta feature tem: não existe "anular até gostar
    do resultado", porque cada refazimento custa uma Retificação publicada.
    """
    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        certame["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={certame['perfil']}"
                    f"/classificationMilestones/id={certame['marco']}/drawMethod/occurrence"
                ),
                "operation": "REPLACE",
                "newValue": "5901",
            },
            {
                "targetPath": (
                    f"/profiles/id={certame['perfil']}"
                    f"/classificationMilestones/id={certame['marco']}/drawMethod/derivation"
                ),
                "operation": "REPLACE",
                "newValue": "Concurso 5901: a extração seguinte, após a anulação do sorteio.",
            },
        ],
    )
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
        fonte=METODO["source"],
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


def test_a_anulacao_exige_motivo(sorteado, api_client):  # noqa: F811
    certame, sorteio = sorteado

    with pytest.raises(DomainError, match="draw_annulment_reason_required"):
        _sucessor(certame, api_client, sorteio, motivo="   ")


def test_o_sucessor_nasce_de_relacao_nova_e_ocorrencia_nova(sorteado, api_client):  # noqa: F811
    certame, sorteio = sorteado

    declarado = _sucessor(certame, api_client, sorteio)

    novo = Sorteio.objects.get(pk=declarado["sorteio"])
    assert novo.sorteio_anterior_id == sorteio.id
    assert novo.relacao_id != sorteio.relacao_id
    assert novo.ocorrencia_id != sorteio.ocorrencia_id
    assert novo.motivo_da_anulacao


def test_os_dois_coexistem_e_o_anulado_continua_integro_e_verificavel(sorteado, api_client):  # noqa: F811
    certame, sorteio = sorteado

    _sucessor(certame, api_client, sorteio)

    assert Sorteio.objects.count() == 2
    anulado = Sorteio.objects.get(pk=sorteio.pk)
    assert verificar(anulado)["integro"] is True, "o ato anulado continua conferindo"
    assert anulado.manifesto_hash and anulado.semente_normalizada


def test_a_relacao_do_sorteio_anulado_permanece_legivel(sorteado, api_client):  # noqa: F811
    certame, sorteio = sorteado
    resumo_de_entao = sorteio.relacao.resumo

    _sucessor(certame, api_client, sorteio)

    anterior = RelacaoDeHabilitados.objects.get(pk=sorteio.relacao_id)
    assert anterior.resumo == resumo_de_entao
    assert anterior.sucessoras.exists(), "sucedida, e não apagada"


def test_o_sucessor_nao_pode_reusar_a_relacao_do_anulado(sorteado, api_client):  # noqa: F811
    """Reusar a relação seria refazer o sorteio sobre o mesmo universo (FR-052)."""
    from processo_seletivo.sorteios.application.sorteio import anular_sorteio

    certame, sorteio = sorteado
    outra_ocorrencia = observar_ocorrencia(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia="5901",
        idempotency_key="reuso-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=OutraExtracao(),
    )["ocorrencia"]

    with pytest.raises(DomainError, match="draw_succession_reuses_relation"):
        anular_sorteio(
            actor=_presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            sorteio_anterior_id=sorteio.id,
            relacao_id=sorteio.relacao_id,
            ocorrencia_id=outra_ocorrencia,
            motivo="Vício qualquer.",
            idempotency_key="reuso-relacao",
            correlation_id="teste-021",
        )


def test_o_sucessor_nao_pode_reusar_a_ocorrencia_do_anulado(sorteado, api_client):  # noqa: F811
    """Reusar a semente produziria a mesma ordem, com outro número de ato (FR-054)."""
    from processo_seletivo.sorteios.application.sorteio import anular_sorteio

    certame, sorteio = sorteado
    relacao_nova = publicar_relacao(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="reuso-relacao-nova",
        correlation_id="teste-021",
        motivo="Relação nova.",
    )["relacao"]

    with pytest.raises(DomainError, match="draw_succession_reuses_occurrence"):
        anular_sorteio(
            actor=_presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            sorteio_anterior_id=sorteio.id,
            relacao_id=relacao_nova,
            ocorrencia_id=sorteio.ocorrencia_id,
            motivo="Vício qualquer.",
            idempotency_key="reuso-ocorrencia-chave",
            correlation_id="teste-021",
        )


def test_um_sorteio_ja_anulado_nao_se_anula_de_novo(sorteado, api_client):  # noqa: F811
    """A cadeia é linear: anula-se o vigente, e não um elo antigo."""
    from processo_seletivo.sorteios.application.sorteio import anular_sorteio

    certame, sorteio = sorteado
    _sucessor(certame, api_client, sorteio)

    # Insumos **reais** para uma terceira tentativa: o comando resolve relação e ocorrência antes
    # de olhar a cadeia, e identificadores inventados parariam num 404 que mediria outra coisa.
    relacao_terceira = publicar_relacao(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="terceira-relacao",
        correlation_id="teste-021",
        motivo="Terceira relação.",
    )["relacao"]
    ocorrencia_terceira = observar_ocorrencia(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia="5902",
        idempotency_key="terceira-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=OutraExtracao(),
    )["ocorrencia"]

    with pytest.raises(DomainError, match="draw_already_superseded"):
        anular_sorteio(
            actor=_presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            sorteio_anterior_id=sorteio.id,
            relacao_id=relacao_terceira,
            ocorrencia_id=ocorrencia_terceira,
            motivo="Segunda anulação do mesmo ato.",
            idempotency_key="dupla-anulacao",
            correlation_id="teste-021",
        )


def test_a_relacao_do_sucessor_precisa_suceder_a_do_anulado(sorteado, api_client):  # noqa: F811
    """Uma relação de outra cadeia deixaria o universo do sucessor sem ligação com o anulado."""
    from processo_seletivo.sorteios.application.sorteio import anular_sorteio
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados
    from tests.fixtures.sorteio import LISTA_PPI
    from tests.fixtures.sorteio import relacao as relacao_solta

    certame, sorteio = sorteado
    de_outra_cadeia = relacao_solta(
        certame["edital"],
        versao=sorteio.relacao.versao,
        perfil_id=certame["perfil"],
        lista_id=LISTA_PPI,
        inscricoes=list(certame["inscricoes"]),
        metodo_hash=sorteio.relacao.metodo_hash,
    )
    outra_ocorrencia = observar_ocorrencia(
        actor=_presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia="5901",
        idempotency_key="cadeia-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=OutraExtracao(),
    )["ocorrencia"]

    assert RelacaoDeHabilitados.objects.filter(pk=de_outra_cadeia.id).exists()
    with pytest.raises(
        DomainError, match="draw_succession_across_scopes|draw_succession_relation_not_linked"
    ):
        anular_sorteio(
            actor=_presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            sorteio_anterior_id=sorteio.id,
            relacao_id=de_outra_cadeia.id,
            ocorrencia_id=outra_ocorrencia,
            motivo="Vício qualquer.",
            idempotency_key="cadeia-errada",
            correlation_id="teste-021",
        )
