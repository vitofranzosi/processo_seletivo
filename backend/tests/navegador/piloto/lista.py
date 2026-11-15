"""Os doze estados da Lista de Processos Seletivos (172, D-004, L-01 a L-12).

A carga é a de `tests/fixtures/lista_de_processos.py`, direto no banco e sem o ciclo de publicação,
como os testes da `129` fazem; o ciclo inteiro só onde o estado depende dele (a Retificação em
curso do L-09 e a comissão do L-10).

**O seletor de identidade fica ligado em todo estado**, porque é por ele que a jornada entra — e por
isso o aviso "Ambiente de demonstração." aparece em todos, como no banco de demonstração em que a
equipe vai ler a tela.
"""

from django.test import Client
from django.urls import reverse

from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.lista_de_processos import muitos, processo
from tests.interface.conftest import identificar
from tests.navegador.piloto.estados import Montagem, estado

LISTA = reverse("interface:lista")
Status = ProcessoSeletivo.Status


def _sessao(request, subject, papeis):
    request.getfixturevalue("seletor_ligado")
    cliente = Client()
    identificar(cliente, subject, papeis)
    return cliente


def _acervo():
    """Os cinco Processos que as abas e a busca mostram."""
    processo(
        "Seleção de tutores em elaboração", editais=[("1", 2026, "EM_ELABORACAO")], ha_minutos=1
    )
    processo(
        "Seleção de bolsistas",
        editais=[("2", 2026, "PUBLICADO"), ("3", 2026, "PUBLICADO", "Edital 3/2026 — Libras")],
        ha_minutos=2,
    )
    processo("Processo ainda sem Edital", status=Status.EM_ELABORACAO, ha_minutos=3)
    processo(
        "Seleção encerrada",
        status=Status.ENCERRADO,
        editais=[("4", 2026, "ENCERRADO")],
        ha_minutos=4,
    )
    processo(
        "Seleção cancelada",
        status=Status.CANCELADO,
        editais=[("90", 2026, "CANCELADO")],
        ha_minutos=5,
    )


QUEM_CRIA_E_ELABORA = ("gabi.gestora", ["gestor", "elaborador"])


@estado(
    "L-01",
    tela="lista",
    papel="quem gere e elabora",
    prova="Ações disponíveis para você",
    acao_principal="Novo Processo Seletivo",
)
def em_andamento(request):
    _acervo()
    return Montagem(LISTA, _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado("L-02", tela="lista", papel="quem gere e elabora", prova="Seleção encerrada")
def encerrados(request):
    _acervo()
    return Montagem(LISTA + "?situacao=encerrados", _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado("L-03", tela="lista", papel="quem gere e elabora", prova="Seleção cancelada")
def cancelados(request):
    _acervo()
    return Montagem(LISTA + "?situacao=cancelados", _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado("L-04", tela="lista", papel="quem gere e elabora", prova="Processo ainda sem Edital")
def todos(request):
    _acervo()
    return Montagem(LISTA + "?situacao=todos", _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado(
    "L-05", tela="lista", papel="quem gere e elabora", prova="1 Processo encontrado para “90/2026”"
)
def busca_com_resultado(request):
    _acervo()
    return Montagem(LISTA + "?busca=90%2F2026", _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado(
    "L-06",
    tela="lista",
    papel="quem gere e elabora",
    prova="Nenhum Processo encontrado para “inexistente”",
)
def busca_sem_resultado(request):
    _acervo()
    return Montagem(LISTA + "?busca=inexistente", _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado(
    "L-07",
    tela="lista",
    papel="quem gere e elabora",
    prova="Nenhum Processo Seletivo no seu escopo institucional.",
)
def escopo_vazio(request):
    return Montagem(LISTA, _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado("L-08", tela="lista", papel="quem gere e elabora", prova="25 Processos, mostrando 21–25.")
def segunda_pagina(request):
    muitos(25)
    return Montagem(LISTA + "?pagina=2", _sessao(request, *QUEM_CRIA_E_ELABORA))


@estado("L-09", tela="lista", papel="quem homologa", prova="Retificação em revisão · aguarda")
def retificacao_em_curso(request):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.publicacao import publish_original
    from tests.interface.test_acoes_disponiveis import submetida

    request.getfixturevalue("seletor_ligado")
    edital = publish_original(
        request.getfixturevalue("api_client"),
        request.getfixturevalue("manager_headers"),
        request.getfixturevalue("process_payload"),
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    submetida(edital, vigente)
    return Montagem(LISTA, _sessao(request, "bruno.homologador", ["homologador"]))


@estado(
    "L-10",
    tela="lista",
    papel="quem preside uma comissão e integra outra",
    prova="Você preside a comissão",
)
def presidencia_e_membro(request):
    from tests.fixtures.comissao import constituir

    request.getfixturevalue("comissao_de_a")
    gestor = request.getfixturevalue("gestor")
    outro = processo("Seleção de mediadores", editais=[("7", 2026, "PUBLICADO")], ha_minutos=1)
    constituir(gestor, outro, [("ana.membro", "PRESIDENTE"), ("maria", "MEMBRO")], prefixo="piloto")
    return Montagem(LISTA, _sessao(request, "maria", []))


@estado(
    "L-11",
    tela="lista",
    papel="quem elabora, sem Edital a elaborar",
    prova="Nenhum ato de Edital ou de Retificação, recurso ou avaliação aguarda você agora.",
)
def sem_faixa_e_sem_criar(request):
    processo("Seleção de bolsistas", editais=[("2", 2026, "PUBLICADO")])
    return Montagem(LISTA, _sessao(request, "ana.elaboradora", ["elaborador"]))


@estado("L-12", tela="lista", papel="sem papel nenhum", prova="Sem permissões.")
def sem_papel(request):
    processo("Seleção de bolsistas", editais=[("2", 2026, "PUBLICADO")])
    # Quem entra sem papel cai em Minhas atividades; a Lista se abre pelo endereço.
    return Montagem(LISTA, _sessao(request, "servidor.novo", []))
