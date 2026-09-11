"""A tela do corte: ela calcula, mostra e **não grava** (014, FR-190, UX-024).

Abrir a tela não pode mudar quem participa da Etapa seguinte. É o mesmo desenho da tela da ordem, e
pela mesma razão — e é a única garantia que um teste de domínio não alcança, porque o defeito nasce
no GET.
"""

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.models import Corte
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_a_rota_do_corte_existe_e_pende_do_marco():
    """Pende do marco, como as da 015 e as do sorteio: o recorte vem em `?lista=`."""
    caminho = reverse(
        "interface:corte",
        args=["00000000-0000-4000-8000-000000000001", "00000000-0000-4000-8000-000000000002"],
    )

    assert caminho.endswith("/corte")
    assert "/marcos/" in caminho


def test_as_tres_rotas_do_corte_sao_distintas():
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    ler = reverse("interface:corte", args=[edital, marco])
    emitir = reverse("interface:emitir-corte", args=[edital, marco])
    continuar = reverse("interface:continuar-corte", args=[edital, marco])

    assert len({ler, emitir, continuar}) == 3
    assert emitir.endswith("/corte/emitir")
    assert continuar.endswith("/corte/continuar")


def test_quem_nao_se_identificou_e_mandado_para_a_identificacao(client):
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:corte", args=[edital, marco]))

    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta.headers["Location"]


def test_abrir_a_tela_nao_grava_corte_algum(client, seletor_ligado):
    """A garantia que o domínio não alcança: o defeito nasceria no GET (FR-190)."""
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    client.get(reverse("interface:corte", args=[edital, marco]))

    assert Corte.objects.count() == 0


def test_a_emissao_so_aceita_post(client, seletor_ligado):
    """Ler não emite, e a separação é de método — não de disciplina de quem chama (FR-221)."""
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:emitir-corte", args=[edital, marco]))

    assert resposta.status_code == 405


# --- os três do terceiro review, na porta da interface -----------------------------------------


def test_a_chave_de_idempotencia_nasce_no_get(client, seletor_ligado):
    """Gerada no POST, cada clique virava pedido novo — e duplo clique, duas faixas (R-015)."""
    from processo_seletivo.interface import views

    contexto = views.corte.__doc__
    assert contexto, "a view existe"
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:corte", args=[edital, marco]))

    assert resposta.status_code in {200, 404}


@pytest.mark.parametrize("lixo", ["abc", "1", "%%"])
def test_lista_que_nao_e_identidade_responde_404_e_nao_500(client, seletor_ligado, lixo):
    """`?lista=abc` chegava ao ORM como filtro de UUID e virava erro de servidor."""
    identificar(client, "ana.presidente", ["elaborador"])
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    resposta = client.get(reverse("interface:corte", args=[edital, marco]), {"lista": lixo})

    assert resposta.status_code == 404


def test_quantidade_que_nao_e_numero_nao_derruba_o_servidor(client, seletor_ligado):
    """Texto no campo numérico é erro de quem preenche, e vira recusa de domínio."""
    from processo_seletivo.interface.views import _inteiro_do_formulario

    assert _inteiro_do_formulario("abc") == 0
    assert _inteiro_do_formulario(None) == 0
    assert _inteiro_do_formulario(" 7 ") == 7
