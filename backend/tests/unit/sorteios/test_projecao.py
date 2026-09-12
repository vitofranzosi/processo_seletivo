"""A relação é projeção, e a numeração é determinística (FR-002, FR-003, R-011, R-012).

Função pura sobre dados já lidos: é o que permite exercitar a regra sem montar um certame inteiro,
e é onde o defeito de numeração apareceria antes de qualquer tela.
"""

from types import SimpleNamespace

import pytest

from processo_seletivo.sorteios.domain import projecao

PPI = "00000000-0000-4000-8000-000000000831"
PCD = "00000000-0000-4000-8000-000000000832"


def inscricao(protocolo, *, modalidade=None, nome=None, identidade=None):
    return SimpleNamespace(
        id=identidade or f"id-{protocolo}",
        protocolo=protocolo,
        modality_id=modalidade,
        nome=nome or f"Candidata {protocolo}",
    )


def test_a_ampla_concorrencia_alcanca_todas_as_submetidas():
    universo = [inscricao("INS-2026-0003", modalidade=PPI), inscricao("INS-2026-0001")]

    assert len(projecao.elegiveis(universo)) == 2


def test_a_lista_de_reserva_alcanca_so_quem_declarou_aquela_modalidade():
    universo = [
        inscricao("INS-2026-0001"),
        inscricao("INS-2026-0002", modalidade=PPI),
        inscricao("INS-2026-0003", modalidade=PCD),
    ]

    assert [i.protocolo for i in projecao.elegiveis(universo, lista_id=PPI)] == ["INS-2026-0002"]


def test_a_numeracao_e_por_protocolo_crescente_de_1_a_n():
    universo = [inscricao("INS-2026-0009"), inscricao("INS-2026-0002"), inscricao("INS-2026-0005")]

    numerados = projecao.numerar(universo)

    assert [numero for numero, _ in numerados] == [1, 2, 3]
    assert [i.protocolo for _, i in numerados] == [
        "INS-2026-0002",
        "INS-2026-0005",
        "INS-2026-0009",
    ]


def test_duas_projecoes_do_mesmo_universo_produzem_a_mesma_numeracao():
    """Se não produzissem, o resumo da relação deixaria de ser reproduzível."""
    universo = [inscricao(f"INS-2026-{n:04d}") for n in (7, 3, 11, 1)]

    primeira = [(n, i.protocolo) for n, i in projecao.numerar(universo)]
    segunda = [(n, i.protocolo) for n, i in projecao.numerar(list(reversed(universo)))]

    assert primeira == segunda


def test_habilitadas_none_e_habilitadas_vazio_sao_coisas_diferentes():
    """`None` = não há Etapa de habilitação; vazio = há, e ninguém passou (R-012)."""
    universo = [
        inscricao("INS-2026-0001", identidade="a"),
        inscricao("INS-2026-0002", identidade="b"),
    ]

    assert len(projecao.elegiveis(universo, habilitadas=None)) == 2
    assert projecao.elegiveis(universo, habilitadas=set()) == []
    assert len(projecao.elegiveis(universo, habilitadas={"a"})) == 1


def test_o_criterio_publicado_diz_quem_entrou_e_por_que():
    ampla = projecao.criterio(quantidade=237)
    reserva = projecao.criterio(lista_id=PPI, nome_da_modalidade="PPI", quantidade=41)

    assert "Todas as inscrições submetidas" in ampla and "1 a 237" in ampla
    assert "PPI" in reserva and "1 a 41" in reserva


def test_o_conteudo_canonico_nao_carrega_identificador_interno():
    """O resumo cobre só o que o portal mostra — é o que o cidadão consegue recalcular (R-015)."""
    participantes = projecao.numerar([inscricao("INS-2026-0001", identidade="uuid-interno")])

    conteudo = projecao.conteudo_canonico(
        relacao_id="r1",
        edital_id="e1",
        versao_id="v1",
        perfil_id="p1",
        marco_id="m1",
        lista_id=None,
        metodo_hash="a" * 64,
        criterio_publicado="critério",
        participantes=participantes,
    )

    assert sorted(conteudo["participants"][0]) == ["name", "protocol", "publicNumber"]
    assert "uuid-interno" not in str(conteudo)


@pytest.mark.parametrize("campo", ["relationId", "editalId", "versionId", "methodHash"])
def test_o_conteudo_canonico_amarra_a_relacao_a_sua_norma_e_ao_seu_metodo(campo):
    conteudo = projecao.conteudo_canonico(
        relacao_id="r1",
        edital_id="e1",
        versao_id="v1",
        perfil_id="p1",
        marco_id="m1",
        lista_id=None,
        metodo_hash="a" * 64,
        criterio_publicado="critério",
        participantes=[],
    )

    assert campo in conteudo
