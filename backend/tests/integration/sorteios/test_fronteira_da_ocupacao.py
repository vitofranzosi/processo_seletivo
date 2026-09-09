"""Nada no sistema responde quem ocupa vaga, quem é suplente ou quem sai de qual lista (FR-064).

**Este teste existe para denunciar a próxima tarefa que responder a essas perguntas.** A `021`
produz uma ordem, e só. Vaga ocupada, suplência, remanejamento, convocação e a interação entre
listas do 57/28 — o cotista sorteado nas duas fica na de ampla concorrência — são de outra
capacidade, e a tentação de resolvê-las "já que a ordem está pronta" é a que o Out of Scope da spec
recusa em nome próprio.
"""

import inspect

import pytest

from processo_seletivo.sorteios import models as modelos_do_sorteio
from processo_seletivo.sorteios.application import previa, relacao, sorteio, verificacao
from processo_seletivo.sorteios.domain import chave, manifesto, metodo, normalizacao, projecao

pytestmark = [pytest.mark.integration]

PROIBIDOS = (
    "vaga_ocupada",
    "ocupacao",
    "suplente",
    "suplencia",
    "remanejamento",
    "convocacao",
    "convocar",
    "classificado_dentro",
    "aprovado",
    "corte",
)

MODULOS = (
    modelos_do_sorteio,
    previa,
    relacao,
    sorteio,
    verificacao,
    chave,
    manifesto,
    metodo,
    normalizacao,
    projecao,
)


@pytest.mark.parametrize("modulo", MODULOS, ids=lambda m: m.__name__.split(".")[-1])
def test_nenhum_nome_publico_do_modulo_responde_quem_entrou(modulo):
    """A fronteira é de vocabulário: um nome desses aqui seria a capacidade errada nascendo.

    A comparação é por **segmento inteiro** do nome, e não por substring: `recorte` — o par
    (recorte de vaga × lista), que é vocabulário central desta feature — contém `corte`, que é o
    que se proíbe. Uma varredura por substring reprovaria a palavra que a spec mais usa.
    """
    publicos = [nome for nome in dir(modulo) if not nome.startswith("_")]

    for nome in publicos:
        segmentos = set(nome.lower().split("_"))
        assert not (segmentos & set(PROIBIDOS)), f"{modulo.__name__}.{nome}"


@pytest.mark.parametrize("modulo", MODULOS, ids=lambda m: m.__name__.split(".")[-1])
def test_nenhuma_funcao_do_modulo_decide_ocupacao(modulo):
    """Não é sobre a palavra na prosa — é sobre **código** que decida quem entrou."""
    fonte = inspect.getsource(modulo)

    for linha in fonte.splitlines():
        despida = linha.strip()
        if despida.startswith("#") or despida.startswith('"') or despida.startswith("*"):
            continue
        for proibido in ("vagas_disponiveis", "dentro_das_vagas", "ate_a_vaga", "limite_de_vagas"):
            assert proibido not in despida, f"{modulo.__name__}: {despida}"


def test_a_ordem_nao_e_truncada_pelo_numero_de_vagas():
    """FR-025: todos recebem posição, e o número de vagas não entra na conta."""
    parametros = set(inspect.signature(chave.ordem).parameters)

    assert parametros == {"relation_hash", "draw_scope_id", "seed", "public_numbers"}
    assert "vagas" not in parametros


def test_o_modelo_nao_tem_coluna_que_responda_quem_ocupou():
    campos = {
        campo.name
        for modelo in (
            modelos_do_sorteio.RelacaoDeHabilitados,
            modelos_do_sorteio.ParticipanteHabilitado,
            modelos_do_sorteio.Sorteio,
        )
        for campo in modelo._meta.get_fields()
        if hasattr(campo, "name")
    }

    for proibido in PROIBIDOS:
        assert not any(proibido in campo for campo in campos), proibido
