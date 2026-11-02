"""O que a confirmação de encerrar e de cancelar diz antes do ato (113, FR-3534 a FR-3542).

**Só redige; não decide.** O que impede encerrar é a regra de `pendencias_do_edital`, a mesma que o
comando aplica sob as travas — aqui ela é lida antes, para que a tela não ofereça "Confirmar" a um
ato que vai ser recusado (`recusa_certa`). O que só se adverte vem de dois lugares: as situações que
a `113` acrescentou, da mesma regra, e as providências do relatório da `099`, **do próprio
relatório** — o que a confirmação adverte é o que o relatório dirá depois (FR-3535).

**Contagens, nunca pessoas** (FR-3540). Recurso e convocação são fato não público; a tela diz
quantos, e o caminho leva à tela dona, que decide com a permissão dela quem vê quem. As
providências da `099` são somadas no Edital inteiro, e não por Perfil, que é como o relatório
protege o Perfil pequeno.

**O caminho só a quem a tela de destino aceita** (FR-3538, a regra da `104`). A quem ela recusaria,
a frase diz a quem pedir — inteira aqui, e na forma canônica da `033` ("a quem", "à"), porque a
varredura de `test_gramatica_das_portas.py` lê o texto e não enxergaria o destinatário numa variável
do template.
"""

from dataclasses import dataclass

from django.urls import reverse

from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
from processo_seletivo.processos.application import pendencias_do_edital as p
from processo_seletivo.processos.models import Edital


@dataclass(frozen=True)
class Item:
    mensagem: str
    url: str = ""
    rotulo: str = ""
    a_quem_pedir: str = ""


@dataclass(frozen=True)
class Confirmacao:
    """Os blocos da confirmação. Vazio quando o Edital não tem situação a dizer."""

    impedimentos: tuple = ()
    advertencias: tuple = ()
    #: "Continuam depois do encerramento" ou "Serão atingidos pelo cancelamento".
    titulo_das_advertencias: str = ""
    #: Só no encerrar sem situação nenhuma: a frase da FR-3541.
    nada_impede: bool = False


TITULOS = {
    "encerrar": "Continuam depois do encerramento",
    "cancelar": "Serão atingidos pelo cancelamento",
}


def da_confirmacao(edital, ator, *, acao, agora):
    """A `Confirmacao` de `encerrar` ou `cancelar` deste Edital, para este ator."""
    # Antes da publicação não há conteúdo vigente, inscrição, resultado nem Retificação: nenhuma
    # situação desta feature existe, e o cancelamento segue como sempre foi.
    if edital.status != Edital.Status.PUBLICADO or acao not in TITULOS:
        return Confirmacao()
    situacoes = p.situacoes(edital, agora=agora, ato=acao, com_advertencias=True)
    impedimentos = tuple(
        _item(situacao, edital, ator, acao)
        for situacao in situacoes
        if situacao.especie == p.IMPEDIMENTO
    )
    advertencias = [
        _item(situacao, edital, ator, acao)
        for situacao in situacoes
        if situacao.especie == p.ADVERTENCIA
    ]
    advertencias.extend(_providencias_da_099(edital, agora))
    return Confirmacao(
        impedimentos=impedimentos,
        advertencias=tuple(advertencias),
        titulo_das_advertencias=TITULOS[acao],
        nada_impede=acao == "encerrar" and not impedimentos and not advertencias,
    )


