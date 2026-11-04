"""As telas da entrega documental à formalização (117): a do setor e a da definição, na condução.

**Três funções, três donos** (matriz da spec). A condução define **o quê**, na tela da definição; a
gestão de acessos define **quem**, em `acessos.py`; e o setor **exporta**, nas telas daqui.

**A porta do setor é o predicado único** (FR-3664): `pode_acessar` decide a página, cada arquivo, a
verificação e a exportação, na mesma requisição. Fora do alcance é *inexistente*; sem o papel, a
recusa que o nomeia. Nenhuma outra base alcança estas telas (FR-3665): nem a presidência, nem quem
confere, nem quem consulta inscrições.

**Nada é escolhido antes** (FR-3683): a lista começa sem marcação. A seleção vai por POST, nunca na
URL, e as URLs levam só identificadores opacos (FR-3703).

**Visualizar é a ação primária** (FR-3677): `inline`, sem cache, com a cópia verificada da `009`.
Baixar é secundária e individual, com o nome `‹protocolo›-‹requisito›.pdf`, nunca o nome enviado.
"""

from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.comissoes.domain.autorizacao import (
    BASES_DA_GESTAO_DA_COMISSAO,
    pode_gerir_comissao,
)
from processo_seletivo.formalizacao.application import conjunto, definir, exportar
from processo_seletivo.formalizacao.domain import caminhos, nomes
from processo_seletivo.formalizacao.domain.autorizacao import (
    designacoes_vigentes,
    exigir_o_papel,
    pode_acessar,
)
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import identidade
from processo_seletivo.portal.arquivos import ArquivoIndisponivel, copia_verificada
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada

BASE_DA_AUDITORIA = base_de_permissao("consultar a trilha de auditoria")
INTEGRIDADE = (
    "O arquivo guardado não confere com o que foi conferido. O documento não pode ser entregue "
    "como íntegro; registre a ocorrência à presidência."
)


def _ator(request):
    return identidade.ator_da_sessao(request)


def _correlacao(request, sufixo):
    return getattr(request, "correlation_id", "") or f"formalizacao-{sufixo}"


# ---------------------------------------------------------------------------
# A lista e a página do Edital, do setor
# ---------------------------------------------------------------------------


