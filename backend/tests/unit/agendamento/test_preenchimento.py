"""A ordem do preenchimento automático (167, T023, FR-7213, FR-7214, SC-2392)."""

from collections import Counter
from datetime import date, time

from processo_seletivo.agendamento.domain.horarios import Banca, Configuracao, derivar
from processo_seletivo.agendamento.domain.preenchimento import ORDEM, Pessoa, propor

SEG = date(2026, 11, 23)
TER = date(2026, 11, 24)
MANHA_E_TARDE = ((time(8), time(12)), (time(13), time(17)))


def horarios(dias=((SEG, MANHA_E_TARDE),), n_bancas=1):
    return derivar(
        Configuracao(
            "REMOTA",
            10,
            5,
            dias,
            tuple(Banca(f"b{n}", f"Banca {n}", "", n) for n in range(1, n_bancas + 1)),
        )
    )


def pessoas(quantas):
    return [Pessoa(f"i{n:02d}", f"Pessoa {n:02d}", f"INS-2026-{n:04d}") for n in range(quantas)]


def test_32_recebem_e_11_sobram():
    proposta = propor(pessoas(43), horarios())

    assert proposta.recebem == 32
    assert len(proposta.sem_horario) == 11
    assert proposta.livres == ()
    assert proposta.frase == "32 pessoas recebem horário. 11 continuam sem horário."
    assert proposta.ordem == ORDEM


def test_todas_recebem_com_64_horarios():
    proposta = propor(pessoas(43), horarios(((SEG, MANHA_E_TARDE), (TER, MANHA_E_TARDE))))

    assert proposta.frase == "Todas as 43 pessoas recebem horário."
    assert len(proposta.livres) == 21
    assert proposta.por_dia_e_banca == {(SEG, "b1"): 32, (TER, "b1"): 11}


def test_pessoas_pelo_nome_sem_acento_e_pelo_protocolo_no_empate():
    """ "Álvaro" não vai para o fim da fila por causa do acento (T-011)."""
    lista = [
        Pessoa("z", "Zélia", "INS-2026-0001"),
        Pessoa("a2", "Ana", "INS-2026-0009"),
        Pessoa("al", "Álvaro", "INS-2026-0005"),
        Pessoa("a1", "ana", "INS-2026-0003"),
    ]
    proposta = propor(lista, horarios())

    assert [pessoa.inscricao_id for pessoa, _ in proposta.pares] == ["al", "a1", "a2", "z"]
    inicios = [horario.inicio for _, horario in proposta.pares]
    assert inicios == sorted(inicios)


def test_as_bancas_lado_a_lado_em_cada_horario():
    proposta = propor(pessoas(4), horarios(n_bancas=2))

    assert [horario.banca_id for _, horario in proposta.pares] == ["b1", "b2", "b1", "b2"]
    assert proposta.pares[0][1].inicio == proposta.pares[1][1].inicio


def test_quem_ja_tem_horario_nao_entra_e_o_horario_dele_nao_e_dado():
    """SC-2392: o horário ocupado não está entre os livres, e a pessoa não está entre as sem."""
    todos = horarios()
    ocupado = todos[5]
    livres = [h for h in todos if h != ocupado]
    proposta = propor(pessoas(40), livres)

    assert ocupado not in [h for _, h in proposta.pares]
    assert len({h.chave for _, h in proposta.pares}) == len(proposta.pares)
    contagem = Counter(p.inscricao_id for p, _ in proposta.pares)
    assert max(contagem.values()) == 1
