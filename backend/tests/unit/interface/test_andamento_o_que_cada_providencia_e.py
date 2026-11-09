"""O andamento diz o que cada providência é — as quatro correções, sem banco (135).

As regras puras da `127` recebem os fatos e devolvem a célula; aqui se prova que o que a `135`
acrescenta é **dado e texto**, e nunca situação: a lista sem inscritos (FR-4670 a FR-4676), o que
foi divulgado (FR-4677 a FR-4680), a razão da espera do definitivo (FR-4681 a FR-4683) e o escopo da
contagem do Perfil (FR-4684, FR-4685). Os mesmos casos, sobre os cenários da `134`, estão em
`tests/integration/treinamento/test_andamento_dos_cenarios.py`.
"""

from datetime import UTC, datetime

import pytest

from processo_seletivo.divulgacao.domain import publicabilidade as p
from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import providencias as pr
from tests.unit.interface.test_andamento_composicao import conteudo, sorteio, tipos

FECHA = datetime(2026, 11, 14, 21, tzinfo=UTC)
OFERTA = "publique como resultado preliminar"


def ordem(estado="falta", *, vazia=False, faltam=()):
    return a.situacao_da_ordem(
        {
            "celula": {"estado": estado, "url": "/ordenacao?lista=ppp"},
            "faltam": list(faltam),
            "vazia": vazia,
        }
    )


def resultado(estado, natureza="", *, nota=None, ordem_=a.FEITO, **fatos):
    celula = {"estado": estado, "natureza": natureza}
    if nota is not None:
        celula["nota"] = nota
    elif natureza:
        celula["nota"] = "resultado " + ("preliminar" if natureza == "PRELIMINAR" else "definitivo")
    return a.situacao_do_resultado({"celula": celula, "ordem": a.Celula(ordem_), **fatos})


# --- US1: a lista sem inscritos ---------------------------------------------------------------


def test_a_ordem_da_lista_vazia_continua_pendente_e_diz_o_que_e():
    """FR-4671, FR-4672, D-001: *Pendente*, de quem conduz, com o mesmo link; a frase e o dado."""
    vazia, cheia = ordem(vazia=True), ordem()
    assert (vazia.situacao, vazia.responsavel, vazia.url) == (
        cheia.situacao,
        cheia.responsavel,
        cheia.url,
    )
    assert vazia.lista_vazia and not cheia.lista_vazia
    assert vazia.nota == "lista sem inscritos" and cheia.nota == ""
    assert "lista sem inscritos" in vazia.ato and "declara que ninguém concorreu" in vazia.ato
    assert cheia.ato == "Emitir a ordem"


def test_a_lista_vazia_nao_muda_situacao_nenhuma():
    """FR-4676 e os casos-limite da spec: *Depois* (a recusa da `128` e as Etapas não feitas),
    *Feito* com "ninguém concorreu" e *Obsoleto* continuam decidindo como antes."""
    for estado, faltam in (
        ("falta", ["Prova"]),
        ("feito", []),
        ("obsoleto", []),
        ("nao_se_aplica", []),
    ):
        com, sem = ordem(estado, vazia=True, faltam=faltam), ordem(estado, faltam=faltam)
        assert com.situacao == sem.situacao, estado
    depois = ordem("falta", vazia=True, faltam=["Prova"])
    assert depois.situacao == a.DEPOIS and not depois.lista_vazia and not depois.ato


def test_a_ordem_obsoleta_de_lista_que_ficou_vazia_leva_a_nota():
    """Caso-limite: a célula é *Obsoleto*, como hoje; se a lista segue vazia, a nota acompanha."""
    celula = ordem("obsoleto", vazia=True)
    assert celula.situacao == a.OBSOLETO
    assert celula.nota == "lista sem inscritos" and celula.lista_vazia
    assert "lista sem inscritos" in celula.ato and "sucessora" in celula.ato


def _providencia(celula, lista, *, sua=True):
    return pr.Providencia.da_celula(
        celula,
        onde=f"Cefor · {lista}",
        lugar="Cefor",
        sua=sua,
        chave=(celula.natureza, lista),
        marco_id="m1",
        lista=(lista.lower(), lista),
    )


