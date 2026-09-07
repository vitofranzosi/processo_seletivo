"""A leitura dos recursos — e a situação de cada um, que é **derivada** e não coluna.

O `Recurso` não tem estado persistido (D-010). O que aconteceu com uma peça é a existência dos atos
que a alcançaram, e a situação exibida se lê deles:

```text
sem juízo de admissibilidade      →  aguardando admissibilidade
juízo negativo                    →  inadmitido (terminal)
admitido, sem decisão             →  aguardando julgamento
decisão existente                 →  decidido, e a espécie diz o efeito
```

Uma coluna seria estado a manter coerente onde a existência de linha já responde — o mesmo idioma
de `PENDENTE`/`CONSOLIDADO` na 013 e da vigência na 015 e na 017. E o primeiro lugar onde ela
apareceria é justamente aqui, por conveniência de uma tela de listagem.

**A espécie chega ao candidato em texto institucional**, nunca como enum: quem lê "Recurso deferido
— o resultado foi corrigido" entende; quem lê `CORRECAO_FIXADA`, não (FR-048, SC-021).
"""

from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade, Recurso
from processo_seletivo.shared.canonical import canonical_sha256

AGUARDANDO_ADMISSIBILIDADE = "aguardando_admissibilidade"
INADMITIDO = "inadmitido"
AGUARDANDO_JULGAMENTO = "aguardando_julgamento"
DECIDIDO = "decidido"

SITUACOES = {
    AGUARDANDO_ADMISSIBILIDADE: "Aguardando análise de admissibilidade",
    INADMITIDO: "Recurso não admitido",
    AGUARDANDO_JULGAMENTO: "Admitido, aguardando julgamento",
    DECIDIDO: "Julgado",
}

# O que a decisão diz a **quem recorreu**. O enum descreve o efeito para o domínio; estas frases
# descrevem o que aconteceu com a pessoa, que é outra coisa e é a que a tela mostra.
ESPECIES = {
    DecisaoRecurso.Especie.INDEFERIDO: "Recurso indeferido",
    DecisaoRecurso.Especie.CORRECAO_FIXADA: "Recurso deferido — o resultado foi corrigido",
    DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA: ("Recurso deferido — a etapa será reavaliada"),
    DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE: (
        "Recurso deferido — a instituição praticará o ato corretivo"
    ),
}


def recursos_do_titular(inscricao):
    """Os recursos da Inscrição, do mais recente para o mais antigo.

    Duas consultas e não uma por peça: `prefetch_related` traz juízos e decisões em bloco. Uma
    listagem que fizesse uma leitura por recurso pareceria rápida com uma peça e sumiria com dez —
    e é o defeito que a 010 já encontrou na listagem de inscrições.
    """
    peças = (
        Recurso.objects.filter(inscricao=inscricao)
        # `versao` entra no `select_related` porque `_objeto` lê o nome publicado do Marco ou da
        # Etapa: sem ele, nomear o objeto custaria uma leitura da Versão Consolidada por peça.
        .select_related("versao", "publicacao_atacada", "resultado_atacado")
        .prefetch_related("juizos", "decisoes")
        .order_by("-interposto_em")
    )
    return [resumo(peca) for peca in peças]


def resumo(peca):
    """A peça como o titular a lê: protocolo, objeto, situação e, havendo, a decisão."""
    juizo = next(iter(peca.juizos.all()), None)
    decisao = next(iter(peca.decisoes.all()), None)
    return {
        "recurso": peca,
        "protocolo": peca.protocolo,
        "interposto_em": peca.interposto_em,
        "fundamentacao": peca.fundamentacao,
        "objeto": _objeto(peca),
        "situacao": _situacao(juizo, decisao),
        "situacao_rotulo": SITUACOES[_situacao(juizo, decisao)],
        "admissibilidade": (
            {"admitido": juizo.admitido, "motivo": juizo.motivo, "quando": juizo.decidido_em}
            if juizo is not None
            else None
        ),
        "decisao": (
            {
                "especie_rotulo": ESPECIES[decisao.especie],
                "motivacao": decisao.motivacao,
                # **Quem decidiu**, e não só o quê: uma decisão sem autor não é ato administrativo,
                # é um texto que apareceu. Quem julga não é quem avalia — o nome do avaliador
                # continua fora, e é essa a fronteira da FR-093.
                "quem": decisao.decidido_por,
                "quando": decisao.decidido_em,
            }
            if decisao is not None
            else None
        ),
    }


