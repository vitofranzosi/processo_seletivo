"""A leitura da ocupação: a apuração vigente, as causas de obsolescência e os três números.

**Vigente é derivada, e obsolescência é calculada.** Nenhuma das duas é coluna, porque mantê-las
exigiria `UPDATE` numa tabela append-only — o provisionamento instala e verifica a proibição. É o
mesmo desenho de `classificacao/application/corte.py`, e as causas vêm **nomeadas**, nunca como
"divergências": a `018` já pagou esse preço.
"""

from processo_seletivo.classificacao.application.corte import geracao_vigente, linha_do_quadro
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.models import ItemDoCorte
from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.models import ResultadoEtapa


def apuracao_vigente(*, edital, perfil_id, marco_id, lista_id=None):
    """A apuração que ninguém sucedeu no recorte, ou `None`.

    **Vigente não é coluna**: é a linha sem sucessora. Uma flag exigiria `UPDATE`, e a constraint
    `uq_apuracao_sucessora_unica` é o que garante que esta pergunta tem no máximo uma resposta —
    sem ela, duas apurações sucederiam a mesma anterior e o recorte teria duas vigentes.
    """
    return (
        ApuracaoDeOcupacao.objects.filter(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
        .filter(sucessoras__isnull=True)
        .order_by("-emitida_em")
        .first()
    )


def movimentos_lidos_por(apuracao):
    """`(especie, recebida, quantidade)` dos movimentos que **aquela** apuração congelou.

    Lê os ids de `universo.movimentosLidos`, e não "os movimentos de hoje": é o que torna a
    reprodução determinística (`FR-244`). Uma apuração antiga relida hoje devolve o número que ela
    apurou, e não o que o mundo virou depois.
    """
    ids = (apuracao.universo or {}).get("movimentosLidos") or []
    if not ids:
        return []
    encontrados = {str(m.id): m for m in MovimentoDeVaga.objects.filter(id__in=ids)}
    lidos = []
    for identidade in ids:
        movimento = encontrados.get(str(identidade))
        if movimento is None:
            continue
        recebida = calculo.mesma_lista(movimento.destino_lista_id, apuracao.lista_id)
        lidos.append((movimento.especie, recebida, movimento.quantidade))
    return lidos


def causas_de_obsolescencia(apuracao, *, at=None):
    """As **quatro** causas, nomeadas (`FR-263`).

    A quarta — movimento posterior que alcança o recorte — é o que dispensa orquestração: a reversão
    não precisa disparar, em cascata, a emissão do destino. O destino aparece obsoleto, com a causa
    dita, e quem quiser o número novo emite. Reusar a obsolescência que já existe custa uma causa;
    obrigar emissão encadeada custaria uma orquestração entre dois recortes.
    """
    if apuracao is None:
        return []
    causas = []
    edital = apuracao.edital
    ato = ato_vigente(edital=edital, marco_id=apuracao.marco_id, lista_id=apuracao.lista_id)
    if ato is None or ato.id != apuracao.ato_id:
        causas.append(
            {
                "causa": nomes.CAUSA_ORDEM_SUCEDIDA,
                "descricao": "A ordem deste recorte foi sucedida depois desta apuração.",
            }
        )
    estado = estado_do_marco(
        edital=edital, marco_id=apuracao.marco_id, at=at, lista_id=apuracao.lista_id
    )
    if estado.get("obsoleto"):
        causas.append(
            {
                "causa": nomes.CAUSA_ORDEM_SUCEDIDA,
                "descricao": "A ordem deste recorte está obsoleta.",
            }
        )
    if apuracao.corte_id is not None:
        geracao = geracao_vigente(
            edital=edital,
            perfil_id=apuracao.perfil_id,
            marco_id=apuracao.marco_id,
            lista_id=apuracao.lista_id,
        )
        vigentes = {item.id for item in geracao}
        if apuracao.corte_id not in vigentes:
            causas.append(
                {
                    "causa": nomes.CAUSA_CORTE_OBSOLETO,
                    "descricao": "O corte que alimentou esta apuração não é mais o vigente.",
                }
            )
    if _quadro_retificado(apuracao, at=at):
        causas.append(
            {
                "causa": nomes.CAUSA_QUADRO_RETIFICADO,
                "descricao": "A linha do quadro que esta apuração leu mudou por Retificação.",
            }
        )
    if _movimento_posterior(apuracao):
        causas.append(
            {
                "causa": nomes.CAUSA_MOVIMENTO_POSTERIOR,
                "descricao": "Um movimento de vaga alcançou este recorte depois desta apuração.",
            }
        )
    return causas


def ocupacao_do_recorte(*, edital, perfil_id, marco_id, lista_id=None, at=None):
    """Os quatro números e o estado do recorte, para a tela e para o contrato (`UX-031`).

    **`faltando` é calculado aqui**, e não lido de coluna: é `efetivas - ocupadas`, aritmética da
    mesma linha. `efetivas` vem de coluna porque depende de somar movimentos, e `CHECK` não agrega.
    """
    versao = effective_version(edital_id=edital.id, at=at)
    linha = linha_do_quadro(versao.content, perfil_id=perfil_id, lista_id=lista_id)
    vigente = apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    causas = causas_de_obsolescencia(vigente, at=at)
    estado = calculo.estado(
        tem_quadro=linha is not None,
        tem_apuracao=vigente is not None,
        causas_de_obsolescencia=causas,
    )
    # **Quantidade que nenhum ato produziu vem nula, e nunca zero.** Zero é uma afirmação — "não há
    # vaga a ocupar" —, e sem apuração emitida ninguém afirmou isso. Colapsar o estado em zero é o
    # que o contrato proíbe, e seria "ler ocupa" pela porta dos fundos: a tela passaria a dizer um
    # número que ato nenhum sustenta, contra a `FR-259` e contra a `FR-261`.
    #
    # `publicadas` é a exceção, e por uma razão: ela **não** vem de apuração. Sai da linha do quadro
    # publicado, que é fato normativo do Edital e é rastreável a ele. Dizer "o Edital publicou 3
    # vagas neste recorte, e a ocupação ainda não foi apurada" é verdadeiro nas duas metades.
    sem_apuracao = vigente is None
    return {
        "perfilId": str(perfil_id),
        "marcoId": str(marco_id),
        "listaId": str(lista_id) if lista_id else None,
        "publicadas": _quantidade(linha) if sem_apuracao else vigente.publicadas,
        "efetivas": None if sem_apuracao else vigente.efetivas,
        "ocupadas": None if sem_apuracao else vigente.ocupadas,
        "faltando": None if sem_apuracao else vigente.faltando,
        "estado": estado,
        "causasDeObsolescencia": [item["causa"] for item in causas],
        # **Os movimentos que a apuração vigente leu**, e não os de hoje: a tela mostra o que o ato
        # considerou, que é o mesmo critério da `FR-244`. Movimento posterior aparece como causa de
        # obsolescência, e não como linha que o número não explica.
        "movimentos": _movimentos_lidos_por_apuracao(vigente),
        "apuracao": vigente,
    }


def _movimentos_lidos_por_apuracao(apuracao):
    if apuracao is None:
        return []
    ids = (apuracao.universo or {}).get("movimentosLidos") or []
    if not ids:
        return []
    encontrados = {str(m.id): m for m in MovimentoDeVaga.objects.filter(id__in=ids)}
    return [encontrados[str(i)] for i in ids if str(i) in encontrados]


def recortes_do_marco(*, edital, perfil_id, marco_id, at=None):
    """Todo recorte do marco, com os quatro números e o estado de cada um (`UX-031`).

    **A Modalidade declarada como ampla concorrência não é recorte próprio**, e por isso não entra
    na lista: a quantidade dela mora na linha geral, e dar-lhe linha declararia duas vezes o mesmo
    número. É a mesma regra que o leitor de linha da `014` aplica, vista de fora.

    **O rótulo do recorte sem lista diz o que ele é.** A `021` pagou o preço de não dizer: num
    Edital que declara uma Modalidade chamada "Ampla concorrência", a tela mostrava dois blocos
    homônimos e quem conduz o certame não sabia em qual agir.
    """
    from processo_seletivo.classificacao.domain.universo import por_identidade

    versao = effective_version(edital_id=edital.id, at=at)
    perfil = por_identidade((versao.content or {}).get("profiles"), perfil_id) or {}
    ampla_declarada = perfil.get("generalCompetitionModalityId")
    recortes = [(None, "Ampla concorrência (linha geral do quadro)")]
    for modalidade in perfil.get("competitionModalities") or []:
        if not isinstance(modalidade, dict) or not modalidade.get("id"):
            continue
        identidade = str(modalidade["id"])
        if ampla_declarada and identidade == str(ampla_declarada):
            continue
        nome = modalidade.get("name") or identidade
        recortes.append((identidade, f"{nome} ({modalidade.get('code')})"))
    return [
        {
            "rotulo": rotulo,
            **ocupacao_do_recorte(
                edital=edital,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista,
                at=at,
            ),
        }
        for lista, rotulo in recortes
    ]


def dentro_da_faixa(*, edital, perfil_id, marco_id, lista_id=None):
    """As inscrições que o corte vigente fez progredir — ou o universo do ato, quando não há corte.

    **Marco que não corta continua tendo ocupação apurável**: a `014` fechou que corte de marco
    terminal é legítimo, e há Editais em que o marco não governa Etapa alguma. Nesse caso quem está
    "dentro" é quem o ato de ordenação considerou com posição.
    """
    geracao = geracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    if geracao:
        itens = ItemDoCorte.objects.filter(
            corte__in=geracao, consequencia=ItemDoCorte.Consequencia.PROGREDIU
        )
        return {item.inscricao_id for item in itens}, geracao[-1]
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if ato is None:
        return set(), None
    return {
        posicao.inscricao_id for posicao in ato.posicoes.all() if posicao.posicao is not None
    }, None


def habilitadas_na_etapa(*, edital, etapa_id):
    """As inscrições cujo Resultado vigente da Etapa é `HABILITADA` (`R-001`).

    Vigente é o Resultado que ninguém superou — a mesma leitura que a `018` deixou, e não o mais
    recente por data: superação cria linha nova, e a anterior continua legível.
    """
    if etapa_id is None:
        return set()
    # **`vigentes`, e não `objects`.** O manager é o contrato de leitura de efeito que a `018`
    # deixou, e a varredura `tests/test_vigencia_do_resultado.py` o cobra: eu havia reimplementado
    # o filtro à mão, e ela recusou — com razão. O defeito que ela impede não produz erro: lido por
    # `objects`, um Resultado **superado** por recurso deferido voltaria a contar como ocupação.
    resultados = ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=etapa_id)
    return {
        r.inscricao_id
        for r in resultados
        if r.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    }


