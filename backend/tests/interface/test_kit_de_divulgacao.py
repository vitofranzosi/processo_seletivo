"""A tela do kit de divulgação: a ação, os modos, as faixas e a forma (111, FR-3401, FR-3443)."""

import pytest
from django.urls import reverse

from tests.fixtures import kit
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db

PUBLICO = "gps.exemplo.ifes.edu.br"


@pytest.fixture
def host_publico(settings):
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, PUBLICO]
    return PUBLICO


def _url(edital):
    return reverse("interface:kit-de-divulgacao", args=[edital.id])


def test_a_acao_aparece_so_com_a_capacidade(api_client, client, seletor_ligado):
    edital = kit.publicar(api_client, ate=1, chave="acao-do-kit")
    detalhe = reverse("interface:detalhe", args=[edital.id])
    identificar(client, "cora.comunicacao", ["comunicacao"])
    assert _url(edital) in client.get(detalhe).content.decode()
    identificar(client, "gustavo.gestor", ["gestor"])
    assert _url(edital) not in client.get(detalhe).content.decode()


def test_antes_da_publicacao_a_acao_e_indisponivel_com_motivo(client, seletor_ligado, edital):
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "O kit de divulgação fica disponível quando o Edital for publicado." in corpo


def test_tela_com_periodo(api_client, client, seletor_ligado, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="tela-do-kit")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    resposta = client.get(_url(edital), HTTP_HOST=host_publico)
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "no-store" in resposta["Cache-Control"]
    for trecho in (
        "Confira as informações oficiais",
        "Polo Bom Jesus do Norte: 40 vagas",
        "Legenda para rede social",
        "busque por 91/2026 – Cefor",
        # O esquema é o da requisição: `https` em produção, atrás do proxy, e `http` aqui.
        f"//{host_publico}/selecoes/{edital.id}/",
        'name="impressao"',
        "Copiar",
    ):
        assert trecho in corpo, trecho


def test_tela_neutra_e_sem_material(api_client, client, seletor_ligado):
    neutro = kit.publicar(api_client, chave="tela-neutra", mudar=kit.sem_periodo)
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(neutro)).content.decode()
    assert "não recebe inscrições pelo GPS" in corpo


def test_host_local_sem_link_absoluto(api_client, client, seletor_ligado):
    edital = kit.publicar(api_client, ate=1, chave="tela-local")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(edital)).content.decode()  # testserver é host local
    assert "O endereço público não é conhecido neste acesso" in corpo
    assert "http://testserver/selecoes" not in corpo


def test_exportacoes_por_formulario(api_client, client, seletor_ligado):
    """Sem script, exportar funciona: são formulários comuns (EC-22)."""
    edital = kit.publicar(api_client, ate=1, chave="tela-formulario")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(edital)).content.decode()
    for formato in ("md", "txt"):
        assert reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, formato]) in corpo
    assert 'method="post"' in corpo


def test_nenhum_estilo_nem_script_embutido(api_client, client, seletor_ligado):
    edital = kit.publicar(api_client, ate=1, chave="tela-csp")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(edital)).content.decode()
    assert ' style="' not in corpo and "<style" not in corpo
    assert "onclick=" not in corpo
    assert "interface/kit-de-divulgacao.js" in corpo


# ---- A peça (111, incremento B: FR-3422, FR-3432, FR-3442, FR-3446, FR-3447, D-014, D-021) -----


def _impressao(edital):
    from django.utils import timezone

    from processo_seletivo.portal import ficha as fichas

    return fichas.ler(edital, agora=timezone.now(), base_url=None).impressao


def _previa(client, edital, host, **params):
    params.setdefault("impressao", _impressao(edital))
    url = reverse("interface:kit-de-divulgacao-previa", args=[edital.id])
    return client.get(url, params, HTTP_HOST=host)


def _exportar_peca(client, edital, formato, host, **dados):
    dados.setdefault("impressao", _impressao(edital))
    url = reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, formato])
    return client.post(url, dados, HTTP_HOST=host)


