"""Impedimento: bloqueia a atribuição nova, e alcança a que já existe (US5).

O efeito sobre a Avaliação já concluída é o par de FR-075: **preservada e tornada inelegível**.
Preservada porque nada nela é apagado ou alterado; inelegível porque deixa de integrar o conjunto
que a 013 consome — o que libera a vaga que ela ocupava.
"""

import pytest

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.application.impedimento import (
    IMPEDIR,
    TORNAR_INELEGIVEL,
    alcance_do_impedimento,
    registrar_impedimento,
)
from processo_seletivo.avaliacoes.application.selectors import avaliacoes_elegiveis
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.processos.models import AtoAdministrativo
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MOTIVO = "Parentesco de segundo grau com a candidata."


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=8, codigo="81")


@pytest.fixture
def inscricoes(cenario):
    return inscricoes_de(cenario, 2, primeiro=800)


def impedir(gestor, cenario, subject, inscricao, *, chave="imp", motivo=MOTIVO):
    return registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject=subject,
        inscricao_id=inscricao.id,
        motivo=motivo,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_o_impedimento_exige_motivo(gestor, cenario, inscricoes):
    """É o motivo que faz do impedimento um ato, e não uma preferência (FR-039)."""
    with pytest.raises(DomainError) as recusa:
        impedir(gestor, cenario, "joao", inscricoes[0], motivo="   ")

    assert recusa.value.code == "motivo_obrigatorio"


def test_impedimento_bloqueia_a_atribuicao_e_a_recusa_nomeia_o_motivo(gestor, cenario, inscricoes):
    """FR-040: a recusa nomeia o motivo — quem distribui precisa saber por que não pode."""
    impedir(gestor, cenario, "joao", inscricoes[0])

    resultado = distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="depois")

    assert resultado["feitas"] == 1
    assert any("impedimento" in m["motivo"].lower() for m in resultado["motivos"])
    assert not Atribuicao.objects.filter(
        inscricao=inscricoes[0], membro__identity_subject="joao", ativo=True
    ).exists()


def test_impedimento_inativa_a_atribuicao_ativa_no_mesmo_ato(gestor, cenario, inscricoes):
    """FR-041: o acesso é revogado na hora, e não na próxima distribuição."""
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])

    resultado = impedir(gestor, cenario, "joao", inscricoes[0])

    assert resultado["inativadas"] == 1
    assert not Atribuicao.objects.filter(
        inscricao=inscricoes[0], membro__identity_subject="joao", ativo=True
    ).exists()


def test_a_contagem_previa_declara_o_alcance_antes_da_confirmacao(gestor, cenario, inscricoes):
    """Retirar trabalho não pode ser efeito colateral silencioso de registrar um motivo."""
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])
    concluir_como(cenario, "joao", inscricoes[0])

    alcance = alcance_do_impedimento(
        processo=cenario["processo"], identity_subject="joao", inscricao_id=inscricoes[0].id
    )

    assert alcance["atribuicoes"] == 1
    assert alcance["concluidas"] == 1
    # A assinatura acompanha a contagem porque contar não basta: o ato a confere sob trava, contra
    # o conjunto que vai mesmo inativar.
    assert alcance["assinatura"]


def test_a_concluida_e_preservada_e_tornada_inelegivel(gestor, cenario, inscricoes):
    """As duas coisas juntas, e cada uma verificada por si (FR-075, FR-079, FR-091)."""
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])
    avaliacao = concluir_como(cenario, "joao", inscricoes[0], pontuacao="95", parecer="Excelente")

    impedir(gestor, cenario, "joao", inscricoes[0])

    avaliacao.refresh_from_db()
    # Preservada: nada nela foi apagado nem alterado.
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert str(avaliacao.pontuacao) == "95.0000"
    assert avaliacao.parecer == "Excelente"
    # Inelegível: fora do conjunto que a 013 consome.
    elegiveis = avaliacoes_elegiveis(edital=cenario["edital"], etapa_id=cenario["etapa"])
    assert avaliacao not in list(elegiveis)


