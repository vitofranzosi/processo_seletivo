"""O catálogo de Seções do Edital — declarado, e não gerenciável.

O conjunto de seções e a ordem entre elas são definidos pelo sistema; quem elabora edita o texto
das textuais (FR-034). É o que separa um documento institucional estruturado de um construtor de
documentos.

**Por que declaração em código, e não linhas de tabela.** A estrutura passaria a depender do estado
do banco, e um Edital criado antes de uma mudança de catálogo ficaria estruturalmente diferente sem
que nada registrasse a diferença. Declarado, o catálogo é revisável em diff, dispensa migration para
mudar a redação institucional inicial, e a ausência de uma seção obrigatória deixa de ser estado
alcançável.

**A identidade é determinística.** A seção precisa ter identidade **antes de existir linha em
`SecaoEdital`** — a gerada nunca tem linha, e a textual só passa a ter depois da primeira edição.
`uuid5` sobre `(edital.id, key)` dá identidade estável desde o primeiro snapshot, igual entre duas
gerações do mesmo conteúdo e distinta entre Editais. E é UUID, e não a chave textual, porque o
seletor da gramática de Retificação só aceita UUID (`publicacoes/domain/changes.py:101-113`):
`/sections/id=cronograma/content` seria recusado como seletor inválido e a coleção ficaria
inendereçável.
"""

from dataclasses import dataclass
from uuid import NAMESPACE_URL, UUID, uuid5

GERADA = "GENERATED"
TEXTUAL = "TEXT"


@dataclass(frozen=True)
class Secao:
    """Uma entrada do catálogo.

    `source` nomeia a coleção que origina o conteúdo de uma seção gerada; `default_text` é a
    redação institucional inicial de uma textual. Cada tipo usa um, e nunca os dois.
    """

    key: str
    title: str
    order: int
    type: str
    source: str = ""
    default_text: str = ""

    @property
    def gerada(self) -> bool:
        return self.type == GERADA


CATALOGO: tuple[Secao, ...] = (
    Secao(
        key="disposicoes-preliminares",
        title="Disposições Preliminares",
        order=1,
        type=TEXTUAL,
        default_text=(
            "O presente Edital estabelece as normas do processo seletivo, cuja execução observará "
            "a legislação aplicável e os princípios que regem a Administração Pública."
        ),
    ),
    Secao(
        key="perfis",
        title="Perfis de Vaga",
        order=2,
        type=GERADA,
        source="profiles",
    ),
    Secao(
        key="inscricao",
        title="Da Inscrição",
        order=3,
        type=TEXTUAL,
        default_text=(
            "A inscrição será realizada exclusivamente pelos meios indicados neste Edital, nos "
            "prazos do Cronograma, e implica conhecimento e aceitação das condições aqui "
            "estabelecidas."
        ),
    ),
    Secao(
        key="etapas",
        title="Etapas de Avaliação",
        order=4,
        type=GERADA,
        source="stages",
    ),
    Secao(
        key="cronograma",
        title="Cronograma",
        order=5,
        type=GERADA,
        source="schedule",
    ),
    Secao(
        key="recursos",
        title="Dos Recursos",
        order=6,
        type=TEXTUAL,
        default_text=(
            "Caberá recurso contra os resultados divulgados, nos prazos do Cronograma, pelos meios "
            "indicados neste Edital."
        ),
    ),
    Secao(
        key="disposicoes-finais",
        title="Disposições Finais",
        order=7,
        type=TEXTUAL,
        default_text=(
            "Os casos omissos serão resolvidos pela autoridade responsável pelo processo seletivo, "
            "observada a legislação aplicável."
        ),
    ),
)

POR_CHAVE = {secao.key: secao for secao in CATALOGO}
CHAVES_TEXTUAIS = frozenset(secao.key for secao in CATALOGO if not secao.gerada)

# O espaço de nomes do `uuid5`. Fixá-lo é o que torna a identidade reproduzível entre execuções e
# entre máquinas; derivá-lo do ambiente faria a mesma seção do mesmo Edital ter duas identidades.
NAMESPACE = uuid5(NAMESPACE_URL, "https://cefor.ifes.edu.br/editais/sections")


def identidade(edital_id, key: str) -> UUID:
    return uuid5(NAMESPACE, f"{edital_id}:{key}")


def e_textual(key: str) -> bool:
    return key in CHAVES_TEXTUAIS
