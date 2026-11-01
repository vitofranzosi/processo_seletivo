"""Atos do fluxo da Retificação, no mesmo formato dos atos do Edital.

Separado porque os commands recebem `retificacao_id`, e porque as consequências são outras:
o que uma Retificação provoca depende de vigência, não só de estado.
"""

from dataclasses import dataclass

from django.db.models import F
from django.urls import reverse

from processo_seletivo.interface.acoes import entrega_para
from processo_seletivo.publicacoes.application.retificacoes import (
    publish_retification,
    transition_retification,
)
from processo_seletivo.publicacoes.application.selectors import (
    homologar_fecharia_a_publicacao,
    impede_por_segregacao,
)
from processo_seletivo.publicacoes.models_retificacao import Retificacao


@dataclass(frozen=True)
class AtoRetificacao:
    """Um ato e as situações de que ele parte.

    `situacoes_exigidas` é conjunto, e não situação única, porque `devolver` parte de duas — o
    domínio admite desfazer tanto a revisão quanto a homologação (`TRANSITIONS`). Enquanto era
    escalar, `cancelar` precisava de um ramo próprio em `disponiveis` e outro em `impedimento`
    para consultar o seu conjunto à parte; com o conjunto no próprio ato, os dois ramos somem e
    o terceiro caso nunca precisa nascer.
    """

    chave: str
    rotulo: str
    permissao: str
    situacoes_exigidas: frozenset[str]
    consequencias: list[str]
    irreversivel: bool = False
    interrupcao: bool = False
    exige_motivo: bool = False
    exige_signatario: bool = False
    rotulo_motivo: str = "Motivo"


# Só a elaboração (E2E-021). O conjunto espelha `TRANSITIONS["cancelar"]` do domínio, que é quem
# recusa de fato — esta lista decide o que a tela **oferece**, e oferecer o que o domínio recusa
# seria convidar para um beco.
CANCELAVEL = frozenset({"EM_ELABORACAO"})
# Devolver desfaz a revisão ou a homologação, e por isso parte das duas — é o mesmo conjunto que
# `TRANSITIONS["devolver"]` declara no domínio.
DEVOLVIVEL = frozenset({"EM_REVISAO", "HOMOLOGADA"})

ATOS = {
    "submeter": AtoRetificacao(
        chave="submeter",
        rotulo="Submeter para revisão",
        permissao="retificacao:submeter",
        situacoes_exigidas=frozenset({"EM_ELABORACAO"}),
        consequencias=[
            "As alterações declaradas são congeladas para revisão.",
            "A Retificação deixa de poder ser editada até ser devolvida ou homologada.",
        ],
    ),
    "homologar": AtoRetificacao(
        chave="homologar",
        rotulo="Homologar",
        permissao="retificacao:homologar",
        situacoes_exigidas=frozenset({"EM_REVISAO"}),
        exige_motivo=True,
        rotulo_motivo="Fundamento da homologação",
        consequencias=[
            "As alterações passam a ser a versão candidata à Publicação.",
            "Nada muda no conteúdo vigente do Edital até a Publicação.",
        ],
    ),
    "publicar": AtoRetificacao(
        chave="publicar",
        rotulo="Publicar Retificação",
        permissao="retificacao:publicar",
        situacoes_exigidas=frozenset({"HOMOLOGADA"}),
        irreversivel=True,
        exige_signatario=True,
        consequencias=[
            "A Retificação torna-se pública e imutável.",
            "O conteúdo vigente do Edital passa a incluir estas alterações a partir da vigência "
            "declarada — imediatamente, se nenhuma data futura foi informada.",
            "A Publicação original e as versões anteriores continuam preservadas e consultáveis.",
            "Correções posteriores exigem nova Retificação.",
        ],
    ),
    # Depois de `publicar`, e não antes: a tela lista os atos na ordem deste dicionário, e numa
    # Retificação homologada os dois são oferecidos juntos. O ato principal vem primeiro; o que
    # anda para trás vem depois dele, como no Edital.
    "devolver": AtoRetificacao(
        chave="devolver",
        rotulo="Devolver para elaboração",
        permissao="retificacao:homologar",
        situacoes_exigidas=DEVOLVIVEL,
        exige_motivo=True,
        rotulo_motivo="Motivo da devolução",
        consequencias=[
            "A Retificação volta para elaboração e pode ser editada novamente.",
            "Uma homologação anterior deixa de valer; sua autoria permanece na auditoria.",
            "O motivo fica registrado e é o que orienta quem for corrigir.",
        ],
    ),
    "cancelar": AtoRetificacao(
        chave="cancelar",
        rotulo="Cancelar Retificação",
        permissao="retificacao:cancelar",
        situacoes_exigidas=CANCELAVEL,
        irreversivel=True,
        interrupcao=True,
        exige_motivo=True,
        rotulo_motivo="Motivo do cancelamento",
        consequencias=[
            "A Retificação é encerrada sem produzir efeito no conteúdo vigente.",
            "O registro é preservado no histórico, marcado como cancelado.",
        ],
    ),
}


