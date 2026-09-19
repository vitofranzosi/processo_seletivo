"""A leitura da ocupação: a apuração vigente, as causas de obsolescência e os três números.

**Vigente é derivada, e obsolescência é calculada.** Nenhuma das duas é coluna, porque mantê-las
exigiria `UPDATE` numa tabela append-only — o provisionamento instala e verifica a proibição. É o
mesmo desenho de `classificacao/application/corte.py`, e as causas vêm **nomeadas**, nunca como
"divergências": a `018` já pagou esse preço.
"""

from processo_seletivo.classificacao.application.corte import geracao_vigente, linha_do_quadro
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.models import ItemDoCorte

# **A primeira dependência de `ocupacao` sobre `editais`**, e ela é deliberada — conferido em
# 18/09/2026: até aqui este módulo importava `classificacao`, `publicacoes` e `resultados`, e nada
# de `editais`. A aresta é legítima na direção em que vai: `editais` é conteúdo normativo, não
# depende de ninguém, e nada depende de `ocupacao`. O que se lê daqui são dois fatos do **marco
# publicado** — se ele declara regra de corte, e se ele emite ordem num dado recorte —, e ambos são
# conteúdo do Edital. Registrada por escrito para que a próxima pessoa saiba que ela foi escolhida,
# e não acidental (032, T034).
from processo_seletivo.editais.domain import marcos
from processo_seletivo.ocupacao.application import efeitos as efeitos_de_ocupacao
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
    """As **cinco** causas, nomeadas (`FR-263`, e a quinta veio com a `019`).

    A quarta — movimento posterior que alcança o recorte — é o que dispensa orquestração: a reversão
    não precisa disparar, em cascata, a emissão do destino. O destino aparece obsoleto, com a causa
    dita, e quem quiser o número novo emite. Reusar a obsolescência que já existe custa uma causa;
    obrigar emissão encadeada custaria uma orquestração entre dois recortes.

    A quinta — efeito posterior — é o mesmo desenho aplicado ao desfecho de convocação: nenhuma
    apuração é reescrita quando alguém desiste ou aceita. A vigente passa a aparecer obsoleta, e o
    número novo sai na **emissão seguinte** (`D-006`). Fosse a `019` a reescrever a apuração, seria
    `UPDATE` em tabela append-only — e a proibição está instalada no banco.
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
    # **A comparação é nos dois sentidos, e o percurso conduzido mostrou por quê.** A versão
    # anterior só olhava o corte quando a apuração citava um: apurado um recorte **antes** de
    # existir corte — o que é legítimo, porque o marco pode ainda não ter cortado — e emitido o
    # corte depois, a apuração continuava aparecendo vigente afirmando `0 ocupada`, quando a faixa
    # recém-criada alcançava 28 pessoas. Corte que **aparece** muda o número tanto quanto corte que
    # é sucedido.
    #
    # O marco que **não corta** continua sem causa: ali não há geração vigente e a apuração não cita
    # corte algum, de modo que os dois lados concordam.
    #
    # A causa é **uma só** para os dois sentidos, e a tela a diz como *"o corte deste recorte não é
    # o que ela leu"* — frase verdadeira tanto quando o corte foi sucedido quanto quando ele nem
    # existia. A primeira redação dizia "não é mais o vigente", que era falsa no segundo caso.
    geracao = geracao_vigente(
        edital=edital,
        perfil_id=apuracao.perfil_id,
        marco_id=apuracao.marco_id,
        lista_id=apuracao.lista_id,
    )
    vigentes = {item.id for item in geracao}
    if apuracao.corte_id is not None and apuracao.corte_id not in vigentes:
        causas.append(
            {
                "causa": nomes.CAUSA_CORTE_OBSOLETO,
                "descricao": "O corte que alimentou esta apuração não é mais o vigente.",
            }
        )
    elif apuracao.corte_id is None and vigentes:
        causas.append(
            {
                "causa": nomes.CAUSA_CORTE_OBSOLETO,
                "descricao": "Esta apuração foi emitida antes de existir corte, e já existe um.",
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
    if _efeito_posterior(apuracao):
        causas.append(
            {
                "causa": nomes.CAUSA_EFEITO_POSTERIOR,
                # **A descrição não nomeia convocação**, e a `UX-034` é quem o exige: esta
                # feature não conhece esse fato. O que ela conhece é o efeito que entrou pela
                # porta — uma inscrição saiu do conjunto de ocupantes, ou entrou nele —, e quem
                # dá sentido ao fundamento é quem o escreveu.
                "descricao": (
                    "Um efeito registrado depois desta apuração mudou o conjunto de ocupantes "
                    "deste recorte."
                ),
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
    marco = marcos.marco_no_conteudo(versao.content, perfil_id=perfil_id, marco_id=marco_id)
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
        # **Dois booleanos aditivos, e nenhum valor novo em `estado`** (032, `data-model.md`). Um
        # recorte reservado em marco computado **é**, de fato, `NOT_APPRAISED`, e continuará
        # sendo; acrescentar um quinto valor obrigaria todo consumidor que hoje distingue os
        # quatro a aprender um quinto. A `016` registra por escrito que colapsar estados é o que a
        # `UX-032` proíbe, e multiplicá-los sem necessidade é o erro simétrico. Campo é aditivo:
        # quem não o lê continua lendo o que lia.
        #
        # `faixaDisponivel` é falso quando o marco não declara regra de corte alguma (`FR-463`):
        # sem corte não há geração, sem geração não há faixa, e não há faixa seguinte a pedir. O
        # marco do acervo carrega `cutRule` nulo, e é exatamente esse o caso que a tela precisa
        # deixar de oferecer.
        "faixaDisponivel": bool(marco and marco.get("cutRule")),
        # **`apuravel` foi removido, e a ausência é a notícia** (034, `FR-501a`). Ele era falso
        # no recorte reservado de marco computado, porque um ato computado emitia uma lista só; a
        # `034` fez a ordem por recorte existir, e o predicado que o derivava passou a responder
        # sempre "sim". Guarda que nunca reprova é pior do que guarda nenhum: o próximo a ler o
        # código confia nele. Quem quiser saber se há o que apurar pergunta pela ordem vigente
        # daquele recorte, que é a regra real — e é o que a apuração já faz ao recusar.
    }


def _movimentos_lidos_por_apuracao(apuracao):
    if apuracao is None:
        return []
    ids = (apuracao.universo or {}).get("movimentosLidos") or []
    if not ids:
        return []
    encontrados = {str(m.id): m for m in MovimentoDeVaga.objects.filter(id__in=ids)}
    return [encontrados[str(i)] for i in ids if str(i) in encontrados]


def historico_do_recorte(*, edital, marco_id, lista_id=None, perfil_id=None):
    """Todas as apurações do recorte, da mais antiga à mais nova, com o que cada uma leu.

    **Lidas como elas foram emitidas**, e não reinterpretadas pela versão vigente: cada apuração
    guarda a versão do quadro, a ordem, o corte e os movimentos que considerou. Uma Retificação
    posterior não reescreve o que uma apuração antiga apurou — o ato é imutável, e a leitura dele
    também precisa ser. É a mesma regra que a `015` aplica ao ato de ordenação.

    **`perfil_id` é opcional de propósito, e é o que faz o histórico sobreviver à Retificação.** As
    apurações guardam o Perfil e o marco como **identidades publicadas**; resolver o Perfil pelo
    snapshot vigente daria 404 no dia em que uma Retificação removesse o marco — e seria justamente
    o histórico antigo, o que mais importa, a desaparecer. A `T058` pedia isso em letras, e a
    primeira versão desta tela o contrariou.
    """
    recorte = {"edital": edital, "marco_id": marco_id, "lista_id": lista_id}
    if perfil_id is not None:
        recorte["perfil_id"] = perfil_id
    apuracoes = list(ApuracaoDeOcupacao.objects.filter(**recorte).order_by("emitida_em"))
    if not apuracoes:
        return []
    vigente = apuracoes[-1] if not apuracoes[-1].sucessoras.exists() else None
    causas = {}
    if vigente is not None:
        causas[vigente.id] = causas_de_obsolescencia(vigente)
    return [
        {
            "apuracao": item,
            "publicadas": item.publicadas,
            "efetivas": item.efetivas,
            "ocupadas": item.ocupadas,
            "faltando": item.faltando,
            "movimentos": _movimentos_lidos_por_apuracao(item),
            "vigente": item is vigente,
            "causasDeObsolescencia": [c["causa"] for c in causas.get(item.id, [])],
        }
        for item in apuracoes
    ]


def recortes_do_marco(*, edital, perfil_id, marco_id, at=None):
    """Todo recorte do marco, com os quatro números e o estado de cada um (`UX-031`).

    **A derivação deixou de morar aqui** (034, `FR-491`). A regra é a mesma — a Modalidade
    declarada como ampla não é recorte próprio, porque a quantidade dela mora na linha geral, e
    dar-lhe linha declararia duas vezes o mesmo número —, e o que mudou é que ela passou a ser
    respondida por `editais/domain/recortes.py`, que a classificação também consome. Duas listas
    iguais hoje e derivadas em dois lugares divergem na primeira Retificação, e a `SC-172` compara
    as duas justamente por isso.

    **Os rótulos são os mesmos**, e continuam sendo os da derivação: o do recorte sem lista diz que
    ele é a linha geral. A `021` pagou o preço de não dizer — num Edital que declara uma Modalidade
    chamada "Ampla concorrência", a tela mostrava dois blocos homônimos e quem conduz o certame não
    sabia em qual agir.
    """
    from processo_seletivo.editais.domain.recortes import recortes_do_perfil

    versao = effective_version(edital_id=edital.id, at=at)
    recortes = recortes_do_perfil(versao.content, perfil_id=perfil_id)
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


def progrediram_em_ordem(*, edital, perfil_id, marco_id, lista_id=None):
    """`(sequência ordenada, corte, empates residuais)` do recorte (019, `R-001`, `R-002`).

    **Sequência, e não conjunto, porque titular inicial depende de ordem.** É a correção que a
    `019` trouxe: o cálculo anterior contava capacidade — enquanto sobrassem habilitados na faixa,
    o número saturava no alvo — e 27 suplentes eram promovidas em silêncio antes de ele se mover.

    **A ordem vem de `PosicaoNaOrdem`, e não de `ItemDoCorte`.** Os dois guardam posição, mas é a
    posição na ordem que carrega `empate_residual`, e sem ela não há como saber se um empate não
    julgado atravessa a fronteira do alvo (`R-002`). Ler os dois lugares para o mesmo fato é como
    um deles fica para trás.

    **Marco que não corta continua tendo ocupação apurável**: a `014` fechou que corte de marco
    terminal é legítimo, e há Editais em que o marco não governa Etapa alguma. Nesse caso quem está
    "dentro" é quem o ato de ordenação considerou com posição.
    """
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    geracao = geracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    corte = geracao[-1] if geracao else None
    if ato is None:
        return [], corte, {}
    posicoes = [p for p in ato.posicoes.all() if p.posicao is not None]
    posicoes.sort(key=lambda p: p.posicao)
    if geracao:
        itens = ItemDoCorte.objects.filter(
            corte__in=geracao, consequencia=ItemDoCorte.Consequencia.PROGREDIU
        )
        progrediram = {item.inscricao_id for item in itens}
        # **O corte pode alcançar quem o ato vigente não posiciona**, e o contrário também: são
        # atos distintos, e o corte é lido pela faixa que ele emitiu. Quem progrediu sem posição
        # legível entra ao fim, preservando o conjunto que a contagem anterior usava — perder
        # alguém aqui reduziria a ocupação em silêncio, que é o modo de falha mais caro da `016`.
        ordenadas = [p.inscricao_id for p in posicoes if p.inscricao_id in progrediram]
        vistas = set(ordenadas)
        ordenadas += sorted((i for i in progrediram if i not in vistas), key=str)
    else:
        ordenadas = [p.inscricao_id for p in posicoes]
    empates = {p.inscricao_id: p.posicao for p in posicoes if p.empate_residual}
    return ordenadas, corte, empates


def dentro_da_faixa(*, edital, perfil_id, marco_id, lista_id=None):
    """O **conjunto** de quem progrediu, para quem não precisa da ordem.

    Sobrevive à `019` porque a concorrência concomitante é pergunta de pertinência, e não de
    posição: quem ocupou pela ampla ocupou, e em que lugar da fila não muda nada.
    """
    ordenadas, corte, _ = progrediram_em_ordem(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    return set(ordenadas), corte


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


def _movimentos_que_alcancam(*, edital, perfil, marco, lista):
    """Os movimentos que alcançam o recorte, cedendo ou recebendo.

    **A busca é pelo recorte, e não pela apuração**: o movimento nasce com a apuração da origem, e
    é a do destino que o lê — procurá-lo por `apuracao` devolveria só o que a própria origem gravou.
    """
    candidatos = MovimentoDeVaga.objects.filter(
        apuracao__edital=edital, apuracao__perfil_id=perfil, apuracao__marco_id=marco
    ).order_by("registrado_em")
    return [
        m
        for m in candidatos
        if calculo.mesma_lista(m.origem_lista_id, lista)
        or calculo.mesma_lista(m.destino_lista_id, lista)
    ]


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


def ocupantes_da_ampla(*, edital, perfil_id, marco_id, versao):
    """Quem **ocupa vaga** pela ampla concorrência: os titulares dela, e não a faixa inteira.

    É a mesma conta que a apuração da ampla faz, lida de fora — e é ela que a reservada subtrai.

    **Titulares, e não "dentro da faixa"** (019, `R-001`). A versão anterior devolvia a faixa da
    ampla inteira interseccionada com as habilitadas, e isso incluía os **suplentes** dela — gente
    que está na faixa, habilitou, e não ocupa vaga nenhuma até que uma vague. Subtraí-los do recorte
    reservado tirava da reserva quem não estava ocupando nada em lugar algum: num Perfil com 40
    vagas na ampla, faixa de 70 e 2 vagas na PPI, as duas melhores candidatas PPI classificadas
    entre a 41ª e a 70ª posição da ampla eram excluídas da própria reserva, e a PPI apurava
    `ocupadas: 0` com as duas vagas preenchidas.

    O erro não aparecia antes porque o cálculo antigo saturava: `min(cabem, efetivas)` devolvia o
    alvo enquanto sobrasse gente na faixa, e escondia a subtração indevida. Com a contagem de
    titulares da `019` ele passou a sair no número.

    **O item 8.9 do 28/2026 fala de quem foi *"sorteado dentro do número de vagas oferecido para
    ampla concorrência"*** — que é o titular, e não quem apenas alcançou a faixa dela.
    """
    progrediram, corte, empates = progrediram_em_ordem(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None
    )
    etapa = corte.etapa_governada_id if corte is not None else None
    habilitadas = habilitadas_na_etapa(edital=edital, etapa_id=etapa)
    linha = linha_do_quadro(versao.content, perfil_id=perfil_id, lista_id=None)
    if linha is None:
        # Sem linha geral publicada não há quantidade de ampla, e portanto ninguém a ocupa. É a
        # mesma leitura que a `UX-032` fixa: ausência de quadro não é zero vaga, é nenhuma
        # afirmação — e aqui a afirmação que não se faz é "estas pessoas ocupam vagas de ampla".
        return set()
    movimentos = _movimentos_que_alcancam(
        edital=edital, perfil=perfil_id, marco=marco_id, lista=None
    )
    lidos = [
        (m.especie, calculo.mesma_lista(m.destino_lista_id, None), m.quantidade) for m in movimentos
    ]
    recebidas = sum(q for _, recebida, q in lidos if recebida)
    cedidas = sum(q for _, recebida, q in lidos if not recebida)
    efetivas = (_quantidade(linha) or 0) + recebidas - cedidas
    efeitos = efeitos_de_ocupacao.efeitos_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None
    )
    # **Os efeitos da ampla entram**: quem desistiu de uma vaga de ampla deixou de ocupá-la, e
    # continuar subtraindo essa pessoa da reserva a manteria fora das duas listas ao mesmo tempo.
    return calculo.ocupantes(
        titulares=calculo.titulares_iniciais(
            progrediram_em_ordem=progrediram,
            habilitadas=habilitadas,
            efetivas=efetivas,
            empates_residuais=empates,
        ),
        efeitos_lidos=efeitos_de_ocupacao.efeitos_lidos_por(efeitos),
    )


def _efeito_posterior(apuracao):
    """Efeito de ocupação que alcança o recorte e não estava entre os que a apuração leu.

    **A comparação é por id congelado, e não por instante** — a mesma disciplina de
    `_movimento_posterior`, e pela mesma razão: um efeito gravado na mesma transação da apuração
    pareceria posterior a ela mesma se o critério fosse o relógio.

    Apuração emitida antes desta feature não tem `efeitosLidos` no universo, e qualquer efeito do
    recorte a torna obsoleta. Está certo: aquele efeito é mesmo posterior a ela.

    **A pergunta é respondida no banco, e não em Python.** A versão anterior trazia todas as linhas
    de efeito do recorte para descartar tudo menos um booleano — e esta função corre uma vez por
    lista de concorrência em `recortes_do_marco`, na tela que tem teto de 3 s com 1.000
    participantes (`SC-090`). Num certame longo o recorte acumula um efeito por desfecho, e o custo
    de abrir a tela cresceria com o número de desistências.
    """
    from processo_seletivo.ocupacao.models import EfeitoDeOcupacao

    lidos = [str(i) for i in (apuracao.universo or {}).get("efeitosLidos") or []]
    return (
        EfeitoDeOcupacao.objects.filter(
            edital=apuracao.edital_id,
            perfil_id=apuracao.perfil_id,
            marco_id=apuracao.marco_id,
            lista_id=apuracao.lista_id,
        )
        .exclude(id__in=lidos)
        .exists()
    )


__all__ = [
    "apuracao_vigente",
    "recortes_do_marco",
    "causas_de_obsolescencia",
    "dentro_da_faixa",
    "progrediram_em_ordem",
    "habilitadas_na_etapa",
    "historico_do_recorte",
    "movimentos_lidos_por",
    "ocupacao_do_recorte",
    "ocupantes_da_ampla",
]
