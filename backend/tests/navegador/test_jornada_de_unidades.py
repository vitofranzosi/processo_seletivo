"""De unidade inexistente a Processo criado nela, só pelo navegador (110, `D-015`, SC-1041).

A prova automatizada de que uma unidade nova entra em operação sem commit, sem deploy e sem comando
no servidor. Três partes, como as jornadas da `107`:

1. **Preparação** — o Administrador institucional, designado como a implantação o designaria, e as
   duas pessoas que vão atuar no campus, que já entraram uma vez;
2. **Ações** — só no navegador: o cadastro da unidade, a concessão do Administrador de acessos, a
   do Gestor, a criação do Processo;
3. **Verificações** — no banco e na trilha.

A validação por pessoas é outra coisa, e não está aqui: é o roteiro G do quickstart (SC-1048).
"""

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from processo_seletivo.auditoria.models import RegistroAuditoria  # noqa: E402
from processo_seletivo.processos.models import ProcessoSeletivo  # noqa: E402
from processo_seletivo.seguranca import acessos as catalogo  # noqa: E402
from processo_seletivo.seguranca.models import Vinculo  # noqa: E402
from processo_seletivo.unidades.application.semente import ler  # noqa: E402
from processo_seletivo.unidades.models import Unidade  # noqa: E402
from tests.seguranca.apoio import pessoa, vincular  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

INES = {"nome": "Inês Institucional", "email": "ines@ifes.edu.br"}
BRUNO = {"nome": "Bruno Serra", "email": "bruno@ifes.edu.br"}
CARLA = {"nome": "Carla Gestora", "email": "carla@ifes.edu.br"}


def test_de_unidade_inexistente_a_processo_criado(jornada):
    # Preparação.
    vincular(
        pessoa("ines", **INES), catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL
    )
    pessoa("bruno", **BRUNO)
    pessoa("carla", **CARLA)
    arquivo_antes = ler()
    ines, bruno, carla = jornada.pessoa(), jornada.pessoa(), jornada.pessoa()

    # Ações — a Administradora institucional cadastra o Campus Serra.
    jornada.entrar(ines, "ines", **INES)
    ines.get_by_role("link", name="Unidades").click()
    ines.get_by_role("link", name="Cadastrar unidade").click()
    ines.get_by_label("Código").fill("serra")
    ines.get_by_label("Sigla").fill("Serra")
    ines.locator("#nome").fill("Campus Serra")
    ines.get_by_label("Primeira linha").fill("Campus Serra")
    ines.get_by_label("Local do ato").fill("Serra (ES)")
    ines.get_by_role("button", name="Conferir").click()
    jornada.capturar(ines, "conferencia")
    expect(ines.get_by_role("heading", name="Confira antes de cadastrar")).to_be_visible()
    expect(ines.locator(".orgao")).to_contain_text("Campus Serra")
    ines.get_by_label("Motivo").fill("Portaria nº 10/2026")
    ines.get_by_role("button", name="Confirmar o cadastro").click()
    expect(ines.get_by_text("Unidade cadastrada.")).to_be_visible()

    # Ações — ela concede o Administrador de acessos do Campus Serra ao Bruno.
    ines.get_by_role("link", name="Administração de acessos").click()
    ines.get_by_role("link", name="Conceder acesso").click()
    ines.get_by_label("Nome ou e-mail da pessoa").fill("bruno")
    ines.get_by_role("button", name="Buscar").click()
    ines.locator("#unidade-1").select_option(label="Campus Serra")
    ines.get_by_role("button", name="Conferir a concessão a Bruno Serra").click()
    ines.get_by_label("Motivo").fill("Portaria nº 11/2026")
    ines.get_by_role("button", name="Confirmar a concessão").click()
    expect(ines.get_by_text("Acesso concedido")).to_be_visible()

    # Ações — o Bruno entra e concede o Gestor à Carla.
    jornada.entrar(bruno, "bruno", **BRUNO)
    bruno.get_by_role("link", name="Acessos da unidade").click()
    bruno.get_by_role("link", name="Conceder acesso").click()
    bruno.get_by_label("Nome ou e-mail da pessoa").fill("carla")
    bruno.get_by_role("button", name="Buscar").click()
    bruno.get_by_label("Papel").select_option(label="Gestor")
    bruno.get_by_role("button", name="Conferir a concessão a Carla Gestora").click()
    bruno.get_by_label("Motivo").fill("Memorando 1/2026")
    bruno.get_by_role("button", name="Confirmar a concessão").click()
    expect(bruno.get_by_text("Acesso concedido")).to_be_visible()

    # Ações — a Carla cria o primeiro Processo do Campus Serra.
    jornada.entrar(carla, "carla", **CARLA)
    carla.get_by_role("link", name="Novo Processo Seletivo").click()
    carla.get_by_label("Identificação institucional").fill("PS-SERRA-2026-01")
    carla.locator("#titulo").fill("Processo seletivo do Campus Serra")
    carla.get_by_label("Número").fill("1")
    carla.get_by_label("Ano").fill("2026")
    carla.locator("#titulo_edital").fill("Edital de seleção do Campus Serra")
    carla.get_by_role("button", name="Criar Processo e Edital").click()
    expect(carla.get_by_text("PS-SERRA-2026-01").first).to_be_visible()
    jornada.capturar(carla, "processo-criado")

    # Verificações.
    serra = Unidade.objects.get(codigo="serra")
    assert (serra.sigla, serra.cabecalho, serra.ativa) == ("Serra", ["Campus Serra"], True)
    assert ler() == arquivo_antes, "nenhuma mudança no repositório"
    registro = RegistroAuditoria.objects.get(operation="REGISTRAR_UNIDADE", aggregate_id=serra.pk)
    assert (registro.institution_scope, registro.reason) == ("serra", "Portaria nº 10/2026")
    assert (
        Vinculo.objects.filter(escopo="serra", papel=catalogo.ADMINISTRADOR_DE_ACESSOS).count() == 1
    )
    assert Vinculo.objects.filter(escopo="serra", papel="gestor").count() == 1
    processo = ProcessoSeletivo.objects.get(institutional_code="PS-SERRA-2026-01")
    assert processo.institution_scope == "serra"
