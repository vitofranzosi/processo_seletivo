"""A seção Barema no cartão da Etapa, e o caminho do barema até o banco (146, T009).

**O que se prende aqui são as travessias** (risco 2 do plano). `replace_draft` apaga e recria as
Etapas a cada gravação, e a `CASCADE` leva os critérios junto: campo que falte num dos caminhos
volta vazio sem aviso — foi assim que a designação do período de inscrições morria no passo
seguinte (E2E17-001), e é o que a `144` evitou para a visibilidade do Evento. O barema tem os
mesmos caminhos: a própria etapa, as etapas seguintes, a recusa, a linha nova e a troca de forma.

O rascunho de partida é o da fixture `com_etapas`, com dois documentos gravados na etapa Inscrição:
"Títulos acadêmicos", pedido a toda inscrição, e uma declaração restrita ao Perfil — a que o barema
não pode usar (D-010).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.etapas import CriterioAvaliacao, EtapaAvaliacao
from tests.interface.conftest import ETAPA_CLASSIFICATORIA, ETAPA_SO_ELIMINATORIA
from tests.interface.test_compor import EVENTO, PERFIL, eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

TITULOS = "aaaaaaaa-0000-4000-8000-000000014601"
DECLARACAO = "aaaaaaaa-0000-4000-8000-000000014602"
DOUTORADO = "aaaaaaaa-0000-4000-8000-000000014611"
ESPECIALIZACAO = "aaaaaaaa-0000-4000-8000-000000014612"
ENTREVISTA = "aaaaaaaa-0000-4000-8000-000000014613"


def documentos(**ajustes):
    base = {
        "periodo-inscricoes": EVENTO,
        "documento-0-id": TITULOS,
        "documento-0-key": "titulos",
        "documento-0-name": "Títulos acadêmicos",
        "documento-0-order": "1",
        "documento-0-profileId": "",
        "documento-0-modalityId": "",
        "documento-1-id": DECLARACAO,
        "documento-1-key": "declaracao",
        "documento-1-name": "Declaração do Perfil",
        "documento-1-order": "2",
        "documento-1-profileId": PERFIL,
        "documento-1-modalityId": "",
    }
    return {**base, **ajustes}


def etapas(**ajustes):
    """As duas Etapas da fixture, e o barema da primeira: dois por unidade e um direto."""
    base = {
        "etapa-0-id": ETAPA_CLASSIFICATORIA,
        "etapa-0-name": "Prova de Títulos",
        "etapa-0-order": "1",
        "etapa-0-weight": "2",
        "etapa-0-classificatory": "on",
        "etapa-0-scheduleEventId": EVENTO,
        "etapa-0-forma": "PONTUADA",
        # Digitada errada de propósito: com barema, quem decide a máxima é a soma (FR-5203).
        "etapa-0-maximumScore": "999",
        "criterio-etapa-0-0-id": DOUTORADO,
        "criterio-etapa-0-0-order": "1",
        "criterio-etapa-0-0-name": "Diploma de Doutorado",
        "criterio-etapa-0-0-maximumScore": "20",
        "criterio-etapa-0-0-modo": "POR_UNIDADE",
        "criterio-etapa-0-0-pointsPerUnit": "20",
        "criterio-etapa-0-0-unitLabel": "diploma",
        "criterio-etapa-0-0-documentRequirementId": TITULOS,
        "criterio-etapa-0-0-description": "",
        "criterio-etapa-0-1-id": ESPECIALIZACAO,
        "criterio-etapa-0-1-order": "2",
        "criterio-etapa-0-1-name": "Especialização",
        "criterio-etapa-0-1-maximumScore": "10",
        "criterio-etapa-0-1-modo": "POR_UNIDADE",
        "criterio-etapa-0-1-pointsPerUnit": "5",
        "criterio-etapa-0-1-unitLabel": "certificado",
        "criterio-etapa-0-1-documentRequirementId": TITULOS,
        "criterio-etapa-0-1-description": "Na área da Educação.",
        "criterio-etapa-0-2-id": ENTREVISTA,
        "criterio-etapa-0-2-order": "3",
        "criterio-etapa-0-2-name": "Entrevista",
        "criterio-etapa-0-2-maximumScore": "15",
        # A pontuação atribuída descarta o que só a por unidade usa, ainda que tenha sido digitado.
        "criterio-etapa-0-2-modo": "DIRETA",
        "criterio-etapa-0-2-pointsPerUnit": "7",
        "criterio-etapa-0-2-unitLabel": "faixa",
        "criterio-etapa-0-2-documentRequirementId": "",
        "criterio-etapa-0-2-description": "Fracos: 0 a 5; bons: 6 a 10; ótimos: 11 a 15.",
        "etapa-1-id": ETAPA_SO_ELIMINATORIA,
        "etapa-1-name": "Análise documental",
        "etapa-1-order": "2",
        "etapa-1-weight": "1",
        "etapa-1-eliminatory": "on",
        "etapa-1-scheduleEventId": "",
        "etapa-1-forma": "PONTUADA",
    }
    return {**base, **ajustes}


def gravar(client, edital, etapa, dados):
    return client.post(reverse("interface:compor-etapa", args=[edital.id, etapa]), dados)


def barema(edital):
    return [
        (str(c.id), c.nome, c.maxima, c.pontos_por_unidade, c.unidade, c.documento, c.descricao)
        for c in CriterioAvaliacao.objects.filter(etapa__edital=edital).order_by("ordem")
    ]


@pytest.fixture
def com_documentos(client, com_etapas):
    resposta = gravar(client, com_etapas, "inscricao", documentos())
    assert resposta.status_code == 302, resposta.content
    com_etapas.refresh_from_db()
    return com_etapas


@pytest.fixture
def com_barema(client, com_documentos):
    resposta = gravar(client, com_documentos, "etapas", etapas())
    assert resposta.status_code == 302, resposta.content
    com_documentos.refresh_from_db()
    return com_documentos


def pagina(client, edital):
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"])
    ).content.decode()


# --- a gravação (FR-5201, FR-5202, FR-5203, FR-5206) ----------------------------------------------


def test_gravar_persiste_o_barema_na_ordem_do_formulario(com_barema):
    from decimal import Decimal
    from uuid import UUID

    assert barema(com_barema) == [
        (
            DOUTORADO,
            "Diploma de Doutorado",
            Decimal("20"),
            Decimal("20"),
            "diploma",
            UUID(TITULOS),
            "",
        ),
        (
            ESPECIALIZACAO,
            "Especialização",
            Decimal("10"),
            Decimal("5"),
            "certificado",
            UUID(TITULOS),
            "Na área da Educação.",
        ),
        (
            ENTREVISTA,
            "Entrevista",
            Decimal("15"),
            None,
            "",
            None,
            "Fracos: 0 a 5; bons: 6 a 10; ótimos: 11 a 15.",
        ),
    ]


def test_a_maxima_da_etapa_e_a_soma_dos_criterios(com_barema):
    """D-003, FR-5203: o 999 digitado não sobrevive; a máxima é 45."""
    from decimal import Decimal

    assert EtapaAvaliacao.objects.get(id=ETAPA_CLASSIFICATORIA).maximum_score == Decimal("45")


def test_mover_um_criterio_muda_a_ordem_gravada(client, com_barema):
    """`ordenacao.js` reescreve a `order`; a leitura ordena por ela, e não pelo índice."""
    resposta = gravar(
        client,
        com_barema,
        "etapas",
        etapas(**{"criterio-etapa-0-0-order": "3", "criterio-etapa-0-2-order": "1"}),
    )

    assert resposta.status_code == 302, resposta.content
    assert [linha[1] for linha in barema(com_barema)] == [
        "Entrevista",
        "Especialização",
        "Diploma de Doutorado",
    ]


def test_remover_um_criterio_o_tira_e_a_maxima_acompanha(client, com_barema):
    from decimal import Decimal

    dados = {chave: valor for chave, valor in etapas().items() if "-0-1-" not in chave}
    resposta = gravar(client, com_barema, "etapas", dados)

    assert resposta.status_code == 302, resposta.content
    assert [linha[0] for linha in barema(com_barema)] == [DOUTORADO, ENTREVISTA]
    assert EtapaAvaliacao.objects.get(id=ETAPA_CLASSIFICATORIA).maximum_score == Decimal("35")


def test_linha_em_branco_nao_vira_criterio(client, com_documentos):
    """O cartão acrescentado e não preenchido é desistência, e não critério sem nome."""
    resposta = gravar(
        client,
        com_documentos,
        "etapas",
        etapas(
            **{
                "criterio-etapa-0-3-id": "aaaaaaaa-0000-4000-8000-000000014619",
                "criterio-etapa-0-3-order": "4",
                "criterio-etapa-0-3-modo": "POR_UNIDADE",
            }
        ),
    )

    assert resposta.status_code == 302, resposta.content
    assert len(barema(com_documentos)) == 3


# --- a releitura e a prévia (UX-420, UX-421) ------------------------------------------------------


def test_recarregar_mostra_o_barema_a_previa_e_a_maxima_em_leitura(client, com_barema):
    html = pagina(client, com_barema)

    assert 'name="criterio-etapa-0-0-name" maxlength="200"' in html
    assert 'value="Diploma de Doutorado"' in html
    assert "Opcional. Sem barema, a comissão lança o total." in html
    # A prévia que o servidor desenha, com as frases do PDF.
    assert '<td data-rotulo="Pontuação">5 pontos por certificado, até 10</td>' in html
    assert '<td data-rotulo="Pontuação">20 pontos por diploma</td>' in html
    assert '<td data-rotulo="Pontuação">de 0 a 15</td>' in html
    assert "Especialização — Na área da Educação." in html
    assert "data-total-do-barema>45</td>" in html
    # A máxima da Etapa com barema é leitura, com a marca de onde o número vem.
    assert 'name="etapa-0-maximumScore" value="45"' in html
    assert "data-maxima-da-etapa readonly" in html
    assert "data-soma-do-barema>soma dos critérios</span>" in html


def test_a_etapa_sem_barema_continua_com_a_maxima_digitavel(client, com_barema):
    html = pagina(client, com_barema)
    segunda = html.split('name="etapa-1-id"', 1)[1]

    assert 'id="etapa-1-maximumScore"' in segunda
    assert "data-maxima-da-etapa readonly" not in segunda.split("etapa-1-maximumScore", 2)[1][:400]
    assert "data-previa-do-barema hidden" in segunda


def test_a_pontuacao_direta_volta_marcada_como_direta(client, com_barema):
    html = pagina(client, com_barema)

    assert re.search(r'id="criterio-etapa-0-2-modo-direta"[^>]*\bchecked', html)
    assert not re.search(r'id="criterio-etapa-0-2-modo-unidade"[^>]*\bchecked', html)


def test_o_documento_restrito_nao_e_oferecido(client, com_barema):
    """D-010: só o documento pedido a toda inscrição comprova critério."""
    html = pagina(client, com_barema)
    escolha = html.split('id="criterio-etapa-0-0-documentRequirementId"', 1)[1].split("</select>")[
        0
    ]

    assert "Títulos acadêmicos" in escolha
    assert "Declaração do Perfil" not in escolha


def test_a_linha_nova_nasce_com_identidade_e_com_os_documentos_do_edital(client, com_documentos):
    corpo = client.get(
        reverse("interface:fragmento-criterio-de-avaliacao", args=[com_documentos.id, "0"]),
        {"indice": "7"},
    ).content.decode()

    assert 'name="criterio-etapa-0-7-id" value="' in corpo
    assert 'name="criterio-etapa-0-7-order" value="8"' in corpo
    assert "criterio-de-avaliacao-novo" in corpo
    assert "Títulos acadêmicos" in corpo
    assert "Declaração do Perfil" not in corpo
    assert re.search(r'value="POR_UNIDADE"[^>]*\bchecked', corpo), "a linha nova nasce por unidade"


def test_a_linha_nova_de_outro_edital_e_404(client, com_documentos):
    from uuid import uuid4

    resposta = client.get(reverse("interface:fragmento-criterio-de-avaliacao", args=[uuid4(), "0"]))

    assert resposta.status_code == 404


# --- as travessias (risco 2, FR-5213) -------------------------------------------------------------


@pytest.mark.parametrize(
    ("etapa", "dados"),
    [
        ("identificacao", {"title": "Outro título", "description": "Qualquer."}),
        ("perfis", None),
        ("cronograma", None),
        ("inscricao", None),
    ],
)
def test_gravar_outra_etapa_preserva_o_barema(client, com_barema, etapa, dados):
    """O barema de `etapas_persistidas`: sem ele, gravar os Perfis apagaria a ficha."""
    from tests.interface.conftest import FATO_DO_DESEMPATE

    formularios = {
        "perfis": perfis(
            **{
                "fato-0-0-id": FATO_DO_DESEMPATE,
                "fato-0-0-code": "EXPERIENCIA",
                "fato-0-0-label": "Meses de experiência em EaD",
                "fato-0-0-type": "INTEIRO",
            }
        ),
        "cronograma": eventos(),
        "inscricao": documentos(),
    }
    antes = barema(com_barema)
    assert len(antes) == 3

    resposta = gravar(client, com_barema, etapa, dados or formularios[etapa])

    assert resposta.status_code in (200, 302), resposta.content
    assert barema(com_barema) == antes


def test_remover_o_documento_desfaz_o_vinculo_e_o_criterio_continua(client, com_barema):
    """Caso-limite: o critério é da Etapa; o documento é só a comprovação esperada."""
    sem_titulos = {
        chave.replace("documento-1-", "documento-0-"): valor
        for chave, valor in documentos().items()
        if not chave.startswith("documento-0-")
    }
    resposta = gravar(client, com_barema, "inscricao", sem_titulos)

    assert resposta.status_code == 302, resposta.content
    assert [(linha[1], linha[5]) for linha in barema(com_barema)] == [
        ("Diploma de Doutorado", None),
        ("Especialização", None),
        ("Entrevista", None),
    ]


def test_restringir_o_documento_ligado_e_recusado_na_inscricao(client, com_barema):
    """SC-1634: a restrição chega depois do vínculo, pela edição do próprio documento."""
    antes = barema(com_barema)
    resposta = gravar(
        client, com_barema, "inscricao", documentos(**{"documento-0-profileId": PERFIL})
    )

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "não é pedido a toda inscrição" in html
    assert "«Títulos acadêmicos»" in html
    assert barema(com_barema) == antes, "nada gravado na recusa"


# --- a recusa (FR-033, FR-5204, FR-5205) ----------------------------------------------------------


def test_recusa_reexibe_o_digitado_e_ancora_no_campo(client, com_documentos):
    resposta = gravar(
        client,
        com_documentos,
        "etapas",
        etapas(**{"criterio-etapa-0-0-pointsPerUnit": "25"}),
    )

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "uma unidade só já passaria do teto" in html
    assert 'href="#criterio-etapa-0-0-pointsPerUnit"' in html
    assert 'id="recusa-criterio-etapa-0-0-pointsPerUnit"' in html
    assert 'value="25"' in html
    assert 'value="Na área da Educação."' not in html, "a descrição é caixa de texto"
    assert "Na área da Educação." in html
    assert barema(com_documentos) == [], "nada gravado na recusa"


def test_documento_restrito_forjado_e_recusado(client, com_documentos):
    resposta = gravar(
        client,
        com_documentos,
        "etapas",
        etapas(**{"criterio-etapa-0-0-documentRequirementId": DECLARACAO}),
    )

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "não é pedido a toda inscrição" in html
    assert 'href="#criterio-etapa-0-0-documentRequirementId"' in html
    # O ligado que deixou de valer continua na lista, marcado, para a pessoa saber o que trocar.
    assert "Declaração do Perfil (não é pedido a toda inscrição)" in html


def test_nome_repetido_e_recusado_no_segundo(client, com_documentos):
    resposta = gravar(
        client,
        com_documentos,
        "etapas",
        etapas(**{"criterio-etapa-0-1-name": "Diploma de Doutorado"}),
    )

    assert resposta.status_code == 200
    assert 'href="#criterio-etapa-0-1-name"' in resposta.content.decode()


def test_trocar_para_decisoria_descarta_o_barema(client, com_barema):
    """FR-5204: a decisória não tem barema — a tela esconde a seção, e a leitura a descarta."""
    resposta = gravar(
        client,
        com_barema,
        "etapas",
        etapas(
            **{
                "etapa-0-forma": "DECISORIA",
                "etapa-0-rotuloFavoravel": "Apto",
                "etapa-0-rotuloDesfavoravel": "Inapto",
                "etapa-0-eliminatoryDecisoria": "on",
                "etapa-0-caraterPorForma": "1",
            }
        ),
    )

    assert resposta.status_code == 302, resposta.content
    etapa = EtapaAvaliacao.objects.get(id=ETAPA_CLASSIFICATORIA)
    assert etapa.forma == "DECISORIA"
    assert etapa.maximum_score is None
    assert barema(com_barema) == []


def test_a_secao_so_aparece_na_forma_pontuada(client, com_barema):
    """A folha esconde a seção pela forma marcada; a marcação a carrega como `so-pontuada`."""
    html = pagina(client, com_barema)

    assert '<section class="barema so-pontuada" id="etapa-0-criteria"' in html
