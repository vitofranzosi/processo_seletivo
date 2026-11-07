"""A composição da advertência do "Encerrar Processo", sem banco (130, R-2 e R-5).

Duas garantias que não dependem de cenário: que cada tipo de situação da `113` foi **decidido** —
entra no Processo, fica fora, ou vem do relatório —, e que o resumo da lista muda quando, e só
quando, o que o gestor leu muda.
"""

import uuid
from types import SimpleNamespace

from processo_seletivo.interface import encerramento as e
from processo_seletivo.processos.application import pendencias_do_edital as p

ESPECIES = {p.IMPEDIMENTO, p.ADVERTENCIA}


def _tipos_declarados():
    return {
        valor
        for nome, valor in vars(p).items()
        if nome.isupper() and isinstance(valor, str) and valor == nome and valor not in ESPECIES
    }


def test_todo_tipo_de_situacao_foi_decidido_uma_vez():
    """Um tipo novo na `113` reprova aqui até alguém decidir se ele diz algo no Processo (R-2)."""
    conjuntos = (e.TIPOS_NO_PROCESSO, e.TIPOS_FORA_DO_PROCESSO, frozenset(e.DA_099))
    tipos = _tipos_declarados()
    assert tipos, "a varredura não encontrou tipo nenhum"
    sem_decisao = sorted(t for t in tipos if not any(t in c for c in conjuntos))
    duas_vezes = sorted(t for t in tipos if sum(t in c for c in conjuntos) > 1)
    assert not sem_decisao, f"tipos sem decisão sobre o Processo: {sem_decisao}"
    assert not duas_vezes, f"tipos decididos mais de uma vez: {duas_vezes}"


def test_periodo_e_retificacao_ficam_fora():
    """D-002: num Edital final, o período e a Retificação não dizem nada verdadeiro."""
    for tipo in (
        p.PERIODO_EM_CURSO,
        p.PERIODO_POR_ABRIR,
        p.PERIODO_SEM_TERMINO,
        p.RETIFICACAO_HOMOLOGADA,
        p.RETIFICACAO_EM_CURSO,
    ):
        assert tipo in e.TIPOS_FORA_DO_PROCESSO


def _grupo(mensagens, *, edital_id=None, tipos=None, urls=None):
    edital = SimpleNamespace(id=edital_id or uuid.uuid4())
    tipos = tipos or [""] * len(mensagens)
    urls = urls or [""] * len(mensagens)
    itens = tuple(e.Item(m, url=u, tipo=t) for m, t, u in zip(mensagens, tipos, urls, strict=True))
    return e.GrupoDoEdital(edital, itens)


def test_a_mesma_lista_da_o_mesmo_resumo():
    um = _grupo(["1 recurso aguarda decisão."])
    assert e.resumo_de((um,)) == e.resumo_de(
        (_grupo(["1 recurso aguarda decisão."], edital_id=um.edital.id),)
    )


def test_uma_frase_diferente_muda_o_resumo():
    edital_id = uuid.uuid4()
    antes = _grupo(["2 convocações aguardando resposta, até 20/11."], edital_id=edital_id)
    depois = _grupo(["1 convocação aguardando resposta, até 20/11."], edital_id=edital_id)
    assert e.resumo_de((antes,)) != e.resumo_de((depois,))


def test_a_ordem_das_frases_dentro_do_edital_nao_muda_o_resumo():
    """A `113` lê os prazos de recurso sem ordem fixa; a mesma lista não pode dar 409 (R-5)."""
    edital_id = uuid.uuid4()
    um = _grupo(
        ["O prazo de recurso contra “A” vai até x.", "1 recurso aguarda decisão."],
        edital_id=edital_id,
    )
    outro = _grupo(
        ["1 recurso aguarda decisão.", "O prazo de recurso contra “A” vai até x."],
        edital_id=edital_id,
    )
    assert e.resumo_de((um,)) == e.resumo_de((outro,))


def test_a_ordem_dos_editais_muda_o_resumo():
    a, b = _grupo(["x."]), _grupo(["y."])
    assert e.resumo_de((a, b)) != e.resumo_de((b, a))


def test_a_lista_vazia_tem_resumo_proprio():
    vazio = e.resumo_de(())
    assert len(vazio) == 64
    assert vazio != e.resumo_de((_grupo(["x."]),))


def test_o_caminho_nao_entra_no_resumo():
    """O URL depende de quem lê; o que precisa ser igual é o que está em aberto (R-5)."""
    edital_id = uuid.uuid4()
    com = _grupo(["1 recurso aguarda decisão."], edital_id=edital_id, urls=["/gestao/x"])
    sem = _grupo(["1 recurso aguarda decisão."], edital_id=edital_id)
    assert e.resumo_de((com,)) == e.resumo_de((sem,))


def test_convocado_no_prazo_so_com_convocacao_aguardando():
    aguardando = _grupo(["1 convocação aguardando resposta."], tipos=[p.CONVOCACAO_AGUARDANDO])
    vencida = _grupo(["1 convocação com prazo encerrado."], tipos=[p.CONVOCACAO_VENCIDA])
    assert e.AdvertenciaDoProcesso.de((aguardando,)).convocado_no_prazo
    assert not e.AdvertenciaDoProcesso.de((vencida,)).convocado_no_prazo
    assert e.AdvertenciaDoProcesso.de(()).vazia
