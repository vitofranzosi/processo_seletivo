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

from dataclasses import dataclass

from django.db.models import Prefetch
from django.utils import timezone

from processo_seletivo.convocacao.domain import fila, nomes, prazo, vocabulario_do_canal
from processo_seletivo.convocacao.models import Convocacao, DesfechoDaConvocacao
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


def chamada_em_aberto(inscricao):
    """A convocação vigente **sem desfecho** desta Inscrição, ou `None` (029, `FR-373`).

    **Em aberto, e não vigente** — a distinção é a mesma que `convocar.py::_em_aberto_da_pessoa`
    registra, e é a que faz a diferença: uma convocação com desfecho continua **vigente**, porque
    ninguém a sucedeu, mas está **concluída** — a pessoa respondeu, ou a Administração concluiu por
    ela. A primeira versão daquele bloqueio olhava só a vigência e produziu um beco; ler só a
    vigência aqui abriria o requerimento para quem já teve a chamada desfechada.

    **Esta função existe para haver uma fonte só.** A `029` a consome para decidir se o requerimento
    abre e se um sucessor pode nascer; escrever o predicado de novo lá dentro faria duas leituras de
    "em aberto" que divergiriam na primeira mudança — e o preço dessa divergência já foi pago uma
    vez nesta feature.
    """
    convocacoes = vigentes(
        Convocacao.objects.filter(inscricao=inscricao)
        .prefetch_related("desfechos", "sucessoras", "comunicacoes")
        .order_by("-criado_em")
    )
    # **Só a visível ao candidato** (125, FR-3986, D-003): quem consulta aqui é o Requerimento de
    # Matrícula, que é do portal; a chamada por publicação ainda não publicada não abre nada. A
    # gestão, que vê toda convocação, não passa por esta função.
    visiveis = visiveis_ao_candidato(convocacoes)
    for convocacao in convocacoes:
        if desfecho_de(convocacao) is None and convocacao.id in visiveis:
            return convocacao
    return None


# --- A visibilidade ao candidato (125) ---------------------------------------------------------


def forma_do_perfil(profiles, perfil_id):
    """A forma de comunicar que um Perfil declarou, de uma lista `profiles` de versão publicada.

    `None` quando o Perfil não declarou forma, ou declarou uma desconhecida — e nunca a publicação
    por omissão, pela mesma razão de `comunicar.forma_declarada`, que lê daqui.
    """
    from processo_seletivo.classificacao.domain.universo import por_identidade
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMAS_DE_CONVOCACAO

    forma = (por_identidade(profiles, perfil_id) or {}).get("callForm")
    return forma if forma in FORMAS_DE_CONVOCACAO else None


def _comunicada(convocacao):
    """Tem comunicação bem-sucedida? Lê só o que estiver no `prefetch` de `comunicacoes`."""
    return any(
        c.resultado == "ENVIADA" and c.enviado_em is not None for c in convocacao.comunicacoes.all()
    )


