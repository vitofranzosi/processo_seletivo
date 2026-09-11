"""O universo declarado reproduz a faixa — meses depois, e sob a norma que a governou (014, US6).

É a prova que sustenta o ato mais contestável do certame: "por que a pessoa de posição onze não foi
à entrevista". Registrar o que foi usado e chegar de novo ao mesmo resultado são coisas distintas, e
a Constituição pede a segunda.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.corte import (
    divergencias_da_reproducao,
    reproduzir_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import EMITIR
from processo_seletivo.classificacao.domain.nomes import nomes_do_marco
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from tests.fixtures.corte import MARCO, emitir
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


# --- T086 · a reprodução chega à mesma faixa (FR-199, SC-061) --------------------------------


def test_o_universo_declarado_reproduz_a_mesma_faixa(cenario, gestor):
    edital, _, inscricoes = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()

    reproduzido = reproduzir_corte(corte)

    assert reproduzido["progrediram"] == [str(inscricoes[0].id), str(inscricoes[1].id)]
    assert (reproduzido["primeira_posicao"], reproduzido["ultima_posicao"]) == (1, 2)
    assert divergencias_da_reproducao(corte) == []


def test_a_reproducao_nao_usa_a_posicao_gravada_no_item(cenario, gestor):
    """Usá-la faria a reprodução confirmar a si mesma, e não provar coisa alguma."""
    edital, _, _ = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()

    posicoes_do_ato = set(corte.ato.posicoes.values_list("posicao", flat=True))
    reproduzido = reproduzir_corte(corte)

    assert reproduzido["ultima_posicao"] in posicoes_do_ato


def test_a_reproducao_nao_muda_quando_a_regra_vigente_muda(cenario, gestor, api_client):
    """O corte é lido sob a norma que o governou, e não sob a de hoje (FR-217)."""
    edital, _, _ = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()
    antes = reproduzir_corte(corte)

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": (
                    f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}"
                    "/cutRule/targetCount"
                ),
                "operation": "REPLACE",
                "newValue": 3,
            }
        ],
    )

    assert reproduzir_corte(Corte.objects.get(pk=corte.pk)) == antes


# --- T087 · o ato antigo é lido com os nomes da versão que congelou --------------------------


def test_o_corte_antigo_e_lido_com_os_nomes_da_versao_que_congelou(cenario, gestor, api_client):
    edital, _, _ = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()
    nome_de_entao = nomes_do_marco(
        corte.versao.content, perfil_id=corte.perfil_id, marco_id=corte.marco_id
    )["marco"]["name"]

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}/name",
                "operation": "REPLACE",
                "newValue": "Classificação renomeada",
            }
        ],
        suffix="b",
    )

    depois = Corte.objects.get(pk=corte.pk)
    lido = nomes_do_marco(
        depois.versao.content, perfil_id=depois.perfil_id, marco_id=depois.marco_id
    )["marco"]["name"]
    assert lido == nome_de_entao != "Classificação renomeada"


# --- T089 · a auditoria da emissão (FR-222, SC-070) ------------------------------------------


def test_a_auditoria_traz_o_ator_o_instante_e_o_recorte(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()

    registro = RegistroAuditoria.objects.get(operation=EMITIR)

    assert str(registro.aggregate_id) == str(corte.id)
    assert registro.actor_subject == gestor.subject
    assert registro.occurred_at is not None
    assert registro.reason


def test_o_ato_guarda_quem_emitiu_e_quando(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)

    corte = Corte.objects.get()

    assert corte.emitido_por == gestor.subject
    assert corte.emitido_em is not None
    assert corte.itens.count() == 4, "a proveniência inclui quem ficou fora"
    assert corte.itens.filter(consequencia=ItemDoCorte.Consequencia.FORA_DA_FAIXA).exists()
