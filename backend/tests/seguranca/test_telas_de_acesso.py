"""A gestão de acessos pela interface (107, US1 a US4).

Pelo cliente do Django, com a entrada institucional inteira — ida, provedor simulado, retorno — e
nenhuma sessão montada à mão. A jornada pelo navegador, com a página executada, está em
`tests/navegador/`; aqui ficam as recusas, que pedem envio montado à mão, e as consequências que se
leem do banco.
"""

import re

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.models import RevogacaoDeVinculo, Vinculo
from tests.interface.conftest import identificar
from tests.seguranca.apoio import ator_do_cliente, entrar, pessoa, vincular

pytestmark = pytest.mark.django_db

CONCEDER = reverse("interface:acessos-conceder")


@pytest.fixture
def bea():
    return pessoa("bea", nome="Beatriz Prado", email="beatriz.prado@ifes.edu.br")


@pytest.fixture
def admin_cefor(client, provedor):
    """O administrador de acessos do `cefor`, com a sessão aberta neste cliente."""
    alguem = pessoa("admin-cefor", nome="Carlos Admin", email="carlos@ifes.edu.br")
    vincular(alguem, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    entrar(client, "admin-cefor", nome="Carlos Admin", email="carlos@ifes.edu.br")
    return alguem


def _cliente_de(identificador, **dados):
    outro = Client()
    entrar(outro, identificador, **dados)
    return outro


def _conferir(client, alvo, papel="elaborador", **extra):
    return client.post(
        CONCEDER, {"acao": "conferir", "pessoa": alvo.username, "papel": papel, **extra}
    )


def _confirmar(client, alvo, papel="elaborador", motivo="Memorando 12/2026", **extra):
    return client.post(
        CONCEDER,
        {"acao": "confirmar", "pessoa": alvo.username, "papel": papel, "motivo": motivo, **extra},
    )


# --- US1: sem acesso ----------------------------------------------------------------------------


def test_quem_entra_sem_vinculo_ve_a_tela_sem_acesso_com_o_proprio_nome(client, provedor):
    resposta = entrar(client, "nova", nome="Nádia Nova", email="nadia@ifes.edu.br")
    destino = client.get(resposta["Location"])

    assert destino.status_code == 302
    assert destino["Location"] == reverse("interface:sem-acesso")
    corpo = client.get(reverse("interface:sem-acesso")).content.decode()
    assert "Nádia Nova" in corpo
    assert "nadia@ifes.edu.br" in corpo
    assert "Peça acesso ao administrador de acessos da sua unidade" in corpo
    assert "pessoa-" not in corpo


def test_toda_porta_leva_quem_esta_sem_acesso_a_tela_sem_acesso(client, provedor):
    entrar(client, "nova", nome="Nádia Nova")

    for rota in ("interface:lista", "interface:agenda", "interface:minhas-etapas"):
        resposta = client.get(reverse(rota))
        assert resposta.status_code == 302, rota
        assert resposta["Location"] == reverse("interface:sem-acesso"), rota


def test_quem_perdeu_a_unidade_ativa_troca_pela_tela_sem_acesso(client, provedor, campus_a):
    from processo_seletivo.seguranca.application import acessos

    ana = pessoa("ana", nome="Ana")
    no_cefor = vincular(ana, "cefor", "elaborador")
    vincular(ana, "campus-a", "gestor")
    entrar(client, "ana", nome="Ana")
    assert ator_do_cliente(client).institution_scope == "campus-a"
    sessao = client.session
    sessao["interface_identidade"] = {**sessao["interface_identidade"], "unidade": "cefor"}
    sessao.save()
    revogador = pessoa("revogador")
    vincular(revogador, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    from processo_seletivo.seguranca.domain import Actor

    acessos.revogar(
        Actor(revogador.username, "cefor", frozenset({catalogo.GERIR})),
        vinculo=no_cefor,
        motivo="saiu",
        now=no_cefor.concedido_em,
    )

    assert client.get(reverse("interface:lista"))["Location"] == reverse("interface:sem-acesso")
    corpo = client.get(reverse("interface:sem-acesso")).content.decode()
    assert 'name="unidade" value="campus-a"' in corpo
    assert 'value="cefor"' not in corpo
    troca = client.post(reverse("interface:unidade-ativa"), {"unidade": "campus-a"})
    assert troca.status_code == 302
    assert ator_do_cliente(client).institution_scope == "campus-a"


def test_a_tela_sem_acesso_nao_atende_quem_nao_entrou_nem_quem_tem_acesso(
    client, provedor, seletor_ligado
):
    assert client.get(reverse("interface:sem-acesso"))["Location"] == reverse(
        "interface:identificar"
    )
    identificar(client, "gustavo.gestor", ["gestor"])
    assert client.get(reverse("interface:sem-acesso"))["Location"] == reverse("interface:lista")


# --- US2: o nome e a unidade ativa na barra -----------------------------------------------------


def test_a_barra_mostra_o_nome_e_nao_o_identificador(client, provedor):
    ana = pessoa("ana", nome="Ana Souza", email="ana@ifes.edu.br")
    vincular(ana, "cefor", "elaborador")
    entrar(client, "ana", nome="Ana Souza", email="ana@ifes.edu.br")

    corpo = client.get(reverse("interface:lista")).content.decode()
    barra = corpo.split('<div class="pessoa-identificada">')[1].split("</div>")[0]
    assert "<strong>Ana Souza</strong>" in barra
    assert ana.username not in barra
    assert '<span class="iniciais" aria-hidden="true" title="Ana Souza">AS</span>' in barra


def test_sem_nome_a_barra_usa_o_email_e_nunca_o_identificador(client, provedor):
    ana = pessoa("ana", email="ana@ifes.edu.br")
    vincular(ana, "cefor", "elaborador")
    entrar(client, "ana", email="ana@ifes.edu.br")

    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "<strong>ana@ifes.edu.br</strong>" in corpo
    assert ana.username not in corpo


def test_o_seletor_da_barra_troca_a_unidade_sem_levar_permissao(client, provedor, campus_a):
    ana = pessoa("ana", nome="Ana")
    vincular(ana, "cefor", "gestor")
    vincular(ana, "campus-a", "elaborador")
    entrar(client, "ana", nome="Ana")

    corpo = client.get(reverse("interface:lista")).content.decode()
    seletor = corpo.split('<div class="unidade-ativa">')[1].split("</div>")[0]
    assert re.search(r'<option value="campus-a" selected>', seletor)
    assert '<option value="cefor">' in seletor
    client.post(reverse("interface:unidade-ativa"), {"unidade": "cefor"})
    ator = ator_do_cliente(client)
    assert ator.can("processo:criar")
    assert not ator.can("edital:elaborar")


def test_com_um_escopo_so_nao_ha_seletor(client, provedor):
    ana = pessoa("ana", nome="Ana")
    vincular(ana, "cefor", "elaborador")
    entrar(client, "ana", nome="Ana")

    corpo = client.get(reverse("interface:lista")).content.decode()
    assert '<div class="unidade-ativa">' in corpo
    assert 'name="unidade"' not in corpo.split('<div class="unidade-ativa">')[1].split("</div>")[0]


def test_a_demonstracao_ve_a_barra_de_sempre(client, seletor_ligado):
    identificar(client, "gustavo.gestor", ["gestor"])

    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "<strong>gustavo.gestor</strong>" in corpo
    assert '<div class="unidade-ativa">' not in corpo
    assert "Acessos da unidade" not in corpo


# --- US3: acessos da unidade ---------------------------------------------------------------------


def test_a_tela_lista_quem_atua_na_unidade_pelo_nome(client, admin_cefor, bea, campus_a):
    vincular(bea, "cefor", "homologador", por=admin_cefor.username)
    de_fora = pessoa("fora", nome="Fulano de Fora")
    vincular(de_fora, "campus-a", "gestor")

    corpo = client.get(reverse("interface:acessos")).content.decode()
    assert "Beatriz Prado" in corpo
    assert "Homologador" in corpo
    assert "Carlos Admin" in corpo
    assert "Fulano de Fora" not in corpo
    assert bea.username not in corpo.split("<h1>")[1]


def test_a_concessao_pela_tela_passa_pela_confirmacao_e_vale_na_requisicao_seguinte(
    client, admin_cefor, bea
):
    cliente_da_bea = _cliente_de("bea", nome="Beatriz Prado")
    assert ator_do_cliente(cliente_da_bea) is None

    busca = client.post(CONCEDER, {"acao": "buscar", "termo": "beatriz"}).content.decode()
    assert "Beatriz Prado" in busca
    assert f'name="pessoa" value="{bea.username}"' in busca
    conferencia = _conferir(client, bea)
    corpo = conferencia.content.decode()
    assert conferencia.status_code == 200
    for esperado in ("Beatriz Prado", "Centro de Referência", "Elaborador", "Redige Editais"):
        assert esperado in corpo, esperado
    assert not Vinculo.objects.filter(pessoa=bea).exists()

    assert _confirmar(client, bea)["Location"] == reverse("interface:acessos") + "?feito=concedido"
    vinculo = Vinculo.objects.get(pessoa=bea)
    assert (vinculo.escopo, vinculo.papel, vinculo.concedido_por) == (
        "cefor",
        "elaborador",
        admin_cefor.username,
    )
    assert vinculo.motivo == "Memorando 12/2026"
    evento = RegistroAuditoria.objects.get(operation="ACESSO_CONCEDER", aggregate_id=vinculo.pk)
    assert evento.actor_subject == admin_cefor.username
    assert ator_do_cliente(cliente_da_bea).can("edital:elaborar")


def test_sem_motivo_a_confirmacao_volta_e_nada_e_gravado(client, admin_cefor, bea):
    resposta = _confirmar(client, bea, motivo="   ")

    assert resposta.status_code == 422
    assert "Informe o motivo" in resposta.content.decode()
    assert 'name="acao" value="confirmar"' in resposta.content.decode()
    assert not Vinculo.objects.filter(pessoa=bea).exists()


def test_a_confirmacao_reenviada_nao_duplica(client, admin_cefor, bea):
    _confirmar(client, bea)
    segunda = _confirmar(client, bea)

    assert segunda.status_code == 409
    assert Vinculo.objects.filter(pessoa=bea).count() == 1


def test_a_revogacao_pela_tela_vale_com_a_sessao_da_pessoa_aberta(client, admin_cefor, bea):
    vinculo = vincular(bea, "cefor", "elaborador")
    cliente_da_bea = _cliente_de("bea", nome="Beatriz Prado")
    assert cliente_da_bea.get(reverse("interface:lista")).status_code == 200
    revogar = reverse("interface:acessos-revogar", args=[vinculo.pk])

    conferencia = client.post(revogar, {"acao": "conferir"})
    assert conferencia.status_code == 200
    assert "perde o papel Elaborador" in conferencia.content.decode()
    assert not RevogacaoDeVinculo.objects.exists()
    assert client.post(revogar, {"acao": "confirmar", "motivo": "Saiu da unidade"})["Location"] == (
        reverse("interface:acessos") + "?feito=revogado"
    )

    assert RevogacaoDeVinculo.objects.get(vinculo=vinculo).motivo == "Saiu da unidade"
    assert RegistroAuditoria.objects.filter(operation="ACESSO_REVOGAR").count() == 1
    seguinte = cliente_da_bea.get(reverse("interface:lista"))
    assert seguinte["Location"] == reverse("interface:sem-acesso")


def test_o_historico_mostra_concessao_e_revogacao_com_motivo(client, admin_cefor, bea):
    vinculo = vincular(bea, "cefor", "elaborador", por=admin_cefor.username)
    revogar = reverse("interface:acessos-revogar", args=[vinculo.pk])
    client.post(revogar, {"acao": "confirmar", "motivo": "Fim da portaria 7"})

    corpo = client.get(reverse("interface:acessos")).content.decode()
    historico = corpo.split('class="historico-de-acessos"')[1]
    assert "revogou" in historico
    assert "concedeu" in historico
    assert "Fim da portaria 7" in historico
    assert "Carlos Admin" in historico


# --- Busca ---------------------------------------------------------------------------------------


def test_a_busca_exige_tres_letras_e_nao_lista_sem_termo(client, admin_cefor, bea):
    assert "Beatriz" not in client.get(CONCEDER).content.decode()
    curta = client.post(CONCEDER, {"acao": "buscar", "termo": "be"}).content.decode()
    assert "Beatriz" not in curta
    assert "ao menos 3 letras" in curta
    # O termo pelo endereço não busca: a busca é `POST` (`FR-3115`).
    assert "Beatriz" not in client.get(CONCEDER, {"termo": "beatriz"}).content.decode()


def test_a_busca_para_em_dez_e_avisa(client, admin_cefor):
    for numero in range(12):
        pessoa(f"servidor-{numero}", nome=f"Servidor {numero:02d}")

    corpo = client.post(CONCEDER, {"acao": "buscar", "termo": "servidor"}).content.decode()
    assert corpo.count('name="acao" value="conferir"') == 10
    assert "Mais de 10 pessoas encontradas" in corpo


def test_a_busca_nao_mostra_o_ator_nem_inativo_nem_identificadores(client, admin_cefor, bea):
    inativa = pessoa("inativa", nome="Beatriz Inativa")
    get_user_model().objects.filter(pk=inativa.pk).update(is_active=False)

    resultado = client.post(CONCEDER, {"acao": "buscar", "termo": "beatriz"}).content.decode()
    resultado = resultado.split('id="resultado-titulo"')[1]
    assert "Beatriz Prado" in resultado
    assert "beatriz.prado@ifes.edu.br" in resultado
    assert "Beatriz Inativa" not in resultado
    # O identificador interno vai só no campo oculto; o do provedor, em lugar nenhum.
    assert re.findall(r"pessoa-[0-9a-f]{8}-", resultado) == re.findall(
        r'value="(pessoa-[0-9a-f]{8}-)', resultado
    )
    assert '"bea"' not in resultado
    proprio = client.post(CONCEDER, {"acao": "buscar", "termo": "carlos"}).content.decode()
    assert "Ninguém encontrado" in proprio


def test_a_busca_e_recusada_a_quem_nao_concede(client, provedor):
    gestora = pessoa("gestora", nome="Gina")
    vincular(gestora, "cefor", "gestor")
    entrar(client, "gestora", nome="Gina")

    assert client.post(CONCEDER, {"acao": "buscar", "termo": "beatriz"}).status_code == 403
    assert client.get(reverse("interface:acessos")).status_code == 403
    assert "Acessos da unidade" not in client.get(reverse("interface:lista")).content.decode()


# --- Recusas montadas à mão ---------------------------------------------------------------------


def test_autoconcessao_montada_a_mao_e_recusada(client, admin_cefor):
    conferencia = _conferir(client, admin_cefor, papel="gestor")
    assert conferencia.status_code == 403
    assert "Ninguém concede nem revoga o próprio acesso" in conferencia.content.decode()
    assert 'name="acao" value="confirmar"' not in conferencia.content.decode()

    assert _confirmar(client, admin_cefor, papel="gestor").status_code == 403
    assert not Vinculo.objects.filter(pessoa=admin_cefor, papel="gestor").exists()


def test_papel_de_acesso_pela_porta_da_unidade_e_recusado(client, admin_cefor, bea):
    resposta = _confirmar(client, bea, papel=catalogo.ADMINISTRADOR_DE_ACESSOS)

    assert resposta.status_code == 422
    assert not Vinculo.objects.filter(pessoa=bea).exists()


def test_a_unidade_do_formulario_e_ignorada(client, admin_cefor, bea, campus_a):
    _confirmar(client, bea, unidade="campus-a")

    assert list(Vinculo.objects.filter(pessoa=bea).values_list("escopo", flat=True)) == ["cefor"]


def test_vinculo_de_outra_unidade_e_nao_encontrado(client, admin_cefor, bea, campus_a):
    de_fora = vincular(bea, "campus-a", "gestor")
    revogar = reverse("interface:acessos-revogar", args=[de_fora.pk])

    assert client.post(revogar, {"acao": "conferir"}).status_code == 404
    assert client.post(revogar, {"acao": "confirmar", "motivo": "x"}).status_code == 404
    assert not RevogacaoDeVinculo.objects.exists()


def test_o_administrador_da_unidade_nao_revoga_outro_administrador(client, admin_cefor, bea):
    outro = vincular(bea, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)

    corpo = client.get(reverse("interface:acessos")).content.decode()
    assert reverse("interface:acessos-revogar", args=[outro.pk]) not in corpo
    resposta = client.post(
        reverse("interface:acessos-revogar", args=[outro.pk]),
        {"acao": "confirmar", "motivo": "x"},
    )
    assert resposta.status_code == 403
    assert not RevogacaoDeVinculo.objects.exists()


def test_pessoa_desativada_entre_a_busca_e_a_confirmacao_e_recusada(client, admin_cefor, bea):
    assert _conferir(client, bea).status_code == 200
    get_user_model().objects.filter(pk=bea.pk).update(is_active=False)

    assert _confirmar(client, bea).status_code == 409
    assert not Vinculo.objects.filter(pessoa=bea).exists()


def test_identificador_que_nao_e_de_pessoa_e_recusado(client, admin_cefor):
    resposta = client.post(
        CONCEDER, {"acao": "conferir", "pessoa": "gustavo.gestor", "papel": "gestor"}
    )
    assert resposta.status_code == 409


def test_a_demonstracao_nao_alcanca_as_telas_de_acesso(client, seletor_ligado):
    identificar(client, "gustavo.gestor", list(catalogo_operacional()))

    for rota in ("interface:acessos", "interface:administracao-de-acessos"):
        assert client.get(reverse(rota)).status_code == 403, rota
    assert client.post(CONCEDER, {"acao": "buscar", "termo": "ana"}).status_code == 403


def catalogo_operacional():
    from processo_seletivo.interface.identidade import PAPEIS

    return PAPEIS


# --- US4: administração institucional ------------------------------------------------------------


@pytest.fixture
def admin_institucional(client, provedor):
    alguem = pessoa("reitoria", nome="Rita Reitoria")
    vincular(
        alguem,
        catalogo.ESCOPO_INSTITUCIONAL,
        catalogo.ADMINISTRADOR_INSTITUCIONAL,
        por="implantacao",
    )
    entrar(client, "reitoria", nome="Rita Reitoria")
    return alguem


def test_o_institucional_concede_o_administrador_de_acessos_de_uma_unidade(
    client, admin_institucional, bea, campus_a
):
    conceder = reverse("interface:administracao-de-acessos-conceder")
    lista = client.get(reverse("interface:administracao-de-acessos")).content.decode()
    assert "Centro de Referência" in lista
    busca = client.post(conceder, {"acao": "buscar", "termo": "beatriz"}).content.decode()
    assert '<option value="campus-a">' in busca

    dados = {"pessoa": bea.username, "papel": catalogo.ADMINISTRADOR_DE_ACESSOS}
    conferencia = client.post(conceder, {"acao": "conferir", "unidade": "campus-a", **dados})
    assert "Administrador de acessos da unidade" in conferencia.content.decode()
    gravada = client.post(
        conceder, {"acao": "confirmar", "unidade": "campus-a", "motivo": "Portaria 9", **dados}
    )

    assert gravada.status_code == 302
    vinculo = Vinculo.objects.get(pessoa=bea)
    assert (vinculo.escopo, vinculo.papel) == ("campus-a", catalogo.ADMINISTRADOR_DE_ACESSOS)
    cliente_da_bea = _cliente_de("bea", nome="Beatriz Prado")
    assert cliente_da_bea.get(reverse("interface:acessos")).status_code == 200


def test_o_institucional_nao_concede_papel_operacional_nem_a_si(client, admin_institucional, bea):
    conceder = reverse("interface:administracao-de-acessos-conceder")
    operacional = client.post(
        conceder,
        {
            "acao": "confirmar",
            "pessoa": bea.username,
            "papel": "gestor",
            "unidade": "cefor",
            "motivo": "x",
        },
    )
    a_si = client.post(
        conceder,
        {
            "acao": "confirmar",
            "pessoa": admin_institucional.username,
            "papel": catalogo.ADMINISTRADOR_DE_ACESSOS,
            "unidade": "cefor",
            "motivo": "x",
        },
    )

    assert operacional.status_code == 422
    assert a_si.status_code == 403
    assert not Vinculo.objects.exclude(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL).exists()


def test_o_institucional_revoga_so_administrador_de_acessos(client, admin_institucional, bea):
    administrador = vincular(bea, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    operacional = vincular(bea, "cefor", "gestor")

    assert (
        client.post(
            reverse("interface:administracao-de-acessos-revogar", args=[operacional.pk]),
            {"acao": "conferir"},
        ).status_code
        == 404
    )
    resposta = client.post(
        reverse("interface:administracao-de-acessos-revogar", args=[administrador.pk]),
        {"acao": "confirmar", "motivo": "Portaria 10"},
    )
    assert resposta.status_code == 302
    assert RevogacaoDeVinculo.objects.filter(vinculo=administrador).exists()
    assert not RevogacaoDeVinculo.objects.filter(vinculo=operacional).exists()


def test_o_administrador_da_unidade_nao_abre_a_administracao_institucional(client, admin_cefor):
    resposta = client.get(reverse("interface:administracao-de-acessos"))

    assert resposta.status_code == 403
    assert "administrar os acessos das unidades" in resposta.content.decode()
