"""A grafia dos eventos da formalização que a trilha lê sem importar o app (117, FR-3699).

`auditoria/selectors.py` escreve por extenso as operações que podem ter um documento da inscrição
por agregado, para não carregar `formalizacao` em todo processo que grava um registro. A
concordância precisa de teste: nada no código as liga.
"""

from processo_seletivo.auditoria.selectors import OPERACOES_DO_DOCUMENTO_NA_FORMALIZACAO
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.interface.views import OPERACOES


def test_as_operacoes_do_documento_sao_as_da_feature():
    assert set(OPERACOES_DO_DOCUMENTO_NA_FORMALIZACAO) == {
        nomes.VISUALIZAR,
        nomes.DOWNLOAD,
        nomes.ARQUIVO_INDISPONIVEL,
        "INTEGRIDADE",
    }


def test_toda_operacao_da_feature_tem_rotulo_na_trilha():
    for operacao in nomes.ROTULOS_DA_TRILHA:
        assert OPERACOES.get(operacao, operacao) != operacao, operacao


def test_nenhum_rotulo_afirma_o_que_o_gps_nao_sabe():
    """FR-3699, FR-3701: nada de obtido, encaminhado, recebido ou entregue."""
    vedados = ("obtid", "encaminhad", "recebid", "entregue", "matriculad", "vinculad", "contratad")
    for rotulo in nomes.ROTULOS_DA_TRILHA.values():
        assert not any(palavra in rotulo.lower() for palavra in vedados), rotulo
