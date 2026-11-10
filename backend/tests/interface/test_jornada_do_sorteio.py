"""A tela do sorteio como a jornada de quem o conduz (142), contra PostgreSQL.

Um certame com três listas — a ampla com seis pessoas, a PPI com uma e a PcD com nenhuma —
percorrido pela tela, na ordem das regras: nada fixado, a ampla fixada, todas fixadas, a semente
obtida, uma lista sorteada, as duas sorteadas. Em cada estado, o que a tela diz dos quatro passos,
o que ela oferece, e se diz o mesmo que o Centro. E os casos à parte: a operação recusada e quem
só lê.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, METODO, certame_com_cotas, presidente
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    # A PcD sem inscrito: o Polo Vitória do Edital 35 numa lista só (126). É a lista que não se
    # aplica (cenário 9).
    return certame_com_cotas(
        gestor, api_client, manager_headers, process_payload, modalidades={0: LISTA_PPI}
    )


def _url(certame, nome="interface:sorteio"):
    return reverse(nome, args=[certame["edital"].id, certame["marco"]])


def _abrir(client, certame, subject="maria", papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(_url(certame))
    assert resposta.status_code == 200
    return resposta.content.decode()


def _fixar(client, certame, lista):
    identificar(client, "maria", [])
    return client.post(
        _url(certame, "interface:publicar-relacao-do-sorteio"),
        {"lista_id": lista, "chave_idempotencia": f"jornada-142-{lista or 'ampla'}"},
        follow=True,
    )


def _observar(certame):
    observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="jornada-142-semente",
        correlation_id="teste-142",
        fonte_externa=FonteDeTeste(),
    )


def _sortear(client, certame, lista):
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados

    identificar(client, "maria", [])
    return client.post(
        _url(certame, "interface:realizar-sorteio"),
        {
            "chave_idempotencia": f"jornada-142-sorteio-{lista or 'ampla'}",
            "relacao_id": RelacaoDeHabilitados.objects.get(lista_id=lista or None).id,
            "ocorrencia_id": OcorrenciaDaFonte.objects.get().id,
        },
        follow=True,
    )


def _cartoes(corpo):
    """`[(classes do cartão, HTML do cartão)]` da navegação dos passos."""
    nav = corpo.split('<nav class="passos-do-sorteio"', 1)[1].split("</nav>", 1)[0]
    return re.findall(
        r'<li class="(passo[^"]*)">(.*?)</li>\s*(?=<li class="passo|</ol>)', nav, re.S
    )


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _passos(corpo):
    """`[(classes do cartão, texto do cartão)]`."""
    return [(classes, _texto(html)) for classes, html in _cartoes(corpo)]


def _bloco(corpo, ident):
    """O elemento de id `ident`, até o próximo bloco do mesmo nível."""
    inicio = corpo.index(f'id="{ident}"')
    resto = corpo[inicio:]
    fim = min(
        (
            i
            for marca in ("<article", '<div class="execucao"', "</section>")
            if (i := resto.find(marca, 1)) > 0
        ),
        default=len(resto),
    )
    return resto[:fim]


def _formularios(corpo):
    return re.findall(r'<form method="post" action="[^"]*/sorteio/(\w+)"', corpo)


# --- 1 · nada preparado ---------------------------------------------------------------------------


def test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora(certame, client):
    """US1, cenário 1 (FR-4900, FR-4904, FR-4910, SC-1540, SC-1546)."""
    corpo = _abrir(client, certame)
    passos = _passos(corpo)

    nomes = [
        _texto(re.search(r'<p class="passo-nome">(.*?)</a>', html, re.S).group(1))
        for _, html in _cartoes(corpo)
    ]
    assert nomes == [
        "1 Fixar os participantes",
        "2 Obter a semente pública",
        "3 Realizar o sorteio",
        "4 Consultar a ordem sorteada",
    ]
    assert [("passo-agora" in classes) for classes, _ in passos] == [True, False, False, False]
    assert "0 de 2 listas fixadas" in passos[0][1]

    # As seções seguem a ordem do trabalho, e o método não está na frente de nada.
    ordem = [
        corpo.index(f'id="{i}"')
        for i in ("titulo-recortes", "titulo-ocorrencia", "titulo-execucao", "titulo-resultado")
    ]
    assert ordem == sorted(ordem)
    assert corpo.index("<summary>Método declarado no Edital</summary>") > corpo.index(
        'id="titulo-ocorrencia"'
    )

    # Fixar vem antes de observar, na página e no teclado; observar perde peso, e não some.
    assert corpo.index("/sorteio/relacao") < corpo.index("/sorteio/ocorrencia")
    assert 'class="botao secundario">Observar a ocorrência' in corpo
    assert "Nenhum corte emitido" not in corpo


def test_a_conferencia_vem_no_cartao_antes_do_botao(certame, client):
    """US2 (FR-4908): a lista, quantas pessoas, a numeração, a consequência e o passo seguinte."""
    corpo = _abrir(client, certame)
    ampla = _bloco(corpo, "recorte-ampla")

    conferencia = ampla.index("Confira antes de fixar.")
    assert "participam <strong>6 pessoas</strong>" in " ".join(ampla.split())
    assert "não muda mais" in ampla and "obter a semente pública" in ampla
    assert (
        conferencia < ampla.index("<table>") < ampla.index("Fixar os 6 participantes desta lista")
    )


# --- 2 e 9 · uma fixada, outra pendente, e a lista vazia ---------------------------------------


def test_a_ampla_fixada_e_a_ppi_pendente(certame, client):
    """US1, cenário 2; US2, cenário 3 (FR-4905, FR-4909, FR-4916)."""
    resposta = _fixar(client, certame, "")
    retorno = resposta.content.decode()
    # A mensagem do ato e o "Próximo nesta lista" continuam no alto, antes dos passos.
    assert retorno.index("Relação publicada e congelada") < retorno.index(
        '<nav class="passos-do-sorteio"'
    )
    assert retorno.index('class="proximo-nesta-lista"') < retorno.index(
        '<nav class="passos-do-sorteio"'
    )

    corpo = _abrir(client, certame)
    passos = _passos(corpo)
    assert "1 de 2 listas fixadas" in passos[0][1]
    assert "passo-agora" in passos[0][0]
    assert "✓ Feito Todos os inscritos" in passos[0][1]
    assert "● Pendente Pretos, pardos e indígenas" in passos[0][1]
    assert "— Não se aplica Pessoas com deficiência" in passos[0][1]
    # A semente disponível, sem bloqueio e sem frase nova (FR-4909): o formulário de antes.
    assert "● Pendente" in passos[1][1]
    assert _formularios(corpo).count("ocorrencia") == 1
    assert 'class="botao secundario">Observar a ocorrência' in corpo

    # O cartão da ampla fixada: o registro, e a tabela recolhida (D-007).
    ampla = _bloco(corpo, "recorte-ampla")
    assert "relação congelada em" in ampla
    assert "<summary>Ver os 6 participantes fixados" in ampla
    # A PcD: não se aplica, com a razão, e sem botão (cenário 9).
    pcd = _bloco(corpo, f"recorte-{LISTA_PCD}")
    assert "Não se aplica" in pcd and "Nenhuma inscrição submetida declarou esta lista" in pcd
    assert "<form" not in pcd


# --- 3 e 4 · todas fixadas, semente por obter -----------------------------------------------------


def test_todas_fixadas_a_semente_e_a_vez(certame, client):
    _fixar(client, certame, "")
    _fixar(client, certame, LISTA_PPI)

    corpo = _abrir(client, certame)
    passos = _passos(corpo)

    assert "✓ Feito 2 de 2 listas fixadas" in passos[0][1]
    assert [("passo-agora" in classes) for classes, _ in passos] == [False, True, False, False]
    assert 'class="botao">Observar a ocorrência' in corpo
    assert "/sorteio/realizar" not in corpo


# --- 5 · semente observada --------------------------------------------------------------------


def test_com_a_semente_o_sorteio_e_a_vez_e_a_semente_aparece_uma_vez(certame, client):
    """US3, cenário 2 (FR-4906, FR-4911)."""
    _fixar(client, certame, "")
    _fixar(client, certame, LISTA_PPI)
    _observar(certame)

    corpo = _abrir(client, certame)
    passos = _passos(corpo)

    assert "✓ Feito" in passos[1][1]
    assert passos[1][1].count("Uma só, para as 3 listas do marco.") == 1
    assert "passo-agora" in passos[2][0]
    assert corpo.count("Material bruto observado") == 1
    # Um botão de sortear em cada lista com participantes, cada um na execução dela.
    assert _formularios(corpo).count("realizar") == 2
    assert "/sorteio/realizar" in _bloco(corpo, "sorteio-ampla")
    assert "/sorteio/realizar" in _bloco(corpo, f"sorteio-{LISTA_PPI}")
    assert "/sorteio/realizar" not in _bloco(corpo, f"sorteio-{LISTA_PCD}")


# --- 6 e 7 · uma sorteada e outra não; as duas ------------------------------------------------


def test_uma_sorteada_e_a_outra_nao(certame, client):
    """US3, cenário 1; US4 (FR-4911 a FR-4914, SC-1543, SC-1544)."""
    _fixar(client, certame, "")
    _fixar(client, certame, LISTA_PPI)
    _observar(certame)

    retorno = _sortear(client, certame, "").content.decode()
    # A ordem da lista que acabou de ser sorteada aparece aberta, com as seis posições, na ordem.
    ordem = _bloco(retorno, "ordem-ampla")
    assert '<details class="ordem-sorteada" open>' in ordem
    assert "Ver a ordem sorteada — 6 posições" in ordem
    assert re.findall(r"<td>(\d+)º</td>", ordem) == [str(n) for n in range(1, 7)]

    corpo = _abrir(client, certame)
    passos = _passos(corpo)
    assert "1 de 2 listas sorteadas" in passos[2][1]
    assert "passo-agora" in passos[2][0]
    assert "1 de 2 listas com ordem gravada" in passos[3][1]
    assert _formularios(corpo).count("realizar") == 1
    assert "/sorteio/realizar" in _bloco(corpo, f"sorteio-{LISTA_PPI}")
    assert "Anular este sorteio" in _bloco(corpo, "sorteio-ampla")

    # Não divulgada, e a tela não sugere o contrário (FR-4913, SC-1544).
    assert "Ainda não foi divulgada como resultado" in _bloco(corpo, "ordem-ampla")
    assert "Divulgada como" not in corpo
    # Sem corte antes do sorteio da lista (SC-1546), e a PPI ainda sem ordem.
    assert "Nenhum corte emitido" not in corpo
    assert "ainda sem sorteio — a ordem aparece aqui depois dele" in corpo


def test_o_sorteio_concluido(certame, client):
    """Cenário 7: nenhum passo da tela é a tarefa de agora, e as duas ordens estão à vista."""
    _fixar(client, certame, "")
    _fixar(client, certame, LISTA_PPI)
    _observar(certame)
    _sortear(client, certame, "")
    _sortear(client, certame, LISTA_PPI)

    corpo = _abrir(client, certame)
    passos = _passos(corpo)

    assert "✓ Feito 2 de 2 listas sorteadas" in passos[2][1]
    assert not any("passo-agora" in classes for classes, _ in passos)
    assert "Ver a ordem sorteada — 6 posições" in corpo
    assert "Ver a ordem sorteada — 1 posição" in corpo
    assert "/sorteio/realizar" not in corpo


# --- 8 · a operação recusada --------------------------------------------------------------------


def test_fixar_a_lista_vazia_por_formulario_forjado_e_recusado_como_antes(certame, client):
    """Cenário 8: a tela não oferece fixar a PcD, que não tem ninguém; o formulário forjado é
    recusado pelo serviço, e a tela diz por quê. A jornada não autoriza nada (FR-4903)."""
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados

    corpo = _fixar(client, certame, LISTA_PCD).content.decode()

    assert "Não foi possível publicar a relação" in corpo
    assert not RelacaoDeHabilitados.objects.exists()
    assert "<form" not in _bloco(corpo, f"recorte-{LISTA_PCD}")
    assert "passo-agora" in _cartoes(corpo)[0][0], "nada mudou: fixar continua a tarefa de agora"


# --- 10 · quem só lê ----------------------------------------------------------------------------


def test_a_auditoria_ve_os_passos_sem_controle_e_sem_tarefa_de_agora(certame, client):
    """US5 (FR-4917)."""
    _fixar(client, certame, "")
    corpo = _abrir(client, certame, "auditoria-142", ["auditor"])
    passos = _passos(corpo)

    assert len(passos) == 4
    assert "1 de 2 listas fixadas" in passos[0][1]
    assert not any("passo-agora" in classes for classes, _ in passos)
    assert _formularios(corpo) == []
    assert "Conduzir o sorteio deste marco" in corpo


# --- a coerência com o Centro --------------------------------------------------------------------


def test_a_tela_diz_o_mesmo_que_o_centro_e_a_providencia_chega_a_execucao(certame, client):
    """SC-1541, FR-4902, FR-4915: a derivação do Edital inteiro, a do Centro, diz de cada lista o
    que a tela diz; a providência do sorteio leva à execução da lista, e a da relação, ao cartão."""
    _fixar(client, certame, "")
    _observar(certame)

    corpo = _abrir(client, certame)
    cartoes = _cartoes(corpo)
    [perfil] = a.do_edital(certame["edital"], presidente()).perfis
    pontos = {
        p.tipo: p for p in perfil.pontos if p.marco and p.tipo in (a.RELACAO, a.SEMENTE, a.SORTEIO)
    }
    for numero, tipo in ((0, a.RELACAO), (2, a.SORTEIO)):
        do_centro = sorted(pontos[tipo].celula(lista).situacao for lista, _ in perfil.listas)
        listas = cartoes[numero][1].split('<ul class="passo-listas">', 1)[1]
        da_tela = sorted(re.findall(r'class="situacao-do-andamento s-(\w+)"', listas))
        assert da_tela == do_centro, (tipo, da_tela, do_centro)
    semente = pontos[a.SEMENTE].celula(None)
    assert f"s-{semente.situacao}" in cartoes[1][1]

    sortear = pontos[a.SORTEIO].celula(None)
    assert sortear.situacao == a.PENDENTE
    assert sortear.url.endswith("#sorteio-ampla"), sortear.url
    assert 'id="sorteio-ampla"' in corpo
    fixar_ppi = pontos[a.RELACAO].celula(LISTA_PPI)
    assert fixar_ppi.url.endswith(f"#recorte-{LISTA_PPI}"), fixar_ppi.url
    assert f'id="recorte-{LISTA_PPI}"' in corpo


# --- regressões da revisão do PR #452 ----------------------------------------------------------


def test_depois_de_sortear_a_cota_a_mensagem_e_a_abertura_sao_da_cota(certame, client):
    """Achado 1: o desfecho do sorteio não trazia a lista, e a tela lia a ampla — "Ver a ordem
    sorteada" apontava para a ordem da ampla, e era ela que abria."""
    from processo_seletivo.interface.views import _com_a_lista_da_relacao
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados

    _fixar(client, certame, "")
    _fixar(client, certame, LISTA_PPI)
    _observar(certame)
    _sortear(client, certame, "")

    retorno = _sortear(client, certame, LISTA_PPI).content.decode()
    ancora = a.ancora_da_ordem(LISTA_PPI)

    mensagem = retorno.split('<p class="sucesso"', 1)[1].split("</p>", 1)[0]
    assert f'href="#{ancora}"' in mensagem
    assert '<details class="ordem-sorteada" open>' in _bloco(retorno, ancora)
    assert '<details class="ordem-sorteada" open>' not in _bloco(retorno, a.ancora_da_ordem(""))
    # E o "Próximo nesta lista" é o da cota, que não tem mais nada a sortear: nada diz "realizar
    # o sorteio" da ampla, que já foi feito.
    proximo = retorno.split('class="proximo-nesta-lista"', 1)[1].split("</p>", 1)[0]
    assert "Realizar o sorteio" not in proximo

    # A anulação usa o mesmo caminho: a lista vem da relação que o comando gravou.
    ppi = RelacaoDeHabilitados.objects.get(lista_id=LISTA_PPI)
    assert _com_a_lista_da_relacao({"relacao": str(ppi.id)})["listaId"] == LISTA_PPI
    ampla = RelacaoDeHabilitados.objects.get(lista_id=None)
    assert _com_a_lista_da_relacao({"relacao": str(ampla.id)})["listaId"] == ""


