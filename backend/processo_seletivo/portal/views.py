"""O canal público: quem é de fora encontra a seleção e decide se quer participar.

Duas telas na entrega 1 — a vitrine e o detalhe —, e as duas leem **exclusivamente** a versão
consolidada vigente (FR-011). Nenhuma view daqui consulta `PerfilVaga`, `ModalidadeConcorrencia`
ou qualquer tabela de elaboração: o que o candidato lê é o que foi publicado, e é isso que torna
reproduzível, depois, sob qual regra cada pessoa se inscreveu.

O que **ainda não** existe aqui, e é da entrega 2: situação das inscrições e convite por vaga.
Os dois dependem da designação do período, que o Edital ainda não sabe fazer. A US1 se completa
lá; esta entrega é a fatia navegável dela.
"""

from hashlib import sha256

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from processo_seletivo.editais.domain.documentos import aplicaveis
from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    descartes_por_mudanca_de_modalidade,
    gravar_dados,
    remover_documento,
    requisitos_da_inscricao,
)
from processo_seletivo.inscricoes.application.submissao import (
    documentos_que_a_retificacao_invalida,
    edital_foi_retificado,
    enviar_inscricao,
    pendencias_para_enviar,
    reconhecer_versao,
)
from processo_seletivo.inscricoes.domain.arquivos import tamanho_legivel
from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao
from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes, recebe_inscricoes
from processo_seletivo.inscricoes.domain.pessoais import (
    cpf_valido,
    formatar_cpf,
    formatar_telefone,
    telefone_valido,
)
from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade
from processo_seletivo.inscricoes.infrastructure import comprovante_pdf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.portal import identidade as identidade_do_candidato
from processo_seletivo.portal.arquivos import entregar_ao_titular
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada, resposta_privada

# O limite da coluna, aplicado antes de a gravação chegar ao banco.
LIMITE_DO_TELEFONE = 30

# A mesma tradução que o documento publicado usa, e pelo mesmo motivo: `UNLIMITED` é forma
# interna, e forma interna não é o que se lê numa página de oportunidade.
RESERVA = {
    "NONE": "",
    "LIMITED": "com cadastro reserva",
    "UNLIMITED": "com cadastro reserva ilimitado",
}


def _selecao(versao):
    """O que a página precisa saber, tirado do conteúdo publicado e de mais nada.

    A unidade vem do Edital porque escopo institucional é identificação do ato, não conteúdo
    normativo — não está no snapshot e não deveria estar.
    """
    conteudo = versao.content
    return {
        "edital_id": versao.edital_id,
        "periodo": periodo_de_inscricoes(conteudo, timezone.now()),
        "processo_codigo": conteudo.get("processoCode", ""),
        "processo_titulo": conteudo.get("processoTitle", ""),
        "unidade": versao.edital.institution_scope.upper(),
        "numero": conteudo.get("number", ""),
        "ano": conteudo.get("year", ""),
        "titulo": conteudo.get("title", ""),
        "descricao": conteudo.get("description", ""),
        "publicacao_id": versao.source_publication_id,
    }


ETAPAS = ("Seus dados e documentos", "Revisão", "Comprovante")


def etapas_ate(atual: int) -> list[dict]:
    """Onde a pessoa está, e quanto falta (L3 da auditoria de percurso).

    Três, e não cinco: a identificação já passou quando esta lista aparece, e os documentos
    acontecem **dentro** da primeira etapa — anunciá-los como etapa própria prometeria uma tela
    que não existe.
    """
    return [
        {
            "nome": nome,
            "estado": "concluida" if indice < atual else "atual" if indice == atual else "pendente",
        }
        for indice, nome in enumerate(ETAPAS)
    ]


def _perfil(perfil):
    vagas = perfil.get("immediateVacancies") or 0
    return {
        "codigo": perfil.get("code", ""),
        "nome": perfil.get("name", ""),
        "descricao": perfil.get("description", ""),
        "localidade": perfil.get("locality", ""),
        "vagas": vagas,
        "reserva": RESERVA.get(perfil.get("reserveType"), ""),
        "requisitos": perfil.get("requirements") or [],
        "modalidades": [
            modalidade.get("name", "") for modalidade in perfil.get("competitionModalities") or []
        ],
    }


