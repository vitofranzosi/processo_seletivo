"""A recusa por precedência diz o que fazer, e a comparação não muda (102, FR-2662–FR-2664).

**O que a recusa de 29/10 não dizia.** O operador do Edital 72/2026 leu que a fonte situava a
extração "a partir de 03:00" e foi investigar um horário que a Caixa nunca publicou. E a saída
óbvia, suceder a relação, não resolve: congela ainda mais tarde diante da mesma extração. A recusa
passa a dizer o que houve, por que, e o que fazer — nessa ordem, e com a data pronta.

**A garantia fica onde estava.** O teste da borda fixa a comparação: limite igual ao congelamento
recusa, um microssegundo depois sorteia. Esta feature avisa antes; não afrouxa nada.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SO_A_DATA = "essa fonte publica a data da extração, sem o horário"
SAIDA = "Publicar a relação nova sem retificar antes não resolve."


class _Fonte:
    def __init__(self, limite):
        self.limite = limite

    def observar(self, *, fonte, referencia):
        return Observacao(
            material_bruto="12345 67890 11223 44556 77889", ocorrida_nao_antes_de=self.limite
        )


def _congelado(gestor, api_client, manager_headers, process_payload, *, fonte):
    metodo = {**METODO, "source": fonte, "occurrence": "6113"}
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    relacao = RelacaoDeHabilitados.objects.get(
        pk=publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="saida-relacao",
            correlation_id="teste-102",
        )["relacao"]
    )
    return certame, relacao, metodo


def _sortear(certame, relacao, metodo, limite):
    ocorrencia = OcorrenciaDaFonte.objects.get(
        pk=observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=metodo["source"],
            referencia=metodo["occurrence"],
            idempotency_key="saida-obs",
            correlation_id="teste-102",
            fonte_externa=_Fonte(limite),
        )["ocorrencia"]
    )
    return constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao.id,
        ocorrencia_id=ocorrencia.id,
        idempotency_key="saida-sorteio",
        correlation_id="teste-102",
    )


def test_com_fonte_que_publica_so_a_data_a_recusa_diz_a_granularidade_e_a_saida(
    gestor, api_client, manager_headers, process_payload
):
    certame, relacao, metodo = _congelado(
        gestor, api_client, manager_headers, process_payload, fonte="Loteria Federal"
    )

    with pytest.raises(DomainError, match="occurrence_precedes_freeze") as recusa:
        _sortear(certame, relacao, metodo, relacao.publicada_em - timedelta(hours=11))

    mensagem = str(recusa.value.detail)
    congelada = f"{timezone.localtime(relacao.publicada_em):%d/%m/%Y %H:%M}"
    amanha = timezone.localdate(timezone.now(), ZONA) + timedelta(days=1)
    assert mensagem.startswith(f"A relação foi congelada em {congelada}, e a extração 6113")
    assert SO_A_DATA in mensagem
    assert f"se ela for congelada hoje, a partir de {amanha:%d/%m/%Y}" in mensagem
    assert SAIDA in mensagem
    passos = ["(1) retifique o Edital", "(2) publique a relação nova", "(3) observe a nova"]
    assert [mensagem.index(p) for p in passos] == sorted(mensagem.index(p) for p in passos)
    assert "compromisso do universo" not in mensagem, "o jargão saiu"


def test_com_fonte_que_publica_a_hora_a_recusa_diz_so_a_saida(
    gestor, api_client, manager_headers, process_payload
):
    certame, relacao, metodo = _congelado(
        gestor, api_client, manager_headers, process_payload, fonte="Fonte de demonstração"
    )

    with pytest.raises(DomainError, match="occurrence_precedes_freeze") as recusa:
        _sortear(certame, relacao, metodo, relacao.publicada_em - timedelta(hours=1))

    mensagem = str(recusa.value.detail)
    assert SO_A_DATA not in mensagem
    assert "a fonte situa a extração 6113" in mensagem
    assert SAIDA in mensagem


def test_limite_igual_ao_congelamento_continua_recusado(
    gestor, api_client, manager_headers, process_payload
):
    """FR-2664: a comparação é `<=`, e esta feature não a toca."""
    certame, relacao, metodo = _congelado(
        gestor, api_client, manager_headers, process_payload, fonte="Fonte de demonstração"
    )

    with pytest.raises(DomainError, match="occurrence_precedes_freeze"):
        _sortear(certame, relacao, metodo, relacao.publicada_em)


def test_limite_um_microssegundo_depois_do_congelamento_sorteia(
    gestor, api_client, manager_headers, process_payload
):
    certame, relacao, metodo = _congelado(
        gestor, api_client, manager_headers, process_payload, fonte="Fonte de demonstração"
    )

    declarado = _sortear(certame, relacao, metodo, relacao.publicada_em + timedelta(microseconds=1))

    assert declarado["quantidade"] == relacao.quantidade
    assert timezone.now() > relacao.publicada_em
