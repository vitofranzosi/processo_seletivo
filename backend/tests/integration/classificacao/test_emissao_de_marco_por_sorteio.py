"""Marco por sorteio sem arredondamento: a emissão recusa antes de calcular, e o sorteio segue.

A `067` (ED-03) tirou a exigência de arredondamento do marco que declara ordem por sorteio. Isso
tornou alcançável um caminho que antes a validação fechava: um marco por sorteio que enumera Etapa,
com pontuação de todos, levado à emissão computada. `calcular_ordem` rodava antes da recusa do
sorteio, e `combinar → arredondar` levantava `RegraIncompleta` sem tratamento — erro interno no
lugar de `ordering_milestone_is_drawn` (FR-1318, D-009). E nada no caminho do sorteio lê
arredondamento (FR-1319).
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.application import emissao
from processo_seletivo.classificacao.domain.combinacao import RegraIncompleta, combinar
from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem, PosicaoNaOrdem
from processo_seletivo.divulgacao.domain.conteudo import ESCALA_PADRAO, _escala
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.domain import chave as dominio_da_chave
from tests.fixtures import sorteio as fixtures_do_sorteio
from tests.integration.sorteios.test_constituicao import _constituir, pronto  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture(autouse=True)
def sem_arredondamento(monkeypatch):
    """O marco do certame de sorteio da suíte, mas sem arredondamento declarado."""
    original = fixtures_do_sorteio.marco_com_metodo

    def sem(rascunho, **kwargs):
        rascunho = original(rascunho, **kwargs)
        for perfil in rascunho["profiles"]:
            for marco in perfil.get("classificationMilestones") or []:
                marco["rounding"] = {}
        return rascunho

    monkeypatch.setattr(fixtures_do_sorteio, "marco_com_metodo", sem)


def test_o_calculo_de_um_marco_por_sorteio_sem_arredondamento_quebraria():
    """A razão da ordem: combinar com pontuação e sem arredondamento é regra incompleta."""
    marco = {"stages": ["e"], "operation": "SOMA_PONDERADA", "normalization": "NENHUMA"}
    etapas = {"e": {"id": "e", "weight": "1.0000"}}
    with pytest.raises(RegraIncompleta):
        combinar({**marco, "rounding": {}}, etapas, {"e": Decimal("7.5")})


def test_a_emissao_recusa_o_sorteio_antes_de_calcular(
    gestor, api_client, manager_headers, process_payload, monkeypatch
):
    certame = fixtures_do_sorteio.certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, quantos=3
    )

    def nao_calcula(**_):
        raise AssertionError("a ordem de um marco por sorteio não se calcula")

    monkeypatch.setattr(emissao, "calcular_ordem", nao_calcula)
    with pytest.raises(DomainError) as recusa:
        emissao.emitir_ordem(
            actor=gestor,
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            lista_id=None,
            idempotency_key="067-sorteio-sem-arredondamento",
            correlation_id="teste-067",
            confirmacao_do_calculo="qualquer",
        )
    assert recusa.value.code == "ordering_milestone_is_drawn"
    assert not AtoDeOrdenacao.objects.filter(edital=certame["edital"]).exists()


def test_o_sorteio_sem_arredondamento_produz_a_ordem_do_algoritmo(pronto):  # noqa: F811
    certame, relacao, ocorrencia = pronto
    conteudo = effective_version(edital_id=certame["edital"].id).content
    marcos = [m for p in conteudo["profiles"] for m in p.get("classificationMilestones") or []]
    assert marcos and all(not m.get("rounding") for m in marcos), "publicado sem arredondamento"

    declarado = _constituir(certame, relacao, ocorrencia)

    ato = AtoDeOrdenacao.objects.get(pk=declarado["ato"])
    assert ato.origem == OrigemDaOrdem.SORTEIO
    esperada = dominio_da_chave.ordem(
        relation_hash=relacao.resumo,
        draw_scope_id=dominio_da_chave.recorte(perfil_id=relacao.perfil_id),
        seed=declarado["semente"],
        public_numbers=[p.numero_publico for p in relacao.participantes.all()],
    )
    numero = {p.inscricao_id: p.numero_publico for p in relacao.participantes.all()}
    gravada = [
        numero[p.inscricao_id] for p in PosicaoNaOrdem.objects.filter(ato=ato).order_by("posicao")
    ]
    assert gravada == esperada
    assert [p.posicao for p in PosicaoNaOrdem.objects.filter(ato=ato).order_by("posicao")] == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_a_divulgacao_nao_depende_do_arredondamento_do_marco_por_sorteio():
    """A escala da divulgação cai no padrão — e o sorteio não tem pontuação a formatar."""
    assert _escala({"rounding": {}}) == ESCALA_PADRAO
    assert _escala({}) == ESCALA_PADRAO


def test_a_divulgacao_e_a_verificacao_do_sorteio_nao_dependem_do_arredondamento(pronto):  # noqa: F811
    """FR-1319, pelo caminho inteiro: compor o que se divulga e verificar o sorteio, que o cidadão
    refaz pela página pública, sobre o ato de um marco publicado sem arredondamento."""
    from processo_seletivo.divulgacao.domain.conteudo import compor
    from processo_seletivo.sorteios.application.verificacao import verificar

    certame, relacao, ocorrencia = pronto
    declarado = _constituir(certame, relacao, ocorrencia)
    ato = AtoDeOrdenacao.objects.get(pk=declarado["ato"])

    divulgado = compor(ato)
    assert [linha["posicao"] for linha in divulgado["posicoes"]] == [1, 2, 3, 4, 5]
    assert not any(linha["compartilhada"] for linha in divulgado["posicoes"]), "ordem total"
    assert all(not linha.get("pontuacao") for linha in divulgado["posicoes"]), "sorteio não pontua"

    verificado = verificar(ato.sorteio)
    assert verificado["integro"], verificado["conferencias"]
