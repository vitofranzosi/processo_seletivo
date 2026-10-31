"""A regra de uma Unidade: a mesma para a semente, o cadastro e a edição (110, `D-005`, FR-3318).

Até a `110`, ela morava na sincronização e só valia para o arquivo. Com a tela, haveria duas: a do
arquivo e a do formulário, e a primeira correção de uma não chegaria à outra. Uma função pura,
que recebe os campos e devolve os valores aparados ou a primeira recusa, com o campo — para a tela
pôr a mensagem no lugar certo, como as autoridades da `060` fazem.

**A situação não é desta regra.** `ativa` muda só por desativar e reativar, que não passam por
formulário; na semente, quem confere o booleano é o leitor do arquivo.
"""

import re

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
    if not isinstance(codigo, str) or not CODIGO.match(codigo) or len(codigo) > CODIGO_MAXIMO:
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


def validar_campos(campos):
    """Sigla, nome, cabeçalho, local e canal aparados, ou a primeira recusa (FR-3318).

    O canal é opcional: vazio é "não declarado", e então vale o canal da instituição (109).
    """
    valores = {}
    for campo in ("sigla", "nome", "local"):
        valor = campos.get(campo)
        valor = valor.strip() if isinstance(valor, str) else ""
        if not valor or len(valor) > LIMITES[campo]:
            raise DomainError(
                nomes.CAMPO_OBRIGATORIO,
                f"{ROTULOS[campo]} deve ser preenchido, com até {LIMITES[campo]} caracteres.",
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
    # só. Que forma ele tem é política de atendimento, que o sistema não decide (109, P-2).
    if (
        not isinstance(atendimento, str)
        or "\n" in atendimento
        or "\r" in atendimento
        or len(atendimento.strip()) > ATENDIMENTO_MAXIMO
    ):
        raise DomainError(
            nomes.ATENDIMENTO_INVALIDO,
            f"O canal de atendimento deve ser uma linha só, de até {ATENDIMENTO_MAXIMO} "
            "caracteres — ou ficar vazio, para valer o canal da instituição.",
            422,
            campo="atendimento",
        )
    valores["atendimento"] = atendimento.strip()
    return valores
