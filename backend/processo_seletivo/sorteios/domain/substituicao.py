"""A regra de substituição, aplicada **sem escolha humana** no dia do sorteio (021, FR-015).

**O que estava errado e esta correção fecha.** A regra de substituição era prosa publicada, e o
sistema apenas dizia "observe a ocorrência que a substitui". Quem decidia qual era ela? Uma pessoa,
no dia, ao vivo — que é exatamente a escolha que a FR-015 proíbe. Pior: a tela deixava de oferecer o
botão de observar depois de registrar a indisponibilidade, de modo que uma extração não publicada
travava o certame para sempre.

A regra passa a ser **executável**, pelo mesmo desenho da normalização: identificador de vocabulário
fechado que a máquina aplica, mais a frase que se publica. Dada a ocorrência declarada e as
ocorrências já registradas como indisponíveis, existe **uma** próxima ocorrência a observar, e ela é
derivada — não escolhida.

**O limite da cadeia é deliberado.** Uma fonte permanentemente fora do ar não pode fazer o sistema
percorrer referências indefinidamente: passado o limite, o certame precisa de um ato humano — uma
Retificação que declare outro método —, e é honesto que ele precise. Automatizar além disso seria
inventar norma que o Edital não publicou.
"""

import re

from processo_seletivo.shared.api.problems import DomainError

OCORRENCIA_SEGUINTE_DA_MESMA_FONTE = "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE"

# Quantas substituições a regra encadeia antes de exigir ato humano. Cinco cobre um mês de
# extrações semanais indisponíveis — muito além de qualquer caso real — e ainda assim é finito.
LIMITE_DA_CADEIA = 5

_NUMERO_FINAL = re.compile(r"^(?P<prefixo>.*?)(?P<numero>\d+)$")


def _seguinte_da_mesma_fonte(referencia: str) -> str:
    """`5900` → `5901`. A ocorrência imediatamente seguinte, pela numeração da própria fonte.

    A derivação é sobre o **número final** da referência, e preserva o que vier antes dele e a
    quantidade de dígitos: `Concurso 5900` vira `Concurso 5901`, e `0099` vira `0100`.
    """
    achado = _NUMERO_FINAL.match(referencia.strip())
    if achado is None:
        raise DomainError(
            "substitution_rule_not_applicable",
            f"A regra da ocorrência seguinte não se aplica a {referencia!r}: ela deriva do número "
            "da ocorrência, e esta referência não termina em número. Substituir exige, aqui, "
            "Retificação que declare outro método.",
            422,
            campo="substitutionRule",
        )
    numero = achado.group("numero")
    return f"{achado.group('prefixo')}{int(numero) + 1:0{len(numero)}d}"


REGRAS = {OCORRENCIA_SEGUINTE_DA_MESMA_FONTE: _seguinte_da_mesma_fonte}


def regra_publicada(metodo) -> str:
    """O identificador da regra de substituição declarada. Recusa a que este sistema não executa."""
    identificador = ((metodo or {}).get("substitutionRule") or {}).get("rule", "")
    if identificador not in REGRAS:
        raise DomainError(
            "draw_method_unknown_substitution",
            f"Regra de substituição não publicada por este sistema: {identificador!r}.",
            422,
            campo="substitutionRule",
        )
    return identificador


def cadeia(metodo, *, limite=LIMITE_DA_CADEIA):
    """As referências admissíveis, da declarada às substitutas, **nesta ordem**.

    A primeira é sempre a que o Edital declarou. As demais só se tornam admissíveis quando as
    anteriores estiverem registradas como indisponíveis — quem decide isso é `proxima_a_observar`,
    porque é ele que conhece o que já foi observado.
    """
    aplicar = REGRAS[regra_publicada(metodo)]
    referencia = str((metodo or {}).get("occurrence") or "")
    saida = [referencia]
    for _ in range(limite):
        referencia = aplicar(referencia)
        saida.append(referencia)
    return saida


def proxima_a_observar(metodo, indisponiveis):
    """A **única** referência que a regra manda observar agora, dado o que já se observou.

    `indisponiveis` é o conjunto de referências já registradas como indisponíveis. A resposta é a
    primeira da cadeia que ainda não está nele — e, esgotada a cadeia, a recusa nomeia o que falta:
    um ato normativo, e não mais uma tentativa.
    """
    for referencia in cadeia(metodo):
        if referencia not in indisponiveis:
            return referencia
    raise DomainError(
        "substitution_chain_exhausted",
        f"A ocorrência declarada e as {LIMITE_DA_CADEIA} substitutas previstas pela regra "
        "publicada estão todas indisponíveis. Prosseguir exige Retificação que declare outro "
        "método: o sistema não escolhe fonte por conta própria.",
        409,
        campo="substitutionRule",
    )


def admissivel(metodo, ocorrencia, indisponiveis) -> bool:
    """Se **esta** ocorrência é a que a regra publicada manda usar agora.

    É a pergunta que faltava no comando de constituição: a ocorrência chegava por identidade, e
    fonte e referência nunca eram comparadas com o método congelado. Bastava passar outro UUID para
    sortear com uma extração que o Edital não declarou.
    """
    if ocorrencia.fonte != str((metodo or {}).get("source") or ""):
        return False
    return ocorrencia.referencia == proxima_a_observar(metodo, indisponiveis)


__all__ = [
    "LIMITE_DA_CADEIA",
    "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
    "REGRAS",
    "admissivel",
    "cadeia",
    "proxima_a_observar",
    "regra_publicada",
]
