"""As obrigações da convocação, derivadas, sem consulta (118, FR-3721 a FR-3729, FR-3746, SC-1126).

Os itens são os `ItemLido` de verdade, da `115`, sobre apresentações e conferências de mentira: o
que se testa é a projeção, e ela só lê os atributos que a leitura documental já entrega. A política
do Requerimento é a `Disponibilidade` de verdade, da `029`, montada com o que `apurar` devolveria.
"""

import itertools
import re
from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.convocacao.application.documentos import ItemLido, LeituraDocumental
from processo_seletivo.convocacao.domain import nomes, vocabulario_dos_documentos
from processo_seletivo.portal import obrigacoes as o
from processo_seletivo.requerimentos.domain import nomes as req_nomes
from processo_seletivo.requerimentos.domain.disponibilidade import Disponibilidade

FUSO = ZoneInfo("America/Sao_Paulo")
VENCIMENTO = datetime(2026, 11, 9, 13, 27, tzinfo=FUSO)
RECEBIDO_EM = datetime(2026, 11, 4, 9, 5, tzinfo=FUSO)
NA_INSCRICAO_EM = datetime(2026, 3, 2, 10, 0, tzinfo=FUSO)
MOTIVO = "Falta a página 2."

MOMENTOS = {
    o.ABERTA: {"causa": None, "desfecho": None},
    o.ENCERRADA_PELO_PRAZO: {"causa": o.PRAZO, "desfecho": None},
    o.ENCERRADA_PELO_PROCESSO: {"causa": o.PROCESSO, "desfecho": None},
    o.DECIDIDA: {"causa": None, "desfecho": SimpleNamespace(especie=nomes.INDEFERIMENTO)},
}

_ids = itertools.count(1)


def _apresentacao(origem="portal"):
    id_ = next(_ids)
    if origem == "portal":
        return SimpleNamespace(id=id_, arquivo="x.pdf", apresentado_em=RECEBIDO_EM)
    if origem == "inscricao":
        return SimpleNamespace(
            id=id_,
            arquivo="",
            documento_da_inscricao_id=1,
            documento_da_inscricao=SimpleNamespace(uploaded_at=NA_INSCRICAO_EM),
            apresentado_em=RECEBIDO_EM,
        )
    origem_anterior = SimpleNamespace(
        apresentado_em=NA_INSCRICAO_EM, item=SimpleNamespace(versao_id=1)
    )
    return SimpleNamespace(
        id=id_,
        arquivo="",
        documento_da_inscricao_id=None,
        apresentacao_de_origem=origem_anterior,
        apresentado_em=RECEBIDO_EM,
    )


def lido(estado, *, obrigatorio=True, origem="portal", apresentado=None, nome=None, ordem=0):
    """Um `ItemLido` no estado pedido, com o que a leitura da `115` teria lido."""
    if apresentado is None:
        apresentado = estado not in (nomes.ITEM_A_APRESENTAR,)
    apresentacoes = [_apresentacao(origem)] if apresentado else []
    conferencias = []
    if estado == nomes.ITEM_PENDENTE:
        conferencias = [SimpleNamespace(resultado=nomes.PENDENTE, motivo=MOTIVO)]
    elif estado == nomes.ITEM_COMPLEMENTADO:
        conferencias = [SimpleNamespace(resultado=nomes.PENDENTE, motivo=MOTIVO)]
    elif estado == nomes.ITEM_CONFORME:
        conferencias = [SimpleNamespace(resultado=nomes.CONFORME, motivo="")]
    elif estado == nomes.ITEM_NAO_SE_APLICA:
        conferencias = [SimpleNamespace(resultado="NAO_SE_APLICA", motivo="Concluiu no Ifes.")]
    item = SimpleNamespace(
        id=next(_ids),
        chave="doc",
        situacao="OBRIGATORIO" if obrigatorio else "FACULTATIVO",
        versao_id=1,
    )
    return ItemLido(
        item=item,
        requisito={"name": nome or f"Documento {item.id}", "order": ordem},
        estado=estado,
        apresentacoes=apresentacoes,
        conferencias=conferencias,
    )


def disp(momento=req_nomes.NA_CONVOCACAO, *, status="", disponivel=True, prazo=False, final=""):
    if momento is None:
        return Disponibilidade(exigido=False, momento="", disponivel=False)
    return Disponibilidade(
        exigido=True,
        momento=momento,
        disponivel=disponivel,
        chamada=object() if disponivel else None,
        status_do_requerimento=status,
        prazo_decorrido=prazo,
        estado_final_do_processo=final,
    )


def projetar(
    itens,
    momento=o.ABERTA,
    *,
    requerimento=None,
    estado=nomes.CONVOCADO_PRAZO_EM_CURSO,
    vencimento=VENCIMENTO,
    final="ENCERRADO",
    agora=None,
    corrigida=False,
):
    return o.obrigacoes_da_convocacao(
        leitura=LeituraDocumental(itens=list(itens)),
        requerimento=requerimento,
        estado_do_prazo=estado,
        causa_do_fechamento=MOMENTOS[momento]["causa"],
        desfecho=MOMENTOS[momento]["desfecho"],
        vencimento=vencimento,
        estado_final_do_processo=final,
        canal="atendimento@ifes.edu.br",
        agora=agora,
        corrigida=corrigida,
    )


# --- SC-1126: cada combinação em exatamente uma categoria ---------------------------------------

# (estado, origem, apresentado) → categoria (obrigatório, facultativo). É a tabela da FR-3722.
CASOS = {
    "a_apresentar": ((nomes.ITEM_A_APRESENTAR, "portal", False), (o.A_ENVIAR, o.OPCIONAL)),
    "pendente_com_envio": ((nomes.ITEM_PENDENTE, "portal", True), (o.A_CORRIGIR, o.OPCIONAL)),
    "pendente_sem_envio": ((nomes.ITEM_PENDENTE, "portal", False), (o.A_ENVIAR, o.OPCIONAL)),
    "recebido_portal": (
        (nomes.ITEM_RECEBIDO, "portal", True),
        (o.COM_A_COMISSAO, o.COM_A_COMISSAO),
    ),
    "recebido_inscricao": (
        (nomes.ITEM_RECEBIDO, "inscricao", True),
        (o.COM_A_COMISSAO, o.COM_A_COMISSAO),
    ),
    "recebido_chamada": (
        (nomes.ITEM_RECEBIDO, "chamada", True),
        (o.COM_A_COMISSAO, o.COM_A_COMISSAO),
    ),
    "complementado": (
        (nomes.ITEM_COMPLEMENTADO, "portal", True),
        (o.COM_A_COMISSAO, o.COM_A_COMISSAO),
    ),
    "conforme": ((nomes.ITEM_CONFORME, "portal", True), (o.CONFERIDO, o.CONFERIDO)),
    "conforme_inscricao": ((nomes.ITEM_CONFORME, "inscricao", True), (o.CONFERIDO, o.CONFERIDO)),
    "nao_se_aplica": ((nomes.ITEM_NAO_SE_APLICA, "portal", False), (o.CONFERIDO, o.CONFERIDO)),
}


