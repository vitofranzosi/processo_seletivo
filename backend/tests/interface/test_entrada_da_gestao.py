"""A entrada da gestão (075): a página de acesso, a escolha de identidades, o destino e a porta.

O que se prende aqui é o que a tela nova promete e a antiga não fazia: a gestão tem porta no
portal, a escolha diz o que cada identidade faz sem expor código de permissão, quem abre um link
volta a ele, e a demonstração não sobrevive ao seletor desligado. O que a tela antiga já fazia —
presidir não é papel, a identidade escolhida vence o campo, o envio com CSRF — continua preso nos
testes que a provavam.
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import demonstracao, identidade

pytestmark = pytest.mark.django_db

ACESSO = reverse("interface:identificar")
ESCOLHA = reverse("interface:identificar-demonstracao")


def _entrar(client, **campos):
    return client.post(ACESSO, campos)


def _sessao(client):
    return client.session.get(identidade.CHAVE_SESSAO)


# --- FR-1701: todo papel tem descrição ----------------------------------------------------------


def test_todo_papel_tem_descricao_e_nenhuma_descricao_sobra():
    """O guardião de `FR-1701`: papel novo sem frase apareceria na escolha sem dizer o que faz."""
    assert set(identidade.DESCRICOES) == set(identidade.PAPEIS)
    assert all(texto.strip() for texto in identidade.DESCRICOES.values())


# --- FR-1690, FR-1691: a página de acesso e o método --------------------------------------------


def test_a_pagina_de_acesso_apresenta_o_produto_e_a_entrada(client, seletor_ligado):
    corpo = client.get(ACESSO).content.decode()

    assert "Bem-vindo à gestão" in corpo
    assert "Gestão de Processos Seletivos" in corpo
    assert "Acessar ambiente de demonstração" in corpo
    assert ESCOLHA in corpo
    # O candidato que chegou aqui por engano tem caminho de volta.
    assert reverse("portal:inscricoes") in corpo


def test_sem_metodo_a_pagina_diz_que_a_entrada_nao_esta_configurada(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = False

    resposta = client.get(ACESSO)

    assert resposta.status_code == 503
    corpo = resposta.content.decode()
    assert "Autenticação institucional não configurada" in corpo
    assert ESCOLHA not in corpo
    assert "Acessar ambiente de demonstração" not in corpo


def test_sem_metodo_a_escolha_nao_existe_e_o_envio_nao_grava(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = False

    assert client.get(ESCOLHA).status_code == 503
    resposta = _entrar(client, identidade_sugerida="alguem", papeis=["gestor"])

    assert resposta.status_code == 503
    assert _sessao(client) is None


# --- FR-1692, FR-1693: a escolha ----------------------------------------------------------------


def test_a_escolha_agrupa_e_descreve_sem_codigo_de_permissao(client, seletor_ligado, comissao_de_a):
    corpo = client.get(ESCOLHA).content.decode()

    assert "Comissões" in corpo and "Responsabilidades da unidade" in corpo
    assert "maria" in corpo and "Presidência de comissão" in corpo
    assert identidade.DESCRICOES["gestor"].split(":")[0] in corpo
    codigos = {p for _, permissoes in identidade.PAPEIS.values() for p in permissoes}
    assert [codigo for codigo in codigos if codigo in corpo] == []


def test_entrar_pela_comissao_nao_concede_papel(client, seletor_ligado, comissao_de_a):
    _entrar(client, identidade_sugerida="maria")

    assert _sessao(client)["papeis"] == []


def test_entrar_por_uma_responsabilidade_concede_so_ela(client, seletor_ligado):
    resposta = _entrar(client, identidade_sugerida="gustavo.gestor", papeis=["gestor", "inventado"])

    assert resposta["Location"] == reverse("interface:lista")
    assert _sessao(client)["papeis"] == ["gestor"]


def test_sem_ninguem_na_trilha_o_nome_se_denuncia_como_demonstracao():
    entradas = {e["chave"]: e for e in demonstracao.responsabilidades()}

    assert entradas["auditor"]["subject"] == "demo.auditor"


def test_o_nome_sugerido_e_o_de_quem_exerceu_o_papel_na_trilha():
    for _ in range(2):
        RegistroAuditoria.objects.create(
            occurred_at=timezone.now(),
            actor_subject="bruno.homologador",
            permission="edital:homologar",
            institution_scope=identidade.ESCOPO_PADRAO,
            operation="homologar",
            aggregate_type="Edital",
            aggregate_id=uuid.uuid4(),
            correlation_id="teste",
        )

    entradas = {e["chave"]: e for e in demonstracao.responsabilidades()}

    assert entradas["homologador"]["subject"] == "bruno.homologador"


# --- FR-1694, FR-1695: opções avançadas e busca -------------------------------------------------


def test_envio_sem_nome_volta_com_a_recusa_junto_do_campo(client, seletor_ligado):
    resposta = _entrar(client, subject="  ", papeis=["gestor"])

    assert resposta.status_code == 422
    corpo = resposta.content.decode()
    assert "Informe um nome para entrar." in corpo
    assert '<details class="avancado" open>' in corpo
    assert 'aria-describedby="recusa-do-nome"' in corpo
    assert _sessao(client) is None


def test_a_busca_so_aparece_acima_do_limiar(client, seletor_ligado, comissao_de_a):
    """Nove papéis e duas pessoas de comissão: onze entradas, e a busca vem escondida."""
    corpo = client.get(ESCOLHA).content.decode()

    assert 'id="busca-de-identidade" hidden' in corpo
    assert "interface/acesso.js" in corpo


def test_sem_comissao_a_busca_nao_vem_e_o_grupo_nao_aparece(client, seletor_ligado):
    corpo = client.get(ESCOLHA).content.decode()

    assert len(identidade.PAPEIS) <= demonstracao.LIMIAR_DA_BUSCA
    assert 'id="busca-de-identidade"' not in corpo
    assert 'id="grupo-comissoes"' not in corpo


# --- FR-1696: o destino -------------------------------------------------------------------------


def test_a_porta_manda_ao_acesso_com_o_proprio_endereco(client, seletor_ligado):
    resposta = client.get(reverse("interface:visao-geral") + "?ano=2026")

    assert resposta.status_code == 302
    assert resposta["Location"] == ACESSO + "?proximo=%2Fgestao%2Fvisao-geral%3Fano%3D2026"


def test_o_destino_atravessa_a_escolha_e_e_seguido(client, seletor_ligado):
    destino = reverse("interface:visao-geral")
    corpo = client.get(ESCOLHA, {"proximo": destino}).content.decode()
    assert f'name="proximo" value="{destino}"' in corpo

    resposta = _entrar(client, identidade_sugerida="carlos", papeis=["gestor"], proximo=destino)

    assert resposta["Location"] == destino


@pytest.mark.parametrize(
    "destino",
    [
        "https://outro.exemplo/gestao/",
        "//outro.exemplo/gestao/",
        "/selecoes/",
        "/gestao/identificar",
        "/gestao/identificar/demonstracao",
        "/gestao/sair",
    ],
)
def test_destino_fora_da_gestao_ou_em_laco_e_ignorado(client, seletor_ligado, destino):
    resposta = _entrar(client, identidade_sugerida="carlos", papeis=["gestor"], proximo=destino)

    assert resposta["Location"] == reverse("interface:lista")


def test_porta_alcancada_por_post_nao_guarda_destino(client, seletor_ligado):
    resposta = client.post(reverse("interface:processo-criar"), {})

    assert resposta["Location"] == ACESSO


# --- FR-1697: sair e continuar ------------------------------------------------------------------


def test_sair_leva_a_pagina_de_acesso(client, seletor_ligado):
    _entrar(client, identidade_sugerida="carlos", papeis=["gestor"])

    resposta = client.post(reverse("interface:sair"))

    assert resposta["Location"] == ACESSO
    assert _sessao(client) is None


def test_identificado_a_pagina_oferece_continuar_ou_trocar(client, seletor_ligado):
    _entrar(client, identidade_sugerida="carlos", papeis=["gestor"])

    corpo = client.get(ACESSO).content.decode()

    assert "Continuar como carlos" in corpo
    assert "Trocar de identidade" in corpo


# --- FR-1698: a origem da sessão ----------------------------------------------------------------


def test_a_sessao_grava_a_origem(client, seletor_ligado):
    _entrar(client, identidade_sugerida="carlos", papeis=["gestor"])

    assert _sessao(client)["origem"] == identidade.ORIGEM_DEMONSTRACAO


def test_a_demonstracao_nao_sobrevive_ao_seletor_desligado(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    _entrar(client, identidade_sugerida="carlos", papeis=["gestor"])

    settings.INTERFACE_SELETOR_IDENTIDADE = False
    assert client.get(reverse("interface:lista")).status_code == 302

    # E religar a chave não traz a sessão de volta: ela foi apagada, e não só ignorada.
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    assert _sessao(client) is None
    assert client.get(reverse("interface:lista")).status_code == 302


def test_sessao_anterior_sem_origem_conta_como_demonstracao(client, settings):
    sessao = client.session
    sessao[identidade.CHAVE_SESSAO] = {"subject": "antiga", "escopo": "cefor", "papeis": ["gestor"]}
    sessao.save()
    settings.INTERFACE_SELETOR_IDENTIDADE = False

    assert client.get(reverse("interface:lista")).status_code == 302
    assert _sessao(client) is None


# --- FR-1699, FR-1700: o portal -----------------------------------------------------------------


def test_o_portal_oferece_a_gestao_onde_ha_por_onde_entrar(client, seletor_ligado):
    cabecalho = client.get(reverse("portal:vitrine")).content.decode().split("</header>")[0]

    assert "Gestão de Processos Seletivos" in cabecalho
    assert "Minhas inscrições" in cabecalho
    assert "Área de gestão" in cabecalho
    assert f'href="{reverse("interface:lista")}"' in cabecalho


def test_sem_metodo_o_portal_nao_oferece_a_gestao(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = False

    cabecalho = client.get(reverse("portal:vitrine")).content.decode().split("</header>")[0]

    assert "Minhas inscrições" in cabecalho
    assert "Área de gestão" not in cabecalho


# --- FR-1702: os protótipos saíram --------------------------------------------------------------


def test_os_prototipos_do_estudo_sairam(client, seletor_ligado):
    assert client.get("/gestao/prototipos/acesso/").status_code == 404
