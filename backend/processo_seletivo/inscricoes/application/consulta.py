"""O que a equipe consulta — e sob qual autorização.

A permissão é `inscricao:consultar`, e ela é nova. As existentes não serviam: nenhuma delas
significa "pode ler dado pessoal de candidato", e reaproveitar `processo:encerrar` ou
`edital:elaborar` para abrir documento comprobatório seria decidir por omissão o que a
Constituição manda decidir explicitamente. O papel, esse sim, é o que já existia — a permissão
entra no Gestor, que é quem conduz a seleção.

O escopo institucional é conferido junto: um Edital de outro escopo não é "sem permissão", é
inexistente para quem pergunta — a mesma resposta que `require_permission` já dá (FR-072).
"""

from django.core.paginator import Paginator
from django.db.models import Count, Q

from processo_seletivo.inscricoes.application.rascunho import requisitos_da_inscricao
from processo_seletivo.inscricoes.domain.arquivos import tamanho_legivel
from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao
from processo_seletivo.inscricoes.domain.pessoais import mascarar_cpf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError

CONSULTAR = "inscricao:consultar"


def _edital_no_escopo(actor, edital_id):
    require_permission(actor, CONSULTAR)
    try:
        return Edital.objects.get(pk=edital_id, institution_scope=actor.institution_scope)
    except Edital.DoesNotExist as exc:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from exc


def _nome_no_conteudo(conteudo, inscricao):
    perfil = next(
        (
            item
            for item in conteudo.get("profiles") or []
            if str(item.get("id")) == str(inscricao.profile_id)
        ),
        {},
    )
    modalidade = next(
        (
            item.get("name", "")
            for item in perfil.get("competitionModalities") or []
            if str(item.get("id")) == str(inscricao.modality_id)
        ),
        "",
    )
    return perfil.get("name", ""), modalidade


POR_PAGINA = 25


def inscricoes_do_edital(*, actor, edital_id):
    """A lista do que chegou, com o que decide a conferência — e nada de avaliação (FR-067).

    Todas as linhas, sem paginar: é a leitura do conjunto inteiro, e quem a usa quer o conjunto.
    A tela tem porta própria — `consulta_de_inscricoes` —, porque lá a pergunta é outra e mil
    linhas não cabem numa página.
    """
    edital = _edital_no_escopo(actor, edital_id)
    inscricoes = list(
        Inscricao.objects.filter(edital=edital)
        .select_related("versao_aceita")
        .order_by("-submitted_at", "-created_at")
    )
    return edital, _linhas(edital, inscricoes)


def consulta_de_inscricoes(
    *, actor, edital_id, pagina=1, pagina_rascunhos=1, busca=None, perfil=None, modalidade=None
):
    """A tela: paginada, filtrável e com o que substitui a planilha (FR-066, FR-067).

    Mil e quinhentas inscrições numa página só era o convite para o Excel — não por feiura, mas
    porque as perguntas de quem confere não se respondiam ali: "quantas por Perfil", "quantas na
    modalidade reservada", "onde está fulano". Nenhuma delas exige exportar; todas exigem que a
    tela saiba contar e filtrar.

    Os contadores saem de `GROUP BY` e valem o Edital inteiro — o filtro muda o que se lista, e
    nunca o que se conta, senão os números passariam a descrever a pergunta em vez do certame.
    As duas seções paginam em separado porque são dois conjuntos com prazos distintos: o que
    chegou é trabalho, e o que está em preenchimento ainda pode nunca chegar.
    """
    edital = _edital_no_escopo(actor, edital_id)
    vigente = selectors.selecao_publica(edital_id=edital.id)
    consulta = Inscricao.objects.filter(edital=edital).select_related("versao_aceita")
    contagens = _contagens(edital, vigente)
    filtrada = _filtrar(consulta, busca=busca, perfil=perfil, modalidade=modalidade)

    def paginar(queryset, numero):
        return Paginator(queryset.order_by("-submitted_at", "-created_at"), POR_PAGINA).get_page(
            numero
        )

    recebidas = paginar(filtrada.filter(status=Inscricao.Status.SUBMETIDA), pagina)
    rascunhos = paginar(filtrada.filter(status=Inscricao.Status.RASCUNHO), pagina_rascunhos)
    return {
        "edital": edital,
        "pagina_recebidas": recebidas,
        "pagina_rascunhos": rascunhos,
        # As linhas de **cada página**, e não do Edital: é o que torna o custo da tela constante.
        "recebidas": _linhas(edital, list(recebidas), vigente=vigente),
        "em_preenchimento": _linhas(edital, list(rascunhos), vigente=vigente),
        **contagens,
    }


