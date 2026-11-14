"""O envio do vídeo em partes retomáveis, e a conclusão que o torna vídeo (166, FR-7118 a FR-7126).

**Partes de até 8 MiB**: cabem nos 12 MB do nginx e nos 120 s do gunicorn síncrono, sem mudar nenhum
limite global (research T-002). Cada parte só é aceita no deslocamento que o servidor já recebeu, e
quem retoma pergunta o deslocamento, em vez de reenviar o que chegou.

**A conclusão confere tudo de novo, no servidor** (Constituição, IV): o tamanho, a assinatura do
contêiner, a duração contra o teto, as marcas contra a duração e o resumo contra o do aparelho. O
que a página conferiu antes melhora a experiência, e não é fronteira.

**A titularidade e a disponibilidade são relidas a cada ato**, sob a trava da inscrição: o período
pode ter acabado, a comissão pode ter aberto o vídeo, e a resposta precisa ser a de agora (FR-7152).
"""

import hashlib
import os
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.verificacao.application import disponibilidade
from processo_seletivo.verificacao.domain import conteiner, roteiro
from processo_seletivo.verificacao.models import (
    AberturaDoVideo,
    EnvioDoVideo,
    VideoDaVerificacao,
)

PARTE_MAXIMA = 8 * 1024 * 1024
RECEBIDO = "VIDEO_DA_VERIFICACAO_RECEBIDO"
# A duração no contêiner pode passar da medida pelo aparelho em uma fração: o último quadro e o
# relógio da página não fecham juntos. Um segundo de folga não abre espaço a nada.
_FOLGA_DO_TETO = 1


class ForaDoDeslocamento(Exception):
    """A parte não começa onde o recebido termina; a resposta diz onde retomar (409)."""

    def __init__(self, deslocamento):
        super().__init__(deslocamento)
        self.deslocamento = deslocamento


def _nao_encontrado():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def _recusa(codigo, frase, status=422, campo=""):
    return DomainError(codigo, frase, status, campo=campo)


def _armazenamento():
    from processo_seletivo.inscricoes.storage import ArmazenamentoPrivado

    return ArmazenamentoPrivado()


def caminho(nome: str) -> str:
    """O caminho no disco de um nome do armazenamento privado."""
    return _armazenamento().path(nome)


def contexto_do_titular(*, identidade, inscricao_id, etapa_id, travar=False):
    """`(inscricao, etapa, situacao)` do titular, ou a recusa indistinguível (FR-7110).

    A inscrição de outra pessoa, a que não existe, a Etapa que não admite o vídeo ou não alcança a
    inscrição, e a chave desligada respondem igual: "recurso não encontrado".
    """
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
    from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade
    from processo_seletivo.inscricoes.models import Inscricao

    if not settings.VERIFICACAO_POR_VIDEO:
        raise _nao_encontrado()
    consulta = Inscricao.objects.select_related("edital")
    if travar:
        consulta = consulta.select_for_update(of=("self",))
    inscricao = consulta.filter(pk=inscricao_id).first()
    if inscricao is None:
        raise _nao_encontrado()
    exigir_titularidade(inscricao, identidade)
    try:
        conteudo = conteudo_vigente(inscricao.edital)
    except DomainError as erro:
        raise _nao_encontrado() from erro
    etapa = next(
        (
            item
            for item in conteudo.get("stages") or []
            if isinstance(item, dict) and str(item.get("id")) == str(etapa_id)
        ),
        None,
    )
    situacao = (
        None
        if etapa is None
        else disponibilidade.situacao(inscricao=inscricao, etapa=etapa, conteudo=conteudo)
    )
    if situacao is None:
        raise _nao_encontrado()
    return inscricao, etapa, situacao


def _recusar_se_indisponivel(situacao):
    if situacao.estado == disponibilidade.EM_ANALISE:
        raise _recusa(
            "ja_aberto",
            "A comissão já começou a análise do seu vídeo, e ele não pode mais ser trocado.",
            409,
        )
    if not situacao.pode_enviar:
        raise _recusa(
            "indisponivel",
            "O envio do vídeo não está disponível para esta inscrição agora.",
            409,
        )


def _formato_base(formato) -> str:
    return str(formato or "").split(";")[0].strip().lower()