def test_a_vaga_e_liberada_para_uma_substituta(gestor, cenario, inscricoes):
    """FR-090, EC-020: o registro histórico de uma pessoa não bloqueia a substituta para sempre."""
    distribuir_para(cenario, gestor, ["joao", "ana"], inscricoes[:1])
    concluir_como(cenario, "joao", inscricoes[0])
    impedir(gestor, cenario, "joao", inscricoes[0])
    bruno = _terceiro_avaliador(gestor, cenario)

    resultado = distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[bruno.id],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="substituta",
        correlation_id="teste",
    )

    assert resultado["feitas"] == 1


def _terceiro_avaliador(gestor, cenario):
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import alocar_em, constituir

    bruno = constituir(gestor, cenario["processo"], [("bruno", Funcao.MEMBRO)], prefixo="subst")[
        "bruno"
    ]
    alocar_em(gestor, cenario["processo"], bruno, cenario["edital"], cenario["etapa"])
    return bruno


def test_impedimento_sem_atribuicao_ativa_e_ato_legitimo_e_auditado(gestor, cenario, inscricoes):
    """O caso preventivo — e o agregado é o próprio Impedimento, porque não há outro (T-016)."""
    resultado = impedir(gestor, cenario, "ana", inscricoes[1], chave="preventivo")

    assert resultado["inativadas"] == 0
    ato = AtoAdministrativo.objects.get(operation=IMPEDIR)
    assert ato.aggregate_type == "Impedimento"
    assert str(ato.aggregate_id) == resultado["impedimento"]
    assert ato.reason == MOTIVO


def test_a_inativacao_por_impedimento_grava_ato_com_motivo(gestor, cenario, inscricoes):
    """FR-093: é daqui que a organização do trabalho lê o motivo ao lado da inelegível."""
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])
    concluir_como(cenario, "joao", inscricoes[0])

    impedir(gestor, cenario, "joao", inscricoes[0])

    ato = AtoAdministrativo.objects.get(operation=TORNAR_INELEGIVEL)
    assert ato.aggregate_type == "Atribuicao"
    assert ato.reason == MOTIVO
    assert ato.actor_subject == "carlos"


def test_impedimento_repetido_e_recusado(gestor, cenario, inscricoes):
    impedir(gestor, cenario, "joao", inscricoes[0], chave="a")

    with pytest.raises(DomainError) as recusa:
        impedir(gestor, cenario, "joao", inscricoes[0], chave="b")

    assert recusa.value.code == "impedimento_ja_registrado"
    assert Impedimento.objects.count() == 1


def test_a_mesma_chave_com_outro_motivo_e_conflito(gestor, cenario, inscricoes):
    """O motivo entra no conteúdo da chave (FR-084).

    Fora dele, reenviar a mesma chave com outro motivo seria tratado como repetição — e o ato
    registrado não seria o que se pediu. Num ato cujo motivo é a sua própria justificativa, isso
    seria pior do que não ter idempotência.
    """
    impedir(gestor, cenario, "joao", inscricoes[0], chave="mesma", motivo="Parentesco.")

    with pytest.raises(DomainError) as recusa:
        impedir(gestor, cenario, "joao", inscricoes[0], chave="mesma", motivo="Outro motivo.")

    assert recusa.value.code == "idempotency_conflict"


def test_a_repeticao_devolve_o_desfecho_com_a_contagem(gestor, cenario, inscricoes):
    """FR-084 e FR-097: a tela precisa dizer quantas o ato inativou, e a repetição também."""
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])
    concluir_como(cenario, "joao", inscricoes[0])
    primeiro = impedir(gestor, cenario, "joao", inscricoes[0], chave="repetida")

    repetido = impedir(gestor, cenario, "joao", inscricoes[0], chave="repetida")

    assert primeiro["inativadas"] == 1
    assert primeiro["concluidas_inelegiveis"] == 1
    assert repetido == primeiro


