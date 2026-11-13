"""O despacho dos avisos: a quarta e a quinta situações em que o sistema envia mensagem (`FR-084`).

**É o único lugar dos avisos que chama o servidor de correio**, e o módulo que
`tests/test_situacoes_de_mensagem.py` declara como a quarta situação. A `FR-084` foi revisada em
2026-10-09 para admiti-la, com as redações anteriores preservadas: o aviso complementar vinculado a
ato oficial, **sem efeito nenhum** sobre prazo, classificação, situação ou direito.

**A quinta situação sai daqui também** (134, FR-4619). A `FR-084` foi revisada em 2026-11-08 para o
aviso de pendência documental, que o gesto de quem confere grava como aviso de origem `PENDENCIA`.
O despacho a distingue em dois pontos, e só neles — fila, tentativa antes do envio, indeterminada
que nunca se repete e limite por minuto são os mesmos. **Antes de cada tentativa**, ele relê se a
pendência ainda existe e o prazo ainda corre, e interrompe o aviso que chegaria tarde (FR-4623,
D-011). **Depois**, cada resultado vai também à trilha de auditoria (FR-4621, D-009).

**Fora da requisição, por um comando que o timer roda a cada minuto** (`R-005`). A confirmação grava
e responde; aqui se envia, no máximo `AVISOS_LIMITE_POR_MINUTO` por execução — o limite por minuto
sai do próprio relógio, sem fila e sem worker.

**O contrato que o usuário exigiu, passo a passo** (contracts/despacho.md):

1. **Uma execução por vez**, pela trava consultiva global. `FOR UPDATE` não serve: as tabelas são
   append-only, e a role de runtime não tem o `UPDATE` que o PostgreSQL exige para ele (`R-002`).
2. **Tentativa sem resultado é indeterminada**, e quem a encontra com a trava global sabe que ela é
   de uma execução que morreu. Ela recebe o resultado e nunca é repetida (`FR-1267`).
3. **O início da tentativa é gravado e confirmado antes de o servidor ser chamado** (`R-003`), sob a
   trava do aviso — a mesma que a interrupção toma, e por isso nenhuma tentativa começa depois de
   uma interrupção (`FR-1273`).
4. **A resposta é classificada pela fase** em que veio (`R-004`), e a execução para na primeira
   indeterminada: a conexão está em estado desconhecido.
"""

import hashlib
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail.message import sanitize_address
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.avisos.domain import estado as estado_
from processo_seletivo.avisos.domain import nomes, resposta
from processo_seletivo.avisos.domain.mensagem import CABECALHOS, para_a_pessoa

logger = logging.getLogger("processo_seletivo.avisos")

#: A data da revisão da `FR-084` da `010` que admite esta situação, conferida contra a spec por
#: `tests/test_situacoes_de_mensagem.py`. Constante, e não leitura de `specs/` em tempo de execução,
#: pela mesma razão escrita em `convocacao/application/comunicar.py`: o contêiner de produção não
#: carrega a árvore de documentação.
REVISAO_DA_FR_084_PELA_066 = "2026-10-09"

#: A data da revisão que admite a quinta situação, o aviso de pendência documental (134, FR-4602).
REVISAO_DA_FR_084_PELA_134 = "2026-11-08"

#: A trava da execução, uma constante só: duas execuções do despacho nunca correm juntas.
TRAVA_DO_DESPACHO = int.from_bytes(hashlib.sha256(b"avisos:despacho").digest()[:8], "big") >> 1

ORFA = "a execução anterior terminou sem registrar o resultado"


class ConexaoNaoAbriu(Exception):
    """A sessão com o servidor de correio não se abriu: nada saiu, e a próxima execução tenta."""


@dataclass
class Resumo:
    desabilitado: bool = False
    ocupado: bool = False
    orfas: int = 0
    tentadas: int = 0
    #: Avisos de pendência que o próprio despacho interrompeu antes de enviar (134, FR-4623).
    interrompidos: int = 0
    resultados: dict = field(default_factory=dict)
    avisos: set = field(default_factory=set)
    parou_por: str = ""

    def __str__(self):
        if self.desabilitado:
            return "avisos desabilitados nesta instalação: nada a despachar"
        if self.ocupado:
            return "outra execução do despacho está em curso: nada feito"
        contagem = ", ".join(f"{chave} {valor}" for chave, valor in sorted(self.resultados.items()))
        return (
            f"{self.tentadas} tentativa(s) em {len(self.avisos)} aviso(s)"
            + (f": {contagem}" if contagem else "")
            + (f"; {self.orfas} órfã(s) marcada(s) como indeterminada(s)" if self.orfas else "")
            + (
                f"; {self.interrompidos} aviso(s) de pendência interrompido(s) antes do envio"
                if self.interrompidos
                else ""
            )
            + (f"; parou: {self.parou_por}" if self.parou_por else "")
        )


