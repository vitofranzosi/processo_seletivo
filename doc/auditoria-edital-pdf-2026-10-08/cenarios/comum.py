"""Infra comum aos cenários da auditoria do PDF: atores, unidade, autoridade, publicação, extração.

Tudo pelos comandos de aplicação reais (os mesmos do seed_demo), num banco isolado
(ps_auditoria_pdf). Dados fictícios, marcados como DEMONSTRAÇÃO.
"""

import hashlib
import uuid
from datetime import timedelta
from pathlib import Path

from django.utils import timezone

from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.editais.application.requerimento import atualizar_requerimento_de_matricula
from processo_seletivo.editais.application.teto import atualizar_teto_de_inscricoes
from processo_seletivo.processos.application.commands import create_process_with_first_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import (
    homologate_edital,
    publish_edital,
    submit_edital,
)
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.application.autoridades import cadastrar as cadastrar_autoridade
from processo_seletivo.unidades.application.sincronizacao import ler as ler_unidades
from processo_seletivo.unidades.application.sincronizacao import sincronizar as sincronizar_unidades
from processo_seletivo.unidades.domain.nomes import GERIR as GERIR_AUTORIDADES

SAIDA = Path(
    "/private/tmp/claude-501/-Users-saymoncastro-Projetos-processo-seletivo--claude-worktrees-"
    "auditoria-edital-pdf-d33731/fba18c90-9168-4aeb-8300-d572628e7dd7/scratchpad/pdfs"
)
SAIDA.mkdir(parents=True, exist_ok=True)
ESCOPO = "cefor"


def ator(subject, *permissoes):
    return Actor(subject, ESCOPO, frozenset(permissoes))


ELABORADOR = ator("ana.elaboradora", "processo:criar", "edital:elaborar", "edital:submeter")
HOMOLOGADOR = ator("bruno.homologador", "edital:homologar")
PUBLICADOR = ator("carla.publicadora", "edital:publicar")


