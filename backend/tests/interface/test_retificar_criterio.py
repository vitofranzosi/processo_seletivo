"""O critério de desempate se corrige pela tela, e não só se reduz (048, US4, FR-792, FR-793).

Até a 048 a Retificação removia critério e não acrescentava: quem publicou o critério errado podia
tirá-lo, e não pôr o certo no lugar. O acréscimo usa o molde da linha do quadro — fragmento escopado
ao Edital, opções lidas do vigente — e a validação é a da composição, a mesma função que o ato
chama de novo.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis, diferencas
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import CRITERIO, ETAPA, FATO, MARCO, rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

NOVO = "00000000-0000-4000-8000-000000048001"


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _perfil_do_marco(conteudo):
    return next(p for p in conteudo["profiles"] if p.get("classificationMilestones"))


def _formulario(vigente, *, remover=(), **linha):
    """O que a tela envia sem ninguém tocar em nada, mais a linha do critério novo."""
    grupos = campos_editaveis(vigente.content)
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{c['referencia']}": c["valor"] for g in grupos for c in g["campos"]}
    for grupo in grupos:
        if any(grupo["caminho"].endswith(f"tiebreakers/id={alvo}") for alvo in remover):
            enviados[f"remover:{grupo['referencia']}"] = "1"
    enviados |= {f"novo-criterio-0-{chave}": valor for chave, valor in linha.items()}
    return enviados


def _linha(vigente, **alteracoes):
    perfil = _perfil_do_marco(vigente.content)
    return {
        "id": NOVO,
        "milestone": f"{perfil['id']}|{MARCO}",
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "target": f"etapa|{ETAPA['A']}",
        "whenMissing": "ULTIMO_NO_CRITERIO",
        "order": "3",
        **alteracoes,
    }


def test_o_botao_e_o_fragmento_existem(client, seletor_ligado, publicado):
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    destino = reverse("interface:fragmento-retificacao-criterio", args=[edital.id])

    tela = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    fragmento = client.get(destino)

    assert "Acrescentar critério de desempate" in tela
    assert destino in tela
    assert fragmento.status_code == 200
    corpo = fragmento.content.decode()
    assert re.search(r'name="novo-criterio-[^"]+-milestone"', corpo)
    assert "Maior pontuação numa Etapa" in corpo
    assert "tiebreakers" not in corpo, "o caminho normativo não chega ao HTML (FR-019)"


def test_as_opcoes_sao_etapas_classificatorias_e_fatos_do_vigente(publicado):
    from processo_seletivo.interface.retificacao import opcoes_do_criterio_novo

    _, vigente = publicado
    opcoes = opcoes_do_criterio_novo(vigente.content)
    classificatorias = {
        etapa["id"] for etapa in vigente.content["stages"] if etapa.get("classificatory")
    }
    fatos = {
        str(fato["id"])
        for perfil in vigente.content["profiles"]
        for fato in perfil.get("declaredFacts") or []
    }

    alvos = {valor for valor, _ in opcoes["target"]}
    assert alvos == {f"etapa|{e}" for e in classificatorias} | {f"fato|{f}" for f in fatos}
    assert MARCO in {valor.split("|")[1] for valor, _ in opcoes["milestone"]}


def test_o_criterio_completo_vira_um_add_com_a_identidade_do_fragmento(publicado):
    _, vigente = publicado
    perfil = _perfil_do_marco(vigente.content)

    alteracoes, resumo = diferencas(vigente.content, _formulario(vigente, **_linha(vigente)))

    assert alteracoes == [
        {
            "targetPath": f"/profiles/id={perfil['id']}/classificationMilestones/id={MARCO}"
            "/tiebreakers/-",
            "operation": "ADD",
            "newValue": {
                "id": NOVO,
                "order": 3,
                "type": "MAIOR_PONTUACAO_NA_ETAPA",
                "parameters": {"stageId": ETAPA["A"]},
                "whenMissing": "ULTIMO_NO_CRITERIO",
            },
        }
    ]
    # FR-800: antes, nada; depois, a ordem, o tipo e o alvo por extenso.
    assert len(resumo) == 1
    assert resumo[0]["rotulo"] == "Acréscimo"
    assert resumo[0]["antes"] == "—"
    assert resumo[0]["depois"].startswith("3 — Maior pontuação numa Etapa: Pontuação na Etapa")


@pytest.mark.parametrize(
    ("alteracoes", "trecho"),
    [
        ({"order": "1"}, "compartilhar a mesma ordem"),
        ({"order": ""}, "número inteiro a partir de 1"),
        ({"type": "MAIOR_VALOR_DE_FATO"}, "declarar o que compara"),
        ({"milestone": ""}, "a que marco"),
    ],
)
def test_ao_conferir_a_recusa_e_a_da_composicao(publicado, alteracoes, trecho):
    _, vigente = publicado

    with pytest.raises(ValueError, match=trecho):
        diferencas(vigente.content, _formulario(vigente, **_linha(vigente, **alteracoes)))


def test_o_fato_de_outro_perfil_e_recusado(publicado):
    """O alvo é uma escolha só, com os fatos de todos os Perfis: `diferencas` confere o Perfil.

    O fato alheio é acrescentado ao conteúdo em memória — o que se prova é a conferência, e montar
    um segundo Perfil com fato pela composição não acrescentaria nada a ela.
    """
    from copy import deepcopy
    from types import SimpleNamespace

    _, publicado_de_verdade = publicado
    conteudo = deepcopy(publicado_de_verdade.content)
    do_marco = _perfil_do_marco(conteudo)["id"]
    alheio = next(p for p in conteudo["profiles"] if p["id"] != do_marco)
    alheio.setdefault("declaredFacts", []).append(
        {"id": "00000000-0000-4000-8000-000000048002", "code": "X", "label": "X", "type": "DATA"}
    )
    vigente = SimpleNamespace(content=conteudo, id=publicado_de_verdade.id)

    with pytest.raises(ValueError, match="não é declarado pelo Perfil deste marco"):
        diferencas(
            conteudo,
            _formulario(
                vigente,
                **_linha(
                    vigente,
                    type="MAIOR_VALOR_DE_FATO",
                    target="fato|00000000-0000-4000-8000-000000048002",
                ),
            ),
        )


def test_remover_um_e_acrescentar_outro_na_mesma_ordem_passa(publicado):
    """A troca que a US4 existe para permitir: a ordem conta os critérios que **continuam**."""
    _, vigente = publicado

    alteracoes, _ = diferencas(
        vigente.content,
        _formulario(vigente, remover=[CRITERIO["ETAPA"]], **_linha(vigente, order="1")),
    )

    assert sorted(alteracao["operation"] for alteracao in alteracoes) == ["ADD", "REMOVE"]


def test_a_linha_deixada_em_branco_nao_acrescenta_nada(publicado):
    _, vigente = publicado

    assert diferencas(vigente.content, _formulario(vigente, id=NOVO)) == ([], [])


def test_o_criterio_por_fato_do_perfil_passa(publicado):
    _, vigente = publicado

    alteracoes, _ = diferencas(
        vigente.content,
        _formulario(
            vigente,
            **_linha(vigente, type="MENOR_VALOR_DE_FATO", target=f"fato|{FATO['NASCIMENTO']}"),
        ),
    )

    assert alteracoes[0]["newValue"]["parameters"] == {"factId": FATO["NASCIMENTO"]}


def test_confirmado_pela_tela_o_criterio_e_gravado(client, seletor_ligado, publicado):
    edital, vigente = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **_formulario(vigente, **_linha(vigente)),
            "justificativa": "O Edital omitiu o terceiro critério de desempate.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-criterio-000001",
        },
    )

    assert resposta.status_code == 302, resposta.content.decode()
    gravada = Retificacao.objects.get().alteracoes.get()
    assert gravada.new_value["id"] == NOVO