def disponiveis(retificacao, ator):
    for ato in ATOS.values():
        if ator.can(ato.permissao) and retificacao.status in ato.situacoes_exigidas:
            yield ato


def executar(ato, request, ator, retificacao, autoridade_id=None):
    argumentos = {
        "actor": ator,
        "retificacao_id": retificacao.id,
        "expected_revision": retificacao.revision,
        # Confirmar duas vezes repete o mesmo ato, não pratica dois: a chave nasce na tela de
        # confirmação e volta no formulário, como nos atos do Edital e do Processo.
        "idempotency_key": request.POST.get("chave_idempotencia", ""),
        "correlation_id": request.correlation_id,
    }
    if ato.chave == "publicar":
        return publish_retification(**argumentos, autoridade_id=autoridade_id)
    return transition_retification(
        **argumentos, action=ato.chave, reason=(request.POST.get("motivo") or "").strip()
    )


def impedimento(retificacao, ator, ato):
    """O que impede este ato agora — para dizer antes da confirmação, não depois dela.

    `disponiveis` já responde isto para montar a lista de ações; a tela de confirmação,
    alcançável por URL direta, oferecia "Confirmar" sem consultá-lo. Quem recusa continua
    sendo o command: aqui só se explica o que ele responderia.
    """
    if not ator.can(ato.permissao):
        return {"motivo": "permissao", "permissao": ato.permissao}
    if any(cabivel.chave == ato.chave for cabivel in disponiveis(retificacao, ator)):
        # A segregação depois da situação, como no command: publicar o que não está homologado é
        # recusado por situação, e só a Retificação homologada chega a perguntar quem a homologou
        # (103, FR-2725, FR-2727).
        texto = motivo_previsivel(retificacao, ator, ato)
        return {"motivo": "segregacao", "texto": texto} if texto else None
    return {
        "motivo": "situacao",
        "exigidas": sorted(ato.situacoes_exigidas),
        "atual": retificacao.status,
    }


# ---------------------------------------------------------------------------
# A jornada da Retificação pela navegação comum (103)
# ---------------------------------------------------------------------------

#: Quem age depois de cada situação (103, FR-2711, D-003). A forma é a do Edital
#: (`acoes.PROXIMO_RESPONSAVEL`), e a tabela é outra porque as situações têm outros nomes —
#: "homologada", e não "homologado". O terceiro termo é o ato **principal** da situação: em revisão
#: cabem homologar e devolver, e o que anda para frente é homologar; devolver é retrocesso, e
#: nunca o próximo passo, como no Edital.
PROXIMO_RESPONSAVEL = {
    "EM_ELABORACAO": ("quem elabora", "submeter a Retificação para revisão", "submeter"),
    "EM_REVISAO": ("quem homologa", "homologar ou devolver a Retificação", "homologar"),
    "HOMOLOGADA": ("quem publica", "publicar a Retificação", "publicar"),
}

#: As situações em que a Retificação ainda pede um ato. É o que as telas chamam de "em curso", e é
#: a mesma tabela de cima: uma situação que não tem próximo responsável não está em curso.
EM_CURSO = frozenset(PROXIMO_RESPONSAVEL)

SEGREGACAO = "Você submeteu e homologou esta Retificação; publicar exige outra pessoa autorizada."


@dataclass(frozen=True)
class Oferta:
    """Um ato que a tela mostra, e por que ele não pode ser praticado agora — vazio se pode.

    `disponiveis` continua respondendo "permissão e situação", que é a pergunta do servidor sobre
    papel. A oferta acrescenta o que a tela já sabe que o command recusaria, como
    `acoes._motivo_previsivel` faz no Edital: o ato aparece desabilitado com o motivo, e não como
    caminho para uma recusa (FR-2725).
    """

    ato: AtoRetificacao
    url: str
    motivo: str = ""

    @property
    def disponivel(self):
        return not self.motivo


