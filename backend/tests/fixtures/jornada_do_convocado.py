"""Os cenários da jornada do convocado (118), montados pelas fixtures da `115` e da `059`.

As letras são as da revisão de UX de 04/11/2026 (`doc/revisao-ux-jornada-do-convocado-2026-11-04/`)
e as do plano da `118`: A–K, e os de controle B2, L, M, N, K2, G0, N0 e M0. O roteiro de captura do
PR #375 montava os mesmos cenários dentro de um arquivo descartável; aqui eles moram onde o teste de
interface, o do navegador e as capturas da `118` os alcançam, e cada um diz o que prova.

**Um cenário por certame**, e o prefixo é a letra: dois cenários de convocação no mesmo certame
colidem na fila e na idempotência.

**O prazo vencido sem esperar.** `convocar` recusa vencimento anterior ao envio, e o roteiro do #375
dormia 25 segundos. Aqui o vencimento é de um minuto, e quem lê o cenário vencido o lê com o relógio
adiantado (`DEPOIS_DO_PRAZO`), como os testes de prazo da `115` já fazem.
"""

from dataclasses import dataclass
from datetime import timedelta
from unittest import mock

from django.utils import timezone

from processo_seletivo.convocacao.domain import nomes
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    _documento,
)
from tests.fixtures.edital import identificador

CINCO_DIAS = timedelta(days=5)
UM_MINUTO = timedelta(minutes=1)
DEPOIS_DO_PRAZO = timedelta(days=2)
OPCIONAL = identificador(1181, 0)
FOTO = identificador(1182, 0)
TITULO = identificador(1183, 0)

MOTIVO_DO_HISTORICO = "Falta a página 2."
MOTIVO_DA_RESIDENCIA = "Envie conta de água, luz ou telefone dos últimos 3 meses."


def documentos_com_opcional():
    """Um obrigatório e um facultativo, os dois na convocação (cenários L e K2)."""
    return [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        _documento(
            CERTIDAO, "certidao", "Certidão de nascimento ou casamento", 2, momento="AT_CALL"
        ),
        _documento(
            HISTORICO,
            "historico",
            "Histórico escolar do ensino médio",
            3,
            momento="AT_CALL",
            instrucao="Todas as páginas, em arquivo único.",
        ),
        _documento(
            OPCIONAL,
            "declaracao-opcional",
            "Declaração de interesse em auxílio estudantil",
            4,
            momento="AT_CALL",
            obrigatorio=False,
        ),
    ]


def documentos_em_numero(quantos):
    """Uma chamada com `quantos` itens pedidos — para provar que o custo não cresce com eles."""
    todos = [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        *[d for d in cenarios.documentos_do_aluno() if d["moment"] == "AT_CALL"],
        _documento(FOTO, "foto", "Fotografia 3x4", 6, momento="AT_CALL"),
        _documento(TITULO, "titulo", "Título de eleitor", 7, momento="AT_CALL"),
    ]
    na_convocacao = [d for d in todos if d["moment"] == "AT_CALL"]
    return [todos[0], *na_convocacao[:quantos]]


def publicar_com_requerimento(api_client, manager_headers, process_payload, *, draft=None):
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=draft,
        antes_de_submeter=declarar("AT_CALL"),
    )


@dataclass
class Cenario:
    letra: str
    edital: object
    pessoa: object
    convocacao: object
    # O relógio com que o cenário se lê: `None` é o de agora; o vencido se lê depois do prazo.
    adiantar: timedelta | None = None

    def relogio(self):
        """O contexto em que as telas do cenário se leem."""
        if self.adiantar is None:
            return _sem_efeito()
        return mock.patch("django.utils.timezone.now", return_value=timezone.now() + self.adiantar)


class _sem_efeito:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def certame(fx, *, prefixo, documentos=None, requerimento=False, documentos_da_inscricao=None):
    extras = {}
    if requerimento:
        extras["publicar"] = publicar_com_requerimento
    if documentos is not None:
        extras["documentos"] = documentos
    from tests.fixtures.convocacao import montar_cenario_da_convocacao

    return montar_cenario_da_convocacao(
        fx.gestor,
        fx.api_client,
        fx.manager_headers,
        fx.process_payload,
        prefixo=prefixo,
        documentos_da_inscricao=documentos_da_inscricao,
        **extras,
    )