def _item(situacao, edital, ator, acao):
    mensagem = p.frase(situacao, acao) + "."
    if acao == "cancelar":
        # No cancelamento o item diz o efeito; o caminho para resolver antes seria contraditório.
        return Item(mensagem)
    tipo = situacao.tipo
    if tipo in (p.PERIODO_EM_CURSO, p.PERIODO_SEM_TERMINO):
        from processo_seletivo.interface.acoes import pode_retificar

        if pode_retificar(edital, ator):
            return Item(mensagem, reverse("interface:retificar", args=[edital.id]), "Retificar")
        if tipo == p.PERIODO_EM_CURSO:
            return Item(mensagem, a_quem_pedir="Peça a quem elabora Retificações.")
        return Item(mensagem)
    if tipo == p.PERIODO_POR_ABRIR:
        if ator.can("edital:cancelar"):
            return Item(
                mensagem, reverse("interface:ato", args=[edital.id, "cancelar"]), "Cancelar"
            )
        return Item(mensagem, a_quem_pedir="Peça a quem pode cancelar o Edital.")
    if tipo == p.RECURSO_AGUARDANDO:
        from processo_seletivo.recursos.application import admitir

        if ator.can(admitir.PERMISSAO):
            return Item(
                mensagem, reverse("interface:recursos", args=[edital.id]), "Ir aos recursos"
            )
        return Item(mensagem, a_quem_pedir="Peça a quem julga recursos.")
    if tipo in (p.REAVALIACAO_PENDENTE, p.PROVIDENCIA_PENDENTE) and situacao.marco_id:
        if pode_gerir_comissao(ator, edital.processo) is not None:
            return Item(
                mensagem,
                reverse("interface:marco", args=[edital.id, situacao.marco_id]),
                "Conduzir o marco",
            )
        return Item(mensagem, a_quem_pedir="Peça à presidência da comissão.")
    if tipo in (p.RETIFICACAO_HOMOLOGADA, p.RETIFICACAO_EM_CURSO):
        # O detalhe da Retificação é aberto a todo ator do escopo (103): o caminho vale para todos.
        return Item(
            mensagem,
            reverse("interface:retificacao-detalhe", args=[situacao.retificacao_id]),
            "Abrir a Retificação",
        )
    return Item(mensagem)


# As providências da `099` que a confirmação repete. Recurso, reavaliação e providência de recurso
# ficam de fora: já são impedimentos, ditos pela regra da `113`, e apareceriam duas vezes.
DA_099 = (
    p.CONVOCACAO_AGUARDANDO,
    p.CONVOCACAO_VENCIDA,
    p.RESULTADO_NAO_DIVULGADO,
    p.DEFINITIVO_NAO_PUBLICADO,
    p.APURACAO_DESATUALIZADA,
)


def _providencias_da_099(edital, agora):
    """As providências do relatório, somadas no Edital, com a frase do relatório (FR-3535)."""
    from processo_seletivo.interface.relatorio_do_edital import (
        Pendencia,
        fatos_do_edital,
        texto_da_pendencia,
    )

    pendencias = [
        pendencia
        for pendencia in fatos_do_edital(edital, agora=agora).pendencias
        if pendencia.tipo in DA_099
    ]
    somadas = []
    for tipo in (p.CONVOCACAO_AGUARDANDO, p.CONVOCACAO_VENCIDA):
        do_tipo = [pendencia for pendencia in pendencias if pendencia.tipo == tipo]
        if do_tipo:
            prazos = [pendencia.ate for pendencia in do_tipo if pendencia.ate]
            somadas.append(
                Pendencia(
                    tipo,
                    None,
                    sum(pendencia.quantidade for pendencia in do_tipo),
                    ate=max(prazos) if prazos else None,
                )
            )
    vistos = set()
    for pendencia in pendencias:
        if pendencia.tipo in (p.CONVOCACAO_AGUARDANDO, p.CONVOCACAO_VENCIDA):
            continue
        # Por marco, e não por Perfil: o nome do marco é público, e o Perfil pequeno não aparece.
        chave = (pendencia.tipo, pendencia.marco)
        if chave not in vistos:
            vistos.add(chave)
            somadas.append(pendencia)
    return [Item(_frase_da_099(texto_da_pendencia(pendencia))) for pendencia in somadas]


def _frase_da_099(texto):
    return texto[:1].upper() + texto[1:] + "."
