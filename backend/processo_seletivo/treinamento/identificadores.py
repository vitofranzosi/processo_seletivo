"""Identificadores, nomes e CPFs dos cenários — todos derivados, nenhum digitado (134, FR-4630).

**Por que derivar, e não sortear.** Perfis, Etapas, marcos e Eventos têm identidade **global**: o
mesmo UUID em dois Editais é recusado (`identifier_belongs_to_another_edital`). Os construtores do
`seed_demo` usam `00000000-0000-0000-00NN-…`, com dois dígitos do número do Edital, e cem números
não bastam para rodadas sucessivas de quinze cenários — e colidiriam com as demonstrações que já
existem na homologação. Aqui cada rodada tem o seu espaço: `uuid5(cenário, rodada, posição)`, que
é estável entre execuções e distinto entre rodadas.
"""

import uuid

# Fixo: mudá-lo mudaria a identidade de todo cenário já gerado, e a verificação deixaria de
# reconhecê-los.
ESPACO = uuid.UUID("6f1c2a52-6d0e-5b8e-9a43-1340a0c0ffee")

# O número que os construtores do `seed_demo` recebem para montar o molde. Ele nunca chega ao
# banco: `remapear` troca toda ocorrência antes do rascunho ser gravado.
MOLDE = "99"
_PREFIXO_DO_MOLDE = f"00000000-0000-0000-00{MOLDE}-0000000000"


def identificador(codigo, rodada, posicao):
    return str(uuid.uuid5(ESPACO, f"{codigo}/r{rodada}/{posicao}"))


def remapear(valor, codigo, rodada):
    """O mesmo molde, com os identificadores desta rodada — e nada além deles mudado."""
    if isinstance(valor, dict):
        return {chave: remapear(item, codigo, rodada) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [remapear(item, codigo, rodada) for item in valor]
    if isinstance(valor, str) and valor.startswith(_PREFIXO_DO_MOLDE) and len(valor) == 36:
        return identificador(codigo, rodada, valor[-2:])
    return valor


def do_molde(posicao):
    """O identificador do molde numa posição, para nomear uma peça antes de remapear."""
    return f"{_PREFIXO_DO_MOLDE}{posicao}"


def cpf(codigo, rodada, ordem):
    """Um CPF com dígitos verificadores corretos, gerado e não colhido de ninguém (FR-4631).

    **Começa sempre por 000**, para saltar aos olhos de quem lê a lista. Os seis dígitos seguintes
    são o cenário, a rodada e a ordem — dois cenários nunca produzem o mesmo número, e o mesmo
    cenário o produz sempre igual. O que se garante é a origem, e não a ausência: o número é
    calculado, e não colhido de pessoa alguma; que nenhum CPF válido coincida com o de alguém, só a
    Receita poderia afirmar.
    """
    numero_do_cenario = int("".join(ch for ch in codigo if ch.isdigit()) or 0)
    base = f"000{numero_do_cenario % 100:02d}{rodada % 10}{ordem % 1000:03d}"
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


def pessoa(codigo, rodada, ordem):
    """Nome, CPF, e-mail e sujeito de uma pessoa fictícia do cenário.

    O e-mail é de `exemplo.test`: o domínio `.test` é reservado (RFC 2606) e não entrega a ninguém.
    """
    prenome = PRENOMES[(ordem - 1) % len(PRENOMES)]
    sufixo = f"{codigo.lower()}r{rodada}p{ordem:02d}"
    return {
        "nome": f"{prenome} Treinamento {codigo}-{ordem:02d}",
        "cpf": cpf(codigo, rodada, ordem),
        "email": f"{sufixo}@treinamento.exemplo.test",
        "subject": f"cand:treinamento-{sufixo}",
    }
