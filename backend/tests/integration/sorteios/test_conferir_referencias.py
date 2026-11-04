"""O orquestrador da conferência: quais referências, e quantas chamadas (116, FR-3631–FR-3633).

Sem banco: o orquestrador lê conteúdo e consulta a fonte, e a fonte é a Caixa da suíte, que conta
as chamadas. A carga é requisito — uma consulta principal por ato, e uma por referência realizada
distinta (SC-1097).
"""

import copy
from datetime import UTC, date, datetime

from processo_seletivo.sorteios.application import conferencia
from processo_seletivo.sorteios.domain import conferencia as dominio
from tests.fixtures.edital import DRAW_METHOD, complete_draft, identidade_do_marco, identificador

LF = "Loteria Federal"
AGORA = datetime(2026, 11, 3, 22, 3, tzinfo=UTC)


def _metodo(ocorrencia, fonte=LF):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": fonte, "occurrence": ocorrencia})
    return metodo


def _com_marcos(*ocorrencias, fonte=LF):
    """Um Perfil por ocorrência, cada um com um marco de sorteio e método próprio."""
    rascunho = complete_draft()
    modelo = rascunho["profiles"][0]
    rascunho["profiles"] = []
    for indice, ocorrencia in enumerate(ocorrencias):
        perfil = copy.deepcopy(modelo)
        perfil["id"] = identificador(401, 10 + indice)
        perfil["code"] = f"P{indice}"
        marco = perfil["classificationMilestones"][0]
        marco["id"] = identidade_do_marco(perfil["id"])
        marco["code"] = f"M{indice}"
        marco["orderProduction"] = "POR_SORTEIO"
        marco["drawMethod"] = _metodo(ocorrencia, fonte) if ocorrencia else None
        if not ocorrencia:
            marco.pop("drawMethod")
        rascunho["profiles"].append(perfil)
    return rascunho


def _marco(conteudo, indice):
    return conteudo["profiles"][indice]["classificationMilestones"][0]["id"]


def test_uma_consulta_principal_por_ato(caixa):
    caixa.usar_gravacao()
    referencias = conferencia.referencias_a_conferir(_com_marcos("6116", "6117", "6200", "6116"))
    assert len(referencias) == 4
    situacoes = conferencia.conferir(referencias, agora=AGORA)
    assert caixa.chamadas_ao_ultimo == 1
    assert caixa.chamadas_por_numero == []
    assert {s.estado for s in situacoes.values()} == {dominio.AINDA_NAO_REALIZADO}
    # Três referências distintas, e não quatro: a situação é da referência, e não do marco.
    assert set(situacoes) == {(LF, "6116"), (LF, "6117"), (LF, "6200")}


def test_uma_consulta_por_referencia_realizada_distinta(caixa):
    caixa.usar_gravacao()
    referencias = conferencia.referencias_a_conferir(_com_marcos("6113", "6113", "5000", "6116"))
    situacoes = conferencia.conferir(referencias, agora=AGORA)
    assert caixa.chamadas_ao_ultimo == 1
    assert sorted(caixa.chamadas_por_numero) == [5000, 6113]
    assert situacoes[(LF, "6113")].realizada_em == date(2026, 10, 28)
    assert situacoes[(LF, "6116")].estado == dominio.AINDA_NAO_REALIZADO


def test_realizado_sem_data_continua_realizado(caixa):
    """A consulta pelo número falhou: a situação é a do último, sem data (FR-3629)."""
    caixa.realizado_ate(6114, date(2026, 11, 1))
    caixa.datas.pop(6114)
    situacoes = conferencia.conferir(
        conferencia.referencias_a_conferir(_com_marcos("6114")), agora=AGORA
    )
    situacao = situacoes[(LF, "6114")]
    assert situacao.estado == dominio.REALIZADO
    assert situacao.realizada_em is None
    assert caixa.chamadas_por_numero == [6114]


def test_a_forma_invalida_nao_consulta(caixa):
    situacoes = conferencia.conferir(
        conferencia.referencias_a_conferir(_com_marcos("6106-9", "Concurso 6115")), agora=AGORA
    )
    assert {s.estado for s in situacoes.values()} == {dominio.REFERENCIA_INVALIDA}
    assert caixa.chamadas == 0