def test_a_providencia_carrega_o_dado_e_a_frase_para_qualquer_papel():
    """FR-4672, FR-4673 e o cenário 5 da US1: a de outro papel diz a mesma frase."""
    de_outro = _providencia(ordem(vazia=True), "PPP", sua=False)
    assert de_outro.lista_vazia
    assert de_outro.grupo == pr.DE_OUTRO
    assert "lista sem inscritos" in de_outro.ato_no_meio_da_frase
    assert de_outro.texto_do_papel == "Quem conduz a seleção"


def test_a_vazia_nao_se_junta_a_lista_com_inscritos():
    """FR-4674: uma providência por ato, mas nunca a vazia com a cheia."""
    itens = pr.agrupar([_providencia(ordem(), "Ampla"), _providencia(ordem(vazia=True), "PPP")])
    assert len(itens) == 2
    assert [i.lista_vazia for i in itens] == [False, True]


def test_a_vazia_nao_se_junta_mesmo_que_a_frase_coincida():
    """FR-4674 pelo dado, e não pela redação: o mesmo ato com e sem lista vazia são dois itens."""
    cheia = _providencia(ordem(), "Ampla")
    vazia = _providencia(
        a.Celula(
            a.PENDENTE,
            natureza=a.ORDEM,
            ato="Emitir a ordem",
            responsavel=a.CONDUZ,
            lista_vazia=True,
        ),
        "PPP",
    )
    assert len(pr.agrupar([cheia, vazia])) == 2


def test_duas_vazias_viram_uma_providencia_no_plural():
    """Caso-limite: a providência agrupada diz quais listas são, e que nenhuma tem inscritos."""
    [item] = pr.agrupar(
        [_providencia(ordem(vazia=True), "PPP"), _providencia(ordem(vazia=True), "PcD")]
    )
    assert item.listas == ("PPP", "PcD")
    assert item.ato == a.ATO_DAS_ORDENS_VAZIAS
    assert "listas sem inscritos" in item.ato
    assert item.onde_por_extenso == "Cefor · PPP e PcD"


# --- US2: o que foi divulgado é dado ----------------------------------------------------------

AFERICOES = {
    "publicavel": {"nivel": p.AVISO},
    "janela": {"nivel": p.IMPEDIMENTO, "codigo": p.JANELA_ABERTA, "mensagem": "x.", "ate": FECHA},
    "recurso": {"nivel": p.IMPEDIMENTO, "codigo": p.RECURSO_PENDENTE, "mensagem": "x."},
    "corte": {"nivel": p.IMPEDIMENTO, "codigo": p.CORTE_OBSOLETO, "mensagem": "Emita."},
}


@pytest.mark.parametrize(
    ("estado", "natureza", "fatos", "situacao", "divulgado"),
    [
        ("falta", "", {}, a.PENDENTE, a.NADA),
        ("feito", "PRELIMINAR", {"definitiva": AFERICOES["publicavel"]}, a.PENDENTE, a.PRELIMINAR),
        ("feito", "PRELIMINAR", {"definitiva": AFERICOES["janela"]}, a.AGUARDA, a.PRELIMINAR),
        ("feito", "PRELIMINAR", {"definitiva": AFERICOES["recurso"]}, a.AGUARDA, a.PRELIMINAR),
        ("feito", "PRELIMINAR", {"definitiva": AFERICOES["corte"]}, a.IMPEDIDO, a.PRELIMINAR),
        ("feito", "DEFINITIVA", {}, a.FEITO, a.DEFINITIVO),
        ("obsoleto", "DEFINITIVA", {}, a.OBSOLETO, a.DEFINITIVO),
        ("obsoleto", "PRELIMINAR", {}, a.OBSOLETO, a.PRELIMINAR),
    ],
)
def test_a_celula_do_resultado_diz_o_que_o_publico_le(estado, natureza, fatos, situacao, divulgado):
    """FR-4677, FR-4678: o dado ao lado da situação, que é a de antes (D-002)."""
    celula = resultado(estado, natureza, **fatos)
    assert (celula.situacao, celula.divulgado) == (situacao, divulgado)


