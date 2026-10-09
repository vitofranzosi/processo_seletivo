"""As telas dos avisos complementares aos candidatos (066, contracts/telas.md).

**Módulo próprio, e não `views.py`**, que já passa de oito mil linhas. O custo da separação está
pago em `tests/test_gramatica_das_portas.py`: o inventário de negativas varre também este módulo.
Nenhuma view daqui levanta `Http404`: as recusas são `DomainError`, que o middleware de recusas
traduz em página com o mesmo status — e o 404 do escopo alheio é o `not_found` de sempre.

**POST-redirect-GET, e nenhum htmx** (`R-014`). A prévia é um GET que não grava nada; atualizá-la é
um POST que também não grava; só o botão "Enviar a N pessoas" confirma. O htmx não troca resposta
4xx, e nada aqui precisa de fragmento.
"""

from uuid import UUID, uuid4

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.avisos.application import destinatarios, previa
from processo_seletivo.avisos.application import selectors as avisos_selectors
from processo_seletivo.avisos.application.comando import (
    base_do_aviso,
    envio_habilitado,
    exigir_base,
    nao_encontrado,
    pode_consultar,
)
from processo_seletivo.avisos.application.confirmar import (
    confirmar_aviso_da_chamada,
    confirmar_aviso_do_resultado,
)
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.mensagem import RODAPE
from processo_seletivo.avisos.domain.variaveis import SIGNIFICADO, VARIAVEIS
from processo_seletivo.avisos.models import ModeloDeAviso
from processo_seletivo.interface import identidade
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada


def _identificador(valor):
    try:
        return UUID(str(valor)) if valor else None
    except ValueError:
        raise nao_encontrado() from None


def _edital_do_ator(ator, edital_id):
    from processo_seletivo.processos.models import Edital

    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise nao_encontrado()
    return edital


def _enderecos(request, edital, publicacoes=()):
    """Os links absolutos que o texto congela na confirmação (`R-007`, `R-008`)."""
    return {
        "pagina": request.build_absolute_uri(reverse("portal:selecao", args=[edital.id])),
        "area": request.build_absolute_uri(reverse("portal:inscricoes")),
        "publicacao": {
            str(p.id): request.build_absolute_uri(reverse("portal:resultado", args=[p.id]))
            for p in publicacoes
        },
    }


def _modelos_ativos(ator):
    return list(
        ModeloDeAviso.objects.filter(institution_scope=ator.institution_scope, ativo=True).order_by(
            "nome"
        )
    )


def _texto_inicial(ator, modelos, modelo_id):
    """Assunto e corpo do modelo escolhido; sem escolha, o primeiro modelo ativo, ou vazio."""
    escolhido = next((m for m in modelos if str(m.id) == str(modelo_id or "")), None)
    if escolhido is None and not modelo_id and modelos:
        escolhido = modelos[0]
    if escolhido is None:
        return None, "", ""
    return escolhido, escolhido.assunto, escolhido.corpo


def _variaveis_da_origem(origem, publicacoes_citadas):
    """A lista ao lado do editor (`UX-176`): só as que têm valor neste aviso."""
    return [
        {"nome": nome, "significado": SIGNIFICADO[nome]}
        for nome, origens in VARIAVEIS.items()
        if origem in origens and (nome != "link_da_publicacao" or publicacoes_citadas == 1)
    ]


def _rodape_visivel(origem):
    """O rodapé como aparece no editor: fixo, com os marcadores do sistema por extenso."""
    from processo_seletivo.avisos.domain.mensagem import FRASE_DA_CHAMADA

    return RODAPE.format(
        destino_oficial="[endereço da publicação oficial]",
        edital="[Edital]",
        frase_da_chamada=FRASE_DA_CHAMADA if origem == nomes.CHAMADA else "",
        atendimento=getattr(settings, "PORTAL_ATENDIMENTO", "") or "a comissão do certame",
    )


def _renderizar_previa(request, contexto, *, status=200):
    return marcar_como_privada(
        render(request, "interface/aviso_previa.html", contexto, status=status)
    )