def test_a_fonte_que_nao_sabe_conferir_fica_de_fora(caixa, monkeypatch):
    """Fonte que não declara conferência: nenhuma consulta, e nenhum achado (D-008)."""
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    monkeypatch.setattr(LoteriaFederal, "SABE_CONFERIR", False)
    referencias = conferencia.referencias_a_conferir(_com_marcos("5000"))
    assert referencias == []
    assert conferencia.conferir(referencias, agora=AGORA) == {}
    assert caixa.chamadas == 0


def test_a_demonstracao_e_consultada_pela_tabela_e_nao_pela_caixa(caixa):
    referencias = conferencia.referencias_a_conferir(
        _com_marcos("5000", "9998", fonte="Fonte de demonstração")
    )
    situacoes = conferencia.conferir(referencias, agora=AGORA)
    assert situacoes[("Fonte de demonstração", "5000")].estado == dominio.REALIZADO
    assert situacoes[("Fonte de demonstração", "9998")].estado == dominio.INCONCLUSIVO
    assert caixa.chamadas == 0


def test_o_metodo_comum_e_conferido_uma_vez():
    rascunho = _com_marcos(None, None)
    rascunho["drawMethod"] = _metodo("6116")
    (referencia,) = conferencia.referencias_a_conferir(rascunho)
    assert referencia.caminho == "/drawMethod"
    assert (referencia.fonte, referencia.referencia) == (LF, "6116")


def test_o_comum_e_conferido_enquanto_houver_marco_por_sortear():
    rascunho = _com_marcos(None, None)
    rascunho["drawMethod"] = _metodo("6116")
    sorteado = frozenset({_marco(rascunho, 0)})
    assert len(conferencia.referencias_a_conferir(rascunho, marcos_sorteados=sorteado)) == 1
    todos = frozenset({_marco(rascunho, 0), _marco(rascunho, 1)})
    assert conferencia.referencias_a_conferir(rascunho, marcos_sorteados=todos) == []


def test_o_marco_sem_sorteio_a_fazer_fica_de_fora():
    rascunho = _com_marcos("6113", "6116")
    referencias = conferencia.referencias_a_conferir(
        rascunho, marcos_sorteados=frozenset({_marco(rascunho, 0)})
    )
    assert [r.referencia for r in referencias] == ["6116"]


def test_o_marco_que_ordena_por_pontuacao_fica_de_fora():
    rascunho = _com_marcos("6113")
    rascunho["profiles"][0]["classificationMilestones"][0]["orderProduction"] = "POR_PONTUACAO"
    assert conferencia.referencias_a_conferir(rascunho) == []


def test_com_base_so_as_introduzidas():
    """Na Retificação, só a referência diferente da do mesmo marco na base (FR-3633, D-006)."""
    base = _com_marcos("5000", "6116")
    conteudo = copy.deepcopy(base)
    conteudo["profiles"][1]["classificationMilestones"][0]["drawMethod"]["occurrence"] = "6113"
    conteudo["schedule"][0]["title"] = "Outra data"
    referencias = conferencia.referencias_a_conferir(conteudo, base=base)
    assert [(r.referencia, r.caminho.split("/")[2]) for r in referencias] == [
        ("6113", f"id={conteudo['profiles'][1]['id']}")
    ]
    assert conferencia.referencias_a_conferir(base, base=base) == []


def test_com_base_a_troca_de_fonte_e_introducao():
    base = _com_marcos("5000", fonte="Fonte de demonstração")
    conteudo = copy.deepcopy(base)
    conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"]["source"] = LF
    (referencia,) = conferencia.referencias_a_conferir(conteudo, base=base)
    assert (referencia.fonte, referencia.referencia) == (LF, "5000")


def test_referencia_travada_sem_consulta_e_inconclusiva():
    """O conteúdo mudou entre a consulta e a trava: nunca "ainda não realizado" (FR-3632)."""
    consultadas = {
        (LF, "6116"): dominio.situacao(
            fonte=LF,
            referencia="6116",
            consulta=dominio.ConsultaDoUltimo(dominio.UltimoConcurso(6114, date(2026, 11, 1))),
            consultada_em=AGORA,
        )
    }
    travadas = conferencia.referencias_a_conferir(_com_marcos("6116", "6113"))
    conferidas = conferencia.conferidas(travadas, consultadas, agora=AGORA)
    estados = {item.referencia.referencia: item.situacao.estado for item in conferidas}
    assert estados == {"6116": dominio.AINDA_NAO_REALIZADO, "6113": dominio.INCONCLUSIVO}
