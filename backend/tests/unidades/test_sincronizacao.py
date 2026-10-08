"""O registro de Unidades: declarado em arquivo, aplicado com trilha, tudo ou nada (060, R-003).

A fixture da suíte já registra o Cefor com os valores de `unidades.json`; é sobre ele que a
sincronização sem mudança diz `1 sem mudança`.
"""

import json
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application.sincronizacao import ARQUIVO, ler, sincronizar
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import CEFOR

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SERRA = {
    "sigla": "Serra",
    "nome": "Campus Serra",
    "cabecalho": ["Campus Serra"],
    "local": "Serra (ES)",
    "ativa": True,
}


def _declarado(**extra):
    cefor = {chave: valor for chave, valor in CEFOR.items() if chave != "codigo"}
    return {"cefor": cefor, **extra}


def test_o_arquivo_versionado_declara_o_cefor_como_o_compositor_o_imprimia():
    """FR-1111: a primeira Unidade é o Cefor, com as linhas e o local das constantes de antes."""
    declarado = ler()
    assert declarado == _declarado()
    assert ler(ARQUIVO) == json.loads(ARQUIVO.read_text(encoding="utf-8"))


def test_sem_mudanca_nada_e_gravado():
    antes = RegistroAuditoria.objects.count()
    assert sincronizar(_declarado()) == (0, 0, 1)
    assert RegistroAuditoria.objects.count() == antes


def test_unidade_nova_e_registrada_com_trilha():
    assert sincronizar(_declarado(serra=SERRA)) == (1, 0, 1)

    serra = Unidade.objects.get(codigo="serra")
    assert (serra.nome, serra.cabecalho, serra.local) == (
        "Campus Serra",
        ["Campus Serra"],
        "Serra (ES)",
    )
    evento = RegistroAuditoria.objects.get(operation="REGISTRAR_UNIDADE", aggregate_id=serra.pk)
    assert evento.actor_subject == "implantacao"
    assert evento.institution_scope == "serra"
    assert evento.detalhe["depois"]["nome"] == "Campus Serra"


def test_mudanca_e_aplicada_com_antes_e_depois():
    """FR-1108: quem, quando, o valor anterior e o novo."""
    sincronizar(_declarado(serra=SERRA))
    renomeada = {**SERRA, "nome": "Campus Serra — Novo", "ativa": False}

    assert sincronizar(_declarado(serra=renomeada)) == (0, 1, 1)

    serra = Unidade.objects.get(codigo="serra")
    assert (serra.nome, serra.ativa) == ("Campus Serra — Novo", False)
    assert serra.alterada_em is not None
    evento = RegistroAuditoria.objects.get(operation="ALTERAR_UNIDADE", aggregate_id=serra.pk)
    assert evento.detalhe["antes"]["nome"] == "Campus Serra"
    assert evento.detalhe["depois"]["nome"] == "Campus Serra — Novo"
    assert (evento.previous_state, evento.new_state) == ("ATIVA", "DESATIVADA")


def test_retirar_uma_unidade_do_arquivo_e_recusado_sem_gravar_nada():
    """FR-1109: nenhuma Unidade é excluída — desativa-se."""
    sincronizar(_declarado(serra=SERRA))
    antes = RegistroAuditoria.objects.count()

    with pytest.raises(DomainError) as recusa:
        sincronizar({"serra": SERRA, "vitoria": {**SERRA, "nome": "Campus Vitória"}})

    assert recusa.value.code == "unidade_retirada"
    assert "ativa" in recusa.value.detail
    assert not Unidade.objects.filter(codigo="vitoria").exists(), "tudo ou nada"
    assert RegistroAuditoria.objects.count() == antes


@pytest.mark.parametrize(
    "entrada",
    [
        {**SERRA, "cabecalho": []},
        {**SERRA, "cabecalho": ["um", "dois", "três"]},
        {**SERRA, "cabecalho": ["", "dois"]},
        {**SERRA, "nome": "   "},
        {**SERRA, "ativa": "sim"},
        {k: v for k, v in SERRA.items() if k != "local"},
        {**SERRA, "sobrando": 1},
    ],
    ids=["sem-linha", "tres-linhas", "linha-vazia", "nome-vazio", "ativa-texto", "falta", "sobra"],
)
def test_entrada_malformada_e_recusada_sem_gravar_nada(entrada):
    with pytest.raises(DomainError) as recusa:
        sincronizar(_declarado(serra=entrada))
    assert recusa.value.code == "unidade_malformada"
    assert not Unidade.objects.filter(codigo="serra").exists()


@pytest.mark.parametrize("codigo", ["Serra", "serra campus", "serra_campus", "-serra"])
def test_codigo_fora_do_formato_e_recusado(codigo):
    with pytest.raises(DomainError) as recusa:
        sincronizar(_declarado(**{codigo: SERRA}))
    assert recusa.value.code == "unidade_malformada"


def test_o_comando_diz_o_que_aplicou(tmp_path):
    arquivo = tmp_path / "unidades.json"
    arquivo.write_text(json.dumps(_declarado(serra=SERRA)), encoding="utf-8")
    saida = StringIO()

    call_command("sincronizar_unidades", "--arquivo", str(arquivo), stdout=saida)
    assert saida.getvalue().strip() == "Unidades: 1 criadas, 0 alteradas, 1 sem mudança."

    saida = StringIO()
    call_command("sincronizar_unidades", "--arquivo", str(arquivo), stdout=saida)
    assert saida.getvalue().strip() == "Unidades: 0 criadas, 0 alteradas, 2 sem mudança."


def test_o_comando_transforma_a_recusa_em_erro_de_comando(tmp_path):
    arquivo = tmp_path / "unidades.json"
    arquivo.write_text(json.dumps({"serra": SERRA}), encoding="utf-8")
    with pytest.raises(CommandError, match="unidade_retirada"):
        call_command("sincronizar_unidades", "--arquivo", str(arquivo))