@require_http_methods(["GET"])
def lista(request):
    """Os Editais com designação vigente do ator, e só eles (FR-3675)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    exigir_o_papel(ator)
    designacoes = list(
        designacoes_vigentes(pessoa=ator.subject)
        .filter(edital__institution_scope=ator.institution_scope)
        .select_related("edital")
        .order_by("-edital__year", "edital__number")
    )
    # As versões de todos os Editais numa consulta só, e não uma por linha.
    definir.guardar_conteudos([designacao.edital for designacao in designacoes])
    linhas = []
    for designacao in designacoes:
        perfis = {p.id: p.nome for p in definir.perfis_do_edital(designacao.edital)}
        linhas.append(
            {
                "edital": designacao.edital,
                "perfis": [perfis.get(str(p), "Perfil") for p in designacao.perfis],
            }
        )
    return marcar_como_privada(
        render(request, "interface/formalizacao_lista.html", {"linhas": linhas})
    )


def _perfis_no_alcance(acesso):
    todos = definir.perfis_do_edital(acesso.edital)
    return [perfil for perfil in todos if acesso.cobre(perfil.id)]


def _historico_de_exportacoes(edital, *, perfis=None, exportacoes=None):
    """As exportações do Edital, com as pessoas pelo protocolo e nome (FR-3679).

    `perfis`, quando dado, restringe ao alcance de quem lê: só as exportações cujas pessoas estão
    todas nos Perfis dele. Uma consulta pelas exportações e uma pelas pessoas citadas.
    """
    from processo_seletivo.seguranca.application.acessos import nomes_dos_autores

    if exportacoes is None:
        exportacoes = conjunto.exportacoes_do_edital(edital)
    ids = {pessoa["inscricao"] for e in exportacoes for pessoa in e.pessoas}
    inscricoes = {
        str(i.id): i
        for i in Inscricao.objects.filter(id__in=list(ids)).only("id", "protocolo", "nome")
    }
    perfil_de = {}
    if perfis is not None:
        from processo_seletivo.convocacao.models import Convocacao

        perfil_de = dict(
            Convocacao.objects.filter(
                id__in={p["convocacao"] for e in exportacoes for p in e.pessoas}
            ).values_list("id", "perfil_id")
        )
    autores = nomes_dos_autores({e.exportado_por for e in exportacoes})
    perfis_do = {p.id: p.nome for p in definir.perfis_do_edital(edital)}
    linhas = []
    for exportacao in exportacoes:
        if perfis is not None and any(
            str(perfil_de.get(_uuid(p["convocacao"]))) not in perfis for p in exportacao.pessoas
        ):
            continue

        def legivel(pessoa):
            registro = inscricoes.get(pessoa["inscricao"])
            return {
                "protocolo": registro.protocolo if registro else pessoa["inscricao"],
                "nome": registro.nome if registro else "",
                "motivo": nomes.ROTULO_DA_SITUACAO.get(pessoa.get("motivo", ""), ""),
            }

        alcance = nomes.ROTULO_DO_ALCANCE[exportacao.alcance]
        if exportacao.perfil_id:
            alcance += f" do Perfil {perfis_do.get(str(exportacao.perfil_id), '')}"
        linhas.append(
            {
                "exportacao": exportacao,
                "autor": autores.get(exportacao.exportado_por, exportacao.exportado_por),
                "alcance": alcance,
                "resultado": exportar.frase_do_resultado(
                    exportacao.resultado, len(exportacao.incluidas), len(exportacao.pessoas)
                ),
                "incluidas": [legivel(p) for p in exportacao.incluidas],
                "nao_incluidas": [legivel(p) for p in exportacao.nao_incluidas],
                "tamanho": conjunto.tamanho_legivel(exportacao.tamanho),
            }
        )
    return linhas


def _uuid(valor):
    import uuid

    try:
        return uuid.UUID(str(valor))
    except ValueError:
        return None


def _agrupar(pessoas):
    grupos = []
    for pessoa in pessoas:
        if not grupos or grupos[-1]["perfil_id"] != pessoa.perfil_id:
            grupos.append(
                {"perfil_id": pessoa.perfil_id, "nome": pessoa.perfil_nome, "pessoas": []}
            )
        grupos[-1]["pessoas"].append(pessoa)
    return grupos


@require_http_methods(["GET"])
def edital(request, edital_id):
    """Os aptos do alcance, por Perfil, com os documentos definidos e o histórico (FR-3676)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    acesso = pode_acessar(ator, edital_id)
    no_alcance = _perfis_no_alcance(acesso)
    # Um controle de recorte só, o Perfil, e só com mais de um no alcance (FR-3681).
    perfil = request.GET.get("perfil") or ""
    if perfil and perfil not in {p.id for p in no_alcance}:
        raise Http404
    perfis = [perfil] if perfil else (list(acesso.designacao.perfis) or None)
    definicao = definir.vigente(acesso.edital)
    # Uma leitura dos registros de exportação, para a "última exportação" e para o histórico.
    exportacoes = conjunto.exportacoes_do_edital(acesso.edital)
    pessoas = conjunto.aptos(
        acesso.edital, definicao=definicao, perfis=perfis, exportacoes=exportacoes
    )
    com_documento = any(pessoa.incluiveis for pessoa in pessoas)
    return marcar_como_privada(
        render(
            request,
            "interface/formalizacao_edital.html",
            {
                "edital": acesso.edital,
                "grupos": _agrupar(pessoas),
                "total": len(pessoas),
                "definicao": definicao,
                "com_documento": com_documento,
                "perfis_no_alcance": no_alcance if len(no_alcance) > 1 else [],
                "perfil": perfil,
                "historico": _historico_de_exportacoes(
                    acesso.edital,
                    exportacoes=exportacoes,
                    perfis=(
                        {str(p) for p in acesso.designacao.perfis}
                        if acesso.designacao.perfis
                        else None
                    ),
                ),
                "nomes": nomes,
            },
        )
    )


# ---------------------------------------------------------------------------
# O arquivo, um por vez
# ---------------------------------------------------------------------------


def _evento_do_documento(ator, operacao, documento, request):
    with transaction.atomic():
        exportar.registrar_evento(
            ator,
            operacao,
            documento.objeto,
            reason=f"requisito {documento.requisito_id}",
            correlation_id=_correlacao(request, "documento"),
        )


