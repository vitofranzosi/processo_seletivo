"""O pacote do kit de divulgação: o ZIP e o manifesto (111, FR-3435, FR-3437, FR-3438, FR-3441).

**Dois níveis de determinismo** (FR-3438). A peça e os textos publicáveis não dependem do instante;
o ZIP inteiro depende, porque o manifesto e as notas dizem quando o material foi gerado. Por isso o
segundo nível se prova com o mesmo instante de referência, e o primeiro com dois instantes.

**Sem peça, o pacote sai mesmo assim** (EC-21): com a chave desligada, em host local ou com a peça
recusada, os três arquivos dela não entram, e o manifesto diz por quê.
"""

import io
import json
import zipfile
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import kit_de_divulgacao, kit_pacote, kit_peca
from processo_seletivo.portal import ficha as fichas
from tests.fixtures import kit
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db

PUBLICO = "gps.exemplo.ifes.edu.br"
DA_PECA = {"peca-feed-1080x1350.png", "peca-feed-1080x1350.svg", "texto-alternativo.txt"}

sem_rasterizador = pytest.mark.skipif(
    not kit_pacote.disponivel(), reason="o `resvg-py` não está instalado neste ambiente"
)


@pytest.fixture
def host_publico(settings):
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, PUBLICO]
    return PUBLICO


@pytest.fixture
def comunicacao(client, seletor_ligado):
    identificar(client, "cora.comunicacao", ["comunicacao"])
    return client


def _ficha(edital, agora, base_url=kit.BASE):
    return fichas.ler(edital, agora=agora, base_url=base_url)


def _pacote(ficha, *, motivo=""):
    return kit_de_divulgacao.pacote(ficha, manchete=None, motivo_sem_peca=motivo)[0]


def _abrir(dados):
    with zipfile.ZipFile(io.BytesIO(dados)) as arquivo:
        return {info.filename: arquivo.read(info) for info in arquivo.infolist()}


def _manifesto(dados):
    return json.loads(_abrir(dados)["manifesto.json"])


def _exportar(client, edital, host=None, **dados):
    dados.setdefault("impressao", _ficha(edital, timezone.now(), None).impressao)
    url = reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, "zip"])
    extra = {"HTTP_HOST": host} if host else {}
    return client.post(url, dados, **extra)


def _eventos(edital):
    return RegistroAuditoria.objects.filter(aggregate_id=edital.id, operation="EXPORTAR_MATERIAL")


@sem_rasterizador
def test_o_pacote_completo_tem_os_sete_arquivos_na_ordem_fixa(api_client):
    edital = kit.publicar(api_client, ate=1, chave="pacote-completo")
    dados = _pacote(_ficha(edital, timezone.now()))
    with zipfile.ZipFile(io.BytesIO(dados)) as arquivo:
        infos = arquivo.infolist()
    assert [info.filename for info in infos] == list(kit_pacote.ARQUIVOS)
    assert {info.date_time for info in infos} == {kit_pacote.DATA_FIXA}
    conteudo = _abrir(dados)
    assert conteudo["peca-feed-1080x1350.png"].startswith(b"\x89PNG")
    assert b"Edital Sans" in conteudo["peca-feed-1080x1350.svg"]
    assert conteudo["kit.txt"].decode().startswith("INFORMAÇÕES OFICIAIS")
    resumo = _manifesto(dados)["impressao"]["resumo"]
    assert json.loads(conteudo["ficha.json"])["impressao"] == resumo


@sem_rasterizador
def test_peca_e_textos_publicaveis_iguais_em_dois_instantes(api_client):
    edital = kit.publicar(api_client, ate=1, chave="pacote-dois-instantes")
    agora = timezone.now()
    primeiro = _abrir(_pacote(_ficha(edital, agora)))
    depois = _abrir(_pacote(_ficha(edital, agora + timedelta(minutes=37))))
    for nome in DA_PECA:
        assert primeiro[nome] == depois[nome], nome
    # Os textos publicáveis são os mesmos; as notas e o manifesto dizem o instante, por desenho.
    assert kit_textos_publicaveis(edital, agora) == kit_textos_publicaveis(
        edital, agora + timedelta(minutes=37)
    )
    assert primeiro["manifesto.json"] != depois["manifesto.json"]


