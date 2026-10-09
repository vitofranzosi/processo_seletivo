"""Os atalhos dos testes da `066`: o resultado publicado, a prévia e a confirmação, como na tela.

**Funções, e não fixtures** — a regra que `tests/fixtures/corte.py` registra: importar uma fixture
de outro módulo a redefine no importador, e o `F811` acusa; importar uma função comum, não.
"""

from processo_seletivo.avisos.application import destinatarios, previa
from processo_seletivo.avisos.application.confirmar import (
    confirmar_aviso_da_chamada,
    confirmar_aviso_do_resultado,
)
from processo_seletivo.avisos.domain import nomes
from tests.conftest import ator_institucional

PUBLICADORA = ator_institucional("publicadora-aviso", nomes.PERMISSAO, "resultado:publicar")

ASSUNTO = "Processo Seletivo Ifes — Nova publicação disponível"
CORPO = (
    "Olá, {nome_do_candidato}.\n\n"
    "Foi publicado o resultado {natureza_do_resultado} da etapa {etapa}, do {perfil}, "
    "no {edital}.\n\nConsulte a sua situação: {area_do_candidato}"
)


def enderecos(edital, publicacoes=()):
    """Os links absolutos que a view monta com `build_absolute_uri`."""
    return {
        "pagina": f"https://selecoes.exemplo.test/selecoes/{edital.id}/",
        "area": "https://selecoes.exemplo.test/selecoes/inscricoes/",
        "publicacao": {
            str(p.id): f"https://selecoes.exemplo.test/selecoes/resultados/{p.id}/"
            for p in publicacoes
        },
    }


def avisar_resultado(
    edital,
    marco_id,
    *,
    ator=PUBLICADORA,
    natureza=nomes.PRELIMINAR,
    chave="avisar-066",
    assunto=ASSUNTO,
    corpo=CORPO,
    justificativa="",
    assinatura=None,
):
    """Prévia e confirmação, na ordem da tela: a assinatura sai da prévia e volta no POST."""
    universo = destinatarios.universo_do_resultado(
        edital=edital, marco_id=marco_id, natureza=natureza, reenvio=bool(justificativa)
    )
    motivo = nomes.REENVIO_JUSTIFICADO if justificativa else nomes.PRIMEIRO_AVISO
    return confirmar_aviso_do_resultado(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        marco_id=marco_id,
        natureza=natureza,
        assunto=assunto,
        corpo=corpo,
        assinatura=assinatura or previa.assinatura(universo, motivo=motivo),
        enderecos=enderecos(edital, universo.publicacoes),
        idempotency_key=chave,
        correlation_id="teste-066",
        justificativa=justificativa,
    )


def avisar_chamada(
    edital,
    marco_id,
    comunicacao_id,
    *,
    ator,
    agora,
    lista_id=None,
    chave="avisar-chamada-066",
    assunto=ASSUNTO,
    corpo="Olá, {nome_do_candidato}. Saiu uma nova chamada do {perfil}: {referencia_da_publicacao}",
    justificativa="",
):
    universo = destinatarios.universo_da_chamada(
        edital=edital,
        marco_id=marco_id,
        lista_id=lista_id,
        comunicacao_id=comunicacao_id,
        agora=agora,
    )
    motivo = nomes.REENVIO_JUSTIFICADO if universo.ja_avisado else nomes.PRIMEIRO_AVISO
    return confirmar_aviso_da_chamada(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        marco_id=marco_id,
        lista_id=lista_id,
        comunicacao_id=comunicacao_id,
        assunto=assunto,
        corpo=corpo,
        assinatura=previa.assinatura(universo, motivo=motivo),
        enderecos=enderecos(edital),
        idempotency_key=chave,
        correlation_id="teste-066",
        justificativa=justificativa,
    )


def engordar(publicacao, quantos):
    """Inscrições consideradas na publicação, gravadas em lote: o cenário que a fixture não faz.

    São linhas novas, e não alterações: a `SituacaoDivulgada` é append-only, e acrescentar a ela é o
    que a publicação faz.
    """
    from django.utils import timezone

    from processo_seletivo.divulgacao.models import SituacaoDivulgada
    from processo_seletivo.inscricoes.models import Inscricao

    agora = timezone.now()
    inscricoes = Inscricao.objects.bulk_create(
        Inscricao(
            identity_subject=f"cand:orcamento-{indice}",
            edital=publicacao.edital,
            profile_id=publicacao.perfil_id,
            nome=f"Pessoa {indice}",
            email=f"pessoa{indice}@exemplo.test",
            protocolo=f"ORC-{indice:05d}",
            created_at=agora,
        )
        for indice in range(quantos)
    )
    SituacaoDivulgada.objects.bulk_create(
        SituacaoDivulgada(
            publicacao=publicacao,
            inscricao=inscricao,
            situacao=SituacaoDivulgada.Situacao.CLASSIFICADA,
            posicao=100 + indice,
        )
        for indice, inscricao in enumerate(inscricoes)
    )
