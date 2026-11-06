"""O texto que chega ao candidato, conferido antes do ato (125, US2, FR-3991 a FR-3997).

**O texto livre continua chegando ao candidato**, por decisão do usuário de 06/11/2026: o
complemento do fundamento e o fundamento do desfecho. O que estes casos prendem é o que veio no
lugar de tirá-lo: o aviso ao lado de cada campo, e a prévia, com o número de pessoas, antes do
botão que pratica o ato. A prévia é do servidor, e por isso o cliente de teste, que não roda
script, a vê como quem não tem script (FR-3995).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.convocacao.models import Convocacao, DesfechoDaConvocacao
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.interface.conftest import identificar
from tests.interface.test_convocacao_em_fluxo import VENCIMENTO, abrir, postar_titulares, previa

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario_da_tela(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O recorte do teste da `050`: duas vagas, dois titulares e uma suplente."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="interface-125",
        geral=2,
        cut=regra(surplusCount=1),
    )


AVISO = "Este texto será mostrado ao candidato."
COMPLEMENTO = "Item 8.2 do Edital: apresentar-se na secretaria."


def _seguir(client, resposta):
    assert resposta.status_code == 302
    return client.get(resposta["Location"]).content.decode()


def _campos_da_conferencia(pagina):
    """Os campos do formulário da conferência, como o navegador os enviaria."""
    bloco = pagina.split('id="conferir-o-texto"', 1)[1].split("</section>", 1)[0]
    campos = dict(re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]*)"', bloco))
    texto = re.search(r"<textarea[^>]*name=\"([^\"]+)\"[^>]*>(.*?)</textarea>", bloco, re.S)
    campos[texto.group(1)] = texto.group(2)
    acao = re.search(r'<form method="post" action="([^"]+)"', bloco).group(1)
    return acao, {chave: valor.replace("&amp;", "&") for chave, valor in campos.items()}


def test_cada_campo_diz_que_o_texto_chega_ao_candidato(client, seletor_ligado, cenario_da_tela):
    """FR-3991, FR-3992, SC-1205: visível, ligado ao campo, e fora de bloco de ajuda escondido."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)

    for campo in ("complemento-titulares", "complemento-individual"):
        descricao = re.search(rf'id="{campo}"[^>]*aria-describedby="([^"]+)"', pagina).group(1)
        assert re.search(rf'id="{descricao}"[^>]*><strong>{AVISO}</strong>', pagina), campo
    assert "O candidato lerá este fundamento" in pagina


def test_sem_complemento_o_gesto_e_direto_como_hoje(client, seletor_ligado, cenario_da_tela):
    """D-004: sem texto digitado, nada a conferir — o derivado já está na tela."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    postar_titulares(client, edital, previa(edital)["assinatura"])

    assert Convocacao.objects.count() == 2


def test_com_complemento_a_previa_vem_antes_e_nao_pratica_nada(
    client, seletor_ligado, cenario_da_tela
):
    """FR-3993, FR-3994, FR-3996: o texto composto e quantas pessoas, sem ato nenhum."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    p = previa(edital)

    pagina = _seguir(
        client, postar_titulares(client, edital, p["assinatura"], complemento=COMPLEMENTO)
    )

    assert Convocacao.objects.count() == 0
    assert "Conferir o texto" in pagina
    assert f"{p['fundamento']} Complemento: {COMPLEMENTO}" in pagina
    assert "Este texto será mostrado a 2 pessoas." in pagina
    assert "Convocar as 2" in pagina


