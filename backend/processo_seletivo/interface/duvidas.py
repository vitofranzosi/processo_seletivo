"""A tela de validação interna das respostas do assistente de dúvidas (070, contracts/tela.md).

**Validação interna, e não rota pública** (`D-001`, `FR-1445`). Aqui o setor de seleção confere,
Edital a Edital, o que o assistente poderá dizer — antes de qualquer abertura ao público. Nada desta
tela é exibido a candidatos.

**O alcance é o da página do Edital, sem capacidade nova** (`D-010`): identidade da gestão no escopo
institucional do Edital. Fora dele, a recusa é o `not_found` de sempre, como nas telas dos avisos —
um `DomainError` que o middleware de recusas traduz, e não um `Http404` solto.

**GET, e nada grava** (`R-018`, `FR-1449`). A consulta é endereçável, o "voltar" funciona, e a mesma
leitura serve a resposta e os pontos para revisão: um instante, uma versão (`FR-1411`).
"""

from datetime import UTC, datetime
from uuid import UUID

from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, contexto
from processo_seletivo.duvidas.domain import catalogo, leitura, respostas, revisao
from processo_seletivo.duvidas.domain.estruturas import (
    ROTULO_DA_NATUREZA,
    ROTULO_DO_TIPO,
)
from processo_seletivo.interface import identidade
from processo_seletivo.processos.application.selectors import obter_edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.tempo import ZONA

FORMATO_DO_INSTANTE = "%Y-%m-%dT%H:%M"


def _instante(valor):
    """`(instante, recusa)`: o instante de referência na zona institucional (`R-020`, `D-009`).

    Sem valor, o presente. Valor que não se entende não vira erro: a tela consulta no presente e
    diz que não entendeu, porque recusar a página inteira por um campo opcional seria pior.
    """
    if not valor:
        return timezone.now(), ""
    try:
        instante = datetime.strptime(valor, FORMATO_DO_INSTANTE).replace(tzinfo=ZONA)
        # O banco compara em UTC, e `9999-12-31T23:59` em Brasília passa do último instante que o
        # `datetime` representa: sem a conversão aqui, o campo opcional derrubava a página com 500.
        instante.astimezone(UTC)
    except (ValueError, OverflowError):
        return timezone.now(), "O instante informado não foi entendido; a consulta usa o presente."
    return instante, ""


def _uuid(valor):
    try:
        return str(UUID(str(valor))) if valor else None
    except ValueError:
        return None


def _modalidades_por_perfil(conteudo):
    return [
        (codigo, rotulo, catalogo.opcoes_de_modalidade(leitura.perfil_por_codigo(conteudo, codigo)))
        for codigo, rotulo in catalogo.opcoes_de_perfil(conteudo)
    ]


@require_http_methods(["GET"])
def respostas_do_assistente(request, edital_id):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)

    instante, recusa_do_instante = _instante(request.GET.get("em", "").strip())
    pagina = {
        "edital": edital,
        "processo": edital.processo,
        "instante": instante,
        "instante_no_campo": instante.astimezone(ZONA).strftime(FORMATO_DO_INSTANTE),
        "instante_legivel": leitura.instante_legivel(instante),
        "recusa_do_instante": recusa_do_instante,
        "rotulo_da_natureza": ROTULO_DA_NATUREZA,
        "rotulo_do_tipo": ROTULO_DO_TIPO,
    }
    try:
        lido = contexto(
            edital_id=edital.id,
            instante=instante,
            versao_anterior=_uuid(request.GET.get("versao")),
        )
    except SemVersaoVigente:
        pagina["publicado"] = Publicacao.objects.filter(edital=edital).exists()
        return render(request, "interface/duvidas.html", pagina)

    pagina.update(
        {
            "publicado": True,
            "versao": lido.versao,
            "perguntas": catalogo.oferecidas(lido.conteudo),
            "perfis": _modalidades_por_perfil(lido.conteudo),
            "pontos": revisao.pontos_para_revisao(lido),
            "pergunta_escolhida": request.GET.get("pergunta", ""),
            "perfil_escolhido": request.GET.get("perfil", ""),
            "modalidade_escolhida": request.GET.get("modalidade", ""),
        }
    )
    codigo = request.GET.get("pergunta", "").strip()
    if codigo:
        try:
            pagina["resposta"] = respostas.responder(
                lido,
                codigo,
                perfil=request.GET.get("perfil") or None,
                modalidade=request.GET.get("modalidade") or None,
            )
        except catalogo.ParametroRecusado as recusa:
            pagina["recusa"] = str(recusa)
    return render(request, "interface/duvidas.html", pagina)
