"""O envio exige a data de nascimento e a congela na inscrição (180, história 2).

FR-8303 (recusa do comando), FR-8308 (congela no ato, com a data do cadastro naquele instante), o
gatilho da enviada alcançando a coluna nova, e a premissa de que o comprovante não mostra a data.
"""

import dataclasses
from datetime import date

import pytest
from django.db import DatabaseError, transaction
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao, ValorDeFato
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, identificar, pdf
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEM_DATA = dataclasses.replace(MARIA, data_nascimento=None)


def _pronta(inscricao):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao, identidade=MARIA, chave="envio-180"):
    return enviar_inscricao(
        identidade=identidade,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=chave,
    )


def test_sem_data_o_envio_e_recusado(inscricao_de_maria):
    inscricao = _pronta(inscricao_de_maria)

    with pytest.raises(DomainError) as recusa:
        _enviar(inscricao, identidade=SEM_DATA)

    assert recusa.value.code == "birth_date_required"
    assert "Seus dados" in str(recusa.value.detail)
    inscricao.refresh_from_db()
    assert inscricao.status == Inscricao.Status.RASCUNHO


def test_o_envio_congela_a_data_do_cadastro(inscricao_de_maria):
    enviada = _enviar(_pronta(inscricao_de_maria))
    assert enviada.data_nascimento == MARIA.data_nascimento


def test_corrigir_o_cadastro_antes_do_envio_muda_o_que_e_congelado(inscricao_de_maria):
    """O rascunho acompanha o cadastro até o envio (FR-8308)."""
    corrigida = dataclasses.replace(MARIA, data_nascimento=date(1998, 3, 7))
    enviada = _enviar(_pronta(inscricao_de_maria), identidade=corrigida)
    assert enviada.data_nascimento == date(1998, 3, 7)


def test_a_data_da_enviada_nao_muda_pelo_banco(inscricao_de_maria):
    """O gatilho da `inscricoes/0007` alcança a coluna nova: a enviada é ato."""
    enviada = _enviar(_pronta(inscricao_de_maria))

    with pytest.raises(DatabaseError, match="submitted enrollments are immutable"):
        with transaction.atomic():
            Inscricao.objects.filter(pk=enviada.pk).update(data_nascimento=date(1990, 1, 1))

    enviada.refresh_from_db()
    assert enviada.data_nascimento == MARIA.data_nascimento


def test_o_comprovante_nao_mostra_a_data(client, inscricao_de_maria):
    """Minimização: o comprovante já identifica por nome e CPF (premissa da spec)."""
    enviada = _enviar(_pronta(inscricao_de_maria))
    identificar(client, MARIA)

    pagina = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert "Maria Silva" in pagina
    assert MARIA.data_nascimento.strftime("%d/%m/%Y") not in pagina
    assert "nascimento" not in pagina.lower()


FATO_DE_NASCIMENTO = "00000000-0000-0000-0000-0000000180a1"


def _com_o_fato_declarado(api_client, edital):
    """O Perfil passa a declarar o fato "data de nascimento", como quem desempata por idade."""
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/declaredFacts/-",
                "operation": "ADD",
                "newValue": {
                    "id": FATO_DE_NASCIMENTO,
                    "code": "NASCIMENTO",
                    "label": "Data de nascimento",
                    "type": "DATA",
                },
            }
        ],
        suffix="fato-180",
    )
    return abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)


def test_o_fato_declarado_do_perfil_continua_exigido_com_a_data_no_cadastro(
    api_client, selecao, candidatos_registrados
):
    """FR-8318, D-003: o cadastro tem a data, e o fato do Perfil não é preenchido por ela.

    O fato entra na classificação e é ato da inscrição. Preenchê-lo sozinho mudaria a regra do
    desempate sem que o Edital dissesse.
    """
    inscricao = _pronta(_com_o_fato_declarado(api_client, selecao))

    with pytest.raises(DomainError) as recusa:
        _enviar(inscricao)

    assert recusa.value.code == "declared_fact_required"
    assert not ValorDeFato.objects.filter(inscricao=inscricao).exists()


def test_o_fato_e_a_data_do_cadastro_sao_dois_valores_e_cada_um_congela_o_seu(
    api_client, selecao, candidatos_registrados
):
    """O fato pode trazer uma data diferente da do cadastro, e nenhuma corrige a outra."""
    inscricao = _pronta(_com_o_fato_declarado(api_client, selecao))

    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-180-fato",
        fatos={FATO_DE_NASCIMENTO: "1990-05-20"},
    )

    assert enviada.data_nascimento == MARIA.data_nascimento
    assert ValorDeFato.objects.get(inscricao=enviada).valor_data == date(1990, 5, 20)


def test_a_revisao_pede_o_fato_em_branco_mesmo_com_a_data_no_cadastro(
    client, api_client, selecao, candidatos_registrados
):
    """Na tela: a linha do cadastro mostra a data, e o campo do fato chega vazio (FR-8318)."""
    inscricao = _pronta(_com_o_fato_declarado(api_client, selecao))
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()

    inicio = corpo.index(f'id="fato-{FATO_DE_NASCIMENTO}"')
    campo = corpo[inicio : corpo.index(">", inicio)]
    assert 'value=""' in campo
    assert MARIA.data_nascimento.isoformat() not in campo
    assert MARIA.data_nascimento.strftime("%d/%m/%Y") in corpo, "a do cadastro está na linha dela"


def test_a_enviada_antes_da_180_fica_sem_data_e_nao_impede_nada(client, inscricao_de_maria):
    """FR-8304: a inscrição antiga não é alterada nem bloqueia o que o titular faz com ela.

    O desvio do gatilho é o único caminho para o estado: desde a `180` o envio recusa quem não tem
    data, e uma enviada sem ela é o que o produto produzia antes.
    """
    from tests.fixtures.comissao import sem_imutabilidade_da_enviada

    enviada = _enviar(_pronta(inscricao_de_maria))
    with sem_imutabilidade_da_enviada():
        Inscricao.objects.filter(pk=enviada.pk).update(data_nascimento=None)
    identificar(client, MARIA)

    comprovante = client.get(reverse("portal:comprovante", args=[enviada.id]))
    lista = client.get(reverse("portal:inscricoes"))

    assert comprovante.status_code == 200
    assert enviada.protocolo in lista.content.decode()
    enviada.refresh_from_db()
    assert enviada.data_nascimento is None, "ninguém a preencheu por causa da consulta"
    assert enviada.status == Inscricao.Status.SUBMETIDA
