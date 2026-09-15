"""A linha geral de um Perfil sem lista reservada é a vaga imediata dele (027, FR-316 a FR-322).

**Por que estes testes existem separados dos da `025`.** Lá o quadro era declarado inteiro por quem
compõe, e o que se verificava era forma, unicidade e referência. Aqui há um número que o sistema
escreve sozinho, e o que se verifica é outra coisa: de onde ele vem, que ele não vem de mais lugar
nenhum, e que a identidade dele sobrevive à gravação seguinte.
"""

from processo_seletivo.editais.domain.perfis import derivar_linha_geral, listas_reservadas

AC = "11111111-1111-1111-1111-111111111111"
PPI = "22222222-2222-2222-2222-222222222222"


def _perfil(**ajustes):
    base = {
        "id": "00000000-0000-0000-0000-0000000000b1",
        "code": "DOC",
        "name": "Docente",
        "immediateVacancies": 80,
        "reserveType": "NONE",
        "competitionModalities": [],
        "vacancyTable": [],
    }
    return {**base, **ajustes}


def _modalidade(identidade, codigo):
    return {"id": identidade, "code": codigo, "name": codigo}


# --- FR-317: o que conta como lista reservada -------------------------------------------------


def test_perfil_sem_modalidade_nao_tem_lista_reservada():
    assert listas_reservadas(_perfil()) == set()


def test_a_modalidade_declarada_como_ampla_nao_e_lista_reservada():
    perfil = _perfil(competitionModalities=[_modalidade(AC, "AC")], generalCompetitionModalityId=AC)
    assert listas_reservadas(perfil) == set()


def test_a_reservada_conta_e_a_ampla_declarada_nao():
    perfil = _perfil(
        competitionModalities=[_modalidade(AC, "AC"), _modalidade(PPI, "PPI")],
        generalCompetitionModalityId=AC,
    )
    assert listas_reservadas(perfil) == {PPI}


def test_sem_ampla_apontada_toda_modalidade_conta_como_reservada():
    """A armadilha que a FR-325 adverte: o sistema não adivinha qual é a ampla pelo nome."""
    perfil = _perfil(
        competitionModalities=[_modalidade(AC, "AC"), _modalidade(PPI, "PPI")],
    )
    assert listas_reservadas(perfil) == {AC, PPI}


# --- FR-318 e FR-320: a derivação ---------------------------------------------------------------


def test_perfil_sem_lista_reservada_ganha_linha_geral_com_o_total():
    derivado = derivar_linha_geral(_perfil(immediateVacancies=2))
    assert [
        (linha["modalityId"], linha["immediateVacancies"]) for linha in derivado["vacancyTable"]
    ] == [(None, 2)]
    assert derivado["immediateVacancies"] == 2


def test_total_zero_deriva_linha_de_zero_e_nao_ausencia():
    """`0` diz zero vagas; ausência diria que o Edital não declarou. São afirmações diferentes."""
    derivado = derivar_linha_geral(_perfil(immediateVacancies=0))
    assert derivado["vacancyTable"][0]["immediateVacancies"] == 0


def test_a_derivacao_reafirma_a_quantidade_e_preserva_a_identidade():
    """FR-322: removida a última lista reservada, a linha geral volta a valer o total."""
    perfil = _perfil(
        immediateVacancies=78,
        vacancyTable=[{"id": "linha-1", "modalityId": None, "immediateVacancies": 60}],
    )
    derivado = derivar_linha_geral(perfil)
    assert derivado["vacancyTable"] == [
        {"id": "linha-1", "modalityId": None, "immediateVacancies": 78}
    ]


def test_a_derivacao_e_idempotente():
    uma = derivar_linha_geral(_perfil())
    outra = derivar_linha_geral(uma)
    assert uma == outra


def test_perfil_com_lista_reservada_nao_e_derivado():
    """Ali a repartição é declarada, e derivar apagaria declaração de quem compõe."""
    perfil = _perfil(
        competitionModalities=[_modalidade(PPI, "PPI")],
        vacancyTable=[
            {"id": "geral", "modalityId": None, "immediateVacancies": 60},
            {"id": "ppi", "modalityId": PPI, "immediateVacancies": 20},
        ],
    )
    assert derivar_linha_geral(perfil) == perfil


def test_a_linha_geral_vem_primeiro_e_as_reservadas_sobrevivem():
    """Um POST pode remover a última Modalidade e deixar a linha dela para trás: quem recusa esse
    conteúdo é `validate_vacancy_table`, com a mensagem certa, e não esta função apagando em
    silêncio."""
    perfil = _perfil(vacancyTable=[{"id": "ppi", "modalityId": PPI, "immediateVacancies": 20}])
    derivado = derivar_linha_geral(perfil)
    assert [linha["modalityId"] for linha in derivado["vacancyTable"]] == [None, PPI]


# --- FR-319: a derivação tem uma fonte só (invariante 8 da §5) ----------------------------------


def test_a_derivacao_ignora_percentual_e_fundamento_da_regra_normativa():
    """O invariante 8: nenhuma quantidade derivada tem outra fonte que o total do Perfil."""
    perfil = _perfil(
        immediateVacancies=80,
        competitionModalities=[
            {
                **_modalidade(AC, "AC"),
                "normativeRule": {"percentage": "50", "foundation": "Lei 12.711/2012"},
            }
        ],
        generalCompetitionModalityId=AC,
    )
    derivado = derivar_linha_geral(perfil)
    assert derivado["vacancyTable"][0]["immediateVacancies"] == 80


def test_total_malformado_nao_inventa_linha():
    """Quem tem a mensagem certa para total inválido é `validate_profile`; esconder a recusa boa
    atrás de uma linha inventada seria trocar um erro legível por um mudo."""
    assert derivar_linha_geral(_perfil(immediateVacancies=None))["vacancyTable"] == []
    assert derivar_linha_geral(_perfil(immediateVacancies=True))["vacancyTable"] == []
