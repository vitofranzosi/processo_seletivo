"""O barema pela tela de Retificação (146, T012, FR-5210).

A tela edita o conteúdo vigente e traduz a diferença em alterações. O que se prende aqui é a
tradução: cada critério é um cartão com os seis campos, aninhado na Etapa; acrescentar critério é
uma linha nova; e o ato que acrescenta critério sem alterar a máxima é recusado pela conferência do
conteúdo consolidado — a mesma regra da gravação do rascunho.
"""

import pytest

from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.interface import retificacao as ui
from processo_seletivo.publicacoes.domain.changes import apply_changes

pytestmark = [pytest.mark.contract]

ETAPA = "aaaaaaaa-0000-4000-8000-000000014680"
DECISORIA = "aaaaaaaa-0000-4000-8000-000000014681"
TITULOS = "aaaaaaaa-0000-4000-8000-000000014682"
DOUTORADO = "aaaaaaaa-0000-4000-8000-000000014683"
NOVO = "aaaaaaaa-0000-4000-8000-000000014684"


def conteudo():
    return {
        "schemaVersion": 21,
        "profiles": [],
        "schedule": [],
        "sections": [],
        "attachments": [],
        "stages": [
            {
                "id": ETAPA,
                "name": "Prova de Títulos",
                "order": 1,
                "weight": None,
                "eliminatory": False,
                "classificatory": True,
                "minimumScore": None,
                "evaluationsPerRegistration": 1,
                "maximumScore": "20.0000",
                "forma": "PONTUADA",
                # O degrau 25 (166): o conteúdo da Retificação já vem elevado.
                "videoOption": False,
                "rotuloFavoravel": None,
                "rotuloDesfavoravel": None,
                "scheduleEventId": None,
                "criteria": [
                    {
                        "id": DOUTORADO,
                        "name": "Diploma de Doutorado",
                        "description": "Na área da Educação.",
                        "maximumScore": "20.0000",
                        "pointsPerUnit": "20.0000",
                        "unitLabel": "diploma",
                        "documentRequirementId": TITULOS,
                    }
                ],
            },
            {
                "id": DECISORIA,
                "name": "Análise documental",
                "order": 2,
                "weight": None,
                "eliminatory": True,
                "classificatory": False,
                "minimumScore": None,
                "evaluationsPerRegistration": 1,
                "maximumScore": None,
                "forma": "DECISORIA",
                "videoOption": False,
                "rotuloFavoravel": "Apto",
                "rotuloDesfavoravel": "Inapto",
                "scheduleEventId": None,
                "criteria": [],
            },
        ],
        "documentRequirements": [
            {
                "id": TITULOS,
                "key": "titulos",
                "name": "Títulos acadêmicos",
                "instructions": "",
                "required": False,
                "order": 1,
                "profileId": None,
                "modalityId": None,
                "attachmentId": None,
                "modalityCode": None,
                "moment": "AT_ENROLLMENT",
                "reusesRequirementId": None,
                "requiredWhen": None,
            }
        ],
    }


def grupo_do_criterio(base):
    grupos = ui.campos_editaveis(base)
    return next(g for g in grupos if g["tipo"] == "Critério de avaliação")


def enviado(base, alteracoes=None, remover=False, **extras):
    """O POST da tela: todo campo de todo cartão com o valor que veio, mais os ajustes."""
    dados = {}
    for grupo in ui.campos_editaveis(base):
        for campo in grupo["campos"]:
            dados[f"campo:{campo['referencia']}"] = campo["valor"]
    criterio = grupo_do_criterio(base)
    for chave, valor in (alteracoes or {}).items():
        campo = next(c for c in criterio["campos"] if c["chave"] == chave)
        dados[f"campo:{campo['referencia']}"] = valor
    if remover:
        dados[f"remover:{criterio['referencia']}"] = "1"
    dados.update(extras)
    return dados


