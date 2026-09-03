"""T024 — a causa de cada impedimento de prontidão.

Duas propriedades, e a primeira é a que sustenta a segunda: se os estados não particionam a
população, resumo e detalhe filtrado divergem, e a presidência passa a ter dois números para a
mesma Etapa. A segunda é o que separa "erro" de uma tela que diz a ação seguinte.
"""

from uuid import UUID

import pytest

from processo_seletivo.avaliacoes.application.selectors import (
    inscricoes_da_etapa,
    resumo_da_etapa,
)
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.prontidao import (
    IMPEDIDA,
    PRONTA,
    panorama_da_etapa,
)
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def montar(gestor, api_client, manager_headers, *, seed, avaliacoes=1):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=seed, codigo=str(seed), avaliacoes=avaliacoes
    )
    cenario["vigentes"] = etapas_vigentes(cenario["edital"])
    cenario["etapa_publicada"] = cenario["vigentes"][UUID(str(cenario["primeira"]))]
    return cenario


def panorama(cenario):
    return panorama_da_etapa(
        edital=cenario["edital"],
        etapa=cenario["etapa_publicada"],
        etapas_vigentes=cenario["vigentes"],
    )


def test_a_inscricao_com_conclusao_elegivel_fica_pronta(gestor, api_client, manager_headers):
    cenario = montar(gestor, api_client, manager_headers, seed=1321)
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1321")
    concluir_como(cenario, "joao", inscricao, pontuacao="75")

    estado, _ = panorama(cenario)["estados"][inscricao.id]
    assert estado == PRONTA


def test_sem_conclusao_a_causa_e_nomeada(gestor, api_client, manager_headers):
    """ "Erro" não diz o que fazer; "ainda não há avaliação concluída" diz."""
    cenario = montar(gestor, api_client, manager_headers, seed=1322)
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1322")

    estado, motivo = panorama(cenario)["estados"][inscricao.id]
    assert estado == IMPEDIDA
    assert "ainda não há avaliação concluída" in motivo


def test_etapa_de_leitura_multipla_impede_a_etapa_inteira(gestor, api_client, manager_headers):
    """Todas as inscrições impedidas, com a mesma frase, e a quantidade publicada nela."""
    cenario = montar(gestor, api_client, manager_headers, seed=1323, avaliacoes=2)
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1323")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")

    resultado = panorama(cenario)
    assert resultado["impedimento_da_etapa"] is not None
    assert resultado["contagens"]["prontas"] == 0
    for inscricao in inscricoes:
        estado, motivo = resultado["estados"][inscricao.id]
        assert estado == IMPEDIDA
        assert "2 avaliações" in motivo


def test_o_resumo_existente_recebe_as_contagens_sem_duplicar(gestor, api_client, manager_headers):
    """O mesmo resumo da 012 — acrescido, e não um painel ao lado (D-004)."""
    cenario = montar(gestor, api_client, manager_headers, seed=1324)
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1324")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")

    resumo = resumo_da_etapa(
        edital=cenario["edital"], etapa=cenario["etapa_publicada"], panorama=panorama(cenario)
    )
    # As dimensões da 012 continuam lá, e as da 013 entram ao lado delas.
    assert resumo["inscricoes"] == 2 and resumo["sem_conclusao"] == 1
    assert resumo["prontas"] == 1 and resumo["impedidas"] == 1


def test_o_filtro_da_listagem_devolve_exatamente_o_grupo(gestor, api_client, manager_headers):
    """Resumo e detalhe filtrado saem do mesmo dicionário, e por isso não divergem."""
    cenario = montar(gestor, api_client, manager_headers, seed=1325)
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1325")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    visao = panorama(cenario)

    linhas, _ = inscricoes_da_etapa(
        edital=cenario["edital"],
        etapa=cenario["etapa_publicada"],
        panorama=visao,
        prontidao=PRONTA,
    )
    assert [linha["inscricao"].id for linha in linhas] == [inscricoes[0].id]
    assert len(linhas) == visao["contagens"]["prontas"]
