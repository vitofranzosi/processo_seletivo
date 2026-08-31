"""O que se pode fazer com um Edital agora — calculado **uma vez**, num lugar só.

**Por que este módulo existe.** Três lugares respondiam a esta pergunta e não se falavam:
`ACOES_POR_SITUACAO` na listagem, `atos.disponiveis` no detalhe, e um `<li>` fixo com `Retificar`
no template, fora dos dois. O `{% empty %}` observava apenas o terceiro. O resultado era o cartão
que oferece uma ação e, na linha seguinte, afirma que não há ação — o achado 08 da auditoria.

Os achados 07, 08 e 09 têm essa única causa, e por isso se resolvem juntos:

- **08** — a mensagem de ausência passa a derivar do mesmo conjunto que a lista.
- **07** — `Retificar` deixa de ser um `<li>` incondicional e passa a consultar
  `retificacao:elaborar`, permissão que `ACOES_POR_SITUACAO` já declarava e que ninguém lia.
- **09** — a previsão de recusa que a tela de confirmação já fazia passa a valer também onde o ato
  é **oferecido**. `praticar_ato` combinava `atos.impedimento`, as pendências impeditivas e a
  segregação de funções em `recusa_certa`; o detalhe tinha os mesmos dados e não os usava.

**A desabilitação é previsão, não autorização** (FR-025). Quem recusa continua sendo o command.
Aqui só se antecipa o que ele responderia, para que a pessoa não preencha uma tela inteira antes de
descobrir.
"""

from dataclasses import dataclass

from django.urls import reverse

from processo_seletivo.interface import atos
from processo_seletivo.processos.models import Edital

# Os nomes são os que `base.html` já define: `.botao` sozinho é a ação primária, e as duas
# variações têm classe própria. Inventar nomes aqui deixaria o estilo sem efeito.
PRIMARIA, SECUNDARIA, PERIGOSA = "", "secundario", "perigoso"

# Onde a prévia faz sentido. Publicado tem documento de verdade, e oferecer uma prévia ao lado dele
# criaria dois documentos concorrentes para o mesmo conteúdo. Mora aqui, e não em `views`, porque
# é o conjunto de ações que precisa dela — e importá-la de `views` seria ciclo.
ESTADOS_COM_PREVIA = (
    Edital.Status.EM_ELABORACAO,
    Edital.Status.EM_REVISAO,
    Edital.Status.HOMOLOGADO,
)


@dataclass(frozen=True)
class Acao:
    chave: str
    rotulo: str
    url: str
    estilo: str = SECUNDARIA
    irreversivel: bool = False
    # Vazio significa disponível. Preenchido, a tela mostra o controle desabilitado com este texto
    # ao lado — nem oferecido, nem escondido (FR-024).
    motivo: str = ""

    @property
    def disponivel(self) -> bool:
        return not self.motivo


def _navegacao(edital, ator):
    """Ações que levam a outra tela. Não são atos: não confirmam, não registram, não alteram."""
    if ator.can("edital:elaborar") and edital.status == "EM_ELABORACAO":
        yield Acao(
            "elaborar",
            "Elaborar o Edital",
            reverse("interface:compor", args=[edital.id]),
            estilo=PRIMARIA,
        )
    if edital.status in ESTADOS_COM_PREVIA:
        yield Acao(
            "visualizar", "Visualizar Edital", reverse("interface:previa", args=[edital.id])
        )
    # A permissão que `ACOES_POR_SITUACAO` já declarava desde a `002` e que o template ignorava.
    if edital.status == "PUBLICADO" and ator.can("retificacao:elaborar"):
        yield Acao("retificar", "Retificar", reverse("interface:retificar", args=[edital.id]))
    # Só depois de publicado: antes disso não há inscrição a consultar, e oferecer a tela vazia
    # seria oferecer um beco — exatamente o que a `007` tirou desta página.
    if edital.status in ("PUBLICADO", "ENCERRADO") and ator.can("inscricao:consultar"):
        yield Acao(
            "inscricoes",
            "Inscrições recebidas",
            reverse("interface:inscricoes", args=[edital.id]),
        )
    if ator.can("auditoria:consultar"):
        yield Acao(
            "auditoria",
            "Ver trilha de auditoria",
            reverse("interface:auditoria", args=[edital.id]),
        )


