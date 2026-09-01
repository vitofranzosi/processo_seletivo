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

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from processo_seletivo.editais.domain.documentos import aplicaveis
from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import credenciais as nucleo_da_identidade
from processo_seletivo.identidade.application import desafio as desafio_de_acesso
from processo_seletivo.identidade.application.mensagem import (
    avisar_mudanca_de_credencial,
    enviar_codigo,
)
from processo_seletivo.identidade.domain import codigo as codigo_de_acesso
from processo_seletivo.identidade.domain.enderecos import canonizar, endereco_aceitavel
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.inscricoes.application.mensagem import enviar_comprovante
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
        "tem_reserva": any(
            (perfil.get("reserveType") or "NONE") != "NONE" for perfil in perfis
        ),
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



# ---------------------------------------------------------------------------
# Acesso sem senha (010). Três telas curtas, e a decisão de a qual identidade o endereço pertence
# acontece entre a validação do código e a criação de qualquer vínculo (FR-052).
# ---------------------------------------------------------------------------

CHAVE_DO_ENDERECO = "portal_acesso_email"
CHAVE_DO_DESAFIO = "portal_acesso_desafio"
# Qual desafio está em curso. Sem isto, um código pedido para retomar seria validado como se fosse
# de entrar, e a finalidade da FR-028 seria decorativa.
CHAVE_DA_FINALIDADE = "portal_acesso_finalidade"
# Para onde voltar depois de informar nome e CPF: quem chegou a caminho de uma vaga não pode ser
# despejado numa lista vazia e obrigado a procurar tudo de novo.
CHAVE_DO_DESTINO = "portal_acesso_destino"
# O que dizer sobre o último pedido de código — inclusive "nada foi enviado". Sobrevive ao
# redirecionamento porque a tela que precisa da notícia é a seguinte, e é lida uma vez só.
CHAVE_DO_ENVIO = "portal_acesso_envio"
# O que dizer na tela seguinte sobre o ato que acabou de acontecer. Um par de chaves para todo o
# portal, e não uma por tela: quatro atos mudavam a página em silêncio, e silêncio depois de uma
# ação é indistinguível de falha.
CHAVE_DO_AVISO = "portal_aviso"
CHAVE_DA_RECUSA = "portal_recusa"
# A mesma frase nos quatro casos que poderiam revelar existência: endereço com identidade, sem
# identidade, limite esgotado e falha de envio (FR-020, FR-021, FR-083).
AVISO_NEUTRO = "Se este endereço puder ser utilizado, enviaremos um código de acesso."


def _avisar(request, texto: str) -> None:
    """Guarda a confirmação para a tela em que a pessoa vai cair."""
    request.session[CHAVE_DO_AVISO] = texto


def _recusar(request, texto: str) -> None:
    request.session[CHAVE_DA_RECUSA] = texto


def _mensagens(request) -> dict:
    """Lidas uma vez só, e por quem as exibe.

    Lidas aqui, e não num processador de contexto: aquele roda também para os fragmentos que o
    htmx devolve, e a confirmação seria consumida por um envio de arquivo que aconteceu logo
    depois — some sem nunca ter sido lida.
    """
    return {
        "aviso": request.session.pop(CHAVE_DO_AVISO, ""),
        "recusa": request.session.pop(CHAVE_DA_RECUSA, ""),
    }


def _origem(request) -> str:
    """O que distingue uma origem da outra, sem guardar de onde veio.

    **O cabeçalho de proxy só é lido quando a implantação declara que existe um proxy.** Ele é
    escrito pelo cliente: lê-lo sempre tornava o limite por origem decorativo — quem varre
    endereços mandava um valor diferente a cada requisição, cada uma parecia vir de outro lugar, e
    o teto nunca era alcançado. Sobrava só o limite por endereço, que não contém exatamente o caso
    que o limite por origem existe para conter.

    Atrás de um proxy que sobrescreve o cabeçalho, `REMOTE_ADDR` é sempre o mesmo e não distingue
    ninguém — daí a variável. Quem implanta declara o que é verdade na sua topologia; o padrão é
    não confiar. O valor é resumido antes de ser gravado (D-005).
    """
    if getattr(settings, "PORTAL_ATRAS_DE_PROXY", False):
        encaminhado = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if encaminhado:
            return encaminhado.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def acesso(request):
    """Informe seu e-mail — e a resposta é a mesma para todo mundo."""
    destino = _destino_seguro(request, "")
    if destino:
        request.session[CHAVE_DO_DESTINO] = destino
    if identidade_do_candidato.identidade_autenticada(request):
        return redirect(reverse("portal:inscricoes"))
    if request.method != "POST":
        return render(request, "portal/acesso_email.html", {"email": "", "erro": ""})

    informado = request.POST.get("email", "").strip()
    if not endereco_aceitavel(informado):
        # Recusa da **forma**, anterior a qualquer consulta: ela não revela nada sobre quem existe.
        return render(
            request,
            "portal/acesso_email.html",
            {"email": informado, "erro": "Informe um e-mail válido."},
        )

    canonico = canonizar(informado)
    # Reenviar é pedir de novo o mesmo endereço estando já na tela do código. A distinção não muda
    # nada do que acontece — muda o que a tela diz depois, e é justamente isso que faltava.
    reenvio = request.session.get(CHAVE_DO_ENDERECO, "") == informado
    _, codigo = desafio_de_acesso.solicitar(
        email_canonico=canonico,
        finalidade=DesafioDeAcesso.Finalidade.ENTRAR,
        origem=_origem(request),
    )
    enviar_codigo(para=informado, codigo=codigo, finalidade=DesafioDeAcesso.Finalidade.ENTRAR)
    request.session[CHAVE_DO_ENDERECO] = informado
    request.session[CHAVE_DA_FINALIDADE] = DesafioDeAcesso.Finalidade.ENTRAR
    request.session[CHAVE_DO_ENVIO] = _noticia_do_envio(enviado=bool(codigo), reenvio=reenvio)
    return redirect(reverse("portal:acesso-codigo"))