def _contexto_da_previa(request, ator, universo, *, motivo, acao, extra):
    """O que a prévia precisa, para as duas origens — o texto vem do POST ou do modelo."""
    modelos = _modelos_ativos(ator)
    modelo_id = (
        request.POST.get("modelo") if request.method == "POST" else request.GET.get("modelo")
    )
    if request.method == "POST":
        modelo = next((m for m in modelos if str(m.id) == (modelo_id or "")), None)
        assunto = request.POST.get("assunto", "")
        corpo = request.POST.get("corpo", "")
    else:
        modelo, assunto, corpo = _texto_inicial(ator, modelos, modelo_id)
    try:
        exemplo = int(request.POST.get("exemplo") or 0)
    except ValueError:
        exemplo = 0
    enderecos = _enderecos(request, universo.edital, universo.publicacoes)
    composta = previa.compor(
        universo,
        assunto=assunto,
        corpo=corpo,
        enderecos=enderecos,
        exemplo=exemplo,
        motivo=motivo,
    )
    return {
        "processo": universo.edital.processo,
        "edital": universo.edital,
        "universo": universo,
        "previa": composta,
        "contagens": composta["contagens"],
        "modelos": modelos,
        "modelo": modelo,
        "assunto": assunto,
        "corpo": corpo,
        "variaveis": _variaveis_da_origem(universo.origem, len(universo.publicacoes)),
        "rodape": _rodape_visivel(universo.origem),
        "chave": uuid4().hex,
        "habilitado": envio_habilitado(),
        "reenvio": motivo == nomes.REENVIO_JUSTIFICADO,
        "justificativa": request.POST.get("justificativa", ""),
        "acao": acao,
        "proximo_exemplo": composta["indice_do_exemplo"] + 1,
        **extra,
    }


# --- O aviso de resultado (US1, US2) ---------------------------------------------------------


