"""Leitura do vigente, da proposta atual e da divergência entre os dois."""

from django.core.paginator import Paginator
from django.db.models import F

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.domain.nomes import edital_por_extenso, nomes_do_marco
from processo_seletivo.classificacao.domain.universo import (
    comparar,
    por_identidade,
    recorte_da_regra,
)
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    criterio_por_extenso,
    por_identificador,
)
from processo_seletivo.shared.api.problems import DomainError

# O que um ato de sorteio grava em `universo["origem"]` (021, FR-069). Lido daqui e não do modelo
# para que a leitura não passe a depender do app do sorteio: a direção é `sorteios → classificacao`,
# e nunca o contrário.
ORIGEM_SORTEIO = "SORTEIO"


def ato_vigente(*, edital, marco_id, lista_id=None):
    """O ato sem sucessor daquele recorte, derivado da cadeia append-only.

    **`lista_id` deixou de ser opcional no sentido que importa** (021, D-006, FR-069). Desde que
    três listas de concorrência podem produzir três atos raiz no mesmo marco, "o vigente do marco"
    não é pergunta com uma resposta: sem filtrar pela lista, `.first()` escolheria uma das três pela
    ordem de emissão, que é sorteio de dado — e a tela mostraria a ordem de outra lista sem que nada
    acusasse.

    O padrão `None` é a ampla concorrência, que é o que todo ato emitido antes da `021` é: quem
    chamava sem o argumento continua recebendo exatamente o ato que recebia.
    """
    return (
        AtoDeOrdenacao.objects.filter(
            edital=edital,
            marco_id=marco_id,
            lista_id=lista_id,
            sucessores__isnull=True,
        )
        .select_related("versao")
        .order_by("-emitido_em")
        .first()
    )


def _estado_do_marco_sorteado(*, edital, marco_id, vigente, at):
    """O estado de um marco cujo ato veio de sorteio — que **não** se afere recomputando (FR-069).

    `calcular_ordem` produz a ordem por Etapas. Um ato de sorteio não veio dali, e comparar os dois
    acusaria divergência a cada mudança de Etapa num marco que não depende de Etapa nenhuma: a
    publicabilidade recusaria toda ordem sorteada como obsoleta, e o certame com sorteio nunca
    divulgaria.

    **A pergunta continua sendo a mesma** — "o ato ainda reflete o fato que o originou?" —, e só o
    fato de origem muda: para o ato computado é o cálculo por Etapas; para o sorteado é a **relação
    de habilitados**, que foi sucedida ou não. Uma relação sucedida depois do sorteio significa que
    o universo comprometido mudou, e a ordem publicada já não corresponde a ele.

    `proposta` é `None` de propósito, e é o que a tela usa para não oferecer "recalcular": não há o
    que recalcular sem semente nova, e oferecer o botão seria oferecer o ensaio que a D-010 proíbe.
    """
    versao_atual = effective_version(edital_id=edital.id, at=at)
    perfil, marco = _marco_na_versao(versao_atual.content, marco_id)
    perfil_historico, marco_historico = _marco_na_versao(vigente.versao.content, marco_id)
    if marco is None:
        # **O marco removido é impedimento igual, e a resposta é a mesma que o caminho computado
        # já dava.** Devolver a forma dele aqui — sem a chave `origem` — é o que faz `aferir` cair
        # no mesmo degrau, em vez de precisar de um segundo ramo dizendo a mesma coisa.
        return _marco_removido(vigente, perfil_historico, marco_historico)
    divergencias = _divergencias_do_sorteio(vigente)
    return {
        "proposta": None,
        "vigente": vigente,
        "perfil": perfil,
        "marco": marco,
        "obsoleto": bool(divergencias),
        # Não é recomputável, e dizer isso é o ponto: quem lê este dicionário não deve oferecer
        # recálculo de uma ordem que só uma semente nova produziria (D-010).
        "recomputavel": False,
        # **A chave que faz `aferir` distinguir "não recomputável" de "marco removido".** Sem ela,
        # todo ato de sorteio seria recusado como se o marco tivesse sumido da norma.
        "origem": ORIGEM_SORTEIO,
        "divergencias": divergencias,
        "posicoes_divergentes": [],
    }


