"""O reuso copia só o texto que alguém escreveu (054, FR-983; code review do PR 233).

Dois defeitos que a retirada da redação padrão abria no reuso de um Edital publicado: a redação
padrão que o acervo anterior à `054` publicou voltaria como texto do autor, sem o aviso que a
acusava; e a seção vazia viraria linha vazia, marcando a etapa Conteúdo como concluída.
"""

import pytest

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.reaproveitamento import payload_do_conteudo

PADRAO_DA_CLASSIFICACAO = (
    "A classificação observará a pontuação obtida nas Etapas de Avaliação, respeitados os pesos "
    "e as notas mínimas declarados neste Edital e as reservas de vaga previstas."
)


def _conteudo(**textos):
    return {
        "sections": [
            {
                "key": secao.key,
                "type": secao.type,
                **({} if secao.gerada else {"content": textos.get(secao.key, "")}),
            }
            for secao in secoes.CATALOGO
        ]
    }


def _copiadas(conteudo):
    return {item["key"]: item["content"] for item in payload_do_conteudo(conteudo)["sections"]}


def test_a_secao_vazia_nao_vira_linha():
    assert _copiadas(_conteudo()) == {}


def test_o_texto_escrito_e_copiado_sem_espaco_nas_bordas():
    copiadas = _copiadas(_conteudo(**{"publico-alvo": "  Graduados.  "}))
    assert copiadas == {"publico-alvo": "Graduados."}


@pytest.mark.parametrize("padrao", sorted(secoes.REDACOES_PADRAO_RETIRADAS))
def test_a_redacao_padrao_do_acervo_nao_e_copiada(padrao):
    assert _copiadas(_conteudo(classificacao=padrao)) == {}


def test_o_texto_que_so_comeca_pela_redacao_padrao_e_do_autor():
    """Só o texto **igual** ao padrão é o intocado: o que o autor acrescentou é dele."""
    texto = PADRAO_DA_CLASSIFICACAO + " O sorteio é eletrônico."
    assert _copiadas(_conteudo(classificacao=texto)) == {"classificacao": texto}
