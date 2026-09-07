"""Deferir determinando reavaliação — a decisão que **não antecipa** o resultado.

```text
decisão      determina reavaliar, e cita o Resultado que protege
             nenhum sucessor nasce: o resultado corrigido ainda não existe
avaliação    alguém reavalia, pelas operações que já existem
consolidação a exceção única — e é ela que cria o sucessor, citando a decisão
```

**Declarar a consequência aqui seria afirmar o que ninguém apurou** (D-009). A decisão diz que a
Etapa será reavaliada; qual será a nota é matéria de quem avalia, e antecipá-la faria a decisão
substituir a avaliação em vez de determiná-la.
"""

from decimal import Decimal

import pytest

from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.application.selectors import (
    reavaliacao_pendente_do_par,
    reavaliacoes_pendentes,
)
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=116, codigo="0816"
    )


def determinar_reavaliacao(peca):
    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso do que a concluiu.",
        etapa_id=peca["cenario"]["etapa"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-us5",
    )


def test_deferida_a_reavaliacao_zero_sucessores_existem(peca):
    """Até a consolidação, nada mudou no Resultado — e é isso que a espécie promete (SC-009)."""
    decisao, sucessor = determinar_reavaliacao(peca)

    assert sucessor is None
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()
    assert decisao.consequencia == ""
    assert decisao.pontuacao is None
    assert decisao.forma == ""
    assert decisao.resultado_protegido_id == peca["superado"].id


def test_o_vigente_do_par_continua_sendo_o_resultado_atacado(peca):
    determinar_reavaliacao(peca)

    vigente = ResultadoEtapa.vigentes.get(
        inscricao=peca["inscricao"], etapa_id=peca["cenario"]["etapa"]
    )

    assert vigente.pk == peca["superado"].pk


def test_a_pendencia_nasce_da_decisao_e_e_derivada(peca):
    """Derivada, e nunca coluna (D-010, FR-066).

    O cumprimento é a existência do sucessor do Resultado protegido, e não um campo a alternar. Uma
    coluna `cumprida` seria estado a manter coerente onde a existência de linha já responde — e o
    primeiro lugar onde ela apareceria é justamente numa tela de organização da Etapa.

    **Que a pendência some quando cumprida é provado em `tests/integration/resultados`**, onde o
    cumprimento acontece pelo caminho real: a consolidação da nova avaliação. Forjá-lo aqui exigiria
    gravar um sucessor de origem `RECURSO` citando uma decisão que não fixou correção — e a trigger
    recusa isso, com razão.
    """
    determinar_reavaliacao(peca)
    edital = peca["cenario"]["edital"]
    etapa = peca["cenario"]["etapa"]

    assert peca["inscricao"].id in reavaliacoes_pendentes(edital, etapa_id=etapa)
    assert reavaliacao_pendente_do_par(peca["inscricao"].id, etapa) is not None


def test_a_pendencia_nao_alcanca_outra_etapa(peca):
    """A decisão alcança **um par**, e não a inscrição inteira."""
    determinar_reavaliacao(peca)

    outra = peca["cenario"]["primeira"]

    assert reavaliacao_pendente_do_par(peca["inscricao"].id, outra) is None
    assert not reavaliacoes_pendentes(peca["cenario"]["edital"], etapa_id=outra)


def test_a_decisao_de_reavaliacao_nao_declara_grandeza(peca):
    """As constraints já o exigem; o teste registra **por que** elas existem.

    Uma pontuação pendurada numa reavaliação seria afirmação sem efeito — e, pior, um convite a que
    alguém a consumisse depois como se fosse a decisão.
    """
    from django.db.utils import IntegrityError

    from tests.fixtures.recursos import decidir

    with pytest.raises(IntegrityError, match="ck_decisao_sem_grandeza_residual"):
        decidir(
            peca["recurso"],
            especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
            protegido=peca["superado"],
            forma="PONTUADA",
            pontuacao=Decimal("80.0000"),
        )