def _estado_do_marco_que_sorteia(*, perfil, marco, vigente):
    """O marco declara sorteio, e ainda não há ato de sorteio: **não há o que recomputar aqui**.

    **É o buraco por onde o certame se travava.** O detalhe do Edital manda todo marco para a tela
    de ordenação; sem ato, o estado dizia `recomputavel=True`, a tela oferecia "Emitir ordem", e o
    cálculo por Etapas de um marco que não ordena por Etapas produzia um ato raiz do recorte. Dali
    em diante `constituir_sorteio` recusava — corretamente, com `ordering_act_already_exists` —, e
    o sucessor exigia um sorteio anterior que nunca existiu: o sorteio ficava inalcançável pela
    própria tela, que é o modo de falha que a Constituição §VI nomeia.

    `proposta` é `None` e `recomputavel` é `False` pela mesma razão do ato já sorteado: a ordem
    deste marco nasce de uma semente que ainda não existe, e nenhuma quantidade de cálculo por
    Etapas a produz.

    **`origem` viaja mesmo sem ato de sorteio**, e é o que impede `aferir` de anunciar "marco
    removido" — que é o que ele diria de qualquer coisa não recomputável, e seria falso duas vezes.

    Um ato **computado** vivo neste marco é divergência nomeada, e não silêncio: ele é o defeito
    consumado, e quem o vê precisa saber que a ordem vigente não veio de onde a norma manda.
    """
    divergencias = []
    if vigente is not None and (vigente.universo or {}).get("origem") != ORIGEM_SORTEIO:
        divergencias = [
            {
                "tipo": "ordem_computada_em_marco_de_sorteio",
                "descricao": (
                    "O Edital declara que este marco ordena por sorteio, e o ato vigente foi "
                    "computado a partir de Etapas. A ordem publicada não veio da regra que a "
                    "norma declara."
                ),
            }
        ]
    return {
        "proposta": None,
        "vigente": vigente,
        "perfil": perfil,
        "marco": marco,
        "obsoleto": bool(divergencias),
        "recomputavel": False,
        "origem": ORIGEM_SORTEIO,
        "divergencias": divergencias,
        "posicoes_divergentes": [],
    }


def _marco_removido(vigente, perfil_historico, marco_historico):
    return {
        "proposta": None,
        "vigente": vigente,
        "perfil": perfil_historico or {"id": str(vigente.perfil_id), "name": "Perfil"},
        "marco": marco_historico or {"id": str(vigente.marco_id), "name": "Marco removido"},
        "obsoleto": True,
        "recomputavel": False,
        "divergencias": [
            {
                "tipo": "regra_ausente",
                "descricao": (
                    "O marco não existe na norma vigente; não há regra vigente com que comparar."
                ),
            }
        ],
        "posicoes_divergentes": [],
    }


def _divergencias_do_sorteio(vigente):
    """A obsolescência de um ato sorteado é a da relação que o originou, e nada mais.

    **E a ausência da relação é divergência, não silêncio.** Esta função devolvia `[]` quando o
    `universo` não trazia `relacaoId` ou quando a identidade apontava para relação inexistente — as
    duas situações que mais precisam ser ditas. Um ato de origem `SORTEIO` cuja proveniência não
    resolve não é um ato íntegro sobre o qual nada há a observar: é um ato que ninguém consegue
    conferir, e chamá-lo de não obsoleto seria falhar aberto justamente onde a feature promete o
    contrário.
    """
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados

    identidade = (vigente.universo or {}).get("relacaoId")
    if not identidade:
        return [
            {
                "tipo": "proveniencia_ausente",
                "descricao": (
                    "Este ato declara origem por sorteio e não cita a relação de habilitados que "
                    "o originou. Sem ela, a ordem publicada não é conferível contra universo "
                    "algum."
                ),
            }
        ]
    relacao = RelacaoDeHabilitados.objects.filter(pk=identidade).first()
    if relacao is None:
        return [
            {
                "tipo": "proveniencia_inexistente",
                "descricao": (
                    "A relação de habilitados que este ato cita não existe. A proveniência do "
                    "sorteio não resolve, e a ordem publicada não é conferível."
                ),
            }
        ]
    if not relacao.sucessoras.exists():
        return []
    return [
        {
            "tipo": "relacao_sucedida",
            "descricao": (
                "A relação de habilitados que originou este sorteio foi sucedida; a ordem "
                "publicada já não corresponde ao universo comprometido. Um sorteio novo nasce de "
                "relação nova e de ocorrência nova."
            ),
        }
    ]