def test_o_preliminar_com_a_ordem_obsoleta_e_depois_e_diz_preliminar():
    """Caso-limite (FR-4550 da `133`): *Depois*, como hoje, e o dado diz o que o público lê."""
    celula = resultado("feito", "PRELIMINAR", ordem_=a.OBSOLETO)
    assert (celula.situacao, celula.divulgado) == (a.DEPOIS, a.PRELIMINAR)


@pytest.mark.parametrize("nota", ["", "outra redação qualquer", "resultado definitivo"])
def test_a_redacao_da_nota_nao_decide_a_situacao(nota):
    """SC-1463, FR-4679: trocada a nota, a situação de cada caso é a mesma — e a nota sai como está
    (FR-4680)."""
    for estado, natureza, fatos in (
        ("feito", "PRELIMINAR", {"definitiva": AFERICOES["janela"]}),
        ("feito", "PRELIMINAR", {"definitiva": AFERICOES["publicavel"]}),
        ("feito", "DEFINITIVA", {}),
        ("falta", "", {}),
    ):
        original, trocada = (
            resultado(estado, natureza, **fatos),
            resultado(estado, natureza, nota=nota, **fatos),
        )
        assert (trocada.situacao, trocada.divulgado) == (original.situacao, original.divulgado)
        if trocada.nota:
            assert trocada.nota == nota


def _perfil_com_resultados(*celulas):
    c = conteudo([], [sorteio()])
    _, pontos = tipos(c)
    listas = [(None, "Ampla")] + [(f"l{n}", f"L{n}") for n in range(1, len(celulas))]
    perfil = a.PerfilNoAndamento(
        perfil={"name": "Cefor"}, forma="", listas=listas, pontos=pontos, inscritos=3
    )
    ponto = next(p_ for p_ in pontos if p_.tipo == a.RESULTADO)
    ponto.celulas = {a._chave(lista): c_ for (lista, _), c_ in zip(listas, celulas, strict=True)}
    return perfil


@pytest.mark.parametrize("nota", ["", "xyz"])
def test_o_resumo_do_perfil_le_o_dado_e_nao_a_nota(nota):
    """SC-1463: os casos de divulgação do resumo, com a nota trocada, dizem o mesmo."""
    preliminar = a.Celula(a.AGUARDA, nota=nota, divulgado=a.PRELIMINAR)
    definitivo = a.Celula(a.FEITO, nota=nota, divulgado=a.DEFINITIVO)
    nada = a.Celula(a.PENDENTE, nota=nota, divulgado=a.NADA)
    obsoleto = a.Celula(a.OBSOLETO, nota=nota, divulgado=a.DEFINITIVO)
    casos = {
        (preliminar,): "resultado preliminar",
        (definitivo, definitivo): "resultado definitivo",
        (definitivo, nada, nada): "resultado publicado em 1 de 3 listas",
        (nada,): "resultado não publicado",
        # O definitivo de um ato anterior não é o definitivo da lista (R-006).
        (obsoleto, definitivo): "resultado preliminar",
    }
    for celulas, esperado in casos.items():
        assert a._resultado_em_palavras(_perfil_com_resultados(*celulas)) == esperado


def test_o_preliminar_com_a_ordem_obsoleta_conta_como_publicado_no_resumo():
    """R-006: a célula *Depois* sem nota contava como não publicada; pelo dado, é o preliminar."""
    depois = a.Celula(a.DEPOIS, divulgado=a.PRELIMINAR)
    assert a._resultado_em_palavras(_perfil_com_resultados(depois)) == "resultado preliminar"


# --- US3: a razão da espera do definitivo -----------------------------------------------------


