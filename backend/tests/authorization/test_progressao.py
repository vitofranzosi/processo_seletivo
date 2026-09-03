"""T045 — a inscrição excluída responde 404 uniforme, nas quatro superfícies do avaliador.

404, e nunca 403: a existência não é enumerável por quem não tem acesso, e é a mesma resposta que a
012 dá para inscrição não atribuída. Um 403 diria "existe, e você não pode" — que é informação.
"""

from uuid import UUID

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.selectors import mesa, proxima_pendente
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.authorization, pytest.mark.django_db]


@pytest.fixture
def com_eliminada(gestor, api_client, manager_headers):
    """Etapa 1 consolidada: uma habilitada, uma eliminada. As duas distribuídas na Etapa 2."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1400, codigo="1400"
    )
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1400")
    for inscricao, nota in zip(inscricoes, ("75", "40"), strict=True):
        concluir_como(cenario, "joao", inscricao, pontuacao=nota)
    # A Etapa 2 é distribuída **antes** da consolidação, que é quando ela ainda aceita as duas.
    distribuir_para(
        {**cenario, "etapa": cenario["segunda"]}, gestor, ["joao"], inscricoes, chave="lote2-1400"
    )
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="k-1400",
        correlation_id="teste",
    )
    cenario["habilitada"], cenario["eliminada"] = inscricoes
    return cenario


def test_a_mesa_da_etapa_seguinte_nao_lista_a_eliminada(com_eliminada):
    linhas, _, contagens = mesa(
        ator=ator_institucional("joao"),
        edital=com_eliminada["edital"],
        etapa_id=UUID(str(com_eliminada["segunda"])),
        vigentes=etapas_vigentes(com_eliminada["edital"]),
    )
    listadas = {linha["atribuicao"].inscricao_id for linha in linhas}
    assert com_eliminada["habilitada"].id in listadas
    assert com_eliminada["eliminada"].id not in listadas
    assert contagens["total"] == 1


def test_a_proxima_pendente_nao_oferece_a_eliminada(com_eliminada):
    """A porta que entrega sem que ninguém peça — e por isso a mais fácil de esquecer."""
    seguinte = proxima_pendente(
        ator=ator_institucional("joao"),
        edital=com_eliminada["edital"],
        etapa_id=com_eliminada["segunda"],
        depois_de=com_eliminada["habilitada"].id,
    )
    assert seguinte is None


@pytest.mark.parametrize("rota", ["interface:mesa-inscricao", "interface:minha-etapa"])
def test_o_identificador_da_eliminada_nao_alcanca_a_inscricao(
    client, seletor_ligado, com_eliminada, rota
):
    """Trocar o UUID na URL não abre a porta: identificador não concede acesso."""
    identificar(client, "joao", [])
    args = [com_eliminada["edital"].id, com_eliminada["segunda"]]
    if rota == "interface:mesa-inscricao":
        args.append(com_eliminada["eliminada"].id)
        assert client.get(reverse(rota, args=args)).status_code == 404
    else:
        # A Etapa continua alcançável — o que não é alcançável é a inscrição eliminada dentro dela.
        assert client.get(reverse(rota, args=args)).status_code == 200


def test_a_inscricao_habilitada_continua_alcancavel(client, seletor_ligado, com_eliminada):
    """A não regressão que acompanha toda recusa: o caminho legítimo não fechou junto."""
    identificar(client, "joao", [])
    url = reverse(
        "interface:mesa-inscricao",
        args=[
            com_eliminada["edital"].id,
            com_eliminada["segunda"],
            com_eliminada["habilitada"].id,
        ],
    )
    assert client.get(url).status_code == 200
