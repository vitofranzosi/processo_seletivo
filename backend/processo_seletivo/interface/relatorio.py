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
from processo_seletivo.interface import identidade, relatorio_do_edital, relatorio_pdf
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.infrastructure.pdf import CaractereSemGrafia
from processo_seletivo.seguranca.application.authorization import require_authorization_base
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada

INDISPONIVEL = "O relatório fica disponível quando o Edital for publicado."
TENTE_DE_NOVO = "Outro registro foi gravado agora. Baixe o relatório de novo."
#: `serialization_failure` e `deadlock_detected`, os dois códigos do PostgreSQL que dizem "tente de
#: novo" a uma transação que leu um instante e encontrou outro.
CONCORRENCIA = frozenset({"40001", "40P01"})


class _Enderecos:
    """Os endereços públicos, absolutos, como os avisos aos candidatos os montam (R-005)."""

    def __init__(self, request, edital):
        self.request = request
        self.edital = edital

    def selecao(self):
        return self.request.build_absolute_uri(reverse("portal:selecao", args=[self.edital.id]))

    def resultado(self, publicacao_id):
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
                edital, agora=agora, enderecos=_Enderecos(request, edital)
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
