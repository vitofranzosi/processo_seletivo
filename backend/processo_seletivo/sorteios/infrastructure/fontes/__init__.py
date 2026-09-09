"""A porta da fonte externa da semente, e os seus adaptadores (021, R-005).

**A fronteira que este módulo desenha.** A *identidade* da fonte, a ocorrência, a derivação, a
normalização e a regra de substituição são **conteúdo normativo publicado**: vivem no `drawMethod`
do marco, e alterá-las é Retificação. O *acesso* à fonte é implementação — qual biblioteca, qual
tempo limite, quantas tentativas —, e é o que mora aqui, configurado por ambiente.

Confundir as duas coisas seria deixar uma implantação de software mudar o sentido de um Edital já
publicado, que é exatamente o que a FR-014 proíbe.

O adaptador devolve **material bruto**, e nada mais: nem semente normalizada — normalizar é regra do
método (D-016) —, nem juízo sobre o que fazer quando a ocorrência falta. A ausência é um desfecho
declarado, e quem decide o que fazer com ela é a regra publicada.
"""

from dataclasses import dataclass

from django.utils.module_loading import import_string

from processo_seletivo.shared.api.problems import DomainError


@dataclass(frozen=True)
class Observacao:
    """O que a fonte devolveu sobre uma ocorrência.

    `indisponivel` não é erro: é desfecho previsto, e é ele que aciona a regra de substituição
    publicada. `evidencia` é o que se observou — o que a fonte respondeu, e quando —, porque
    aplicar a substituição sem registrar o que a motivou seria afirmar indisponibilidade sem lastro
    (FR-015, R-006).

    **`ocorrida_nao_antes_de` é o instante mais cedo em que a ocorrência pode ter acontecido**,
    conforme a fonte publica — e não quando nós a lemos. A distinção é a feature inteira: a FR-016
    exige que a ocorrência seja **posterior ao congelamento**, e comparar o instante da leitura
    permitiria congelar a relação já sabendo o resultado e só depois registrá-lo no sistema.

    **O nome diz o que o dado é, e não mais do que ele é.** A Loteria Federal publica
    `dataApuracao: "11/09/2024"` — uma data, sem horário. A versão anterior deste campo se chamava
    `ocorrida_em` e o adaptador carimbava `20:00`, um horário que a fonte não publica: uma relação
    congelada no mesmo dia passava ou falhava por causa de um instante inventado. Agora o adaptador
    devolve o **início do dia publicado**, que é o limite inferior verdadeiro, e a comparação exige
    que o congelamento seja anterior a ele. Onde a fonte publicar o horário, o limite inferior é o
    próprio horário, e a garantia fica mais apertada sem mudar de forma.

    O adaptador que não souber dizer quando a ocorrência aconteceu não serve para semear sorteio, e
    o comando o recusa.
    """

    material_bruto: str = ""
    ocorrida_nao_antes_de: object = None
    indisponivel: bool = False
    evidencia: str = ""


class FonteExterna:
    """A porta. Um método, e ele não decide nada."""

    def observar(self, *, fonte: str, referencia: str) -> Observacao:  # pragma: no cover - contrato
        raise NotImplementedError


# **O vocabulário de fontes, fechado e ligado ao adaptador que cada uma executa** (FR-076).
#
# Sem esta tabela, `source` era texto livre: um Edital podia declarar `Random.org`, o sistema
# consultava a Caixa de qualquer jeito — `LoteriaFederal.observar` ignorava o argumento `fonte` — e
# o manifesto publicava uma fonte que nunca foi consultada. A identidade da fonte é conteúdo
# normativo; se ela não determinar de onde a semente vem, não é conteúdo normativo de nada.
#
# Acrescentar fonte é publicar adaptador, e não escrever uma linha no Edital.
FONTES = {
    "Loteria Federal": (
        "processo_seletivo.sorteios.infrastructure.fontes.loteria_federal.LoteriaFederal"
    ),
    # O falso, endereçável por nome: é o que permite ao `seed_demo` e ao roteiro do `quickstart`
    # rodarem sem rede, **sem** que a escolha do adaptador dependa de configuração de ambiente.
    "Fonte de demonstração": (
        "processo_seletivo.sorteios.infrastructure.fontes.loteria_federal.FonteDeTeste"
    ),
}


def fonte_declarada(nome):
    """O adaptador que executa a fonte **que o Edital declarou**, e não o que o ambiente escolheu.

    A configuração continua existindo para o que é operação — tempo limite, tentativas —, e deixou
    de decidir *de onde* a semente vem: isso é norma publicada.
    """
    caminho = FONTES.get(nome)
    if caminho is None:
        raise DomainError(
            "draw_source_not_supported",
            f"Fonte não publicada por este sistema: {nome!r}. "
            f"As publicadas são: {', '.join(sorted(FONTES))}.",
            422,
            campo="source",
        )
    return import_string(caminho)()


__all__ = ["FONTES", "FonteExterna", "Observacao", "fonte_declarada"]
