"""Os quatro passos da tela do sorteio, sem banco (142, FR-4900 a FR-4918).

O módulo só agrupa as células da derivação da `127`: estes testes montam os pontos à mão, nas
combinações que o banco de demonstração não tem todas — três listas em situações diferentes, a
lista vazia, a derivação ausente —, e conferem a contagem, o sinal do passo e a tarefa de agora.
"""

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import conceitos
from processo_seletivo.interface import jornada_do_sorteio as j
from processo_seletivo.interface.templatetags.interface_extras import ancora_do_sorteio

MARCO = "00000000-0000-4000-8000-0000000000aa"
PPI = "00000000-0000-4000-8000-000000000831"
PCD = "00000000-0000-4000-8000-000000000832"
RECORTES = [
    {"lista_id": "", "nome": "Ampla"},
    {"lista_id": PPI, "nome": "PPI"},
    {"lista_id": PCD, "nome": "PcD"},
]


def _ponto(tipo, **por_lista):
    chaves = {"ampla": "", "ppi": PPI, "pcd": PCD}
    return a.Ponto(
        tipo,
        tipo,
        "grupo",
        marco={"id": MARCO},
        celulas={chaves[nome]: celula for nome, celula in por_lista.items()},
    )


def _pontos(relacao, semente, sorteio, resultado=None):
    def mesmo(celula):
        return {"ampla": celula, "ppi": celula, "pcd": celula}

    pontos = {
        a.RELACAO: _ponto(a.RELACAO, **relacao),
        a.SEMENTE: _ponto(a.SEMENTE, **mesmo(semente)),
        a.SORTEIO: _ponto(a.SORTEIO, **sorteio),
    }
    if resultado is not None:
        pontos[a.RESULTADO] = _ponto(a.RESULTADO, **resultado)
    return pontos


C = a.Celula
FEITO, PENDENTE, NSA = C(a.FEITO), C(a.PENDENTE), C(a.NAO_SE_APLICA)
DEPOIS = C(a.DEPOIS, razao="falta a semente")


def _nada_fixado():
    return _pontos(
        {"ampla": PENDENTE, "ppi": PENDENTE, "pcd": NSA},
        C(a.DEPOIS, razao="nenhuma relação deste marco está congelada"),
        {"ampla": DEPOIS, "ppi": DEPOIS, "pcd": NSA},
    )


def test_os_quatro_passos_na_ordem_com_os_nomes_do_centro():
    """FR-4900: os três primeiros leem `conceitos.py`, e não uma cópia."""
    passos = j.da_tela(_nada_fixado(), RECORTES, conduz=True)

    assert [p.numero for p in passos] == [1, 2, 3, 4]
    assert [p.simples for p in passos[:3]] == [
        conceitos.CONCEITOS[a.RELACAO]["simples"],
        conceitos.CONCEITOS[a.SEMENTE]["simples"],
        conceitos.CONCEITOS[a.SORTEIO]["simples"],
    ]
    assert passos[3].simples == "Consultar a ordem sorteada"
    assert [p.ancora for p in passos] == [
        "titulo-recortes",
        "titulo-ocorrencia",
        "titulo-execucao",
        "titulo-resultado",
    ]
    # O nome no GPS só aparece onde é jargão (FR-4729 da `136`).
    assert [p.jargao for p in passos] == [True, True, False, False]


def test_cada_passo_diz_o_que_pede_alcanca_desencadeia_e_se_volta_atras():
    """FR-4901."""
    for passo in j.da_tela(_nada_fixado(), RECORTES, conduz=True):
        assert passo.curta and passo.porque
        assert passo.precisa and passo.afeta and passo.depois and passo.irreversivel


def test_os_textos_da_tela_nao_usam_os_termos_que_ela_define():
    """Texto que chega por variável escapa da varredura de vocabulário (a razão de
    `conceitos.py`)."""
    textos = [*j.CONCEITO_DA_ORDEM.values()]
    textos += [frase for contexto in j.CONTEXTO.values() for frase in contexto.values()]
    for texto in textos:
        for termo in ("recorte", "faixa", "geração"):
            assert termo not in texto.lower(), (termo, texto)


def test_nada_fixado_o_primeiro_passo_e_a_tarefa_de_agora():
    """US1, cenário 1: a lista vazia não conta, e o passo da semente espera."""
    fixar, semente, sorteio, ordem = j.da_tela(_nada_fixado(), RECORTES, conduz=True)

    assert fixar.agora and not semente.agora and not sorteio.agora and not ordem.agora
    assert fixar.contagem == "0 de 2 listas fixadas"
    assert fixar.situacao.situacao == a.PENDENTE
    assert semente.situacao.situacao == a.DEPOIS
    assert [(rotulo, c.situacao) for rotulo, c in fixar.listas] == [
        ("Ampla", a.PENDENTE),
        ("PPI", a.PENDENTE),
        ("PcD", a.NAO_SE_APLICA),
    ]


