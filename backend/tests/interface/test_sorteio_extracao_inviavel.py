"""A tela do sorteio avisa antes de congelar a relação que nunca sortearia (102, FR-2658–FR-2661).

**Por que a tela, se a publicação já recusa.** A publicação recusa o Edital novo; o Edital publicado
antes desta feature, e o que uma Retificação condenou — prorrogando as inscrições, ou trazendo a
extração para o dia do fim —, chegam à tela do sorteio no estado do 72/2026. O congelamento é ato
append-only: o aviso é a última chance.

**O caminho é o real.** O Edital nasce viável e publica; a Retificação, que só adverte, o leva ao
estado. Publicar já condenado não é caminho: a publicação o recusa (cenário 1 do quickstart).
"""

import copy
from datetime import datetime, time, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from tests.fixtures.publicacao import encerrar_inscricoes, retify
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

AVISO = "o sorteio seria recusado."
DIAGNOSTICO = "Esta relação não pode ser sorteada com a extração do Edital."
RETIFICADO = (
    "A extração já foi trocada por Retificação, mas esta relação continua presa à extração antiga."
)
BOTAO = "Publicar e congelar a relação"


def _amanha():
    """A data pronta que o aviso e o diagnóstico dão: o dia seguinte a um congelamento hoje."""
    return (timezone.localdate(timezone.now(), ZONA) + timedelta(days=1)).strftime("%d/%m/%Y")


def _hoje(hora, minuto=0):
    return datetime.combine(timezone.localdate(timezone.now(), ZONA), time(hora, minuto), ZONA)


def _certame(gestor, api_client, manager_headers, process_payload, *, fonte="Loteria Federal"):
    """Inscrições correndo até depois de amanhã, e a extração para daqui a cinco dias: viável."""
    metodo = copy.deepcopy(METODO)
    metodo.update(
        {
            "source": fonte,
            "occurrence": "6113",
            "occurrenceAt": (timezone.now() + timedelta(days=5)).astimezone(ZONA).isoformat(),
        }
    )
    return certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo, periodo_aberto=True
    )


def _retificar_a_extracao(api_client, certame, instante, *, suffix):
    conteudo = (
        VersaoConsolidada.objects.filter(edital=certame["edital"]).latest("materialized_at").content
    )
    perfil = conteudo["profiles"][0]
    marco = next(
        m for m in perfil["classificationMilestones"] if str(m["id"]) == str(certame["marco"])
    )
    retify(
        api_client,
        certame["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={perfil['id']}/classificationMilestones/id={marco['id']}"
                    "/drawMethod/occurrenceAt"
                ),
                "operation": "REPLACE",
                "newValue": instante.isoformat(),
            }
        ],
        suffix=suffix,
    )


def _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload, **op):
    certame = _certame(gestor, api_client, manager_headers, process_payload, **op)
    encerrar_inscricoes(api_client, certame["edital"], timezone.now() - timedelta(minutes=1))
    _retificar_a_extracao(api_client, certame, _hoje(0, 1), suffix="hoje")
    return certame


def _abrir(client, certame, papeis=()):
    identificar(client, "maria", list(papeis))
    resposta = client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    )
    assert resposta.status_code == 200
    # O template quebra a prosa em linhas; quem lê vê espaços, e é isso que se compara.
    return " ".join(resposta.content.decode().split())


def _congelar(certame, *, chave="inviavel-relacao", motivo=""):
    publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key=chave,
        correlation_id="teste-102",
        motivo=motivo,
    )


# --- antes de congelar (FR-2659) ------------------------------------------------------------


def test_com_a_extracao_hoje_o_aviso_vem_antes_do_botao_e_o_botao_continua(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)

    corpo = _abrir(client, certame)

    assert f"Não congele a relação hoje: {AVISO}" in corpo
    assert "A extração do Edital (6113 de Loteria Federal)" in corpo
    assert "essa fonte publica só a data, sem o horário" in corpo
    assert f"trocando a extração por uma a partir de <strong>{_amanha()}</strong>" in corpo
    assert "Congelar não se desfaz." in corpo
    assert BOTAO in corpo, "o congelamento não é recusado por esta regra (D-005)"
    assert corpo.index(AVISO) < corpo.index(BOTAO)


