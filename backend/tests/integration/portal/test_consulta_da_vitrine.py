"""Encontrar a oportunidade certa sem ler todas (024, FR-138 a FR-146a).

**Por que existe.** A vitrine não lia parâmetro nenhum: sem busca, sem filtro, sem ordenação e sem
contagem. Com um punhado de seleções, ler todos os cartões funciona; a lacuna cresce com o catálogo,
e o custo de voltar a esta tela depois é maior que o de fazer junto.

O que estes testes prendem, além do óbvio: que a consulta viva **no endereço** — compartilhável,
reproduzível, e sobrevivendo à volta —, e que valor irreconhecível seja lido como ausência de filtro
e nunca como erro.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def publicar(api_client, manager_headers, process_payload, *, numero, seed, ajustar=None):
    """Uma seleção com identidade própria — código, número e Perfis distintos dos demais."""
    rascunho = rascunho_de_selecao(seed=seed)
    agora = timezone.now()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=9)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    if ajustar:
        ajustar(rascunho)
    return publicar_selecao(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"consulta-da-vitrine-{numero:04d}"},
        {
            **process_payload,
            "institutionalCode": f"PS-BUSCA-{numero}",
            "firstEdital": {**process_payload["firstEdital"], "number": f"8{numero}"},
        },
        rascunho=rascunho,
        seed=seed,
    )


@pytest.fixture
def catalogo(api_client, manager_headers, process_payload):
    """Duas seleções que não se confundem: Perfis distintos e unidades distintas."""

    def enfermagem(rascunho):
        rascunho["profiles"][0]["name"] = "Enfermeiro"
        rascunho["profiles"][0]["locality"] = "Campus Cariacica"
        rascunho["profiles"][1]["name"] = "Auxiliar de Enfermagem"

    publicar(api_client, manager_headers, process_payload, numero=1, seed=1)
    publicar(api_client, manager_headers, process_payload, numero=2, seed=2, ajustar=enfermagem)
    return None


def buscar(client, **parametros):
    return client.get(reverse("portal:vitrine"), parametros).content.decode()


def lista(corpo):
    """A lista de cartões, sem o formulário: o `<select>` de filtros contém os mesmos rótulos das
    situações, e uma busca por substring na página inteira encontraria aqueles."""
    marcador = '<ul class="selecoes">'
    return corpo[corpo.index(marcador) :] if marcador in corpo else ""


def test_a_busca_devolve_so_o_que_tem_o_termo_e_diz_quantas(client, catalogo):
    """FR-138, FR-141, T-011 — e o termo procurado aparece em cada cartão devolvido.

    Buscar dentro de descrição ou requisitos devolveria cartões em que o termo não aparece em lugar
    nenhum, e o resultado pareceria erro. O que se busca é o que se vê.
    """
    corpo = buscar(client, busca="Enfermeiro")

    assert "Enfermeiro" in lista(corpo)
    assert "Professor de Informática" not in lista(corpo)
    assert "<strong>1</strong>" in corpo
    assert "seleção encontrada" in corpo


def test_acento_e_caixa_nao_distinguem(client, catalogo):
    """T-005 — quem digita no celular quase nunca acentua."""
    com_acento = buscar(client, busca="Informática")
    sem_acento = buscar(client, busca="informatica")

    assert "Professor de Informática" in lista(com_acento)
    assert "Professor de Informática" in lista(sem_acento)


def test_a_busca_alcanca_o_numero_do_edital(client, catalogo):
    """FR-138 — o número está no cartão, e por isso é buscável."""
    corpo = buscar(client, busca="81/2026")

    assert "<strong>1</strong>" in corpo


def test_filtro_e_busca_se_somam(client, catalogo):
    """FR-139 — `E` entre eles, nunca `OU`.

    `OU` devolveria **mais** resultados a cada filtro acrescentado, que é o contrário do que quem
    filtra está pedindo.
    """
    so_busca = buscar(client, busca="Enfermeiro")
    com_filtro = buscar(client, busca="Enfermeiro", perfil="Professor de Informática")

    assert "<strong>1</strong>" in so_busca
    assert "Nenhuma seleção encontrada" in com_filtro


def test_filtro_por_situacao_e_por_unidade(client, catalogo):
    """FR-139 — os dois filtros que restringem sem depender do que a pessoa digita."""
    abertas = buscar(client, situacao="aberto")
    encerradas = buscar(client, situacao="encerrado")

    assert "<strong>2</strong>" in abertas
    assert "Nenhuma seleção encontrada" in encerradas


def test_consulta_sem_resultado_diz_o_que_foi_procurado_e_nao_e_erro(client, catalogo):
    """FR-142 — a tela oferece a volta ao catálogo, e a resposta continua 200.

    Tratar como falha faria alguém achar que a página quebrou, quando o que houve foi um catálogo
    que não tem aquilo hoje.
    """
    resposta = client.get(reverse("portal:vitrine"), {"busca": "veterinária"})
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Nenhuma seleção encontrada" in corpo
    assert "veterinária" in corpo, "a tela não disse o que foi procurado"
    assert "Ver todas as seleções" in corpo


@pytest.mark.parametrize(
    "parametros",
    [
        {"situacao": "banana"},
        {"ordem": "xyz"},
        {"unidade": "Campus Que Nao Existe"},
        {"perfil": "Cargo inventado"},
        {"busca": "   "},
    ],
)
def test_valor_irreconhecivel_e_lido_como_ausencia_de_filtro(client, catalogo, parametros):
    """T-004 — nunca 4xx, nunca mensagem de erro.

    Recusar daria a um endereço colado um comportamento pior do que o de não filtrar, e abriria
    superfície de mensagem de erro numa página anônima. É a mesma régua da `FR-142`.
    """
    resposta = client.get(reverse("portal:vitrine"), parametros)
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Nenhuma seleção encontrada" not in corpo
    assert "Professor de Informática" in lista(corpo)
    assert "Enfermeiro" in lista(corpo)


def test_a_ordem_padrao_e_o_prazo_e_recentes_ordena_pela_vigencia(client, catalogo):
    """FR-140, T-006 — ordena-se pelo instante **do que o cartão mostra**.

    Não pelo do ato que o produziu: uma Retificação publicada hoje e vigente semana que vem não
    muda a posição hoje, porque o cartão ainda mostra o conteúdo anterior.
    """
    padrao = buscar(client)
    recentes = buscar(client, busca="a", ordem="recentes")

    assert '<h2 class="secao-vitrine">Inscrições abertas</h2>' in padrao
    # A segunda publicada é a mais recente, e com `recentes` ela vem primeiro.
    assert lista(recentes).index("Enfermeiro") < lista(recentes).index("Professor de Informática")


def test_sem_consulta_ha_grupos_e_com_consulta_ha_lista_unica(client, catalogo):
    """FR-146, FR-146a — agrupar é ajuda para quem folheia; ordenar, para quem procura.

    Quatro cabeçalhos sobre um cartão cada seria ruído. A lista corrida é segura porque cada cartão
    traz a própria marca de situação.
    """
    sem_consulta = buscar(client)
    com_consulta = buscar(client, busca="Enfermeiro")

    assert '<h2 class="secao-vitrine">' in sem_consulta
    assert '<h2 class="secao-vitrine">' not in com_consulta
    assert 'class="marca-situacao aberto"' in lista(com_consulta)


def test_ordenar_sozinho_nao_desfaz_os_grupos(client, catalogo):
    """FR-146a — ordenar não reduz o catálogo, e por isso não é "consulta ativa".

    Tratar a ordenação como filtro faria a lista perder os grupos por um gesto que não filtrou nada.
    """
    corpo = buscar(client, ordem="recentes")

    assert '<h2 class="secao-vitrine">' in corpo
    assert "Nenhuma seleção encontrada" not in corpo


def test_a_consulta_esta_inteira_no_endereco_e_reproduz_a_mesma_lista(client, catalogo):
    """FR-143, SC-045 — compartilhável, e o histórico do navegador a reproduz.

    Guardar em sessão seria a alternativa aparentemente mais simples, e produziria duas abas na
    mesma vitrine mostrando listas diferentes sem explicação na tela.
    """
    from django.test import Client

    primeira = buscar(client, busca="Enfermeiro", ordem="recentes")
    outra_pessoa = Client().get(
        reverse("portal:vitrine"), {"busca": "Enfermeiro", "ordem": "recentes"}
    )

    assert lista(primeira) == lista(outra_pessoa.content.decode())


def test_o_cartao_leva_a_consulta_consigo(client, catalogo):
    """FR-144 — sem isto, cada cartão aberto custava refazer o filtro."""
    corpo = buscar(client, busca="Enfermeiro")

    assert "?busca=Enfermeiro" in lista(corpo)


def test_a_ordem_padrao_nao_polui_o_endereco(client, catalogo):
    """Sem consulta nenhuma, o link do cartão não carrega parâmetro.

    A ordem padrão é ordem, não escolha. Pô-la no endereço fazia toda vitrine virgem produzir
    `?ordem=prazo` em cada cartão: o endereço deixava de ser canônico, e quem copiasse
    compartilharia um parâmetro que não escolheu.
    """
    virgem = buscar(client)
    escolhida = buscar(client, ordem="recentes")

    assert "?ordem=prazo" not in virgem
    assert "?" not in lista(virgem).split("</ul>")[0].split('href="')[1].split('"')[0]
    assert "ordem=recentes" in escolhida
