"""As telas do registro de Unidades, pela entrada institucional (110, FR-3312, FR-3314 a FR-3330).

O Administrador institucional entra pelo provedor simulado da `106`, como entraria pelo SSO; a
demonstração é recusada. Os casos percorrem o que só a tela prova: a conferência que não grava, a
prévia pelas linhas do compositor, as consequências antes do botão e o envio forjado recusado.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_DE_ACESSOS,
    ADMINISTRADOR_INSTITUCIONAL,
    ESCOPO_INSTITUCIONAL,
)
from processo_seletivo.unidades.models import Unidade
from tests.fixtures import provedor_simulado
from tests.fixtures.autoridades import CEFOR, registrar_unidade
from tests.interface.conftest import identificar
from tests.seguranca.apoio import entrar, pessoa, vincular

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

LISTA = reverse("interface:unidades")
CADASTRAR = reverse("interface:unidade-cadastrar")
SERRA = {
    "codigo": "serra",
    "sigla": "Serra",
    "nome": "Campus Serra",
    "cabecalho_1": "Campus Serra",
    "cabecalho_2": "",
    "local": "Serra (ES)",
    "atendimento": "",
}


@pytest.fixture
def provedor(settings):
    provedor_simulado.limpar()
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = provedor_simulado.CAMINHO
    yield provedor_simulado
    provedor_simulado.limpar()


@pytest.fixture
def administradora(client, provedor):
    """A Administradora institucional, com a sessão institucional aberta neste cliente."""
    vincular(
        pessoa("ines", nome="Inês Institucional"), ESCOPO_INSTITUCIONAL, ADMINISTRADOR_INSTITUCIONAL
    )
    assert entrar(client, "ines", nome="Inês Institucional").status_code == 302
    return client


def _pagina(resposta):
    return resposta.content.decode()


def _conferir(client, **campos):
    return client.post(CADASTRAR, {**SERRA, "acao": "conferir", **campos})


def _confirmar(client, **campos):
    return client.post(CADASTRAR, {**SERRA, "acao": "confirmar", "motivo": "Portaria 1", **campos})


def _versao(pagina):
    return re.search(r'name="versao" value="([^"]+)"', pagina).group(1)


# --- Quem chega --------------------------------------------------------------------------------


def test_a_demonstracao_e_recusada_e_nao_ve_o_item(client, settings):
    """FR-3312, EC-10, item 15 do pedido: o seletor continua, e não alcança as unidades."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "ana.gestora", ["gestor"])

    barra = _pagina(client.get(reverse("interface:lista")))
    recusa = client.get(LISTA)

    assert "Unidades</span>" not in barra and reverse("interface:unidades") not in barra
    assert recusa.status_code == 403


def test_o_administrador_de_acessos_da_unidade_nao_ve_unidades(client, provedor):
    """FR-3311: papel de unidade, com qualquer permissão, recebe a recusa."""
    vincular(pessoa("bia"), "cefor", ADMINISTRADOR_DE_ACESSOS)
    entrar(client, "bia")

    barra = _pagina(client.get(reverse("interface:lista")))

    assert reverse("interface:unidades") not in barra
    assert client.get(LISTA).status_code == 403
    assert client.post(CADASTRAR, {**SERRA, "acao": "confirmar", "motivo": "x"}).status_code == 403
    assert not Unidade.objects.filter(codigo="serra").exists()


def test_o_administrador_institucional_ve_os_dois_itens(administradora):
    barra = _pagina(administradora.get(LISTA))

    assert reverse("interface:administracao-de-acessos") in barra
    assert reverse("interface:unidades") in barra


def test_envio_forjado_sem_permissao_e_recusado(client, provedor):
    """SC-1043: a sessão institucional sem o papel não grava por envio montado à mão."""
    pessoa("sem-papel")
    entrar(client, "sem-papel")

    for rota in (
        CADASTRAR,
        reverse("interface:unidade-editar", args=["cefor"]),
        reverse("interface:unidade-desativar", args=["cefor"]),
    ):
        resposta = client.post(rota, {**SERRA, "acao": "confirmar", "motivo": "x", "versao": "x"})
        assert resposta.status_code in (302, 403), rota
    assert Unidade.objects.get(codigo="cefor").ativa is True
    assert not Unidade.objects.filter(codigo="serra").exists()