@pytest.mark.parametrize("momento", list(MOMENTOS))
@pytest.mark.parametrize("obrigatorio", [True, False], ids=["obrigatorio", "facultativo"])
@pytest.mark.parametrize("caso", list(CASOS))
def test_cada_item_cai_em_exatamente_uma_categoria(caso, obrigatorio, momento):
    (estado, origem, apresentado), esperadas = CASOS[caso]
    item = lido(estado, obrigatorio=obrigatorio, origem=origem, apresentado=apresentado)
    projetada = projetar([item], momento)
    (resultado,) = projetada.itens

    assert resultado.categoria == esperadas[0 if obrigatorio else 1]
    # Exatamente uma: o item aparece em um, e um só, dos grupos que as telas desenham.
    grupos = [
        projetada.tarefas_de_documento,
        projetada.opcionais_a_enviar,
        tuple(i for i in projetada.itens if i.categoria == o.COM_A_COMISSAO),
        tuple(i for i in projetada.itens if i.categoria == o.CONFERIDO),
    ]
    assert sum(resultado in grupo for grupo in grupos) == 1
    # O convite a enviar existe só com a chamada aberta, e nunca no conferido (FR-3722).
    if momento != o.ABERTA or resultado.categoria == o.CONFERIDO:
        assert not resultado.pode_enviar
    if momento != o.ABERTA:
        assert projetada.tarefas == ()


@pytest.mark.parametrize("momento", list(MOMENTOS))
def test_a_categoria_nao_muda_com_o_momento(momento):
    aberta = projetar([lido(nomes.ITEM_PENDENTE)], o.ABERTA).itens[0].categoria
    assert projetar([lido(nomes.ITEM_PENDENTE)], momento).itens[0].categoria == aberta


# --- O momento (FR-3722) e a causa (FR-3721, D-015) ---------------------------------------------


def test_processo_e_prazo_juntos_vale_o_processo():
    """Com as duas causas, a view entrega `PROCESSO`; aqui se prova o que isso produz."""
    req = disp(prazo=True, final="ENCERRADO")
    projetada = projetar(
        [lido(nomes.ITEM_A_APRESENTAR)], o.ENCERRADA_PELO_PROCESSO, requerimento=req
    )

    assert projetada.momento == o.ENCERRADA_PELO_PROCESSO
    assert projetada.requerimento == o.REQ_NAO_ENVIADO_ENCERRADO
    assert "prazo terminou" not in " ".join(projetada.frase_do_fechamento).lower()


def test_o_desfecho_com_o_processo_aberto_nao_reabre_a_escrita():
    projetada = projetar([lido(nomes.ITEM_A_APRESENTAR), lido(nomes.ITEM_RECEBIDO)], o.DECIDIDA)

    assert projetada.momento == o.DECIDIDA
    assert not any(item.pode_enviar for item in projetada.itens)
    assert projetada.frase_de_estado == o.NADA_POR_ENQUANTO


def test_sem_item_pedido_nao_ha_projecao():
    assert projetar([]) is None


# --- O Requerimento: as sete linhas da FR-3725 --------------------------------------------------

DESFECHO = SimpleNamespace(especie=nomes.INDEFERIMENTO)
LINHAS = [
    ("1", disp(None), None, None, o.REQ_NAO_PEDIDO),
    ("2_na_convocacao", disp(status=req_nomes.ENVIADO), None, None, o.REQ_ENVIADO),
    (
        "2_na_inscricao",
        disp(req_nomes.NA_INSCRICAO, status=req_nomes.ENVIADO),
        None,
        None,
        o.REQ_ENVIADO,
    ),
    (
        "2_com_desfecho",
        disp(status=req_nomes.ENVIADO, disponivel=False),
        DESFECHO,
        None,
        o.REQ_ENVIADO,
    ),
    ("3_sem_rascunho", disp(disponivel=False), DESFECHO, None, o.REQ_NAO_ENVIADO),
    (
        "3_com_rascunho",
        disp(status=req_nomes.RASCUNHO, disponivel=False),
        DESFECHO,
        None,
        o.REQ_NAO_ENVIADO,
    ),
    ("3a", disp(final="ENCERRADO"), None, o.PROCESSO, o.REQ_NAO_ENVIADO_ENCERRADO),
    (
        "3a_com_o_prazo",
        disp(final="CANCELADO", prazo=True),
        None,
        o.PROCESSO,
        o.REQ_NAO_ENVIADO_ENCERRADO,
    ),
    ("4_sem_rascunho", disp(prazo=True), None, o.PRAZO, o.REQ_NAO_ENVIADO_ATE_O_PRAZO),
    (
        "4_com_rascunho",
        disp(status=req_nomes.RASCUNHO, prazo=True),
        None,
        o.PRAZO,
        o.REQ_NAO_ENVIADO_ATE_O_PRAZO,
    ),
    ("5_disponivel", disp(), None, None, o.REQ_A_PREENCHER),
    ("5_em_preenchimento", disp(status=req_nomes.RASCUNHO), None, None, o.REQ_A_PREENCHER),
    ("6", disp(disponivel=False), None, None, o.REQ_SEM_CHAMADO),
]


@pytest.mark.parametrize(
    ("disponibilidade", "desfecho", "causa", "esperado"),
    [linha[1:] for linha in LINHAS],
    ids=[linha[0] for linha in LINHAS],
)
def test_as_sete_linhas_do_requerimento(disponibilidade, desfecho, causa, esperado):
    assert o.estado_do_requerimento(disponibilidade, desfecho=desfecho, causa=causa) == esperado


def test_o_pedido_e_nao_enviado_nunca_vira_nao_pedido_depois_do_desfecho():
    """D-016: depois do desfecho a política diz "ainda indisponível" — e isso não apaga o pedido."""
    for status in ("", req_nomes.RASCUNHO):
        politica = disp(status=status, disponivel=False)
        assert politica.estado_de_leitura == req_nomes.AINDA_INDISPONIVEL
        assert o.estado_do_requerimento(politica, desfecho=DESFECHO) == o.REQ_NAO_ENVIADO


def test_o_processo_nao_alcanca_o_requerimento_na_inscricao():
    politica = disp(req_nomes.NA_INSCRICAO, prazo=True)
    assert o.estado_do_requerimento(politica, desfecho=None, causa=o.PROCESSO) == (
        o.REQ_NAO_ENVIADO_ATE_O_PRAZO
    )


