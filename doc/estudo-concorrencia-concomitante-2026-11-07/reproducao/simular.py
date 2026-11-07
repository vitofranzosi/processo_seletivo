# Cenários de concomitância sobre o Edital 93/2026 (fictício), num clone descartável.
# A guarda documental do aceite (115) é desligada SÓ neste processo: está fora do escopo do estudo e
# não toca a ocupação nem a fila. Nada mais é alterado.
# Uso: manage.py shell -c "exec(open(ARQ).read()); cenario_a()" — cenários a, b2, c, c2 e d2,
# cada um num clone próprio. Ícaro está eliminado na Etapa, e por isso entra pela regularização.
import itertools
from datetime import timedelta

from django.utils import timezone

from processo_seletivo.convocacao.application import desfechar as mod_desfechar
from processo_seletivo.convocacao.application.convocar import convocar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.application.fluxo import convocar_titulares, previa_dos_titulares
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError

mod_desfechar._recusar_inclusao_sem_documentos = lambda convocacao, *, especie, ciencia=None: []

ATOR = Actor("demo.gestor", "cefor", frozenset({"comissao:gerir"}))
_seq = itertools.count(1)
ED = Edital.objects.get(number__in=["93"], year=2026)
PERFIL = "240b7f2c"
LISTAS = {}
for c in Convocacao.objects.filter(edital=ED):
    LISTAS.setdefault(c.lista_id, (c.perfil_id, c.marco_id))
PPI = next(lista for lista in LISTAS if lista and str(lista).startswith("30cdeae3"))
PCD = next(lista for lista in LISTAS if lista and str(lista).startswith("cfed95c1"))
PERFIL_ID, MARCO_ID = LISTAS[None]


def pessoa(primeiro_nome):
    return Inscricao.objects.get(edital=ED, nome__startswith=primeiro_nome).id


def _chave(prefixo):
    return f"estudo-conc-{prefixo}-{next(_seq)}"


def _vigente(nome, lista):
    qs = Convocacao.objects.filter(edital=ED, inscricao_id=pessoa(nome), lista_id=lista)
    for c in qs.order_by("-criado_em"):
        if not c.sucessoras.exists():
            return c
    raise LookupError(nome)


def chamar(nome, lista, especie=""):
    try:
        r = convocar(
            actor=ATOR,
            processo_id=ED.processo_id,
            edital_id=ED.id,
            perfil_id=PERFIL_ID,
            marco_id=MARCO_ID,
            lista_id=lista,
            inscricao_id=pessoa(nome),
            fundamento="Simulação do estudo de concomitância.",
            idempotency_key=_chave("conv"),
            correlation_id="estudo-conc",
            vencimento=timezone.now() + timedelta(days=7),
            especie=especie,
        )
        print(f"  convocar {nome} em {_r(lista)}: OK, espécie {r.get('especie')}")
    except DomainError as e:
        print(f"  convocar {nome} em {_r(lista)}: RECUSA {e.code}: {e.detail}")


def responder(nome, lista, especie):
    c = _vigente(nome, lista)
    try:
        r = desfechar(
            actor=ATOR,
            processo_id=ED.processo_id,
            convocacao_id=c.id,
            especie=especie,
            fundamento="Simulação do estudo de concomitância.",
            idempotency_key=_chave("desf"),
            correlation_id="estudo-conc",
        )
        seg = r.get("apuracaoSeguinte") or {}
        pend = r.get("apuracaoPendente")
        print(
            f"  {especie} de {nome} em {_r(lista)}: OK; apuração seguinte do mesmo recorte: "
            f"{ {k: seg.get(k) for k in ('publicadas', 'efetivas', 'ocupadas')} if seg else pend }"
        )
    except DomainError as e:
        print(f"  {especie} de {nome} em {_r(lista)}: RECUSA {e.code}: {e.detail}")


def apurar(lista, motivo="Reapuração do estudo"):
    try:
        r = emitir_apuracao(
            actor=ATOR,
            processo_id=ED.processo_id,
            edital_id=ED.id,
            perfil_id=PERFIL_ID,
            marco_id=MARCO_ID,
            lista_id=lista,
            idempotency_key=_chave("apu"),
            correlation_id="estudo-conc",
            motivo=motivo,
        )
        print(
            f"  apurar {_r(lista)}: {r['publicadas']}/{r['efetivas']}/{r['ocupadas']} (pub/efet/ocup)"
        )
    except DomainError as e:
        print(f"  apurar {_r(lista)}: RECUSA {e.code}: {e.detail}")


def titulares(lista):
    p = previa_dos_titulares(edital=ED, perfil_id=PERFIL_ID, marco_id=MARCO_ID, lista_id=lista)
    nomes = [x["nome"].split()[0] for x in p["pessoas"]]
    print(f"  prévia 'Convocar titulares' em {_r(lista)}: {nomes}")
    if not nomes or p["impedimento"]:
        print(f"    impedimento: {p['impedimento']}")
        return
    try:
        convocar_titulares(
            actor=ATOR,
            processo_id=ED.processo_id,
            edital_id=ED.id,
            perfil_id=PERFIL_ID,
            marco_id=MARCO_ID,
            lista_id=lista,
            alcance_confirmado=p["assinatura"],
            idempotency_key=_chave("tit"),
            vencimento=timezone.now() + timedelta(days=7),
        )
        print("    gesto confirmado: OK")
    except DomainError as e:
        print(f"    gesto: RECUSA {e.code}: {e.detail}")


def _r(lista):
    return {None: "AMPLA", PPI: "PPI", PCD: "PcD"}.get(lista, str(lista))


def cenario_a():
    """Helena: desistiu na ampla; a PPI a propõe como titular. O que acontece se seguirmos."""
    print("A. Continuação do caso Helena")
    apurar(PPI, "Reapurar depois da desistência na ampla")
    titulares(PPI)
    responder("Helena", PPI, "ACEITE")
    apurar(PPI, "Depois do aceite de Helena na PPI")


def cenario_c():
    """Ícaro desiste na PcD; a ampla o alcança e o propõe."""
    print("C. Desistência na reservada não alcança a ampla")
    responder("Gael", PCD, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", PCD)
    responder("Ícaro", PCD, "DESISTENCIA_EXPRESSA")
    responder("Davi", None, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", None)


def cenario_b2():
    """Ícaro regulariza pela PcD (passa a ocupá-la) e depois é alcançado e aceita pela ampla."""
    print("B2. Dupla ocupação: regulariza na PcD, aceita na ampla")
    responder("Gael", PCD, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", PCD)
    responder("Ícaro", PCD, "REGULARIZACAO")
    responder("Davi", None, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", None)
    responder("Ícaro", None, "ACEITE")
    apurar(PCD, "Depois do aceite de Ícaro na ampla")


def cenario_c2():
    """Ícaro regulariza pela PcD, depois desiste na PcD; a ampla ainda o chama."""
    print("C2. Desistência na reservada, depois de ocupar, não alcança a ampla")
    responder("Gael", PCD, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", PCD)
    responder("Ícaro", PCD, "REGULARIZACAO")
    responder("Ícaro", PCD, "INERCIA")
    responder("Davi", None, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", None)


def cenario_d2():
    """Ícaro regulariza e aceita pela ampla primeiro; a PcD o pula (o caminho que funciona)."""
    print("D2. Ordem inversa: ampla primeiro")
    responder("Davi", None, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", None)
    responder("Ícaro", None, "REGULARIZACAO")
    responder("Gael", PCD, "DESISTENCIA_EXPRESSA")
    chamar("Ícaro", PCD)
    apurar(PCD, "Depois da desistência de Gael")
