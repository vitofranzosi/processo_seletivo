"""Os estados da Ocupação de vagas: a página (O-01 a O-18) e o retorno de cada gesto (R-01 a R-12).

Os cenários são os dos testes de tela da `016`, da `034`, da `097` e da `155`, pelas funções de
`tests/fixtures/ocupacao_da_tela.py` e pelos ajudantes que aqueles testes já exportam.

**O retorno se monta pelo cliente da sessão, e não por clique.** A tela guarda o resultado do gesto na
sessão e o devolve no GET seguinte (`resultado_da_ocupacao`, `erro_da_ocupacao`). A jornada usa o
mesmo `sessionid` do cliente: o POST que o cliente faz antes de o navegador abrir a página é o mesmo
gesto, e a página que abre é o retorno dele. Clicar exigiria, para as recusas, um botão que a tela
de propósito não oferece.
"""

from django.test import Client
from django.urls import reverse

from tests.fixtures import ocupacao_da_tela as cenarios
from tests.fixtures.corte import MARCO
from tests.interface.conftest import identificar
from tests.navegador.piloto.estados import Montagem, estado

QUEM_EMITE = ("carlos", ["gestor"])
QUEM_EMITE_E_RETIFICA = ("carlos", ["gestor", "elaborador"])
QUEM_SO_LE = ("aud", ["auditor"])


def _sessao(request, subject, papeis):
    request.getfixturevalue("seletor_ligado")
    cliente = Client()
    identificar(cliente, subject, papeis)
    return cliente


def _base(request):
    request.getfixturevalue("raiz_de_arquivos")
    return (
        request.getfixturevalue("gestor"),
        request.getfixturevalue("api_client"),
        request.getfixturevalue("manager_headers"),
        request.getfixturevalue("process_payload"),
    )


def _url(edital, marco=MARCO):
    return reverse("interface:ocupacao", args=[edital.id, marco])


def _cenario_padrao(request):
    """O `cenario` de `tests/interface/conftest.py`: ampla com ordem, PPI sem ordem, nada apurado."""
    from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

    edital, _, inscricoes = montar_cenario_da_ocupacao(
        *_base(request), prefixo="ocupacao-016-tela", geral=3, ppi=2
    )
    return edital, inscricoes


def _apurar(edital, gestor, chave):
    from tests.integration.ocupacao.test_emissao import apurar

    apurar(edital, gestor, chave=chave)


# ── A página ─────────────────────────────────────────────────────────────────────────────────────


@estado("O-01", tela="ocupacao", papel="quem emite", prova="Abrir a ocupação da")
def marco_intermediario(request):
    from tests.fixtures import marco_intermediario as m900

    cenario = m900.ate_a_apuracao_m2(m900.montar(*_base(request)))
    return Montagem(_url(cenario["edital"], m900.MARCO_1), _sessao(request, *QUEM_EMITE))


def _sem_quadro(request):
    from tests.fixtures.corte import montar_cenario_do_corte
    from tests.fixtures.legado import antes_do_quadro

    edital, _, _ = montar_cenario_do_corte(
        *_base(request), prefixo="ocupacao-016-tela", publicar=antes_do_quadro
    )
    return edital


@estado(
    "O-02",
    tela="ocupacao",
    papel="quem emite e não retifica",
    prova="quem elabora Retificações é quem pode declará-la",
)
def sem_quadro(request):
    return Montagem(_url(_sem_quadro(request)), _sessao(request, *QUEM_EMITE))


@estado(
    "O-03",
    tela="ocupacao",
    papel="quem emite e retifica",
    prova="abrir a Retificação deste Edital",
)
def sem_quadro_para_quem_retifica(request):
    return Montagem(_url(_sem_quadro(request)), _sessao(request, *QUEM_EMITE_E_RETIFICA))


@estado(
    "O-04",
    tela="ocupacao",
    papel="quem emite",
    prova="Apurar a ocupação deste recorte",
    acao_principal="Apurar a ocupação deste recorte",
)
def nao_apurado_com_ordem(request):
    from tests.fixtures.ocupacao import MODALIDADE_PPI
    from tests.fixtures.recortes import emitir_recorte

    edital, _ = _cenario_padrao(request)
    emitir_recorte(edital, request.getfixturevalue("gestor"), lista_id=MODALIDADE_PPI, chave="piloto-o04")
    return Montagem(_url(edital), _sessao(request, *QUEM_EMITE))


@estado(
    "O-05",
    tela="ocupacao",
    papel="quem emite",
    prova="Este recorte ainda não tem ordem emitida",
)
def nao_apurado_sem_ordem(request):
    edital, _ = _cenario_padrao(request)
    return Montagem(_url(edital), _sessao(request, *QUEM_EMITE))