def _documentos_anunciados(conteudo, perfil):
    """O que será pedido, dito **antes** da identificação (L7 da auditoria de percurso).

    A página pública listava requisitos de titulação e nada sobre arquivos: para descobrir que
    precisaria do diploma digitalizado, a pessoa tinha de se identificar e abrir uma inscrição.
    Quem lê no ônibus e não tem os arquivos à mão desiste no meio — e volta, se souber o que
    preparar.

    A modalidade ainda não foi escolhida, então a lista se divide: o que vale para todo mundo
    naquele Perfil, e o que cada modalidade acrescenta. É a mesma função de aplicabilidade que
    decide o que a inscrição pede — três leituras da mesma regra, e não três interpretações.
    """
    exigidos = conteudo.get("documentRequirements") or []
    perfil_id = str(perfil.get("id"))
    sempre = aplicaveis(exigidos, profile_id=perfil_id, modality_id=None)
    nomes_de_sempre = {str(item.get("id")) for item in sempre}
    por_modalidade = []
    for modalidade in perfil.get("competitionModalities") or []:
        com_ela = [
            item.get("name", "")
            for item in aplicaveis(
                exigidos, profile_id=perfil_id, modality_id=str(modalidade.get("id"))
            )
            if str(item.get("id")) not in nomes_de_sempre
        ]
        if com_ela:
            por_modalidade.append({"modalidade": modalidade.get("name", ""), "documentos": com_ela})
    return {
        "sempre": [item.get("name", "") for item in sempre],
        "por_modalidade": por_modalidade,
    }


def vitrine(request):
    """As seleções que estão publicadas, sem nada de gestão e sem pedir identificação.

    O cartão diz o que decide entrar ou não entrar: para qual vaga, quantas, até quando e quanto
    tempo resta. Antes dizia o nome do processo e a data-limite, e descobrir se havia vaga para si
    custava abrir a página — o que quem procura emprego faz uma vez, não dez.

    Abertas primeiro, e entre elas a que fecha antes: a ordem da página é a ordem da urgência de
    quem lê, e não a de criação de quem publicou.
    """
    agora = timezone.now()
    selecoes = [_selecao_da_vitrine(versao, agora) for versao in selectors.selecoes_publicas()]
    ordem = {"aberto": 0, "futuro": 1}
    selecoes.sort(
        key=lambda item: (
            ordem.get(item["periodo"].estado, 2),
            item["periodo"].fim or item["periodo"].inicio or agora,
        )
    )
    return render(
        request,
        "portal/vitrine.html",
        {
            "selecoes": selecoes,
            "abertas": [s for s in selecoes if s["periodo"].estado == "aberto"],
            "outras": [s for s in selecoes if s["periodo"].estado != "aberto"],
        },
    )


def _selecao_da_vitrine(versao, agora):
    """O cartão da vitrine: o da página da seleção, mais o que decide clicar.

    Perfis e vagas vêm do conteúdo publicado, e não de uma contagem própria: é o mesmo número que
    a página da seleção mostra, lido do mesmo lugar.
    """
    dados = _selecao(versao)
    perfis = versao.content.get("profiles") or []
    periodo = dados["periodo"]
    return {
        **dados,
        "perfis": [perfil.get("name", "") for perfil in perfis if perfil.get("name")],
        "vagas": sum(perfil.get("immediateVacancies") or 0 for perfil in perfis),
        "tem_reserva": any((perfil.get("reserveType") or "NONE") != "NONE" for perfil in perfis),
        "dias_restantes": _dias_ate(periodo.fim, agora) if periodo.estado == "aberto" else None,
    }


def _dias_ate(quando, agora):
    """Quantos dias faltam, arredondado para baixo — `None` quando não há prazo declarado.

    Arredondado para baixo porque a pessoa precisa saber de quanto tempo **dispõe**, e dizer
    "faltam 3 dias" para 2 dias e 20 horas empurraria alguém a deixar para depois do prazo.
    """
    if quando is None:
        return None
    return max((quando - agora).days, 0)


def _destino_seguro(request, padrao):
    """Para onde voltar depois de identificar-se (FR-025).

    O destino vem da requisição, e por isso é conferido: um endereço externo aqui transformaria a
    identificação numa ponte para fora do sistema. Só caminho deste host passa.
    """
    destino = request.POST.get("destino") or request.GET.get("destino") or ""
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return destino
    return padrao


