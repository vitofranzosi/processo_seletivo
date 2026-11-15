"""O que a agenda não faz (167, T059, FR-7250, FR-7251, FR-7252).

A agenda diz quando cada pessoa é atendida. Nenhuma operação dela — configurar, montar, conferir,
publicar — grava Resultado de Etapa (a Ocorrência é um deles), Avaliação, convocação ou prazo; as
orientações são só texto; e nenhuma tabela dela tem campo de presença, nota ou prazo.
"""

import pytest
from django.apps import apps

from processo_seletivo.agendamento.application import conferir, leitura
from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _fora_da_agenda():
    return {
        modelo.__name__: modelo.objects.count()
        for modelo in (ResultadoEtapa, Avaliacao, Convocacao, ComunicacaoEmitida)
    }


def test_nenhuma_operacao_da_agenda_grava_fora_dela(gestor, edital_a, etapa_a2, inscricoes):
    antes = _fora_da_agenda()

    montar_completa(gestor, edital_a, etapa_a2)
    conferir.conferencia(actor=gestor, edital=edital_a, etapa_id=etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2)

    assert _fora_da_agenda() == antes


def test_as_orientacoes_sao_so_texto(gestor, edital_a, etapa_a2, inscricoes):
    montar_completa(gestor, edital_a, etapa_a2)
    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)

    campo = type(agenda)._meta.get_field("orientacoes")
    assert campo.get_internal_type() == "TextField"
    assert agenda.orientacoes == "Tenha o documento."


@pytest.mark.parametrize("proibido", ["presen", "ausen", "nota", "pontua", "prazo", "parecer"])
def test_nenhuma_tabela_da_agenda_tem_campo_de_presenca_nota_ou_prazo(proibido):
    campos = [
        f"{modelo.__name__}.{campo.name}"
        for modelo in apps.get_app_config("agendamento").get_models()
        for campo in modelo._meta.get_fields()
        if proibido in campo.name
    ]
    assert campos == []
