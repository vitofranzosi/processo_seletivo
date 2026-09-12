"""Se este ato pode ser divulgado agora — e, não podendo, qual das três razões impede (FR-004).

**Nada aqui é regra nova.** `estado_do_marco` já devolve `vigente`, `obsoleto`, `recomputavel` e as
`divergencias`, e já trata o marco removido por Retificação sem exceção especial (015). As três
formas de impedimento são **leitura** desse retorno (T-004).

A classificação é em três degraus, e é ela que a prévia mostra (FR-005):

| degrau | o que significa | efeito na tela |
|---|---|---|
| `informacao` | o estado normal, sem nada a ressalvar | publica |
| `aviso` | há o que ler antes de confirmar, mas nada impede | publica |
| `impedimento` | o ato não é publicável | **não** oferece o botão |

Havendo impedimento, não existe publicar mediante confirmação adicional (D-001): a tela mostra a
recusa nomeada e o caminho — emitir o ato sucessor, na tela da 015 (FR-006).

**O caminho não é o mesmo nas três.** Ato sucedido e ato desatualizado deixam o marco na norma:
existe o que recomputar, e o sucessor é o remédio. Marco removido não deixa — e a recusa que
mandava emitir sucessor instruía o operador a fazer o impossível (E2E17-002). `admite_sucessor`
é o que separa as duas situações, e é o domínio que o declara: a tela não pode deduzi-lo do
código da recusa sem repetir aqui a regra que vive aqui.
"""

from dataclasses import dataclass, field

from processo_seletivo.classificacao.application.selectors import ORIGEM_SORTEIO, estado_do_marco

INFORMACAO, AVISO, IMPEDIMENTO = "informacao", "aviso", "impedimento"

# As três recusas de obsolescência, com o código do contrato, o HTTP e o caminho que cada uma
# nomeia. O caminho é o requisito: uma recusa que não diz o que fazer a seguir devolve a pessoa à
# tela anterior sem nada (FR-006).
SUCEDIDO = "publication_act_superseded"
DESATUALIZADO = "publication_act_stale"
MARCO_REMOVIDO = "publication_milestone_removed"
# A quarta, e a única que a 018 acrescenta. Ela não é sobre o ato: é sobre alguém que **voltou** ao
# certame e cujo Resultado ainda não existe na Etapa que o marco enumera. Divulgar assim publicaria
# uma ordem que já se sabe incompleta — e a pessoa reabilitada apareceria como ausente da lista, o
# que é pior do que não publicar (FR-079).
REINGRESSO_PENDENTE = "publication_reentry_pending"
# A quinta, e a única que a 014 acrescenta. Ela também não é sobre o ato de ordenação: é sobre a
# **faixa** que ele alimentou. Divulgar um resultado que depende de um corte que o sistema já sabe
# estar para trás é divulgar uma faixa que a geração sucessora vai mudar — e o que se publicou não
# se despublica (014, FR-219).
CORTE_OBSOLETO = "publication_cut_stale"
# As três da definitividade. Elas impedem **só** a natureza definitiva: publicar como preliminar
# com recurso pendente é exatamente o caminho normal — é o preliminar que abre o prazo (FR-083).
RECURSO_PENDENTE = "publication_appeal_pending"
REAVALIACAO_PENDENTE = "publication_reassessment_pending"
PROVIDENCIA_PENDENTE = "publication_remedy_pending"
JANELA_ABERTA = "publication_window_open"
DECLARACAO_EXIGIDA = "publication_deadline_declaration_required"
DECLARACAO_RECUSADA = "publication_deadline_declaration_refused"

STATUS = {
    CORTE_OBSOLETO: 422,
    SUCEDIDO: 409,
    DESATUALIZADO: 422,
    MARCO_REMOVIDO: 422,
    REINGRESSO_PENDENTE: 422,
    RECURSO_PENDENTE: 422,
    REAVALIACAO_PENDENTE: 422,
    PROVIDENCIA_PENDENTE: 422,
    JANELA_ABERTA: 422,
    DECLARACAO_EXIGIDA: 422,
    DECLARACAO_RECUSADA: 422,
}

CAMINHO_DO_SUCESSOR = (
    "Emita o ato sucessor na tela de classificação do marco e publique o ato vigente."
)

