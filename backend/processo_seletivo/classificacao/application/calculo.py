"""Leitura do universo e cálculo da ordem, sem gravar ato, posição ou auditoria.

Todas as consultas acontecem antes do laço de participantes. Em particular, as Versões citadas
pelos Resultados são resolvidas uma vez por identidade distinta: fazer ``select_related('versao')``
traria uma cópia do JSON inteiro do Edital por Resultado sem alterar a contagem de consultas.
"""

from collections import defaultdict
from functools import reduce
from operator import or_

from django.db.models import Exists, OuterRef, Q

from processo_seletivo.classificacao.domain import universo_classificavel
from processo_seletivo.classificacao.domain.desempate import etapas_que_a_ordem_le, ordenar
from processo_seletivo.editais.domain import alcance as alcance_da_etapa
from processo_seletivo.editais.domain.recortes import normalizar_recorte
from processo_seletivo.inscricoes.models import Inscricao, ValorDeFato
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.application.prontidao import restringir_a_participantes
from processo_seletivo.resultados.application.selectors import conteudos_das_versoes
from processo_seletivo.resultados.domain import efeito as efeito_do_desfecho
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError


def calcular_ordem(*, edital, perfil_id, marco_id, lista_id=None, at=None):
    """Calcula a proposta vigente de **um recorte** do marco, e devolve a proveniência em memória.

    A função é deliberadamente read-only. Quem emite chama o mesmo cálculo dentro do comando
    transacional; abrir a tela pode chamá-la quantas vezes quiser, em quantos recortes forem, sem
    constituir ato algum (`FR-496`).

    **`lista_id` nulo é a ampla concorrência, e ela continua sendo o universo inteiro do Perfil**
    (`FR-492`, `FR-493`, `D-001`). Quem se autodeclarou numa Modalidade reservada **permanece**
    aqui: a cota preenche o que a ampla não preencheu, e é a ocupação que desconta da cota quem
    já ocupou pela ampla. Não é uma partição — é uma sobreposição, e ler isso ao contrário mudaria
    a ordem de todo Edital do acervo sem que teste algum de recorte reservado acusasse.

    **O padrão é o comportamento de antes desta feature**, e por isso Perfil sem Modalidade
    reservada produz exatamente a ordem que produzia: o único filtro novo é o que o recorte
    reservado acrescenta.
    """
    versao = effective_version(edital_id=edital.id, at=at)
    conteudo = versao.content
    perfil = _por_identidade(conteudo.get("profiles"), perfil_id)
    marco = _por_identidade(perfil.get("classificationMilestones") if perfil else None, marco_id)
    if perfil is None or marco is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    # **A recusa do recorte inexistente é aqui, e não só na tela** (`FR-499`). A porta do comando
    # também passa por este ponto, e fechar só a view deixaria a emissão alcançável por quem
    # tivesse o formulário antigo aberto. A normalização também reduz ao nulo a Modalidade que o
    # Perfil aponta como sendo a ampla: aceitar o apelido e nunca oferecê-lo é o que o corte já faz.
    recorte = normalizar_recorte(conteudo, perfil_id=perfil["id"], lista_id=lista_id)

    etapas = {str(item["id"]): item for item in conteudo.get("stages") or []}
    enumeradas = [str(item) for item in marco.get("stages") or []]
    etapa_do_marco = _ultima_etapa(enumeradas, etapas)
    # **As Etapas que um critério compara sem que o marco as enumere** (114, FR-3546). Entram só
    # na leitura dos Resultados — e daí na nota que o desempate compara e no universo que o ato
    # grava —, nunca na progressão acima nem no que decide quem tem posição (`preparar`, FR-3548).
    lidas = etapas_que_a_ordem_le(marco)

    consulta = _universo(edital, perfil, etapas, etapa_do_marco, enumeradas=enumeradas)
    # **O filtro do recorte reservado, e ele é o único acréscimo ao universo** (`FR-492`). Fica na
    # própria consulta, junto do resto: filtrar em memória depois de ler leria o Perfil inteiro por
    # recorte, e o projeto tem orçamento de consulta verificado por teste.
    if recorte is not None:
        consulta = _sem_retirada_anterior(
            consulta.filter(modality_id=recorte), etapas, etapa_do_marco
        )
    inscricoes = list(
        consulta.order_by("id").values("id", "protocolo", "nome", "identity_subject", "modality_id")
    )
    inscricoes_ids = [item["id"] for item in inscricoes]

    # **`vigentes`, e não `objects`** — e o `order_by` não é estilo (018, T-004). As duas coisas
    # corrigem defeitos **diferentes**, e a execução mostrou que confundi-los era fácil:
    #
    # 1. o dicionário de pontuações abaixo é indexado por `etapa_id`, e dois Resultados do mesmo
    #    par **colapsam** nele. Aqui quem corrige é o `order_by`: ordenando por `consolidado_em`,
    #    o último a entrar é o sucessor, que é justamente o vigente. Sem a ordenação, o colapso
    #    passa a depender da ordem em que o banco devolveu as linhas — e um defeito
    #    irreproduzível some da suíte;
    # 2. o **universo do ato**, montado adiante, grava o conjunto de ids dos Resultados que o
    #    produziram. Aqui o `order_by` não ajuda: sem o filtro, o universo cita o superado, e
    #    `comparar()` não vê mudança nenhuma quando o deferimento acontece. O ato **não fica
    #    obsoleto**, a publicação continua sendo oferecida, e a cadeia inteira a jusante fica cega
    #    ao recurso — que é o defeito pelo qual a alternativa 3 da decisão C foi descartada.
    #
    # É o segundo que torna o filtro indispensável, e é ele que o teste de regressão prende.
    #
    # **As Etapas do desempate vêm na mesma consulta** (114): uma consulta a mais por critério
    # estouraria o orçamento verificado por teste, e a nota que decide a ordem precisa estar no
    # universo pelo mesmo motivo do item 2 — sem ela, o recurso que a corrige não obsoleta nada.
    resultados = list(
        ResultadoEtapa.vigentes.filter(
            edital=edital,
            inscricao_id__in=inscricoes_ids,
            etapa_id__in=lidas,
        )
        .order_by("inscricao_id", "etapa_id", "consolidado_em", "id")
        .values(
            "id",
            "inscricao_id",
            "etapa_id",
            "versao_id",
            "pontuacao",
            "consequencia",
            "motivo",
            "consolidado_em",
        )
    )
    # Uma linha por versão distinta, e nenhuma cópia do conteúdo dentro da consulta de Resultados.
    conteudos_historicos = conteudos_das_versoes({item["versao_id"] for item in resultados})
    _conferir_ancoras_dos_resultados(resultados, conteudos_historicos)

    fatos_ids = _fatos_consumidos(marco)
    fatos = list(
        ValorDeFato.objects.filter(
            inscricao_id__in=inscricoes_ids,
            fato_id__in=fatos_ids,
        ).values("inscricao_id", "fato_id", "valor_data", "valor_inteiro")
    )

    resultados_por_inscricao = defaultdict(list)
    for resultado in resultados:
        resultados_por_inscricao[resultado["inscricao_id"]].append(resultado)
    fatos_por_inscricao = defaultdict(dict)
    for fato in fatos:
        fatos_por_inscricao[fato["inscricao_id"]][str(fato["fato_id"])] = (
            fato["valor_data"] if fato["valor_data"] is not None else fato["valor_inteiro"]
        )

    # **A decisão sobre quem tem posição mora em `universo_classificavel`**, que a prévia também
    # chama (094, D-004): uma montagem só do universo, e não duas que divergiriam em silêncio. Aqui
    # ficam as consultas — e a ordem dos Resultados de cada inscrição, que é a do `order_by` acima
    # e decide o colapso por Etapa.
    inscritos = [
        {
            "inscricao_id": str(inscricao["id"]),
            "protocolo": inscricao["protocolo"],
            "nome": inscricao["nome"],
            "identity_subject": inscricao["identity_subject"],
            "modalidade_id": (str(inscricao["modality_id"]) if inscricao["modality_id"] else None),
            "fatos": fatos_por_inscricao[inscricao["id"]],
            "resultados": resultados_por_inscricao[inscricao["id"]],
        }
        for inscricao in inscricoes
    ]
    classificaveis, sem_posicao = universo_classificavel.preparar(
        marco, etapas, inscritos, recorte=recorte
    )

    posicoes = ordenar(classificaveis, marco.get("tiebreakers") or [])
    return {
        "edital": edital,
        "versao": versao,
        "perfil": perfil,
        "marco": marco,
        # **O recorte, normalizado, viaja com a proposta** — é dele que a assinatura da confirmação
        # se distingue (`FR-495`). Dois recortes reservados vazios do mesmo marco produziriam
        # universo e ordem idênticos, e uma assinatura comum aceitaria no recorte B a leitura feita
        # no A. Não entra em `universo`: o ato já guarda o recorte na coluna `lista_id`, e
        # acrescentá-lo ao resumo faria a comparação de obsolescência de todo ato do acervo
        # confrontar um universo gravado sem a chave com um calculado com ela.
        "lista_id": recorte,
        "etapas": etapas,
        "posicoes": posicoes,
        "sem_posicao": sem_posicao,
        "universo": _resumo_do_universo(edital, perfil, marco, versao, inscricoes, resultados),
    }


