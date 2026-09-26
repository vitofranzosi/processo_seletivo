"""As formas de aplicabilidade (US4 da 009, FR-006, FR-040; 044, FR-701, FR-705).

A função é pura sobre o conteúdo publicado e vive no domínio dos Editais, junto da regra que a
declara. É ela que decide o que a tela pede, o que o envio aceita e o que a submissão exige: três
leituras da mesma função, e não três interpretações da mesma frase.
"""

import pytest

from processo_seletivo.editais.domain import documentos
from processo_seletivo.editais.domain.documentos import aplicabilidade, aplicaveis, razao_legivel

PERFIL_A, PERFIL_B = "perfil-a", "perfil-b"
MODALIDADE_A, MODALIDADE_B = "modalidade-a", "modalidade-b"

DE_TODOS = {"id": "r1", "name": "Identificação", "order": 1}
DO_PERFIL = {"id": "r2", "name": "Diploma", "order": 2, "profileId": PERFIL_A}
DA_MODALIDADE = {"id": "r3", "name": "Autodeclaração", "order": 3, "modalityId": MODALIDADE_A}
DA_COMBINACAO = {
    "id": "r4",
    "name": "Laudo",
    "order": 4,
    "profileId": PERFIL_A,
    "modalityId": MODALIDADE_A,
}
TODOS = [DE_TODOS, DO_PERFIL, DA_MODALIDADE, DA_COMBINACAO]


def _conteudo(requisitos, perfis=()):
    """O conteúdo publicado, com o mínimo: a função recebe o conteúdo porque o recorte por código
    precisa dos Perfis para ler o código da Modalidade escolhida."""
    return {"documentRequirements": list(requisitos), "profiles": list(perfis)}


@pytest.mark.parametrize(
    ("perfil", "modalidade", "esperados", "porque"),
    [
        (PERFIL_A, MODALIDADE_A, ["r1", "r2", "r3", "r4"], "a combinação recebe as quatro"),
        (PERFIL_A, None, ["r1", "r2"], "sem modalidade, só o de todos e o do Perfil"),
        (PERFIL_B, MODALIDADE_A, ["r1", "r3"], "outro Perfil não recebe o documento do Perfil A"),
        (PERFIL_B, MODALIDADE_B, ["r1"], "nada específico se aplica"),
        (PERFIL_B, None, ["r1"], "só o de todos"),
    ],
)
def test_cada_combinacao_recebe_exatamente_o_que_lhe_cabe(perfil, modalidade, esperados, porque):
    escolhidos = aplicaveis(_conteudo(TODOS), profile_id=perfil, modality_id=modalidade)

    assert [item["id"] for item in escolhidos] == esperados, porque


def test_a_ordem_e_a_declarada_e_nao_a_da_lista():
    fora_de_ordem = [DA_COMBINACAO, DE_TODOS, DO_PERFIL]

    escolhidos = aplicaveis(_conteudo(fora_de_ordem), profile_id=PERFIL_A, modality_id=MODALIDADE_A)

    assert [item["order"] for item in escolhidos] == [1, 2, 4]


def test_lista_vazia_nao_pede_nada():
    assert aplicaveis(_conteudo([]), profile_id=PERFIL_A, modality_id=MODALIDADE_A) == []


def test_nenhuma_modalidade_e_diferente_de_qualquer_modalidade():
    """`None` não é curinga: quem não escolheu não recebe o documento de modalidade nenhuma."""
    escolhidos = aplicaveis(_conteudo([DA_MODALIDADE]), profile_id=PERFIL_A, modality_id=None)

    assert escolhidos == []


# ---------------------------------------------------------------------------
# 044 — o veredito, o recorte por código, a divergência e a razão
# ---------------------------------------------------------------------------


def _modalidade(ident, codigo, nome):
    return {"id": ident, "code": codigo, "name": nome}


