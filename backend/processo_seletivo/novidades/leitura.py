"""Quem vê qual nota, e o que cada identidade ainda não viu (168).

**A barra não consulta o banco** (`FR-1715` da `076`, FR-7415). O que a identidade não viu se lê do
banco em dois momentos só — na entrada da gestão e na abertura da página — e se guarda na sessão; a
barra cruza a lista da sessão com as notas disponíveis, que estão em memória. O preço (`D-005`): a
contagem não acompanha, na mesma sessão, uma visita feita noutro navegador.
"""

import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from processo_seletivo.novidades import catalogo
from processo_seletivo.novidades.models import LeituraDasNovidades

logger = logging.getLogger(__name__)

# O que a identidade não tinha visto na entrada. Ausente — sessão aberta antes desta feature, ou
# arquivo inválido — é "não sei", e a barra não mostra número.
NAO_VISTAS = "novidades:nao_vistas"
# O bloco "Desde sua última visita": o que era novo na primeira abertura da página nesta sessão
# (FR-7417). Recarregar a página não o esvazia; uma sessão nova, sim.
DESTA_VISITA = "novidades:desta_visita"
# O instante da visita anterior, em ISO, ou "" quando é a primeira da identidade.
VISITA_ANTERIOR = "novidades:visita_anterior"

TETO_DA_CONTAGEM = 9


def disponivel(nota, ator):
    """Se a nota existe para este ator neste ambiente (FR-7410, FR-7411)."""
    if nota.requer_configuracao and not getattr(settings, nota.requer_configuracao, False):
        return False
    return not (nota.para_capacidade and not ator.can(nota.para_capacidade))


def disponiveis(ator, notas=None):
    notas = catalogo.notas() if notas is None else notas
    return [nota for nota in notas if disponivel(nota, ator)]


def ao_entrar(request, ator):
    """Na entrada da gestão: guarda na sessão o que a identidade ainda não viu.

    Chamada pela entrada de demonstração, pela institucional e pela troca de unidade — a troca muda
    as capacidades, e com elas as notas disponíveis. Uma consulta, na entrada, e nenhuma depois.
    """
    for chave in (NAO_VISTAS, DESTA_VISITA, VISITA_ANTERIOR):
        request.session.pop(chave, None)
    if ator is None:
        return
    try:
        notas = disponiveis(ator)
    except catalogo.CatalogoInvalido:
        # Release com arquivo inválido não passa no CI; se passar, a gestão continua de pé e a
        # barra fica sem número.
        logger.exception("novidades_indisponiveis")
        return
    leitura = LeituraDasNovidades.objects.filter(subject=ator.subject).only("vistas").first()
    vistas = set(leitura.vistas) if leitura else set()
    request.session[NAO_VISTAS] = [nota.id for nota in notas if nota.id not in vistas]


def contagem(request, ator):
    """Quantas notas disponíveis a identidade não viu — sem consulta (FR-7414, FR-7415)."""
    ids = request.session.get(NAO_VISTAS)
    if not ids:
        return 0
    try:
        notas = disponiveis(ator)
    except catalogo.CatalogoInvalido:
        return 0
    pendentes = set(ids)
    return sum(1 for nota in notas if nota.id in pendentes)


def rotulo_da_contagem(quantidade):
    return f"{TETO_DA_CONTAGEM}+" if quantidade > TETO_DA_CONTAGEM else str(quantidade)


def registrar_visita(request, ator, notas):
    """Abrir a página é ver: marca como vistas todas as notas disponíveis (FR-7416, `D-006`).

    Devolve `(desta_visita, visita_anterior)`: os identificadores do bloco "Desde sua última visita"
    e o instante da visita anterior (`None` na primeira da identidade).
    """
    leitura = LeituraDasNovidades.objects.filter(subject=ator.subject).first()
    anteriores = set(leitura.vistas) if leitura else set()
    novas = [nota.id for nota in notas if nota.id not in anteriores]
    sessao = request.session
    if DESTA_VISITA not in sessao:
        sessao[DESTA_VISITA] = novas
        sessao[VISITA_ANTERIOR] = leitura.ultima_visita.isoformat() if leitura else ""
    else:
        # Implantação no meio da sessão: o que chegou entra no mesmo bloco.
        ja = set(sessao[DESTA_VISITA])
        sessao[DESTA_VISITA] = [*sessao[DESTA_VISITA], *(i for i in novas if i not in ja)]
    agora = timezone.now()
    # As vistas de antes ficam, mesmo as de nota que saiu do arquivo ou que esta pessoa deixou de
    # alcançar: voltando a alcançá-la, ela não reaparece como nova.
    vistas = sorted(anteriores | {nota.id for nota in notas})
    LeituraDasNovidades.objects.update_or_create(
        subject=ator.subject, defaults={"vistas": vistas, "ultima_visita": agora}
    )
    sessao[NAO_VISTAS] = []
    anterior = sessao[VISITA_ANTERIOR]
    return list(sessao[DESTA_VISITA]), (datetime.fromisoformat(anterior) if anterior else None)
