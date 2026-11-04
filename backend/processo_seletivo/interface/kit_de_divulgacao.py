"""As portas do kit de divulgação do Edital: ler a tela e exportar o material (111).

**A porta** (`FR-3402`, contrato em `specs/111-kit-de-divulgacao/contracts/kit.md`):

1. Edital inexistente ou de outra unidade responde "não encontrado" (`033`);
2. quem é da unidade sem `material:gerar` recebe a recusa que diz o que falta;
3. Edital ainda não publicado responde 409, como o relatório do Edital (`099`).

Encerrado e cancelado passam: a tela diz o motivo e, se houve exportação, que ela não deve mais
circular (`FR-3445`).

**Exportar é o que registra, e abrir não** (`FR-3435`). O material sai do sistema numa exportação, e
a trilha precisa dizer quem o levou, sobre qual versão e com qual impressão. A desatualização
compara a ficha de agora com essas exportações (`FR-3439`). Abrir a tela e copiar um texto não
registram (P-5).

**A impressão conferida viaja da tela à exportação** (`FR-3446`, `D-019`). São duas requisições, e
na passagem de uma vigência a pessoa conferiria um Edital e baixaria outro.

**A peça é a mesma composição na prévia e na exportação** (`D-014`). A prévia é um `<img>` que
pede o PNG por GET, com a impressão conferida, e não registra; a exportação é o POST que registra.
O SVG sai só como anexo, com uma política própria que admite só a fonte e a marca embutidas
(`D-021`): a do projeto só se aplica a `text/html`. Com a chave desligada, em host local, sem
material ou com a peça recusada, a prévia e a exportação da peça respondem 404 — o motivo é dito na
tela (contrato).

**Nada aqui toca a publicação** (`FR-3405`): a única escrita é o evento da trilha.
"""

import hashlib

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import (
    identidade,
    kit_escolha,
    kit_familias,
    kit_pacote,
    kit_peca,
    kit_textos,
)
from processo_seletivo.interface.kit_familias import institucional
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import host_local, marcar_como_privada

PERMISSAO = "material:gerar"
OPERACAO = "EXPORTAR_MATERIAL"
BASE = base_de_permissao("gerar o material de divulgação")

#: Os estados em que o kit abre. Antes da publicação não há o que divulgar; encerrado e cancelado
#: abrem para dizer que o material exportado não deve mais circular.
ESTADOS_COM_KIT = frozenset(
    {Edital.Status.PUBLICADO, Edital.Status.ENCERRADO, Edital.Status.CANCELADO}
)
INDISPONIVEL = "O kit de divulgação fica disponível quando o Edital for publicado."
MUDOU = (
    "O Edital mudou desde que você abriu o kit. Abra o kit de novo e confira as informações "
    "antes de exportar."
)

PECA_EM_VALIDACAO = (
    "A peça visual está em validação pela comunicação e não está disponível neste ambiente. Os "
    "textos continuam disponíveis."
)
SEM_RASTERIZADOR = (
    "O rasterizador da peça não está instalado neste ambiente: a peça sai só em SVG. Os textos "
    "continuam disponíveis."
)
MANCHETE_INVALIDA = "A manchete escolhida não está entre as oferecidas. Abra o kit de novo."

TEXTOS = {
    "md": ("text/markdown; charset=utf-8", "md"),
    "txt": ("text/plain; charset=utf-8", "txt"),
}
PECAS = {
    "png": ("image/png", "png"),
    "svg": ("image/svg+xml", "svg"),
}
#: O pacote (incremento C): sai também sem a peça, e diz por quê (EC-21).
PACOTE = {"zip": ("application/zip", "zip")}
FORMATOS = {**TEXTOS, **PECAS, **PACOTE}
#: A política do anexo SVG (FR-3442, `D-014`, `D-021`): nada de fora, nenhum script; só o estilo
#: que declara a fonte, a fonte em `data:` e a marca em `data:`.
POLITICA_DO_SVG = "default-src 'none'; style-src 'unsafe-inline'; font-src data:; img-src data:"


