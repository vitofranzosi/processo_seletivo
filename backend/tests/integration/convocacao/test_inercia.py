"""Atestado, cancelamento por inércia, e o suplente que fica chamável (019, `US5`, `T085`).

**O aluno que desaparece trava o certame.** Ele foi convocado, a matrícula aconteceu, e ele nunca
acessou o ambiente; a vaga está formalmente ocupada e materialmente vazia, e a lista de espera não
anda. Hoje a saída é uma decisão fora do sistema, anotada em algum lugar — e a vaga volta a existir
sem que nada registre quem decidiu que ela voltou.

**Aqui são dois atos, e de propósito** (`D-004`). Quem constata o fato — não acessou, não apareceu —
e quem decide a consequência dele não precisam ser a mesma pessoa; separá-los é o que torna a
decisão auditável, e é o que impede que "o prazo venceu" seja a única justificativa de alguém ter
perdido a vaga.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.atestar import atestar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import AtestadoDeFatoExterno, Convocacao
from processo_seletivo.ocupacao.application.selectors import ocupacao_do_recorte
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def contexto(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def registrar_atestado(edital, gestor, inscricao, *, chave, especie=None):
    return atestar(
        actor=gestor,
        processo_id=edital.processo_id,
        inscricao_id=inscricao,
        especie=especie or nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE,
        conclusao="Não houve nenhum acesso ao ambiente virtual até o fim do prazo.",
        referencia_do_prazo="Primeira semana letiva, item 9.4 do Edital 77/2026.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
    )


def desfechar_como(edital, gestor, convocacao_id, especie, chave, **kwargs):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=especie,
        fundamento="Cancelamento da matrícula por inércia, item 9.4 do Edital.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
        **kwargs,
    )


def test_o_atestado_registra_quem_concluiu_e_contra_qual_prazo(cenario_do_77, gestor):
    """**O sistema não detém o artefato e não infere o fato** (`D-004`).

    O que fica é a conclusão de uma pessoa competente e o prazo contra o qual ela concluiu — e a
    referência do prazo é copiada do Edital porque o sistema não a tem para ler (`R-004`).
    """
    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]

    declarado = registrar_atestado(edital, gestor, titular, chave="in-atesta")

    atestado = AtestadoDeFatoExterno.objects.get(id=declarado["id"])
    assert atestado.atestado_por == "carlos"
    assert "item 9.4" in atestado.referencia_do_prazo
    assert atestado.conclusao


def test_o_atestado_sem_conclusao_ou_sem_prazo_e_recusado(cenario_do_77, gestor):
    """Sem conclusão ele não conclui nada; sem o prazo ele não diz até quando."""
    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]

    with pytest.raises(DomainError) as vazio:
        atestar(
            actor=gestor,
            processo_id=edital.processo_id,
            inscricao_id=titular,
            especie=nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE,
            conclusao="   ",
            referencia_do_prazo="Item 9.4",
            idempotency_key="in-sem-conclusao",
            correlation_id="teste",
        )
    with pytest.raises(DomainError) as sem_prazo:
        atestar(
            actor=gestor,
            processo_id=edital.processo_id,
            inscricao_id=titular,
            especie=nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE,
            conclusao="Não acessou.",
            referencia_do_prazo="",
            idempotency_key="in-sem-prazo",
            correlation_id="teste",
        )

    assert vazio.value.code == nomes.CONCLUSAO_OBRIGATORIA
    assert sem_prazo.value.code == nomes.REFERENCIA_DO_PRAZO_OBRIGATORIA


def test_o_atestado_nao_cancela_matricula_nenhuma(cenario_do_77, gestor):
    """**Ele é insumo do desfecho, e não o desfecho.**

    Se atestar já cancelasse, quem constata o fato decidiria a consequência — e a `D-004` separou
    as duas coisas justamente porque podem ser duas pessoas.
    """
    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="in-nao-cancela-conv")
    desfechar_como(edital, gestor, convocada["id"], nomes.ACEITE, "in-nao-cancela-aceite")

    registrar_atestado(edital, gestor, titular, chave="in-nao-cancela-atesta")

    leitura = contexto(edital)
    assert titular in leitura["servidos"], "a matrícula continua efetivada"


def test_a_inercia_sem_atestado_e_recusada(cenario_do_77, gestor):
    """`atestado_obrigatorio`, e a recusa vem antes de qualquer gravação."""
    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="in-sem-atestado-conv")

    with pytest.raises(DomainError) as erro:
        desfechar_como(edital, gestor, convocada["id"], nomes.INERCIA, "in-sem-atestado")

    assert erro.value.code == nomes.ATESTADO_OBRIGATORIO


def test_o_atestado_de_outra_pessoa_nao_serve(cenario_do_77, gestor):
    """Aceitá-lo cancelaria a matrícula de quem nunca foi atestado.

    E a trilha apontaria para o fato de um terceiro — que é o pior desfecho possível numa decisão
    que tira a vaga de alguém.
    """
    edital, _, _ = cenario_do_77
    fila = contexto(edital)["fila"]
    convocada = convocar(edital, gestor, fila[0], idempotency_key="in-troca-conv")
    de_outro = registrar_atestado(edital, gestor, fila[1], chave="in-troca-atesta")

    with pytest.raises(DomainError) as erro:
        desfechar_como(
            edital,
            gestor,
            convocada["id"],
            nomes.INERCIA,
            "in-troca-desfecho",
            atestado_id=de_outro["id"],
        )

    assert erro.value.code == nomes.ATESTADO_OBRIGATORIO


def test_o_ciclo_da_inercia_devolve_a_vaga_e_o_suplente_fica_chamavel(cenario_do_77, gestor):
    """`T085`: atestado → cancelamento → suplente chamável.

    **E o cancelamento registra o atestante, não o relógio.** É a diferença entre uma vaga que
    voltou porque alguém competente concluiu que ela estava vazia, e uma vaga que voltou porque um
    `cron` achou que o prazo tinha passado.
    """
    edital, _, _ = cenario_do_77
    inicio = contexto(edital)["fila"]
    titulares, suplente = list(inicio[:2]), inicio[2]
    # **A titular já ocupa vaga desde a apuração** — é o que a `016` conta —, e foi chamada. A
    # matrícula aconteceu fora daqui; o que o sistema sabe é que a chamada não teve desfecho e que
    # alguém competente concluiu que a pessoa desapareceu.
    primeira = convocar(edital, gestor, titulares[0], idempotency_key="in-ciclo-t1")
    convocar(edital, gestor, titulares[1], idempotency_key="in-ciclo-t2")
    assert (
        ocupacao_do_recorte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None)[
            "faltando"
        ]
        == 0
    )

    atestado = registrar_atestado(edital, gestor, titulares[0], chave="in-ciclo-atesta")
    declarado = desfechar_como(
        edital,
        gestor,
        primeira["id"],
        nomes.INERCIA,
        "in-ciclo-inercia",
        atestado_id=atestado["id"],
    )

    assert erro_nao_houve(declarado)
    apurar(edital, gestor, chave="in-ciclo-apura-2", motivo="Cancelamento por inércia")

    numeros = ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert numeros["faltando"] == 1, "a vaga voltou a faltar"
    depois = contexto(edital)
    assert suplente in depois["fila"], "e a suplente ficou chamável"
    assert convocar(
        edital,
        gestor,
        suplente,
        especie=nomes.SUPLENCIA,
        idempotency_key="in-ciclo-suplente",
    )


def erro_nao_houve(declarado):
    """O desfecho foi registrado, e o efeito dele é exclusão — as duas metades do ato."""
    return declarado["especie"] == nomes.INERCIA and declarado["efeito"] == "EXCLUSAO"


def test_o_desfecho_de_inercia_cita_o_atestado_e_o_atestante(cenario_do_77, gestor):
    """Quem lê a trilha não pergunta *"o prazo venceu?"*, e sim *"quem concluiu que venceu?"*."""
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao

    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="in-cita-conv")
    atestado = registrar_atestado(edital, gestor, titular, chave="in-cita-atesta")

    declarado = desfechar_como(
        edital,
        gestor,
        convocada["id"],
        nomes.INERCIA,
        "in-cita-desfecho",
        atestado_id=atestado["id"],
    )

    desfecho = DesfechoDaConvocacao.objects.select_related("atestado").get(id=declarado["id"])
    assert str(desfecho.atestado_id) == atestado["id"]
    assert desfecho.atestado.atestado_por == "carlos"


def test_a_inercia_sucede_o_aceite_de_quem_desapareceu_depois(cenario_do_77, gestor):
    """**O caso que a `§6` da spec descreve**: quem já ocupava, aceitou, e desapareceu.

    A `FR-273` admite um desfecho por convocação, e o aceite fecha a chamada. A inércia posterior
    **sucede** aquele desfecho, com motivo: o aceite era verdadeiro quando registrado, e o que mudou
    foi o mundo depois dele. É a mesma forma que o `ResultadoEtapa` usa para a superação por
    recurso.

    *A primeira implementação não tinha sucessão de desfecho, e este caminho era estruturalmente
    impossível — a `US5` só alcançava quem nunca havia aceitado, que é o contrário do que a norma
    descreve.*
    """
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao

    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="in-suc-conv")
    desfechar_como(edital, gestor, convocada["id"], nomes.ACEITE, "in-suc-aceite")
    apurar(edital, gestor, chave="in-suc-apura-1", motivo="Aceite registrado")
    atestado = registrar_atestado(edital, gestor, titular, chave="in-suc-atesta")

    declarado = desfechar_como(
        edital,
        gestor,
        convocada["id"],
        nomes.INERCIA,
        "in-suc-inercia",
        atestado_id=atestado["id"],
        motivo="Cancelamento de matrícula por inércia, atestado em processo.",
    )

    assert declarado["efeito"] == "EXCLUSAO"
    vigente = selectors.desfecho_de(
        Convocacao.objects.prefetch_related("desfechos").get(id=convocada["id"])
    )
    assert vigente.especie == nomes.INERCIA
    assert vigente.desfecho_anterior.especie == nomes.ACEITE, "o aceite continua legível"
    assert DesfechoDaConvocacao.objects.filter(convocacao_id=convocada["id"]).count() == 2

    apurar(edital, gestor, chave="in-suc-apura-2", motivo="Cancelamento por inércia")
    numeros = ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert numeros["faltando"] == 1, "a vaga voltou a faltar"


def test_a_inercia_sem_motivo_de_sucessao_e_recusada(cenario_do_77, gestor):
    """Suceder um desfecho é dizer por quê — e a recusa nomeia o caminho, em vez de só barrar."""
    edital, _, _ = cenario_do_77
    titular = contexto(edital)["fila"][0]
    convocada = convocar(edital, gestor, titular, idempotency_key="in-sm-conv")
    desfechar_como(edital, gestor, convocada["id"], nomes.ACEITE, "in-sm-aceite")
    atestado = registrar_atestado(edital, gestor, titular, chave="in-sm-atesta")

    with pytest.raises(DomainError) as erro:
        desfechar_como(
            edital,
            gestor,
            convocada["id"],
            nomes.INERCIA,
            "in-sm-inercia",
            atestado_id=atestado["id"],
        )

    assert erro.value.code == nomes.DESFECHO_JA_REGISTRADO


def test_a_inercia_sobre_quem_nunca_ocupou_e_recusada(cenario_do_77, gestor):
    """`inercia_sem_ocupacao`: não há matrícula a cancelar, e o desfecho certo é outro.

    **Registrá-la ali cancelaria uma matrícula que não existe.** Quem foi chamado e não respondeu
    tem desfecho próprio — não atendimento à convocação —, e a recusa diz qual é.
    """
    edital, _, _ = cenario_do_77
    fila = contexto(edital)["fila"]
    suplente = fila[2]
    convocar(edital, gestor, fila[0], idempotency_key="in-so-t1")
    primeira = convocar(edital, gestor, fila[1], idempotency_key="in-so-t2")
    desfechar_como(edital, gestor, primeira["id"], nomes.DESISTENCIA_EXPRESSA, "in-so-desiste")
    apurar(edital, gestor, chave="in-so-apura", motivo="Desistência")
    chamada = convocar(
        edital, gestor, suplente, especie=nomes.SUPLENCIA, idempotency_key="in-so-suplente"
    )
    atestado = registrar_atestado(edital, gestor, suplente, chave="in-so-atesta")

    with pytest.raises(DomainError) as erro:
        desfechar_como(
            edital,
            gestor,
            chamada["id"],
            nomes.INERCIA,
            "in-so-inercia",
            atestado_id=atestado["id"],
        )

    assert erro.value.code == nomes.INERCIA_SEM_OCUPACAO
