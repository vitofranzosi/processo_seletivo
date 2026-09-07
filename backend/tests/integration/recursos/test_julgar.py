"""A decisão de mérito, e o que cada espécie produz — ou deixa de produzir.

**A atomicidade é a substância** (FR-056). Decisão sem sucessor é um deferimento que o candidato lê
e que não valeu; sucessor sem decisão é um Resultado alterado sem fonte jurídica. As duas metades
são inúteis, e a única forma de nunca ter uma delas é nunca gravar uma sem a outra.

```text
INDEFERIDO               nenhum efeito sobre Resultado
CORRECAO_FIXADA          exatamente um sucessor, na mesma transação
REAVALIACAO_DETERMINADA  nenhum sucessor — o resultado corrigido ainda não existe
PROVIDENCIA_A_JUSANTE    nomeia a providência e não a executa
```

**O anterior permanece íntegro.** Superar não é reescrever: o Resultado atacado continua com a
pontuação, a consequência e o motivo que afirmou, e é isso que torna a correção auditável em vez de
invisível (D-003 da decisão C).
"""

from decimal import Decimal

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.application.selectors import historico_do_par
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=110, codigo="0810"
    )


def decidir_por_recurso(peca, **extra):
    argumentos = {
        "actor": julgador(),
        "recurso_id": peca["recurso"].id,
        "especie": DecisaoRecurso.Especie.CORRECAO_FIXADA,
        "motivacao": "O parecer não enfrentou o documento juntado na inscrição.",
        "etapa_id": peca["cenario"]["etapa"],
        "pontuacao": Decimal("82.0000"),
        "assinatura_do_resultado": str(peca["superado"].id),
        "idempotency_key": "julgar-us4",
    }
    return julgar(**{**argumentos, **extra})


# ---------------------------------------------------------------------------
# T063 — a atomicidade
# ---------------------------------------------------------------------------


def test_decisao_e_sucessor_nascem_juntos(peca):
    decisao, sucessor = decidir_por_recurso(peca)

    assert decisao.especie == DecisaoRecurso.Especie.CORRECAO_FIXADA
    assert sucessor is not None
    assert sucessor.resultado_anterior_id == peca["superado"].id
    assert sucessor.decisao_id == decisao.id
    assert (
        ResultadoEtapa.vigentes.get(
            inscricao=peca["inscricao"], etapa_id=peca["cenario"]["etapa"]
        ).pk
        == sucessor.pk
    )


def test_invariante_que_falha_derruba_a_transacao_inteira(peca):
    """Não fica decisão sem efeito, nem efeito sem decisão (FR-056, SC-007).

    A invariante escolhida é a da conclusão: uma correção fixada sem a pontuação que a forma da
    Etapa exige. A recusa acontece **depois** de o comando ter começado a decidir, e o que se prova
    é que nada sobrou — nem a decisão, nem um sucessor órfão.
    """
    with pytest.raises(DomainError) as recusa:
        decidir_por_recurso(peca, pontuacao=None)

    assert recusa.value.code == "appeal_correction_incomplete"
    assert not DecisaoRecurso.objects.exists()
    assert ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).count() == 0


def test_julgar_sem_admissao_e_recusado(gestor, api_client, manager_headers, process_payload):
    """Julgar o mérito exige juízo positivo — e a recusa vem antes de gravar (FR-036)."""
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=111,
        codigo="0811",
        admitir_a_peca=False,
    )

    with pytest.raises(DomainError) as recusa:
        decidir_por_recurso(peca)

    assert recusa.value.code == "appeal_not_admitted"
    assert recusa.value.status == 409
    assert not DecisaoRecurso.objects.exists()


def test_a_segunda_decisao_e_recusada(peca):
    decidir_por_recurso(peca)

    with pytest.raises(DomainError) as recusa:
        decidir_por_recurso(
            peca,
            especie=DecisaoRecurso.Especie.INDEFERIDO,
            etapa_id=None,
            pontuacao=None,
            assinatura_do_resultado="",
            idempotency_key="julgar-us4-b",
        )

    assert recusa.value.code == "appeal_already_judged"
    assert DecisaoRecurso.objects.count() == 1


