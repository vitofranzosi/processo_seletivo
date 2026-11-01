"""Os cenários de referência do kit de divulgação (111), pelo fluxo real de publicação.

Os Editais são os do corpus da `070` (`corpus_070/`), republicados pelos comandos reais por
`publicar_do_corpus`, e as variações saem do `mudar` do próprio corpus — o mesmo caminho da POC
(`doc/poc-kit-de-divulgacao-2026-10-31/test_poc_kit.py`).

**Deslocamento em dias inteiros.** O `deslocamento_ate_agora` do corpus leva a hora do relógio
junto, e o término "23h59" do 91/2026 viraria uma hora qualquer. Somar dias inteiros preserva as
horas que o corpus publicou, e é delas que os textos falam.

**Um Edital por caso.** O 91/2026 republicado duas vezes no mesmo banco colide no número; cada caso
de teste tem a própria transação.
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.corpus import REFERENCIA, publicar_do_corpus, retificar_do_corpus
from tests.fixtures.publicacao import retify

BASE = "https://gps.exemplo.ifes.edu.br"


def deslocamento():
    return timedelta(days=(timezone.now() - REFERENCIA).days + 2)


def publicar(api_client, nome="91", *, chave, ate=None, mudar=None):
    """O Edital `nome` do corpus, publicado; `ate` limita as Retificações aplicadas."""
    edital, _ = publicar_do_corpus(
        api_client, nome, ate=ate, deslocamento=deslocamento(), chave=chave, mudar=mudar
    )
    return edital


def retificar(api_client, edital, nome, numero, *, chave):
    """A Retificação `numero` do corpus, com o mesmo deslocamento da publicação."""
    return retificar_do_corpus(api_client, edital, nome, numero, deslocamento(), chave=chave)


def vigente(edital):
    return (
        VersaoConsolidada.objects.filter(edital=edital, valid_from__lte=timezone.now())
        .order_by("-valid_from", "-materialized_at")
        .first()
    )


def evento_das_inscricoes(edital):
    return next(e for e in vigente(edital).content["schedule"] if e.get("isRegistrationPeriod"))


def inicio(edital):
    return parse_datetime(evento_das_inscricoes(edital)["startAt"])


def retificar_termino(api_client, edital, novo_fim, *, suffix):
    """Uma Retificação que só muda o término das inscrições, com vigência imediata."""
    evento = evento_das_inscricoes(edital)
    return retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/endAt",
                "operation": "REPLACE",
                "newValue": novo_fim.isoformat(),
            }
        ],
        suffix=suffix,
    )


def retificar_secao(api_client, edital, *, suffix):
    """Uma Retificação que não toca nenhum campo do material (`EC-9`)."""
    secao = next(
        s
        for s in vigente(edital).content["sections"]
        if s.get("type") == "TEXT" and s.get("content")
    )
    return retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/sections/id={secao['id']}/content",
                "operation": "REPLACE",
                "newValue": f"{secao['content']}\nTexto acrescentado pela Retificação.",
            }
        ],
        suffix=suffix,
    )


# ---- as variações, pelo `mudar` do corpus ---------------------------------------------------


def _podar_referencias(conteudo):
    restantes = {perfil["id"] for perfil in conteudo["profiles"]}
    for documento in conteudo.get("documentRequirements") or []:
        alcance = documento.get("profileIds")
        if alcance:
            documento["profileIds"] = [p for p in alcance if p in restantes]


def so_um_perfil(conteudo):
    conteudo["profiles"] = conteudo["profiles"][:1]
    _podar_referencias(conteudo)


def sem_localidade(conteudo):
    """Dois Perfis, um sem localidade: a ausência some da frase, e não vira "não informado"."""
    conteudo["profiles"] = conteudo["profiles"][:2]
    conteudo["profiles"][1]["locality"] = ""
    _podar_referencias(conteudo)


def sem_periodo(conteudo):
    for evento in conteudo["schedule"]:
        evento["isRegistrationPeriod"] = False


def termo_no_titulo(conteudo):
    """Um valor oficial com termo da lista (`EC-26`): fica, e é apontado."""
    conteudo["title"] = "Edital nº 91/2026 – Curso de Formação no Polo São Marcos (DEMONSTRAÇÃO)"