@require_http_methods(["GET", "POST"])
def aviso_do_resultado(request, edital_id, marco_id):
    """A prévia e a confirmação do aviso de resultado (contracts/telas.md)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = _edital_do_ator(ator, edital_id)
    exigir_base(ator, edital.processo, origem=nomes.RESULTADO)
    dados = request.POST if request.method == "POST" else request.GET
    pendentes = destinatarios.naturezas_pendentes(edital=edital, marco_id=marco_id)
    natureza = dados.get("natureza") or (pendentes[0] if pendentes else nomes.PRELIMINAR)
    reenvio = dados.get("reenvio") == "1"
    universo = destinatarios.universo_do_resultado(
        edital=edital, marco_id=marco_id, natureza=natureza, reenvio=reenvio
    )
    motivo = nomes.REENVIO_JUSTIFICADO if reenvio else nomes.PRIMEIRO_AVISO
    acao = reverse("interface:aviso-do-resultado", args=[edital.id, marco_id])
    extra = {
        "marco_id": marco_id,
        "natureza": natureza,
        "naturezas_pendentes": pendentes,
        "voltar": reverse("interface:avisos-do-edital", args=[edital.id]),
    }
    if request.method == "POST" and request.POST.get("acao") == "confirmar":
        try:
            declarado = confirmar_aviso_do_resultado(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                marco_id=marco_id,
                natureza=natureza,
                assunto=request.POST.get("assunto", ""),
                corpo=request.POST.get("corpo", ""),
                assinatura=request.POST.get("assinatura", ""),
                enderecos=_enderecos(request, edital, universo.publicacoes),
                idempotency_key=request.POST.get("chave") or uuid4().hex,
                correlation_id=f"interface-aviso-{edital.id}",
                modelo_id=_identificador(request.POST.get("modelo")),
                justificativa=request.POST.get("justificativa", ""),
            )
        except DomainError as erro:
            if erro.status == 404:
                raise
            contexto = _contexto_da_previa(
                request, ator, universo, motivo=motivo, acao=acao, extra=extra
            )
            contexto["erro"] = erro
            return _renderizar_previa(request, contexto, status=erro.status)
        _depois_de_confirmar(request, ator, declarado)
        return redirect(reverse("interface:aviso", args=[declarado["aviso"]]))
    contexto = _contexto_da_previa(request, ator, universo, motivo=motivo, acao=acao, extra=extra)
    return _renderizar_previa(request, contexto)


def _depois_de_confirmar(request, ator, declarado):
    """O aviso foi gravado; "Salvar como novo modelo" é o passo opcional depois (`FR-1261`)."""
    request.session["aviso_confirmado"] = declarado["destinatarios"]
    if request.POST.get("salvar_como_modelo") != "1":
        return
    from processo_seletivo.avisos.application.modelos import salvar_como_novo_modelo

    try:
        salvar_como_novo_modelo(
            actor=ator,
            nome=request.POST.get("nome_do_modelo", ""),
            assunto=request.POST.get("assunto", ""),
            corpo=request.POST.get("corpo", ""),
        )
        request.session["modelo_salvo"] = request.POST.get("nome_do_modelo", "")
    except DomainError as erro:
        request.session["modelo_nao_salvo"] = erro.detail


# --- A chamada comunicada por publicação (US3) -----------------------------------------------


@require_http_methods(["GET", "POST"])
def aviso_da_chamada(request, edital_id, marco_id):
    """A prévia e a confirmação do aviso de uma chamada por publicação (`FR-1251`, `UX-178`)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = _edital_do_ator(ator, edital_id)
    exigir_base(ator, edital.processo, origem=nomes.CHAMADA)
    dados = request.POST if request.method == "POST" else request.GET
    lista_id = _identificador(dados.get("lista"))
    comunicacao_id = _identificador(dados.get("comunicacao"))
    if comunicacao_id is None:
        raise nao_encontrado()
    universo = destinatarios.universo_da_chamada(
        edital=edital,
        marco_id=marco_id,
        lista_id=lista_id,
        comunicacao_id=comunicacao_id,
        agora=timezone.now(),
    )
    motivo = nomes.REENVIO_JUSTIFICADO if universo.ja_avisado else nomes.PRIMEIRO_AVISO
    acao = reverse("interface:aviso-da-chamada", args=[edital.id, marco_id])
    extra = {
        "marco_id": marco_id,
        "lista_id": lista_id,
        "comunicacao_id": comunicacao_id,
        "voltar": reverse("interface:convocacao", args=[edital.id, marco_id])
        + (f"?lista={lista_id}" if lista_id else ""),
    }
    if request.method == "POST" and request.POST.get("acao") == "confirmar":
        try:
            declarado = confirmar_aviso_da_chamada(
                actor=ator,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                marco_id=marco_id,
                lista_id=lista_id,
                comunicacao_id=comunicacao_id,
                assunto=request.POST.get("assunto", ""),
                corpo=request.POST.get("corpo", ""),
                assinatura=request.POST.get("assinatura", ""),
                enderecos=_enderecos(request, edital),
                idempotency_key=request.POST.get("chave") or uuid4().hex,
                correlation_id=f"interface-aviso-chamada-{edital.id}",
                modelo_id=_identificador(request.POST.get("modelo")),
                justificativa=request.POST.get("justificativa", ""),
            )
        except DomainError as erro:
            if erro.status == 404:
                raise
            contexto = _contexto_da_previa(
                request, ator, universo, motivo=motivo, acao=acao, extra=extra
            )
            contexto["erro"] = erro
            return _renderizar_previa(request, contexto, status=erro.status)
        _depois_de_confirmar(request, ator, declarado)
        return redirect(reverse("interface:aviso", args=[declarado["aviso"]]))
    contexto = _contexto_da_previa(request, ator, universo, motivo=motivo, acao=acao, extra=extra)
    return _renderizar_previa(request, contexto)


# --- O histórico (US1, US5) --------------------------------------------------------------------


def _aviso_para_ler(request, aviso_id):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None
    aviso = avisos_selectors.aviso_do_ator(ator, aviso_id)
    processo = aviso.edital.processo
    if not (
        pode_consultar(ator, processo)
        or base_do_aviso(ator, processo, origem=aviso.origem) is not None
    ):
        raise nao_encontrado()
    return ator, aviso


