"""O rodízio que segue a agenda e não põe ninguém em dois lugares (179, FR-8207, SC-2842).

A evidência do estudo vira teste: 43 pessoas, 6 avaliadores, 3 bancas simultâneas, dupla avaliação.
Na ordem do protocolo, a mesma dupla ficava com dois candidatos ao mesmo tempo; na da agenda, com o
conflito como inelegibilidade, em nenhuma ordem de protocolo. Sem agenda, a proposta é a de antes.
"""

import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from types import SimpleNamespace as N
from zoneinfo import ZoneInfo

from processo_seletivo.avaliacoes.domain.conflito import Compromisso
from processo_seletivo.avaliacoes.domain.rodizio import CONFLITO_NO_RODIZIO, assinar, propor

ZONA = ZoneInfo("America/Sao_Paulo")
INICIO = datetime(2026, 11, 25, 8, tzinfo=ZONA)


def _membros(n):
    return [N(id=m, identity_subject=f"pessoa-{m}") for m in range(n)]


def _caso(seed, *, n=43, bancas=3):
    """Inscrições com protocolo sorteado, e a agenda preenchida por nome, como a `167` preenche."""
    rnd = random.Random(seed)
    protocolos = list(range(n))
    rnd.shuffle(protocolos)
    inscricoes = [
        N(id=i, nome=f"nome{i:02d}", protocolo=f"INS-{protocolos[i]:04d}") for i in range(n)
    ]
    horario = {}
    for k, inscricao in enumerate(sorted(inscricoes, key=lambda i: i.nome)):
        inicio = INICIO + timedelta(minutes=15 * (k // bancas))
        horario[inscricao.id] = (
            inicio,
            inicio + timedelta(minutes=10),
            f"Banca {k % bancas + 1:02d}",
        )
    return sorted(inscricoes, key=lambda i: i.protocolo), horario


def _propor(inscricoes, membros, **extra):
    return propor(
        previstas=2,
        inscricoes=inscricoes,
        membros=membros,
        ocupacao={},
        carga={},
        impedidos=set(),
        ja_atribuidas=set(),
        ja_concluidas=set(),
        **extra,
    )


def _conflitos(pares, horario):
    por_hora = defaultdict(Counter)
    for inscricao, membro in pares:
        por_hora[horario[inscricao.id][0]][membro.id] += 1
    return sum(1 for contagem in por_hora.values() for n in contagem.values() if n > 1)


def test_sem_agenda_a_proposta_e_a_de_antes():
    inscricoes = [N(id=i, protocolo=f"INS-{i}") for i in range(4)]
    membros = _membros(2)
    pares, _, fora = propor(
        previstas=1,
        inscricoes=inscricoes,
        membros=membros,
        ocupacao={},
        carga={},
        impedidos=set(),
        ja_atribuidas=set(),
        ja_concluidas=set(),
    )
    assert [(i.id, m.id) for i, m in pares] == [(0, 0), (1, 1), (2, 0), (3, 1)]
    assert fora == []
    com_vazio, _, _ = propor(
        previstas=1,
        inscricoes=inscricoes,
        membros=membros,
        ocupacao={},
        carga={},
        impedidos=set(),
        ja_atribuidas=set(),
        ja_concluidas=set(),
        horario={},
        compromissos={},
    )
    assert assinar(com_vazio) == assinar(pares)


def test_na_ordem_do_protocolo_havia_conflito_e_na_da_agenda_nao_ha():
    """O caso do estudo, em dez ordens de protocolo (SC-2842)."""
    membros = _membros(6)
    com_conflito_antes = 0
    for seed in range(10):
        inscricoes, horario = _caso(seed)
        antes, _, _ = _propor(inscricoes, membros)
        com_conflito_antes += _conflitos(antes, horario)
        pares, _, fora = _propor(inscricoes, membros, horario=horario, compromissos={})
        assert _conflitos(pares, horario) == 0, seed
        assert fora == [], seed
        assert len(pares) == 86
        duplas = Counter(frozenset(m.id for i2, m in pares if i2.id == i.id) for i in inscricoes)
        assert len(duplas) == 3, "o ciclo da menor carga forma três duplas, uma por banca"
    assert com_conflito_antes > 0, "a ordem do protocolo produzia conflito: o teste mede algo"


def test_a_ordem_e_a_da_agenda():
    inscricoes, horario = _caso(1, n=6, bancas=2)
    pares, _, _ = _propor(inscricoes, _membros(4), horario=horario, compromissos={})
    vistos = []
    for inscricao, _ in pares:
        if inscricao.id not in vistos:
            vistos.append(inscricao.id)
    assert vistos == sorted(vistos, key=lambda i: (horario[i][0], horario[i][2]))


def test_quem_ja_tem_entrevista_no_horario_e_inelegivel():
    inscricoes, horario = _caso(2, n=2, bancas=2)
    membros = _membros(3)
    inicio, fim, _ = horario[inscricoes[0].id]
    ocupado = {"pessoa-0": [Compromisso(inicio, fim, "outra")]}
    pares, _, _ = _propor(inscricoes, membros, horario=horario, compromissos=ocupado)
    assert all(m.identity_subject != "pessoa-0" for _, m in pares)


def test_sem_ninguem_livre_o_motivo_e_o_conflito():
    inscricoes, horario = _caso(3, n=1, bancas=1)
    membros = _membros(2)
    inicio, fim, _ = horario[inscricoes[0].id]
    ocupados = {m.identity_subject: [Compromisso(inicio, fim, "outra")] for m in membros}
    pares, _, fora = _propor(inscricoes, membros, horario=horario, compromissos=ocupados)
    assert pares == []
    assert fora[0].motivo == CONFLITO_NO_RODIZIO and fora[0].faltam == 2


def test_impedimento_continua_valendo_com_agenda():
    inscricoes, horario = _caso(4, n=1, bancas=1)
    membros = _membros(3)
    pares, _, _ = propor(
        previstas=2,
        inscricoes=inscricoes,
        membros=membros,
        ocupacao={},
        carga={},
        impedidos={("pessoa-0", inscricoes[0].id)},
        ja_atribuidas=set(),
        ja_concluidas=set(),
        horario=horario,
        compromissos={},
    )
    assert {m.identity_subject for _, m in pares} == {"pessoa-1", "pessoa-2"}


def test_a_proposta_com_agenda_e_reproduzivel():
    inscricoes, horario = _caso(5)
    membros = _membros(6)
    a, _, _ = _propor(inscricoes, membros, horario=horario, compromissos={})
    b, _, _ = _propor(list(reversed(inscricoes)), membros, horario=horario, compromissos={})
    assert assinar(a) == assinar(b)
