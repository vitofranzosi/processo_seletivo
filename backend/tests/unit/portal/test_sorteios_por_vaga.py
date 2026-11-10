"""Os sorteios do Edital na forma do cartão da vaga (145, FR-5150 a FR-5154, FR-5160).

Relações e sorteios de mentira, com os atributos que `sorteios_do_edital` entrega: o que se testa é
a reorganização, e ela não lê o banco. Os casos de página estão em
`tests/portal/test_sorteio_na_pagina_do_edital.py`.
"""

from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from processo_seletivo.portal.leitura import sorteios_por_vaga

FUSO = ZoneInfo("America/Sao_Paulo")
FECHADA = datetime(2026, 11, 3, 14, 0, tzinfo=FUSO)
SORTEADA = datetime(2026, 11, 9, 10, 30, tzinfo=FUSO)

CONTEUDO = {
    "profiles": [
        {
            "id": "vaga-1",
            "name": "Design Educacional",
            "classificationMilestones": [
                {"id": "iniciais", "name": "Sorteio das vagas iniciais"},
                {"id": "remanescentes", "name": "Sorteio das vagas remanescentes"},
            ],
            "competitionModalities": [
                {"id": "pcd", "name": "Pessoa com Deficiência (PcD)"},
                {"id": "ppi", "name": "Pretos, Pardos e Indígenas (PPI)"},
            ],
        },
        {"id": "vaga-2", "name": "Professor Mediador", "classificationMilestones": []},
    ]
}
NOMES = {"pcd": "Pessoa com Deficiência (PcD)", "ppi": "Pretos, Pardos e Indígenas (PPI)"}


def _item(perfil, marco, lista=None, *, sorteado=None, fechada=FECHADA, versao=None):
    nome_do_marco = {
        "iniciais": "Sorteio das vagas iniciais",
        "remanescentes": "Sorteio das vagas remanescentes",
    }.get(marco, "")
    return {
        "relacao": SimpleNamespace(
            perfil_id=perfil, marco_id=marco, lista_id=lista, publicada_em=fechada, versao=versao
        ),
        "sorteio": SimpleNamespace(executado_em=sorteado) if sorteado else None,
        "perfil": "Design Educacional" if perfil == "vaga-1" else "",
        "marco": nome_do_marco,
        "lista": NOMES.get(lista, ""),
    }


def test_a_vaga_sem_relacao_nao_ganha_nada():
    """FR-5150: a que classifica por outro método não tem bloco nem frase de ausência."""
    por_vaga, resumo = sorteios_por_vaga([_item("vaga-1", "iniciais")], CONTEUDO)

    assert "vaga-2" not in por_vaga
    assert resumo == {"total": 1, "realizados": 0, "sem_vaga": []}


def test_a_ampla_vem_primeiro_e_as_listas_na_ordem_que_o_perfil_declara():
    """FR-5152, FR-5153: a ordem de publicação das relações não decide a ordem da leitura."""
    itens = [
        _item("vaga-1", "iniciais", "ppi"),
        _item("vaga-1", "iniciais", "pcd"),
        _item("vaga-1", "iniciais"),
    ]

    por_vaga, _ = sorteios_por_vaga(itens, CONTEUDO)
    marco = por_vaga["vaga-1"]["marcos"][0]

    assert [lista["nome"] for lista in marco["listas"]] == [
        "Ampla concorrência",
        "Pessoa com Deficiência (PcD)",
        "Pretos, Pardos e Indígenas (PPI)",
    ]
    assert not por_vaga["vaga-1"]["varios_marcos"]


def test_os_marcos_vem_na_ordem_do_edital_e_so_entao_sao_nomeados():
    """FR-5151: com um marco só o nome é ruído; com dois, é o que diz de qual sorteio se fala."""
    itens = [_item("vaga-1", "remanescentes"), _item("vaga-1", "iniciais")]

    por_vaga, _ = sorteios_por_vaga(itens, CONTEUDO)

    assert por_vaga["vaga-1"]["varios_marcos"]
    assert [marco["nome"] for marco in por_vaga["vaga-1"]["marcos"]] == [
        "Sorteio das vagas iniciais",
        "Sorteio das vagas remanescentes",
    ]


def test_o_estado_e_dito_uma_vez_so_quando_as_listas_estao_no_mesmo_ponto():
    """FR-5154: três aguardando são uma frase; uma sorteada entre três, não."""
    aguardando, _ = sorteios_por_vaga(
        [_item("vaga-1", "iniciais"), _item("vaga-1", "iniciais", "pcd")], CONTEUDO
    )
    misto, resumo = sorteios_por_vaga(
        [_item("vaga-1", "iniciais"), _item("vaga-1", "iniciais", "pcd", sorteado=SORTEADA)],
        CONTEUDO,
    )
    sorteado, _ = sorteios_por_vaga(
        [
            _item("vaga-1", "iniciais", sorteado=SORTEADA),
            _item("vaga-1", "iniciais", "pcd", sorteado=SORTEADA),
        ],
        CONTEUDO,
    )

    assert aguardando["vaga-1"]["marcos"][0]["aguardando"]
    assert aguardando["vaga-1"]["marcos"][0]["uniforme"]
    assert not misto["vaga-1"]["marcos"][0]["uniforme"]
    assert misto["vaga-1"]["marcos"][0]["realizados"] == 1
    assert resumo["realizados"] == 1
    assert sorteado["vaga-1"]["marcos"][0]["realizado"]
    assert sorteado["vaga-1"]["marcos"][0]["executado_em"] == SORTEADA


def test_listas_fechadas_em_instantes_diferentes_nao_ganham_uma_data_so():
    """FR-5154: a frase única diria a hora de uma lista só — então cada linha diz a sua."""
    outra = FECHADA.replace(day=4)

    por_vaga, _ = sorteios_por_vaga(
        [_item("vaga-1", "iniciais"), _item("vaga-1", "iniciais", "pcd", fechada=outra)], CONTEUDO
    )

    assert not por_vaga["vaga-1"]["marcos"][0]["aguardando"]
    assert not por_vaga["vaga-1"]["marcos"][0]["uniforme"]


def test_a_relacao_de_vaga_que_o_vigente_nao_lista_fica_no_resumo():
    """FR-5160: ela continua publicada, e não há cartão que a receba — sumir esconderia um ato."""
    orfa = _item("vaga-retirada", "iniciais")

    por_vaga, resumo = sorteios_por_vaga([orfa, _item("vaga-1", "iniciais")], CONTEUDO)

    assert list(por_vaga) == ["vaga-1"]
    assert resumo["sem_vaga"] == [orfa]
    assert resumo["total"] == 2


def test_a_lista_que_o_vigente_nao_nomeia_e_lida_da_versao_que_a_relacao_citou():
    """FR-5153: sem nome ela se confundiria com a ampla; o nome é o que o Edital publicou."""
    versao = SimpleNamespace(
        content={
            "profiles": [
                {"id": "vaga-1", "competitionModalities": [{"id": "idosos", "name": "Idosos"}]}
            ]
        }
    )

    por_vaga, _ = sorteios_por_vaga(
        [_item("vaga-1", "iniciais", "idosos", versao=versao)], CONTEUDO
    )

    assert por_vaga["vaga-1"]["marcos"][0]["listas"][0]["nome"] == "Idosos"
