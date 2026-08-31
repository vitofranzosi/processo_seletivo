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

import hashlib
import hmac
from dataclasses import dataclass

from django.conf import settings

CHAVE_SESSAO = "portal_identidade"
PREFIXO_DEMONSTRACAO = "demo"
# Limites que a persistência impõe. Conferi-los aqui é o que impede um campo grande demais virar
# erro de banco na gravação — em SQLite ele passa truncado, em PostgreSQL ele estoura.
LIMITES = {"nome": 255, "cpf": 20, "email": 254}


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


def contexto_candidato(request):
    """A identidade do candidato em todo template do portal, para o cabeçalho poder oferecer `Sair`.

    Separado de `contexto_identidade`, que é da interface administrativa: são dois eixos, com
    chaves de sessão distintas, e um não identifica no outro (FR-020, FR-021). Sem isto o portal
    não tinha como oferecer a saída — quem se identificasse num computador compartilhado ficava,
    e a pessoa seguinte se inscrevia com o CPF de quem estava antes.
    """
    return {"candidato": identidade_da_sessao(request)}


def identidade_da_sessao(request) -> IdentidadeDoCandidato | None:
    dados = request.session.get(CHAVE_SESSAO)
    if not dados:
        return None
    return IdentidadeDoCandidato(**dados)


def subject_de(cpf: str) -> str:
    """Identificador estável e **opaco**, derivado do CPF sem carregá-lo.

    O `subject` viaja para a auditoria como autor do ato, e FR-078 proíbe CPF completo ali. Derivar
    por HMAC preserva as duas propriedades que importam — a mesma pessoa é o mesmo subject entre
    visitas, e pessoas distintas não colidem — sem que o documento fique gravado em cada registro
    de auditoria, em cada inscrição e em cada log que mencione o ator.

    *A primeira redação usava `demo:<cpf>`, o que era legível e errado: o identificador que existe
    para não depender de dado pessoal não pode ser feito de dado pessoal.*

    Trocar a chave secreta troca os identificadores desta demonstração. É aceitável porque o
    provedor real trará os seus próprios, e o prefixo mantém os dois conjuntos separados.
    """
    digest = hmac.new(
        settings.SECRET_KEY.encode(), normalizar_cpf(cpf).encode(), hashlib.sha256
    ).hexdigest()
    return f"{PREFIXO_DEMONSTRACAO}:{digest[:32]}"


def identificar(request, *, nome, cpf, email):
    """Registra a identidade na sessão do portal.

    O `subject` deriva do CPF porque é o que identifica a mesma pessoa entre visitas — e é ele,
    não o nome, que decide de quem é a inscrição. O prefixo diz de onde a identidade veio: quando
    o provedor real chegar, os dois conjuntos não se confundem.
    """
    identidade = IdentidadeDoCandidato(
        subject=subject_de(cpf),
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
