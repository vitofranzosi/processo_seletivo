"""A janela que nasce por Retificação é a que a interposição aplica (048, US3, FR-797).

`test_janela.py` declara a janela escrevendo direto no conteúdo publicado, e diz por quê: ali o que
se prova é a aplicação. Aqui é o contrário — o que se prova é o **caminho**: um marco publicado sem
janela ganha a janela por uma Retificação de verdade, e o ato divulgado depois dela abre a
interposição com o prazo declarado.
"""

import pytest

from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato
from tests.fixtures.publicacao import create_retification, publish_retification

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

TRES_DIAS = {"admits": True, "durationDays": 3, "unit": "DIAS_CORRIDOS"}


def interpor_como_titular(cenario, inscricao):
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.interpor import interpor

    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    return interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=alvo,
        fundamentacao="A prova didática entregue não foi considerada.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key="interpor-janela-nascida",
    )


def test_o_ato_divulgado_depois_da_retificacao_abre_o_prazo_que_ela_declarou(
    gestor, api_client, manager_headers, process_payload
):
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=148,
        codigo="0848",
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    edital = cenario["edital"]
    caminho = (
        f"/profiles/id={cenario['perfil']}/classificationMilestones/id={cenario['marco']}"
        "/appealWindow"
    )
    publicado = edital.versoes_consolidadas.latest("materialized_at").content
    marco = next(
        marco
        for perfil in publicado["profiles"]
        for marco in perfil.get("classificationMilestones") or []
        if str(marco["id"]) == str(cenario["marco"])
    )
    assert marco.get("appealWindow") is None, "a contraprova: o marco nasceu sem janela"

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [{"targetPath": caminho, "operation": "REPLACE", "newValue": TRES_DIAS}],
            suffix="janela",
        ),
        suffix="janela",
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["55.0000", "90.0000"], primeiro=1481, sufixo="148"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-janela-nascida")
    cenario["publicacao"] = publicar_o_ato(cenario, chave="publicar-janela-nascida")

    peca = interpor_como_titular(cenario, cenario["inscricoes"][0])

    assert peca.janela_abriu_em is not None
    assert peca.janela_fecha_em is not None
    assert (peca.janela_fecha_em - peca.janela_abriu_em).days in (2, 3)
