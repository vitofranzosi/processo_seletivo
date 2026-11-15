"""Os estados das duas conferências da Ocupação (172, D-001, K-01 a K-09).

**A conferência é a resposta de um POST**, e não tem endereço que se abra: a página nasce do clique
em "Conferir o acréscimo", "Conferir o desfazimento", "Declarar a vaga não preenchida" ou "Desfazer
esta declaração". Por isso todo estado daqui abre a Ocupação e chega à conferência pelo gesto, no
navegador, como a pessoa chega.
"""

from tests.fixtures import ocupacao_da_tela as cenarios
from tests.interface.test_acrescimo import FUNDAMENTO, ORIGEM
from tests.navegador.piloto.estados import Montagem, estado
from tests.navegador.piloto.ocupacao import (
    QUEM_EMITE,
    _acrescentar,
    _apurar,
    _base,
    _chamada_dependente,
    _declarar,
    _sessao,
    _silente,
    _url,
)


def _preencher_o_acrescimo(pagina, quantidade=1, referencia=None):
    pagina.fill("#quantidade-1", str(quantidade))
    pagina.fill("#origem-1", ORIGEM)
    pagina.fill("#fundamento-1", FUNDAMENTO)
    if referencia:
        pagina.fill("#referencia-1", referencia)
    pagina.get_by_role("button", name="Conferir o acréscimo").click()
    pagina.wait_for_load_state("networkidle")


@estado(
    "K-01",
    tela="conferencia-acrescimo",
    papel="quem emite",
    prova="Conferir o acréscimo de 1 vaga",
    acao_principal="Acrescentar 1 vaga",
)
def conferir_o_acrescimo(request):
    edital, _ = cenarios.reserva(*_base(request))
    return Montagem(
        _url(edital),
        _sessao(request, *QUEM_EMITE),
        gesto=lambda p: _preencher_o_acrescimo(p, referencia="Processo 23147.000123/2026-11"),
    )


@estado(
    "K-02",
    tela="conferencia-acrescimo",
    papel="quem emite",
    prova="a ordem publicada alcança só",
)
def conferir_mais_vagas_que_a_faixa(request):
    edital, _ = cenarios.reserva(*_base(request))
    return Montagem(
        _url(edital), _sessao(request, *QUEM_EMITE), gesto=lambda p: _preencher_o_acrescimo(p, 3)
    )


@estado(
    "K-03",
    tela="conferencia-acrescimo",
    papel="quem emite",
    prova="já está obsoleta por outra causa",
)
def conferir_com_apuracao_obsoleta(request):
    import uuid

    from django.utils import timezone

    from processo_seletivo.ocupacao.domain import nomes
    from processo_seletivo.ocupacao.models import EfeitoDeOcupacao
    from tests.fixtures.corte import MARCO
    from tests.fixtures.edital import PROFILE_ID

    gestor = request.getfixturevalue("gestor")
    edital, inscricoes = cenarios.reserva(*_base(request))
    _apurar(edital, gestor, "piloto-k03")
    EfeitoDeOcupacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        inscricao_id=inscricoes[0].id,
        especie=nomes.EFEITO_EXCLUSAO,
        fundamento="Desfecho registrado",
        ato_de_origem_id=uuid.uuid4(),
        rotulo_da_origem="piloto",
        registrado_por="piloto",
        registrado_em=timezone.now(),
    )
    return Montagem(_url(edital), _sessao(request, *QUEM_EMITE), gesto=_preencher_o_acrescimo)


def _clicar(nome):
    def gesto(pagina):
        pagina.get_by_role("button", name=nome).first.click()
        pagina.wait_for_load_state("networkidle")

    return gesto


@estado(
    "K-04",
    tela="conferencia-acrescimo",
    papel="quem emite",
    prova="Desfazer 1 vaga do acréscimo de",
    acao_principal="Desfazer 1 vaga",
)
def conferir_o_desfazimento(request):
    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)
    _acrescentar(cliente, edital)
    cliente.get(_url(edital))
    return Montagem(_url(edital), cliente, gesto=_clicar("Conferir o desfazimento"))


@estado(
    "K-05",
    tela="conferencia-acrescimo",
    papel="quem emite",
    prova="mudaram desde que a conferência foi aberta",
)
def recusa_na_conferencia_do_acrescimo(request):
    from tests.interface.test_acrescimo import conferir, confirmar

    edital, _ = cenarios.reserva(*_base(request))
    cliente = _sessao(request, *QUEM_EMITE)

    def leitura_mudada(pagina):
        # A pessoa abre a conferência; enquanto ela lê, outra confirma um acréscimo no mesmo recorte;
        # quando ela confirma, a leitura que assinou não é mais a de agora.
        _preencher_o_acrescimo(pagina)
        nova = conferir(cliente, edital, chave="piloto-k05-outro").content.decode()
        confirmar(cliente, edital, nova)
        pagina.get_by_role("button", name="Acrescentar 1 vaga").click()
        pagina.wait_for_load_state("networkidle")

    return Montagem(_url(edital), cliente, gesto=leitura_mudada)


@estado(
    "K-06",
    tela="conferencia-nao-preenchida",
    papel="quem emite",
    prova="Conferir a declaração de 1 vaga não preenchida",
    acao_principal="Declarar 1 vaga não preenchida",
)
def conferir_a_declaracao(request):
    _, url = _silente(request)
    return Montagem(
        url, _sessao(request, *QUEM_EMITE), gesto=_clicar("Declarar a vaga não preenchida")
    )


@estado(
    "K-07",
    tela="conferencia-nao-preenchida",
    papel="quem emite",
    prova="Desfazer a declaração de 1 vaga não preenchida",
    acao_principal="Desfazer a declaração",
)
def conferir_o_desfazimento_da_declaracao(request):
    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _declarar(cliente, certame)
    cliente.get(url)
    return Montagem(url, cliente, gesto=_clicar("Desfazer esta declaração"))


@estado(
    "K-08",
    tela="conferencia-nao-preenchida",
    papel="quem emite",
    prova="O desfazimento não cabe agora",
)
def desfazimento_que_nao_cabe(request):
    certame, url = _silente(request)
    cliente = _sessao(request, *QUEM_EMITE)
    _declarar(cliente, certame)
    cliente.get(url)

    def chamada_no_meio(pagina):
        # A tela foi aberta antes da chamada; a pessoa clica depois dela, e a conferência diz que o
        # desfazimento não cabe mais.
        _chamada_dependente(request)
        _clicar("Desfazer esta declaração")(pagina)

    return Montagem(url, cliente, gesto=chamada_no_meio)


@estado(
    "K-09",
    tela="conferencia-nao-preenchida",
    papel="quem emite",
    prova="exige fundamento escrito",
)
def recusa_na_conferencia_da_declaracao(request):
    _, url = _silente(request)

    def fundamento_em_branco(pagina):
        _clicar("Declarar a vaga não preenchida")(pagina)
        pagina.fill("#fundamento", "   ")
        pagina.get_by_role("button", name="Declarar 1 vaga não preenchida").click()
        pagina.wait_for_load_state("networkidle")

    return Montagem(url, _sessao(request, *QUEM_EMITE), gesto=fundamento_em_branco)