@pytest.mark.parametrize("momento", list(MOMENTOS))
@pytest.mark.parametrize("linha", LINHAS, ids=[linha[0] for linha in LINHAS])
def test_o_requerimento_so_e_tarefa_com_a_chamada_aberta(linha, momento):
    _, politica, _, _, _ = linha
    projetada = projetar([lido(nomes.ITEM_RECEBIDO)], momento, requerimento=politica)
    tarefa = any(t.requerimento for t in projetada.tarefas)
    assert tarefa == (momento == o.ABERTA and projetada.requerimento == o.REQ_A_PREENCHER)
    assert projetada.totais["requerimento"] == tarefa


# --- A ordem e os totais (FR-3726, FR-3727, FR-3723) --------------------------------------------


def test_a_ordem_e_pendencia_depois_o_que_falta_depois_o_requerimento():
    falta = lido(nomes.ITEM_A_APRESENTAR, nome="Certidão", ordem=1)
    corrigir = lido(nomes.ITEM_PENDENTE, nome="Histórico", ordem=2)
    falta_com_motivo = lido(nomes.ITEM_PENDENTE, apresentado=False, nome="Residência", ordem=3)
    com_a_comissao = lido(nomes.ITEM_RECEBIDO, nome="Identidade", ordem=4)

    projetada = projetar([falta, corrigir, falta_com_motivo, com_a_comissao], requerimento=disp())

    assert [t.texto for t in projetada.tarefas] == [
        "Histórico",
        "Residência",
        "Certidão",
        "Requerimento de Matrícula",
    ]
    assert [t.motivo for t in projetada.tarefas[:2]] == [MOTIVO, MOTIVO]
    assert projetada.primeira_ancora == f"item-{corrigir.item.id}"
    # Um link só, que só navega: "Ver o que preciso fazer" (121, FR-3863, revendo a FR-3736 da 118).
    assert projetada.acao == o.AcaoDaChamada("Ver o que preciso fazer", f"item-{corrigir.item.id}")
    assert projetada.frase_de_estado == (
        "Você ainda precisa corrigir 1 documento, enviar 2 documentos e preencher o "
        "Requerimento de Matrícula."
    )


def test_o_facultativo_fica_fora_dos_totais_e_da_frase():
    projetada = projetar(
        [
            lido(nomes.ITEM_RECEBIDO),
            lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False),
            lido(nomes.ITEM_PENDENTE, obrigatorio=False),
            lido(nomes.ITEM_RECEBIDO, obrigatorio=False),
        ]
    )

    assert projetada.totais == {
        "a_corrigir": 0,
        "a_enviar": 0,
        "com_a_comissao": 1,
        "conferidos": 0,
        "requerimento": False,
    }
    assert projetada.tarefas == ()
    assert projetada.frase_de_estado == o.NADA_POR_ENQUANTO
    assert projetada.frase_de_conclusao == o.FRASE_DE_CONCLUSAO
    # O opcional continua alcançável para envio sem tarefa nenhuma (FR-3723, D-018).
    assert len(projetada.opcionais_a_enviar) == 2
    assert all(item.pode_enviar for item in projetada.opcionais_a_enviar)
    assert projetada.tem_bloco_que_falta


def test_so_o_requerimento_a_preencher_leva_ao_requerimento():
    """121, FR-3863, SC-1151: o Requerimento, quando ele é a única tarefa. Antes da 121 o botão
    sumia justamente aí, porque a âncora só olhava documentos."""
    projetada = projetar([lido(nomes.ITEM_RECEBIDO)], requerimento=disp())
    assert projetada.frase_de_estado == "Você ainda precisa preencher o Requerimento de Matrícula."
    assert projetada.acao == o.AcaoDaChamada("Ver o que preciso fazer", "requerimento-a-preencher")
    assert projetada.requerimento_a_preencher_na_chamada
    assert projetada.tem_bloco_que_falta
    assert projetada.frase_de_conclusao == ""


def test_so_o_que_falta_enviar_leva_ao_primeiro_cartao():
    pendente = lido(nomes.ITEM_PENDENTE, apresentado=False)
    projetada = projetar([pendente])
    assert projetada.frase_de_estado == "Você ainda precisa enviar 1 documento."
    assert projetada.acao.ancora == f"item-{pendente.item.id}"


# --- Os textos literais (FR-3746) ---------------------------------------------------------------

# (caso, obrigatório) → as quatro colunas: aberta, prazo, Processo, decidida.
TEXTOS = {
    ("a_apresentar", True): (
        "Falta enviar.",
        "Não enviado até o prazo.",
        "Não enviado.",
        "Não enviado.",
    ),
    ("pendente_com_envio", True): (
        "Precisa de correção: Falta a página 2. Envie um novo arquivo até 09/11/2026, às 13h27.",
        "Precisava de correção: Falta a página 2. Nenhum novo arquivo foi enviado até o prazo.",
        "Precisava de correção: Falta a página 2.",
        "Precisava de correção: Falta a página 2.",
    ),
    ("pendente_sem_envio", True): (
        "Precisa de correção: Falta a página 2. Envie o arquivo até 09/11/2026, às 13h27.",
        "Precisava de correção: Falta a página 2. Nenhum arquivo foi enviado até o prazo.",
        "Precisava de correção: Falta a página 2.",
        "Precisava de correção: Falta a página 2.",
    ),
    ("recebido_portal", True): (
        "Recebido em 04/11/2026, às 09h05. A comissão vai conferir; você não precisa fazer nada "
        "agora.",
        "Recebido em 04/11/2026, às 09h05. A comissão vai conferir.",
        "Recebido em 04/11/2026, às 09h05; não foi conferido antes do encerramento do Processo.",
        "Enviado em 04/11/2026; não foi conferido antes do resultado.",
    ),
    ("recebido_inscricao", True): (
        "Você já enviou este documento na inscrição, em 02/03/2026. Não precisa enviar de novo. "
        "A comissão vai conferir.",
        "Enviado na inscrição, em 02/03/2026. A comissão vai conferir.",
        "Enviado na inscrição, em 02/03/2026; não foi conferido antes do encerramento do Processo.",
        "Enviado na inscrição, em 02/03/2026; não foi conferido antes do resultado.",
    ),
    ("recebido_chamada", True): (
        "Aproveitado da chamada anterior, enviado em 02/03/2026. Não precisa enviar de novo. A "
        "comissão vai conferir de novo.",
        "Aproveitado da chamada anterior, enviado em 02/03/2026. A comissão vai conferir de novo.",
        "Aproveitado da chamada anterior, enviado em 02/03/2026; não foi conferido antes do "
        "encerramento do Processo.",
        "Aproveitado da chamada anterior, enviado em 02/03/2026; não foi conferido antes do "
        "resultado.",
    ),
    # 154, FR-6213: o nome da gestão abre o cartão (D-003); o prazo vencido, sozinho, mantém
    # "aguardando"; sem conferência possível, o passado (D-005).
    ("complementado", True): (
        "Reenviado — aguardando nova conferência. Novo arquivo recebido em 04/11/2026, às 09h05, "
        "depois da correção pedida.",
        "Reenviado — aguardando nova conferência. Novo arquivo recebido em 04/11/2026, às 09h05, "
        "depois da correção pedida.",
        "Reenviado em 04/11/2026; não foi conferido antes do encerramento do Processo.",
        "Reenviado em 04/11/2026; não foi conferido antes do resultado.",
    ),
    ("conforme", True): ("Conferido: de acordo com o Edital.",) * 4,
    ("conforme_inscricao", True): (
        "Conferido: de acordo com o Edital. É o arquivo enviado na inscrição, em 02/03/2026.",
    )
    * 4,
    ("nao_se_aplica", True): ("Não se aplica: Concluiu no Ifes.",) * 4,
    ("a_apresentar", False): (
        "Opcional: envie se quiser.",
        "Opcional, não enviado.",
        "Opcional, não enviado.",
        "Opcional, não enviado.",
    ),
    ("pendente_com_envio", False): (
        "Opcional. A comissão apontou: Falta a página 2. Se quiser, envie um novo arquivo até "
        "09/11/2026, às 13h27.",
        "Opcional. A comissão apontou: Falta a página 2.",
        "Opcional. A comissão apontou: Falta a página 2.",
        "Opcional. A comissão apontou: Falta a página 2.",
    ),
    ("pendente_sem_envio", False): (
        "Opcional. A comissão apontou: Falta a página 2. Se quiser, envie o arquivo até "
        "09/11/2026, às 13h27.",
        "Opcional. A comissão apontou: Falta a página 2.",
        "Opcional. A comissão apontou: Falta a página 2.",
        "Opcional. A comissão apontou: Falta a página 2.",
    ),
}


