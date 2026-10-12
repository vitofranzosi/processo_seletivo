"""Os defeitos que a revisão de código de 12/10 achou na camada de conteúdo, um caso cada (070).

Nenhum deles aparecia no corpus como publicado: cada caso troca uma parte do conteúdo, vigente ou
futuro, pelo que a validação de publicação admite e o corpus não tem. As origens de cada defeito
estão nos comentários do código que o corrigiu.
"""

import copy
from dataclasses import replace

import pytest

from processo_seletivo.duvidas.domain import catalogo, leitura, rotulos
from processo_seletivo.duvidas.domain.estruturas import (
    AVISO_REDACAO_ALCANCA_MAIS,
    AVISO_RETIFICACAO_FUTURA,
    DADO,
    DEPENDE_DA_LEITURA,
    AtoPublicado,
    Desfecho,
)
from processo_seletivo.duvidas.domain.origem import acrescimos, origens
from processo_seletivo.duvidas.domain.respostas import responder
from tests.fixtures.corpus import contexto_do_corpus
from tests.unit.duvidas.conftest import em

ANTES_DA_VIGENCIA_FUTURA = em("2026-10-20T12:00:00-03:00")


def _perfil(conteudo, codigo):
    return next(perfil for perfil in conteudo["profiles"] if perfil["code"] == codigo)


def _com_futuro(contexto, mudar):
    """O contexto com a primeira versão futura alterada por `mudar(conteudo)`."""
    futura = contexto.futuras[0]
    conteudo = copy.deepcopy(futura.conteudo)
    mudar(conteudo)
    return replace(contexto, futuras=(replace(futura, conteudo=conteudo), *contexto.futuras[1:]))


def _aviso(resposta, tipo):
    return next(aviso for aviso in resposta.avisos if aviso.tipo == tipo)


def _dados(resposta):
    return {r.rotulo: r for r in resposta.referencias if r.natureza == DADO}


# ---- o valor futuro sai nas palavras do cartão (`FR-1414`) -----------------------------------


def test_o_valor_futuro_vem_nas_palavras_do_cartao_e_nao_cru():
    def mudar(conteudo):
        _perfil(conteudo, "DOC-INFO")["reserveType"] = "UNLIMITED"

    contexto = _com_futuro(contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA), mudar)
    resposta = responder(contexto, "P-03", perfil="DOC-INFO")
    reserva = _dados(resposta)["Cadastro de reserva"]
    esperado = rotulos.em_palavras(rotulos.RESERVA, "UNLIMITED")
    assert [valor.valor for valor in reserva.futuro] == [esperado]
    aviso = _aviso(resposta, AVISO_RETIFICACAO_FUTURA).texto
    assert esperado in aviso
    assert "UNLIMITED" not in aviso


def test_requisito_acrescentado_no_inicio_nao_desloca_os_outros():
    def mudar(conteudo):
        perfil = _perfil(conteudo, "DOC-INFO")
        perfil["requirements"] = ["Requisito novo, no início", *perfil["requirements"]]

    contexto = _com_futuro(contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA), mudar)
    resposta = responder(contexto, "P-04", perfil="DOC-INFO")
    aviso = _aviso(resposta, AVISO_RETIFICACAO_FUTURA).texto
    assert "passa a constar Requisito" in aviso and "Requisito novo, no início" in aviso
    assert "passa a ser" not in aviso
    assert "deixa de constar" not in aviso


def test_evento_acrescentado_no_futuro_nao_e_dito_como_sem_mudanca():
    def mudar(conteudo):
        evento = copy.deepcopy(conteudo["schedule"][-1])
        evento["id"] = "00000000-0000-4000-8000-0000000000e9"
        evento["type"] = "Evento acrescentado pela Retificação"
        evento["startAt"] = "2026-12-20T10:00:00-03:00"
        evento["endAt"] = "2026-12-21T10:00:00-03:00"
        conteudo["schedule"].append(evento)

    contexto = _com_futuro(contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA), mudar)
    aviso = _aviso(responder(contexto, "P-02"), AVISO_RETIFICACAO_FUTURA).texto
    assert "Ela não altera o que esta resposta cita" not in aviso
    assert "passa a constar" in aviso and "20/12/2026" in aviso


def test_a_retificacao_futura_e_nomeada_pela_data_da_propria_retificacao():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA)
    aviso = _aviso(responder(contexto, "P-01"), AVISO_RETIFICACAO_FUTURA).texto
    retificacao = contexto.futuras[0].atos[-1]
    assert f"por Retificação publicada em {leitura.instante_legivel(retificacao.publicado_em)}" in (
        aviso
    )


# ---- P-05: a redação que alcança mais (`R-008`) -----------------------------------------------


