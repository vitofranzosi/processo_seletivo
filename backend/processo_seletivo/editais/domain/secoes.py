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
        key="apresentacao",
        title="Apresentação",
        order=1,
        type=TEXTUAL,
        default_text=(
            "O Instituto Federal do Espírito Santo, por meio do Centro de Referência em Formação "
            "e em Educação a Distância, torna pública a realização do processo seletivo regido "
            "por este Edital."
        ),
    ),
    Secao(
        key="disposicoes-preliminares",
        title="Disposições Preliminares",
        order=2,
        type=TEXTUAL,
        default_text=(
            "O presente Edital estabelece as normas do processo seletivo, cuja execução observará "
            "a legislação aplicável e os princípios que regem a Administração Pública."
        ),
    ),
    Secao(
        key="requisitos-gerais",
        title="Requisitos Gerais de Participação",
        order=3,
        type=TEXTUAL,
        default_text=(
            "Poderá participar do processo seletivo quem atender às condições estabelecidas neste "
            "Edital e aos requisitos específicos do Perfil de Vaga pretendido, comprovados na "
            "forma e nos prazos aqui previstos."
        ),
    ),
    Secao(
        key="inscricao",
        title="Da Inscrição",
        order=4,
        type=TEXTUAL,
        default_text=(
            "A inscrição será realizada exclusivamente pelos meios indicados neste Edital, nos "
            "prazos do Cronograma, e implica conhecimento e aceitação das condições aqui "
            "estabelecidas."
        ),
    ),
    # Gerada, e ao lado da textual `inscricao` em vez de dentro dela: uma entrada do catálogo é
    # textual **ou** gerada, e o híbrido pediria um terceiro tipo para atender um caso. O que a
    # seção enuncia — os documentos que o candidato precisa apresentar — deriva dos dados
    # estruturados, como Perfis, Etapas e Cronograma já derivam (FR-010 da 009).
    Secao(
        key="documentos-exigidos",
        title="Documentos Exigidos para a Inscrição",
        order=5,
        type=GERADA,
        source="documentRequirements",
    ),
    Secao(
        key="perfis",
        title="Perfis de Vaga",
        order=6,
        type=GERADA,
        source="profiles",
    ),
    Secao(
        key="etapas",
        title="Etapas de Avaliação",
        order=7,
        type=GERADA,
        source="stages",
    ),
    Secao(
        key="classificacao",
        title="Critérios de Classificação",
        order=8,
        type=TEXTUAL,
        default_text=(
            "A classificação observará a pontuação obtida nas Etapas de Avaliação, respeitados os "
            "pesos e as notas mínimas declarados neste Edital e as reservas de vaga previstas."
        ),
    ),
    Secao(
        key="cronograma",
        title="Cronograma",
        order=9,
        type=GERADA,
        source="schedule",
    ),
    Secao(
        key="recursos",
        title="Dos Recursos",
        order=10,
        type=TEXTUAL,
        default_text=(
            "Caberá recurso contra os resultados divulgados, nos prazos do Cronograma, pelos meios "
            "indicados neste Edital."
        ),
    ),
    Secao(
        key="disposicoes-finais",
        title="Disposições Finais",
        order=11,
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
