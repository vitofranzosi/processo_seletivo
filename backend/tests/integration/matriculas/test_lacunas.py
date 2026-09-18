"""O que saiu vazio, dito antes de alguém perguntar (`US2`, `FR-439`, `FR-440`, `FR-452`).

**Sem o relatório, a lacuna vira preenchimento manual às pressas** — e o erro volta pela porta que a
feature existe para fechar.
"""

import pytest

from processo_seletivo.matriculas.application.exportar import compor
from processo_seletivo.matriculas.application.populacao import opcoes
from processo_seletivo.matriculas.domain import nomes
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from tests.fixtures.matriculas import montar_cenario_da_exportacao

pytestmark = pytest.mark.django_db


def relatorio_de(quem_exporta, edital):
    escolhida = opcoes(edital)[0]
    return compor(
        ator=quem_exporta,
        edital=edital,
        especie=escolhida.especie,
        referencia=escolhida.referencia,
    ).relatorio


def item(relatorio, coluna):
    return next(linha for linha in relatorio if linha.coluna == coluna)


def test_as_tres_colunas_externas_aparecem_com_a_razao_e_nao_como_erro(cenario, quem_exporta):
    """`SC-145`, `C3`: *"vocabulário do sistema acadêmico — preencher no destino"*."""
    edital, convocadas = cenario
    relatorio = relatorio_de(quem_exporta, edital)
    for coluna in ("COD_CURSO", "COD_TURNO", "COD_POLO"):
        lacuna = item(relatorio, coluna)
        assert lacuna.especie == nomes.EXTERNA
        assert "sistema acadêmico" in lacuna.razao
        assert lacuna.quantidade == len(convocadas)


def test_o_aviso_da_renda_vem_mesmo_sem_nenhuma_outra_lacuna(cenario, quem_exporta):
    """`SC-153`: **em toda geração**, com as duas medidas nomeadas.

    Se o aviso não estiver lá, o cenário falhou — mesmo com o arquivo perfeito. Ele é o que impede o
    número de viajar sem etiqueta.
    """
    edital, _ = cenario
    aviso = item(relatorio_de(quem_exporta, edital), "RENDA_PER_CAPITA_PNP")
    assert aviso.especie == nomes.DIVERGENCIA
    assert "soma" in aviso.razao
    assert "por pessoa" in aviso.razao


def test_quem_declarou_cor_indigena_e_nomeado(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, quem_exporta
):
    """`FR-440`, `SC-146`, `R-1`: caso próprio, e não efeito colateral.

    A coluna sai vazia **e a pessoa aparece no relatório com o que declarou** — porque apagar uma
    declaração em silêncio é o defeito que esta feature existe para não cometer.
    """
    edital, convocadas = montar_cenario_da_exportacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="matriculas-031-indigena",
        declaracoes=[{"cor_raca": requerimento_nomes.INDIGENA}],
    )
    lacuna = item(relatorio_de(quem_exporta, edital), "COR")
    assert lacuna.especie == nomes.NOMINAL
    assert lacuna.quantidade == 1
    assert convocadas[0].protocolo in lacuna.pessoas[0]
    assert "Indígena" in lacuna.pessoas[0]


def test_quem_declarou_outro_pais_e_nomeado(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, quem_exporta
):
    """`SC-154`: o estrangeiro sai com a coluna vazia e aparece nomeado.

    `BR` é o único código que a amostra prova; emitir outro seria a invenção que a `D-001` recusa.
    """
    edital, convocadas = montar_cenario_da_exportacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="matriculas-031-estrangeira",
        declaracoes=[{"nacionalidade": requerimento_nomes.OUTRO_PAIS}],
    )
    lacuna = item(relatorio_de(quem_exporta, edital), "COD_NACIONALIDADE")
    assert lacuna.especie == nomes.NOMINAL
    assert convocadas[0].protocolo in lacuna.pessoas[0]


def test_a_ausencia_declarada_e_contada_sem_expor_ninguem(cenario, quem_exporta):
    """`FR-439`: a coluna vazia entra no relatório com a quantidade — e sem lista de nomes.

    Quem não declarou o nome do pai está numa situação legítima (`FR-384` da `029`); listá-lo seria
    expor a ausência sem ganho nenhum para quem lê.
    """
    edital, convocadas = cenario
    lacuna = item(relatorio_de(quem_exporta, edital), "NOME_PAI")
    assert lacuna.especie == nomes.AUSENCIA
    assert lacuna.quantidade == len(convocadas)
    assert lacuna.pessoas == ()
