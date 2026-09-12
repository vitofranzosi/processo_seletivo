"""A prévia **da relação**, e nunca da ordem (021, FR-030, D-010).

**O que esta leitura deliberadamente não faz.** Ela não calcula chave, não ordena e não devolve
posição nenhuma. Uma prévia da ordem depois de conhecida a semente seria o ensaio que a feature
existe para impedir; antes da semente ela nem existiria. O que a tela precisa mostrar é o
**universo** — quem entra, com que número — e o estado do compromisso de cada recorte.
"""

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.habilitacao import habilitadas_na_etapa
from processo_seletivo.sorteios.application.selectors import relacao_vigente
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import projecao, substituicao


def recortes_do_marco(*, edital, perfil_id, marco_id, at=None):
    """O marco, o método publicado e o estado de cada recorte — ampla concorrência e reservas."""
    versao = effective_version(edital_id=edital.id, at=at)
    perfil, marco = _perfil_e_marco(versao.content, perfil_id, marco_id)
    metodo = dominio_do_metodo.metodo_declarado(
        versao.content, perfil_id=perfil_id, marco_id=marco_id
    )
    submetidas = list(
        Inscricao.objects.filter(
            edital=edital, profile_id=perfil_id, status=Inscricao.Status.SUBMETIDA
        )
    )
    # **A mesma regra de quem entra que a publicação aplica** (FR-002, R-012). A prévia projetava
    # sem o filtro da Etapa de habilitação: onde o Edital declara uma, a comissão via um número e
    # congelava outro, sem que nada explicasse a diferença.
    habilitadas = habilitadas_na_etapa(edital, metodo)
    ocorrencia_da_vez, proxima_referencia, descartadas = _ocorrencia_declarada(metodo)
    # **Os recortes precisam ser distinguíveis na tela** (021, D-006). O primeiro é o recorte sem
    # lista — todos os inscritos do Perfil —, e os demais são as modalidades declaradas. Quando o
    # Edital declara uma modalidade chamada "Ampla concorrência", que é o caso normal, os dois
    # nomes colidiam: a tela mostrava dois blocos homônimos, um com o sorteio feito e outro vazio,
    # e quem conduz o certame não tinha como saber em qual publicar.
    #
    # O rótulo do recorte sem lista passa a dizer o que ele é — o universo inteiro do Perfil —, e
    # cada modalidade carrega o código que o Edital publica.
    listas = [(None, "Todos os inscritos do recorte de vaga (sem lista de concorrência)")] + [
        (
            str(modalidade.get("id")),
            f"{modalidade.get('name') or ''} ({modalidade.get('code')})"
            if modalidade.get("code")
            else (modalidade.get("name") or ""),
        )
        for modalidade in perfil.get("competitionModalities") or []
    ]
    return {
        "perfil": perfil,
        "marco": marco,
        "metodo": metodo,
        # O instante publicado da ocorrência: separa "ainda não" de "não haverá", e a tela precisa
        # dele para não oferecer o descarte antes da hora (FR-077).
        "ocorre_em": _instante_declarado(metodo),
        # A ocorrência da vez — a declarada, ou a que a regra de substituição pôs no lugar dela —,
        # a referência que ainda falta observar, e as que a indisponibilidade descartou. A tela as
        # exibe para que a semente esteja **à vista antes do ato**, e para que o descarte fique
        # visível: é o controle da R-006.
        "ocorrencia": ocorrencia_da_vez,
        "proxima_referencia": proxima_referencia,
        "ocorrencias_descartadas": descartadas,
        "metodo_hash": dominio_do_metodo.resumo_do_metodo(metodo) if metodo else "",
        "recortes": [
            _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas, habilitadas)
            for lista_id, nome in listas
        ],
    }


def _instante_declarado(metodo):
    """O instante publicado em que a ocorrência acontece, ou `None` se o método não o declara."""
    from django.utils.dateparse import parse_datetime

    return parse_datetime(str((metodo or {}).get("occurrenceAt") or "")) or None


def _ocorrencia_declarada(metodo):
    """A ocorrência que a regra publicada manda usar **agora**, se já foi observada.

    **Não é mais "a declarada", e a diferença é a regra de substituição funcionando** (FR-015). A
    tela lia sempre a referência declarada no Edital: registrada uma indisponibilidade, ela
    continuava mostrando aquela linha, o botão de observar sumia — porque a ocorrência "existia" —
    e o sorteio ficava travado para sempre. Agora ela pergunta à regra qual é a vez, e a resposta é
    derivada, não escolhida.
    """
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    if not metodo:
        return None, "", []
    fonte = metodo.get("source", "")
    registradas = list(OcorrenciaDaFonte.objects.filter(fonte=fonte))
    indisponiveis = {o.referencia for o in registradas if o.indisponivel}
    try:
        proxima = substituicao.proxima_a_observar(metodo, indisponiveis)
    except DomainError as esgotada:
        return (
            None,
            "",
            [
                {"referencia": o.referencia, "evidencia": o.evidencia, "motivo": esgotada.detail}
                for o in registradas
                if o.indisponivel
            ],
        )
    atual = next((o for o in registradas if o.referencia == proxima), None)
    descartadas = [
        {"referencia": o.referencia, "evidencia": o.evidencia}
        for o in registradas
        if o.indisponivel and o.referencia != proxima
    ]
    return atual, proxima, descartadas