def _chave_do_aviso(aviso_id):
    return int.from_bytes(hashlib.sha256(f"aviso:{aviso_id}".encode()).digest()[:8], "big") >> 1


def travar_o_aviso(aviso_id):
    """A trava que serializa o início de tentativa e a interrupção do mesmo aviso (`R-002`).

    Fora do PostgreSQL é no-op, e é honesto que seja: o SQLite serializa a escrita inteira.
    """
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [_chave_do_aviso(aviso_id)])


@contextmanager
def _trava_global():
    if connection.vendor != "postgresql":
        yield True
        return
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s)", [TRAVA_DO_DESPACHO])
        obtida = cursor.fetchone()[0]
    try:
        yield obtida
    finally:
        if obtida:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [TRAVA_DO_DESPACHO])


def _marcar_orfas():
    """Passo 2: com a trava global, toda tentativa sem resultado é de uma execução que morreu."""
    from processo_seletivo.avisos.models import ResultadoDaTentativa, TentativaDeEnvio

    orfas = list(
        TentativaDeEnvio.objects.filter(resultado__isnull=True).select_related(
            "destinatario__aviso"
        )
    )
    if orfas:
        agora = timezone.now()
        with transaction.atomic():
            ResultadoDaTentativa.objects.bulk_create(
                ResultadoDaTentativa(
                    tentativa=tentativa,
                    resultado=nomes.INDETERMINADA,
                    registrado_em=agora,
                    detalhe_tecnico=ORFA,
                )
                for tentativa in orfas
            )
            for tentativa in orfas:
                _auditar_o_envio(
                    tentativa.destinatario.aviso, tentativa, nomes.INDETERMINADA, agora
                )
    return len(orfas)


class _Despacho:
    """Quem assina, na trilha, o que o despacho registra: um timer, e não uma pessoa (D-009)."""

    subject = nomes.SUJEITO_DO_DESPACHO

    def __init__(self, institution_scope):
        self.institution_scope = institution_scope


def _auditar_o_envio(aviso, tentativa, resultado, agora):
    """A trilha de um resultado, **só para o aviso de pendência** (134, FR-4621, D-009).

    As origens da `066` registram o envio nas tabelas de tentativa e resultado, e a trilha delas
    continua sem ele. Sem endereço, sem nome e sem o detalhe técnico (FR-1279 da `066`): o aviso, o
    número da tentativa e o resultado bastam para encontrar o resto no registro do aviso.
    """
    if aviso.origem != nomes.PENDENCIA:
        return
    from processo_seletivo.auditoria.application import record_event

    # **Num ponto de salvamento, e não na transação do resultado.** O resultado é o registro do que
    # o servidor de correio respondeu, e a mensagem já saiu: se a trilha falhasse junto, a tentativa
    # ficaria sem resultado e a próxima execução a marcaria indeterminada — uma entrega aceita
    # registrada como dúvida. A falha da trilha vai ao log, e o resultado fica.
    try:
        with transaction.atomic():
            record_event(
                actor=_Despacho(aviso.institution_scope),
                permission="",
                operation=nomes.OPERACAO_ENVIO_DA_PENDENCIA,
                aggregate=aviso,
                now=agora,
                correlation_id=aviso.correlation_id or str(aviso.id),
                reason=f"Tentativa {tentativa.numero} do aviso de pendência: {resultado}.",
                new_state="",
                new_revision=None,
                detalhe={"tentativa": tentativa.numero, "resultado": resultado},
            )
    except Exception:  # noqa: BLE001 — a trilha não desfaz o resultado registrado
        logger.exception(
            "A trilha do envio do aviso de pendência %s, tentativa %s, não foi gravada.",
            aviso.id,
            tentativa.numero,
        )


def _interromper_pelo_despacho(aviso, motivo, agora):
    """O aviso de pendência que chegaria tarde não sai: o despacho o interrompe (FR-4623, D-011).

    **A interrupção da `066`, e não um resultado inventado.** Nenhuma tentativa começa, e a tela do
    aviso o mostra interrompido, com o motivo e o despacho como autor. O gesto seguinte, no mesmo
    dia, não o conta no limite: nada foi enviado.
    """
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.avisos.models import InterrupcaoDoAviso

    interrupcao = InterrupcaoDoAviso.objects.create(
        aviso=aviso,
        motivo=f"Interrompido pelo despacho antes do envio: {motivo}.",
        interrompido_por=nomes.SUJEITO_DO_DESPACHO,
        interrompido_em=agora,
    )
    record_event(
        actor=_Despacho(aviso.institution_scope),
        permission="",
        operation=nomes.OPERACAO_INTERROMPER,
        aggregate=interrupcao,
        now=agora,
        correlation_id=aviso.correlation_id or str(aviso.id),
        reason=f"Aviso de pendência {aviso.id} interrompido antes do envio: {motivo}.",
        new_state="",
        new_revision=None,
    )