def _situacao(juizo, decisao):
    if juizo is None:
        return AGUARDANDO_ADMISSIBILIDADE
    if not juizo.admitido:
        return INADMITIDO
    return DECIDIDO if decisao is not None else AGUARDANDO_JULGAMENTO


def _objeto(peca):
    """O objeto atacado, **nomeado pelo Marco ou pela Etapa** — e nunca por identificador.

    "O resultado divulgado" não identifica nada para quem tem dois marcos publicados, e "o meu
    resultado de etapa" não identifica nada para quem tem quatro Etapas. O candidato precisa
    reconhecer **o que** contestou, e o nome que ele reconhece é o que o Edital publicou: *"o
    resultado divulgado da Classificação final"*, *"o meu resultado da Prova didática"*.

    Cai no genérico quando o conteúdo não alcança o nome — marco removido por Retificação, por
    exemplo. É pior que o nome e melhor que o identificador, pela mesma razão que a 013 já
    registrou em `_nome_da_etapa`.
    """
    conteudo = peca.versao.content
    if peca.publicacao_atacada_id is not None:
        nome = _nome_do_marco(conteudo, peca.publicacao_atacada.marco_id)
        return f"o resultado divulgado da {nome}" if nome else "o resultado divulgado"
    nome = _nome_da_etapa(conteudo, peca.resultado_atacado.etapa_id)
    return f"o meu resultado da {nome}" if nome else "o meu resultado de etapa"


def _nome_do_marco(conteudo, marco_id):
    alvo = str(marco_id)
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == alvo:
                return marco.get("name") or ""
    return ""


def _nome_da_etapa(conteudo, etapa_id):
    alvo = str(etapa_id)
    for etapa in conteudo.get("stages") or []:
        if str(etapa.get("id")) == alvo:
            return etapa.get("name") or ""
    return ""


# ---------------------------------------------------------------------------
# O canal da instituição
# ---------------------------------------------------------------------------

DENTRO = "dentro"
FORA = "fora"
SEM_JANELA = "sem_janela"

TEMPESTIVIDADES = {
    DENTRO: "Dentro do prazo",
    FORA: "Fora do prazo",
    # Não é omissão a corrigir: é o que o Edital declarou. Enquanto a norma não declara janela, a
    # tempestividade é juízo humano motivado, e a tela precisa dizer isso em vez de fingir um prazo
    # (D-004, FR-034).
    SEM_JANELA: "Sem prazo computável",
}


def assinatura_do_estado_da_peca(peca):
    """O resumo do que a tela leu — juízo e decisão, que é todo o estado que a peça tem.

    Não há coluna de estado a assinar (D-010): o que muda entre abrir a tela e confirmar é a
    **existência** desses dois atos, e é exatamente isso que o resumo cobre. Incluir o instante
    faria a confirmação nunca conferir.
    """
    juizo = next(iter(peca.juizos.all()), None)
    decisao = next(iter(peca.decisoes.all()), None)
    return canonical_sha256(
        {
            "recurso": str(peca.pk),
            "juizo": str(juizo.pk) if juizo is not None else None,
            "decisao": str(decisao.pk) if decisao is not None else None,
        }
    )


def recursos_do_edital(edital, *, situacao=""):
    """Os recursos recebidos, para quem julga — **sem uma consulta de impedimento sequer**.

    A listagem mostra recursos que o ator talvez não possa julgar, e é a tela da peça que nomeia o
    impedimento. Perguntar aqui custaria cinco leituras por linha, que é o custo por linha que a
    012 já recusou uma vez (T-006, FR-031).

    A fundamentação também não vem: ela é conteúdo do juízo, e a lista existe para escolher o que
    abrir.
    """
    peças = (
        Recurso.objects.filter(inscricao__edital=edital)
        .select_related("inscricao", "versao", "resultado_atacado", "publicacao_atacada")
        .prefetch_related("juizos", "decisoes")
        .order_by("interposto_em")
    )
    linhas = [_linha(peca) for peca in peças]
    return [linha for linha in linhas if not situacao or linha["situacao"] == situacao]


