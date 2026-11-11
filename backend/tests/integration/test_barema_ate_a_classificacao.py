"""Do barema publicado até o candidato, sem tocar o que vem depois do total (146, T023, T026, T036).

A jornada é a de `quickstart.md` §2–§3, pelos comandos reais: a Etapa do marco publica o barema do
14/2026, duas inscrições são pontuadas pela ficha, a presidência consolida, emite a ordem e publica
o preliminar. Daí em diante nada sabe do barema (FR-5220): a consolidação copia o total, e a ordem
o combina. O que é novo é o que o titular lê — a pontuação critério a critério, pela versão que o
Resultado cita — e a recusa da correção fixada enquanto o incremento C não chega (FR-5232).
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.portal.identidade import IdentidadeDoCandidato
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.recursos.application.interpor import interpor
from processo_seletivo.recursos.application.julgar import CORRECAO_FIXADA_SEM_BAREMA, julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.selectors import detalhamento_do_resultado
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.barema import (
    concluir_com_ficha,
    criterio_de,
    ficha,
    montar_marco_com_barema,
    pontuar_com_ficha,
)
from tests.fixtures.divulgacao import emitir, entrar_como_titular, publicar_o_ato
from tests.fixtures.mesa import distribuir_para
from tests.fixtures.publicacao import retify
from tests.fixtures.recursos_us4 import assinatura_de, julgador

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.usefixtures("raiz_de_arquivos"),
]

SEED = 150
FORA_DA_AREA = "O certificado de especialização apresentado não é da área da Educação."


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Duas inscrições: 70 (o quickstart) e 30, eliminada pela mínima de 60."""
    cenario = montar_marco_com_barema(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=SEED,
        codigo="0150",
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    cenario["inscricoes"] = pontuar_com_ficha(
        cenario,
        gestor,
        [
            ficha(SEED, 1, 0, 3, 0, 52),
            ficha(SEED, 0, 1, 1, 0, 10, justificativas={2: FORA_DA_AREA}),
        ],
        primeiro=1501,
        sufixo="150",
    )
    return cenario


def acompanhamento(client, inscricao):
    entrar_como_titular(client, inscricao)
    corpo = client.get(reverse("portal:acompanhamento", args=[inscricao.id])).content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def test_o_total_da_ficha_e_o_que_a_consolidacao_e_a_ordem_usam(cenario, gestor):
    """FR-5220: consolidar, ordenar e publicar recebem o total pelo campo de sempre."""
    setenta, trinta = cenario["inscricoes"]
    resultados = {
        r.inscricao_id: r for r in ResultadoEtapa.vigentes.filter(etapa_id=cenario["etapa"])
    }

    assert resultados[setenta.id].pontuacao == Decimal("70.0000")
    assert resultados[trinta.id].pontuacao == Decimal("30.0000")
    assert resultados[trinta.id].consequencia == ResultadoEtapa.Consequencia.ELIMINADA
    # O Resultado não copia o detalhamento: ele cita a Avaliação, e o detalhamento é dela.
    assert detalhamento_do_resultado(resultados[setenta.id])[4]["parcela"] == "40.0000"

    ato = emitir(cenario, gestor, chave="emitir-146")
    publicar_o_ato(cenario, chave="publicar-146", ato=ato)

    posicoes = list(PosicaoNaOrdem.objects.filter(ato=ato).order_by("posicao"))
    assert [p.inscricao_id for p in posicoes][:1] == [setenta.id]


def test_o_titular_ve_a_pontuacao_por_criterio_depois_do_preliminar(client, cenario, gestor):
    """US3 cenários 2 e 3, SC-1631: antes da publicação nada; depois, só a do titular."""
    setenta, trinta = cenario["inscricoes"]
    ato = emitir(cenario, gestor, chave="emitir-146b")

    assert "Pontuação por critério" not in acompanhamento(client, trinta)

    publicar_o_ato(cenario, chave="publicar-146b", ato=ato)
    dele = acompanhamento(client, trinta)

    assert "Pontuação por critério" in dele
    assert "Exercício de docência em EaD" in dele
    assert FORA_DA_AREA in dele
    # A descrição da versão que o Resultado cita.
    assert "Em cursos a distância." in dele
    outra = acompanhamento(client, setenta)
    assert "limitada ao máximo" in outra
    # O que o outro titular escreveu na justificativa não atravessa.
    assert FORA_DA_AREA not in outra


def test_retificacao_posterior_nao_muda_o_que_o_titular_le(client, api_client, cenario, gestor):
    """SC-1633, FR-5233: o detalhamento se lê com o barema da versão que o Resultado cita."""
    _, trinta = cenario["inscricoes"]
    ato = emitir(cenario, gestor, chave="emitir-146c")
    publicar_o_ato(cenario, chave="publicar-146c", ato=ato)
    caminho = f"/stages/id={cenario['etapa']}/criteria/id={criterio_de(4, SEED)}"
    retify(
        api_client,
        cenario["edital"],
        [
            {"targetPath": f"{caminho}/name", "operation": "REPLACE", "newValue": "Docência EaD"},
            {
                "targetPath": f"{caminho}/description",
                "operation": "REPLACE",
                "newValue": "Só em cursos EaD.",
            },
        ],
        suffix="146c",
    )

    corpo = acompanhamento(client, trinta)

    assert "Exercício de docência em EaD" in corpo
    assert "Em cursos a distância." in corpo
    assert "Docência EaD" not in corpo
    assert "Só em cursos EaD." not in corpo


@pytest.fixture
def peca(cenario, gestor):
    """O recurso da eliminada, interposto e admitido pelo caminho real, contra o preliminar."""
    ato = emitir(cenario, gestor, chave="emitir-146d")
    publicar_o_ato(cenario, chave="publicar-146d", ato=ato)
    inscricao = cenario["inscricoes"][1]
    superado = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    recurso = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=superado,
        fundamentacao="A especialização é da área: o certificado diz Educação a Distância.",
        assinatura_do_objeto=str(superado.pk),
        idempotency_key="interpor-146",
    )
    admitir(
        actor=julgador(),
        recurso_id=recurso.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(recurso),
        idempotency_key="admitir-146",
    )
    return {"recurso": recurso, "superado": superado, "inscricao": inscricao}