def _sem_retirada_anterior(consulta, etapas, etapa_do_marco):
    """O universo de uma lista **reservada**, sem quem uma Etapa anterior retirou da reserva (164).

    É o par exato do que a eliminação faz em todas as listas (FR-7012): retirada antes da última
    Etapa que o marco enumera, a inscrição sai do universo da lista reservada, como a eliminada sai
    de todos; retirada **na** última enumerada, ela fica e sai sem posição, pela mão de
    `universo_classificavel.preparar`. A ampla nunca passa por aqui: ali a retirada não produz
    efeito nenhum.

    **Só as anteriores que podem retirar entram na subconsulta**, e sem nenhuma a consulta volta
    intacta: em todo Edital sem Etapa restrita e eliminatória que retire, a ordem é a de antes,
    sem `EXISTS` a mais.
    """
    limite = etapa_do_marco.get("order") or 0
    que_retiram = [
        etapa["id"]
        for etapa in etapas.values()
        if (etapa.get("order") or 0) < limite and efeito_do_desfecho.pode_retirar(etapa)
    ]
    if not que_retiram:
        return consulta
    return consulta.exclude(
        Exists(
            ResultadoEtapa.vigentes.filter(
                inscricao_id=OuterRef("pk"),
                etapa_id__in=que_retiram,
                consequencia=ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA,
            )
        )
    )


