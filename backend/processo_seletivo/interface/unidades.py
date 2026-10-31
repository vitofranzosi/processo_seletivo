"""As telas do registro de Unidades: lista, ficha, cadastrar, editar, desativar e reativar (110).

**No molde da gestão de acessos da `107`** (`D-011`): o ator do nível institucional com a permissão,
depois a recusa da sessão de demonstração, as duas antes de ler o registro; a conferência que não
grava, e a confirmação que chama o caso de uso. A permissão é conferida de novo na aplicação
(`unidades/application/registro.py`): a tela é a segunda barreira, e não a primeira (FR-3309).

**A prévia é texto, pelas funções do compositor** (`D-010`). As linhas do órgão saem de
`linhas_do_orgao` e a sigla no anúncio de `anuncio_em_caixa_alta` — as mesmas que imprimem o
documento oficial —, e a largura de cada linha é medida pela métrica do documento, para avisar o que
o HTML não mostra: a linha que no documento quebraria em duas.
"""

from types import SimpleNamespace

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import identidade
from processo_seletivo.interface.trilha_da_unidade import CAMPOS_LEGIVEIS, linhas
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import registro
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.domain.registro import ATENDIMENTO_MAXIMO, LIMITES


def _ator(request):
    """O Administrador institucional na entrada institucional, ou a recusa que diz o que falta."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None
    registro.exigir_permissao(ator)
    if identidade.resolucao_institucional(request).pessoa is None:
        raise DomainError(
            "so_entrada_institucional",
            "A administração de unidades é da entrada institucional; a demonstração não a alcança.",
            403,
        )
    return ator


def _correlacao(request):
    return getattr(request, "correlation_id", "")


def _campos_do_formulario(request):
    linhas = [
        (request.POST.get(f"cabecalho_{n}") or "").strip()
        for n in (1, 2)
        if (request.POST.get(f"cabecalho_{n}") or "").strip()
    ]
    return {
        "codigo": request.POST.get("codigo", ""),
        "sigla": request.POST.get("sigla", ""),
        "nome": request.POST.get("nome", ""),
        "cabecalho": linhas,
        "local": request.POST.get("local", ""),
        "atendimento": request.POST.get("atendimento", ""),
    }


def _valores_da_unidade(unidade):
    return {
        "codigo": unidade.codigo,
        "sigla": unidade.sigla,
        "nome": unidade.nome,
        "cabecalho": list(unidade.cabecalho),
        "local": unidade.local,
        "atendimento": unidade.atendimento,
    }


def previa(valores):
    """O cabeçalho como o documento oficial o imprime, e o aviso da linha que não cabe (FR-3324)."""
    from processo_seletivo.publicacoes.infrastructure import humano, pdf

    linhas = pdf.linhas_do_orgao(SimpleNamespace(cabecalho=valores["cabecalho"]))
    disponivel = pdf.LARGURA - 2 * pdf.MARGEM
    longas = [
        linha
        for linha in valores["cabecalho"]
        if pdf.METRICA_DO_EDITAL.largura(linha, pdf.CORPO_INSTITUCIONAL, pdf.REGULAR) > disponivel
    ]
    hoje = timezone.localdate()
    exemplo = {"number": "1", "year": hoje.year, "title": f"Processo seletivo — {valores['sigla']}"}
    return {
        "linhas": linhas,
        "anuncio": pdf.anuncio_em_caixa_alta(pdf.anuncio_do_ato(exemplo), valores["sigla"]),
        "fecho": f"{valores['local']}, {humano.data_por_extenso(hoje)}.",
        "longas": longas,
    }


def _formulario(request, *, modo, valores, unidade=None, erro=None, status=200):
    return render(
        request,
        "interface/unidades_formulario.html",
        {
            "modo": modo,
            "unidade": unidade,
            "valores": valores,
            "erro": erro,
            "limites": LIMITES,
            "atendimento_maximo": ATENDIMENTO_MAXIMO,
        },
        status=status,
    )


def _conferencia(
    request,
    *,
    modo,
    valores,
    unidade=None,
    antes=None,
    mudados=(),
    versao="",
    erro=None,
    status=200,
):
    moldura = registro.mudanca_da_moldura(
        codigo=valores["codigo"],
        ativa_depois=unidade.ativa if unidade is not None else True,
        sigla_depois=valores["sigla"],
    )
    return render(
        request,
        "interface/unidades_conferencia.html",
        {
            "modo": modo,
            "unidade": unidade,
            "valores": valores,
            "mudancas": [
                {
                    "rotulo": CAMPOS_LEGIVEIS["Unidade"][campo],
                    "antes": _legivel(antes[campo]),
                    "depois": _legivel(valores[campo]),
                }
                for campo in mudados
            ],
            "versao": versao,
            "previa": previa(valores),
            "moldura": moldura,
            "motivo": request.POST.get("motivo", ""),
            "erro": erro,
        },
        status=status,
    )


def _legivel(valor):
    if isinstance(valor, list):
        return " / ".join(valor) or "—"
    return valor or "—"


def _unidade_ou_404(funcao, *argumentos, **nomeados):
    """O caso de uso de uma unidade da rota; o código que não está registrado é inexistente."""
    try:
        return funcao(*argumentos, **nomeados)
    except DomainError as recusa:
        if recusa.code == nomes.UNIDADE_NAO_REGISTRADA:
            raise Http404 from recusa
        raise


# --- Lista e ficha -----------------------------------------------------------------------------


@require_http_methods(["GET"])
def lista(request):
    """Todas as unidades, ativas e desativadas, por sigla (FR-3314)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    return render(
        request,
        "interface/unidades.html",
        {"unidades": registro.listar(ator), "feito": request.GET.get("feito", "")},
    )