# **O marco removido não tem esse caminho, e dizer que tem é mandar fazer o impossível.**
# `estado_do_marco` devolve `recomputavel=False` justamente porque não há regra vigente sobre a
# qual calcular ordem alguma: não existe ato sucessor a emitir enquanto o marco não voltar à
# norma. A recusa diz o que é verdade e para — restabelecer o marco é decisão normativa, tomada
# por Retificação, e não operação que esta tela ofereça (E2E17-002).
SEM_SUCESSOR = (
    "Não há ato sucessor a emitir: sem o marco na norma, não há ordem vigente a divulgar."
)

# O caminho do reingresso é **para trás**, e por isso ele é dito por extenso: quem lê a recusa está
# na tela da publicação e precisa saber que o trabalho está na organização da Etapa.
CAMINHO_DO_REINGRESSO = (
    "Consolide o resultado dessa inscrição na Etapa e emita o ato sucessor antes de divulgar."
)

MENSAGENS = {
    CORTE_OBSOLETO: (
        "A faixa que este resultado reflete está para trás: o corte vigente deste marco ficou "
        "obsoleto. Emita a geração sucessora antes de divulgar."
    ),
    SUCEDIDO: (
        "Este ato foi sucedido por outro e não é mais o vigente do marco. " + CAMINHO_DO_SUCESSOR
    ),
    DESATUALIZADO: (
        "A regra ou o universo mudaram desde a emissão deste ato, e divulgá-lo publicaria uma "
        "ordem que já não é a que o Edital vigente produz. " + CAMINHO_DO_SUCESSOR
    ),
    MARCO_REMOVIDO: (
        "O marco não existe na norma vigente: uma Retificação o removeu, e não há regra vigente "
        "com que comparar o ato. " + SEM_SUCESSOR
    ),
    REINGRESSO_PENDENTE: (
        "Há inscrição reabilitada por recurso cujo resultado ainda não foi consolidado numa Etapa "
        "que este marco enumera. " + CAMINHO_DO_REINGRESSO
    ),
    RECURSO_PENDENTE: (
        "Há recurso pendente de julgamento sobre este marco: chamar de definitivo o que ainda "
        "está em disputa afirma o que não aconteceu. Aguarde o julgamento, ou publique como "
        "resultado preliminar."
    ),
    REAVALIACAO_PENDENTE: (
        "Há reavaliação determinada por recurso e ainda não cumprida numa Etapa que este marco "
        "enumera. Conclua a reavaliação, consolide o resultado e emita o ato sucessor."
    ),
    PROVIDENCIA_PENDENTE: (
        "Há decisão de recurso que determinou providência a jusante e ainda não cumprida neste "
        "marco. Emita o ato sucessor **citando a decisão** e publique aquele ato."
    ),
    JANELA_ABERTA: (
        "O prazo recursal deste marco ainda está aberto: ele se encerra em {fecha}. "
        "Aguarde o encerramento, ou publique como resultado preliminar."
    ),
    DECLARACAO_EXIGIDA: (
        "Este marco não declara prazo recursal computável: para publicar como definitivo é "
        "preciso declarar expressamente, com fundamento escrito, que o prazo se encerrou."
    ),
    DECLARACAO_RECUSADA: (
        "Este marco declara prazo recursal computável, e o sistema o verifica: a declaração "
        "expressa de encerramento não é aceita aqui."
    ),
}

# Quais recusas admitem o remédio que a mensagem nomeia. É o que a tela lê para decidir se oferece
# o caminho — e não o código da recusa, que a obrigaria a repetir aqui a regra do domínio.
ADMITE_SUCESSOR = {
    CORTE_OBSOLETO: True,
    SUCEDIDO: True,
    DESATUALIZADO: True,
    MARCO_REMOVIDO: False,
    # O caminho aqui **não** é emitir ato sucessor: é consolidar o Resultado de quem voltou. Emitir
    # antes disso produziria o mesmo ato incompleto, e a tela mandaria repetir o que não resolve.
    REINGRESSO_PENDENTE: False,
    # Nenhuma das três se resolve emitindo outro ato do mesmo jeito: a primeira espera julgamento,
    # a segunda espera avaliação e consolidação, e a terceira exige um ato que **cite a decisão**.
    RECURSO_PENDENTE: False,
    REAVALIACAO_PENDENTE: False,
    PROVIDENCIA_PENDENTE: False,
    JANELA_ABERTA: False,
    DECLARACAO_EXIGIDA: False,
    DECLARACAO_RECUSADA: False,
}


