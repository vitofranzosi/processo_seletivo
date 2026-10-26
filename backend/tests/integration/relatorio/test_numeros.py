"""Os números do relatório são os das telas donas (099, SC-933).

Cada número é conferido contra a leitura que a tela de gestão correspondente faz, e não contra uma
segunda conta escrita aqui: o defeito que se quer pegar é a derivação do relatório divergir da tela.
Os valores esperados são os da maquete v2, que o usuário aprovou.
"""

from decimal import Decimal

import pytest

from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.models import SituacaoDivulgada
from processo_seletivo.interface import supervisao, visao_geral
from processo_seletivo.interface.relatorio_do_edital import interpretar, texto_do_indicador
from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
from processo_seletivo.recursos.application.selectors import recursos_do_edital
from tests.fixtures.relatorio import MARCO_PROF, PPP, PROF, PROVA, REFERENCIA
from tests.integration.relatorio.conftest import ler

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _indicador(relatorio, rotulo):
    return next(i for i in relatorio.indicadores if i.rotulo == rotulo)


def test_os_indicadores_sao_os_da_maquete_e_os_das_telas_donas(pendente):
    """FR-2528 a FR-2533: seis números, cada um com a base, iguais aos da tela dona."""
    relatorio = ler(pendente)
    edital = pendente.edital

    contagem = visao_geral.contagens_por_edital([edital])[edital.id]
    assert interpretar(_indicador(relatorio, "inscrições enviadas").numero) == str(
        sum(contagem["submetidas"].values())
    )
    assert texto_do_indicador(_indicador(relatorio, "inscrições enviadas")) == "38"
    assert "4 iniciadas e não enviadas" in _indicador(relatorio, "inscrições enviadas").base

    assert texto_do_indicador(_indicador(relatorio, "vagas imediatas")) == "2"
    assert texto_do_indicador(_indicador(relatorio, "inscrições por vaga")) == "13,0"
    assert texto_do_indicador(_indicador(relatorio, "resultados definitivos publicados")) == (
        "2 de 2"
    )

    ocupadas = sum(
        r["ocupadas"] or 0
        for r in recortes_do_marco(edital=edital, perfil_id=PROF, marco_id=MARCO_PROF)
    )
    habilitadas = _indicador(relatorio, "vagas com inscrição classificada e habilitada")
    assert habilitadas.numero.valor == ocupadas == 2
    assert "Não é matrícula" in habilitadas.base

    aceitas = _indicador(relatorio, "convocações aceitas")
    assert texto_do_indicador(aceitas) == "1 de 2"
    assert "1 aguardando resposta até 30/10/2026" in aceitas.base


def test_a_tabela_por_perfil_une_as_listas_e_nao_soma_os_marcos(pendente):
    """FR-2535 e FR-2541: classificação publicada é por inscrição, unindo ampla e reservada."""
    relatorio = ler(pendente)
    edital = pendente.edital
    professor = next(p for p in relatorio.perfis if p.id == PROF)

    por_lista = {}
    for lista in (None, PPP):
        publicacao = vigente_do_marco(edital=edital, marco_id=MARCO_PROF, lista_id=lista)
        por_lista[lista] = set(
            SituacaoDivulgada.objects.filter(
                publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.CLASSIFICADA
            ).values_list("inscricao_id", flat=True)
        )
    assert professor.classificadas.valor == len(por_lista[None] | por_lista[PPP]) == 14
    assert [(lista.lista, lista.classificadas.valor) for lista in professor.listas] == [
        ("Ampla concorrência", 14),
        ("Pessoas pretas, pardas e indígenas", 5),
    ]
    assert professor.por_vaga.valor == Decimal("13.0")
    tecnico = next(p for p in relatorio.perfis if p.id != PROF)
    assert interpretar(tecnico.por_vaga) == "só cadastro de reserva"
    assert interpretar(tecnico.habilitadas_nas_vagas) == "só cadastro de reserva"


def test_as_etapas_contam_avaliadas_e_ocorrencias_sem_presenca(pendente):
    """FR-2540: avaliadas, habilitadas, eliminadas e por ocorrência — nunca presentes."""
    relatorio = ler(pendente)
    professor = next(p for p in relatorio.perfis if p.id == PROF)
    prova = professor.etapas[0]
    assert (prova.avaliadas, prova.habilitadas, prova.eliminadas, prova.por_ocorrencia) == (
        25,
        14,
        11,
        1,
    )
    assert [e.nome for e in professor.etapas] == [
        "Prova objetiva",
        "Análise de títulos",
        "Análise documental",
    ]
    tecnico = next(p for p in relatorio.perfis if p.id != PROF)
    # A Etapa governada é do marco do Professor; o Técnico não passa por ela.
    assert [e.nome for e in tecnico.etapas] == ["Prova objetiva", "Análise de títulos"]
    assert PROVA


def test_procura_recursos_e_retificacao(pendente):
    """FR-2536 e FR-2537: a série da Supervisão, os recursos da tela dona e o antes e depois."""
    relatorio = ler(pendente)
    edital = pendente.edital
    assert sum(p.quantidade for p in relatorio.serie) == 38
    assert relatorio.no_periodo_acrescentado == 13
    from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
    from processo_seletivo.publicacoes.application.selectors import effective_version

    vigente = effective_version(edital_id=edital.id, at=REFERENCIA).content
    serie = supervisao.serie_do_edital(
        edital, periodo_de_inscricoes(vigente, REFERENCIA), REFERENCIA
    )
    assert tuple(serie) == relatorio.serie

    assert relatorio.recursos.apresentados == len(list(recursos_do_edital(edital))) == 3
    assert (relatorio.recursos.indeferidos, relatorio.recursos.nao_admitidos) == (2, 1)

    (retificacao,) = relatorio.retificacoes
    (alteracao,) = retificacao.alteracoes
    assert (alteracao["antes"], alteracao["depois"]) == ("30/08/2026 23:59", "04/09/2026 23:59")
    assert retificacao.justificativa == "Prorrogação do período de inscrições."


def test_o_resultado_substituido_conta_so_o_vigente(pendente):
    """O preliminar sucedido pelo definitivo não soma: o relatório lê a publicação vigente."""
    relatorio = ler(pendente)
    professor = next(p for p in relatorio.perfis if p.id == PROF)
    assert professor.natureza_do_resultado == "definitivo"
    assert {lista.natureza for lista in professor.listas} == {"Resultado definitivo"}
    titulos = [d.titulo for d in relatorio.documentos]
    assert sum(t.startswith("Resultado preliminar") for t in titulos) == 3
    assert sum(t.startswith("Resultado definitivo") for t in titulos) == 3
