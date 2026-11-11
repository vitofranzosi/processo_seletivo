"""A composição da página do Processo (147): pura, sobre o que a view já leu.

`compor` lê as Retificações e a faixa da 104 — as duas leituras que ela faz — por funções que estes
casos substituem; o resto é reagrupar, contar e ordenar, e é isso que se prova aqui.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from processo_seletivo.interface import pagina_do_processo as pagina
from processo_seletivo.interface import trabalho

AGORA = datetime(2026, 11, 11, 12, 0)


def edital(numero, status="PUBLICADO", ano=2026):
    return SimpleNamespace(
        id=uuid4(), number=str(numero), year=ano, status=status, title=f"E{numero}"
    )


def processo(status="ATIVO"):
    return SimpleNamespace(id=uuid4(), status=status)


def marco(e, dias, descricao="Marco"):
    return SimpleNamespace(edital=e, inicio=AGORA + timedelta(days=dias), descricao=descricao)


def periodo(situacao="aberto", cancelado=False):
    return SimpleNamespace(situacao=situacao, cancelado=cancelado, em_curso=situacao == "aberto")


def pulso_de(*itens):
    return SimpleNamespace(por_edital=itens)


def item(e, *, marcos=(), per=None):
    return SimpleNamespace(edital=e, proximos_marcos=tuple(marcos), periodo=per)


def sinal(e):
    return SimpleNamespace(edital=e)


def ato(chave, *, irreversivel=False, depende=False):
    return SimpleNamespace(chave=chave, irreversivel=irreversivel, depende_dos_editais=depende)


@pytest.fixture
def sem_leituras(monkeypatch):
    """As duas leituras de `compor`, substituídas: nenhuma Retificação e a faixa pedida."""
    faixa = []
    monkeypatch.setattr(pagina.atos_retificacao, "em_curso_por_edital", lambda ids, ator: {})
    monkeypatch.setattr(pagina.trabalho, "do_ator", lambda *a, **k: list(faixa))
    return faixa


def compor(
    editais, *, status="ATIVO", pulso=None, sinais=(), atos=(), pendentes=(), elaboravel=None
):
    return pagina.compor(
        processo=processo(status),
        ator=SimpleNamespace(),
        editais=editais,
        pulso=pulso or pulso_de(),
        sinais=sinais,
        atos=atos,
        pendentes=pendentes,
        elaboravel=elaboravel,
    )


# ---- Onde estamos (FR-5301) ---------------------------------------------------------------------


def test_a_frase_conta_os_editais_por_situacao_na_ordem_administrativa():
    contagem = {"PUBLICADO": 13, "EM_ELABORACAO": 16, "CANCELADO": 1, "ENCERRADO": 1}
    assert pagina.situacoes_por_extenso(contagem) == (
        "16 em elaboração, 13 publicados, 1 encerrado, 1 cancelado"
    )


def test_a_frase_diz_inscricoes_abertas_e_atencao_so_quando_ha():
    frase, detalhe = pagina.onde_estamos(processo(), {"PUBLICADO": 4}, abertas=1, com_sinal=2)
    assert frase == "4 Editais: 4 publicados."
    assert detalhe == "Inscrições abertas em 1 Edital. 2 Editais com condição de atenção."
    assert pagina.onde_estamos(processo(), {"PUBLICADO": 1}, abertas=0, com_sinal=0)[1] == ""


def test_o_processo_final_diz_a_situacao_final():
    assert pagina.onde_estamos(processo("ENCERRADO"), {"ENCERRADO": 2}, abertas=0, com_sinal=0)[
        0
    ] == ("Processo encerrado.")
    frase, detalhe = pagina.onde_estamos(
        processo("CANCELADO"), {"CANCELADO": 1}, abertas=0, com_sinal=0
    )
    assert frase == "Processo cancelado."
    assert "mantêm suas próprias situações" in detalhe


def test_processo_sem_edital_diz_nenhum():
    assert pagina.onde_estamos(processo(), {}, abertas=0, com_sinal=0)[0] == "Nenhum Edital."


# ---- Os grupos (FR-5310, FR-5311) --------------------------------------------------------------


def test_os_grupos_vem_na_ordem_do_certame_e_so_os_que_tem_edital(sem_leituras):
    editais = [
        edital(1, "EM_ELABORACAO"),
        edital(2),
        edital(3, "CANCELADO"),
        edital(4, "HOMOLOGADO"),
    ]
    grupos = compor(editais).grupos
    assert [g.chave for g in grupos] == [pagina.PUBLICADOS, pagina.EM_PREPARO, pagina.FINAIS]
    assert [len(g.linhas) for g in grupos] == [1, 2, 1]
    assert not any(g.recolhido for g in grupos if g.chave != pagina.FINAIS)


@pytest.mark.parametrize(
    ("status", "recolhido"),
    [("ATIVO", True), ("EM_ELABORACAO", True), ("ENCERRADO", False), ("CANCELADO", False)],
)
def test_encerrados_e_cancelados_recolhem_so_no_processo_em_curso(sem_leituras, status, recolhido):
    grupos = compor([edital(1, "ENCERRADO")], status=status).grupos
    assert grupos[0].recolhido is recolhido


# ---- A linha (FR-5313) -------------------------------------------------------------------------


def test_a_linha_le_o_periodo_do_pulso(sem_leituras):
    aberto, cancelado, preparo = edital(1), edital(2), edital(3, "EM_ELABORACAO")
    linhas = compor(
        [aberto, cancelado, preparo],
        pulso=pulso_de(item(aberto, per=periodo()), item(cancelado, per=periodo(cancelado=True))),
    ).linhas
    assert [linha.inscricoes_abertas for linha in linhas] == [True, False, False]
    assert linhas[2].ainda_nao_publicado


def test_edital_encerrado_com_sinal_continua_contado(sem_leituras):
    """Caso-limite: as espécies que não param com o Edital continuam valendo, e contando."""
    encerrado = edital(1, "ENCERRADO")
    composta = compor([encerrado], sinais=[sinal(encerrado)])
    assert composta.total_de_sinais == 1
    assert composta.com_sinal[0].edital is encerrado


# ---- Os marcos (FR-5319) -----------------------------------------------------------------------


def test_os_marcos_de_todos_os_editais_numa_lista_por_data_seis_a_vista(sem_leituras):
    a, b = edital(1), edital(2)
    composta = compor(
        [a, b],
        pulso=pulso_de(
            item(a, marcos=[marco(a, d) for d in (5, 1, 9, 13)]),
            item(b, marcos=[marco(b, d) for d in (2, 7, 3)]),
        ),
    )
    dias = [(m.inicio - AGORA).days for m in composta.marcos + composta.marcos_demais]
    assert dias == [1, 2, 3, 5, 7, 9, 13]
    assert len(composta.marcos) == pagina.MARCOS_MOSTRADOS
    assert all(m.edital in (a, b) for m in composta.marcos)


# ---- A série (FR-5320) -------------------------------------------------------------------------


def test_a_serie_so_dos_periodos_em_curso(sem_leituras):
    a, b, c = edital(1), edital(2), edital(3)
    composta = compor(
        [a, b, c],
        pulso=pulso_de(item(a, per=periodo()), item(b, per=periodo("encerrado")), item(c)),
    )
    assert [linha.edital for linha in composta.com_inscricoes_abertas] == [a]


# ---- A faixa (FR-5303) -------------------------------------------------------------------------


def test_o_edital_do_proximo_passo_nao_se_repete_na_faixa(sem_leituras):
    a, b = edital(1, "EM_ELABORACAO"), edital(2, "EM_ELABORACAO")
    sem_leituras.extend(
        trabalho.ObjetoDeTrabalho("edital", ("edital", e.id), "", "Continuar", "", "", "/", e)
        for e in (a, b)
    )
    composta = compor([a, b], elaboravel=a)
    assert [objeto.edital for objeto in composta.faixa.objetos] == [b]
    # A marca da linha conta todas, inclusive a do botão: são da pessoa.
    assert [len(linha.meus) for linha in composta.linhas] == [1, 1]


def test_a_faixa_e_recortada_aos_editais_do_processo(sem_leituras):
    deste, de_outro = edital(1), edital(2)
    sem_leituras.extend(
        trabalho.ObjetoDeTrabalho("avaliacao", ("avaliacao", e.id), "", "Avaliar", "", "", "/", e)
        for e in (deste, de_outro)
    )
    assert [o.edital for o in compor([deste]).faixa.objetos] == [deste]


# ---- A administração (FR-5306, FR-5307) --------------------------------------------------------


def test_os_irreversiveis_vao_para_as_terminais_e_impedem_com_edital_pendente(sem_leituras):
    atos = [
        ato("ativar"),
        ato("encerrar", irreversivel=True, depende=True),
        ato("cancelar", irreversivel=True, depende=True),
    ]
    composta = compor([edital(1)], atos=atos, pendentes=[edital(1)])
    assert composta.ativar.chave == "ativar"
    assert [(t.ato.chave, t.impedido) for t in composta.terminais] == [
        ("encerrar", True),
        ("cancelar", True),
    ]
    assert composta.algum_impedido
    livre = compor([edital(1, "ENCERRADO")], atos=atos[1:], pendentes=[])
    assert not livre.algum_impedido
    assert livre.ativar is None


def test_sem_ato_nao_ha_administracao(sem_leituras):
    assert not compor([edital(1)]).tem_administracao