@estado("O-06", tela="ocupacao", papel="quem preside a comissão", prova="Não se aplica.")
def tres_recortes(request):
    from tests.fixtures.sorteio import LISTA_PPI, certame_com_cotas

    certame = certame_com_cotas(*_base(request), quantos=3, modalidades={0: LISTA_PPI})
    return Montagem(_url(certame["edital"], certame["marco"]), _sessao(request, "maria", []))


@estado(
    "O-07",
    tela="ocupacao",
    papel="quem emite",
    prova="Pedir a faixa seguinte com este déficit",
    acao_principal="Pedir a faixa seguinte com este déficit",
)
def com_faixa_seguinte(request):
    gestor = request.getfixturevalue("gestor")
    edital, _, _ = cenarios.com_continuacao(*_base(request))
    _apurar(edital, gestor, "piloto-o07")
    return Montagem(_url(edital), _sessao(request, *QUEM_EMITE))


@estado(
    "O-08",
    tela="ocupacao",
    papel="quem emite",
    prova="não publicou que admite chamar além da faixa",
)
def sem_continuacao(request):
    edital, _ = _cenario_padrao(request)
    _apurar(edital, request.getfixturevalue("gestor"), "piloto-o08")
    return Montagem(_url(edital), _sessao(request, *QUEM_EMITE))


@estado("O-09", tela="ocupacao", papel="quem emite", prova="Este marco não declara regra de corte")
def sem_regra_de_corte(request):
    edital, _, _ = cenarios.sem_regra_de_corte(*_base(request))
    _apurar(edital, request.getfixturevalue("gestor"), "piloto-o09")
    return Montagem(_url(edital), _sessao(request, *QUEM_EMITE))


@estado("O-10", tela="ocupacao", papel="quem só lê", prova="A presidência não é papel")
def para_quem_so_le(request):
    edital, _ = _cenario_padrao(request)
    _apurar(edital, request.getfixturevalue("gestor"), "piloto-o10")
    return Montagem(_url(edital), _sessao(request, *QUEM_SO_LE))


def _acrescentar(cliente, edital, quantidade=1, **campos):
    from tests.interface.test_acrescimo import acrescentar_pela_tela

    return acrescentar_pela_tela(cliente, edital, quantidade)


@estado("O-11", tela="ocupacao", papel="quem emite", prova="0 A ocupar")
def sem_vaga_a_ocupar(request):
    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    _acrescentar(cliente, edital)
    # O GET do retorno consome o resultado: a página fotografada é a ocupação depois dele.
    cliente.get(_url(edital))
    return Montagem(_url(edital), cliente)


@estado(
    "O-13",
    tela="ocupacao",
    papel="quem emite",
    prova="desfazimento de 1 vaga",
    acao_principal="Conferir o desfazimento",
)
def com_vagas_acrescidas(request):
    from tests.interface.test_acrescimo import assinatura_de, desfazer

    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    acrescimo = _acrescentar(cliente, edital, 2)
    pagina = desfazer(cliente, edital, acrescimo).content.decode()
    desfazer(
        cliente,
        edital,
        acrescimo,
        confirmar="1",
        motivo="Matrícula efetivada no Edital regular",
        leitura=assinatura_de(pagina),
    )
    cliente.get(_url(edital))
    return Montagem(_url(edital), cliente)


@estado(
    "O-12",
    tela="ocupacao",
    papel="quem emite",
    prova="Esta apuração está obsoleta.",
)
def obsoleta(request):
    from processo_seletivo.ocupacao.domain import nomes
    from tests.fixtures.sorteio import MARCO as MARCO_DO_SORTEIO

    certame = cenarios.pela_desistencia(
        *_base(request), "tela-saldo-155", reversao=nomes.REVERSAO_POR_SALDO
    )
    return Montagem(_url(certame["edital"], MARCO_DO_SORTEIO), _sessao(request, *QUEM_EMITE))


@estado("O-14", tela="ocupacao", papel="quem emite", prova="Reversão de cota:")
def com_movimento(request):
    from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
    from processo_seletivo.ocupacao.domain import nomes
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
    from tests.fixtures.sorteio import MARCO as MARCO_DO_SORTEIO

    gestor = request.getfixturevalue("gestor")
    certame = certame_sorteado_com_quadro(
        *_base(request), prefixo="tela-mov-016", reversao=nomes.REVERSAO_POR_SALDO
    )
    for lista, chave in ((LISTA_PPI, "piloto-o14-ppi"), (None, "piloto-o14-ampla")):
        emitir_apuracao(
            actor=gestor,
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO_DO_SORTEIO,
            lista_id=lista,
            idempotency_key=chave,
            correlation_id="piloto-172",
        )
    return Montagem(_url(certame["edital"], MARCO_DO_SORTEIO), _sessao(request, *QUEM_EMITE))


