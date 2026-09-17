"""As duas ausências, na tela — e elas não são a mesma coisa (029, `US2`, `FR-405`, `SC-122`).

*"Este certame não pede Requerimento de Matrícula"* diz que não há o que preencher, nunca.
*"Ainda não é a hora"* diz que há, e que a vez da pessoa não chegou. Colapsá-las diria a quem ainda
tem chance que ela não tem — e a pessoa pararia de acompanhar. É a mesma distinção que a tela de
convocação já é obrigada a fazer, e pela mesma razão.

**A distinção é de tela, e por isso o teste é de tela.** O domínio já as separa em dois estados de
leitura, e um teste de domínio continuaria verde com as duas frases iguais no template — que é
precisamente o defeito que importa ao candidato.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.requerimentos.application import selectors
from processo_seletivo.requerimentos.domain import nomes
from tests.fixtures.requerimento import pronta_para_enviar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def texto_visivel(corpo):
    """O que a pessoa lê — **sem a folha de estilo**, que mora dentro do `base.html`.

    A prosa daquela folha explica as regras em português e cita *deferido*, *indeferido* e meia
    dúzia de outros termos do domínio. Varrer o HTML inteiro reprova por causa de um comentário de
    CSS, e é uma armadilha que este repositório já pagou mais de uma vez.
    """
    return re.sub(r"<style.*?</style>", " ", corpo, flags=re.S).lower()


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def test_as_duas_ausencias_tem_textos_distintos_no_vocabulario_da_tela():
    """A premissa, presa antes de olhar o HTML: as frases não podem ser a mesma string.

    Sem isto, alguém poderia igualar os dois textos no tradutor e a asserção de tela abaixo
    continuaria passando — ela veria a frase certa nos dois casos.
    """
    nao_pede = selectors._FRASES[nomes.NAO_APLICAVEL]
    ainda_nao = selectors._FRASES[nomes.AINDA_INDISPONIVEL]

    assert nao_pede[0] != ainda_nao[0]
    assert nao_pede[1] != ainda_nao[1]


def test_o_certame_que_nao_pede_nao_tem_pagina_nenhuma(client, selecao, candidatos_registrados):
    """A primeira ausência é **404**: onde o Edital não declara, o recurso não existe (`FR-371`).

    E é por isso que ela não precisa de frase na tela do requerimento — a frase dela mora no
    tradutor, para o cartão da inscrição, que também não aparece.
    """
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
    from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE

    inscricao = abrir_inscricao(identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE)
    entrar_como(client, inscricao)

    resposta = client.get(reverse("portal:requerimento", args=[inscricao.id]))

    assert resposta.status_code == 404
    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert "Requerimento de Matrícula" not in corpo, "nem cartão, nem menção"


def test_o_certame_que_pede_na_convocacao_diz_que_ainda_nao_chegou_a_vez(
    client, selecao_na_convocacao, candidatos_registrados
):
    """A segunda ausência é **200 com explicação**: o recurso existe e ainda não abriu."""
    inscricao = pronta_para_enviar(selecao_na_convocacao)
    entrar_como(client, inscricao)

    resposta = client.get(reverse("portal:requerimento", args=[inscricao.id]))

    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert selectors._FRASES[nomes.AINDA_INDISPONIVEL][0] in corpo
    assert "continue acompanhando" in corpo, "e diz o que fazer enquanto isso"
    assert selectors._FRASES[nomes.NAO_APLICAVEL][0] not in corpo


def test_a_tela_nao_promete_vaga_nem_matricula(
    client, selecao_na_convocacao, candidatos_registrados
):
    """`SC-132`: enviar o requerimento não decide nada, e nenhuma frase pode sugerir que decide.

    Quem decide a vaga é a convocação; quem efetiva a matrícula é o Registro Acadêmico. Uma frase
    aqui que prometesse qualquer um dos dois diria à pessoa que ela tem o que ainda não tem.
    """
    inscricao = pronta_para_enviar(selecao_na_convocacao)
    entrar_como(client, inscricao)

    corpo = client.get(reverse("portal:requerimento", args=[inscricao.id])).content.decode()

    visivel = texto_visivel(corpo)
    for proibida in (
        "deferido",
        "indeferido",
        "homologado",
        "matrícula efetivada",
        "vaga garantida",
    ):
        assert proibida not in visivel, f"a tela não pode dizer {proibida!r}"
