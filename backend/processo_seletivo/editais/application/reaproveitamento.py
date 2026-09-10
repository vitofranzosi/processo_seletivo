"""Iniciar um Edital a partir da configuração de outro (023).

**A frase que governa**: um Edital anterior pode ser o ponto de partida de um novo Edital; nunca sua
continuação. Reaproveita-se o que descreve como a oferta se organiza; nunca o que aconteceu na
oferta anterior.

Três decisões desta feature moram inteiras aqui, e cada uma existe por um defeito concreto:

**A fonte é a versão vigente, não as tabelas.** A Retificação não reescreve `PerfilVaga`,
`EventoCronograma` e companhia — ela opera sobre o conteúdo canônico. O estado relacional de um
Edital publicado é, portanto, o **do dia da publicação**, e copiá-lo reproduziria em silêncio uma
configuração que não vigora, justamente nos campos que mais se retificam: datas e vagas (D-003).

**A escrita entra por `replace_draft`.** É lá que moram as validações de perfis, cronograma, etapas,
documentos e seções, e a recusa de identidade de outro contêiner. Uma segunda porta para as mesmas
invariantes é o defeito que este repositório mais evita — a `003` já o pagou uma vez (T-004).

**A reserva da chave vem antes das precondições mutáveis.** A operação altera justamente a
precondição que seria conferida: depois da primeira cópia o rascunho não está mais vazio, e checar
isso antes da chave faria toda repetição responder `draft_not_empty` (FR-017a). É a ordem que
`add_edital` já pratica.
"""

import hashlib

from django.core.exceptions import ValidationError
from django.db.models import Q

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.domain.reaproveitamento import (
    converter_valores,
    mapa_de_identidades,
    payload_do_conteudo,
    remapear,
)
from processo_seletivo.editais.models.anexos import AnexoEdital, ArtefatoAnexo
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import (
    effective_version,
    versoes_vigentes,
)
from processo_seletivo.publicacoes.domain.elevacao import elevar
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish as _finish_idempotency
from processo_seletivo.shared.idempotency import reserve

PERMISSAO = "edital:elaborar"
OPERACAO = "REAPROVEITAR_EDITAL"

# As situações em que um Edital serve de origem (D-008). A restrição resolve a autorização sem
# inventar permissão: o conteúdo de um Edital publicado **já é público** — existe consulta pública
# dele —, e seus anexos congelados também o são, porque são norma. Ler para copiar não concede nada
# que o portal já não conceda. Rascunho de terceiro exigiria permissão que ninguém tem hoje, e de
# Edital cancelado não se parte: é ato desfeito.
ORIGENS_ELEGIVEIS = (Edital.Status.PUBLICADO, Edital.Status.ENCERRADO)

# O rótulo que vai para a área da gravação do rascunho. **Não é nome de etapa**, de propósito: a
# trilha usa a área para dizer qual etapa mudou (006, FR-042), e nomear uma afirmaria que alguém a
# compôs. Vazio devolveria o registro indistinguível que aquela decisão veio corrigir.
AREA = "Reaproveitamento de Edital anterior"


def rascunho_vazio(edital) -> bool:
    """Nenhuma das seis coleções da elaboração tem linha.

    A pergunta existe porque `replace_draft` substitui o rascunho inteiro: o que não é reenviado é
    apagado. Oferecer a cópia sobre um Edital já composto destruiria trabalho em silêncio, e nenhum
    diálogo de confirmação compra isso de volta (D-002).
    """
    cronograma = getattr(edital, "cronograma", None)
    return not any(
        (
            edital.perfis.exists(),
            edital.etapas.exists(),
            edital.documentos_exigidos.exists(),
            edital.secoes.exists(),
            edital.anexos.exists(),
            cronograma is not None and cronograma.eventos.exists(),
        )
    )


def _procura_por(termo):
    """A busca por número, ano, título e Processo — os mesmos atributos que a lista mostra.

    `FR-004` pede que a origem seja **localizável** pelos atributos com que ela é identificada, e é
    isso e nada mais: um campo só, sobre o que está na tela. Filtro por situação não entra porque a
    lista já é fechada nas duas elegíveis, e filtro por Processo em separado repetiria o que o texto
    livre já alcança.

    O ano entra por igualdade e só quando o termo é um ano plausível: `year` é inteiro, e comparar
    inteiro por semelhança de texto é conveniência que devolve resultado que ninguém pediu.
    """
    procura = (
        Q(number__icontains=termo)
        | Q(title__icontains=termo)
        | Q(processo__institutional_code__icontains=termo)
        | Q(processo__title__icontains=termo)
    )
    if termo.isdigit() and len(termo) == 4:
        procura |= Q(year=int(termo))
    return procura