def _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas, habilitadas):
    vigente = relacao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    projetados = projecao.numerar(
        projecao.elegiveis(submetidas, lista_id=lista_id, habilitadas=habilitadas)
    )
    # **O sorteio é do recorte, e não da relação vigente.** Lê-lo de `vigente.sorteios` funcionava
    # até alguém publicar a relação nova: dali em diante a vigente é a sucessora, que ainda não tem
    # sorteio — e a tela deixava de reconhecer o ato a anular exatamente no passo em que ele
    # precisava ser reconhecido.
    sorteio = _sorteio_vigente(edital, perfil_id, marco_id, lista_id)
    return {
        "lista_id": lista_id or "",
        "nome": nome,
        # **Os insumos da sucessão, oferecidos e não digitados** (Princípio VI). A tela pedia que
        # alguém colasse dois UUIDs; depois da Retificação não havia caminho visível para criá-los
        # e escolhê-los, e a anulação — corrigida no domínio — ficava inalcançável pelo canal do
        # ator. Aqui vão as relações que sucedem a do sorteio a anular e as ocorrências observadas
        # que ainda não foram consumidas.
        "relacoes_sucessoras": _relacoes_sucessoras(vigente, sorteio),
        "ocorrencias_disponiveis": _ocorrencias_disponiveis(sorteio),
        # Quantos entrariam **agora**, se a relação fosse publicada neste instante. Depois do
        # congelamento é a relação que manda, e a divergência entre os dois números é informação:
        # ela diz que um fato de origem mudou desde o compromisso.
        "projetados": len(projetados),
        # **Congelada a relação, a tabela é a da relação — e não a projeção de agora.** Esta é a
        # tela que vai ao ar: mostrar a projeção do instante fazia a audiência ver uma lista que
        # **não** era o universo comprometido, e a divergência, quando existia, aparecia só como
        # uma diferença de contagem num aviso ao lado. O que se transmite passa a ser exatamente o
        # que o portal publica e o que o resumo cobre (021, FR-006).
        "participantes": _congelados(vigente) if vigente is not None else _projetados(projetados),
        "relacao": vigente,
        "congelada": vigente is not None,
        "sorteio": sorteio,
    }


def _projetados(numerados):
    """Quem entraria se a relação fosse publicada agora — o universo ainda não comprometido."""
    return [
        {"numero": numero, "nome": inscricao.nome or "", "protocolo": inscricao.protocolo or ""}
        for numero, inscricao in numerados
    ]


def _congelados(relacao):
    """Os participantes **da relação publicada**, na numeração que ela gravou.

    Os mesmos três dados que o portal mostra e que o resumo cobre — número, nome e protocolo —, e
    lidos da relação, que é imutável. É esta lista que a transmissão exibe.
    """
    return [
        {
            "numero": participante.numero_publico,
            "nome": participante.inscricao.nome or "",
            "protocolo": participante.inscricao.protocolo or "",
        }
        for participante in relacao.participantes.select_related("inscricao").order_by(
            "numero_publico"
        )
    ]


def _sorteio_vigente(edital, perfil_id, marco_id, lista_id):
    """O sorteio sem sucessor daquele recorte, ou `None`."""
    from processo_seletivo.sorteios.models import Sorteio

    return (
        Sorteio.objects.filter(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            sucessores__isnull=True,
        )
        .select_related("relacao", "ocorrencia")
        .order_by("-executado_em")
        .first()
    )


def _relacoes_sucessoras(vigente, sorteio):
    """As relações que sucedem a do sorteio a anular — os únicos universos que o sucessor admite.

    Vazia enquanto ninguém publicou a relação nova, e é isso que a tela usa para dizer, em ordem, o
    que ainda falta fazer (FR-054).
    """
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados

    if sorteio is None:
        return []
    return list(
        RelacaoDeHabilitados.objects.filter(relacao_anterior_id=sorteio.relacao_id).order_by(
            "publicada_em"
        )
    )


def _ocorrencias_disponiveis(sorteio):
    """As ocorrências observadas que nenhum sorteio consumiu, e que não são a do ato a anular."""
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    if sorteio is None:
        return []
    return list(
        OcorrenciaDaFonte.objects.filter(indisponivel=False, sorteios__isnull=True)
        .exclude(pk=sorteio.ocorrencia_id)
        .order_by("observada_em")
    )


def _perfil_e_marco(conteudo, perfil_id, marco_id):
    for perfil in conteudo.get("profiles") or []:
        if str(perfil.get("id")) != str(perfil_id):
            continue
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(marco_id):
                return perfil, marco
    raise DomainError("not_found", "Recurso não encontrado.", 404)


__all__ = ["recortes_do_marco"]
