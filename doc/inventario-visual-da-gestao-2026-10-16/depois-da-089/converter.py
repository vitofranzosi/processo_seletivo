"""Converte a folha comum da gestão do modelo para arquivo estático (089, R-001 e R-002).

    converter.py            (de backend/, sobre o modelo de antes)

Lê o `<style>` do `interface/base.html` e o parcial dos tokens, e grava
`interface/static/interface/gestao.css` e `shared/static/shared/tokens.css`: as mesmas linhas, na mesma
ordem, com `{% comment %}`/`{% endcomment %}` trocados por `/*`/`*/`. Não reformata nada — vários
guardiões ancoram no formato (`^` multilinha, `\\n}` no fim de `@media`).

Roda uma vez. Depois dele, os `.css` são a fonte, e o modelo perde a folha (à mão, no mesmo commit).
"""

from pathlib import Path

BASE = Path("processo_seletivo/interface/templates/interface/base.html")
TOKENS = Path("processo_seletivo/shared/templates/shared/_tokens.css.html")
GESTAO_CSS = Path("processo_seletivo/interface/static/interface/gestao.css")
TOKENS_CSS = Path("processo_seletivo/shared/static/shared/tokens.css")

INCLUSAO = '{% include "shared/_tokens.css.html" %}\n'
PONTO_DE_EXTENSAO = "{% comment %}\n**O estilo daquela página, e não de todas** (040)."

# O único comentário que cita a sintaxe do comentário de CSS. Copiado como está, o `*/` dele fecharia
# o comentário no meio, e o resto da prosa entraria no seletor da regra seguinte (R-002).
CITA_A_SINTAXE = "escrito com\n`/* */`, este bloco"
CITA_A_SINTAXE_CONVERTIDA = "escrito como\ncomentário de CSS, este bloco"
PREMISSA_ANTIGA = "pesada do sistema. `\n{% endcomment %}"
NOTA_DA_089 = (
    "pesada do sistema. `\n\n"
    "**Desde a 089 a premissa não vale mais:** a folha saiu do HTML para este arquivo, que viaja uma vez e\n"
    "fica no cache, e os comentários vieram com ela, junto de cada regra (D-002 da `089`).\n"
    "{% endcomment %}"
)

CABECALHO_GESTAO = """/*
A folha comum da gestão (089). Até a 089 ela era o `<style>` do `interface/base.html` e viajava em toda
resposta HTML de `/gestao/`; agora viaja uma vez e fica no cache. As regras e a ordem são as de antes,
linha a linha — vários guardiões ancoram no formato, e não se reformata.

Carregada depois de `shared/tokens.css` e antes do estilo de cada página (o bloco `estilo_da_pagina`,
que continua no modelo). Os comentários eram de modelo enquanto a folha estava no HTML; aqui são de CSS.
*/
"""


def converter(texto):
    texto = texto.replace("{% comment %}", "/*").replace("{% endcomment %}", "*/")
    assert "{%" not in texto and "%}" not in texto and "{{" not in texto, "sintaxe de modelo restante"
    return texto


modelo = BASE.read_text(encoding="utf-8")
inicio = modelo.index("<style>\n" + INCLUSAO) + len("<style>\n" + INCLUSAO)
fim = modelo.index(PONTO_DE_EXTENSAO)
folha = modelo[inicio:fim].rstrip("\n") + "\n"

assert folha.count(CITA_A_SINTAXE) == 1 and folha.count(PREMISSA_ANTIGA) == 1
folha = folha.replace(CITA_A_SINTAXE, CITA_A_SINTAXE_CONVERTIDA).replace(PREMISSA_ANTIGA, NOTA_DA_089)

GESTAO_CSS.write_text(CABECALHO_GESTAO + converter(folha), encoding="utf-8")
TOKENS_CSS.parent.mkdir(parents=True, exist_ok=True)
TOKENS_CSS.write_text(converter(TOKENS.read_text(encoding="utf-8")), encoding="utf-8")
print(GESTAO_CSS, len(GESTAO_CSS.read_bytes()), "bytes;", TOKENS_CSS, len(TOKENS_CSS.read_bytes()), "bytes")