def test_cada_criterio_e_um_cartao_aninhado_na_secao_das_etapas():
    grupos = ui.campos_editaveis(conteudo())
    criterio = grupo_do_criterio(conteudo())

    assert criterio["caminho"] == f"/stages/id={ETAPA}/criteria/id={DOUTORADO}"
    assert [c["chave"] for c in criterio["campos"]] == [
        "name",
        "description",
        "maximumScore",
        "pointsPerUnit",
        "unitLabel",
        "documentRequirementId",
    ]
    assert criterio["removivel"] is True
    etapas = next(s for s in ui.agrupar_em_secoes(grupos) if s["id"] == "etapas")
    tipos = [g["tipo"] for g in etapas["grupos"]]
    assert tipos == ["Etapa", "Critério de avaliação", "Etapa"], "o critério logo abaixo da Etapa"
    assert next(g for g in etapas["grupos"] if g["tipo"] == "Critério de avaliação")["aninhado"]


def test_o_documento_oferecido_e_o_da_inscricao_e_o_vazio_diz_nenhum():
    criterio = grupo_do_criterio(conteudo())
    documento = next(c for c in criterio["campos"] if c["chave"] == "documentRequirementId")

    assert documento["opcoes"] == ((TITULOS, "Títulos acadêmicos"),)
    assert documento["rotulo_do_vazio"] == "Nenhum documento"
    assert documento["valor"] == TITULOS


def test_alterar_um_campo_emite_o_replace_daquele_campo():
    base = conteudo()
    alteracoes, resumo = ui.diferencas(base, enviado(base, {"name": "Doutorado em Educação"}))

    assert alteracoes == [
        {
            "targetPath": f"/stages/id={ETAPA}/criteria/id={DOUTORADO}/name",
            "operation": "REPLACE",
            "newValue": "Doutorado em Educação",
        }
    ]
    assert resumo[0]["rotulo"] == "Critério"


def test_nada_alterado_nada_emitido():
    base = conteudo()

    assert ui.diferencas(base, enviado(base)) == ([], [])


def test_apagar_a_descricao_publica_texto_vazio_e_nao_nulo():
    base = conteudo()
    alteracoes, _ = ui.diferencas(base, enviado(base, {"description": ""}))

    assert alteracoes[0]["newValue"] == ""


def test_desligar_o_documento_diz_nenhum_documento_no_resumo():
    base = conteudo()
    alteracoes, resumo = ui.diferencas(base, enviado(base, {"documentRequirementId": ""}))

    assert alteracoes[0]["newValue"] is None
    assert (resumo[0]["antes"], resumo[0]["depois"]) == ("Títulos acadêmicos", "nenhum documento")


def test_documento_forjado_e_recusado_pela_tela():
    base = conteudo()

    with pytest.raises(ValueError, match="a opção escolhida não existe"):
        ui.diferencas(base, enviado(base, {"documentRequirementId": NOVO}))


def test_remover_um_criterio():
    base = conteudo()
    alteracoes, _ = ui.diferencas(base, enviado(base, remover=True))

    assert alteracoes == [
        {"targetPath": f"/stages/id={ETAPA}/criteria/id={DOUTORADO}", "operation": "REMOVE"}
    ]


def linha_nova(**campos):
    base = {
        "id": NOVO,
        "stage": ETAPA,
        "name": "Especialização",
        "description": "",
        "maximumScore": "10",
        "pointsPerUnit": "5",
        "unitLabel": "certificado",
        "documentRequirementId": TITULOS,
        **campos,
    }
    return {f"novo-barema-0-{chave}": valor for chave, valor in base.items()}


def test_acrescentar_criterio_emite_o_add_na_forma_publicada():
    base = conteudo()
    alteracoes, resumo = ui.diferencas(base, enviado(base, **linha_nova()))

    assert alteracoes == [
        {
            "targetPath": f"/stages/id={ETAPA}/criteria/-",
            "operation": "ADD",
            "newValue": {
                "id": NOVO,
                "name": "Especialização",
                "description": "",
                "maximumScore": "10.0000",
                "pointsPerUnit": "5.0000",
                "unitLabel": "certificado",
                "documentRequirementId": TITULOS,
            },
        }
    ]
    assert resumo[0]["grupo"] == "Critério do barema da Etapa Prova de Títulos"
    assert resumo[0]["depois"] == "Especialização — 5 pontos por certificado, até 10"


def test_a_etapa_decisoria_nao_e_oferecida_para_acrescentar():
    opcoes = ui.opcoes_do_criterio_de_avaliacao_novo(conteudo())

    assert opcoes["stage"] == ((ETAPA, "Prova de Títulos"),)
    with pytest.raises(ValueError, match="a opção escolhida não existe"):
        ui.diferencas(conteudo(), enviado(conteudo(), **linha_nova(stage=DECISORIA)))