def _filtrar(consulta, *, busca, perfil, modalidade):
    """Perfil e modalidade por identificador, e não por nome.

    A denominação vive no conteúdo publicado, e não em coluna: filtrar por ela exigiria varrer o
    JSON de cada inscrição. O identificador é estável e é o que a tela já carrega nos próprios
    links, então é por ele que se filtra — e é por isso que uma denominação alterada por
    Retificação não quebra o filtro de quem estava no meio da conferência.
    """
    if perfil:
        consulta = consulta.filter(profile_id=perfil)
    if modalidade:
        consulta = consulta.filter(modality_id=modalidade)
    texto = (busca or "").strip()
    if texto:
        # Três formas de procurar a mesma pessoa, porque quem confere tem uma das três em mãos:
        # o nome que leu, o protocolo que ela informou, ou o CPF de um documento.
        digitos = "".join(caractere for caractere in texto if caractere.isdigit())
        alcance = Q(nome__icontains=texto) | Q(protocolo__iexact=texto)
        if digitos:
            alcance |= Q(cpf_normalizado__contains=digitos)
        consulta = consulta.filter(alcance)
    return consulta


def _contagens(edital, vigente):
    """Quantas, e de que tipo — por agregação, e sempre sobre o Edital inteiro.

    Uma consulta para os totais e uma por eixo de recorte. Contar em Python custaria materializar
    mil e quinhentas inscrições para produzir meia dúzia de inteiros.
    """
    conteudo = vigente.content if vigente is not None else {}
    perfis = conteudo.get("profiles") or []
    totais = Inscricao.objects.filter(edital=edital).aggregate(
        recebidas=Count("id", filter=Q(status=Inscricao.Status.SUBMETIDA)),
        rascunhos=Count("id", filter=Q(status=Inscricao.Status.RASCUNHO)),
    )
    enviadas = Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)

    def agrupar(campo):
        # Chave em texto: o banco devolve `UUID`, e o conteúdo publicado traz o identificador
        # como string. Comparar os dois sem normalizar não levanta erro — devolve zero para
        # tudo, que é o pior dos dois mundos: a tela conta, e conta errado.
        return {
            str(identificador): quantas
            for identificador, quantas in enviadas.values_list(campo)
            .annotate(quantas=Count("id"))
            .values_list(campo, "quantas")
            if identificador is not None
        }

    por_perfil = agrupar("profile_id")
    por_modalidade = agrupar("modality_id")
    return {
        "total": totais["recebidas"],
        "total_rascunhos": totais["rascunhos"],
        # O rótulo vem do conteúdo vigente, e a contagem do banco: um Perfil sem inscrição
        # aparece com zero, porque "ninguém se inscreveu para esta vaga" é resposta, não ausência.
        "por_perfil": [
            {
                "id": str(perfil.get("id")),
                "nome": perfil.get("name", ""),
                "quantas": por_perfil.get(str(perfil.get("id")), 0),
            }
            for perfil in perfis
        ],
        "por_modalidade": [
            {
                "id": str(modalidade.get("id")),
                "nome": modalidade.get("name", ""),
                "perfil": perfil.get("name", ""),
                "quantas": por_modalidade.get(str(modalidade.get("id")), 0),
            }
            for perfil in perfis
            for modalidade in perfil.get("competitionModalities") or []
        ],
    }


def _linhas(edital, inscricoes, *, vigente=None):
    """A linha de cada inscrição, com o que decide a conferência.

    A contagem de documentos é sobre os **obrigatórios aplicáveis àquela inscrição**, e não sobre
    o total do Edital: um candidato de ampla concorrência com dois de dois está completo, e exibir
    "2 de 3" por causa de um requisito que não é dele diria que falta algo que não falta.
    """
    if not inscricoes:
        return []
    if vigente is None:
        vigente = selectors.selecao_publica(edital_id=edital.id)
    # Só os documentos das inscrições desta página: sobre o Edital inteiro, o custo da tela
    # crescia com o certame em vez de com o que ela mostra.
    enviados = {}
    for documento in DocumentoSubmetido.objects.filter(
        inscricao__in=[inscricao.pk for inscricao in inscricoes]
    ):
        enviados.setdefault(documento.inscricao_id, set()).add(str(documento.requirement_id))
    coincidentes = _cpfs_coincidentes(edital)
    linhas = []
    for inscricao in inscricoes:
        # **A versão de cada inscrição, e não a vigente para todas.** Uma inscrição enviada
        # responde à versão que ela aceitou: usar a vigente faria Perfil, modalidade e contagem de
        # documentos mudarem retroativamente na lista a cada Retificação — o passado sendo
        # reescrito na tela de quem confere (princípio II).
        conteudo = _conteudo_da_inscricao(inscricao, vigente)
        perfil, modalidade = _nome_no_conteudo(conteudo, inscricao)
        obrigatorios = [
            str(requisito["id"])
            for requisito in requisitos_da_inscricao(conteudo, inscricao)
            if requisito.get("required", True)
        ]
        recebidos = enviados.get(inscricao.id, set())
        linhas.append(
            {
                "id": inscricao.id,
                "protocolo": inscricao.protocolo,
                "candidato": inscricao.nome,
                "cpf": mascarar_cpf(inscricao.cpf),
                "perfil": perfil,
                "modalidade": modalidade,
                "situacao": inscricao.get_status_display(),
                "enviada": inscricao.status == Inscricao.Status.SUBMETIDA,
                "recebidos": len([item for item in obrigatorios if item in recebidos]),
                "esperados": len(obrigatorios),
                "quando": inscricao.submitted_at or inscricao.created_at,
                # Assinalado, e não apenas visível: a coluna mostra o CPF mascarado, e comparar
                # máscaras a olho numa listagem não é detecção (FR-065).
                "cpf_coincidente": (
                    str(inscricao.profile_id),
                    inscricao.cpf_normalizado,
                )
                in coincidentes,
            }
        )
    return linhas


