"""US1 da `027`: quem compõe declara a quantidade **uma vez**, e o Edital apura por ela.

Percurso `A1`–`A5` do quickstart, pelo canal do ator — a interface administrativa —, que é o que o
Princípio VI exige e o que a suíte de unidade não prova.

**O que este arquivo existe para impedir que volte.** Antes da `027`, o Perfil tinha duas caixas de
número: "Vagas imediatas", com rótulo em português corrente, e "Quadro de vagas › Ampla
concorrência", sem explicação visível. O Edital publicava a primeira; a Ocupação e a Convocação
usavam a segunda. Quem preenchia só a primeira — que é o caminho natural — publicava um Edital que
dizia "2 vagas imediatas" e respondia, semanas depois, "não há quantidade declarada a apurar". Os
três Editais da demonstração oficial e os quatro do ambiente auditado estavam todos assim.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.perfis import LinhaDoQuadroDeVagas
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import DocumentoPublicado
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.interface.conftest import identificar
from tests.interface.test_fluxo import EVENTOS, texto_de_pdf_bytes

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.acceptance]

SIGNATARIO = {"signatario": "reitoria"}
PERFIL_SEM_COTA = {
    "perfil-0-id": "cccccccc-0000-4000-8000-00000000e001",
    "perfil-0-code": "DOC-INFO",
    "perfil-0-name": "Professor de Informática",
    "perfil-0-immediateVacancies": "2",
    "perfil-0-reserveType": "NONE",
}


@pytest.fixture
def edital(db, api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def compor(client, edital, etapa, dados):
    edital.refresh_from_db()
    resposta = client.post(reverse("interface:compor-etapa", args=[edital.id, etapa]), dados)
    assert resposta.status_code == 302, resposta.content


def praticar(client, acao, **campos):
    edital = Edital.objects.get()
    url = reverse("interface:ato", args=[edital.id, acao])
    confirmacao = client.get(url)
    assert confirmacao.status_code == 200, confirmacao.content
    resposta = client.post(
        url, {"chave_idempotencia": confirmacao.context["chave_idempotencia"], **campos}
    )
    assert resposta.status_code in (200, 302), resposta.content


def test_a1_a5_a_quantidade_declarada_uma_vez_governa_o_documento_e_a_apuracao(
    client, seletor_ligado, edital
):
    """O percurso inteiro: compor, publicar, ler o documento, e ter o que apurar.

    `A1` a `A5` do [quickstart](../../specs/027-estrutural-de-vagas/quickstart.md).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    # A1 — o cartão que a tela oferece tem **um** campo de quantidade, e nenhum bloco de quadro.
    # É o fragmento que chega ao clicar em "Acrescentar Perfil": o Edital vazio ainda não tem
    # nenhum, e é aqui que quem compõe do zero encontra o campo pela primeira vez.
    cartao = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' not in cartao
    assert re.search(r'name="perfil-0-immediateVacancies"', cartao)
    visiveis = re.findall(r'<input type="number"[^>]*name="linha-0-\d+-immediateVacancies"', cartao)
    assert visiveis == [], "não existe um segundo campo para a mesma quantidade"

    # A2 — declarada a quantidade, a linha geral existe, e ninguém a digitou.
    compor(client, edital, "perfis", PERFIL_SEM_COTA)
    linha = LinhaDoQuadroDeVagas.objects.get()
    assert (linha.modalidade_id, linha.vagas_imediatas) == (None, 2)

    # A3 — a travessia que já custou quantidade publicável: gravar **outra** etapa não a leva.
    identidade = linha.id
    compor(client, edital, "cronograma", EVENTOS)
    assert LinhaDoQuadroDeVagas.objects.get().id == identidade

    # A4 — a Revisão mostra o Perfil, e o Edital pode ser submetido.
    revisao = client.get(
        reverse("interface:compor-etapa", args=[Edital.objects.get().id, "revisao"])
    )
    assert revisao.status_code == 200
    assert "2 vaga(s) imediata(s)" in revisao.content.decode()

    # A5 — publicado, o conteúdo canônico carrega a linha, e o documento a exibe.
    praticar(client, "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, "homologar", motivo="Conferido")
    identificar(client, "carla.publicadora", ["publicador"])
    praticar(client, "publicar", motivo="Publicação", **SIGNATARIO)

    vigente = VersaoConsolidada.objects.get().content
    quadro = vigente["profiles"][0]["vacancyTable"]
    assert [(item["modalityId"], item["immediateVacancies"]) for item in quadro] == [(None, 2)], (
        "a quantidade que o Edital publica é a mesma que a apuração vai usar"
    )

    documento = texto_de_pdf_bytes(bytes(DocumentoPublicado.objects.get().bytes))
    assert "Ampla concorrência" in documento, "o candidato lê a repartição, e não só o total"


def test_a6_a_primeira_lista_reservada_faz_o_bloco_aparecer_preenchido(
    client, seletor_ligado, edital
):
    """`A6`: o bloco chega quando há repartição a pedir, e não antes (FR-321).

    E chega **preenchido com o total**: a repartição começa de um lugar verdadeiro, em vez de um
    campo vazio que quem compõe teria de reconstituir de cabeça.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, "perfis", PERFIL_SEM_COTA)

    fragmento = client.get(
        reverse("interface:fragmento-modalidade", args=[0]),
        {"indice": "3", "perfil-0-immediateVacancies": "2"},
    ).content.decode()

    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in fragmento
    assert "Este Perfil declara lista reservada" in fragmento
    quantidades = re.findall(r'name="linha-0-\d+-immediateVacancies"\s+value="([^"]*)"', fragmento)
    assert quantidades[0] == "2", "a linha geral chega com o total que está na tela"