def uid(prefixo, n):
    """UUID determinístico por cenário — legível na depuração, único no banco."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"auditoria-pdf:{prefixo}:{n}"))


def autoridade(chave, cargo, nome="", ato=""):
    sincronizar_unidades(ler_unidades())
    hoje = timezone.now().astimezone(ZONA).date()
    return cadastrar_autoridade(
        actor=ator("gabriel.gestor", GERIR_AUTORIDADES),
        cargo=cargo,
        nome=nome,
        ato_de_nomeacao=ato,
        inicio_vigencia=hoje - timedelta(days=365),
        idempotency_key=f"auditoria-pdf-autoridade-{chave}",
        correlation_id="auditoria-pdf",
    )


def criar(codigo, titulo_processo, numero, ano, titulo, descricao):
    processo, _ = create_process_with_first_edital(
        actor=ELABORADOR,
        data={
            "institutionalCode": codigo,
            "title": titulo_processo,
            "firstEdital": {"number": numero, "year": ano, "title": titulo, "description": descricao},
        },
        idempotency_key=f"auditoria-pdf-{codigo}-{numero}",
        correlation_id="auditoria-pdf",
    )
    return Edital.objects.get(processo=processo)


def elaborar(edital, *, profiles, schedule, stages, sections, documents, draw_method=None):
    from processo_seletivo.editais.api.serializers import EditalDraftSerializer

    entrada = {"profiles": profiles, "schedule": schedule, "stages": stages, "sections": sections,
               "documentRequirements": documents}
    if draw_method is not None:
        entrada["drawMethod"] = draw_method
    serializer = EditalDraftSerializer(data=entrada)
    if not serializer.is_valid():
        raise SystemExit(f"rascunho recusado pelo serializer: {serializer.errors}")
    dados = serializer.validated_data
    profiles, schedule = dados["profiles"], dados["schedule"]
    stages, sections = dados.get("stages"), dados.get("sections")
    documents, draw_method = dados.get("documentRequirements"), dados.get("drawMethod")
    replace_draft(
        actor=ELABORADOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        profiles=profiles,
        schedule=schedule,
        stages=stages,
        sections=sections,
        document_requirements=documents,
        draw_method=draw_method,
        correlation_id="auditoria-pdf",
    )
    edital.refresh_from_db()
    return edital


def requerimento(edital, momento, declaracao):
    atualizar_requerimento_de_matricula(
        actor=ELABORADOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        momento=momento,
        declaracao=declaracao,
        correlation_id="auditoria-pdf",
    )
    edital.refresh_from_db()


def teto(edital, valor):
    atualizar_teto_de_inscricoes(
        actor=ELABORADOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        teto=valor,
        correlation_id="auditoria-pdf",
    )
    edital.refresh_from_db()


def anexos(edital, rotulos, vinculos=None):
    """Os Anexos pelo modelo, como o seed_demo (a coleção fica fora do replace_draft)."""
    from processo_seletivo.editais.models.anexos import AnexoEdital, ArtefatoAnexo
    from processo_seletivo.editais.models.documentos import DocumentoExigido

    criados = {}
    for ordem, rotulo in enumerate(rotulos, 1):
        conteudo = b"%PDF-1.4\n% anexo de demonstracao " + str(ordem).encode() + b"\n%%EOF\n"
        artefato = ArtefatoAnexo.objects.create(
            bytes=conteudo,
            tamanho=len(conteudo),
            document_hash=hashlib.sha256(conteudo).hexdigest(),
            nome_original=f"anexo-{ordem}.pdf",
            enviado_por="ana.elaboradora",
            enviado_em=timezone.now(),
        )
        criados[ordem] = AnexoEdital.objects.create(
            edital=edital, rotulo=rotulo, order=ordem, artefato=artefato
        )
    for chave, ordem in (vinculos or {}).items():
        DocumentoExigido.objects.filter(edital=edital, key=chave).update(anexo=criados[ordem])
    edital.refresh_from_db()


def publicar(edital, autoridade_id, rotulo):

    edital, achados, _ = submit_edital(
        actor=ELABORADOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        idempotency_key=f"auditoria-pdf-sub-{edital.id.hex[:12]}",
        correlation_id="auditoria-pdf",
    )
    for achado in achados or []:
        print("  achado na submissão:", getattr(achado, "severity", ""), getattr(achado, "message", achado))
    edital, _ = homologate_edital(
        actor=HOMOLOGADOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Conteúdo conferido (auditoria do PDF).",
        idempotency_key=f"auditoria-pdf-hom-{edital.id.hex[:12]}",
        correlation_id="auditoria-pdf",
    )
    publicacao, _ = publish_edital(
        actor=PUBLICADOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        autoridade_id=autoridade_id,
        reason="Publicação do edital original.",
        idempotency_key=f"auditoria-pdf-pub-{edital.id.hex[:12]}",
        correlation_id="auditoria-pdf",
    )
    return gravar(publicacao, rotulo)


def gravar(publicacao, rotulo):
    from processo_seletivo.publicacoes.models import DocumentoPublicado

    documento = DocumentoPublicado.objects.get(publicacao=publicacao)
    caminho = SAIDA / f"{rotulo}.pdf"
    caminho.write_bytes(bytes(documento.bytes))
    print(f"  {rotulo}: {caminho} ({len(bytes(documento.bytes))} bytes)")
    return caminho


def previa(edital, rotulo):
    """A prévia pelo mesmo caminho da view `previa_documento`."""
    from processo_seletivo.interface.views import unidade_para_o_compositor
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
    from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA, render_edital_pdf
    from processo_seletivo.unidades.application import selectors as unidades_selectors

    unidade = unidades_selectors.exigir_unidade(edital.institution_scope)
    documento = render_edital_pdf(
        edital_snapshot(edital), "", modo=MODO_PREVIA, unidade=unidade_para_o_compositor(unidade)
    )
    caminho = SAIDA / f"{rotulo}.pdf"
    caminho.write_bytes(documento)
    print(f"  {rotulo}: {caminho} ({len(documento)} bytes)")
    return caminho
