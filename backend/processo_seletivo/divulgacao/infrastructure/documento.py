"""O resultado divulgado como documento oficial — o terceiro a entrar pela mesma costura.

`Composicao` acumula e `render_documento` pagina, e a costura já sustentava dois documentos: o
Edital e o comprovante de inscrição. O terceiro entra pelo mesmo lugar, com `_tabela` para a lista.
Nenhuma biblioteca nova, nenhum motor de layout (T-007).

**Nada aqui consulta banco.** A função recebe os bytes já compostos — o mesmo objeto que virou
`conteudo_publico` — e devolve bytes. É o que torna a correspondência entre a página e o documento
uma consequência da origem comum, e não uma coincidência a conferir (FR-064).

**Determinismo.** Não há data de criação embutida nem identificador aleatório: a mesma composição
produz sempre os mesmos bytes, e é isso que permite publicar o resumo do documento e esperar que
ele confira. O instante impresso é `publicado_em`, que é um fato passado — usar o relógio da
geração faria o mesmo resultado produzir arquivos diferentes a cada download.
"""

from processo_seletivo.publicacoes.infrastructure.pdf import (
    ALTURA_DO_BRASAO,
    ANTES_DE_LINHA,
    CENTRO,
    CORPO_ATO,
    CORPO_NOTA,
    CORPO_SECAO,
    CORPO_TEXTO,
    DIREITA,
    ESQUERDA,
    NEGRITO,
    ORGAO,
    Composicao,
    _tabela,
    render_documento,
)
from processo_seletivo.shared.canonical import canonical_sha256

ENTRE_SECOES = 12.0
RECUO_DO_VALOR = 118.0
# O valor sobe para a linha do rótulo, como no comprovante: um par não precisa da grade de uma
# tabela, e a grade traria fios que este documento não usa.
SUBIR_PARA_A_LINHA = -11.5


def render_resultado_pdf(conteudo: dict) -> bytes:
    """O documento do resultado divulgado, a partir dos bytes que a página também lê."""
    cabecalho = conteudo["cabecalho"]
    composicao = Composicao()
    _timbre(composicao, cabecalho)
    _identificacao(composicao, cabecalho)
    _lista(composicao, conteudo["posicoes"])
    _autoridade(composicao, cabecalho)
    _integridade(composicao, conteudo)
    return render_documento(
        composicao,
        identificacao=f"{cabecalho['edital']} · {cabecalho['marco']}",
    )


def _timbre(composicao, cabecalho):
    composicao.espaco(ALTURA_DO_BRASAO - 10)
    for indice, linha in enumerate(ORGAO):
        composicao.escrever(
            linha, tamanho=CORPO_TEXTO, alinhamento=CENTRO, antes=0.0 if indice else 4.0
        )
    # O título já vem resolvido do conteúdo: "Resultado preliminar — Professor de Matemática".
    # Montá-lo aqui faria o documento e a página nomearem o mesmo ato de dois jeitos.
    composicao.escrever(
        cabecalho["titulo"].upper(),
        tamanho=CORPO_ATO,
        fonte=NEGRITO,
        antes=16,
        alinhamento=CENTRO,
    )


def _identificacao(composicao, cabecalho):
    """Processo, Edital, marco, natureza e o ato de origem — o que o documento afirma ser.

    O ato de origem entra com o seu instante: é ele que liga a divulgação à decisão que ela
    divulga, e sem ele o documento afirmaria uma ordem sem dizer de onde ela veio (FR-063).
    """
    with composicao.bloco(moldura=True):
        composicao.espaco(4.0)
        for rotulo, valor in (
            ("PROCESSO", cabecalho["processo"]),
            ("EDITAL", cabecalho["edital"]),
            ("PERFIL", cabecalho["perfil"]),
            ("MARCO", cabecalho["marco"]),
            ("NATUREZA", cabecalho["natureza_rotulo"]),
            # **A causa da retificação, quando existe** (FR-088). Sem ela, o documento de uma
            # divulgação que corrige outra afirmava uma ordem nova sem dizer que corrigia nada —
            # e a página, que lê os mesmos bytes, já dizia.
            ("RETIFICAÇÃO", _retificacao(cabecalho)),
            ("ATO DE ORIGEM", f"emitido em {_instante(cabecalho['ato']['emitido_em'])}"),
            ("PUBLICADO EM", _instante(cabecalho["publicado_em"])),
        ):
            if valor:
                _par(composicao, rotulo, valor)
        composicao.espaco(4.0)


