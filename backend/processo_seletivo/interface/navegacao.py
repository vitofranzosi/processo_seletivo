"""As seções da gestão e quem as alcança — a barra lateral do shell (076).

A barra está em toda tela, e por isso não pode oferecer o que a autorização recusa: seria o `N-03`
da 038 repetido em 59 telas. Cada item leva o predicado que a **lista** usava para o seu botão
(`R-002`). Desde a 077 a lista não tem mais esses botões (`FR-1740`), e o predicado mora só aqui.
Retirar o link não substitui a recusa — a view de cada destino continua decidindo (`FR-482` da
033).

Nada aqui consulta o banco. As capacidades vêm da sessão (`FR-1715`), e a seção atual sai do
endereço (`R-003`), que é hierárquico de propósito: as rotas da Mesa pendem de `minhas-etapas`.
"""

import re
from dataclasses import dataclass

from django.urls import reverse
from django.utils.functional import SimpleLazyObject

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
    # O símbolo no sprite do `base.html` (`FR-1731`). Pelo significado: a pasta do Processo, a
    # prancheta do trabalho alocado, o gráfico da visão, o calendário da agenda, o prédio da
    # unidade, o envelope do aviso, o livro do manual.
    icone: str


TRABALHO = "Trabalho"
UNIDADE = "Unidade"
AJUDA = "Ajuda"

# A ordem é a da barra. "Novo Processo Seletivo" não está aqui: é ação, e não lugar (DP-1).
SECOES = (
    Secao("Processos Seletivos", "interface:lista", TRABALHO, _toda_identidade, "i-pasta"),
    Secao("Minhas Etapas", "interface:minhas-etapas", TRABALHO, _toda_identidade, "i-prancheta"),
    Secao("Visão Geral", "interface:visao-geral", TRABALHO, pode_ver_visao, "i-grafico"),
    # Toda identidade, como a lista: a agenda só mostra cronograma publicado (101, `D-004`).
    Secao("Agenda", "interface:agenda", TRABALHO, _toda_identidade, "i-calendario"),
    Secao(
        "Autoridades da unidade",
        "interface:autoridades",
        UNIDADE,
        pode_gerir_autoridades,
        "i-predio",
    ),
    Secao(
        "Modelos de aviso", "interface:modelos-de-aviso", UNIDADE, pode_gerir_modelos, "i-envelope"
    ),
    # Por último e em grupo próprio: não é lugar de trabalho, e abre o manual fora da moldura da
    # gestão (105, `D-004`). Toda identidade, pela razão da Agenda (`D-001`).
    Secao("Documentação do Sistema", "interface:documentacao", AJUDA, _toda_identidade, "i-livro"),
)


# As telas cuja matriz não cabe ao lado da barra a 1.280 px (DP-4). Nelas a barra fica recolhida
# em qualquer largura, como no celular: a Alocação por Etapa, com nove Etapas, tem ~1.213 px de
# matriz, e a 057 exige que ela caiba sem rolagem interna e com o cabeçalho preso à janela
# (`FR-1062`). Pela rota, e não por marcação na tela, para não tocar o conteúdo dela.
TELAS_LARGAS = frozenset({"interface:alocacoes"})


def secao_do_caminho(caminho, enderecos=None):
    """A seção a que pertence a tela daquele endereço — a de prefixo mais longo.

    A lista responde na raiz da gestão, e por isso é o prefixo de todos: toda tela que não está sob
    outra seção é de Processos Seletivos — o Processo, o Edital, a composição, o recurso.
    """
    enderecos = enderecos or _enderecos()
    candidatas = [s for s in SECOES if caminho.startswith(enderecos[s.rota])]
    return max(candidatas, key=lambda s: len(enderecos[s.rota]), default=None)


def declarar_secao(request, rota):
    """A view diz a seção quando o endereço não basta para dizê-la (077, `FR-1752`).

    A Etapa mora sob `minhas-etapas` porque é dali que o avaliador a alcança, mas quem gere a
    comissão chega a ela pela Alocação, que é de Processos Seletivos. Pelo endereço, a barra
    marcava Minhas Etapas e a trilha do cabeçalho, ao lado, dizia Alocação por Etapa: duas
    orientações contraditórias na mesma faixa da tela. Só a view sabe a porta; ela a declara
    antes de renderizar, e a barra, que só se monta quando lida, já a encontra.
    """
    request.secao_da_gestao = rota


def _secao_da_tela(request, enderecos):
    rota = getattr(request, "secao_da_gestao", None)
    if rota is not None:
        return next(secao for secao in SECOES if secao.rota == rota)
    return secao_do_caminho(request.path, enderecos)


def _enderecos():
    # Uma vez por pedido, e não guardado no módulo: o prefixo do endereço é do pedido.
    return {secao.rota: reverse(secao.rota) for secao in SECOES}


def grupos_da_barra(ator, caminho, atual, enderecos):
    """Os grupos com os itens que o ator alcança. Grupo sem item não vem (`FR-1714`)."""
    grupos = {}
    for secao in SECOES:
        if not secao.alcanca(ator):
            continue
        endereco = enderecos[secao.rota]
        grupos.setdefault(secao.grupo, []).append(
            {
                "rotulo": secao.rotulo,
                "endereco": endereco,
                "icone": secao.icone,
                # Na própria página, `page`; abaixo dela, `true` — a tela é daquela seção.
                "atual": ("page" if caminho == endereco else "true") if secao is atual else "",
            }
        )
    return [{"nome": nome, "itens": itens} for nome, itens in grupos.items()]


def iniciais(nome):
    """As duas letras do avatar da barra recolhida: `gustavo.gestor` vira `GG`, `ana` vira `A`.

    O nome da demonstração é um identificador, e não um nome civil: as partes se separam por ponto,
    hífen, sublinhado ou espaço. O diretório institucional, quando chegar, traz o nome de verdade.
    """
    partes = [parte for parte in re.split(r"[.\-_\s]+", nome or "") if parte]
    return "".join(parte[0] for parte in partes[:2]).upper()


def _navegacao(request):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return {}
    enderecos = _enderecos()
    atual = _secao_da_tela(request, enderecos)
    return {
        "barra": grupos_da_barra(ator, request.path, atual, enderecos),
        "no_topo": getattr(request.resolver_match, "view_name", None) in TELAS_LARGAS,
        "iniciais": iniciais(ator.subject),
        "secao_atual": atual.rotulo if atual else "",
    }


def contexto_da_navegacao(request):
    """A barra e a seção atual, a todo template da gestão, sob o nome `navegacao`.

    **Preguiçosa**: só se monta quando o `base.html` a lê. O processador roda em toda resposta, e
    os fragmentos que o htmx troca — muitos por minuto na composição — não têm barra. No portal,
    que também não tem, ele nem a oferece.
    """
    if not request.path.startswith(reverse("interface:lista")):
        return {}
    return {"navegacao": SimpleLazyObject(lambda: _navegacao(request))}
