"""Identificadores, nomes e CPFs dos cenários — todos derivados, nenhum digitado (134, FR-4630).

**Por que derivar, e não sortear.** Perfis, Etapas, marcos e Eventos têm identidade **global**: o
mesmo UUID em dois Editais é recusado (`identifier_belongs_to_another_edital`). Os construtores do
`seed_demo` usam `00000000-0000-0000-00NN-…`, com dois dígitos do número do Edital, e cem números
não bastam para rodadas sucessivas de quinze cenários — e colidiriam com as demonstrações que já
existem na homologação. Aqui cada rodada tem o seu espaço: `uuid5(unidade, cenário, rodada,
posição)`, que é estável entre execuções e distinto entre rodadas.

**A unidade entra em tudo o que é global.** Identificadores, e-mails, sujeitos e concurso do
sorteio são únicos no banco inteiro, e não por unidade: sem ela na derivação, o C04 da segunda
unidade a carregar esbarrava nos Perfis do C04 da primeira, reaproveitava as pessoas dela e
observava o mesmo concurso — e todo cenário falhava.
"""

import hashlib
import re
import uuid

# Fixo: mudá-lo mudaria a identidade de todo cenário já gerado, e a verificação deixaria de
# reconhecê-los.
ESPACO = uuid.UUID("6f1c2a52-6d0e-5b8e-9a43-1340a0c0ffee")

# O número que os construtores do `seed_demo` recebem para montar o molde. Ele nunca chega ao
# banco: `remapear` troca toda ocorrência antes do rascunho ser gravado.
MOLDE = "99"
_PREFIXO_DO_MOLDE = f"00000000-0000-0000-00{MOLDE}-0000000000"


_CODIGO_LEGIVEL = re.compile(r"[a-z0-9][a-z0-9-]{0,23}")


def etiqueta(unidade):
    """A unidade como pedaço de e-mail, sujeito e correlação: o código, quando ele cabe e é legível.

    O código da unidade é texto livre de até 100 caracteres, e a correlação da trilha tem 100 no
    total. Um código fora da forma vira um resumo curto dele — distinto, e estável.
    """
    codigo = unidade.lower()
    if _CODIGO_LEGIVEL.fullmatch(codigo):
        return codigo
    return "u" + hashlib.sha256(unidade.encode()).hexdigest()[:10]


def identificador(unidade, codigo, rodada, posicao):
    return str(uuid.uuid5(ESPACO, f"{unidade}/{codigo}/r{rodada}/{posicao}"))


def remapear(valor, unidade, codigo, rodada):
    """O mesmo molde, com os identificadores desta rodada — e nada além deles mudado."""
    if isinstance(valor, dict):
        return {chave: remapear(item, unidade, codigo, rodada) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [remapear(item, unidade, codigo, rodada) for item in valor]
    if isinstance(valor, str) and valor.startswith(_PREFIXO_DO_MOLDE) and len(valor) == 36:
        return identificador(unidade, codigo, rodada, valor[-2:])
    return valor


def do_molde(posicao):
    """O identificador do molde numa posição, para nomear uma peça antes de remapear."""
    return f"{_PREFIXO_DO_MOLDE}{posicao}"


# Quantas pessoas cabem numa rodada. O CPF tem quatro dígitos para a rodada e a ordem juntas, e
# este é o passo entre uma rodada e a seguinte: com ele, os números só se repetem depois da
# rodada 500 de um mesmo cenário.
PESSOAS_POR_RODADA = 20


def cpf(codigo, rodada, ordem):
    """Um CPF com dígitos verificadores corretos, gerado e não colhido de ninguém (FR-4631).

    **Começa sempre por 000**, para saltar aos olhos de quem lê a lista. Os seis dígitos seguintes
    são o cenário (dois) e a posição da pessoa na sequência das rodadas (quatro): dois cenários
    nunca produzem o mesmo número, e um cenário só o repete depois de quinhentas rodadas. Eram a
    rodada **módulo 10** e a ordem, e a rodada 11 repetia os CPFs da 1. A unidade não cabe nos
    nove dígitos: duas unidades repetem os números, o que não colide com nada — o CPF não é chave
    de identidade, e a pessoa de cada unidade tem e-mail e sujeito próprios.

    O que se garante é a origem, e não a ausência: o número é calculado, e não colhido de pessoa
    alguma; que nenhum CPF válido coincida com o de alguém, só a Receita poderia afirmar.
    """
    if not 1 <= ordem <= PESSOAS_POR_RODADA:
        raise ValueError(f"a ordem {ordem} passa das {PESSOAS_POR_RODADA} pessoas por rodada.")
    numero_do_cenario = int("".join(ch for ch in codigo if ch.isdigit()) or 0)
    posicao = ((rodada - 1) * PESSOAS_POR_RODADA + ordem) % 10000
    base = f"000{numero_do_cenario % 100:02d}{posicao:04d}"
    digitos = [int(ch) for ch in base]
    for tamanho in (9, 10):
        soma = sum(d * (tamanho + 1 - i) for i, d in enumerate(digitos[:tamanho]))
        resto = (soma * 10) % 11
        digitos.append(0 if resto == 10 else resto)
    texto = "".join(str(d) for d in digitos)
    return f"{texto[:3]}.{texto[3:6]}.{texto[6:9]}-{texto[9:]}"


# Nomes compostos de propósito com um sobrenome que não existe ("Treinamento"), para que a lista de
# inscritos de um cenário nunca seja confundida com a de um certame real, nem num relatório
# exportado (FR-4632).
PRENOMES = (
    "Alice",
    "Bernardo",
    "Cecília",
    "Davi",
    "Estela",
    "Fernando",
    "Gabriela",
    "Heitor",
    "Isadora",
    "João",
    "Lara",
    "Miguel",
    "Natália",
    "Otávio",
    "Paula",
    "Rafael",
)


def pessoa(unidade, codigo, rodada, ordem):
    """Nome, CPF, e-mail e sujeito de uma pessoa fictícia do cenário.

    O e-mail é de `exemplo.test`: o domínio `.test` é reservado (RFC 2606) e não entrega a ninguém.
    """
    prenome = PRENOMES[(ordem - 1) % len(PRENOMES)]
    sufixo = f"{etiqueta(unidade)}-{codigo.lower()}r{rodada}p{ordem:02d}"
    return {
        "nome": f"{prenome} Treinamento {codigo}-{ordem:02d}",
        "cpf": cpf(codigo, rodada, ordem),
        "email": f"{sufixo}@treinamento.exemplo.test",
        "subject": f"cand:treinamento-{sufixo}",
    }