def _edital_do_kit(request, edital_id):
    """Ator e Edital, na ordem da porta. `(None, None)` pede identificação."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    require_authorization_base(ator.can(PERMISSAO), bases=[BASE])
    if edital.status not in ESTADOS_COM_KIT:
        raise DomainError("kit_indisponivel", INDISPONIVEL, 409)
    return ator, edital


def _base_url(request):
    """O endereço público da requisição, ou nenhum em host local (`FR-3447`, `D-020`)."""
    if host_local(request):
        return None
    return request.build_absolute_uri("/").rstrip("/")


def _indice_da_manchete(dados):
    """O índice pedido, ou `None`. Texto que não é índice tem a recusa do índice fora da lista."""
    bruto = dados.get("manchete", "")
    if bruto == "":
        return None
    try:
        return int(bruto)
    except ValueError:
        raise DomainError("kit_manchete_invalida", MANCHETE_INVALIDA, 422) from None


def _motivo_sem_peca(request, *, da_institucional=True):
    """Por que a peça não existe neste acesso, antes de compor: chave desligada ou host local.

    A chave da `111` é da Institucional; as famílias da comunicação têm a liberação por template
    (119, FR-3808), conferida na composição.
    """
    if da_institucional:
        motivo = _motivo_da_institucional()
        if motivo:
            return motivo
    if host_local(request):
        return kit_peca.HOST_LOCAL
    return ""


def _motivo_da_institucional():
    """A Institucional também passa pela liberação (FR-3835): `liberados()` decide.

    A versão 1 com o resumo congelado continua da chave da `111`; qualquer outra versão, ou outro
    resumo, só sai pela configuração nova, que a nomeia — a chave da `111` não a alcança.
    """
    if institucional.POST in kit_familias.liberados():
        return ""
    if kit_familias.institucional_v1(institucional.POST):
        return PECA_EM_VALIDACAO
    return kit_escolha.VERSAO_EM_APROVACAO


#: O que só uma família da comunicação pede. A Institucional não tem banco, variante nem outro
#: formato; um envio que os traz não saiu da tela e é recusado sem gerar (EC-9).
CAMPOS_SO_DAS_FAMILIAS = ("variante", "imagem")


def _conferir_institucional(dados):
    if any((dados.get(campo) or "").strip() for campo in CAMPOS_SO_DAS_FAMILIAS):
        raise kit_escolha.EscolhaInvalida
    if (dados.get("formato_da_peca") or "").strip() not in ("", institucional.POST.formato.chave):
        raise kit_escolha.EscolhaInvalida


def _compor(ficha, indice):
    """A peça, ou `DomainError` 422 para manchete fora da lista."""
    try:
        return kit_peca.compor(ficha, manchete=indice)
    except kit_peca.MancheteInvalida:
        raise DomainError("kit_manchete_invalida", MANCHETE_INVALIDA, 422) from None


#: O nome de cada formato na tela.
NOMES_DOS_FORMATOS = {"post": "Post", "story": "Story", "banner": "Banner do site"}


def _da_familia(dados):
    """O pedido é de uma família da comunicação? A Institucional segue o caminho da `111`."""
    return (dados.get("familia") or "").strip() not in ("", institucional.CHAVE)


def _peca_pedida(ficha, edital, dados, indice):
    """`(peca, escolhida)` do pedido de prévia ou exportação de PNG e SVG.

    Sem família da comunicação, a peça da `111`, como sempre foi. Com ela, a escolha validada
    contra as listas e o template do `formato_da_peca` (`D-012`).
    """
    if not _da_familia(dados):
        _conferir_institucional(dados)
        peca = _compor(ficha, indice)
        return peca, kit_escolha.Escolhida(institucional.FAMILIA, None, None, indice)
    escolhida = kit_escolha.ler(dados, ficha, edital, indice_da_manchete=indice)
    liberados = kit_familias.liberados()
    peca = kit_escolha.compor(
        ficha,
        escolhida,
        (dados.get("formato_da_peca") or "").strip(),
        liberados,
        kit_escolha.manchetes(ficha, escolhida, liberados),
    )
    return peca, escolhida


def _secoes_da_familia(request, ficha, escolhida):
    """Uma prévia por formato da família, com o motivo de cada um que não sai (FR-3830)."""
    motivo = _motivo_sem_peca(request, da_institucional=False) or (
        "" if ficha.tem_material else ficha.motivo
    )
    liberados = kit_familias.liberados()
    lista = () if motivo else kit_escolha.manchetes(ficha, escolhida, liberados)
    formatos, sem_titulo, sem_contato, resumidos = [], [], [], []
    for template in kit_escolha.templates_da_familia(escolhida.familia):
        formato = template.formato
        item = {
            "formato": formato.chave,
            "nome": NOMES_DOS_FORMATOS[formato.chave],
            "largura": formato.largura // 2,
            "altura": formato.altura // 2,
            "peca": None,
            "motivo": motivo,
        }
        if not motivo:
            try:
                peca = kit_escolha.compor(ficha, escolhida, formato.chave, liberados, lista)
            except kit_peca.PecaRecusada as recusa:
                item["motivo"] = recusa.motivo
            else:
                item["peca"] = peca
                if kit_peca.SEM_TITULO_EM.split(":")[0] in " ".join(peca.avisos):
                    sem_titulo.append(item["nome"].lower())
                if kit_peca.SEM_CONTATO_EM.split(":")[0] in " ".join(peca.avisos):
                    sem_contato.append(item["nome"].lower())
                if kit_peca.RESUMO_EM.split(":")[0] in " ".join(peca.avisos):
                    resumidos.append(item["nome"].lower())
        formatos.append(item)
    avisos = []
    if sem_titulo:
        avisos.append(kit_peca.SEM_TITULO_EM.format(formatos=", ".join(sem_titulo)))
    if sem_contato:
        avisos.append(kit_peca.SEM_CONTATO_EM.format(formatos=", ".join(sem_contato)))
    if resumidos:
        avisos.append(kit_peca.RESUMO_EM.format(formatos=", ".join(resumidos)))
    return {
        "formatos": formatos,
        "manchetes": lista,
        "manchete": escolhida.manchete,
        "png": kit_pacote.disponivel(),
        "sem_rasterizador": "" if kit_pacote.disponivel() else SEM_RASTERIZADOR,
        "avisos": avisos,
        # O motivo comum a todos os formatos (host local, sem material): dito uma vez só.
        "motivo": motivo,
    }


def _secao_da_peca(request, ficha, indice):
    """O que a tela mostra da peça: a peça, as manchetes oferecidas e o motivo quando não há."""
    motivo = _motivo_sem_peca(request)
    if motivo or not ficha.tem_material:
        return {"peca": None, "motivo": motivo, "manchetes": ()}
    try:
        peca = _compor(ficha, indice)
    except kit_peca.PecaRecusada as recusa:
        return {"peca": None, "motivo": recusa.motivo, "manchetes": ()}
    return {
        "peca": peca,
        "motivo": "" if kit_pacote.disponivel() else SEM_RASTERIZADOR,
        "png": kit_pacote.disponivel(),
        "manchetes": kit_peca.manchetes(ficha),
        "manchete": indice,
    }


def exportacoes(edital):
    """A exportação mais recente de cada impressão registrada, da mais nova à mais antiga (`D-005`).

    **O leve primeiro.** A faixa compara por impressão (`FR-3439`), e de cada impressão só a mais
    recente conta. Ler o `detalhe` inteiro de todos os eventos — com os campos de todos os Perfis —
    custaria cada vez mais a cada exportação; lê-se o instante e a impressão de todos, e o `detalhe`
    completo só de um evento por impressão, que são tantas quantas as versões do material.
    """
    base = RegistroAuditoria.objects.filter(
        aggregate_type="Edital", aggregate_id=edital.pk, operation=OPERACAO
    )
    escolhidos, vistas = [], set()
    for identificador, impressao in base.order_by("-occurred_at").values_list(
        "pk", "detalhe__impressao"
    ):
        if impressao not in vistas:
            vistas.add(impressao)
            escolhidos.append(identificador)
    detalhes = {
        identificador: (quando, detalhe)
        for identificador, quando, detalhe in base.filter(pk__in=escolhidos).values_list(
            "pk", "occurred_at", "detalhe"
        )
    }
    return [
        {
            **(detalhes[i][1] or {}),
            "exportado_em": fichas.instante_por_extenso(detalhes[i][0]),
        }
        for i in escolhidos
    ]


def _material(ficha):
    textos = kit_textos.compor(ficha)
    notas = kit_textos.notas_para_quem_divulga(ficha)
    return textos, notas


@require_http_methods(["GET"])
def kit(request, edital_id):
    """A tela única do kit (`FR-3443`): conferência, textos, faixas e exportações."""
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=_base_url(request))
    dados = request.GET
    tela = (dados.get("familia_da_tela") or "").strip()
    if tela and tela != (dados.get("familia") or "").strip():
        # A pessoa trocou de família no formulário: a imagem, a variante e a manchete marcadas
        # eram da família anterior, e não um pedido para a nova. A nova abre com as primeiras da
        # lista dela; sem isto, sair da Pós para a Institucional era "escolha indisponível".
        dados = {"familia": dados.get("familia", "")}
    indice = _indice_da_manchete(dados)
    try:
        escolhida = kit_escolha.ler(dados, ficha, edital, indice_da_manchete=indice)
        aviso_da_escolha = escolhida.aviso
    except kit_escolha.EscolhaInvalida:
        # A tela abre com a pré-escolha e diz por quê; nada é gerado com a escolha pedida (EC-9).
        escolhida, indice = kit_escolha.ler({}, ficha, edital), None
        aviso_da_escolha = kit_escolha.ESCOLHA_INDISPONIVEL
    textos, notas = _material(ficha)
    anteriores = exportacoes(edital)
    desatualizadas, mais = fichas.desatualizacoes(anteriores, ficha)
    return marcar_como_privada(
        render(
            request,
            "interface/kit_de_divulgacao.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "ficha": ficha,
                "conferencia": kit_textos.conferencia(ficha),
                "textos": [
                    (chave, kit_textos.TITULOS[chave], textos[chave])
                    for chave in kit_textos.TITULOS
                    if chave in textos
                ],
                "notas": notas,
                "desatualizadas": desatualizadas,
                "mais_desatualizadas": mais,
                # O desfecho depois de uma exportação: o material não deve mais circular (FR-3445).
                "exportado_sem_material": (not ficha.tem_material) and bool(anteriores),
                "ultima_exportacao": anteriores[0]["exportado_em"] if anteriores else "",
                "formatos": list(TEXTOS),
                "formatos_da_peca": list(PECAS),
                "formato_do_pacote": next(iter(PACOTE)),
                "secao_da_peca": (
                    _secao_da_peca(request, ficha, indice) if escolhida.institucional else None
                ),
                "secoes_da_familia": (
                    None
                    if escolhida.institucional
                    else _secoes_da_familia(request, ficha, escolhida)
                ),
                "escolha": escolhida,
                "familias": kit_escolha.familias_oferecidas(ficha),
                "aviso_da_escolha": aviso_da_escolha,
            },
        )
    )


@require_http_methods(["GET"])
def previa(request, edital_id):
    """O PNG da peça para a tela, com a impressão conferida, sem registro (`D-014`, FR-3446)."""
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    da_institucional = not _da_familia(request.GET)
    if _motivo_sem_peca(request, da_institucional=da_institucional) or not kit_pacote.disponivel():
        raise Http404
    indice = _indice_da_manchete(request.GET)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=_base_url(request))
    if not ficha.tem_material:
        raise Http404
    if request.GET.get("impressao", "") != ficha.impressao:
        raise DomainError("kit_desatualizado", MUDOU, 409)
    try:
        # Escolha fora da lista e template não liberado são a peça que não existe neste acesso.
        peca, _ = _peca_pedida(ficha, edital, request.GET, indice)
    except kit_peca.PecaRecusada:
        raise Http404 from None
    resposta = HttpResponse(
        kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca)), "image/png"
    )
    resposta["Content-Disposition"] = "inline"
    resposta["X-Content-Type-Options"] = "nosniff"
    return marcar_como_privada(resposta)


def _arquivo_da_peca(ficha, peca, formato):
    if formato == "svg":
        return kit_peca.svg(peca, ficha, fonte_embutida=True).encode()
    return kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca))


def pacote(ficha, *, manchete, motivo_sem_peca):
    """O ZIP do material, a peça que entrou e o motivo de ela faltar (`FR-3435`, EC-21).

    **A recusa da peça não recusa o pacote** (contrato): a composição que não cabe sai do ZIP com o
    motivo nomeado no manifesto, e os textos seguem. Manchete fora da lista continua 422 — é pedido
    inválido, e não peça que não cabe.
    """
    peca, motivo = None, motivo_sem_peca
    if not motivo:
        try:
            peca = _compor(ficha, manchete)
        except kit_peca.PecaRecusada as recusa:
            motivo = recusa.motivo
    png = svg = None
    if peca is not None:
        svg = kit_peca.svg(peca, ficha, fonte_embutida=True).encode()
        if kit_pacote.disponivel():
            png = kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca))
        else:
            motivo = SEM_RASTERIZADOR
    textos, notas = _material(ficha)
    dados = kit_pacote.montar(
        ficha,
        markdown=kit_textos.em_markdown(ficha, textos, notas),
        texto=kit_textos.em_texto(ficha, textos, notas),
        peca=peca,
        svg=svg,
        png=png,
        motivo_sem_peca=motivo,
    )
    return dados, peca, motivo


def pacote_da_familia(ficha, edital, dados, indice):
    """O ZIP da família: a peça de cada formato liberado, e o motivo dos que não entram (FR-3829).

    Escolha fora da lista continua 400 — é pedido inválido, e não formato que não cabe.
    """
    escolhida = kit_escolha.ler(dados, ficha, edital, indice_da_manchete=indice)
    liberados = kit_familias.liberados()
    lista = kit_escolha.manchetes(ficha, escolhida, liberados)
    formatos = []
    for template in kit_escolha.templates_da_familia(escolhida.familia):
        item = {"formato": template.formato.chave, "template": template, "peca": None}
        item.update(svg=None, png=None, motivo="", recusa="")
        try:
            peca = kit_escolha.compor(ficha, escolhida, item["formato"], liberados, lista)
        except kit_escolha.EscolhaInvalida:
            raise
        except kit_escolha.NaoLiberado as fechado:
            divergente = fechado.motivo == kit_escolha.VERSAO_EM_APROVACAO
            item["motivo"] = "versao_divergente" if divergente else "nao_liberado"
        except kit_peca.PecaRecusada as recusa:
            item.update(motivo="recusa", recusa=recusa.motivo)
        else:
            item["peca"] = peca
            item["svg"] = kit_peca.svg(peca, ficha, fonte_embutida=True).encode()
            if kit_pacote.disponivel():
                item["png"] = kit_pacote.rasterizar(
                    kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca)
                )
            else:
                item["motivo"] = "sem_rasterizador"
        formatos.append(item)
    textos, notas = _material(ficha)
    dados_do_zip, pecas = kit_pacote.montar_da_familia(
        ficha,
        markdown=kit_textos.em_markdown(ficha, textos, notas),
        texto=kit_textos.em_texto(ficha, textos, notas),
        escolhida=escolhida,
        formatos=formatos,
    )
    imagem = escolhida.imagem_do_banco()
    detalhe = {
        "familia": escolhida.familia.chave,
        "familia_versao": escolhida.familia.versao,
        "variante": escolhida.variante,
        "imagem": imagem.chave if imagem else None,
        "imagem_sha256": {f: imagem.sha256(f) for f in imagem.arquivos} if imagem else None,
        "pecas": pecas,
    }
    return dados_do_zip, detalhe


@require_http_methods(["POST"])
def exportar(request, edital_id, formato):
    """O material num arquivo, registrado na trilha do Edital (`FR-3435`, `FR-3436`)."""
    if formato not in FORMATOS:
        raise Http404
    ator, edital = _edital_do_kit(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    e_peca = formato in PECAS
    da_institucional = not _da_familia(request.POST)
    if e_peca and (
        _motivo_sem_peca(request, da_institucional=da_institucional)
        or (formato == "png" and not kit_pacote.disponivel())
    ):
        raise Http404
    agora = timezone.now()
    ficha = fichas.ler(edital, agora=agora, base_url=_base_url(request))
    if not ficha.tem_material:
        raise DomainError("kit_sem_material", ficha.motivo, 409)
    if request.POST.get("impressao", "") != ficha.impressao:
        raise DomainError("kit_desatualizado", MUDOU, 409)
    peca, sem_peca, escolhida, da_familia = None, None, None, {}
    if formato in PACOTE and not da_institucional:
        try:
            dados, da_familia = pacote_da_familia(
                ficha, edital, request.POST, _indice_da_manchete(request.POST)
            )
        except kit_escolha.EscolhaInvalida as invalida:
            raise DomainError("kit_escolha_invalida", invalida.motivo, 400) from None
    elif formato in PACOTE:
        try:
            _conferir_institucional(request.POST)
        except kit_escolha.EscolhaInvalida as invalida:
            raise DomainError("kit_escolha_invalida", invalida.motivo, 400) from None
        # A família também no ZIP da Institucional (FR-3828): é por ela que a tela reabre na
        # escolha mais recente, e não na última exportação que a registrou.
        da_familia = kit_escolha.detalhe_da_familia(
            kit_escolha.Escolhida(institucional.FAMILIA, None, None, None)
        )
        dados, peca, motivo = pacote(
            ficha,
            manchete=_indice_da_manchete(request.POST),
            motivo_sem_peca=_motivo_sem_peca(request),
        )
        sem_peca = motivo or None
    elif e_peca:
        indice = _indice_da_manchete(request.POST)
        try:
            peca, escolhida = _peca_pedida(ficha, edital, request.POST, indice)
        except kit_escolha.EscolhaInvalida as invalida:
            raise DomainError("kit_escolha_invalida", invalida.motivo, 400) from None
        except kit_escolha.NaoLiberado as fechado:
            raise DomainError("kit_template_indisponivel", fechado.motivo, 409) from None
        except kit_peca.PecaRecusada as recusa:
            raise DomainError("kit_peca_recusada", recusa.motivo, 409) from None
        dados = _arquivo_da_peca(ficha, peca, formato)
    else:
        textos, notas = _material(ficha)
        if formato == "md":
            conteudo = kit_textos.em_markdown(ficha, textos, notas)
        else:
            conteudo = kit_textos.em_texto(ficha, textos, notas)
        dados = conteudo.encode()
    record_event(
        actor=ator,
        permission=PERMISSAO,
        operation=OPERACAO,
        aggregate=edital,
        now=agora,
        correlation_id=request.correlation_id,
        # Não é transição: o estado e a revisão anteriores são os de agora (FR-3436).
        previous_state=edital.status,
        previous_revision=edital.revision,
        detalhe={
            "formato": formato,
            "referencia": ficha.referencia,
            "versao": {
                "id": ficha.versao_id,
                "content_hash": ficha.versao_hash,
                "vigente_desde": ficha.versao_desde,
                "ato": ficha.versao_ato,
            },
            "template": peca.template.identificador if peca else None,
            "impressao": ficha.impressao,
            "versao_da_impressao": ficha.versao_da_impressao,
            "campos": ficha.campos,
            "manchete": peca.manchete if peca else None,
            "sha256": hashlib.sha256(dados).hexdigest(),
            **({"sem_peca": sem_peca} if formato in PACOTE else {}),
            # A escolha da peça, que não é guardada em lugar nenhum além daqui (FR-3828, D-008).
            **(kit_escolha.detalhe(escolhida, peca) if escolhida and peca else {}),
            **da_familia,
        },
    )
    tipo, extensao = FORMATOS[formato]
    resposta = HttpResponse(dados, content_type=tipo)
    resposta["Content-Disposition"] = (
        f'attachment; filename="kit-{ficha.numero}-{ficha.ano}.{extensao}"'
    )
    resposta["X-Content-Type-Options"] = "nosniff"
    if formato == "svg":
        resposta["Content-Security-Policy"] = POLITICA_DO_SVG
    return marcar_como_privada(resposta)
