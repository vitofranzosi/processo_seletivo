"""A ficha de divulgação contra os cenários de referência (111, FR-3404 a FR-3411, FR-3448).

Os Editais chegam ao banco pelo fluxo real, a partir do corpus da `070` (`tests/fixtures/kit.py`).
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.portal import ficha as fichas
from processo_seletivo.portal.views import _selecao, _selecao_da_vitrine
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures import editais_do_piloto, kit

pytestmark = pytest.mark.django_db


def _ler(edital, agora=None, base_url=kit.BASE):
    return fichas.ler(edital, agora=agora or timezone.now(), base_url=base_url)


# ---- FR-3407: a ficha diz o que a vitrine e a página dizem -----------------------------------


@pytest.mark.parametrize("dias", [0, 3])
def test_a_ficha_diz_o_que_a_vitrine_e_a_pagina_dizem(api_client, dias):
    edital = kit.publicar(api_client, chave="kit-equivalencia")
    agora = timezone.now() + timedelta(days=dias)
    lida = _ler(edital, agora)
    versao = effective_version(edital_id=edital.id, at=agora)
    cartao = _selecao_da_vitrine(versao, agora, desfechos([versao.edital])[edital.id])
    pagina = _selecao(versao, agora)

    assert (lida.periodo_estado, lida.situacao_chave) == (
        cartao["periodo"].estado,
        cartao["situacao_chave"],
    )
    assert pagina["periodo"].estado == lida.periodo_estado
    assert lida.inicio == pagina["periodo"].inicio.astimezone(fichas.ZONA).isoformat()
    assert [(o.nome, o.quantidade) for o in lida.ofertas] == [
        (o["nome"], o["quantidade"]) for o in cartao["ofertas_todas"]
    ]


# ---- FR-3410: o modo ---------------------------------------------------------------------------


def test_inscricoes_futuras_e_em_andamento_tem_o_mesmo_material(api_client):
    edital = kit.publicar(api_client, ate=1, chave="kit-futuro")
    futuro = _ler(edital)
    andamento = _ler(edital, kit.inicio(edital) + timedelta(days=1))

    assert futuro.periodo_estado == "futuro"
    assert andamento.periodo_estado == "aberto"
    assert futuro.modo == andamento.modo == fichas.COM_PERIODO
    assert futuro.impressao == andamento.impressao


def test_sem_periodo_designado_e_neutro(api_client):
    edital = kit.publicar(api_client, chave="kit-neutro", mudar=kit.sem_periodo)
    lida = _ler(edital)
    assert lida.modo == fichas.NEUTRO
    assert lida.periodo_curto == ""


def test_cancelado_dentro_do_periodo_nao_tem_material(api_client):
    edital = editais_do_piloto.cancelado(api_client)
    lida = _ler(edital)
    assert lida.modo == fichas.SEM_MATERIAL
    assert "cancelado" in lida.motivo


def test_periodo_encerrado_nao_tem_material(api_client):
    edital = kit.publicar(api_client, ate=1, chave="kit-encerrado")
    fim = parse_datetime(kit.evento_das_inscricoes(edital)["endAt"])
    lida = _ler(edital, fim + timedelta(days=1))
    assert lida.modo == fichas.SEM_MATERIAL
    assert "encerradas" in lida.motivo


# ---- FR-3408: a proveniência pela regra da 070 ---------------------------------------------


def test_o_termino_prorrogado_vem_da_retificacao(api_client):
    edital = kit.publicar(api_client, ate=1, chave="kit-prorrogado")
    kit.retificar(api_client, edital, "91", 2, chave="kit-prorrogado")
    lida = _ler(edital, kit.inicio(edital) + timedelta(days=1))
    por_campo = {origem.campo: origem.atos for origem in lida.origens}

    assert por_campo["Término das inscrições"] == ("Retificação nº 1",)
    assert por_campo["Início das inscrições"] == ("Publicação original",)
    acrescidas = [atos for campo, atos in por_campo.items() if "Bom Jesus" in campo]
    assert acrescidas == [("Retificação nº 1",)]
    assert lida.prorrogado
    assert lida.versao_ato.startswith("Retificação nº 1")


# ---- FR-3404, EC-8: a versão futura só é anunciada -------------------------------------------


def test_versao_futura_nunca_e_aplicada(api_client):
    edital = kit.publicar(api_client, "01", chave="kit-a-vigorar")
    agora = kit.inicio(edital) + timedelta(hours=1)
    lida = _ler(edital, agora)

    assert lida.retificacao_a_vigorar
    assert not lida.prorrogado
    depois = _ler(edital, parse_datetime(lida.retificacao_a_vigorar) + timedelta(hours=1))
    assert depois.prorrogado
    assert depois.fim != lida.fim
    assert depois.impressao != lida.impressao


# ---- FR-3411, FR-3448: a impressão ---------------------------------------------------------


def test_impressao_nao_inclui_instante_versao_host_nem_ordem(api_client):
    edital = kit.publicar(api_client, ate=1, chave="kit-impressao")
    agora = timezone.now()
    um = _ler(edital, agora)
    outro_host = _ler(edital, agora + timedelta(days=2), base_url="http://outro.exemplo:8000")
    assert um.impressao == outro_host.impressao
    assert um.versao_da_impressao == fichas.VERSAO_DA_IMPRESSAO

    # A ordem publicada não entra: as ofertas vão pela identidade (D-018).
    ofertas = um.campos["ofertas"]
    assert ofertas == sorted(ofertas, key=lambda oferta: oferta["perfil_id"])


# ---- FR-3406, FR-3409, FR-3425 ---------------------------------------------------------------


def test_total_so_com_vaga_em_todas(api_client):
    noventa_e_um = _ler(kit.publicar(api_client, ate=1, chave="kit-total-91"))
    assert noventa_e_um.total_de_vagas == 160
    assert noventa_e_um.nomes_iguais


def test_cadastro_reserva_sem_vaga_nao_soma(api_client):
    zero_um = _ler(kit.publicar(api_client, "01", ate=1, chave="kit-total-01"))
    assert zero_um.total_de_vagas is None
    assert [o.quantidade for o in zero_um.ofertas] == [
        "2 vagas e cadastro reserva",
        "cadastro reserva",
    ]


def test_nome_e_localidade_literais_e_titulo_sem_numero(api_client):
    lida = _ler(kit.publicar(api_client, ate=1, chave="kit-literais"))
    assert lida.ofertas[0].localidade == "Polo Bom Jesus do Norte"
    assert lida.titulo.startswith("Edital nº 91/2026")
    assert lida.titulo_sem_numero.startswith("Curso de Pós-graduação")
    assert lida.unidade_sigla == "Cefor"


def test_localidade_ausente_fica_vazia(api_client):
    lida = _ler(kit.publicar(api_client, chave="kit-sem-local", mudar=kit.sem_localidade))
    assert [o.localidade for o in lida.ofertas] == ["Polo Bom Jesus do Norte", ""]


def test_termo_em_valor_oficial_e_apontado(api_client):
    lida = _ler(kit.publicar(api_client, chave="kit-termo", mudar=kit.termo_no_titulo))
    assert "São Marcos" in lida.titulo
    assert lida.termos_em_valor_oficial


# ---- EC-25, EC-7: a hora e o ano ------------------------------------------------------------


def test_prorrogacao_so_de_hora(api_client):
    """O 01/2026 termina às 09h43; adiado para as 18h do mesmo dia, a hora vai nas duas pontas."""
    edital = kit.publicar(api_client, "01", ate=1, chave="kit-hora")
    fim = parse_datetime(kit.evento_das_inscricoes(edital)["endAt"]).astimezone(fichas.ZONA)
    kit.retificar_termino(api_client, edital, fim.replace(hour=18, minute=0), suffix="kit-hora")
    lida = _ler(edital, kit.inicio(edital) + timedelta(hours=1))

    assert lida.prorrogado
    assert lida.fim_original_texto.endswith("09h43")
    assert lida.fim_vigente_texto.endswith("18h00")
    assert lida.fim_original_texto[:10] == lida.fim_vigente_texto[:10]


def test_periodo_curto_repete_o_ano_so_se_muda():
    from datetime import datetime

    mesmo = fichas._periodo_curto(
        datetime(2026, 11, 4, 12, tzinfo=fichas.ZONA),
        datetime(2026, 11, 26, 23, 59, tzinfo=fichas.ZONA),
    )
    virada = fichas._periodo_curto(
        datetime(2026, 12, 15, 12, tzinfo=fichas.ZONA),
        datetime(2027, 1, 10, 23, 59, tzinfo=fichas.ZONA),
    )
    assert mesmo == "04/11 a 26/11/2026"
    assert virada == "15/12/2026 a 10/01/2027"


# ---- FR-3439: o de → para ---------------------------------------------------------------------


def _campos(**mudar):
    base = {
        "numero": "91",
        "ano": "2026",
        "titulo": "T",
        "titulo_do_processo": "P",
        "unidade": "Cefor",
        "inicio": "2026-11-04T09:00:00-03:00",
        "fim": "2026-11-21T23:59:00-03:00",
        "cancelado": False,
        "designado": True,
        "caminho": "/selecoes/x/",
        "ofertas": [
            {
                "perfil_id": "a",
                "nome": "Curso",
                "localidade": "Iúna",
                "vagas": 40,
                "reserva": False,
            },
            {
                "perfil_id": "b",
                "nome": "Curso",
                "localidade": "Serra",
                "vagas": 40,
                "reserva": False,
            },
        ],
    }
    base.update(mudar)
    return base


def test_diferencas_nomeiam_o_campo_e_os_dois_valores():
    novos = _campos(fim="2026-11-26T23:59:00-03:00")
    mudancas = fichas.diferencas(_campos(), novos)
    assert [(m.campo, m.de, m.para) for m in mudancas] == [
        ("término das inscrições", "21/11/2026, 23h59", "26/11/2026, 23h59")
    ]


def test_perfil_retirado_acrescentado_renomeado_e_reordenado():
    antigos = _campos()
    novos = _campos(
        ofertas=[
            {
                "perfil_id": "b",
                "nome": "Curso",
                "localidade": "Serra Sede",
                "vagas": 40,
                "reserva": False,
            },
            {
                "perfil_id": "c",
                "nome": "Curso",
                "localidade": "Linhares",
                "vagas": 10,
                "reserva": True,
            },
        ]
    )
    campos = {m.campo: (m.de, m.para) for m in fichas.diferencas(antigos, novos)}
    assert campos["nome da opção"] == ("Curso — Serra", "Curso — Serra Sede")
    assert campos["opção Curso — Linhares"][1].startswith("acrescentada")
    assert campos["opção Curso — Iúna"] == ("40 vagas", "retirada")
    assert (
        fichas.diferencas(antigos, dict(antigos, ofertas=list(reversed(antigos["ofertas"])))) == ()
    )
