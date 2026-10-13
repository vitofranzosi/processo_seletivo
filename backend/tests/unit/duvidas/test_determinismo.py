"""A mesma entrada dá a mesma resposta (070, `FR-1446`, T015).

A ordem dos cartões vem do conteúdo publicado e da tabela da pergunta, nunca da ordem em que o banco
devolve as linhas. Embaralhar as proveniências — que chegam do banco sem ordem garantida — não pode
mudar nada. Os atos chegam ordenados pela aplicação, porque a ordem deles **é** semântica: é a ordem
de aplicação das Retificações (`R-004`).
"""

import random
from dataclasses import replace

from processo_seletivo.duvidas.domain.respostas import responder
from tests.fixtures.corpus import contexto_do_corpus
from tests.unit.duvidas.conftest import combinacoes, instantes


def test_duas_consultas_iguais_dao_a_mesma_resposta_e_a_ordem_do_banco_nao_importa():
    sorteio = random.Random(70)
    comparadas = 0
    for nome in ("01", "91", "92"):
        for instante in instantes(nome):
            contexto = contexto_do_corpus(nome, instante)
            proveniencias = list(contexto.proveniencias)
            sorteio.shuffle(proveniencias)
            embaralhado = replace(
                contexto,
                proveniencias=tuple(proveniencias),
                anexos_publicos=dict(reversed(list(contexto.anexos_publicos.items()))),
            )
            for codigo, perfil, modalidade in combinacoes(contexto):
                primeira = responder(contexto, codigo, perfil=perfil, modalidade=modalidade)
                segunda = responder(contexto, codigo, perfil=perfil, modalidade=modalidade)
                outra_ordem = responder(embaralhado, codigo, perfil=perfil, modalidade=modalidade)
                assert primeira.como_dict() == segunda.como_dict() == outra_ordem.como_dict()
                comparadas += 1
    assert comparadas > 300
