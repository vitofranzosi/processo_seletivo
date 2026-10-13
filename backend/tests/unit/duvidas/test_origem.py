"""A origem de cada valor: ancestral ou próprio caminho, e o último ato aplicado (070, `R-004`).

O caso que decide a regra é o terceiro: um Perfil substituído inteiro **depois** de outra
Retificação ter mudado um campo dele. Pelo caminho mais longo, o campo viria da Retificação antiga,
cujo valor já não vigora.
"""

from datetime import UTC, datetime

from processo_seletivo.duvidas.domain.estruturas import ORIGINAL, RETIFICACAO, AtoPublicado
from processo_seletivo.duvidas.domain.origem import origens

DIA = datetime(2026, 10, 11, tzinfo=UTC)
ORIGEM = AtoPublicado("pub-1", ORIGINAL, 1, DIA, DIA)
R2 = AtoPublicado("pub-2", RETIFICACAO, 2, DIA, DIA)
R3 = AtoPublicado("pub-3", RETIFICACAO, 3, DIA, DIA)
ATOS = (ORIGEM, R2, R3)
PERFIL = "/profiles/id=p1"


def ids(resultado):
    return [ato.publicacao_id for ato in resultado]


def test_sem_proveniencia_vale_a_publicacao_original():
    assert ids(origens(f"{PERFIL}/name", (), ATOS)) == ["pub-1"]


def test_proveniencia_no_proprio_caminho():
    assert ids(origens(f"{PERFIL}/name", ((f"{PERFIL}/name", "pub-2"),), ATOS)) == ["pub-2"]


def test_proveniencia_num_ancestral():
    assert ids(origens(f"{PERFIL}/name", ((PERFIL, "pub-3"),), ATOS)) == ["pub-3"]


def test_o_perfil_substituido_depois_vence_o_campo_alterado_antes():
    proveniencias = ((f"{PERFIL}/name", "pub-2"), (PERFIL, "pub-3"))
    assert ids(origens(f"{PERFIL}/name", proveniencias, ATOS)) == ["pub-3"]


def test_o_campo_alterado_depois_do_perfil_vence_a_substituicao():
    atos = (ORIGEM, R3, R2)  # R3 aplicada antes de R2: vigência anterior
    proveniencias = ((PERFIL, "pub-3"), (f"{PERFIL}/name", "pub-2"))
    assert ids(origens(f"{PERFIL}/name", proveniencias, atos)) == ["pub-2"]


def test_valor_composto_tem_uma_origem_por_ato_que_o_alterou():
    quadro = f"{PERFIL}/vacancyTable"
    proveniencias = ((f"{quadro}/id=l1/immediateVacancies", "pub-2"),)
    assert ids(origens(quadro, proveniencias, ATOS)) == ["pub-1", "pub-2"]


def test_descendente_alterado_antes_da_substituicao_do_todo_nao_conta():
    quadro = f"{PERFIL}/vacancyTable"
    proveniencias = ((f"{quadro}/id=l1/immediateVacancies", "pub-2"), (PERFIL, "pub-3"))
    assert ids(origens(quadro, proveniencias, ATOS)) == ["pub-3"]


def test_a_ordem_e_a_de_aplicacao_e_nao_a_de_publicacao():
    # A Retificação publicada por último (ordem 3) vigora antes da outra: aplica-se antes.
    atos = (ORIGEM, R3, R2)
    proveniencias = ((f"{PERFIL}/name", "pub-3"), (f"{PERFIL}/name", "pub-2"))
    assert ids(origens(f"{PERFIL}/name", proveniencias, atos)) == ["pub-2"]


def test_caminho_que_so_comeca_igual_nao_e_ancestral():
    proveniencias = (("/profiles/id=p10", "pub-2"),)
    assert ids(origens("/profiles/id=p1/name", proveniencias, ATOS)) == ["pub-1"]
