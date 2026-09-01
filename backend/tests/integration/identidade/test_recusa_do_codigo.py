"""A recusa diz qual dos motivos foi — e para de mentir sobre o código certo.

O percurso da jornada no navegador encontrou o defeito que estes testes fecham: esgotadas as cinco
tentativas, o desafio morre, mas a mensagem continuava sendo "Código inválido ou expirado". Quem
então encontrava o código **certo** na caixa de entrada e o digitava corretamente lia exatamente a
mesma recusa. Do lado do servidor tudo estava correto; do lado da pessoa o sistema estava mentindo
sobre a causa — e a saída que a frase indicava, pedir outro código, estava bloqueada pela janela de
espera, sem aviso. Era um laço fechado, no primeiro minuto de uso.

A `FR-031` continua valendo: ela proíbe distinguir **código errado de endereço inexistente**, e é
`test_a_recusa_nao_distingue_quem_existe` que a guarda.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import TETO_DE_TENTATIVAS, DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR
ENDERECO = "quem.erra@exemplo.test"


def pedir(client, endereco=ENDERECO):
    client.post(reverse("portal:acesso"), {"email": endereco})
    return DesafioDeAcesso.objects.filter(email_canonico=endereco).latest("criado_em")


def tentar(client, codigo):
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})
    corpo = resposta.content.decode()
    recusa = re.search(r'class="recusa"[^>]*>(.*?)</span>', corpo, re.S)
    return re.sub(r"\s+", " ", recusa.group(1)).strip() if recusa else ""


@pytest.fixture
def codigo_certo(client):
    """Um desafio real, com o código que a pessoa receberia."""
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    sessao = client.session
    sessao["portal_acesso_email"] = ENDERECO
    sessao["portal_acesso_finalidade"] = ENTRAR
    sessao.save()
    return codigo


def test_o_codigo_certo_depois_do_teto_diz_que_o_codigo_foi_cancelado(client, codigo_certo):
    """O defeito que perdia candidato, escrito como teste.

    Cinco erros, e então o código **correto**. Antes, a resposta era a mesma frase de código
    errado, e a pessoa concluía que o sistema estava quebrado.
    """
    for _ in range(TETO_DE_TENTATIVAS):
        tentar(client, "000000")

    recusa = tentar(client, codigo_certo)

    assert "tentativas deste código acabaram" in recusa
    assert "mesmo o código certo não vale mais" in recusa
    assert "Peça um novo código" in recusa
    assert "inválido" not in recusa, "a causa não é o código; é o teto"


def test_errar_diz_quantas_tentativas_restam(client, codigo_certo):
    assert "Restam 4 tentativas" in tentar(client, "000000")
    assert "Restam 3 tentativas" in tentar(client, "000000")
    tentar(client, "000000")
    assert "Resta 1 tentativa" in tentar(client, "000000"), "singular, e não '1 tentativas'"


def test_expirado_e_esgotado_nao_dizem_a_mesma_coisa(client, codigo_certo):
    from datetime import timedelta

    from django.utils import timezone

    DesafioDeAcesso.objects.filter(email_canonico=ENDERECO).update(
        expira_em=timezone.now() - timedelta(seconds=1)
    )

    recusa = tentar(client, codigo_certo)

    assert "expirou" in recusa
    assert "tentativas" not in recusa, "a causa é o prazo, e o saldo de tentativas não vem ao caso"


def test_codigo_ja_usado_diz_que_foi_usado(client, codigo_certo):
    assert tentar(client, codigo_certo) == "", "o primeiro uso entra"
    sessao = client.session
    sessao["portal_acesso_email"] = ENDERECO
    sessao["portal_acesso_finalidade"] = ENTRAR
    sessao.save()

    assert "já foi usado" in tentar(client, codigo_certo)


def test_a_recusa_nao_distingue_quem_existe(client):
    """O que a FR-031 realmente proíbe — e que continua valendo.

    Um endereço com identidade e outro sem produzem a mesma recusa, com o mesmo saldo: o desafio é
    criado para os dois de forma idêntica, e é o desafio, não a identidade, que a mensagem lê.
    """
    associacao.criar_identidade_com("existe@exemplo.test", "existe@exemplo.test")

    pedir(client, "existe@exemplo.test")
    com = tentar(client, "000000")
    client.session.flush()
    pedir(client, "ninguem@exemplo.test")
    sem = tentar(client, "000000")

    assert com == sem != ""


def test_o_estado_lido_depois_de_validar_conta_a_tentativa_recusada():
    """A classificação é lida **depois** da tentativa, e é o saldo posterior que ela anuncia."""
    _, codigo = servico.solicitar(email_canonico=ENDERECO, finalidade=ENTRAR)
    servico.validar(email_canonico=ENDERECO, finalidade=ENTRAR, codigo="000000")

    estado = servico.estado_atual(email_canonico=ENDERECO, finalidade=ENTRAR)

    assert estado.motivo == servico.CODIGO_ERRADO
    assert estado.tentativas_restantes == TETO_DE_TENTATIVAS - 1
    assert codigo, "o código certo continua existindo — o que mudou foi o saldo"


def test_sem_desafio_nenhum_o_estado_e_sem_desafio():
    assert servico.estado_atual(email_canonico=ENDERECO, finalidade=ENTRAR).motivo == (
        servico.SEM_DESAFIO
    )