def _eventos(edital):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    return RegistroAuditoria.objects.filter(aggregate_id=edital.id, operation="EXPORTAR_MATERIAL")


@pytest.fixture
def comunicacao(client, seletor_ligado):
    identificar(client, "cora.comunicacao", ["comunicacao"])
    return client


sem_rasterizador = pytest.mark.skipif(
    not __import__("processo_seletivo.interface.kit_pacote", fromlist=["x"]).disponivel(),
    reason="o `resvg-py` não está instalado neste ambiente",
)


@sem_rasterizador
def test_a_tela_mostra_a_previa_e_o_texto_alternativo(api_client, comunicacao, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="peca-tela")
    corpo = comunicacao.get(_url(edital), HTTP_HOST=host_publico).content.decode()
    previa = reverse("interface:kit-de-divulgacao-previa", args=[edital.id])
    assert f'src="{previa}?impressao={_impressao(edital)}"' in corpo
    assert "Texto alternativo da peça" in corpo
    assert "Peça de divulgação do Cefor/Ifes" in corpo
    for formato in ("png", "svg"):
        assert reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, formato]) in corpo


@sem_rasterizador
def test_previa_png_privada_e_sem_registro(api_client, comunicacao, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="peca-previa")
    resposta = _previa(comunicacao, edital, host_publico)
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "image/png"
    assert resposta["Content-Disposition"] == "inline"
    assert resposta["X-Content-Type-Options"] == "nosniff"
    assert "no-store" in resposta["Cache-Control"]
    assert resposta.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert not _eventos(edital).exists()


def test_previa_com_impressao_antiga_e_recusada(api_client, comunicacao, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="peca-mudou")
    conferida = _impressao(edital)
    kit.retificar(api_client, edital, "91", 2, chave="peca-mudou")
    resposta = _previa(comunicacao, edital, host_publico, impressao=conferida)
    assert resposta.status_code == 409
    assert "O Edital mudou desde que você abriu o kit" in resposta.content.decode()


@pytest.mark.parametrize("manchete", ["0", "x"])
def test_manchete_fora_da_lista_e_422(api_client, comunicacao, host_publico, manchete):
    edital = kit.publicar(api_client, ate=1, chave=f"peca-manchete-{manchete}")
    # O 91/2026 tem título que cabe: nenhuma manchete é oferecida, e qualquer índice é inválido.
    assert _previa(comunicacao, edital, host_publico, manchete=manchete).status_code == 422
    resposta = _exportar_peca(comunicacao, edital, "svg", host_publico, manchete=manchete)
    assert resposta.status_code == 422
    assert not _eventos(edital).exists()


@sem_rasterizador
def test_exportar_png_registra_com_o_template(api_client, comunicacao, host_publico):
    from processo_seletivo.interface import kit_peca

    edital = kit.publicar(api_client, ate=1, chave="peca-png")
    resposta = _exportar_peca(comunicacao, edital, "png", host_publico)
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "image/png"
    assert resposta["Content-Disposition"] == 'attachment; filename="kit-91-2026.png"'
    assert resposta["X-Content-Type-Options"] == "nosniff"
    (evento,) = _eventos(edital)
    assert evento.detalhe["formato"] == "png"
    assert evento.detalhe["template"] == kit_peca.TEMPLATE
    assert evento.detalhe["manchete"] is None


def test_exportar_svg_com_a_politica_propria(api_client, comunicacao, host_publico):
    import hashlib

    edital = kit.publicar(api_client, ate=1, chave="peca-svg")
    resposta = _exportar_peca(comunicacao, edital, "svg", host_publico)
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "image/svg+xml"
    assert resposta["Content-Disposition"] == 'attachment; filename="kit-91-2026.svg"'
    assert resposta["X-Content-Type-Options"] == "nosniff"
    assert resposta["Content-Security-Policy"] == (
        "default-src 'none'; style-src 'unsafe-inline'; font-src data:; img-src data:"
    )
    corpo = resposta.content.decode()
    assert "@font-face" in corpo and 'data-campo="periodo_curto"' in corpo
    (evento,) = _eventos(edital)
    assert evento.detalhe["sha256"] == hashlib.sha256(resposta.content).hexdigest()


