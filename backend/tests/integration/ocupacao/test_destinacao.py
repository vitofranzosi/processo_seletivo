"""O ato "Destinar à ampla concorrência", por esgotamento (155, T023, US1, contrato).

O cenário é a V-1 da verificação: um único cotista PPI, habilitado e titular, desiste; a reserva
fica sem quem a ocupe. Os fatos externos — o resultado definitivo, o prazo, os recursos, as
chamadas — chegam por um *callable* fixo, porque é o que o ato recebe: a composição deles pela
interface tem os seus casos em `test_condicao_do_esgotamento.py`, sobre a publicação de verdade.
"""

import threading

import pytest
from django.db import connection
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.destinacao import (
    destinar_vaga,
    frase_publicada,
    leitura_da_vaga,
    previa_da_destinacao,
)
from processo_seletivo.ocupacao.domain import destinacao, nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_concomitancia import apurar, emitir_cortes, habilitar
from tests.integration.ocupacao.test_condicao_do_esgotamento import efeito, sem_concomitancia

pytestmark = pytest.mark.django_db(transaction=True)


def definitivo(**fatos):
    """Os fatos externos de um marco com o resultado definitivo e nada pendente."""

    def fatos_externos(**_):
        return {"natureza_do_resultado": "DEFINITIVA", **fatos}

    return fatos_externos


DEFINITIVO = definitivo()


def esgotado(gestor, api_client, manager_headers, process_payload, prefixo, *, reversao):
    """A V-1: o único cotista desiste, e a apuração seguinte dá 1 a ocupar e ninguém mais."""
    certame = certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        com_corte=True,
        quantos=8,
        geral=1,
        reversao=reversao,
    )
    cotista = certame["cotista_ppi"]
    emitir_cortes(certame, gestor)
    habilitar(certame, [cotista])
    apurar(certame, gestor, chave=f"{prefixo}-ampla")
    sem_concomitancia(certame, cotista)
    apurar(certame, gestor, chave=f"{prefixo}-ampla-2", motivo="Saída da ampla registrada")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave=f"{prefixo}-ppi")
    efeito(certame, cotista, nomes.EFEITO_EXCLUSAO)
    apurar(certame, gestor, lista_id=LISTA_PPI, chave=f"{prefixo}-ppi-2", motivo="Desistência")
    return certame