def _cpfs_coincidentes(edital) -> set:
    """Os pares Perfil + CPF com mais de uma inscrição **enviada** neste Edital (FR-064, FR-065).

    O sistema não decide qual das duas vale — essa decisão é institucional, e a regra pertence à
    feature que for avaliar inscrições, junto com o estado, o contraditório e o ato que a
    acompanham. O que ele faz é não deixar a coincidência passar despercebida.

    Só as enviadas: a regra fala do ato de enviar, e rascunho alheio não marca ninguém. E por
    Perfil, porque concorrer a duas vagas distintas é legítimo — a Constituição o diz.
    """
    contagens = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .exclude(cpf_normalizado="")
        .values("profile_id", "cpf_normalizado")
        .annotate(quantas=Count("id"))
        .filter(quantas__gt=1)
    )
    return {(str(linha["profile_id"]), linha["cpf_normalizado"]) for linha in contagens}


def _conteudo_da_inscricao(inscricao, vigente):
    """O conteúdo sob o qual aquela inscrição existe.

    Enviada, é a versão aceita — congelada no ato. Em preenchimento, é a vigente, porque é a ela
    que o candidato ainda está respondendo.
    """
    return (inscricao.versao_aceita or vigente).content


def inscricao_para_consulta(*, actor, inscricao_id):
    """O detalhe, com cada documento **sob o requisito que ele atende** (FR-068).

    É a diferença entre o que este sistema entrega e uma pasta de arquivos: a lista é a dos
    requisitos, e o arquivo aparece dentro do seu. Requisito sem arquivo aparece como requisito
    sem arquivo, que é informação — não uma linha que some.
    """
    inscricao = (
        Inscricao.objects.select_related("edital", "versao_aceita").filter(pk=inscricao_id).first()
    )
    if inscricao is None:
        require_permission(actor, CONSULTAR)
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    _edital_no_escopo(actor, inscricao.edital_id)
    versao = inscricao.versao_aceita or selectors.selecao_publica(edital_id=inscricao.edital_id)
    conteudo = versao.content
    perfil, modalidade = _nome_no_conteudo(conteudo, inscricao)
    enviados = {
        str(documento.requirement_id): documento
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
    }
    documentos = [
        {
            "id": str(requisito["id"]),
            "nome": requisito.get("name", ""),
            "obrigatorio": requisito.get("required", True),
            "enviado": enviados.get(str(requisito["id"])),
            # O tamanho legível acompanha o nome porque dois arquivos com o mesmo nome quase nunca
            # têm o mesmo tamanho; o resumo, que vem do próprio documento, decide quando têm.
            "tamanho": (
                None
                if enviados.get(str(requisito["id"])) is None
                else tamanho_legivel(enviados[str(requisito["id"])].tamanho)
            ),
        }
        for requisito in requisitos_da_inscricao(conteudo, inscricao)
    ]
    return {
        "inscricao": inscricao,
        "perfil": perfil,
        "modalidade": modalidade,
        # O mesmo código impresso no comprovante do candidato: é comparando os dois que quem
        # confere recusa um papel alterado, sem ter de conferir linha por linha.
        "codigo_de_verificacao": (
            codigo_de_verificacao(inscricao, enviados.values()) if inscricao.protocolo else ""
        ),
        "cpf": mascarar_cpf(inscricao.cpf),
        "versao": versao,
        "documentos": documentos,
    }


def documento_para_consulta(*, actor, inscricao_id, requirement_id):
    """O documento que a equipe abre, conferido antes de sair um byte."""
    inscricao = Inscricao.objects.filter(pk=inscricao_id).first()
    if inscricao is None:
        require_permission(actor, CONSULTAR)
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    _edital_no_escopo(actor, inscricao.edital_id)
    documento = DocumentoSubmetido.objects.filter(
        inscricao=inscricao, requirement_id=requirement_id
    ).first()
    if documento is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return documento