def kit_textos_publicaveis(edital, agora):
    from processo_seletivo.interface import kit_textos

    return kit_textos.compor(_ficha(edital, agora))


def test_mesmo_zip_no_mesmo_instante_de_referencia(api_client):
    edital = kit.publicar(api_client, ate=1, chave="pacote-mesmo-instante")
    agora = timezone.now()
    assert _pacote(_ficha(edital, agora)) == _pacote(_ficha(edital, agora))


def test_manifesto_com_os_tres_instantes_e_sem_validade(api_client):
    edital = kit.publicar(api_client, "01", chave="pacote-manifesto")
    agora = timezone.now()
    ficha = _ficha(edital, agora)
    dados = _pacote(ficha)
    manifesto = _manifesto(dados)
    instantes = manifesto["instantes"]
    assert instantes["gerado_em"] == ficha.referencia
    assert instantes["versao_vigente_desde"] == {
        "instante": ficha.versao_desde,
        "ato": ficha.versao_ato,
    }
    marcos = {marco["marco"]: marco["instante"] for marco in instantes["proximos_marcos"]}
    assert ficha.retificacao_a_vigorar, "o 01/2026 do corpus tem Retificação a vigorar"
    assert marcos[kit_pacote.MARCO_DA_RETIFICACAO] == ficha.retificacao_a_vigorar
    assert manifesto["impressao"] == {
        "resumo": ficha.impressao,
        "versao": ficha.versao_da_impressao,
    }
    assert manifesto["template"] == kit_peca.TEMPLATE
    assert set(manifesto["fontes"]) == {"EditalSans-Regular.ttf", "EditalSans-Bold.ttf"}
    texto = _abrir(dados)["manifesto.json"].decode().lower()
    assert "validade" not in texto
    assert "válid" not in texto


def test_manifesto_resume_cada_arquivo(api_client):
    import hashlib

    edital = kit.publicar(api_client, ate=1, chave="pacote-resumos")
    dados = _pacote(_ficha(edital, timezone.now()))
    conteudo = _abrir(dados)
    resumos = {item["nome"]: item["sha256"] for item in _manifesto(dados)["arquivos"]}
    assert set(resumos) == set(conteudo) - {"manifesto.json"}
    for nome, resumo in resumos.items():
        assert hashlib.sha256(conteudo[nome]).hexdigest() == resumo


def test_periodo_futuro_tem_o_termino_entre_os_proximos_marcos(api_client):
    edital = kit.publicar(api_client, ate=1, chave="pacote-termino")
    ficha = _ficha(edital, timezone.now())
    instantes = _manifesto(_pacote(ficha))["instantes"]
    marcos = {m["marco"]: m["instante"] for m in instantes["proximos_marcos"]}
    assert marcos[kit_pacote.MARCO_DO_TERMINO] == ficha.fim


@pytest.mark.parametrize(
    "motivo",
    [kit_de_divulgacao.PECA_EM_VALIDACAO, kit_peca.HOST_LOCAL],
    ids=["chave-desligada", "host-local"],
)
def test_sem_peca_o_zip_sai_sem_os_tres_arquivos_e_diz_por_que(api_client, motivo):
    edital = kit.publicar(api_client, ate=1, chave=f"pacote-sem-peca-{len(motivo)}")
    dados = _pacote(_ficha(edital, timezone.now()), motivo=motivo)
    conteudo = _abrir(dados)
    assert not DA_PECA & set(conteudo)
    assert set(conteudo) == set(kit_pacote.ARQUIVOS) - DA_PECA
    assert _manifesto(dados)["peca"] == {"incluida": False, "motivo": motivo, "manchete": None}


