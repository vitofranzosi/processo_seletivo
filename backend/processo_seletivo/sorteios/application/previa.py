"""A prévia **da relação**, e nunca da ordem (021, FR-030, D-010).

**O que esta leitura deliberadamente não faz.** Ela não calcula chave, não ordena e não devolve
posição nenhuma. Uma prévia da ordem depois de conhecida a semente seria o ensaio que a feature
existe para impedir; antes da semente ela nem existiria. O que a tela precisa mostrar é o
**universo** — quem entra, com que número — e o estado do compromisso de cada recorte.
"""

from django.utils import timezone

from processo_seletivo.avaliacoes.domain.conjunto import (
    CONGELAR_A_RELACAO,
    recusa_por_inscricoes_em_curso,
)
from processo_seletivo.editais.domain.recortes import recortes_do_perfil
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.habilitacao import (
    habilitadas_na_etapa,
    para_o_recorte,
)
from processo_seletivo.sorteios.application.selectors import relacao_vigente
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import projecao, substituicao, viabilidade


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
    ocorrencia_da_vez, proxima_referencia, descartadas, recusa = _ocorrencia_declarada(metodo)
    # **Os recortes precisam ser distinguíveis na tela** (021, D-006). O primeiro é o recorte sem
    # lista — todos os inscritos do Perfil —, e os demais são as modalidades declaradas, com o
    # código que o Edital publica.
    #
    # **E são os da derivação única** (122, FR-3893). A lista daqui dava recorte próprio à
    # Modalidade que o Perfil aponta como a ampla, e dela nascia uma relação, um sorteio e um ato
    # que a ocupação não consome — o quarto "divulgar o resultado" da página do Edital. O que o
    # sorteio já produziu nesse recorte não some: vai para `registros_excedentes`, que a tela
    # mostra à parte, só para consulta (FR-3903).
    agora = at or timezone.now()
    listas = [(None, "Todos os inscritos do recorte de vaga (sem lista de concorrência)")] + [
        (lista, _rotulo_da_modalidade(perfil, lista))
        for lista, _ in recortes_do_perfil(versao.content, perfil_id=perfil_id)
        if lista is not None
    ]
    recortes = [
        _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas, habilitadas, metodo)
        for lista_id, nome in listas
    ]
    congelar_agora_inviavel = _congelar_agora_inviavel(
        versao.content, metodo, proxima_referencia, agora
    )
    for recorte in recortes:
        diagnostico = recorte["diagnostico_da_relacao"]
        if diagnostico is None:
            continue
        # **A data concreta da saída**, supondo a relação nova congelada hoje: é o dia que quem
        # retifica precisa escolher, e fazer a conta ao vivo era o que a primeira versão pedia.
        diagnostico["primeiro_dia"] = viabilidade.primeiro_dia_possivel(agora)
        # **E se a extração já retificada também for cedo demais**, o operador precisa saber antes
        # de suceder: a relação nova seria condenada do mesmo jeito.
        diagnostico["nova_cedo_demais"] = (
            congelar_agora_inviavel if diagnostico["metodo_retificado"] else None
        )
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
        # **Por que não há ocorrência da vez**, quando não há — e são duas razões, não uma (035,
        # FR-516). `None` quando há. A tela precisa da distinção porque as duas pedem coisas
        # opostas de quem lê: uma manda esperar pela fonte, a outra manda corrigir a declaração.
        "recusa_da_ocorrencia": recusa,
        "metodo_hash": dominio_do_metodo.resumo_do_metodo(metodo) if metodo else "",
        # **O impedimento anunciado antes de alguém bater nele**, como a distribuição faz: a
        # publicação da relação é recusada com o período correndo, e a tela oferecia o botão sem
        # dizer nada. É a mesma recusa, da mesma versão e da mesma função — `None` quando não há.
        "inscricoes_em_curso": recusa_por_inscricoes_em_curso(
            versao.content, agora, consequencia=CONGELAR_A_RELACAO
        ),
        "recortes": recortes,
        # **O acervo do recorte excedente, para consulta** (122, FR-3902, FR-3903): o que o sorteio
        # produziu quando dava lista própria à Modalidade apontada, ou o que uma Retificação tirou
        # da operação. Nenhum gesto o alcança.
        "registros_excedentes": registros_excedentes(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, at=at
        ),
        "modalidade_apontada": _nome_da_apontada(perfil),
        # **O congelamento que condena o sorteio, dito antes do ato** (102, FR-2659). Congelar é
        # append-only, e quem congelava no dia da extração só descobria na recusa do sorteio, sem
        # caminho de volta. O botão continua (D-005): a relação pode ter data no cronograma.
        #
        # **A sucessão também congela.** O aviso valia só para recorte por congelar, e a relação
        # congelada que sorteia normalmente era sucedida, hoje, sem nada dizer que a nova nasceria
        # condenada. Fica de fora só o recorte cujo diagnóstico já diz a saída inteira.
        "congelar_agora_inviavel": (
            {
                **congelar_agora_inviavel,
                "inclui_sucessao": any(
                    recorte["congelada"] and recorte["diagnostico_da_relacao"] is None
                    for recorte in recortes
                ),
                # **Há relação a congelar pela primeira vez** (126, FR-4031). Sem ela, o aviso vale
                # só para a sucessão, e a tela o mostra dentro do bloco dela — e não como primeira
                # frase dos recortes, onde lia como a próxima ação. A lista sem inscrito não conta:
                # não há o que congelar nela (FR-4033).
                "inclui_congelamento": any(
                    not recorte["congelada"]
                    and recorte["projetados"]
                    and recorte["diagnostico_da_relacao"] is None
                    for recorte in recortes
                ),
            }
            if congelar_agora_inviavel
            and any(recorte["diagnostico_da_relacao"] is None for recorte in recortes)
            else None
        ),
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

    **E quando não há resposta, a razão é dita** (035, FR-516). Duas causas distintas caíam no mesmo
    `except`, e a tela dizia a mesma frase para as duas — *"a ocorrência declarada e todas as
    substitutas estão indisponíveis"*. Ela é verdadeira quando a cadeia esgotou, e **falsa** quando
    a regra não soube derivar: ali a fonte nunca esteve indisponível, e a pessoa é mandada esperar
    por algo que não vai acontecer, para depois Retificar sem saber o quê.

    **A frase certa já existia**, específica e correta — é o `detail` da recusa que a própria regra
    de substituição levanta —, e era descartada a uma linha de onde seria exibida. O trabalho aqui
    não foi escrevê-la: foi parar de jogá-la fora.
    """
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    if not metodo:
        return None, "", [], None
    fonte = metodo.get("source", "")
    registradas = list(OcorrenciaDaFonte.objects.filter(fonte=fonte))
    indisponiveis = {o.referencia for o in registradas if o.indisponivel}
    try:
        proxima = substituicao.proxima_a_observar(metodo, indisponiveis)
    except DomainError as recusa:
        return (
            None,
            "",
            [
                {"referencia": o.referencia, "evidencia": o.evidencia, "motivo": recusa.detail}
                for o in registradas
                if o.indisponivel
            ],
            _causa_da_recusa(recusa, metodo),
        )
    atual = next((o for o in registradas if o.referencia == proxima), None)
    descartadas = [
        {"referencia": o.referencia, "evidencia": o.evidencia}
        for o in registradas
        if o.indisponivel and o.referencia != proxima
    ]
    return atual, proxima, descartadas, None


def _causa_da_recusa(recusa, metodo):
    """Qual das duas, e o que a tela precisa dizer sobre cada uma (035, FR-516 a FR-518).

    A distinção sai do **código** da recusa, e não da frase: a frase é para quem lê, e duas frases
    comparadas por substring seriam a terceira cópia da mesma regra.

    **Os dois nomes do campo vêm de `CAMPOS_DO_METODO`**, que é a mesma tabela de onde o documento
    publicado tira os dele desde a `032` — e ela guarda os dois de propósito: o rótulo curto, que
    encabeça o par rótulo-valor, e a frase, que completa uma recusa. A tela precisa dos dois: o
    curto é como o campo se chama, e a frase é o que ele é. Escrevê-los aqui daria ao Edital um
    nome na tela do sorteio e outro no documento, que é o que o Princípio I proíbe.

    **E a direção da dependência não se inverte** (FR-521): esta leitura importa do domínio dos
    Editais, e não da interface — o rótulo que a tela de Retificação exibe é outro registro do mesmo
    conceito, e lê-lo daqui seria `sorteios/application` dependendo de `interface`.
    """
    from processo_seletivo.editais.domain.perfis import CAMPOS_DO_METODO

    if recusa.code != substituicao.RECUSA_POR_FORMA_DA_REFERENCIA:
        # A cadeia esgotou: a fonte esteve indisponível tantas vezes quanto a regra encadeia. Para
        # **esta** causa a frase de hoje está certa, e a `FR-518` manda não mexer no que está certo.
        return {"causa": "cadeia", "detalhe": recusa.detail}
    campo, o_que_e, rotulo = next(
        (linha for linha in CAMPOS_DO_METODO if linha[0] == "occurrence"),
        ("occurrence", "a ocorrência concreta que fixará a semente", "Ocorrência"),
    )
    return {
        "causa": "declaracao",
        "campo": rotulo,
        "o_que_e": o_que_e,
        "referencia": str((metodo or {}).get("occurrence") or ""),
        "detalhe": recusa.detail,
    }


def _congelar_agora_inviavel(conteudo, metodo, proxima_referencia, agora):
    """Fonte e dia da extração quando congelar a partir de agora a condena — ou `None` (102).

    **O congelamento mais cedo não é agora quando as inscrições correm** (FR-2651): o congelamento é
    recusado até o fim delas, e comparar só com agora deixava sem aviso justamente o Edital que uma
    Retificação de prorrogação levou ao dia da extração.

    **Só a ocorrência declarada** (FR-2659). A substituta não tem instante publicado, e prever o dia
    dela seria inventar o que o Edital não diz.
    """
    from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
    from processo_seletivo.sorteios.infrastructure.fontes import publica_so_a_data

    if not metodo or proxima_referencia != str(metodo.get("occurrence") or ""):
        return None
    fonte = metodo.get("source")
    limite = viabilidade.limite_previsto(
        metodo.get("occurrenceAt"), so_a_data=publica_so_a_data(fonte)
    )
    periodo = periodo_de_inscricoes(conteudo, agora)
    fim = None if periodo.cancelado else periodo.fim
    mais_cedo = viabilidade.congelamento_mais_cedo(agora=agora, fim_das_inscricoes=fim)
    if not viabilidade.inviavel(limite, mais_cedo):
        return None
    return {
        "fonte": fonte,
        "referencia": proxima_referencia,
        "dia": limite,
        "inscricoes_correndo": mais_cedo > agora,
        "primeiro_dia": viabilidade.primeiro_dia_possivel(mais_cedo),
    }


def _diagnostico_da_relacao(vigente, sorteio, metodo_vigente):
    """Por que esta relação congelada nunca sorteará com a extração dela — ou `None` (102).

    **O método é o da versão que a relação cita, e não o vigente** (FR-2660, FR-2661, R-006). É o
    que o sorteio lê: a relação comprometeu um método ao congelar, e uma Retificação posterior não
    o muda. Ler o vigente aqui repetiria, na explicação, o engano que a tela já comete com a
    ocorrência da vez — e diria "viável" a uma relação que a constituição vai recusar.
    """
    from processo_seletivo.sorteios.infrastructure.fontes import publica_so_a_data
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    if vigente is None or (sorteio is not None and sorteio.relacao_id == vigente.id):
        return None
    comprometido = dominio_do_metodo.metodo_declarado(
        vigente.versao.content, perfil_id=vigente.perfil_id, marco_id=vigente.marco_id
    )
    if not comprometido:
        return None
    fonte = comprometido.get("source")
    declarada = str(comprometido.get("occurrence") or "")
    if OcorrenciaDaFonte.objects.filter(
        fonte=fonte, referencia=declarada, indisponivel=True
    ).exists():
        # A substituta não tem instante publicado (FR-2660): a recusa, se vier, é a de sempre.
        return None
    limite = viabilidade.limite_previsto(
        comprometido.get("occurrenceAt"), so_a_data=publica_so_a_data(fonte)
    )
    if not viabilidade.inviavel(limite, vigente.publicada_em):
        return None
    return {
        "fonte": fonte,
        "referencia": declarada,
        "dia": limite,
        "congelada_em": vigente.publicada_em,
        "metodo_retificado": bool(metodo_vigente)
        and dominio_do_metodo.resumo_do_metodo(metodo_vigente) != vigente.metodo_hash,
    }


def _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas, habilitadas, metodo=None):
    vigente = relacao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    projetados = projecao.numerar(
        projecao.elegiveis(
            submetidas,
            lista_id=lista_id,
            habilitadas=para_o_recorte(edital, metodo, habilitadas, lista_id),
        )
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
        "diagnostico_da_relacao": _diagnostico_da_relacao(vigente, sorteio, metodo),
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


__all__ = ["recortes_do_marco", "recortes_sem_inscrito"]


def recortes_sem_inscrito(*, edital, conteudo, perfil_id, marco_id, agora=None):
    """Os recortes do marco de sorteio em que **não haverá** relação — não só os que não a têm.

    **Ausência de ato não é pendência** (126, FR-4019, D-002). A condução contava como *Falta* a
    lista que nenhuma inscrição declarou, e oferecia cortá-la e apurá-la: no Polo Vitória do
    Edital 35, doze células em falta e dois gestos que só podiam ser recusados.

    **Mora aqui, ao lado de `recortes_do_marco`, porque é a mesma pergunta que ela responde** em
    `projetados` e `congelada`, e que `publicar_relacao` faz ao recusar com
    `relation_would_be_empty`. Três redações da mesma regra divergiriam na primeira mudança da
    projeção. As diferenças são de propósito, e só estreitam — tudo o que sai daqui teria o
    congelamento recusado:

    - **inscrições que não chegam mais**: o período encerrado, ou não designado — o Edital que não
      recebe inscrição por este sistema (`periodo_de_inscricoes`); aberto ou por abrir, alguém ainda
      pode declarar a lista;
    - **sem o filtro da Etapa de habilitação**: com ela, a projeção é zero enquanto a Etapa não é
      consolidada, e zero por espera não é "ninguém se inscreveu";
    - **sem relação nem ordem vigente**: ato que exista não se esconde — um Edital retificado de
      pontuação para sorteio pode ter ordem vazia emitida antes.

    **Uma consulta para o Perfil**, e não a lista das inscrições: as Modalidades declaradas,
    distintas. É o que `projecao.elegiveis` pergunta a cada inscrição, sem trazê-las.
    """
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.editais.domain import marcos
    from processo_seletivo.inscricoes.domain.periodo import (
        ENCERRADO,
        NAO_DESIGNADO,
        periodo_de_inscricoes,
    )

    if not marcos.marco_ordena_por_sorteio(conteudo, perfil_id=perfil_id, marco_id=marco_id):
        return set()
    estado = periodo_de_inscricoes(conteudo, agora or timezone.now()).estado
    if estado not in (ENCERRADO, NAO_DESIGNADO):
        return set()
    declaradas = {
        str(modalidade) if modalidade else None
        for modalidade in Inscricao.objects.filter(
            edital=edital, profile_id=perfil_id, status=Inscricao.Status.SUBMETIDA
        )
        .values_list("modality_id", flat=True)
        .distinct()
    }
    vazios = set()
    for lista_id, _ in recortes_do_perfil(conteudo, perfil_id=perfil_id):
        # A ampla reúne todos os inscritos; a lista, quem a declarou (`projecao.elegiveis`).
        if declaradas if lista_id is None else str(lista_id) in declaradas:
            continue
        if relacao_vigente(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        ):
            continue
        if ato_vigente(edital=edital, marco_id=str(marco_id), lista_id=lista_id) is not None:
            continue
        vazios.add(lista_id)
    return vazios


def _rotulo_da_modalidade(perfil, lista_id):
    for modalidade in perfil.get("competitionModalities") or []:
        if str(modalidade.get("id")) == str(lista_id):
            nome = modalidade.get("name") or ""
            return f"{nome} ({modalidade.get('code')})" if modalidade.get("code") else nome
    return ""


def _nome_da_apontada(perfil):
    """O nome da Modalidade apontada como a ampla, para a frase da tela (FR-3895); "" sem ela."""
    apontada = perfil.get("generalCompetitionModalityId")
    return _rotulo_da_modalidade(perfil, apontada) if apontada else ""


def registros_excedentes(*, edital, perfil_id, marco_id, at=None):
    """O acervo do recorte excedente daquele marco, com a frase da origem de cada um (122, FR-3903).

    **Uma consulta por espécie**, e as versões do Edital uma vez só: são as quatro espécies que o
    sorteio produzia no recorte — relação, sorteio, ato e publicação —, e cada uma é rara. O
    recorte excedente é o que a versão **vigente** aponta (FR-3911); a frase de cada registro sai da
    versão que **ele** cita, e por isso distingue o nascido excedente do que uma Retificação tornou
    excedente.

    Nenhuma linha leva a gesto: o endereço de cada uma é o de consulta — a página pública da
    relação, a verificação do sorteio, a tela do ato e a página pública do resultado.
    """
    from django.urls import reverse

    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.publicacoes.application.papel_do_recorte import (
        frase_do_registro,
        versoes_do_edital,
    )
    from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio

    versoes = versoes_do_edital(edital, at=at)
    if not versoes:
        return []
    perfil = next(
        (p for p in versoes[-1][1].get("profiles") or [] if str(p.get("id")) == str(perfil_id)),
        {},
    )
    apontada = perfil.get("generalCompetitionModalityId")
    if not apontada:
        return []
    filtro = {"edital": edital, "perfil_id": perfil_id, "marco_id": marco_id, "lista_id": apontada}
    especies = (
        (
            "Relação de habilitados",
            RelacaoDeHabilitados.objects.filter(**filtro),
            lambda r: r.versao_id,
            lambda r: r.publicada_em,
            lambda r: reverse("portal:relacao-de-habilitados", args=[r.id]),
        ),
        (
            "Sorteio",
            Sorteio.objects.filter(**filtro).select_related("relacao"),
            lambda r: r.relacao.versao_id,
            lambda r: r.executado_em,
            lambda r: reverse("portal:verificar-sorteio", args=[r.id]),
        ),
        (
            "Ato de classificação",
            AtoDeOrdenacao.objects.filter(**filtro),
            lambda r: r.versao_id,
            lambda r: r.emitido_em,
            lambda r: reverse("interface:ato-de-ordenacao", args=[edital.id, marco_id, r.id]),
        ),
        (
            "Resultado divulgado",
            PublicacaoResultado.objects.filter(**filtro).select_related("ato"),
            lambda r: r.ato.versao_id,
            lambda r: r.publicado_em,
            lambda r: reverse("portal:resultado", args=[r.id]),
        ),
    )
    registros = []
    for especie, consulta, versao_de, quando, url in especies:
        for registro in consulta:
            registros.append(
                {
                    "especie": especie,
                    "quando": quando(registro),
                    "url": url(registro),
                    "frase": frase_do_registro(
                        versoes,
                        perfil_id=perfil_id,
                        lista_id=apontada,
                        versao_id=versao_de(registro),
                    ),
                }
            )
    return sorted(registros, key=lambda r: r["quando"])
