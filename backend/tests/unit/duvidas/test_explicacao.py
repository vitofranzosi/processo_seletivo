"""A explicação só diz o que os cartões mostram, e nunca avalia a pessoa (070, `FR-1425`, T014).

**Os números e as datas.** Todo número e toda data da explicação estão em algum cartão ou aviso da
mesma resposta. A única exceção é o canal institucional da `P-11`, que é configuração da implantação
e por isso não tem cartão (`FR-1441`) — o corpus o deixa vazio, e o caso não aparece aqui.
"""

import re

from tests.unit.duvidas.conftest import varrer

NUMERO = re.compile(r"\d+(?:[.,/]\d+)*")

PROIBIDAS = ("você pode", "voce pode", "será aceito", "sera aceito", "edital completo")
# "não classifica" é a negativa que a `P-09` fazia sobre Perfil sem marco nenhum (revisão de 12/10).
NEGATIVAS = ("não cabe", "não há", "não é permitido", "não classifica")


def _textos_de_apoio(resposta):
    partes = [referencia.conteudo for referencia in resposta.referencias]
    partes += [referencia.rotulo for referencia in resposta.referencias]
    partes += [referencia.localizacao for referencia in resposta.referencias]
    partes += [aviso.texto for aviso in resposta.avisos]
    # O código do Perfil e da modalidade que a pessoa escolheu: é a pergunta, e não um valor novo.
    partes += [valor for _chave, valor in resposta.parametros if valor]
    return " ".join(partes)


def test_todo_numero_e_toda_data_da_explicacao_estao_nos_cartoes():
    faltando = []
    for nome, instante, _contexto, resposta in varrer():
        apoio = _textos_de_apoio(resposta)
        for numero in NUMERO.findall(resposta.explicacao.conteudo):
            if numero not in apoio:
                faltando.append((nome, instante, resposta.pergunta, numero))
    assert faltando == []


def test_a_explicacao_nao_avalia_a_pessoa_nem_chama_documento_de_completo():
    for _nome, _instante, _contexto, resposta in varrer():
        texto = resposta.explicacao.conteudo.lower()
        assert not [termo for termo in PROIBIDAS if termo in texto], resposta.explicacao.conteudo


def test_negativa_so_aparece_quando_o_edital_a_declara():
    """`FR-1422`: "não cabe" só com a negativa declarada num cartão de dado da mesma resposta."""
    for _nome, _instante, _contexto, resposta in varrer():
        texto = resposta.explicacao.conteudo.lower()
        declarada = any("não cabe" in r.conteudo for r in resposta.referencias)
        for negativa in NEGATIVAS:
            if negativa in texto and "não quer dizer que não caiba" not in texto:
                assert negativa == "não cabe" and declarada, resposta.explicacao.conteudo
