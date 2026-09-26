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

from django.db.models import Exists, OuterRef
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import atos
from processo_seletivo.processos.models import Edital
from processo_seletivo.recursos.application import admitir as recursos_admitir
from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade, Recurso
from processo_seletivo.shared.api.problems import DomainError

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


# Estados em que existe inscrição a consultar. Em elaboração e em revisão não existe; publicado,
# encerrado e cancelado, sim — e o cancelado é justamente o que mais precisa ser consultável.
ESTADOS_COM_INSCRICOES = ("PUBLICADO", "ENCERRADO", "CANCELADO")


def pode_retificar(edital, ator) -> bool:
    """Esta pessoa pode propor a Retificação **deste** Edital? (037, FR-541a)

    **A pergunta já era feita aqui**, para decidir se `Retificar` entra na lista — o que ela não
    era é consultável de fora. E ela passou a ter mais de um leitor: o aviso de conteúdo imutável
    cala quando a ação está oferecida (`FR-541b`), e a tela do corte só oferece o caminho até a
    regra a quem a alcança (`FR-539b`).

    **Uma derivação, e não duas.** Duas respostas para a mesma pergunta divergem na primeira
    mudança — foi o que a `034` gastou uma feature inteira corrigindo em outra tela —, e o custo
    aqui seria a tela afirmar que alguém não pode ao lado do botão que ele pode clicar.

    **O estado entra no predicado**, e não só a permissão: Edital que não está publicado não se
    retifica, e é por isso que a ação nunca apareceu antes da publicação.
    """
    return edital.status == "PUBLICADO" and ator.can("retificacao:elaborar")


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
        yield Acao("visualizar", "Visualizar Edital", reverse("interface:previa", args=[edital.id]))
    # A permissão que `ACOES_POR_SITUACAO` já declarava desde a `002` e que o template ignorava.
    if pode_retificar(edital, ator):
        yield Acao("retificar", "Retificar", reverse("interface:retificar", args=[edital.id]))
    # Só depois de publicado: antes disso não há inscrição a consultar, e oferecer a tela vazia
    # seria oferecer um beco — exatamente o que a `007` tirou desta página. Cancelado entra na
    # lista pelo motivo oposto: ele **tem** inscrições, e quem as recebeu continua respondendo por
    # elas; tirar o caminho deixaria a tela alcançável só por URL decorada.
    if edital.status in ESTADOS_COM_INSCRICOES and ator.can("inscricao:consultar"):
        # Só as submetidas: o rótulo diz "recebidas", e rascunho aberto não foi recebido por
        # ninguém. Contá-lo faria a página anunciar um volume que a lista não confirma.
        recebidas = Inscricao.objects.filter(
            edital=edital, status=Inscricao.Status.SUBMETIDA
        ).count()
        yield Acao(
            "inscricoes",
            # O total no próprio rótulo (FR-066): "há inscrições e quantas" é a informação que
            # decide se vale abrir, e obrigar a abrir para descobrir é o atrito que a `007`
            # passou a feature inteira tirando.
            f"Inscrições recebidas ({recebidas})",
            reverse("interface:inscricoes", args=[edital.id]),
        )
    # Quem julga recurso não tinha por onde chegar ao próprio trabalho: a tela existia e nada
    # apontava para ela. O avaliador tem "Minhas Etapas" no cabeçalho de toda página; o julgador
    # não tem equivalente. O total no rótulo pela mesma razão das inscrições — decide se vale abrir.
    #
    # **O número é de trabalho, e não de histórico** (045, `FR-734`). Ele contava toda peça já
    # recebida, decididas inclusive, e um julgador com a fila vazia lia "Recursos recebidos (7)". A
    # tela para onde a ação leva continua listando todas; o rótulo é o que diz o que espera.
    if edital.status in ESTADOS_COM_INSCRICOES and ator.can(recursos_admitir.PERMISSAO):
        yield Acao(
            "recursos",
            f"Recursos aguardando decisão ({recursos_aguardando_decisao(edital)})",
            reverse("interface:recursos", args=[edital.id]),
        )
    # A exportação de matrículas (031). **Sem porta, a capacidade não é entregue** — Princípio VI:
    # *"uma capacidade que o domínio sustenta mas que nenhuma interface alcança NÃO DEVE ser
    # considerada entregue"*. A permissão é própria e não é concedida a papel nenhum por padrão, de
    # modo que a ação só aparece para quem a tem (`FR-455`).
    #
    # **Só depois de publicado**, como as inscrições: antes disso não há convocado nem resultado, e
    # oferecer a tela vazia seria oferecer um beco.
    if (
        edital.status in ESTADOS_COM_INSCRICOES
        and ator.can("matricula:exportar")
        and _pede_requerimento_de_matricula(edital)
    ):
        yield Acao(
            "matriculas",
            "Exportar para matrícula",
            reverse("interface:exportar-matriculas", args=[edital.id]),
        )
    if ator.can("auditoria:consultar"):
        yield Acao(
            "auditoria",
            "Ver trilha de auditoria",
            reverse("interface:auditoria", args=[edital.id]),
        )