def test_o_documento_divergente_tem_cartao_e_aviso():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA)
    conteudo = copy.deepcopy(contexto.conteudo)
    ampla_do_doc_info = next(
        m for m in _perfil(conteudo, "DOC-INFO")["competitionModalities"] if m["code"] == "AC"
    )
    documento = conteudo["documentRequirements"][-1]
    documento.pop("profileId", None)
    documento["modalityId"] = ampla_do_doc_info["id"]
    resposta = responder(
        replace(contexto, conteudo=conteudo, futuras=()), "P-05", perfil="TEC-LAB", modalidade="AC"
    )
    assert resposta.tipo == DEPENDE_DA_LEITURA
    assert AVISO_REDACAO_ALCANCA_MAIS in [aviso.tipo for aviso in resposta.avisos]
    assert any(documento["name"] in r.localizacao for r in resposta.referencias)


def test_a_explicacao_dos_documentos_nao_diz_que_o_facultativo_e_exigido():
    resposta = responder(
        contexto_do_corpus("91", ANTES_DA_VIGENCIA_FUTURA),
        "P-05",
        perfil="INF-BJN",
        modalidade="nenhuma",
    )
    assert "facultativo" in [r.conteudo for r in resposta.referencias]
    assert "exige" not in resposta.explicacao.conteudo


# ---- P-02: desfecho e Eventos cancelados ------------------------------------------------------


def test_o_desfecho_do_edital_prevalece_sobre_o_cronograma():
    contexto = replace(
        contexto_do_corpus("92", ANTES_DA_VIGENCIA_FUTURA),
        desfecho=Desfecho("EDITAL", "CANCELADO", em("2026-10-15T12:00:00-03:00"), True),
    )
    explicacao = responder(contexto, "P-02").explicacao.conteudo
    assert "Em andamento" not in explicacao
    assert "desfecho" in explicacao


def test_eventos_cancelados_nao_sao_ditos_como_passados():
    contexto = contexto_do_corpus("92", ANTES_DA_VIGENCIA_FUTURA)
    conteudo = copy.deepcopy(contexto.conteudo)
    for evento in conteudo["schedule"]:
        evento["status"] = "CANCELADO"
    explicacao = responder(replace(contexto, conteudo=conteudo), "P-02").explicacao.conteudo
    assert "passaram" not in explicacao


# ---- ausente não é zero nem "não" (`FR-1416`, `FR-1422`) --------------------------------------


def test_vagas_imediatas_ausentes_nao_viram_zero():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA)
    conteudo = copy.deepcopy(contexto.conteudo)
    del _perfil(conteudo, "DOC-INFO")["immediateVacancies"]
    resposta = responder(
        replace(contexto, conteudo=conteudo, futuras=()), "P-03", perfil="DOC-INFO"
    )
    assert _dados(resposta)["Vagas imediatas"].conteudo == "não declarado"
    assert "não tem vagas" not in resposta.explicacao.conteudo
    assert "não declara a quantidade de vagas imediatas" in resposta.explicacao.conteudo


def test_carater_da_etapa_ausente_nao_vira_nao():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA)
    conteudo = copy.deepcopy(contexto.conteudo)
    for etapa in conteudo["stages"]:
        etapa.pop("eliminatory", None)
    resposta = responder(
        replace(contexto, conteudo=conteudo, futuras=()), "P-07", perfil="DOC-INFO"
    )
    eliminatorias = [r.conteudo for r in resposta.referencias if r.rotulo == "Eliminatória"]
    assert eliminatorias and set(eliminatorias) == {"não declarado"}


def test_instante_inexistente_ou_sem_zona_nao_derruba_nem_usa_a_zona_da_maquina():
    assert leitura.instante_legivel("2026-02-30T10:00:00-03:00") == "“2026-02-30T10:00:00-03:00”"
    assert leitura.instante_legivel("2026-10-05T14:00:00") == leitura.instante_legivel(
        "2026-10-05T14:00:00-03:00"
    )


# ---- a oferta por Perfil (`FR-1417`) ----------------------------------------------------------


def test_sorteio_de_um_perfil_nao_e_oferecido_a_outro():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA)
    conteudo = copy.deepcopy(contexto.conteudo)
    _perfil(conteudo, "DOC-INFO")["classificationMilestones"][0]["orderProduction"] = "POR_SORTEIO"
    contexto = replace(contexto, conteudo=conteudo, futuras=())
    assert "P-09" in [pergunta.codigo for pergunta in catalogo.oferecidas(conteudo)]
    with pytest.raises(catalogo.ParametroRecusado, match="não se aplica ao Perfil TEC-LAB"):
        responder(contexto, "P-09", perfil="TEC-LAB")


def test_perfil_sem_marco_mostra_as_etapas_do_edital():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA)
    conteudo = copy.deepcopy(contexto.conteudo)
    _perfil(conteudo, "TEC-LAB")["classificationMilestones"] = []
    resposta = responder(replace(contexto, conteudo=conteudo, futuras=()), "P-07", perfil="TEC-LAB")
    nomes = {r.conteudo for r in resposta.referencias if r.rotulo == "Nome"}
    assert nomes == {etapa["name"] for etapa in conteudo["stages"]}
    assert "não as liga a um marco" in resposta.explicacao.conteudo


# ---- a mudança de versão nos dois sentidos (`FR-1415`) ----------------------------------------


