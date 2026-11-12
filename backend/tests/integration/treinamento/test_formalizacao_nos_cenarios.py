"""O treinamento da formalização pela interface (134, FR-6720 a FR-6729, SC-2210 a SC-2212).

**O achado que motivou a revisão** (achado 06 da reavaliação da jornada final de 12/11/2026): o
papel Formalização do seletor vale só para a sessão, e o Centro dizia "ninguém designado" com o
setor exportando. Aqui a pessoa do setor é a do cenário, com vínculo e designação de verdade, e a
exportação e o Centro são lidos **pela tela**, com a identidade que o guia manda usar.
"""

import re

import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError
from django.urls import reverse

from processo_seletivo.formalizacao.application import passagem
from processo_seletivo.formalizacao.application.designar import designar
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.domain.autorizacao import designacoes_vigentes
from processo_seletivo.formalizacao.models import (
    DesignacaoParaFormalizacao,
    ExportacaoDeFormalizacao,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.models import Vinculo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, restaurar, retomar
from tests.integration.formalizacao.apoio import abrir_zip, baixar, comprovante_da, verificar
from tests.interface.conftest import identificar
from tests.seguranca.apoio import vincular

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

AUTORIDADE = str(AUTORIDADE_DA_SUITE)
SETOR = (k.FORMALIZACAO, [nomes.PAPEL])


@pytest.fixture
def cenario(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True

    def montar(codigo):
        saida = carregar(codigo, autoridade=AUTORIDADE)
        assert f"{codigo}  CRIADO" in saida, saida
        manifesto = CenarioDeTreinamento.objects.get(codigo=codigo, situacao="PRONTO")
        return Edital.objects.get(processo=manifesto.processo)

    return montar


def _centro(client, edital):
    identificar(client, k.GESTAO, ["gestor"])
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]) + "?fase=conclusao")
    assert resposta.status_code == 200
    return " ".join(re.sub(r"<[^>]+>", " ", resposta.content.decode()).split())


def test_c16_o_setor_entra_verifica_e_exporta_e_o_centro_conta_a_designacao(client, cenario):
    """SC-2210: o fim da jornada pela interface, com a identidade do guia."""
    edital = cenario("C16")
    lido = passagem.da_passagem(edital)
    assert (lido.aptas, lido.designadas, lido.com_o_papel) == (3, 1, 1)
    assert lido.pendentes[passagem.A_EXPORTAR] == 3

    centro = _centro(client, edital)
    assert "Quem recebe: 1 pessoa designada" in centro
    assert "ninguém está designado" not in centro

    identificar(client, *SETOR)
    lista = client.get(reverse("interface:formalizacao")).content.decode()
    assert str(edital.id) in lista
    comprovante = comprovante_da(verificar(client, edital))
    assert comprovante, "a verificação oferece o download"
    resposta = baixar(client, edital, comprovante)
    assert resposta.status_code == 200
    pacote = abrir_zip(resposta)
    assert sum(nome.endswith(".pdf") for nome in pacote.namelist()) == 3

    assert ExportacaoDeFormalizacao.objects.filter(edital=edital).count() == 1
    assert passagem.da_passagem(edital).disponibilizadas == 3


def test_c17_a_pessoa_so_habilitada_ve_que_nao_foi_designada_e_o_centro_pede_a_designacao(
    client, cenario
):
    """SC-2211, e a próxima ação da ficha: quem administra os acessos designa (FR-4655)."""
    edital = cenario("C17")
    lido = passagem.da_passagem(edital)
    assert (lido.aptas, lido.designadas, lido.com_o_papel) == (3, 0, 1)
    assert lido.pendentes[passagem.SEM_QUEM_RECEBA] == 3
    assert "ninguém está designado" in _centro(client, edital)

    identificar(client, *SETOR)
    lista = client.get(reverse("interface:formalizacao")).content.decode()
    assert "Você ainda não foi designado" in lista

    m = retomar(CenarioDeTreinamento.objects.get(codigo="C17"), autoridade=AUTORIDADE)
    pessoa = get_user_model().objects.get(username=k.FORMALIZACAO)
    # Quem a ficha não nomeia não designa: a presidência conduz, e não dá acesso (18.6).
    with pytest.raises(DomainError):
        designar(
            m.ator(k.PRESIDENCIA),
            edital_id=edital.id,
            pessoa=pessoa,
            perfis=[],
            motivo="Exercício.",
            now=m.agora,
        )
    designar(
        m.ator(k.ACESSOS),
        edital_id=edital.id,
        pessoa=pessoa,
        perfis=[],
        motivo="Exercício.",
        now=m.agora,
    )
    assert passagem.da_passagem(edital).designadas == 1


def _da_formalizacao():
    return Vinculo.objects.filter(pessoa__username=k.FORMALIZACAO, papel=nomes.PAPEL)


