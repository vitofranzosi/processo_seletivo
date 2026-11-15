"""O degrau do passo da Etapa restrita, sem banco (171, FR-7303, FR-7304, FR-7306, FR-7309).

A função é pura: os passos chegam prontos (`portal/passo_da_etapa.py`), e aqui se prova o texto, a
precedência e o que cada rótulo afirma — e o que não afirma.
"""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
from processo_seletivo.portal import situacao
from processo_seletivo.portal.passo_da_etapa import (
    AGUARDA_COMISSAO,
    AGUARDA_RESULTADO,
    FALTA,
    Passo,
)
from processo_seletivo.resultados.domain import efeito
from tests.unit.portal.test_situacao_da_inscricao import (
    PERFIL,
    calcular,
    cartao,
    convocacao,
    eliminada,
    textos,
)

INICIO = datetime(2026, 12, 1, 12, 0, tzinfo=UTC)
FIM = datetime(2026, 12, 5, 23, 0, tzinfo=UTC)
ETAPA = "Verificação da autodeclaração"
MODALIDADE = "Pretos e pardos de escola pública"
TERMOS = ("heteroidentifica", "fenótip", "fenotíp", "aferição", "indeferid")


def passo(estado=FALTA, *, inicio=INICIO, fim=FIM, comecou=False, efeito_=None, etapa=ETAPA):
    return Passo(
        etapa_id=str(uuid.uuid4()),
        etapa=etapa,
        modalidade=MODALIDADE,
        estado=estado,
        inicio=inicio,
        fim=fim,
        efeito_da_ausencia=efeito_ or efeito.RETIRA_DA_RESERVA,
        comecou=comecou,
    )


def com_passos(*passos, **outros):
    inscricao = SimpleNamespace(
        id=uuid.uuid4(), edital_id=uuid.uuid4(), submitted_at=datetime(2026, 9, 1, tzinfo=UTC)
    )
    return calcular(inscricao=inscricao, perfil=PERFIL, passos=passos, **outros)


def tudo(resultado):
    acao = resultado.o_que_fazer
    return " ".join(
        [resultado.rotulo, textos(resultado), acao.principal, acao.consequencia, acao.secundaria]
    )


class TestFaltaUmPasso:
    def test_antes_do_periodo(self):
        resultado = com_passos(passo())
        assert resultado.codigo == situacao.PASSO_PENDENTE
        assert resultado.rotulo == "Falta um passo seu"
        assert resultado.provisoria
        assert textos(resultado) == (
            f"Você se inscreveu em {MODALIDADE}, e quem se inscreve nela passa também por esta "
            f"etapa: {ETAPA}."
        )
        assert resultado.o_que_fazer.principal == (
            "Acontece de 01/12/2026 a 05/12/2026. "
            "A comissão vai informar o dia, a hora e como participar."
        )

    def test_no_periodo(self):
        resultado = com_passos(passo(comecou=True))
        assert resultado.o_que_fazer.principal.startswith("Está acontecendo até 05/12/2026.")

    def test_sem_periodo_nao_inventa_data(self):
        """FR-7305."""
        resultado = com_passos(passo(inicio=None, fim=None, comecou=True))
        assert resultado.o_que_fazer.principal == situacao.COMISSAO_INFORMA_QUANDO

    @pytest.mark.parametrize(
        ("efeito_", "frase"),
        [
            (efeito.RETIRA_DA_RESERVA, "continua concorrendo pela ampla concorrência"),
            (efeito.ELIMINA, "é eliminado desta seleção"),
        ],
    )
    def test_a_consequencia_vem_do_efeito_da_ausencia(self, efeito_, frase):
        """FR-7304, UX-794: no mesmo cartão, e pelo efeito que o Edital declara (`164`)."""
        resultado = com_passos(passo(efeito_=efeito_))
        assert frase in resultado.o_que_fazer.consequencia
        assert "perde" not in resultado.o_que_fazer.consequencia

    def test_o_link_vai_ao_edital_vigente_e_nomeia_a_etapa(self):
        """FR-7304, ajuste 1 do usuário: nenhuma seção pressuposta."""
        resultado = com_passos(passo())
        acao = resultado.o_que_fazer
        assert acao.secundaria == f"No Edital, veja a etapa {ETAPA}."
        assert acao.secundaria_rotulo == "Ver o Edital vigente"
        assert "/selecoes/" in acao.secundaria_link
        assert "#" not in acao.secundaria_link

    def test_a_pericia_e_o_mesmo_passo_pelo_nome_publicado(self):
        """D-001: o texto fixo não nomeia o procedimento."""
        resultado = com_passos(passo(etapa="Perícia médica"))
        assert "Perícia médica" in textos(resultado)
        assert "autodeclaração" not in tudo(resultado)