def participantes(retificacao):
    """Os nomes que as duas leituras de segregação do Edital recebem, com os campos da Retificação.

    **A regra não é copiada** (D-004). `impede_por_segregacao` e `homologar_fecharia_a_publicacao`
    só leem `elaborou` e `homologou`; o que a Retificação chama de elaborar, para a segregação, é
    submeter — `prepared_by` —, que é o mesmo que o command compara. Se a governança decidir que
    "elaborou" é quem compôs (AUD-RET-05), a troca é aqui e no command, juntas.
    """
    return {"elaborou": retificacao.prepared_by, "homologou": retificacao.homologated_by}


def motivo_previsivel(retificacao, ator, ato):
    if ato.chave == "publicar" and impede_por_segregacao(participantes(retificacao), ator):
        return SEGREGACAO
    return ""


def ofertas(retificacao, ator):
    return [
        Oferta(
            ato,
            reverse("interface:retificacao-ato", args=[retificacao.id, ato.chave]),
            motivo_previsivel(retificacao, ator, ato),
        )
        for ato in disponiveis(retificacao, ator)
    ]


def fecharia_a_publicacao(retificacao, ator, ato):
    """Homologar o que a própria pessoa submeteu deixa a publicação para outra (FR-2726)."""
    return ato.chave == "homologar" and homologar_fecharia_a_publicacao(
        participantes(retificacao), ator
    )


def pode_editar(retificacao, ator):
    """A edição do mesmo registro é oferecida? (FR-2715, FR-2721).

    A mesma condição que `edit_retification` impõe — permissão de elaborar e situação de
    elaboração —, perguntada antes, para que o link não leve a uma recusa.
    """
    return retificacao.status == Retificacao.Status.EM_ELABORACAO and ator.can(
        "retificacao:elaborar"
    )


def proximo_passo(retificacao, ator, ofertadas=None):
    """Situação e quem age a seguir — derivado, nunca persistido (FR-2711, FR-2712, FR-2732).

    "É você" sai das ofertas, e não do mapa de permissões: quem submeteu e homologou tem
    `retificacao:publicar` e mesmo assim não é a pessoa que o ato espera. É o caso que
    `acoes.proximo_passo` já trata no Edital, e pela mesma razão.
    """
    responsavel = PROXIMO_RESPONSAVEL.get(retificacao.status)
    if responsavel is None:
        return None
    papel, ato, chave = responsavel
    if foi_devolvida(retificacao):
        # Um verbo para a devolvida em toda tela (revisão de 30/10, D-013): a faixa e o cartão
        # dizem "Corrigir", e a passagem de bastão dizia "submeter" sobre o mesmo momento.
        # Primeiro se corrige, depois se submete — e a frase diz as duas coisas nessa ordem.
        ato = "corrigir a Retificação devolvida e submetê-la de novo"
    ofertadas = ofertas(retificacao, ator) if ofertadas is None else ofertadas
    principal = next((oferta for oferta in ofertadas if oferta.ato.chave == chave), None)
    return {
        "papel": papel,
        "ato": ato,
        "chave": chave,
        "sou_eu": principal is not None and principal.disponivel,
        "oferta": principal,
        "observacao": principal.motivo if principal is not None else "",
    }


#: O que a seção diz da Retificação parada, pela situação do Edital (113, FR-3544).
PARADA_POR_DESFECHO = {"ENCERRADO": "encerrado", "CANCELADO": "cancelado"}


def resumo(retificacao, ator):
    """Uma Retificação em curso como a Lista, o Edital e a tela de Retificar a mostram (FR-2702).

    As três telas leem daqui, e por isso a marca da Lista e a seção do Edital não divergem sobre a
    mesma Retificação e o mesmo ator (FR-2730). Nada aqui consulta o banco: quem chama já trouxe a
    Retificação na consulta única da tela (FR-2705, FR-2707).
    """
    # **A Retificação de Edital em estado final está parada** (113, FR-3544). Desde o A-09 nenhum
    # ato dela é aceito — nem cancelar —, e a seção anunciava um próximo responsável que nada podia
    # fazer. A situação do Edital vem anotada na consulta da tela, e não de uma consulta por item.
    parada = PARADA_POR_DESFECHO.get(getattr(retificacao, "situacao_do_edital", None), "")
    passo = None if parada else proximo_passo(retificacao, ator)
    devolvida, reenviada = foi_devolvida(retificacao), foi_reenviada(retificacao)
    item = {
        "retificacao": retificacao,
        "parada": parada,
        # A devolvida e a reenviada, ditas a partir do motivo já gravado (104, D-006): nenhuma
        # situação nova, só a leitura de `return_reason`, que a devolução grava e o reenvio mantém.
        "devolvida": devolvida,
        "reenviada": reenviada,
        "rotulo_situacao": rotulo_da_situacao(retificacao),
        "desde": desde(retificacao),
        "url": reverse("interface:retificacao-detalhe", args=[retificacao.id]),
        "passo": passo,
        "meu_ato": passo["oferta"].ato.rotulo if passo and passo["sou_eu"] else "",
        "editar": (
            reverse("interface:retificacao-editar", args=[retificacao.id])
            if not parada and pode_editar(retificacao, ator)
            else ""
        ),
    }
    # O rótulo do ato na Lista e na faixa (104): uma função só, lida pelos dois lugares.
    item["ato_na_lista"] = ato_na_lista(item) if item["meu_ato"] else ""
    return item


