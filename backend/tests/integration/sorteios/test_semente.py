"""Nenhum caminho aceita semente, e a indisponibilidade não abre digitação (FR-017, FR-018).

**A garantia não é uma validação.** Não existe campo de semente a validar: a assinatura dos comandos
não tem parâmetro para ela, a tela não tem entrada, e a semente nasce da normalização do material
que a fonte publicou. É isso que o teste afirma — a ausência do caminho, e não a rejeição dele.
"""

import inspect

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application import ocorrencia as comando_da_ocorrencia
from processo_seletivo.sorteios.application import relacao as comando_da_relacao
from processo_seletivo.sorteios.application import sorteio as comando_do_sorteio
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados
from tests.fixtures.sorteio import certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

PROIBIDOS = ("semente", "seed", "ordem", "posicao", "chave_do_participante")

COMANDOS = (
    comando_da_relacao.publicar_relacao,
    comando_da_ocorrencia.observar_ocorrencia,
    comando_do_sorteio.constituir_sorteio,
    comando_do_sorteio.anular_sorteio,
)


@pytest.mark.parametrize("comando", COMANDOS, ids=lambda c: c.__name__)
def test_nenhum_comando_aceita_semente_nem_ordem(comando):
    """A assinatura **é** a garantia: não há parâmetro por onde a semente entre."""
    parametros = set(inspect.signature(comando).parameters)

    assert not (parametros & set(PROIBIDOS)), sorted(parametros & set(PROIBIDOS))
    assert "idempotency_key" in parametros, "todo comando é idempotente"


class FonteIndisponivel:
    def observar(self, *, fonte, referencia):
        return Observacao(
            indisponivel=True,
            evidencia=f"Concurso {referencia} de {fonte}: sem extração publicada na data.",
        )


class FonteSemEvidencia:
    def observar(self, *, fonte, referencia):
        return Observacao(indisponivel=True, evidencia="")


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def test_a_indisponibilidade_e_registrada_com_evidencia_e_nao_abre_digitacao(certame):
    declarado = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte="Loteria Federal",
        referencia="5901",
        idempotency_key="indisponivel-1",
        correlation_id="teste-021",
        fonte_externa=FonteIndisponivel(),
    )

    ocorrencia = OcorrenciaDaFonte.objects.get(pk=declarado["ocorrencia"])
    assert ocorrencia.indisponivel is True
    assert "sem extração publicada" in ocorrencia.evidencia
    assert ocorrencia.material_bruto == ""


def test_indisponibilidade_sem_evidencia_e_recusada(certame):
    """Afirmar indisponibilidade sem lastro seria acionar a substituição sem motivo (R-006)."""
    with pytest.raises(DomainError, match="source_unavailable_without_evidence"):
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte="Loteria Federal",
            referencia="5902",
            idempotency_key="sem-evidencia-1",
            correlation_id="teste-021",
            fonte_externa=FonteSemEvidencia(),
        )


def test_a_ocorrencia_indisponivel_nao_sorteia(certame):
    """A regra publicada diz qual ocorrência a substitui; observar aquela é o caminho."""
    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="indisponivel-relacao",
            correlation_id="teste-021",
        )["relacao"]
    )
    ocorrencia = OcorrenciaDaFonte.objects.get(
        pk=observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte="Loteria Federal",
            referencia="5903",
            idempotency_key="indisponivel-2",
            correlation_id="teste-021",
            fonte_externa=FonteIndisponivel(),
        )["ocorrencia"]
    )

    with pytest.raises(DomainError, match="occurrence_unavailable"):
        constituir_sorteio(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            relacao_id=relacao.id,
            ocorrencia_id=ocorrencia.id,
            idempotency_key="indisponivel-3",
            correlation_id="teste-021",
        )


def test_toda_observacao_fica_registrada_inclusive_a_que_nao_vira_sorteio(certame):
    """É o controle que torna visível o descarte de ocorrência (R-006)."""
    for indice, referencia in enumerate(("5910", "5911", "5912")):
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte="Loteria Federal",
            referencia=referencia,
            idempotency_key=f"descarte-{indice}",
            correlation_id="teste-021",
            fonte_externa=FonteDeTeste(),
        )

    assert OcorrenciaDaFonte.objects.count() == 3, "nenhuma observação some por não ter virado ato"


def test_observar_duas_vezes_devolve_a_mesma_linha(certame):
    """Idempotência por `(fonte, referência)`: reobservar não permite trocar o material bruto."""
    primeira = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte="Loteria Federal",
        referencia="5920",
        idempotency_key="idem-1",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )

    class OutroMaterial:
        def observar(self, *, fonte, referencia):
            return Observacao(material_bruto="99999 99999 99999 99999 99999")

    segunda = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte="Loteria Federal",
        referencia="5920",
        idempotency_key="idem-2",
        correlation_id="teste-021",
        fonte_externa=OutroMaterial(),
    )

    assert segunda["ocorrencia"] == primeira["ocorrencia"]
    assert segunda["materialBruto"] == primeira["materialBruto"]
    assert OcorrenciaDaFonte.objects.count() == 1
