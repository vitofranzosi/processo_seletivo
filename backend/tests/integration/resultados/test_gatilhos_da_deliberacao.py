"""O banco garante a proveniência do Resultado deliberado (165, FR-7065, research T-006).

A invariante da `013` foi revista, e com a mesma força: quem chega por fora da aplicação também não
grava uma deliberação incoerente.

```text
contagem   pareceres ligados ≠ a contagem gravada         recusado no COMMIT
cruzado    parecer de outra inscrição                      recusado no INSERT
único      Avaliação já ligada, ou já fonte de Resultado   recusado
imutável   UPDATE e DELETE nas duas tabelas novas          recusados
```
"""

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.avaliacoes.models import ExposicaoAoParecer
from processo_seletivo.resultados.models import ParecerDaDeliberacao, ResultadoEtapa
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    consolidar_na,
    distribuir_na_hetero,
    montar_colegiada,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

F, D = "FAVORAVEL", "DESFAVORAVEL"


def _deliberado(gestor, api_client, manager_headers, seed):
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=seed)
    maria, joana, _ = cenario["inscricoes"]
    distribuir_na_hetero(cenario, gestor, [maria, joana], chave=f"hetero-{seed}")
    pareceres_maria = concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": F})
    pareceres_joana = concluir_pareceres(cenario, joana, {"ana": F, "bruno": F})
    consolidar_na(cenario, cenario["hetero"], [maria], chave=f"consolidar-{seed}")
    resultado = ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=maria)
    return cenario, resultado, pareceres_maria, pareceres_joana


def test_parecer_de_outra_inscricao_e_recusado(gestor, api_client, manager_headers):
    _cenario, resultado, _maria, joana = _deliberado(gestor, api_client, manager_headers, 1661)
    with pytest.raises(DatabaseError, match="does not match its result"):
        with transaction.atomic():
            ParecerDaDeliberacao.objects.create(resultado=resultado, avaliacao=joana[0])


def test_contagem_divergente_e_recusada_no_commit(gestor, api_client, manager_headers):
    """O adiável: dois pareceres de Joana ligados a um Resultado que se diz de dois favoráveis e um
    desfavorável não sobrevivem ao `COMMIT`."""
    cenario, resultado, _maria, joana = _deliberado(gestor, api_client, manager_headers, 1662)
    inscricao = joana[0].atribuicao.inscricao
    with pytest.raises(DatabaseError, match="does not match its opinions"):
        with transaction.atomic():
            forjado = ResultadoEtapa.objects.create(
                inscricao=inscricao,
                edital=cenario["edital"],
                etapa_id=cenario["hetero"],
                origem=ResultadoEtapa.Origem.DELIBERACAO,
                versao_id=resultado.versao_id,
                forma="DECISORIA",
                sentido=F,
                consequencia="HABILITADA",
                motivo="forjado",
                consolidado_em=resultado.consolidado_em,
                consolidado_por="intruso",
                regra_de_deliberacao="MAJORITY",
                favoraveis=2,
                desfavoraveis=1,
            )
            for avaliacao in joana:
                ParecerDaDeliberacao.objects.create(resultado=forjado, avaliacao=avaliacao)
    assert not ResultadoEtapa.objects.filter(inscricao=inscricao, etapa_id=cenario["hetero"])


def test_avaliacao_ja_ligada_nao_se_liga_de_novo(gestor, api_client, manager_headers):
    _cenario, resultado, maria, _joana = _deliberado(gestor, api_client, manager_headers, 1663)
    with pytest.raises(DatabaseError):
        with transaction.atomic():
            ParecerDaDeliberacao.objects.create(resultado=resultado, avaliacao=maria[0])


def test_as_duas_tabelas_novas_sao_append_only(gestor, api_client, manager_headers):
    cenario, resultado, _maria, _joana = _deliberado(gestor, api_client, manager_headers, 1664)
    ExposicaoAoParecer.objects.create(
        edital=cenario["edital"],
        etapa_id=cenario["hetero"],
        inscricao=resultado.inscricao,
        pessoa="maria",
        registrada_em=resultado.consolidado_em,
    )
    for sql in (
        "UPDATE resultados_parecer_da_deliberacao SET avaliacao_id = avaliacao_id",
        "DELETE FROM resultados_parecer_da_deliberacao",
        "UPDATE avaliacoes_exposicao_ao_parecer SET pessoa = 'outra'",
        "DELETE FROM avaliacoes_exposicao_ao_parecer",
    ):
        with pytest.raises(DatabaseError, match="append-only"):
            with transaction.atomic(), connection.cursor() as cursor:
                cursor.execute(sql)


def test_resultado_unico_nao_cita_parecer_de_deliberacao(gestor, api_client, manager_headers):
    """Um parecer fundamenta no máximo um Resultado, nos dois ramos."""
    cenario, resultado, maria, _joana = _deliberado(gestor, api_client, manager_headers, 1665)
    with pytest.raises(DatabaseError):
        with transaction.atomic():
            ResultadoEtapa.objects.create(
                inscricao=resultado.inscricao,
                edital=cenario["edital"],
                etapa_id=cenario["hetero"],
                origem=ResultadoEtapa.Origem.AVALIACAO,
                avaliacao=maria[0],
                versao_id=maria[0].versao_id,
                forma="DECISORIA",
                sentido=D,
                consequencia="ELIMINADA",
                motivo="forjado",
                consolidado_em=resultado.consolidado_em,
                consolidado_por="intruso",
            )