@dataclass(frozen=True)
class Afericao:
    """O que a prévia mostra e o que o comando decide, na mesma leitura.

    Existem os dois porque são perguntas diferentes: a tela quer **o que dizer**, e o comando quer
    **se recusa**. Derivar a segunda de um texto seria pedir à interface que decidisse o domínio.
    """

    nivel: str
    codigo: str = ""
    mensagem: str = ""
    status: int = 422
    divergencias: list = field(default_factory=list)
    # Se há ato sucessor a emitir. Só faz sentido diante de impedimento, e é por isso que o padrão
    # é `True`: quem não impede não nomeia caminho nenhum, e a tela não lê este campo.
    admite_sucessor: bool = True

    @property
    def publicavel(self) -> bool:
        return self.nivel != IMPEDIMENTO


SUCEDERA = "publication_supersedes"

AVISO_DE_SUCESSAO = (
    "Este marco já tem resultado divulgado. Publicar de novo **sucede** aquela divulgação: ela "
    "permanece consultável no mesmo endereço e passa a dizer que foi sucedida."
)


def reingressos_pendentes(*, edital, marco, at=None):
    """As inscrições reabilitadas por recurso e ainda sem Resultado numa Etapa que o marco enumera.

    O fato é **derivado**, e por isso não depende de ninguém ter marcado nada: a reabilitação é um
    Resultado sucessor que habilita, e a pendência é a ausência de Resultado na Etapa seguinte
    (D-010, FR-075, FR-076).

    Duas consultas, e nenhuma por inscrição — a tela do marco lista dezenas.
    """
    from processo_seletivo.resultados.application.selectors import (
        inscricoes_com_resultado,
        reabilitadas_por_recurso,
    )

    etapas = [str(item) for item in (marco or {}).get("stages") or []]
    if not etapas:
        return {}
    reabilitadas = reabilitadas_por_recurso(edital=edital)
    if not reabilitadas:
        return {}

    pendentes = {}
    for etapa_id in etapas:
        com_resultado = inscricoes_com_resultado(edital=edital, etapa_id=etapa_id)
        for inscricao_id, resultado in reabilitadas.items():
            # A própria Etapa em que a reabilitação aconteceu não é pendência: ali o Resultado
            # existe, e é justamente o sucessor.
            if inscricao_id not in com_resultado:
                pendentes.setdefault(inscricao_id, resultado)
    return pendentes


