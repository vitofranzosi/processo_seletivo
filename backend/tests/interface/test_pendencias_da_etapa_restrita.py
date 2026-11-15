"""As pendências da Etapa restrita no Centro e em Minhas atividades (171, US3; FR-7321 a FR-7328).

O Edital é o da `166` sem o vídeo: a Etapa restrita a `PPI`, colegiada com três pareceres, e o
período no Evento. `maria` preside; `ana`, `bruno` e `carla` dão os pareceres.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.avaliacoes.application.selectors import pendentes_por_membro
from processo_seletivo.interface import andamento as a
from tests.conftest import ator_institucional
from tests.fixtures.avisos import avisar_passo
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    distribuir_na_hetero,
    montar_colegiada,
)
from tests.fixtures.verificacao import rascunho_com_video
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PRESIDENCIA = ator_institucional("maria")


def _rascunho(seed, *, inicio, fim, video=False):
    """O Edital da `166` sem o vídeo, com um marco de pontuação que lê a Prova didática.

    O marco da fixture é um sorteio sem Etapa enumerada, e com ele nenhuma Etapa tem efeito no GPS:
    o andamento as põe em "Atenção", sem cobrar nada. Aqui o marco ordena pela Prova, e a Etapa
    restrita, anterior a ela, passa a ser esperada pela progressão — como num Edital do Ifes.
    """
    rascunho = rascunho_com_video(seed, inicio=inicio, fim=fim, video=video)
    prova = rascunho["stages"][2]
    prova["weight"] = "1.0000"
    marco = rascunho["profiles"][0]["classificationMilestones"][0]
    marco.pop("drawMethod", None)
    marco.update(orderProduction="POR_PONTUACAO", stages=[prova["id"]], code="M1", name="Final")
    return rascunho


def _montar(gestor, api_client, manager_headers, *, seed, inicio, fim):
    return montar_colegiada(
        gestor,
        api_client,
        manager_headers,
        seed=seed,
        regra="UNANIMOUS_FOR_FAVORABLE",
        quantas=2,
        rascunho=_rascunho(seed, inicio=inicio, fim=fim),
    )


@pytest.fixture
def no_periodo(gestor, api_client, manager_headers):
    agora = timezone.now()
    return _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6820,
        inicio=agora - timedelta(days=1),
        fim=agora + timedelta(days=3),
    )


@pytest.fixture
def vencido(gestor, api_client, manager_headers):
    agora = timezone.now()
    return _montar(
        gestor,
        api_client,
        manager_headers,
        seed=6821,
        inicio=agora - timedelta(days=5),
        fim=agora - timedelta(days=1),
    )


def _da_etapa(cenario, ator=PRESIDENCIA):
    andamento = a.do_edital(cenario["edital"], ator)
    return [
        p for p in andamento.providencias if (p.chave or ())[:2] == ("etapa", cenario["hetero"])
    ]


def _por_natureza(providencias, natureza):
    return [p for p in providencias if p.natureza == natureza]


def test_os_pareceres_que_faltam_por_membro_sem_sentido(no_periodo, gestor):
    """FR-7321, UX-793, SC-2413: nome e contagem, em ordem decrescente, e igual à Mesa."""
    maria, joao = no_periodo["inscricoes"]
    distribuir_na_hetero(no_periodo, gestor, [maria, joao], chave="hetero-6820")
    concluir_pareceres(no_periodo, maria, {"ana": "DESFAVORAVEL", "bruno": "FAVORAVEL"})
    concluir_pareceres(no_periodo, joao, {"ana": "FAVORAVEL"})
    (avaliar,) = _por_natureza(_da_etapa(no_periodo), a.AVALIAR)
    assert avaliar.ato == "Avaliar 2 inscrições distribuídas; faltam 3 pareceres: carla 2, bruno 1"
    assert avaliar.ate is not None
    for sentido in ("favor", "desfavor", "deferid", "indeferid"):
        assert sentido not in avaliar.ato.lower()
    # A mesma conta da Mesa: Atribuição ativa de participante, menos a concluída.
    assert pendentes_por_membro(
        edital=no_periodo["edital"],
        etapa_id=no_periodo["hetero"],
        participantes=[maria.id, joao.id],
    ) == [("carla", 2), ("bruno", 1)]


def test_avisar_ate_o_fim_do_periodo(no_periodo):
    """FR-7323: a pendência leva à confirmação do aviso, e some depois de avisar."""
    (avisar,) = _por_natureza(_da_etapa(no_periodo), a.AVISAR)
    assert avisar.ato == "Avisar 2 inscrições sobre Heteroidentificação"
    assert avisar.responsavel == a.CONDUZ
    assert avisar.url == reverse(
        "interface:aviso-do-passo", args=[no_periodo["edital"].id, no_periodo["hetero"]]
    )
    avisar_passo(no_periodo["edital"], no_periodo["hetero"])
    assert _por_natureza(_da_etapa(no_periodo), a.AVISAR) == []


def test_o_periodo_vencido_sem_nada_registrado(vencido):
    """FR-7324: a presidência registra a ausência ou os pareceres, pela distribuição."""
    da_etapa = _da_etapa(vencido)
    assert _por_natureza(da_etapa, a.AVISAR) == []
    (registrar,) = [p for p in da_etapa if p.ato.startswith("Registrar a ausência")]
    assert registrar.ato == "Registrar a ausência ou os pareceres de 2 inscrições"
    assert registrar.nota.startswith("o período terminou em ")
    assert registrar.url == reverse(
        "interface:distribuicao", args=[vencido["edital"].id, vencido["hetero"]]
    )


def test_quem_nao_conduz_nao_ve_de_quem_falta(no_periodo, gestor):
    """FR-7321: a contagem por membro é da presidência."""
    distribuir_na_hetero(no_periodo, gestor, no_periodo["inscricoes"], chave="hetero-6820-b")
    ana = ator_institucional("ana")
    andamento = a.do_edital(no_periodo["edital"], ana)
    assert not [p for p in andamento.providencias if "faltam" in p.ato]
    assert not [p for p in andamento.providencias if p.natureza == a.AVISAR]


def test_a_linha_de_avaliar_traz_o_prazo(no_periodo, gestor, client, seletor_ligado):
    """FR-7326: "até dd/mm" na linha de quem avalia, em Minhas atividades."""
    distribuir_na_hetero(no_periodo, gestor, no_periodo["inscricoes"], chave="hetero-6820-c")
    identificar(client, "carla", [])
    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()
    fim = timezone.localtime(timezone.now() + timedelta(days=3))
    assert "Avaliar 2 inscrições" in corpo
    assert f"até {fim:%d/%m/%Y}" in corpo


def test_o_centro_mostra_a_etapa_e_o_aviso(no_periodo, client, seletor_ligado):
    """FR-7322, FR-7329: na tela que já existe, e sem página nova."""
    identificar(client, "maria", [])
    corpo = client.get(
        reverse("interface:centro-do-edital", args=[no_periodo["edital"].id]), follow=True
    ).content.decode()
    assert "Avisar 2 inscrições sobre Heteroidentificação" in corpo
    assert (
        reverse("interface:aviso-do-passo", args=[no_periodo["edital"].id, no_periodo["hetero"]])
        in corpo
    )


def test_com_o_video_quem_ele_nao_confirmou_espera_o_encaminhamento(
    raiz_de_arquivos, gestor, api_client, manager_headers, settings
):
    """FR-7325, US4: «Encaminhar N inscrições à entrevista ao vivo», e não «Consolidar»."""
    from tests.fixtures.verificacao import enviar_video
    from tests.integration.verificacao.test_mesa_e_r11 import pareceres_pelo_video

    agora = timezone.now()
    cenario = montar_colegiada(
        gestor,
        api_client,
        manager_headers,
        seed=6822,
        regra="UNANIMOUS_FOR_FAVORABLE",
        quantas=2,
        rascunho=_rascunho(
            6822, inicio=agora - timedelta(days=1), fim=agora + timedelta(days=1), video=True
        ),
    )
    distribuir_na_hetero(cenario, gestor, cenario["inscricoes"], chave="dist-6822")
    enviar_video(cenario["inscricoes"][0], cenario["hetero"])
    pareceres_pelo_video(
        cenario, {"ana": "FAVORAVEL", "bruno": "DESFAVORAVEL", "carla": "FAVORAVEL"}
    )
    for ligada in (True, False):
        # A chave fecha o portal, e não a Mesa (achado I1 da `166`): a pendência continua.
        settings.VERIFICACAO_POR_VIDEO = ligada
        da_etapa = _da_etapa(cenario)
        (encaminhar,) = [p for p in da_etapa if p.ato.startswith("Encaminhar")]
        assert encaminhar.ato == "Encaminhar 1 inscrição à entrevista ao vivo"
        assert encaminhar.url == reverse(
            "interface:encaminhar-ao-vivo", args=[cenario["edital"].id, cenario["hetero"]]
        )
        assert not [p for p in da_etapa if p.ato.startswith("Consolidar")]


def test_o_membro_institucional_sai_pelo_nome(no_periodo, gestor):
    """FR-7321, UX-793: nunca `pessoa-<uuid>` na contagem por membro."""
    from django.contrib.auth import get_user_model

    from processo_seletivo.avaliacoes.models import Atribuicao
    from processo_seletivo.comissoes.models import MembroComissao

    distribuir_na_hetero(no_periodo, gestor, no_periodo["inscricoes"], chave="hetero-6820-d")
    carla = MembroComissao.objects.get(processo=no_periodo["processo"], identity_subject="carla")
    subject = "pessoa-00000000-0000-4000-8000-000000006820"
    get_user_model().objects.create(username=subject, first_name="Carla Souza")
    MembroComissao.objects.filter(pk=carla.pk).update(identity_subject=subject, display_label="")
    pares = pendentes_por_membro(
        edital=no_periodo["edital"],
        etapa_id=no_periodo["hetero"],
        participantes=[i.id for i in no_periodo["inscricoes"]],
    )
    assert ("Carla Souza", 2) in pares
    assert not [nome for nome, _ in pares if nome.startswith("pessoa-")]
    assert Atribuicao.objects.filter(membro=carla).exists()