def visiveis_ao_candidato(convocacoes):
    """Os `id` das convocações que o portal pode mostrar ao candidato (125, FR-3981).

    **Visível** é a convocação cuja forma citada não é a publicação, ou cuja cadeia de correções —
    ela ou uma anterior — já teve comunicação bem-sucedida, em qualquer forma (D-001). A convocação
    por publicação que ninguém publicou ainda **não existe para o candidato**: na publicação, quem
    convoca é a publicação, e o portal não pode anunciar o ato antes do ato oficial (1ª decisão).

    **A gestão não passa por aqui**: ela vê toda convocação, e diz quando o candidato ainda não vê.

    **Por conjunto, e só paga quem não foi comunicada** (FR-3990, R-002). As comunicações vêm do
    `prefetch` de quem chama; sem convocação pendente, nenhuma consulta. Com alguma, até três: a
    cadeia das inscrições em questão, as comunicadas entre elas, e os `profiles` das versões citadas
    — nunca o conteúdo inteiro, que é o Edital todo. Cada convocação lida no terceiro passo recebe a
    forma em `forma_lida`, para que o vocabulário da tela não a leia de novo.
    """
    from processo_seletivo.convocacao.models import ComunicacaoEmitida
    from processo_seletivo.publicacoes.models import VersaoConsolidada

    convocacoes = list(convocacoes)
    pendentes = [c for c in convocacoes if not _comunicada(c)]
    visiveis = {c.id for c in convocacoes if _comunicada(c)}
    if not pendentes:
        return visiveis

    # **A cadeia**, percorrida em memória: a correção não tem profundidade máxima (a `121` corrige a
    # correção), e subir elo a elo pelo banco custaria uma consulta por elo.
    pela_cadeia = set()
    if any(c.convocacao_anterior_id for c in pendentes):
        inscricoes = {c.inscricao_id for c in pendentes}
        anterior_de = dict(
            Convocacao.objects.filter(inscricao_id__in=inscricoes).values_list(
                "id", "convocacao_anterior_id"
            )
        )
        comunicadas = set(
            ComunicacaoEmitida.objects.filter(
                convocacao__inscricao_id__in=inscricoes,
                resultado="ENVIADA",
                enviado_em__isnull=False,
            ).values_list("convocacao_id", flat=True)
        )
        for convocacao in pendentes:
            atual, vistos = convocacao.convocacao_anterior_id, set()
            while atual is not None and atual not in vistos:
                if atual in comunicadas:
                    pela_cadeia.add(convocacao.id)
                    break
                vistos.add(atual)
                atual = anterior_de.get(atual)
    visiveis |= pela_cadeia

    restantes = [c for c in pendentes if c.id not in pela_cadeia]
    if restantes:
        profiles = dict(
            VersaoConsolidada.objects.filter(id__in={c.versao_id for c in restantes}).values_list(
                "id", "content__profiles"
            )
        )
        for convocacao in restantes:
            convocacao.forma_lida = forma_do_perfil(
                profiles.get(convocacao.versao_id), convocacao.perfil_id
            )
            # Sem forma declarada a convocação não pode ser comunicada, e continua como sempre foi:
            # a 1ª decisão alcança só a publicação.
            if convocacao.forma_lida != FORMA_POR_PUBLICACAO:
                visiveis.add(convocacao.id)
    return visiveis


def visivel_ao_candidato(convocacao):
    """A FR-3981 para uma convocação só — nos comandos do portal, que leem uma de cada vez."""
    return convocacao.id in visiveis_ao_candidato([convocacao])


def ha_convocacao_visivel_no_recorte(*, edital, perfil_id):
    """O certame chegou a convocar, **para o candidato**, neste Perfil? (125, FR-3984, R-003).

    É a pergunta que separa *"não há convocação"* de *"você não foi chamado"* (US6 da `019`).
    Contar as convocações que ninguém publicou diria a todo inscrito que a convocação começou antes
    de publicada — e diria ao próprio convocado que ele não foi chamado.
    """
    from processo_seletivo.publicacoes.models import VersaoConsolidada

    convocacoes = Convocacao.objects.filter(edital=edital, perfil_id=perfil_id)
    if convocacoes.filter(
        comunicacoes__resultado="ENVIADA", comunicacoes__enviado_em__isnull=False
    ).exists():
        return True
    # As versões citadas são poucas — uma por Retificação —, e de cada uma só os `profiles`.
    versoes = VersaoConsolidada.objects.filter(id__in=convocacoes.values("versao_id")).values_list(
        "content__profiles", flat=True
    )
    return any(forma_do_perfil(p, perfil_id) != FORMA_POR_PUBLICACAO for p in versoes)


