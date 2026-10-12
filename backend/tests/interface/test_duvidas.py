"""A tela de validação interna das respostas do assistente de dúvidas (070, contracts/tela.md).

O setor de seleção confere, na gestão, o que o assistente poderá dizer. Os casos prendem o alcance
(`D-010`), a entrada só com publicação (`FR-1413`), os rótulos em palavras (`UX-200`), a resposta
anunciada (`UX-204`) e as recusas em 200 com motivo (contracts/tela.md, *Portas e negativas*).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.edital import actor_headers
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="tela91")
    return edital


@pytest.fixture
def edital_01(api_client):
    edital, _ = publicar_do_corpus(api_client, "01", chave="tela01")
    return edital


def _url(edital, **parametros):
    consulta = "&".join(f"{chave}={valor}" for chave, valor in parametros.items())
    return reverse("interface:duvidas", args=[edital.id]) + (f"?{consulta}" if consulta else "")


def _texto(resposta):
    return re.sub(r"\s+", " ", resposta.content.decode())


def test_sem_identidade_a_tela_pede_identificacao(client, edital_91):
    resposta = client.get(_url(edital_91))
    assert resposta.status_code == 302
    assert resposta.url == reverse("interface:identificar")


def test_fora_do_escopo_a_tela_responde_como_inexistente(client, edital_91):
    identificar(client, "gestora", ["gestor"], escopo="outra-unidade")
    assert client.get(_url(edital_91)).status_code == 404


def test_a_entrada_aparece_na_pagina_do_edital_publicado(client, edital_91):
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(reverse("interface:detalhe", args=[edital_91.id])))
    assert reverse("interface:duvidas", args=[edital_91.id]) in corpo
    assert "Ver as respostas do assistente de dúvidas (validação interna)" in corpo


def test_edital_sem_publicacao_nao_tem_entrada_nem_respostas(client, api_client):
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-070-SEM-PUBLICACAO",
            "title": "Processo sem publicação",
            "firstEdital": {"number": "70", "year": 2026, "title": "Edital em elaboração"},
        },
        format="json",
        **actor_headers(
            "gestor-a", ["processo:criar", "edital:criar"], key="duvidas-sem-publicacao-0001"
        ),
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    identificar(client, "gestora", ["gestor"])

    detalhe = _texto(client.get(reverse("interface:detalhe", args=[edital.id])))
    assert reverse("interface:duvidas", args=[edital.id]) not in detalhe
    tela = client.get(_url(edital))
    assert tela.status_code == 200
    assert "Só Edital publicado tem respostas" in _texto(tela)


def test_a_tela_se_declara_interna_e_lista_as_perguntas_do_edital(client, edital_91):
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(_url(edital_91)))
    assert "Nada dela é exibido a candidatos" in corpo
    assert "Como funciona o sorteio?" in corpo
    assert "Pontos para revisão antes da abertura pública" in corpo


def test_a_resposta_traz_versao_tipo_e_os_tres_rotulos_em_palavras(client, edital_91):
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(_url(edital_91, pergunta="P-05", perfil="INF-BJN", modalidade="PPI")))
    assert 'aria-live="polite"' in corpo
    assert 'id="titulo-resposta" tabindex="-1" autofocus' in corpo
    assert "Versão vigente desde" in corpo
    assert "Respondida pelos dados" in corpo
    for rotulo in ("Texto do Edital", "Dado da versão vigente", "Explicação"):
        assert rotulo in corpo
    assert "Abrir o documento deste ato" in corpo
    assert "Edital completo" not in corpo


def test_pergunta_que_nao_se_aplica_e_recusada_com_motivo(client, edital_01):
    identificar(client, "gestora", ["gestor"])
    resposta = client.get(_url(edital_01, pergunta="P-09", perfil="DOC-INFO"))
    assert resposta.status_code == 200
    assert "Esta pergunta não se aplica a este Edital." in _texto(resposta)


def test_perfil_inexistente_e_recusado_com_motivo(client, edital_91):
    identificar(client, "gestora", ["gestor"])
    resposta = client.get(_url(edital_91, pergunta="P-03", perfil="XYZ"))
    assert resposta.status_code == 200
    assert "O Perfil XYZ não existe na versão vigente deste Edital." in _texto(resposta)


# ---- US2 -------------------------------------------------------------------------------------


# O último instante do calendário passa do limite do `datetime` ao ir para UTC: era 500.
@pytest.mark.parametrize("em", ["ontem", "9999-12-31T23:59"])
def test_instante_invalido_consulta_no_presente_e_diz(client, edital_91, em):
    identificar(client, "gestora", ["gestor"])
    resposta = client.get(_url(edital_91, em=em, pergunta="P-01"))
    corpo = _texto(resposta)
    assert resposta.status_code == 200
    assert "O instante informado não foi entendido; a consulta usa o presente." in corpo
    assert "Respondida pelos dados" in corpo


def test_o_formulario_carrega_a_versao_e_o_aviso_de_mudanca_vem_antes_da_versao(client, api_client):
    from tests.fixtures.corpus import retificar_do_corpus

    edital, deslocamento = publicar_do_corpus(api_client, "91", ate=1, chave="tela-mudanca")
    identificar(client, "gestora", ["gestor"])
    primeira = _texto(client.get(_url(edital, pergunta="P-03", perfil="INF-BJN")))
    versao = re.search(r'name="versao" value="([0-9a-f-]{36})"', primeira).group(1)

    retificar_do_corpus(api_client, edital, "91", 2, deslocamento, chave="tela-mudanca")
    segunda = _texto(client.get(_url(edital, pergunta="P-03", perfil="INF-BJN", versao=versao)))
    aviso = segunda.index("Este Edital mudou desde a resposta anterior")
    assert aviso < segunda.index("Versão vigente desde")


# ---- US3 e US4 -------------------------------------------------------------------------------


def _dois_canais(publicado):
    secao = next(s for s in publicado["sections"] if s["key"] == "disposicoes-finais")
    secao["content"] += (
        "\nDúvidas sobre a matrícula também podem ser enviadas a "
        "matricula.demo@exemplo.ifes.edu.br."
    )


def _sem_canal(publicado):
    secao = next(s for s in publicado["sections"] if s["key"] == "disposicoes-preliminares")
    secao["content"] = "\n".join(
        linha for linha in secao["content"].split("\n") if "@" not in linha
    )


@pytest.mark.parametrize(
    ("pergunta", "perfil", "tipo"),
    [
        ("P-08", "INF-BJN", "Depende da leitura do Edital"),
        ("P-03", "INF-BJN", "Respondida pelos dados"),
    ],
)
def test_o_tipo_vem_em_palavras(client, edital_91, pergunta, perfil, tipo):
    identificar(client, "gestora", ["gestor"])
    assert tipo in _texto(client.get(_url(edital_91, pergunta=pergunta, perfil=perfil)))


def test_o_aviso_de_anexo_leva_ao_anexo(client, api_client):
    edital, _ = publicar_do_corpus(api_client, "92", chave="tela-anexo")
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(_url(edital, pergunta="P-07", perfil="TD-ADM")))
    assert "que esta consulta não lê" in corpo
    assert re.search(r'href="/api/v1/public/anexos/[0-9a-f-]{36}">ANEXO IV', corpo)


def test_dois_canais_sao_fontes_divergentes_e_ponto_para_revisao(client, api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="tela-canais", mudar=_dois_canais)
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(_url(edital, pergunta="P-11")))
    assert "Fontes divergentes" in corpo
    assert "O Edital informa mais de um canal para dúvidas" in corpo
    assert "selecao.demo@exemplo.ifes.edu.br" in corpo
    assert "matricula.demo@exemplo.ifes.edu.br" in corpo


def test_sem_canal_no_edital_vale_o_institucional_rotulado(client, api_client, settings):
    settings.PORTAL_ATENDIMENTO = "atendimento@exemplo.ifes.edu.br"
    edital, _ = publicar_do_corpus(api_client, "91", chave="tela-sem-canal", mudar=_sem_canal)
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(_url(edital, pergunta="P-11")))
    assert "O canal institucional é atendimento@exemplo.ifes.edu.br" in corpo
    assert "canal que o Edital informa" not in corpo


def test_sem_canal_nenhum_a_resposta_diz_que_nao_ha_canal_informado(client, api_client, settings):
    settings.PORTAL_ATENDIMENTO = ""
    edital, _ = publicar_do_corpus(api_client, "91", chave="tela-nenhum", mudar=_sem_canal)
    identificar(client, "gestora", ["gestor"])
    corpo = _texto(client.get(_url(edital, pergunta="P-11")))
    assert "O Edital não informa" in corpo
    assert "Nem o Edital nem a implantação informam um canal para dúvidas." in corpo