@pytest.mark.parametrize(("caso", "obrigatorio"), list(TEXTOS), ids=lambda v: str(v))
def test_o_texto_de_cada_celula(caso, obrigatorio):
    (estado, origem, apresentado), _ = CASOS[caso]
    for coluna, momento in enumerate(MOMENTOS):
        item = lido(estado, obrigatorio=obrigatorio, origem=origem, apresentado=apresentado)
        (projetado,) = projetar([item], momento).itens
        assert projetado.texto == TEXTOS[(caso, obrigatorio)][coluna], momento


def test_o_facultativo_reenviado_usa_o_mesmo_nome_com_o_selo():
    """154, caso-limite *Facultativo reenviado*."""
    (item,) = projetar([lido(nomes.ITEM_COMPLEMENTADO, obrigatorio=False)]).itens
    assert item.texto.startswith(vocabulario_dos_documentos.REENVIADO + ". ")
    assert item.selos == (o.SELO_AGUARDANDO, o.SELO_OPCIONAL)


def test_o_facultativo_recebido_usa_a_linha_do_estado_com_o_selo():
    (item,) = projetar([lido(nomes.ITEM_RECEBIDO, obrigatorio=False)]).itens
    assert item.texto.startswith("Recebido em 04/11/2026")
    assert item.selos == (o.SELO_AGUARDANDO, o.SELO_OPCIONAL)


@pytest.mark.parametrize(
    ("estado", "vencimento"),
    [(nomes.CONVOCADO_PRAZO_NAO_INICIADO, VENCIMENTO), (nomes.CONVOCADO_PRAZO_EM_CURSO, None)],
    ids=["prazo_nao_iniciado", "sem_vencimento"],
)
def test_sem_prazo_correndo_nenhuma_frase_diz_ate(estado, vencimento):
    """K2 e a convocação sem vencimento: a regra prevalece sobre toda menção ao prazo (FR-3749)."""
    so_opcional = projetar(
        [lido(nomes.ITEM_PENDENTE, obrigatorio=False)], estado=estado, vencimento=vencimento
    )
    com_tarefa = projetar(
        [
            lido(nomes.ITEM_PENDENTE),
            lido(nomes.ITEM_PENDENTE, apresentado=False),
            lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False),
        ],
        estado=estado,
        vencimento=vencimento,
    )
    for projetada in (so_opcional, com_tarefa):
        frases = [item.texto for item in projetada.itens] + [
            projetada.frase_de_estado,
            projetada.frase_de_conclusao,
            projetada.frase_do_opcional,
        ]
        assert not [f for f in frases if " até " in f], frases
        assert projetada.prazo == ""
    if estado == nomes.CONVOCADO_PRAZO_NAO_INICIADO:
        assert com_tarefa.frase_do_prazo == (o.PRAZO_NAO_INICIADO, o.JA_PODE_ENVIAR)
        assert (
            so_opcional.frase_do_opcional
            == "Se quiser, você ainda pode enviar o documento opcional."
        )
    else:
        assert com_tarefa.frase_do_prazo == (o.SEM_PRAZO_REGISTRADO,)


def test_prazo_nao_iniciado_sem_nada_a_enviar_nao_diz_que_ja_pode_enviar():
    projetada = projetar([lido(nomes.ITEM_RECEBIDO)], estado=nomes.CONVOCADO_PRAZO_NAO_INICIADO)
    assert projetada.frase_do_prazo == (o.PRAZO_NAO_INICIADO,)


def test_a_frase_de_conclusao_com_e_sem_opcional():
    sem = projetar([lido(nomes.ITEM_RECEBIDO)])
    com = projetar([lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False)])

    assert (sem.frase_de_estado, sem.frase_de_conclusao, sem.frase_do_opcional) == (
        "Nada por enquanto.",
        "Você não tem mais documentos para enviar agora. A comissão ainda vai concluir a análise.",
        "",
    )
    assert com.frase_do_opcional == (
        "Se quiser, você ainda pode enviar o documento opcional até 09/11/2026, às 13h27."
    )


def test_com_tarefa_nao_ha_frase_de_conclusao():
    projetada = projetar([lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_A_APRESENTAR)])
    assert projetada.frase_de_conclusao == ""


# --- O fechamento (FR-3741, FR-3748) ------------------------------------------------------------


