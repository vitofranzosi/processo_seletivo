"""Acrescentar e remover Perfil e Evento por Retificação (T037).

Remover desloca índices e o domínio aplica as alterações em sequência, então a ordem em que
elas são emitidas é o que decide se o Perfil certo é apagado. Estes testes aplicam as
alterações com o mesmo `apply_changes` do domínio, sobre o mesmo conteúdo — a comparação é com
o resultado, não com a lista de operações.
"""

import pytest

from processo_seletivo.interface import retificacao
from processo_seletivo.publicacoes.domain.changes import apply_changes


def perfil(codigo, nome):
    return {
        "id": f"id-{codigo}",
        "code": codigo,
        "name": nome,
        "description": "",
        "requirements": [],
        "immediateVacancies": 1,
        "reserveType": "NONE",
        "reserveLimit": None,
        "locality": "Vitória",
        "classificationInformation": {},
        "callInformation": {},
        "competitionModalities": [],
    }


def evento(tipo, ordem):
    return {
        "id": f"ev-{ordem}",
        "type": tipo,
        "description": tipo,
        "startAt": "2026-10-01T12:00:00+00:00",
        "endAt": None,
        "order": ordem,
        "status": "PLANEJADO",
    }


@pytest.fixture
def conteudo():
    return {
        "title": "Edital",
        "description": "",
        "profiles": [perfil("A", "Primeiro"), perfil("B", "Segundo"), perfil("C", "Terceiro")],
        "schedule": [evento("Inscrições", 1), evento("Prova", 2)],
    }


def aplicar(conteudo, dados):
    alteracoes, resumo = retificacao.diferencas(conteudo, dados)
    resultado, _ = apply_changes(conteudo, alteracoes, publication_id="p1")
    return resultado, alteracoes, resumo


def test_remover_dois_perfis_apaga_os_marcados_e_nao_os_vizinhos(conteudo):
    """Com REMOVE em ordem crescente, apagar /profiles/0 faria /profiles/2 virar /profiles/1."""
    resultado, _, resumo = aplicar(
        conteudo, {"remover:/profiles/0": "1", "remover:/profiles/2": "1"}
    )

    assert [p["code"] for p in resultado["profiles"]] == ["B"]
    assert [item["rotulo"] for item in resumo] == ["Remoção", "Remoção"]


def test_alterar_e_remover_na_mesma_retificacao_usa_os_indices_do_vigente(conteudo):
    """O REPLACE precisa vir antes do REMOVE, senão altera o Perfil que passou a ocupar o índice."""
    resultado, _, _ = aplicar(
        conteudo,
        {"campo:/profiles/2/name": "Terceiro alterado", "remover:/profiles/0": "1"},
    )

    assert [p["name"] for p in resultado["profiles"]] == ["Segundo", "Terceiro alterado"]


def test_campo_de_linha_removida_nao_vira_alteracao(conteudo):
    """Alterar o que será apagado não tem efeito e poluiria o resumo mostrado antes de confirmar."""
    _, alteracoes, resumo = aplicar(
        conteudo, {"remover:/profiles/1": "1", "campo:/profiles/1/name": "irrelevante"}
    )

    assert [a["operation"] for a in alteracoes] == ["REMOVE"]
    assert len(resumo) == 1


def test_perfil_acrescentado_nasce_com_a_forma_do_snapshot(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        {
            "novo-perfil-77-code": "D",
            "novo-perfil-77-name": "Quarto",
            "novo-perfil-77-immediateVacancies": "2",
            "novo-perfil-77-requirements": "Ensino médio\nExperiência",
        },
    )

    acrescentado = resultado["profiles"][-1]
    assert acrescentado["code"] == "D"
    assert acrescentado["requirements"] == ["Ensino médio", "Experiência"]
    assert acrescentado["immediateVacancies"] == 2
    assert set(acrescentado) == set(conteudo["profiles"][0]), (
        "um subconjunto quebraria a consulta pública e o PDF"
    )


def test_acrescentar_e_remover_juntos_preserva_o_que_nao_foi_tocado(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        {"remover:/profiles/1": "1", "novo-perfil-9-code": "D", "novo-perfil-9-name": "Quarto"},
    )

    assert [p["code"] for p in resultado["profiles"]] == ["A", "C", "D"]


def test_linha_nova_em_branco_e_ignorada(conteudo):
    """Acrescentar e desistir de preencher não pode virar Perfil vazio no Edital publicado."""
    _, alteracoes, _ = aplicar(conteudo, {"novo-perfil-5-code": "", "novo-perfil-5-name": "  "})

    assert alteracoes == []


def test_evento_acrescentado_continua_a_ordem_existente(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        {
            "novo-evento-3-type": "Resultado",
            "novo-evento-3-description": "Divulgação",
            "novo-evento-3-startAt": "2026-12-01T09:00",
        },
    )

    assert [e["order"] for e in resultado["schedule"]] == [1, 2, 3]
    assert resultado["schedule"][-1]["type"] == "Resultado"


def test_nada_marcado_nem_acrescentado_nao_produz_alteracao(conteudo):
    _, alteracoes, _ = aplicar(conteudo, {})
    assert alteracoes == []


def test_abrir_e_nao_tocar_em_nada_nao_produz_alteracao_de_instante():
    """O campo tem precisão de minuto e o snapshot guarda segundos.

    Com comparação de precisão total, todo Evento cujo instante não terminasse em zero segundos
    aparecia como alterado — abrir a tela e reenviar listava mudanças que ninguém fez.
    """
    conteudo = {
        "title": "Edital",
        "description": "",
        "profiles": [],
        "schedule": [
            {**evento("Inscrições", 1), "startAt": "2026-10-01T12:00:37.482913+00:00"}
        ],
    }
    campos = retificacao.campos_editaveis(conteudo)
    reenviado = {
        f"campo:{campo['caminho']}": campo["valor"]
        for grupo in campos
        for campo in grupo["campos"]
    }

    alteracoes, _ = retificacao.diferencas(conteudo, reenviado)
    assert alteracoes == []
