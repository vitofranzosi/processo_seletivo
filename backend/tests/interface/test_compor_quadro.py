"""A seção do quadro de vagas na tela de composição do Perfil (025, US1 e US4).

O que a tela promete: uma seção **dentro** do cartão do Perfil, linhas oferecidas a partir das
Modalidades já declaradas, e só as quantidades digitadas. É o que faz um Edital de sete polos ser
composto sem redigitar rótulo nenhum — e o que separa a US1 de "possível e insuportável".
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import (
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.editais.models.perfis import LinhaDoQuadroDeVagas, PerfilVaga
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


# Identidades por família, e não por sorteio: `2500` é Perfil, `2510` é Modalidade e `2520` é
# linha do quadro. O sufixo é `<sub><indice>`. Famílias separadas porque um identificador repetido
# entre coleções responde 409 `identifier_belongs_to_another_edital` — e a recusa apareceria como
# "a tela não gravou", longe da causa.
def _id(familia, sub=0, indice=0):
    return f"aaaaaaaa-0000-4000-8000-{familia}0000{sub:02d}{indice:02d}"


PERFIL = _id("2500")

# As três Modalidades do Perfil, na ordem em que a tela as desenha.
MODALIDADES = (
    ("AC", "Ampla concorrência"),
    ("PCD", "Pessoa com deficiência"),
    ("PPI", "Pretos, pardos e indígenas"),
)


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def perfil(indice=0, total="80", quantidades=("56", "4", "20"), **extras):
    """Um Perfil com três Modalidades e as quatro quantidades do quadro — nada mais.

    A tela oferece **quatro** linhas: a geral e uma por Modalidade. A da "Ampla concorrência" vai
    em branco, que é o que a D-004 manda — o número dela mora na linha geral, e em branco não grava
    linha nenhuma.
    """
    campos = {
        f"perfil-{indice}-id": _id("2500", indice=indice),
        f"perfil-{indice}-code": f"C{indice + 1}",
        f"perfil-{indice}-name": f"Curso {indice + 1}",
        f"perfil-{indice}-immediateVacancies": total,
        f"perfil-{indice}-reserveType": "NONE",
        f"linha-{indice}-0-id": _id("2520", indice=indice),
        f"linha-{indice}-0-modalityId": "",
        f"linha-{indice}-0-immediateVacancies": quantidades[0],
    }
    for sub, (codigo, nome) in enumerate(MODALIDADES):
        modalidade = _id("2510", sub=sub + 1, indice=indice)
        campos[f"modalidade-{indice}-{sub}-id"] = modalidade
        campos[f"modalidade-{indice}-{sub}-code"] = codigo
        campos[f"modalidade-{indice}-{sub}-name"] = nome
        campos[f"linha-{indice}-{sub + 1}-id"] = _id("2520", sub=sub + 1, indice=indice)
        campos[f"linha-{indice}-{sub + 1}-modalityId"] = modalidade
        campos[f"linha-{indice}-{sub + 1}-immediateVacancies"] = (
            "" if codigo == "AC" else quantidades[sub]
        )
    return {**campos, **extras}


def compor(client, edital, dados):
    return client.post(reverse("interface:compor-etapa", args=[edital.id, "perfis"]), dados)


def tela(client, edital):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "perfis"]))
    assert resposta.status_code == 200
    return resposta.content.decode()


@pytest.fixture
def composto(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, perfil())
    assert resposta.status_code == 302, resposta.content
    return edital


def secao_do_quadro(corpo, indice=0):
    """O trecho da seção do quadro daquele Perfil, e nada além dele."""
    inicio = corpo.index(f'<h3 id="quadro-titulo-{indice}">')
    return corpo[inicio : corpo.index("</section>", inicio)]


# --- T018 · a seção mora dentro do cartão do Perfil (UX-020) ---------------------------------


def test_o_quadro_e_secao_do_cartao_do_perfil_e_nao_tela_a_parte(client, seletor_ligado, composto):
    """Tela à parte seria mais fácil de escrever e destruiria o que a outra tivesse gravado.

    O rascunho é substituído inteiro a cada POST: duas telas gravando Perfis significa a segunda
    apagando a primeira. Na mesma seção e no mesmo envio, o problema não existe (UX-020).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = tela(client, composto)

    cartao = corpo[corpo.index('class="linha perfil"') :]
    cartao = cartao[: cartao.index("Remover este Perfil")]
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in cartao, (
        "o quadro é seção do cartão do Perfil, e vem antes do fim dele"
    )

    # E o quadro não tem passo próprio no assistente: ele não é etapa, é seção.
    from processo_seletivo.interface.views import CHAVES_ETAPA

    assert "quadro" not in CHAVES_ETAPA


# --- T019 · só quantidades são digitadas (UX-021, SC-048) -----------------------------------


