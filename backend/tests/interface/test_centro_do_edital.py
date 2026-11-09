"""A página do Centro de Controle do Edital: a porta, os dois links e os casos-limite (136).

**A porta é a do detalhe** (FR-4701, D-002): o mesmo 404 para o Edital de outra unidade, e o detalhe
para o Edital sem andamento. **O detalhe não muda**, salvo o link de ida (FR-4703): a suíte dele
continua passando sem alteração, e este arquivo prende só a linha nova.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import conceitos as c
from tests.fixtures.andamento import certame_s1
from tests.fixtures.autoridades import registrar_unidade
from tests.fixtures.edital import mudanca_de_vagas
from tests.fixtures.publicacao import create_retification
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

OUTRA = "campus-136"


def mapa(texto):
    """O mapa só: a barra lateral também usa `aria-current`, para a seção em que se está."""
    return texto.split('<nav class="cc-mapa"', 1)[1].split("</nav>", 1)[0]


def centro(client, edital, fase=None):
    url = reverse("interface:centro-do-edital", args=[edital.id])
    return client.get(url + (f"?fase={fase}" if fase else ""))


@pytest.fixture
def s1(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_s1(gestor, api_client, manager_headers, process_payload)


def test_o_centro_abre_e_volta_ao_detalhe_e_o_detalhe_leva_a_ele(client, s1):
    """US6, FR-4703, FR-4704, SC-1478: ida e volta."""
    edital = s1["edital"]
    identificar(client, "carlos", ["gestor"])

    resposta = centro(client, edital)
    assert resposta.status_code == 200
    texto = resposta.content.decode()
    assert f'href="{reverse("interface:detalhe", args=[edital.id])}"' in texto
    assert "Em validação." in texto and "Onde estamos" in texto
    # FR-4720: três estados separados, cada um com rótulo.
    for rotulo in ("Situação administrativa", "Inscrições", "Seu papel aqui"):
        assert f"<dt>{rotulo}</dt>" in texto
    assert "Você conduz a seleção." in texto
    # FR-4740: a administração depois da operação.
    administracao = texto.split('id="administracao"', 1)[1]
    for titulo in ("Documentos publicados", "Consultas e documentos", "Quem atuou"):
        assert f"<h3>{titulo}</h3>" in administracao
    assert texto.index('id="agora-titulo"') < texto.index('id="administracao-titulo"')

    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert f'href="{reverse("interface:centro-do-edital", args=[edital.id])}"' in detalhe


def test_o_mapa_tem_oito_fases_e_uma_so_consultada(client, s1):
    """FR-4708, FR-4731: a fase pedida que não existe cai na regra fixa."""
    identificar(client, "carlos", ["gestor"])
    texto = centro(client, s1["edital"], fase="inexistente").content.decode()

    assert texto.count('<li class="cc-fase') == 8
    # FR-4748: o sinal do andamento sempre com a palavra.
    edital = mapa(texto).split('data-fase="publicacao"', 1)[1].split("</li>", 1)[0]
    assert "✓" in edital and "Concluída" in edital
    for rotulo in ("Abertura", "Seleção", "Ocupação"):
        assert f">{rotulo}</h3>" in texto
    assert mapa(texto).count('aria-current="true"') == 1
    assert texto.count('<span class="oculto">fase consultada: </span>') == 1


def test_antes_da_publicacao_o_centro_leva_ao_detalhe(
    client, api_client, manager_headers, process_payload, seletor_ligado
):
    """D-002, FR-4702: o Edital em elaboração não tem andamento, e o detalhe não oferece o link."""
    from processo_seletivo.processos.models import Edital

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    identificar(client, "carlos", ["gestor"])
    resposta = centro(client, edital)

    assert resposta.status_code == 302
    assert resposta.url == reverse("interface:detalhe", args=[edital.id])
    detalhe = client.get(resposta.url).content.decode()
    assert reverse("interface:centro-do-edital", args=[edital.id]) not in detalhe


def test_o_edital_de_outra_unidade_e_inexistente(client, s1):
    """FR-4701: o mesmo 404 do detalhe."""
    registrar_unidade(OUTRA)
    identificar(client, "carlos", ["gestor"], escopo=OUTRA)

    assert centro(client, s1["edital"]).status_code == 404
    assert client.get(reverse("interface:detalhe", args=[s1["edital"].id])).status_code == 404


def test_sem_identidade_pede_identificacao(client, s1):
    resposta = centro(client, s1["edital"])
    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta.url


def test_o_edital_sem_inscricao_nao_tem_nada_em_aberto(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """Caso-limite: o porquê de "Nada em aberto" é o da `127`."""
    vazio = certame_s1(gestor, api_client, manager_headers, process_payload, quantos=0)
    identificar(client, "carlos", ["gestor"])
    resposta = centro(client, vazio["edital"])
    texto = resposta.content.decode()

    assert resposta.context["centro"].total == 0
    assert "<strong>Nada em aberto:</strong> nenhum Perfil com marco recebeu inscrição." in texto
    assert '<article class="cc-destaque"' not in texto


def test_a_retificacao_em_curso_aparece_e_poe_o_edital_em_curso(client, s1, api_client):
    """Caso-limite: a Retificação pode mudar qualquer fase, e a página o diz."""
    create_retification(api_client, s1["edital"], mudanca_de_vagas(5), suffix="cc136")
    identificar(client, "carlos", ["gestor"])
    resposta = centro(client, s1["edital"], fase="publicacao")
    texto = resposta.content.decode()

    [edital] = [f for f in resposta.context["centro"].fases if f.chave == c.PUBLICACAO]
    assert edital.andamento == c.EM_CURSO
    assert c.RETIFICACAO_EM_CURSO in texto
    assert "Retificação em curso</strong>" in texto


def test_o_sorteio_s1_mostra_a_relacao_como_acao_de_quem_conduz(client, s1):
    """S1 da `127`: a presidência (`maria`) tem a relação; quem só acompanha, não."""
    identificar(client, "maria", [])
    resposta = centro(client, s1["edital"])
    nomes = [i.titulo for i in resposta.context["centro"].suas]
    assert "Fixar os participantes" in nomes

    identificar(client, "auditora", ["auditor"])
    resposta = centro(client, s1["edital"])
    assert resposta.status_code == 200
    assert not resposta.context["centro"].suas


def test_as_fases_do_edital_tem_detalhe_proprio(client, s1):
    """FR-4735: documentos na fase Edital, a linha das inscrições, o que o encerramento pede."""
    identificar(client, "carlos", ["gestor"])
    texto = centro(client, s1["edital"], fase="publicacao").content.decode()
    detalhe = texto.split('id="detalhe-da-fase"', 1)[1].split("</section>", 1)[0]
    assert "Publicação original nº 1" in detalhe and "corrige-se por Retificação" in detalhe

    texto = centro(client, s1["edital"], fase="inscricoes").content.decode()
    detalhe = texto.split('id="detalhe-da-fase"', 1)[1].split("</section>", 1)[0]
    assert "Inscrições" in detalhe and "enviadas" in detalhe

    texto = centro(client, s1["edital"], fase="conclusao").content.decode()
    detalhe = texto.split('id="detalhe-da-fase"', 1)[1].split("</section>", 1)[0]
    assert "O encerramento é do Gestor" in detalhe


def test_a_fase_por_lista_traz_o_roteiro_e_o_porque_recolhido(client, s1):
    """FR-4733, FR-4736: o roteiro à vista, o porquê de cada passo num bloco recolhido só."""
    identificar(client, "carlos", ["gestor"])
    texto = centro(client, s1["edital"], fase="classificacao").content.decode()
    detalhe = texto.split('id="detalhe-da-fase"', 1)[1].split("</section>", 1)[0]
    assert '<ol class="cc-roteiro"' in detalhe
    assert "Fixar os participantes" in detalhe and "no GPS: congelar a relação" in detalhe
    assert detalhe.count("<summary>Entenda os passos desta fase</summary>") == 1