def test_com_fixar_como_a_vez_sortear_e_secundario_e_o_texto_fala_dos_numeros(certame, client):
    """Achados 4, 5 e 6: a ampla fixada e a semente obtida, a PPI por fixar. Fixar é a tarefa de
    agora; o botão de sortear a ampla existe, como antes, e é ação secundária; antes do ato a tela
    fala dos números observados, e não da semente; e o passo seguinte a fixar a PPI é sortear."""
    _fixar(client, certame, "")
    _observar(certame)

    corpo = _abrir(client, certame)
    cartoes = _cartoes(corpo)
    assert "passo-agora" in cartoes[0][0], "a PPI por fixar"

    execucao = _bloco(corpo, "sorteio-ampla")
    assert 'class="botao secundario">Realizar o sorteio desta lista' in execucao
    texto = " ".join(execucao.split())
    assert "a partir dos números observados na fonte" in texto
    assert "com a semente" not in texto

    ppi = " ".join(_bloco(corpo, f"recorte-{LISTA_PPI}").split())
    assert "Depois de fixar: realizar o sorteio desta lista" in ppi
    assert "obter a semente pública" not in ppi


def test_com_tudo_fixado_sortear_volta_a_ser_o_botao_principal(certame, client):
    """Achado 4, a contraprova: sem lista a fixar, o botão de sortear é o da tarefa de agora."""
    _fixar(client, certame, "")
    _fixar(client, certame, LISTA_PPI)
    _observar(certame)

    corpo = _abrir(client, certame)
    assert corpo.count('class="botao">Realizar o sorteio desta lista') == 2
    assert 'class="botao secundario">Realizar o sorteio' not in corpo
