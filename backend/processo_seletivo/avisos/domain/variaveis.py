"""As variáveis que o texto da seleção pode usar, e onde cada uma tem valor (066, `FR-1255`).

**Lista fechada, e nenhuma linguagem de template.** A seleção escreve texto; o sistema troca
`{nome}` pelo valor, e nada mais — sem condicional, sem laço, sem acesso a atributo. Um mecanismo de
template daria ao texto o poder de ler o que a lista não oferece, e a proteção de dado pessoal
deixaria de ser a lista para depender de quem escreve.

**Nenhuma variável diz modalidade, lista, posição, pontuação, resultado, motivo, CPF ou telefone**
(`D-007`). O dado sensível só entra num aviso se alguém o digitar.

**Três variáveis de destino, cada uma com um significado** (`R-008`): a publicação específica, a
página do processo seletivo e a referência declarada na chamada. Nenhuma vale o que outra vale.
"""

import re

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.shared.api.problems import DomainError

AMBAS = (nomes.RESULTADO, nomes.CHAMADA)

#: Cada variável e as origens em que ela tem valor (contracts/mensagem.md).
VARIAVEIS = {
    "nome_do_candidato": AMBAS,
    "edital": AMBAS,
    "processo_seletivo": AMBAS,
    "perfil": AMBAS,
    "etapa": (nomes.RESULTADO,),
    "natureza_do_resultado": (nomes.RESULTADO,),
    "data_da_publicacao": AMBAS,
    # Só quando o aviso cita **uma** publicação: com várias, não há URL inequívoca.
    "link_da_publicacao": (nomes.RESULTADO,),
    "pagina_do_processo_seletivo": AMBAS,
    "referencia_da_publicacao": (nomes.CHAMADA,),
    "area_do_candidato": AMBAS,
}

#: O que cada uma significa, para a lista ao lado do editor (`UX-176`).
SIGNIFICADO = {
    "nome_do_candidato": "o nome da pessoa que recebe",
    "edital": "o Edital, como em “Edital nº 57/2026”",
    "processo_seletivo": "o título do processo seletivo",
    "perfil": "o Perfil de vaga",
    "etapa": "a etapa do resultado (só em aviso de resultado)",
    "natureza_do_resultado": "“preliminar” ou “definitivo” (só em aviso de resultado)",
    "data_da_publicacao": "a data e a hora da publicação",
    "link_da_publicacao": "o endereço da publicação (só quando o aviso cita uma publicação)",
    "pagina_do_processo_seletivo": "a página pública do processo seletivo",
    "referencia_da_publicacao": "onde a chamada foi publicada (só em aviso de chamada)",
    "area_do_candidato": "a área do candidato, onde a pessoa vê a própria situação",
}

#: A única que varia por pessoa, e a única resolvida no envio (`R-007`).
POR_PESSOA = "nome_do_candidato"

# `{nome}`, com nome em minúsculas e sublinhado. `{{` e `}}` são chaves literais — a mesma convenção
# de `str.format`, que é a que quem já escreveu um texto com chaves espera.
_VARIAVEL = re.compile(r"\{\{|\}\}|\{([a-z_]+)\}")


def usadas(texto):
    """As variáveis do texto, na ordem em que aparecem, sem as chaves literais."""
    return [achado.group(1) for achado in _VARIAVEL.finditer(texto) if achado.group(1)]


def validar(texto, *, origem=None, publicacoes_citadas=None, campo="corpo"):
    """Recusa a variável que não existe, ou que não tem valor para a origem (`FR-1256`).

    **Sem origem**, valida um modelo: ele serve a qualquer aviso, e só a variável desconhecida o
    recusa. **Com origem**, valida um aviso, e a variável que existe mas não tem valor ali —
    `{etapa}` numa chamada, `{link_da_publicacao}` com várias publicações — também recusa, nomeada.
    """
    for nome in usadas(texto):
        if nome not in VARIAVEIS:
            raise DomainError(
                nomes.AVISO_VARIAVEL_DESCONHECIDA,
                f"A variável {{{nome}}} não existe. As variáveis possíveis estão listadas ao lado "
                "do texto.",
                422,
                campo=campo,
            )
        if origem is None:
            continue
        if origem not in VARIAVEIS[nome]:
            raise DomainError(
                nomes.AVISO_VARIAVEL_SEM_VALOR,
                f"A variável {{{nome}}} não tem valor neste aviso: ela só existe em aviso de "
                f"{'resultado' if origem == nomes.CHAMADA else 'chamada'}.",
                422,
                campo=campo,
            )
        if nome == "link_da_publicacao" and (publicacoes_citadas or 0) != 1:
            raise DomainError(
                nomes.AVISO_VARIAVEL_SEM_VALOR,
                "A variável {link_da_publicacao} só tem valor quando o aviso cita uma publicação, "
                "e este cita várias: use {pagina_do_processo_seletivo}.",
                422,
                campo=campo,
            )


def escapar(valor):
    """O valor posto no texto congelado, com as chaves dele protegidas.

    Um nome de Perfil com chaves, posto cru, seria lido no envio como variável ou como chave
    literal. Escapado aqui e desescapado no envio, ele chega como foi escrito.
    """
    return str(valor).replace("{", "{{").replace("}", "}}")


def resolver(texto, valores):
    """Troca as variáveis de `valores` e **mantém** as demais, com as chaves literais intactas.

    É o passo da confirmação: tudo se resolve menos `{nome_do_candidato}`, e o texto congelado
    continua no mesmo dialeto — por isso as chaves literais não são desfeitas aqui.
    """

    def trocar(achado):
        nome = achado.group(1)
        if nome is None or nome not in valores:
            return achado.group(0)
        return escapar(valores[nome])

    return _VARIAVEL.sub(trocar, texto)


def resolver_no_envio(texto, *, nome_do_candidato):
    """O passo do envio: o nome, e então as chaves literais viram chaves."""

    def trocar(achado):
        token = achado.group(0)
        if token == "{{":
            return "{"
        if token == "}}":
            return "}"
        if achado.group(1) == POR_PESSOA:
            return nome_do_candidato
        return token

    return _VARIAVEL.sub(trocar, texto)


__all__ = [
    "POR_PESSOA",
    "SIGNIFICADO",
    "VARIAVEIS",
    "escapar",
    "resolver",
    "resolver_no_envio",
    "usadas",
    "validar",
]
