"""Toda citação de requisito aponta para um requisito que existe.

**Por que existe.** Três passadas de revisão da `010` encontraram, cada uma, uma citação a
identificador inventado: um `SC-011` com sufixo de letra no quickstart, o mesmo de novo numa
docstring de teste, e um `FR-040` com sufixo em `associacao.py` — nenhum dos três definido em
especificação alguma. Nenhuma das três foi achada pela passada anterior, e o motivo foi sempre o
mesmo: a varredura era feita com o padrão do que já se sabia procurar. Uma citação errada não quebra
nada em execução — ela quebra a leitura, que é o que a rastreabilidade existe para sustentar
(Princípio V). É defeito silencioso por natureza, e por isso vira teste.

**O que ela protege.** Um comentário que cita uma regra convida quem lê a procurá-la, e quem procura
não encontra nada — nem sabe se ela foi renumerada, revogada, ou se nunca existiu. Pior no sentido
inverso: renumerar um requisito é barato **porque** este teste denuncia quem ficou para trás.

**Este arquivo é varrido como qualquer outro**, e por isso os exemplos acima aparecem descritos e
não escritos: um identificador inventado citado aqui seria, ele próprio, uma citação para o nada.
Quem verifica que a varredura ainda enxerga é
`test_a_varredura_reconhece_um_identificador_inventado`.

**Onde ela não vale.** Os `checklists/` são artefatos de revisão: eles apontam lacunas e
**propõem** identificadores que ainda não existem — é o trabalho deles. E o rascunho de entrada da
`010` guarda a numeração anterior ao `/speckit-specify`, de propósito e com aviso no topo.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SPECS = RAIZ / "specs"
BACKEND = RAIZ / "backend"

# `SC-UX-001` vem primeiro na alternância: sem isso o `SC-` casaria sozinho e a família de
# experiência da `009` seria lida como um `SC` comum, que não existe com aquele número.
CITACAO = re.compile(r"\b(SC-UX-\d+[a-z]?|(?:FR|SC|UX)-\d+[a-z]?)\b")
DEFINICAO = re.compile(r"\*\*(SC-UX-\d+[a-z]?|(?:FR|SC|UX)-\d+[a-z]?)\*\*")
DECISAO = re.compile(r"\b(D-\d+)\b")
# O nível do título não importa, e o arquivo é o da feature: a `012` fechou as decisões dela
# **antes** do planejamento, e por isso elas moram na §5 da spec, em `###`, enquanto a
# `research.md` guarda as questões técnicas em `T-NNN`. Exigir `##` em `research.md` prenderia
# o hábito das features que puderam decidir depois, e não a regra — que é a decisão estar
# declarada dentro da feature que a produziu.
DECISAO_DEFINIDA = re.compile(r"^#{2,4} (D-\d+)", re.M)
ONDE_SE_DECIDE = ("research.md", "spec.md")

IGNORADOS = ("checklists", "rascunho-de-entrada.md")
FORA_DA_ARVORE = (".venv", "__pycache__", "node_modules", "htmlcov", ".pytest_cache")


def requisitos_definidos() -> set[str]:
    """Todo identificador que alguma especificação define, de todas as features.

    De **todas**, e não só da feature em questão: o código da `010` cita `FR-053a` e `FR-075a`, que
    são da `009`, e uma varredura por feature acusaria os dois como inventados. Foi esse falso
    positivo que quase escondeu, no meio do ruído, a citação inventada verdadeira.
    """
    definidos: set[str] = set()
    for spec in sorted(SPECS.glob("*/spec.md")):
        definidos |= set(DEFINICAO.findall(spec.read_text(encoding="utf-8")))
    return definidos


def _relevante(caminho: Path) -> bool:
    return not any(parte in FORA_DA_ARVORE for parte in caminho.parts) and not any(
        ignorado in caminho.parts or caminho.name == ignorado for ignorado in IGNORADOS
    )


def arquivos_que_citam() -> list[Path]:
    """Onde uma citação pode aparecer: no código, nos testes e nos artefatos de especificação."""
    fontes = [
        arquivo
        for padrao in ("*.py", "*.html", "*.js")
        for arquivo in BACKEND.rglob(padrao)
        if _relevante(arquivo)
    ]
    documentos = [arquivo for arquivo in SPECS.rglob("*.md") if _relevante(arquivo)]
    return sorted(fontes + documentos)


def _citacoes_perdidas(arquivo: Path, definidos: set[str]) -> list[str]:
    texto = arquivo.read_text(encoding="utf-8", errors="ignore")
    return sorted({ident for ident in CITACAO.findall(texto) if ident not in definidos})


def test_nenhuma_citacao_aponta_para_requisito_inexistente():
    definidos = requisitos_definidos()

    perdidas = {
        arquivo.relative_to(RAIZ): faltando
        for arquivo in arquivos_que_citam()
        if (faltando := _citacoes_perdidas(arquivo, definidos))
    }

    relatorio = "\n".join(
        f"  {arquivo}: {', '.join(ids)}" for arquivo, ids in sorted(perdidas.items())
    )
    assert not perdidas, f"citações a requisitos inexistentes em especificação alguma:\n{relatorio}"


def test_nenhuma_decisao_citada_esta_ausente_da_pesquisa():
    """As decisões são por feature: `D-020` da `010` não é a `D-020` da `009`.

    Aqui a varredura é feita **dentro** de cada feature, ao contrário da dos requisitos — e é o que
    faz sentido, porque uma decisão só é lida no contexto que a produziu.

    Onde ela é declarada varia, e não deveria fazer diferença: a `009`, a `010` e a `011` decidiram
    durante a pesquisa e escreveram em `research.md`; a `012` fechou as dela **antes** do
    planejamento, e escreveu na spec. O que o teste cobra é que a decisão citada exista na feature,
    não em qual dos dois arquivos ela ficou.
    """
    perdidas = {}
    for feature in sorted(SPECS.glob("*/")):
        onde = [feature / nome for nome in ONDE_SE_DECIDE]
        if not any(arquivo.exists() for arquivo in onde):
            continue
        decisoes = {
            identificador
            for arquivo in onde
            if arquivo.exists()
            for identificador in DECISAO_DEFINIDA.findall(arquivo.read_text(encoding="utf-8"))
        }
        for artefato in sorted(feature.rglob("*.md")):
            if not _relevante(artefato):
                continue
            texto = artefato.read_text(encoding="utf-8")
            faltando = sorted({d for d in DECISAO.findall(texto) if d not in decisoes})
            if faltando:
                perdidas[artefato.relative_to(RAIZ)] = faltando

    relatorio = "\n".join(
        f"  {artefato}: {', '.join(ids)}" for artefato, ids in sorted(perdidas.items())
    )
    assert not perdidas, f"decisões citadas e ausentes do research.md da feature:\n{relatorio}"


def _expandir(intervalos: str) -> set[str]:
    """`FR-049 a FR-052c` cobre FR-049, FR-050, FR-051 e FR-052 — e as letras que a linha nomear.

    A matriz agrupa requisitos vizinhos numa linha só, e é bom que agrupe: uma linha por requisito
    faria a matriz repetir o mesmo arquivo de teste dezenas de vezes. O que o intervalo **não**
    cobre são as letras, que precisam ser citadas de forma explícita — foi assim que duas linhas
    perdidas na `010` passaram despercebidas.
    """
    cobertos = set(CITACAO.findall(intervalos))
    for prefixo, inicio, fim in re.findall(
        r"\b((?:FR|SC|UX))-(\d+)[a-z]? a (?:FR|SC|UX)?-?(\d+)[a-z]?", intervalos
    ):
        for numero in range(int(inicio), int(fim) + 1):
            cobertos.add(f"{prefixo}-{numero:03d}")
    return cobertos


def test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature():
    """Onde existir matriz, ela alcança cada requisito — inclusive os de sufixo de letra.

    Uma linha perdida na matriz é invisível: o requisito continua implementado e testado, e só a
    leitura fica sem o caminho. Aconteceu na `010`, com duas linhas que um script abortado nunca
    gravou.
    """
    faltando = {}
    for matriz in sorted(SPECS.glob("*/rastreabilidade.md")):
        spec = matriz.parent / "spec.md"
        exigidos = set(DEFINICAO.findall(spec.read_text(encoding="utf-8")))
        cobertos = _expandir(matriz.read_text(encoding="utf-8"))
        # Sem tolerância para o sufixo de letra: `FR-031a` **não** é coberto por "FR-029 a FR-031".
        # A primeira versão deste teste aceitava a base como substituta, e com isso reproduzia o
        # próprio defeito que ele existe para pegar — as duas linhas perdidas da `010` tinham base
        # coberta por um intervalo, e passariam batido.
        ausentes = sorted(ident for ident in exigidos if ident not in cobertos)
        if ausentes:
            faltando[matriz.relative_to(RAIZ)] = ausentes

    assert not faltando, "requisitos sem linha na matriz de rastreabilidade:\n" + "\n".join(
        f"  {matriz}: {', '.join(ids)}" for matriz, ids in sorted(faltando.items())
    )


def test_a_varredura_reconhece_um_identificador_inventado():
    """A prova de que o padrão ainda enxerga — sem escrever um identificador falso em lugar nenhum.

    Uma expressão regular que deixa de casar não falha: ela aprova tudo, calada. É o mesmo risco que
    o teste de alcance cobre do outro lado.
    """
    definidos = requisitos_definidos()
    inventado = "FR-" + "999z"
    assert inventado not in definidos

    achados = [
        ident
        for ident in CITACAO.findall(f"o comentário cita ({inventado}) e também (FR-001)")
        if ident not in definidos
    ]

    assert achados == [inventado]


def test_a_varredura_alcanca_o_que_promete():
    """Sem isto, renomear uma pasta transformaria a garantia em silêncio aprovado.

    O risco é real: os três defeitos que este arquivo existe para pegar escaparam justamente de
    varreduras que olhavam menos do que pareciam olhar.
    """
    definidos = requisitos_definidos()
    arquivos = arquivos_que_citam()

    assert len(definidos) >= 150, "as especificações deixaram de ser lidas"
    assert len(arquivos) >= 300, "a árvore varrida encolheu"
    assert any(a.suffix == ".py" for a in arquivos) and any(a.suffix == ".md" for a in arquivos)
    citam = sum(
        1 for a in arquivos if CITACAO.search(a.read_text(encoding="utf-8", errors="ignore"))
    )
    assert citam >= 50, (
        "quase nenhum arquivo cita requisito — o padrão de citação provavelmente parou de casar"
    )
