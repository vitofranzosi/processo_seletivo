"""Três rascunhos com documentos exigidos, para o inventário ver a barra de progresso (092).

    DB_NAME=ps_inventario_092 uv run python manage.py shell < preparar_rascunhos.py

A barra de `portal/_documentos.html` era o único `style=""` do portal, e só aparece no rascunho de
uma seleção com prazo aberto que pede documento. O seed do inventário só tem inscrição enviada. Este
roteiro abre, pela mesma função da view `inscrever`, um rascunho para três candidatas numa seleção
aberta, e registra documento em nenhum, em parte e em todos os obrigatórios — 0%, um valor do meio e
100% na barra.

O documento entra por `bulk_create`, como na memória "Mesa com documentos no demo": a página só lê a
linha (nome, tamanho, data), e o arquivo não é aberto. Rode no banco-modelo do inventário, antes de
copiá-lo para as passadas.
"""

import hashlib
import uuid

from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.portal import identidade as identidade_do_candidato
from processo_seletivo.portal.views import _documentos, abrir_inscricao
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError

CANDIDATAS = ("clara@exemplo.test", "daniel@exemplo.test", "elisa@exemplo.test")


def perfis_abertos():
    for versao in selectors.selecoes_publicas():
        for perfil in versao.content.get("profiles", []):
            yield versao, perfil


def abrir(email):
    registro = CandidateIdentity.objects.get(credenciais__email_como_informado=email)
    identidade = identidade_do_candidato.contrato_de(registro)
    for versao, perfil in perfis_abertos():
        try:
            inscricao = abrir_inscricao(
                identidade=identidade,
                edital_id=versao.edital_id,
                profile_id=perfil["id"],
                correlation_id="inventario-092",
            )
        except DomainError:
            continue
        documentos = _documentos(versao.content, inscricao)
        if documentos["total"] >= 2:
            return inscricao, documentos
    raise SystemExit(f"nenhuma seleção aberta com dois documentos para {email}")


for quantos, email in zip((0, 1, None), CANDIDATAS, strict=True):
    inscricao, documentos = abrir(email)
    obrigatorias = [linha for linha in documentos["linhas"] if linha["obrigatorio"]]
    alvo = obrigatorias if quantos is None else obrigatorias[:quantos]
    conteudo = b"%PDF-1.4 inventario 092"
    DocumentoSubmetido.objects.bulk_create(
        [
            DocumentoSubmetido(
                id=uuid.uuid4(),
                inscricao=inscricao,
                requirement_id=linha["id"],
                arquivo=f"inventario-092/{inscricao.id}/{linha['id']}.pdf",
                nome_original=f"{linha['nome'][:40]}.pdf",
                tamanho=len(conteudo),
                content_hash=hashlib.sha256(conteudo).hexdigest(),
                uploaded_at=timezone.now(),
            )
            for linha in alvo
        ]
    )
    print(email, inscricao.id, f"{len(alvo)} de {documentos['total']}")