def _tentativas(destinatario):
    return [
        estado_.Tentativa(
            t.numero,
            t.iniciada_em,
            getattr(getattr(t, "resultado", None), "resultado", None),
            getattr(getattr(t, "resultado", None), "registrado_em", None),
        )
        for t in sorted(destinatario.tentativas.all(), key=lambda t: t.numero)
    ]


def _selecionar(*, agora, limite):
    """Passo 3: até `limite` destinatários que o despacho pode tentar agora, em ordem."""
    from processo_seletivo.avisos.models import DestinatarioDoAviso

    inicio_da_janela = agora - timedelta(hours=settings.AVISOS_JANELA_DE_DESPACHO_HORAS)
    candidatos = (
        DestinatarioDoAviso.objects.filter(
            aviso__solicitado_em__gt=inicio_da_janela,
            aviso__interrupcao__isnull=True,
            elegibilidade=nomes.ELEGIVEL,
        )
        .exclude(endereco="")
        .select_related("aviso", "inscricao")
        .prefetch_related("tentativas__resultado")
        .order_by("aviso__solicitado_em", "aviso_id", "inscricao__protocolo", "id")
    )
    selecionados = []
    for destinatario in candidatos:
        tentativas = _tentativas(destinatario)
        estado = estado_.estado_do_destinatario(
            elegibilidade=destinatario.elegibilidade,
            endereco=destinatario.endereco,
            tentativas=tentativas,
            interrompido=False,
            solicitado_em=destinatario.aviso.solicitado_em,
            agora=agora,
            max_tentativas=settings.AVISOS_MAX_TENTATIVAS,
            janela_horas=settings.AVISOS_JANELA_DE_DESPACHO_HORAS,
        )
        if estado_.elegivel_ao_despacho(
            estado=estado,
            tentativas=tentativas,
            agora=agora,
            intervalos=settings.AVISOS_INTERVALOS_DE_RETENTATIVA,
            habilitado=True,
        ):
            selecionados.append((destinatario, len(tentativas) + 1))
            if len(selecionados) >= limite:
                break
    return selecionados


def _iniciar(destinatario, numero, resumo):
    """Passo 5.1: sob a trava do aviso, confere a interrupção e grava o início — já confirmado.

    Devolve a tentativa, ou `None` quando o aviso foi interrompido desde a seleção. O `UNIQUE` de
    `(destinatario, numero)` é a última porta: se outra inserção da mesma tentativa existisse, a
    gravação colidiria em vez de duplicar (`R-002`).

    **O aviso de pendência relê a pendência aqui** (134, FR-4623), sob a mesma trava: a regra do
    gesto, para esta pessoa e neste instante. Se ela já não vale, o aviso é interrompido e nada sai.
    """
    from processo_seletivo.avisos.models import InterrupcaoDoAviso, TentativaDeEnvio

    with transaction.atomic():
        travar_o_aviso(destinatario.aviso_id)
        if InterrupcaoDoAviso.objects.filter(aviso_id=destinatario.aviso_id).exists():
            return None
        agora = timezone.now()
        if destinatario.aviso.origem == nomes.PENDENCIA:
            from processo_seletivo.avisos.application.pendencias import motivo_para_nao_enviar

            motivo = motivo_para_nao_enviar(destinatario, agora=agora)
            if motivo:
                _interromper_pelo_despacho(destinatario.aviso, motivo, agora)
                resumo.interrompidos += 1
                return None
        return TentativaDeEnvio.objects.create(
            destinatario=destinatario, numero=numero, iniciada_em=agora
        )


def _mensagem(destinatario, conexao):
    """A mensagem de uma pessoa, preparada e validada **antes** da rede (`R-004`, fase 1).

    Sanear o endereço e montar o MIME aqui faz o `ValueError` de endereço ou codificação acontecer
    onde se sabe que nada saiu. Dentro de `send_messages`, o mesmo erro seria indistinguível de
    uma falha no meio da conversa.
    """
    aviso = destinatario.aviso
    assunto, corpo = para_a_pessoa(
        assunto=aviso.assunto, corpo=aviso.corpo, nome_do_candidato=destinatario.inscricao.nome
    )
    remetente = settings.DEFAULT_FROM_EMAIL or None
    # **Um destinatário só, sem cópia e sem cópia oculta** (`FR-1271`): nenhum endereço é exposto a
    # outra pessoa.
    mensagem = EmailMultiAlternatives(
        subject=assunto,
        body=corpo,
        from_email=remetente,
        to=[destinatario.endereco],
        headers=dict(CABECALHOS),
        connection=conexao,
    )
    html = _html(assunto, corpo, origem=aviso.origem)
    if html:
        mensagem.attach_alternative(html, "text/html")
    codificacao = mensagem.encoding or settings.DEFAULT_CHARSET
    sanitize_address(destinatario.endereco, codificacao)
    # O remetente vazio só existe fora de produção, que recusa subir sem `DEFAULT_FROM_EMAIL`.
    if mensagem.from_email:
        sanitize_address(mensagem.from_email, codificacao)
    mensagem.message()
    return mensagem


