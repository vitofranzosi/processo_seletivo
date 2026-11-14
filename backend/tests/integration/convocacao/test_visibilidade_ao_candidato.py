"""A convocação por publicação só existe para o candidato depois do registro (125, US1).

**Na publicação, quem convoca é a publicação.** A comissão pratica a convocação no GPS, publica a
lista no site do certame e só então registra onde publicou. Entre um gesto e outro o portal mostrava
*"Você foi convocado!"* e aceitava documento de quem nenhum ato público chamou. A 1ª decisão do
usuário (06/11/2026) fecha isso em todo o portal — e só na publicação: na mensagem individual, o
estado *"convocado, prazo não iniciado"* da `019` continua visível (FR-3988).

Os cenários: **K-pub** é a convocação por publicação sem registro; **K-msg**, a por mensagem sem
envio bem-sucedido.
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ApresentacaoDeDocumento, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.documentos_da_convocacao import CERTIDAO
from tests.interface.test_portal_convocacao import entrar_como

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

REFERENCIA = "site do certame, 06/11/2026"


@pytest.fixture
def caixa_de_saida(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"


def _certame(fixtures, *, forma, prefixo, documentos=True, **extras):
    gestor, api_client, manager_headers, process_payload = fixtures
    if documentos:
        extras["documentos"] = cenarios.documentos_do_aluno()
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        forma=forma,
        **extras,
    )


@pytest.fixture
def fixtures(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return gestor, api_client, manager_headers, process_payload


def _convocar(certame, gestor, chave):
    return cenarios.convocar_primeira(
        certame, gestor, chave=chave, vencimento=timezone.now() + timedelta(days=5)
    )


def _publicar(edital, gestor, convocacao, chave):
    from processo_seletivo.convocacao.application.comunicar import comunicar

    return comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        idempotency_key=chave,
        correlation_id="teste-125",
        referencia_da_publicacao=REFERENCIA,
    )


def _vigente(pessoa):
    return selectors.vigentes_por_inscricao([pessoa.id]).get(pessoa.id)


# --- O predicado (FR-3981, R-001 a R-003) -------------------------------------------------------


class TestOPredicado:
    def test_publicacao_sem_registro_e_invisivel(self, fixtures, gestor):
        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-a")
        pessoa, convocacao = _convocar(certame, gestor, "v125-a")

        assert not selectors.visivel_ao_candidato(convocacao)
        assert _vigente(pessoa) is None
        # O Requerimento lê a mesma chamada (D-003).
        assert selectors.chamada_em_aberto(pessoa) is None
        # A gestão continua vendo (FR-3989).
        assert Convocacao.objects.filter(inscricao=pessoa).exists()

    def test_publicacao_registrada_e_visivel(self, fixtures, gestor):
        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-b")
        pessoa, convocacao = _convocar(certame, gestor, "v125-b")
        _publicar(certame[0], gestor, convocacao, "v125-b-pub")

        assert _vigente(pessoa) == convocacao
        assert selectors.chamada_em_aberto(pessoa) == convocacao

    def test_mensagem_sem_envio_continua_visivel(self, fixtures, gestor):
        """K-msg: o estado *"convocado, prazo não iniciado"* da `019` não muda (FR-3988)."""
        certame = _certame(fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="v125-c")
        pessoa, convocacao = _convocar(certame, gestor, "v125-c")

        assert selectors.envio_de(convocacao) is None
        assert _vigente(pessoa) == convocacao

    def test_desfecho_antes_da_publicacao_nao_a_torna_visivel(self, fixtures, gestor):
        """D-002: a convocação e o desfecho aparecem juntos, no registro."""
        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-d")
        pessoa, convocacao = _convocar(certame, gestor, "v125-d")
        cenarios.desfechar(
            certame[0], gestor, convocacao, nomes.DESISTENCIA_EXPRESSA, chave="v125-d-desf"
        )

        assert _vigente(pessoa) is None

    def test_a_forma_do_perfil_nao_declarada_e_none(self):
        """Sem forma, a convocação continua como sempre foi: a 1ª decisão alcança a publicação."""
        perfis = [{"id": "p1", "callForm": None}, {"id": "p2", "callForm": "OUTRA"}]

        assert selectors.forma_do_perfil(perfis, "p1") is None
        assert selectors.forma_do_perfil(perfis, "p2") is None
        assert selectors.forma_do_perfil(perfis, "p3") is None


class TestACadeia:
    """D-001: a correção de convocação já publicada continua visível."""

    def test_correcao_de_publicada_continua_visivel(self, fixtures, gestor, caixa_de_saida):
        from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-e")
        pessoa, convocacao = _convocar(certame, gestor, "v125-e")
        _publicar(certame[0], gestor, convocacao, "v125-e-pub")
        corrigir(certame[0], gestor, convocacao, chave="v125-e-corr")

        sucessora = _vigente(pessoa)
        assert sucessora is not None and sucessora.convocacao_anterior_id == convocacao.id
        assert selectors.envio_de(sucessora) is None

    def test_correcao_de_nao_publicada_continua_invisivel(self, fixtures, gestor, caixa_de_saida):
        from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-f")
        pessoa, convocacao = _convocar(certame, gestor, "v125-f")
        corrigir(certame[0], gestor, convocacao, chave="v125-f-corr")

        assert _vigente(pessoa) is None

    def test_tres_elos_com_a_raiz_publicada(self, fixtures, gestor, caixa_de_saida):
        """A cadeia se percorre até a raiz, e não só um elo (R-002)."""
        from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-g")
        pessoa, convocacao = _convocar(certame, gestor, "v125-g")
        _publicar(certame[0], gestor, convocacao, "v125-g-pub")
        corrigir(certame[0], gestor, convocacao, chave="v125-g-c1")
        segunda = _vigente(pessoa)
        corrigir(
            certame[0],
            gestor,
            segunda,
            chave="v125-g-c2",
            vencimento=timezone.now() + timedelta(days=9),
        )

        terceira = _vigente(pessoa)
        assert terceira is not None and terceira.convocacao_anterior_id == segunda.id


# --- As superfícies do portal (FR-3982 a FR-3987, SC-1201 a SC-1203) ----------------------------


class TestAsSuperficiesDoPortal:
    @pytest.fixture
    def kpub(self, fixtures, gestor):
        certame = _certame(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-s")
        pessoa, convocacao = _convocar(certame, gestor, "v125-s")
        return certame, pessoa, convocacao

    def test_a_lista_e_o_acompanhamento_nao_mostram(self, client, kpub):
        _, pessoa, _ = kpub
        entrar_como(client, pessoa)

        lista = client.get(reverse("portal:inscricoes")).content.decode()
        acompanhamento = client.get(reverse("portal:acompanhamento", args=[pessoa.id]))

        assert "Ver convocação" not in lista
        assert 'id="convocacao-da-inscricao"' not in acompanhamento.content.decode()
        assert "Você foi convocado" not in acompanhamento.content.decode()

    def test_a_tela_e_a_de_quem_nao_tem_convocacao_e_nao_registra_leitura(self, client, kpub):
        _, pessoa, _ = kpub
        entrar_como(client, pessoa)
        antes = RegistroAuditoria.objects.filter(operation="CONVOCACAO_LER").count()

        pagina = client.get(reverse("portal:convocacao", args=[pessoa.id])).content.decode()

        assert "não há convocação" in pagina
        assert "Você foi convocado" not in pagina
        assert "não foi chamado" not in pagina
        assert RegistroAuditoria.objects.filter(operation="CONVOCACAO_LER").count() == antes

    def test_outro_inscrito_do_recorte_nao_le_que_o_certame_convocou(self, client, kpub):
        """FR-3984: só a convocação visível conta para *"houve convocação no recorte"*."""
        (_, _, inscricoes), pessoa, _ = kpub
        outra = next(i for i in inscricoes if i.id != pessoa.id)
        entrar_como(client, outra)

        pagina = client.get(reverse("portal:convocacao", args=[outra.id])).content.decode()

        assert "não há convocação" in pagina
        assert "não foi chamado" not in pagina

    def test_o_envio_de_documento_e_recusado_como_inexistente(self, client, kpub):
        """FR-3985: no comando, e com a resposta do item inexistente."""
        _, pessoa, convocacao = kpub
        entrar_como(client, pessoa)
        item = cenarios.item(convocacao, CERTIDAO)

        resposta = client.post(
            reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, item.id]),
            {"arquivo": cenarios.pdf()},
        )

        assert resposta.status_code == 404
        assert not ApresentacaoDeDocumento.objects.filter(item=item).exists()

    def test_o_comando_recusa_o_envio_sem_a_tela(self, kpub):
        from processo_seletivo.shared.api.problems import DomainError

        _, pessoa, convocacao = kpub
        with pytest.raises(DomainError) as recusa:
            cenarios.apresentar(pessoa, convocacao, CERTIDAO)

        assert recusa.value.status == 404 and recusa.value.code == "not_found"

    def test_o_arquivo_apresentado_antes_da_regra_tambem_some(self, client, kpub):
        """Caso-limite: o arquivo de antes da implantação não se apaga, e não aparece."""
        _, pessoa, convocacao = kpub
        with mock.patch(
            "processo_seletivo.convocacao.application.selectors.visivel_ao_candidato",
            return_value=True,
        ):
            feita = cenarios.apresentar(pessoa, convocacao, CERTIDAO)
        entrar_como(client, pessoa)

        resposta = client.get(
            reverse("portal:documento-da-convocacao", args=[pessoa.id, feita.apresentacao.id])
        )

        assert resposta.status_code == 404
        assert ApresentacaoDeDocumento.objects.filter(id=feita.apresentacao.id).exists()

    def test_depois_do_registro_todas_mostram(self, client, kpub, gestor):
        """FR-3987, SC-1202: na leitura seguinte, sem outro gesto."""
        (edital, _, _), pessoa, convocacao = kpub
        _publicar(edital, gestor, convocacao, "v125-s-pub")
        entrar_como(client, pessoa)

        lista = client.get(reverse("portal:inscricoes")).content.decode()
        acompanhamento = client.get(
            reverse("portal:acompanhamento", args=[pessoa.id])
        ).content.decode()
        tela = client.get(reverse("portal:convocacao", args=[pessoa.id])).content.decode()

        assert "Ver convocação" in lista
        assert 'id="convocacao-da-inscricao"' in acompanhamento
        assert "Você tem uma convocação!" in tela
        # A palavra do canal (FR-3998): a referência, e não *"Comunicação enviada em"*.
        assert f"Publicada em</dt><dd>{REFERENCIA}" in tela
        assert "Comunicação enviada em" not in tela
        assert "contado do envio da comunicação" not in tela


class TestORequerimentoDaChamada:
    """D-003: o Requerimento *na convocação* segue a convocação."""

    def test_k_pub_nao_abre_o_requerimento(self, fixtures, gestor):
        from processo_seletivo.requerimentos.application import preencher
        from tests.fixtures.jornada_do_convocado import publicar_com_requerimento

        certame = _certame(
            fixtures,
            forma=FORMA_POR_PUBLICACAO,
            prefixo="v125-r",
            documentos=False,
            publicar=publicar_com_requerimento,
        )
        pessoa, convocacao = _convocar(certame, gestor, "v125-r")

        assert not preencher.apurar(pessoa).disponivel

        _publicar(certame[0], gestor, convocacao, "v125-r-pub")
        assert preencher.apurar(pessoa).disponivel


# --- O custo (FR-3990, SC-1204) -----------------------------------------------------------------


class TestOCusto:
    def test_o_custo_nao_cresce_com_as_convocacoes_pendentes(self, fixtures, gestor):
        """Por conjunto: uma pendente ou duas, o mesmo número de consultas (R-002)."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        from tests.fixtures.convocacao import convocar

        certame = _certame(
            fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="v125-custo", documentos=False, geral=2
        )
        edital, _, inscricoes = certame
        fila = selectors.contexto_do_recorte(
            edital=edital,
            perfil_id=certame[2][0].profile_id,
            marco_id=_marco(),
            lista_id=None,
        )["fila"]
        convocar(edital, gestor, fila[0], idempotency_key="v125-custo-1")
        ids = [i.id for i in inscricoes]

        with CaptureQueriesContext(connection) as uma:
            assert selectors.vigentes_por_inscricao(ids) == {}
        convocar(edital, gestor, fila[1], idempotency_key="v125-custo-2")
        with CaptureQueriesContext(connection) as duas:
            assert selectors.vigentes_por_inscricao(ids) == {}

        assert len(duas) == len(uma)


def _marco():
    from tests.fixtures.corte import MARCO

    return MARCO
