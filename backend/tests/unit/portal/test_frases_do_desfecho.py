"""As frases simples do desfecho (156, FR-6406 a FR-6408, UX-620).

Uma por espécie, pela tabela da FR-6406, e nenhuma com o vocabulário do ato (FR-6403): o
fundamento continua existindo, recolhido logo abaixo, e é lá que *"decorreu"* e *"recorte"* podem
estar. Aqui se prova o texto; a varredura das telas renderizadas está em
`tests/test_vocabulario_do_desfecho.py`.
"""

import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.portal import desfecho

REGISTRO = datetime(2026, 11, 12, 15, 0, tzinfo=UTC)
FIM_DO_PRAZO = datetime(2026, 11, 9, 16, 27, tzinfo=UTC)

#: Os termos que a FR-6403 deixa só dentro do fundamento recolhido.
DO_ATO = (
    "faixa vigente",
    "recorte",
    "apuração",
    "decorreu",
    "desfecho registrado",
    "vencimento informado no ato",
    "espécie",
)


def frase(especie, **kwargs):
    argumentos = {
        "registrado_em": REGISTRO,
        "fim_do_prazo": FIM_DO_PRAZO,
        "atestado": nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE,
    }
    return desfecho.frase_do_desfecho(especie, **{**argumentos, **kwargs})


ESPERADAS = {
    nomes.ACEITE: (
        "A comissão registrou o resultado da sua convocação em 12/11/2026. Este registro não é "
        "matrícula, bolsa nem contrato."
    ),
    nomes.REGULARIZACAO: (
        "A comissão registrou a regularização da sua situação nesta convocação em 12/11/2026. "
        "Este registro não é matrícula, bolsa nem contrato."
    ),
    nomes.INDEFERIMENTO: (
        "A comissão registrou o indeferimento desta convocação em 12/11/2026: ela concluiu que o "
        "que o Edital pede nesta etapa não foi cumprido. O motivo está no fundamento, abaixo."
    ),
    nomes.DESISTENCIA_EXPRESSA: (
        "A comissão registrou a sua desistência desta convocação em 12/11/2026. Esta convocação "
        "está encerrada para você."
    ),
    nomes.NAO_ATENDIMENTO: (
        "O prazo desta convocação terminou em 09/11/2026 sem que ela fosse atendida, e a comissão "
        "registrou isso em 12/11/2026. Esta convocação está encerrada para você."
    ),
    nomes.INERCIA: (
        "A comissão registrou o cancelamento em 12/11/2026, porque não houve acesso ao ambiente do "
        "curso. Esta convocação está encerrada para você."
    ),
    nomes.RECLASSIFICACAO: (
        "A comissão registrou a sua reclassificação em 12/11/2026. Esta convocação está encerrada "
        "para você; o que acontece depois é o que o Edital diz."
    ),
}


def test_a_tabela_cobre_as_sete_especies():
    assert set(ESPERADAS) == set(nomes.ESPECIES_DE_DESFECHO)


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_DESFECHO)
def test_cada_especie_tem_a_frase_da_fr_6406(especie):
    assert frase(especie) == ESPERADAS[especie]


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_DESFECHO)
def test_nenhuma_frase_usa_o_vocabulario_do_ato(especie):
    """FR-6403, e as proibições que as varreduras da `063` e da `029` já tinham (R-001)."""
    texto = frase(especie).lower()
    achados = [termo for termo in (*DO_ATO, "homologa", "dentro das vagas") if termo in texto]
    assert achados == []


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_DESFECHO)
def test_no_maximo_duas_frases(especie):
    """UX-620: o próximo passo, quando houver, vem depois, e a frase simples cabe em duas."""
    assert len(re.findall(r"[.!?](?:\s|$)", frase(especie))) <= 2


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_DESFECHO)
def test_nenhuma_frase_promete_vaga_chamada_nem_matricula(especie):
    """FR-6408 e FR-6413: o efeito é sobre a chamada, e o aceite só diz o que o registro não é."""
    texto = frase(especie).lower()
    for promessa in ("perdeu a vaga", "nova chamada", "posição", "será chamad", "matriculad"):
        assert promessa not in texto


