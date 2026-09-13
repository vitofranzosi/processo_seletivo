"""A leitura do recorte da convocação: a fila, o estado de cada chamada, e o histórico (019).

**Os números de ocupação não são calculados aqui** (`UX-035`, `SC-092`). Eles vêm de
`ocupacao.application.selectors.ocupacao_do_recorte`, que é quem responde *"quantas estão
ocupadas"*. Esta feature lê o conjunto de ocupantes para saber **quem** já está servido — que é
outra pergunta —, e nunca afirma a contagem por conta própria.

**Tudo por conjunto, e nunca uma consulta por convocação** (`SC-088`, `SC-090`). O modo de errar
aqui é invisível com 40 pessoas e mata com 1.000: a tela do recorte carrega convocações, desfechos e
comunicações de uma vez, e o custo não cresce com o número de chamadas praticadas.

**Vigente é derivada.** A convocação vigente é a que ninguém sucedeu, como a apuração da `016` e o
corte da `014`; e o estado do prazo é calculado a cada leitura, e não guardado — coluna exigiria
`UPDATE` em tabela append-only, e o relógio andaria dentro de um ato imutável.
"""

from django.utils import timezone

from processo_seletivo.convocacao.domain import fila, nomes, prazo
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.ocupacao.application import efeitos as efeitos_de_ocupacao
from processo_seletivo.ocupacao.application import selectors as ocupacao_selectors
from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO


