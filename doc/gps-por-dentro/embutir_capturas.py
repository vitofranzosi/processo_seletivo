"""Embute referências reais já existentes, sem arquivos externos para executar o guia."""

import base64
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PASTA = Path(__file__).resolve().parent
REFERENCIAS = {
    "config": (
        "doc/estudo-classificacao-demonstrativa-2026-11-07/capturas/12-compor-marco-entrevista.jpg",
        "Configuração real · Marcos classificatórios",
        "Captura real do estudo de 07/11/2026, edital demonstrativo 900/2026. Os números são de outro exemplo: o alvo desta tela é 8 por lista; na história deste guia é 4. Nomenclatura conferida nos templates da base da POC.",
    ),
    "ocupacao": (
        "doc/estudo-classificacao-demonstrativa-2026-11-07/capturas/40-ocupacao-final.jpg",
        "Tela real · Ocupação de vagas",
        "Captura real do estudo de 07/11/2026, após reversão. Tem outros números e uma reversão que não ocorre na história desta POC. Observe os quatro rótulos: Publicadas, Efetivas, Ocupadas e A ocupar.",
    ),
    "docs": (
        "specs/118-jornada-consolidada-do-convocado/capturas/depois/F-convocacao-desktop.jpg",
        "Portal real · Convocação e documentos",
        "Captura real de cenário de teste da 118, com documentos fictícios. Observe a separação entre pendências, prazo e dados da convocação. Os documentos e datas não são os da história deste guia.",
    ),
}


def gerar():
    telas = {}
    for chave, (caminho, titulo, legenda) in REFERENCIAS.items():
        dados = base64.b64encode((RAIZ / caminho).read_bytes()).decode()
        telas[chave] = {
            "titulo": titulo,
            "legenda": legenda,
            "alt": titulo + ". " + legenda,
            "src": "data:image/jpeg;base64," + dados,
        }
    arquivo = PASTA / "index.html"
    html = arquivo.read_text()
    inicio = html.index("<!-- TELAS_EMBUTIDAS -->")
    html = (
        html[:inicio]
        + "<!-- TELAS_EMBUTIDAS -->\n<script>Object.assign(TELAS,"
        + json.dumps(telas, ensure_ascii=False)
        + ");</script>\n</body></html>\n"
    )
    arquivo.write_text(html)
    print(
        "3 capturas reais embutidas, com origem e diferença de cenário identificadas."
    )


if __name__ == "__main__":
    gerar()
