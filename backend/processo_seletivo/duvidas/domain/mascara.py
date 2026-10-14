"""O mascaramento simples do piloto: CPF, e-mail e telefone (071, `R-015`).

**O que ele não é: anonimização.** Ele troca três padrões, e só eles. Um nome, um endereço ou uma
situação escritos por extenso passam inteiros. A proteção principal é outra — a orientação dada no
início de cada sessão acompanhada e a ausência de identidade no registro (`D-013`) —, e nada aqui,
na tela ou no relatório pode chamar o resultado de anônimo (`FR-1509`).

**A pergunta é mascarada antes de tudo**, e é o texto mascarado que vai ao modelo e ao registro:
assim o histórico que o modelo recebe e o registro que a equipe lê são o mesmo texto. **A resposta
tem só o CPF mascarado.** E-mail e telefone numa resposta conferida estão, por construção, numa
fonte citada (`R-005`) — são o canal publicado do Edital —, e mascará-los apagaria o encaminhamento
do registro sem proteger ninguém.

Os padrões de e-mail e telefone são os da `070` (`canal.py`), e não cópias: um contato que o canal
reconhece é um contato que a máscara reconhece.
"""

from __future__ import annotations

import re

from processo_seletivo.duvidas.domain.canal import EMAIL, TELEFONE

CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")


def mascarar(texto: str) -> str:
    """CPF primeiro: com onze dígitos, ele também casaria com o padrão de telefone."""
    texto = CPF.sub("[CPF]", texto)
    texto = EMAIL.sub("[e-mail]", texto)
    return TELEFONE.sub("[telefone]", texto)


def tem_padrao_pessoal(texto: str) -> bool:
    """Se a pergunta traz algum dos três padrões — o que recusa o envio a serviço externo."""
    return mascarar(texto) != texto


def mascarar_resposta(texto: str) -> str:
    return CPF.sub("[CPF]", texto)