def test_motivacao_vazia_e_recusada_inclusive_no_indeferimento(peca):
    """Indeferir sem dizer por quê é decisão que ninguém consegue discutir (FR-047)."""
    with pytest.raises(DomainError) as recusa:
        decidir_por_recurso(
            peca, especie=DecisaoRecurso.Especie.INDEFERIDO, motivacao="  \n ", etapa_id=None
        )

    assert recusa.value.code == "appeal_reason_required"
    assert not DecisaoRecurso.objects.exists()


# ---------------------------------------------------------------------------
# T064 — o sucessor, e a integridade do anterior
# ---------------------------------------------------------------------------


def test_o_sucessor_tem_origem_em_recurso_e_nao_cita_avaliacao(peca):
    _decisao, sucessor = decidir_por_recurso(peca)

    assert sucessor.origem == ResultadoEtapa.Origem.RECURSO
    assert sucessor.avaliacao_id is None
    assert sucessor.decisao_id is not None
    assert sucessor.motivo_da_superacao != ""


def test_o_anterior_permanece_intacto(peca):
    """Superar não é reescrever — e é isso que torna a correção auditável (FR-051, SC-007)."""
    superado = peca["superado"]
    antes = (superado.pontuacao, superado.consequencia, superado.motivo, superado.consolidado_por)

    decidir_por_recurso(peca)

    superado.refresh_from_db()
    assert (
        superado.pontuacao,
        superado.consequencia,
        superado.motivo,
        superado.consolidado_por,
    ) == antes


def test_o_historico_do_par_mostra_os_dois_em_ordem(peca):
    """A consulta que existe para ver o superado ao lado do vigente (FR-064)."""
    _decisao, sucessor = decidir_por_recurso(peca)

    historico = historico_do_par(peca["inscricao"].id, peca["cenario"]["etapa"])

    assert [linha["resultado"].pk for linha in historico] == [peca["superado"].pk, sucessor.pk]
    assert historico[0]["vigente"] is False
    assert historico[1]["vigente"] is True
    assert historico[1]["recurso"] == peca["recurso"].protocolo


def test_a_consequencia_e_derivada_e_nao_digitada(peca):
    """A regra publicada da Etapa decide, e o julgador só fixa a conclusão (FR-059).

    A correção **melhora** a nota — de 55 para 58, e por isso não esbarra na vedação de piora — e
    ainda assim o resultado continua eliminando, porque 58 está abaixo da mínima publicada. É o
    caso que separa deferir de habilitar: uma consequência digitada permitiria declarar habilitação
    com nota abaixo da mínima, contradizendo a norma que a própria decisão cita.
    """
    minima = _nota_minima(peca)
    assert peca["superado"].pontuacao < minima, "o cenário precisa partir de uma eliminação"

    decisao, sucessor = decidir_por_recurso(peca, pontuacao=Decimal("58.0000"))

    assert Decimal("58.0000") > peca["superado"].pontuacao, "a correção precisa melhorar a nota"
    assert Decimal("58.0000") < minima, "e ainda assim ficar abaixo da mínima publicada"
    assert decisao.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
    assert sucessor.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
    assert "nota mínima" in sucessor.motivo


def _nota_minima(peca):
    from processo_seletivo.recursos.domain.consequencia import etapa_publicada
    from processo_seletivo.resultados.domain.regra import nota_minima

    etapa = etapa_publicada(peca["recurso"].versao, peca["cenario"]["etapa"])
    return nota_minima(etapa)


def test_o_resultado_lido_obsoleto_recusa(peca):
    """Decidir sobre o que já mudou corrigiria o Resultado errado (FR-100)."""
    with pytest.raises(DomainError) as recusa:
        decidir_por_recurso(peca, assinatura_do_resultado="outro-identificador")

    assert recusa.value.code == "stale_stage_result"
    assert recusa.value.status == 409


