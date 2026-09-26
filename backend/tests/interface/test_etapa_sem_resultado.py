"""A Etapa que o fluxo não consegue concluir não atravessa a publicação — pela tela (046, US1).

O caso do achado de 21/09: *"Avaliações por inscrição"* = 2 numa Etapa eliminatória. O Edital
publicava, a distribuição atribuía duas leituras, dois avaliadores concluíam, e só a consolidação
dizia que não sabia combinar o que produziu. Aqui a Revisão diz antes, a submissão recusa, e o
`como-preencher` explica o campo onde ele é preenchido (`FR-750`).
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import levar_a_publicacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

NAO_TERA_RESULTADO = "não terá Resultado"
COMBINAR = "não declara como combiná-las"


def _criar(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _gravar(api_client, edital, rascunho, chave):
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert gravado.status_code == 200, gravado.content
    return Edital.objects.get(pk=edital.pk)


def _pagina(client, edital, etapa):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, etapa]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def _severidade_de(pagina, frase):
    """`"erro"` ou `"aviso"`: a classe do item da lista que carrega a frase."""
    trecho = pagina[: pagina.index(frase)]
    return "erro" if trecho.rfind("p-erro") > trecho.rfind("p-aviso") else "aviso"


def test_a_etapa_eliminatoria_de_dupla_leitura_e_recusada_e_a_de_uma_publica(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    rascunho = rascunho_com_etapas(avaliacoes=2)
    edital = _gravar(
        api_client, _criar(api_client, manager_headers, process_payload), rascunho, "046-us1-a"
    )
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = _pagina(client, edital, "revisao")
    assert COMBINAR in revisao and NAO_TERA_RESULTADO in revisao
    assert _severidade_de(revisao, COMBINAR) == "erro"
    destino = reverse("interface:compor-etapa", args=[edital.id, "etapas"])
    assert f'href="{destino}#etapas-titulo"' in revisao, "e corrige-se na etapa Etapas"

    client.post(reverse("interface:ato", args=[edital.id, "submeter"]), {})
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO

    # Uma avaliação: o Cenário B, e a mesma Etapa publica.
    publicado = levar_a_publicacao(
        api_client, Edital.objects.get(pk=edital.pk), draft=rascunho_com_etapas(avaliacoes=1)
    )
    assert publicado.status == Edital.Status.PUBLICADO


def test_a_decisoria_sem_efeito_fora_de_marco_avisa_e_publica(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A recusa da `013` de 03/09: nada exige o Resultado dela, e ela não é proibida por si."""
    rascunho = rascunho_com_etapas()
    rascunho["stages"][1].update(
        forma="DECISORIA",
        rotuloFavoravel="Apto",
        rotuloDesfavoravel="Inapto",
    )
    edital = _gravar(
        api_client, _criar(api_client, manager_headers, process_payload), rascunho, "046-us1-b"
    )
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = _pagina(client, edital, "revisao")
    assert "Prova didática" in revisao and NAO_TERA_RESULTADO in revisao
    assert _severidade_de(revisao, NAO_TERA_RESULTADO) == "aviso"

    publicado = levar_a_publicacao(api_client, edital, draft=rascunho)
    assert publicado.status == Edital.Status.PUBLICADO


def test_a_mesma_decisoria_enumerada_por_marco_e_recusada(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    rascunho = rascunho_com_etapas()
    segunda = rascunho["stages"][1]
    segunda.update(forma="DECISORIA", rotuloFavoravel="Apto", rotuloDesfavoravel="Inapto")
    rascunho["profiles"][0]["classificationMilestones"][0]["stages"] = [segunda["id"]]
    edital = _gravar(
        api_client, _criar(api_client, manager_headers, process_payload), rascunho, "046-us1-c"
    )
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = _pagina(client, edital, "revisao")

    assert _severidade_de(revisao, NAO_TERA_RESULTADO) == "erro"
    assert "retire-a do marco na etapa Classificação" in revisao, "a outra correção possível"


def test_o_como_preencher_explica_a_dupla_leitura_e_o_cartao_nao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-750`: a explicação mora no `como-preencher`, e nunca no cartão da Etapa."""
    edital = _gravar(
        api_client,
        _criar(api_client, manager_headers, process_payload),
        rascunho_com_etapas(),
        "046-us1-d",
    )
    identificar(client, "ana.elaboradora", ["elaborador"])

    pagina = _pagina(client, edital, "etapas")
    como_preencher = pagina[pagina.index('class="como-preencher"') :]
    como_preencher = como_preencher[: como_preencher.index("</details>")]

    assert "Avaliações por inscrição" in como_preencher
    assert "como combiná-las" in como_preencher
    assert pagina.count("como combiná-las") == 1, "e só ali"