def _linha(peca):
    juizo = next(iter(peca.juizos.all()), None)
    decisao = next(iter(peca.decisoes.all()), None)
    return {
        "recurso": peca,
        "protocolo": peca.protocolo,
        "interposto_em": peca.interposto_em,
        "candidato": peca.inscricao.nome,
        "inscricao": peca.inscricao.protocolo,
        "objeto": _objeto(peca),
        "situacao": _situacao(juizo, decisao),
        "situacao_rotulo": SITUACOES[_situacao(juizo, decisao)],
        "tempestividade": _tempestividade(peca),
        "tempestividade_rotulo": TEMPESTIVIDADES[_tempestividade(peca)],
    }


def _tempestividade(peca):
    """Derivada da janela **gravada na peça**, e não recalculada agora (FR-024).

    Recalcular responderia com a norma de hoje sobre um ato de ontem. Enquanto o degrau 8 não
    existe, nenhuma peça tem janela, e a resposta honesta é dizer que não há prazo computável.
    """
    if peca.janela_fecha_em is None:
        return SEM_JANELA
    return DENTRO if peca.interposto_em <= peca.janela_fecha_em else FORA


def proveniencia(peca):
    """A lista inteira da FR-092, **numa jornada só** — sem banco e sem shell (SC-020).

    A pergunta que ela responde é a da auditoria e a do julgador: *como este recurso chegou aqui, e
    o que ele alcançou?* Responder isso hoje exigiria abrir cinco telas e cruzar identificadores à
    mão, e é exatamente o que a FR-092 recusa.

    ```text
    quem interpôs · qual Inscrição · qual objeto · qual era o ato vigente naquele instante
    sob qual versão · quando · se dentro da janela
    quem admitiu e por quê · quem decidiu e por quê
    qual efeito · qual ato superado · qual sucessor nasceu
    ```

    **É a FR-092, e não a FR-093.** Aqui aparecem identificadores técnicos e autoria de ato, porque
    quem lê é a administração; o que chega ao candidato está em `resumo`, e é outra coisa.
    """
    juizo = next(iter(peca.juizos.all()), None)
    decisao = next(iter(peca.decisoes.all()), None)
    superado = peca.resultado_atacado
    return {
        "interposto_por": peca.interposto_por,
        "interposto_em": peca.interposto_em,
        "inscricao": peca.inscricao,
        "objeto": _objeto(peca),
        "objeto_identidade": str(peca.publicacao_atacada_id or peca.resultado_atacado_id or ""),
        "ato_vigente": _ato_vigente(peca),
        "versao": peca.versao,
        "janela_abriu_em": peca.janela_abriu_em,
        "janela_fecha_em": peca.janela_fecha_em,
        "tempestividade_rotulo": TEMPESTIVIDADES[_tempestividade(peca)],
        "admissibilidade": juizo,
        "decisao": decisao,
        "especie_rotulo": ESPECIES[decisao.especie] if decisao is not None else "",
        "resultado_superado": superado,
        "sucessor": _sucessor(superado),
    }


def _ato_vigente(peca):
    """Qual era o ato de ordenação vigente quando a peça nasceu.

    No ramo da publicação ele é o ato que ela divulgou; no ramo do Resultado não há ato de
    ordenação a nomear, e afirmar um seria inventar proveniência.
    """
    if peca.publicacao_atacada_id is None:
        return None
    return peca.publicacao_atacada.ato


def _sucessor(superado):
    if superado is None:
        return None
    return next(iter(superado.sucessor.all()), None)


# ---------------------------------------------------------------------------
# A reavaliação determinada, e a pendência que dela nasce
# ---------------------------------------------------------------------------