@require_http_methods(["GET"])
def ficha(request, codigo):
    """Os campos, a prévia e o histórico da unidade, mais recente primeiro (FR-3315, `D-009`)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    unidade, _versao, eventos = _unidade_ou_404(registro.ficha, ator, codigo=codigo)
    return render(
        request,
        "interface/unidades_ficha.html",
        {
            "unidade": unidade,
            "previa": previa(_valores_da_unidade(unidade)),
            "historico": linhas(eventos, nome_da_unidade=unidade.nome),
            "feito": request.GET.get("feito", ""),
        },
    )


# --- Cadastrar e editar ------------------------------------------------------------------------


@require_http_methods(["GET", "POST"])
def cadastrar(request):
    """O formulário, a conferência com a prévia e a confirmação (FR-3316, FR-3317, FR-3324)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    acao = request.POST.get("acao", "") if request.method == "POST" else ""
    if acao not in ("conferir", "confirmar"):
        vazio = {campo: "" for campo in ("codigo", "sigla", "nome", "local", "atendimento")}
        return _formulario(request, modo="cadastrar", valores={**vazio, "cabecalho": []})
    campos = _campos_do_formulario(request)
    if acao == "conferir":
        try:
            valores = registro.conferir_registro(ator, campos=campos)
        except DomainError as recusa:
            if recusa.status == 403:
                raise
            return _formulario(
                request, modo="cadastrar", valores=campos, erro=recusa, status=recusa.status
            )
        return _conferencia(request, modo="cadastrar", valores=valores)
    # A confirmação não confere antes: `registrar` confere tudo, e a recusa diz o que voltar a ver.
    try:
        unidade = registro.registrar(
            ator,
            campos=campos,
            motivo=request.POST.get("motivo", ""),
            correlation_id=_correlacao(request),
        )
    except DomainError as recusa:
        if recusa.status == 403:
            raise
        if recusa.code == nomes.MOTIVO_OBRIGATORIO:
            # Só o motivo faltou: os campos passaram, e a conferência volta com eles.
            valores = registro.conferir_registro(ator, campos=campos)
            return _conferencia(
                request, modo="cadastrar", valores=valores, erro=recusa, status=recusa.status
            )
        return _formulario(
            request, modo="cadastrar", valores=campos, erro=recusa, status=recusa.status
        )
    return redirect(f"{reverse('interface:unidade', args=[unidade.codigo])}?feito=cadastrada")