C1 = {
    "id": "c1",
    "code": "C1",
    "name": "Curso um",
    "competitionModalities": [
        _modalidade("c1-ac", "AC", "Ampla concorrência"),
        _modalidade("c1-pcd", "PcD", "Pessoas com Deficiência"),
        _modalidade("c1-ppiq", "PPIQ", "Pretos, Pardos, Indígenas e Quilombolas"),
    ],
    "generalCompetitionModalityId": "c1-ac",
}
C2 = {
    "id": "c2",
    "code": "C2",
    "name": "Curso dois",
    "competitionModalities": [
        _modalidade("c2-ac", "AC", "Ampla concorrência"),
        _modalidade("c2-pcd", "PcD", "Pessoas com Deficiência"),
    ],
    "generalCompetitionModalityId": "c2-ac",
}
IDENTIDADE = {"id": "d-id", "name": "Identidade", "order": 1}
LAUDO_TRANSVERSAL = {"id": "d-laudo", "name": "Laudo", "order": 2, "modalityCode": "PcD"}
AUTODECLARACAO_PPIQ_C1 = {
    "id": "d-ppiq",
    "name": "Autodeclaração étnico-racial",
    "order": 3,
    "profileId": "c1",
    "modalityId": "c1-ppiq",
}
DEFICIENCIA_FACULTATIVA = {
    "id": "d-fac",
    "name": "Autodeclaração de deficiência",
    "order": 4,
    "required": False,
}
EDITAL_903 = _conteudo(
    [IDENTIDADE, LAUDO_TRANSVERSAL, AUTODECLARACAO_PPIQ_C1, DEFICIENCIA_FACULTATIVA], [C1, C2]
)


def _por_id(vereditos):
    return {veredito.requisito["id"]: veredito for veredito in vereditos}


def test_ha_um_veredito_por_documento_na_ordem_declarada():
    vereditos = aplicabilidade(EDITAL_903, profile_id="c2", modality_id="c2-pcd")

    assert [v.requisito["id"] for v in vereditos] == ["d-id", "d-laudo", "d-ppiq", "d-fac"]


def test_o_veredito_diz_obrigatorio_facultativo_e_nao_se_aplica():
    vereditos = _por_id(aplicabilidade(EDITAL_903, profile_id="c2", modality_id="c2-pcd"))

    assert vereditos["d-id"].situacao == documentos.OBRIGATORIO
    assert vereditos["d-laudo"].situacao == documentos.OBRIGATORIO
    assert vereditos["d-ppiq"].situacao == documentos.NAO_SE_APLICA
    assert vereditos["d-fac"].situacao == documentos.FACULTATIVO


@pytest.mark.parametrize(
    ("requisito", "forma", "parametros"),
    [
        (IDENTIDADE, documentos.TODOS, (None, None, None)),
        ({"id": "x", "profileId": "c1"}, documentos.PERFIL, ("c1", None, None)),
        (AUTODECLARACAO_PPIQ_C1, documentos.PERFIL_E_MODALIDADE, ("c1", "c1-ppiq", None)),
        (LAUDO_TRANSVERSAL, documentos.MODALIDADE_EM_TODOS_OS_PERFIS, (None, None, "PcD")),
        (
            {"id": "x", "modalityId": "c1-pcd"},
            documentos.TODOS_COM_MODALIDADE_DE_UM_PERFIL,
            (None, "c1-pcd", None),
        ),
    ],
)
def test_o_recorte_se_le_por_presenca_de_campo(requisito, forma, parametros):
    recorte = documentos.recorte_de(requisito)

    assert recorte.forma == forma
    assert (recorte.perfil_id, recorte.modalidade_id, recorte.modalidade_codigo) == parametros


@pytest.mark.parametrize(
    ("perfil", "modalidade", "aplica", "porque"),
    [
        ("c1", "c1-pcd", True, "PcD do C1"),
        ("c2", "c2-pcd", True, "PcD do C2 — o caso do 903"),
        ("c1", "c1-ac", False, "AC não é PcD"),
        ("c1", "c1-ppiq", False, "PPIQ não é PcD"),
        ("c2", None, False, "sem modalidade escolhida, não se aplica"),
    ],
)
def test_o_recorte_por_codigo_vale_em_todo_perfil_que_tem_o_codigo(
    perfil, modalidade, aplica, porque
):
    escolhidos = aplicaveis(EDITAL_903, profile_id=perfil, modality_id=modalidade)

    assert ("d-laudo" in [item["id"] for item in escolhidos]) is aplica, porque


def test_o_codigo_e_lido_no_perfil_da_inscricao_e_nao_em_outro():
    """A Modalidade do C1 apresentada como escolha no C2 não existe ali: não se aplica."""
    escolhidos = aplicaveis(EDITAL_903, profile_id="c2", modality_id="c1-pcd")

    assert "d-laudo" not in [item["id"] for item in escolhidos]


def test_codigo_presente_num_perfil_so_equivale_ao_recorte_exato():
    so_no_c1 = {"id": "d-x", "name": "Declaração", "order": 9, "modalityCode": "PPIQ"}
    conteudo = _conteudo([so_no_c1], [C1, C2])

    assert aplicaveis(conteudo, profile_id="c1", modality_id="c1-ppiq") == [so_no_c1]
    assert aplicaveis(conteudo, profile_id="c2", modality_id="c2-pcd") == []


