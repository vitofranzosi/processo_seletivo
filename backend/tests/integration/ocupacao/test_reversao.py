"""A reversão de cota: declaração publicada, movimento e efeito (016).

**Um achado que a implementação revelou, e que a spec não previa.** Apurar a ocupação de uma cota
exige **ordem vigente daquele recorte** (`FR-243`), e `emitir_ordem` fixa `lista_id=None` por
decisão declarada (PR #85): *"um ato computado é sempre o de ampla concorrência — só o sorteio emite
por lista"*. Logo **reversão de cota só é apurável em certame de sorteio**.

Isso é coerente com a amostra, e não uma limitação surpresa: o 28/2026 e o 57/2026 — os dois Editais
que declaram reversão — são certames de **sorteio**. Mas significa que o percurso de ponta a ponta
da reversão precisa do cenário de sorteio com cotas, e não do cenário computado da `014`.

Enquanto esse cenário não existir, estes testes cobrem o que é provável sem ele: a declaração
atravessando a publicação inteira, e o movimento sobre uma apuração de cota construída à mão — com a
construção declarada, para ninguém a confundir com o percurso do ator.
"""

import pytest

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import MODALIDADE_PPI, montar_cenario_da_ocupacao
from tests.integration.ocupacao.test_emissao import apurar

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def com_saldo(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Perfil `3 / 2` com reversão por saldo declarada. A cota não tem quem a ocupe."""
    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-016-reversao",
        geral=3,
        ppi=2,
        reversao=nomes.REVERSAO_POR_SALDO,
    )


@pytest.fixture
def sem_declaracao(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O mesmo Perfil, sem declarar reversão. É o formato do 57/2026 item 4.5."""
    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-016-sem-reversao",
        geral=3,
        ppi=2,
    )


def test_a_declaracao_atravessa_o_snapshot(com_saldo):
    """A espécie declarada na composição chega ao conteúdo publicado (`FR-250`, degrau 14)."""
    from processo_seletivo.publicacoes.application.selectors import effective_version

    edital, _, _ = com_saldo
    versao = effective_version(edital_id=edital.id)
    perfil = next(p for p in versao.content["profiles"] if str(p["id"]) == PROFILE_ID)

    assert perfil["vacancyReversion"] == {"kind": nomes.REVERSAO_POR_SALDO}


def apuracao_da_cota(edital, gestor, *, publicadas=2, ocupadas=0):
    """A apuração da cota, **construída à mão** — e a razão está no topo do arquivo.

    O caminho do ator não a alcança em certame computado, porque não existe ordem com `lista_id`.
    Construí-la aqui isola o que este arquivo testa — o movimento — do que falta para o percurso
    completo, que é o cenário de sorteio com cotas.
    """
    from django.utils import timezone

    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
    from processo_seletivo.publicacoes.application.selectors import effective_version

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=None)
    versao = effective_version(edital_id=edital.id)
    return ApuracaoDeOcupacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=MODALIDADE_PPI,
        ato=ato,
        versao=versao,
        publicadas=publicadas,
        efetivas=publicadas,
        ocupadas=ocupadas,
        emitida_por="teste",
        emitida_em=timezone.now(),
    )


def reverter(edital, gestor, apuracao, *, especie=nomes.REVERSAO_POR_SALDO, ha_quem_ocupar=False):
    """`especie` vem com padrão no parâmetro, e **não** por `or` no corpo.

    `especie or padrao` transformava `""` — a ausência de declaração — no gatilho por saldo, e o
    teste do Edital que não declara passava a testar o contrário do que dizia.
    """
    from django.utils import timezone

    from processo_seletivo.ocupacao.application.movimento import reverter_cota

    return reverter_cota(
        apuracao=apuracao,
        especie=especie,
        ha_quem_ocupar=ha_quem_ocupar,
        registrado_por="teste",
        registrado_em=timezone.now(),
    )


def test_a_cota_com_saldo_reverte_para_a_linha_geral(com_saldo, gestor):
    """O movimento nasce **com a apuração da origem**, e vai para a linha geral (`FR-246`)."""
    edital, _, _ = com_saldo

    reverter(edital, gestor, apuracao_da_cota(edital, gestor))

    movimento = MovimentoDeVaga.objects.get()
    assert movimento.especie == nomes.MOVIMENTO_REVERSAO
    assert str(movimento.origem_lista_id) == MODALIDADE_PPI
    # **O destino é a linha geral — nulo** —, e não a Modalidade declarada como ampla concorrência.
    assert movimento.destino_lista_id is None
    assert movimento.quantidade == 2
    assert "não preenchidas" in movimento.causa


def test_a_linha_geral_recebe_e_a_publicada_nao_muda(com_saldo, gestor):
    """**`FR-239a` no caminho de verdade**: a efetiva sobe, a publicada fica."""
    edital, _, _ = com_saldo
    reverter(edital, gestor, apuracao_da_cota(edital, gestor))

    declarado = apurar(edital, gestor, chave="rev-ampla")

    assert declarado["publicadas"] == 3
    assert declarado["efetivas"] == 5


