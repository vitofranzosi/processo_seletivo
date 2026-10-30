"""O trabalho de quem abre a Lista — os objetos em que a pessoa pode atuar agora (104).

**Por que este módulo existe.** O GPS respondia "o que se pode fazer com este Edital" em toda tela,
e nenhuma respondia "o que eu tenho a fazer". O trabalho que mora dentro do Edital — a Retificação,
o recurso, a avaliação — aparecia em quatro lugares, com quatro gramáticas, e o homologador lia
"Nenhuma ação disponível" ao lado da Retificação que esperava por ele (diagnóstico de 30/10/2026).

**Leitura, e não motor** (FR-2801, FR-2829). Nada aqui autoriza, pratica ou guarda coisa alguma:
cada objeto é a resposta de uma função que **já** decide o botão de uma tela de detalhe —
`atos.disponiveis` no Edital, `atos_retificacao.ofertas` na Retificação, `impede_por_segregacao`
nos dois, a contagem de recursos da coluna e a carga de Minhas Etapas. Uma segunda regra, aqui,
divergiria da do detalhe na primeira mudança; é a lição da 103, que fez a marca da Lista e o
detalhe lerem o mesmo resumo.

**Um objeto, uma linha** (FR-2802). A Retificação em revisão admite homologar e devolver; para quem
lê, é uma coisa esperando análise, e não duas. O ato que a linha nomeia é o principal da situação.

**O custo não cresce com o número de Editais** (FR-2806). Os Editais chegam carregados por quem
chama; o resto são leituras para a página inteira: as Retificações em curso, os participantes dos
Editais em revisão ou homologados, os recursos. A avaliação custa o que Minhas Etapas já custa, e
isso cresce com as alocações da própria pessoa, e não com o escopo.
"""

from dataclasses import dataclass
from datetime import datetime

from django.urls import reverse

from processo_seletivo.avaliacoes.application import selectors as avaliacao_selectors
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.interface import acoes, atos, atos_retificacao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import (
    impede_por_segregacao,
    participantes_em_lote,
)
from processo_seletivo.recursos.application import admitir as recursos_admitir

#: Quantos objetos a faixa mostra antes de "Mostrar os outros" (104, D-009). Cinco cabem na
#: primeira tela a 375 px junto do título; mais do que isso transforma a faixa na lista inteira.
MOSTRADOS = 5

#: O que a faixa não cobre, e onde isso está (104, D-002, FR-2812). Dito na própria tela para que a
#: faixa não se apresente como "todas as pendências".
FORA_DA_FAIXA = (
    "Inclui atos de Edital e de Retificação, recursos e avaliações de comissão. Classificação, "
    "divulgação de resultado e avisos aos candidatos continuam no detalhe de cada Edital."
)


@dataclass(frozen=True)
class ObjetoDeTrabalho:
    natureza: str
    chave: tuple
    titulo: str
    ato: str
    situacao: str
    detalhe: str
    url: str
    edital: Edital
    desde: datetime | None = None


def _nome(edital):
    return f"Edital {edital.number}/{edital.year}"


def _do_edital(editais, ator):
    """O ato principal de cada Edital em fluxo, quando é desta pessoa e o domínio o aceitaria.

    **Em elaboração, o ato é continuar a elaboração**, e não submeter (D-004). Submeter depende da
    validação do conteúdo inteiro, que custaria dezenas de consultas por Edital; elaborar nunca é
    recusado a quem tem a permissão. É também o que `acoes.PREFERENCIA_DA_PRINCIPAL` põe primeiro.

    **Homologado, a segregação é lida em lote** (D-005): quem submeteu e homologou não publica, e o
    objeto não entra como ação dele.
    """
    em_fluxo = [edital for edital in editais if edital.status in ("EM_REVISAO", "HOMOLOGADO")]
    participantes = participantes_em_lote(em_fluxo) if em_fluxo else {}
    for edital in editais:
        detalhe = reverse("interface:detalhe", args=[edital.id])
        if edital.status == Edital.Status.EM_ELABORACAO and ator.can("edital:elaborar"):
            yield ObjetoDeTrabalho(
                "edital",
                ("edital", edital.id),
                _nome(edital),
                "Continuar a elaboração",
                "Edital em elaboração",
                edital.title,
                reverse("interface:compor", args=[edital.id]),
                edital,
            )
            continue
        meus = {ato.chave for ato in atos.disponiveis(edital, ator)}
        if edital.status == Edital.Status.EM_REVISAO and "homologar" in meus:
            yield ObjetoDeTrabalho(
                "edital",
                ("edital", edital.id),
                _nome(edital),
                "Homologar o Edital",
                "Edital em revisão",
                edital.title,
                detalhe,
                edital,
                participantes[edital.id]["elaborou_em"],
            )
        elif (
            edital.status == Edital.Status.HOMOLOGADO
            and "publicar" in meus
            and not impede_por_segregacao(participantes[edital.id], ator)
        ):
            yield ObjetoDeTrabalho(
                "edital",
                ("edital", edital.id),
                _nome(edital),
                "Publicar o Edital",
                "Edital homologado",
                edital.title,
                detalhe,
                edital,
                participantes[edital.id]["homologou_em"],
            )


