"""A leitura do quadro publicado não infere linha ausente (027, FR-330, invariante 3).

**É o contrato negativo desta feature, e o mais importante dela.** A derivação da linha geral
acontece na **autoria** — o rascunho a materializa antes de publicar —, e nunca na leitura. Derivar
aqui faria um Edital publicado passar a afirmar uma quantidade que ele não publicou, o que é
reescrevê-lo por interpretação: publicação é ato imutável.

**E não funcionaria.** A derivação só é inequívoca onde não há lista reservada, e os três Editais da
demonstração declaram Modalidade sem apontar a ampla. Derivar na leitura consertaria zero deles — a
medição está na `D-005` da spec, e é ela que separa este arquivo de uma opinião.

Este é o guarda que impede que alguém "conserte" o acervo por interpretação em vez de por ato.
"""

import pytest

from processo_seletivo.classificacao.application.corte import linha_do_quadro

PERFIL = "aaaaaaaa-0000-4000-8000-000000000701"
AC = "aaaaaaaa-0000-4000-8000-000000000702"
PPI = "aaaaaaaa-0000-4000-8000-000000000703"


def conteudo(**perfil):
    base = {
        "id": PERFIL,
        "code": "P1",
        "immediateVacancies": 40,
        "competitionModalities": [],
        "vacancyTable": [],
        "generalCompetitionModalityId": None,
    }
    return {"profiles": [{**base, **perfil}]}


def test_perfil_do_acervo_sem_quadro_nao_devolve_linha_nenhuma():
    """Publicado antes de a capacidade existir: ele declara 40 vagas e nenhuma quantidade por
    recorte. Devolver 40 aqui seria inventar uma linha que o Edital não publicou."""
    assert linha_do_quadro(conteudo(), perfil_id=PERFIL, lista_id=None) is None


def test_o_total_do_perfil_nao_vira_linha_geral_na_leitura():
    """O caminho exato pelo qual a inferência entraria: o total está ali, ao lado, e é tentador."""
    lido = linha_do_quadro(conteudo(immediateVacancies=999), perfil_id=PERFIL, lista_id=None)
    assert lido is None, "o total publicado não é a linha do quadro"


def test_lista_reservada_sem_linha_nao_herda_a_geral():
    """Quadro parcial é legítimo, e a ausência da linha da PPI diz "não declarado" — nunca "o
    mesmo que a ampla" nem "zero" (`025`, D-006)."""
    publicado = conteudo(
        competitionModalities=[{"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"}],
        vacancyTable=[{"id": "l1", "modalityId": None, "immediateVacancies": 30}],
    )
    assert linha_do_quadro(publicado, perfil_id=PERFIL, lista_id=PPI) is None
    assert linha_do_quadro(publicado, perfil_id=PERFIL, lista_id=None)["immediateVacancies"] == 30


def test_a_linha_publicada_e_lida_exatamente_como_foi_publicada():
    """A metade positiva: o que está lá é lido, e lido como está."""
    publicado = conteudo(
        vacancyTable=[{"id": "l1", "modalityId": None, "immediateVacancies": 0}],
    )
    lida = linha_do_quadro(publicado, perfil_id=PERFIL, lista_id=None)
    assert lida["immediateVacancies"] == 0, "`0` é uma declaração, e não ausência"


def test_a_ampla_declarada_le_a_linha_geral_e_nao_inventa_uma_propria():
    """A Modalidade apontada como ampla não tem linha própria — por norma (`025`, D-004) —, e a
    leitura dela é a linha geral. Isso é resolução de identidade declarada pelo Edital, e não
    inferência: o Perfil **disse** que aquela Modalidade é a ampla."""
    publicado = conteudo(
        competitionModalities=[{"id": AC, "code": "AC", "name": "Ampla concorrência"}],
        generalCompetitionModalityId=AC,
        vacancyTable=[{"id": "l1", "modalityId": None, "immediateVacancies": 40}],
    )
    assert linha_do_quadro(publicado, perfil_id=PERFIL, lista_id=AC)["immediateVacancies"] == 40


def test_sem_a_declaracao_a_modalidade_homonima_nao_le_a_linha_geral():
    """E o contraste que prova que a de cima não é adivinhação: sem o apontamento, a Modalidade
    chamada "Ampla concorrência" é uma lista como outra qualquer, e não tem linha."""
    publicado = conteudo(
        competitionModalities=[{"id": AC, "code": "AC", "name": "Ampla concorrência"}],
        vacancyTable=[{"id": "l1", "modalityId": None, "immediateVacancies": 40}],
    )
    assert linha_do_quadro(publicado, perfil_id=PERFIL, lista_id=AC) is None


@pytest.mark.parametrize("conteudo_vazio", [None, {}, {"profiles": []}])
def test_conteudo_sem_perfil_nao_quebra_nem_inventa(conteudo_vazio):
    assert linha_do_quadro(conteudo_vazio, perfil_id=PERFIL, lista_id=None) is None