def reavaliacoes_pendentes(edital, etapa_id=None):
    """`{(inscricao_id, etapa_id): decisao}` das reavaliações determinadas e **não cumpridas**.

    **A chave é o par, e não a inscrição.** Chaveando por inscrição, uma segunda reavaliação
    determinada para a mesma pessoa em outra Etapa sobrescrevia a primeira — e a pendência
    desaparecida liberava indevidamente a publicação definitiva do marco que a enumerava. É o tipo
    de perda que não produz erro nenhum: o dicionário simplesmente fica menor.

    Pendente é **derivado**, e não coluna (D-010): a decisão determinou reavaliar, e o cumprimento
    é a existência de um sucessor do Resultado protegido. Uma coluna `cumprida` seria estado a
    manter coerente onde a existência de linha já responde — e o primeiro lugar onde ela apareceria
    é justamente aqui, por conveniência de uma tela de organização da Etapa (FR-066).

    Duas consultas, e não uma por inscrição: as decisões da espécie vêm em bloco, e os sucessores
    dos Resultados que elas protegem vêm em outra. Perguntar por linha seria o custo que a 012
    recusou.
    """
    decisoes = (
        DecisaoRecurso.objects.filter(
            especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
            recurso__inscricao__edital=edital,
        )
        .select_related("recurso", "resultado_protegido")
        .order_by("decidido_em")
    )
    if etapa_id is not None:
        decisoes = decisoes.filter(etapa_id=etapa_id)
    decisoes = list(decisoes)
    if not decisoes:
        return {}

    from processo_seletivo.resultados.models import ResultadoEtapa

    cumpridas = set(
        ResultadoEtapa.objects.filter(
            resultado_anterior_id__in=[item.resultado_protegido_id for item in decisoes]
        ).values_list("resultado_anterior_id", flat=True)
    )
    pendentes = {}
    for decisao in decisoes:
        if decisao.resultado_protegido_id not in cumpridas:
            pendentes[(decisao.recurso.inscricao_id, decisao.etapa_id)] = decisao
    return pendentes


