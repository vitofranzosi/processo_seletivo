"""Confere o relatório do veraPDF contra o manifesto dos exemplares (178, FR-8168).

    uv run python scripts/conferir_o_verapdf.py <manifesto.json> <relatorio.json>

O manifesto (`tests/pdfa/test_exemplares.py`) diz, por arquivo, o nível que ele tem de declarar —
`2u` ou `2a`. O veraPDF valida cada arquivo contra o que ele **declara**; este roteiro exige, além
da conformidade, que a declaração seja a esperada. Sem isso, um documento que passasse a declarar 2b
por engano passaria verde.

Sai com 1, e diz o arquivo e as regras, se algum exemplar faltar no relatório, não for conforme ou
declarar outro nível. Biblioteca padrão só: roda no runner sem instalar nada.
"""

import json
import sys
from pathlib import Path

PERFIS = {
    "2u": "PDF/A-2u validation profile",
    "2a": "PDF/A-2a validation profile",
}


def conferir(manifesto, relatorio):
    """`[str]`: um problema por linha; vazia quando tudo confere."""
    resultados = {}
    for job in relatorio["report"]["jobs"]:
        nome = Path(job["itemDetails"]["name"]).name
        validacao = job.get("validationResult") or [{}]
        resultados[nome] = validacao[0] if isinstance(validacao, list) else validacao
    problemas = []
    for arquivo, nivel in sorted(manifesto.items()):
        resultado = resultados.get(arquivo)
        if resultado is None:
            problemas.append(f"{arquivo}: ausente do relatório do veraPDF")
            continue
        perfil = resultado.get("profileName", "?")
        if perfil != PERFIS[nivel]:
            problemas.append(f"{arquivo}: validado por {perfil!r}, e devia declarar {nivel}")
        if not resultado.get("compliant"):
            regras = [
                f"{regra['clause']}-{regra['testNumber']} {regra.get('description', '')[:90]}"
                for regra in resultado.get("details", {}).get("ruleSummaries", [])
            ]
            problemas.append(f"{arquivo}: não conforme em {perfil}")
            problemas.extend(f"    {regra}" for regra in regras)
    return problemas


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    manifesto = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    relatorio = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    problemas = conferir(manifesto, relatorio)
    for linha in problemas:
        print(linha)
    if problemas:
        return 1
    print(f"{len(manifesto)} exemplares conformes, cada um no nível esperado.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