def test_o_vencido_usa_o_nucleo_e_inclui_o_requerimento_no_resumo():
    projetada = projetar(
        [
            lido(nomes.ITEM_PENDENTE, nome="Histórico"),
            lido(nomes.ITEM_A_APRESENTAR, nome="Certidão"),
        ],
        o.ENCERRADA_PELO_PRAZO,
        requerimento=disp(prazo=True),
    )

    assert projetada.titulo_do_fechamento == "O prazo terminou"
    assert projetada.frase_do_fechamento == (
        "O prazo terminou em 09/11/2026, às 13h27. O fim do prazo não decide nada sozinho: quem "
        "registra o resultado é a comissão.",
        "Não é mais possível enviar documentos nem o Requerimento de Matrícula pelo portal.",
        "Se você enviou algo que não aparece aqui, fale com o atendimento: "
        "atendimento@ifes.edu.br.",
    )
    assert projetada.titulo_do_resumo == "Até o prazo, ficou assim"
    assert o.REQUERIMENTO_NAO_ENVIADO_ATE_O_PRAZO in projetada.resumo
    assert (
        "Até o prazo, ficaram sem envio: Histórico (correção pedida), Certidão e Requerimento"
        in (projetada.frase_de_estado)
    )


@pytest.mark.parametrize(
    ("status", "participio"), [("ENCERRADO", "encerrado"), ("CANCELADO", "cancelado")]
)
def test_o_processo_nao_diz_prazo_vencido_nem_promete_conferencia(status, participio):
    """M: a escrita fechada pelo Processo, com o prazo ainda correndo (D-015, D-020)."""
    projetada = projetar(
        [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_A_APRESENTAR)],
        o.ENCERRADA_PELO_PROCESSO,
        requerimento=disp(final=status),
        final=status,
    )
    tudo = " ".join(
        (projetada.frase_de_estado, *projetada.frase_do_fechamento, *projetada.resumo)
        + tuple(item.texto for item in projetada.itens)
        + tuple(selo for item in projetada.itens for selo in item.selos)
    ).lower()

    assert projetada.titulo_do_fechamento == "O envio pelo portal está encerrado"
    assert projetada.frase_do_fechamento[0] == (
        f"Este Processo Seletivo foi {participio}, e não é mais possível enviar documentos nem o "
        "Requerimento de Matrícula pelo portal."
    )
    assert o.REQUERIMENTO_NAO_ENVIADO_ENCERRADO in projetada.resumo
    for proibida in ("prazo terminou", "vai conferir", "aguardando", "vai decidir", "venceu"):
        assert proibida not in tudo


def test_decidida_sem_aguardando_nem_convite():
    projetada = projetar(
        [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_A_APRESENTAR), lido(nomes.ITEM_PENDENTE)],
        o.DECIDIDA,
        requerimento=disp(disponivel=False),
    )
    tudo = " ".join(
        tuple(item.texto for item in projetada.itens)
        + tuple(selo for item in projetada.itens for selo in item.selos)
    ).lower()

    for proibida in ("aguardando conferência", "falta enviar", "envie", "precisa de correção"):
        assert proibida not in tudo
    assert projetada.linha_do_requerimento == "Requerimento de Matrícula: não enviado."


# --- A linguagem (FR-3751, SC-1118) -------------------------------------------------------------

PROIBIDOS = (
    r"apto para formaliza",
    r"encaminhad",
    r"matriculad",
    r"matr[íi]cula efetivada",
    r"bolsa concedida",
    r"vinculad",
    r"contratad",
    r"autêntic",
    r"\baprovad",
    r"\batendid",
    r"\baceit[oa]\b",
    r"enviou tudo",
    r"tudo certo",
    r"\bconcluíd",
)


@pytest.mark.parametrize("momento", list(MOMENTOS))
def test_nenhuma_frase_afirma_o_que_ninguem_decidiu(momento):
    itens = [
        lido(estado, obrigatorio=obrigatorio, origem=origem, apresentado=apresentado)
        for (estado, origem, apresentado), _ in CASOS.values()
        for obrigatorio in (True, False)
    ]
    for requerimento in (disp(), disp(status=req_nomes.ENVIADO), disp(prazo=True), disp(final="X")):
        projetada = projetar(itens, momento, requerimento=requerimento)
        frases = [
            projetada.frase_de_estado,
            projetada.frase_de_conclusao,
            projetada.frase_do_opcional,
            *projetada.frase_do_prazo,
            *projetada.frase_do_fechamento,
            *projetada.resumo,
            projetada.linha_do_requerimento,
            *(item.texto for item in projetada.itens),
            *(selo for item in projetada.itens for selo in item.selos),
        ]
        lidas = " ".join(frases).lower()
        assert [p for p in PROIBIDOS if re.search(p, lidas)] == [], momento


def test_a_frase_do_aceite_diz_o_que_vem_depois_e_nao_repete_a_frase_simples():
    """O que o registro não é foi para a frase simples do aceite (156, FR-6406)."""
    from processo_seletivo.portal import desfecho

    assert o.ACEITE == "Os próximos passos são os que o Edital indica."
    assert desfecho.NAO_E_MATRICULA == "Este registro não é matrícula, bolsa nem contrato."
    assert desfecho.NAO_E_MATRICULA not in o.ACEITE


def test_o_formato_do_prazo_e_um_so():
    assert o.ate(VENCIMENTO) == "até 09/11/2026, às 13h27"
    assert o.ate(VENCIMENTO + timedelta(hours=10, minutes=33)) == "até 10/11/2026, às 00h00"
    assert o.ate(None) == ""


# --- Sem relógio e sem banco (FR-3721, FR-3734) -------------------------------------------------


@pytest.mark.django_db
def test_a_projecao_nao_consulta_o_banco(django_assert_num_queries):
    itens = [
        lido(estado, obrigatorio=obrigatorio, origem=origem, apresentado=apresentado)
        for (estado, origem, apresentado), _ in CASOS.values()
        for obrigatorio in (True, False)
    ]
    with django_assert_num_queries(0):
        for momento in MOMENTOS:
            projetar(itens, momento, requerimento=disp())
        o.linha_informativa_do_requerimento(disp(prazo=True), desfecho=None)


# --- A chamada da 121 (FR-3858 a FR-3870) -------------------------------------------------------


def test_data_hora_e_ate_delegam_ao_prazo_apresentado(settings):
    """121, FR-3873: as funções da 118 passam pela função única, e dizem o mesmo que antes."""
    from unittest import mock

    settings.TIME_ZONE = "America/Sao_Paulo"
    with mock.patch.object(o, "apresentar", wraps=o.apresentar) as apresentar:
        assert o.data(VENCIMENTO) == "09/11/2026"
        assert o.hora(VENCIMENTO) == "13h27"
        assert o.ate(VENCIMENTO) == "até 09/11/2026, às 13h27"
    assert apresentar.call_count == 3