def _noticia_do_envio(*, enviado: bool, reenvio: bool) -> str:
    """O que dizer sobre o pedido que acabou de acontecer — inclusive quando nada aconteceu.

    O botão de reenviar estava sempre clicável e, dentro da janela de espera, não enviava nada e
    não dizia nada: a página recarregava idêntica e a recusa que estava na tela sumia junto, o que
    fazia o clique **parecer** ter dado certo. A pessoa passava a esperar um e-mail que nunca foi
    enviado. Silêncio é a pior resposta possível aqui, porque é indistinguível de sucesso.

    Nenhuma das frases depende de existir identidade: o que decide é a contagem de pedidos daquele
    endereço e daquela origem, que avança igual para quem existe e para quem não existe (FR-021).
    """
    if enviado:
        return "Enviamos um código novo. Use o mais recente." if reenvio else ""
    # Sem número aqui de propósito: a contagem ao lado do botão é recalculada a cada renderização
    # e corre em tempo real. Repetir o valor apurado no instante do POST punha dois números
    # diferentes para a mesma espera na mesma tela.
    return (
        "Ainda não enviamos outro código — o pedido anterior foi há pouco. "
        "Veja abaixo quando será possível pedir de novo."
    )


def acesso_codigo(request):
    """Informe o código — um campo só, que aceita a colagem inteira (UX-005)."""
    informado = request.session.get(CHAVE_DO_ENDERECO, "")
    if not informado:
        return redirect(reverse("portal:acesso"))
    canonico = canonizar(informado)
    finalidade = request.session.get(CHAVE_DA_FINALIDADE, DesafioDeAcesso.Finalidade.ENTRAR)
    contexto = {
        "email": informado,
        "erro": "",
        # Recalculada a cada renderização: guardada na sessão, a espera envelhecia junto com a
        # página e anunciava sessenta segundos depois de dois minutos parada ali (UX-006).
        "espera": desafio_de_acesso.espera_de_reenvio(
            email_canonico=canonico, finalidade=finalidade
        ),
        "aviso": AVISO_NEUTRO,
        "noticia": request.session.pop(CHAVE_DO_ENVIO, ""),
    }
    if request.method != "POST":
        return render(request, "portal/acesso_codigo.html", contexto)

    digitado = request.POST.get("codigo", "")
    if not codigo_de_acesso.formato_aceitavel(digitado):
        contexto["erro"] = "O código tem seis dígitos."
        return render(request, "portal/acesso_codigo.html", contexto)

    desafio = desafio_de_acesso.validar(
        email_canonico=canonico, finalidade=finalidade, codigo=digitado
    )
    if desafio is None:
        contexto["erro"] = _recusa_do_codigo(canonico, finalidade)
        return render(request, "portal/acesso_codigo.html", contexto)

    if finalidade == DesafioDeAcesso.Finalidade.RETOMAR:
        return _abrir_retomada(request, desafio)
    if finalidade == DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL:
        return _concluir_adicao(request, desafio)
    return _decidir_a_quem_pertence(request, desafio, informado)


def _recusa_do_codigo(email_canonico: str, finalidade: str) -> str:
    """Diz qual dos motivos foi — e é a correção de um defeito que perdia candidato.

    A frase única ("código inválido ou expirado") cobria quatro situações, e uma delas é fatal:
    esgotadas as cinco tentativas, o desafio morre, mas quem depois encontrava o código **certo**
    na caixa de entrada e o digitava corretamente lia exatamente a mesma recusa. Do lado de cá o
    sistema estava correto; do lado de lá ele estava mentindo. A pessoa parava ali.

    A FR-031 continua respeitada: ela proíbe distinguir código errado de endereço inexistente, e
    nenhuma destas frases faz isso — `solicitar` cria desafio para qualquer endereço de forma
    aceitável, então motivo e saldo são idênticos exista ou não identidade (ver `estado_atual`).
    """
    estado = desafio_de_acesso.estado_atual(email_canonico=email_canonico, finalidade=finalidade)
    if estado.motivo == desafio_de_acesso.CODIGO_ERRADO:
        if estado.tentativas_restantes == 1:
            return "Código incorreto. Resta 1 tentativa antes de este código ser cancelado."
        return (
            f"Código incorreto. Restam {estado.tentativas_restantes} tentativas "
            "antes de este código ser cancelado."
        )
    if estado.motivo == desafio_de_acesso.ESGOTADO:
        return (
            "As tentativas deste código acabaram e ele foi cancelado — mesmo o código certo não "
            "vale mais. Peça um novo código abaixo."
        )
    if estado.motivo == desafio_de_acesso.EXPIRADO:
        return "Este código expirou. Peça um novo código abaixo."
    return "Este código já foi usado. Peça um novo código abaixo."