def aferir(*, edital, marco_id, ato, sucede=None, at=None, natureza="", lista_id=None):
    """Afere a publicabilidade de `ato` contra o estado atual do marco.

    **`natureza` é a pretendida, e sem ela a verificação não distingue o que impede a definitiva do
    que não impede nada** (T-010, FR-081). Recurso pendente é o caminho normal do preliminar — é ele
    que abre o prazo — e é impedimento absoluto da definitiva. Uma aferição cega à natureza teria de
    escolher entre bloquear o preliminar, que travaria o certame, e liberar a definitiva, que é o
    defeito que o E2E17-005 registrou.

    Omitida, ela vale como preliminar: os três fatos da definitividade não se colocam, e a resposta
    é a mesma que a 017 já dava. É o padrão seguro — quem não sabe a natureza não pode estar
    pedindo a definitiva.

    `at` existe para o comando aferir no instante da transação, e não no da leitura da tela.

    `sucede` é a publicação vigente do marco, quando há uma. Ela **não** decide publicabilidade —
    suceder é o caminho normal da correção (FR-041) —, e é ela que produz o terceiro degrau da
    FR-005: há o que ler antes de confirmar, e nada impede. Sem ela, `aviso` seria um nível
    declarado e nunca alcançado, e a próxima pessoa a ler este módulo confiaria numa classificação
    que na prática tem dois valores.

    Quem chama sem `sucede` — o comando, que precisa saber apenas se recusa — recebe `informacao`
    no lugar de `aviso`, e a decisão dele é a mesma nos dois casos.
    """
    estado = estado_do_marco(edital=edital, marco_id=marco_id, at=at, lista_id=lista_id)
    # **Ato de sorteio não se afere recomputando** (021, FR-069, R-014). Ele também não é
    # recomputável, e pela razão oposta: não falta regra, falta cabimento — recalcular por Etapas
    # produziria uma ordem que não é a dele. A obsolescência dele já veio decidida no estado, pela
    # sucessão da relação que o originou, e é ela que os degraus abaixo consomem.
    sorteado = estado.get("origem") == ORIGEM_SORTEIO

    # **Primeiro o marco removido.** Sem regra vigente não há com que comparar, e as outras duas
    # perguntas não se colocam: `estado_do_marco` devolve `recomputavel=False` e uma divergência
    # de `regra_ausente` justamente para dizer isso.
    if not sorteado and not estado["recomputavel"]:
        return Afericao(
            IMPEDIMENTO,
            MARCO_REMOVIDO,
            MENSAGENS[MARCO_REMOVIDO],
            STATUS[MARCO_REMOVIDO],
            estado["divergencias"],
            ADMITE_SUCESSOR[MARCO_REMOVIDO],
        )

    vigente = estado["vigente"]
    if vigente is None or str(vigente.id) != str(ato.id):
        # Publicar um ato que outro já sucedeu divulgaria uma ordem revogada. O vigente ausente
        # cai aqui pelo mesmo raciocínio: o ato citado não é o que o marco reconhece hoje.
        return Afericao(
            IMPEDIMENTO,
            SUCEDIDO,
            MENSAGENS[SUCEDIDO],
            STATUS[SUCEDIDO],
            estado["divergencias"],
            ADMITE_SUCESSOR[SUCEDIDO],
        )

    # O reingresso pendente é pergunta sobre **Etapas**: falta Resultado na Etapa seguinte para
    # quem um recurso reabilitou. Num marco sorteado ela é categoria errada — a ordem não vem de
    # Etapa —, e a mudança de universo que importa ali já aparece como relação sucedida.
    pendentes = (
        {} if sorteado else reingressos_pendentes(edital=edital, marco=estado.get("marco"), at=at)
    )
    if pendentes:
        # **Antes da obsolescência**, e de propósito: quem lê precisa saber que o trabalho está na
        # Etapa, e não em emitir outro ato. Emitir sucessor aqui produziria o mesmo ato incompleto.
        return Afericao(
            IMPEDIMENTO,
            REINGRESSO_PENDENTE,
            MENSAGENS[REINGRESSO_PENDENTE],
            STATUS[REINGRESSO_PENDENTE],
            estado["divergencias"],
            ADMITE_SUCESSOR[REINGRESSO_PENDENTE],
        )

    # **Antes da definitividade e antes da obsolescência do ato**: o corte para trás é trabalho de
    # quem emite a geração sucessora, e dizê-lo primeiro entrega o próximo passo a quem lê — que é
    # o critério de ordem que esta função já segue.
    corte_para_tras = _corte_obsoleto(edital=edital, estado=estado, at=at, lista_id=lista_id)
    if corte_para_tras:
        return Afericao(
            IMPEDIMENTO,
            CORTE_OBSOLETO,
            MENSAGENS[CORTE_OBSOLETO],
            STATUS[CORTE_OBSOLETO],
            corte_para_tras,
            ADMITE_SUCESSOR[CORTE_OBSOLETO],
        )

    if str(natureza).upper() == "DEFINITIVA":
        impedimento = _impedimento_da_definitiva(
            edital=edital,
            marco_id=marco_id,
            marco=estado.get("marco"),
            ato=ato,
            at=at,
            # **O eixo da lista atravessa até aqui** (021, D-015). Sem ele, `_janela_aberta`
            # procurava a publicação da ampla concorrência: havendo só uma preliminar de PPI, a
            # consulta devolvia `None`, a janela não existia, e a definitiva da PPI era liberada
            # imediatamente — antes de qualquer prazo recursal.
            lista_id=lista_id,
        )
        if impedimento is not None:
            codigo, mensagem = impedimento
            return Afericao(
                IMPEDIMENTO,
                codigo,
                mensagem,
                STATUS[codigo],
                estado["divergencias"],
                ADMITE_SUCESSOR[codigo],
            )

    if estado["obsoleto"]:
        return Afericao(
            IMPEDIMENTO,
            DESATUALIZADO,
            MENSAGENS[DESATUALIZADO],
            STATUS[DESATUALIZADO],
            estado["divergencias"],
            ADMITE_SUCESSOR[DESATUALIZADO],
        )

    if sucede is not None:
        return Afericao(AVISO, SUCEDERA, AVISO_DE_SUCESSAO, 200)

    return Afericao(INFORMACAO, divergencias=[])


