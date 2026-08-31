"""O canal público: quem é de fora encontra a seleção e decide se quer participar.

Duas telas na entrega 1 — a vitrine e o detalhe —, e as duas leem **exclusivamente** a versão
consolidada vigente (FR-011). Nenhuma view daqui consulta `PerfilVaga`, `ModalidadeConcorrencia`
ou qualquer tabela de elaboração: o que o candidato lê é o que foi publicado, e é isso que torna
reproduzível, depois, sob qual regra cada pessoa se inscreveu.

O que **ainda não** existe aqui, e é da entrega 2: situação das inscrições e convite por vaga.
Os dois dependem da designação do período, que o Edital ainda não sabe fazer. A US1 se completa
lá; esta entrega é a fatia navegável dela.
"""

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError

FUTURA, ABERTA, ENCERRADA, SEM_PERIODO = "futura", "aberta", "encerrada", "sem-periodo"

# A mesma tradução que o documento publicado usa, e pelo mesmo motivo: `UNLIMITED` é forma
# interna, e forma interna não é o que se lê numa página de oportunidade.
RESERVA = {
    "NONE": "",
    "LIMITED": "com cadastro reserva",
    "UNLIMITED": "com cadastro reserva ilimitado",
}


def _periodo(conteudo, agora):
    """A situação das inscrições, derivada do Evento designado — e de mais nada.

    Três estados e uma ausência. A ausência não é um quarto estado da inscrição: é o Edital que
    não recebe inscrição por este sistema, e a página simplesmente não fala de prazo.

    Nada aqui procura texto em `type` ou `description`. O Evento designado se diz designado, e a
    marca é dado publicado — foi essa a decisão que tornou a situação uma leitura, e não um
    palpite sobre o que alguém digitou.
    """
    designado = next(
        (evento for evento in conteudo.get("schedule") or [] if evento.get("isRegistrationPeriod")),
        None,
    )
    if designado is None:
        return {"estado": SEM_PERIODO, "inicio": None, "fim": None}
    inicio = parse_datetime(designado.get("startAt") or "")
    fim = parse_datetime(designado.get("endAt") or "") if designado.get("endAt") else None
    if inicio is not None and agora < inicio:
        estado = FUTURA
    elif fim is not None and agora > fim:
        estado = ENCERRADA
    else:
        # Sem término declarado, o período segue aberto: é o que o Evento diz, e inventar um
        # fechamento seria o sistema criando prazo que o Edital não fixou.
        estado = ABERTA
    return {"estado": estado, "inicio": inicio, "fim": fim}


def _selecao(versao):
    """O que a página precisa saber, tirado do conteúdo publicado e de mais nada.

    A unidade vem do Edital porque escopo institucional é identificação do ato, não conteúdo
    normativo — não está no snapshot e não deveria estar.
    """
    conteudo = versao.content
    return {
        "edital_id": versao.edital_id,
        "periodo": _periodo(conteudo, timezone.now()),
        "processo_codigo": conteudo.get("processoCode", ""),
        "processo_titulo": conteudo.get("processoTitle", ""),
        "unidade": versao.edital.institution_scope.upper(),
        "numero": conteudo.get("number", ""),
        "ano": conteudo.get("year", ""),
        "titulo": conteudo.get("title", ""),
        "descricao": conteudo.get("description", ""),
        "publicacao_id": versao.source_publication_id,
    }


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


def vitrine(request):
    """As seleções que estão publicadas, sem nada de gestão e sem pedir identificação."""
    selecoes = [_selecao(versao) for versao in selectors.selecoes_publicas()]
    return render(request, "portal/vitrine.html", {"selecoes": selecoes})


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
    contexto["perfis"] = [_perfil(perfil) for perfil in versao.content.get("profiles") or []]
    return render(request, "portal/selecao.html", contexto)