def test_o_ato_recusa_quando_o_alcance_mudou_desde_a_confirmacao(gestor, cenario, inscricoes):
    """FR-041: confirmar um alcance e executar outro é a mesma falha, só mais difícil de ver.

    A confirmação é de dois passos, e entre eles a realidade continua andando: o avaliador conclui
    a avaliação que estava pendente. Quem confirmou "nenhuma concluída" tornaria uma conclusão
    inelegível sem ter sido avisado — o efeito de FR-092 sem o ato que ele exige.
    """
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])
    alcance = alcance_do_impedimento(
        processo=cenario["processo"], identity_subject="joao", inscricao_id=inscricoes[0].id
    )
    assert alcance["concluidas"] == 0

    concluir_como(cenario, "joao", inscricoes[0])  # o mundo andou entre a confirmação e o ato

    with pytest.raises(DomainError) as recusa:
        registrar_impedimento(
            actor=gestor,
            processo_id=cenario["processo"].id,
            identity_subject="joao",
            inscricao_id=inscricoes[0].id,
            motivo=MOTIVO,
            idempotency_key="alcance",
            correlation_id="teste",
            alcance_confirmado=alcance["assinatura"],
        )

    assert recusa.value.code == "alcance_mudou"
    # E nada aconteceu: nem impedimento, nem inativação, nem ato registrado.
    assert not Impedimento.objects.filter(identity_subject="joao").exists()
    assert Atribuicao.objects.filter(inscricao=inscricoes[0], ativo=True).count() == 1
    assert not AtoAdministrativo.objects.filter(operation=IMPEDIR).exists()


def test_o_alcance_reconfirmado_sobre_o_conjunto_atual_e_aceito(gestor, cenario, inscricoes):
    """A recusa acima é para conferir, e não para impedir: reconfirmado, o ato acontece."""
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])
    concluir_como(cenario, "joao", inscricoes[0])
    alcance = alcance_do_impedimento(
        processo=cenario["processo"], identity_subject="joao", inscricao_id=inscricoes[0].id
    )

    resultado = registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=inscricoes[0].id,
        motivo=MOTIVO,
        idempotency_key="alcance-2",
        correlation_id="teste",
        alcance_confirmado=alcance["assinatura"],
    )

    assert resultado["concluidas_inelegiveis"] == 1


def test_a_inscricao_e_encontrada_pelo_protocolo(gestor, cenario, inscricoes):
    """O protocolo é o número que o candidato tem em mãos, e é o que toda tela mostra.

    Exigir o UUID obrigava a presidência a achá-lo em outro lugar e colar — e um erro de digitação
    chegava ao ORM como `ValidationError`, virando 500 onde deveria haver erro de formulário.
    """
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:1])

    alcance = alcance_do_impedimento(
        processo=cenario["processo"],
        identity_subject="joao",
        inscricao_id=inscricoes[0].protocolo,
    )

    assert alcance["atribuicoes"] == 1
    assert alcance["inscricao"] == inscricoes[0].protocolo
    assert alcance["pessoa"] == "joao"

    resultado = registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=inscricoes[0].protocolo,
        motivo=MOTIVO,
        idempotency_key="por-protocolo",
        correlation_id="teste",
        alcance_confirmado=alcance["assinatura"],
    )

    assert resultado["inativadas"] == 1
    assert Impedimento.objects.filter(inscricao=inscricoes[0]).exists()


def test_identificador_desconhecido_e_recusa_de_formulario_nos_dois_passos(gestor, cenario):
    """Errar o que se digita não pode ser erro de servidor (FR-044)."""
    with pytest.raises(DomainError) as na_previa:
        alcance_do_impedimento(
            processo=cenario["processo"], identity_subject="joao", inscricao_id="não-é-uuid"
        )
    assert (na_previa.value.code, na_previa.value.status) == ("inscricao_nao_encontrada", 422)

    with pytest.raises(DomainError) as no_ato:
        registrar_impedimento(
            actor=gestor,
            processo_id=cenario["processo"].id,
            identity_subject="joao",
            inscricao_id="7777",
            motivo=MOTIVO,
            idempotency_key="desconhecido",
            correlation_id="teste",
        )
    assert no_ato.value.code == "inscricao_nao_encontrada"