def test_a_linha_nova_sem_etapa_e_recusada():
    with pytest.raises(ValueError, match="diga a que Etapa"):
        ui.diferencas(conteudo(), enviado(conteudo(), **linha_nova(stage="")))


def test_o_prefixo_da_linha_nova_nao_cria_linha_fantasma_no_desempate():
    """`novo-criterio-` é o do desempate: o do barema não pode começar por ele."""
    dados = linha_nova()

    assert ui.novas_para_formulario(dados, "criterio", ui.NOVO_CRITERIO) == []
    assert len(ui.novas_para_formulario(dados, "barema", ui.NOVO_CRITERIO_DE_AVALIACAO)) == 1


def _consolidado(base, alteracoes):
    resultado, _ = apply_changes(
        base, alteracoes, publication_id="aaaaaaaa-0000-4000-8000-000000014689"
    )
    return [
        achado
        for achado in blocking_findings(validate_for_publication(resultado))
        if "/criteria" in achado.path or "maximumScore" in achado.path
    ]


def test_acrescentar_sem_alterar_a_maxima_e_recusado_e_com_ela_passa():
    """O caso que quebra a soma, e o mesmo ato com a máxima corrigida (FR-5210)."""
    base = conteudo()
    so_o_criterio, _ = ui.diferencas(base, enviado(base, **linha_nova()))

    recusas = _consolidado(base, so_o_criterio)
    assert [achado.path for achado in recusas] == [f"/stages/id={ETAPA}/maximumScore"]
    assert "a soma das máximas dos critérios do barema, 30" in recusas[0].message

    etapa = next(g for g in ui.campos_editaveis(base) if g["tipo"] == "Etapa")
    maxima = next(c for c in etapa["campos"] if c["chave"] == "maximumScore")
    com_a_maxima, _ = ui.diferencas(
        base, enviado(base, **linha_nova(), **{f"campo:{maxima['referencia']}": "30"})
    )

    assert _consolidado(base, com_a_maxima) == []


# --- o texto apagado, pela forma publicada (revisão do PR #461) ---------------------------------

EVENTO = "aaaaaaaa-0000-4000-8000-000000014685"


def com_evento():
    base = conteudo()
    base["schedule"] = [
        {
            "id": EVENTO,
            "type": "AVALIACAO",
            "description": "Prova de Títulos",
            "startAt": "2027-01-10T12:00:00+00:00",
            "endAt": None,
            "order": 1,
            "status": "PLANEJADO",
            "location": "Auditório do Cefor",
            "isRegistrationPeriod": False,
            "shownInPdf": True,
        }
    ]
    return base


def campo_do_evento(base, chave):
    grupo = next(g for g in ui.campos_editaveis(base) if g["tipo"] == "Evento")
    return next(c for c in grupo["campos"] if c["chave"] == chave)


@pytest.mark.parametrize(
    ("chave", "esperado"),
    [("location", ""), ("description", None)],
    ids=["local-vazio-e-ausencia", "descricao-e-o-nome"],
)
def test_o_texto_apagado_segue_a_forma_publicada(chave, esperado):
    """O local apagado é "não declarado" (`""`); a descrição do Evento é o nome dele, e apagada
    continua nula — a forma publicada a recusa, e é essa a recusa certa."""
    base = com_evento()
    campo = campo_do_evento(base, chave)
    alteracoes, _ = ui.diferencas(base, enviado(base, **{f"campo:{campo['referencia']}": ""}))

    assert alteracoes == [
        {
            "targetPath": f"/schedule/id={EVENTO}/{chave}",
            "operation": "REPLACE",
            "newValue": esperado,
        }
    ]


def test_o_documento_restrito_e_oferecido_marcado_na_retificacao():
    """A mesma leitura e o mesmo rótulo da composição (`documentos.documentos_do_barema`)."""
    base = conteudo()
    base["documentRequirements"][0]["profileId"] = "aaaaaaaa-0000-4000-8000-000000014686"

    opcoes = ui.opcoes_do_barema(base)["documentRequirementId"]

    assert opcoes == ((TITULOS, "Títulos acadêmicos (não é pedido a toda inscrição)"),)
