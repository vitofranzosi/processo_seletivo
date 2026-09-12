"""A trilha da ocupação: cada número reconstruível a partir do quadro publicado (016, `FR-259`).

**O que esta feature tem de particular, e que a auditoria precisa alcançar**, é que dois mecanismos
diferentes mudam o número: a **reversão**, que move quantidade e deixa linha própria; e a
**concomitância**, que não move nada e ainda assim muda a ocupação da lista reservada.

O segundo é o que torna a trilha indispensável. Uma reservada que publica 1 e apura 0 ocupada não
tem movimento nenhum a exibir — e sem o registro de *qual apuração leu qual versão do quadro, sobre
qual ordem e qual corte*, ninguém reconstrói por que o número é aquele.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_concomitancia import apurar, emitir_cortes, habilitar

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def com_movimentos(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O certame com os **dois** mecanismos exercitados: reversão e concomitância."""
    return certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="audit-016",
        com_corte=True,
        quantos=4,
        geral=4,
        reversao=nomes.REVERSAO_POR_SALDO,
    )


class TestAReconstrucao:
    """`T056`: quadro → apurações → movimentos devolve o número de hoje."""

    def test_a_sequencia_reconstroi_a_efetiva_vigente(self, com_movimentos, gestor):
        """A conta fecha a partir do publicado, sem abrir o banco por outro caminho."""
        emitir_cortes(com_movimentos, gestor)
        habilitar(com_movimentos, [com_movimentos["cotista_ppi"]])
        apurar(com_movimentos, gestor, chave="audit-016-ampla")
        apurar(com_movimentos, gestor, lista_id=LISTA_PPI, chave="audit-016-ppi")
        depois = apurar(
            com_movimentos, gestor, chave="audit-016-ampla-2", motivo="Reversão recebida"
        )

        vigente = ApuracaoDeOcupacao.objects.get(id=depois["id"])
        recebidas = sum(
            m.quantidade
            for m in MovimentoDeVaga.objects.filter(id__in=vigente.universo["movimentosLidos"])
        )

        assert vigente.publicadas + recebidas == vigente.efetivas
        assert vigente.publicadas == 4 and recebidas == 1 and vigente.efetivas == 5

    def test_cada_apuracao_declara_a_ordem_e_o_corte_que_leu(self, com_movimentos, gestor):
        """Sem isso, o número não tem de onde ser reconstruído — ele só existe."""
        emitir_cortes(com_movimentos, gestor)
        apurar(com_movimentos, gestor, chave="audit-016-ampla")

        vigente = ApuracaoDeOcupacao.objects.get(lista_id=None)

        assert vigente.universo["orderId"] == str(vigente.ato_id)
        assert vigente.universo["cutId"] == str(vigente.corte_id)
        assert vigente.ato_id is not None and vigente.corte_id is not None

    def test_a_apuracao_sucedida_continua_legivel_com_os_seus_numeros(self, com_movimentos, gestor):
        """**Correção é sucessão**, e a anterior guarda o que ela apurou (`FR-262`)."""
        emitir_cortes(com_movimentos, gestor)
        primeira = apurar(com_movimentos, gestor, chave="audit-016-ampla")
        apurar(com_movimentos, gestor, lista_id=LISTA_PPI, chave="audit-016-ppi")
        apurar(com_movimentos, gestor, chave="audit-016-ampla-2", motivo="Reversão recebida")

        anterior = ApuracaoDeOcupacao.objects.get(id=primeira["id"])

        assert anterior.efetivas == 4, "ela apurou antes da reversão, e continua dizendo isso"
        assert anterior.sucessoras.count() == 1