def selecao(request, edital_id):
    """O detalhe de uma seleção, orientado à decisão de participar.

    Continua abrindo depois de encerrada e depois de cancelada (FR-017): o que foi publicado
    permanece legível. O que muda com o cancelamento é deixar de ser anunciado na vitrine.
    """
    try:
        versao = selectors.selecao_publica(edital_id=edital_id)
    except DomainError as exc:
        raise Http404 from exc
    contexto = _selecao(versao)
    iniciadas = _inscricoes_iniciadas(request, edital_id)
    contexto["perfis"] = [
        _perfil_da_vitrine(perfil, iniciadas, versao.content)
        for perfil in versao.content.get("profiles") or []
    ]
    # Consultável e recebendo inscrição são decisões diferentes: um Edital cancelado continua
    # legível — o ato publicado não se apaga — e não convida ninguém a se inscrever no que não
    # existe mais.
    # A urgência também aqui, e não só na vitrine: é nesta página que a pessoa decide se começa
    # agora ou depois, e "faltam 3 dias" decide isso melhor do que uma data.
    contexto["dias_restantes"] = (
        _dias_ate(contexto["periodo"].fim, timezone.now())
        if contexto["periodo"].estado == "aberto"
        else None
    )
    contexto["recebe_inscricoes"] = recebe_inscricoes(
        status=versao.edital.status, conteudo=versao.content, agora=timezone.now()
    )
    resposta = render(request, "portal/selecao.html", contexto)
    # A página é pública, mas deixa de ser genérica quando quem lê já começou uma inscrição: o
    # `Continuar inscrição` diz que aquela pessoa se inscreveu. Num computador compartilhado, o
    # histórico entregaria isso a quem sentar depois (FR-075a).
    return marcar_como_privada(resposta) if iniciadas else resposta


def _inscricoes_iniciadas(request, edital_id):
    """As inscrições que **esta** pessoa já abriu neste Edital, por Perfil.

    Sem identidade não há o que procurar, e é por isso que a consulta nem acontece: a página
    pública continua sendo pública, e ninguém descobre inscrição de terceiro por ela.
    """
    identidade = identidade_do_candidato.identidade_da_sessao(request)
    if identidade is None:
        return {}
    return {
        str(registro.profile_id): registro
        for registro in Inscricao.objects.filter(
            identity_subject=identidade.subject, edital_id=edital_id
        )
    }


def _perfil_da_vitrine(perfil, iniciadas, conteudo):
    registro = iniciadas.get(str(perfil.get("id")))
    return {
        **_perfil(perfil),
        "documentos_anunciados": _documentos_anunciados(conteudo, perfil),
        "id": str(perfil.get("id")),
        # O convite muda de texto conforme o estado: `Inscrever-se nesta vaga` para quem chega,
        # `Continuar inscrição` para quem voltou, `Ver comprovante` para quem já enviou (FR-016,
        # FR-029, FR-065). Três estados numa linha, e nenhum portal do candidato.
        "inscricao_id": None if registro is None else registro.id,
        "enviada": registro is not None and registro.status == Inscricao.Status.SUBMETIDA,
    }


@require_http_methods(["GET", "POST"])
@resposta_privada
def identificar(request):
    """A identificação do candidato — provedor de demonstração enquanto o real não existe.

    A tela diz o que é, sem eufemismo: quem se identifica aqui declara quem é, e nada verifica a
    declaração. Em produção o processo nem sobe com este provedor ligado (FR-024).
    """
    if not identidade_do_candidato.provedor_de_demonstracao():
        raise Http404
    destino = _destino_seguro(request, reverse("portal:vitrine"))
    erros = []
    dados = {"nome": "", "cpf": "", "email": ""}
    if request.method == "POST":
        dados = {campo: request.POST.get(campo, "").strip() for campo in dados}
        erros = _recusas_da_identificacao(dados)
        if not erros:
            # Uma forma só: o CPF entra como a pessoa digitou e é guardado sempre igual. Sem isto
            # a mesma pessoa aparece de três jeitos nas telas de quem confere.
            dados["cpf"] = formatar_cpf(dados["cpf"])
            identidade = identidade_do_candidato.identificar(request, **dados)
            return _retomar(request, destino, identidade)
    return render(
        request,
        "portal/identificar.html",
        {"destino": destino, "erros": erros, "dados": dados},
    )


def _retomar(request, destino, identidade):
    """Volta ao ponto de origem — e, quando ele era o convite, conclui o que a pessoa pediu.

    O convite é POST, porque abrir rascunho cria registro e pratica ato auditado. O retorno depois
    da identificação é GET, e mandar a pessoa de volta a uma rota que só aceita POST a deixaria
    numa recusa do navegador. Em vez de abrir o convite para GET — o que faria um endereço
    compartilhado criar inscrição —, a identificação resolve a intenção que já estava declarada:
    quem clicou em "inscrever-se" e se identificou entra na inscrição, e não numa tela a mais.
    """
    try:
        rota = resolve(destino)
    except Resolver404:
        return redirect(destino)
    if rota.view_name != "portal:inscrever":
        return redirect(destino)
    inscricao_aberta = abrir_inscricao(
        identidade=identidade,
        edital_id=rota.kwargs["edital_id"],
        profile_id=rota.kwargs["profile_id"],
        correlation_id=getattr(request, "correlation_id", ""),
    )
    return redirect(reverse("portal:inscricao", args=[inscricao_aberta.id]))