@pytest.mark.parametrize(
    ("momento", "titulo"),
    [
        (o.ABERTA, "Você tem uma convocação!"),
        (o.ENCERRADA_PELO_PRAZO, "O prazo desta convocação terminou"),
        (o.ENCERRADA_PELO_PROCESSO, "O envio pelo portal está encerrado"),
        (o.DECIDIDA, "Resultado da sua convocação"),
    ],
)
def test_o_titulo_por_estado(momento, titulo):
    """FR-3858: o título diz o estado, e nenhum promete vaga, matrícula nem contratação."""
    projetada = projetar([lido(nomes.ITEM_A_APRESENTAR)], momento, requerimento=disp())

    assert projetada.titulo == titulo
    for proibido in ("matrícula", "matriculad", "vaga", "contrat", "bolsa"):
        assert proibido not in titulo.lower()


@pytest.mark.parametrize(
    ("obrigatorio", "requerimento", "etapa"),
    [
        (
            True,
            True,
            "Nesta etapa, você envia seus documentos e o Requerimento de Matrícula para a "
            "comissão conferir.",
        ),
        (True, False, "Nesta etapa, você envia seus documentos para a comissão conferir."),
        (
            False,
            True,
            "Nesta etapa, você envia o Requerimento de Matrícula e pode enviar documento "
            "opcional para a comissão conferir.",
        ),
        (
            False,
            False,
            "Nesta etapa, você pode enviar documento opcional para a comissão conferir.",
        ),
    ],
)
def test_a_etapa_descreve_a_chamada_e_nao_o_estado(obrigatorio, requerimento, etapa):
    """FR-3860: igual antes e depois de qualquer envio, e nunca no imperativo."""
    disponibilidade = disp() if requerimento else None
    antes = projetar(
        [lido(nomes.ITEM_A_APRESENTAR, obrigatorio=obrigatorio)], requerimento=disponibilidade
    )
    depois = projetar(
        [lido(nomes.ITEM_RECEBIDO, obrigatorio=obrigatorio)],
        requerimento=disp(status=req_nomes.ENVIADO) if requerimento else None,
    )

    assert antes.etapa == depois.etapa == etapa
    assert not re.search(r"\b(envie|apresente)\b", etapa.lower())


def test_o_requerimento_na_inscricao_nao_entra_na_etapa():
    projetada = projetar([lido(nomes.ITEM_A_APRESENTAR)], requerimento=disp(req_nomes.NA_INSCRICAO))

    assert projetada.etapa == "Nesta etapa, você envia seus documentos para a comissão conferir."
    assert projetada.ressalva == o.RESSALVA_DA_MATRICULA, "o Edital ainda pede o Requerimento"


def test_a_ressalva_so_fala_de_matricula_com_o_requerimento():
    """D-003: num Edital de bolsista, "ainda não é a matrícula" seria falso."""
    com = projetar([lido(nomes.ITEM_A_APRESENTAR)], requerimento=disp())
    sem = projetar([lido(nomes.ITEM_A_APRESENTAR)])

    assert com.ressalva == (
        "Esta convocação ainda não é a matrícula: a comissão confere o que você enviar e registra "
        "o resultado."
    )
    assert sem.ressalva == (
        "Esta convocação ainda não é o resultado: a comissão confere o que você enviar e registra "
        "o resultado."
    )


def test_o_andamento_conta_so_obrigatorios_e_sem_o_requerimento():
    """FR-3865, D-004: sem o Requerimento, sem barra, e "a corrigir" só quando houver."""
    sem_corrigir = projetar(
        [
            lido(nomes.ITEM_A_APRESENTAR),
            lido(nomes.ITEM_RECEBIDO),
            lido(nomes.ITEM_CONFORME),
            lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False),
        ],
        requerimento=disp(),
    )
    com_corrigir = projetar([lido(nomes.ITEM_PENDENTE), lido(nomes.ITEM_A_APRESENTAR)])

    assert sem_corrigir.andamento == (
        ("A enviar", 1),
        ("Aguardando conferência", 1),
        ("Conferidos", 1),
    )
    assert com_corrigir.andamento[0] == ("A corrigir", 1)
    assert all("%" not in rotulo for rotulo, _ in com_corrigir.andamento)


class TestAAcao:
    """FR-3863, SC-1151: um link, *"Ver o que preciso fazer"*, à primeira tarefa da FR-3726."""

    def test_a_pendente_antes_da_que_falta(self):
        falta = lido(nomes.ITEM_A_APRESENTAR, ordem=1)
        pendente = lido(nomes.ITEM_PENDENTE, ordem=2)

        projetada = projetar([falta, pendente], requerimento=disp())

        assert projetada.acao == o.AcaoDaChamada(
            "Ver o que preciso fazer", f"item-{pendente.item.id}"
        )

    def test_a_primeira_a_enviar(self):
        primeira = lido(nomes.ITEM_A_APRESENTAR, ordem=1)

        projetada = projetar([primeira, lido(nomes.ITEM_A_APRESENTAR, ordem=2)])

        assert projetada.acao.ancora == f"item-{primeira.item.id}"
        assert not projetada.acao.rotulo.startswith("Enviar")

    def test_o_requerimento_quando_e_a_unica(self):
        projetada = projetar([lido(nomes.ITEM_CONFORME)], requerimento=disp())

        assert projetada.acao.ancora == "requerimento-a-preencher"

    def test_sem_tarefa_sem_acao(self):
        projetada = projetar([lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_CONFORME)])

        assert projetada.acao is None
        assert projetada.resumo_do_que_falta == o.FRASE_DE_CONCLUSAO

    @pytest.mark.parametrize(
        "momento", [o.ENCERRADA_PELO_PRAZO, o.ENCERRADA_PELO_PROCESSO, o.DECIDIDA]
    )
    def test_fechada_nao_tem_nada_da_chamada_aberta(self, momento):
        """FR-3867: nem etapa, contagem, ação, consequência, ressalva nem andamento."""
        projetada = projetar([lido(nomes.ITEM_A_APRESENTAR)], momento, requerimento=disp())

        assert (projetada.etapa, projetada.cartao, projetada.acao) == ("", None, None)
        assert (projetada.ressalva, projetada.andamento, projetada.resumo_do_que_falta) == (
            "",
            (),
            "",
        )