def test_com_o_preliminar_publicado_a_espera_do_prazo_nao_oferece_o_preliminar():
    """FR-4681: o motivo e até quando, e não a alternativa já praticada."""
    lida = {
        "nivel": p.IMPEDIMENTO,
        "codigo": p.JANELA_ABERTA,
        "mensagem": p.MENSAGENS[p.JANELA_ABERTA].format(fecha="14/11/2026 às 18h00"),
        "ate": FECHA,
    }
    celula = resultado("feito", "PRELIMINAR", definitiva=lida)
    assert celula.situacao == a.AGUARDA
    assert OFERTA not in celula.razao
    assert "14/11/2026" in celula.razao and "prazo recursal" in celula.razao
    assert "resultado preliminar já está publicado" in celula.razao
    # A primeira frase é a da aferição: o nível 1 agrupa as esperas por ela.
    assert pr._primeira_frase(celula.razao) == pr._primeira_frase(a._frase(lida["mensagem"]))


def test_com_o_preliminar_publicado_a_espera_do_recurso_nao_oferece_o_preliminar():
    lida = {
        "nivel": p.IMPEDIMENTO,
        "codigo": p.RECURSO_PENDENTE,
        "mensagem": p.MENSAGENS[p.RECURSO_PENDENTE],
    }
    celula = resultado("feito", "PRELIMINAR", definitiva=lida)
    assert celula.situacao == a.AGUARDA
    assert OFERTA not in celula.razao
    assert "recurso pendente" in celula.razao


@pytest.mark.parametrize(
    "codigo", [p.REAVALIACAO_PENDENTE, p.PROVIDENCIA_PENDENTE, p.CORTE_OBSOLETO]
)
def test_as_outras_razoes_continuam_as_da_afericao(codigo):
    """FR-4683."""
    mensagem = p.MENSAGENS[codigo]
    celula = resultado(
        "feito",
        "PRELIMINAR",
        definitiva={"nivel": p.IMPEDIMENTO, "codigo": codigo, "mensagem": mensagem},
    )
    assert celula.razao == a._frase(mensagem)


def test_as_mensagens_da_afericao_continuam_oferecendo_o_preliminar():
    """FR-4682, D-003: a prévia e o comando leem `MENSAGENS`, que não muda."""
    assert p.MENSAGENS[p.JANELA_ABERTA].endswith("ou publique como resultado preliminar.")
    assert p.MENSAGENS[p.RECURSO_PENDENTE].endswith("ou publique como resultado preliminar.")
    for codigo, segunda in p.MENSAGENS_COM_O_PRELIMINAR_PUBLICADO.items():
        assert OFERTA not in segunda
        assert segunda.split(". ")[0] == p.MENSAGENS[codigo].split(". ")[0]
    assert p.mensagem_com_o_preliminar_publicado(p.CORTE_OBSOLETO) is None


# --- US4: a contagem do Perfil diz o escopo ---------------------------------------------------


def test_o_resumo_do_perfil_diz_que_conta_as_providencias_dos_marcos():
    """FR-4684, FR-4685: o mesmo número, com o escopo em palavras."""
    perfil = _perfil_com_resultados(a.Celula(a.PENDENTE, divulgado=a.NADA))
    perfil.providencias = [
        _providencia(ordem(), "Ampla"),
        _providencia(
            a.Celula(
                a.PENDENTE, natureza=a.RESULTADO, ato="Publicar o resultado", responsavel=a.PUBLICA
            ),
            "Ampla",
        ),
    ]
    assert "2 providências em aberto nos marcos" in a.resumo_do_perfil(perfil)
    perfil.providencias = perfil.providencias[:1]
    assert "1 providência em aberto nos marcos" in a.resumo_do_perfil(perfil)


def test_sem_providencia_de_marco_a_contagem_nao_aparece():
    perfil = _perfil_com_resultados(a.Celula(a.FEITO, divulgado=a.DEFINITIVO))
    assert "em aberto" not in a.resumo_do_perfil(perfil)


def test_o_cartao_continua_com_a_contagem_do_edital():
    """FR-4685, US4 cenário 2: o cartão "O que fazer agora" não muda."""
    nivel = pr.Nivel1([_providencia(ordem(), "Ampla"), _providencia(ordem(vazia=True), "PPP")])
    assert pr.contagem(nivel) == "2 providências em aberto · 2 são suas"
