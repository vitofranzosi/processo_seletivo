"""O registro excedente, perguntado às versões do Edital (122, FR-3903, FR-3904, FR-3911).

**Uma pergunta, e não uma marca** (D-002 da `122`): um registro é excedente quando o recorte
dele tem papel `EXCEDENTE` na versão vigente, e a frase que o explica sai da versão que ele cita.
Nada disto se grava — a primeira Retificação do apontamento tornaria velha qualquer marca, e o
append-only impediria corrigi-la.

**Vive em `publicacoes`** porque as versões são daqui, e o domínio dos recortes
(`editais/domain/recortes.py`) é puro: recebe conteúdo, e não lê banco.

**Custo**: as versões do Edital se leem numa consulta só, e quem pergunta por vários registros passa
a lista adiante. Só as telas de histórico e as de um registro perguntam — nenhuma listagem paga.
"""

from django.utils import timezone

from processo_seletivo.editais.domain.recortes import (
    EXCEDENTE,
    OPERACIONAL,
    frase_da_origem,
    frase_do_papel_mudado,
    origem_do_registro,
    papel_do_recorte,
    retificacao_que_mudou_o_papel,
)
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


def versoes_do_edital(edital, *, at=None):
    """`[(identidade, conteudo, numero)]` em ordem de vigência, até a vigente no instante."""
    momento = at or timezone.now()
    return [
        (versao.id, versao.content, versao.source_publication.publication_order)
        for versao in VersaoConsolidada.objects.filter(edital=edital, valid_from__lte=momento)
        .select_related("source_publication")
        .order_by("valid_from", "materialized_at")
    ]


def frase_do_registro(versoes, *, perfil_id, lista_id, versao_id):
    """A frase da origem quando o registro é excedente na vigente; `""` quando é da operação."""
    if not versoes:
        return ""
    _, vigente, _ = versoes[-1]
    if papel_do_recorte(vigente, perfil_id=perfil_id, lista_id=lista_id) != EXCEDENTE:
        return ""
    origem, numero = origem_do_registro(
        versoes, perfil_id=perfil_id, lista_id=lista_id, versao_do_registro=versao_id
    )
    return frase_da_origem(origem, numero)


def frase_do_ato(ato, versoes=None):
    """A frase do ato de ordenação excedente, ou `""` (FR-3904)."""
    versoes = versoes if versoes is not None else versoes_do_edital(ato.edital)
    return frase_do_registro(
        versoes, perfil_id=ato.perfil_id, lista_id=ato.lista_id, versao_id=ato.versao_id
    )


def divergencia_de_papel(ato, conteudo_vigente, *, versoes=None):
    """A causa `papel_do_recorte`, ou `None` (122, FR-3912, contrato §3).

    Entra quando o papel na versão do ato difere do papel na vigente **e** o vigente é operacional:
    o ato foi produzido para outro universo, e o recorte de hoje precisa de ato novo. Quando o
    vigente é excedente, o ato não é deste recorte operacional — é acervo, e quem o mostra é a seção
    de histórico.
    """
    papel_hoje = papel_do_recorte(conteudo_vigente, perfil_id=ato.perfil_id, lista_id=ato.lista_id)
    papel_na_origem = papel_do_recorte(
        ato.versao.content, perfil_id=ato.perfil_id, lista_id=ato.lista_id
    )
    if papel_hoje != OPERACIONAL or papel_na_origem == papel_hoje:
        return None
    versoes = versoes if versoes is not None else versoes_do_edital(ato.edital)
    numero = retificacao_que_mudou_o_papel(
        versoes, perfil_id=ato.perfil_id, lista_id=ato.lista_id, versao_do_registro=ato.versao_id
    )
    return {"tipo": "papel_do_recorte", "descricao": frase_do_papel_mudado(numero)}


__all__ = [
    "divergencia_de_papel",
    "frase_do_ato",
    "frase_do_registro",
    "versoes_do_edital",
]