@require_http_methods(["GET", "POST"])
def editar(request, codigo):
    """Como cadastrar, sem o código: o da rota é a unidade (FR-3321, FR-3322, EC-9)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    unidade = _unidade_ou_404(registro.ler_unidade, ator, codigo=codigo)
    acao = request.POST.get("acao", "") if request.method == "POST" else ""
    if acao not in ("conferir", "confirmar"):
        return _formulario(
            request, modo="editar", valores=_valores_da_unidade(unidade), unidade=unidade
        )
    campos = {**_campos_do_formulario(request), "codigo": unidade.codigo}
    try:
        conferencia = registro.conferir_alteracao(ator, codigo=unidade.codigo, campos=campos)
    except DomainError as recusa:
        if recusa.status == 403:
            raise
        return _formulario(
            request,
            modo="editar",
            valores=campos,
            unidade=unidade,
            erro=recusa,
            status=recusa.status,
        )
    valores = {**conferencia["depois"], "codigo": unidade.codigo}
    contexto = {
        "modo": "editar",
        "valores": valores,
        "unidade": unidade,
        "antes": conferencia["antes"],
        "mudados": conferencia["mudados"],
    }
    if acao == "conferir":
        return _conferencia(request, versao=conferencia["versao"], **contexto)
    try:
        registro.alterar(
            ator,
            codigo=unidade.codigo,
            campos=campos,
            versao_conferida=request.POST.get("versao", ""),
            motivo=request.POST.get("motivo", ""),
            correlation_id=_correlacao(request),
        )
    except DomainError as recusa:
        if recusa.status == 403:
            raise
        # A versão que a recusa mostra é a de agora: quem confere de novo vê o que a outra pessoa
        # gravou, e não a versão que já não existe.
        return _conferencia(
            request,
            versao=conferencia["versao"],
            erro=recusa,
            status=recusa.status,
            **contexto,
        )
    return redirect(f"{reverse('interface:unidade', args=[unidade.codigo])}?feito=alterada")


# --- Desativar e reativar ----------------------------------------------------------------------


def _situacao(request, codigo, ato):
    """As consequências e o motivo, e a confirmação (FR-3326 a FR-3328, FR-3330)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    erro, status = None, 200
    if request.method == "POST" and request.POST.get("acao") == "confirmar":
        funcao = registro.desativar if ato == "desativar" else registro.reativar
        try:
            _unidade_ou_404(
                funcao,
                ator,
                codigo=codigo,
                versao_conferida=request.POST.get("versao", ""),
                motivo=request.POST.get("motivo", ""),
                correlation_id=_correlacao(request),
            )
        except DomainError as recusa:
            if recusa.status == 403:
                raise
            erro, status = recusa, recusa.status
        else:
            feito = "desativada" if ato == "desativar" else "reativada"
            return redirect(f"{reverse('interface:unidade', args=[codigo])}?feito={feito}")
    consequencias = _unidade_ou_404(registro.consequencias, ator, codigo=codigo, ato=ato)
    return render(
        request,
        "interface/unidades_situacao.html",
        {
            "ato": ato,
            "unidade": consequencias["unidade"],
            "versao": consequencias["versao"],
            "processos": consequencias["processos_nao_encerrados"],
            "moldura": consequencias["moldura"],
            "motivo": request.POST.get("motivo", ""),
            "erro": erro,
        },
        status=status,
    )


@require_http_methods(["GET", "POST"])
def desativar(request, codigo):
    return _situacao(request, codigo, "desativar")


@require_http_methods(["GET", "POST"])
def reativar(request, codigo):
    return _situacao(request, codigo, "reativar")