def test_so_as_quantidades_sao_digitaveis_na_secao_do_quadro(client, seletor_ligado, composto):
    """Quatro números, e nenhum rótulo, código ou denominação redigitado (SC-048)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    editaveis = re.findall(r'<input type="(?!hidden)[^"]*"[^>]*name="(linha-[^"]+)"', quadro)
    assert len(editaveis) == 4, editaveis
    assert all(nome.endswith("-immediateVacancies") for nome in editaveis)

    # Os rótulos aparecem como **texto**, e não como campo: nada neles é redigitável.
    assert "Pessoa com deficiência (PCD)" in quadro
    assert "Pretos, pardos e indígenas (PPI)" in quadro
    ocultos = re.findall(r'<input type="hidden"[^>]*name="(linha-[^"]+)"', quadro)
    assert {nome.rsplit("-", 1)[1] for nome in ocultos} == {"id", "modalityId"}


# --- T020 · a linha geral é distinguível sem cor (UX-022) -----------------------------------


def test_a_linha_geral_e_distinguivel_sem_cor_e_diz_que_e_a_da_ampla_concorrencia(
    client, seletor_ligado, composto
):
    """Sem depender de cor: o texto do próprio rótulo, e peso tipográfico — não uma pastilha."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    assert "<strong>Ampla concorrência</strong>" in quadro
    assert "Esta é a linha" in quadro and "ampla concorrência" in quadro
    # A distinção não é de cor: a linha geral não ganha classe de cor nenhuma.
    primeira = quadro[: quadro.index("</div>")]
    assert 'class="linha-do-quadro"' in primeira


# --- T021 · quantidade em branco não grava linha (FR-159, D-006) ----------------------------


def test_quantidade_em_branco_nao_grava_linha_e_ausencia_nao_vira_zero(composto):
    """A Modalidade "Ampla concorrência" foi oferecida e deixada em branco (D-004)."""
    perfil_gravado = PerfilVaga.objects.get(pk=PERFIL)
    linhas = list(perfil_gravado.quadro_de_vagas.all())

    assert [
        (str(linha.modalidade_id) if linha.modalidade_id else None, linha.vagas_imediatas)
        for linha in linhas
    ] == [
        (None, 56),
        (_id("2510", sub=2), 4),
        (_id("2510", sub=3), 20),
    ]
    assert not perfil_gravado.quadro_de_vagas.filter(modalidade_id=_id("2510", sub=1)).exists()


def test_o_quadro_gravado_volta_a_tela_com_as_quantidades(client, seletor_ligado, composto):
    """Travessia 3 de 4: sem a reexibição, a gravação seguinte apagaria o que já estava lá."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    valores = re.findall(r'name="linha-0-\d+-immediateVacancies"\s+value="([^"]*)"', quadro)
    assert valores == ["56", "", "4", "20"]


# --- A recusa da soma chega ancorada na linha, com os três números (UX-023) ------------------


def test_a_divergencia_da_soma_e_dita_em_numeros_na_submissao(client, seletor_ligado, composto):
    """A conferência é da submissão, e não da gravação: o rascunho aceita o quadro que não fecha.

    Recusá-lo na gravação impediria salvar o trabalho pela metade, que é o que compor um Edital de
    sete polos exige. Quem recusa é quem publica — e diz os três números (FR-161, UX-023, SC-054).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, composto, perfil(quantidades=("55", "4", "20")))
    assert resposta.status_code == 302, "o rascunho aceita o quadro que ainda não fecha"

    composto.refresh_from_db()
    achados = [
        item
        for item in blocking_findings(validate_for_publication(edital_snapshot(composto)))
        if item.code.startswith("vacancy_")
    ]
    assert [item.code for item in achados] == ["vacancy_sum_mismatch"]
    assert "79" in achados[0].message and "80" in achados[0].message


# --- T074–T076 · o Edital grande (US4) -------------------------------------------------------


def sete_polos():
    dados = {}
    for indice in range(7):
        dados.update(perfil(indice=indice))
    return dados


def test_sete_perfis_de_tres_modalidades_pedem_no_maximo_vinte_e_oito_campos(
    client, seletor_ligado, edital
):
    """7 × (1 geral + 3 reservadas) = 28, e nenhum campo de rótulo, código ou denominação.

    É a medida da SC-052, e ela está num teste em vez de numa impressão de propósito: a pressão de
    autoria do Edital grande é o que faz a US1 ser possível e insuportável sem a US4.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, sete_polos())
    assert resposta.status_code == 302, resposta.content

    corpo = tela(client, edital)
    editaveis = re.findall(r'<input type="(?!hidden)[^"]*"[^>]*name="(linha-[^"]+)"', corpo)
    assert len(editaveis) == 28, len(editaveis)
    assert all(nome.endswith("-immediateVacancies") for nome in editaveis)


def test_os_sete_quadros_sao_gravados_numa_submissao_so(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, sete_polos())
    assert resposta.status_code == 302, resposta.content

    assert LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).count() == 21
    assert (
        sum(
            linha.vagas_imediatas
            for linha in LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital)
        )
        == 7 * 80
    )


def test_uma_quantidade_em_branco_entre_sete_perfis_apaga_so_aquela_linha(
    client, seletor_ligado, edital
):
    """As outras vinte permanecem: a ausência é daquela linha, e não do quadro (FR-159, D-006)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = sete_polos()
    dados["linha-3-3-immediateVacancies"] = ""
    dados["perfil-3-immediateVacancies"] = "60"
    resposta = compor(client, edital, dados)
    assert resposta.status_code == 302, resposta.content

    assert LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).count() == 20
    do_perfil = LinhaDoQuadroDeVagas.objects.filter(perfil_id=_id("2500", indice=3))
    assert do_perfil.count() == 2
    assert not do_perfil.filter(modalidade_id=_id("2510", sub=3, indice=3)).exists()
