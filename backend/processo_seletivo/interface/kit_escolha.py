"""A escolha de família, variante, imagem e formato do kit, em listas fechadas (119, FR-3805).

**Nada é guardado** (`D-008`). A escolha vem do formulário, é validada contra as listas do instante
e vai no evento da exportação; a pré-escolha da tela lê a exportação de peça mais recente do Edital.
Sem exportação, a Institucional (FR-3806).

**Negar por padrão.** Família de outra unidade, variante, imagem ou formato fora da lista é
`EscolhaInvalida`, e nada é gerado (EC-9). Template não liberado no ambiente, ou em versão ou resumo
diferentes dos liberados, é `NaoLiberado` (EC-7, EC-23). As duas são `PecaRecusada`, para que a
prévia, que só sabe responder "não encontrado", as trate como a peça que não existe neste acesso.
"""

from dataclasses import dataclass

from django.conf import settings

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import kit_familias, kit_peca
from processo_seletivo.interface.kit_familias import institucional
from processo_seletivo.interface.kit_formatos import FORMATOS

ESCOLHA_INDISPONIVEL = kit_peca.ESCOLHA_INDISPONIVEL
EM_APROVACAO = "Em aprovação pela comunicação."
VERSAO_EM_APROVACAO = "Versão nova em aprovação pela comunicação."
IMAGEM_RETIRADA = (
    "A imagem da última exportação não está mais no banco da família; a primeira da lista foi "
    "escolhida."
)
MANCHETE_INVALIDA = "A manchete escolhida não está entre as oferecidas. Abra o kit de novo."
FAMILIA_RETIRADA = (
    "A família da última exportação não está mais disponível neste ambiente; a Institucional foi "
    "escolhida."
)
VARIANTE_RETIRADA = (
    "A variante da última exportação não está mais na família; a primeira da lista foi escolhida."
)
#: As exportações que levam peça, e por isso família: o texto não tem (data-model §Evento).
EXPORTACOES_DE_PECA = ("png", "svg", "zip")


#: A mesma classe da composição: uma escolha forjada é uma recusa só, venha de onde vier.
EscolhaInvalida = kit_peca.EscolhaInvalida


class NaoLiberado(kit_peca.PecaRecusada):
    """O template não está liberado neste ambiente, nesta versão e neste resumo (EC-7, EC-23)."""


@dataclass(frozen=True)
class Escolhida:
    familia: kit_familias.Familia
    variante: str | None
    imagem: str | None
    manchete: int | None
    #: Por que a pré-escolha mudou (EC-8): dito na tela.
    aviso: str = ""

    @property
    def institucional(self):
        return self.familia.chave == institucional.CHAVE

    def imagem_do_banco(self):
        return next((i for i in self.familia.imagens if i.chave == self.imagem), None)


def familias_oferecidas(ficha):
    """As famílias da unidade do ato com algum template liberado, e a Institucional (FR-3805)."""
    liberadas = {template.familia for template in kit_familias.liberados()}
    return tuple(
        familia
        for familia in kit_familias.familias_da_unidade(ficha.unidade_codigo)
        if familia.chave == institucional.CHAVE or familia.chave in liberadas
    )


def ultima_escolha(edital):
    """O `detalhe` da exportação de peça mais recente que registrou família, ou vazio."""
    detalhe = (
        RegistroAuditoria.objects.filter(
            aggregate_type="Edital",
            aggregate_id=edital.pk,
            operation="EXPORTAR_MATERIAL",
            detalhe__formato__in=EXPORTACOES_DE_PECA,
            detalhe__has_key="familia",
        )
        .order_by("-occurred_at")
        .values_list("detalhe", flat=True)
        .first()
    )
    return detalhe or {}


def _da_lista(pedida, opcoes, *, explicita, aviso):
    """A opção pedida, a primeira quando não pedida, e o aviso quando a anterior saiu (EC-8)."""
    if not opcoes:
        if explicita and pedida:
            raise EscolhaInvalida
        return None, ""
    if pedida in opcoes:
        return pedida, ""
    if explicita and pedida:
        raise EscolhaInvalida
    return opcoes[0], (aviso if pedida else "")


