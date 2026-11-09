"""O retrato de um cenário: quantas linhas de cada espécie ele tem agora (134, FR-4617).

**Por introspecção, e não por lista.** Uma lista de modelos esqueceria o primeiro app que nascesse
depois dela — e um cenário exercitado nele pareceria intacto. Aqui entra todo modelo com chave
estrangeira para o Processo, para um Edital ou para uma Inscrição, que é onde o domínio pendura o
que um certame produz; e a trilha de auditoria desses agregados, que é onde **todo** ato deixa
rastro, inclusive os que não criam linha nova.

O retrato não decide nada sozinho: comparado com o do instante em que o cenário ficou pronto, ele
diz se alguém já o exercitou. É informação para a pessoa que vai restaurar — nunca autorização.
"""

from django.apps import apps
from django.db import models

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo

_ALVOS = (ProcessoSeletivo, Edital, Inscricao)


def _ligacoes():
    """(modelo, campo, alvo) de todo vínculo direto com Processo, Edital ou Inscrição."""
    ligacoes = []
    for modelo in apps.get_models():
        if modelo._meta.app_label == "treinamento":
            continue
        for campo in modelo._meta.get_fields():
            if (
                isinstance(campo, (models.ForeignKey, models.OneToOneField))
                and campo.related_model in _ALVOS
                and campo.concrete
            ):
                ligacoes.append((modelo, campo.name, campo.related_model))
    return ligacoes


def retratar(processo):
    """{rótulo: contagem}, mais o estado e a revisão de cada Edital — o que muda quando se age."""
    editais = list(Edital.objects.filter(processo=processo).order_by("id"))
    inscricoes = list(
        Inscricao.objects.filter(edital__processo=processo).values_list("id", flat=True)
    )
    filtros = {
        ProcessoSeletivo: [processo.id],
        Edital: [edital.id for edital in editais],
        Inscricao: inscricoes,
    }
    retrato = {
        "processo": f"{processo.status}/{processo.revision}",
        "editais": {str(edital.id): f"{edital.status}/{edital.revision}" for edital in editais},
    }
    contagens = {}
    for modelo, campo, alvo in _ligacoes():
        total = modelo._default_manager.filter(**{f"{campo}__in": filtros[alvo]}).count()
        if total:
            rotulo = f"{modelo._meta.label}.{campo}"
            contagens[rotulo] = total
    agregados = [processo.id, *filtros[Edital], *inscricoes]
    contagens["auditoria"] = RegistroAuditoria.objects.filter(aggregate_id__in=agregados).count()
    retrato["contagens"] = dict(sorted(contagens.items()))
    return retrato


def diferencas(antes, depois):
    """As linhas que mudaram, em frases curtas, para quem lê a verificação."""
    frases = []
    if antes.get("processo") != depois.get("processo"):
        frases.append(f"Processo: {antes.get('processo')} → {depois.get('processo')}")
    for edital, estado in depois.get("editais", {}).items():
        anterior = antes.get("editais", {}).get(edital)
        if anterior != estado:
            frases.append(f"Edital {edital[:8]}: {anterior or 'novo'} → {estado}")
    contagens_antes = antes.get("contagens", {})
    for rotulo, total in depois.get("contagens", {}).items():
        if contagens_antes.get(rotulo, 0) != total:
            frases.append(f"{rotulo}: {contagens_antes.get(rotulo, 0)} → {total}")
    return frases