def _quantidade(linha):
    """A quantidade da linha publicada, ou `None` quando não há linha.

    `None`, e não zero: sem quadro publicado o Edital não declarou quantidade nenhuma, e zero
    afirmaria que ele declarou nenhuma vaga (`UX-032`).
    """
    if not linha:
        return None
    quantidade = linha.get("immediateVacancies")
    return quantidade if isinstance(quantidade, int) and not isinstance(quantidade, bool) else 0


def _quadro_retificado(apuracao, *, at=None):
    """A linha que a apuração leu mudou de quantidade na versão em vigor agora.

    **Compara por identidade da linha**, e não por quantidade: sem `linha_do_quadro_id` não haveria
    como dizer se **esta** apuração ficou para trás, porque a quantidade sozinha não identifica a
    linha. É a lição que o `Corte` já registra para o alvo derivado.
    """
    if apuracao.linha_do_quadro_id is None:
        return False
    versao = effective_version(edital_id=apuracao.edital_id, at=at)
    linha = linha_do_quadro(
        versao.content, perfil_id=apuracao.perfil_id, lista_id=apuracao.lista_id
    )
    if linha is None:
        return True
    if str(linha.get("id")) != str(apuracao.linha_do_quadro_id):
        return True
    return _quantidade(linha) != apuracao.publicadas


def _movimento_posterior(apuracao):
    """Movimento que alcança o recorte e é mais novo que a apuração vigente.

    A comparação é por **id congelado**, e não por instante: o movimento nasce na mesma transação da
    apuração da origem, e comparar horários faria o próprio movimento da origem parecer posterior a
    ela mesma.
    """
    lidos = {str(i) for i in (apuracao.universo or {}).get("movimentosLidos") or []}
    alcancam = MovimentoDeVaga.objects.filter(
        apuracao__edital=apuracao.edital_id,
        apuracao__perfil_id=apuracao.perfil_id,
        apuracao__marco_id=apuracao.marco_id,
    )
    for movimento in alcancam:
        toca = calculo.mesma_lista(
            movimento.origem_lista_id, apuracao.lista_id
        ) or calculo.mesma_lista(movimento.destino_lista_id, apuracao.lista_id)
        if toca and str(movimento.id) not in lidos:
            return True
    return False


__all__ = [
    "apuracao_vigente",
    "recortes_do_marco",
    "causas_de_obsolescencia",
    "dentro_da_faixa",
    "habilitadas_na_etapa",
    "movimentos_lidos_por",
    "ocupacao_do_recorte",
]
