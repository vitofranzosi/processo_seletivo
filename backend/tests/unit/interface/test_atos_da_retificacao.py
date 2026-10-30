"""A derivação do que a Retificação pede a seguir, sem banco (103, R-001).

A Lista, o detalhe do Edital, a tela de Retificar, o detalhe da Retificação e a confirmação leem
daqui (FR-2730). Estes casos fixam a tabela de quem age a seguir, o "é você" e a segregação
antecipada — sem nenhuma requisição, para que a regra se leia sozinha.
"""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from processo_seletivo.interface import atos_retificacao
from processo_seletivo.interface.identidade import permissoes_de
from processo_seletivo.seguranca.domain import Actor


def ator(subject, *papeis):
    return Actor(subject, "cefor", permissoes_de(list(papeis)))


def retificacao(status, prepared_by="", homologated_by=""):
    return SimpleNamespace(
        id=uuid4(), status=status, prepared_by=prepared_by, homologated_by=homologated_by
    )


@pytest.mark.parametrize(
    ("status", "papel", "chave"),
    [
        ("EM_ELABORACAO", "quem elabora", "submeter"),
        ("EM_REVISAO", "quem homologa", "homologar"),
        ("HOMOLOGADA", "quem publica", "publicar"),
    ],
)
def test_quem_age_a_seguir_sai_da_situacao(status, papel, chave):
    passo = atos_retificacao.proximo_passo(retificacao(status), ator("leitor"))

    assert (passo["papel"], passo["chave"]) == (papel, chave)
    assert passo["sou_eu"] is False


@pytest.mark.parametrize("status", ["PUBLICADA", "CANCELADA"])
def test_situacao_final_nao_tem_proximo_responsavel(status):
    assert atos_retificacao.proximo_passo(retificacao(status), ator("x", *TODOS)) is None
    assert status not in atos_retificacao.EM_CURSO


TODOS = ("elaborador", "homologador", "publicador", "gestor")


@pytest.mark.parametrize(
    ("status", "papel"),
    [("EM_ELABORACAO", "elaborador"), ("EM_REVISAO", "homologador"), ("HOMOLOGADA", "publicador")],
)
def test_e_voce_quando_o_ato_principal_esta_entre_os_seus(status, papel):
    passo = atos_retificacao.proximo_passo(retificacao(status), ator("pessoa", papel))

    assert passo["sou_eu"] is True
    assert passo["oferta"].disponivel


def test_as_ofertas_sao_os_atos_disponiveis_quando_nao_ha_segregacao():
    item = retificacao("HOMOLOGADA", prepared_by="ana", homologated_by="bruno")
    carla = ator("carla", *TODOS)

    assert [o.ato.chave for o in atos_retificacao.ofertas(item, carla)] == [
        ato.chave for ato in atos_retificacao.disponiveis(item, carla)
    ]
    assert all(o.disponivel for o in atos_retificacao.ofertas(item, carla))


def test_quem_submeteu_e_homologou_ve_publicar_desabilitado_com_o_motivo():
    item = retificacao("HOMOLOGADA", prepared_by="dora", homologated_by="dora")
    dora = ator("dora", *TODOS)

    publicar = next(o for o in atos_retificacao.ofertas(item, dora) if o.ato.chave == "publicar")
    passo = atos_retificacao.proximo_passo(item, dora)

    assert publicar.motivo == atos_retificacao.SEGREGACAO
    assert passo["sou_eu"] is False
    assert passo["observacao"] == atos_retificacao.SEGREGACAO
    assert atos_retificacao.impedimento(item, dora, publicar.ato) == {
        "motivo": "segregacao",
        "texto": atos_retificacao.SEGREGACAO,
    }


def test_so_ter_submetido_nao_impede_publicar():
    """A regra é a das três etapas: submeter e publicar, com outra pessoa no meio, é permitido."""
    item = retificacao("HOMOLOGADA", prepared_by="dora", homologated_by="bruno")

    assert atos_retificacao.proximo_passo(item, ator("dora", *TODOS))["sou_eu"] is True


def test_homologar_o_que_submeteu_avisa_sem_impedir():
    item = retificacao("EM_REVISAO", prepared_by="dora")
    dora = ator("dora", *TODOS)
    homologar = atos_retificacao.ATOS["homologar"]

    assert atos_retificacao.fecharia_a_publicacao(item, dora, homologar) is True
    assert atos_retificacao.impedimento(item, dora, homologar) is None
    assert atos_retificacao.fecharia_a_publicacao(item, ator("bruno", *TODOS), homologar) is False


def test_a_permissao_continua_vindo_antes_da_situacao_e_da_segregacao():
    item = retificacao("HOMOLOGADA", prepared_by="dora", homologated_by="dora")

    assert atos_retificacao.impedimento(
        item, ator("dora", "homologador"), atos_retificacao.ATOS["publicar"]
    ) == {"motivo": "permissao", "permissao": "retificacao:publicar"}


def test_a_situacao_vem_antes_da_segregacao():
    item = retificacao("EM_REVISAO", prepared_by="dora", homologated_by="dora")

    assert (
        atos_retificacao.impedimento(item, ator("dora", *TODOS), atos_retificacao.ATOS["publicar"])[
            "motivo"
        ]
        == "situacao"
    )


@pytest.mark.parametrize(
    ("status", "papeis", "pode"),
    [
        ("EM_ELABORACAO", ("elaborador",), True),
        ("EM_ELABORACAO", ("homologador", "publicador", "gestor"), False),
        ("EM_REVISAO", ("elaborador",), False),
        ("HOMOLOGADA", ("elaborador",), False),
    ],
)
def test_a_edicao_so_e_oferecida_a_quem_elabora_em_elaboracao(status, papeis, pode):
    assert atos_retificacao.pode_editar(retificacao(status), ator("x", *papeis)) is pode


@pytest.mark.parametrize(
    ("chave", "papel"),
    [("submeter", "quem homologa"), ("homologar", "quem publica"), ("devolver", "quem elabora")],
)
def test_cada_ato_diz_a_quem_entrega(chave, papel):
    assert atos_retificacao.entrega(atos_retificacao.ATOS[chave]) == papel


def test_publicar_e_cancelar_nao_entregam_a_ninguem():
    assert atos_retificacao.entrega(atos_retificacao.ATOS["publicar"]) == ""
    assert atos_retificacao.entrega(atos_retificacao.ATOS["cancelar"]) == ""
