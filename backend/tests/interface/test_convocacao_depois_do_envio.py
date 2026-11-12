"""A convocação depois do envio, nas telas do candidato (154, US1).

Requisitos: FR-6200 a FR-6203 e FR-6208 a FR-6210.

O achado 20 do estudo da jornada final: com tudo enviado, o topo da convocação dizia *"Você foi
convocado!"* e advertia que a comissão poderia registrar o não atendimento. Estes casos leem as duas
telas — a convocação e o acompanhamento — em cada cenário da tabela de `data-model.md`, contando a
advertência: **zero** sem providência, **exatamente uma** com ela.

**A página da convocação sem documento nunca teve a advertência** (D-007 da `154`): nela, o parcial
da chamada só a põe com a projeção das obrigações, que essa chamada não tem. Fica como hoje, e a
advertência dessa chamada mora só no acompanhamento.

Os cenários são os de `tests/fixtures/jornada_do_convocado.py`: **T** é o `E` (tudo enviado, nada
conferido) e **Tc** é o `H` (todo obrigatório conferido); os casos-limite da `154` foram
acrescentados lá.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.portal import obrigacoes, situacao
from tests.interface.test_portal_convocacao import entrar_como

ADVERTENCIA = situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO
CONVOCADO = "Você foi convocado!"
ACOMPANHE = "Acompanhe sua convocação"


@pytest.fixture
def fx(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    from tests.fixtures import jornada_do_convocado as jornada

    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


def _montar(fx, letra):
    from tests.fixtures import jornada_do_convocado as jornada

    return jornada.montar(letra, fx)


def _main(client, cenario, rota):
    with cenario.relogio():
        entrar_como(client, cenario.pessoa)
        resposta = client.get(reverse(rota, args=[cenario.pessoa.id]))
    assert resposta.status_code == 200
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.S).group(1)


def _texto(html):
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def _titulo(pagina):
    return _texto(re.search(r'<h1 id="titulo-da-chamada">(.*?)</h1>', pagina, re.S).group(1))


def _situacao(pagina):
    """A seção *Sua situação* do acompanhamento, onde mora a ação da convocação."""
    return re.search(r'<section class="situacao-da-inscricao".*?</section>', pagina, re.S).group(0)


# (cenário, título, advertências na convocação, advertências no acompanhamento)
CENARIOS = [
    # Com providência pendente: o título de hoje e a advertência uma vez em cada tela.
    ("C1", CONVOCADO, 1, 1),
    ("F", CONVOCADO, 1, 1),
    ("T-pendencia-nova", CONVOCADO, 1, 1),
    # Sem providência: o título novo e nenhuma advertência (SC-2000).
    ("E", ACOMPANHE, 0, 0),
    ("H", ACOMPANHE, 0, 0),
    ("L", ACOMPANHE, 0, 0),
    ("so-facultativo", ACOMPANHE, 0, 0),
    ("T-sem-vencimento", ACOMPANHE, 0, 0),
    ("T-prazo-nao-iniciado", ACOMPANHE, 0, 0),
    # Sem documento (D-006, D-007): a página da convocação nunca teve a advertência.
    ("B", CONVOCADO, 0, 1),
    ("B2", ACOMPANHE, 0, 0),
    ("sem-documento-nem-requerimento", CONVOCADO, 0, 1),
    # Controle: com providência, mas o prazo não começou — nenhuma advertência, como hoje.
    ("K", CONVOCADO, 0, 0),
]


@pytest.mark.parametrize(("letra", "titulo", "na_convocacao", "no_acompanhamento"), CENARIOS)
def test_o_titulo_e_a_advertencia_seguem_a_providencia(
    client, fx, letra, titulo, na_convocacao, no_acompanhamento
):
    """FR-6202, FR-6209, SC-2000, SC-2001 e D-007."""
    cenario = _montar(fx, letra)

    convocacao = _main(client, cenario, "portal:convocacao")
    acompanhamento = _main(client, cenario, "portal:acompanhamento")

    assert _titulo(convocacao) == titulo
    assert _texto(convocacao).count(ADVERTENCIA) == na_convocacao
    assert _texto(_situacao(acompanhamento)).count(ADVERTENCIA) == no_acompanhamento


@pytest.mark.parametrize("letra", ["C1", "E", "H", "L", "so-facultativo", "B2"])
def test_o_prazo_continua_com_e_sem_providencia(client, fx, letra):
    """FR-6208, SC-2002: o cartão do prazo na convocação e o prazo no acompanhamento."""
    cenario = _montar(fx, letra)

    convocacao = _main(client, cenario, "portal:convocacao")
    acompanhamento = _main(client, cenario, "portal:acompanhamento")

    assert 'class="data-do-prazo"' in convocacao
    assert "Prazo desta convocação:" in _texto(_situacao(acompanhamento))


@pytest.mark.parametrize("letra", ["C1", "E", "H"])
def test_a_ressalva_continua_com_e_sem_providencia(client, fx, letra):
    """FR-6210: a ressalva não é frase de consequência."""
    pagina = _main(client, _montar(fx, letra), "portal:convocacao")

    assert 'class="ressalva"' in pagina


def test_t_le_acompanhar_o_prazo_a_conclusao_e_nenhuma_acao(client, fx):
    """Cenário 1 da US1, sobre o `E`: a captura `B08-tudo-enviado` do estudo, refeita."""
    pagina = _main(client, _montar(fx, "E"), "portal:convocacao")
    texto = _texto(pagina)

    assert _titulo(pagina) == ACOMPANHE
    assert 'class="data-do-prazo"' in pagina
    assert obrigacoes.FRASE_DE_CONCLUSAO in texto
    assert 'class="acao-da-chamada"' not in pagina, "sem tarefa, nenhuma ação principal"
    assert ADVERTENCIA not in texto


def test_t_no_acompanhamento_nada_por_enquanto_e_a_conclusao(client, fx):
    """Cenário 2 da US1: *"Nada por enquanto."*, a frase de conclusão, o prazo, sem advertência."""
    texto = _texto(_situacao(_main(client, _montar(fx, "E"), "portal:acompanhamento")))

    assert f"{situacao.NADA_POR_ENQUANTO} {obrigacoes.FRASE_DE_CONCLUSAO}" in texto
    assert "Prazo desta convocação:" in texto
    assert ADVERTENCIA not in texto


def test_so_facultativo_le_a_conclusao_e_a_linha_do_opcional(client, fx):
    """Caso-limite *chamada só com documento facultativo, nada enviado*."""
    texto = _texto(_main(client, _montar(fx, "so-facultativo"), "portal:convocacao"))

    assert obrigacoes.FRASE_DE_CONCLUSAO in texto
    assert "Se quiser, você ainda pode enviar o documento opcional" in texto


@pytest.mark.parametrize(
    ("letra", "frase"),
    [
        ("T-prazo-nao-iniciado", "O prazo ainda não começou a correr"),
        ("T-sem-vencimento", obrigacoes.SEM_PRAZO_REGISTRADO),
    ],
)
def test_sem_prazo_correndo_o_cartao_diz_so_a_frase_do_caso(client, fx, letra, frase):
    """Casos-limite *prazo não iniciado* e *sem vencimento*, com tudo enviado."""
    pagina = _main(client, _montar(fx, letra), "portal:convocacao")
    cartao = re.search(r'<div class="cartao-do-prazo">(.*?)</div>', pagina, re.S).group(1)

    assert _titulo(pagina) == ACOMPANHE
    assert frase in _texto(cartao)
    assert 'class="data-do-prazo"' not in cartao


def test_o_envio_que_tira_a_ultima_tarefa_volta_com_o_titulo_novo(client, fx):
    """FR-6203: a volta da confirmação (FR-3870 da `121`) já lê a projeção depois do envio."""
    from tests.fixtures import documentos_da_convocacao as cenarios
    from tests.fixtures.documentos_da_convocacao import RESIDENCIA

    cenario = _montar(fx, "T-menos-um")
    antes = _main(client, cenario, "portal:convocacao")
    assert _titulo(antes) == CONVOCADO
    assert _texto(antes).count(ADVERTENCIA) == 1

    alvo = cenarios.item(cenario.convocacao, RESIDENCIA)
    resposta = client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[cenario.pessoa.id, alvo.id]),
        {"arquivo": cenarios.pdf(b"t1-residencia")},
    )
    assert resposta.status_code == 302
    assert resposta["Location"].endswith("#confirmacao")

    depois = _main(client, cenario, "portal:convocacao")
    assert _titulo(depois) == ACOMPANHE
    assert "Recebemos: " in _texto(depois)
    assert ADVERTENCIA not in _texto(depois)
