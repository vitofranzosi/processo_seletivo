"""O que o sistema aceita como documento do candidato — e como ele recusa o que não aceita.

Duas regras, e nenhuma além: é PDF, e cabe no limite. O resto que se poderia querer aqui — OCR,
conferência de conteúdo, antivírus, extração — está fora de escopo por decisão declarada, e a
recusa em implementá-lo é o que mantém esta camada pequena o bastante para ser confiável.

**A recusa ensina.** Um arquivo que o celular produziu ao fotografar um documento é o caso mais
provável de todos, e "arquivo inválido" não diz à pessoa o que fazer com ele. Reconhecer as
assinaturas de imagem custa uma tabela e transforma um beco numa instrução (FR-047).
"""

import hashlib

from processo_seletivo.shared.api.problems import DomainError

ASSINATURA_PDF = b"%PDF-"
BLOCO = 64 * 1024

# As assinaturas que um celular produz ao fotografar ou capturar tela. Não é catálogo de formatos:
# é a lista do que se sabe explicar. O que não estiver aqui recebe a recusa genérica, que continua
# dizendo o que era esperado.
IMAGENS = (
    (b"\xff\xd8\xff", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"GIF87a", "GIF"),
    (b"GIF89a", "GIF"),
    (b"RIFF", "WebP"),
    (b"\x00\x00\x00", "HEIC"),
)


def _primeiros_bytes(arquivo, quantos=16) -> bytes:
    posicao = arquivo.tell() if hasattr(arquivo, "tell") else 0
    arquivo.seek(0)
    cabecalho = arquivo.read(quantos)
    arquivo.seek(posicao)
    return cabecalho


def _formato_de_imagem(cabecalho: bytes) -> str:
    for assinatura, nome in IMAGENS:
        if cabecalho.startswith(assinatura):
            return nome
        # HEIC e MP4 declaram o tipo no quarto byte em diante; a assinatura fixa não basta.
        if nome == "HEIC" and cabecalho[4:8] == b"ftyp":
            return "HEIC"
    return ""


def aceitar(arquivo, *, nome_original: str, limite_em_bytes: int) -> None:
    """Recusa o que não é PDF ou não cabe — com a frase que resolve, não com a que informa.

    A extensão é conferida **e** o conteúdo, porque renomear um arquivo é a coisa mais fácil do
    mundo e a extensão sozinha não diz nada sobre o que está dentro (FR-045).
    """
    if arquivo.size > limite_em_bytes:
        raise DomainError(
            "file_too_large",
            f"O arquivo tem {_megabytes(arquivo.size)} e o limite é "
            f"{_megabytes(limite_em_bytes)}. Reduza o tamanho e envie novamente.",
            422,
        )
    if arquivo.size == 0:
        raise DomainError("file_empty", "O arquivo está vazio.", 422)
    cabecalho = _primeiros_bytes(arquivo)
    if cabecalho.startswith(ASSINATURA_PDF):
        if not nome_original.lower().endswith(".pdf"):
            raise DomainError(
                "file_extension_mismatch",
                "O conteúdo é PDF, mas o nome do arquivo não termina em .pdf. "
                "Renomeie o arquivo e envie novamente.",
                422,
            )
        return
    imagem = _formato_de_imagem(cabecalho)
    if imagem:
        raise DomainError(
            "file_is_an_image",
            f"Este arquivo é uma imagem ({imagem}), e não um PDF — é o que o celular produz ao "
            "fotografar um documento. Converta a imagem em PDF e envie novamente.",
            422,
        )
    raise DomainError(
        "file_not_pdf",
        "O arquivo enviado não é um PDF. Envie o documento em PDF.",
        422,
    )


def resumo(arquivo) -> str:
    """SHA-256 do conteúdo recebido, lido em blocos.

    Em blocos porque o arquivo pode ter dez megabytes e carregá-lo inteiro em memória para
    calcular um resumo seria pagar o preço da leitura duas vezes — e por candidato.
    """
    digest = hashlib.sha256()
    posicao = arquivo.tell() if hasattr(arquivo, "tell") else 0
    arquivo.seek(0)
    for bloco in iter(lambda: arquivo.read(BLOCO), b""):
        digest.update(bloco)
    arquivo.seek(posicao)
    return digest.hexdigest()


def _megabytes(quantidade: int) -> str:
    return f"{quantidade / (1024 * 1024):.1f} MB".replace(".", ",")


def tamanho_legivel(quantidade: int) -> str:
    """`184320` vira `180 KB`.

    O tamanho vai para o comprovante porque é o segundo sinal de que o arquivo certo chegou: o
    nome pode coincidir entre duas versões do mesmo documento, o tamanho quase nunca. Quem
    confere, confere os dois — e o resumo criptográfico decide quando os dois baterem.
    """
    if quantidade < 1024:
        return f"{quantidade} bytes"
    if quantidade < 1024 * 1024:
        return f"{round(quantidade / 1024)} KB"
    return _megabytes(quantidade)