@require_http_methods(["GET"])
def documento(request, edital_id, inscricao_id, origem, objeto_id):
    """Um documento definido de uma pessoa apta do alcance, conferido antes de sair um byte."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    acesso = pode_acessar(ator, edital_id)
    if origem not in nomes.ORIGENS:
        raise Http404
    pessoas = conjunto.aptos(
        acesso.edital,
        definicao=definir.vigente(acesso.edital),
        perfis=list(acesso.designacao.perfis) or None,
        inscricoes=[inscricao_id],
        com_exportacoes=False,
    )
    alvo = next(
        (
            (pessoa, item)
            for pessoa in pessoas
            for item in pessoa.incluiveis
            if item.origem == origem and item.objeto_id == str(objeto_id)
        ),
        None,
    )
    if alvo is None:
        raise Http404
    pessoa, item = alvo
    try:
        copia, calculado = copia_verificada(item.fonte)
    except ArquivoIndisponivel:
        _evento_do_documento(ator, nomes.ARQUIVO_INDISPONIVEL, item, request)
        raise
    if calculado != item.hash_esperado:
        copia.close()
        _evento_do_documento(ator, "INTEGRIDADE", item, request)
        raise DomainError("document_integrity_failed", INTEGRIDADE, 409)
    baixar = bool(request.GET.get("baixar"))
    _evento_do_documento(ator, nomes.DOWNLOAD if baixar else nomes.VISUALIZAR, item, request)
    resposta = FileResponse(
        copia,
        content_type="application/pdf",
        as_attachment=baixar,
        filename=caminhos.nome_do_download_individual(pessoa.protocolo, item.chave),
    )
    return marcar_como_privada(resposta)


# ---------------------------------------------------------------------------
# A verificação e a exportação
# ---------------------------------------------------------------------------


def _recusa(request, edital_id, erro, *, status=None):
    """A página das recusas da exportação, que oferece verificar de novo (FR-3689)."""
    contexto = {
        "edital_id": edital_id,
        "titulo": "A exportação não aconteceu",
        "detalhe": erro.detail,
        "codigo": erro.code,
        "limite": getattr(erro, "pessoas", None),
        "limite_total": conjunto.tamanho_legivel(getattr(erro, "total", 0)),
    }
    if isinstance(erro, exportar.PessoaIncompleta):
        contexto["titulo"] = "O pacote desta pessoa não foi gerado"
    if isinstance(erro, exportar.ExportacaoInterrompida):
        contexto["titulo"] = "A exportação não foi concluída"
    return marcar_como_privada(
        render(
            request,
            "interface/formalizacao_recusa.html",
            contexto,
            status=status or erro.status,
        )
    )


#: As recusas que a página da exportação explica; as demais são da matriz e vão à página comum.
RECUSAS_DA_EXPORTACAO = (
    exportar.LimiteExcedido,
    exportar.VerificacaoDefasada,
    exportar.PessoaIncompleta,
    exportar.ExportacaoInterrompida,
)
CODIGOS_DA_EXPORTACAO = {
    nomes.VERIFICACAO_INVALIDA,
    nomes.VERIFICACAO_EXPIRADA,
    nomes.EXPORTACAO_EM_ANDAMENTO,
    nomes.SEM_DOCUMENTO,
    nomes.SEM_PESSOA,
    nomes.ALCANCE_INVALIDO,
}


def _servir(gerado):
    resposta = FileResponse(
        gerado.arquivo,
        content_type="application/zip",
        as_attachment=True,
        filename=gerado.nome,
    )
    return marcar_como_privada(resposta)


def _exportando(request, edital_id, fazer):
    try:
        return fazer()
    except DomainError as erro:
        if isinstance(erro, RECUSAS_DA_EXPORTACAO) or erro.code in CODIGOS_DA_EXPORTACAO:
            return _recusa(request, edital_id, erro)
        raise


@require_http_methods(["POST"])
def verificar(request, edital_id):
    """A verificação: lê e confere tudo, e mostra o resultado antes do download (FR-3684)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    todos = request.POST.get("alcance") == "todos"

    def fazer():
        verificacao, comprovante = exportar.verificar(
            ator,
            edital_id=edital_id,
            alcance=nomes.RECORTE if todos else nomes.SELECAO,
            perfil_id=request.POST.get("perfil", "") if todos else "",
            pessoas=[] if todos else request.POST.getlist("pessoa"),
            correlation_id=_correlacao(request, "verificar"),
        )
        perfis = {p.id: p.nome for p in definir.perfis_do_edital(verificacao.edital)}
        return marcar_como_privada(
            render(
                request,
                "interface/formalizacao_verificacao.html",
                {
                    "edital": verificacao.edital,
                    "verificacao": verificacao,
                    "comprovante": comprovante,
                    "frase": exportar.frase_do_resultado(
                        verificacao.resultado,
                        len(verificacao.incluidas),
                        len(verificacao.pessoas),
                    ),
                    "alcance": nomes.ROTULO_DO_ALCANCE[verificacao.alcance],
                    "perfil_do_recorte": perfis.get(verificacao.perfil_id, ""),
                    "nomes": nomes,
                },
            )
        )

    return _exportando(request, edital_id, fazer)


