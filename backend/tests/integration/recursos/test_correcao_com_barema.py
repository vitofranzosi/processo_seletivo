"""A correção fixada critério a critério (146, incremento C — T031 a T034).

O quickstart §4: a eliminada com 30 recorre dizendo que a especialização é da área e que a
docência declarada é de 50 meses; quem julga confere a ficha atacada e fixa o detalhamento novo. O
total sai da mesma função da Mesa (D-005), a vedação de piora continua sobre o total, o sucessor
nasce com o detalhamento da decisão, a ordem fica obsoleta como sempre e a reemissão usa o total
novo. Nenhum fluxo novo de recurso: a decisão, o sucessor e a cadeia a jusante são os de sempre.
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application.selectors import estado_do_marco
from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.domain.pejus import PIORA
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.application.selectors import detalhamento_do_resultado
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.barema import (
    criterio_de,
    ficha,
    montar_marco_com_barema,
    pontuar_com_ficha,
    recorrer_do_preliminar,
)
from tests.fixtures.divulgacao import emitir, entrar_como_titular
from tests.fixtures.recursos_us4 import JULGADORA, julgador
from tests.interface.conftest import identificar

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.usefixtures("raiz_de_arquivos"),
]

SEED = 153
#: A eliminada: Mestrado (15), 1 especialização (5), 10 meses (10) — 30, abaixo da mínima de 60.
ATACADA = ficha(SEED, 0, 1, 1, 0, 10)
#: A correção: 2 especializações (10, no teto) e 50 meses (40, no teto) — 65.
CORRIGIDA = ficha(SEED, 0, 1, 2, 0, 50)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    cenario = montar_marco_com_barema(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=SEED,
        codigo="0153",
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    cenario["inscricoes"] = pontuar_com_ficha(
        cenario, gestor, [ficha(SEED, 1, 0, 3, 0, 52), ATACADA], primeiro=1531, sufixo="153"
    )
    return cenario


@pytest.fixture
def peca(cenario, gestor):
    return recorrer_do_preliminar(cenario, gestor, cenario["inscricoes"][1], sufixo="153")


def corrigir(cenario, peca, criterios, *, chave="corrigir-153", pontuacao=None):
    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A especialização é da área, e a declaração comprova 50 meses.",
        etapa_id=cenario["etapa"],
        pontuacao=pontuacao,
        criterios=criterios,
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key=chave,
    )


def test_a_correcao_fixada_grava_o_detalhamento_e_o_sucessor_o_cita(cenario, peca):
    """FR-5227, SC-1622: o total da mesma função da Mesa; a decisão guarda o detalhamento."""
    decisao, sucessor = corrigir(cenario, peca, CORRIGIDA)

    assert decisao.pontuacao == Decimal("65.0000")
    assert [linha["parcela"] for linha in decisao.criterios] == [
        "0.0000",
        "15.0000",
        "10.0000",
        "0.0000",
        "40.0000",
    ]
    assert decisao.criterios[4]["limitada"] is True
    assert sucessor.pontuacao == Decimal("65.0000")
    assert sucessor.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    assert sucessor.resultado_anterior_id == peca["superado"].id
    # O sucessor não copia: ele cita a decisão, e o detalhamento é dela.
    assert detalhamento_do_resultado(sucessor) == decisao.criterios
    assert detalhamento_do_resultado(peca["superado"])[2]["parcela"] == "5.0000"


def test_o_total_vindo_junto_e_recusado(cenario, peca):
    with pytest.raises(DomainError) as recusa:
        corrigir(cenario, peca, CORRIGIDA, pontuacao="65")

    assert recusa.value.code == "pontuacao_calculada"
    assert not DecisaoRecurso.objects.exists()


def test_sem_detalhamento_a_correcao_e_incompleta(cenario, peca):
    with pytest.raises(DomainError) as recusa:
        corrigir(cenario, peca, None, pontuacao="65")

    assert recusa.value.code == "pontuacao_calculada"
    with pytest.raises(DomainError) as recusa:
        corrigir(cenario, peca, None, chave="corrigir-153-b")
    assert recusa.value.code == "appeal_correction_incomplete"


def test_a_correcao_cobra_todos_os_criterios(cenario, peca):
    with pytest.raises(DomainError) as recusa:
        corrigir(cenario, peca, ficha(SEED, 0, 1, 2, None, 50))

    assert recusa.value.code == "criterios_pendentes"
    assert "Curso de formação de orientadores" in recusa.value.detail


def test_a_vedacao_de_piora_continua_sobre_o_total(cenario, peca):
    """US4 cenário 2: a correção que reduziria o total é recusada, e nada nasce."""
    with pytest.raises(DomainError) as recusa:
        corrigir(cenario, peca, ficha(SEED, 0, 0, 1, 0, 10))

    assert recusa.value.code == PIORA
    assert not DecisaoRecurso.objects.exists()
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def test_o_mesmo_total_com_criterio_ja_no_teto_e_aceito(cenario, gestor):
    """Quickstart §4: a docência de 52 para 60 meses já estava no teto — o total segue 70."""
    setenta = cenario["inscricoes"][0]
    outra = recorrer_do_preliminar(cenario, gestor, setenta, sufixo="153t")

    decisao, sucessor = corrigir(
        cenario, outra, ficha(SEED, 1, 0, 3, 0, 60), chave="corrigir-153-teto"
    )

    assert decisao.pontuacao == sucessor.pontuacao == Decimal("70.0000")
    assert decisao.criterios[4]["quantidade"] == 60


def test_a_ordem_fica_obsoleta_e_a_reemitida_usa_o_total_novo(cenario, peca, gestor):
    """SC-1622: a cadeia a jusante reage como sempre — e não se conserta sozinha."""
    assert estado_do_marco(edital=cenario["edital"], marco_id=cenario["marco"])["obsoleto"] is False

    corrigir(cenario, peca, CORRIGIDA)

    assert estado_do_marco(edital=cenario["edital"], marco_id=cenario["marco"])["obsoleto"] is True
    novo = emitir(cenario, gestor, chave="emitir-153-depois", motivo="Recurso REC deferido.")
    posicao = PosicaoNaOrdem.objects.get(ato=novo, inscricao=peca["inscricao"])
    assert posicao.pontuacao_combinada == Decimal("65.00")
    assert novo.id != peca["ato"].id


def test_o_titular_le_o_detalhamento_da_decisao_com_os_alterados_marcados(client, cenario, peca):
    """FR-5228: o detalhamento do Resultado vigente é o da decisão; o que ela mudou, marcado."""
    corrigir(cenario, peca, CORRIGIDA)
    entrar_como_titular(client, peca["inscricao"])

    corpo = client.get(
        reverse("portal:acompanhamento", args=[peca["inscricao"].id])
    ).content.decode()
    itens = re.findall(r"<li>\s*<p class=\"criterio-da-ficha\">(.*?)</li>", corpo, re.S)
    marcados = [item.split("<")[0].strip() for item in itens if "alterada pelo recurso" in item]

    assert marcados == ["Especialização", "Exercício de docência em EaD"]
    assert "Resultado corrigido" in corpo


def test_a_tela_de_julgamento_mostra_a_ficha_atacada_e_corrige_por_ela(
    client, seletor_ligado, cenario, peca
):
    """FR-5226, FR-5227: a ficha atacada em leitura e a correção pela mesma ficha da Mesa."""
    identificar(client, JULGADORA, ["julgador"])
    tela = reverse("interface:recurso", args=[peca["recurso"].id])
    corpo = client.get(tela).content.decode()

    assert "Pontuação por critério do resultado atacado" in corpo
    assert "Correção por critério" in corpo
    # Pré-preenchida com o detalhamento atacado, e sem o campo de pontuação única.
    assert f'name="ficha-{criterio_de(4, SEED)}-quantidade" value="10"' in corpo
    assert f'name="pontuacao-{cenario["etapa"]}"' not in corpo
    assert "interface/mesa_barema.js" in corpo
    assert "interface/grupos/ficha-do-barema.css" in corpo

    opcao = re.search(r'<option value="([^"|]+)\|([^"]+)"', corpo)
    dados = {
        "especie": "CORRECAO_FIXADA",
        "motivacao": "A especialização é da área.",
        "etapa": f"{opcao.group(1)}|{opcao.group(2)}",
    }
    for linha in CORRIGIDA:
        dados[f"ficha-{linha['criterionId']}-quantidade"] = linha["quantidade"]
        dados[f"ficha-{linha['criterionId']}-justificativa"] = ""
    dados[f"ficha-{criterio_de(2, SEED)}-justificativa"] = "Certificado da área, conferido."
    resposta = client.post(reverse("interface:recurso-julgar", args=[peca["recurso"].id]), dados)

    assert resposta.status_code == 302
    decisao = DecisaoRecurso.objects.get(recurso=peca["recurso"])
    assert decisao.pontuacao == Decimal("65.0000")
    assert decisao.criterios[2]["justificativa"] == "Certificado da área, conferido."


def test_a_recusa_na_tela_devolve_a_ficha_digitada(client, seletor_ligado, cenario, peca):
    identificar(client, JULGADORA, ["julgador"])
    corpo = client.get(reverse("interface:recurso", args=[peca["recurso"].id])).content.decode()
    opcao = re.search(r'<option value="([^"|]+)\|([^"]+)"', corpo)
    dados = {
        "especie": "CORRECAO_FIXADA",
        "motivacao": "Reduzir.",
        "etapa": f"{opcao.group(1)}|{opcao.group(2)}",
    }
    for linha in ficha(SEED, 0, 0, 1, 0, 7):
        dados[f"ficha-{linha['criterionId']}-quantidade"] = linha["quantidade"]

    resposta = client.post(reverse("interface:recurso-julgar", args=[peca["recurso"].id]), dados)

    assert resposta.status_code == 422
    texto = resposta.content.decode()
    assert f'name="ficha-{criterio_de(4, SEED)}-quantidade" value="7"' in texto
