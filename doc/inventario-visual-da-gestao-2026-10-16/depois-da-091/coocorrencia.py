"""Que classes aparecem juntas num mesmo elemento, em todos os modelos (091, R-003).

A prova de ordem mede nas páginas do inventário quais seletores alcançam um mesmo elemento. Um
seletor que não casa com nada lá — a série da supervisão, o lote da Distribuição, a trilha — não
tem medida, e a primeira versão o tratava como se casasse com tudo. Esta é a segunda fonte, estática
e mais larga que o inventário: para dois sujeitos (o último composto de cada seletor) alcançarem o
mesmo elemento, algum elemento de algum modelo tem de ter as classes dos dois, e uma marca que
aceite os dois tipos.

Do lado conservador em tudo:

- o atributo `class` é lido com os `{% if %}` abertos — `botao{% if x %} secundario{% endif %}`
  vale como `botao secundario`, o que só junta classes;
- uma classe com `{{ }}` — `s-{{ estado }}` — vale como qualquer classe com aquele prefixo;
- uma classe que algum script acrescenta (`classList.add`, `className =`, `classList.toggle`) pode
  estar em qualquer elemento;
- sujeito sem classe (`input`, `*`) só se separa de outro por tipo;
- classe que nenhum modelo, script ou módulo da gestão escreve não está em elemento nenhum dela:
  as fontes de classe são essas três (os `class="{{ }}"` inteiramente variáveis têm os valores em
  `VARIAVEIS`), e a regra que só a cita é regra morta.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3] / "backend/processo_seletivo"

_ELEMENTO = re.compile(r"<([a-zA-Z][\w-]*)\b([^<>]*?(?:\{[{%].*?[%}]\}[^<>]*?)*)>", re.S)
_CLASSE = re.compile(r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.S)
_TAG_DE_MODELO = re.compile(r"\{%.*?%\}", re.S)


# As classes inteiramente variáveis dos modelos da gestão, e os valores que o Python lhes dá. Uma
# variável que não esteja aqui vale como qualquer classe.
VARIAVEIS = {
    "peso": {"secundario", "perigoso"},  # `_acao_do_edital.html`; `acoes.SECUNDARIA`, `PERIGOSA`
    "acao.estilo": {"secundario", "perigoso"},  # `ato_ordenacao.html`; idem
    "linha.classe": {"sem-efeito", "fora-do-alcance"},  # `aplicacao_na_retificacao.CLASSE_DA_LINHA`
}


def elementos_dos_modelos():
    """(marca, classes fixas, prefixos de classe variável) de todo elemento com `class`.

    Só os modelos que a folha da gestão alcança — os da `interface` e os comuns; o portal tem a
    folha própria, e nenhum elemento dele recebe a da gestão.
    """
    encontrados = []
    modelos = [*RAIZ.glob("interface/templates/**/*.html"), *RAIZ.glob("shared/templates/**/*.html")]
    for modelo in sorted(modelos):
        texto = re.sub(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", "", modelo.read_text(), flags=re.S)
        for marca, atributos in _ELEMENTO.findall(texto):
            for achado in _CLASSE.finditer(atributos):
                valor = _TAG_DE_MODELO.sub(" ", achado.group(1) or achado.group(2) or "")
                fixas, prefixos = set(), set()
                for variavel in re.findall(r"\{\{\s*([\w.]+)\s*\}\}", valor):
                    fixas |= VARIAVEIS.get(variavel, set())
                for palavra in re.sub(r"\{\{\s*(%s)\s*\}\}" % "|".join(map(re.escape, VARIAVEIS)), " ", valor).split():
                    if "{{" in palavra or "}}" in palavra:
                        prefixos.add(palavra.split("{{")[0])
                    else:
                        fixas.add(palavra)
                encontrados.append((marca.lower(), frozenset(fixas), frozenset(prefixos)))
    return encontrados


def classes_dos_scripts():
    """O que os scripts e o Python fazem com classes: (classes acrescentadas, elementos criados).

    `classList.add`/`toggle`/`replace` põem a classe num elemento que já existe — qualquer um, para
    esta leitura. `className =`, `setAttribute("class", …)`, `class="…"` em texto de marcação e o
    terceiro argumento do `elemento()` da vista do conjunto criam elemento novo com aquelas
    classes, de marca desconhecida. O HTML que o Python monta entra do mesmo jeito.
    """
    acrescentadas, criados = set(), []
    for script in sorted(RAIZ.glob("interface/static/**/*.js")):
        if script.name.endswith(".min.js"):
            continue
        texto = script.read_text()
        for lista in re.findall(r"classList\.(?:add|toggle|replace)\(([^)]*)\)", texto):
            acrescentadas |= set(re.findall(r"""["']([\w-]+)["']""", lista))
        for padrao in (
            r"""className\s*[+]?=\s*["']([^"']*)["']""",
            r"""class=\\?["']([^"'\\]*)""",
            r"""setAttribute\(\s*["']class["']\s*,\s*["']([^"']*)""",
            r"""elemento\([^()]*,\s*["']([\w -]+)["']\s*\)""",
        ):
            for valor in re.findall(padrao, texto):
                criados.append((None, frozenset(valor.split()), frozenset()))
    for modulo in sorted([*RAIZ.glob("interface/**/*.py"), *RAIZ.glob("shared/**/*.py")]):
        texto = modulo.read_text()
        for padrao in (r"""class=\\?["']([^"'{\\]*)""", r"""["']class["']\s*:\s*["']([^"']*)"""):
            for valor in re.findall(padrao, texto):
                criados.append((None, frozenset(valor.split()), frozenset()))
    return acrescentadas, criados


ELEMENTOS = None
DINAMICAS = None


def _composto(seletor):
    """(marca ou None, classes, tem id) do composto, já alargado (sem pseudo e sem atributo)."""
    if seletor.startswith(":is("):
        return None
    marca = re.match(r"[a-zA-Z][\w-]*", seletor)
    return (
        marca.group(0).lower() if marca else None,
        set(re.findall(r"\.([\w-]+)", seletor)),
        "#" in seletor,
    )


def podem_coincidir(sujeito_a, sujeito_b):
    """Algum elemento de algum modelo pode casar com os dois sujeitos? Na dúvida, sim."""
    global ELEMENTOS, DINAMICAS
    if ELEMENTOS is None:
        DINAMICAS, criados = classes_dos_scripts()
        ELEMENTOS = elementos_dos_modelos() + criados
    a, b = _composto(sujeito_a), _composto(sujeito_b)
    if a is None or b is None or a[2] or b[2]:
        return True
    if a[0] and b[0] and a[0] != b[0]:
        return False
    marca = a[0] or b[0]
    exigidas = (a[1] | b[1]) - DINAMICAS
    conhecidas = {c for _, fixas, _ in ELEMENTOS for c in fixas}
    prefixos = {p for _, _, ps in ELEMENTOS for p in ps}
    if any(c not in conhecidas and not any(c.startswith(p) for p in prefixos) for c in exigidas):
        # Classe que nenhum modelo, script ou módulo da gestão escreve: não está em elemento
        # nenhum dela. É a regra morta — `.trilha` é do portal —, e ela não disputa com ninguém.
        return False
    if not exigidas:
        # Sem classe que separe, só a marca separaria — e ela já foi conferida.
        return True
    for elemento, fixas, prefixos in ELEMENTOS:
        if marca and elemento and elemento != marca:
            continue
        if all(c in fixas or any(c.startswith(p) for p in prefixos) for c in exigidas):
            return True
    return False
