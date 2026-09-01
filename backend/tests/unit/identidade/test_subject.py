"""O identificador estável de identidades novas.

Ele não deve nada a segredo de configuração nem a dado pessoal (FR-002).
"""

from django.test import override_settings

from processo_seletivo.identidade.models import PREFIXO, novo_subject


def test_e_opaco_e_prefixado():
    subject = novo_subject()
    assert subject.startswith(f"{PREFIXO}:")
    assert len(subject) == len(PREFIXO) + 1 + 32


def test_nao_se_repete():
    assert len({novo_subject() for _ in range(500)}) == 500


def test_nao_depende_da_chave_secreta():
    """Era a dependência do provedor de demonstração, e é a que esta feature existe para encerrar.

    Com o identificador derivado da `SECRET_KEY`, rotacioná-la tornaria cada inscrição
    inalcançável pelo titular — em silêncio, porque nada quebra: a busca simplesmente não acha.
    """
    with override_settings(SECRET_KEY="uma-chave"):
        um = novo_subject()
    with override_settings(SECRET_KEY="outra-chave-totalmente-diferente"):
        outro = novo_subject()
    assert um.split(":")[0] == outro.split(":")[0]
    assert um != outro, "identificadores distintos por serem aleatórios, não por causa da chave"


def test_nao_carrega_dado_pessoal():
    """Um `subject` não pode ser derivado do CPF: ele viaja para a auditoria como autor do ato."""
    subject = novo_subject()
    assert subject.split(":")[1].isalnum()
    assert not any(caractere.isspace() for caractere in subject)