def _abrir_retomada(request, desafio):
    """Provado o endereço de novo, o convite volta — agora a partir de dentro."""
    correspondentes = [
        candidata
        for candidata in associacao.correspondencia_historica(desafio.email_canonico)
        if not associacao.esta_vazia(candidata)
    ]
    if not correspondentes:
        return redirect(reverse("portal:inscricoes"))
    associacao.abrir_reconciliacao(desafio, correspondentes)
    request.session[CHAVE_DO_DESAFIO] = str(desafio.pk)
    return redirect(reverse("portal:acesso-reconciliar"))


def _decidir_a_quem_pertence(request, desafio, email_como_informado):
    """A decisão da FR-052, tomada **antes** de qualquer vínculo existir."""
    canonico = desafio.email_canonico
    ja_verificado = associacao.identidade_da_credencial(canonico)
    if ja_verificado is not None:
        return _entrar(request, ja_verificado)

    correspondentes = associacao.correspondencia_historica(canonico)
    if correspondentes:
        associacao.abrir_reconciliacao(desafio, correspondentes)
        request.session[CHAVE_DO_DESAFIO] = str(desafio.pk)
        return redirect(reverse("portal:acesso-reconciliar"))

    return _entrar(
        request, associacao.criar_identidade_com(canonico, email_como_informado)
    )


def _entrar(request, identidade):
    destino = request.session.get(CHAVE_DO_DESTINO, "")
    for chave in (
        CHAVE_DO_ENDERECO,
        CHAVE_DO_DESAFIO,
        CHAVE_DA_FINALIDADE,
        CHAVE_DO_DESTINO,
        CHAVE_DO_ENVIO,
    ):
        request.session.pop(chave, None)
    identidade_do_candidato.abrir_sessao(request, identidade)
    if not destino:
        return redirect(reverse("portal:inscricoes"))
    request.session[CHAVE_DO_DESTINO] = destino
    if nucleo_da_identidade.falta_o_nucleo(identidade):
        # Quem veio a caminho de uma vaga e ainda não tem nome nem CPF informa os dois agora, e
        # volta para a vaga em seguida. Mandá-la primeiro ao convite e só depois ao formulário
        # acrescentaria uma tela sem acrescentar nada.
        return redirect(reverse("portal:meus-dados"))
    return render(request, "portal/retomar_convite.html", {"destino": destino})


def _desafio_provado(request):
    """O desafio cujo código **já foi validado nesta sessão** — a única prova que existe aqui.

    A distinção é a correção de um desvio de autenticação. `CHAVE_DO_ENDERECO` é gravada no POST do
    formulário de acesso, **antes** de qualquer prova: ela diz apenas o que alguém digitou. Só
    `CHAVE_DO_DESAFIO` é gravada depois de o código conferir, e só ela autoriza seguir. Exigir
    `consumido_em` fecha a porta também contra uma sessão forjada com um identificador qualquer.
    """
    identificador = request.session.get(CHAVE_DO_DESAFIO)
    if not identificador:
        return None
    return DesafioDeAcesso.objects.filter(
        pk=identificador, consumido_em__isnull=False
    ).first()


def _endereco_do_desafio(request, desafio):
    """O endereço como a pessoa o informou — mas só se for o mesmo que ela provou.

    O valor da sessão serve para exibição; a identidade é sempre construída sobre o canônico do
    desafio. Divergindo, o canônico ganha: nenhum dado de sessão decide a quem uma credencial
    pertence.
    """
    informado = request.session.get(CHAVE_DO_ENDERECO, "")
    if informado and canonizar(informado) == desafio.email_canonico:
        return informado
    return desafio.email_canonico


