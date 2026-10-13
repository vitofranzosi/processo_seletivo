"""O texto do Edital sai como está (070, `SC-534`, `FR-1433`, `FR-1434`, `R-010`).

A varredura passa por toda resposta do corpus, e cada cartão "Texto do Edital" é comparado ao valor
publicado no caminho dele. Uma frase escrita pelo sistema rotulada como texto do Edital — a do
compositor do documento, ou qualquer outra — não está no conteúdo publicado, e reprova aqui.
"""

import re

from processo_seletivo.duvidas.domain.estruturas import TEXTO
from processo_seletivo.duvidas.domain.respostas import no_item
from processo_seletivo.publicacoes.domain.changes import resolve_path
from tests.unit.duvidas.conftest import varrer


def test_todo_texto_do_edital_e_identico_ao_publicado():
    conferidos, divergentes = 0, []
    for nome, instante, contexto, resposta in varrer():
        for referencia in resposta.referencias:
            if referencia.natureza != TEXTO:
                continue
            publicado = no_item(
                resolve_path(contexto.conteudo, referencia.caminho), referencia.posicao
            )
            conferidos += 1
            if publicado != referencia.conteudo:
                divergentes.append((nome, instante, resposta.pergunta, referencia.caminho))
    assert conferidos > 500, "a varredura precisa alcançar os textos do corpus"
    assert divergentes == []


#: A numeração impressa: "11.1", "5.2.3", "item 4". O nome entre aspas é do Edital, e fica de fora.
NUMERACAO = re.compile(r"\b\d+(?:\.\d+)+\b|\bitem\s+\d", re.IGNORECASE)


def test_nenhuma_localizacao_usa_numero_impresso():
    """`CA-16`: a seção é dita pelo título; "11.1" não serve depois de uma Retificação.

    A versão anterior deste teste olhava os três primeiros caracteres, e toda localização começa
    por palavra ("Seção", "Perfil", "Cronograma"): não reprovava nada (revisão de 12/10).
    """
    secoes = 0
    for _nome, _instante, _contexto, resposta in varrer(("92",)):
        for referencia in resposta.referencias:
            fora_das_aspas = re.sub(r"“[^”]*”", "", referencia.localizacao)
            assert not NUMERACAO.search(fora_das_aspas), referencia.localizacao
            secoes += referencia.localizacao.startswith("Seção “")
    assert secoes > 0, "a varredura precisa alcançar as seções"