def _recusas_da_identificacao(dados):
    """As recusas que a pessoa lê, e os limites que a persistência impõe.

    O comprimento entra aqui porque sem ele o campo grande demais atravessa a aplicação inteira e
    estoura na gravação — em PostgreSQL, como erro de servidor. Recusar antes é a diferença entre
    "o nome é longo demais" e uma página de erro sem explicação.
    """
    recusas = {}
    limites = identidade_do_candidato.LIMITES
    if not dados["nome"]:
        recusas["nome"] = "Informe seu nome completo."
    elif len(dados["nome"]) > limites["nome"]:
        recusas["nome"] = f"O nome pode ter no máximo {limites['nome']} caracteres."
    elif len([parte for parte in dados["nome"].split() if len(parte) > 1]) < 2:
        # O rótulo pede o nome **completo**, e "Joao" passava. O nome vai no comprovante e é por
        # ele que a comissão confere o documento apresentado: um primeiro nome sozinho obriga a
        # conferência manual que esta feature existe para tirar.
        recusas["nome"] = "Informe o nome completo, com sobrenome."
    if len(identidade_do_candidato.normalizar_cpf(dados["cpf"])) != 11:
        recusas["cpf"] = "Informe um CPF com 11 dígitos."
    elif len(dados["cpf"]) > limites["cpf"]:
        recusas["cpf"] = "Informe o CPF apenas com números ou na forma 000.000.000-00."
    elif not cpf_valido(dados["cpf"]):
        # Contar onze dígitos aceitava qualquer número inventado. O CPF decide de quem é a
        # inscrição e alimenta o `subject` da auditoria: digitado errado, produz uma identidade
        # que ninguém reencontra — a pessoa volta, digita certo, e sua inscrição "sumiu".
        recusas["cpf"] = "Este CPF não existe. Confira os números digitados."
    if "@" not in dados["email"]:
        recusas["email"] = "Informe um e-mail válido."
    elif len(dados["email"]) > limites["email"]:
        recusas["email"] = f"O e-mail pode ter no máximo {limites['email']} caracteres."
    return recusas


@require_http_methods(["POST"])
def sair(request):
    identidade_do_candidato.encerrar(request)
    return redirect(_destino_seguro(request, reverse("portal:vitrine")))


@require_http_methods(["POST"])
def inscrever(request, edital_id, profile_id):
    """Começa — ou retoma — a inscrição naquela vaga.

    POST, e não link: abrir rascunho cria registro e pratica ato auditado, e isso não é o que um
    GET significa. Quem não está identificado vai identificar-se e **volta para cá** (FR-025).
    """
    identidade = identidade_do_candidato.identidade_da_sessao(request)
    aqui = reverse("portal:inscrever", args=[edital_id, profile_id])
    if identidade is None:
        return redirect(f"{reverse('portal:identificar')}?destino={aqui}")
    inscricao = abrir_inscricao(
        identidade=identidade,
        edital_id=edital_id,
        profile_id=profile_id,
        correlation_id=getattr(request, "correlation_id", ""),
    )
    return redirect(reverse("portal:inscricao", args=[inscricao.id]))


