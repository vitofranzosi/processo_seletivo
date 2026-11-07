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

import hashlib
import json
from dataclasses import dataclass, replace

from django.db.models import Exists, OuterRef
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
    #: O tipo da situação ou da providência. A confirmação do Edital não o lê; o "Encerrar Processo"
    #: (`130`) precisa dele para saber se há convocado no prazo (UX-276).
    tipo: str = ""


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
    return replace(_item_sem_tipo(situacao, edital, ator, acao), tipo=situacao.tipo)


def _item_sem_tipo(situacao, edital, ator, acao):
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
    p.CONVOCACAO_SEM_COMUNICACAO,
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
    # A convocação sem comunicação enviada é espécie própria (126, FR-4029): somada a "aguardando
    # resposta", a única lista do que falta no Edital dizia o contrário do domínio.
    da_convocacao = (p.CONVOCACAO_SEM_COMUNICACAO, p.CONVOCACAO_AGUARDANDO, p.CONVOCACAO_VENCIDA)
    for tipo in da_convocacao:
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
        if pendencia.tipo in da_convocacao:
            continue
        # Por marco, e não por Perfil: o nome do marco é público, e o Perfil pequeno não aparece.
        chave = (pendencia.tipo, pendencia.marco)
        if chave not in vistos:
            vistos.add(chave)
            somadas.append(pendencia)
    return [
        Item(_frase_da_099(texto_da_pendencia(pendencia)), tipo=pendencia.tipo)
        for pendencia in somadas
    ]


def _frase_da_099(texto):
    return texto[:1].upper() + texto[1:] + "."


# --- O "Encerrar Processo" (130) ----------------------------------------------------------------
#
# **A mesma regra e a mesma frase do Edital, Edital a Edital** (FR-4351). O encerramento do
# Processo corta o que ainda corre nos Editais finais dele — o convocado no prazo é o caso que
# motivou a feature —, e a tela diz isso antes do ato. Diz, e não impede: impedir seria outra
# decisão de domínio (a décima decisão da revisão de 06/11 da página de Processos Seletivos).

#: Os tipos da `113` que dizem algo verdadeiro num Edital já final. Os de recurso continuam a
#: correr depois do encerramento do Edital, e aqui são advertência mesmo os que lá impedem (D-003
#: da `130`).
TIPOS_NO_PROCESSO = frozenset(
    {
        p.PRAZO_RECURSAL_EM_CURSO,
        p.PRAZO_RECURSAL_NAO_DECLARADO,
        p.RECURSO_AGUARDANDO,
        p.REAVALIACAO_PENDENTE,
        p.PROVIDENCIA_PENDENTE,
    }
)

#: Os que não: o Edital final já não recebe inscrição, e desde o A-09 recusa os atos da
#: Retificação — a frase da homologada mandaria "publique-a ou devolva-a" (D-002 da `130`). O
#: rascunho só existe no cancelar. Um tipo novo em `pendencias_do_edital` reprova o guardião até
#: cair num dos três conjuntos.
TIPOS_FORA_DO_PROCESSO = frozenset(
    {
        p.PERIODO_EM_CURSO,
        p.PERIODO_POR_ABRIR,
        p.PERIODO_SEM_TERMINO,
        p.RETIFICACAO_HOMOLOGADA,
        p.RETIFICACAO_EM_CURSO,
        p.RASCUNHOS_NAO_ENVIAVEIS,
    }
)


@dataclass(frozen=True)
class GrupoDoEdital:
    edital: object
    itens: tuple


@dataclass(frozen=True)
class AdvertenciaDoProcesso:
    """O que a confirmação do Processo diz, e o resumo que o envio devolve (FR-4365)."""

    grupos: tuple = ()
    convocado_no_prazo: bool = False
    resumo: str = ""

    @property
    def vazia(self):
        return not self.grupos

    @classmethod
    def de(cls, grupos):
        grupos = tuple(grupos)
        return cls(
            grupos=grupos,
            convocado_no_prazo=any(
                item.tipo == p.CONVOCACAO_AGUARDANDO for grupo in grupos for item in grupo.itens
            ),
            resumo=resumo_de(grupos),
        )


def resumo_de(grupos):
    """O hash do que o gestor leu: o Edital e as frases, na ordem (R-5 da `130`).

    **As frases, e não os fatos**: a frase já leva a contagem, a data e o marco, que é o que precisa
    ser igual. O caminho fica fora, porque depende de quem lê. Sem assinatura: o resumo não autoriza
    nada — quem o forjasse só pularia uma renovação que confirmar duas vezes já pula.

    **As frases de cada Edital entram ordenadas**: a regra da `113` percorre os recortes de
    resultado sem `order_by`, e a ordem dos prazos de recurso entre marcos é a do banco. Na tela
    isso é só exibição; aqui seria um 409 sem nada ter mudado. Os Editais, de ordem estável, entram
    nela.
    """
    lido = [
        [str(grupo.edital.id), sorted(item.mensagem for item in grupo.itens)] for grupo in grupos
    ]
    texto = json.dumps(lido, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def do_processo(processo, ator, *, agora):
    """A advertência de "Encerrar Processo": por Edital final publicado, o que está em aberto (130).

    Supõe `leitura_consistente` aberta por quem chama, como `fatos_do_edital`: os Editais são lidos
    no mesmo instante (FR-4361). O Edital nunca publicado não tem conteúdo vigente, e fica de fora;
    o final sem nada em aberto também (FR-4358). A ordem é a em que a recusa nomeia os pendentes.
    """
    from processo_seletivo.processos.domain.finalizacao import EDITAL_FINAL
    from processo_seletivo.publicacoes.models import Publicacao

    editais = (
        processo.editais.filter(status__in=EDITAL_FINAL)
        .filter(Exists(Publicacao.objects.filter(edital=OuterRef("pk"))))
        .order_by("year", "number", "id")
    )
    grupos = []
    for edital in editais:
        itens = [
            _item(situacao, edital, ator, "encerrar")
            for situacao in p.situacoes(edital, agora=agora, ato="encerrar", com_advertencias=True)
            if situacao.tipo in TIPOS_NO_PROCESSO
        ]
        itens.extend(_providencias_da_099(edital, agora))
        if itens:
            grupos.append(GrupoDoEdital(edital, tuple(itens)))
    return AdvertenciaDoProcesso.de(grupos)