def test_host_local_sem_peca(api_client, comunicacao):
    from processo_seletivo.interface import kit_peca

    edital = kit.publicar(api_client, ate=1, chave="peca-local")
    corpo = comunicacao.get(_url(edital)).content.decode()  # testserver é host local
    assert kit_peca.HOST_LOCAL in corpo
    assert _previa(comunicacao, edital, "testserver").status_code == 404
    assert _exportar_peca(comunicacao, edital, "svg", "testserver").status_code == 404
    assert not _eventos(edital).exists()


def test_chave_desligada_a_peca_some_e_os_textos_ficam(
    api_client, comunicacao, host_publico, settings
):
    from processo_seletivo.interface.kit_de_divulgacao import PECA_EM_VALIDACAO

    settings.KIT_DE_DIVULGACAO_PECA = False
    edital = kit.publicar(api_client, ate=1, chave="peca-desligada")
    corpo = comunicacao.get(_url(edital), HTTP_HOST=host_publico).content.decode()
    assert PECA_EM_VALIDACAO in corpo
    assert "Legenda para rede social" in corpo
    assert "previa.png" not in corpo
    assert _previa(comunicacao, edital, host_publico).status_code == 404
    for formato in ("png", "svg"):
        assert _exportar_peca(comunicacao, edital, formato, host_publico).status_code == 404
    url = reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, "md"])
    md = comunicacao.post(url, {"impressao": _impressao(edital)}, HTTP_HOST=host_publico)
    assert md.status_code == 200


def test_institucional_fora_da_versao_congelada_so_sai_liberada(
    api_client, comunicacao, host_publico, settings, monkeypatch
):
    """119, FR-3835, EC-23: outro resumo da Institucional não sai pela chave da `111`.

    O resumo congelado trocado simula a versão nova; a chave da `111` continua ligada, e a peça só
    volta quando a configuração nova nomeia o resumo do código.
    """
    from processo_seletivo.interface import kit_familias
    from processo_seletivo.interface.kit_familias import institucional

    monkeypatch.setattr(institucional, "RESUMO_CONGELADO_V1", "0" * 64)
    settings.KIT_DE_DIVULGACAO_PECA = True
    settings.KIT_DE_DIVULGACAO_TEMPLATES = tuple(
        e for e in settings.KIT_DE_DIVULGACAO_TEMPLATES if e[0] != "institucional"
    )
    edital = kit.publicar(api_client, ate=1, chave="peca-versao-nova")
    corpo = comunicacao.get(_url(edital), HTTP_HOST=host_publico).content.decode()
    assert kit_familias.VERSAO_EM_APROVACAO in corpo
    assert _previa(comunicacao, edital, host_publico).status_code == 404
    assert _exportar_peca(comunicacao, edital, "svg", host_publico).status_code == 404
    assert not _eventos(edital).exists()

    curto = kit_familias.resumo(institucional.POST)[: kit_familias.RESUMO_CURTO]
    settings.KIT_DE_DIVULGACAO_TEMPLATES = (("institucional", "post", 1, curto),)
    assert _exportar_peca(comunicacao, edital, "svg", host_publico).status_code == 200


def test_peca_recusada_diz_o_motivo_e_exportar_e_409(
    api_client, comunicacao, host_publico, monkeypatch
):
    from processo_seletivo.interface import kit_peca

    def recusar(ficha, *, manchete=None):
        raise kit_peca.PecaRecusada("A peça não desenha o caractere «≥» (U+2265).")

    monkeypatch.setattr(kit_peca, "compor", recusar)
    edital = kit.publicar(api_client, ate=1, chave="peca-recusada")
    corpo = comunicacao.get(_url(edital), HTTP_HOST=host_publico).content.decode()
    assert "U+2265" in corpo
    assert "Legenda para rede social" in corpo
    resposta = _exportar_peca(comunicacao, edital, "svg", host_publico)
    assert resposta.status_code == 409
    assert "U+2265" in resposta.content.decode()
    assert _previa(comunicacao, edital, host_publico).status_code == 404
