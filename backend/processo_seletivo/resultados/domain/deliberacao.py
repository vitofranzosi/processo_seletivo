"""A regra de deliberação de uma Etapa colegiada, e a deliberação que ela produz (165).

Função pura sobre a Etapa **do conteúdo publicado**. Não consulta banco nem conhece modelo, e é por
isso que a tabela-verdade inteira — três e cinco pareceres, todas as combinações, as três regras —
cabe num teste unitário (SC-2351).

**A regra combina sentidos, e só sentidos** (FR-7061). Não lê motivo, texto, ordem nem autor: dois
pareceres "Indeferido" por razões diferentes contam igual, e o que o candidato contesta é o texto,
que vai a ele à parte (FR-7077).

**Não há regra padrão** (D-002). A pergunta de qual regra os Editais do Ifes usarão está com a CPVA,
e marcar uma seria o sistema respondendo por ela. Por isso o nulo é "sem regra", e a Etapa colegiada
sem regra continua impedida na consolidação, como era antes do degrau 24.
"""

from dataclasses import dataclass, field

from processo_seletivo.avaliacoes.domain.formas import Forma, Sentido
from processo_seletivo.avaliacoes.domain.previsao import (
    avaliacoes_previstas,
    forma_publicada,
    rotulos,
)

MAIORIA = "MAIORIA"
UNANIMIDADE_PARA_O_FAVORAVEL = "UNANIMIDADE_PARA_O_FAVORAVEL"
UNANIMIDADE_PARA_O_DESFAVORAVEL = "UNANIMIDADE_PARA_O_DESFAVORAVEL"

REGRAS = (MAIORIA, UNANIMIDADE_PARA_O_FAVORAVEL, UNANIMIDADE_PARA_O_DESFAVORAVEL)

# A grafia do conteúdo publicado, e a do modelo, no molde do efeito da `164`.
PUBLICADO = {
    MAIORIA: "MAJORITY",
    UNANIMIDADE_PARA_O_FAVORAVEL: "UNANIMOUS_FOR_FAVORABLE",
    UNANIMIDADE_PARA_O_DESFAVORAVEL: "UNANIMOUS_FOR_UNFAVORABLE",
}
DO_PUBLICADO = {valor: chave for chave, valor in PUBLICADO.items()}

CAMPO = "deliberationRule"


def da_coluna(valor) -> str | None:
    """A grafia publicada do valor da coluna, ou `None` para o vazio."""
    return PUBLICADO.get(valor or "")


def para_coluna(valor) -> str:
    """O valor da coluna para a grafia publicada; `""` para `None`, vazio ou desconhecido."""
    return DO_PUBLICADO.get(valor or "", "")


def decisoria_com_varias(etapa) -> bool:
    """A Etapa **precisa** de regra: decisória, com mais de uma avaliação por inscrição."""
    return bool(
        isinstance(etapa, dict)
        and forma_publicada(etapa) == Forma.DECISORIA
        and avaliacoes_previstas(etapa) > 1
    )


def regra_publicada(etapa) -> str | None:
    """A regra da Etapa (o valor do domínio), ou `None` quando não declarada ou fora do contrato."""
    if not isinstance(etapa, dict):
        return None
    return DO_PUBLICADO.get(etapa.get(CAMPO))


def colegiada(etapa) -> bool:
    """Decisória, com mais de uma avaliação por inscrição, e com a regra declarada."""
    return decisoria_com_varias(etapa) and regra_publicada(etapa) is not None


def publicar(etapa_dict, coluna) -> dict:
    """O campo como a publicação o grava (research T-002): explícito só onde ele vale.

    Na Etapa pontuada, ou de uma avaliação, `null`: a regra ali seria a coerência que a FR-7053
    recusa, e não gravá-la é mais barato que recusá-la depois. Na decisória com várias avaliações, o
    vazio do rascunho continua `null` — sem padrão (D-002) —, e é a publicação que o recusa.
    """
    if not decisoria_com_varias(etapa_dict):
        return {CAMPO: None}
    return {CAMPO: PUBLICADO.get(coluna or "")}


def deliberar(regra, sentidos) -> str:
    """O sentido deliberado, pela tabela da FR-7050. `regra` é o valor do domínio."""
    sentidos = [str(item) for item in sentidos]
    favoraveis = sum(1 for item in sentidos if item == Sentido.FAVORAVEL)
    total = len(sentidos)
    if regra == MAIORIA:
        favoravel = favoraveis * 2 > total
    elif regra == UNANIMIDADE_PARA_O_FAVORAVEL:
        favoravel = favoraveis == total
    elif regra == UNANIMIDADE_PARA_O_DESFAVORAVEL:
        favoravel = favoraveis > 0
    else:
        raise ValueError(f"regra de deliberação desconhecida: {regra!r}")
    return str(Sentido.FAVORAVEL if favoravel else Sentido.DESFAVORAVEL)


@dataclass(frozen=True)
class Deliberacao:
    """A deliberação de uma inscrição, lida por `regra.consequencia` como se lê uma conclusão.

    `forma`, `pontuacao` e `sentido` são o que a conclusão única oferece; o resto é o que só a
    deliberação tem. `pareceres` são as identidades das Avaliações, na ordem de conclusão, e
    `versao_id` é a versão cuja regra foi aplicada — a vigente no ato (D-006).
    """

    regra: str
    sentidos: tuple
    pareceres: tuple = field(default_factory=tuple)
    versao_id: object = None

    forma = str(Forma.DECISORIA)
    pontuacao = None

    @property
    def favoraveis(self) -> int:
        return sum(1 for item in self.sentidos if str(item) == Sentido.FAVORAVEL)

    @property
    def desfavoraveis(self) -> int:
        return len(self.sentidos) - self.favoraveis

    @property
    def sentido(self) -> str:
        return deliberar(self.regra, self.sentidos)

    @property
    def criterios(self) -> list:
        return []