def _corte_obsoleto(*, edital, estado, at=None, lista_id=None):
    """As causas, quando a geração vigente do corte deste marco está para trás (014, FR-219).

    Devolve a lista de causas — vazia quando não há corte, ou quando ele está em dia. O import é
    local pela razão de sempre neste módulo: a divulgação lê a classificação, e não o contrário.
    """
    from processo_seletivo.classificacao.application.corte import estado_do_corte

    marco = estado.get("marco") or {}
    perfil = estado.get("perfil") or {}
    if not marco.get("id") or not perfil.get("id"):
        return []
    estado_da_faixa = estado_do_corte(
        edital=edital,
        perfil_id=perfil["id"],
        marco_id=marco["id"],
        lista_id=lista_id,
        at=at,
    )
    return estado_da_faixa["causas"] if estado_da_faixa["obsoleto"] else []


def _impedimento_da_definitiva(*, edital, marco_id, marco, ato, at=None, lista_id=None):
    """Os três fatos que só a definitiva enfrenta, na ordem em que a instituição os resolve.

    Primeiro o recurso pendente, porque enquanto há disputa em aberto nada mais importa; depois a
    reavaliação, que é trabalho de quem avalia; por último a providência, que é ato de quem emite.
    A ordem é a do caminho, e não da severidade: quem lê a recusa deve receber o próximo passo, e
    não o mais grave.

    O quarto fato — janela aberta — é do degrau 8, e entra quando ele existir. O quinto, ato
    obsoleto, é o que a 017 já verifica e vale para as duas naturezas. O sexto, reingresso pendente,
    é verificado antes, porque também impede o preliminar.
    """
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.recursos.application import selectors as recursos

    publicacoes = list(
        PublicacaoResultado.objects.filter(edital=edital, marco_id=marco_id).values_list(
            "id", flat=True
        )
    )
    if recursos.recursos_pendentes_do_marco(
        edital=edital, marco_id=marco_id, marco=marco, publicacoes_do_marco=publicacoes
    ):
        return (RECURSO_PENDENTE, MENSAGENS[RECURSO_PENDENTE])
    if recursos.reavaliacoes_pendentes_do_marco(edital=edital, marco=marco):
        return (REAVALIACAO_PENDENTE, MENSAGENS[REAVALIACAO_PENDENTE])
    if recursos.providencias_pendentes_do_marco(
        edital=edital,
        marco_id=marco_id,
        marco=marco,
        publicacoes_do_marco=publicacoes,
        ato=ato,
    ):
        return (PROVIDENCIA_PENDENTE, MENSAGENS[PROVIDENCIA_PENDENTE])
    fecha = _janela_aberta(edital=edital, marco_id=marco_id, marco=marco, at=at, lista_id=lista_id)
    if fecha is not None:
        # **A mensagem diz o instante**, e não só que há prazo: quem lê precisa saber quando voltar,
        # e "aguarde" sem data manda a pessoa tentar de novo às cegas.
        return (JANELA_ABERTA, MENSAGENS[JANELA_ABERTA].format(fecha=_quando(fecha)))
    return None


def _quando(momento):
    from processo_seletivo.shared.tempo import ZONA

    return momento.astimezone(ZONA).strftime("%d/%m/%Y às %Hh%M")


def _janela_aberta(*, edital, marco_id, marco, at, lista_id=None):
    """O instante em que o prazo declarado fecha, se ele ainda corre — senão `None` (FR-082).

    **Onde há janela declarada, o sistema verifica** — e é justamente por isso que a declaração
    expressa é recusada ali: pedir que a pessoa afirme o que a máquina sabe reintroduziria, com mais
    passos, a afirmação sem lastro que o E2E17-005 registrou (FR-086).
    """
    from django.utils import timezone

    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.recursos.domain.janela import computavel, janela_da_publicacao

    if computavel((marco or {}).get("appealWindow")) is None:
        return None
    vigente = vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
    computada = janela_da_publicacao(vigente, (marco or {}).get("appealWindow"))
    if computada is None:
        return None
    _, fecha = computada
    return fecha if (at or timezone.now()) <= fecha else None


__all__ = [
    "ADMITE_SUCESSOR",
    "AVISO",
    "Afericao",
    "DESATUALIZADO",
    "IMPEDIMENTO",
    "INFORMACAO",
    "DECLARACAO_EXIGIDA",
    "DECLARACAO_RECUSADA",
    "JANELA_ABERTA",
    "MARCO_REMOVIDO",
    "PROVIDENCIA_PENDENTE",
    "REAVALIACAO_PENDENTE",
    "RECURSO_PENDENTE",
    "REINGRESSO_PENDENTE",
    "SEM_SUCESSOR",
    "SUCEDERA",
    "SUCEDIDO",
    "aferir",
]
