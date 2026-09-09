"""A ordem não depende de gerador pseudoaleatório, e o módulo não integra vídeo (FR-026, FR-065).

**São as duas negativas que a feature precisa provar por varredura**, porque nenhuma delas aparece
num caminho feliz. A primeira é a diferença entre "sorteio" e "aleatório": um `random.shuffle` daria
uma ordem imprevisível **e irreproduzível**, e é justamente a reprodutibilidade que faz do ato uma
prova. A segunda é a fronteira da D-012: a transmissão continua sendo canal externo, e o dia em que
o sistema importar um cliente de vídeo será o dia em que ele passa a responder por ela.

A varredura é sobre **importações e chamadas**, e não sobre a prosa: os comentários deste módulo
falam de aleatoriedade e de transmissão o tempo todo, e devem falar.
"""

import ast
import pathlib

import pytest

pytestmark = [pytest.mark.integration]

RAIZ = pathlib.Path(__file__).resolve().parents[3] / "processo_seletivo" / "sorteios"

# `uuid` fica de fora de propósito: identidade sorteada não entra na ordem, e o `uuid4` das chaves
# primárias é o mesmo de todo agregado do sistema.
GERADORES = {"random", "secrets", "numpy", "numpy.random", "os.urandom"}
VIDEO = {"cv2", "ffmpeg", "streamlink", "obsws_python", "youtube_dl", "yt_dlp", "webrtc"}


def _modulos():
    return sorted(RAIZ.rglob("*.py"))


def _importados(arvore):
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


def test_a_varredura_encontra_o_modulo():
    """Sem esta linha, uma varredura que não achasse arquivo algum passaria em silêncio."""
    assert len(_modulos()) > 10


@pytest.mark.parametrize("caminho", _modulos(), ids=lambda c: c.name)
def test_nenhum_gerador_pseudoaleatorio_e_importado(caminho):
    importados = _importados(ast.parse(caminho.read_text(encoding="utf-8")))

    for gerador in GERADORES:
        assert gerador not in importados, f"{caminho.name} importa {gerador}"
        assert not any(nome.startswith(f"{gerador}.") for nome in importados), caminho.name


@pytest.mark.parametrize("caminho", _modulos(), ids=lambda c: c.name)
def test_nenhum_canal_de_video_e_importado_ou_roteado(caminho):
    """FR-065: o sistema não transmite, não grava e não integra canal de vídeo."""
    fonte = caminho.read_text(encoding="utf-8")
    importados = _importados(ast.parse(fonte))

    for biblioteca in VIDEO:
        assert biblioteca not in importados, f"{caminho.name} importa {biblioteca}"
    for chamada in ("rtmp://", "rtsp://", "VideoCapture(", "start_stream("):
        assert chamada not in fonte, f"{caminho.name} fala em {chamada}"


def test_a_ordem_vem_do_resumo_criptografico_e_de_mais_nada():
    """A afirmação positiva por trás da negativa: a chave é SHA-256 sobre bytes canônicos."""
    import inspect

    from processo_seletivo.sorteios.domain import chave

    fonte = inspect.getsource(chave)
    assert "hashlib.sha256" in fonte
    assert "random" not in fonte.replace("aleatori", "")


def test_a_mesma_entrada_produz_sempre_a_mesma_ordem():
    """Se houvesse gerador em algum lugar do caminho, esta afirmação falharia às vezes."""
    from processo_seletivo.sorteios.domain.chave import ordem

    entradas = {
        "relation_hash": "b" * 64,
        "draw_scope_id": "perfil-1",
        "seed": "0 4 8 1 5",
        "public_numbers": list(range(1, 51)),
    }

    assert len({tuple(ordem(**entradas)) for _ in range(20)}) == 1