@require_http_methods(["GET", "POST"])
@resposta_privada
def inscricao(request, inscricao_id):
    """`Sua inscrição` — uma tela, e o que ela precisa saber vem do conteúdo publicado.

    Nome, CPF e e-mail chegam da identidade e aparecem como **informação**, não como campo
    desabilitado sem explicação (FR-037). O bloco de concorrência só existe quando há escolha
    relevante: um Perfil sem modalidade declarada não faz pergunta nenhuma (FR-038, FR-039).
    """
    identidade = identidade_do_candidato.identidade_da_sessao(request)
    registro = Inscricao.objects.filter(pk=inscricao_id).select_related("edital").first()
    if registro is None:
        # A **mesma** recusa que a titularidade produz, e não um 404 do framework: dois corpos
        # diferentes com o mesmo status continuam dizendo qual identificador existe. Indistinguível
        # é o requisito; igual status não basta (FR-071).
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    exigir_titularidade(registro, identidade)
    versao = selectors.selecao_publica(edital_id=registro.edital_id)
    conteudo = versao.content
    perfil = _perfil_do_conteudo(conteudo, registro.profile_id)
    guardado = False
    erros = []
    # O que a pessoa digitou volta ao campo mesmo quando recusado (SC-UX-007): ler o valor do
    # banco depois de uma recusa apagaria o que ela acabou de escrever.
    telefone_no_campo = registro.telefone
    descartes = []
    if request.method == "POST":
        # A mudança de modalidade que invalida documento já enviado é confirmada antes, com a
        # lista do que se perde: nada some em silêncio, e nada é reaproveitado em silêncio
        # (FR-031).
        descartes = descartes_por_mudanca_de_modalidade(
            conteudo, registro, request.POST.get("modalidade", "").strip() or None
        )
        if descartes and not request.POST.get("confirmar_descarte"):
            return render(
                request,
                "portal/descarte.html",
                {
                    "inscricao": registro,
                    "selecao": _selecao(versao),
                    "descartes": descartes,
                    "modalidade": request.POST.get("modalidade", "").strip(),
                    "telefone": request.POST.get("telefone", "").strip(),
                },
            )
        telefone_no_campo = telefone = request.POST.get("telefone", "").strip()
        if not telefone_valido(telefone):
            # Recusado, e não aparado: um telefone truncado é pior do que nenhum — a equipe liga
            # para um número que não existe e conclui que a pessoa desistiu.
            erros.append("Informe o telefone com DDD, como (27) 99999-0000 — ou deixe em branco.")
        else:
            try:
                registro = gravar_dados(
                    descartes_confirmados=[descarte["id"] for descarte in descartes],
                    identidade=identidade,
                    inscricao=registro,
                    dados={
                        "nome": identidade.nome,
                        "cpf": identidade.cpf,
                        "email": identidade.email,
                        # Guardado numa forma só, como o CPF: `(27) 99999-0000`, venha como vier.
                        "telefone": formatar_telefone(telefone)[:LIMITE_DO_TELEFONE],
                        "modality_id": request.POST.get("modalidade", "").strip(),
                    },
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                return redirect(reverse("portal:revisao", args=[registro.id]))
            except DomainError as exc:
                erros.append(exc.detail)
    return render(
        request,
        "portal/inscricao.html",
        {
            "inscricao": registro,
            "selecao": _selecao(versao),
            "perfil": _perfil_legivel(perfil),
            "telefone_no_campo": telefone_no_campo,
            "cpf_do_candidato": formatar_cpf(registro.cpf),
            "modalidades": _modalidades_ofertadas(perfil),
            "modalidade_unica": _modalidade_unica(perfil),
            "identidade": identidade,
            "guardado": guardado,
            "erros": erros,
            "documentos": _documentos(conteudo, registro),
            "descartes": descartes,
            "etapas": etapas_ate(0),
        },
    )


def _documentos(conteudo, inscricao):
    """Cada requisito aplicável, com o arquivo que já chegou para ele — e o que falta.

    A contagem é do que **falta**, e não do que existe: é a pergunta que o candidato faz, e é a
    que decide se ele pode enviar a inscrição (FR-035, FR-056).
    """
    enviados = {
        str(documento.requirement_id): documento
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
    }
    linhas = []
    for requisito in requisitos_da_inscricao(conteudo, inscricao):
        documento = enviados.get(str(requisito["id"]))
        linhas.append(
            {
                "id": str(requisito["id"]),
                "nome": requisito.get("name", ""),
                "instrucao": requisito.get("instructions", ""),
                "obrigatorio": requisito.get("required", True),
                "enviado": documento,
                # Tamanho e resumo criptográfico vão para o comprovante (D9): são o que permite a
                # alguém, depois, afirmar que o arquivo em mãos é o que foi entregue.
                "tamanho": None if documento is None else tamanho_legivel(documento.tamanho),
            }
        )
    obrigatorios = [linha for linha in linhas if linha["obrigatorio"]]
    recebidos = len([linha for linha in obrigatorios if linha["enviado"]])
    return {
        "linhas": linhas,
        "total": len(obrigatorios),
        "recebidos": recebidos,
        "faltam": len(obrigatorios) - recebidos,
    }


def _perfil_do_conteudo(conteudo, profile_id):
    """O Perfil da inscrição, lido do conteúdo publicado — nunca da tabela de elaboração."""
    return (
        next(
            (
                perfil
                for perfil in conteudo.get("profiles") or []
                if str(perfil.get("id")) == str(profile_id)
            ),
            None,
        )
        or {}
    )


def _perfil_legivel(perfil):
    return {"nome": perfil.get("name", ""), "codigo": perfil.get("code", "")}


def _modalidade_unica(perfil):
    """A modalidade que o Perfil declara sozinha — informada, e não perguntada (FR-038)."""
    modalidades = _modalidades_ofertadas(perfil)
    return modalidades[0] if len(modalidades) == 1 else None


def _modalidades_ofertadas(perfil):
    """As modalidades daquele Perfil, e nenhuma inventada (FR-039).

    Duas consequências da mesma regra: um Perfil sem modalidade declarada não faz nascer "ampla
    concorrência" nenhuma — a pergunta simplesmente não é feita —, e um Perfil que **declara**
    ampla concorrência oferece a dele, sem que o sistema acrescente uma segunda com o mesmo
    significado ao lado.
    """
    return [
        {"id": str(modalidade.get("id")), "nome": modalidade.get("name", "")}
        for modalidade in perfil.get("competitionModalities") or []
    ]


@require_http_methods(["POST"])
def enviar_documento(request, inscricao_id, requirement_id):
    """Um requisito, uma requisição — e a resposta é o bloco de documentos inteiro.

    Requisição própria por arquivo é o que faz o envio persistir na hora, sem `Salvar`, e o que
    faz a recusa de um não derrubar os outros (FR-041, FR-049). A resposta devolve o bloco todo
    porque a contagem "n de m" muda junto: devolver só a linha obrigaria a atualizar dois lugares
    no cliente, e um deles ficaria para trás.
    """
    registro, identidade, versao = _inscricao_do_titular(request, inscricao_id)
    erro = ""
    codigo = ""
    arquivo = request.FILES.get("arquivo")
    if arquivo is None:
        erro = "Escolha um arquivo em PDF."
    else:
        try:
            anexar_documento(
                identidade=identidade,
                inscricao=registro,
                requirement_id=requirement_id,
                arquivo=arquivo,
                correlation_id=getattr(request, "correlation_id", ""),
            )
        except DomainError as exc:
            erro = _erro_do_arquivo(exc)
            codigo = exc.code
    return _bloco_de_documentos(
        request, registro, versao, erro=erro, requisito=requirement_id, codigo=codigo
    )


@require_http_methods(["POST"])
def remover_documento_enviado(request, inscricao_id, requirement_id):
    registro, identidade, versao = _inscricao_do_titular(request, inscricao_id)
    erro = ""
    try:
        remover_documento(
            identidade=identidade,
            inscricao=registro,
            requirement_id=requirement_id,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as exc:
        erro = _erro_do_arquivo(exc)
    return _bloco_de_documentos(request, registro, versao, erro=erro, requisito=requirement_id)


@require_http_methods(["GET"])
def documento_do_candidato(request, inscricao_id, requirement_id):
    """O candidato vê o que enviou — mediado, e recusado a qualquer outra pessoa."""
    registro, _, _ = _inscricao_do_titular(request, inscricao_id)
    return entregar_ao_titular(
        inscricao=registro,
        identidade=identidade_do_candidato.identidade_da_sessao(request),
        requirement_id=requirement_id,
    )


def _erro_do_arquivo(exc):
    """Recusa sobre o arquivo aparece junto do campo; o resto é recusa de página.

    "O arquivo é uma imagem" e "o arquivo é grande demais" são sobre o que a pessoa escolheu, e o
    lugar delas é ao lado do controle. "Este requisito não é seu" e "as inscrições fecharam" não
    são erro de campo — mostrá-las ali sugeriria que escolher outro arquivo resolveria.
    """
    if exc.status != 422:
        raise exc
    return exc.detail


def _inscricao_do_titular(request, inscricao_id):
    identidade = identidade_do_candidato.identidade_da_sessao(request)
    registro = Inscricao.objects.filter(pk=inscricao_id).select_related("edital").first()
    if registro is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    exigir_titularidade(registro, identidade)
    return registro, identidade, selectors.selecao_publica(edital_id=registro.edital_id)


def _bloco_de_documentos(request, inscricao, versao, *, erro="", requisito="", codigo=""):
    resposta = render(
        request,
        "portal/_documentos.html",
        {
            "inscricao": inscricao,
            "documentos": _documentos(versao.content, inscricao),
            "erro_do_envio": erro,
            "requisito_recusado": str(requisito) if erro else "",
            # Foto de celular é o erro mais comum de candidato, e a mensagem explica a causa sem
            # explicar o caminho. Quem não sabe converter continua sem saber (L5 da auditoria).
            "erro_de_imagem": codigo == "file_is_an_image",
            # Resposta de envio, e não render inicial: só aqui o resumo do cabeçalho viaja junto.
            "fragmento": True,
        },
    )
    return marcar_como_privada(resposta)


@require_http_methods(["GET", "POST"])
@resposta_privada
def revisao(request, inscricao_id):
    """A segunda e última tela antes do envio (US5, FR-055 a FR-057).

    Resumo legível, com `Editar` em cada bloco — e voltar não apaga nada, porque não há nada a
    perder: os dados já foram gravados na passagem para cá e os arquivos persistiram no envio de
    cada um.

    O aviso de Retificação aparece **aqui**, antes das declarações: confirmar que leu o Edital
    atualizado é parte do ato, e mostrá-lo depois seria pedir concordância com o que ela não viu.
    """
    registro, identidade, versao = _inscricao_do_titular(request, inscricao_id)
    if registro.status == Inscricao.Status.SUBMETIDA:
        return redirect(reverse("portal:comprovante", args=[registro.id]))
    conteudo = versao.content
    retificado = edital_foi_retificado(registro, versao)
    erros = []
    # O que a pessoa marcou volta marcado. Uma recusa não pode custar o que já estava certo
    # (SC-UX-007): quem marca uma das duas e esquece a outra reencontrava as duas em branco.
    declaracoes = {
        "veracidade": bool(request.POST.get("veracidade")),
        "ciencia": bool(request.POST.get("ciencia")),
    }
    if request.method == "POST":
        if request.POST.get("reconhecer_versao"):
            registro = reconhecer_versao(
                identidade=identidade,
                inscricao=registro,
                versao=versao,
                correlation_id=getattr(request, "correlation_id", ""),
            )
            retificado = False
        else:
            try:
                registro = enviar_inscricao(
                    identidade=identidade,
                    inscricao=registro,
                    declaracoes=declaracoes,
                    # A chave é da Inscrição e da revisão dela: o mesmo botão apertado duas vezes
                    # reserva a mesma chave, e a segunda tentativa devolve o mesmo resultado.
                    idempotency_key=f"envio-{registro.id}-{registro.revision}",
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                return redirect(reverse("portal:comprovante", args=[registro.id]))
            except DomainError as exc:
                erros.append(exc.detail)
                registro.refresh_from_db()
                retificado = edital_foi_retificado(registro, versao)
    return render(
        request,
        "portal/revisao.html",
        {
            "inscricao": registro,
            "selecao": _selecao(versao),
            "perfil": _perfil_legivel(_perfil_do_conteudo(conteudo, registro.profile_id)),
            "modalidade": _modalidade_da_inscricao(conteudo, registro),
            "identidade": identidade,
            "documentos": _documentos(conteudo, registro),
            "pendencias": pendencias_para_enviar(conteudo, registro),
            "retificado": retificado,
            # O que a Retificação deixou de exigir, listado **antes** de a pessoa confirmar: sem
            # isso, o descarte seria silencioso, e sem descarte nenhum ela ficaria presa numa
            # recusa de envio sem saída (FR-031).
            "descartes_da_retificacao": (
                documentos_que_a_retificacao_invalida(registro, versao) if retificado else []
            ),
            "erros": erros,
            "declaracoes": declaracoes,
            "etapas": etapas_ate(1),
        },
    )


def _dados_do_comprovante(request, registro, conteudo, versao):
    """Os fatos do comprovante, num lugar só.

    A página e o PDF são duas apresentações do mesmo documento, e montá-los de fontes diferentes
    faria os dois divergirem na primeira mudança — o candidato teria uma tela e um papel que não
    dizem a mesma coisa.
    """
    documentos = _documentos(conteudo, registro)
    enviados = DocumentoSubmetido.objects.filter(inscricao=registro)
    perfil = _perfil_legivel(_perfil_do_conteudo(conteudo, registro.profile_id))
    selecao = _selecao(versao)
    modalidade = _modalidade_da_inscricao(conteudo, registro)
    aceita = registro.versao_aceita
    return {
        "protocolo": registro.protocolo,
        "codigo_de_verificacao": codigo_de_verificacao(registro, enviados),
        "endereco": request.build_absolute_uri(reverse("portal:vitrine")),
        "campos": [
            ("Processo Seletivo", f"{selecao['processo_titulo']} ({selecao['processo_codigo']})"),
            ("Edital", f"{selecao['numero']}/{selecao['ano']}"),
            ("Perfil de Vaga", perfil["nome"]),
            ("Concorrência", modalidade),
            ("Candidato", registro.nome),
            ("CPF", formatar_cpf(registro.cpf)),
            ("E-mail", registro.email),
            ("Telefone", registro.telefone),
            ("Enviada em", comprovante_pdf.instante(registro.submitted_at)),
            (
                "Versão do Edital",
                (f"vigente desde {comprovante_pdf.instante(aceita.valid_from)}" if aceita else ""),
            ),
        ],
        "documentos": [
            {
                "requisito": linha["nome"],
                "arquivo": linha["enviado"].nome_original,
                "tamanho": linha["tamanho"],
                "quando": comprovante_pdf.instante(linha["enviado"].uploaded_at),
                "resumo": linha["enviado"].content_hash,
            }
            for linha in documentos["linhas"]
            if linha["enviado"]
        ],
    }


@require_http_methods(["GET"])
def comprovante_em_pdf(request, inscricao_id):
    """O comprovante como arquivo, e não como página impressa (FR-063).

    Gerado no servidor porque é documento: nome de arquivo próprio, sem o endereço que o navegador
    escreve na folha, e **bytes determinísticos** — o mesmo comprovante gera sempre o mesmo
    arquivo, e é isso que permite publicar o resumo do próprio documento.

    Titularidade decide o acesso, como em toda página da inscrição: conhecer o identificador não
    autoriza (FR-071).
    """
    registro, _identidade, versao = _inscricao_do_titular(request, inscricao_id)
    if registro.status != Inscricao.Status.SUBMETIDA:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    versao = registro.versao_aceita or versao
    dados = _dados_do_comprovante(request, registro, versao.content, versao)
    arquivo = comprovante_pdf.render_comprovante_pdf(dados)
    resposta = HttpResponse(arquivo, content_type="application/pdf")
    # `attachment`, e não `inline`: o candidato veio buscar um arquivo para guardar, e abrir no
    # visualizador do navegador o devolveria à mesma tela de onde saiu.
    resposta["Content-Disposition"] = f'attachment; filename="Comprovante {registro.protocolo}.pdf"'
    return marcar_como_privada(resposta)


@require_http_methods(["GET"])
@resposta_privada
def comprovante(request, inscricao_id):
    """O que a pessoa leva embora (FR-063).

    Imprimível pelo navegador, e não PDF gerado: o comprovante não é ato normativo — é a prova de
    que a inscrição chegou, e o navegador já sabe imprimir uma página.
    """
    registro, identidade, versao = _inscricao_do_titular(request, inscricao_id)
    if registro.status != Inscricao.Status.SUBMETIDA:
        return redirect(reverse("portal:inscricao", args=[registro.id]))
    # O comprovante é a prova de um ato, e o ato aconteceu sob uma versão. Ler a vigente faria o
    # Perfil e a modalidade impressos mudarem depois de uma Retificação — um comprovante que se
    # reescreve não prova nada (FR-058, FR-063).
    versao = registro.versao_aceita or versao
    conteudo = versao.content
    return render(
        request,
        "portal/comprovante.html",
        {
            "inscricao": registro,
            "selecao": _selecao(versao),
            "perfil": _perfil_legivel(_perfil_do_conteudo(conteudo, registro.profile_id)),
            "modalidade": _modalidade_da_inscricao(conteudo, registro),
            "identidade": identidade,
            "documentos": _documentos(conteudo, registro),
            "etapas": etapas_ate(2),
            # A versão sob a qual a inscrição foi feita, no próprio comprovante: é ela que diz a
            # que regras a pessoa respondeu, e uma Retificação posterior não a altera (FR-058).
            "versao_aceita": registro.versao_aceita,
            # O documento diz quando foi emitido: o cabeçalho do navegador não é parte dele, e
            # quem imprime meses depois precisa saber de quando é o papel que tem em mãos.
            "agora": timezone.now(),
            # O código que prova que **este papel** é o que o sistema emitiu. O resumo de cada
            # arquivo responde pelos anexos; este responde pelo comprovante.
            "codigo_de_verificacao": codigo_de_verificacao(
                registro, DocumentoSubmetido.objects.filter(inscricao=registro)
            ),
            # O resumo do **arquivo** que o botão baixa. Só é possível publicá-lo porque o PDF é
            # determinístico: gerado agora para calcular o resumo, ele sairá idêntico quando o
            # candidato clicar, e idêntico de novo daqui a um ano.
            "resumo_do_pdf": sha256(
                comprovante_pdf.render_comprovante_pdf(
                    _dados_do_comprovante(request, registro, conteudo, versao)
                )
            ).hexdigest(),
            # Formatado na saída, e não só na entrada: inscrições anteriores a esta correção
            # guardaram o CPF como a pessoa digitou.
            "cpf_do_candidato": formatar_cpf(registro.cpf),
        },
    )


def _modalidade_da_inscricao(conteudo, inscricao):
    if inscricao.modality_id is None:
        return ""
    perfil = _perfil_do_conteudo(conteudo, inscricao.profile_id)
    return next(
        (
            modalidade.get("name", "")
            for modalidade in perfil.get("competitionModalities") or []
            if str(modalidade.get("id")) == str(inscricao.modality_id)
        ),
        "",
    )