# --- Lista e ficha -----------------------------------------------------------------------------


def test_a_lista_mostra_ativas_e_desativadas(administradora):
    """FR-3314."""
    registrar_unidade("serra", sigla="Serra", nome="Campus Serra", ativa=False)

    pagina = _pagina(administradora.get(LISTA))

    assert "Campus Serra" in pagina and "Desativada" in pagina
    assert CEFOR["nome"] in pagina and "Ativa" in pagina
    assert reverse("interface:unidade", args=["serra"]) in pagina


def test_codigo_inexistente_e_404(administradora):
    """FR-3315."""
    for rota in ("interface:unidade", "interface:unidade-editar", "interface:unidade-desativar"):
        assert administradora.get(reverse(rota, args=["nao-existe"])).status_code == 404, rota


def test_a_ficha_mostra_o_historico_da_implantacao_e_da_pessoa(administradora):
    """FR-3315, `D-009`: o registro pela tela, e depois a alteração, mais recente primeiro."""
    assert _confirmar(administradora).status_code == 302
    pagina = _pagina(administradora.get(reverse("interface:unidade-editar", args=["serra"])))
    conferencia = _pagina(
        administradora.post(
            reverse("interface:unidade-editar", args=["serra"]),
            {**SERRA, "local": "Serra (ES) — sede", "acao": "conferir"},
        )
    )
    administradora.post(
        reverse("interface:unidade-editar", args=["serra"]),
        {
            **SERRA,
            "local": "Serra (ES) — sede",
            "acao": "confirmar",
            "motivo": "Ofício 2",
            "versao": _versao(conferencia),
        },
    )

    ficha = _pagina(administradora.get(reverse("interface:unidade", args=["serra"])))

    assert "Editar" in pagina
    historico = ficha[ficha.index("Histórico") :]
    assert historico.index("Alteração da unidade") < historico.index("Registro da unidade")
    assert "Inês Institucional" in historico
    assert "<dt>Local</dt><dd>Serra (ES) → Serra (ES) — sede</dd>" in historico
    assert "“Ofício 2”" in historico


# --- Cadastrar ---------------------------------------------------------------------------------


def test_o_cadastro_passa_pela_conferencia_que_nao_grava(administradora):
    """FR-3324, SC-1046: lista, formulário, conferência — e nada gravado antes de confirmar."""
    eventos = RegistroAuditoria.objects.count()

    formulario = _pagina(administradora.get(CADASTRAR))
    conferencia = _pagina(_conferir(administradora))

    assert 'name="codigo"' in formulario
    assert "Confira antes de cadastrar" in conferencia
    assert "permanente" in conferencia
    assert not Unidade.objects.filter(codigo="serra").exists()
    assert RegistroAuditoria.objects.count() == eventos

    resposta = _confirmar(administradora)

    assert resposta.status_code == 302
    assert resposta["Location"].startswith(reverse("interface:unidade", args=["serra"]))
    assert Unidade.objects.get(codigo="serra").ativa is True


def test_a_previa_usa_as_linhas_do_compositor(administradora):
    """FR-3324, `D-010`: as linhas da instituição, as da unidade, a sigla no anúncio e o local."""
    pagina = _pagina(_conferir(administradora, cabecalho_2="Unidade de teste", sigla="SerrA"))

    orgao = re.search(r'<p class="orgao">(.*?)</p>', pagina, re.S).group(1)
    assert orgao.split("<br>") == [
        "Ministério da Educação",
        "Instituto Federal do Espírito Santo",
        "Campus Serra",
        "Unidade de teste",
    ]
    assert "EDITAL Nº 1/" in pagina and "SerrA" in pagina, "a sigla sai como foi escrita"
    assert "Serra (ES), " in pagina


def test_a_previa_avisa_a_linha_que_nao_cabe(administradora):
    longa = "Centro de Referência em Formação e em Educação a Distância do Instituto Federal"
    pagina = _pagina(_conferir(administradora, cabecalho_1=longa))

    assert "não cabe" in pagina and longa in pagina


