"""A tela do sorteio no dia do sorteio — com a transmissão aberta (021, FR-062).

**O que este arquivo guarda é o que a suíte verde não via.** Os 216 casos da feature provavam que o
domínio recusa o que tem de recusar; nenhum deles lia a frase que a tela devolve depois de cada
comando, nem clicava duas vezes no botão de sortear, nem perguntava se a tela era alcançável por
algum link.

Os quatro defeitos que ele fecha são de tela, e todos apareceriam no pior momento possível:

1. uma faixa de sucesso só, escrita para a publicação da relação, respondia aos quatro comandos —
   depois de **realizar o sorteio** a tela anunciava "Relação publicada e congelada, com 327
   participantes", omitindo a semente e a ordem;
2. os formulários não enviavam chave de idempotência: o duplo clique não era repetição, batia numa
   recusa e pintava a tela de vermelho depois de o sorteio ter dado certo;
3. a tabela transmitida era a projeção do instante, e não a relação congelada;
4. terminado o sorteio, o caminho para divulgá-lo não estava em lugar nenhum desta tela.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.sorteios.models import Sorteio
from tests.fixtures.sorteio import certame_de_sorteio
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _tela(client, certame):
    return client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()


def _postar(client, certame, rota, dados=None):
    return client.post(reverse(rota, args=[certame["edital"].id, certame["marco"]]), dados or {})


def _congelar(client, certame):
    return _postar(
        client,
        certame,
        "interface:publicar-relacao-do-sorteio",
        {"lista_id": "", "chave_idempotencia": "console-relacao"},
    )


def _observar(client, certame):
    return _postar(
        client,
        certame,
        "interface:observar-ocorrencia-do-sorteio",
        {"chave_idempotencia": "console-ocorrencia"},
    )


def _campos_do_botao(client, certame):
    """O que o formulário de sortear leva — capturado **uma vez**, como o navegador o teria.

    Capturar antes é o que permite reproduzir o duplo clique: depois do primeiro envio a tela deixa
    de oferecer o botão, corretamente, e quem já tinha a página aberta continua com ele na tela.
    """
    corpo = _tela(client, certame)
    relacao = re.search(r'name="relacao_id" value="([^"]+)"', corpo)
    ocorrencia = re.search(r'name="ocorrencia_id" value="([^"]+)"', corpo)
    assert relacao and ocorrencia, "a tela não ofereceu o botão de sortear"
    return relacao.group(1), ocorrencia.group(1)


def _sortear(client, certame, *, campos=None, chave="console-sorteio"):
    relacao, ocorrencia = campos or _campos_do_botao(client, certame)
    return _postar(
        client,
        certame,
        "interface:realizar-sorteio",
        {"relacao_id": relacao, "ocorrencia_id": ocorrencia, "chave_idempotencia": chave},
    )


def test_a_faixa_de_desfecho_diz_o_que_o_comando_fez(certame, client):
    """**Cada comando responde pelo que ele fez**, e a transmissão lê essa frase.

    Havia uma frase só. Depois de observar a extração, a tela dizia "Relação publicada e congelada,
    com  participante. O resumo é ." — com os dois valores em branco, porque o desfecho da
    observação não os tem. Depois de sortear, dizia a mesma coisa com a contagem certa e o resumo
    vazio: factualmente falsa, no minuto mais visto do certame.
    """
    identificar(client, "maria", [])

    _congelar(client, certame)
    depois_da_relacao = _tela(client, certame)
    assert "Relação publicada e congelada" in depois_da_relacao

    _observar(client, certame)
    depois_da_ocorrencia = _tela(client, certame)
    assert "Relação publicada e congelada" not in depois_da_ocorrencia, (
        "observar a extração não publica relação nenhuma"
    )
    assert "Números obtidos" in depois_da_ocorrencia
    assert "12345 67890 11223 44556 77889" in depois_da_ocorrencia

    _sortear(client, certame)
    depois_do_sorteio = _tela(client, certame)
    assert "Relação publicada e congelada" not in depois_do_sorteio
    assert "Sorteio realizado" in depois_do_sorteio
    # A semente e o manifesto são o que a audiência precisa ver no instante em que o ato nasce.
    assert "12345 67890 11223 44556 77889" in depois_do_sorteio
    assert "Falta publicar a classificação" in depois_do_sorteio


def test_a_recusa_nomeia_o_comando_que_falhou(certame, client):
    """ "Não foi possível publicar" prefixava a falha da fonte externa e a do próprio sorteio."""
    identificar(client, "maria", [])
    _congelar(client, certame)
    _observar(client, certame)
    campos = _campos_do_botao(client, certame)
    _sortear(client, certame, campos=campos)

    # Sortear de novo, sobre a mesma tupla, é recusado — e a recusa é do sorteio, não da relação.
    _sortear(client, certame, campos=campos, chave="console-sorteio-outra")
    corpo = _tela(client, certame)

    assert "Não foi possível realizar o sorteio:" in corpo
    assert "Não foi possível publicar a relação:" not in corpo


def test_o_duplo_clique_no_botao_de_sortear_nao_vira_faixa_vermelha(certame, client):
    """**A repetição devolve o desfecho da primeira**, e a tela continua verde (FR-032).

    Sem a chave no formulário, cada envio gerava uma chave nova: o segundo clique não era
    reconhecido como repetição, batia em `draw_already_constituted` e anunciava uma falha — depois
    de o sorteio ter dado certo, ao vivo.
    """
    identificar(client, "maria", [])
    _congelar(client, certame)
    _observar(client, certame)

    campos = _campos_do_botao(client, certame)
    _sortear(client, certame, campos=campos, chave="duplo-clique")
    _sortear(client, certame, campos=campos, chave="duplo-clique")

    assert Sorteio.objects.count() == 1, "um clique duplo não constitui dois atos"
    corpo = _tela(client, certame)
    assert "Sorteio realizado" in corpo
    assert "Não foi possível" not in corpo


def test_todo_formulario_da_tela_leva_chave_de_idempotencia(certame, client):
    """A varredura é sobre a marcação: um formulário novo sem a chave aparece aqui."""
    identificar(client, "maria", [])
    _congelar(client, certame)
    _observar(client, certame)
    corpo = _tela(client, certame)

    formularios = [
        formulario
        for formulario in re.findall(r"<form method=\"post\".*?</form>", corpo, re.S)
        # Os desta tela, e não o de sair, que a base põe no cabeçalho de todas.
        if "/sorteio" in formulario.split(">", 1)[0]
    ]
    assert formularios, "a varredura não encontrou formulário algum"
    for formulario in formularios:
        assert 'name="chave_idempotencia"' in formulario, formulario[:200]


def test_a_tabela_transmitida_e_a_relacao_congelada(certame, client, gestor):
    """**O que vai ao ar é o universo comprometido**, e não a projeção do instante (FR-006).

    Depois do congelamento, a tela mostrava quem entraria *agora*: mudado um fato de origem, a
    audiência via uma lista que não era a que o resumo publicado cobre — e a divergência aparecia
    apenas como uma diferença de contagem num aviso ao lado.
    """
    from tests.fixtures.comissao import inscrever

    identificar(client, "maria", [])
    _congelar(client, certame)
    congelados = {inscricao.protocolo for inscricao in certame["inscricoes"]}

    depois = inscrever(certame["edital"], 1, primeiro=950)

    corpo = _tela(client, certame)
    for protocolo in congelados:
        assert protocolo in corpo
    assert depois[0].protocolo not in corpo, (
        "quem se inscreveu depois do congelamento não está na relação, e não pode aparecer na "
        "tabela que a transmissão mostra"
    )
    assert "Relação congelada" in corpo
    # A divergência continua sendo dita — ela é informação, e some da tabela para virar aviso.
    assert "A projeção de agora traria" in corpo


def test_o_caminho_para_publicar_aparece_depois_do_sorteio(certame, client):
    """O passo seguinte fica na tela em que o sorteio terminou (017, FR-069)."""
    identificar(client, "maria", ["publicador"])
    _congelar(client, certame)
    _observar(client, certame)
    _sortear(client, certame)

    corpo = _tela(client, certame)
    sorteio = Sorteio.objects.get()

    assert "Publicar a classificação deste sorteio" in corpo
    assert (
        reverse(
            "interface:previa-de-publicacao",
            args=[certame["edital"].id, certame["marco"], sorteio.ato_id],
        )
        in corpo
    )


def test_quem_nao_publica_nao_recebe_o_caminho(certame, client):
    """Oferecer o que se vai recusar é pior do que não oferecer: `resultado:publicar` é própria."""
    identificar(client, "maria", [])
    _congelar(client, certame)
    _observar(client, certame)
    _sortear(client, certame)

    assert "Publicar a classificação deste sorteio" not in _tela(client, certame)


def test_o_detalhe_do_edital_leva_ao_sorteio(certame, client):
    """**A tela do sorteio não era alcançável por link nenhum** (Constituição §VI).

    O detalhe mandava todo marco para a ordenação — inclusive o que ordena por sorteio —, e no dia
    da transmissão a tela dependia de alguém ter a URL decorada. A ordenação passou a **encaminhar**
    para cá (`test_marco_de_sorteio_nao_se_ordena.py`), e o link direto continua sendo o certo: quem
    lê o Edital procura a ordem deste marco, e ela nasce do sorteio — o desvio no meio do caminho
    resolve o engano, e não o evita.
    """
    identificar(client, "maria", [])

    corpo = client.get(reverse("interface:detalhe", args=[certame["edital"].id])).content.decode()

    assert reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]]) in corpo
    # Com a aspa de fechamento: o endereço da ordenação é **prefixo** do endereço do sorteio, e
    # procurá-lo solto encontraria o próprio link que se acabou de conferir.
    ordenacao = reverse("interface:ordenacao", args=[certame["edital"].id, certame["marco"]])
    assert f'"{ordenacao}"' not in corpo, (
        "o marco que sorteia não abre a tela do cálculo por Etapas"
    )