# Só o que as telas usam: a derivação acima lê a situação e dois nomes, e a seção diz quem criou,
# quando e por quê. Trazer as Alterações seria carregar o ato inteiro para uma linha.
_CAMPOS_DO_RESUMO = (
    "id",
    "edital_id",
    "status",
    "justification",
    "created_by",
    "created_at",
    "prepared_by",
    "homologated_by",
    "return_reason",
    "submitted_at",
    "homologated_at",
)


def foi_devolvida(retificacao):
    """Em elaboração **depois** de uma devolução, e não rascunho que nunca saiu (104, FR-2821)."""
    return retificacao.status == Retificacao.Status.EM_ELABORACAO and bool(
        retificacao.return_reason
    )


def foi_reenviada(retificacao):
    """Em revisão de novo, depois de devolvida (104, FR-2822)."""
    return retificacao.status == Retificacao.Status.EM_REVISAO and bool(retificacao.return_reason)


def rotulo_da_situacao(retificacao):
    """A situação dita por extenso, em minúscula, com a devolução quando houve."""
    if foi_devolvida(retificacao):
        return "devolvida"
    if foi_reenviada(retificacao):
        return "reenviada, em revisão"
    return {
        "EM_ELABORACAO": "em elaboração",
        "EM_REVISAO": "em revisão",
        "HOMOLOGADA": "homologada",
        "PUBLICADA": "publicada",
        "CANCELADA": "cancelada",
    }.get(retificacao.status, retificacao.status)


def desde(retificacao):
    """Desde quando a Retificação espera o próximo ato — só quando o modelo grava o instante.

    A devolução não tem instante no registro (só na trilha), e por isso a devolvida não diz desde
    quando: ler a trilha por item seria uma consulta por Retificação (104, Assumptions).
    """
    if retificacao.status == Retificacao.Status.EM_REVISAO:
        return retificacao.submitted_at
    if retificacao.status == Retificacao.Status.HOMOLOGADA:
        return retificacao.homologated_at
    return None


def ato_na_lista(resumo):
    """O ato da pessoa dito para quem ainda não abriu a Retificação (104, FR-2809, FR-2814).

    É o mesmo ato principal da passagem de bastão, com o verbo de quem vai começar a trabalhar: o
    homologador "analisa" — e decide entre homologar e devolver na página dela —, quem elabora a
    devolvida "corrige". A faixa e a coluna da Lista leem daqui, e por isso dizem a mesma coisa.
    """
    retificacao = resumo["retificacao"]
    if resumo["devolvida"]:
        return "Corrigir a Retificação devolvida"
    return {
        "EM_ELABORACAO": "Concluir e submeter a Retificação",
        "EM_REVISAO": "Analisar a Retificação",
        "HOMOLOGADA": "Publicar a Retificação",
    }.get(retificacao.status, "Abrir a Retificação")


def em_curso_por_edital(edital_ids, ator):
    """As Retificações em curso de vários Editais, numa consulta só (FR-2707, R-002).

    Devolve `{edital_id: [resumo, ...]}`, da mais antiga para a mais recente. Edital sem
    Retificação em curso não aparece no dicionário.
    """
    por_edital = {}
    for retificacao in (
        Retificacao.objects.filter(edital_id__in=list(edital_ids), status__in=EM_CURSO)
        .only(*_CAMPOS_DO_RESUMO)
        .annotate(situacao_do_edital=F("edital__status"))
        .order_by("created_at", "id")
    ):
        por_edital.setdefault(retificacao.edital_id, []).append(resumo(retificacao, ator))
    return por_edital


def em_curso(edital, ator):
    return em_curso_por_edital([edital.id], ator).get(edital.id, [])


def entrega(ato):
    """A quem o ato passa a Retificação (FR-2728).

    A tabela é a do Edital, chaveada pelo ato — e as chaves são as mesmas: submeter entrega a quem
    homologa, homologar a quem publica, devolver a quem elabora.
    """
    return entrega_para(ato)