def _validar_declaracao(*, tamanho, formato, duracao, marcas, versao, maioridade):
    if maioridade is not True:
        raise _recusa(
            "maioridade",
            "Para gravar o vídeo, declare que tem 18 anos ou mais. Quem tem menos de 18 faz a "
            "entrevista ao vivo.",
            campo="maioridade",
        )
    formato = _formato_base(formato)
    if formato not in conteiner.FORMATOS:
        raise _recusa("formato", "O vídeo precisa ser MP4 ou WebM.", campo="formato")
    try:
        tamanho = int(tamanho)
        duracao = Decimal(str(duracao)).quantize(Decimal("0.001"))
    except (TypeError, ValueError, ArithmeticError) as erro:
        raise _recusa("tamanho", "O tamanho ou a duração do vídeo não são números.") from erro
    if tamanho <= 0 or tamanho > settings.VERIFICACAO_POR_VIDEO_LIMITE_BYTES:
        raise _recusa("tamanho", "O vídeo é maior que o permitido.", campo="tamanho")
    if duracao <= 0 or duracao > roteiro.TETO_SEGUNDOS:
        raise _recusa(
            "duracao",
            f"O vídeo pode ter até {roteiro.TETO_SEGUNDOS // 60} minutos.",
            campo="duracao",
        )
    if versao != roteiro.VERSAO:
        raise _recusa("marcas", "O roteiro da gravação mudou. Recarregue a página e grave de novo.")
    try:
        marcas = roteiro.conferir_marcas(marcas, duracao)
    except roteiro.MarcasInvalidas as erro:
        raise _recusa("marcas", f"A gravação não seguiu o roteiro: {erro}.") from erro
    return tamanho, formato, duracao, marcas


def _apagar(nome):
    try:
        os.remove(caminho(nome))
    except FileNotFoundError:
        pass


def iniciar(
    *,
    identidade,
    inscricao_id,
    etapa_id,
    tamanho,
    formato,
    duracao,
    marcas,
    roteiro_versao,
    maioridade,
):
    """Abre o envio; o anterior, incompleto, do mesmo titular para a mesma Etapa é descartado."""
    tamanho, formato, duracao, marcas = _validar_declaracao(
        tamanho=tamanho,
        formato=formato,
        duracao=duracao,
        marcas=marcas,
        versao=roteiro_versao,
        maioridade=maioridade,
    )
    from django.utils import timezone

    with transaction.atomic():
        inscricao, etapa, situacao = contexto_do_titular(
            identidade=identidade, inscricao_id=inscricao_id, etapa_id=etapa_id, travar=True
        )
        _recusar_se_indisponivel(situacao)
        if not situacao.dentro_do_periodo:
            raise _recusa("indisponivel", "O período da verificação não está aberto.", 409)
        anteriores = list(
            EnvioDoVideo.objects.filter(
                edital=inscricao.edital, etapa_id=etapa["id"], inscricao=inscricao
            )
        )
        for anterior in anteriores:
            _apagar(anterior.arquivo)
            anterior.delete()
        identificador = uuid.uuid4()
        nome = f"verificacao/{inscricao.id}/envio-{identificador}.parte"
        os.makedirs(os.path.dirname(caminho(nome)), exist_ok=True)
        open(caminho(nome), "wb").close()
        return EnvioDoVideo.objects.create(
            id=identificador,
            inscricao=inscricao,
            edital=inscricao.edital,
            etapa_id=etapa["id"],
            tamanho=tamanho,
            formato=formato,
            duracao_medida=duracao,
            marcas=marcas,
            roteiro=roteiro_versao,
            declarou_maioridade=True,
            iniciado_em=timezone.now(),
            arquivo=nome,
        )


def _envio_do_titular(*, identidade, inscricao_id, etapa_id, envio_id, travar=False):
    from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade

    if not settings.VERIFICACAO_POR_VIDEO:
        raise _nao_encontrado()
    consulta = EnvioDoVideo.objects.select_related("inscricao", "edital")
    if travar:
        consulta = consulta.select_for_update(of=("self",))
    envio = consulta.filter(pk=envio_id, inscricao_id=inscricao_id, etapa_id=etapa_id).first()
    if envio is None:
        raise _nao_encontrado()
    exigir_titularidade(envio.inscricao, identidade)
    return envio


def consultar(*, identidade, inscricao_id, etapa_id, envio_id):
    """O envio, para a retomada saber de onde continuar (FR-7119)."""
    return _envio_do_titular(
        identidade=identidade, inscricao_id=inscricao_id, etapa_id=etapa_id, envio_id=envio_id
    )


def receber_parte(*, identidade, inscricao_id, etapa_id, envio_id, deslocamento, dados):
    """Acrescenta a parte no deslocamento recebido; devolve o novo deslocamento."""
    if len(dados) > PARTE_MAXIMA:
        raise _recusa("parte", "Cada parte do envio tem no máximo 8 MiB.", 413)
    if not dados:
        raise _recusa("parte", "A parte veio vazia.")
    with transaction.atomic():
        envio = _envio_do_titular(
            identidade=identidade,
            inscricao_id=inscricao_id,
            etapa_id=etapa_id,
            envio_id=envio_id,
            travar=True,
        )
        if deslocamento != envio.recebido:
            raise ForaDoDeslocamento(envio.recebido)
        if envio.recebido + len(dados) > envio.tamanho:
            raise _recusa("tamanho", "O envio passou do tamanho declarado.")
        with open(caminho(envio.arquivo), "r+b") as arquivo:
            arquivo.seek(deslocamento)
            arquivo.write(dados)
            arquivo.truncate()
        envio.recebido += len(dados)
        envio.save(update_fields=["recebido"])
        return envio.recebido


