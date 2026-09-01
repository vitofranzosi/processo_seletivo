"""A identidade do candidato na sessão — agora lida de um registro, e não mais declarada.

O ator institucional tem escopo e permissões; o candidato não tem nem uma coisa nem outra. Ele é
titular de uma Inscrição, e titularidade é outra pergunta (`inscricoes/domain/titularidade.py`).
Acrescentar `CANDIDATO` ao mapa de papéis faria o candidato atravessar `require_permission` — e o
dia em que uma permissão fosse concedida a mais, ele praticaria ato institucional.

**Chave de sessão própria** (FR-039). A interface administrativa guarda a dela em
`interface_identidade`; esta fica em `portal_identidade`. As duas coexistem sem se confundir, e
cada canal lê apenas a sua: quem está identificado no `/gestao/` não é candidato, e vice-versa.

**A identificação por declaração saiu.** Quem entra prova o controle de um endereço de e-mail; o
provedor que deixava qualquer pessoa dizer quem era foi removido com a `010`, e com ele o
identificador derivado do CPF pela chave secreta — a dependência que tornava a propriedade de cada
inscrição refém da rotação de um segredo de configuração.

**O que a 010 mudou aqui.** A sessão guarda o **identificador da identidade**, e nada mais. Nome,
CPF e endereço vêm do registro a cada requisição (D-008). A `009` guardava os três na sessão, o que
era correto quando eram declarados e efêmeros; guardá-los agora deixaria a sessão exibir dado
obsoleto até a pessoa sair e entrar — e a regra é que corrigir o nome alcance os rascunhos abertos
(FR-014). O custo é uma consulta por requisição do portal, na ordem das que a página já faz.
"""

from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.domain.pessoais import digitos, formatar_cpf

CHAVE_SESSAO = "portal_identidade"
PREFIXO_DEMONSTRACAO = "demo"
# Limites que a persistência impõe. Conferi-los aqui é o que impede um campo grande demais virar
# erro de banco na gravação — em SQLite ele passa truncado, em PostgreSQL ele estoura.
LIMITES = {"nome": 255, "cpf": 20, "email": 254}


@dataclass(frozen=True)
class IdentidadeDoCandidato:
    """O que o sistema afirma sobre quem está ali.

    `subject` é o identificador estável, e é o único campo que decide propriedade de inscrição
    (FR-001). Nome, CPF e e-mail são o que a identidade **fornece** — e por isso não são pedidos de
    novo a cada inscrição (FR-005).
    """

    subject: str
    nome: str = ""
    cpf: str = ""
    email: str = ""


def normalizar_cpf(valor: str) -> str:
    """O CPF só com dígitos. Continua exposto daqui porque `rascunho.py` e as views o consomem."""
    return digitos(valor)


def normalizar_email(valor: str) -> str:
    return valor.strip().lower()


def contexto_candidato(request):
    """A identidade do candidato em todo template do portal, para o cabeçalho poder oferecer `Sair`.

    Separado de `contexto_identidade`, que é da interface administrativa: são dois eixos, com
    chaves de sessão distintas, e um não identifica no outro (FR-039).
    """
    return {"candidato": identidade_da_sessao(request)}


def identidade_da_sessao(request) -> IdentidadeDoCandidato | None:
    guardado = request.session.get(CHAVE_SESSAO)
    if not guardado:
        return None
    return contrato_de(_registro(guardado))


def _registro(identidade_id) -> CandidateIdentity | None:
    return (
        CandidateIdentity.objects.filter(pk=identidade_id)
        .prefetch_related("credenciais")
        .first()
    )


def contrato_de(registro: CandidateIdentity | None) -> IdentidadeDoCandidato | None:
    """O que a jornada da `009` consome, montado a partir do que a `010` persiste (P-008).

    O e-mail é o da credencial **principal**, e não o endereço que autenticou a sessão: é ele que
    vai para a Inscrição, e trocar de caixa não pode trocar o contato de um certame em andamento
    (FR-013).
    """
    if registro is None:
        return None
    principal = next(
        (item for item in registro.credenciais.all() if item.principal),
        None,
    )
    return IdentidadeDoCandidato(
        subject=registro.subject,
        nome=registro.nome,
        cpf=formatar_cpf(registro.cpf_normalizado) if registro.cpf_normalizado else "",
        email=principal.email_como_informado if principal else "",
    )


def abrir_sessao(request, registro: CandidateIdentity) -> IdentidadeDoCandidato:
    """Autentica — e a primeira coisa que faz é trocar o identificador da sessão (FR-035).

    Sem a rotação, quem induzir a pessoa a usar uma sessão conhecida antes de entrar continua
    dentro dela depois: o desafio inteiro é contornado sem ser tocado. `cycle_key` troca o
    identificador e preserva o conteúdo, que é o necessário para não perder o destino de retorno.
    """
    request.session.cycle_key()
    request.session[CHAVE_SESSAO] = str(registro.pk)
    return contrato_de(registro)


def identidade_autenticada(request) -> CandidateIdentity | None:
    """O registro, para quem precisa dele — e não do contrato."""
    guardado = request.session.get(CHAVE_SESSAO)
    if not guardado:
        return None
    return _registro(guardado)


def criar_identidade(*, nome: str = "", cpf_normalizado: str = "") -> CandidateIdentity:
    from processo_seletivo.identidade.models import novo_subject

    return CandidateIdentity.objects.create(
        subject=novo_subject(),
        nome=nome,
        cpf_normalizado=cpf_normalizado,
        created_at=timezone.now(),
    )


def encerrar(request):
    request.session.pop(CHAVE_SESSAO, None)


def provedor_de_demonstracao() -> bool:
    """Sobrevive apenas como armadilha, e nunca devolve verdade em produção.

    A tela que esta variável habilitava **não existe mais** (FR-048). A recusa de inicialização que
    ela dispara em `production.py` continua ativa de propósito: se a identificação por declaração
    voltar, por descuido ou por atalho de alguém com pressa, produção não sobe.
    """
    return bool(getattr(settings, "PORTAL_IDENTIDADE_DEMO", False))