class TestOCartaoDoPrazo:
    """FR-3861, FR-3869, FR-3874."""

    def test_a_data_o_dia_e_a_contagem(self):
        agora = VENCIMENTO - timedelta(days=3)

        cartao = projetar([lido(nomes.ITEM_A_APRESENTAR)], agora=agora).cartao

        assert cartao.rotulo == "Prazo desta convocação"
        assert cartao.data == "até 09/11/2026, às 13h27"
        assert cartao.linha == "segunda-feira · faltam 3 dias"
        assert cartao.corrigida == "" and cartao.frases == ()

    def test_o_prazo_nao_iniciado_diz_so_a_frase(self):
        """Cenário K: sem data, sem dia da semana e sem contagem (FR-3749 da 118)."""
        projetada = projetar(
            [lido(nomes.ITEM_A_APRESENTAR)],
            requerimento=disp(),
            estado=nomes.CONVOCADO_PRAZO_NAO_INICIADO,
            agora=VENCIMENTO - timedelta(days=3),
        )

        assert projetada.titulo == "Você tem uma convocação!"
        assert projetada.cartao == o.CartaoDoPrazo(frases=(o.PRAZO_NAO_INICIADO, o.JA_PODE_ENVIAR))

    def test_sem_vencimento(self):
        cartao = projetar([lido(nomes.ITEM_A_APRESENTAR)], vencimento=None).cartao

        assert cartao == o.CartaoDoPrazo(frases=(o.SEM_PRAZO_REGISTRADO,))

    def test_a_correcao_e_dita_no_cartao(self):
        cartao = projetar(
            [lido(nomes.ITEM_A_APRESENTAR)], agora=VENCIMENTO - timedelta(days=3), corrigida=True
        ).cartao

        assert cartao.corrigida == "Convocação corrigida: este é o prazo válido."

    def test_so_facultativo_segue_a_118(self):
        """Caso-limite: a etapa da FR-3860 e o bloco *O que falta* só com o opcional."""
        projetada = projetar([lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False)])

        assert projetada.etapa.startswith("Nesta etapa, você pode enviar documento opcional")
        assert projetada.tem_bloco_que_falta and projetada.acao is None
        assert projetada.convite_ao_opcional == o.CONVITE_AO_OPCIONAL


def _comunicacao(resultado, quando=None, forma="INDIVIDUAL_MESSAGE", referencia=""):
    return SimpleNamespace(
        resultado=resultado,
        forma=forma,
        enviado_em=quando,
        referencia_da_publicacao=referencia,
    )


def _anterior(*comunicacoes, vencimento=VENCIMENTO):
    return SimpleNamespace(
        vencimento=vencimento, comunicacoes=SimpleNamespace(all=lambda: list(comunicacoes))
    )


class TestASubstituida:
    """FR-3869, R-008: a imediatamente anterior, nos três textos, sem motivo nem "novo prazo".

    Na mensagem, *"Enviada em"*, e não *"Comunicada em"*, desde a `125` (D-008): a palavra do canal.
    """

    def test_comunicada(self):
        enviada = _comunicacao("ENVIADA", RECEBIDO_EM)

        assert o.linha_da_substituida(_anterior(enviada)) == (
            "Enviada em 04/11/2026, às 09h05, com prazo até 09/11/2026, às 13h27. Esse prazo "
            "não vale mais."
        )

    def test_por_publicacao(self):
        publicada = _comunicacao(
            "ENVIADA", RECEBIDO_EM, forma="PUBLICATION", referencia="ifes.edu.br/editais, 04/11"
        )

        assert o.linha_da_substituida(_anterior(publicada)) == (
            "Publicada em ifes.edu.br/editais, 04/11, com prazo até 09/11/2026, às 13h27. Esse "
            "prazo não vale mais."
        )

    def test_nao_comunicada(self):
        """D-008: com A enviada, B falhada e C vigente, a linha descreve **B**."""
        b = _anterior(_comunicacao("FALHA"))

        assert o.linha_da_substituida(b) == (
            "Não comunicada. O prazo registrado era até 09/11/2026, às 13h27, e não vale mais."
        )

    def test_a_ultima_enviada_da_anterior(self):
        anterior = _anterior(
            _comunicacao("ENVIADA", RECEBIDO_EM),
            _comunicacao("FALHA"),
            _comunicacao("ENVIADA", RECEBIDO_EM + timedelta(days=1)),
        )

        assert o.linha_da_substituida(anterior).startswith("Enviada em 05/11/2026")

    def test_nada_de_motivo_nem_novo_prazo(self):
        for anterior in (_anterior(), _anterior(_comunicacao("ENVIADA", RECEBIDO_EM))):
            linha = o.linha_da_substituida(anterior).lower()
            for proibido in ("motivo", "novo prazo", "prorrogação"):
                assert proibido not in linha

    def test_sem_anterior_nao_ha_linha(self):
        assert o.linha_da_substituida(None) == ""


class TestAConfirmacaoDoEnvio:
    """FR-3870, D-010: o documento e a data, "o arquivo aguarda", e a próxima tarefa."""

    def _enviado(self):
        recebido = lido(nomes.ITEM_RECEBIDO, nome="Certidão de nascimento ou casamento", ordem=1)
        apresentacao = recebido.apresentacoes[0]
        return recebido, apresentacao

    def test_com_tarefa_restante(self):
        recebido, apresentacao = self._enviado()
        falta = lido(nomes.ITEM_A_APRESENTAR, nome="Histórico escolar", ordem=2)
        projetada = projetar([recebido, falta])

        confirmacao = o.confirmacao_do_envio(
            projetada, item_id=recebido.item.id, apresentacao_id=apresentacao.id, ja_recebido=False
        )

        assert confirmacao.frase == (
            "Recebemos: Certidão de nascimento ou casamento, em 04/11/2026, às 09h05. O arquivo "
            "aguarda a conferência da comissão."
        )
        assert confirmacao.proxima.texto == "Histórico escolar"
        assert confirmacao.proxima_ancora == f"item-{falta.item.id}"
        assert confirmacao.rotulo == "Próxima tarefa:"

    def test_sem_tarefa_restante_a_conclusao(self):
        recebido, apresentacao = self._enviado()

        confirmacao = o.confirmacao_do_envio(
            projetar([recebido]),
            item_id=recebido.item.id,
            apresentacao_id=apresentacao.id,
            ja_recebido=False,
        )

        assert confirmacao.proxima is None
        assert confirmacao.conclusao == o.FRASE_DE_CONCLUSAO

    def test_o_mesmo_arquivo(self):
        recebido, apresentacao = self._enviado()

        confirmacao = o.confirmacao_do_envio(
            projetar([recebido, lido(nomes.ITEM_A_APRESENTAR)]),
            item_id=recebido.item.id,
            apresentacao_id=apresentacao.id,
            ja_recebido=True,
        )

        assert (confirmacao.frase, confirmacao.proxima) == (
            "Este arquivo já tinha sido recebido.",
            None,
        )

    @pytest.mark.parametrize(
        "momento", [o.ENCERRADA_PELO_PRAZO, o.ENCERRADA_PELO_PROCESSO, o.DECIDIDA]
    )
    def test_fechada_entre_o_envio_e_a_volta_nao_conclui_nada(self, momento):
        """O prazo fechou depois do envio, com documento ainda sem envio: a confirmação diz o que
        foi recebido, e nem próxima tarefa nem *"não tem mais documentos para enviar"*."""
        recebido, apresentacao = self._enviado()
        projetada = projetar([recebido, lido(nomes.ITEM_A_APRESENTAR)], momento)

        confirmacao = o.confirmacao_do_envio(
            projetada,
            item_id=recebido.item.id,
            apresentacao_id=apresentacao.id,
            ja_recebido=False,
        )

        assert confirmacao.frase.startswith("Recebemos: Certidão de nascimento ou casamento")
        assert (confirmacao.proxima, confirmacao.conclusao) == (None, "")

    def test_nunca_aceito_aprovado_conferido_nem_atendido(self):
        recebido, apresentacao = self._enviado()
        confirmacao = o.confirmacao_do_envio(
            projetar([recebido]),
            item_id=recebido.item.id,
            apresentacao_id=apresentacao.id,
            ja_recebido=False,
        )
        lida = f"{confirmacao.frase} {confirmacao.conclusao}".lower()

        for proibido in ("aceito", "aprovado", "conferido", "atendido"):
            assert proibido not in lida


