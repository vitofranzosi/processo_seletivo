"""O candidato retirado fica sabendo, e pode recorrer (164, FR-7031, FR-7032, D-012).

O cenário é o da jornada de 14/11: a Heteroidentificação restrita a `PPI`, e o marco por pontuação
enumerando a Prova, que vem depois dela. A Heteroidentificação nunca é enumerada — o marco só
enumera Etapa classificatória —, e antes da decisão do usuário o Resultado dela não era visível
nem recorrível: a candidata lia "1º lugar" na ampla e nada sobre a reserva perdida.
"""

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.recursos.application.interpor import objetos_recorriveis
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.selectors import resultados_visiveis
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PPI, rascunho_com_alcance
from tests.fixtures.comissao import alocar_em, constituir, inscrever
from tests.fixtures.divulgacao import entrar_como_titular, publicar_o_ato
from tests.fixtures.edital import corte_que_nao_governa, identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

SEED = 1671
JANELA = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}


def _consolidar(cenario, etapa, inscricoes, chave):
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa,
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    rascunho = rascunho_com_alcance(SEED)
    analise, hetero, prova = rascunho["stages"]
    prova["classificatory"] = True
    prova["weight"] = "1.0000"
    perfil = rascunho["profiles"][0]
    marco = identificador(1679, SEED)
    perfil["classificationMilestones"] = [
        {
            "id": marco,
            "code": "Z-FINAL",
            "name": "Classificação final",
            "orderProduction": "POR_PONTUACAO",
            "stages": [prova["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
            "cutRule": corte_que_nao_governa(),
            "appealWindow": JANELA,
        }
    ]
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"visivel-ao-titular-{SEED:04d}"},
        {
            "institutionalCode": f"PS-2026-{SEED}",
            "title": f"Processo {SEED}",
            "firstEdital": {"number": str(SEED), "year": 2026, "title": f"Edital {SEED}"},
        },
        draft=rascunho,
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"visivel-{SEED}",
    )
    for etapa in (analise["id"], hetero["id"], prova["id"]):
        alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave=f"v-{etapa}")
    maria, ana, bia = inscrever(
        edital,
        3,
        primeiro=1,
        modalidades={0: MODALIDADE_PPI, 1: MODALIDADE_PPI},
        perfil=perfil["id"],
    )
    cenario = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": analise["id"],
    }
    distribuir_para(cenario, gestor, ["joao"], [maria, ana, bia], chave="v-analise")
    for inscricao in (maria, ana, bia):
        concluir_como(cenario, "joao", inscricao, pontuacao="80")
    _consolidar(cenario, analise["id"], [maria, ana, bia], "v-consolidar-analise")
    na_hetero = {**cenario, "etapa": hetero["id"]}
    distribuir_para(na_hetero, gestor, ["joao"], [maria, ana], chave="v-hetero")
    concluir_como(na_hetero, "joao", maria, sentido="DESFAVORAVEL")
    concluir_como(na_hetero, "joao", ana, sentido="FAVORAVEL")
    _consolidar(cenario, hetero["id"], [maria, ana], "v-consolidar-hetero")
    na_prova = {**cenario, "etapa": prova["id"]}
    distribuir_para(na_prova, gestor, ["joao"], [maria, ana, bia], chave="v-prova")
    for inscricao, nota in ((maria, "95"), (ana, "85"), (bia, "75")):
        concluir_como(na_prova, "joao", inscricao, pontuacao=nota)
    _consolidar(cenario, prova["id"], [maria, ana, bia], "v-consolidar-prova")
    return {
        **cenario,
        "perfil": perfil["id"],
        "marco": marco,
        "hetero": hetero["id"],
        "maria": maria,
        "ana": ana,
        "bia": bia,
        "gestor": gestor,
    }


def _publicar_a_ampla(cenario):
    proposta = calcular_ordem(
        edital=cenario["edital"], perfil_id=cenario["perfil"], marco_id=cenario["marco"]
    )
    emitir_ordem(
        actor=cenario["gestor"],
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        perfil_id=cenario["perfil"],
        marco_id=cenario["marco"],
        idempotency_key="v-emitir",
        correlation_id="teste",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=None),
    )
    ato = AtoDeOrdenacao.objects.get(
        edital=cenario["edital"], marco_id=cenario["marco"], lista_id=None
    )
    publicar_o_ato({"edital": cenario["edital"], "ato": ato}, chave="v-publicar")


def test_antes_da_publicacao_do_marco_a_retirada_nao_aparece(cenario):
    """FR-7031: a visibilidade vem da publicação, e não da consolidação."""
    assert resultados_visiveis(cenario["maria"]) == []


def test_publicado_o_marco_a_retirada_fica_visivel_ao_titular(cenario):
    """FR-7031, D-012: a Prova vem depois da Heteroidentificação; o marco a leu."""
    _publicar_a_ampla(cenario)

    visiveis = {item["etapa_id"]: item for item in resultados_visiveis(cenario["maria"])}

    assert str(cenario["hetero"]) in visiveis
    assert visiveis[str(cenario["hetero"])]["retirada"] is True
    # Bia, da ampla, não tem Resultado na Heteroidentificação, e nada a mais aparece para ela.
    assert str(cenario["hetero"]) not in {
        item["etapa_id"] for item in resultados_visiveis(cenario["bia"])
    }


def test_a_retirada_e_recorrivel_pelo_prazo_do_marco(cenario):
    """FR-7032: o Resultado visível é recorrível pela janela da publicação que o leu."""
    _publicar_a_ampla(cenario)

    rotulos = {item["rotulo"] for item in objetos_recorriveis(cenario["maria"])}

    assert "Heteroidentificação" in rotulos


def test_o_acompanhamento_diz_a_reserva_perdida(cenario, client):
    """FR-7024, UX-742: pelo canal do candidato, a linha da reserva perdida, e nunca "Eliminado"."""
    _publicar_a_ampla(cenario)
    entrar_como_titular(client, cenario["maria"])

    corpo = client.get(
        reverse("portal:acompanhamento", args=[cenario["maria"].id])
    ).content.decode()

    assert "você deixou de concorrer pela reserva de vagas" in corpo
    assert "continua concorrendo pela ampla concorrência" in corpo
    # "Eliminada" também: o cartão da Etapa a dizia, e a jornada de 14/11 o achou.
    assert "Eliminad" not in corpo
    assert "Deixou de concorrer pela reserva" in corpo
