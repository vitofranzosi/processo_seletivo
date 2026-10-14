"""A varredura da camada de conteúdo da 070: toda pergunta, todo parâmetro, todo instante.

Os instantes cobrem cada fronteira do corpus — logo depois de cada publicação e de cada vigência —
e três datas do calendário dos Editais, para que a situação de calendário passe pelos três estados.
"""

from datetime import datetime, timedelta

import pytest

from processo_seletivo.duvidas.domain import catalogo
from processo_seletivo.duvidas.domain.respostas import responder
from tests.fixtures.corpus import _atos_do_corpus, contexto_do_corpus
from tests.fixtures.inferencia import contador_falso, porta_falsa, sem_rede  # noqa: F401


@pytest.fixture(autouse=True)
def _nenhum_caso_alcanca_a_rede(sem_rede):  # noqa: F811
    """O piloto (071) fala com serviço externo; nenhum caso deste pacote pode (`FR-1519`)."""


DATAS = ("2026-10-20T12:00:00-03:00", "2026-10-27T12:00:00-03:00", "2026-12-15T12:00:00-03:00")


def instantes(nome):
    fronteiras = {ato.vigente_desde + timedelta(seconds=30) for ato in _atos_do_corpus(nome)}
    return sorted(fronteiras | {datetime.fromisoformat(data) for data in DATAS})


def combinacoes(contexto):
    """`(pergunta, perfil, modalidade)` de toda pergunta oferecida, com todo parâmetro possível."""
    for pergunta in catalogo.oferecidas(contexto.conteudo):
        perfis = (
            [
                codigo
                for codigo, _ in catalogo.opcoes_de_perfil(contexto.conteudo)
                if catalogo.aplicavel_ao_perfil(
                    pergunta.codigo,
                    catalogo.leitura.perfil_por_codigo(contexto.conteudo, codigo),
                    contexto.conteudo,
                )
            ]
            if catalogo.PERFIL in pergunta.parametros
            else [None]
        )
        for perfil in perfis:
            modalidades = [None]
            if catalogo.MODALIDADE in pergunta.parametros:
                encontrado = next(
                    item for item in contexto.conteudo["profiles"] if item["code"] == perfil
                )
                modalidades = [codigo for codigo, _ in catalogo.opcoes_de_modalidade(encontrado)]
            for modalidade in modalidades:
                yield pergunta.codigo, perfil, modalidade


def varrer(nomes=("01", "91", "92")):
    """Toda resposta do corpus: `(nome, instante, contexto, resposta)`."""
    for nome in nomes:
        for instante in instantes(nome):
            contexto = contexto_do_corpus(nome, instante)
            for codigo, perfil, modalidade in combinacoes(contexto):
                yield (
                    nome,
                    instante,
                    contexto,
                    responder(contexto, codigo, perfil=perfil, modalidade=modalidade),
                )


def em(data):
    return datetime.fromisoformat(data)
