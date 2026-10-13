"""O despacho dos avisos: a quarta situação em que o sistema envia mensagem (`FR-084` da `010`).

**É o único lugar dos avisos que chama o servidor de correio**, e o módulo que
`tests/test_situacoes_de_mensagem.py` declara como a quarta situação. A `FR-084` foi revisada em
2026-10-09 para admiti-la, com as redações anteriores preservadas: o aviso complementar vinculado a
ato oficial, **sem efeito nenhum** sobre prazo, classificação, situação ou direito.

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
from django.core.mail import EmailMessage, get_connection
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

    orfas = list(TentativaDeEnvio.objects.filter(resultado__isnull=True))
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
    return len(orfas)


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


def _iniciar(destinatario, numero):
    """Passo 5.1: sob a trava do aviso, confere a interrupção e grava o início — já confirmado.

    Devolve a tentativa, ou `None` quando o aviso foi interrompido desde a seleção. O `UNIQUE` de
    `(destinatario, numero)` é a última porta: se outra inserção da mesma tentativa existisse, a
    gravação colidiria em vez de duplicar (`R-002`).
    """
    from processo_seletivo.avisos.models import InterrupcaoDoAviso, TentativaDeEnvio

    with transaction.atomic():
        travar_o_aviso(destinatario.aviso_id)
        if InterrupcaoDoAviso.objects.filter(aviso_id=destinatario.aviso_id).exists():
            return None
        return TentativaDeEnvio.objects.create(
            destinatario=destinatario, numero=numero, iniciada_em=timezone.now()
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
    mensagem = EmailMessage(
        subject=assunto,
        body=corpo,
        from_email=remetente,
        to=[destinatario.endereco],
        headers=dict(CABECALHOS),
        connection=conexao,
    )
    codificacao = mensagem.encoding or settings.DEFAULT_CHARSET
    sanitize_address(destinatario.endereco, codificacao)
    # O remetente vazio só existe fora de produção, que recusa subir sem `DEFAULT_FROM_EMAIL`.
    if mensagem.from_email:
        sanitize_address(mensagem.from_email, codificacao)
    mensagem.message()
    return mensagem


def _registrar(tentativa, classificacao):
    from processo_seletivo.avisos.models import ResultadoDaTentativa

    with transaction.atomic():
        ResultadoDaTentativa.objects.create(
            tentativa=tentativa,
            resultado=classificacao.resultado,
            registrado_em=timezone.now(),
            detalhe_tecnico=classificacao.detalhe,
        )


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
                tentativa = _iniciar(destinatario, numero)
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
                _registrar(tentativa, classificacao)
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
    "Resumo",
    "TRAVA_DO_DESPACHO",
    "despachar",
    "travar_o_aviso",
]
