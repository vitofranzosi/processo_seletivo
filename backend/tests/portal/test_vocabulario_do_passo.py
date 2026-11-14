"""A varredura do vocabulário do passo, nas telas do candidato (168, FR-7330 a FR-7332; SC-2411).

**A lista é literal, e tela nova escapa dela em silêncio.** Aqui entram o degrau do acompanhamento,
em todos os estados, com e sem a chave do vídeo, e as páginas da gravação e do comprovante da `166`,
que nenhuma varredura lia. Toda tela nova do candidato desta feature entra em `TELAS` no mesmo
commit.

**A Etapa tem nome neutro** (FR-7332): a fixture da `163` a chama "Heteroidentificação", e o nome
publicado é dado, e não texto fixo (Q-2). Com ele na página, a varredura acusaria o Edital, e não a
tela; aqui o nome e os rótulos do desfecho são os que o Edital do Ifes usaria.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures.deliberacao import concluir_pareceres, distribuir_na_hetero, montar_colegiada
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.verificacao import enviar_video, rascunho_com_video
from tests.portal.test_vocabulario_das_telas_publicas import visivel

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

#: Os termos da tabela de linguagem do estudo (FR-7330), por raiz, sem depender de acento.
PROIBIDOS = {
    r"(?i)heteroidentifica": "o nome normativo fica nas telas da gestão",
    r"(?i)fen[oó]t[ií]p": "a comissão olha só a aparência; o termo técnico assusta",
    r"(?i)aferi[cç][aã]o": "termo técnico",
    r"(?i)indeferid": "o desfavorável, ao candidato, é «não confirmada»",
}

#: As telas do candidato que esta feature varre. Literal, de propósito (FR-7331).
TELAS = (
    "portal/templates/portal/acompanhamento.html",
    "portal/situacao.py",
    "portal/templates/portal/verificacao.html",
    "portal/templates/portal/verificacao_comprovante.html",
)

NOME = "Verificação da autodeclaração"


def _montar(gestor, api_client, manager_headers, *, seed, inicio, fim, video):
    rascunho = rascunho_com_video(seed, inicio=inicio, fim=fim, video=video)
    etapa = rascunho["stages"][1]
    etapa.update(name=NOME, rotuloFavoravel="Confirmada", rotuloDesfavoravel="Não confirmada")
    return montar_colegiada(
        gestor,
        api_client,
        manager_headers,
        seed=seed,
        regra="UNANIMOUS_FOR_FAVORABLE",
        quantas=2,
        rascunho=rascunho,
    )


def termos_em(texto):
    return [
        f"{padrao}: {porque}" for padrao, porque in PROIBIDOS.items() if re.search(padrao, texto)
    ]


def _acompanhamento(client, inscricao):
    entrar_como_titular(client, inscricao)
    return client.get(reverse("portal:acompanhamento", args=[inscricao.id]))


def test_as_telas_da_lista_existem():
    """A lista literal não aponta para arquivo que sumiu — senão ela protegeria o nada."""
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2] / "processo_seletivo"
    assert [tela for tela in TELAS if not (raiz / tela).exists()] == []


@pytest.mark.parametrize("ligada", [True, False])
def test_falta_e_aguarda_o_resultado(gestor, api_client, manager_headers, client, settings, ligada):
    """Um Edital por teste: os identificadores de Modalidade da fixture são fixos."""
    settings.VERIFICACAO_POR_VIDEO = ligada
    agora = timezone.now()
    antes = _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6830 + ligada,
        inicio=agora + timedelta(days=2),
        fim=agora + timedelta(days=4),
        video=False,
    )
    maria, joao = antes["inscricoes"]
    distribuir_na_hetero(antes, gestor, [joao], chave=f"hetero-683{ligada}")
    concluir_pareceres(antes, joao, {"ana": "FAVORAVEL"})
    for estado, inscricao in (("falta", maria), ("aguarda o resultado", joao)):
        pagina = _acompanhamento(client, inscricao)
        assert pagina.status_code == 200, estado
        assert termos_em(visivel(pagina)) == [], estado


@pytest.mark.parametrize("ligada", [True, False])
def test_aguarda_a_comissao(gestor, api_client, manager_headers, client, settings, ligada):
    settings.VERIFICACAO_POR_VIDEO = ligada
    agora = timezone.now()
    vencido = _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6832 + ligada,
        inicio=agora - timedelta(days=4),
        fim=agora - timedelta(days=1),
        video=False,
    )
    pagina = _acompanhamento(client, vencido["inscricoes"][0])
    assert pagina.status_code == 200
    assert "Aguardando a comissão" in visivel(pagina)
    assert termos_em(visivel(pagina)) == []


def test_o_degrau_e_as_paginas_do_video(
    raiz_de_arquivos, gestor, api_client, manager_headers, client
):
    """Com a chave ligada (o padrão da suíte): poder gravar, gravação, enviado e comprovante."""
    agora = timezone.now()
    cenario = _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6834,
        inicio=agora - timedelta(days=1),
        fim=agora + timedelta(days=1),
        video=True,
    )
    maria, joao = cenario["inscricoes"]
    enviar_video(joao, cenario["hetero"])
    entrar_como_titular(client, maria)
    paginas = [
        client.get(reverse("portal:acompanhamento", args=[maria.id])),
        client.get(reverse("portal:verificacao", args=[maria.id, cenario["hetero"]])),
    ]
    entrar_como_titular(client, joao)
    paginas += [
        client.get(reverse("portal:acompanhamento", args=[joao.id])),
        client.get(reverse("portal:verificacao-comprovante", args=[joao.id, cenario["hetero"]])),
    ]
    for pagina in paginas:
        assert pagina.status_code == 200
        assert termos_em(visivel(pagina)) == []
