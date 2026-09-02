"""Identidades, arquivos e atalhos de sessão do candidato.

As *fixtures* que dependem destes helpers vivem em `tests/conftest.py`, porque são usadas por
diretórios diferentes — integração e autorização — e o pytest só enxerga fixture do conftest da
raiz ou do próprio diretório.

**O que a 010 mudou aqui.** `MARIA` e `JOAO` continuam sendo o contrato que a jornada da `009`
consome, mas os identificadores deixaram de ser derivados do CPF pela chave secreta: agora são
valores fixos e opacos, como os que a aplicação passou a gerar. E `identificar` deixou de escrever
um dicionário na sessão — ela cria a identidade e a credencial, e guarda o identificador. É a mesma
troca que a feature fez no produto: o que estava declarado passou a estar registrado.
"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from processo_seletivo.portal.identidade import IdentidadeDoCandidato
from tests.fixtures.edital import identificador

CPF_MARIA = "123.456.789-09"
MARIA = IdentidadeDoCandidato(
    "cand:00000000000000000000000000000001", "Maria Silva", CPF_MARIA, "m@ex.br"
)
CPF_JOAO = "987.654.321-00"
JOAO = IdentidadeDoCandidato(
    "cand:00000000000000000000000000000002", "João Souza", CPF_JOAO, "j@ex.br"
)

PERFIL_DOCENTE = identificador(401, 0)
PERFIL_TECNICO = identificador(406, 0)
MODALIDADE_AC = identificador(403, 0)
MODALIDADE_PPP = identificador(404, 0)


def pdf(nome="diploma.pdf", corpo=b"conteudo"):
    return SimpleUploadedFile(nome, b"%PDF-1.4\n" + corpo, content_type="application/pdf")


def imagem(nome="foto.pdf"):
    """O que o celular produz ao fotografar um documento — renomeado, como as pessoas fazem."""
    return SimpleUploadedFile(nome, b"\xff\xd8\xff\xe0" + b"0" * 64, content_type="image/jpeg")


def registrar(identidade):
    """A identidade persistida que corresponde ao contrato, com a credencial já provada.

    Reusa a existente quando já há uma com aquele identificador: as *fixtures* compõem, e criar
    duas violaria a unicidade do endereço canônico — que é justamente o invariante que se quer
    exercendo, e não contornando.
    """
    from processo_seletivo.identidade.application.associacao import associar_credencial
    from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity
    from processo_seletivo.inscricoes.domain.pessoais import digitos

    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=identidade.subject,
        defaults={
            "nome": identidade.nome,
            "cpf_normalizado": digitos(identidade.cpf),
            "created_at": timezone.now(),
        },
    )
    if identidade.email and not CandidateEmail.objects.filter(
        email_canonico=identidade.email.lower()
    ).exists():
        associar_credencial(registro, identidade.email.lower(), identidade.email)
    return registro


def identificar(client, identidade):
    """Deixa a sessão do portal identificada — pelo registro, e não por declaração."""
    registro = registrar(identidade)
    sessao = client.session
    sessao["portal_identidade"] = str(registro.pk)
    sessao.save()
    return registro
