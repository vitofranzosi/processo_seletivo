"""O número do cadastro de reserva, derivado do corte do marco que convoca (162, T003, T004).

**Puro, e por isso aqui.** A derivação recebe o Perfil do conteúdo e responde; os casos montam o
Perfil à mão, com o mínimo que a conta lê — quadro, marcos e regra de corte —, para que cada caso
diga qual peça muda o número.
"""

import pytest

from processo_seletivo.editais.domain import cadastro_de_reserva as cadastro

ETAPA_DA_ENTREVISTA = "00000000-0000-0000-0000-0000000000e1"
ETAPA_FINAL = "00000000-0000-0000-0000-0000000000e2"


def regra(*, alvo=None, excedente=0, continuacao="NONE", empate="STRICT", governada="NONE"):
    return {
        "targetKind": "FIXED" if alvo is not None else "FROM_VACANCY_TABLE",
        "targetCount": alvo,
        "surplusCount": excedente,
        "tieOutcome": empate,
        "governedStage": governada,
        "continuation": continuacao,
    }


def marco(identidade="m1", *, corte=None, nome="Classificação final", etapas=(ETAPA_FINAL,)):
    item = {"id": identidade, "name": nome, "stages": list(etapas)}
    if corte is not None:
        item["cutRule"] = corte
    return item


def perfil(*, especie="LIMITED", vagas=2, marcos=None, quadro=None, modalidades=(), limite=None):
    return {
        "id": "p1",
        "code": "P1",
        "immediateVacancies": vagas,
        "reserveType": especie,
        "reserveLimit": limite,
        "competitionModalities": list(modalidades),
        "vacancyTable": quadro if quadro is not None else [],
        "classificationMilestones": marcos if marcos is not None else [],
    }


def tres_listas():
    modalidades = [
        {"id": "pcd", "code": "PcD", "name": "Pessoas com deficiência"},
        {"id": "ppi", "code": "PPI", "name": "Pretos, pardos e indígenas"},
    ]
    quadro = [
        {"id": "l0", "modalityId": None, "immediateVacancies": 2},
        {"id": "l1", "modalityId": "pcd", "immediateVacancies": 1},
        {"id": "l2", "modalityId": "ppi", "immediateVacancies": 1},
    ]
    return modalidades, quadro


# --- A conta (FR-6929, T-006) -------------------------------------------------------------------


def test_com_alvo_do_quadro_o_numero_e_o_excedente():
    c = cadastro.do_perfil(perfil(marcos=[marco(corte=regra(excedente=3))]))
    assert [lista.numero for lista in c.por_lista] == [3]
    assert c.numero_unico == 3


def test_com_alvo_fixo_e_o_alcance_menos_as_vagas():
    so_reserva = perfil(vagas=0, marcos=[marco(corte=regra(alvo=4, excedente=2))])
    assert cadastro.do_perfil(so_reserva).numero_unico == 6
    sem_excedente = perfil(vagas=2, marcos=[marco(corte=regra(alvo=2))])
    assert cadastro.do_perfil(sem_excedente).numero_unico == 0
    alvo_menor = perfil(vagas=2, marcos=[marco(corte=regra(alvo=1))])
    assert cadastro.do_perfil(alvo_menor).numero_unico == -1


def test_o_perfil_do_seed_demo_da_dois_em_cada_lista():
    """Alvo de 2 e excedente de 1 em cada lista, com 1 vaga em cada: o "limitado em 6" da
    demonstração era 2 em cada lista (o alvo fixo vale por lista, a FR-4553 da `133`)."""
    from processo_seletivo.processos.management.commands import seed_demo

    (demo,) = [p for p in seed_demo.perfis("00") if p["code"] == "DOC-INFO"]
    c = cadastro.do_perfil(demo)
    assert [lista.numero for lista in c.por_lista] == [2, 2]
    assert c.numero_unico == 2
    assert c.com_modalidade


def test_por_lista_com_nomes_e_codigos():
    modalidades, quadro = tres_listas()
    c = cadastro.do_perfil(
        perfil(vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))])
    )
    assert [(lista.codigo, lista.numero) for lista in c.por_lista] == [
        ("AC", 1),
        ("PcD", 2),
        ("PPI", 2),
    ]
    assert c.por_lista[0].nome == "Ampla concorrência"
    assert c.por_lista[1].nome == "Pessoas com deficiência"
    assert c.numero_unico is None
    assert c.com_modalidade


def test_perfil_sem_quadro_tem_so_a_linha_geral():
    c = cadastro.do_perfil(perfil(vagas=5, quadro=[], marcos=[marco(corte=regra(alvo=7))]))
    assert [(lista.lista_id, lista.numero) for lista in c.por_lista] == [(None, 2)]
    assert not c.com_modalidade


