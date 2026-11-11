"""A consequência da correção é **derivada**, e nunca digitada.

O julgador fixa a **conclusão** — a pontuação na forma pontuada, o sentido na decisória. Quem diz
o que essa conclusão produz é a regra publicada da Etapa: a nota mínima e o caráter eliminatório na
forma pontuada, o sentido na decisória.

**Deixá-la livre permitiria uma decisão declarar `HABILITADA` com nota abaixo da mínima** — e
contradizer, no mesmo ato, a norma que ela própria cita. Não é hipótese remota: é o erro natural de
quem defere querendo ajudar e não confere a tabela (FR-059).

**A regra vem da versão que a decisão cita**, e não da vigente hoje. É a mesma escolha que a 015 fez
ao ler a norma pela versão que o ato cita: uma Retificação posterior não pode mudar retroativamente
o que uma decisão já produziu.

Nada aqui é regra nova. `resultados/domain/regra.py` é a mesma função que a consolidação usa desde a
013, e reusá-la é o que garante que a correção por recurso e a consolidação ordinária cheguem à
mesma consequência para a mesma nota — duas tabelas-verdade divergiriam no primeiro Edital atípico.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from processo_seletivo.avaliacoes.domain import barema
from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.avaliacoes.domain.pontuacao import normalizar_sentido, validar
from processo_seletivo.avaliacoes.domain.previsao import forma_publicada
from processo_seletivo.resultados.domain.regra import consequencia as consequencia_da_regra
from processo_seletivo.resultados.domain.regra import impedimento_da_regra
from processo_seletivo.shared.api.problems import DomainError

INCOMPLETA = "appeal_correction_incomplete"


@dataclass(frozen=True)
class Conclusao:
    """O que o julgador fixou, na forma que a Etapa publica.

    O mesmo contrato que a consolidação já consome — três campos, e a forma escolhe qual vale.
    """

    forma: str
    pontuacao: Decimal | None
    sentido: str
    # O detalhamento por critério, na Etapa com barema (146, FR-5227); vazio fora dela.
    criterios: list = field(default_factory=list)


def etapa_publicada(versao, etapa_id):
    """A Etapa como a **versão citada pela decisão** a descreve, ou `None`."""
    alvo = str(etapa_id)
    for etapa in versao.content.get("stages") or []:
        if str(etapa.get("id")) == alvo:
            return etapa
    return None


def derivar(*, versao, etapa_id, pontuacao=None, sentido="", criterios=None):
    """`(consequencia, motivo, conclusao)` — ou recusa dizendo o que falta.

    A recusa é `422` e nomeia o campo ausente: uma correção fixada sem Etapa, ou sem a conclusão que
    a forma exige, não é decisão incompleta por descuido de quem implementa — é decisão que a tela
    deixou sair pela metade, e devolvê-la em silêncio faria nascer um sucessor sem grandeza onde a
    Etapa tem uma.
    """
    if etapa_id is None:
        raise DomainError(INCOMPLETA, "A correção precisa dizer a que Etapa se refere.", 422)
    etapa = etapa_publicada(versao, etapa_id)
    if etapa is None:
        raise DomainError(
            INCOMPLETA,
            "A Etapa indicada não existe na versão do Edital que esta decisão cita.",
            422,
        )
    impedimento = impedimento_da_regra(etapa)
    if impedimento is not None:
        # A mesma recusa que a consolidação daria, e pelo mesmo motivo: sem regra suficiente,
        # qualquer consequência que se declarasse afirmaria norma que ninguém escreveu.
        raise DomainError(INCOMPLETA, f"A Etapa não tem regra suficiente: {impedimento[1]}.", 422)

    forma = forma_publicada(etapa)
    conclusao = _conclusao(forma, pontuacao, sentido, etapa, criterios)
    efeito, motivo = consequencia_da_regra(etapa, conclusao)
    return efeito, motivo, conclusao


def _conclusao(forma, pontuacao, sentido, etapa, criterios=None):
    """O que o julgador fixou, validado **pelas mesmas regras que o avaliador enfrenta**.

    A ausência é recusada aqui, e com código próprio: decisão sem a conclusão que a forma exige não
    é valor inválido — é decisão que saiu pela metade, e a mensagem precisa dizer isso.

    O **valor**, existindo, não tem validação própria: ele passa por
    `avaliacoes.domain.pontuacao.validar`, que é a mesma porta da conclusão de Avaliação. Ter duas
    validações para o mesmo campo produz, mais cedo ou mais tarde, um Resultado que uma porta
    aceita e a outra recusaria — e a porta do recurso grava sob decisão irreversível. A revisão do
    PR mostrou o que a segunda validação deixava passar: negativo, `Infinity`, casas em excesso e
    valor acima da máxima publicada; `NaN` nem recusava — estourava.

    O mesmo vale para o **sentido**: `normalizar_sentido` é quem sabe que o enum tem dois valores e
    que o rótulo publicado não é um deles (FR-118).
    """
    if forma == Forma.DECISORIA:
        if not (sentido or "").strip():
            raise DomainError(
                INCOMPLETA, "Esta Etapa é decisória: a correção precisa fixar o sentido.", 422
            )
        return Conclusao(
            forma=str(forma),
            pontuacao=None,
            sentido=normalizar_sentido(sentido, exigir=True),
        )
    if barema.tem_barema(etapa):
        return _conclusao_pelo_barema(forma, pontuacao, etapa, criterios)
    if criterios:
        raise DomainError(
            INCOMPLETA,
            "Esta Etapa não publicou barema: a correção fixa a pontuação, e não critérios.",
            422,
        )
    if pontuacao is None or str(pontuacao).strip() == "":
        raise DomainError(
            INCOMPLETA, "Esta Etapa é pontuada: a correção precisa fixar a pontuação.", 422
        )
    return Conclusao(forma=str(forma), pontuacao=validar(pontuacao, etapa), sentido="")


def _conclusao_pelo_barema(forma, pontuacao, etapa, criterios):
    """A correção critério a critério, pela **mesma função** da Mesa (146, D-005, FR-5227).

    O total é do servidor, como na Mesa: a pontuação vinda junto é recusada, e não somada nem
    ignorada. Todo critério precisa de resposta — a decisão é ato com efeito, como a conclusão —,
    e o total passa depois pela mesma `validar` da pontuação única. A vedação de piora continua
    sobre o total, no caminho de sempre (`julgar._recusar_se_piora`).

    O barema é o da Etapa **na versão que a decisão cita** — a vigente no julgamento —, e é com ele
    que o detalhamento gravado se lê depois (D-011).
    """
    if pontuacao is not None and str(pontuacao).strip() != "":
        raise DomainError(
            "pontuacao_calculada",
            "Esta Etapa tem barema: a correção é informada critério a critério, e o total é "
            "calculado pelo sistema.",
            422,
        )
    if not criterios:
        raise DomainError(
            INCOMPLETA,
            "Esta Etapa tem barema: a correção precisa fixar a pontuação de cada critério.",
            422,
        )
    linhas, total = barema.calcular(barema.criterios_da_etapa(etapa), criterios, exigir=True)
    return Conclusao(
        forma=str(forma), pontuacao=validar(total, etapa), sentido="", criterios=linhas
    )


__all__ = ["INCOMPLETA", "Conclusao", "derivar", "etapa_publicada"]
