"""A recusa da conferência de um documento da convocação, no lugar em que se a vê (FR-3611).

A recusa existia — "Abra o documento antes de conferi-lo como conforme" —, mas era impressa no topo
da página, enquanto o endereço levava a tela ao cartão do documento: quem marcava "conforme" sem
abrir o arquivo via a página recarregar no mesmo lugar e concluía que o botão não fazia nada. Agora
ela mora no formulário que a provocou, com o que foi marcado e digitado; no topo, só quando não há
formulário onde morar. E o formulário avisa antes do clique que a abertura é exigida.
"""

import pytest
from django.urls import reverse

from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import CERTIDAO, apresentar, conferir, item
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

RECUSADA = "A conferência não foi registrada."


@pytest.fixture
def chamada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    """Uma convocação com a certidão apresentada, a página dos documentos e o POST."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="recusa-3611",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao
    return {
        "edital": edital,
        "pessoa": pessoa,
        "convocacao": convocacao,
        "item": item(convocacao, CERTIDAO).id,
        "pagina": reverse(
            "interface:documentos-da-convocacao", args=[edital.id, MARCO, convocacao.id]
        ),
        "arquivo": reverse(
            "interface:documento-da-convocacao", args=[edital.id, MARCO, convocacao.id, feita.id]
        ),
        "conferir": reverse(
            "interface:conferir-documento",
            args=[edital.id, MARCO, convocacao.id, item(convocacao, CERTIDAO).id],
        ),
        "apresentacao": feita,
    }


def _conforme(client, chamada, **campos):
    return client.post(
        chamada["conferir"],
        {
            "resultado": "CONFORME",
            "apresentacao": str(chamada["apresentacao"].id),
            "chave": "conforme",
            **campos,
        },
    )


def _recusa(corpo, item_id):
    """O parágrafo da recusa, do `<p` de abertura ao `</p>`."""
    posicao = corpo.index(f'id="recusa-{item_id}"')
    return posicao, corpo[corpo.rindex("<p", 0, posicao) : corpo.index("</p>", posicao)]


def test_o_conforme_sem_abertura_volta_recusado_ao_cartao_do_documento(chamada, client):
    identificar(client, "carlos", ["gestor"])

    resposta = _conforme(client, chamada, motivo="Legível.")

    assert resposta.status_code == 302
    assert resposta["Location"].endswith(f"#recusa-{chamada['item']}")
    corpo = client.get(chamada["pagina"]).content.decode()
    posicao, trecho = _recusa(corpo, chamada["item"])
    assert corpo.index(f'id="item-{chamada["item"]}"') < posicao, "mora no cartão do item"
    assert corpo.index("Situação desta convocação") < posicao
    assert 'class="erro"' in trecho and 'role="alert"' in trecho and "autofocus" in trecho
    # A frase diz o que falta e como prosseguir, com o preenchimento mantido (157, UX-651).
    assert RECUSADA in trecho and "Você ainda não abriu a versão 1." in trecho
    assert "Abra a versão 1 e registre de novo; o que você marcou continua aqui." in trecho
    assert chamada["arquivo"] in trecho, "a recusa oferece abrir a versão que falta"
    assert 'value="CONFORME" required checked' in corpo, "o resultado marcado volta"
    assert ">Legível.</textarea>" in corpo, "o motivo digitado volta"


def test_a_recusa_vale_para_uma_leitura_so(chamada, client):
    identificar(client, "carlos", ["gestor"])
    _conforme(client, chamada)
    client.get(chamada["pagina"])

    corpo = client.get(chamada["pagina"]).content.decode()

    assert RECUSADA not in corpo
    assert "required checked" not in corpo


def test_o_formulario_avisa_antes_que_o_conforme_pede_a_abertura(chamada, client):
    identificar(client, "carlos", ["gestor"])
    frase = "Você ainda não abriu a versão 1."

    antes = client.get(chamada["pagina"]).content.decode()
    assert frase in antes
    assert 'aria-describedby="abertura-' in antes, "a frase descreve a opção para o leitor de tela"

    abrir_arquivo(client, chamada["arquivo"])
    depois = client.get(chamada["pagina"]).content.decode()
    assert frase not in depois
    assert "aberto por você" in depois


def test_depois_de_abrir_o_conforme_volta_ao_item_sem_recusa(chamada, client):
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    resposta = _conforme(client, chamada)

    assert resposta["Location"].endswith(f"#item-{chamada['item']}")
    corpo = client.get(chamada["pagina"]).content.decode()
    assert "Conferência registrada." in corpo
    assert RECUSADA not in corpo


def test_a_recusa_por_outro_motivo_nao_manda_abrir_o_arquivo(chamada, client):
    """A pendência sem motivo também volta ao cartão, mas a saída dela é o motivo, e não o
    arquivo: o link "abrir a versão" não a acompanha."""
    identificar(client, "carlos", ["gestor"])

    client.post(chamada["conferir"], {"resultado": "PENDENTE", "chave": "sem-motivo"})

    corpo = client.get(chamada["pagina"]).content.decode()
    _, trecho = _recusa(corpo, chamada["item"])
    assert "Diga o motivo" in trecho
    assert "Abrir a versão" not in trecho
    assert 'value="PENDENTE" required checked' in corpo


def test_sem_formulario_na_pagina_a_recusa_vai_ao_topo(chamada, client):
    """O Processo se encerrou entre abrir a página e registrar: a página não oferece mais o
    formulário, e uma recusa que só morasse nele se perderia sem aparecer em lugar nenhum."""
    from processo_seletivo.processos.models import ProcessoSeletivo

    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])
    ProcessoSeletivo.objects.filter(pk=chamada["edital"].processo_id).update(
        status=ProcessoSeletivo.Status.ENCERRADO
    )

    resposta = _conforme(client, chamada)

    assert resposta["Location"].endswith(f"#recusa-{chamada['item']}")
    corpo = client.get(chamada["pagina"]).content.decode()
    assert "Registrar conferência" not in corpo
    posicao, trecho = _recusa(corpo, chamada["item"])
    assert posicao < corpo.index("Situação desta convocação"), "no topo, e não num cartão"
    assert RECUSADA in trecho and "estado final" in trecho
    assert 'role="alert"' in trecho


def test_a_versao_superada_oferece_a_atual_e_nao_remarca_o_juizo(chamada, client, gestor):
    """Chegou a versão 2 enquanto se conferia a 1: a recusa manda abrir a atual e oferece o link
    dela, e o "conforme" dado à 1 não volta marcado sobre a 2, que a pessoa ainda não viu."""
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])
    conferir(
        gestor, chamada["convocacao"], CERTIDAO, "PENDENTE", chave="pendencia", motivo="Ilegível."
    )
    nova = apresentar(chamada["pessoa"], chamada["convocacao"], CERTIDAO, corpo=b"v2").apresentacao

    _conforme(client, chamada, motivo="Agora legível.")

    corpo = client.get(chamada["pagina"]).content.decode()
    _, trecho = _recusa(corpo, chamada["item"])
    assert "Chegou uma versão mais nova" in trecho
    assert f"Abrir a versão {nova.numero}" in trecho
    assert str(nova.id) in trecho
    assert "required checked" not in corpo, "o juízo era sobre a versão anterior"
    assert ">Agora legível.</textarea>" in corpo, "o texto digitado fica, para ser relido"