def test_a_versao_anterior_mais_nova_diz_o_que_deixou_de_valer():
    contexto = contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA, versao_anterior="01-v3")
    mudanca = responder(contexto, "P-01").mudanca
    assert mudanca.atos == ()
    assert [ato.publicacao_id for ato in mudanca.sem_efeito] == ["01-pub3"]


# ---- a origem da entidade acrescentada por Retificação (`FR-1437`, `SC-535`) ------------------


def _ato(identificador, ordem):
    data = em(f"2026-10-0{ordem}T12:00:00-03:00")
    return AtoPublicado(
        identificador,
        "ORIGINAL" if ordem == 1 else "RETIFICACAO",
        ordem,
        data,
        data,
        f"/doc/{identificador}",
        (identificador,),
    )


def test_o_perfil_acrescentado_leva_ao_ato_que_o_acrescentou():
    original, r1, r2 = _ato("O", 1), _ato("R1", 2), _ato("R2", 3)
    # O seletor `id=` da gramática da `004` só aceita UUID.
    A, B, C = (f"00000000-0000-4000-8000-00000000000{letra}" for letra in "abc")
    base = {"profiles": [{"id": A, "code": "A"}]}
    depois_r1 = {"profiles": [{"id": A, "code": "A"}, {"id": B, "code": "B"}]}
    depois_r2 = {"profiles": [*depois_r1["profiles"], {"id": C, "code": "C"}]}
    # `consolidate` guarda um registro por caminho: o de R1 em `/profiles/-` foi sobrescrito por R2.
    proveniencias = (("/profiles/-", "R2"),)
    atos = (original, r1, r2)
    novos = acrescimos(
        proveniencias, depois_r2, atos, {"O": base, "R1": depois_r1, "R2": depois_r2}
    )
    completas = proveniencias + novos
    assert [o.publicacao_id for o in origens(f"/profiles/id={A}/code", completas, atos)] == ["O"]
    assert [o.publicacao_id for o in origens(f"/profiles/id={B}/code", completas, atos)] == ["R1"]
    assert [o.publicacao_id for o in origens(f"/profiles/id={C}/code", completas, atos)] == ["R2"]


def test_sem_acrescimo_nao_ha_registro_novo():
    assert acrescimos((("/profiles/id=A/code", "R1"),), {"profiles": []}, (_ato("O", 1),), {}) == ()


# ---- o desfecho do Processo, que o fluxo real não alcança sozinho (`R-006`) -------------------


def test_o_desfecho_do_processo_e_dito_mas_nao_fecha_o_periodo():
    contexto = replace(
        contexto_do_corpus("91", ANTES_DA_VIGENCIA_FUTURA),
        desfecho=Desfecho("PROCESSO", "CANCELADO", em("2026-10-15T12:00:00-03:00"), False),
    )
    resposta = responder(contexto, "P-01")
    assert any("O Processo Seletivo deste Edital foi cancelado" in a.texto for a in resposta.avisos)
    assert resposta.explicacao.conteudo.startswith("As inscrições estão abertas")


def test_desfecho_sem_data_vale_so_para_o_presente(monkeypatch):
    """`R-006`: sem o ato encontrado, o desfecho não se data, e dizê-lo no passado afirmaria um
    cancelamento que pode ser posterior ao instante."""
    from datetime import timedelta
    from types import SimpleNamespace

    from django.utils import timezone

    from processo_seletivo.duvidas.application import consultar

    sem_data = SimpleNamespace(alcance="EDITAL", operacao="CANCELADO", em=None, do_edital=True)
    monkeypatch.setattr(consultar, "desfechos", lambda editais: {1: sem_data})
    edital = SimpleNamespace(id=1)
    assert consultar._desfecho(edital, timezone.now() - timedelta(days=3)) is None
    assert consultar._desfecho(edital, timezone.now()).do_edital is True


# ---- o cadastro de reserva e a reversão (`FR-1428`) -------------------------------------------


def test_cadastro_de_reserva_limite_e_reversao_vem_em_palavras():
    """A `FR-1428` citava o `CA-01`, que não confere nem a reserva nem a reversão."""
    doc_info = _dados(
        responder(contexto_do_corpus("01", ANTES_DA_VIGENCIA_FUTURA), "P-03", perfil="DOC-INFO")
    )
    assert doc_info["Cadastro de reserva"].conteudo == rotulos.em_palavras(
        rotulos.RESERVA, "LIMITED"
    )
    assert doc_info["Limite do cadastro de reserva"].conteudo == "6"

    inf_bjn = responder(
        contexto_do_corpus("91", ANTES_DA_VIGENCIA_FUTURA), "P-03", perfil="INF-BJN"
    )
    reversao = _dados(inf_bjn)["Reverter vaga reservada não preenchida para a ampla concorrência"]
    assert reversao.conteudo == rotulos.em_palavras(rotulos.REVERSAO, "ON_EXHAUSTION")
    assert "não forma cadastro de reserva" in inf_bjn.explicacao.conteudo
