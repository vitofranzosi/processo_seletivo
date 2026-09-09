"""A ocorrência é a declarada — ou a que a regra publicada põe no lugar (021, FR-072, FR-073).

**Os dois defeitos que este arquivo fecha, e que passaram pela suíte anterior.**

A ocorrência chegava ao comando por identidade, e `fonte` e `referencia` nunca eram comparadas com o
método congelado: bastava outro UUID para sortear com uma extração que ninguém publicou. Um teste
até usava `5930` onde o Edital declarava `5900`, e passava — consolidando o defeito.

E a precedência era medida pelo instante da **leitura**, e não pelo da ocorrência: dava para ver a
extração na televisão, congelar a relação depois e registrar o resultado em seguida.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


class Extracao:
    """Uma fonte que publica a extração e **diz quando ela aconteceu**."""

    def __init__(self, *, ocorrida_em=None, material="12345 67890 11223 44556 77889"):
        self.ocorrida_em = ocorrida_em
        self.material = material

    def observar(self, *, fonte, referencia):
        return Observacao(
            material_bruto=self.material, ocorrida_em=self.ocorrida_em or timezone.now()
        )


class SemData:
    def observar(self, *, fonte, referencia):
        return Observacao(material_bruto="1 2 3 4 5", ocorrida_em=None)


class Indisponivel:
    def observar(self, *, fonte, referencia):
        return Observacao(
            indisponivel=True, evidencia=f"Concurso {referencia}: sem extração publicada."
        )


@pytest.fixture
def congelado(gestor, api_client, manager_headers, process_payload):
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)
    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="declarada-relacao",
            correlation_id="teste-021",
        )["relacao"]
    )
    return certame, relacao


def _observar(certame, referencia, fonte_externa, *, chave="obs"):
    return OcorrenciaDaFonte.objects.get(
        pk=observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=referencia,
            idempotency_key=f"{chave}-{referencia}",
            correlation_id="teste-021",
            fonte_externa=fonte_externa,
        )["ocorrencia"]
    )


def _constituir(certame, relacao, ocorrencia, *, chave="constituir"):
    return constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao.id,
        ocorrencia_id=ocorrencia.id,
        idempotency_key=chave,
        correlation_id="teste-021",
    )


def test_uma_ocorrencia_que_o_edital_nao_declara_e_recusada(congelado):
    """O ataque direto: registrar outra extração e passar o UUID dela ao comando."""
    certame, relacao = congelado
    outra = _observar(certame, "5930", Extracao())

    with pytest.raises(DomainError, match="occurrence_not_declared"):
        _constituir(certame, relacao, outra)


def test_uma_fonte_que_o_edital_nao_declara_e_recusada(congelado):
    certame, relacao = congelado
    de_outra_fonte = OcorrenciaDaFonte.objects.create(
        fonte="Sorteio da casa",
        referencia=METODO["occurrence"],
        material_bruto="1 1 1 1 1",
        ocorrida_em=timezone.now(),
        observada_em=timezone.now(),
        observada_por="cpf:presidente",
    )

    with pytest.raises(DomainError, match="occurrence_not_declared"):
        _constituir(certame, relacao, de_outra_fonte)


def test_a_ocorrencia_declarada_e_aceita(congelado):
    certame, relacao = congelado
    declarada = _observar(certame, METODO["occurrence"], Extracao())

    declarado = _constituir(certame, relacao, declarada)

    assert declarado["quantidade"] == relacao.quantidade


def test_uma_extracao_anterior_ao_congelamento_e_recusada_mesmo_lida_depois(congelado):
    """**A garantia que era contornável**: ver o resultado, congelar, e só então registrar."""
    certame, relacao = congelado
    antiga = _observar(
        certame,
        METODO["occurrence"],
        Extracao(ocorrida_em=relacao.publicada_em - timedelta(hours=1)),
    )

    assert antiga.observada_em > relacao.publicada_em, "a leitura é posterior, e não basta"
    with pytest.raises(DomainError, match="occurrence_precedes_freeze"):
        _constituir(certame, relacao, antiga)


def test_uma_ocorrencia_sem_data_nao_semeia_sorteio(congelado):
    """Sem saber quando o evento aconteceu, não há como afirmar precedência (FR-016)."""
    certame, relacao = congelado
    sem_data = _observar(certame, METODO["occurrence"], SemData())

    with pytest.raises(DomainError, match="occurrence_without_instant"):
        _constituir(certame, relacao, sem_data)


def test_a_regra_de_substituicao_desloca_a_referencia_admissivel(congelado):
    """Indisponível a declarada, a **seguinte** passa a ser a admissível — e só ela (FR-015)."""
    certame, relacao = congelado
    _observar(certame, METODO["occurrence"], Indisponivel())
    substituta = _observar(certame, "5901", Extracao(), chave="sub")

    declarado = _constituir(certame, relacao, substituta)

    assert declarado["quantidade"] == relacao.quantidade


def test_a_substituta_nao_e_admissivel_enquanto_a_declarada_estiver_disponivel(congelado):
    """A regra não é um menu: pular a declarada seria escolher a extração."""
    certame, relacao = congelado
    salto = _observar(certame, "5901", Extracao(), chave="salto")

    with pytest.raises(DomainError, match="occurrence_not_declared"):
        _constituir(certame, relacao, salto)


def test_a_cadeia_de_substituicao_e_finita_e_a_recusa_nomeia_o_ato_que_falta(congelado):
    """Fonte permanentemente fora do ar não faz o sistema escolher outra por conta própria."""
    from processo_seletivo.sorteios.domain import substituicao

    certame, _relacao = congelado
    referencias = substituicao.cadeia(METODO)
    for indice, referencia in enumerate(referencias):
        _observar(certame, referencia, Indisponivel(), chave=f"esgotar-{indice}")

    with pytest.raises(DomainError, match="substitution_chain_exhausted"):
        substituicao.proxima_a_observar(METODO, set(referencias))