def _resumo_do_arquivo(nome) -> str:
    sha = hashlib.sha256()
    with open(caminho(nome), "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            sha.update(bloco)
    return sha.hexdigest()


def concluir(*, identidade, inscricao_id, etapa_id, envio_id, sha256, correlation_id):
    """Confere o arquivo e grava o vídeo; o envio some. Devolve o `VideoDaVerificacao`."""
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.inscricoes.application.rascunho import ator_do_candidato
    from processo_seletivo.shared.application.commands import command_context

    with command_context() as agora:
        # A inscrição primeiro, e só depois o envio: a ordem das travas é a do `iniciar`, e duas
        # conclusões concorrentes da mesma inscrição se enfileiram aqui (FR-7152).
        inscricao, etapa, situacao = contexto_do_titular(
            identidade=identidade, inscricao_id=inscricao_id, etapa_id=etapa_id, travar=True
        )
        envio = _envio_do_titular(
            identidade=identidade,
            inscricao_id=inscricao_id,
            etapa_id=etapa_id,
            envio_id=envio_id,
            travar=True,
        )
        _recusar_se_indisponivel_na_conclusao(situacao)
        if envio.recebido != envio.tamanho:
            raise _recusa("tamanho", "O envio ainda não chegou inteiro.")
        with open(caminho(envio.arquivo), "rb") as arquivo:
            arquivo.seek(0, 2)
            if arquivo.tell() != envio.tamanho:
                raise _recusa("tamanho", "O arquivo recebido não tem o tamanho declarado.")
            try:
                lido = conteiner.ler(arquivo)
            except conteiner.ConteinerInvalido as erro:
                raise _recusa("formato", "O arquivo enviado não é um vídeo MP4 ou WebM.") from erro
        if lido.formato != envio.formato:
            raise _recusa("formato", "O formato do arquivo não é o que a página declarou.")
        duracao = (
            Decimal(str(lido.duracao)).quantize(Decimal("0.001"))
            if lido.duracao
            else envio.duracao_medida
        )
        if duracao > roteiro.TETO_SEGUNDOS + _FOLGA_DO_TETO:
            raise _recusa("duracao", f"O vídeo pode ter até {roteiro.TETO_SEGUNDOS // 60} minutos.")
        calculado = _resumo_do_arquivo(envio.arquivo)
        if str(sha256 or "").lower() != calculado:
            raise _recusa(
                "resumo",
                "O vídeo chegou diferente do que saiu do seu aparelho. Envie de novo.",
            )
        anterior = situacao.video
        identificador = uuid.uuid4()
        nome = f"verificacao/{inscricao.id}/{identificador}.{conteiner.EXTENSAO[lido.formato]}"
        os.replace(caminho(envio.arquivo), caminho(nome))
        video = VideoDaVerificacao.objects.create(
            id=identificador,
            inscricao=inscricao,
            edital=inscricao.edital,
            etapa_id=etapa["id"],
            arquivo=nome,
            sha256=calculado,
            tamanho=envio.tamanho,
            duracao=duracao,
            formato=lido.formato,
            roteiro=envio.roteiro,
            marcas=envio.marcas,
            declarou_maioridade=True,
            substitui=anterior,
            recebido_em=agora,
        )
        envio.delete()
        record_event(
            actor=ator_do_candidato(identidade, inscricao.edital),
            permission="",
            operation=RECEBIDO,
            aggregate=video,
            now=agora,
            correlation_id=correlation_id,
            reason=(
                f"Vídeo da verificação da autodeclaração recebido na Etapa {etapa['id']}"
                + (f", em troca do {anterior.id}." if anterior else ".")
            ),
            new_state="",
            new_revision=None,
            # O que o servidor conferiu, e nunca o conteúdo (FR-7151).
            detalhe={
                "tamanho": envio.tamanho,
                "duracao": str(duracao),
                "formato": lido.formato,
                "sha256": calculado,
                "substitui": str(anterior.id) if anterior else None,
            },
        )
        return video


def _recusar_se_indisponivel_na_conclusao(situacao):
    """Na conclusão vale a tolerância do período (FR-7126); a abertura continua barrando a troca."""
    if situacao.estado == disponibilidade.EM_ANALISE:
        raise _recusa(
            "ja_aberto",
            "A comissão já começou a análise do seu vídeo, e ele não pode mais ser trocado.",
            409,
        )
    if situacao.estado not in (disponibilidade.PODE_GRAVAR, disponibilidade.RECEBIDO):
        if not (
            situacao.estado == disponibilidade.AO_VIVO
            and situacao.motivo == "periodo"
            and disponibilidade.dentro_da_tolerancia(situacao)
        ):
            raise _recusa(
                "indisponivel",
                "O envio do vídeo não está disponível para esta inscrição agora.",
                409,
            )
    elif not disponibilidade.dentro_da_tolerancia(situacao):
        raise _recusa("indisponivel", "O período da verificação terminou.", 409)


def ha_abertura_da_comissao(video) -> bool:
    return AberturaDoVideo.objects.filter(
        video=video, papel=AberturaDoVideo.Papel.COMISSAO
    ).exists()
