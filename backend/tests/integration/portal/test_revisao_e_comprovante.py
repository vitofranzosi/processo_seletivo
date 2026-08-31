"""A revisão, o envio e o comprovante, pela tela (US5 e US7 da 009).

Duas telas depois da identificação, e a segunda é esta. O que se prova aqui é o percurso: o que a
pessoa lê antes de confirmar, o que ela recebe depois, e o que acontece quando ela volta.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL


def _completar(inscricao, *, faltando=False):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    requisitos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if not faltando:
        requisitos.append((DOCUMENTO_DO_PERFIL, "diploma.pdf"))
    for requisito, nome in requisitos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_revisao_resume_tudo_com_editar_em_cada_bloco(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:revisao", args=[completa.id])).content.decode()

    assert "Professor de Informática" in corpo
    assert "Maria Silva" in corpo
    assert "rg.pdf" in corpo and "diploma.pdf" in corpo
    assert corpo.count("Editar") == 3, "oportunidade, dados e documentos"
    assert corpo.count(reverse("portal:inscricao", args=[completa.id])) >= 3


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_faltando_documento_a_revisao_nao_oferece_enviar(client, inscricao_de_maria):
    incompleta = _completar(inscricao_de_maria, faltando=True)
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:revisao", args=[incompleta.id])).content.decode()

    assert "Falta enviar: Diploma de graduação" in corpo
    assert "Enviar inscrição" not in corpo
    assert "Declarações" not in corpo, "não se pede aceite do que não se pode enviar"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_leva_ao_comprovante(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    resposta = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    assert resposta["Location"] == reverse("portal:comprovante", args=[completa.id])
    corpo = client.get(resposta["Location"]).content.decode()
    enviada = Inscricao.objects.get()
    assert enviada.protocolo in corpo
    assert "Inscrição realizada" in corpo
    assert "Professor de Informática" in corpo
    assert "rg.pdf" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_marcar_as_declaracoes_o_envio_e_recusado(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    resposta = client.post(reverse("portal:revisao", args=[completa.id]), {"veracidade": "on"})

    assert "declarações são obrigatórias" in resposta.content.decode()
    assert Inscricao.objects.get().status == Inscricao.Status.RASCUNHO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_duplo_envio_pela_tela_nao_cria_duas(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    declaracoes = {"veracidade": "on", "ciencia": "on"}

    primeira = client.post(reverse("portal:revisao", args=[completa.id]), declaracoes)
    segunda = client.post(reverse("portal:revisao", args=[completa.id]), declaracoes)

    assert primeira["Location"] == segunda["Location"], "o segundo clique leva ao mesmo lugar"
    assert Inscricao.objects.filter(status=Inscricao.Status.SUBMETIDA).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_inscricao_enviada_nao_volta_para_a_revisao(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    revisao = client.get(reverse("portal:revisao", args=[completa.id]))
    inscricao = client.get(reverse("portal:inscricao", args=[completa.id]))

    assert revisao["Location"] == reverse("portal:comprovante", args=[completa.id])
    assert inscricao.status_code == 200, "a tela abre, e é a de uma inscrição enviada"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_e_privado_e_imprimivel(client, inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    resposta = client.get(reverse("portal:comprovante", args=[completa.id]))

    assert "no-store" in resposta.headers["Cache-Control"]
    assert "@media print" in resposta.content.decode(), "a página se prepara para o papel"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_ja_enviou_reencontra_o_comprovante_na_selecao(client, inscricao_de_maria, selecao):
    """US7: voltar depois e achar o que fez, sem portal do candidato."""
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )

    corpo = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()

    assert "Ver comprovante" in corpo
    assert reverse("portal:comprovante", args=[completa.id]) in corpo
    assert "Continuar inscrição" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_o_comprovante_alheio_nao_e_alcancavel(client, inscricao_de_maria):
    from tests.fixtures.candidato import JOAO

    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)
    client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )
    identificar(client, JOAO)

    assert client.get(reverse("portal:comprovante", args=[completa.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_das_declaracoes_recebe_o_foco_e_aponta_o_que_falta(client, inscricao_de_maria):
    """SC-UX-005: alcançar o motivo da recusa.

    Quem acionou o botão estava no fim da página, e `role=alert` anuncia o que **muda** numa página
    já carregada — não o que já veio no HTML da resposta. Sem mover o foco, para quem usa leitor de
    tela o envio simplesmente não acontece e nada é dito.
    """
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    corpo = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on"}
    ).content.decode()

    assert 'data-recusa' in corpo and 'tabindex="-1"' in corpo
    assert 'href="#ciencia"' in corpo, "o resumo leva à declaração que falta"
    assert 'href="#veracidade"' not in corpo, "a que foi marcada não é cobrada"
    assert "portal/recusa.js" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_nao_apaga_a_declaracao_ja_marcada(client, inscricao_de_maria):
    """SC-UX-007: nenhuma recusa obriga a repetir o que já estava certo."""
    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    corpo = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on"}
    ).content.decode()

    marcada = corpo[corpo.index('id="veracidade"') :][:220]
    esquecida = corpo[corpo.index('id="ciencia"') :][:220]
    assert "checked" in marcada, "volta marcada"
    assert "checked" not in esquecida
    assert 'aria-invalid="true"' in esquecida, "e a que falta é anunciada como inválida"
    assert 'aria-invalid="true"' not in marcada


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_pode_ser_impresso_e_reencontrado(client, inscricao_de_maria):
    """L1 da auditoria de percurso: o comprovante precisa ser levável.

    Num celular, "imprimir ou salvar em PDF" está atrás do menu do navegador, e quem acabou de se
    inscrever não vai procurá-lo. O protocolo é a única prova que a pessoa leva.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    completa = _completar(inscricao_de_maria)
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-comprovante-imprimivel",
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert "Imprimir ou salvar em PDF" in corpo
    assert "data-imprimir" in corpo and "hidden" in corpo, "sem JS não fica botão morto na tela"
    assert "portal/comprovante.js" in corpo
    assert "Guarde o número do protocolo" in corpo
    assert "identifique-se com o mesmo CPF" in corpo, "diz como voltar a este comprovante"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_tres_etapas_dizem_onde_a_pessoa_esta(client, inscricao_de_maria):
    """L3: identificação, dados, documentos, revisão e comprovante eram cinco momentos sem nome.

    Quem se inscreve num concurso costuma fazê-lo uma vez na vida, e a incerteza sobre "quanto
    ainda falta" é o que faz fechar a aba.
    """
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    completa = _completar(inscricao_de_maria)
    identificar(client, MARIA)

    inscricao = client.get(reverse("portal:inscricao", args=[completa.id])).content.decode()
    assert "Etapa 1 de 3" in inscricao
    assert 'aria-label="Etapas da inscrição"' in inscricao

    revisao = client.get(reverse("portal:revisao", args=[completa.id])).content.decode()
    assert "Etapa 2 de 3" in revisao
    assert revisao.count('class="concluida"') == 1, "a primeira já passou"

    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-etapas",
    )
    comprovante = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()
    assert "Etapa 3 de 3" in comprovante
    assert comprovante.count('class="concluida"') == 2