def convocar(cenario, gestor, *, letra, vencimento_em=CINCO_DIAS, comunicar=True):
    edital = cenario[0]
    kwargs = {}
    if vencimento_em is not None:
        kwargs["vencimento"] = timezone.now() + vencimento_em
    pessoa, convocacao = cenarios.convocar_primeira(
        cenario, gestor, chave=f"convocar-{letra}-118", **kwargs
    )
    if comunicar:
        cenarios.comunicar(edital, gestor, convocacao, chave=f"comunicar-{letra}-118")
    return pessoa, convocacao


def enviar_requerimento(pessoa):
    from processo_seletivo.requerimentos.application import preencher
    from tests.fixtures.requerimento import campos_de_exemplo

    preencher.abrir_rascunho(inscricao=pessoa)
    preencher.gravar(inscricao=pessoa, dados=campos_de_exemplo(), expected_revision=None)
    versao = preencher._conteudo(pessoa)
    return preencher.enviar(
        identidade=cenarios.Titular(pessoa),
        inscricao=pessoa,
        versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content),
        aceite=True,
    )


def abrir_rascunho(pessoa):
    from processo_seletivo.requerimentos.application import preencher

    return preencher.abrir_rascunho(inscricao=pessoa)


def encerrar_o_processo(edital, estado="ENCERRADO"):
    """O Processo em estado final, sem passar pelo comando — o que se prende é o estado (029)."""
    from processo_seletivo.processos.models import ProcessoSeletivo

    ProcessoSeletivo.objects.filter(editais__id=edital.id).update(status=estado)


# --- Os cenários --------------------------------------------------------------------------------


def montar(letra, fx):
    """O cenário `letra`, pronto para ser lido pelas telas do candidato."""
    return CENARIOS[letra](fx)


def _a(fx):
    """A — documentos sem Requerimento, nada enviado."""
    c = certame(fx, prefixo="j118-a", documentos=cenarios.documentos_do_aluno())
    pessoa, conv = convocar(c, fx.gestor, letra="a")
    return Cenario("A", c[0], pessoa, conv)


def _b(fx):
    """B — Requerimento sem documentos, a preencher: o caminho direto continua."""
    c = certame(fx, prefixo="j118-b", requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="b")
    return Cenario("B", c[0], pessoa, conv)


def _b2(fx):
    """B2 — Requerimento sem documentos, já enviado: o enviado continua a ação principal."""
    cenario = _b(fx)
    enviar_requerimento(cenario.pessoa)
    cenario.letra = "B2"
    return cenario


def _c1(fx):
    """C1 — documentos e Requerimento, nada enviado."""
    c = certame(fx, prefixo="j118-c", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="c")
    return Cenario("C1", c[0], pessoa, conv)


def _c2(fx):
    """C2 — os dois, só o Requerimento enviado: a falsa conclusão de hoje."""
    cenario = _c1(fx)
    enviar_requerimento(cenario.pessoa)
    cenario.letra = "C2"
    return cenario


def _d(fx):
    """D — o certificado aproveitado da inscrição, sem conferência."""
    c = certame(
        fx,
        prefixo="j118-d",
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
    )
    pessoa, conv = convocar(c, fx.gestor, letra="d")
    return Cenario("D", c[0], pessoa, conv)


def _e(fx):
    """E — os quatro enviados pelo portal, aguardando conferência."""
    c = certame(fx, prefixo="j118-e", documentos=cenarios.documentos_do_aluno())
    pessoa, conv = convocar(c, fx.gestor, letra="e")
    for req in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA):
        cenarios.apresentar(pessoa, conv, req, corpo=f"e-{req}".encode())
    return Cenario("E", c[0], pessoa, conv)


