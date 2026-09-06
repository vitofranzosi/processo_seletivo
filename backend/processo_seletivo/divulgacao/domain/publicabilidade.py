"""Se este ato pode ser divulgado agora — e, não podendo, qual das três razões impede (FR-004).

**Nada aqui é regra nova.** `estado_do_marco` já devolve `vigente`, `obsoleto`, `recomputavel` e as
`divergencias`, e já trata o marco removido por Retificação sem exceção especial (015). As três
formas de impedimento são **leitura** desse retorno (T-004).

A classificação é em três degraus, e é ela que a prévia mostra (FR-005):

| degrau | o que significa | efeito na tela |
|---|---|---|
| `informacao` | o estado normal, sem nada a ressalvar | publica |
| `aviso` | há o que ler antes de confirmar, mas nada impede | publica |
| `impedimento` | o ato não é publicável | **não** oferece o botão |

Havendo impedimento, não existe publicar mediante confirmação adicional (D-001): a tela mostra a
recusa nomeada e o caminho — emitir o ato sucessor, na tela da 015 (FR-006).
"""

from dataclasses import dataclass, field

from processo_seletivo.classificacao.application.selectors import estado_do_marco

INFORMACAO, AVISO, IMPEDIMENTO = "informacao", "aviso", "impedimento"

# As três recusas de obsolescência, com o código do contrato, o HTTP e o caminho que cada uma
# nomeia. O caminho é o requisito: uma recusa que não diz o que fazer a seguir devolve a pessoa à
# tela anterior sem nada (FR-006).
SUCEDIDO = "publication_act_superseded"
DESATUALIZADO = "publication_act_stale"
MARCO_REMOVIDO = "publication_milestone_removed"

STATUS = {SUCEDIDO: 409, DESATUALIZADO: 422, MARCO_REMOVIDO: 422}

CAMINHO_DO_SUCESSOR = (
    "Emita o ato sucessor na tela de classificação do marco e publique o ato vigente."
)

MENSAGENS = {
    SUCEDIDO: (
        "Este ato foi sucedido por outro e não é mais o vigente do marco. " + CAMINHO_DO_SUCESSOR
    ),
    DESATUALIZADO: (
        "A regra ou o universo mudaram desde a emissão deste ato, e divulgá-lo publicaria uma "
        "ordem que já não é a que o Edital vigente produz. " + CAMINHO_DO_SUCESSOR
    ),
    MARCO_REMOVIDO: (
        "O marco não existe na norma vigente: uma Retificação o removeu, e não há regra vigente "
        "com que comparar o ato. " + CAMINHO_DO_SUCESSOR
    ),
}


@dataclass(frozen=True)
class Afericao:
    """O que a prévia mostra e o que o comando decide, na mesma leitura.

    Existem os dois porque são perguntas diferentes: a tela quer **o que dizer**, e o comando quer
    **se recusa**. Derivar a segunda de um texto seria pedir à interface que decidisse o domínio.
    """

    nivel: str
    codigo: str = ""
    mensagem: str = ""
    status: int = 422
    divergencias: list = field(default_factory=list)

    @property
    def publicavel(self) -> bool:
        return self.nivel != IMPEDIMENTO


SUCEDERA = "publication_supersedes"

AVISO_DE_SUCESSAO = (
    "Este marco já tem resultado divulgado. Publicar de novo **sucede** aquela divulgação: ela "
    "permanece consultável no mesmo endereço e passa a dizer que foi sucedida."
)


def aferir(*, edital, marco_id, ato, sucede=None, at=None):
    """Afere a publicabilidade de `ato` contra o estado atual do marco.

    `at` existe para o comando aferir no instante da transação, e não no da leitura da tela.

    `sucede` é a publicação vigente do marco, quando há uma. Ela **não** decide publicabilidade —
    suceder é o caminho normal da correção (FR-041) —, e é ela que produz o terceiro degrau da
    FR-005: há o que ler antes de confirmar, e nada impede. Sem ela, `aviso` seria um nível
    declarado e nunca alcançado, e a próxima pessoa a ler este módulo confiaria numa classificação
    que na prática tem dois valores.

    Quem chama sem `sucede` — o comando, que precisa saber apenas se recusa — recebe `informacao`
    no lugar de `aviso`, e a decisão dele é a mesma nos dois casos.
    """
    estado = estado_do_marco(edital=edital, marco_id=marco_id, at=at)

    # **Primeiro o marco removido.** Sem regra vigente não há com que comparar, e as outras duas
    # perguntas não se colocam: `estado_do_marco` devolve `recomputavel=False` e uma divergência
    # de `regra_ausente` justamente para dizer isso.
    if not estado["recomputavel"]:
        return Afericao(
            IMPEDIMENTO,
            MARCO_REMOVIDO,
            MENSAGENS[MARCO_REMOVIDO],
            STATUS[MARCO_REMOVIDO],
            estado["divergencias"],
        )

    vigente = estado["vigente"]
    if vigente is None or str(vigente.id) != str(ato.id):
        # Publicar um ato que outro já sucedeu divulgaria uma ordem revogada. O vigente ausente
        # cai aqui pelo mesmo raciocínio: o ato citado não é o que o marco reconhece hoje.
        return Afericao(
            IMPEDIMENTO, SUCEDIDO, MENSAGENS[SUCEDIDO], STATUS[SUCEDIDO], estado["divergencias"]
        )

    if estado["obsoleto"]:
        return Afericao(
            IMPEDIMENTO,
            DESATUALIZADO,
            MENSAGENS[DESATUALIZADO],
            STATUS[DESATUALIZADO],
            estado["divergencias"],
        )

    if sucede is not None:
        return Afericao(AVISO, SUCEDERA, AVISO_DE_SUCESSAO, 200)

    return Afericao(INFORMACAO, divergencias=[])


__all__ = [
    "AVISO",
    "Afericao",
    "DESATUALIZADO",
    "IMPEDIMENTO",
    "INFORMACAO",
    "MARCO_REMOVIDO",
    "SUCEDERA",
    "SUCEDIDO",
    "aferir",
]
