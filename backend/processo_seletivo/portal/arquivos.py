"""A entrega de um documento ao seu titular — mediada, e nunca por endereço direto.

Nada serve o diretório dos candidatos. Chegar a um arquivo significa passar por aqui, e aqui a
primeira coisa que acontece é a conferência de titularidade: conhecer o identificador não autoriza
(FR-051, FR-071).

`inline` porque o candidato quer **ver** o que enviou, e não baixar de novo o que já tem. E
`no-store`, porque um PDF com dado pessoal no cache do navegador é o mesmo vazamento que a tela.
"""

from tempfile import SpooledTemporaryFile

from django.http import FileResponse

from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.arquivos import BLOCO
from processo_seletivo.shared.http import marcar_como_privada

# Acima disto a cópia verificada vai para o disco em vez da memória. Dez megabytes é o limite de
# um documento, e segurar isso em memória por requisição concorrente seria pagar caro por um caso
# raro; abaixo, a cópia nem toca o disco.
LIMITE_EM_MEMORIA = 2 * 1024 * 1024


def entregar_ao_titular(*, inscricao, identidade, requirement_id, anexo=False):
    exigir_titularidade(inscricao, identidade)
    documento = DocumentoSubmetido.objects.filter(
        inscricao=inscricao, requirement_id=requirement_id
    ).first()
    if documento is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return entregar(documento, anexo=anexo)


def entregar(documento, *, anexo=False, verificado=None):
    """Serve o arquivo — e, quando há cópia verificada, serve **ela**.

    `verificado` é o que fecha a janela entre conferir e entregar: sem ele, quem verifica abre o
    arquivo, calcula o resumo, fecha, e quem entrega abre de novo — e entre as duas aberturas o
    conteúdo pode ter mudado. Os bytes conferidos e os bytes servidos precisam ser os mesmos
    bytes, não o mesmo caminho.
    """
    resposta = FileResponse(
        verificado if verificado is not None else documento.arquivo.open("rb"),
        content_type="application/pdf",
        as_attachment=anexo,
        filename=documento.nome_original,
    )
    return marcar_como_privada(resposta)


def entregar_e_registrar_ao_fim(documento, *, anexo=False, verificado, ao_fim):
    """Serve a cópia verificada e chama `ao_fim()` **só depois do último bloco** (157, FR-6544).

    **A abertura é o acesso ao arquivo vigente** (decisão do usuário de 11/11/2026): o servidor
    autorizou, conferiu o resumo e entregou o arquivo inteiro. `entregar`, acima, devolve a resposta
    e a vista grava a consulta antes de sair o primeiro byte — e o pedido que caía no meio virava
    abertura, e abertura é o que autoriza o "conforme" (FR-3611 da `115`). Aqui o registro mora no
    fim da entrega: se o navegador desiste, o servidor web para de iterar, o gerador é fechado no
    meio, e `ao_fim` nunca roda. Nada disso diz que o navegador mostrou o arquivo, nem que alguém o
    leu: só que ele foi entregue.

    **Um gerador, e não o arquivo.** Com um objeto de arquivo, a `FileResponse` usa o
    `wsgi.file_wrapper` — o `sendfile` do servidor —, que entrega sem passar pelo Python, e o fim da
    entrega ficaria invisível daqui. Os cabeçalhos são os de `entregar`.
    """
    from django.http import StreamingHttpResponse
    from django.utils.http import content_disposition_header

    verificado.seek(0, 2)
    tamanho = verificado.tell()
    verificado.seek(0)

    def blocos():
        try:
            while bloco := verificado.read(BLOCO):
                yield bloco
            ao_fim()
        finally:
            verificado.close()

    resposta = StreamingHttpResponse(blocos(), content_type="application/pdf")
    resposta["Content-Length"] = str(tamanho)
    resposta["Content-Disposition"] = content_disposition_header(
        anexo, documento.nome_original
    )
    return marcar_como_privada(resposta)


#: A frase do arquivo que não está onde o registro diz (117, FR-3695). A mesma em toda tela.
ARQUIVO_INDISPONIVEL = (
    "Arquivo indisponível. O registro do documento existe, mas o arquivo não pôde ser lido. "
    "Registre a ocorrência à presidência."
)


class ArquivoIndisponivel(DomainError):
    """O arquivo que o registro aponta não existe ou não se lê (117, FR-3695).

    **Recusa do domínio, e não erro do servidor.** Antes da `117`, o `FileNotFoundError` de
    `arquivo.open` subia cru e virava 500 sem registro nenhum (§2.9 do diagnóstico): a pessoa via a
    página de falha, e a trilha não sabia que um documento tinha sumido. Como recusa, a página é a
    da área, com 409, e quem chama grava o evento antes de deixá-la subir.
    """

    def __init__(self):
        super().__init__("arquivo_indisponivel", ARQUIVO_INDISPONIVEL, 409)


def copia_verificada(documento):
    """Uma passagem: copia, calcula o resumo sobre o que copiou, e devolve a cópia rebobinada.

    Devolve `(cópia, resumo)`. Quem chama decide o que fazer com a divergência — recusar é
    decisão da camada que sabe quem está perguntando, não desta.

    O arquivo ausente ou ilegível levanta `ArquivoIndisponivel`, com a cópia já fechada (117,
    FR-3695): `OSError` cobre o `FileNotFoundError` e o disco que falha no meio da leitura.
    """
    import hashlib

    digest = hashlib.sha256()
    copia = SpooledTemporaryFile(max_size=LIMITE_EM_MEMORIA)
    try:
        with documento.arquivo.open("rb") as origem:
            for bloco in iter(lambda: origem.read(BLOCO), b""):
                digest.update(bloco)
                copia.write(bloco)
    except OSError as erro:
        copia.close()
        raise ArquivoIndisponivel() from erro
    copia.seek(0)
    return copia, digest.hexdigest()