def _f(fx):
    """F — um pendente e um a enviar, com o prazo em curso, e o Requerimento enviado."""
    c = certame(fx, prefixo="j118-f", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="f")
    for req in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO):
        cenarios.apresentar(pessoa, conv, req, corpo=f"f-{req}".encode())
    cenarios.conferir(fx.gestor, conv, CERTIDAO, "CONFORME", chave="f-c1-118")
    cenarios.conferir(fx.gestor, conv, CERTIFICADO_DO_MEDIO, "CONFORME", chave="f-c2-118")
    cenarios.conferir(
        fx.gestor, conv, HISTORICO, "PENDENTE", chave="f-p1-118", motivo=MOTIVO_DO_HISTORICO
    )
    enviar_requerimento(pessoa)
    return Cenario("F", c[0], pessoa, conv)


def _g(fx):
    """G — um pendente, o prazo vencido sem desfecho, o Requerimento nunca enviado."""
    c = certame(fx, prefixo="j118-g", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="g", vencimento_em=UM_MINUTO)
    cenarios.apresentar(pessoa, conv, HISTORICO, corpo=b"g-historico")
    cenarios.conferir(
        fx.gestor, conv, HISTORICO, "PENDENTE", chave="g-p1-118", motivo=MOTIVO_DO_HISTORICO
    )
    return Cenario("G", c[0], pessoa, conv, adiantar=DEPOIS_DO_PRAZO)


def _h(fx):
    """H — os quatro conferidos conformes e o Requerimento enviado, sem desfecho."""
    c = certame(fx, prefixo="j118-h", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="h")
    for n, req in enumerate((CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)):
        cenarios.apresentar(pessoa, conv, req, corpo=f"h-{req}".encode())
        cenarios.conferir(fx.gestor, conv, req, "CONFORME", chave=f"h-c{n}-118")
    enviar_requerimento(pessoa)
    return Cenario("H", c[0], pessoa, conv)


def _i1(fx):
    """I1 — o aceite registrado, depois de tudo conferido."""
    cenario = _h(fx)
    cenarios.desfechar(
        cenario.edital,
        fx.gestor,
        cenario.convocacao,
        nomes.ACEITE,
        chave="i1-desfecho-118",
        fundamento="Documentação conferida e conforme.",
    )
    cenario.letra = "I1"
    return cenario


def _i2(fx):
    """I2 — o indeferimento, com itens não enviados e um recebido sem conferência."""
    c = certame(fx, prefixo="j118-i2", documentos=cenarios.documentos_do_aluno())
    pessoa, conv = convocar(c, fx.gestor, letra="i2")
    cenarios.apresentar(pessoa, conv, CERTIDAO, corpo=b"i2-certidao")
    cenarios.apresentar(pessoa, conv, HISTORICO, corpo=b"i2-historico")
    cenarios.conferir(
        fx.gestor, conv, HISTORICO, "PENDENTE", chave="i2-p1-118", motivo=MOTIVO_DO_HISTORICO
    )
    cenarios.desfechar(
        c[0],
        fx.gestor,
        conv,
        nomes.INDEFERIMENTO,
        chave="i2-desfecho-118",
        fundamento="Documentação exigida na convocação não atendida.",
    )
    return Cenario("I2", c[0], pessoa, conv)


def _j(fx):
    """J — a pendência registrada sobre item que nunca recebeu arquivo."""
    c = certame(fx, prefixo="j118-j", documentos=cenarios.documentos_do_aluno())
    pessoa, conv = convocar(c, fx.gestor, letra="j")
    for req in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO):
        cenarios.apresentar(pessoa, conv, req, corpo=f"j-{req}".encode())
    cenarios.conferir(
        fx.gestor, conv, RESIDENCIA, "PENDENTE", chave="j-p1-118", motivo=MOTIVO_DA_RESIDENCIA
    )
    return Cenario("J", c[0], pessoa, conv)


def _k(fx):
    """K — a comunicação ainda não enviada: o prazo não começou a correr."""
    c = certame(fx, prefixo="j118-k", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="k", comunicar=False)
    return Cenario("K", c[0], pessoa, conv)


def _k2(fx):
    """K2 — o prazo não iniciado, com um pendente, uma tarefa e um opcional."""
    c = certame(fx, prefixo="j118-k2", documentos=documentos_com_opcional())
    pessoa, conv = convocar(c, fx.gestor, letra="k2", comunicar=False)
    cenarios.apresentar(pessoa, conv, HISTORICO, corpo=b"k2-historico")
    cenarios.conferir(
        fx.gestor, conv, HISTORICO, "PENDENTE", chave="k2-p1-118", motivo=MOTIVO_DO_HISTORICO
    )
    return Cenario("K2", c[0], pessoa, conv)


