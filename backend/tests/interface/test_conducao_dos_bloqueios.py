"""Quem esbarra num bloqueio lê o que fazer **e a quem pedir** (037, US2).

**Os dois bloqueios que calavam, e eles calavam de modos diferentes.** O aviso de conteúdo imutável
dizia que correções ocorrem por Retificação e parava aí — e a frase que conduz já era praticada seis
linhas acima, no mesmo cartão. A pendência de ausência de Perfil dizia o que falta e levava à etapa;
o que ela não dizia é a quem pedir quando quem lê não pode resolver.

**O caso que separa isto de microcópia** é o do silêncio: quem **pode** praticar a ação recebe o
caminho, e não a frase de pedir a outra pessoa. Dizer *"peça a alguém"* ao lado do botão que a
pessoa pode clicar é pior do que não dizer nada — ensina a desconfiar da tela.

O percurso que autorizou a segunda metade a existir está em
`specs/037-quatro-becos-conhecidos/achado-do-ach-02.md`: ele reproduziu o Gestor da reauditoria e
mediu que o caminho existe, leva à etapa, e termina em "Somente leitura".
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

#: As duas conduções, literais. Afirmá-las pelo texto — e não por "alguma frase apareceu" — é o que
#: prende a forma **cheia** (`FR-543a`) e o que faria uma redação à mão ser notada (`FR-543`).
CONDUCAO_DA_RETIFICACAO = (
    "A Retificação depende da permissão de retificar. "
    "Peça a alguém com a permissão de retificar que a proponha."
)
CONDUCAO_DA_COMPOSICAO = (
    "A correção depende da permissão de elaborar o Edital. "
    "Peça a alguém com a permissão de elaborar o Edital que a faça."
)

_CARTAO = re.compile(r'<section aria-labelledby="acoes-titulo".*?</section>', re.DOTALL)


def _cartao_de_acoes(client, edital):
    """O cartão *"O que fazer agora"*, e não a página.

    A `SC-189` conta bloqueios **naquele cartão**; procurar a frase no corpo inteiro acharia
    qualquer outra superfície e responderia "conduz" sem que o cartão tivesse mudado.
    """
    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    bloco = _CARTAO.search(corpo)
    assert bloco is not None, "o cartão de ações não apareceu"
    return bloco.group(0)


# ---------------------------------------------------------------------------
# ACH-30 · o aviso de conteúdo imutável
# ---------------------------------------------------------------------------


def test_o_aviso_nomeia_a_acao_e_a_permissao_para_quem_nao_pode_retificar(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-541`: o bloqueio é dito, e agora o que fazer também.

    Bruno homologa e publica, e **não** retifica. Antes, ele lia que correções ocorrem por
    Retificação e ficava sem saber a quem se dirigir — a `SC-189` conta este cartão, e era este o
    bloqueio que sobrava nele.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "bruno.homologador", ["homologador", "publicador"])

    cartao = _cartao_de_acoes(client, edital)

    assert "Conteúdo imutável" in cartao
    assert CONDUCAO_DA_RETIFICACAO in cartao


def test_quem_pode_retificar_recebe_o_caminho_e_o_aviso_cala(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-541b` e `FR-544`: o silêncio é a entrega, e não a omissão.

    Ana elabora, e `retificacao:elaborar` vem com o papel. O caminho **já era** entregue a ela — a
    ação está na lista —, e o que a `037` acrescenta neste caso é o aviso não repetir "peça a
    alguém" ao lado do botão que ela pode clicar.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])

    cartao = _cartao_de_acoes(client, edital)

    assert "Conteúdo imutável" in cartao, "o aviso continua existindo — o que cala é a condução"
    assert CONDUCAO_DA_RETIFICACAO not in cartao
    assert ">Retificar</a>" in cartao, "e o caminho continua oferecido"


def test_retificar_nao_virou_botao_desabilitado_com_motivo(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-541c`: a correção **plausível e errada**, prendida para que ninguém a refaça.

    O cartão desabilita **atos** com o motivo ao lado (`FR-024`), e aplicar isso a `Retificar`
    parece a solução natural. Mas navegação segue outra regra: destino que o ator não abre **não é
    oferecido** — é a garantia que a `007` e a `033` deixaram, e desfazê-la aqui a desfaria para
    todas as telas que a herdaram. A condução é prosa no aviso.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "bruno.homologador", ["homologador", "publicador"])

    cartao = _cartao_de_acoes(client, edital)

    assert "Retificar" not in cartao.replace("por Retificação", ""), (
        "a ação não é oferecida a quem não a pratica, nem desabilitada com motivo"
    )


def test_o_edital_em_elaboracao_nao_ganha_aviso_nenhum(client, seletor_ligado, edital):
    """A contraprova do estado: só o Edital **publicado** tem conteúdo imutável a anunciar.

    Sem este caso, um predicado que esquecesse o estado passaria por todos os outros — e o cartão
    mandaria pedir uma Retificação para um Edital que ainda está sendo escrito.
    """
    assert edital.status == Edital.Status.EM_ELABORACAO
    identificar(client, "bruno.homologador", ["homologador", "publicador"])

    cartao = _cartao_de_acoes(client, edital)

    assert "Conteúdo imutável" not in cartao
    assert CONDUCAO_DA_RETIFICACAO not in cartao


# ---------------------------------------------------------------------------
# ACH-02 · a pendência de ausência de Perfil
# ---------------------------------------------------------------------------


def _etapa(client, edital, etapa):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, etapa]))
    assert resposta.status_code == 200, resposta.status_code
    return resposta.content.decode()


def test_a_pendencia_continua_dizendo_o_que_falta_e_levando_a_etapa(client, seletor_ligado, edital):
    """`FR-542`: **o que já existe não é refeito**.

    Esta metade foi fechada por feature anterior, e a `037` não a toca. O caso está aqui porque a
    mudança de assinatura da montagem das pendências passa exatamente por cima dela: uma condução
    que substituísse o caminho em vez de acompanhá-lo passaria em todos os outros casos deste
    arquivo.
    """
    identificar(client, "ana.gestora", ["gestor"])

    pagina = _etapa(client, edital, "revisao")

    assert "Ao menos um Perfil é obrigatório." in pagina
    assert "Ir para Perfis de Vaga" in pagina


def test_quem_nao_pode_compor_le_a_quem_pedir(client, seletor_ligado, edital):
    """`FR-542` e `SC-195`: a metade que faltava, na tela onde o percurso mediu que ela faltava.

    O Gestor da reauditoria chega aqui, lê o que falta, segue o caminho e encontra uma tela de
    leitura. A condução é o que fecha o `ACH-02` — e ela nomeia **a permissão**, nunca uma pessoa.
    """
    identificar(client, "ana.gestora", ["gestor"])

    pagina = _etapa(client, edital, "revisao")

    assert CONDUCAO_DA_COMPOSICAO in pagina


def test_a_conducao_e_dita_uma_vez_para_a_lista_inteira(client, seletor_ligado, edital):
    """O predicado é do par Edital×ator, e a resposta é a mesma para todas as pendências.

    **Foi o percurso que achou isto**, e não um teste: dita por item, a mesma frase saía três
    vezes seguidas na Revisão — ruído exatamente na tela que a auditoria já acusa de densa. Dizê-la
    uma vez não é economia de tela; é a diferença entre conduzir e repetir.
    """
    identificar(client, "ana.gestora", ["gestor"])

    pagina = _etapa(client, edital, "revisao")

    assert pagina.count(CONDUCAO_DA_COMPOSICAO) == 1, (
        "a condução se repetiu: ela é da lista, e não de cada pendência"
    )


def test_a_conducao_alcanca_tambem_a_etapa_em_que_a_pendencia_mora(client, seletor_ligado, edital):
    """Sete das oito telas passam `com_link=False`, e a condução vale nelas também.

    Uma condução escrita dentro do bloco do caminho apareceria **só na Revisão** — e a Revisão é a
    nona etapa. Quem segue o caminho para de onde a pendência o manda, que é onde ele descobre que
    não pode agir, não leria nada.
    """
    identificar(client, "ana.gestora", ["gestor"])

    pagina = _etapa(client, edital, "perfis")

    assert "Ao menos um Perfil é obrigatório." in pagina
    assert CONDUCAO_DA_COMPOSICAO in pagina


def test_quem_pode_compor_nao_recebe_a_frase_de_pedir(client, seletor_ligado, edital):
    """`FR-544` e `D-002`: *"peça a alguém com a permissão de X"* é falso para quem tem X.

    É por isto que a condução nasce na tela e não na mensagem normativa: a mensagem descreve o
    defeito do conteúdo, é lida por mais de uma superfície e não conhece quem está olhando.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    pagina = _etapa(client, edital, "revisao")

    assert "Ao menos um Perfil é obrigatório." in pagina
    assert CONDUCAO_DA_COMPOSICAO not in pagina