def test_a_soma_so_fecha_entre_apuracoes_que_leram_o_mesmo_movimento(com_saldo, gestor):
    """**Uma precisão que a implementação obrigou, e a `FR-247` não dizia.**

    O invariante da soma vale sobre o **conjunto de movimentos lidos**, e não sobre duas apurações
    quaisquer. Aqui a da cota é anterior ao movimento — logo não o leu, e a efetiva dela ainda diz 2
    enquanto a da ampla já diz 5. A soma dá 7, e isso **não** é violação: é a cota estando obsoleta.

    O que o sistema garante é que somar apurações que leram os mesmos movimentos fecha, e que o
    recorte desatualizado **se declara** obsoleto em vez de mentir. A prova do invariante em si é de
    unidade, em `test_soma_constante.py`, sobre o razão de movimentos.
    """
    edital, _, _ = com_saldo
    reverter(edital, gestor, apuracao_da_cota(edital, gestor))
    apurar(edital, gestor, chave="rev-ampla")

    ampla = selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    cota = selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=MODALIDADE_PPI
    )

    # A ampla leu o movimento; a cota é anterior a ele e se declara obsoleta.
    assert ampla["efetivas"] == 5 and ampla["estado"] == nomes.VIGENTE
    assert cota["efetivas"] == 2 and cota["estado"] == nomes.OBSOLETO
    assert nomes.CAUSA_MOVIMENTO_POSTERIOR in cota["causasDeObsolescencia"]
    # **O publicado não se move**, e a soma dele fecha sempre (`FR-239a`).
    assert ampla["publicadas"] + cota["publicadas"] == 5


def test_o_edital_que_nao_declara_nao_reverte(sem_declaracao, gestor):
    """**Ausência é "não move"** (`D-002`), e é o que o item 4.5 do 57/2026 exige."""
    edital, _, _ = sem_declaracao

    # Sem declaração, `reverter_cota` chamado com a espécie vazia não move nada — que é o que a
    # emissão faz quando o Perfil não declara: ela nem chega a chamar.
    assert reverter(edital, gestor, apuracao_da_cota(edital, gestor), especie="") is None
    assert MovimentoDeVaga.objects.count() == 0


def test_a_reversao_obsoleta_o_destino_sem_ninguem_emitir(com_saldo, gestor):
    """**`SC-084`**: é o que substitui a orquestração em cascata.

    A apuração da ampla é emitida **antes** da reversão. Quando a cota cede, aquela apuração fica
    obsoleta — com a causa nomeada — sem que ninguém toque nela, e volta a vigente na emissão
    seguinte, já com a efetiva maior.
    """
    edital, _, _ = com_saldo
    apurar(edital, gestor, chave="rev-ampla-antes")
    antes = selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert antes["estado"] == nomes.VIGENTE

    reverter(edital, gestor, apuracao_da_cota(edital, gestor))

    depois = selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert depois["estado"] == nomes.OBSOLETO
    assert nomes.CAUSA_MOVIMENTO_POSTERIOR in depois["causasDeObsolescencia"]

    nova = apurar(edital, gestor, chave="rev-ampla-depois", motivo="Reversão recebida")
    assert nova["efetivas"] == 5


def test_a_linha_geral_nao_reverte_para_si_mesma(com_saldo, gestor):
    """A ampla é destino, nunca origem.

    A recusa diz por quê, em vez de deixar a constraint de recortes distintos falar por ela.
    """
    from processo_seletivo.ocupacao.application.movimento import reverter_cota
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
    from processo_seletivo.shared.api.problems import DomainError

    edital, _, _ = com_saldo
    apurar(edital, gestor, chave="rev-ampla")
    apuracao = ApuracaoDeOcupacao.objects.get(lista_id=None)

    with pytest.raises(DomainError) as erro:
        reverter_cota(
            apuracao=apuracao,
            especie=nomes.REVERSAO_POR_SALDO,
            ha_quem_ocupar=False,
            registrado_por="teste",
            registrado_em=apuracao.emitida_em,
        )

    assert erro.value.code == "reversao_da_linha_geral"


def test_nenhuma_vaga_atravessa_perfil(com_saldo, gestor):
    """**`FR-246`, e é o item 4.5 do 57/2026**: não há remanejamento entre cursos.

    O movimento é sempre lido pelo recorte da **sua própria** apuração, e a apuração pertence a um
    Perfil. A asserção é estrutural: não existe caminho em que o `destino_lista_id` de um Perfil
    seja lido pela apuração de outro, porque a busca filtra por `apuracao__perfil_id`.
    """
    edital, _, _ = com_saldo
    reverter(edital, gestor, apuracao_da_cota(edital, gestor))
    movimento = MovimentoDeVaga.objects.get()

    assert str(movimento.apuracao.perfil_id) == PROFILE_ID
    outro_perfil = "00000000-0000-4000-8000-00000000dead"
    lidos = selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=outro_perfil, marco_id=MARCO, lista_id=None
    )
    assert lidos["estado"] == nomes.SEM_QUADRO