def _universo(edital, perfil, etapas, etapa_do_marco, *, conteudo=None, enumeradas=()):
    """As inscrições que concorrem no marco, antes do filtro do recorte.

    A progressão é aplicada no próprio queryset: nenhuma lista integral é lida uma segunda vez só
    para ser devolvida em ``id__in``. O conjunto inclui quem foi eliminado na Etapa do marco e
    exclui quem já havia sido eliminado antes dela. O filtro do recorte entra depois, em quem
    chama.

    `conteudo`, quando quem chama já o leu, poupa à condição do corte a releitura do conteúdo
    vigente (135, a revisão do PR #441).

    `enumeradas` são as Etapas do marco, e só pesam quando a última delas é restrita (163).
    """
    consulta = Inscricao.objects.filter(
        edital=edital,
        profile_id=perfil["id"],
        status=Inscricao.Status.SUBMETIDA,
    )
    vigentes = {_uuid_da_etapa(chave): valor for chave, valor in etapas.items()}
    if not alcance_da_etapa.restrita(etapa_do_marco):
        return restringir_a_participantes(
            consulta,
            edital=edital,
            etapa_id=etapa_do_marco["id"],
            vigentes=vigentes,
            prefixo="",
            conteudo=conteudo,
        )
    return _universo_por_alcance(consulta, edital, etapas, vigentes, enumeradas, conteudo=conteudo)