def historico(*, edital, marco_id):
    return list(
        AtoDeOrdenacao.objects.filter(edital=edital, marco_id=marco_id)
        .select_related("versao", "ato_anterior")
        .order_by("-emitido_em")
    )


def ato_por_id(*, edital, marco_id, ato_id):
    return (
        AtoDeOrdenacao.objects.filter(
            pk=ato_id,
            edital=edital,
            marco_id=marco_id,
        )
        .select_related("versao", "ato_anterior")
        .first()
    )


def sucessor_de(ato):
    """O ato que sucedeu este, ou ``None``. A cadeia é append-only e o sucessor é no máximo um.

    Quem abre um ato histórico precisa saber disso **antes** de citá-lo: os valores continuam
    íntegros e vigentes na sua data, mas já não são a ordem que produz efeito (E2E15-010).
    """
    return ato.sucessores.order_by("emitido_em").first()


def nomes_do_ato(ato):
    """Como a versão que o ato **cita** nomeia o que ele identifica por UUID.

    A leitura é da versão congelada, e nunca da vigente: uma Retificação posterior que renomeie o
    perfil, o marco ou o Edital não pode reescrever retroativamente como um ato antigo é lido. Os
    nomes acompanham os identificadores na proveniência — não os substituem —, porque ali o UUID
    é a âncora de auditoria (E2E15-006).
    """
    conteudo = ato.versao.content
    nomes = nomes_do_marco(conteudo, perfil_id=ato.perfil_id, marco_id=ato.marco_id)
    return {
        "processo": nomes["processo"],
        "edital": edital_por_extenso(conteudo, ato.edital),
        "perfil": nomes["perfil"].get("name", "") or "",
        "marco": nomes["marco"].get("name", "") or "",
    }


def nomear_criterios(linhas, ato):
    """Acrescenta a cada critério do desempate a frase publicada que o nomeia (FR-050, SC-010).

    O snapshot guarda `type` e `criterionId`, e não a grafia: a tabela imprimia
    `MAIOR_VALOR_DE_FATO` sem dizer o que ele compara, que é justamente o que a FR-050 exige que a
    consulta mostre. O critério é localizado por `criterionId` na versão que **o ato cita** — mesmo
    princípio das modalidades e do marco: renomear um fato hoje não pode mudar o que um ato antigo
    diz ter comparado.

    A decoração é em memória e sobre `PosicaoNaOrdem`, que é append-only e recusa `save`: ela não
    tem como alcançar o banco.
    """
    conteudo = ato.versao.content
    nomes = nomes_do_marco(conteudo, perfil_id=ato.perfil_id, marco_id=ato.marco_id)
    etapas = por_identificador(conteudo.get("stages"))
    fatos = por_identificador(nomes["perfil"].get("declaredFacts"))
    rotulos = {
        str(criterio.get("id")): criterio_por_extenso(criterio, etapas, fatos)
        for criterio in nomes["marco"].get("tiebreakers") or []
    }
    for linha in linhas:
        for criterio in linha.desempate or []:
            criterio["rotulo"] = rotulos.get(str(criterio.get("criterionId")), "")
    return linhas


