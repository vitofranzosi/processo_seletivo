"""O conflito de horário de quem avalia (179, FR-8202, FR-8203).

A conta é a do intervalo semiaberto: cada entrevista começa antes de a outra terminar. Os que só se
tocam não conflitam, e o intervalo entre atendimentos não entra. A varredura é conferida contra a
comparação de todos os pares, para que a otimização nunca mude a resposta.
"""

import random
from datetime import datetime, timedelta
from itertools import combinations
from zoneinfo import ZoneInfo

from processo_seletivo.avaliacoes.domain.conflito import Compromisso, cabe, conflitos, sobrepoem

ZONA = ZoneInfo("America/Sao_Paulo")


def conflitos_por_forca_bruta(compromissos_por_pessoa) -> set:
    """A mesma pergunta, por todos os pares: a referência contra a qual a varredura é conferida."""
    pares = set()
    for pessoa, lista in compromissos_por_pessoa.items():
        for a, b in combinations(lista, 2):
            if a.inscricao_id != b.inscricao_id and sobrepoem(a.inicio, a.fim, b.inicio, b.fim):
                pares.add((pessoa, frozenset({str(a.inscricao_id), str(b.inscricao_id)})))
    return pares


def _h(dia, hora, minuto=0):
    return datetime(2026, 11, dia, hora, minuto, tzinfo=ZONA)


def _c(inscricao, dia, hora, minuto=0, duracao=15, banca="Banca 01"):
    inicio = _h(dia, hora) + timedelta(minutes=minuto)
    return Compromisso(inicio, inicio + timedelta(minutes=duracao), inscricao, "etapa", banca)


def test_igual_contido_e_parcial_conflitam():
    assert sobrepoem(_h(25, 8), _h(25, 8, 15), _h(25, 8), _h(25, 8, 15))
    assert sobrepoem(_h(25, 8), _h(25, 9), _h(25, 8, 15), _h(25, 8, 30))
    assert sobrepoem(_h(25, 8), _h(25, 8, 20), _h(25, 8, 15), _h(25, 8, 35))


def test_horarios_que_so_se_tocam_nao_conflitam():
    """Quem sai de uma sala às 08:15 entra na seguinte às 08:15."""
    assert not sobrepoem(_h(25, 8), _h(25, 8, 15), _h(25, 8, 15), _h(25, 8, 30))
    assert conflitos({"ana": [_c("a", 25, 8), _c("b", 25, 8, 15)]}) == []


def test_o_intervalo_entre_atendimentos_nao_entra_na_conta():
    """Com 10 de duração e 5 de intervalo, 08:00–08:10 e 08:15–08:25 estão livres um do outro."""
    assert conflitos({"ana": [_c("a", 25, 8, 0, 10), _c("b", 25, 8, 15, 10)]}) == []


def test_dias_diferentes_nao_conflitam():
    assert conflitos({"ana": [_c("a", 25, 8), _c("b", 26, 8)]}) == []


def test_o_conflito_diz_a_pessoa_e_as_duas_entrevistas_em_ordem():
    achados = conflitos({"ana": [_c("b", 25, 8, 5, banca="Banca 02"), _c("a", 25, 8)]})
    assert len(achados) == 1
    assert achados[0].pessoa == "ana"
    assert achados[0].primeiro.inscricao_id == "a"
    assert achados[0].segundo.banca_nome == "Banca 02"
    assert achados[0].inscricoes == {"a", "b"}


def test_pessoas_diferentes_no_mesmo_horario_nao_conflitam():
    assert conflitos({"ana": [_c("a", 25, 8)], "bruno": [_c("b", 25, 8)]}) == []


def test_a_mesma_inscricao_duas_vezes_nao_e_conflito_consigo():
    """Duas Etapas não dão dois horários à mesma inscrição na mesma agenda; mas quem chama pode
    repetir o compromisso, e repetir não é estar em dois lugares."""
    assert conflitos({"ana": [_c("a", 25, 8), _c("a", 25, 8)]}) == []


def test_cabe_aponta_o_compromisso_que_impede_e_ignora_o_da_propria_inscricao():
    agenda = [_c("a", 25, 8), _c("b", 25, 9)]
    impede = cabe(agenda, _h(25, 9, 5), _h(25, 9, 20))
    assert impede is not None and impede.inscricao_id == "b"
    assert cabe(agenda, _h(25, 8, 15), _h(25, 8, 30)) is None
    assert cabe(agenda, _h(25, 9, 5), _h(25, 9, 20), exceto="b") is None


def test_passado_quando_as_duas_ja_terminaram():
    achados = conflitos({"ana": [_c("a", 25, 8), _c("b", 25, 8, 5)]}, agora=_h(25, 10))
    assert achados[0].passado is True
    achados = conflitos({"ana": [_c("a", 25, 8), _c("b", 25, 8, 5)]}, agora=_h(25, 8, 10))
    assert achados[0].passado is False


def test_a_saida_e_estavel_e_igual_a_forca_bruta():
    rnd = random.Random(179)
    for _ in range(50):
        por_pessoa = {}
        for pessoa in ("ana", "bruno", "carla"):
            lista = [
                _c(f"{pessoa}-{i}", 25, 8, rnd.choice(range(0, 120, 5)), rnd.choice((10, 15, 20)))
                for i in range(12)
            ]
            rnd.shuffle(lista)
            por_pessoa[pessoa] = lista
        achados = conflitos(por_pessoa)
        assert {
            (c.pessoa, frozenset({str(c.primeiro.inscricao_id), str(c.segundo.inscricao_id)}))
            for c in achados
        } == conflitos_por_forca_bruta(por_pessoa)
        embaralhado = {p: list(reversed(lista)) for p, lista in por_pessoa.items()}
        assert conflitos(embaralhado) == achados
