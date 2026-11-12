"""Que desfecho cabe agora nesta chamada — a verificação que a tela e o comando leem (152, R-005).

**As frases estão escritas aqui por extenso, e não lidas do módulo.** Elas são as que as guardas de
`desfechar.py` diziam antes de passarem a ler os predicados (FR-5846): se alguém mudar uma, este
arquivo acusa, e a recusa do comando não muda de palavra sem decisão.

Sem banco: os predicados são puros, e a tabela espécie da chamada × prazo × atestado × ocupação ×
pendências cabe inteira em memória.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from processo_seletivo.convocacao.domain import desfechos_cabiveis as cabiveis
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.domain.vocabulario_do_canal import MENSAGEM, PUBLICACAO

AGORA = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
ENVIO = AGORA - timedelta(days=3)
POR_VIR = AGORA + timedelta(days=5)
PASSADO = AGORA - timedelta(days=1)

FRASE_DO_VENCIMENTO_POR_VIR = (
    "O vencimento informado nesta convocação ainda não passou: a pessoa está dentro do prazo dela."
)
FRASE_SEM_ENVIO_NA_MENSAGEM = (
    "A comunicação desta convocação não foi enviada com sucesso: o prazo não começou a correr, e "
    "não há não atendimento a registrar."
)
FRASE_SEM_ENVIO_NA_PUBLICACAO = (
    "A publicação desta convocação ainda não foi registrada: o prazo não começou a correr, e não "
    "há não atendimento a registrar."
)
FRASE_DA_INERCIA_SEM_OCUPACAO = (
    "Esta Inscrição não consta ocupando vaga neste recorte: não há matrícula a cancelar por "
    "inércia. Quem foi chamado e não respondeu tem desfecho próprio — não atendimento à "
    "convocação."
)
FRASE_DA_INERCIA_SEM_ATESTADO = (
    "O cancelamento de matrícula por inércia exige atestado de fato externo: registre quem atestou "
    "e o que concluiu."
)


@dataclass
class Lido:
    nome: str
    sem_condicao_publicada: bool = False


PENDENTES = [Lido("Certidão de nascimento")]

#: O prazo da chamada, nos quatro estados que a tela distingue.
PRAZOS = {
    "sem envio": {"enviado_em": None, "vencimento": POR_VIR},
    "em curso": {"enviado_em": ENVIO, "vencimento": POR_VIR},
    "sem vencimento": {"enviado_em": ENVIO, "vencimento": None},
    "decorrido": {"enviado_em": ENVIO, "vencimento": PASSADO},
}


def _cabiveis(especie_da_chamada, *, prazo="decorrido", ocupando=True, atestado=True, pendentes=()):
    return cabiveis.cabiveis(
        especie_da_chamada=especie_da_chamada,
        agora=AGORA,
        canal=MENSAGEM,
        ocupando=ocupando,
        tem_atestado=atestado,
        pendentes=list(pendentes),
        **PRAZOS[prazo],
    )


class TestAEspecieDaChamada:
    """FR-5837: o que a espécie da chamada nunca admite não aparece em lugar nenhum."""

    @pytest.mark.parametrize("especie", [nomes.VAGA_INICIAL, nomes.SUPLENCIA])
    def test_a_chamada_para_vaga_nunca_oferece_a_regularizacao(self, especie):
        cabem, ainda_nao = _cabiveis(especie)

        assert nomes.REGULARIZACAO not in cabem
        assert nomes.REGULARIZACAO not in {e for e, _ in ainda_nao}
        assert nomes.ACEITE in cabem

    def test_a_chamada_para_regularizar_nunca_oferece_aceite_nem_inercia(self):
        cabem, ainda_nao = _cabiveis(nomes.PARA_REGULARIZAR)

        oferecidas = set(cabem) | {e for e, _ in ainda_nao}
        assert nomes.ACEITE not in oferecidas
        assert nomes.INERCIA not in oferecidas
        assert nomes.REGULARIZACAO in cabem

    def test_a_ordem_e_a_dos_sete(self):
        cabem, _ = _cabiveis(nomes.VAGA_INICIAL)

        assert cabem == [e for e in nomes.ESPECIES_DE_DESFECHO if e in cabem]

    def test_a_recusa_de_compatibilidade_tem_a_frase_do_comando(self):
        achado = cabiveis.desfecho_incompativel(
            especie_da_chamada=nomes.PARA_REGULARIZAR,
            especie=nomes.ACEITE,
            rotulo_da_chamada="Para regularizar o indeferimento",
        )

        assert achado.codigo == nomes.DESFECHO_INCOMPATIVEL_COM_A_CHAMADA
        assert achado.frase == (
            "Uma convocação da espécie para regularizar o indeferimento não admite este desfecho."
        )

    def test_a_especie_admitida_nao_e_recusada(self):
        assert (
            cabiveis.desfecho_incompativel(
                especie_da_chamada=nomes.SUPLENCIA, especie=nomes.ACEITE, rotulo_da_chamada="x"
            )
            is None
        )

    @pytest.mark.parametrize(
        "especie, admite",
        [(nomes.VAGA_INICIAL, True), (nomes.SUPLENCIA, True), (nomes.PARA_REGULARIZAR, False)],
    )
    def test_o_atestado_so_onde_a_inercia_cabe(self, especie, admite):
        """FR-5840: na chamada para regularizar, não há matrícula a cancelar."""
        assert cabiveis.admite_inercia(especie) is admite


class TestONaoAtendimento:
    """FR-269a e FR-269b da `019`: não atender pressupõe ter tido como atender."""

    def test_sem_envio_nao_cabe_e_diz_a_palavra_do_canal(self):
        _, ainda_nao = _cabiveis(nomes.SUPLENCIA, prazo="sem envio")

        achado = dict(ainda_nao)[nomes.NAO_ATENDIMENTO]
        assert achado.codigo == nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO
        assert achado.frase == FRASE_SEM_ENVIO_NA_MENSAGEM
        assert achado.a_partir_de is None

    def test_na_publicacao_a_frase_e_a_da_publicacao(self):
        achado = cabiveis.nao_atendimento_prematuro(
            especie=nomes.NAO_ATENDIMENTO,
            enviado_em=None,
            vencimento=POR_VIR,
            agora=AGORA,
            canal=PUBLICACAO,
        )

        assert achado.frase == FRASE_SEM_ENVIO_NA_PUBLICACAO

    def test_com_o_vencimento_por_vir_diz_a_partir_de_quando(self):
        """FR-5836: quando a razão é o prazo, a nota diz a data a partir da qual cabe."""
        _, ainda_nao = _cabiveis(nomes.SUPLENCIA, prazo="em curso")

        achado = dict(ainda_nao)[nomes.NAO_ATENDIMENTO]
        assert achado.frase == FRASE_DO_VENCIMENTO_POR_VIR
        assert achado.a_partir_de == POR_VIR

    @pytest.mark.parametrize("prazo", ["decorrido", "sem vencimento"])
    def test_depois_do_vencimento_ou_sem_ele_cabe(self, prazo):
        cabem, _ = _cabiveis(nomes.SUPLENCIA, prazo=prazo)

        assert nomes.NAO_ATENDIMENTO in cabem

    def test_outra_especie_nao_le_o_prazo(self):
        assert (
            cabiveis.nao_atendimento_prematuro(
                especie=nomes.ACEITE, enviado_em=None, vencimento=None, agora=AGORA, canal=None
            )
            is None
        )


class TestAInercia:
    """§6 e FR-277 da `019`: só sobre quem ocupava, e só com atestado."""

    def test_sem_ocupacao_diz_a_frase_da_ocupacao_antes_da_do_atestado(self):
        """As duas razões na mesma espécie: vale a que o comando diz primeiro."""
        _, ainda_nao = _cabiveis(nomes.VAGA_INICIAL, ocupando=False, atestado=False)

        achado = dict(ainda_nao)[nomes.INERCIA]
        assert achado.codigo == nomes.INERCIA_SEM_OCUPACAO
        assert achado.frase == FRASE_DA_INERCIA_SEM_OCUPACAO

    def test_ocupando_sem_atestado_diz_a_frase_do_atestado(self):
        _, ainda_nao = _cabiveis(nomes.VAGA_INICIAL, ocupando=True, atestado=False)

        achado = dict(ainda_nao)[nomes.INERCIA]
        assert achado.codigo == nomes.ATESTADO_OBRIGATORIO
        assert achado.frase == FRASE_DA_INERCIA_SEM_ATESTADO

    def test_ocupando_e_com_atestado_cabe(self):
        cabem, _ = _cabiveis(nomes.VAGA_INICIAL, ocupando=True, atestado=True)

        assert nomes.INERCIA in cabem


class TestAInclusao:
    """FR-3592 da `115`: aceite e regularização só com os obrigatórios conferidos."""

    @pytest.mark.parametrize(
        "chamada, especie",
        [(nomes.SUPLENCIA, nomes.ACEITE), (nomes.PARA_REGULARIZAR, nomes.REGULARIZACAO)],
    )
    def test_com_obrigatorio_por_conferir_nao_cabe(self, chamada, especie):
        _, ainda_nao = _cabiveis(chamada, pendentes=PENDENTES)

        achado = dict(ainda_nao)[especie]
        assert achado.codigo == nomes.DOCUMENTOS_NAO_CONFERIDOS
        assert achado.frase == (
            "Para registrar este desfecho, todo documento obrigatório da convocação precisa estar "
            "conferido como conforme, ou como não se aplica quando o Edital publicou a condição. "
            "Falta: Certidão de nascimento."
        )

    def test_o_nao_se_aplica_sem_condicao_publicada_e_dito(self):
        achado = cabiveis.inclusao_por_conferir(
            especie=nomes.ACEITE,
            pendentes=[Lido("Histórico"), Lido("Certificado", sem_condicao_publicada=True)],
        )

        assert achado.frase.endswith(
            'Falta: Histórico, Certificado ("não se aplica" registrado sem condição publicada).'
        )

    def test_os_que_excluem_nao_leem_os_documentos(self):
        """FR-3593 da `115`: o indeferimento, a desistência e os demais cabem com pendência."""
        cabem, _ = _cabiveis(nomes.SUPLENCIA, pendentes=PENDENTES)

        for especie in (
            nomes.INDEFERIMENTO,
            nomes.DESISTENCIA_EXPRESSA,
            nomes.NAO_ATENDIMENTO,
            nomes.INERCIA,
            nomes.RECLASSIFICACAO,
        ):
            assert especie in cabem


@pytest.mark.parametrize("chamada", nomes.ESPECIES_DE_CONVOCACAO)
@pytest.mark.parametrize("prazo", list(PRAZOS))
@pytest.mark.parametrize("ocupando", [True, False])
@pytest.mark.parametrize("atestado", [True, False])
@pytest.mark.parametrize("pendentes", [(), tuple(PENDENTES)])
def test_a_tabela_inteira_reparte_as_admitidas_sem_sobra(
    chamada, prazo, ocupando, atestado, pendentes
):
    """Toda espécie admitida está em uma das duas listas, e só em uma; o indeferimento sempre cabe.

    Cada impedimento é o mesmo que o predicado da guarda diria isolado: a nota não inventa razão.
    """
    cabem, ainda_nao = _cabiveis(
        chamada, prazo=prazo, ocupando=ocupando, atestado=atestado, pendentes=pendentes
    )

    admitidas = set(nomes.DESFECHOS_POR_ESPECIE[chamada])
    impedidas = [especie for especie, _ in ainda_nao]
    assert set(cabem) | set(impedidas) == admitidas
    assert not set(cabem) & set(impedidas)
    assert nomes.INDEFERIMENTO in cabem
    for especie, achado in ainda_nao:
        assert achado == cabiveis.impedimento(
            especie=especie,
            agora=AGORA,
            canal=MENSAGEM,
            ocupando=ocupando,
            tem_atestado=atestado,
            pendentes=list(pendentes),
            **PRAZOS[prazo],
        )


class TestACienciaDoPrazo:
    """R-002: a ciência é pedida onde o não atendimento ainda é recusado."""

    def _exige(self, *, especie=nomes.INDEFERIMENTO, prazo="em curso", pendentes=PENDENTES):
        return cabiveis.exige_ciencia_do_prazo(
            especie=especie, pendentes=list(pendentes), agora=AGORA, **PRAZOS[prazo]
        )

    @pytest.mark.parametrize("prazo", ["em curso", "sem vencimento", "sem envio"])
    def test_com_o_prazo_nao_decorrido_e_pendencia_e_exigida(self, prazo):
        """FR-5803, FR-5804; e a ainda não comunicada, cujo relógio nem começou."""
        assert self._exige(prazo=prazo) is True

    def test_com_o_prazo_decorrido_nao_e_exigida(self):
        assert self._exige(prazo="decorrido") is False

    def test_sem_obrigatorio_por_atender_nao_e_exigida(self):
        assert self._exige(pendentes=()) is False

    @pytest.mark.parametrize(
        "especie", [e for e in nomes.ESPECIES_DE_DESFECHO if e != nomes.INDEFERIMENTO]
    )
    def test_so_o_indeferimento_a_exige(self, especie):
        """FR-5808: nenhum outro desfecho passa a depender do prazo."""
        assert self._exige(especie=especie) is False

    def test_o_mesmo_corte_que_libera_o_nao_atendimento(self):
        """Exigida exatamente onde o não atendimento ainda é recusado, quando há vencimento."""
        for prazo in ("em curso", "decorrido", "sem envio"):
            recusado = (
                cabiveis.nao_atendimento_prematuro(
                    especie=nomes.NAO_ATENDIMENTO, agora=AGORA, canal=MENSAGEM, **PRAZOS[prazo]
                )
                is not None
            )
            assert self._exige(prazo=prazo) is recusado, prazo