@pytest.mark.parametrize(
    "campos, campo",
    [
        ({"codigo": "Serra"}, "codigo"),
        ({"codigo": "institucional"}, "codigo"),
        ({"sigla": ""}, "sigla"),
    ],
)
def test_as_recusas_voltam_ao_formulario_com_os_valores(administradora, campos, campo):
    """EC-1: a recusa no campo, com o que foi digitado."""
    resposta = _conferir(administradora, nome="Nome digitado", **campos)
    pagina = _pagina(resposta)

    assert resposta.status_code == 422
    assert f'id="{campo}"' in pagina and 'aria-invalid="true"' in pagina
    assert 'value="Nome digitado"' in pagina
    assert not Unidade.objects.filter(nome="Nome digitado").exists()


def test_o_aviso_da_moldura_aparece_quando_muda_o_numero_de_ativas(administradora):
    """FR-3330, EC-7, nas três situações: a segunda ativa, a única que sai, a sigla da única."""
    segunda = _pagina(_conferir(administradora))
    assert "passam a dizer <strong>Ifes</strong>" in segunda

    desativar = _pagina(administradora.get(reverse("interface:unidade-desativar", args=["cefor"])))
    assert "passam a dizer <strong>Ifes</strong>" in desativar

    sigla = _pagina(
        administradora.post(
            reverse("interface:unidade-editar", args=["cefor"]),
            {
                **{k: v for k, v in CEFOR.items() if k not in ("cabecalho", "ativa")},
                "cabecalho_1": CEFOR["cabecalho"][0],
                "cabecalho_2": CEFOR["cabecalho"][1],
                "sigla": "CEFOR",
                "acao": "conferir",
            },
        )
    )
    assert "passam a dizer <strong>CEFOR/Ifes</strong>" in sigla


# --- Editar ------------------------------------------------------------------------------------


def test_a_edicao_mostra_antes_e_depois_e_ignora_o_codigo(administradora):
    """FR-3321, EC-9."""
    rota = reverse("interface:unidade-editar", args=["cefor"])
    campos = {
        **{k: v for k, v in CEFOR.items() if k not in ("cabecalho", "ativa")},
        "cabecalho_1": CEFOR["cabecalho"][0],
        "cabecalho_2": CEFOR["cabecalho"][1],
        "local": "Serra (ES)",
    }

    formulario = _pagina(administradora.get(rota))
    conferencia = _pagina(administradora.post(rota, {**campos, "acao": "conferir"}))
    resposta = administradora.post(
        rota,
        {
            **campos,
            "codigo": "outro",
            "acao": "confirmar",
            "motivo": "Ofício",
            "versao": _versao(conferencia),
        },
    )

    assert 'name="codigo"' not in formulario
    assert '<span class="antes">Vitória (ES)</span>' in conferencia
    assert '<span class="depois">Serra (ES)</span>' in conferencia
    assert resposta.status_code == 302
    assert Unidade.objects.get(codigo="cefor").local == "Serra (ES)"
    assert not Unidade.objects.filter(codigo="outro").exists()


def test_a_versao_antiga_e_recusada_na_tela(administradora):
    """FR-3325: outra pessoa alterou no meio."""
    rota = reverse("interface:unidade-editar", args=["cefor"])
    campos = {
        **{k: v for k, v in CEFOR.items() if k not in ("cabecalho", "ativa")},
        "cabecalho_1": CEFOR["cabecalho"][0],
        "cabecalho_2": CEFOR["cabecalho"][1],
        "local": "Serra (ES)",
    }
    conferencia = _pagina(administradora.post(rota, {**campos, "acao": "conferir"}))
    Unidade.objects.filter(codigo="cefor").update(nome="Mudado por outra pessoa")

    resposta = administradora.post(
        rota, {**campos, "acao": "confirmar", "motivo": "x", "versao": _versao(conferencia)}
    )

    assert resposta.status_code == 409
    assert "Outra pessoa alterou" in _pagina(resposta)
    assert Unidade.objects.get(codigo="cefor").local == "Vitória (ES)"