def aviso(request, aviso_id):
    """O histórico do aviso: texto enviado, ato, estados e alerta (contracts/telas.md)."""
    ator, aviso_ = _aviso_para_ler(request, aviso_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    historico = avisos_selectors.historico(aviso_, agora=timezone.now())
    pode_agir = base_do_aviso(ator, aviso_.edital.processo, origem=aviso_.origem) is not None
    return marcar_como_privada(
        render(
            request,
            "interface/aviso.html",
            {
                **historico,
                "processo": aviso_.edital.processo,
                "edital": aviso_.edital,
                "pode_agir": pode_agir,
                "habilitado": envio_habilitado(),
                "confirmado": request.session.pop("aviso_confirmado", None),
                "modelo_salvo": request.session.pop("modelo_salvo", None),
                "modelo_nao_salvo": request.session.pop("modelo_nao_salvo", None),
                "interrompido_agora": request.session.pop("aviso_interrompido", None),
                "alerta_minutos": settings.AVISOS_ALERTA_DE_PENDENTE_MIN,
            },
        )
    )


def avisos_do_edital(request, edital_id):
    """Os avisos do Edital e, por marco com resultado publicado, o que ainda pode ser avisado."""
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    edital = _edital_do_ator(ator, edital_id)
    processo = edital.processo
    if not pode_consultar(ator, processo):
        raise nao_encontrado()
    pode_avisar = base_do_aviso(ator, processo, origem=nomes.RESULTADO) is not None
    marcos = []
    vistos = set()
    for publicacao in PublicacaoResultado.objects.filter(
        edital=edital, sucessoras__isnull=True
    ).order_by("publicado_em"):
        if publicacao.marco_id in vistos:
            continue
        vistos.add(publicacao.marco_id)
        marcos.append(
            {
                "marco_id": publicacao.marco_id,
                "nome": destinatarios.cabecalho_de(publicacao).get("marco", ""),
                "pendentes": destinatarios.naturezas_pendentes(
                    edital=edital, marco_id=publicacao.marco_id
                ),
            }
        )
    return marcar_como_privada(
        render(
            request,
            "interface/avisos_do_edital.html",
            {
                "processo": processo,
                "edital": edital,
                "avisos": avisos_selectors.avisos_do_edital(edital),
                "marcos": marcos,
                "pode_avisar": pode_avisar,
                "habilitado": envio_habilitado(),
                "natureza_rotulo": previa.NATUREZA_POR_EXTENSO,
            },
        )
    )


def contexto_do_marco(ator, edital, marco_id):
    """O que `publicacoes_do_marco.html` precisa para oferecer o aviso (`UX-174`, `UX-175`)."""
    pode_avisar = base_do_aviso(ator, edital.processo, origem=nomes.RESULTADO) is not None
    vigentes = [
        p
        for natureza in nomes.NATUREZAS
        for p in destinatarios.vigentes_da_natureza(
            edital=edital, marco_id=marco_id, natureza=natureza
        )
    ]
    ultimo = avisos_selectors.ultimo_aviso_das_publicacoes(vigentes) if vigentes else None
    return {
        "pode_avisar": pode_avisar,
        "habilitado": envio_habilitado(),
        "pendentes": destinatarios.naturezas_pendentes(edital=edital, marco_id=marco_id)
        if pode_avisar
        else [],
        "natureza_rotulo": previa.NATUREZA_POR_EXTENSO,
        "ultimo": avisos_selectors.linha_de_estado(ultimo, agora=timezone.now()),
    }


# --- Interromper e reenviar (US5) --------------------------------------------------------------


@require_http_methods(["GET", "POST"])
def aviso_interromper(request, aviso_id):
    """A confirmação da interrupção, que diz quantas já saíram e que elas não voltam (`UX-177`)."""
    from processo_seletivo.avisos.application.interromper import interromper

    ator, aviso_ = _aviso_para_ler(request, aviso_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    exigir_base(ator, aviso_.edital.processo, origem=aviso_.origem)
    erro = None
    if request.method == "POST":
        try:
            interromper(
                actor=ator,
                aviso_id=aviso_.id,
                motivo=request.POST.get("motivo", ""),
                idempotency_key=request.POST.get("chave") or uuid4().hex,
                correlation_id=f"interface-aviso-interromper-{aviso_.id}",
            )
        except DomainError as recusa:
            if recusa.status == 404:
                raise
            erro = recusa
        else:
            request.session["aviso_interrompido"] = True
            return redirect(reverse("interface:aviso", args=[aviso_.id]))
    historico = avisos_selectors.historico(aviso_, agora=timezone.now())
    return marcar_como_privada(
        render(
            request,
            "interface/aviso_interromper.html",
            {
                **historico,
                "processo": aviso_.edital.processo,
                "edital": aviso_.edital,
                "chave": uuid4().hex,
                "motivo": request.POST.get("motivo", ""),
                "erro": erro,
            },
            status=erro.status if erro else 200,
        )
    )


@require_http_methods(["GET", "POST"])
def aviso_reenviar(request, aviso_id):
    """A prévia do aviso filho: falhas e expiradas, ou — com justificativa — indeterminadas e
    interrompidas (`R-011`, `FR-1264`)."""
    from processo_seletivo.avisos.application.confirmar import (
        confirmar_reenvio,
        recusar_falhas_ja_reenviadas,
    )

    ator, anterior = _aviso_para_ler(request, aviso_id)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    exigir_base(ator, anterior.edital.processo, origem=anterior.origem)
    dados = request.POST if request.method == "POST" else request.GET
    motivo = dados.get("motivo") or nomes.REENVIO_DE_FALHAS
    if motivo not in nomes.ALCANCE_DO_REENVIO:
        raise nao_encontrado()
    if motivo == nomes.REENVIO_DE_FALHAS:
        # Antes da prévia, e não só na confirmação: a tela não oferece o que vai recusar.
        recusar_falhas_ja_reenviadas(anterior)
    universo = destinatarios.universo_do_reenvio(anterior, motivo=motivo, agora=timezone.now())
    acao = reverse("interface:aviso-reenviar", args=[anterior.id])
    extra = {
        "anterior": anterior,
        "motivo_do_reenvio": motivo,
        "voltar": reverse("interface:aviso", args=[anterior.id]),
    }
    if request.method == "POST" and request.POST.get("acao") == "confirmar":
        try:
            declarado = confirmar_reenvio(
                actor=ator,
                aviso_id=anterior.id,
                motivo=motivo,
                assinatura=request.POST.get("assinatura", ""),
                enderecos=_enderecos(request, anterior.edital, universo.publicacoes),
                idempotency_key=request.POST.get("chave") or uuid4().hex,
                correlation_id=f"interface-aviso-reenvio-{anterior.id}",
                assunto=request.POST.get("assunto", ""),
                corpo=request.POST.get("corpo", ""),
                modelo_id=_identificador(request.POST.get("modelo")),
                justificativa=request.POST.get("justificativa", ""),
            )
        except DomainError as erro:
            if erro.status == 404:
                raise
            contexto = _contexto_do_reenvio(request, ator, universo, motivo, acao, extra)
            contexto["erro"] = erro
            return _renderizar_previa(request, contexto, status=erro.status)
        request.session["aviso_confirmado"] = declarado["destinatarios"]
        return redirect(reverse("interface:aviso", args=[declarado["aviso"]]))
    return _renderizar_previa(
        request, _contexto_do_reenvio(request, ator, universo, motivo, acao, extra)
    )


def _contexto_do_reenvio(request, ator, universo, motivo, acao, extra):
    """No reenvio de falhas o texto é o do anterior, e não se edita; no justificado, sim."""
    contexto = _contexto_da_previa(request, ator, universo, motivo=motivo, acao=acao, extra=extra)
    if motivo == nomes.REENVIO_DE_FALHAS:
        anterior = extra["anterior"]
        contexto["texto_fixo"] = {"assunto": anterior.assunto, "corpo": anterior.corpo}
        contexto["reenvio"] = False
        contexto["previa"]["erro"] = None
    else:
        contexto["reenvio"] = True
    return contexto


# --- Os modelos da unidade (US4) ----------------------------------------------------------------


def _ator_que_gere(request):
    from processo_seletivo.avisos.application.modelos import exigir_quem_gere

    ator = identidade.ator_da_sessao(request)
    if ator is not None:
        exigir_quem_gere(ator)
    return ator


def modelos_de_aviso(request):
    """Os modelos da unidade, ativos e inativos (`FR-1260`)."""
    from processo_seletivo.avisos.application.modelos import modelos_da_unidade

    ator = _ator_que_gere(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    return marcar_como_privada(
        render(
            request,
            "interface/modelos_de_aviso.html",
            {
                "modelos": modelos_da_unidade(ator),
                "salvo": request.session.pop("modelo_de_aviso_salvo", None),
            },
        )
    )


@require_http_methods(["GET", "POST"])
def modelo_de_aviso(request, modelo_id=None):
    """Criar (sem `modelo_id`) ou editar um modelo, com as variáveis ao lado (`UX-176`)."""
    from processo_seletivo.avisos.application import modelos as modelos_app

    ator = _ator_que_gere(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    modelo = modelos_app.modelo_da_unidade(ator, modelo_id) if modelo_id else None
    erro = None
    if request.method == "POST":
        dados = {
            "nome": request.POST.get("nome", ""),
            "assunto": request.POST.get("assunto", ""),
            "corpo": request.POST.get("corpo", ""),
        }
        try:
            if modelo is None:
                modelo = modelos_app.criar(actor=ator, **dados)
            else:
                modelos_app.editar(actor=ator, modelo_id=modelo.id, **dados)
        except DomainError as recusa:
            if recusa.status == 404:
                raise
            erro = recusa
        else:
            request.session["modelo_de_aviso_salvo"] = dados["nome"]
            return redirect(reverse("interface:modelos-de-aviso"))
    else:
        dados = {
            "nome": modelo.nome if modelo else "",
            "assunto": modelo.assunto if modelo else "",
            "corpo": modelo.corpo if modelo else "",
        }
    return marcar_como_privada(
        render(
            request,
            "interface/modelo_de_aviso.html",
            {
                "modelo": modelo,
                **dados,
                "erro": erro,
                "variaveis": [
                    {"nome": nome, "significado": SIGNIFICADO[nome]} for nome in VARIAVEIS
                ],
                "rodape": _rodape_visivel(nomes.RESULTADO),
            },
            status=erro.status if erro else 200,
        )
    )


@require_http_methods(["POST"])
def modelo_de_aviso_situacao(request, modelo_id):
    """Inativar ou reativar: o modelo sai do seletor, e nada se apaga (`FR-1260`)."""
    from processo_seletivo.avisos.application.modelos import mudar_situacao

    ator = _ator_que_gere(request)
    if ator is None:
        return redirect(reverse("interface:identificar"))
    modelo = mudar_situacao(actor=ator, modelo_id=modelo_id, ativo=request.POST.get("ativo") == "1")
    request.session["modelo_de_aviso_salvo"] = modelo.nome
    return redirect(reverse("interface:modelos-de-aviso"))


def chamadas_publicadas(ator, edital, marco_id, lista_id):
    """As chamadas do recorte comunicadas por publicação, uma por referência (`UX-174`, `D-003`).

    **Uma linha por referência, e não um botão por convocação**: o aviso é sobre a publicação, e
    quarenta chamadas de um mesmo gesto são uma publicação só. Perfil que convoca por mensagem
    individual não tem comunicação por publicação, e a lista sai vazia (`FR-1245`).
    """
    from processo_seletivo.avisos.models import Aviso
    from processo_seletivo.convocacao.models import ComunicacaoEmitida
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO

    if base_do_aviso(ator, edital.processo, origem=nomes.CHAMADA) is None:
        return {"habilitado": envio_habilitado(), "itens": []}
    por_referencia = {}
    for referencia, comunicacao_id, convocacao_id in (
        ComunicacaoEmitida.objects.filter(
            convocacao__edital=edital,
            convocacao__marco_id=marco_id,
            convocacao__lista_id=lista_id,
            forma=FORMA_POR_PUBLICACAO,
            resultado="ENVIADA",
        )
        .order_by("enviado_em", "id")
        .values_list("referencia_da_publicacao", "id", "convocacao_id")
    ):
        item = por_referencia.setdefault(
            referencia,
            {"referencia": referencia, "comunicacao": comunicacao_id, "convocacoes": set()},
        )
        item["convocacoes"].add(convocacao_id)
    avisadas = set(
        Aviso.objects.filter(
            edital=edital,
            origem=nomes.CHAMADA,
            marco_id=marco_id,
            lista_id=lista_id,
            referencia_da_publicacao__in=list(por_referencia),
        ).values_list("referencia_da_publicacao", flat=True)
    )
    return {
        "habilitado": envio_habilitado(),
        "itens": [
            {**item, "quantas": len(item["convocacoes"]), "avisada": item["referencia"] in avisadas}
            for item in por_referencia.values()
        ],
    }