def acesso_reconciliar(request):
    """O convite: encontramos participação anterior — e ele é recusável (FR-050)."""
    desafio = _desafio_provado(request)
    if desafio is None:
        # **Sem prova, nada acontece.** A versão anterior criava identidade a partir do endereço
        # guardado na sessão, que é apenas o que alguém digitou no formulário — bastava informar o
        # e-mail de outra pessoa e abrir esta rota para entrar em nome dela, e ainda prender aquele
        # endereço à identidade do atacante pela restrição de unicidade. Quem não validou código
        # nenhum volta para o começo.
        return redirect(reverse("portal:acesso"))

    informado = _endereco_do_desafio(request, desafio)
    if not associacao.reconciliacao_pendente(desafio):
        # Expirou ou esgotou — mas o código **foi** validado, e nenhum desfecho aqui é beco sem
        # saída (FR-052b).
        #
        # A pergunta é a mesma que a primeira associação já faz: aquele endereço **já** pertence a
        # alguém? Na retomada pertence — é uma credencial da identidade em que a pessoa está — e a
        # resposta é reentrar nela. A versão anterior chamava direto a criação de identidade e só
        # não errava porque a violação de unicidade era capturada e devolvia a dona. Correção por
        # acidente: bastava alguém tornar aquela captura estrita para esta linha passar a criar
        # identidade órfã e trocar a sessão da pessoa por ela, sem que nada acusasse.
        dona = associacao.identidade_da_credencial(desafio.email_canonico)
        return _entrar(
            request,
            dona or associacao.criar_identidade_com(desafio.email_canonico, informado),
        )

    contexto = {"erro": ""}
    if request.method != "POST":
        return render(request, "portal/acesso_reconciliar.html", contexto)

    if request.POST.get("acao") == "continuar":
        associacao.encerrar_reconciliacao(desafio)
        _avisar(
            request,
            "Tudo certo. Se mudar de ideia, você pode vincular a participação anterior enquanto "
            "não abrir nenhuma inscrição.",
        )
        return _entrar(
            request, associacao.criar_identidade_com(desafio.email_canonico, informado)
        )

    identidade = associacao.confirmar_cpf(desafio, request.POST.get("cpf", ""))
    if identidade is not None:
        vazia = identidade_do_candidato.identidade_autenticada(request)
        if desafio.finalidade == DesafioDeAcesso.Finalidade.RETOMAR and vazia is not None:
            if not associacao.retomar(vazia=vazia, destino=identidade):
                # A premissa caiu dentro do bloqueio: nasceu inscrição no intervalo. Nada se move.
                contexto["erro"] = (
                    "Não foi possível concluir agora. Sua inscrição em andamento permanece como "
                    "está."
                )
                return render(request, "portal/acesso_reconciliar.html", contexto)
        else:
            associacao.associar_credencial(identidade, desafio.email_canonico, informado)
        associacao.encerrar_reconciliacao(desafio)
        # O momento mais aliviante da jornada acontecia em silêncio: a pessoa confirmava o CPF e
        # caía numa lista que, para ela, podia ser a de sempre. Dizer o que aconteceu é o mínimo.
        _avisar(request, "Pronto: sua participação anterior está aqui.")
        return _entrar(request, identidade)

    if not associacao.reconciliacao_pendente(desafio):
        # Tentativas esgotadas: entra na própria identidade, e o convite morre com o desafio.
        #
        # Com uma frase antes: a pessoa digitava o CPF, apertava confirmar e caía noutra tela sem
        # nenhuma explicação do que tinha acontecido — o desfecho mais confuso do percurso todo.
        _avisar(
            request,
            "Não conseguimos confirmar o CPF desta vez. Sua área está aqui, e você pode tentar "
            "vincular a participação anterior de novo abaixo.",
        )
        return _entrar(
            request, associacao.criar_identidade_com(desafio.email_canonico, informado)
        )
    contexto["erro"] = (
        "Não foi possível confirmar. Confira os números e tente novamente, ou continue sem "
        "vincular sua participação anterior."
    )
    return render(request, "portal/acesso_reconciliar.html", contexto)


def acesso_retomar(request):
    """Retomar a reconciliação recusada por engano — enquanto a identidade estiver vazia (FR-053).

    A janela fecha sozinha assim que a pessoa abre qualquer inscrição, e é isso que torna a
    movimentação segura: não há o que fundir, porque a origem não tem nada.

    Passa por desafio novo, e não pela sessão que já está aberta. São duas razões: a contagem de
    tentativas de CPF mora no desafio, e uma regra só vale para os dois caminhos; e o ato que move
    credenciais e descarta uma identidade merece ser reprovado no instante em que acontece.
    """
    identidade = identidade_do_candidato.identidade_autenticada(request)
    if identidade is None:
        return redirect(reverse("portal:acesso"))
    if not associacao.esta_vazia(identidade):
        # Deixou de ser oferecida. `404` e não `403`: a ação não existe mais para esta identidade.
        raise Http404
    credencial = associacao.credencial_com_correspondencia(identidade)
    if credencial is None:
        raise Http404
    if request.method != "POST":
        return redirect(reverse("portal:inscricoes"))

    _, codigo = desafio_de_acesso.solicitar(
        email_canonico=credencial.email_canonico,
        finalidade=DesafioDeAcesso.Finalidade.RETOMAR,
        origem=_origem(request),
    )
    enviar_codigo(
        para=credencial.email_como_informado,
        codigo=codigo,
        finalidade=DesafioDeAcesso.Finalidade.RETOMAR,
    )
    request.session[CHAVE_DO_ENDERECO] = credencial.email_como_informado
    request.session[CHAVE_DA_FINALIDADE] = DesafioDeAcesso.Finalidade.RETOMAR
    request.session[CHAVE_DO_ENVIO] = _noticia_do_envio(enviado=bool(codigo), reenvio=False)
    return redirect(reverse("portal:acesso-codigo"))


def _conteudos_publicados(inscricoes):
    """O conteúdo vigente de cada Edital da lista — uma leitura por Edital, e não por inscrição.

    Quem tem três inscrições no mesmo Edital lia a versão consolidada três vezes, e cada leitura
    traz o conteúdo publicado inteiro.

    A exceção capturada é **nomeada**: `DomainError` é o que a ausência de versão vigente produz.
    Capturar `Exception` fazia toda a lista degradar em silêncio diante de qualquer defeito de
    leitura — e escondeu um: a primeira versão lia `.conteudo` num objeto cujo atributo se chama
    `content`, e **toda** linha da lista saía sem Edital e sem Perfil, sem que nada acusasse. Os
    testes não pegaram porque afirmavam a situação e a ação, que continuavam certas. Estreitar a
    captura foi o que revelou o defeito.
    """
    conteudos = {}
    for edital_id in {registro.edital_id for registro in inscricoes}:
        try:
            conteudos[edital_id] = selectors.selecao_publica(edital_id=edital_id).content
        except DomainError:
            # Seleção sem versão vigente não apaga a inscrição da lista: a pessoa continua tendo o
            # que enviou, e o protocolo continua valendo.
            conteudos[edital_id] = None
    return conteudos