def test_peca_recusada_o_zip_sai_sem_ela_com_o_motivo(api_client, monkeypatch):
    edital = kit.publicar(api_client, ate=1, chave="pacote-recusada")

    def recusar(ficha, *, manchete=None):
        raise kit_peca.PecaRecusada("A peça não desenha o caractere X, em título.")

    monkeypatch.setattr(kit_peca, "compor", recusar)
    dados = _pacote(_ficha(edital, timezone.now()))
    assert not DA_PECA & set(_abrir(dados))
    assert _manifesto(dados)["peca"]["motivo"] == "A peça não desenha o caractere X, em título."


@sem_rasterizador
def test_exportar_zip_registra_com_o_resumo_dos_bytes(api_client, comunicacao, host_publico):
    import hashlib

    edital = kit.publicar(api_client, ate=1, chave="pacote-exporta")
    resposta = _exportar(comunicacao, edital, host_publico)
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/zip"
    assert resposta["Content-Disposition"] == 'attachment; filename="kit-91-2026.zip"'
    assert resposta["X-Content-Type-Options"] == "nosniff"
    assert "no-store" in resposta["Cache-Control"]
    assert DA_PECA <= set(_abrir(resposta.content))
    detalhe = _eventos(edital).get().detalhe
    assert detalhe["formato"] == "zip"
    assert detalhe["template"] == kit_peca.TEMPLATE
    assert detalhe["sha256"] == hashlib.sha256(resposta.content).hexdigest()
    assert detalhe["sem_peca"] is None


def test_exportar_zip_em_host_local_sai_sem_peca_e_sem_link(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="pacote-local")
    resposta = _exportar(comunicacao, edital)  # testserver é host local
    assert resposta.status_code == 200
    conteudo = _abrir(resposta.content)
    assert not DA_PECA & set(conteudo)
    assert "https://" not in conteudo["kit.md"].decode()
    manifesto = json.loads(conteudo["manifesto.json"])
    assert manifesto["endereco_publico"] is None
    assert manifesto["peca"]["motivo"] == kit_peca.HOST_LOCAL
    detalhe = _eventos(edital).get().detalhe
    assert detalhe["template"] is None
    assert detalhe["sem_peca"] == kit_peca.HOST_LOCAL


def test_exportar_zip_com_a_chave_desligada(api_client, comunicacao, host_publico, settings):
    settings.KIT_DE_DIVULGACAO_PECA = False
    edital = kit.publicar(api_client, ate=1, chave="pacote-chave")
    resposta = _exportar(comunicacao, edital, host_publico)
    assert resposta.status_code == 200
    assert not DA_PECA & set(_abrir(resposta.content))
    assert _manifesto(resposta.content)["peca"]["motivo"] == kit_de_divulgacao.PECA_EM_VALIDACAO


def test_exportar_zip_com_impressao_antiga_e_recusado(api_client, comunicacao, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="pacote-mudou")
    conferida = _ficha(edital, timezone.now(), None).impressao
    kit.retificar(api_client, edital, "91", 2, chave="pacote-mudou")
    resposta = _exportar(comunicacao, edital, host_publico, impressao=conferida)
    assert resposta.status_code == 409
    assert not _eventos(edital).exists()


def test_exportar_zip_com_manchete_fora_da_lista_e_422(api_client, comunicacao, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="pacote-manchete")
    resposta = _exportar(comunicacao, edital, host_publico, manchete="7")
    assert resposta.status_code == 422
    assert not _eventos(edital).exists()


def test_nenhum_arquivo_e_guardado(api_client, comunicacao, host_publico, settings, tmp_path):
    """FR-3441: o pacote é montado na memória, e a única escrita é o evento da trilha."""
    settings.MEDIA_ROOT = str(tmp_path)
    edital = kit.publicar(api_client, ate=1, chave="pacote-nada-guardado")
    antes = RegistroAuditoria.objects.count()
    assert _exportar(comunicacao, edital, host_publico).status_code == 200
    assert list(tmp_path.iterdir()) == []
    assert RegistroAuditoria.objects.count() == antes + 1


def test_a_tela_oferece_o_pacote_por_formulario(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="pacote-na-tela")
    corpo = comunicacao.get(reverse("interface:kit-de-divulgacao", args=[edital.id])).content
    url = reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, "zip"])
    assert url in corpo.decode()
    assert "Baixar o pacote (.zip)" in corpo.decode()