# ---------------------------------------------------------------------------
# As espécies sem efeito sobre Resultado
# ---------------------------------------------------------------------------


def test_indeferir_nao_produz_sucessor(peca):
    decisao, sucessor = decidir_por_recurso(
        peca,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        etapa_id=None,
        pontuacao=None,
        assinatura_do_resultado="",
    )

    assert sucessor is None
    assert decisao.resultado_protegido_id is None
    assert decisao.consequencia == ""
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def test_a_providencia_a_jusante_nomeia_e_nao_executa(peca):
    """Executá-la aqui daria a quem julga a autoridade da 015 e da 017 (FR-049).

    O que a decisão faz é **nomear** a providência na motivação. Quem a executa é quem tem a
    autoridade do ato, e o cumprimento se prova pela citação que o ato sucessor carrega.
    """
    atos_antes = _atos_e_publicacoes()

    decisao, sucessor = decidir_por_recurso(
        peca,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato de ordenação do marco, corrigindo o critério de desempate.",
        etapa_id=None,
        pontuacao=None,
        assinatura_do_resultado="",
    )

    assert sucessor is None
    assert decisao.resultado_protegido_id is None
    assert "Emita-se novo ato" in decisao.motivacao
    assert _atos_e_publicacoes() == atos_antes, "julgar não pratica ato a jusante"


def test_a_reavaliacao_determinada_nao_antecipa_resultado(peca):
    """Nenhum sucessor: o resultado corrigido ainda não existe para ser declarado (D-009)."""
    decisao, sucessor = decidir_por_recurso(
        peca,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        pontuacao=None,
    )

    assert sucessor is None
    assert decisao.resultado_protegido_id == peca["superado"].id
    assert decisao.consequencia == ""
    assert decisao.pontuacao is None
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def _atos_e_publicacoes():
    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    return (AtoDeOrdenacao.objects.count(), PublicacaoResultado.objects.count())


# ---------------------------------------------------------------------------
# T069 — a trilha
# ---------------------------------------------------------------------------


def test_a_trilha_registra_os_quatro_atos_sem_copiar_conteudo(peca):
    """Um evento por agregado, e **sem** fundamentação nem pontuação (FR-094, FR-095).

    Fundamentação e nota são conteúdo do juízo, e não registro de que houve juízo — a mesma linha
    que a 012 traçou ao manter parecer e pontuação fora da trilha. Copiá-las criaria uma segunda
    cópia do conteúdo sensível, num lugar com outro regime de acesso.
    """
    _decisao, sucessor = decidir_por_recurso(peca)

    operacoes = set(RegistroAuditoria.objects.values_list("operation", flat=True))
    assert {"recurso:interpor", "recurso:admitir", "recurso:julgar", "resultado:superar"} <= (
        operacoes
    )

    corpo = " ".join(
        f"{evento.previous_state} {evento.new_state} {evento.reason}"
        for evento in RegistroAuditoria.objects.filter(operation__startswith="recurso:")
    )
    assert peca["recurso"].fundamentacao not in corpo
    assert "82" not in corpo
    assert sucessor.pontuacao == Decimal("82.0000")


# ---------------------------------------------------------------------------
# T124 — nada é notificado
# ---------------------------------------------------------------------------


def test_nada_e_notificado_em_nenhum_dos_tres_atos(peca, mailoutbox):
    """O candidato descobre consultando, e é por isso que a decisão precisa ser legível lá.

    Notificar seria funcionalidade nova, com regime próprio de falha e de reenvio — e a 018 declara
    que não a tem. O teste existe para que ninguém a acrescente por engano achando que faltava
    (FR-109).
    """
    # A fixture já percorreu a interposição e a admissibilidade: o que se mede aqui é o silêncio
    # dos três atos, e não só o do julgamento.
    assert peca["recurso"].juizos.exists(), "a fixture precisa ter admitido a peça"

    decidir_por_recurso(peca)

    assert len(mailoutbox) == 0
    assert DecisaoRecurso.objects.count() == 1