def _item_da_lista(registro, conteudo):
    """O que decide a próxima ação de uma inscrição, e nada além disso.

    Perfil e Edital vêm do **conteúdo publicado**, como em toda tela do candidato: é o que foi
    publicado que governa a inscrição, e não a linha de elaboração que a Retificação altera depois.

    A ação principal é uma só por item, e é inequívoca: rascunho se continua, enviada se acompanha
    (`SC-UX-005`). Duas ações lado a lado devolveriam à pessoa a decisão que a lista existe para
    tomar por ela.
    """
    enviada = registro.status == Inscricao.Status.SUBMETIDA
    if conteudo is None:
        perfil, edital, processo = {"nome": "", "codigo": ""}, "", ""
    else:
        perfil = _perfil_legivel(_perfil_do_conteudo(conteudo, registro.profile_id))
        edital = f"Edital {conteudo.get('number', '')}/{conteudo.get('year', '')}".strip("/ ")
        # O nome do processo, e não só o número do Edital. Com uma inscrição, "Edital 01/2026"
        # bastava; com três processos abertos ao mesmo tempo — que é a situação normal de um
        # instituto — ele deixa de identificar qualquer coisa.
        processo = conteudo.get("processoTitle", "")
    return {
        "id": registro.id,
        "perfil": perfil["nome"],
        "processo": processo,
        "edital": edital,
        "enviada": enviada,
        "protocolo": registro.protocolo,
        "acao": "Acompanhar" if enviada else "Continuar inscrição",
    }


@require_http_methods(["GET", "POST"])
@resposta_privada
def meus_dados(request):
    """Nome e CPF, uma vez na vida da identidade — e corrigíveis depois (FR-005, FR-008).

    Vive fora da jornada de inscrição de propósito: a `009` não é reaberta, e o que mudou foi de
    onde vêm os dados que ela consome, não a jornada que os usa (P-008).
    """
    registro = identidade_do_candidato.identidade_autenticada(request)
    if registro is None:
        return redirect(reverse("portal:acesso"))
    editavel = not nucleo_da_identidade.cpf_congelado(registro)
    dados = {
        "nome": registro.nome,
        "cpf": formatar_cpf(registro.cpf_normalizado) if registro.cpf_normalizado else "",
    }
    contexto = {"dados": dados, "erros": {}, "cpf_editavel": editavel}
    if request.method != "POST":
        return render(request, "portal/meus_dados.html", contexto)

    dados = {campo: request.POST.get(campo, "").strip() for campo in ("nome", "cpf")}
    erros = nucleo_da_identidade.recusas(dados, cpf_editavel=editavel)
    if erros:
        contexto.update({"dados": dados, "erros": erros})
        return render(request, "portal/meus_dados.html", contexto)

    nucleo_da_identidade.gravar_nucleo(registro, nome=dados["nome"], cpf=dados["cpf"])
    _avisar(request, "Seus dados foram guardados.")
    destino = request.session.pop(CHAVE_DO_DESTINO, "")
    if destino:
        # O convite é POST porque abrir rascunho cria registro e pratica ato auditado — a mesma
        # razão da `009`. Reenviar por formulário é o que evita um endereço compartilhado virar
        # criador de inscrições.
        return render(request, "portal/retomar_convite.html", {"destino": destino})
    return redirect(reverse("portal:inscricoes"))


@require_http_methods(["GET"])
@resposta_privada
def conta(request):
    """Acesso à conta: as credenciais provadas, e qual delas a instituição usa."""
    registro = identidade_do_candidato.identidade_autenticada(request)
    if registro is None:
        return redirect(reverse("portal:acesso"))
    return render(
        request,
        "portal/conta.html",
        {"credenciais": list(registro.credenciais.order_by("created_at")), **_mensagens(request)},
    )


@require_http_methods(["POST"])
def conta_adicionar(request):
    """Pede o código para um endereço novo — e não pede CPF (FR-016).

    A recusa de endereço que já pertence a outra identidade não diz **a quem** (FR-017), e por isso
    ela acontece aqui, antes de qualquer mensagem: enviar código para um endereço alheio e recusar
    depois já teria contado a essa pessoa que alguém tentou.
    """
    registro = identidade_do_candidato.identidade_autenticada(request)
    if registro is None:
        return redirect(reverse("portal:acesso"))
    informado = request.POST.get("email", "").strip()
    if not endereco_aceitavel(informado):
        _recusar(request, "Informe um e-mail válido.")
        return redirect(reverse("portal:conta"))
    canonico = canonizar(informado)
    if nucleo_da_identidade.pertence_a_outra(registro, canonico):
        _recusar(request, "Não foi possível usar este endereço. Tente outro.")
        return redirect(reverse("portal:conta"))
    if canonico in {item.email_canonico for item in registro.credenciais.all()}:
        _avisar(request, "Este endereço já é seu.")
        return redirect(reverse("portal:conta"))

    _, codigo = desafio_de_acesso.solicitar(
        email_canonico=canonico,
        finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
        origem=_origem(request),
    )
    enviar_codigo(
        para=informado,
        codigo=codigo,
        finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
    )
    request.session[CHAVE_DO_ENDERECO] = informado
    request.session[CHAVE_DA_FINALIDADE] = DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL
    request.session[CHAVE_DO_ENVIO] = _noticia_do_envio(enviado=bool(codigo), reenvio=False)
    return redirect(reverse("portal:acesso-codigo"))


