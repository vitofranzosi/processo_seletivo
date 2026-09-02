"""Dado pessoal do candidato não vaza para log nem para auditoria (T109, FR-074, FR-078).

O sistema já registra muita coisa — é o que a Constituição exige. O que este arquivo protege é o
que **não** pode estar nesses registros: eles são lidos por operação, exportados para análise, e
sobrevivem à inscrição.

A verificação percorre a jornada inteira, com o log capturado, em vez de conferir campo a campo:
um campo novo que passe a carregar CPF aparece aqui sem que ninguém precise lembrar de acrescentar
uma asserção.
"""

import logging

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.domain.pessoais import digitos
from tests.fixtures.candidato import CPF_MARIA, MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

# O que não pode aparecer: o documento em qualquer grafia, o e-mail, o nome da pessoa e o nome do
# arquivo que ela escolheu — nomes de arquivo carregam dado pessoal com frequência.
PROIBIDOS = ("123.456.789-09", "12345678909", "maria@exemplo.br", "Maria Silva", "cpf-de-maria.pdf")


@pytest.fixture
def jornada(client, inscricao_de_maria):
    """Abre, preenche, anexa, envia — e ainda erra de propósito, para exercitar as recusas."""
    identificar(client, MARIA)
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        dados={
            "nome": "Maria Silva",
            "cpf": "123.456.789-09",
            "email": "maria@exemplo.br",
            "modality_id": MODALIDADE_AC,
        },
    )
    for requisito, nome in (
        (DOCUMENTO_DE_TODOS, "cpf-de-maria.pdf"),
        (DOCUMENTO_DO_PERFIL, "diploma.pdf"),
    ):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    # Uma recusa no meio: recusa é o que mais tenta explicar, e explicar é onde o dado escapa.
    client.post(reverse("portal:revisao", args=[inscricao.id]), {"veracidade": "on"})
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="jornada-pii",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_auditoria_da_jornada_nao_carrega_dado_pessoal(jornada):
    registros = RegistroAuditoria.objects.filter(aggregate_type="Inscricao")

    assert registros.exists(), "a jornada precisa ter deixado trilha"
    for registro in registros:
        texto = " ".join(
            [registro.actor_subject, registro.reason, registro.operation, registro.permission]
        )
        for proibido in PROIBIDOS:
            assert proibido not in texto, f"{proibido} apareceu na trilha de auditoria"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_log_da_jornada_nao_carrega_dado_pessoal(client, inscricao_de_maria, caplog):
    with caplog.at_level(logging.DEBUG):
        identificar(client, MARIA)
        inscricao = gravar_dados(
            identidade=MARIA,
            inscricao=inscricao_de_maria,
            dados={
                "nome": "Maria Silva",
                "cpf": "123.456.789-09",
                "email": "maria@exemplo.br",
                "modality_id": MODALIDADE_AC,
            },
        )
        anexar_documento(
            identidade=MARIA,
            inscricao=inscricao,
            requirement_id=DOCUMENTO_DE_TODOS,
            arquivo=pdf("cpf-de-maria.pdf"),
        )
        # Recusas, que é onde a mensagem tenta explicar o que houve.
        client.post(
            reverse("portal:enviar-documento", args=[inscricao.id, DOCUMENTO_DO_PERFIL]),
            {"arquivo": pdf("grande.pdf", corpo=b"x")},
        )
        client.post(reverse("portal:revisao", args=[inscricao.id]), {"veracidade": "on"})

    registrado = " ".join(registro.getMessage() for registro in caplog.records)
    for proibido in PROIBIDOS:
        assert proibido not in registrado, f"{proibido} apareceu no log"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_ator_registrado_e_o_identificador_opaco(jornada):
    registro = RegistroAuditoria.objects.filter(aggregate_type="Inscricao").first()

    assert registro.actor_subject == MARIA.subject
    # O prefixo mudou de `demo:` para `cand:` com a 010, e o que o teste afirma é o mesmo: o ator
    # registrado é opaco. O que ele **não** pode ser é derivado do CPF — nem por segredo.
    assert registro.actor_subject.startswith("cand:")
    assert CPF_MARIA not in registro.actor_subject
    assert digitos(CPF_MARIA) not in registro.actor_subject
    assert len(registro.actor_subject.split(":")[1]) == 32, "resumo, e não documento"
