"""O passo da chamada, a situação do aviso da pendência e o índice do recorte, sem banco (143).

As leituras são de estados que já existem (o prazo da `019`, os documentos da `115`, o aviso da
`066`); o que se prova aqui é a precedência do passo, que nenhuma frase trata pendência como
comunicação, e que o índice não escolhe providência.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.avisos.domain import nomes as avisos
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.domain import vocabulario_do_canal as canal
from processo_seletivo.interface import conducao_da_convocacao as c

AGORA = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))


def documentos(estado, **contagens):
    base = {
        "recebidos": 0,
        "complementados": 0,
        "pendentes": 0,
        "conformes": 0,
        "nao_se_aplica": 0,
        "a_apresentar": 0,
        "obrigatorios": 0,
        "total": 2,
    }
    return SimpleNamespace(estado=estado, contagens={**base, **contagens}, pedidos=[])


def desfecho(especie="ACEITE", rotulo="Aceite"):
    return SimpleNamespace(especie=especie, get_especie_display=lambda: rotulo)


# --- O passo (FR-5011, D-007) ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("estado", "docs", "codigo", "acao"),
    [
        (nomes.CONVOCADO_PRAZO_NAO_INICIADO, None, c.SEM_COMUNICACAO, c.EMITIR),
        (
            nomes.CONVOCADO_VENCIMENTO_DECORRIDO,
            documentos(nomes.DOCUMENTOS_PARA_CONFERIR, recebidos=1),
            c.VENCIDA,
            c.DESFECHO,
        ),
        (
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_PARA_CONFERIR, recebidos=2),
            c.A_CONFERIR,
            c.CONFERIR,
        ),
        (
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_PARA_CONFERIR, recebidos=1, complementados=1),
            c.REENVIADO,
            c.CONFERIR,
        ),
        (
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_COM_PENDENCIA, pendentes=1),
            c.PENDENCIA,
            "",
        ),
        (
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_COM_PENDENCIA),
            c.REFAZER_CONFERENCIA,
            c.CONFERIR,
        ),
        (
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_AGUARDANDO, a_apresentar=2),
            c.AGUARDANDO_DOCUMENTOS,
            "",
        ),
        (
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_PRONTA, conformes=2),
            c.PRONTA,
            c.DESFECHO,
        ),
        (nomes.CONVOCADO_PRAZO_EM_CURSO, None, c.AGUARDANDO_RESPOSTA, ""),
    ],
)
def test_a_precedencia_do_passo(estado, docs, codigo, acao):
    """FR-5011: desfecho → comunicação → vencimento → documentos → prazo."""
    passo = c.passo_da_chamada(
        estado=estado, desfecho=None, documentos=docs, vencimento=AGORA + timedelta(days=3)
    )

    assert (passo.codigo, passo.acao) == (codigo, acao)


def test_com_desfecho_o_passo_e_a_situacao_e_nao_ha_acao():
    passo = c.passo_da_chamada(
        estado=nomes.DESFECHADO,
        desfecho=desfecho(),
        documentos=documentos(nomes.DOCUMENTOS_DECIDIDA),
    )

    assert (passo.codigo, passo.tom, passo.acao) == (c.DESFECHADA, "feito", "")
    assert passo.frase == "Desfecho registrado: Aceite."


def test_por_publicacao_o_passo_diz_registrar_a_publicacao():
    """FR-4000 da `125`: a palavra do canal, e não "emitir a comunicação"."""
    passo = c.passo_da_chamada(
        estado=nomes.CONVOCADO_PRAZO_NAO_INICIADO,
        desfecho=None,
        documentos=None,
        canal=canal.PUBLICACAO,
    )

    assert passo.frase.startswith("Registrar a publicação:")
    assert "comunicação" not in passo.frase.split(":")[0]


def test_sem_vencimento_o_passo_diz_que_o_edital_nao_publica_prazo():
    passo = c.passo_da_chamada(
        estado=nomes.CONVOCADO_PRAZO_EM_CURSO, desfecho=None, documentos=None, vencimento=None
    )

    assert "não publica prazo" in passo.frase


# --- O aviso da pendência (FR-5015 a FR-5018) ---------------------------------------------------


def _lido(estado, *, conferido_em=None, apresentado_em=None):
    return SimpleNamespace(
        estado=estado,
        conferencia=SimpleNamespace(conferido_em=conferido_em) if conferido_em else None,
        vigente=SimpleNamespace(apresentado_em=apresentado_em) if apresentado_em else None,
    )


def _com_pendencia(instante=AGORA):
    return SimpleNamespace(pedidos=[_lido(nomes.ITEM_PENDENTE, conferido_em=instante)])


def _aviso(solicitado_em, estado, aceito_em=None):
    return (SimpleNamespace(aviso=SimpleNamespace(solicitado_em=solicitado_em)), estado, aceito_em)


PALAVRAS_DE_COMUNICACAO = ("avisad", "comunicad", "entregue", "recebid", "lid")


def test_sem_aviso_a_pendencia_nao_e_comunicacao():
    """FR-5017, FR-5018: nenhuma palavra diz que o candidato soube por e-mail."""
    situacao = c.situacao_do_aviso(_com_pendencia(), motivo="")
    texto = (situacao.frase_da_pendencia + " " + situacao.frase_do_aviso).lower()

    assert "Nenhum aviso desde esta pendência" in situacao.frase_do_aviso
    assert "O aviso pode ser pedido agora" in situacao.frase_do_aviso
    assert situacao.oferece_o_aviso
    for palavra in PALAVRAS_DE_COMUNICACAO:
        assert palavra not in texto, palavra


def test_o_motivo_da_previa_diz_por_que_o_aviso_nao_alcanca():
    situacao = c.situacao_do_aviso(_com_pendencia(), motivo="já avisada hoje")

    assert "O aviso não a alcança agora: já avisada hoje." in situacao.frase_do_aviso
    assert not situacao.oferece_o_aviso


def test_quem_nao_confere_nao_le_sobre_o_gesto():
    """Sem a prévia (`motivo=None`), a tela não sabe se o gesto alcança: não diz nada sobre ele."""
    situacao = c.situacao_do_aviso(_com_pendencia(), motivo=None)

    assert "pode ser pedido" not in situacao.frase_do_aviso
    assert "não a alcança" not in situacao.frase_do_aviso
    assert not situacao.oferece_o_aviso


def test_envio_desabilitado_e_dito():
    situacao = c.situacao_do_aviso(_com_pendencia(), motivo="", habilitado=False)

    assert "desabilitado" in situacao.frase_do_aviso
    assert situacao.oferece_o_aviso  # o link leva à seção, que diz o mesmo e não tem botão


@pytest.mark.parametrize(
    ("estado", "esperado"),
    [
        (avisos.PENDENTE, "ainda não foi enviado"),
        (avisos.EM_ENVIO, "o envio está em curso"),
        (avisos.ESTADO_ACEITA, "aceito pelo servidor de correio em 10/11/2026 12:05"),
        (avisos.ESTADO_FALHA_DEFINITIVA, ": falha."),
        (avisos.SEM_ENDERECO, ": sem endereço."),
    ],
)
def test_o_aviso_depois_da_pendencia_diz_a_situacao_do_envio(estado, esperado):
    """FR-5016: as palavras da `066` — aceita pelo servidor de correio, nunca entregue."""
    situacao = c.situacao_do_aviso(
        _com_pendencia(),
        aviso=_aviso(AGORA + timedelta(minutes=1), estado, AGORA + timedelta(minutes=5)),
        motivo="já avisada hoje",
    )

    assert situacao.frase_do_aviso.startswith("Aviso de pendência registrado em 10/11/2026 12:01")
    assert esperado in situacao.frase_do_aviso
    assert "entregue" not in situacao.frase_do_aviso
    assert not situacao.oferece_o_aviso


def test_aviso_anterior_a_pendencia_nao_a_cobre():
    """Caso-limite: o aviso de ontem não fala da pendência de hoje."""
    situacao = c.situacao_do_aviso(
        _com_pendencia(AGORA),
        aviso=_aviso(AGORA - timedelta(days=1), avisos.ESTADO_ACEITA, AGORA - timedelta(days=1)),
        motivo="",
    )

    assert situacao.aviso_em is None
    assert "Nenhum aviso desde esta pendência" in situacao.frase_do_aviso


def test_documento_reenviado_pede_nova_conferencia_e_nao_oferece_o_aviso():
    reenviado = SimpleNamespace(pedidos=[_lido(nomes.ITEM_COMPLEMENTADO, apresentado_em=AGORA)])

    situacao = c.situacao_do_aviso(reenviado, motivo="documento reenviado, aguardando conferência")

    assert "reenviou o documento pendente em 10/11/2026 12:00" in situacao.frase_da_pendencia
    assert situacao.frase_do_aviso == ""
    assert not situacao.oferece_o_aviso


def test_sem_pendencia_nem_reenvio_nao_ha_situacao():
    assert c.situacao_do_aviso(SimpleNamespace(pedidos=[_lido(nomes.ITEM_CONFORME)])) is None
    assert c.situacao_do_aviso(None) is None


# --- O índice (FR-5001 a FR-5004, D-002) --------------------------------------------------------


def _linha(estado, docs=None, *, vencimento=None, n=1, desfecho_=None, apto=False):
    return {
        "convocacao": SimpleNamespace(id=f"c{n}", vencimento=vencimento),
        "estado": estado,
        "desfecho": desfecho_,
        "documentos": docs,
        "apto": apto,
    }


def _leitura(linhas, **extra):
    por_estado = {
        estado: sum(1 for linha in linhas if linha["estado"] == estado)
        for estado in (
            nomes.CONVOCADO_PRAZO_NAO_INICIADO,
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            nomes.CONVOCADO_VENCIMENTO_DECORRIDO,
            nomes.DESFECHADO,
        )
    }
    return {
        "linhas": linhas,
        "porEstado": por_estado,
        "convocadas": len(linhas),
        "canal": canal.MENSAGEM,
        **extra,
    }


def _indice(leitura, **opcoes):
    padrao = {
        "titulares": None,
        "pode_convocar": True,
        "pode_emitir": True,
        "confere": True,
        "pendencias_a_avisar": None,
        "sem_inscrito": False,
        "marco_intermediario": None,
        "secao_dos_pendentes": False,
        "secao_dos_vencidos": False,
    }
    return {p.chave: p for p in c.indice(leitura=leitura, **{**padrao, **opcoes})}


def test_o_indice_leva_a_primeira_chamada_de_cada_pergunta():
    linhas = [
        _linha(
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_AGUARDANDO, a_apresentar=2),
            vencimento=AGORA + timedelta(days=9),
            n=1,
        ),
        _linha(
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_COM_PENDENCIA, pendentes=1),
            vencimento=AGORA + timedelta(days=3),
            n=2,
        ),
        _linha(
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            documentos(nomes.DOCUMENTOS_PARA_CONFERIR, recebidos=2),
            n=3,
        ),
    ]
    perguntas = _indice(
        _leitura(linhas),
        titulares={"pessoas": []},
        pendencias_a_avisar={"alcancadas": 1, "exclusoes": []},
    )

    assert perguntas["a_conferir"].ancora == "convocacao-c3"
    assert perguntas["a_conferir"].trabalho
    assert perguntas["pendencia"].ancora == "convocacao-c2"
    assert perguntas["pendencia"].detalhe == "1 pode ser avisada agora"
    assert perguntas["pendencia"].detalhe_ancora == "avisar-pendencias"
    assert not perguntas["pendencia"].trabalho  # é o candidato quem age
    assert perguntas["aguardando"].quantas == 3
    assert "13/11/2026" in perguntas["aguardando"].detalhe  # o primeiro vencimento
    assert perguntas["a_convocar"].quantas == 0 and perguntas["a_convocar"].ancora == ""
    assert not c.sem_providencia(list(perguntas.values()))


def test_a_ordem_do_indice_e_fixa():
    """D-002: as perguntas não mudam de lugar conforme o que há a fazer."""
    vazio = [p.chave for p in c.indice(leitura=_leitura([]), **_opcoes())]
    cheio = [
        p.chave
        for p in c.indice(
            leitura=_leitura(
                [
                    _linha(nomes.CONVOCADO_PRAZO_NAO_INICIADO, n=1),
                    _linha(nomes.CONVOCADO_VENCIMENTO_DECORRIDO, n=2),
                ]
            ),
            **_opcoes(),
        )
    ]

    assert [chave for chave in cheio if chave in vazio] == vazio
    assert cheio.index("sem_comunicacao") < cheio.index("convocadas")
    assert cheio.index("vencidas") < cheio.index("a_conferir")


def _opcoes(**extra):
    return {
        "titulares": {"pessoas": []},
        "pode_convocar": True,
        "pode_emitir": True,
        "confere": True,
        "pendencias_a_avisar": None,
        "sem_inscrito": False,
        "marco_intermediario": None,
        "secao_dos_pendentes": True,
        "secao_dos_vencidos": True,
        **extra,
    }


def test_quem_so_consulta_nao_tem_trabalho_marcado_nem_titulares():
    linhas = [_linha(nomes.CONVOCADO_PRAZO_NAO_INICIADO, n=1)]
    perguntas = {
        p.chave: p
        for p in c.indice(
            leitura=_leitura(linhas),
            **_opcoes(pode_convocar=False, pode_emitir=False, confere=False),
        )
    }

    assert "a_convocar" not in perguntas
    assert not any(p.trabalho for p in perguntas.values())


def test_sem_providencia_quando_ninguem_tem_ato():
    linhas = [
        _linha(nomes.DESFECHADO, desfecho_=desfecho(), apto=True, n=1),
        _linha(nomes.CONVOCADO_PRAZO_EM_CURSO, n=2),
    ]
    perguntas = c.indice(leitura=_leitura(linhas), **_opcoes())

    assert c.sem_providencia(perguntas)
    com_desfecho = next(p for p in perguntas if p.chave == "com_desfecho")
    assert com_desfecho.detalhe == "1 apta para formalização"


def test_lista_que_ninguem_declarou_nao_tem_perguntas():
    assert c.indice(leitura=_leitura([]), **_opcoes(sem_inscrito=True)) == []
