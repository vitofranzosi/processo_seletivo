"""A regra de uma Unidade: a mesma para a semente, o cadastro e a edição (110, `D-005`, FR-3318).

Até a `110`, ela morava na sincronização e só valia para o arquivo. Com a tela, haveria duas: a do
arquivo e a do formulário, e a primeira correção de uma não chegaria à outra. Uma função pura,
que recebe os campos e devolve os valores aparados ou a primeira recusa, com o campo — para a tela
pôr a mensagem no lugar certo, como as autoridades da `060` fazem.

**A situação não é desta regra.** `ativa` muda só por desativar e reativar, que não passam por
formulário; na semente, quem confere o booleano é o leitor do arquivo.
"""

import re
import unicodedata

from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.domain import nomes

CODIGO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CODIGO_MAXIMO = 100
ATENDIMENTO_MAXIMO = 255
LINHA_DO_CABECALHO_MAXIMA = 255
# Os limites das colunas (`unidades/0001`): o formulário diz o limite antes de o banco recusar.
LIMITES = {"sigla": 30, "nome": 255, "local": 120}
ROTULOS = {"sigla": "A sigla", "nome": "O nome", "local": "O local"}

# Os campos que a tela edita — o código não está entre eles: é permanente (FR-3321).
EDITAVEIS = ("sigla", "nome", "cabecalho", "local", "atendimento")


def validar_codigo(codigo):
    """O código como foi digitado, ou a recusa. **Não converte**: o código é permanente (EC-1).

    Uma conversão silenciosa — tirar o espaço, baixar a caixa — decidiria por quem cadastra um
    valor que nunca mais muda.
    """
    # `fullmatch`, e não `match`: com `match`, o `$` aceita uma quebra de linha no fim, e "serra\n"
    # viraria um código permanente com um caractere invisível (revisão de código do #352).
    if not isinstance(codigo, str) or not CODIGO.fullmatch(codigo) or len(codigo) > CODIGO_MAXIMO:
        raise DomainError(
            nomes.CODIGO_INVALIDO,
            "O código deve ter só letras minúsculas, dígitos e hífen, sem espaço, sem hífen nas "
            f"pontas e sem dois seguidos, com até {CODIGO_MAXIMO} caracteres — por exemplo, "
            "campus-serra.",
            422,
            campo="codigo",
        )
    if codigo == ESCOPO_INSTITUCIONAL:
        # O escopo dos vínculos que não são de unidade (106, `D-011`): uma unidade com este código
        # receberia, sem ninguém conceder, o que o Administrador institucional concede.
        raise DomainError(
            nomes.CODIGO_RESERVADO,
            f"O código {ESCOPO_INSTITUCIONAL} é reservado ao nível institucional. Escolha outro.",
            422,
            campo="codigo",
        )
    return codigo


def _uma_linha(texto):
    """Sem quebra de linha nem outro caractere de controle: todo campo da unidade é uma linha.

    O compositor do PDF não divide linhas por `\n` — a sigla vai ao anúncio do ato e as linhas do
    cabeçalho ao topo do documento oficial, que depois de publicado não se corrige.
    """
    return not any(unicodedata.category(caractere) == "Cc" for caractere in texto)


def validar_campos(campos):
    """Sigla, nome, cabeçalho, local e canal aparados, ou a primeira recusa (FR-3318).

    O canal é opcional: vazio é "não declarado", e então vale o canal da instituição (109).
    """
    valores = {}
    for campo in ("sigla", "nome", "local"):
        valor = campos.get(campo)
        valor = valor.strip() if isinstance(valor, str) else ""
        if not valor or len(valor) > LIMITES[campo] or not _uma_linha(valor):
            raise DomainError(
                nomes.CAMPO_OBRIGATORIO,
                f"{ROTULOS[campo]} deve ser preenchido numa linha só, com até {LIMITES[campo]} "
                "caracteres.",
                422,
                campo=campo,
            )
        valores[campo] = valor
    linhas = campos.get("cabecalho")
    if (
        not isinstance(linhas, list | tuple)
        or not 1 <= len(linhas) <= 2
        or not all(isinstance(linha, str) and linha.strip() for linha in linhas)
        or any(len(linha.strip()) > LINHA_DO_CABECALHO_MAXIMA for linha in linhas)
        or not all(_uma_linha(linha.strip()) for linha in linhas)
    ):
        raise DomainError(
            nomes.CABECALHO_INVALIDO,
            "O cabeçalho deve ter uma ou duas linhas preenchidas — o nome da unidade como o "
            "documento oficial o imprime.",
            422,
            campo="cabecalho",
        )
    valores["cabecalho"] = [linha.strip() for linha in linhas]
    atendimento = campos.get("atendimento") or ""
    # O canal entra no meio de uma frase da mensagem — "fale com {canal}." —, e por isso uma linha
    # só. Que forma ele tem é política de atendimento, que o sistema não decide (109, P-2). Aparado
    # antes de conferir, como os outros campos: a quebra só nas pontas é espaço, e sai.
    atendimento = atendimento.strip() if isinstance(atendimento, str) else None
    if atendimento is None or len(atendimento) > ATENDIMENTO_MAXIMO or not _uma_linha(atendimento):
        raise DomainError(
            nomes.ATENDIMENTO_INVALIDO,
            f"O canal de atendimento deve ser uma linha só, de até {ATENDIMENTO_MAXIMO} "
            "caracteres — ou ficar vazio, para valer o canal da instituição.",
            422,
            campo="atendimento",
        )
    valores["atendimento"] = atendimento
    return valores
