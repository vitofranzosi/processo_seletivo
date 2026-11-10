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
    assert resumo == {"total": 1, "realizados": 0, "em_cartao": True, "sem_vaga": []}


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
    # Com o nome da lista — também o da ampla: sem ele, dois acessos de texto igual (FR-5153).
    assert resumo["sem_vaga"] == [{**orfa, "lista": "Ampla concorrência"}]
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


def test_so_relacao_sem_vaga_nao_promete_cartao():
    """FR-5158: "está na vaga" só é verdade havendo cartão que receba o sorteio."""
    _, resumo = sorteios_por_vaga([_item("vaga-retirada", "iniciais")], CONTEUDO)

    assert not resumo["em_cartao"]


# --- O modelo da página, sobre a leitura (FR-5151, FR-5154, FR-5160) ------------------------------
#
# Os ramos que um certame de teste não alcança sem uma Retificação que retire vaga ou sem dois
# marcos por sorteio: aqui o modelo real é renderizado sobre um contexto de mentira, sem banco.


def _pagina(itens):
    from uuid import UUID

    from django.template.loader import render_to_string

    for n, item in enumerate(itens, start=1):
        item["relacao"].id = UUID(int=n)
        item["relacao"].quantidade = 10 + n
        if item["sorteio"]:
            item["sorteio"].id = UUID(int=100 + n)
    por_vaga, resumo = sorteios_por_vaga(itens, CONTEUDO)
    perfis = [
        {
            "id": perfil["id"],
            "nome": perfil["name"],
            "vagas": 1,
            "documentos_anunciados": {},
            "sorteio": por_vaga.get(perfil["id"]),
        }
        for perfil in CONTEUDO["profiles"]
    ]
    return render_to_string(
        "portal/selecao.html",
        {
            "identificacao_publica": {"sigla": "Cefor", "instituicao": "Ifes", "rotulo": "Cefor"},
            "processo_titulo": "Processo de teste",
            "publicacao_id": UUID(int=900),
            "edital_id": UUID(int=901),
            "voltar_para": "/",
            "perfis": perfis,
            "sorteios": itens,
            "resumo_do_sorteio": resumo,
        },
    )


def test_a_pagina_nomeia_o_marco_quando_a_vaga_tem_dois():
    corpo = _pagina([_item("vaga-1", "iniciais"), _item("vaga-1", "remanescentes")])

    assert "<h4>Sorteio das vagas iniciais</h4>" in corpo
    assert "<h4>Sorteio das vagas remanescentes</h4>" in corpo
    # A vaga sem sorteio não ganha bloco (FR-5150).
    assert corpo.count('<div class="classificacao-da-vaga">') == 1


def test_a_pagina_aponta_a_relacao_de_vaga_retirada_com_o_nome_da_lista():
    """FR-5160, FR-5153: a ampla e a reserva da vaga retirada são dois acessos distinguíveis."""
    itens = [
        _item("vaga-retirada", "x"),
        _item("vaga-retirada", "x", "pcd", sorteado=SORTEADA),
        _item("vaga-1", "iniciais"),
    ]

    corpo = _pagina(itens)
    resumo = corpo[corpo.index('<aside class="sorteio-da-selecao"') : corpo.index("</aside>")]

    assert "De vagas que o Edital vigente já não lista" in resumo
    assert "Ver quem vai participar, e com que número — Ampla concorrência</a>" in resumo
    assert "Ver quem participou, e com que número — Pessoa com Deficiência (PcD)</a>" in resumo
    assert resumo.count("sorteio/relacoes/") == 2
    assert resumo.count("/verificar") == 1
    assert "está na vaga a que o sorteio pertence" in resumo


def test_a_pagina_so_com_relacao_sem_vaga_nao_manda_procurar_no_cartao():
    corpo = _pagina([_item("vaga-retirada", "x")])

    assert "está na vaga a que o sorteio pertence" not in corpo
    assert 'class="classificacao-da-vaga"' not in corpo


def test_listas_sorteadas_em_instantes_diferentes_dizem_cada_uma_a_sua_hora():
    """FR-5154: o estado único cai, e a linha traz a hora — o dia sozinho as deixaria iguais."""
    depois = SORTEADA.replace(minute=45)
    itens = [
        _item("vaga-1", "iniciais", sorteado=SORTEADA),
        _item("vaga-1", "iniciais", "pcd", sorteado=depois),
    ]

    corpo = _pagina(itens)

    assert "✓ Sorteio realizado</span>.</p>" in corpo
    assert "sorteado em 09/11/2026 às 10:30" in corpo
    assert "sorteado em 09/11/2026 às 10:45" in corpo


def test_listas_fechadas_com_um_minuto_de_intervalo_dizem_a_hora():
    outra = FECHADA.replace(minute=1)

    corpo = _pagina(
        [_item("vaga-1", "iniciais"), _item("vaga-1", "iniciais", "pcd", fechada=outra)]
    )

    assert "aguardando; lista fechada em 03/11/2026 às 14:00" in corpo
    assert "aguardando; lista fechada em 03/11/2026 às 14:01" in corpo