class TestDepoisDoPeriodo:
    def test_sem_registro_aguarda_a_comissao_e_nao_diz_analise(self):
        """FR-7306, ajuste 2 do usuário: prazo encerrado não é análise iniciada."""
        resultado = com_passos(passo(AGUARDA_COMISSAO, comecou=True))
        assert resultado.codigo == situacao.PASSO_AGUARDA_COMISSAO
        assert resultado.rotulo == "Aguardando a comissão"
        assert "terminou em 05/12/2026" in resultado.o_que_fazer.principal
        assert "analis" not in tudo(resultado).lower()
        assert resultado.o_que_fazer.consequencia == ""

    def test_com_registro_aguarda_o_resultado_sem_sentido_nem_data(self):
        resultado = com_passos(passo(AGUARDA_RESULTADO, comecou=True))
        assert resultado.codigo == situacao.PASSO_AGUARDA_RESULTADO
        assert resultado.rotulo == "Aguardando o resultado"
        assert resultado.o_que_fazer.principal == situacao.RESULTADO_APARECE_AQUI
        for palavra in ("confirm", "favor", "deferid", "parecer"):
            assert palavra not in tudo(resultado).lower()


class TestPrecedencia:
    def test_a_eliminacao_vence_o_passo(self):
        resultado = com_passos(passo(), resultados_das_etapas=[eliminada()])
        assert resultado.codigo == situacao.ELIMINADO

    def test_o_passo_vence_a_classificacao(self):
        resultado = com_passos(passo(), cartoes=[cartao()])
        assert resultado.codigo == situacao.PASSO_PENDENTE

    def test_o_passo_vence_a_inscricao_enviada(self):
        assert com_passos(passo()).codigo == situacao.PASSO_PENDENTE

    def test_na_convocacao_o_passo_e_linha(self):
        """FR-7303, D-003."""
        resultado = com_passos(
            passo(),
            convocacao=convocacao(),
            estado=convocacao_nomes.CONVOCADO_PRAZO_EM_CURSO,
        )
        assert resultado.codigo == situacao.CONVOCADO
        assert f"Também falta um passo seu: {ETAPA}, de 01/12/2026 a 05/12/2026." in textos(
            resultado
        )

    def test_o_segundo_passo_e_linha_do_primeiro(self):
        """FR-7309."""
        resultado = com_passos(passo(), passo(etapa="Perícia médica", inicio=None, fim=None))
        assert ETAPA in textos(resultado)
        assert "Também falta um passo seu: Perícia médica." in textos(resultado)

    def test_sem_passo_nada_muda(self):
        assert com_passos().codigo == situacao.INSCRICAO_ENVIADA


@pytest.mark.parametrize("estado", [FALTA, AGUARDA_COMISSAO, AGUARDA_RESULTADO])
def test_nenhum_termo_tecnico_no_texto_fixo(estado):
    """FR-7330: o nome publicado é neutro aqui, e o resto é texto fixo."""
    texto = tudo(com_passos(passo(estado))).lower()
    assert not [termo for termo in TERMOS if termo in texto]


def test_nenhuma_frase_do_passo_diz_video_sem_o_video():
    """FR-7313: sem a `Situacao` da `166`, nenhuma palavra sobre vídeo."""
    for estado in (FALTA, AGUARDA_COMISSAO, AGUARDA_RESULTADO):
        assert "vídeo" not in tudo(com_passos(passo(estado))).lower()
