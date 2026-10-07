"""Quando uma autoridade responde — função pura da vigência e da data (FR-1119, FR-1120).

**A situação é derivada, e não coluna.** *Futura*, *vigente* e *encerrada* são a vigência lida
contra a data de hoje; uma coluna de situação divergiria dela à meia-noite, sem que ato nenhum a
mudasse.
"""

FUTURA = "futura"
VIGENTE = "vigente"
ENCERRADA = "encerrada"


def vigente(autoridade, data) -> bool:
    """Início e fim inclusivos; fim nulo é aberto. `data` é a do ato, no fuso institucional."""
    if data < autoridade.inicio_vigencia:
        return False
    return autoridade.fim_vigencia is None or data <= autoridade.fim_vigencia


def situacao(autoridade, hoje) -> str:
    if hoje < autoridade.inicio_vigencia:
        return FUTURA
    if autoridade.fim_vigencia is not None and hoje > autoridade.fim_vigencia:
        return ENCERRADA
    return VIGENTE


def periodo(autoridade) -> str:
    """`desde 06/10/2026` ou `de 06/10/2026 a 31/12/2026`: o período como a tela o diz."""
    inicio = autoridade.inicio_vigencia.strftime("%d/%m/%Y")
    if autoridade.fim_vigencia is None:
        return f"desde {inicio}"
    return f"de {inicio} a {autoridade.fim_vigencia.strftime('%d/%m/%Y')}"
