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


def _constantes(arvore):
    """`NOME = "TEXTO"` no nível do módulo: as operações que a gestão passa por constante."""
    return {
        alvo.id: no.value.value
        for no in arvore.body
        if isinstance(no, ast.Assign) and isinstance(no.value, ast.Constant)
        for alvo in no.targets
        if isinstance(alvo, ast.Name) and isinstance(no.value.value, str)
    }


def operacoes_registradas():
    """Toda operação passada a `record_event`: pelos commands e pelas views da gestão.

    Até a 111 a varredura lia só `application/*.py` e só o literal: as operações que as views da
    gestão passam por constante — a emissão do relatório (`099`), a exportação do kit (`111`) —
    escapavam, e chegariam cruas à trilha. Agora lê também `interface/*.py` e resolve a constante
    do módulo.
    """
    encontradas = set()
    arquivos = [*RAIZ.rglob("application/*.py"), *(RAIZ / "interface").glob("*.py")]
    for arquivo in arquivos:
        arvore = ast.parse(arquivo.read_text())
        constantes = _constantes(arvore)
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Call):
                continue
            alvo = no.func.id if isinstance(no.func, ast.Name) else getattr(no.func, "attr", "")
            if alvo != "record_event":
                continue
            for argumento in no.keywords:
                if argumento.arg != "operation":
                    continue
                if isinstance(argumento.value, ast.Constant):
                    encontradas.add(argumento.value.value)
                elif isinstance(argumento.value, ast.Name) and argumento.value.id in constantes:
                    encontradas.add(constantes[argumento.value.id])
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