def _concluir_adicao(request, desafio):
    """Provado o endereço, ele passa a ser credencial de quem está na sessão (FR-016)."""
    registro = identidade_do_candidato.identidade_autenticada(request)
    if registro is None:
        return redirect(reverse("portal:acesso"))
    if nucleo_da_identidade.pertence_a_outra(registro, desafio.email_canonico):
        # O endereço passou a ser de outra identidade entre o pedido e a confirmação. Antes isto
        # era recusa silenciosa: o código era gasto, nada acontecia, e a pessoa via a lista sem o
        # endereço e sem explicação. A mensagem é a mesma do pedido — não diz a quem pertence.
        _recusar(request, "Não foi possível usar este endereço. Tente outro.")
    else:
        endereco = _endereco_do_desafio(request, desafio)
        nucleo_da_identidade.adicionar(
            registro,
            email_canonico=desafio.email_canonico,
            email_como_informado=endereco,
            correlation_id=getattr(request, "correlation_id", ""),
        )
        _avisar(request, f"{endereco} foi adicionado. Você já pode entrar por ele.")
        # Sem senha, a lista de credenciais **é** a conta: quem consegue anexar um endereço entra
        # por ele para sempre. Este aviso é o único sinal que a titular teria disso.
        principal = next((item for item in registro.credenciais.all() if item.principal), None)
        if principal and principal.email_canonico != desafio.email_canonico:
            avisar_mudanca_de_credencial(
                para=principal.email_como_informado,
                endereco=endereco,
                acao="adicionado",
                atendimento=getattr(settings, "PORTAL_ATENDIMENTO", ""),
            )
    for chave in (CHAVE_DO_ENDERECO, CHAVE_DA_FINALIDADE, CHAVE_DO_ENVIO):
        request.session.pop(chave, None)
    return redirect(reverse("portal:conta"))


@require_http_methods(["POST"])
def conta_principal(request, credencial_id):
    registro = identidade_do_candidato.identidade_autenticada(request)
    if registro is None:
        return redirect(reverse("portal:acesso"))
    if not nucleo_da_identidade.tornar_principal(registro, credencial_id):
        raise Http404
    _avisar(request, "Pronto: é por este endereço que a instituição vai falar com você.")
    return redirect(reverse("portal:conta"))


@require_http_methods(["GET", "POST"])
@resposta_privada
def conta_remover(request, credencial_id):
    """Remover pergunta antes — e avisa a caixa principal depois.

    O botão ficava ao lado de "Tornar principal" e apagava a credencial no primeiro clique, sem
    perguntar e sem dizer nada. Errar o alvo custava uma via de acesso, e a pessoa só descobria na
    vez seguinte em que tentasse entrar por aquele endereço.

    A pergunta é um `GET` na mesma rota, no mesmo formato da confirmação de descarte de documento:
    a tela enuncia o que se perde, e só o `POST` executa.
    """
    registro = identidade_do_candidato.identidade_autenticada(request)
    if registro is None:
        return redirect(reverse("portal:acesso"))
    alvo = registro.credenciais.filter(pk=credencial_id).first()
    if alvo is None:
        # Credencial de outra identidade não existe para esta — a mesma recusa que a titularidade
        # produz em toda a área.
        raise Http404
    if request.method == "GET":
        return render(
            request,
            "portal/conta_remover.html",
            {"credencial": alvo, "e_a_ultima": registro.credenciais.count() == 1},
        )

    endereco = alvo.email_como_informado
    desfecho = nucleo_da_identidade.remover(
        registro, credencial_id, correlation_id=getattr(request, "correlation_id", "")
    )
    if desfecho == nucleo_da_identidade.NAO_E_SUA:
        # Credencial de outra identidade não existe para esta — a mesma recusa que a titularidade
        # produz em toda a área, e não uma mensagem sobre a última credencial dela.
        raise Http404
    if desfecho == nucleo_da_identidade.E_A_ULTIMA:
        # A última não sai: removê-la é apagar o próprio acesso (FR-018). A tela não oferece o
        # botão, e o servidor recusa mesmo assim — esconder não é fronteira de segurança.
        _recusar(request, "Você não pode remover seu último e-mail: é por ele que você entra.")
        return redirect(reverse("portal:conta"))
    _avisar(request, f"{endereco} foi removido. Você não entra mais por ele.")
    # Lida **depois** do ato: removida a principal, outra foi promovida, e é a que resta que
    # precisa saber. Ler antes mandaria o aviso justamente para a caixa que acabou de sair.
    principal = registro.credenciais.filter(principal=True).first()
    avisar_mudanca_de_credencial(
        para=principal.email_como_informado if principal else "",
        endereco=endereco,
        acao="removido",
        atendimento=getattr(settings, "PORTAL_ATENDIMENTO", ""),
    )
    return redirect(reverse("portal:conta"))