# --- O marco que convoca (T-005, a FR-4531 da `133`) -------------------------------------------


def test_o_marco_intermediario_nao_conta():
    intermediario = marco(
        "m1",
        nome="Classificação para a entrevista",
        corte=regra(alvo=10, governada=ETAPA_DA_ENTREVISTA),
    )
    final = marco("m2", etapas=(ETAPA_DA_ENTREVISTA,), corte=regra(excedente=3))
    c = cadastro.do_perfil(perfil(marcos=[intermediario, final]))
    assert [m.marco_id for m in c.marcos] == ["m2"]
    assert c.numero_unico == 3


def test_o_marco_que_governa_etapa_que_ninguem_le_convoca():
    c = cadastro.do_perfil(
        perfil(marcos=[marco(corte=regra(alvo=2, excedente=1, governada=ETAPA_DA_ENTREVISTA))])
    )
    assert [m.marco_id for m in c.marcos] == ["m1"]


def test_dois_marcos_que_convocam_expoem_os_dois():
    c = cadastro.do_perfil(
        perfil(
            marcos=[
                marco("m1", corte=regra(excedente=3)),
                marco("m2", nome="Outra", etapas=("x",), corte=regra(excedente=5)),
            ]
        )
    )
    assert c.numero_unico == 3
    assert [m.listas[0].numero for m in c.marcos] == [3, 5]


def test_continuacao_e_empate_valem_se_algum_admite():
    c = cadastro.do_perfil(
        perfil(
            marcos=[
                marco("m1", corte=regra(excedente=3)),
                marco(
                    "m2",
                    nome="Outra",
                    etapas=("x",),
                    corte=regra(excedente=3, continuacao="ALLOWED", empate="ADMITS_SURPLUS"),
                ),
            ]
        )
    )
    assert c.alcance_cresce
    assert c.admite_empate


def test_sem_corte_no_marco_que_convoca_nao_ha_numero():
    c = cadastro.do_perfil(perfil(marcos=[marco()]))
    assert c.por_lista == ()
    assert c.numero_unico is None
    assert c.marco_que_convoca.marco_id == "m1"
    assert not c.marco_que_convoca.tem_corte


# --- O legado (T-002) ---------------------------------------------------------------------------


@pytest.mark.parametrize("limite", [6, 0])
def test_legado_e_o_limitado_com_numero_digitado(limite):
    c = cadastro.do_perfil(perfil(limite=limite, marcos=[marco(corte=regra(excedente=3))]))
    assert c.legado
    assert c.publicado == limite
    assert c.numero_mostrado() == limite
    assert c.numero_unico == 3, "o alcance continua calculado, para a nota da ocupação"


def test_ilimitado_e_nao_ha_nunca_sao_legado():
    assert not cadastro.do_perfil(perfil(especie="UNLIMITED")).legado
    assert not cadastro.do_perfil(perfil(especie="NONE")).legado


# --- O texto curto e o resumo (contratos D e P) --------------------------------------------------


@pytest.mark.parametrize(
    ("montado", "esperado"),
    [
        (perfil(especie="NONE"), "Não há"),
        (perfil(especie="UNLIMITED"), "Sem limite"),
        (perfil(limite=6), "Limitado em 6"),
        (perfil(marcos=[marco(corte=regra(excedente=3))]), "Limitado: até 3"),
        (perfil(marcos=[marco()]), "Limitado, sem corte no marco que convoca"),
    ],
)
def test_descricao_curta(montado, esperado):
    assert cadastro.do_perfil(montado).descricao_curta() == esperado


def test_descricao_curta_por_lista():
    modalidades, quadro = tres_listas()
    mesma = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(excedente=2))]
    )
    assert cadastro.do_perfil(mesma).descricao_curta() == "Limitado: até 2 por lista"
    diferentes = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))]
    )
    assert cadastro.do_perfil(diferentes).descricao_curta() == "Limitado: até 1 AC, 2 PcD, 2 PPI"


def test_resumo_limitado_nas_tres_formas():
    assert cadastro.do_perfil(perfil(marcos=[marco()])).resumo_limitado() == "limitado"
    unico = perfil(especie="NONE", marcos=[marco(corte=regra(excedente=3))])
    assert cadastro.do_perfil(unico).resumo_limitado() == "limitado: até 3", (
        "calculado sobre o corte salvo, qualquer que seja a espécie marcada agora"
    )
    modalidades, quadro = tres_listas()
    diferentes = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))]
    )
    assert cadastro.do_perfil(diferentes).resumo_limitado() == "limitado: até 1 AC, 2 PcD, 2 PPI"