def _da_retificacao(em_curso, editais):
    """Uma linha por Retificação cujo ato principal é desta pessoa — o resumo da 103, só ele."""
    por_id = {edital.id: edital for edital in editais}
    for edital_id, resumos in em_curso.items():
        for resumo in resumos:
            if not resumo["meu_ato"]:
                continue
            retificacao = resumo["retificacao"]
            yield ObjetoDeTrabalho(
                "retificacao",
                ("retificacao", retificacao.id),
                f"Retificação do {_nome(por_id[edital_id])}",
                atos_retificacao.ato_na_lista(resumo),
                f"Retificação {resumo['rotulo_situacao']}",
                (
                    f"Motivo da devolução: {retificacao.return_reason}"
                    if resumo["devolvida"]
                    else retificacao.justification
                ),
                resumo["url"],
                por_id[edital_id],
                resumo["desde"],
            )


def _dos_recursos(editais, ator, contagens):
    if not ator.can(recursos_admitir.PERMISSAO):
        return
    if contagens is None:
        ids = [edital.id for edital in editais if edital.status in acoes.ESTADOS_COM_INSCRICOES]
        por_edital = acoes.recursos_por_edital(ids) if ids else {}
    else:
        por_edital = contagens["recursos"]
    for edital in editais:
        quantos = por_edital.get(edital.id, 0)
        if quantos:
            yield ObjetoDeTrabalho(
                "recursos",
                ("recursos", edital.id),
                f"Recursos do {_nome(edital)}",
                f"Decidir recursos ({quantos})",
                f"{quantos} aguardando decisão",
                edital.title,
                reverse("interface:recursos", args=[edital.id]),
                edital,
            )


def _das_avaliacoes(ator):
    """As Etapas em que a pessoa tem inscrição a avaliar — a mesma conta de Minhas Etapas."""
    atribuicoes = comissao_selectors.minhas_etapas(ator)
    if not atribuicoes:
        return
    carga = avaliacao_selectors.carga_nas_etapas(ator=ator, atribuicoes=atribuicoes)
    for item in atribuicoes:
        pendentes = (carga.get((item["edital"].id, str(item["etapa_id"]))) or {}).get(
            "pendentes", 0
        )
        if pendentes:
            yield ObjetoDeTrabalho(
                "avaliacao",
                ("avaliacao", item["edital"].id, str(item["etapa_id"])),
                f"{item['nome']} — {_nome(item['edital'])}",
                f"Avaliar ({pendentes} pendente{'s' if pendentes != 1 else ''})",
                "Etapa de avaliação",
                item["edital"].title,
                reverse("interface:minha-etapa", args=[item["edital"].id, item["etapa_id"]]),
                item["edital"],
            )


def _ordem(objeto):
    """Primeiro o que espera há mais tempo; depois o resto, pelo Edital (Clarifications, 30/10).

    Determinística, e sem sugerir urgência: o que não tem instante gravado não é posto na frente
    nem atrás por suposição.
    """
    edital = objeto.edital
    numero = (edital.number or "").strip()
    return (
        objeto.desde is None,
        objeto.desde.timestamp() if objeto.desde else 0,
        edital.year,
        (0, int(numero), "") if numero.isdigit() else (1, 0, numero),
        objeto.natureza,
    )


def do_ator(ator, editais, *, em_curso=None, contagens=None):
    """Os objetos de trabalho do ator, um por objeto, na ordem da faixa (FR-2801 a FR-2806).

    `editais` são os que a tela já carregou, no escopo do ator. `em_curso` e `contagens` chegam de
    quem já os leu para a mesma página — a Lista lê as Retificações em curso para a marca e as
    contagens para a coluna — e são lidos aqui quando não chegam.
    """
    editais = list(editais)
    if em_curso is None:
        em_curso = atos_retificacao.em_curso_por_edital((e.id for e in editais), ator)
    objetos = [
        *_do_edital(editais, ator),
        *_da_retificacao(em_curso, editais),
        *_dos_recursos(editais, ator, contagens),
        *_das_avaliacoes(ator),
    ]
    vistos, unicos = set(), []
    for objeto in sorted(objetos, key=_ordem):
        if objeto.chave not in vistos:
            vistos.add(objeto.chave)
            unicos.append(objeto)
    return unicos


@dataclass(frozen=True)
class Faixa:
    objetos: list

    @property
    def total(self):
        return len(self.objetos)

    @property
    def mostrados(self):
        return self.objetos[:MOSTRADOS]

    @property
    def demais(self):
        return self.objetos[MOSTRADOS:]

    def __bool__(self):
        return bool(self.objetos)

    cobertura = FORA_DA_FAIXA