LAUDO_AMBIGUO = {"id": "d-amb", "name": "Laudo médico (PcD)", "order": 2, "modalityId": "c1-pcd"}
EDITAL_903_ORIGINAL = _conteudo([IDENTIDADE, LAUDO_AMBIGUO], [C1, C2])


def test_a_divergencia_da_161_marca_quem_concorre_na_mesma_denominacao_em_outro_perfil():
    """O documento publicado exigia o laudo de todo PcD; o portal o pediu só no C1 (FR-727)."""
    pcd_do_c2 = _por_id(aplicabilidade(EDITAL_903_ORIGINAL, profile_id="c2", modality_id="c2-pcd"))

    assert pcd_do_c2["d-amb"].situacao == documentos.NAO_SE_APLICA
    assert pcd_do_c2["d-amb"].divergente_do_publicado is True


@pytest.mark.parametrize(
    ("perfil", "modalidade", "porque"),
    [
        ("c2", "c2-ac", "a AC do C2 não concorre em PcD"),
        ("c1", "c1-pcd", "o PcD do C1 recebeu o pedido"),
        ("c1", "c1-ac", "a AC do C1 não concorre em PcD"),
    ],
)
def test_a_divergencia_nao_marca_quem_nao_concorre_na_denominacao(perfil, modalidade, porque):
    veredito = _por_id(
        aplicabilidade(EDITAL_903_ORIGINAL, profile_id=perfil, modality_id=modalidade)
    )["d-amb"]

    assert veredito.divergente_do_publicado is False, porque


def test_sem_outro_perfil_de_mesma_denominacao_nao_ha_divergencia():
    so_c1 = _conteudo([LAUDO_AMBIGUO], [C1])

    veredito = aplicabilidade(so_c1, profile_id="c1", modality_id="c1-ac")[0]

    assert veredito.divergente_do_publicado is False


@pytest.mark.parametrize(
    ("perfil", "modalidade", "documento", "frase"),
    [
        ("c2", "c2-pcd", "d-id", "pedido de todos os candidatos"),
        (
            "c2",
            "c2-pcd",
            "d-laudo",
            "pedido de quem concorre em Pessoas com Deficiência, em todos os Perfis",
        ),
        (
            "c2",
            "c2-pcd",
            "d-ppiq",
            "Não se aplica: pedido de quem concorre ao Perfil C1 em Pretos, Pardos, Indígenas e "
            "Quilombolas",
        ),
        (
            "c1",
            "c1-ac",
            "d-laudo",
            "Não se aplica: pedido de quem concorre em Pessoas com Deficiência, em todos os Perfis",
        ),
    ],
)
def test_a_razao_se_le_como_frase_pela_denominacao(perfil, modalidade, documento, frase):
    veredito = _por_id(aplicabilidade(EDITAL_903, profile_id=perfil, modality_id=modalidade))[
        documento
    ]

    assert razao_legivel(veredito, EDITAL_903) == frase


def test_a_razao_da_divergencia_diz_o_que_o_edital_publicado_exigia():
    veredito = _por_id(aplicabilidade(EDITAL_903_ORIGINAL, profile_id="c2", modality_id="c2-pcd"))[
        "d-amb"
    ]

    assert razao_legivel(veredito, EDITAL_903_ORIGINAL) == (
        "Não se aplica: pedido de quem concorre ao Perfil C1 em Pessoas com Deficiência — o "
        "Edital publicado o exigia de todo candidato em Pessoas com Deficiência. O portal não o "
        "pediu a esta inscrição."
    )


def test_a_razao_do_perfil_nomeia_o_perfil():
    do_perfil = {"id": "d-p", "name": "Diploma", "order": 1, "profileId": "c1"}
    conteudo = _conteudo([do_perfil], [C1, C2])

    veredito = aplicabilidade(conteudo, profile_id="c2", modality_id="c2-ac")[0]

    assert (
        razao_legivel(veredito, conteudo) == "Não se aplica: pedido de quem concorre ao Perfil C1"
    )


def test_perfil_acrescentado_depois_com_o_codigo_recebe_o_documento_sem_linha_nova():
    """Por composição, Retificação ou duplicação: o recorte alcança quem tem o código."""
    c3 = {
        "id": "c3",
        "code": "C3",
        "competitionModalities": [_modalidade("c3-pcd", "PcD", "Pessoas com Deficiência")],
    }
    conteudo = _conteudo([IDENTIDADE, LAUDO_TRANSVERSAL], [C1, C2, c3])

    escolhidos = aplicaveis(conteudo, profile_id="c3", modality_id="c3-pcd")

    assert [item["id"] for item in escolhidos] == ["d-id", "d-laudo"]