def _rotulos(etapa):
    favoravel, desfavoravel = rotulos(etapa)
    return favoravel or "favorável", desfavoravel or "desfavorável"


def _no_sentido(deliberacao_) -> int:
    favoravel = deliberacao_.sentido == Sentido.FAVORAVEL
    return deliberacao_.favoraveis if favoravel else deliberacao_.desfavoraveis


def modo(etapa, deliberacao_) -> str:
    """ "por maioria", "por unanimidade" ou "por não haver unanimidade «X»" (`frases.md`)."""
    if deliberacao_.regra == MAIORIA:
        return "por maioria"
    favoravel, desfavoravel = _rotulos(etapa)
    exigido = (
        Sentido.FAVORAVEL
        if deliberacao_.regra == UNANIMIDADE_PARA_O_FAVORAVEL
        else Sentido.DESFAVORAVEL
    )
    if deliberacao_.sentido == exigido:
        return "por unanimidade"
    faltou = favoravel if exigido == Sentido.FAVORAVEL else desfavoravel
    return f"por não haver unanimidade {faltou}"


def desfecho(etapa, deliberacao_) -> str:
    favoravel, desfavoravel = _rotulos(etapa)
    return favoravel if deliberacao_.sentido == Sentido.FAVORAVEL else desfavoravel


def contagem(etapa, deliberacao_) -> str:
    """ "2 de 3 pareceres Indeferido" — os pareceres no sentido do desfecho, sobre o total."""
    total = len(deliberacao_.sentidos)
    return f"{_no_sentido(deliberacao_)} de {total} pareceres {desfecho(etapa, deliberacao_)}"


def motivo(etapa, deliberacao_) -> str:
    """O motivo do Resultado deliberado (FR-7066). Nunca o autor, nunca o texto de um parecer."""
    return (
        f"a comissão deliberou {desfecho(etapa, deliberacao_)} {modo(etapa, deliberacao_)}: "
        f"{contagem(etapa, deliberacao_)}"
    )


def linha_da_conferencia(etapa, deliberacao_) -> str:
    """A linha da conferência da consolidação (UX-752)."""
    return (
        f"{desfecho(etapa, deliberacao_)} — {contagem(etapa, deliberacao_)}, "
        f"{modo(etapa, deliberacao_)}"
    )


def opcoes_da_regra(favoravel=None, desfavoravel=None) -> list[tuple[str, str]]:
    """As três opções da composição, com os rótulos digitados no cartão (UX-750).

    O template as escreve com as mesmas palavras; esta é a versão que os testes e o contrato leem.
    Sem rótulo, as palavras vão sem aspas, porque não são o vocabulário de Edital nenhum.
    """
    f = f"«{favoravel}»" if favoravel else "favorável"
    d = f"«{desfavoravel}»" if desfavoravel else "desfavorável"
    return [
        (PUBLICADO[MAIORIA], f"Resultado {f} quando a maioria dos pareceres for {f}"),
        (
            PUBLICADO[UNANIMIDADE_PARA_O_FAVORAVEL],
            f"Resultado {f} só quando todos os pareceres forem {f}",
        ),
        (
            PUBLICADO[UNANIMIDADE_PARA_O_DESFAVORAVEL],
            f"Resultado {d} só quando todos os pareceres forem {d}",
        ),
    ]


def frase_da_regra(etapa) -> str:
    """A frase do documento, da Revisão e da Retificação (FR-7075, contrato `frases.md`).

    `""` para a Etapa sem regra: é o que faz o acervo se recompor byte a byte (SC-2350).
    """
    regra = regra_publicada(etapa)
    if regra is None or not decisoria_com_varias(etapa):
        return ""
    favoravel, desfavoravel = _rotulos(etapa)
    if regra == MAIORIA:
        resultado = (
            f"O resultado é «{favoravel}» quando a maioria dos pareceres é «{favoravel}», e "
            f"«{desfavoravel}» nos demais casos."
        )
    elif regra == UNANIMIDADE_PARA_O_FAVORAVEL:
        resultado = (
            f"O resultado é «{favoravel}» só quando todos os pareceres são «{favoravel}», e "
            f"«{desfavoravel}» nos demais casos."
        )
    else:
        resultado = (
            f"O resultado é «{desfavoravel}» só quando todos os pareceres são «{desfavoravel}», e "
            f"«{favoravel}» nos demais casos."
        )
    return (
        f"Cada inscrição recebe {avaliacoes_previstas(etapa)} pareceres, registrados por membros "
        f"da comissão sem conhecer o dos demais. {resultado}"
    )


__all__ = [
    "CAMPO",
    "MAIORIA",
    "PUBLICADO",
    "REGRAS",
    "UNANIMIDADE_PARA_O_DESFAVORAVEL",
    "UNANIMIDADE_PARA_O_FAVORAVEL",
    "Deliberacao",
    "colegiada",
    "contagem",
    "da_coluna",
    "decisoria_com_varias",
    "deliberar",
    "desfecho",
    "frase_da_regra",
    "linha_da_conferencia",
    "modo",
    "motivo",
    "opcoes_da_regra",
    "para_coluna",
    "publicar",
    "regra_publicada",
]
