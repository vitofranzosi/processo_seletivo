"""O teto de inscrições por candidato como o conteúdo publicado o admite (015, FR-063; D-3).

**Uma regra, dois caminhos.** A composição a aplica ao gravar (`editais/application/teto.py`), e a
conferência de publicação a aplica ao conteúdo que vai vigorar (`validation.py`,
`_faixa_do_teto`) — que é o que a Retificação atravessa. Até 28/09 só o primeiro caminho a tinha: a
Retificação convertia o campo por `int()` e publicava teto `0` ou negativo, e com `0` o envio
recusava a primeira inscrição de todo mundo (RC-12, registro pré-piloto de 28/09).

**Vazio é sem limite, e não há valor por omissão.** É a ausência que a `FR-063` declara, e é o
comportamento de todo Edital anterior a este campo. O mínimo é 1: teto zero recusaria a primeira
inscrição de todo mundo, e um Edital que não recebe inscrição diz isso não designando o período.
"""

from processo_seletivo.shared.api.problems import DomainError

CAMPO = "max_inscricoes_por_candidato"

#: O maior valor que a coluna guarda — `integer` do PostgreSQL. Sem o limite, um número longo
#: digitado chegaria ao banco e voltaria como erro 500, e não como recusa junto do campo.
MAXIMO_DA_COLUNA = 2_147_483_647


def teto_declarado(bruto):
    """O teto como o conteúdo publicado o guarda: inteiro a partir de 1, ou `None` sem limite."""
    if bruto is None or (isinstance(bruto, str) and not bruto.strip()):
        return None
    if isinstance(bruto, bool):
        raise _recusa_do_valor()
    if isinstance(bruto, str):
        texto = bruto.strip()
        # `isdecimal`, e não `int()` direto: `int` aceita "+2", "1_0" e dígitos de outras
        # escritas, e nenhum deles é o que alguém quis dizer num campo de quantidade.
        if not (texto.isascii() and texto.isdecimal()):
            raise _recusa_do_valor()
        bruto = int(texto)
    if not isinstance(bruto, int) or bruto < 1:
        raise _recusa_do_valor()
    if bruto > MAXIMO_DA_COLUNA:
        raise DomainError(
            "field_constraint_violated",
            "Inscrições por candidato: o número é grande demais. Deixe em branco para não limitar.",
            422,
            campo=CAMPO,
        )
    return bruto


def _recusa_do_valor():
    return DomainError(
        "field_constraint_violated",
        "Inscrições por candidato é um número inteiro a partir de 1. Deixe em branco para não "
        "limitar.",
        422,
        campo=CAMPO,
    )