def estado_do_marco(*, edital, marco_id, at=None, lista_id=None):
    """A proposta de agora ao lado do ato vigente, sem escrever nenhum dos dois."""
    vigente = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if vigente is not None and (vigente.universo or {}).get("origem") == ORIGEM_SORTEIO:
        return _estado_do_marco_sorteado(edital=edital, marco_id=marco_id, vigente=vigente, at=at)
    versao_atual = effective_version(edital_id=edital.id, at=at)
    perfil, marco = _marco_na_versao(versao_atual.content, marco_id)

    if marco is None:
        if vigente is None:
            raise DomainError("not_found", "Recurso não encontrado.", 404)
        perfil_historico, marco_historico = _marco_na_versao(
            vigente.versao.content,
            marco_id,
        )
        return {
            "proposta": None,
            "vigente": vigente,
            "perfil": perfil_historico or {"id": str(vigente.perfil_id), "name": "Perfil"},
            "marco": marco_historico or {"id": str(vigente.marco_id), "name": "Marco removido"},
            "obsoleto": True,
            "recomputavel": False,
            "divergencias": [
                {
                    "tipo": "regra_ausente",
                    "descricao": (
                        "O marco não existe na norma vigente; "
                        "não há regra vigente com que comparar."
                    ),
                }
            ],
            "posicoes_divergentes": [],
        }

    # **O marco que declara sorteio não passa pelo motor de Etapas**, tenha ou não ato ainda. Ler
    # `drawMethod` aqui é ler conteúdo publicado — não é dependência do app do sorteio, que continua
    # sendo `sorteios → classificacao` e nunca o contrário (021, D-013).
    if marco.get("drawMethod"):
        return _estado_do_marco_que_sorteia(perfil=perfil, marco=marco, vigente=vigente)

    proposta = calcular_ordem(
        edital=edital,
        perfil_id=perfil["id"],
        marco_id=marco_id,
        at=at,
    )
    divergencias = []
    if vigente is not None:
        divergencias = comparar(
            gravado=vigente.universo,
            atual=proposta["universo"],
            regra_gravada=recorte_da_regra(
                vigente.versao.content,
                perfil_id=vigente.perfil_id,
                marco_id=vigente.marco_id,
            ),
            regra_atual=recorte_da_regra(
                versao_atual.content,
                perfil_id=perfil["id"],
                marco_id=marco_id,
            ),
            reingressos=_reingressos(edital, proposta),
        )
    _nomear_modalidades(proposta, versao_atual.content, perfil_id=perfil["id"], marco_id=marco_id)
    return {
        "proposta": proposta,
        "vigente": vigente,
        "perfil": perfil,
        "marco": marco,
        "obsoleto": bool(divergencias),
        "recomputavel": True,
        "divergencias": divergencias,
        "posicoes_divergentes": (
            _divergencias_das_posicoes(vigente, proposta) if vigente is not None else []
        ),
    }


def posicoes_do_ato(*, ato, pagina=1, por_pagina=50):
    """Snapshot paginado; valores nulos vêm depois da ordem classificatória."""
    consulta = (
        PosicaoNaOrdem.objects.filter(ato=ato)
        .select_related("inscricao")
        .order_by(
            F("posicao").asc(nulls_last=True),
            "inscricao__protocolo",
            "inscricao_id",
        )
    )
    return Paginator(consulta, por_pagina).get_page(pagina)


def _marco_na_versao(conteudo, marco_id):
    alvo = str(marco_id)
    for perfil in conteudo.get("profiles") or []:
        marco = por_identidade(perfil.get("classificationMilestones"), alvo)
        if marco is not None:
            return perfil, marco
    return None, None


def _nomear_modalidades(proposta, conteudo, *, perfil_id, marco_id):
    """Acrescenta a cada posição o **nome** que a versão em vigor dá à sua modalidade.

    A fonte é a versão que calculou esta proposta, e não a que algum ato citou: o que a tela
    mostra aqui é a ordem de agora, sob a norma de agora. A tela não resolve identificador
    nenhum — imprimia o UUID justamente porque ninguém o resolvia antes dela (E2E15-006).

    O rótulo é apresentação e **não entra na assinatura da proposta**, que é lida por chaves
    nomeadas; é o que permite decorar as linhas aqui sem que a confirmação do cálculo mude de
    valor entre a conferência na tela e a emissão.
    """
    modalidades = nomes_do_marco(conteudo, perfil_id=perfil_id, marco_id=marco_id)["modalidades"]
    for linha in proposta["posicoes"]:
        linha["modalidade"] = modalidades.get(str(linha["modalidade_id"]), "")


