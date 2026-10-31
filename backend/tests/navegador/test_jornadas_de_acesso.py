"""As jornadas da gestão de acessos, num navegador de verdade (107, `FR-3131`, `SC-1014`).

Cada caso tem três partes, e só três:

1. **Preparação** — pessoas, vínculos e unidades gravados pelo ambiente de testes, como estado de
   partida; quem o provedor autenticará fica preparado na página do provedor.
2. **Ações** — só no navegador: cliques, campos e botões. Nenhum shell, nenhuma sessão editada,
   nenhuma escrita no banco.
3. **Verificações** — depois das ações, no banco e na trilha.

A entrada atravessa a aplicação inteira: a página de acesso, a ida ao provedor, a página dele e o
retorno com o `state`. O relógio da US5 é do ambiente, como o do servidor de verdade: avançá-lo não
é ação de ninguém.
"""

from datetime import timedelta

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from processo_seletivo.auditoria.models import RegistroAuditoria  # noqa: E402
from processo_seletivo.seguranca import acessos as catalogo  # noqa: E402
from processo_seletivo.seguranca import relogio  # noqa: E402
from processo_seletivo.seguranca.models import RevogacaoDeVinculo, Vinculo  # noqa: E402
from tests.seguranca.apoio import AGORA, pessoa, vincular  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

CARLOS = {"nome": "Carlos Admin", "email": "carlos.admin@ifes.edu.br"}
BEATRIZ = {"nome": "Beatriz Prado", "email": "beatriz.prado@ifes.edu.br"}


def test_us1_quem_entra_sem_acesso_ve_o_proprio_nome_e_a_quem_pedir(jornada):
    # Preparação: ninguém concedeu nada a ela.
    nadia = jornada.pessoa()

    # Ações.
    jornada.entrar(nadia, "nadia", nome="Nádia Nova", email="nadia@ifes.edu.br")
    jornada.capturar(nadia, "sem-acesso")

    # Verificações.
    expect(nadia.get_by_role("heading", name="Sem acesso vigente")).to_be_visible()
    expect(nadia.get_by_text("Nádia Nova")).to_be_visible()
    expect(nadia.get_by_text("Peça acesso ao administrador de acessos")).to_be_visible()
    assert "pessoa-" not in nadia.content()
    assert not Vinculo.objects.exists()
    assert RegistroAuditoria.objects.filter(operation="ENTRADA").count() == 1