#: A lista de pendências **com a condução que vem logo depois dela** — é ali que a frase mora, e
#: é ali que se confere que ela não nomeia ninguém.
_PENDENCIAS = re.compile(
    r"<ul>.*?Ao menos um Perfil é obrigatório.*?</ul>\s*(?:<p class=\"ajuda\">.*?</p>)?",
    re.DOTALL,
)


def test_nenhuma_conducao_nomeia_pessoa(client, seletor_ligado, edital):
    """`FR-543b`: não há fila, designação nem nome próprio — só a permissão.

    A disciplina é do produto inteiro, e a maneira de quebrá-la é acrescentar "fale com quem
    elaborou" achando que ajuda. Os nomes de quem já atuou estão à mão nesta mesma requisição, e
    seria barato imprimi-los.

    **Lido da lista de pendências**, e não da página: o cabeçalho nomeia quem está identificado, e
    uma varredura do corpo inteiro reprovaria por causa dele.
    """
    identificar(client, "ana.gestora", ["gestor"])

    bloco = _PENDENCIAS.search(_etapa(client, edital, "revisao"))

    assert bloco is not None, "a lista de pendências não apareceu"
    lista = bloco.group(0)
    assert "com a permissão de elaborar o Edital" in lista
    for nome in ("ana.gestora", "ana.elaboradora", "preparador", "Fale com"):
        assert nome not in lista, f"a condução nomeou {nome!r} em vez da permissão"