def _retificacao(cabecalho):
    """ "Em razão do julgamento do recurso REC-…, decidido em DD/MM/AAAA às HHhMM" — ou vazio.

    Vazio some da moldura: `_identificacao` só imprime o par que tem valor, e uma linha
    "RETIFICAÇÃO —" numa primeira divulgação afirmaria que houve o que não houve.
    """
    causa = cabecalho.get("retificacao") or {}
    if not causa.get("recurso"):
        return ""
    return (
        f"Em razão do julgamento do recurso {causa['recurso']}, "
        f"decidido em {_instante(causa['quando'])}"
    )


def _par(composicao, rotulo, valor):
    composicao.escrever(rotulo, tamanho=CORPO_NOTA, antes=4.5)
    composicao.escrever(valor, tamanho=CORPO_TEXTO, recuo=RECUO_DO_VALOR, antes=SUBIR_PARA_A_LINHA)


def _lista(composicao, posicoes):
    composicao.escrever(
        "Resultado", tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ENTRE_SECOES, junto=True
    )
    if not posicoes:
        composicao.escrever(
            "Nenhum participante recebeu posição neste marco.",
            tamanho=CORPO_TEXTO,
            antes=ANTES_DE_LINHA + 3,
        )
        return
    _tabela(
        composicao,
        ["Posição", "Candidato", "Protocolo", "Modalidade", "Pontuação"],
        [
            [
                _posicao(item),
                item["candidato"],
                item["protocolo"],
                item["modalidade"] or "—",
                item["pontuacao"] or "—",
            ]
            for item in posicoes
        ],
        recuo=0.0,
        alinhamentos=[CENTRO, ESQUERDA, ESQUERDA, ESQUERDA, DIREITA],
    )


def _posicao(item):
    """`3º (compartilhada)` — o empate residual dito em texto, e não por marca visual (FR-014)."""
    return f"{item['posicao']}º (compartilhada)" if item["compartilhada"] else f"{item['posicao']}º"


def _autoridade(composicao, cabecalho):
    """Quem assinou — nome e cargo, e nunca o identificador (FR-063).

    `signatario_id` é dado de vínculo, não de leitura: ele existe para a auditoria responder quem
    assinou, e imprimi-lo devolveria ao documento o UUID que a `007` tirou dele.
    """
    composicao.espaco(ENTRE_SECOES)
    composicao.escrever(
        cabecalho["signatario_nome"], tamanho=CORPO_TEXTO, fonte=NEGRITO, alinhamento=CENTRO
    )
    composicao.escrever(
        cabecalho["signatario_cargo"], tamanho=CORPO_NOTA, alinhamento=CENTRO, antes=2.0
    )


def _integridade(composicao, conteudo):
    """O resumo criptográfico do conteúdo divulgado — o que torna o documento conferível.

    É o mesmo `conteudo_publico_hash` que a publicação gravou, porque é calculado sobre o mesmo
    objeto. Quem recebe o papel pode compará-lo com o do sistema e saber que nada foi alterado
    (FR-011, SC-004).
    """
    composicao.espaco(ENTRE_SECOES)
    composicao.regua()
    composicao.escrever(
        f"SHA-256 do conteúdo divulgado: {canonical_sha256(conteudo)}",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA + 3,
    )
    composicao.escrever(
        "Este documento reproduz o conteúdo divulgado na data e hora indicadas. O resumo acima é "
        "calculado sobre esse conteúdo: a comissão o compara com o do sistema para confirmar que "
        "nada foi alterado.",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
    )


def _instante(texto: str) -> str:
    """`18/10/2026, às 17h42` — o instante já congelado, escrito como um ato o escreve.

    Lê o texto ISO gravado no conteúdo, e **não** o relógio: reformatar a partir de agora faria o
    documento mudar de conteúdo entre duas gerações do mesmo ato.

    **Convertido para o fuso da instituição antes de formatado**, pelo mesmo motivo que o
    comprovante da 009 já converte: `humano.instante` escreve o que recebe, e o conteúdo carrega o
    instante em UTC. Sem a conversão, a mesma publicação sai `às 11h14` na página — que passa pelo
    filtro `date`, e esse localiza — e `às 14h14` aqui. Três horas de diferença entre a página e o
    documento, justamente no dado que o documento existe para provar: quando o resultado foi
    divulgado. E o erro cresce perto da meia-noite, onde ele muda também o **dia**.

    O determinismo continua valendo: a conversão é do texto congelado para um fuso fixo, e não uma
    leitura do relógio — o mesmo conteúdo produz sempre os mesmos bytes.
    """
    from django.utils import timezone
    from django.utils.dateparse import parse_datetime

    from processo_seletivo.publicacoes.infrastructure import humano

    momento = parse_datetime(texto or "")
    if momento is None:
        return texto or "—"
    return humano.instante(timezone.localtime(momento) if timezone.is_aware(momento) else momento)


__all__ = ["render_resultado_pdf"]
