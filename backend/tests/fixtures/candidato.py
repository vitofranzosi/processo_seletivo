"""Identidades, arquivos e atalhos de sessão do candidato.

As *fixtures* que dependem destes helpers vivem em `tests/conftest.py`, porque são usadas por
diretórios diferentes — integração e autorização — e o pytest só enxerga fixture do conftest da
raiz ou do próprio diretório.
"""

from django.core.files.uploadedfile import SimpleUploadedFile

from processo_seletivo.portal.identidade import IdentidadeDoCandidato, subject_de
from tests.fixtures.edital import identificador

CPF_MARIA = "123.456.789-09"
MARIA = IdentidadeDoCandidato(subject_de(CPF_MARIA), "Maria Silva", CPF_MARIA, "m@ex.br")
CPF_JOAO = "987.654.321-00"
JOAO = IdentidadeDoCandidato(subject_de(CPF_JOAO), "João Souza", CPF_JOAO, "j@ex.br")

PERFIL_DOCENTE = identificador(401, 0)
PERFIL_TECNICO = identificador(406, 0)
MODALIDADE_AC = identificador(403, 0)
MODALIDADE_PPP = identificador(404, 0)


def pdf(nome="diploma.pdf", corpo=b"conteudo"):
    return SimpleUploadedFile(nome, b"%PDF-1.4\n" + corpo, content_type="application/pdf")


def imagem(nome="foto.pdf"):
    """O que o celular produz ao fotografar um documento — renomeado, como as pessoas fazem."""
    return SimpleUploadedFile(nome, b"\xff\xd8\xff\xe0" + b"0" * 64, content_type="image/jpeg")


def identificar(client, identidade):
    sessao = client.session
    sessao["portal_identidade"] = identidade.__dict__
    sessao.save()