class TestAConfirmacaoDoLote:
    """150, FR-5608: "Recebemos R de N", cada recebido, e os recusados ligados aos cartões."""

    def _envio(self, lido_, *, ja_recebido=False):
        return {
            "item_id": lido_.item.id,
            "apresentacao_id": lido_.apresentacoes[0].id,
            "ja_recebido": ja_recebido,
        }

    def test_com_um_so_e_a_confirmacao_de_hoje(self):
        recebido = lido(nomes.ITEM_RECEBIDO, nome="Certidão", ordem=1)
        projetada = projetar([recebido, lido(nomes.ITEM_A_APRESENTAR, ordem=2)])

        lote = o.confirmacao_do_lote(projetada, envios=[self._envio(recebido)], total=1)

        assert lote == o.confirmacao_do_envio(projetada, **self._envio(recebido))
        assert "de 1" not in lote.frase

    def test_dois_de_tres_com_um_recusado(self):
        certidao = lido(nomes.ITEM_RECEBIDO, nome="Certidão", ordem=1)
        residencia = lido(nomes.ITEM_RECEBIDO, nome="Residência", ordem=2)
        historico = lido(nomes.ITEM_A_APRESENTAR, nome="Histórico", ordem=3)
        projetada = projetar([certidao, residencia, historico])
        recusa = {"ancora": f"item-{historico.item.id}", "frase": "É uma imagem."}

        lote = o.confirmacao_do_lote(
            projetada,
            envios=[self._envio(certidao), self._envio(residencia)],
            total=3,
            recusas=[recusa],
        )

        assert lote.frase == (
            "Recebemos 2 de 3 documentos. Os arquivos aguardam a conferência da comissão."
        )
        assert lote.recebidos == (
            "Certidão, em 04/11/2026, às 09h05.",
            "Residência, em 04/11/2026, às 09h05.",
        )
        assert lote.nao_recebidos == (("Histórico", f"item-{historico.item.id}"),)
        assert lote.rotulo_dos_nao_recebidos == "1 documento não foi recebido:"
        assert lote.proxima.texto == "Histórico", "a próxima tarefa é a de hoje, depois do último"

    def test_o_mesmo_arquivo_no_lote_e_o_plural_dos_recusados(self):
        certidao = lido(nomes.ITEM_RECEBIDO, nome="Certidão", ordem=1)
        a = lido(nomes.ITEM_A_APRESENTAR, nome="A", ordem=2)
        b = lido(nomes.ITEM_A_APRESENTAR, nome="B", ordem=3)
        recusas = [{"ancora": f"item-{x.item.id}", "frase": "x"} for x in (a, b)]

        lote = o.confirmacao_do_lote(
            projetar([certidao, a, b]),
            envios=[self._envio(certidao, ja_recebido=True)],
            total=3,
            recusas=recusas,
        )

        assert lote.frase == (
            "Recebemos 1 de 3 documentos. O arquivo aguarda a conferência da comissão."
        )
        assert lote.recebidos == ("Certidão: este arquivo já tinha sido recebido.",)
        assert lote.rotulo_dos_nao_recebidos == "2 documentos não foram recebidos:"

    def test_nunca_aceito_aprovado_conferido_nem_atendido(self):
        certidao = lido(nomes.ITEM_RECEBIDO, nome="Certidão", ordem=1)
        residencia = lido(nomes.ITEM_RECEBIDO, nome="Residência", ordem=2)

        lote = o.confirmacao_do_lote(
            projetar([certidao, residencia]),
            envios=[self._envio(certidao), self._envio(residencia)],
            total=2,
        )

        lida = " ".join([lote.frase, *lote.recebidos, lote.conclusao]).lower()
        for proibido in ("aceito", "aprovado", "conferido", "atendido"):
            assert proibido not in lida


# --- 131: o obrigatório condicional -------------------------------------------------------------


def _condicional(estado):
    """O alistamento militar, obrigatório com a condição que o Edital publicou (131)."""
    lido_ = lido(estado, nome="Certificado de alistamento militar")
    lido_.requisito["requiredWhen"] = "no caso de candidatos do sexo masculino, maiores de 18 anos"
    return lido_


def test_condicional_a_apresentar_orienta_e_nao_manda_enviar():
    """FR-4475, UX-304: "Falta enviar." pedia, a quem a condição não alcança, o que não se pede."""
    item = _condicional(nomes.ITEM_A_APRESENTAR)
    categoria = o.categoria(True, item.estado, apresentado=False)

    texto = o.texto_do_item(item, categoria, o.ABERTA, "até 10/11/2026, às 17h00")

    assert texto == (
        "Obrigatório no caso de candidatos do sexo masculino, maiores de 18 anos. Se for o seu "
        "caso, envie até 10/11/2026, às 17h00. Se não for, você não precisa enviar: a comissão "
        "registra."
    )
    assert categoria == o.A_ENVIAR


def test_condicional_fechada_a_chamada_vale_o_texto_de_antes():
    item = _condicional(nomes.ITEM_A_APRESENTAR)
    categoria = o.categoria(True, item.estado, apresentado=False)

    assert (
        o.texto_do_item(item, categoria, o.ENCERRADA_PELO_PRAZO, "") == "Não enviado até o prazo."
    )


def test_incondicional_a_apresentar_continua_falta_enviar():
    item = lido(nomes.ITEM_A_APRESENTAR)
    categoria = o.categoria(True, item.estado, apresentado=False)

    assert o.texto_do_item(item, categoria, o.ABERTA, "") == "Falta enviar."