def vigentes_por_inscricao(inscricao_ids):
    """A convocação que o portal mostra de cada Inscrição pedida: `{inscricao_id: Convocacao}`.

    **A vigente mais recente, e não a em aberto** (059, `D-001`). `chamada_em_aberto`, acima,
    responde se o requerimento abre — e some com a convocação desfechada. O portal precisa dela
    também: quem atendeu continua vendo que foi chamado e o que se registrou. Esta é a regra que a
    tela da convocação já usava dentro da view; morar aqui é o que faz a lista, o acompanhamento e
    a tela mostrarem a **mesma** convocação (`FR-1100`).

    **Por conjunto, e em número fixo de consultas.** A lista de inscrições é o lugar onde uma
    leitura por item passa despercebida com três e mata com trezentas — o defeito que
    `tests/performance/test_area_do_candidato.py` existe para pegar. Inscrição sem
    convocação não aparece no dicionário; lista vazia não consulta nada.
    """
    if not inscricao_ids:
        return {}
    por_inscricao = {}
    lidas = list(
        Convocacao.objects.filter(inscricao_id__in=inscricao_ids, sucessoras__isnull=True)
        # **A anterior e as comunicações dela vêm junto** (121, R-008): a linha *"Convocação
        # substituída"* dos dados do ato as lê, e lidas por item quebrariam a contagem fixa que a
        # `118` mede. A anterior entra pelo `JOIN`; as comunicações dela custam uma consulta só
        # quando há alguma anterior, e nenhuma quando nenhuma vigente corrige outra.
        .select_related("convocacao_anterior")
        # O atestado do desfecho vem junto, pelo `JOIN` (156, R-002): a frase simples do
        # cancelamento por inércia diz o fato atestado, e lê-lo por item — ou numa consulta a mais
        # — quebraria a mesma contagem fixa.
        .prefetch_related(
            Prefetch("desfechos", DesfechoDaConvocacao.objects.select_related("atestado")),
            "comunicacoes",
            "convocacao_anterior__comunicacoes",
        )
        .order_by("-criado_em", "-id")
    )
    # **Só as visíveis ao candidato** (125, FR-3982, FR-1100 da `059` revista): a convocação por
    # publicação que ninguém publicou é ausente aqui, e por isso é ausente na lista, no
    # acompanhamento, na tela e no Requerimento ao mesmo tempo.
    visiveis = visiveis_ao_candidato(lidas)
    for convocacao in lidas:
        # A ordem decrescente faz a primeira vista ser a mais recente; as seguintes da mesma
        # Inscrição — vigentes em paralelo, que o domínio não produz — ficam de fora, como ficavam
        # no `.first()` da view.
        if convocacao.id in visiveis:
            por_inscricao.setdefault(convocacao.inscricao_id, convocacao)
    return por_inscricao


def envio_de(convocacao):
    """O instante do envio bem-sucedido mais recente, ou `None` (`R-009`).

    `None` é o estado *"convocado, prazo não iniciado"*: o ato existe e a mensagem não partiu. Sem
    esta distinção, falha de infraestrutura fica indistinguível de silêncio da pessoa.
    """
    enviados = [c.enviado_em for c in convocacao.comunicacoes.all() if c.enviado_em is not None]
    return max(enviados) if enviados else None


@dataclass(frozen=True)
class Comunicacao:
    """A comunicação que as telas citam: a forma, o instante e, na publicação, a referência."""

    forma: str | None
    instante: object = None
    referencia: str = ""


def comunicacao_de(convocacao):
    """A última comunicação bem-sucedida, ou só a forma, quando nenhuma houve (125, R-007).

    **A forma é a da convocação**, e não a vigente do Edital: a da comunicação, que é o que
    aconteceu; sem comunicação nenhuma, a que a visibilidade já leu (`forma_lida`); e só na falta
    das duas, a versão citada, numa consulta — o caso da correção de convocação publicada que
    aguarda a própria publicação. `envio_de` continua sendo a fonte do prazo: o instante que inicia
    o prazo não muda (FR-4005).
    """
    comunicacoes = list(convocacao.comunicacoes.all())
    enviadas = [c for c in comunicacoes if c.resultado == "ENVIADA" and c.enviado_em is not None]
    if enviadas:
        ultima = max(enviadas, key=lambda c: c.enviado_em)
        return Comunicacao(
            forma=ultima.forma,
            instante=ultima.enviado_em,
            referencia=(ultima.referencia_da_publicacao or "").strip(),
        )
    if comunicacoes:
        # Só a mensagem falha: a publicação não tem envio que falhe.
        return Comunicacao(forma=comunicacoes[0].forma)
    if hasattr(convocacao, "forma_lida"):
        return Comunicacao(forma=convocacao.forma_lida)
    from processo_seletivo.convocacao.application.comunicar import forma_declarada

    return Comunicacao(forma=forma_declarada(convocacao))


def canal_de(convocacao):
    """As frases do canal desta convocação (FR-4004)."""
    from processo_seletivo.convocacao.domain import vocabulario_do_canal

    return vocabulario_do_canal.canal(comunicacao_de(convocacao).forma)


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
    habilitadas = ocupacao_selectors.habilitadas_pelo_corte(
        edital=edital, corte=corte, progrediram=ordem
    )
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