def origens_elegiveis(actor, *, excluindo=None, busca=""):
    """Os Editais que podem servir de origem, no escopo do ator.

    Ordenados do mais recente para o mais antigo: quem reaproveita parte, quase sempre, da edição do
    ciclo anterior.
    """
    consulta = (
        Edital.objects.filter(
            institution_scope=actor.institution_scope, status__in=ORIGENS_ELEGIVEIS
        )
        .select_related("processo")
        .order_by("-year", "-number")
    )
    termo = (busca or "").strip()
    if termo:
        consulta = consulta.filter(_procura_por(termo))
    return consulta.exclude(pk=excluindo) if excluindo is not None else consulta


def com_resumo_da_origem(editais, *, at=None):
    """O que cada origem traz, contado **no conteúdo que vigora** (023, FR-004a).

    Contar nas tabelas seria mais barato e estaria errado pela mesma razão que `D-003` fixou a fonte
    da cópia: a Retificação não reescreve `PerfilVaga` e companhia, então um Edital retificado
    anunciaria na lista um número de Perfis que a cópia não traria. A coluna promete o que a
    operação faz — e a única forma de a promessa se manter é contar o mesmo conteúdo que ela copia.

    O conteúdo é elevado antes da contagem, como na cópia: para um degrau antigo a diferença é entre
    ausência e coleção vazia, que dá o mesmo número, mas depender disso seria confiar que nenhum
    degrau futuro renomeie coleção.
    """
    editais = list(editais)
    if not editais:
        return editais
    versoes = versoes_vigentes(edital_ids=[edital.pk for edital in editais], at=at)
    primeira_publicacao = {}
    for edital_id, publicado_em in (
        Publicacao.objects.filter(edital_id__in=[edital.pk for edital in editais])
        .order_by("edital_id", "publication_order")
        .values_list("edital_id", "published_at")
    ):
        primeira_publicacao.setdefault(edital_id, publicado_em)
    for edital in editais:
        versao = versoes.get(edital.pk)
        conteudo = elevar(versao.content) if versao is not None else {}
        edital.resumo = {
            "perfis": len(conteudo.get("profiles") or []),
            "eventos": len(conteudo.get("schedule") or []),
            "etapas": len(conteudo.get("stages") or []),
            "documentos": len(conteudo.get("documentRequirements") or []),
            "anexos": len(conteudo.get("attachments") or []),
        }
        edital.publicado_em = primeira_publicacao.get(edital.pk)
    return editais


def _origem_elegivel(actor, origem_id):
    """`404` indistinguível para inexistente, fora do escopo e inelegível.

    Os três respondem igual porque distinguir já seria informação: dizer "existe, mas você não pode"
    revela a existência a quem não a alcança. É a regra que a gestão aplica em toda parte.

    **`ValidationError` entra na lista**, e não é detalhe: a origem chega de um campo de
    formulário, e `UUIDField` levanta `ValidationError` — que **não** é `ValueError` — para texto
    que não é UUID. Sem ela, enviar o formulário sem escolher nada devolvia 500 em vez da recusa.
    """
    try:
        return origens_elegiveis(actor).get(pk=origem_id)
    except (Edital.DoesNotExist, ValidationError, ValueError, TypeError) as exc:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from exc


def _copiar_anexos(edital, conteudo, mapa, *, actor, now):
    """Artefato próprio, em rascunho, com os bytes do artefato congelado da origem.

    **Não pelos comandos de Anexo** (T-003): cada um abre transação própria, faz `compare_and_swap`
    e grava evento — `N` comandos seriam `N` saltos de revisão e `N` registros para **uma**
    operação.

    **E não compartilhando o artefato congelado** (D-007): `congelado_em` responde ciclo de vida, e
    não nulo significa publicado e imutável por trigger. O rascunho do destino não poderia
    substituir o próprio anexo. Resumo repetido é legítimo — dois artefatos de conteúdo idêntico
    são legítimos por decisão da `020` (FR-011).

    Antes dos Documentos Exigidos, sempre: `attachmentId` é referência a objeto que precisa existir.
    """
    for anexo in conteudo.get("attachments") or []:
        try:
            original = ArtefatoAnexo.objects.get(pk=anexo["artifactId"])
        except (ArtefatoAnexo.DoesNotExist, ValueError, TypeError) as exc:
            raise DomainError(
                "origin_artifact_missing",
                "O Edital de origem referencia um arquivo que não existe mais.",
                409,
            ) from exc
        bytes_do_anexo = bytes(original.bytes)
        artefato = ArtefatoAnexo.objects.create(
            bytes=bytes_do_anexo,
            content_type=original.content_type,
            tamanho=len(bytes_do_anexo),
            document_hash=hashlib.sha256(bytes_do_anexo).hexdigest(),
            nome_original=original.nome_original,
            enviado_por=actor.subject,
            enviado_em=now,
        )
        AnexoEdital.objects.create(
            # A identidade que o mapa reservou: é ela que `documentRequirements[].attachmentId`
            # passou a apontar, e criar com outra deixaria o requisito pendurado.
            id=mapa[str(anexo["id"])],
            edital=edital,
            rotulo=anexo.get("label", ""),
            order=anexo.get("order", 0),
            artefato=artefato,
        )