def _silente(request):
    from tests.fixtures.sorteio import MARCO as MARCO_DO_SORTEIO

    certame = cenarios.silente(*_base(request))
    cenarios.encerrar_o_prazo(request.getfixturevalue("monkeypatch"))
    return certame, _url(certame["edital"], MARCO_DO_SORTEIO)


FUNDAMENTO = "O Edital não declara reversão, e ninguém concorre pela cota."


def _declarar(cliente, certame):
    from processo_seletivo.ocupacao.models import VagaNaoPreenchida
    from tests.interface.test_destinacao_na_ocupacao import assinatura_de, declarar_pela_tela

    conferencia = declarar_pela_tela(cliente, certame).content.decode()
    declarar_pela_tela(
        cliente, certame, confirmar="1", leitura=assinatura_de(conferencia), fundamento=FUNDAMENTO
    )
    return VagaNaoPreenchida.objects.get()


def _chamada_dependente(request):
    from processo_seletivo.interface import destinacao_da_vaga

    chamada = {"id": "00000000-0000-4000-8000-00000000c155", "rotulo": "P-0701 — Fulana"}

    def dependentes(**pergunta):
        return [{**chamada, "ocupa": False}] if pergunta.get("nao_preenchida_id") else []

    request.getfixturevalue("monkeypatch").setattr(
        destinacao_da_vaga, "chamadas_dependentes", dependentes
    )
    return dependentes


@estado(
    "O-15",
    tela="ocupacao",
    papel="quem emite e retifica",
    prova="Este Edital não declara o que acontece com a vaga reservada não preenchida.",
    acao_principal="Declarar a vaga não preenchida",
)
def vaga_sem_quem_a_ocupe(request):
    _, url = _silente(request)
    return Montagem(url, _sessao(request, *QUEM_EMITE_E_RETIFICA))


@estado(
    "O-16",
    tela="ocupacao",
    papel="quem emite",
    prova="Desfazer esta declaração",
)
def declaracao_desfazivel(request):
    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _declarar(cliente, certame)
    cliente.get(url)
    return Montagem(url, cliente)


@estado("O-17", tela="ocupacao", papel="quem emite", prova="Esta declaração não se desfaz agora")
def declaracao_que_nao_se_desfaz(request):
    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _declarar(cliente, certame)
    cliente.get(url)
    _chamada_dependente(request)
    return Montagem(url, cliente)


@estado(
    "O-18",
    tela="ocupacao",
    papel="quem só lê",
    prova="Declarar a vaga não preenchida é ato de quem apura",
)
def vaga_para_quem_nao_apura(request):
    _, url = _silente(request)
    return Montagem(url, _sessao(request, *QUEM_SO_LE))


# ── O retorno de cada gesto ──────────────────────────────────────────────────────────────────────


def _post(cliente, nome, edital, dados, marco=MARCO):
    resposta = cliente.post(reverse(f"interface:{nome}", args=[edital.id, marco]), dados)
    assert resposta.status_code in (200, 302), resposta.status_code
    return resposta