def inscricoes(request):
    """Minhas inscrições — a lista, o estado vazio, e a porta de saída dele."""
    identidade = identidade_do_candidato.identidade_autenticada(request)
    if identidade is None:
        return redirect(reverse("portal:acesso"))
    minhas = list(
        Inscricao.objects.filter(identity_subject=identidade.subject).order_by("-created_at")
    )
    conteudos = _conteudos_publicados(minhas)
    return render(
        request,
        "portal/inscricoes.html",
        {
            "inscricoes": [
                _item_da_lista(registro, conteudos.get(registro.edital_id))
                for registro in minhas
            ],
            # O convite de retomada só aparece para quem pode aceitá-lo: identidade sem inscrição
            # alguma e com um endereço que consta de participação anterior de outra identidade. A
            # lista já foi materializada acima; perguntar de novo ao banco seria consulta a mais.
            "pode_retomar": bool(
                not minhas and associacao.credencial_com_correspondencia(identidade)
            ),
            **_mensagens(request),
        },
    )


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
    registro = identidade_do_candidato.identidade_autenticada(request)
    aqui = reverse("portal:inscrever", args=[edital_id, profile_id])
    if registro is None:
        return redirect(f"{reverse('portal:acesso')}?destino={aqui}")
    if nucleo_da_identidade.falta_o_nucleo(registro):
        # Nome e CPF são pedidos aqui, e só aqui: quem veio olhar a vitrine não precisa entregar
        # dado pessoal, e quem veio da `009` nunca chega a ver esta tela (FR-005).
        request.session[CHAVE_DO_DESTINO] = aqui
        return redirect(reverse("portal:meus-dados"))
    identidade = identidade_do_candidato.contrato_de(registro)
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
    if registro.status == Inscricao.Status.SUBMETIDA:
        # Enviada não se edita (FR-075). O que esta tela passa a fazer é o que a `010` prometeu:
        # mostrar exatamente o que o sistema recebeu.
        return _conferencia(request, registro, versao)
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
                    # Levada adiante para que confirmar o descarte devolva a pessoa para onde ela
                    # estava indo: guardar a escolha volta à tela da inscrição; avançar vai à
                    # revisão. Perder isto na confirmação mandaria todo mundo para a revisão.
                    "acao": request.POST.get("acao", ""),
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
                if request.POST.get("acao") == "guardar":
                    # A escolha da modalidade era guardada só ao avançar, e a lista de documentos
                    # só era recalculada ali. Quem escolhia a modalidade reservada continuava
                    # vendo dois documentos e o aviso verde de "todos enviados" — e descobria o
                    # terceiro na revisão, quando já se considerava pronta; quem saía e voltava
                    # reencontrava o campo em branco. Guardar na hora e recarregar resolve as duas
                    # coisas, e o redirecionamento evita que atualizar a página reenvie o POST.
                    _avisar(request, "Escolha guardada. A lista de documentos foi atualizada.")
                    return redirect(reverse("portal:inscricao", args=[registro.id]))
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
            **_mensagens(request),
        },
    )


def _conferencia(request, registro, versao):
    """`Minha inscrição` — o que o sistema recebeu, sem redigitar e sem reenviar nada (FR-067).

    **Lida da versão aceita, e não da vigente.** O ato aconteceu sob uma versão; ler a de hoje
    faria o Perfil e a modalidade conferidos mudarem depois de uma Retificação, e uma conferência
    que se reescreve não confere coisa alguma — é a mesma razão pela qual o comprovante já lê a
    aceita.

    **Reusa `_dados_do_comprovante`.** A página de conferência e o comprovante são duas
    apresentações do mesmo ato; montá-los de fontes diferentes faria os dois divergirem na primeira
    mudança, e o candidato teria uma tela e um papel que não dizem a mesma coisa. O que esta tela
    acrescenta é o acesso ao arquivo, que o comprovante não oferece.
    """
    aceita = registro.versao_aceita or versao
    conteudo = aceita.content
    dados = _dados_do_comprovante(request, registro, conteudo, aceita)
    documentos = [
        {
            "requisito": linha["nome"],
            "requisito_id": linha["id"],
            "arquivo": linha["enviado"].nome_original,
            "tamanho": linha["tamanho"],
            "quando": linha["enviado"].uploaded_at,
            "resumo": linha["enviado"].content_hash,
        }
        for linha in _documentos(conteudo, registro)["linhas"]
        if linha["enviado"]
    ]
    return render(
        request,
        "portal/inscricao_enviada.html",
        {
            "inscricao": registro,
            "selecao": _selecao(aceita),
            "campos": dados["campos"],
            "documentos": documentos,
            "codigo_de_verificacao": dados["codigo_de_verificacao"],
        },
    )


# ---------------------------------------------------------------------------
# Acompanhamento (010). Duas linhas de informação que não se confundem: o que aconteceu **com a
# pessoa** e o que está marcado **para o processo** (FR-076).
# ---------------------------------------------------------------------------


