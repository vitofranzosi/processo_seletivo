"""Escopos exatos do operador de laboratório; módulo puro, sem leitura, rede ou subprocesso.

Uma autorização não acumula ações. A matriz delimita efeitos declarados; os recibos e guardas
do operador continuam responsáveis por comprovar as identidades reais antes da execução.
"""

REVISAO = "5B.2-A.2"
ESCOPOS = {
    "inspecionar": {
        "recursos": ["engine-local-no-endpoint-aprovado"],
        "operacoes": ["engine.ler-identidade"],
    },
    "criar-recursos": {
        "recursos": ["cefor-f4-pg-20261016", "cefor-f4-app-20261016", "cefor-f4-rede-20261016",
                     "cefor_f4_pg_20261016", "cefor_f4_midia_20261016", "evidencias-locais-do-operador"],
        "operacoes": ["container.criar-parado", "rede.criar-interna", "volume.criar",
                      "volume.povoamento-inicial-da-imagem", "arquivo.evidencia-criar"],
    },
    "conferir": {
        "recursos": ["cefor-f4-tarefa-conferir-20261016", "ps_homologacao_f4_20261016",
                     "cefor-f4-rede-20261016", "cefor_f4_midia_20261016", "evidencias-locais-do-operador"],
        "operacoes": ["container.tarefa-criar", "container.tarefa-iniciar", "sql.somente-leitura",
                      "arquivo.evidencia-criar"],
    },
    "evidencias": {
        "recursos": ["recursos-identificados-no-recibo", "evidencias-locais-do-operador"],
        "operacoes": ["recurso.ler-metadados", "arquivo.evidencia-criar"],
    },
    "preservar": {
        "recursos": ["cefor-f4-app-20261016"],
        "operacoes": ["recurso.ler-metadados", "container.app-parar"],
    },
    "encerrar": {
        "recursos": ["containers-identificados-no-recibo"],
        "operacoes": ["recurso.ler-metadados", "container.parar"],
    },
}

# Grafo de planejamento: a presença aqui NÃO implementa nem autoriza uma operação.
DEPENDENCIAS = {
    "inspecionar": [],
    "adquirir-imagens": ["inspecionar"],
    "construir-imagens": ["adquirir-imagens"],
    "criar-recursos": ["construir-imagens"],
    "bootstrap-postgres": ["criar-recursos"],
    "iniciar-postgres": ["bootstrap-postgres"],
    "criar-banco": ["iniciar-postgres"],
    "papeis": ["criar-banco"],
    "migrar": ["papeis"],
    "proteger-esquema": ["migrar"],
    "conferir": ["proteger-esquema"],
    "baseline": ["conferir"],
    "iniciar": ["baseline"],
    "demonstrar": ["iniciar"],
    "evidencias": ["criar-recursos"],
    "preservar": ["criar-recursos"],
    "encerrar": ["criar-recursos"],
    "descartar": ["encerrar", "evidencias"],
}


def validar_grafo(grafo):
    visitados, ativos = set(), set()

    def visitar(acao):
        if acao not in grafo or acao in ativos:
            raise RuntimeError("Dependência ausente ou ciclo no plano")
        if acao in visitados:
            return
        ativos.add(acao)
        for anterior in grafo[acao]:
            visitar(anterior)
        ativos.remove(acao)
        visitados.add(acao)

    for acao in grafo:
        visitar(acao)


def validar_escopo(acao, documento):
    if (documento.get("revisao_operador") != REVISAO or acao not in ESCOPOS
        or documento.get("acoes") != [acao] or documento.get("cenarios", []) != []):
        raise RuntimeError("Uma única ação implementada, nesta revisão, é autorizável")
    escopo = documento.get("escopo")
    if not isinstance(escopo, dict) or set(escopo) != {"recursos", "operacoes"}:
        raise RuntimeError("Escopo ausente ou ambíguo")
    for chave in ("recursos", "operacoes"):
        valores = escopo[chave]
        if (not isinstance(valores, list) or not all(isinstance(v, str) for v in valores)
            or len(valores) != len(set(valores)) or set(valores) != set(ESCOPOS[acao][chave])):
            raise RuntimeError("Alvos ou efeitos fora do escopo exato")