def reavaliacao_pendente_do_par(inscricao_id, etapa_id):
    """A decisão que determinou reavaliar este par e ainda não foi cumprida, ou `None`.

    A pergunta pontual que a consolidação faz antes de gravar. Ela existe separada da consulta em
    bloco porque o comando decide sobre **um** par de cada vez, e carregar o Edital inteiro para
    responder sobre uma inscrição seria ler o que não se usa.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    decisao = (
        DecisaoRecurso.objects.filter(
            especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
            recurso__inscricao_id=inscricao_id,
            etapa_id=etapa_id,
        )
        .select_related("resultado_protegido", "recurso")
        .order_by("-decidido_em")
        .first()
    )
    if decisao is None:
        return None
    cumprida = ResultadoEtapa.objects.filter(
        resultado_anterior_id=decisao.resultado_protegido_id
    ).exists()
    return None if cumprida else decisao


# ---------------------------------------------------------------------------
# A pertinência ao marco, e as três pendências que impedem a definitiva
# ---------------------------------------------------------------------------


def _etapas_do_marco(marco):
    return {str(item) for item in (marco or {}).get("stages") or []}


def recursos_pertinentes(*, edital, marco_id, marco, publicacoes_do_marco):
    """Os recursos que dizem respeito a este marco — **dois conjuntos, e não um** (FR-084).

    ```text
    recurso contra a PublicacaoResultado daquele marco
    recurso contra ResultadoEtapa de Etapa que o marco enumera
    ```

    **Sem a segunda metade, o recurso individual seria a porta por onde uma definitiva nasceria com
    um Resultado em disputa dentro dela.** É a metade fácil de esquecer, porque a primeira parece a
    natural: o recurso "do marco". Mas quem contesta a própria nota contesta um número que entra na
    ordem daquele marco, e publicá-la como definitiva enquanto isso é dizer que acabou o que não
    acabou.
    """
    etapas = _etapas_do_marco(marco)
    consulta = Recurso.objects.filter(inscricao__edital=edital).select_related("resultado_atacado")
    pertinentes = []
    identidades = {str(item) for item in publicacoes_do_marco}
    for peca in consulta:
        if peca.publicacao_atacada_id is not None:
            if str(peca.publicacao_atacada_id) in identidades:
                pertinentes.append(peca)
        elif peca.resultado_atacado is not None and str(peca.resultado_atacado.etapa_id) in etapas:
            pertinentes.append(peca)
    return pertinentes


def recursos_pendentes_do_marco(*, edital, marco_id, marco, publicacoes_do_marco):
    """Os pertinentes que **ainda não foram decididos**.

    Pendente é a ausência de decisão, e não a ausência de juízo de admissibilidade: um recurso
    inadmitido está resolvido — a instituição disse que não o conhece, e isso é resposta. O que
    impede a definitiva é a disputa em aberto (FR-082).
    """
    pertinentes = recursos_pertinentes(
        edital=edital,
        marco_id=marco_id,
        marco=marco,
        publicacoes_do_marco=publicacoes_do_marco,
    )
    if not pertinentes:
        return []
    decididos = set(
        DecisaoRecurso.objects.filter(recurso_id__in=[peca.pk for peca in pertinentes]).values_list(
            "recurso_id", flat=True
        )
    )
    inadmitidos = set(
        JuizoDeAdmissibilidade.objects.filter(
            recurso_id__in=[peca.pk for peca in pertinentes], admitido=False
        ).values_list("recurso_id", flat=True)
    )
    return [peca for peca in pertinentes if peca.pk not in decididos and peca.pk not in inadmitidos]


def reavaliacoes_pendentes_do_marco(*, edital, marco):
    """As reavaliações determinadas e não cumpridas que alcançam Etapa deste marco (FR-082)."""
    etapas = _etapas_do_marco(marco)
    if not etapas:
        return {}
    return {
        par: decisao
        for par, decisao in reavaliacoes_pendentes(edital).items()
        if str(decisao.etapa_id) in etapas
    }


def providencias_pendentes_do_marco(*, edital, marco_id, marco, publicacoes_do_marco, ato=None):
    """As providências a jusante que este marco ainda não cumpriu.

    ```text
    cumprida_para(decisao, ato_candidato) =
          o ato_candidato cita a decisão
       OU existe, no MESMO marco, ato citante que já foi publicado
    ```

    **Citar não é cumprir.** Um ato pode citar a decisão e nunca ser publicado — por ficar obsoleto
    antes disso. Enquanto isso não acontecer a providência continua pendente, e **qualquer sucessor
    do marco pode recitá-la**. É essa recitação que impede o único beco possível: um `UNIQUE` sobre
    a decisão tornaria a definitiva do marco impedida para sempre no dia em que o primeiro ato
    citante ficasse obsoleto (FR-112).

    **A apuração é por marco.** Uma decisão cuja providência é normativa alcança todos os marcos que
    a regra retificada governa, e o trabalho feito num deles não libera a definitiva de outro.
    """
    from processo_seletivo.classificacao.models import CitacaoDeDecisao

    pertinentes = [
        peca
        for peca in recursos_pertinentes(
            edital=edital,
            marco_id=marco_id,
            marco=marco,
            publicacoes_do_marco=publicacoes_do_marco,
        )
    ]
    if not pertinentes:
        return []
    decisoes = list(
        DecisaoRecurso.objects.filter(
            recurso_id__in=[peca.pk for peca in pertinentes],
            especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        ).select_related("recurso")
    )
    if not decisoes:
        return []

    citadas_pelo_candidato = (
        set(CitacaoDeDecisao.objects.filter(ato=ato).values_list("decisao_id", flat=True))
        if ato is not None
        else set()
    )
    # A citação **publicada**: o ato citante precisa ter divulgação, e ela precisa ser deste marco.
    cumpridas = set(
        CitacaoDeDecisao.objects.filter(
            decisao_id__in=[item.pk for item in decisoes],
            ato__marco_id=marco_id,
            ato__publicacoes_de_resultado__isnull=False,
        ).values_list("decisao_id", flat=True)
    )
    return [
        decisao
        for decisao in decisoes
        if decisao.pk not in citadas_pelo_candidato and decisao.pk not in cumpridas
    ]


def decisoes_a_citar(*, edital, marco_id, marco, publicacoes_do_marco):
    """O que a tela de emissão oferece: as providências pendentes deste marco (FR-089)."""
    return providencias_pendentes_do_marco(
        edital=edital,
        marco_id=marco_id,
        marco=marco,
        publicacoes_do_marco=publicacoes_do_marco,
    )