def test_uma_lista_fixada_e_outra_nao_o_passo_conta_as_duas_e_a_semente_nao_trava():
    """US1, cenário 2 (FR-4905, FR-4909): o passo 1 continua a tarefa de agora, e a semente
    aparece disponível — a derivação a diz Pendente, e a jornada não a esconde."""
    pontos = _pontos(
        {"ampla": FEITO, "ppi": PENDENTE, "pcd": NSA},
        PENDENTE,
        {"ampla": DEPOIS, "ppi": C(a.DEPOIS, razao="falta congelar a relação"), "pcd": NSA},
    )
    fixar, semente, *_ = j.da_tela(pontos, RECORTES, conduz=True)

    assert fixar.contagem == "1 de 2 listas fixadas"
    assert fixar.agora and fixar.situacao.situacao == a.PENDENTE
    assert semente.situacao.situacao == a.PENDENTE and not semente.agora
    assert fixar.a_praticar


def test_a_semente_e_do_marco_e_aparece_uma_vez():
    """FR-4906: uma célula só, e nenhuma lista no passo."""
    semente = j.da_tela(_nada_fixado(), RECORTES, conduz=True)[1]

    assert semente.do_marco
    assert semente.listas == []
    assert len(semente.celulas) == 1
    assert semente.contagem == ""


def test_todas_fixadas_a_semente_e_a_vez():
    pontos = _pontos(
        {"ampla": FEITO, "ppi": FEITO, "pcd": NSA},
        PENDENTE,
        {"ampla": DEPOIS, "ppi": DEPOIS, "pcd": NSA},
    )
    fixar, semente, *_ = j.da_tela(pontos, RECORTES, conduz=True)

    assert fixar.situacao.situacao == a.FEITO and fixar.contagem == "2 de 2 listas fixadas"
    assert semente.agora


def test_uma_sorteada_e_outra_nao_o_sorteio_e_a_vez_e_a_ordem_existe_numa():
    """US3 (FR-4905): a lista concluída ao lado da pendente."""
    pontos = _pontos(
        {"ampla": FEITO, "ppi": FEITO, "pcd": NSA},
        FEITO,
        {"ampla": FEITO, "ppi": PENDENTE, "pcd": NSA},
    )
    _, _, sorteio, ordem = j.da_tela(pontos, RECORTES, conduz=True)

    assert sorteio.agora and sorteio.contagem == "1 de 2 listas sorteadas"
    assert ordem.contagem == "1 de 2 listas com ordem gravada"
    assert [c.situacao for _, c in ordem.listas] == [a.FEITO, a.DEPOIS, a.NAO_SE_APLICA]
    assert not ordem.agora, "consultar é leitura, e nunca a tarefa de agora"


def test_o_sinal_do_passo_e_o_da_lista_mais_urgente():
    """D-003: o que se pratica antes do impedido, do que espera e do que vem depois."""
    impedido = C(a.IMPEDIDO, razao="a extração é anterior ao congelamento")
    aguarda = C(a.AGUARDA)
    pontos = _pontos(
        {"ampla": FEITO, "ppi": aguarda, "pcd": impedido},
        FEITO,
        {"ampla": FEITO, "ppi": DEPOIS, "pcd": impedido},
    )
    fixar, _, sorteio, _ = j.da_tela(pontos, RECORTES, conduz=True)

    assert fixar.situacao.situacao == a.IMPEDIDO
    assert sorteio.situacao.situacao == a.IMPEDIDO
    assert not fixar.agora and not sorteio.agora, "impedido e aguarda não são a tarefa de agora"


def test_quem_so_le_nao_tem_tarefa_de_agora():
    """FR-4917."""
    assert not any(p.agora for p in j.da_tela(_nada_fixado(), RECORTES, conduz=False))


def test_sem_derivacao_os_passos_existem_sem_situacao():
    """FR-4918: os nomes não dependem da derivação; a situação, sim."""
    passos = j.da_tela({}, RECORTES, conduz=True)

    assert [p.simples for p in passos][0] == conceitos.CONCEITOS[a.RELACAO]["simples"]
    assert all(
        p.situacao is None and not p.agora and p.contagem in ("", "nenhuma lista com participantes")
        for p in passos
    )


def test_os_pontos_do_marco_sao_os_do_perfil_que_o_tem():
    pontos = _nada_fixado()
    perfil = a.PerfilNoAndamento(
        perfil={"id": "p"}, forma="", listas=[], pontos=list(pontos.values()), inscritos=1
    )
    andamento = a.Andamento(perfis=[perfil], providencias=[], atencoes=[], inscricoes={})

    assert j.pontos_do_marco(andamento, MARCO) == pontos
    assert j.pontos_do_marco(andamento, "outro") == {}
    assert j.pontos_do_marco(None, MARCO) == {}


def test_a_execucao_tem_ancora_propria_e_a_tela_le_a_mesma_funcao():
    """FR-4915, D-002: a relação continua no cartão; o sorteio vai à execução."""
    assert a.ancora_do_sorteio(None) == a.ancora_do_sorteio("") == "sorteio-ampla"
    assert a.ancora_do_sorteio(PPI) == f"sorteio-{PPI}"
    for lista in (None, "", PPI):
        assert ancora_do_sorteio(lista) == a.ancora_do_sorteio(lista)
    # Duas listas juntadas numa providência do sorteio chegam à seção da execução.
    assert a.ancora_comum("sorteio-ampla", f"sorteio-{PPI}") == "titulo-execucao"
    assert a.ancora_comum("titulo-execucao", f"sorteio-{PCD}") == "titulo-execucao"
    assert a.ancora_comum("sorteio-ampla", "recorte-ampla") == ""
