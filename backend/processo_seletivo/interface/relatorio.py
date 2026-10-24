"""As duas portas do relatório do Edital: ler a página e emitir o PDF (099).

**A porta é a da Supervisão** (D-003): gestão do escopo ou presidência do Processo, cada uma
suficiente sozinha — quem conduz é quem responde à direção, e já lê cada número do relatório nas
telas donas. A gramática é a da `033`: Edital inexistente ou de outra unidade responde "não
encontrado"; quem é da unidade e não tem a base recebe a recusa que diz o que falta (FR-2514).

**Baixar é emitir, e emitir fica registrado** (FR-2515, FR-2516). Por isso o PDF sai de um `POST`:
o documento sai do sistema, e a trilha precisa dizer quem o levou, com dados de quando e qual
arquivo. A página, que só lê, não registra — como a Supervisão.
"""

import hashlib
from urllib.parse import urlencode

from django.db import OperationalError
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.domain.autorizacao import (
    BASES_DA_GESTAO_DA_COMISSAO,
    pode_gerir_comissao,
)
from processo_seletivo.interface import (
    identidade,
    relatorio_consolidado_pdf,
    relatorio_do_edital,
    relatorio_pdf,
    visao_geral,
)
from processo_seletivo.interface import relatorio_consolidado as relatorio_consolidado_mod
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.infrastructure.pdf import CaractereSemGrafia
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada
from processo_seletivo.unidades.application.selectors import exigir_unidade
from processo_seletivo.unidades.models import Unidade

INDISPONIVEL = "O relatório fica disponível quando o Edital for publicado."
TENTE_DE_NOVO = "Outro registro foi gravado agora. Baixe o relatório de novo."
#: `serialization_failure` e `deadlock_detected`, os dois códigos do PostgreSQL que dizem "tente de
#: novo" a uma transação que leu um instante e encontrou outro.
CONCORRENCIA = frozenset({"40001", "40P01"})


class _Enderecos:
    """Os endereços públicos, absolutos, como os avisos aos candidatos os montam (R-005).

    No PDF, só quando valem para quem recebe o arquivo (FR-2603): emitido de um host local, o
    endereço seria `localhost`, que não abre fora da máquina de quem emitiu. Aí não há endereço, e
    o documento diz por quê. A página da gestão continua com os links: quem a lê está no mesmo host.
    """

    def __init__(self, request, edital, *, so_publicos=False):
        self.request = request
        self.edital = edital
        self.vazios = so_publicos and _host_local(request)

    def selecao(self):
        if self.vazios:
            return ""
        return self.request.build_absolute_uri(reverse("portal:selecao", args=[self.edital.id]))

    def resultado(self, publicacao_id):
        if self.vazios:
            return ""
        return self.request.build_absolute_uri(reverse("portal:resultado", args=[publicacao_id]))