def test_o_provisionamento_cria_uma_pessoa_e_um_vinculo_e_nada_mais_nem_de_novo(treinamento):
    """SC-2212, FR-6721, FR-6722, FR-6725."""
    pessoas, vinculos = get_user_model().objects.count(), Vinculo.objects.count()
    previa = carregar("C16", "C17", dry_run=True)
    assert previa.count(f"pessoa {k.FORMALIZACAO}: criar") == 1, "só o primeiro do plano cria"
    assert previa.count("papel Formalização em cefor: conceder") == 1
    assert "papel Formalização em cefor: do cenário anterior" in previa

    saida = carregar("C16", "C17", autoridade=AUTORIDADE)
    assert saida.count("CRIADO") == 2, saida
    assert get_user_model().objects.count() == pessoas + 1
    assert Vinculo.objects.count() == vinculos + 1
    assert _da_formalizacao().count() == 1
    pessoa = get_user_model().objects.get(username=k.FORMALIZACAO)
    assert not pessoa.has_usable_password()
    assert not pessoa.identidades_externas.exists()

    assert k.FORMALIZACAO not in carregar("C01", dry_run=True), "só o C16 e o C17 provisionam"
    assert carregar("C16", "C17", autoridade=AUTORIDADE).count("MANTER") == 2
    assert get_user_model().objects.count() == pessoas + 1
    assert Vinculo.objects.count() == vinculos + 1


@pytest.mark.parametrize("com_o_papel", [False, True], ids=["sem-vinculo", "suspensa-com-vinculo"])
def test_a_pessoa_inativa_nao_e_reativada_e_o_cenario_falha_pela_recusa(treinamento, com_o_papel):
    """FR-6721: o gerador nunca altera a pessoa que encontra.

    A suspensão da `107` desliga a pessoa e deixa o vínculo vigente: sem a recusa própria, o C17
    nasceria pronto com uma pessoa que ninguém consegue designar.
    """
    pessoa = get_user_model().objects.create(username=k.FORMALIZACAO, is_active=False)
    if com_o_papel:
        vincular(pessoa, "cefor", nomes.PAPEL)
    vinculos = Vinculo.objects.count()
    saida = carregar("C17", autoridade=AUTORIDADE)
    assert "C17  FALHOU" in saida, saida
    assert "pessoa_indisponivel" in saida, saida
    pessoa.refresh_from_db()
    assert not pessoa.is_active
    assert Vinculo.objects.count() == vinculos
    assert not CenarioDeTreinamento.objects.filter(codigo="C17").exists()


@pytest.mark.django_db(transaction=True)
def test_restaurar_o_c16_revoga_a_designacao_anterior_e_reaproveita_pessoa_e_vinculo(
    client, cenario
):
    """FR-6726, SC-2212: a lista do setor fica com o Edital da rodada nova, e só ele."""
    anterior = cenario("C16")
    vinculos = Vinculo.objects.count()
    with pytest.raises(CommandError):
        restaurar("C16")
    restaurar("C16", confirmar="C16", autoridade=AUTORIDADE)
    novo = Edital.objects.get(
        processo=CenarioDeTreinamento.objects.get(codigo="C16", situacao="PRONTO").processo
    )
    assert Vinculo.objects.count() == vinculos
    assert not designacoes_vigentes(edital=anterior).exists()
    assert DesignacaoParaFormalizacao.objects.filter(edital=anterior).count() == 1
    assert designacoes_vigentes(edital=novo, pessoa=k.FORMALIZACAO).count() == 1

    identificar(client, *SETOR)
    lista = client.get(reverse("interface:formalizacao")).content.decode()
    assert str(novo.id) in lista
    assert str(anterior.id) not in lista


def test_restaurar_revoga_e_avisa_a_designacao_feita_a_mao_mesmo_no_edital_encerrado(cenario):
    """FR-6726, nos dois avessos de uma vez: o Edital **encerrado** não se cancela, mas continua
    designável e na lista do setor; e o cenário que **não** provisiona (o C14) também tem a
    designação da rodada revogada, e dita antes.
    """
    from processo_seletivo.processos.application.finalizacao import close_edital
    from tests.seguranca.apoio import pessoa

    edital = cenario("C14")
    rui = pessoa("rui-treino", nome="Rui Registro", email="rui@ifes.edu.br")
    vincular(rui, "cefor", nomes.PAPEL)
    m = retomar(CenarioDeTreinamento.objects.get(codigo="C14"), autoridade=AUTORIDADE)
    designar(
        m.ator(k.ACESSOS),
        edital_id=edital.id,
        pessoa=rui,
        perfis=[],
        motivo="Exercício.",
        now=m.agora,
    )
    edital.refresh_from_db()
    close_edital(
        actor=m.ator(k.GESTAO, "edital:encerrar"),
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Encerramento (exercício).",
        idempotency_key="exercicio-c14-encerrar",
        correlation_id="exercicio",
    )
    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO

    previa = restaurar("C14", dry_run=True)
    assert "Serão revogadas, com motivo, 1 designação(ões)" in previa, previa
    restaurar("C14", confirmar="C14", autoridade=AUTORIDADE)
    assert not designacoes_vigentes(edital=edital).exists()
    assert not _da_formalizacao().exists(), "o C14 não provisiona"
