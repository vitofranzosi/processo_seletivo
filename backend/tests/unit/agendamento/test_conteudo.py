"""O conteúdo público da agenda: só o que a FR-7225 permite (167, T042, SC-2394, `D-009`).

O conteúdo é composto com dados de propósito "vazáveis" — a banca remota com o endereço da sala, a
pessoa com CPF, e-mail e telefone à mão — e os bytes canônicos são varridos atrás de cada um. A
função não recebe CPF, e-mail nem telefone; o teste prova que ela também não deixa passar o
endereço da sala, que ela recebe.
"""

from datetime import date, datetime, time

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.conteudo import Item, compor
from processo_seletivo.agendamento.domain.horarios import zona
from processo_seletivo.shared.canonical import canonical_bytes

SALA = "https://sala.exemplo/secreta-123"
CPF = "111.444.777-35"
EMAIL = "candidata1@exemplo.br"
TELEFONE = "(27) 99999-0000"
MODALIDADE = "PPI"


def _instante(dia, hora, minuto=0):
    return datetime.combine(dia, time(hora, minuto), tzinfo=zona())


SEG = date(2026, 11, 23)
TER = date(2026, 11, 24)
ITENS = [
    Item(_instante(TER, 8), _instante(TER, 8, 10), "Banca 1", "Beatriz Souza", "INS-2026-0002"),
    Item(_instante(SEG, 9), _instante(SEG, 9, 10), "Banca 2", "Álvaro Lima", "INS-2026-0001"),
    Item(_instante(SEG, 9), _instante(SEG, 9, 10), "Banca 1", "Carla Dias", "INS-2026-0003"),
]


def _compor(*, forma=nomes.REMOTA, bancas=(("Banca 1", SALA), ("Banca 2", SALA)), restrita=False):
    return compor(
        unidade={"cabecalho": ["Cefor"], "local": "Vitória (ES)", "sigla": "Cefor", "nome": "C"},
        edital="Edital 146/2025",
        etapa="Entrevista",
        publicado_em=None,
        signatario={"nome": "Diretora", "cargo": "Diretora-Geral", "atoDeNomeacao": ""},
        veiculo=nomes.VEICULO_GPS,
        forma=forma,
        duracao=10,
        bancas=list(bancas),
        itens=ITENS,
        restrita=restrita,
    )


def test_nome_e_protocolo_por_dia_e_por_horario():
    conteudo = _compor()

    assert conteudo["cabecalho"]["identificacao"] == nomes.NOME_E_PROTOCOLO
    assert [dia["dia"] for dia in conteudo["dias"]] == ["2026-11-23", "2026-11-24"]
    segunda = conteudo["dias"][0]["horarios"]
    # No mesmo início, as bancas na ordem da configuração (FR-7213).
    assert [h["banca"] for h in segunda] == ["Banca 1", "Banca 2"]
    assert segunda[0]["pessoa"] == {"nome": "Carla Dias", "protocolo": "INS-2026-0003"}


def test_na_etapa_restrita_por_modalidade_so_o_protocolo():
    conteudo = _compor(restrita=True)

    assert conteudo["cabecalho"]["identificacao"] == nomes.PROTOCOLO
    pessoas = [h["pessoa"] for dia in conteudo["dias"] for h in dia["horarios"]]
    assert all(set(pessoa) == {"protocolo"} for pessoa in pessoas)
    texto = canonical_bytes(conteudo).decode()
    assert "Beatriz" not in texto and "Álvaro" not in texto


def test_a_banca_so_aparece_com_mais_de_uma():
    conteudo = _compor(bancas=(("Banca 1", SALA),))

    assert all("banca" not in h for dia in conteudo["dias"] for h in dia["horarios"])


def test_o_local_so_na_forma_presencial():
    presencial = _compor(forma=nomes.PRESENCIAL, bancas=(("Sala 101", "Bloco B, sala 101"),))
    remota = _compor(bancas=(("Banca 1", SALA),))

    assert presencial["bancas"] == [{"nome": "Sala 101", "local": "Bloco B, sala 101"}]
    assert remota["bancas"] == [{"nome": "Banca 1", "local": ""}]


def test_nada_de_sala_cpf_email_telefone_ou_modalidade_nos_bytes():
    """SC-2394: os bytes canônicos não carregam nenhum dado que a FR-7226 proíbe."""
    for restrita in (False, True):
        texto = canonical_bytes(_compor(restrita=restrita)).decode()
        for proibido in (SALA, "secreta", CPF, "11144477735", "777-35", EMAIL, TELEFONE):
            assert proibido not in texto, proibido
        assert f'"{MODALIDADE}"' not in texto