@estado("R-01", tela="ocupacao", papel="quem emite", prova="Apuração emitida")
def apurar_com_sucesso(request):
    edital, _ = _cenario_padrao(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _post(cliente, "emitir-apuracao", edital, {"lista": "", "chave": "piloto-r01"})
    return Montagem(_url(edital), cliente)


@estado("R-02", tela="ocupacao", papel="quem emite", prova="Não foi possível apurar:")
def apurar_recusado(request):
    from tests.fixtures.ocupacao import MODALIDADE_PPI

    edital, _ = _cenario_padrao(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _post(cliente, "emitir-apuracao", edital, {"lista": MODALIDADE_PPI, "chave": "piloto-r02"})
    return Montagem(_url(edital), cliente)


@estado("R-03", tela="ocupacao", papel="quem emite", prova="Faixa seguinte emitida")
def faixa_com_sucesso(request):
    edital, _, _ = cenarios.com_continuacao(*_base(request))
    _apurar(edital, request.getfixturevalue("gestor"), "piloto-r03")
    cliente = _sessao(request, *QUEM_EMITE)
    _post(cliente, "causar-faixa", edital, {"lista": "", "chave": "piloto-r03-faixa"})
    return Montagem(_url(edital), cliente)


@estado("R-04", tela="ocupacao", papel="quem emite", prova="Não foi possível apurar:")
def faixa_recusada(request):
    edital, _ = _cenario_padrao(request)
    _apurar(edital, request.getfixturevalue("gestor"), "piloto-r04")
    cliente = _sessao(request, *QUEM_EMITE)
    _post(cliente, "causar-faixa", edital, {"lista": "", "chave": "piloto-r04-faixa"})
    return Montagem(_url(edital), cliente)


@estado("R-05", tela="ocupacao", papel="quem emite", prova="Vaga acrescida: 1 vaga.")
def acrescimo_com_sucesso(request):
    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    _acrescentar(cliente, edital)
    return Montagem(_url(edital), cliente)


@estado("R-06", tela="ocupacao", papel="quem emite", prova="Não foi possível acrescentar a vaga:")
def acrescimo_recusado(request):
    from tests.interface.test_acrescimo import conferir

    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    conferir(cliente, edital, origem="")
    return Montagem(_url(edital), cliente)


@estado("R-07", tela="ocupacao", papel="quem emite", prova="Vaga acrescida desfeita: 1 vaga.")
def desfazimento_com_sucesso(request):
    from tests.interface.test_acrescimo import assinatura_de, desfazer

    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    acrescimo = _acrescentar(cliente, edital)
    cliente.get(_url(edital))
    pagina = desfazer(cliente, edital, acrescimo).content.decode()
    desfazer(
        cliente,
        edital,
        acrescimo,
        confirmar="1",
        motivo="Matrícula efetivada no Edital regular",
        leitura=assinatura_de(pagina),
    )
    return Montagem(_url(edital), cliente)


@estado(
    "R-08",
    tela="ocupacao",
    papel="quem emite",
    prova="Não foi possível desfazer a vaga acrescida:",
)
def desfazimento_recusado(request):
    from tests.fixtures.convocacao import convocar
    from tests.interface.test_acrescimo import desfazer

    edital, inscricoes = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    acrescimo = _acrescentar(cliente, edital)
    cliente.get(_url(edital))
    convocar(
        edital, request.getfixturevalue("gestor"), inscricoes[0], idempotency_key="piloto-r08"
    )
    desfazer(cliente, edital, acrescimo)
    return Montagem(_url(edital), cliente)


@estado("R-09", tela="ocupacao", papel="quem emite", prova="Vaga declarada não preenchida: 1 vaga.")
def declaracao_com_sucesso(request):
    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _declarar(cliente, certame)
    return Montagem(url, cliente)


@estado(
    "R-10",
    tela="ocupacao",
    papel="quem emite",
    prova="Não foi possível declarar a vaga não preenchida:",
)
def declaracao_recusada(request):
    from tests.fixtures.sorteio import MARCO as MARCO_DO_SORTEIO
    from tests.interface.test_destinacao_na_ocupacao import declarar_pela_tela

    certame = cenarios.reversao_que_nao_sai(*_base(request))
    cenarios.encerrar_o_prazo(request.getfixturevalue("monkeypatch"))
    cliente = _sessao(request, *QUEM_EMITE)
    declarar_pela_tela(cliente, certame)
    return Montagem(_url(certame["edital"], MARCO_DO_SORTEIO), cliente)


def _desfazer_declaracao(cliente, certame, declaracao, **extra):
    from tests.fixtures.sorteio import MARCO as MARCO_DO_SORTEIO

    return cliente.post(
        reverse("interface:desfazer-nao-preenchida", args=[certame["edital"].id, MARCO_DO_SORTEIO]),
        {"ato": str(declaracao.id), "chave": "piloto-desfazer-np", **extra},
    )


@estado(
    "R-11",
    tela="ocupacao",
    papel="quem emite",
    prova="Declaração de vaga não preenchida desfeita",
)
def desfazer_declaracao_com_sucesso(request):
    from tests.interface.test_destinacao_na_ocupacao import assinatura_de

    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    declaracao = _declarar(cliente, certame)
    cliente.get(url)
    conferencia = _desfazer_declaracao(cliente, certame, declaracao).content.decode()
    _desfazer_declaracao(
        cliente,
        certame,
        declaracao,
        confirmar="1",
        leitura=assinatura_de(conferencia),
        motivo="Declarada por engano.",
    )
    return Montagem(url, cliente)


@estado(
    "R-12",
    tela="ocupacao",
    papel="quem emite",
    prova="Não foi possível desfazer a declaração de vaga não preenchida:",
)
def desfazer_declaracao_recusado(request):
    from processo_seletivo.ocupacao.application import destinacao

    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    declaracao = _declarar(cliente, certame)
    cliente.get(url)
    dependentes = _chamada_dependente(request)
    leitura = destinacao.previa_do_desfazimento_da_nao_preenchida(
        edital=certame["edital"],
        declaracao_id=str(declaracao.id),
        chamadas_dependentes=dependentes,
    )["assinatura"]
    _desfazer_declaracao(
        cliente,
        certame,
        declaracao,
        confirmar="1",
        leitura=leitura,
        motivo="Declarada por engano.",
    )
    return Montagem(url, cliente)
