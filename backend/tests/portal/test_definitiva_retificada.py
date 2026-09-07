"""A definitiva que corrige outra — apresentada pela **causa**, e sem natureza nova.

`DEFINITIVA_RETIFICADA` seria um terceiro valor no enum: três pares a decidir na regra de não
regressão, mais um valor em `uq_publicacao_por_ato_natureza`, e toda leitura de natureza mudando —
tudo para dizer o que a cadeia já diz. Vigência e natureza **derivam da cadeia**, e não de estado
duplicado (FR-087).

E a publicação vigente passa a dizer que é a vigente. Antes, só a sucedida dizia algo sobre a
cadeia: quem abria a vigente não tinha como saber se estava lendo o que vale ou um histórico — a
oportunidade nº 3 do relatório da E2E-017 (FR-090).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, publicar_o_ato
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def retificada(gestor, api_client, manager_headers, process_payload):
    """Uma providência determinada, cumprida por ato citante, e a definitiva publicada sobre ele."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=129, codigo="0829"
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato corrigindo o critério de desempate.",
        idempotency_key="providencia-retificada",
    )
    cenario = peca["cenario"]
    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-retificada",
        motivo="Cumprimento da decisão.",
        decisoes=[str(decisao.id)],
    )
    nova = publicar_o_ato(
        cenario,
        natureza="DEFINITIVA",
        chave="publicar-retificada",
        ato=citante,
        declaracao="O prazo recursal encerrou-se sem interposição.",
    )
    return {**peca, "decisao": decisao, "nova": nova}


def abrir(client, publicacao):
    resposta = client.get(reverse("portal:resultado", args=[publicacao.id]))
    assert resposta.status_code == 200
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def test_a_natureza_continua_sendo_uma_das_duas(retificada):
    """Nenhum valor novo no enum — a causa é derivada, e não gravada (FR-087)."""
    assert retificada["nova"].natureza == "DEFINITIVA"
    assert set(PublicacaoResultado.objects.values_list("natureza", flat=True)) <= {
        "PRELIMINAR",
        "DEFINITIVA",
    }


def test_a_definitiva_que_corrige_e_apresentada_pela_causa(client, retificada):
    """ "Retificado em razão do julgamento do recurso X" — o fato, e não um rótulo (FR-088)."""
    corpo = abrir(client, retificada["nova"])

    assert "retificado em" in corpo.lower()
    assert retificada["recurso"].protocolo in corpo
    assert "DEFINITIVA_RETIFICADA" not in corpo


def test_a_vigente_diz_que_e_a_vigente(client, retificada):
    """Quem abre a vigente precisa saber que está lendo o que vale (FR-090)."""
    corpo = abrir(client, retificada["nova"])

    assert "Este é o resultado vigente deste marco." in corpo


def test_a_sucedida_continua_dizendo_que_foi_sucedida(client, retificada):
    """A cadeia responde nas duas pontas, e o endereço da sucedida continua respondendo."""
    corpo = abrir(client, retificada["publicacao"])

    assert "foi sucedido" in corpo
    assert "Este é o resultado vigente deste marco." not in corpo


def test_a_primeira_publicacao_do_marco_nao_diz_que_corrige(
    client, gestor, api_client, manager_headers, process_payload
):
    """Sem publicação anterior não há o que corrigir — e o aviso não pode aparecer sempre."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=130, codigo="0830"
    )

    corpo = abrir(client, peca["publicacao"])

    assert "retificado em" not in corpo.lower()
    assert "Este é o resultado vigente deste marco." in corpo


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")


@pytest.fixture
def corrigida(gestor, api_client, manager_headers, process_payload):
    """A correção fixada — a espécie que **não** cita decisão e mesmo assim retifica a divulgação.

    A caminhada da T125 chegou aqui pela porta da frente: recurso deferido com correção fixada, ato
    sucessor emitido, definitiva publicada sobre ele — e a página dizia só "Resultado definitivo".
    A causa era derivada da `CitacaoDeDecisao`, que só a providência a jusante produz; a correção
    fixada e a reavaliação determinada corrigem o resultado sem citar nada, e a retificação delas
    ficava anônima.
    """
    from decimal import Decimal

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=131, codigo="0831"
    )
    cenario = peca["cenario"]
    alvo = ResultadoEtapa.vigentes.get(
        inscricao=peca["recurso"].inscricao, etapa_id=cenario["etapa"]
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="O documento juntado na inscrição não foi considerado.",
        etapa_id=str(cenario["etapa"]),
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(alvo.id),
        idempotency_key="correcao-retificada",
    )
    sucessor = emitir(
        cenario,
        _gestor(),
        chave="emitir-corrigida",
        motivo="Cumprimento da decisão que corrigiu a pontuação.",
    )
    nova = publicar_o_ato(
        cenario,
        natureza="DEFINITIVA",
        chave="publicar-corrigida",
        ato=sucessor,
        declaracao="O prazo recursal encerrou-se sem interposição.",
    )
    return {**peca, "decisao": decisao, "nova": nova}


def test_a_correcao_fixada_tambem_apresenta_a_causa(client, corrigida):
    """FR-088 não fala em citação: fala na **decisão que motivou**, qualquer que seja a espécie."""
    corpo = abrir(client, corrigida["nova"])

    assert "retificado em" in corpo.lower()
    assert corrigida["recurso"].protocolo in corpo


def test_a_causa_aparece_tambem_no_documento(retificada):
    """FR-088 diz "na página **e no documento**" — e o documento calava (T125).

    Os dois leem os mesmos bytes, e é daí que vem a correspondência entre eles (FR-064): a causa é
    decidida no ato de publicar e congelada no conteúdo, não derivada de novo na renderização.
    """
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(retificada["nova"].documento.bytes)

    assert "RETIFICAÇÃO" in texto
    assert retificada["recurso"].protocolo in texto


def test_a_primeira_divulgacao_nao_traz_a_linha_de_retificacao(retificada):
    """Uma linha "RETIFICAÇÃO" na primeira divulgação afirmaria o que não houve."""
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(retificada["publicacao"].documento.bytes)

    assert "RETIFICAÇÃO" not in texto