def _html(assunto, corpo, *, origem):
    """A forma HTML do texto congelado, ou `""` quando ela não se compõe.

    **O texto puro é o aviso**: é ele que está gravado, e é ele que sai sempre. O HTML só o mostra
    em blocos, na moldura comum (`shared/correio.py`), sem frase que o texto não tenha. Por isso a
    falha dele não é falha do aviso: a mensagem sai só com o texto, e o registro técnico diz por
    quê. Deixá-la subir faria uma moldura quebrada virar `ValueError` de preparação — e o aviso
    não sairia por uma razão que nada tem a ver com ele.
    """
    from processo_seletivo.shared import correio

    try:
        return correio.html_do_aviso(
            assunto=assunto,
            corpo=corpo,
            estado="pendencia" if origem == nomes.PENDENCIA else "informacao",
        )
    except Exception:  # noqa: BLE001 — sem a forma HTML, o texto sai sozinho, como antes
        logger.exception("O aviso saiu sem a forma HTML, que não se compôs.")
        return ""


def _registrar(tentativa, classificacao, *, aviso):
    from processo_seletivo.avisos.models import ResultadoDaTentativa

    with transaction.atomic():
        agora = timezone.now()
        ResultadoDaTentativa.objects.create(
            tentativa=tentativa,
            resultado=classificacao.resultado,
            registrado_em=agora,
            detalhe_tecnico=classificacao.detalhe,
        )
        _auditar_o_envio(aviso, tentativa, classificacao.resultado, agora)


def despachar(*, limite=None):
    """Uma execução do despacho. Devolve o resumo; `ConexaoNaoAbriu` quando nada pôde sair."""
    resumo = Resumo()
    if not getattr(settings, "AVISOS_AOS_CANDIDATOS", False):
        resumo.desabilitado = True
        return resumo
    limite = limite or settings.AVISOS_LIMITE_POR_MINUTO
    with _trava_global() as obtida:
        if not obtida:
            resumo.ocupado = True
            return resumo
        resumo.orfas = _marcar_orfas()
        selecionados = _selecionar(agora=timezone.now(), limite=limite)
        if not selecionados:
            return resumo
        conexao = get_connection()
        try:
            conexao.open()
        except Exception as erro:
            # **Nenhuma tentativa registrada**: nada de mensagem foi ao servidor (`R-004`, fase 0).
            logger.exception("O despacho de avisos não abriu a conexão com o servidor de correio.")
            raise ConexaoNaoAbriu(f"{type(erro).__name__}: a conexão não se abriu") from erro
        try:
            for destinatario, numero in selecionados:
                tentativa = _iniciar(destinatario, numero, resumo)
                if tentativa is None:
                    continue
                resumo.tentadas += 1
                resumo.avisos.add(destinatario.aviso_id)
                try:
                    mensagem = _mensagem(destinatario, conexao)
                except (ValueError, UnicodeError) as erro:
                    classificacao = resposta.na_preparacao(erro)
                else:
                    try:
                        enviadas = conexao.send_messages([mensagem])
                    except Exception as erro:  # noqa: BLE001 — toda falha vira resultado registrado
                        classificacao = resposta.do_envio(erro=erro)
                    else:
                        classificacao = resposta.do_envio(enviadas=enviadas)
                _registrar(tentativa, classificacao, aviso=destinatario.aviso)
                resumo.resultados[classificacao.resultado] = (
                    resumo.resultados.get(classificacao.resultado, 0) + 1
                )
                if classificacao.para_a_execucao:
                    resumo.parou_por = classificacao.detalhe
                    break
        finally:
            try:
                conexao.close()
            except Exception:  # noqa: BLE001 — fechar mal não desfaz o que foi registrado
                logger.warning("O despacho de avisos não fechou a conexão de correio com limpeza.")
    # O resumo leva números e ids de aviso, e nunca endereço ou nome (`FR-1279`).
    logger.info("Despacho de avisos: %s.", resumo)
    return resumo


__all__ = [
    "ConexaoNaoAbriu",
    "REVISAO_DA_FR_084_PELA_066",
    "REVISAO_DA_FR_084_PELA_134",
    "Resumo",
    "TRAVA_DO_DESPACHO",
    "despachar",
    "travar_o_aviso",
]