def reaproveitar_edital(
    *,
    actor,
    edital_id,
    origem_id,
    expected_revision,
    idempotency_key="",
    correlation_id="",
):
    """Copia a configuração vigente da origem para o rascunho vazio do destino.

    Devolve o Edital de destino. Uma transação do começo ao fim: ou o destino recebe tudo, ou nada —
    anexo criado sem o requisito que o usa é conteúdo órfão, e requisito sem o anexo é referência
    pendurada que só a publicação denuncia (FR-017).
    """
    require_permission(actor, PERMISSAO)
    with command_context() as now:
        try:
            edital = (
                Edital.objects.select_for_update()
                .select_related("processo")
                .get(pk=edital_id, institution_scope=actor.institution_scope)
            )
        except Edital.DoesNotExist as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        origem = _origem_elegivel(actor, origem_id)

        # Antes das precondições mutáveis, e não depois (FR-017a).
        idem = reserve(
            actor=actor,
            operation=f"edital:reaproveitar:{edital.pk}",
            key=idempotency_key,
            payload={"origem": str(origem.pk)},
        )
        if idem.result_id:
            return Edital.objects.get(pk=idem.result_id)

        ensure_processo_accepts_changes(edital.processo)
        if edital.status != Edital.Status.EM_ELABORACAO:
            raise DomainError(
                "invalid_state", "Somente Edital em elaboração pode ser editado.", 409
            )
        if edital.revision != expected_revision:
            raise DomainError("stale_revision", "A revisão informada está obsoleta.", 412)
        if not rascunho_vazio(edital):
            raise DomainError(
                "draft_not_empty",
                "Só é possível partir de outro Edital enquanto este não tiver nenhum conteúdo. "
                "Este Edital já tem conteúdo composto.",
                409,
            )

        # **`at=now`, e não o instante que o seletor tomaria sozinho.** `effective_version` chama
        # `timezone.now()` quando não recebe o instante, e a auditoria registra o `now` da abertura
        # do comando: uma vigência programada que começasse no meio da transação faria o evento
        # afirmar um instante anterior à versão que ele diz ter copiado.
        versao = effective_version(edital_id=origem.pk, at=now)
        conteudo = elevar(versao.content)
        mapa = mapa_de_identidades(conteudo)
        _copiar_anexos(edital, conteudo, mapa, actor=actor, now=now)
        payload = payload_do_conteudo(converter_valores(remapear(conteudo, mapa)))
        replace_draft(
            actor=actor,
            edital_id=edital.pk,
            expected_revision=expected_revision,
            profiles=payload["profiles"],
            schedule=payload["schedule"],
            stages=payload["stages"],
            sections=payload["sections"],
            document_requirements=payload["documentRequirements"],
            correlation_id=correlation_id,
            area=AREA,
        )
        edital.refresh_from_db()
        record_event(
            actor=actor,
            permission=PERMISSAO,
            operation=OPERACAO,
            aggregate=edital,
            now=now,
            correlation_id=correlation_id,
            previous_state=edital.status,
            previous_revision=expected_revision,
            # **A versão, e não o Edital.** A Constituição exige que instâncias incorporadas
            # preservem independência *e versão*; um identificador só responde as duas perguntas,
            # porque o Edital deriva da versão por `edital_id`. Guardar número e ano aqui congelaria
            # dado que uma Retificação pode alterar (FR-015a, T-008).
            reason=str(versao.pk),
            idempotency_key=idempotency_key,
        )
        _finish_idempotency(idem, edital, 200)
        return edital
