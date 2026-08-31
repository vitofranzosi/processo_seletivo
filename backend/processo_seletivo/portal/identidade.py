"""A identidade do candidato — eixo próprio, e não mais um papel institucional.

O ator institucional tem escopo e permissões; o candidato não tem nem uma coisa nem outra. Ele é
titular de uma Inscrição, e titularidade é outra pergunta (`inscricoes/domain/titularidade.py`).
Acrescentar `CANDIDATO` ao mapa de papéis faria o candidato atravessar `require_permission` — e o
dia em que uma permissão fosse concedida a mais, ele praticaria ato institucional.

**Chave de sessão própria** (FR-021). A interface administrativa guarda a dela em
`interface_identidade`; esta fica em `portal_identidade`. As duas coexistem sem se confundir, e
cada canal lê apenas a sua: quem está identificado no `/gestao/` não é candidato, e vice-versa.

Enquanto o provedor institucional não existir, a identidade vem de um provedor de demonstração,
rotulado como tal na tela e recusado em produção pela guarda de `production.py` (FR-023, FR-024).
Quando o provedor real chegar, só este módulo muda — como a `002` decidiu para o outro eixo.
"""

from dataclasses import dataclass

from django.conf import settings

CHAVE_SESSAO = "portal_identidade"
PREFIXO_DEMONSTRACAO = "demo"


@dataclass(frozen=True)
class IdentidadeDoCandidato:
    """O que o provedor afirma sobre quem está ali.

    `subject` é o identificador estável, e é o único campo que decide propriedade de inscrição
    (FR-022). Nome, CPF e e-mail são o que a identidade **fornece** — e por isso não são pedidos
    de novo (FR-037).
    """

    subject: str
    nome: str = ""
    cpf: str = ""
    email: str = ""


def normalizar_cpf(valor: str) -> str:
    return "".join(caractere for caractere in valor if caractere.isdigit())


def identidade_da_sessao(request) -> IdentidadeDoCandidato | None:
    dados = request.session.get(CHAVE_SESSAO)
    if not dados:
        return None
    return IdentidadeDoCandidato(**dados)


def identificar(request, *, nome, cpf, email):
    """Registra a identidade na sessão do portal.

    O `subject` deriva do CPF normalizado porque é o que identifica a mesma pessoa entre visitas —
    e é ele, não o nome, que decide de quem é a inscrição. O prefixo diz de onde a identidade veio:
    quando o provedor real chegar, os dois conjuntos não se confundem.
    """
    identidade = IdentidadeDoCandidato(
        subject=f"{PREFIXO_DEMONSTRACAO}:{normalizar_cpf(cpf)}",
        nome=nome.strip(),
        cpf=cpf.strip(),
        email=email.strip(),
    )
    request.session[CHAVE_SESSAO] = identidade.__dict__
    return identidade


def encerrar(request):
    request.session.pop(CHAVE_SESSAO, None)


def provedor_de_demonstracao() -> bool:
    return bool(getattr(settings, "PORTAL_IDENTIDADE_DEMO", False))
