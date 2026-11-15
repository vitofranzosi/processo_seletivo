"""A fotografia dos estados do piloto do design system (172, FR-7716 a FR-7722, D-005).

Monta cada estado do catálogo (`tests/navegador/piloto/`), abre a tela com o papel dele e grava,
nas cinco larguras do estudo, a captura da página inteira e o inventário de conteúdo. A mesma
jornada roda sobre a `main` (o "antes") e sobre o piloto (o "depois"), e
`doc/auditoria-design-system-2026-11-14/piloto/scripts/comparar.py` compara as duas pastas.

**Só sob demanda**: sem `PILOTO_DS_FOTOGRAFIA=<pasta>`, o módulo pula inteiro. Não é guardião, e não
entra no veredito da suíte (D-009, FR-7719). O que ela verifica é só que o estado pedido foi
alcançado (FR-7718) — o resto é da comparação.

**Uma página por estado, redimensionada**: o retorno de um gesto só existe depois do POST, e
recarregar a página o repetiria. A janela muda de tamanho sobre a mesma página, e a medida da
dobra, a 1280 × 800, é a última.
"""

import json
import os
import platform
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador")

PASTA = os.getenv("PILOTO_DS_FOTOGRAFIA")
if not PASTA:
    pytest.skip("a fotografia do piloto roda só com PILOTO_DS_FOTOGRAFIA", allow_module_level=True)

from tests.navegador.piloto.estados import carregar  # noqa: E402
from tests.navegador.piloto.inventario import DOBRA_JS, INVENTARIO_JS, OUVIR_A_CSP  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

LARGURAS = (375, 768, 1280, 1440, 1920)
ALTURA = 900
DOBRA = (1280, 800)
CATALOGO = carregar()


def _commit():
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "?"


@pytest.fixture(scope="module", autouse=True)
def _registro_da_fotografia():
    pasta = Path(PASTA)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "fotografia.json").write_text(
        json.dumps(
            {
                "commit": _commit(),
                "larguras": LARGURAS,
                "dobra": DOBRA,
                "maquina": platform.platform(),
            },
            indent=1,
        )
    )


def _abrir(navegador, live_server, montagem):
    contexto = navegador.new_context(viewport={"width": 1440, "height": ALTURA}, locale="pt-BR")
    sessao = montagem.cliente.cookies.get("sessionid")
    if sessao is not None:
        contexto.add_cookies([{"name": "sessionid", "value": sessao.value, "url": live_server.url}])
    contexto.add_init_script(OUVIR_A_CSP)
    pagina = contexto.new_page()
    pagina.goto(live_server.url + montagem.url)
    if montagem.gesto is not None:
        montagem.gesto(pagina)
        pagina.wait_for_load_state("networkidle")
    return contexto, pagina


@pytest.mark.parametrize("codigo", sorted(CATALOGO))
def test_fotografa_o_estado(codigo, navegador, live_server, request):
    estado = CATALOGO[codigo]
    montagem = estado.montar(request)
    contexto, pagina = _abrir(navegador, live_server, montagem)
    try:
        texto = pagina.inner_text("main")
        assert estado.prova in " ".join(texto.split()), (
            f"{codigo}: o estado pedido não foi alcançado — falta «{estado.prova}» na tela "
            f"({pagina.url})"
        )
        destino = Path(PASTA) / codigo
        destino.mkdir(parents=True, exist_ok=True)
        for largura in LARGURAS:
            pagina.set_viewport_size({"width": largura, "height": ALTURA})
            pagina.wait_for_timeout(150)
            inventario = pagina.evaluate(INVENTARIO_JS)
            inventario.update(
                codigo=codigo,
                largura=largura,
                papel=estado.papel,
                tela=estado.tela,
                violacoes_de_csp=pagina.evaluate("window.__violacoes || []"),
            )
            pagina.screenshot(path=str(destino / f"{largura}.png"), full_page=True)
            (destino / f"{largura}.json").write_text(
                json.dumps(inventario, ensure_ascii=False, indent=1)
            )
        if estado.acao_principal:
            pagina.set_viewport_size({"width": DOBRA[0], "height": DOBRA[1]})
            pagina.evaluate("window.scrollTo(0, 0)")
            pagina.wait_for_timeout(150)
            dobra = pagina.evaluate(DOBRA_JS, estado.acao_principal)
            arquivo = destino / f"{DOBRA[0]}.json"
            inventario = json.loads(arquivo.read_text())
            inventario["dobra"] = dobra
            arquivo.write_text(json.dumps(inventario, ensure_ascii=False, indent=1))
    finally:
        contexto.close()