def _fatos_da_participacao(registro):
    """O que aconteceu com **esta** inscrição — e só o que aconteceu (FR-077).

    Hoje há um fato, e é o envio. Resultado de etapa, deferimento e convocação são de features que
    ainda não existem, e a `010` não os inventa: uma linha que diz "sua análise foi concluída"
    porque o Cronograma chegou à data final da Etapa é uma afirmação sobre a pessoa que ninguém
    fez. É o erro que a `FR-077` nomeia, e a forma desta função é o que o impede — ela lê a
    Inscrição, e não o calendário.
    """
    fatos = []
    if registro.submitted_at:
        fatos.append({"rotulo": "Inscrição enviada", "quando": registro.submitted_at})
    return fatos


def _cronograma(conteudo, agora):
    """Os Eventos do processo, na ordem publicada, com a situação **do evento**.

    Concluído, em curso ou por vir descrevem o Evento — nunca a pessoa. É a mesma distinção da
    `FR-076`, dita em dado: nada aqui sabe quem está lendo.
    """
    eventos = []
    for evento in sorted(
        conteudo.get("schedule") or [], key=lambda item: item.get("order") or 0
    ):
        inicio = parse_datetime(evento.get("startAt") or "")
        fim = parse_datetime(evento.get("endAt") or "") if evento.get("endAt") else None
        if fim is not None and agora > fim:
            situacao = "concluido"
        elif inicio is not None and agora < inicio:
            situacao = "futuro"
        else:
            situacao = "em_curso"
        eventos.append(
            {
                "nome": evento.get("description") or evento.get("type") or "",
                "inicio": inicio,
                "fim": fim,
                "situacao": situacao,
            }
        )
    return eventos


@require_http_methods(["GET"])
@resposta_privada
def acompanhamento(request, inscricao_id):
    """O que já aconteceu, e o que vem agora — sem inventar o que ninguém disse.

    O Cronograma vem da versão **vigente**, porque ele é o calendário de hoje: uma data remarcada
    por Retificação precisa aparecer remarcada. Os dados da inscrição continuam vindo da versão
    **aceita**, e é justamente por lerem versões diferentes que o aviso da `FR-078` existe.
    """
    registro, _identidade, versao = _inscricao_do_titular(request, inscricao_id)
    if registro.status != Inscricao.Status.SUBMETIDA:
        return redirect(reverse("portal:inscricao", args=[registro.id]))
    return render(
        request,
        "portal/acompanhamento.html",
        {
            "inscricao": registro,
            "selecao": _selecao(versao),
            "fatos": _fatos_da_participacao(registro),
            "cronograma": _cronograma(versao.content, timezone.now()),
            # A versão aceita deixou de ser a vigente: o Edital mudou depois do envio. O aviso
            # informa; ele **não** altera a versão aceita nem reabre coisa alguma (FR-079).
            "retificado": registro.versao_aceita_id != versao.pk,
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
    return next(
        (
            perfil
            for perfil in conteudo.get("profiles") or []
            if str(perfil.get("id")) == str(profile_id)
        ),
        None,
    ) or {}


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
    """O candidato vê o que enviou — mediado, e recusado a qualquer outra pessoa.

    `?baixar=1` entrega o mesmo arquivo como anexo. É uma decisão de apresentação, e não de
    conteúdo: os bytes são os mesmos, e nenhuma das duas formas altera a inscrição (FR-070).
    """
    registro, _, _ = _inscricao_do_titular(request, inscricao_id)
    return entregar_ao_titular(
        inscricao=registro,
        identidade=identidade_do_candidato.identidade_da_sessao(request),
        requirement_id=requirement_id,
        anexo=bool(request.GET.get("baixar")),
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
                _confirmar_por_email(request, registro)
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


def _confirmar_por_email(request, registro):
    """O recibo do envio, na caixa de quem enviou — depois de a inscrição estar gravada.

    Chamado aqui, e não dentro de `enviar_inscricao`: o ato é do domínio, a mensagem é do canal, e
    amarrar um ao outro faria uma falha de SMTP desfazer uma inscrição válida (ver `mensagem.py`).

    Lê a **versão aceita**, como o comprovante: a mensagem e o papel precisam dizer a mesma coisa,
    e a vigente pode já ter mudado por Retificação no instante seguinte.
    """
    aceita = registro.versao_aceita
    if aceita is None:
        return
    dados = _dados_do_comprovante(request, registro, aceita.content, aceita)
    campos = dict(dados["campos"])
    enviar_comprovante(
        para=registro.email,
        dados={
            "protocolo": dados["protocolo"],
            "verificacao": dados["codigo_de_verificacao"],
            "endereco": dados["endereco"],
            # Sem CPF e sem telefone: não ajudam quem lê, e viajam com a mensagem encaminhada.
            "selecao": f"{campos['Processo Seletivo']}\nEdital {campos['Edital']}",
            "perfil": campos["Perfil de Vaga"],
            "modalidade": campos["Concorrência"],
            "quando": campos["Enviada em"],
            "documentos": dados["documentos"],
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
                (
                    f"vigente desde {comprovante_pdf.instante(aceita.valid_from)}"
                    if aceita
                    else ""
                ),
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