def _divergencias_das_posicoes(ato, proposta):
    """Mudanças linha a linha entre o snapshot e a proposta calculada agora."""
    antes = {
        str(item["inscricao_id"]): item
        for item in PosicaoNaOrdem.objects.filter(ato=ato).values(
            "inscricao_id",
            "posicao",
            "pontuacao_combinada",
            "consequencia",
            "motivo",
            "empate_residual",
            # O protocolo entra pela consulta do snapshot porque é o único lado que enxerga quem
            # **saiu** do universo: essa inscrição não tem linha na proposta de agora, e sem isto
            # a tela só teria o UUID dela para mostrar (E2E15-006).
            "inscricao__protocolo",
        )
    }
    depois = {item["inscricao_id"]: item for item in proposta["posicoes"] + proposta["sem_posicao"]}
    divergencias = []
    for inscricao_id in sorted(set(antes) | set(depois)):
        anterior = antes.get(inscricao_id)
        atual = depois.get(inscricao_id)
        assinatura_anterior = (
            None
            if anterior is None
            else (
                anterior["posicao"],
                anterior["pontuacao_combinada"],
                anterior["consequencia"],
                anterior["motivo"],
                anterior["empate_residual"],
            )
        )
        assinatura_atual = (
            None
            if atual is None
            else (
                atual["posicao"],
                atual["pontuacao"],
                atual["consequencia"],
                atual["motivo"],
                atual["empate_residual"],
            )
        )
        if assinatura_anterior != assinatura_atual:
            divergencias.append(
                {
                    "inscricao_id": inscricao_id,
                    "protocolo": (
                        (anterior or {}).get("inscricao__protocolo")
                        or (atual or {}).get("protocolo")
                        or ""
                    ),
                    "antes": _lado(anterior, "pontuacao_combinada"),
                    "agora": _lado(atual, "pontuacao"),
                }
            )
    return divergencias


def _lado(linha, campo_da_pontuacao):
    """Um lado do diff com as chaves que o outro também tem.

    O snapshot chama o valor de `pontuacao_combinada`; a proposta calculada chama o mesmo valor de
    `pontuacao`. Uniformizar aqui é o que permite à tela ler os dois lados com uma linha só, em vez
    de saber de qual deles cada nome veio — e é o que faltava para a pontuação **caber** na tabela:
    ela comparava só a posição, e uma Retificação de peso que dobra a nota sem trocar ninguém de
    lugar aparecia como "1º → 1º", sem nada que explicasse a divergência apontada (E2E15-011).
    """
    if linha is None:
        return None
    return {
        "posicao": linha["posicao"],
        "pontuacao": linha[campo_da_pontuacao],
        "motivo": linha["motivo"],
    }


__all__ = [
    "ato_por_id",
    "ato_vigente",
    "estado_do_marco",
    "historico",
    "nomear_criterios",
    "nomes_do_ato",
    "posicoes_do_ato",
    "sucessor_de",
]


def _reingressos(edital, proposta):
    """Quem voltou ao universo porque um recurso removeu a eliminação que a excluía (FR-078).

    Uma consulta só, e restrita às inscrições do universo proposto: perguntar por linha seria o
    custo por linha que a 012 recusou, e perguntar pelo Edital inteiro leria o que a tela não usa.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    participantes = [str(item) for item in (proposta["universo"].get("participants") or [])]
    if not participantes:
        return frozenset()
    return frozenset(
        str(identificador)
        for identificador in ResultadoEtapa.vigentes.filter(
            edital=edital,
            inscricao_id__in=participantes,
            resultado_anterior__isnull=False,
        ).values_list("inscricao_id", flat=True)
    )
