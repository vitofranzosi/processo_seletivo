"""Os pontos para revisão antes da abertura pública, por Edital (070, `FR-1443`, T041)."""

import copy

from processo_seletivo.duvidas.domain.estruturas import (
    PONTO_ANEXO_CITADO_INEXISTENTE,
    PONTO_CANAIS_DIVERGENTES,
    PONTO_EXCLUSIVIDADE_DO_CANAL,
    PONTO_RETIFICACAO_FUTURA,
)
from processo_seletivo.duvidas.domain.revisao import pontos_para_revisao
from tests.fixtures.corpus import conteudo, contexto_do_corpus
from tests.unit.duvidas.conftest import em

DIA = em("2026-10-20T12:00:00-03:00")


def tipos(contexto):
    return [ponto.tipo for ponto in pontos_para_revisao(contexto)]


def _sintetico(nome, publicacao, mudar):
    publicado = copy.deepcopy(conteudo(nome, publicacao))
    mudar(publicado)
    return contexto_do_corpus(nome, DIA, conteudo_substituto=publicado)


def test_91_a_clausula_de_exclusividade_vai_para_revisao_com_o_paragrafo():
    pontos = pontos_para_revisao(contexto_do_corpus("91", DIA))
    assert [p.tipo for p in pontos] == [PONTO_EXCLUSIVIDADE_DO_CANAL]
    assert "exclusivamente pelo e-mail" in pontos[0].fontes[0].conteudo
    assert "Resolver antes de abrir o assistente de dúvidas neste Edital." in pontos[0].descricao


def test_dois_canais_vao_para_revisao():
    def dois(publicado):
        secao = next(s for s in publicado["sections"] if s["key"] == "disposicoes-finais")
        secao["content"] += "\nDúvidas sobre a matrícula: matricula.demo@exemplo.ifes.edu.br."

    assert PONTO_CANAIS_DIVERGENTES in tipos(_sintetico("92", 2, dois))


def test_anexo_citado_que_nao_existe_vai_para_revisao():
    def cita(publicado):
        publicado["stages"][0]["name"] += " e do Anexo IX"

    pontos = pontos_para_revisao(_sintetico("92", 2, cita))
    citado = next(p for p in pontos if p.tipo == PONTO_ANEXO_CITADO_INEXISTENTE)
    assert "Anexo IX" in citado.descricao


def test_retificacao_de_vigencia_futura_vai_para_revisao():
    assert PONTO_RETIFICACAO_FUTURA in tipos(contexto_do_corpus("01", DIA))
    assert PONTO_RETIFICACAO_FUTURA not in tipos(
        contexto_do_corpus("01", em("2026-10-27T12:00:00-03:00"))
    )


def test_edital_sem_nenhuma_condicao_nao_tem_ponto():
    assert tipos(contexto_do_corpus("92", DIA)) == []
