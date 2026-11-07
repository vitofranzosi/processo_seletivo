# Lê o estado de concomitância de um Edital no banco descartável, sem gravar nada.
# Uso: manage.py shell -c "exec(open(ARQ).read()); mostrar('93')"
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors as conv_sel
from processo_seletivo.convocacao.application.fluxo import previa_dos_titulares
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.ocupacao.application import selectors as ocup_sel
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version


def _nomes(ids):
    mapa = {
        str(i.id): (i.nome or "?").split()[0] for i in Inscricao.objects.filter(id__in=list(ids))
    }
    return [mapa.get(str(i), str(i)[:6]) for i in ids]


def _rotulo(versao, lista_id):
    if lista_id is None:
        return "AMPLA"
    for m in versao.content.get("modalities") or versao.content.get("modalidades") or []:
        if str(m.get("id")) == str(lista_id):
            return m.get("code") or m.get("name")
    return str(lista_id)[:8]


def recortes(edital):
    chaves = set()
    for a in ApuracaoDeOcupacao.objects.filter(edital=edital):
        chaves.add((a.perfil_id, a.marco_id, a.lista_id))
    for c in Convocacao.objects.filter(edital=edital):
        chaves.add((c.perfil_id, c.marco_id, c.lista_id))
    return sorted(chaves, key=lambda k: (str(k[0]), str(k[1]), k[2] is not None, str(k[2])))


def mostrar(numero, at=None):
    agora = at or timezone.now()
    for edital in Edital.objects.filter(number__in=[numero, numero.zfill(2)]):
        versao = effective_version(edital_id=edital.id, at=agora)
        print(f"=== Edital {edital.number}/{edital.year} {edital.id}")
        for perfil, marco, lista in recortes(edital):
            print(
                f"--- recorte {_rotulo(versao, lista)} perfil={str(perfil)[:8]} marco={str(marco)[:8]}"
            )
            ap = ocup_sel.apuracao_vigente(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista
            )
            if ap:
                causas = [c["causa"] for c in ocup_sel.causas_de_obsolescencia(ap, at=agora)]
                print(
                    f"  apuração vigente: pub={ap.publicadas} efet={ap.efetivas} ocup={ap.ocupadas} "
                    f"emitida={ap.emitida_em:%d/%m %H:%M} causas={causas}"
                )
            ordem, corte, _ = ocup_sel.progrediram_em_ordem(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista
            )
            print(f"  progrediram (ordem): {_nomes(ordem)}")
            if lista is not None:
                conc = ocup_sel.ocupantes_da_ampla(
                    edital=edital, perfil_id=perfil, marco_id=marco, versao=versao
                )
                print(f"  ocupantes da ampla (hoje): {_nomes(conc)}")
            for c in Convocacao.objects.filter(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista
            ).order_by("criado_em"):
                d = c.desfechos.first()
                suc = " (sucedida)" if c.sucessoras.exists() else ""
                print(
                    f"  convocação {_nomes([c.inscricao_id])[0]:8} {c.especie:14} -> {d.especie if d else '—'}{suc}"
                )
            ctx = conv_sel.contexto_do_recorte(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=agora
            )
            print(f"  titulares (recalc.): {_nomes(ctx['titulares'])}")
            print(f"  ocupando (recalc.):  {_nomes(ctx['ocupando'])}")
            print(
                f"  servidos: {_nomes(ctx['servidos'])} encerrados: {_nomes(ctx['encerrados'])} emAberto: {_nomes(ctx['emAberto'])}"
            )
            print(f"  fila: {_nomes(ctx['fila'])}")
            try:
                previa = previa_dos_titulares(
                    edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=agora
                )
                print(
                    f"  prévia 'Convocar titulares': {[p['nome'].split()[0] for p in previa['pessoas']]} "
                    f"impedimento={previa['impedimento'] and previa['impedimento']['codigo']}"
                )
            except Exception as erro:  # noqa: BLE001
                print(f"  prévia: erro {erro!r}")
            leitura = ocup_sel.ocupacao_do_recorte(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=agora
            )
            print(
                f"  ocupacao_do_recorte: { {k: leitura.get(k) for k in ('publicadas', 'efetivas', 'ocupadas', 'faltando', 'estado')} }"
            )