def convocacoes_do_recorte(*, edital, perfil_id, marco_id, lista_id=None):
    """Todas as convocações do recorte, com desfecho e comunicações já carregados.

    **`prefetch_related`, e não acesso preguiçoso na alça do laço.** Cada convocação tem no máximo
    um desfecho e algumas comunicações; buscá-los por linha custaria duas consultas por pessoa
    chamada, e é exatamente o crescimento que a `SC-090` proíbe.
    """
    return list(
        Convocacao.objects.filter(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
        .select_related("apuracao")
        .prefetch_related("desfechos", "comunicacoes", "sucessoras")
        .order_by("criado_em", "id")
    )


def vigentes(convocacoes):
    """As que ninguém sucedeu. Correção é sucessão, e a sucedida continua legível."""
    return [c for c in convocacoes if not c.sucessoras.all()]


def desfecho_de(convocacao):
    """O desfecho **vigente** da convocação, ou `None` — o que ninguém sucedeu.

    **Vigente, e não "o único"**: um fato posterior sucede o desfecho sem apagá-lo, e é assim que o
    cancelamento por inércia alcança quem havia aceitado (`US5`). A `FR-273` continua valendo — há
    no máximo um vigente —, e a cadeia inteira continua legível no histórico.
    """
    desfechos = list(convocacao.desfechos.all())
    if not desfechos:
        return None
    sucedidos = {d.desfecho_anterior_id for d in desfechos if d.desfecho_anterior_id}
    vigentes_do_ato = [d for d in desfechos if d.id not in sucedidos]
    return max(vigentes_do_ato, key=lambda d: d.registrado_em) if vigentes_do_ato else None


def envio_de(convocacao):
    """O instante do envio bem-sucedido mais recente, ou `None` (`R-009`).

    `None` é o estado *"convocado, prazo não iniciado"*: o ato existe e a mensagem não partiu. Sem
    esta distinção, falha de infraestrutura fica indistinguível de silêncio da pessoa.
    """
    enviados = [c.enviado_em for c in convocacao.comunicacoes.all() if c.enviado_em is not None]
    return max(enviados) if enviados else None


def estado_de(convocacao, *, agora):
    """Em qual dos quatro estados a convocação está, para a tela e para o portal."""
    return prazo.estado(
        tem_desfecho=desfecho_de(convocacao) is not None,
        enviado_em=envio_de(convocacao),
        vencimento=convocacao.vencimento,
        agora=agora,
    )


def contexto_do_recorte(*, edital, perfil_id, marco_id, lista_id=None, at=None):
    """O que a fila e as recusas precisam saber, lido de uma vez só.

    Devolve a apuração vigente e as causas de obsolescência dela, a faixa alcançada em ordem, o
    conjunto de quem já ocupa, as convocações do recorte e a própria fila de chamada.

    **A apuração pode ser `None`, e isso não é zero.** Recorte sem apuração emitida não tem déficit
    conhecido, e chamar ali seria prometer o que ninguém apurou (`apuracao_ausente`).
    """
    ordem, corte, _ = ocupacao_selectors.progrediram_em_ordem(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    etapa = corte.etapa_governada_id if corte is not None else None
    habilitadas = ocupacao_selectors.habilitadas_na_etapa(edital=edital, etapa_id=etapa)
    # A concorrência concomitante, lida **pela `016`** e não por uma segunda conta: quem ocupa vaga
    # de ampla é titular dela, e essa definição tem um dono só (`FR-252`, `UX-035`).
    concomitantes = (
        ocupacao_selectors.ocupantes_da_ampla(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            versao=effective_version(edital_id=edital.id, at=at),
        )
        if lista_id is not None
        else set()
    )
    alcancados = fila.alcancados(
        progrediram_em_ordem=ordem,
        habilitadas=habilitadas,
        ocupantes_da_ampla=concomitantes,
    )
    apuracao = ocupacao_selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    causas = ocupacao_selectors.causas_de_obsolescencia(apuracao, at=at)
    efeitos = efeitos_de_ocupacao.efeitos_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    # **Os titulares saem da sequência que progrediu, e não dos alcançados** (`R-001`). A janela é
    # recortada antes de perguntar por habilitação: quem é titular e foi eliminado não ocupa a vaga
    # dele, e ela fica faltando. Recortá-la sobre os alcançados promoveria o próximo em silêncio —
    # que é o defeito que esta feature existe para eliminar.
    titulares = calculo.titulares_iniciais(
        progrediram_em_ordem=ordem,
        efetivas=apuracao.efetivas if apuracao else 0,
        ocupantes_da_ampla=concomitantes,
    )
    # **Quem já está servido**, e não quantos: a contagem é da `016`, e a `UX-035` a varre.
    ocupando = calculo.ocupantes(
        titulares=titulares,
        habilitadas=habilitadas,
        efeitos_lidos=efeitos_de_ocupacao.efeitos_lidos_por(efeitos),
    )
    convocacoes = convocacoes_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    em_aberto, servidos, encerrados, reclassificados = _situacoes(convocacoes)
    reabilitados = reabilitados_por_deferimento(edital=edital, etapa_id=etapa)
    return {
        "apuracao": apuracao,
        "causasDeObsolescencia": [c["causa"] for c in causas],
        "corte": corte,
        "alcancados": alcancados,
        "titulares": titulares,
        "ocupando": ocupando,
        "convocacoes": convocacoes,
        "emAberto": em_aberto,
        "servidos": servidos,
        "encerrados": encerrados,
        "reclassificados": reclassificados,
        "reabilitados": reabilitados,
        # **Quem pode ser chamado para regularizar é outro conjunto** (`US3`): quem a faixa alcançou
        # e que **não** habilitou — o indeferido. Ele não está na fila de chamada porque não ocupa
        # e não pode ocupar vaga nenhuma enquanto o indeferimento valer; o que a convocação para
        # regularizar lhe dá é a chance de corrigir o que faltou, na ordem de classificação.
        "regularizaveis": fila.regularizaveis(
            progrediram_em_ordem=ordem,
            habilitadas=habilitadas,
            ja_chamados=em_aberto | servidos | encerrados | reclassificados,
        ),
        "fila": fila.ordem_de_chamada(
            alcancados_em_ordem=alcancados,
            servidos=servidos,
            com_chamada_em_aberto=em_aberto,
            encerrados=encerrados,
            reclassificados=reclassificados,
            reabilitados=reabilitados,
        ),
    }


def reabilitados_por_deferimento(*, edital, etapa_id):
    """Quem voltou a ser habilitado porque um recurso foi deferido (`FR-292b`).

    **A `018` devolveu a essa pessoa uma habilitação que ela deveria ter tido desde o começo**, e é
    isso que a põe na frente: chamá-la depois de quem passou à frente enquanto o recurso corria
    seria executar a decisão pela metade — ela receberia o direito e não a vez.

    A leitura é pela **origem** do Resultado vigente, e não pela existência de um recurso: o que
    importa é que a habilitação de hoje veio de uma decisão recursal, e é o Resultado que diz isso.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    if etapa_id is None:
        return set()
    # `vigentes`, e não `objects`: um Resultado superado depois não devolve precedência nenhuma.
    return {
        resultado.inscricao_id
        for resultado in ResultadoEtapa.vigentes.filter(
            edital=edital,
            etapa_id=etapa_id,
            origem=ResultadoEtapa.Origem.RECURSO,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        )
    }


def _forma_do_recorte(convocacoes):
    """A forma declarada que as convocações deste recorte citam, ou `None`.

    Lida da **versão que cada convocação congelou**, e não da vigente: é a norma que valia quando o
    ato foi praticado. Todas as do recorte citam a mesma, salvo Retificação no meio do caminho — e
    aí a primeira responde, porque é a que a tela está prestes a emitir.
    """
    from processo_seletivo.convocacao.application.comunicar import forma_declarada

    for convocacao in convocacoes:
        forma = forma_declarada(convocacao)
        if forma is not None:
            return forma
    return None


def identidades_de(inscricoes):
    """`{id: {"id", "protocolo", "nome"}}` — o que a tela mostra no lugar do identificador.

    **Numa consulta só** (`SC-088`), e com o identificador preservado: ele continua sendo o valor
    que o formulário envia e a âncora que a auditoria usa. O que muda é o que a pessoa **lê**.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    if not inscricoes:
        return {}
    return {
        registro.id: {
            "id": registro.id,
            "protocolo": registro.protocolo or str(registro.id),
            "nome": registro.nome,
        }
        for registro in Inscricao.objects.filter(id__in=inscricoes).only("id", "protocolo", "nome")
    }


def _atestados_por_inscricao(inscricoes):
    """Os atestados de fato externo de cada Inscrição chamada, numa consulta só."""
    from processo_seletivo.convocacao.models import AtestadoDeFatoExterno

    if not inscricoes:
        return {}
    por_inscricao = {}
    for atestado in AtestadoDeFatoExterno.objects.filter(inscricao_id__in=inscricoes).order_by(
        "atestado_em"
    ):
        por_inscricao.setdefault(atestado.inscricao_id, []).append(atestado)
    return por_inscricao


def _situacoes(convocacoes):
    """Quem tem chamada em aberto, quem já foi servido, quem encerrou e quem foi reclassificado.

    **Só as vigentes contam.** Uma convocação sucedida foi corrigida, e o desfecho dela — se houver
    — pertence ao ato que já não vale; lê-lo faria a correção de um erro de digitação encerrar a
    participação de alguém.

    **"Servido" não é "ocupante", e a distinção é a que faz a US1 existir.** Pela contagem da `016`,
    os titulares ocupam vaga desde a emissão da apuração — antes de qualquer chamada. Se a fila
    tirasse os ocupantes, ninguém jamais seria convocado para vaga inicial: a primeira chamada do
    certame seria recusada por não haver quem chamar. Servido é quem **respondeu** com um desfecho
    que inclui — aceite ou regularização —, e é só esse que não precisa ser chamado de novo.
    """
    em_aberto, servidos, encerrados, reclassificados = set(), set(), set(), set()
    for convocacao in vigentes(convocacoes):
        desfecho = desfecho_de(convocacao)
        if desfecho is None:
            em_aberto.add(convocacao.inscricao_id)
            continue
        if desfecho.especie in fila.DESFECHOS_QUE_ENCERRAM:
            encerrados.add(convocacao.inscricao_id)
        elif desfecho.especie == nomes.RECLASSIFICACAO:
            reclassificados.add(convocacao.inscricao_id)
        else:
            servidos.add(convocacao.inscricao_id)
    return em_aberto, servidos, encerrados, reclassificados


def leitura_do_recorte(*, edital, perfil_id, marco_id, lista_id=None, at=None):
    """O que a tela do recorte mostra: os quatro números da `016` e o estado de cada chamada.

    **Os quatro números vêm da `016`, e não são recalculados aqui** (`UX-035`, `SC-092`). Esta
    feature lê o conjunto de ocupantes para montar a fila — que é outra pergunta —, e a contagem
    continua tendo uma resposta só.

    **As três quantidades desta feature são de chamadas, e não de vagas**: quantas foram convocadas,
    quantas responderam, e se a lista alcançada esgotou. Chamá-las de "ocupadas" seria a `019`
    afirmar contagem de ocupação por conta própria, que é o que a varredura recusa.
    """
    contexto = contexto_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=at
    )
    agora = at or timezone.now()
    vigentes_do_recorte = vigentes(contexto["convocacoes"])
    # **Os atestados do recorte, lidos por conjunto** (`SC-088`): uma consulta para todas as
    # inscrições chamadas, e não uma por linha da tela.
    atestados = _atestados_por_inscricao([c.inscricao_id for c in vigentes_do_recorte])
    identificadas = identidades_de({c.inscricao_id for c in vigentes_do_recorte})
    linhas = [
        {
            "inscricao": identificadas[convocacao.inscricao_id],
            "convocacao": convocacao,
            "desfecho": desfecho_de(convocacao),
            "enviadaEm": envio_de(convocacao),
            "estado": estado_de(convocacao, agora=agora),
            "comunicacoes": list(convocacao.comunicacoes.all()),
            "atestados": atestados.get(convocacao.inscricao_id, []),
        }
        for convocacao in vigentes_do_recorte
    ]
    # **Quem conduz o certame não reconhece ninguém por UUID.** O percurso conduzido encontrou a
    # fila, os dois seletores e o histórico inteiro escritos em identificador — tecnicamente exato e
    # operacionalmente inútil: a pessoa que vai convocar precisa conferir contra a lista publicada,
    # e a lista publicada tem protocolo e nome. É a lição que a fixture de inscrição da `009` já
    # registra ao gerar `INS-<ano>-NNNN` em vez de quatro dígitos nus.
    identificadas |= identidades_de({*contexto["fila"], *contexto["regularizaveis"]})
    return {
        **contexto,
        "ocupacao": ocupacao_selectors.ocupacao_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=at
        ),
        "fila": [identificadas[i] for i in contexto["fila"]],
        "regularizaveis": [identificadas[i] for i in contexto["regularizaveis"]],
        "identificadas": identificadas,
        "linhas": linhas,
        # A tela precisa saber **qual** forma o Edital declarou para oferecer o campo certo: a
        # emissão por publicação pede onde se publicou, e a individual não tem esse campo.
        "formaPorPublicacao": _forma_do_recorte(vigentes_do_recorte) == FORMA_POR_PUBLICACAO,
        "convocadas": len(vigentes_do_recorte),
        "respondidas": sum(1 for linha in linhas if linha["desfecho"] is not None),
        "esgotou": fila.esgotou(contexto["fila"]),
    }


__all__ = [
    "contexto_do_recorte",
    "convocacoes_do_recorte",
    "desfecho_de",
    "envio_de",
    "estado_de",
    "identidades_de",
    "leitura_do_recorte",
    "reabilitados_por_deferimento",
    "vigentes",
]
