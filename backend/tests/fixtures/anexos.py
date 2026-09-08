"""Anexos do Edital para os testes (020).

Os Anexos não viajam no payload do rascunho — a coleção fica fora do `replace_draft`, porque bytes
não fazem a viagem de ida e volta de um POST de formulário (020, R-006). Por isso a fixture os cria
pelas linhas, entre a gravação do rascunho e a submissão, que é onde o autor de verdade os cria.

O PDF é mínimo e **determinístico**: dois testes que pedem o mesmo conteúdo recebem os mesmos bytes
e, portanto, o mesmo resumo — que é o que permite afirmar, num teste de coexistência, que dois
resumos distintos vieram de conteúdos distintos, e não do acaso.
"""

import hashlib

from django.utils import timezone

from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo

ANEXO = {
    "A": "00000000-0000-0000-0000-000000000901",
    "B": "00000000-0000-0000-0000-000000000902",
}


def pdf_de_teste(marca: str = "A") -> bytes:
    """Bytes que começam com a assinatura de PDF, porque é o que o domínio confere."""
    return b"%PDF-1.4\n% anexo de teste " + marca.encode("utf-8") + b"\n%%EOF\n"


def criar_artefato(*, marca="A", congelado=False, nome="anexo.pdf"):
    conteudo = pdf_de_teste(marca)
    return ArtefatoAnexo.objects.create(
        bytes=conteudo,
        tamanho=len(conteudo),
        document_hash=hashlib.sha256(conteudo).hexdigest(),
        nome_original=nome,
        enviado_por="preparador",
        enviado_em=timezone.now(),
        congelado_em=timezone.now() if congelado else None,
    )


def criar_anexo(edital, *, identificador=None, rotulo="ANEXO I — REQUERIMENTO", order=1, marca="A"):
    """`identificador` nulo deixa o modelo gerar o seu — só quem precisa citá-lo no teste o fixa."""
    campos = {} if identificador is None else {"id": identificador}
    return AnexoEdital.objects.create(
        edital=edital,
        rotulo=rotulo,
        order=order,
        artefato=criar_artefato(marca=marca),
        **campos,
    )