def _universo_por_alcance(consulta, edital, etapas, vigentes, enumeradas, *, conteudo=None):
    """Quando a última Etapa enumerada é restrita, cada inscrição é decidida pela última que a
    alcança (163, FR-6985).

    Perguntar só à última, como antes, devolveria só as inscrições que ela alcança — com a
    Heteroidentificação por última enumerada, a ordem da ampla sairia vazia. Da última para a
    primeira, cada Etapa decide sobre as Modalidades que alcança e que nenhuma posterior decidiu; a
    sobra, que nenhuma enumerada alcança, entra como entraria num marco sem Etapa: a inscrição
    submetida do Perfil. Uma consulta, por disjunção de subconsultas — nenhuma lista materializada.

    **A eliminação nas Etapas que o marco não enumera continua valendo para todos** (D-010,
    FR-6971). Ler a ampla na Análise não pode esquecer a Entrevista, fora do marco, que veio depois
    dela e antes da última enumerada: perguntar à última, como antes, a excluía.
    """
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo if conteudo is not None else conteudo_vigente(edital)
    ordenadas = sorted(
        (etapas[item] for item in enumeradas if item in etapas),
        key=lambda etapa: etapa.get("order") or 0,
        reverse=True,
    )
    partes = []
    decididas = frozenset()
    for etapa in ordenadas:
        parte = restringir_a_participantes(
            consulta,
            edital=edital,
            etapa_id=etapa["id"],
            vigentes=vigentes,
            prefixo="",
            conteudo=conteudo,
        )
        if decididas:
            parte = parte.exclude(modality_id__in=list(decididas))
        partes.append(Q(pk__in=parte.values("pk")))
        alcancadas = alcance_da_etapa.modalidades_alcancadas(conteudo, etapa)
        if alcancadas is None:
            break
        decididas = decididas | alcancadas
    else:
        sobra = consulta.exclude(modality_id__in=list(decididas)) if decididas else consulta
        partes.append(Q(pk__in=sobra.values("pk")))
    consulta = consulta.filter(reduce(or_, partes))
    enumeradas_ids = {str(etapa["id"]) for etapa in ordenadas}
    ultima = (ordenadas[0].get("order") or 0) if ordenadas else 0
    fora_do_marco = [
        identidade
        for identidade, etapa in vigentes.items()
        if str(identidade) not in enumeradas_ids and (etapa.get("order") or 0) < ultima
    ]
    if fora_do_marco:
        consulta = consulta.filter(
            ~Exists(
                ResultadoEtapa.vigentes.filter(
                    inscricao_id=OuterRef("pk"),
                    etapa_id__in=fora_do_marco,
                    consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
                )
            )
        )
    return consulta


