"""O documento da Retificação mostra o que ela fez nascer e acrescentou (048, FR-798).

Pelo caminho da publicação, e não compondo o PDF à mão: o que se prova é que o documento que a
Retificação publica sai do conteúdo **retificado**, e que as seis coisas desta feature chegam a
ele — a Modalidade, a linha do quadro dela, a janela, a regra de corte, o critério e a reversão.
"""

import pytest

from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.legado import publicar_como_acervo
from tests.fixtures.publicacao import retify
from tests.fixtures.snapshot import FATO, MARCO, PERFIL, rascunho_completo
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

NOVA = "00000000-0000-4000-8000-000000048401"


def _principal(rascunho):
    return next(p for p in rascunho["profiles"] if p.get("classificationMilestones"))


def test_o_documento_da_retificacao_mostra_as_seis(api_client, manager_headers, process_payload):
    rascunho = rascunho_completo()
    principal = _principal(rascunho)
    principal["vacancyReversion"] = None
    for marco in principal["classificationMilestones"]:
        marco["appealWindow"] = None
        marco["cutRule"] = None
    edital = publicar_como_acervo(
        api_client, manager_headers, process_payload, draft=rascunho, anexos=1
    )
    perfil = f"/profiles/id={principal['id']}"
    marco = f"{perfil}/classificationMilestones/id={MARCO}"
    assert principal["id"] in PERFIL.values()

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"{marco}/appealWindow",
                "operation": "REPLACE",
                "newValue": {"admits": True, "durationDays": 3, "unit": "DIAS_CORRIDOS"},
            },
            {
                "targetPath": f"{marco}/cutRule",
                "operation": "REPLACE",
                "newValue": {
                    "targetKind": "FIXED",
                    "targetCount": 2,
                    "surplusCount": 0,
                    "tieOutcome": "STRICT",
                    "governedStage": "NONE",
                    "continuation": "NONE",
                },
            },
            {
                "targetPath": f"{perfil}/vacancyReversion",
                "operation": "REPLACE",
                "newValue": {"kind": "ON_BALANCE"},
            },
            {
                "targetPath": f"{marco}/tiebreakers/-",
                "operation": "ADD",
                "newValue": {
                    "id": "00000000-0000-4000-8000-000000048402",
                    "order": 3,
                    "type": "MENOR_VALOR_DE_FATO",
                    "parameters": {"factId": FATO["NASCIMENTO"]},
                    "whenMissing": "CRITERIO_NAO_SE_APLICA",
                },
            },
            {
                "targetPath": f"{perfil}/competitionModalities/-",
                "operation": "ADD",
                "newValue": {
                    "id": NOVA,
                    "code": "EPX",
                    "name": "Egressos da escola pública",
                    "description": "",
                    "normativeRule": None,
                },
            },
            {
                "targetPath": f"{perfil}/vacancyTable/-",
                "operation": "ADD",
                "newValue": {
                    "id": "00000000-0000-4000-8000-000000048403",
                    "modalityId": NOVA,
                    "immediateVacancies": 0,
                },
            },
        ],
        suffix="documento-048",
    )

    publicacao = Publicacao.objects.filter(edital=edital).latest("publication_order")
    texto = texto_de(bytes(publicacao.documento.bytes))
    corrido = " ".join(texto.split())

    # A frase nomeia o resultado desde a `067` (ED-02).
    # Na apresentação por perguntas (069), o recurso sai em "Como recorrer?", com o alcance dito
    # pelo código quando só um Perfil tem o marco (R6).
    assert (
        "Para o Perfil P1 — contra o resultado de “Classificação final”: no prazo de 3 (três)"
        in corrido
    ), "a janela que nasceu"
    # Na redação 2 desde a `069` (K4, V2).
    assert "Seguem no processo os 2 (dois) primeiros classificados" in corrido, "a regra de corte"
    assert "que não forem preenchidas passam para a ampla concorrência" in corrido, "a reversão"
    assert "3º" in corrido, "o terceiro critério de desempate"
    assert "Egressos da escola pública" in corrido, "a Modalidade acrescentada"
    # Desde a `068`, com mais de um Perfil, a linha do quadro mora na tabela de vagas: a lista vira
    # coluna, com o código no cabeçalho, e o Perfil que a declara tem a célula dela.
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    legenda = next(
        i
        for i, linha in enumerate(linhas)
        # A matriz da `069` chama-se "Vagas por Perfil e lista de concorrência".
        if linha.startswith("Tabela ") and linha.endswith("lista de concorrência")
    )
    linha_do_perfil = linhas.index(principal["code"], legenda)
    cabecalho = linhas[legenda + 1 : linha_do_perfil]
    assert "EPX" in cabecalho, "e a linha dela no quadro"
    celulas = linhas[linha_do_perfil + 1 : linha_do_perfil + len(cabecalho)]
    assert celulas[cabecalho.index("EPX") - 1] == "0", "com a quantidade declarada"
