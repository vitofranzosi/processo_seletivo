"""Quem ocupa por duas listas ao mesmo tempo (016, US4, `FR-252`–`FR-254`).

**É o item 8.9 do 28/2026, e ele só é alcançável em certame de sorteio** — porque só o sorteio emite
ordem por lista. O autodeclarado sorteado dentro das vagas de ampla **não é computado** no
preenchimento das reservadas, *"abrindo vaga para o próximo suplente autodeclarado"*.

**O que estes testes protegem é o recorte de destino.** A liberação devolve a vaga à **lista
reservada**, e nunca à linha geral: trocar o sentido mantém a soma certa e põe a vaga no lugar
errado, e só asserção de recorte o pega.
"""

import uuid

import pytest

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def sorteado(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Certame de sorteio com quadro `2 / 1 / 1` e uma ordem por recorte."""
    return certame_sorteado_com_quadro(
        gestor, api_client, manager_headers, process_payload, prefixo="conc-016"
    )


def apurar(certame, gestor, *, lista_id=None, chave="conc-016-apurar", motivo=""):
    return emitir_apuracao(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-ocupacao-016",
        motivo=motivo,
    )


def test_a_fixture_produz_uma_ordem_por_recorte(sorteado):
    """**O pré-requisito da US4, e a razão de a fixture existir.**

    Sem ordem por lista, apurar a cota é recusado com `ordem_nao_vigente` — e é o que acontecia no
    cenário computado da `014`, porque `emitir_ordem` fixa `lista_id` nulo.
    """
    atos = sorteado["atos"]

    assert len(atos) == 3, "ampla, PPI e PcD"
    assert atos[None].lista_id is None
    assert atos[uuid.UUID(LISTA_PPI)].lista_id == uuid.UUID(LISTA_PPI)


def test_a_cota_e_apuravel_aqui_e_nao_era_no_cenario_computado(sorteado, gestor):
    """Com ordem do recorte, a apuração da cota passa a existir."""
    declarado = apurar(sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi")

    assert declarado["publicadas"] == 1


def test_sem_etapa_governada_ninguem_ocupa_e_nada_e_liberado(sorteado, gestor):
    """**A precondição da liberação automática, dita como asserção.**

    O marco deste certame **não declara regra de corte**, logo não governa Etapa alguma — e sem
    Etapa governada não há Resultado a ler, de modo que ninguém consta como ocupando. A liberação
    automática pela emissão depende dessa cadeia inteira: faixa, Etapa governada e Resultado
    habilitado.

    O que este teste fixa é que a ausência **não** produz liberação fantasma: zero ocupadas, zero
    liberadas. A semântica da liberação em si está nos testes abaixo, que a exercitam diretamente.
    """
    declarado = apurar(sorteado, gestor, chave="conc-016-ampla")

    assert declarado["ocupadas"] == 0
    assert declarado["liberou"] == 0
    assert MovimentoDeVaga.objects.count() == 0


def test_a_vaga_liberada_volta_para_a_lista_reservada(sorteado, gestor):
    """**`FR-253`, e é a troca que a soma não denuncia.**

    A liberação devolve ao recorte **reservado**. Se fosse para a linha geral, a soma continuaria
    fechando e a vaga estaria no lugar errado — e o próximo da lista reservada nunca a receberia.
    """
    from django.utils import timezone

    from processo_seletivo.ocupacao.application.movimento import liberar_por_concomitancia
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao

    apurar(sorteado, gestor, chave="conc-016-ampla")
    apuracao = ApuracaoDeOcupacao.objects.get(lista_id=None)

    liberar_por_concomitancia(
        apuracao=apuracao,
        inscricao=sorteado["cotista_ppi"],
        registrado_por="teste",
        registrado_em=timezone.now(),
    )

    movimento = MovimentoDeVaga.objects.get(especie=nomes.MOVIMENTO_LIBERACAO)
    assert movimento.origem_lista_id is None, "sai da ampla"
    assert str(movimento.destino_lista_id) == LISTA_PPI, "volta para a reservada, não para a geral"
    assert movimento.quantidade == 1
    assert movimento.inscricao_id == sorteado["cotista_ppi"].id, "é movimento de pessoa"


def test_a_liberacao_torna_o_recorte_reservado_obsoleto(sorteado, gestor):
    """O destino se declara obsoleto, como na reversão — a quarta causa serve aos dois sentidos."""
    from django.utils import timezone

    from processo_seletivo.ocupacao.application.movimento import liberar_por_concomitancia
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao

    apurar(sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi")
    apurar(sorteado, gestor, chave="conc-016-ampla")
    apuracao_da_ampla = ApuracaoDeOcupacao.objects.get(lista_id=None)

    liberar_por_concomitancia(
        apuracao=apuracao_da_ampla,
        inscricao=sorteado["cotista_ppi"],
        registrado_por="teste",
        registrado_em=timezone.now(),
    )

    cota = selectors.ocupacao_do_recorte(
        edital=sorteado["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=LISTA_PPI
    )
    assert cota["estado"] == nomes.OBSOLETO
    assert nomes.CAUSA_MOVIMENTO_POSTERIOR in cota["causasDeObsolescencia"]


def test_a_liberacao_de_quem_nao_declarou_cota_e_recusada(sorteado, gestor):
    """Sem lista reservada não há vaga a liberar, e a recusa o diz."""
    from django.utils import timezone

    from processo_seletivo.ocupacao.application.movimento import liberar_por_concomitancia
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
    from processo_seletivo.shared.api.problems import DomainError

    apurar(sorteado, gestor, chave="conc-016-ampla")
    apuracao = ApuracaoDeOcupacao.objects.get(lista_id=None)
    sem_cota = sorteado["inscricoes"][3]

    with pytest.raises(DomainError) as erro:
        liberar_por_concomitancia(
            apuracao=apuracao,
            inscricao=sem_cota,
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

    assert erro.value.code == "sem_lista_reservada"


def test_a_liberacao_nao_parte_de_apuracao_de_cota(sorteado, gestor):
    """A liberação parte da ocupação **pela ampla**: a origem é a linha geral, sempre."""
    from django.utils import timezone

    from processo_seletivo.ocupacao.application.movimento import liberar_por_concomitancia
    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
    from processo_seletivo.shared.api.problems import DomainError

    apurar(sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi")
    da_cota = ApuracaoDeOcupacao.objects.get(lista_id=uuid.UUID(LISTA_PPI))

    with pytest.raises(DomainError) as erro:
        liberar_por_concomitancia(
            apuracao=da_cota,
            inscricao=sorteado["cotista_ppi"],
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

    assert erro.value.code == "liberacao_de_lista_reservada"