@pytest.mark.parametrize(
    ("atestado", "fato"),
    [
        (nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE, "não houve acesso ao ambiente do curso"),
        (
            nomes.ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA,
            "não houve presença na primeira semana do curso",
        ),
        (nomes.ATESTADO_NAO_ENTREGA_PRESENCIAL, "a entrega presencial não foi feita"),
    ],
)
def test_a_inercia_diz_o_fato_atestado(atestado, fato):
    """FR-6407: uma frase por espécie de atestado da `019`."""
    assert f", porque {fato}." in frase(nomes.INERCIA, atestado=atestado)


def test_as_tres_especies_de_atestado_tem_frase():
    assert set(desfecho.FATO_ATESTADO) == set(nomes.ESPECIES_DE_ATESTADO)


def test_a_data_e_a_local_do_registro():
    """Às 01h00 UTC do dia 13, em Brasília ainda é dia 12."""
    tarde = datetime(2026, 11, 13, 1, 0, tzinfo=UTC)
    assert "em 12/11/2026" in frase(nomes.DESISTENCIA_EXPRESSA, registrado_em=tarde)


def test_o_nao_atendimento_sem_vencimento_nao_inventa_data():
    texto = frase(nomes.NAO_ATENDIMENTO, fim_do_prazo=None)
    assert texto.startswith("O prazo desta convocação terminou sem que ela fosse atendida")


def test_o_fundamento_recolhido_e_o_gravado_com_a_data():
    """FR-6401: o texto do ato, sem edição, com a data do registro."""
    lido = SimpleNamespace(
        fundamento="  A comunicação foi enviada e o vencimento decorreu.  ",
        registrado_em=REGISTRO,
    )
    assert desfecho.fundamento_do_registro(lido) == (
        "Registrado em 12/11/2026: A comunicação foi enviada e o vencimento decorreu."
    )


def test_do_desfecho_le_o_vencimento_da_convocacao_e_o_atestado_so_na_inercia():
    convocacao = SimpleNamespace(vencimento=FIM_DO_PRAZO)
    sem_atestado = SimpleNamespace(especie=nomes.NAO_ATENDIMENTO, registrado_em=REGISTRO)
    assert desfecho.do_desfecho(sem_atestado, convocacao) == ESPERADAS[nomes.NAO_ATENDIMENTO]

    inercia = SimpleNamespace(
        especie=nomes.INERCIA,
        registrado_em=REGISTRO,
        atestado=SimpleNamespace(especie=nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE),
    )
    assert desfecho.do_desfecho(inercia, convocacao) == ESPERADAS[nomes.INERCIA]


# --- A convocação sem desfecho (FR-6442; FR-3740 da `118`, revista) -----------------------------

DA_CONVOCACAO = {
    nomes.VAGA_INICIAL: (
        "Você foi chamado para uma das vagas da lista Ampla concorrência, pela sua posição na "
        "classificação."
    ),
    nomes.SUPLENCIA: (
        "Você foi chamado porque uma vaga da lista Ampla concorrência ficou livre e você é a "
        "próxima pessoa na classificação."
    ),
    nomes.PARA_REGULARIZAR: (
        "Você foi chamado para regularizar a sua situação na lista Ampla concorrência, porque há "
        "vaga."
    ),
}


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_CONVOCACAO)
def test_cada_especie_de_convocacao_tem_a_frase_da_fr_6442(especie):
    assert (
        desfecho.frase_da_convocacao(especie, lista="Ampla concorrência")
        == (DA_CONVOCACAO[especie])
    )


@pytest.mark.parametrize("especie", nomes.ESPECIES_DE_CONVOCACAO)
def test_a_frase_da_convocacao_nao_usa_o_vocabulario_do_ato_nem_promete_vaga(especie):
    """FR-6403, e *"dentro das vagas"*, que a UX-158 da `063` proíbe (FR-6442)."""
    texto = desfecho.frase_da_convocacao(especie, lista="Ampla concorrência").lower()
    assert [t for t in (*DO_ATO, "dentro das vagas", "vaga garantid") if t in texto] == []


def test_sem_o_nome_da_lista_a_frase_nao_inventa_nome():
    assert desfecho.frase_da_convocacao(nomes.SUPLENCIA, lista="").startswith(
        "Você foi chamado porque uma vaga da sua lista ficou livre"
    )
    assert "na sua lista" in desfecho.frase_da_convocacao(nomes.PARA_REGULARIZAR)