def _l(fx):
    """L — só um facultativo sem envio, e nenhuma tarefa."""
    c = certame(fx, prefixo="j118-l", documentos=documentos_com_opcional())
    pessoa, conv = convocar(c, fx.gestor, letra="l")
    for req in (CERTIDAO, HISTORICO):
        cenarios.apresentar(pessoa, conv, req, corpo=f"l-{req}".encode())
    return Cenario("L", c[0], pessoa, conv)


def _m(fx):
    """M — o Processo encerrado, a chamada em aberto e o prazo correndo; um item recebido."""
    c = certame(fx, prefixo="j118-m", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="m")
    cenarios.apresentar(pessoa, conv, CERTIDAO, corpo=b"m-certidao")
    encerrar_o_processo(c[0])
    return Cenario("M", c[0], pessoa, conv)


def _m0(fx):
    """M0 — sem documento, o Processo encerrado, o Requerimento na convocação não enviado."""
    c = certame(fx, prefixo="j118-m0", requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="m0")
    encerrar_o_processo(c[0])
    return Cenario("M0", c[0], pessoa, conv)


def _n(fx, *, rascunho=False):
    """N — o indeferimento, com documento, e o Requerimento pedido na convocação nunca enviado."""
    c = certame(fx, prefixo="j118-n", documentos=cenarios.documentos_do_aluno(), requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="n")
    if rascunho:
        abrir_rascunho(pessoa)
    cenarios.apresentar(pessoa, conv, CERTIDAO, corpo=b"n-certidao")
    cenarios.desfechar(
        c[0],
        fx.gestor,
        conv,
        nomes.INDEFERIMENTO,
        chave="n-desfecho-118",
        fundamento="Documentação exigida na convocação não atendida.",
    )
    return Cenario("N", c[0], pessoa, conv)


def _n0(fx, *, rascunho=False):
    """N0 — o mesmo, sem documento na chamada."""
    c = certame(fx, prefixo="j118-n0", requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="n0")
    if rascunho:
        abrir_rascunho(pessoa)
    cenarios.desfechar(
        c[0],
        fx.gestor,
        conv,
        nomes.INDEFERIMENTO,
        chave="n0-desfecho-118",
        fundamento="Requerimento de Matrícula não enviado.",
    )
    return Cenario("N0", c[0], pessoa, conv)


def _g0(fx, *, rascunho=False):
    """G0 — sem documento, o Requerimento pedido na convocação e não enviado, o prazo vencido."""
    c = certame(fx, prefixo="j118-g0", requerimento=True)
    pessoa, conv = convocar(c, fx.gestor, letra="g0", vencimento_em=UM_MINUTO)
    if rascunho:
        abrir_rascunho(pessoa)
    return Cenario("G0", c[0], pessoa, conv, adiantar=DEPOIS_DO_PRAZO)


def _sem_nada(fx):
    """Controle — Edital sem documento na convocação e sem Requerimento (SC-1123)."""
    c = certame(fx, prefixo="j118-zero")
    pessoa, conv = convocar(c, fx.gestor, letra="zero")
    return Cenario("sem-documento-nem-requerimento", c[0], pessoa, conv)


CENARIOS = {
    "A": _a,
    "B": _b,
    "B2": _b2,
    "C1": _c1,
    "C2": _c2,
    "D": _d,
    "E": _e,
    "F": _f,
    "G": _g,
    "H": _h,
    "I1": _i1,
    "I2": _i2,
    "J": _j,
    "K": _k,
    "K2": _k2,
    "L": _l,
    "M": _m,
    "M0": _m0,
    "N": _n,
    "N0": _n0,
    "G0": _g0,
    "sem-documento-nem-requerimento": _sem_nada,
}


@dataclass
class Montagem:
    """O que as fixtures do `conftest` entregam, junto, para os cenários se montarem."""

    gestor: object
    api_client: object
    manager_headers: object
    process_payload: object