@pytest.fixture
def certame(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return esgotado(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "dest-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )


def previa(certame, fatos_externos=DEFINITIVO):
    return previa_da_destinacao(
        edital=certame["edital"],
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=LISTA_PPI,
        fatos_externos=fatos_externos,
    )


def destinar(certame, gestor, *, chave="dest-155-ato", assinatura=None, fatos=DEFINITIVO):
    return destinar_vaga(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=LISTA_PPI,
        assinatura=assinatura if assinatura is not None else previa(certame, fatos)["assinatura"],
        fatos_externos=fatos,
        idempotency_key=chave,
        correlation_id="teste-155",
    )


def recusa(certame, gestor, **kwargs):
    with pytest.raises(DomainError) as erro:
        destinar(certame, gestor, **kwargs)
    return erro.value


class TestOAto:
    def test_grava_o_movimento_com_o_recorte_o_gatilho_e_o_fundamento(self, certame, gestor):
        """FR-6310: ator, instante, origem, destino, quantidade, gatilho, declaração e versão."""
        conferencia = previa(certame)
        assert conferencia["recusa"] is None
        lida = conferencia["apuracao"]

        declarado = destinar(certame, gestor)

        movimento = MovimentoDeVaga.objects.get()
        assert declarado["quantidade"] == movimento.quantidade == 1
        assert (str(movimento.origem_lista_id), movimento.destino_lista_id) == (LISTA_PPI, None)
        assert movimento.edital_id == certame["edital"].id
        assert (str(movimento.perfil_id), str(movimento.marco_id)) == (PROFILE_ID, MARCO)
        assert movimento.gatilho == nomes.REVERSAO_POR_ESGOTAMENTO
        assert movimento.apuracao_id == lida.id, "a apuração lida pelo ato (R-001)"
        assert movimento.versao_id == conferencia["versao"].id
        assert conferencia["frase"] and conferencia["frase"] in movimento.fundamento
        assert movimento.registrado_por == gestor.subject

    def test_a_sucessora_da_origem_le_o_movimento_e_nasce_vigente(self, certame, gestor):
        declarado = destinar(certame, gestor)

        seguinte = declarado["apuracaoSeguinte"]
        assert seguinte is not None, declarado["apuracaoPendente"]
        assert (seguinte["efetivas"], seguinte["faltando"]) == (0, 0)
        movimento = MovimentoDeVaga.objects.get()
        assert str(movimento.id) in seguinte["universo"]["movimentosLidos"]
        leitura = selectors.ocupacao_do_recorte(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=LISTA_PPI
        )
        assert leitura["estado"] == nomes.VIGENTE

    def test_a_ampla_fica_obsoleta_pelo_movimento(self, certame, gestor):
        """FR-6313: a ampla é emitida por quem conduz, porque é ela que muda quem é chamado."""
        destinar(certame, gestor)

        ampla = selectors.ocupacao_do_recorte(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
        )
        assert ampla["estado"] == nomes.OBSOLETO
        assert nomes.CAUSA_MOVIMENTO_POSTERIOR in ampla["causasDeObsolescencia"]

    def test_a_soma_das_efetivas_do_perfil_nao_muda(self, certame, gestor):
        """FR-6311: a vaga muda de lista, e a quantidade publicada não muda."""

        def soma():
            return sum(
                selectors.apuracao_vigente(
                    edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista
                ).efetivas
                for lista in (None, LISTA_PPI)
            )

        antes = soma()
        destinar(certame, gestor)
        apurar(certame, gestor, chave="dest-155-ampla-3", motivo="Destinação recebida")

        assert soma() == antes
        ampla = selectors.apuracao_vigente(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
        )
        assert (ampla.publicadas, ampla.efetivas) == (1, 2)

    def test_a_trilha_registra_o_ato_com_a_correlacao(self, certame, gestor):
        from processo_seletivo.auditoria.models import RegistroAuditoria

        destinar(certame, gestor)

        registro = RegistroAuditoria.objects.get(operation="OCUPACAO_DESTINAR_VAGA")
        assert registro.correlation_id == "teste-155"
        assert "por esgotamento" in registro.reason


class TestUmRegistroSo:
    def test_a_confirmacao_repetida_devolve_o_mesmo_desfecho(self, certame, gestor):
        """FR-6314, pela chave: a repetição devolve o que o ato respondeu."""
        assinatura = previa(certame)["assinatura"]
        primeira = destinar(certame, gestor, assinatura=assinatura)
        segunda = destinar(certame, gestor, assinatura=assinatura)

        assert segunda == primeira
        assert MovimentoDeVaga.objects.count() == 1

    def test_outra_confirmacao_da_mesma_conferencia_e_recusada(self, certame, gestor):
        """A segunda chave lê, sob a trava, a vaga já destinada."""
        assinatura = previa(certame)["assinatura"]
        destinar(certame, gestor, assinatura=assinatura)

        erro = recusa(certame, gestor, chave="dest-155-ato-2", assinatura=assinatura)

        assert erro.code == nomes.SEM_SALDO_A_DESTINAR
        assert MovimentoDeVaga.objects.count() == 1

    @pytest.mark.skipif(
        connection.vendor != "postgresql", reason="a trava do Processo é do PostgreSQL"
    )
    def test_duas_confirmacoes_simultaneas_dao_um_registro(self, certame, gestor):
        assinatura = previa(certame)["assinatura"]
        desfechos = []
        largada = threading.Barrier(2)

        def confirmar(chave):
            try:
                largada.wait()
                destinar(certame, gestor, chave=chave, assinatura=assinatura)
                desfechos.append("ok")
            except DomainError as erro:
                desfechos.append(erro.code)
            finally:
                connection.close()

        linhas = [threading.Thread(target=confirmar, args=(f"simultanea-{n}",)) for n in (1, 2)]
        for linha in linhas:
            linha.start()
        for linha in linhas:
            linha.join()

        assert sorted(desfechos) == sorted(["ok", nomes.SEM_SALDO_A_DESTINAR])
        assert MovimentoDeVaga.objects.count() == 1


class TestRecusas:
    def test_ainda_ha_quem_ocupar(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        certame = certame_sorteado_com_quadro(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            prefixo="quem-155",
            com_corte=True,
            quantos=8,
            geral=1,
            reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
        )
        emitir_cortes(certame, gestor)
        apurar(certame, gestor, chave="quem-155-ampla")
        sem_concomitancia(certame, certame["cotista_ppi"])
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="quem-155-ppi")

        erro = recusa(certame, gestor)

        assert erro.code == nomes.AINDA_HA_QUEM_OCUPAR
        assert "1 pessoa" in erro.detail

    def test_impedida_pelo_resultado_provisorio(self, certame, gestor):
        erro = recusa(
            certame,
            gestor,
            fatos=definitivo(natureza_do_resultado="PRELIMINAR"),
        )
        assert erro.code == nomes.DESTINACAO_IMPEDIDA
        assert "não é definitivo" in erro.detail

    def test_o_fato_externo_e_relido_sob_a_trava(self, certame, gestor):
        """A conferência leu nada pendente; no clique, há recurso — o ato recusa."""
        assinatura = previa(certame)["assinatura"]

        erro = recusa(
            certame, gestor, assinatura=assinatura, fatos=definitivo(recursos_pendentes=1)
        )

        assert erro.code == nomes.DESTINACAO_IMPEDIDA
        assert MovimentoDeVaga.objects.count() == 0

    def test_leitura_mudada(self, certame, gestor):
        erro = recusa(certame, gestor, assinatura="outra")
        assert erro.code == nomes.LEITURA_DO_RECORTE_MUDOU

    @pytest.mark.parametrize(
        ("reversao", "codigo"),
        [
            (None, nomes.SEM_REVERSAO_DECLARADA),
            (nomes.PASSAGEM_ENTRE_COTAS, nomes.RECUSA_PASSAGEM_ENTRE_COTAS),
        ],
        ids=["sem-reversao", "passagem-entre-cotas"],
    )
    def test_sem_reversao_e_passagem(
        self,
        db,
        gestor,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
        reversao,
        codigo,
    ):
        certame = esgotado(
            gestor, api_client, manager_headers, process_payload, f"rec-{codigo}", reversao=reversao
        )
        assert recusa(certame, gestor).code == codigo
        assert MovimentoDeVaga.objects.count() == 0

    def test_por_saldo_aguarda_e_a_tela_nao_oferece(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        """R-010: por saldo, o ato novo não se aplica; a emissão continua cedendo como antes."""
        certame = esgotado(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            "saldo-155",
            reversao=nomes.REVERSAO_POR_SALDO,
        )
        cedidos = MovimentoDeVaga.objects.count()

        assert recusa(certame, gestor).code == nomes.REVERSAO_POR_SALDO_AGUARDA_DECISAO
        assert MovimentoDeVaga.objects.count() == cedidos
        assert cedidos == 1, "a emissão por saldo cedeu, como antes da 155"
        # A vaga já saiu pela emissão; com saldo ainda a ocupar, o estado seria o da espera.
        situacao = previa(certame)["situacao"]
        assert (situacao["estado"], situacao["destinadas"]) == (destinacao.SEM_VAGA_A_DESTINAR, 1)
        assert destinacao.situacao(
            declaracao=nomes.REVERSAO_POR_SALDO, lista_id=LISTA_PPI, saldo=1
        )["estado"] == (destinacao.AGUARDA_D015)


class TestMovimentoAntigo:
    def test_o_movimento_da_apuracao_conta_como_destinacao_feita(self, certame, gestor):
        """FR-6316 e US1.5: a vaga que a apuração cedeu antes da 155 não se destina de novo."""
        vigente = selectors.apuracao_vigente(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=LISTA_PPI
        )
        # O movimento como a emissão o gravava: só a apuração, sem recorte nem fundamento.
        MovimentoDeVaga.objects.create(
            apuracao=vigente,
            especie=nomes.MOVIMENTO_REVERSAO,
            origem_lista_id=LISTA_PPI,
            destino_lista_id=None,
            quantidade=1,
            causa="Lista reservada esgotada com saldo: 1 de 1.",
            registrado_por="teste",
            registrado_em=timezone.now(),
        )
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="antigo-ppi", motivo="Movimento lido")

        leitura = previa(certame)

        assert leitura["situacao"]["destinadas"] == 1
        assert leitura["situacao"]["estado"] == destinacao.SEM_VAGA_A_DESTINAR
        assert recusa(certame, gestor).code == nomes.SEM_SALDO_A_DESTINAR
        assert MovimentoDeVaga.objects.count() == 1


class TestReproducao:
    def test_relido_depois_da_retificacao_o_ato_diz_o_que_leu(self, certame, gestor, api_client):
        """FR-6342: a Retificação troca a declaração; o ato continua com a dele."""
        from tests.fixtures.publicacao import retify

        destinar(certame, gestor)
        movimento = MovimentoDeVaga.objects.get()
        lida = movimento.versao

        retify(
            api_client,
            certame["edital"],
            [
                {
                    "targetPath": f"/profiles/id={PROFILE_ID}/vacancyReversion/kind",
                    "operation": "REPLACE",
                    "newValue": nomes.REVERSAO_POR_SALDO,
                }
            ],
            suffix="r155",
        )

        relido = MovimentoDeVaga.objects.get(pk=movimento.pk)
        hoje = leitura_da_vaga(
            edital=certame["edital"],
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=LISTA_PPI,
            fatos_externos=DEFINITIVO,
        )
        assert hoje["declaracao"] == nomes.REVERSAO_POR_SALDO, "a declaração de hoje mudou"
        assert hoje["versao"].id != lida.id
        assert (relido.gatilho, relido.quantidade, relido.versao_id) == (
            nomes.REVERSAO_POR_ESGOTAMENTO,
            1,
            lida.id,
        )
        assert frase_publicada(relido.versao, relido.gatilho) in relido.fundamento
        assert relido.apuracao_id == ApuracaoDeOcupacao.objects.get(pk=relido.apuracao_id).id