def _pede_requerimento_de_matricula(edital) -> bool:
    """Este Edital coleta Requerimento de Matrícula? (029, `D-002`).

    **É esta declaração que confina a exportação a processos de alunos.** Nem todo certame deste
    sistema matricula alguém: há Editais de professor substituto, de técnico-administrativo, de
    tutores e de bolsistas, e neles a capacidade **não existe** — não fica escondida, não fica
    desabilitada, não existe. É o que o próprio modelo do Edital escreve, e o sistema não tem (nem
    precisa ter) taxonomia de natureza do Processo: quem coleta, declara.

    **Sem isto, a ação aparecia em todo Edital publicado** — e quem a abrisse num certame de
    servidores encontraria ou uma tela sem população, ou uma recusa listando pessoas como se cada
    uma tivesse deixado de declarar algo. As duas são becos, e o segundo acusa gente inocente.

    **Lido do conteúdo publicado, e não da linha de elaboração**: é a identidade estável, e é o que
    a `029` já consulta para decidir se abre o formulário ao candidato. Edital sem versão vigente
    não declarou coisa nenhuma.
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.requerimentos.domain.disponibilidade import momento_declarado

    try:
        conteudo = effective_version(edital_id=edital.id).content
    except DomainError:
        return False
    return bool(momento_declarado(conteudo))


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
# A divulgação do resultado (017, FR-069)
# ---------------------------------------------------------------------------


def do_ato_de_ordenacao(ato, ator, *, edital):
    """O que se pode fazer com um ato de classificação emitido.

    Hoje há duas: divulgá-lo e consultar o que já se divulgou. Ficam aqui pela mesma razão que as
    do Edital: a tela do ato não deve decidir sozinha o que oferecer, e a mensagem de ausência
    precisa derivar do mesmo conjunto que a lista.

    **A ação é oferecida na tela do ato** porque é dali que ela é alcançada. Sem isso a tela de
    publicar existiria e ninguém a encontraria — FR-069. A condição é a capacidade, e a
    desabilitação continua sendo previsão e não autorização: quem recusa é o command.
    """
    if ator.can("resultado:publicar"):
        yield Acao(
            "publicar-resultado",
            "Publicar resultado",
            reverse("interface:previa-de-publicacao", args=[edital.id, ato.marco_id, ato.id]),
            estilo=PRIMARIA,
            irreversivel=True,
        )
    if ator.can("resultado:publicar") or ator.can("auditoria:consultar"):
        yield Acao(
            "publicacoes-do-marco",
            "Resultados divulgados",
            reverse("interface:publicacoes-do-marco", args=[edital.id, ato.marco_id]),
        )


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
    # Devolver entrega o bastão de volta: é o único ato que anda para trás no fluxo, e dizê-lo
    # antes da confirmação é o que separa devolver de recusar em silêncio.
    "devolver": "quem elabora",
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


def recursos_aguardando_decisao(edital):
    """Quantas peças do Edital esperam decisão — sem juízo, ou admitidas e sem decisão.

    **Uma consulta, e nenhuma peça materializada.** A lista de Processos monta ações para vários
    Editais, e trazer cada peça para contá-la em Python seria custo por linha numa tela que não
    mostra peça nenhuma. As duas condições são as mesmas que a situação da peça usa
    (`recursos/application/selectors.py`, `_situacao`): sem juízo, aguarda admissibilidade;
    admitida e sem decisão, aguarda julgamento; o resto está decidido.
    """
    juizo = JuizoDeAdmissibilidade.objects.filter(recurso_id=OuterRef("pk"))
    decisao = DecisaoRecurso.objects.filter(recurso_id=OuterRef("pk"))
    return (
        Recurso.objects.filter(inscricao__edital=edital)
        .filter(~Exists(juizo) | (Exists(juizo.filter(admitido=True)) & ~Exists(decisao)))
        .count()
    )