# ---------------------------------------------------------------------------
# O estado, que é a outra metade da pergunta — e que a primeira escrita errou
# ---------------------------------------------------------------------------


def test_edital_publicado_nao_manda_pedir_a_ninguem(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-544`: **ninguém** compõe um Edital publicado, e por isso não há a quem pedir.

    **Esta é a regressão do defeito que a revisão achou.** A condução saía de
    `not pode_compor(...)`, e `pode_compor` reúne estado e permissão: negado inteiro, o Edital
    publicado caía no mesmo ramo de quem apenas não tem a permissão. A tela passava a nomear, como
    solução, uma permissão que não abre aquele estado para pessoa alguma.

    O ator deste caso **tem** `edital:elaborar` — é ele quem torna a falsidade dupla: a frase o
    mandava pedir a outra pessoa exatamente o que ele já detém, e que ainda assim não resolveria.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])

    pagina = _etapa(client, edital, "revisao")

    assert edital.status == Edital.Status.PUBLICADO
    assert "Ir para" in pagina, "o cenário só vale se houver pendência corrigível na tela"
    assert CONDUCAO_DA_COMPOSICAO not in pagina


def test_edital_publicado_nao_manda_pedir_nem_a_quem_nao_tem_a_permissao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A contraprova do caso acima, pelo outro lado do par.

    Sem ela, a correção poderia ter sido *"cale quando o ator tem a permissão"* — que conserta o
    caso visível e deixa o defeito de pé para todo mundo que não a tem. O que decide aqui é o
    **estado**: publicado não se compõe, e a pergunta "a quem pedir?" não tem resposta.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.gestora", ["gestor"])

    pagina = _etapa(client, edital, "revisao")

    assert CONDUCAO_DA_COMPOSICAO not in pagina


def test_em_elaboracao_a_conducao_depende_so_da_permissao(client, seletor_ligado, edital):
    """E o par completo, do lado em que a composição ainda é possível.

    Os dois casos acima poderiam ser satisfeitos por um predicado que calasse **sempre**. Este é o
    que impede isso: em elaboração, quem não tem a permissão continua lendo a quem pedir.
    """
    assert edital.status == Edital.Status.EM_ELABORACAO

    identificar(client, "ana.gestora", ["gestor"])
    assert CONDUCAO_DA_COMPOSICAO in _etapa(client, edital, "revisao")

    identificar(client, "ana.elaboradora", ["elaborador"])
    assert CONDUCAO_DA_COMPOSICAO not in _etapa(client, edital, "revisao")