def _motivo_previsivel(ato, *, pendencias, segregacao):
    """O que a tela já sabe que o command recusaria.

    Só o que **está na própria tela**: as pendências impeditivas aparecem no cartão ao lado, e a
    segregação de funções é avisada acima. Prever mais do que isso seria duplicar o domínio.
    """
    if ato.chave == "publicar" and segregacao:
        return "Você elaborou e homologou esta revisão; publicar exige outra pessoa autorizada."
    if ato.chave in {"submeter", "publicar"}:
        impeditivas = [item for item in pendencias if item["severidade"] == "erro"]
        if impeditivas:
            quantas = len(impeditivas)
            return (
                f"{quantas} pendência impeditiva precisa ser resolvida antes."
                if quantas == 1
                else f"{quantas} pendências impeditivas precisam ser resolvidas antes."
            )
    return ""


def do_edital(edital, ator, *, pendencias=(), segregacao=False):
    """O conjunto completo: o que se pode fazer, e o que não se pode **e por quê**.

    `pendencias` e `segregacao` chegam prontas de quem já as calculou para a tela — recalculá-las
    aqui faria a mesma informação vir de dois lugares, que é o defeito que este módulo corrige.
    """
    conjunto = list(_navegacao(edital, ator))
    for ato in atos.disponiveis(edital, ator):
        conjunto.append(
            Acao(
                ato.chave,
                ato.rotulo,
                reverse("interface:ato", args=[edital.id, ato.chave]),
                estilo=PERIGOSA if ato.interrupcao else SECUNDARIA,
                irreversivel=ato.irreversivel,
                motivo=_motivo_previsivel(ato, pendencias=pendencias, segregacao=segregacao),
            )
        )
    return conjunto


# ---------------------------------------------------------------------------
# Passagem de bastão (FR-028 a FR-031)
# ---------------------------------------------------------------------------

# Quem age depois de cada situação. Derivado do mesmo mapa de permissões que governa os atos —
# não é fila, não é atribuição a pessoa, e nada disto é persistido.
PROXIMO_RESPONSAVEL = {
    "EM_ELABORACAO": ("quem elabora", "submeter o Edital para revisão", "submeter"),
    "EM_REVISAO": ("quem homologa", "homologar a revisão submetida", "homologar"),
    "HOMOLOGADO": ("quem publica", "publicar o Edital", "publicar"),
}


# Para quem o ato entrega o bastão. Chave é o ato; valor, o papel que passa a ser aguardado.
ENTREGA_DO_ATO = {
    "submeter": "quem homologa",
    "homologar": "quem publica",
}


def entrega_para(ato):
    """A quem este ato passa o bastão — dito **antes** de praticá-lo.

    Quem submete está entregando o Edital a outra pessoa; saber a quem, na hora de confirmar, é a
    diferença entre um ato e um envio às cegas. `publicar` não aparece: depois dele o Edital é
    público, e não há próximo responsável a aguardar.
    """
    return ENTREGA_DO_ATO.get(ato.chave, "")


def proximo_passo(edital, ator, *, segregacao=False):
    """Situação atual e quem age a seguir — informação derivada, nunca estado novo.

    **O caso que separa isto de uma consulta ao mapa de permissões**: quem elaborou *e* homologou o
    mesmo Edital não pode publicá-lo, ainda que tenha `edital:publicar`. Derivar só do mapa diria
    "é você" a exatamente a pessoa que o domínio vai recusar — e a segregação de funções deixaria de
    ser avisada onde ela importa. Por isso a segregação entra no cálculo.
    """
    responsavel = PROXIMO_RESPONSAVEL.get(edital.status)
    if responsavel is None:
        return None

    papel, ato, chave = responsavel
    if edital.status == "HOMOLOGADO" and segregacao:
        return {
            "papel": papel,
            "ato": ato,
            "sou_eu": False,
            "observacao": (
                "Você elaborou e homologou esta revisão, então o ato exige outra pessoa autorizada."
            ),
        }
    # `do_edital` só devolve atos que este ator pode praticar — a pergunta "sou eu?" é exatamente
    # "o ato que falta está entre os meus". Pendências não entram: quem tem o bastão continua com
    # ele mesmo tendo trabalho a fazer antes.
    meus = {acao.chave for acao in do_edital(edital, ator)}
    return {"papel": papel, "ato": ato, "sou_eu": chave in meus, "observacao": ""}