@require_http_methods(["POST"])
def baixar(request, edital_id):
    """O download do pacote verificado. O comprovante vem no corpo, nunca na URL (FR-3689a)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    return _exportando(
        request,
        edital_id,
        lambda: _servir(
            exportar.baixar(
                ator,
                edital_id=edital_id,
                token=request.POST.get("comprovante", ""),
                correlation_id=_correlacao(request, "baixar"),
            )
        ),
    )


@require_http_methods(["POST"])
def exportar_pessoa(request, edital_id, inscricao_id):
    """A exportação de uma pessoa só: o ZIP num clique, ou a página com o motivo (FR-3685)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    return _exportando(
        request,
        edital_id,
        lambda: _servir(
            exportar.exportar_pessoa(
                ator,
                edital_id=edital_id,
                inscricao_id=inscricao_id,
                correlation_id=_correlacao(request, "pessoa"),
            )
        ),
    )


# ---------------------------------------------------------------------------
# A definição, na condução
# ---------------------------------------------------------------------------


def _edital_da_definicao(ator, edital_id):
    """O Edital e o modo da tela: `gravar` para a condução, `ler` para o auditor (FR-3711).

    Outra unidade ou inexistente é 404; no escopo, sem gerir a comissão nem auditar, a recusa que
    diz o que falta — e o setor da formalização está entre os recusados.
    """
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    pode_gravar = pode_gerir_comissao(ator, edital.processo) is not None
    pode_ler = pode_gravar or ator.can("auditoria:consultar")
    require_authorization_base(pode_ler, bases=(*BASES_DA_GESTAO_DA_COMISSAO, BASE_DA_AUDITORIA))
    return edital, pode_gravar


def _designacoes_para_leitura(edital):
    from processo_seletivo.seguranca.application.acessos import nomes_dos_autores

    vigentes = list(designacoes_vigentes(edital=edital).order_by("designado_em", "id"))
    nomes_legiveis = nomes_dos_autores(
        {d.pessoa for d in vigentes} | {d.designado_por for d in vigentes}
    )
    perfis = {p.id: p.nome for p in definir.perfis_do_edital(edital)}
    return [
        {
            "designacao": d,
            "pessoa": nomes_legiveis.get(d.pessoa, d.pessoa),
            "por": nomes_legiveis.get(d.designado_por, d.designado_por),
            "perfis": [perfis.get(str(p), "Perfil") for p in d.perfis],
        }
        for d in vigentes
    ]


@require_http_methods(["GET", "POST"])
def definicao(request, edital_id):
    """A definição dos documentos para a formalização, o histórico e quem os acessa (US1)."""
    ator = _ator(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    edital_da_tela, pode_gravar = _edital_da_definicao(ator, edital_id)
    requisitos = definir.requisitos_do_edital(edital_da_tela)
    vigente = definir.vigente(edital_da_tela)
    marcados = {str(r) for r in (vigente.requisitos if vigente else [])}
    erro = ""
    motivo = ""
    if request.method == "POST":
        if not pode_gravar:
            require_authorization_base(False, bases=BASES_DA_GESTAO_DA_COMISSAO)
        marcados = set(request.POST.getlist("requisito"))
        motivo = request.POST.get("motivo", "")
        try:
            definir.definir(
                actor=ator,
                edital_id=edital_da_tela.id,
                requisitos=sorted(marcados),
                motivo=motivo,
                correlation_id=_correlacao(request, "definir"),
            )
        except DomainError as recusa:
            if recusa.status not in (409, 422):
                raise
            erro = recusa.detail
        else:
            request.session["aviso_da_definicao"] = (
                "Definição gravada. Ela vale para as próximas consultas e exportações do setor."
            )
            return redirect(reverse("interface:formalizacao-definicao", args=[edital_da_tela.id]))
    from processo_seletivo.interface.navegacao import declarar_secao

    declarar_secao(request, "interface:lista")
    return marcar_como_privada(
        render(
            request,
            "interface/formalizacao_definicao.html",
            {
                "processo": edital_da_tela.processo,
                "edital": edital_da_tela,
                "requisitos": requisitos,
                "marcados": marcados,
                "pode_gravar": pode_gravar,
                "historico": definir.historico(edital_da_tela, requisitos),
                "designacoes": _designacoes_para_leitura(edital_da_tela),
                "exportacoes": _historico_de_exportacoes(edital_da_tela),
                "erro": erro,
                "motivo": motivo,
                "aviso": request.session.pop("aviso_da_definicao", None),
            },
            status=422 if erro else 200,
        )
    )
