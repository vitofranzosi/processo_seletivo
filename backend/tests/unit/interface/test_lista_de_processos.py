"""O recorte, a página e as frases da lista, sem requisição nem banco (129)."""

import pytest

from processo_seletivo.interface import lista_de_processos as lp
from processo_seletivo.processos.application.selectors import (
    ANDAMENTO,
    CANCELADOS,
    ENCERRADOS,
    Contagem,
)


def contagem(andamento=0, encerrados=0, cancelados=0, achados=None):
    por_grupo = {ANDAMENTO: andamento, ENCERRADOS: encerrados, CANCELADOS: cancelados}
    return Contagem(por_grupo, achados or dict(por_grupo))


def test_sem_parametro_e_a_aba_em_andamento_na_primeira_pagina():
    recorte = lp.recorte_de({})
    assert (recorte.situacao, recorte.busca, recorte.pagina_pedida) == ("andamento", "", 1)
    assert recorte.grupo == ANDAMENTO


@pytest.mark.parametrize("valor", ["arquivados", "", "ANDAMENTO", "0"])
def test_aba_invalida_cai_em_andamento(valor):
    assert lp.recorte_de({"situacao": valor}).situacao == "andamento"


def test_todos_nao_tem_grupo():
    assert lp.recorte_de({"situacao": "todos"}).grupo is None


@pytest.mark.parametrize(("valor", "pedida"), [("abc", 1), ("0", 1), ("-3", 1), ("", 1), ("7", 7)])
def test_pagina_invalida_vai_para_a_primeira(valor, pedida):
    assert lp.recorte_de({"pagina": valor}).pagina_pedida == pedida


def test_busca_sem_espacos_nas_pontas_e_cortada():
    assert lp.recorte_de({"busca": "   "}).busca == ""
    # O PostgreSQL recusa o NUL em texto: sem tirá-lo, a página respondia 500.
    assert lp.recorte_de({"busca": "90\x00/2026"}).busca == "90/2026"
    assert lp.recorte_de({"busca": "  90/2026 "}).busca == "90/2026"
    assert len(lp.recorte_de({"busca": "x" * 300}).busca) == lp.BUSCA_MAXIMA


def test_pagina_alem_da_ultima_e_a_ultima_e_o_intervalo():
    recorte = lp.recorte_de({"pagina": "9"})
    pagina = lp.paginar(recorte, 61)
    assert (pagina.numero, pagina.total_de_paginas, pagina.mostrando) == (4, 4, "61–61")
    primeira = lp.paginar(lp.recorte_de({}), 61)
    assert primeira.mostrando == "1–20" and primeira.varias
    assert not lp.paginar(lp.recorte_de({}), 20).varias
    assert lp.paginar(lp.recorte_de({}), 0).total_de_paginas == 1


def test_os_links_de_pagina_preservam_a_aba_e_a_busca():
    aba = lp.paginar(lp.recorte_de({"situacao": "cancelados", "pagina": "2"}), 50)
    assert aba.anterior == "?situacao=cancelados"
    assert aba.seguinte == "?situacao=cancelados&pagina=3"

    padrao = lp.paginar(lp.recorte_de({"pagina": "2"}), 50)
    # A primeira página do padrão é o endereço sem parâmetro (FR-4316).
    assert padrao.anterior == ""

    busca = lp.paginar(lp.recorte_de({"busca": "Física & Química", "situacao": "todos"}), 50)
    # A busca descarta a aba, e o termo vai codificado.
    assert busca.seguinte == "?busca=F%C3%ADsica+%26+Qu%C3%ADmica&pagina=2"
    assert not busca.tem_anterior and busca.tem_seguinte


def test_as_abas_contam_processos_e_a_busca_nao_marca_nenhuma():
    numeros = contagem(61, 120, 19)
    abas = lp.abas(lp.recorte_de({}), numeros)
    assert [(a.rotulo, a.quantidade, a.atual) for a in abas] == [
        ("Em andamento", 61, True),
        ("Encerrados", 120, False),
        ("Cancelados", 19, False),
        ("Todos", 200, False),
    ]
    # A aba leva à página 1 e sem busca (FR-4314); "Em andamento" é o endereço sem parâmetro.
    assert [a.endereco for a in abas] == [
        "",
        "?situacao=encerrados",
        "?situacao=cancelados",
        "?situacao=todos",
    ]
    assert not any(a.atual for a in lp.abas(lp.recorte_de({"busca": "x"}), numeros))


def test_a_frase_do_recorte():
    assert lp.frase_do_recorte(lp.paginar(lp.recorte_de({}), 61)) == (
        "61 Processos, mostrando 1–20."
    )
    assert lp.frase_do_recorte(lp.paginar(lp.recorte_de({}), 1)) == "1 Processo, mostrando 1–1."
    assert lp.frase_do_recorte(lp.paginar(lp.recorte_de({}), 0)) == (
        "Nenhum Processo nesta situação."
    )


def test_a_frase_da_busca_diz_onde_procurou_e_quantos_sao_finais():
    recorte = lp.recorte_de({"busca": "90"})
    achados = {ANDAMENTO: 1, ENCERRADOS: 1, CANCELADOS: 1}
    frase = lp.frase_da_busca(lp.paginar(recorte, 3), contagem(achados=achados))
    assert frase == (
        "3 Processos encontrados para “90”, em todas as situações, mostrando 1–3. "
        "2 estão encerrados ou cancelados: a situação de cada um está ao lado do nome."
    )
    um = {ANDAMENTO: 0, ENCERRADOS: 0, CANCELADOS: 1}
    assert "1 está encerrado ou cancelado" in lp.frase_da_busca(
        lp.paginar(recorte, 1), contagem(achados=um)
    )
    so_andamento = {ANDAMENTO: 1, ENCERRADOS: 0, CANCELADOS: 0}
    frase = lp.frase_da_busca(lp.paginar(recorte, 1), contagem(achados=so_andamento))
    assert frase == "1 Processo encontrado para “90”, em todas as situações, mostrando 1–1."


def test_a_busca_sem_resultado():
    recorte = lp.recorte_de({"busca": "inexistente"})
    assert lp.frase_da_busca(lp.paginar(recorte, 0), contagem()) == (
        "Nenhum Processo encontrado para “inexistente” em nenhuma situação."
    )