def listas_sem_concorrente(*, edital, conteudo, perfil_id, marco_id):
    """As listas reservadas do marco em que ninguém concorre — `{lista_id}`, sem a ampla (135).

    **É a pergunta da tela da ordenação, sem calcular a ordem** (FR-4670, R-001). A tela diz
    "Ninguém concorreu por este recorte" quando o recorte é reservado e a proposta de
    `calcular_ordem` não tem ninguém, com posição ou sem. `universo_classificavel.preparar` põe toda
    inscrição do universo numa das duas, e por isso a proposta é vazia exatamente quando o universo
    filtrado pelo recorte é vazio. Aqui o universo é o mesmo (`_universo`), perguntado **uma vez
    para o marco**: as Modalidades distintas de quem concorre. Calcular a ordem de cada lista leria
    Resultados e fatos de cada inscrição só para contá-las (FR-4686).

    **Custa até duas consultas, e nenhuma por inscrição**: a do gate da progressão, quando a Etapa
    anterior exige habilitação, e a das Modalidades. O conteúdo que chega é repassado à condição do
    corte, que de outro modo o releria.

    A ampla fica fora, como na tela: a ampla vazia é um Perfil sem inscrição nenhuma, outro assunto.
    O marco que `calcular_ordem` recusaria (sem Etapa executável) não tem lista vazia: a recusa é da
    tela do ato, e a lista vazia não pode escondê-la.
    """
    from processo_seletivo.editais.domain.recortes import recortes_do_perfil

    perfil = _por_identidade(conteudo.get("profiles"), perfil_id)
    marco = _por_identidade(perfil.get("classificationMilestones") if perfil else None, marco_id)
    if perfil is None or marco is None:
        return set()
    etapas = {str(item["id"]): item for item in conteudo.get("stages") or []}
    try:
        etapa_do_marco = _ultima_etapa([str(item) for item in marco.get("stages") or []], etapas)
    except DomainError:
        return set()
    # `recortes_do_perfil` já devolve a grafia canônica, sem a ampla declarada.
    reservadas = {
        lista for lista, _ in recortes_do_perfil(conteudo, perfil_id=perfil["id"]) if lista
    }
    if not reservadas:
        return set()
    # A pergunta é das listas reservadas, e por isso o universo é o delas: sem quem uma Etapa
    # anterior retirou da reserva (164, FR-7012). A lista que só tinha retirados está vazia.
    concorrem = {
        str(modalidade)
        for modalidade in _sem_retirada_anterior(
            _universo(
                edital,
                perfil,
                etapas,
                etapa_do_marco,
                conteudo=conteudo,
                enumeradas=[str(item) for item in marco.get("stages") or []],
            ),
            etapas,
            etapa_do_marco,
        )
        .order_by()
        .values_list("modality_id", flat=True)
        .distinct()
        if modalidade
    }
    return reservadas - concorrem


def _por_identidade(itens, identidade):
    alvo = str(identidade)
    return next((item for item in itens or [] if str(item.get("id")) == alvo), None)


def _uuid_da_etapa(valor):
    from uuid import UUID

    return UUID(str(valor))


def _ultima_etapa(enumeradas, etapas):
    existentes = [etapas[item] for item in enumeradas if item in etapas]
    if not existentes:
        raise DomainError(
            "marco_sem_etapa",
            "O marco não enumera uma Etapa publicada executável.",
            422,
        )
    return max(existentes, key=lambda item: item.get("order") or 0)


def _conferir_ancoras_dos_resultados(resultados, conteudos):
    """Cada Resultado precisa citar uma versão em que a sua Etapa realmente existia."""
    for resultado in resultados:
        conteudo = conteudos.get(resultado["versao_id"])
        if (
            conteudo is None
            or _por_identidade(conteudo.get("stages"), resultado["etapa_id"]) is None
        ):
            raise DomainError(
                "resultado_sem_norma",
                "Um Resultado do universo não encontra sua Etapa na versão que o fundamentou.",
                409,
            )


def _fatos_consumidos(marco):
    return {
        str((criterio.get("parameters") or {}).get("factId"))
        for criterio in marco.get("tiebreakers") or []
        if (criterio.get("parameters") or {}).get("factId")
    }


def _resumo_do_universo(edital, perfil, marco, versao, inscricoes, resultados):
    return {
        "processoId": str(edital.processo_id),
        "editalId": str(edital.id),
        "profileId": str(perfil["id"]),
        "milestoneId": str(marco["id"]),
        "versionId": str(versao.id),
        "participants": [str(item["id"]) for item in inscricoes],
        "stageResults": [
            {
                "id": str(item["id"]),
                "registrationId": str(item["inscricao_id"]),
                "stageId": str(item["etapa_id"]),
                "versionId": str(item["versao_id"]),
                "consolidatedAt": item["consolidado_em"].isoformat(),
            }
            for item in sorted(resultados, key=lambda item: str(item["id"]))
        ],
    }


__all__ = ["calcular_ordem", "listas_sem_concorrente"]
