"""Todo leitor da consequência do Resultado diz o que faz com a retirada da reserva (164, FR-7018).

**Por que existe.** A `164` acrescentou a terceira consequência, `RETIRADA_DA_RESERVA`, ao lado de
`HABILITADA` e `ELIMINADA`. Um leitor que só compara com `ELIMINADA` passa a tratar a retirada como
"não eliminada" — e a deixa ocupar a reserva; um que só compara com `HABILITADA` a trata como
"não habilitada" — e a para na Etapa seguinte. Nenhum dos dois quebra nada em execução: o defeito
é silencioso, e é exatamente o que a D-003 da `164` apontou ao recusar guardar a retirada como
`ELIMINADA` lida pelo Edital (SC-2335).

**O que ela cobra.** Todo arquivo de `processo_seletivo/` que lê a consequência — pelo enum ou pelo
literal — está no inventário abaixo, com a razão de estar bem. Leitor novo, fora dele, reprova: quem
o escreveu decide, e diz, o que ele faz com a retirada.
"""

import re
from pathlib import Path

APLICACAO = Path(__file__).resolve().parents[1] / "processo_seletivo"

LEITURA = re.compile(
    r"Consequencia\.(HABILITADA|ELIMINADA|RETIRADA_DA_RESERVA)"
    r"|[\"'](HABILITADA|ELIMINADA)[\"']"
    r"|\b(HABILITADA|ELIMINADA):"
)

TRATA_AS_TRES = "trata as três consequências"
SO_ETAPA_SEM_RESERVA = "lê Etapa que nunca é restrita (governada, de habilitação ou de análise)"
SO_HABILITADA = "só a habilitação importa aqui, e a retirada não habilita"
DEFINE = "define o vocabulário ou a regra"

INVENTARIO = {
    # Definições e a regra.
    "resultados/models.py": DEFINE,
    "resultados/domain/efeito.py": DEFINE,
    "resultados/domain/regra.py": DEFINE,
    "recursos/models.py": DEFINE,
    "classificacao/domain/universo_classificavel.py": (
        f"{TRATA_AS_TRES}: `que_tiram` — a retirada tira só da lista reservada"
    ),
    # O Resultado nasce.
    "resultados/application/consolidacao.py": f"{TRATA_AS_TRES}: o motivo da retirada",
    "resultados/application/ocorrencia.py": f"{TRATA_AS_TRES}: o efeito da ausência",
    # A progressão e as listas.
    "resultados/application/prontidao.py": (
        f"{TRATA_AS_TRES}: a eliminação exclui, a retirada segue (`SEGUEM`) e conta só pela ampla"
    ),
    "resultados/application/selectors.py": (
        f"{TRATA_AS_TRES}: `seguem_de`, `desfavoraveis_registrados` e `retirada` no acompanhamento"
    ),
    "classificacao/application/calculo.py": (
        f"{TRATA_AS_TRES}: `_sem_retirada_anterior` no universo reservado"
    ),
    "classificacao/application/reproducao.py": f"{TRATA_AS_TRES}: `que_tiram` do recorte do ato",
    "ocupacao/application/selectors.py": (
        f"{TRATA_AS_TRES}: `retiradas_da_reserva` na reserva, até o horizonte"
    ),
    "sorteios/application/habilitacao.py": (
        f"{TRATA_AS_TRES}: `para_o_recorte` tira a retirada da relação reservada"
    ),
    # O recurso.
    "recursos/domain/pejus.py": f"{TRATA_AS_TRES}: a ordem de gravidade",
    "recursos/application/julgar.py": (
        f"{SO_HABILITADA}: a correção contra Ocorrência habilita; o resto deriva da regra"
    ),
    # Os que leem Etapa sem reserva — a 163 impede a Etapa restrita nesses papéis.
    "ocupacao/application/destinacao.py": f"{SO_ETAPA_SEM_RESERVA}: eliminados na Etapa governada",
    "convocacao/application/desfechar.py": f"{SO_ETAPA_SEM_RESERVA}: regularização na governada",
    "convocacao/application/fluxo.py": f"{SO_ETAPA_SEM_RESERVA}: indeferimento na governada",
    "convocacao/application/selectors.py": (
        f"{SO_ETAPA_SEM_RESERVA}: reabilitadas por deferimento na governada"
    ),
    "divulgacao/application/inscricoes.py": f"{SO_ETAPA_SEM_RESERVA}: a Etapa de análise",
    "sorteios/application/sorteio.py": f"{SO_HABILITADA}: o sorteio grava o favorável que produz",
    # O que se lê.
    "interface/relatorio_do_edital.py": f"{TRATA_AS_TRES}: as retiradas contadas à parte",
    "interface/views.py": f"{TRATA_AS_TRES}: os nomes das três na confirmação da consolidação",
    "interface/previa_da_classificacao.py": (
        "a prévia não simula retirada (FR-7026): os candidatos fictícios só são eliminados"
    ),
}


def _leitores():
    encontrados = set()
    for padrao in ("*.py", "*.html"):
        for arquivo in APLICACAO.rglob(padrao):
            if "/migrations/" in arquivo.as_posix():
                continue
            if LEITURA.search(arquivo.read_text(encoding="utf-8", errors="ignore")):
                encontrados.add(arquivo.relative_to(APLICACAO).as_posix())
    return encontrados


def test_todo_leitor_da_consequencia_esta_classificado():
    soltos = sorted(_leitores() - set(INVENTARIO))
    assert not soltos, (
        "Leitura da consequência do Resultado fora do inventário da 164 (FR-7018). Diga o que o "
        f"arquivo faz com RETIRADA_DA_RESERVA e acrescente-o a INVENTARIO: {soltos}"
    )


def test_o_inventario_nao_guarda_quem_deixou_de_ler():
    """A entrada que sobra diz uma garantia que ninguém mais precisa dar — e esconde a próxima."""
    sobrando = sorted(set(INVENTARIO) - _leitores())
    assert not sobrando, f"Entradas do inventário que não leem mais a consequência: {sobrando}"


def test_a_varredura_reconhece_um_leitor():
    assert LEITURA.search("if r.consequencia == ResultadoEtapa.Consequencia.ELIMINADA:")
    assert LEITURA.search('consequencia="HABILITADA"')