def ler(dados, ficha, edital, *, indice_da_manchete=None):
    """A escolha do formulário, ou a pré-escolha; `EscolhaInvalida` fora das listas (FR-3806)."""
    familias = {familia.chave: familia for familia in familias_oferecidas(ficha)}
    pedida = (dados.get("familia") or "").strip()
    aviso_da_familia = ""
    if pedida:
        if pedida not in familias:
            raise EscolhaInvalida
        familia, origem, explicita = familias[pedida], dados, True
    else:
        origem = ultima_escolha(edital)
        familia = familias.get(origem.get("familia"), familias[institucional.CHAVE])
        explicita = False
        if familia.chave != origem.get("familia"):
            # A família anterior saiu da lista: troca-se com o motivo dito, como a imagem (EC-8).
            aviso_da_familia = FAMILIA_RETIRADA if origem.get("familia") else ""
            origem = {}
    variante, aviso_da_variante = _da_lista(
        origem.get("variante"),
        [v.chave for v in familia.variantes],
        explicita=explicita,
        aviso=VARIANTE_RETIRADA,
    )
    imagem, aviso_da_imagem = _da_lista(
        origem.get("imagem"),
        [i.chave for i in familia.imagens],
        explicita=explicita,
        aviso=IMAGEM_RETIRADA,
    )
    return Escolhida(
        familia,
        variante,
        imagem,
        indice_da_manchete,
        " ".join(filter(None, (aviso_da_familia, aviso_da_variante, aviso_da_imagem))),
    )


def estado(template, liberados):
    """Vazio quando liberado; senão o motivo que a tela diz (FR-3808, FR-3835)."""
    if template in liberados:
        return ""
    nomeados = {(f, formato) for f, formato, _, _ in settings.KIT_DE_DIVULGACAO_TEMPLATES}
    if (template.familia, template.formato.chave) in nomeados:
        return VERSAO_EM_APROVACAO
    return EM_APROVACAO


def templates_da_familia(familia):
    return [familia.templates[f] for f in FORMATOS if f in familia.templates]


def manchetes(ficha, escolhida, liberados):
    """A lista fechada, sobre os formatos liberados da família (FR-3818)."""
    templates = [t for t in templates_da_familia(escolhida.familia) if t in liberados]
    return kit_peca.manchetes_dos_templates(ficha, templates)


def compor(ficha, escolhida, formato, liberados, lista_de_manchetes):
    """A peça de um formato da família escolhida, ou a recusa com o motivo (FR-3824)."""
    template = escolhida.familia.templates.get(formato)
    if template is None:
        raise EscolhaInvalida
    motivo = estado(template, liberados)
    if motivo:
        raise NaoLiberado(motivo)
    texto = None
    if escolhida.manchete is not None:
        if not 0 <= escolhida.manchete < len(lista_de_manchetes):
            raise EscolhaInvalida(MANCHETE_INVALIDA)
        texto = lista_de_manchetes[escolhida.manchete]
    return kit_peca.compor_template(
        ficha,
        template,
        kit_peca.Escolha(
            manchete=escolhida.manchete,
            variante=escolhida.variante,
            imagem=escolhida.imagem,
            manchete_texto=texto,
        ),
    )


def detalhe_da_familia(escolhida):
    """Família, versão, variante e imagem: o que toda exportação de peça registra (FR-3828)."""
    return {
        "familia": escolhida.familia.chave,
        "familia_versao": escolhida.familia.versao,
        "variante": escolhida.variante,
        "imagem": escolhida.imagem,
    }


def detalhe(escolhida, peca):
    """O que a exportação de PNG ou SVG acrescenta ao evento (FR-3828, data-model §Evento)."""
    template = peca.template
    imagem = peca.imagem
    return {
        **detalhe_da_familia(escolhida),
        "imagem": imagem.chave if imagem else None,
        "imagem_sha256": imagem.sha256(template.formato.chave) if imagem else None,
        "formato_da_peca": template.formato.chave,
        "template_versao": template.versao,
        "template_resumo": kit_familias.resumo(template),
    }
