"""O recurso é do titular, e o protocolo não é chave de acesso.

Duas portas para uma peça — o formulário de interposição e a consulta —, e as duas fazem a mesma
pergunta: **este registro é dele?** Nenhuma composição de permissões institucionais responde a
isso, e escrever a segunda pergunta como se fosse a primeira é como se cria um IDOR com aparência
de autorização (FR-004, FR-104).

A recusa é `404`, e é indistinguível da recusa por inexistência. Um `403` diria "existe, mas não é
seu" — e num certame quem sabe **que** alguém recorreu já sabe demais.

O protocolo aparece aqui por um motivo específico: ele é público no sentido de que a pessoa o
carrega, o cola em e-mail e o mostra na secretaria. Se conferisse acesso, bastaria um protocolo
vazado para ler a fundamentação de outra pessoa.
"""

import uuid

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.divulgacao import (
    emitir,
    entrar_como_titular,
    montar_marco,
    pontuar,
    publicar_o_ato,
)
from tests.fixtures.recursos import interpor

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.authorization]

INEXISTENTE = "00000000-0000-0000-0000-0000000009ff"


@pytest.fixture
def peca_de_outra_pessoa(gestor, api_client, manager_headers, process_payload):
    """Um recurso interposto pela primeira inscrição — e a segunda, que vai tentar lê-lo."""
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=92, codigo="0792"
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=921, sufixo="92"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us2-auth")
    publicar_o_ato(cenario, chave="publicar-018-us2-auth")
    dona, intrusa = cenario["inscricoes"]
    peca = interpor(
        inscricao=dona,
        versao=selecao_publica(edital_id=dona.edital_id),
        resultado=ResultadoEtapa.vigentes.get(inscricao=dona, etapa_id=cenario["etapa"]),
        protocolo="REC-2026-AUTH0001",
    )
    return {"cenario": cenario, "peca": peca, "dona": dona, "intrusa": intrusa}


def test_a_titular_le_o_proprio_recurso(client, peca_de_outra_pessoa):
    """A prova de que a recusa das outras não é uma rota quebrada.

    Sem esta, todo `404` abaixo passaria com a view inexistente — que é o modo clássico de um
    teste de autorização mentir.
    """
    entrar_como_titular(client, peca_de_outra_pessoa["dona"])

    resposta = client.get(reverse("portal:recurso", args=[peca_de_outra_pessoa["peca"].id]))

    assert resposta.status_code == 200
    assert "REC-2026-AUTH0001" in resposta.content.decode()


def test_o_recurso_alheio_responde_404(client, peca_de_outra_pessoa):
    entrar_como_titular(client, peca_de_outra_pessoa["intrusa"])

    resposta = client.get(reverse("portal:recurso", args=[peca_de_outra_pessoa["peca"].id]))

    assert resposta.status_code == 404


def test_a_recusa_e_indistinguivel_da_inexistente(client, peca_de_outra_pessoa):
    entrar_como_titular(client, peca_de_outra_pessoa["intrusa"])

    alheio = client.get(reverse("portal:recurso", args=[peca_de_outra_pessoa["peca"].id]))
    inexistente = client.get(reverse("portal:recurso", args=[INEXISTENTE]))

    assert alheio.status_code == inexistente.status_code == 404
    # O corpo do 404 cita o caminho pedido, e por isso não é idêntico entre os dois. O que não
    # pode vazar é o **conteúdo** da peça: nem o protocolo, nem a fundamentação.
    assert "REC-2026-AUTH0001" not in alheio.content.decode()


def test_sem_sessao_nenhuma_o_recurso_nao_abre(client, peca_de_outra_pessoa):
    """Quem não entrou não é titular de coisa alguma — e `e_titular` recusa identidade vazia."""
    resposta = client.get(reverse("portal:recurso", args=[peca_de_outra_pessoa["peca"].id]))

    assert resposta.status_code in (302, 404), resposta.status_code
    assert "REC-2026-AUTH0001" not in resposta.content.decode()


def test_o_protocolo_nao_confere_acesso(client, peca_de_outra_pessoa):
    """O protocolo circula: vai por e-mail, é lido ao telefone, é colado num formulário.

    Se ele abrisse a peça, bastaria um vazamento para expor a fundamentação de outra pessoa — que
    é justamente o conteúdo mais sensível do recurso.
    """
    entrar_como_titular(client, peca_de_outra_pessoa["intrusa"])

    resposta = client.get(
        reverse("portal:recurso", args=[peca_de_outra_pessoa["peca"].id]),
        {"protocolo": "REC-2026-AUTH0001"},
    )

    assert resposta.status_code == 404


def test_interpor_na_inscricao_alheia_responde_404(client, peca_de_outra_pessoa):
    """A porta de entrada da interposição é a mesma titularidade da consulta."""
    entrar_como_titular(client, peca_de_outra_pessoa["intrusa"])

    resposta = client.get(
        reverse("portal:recorrer", args=[peca_de_outra_pessoa["dona"].id]), follow=False
    )

    assert resposta.status_code == 404


def test_interpor_por_post_na_inscricao_alheia_tambem_responde_404(client, peca_de_outra_pessoa):
    """O `GET` recusado sem o `POST` recusado é meia garantia: é o `POST` que grava."""
    entrar_como_titular(client, peca_de_outra_pessoa["intrusa"])
    alvo = ResultadoEtapa.vigentes.get(
        inscricao=peca_de_outra_pessoa["dona"],
        etapa_id=peca_de_outra_pessoa["cenario"]["etapa"],
    )

    resposta = client.post(
        reverse("portal:recorrer", args=[peca_de_outra_pessoa["dona"].id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "Quero recorrer do resultado dela."},
    )

    assert resposta.status_code == 404
    # A peça da fixture continua sendo a única: o `POST` recusado não acrescentou nada.
    assert peca_de_outra_pessoa["dona"].recursos.count() == 1
    assert alvo.inscricao_id == peca_de_outra_pessoa["dona"].id


def test_recurso_inexistente_responde_404(client, peca_de_outra_pessoa):
    entrar_como_titular(client, peca_de_outra_pessoa["dona"])

    assert client.get(reverse("portal:recurso", args=[uuid.uuid4()])).status_code == 404
