"""Captura as maquetes por file:// (versão 2), em PNG, numa pasta de saída.

Uso: uv run python capturar_maquetes.py <pasta-das-maquetes> <saida>
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

MAQUETES = Path(sys.argv[1]).resolve()
SAIDA = Path(sys.argv[2])
SAIDA.mkdir(parents=True, exist_ok=True)
TELAS = {
    "convocacao": ["desktop", "375", "320"],
    "convocacao-apos-envio": ["desktop", "375"],
    "convocacao-pendencia": ["desktop", "375"],
    "convocacao-sucessora": ["375"],
    "acesso-1-email": ["375"],
    "acesso-2-codigo": ["375"],
    "email": ["desktop", "375", "375-escuro"],
    "email-correcao": ["375"],
}
TAMANHOS = {"desktop": (1280, 900), "375": (375, 812), "375-escuro": (375, 812), "320": (320, 568)}

with sync_playwright() as p:
    navegador = p.chromium.launch()
    for nome, larguras in TELAS.items():
        for largura in larguras:
            w, h = TAMANHOS[largura]
            if nome.startswith("email") and largura == "desktop":
                w = 720
            contexto = navegador.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=1 if largura == "desktop" else 2,
                color_scheme="dark" if "escuro" in largura else "light",
            )
            pagina = contexto.new_page()
            sufixo = "#confirmacao" if nome == "convocacao-apos-envio" else ""
            pagina.goto((MAQUETES / f"{nome}.html").as_uri() + sufixo)
            pagina.screenshot(path=str(SAIDA / f"{nome}-{largura}.png"), full_page=not sufixo)
            if nome.startswith("convocacao") and largura in ("375", "320"):
                pagina.screenshot(path=str(SAIDA / f"{nome}-{largura}-primeira-tela.png"))
            print(nome, largura, "scrollWidth", pagina.evaluate("document.documentElement.scrollWidth"))
            contexto.close()
    navegador.close()
