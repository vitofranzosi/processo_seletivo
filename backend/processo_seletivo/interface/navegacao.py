"""As seções da gestão e quem as alcança — a barra lateral do shell (076).

A barra está em toda tela, e por isso não pode oferecer o que a autorização recusa: seria o `N-03`
da 038 repetido em 59 telas. Cada item leva o predicado que a **lista** já usava para o seu botão,
e a lista passa a ler os predicados daqui (`R-002`): uma grafia só, e a barra e a lista não podem
divergir. Retirar o link não substitui a recusa — a view de cada destino continua decidindo
(`FR-482` da 033).

Nada aqui consulta o banco. As capacidades vêm da sessão (`FR-1715`), e a seção atual sai do
endereço (`R-003`), que é hierárquico de propósito: as rotas da Mesa pendem de `minhas-etapas`.
"""

from dataclasses import dataclass

from django.urls import reverse

from processo_seletivo.interface import identidade
from processo_seletivo.interface import visao_geral as visao_institucional
from processo_seletivo.unidades.domain.nomes import GERIR as GERIR_AUTORIDADES


def pode_ver_visao(ator):
    # Sem consulta nova: a capacidade já veio na sessão (040, FR-605).
    return ator.can(visao_institucional.CONSULTAR)


def pode_gerir_autoridades(ator):
    # O caminho para as autoridades da unidade (060), condicionado à permissão pela razão da visão
    # geral: oferecer um destino que a autorização recusa é o `N-03` da 038.
    return ator.can(GERIR_AUTORIDADES)


def pode_gerir_modelos(ator):
    # Os modelos de aviso da unidade (066): por papel, como as autoridades.
    return ator.can("aviso:enviar")


def _toda_identidade(ator):
    # A lista e Minhas Etapas não dependem de papel: a primeira diz a quem não tem papel o que
    # falta, e a segunda é o caminho de quem só tem vínculo (UX-008).
    return True


@dataclass(frozen=True)
class Secao:
    rotulo: str
    rota: str
    grupo: str
    alcanca: object


TRABALHO = "Trabalho"
UNIDADE = "Unidade"

# A ordem é a da barra. "Novo Processo Seletivo" não está aqui: é ação, e não lugar (DP-1).
SECOES = (
    Secao("Processos Seletivos", "interface:lista", TRABALHO, _toda_identidade),
    Secao("Minhas Etapas", "interface:minhas-etapas", TRABALHO, _toda_identidade),
    Secao("Visão Geral", "interface:visao-geral", TRABALHO, pode_ver_visao),
    Secao("Autoridades da unidade", "interface:autoridades", UNIDADE, pode_gerir_autoridades),
    Secao("Modelos de aviso", "interface:modelos-de-aviso", UNIDADE, pode_gerir_modelos),
)


def secao_do_caminho(caminho):
    """A seção a que pertence a tela daquele endereço — a de prefixo mais longo.

    A lista responde na raiz da gestão, e por isso é o prefixo de todos: toda tela que não está sob
    outra seção é de Processos Seletivos — o Processo, o Edital, a composição, o recurso.
    """
    candidatas = [s for s in SECOES if caminho.startswith(reverse(s.rota))]
    return max(candidatas, key=lambda s: len(reverse(s.rota)), default=None)


def grupos_da_barra(ator, caminho):
    """Os grupos com os itens que o ator alcança. Grupo sem item não vem (`FR-1714`)."""
    atual = secao_do_caminho(caminho)
    grupos = {}
    for secao in SECOES:
        if not secao.alcanca(ator):
            continue
        endereco = reverse(secao.rota)
        grupos.setdefault(secao.grupo, []).append(
            {
                "rotulo": secao.rotulo,
                "endereco": endereco,
                # Na própria página, `page`; abaixo dela, `true` — a tela é daquela seção.
                "atual": ("page" if caminho == endereco else "true") if secao is atual else "",
            }
        )
    return [{"nome": nome, "itens": itens} for nome, itens in grupos.items()]


def contexto_da_navegacao(request):
    """A barra e a seção atual, a todo template da gestão.

    O processador roda também no portal, que não tem barra; ali ele não lê nada.
    """
    if not request.path.startswith(reverse("interface:lista")):
        return {}
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return {}
    secao = secao_do_caminho(request.path)
    return {
        "barra": grupos_da_barra(ator, request.path),
        "secao_atual": secao and {"rotulo": secao.rotulo, "endereco": reverse(secao.rota)},
    }
