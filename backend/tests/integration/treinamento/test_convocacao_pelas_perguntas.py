"""A convocação e os documentos, pelas perguntas de quem conduz, nos cenários da `134` (143).

**Os cenários são os do estudo de continuidade** (jornadas D e E): o C10, antes de convocar, com a
ampla apurada e a PPP ainda sem ordem — duas listas em estados diferentes —; o C11, com uma pessoa
em cada estado documental; e o C12, com três convocações e nada conferido. Um cenário por caso: a
carga custa perto de um minuto, e dois no mesmo banco colidem.

A distância na dobra se mede no navegador, e está em
`specs/143-convocacao-e-documentos/verificacao.md`.
As regras sem banco estão em `tests/unit/interface/test_conducao_da_convocacao.py`.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.convocacao.application import documentos as servico
from processo_seletivo.ocupacao.application.selectors import apuracao_vigente
from processo_seletivo.processos.models import Edital
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures import documentos_da_convocacao as docs
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, retomar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

PALAVRAS_DE_COMUNICACAO = re.compile(r"candidato (foi )?(avisad|comunicad|notificad)", re.I)


@pytest.fixture
def cenario(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True

    def montar(codigo):
        saida = carregar(codigo, autoridade=str(AUTORIDADE_DA_SUITE))
        assert f"{codigo}  CRIADO" in saida, saida
        manifesto = CenarioDeTreinamento.objects.get(codigo=codigo)
        return Edital.objects.get(processo=manifesto.processo), manifesto

    return montar


def _marco_da_convocacao(edital):
    from processo_seletivo.convocacao.models import Convocacao

    convocacao = Convocacao.objects.filter(edital=edital).first()
    return convocacao.marco_id


def _abrir(client, edital, marco_id, lista=None):
    caminho = reverse("interface:convocacao", args=[edital.id, marco_id])
    resposta = client.get(caminho + (f"?lista={lista}" if lista else ""))
    assert resposta.status_code == 200
    return resposta


def _linha(resposta, nome):
    return next(
        linha
        for linha in resposta.context["leitura"]["linhas"]
        if nome in linha["inscricao"]["nome"]
    )


def _cartao(corpo, convocacao_id):
    inicio = corpo.index(f'id="convocacao-{convocacao_id}"')
    return corpo[inicio : corpo.index("</article>", inicio)]


def _pergunta(corpo, texto):
    """O item do índice com o texto, e o link dele (ou `None`)."""
    indice = corpo.split('<nav class="neste-recorte"', 1)[1].split("</nav>", 1)[0]
    item = next(
        li for li in re.findall(r"<li class=\"pergunta[^>]*>.*?</li>", indice) if texto in li
    )
    return item, re.search(r'<a href="#([^"]+)"><strong>(\d+)</strong>', item)


# ---------------------------------------------------------------------------------------------
# C10 — antes de convocar, com duas listas em estados diferentes
# ---------------------------------------------------------------------------------------------


def test_c10(client, cenario):
    edital, _ = cenario("C10")
    identificar(client, k.PRESIDENCIA, [])
    marco_id, ppp = _marco_e_ppp(edital)

    ampla = _abrir(client, edital, marco_id)
    corpo = ampla.content.decode()
    # FR-5000: o lugar do recorte, fora da migalha.
    assert f"Edital {edital.number}/{edital.year}" in corpo
    assert "Lista <strong>Ampla concorrência" in corpo
    # FR-5001, FR-5002: as perguntas, com o número e o lugar do ato da `140`.
    item, link = _pergunta(corpo, "titulares a convocar")
    assert link and link.group(1) == "titulares" and int(link.group(2)) > 0, item
    assert "com-trabalho" in item
    assert 'id="titulares"' in corpo
    # FR-5005 a FR-5007: os números da apuração, com os mesmos valores, e os das chamadas à parte.
    vigente = apuracao_vigente(
        edital=edital, perfil_id=_perfil(edital), marco_id=marco_id, lista_id=None
    )
    assert f"<li><strong>{vigente.ocupadas}</strong>Consideradas ocupadas na apuração</li>" in corpo
    assert f"<li><strong>{vigente.faltando}</strong>A ocupar na apuração</li>" in corpo
    assert "<li><strong>0</strong>Pessoas convocadas</li>" in corpo
    assert "não quer dizer convocada" in corpo
    # A ordem das áreas: convocar antes de acompanhar, e a fila depois das chamadas (FR-5008).
    assert corpo.index('id="area-convocar"') < corpo.index('id="area-acompanhar"')
    assert corpo.index('id="chamadas"') < corpo.index('id="area-fila"') < corpo.index('id="fila"')

    # A outra lista, noutro estado: a PPP ainda não tem apuração, e não há quem convocar nela.
    reservada = _abrir(client, edital, marco_id, lista=ppp).content.decode()
    assert "Lista <strong>Pessoas pretas, pardas e indígenas" in reservada
    assert "<strong>0</strong> titulares a convocar" in reservada
    assert "a ocupação dele ainda não foi apurada" in reservada
    assert "Não há gesto a praticar agora" in reservada
    assert "não quer dizer convocada" not in reservada
    assert "o gesto está impedido" in reservada

    # Quem não convoca lê que há titulares esperando, por outro papel, e não "nenhum ato" (revisão
    # do #453, achado 3).
    identificar(client, "auditora-143", ["auditor"])
    leitura = _abrir(client, edital, marco_id).content.decode()
    item, link = _pergunta(leitura, "titulares a convocar")
    assert "por quem conduz a convocação" in item and link is None, item
    assert "Nenhum ato a praticar" not in leitura


def _marco_e_ppp(edital):
    from processo_seletivo.interface import conducao_do_marco
    from processo_seletivo.publicacoes.application.selectors import effective_version

    conteudo = effective_version(edital_id=edital.id).content
    [perfil] = conteudo["profiles"]
    marco = perfil["classificationMilestones"][-1]
    recortes = conducao_do_marco.recortes_do_marco(conteudo, perfil)
    ppp = next(lista for lista, rotulo in recortes if lista and "PPP" in rotulo)
    return marco["id"], ppp


def _perfil(edital):
    from processo_seletivo.publicacoes.application.selectors import effective_version

    return effective_version(edital_id=edital.id).content["profiles"][0]["id"]


# ---------------------------------------------------------------------------------------------
# C11 — cada pessoa num estado documental; o aviso nos três momentos
# ---------------------------------------------------------------------------------------------


def test_c11(client, cenario, settings):
    edital, manifesto = cenario("C11")
    identificar(client, k.PRESIDENCIA, [])
    marco_id = _marco_da_convocacao(edital)

    resposta = _abrir(client, edital, marco_id)
    corpo = resposta.content.decode()
    alice, bernardo, cecilia = (
        _linha(resposta, nome)["convocacao"] for nome in ("C11-01", "C11-02", "C11-03")
    )

    # O índice: cada pergunta leva à chamada certa, pela âncora estável (D-003).
    _, link = _pergunta(corpo, "com documento a conferir")
    assert link.group(1) == f"convocacao-{cecilia.id}" and link.group(2) == "1"
    item, link = _pergunta(corpo, "com pendência")
    assert link.group(1) == f"convocacao-{bernardo.id}"
    assert '<a href="#avisar-pendencias">1 pode ser avisada agora</a>' in item
    _, link = _pergunta(corpo, "aguardando o envio dos documentos")
    assert link.group(1) == f"convocacao-{alice.id}"

    # O passo de cada chamada (FR-5011).
    assert "Aguardando o candidato enviar 2 documentos." in _cartao(corpo, alice.id)
    assert "Conferir os documentos</a>" in _cartao(corpo, cecilia.id)

    # Com o envio de avisos desligado — o padrão de produção —, nada oferece o gesto (revisão do
    # #453, achado 1): nem o cartão, nem o índice.
    settings.AVISOS_AOS_CANDIDATOS = False
    desligado = _abrir(client, edital, marco_id).content.decode()
    assert "O envio de avisos está desabilitado" in _cartao(desligado, bernardo.id)
    assert '<a href="#avisar-pendencias">' not in desligado.split('id="avisar-pendencias"')[0]
    settings.AVISOS_AOS_CANDIDATOS = True

    # Momento 1: a pendência registrada, sem aviso (FR-5017, FR-5018).
    cartao = _cartao(corpo, bernardo.id)
    assert "Pendência registrada em" in cartao
    assert "Nenhum aviso desde esta pendência" in cartao
    assert "O aviso pode ser pedido agora." in cartao
    assert '<a href="#avisar-pendencias">' in cartao
    assert not PALAVRAS_DE_COMUNICACAO.search(corpo)

    # Momento 2: o gesto da `134` grava, e não envia.
    chave = re.search(r'name="chave" value="([^"]+)-avisar-pendencias"', corpo).group(1)
    client.post(
        reverse("interface:avisar-pendencias", args=[edital.id, marco_id]),
        {"lista": "", "chave": f"{chave}-avisar-pendencias"},
    )
    cartao = _cartao(_abrir(client, edital, marco_id).content.decode(), bernardo.id)
    assert "Aviso de pendência registrado em" in cartao
    assert "ainda não foi enviado" in cartao
    assert "pode ser pedido agora" not in cartao

    # Momento 3: o envio. **As tentativas gravadas fora da ordem do número** (revisão do #453,
    # achado 5): a segunda, aceita, antes da primeira, que falhou. O estado da `066` lê a última
    # pelo número; lida na ordem em que o banco a devolvesse, a tela diria "falha temporária".
    _tentativas_fora_de_ordem(bernardo)
    cartao = _cartao(_abrir(client, edital, marco_id).content.decode(), bernardo.id)
    assert "aceito pelo servidor de correio em" in cartao
    assert "entregue" not in cartao

    # A página dos documentos da mesma pessoa: o lugar, a situação e as vizinhas (FR-5019 a
    # FR-5024).
    pagina = client.get(
        reverse("interface:documentos-da-convocacao", args=[edital.id, marco_id, bernardo.id])
    ).content.decode()
    assert "<dt>Perfil</dt>" in pagina and "<dt>Lista</dt>" in pagina
    assert "Situação desta convocação" in pagina
    assert "aceito pelo servidor de correio em" in pagina
    assert "Pessoa 2 de 3" in pagina
    assert f"/convocacao/{alice.id}/documentos" in pagina
    assert f"/convocacao/{cecilia.id}/documentos" in pagina
    assert "Próxima com documento a conferir: Cecília" in pagina
    assert f"#convocacao-{bernardo.id}" in pagina

    # O candidato reenvia: nova conferência, e o aviso não é oferecido.
    inscricao = bernardo.inscricao
    pendente = next(
        lido for lido in servico.leitura_da_chamada(bernardo).pedidos if lido.estado == "PENDENTE"
    )
    docs.apresentar(inscricao, bernardo, pendente.item.requisito_id, corpo=b"nova versao legivel")
    cartao = _cartao(_abrir(client, edital, marco_id).content.decode(), bernardo.id)
    assert "Conferir de novo: o candidato reenviou 1 documento que estava pendente." in cartao
    assert "reenviou o documento pendente em" in cartao
    assert "pode ser pedido agora" not in cartao

    # Quem só consulta lê tudo, e nenhuma ação lhe é oferecida (FR-5012).
    identificar(client, "auditora-143", ["auditor"])
    leitura = _abrir(client, edital, marco_id).content.decode()
    assert "Neste recorte, agora" in leitura
    assert "com-trabalho" not in leitura
    assert "Conferir os documentos</a>" not in leitura
    # O link dos documentos, que a página recusaria à auditoria, só aparece a quem confere
    # (revisão do #453, achado 4); o rótulo e as contagens continuam.
    assert "Documentos da convocação</a>" not in leitura
    assert "Documentos para conferir" in leitura
    assert "<form" not in leitura.split('id="chamadas"', 1)[1]


def _tentativas_fora_de_ordem(convocacao):
    from django.utils import timezone

    from processo_seletivo.avisos.domain import nomes as avisos
    from processo_seletivo.avisos.models import (
        DestinatarioDoAviso,
        ResultadoDaTentativa,
        TentativaDeEnvio,
    )

    destinatario = DestinatarioDoAviso.objects.get(
        convocacao=convocacao, aviso__origem=avisos.PENDENCIA
    )
    agora = timezone.now()
    for numero, resultado in ((2, avisos.ACEITA), (1, avisos.FALHA_TEMPORARIA)):
        tentativa = TentativaDeEnvio.objects.create(
            destinatario=destinatario, numero=numero, iniciada_em=agora
        )
        ResultadoDaTentativa.objects.create(
            tentativa=tentativa, resultado=resultado, registrado_em=agora
        )


# ---------------------------------------------------------------------------------------------
# C12 — conferir tudo, e o desfecho a um clique
# ---------------------------------------------------------------------------------------------


def test_c12(client, cenario):
    edital, manifesto = cenario("C12")
    identificar(client, k.PRESIDENCIA, [])
    marco_id = _marco_da_convocacao(edital)
    resposta = _abrir(client, edital, marco_id)
    corpo = resposta.content.decode()
    _, link = _pergunta(corpo, "com documento a conferir")
    assert link.group(2) == "3"
    # Os fragmentos da `139` continuam (FR-5009).
    assert 'id="chamadas"' in corpo and 'id="chamada-1"' in corpo

    primeira = resposta.context["leitura"]["linhas"][0]["convocacao"]
    ator = retomar(manifesto, autoridade=str(AUTORIDADE_DA_SUITE)).ator(k.PRESIDENCIA)
    for n, lido in enumerate(servico.leitura_da_chamada(primeira).pedidos):
        docs.conferir(ator, primeira, lido.item.requisito_id, "CONFORME", chave=f"c12-143-{n}")

    pagina = client.get(
        reverse("interface:documentos-da-convocacao", args=[edital.id, marco_id, primeira.id])
    ).content.decode()
    assert "Pronta para o desfecho" in pagina
    destino = re.search(
        r'<a class="acao acao-do-passo" href="([^"]+)">Registrar o desfecho desta convocação</a>',
        pagina,
    )
    assert destino and destino.group(1).endswith(f"#convocacao-{primeira.id}"), pagina[:3000]

    corpo = client.get(destino.group(1).split("#")[0]).content.decode()
    cartao = _cartao(corpo, primeira.id)
    assert "Pronta para o desfecho" in cartao
    assert re.search(
        r'<details class="como-preencher desfecho-da-chamada acao-do-passo" open>', cartao
    )
    _, link = _pergunta(corpo, "prontas para o desfecho")
    assert link.group(1) == f"convocacao-{primeira.id}" and link.group(2) == "1"
    # As outras duas, ainda a conferir, têm o desfecho recolhido, como antes.
    outra = _linha(resposta, "C12-02")["convocacao"]
    assert 'desfecho-da-chamada" >' not in _cartao(corpo, outra.id)
    assert " open>" not in _cartao(corpo, outra.id).split("Registrar desfecho", 1)[0][-200:]