# --- Desativar e reativar ----------------------------------------------------------------------


def test_a_desativacao_diz_as_consequencias_e_desativa(administradora):
    """FR-3326, EC-6."""
    rota = reverse("interface:unidade-desativar", args=["cefor"])
    pagina = _pagina(administradora.get(rota))

    assert "deixa de receber Processo Seletivo, Edital e acesso novos" in pagina
    assert "Nada se exclui" in pagina
    resposta = administradora.post(
        rota, {"acao": "confirmar", "motivo": "Teste", "versao": _versao(pagina)}
    )

    assert resposta.status_code == 302
    assert Unidade.objects.get(codigo="cefor").ativa is False
    ficha = _pagina(administradora.get(reverse("interface:unidade", args=["cefor"])))
    assert reverse("interface:unidade-reativar", args=["cefor"]) in ficha


def test_sem_motivo_a_desativacao_volta_com_a_recusa(administradora):
    rota = reverse("interface:unidade-desativar", args=["cefor"])
    pagina = _pagina(administradora.get(rota))

    resposta = administradora.post(
        rota, {"acao": "confirmar", "motivo": "", "versao": _versao(pagina)}
    )

    assert resposta.status_code == 422
    assert Unidade.objects.get(codigo="cefor").ativa is True


def test_nenhuma_tela_oferece_exclusao(administradora):
    """FR-3329."""
    paginas = [
        _pagina(administradora.get(LISTA)),
        _pagina(administradora.get(reverse("interface:unidade", args=["cefor"]))),
        _pagina(administradora.get(reverse("interface:unidade-editar", args=["cefor"]))),
    ]
    for pagina in paginas:
        assert not re.search(r"[Ee]xcluir|[Aa]pagar", pagina)


def test_nenhuma_tela_tem_estilo_ou_script_embutido():
    """A CSP recusa o embutido (091, 092): ele sumiria em silêncio."""
    from pathlib import Path

    pasta = Path(__file__).resolve().parents[2] / "processo_seletivo/interface/templates/interface"
    for nome in (
        "unidades.html",
        "unidades_ficha.html",
        "unidades_formulario.html",
        "unidades_conferencia.html",
        "unidades_situacao.html",
        "_previa_do_cabecalho.html",
    ):
        texto = (pasta / nome).read_text(encoding="utf-8")
        assert not re.search(r"style=|<style|<script|\son[a-z]+=", texto), nome


def test_a_trilha_da_unidade_le_os_atos(client, settings):
    """FR-3331, `D-008`: os quatro atos aparecem na trilha da `108`, sem mudança nela."""
    from processo_seletivo.seguranca.domain import Actor
    from processo_seletivo.unidades.application import registro

    ines = Actor("ines.institucional", ESCOPO_INSTITUCIONAL, frozenset({"unidade:administrar"}))
    campos = {k: v for k, v in SERRA.items() if not k.startswith("cabecalho")}
    registro.registrar(ines, campos={**campos, "cabecalho": ["Campus Serra"]}, motivo="Portaria 1")
    editaveis = {**campos, "cabecalho": ["Campus Serra"], "atendimento": "serra@ifes.edu.br"}
    versao = registro.conferir_alteracao(ines, codigo="serra", campos=editaveis)["versao"]
    registro.alterar(
        ines, codigo="serra", campos=editaveis, versao_conferida=versao, motivo="Canal"
    )
    for ato, funcao in (("desativar", registro.desativar), ("reativar", registro.reativar)):
        versao = registro.consequencias(ines, codigo="serra", ato=ato)["versao"]
        funcao(ines, codigo="serra", versao_conferida=versao, motivo=ato)
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "aud", ["auditor"], escopo="serra")

    pagina = _pagina(client.get(reverse("interface:trilha-da-unidade")))

    assert pagina.count("Alteração da unidade") == 3
    assert "Registro da unidade" in pagina
    assert "<dt>Canal de atendimento</dt><dd>— → serra@ifes.edu.br</dd>" in pagina
    assert "Ativa → Desativada" in pagina and "Desativada → Ativa" in pagina