def comunicacao_da_linha(convocacao, forma_do_recorte):
    """A comunicação e as frases do canal de um cartão, **sem consulta** (125, FR-4000; `SC-088`).

    Com comunicação, a forma dela; sem nenhuma, a do recorte — que é a que a convocação citou,
    salvo Retificação no meio do caminho. `comunicacao_de` leria a versão de cada cartão sem
    comunicação, e a tela tem dezenas.
    """
    comunicacoes = list(convocacao.comunicacoes.all())
    if comunicacoes:
        comunicacao = comunicacao_de(convocacao)
    else:
        comunicacao = Comunicacao(forma=forma_do_recorte)
    return {
        "comunicacao": comunicacao,
        "canal": vocabulario_do_canal.canal(comunicacao.forma),
    }


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


def pessoas_chamadas(*, edital, perfil_id, marco_id, lista_id=None, at=None):
    """Quantas pessoas do recorte têm chamada em aberto ou atendida — a trava do desfazimento (097).

    **A ocupação pergunta, e a convocação responde** (`T-005`). Desfazer uma vaga acrescida não
    pode deixar sem vaga quem já recebeu a chamada, e quem foi chamado é fato desta feature, que a
    ocupação não conhece (`UX-034`). Quem encerrou — indeferimento, desistência, não atendimento,
    inércia — e o reclassificado não contam: nenhum deles espera a vaga.

    `at` é aceito pela forma da pergunta e não muda nada: as situações não dependem do relógio.
    """
    em_aberto, servidos, _, _ = _situacoes(
        convocacoes_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
    )
    return len(em_aberto | servidos)


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
    forma_do_recorte = _forma_do_recorte(vigentes_do_recorte)
    linhas = [
        {
            "inscricao": identificadas[convocacao.inscricao_id],
            "convocacao": convocacao,
            "desfecho": desfecho_de(convocacao),
            "enviadaEm": envio_de(convocacao),
            "estado": estado_de(convocacao, agora=agora),
            "comunicacoes": list(convocacao.comunicacoes.all()),
            "atestados": atestados.get(convocacao.inscricao_id, []),
            **comunicacao_da_linha(convocacao, forma_do_recorte),
        }
        for convocacao in vigentes_do_recorte
    ]
    # **Na ordem em que foram chamadas** (050). As do mesmo gesto nascem com o mesmo instante, e o
    # desempate pelo identificador embaralhava a lista a cada gesto. **Desempata a posição na
    # ordem**, e só depois o protocolo: com o protocolo primeiro, a 1ª colocada aparecia em último
    # e era a "Pessoa 3 de 3" na conferência (achado 14 do estudo de 11/11/2026). Quem não está
    # entre os alcançados — a chamada para regularizar — vem depois deles, pelo protocolo.
    posicao = {str(inscricao): n for n, inscricao in enumerate(contexto["alcancados"])}
    linhas.sort(
        key=lambda linha: (
            linha["convocacao"].criado_em,
            posicao.get(str(linha["convocacao"].inscricao_id), len(posicao)),
            linha["inscricao"]["protocolo"],
        )
    )
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
        "formaPorPublicacao": forma_do_recorte == FORMA_POR_PUBLICACAO,
        # As frases do canal do recorte (125, FR-4000), para o que a tela diz do recorte inteiro.
        "canal": vocabulario_do_canal.canal(forma_do_recorte),
        "formaDoRecorte": forma_do_recorte,
        "convocadas": len(vigentes_do_recorte),
        # **Quantas chamadas em cada estado**, para a tela dizer onde agir antes da lista (050). São
        # contagens de chamadas, e não de vagas: a contagem de ocupação continua sendo da `016`.
        "porEstado": {
            estado: sum(1 for linha in linhas if linha["estado"] == estado)
            for estado in (
                nomes.CONVOCADO_PRAZO_NAO_INICIADO,
                nomes.CONVOCADO_PRAZO_EM_CURSO,
                nomes.CONVOCADO_VENCIMENTO_DECORRIDO,
                nomes.DESFECHADO,
            )
        },
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
    "pessoas_chamadas",
    "reabilitados_por_deferimento",
    "vigentes",
]