def _edital_para_relatar(request, edital_id):
    """Ator, Edital e base — com 404 só para o que não existe ou é de outra unidade (033)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, None, None
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=ator.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise Http404
    base = pode_gerir_comissao(ator, edital.processo)
    require_authorization_base(base is not None, bases=BASES_DA_GESTAO_DA_COMISSAO)
    if edital.status not in relatorio_do_edital.ESTADOS_COM_RELATORIO:
        raise DomainError("relatorio_indisponivel", INDISPONIVEL, 409)
    return ator, edital, base


@require_http_methods(["GET"])
def relatorio(request, edital_id):
    """A camada executiva do relatório, e o botão que emite o PDF (FR-2515)."""
    ator, edital, _ = _edital_para_relatar(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    lido = relatorio_do_edital.ler(
        edital, agora=timezone.now(), enderecos=_Enderecos(request, edital)
    )
    return marcar_como_privada(
        render(
            request,
            "interface/relatorio_do_edital.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "relatorio": lido,
                "referencia": relatorio_do_edital.instante_por_extenso(lido.referencia),
                # Os textos saem das mesmas funções que o PDF usa: a tela não formata número.
                "indicadores": [
                    (i.rotulo, relatorio_do_edital.texto_do_indicador(i), i.base)
                    for i in lido.indicadores
                ],
                "perfis": [
                    (
                        p,
                        relatorio_do_edital.texto_das_vagas(p),
                        relatorio_do_edital.interpretar(p.inscricoes),
                        relatorio_do_edital.interpretar(p.por_vaga),
                        relatorio_do_edital.interpretar(p.classificadas),
                    )
                    for p in lido.perfis
                ],
                "semanas": relatorio_do_edital.semanas(lido),
            },
        )
    )


@require_http_methods(["POST"])
def emitir(request, edital_id):
    """O PDF, numerado e registrado na trilha com o resumo dos bytes entregues (R-003)."""
    ator, edital, base = _edital_para_relatar(request, edital_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    agora = timezone.now()
    try:
        with relatorio_do_edital.leitura_consistente():
            # A trava serializa as emissões do Edital: duas simultâneas teriam o mesmo número.
            Edital.objects.select_for_update().get(pk=edital.pk)
            emissao = relatorio_do_edital.proxima_emissao(edital)
            lido = relatorio_do_edital.montar(
                edital, agora=agora, enderecos=_Enderecos(request, edital, so_publicos=True)
            )
            documento = relatorio_pdf.compor(lido, emissao=emissao)
            resumo = hashlib.sha256(documento).hexdigest()
            record_event(
                actor=ator,
                permission=base.permissao,
                operation=relatorio_do_edital.OPERACAO_DA_EMISSAO,
                aggregate=edital,
                now=agora,
                correlation_id=request.correlation_id,
                previous_state=edital.status,
                previous_revision=edital.revision,
                detalhe={
                    "referencia": agora.isoformat(),
                    "numero": emissao,
                    "sha256": resumo,
                    "especie": lido.especie,
                },
            )
    except CaractereSemGrafia as falha:
        # Como o Edital: o documento recusa o caractere que não sabe escrever, em vez de trocá-lo
        # por "?" e entregar um texto diferente do registrado (achado de 08/10).
        raise DomainError("relatorio_sem_grafia", str(falha), 422) from falha
    except OperationalError as falha:
        # Só a falha de serialização do `REPEATABLE READ` (ou o impasse) é concorrência: outro
        # registro travou o Edital no meio, e a emissão é refeita do zero, e não composta com metade
        # de cada instante. Qualquer outro erro de banco é defeito, e sobe como tal.
        if getattr(falha.__cause__, "sqlstate", None) not in CONCORRENCIA:
            raise
        raise DomainError("relatorio_concorrente", TENTE_DE_NOVO, 409) from falha
    resposta = HttpResponse(documento, content_type="application/pdf")
    nome = f"relatorio-edital-{edital.number}-{edital.year}-emissao-{emissao}.pdf"
    resposta["Content-Disposition"] = f'attachment; filename="{nome}"'
    return marcar_como_privada(resposta)


# --- O relatório consolidado da unidade (100) ---------------------------------------------------
#
# **A porta é a da Visão Geral** (D-009): ler o panorama institucional. O Gestor que a tem passa na
# porta do relatório do Edital em todo Processo do escopo — tudo o que ele consolida, ele já poderia
# abrir Edital a Edital. Não há 404: as rotas não endereçam objeto, e identificador de outro escopo
# no formulário é ignorado pela consulta, como inexistente (FR-2555).


def _ator_da_visao(request):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None
    require_authorization_base(
        ator.can(visao_geral.CONSULTAR),
        bases=[base_de_permissao("consultar a visão institucional")],
    )
    return ator


#: Hosts que só existem na máquina de quem emite: o endereço deles não vale para quem recebe o PDF.
HOSTS_LOCAIS = frozenset({"localhost", "127.0.0.1", "::1", "[::1]", "testserver"})


def _host_local(request):
    host = request.get_host().rsplit(":", 1)[0] if "]" not in request.get_host() else "[::1]"
    return host in HOSTS_LOCAIS or host.endswith(".localhost")


def _enderecos_das_selecoes(request, conjunto):
    """Os endereços públicos, ou nenhum, quando a emissão é local (revisão visual de 24/10/2026).

    Em produção o host da requisição é o que a instituição publica (R-005 da `099`). Na
    demonstração ele é `localhost`, e um link para ele no PDF parece endereço e não abre na mesa de
    quem o recebe: o documento diz que os endereços não estão disponíveis, em vez de imprimi-los.
    """
    if _host_local(request):
        return {}
    return {
        edital.pk: request.build_absolute_uri(reverse("portal:selecao", args=[edital.pk]))
        for edital in conjunto.incluidos
    }


def _parametros_do_conjunto(conjunto):
    """O conjunto como campos do formulário: o critério e, havendo escolha, os marcados."""
    campos = list(conjunto.criterio.parametros().items())
    if conjunto.escolha:
        campos.append(("escolha", "1"))
        campos.extend(("edital", str(edital.pk)) for edital in conjunto.incluidos)
    return campos


@require_http_methods(["GET"])
def relatorio_consolidado_escolha(request):
    """A escolha do conjunto: critério, atalhos e os Editais que ele alcança, marcados (FR-2559)."""
    ator = _ator_da_visao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    parametros = request.GET.copy()
    # "Aplicar" muda o critério: os marcados do critério anterior não valem no novo. Na escolha
    # manual, valem — buscar outro nome não desmarca o que já foi escolhido.
    if (
        parametros.get("acao") == "aplicar"
        and parametros.get("criterio") != relatorio_consolidado_mod.MANUAL
    ):
        parametros.pop("escolha", None)
        parametros.pop("edital", None)
    conjunto = relatorio_consolidado_mod.conjunto_de(ator, parametros)
    incluidos = {edital.pk for edital in conjunto.incluidos}
    elegiveis = [e for e in conjunto.alcancados if e not in {f for f, _ in conjunto.fora}]
    anos = sorted(
        {e.year for e in Edital.objects.filter(institution_scope=ator.institution_scope)}
        | {timezone.localdate().year},
        reverse=True,
    )
    return marcar_como_privada(
        render(
            request,
            "interface/relatorio_consolidado_escolha.html",
            {
                "conjunto": conjunto,
                "criterio": conjunto.criterio,
                "anos": anos,
                "linhas": [
                    (
                        edital,
                        relatorio_consolidado_mod.texto_da_primeira(conjunto.primeira(edital)),
                        edital.pk in incluidos,
                    )
                    for edital in elegiveis
                ],
                # Na escolha manual, os marcados fora da busca da vez viajam escondidos.
                "marcados_fora_da_lista": [
                    edital for edital in conjunto.incluidos if edital not in elegiveis
                ],
                "limite": relatorio_consolidado_mod.LIMITE_DE_EDITAIS,
            },
        )
    )


@require_http_methods(["GET"])
def relatorio_consolidado(request):
    """A camada executiva do conjunto, e o formulário que emite o PDF (FR-2573)."""
    ator = _ator_da_visao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    # A escolha dos Editais entra no mesmo instante que os números (FR-2564): lida antes, um Edital
    # cancelado no meio da leitura entraria com o estado de antes.
    with relatorio_do_edital.leitura_consistente():
        conjunto = relatorio_consolidado_mod.conjunto_de(ator, request.GET)
        conjunto.exigir_emissivel()
        unidade = exigir_unidade(ator.institution_scope)
        lido = relatorio_consolidado_mod.montar(conjunto, agora=timezone.now(), unidade=unidade)
    return marcar_como_privada(
        render(
            request,
            "interface/relatorio_consolidado.html",
            {
                "consolidado": lido,
                "conjunto": conjunto,
                "referencia": relatorio_do_edital.instante_por_extenso(lido.referencia),
                # Os textos saem das mesmas funções que o PDF usa: a tela não formata número.
                "indicadores": [
                    (i.rotulo, relatorio_do_edital.texto_do_indicador(i), i.base)
                    for i in lido.indicadores
                ],
                "linhas_por_edital": [
                    (
                        linha.edital,
                        str(linha.vagas) if linha.vagas else "só cadastro de reserva",
                        relatorio_do_edital.interpretar(linha.inscricoes)
                        + (" (parcial)" if linha.inscricoes.parcial else ""),
                        relatorio_do_edital.interpretar(linha.por_vaga),
                    )
                    for linha in lido.linhas
                ],
                "campos": _parametros_do_conjunto(conjunto),
                "voltar": f"{reverse('interface:relatorio-consolidado')}?"
                + urlencode(_parametros_do_conjunto(conjunto)),
            },
        )
    )


@require_http_methods(["POST"])
def emitir_relatorio_consolidado(request):
    """O PDF, numerado na unidade e registrado na trilha com o conjunto e o resumo (R-005)."""
    ator = _ator_da_visao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    agora = timezone.now()
    try:
        with relatorio_do_edital.leitura_consistente():
            # A trava serializa as emissões da unidade: duas simultâneas teriam o mesmo número.
            unidade = Unidade.objects.select_for_update().get(codigo=ator.institution_scope)
            conjunto = relatorio_consolidado_mod.conjunto_de(ator, request.POST)
            conjunto.exigir_emissivel()
            emissao = relatorio_consolidado_mod.proxima_emissao(unidade)
            lido = relatorio_consolidado_mod.montar(conjunto, agora=agora, unidade=unidade)
            lido.enderecos = _enderecos_das_selecoes(request, conjunto)
            lido.enderecos_locais = _host_local(request)
            documento = relatorio_consolidado_pdf.compor(lido, emissao=emissao)
            resumo = hashlib.sha256(documento).hexdigest()
            record_event(
                actor=ator,
                permission=visao_geral.CONSULTAR,
                operation=relatorio_consolidado_mod.OPERACAO_DA_EMISSAO,
                aggregate=unidade,
                now=agora,
                correlation_id=request.correlation_id,
                new_state="",
                new_revision=None,
                detalhe=_detalhe_da_emissao(conjunto, agora, emissao, resumo),
            )
    except CaractereSemGrafia as falha:
        raise DomainError("relatorio_sem_grafia", str(falha), 422) from falha
    except OperationalError as falha:
        if getattr(falha.__cause__, "sqlstate", None) not in CONCORRENCIA:
            raise
        raise DomainError("relatorio_concorrente", TENTE_DE_NOVO, 409) from falha
    resposta = HttpResponse(documento, content_type="application/pdf")
    nome = f"relatorio-consolidado-{unidade.sigla.lower()}-emissao-{emissao}.pdf"
    resposta["Content-Disposition"] = f'attachment; filename="{nome}"'
    return marcar_como_privada(resposta)


def _detalhe_da_emissao(conjunto, agora, emissao, resumo):
    def edital(e):
        return {"id": str(e.pk), "edital": f"{e.number}/{e.year}"}

    criterio = conjunto.criterio
    return {
        "referencia": agora.isoformat(),
        "numero": emissao,
        "sha256": resumo,
        "criterio": {
            "modo": criterio.modo,
            "ano": criterio.ano,
            "inicio": criterio.inicio.isoformat() if criterio.inicio else None,
            "fim": criterio.fim.isoformat() if criterio.fim else None,
            "busca": criterio.busca,
        },
        "incluidos": [edital(e) for e in conjunto.incluidos],
        "retirados": [edital(e) for e in conjunto.retirados],
        "fora": [{**edital(e), "motivo": motivo} for e, motivo in conjunto.fora],
    }