def test_com_as_inscricoes_correndo_ate_o_dia_da_extracao_o_aviso_ja_aparece(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    """FR-2651: agora, sozinho, seria viável; o congelamento mais cedo é o fim das inscrições."""
    certame = _certame(gestor, api_client, manager_headers, process_payload)
    versao = VersaoConsolidada.objects.filter(edital=certame["edital"]).latest("materialized_at")
    fim = datetime.fromisoformat(versao.content["schedule"][0]["endAt"]).astimezone(ZONA)
    _retificar_a_extracao(
        api_client, certame, datetime.combine(fim.date(), time(23, 59), ZONA), suffix="fim"
    )

    corpo = _abrir(client, certame)

    assert "Ainda não é possível publicar a relação." in corpo
    assert f"A extração do Edital é cedo demais: {AVISO}" in corpo
    assert "Antes do fim das inscrições," in corpo
    dia_seguinte_ao_fim = (fim.date() + timedelta(days=1)).strftime("%d/%m/%Y")
    assert f"a partir de <strong>{dia_seguinte_ao_fim}</strong>" in corpo, "a data conta do fim"


def test_a_sucessao_de_uma_relacao_que_sorteia_tambem_e_avisada(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    """A relação congelada sorteia; sucedê-la hoje, com a extração retificada para hoje, não."""
    certame = _certame(gestor, api_client, manager_headers, process_payload)
    encerrar_inscricoes(api_client, certame["edital"], timezone.now() - timedelta(minutes=1))
    _congelar(certame)
    _retificar_a_extracao(api_client, certame, _hoje(0, 1), suffix="hoje")

    corpo = _abrir(client, certame)

    assert DIAGNOSTICO not in corpo, "a relação congelada continua sorteando"
    assert f"Não congele a relação hoje: {AVISO}" in corpo
    assert "Vale também para publicar relação nova, sucedendo a atual" in corpo
    assert corpo.index(AVISO) < corpo.index("Publicar relação nova, sucedendo a atual</button>")


def test_com_a_extracao_depois_do_fim_nao_ha_aviso(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _certame(gestor, api_client, manager_headers, process_payload)
    encerrar_inscricoes(api_client, certame["edital"], timezone.now() - timedelta(minutes=1))

    corpo = _abrir(client, certame)

    assert AVISO not in corpo
    assert BOTAO in corpo


def test_com_a_fonte_que_publica_a_hora_nao_ha_aviso(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    """D-006: a demonstração atual fica fora, e a recusa continua valendo para ela."""
    certame = _encerrado_com_a_extracao_hoje(
        gestor, api_client, manager_headers, process_payload, fonte="Fonte de demonstração"
    )

    assert AVISO not in _abrir(client, certame)


def test_com_a_ocorrencia_substituta_nao_ha_aviso(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    """A substituta não tem instante publicado, e prever o dia dela seria inventar (FR-2659)."""
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)

    class Indisponivel:
        def observar(self, *, fonte, referencia):
            return Observacao(indisponivel=True, evidencia=f"Concurso {referencia}: sem extração.")

    observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte="Loteria Federal",
        referencia="6113",
        idempotency_key="inviavel-indisponivel",
        correlation_id="teste-102",
        fonte_externa=Indisponivel(),
    )

    assert AVISO not in _abrir(client, certame)


def test_o_link_para_a_retificacao_so_aparece_para_quem_retifica(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)
    destino = reverse("interface:retificar", args=[certame["edital"].id])

    sem = _abrir(client, certame)
    com = _abrir(client, certame, ["elaborador"])

    assert "peça a quem elabora as Retificações deste Edital que o retifique" in sem
    assert f'<a href="{destino}">retifique o Edital</a>' in com


# --- a relação já congelada (FR-2660, FR-2661) ----------------------------------------------


def test_a_relacao_congelada_no_dia_da_extracao_recebe_o_diagnostico_e_a_saida(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)
    _congelar(certame)

    corpo = _abrir(client, certame)

    assert DIAGNOSTICO in corpo
    assert "Para sortear, nesta ordem:" in corpo
    assert f"por uma a partir de <strong>{_amanha()}</strong>" in corpo
    passos = [
        "trocando a extração por uma",
        "<li>Publique a relação nova, sucedendo esta",
        "<li>Observe a nova ocorrência e realize o sorteio.",
    ]
    assert all(passo in corpo for passo in passos)
    assert [corpo.index(passo) for passo in passos] == sorted(
        corpo.index(passo) for passo in passos
    ), "a ordem é a da saída: retificar, suceder, observar"
    assert "Publicar a relação nova sem retificar antes não resolve." in corpo
    assert AVISO not in corpo, "não há recorte por congelar, e o aviso de antes não se repete"


def test_depois_de_retificado_o_metodo_falta_suceder_a_relacao(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)
    _congelar(certame)
    _retificar_a_extracao(api_client, certame, _hoje(20, 5) + timedelta(days=1), suffix="amanha")

    corpo = _abrir(client, certame)

    assert RETIFICADO in corpo
    assert "<li>Publique a relação nova, sucedendo esta" in corpo
    assert "também é cedo demais" not in corpo, "a extração nova, amanhã, serve"


def test_se_a_extracao_retificada_tambem_e_cedo_demais_a_tela_avisa_antes_de_suceder(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)
    _congelar(certame)
    _retificar_a_extracao(api_client, certame, _hoje(23, 30), suffix="ainda-hoje")

    corpo = _abrir(client, certame)

    assert RETIFICADO in corpo
    assert "também é cedo demais para uma relação congelada hoje" in corpo
    assert f"para uma extração a partir de {_amanha()}" in corpo


def test_depois_de_sucedida_a_relacao_o_diagnostico_some(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)
    _congelar(certame)
    _retificar_a_extracao(api_client, certame, _hoje(20, 5) + timedelta(days=1), suffix="amanha")
    _congelar(certame, chave="inviavel-sucessora", motivo="Extração retificada para amanhã.")

    corpo = _abrir(client, certame)

    assert DIAGNOSTICO not in corpo
    assert RETIFICADO not in corpo


def test_sem_estilo_nem_script_embutido(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client
):
    """A CSP recusa os dois em silêncio (091, 092): o aviso precisa funcionar só com a folha."""
    certame = _encerrado_com_a_extracao_hoje(gestor, api_client, manager_headers, process_payload)
    _congelar(certame)

    corpo = _abrir(client, certame)

    assert DIAGNOSTICO in corpo
    assert 'style="' not in corpo
    assert "<style" not in corpo
    assert "<script>" not in corpo
    assert "onclick=" not in corpo
