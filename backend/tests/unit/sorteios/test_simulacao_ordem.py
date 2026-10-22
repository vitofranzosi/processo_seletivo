"""A ordem da prévia do sorteio é a do algoritmo publicado, sobre uma relação fictícia (098, R-002).

**Os vetores normativos são a prova de forma.** Se `ordem_do_recorte`, com o resumo do vetor
injetado, devolve a ordem que o vetor publica, então a prévia calcula como o certame — e o que muda
entre as duas é só o resumo da relação, que muda *qual* ordem sai. A prova com o caminho oficial
inteiro, no banco, é `tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py`.
"""

import ast
import json
import pathlib

import pytest

from processo_seletivo.classificacao.domain.cenarios_da_previa import nome_ficticio
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.domain import chave, simulacao
from processo_seletivo.sorteios.domain.projecao import conteudo_canonico

VETORES = pathlib.Path(__file__).resolve().parents[2] / "contract" / "fixtures" / "sorteio"
PERFIL = "00000000-0000-4000-8000-000000000980"
PPI = "00000000-0000-4000-8000-000000000981"
PCD = "00000000-0000-4000-8000-000000000982"
RAIZ = pathlib.Path(__file__).resolve().parents[3] / "processo_seletivo"


def _vetores_de_chave():
    # O de ordenação (`desempate-por-numero-publico`) dá chaves prontas, e não entradas: ele prova o
    # § 4.2 sem SHA-256, e não tem o que injetar aqui.
    return [
        dados
        for caminho in sorted(VETORES.glob("*.json"))
        if "input" in (dados := json.loads(caminho.read_text(encoding="utf-8")))
    ]


def _populacao(so_ampla=3, ppi=2, pcd=1):
    return simulacao.populacao(so_ampla, [(PPI, ppi), (PCD, pcd)], nomear=nome_ficticio)


def test_a_varredura_encontra_vetores_de_chave():
    assert len(_vetores_de_chave()) >= 4


@pytest.mark.parametrize("vetor", _vetores_de_chave(), ids=lambda v: v["name"])
def test_com_o_resumo_do_vetor_a_ordem_e_a_que_o_vetor_publica(vetor):
    entrada = vetor["input"]
    candidatos = simulacao.populacao(len(entrada["participants"]), [], nomear=nome_ficticio)
    relacao = simulacao.relacao_ficticia(
        candidatos, perfil_id=entrada["drawScopeId"], lista_id=None
    )

    ordem = simulacao.ordem_do_recorte(
        relacao,
        perfil_id=entrada["drawScopeId"],
        semente=entrada["seed"],
        relation_hash=entrada["relationHash"],
    )

    assert [item["numero_publico"] for item in ordem] == vetor["expectedOrder"]


def test_sem_resumo_injetado_a_ordem_usa_o_da_relacao_ficticia_e_e_deterministica():
    candidatos = _populacao()
    relacao = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=None)

    primeira = simulacao.ordem_do_recorte(relacao, perfil_id=PERFIL, semente="1 2 3")
    segunda = simulacao.ordem_do_recorte(relacao, perfil_id=PERFIL, semente="1 2 3")

    assert primeira == segunda
    esperada = chave.ordem(
        relation_hash=relacao.resumo,
        draw_scope_id=PERFIL,
        seed="1 2 3",
        public_numbers=[1, 2, 3, 4, 5, 6],
    )
    assert [item["numero_publico"] for item in primeira] == esperada


def test_a_ampla_tem_todos_e_cada_reservada_so_os_dela_numerados_de_1_a_n():
    candidatos = _populacao()

    ampla = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=None)
    ppi = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=PPI)

    assert [n for n, _ in ampla.participantes] == [1, 2, 3, 4, 5, 6]
    assert [c.id for _, c in ampla.participantes] == [c.id for c in candidatos]
    assert [n for n, _ in ppi.participantes] == [1, 2]
    assert {c.lista_id for _, c in ppi.participantes} == {PPI}


def test_cada_recorte_tem_a_sua_identidade_e_a_mesma_pessoa_cai_em_outra_posicao():
    """A chave leva `drawScopeId`: com a mesma semente, cada lista é sorteada à parte (FR-2494)."""
    candidatos = _populacao(so_ampla=0, ppi=8, pcd=0)
    ampla = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=None)
    ppi = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=PPI)

    na_ampla = simulacao.ordem_do_recorte(
        ampla, perfil_id=PERFIL, semente="7", relation_hash="r" * 64
    )
    na_ppi = simulacao.ordem_do_recorte(ppi, perfil_id=PERFIL, semente="7", relation_hash="r" * 64)

    # Mesmas pessoas, mesmos números públicos, mesmo resumo e mesma semente: só o recorte difere.
    assert [i["numero_publico"] for i in na_ampla] != [i["numero_publico"] for i in na_ppi]


def test_o_resumo_ficticio_nunca_tem_a_forma_da_relacao_oficial():
    candidatos = _populacao()
    relacao = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=None)

    oficial = conteudo_canonico(
        relacao_id="r",
        edital_id="e",
        versao_id="v",
        perfil_id=PERFIL,
        marco_id="m",
        lista_id=None,
        metodo_hash="h",
        criterio_publicado="c",
        participantes=[],
    )
    assert "previaDoSorteio" not in oficial
    assert relacao.resumo == canonical_sha256(
        {
            "previaDoSorteio": True,
            "perfilId": PERFIL,
            "listaId": None,
            "participantes": [[n, c.nome] for n, c in relacao.participantes],
        }
    )


def test_o_item_da_ordem_tem_o_formato_que_o_corte_e_a_rodada_leem():
    candidatos = _populacao()
    relacao = simulacao.relacao_ficticia(candidatos, perfil_id=PERFIL, lista_id=PPI)

    ordem = simulacao.ordem_do_recorte(relacao, perfil_id=PERFIL, semente="1")

    assert [item["posicao"] for item in ordem] == [1, 2]
    for item in ordem:
        assert set(item) == {"inscricao_id", "posicao", "empate_residual", "numero_publico"}
        assert item["empate_residual"] is False
        assert item["inscricao_id"].startswith(PPI)


def test_a_semente_da_rodada_deriva_da_exibida():
    assert simulacao.semente_da_rodada("048213771904", 0) == "048213771904:0"
    assert simulacao.semente_da_rodada("048213771904", 999) == "048213771904:999"


def _importados(caminho):
    nomes = set()
    for no in ast.walk(ast.parse(caminho.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


def test_o_dominio_do_sorteio_ficticio_nao_importa_classificacao_nem_ocupacao():
    """A fronteira da R-008: os nomes chegam por parâmetro; corte e ocupação são de outra camada."""
    importados = _importados(RAIZ / "sorteios" / "domain" / "simulacao.py")

    assert not any(
        nome.startswith(("processo_seletivo.classificacao", "processo_seletivo.ocupacao"))
        for nome in importados
    ), importados


def test_a_aplicacao_do_sorteio_ficticio_nao_importa_ocupacao():
    """A ocupação chega injetada pela interface, como na `095` (`test_dependencia_da_ocupacao`)."""
    importados = _importados(RAIZ / "sorteios" / "application" / "simulacao.py")

    assert not any(nome.startswith("processo_seletivo.ocupacao") for nome in importados), importados