def test_a_correcao_fixada_e_recusada_enquanto_o_c_nao_chega(cenario, peca):
    """T036, FR-5232, SC-1635: 409 com a orientação para a reavaliação, e nada gravado."""
    with pytest.raises(DomainError) as recusa:
        julgar(
            actor=julgador(),
            recurso_id=peca["recurso"].id,
            especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
            motivacao="A especialização é da área.",
            etapa_id=cenario["etapa"],
            pontuacao="35.0000",
            assinatura_do_resultado=str(peca["superado"].id),
            idempotency_key="corrigir-146",
        )

    assert recusa.value.code == CORRECAO_FIXADA_SEM_BAREMA
    assert recusa.value.status == 409
    assert "reavaliação determinada" in recusa.value.detail
    assert not DecisaoRecurso.objects.exists()
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def test_a_reavaliacao_determinada_continua_e_percorre_a_ficha(client, cenario, peca, gestor):
    """SC-1623, SC-1635: outro avaliador pontua pela ficha; o sucessor nasce com o detalhamento."""
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a especialização por avaliador diverso.",
        etapa_id=cenario["etapa"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-146",
    )
    inscricao = peca["inscricao"]
    distribuir_para(cenario, gestor, ["ana"], [inscricao], chave="reav-146")
    concluir_com_ficha(cenario, "ana", inscricao, ficha(SEED, 0, 1, 2, 0, 50))
    consolidar(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        idempotency_key="cumprir-146",
        correlation_id="teste",
    )

    sucessor = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    assert sucessor.decisao_id == decisao.id
    assert sucessor.resultado_anterior_id == peca["superado"].id
    assert sucessor.pontuacao == Decimal("65.0000")
    assert [linha["parcela"] for linha in detalhamento_do_resultado(sucessor)] == [
        "0.0000",
        "15.0000",
        "10.0000",
        "0.0000",
        "40.0000",
    ]
    # Nenhum Resultado da Etapa com barema existe sem detalhamento (SC-1635).
    assert all(
        detalhamento_do_resultado(resultado)
        for resultado in ResultadoEtapa.objects.filter(etapa_id=cenario["etapa"])
    )
