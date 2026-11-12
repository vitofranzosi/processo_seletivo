"""A lista em que ninguém concorre, num gesto com uma conferência (155, US5, T038, FR-6328 a
FR-6331).

O cenário é o 7/1/2 da `034` sem autodeclarado: as duas listas reservadas não têm quem concorra, e o
marco corta pelo quadro — o gesto emite a ordem vazia **e** o corte vazio. Os caminhos são lidos da
própria página sempre que a tela os oferece, como em `test_navegacao_entre_recortes.py`.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.models import (
    AtoDeOrdenacao,
    Corte,
    ItemDoCorte,
    PosicaoNaOrdem,
)
from processo_seletivo.interface import lista_sem_concorrente as gesto
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import MODALIDADE_PCD, MODALIDADE_PPI, montar_cenario_7_1_2
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def vazio(gestor, api_client, manager_headers, process_payload):
    """O 7/1/2 com a ordem da ampla emitida e ninguém nas duas reservadas."""
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="lista-155-vazia",
        autodeclarar=False,
    )
    return edital


def _rota(edital):
    return reverse("interface:registrar-lista-sem-concorrente", args=[edital.id, MARCO])


def _conferir(client, edital, lista=MODALIDADE_PCD):
    resposta = client.get(f"{_rota(edital)}?lista={lista}")
    assert resposta.status_code == 200, resposta.content
    pagina = resposta.content.decode()
    campos = dict(re.findall(r'name="(chave|leitura)" value="([^"]*)"', pagina))
    return pagina, campos


def _confirmar(client, edital, campos, lista=MODALIDADE_PCD):
    return client.post(
        _rota(edital),
        {"lista": lista, "confirmar": "1", "chave": campos["chave"], "leitura": campos["leitura"]},
    )


def test_a_ordenacao_oferece_o_gesto_e_a_conferencia_diz_o_que_se_registra(
    client, seletor_ligado, vazio
):
    """US5.1, FR-6331: a providência diz que ninguém concorre, e a conferência abre com a frase do
    ato da `135` e diz que a lista vai junto da publicação do marco."""
    identificar(client, "carlos", ["gestor"])
    tela = client.get(
        reverse("interface:ordenacao", args=[vazio.id, MARCO]) + f"?lista={MODALIDADE_PCD}"
    ).content.decode()
    link = re.search(r'href="([^"]*lista-sem-concorrente[^"]*)"', tela)
    assert link is not None, "a tela da ordenação leva ao gesto"
    pagina = client.get(link.group(1).replace("&amp;", "&")).content.decode()

    assert "Emitir a ordem que declara que ninguém concorreu nesta lista" in pagina
    assert "a ordem vazia declara que ninguém concorreu" in pagina
    assert "junto das outras listas" in pagina and "sem publicação própria" in pagina
    assert "o corte vazio" in pagina
    assert not AtoDeOrdenacao.objects.filter(edital=vazio, lista_id=MODALIDADE_PCD).exists(), (
        "abrir a conferência não grava nada"
    )


def test_o_gesto_emite_a_ordem_vazia_e_o_corte_vazio_sem_linha_de_candidato(
    client, seletor_ligado, vazio
):
    """FR-6328, FR-6329: os dois registros de hoje, numa confirmação, e nenhuma linha."""
    identificar(client, "carlos", ["gestor"])
    _, campos = _conferir(client, vazio)

    resposta = _confirmar(client, vazio, campos)

    assert resposta.status_code == 302
    ato = ato_vigente(edital=vazio, marco_id=MARCO, lista_id=MODALIDADE_PCD)
    assert ato is not None
    corte = Corte.objects.get(edital=vazio, lista_id=MODALIDADE_PCD)
    assert corte.ato_id == ato.id and corte.ultima_posicao is None
    assert not PosicaoNaOrdem.objects.filter(ato=ato).exists()
    assert not ItemDoCorte.objects.filter(corte=corte).exists()
    registro = RegistroAuditoria.objects.get(operation=gesto.EVENTO)
    assert str(registro.aggregate_id) == str(ato.id)
    # A outra lista vazia não foi tocada: o gesto é da lista conferida.
    assert ato_vigente(edital=vazio, marco_id=MARCO, lista_id=MODALIDADE_PPI) is None
    tela = client.get(resposta["Location"]).content.decode()
    assert "Registrado que ninguém concorreu" in tela


def test_a_repeticao_do_envio_devolve_o_desfecho_da_primeira_vez(client, seletor_ligado, vazio):
    """A chave do gesto deriva as dos dois comandos: o segundo envio não emite nada."""
    identificar(client, "carlos", ["gestor"])
    _, campos = _conferir(client, vazio)
    _confirmar(client, vazio, campos)
    _confirmar(client, vazio, campos)

    assert AtoDeOrdenacao.objects.filter(edital=vazio, lista_id=MODALIDADE_PCD).count() == 1
    assert Corte.objects.filter(edital=vazio, lista_id=MODALIDADE_PCD).count() == 1
    assert RegistroAuditoria.objects.filter(operation=gesto.EVENTO).count() == 1


def test_o_gesto_recusa_a_lista_em_que_alguem_concorre(
    gestor, api_client, manager_headers, process_payload
):
    """`lista_com_concorrente`: a lista com linhas tem a conferência da ordem, e não o gesto."""
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="lista-155-cheia",
        autodeclarar=False,
        modalidades={0: MODALIDADE_PPI},
    )
    lida = gesto.conferencia(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=MODALIDADE_PPI
    )
    assert lida["recusa"][0] == gesto.LISTA_COM_CONCORRENTE
    with pytest.raises(DomainError) as recusa:
        gesto.registrar_lista_sem_concorrente(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=MODALIDADE_PPI,
            assinatura=lida["assinatura"],
            idempotency_key="lista-155-cheia-gesto",
            correlation_id="teste-155",
        )
    assert recusa.value.code == gesto.LISTA_COM_CONCORRENTE
    assert not AtoDeOrdenacao.objects.filter(edital=edital, lista_id=MODALIDADE_PPI).exists()


def test_a_leitura_mudada_volta_a_conferencia_sem_gravar(client, seletor_ligado, vazio, gestor):
    """A ordem vazia emitida por outra pessoa entre a conferência e o clique é leitura nova."""
    from tests.fixtures.recortes import emitir_recorte

    identificar(client, "carlos", ["gestor"])
    _, campos = _conferir(client, vazio)
    emitir_recorte(vazio, gestor, lista_id=MODALIDADE_PCD, chave="lista-155-por-fora")

    resposta = _confirmar(client, vazio, campos)

    assert resposta.status_code == 200
    assert "mudou desde que a conferência foi aberta" in resposta.content.decode()
    assert not Corte.objects.filter(edital=vazio, lista_id=MODALIDADE_PCD).exists()


def test_a_ordem_vazia_emitida_antes_recebe_so_o_corte(client, seletor_ligado, vazio, gestor):
    """O registro de hoje não se perde nem se repete: a lista que já tem a ordem vazia, emitida
    antes da `155`, recebe só o corte vazio."""
    from tests.fixtures.recortes import emitir_recorte

    emitir_recorte(vazio, gestor, lista_id=MODALIDADE_PCD, chave="lista-155-antes")
    identificar(client, "carlos", ["gestor"])
    pagina, campos = _conferir(client, vazio)
    assert "já emitida, vazia" in pagina

    _confirmar(client, vazio, campos)

    assert AtoDeOrdenacao.objects.filter(edital=vazio, lista_id=MODALIDADE_PCD).count() == 1
    assert Corte.objects.filter(edital=vazio, lista_id=MODALIDADE_PCD).count() == 1