def test_us3_concessao_e_revogacao_pela_tela_valem_na_acao_seguinte(jornada):
    # Preparação: o administrador de acessos do Cefor; e a Beatriz, que já entrou uma vez.
    carlos = pessoa("carlos", **CARLOS)
    vincular(carlos, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    bea = pessoa("bea", **BEATRIZ)
    administrador, beatriz = jornada.pessoa(), jornada.pessoa()

    # Ações — o administrador concede.
    jornada.entrar(administrador, "carlos", **CARLOS)
    expect(administrador.locator(".nome-da-pessoa strong")).to_have_text("Carlos Admin")
    administrador.get_by_role("link", name="Acessos da unidade").click()
    administrador.get_by_role("link", name="Conceder acesso").click()
    administrador.get_by_label("Nome ou e-mail da pessoa").fill("beatriz")
    administrador.get_by_role("button", name="Buscar").click()
    jornada.capturar(administrador, "busca")
    administrador.get_by_label("Papel").select_option(label="Elaborador")
    administrador.get_by_role("button", name="Conferir a concessão a Beatriz Prado").click()
    jornada.capturar(administrador, "confirmacao")
    expect(administrador.get_by_role("heading", name="Confira antes de conceder")).to_be_visible()
    expect(administrador.locator(".dados-do-ato")).to_contain_text("Beatriz Prado")
    expect(administrador.locator(".dados-do-ato")).to_contain_text("Elaborador")
    administrador.get_by_label("Motivo").fill("Memorando 12/2026")
    administrador.get_by_role("button", name="Confirmar a concessão").click()
    expect(administrador.get_by_text("Acesso concedido")).to_be_visible()

    # Ações — a Beatriz entra e trabalha.
    jornada.entrar(beatriz, "bea", **BEATRIZ)
    expect(beatriz.locator(".nome-da-pessoa")).to_contain_text("Elaborador")

    # Ações — o administrador revoga, com a sessão dela aberta.
    administrador.get_by_role("button", name="Revogar Elaborador de Beatriz Prado").click()
    expect(administrador.get_by_role("heading", name="Confira antes de revogar")).to_be_visible()
    administrador.get_by_label("Motivo").fill("Saiu da unidade")
    administrador.get_by_role("button", name="Confirmar a revogação").click()
    expect(administrador.get_by_text("Acesso revogado")).to_be_visible()
    jornada.capturar(administrador, "historico")
    beatriz.get_by_role("link", name="Processos Seletivos").first.click()

    # Verificações.
    expect(beatriz.get_by_role("heading", name="Sem acesso vigente")).to_be_visible()
    vinculo = Vinculo.objects.get(pessoa=bea)
    assert (vinculo.escopo, vinculo.papel, vinculo.concedido_por) == (
        "cefor",
        "elaborador",
        carlos.username,
    )
    assert RevogacaoDeVinculo.objects.get(vinculo=vinculo).motivo == "Saiu da unidade"
    assert list(
        RegistroAuditoria.objects.filter(aggregate_id=vinculo.pk)
        .order_by("occurred_at")
        .values_list("operation", flat=True)
    ) == ["ACESSO_CONCEDER", "ACESSO_REVOGAR"]
    historico = administrador.locator(".historico-de-acessos")
    expect(historico).to_contain_text("Memorando 12/2026")
    expect(historico).to_contain_text("Saiu da unidade")


def test_us2_a_troca_de_unidade_pela_barra_muda_as_permissoes(jornada, campus_a):
    # Preparação: Gestora no Cefor e Elaboradora no campus A.
    ana = pessoa("ana", nome="Ana Souza")
    vincular(ana, "cefor", "gestor")
    vincular(ana, "campus-a", "elaborador")
    pagina = jornada.pessoa()

    # Ações.
    jornada.entrar(pagina, "ana", nome="Ana Souza")
    expect(pagina.get_by_role("link", name="Autoridades da unidade")).to_have_count(0)
    pagina.get_by_label("Atuando em").select_option(
        label="Centro de Referência em Formação e em Educação a Distância"
    )
    pagina.get_by_role("button", name="Trocar").click()
    jornada.capturar(pagina, "depois-da-troca")

    # Verificações.
    expect(pagina.get_by_role("link", name="Autoridades da unidade")).to_be_visible()
    expect(pagina.locator(".nome-da-pessoa")).to_contain_text("Gestor")
    expect(pagina.locator(".nome-da-pessoa")).not_to_contain_text("Elaborador")
    assert RegistroAuditoria.objects.filter(operation="TROCA_DE_UNIDADE").count() == 1


def test_us4_a_administracao_institucional_concede_o_administrador_de_uma_unidade(
    jornada, campus_a
):
    # Preparação: a administradora institucional, como o comando de implantação a deixaria; e a
    # Beatriz, que já entrou uma vez.
    rita = pessoa("rita", nome="Rita Reitoria")
    vincular(
        rita,
        catalogo.ESCOPO_INSTITUCIONAL,
        catalogo.ADMINISTRADOR_INSTITUCIONAL,
        por="implantacao",
    )
    bea = pessoa("bea", **BEATRIZ)
    administradora, beatriz = jornada.pessoa(), jornada.pessoa()

    # Ações.
    jornada.entrar(administradora, "rita", nome="Rita Reitoria")
    expect(administradora.locator(".unidade-ativa")).to_contain_text("Administração institucional")
    administradora.get_by_role("link", name="Administração de acessos").click()
    administradora.get_by_role("link", name="Conceder acesso").click()
    administradora.get_by_label("Nome ou e-mail da pessoa").fill("prado")
    administradora.get_by_role("button", name="Buscar").click()
    resultado = administradora.get_by_role("region", name="Resultado")
    resultado.get_by_label("Unidade").select_option(label="Unidade campus-a")
    administradora.get_by_role("button", name="Conferir a concessão a Beatriz Prado").click()
    expect(administradora.locator(".dados-do-ato")).to_contain_text("Unidade campus-a")
    administradora.get_by_label("Motivo").fill("Portaria 9/2026")
    administradora.get_by_role("button", name="Confirmar a concessão").click()
    expect(administradora.get_by_text("Acesso concedido")).to_be_visible()
    jornada.capturar(administradora, "administradores")
    jornada.entrar(beatriz, "bea", **BEATRIZ)

    # Verificações.
    expect(beatriz.get_by_role("link", name="Acessos da unidade")).to_be_visible()
    vinculo = Vinculo.objects.get(pessoa=bea)
    assert (vinculo.escopo, vinculo.papel) == ("campus-a", catalogo.ADMINISTRADOR_DE_ACESSOS)
    assert vinculo.concedido_por == rita.username


def test_us5_a_sessao_termina_por_inatividade_e_a_pagina_diz_por_que(jornada, monkeypatch):
    # Preparação: uma pessoa com acesso, e o relógio do ambiente.
    ana = pessoa("ana", nome="Ana Souza")
    vincular(ana, "cefor", "elaborador")
    instante = {"agora": AGORA}
    monkeypatch.setattr(relogio, "agora", lambda: instante["agora"])
    pagina = jornada.pessoa()

    # Ações — entra, e volta depois de 31 minutos parada.
    jornada.entrar(pagina, "ana", nome="Ana Souza")
    expect(pagina.locator(".nome-da-pessoa strong")).to_have_text("Ana Souza")
    instante["agora"] = AGORA + timedelta(minutes=31)
    pagina.get_by_role("link", name="Agenda").click()
    jornada.capturar(pagina, "sessao-encerrada")

    # Verificações.
    expect(pagina.get_by_text("Sua sessão terminou por inatividade")).to_be_visible()
    saida = RegistroAuditoria.objects.get(operation="SAIDA")
    assert saida.detalhe["motivo"] == "inatividade"


def test_us6_us7_suspender_encerra_as_sessoes_e_reativar_pede_entrar_de_novo(jornada):
    # Preparação: a administradora institucional; a Beatriz, Elaboradora no Cefor.
    rita = pessoa("rita", nome="Rita Reitoria")
    vincular(
        rita,
        catalogo.ESCOPO_INSTITUCIONAL,
        catalogo.ADMINISTRADOR_INSTITUCIONAL,
        por="implantacao",
    )
    bea = pessoa("bea", **BEATRIZ)
    vincular(bea, "cefor", "elaborador")
    administradora, beatriz = jornada.pessoa(), jornada.pessoa()

    # Ações — a Beatriz está trabalhando; a administradora a suspende.
    jornada.entrar(beatriz, "bea", **BEATRIZ)
    expect(beatriz.locator(".nome-da-pessoa")).to_contain_text("Elaborador")
    jornada.entrar(administradora, "rita", nome="Rita Reitoria")
    administradora.get_by_role("link", name="Administração de acessos").click()
    administradora.get_by_role("link", name="Suspender ou reativar pessoas").click()
    administradora.get_by_label("Nome ou e-mail da pessoa").fill("beatriz")
    administradora.get_by_role("button", name="Buscar").click()
    administradora.get_by_role("button", name="Suspender Beatriz Prado").click()
    expect(administradora.get_by_role("heading", name="Confira antes de suspender")).to_be_visible()
    expect(administradora.get_by_text("Acessos que deixam de valer")).to_be_visible()
    jornada.capturar(administradora, "confirmar-suspensao")
    administradora.get_by_label("Motivo").fill("Processo 23.000/2026")
    administradora.get_by_role("button", name="Confirmar a suspensão").click()
    expect(administradora.get_by_text("Pessoa suspensa")).to_be_visible()
    beatriz.get_by_role("link", name="Agenda").click()
    expect(beatriz.get_by_role("heading", name="Bem-vindo à gestão")).to_be_visible()

    # Ações — reativa; a sessão antiga dela continua morta, e ela entra de novo.
    administradora.get_by_role("button", name="Reativar Beatriz Prado").click()
    expect(administradora.locator(".dados-do-ato").last).to_contain_text("Elaborador")
    jornada.capturar(administradora, "confirmar-reativacao")
    administradora.get_by_label("Motivo").fill("Fim do processo")
    administradora.get_by_role("button", name="Confirmar a reativação").click()
    expect(administradora.get_by_text("Pessoa reativada")).to_be_visible()
    jornada.entrar(beatriz, "bea", **BEATRIZ)

    # Verificações.
    expect(beatriz.locator(".nome-da-pessoa")).to_contain_text("Elaborador")
    assert not RevogacaoDeVinculo.objects.exists()
    assert list(
        RegistroAuditoria.objects.filter(operation__startswith="PESSOA_")
        .order_by("occurred_at")
        .values_list("operation", flat=True)
    ) == ["PESSOA_SUSPENDER", "PESSOA_REATIVAR"]
