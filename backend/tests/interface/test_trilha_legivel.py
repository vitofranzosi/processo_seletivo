"""A trilha precisa ser legível por quem responde um questionamento.

`OPERACOES.get(op, op)` devolve o código cru quando falta um rótulo — a lacuna não aparece
como erro, aparece como "ALTERAR_RASCUNHO" no meio de "Homologação" e "Criação". Foi assim que
a operação mais frequente depois de CRIAR ficou sem tradução.
"""

import ast
import pathlib

import pytest

from processo_seletivo.interface.views import OPERACOES
from tests.fixtures.publicacao import publish_retification

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"


def operacoes_registradas():
    """Todo literal `operation="..."` passado a record_event pelos commands."""
    encontradas = set()
    for arquivo in RAIZ.rglob("application/*.py"):
        arvore = ast.parse(arquivo.read_text())
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Call):
                continue
            alvo = no.func.id if isinstance(no.func, ast.Name) else getattr(no.func, "attr", "")
            if alvo != "record_event":
                continue
            for argumento in no.keywords:
                if argumento.arg == "operation" and isinstance(argumento.value, ast.Constant):
                    encontradas.add(argumento.value.value)
    return encontradas


def test_toda_operacao_auditada_tem_rotulo_na_trilha():
    registradas = operacoes_registradas()
    assert registradas, "nenhuma chamada a record_event encontrada — o rastreio quebrou"
    assert registradas <= set(OPERACOES), (
        f"sem rótulo, aparecem cruas na tela: {sorted(registradas - set(OPERACOES))}"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_publicar_retificacao_deixa_registro(api_client, manager_headers, process_payload):
    """Era o único ato da Retificação fora da transição compartilhada — e o único sem registro."""
    from processo_seletivo.auditoria.models import RegistroAuditoria
    from tests.fixtures.publicacao import create_retification, publish_original

    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Edital retificado"}],
    )
    publicada = publish_retification(api_client, retificacao)

    operacoes = set(
        RegistroAuditoria.objects.filter(
            aggregate_id=publicada.id, aggregate_type="Retificacao"
        ).values_list("operation", flat=True)
    )
    assert "PUBLICAR" in operacoes, (
        "publicar muda o que o público vê; sem registro a trilha não explica a mudança"
    )
    assert {"CRIAR", "SUBMETER", "HOMOLOGAR"} <= operacoes, "os demais atos continuam registrados"
