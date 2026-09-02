"""`definir_distribuicao` — o desenho inteiro num ato, com escopo declarado.

O escopo é a decisão que impede perda de dado: a matriz filtra linhas, e se o comando deduzisse
a distribuição a partir do que veio marcado, filtrar por "Ana" e salvar removeria todo mundo que
não se chama Ana.
"""

import uuid

import pytest

from processo_seletivo.comissoes.application.alocacao import definir_distribuicao
from processo_seletivo.comissoes.models import AlocacaoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em, constituir

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def salvar(gestor, processo, edital, membros, etapas, marcadas, chave="dist-1", **extra):
    return definir_distribuicao(
        actor=gestor,
        processo_id=processo.id,
        escopo_membros=[m.id for m in membros],
        escopo_etapas=[f"{edital.id}:{e}" for e in etapas],
        marcadas=marcadas,
        idempotency_key=chave,
        correlation_id="c",
        **extra,
    )


def test_cria_o_que_faltava_e_remove_o_que_sobrava(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    maria, joao = comissao_de_a["maria"], comissao_de_a["joao"]
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)

    criadas, removidas = salvar(
        gestor,
        processo_a,
        edital_a,
        [maria, joao],
        [etapa_a1, etapa_a2],
        [f"{edital_a.id}:{etapa_a2}:{joao.id}", f"{edital_a.id}:{etapa_a1}:{maria.id}"],
    )

    assert len(criadas) == 2 and len(removidas) == 1
    ativas = {(str(a.etapa_id), a.membro_id) for a in AlocacaoEtapa.objects.filter(ativo=True)}
    assert ativas == {(etapa_a2, joao.id), (etapa_a1, maria.id)}


def test_o_que_esta_fora_do_escopo_nao_e_tocado(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """A garantia central: a tela filtrada só afeta quem ela desenhou."""
    maria, joao = comissao_de_a["maria"], comissao_de_a["joao"]
    alocar_em(gestor, processo_a, maria, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)

    salvar(gestor, processo_a, edital_a, [joao], [etapa_a2], [])

    assert AlocacaoEtapa.objects.filter(membro=maria, ativo=True).count() == 1
    assert AlocacaoEtapa.objects.filter(membro=joao, ativo=True).count() == 0


def test_a_coluna_inteira_e_o_inverso(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    membros = list(comissao_de_a.values())
    coluna = f"{edital_a.id}:{etapa_a1}"

    salvar(gestor, processo_a, edital_a, membros, [etapa_a1], [], coluna_todos=coluna)
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 2

    marcadas = [f"{coluna}:{m.id}" for m in membros]
    salvar(
        gestor,
        processo_a,
        edital_a,
        membros,
        [etapa_a1],
        marcadas,
        chave="dist-2",
        coluna_nenhum=coluna,
    )
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 0


def test_marcacao_fora_do_escopo_e_recusada(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """Envio forjado não é engano de quem opera."""
    maria, joao = comissao_de_a["maria"], comissao_de_a["joao"]

    with pytest.raises(DomainError) as recusa:
        salvar(
            gestor,
            processo_a,
            edital_a,
            [maria],
            [etapa_a1],
            [f"{edital_a.id}:{etapa_a1}:{joao.id}"],
        )

    assert recusa.value.status == 404
    assert AlocacaoEtapa.objects.count() == 0


def test_escopo_ausente_e_recusado(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    with pytest.raises(DomainError) as recusa:
        salvar(gestor, processo_a, edital_a, [], [], [])

    assert recusa.value.code == "escopo_ausente"


def test_membro_que_saiu_durante_a_edicao_recusa_o_ato(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    from processo_seletivo.comissoes.application.comissao import remover_membro

    joao = comissao_de_a["joao"]
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        idempotency_key="saiu",
        correlation_id="c",
    )

    with pytest.raises(DomainError) as recusa:
        salvar(gestor, processo_a, edital_a, list(comissao_de_a.values()), [etapa_a1], [])

    assert recusa.value.code == "selecao_desatualizada"
    assert recusa.value.status == 409


def test_distribuir_exige_presidente(gestor, processo_a, edital_a, etapa_a1):
    membros = constituir(gestor, processo_a, [("joao", "MEMBRO")])
    joao = membros["joao"]

    with pytest.raises(DomainError) as recusa:
        salvar(
            gestor,
            processo_a,
            edital_a,
            [joao],
            [etapa_a1],
            [f"{edital_a.id}:{etapa_a1}:{joao.id}"],
        )

    assert recusa.value.code == "comissao_sem_presidente"


def test_etapa_fora_do_conteudo_vigente_e_recusada(gestor, processo_a, edital_a, comissao_de_a):
    with pytest.raises(DomainError) as recusa:
        salvar(
            gestor,
            processo_a,
            edital_a,
            list(comissao_de_a.values()),
            [str(uuid.uuid4())],
            [],
        )

    assert recusa.value.status == 404


def test_cada_mudanca_gera_o_seu_evento(
    gestor, auditor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    from processo_seletivo.auditoria.selectors import trilha_da_comissao

    maria, joao = comissao_de_a["maria"], comissao_de_a["joao"]
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)

    salvar(
        gestor,
        processo_a,
        edital_a,
        [maria, joao],
        [etapa_a1, etapa_a2],
        [f"{edital_a.id}:{etapa_a2}:{joao.id}"],
    )

    registros, _ = trilha_da_comissao(actor=auditor, processo=processo_a, limit=100)
    pela_distribuicao = [r for r in registros if "pela distribuição" in r.reason]
    assert {r.operation for r in pela_distribuicao} == {"ALOCACAO_INCLUIR", "ALOCACAO_REMOVER"}


def test_salvar_sem_mudanca_nenhuma_nao_gera_evento(
    gestor, auditor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    antes = RegistroAuditoria.objects.count()

    salvar(gestor, processo_a, edital_a, list(comissao_de_a.values()), [etapa_a1], [])

    assert RegistroAuditoria.objects.count() == antes