class TestAVersaoDoQuadro:
    """`T057`: fica legível **qual versão do quadro** cada apuração leu."""

    def test_a_apuracao_cita_a_versao_consolidada_e_a_linha(self, com_movimentos, gestor):
        """Sem a linha, retificado o quadro, não se sabe se **esta** apuração ficou para trás.

        A quantidade sozinha não identifica a linha — é a lição que o `Corte` já registra para o
        alvo derivado, e aqui ela decide a causa de obsolescência por Retificação.
        """
        emitir_cortes(com_movimentos, gestor)
        apurar(com_movimentos, gestor, chave="audit-016-ampla")

        vigente = ApuracaoDeOcupacao.objects.get(lista_id=None)

        assert vigente.versao_id is not None
        assert vigente.linha_do_quadro_id is not None
        assert vigente.universo["rowId"] == str(vigente.linha_do_quadro_id)
        assert vigente.universo["immediateVacancies"] == vigente.publicadas

    def test_a_declaracao_de_reversao_vigente_no_instante_fica_congelada(
        self, com_movimentos, gestor
    ):
        """Retificada a declaração depois, a apuração continua dizendo sob qual regra apurou."""
        emitir_cortes(com_movimentos, gestor)
        apurar(com_movimentos, gestor, lista_id=LISTA_PPI, chave="audit-016-ppi")

        da_cota = ApuracaoDeOcupacao.objects.get(lista_id__isnull=False)

        assert da_cota.universo["vacancyReversion"] == nomes.REVERSAO_POR_SALDO


class TestORegistroDeAuditoria:
    """`T059`: ator, ato, motivo e correlação — e as quantidades na razão."""

    def test_a_emissao_grava_o_registro_com_as_quantidades(self, com_movimentos, gestor):
        """**As quantidades entram na razão, e não só no agregado.**

        Ator, ação e instante o registrador genérico já guarda. Recorte, ordem citada e os números
        são desta feature — e sem eles a auditoria não reconstrói o ato sem abrir o banco.
        """
        emitir_cortes(com_movimentos, gestor)
        apurar(com_movimentos, gestor, chave="audit-016-ampla")

        registro = RegistroAuditoria.objects.filter(operation="OCUPACAO_APURAR").latest(
            "occurred_at"
        )

        assert registro.actor_subject == "carlos"
        assert registro.correlation_id == "teste-ocupacao-016"
        assert "4 publicadas" in registro.reason
        assert "4 efetivas" in registro.reason
        assert "a ocupar" in registro.reason
        assert str(MARCO) in registro.reason

    def test_a_reversao_entra_na_razao_do_registro(self, com_movimentos, gestor):
        """Quem lê a trilha vê que aquela emissão cedeu vaga, sem cruzar duas tabelas."""
        emitir_cortes(com_movimentos, gestor)
        apurar(com_movimentos, gestor, lista_id=LISTA_PPI, chave="audit-016-ppi")

        registro = RegistroAuditoria.objects.filter(operation="OCUPACAO_APURAR").latest(
            "occurred_at"
        )

        assert "Reversão:" in registro.reason

    def test_o_motivo_da_sucessao_entra_na_razao(self, com_movimentos, gestor):
        emitir_cortes(com_movimentos, gestor)
        apurar(com_movimentos, gestor, chave="audit-016-ampla")
        apurar(com_movimentos, gestor, chave="audit-016-ampla-2", motivo="Reanálise documental")

        registro = RegistroAuditoria.objects.filter(operation="OCUPACAO_APURAR").latest(
            "occurred_at"
        )

        assert "Motivo da sucessão: Reanálise documental" in registro.reason


class TestAConcomitanciaQueNaoDeixaMovimento:
    """**O caso em que a trilha é a única explicação do número.**

    A reservada publica 1 e apura 0 ocupada, e não há movimento algum a exibir — porque nada se
    moveu. O que explica o número é a apuração da ampla, emitida antes, em que o mesmo cotista
    consta ocupando.
    """

    def test_a_reservada_sem_movimento_tem_a_ocupacao_explicada_pela_ampla(
        self, com_movimentos, gestor
    ):
        emitir_cortes(com_movimentos, gestor)
        habilitar(com_movimentos, [com_movimentos["cotista_ppi"]])
        apurar(com_movimentos, gestor, chave="audit-016-ampla")
        apurar(com_movimentos, gestor, lista_id=LISTA_PPI, chave="audit-016-ppi")

        ampla = selectors.ocupacao_do_recorte(
            edital=com_movimentos["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
        )
        cota = selectors.ocupacao_do_recorte(
            edital=com_movimentos["edital"],
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=LISTA_PPI,
        )

        assert ampla["ocupadas"] == 1, "ele consta ocupando aqui"
        assert cota["ocupadas"] == 0, "e não consta ocupando ali"
        # **A reversão deixou movimento; a concomitância não deixou nenhum** — e é por isso que a
        # trilha da ampla é o que explica o zero da reservada.
        assert [m.especie for m in cota["movimentos"]] == [nomes.MOVIMENTO_REVERSAO]