def test_confirmada_a_previa_o_candidato_le_o_mesmo_texto(client, seletor_ligado, cenario_da_tela):
    """SC-1206, SC-1207: o texto gravado é o da prévia, e são tantos atos quanto ela disse."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    p = previa(edital)
    pagina = _seguir(
        client, postar_titulares(client, edital, p["assinatura"], complemento=COMPLEMENTO)
    )
    acao, campos = _campos_da_conferencia(pagina)

    client.post(acao, {**campos, "etapa": "confirmar"})

    gravados = list(Convocacao.objects.values_list("fundamento", flat=True))
    assert len(gravados) == 2
    assert set(gravados) == {f"{p['fundamento']} Complemento: {COMPLEMENTO}"}


def test_texto_editado_na_previa_volta_a_previa(client, seletor_ligado, cenario_da_tela):
    """R-006: a prévia assina o texto; o editado e confirmado direto volta, sem ato."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    pagina = _seguir(
        client,
        postar_titulares(client, edital, previa(edital)["assinatura"], complemento=COMPLEMENTO),
    )
    acao, campos = _campos_da_conferencia(pagina)

    resposta = client.post(acao, {**campos, "complemento": "Outro texto.", "etapa": "confirmar"})
    pagina = _seguir(client, resposta)

    assert Convocacao.objects.count() == 0
    assert "O texto mudou desde a prévia" in pagina
    assert "Complemento: Outro texto." in pagina


def test_a_volta_preserva_o_que_foi_preenchido(client, seletor_ligado, cenario_da_tela):
    """FR-3995: o texto volta editável, e o vencimento e o alcance viajam nos campos."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    p = previa(edital)
    pagina = _seguir(
        client, postar_titulares(client, edital, p["assinatura"], complemento=COMPLEMENTO)
    )

    _, campos = _campos_da_conferencia(pagina)

    assert campos["complemento"] == COMPLEMENTO
    assert campos["vencimento"] == VENCIMENTO
    assert campos["alcance"] == p["assinatura"]
    assert campos["chave"] == "tela-titulares"


def test_o_desfecho_passa_sempre_pela_previa(client, seletor_ligado, cenario_da_tela, gestor):
    """O fundamento do desfecho é obrigatório e chega ao candidato: a conferência é sempre."""
    from tests.fixtures.convocacao import convocar

    edital, _, _ = cenario_da_tela
    convocada = convocar(edital, gestor, previa(edital)["pessoas"][0]["id"], idempotency_key="d")
    identificar(client, "carlos", ["gestor"])
    url = reverse("interface:desfechar", args=[edital.id, MARCO, convocada["id"]])

    pagina = _seguir(
        client,
        client.post(
            url,
            {
                "especie": "DESISTENCIA_EXPRESSA",
                "fundamento": "Desistiu por escrito.",
                "chave": "k",
            },
        ),
    )

    assert not DesfechoDaConvocacao.objects.exists()
    assert "Desistência registrada — Desistiu por escrito." in pagina
    assert "Este texto será mostrado a 1 pessoa." in pagina
    acao, campos = _campos_da_conferencia(pagina)
    client.post(acao, {**campos, "etapa": "confirmar"})
    assert DesfechoDaConvocacao.objects.get().fundamento == "Desistiu por escrito."


def test_a_chamada_individual_com_complemento_tambem_confere(
    client, seletor_ligado, cenario_da_tela
):
    """O fundamento da espécie derivada, seguido do complemento, para 1 pessoa."""
    from processo_seletivo.convocacao.application import fluxo

    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    pessoa = previa(edital)["pessoas"][0]["id"]
    leitura = fluxo.selectors.leitura_do_recorte(edital=edital, perfil_id=_perfil(), marco_id=MARCO)
    derivado = fluxo.fundamentos_por_especie(
        edital=edital, perfil_id=_perfil(), lista_id=None, apuracao=leitura["apuracao"]
    )["VAGA_INICIAL"]

    pagina = _seguir(
        client,
        client.post(
            reverse("interface:convocar", args=[edital.id, MARCO]),
            {
                "inscricao": pessoa,
                "vencimento": VENCIMENTO,
                "chave": "individual-125",
                "complemento": COMPLEMENTO,
            },
        ),
    )

    assert Convocacao.objects.count() == 0
    assert f"{derivado} Complemento: {COMPLEMENTO}" in pagina
    assert "Este texto será mostrado a 1 pessoa." in pagina
    acao, campos = _campos_da_conferencia(pagina)
    client.post(acao, {**campos, "etapa": "confirmar"})
    assert Convocacao.objects.get().fundamento == f"{derivado} Complemento: {COMPLEMENTO}"


def _perfil():
    from tests.fixtures.edital import PROFILE_ID

    return PROFILE_ID
