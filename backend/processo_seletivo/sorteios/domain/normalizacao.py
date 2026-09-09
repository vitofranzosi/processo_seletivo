"""Material bruto da fonte → semente normalizada, pela regra que o Edital publicou.

**Por que a regra é um identificador declarado, e não a prosa.** A FR-015 exige normalização
mecânica, "aplicada sem escolha humana no momento da execução", e a FR-027 exige detalhe suficiente
para reimplementação independente. Prosa não atende nem a uma nem a outra: ninguém executa uma
frase, e duas pessoas lendo "os dígitos sorteados" produzem seis grafias diferentes da mesma
semente. O que o Edital publica, então, é **um par**: o identificador da regra, que a máquina
aplica e o terceiro reimplementa, e a frase, que é o que a pessoa lê.

O vocabulário é **fechado e declarado aqui** — não descoberto em tempo de execução —, pela razão
que `publicacoes/domain/colecoes.py` já registrou: decidir por presença de chave acerta hoje e
falha em silêncio no dia em que uma regra nova nascer. Regra que não esteja nesta tabela é
recusada, e acrescentar uma é publicar versão nova do algoritmo — ato normativo, nunca implantação
que muda o sentido de Edital já publicado.
"""

import re
import unicodedata

from processo_seletivo.shared.api.problems import DomainError

DIGITOS_EM_SEQUENCIA = "DIGITOS_EM_SEQUENCIA"
TEXTO_LITERAL = "TEXTO_LITERAL"


def _digitos_em_sequencia(material: str) -> str:
    """Os dígitos do material bruto, na ordem em que aparecem, separados por espaço.

    É a regra da extração da Loteria Federal: cinco prêmios, cinco números, e a semente é a
    sequência deles. Descartar o que não é dígito é o que torna a regra indiferente à moldura com
    que a fonte publica — cabeçalho, pontuação, quebra de linha.
    """
    grupos = re.findall(r"\d+", material)
    if not grupos:
        raise DomainError(
            "draw_seed_material_without_digits",
            "O material obtido da fonte não contém dígito algum; a regra publicada não se aplica.",
            422,
            campo="material_bruto",
        )
    return " ".join(grupos)


def _texto_literal(material: str) -> str:
    """O material bruto com espaços colapsados e bordas aparadas — e nada mais."""
    return re.sub(r"\s+", " ", material).strip()


REGRAS = {
    DIGITOS_EM_SEQUENCIA: _digitos_em_sequencia,
    TEXTO_LITERAL: _texto_literal,
}


def normalizar(*, material_bruto: str, regra: str) -> str:
    """Aplica a regra publicada. Regra desconhecida é recusa, e nunca silêncio.

    A normalização NFC vem antes de qualquer regra: duas grafias Unicode do mesmo texto são o mesmo
    texto, e é o que a serialização canônica do sistema já afirma em toda parte.
    """
    aplicar = REGRAS.get(regra)
    if aplicar is None:
        raise DomainError(
            "draw_method_unknown_normalization",
            f"Regra de normalização não publicada por este sistema: {regra!r}.",
            422,
            campo="normalization",
        )
    material = unicodedata.normalize("NFC", material_bruto or "")
    semente = aplicar(material)
    if not semente:
        raise DomainError(
            "draw_seed_empty",
            "A regra publicada produziu semente vazia sobre o material obtido.",
            422,
            campo="material_bruto",
        )
    return semente


__all__ = ["DIGITOS_EM_SEQUENCIA", "REGRAS", "TEXTO_LITERAL", "normalizar"]
