"""Encerrado não é concluído: a espécie e as duas situações (099, FR-2522 a FR-2526, SC-935)."""

import pytest

from processo_seletivo.interface import relatorio_do_edital as rel
from tests.fixtures.relatorio import REFERENCIA_ABERTA, dia, montar_cenario
from tests.integration.relatorio.conftest import ler

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_encerrado_com_convocacao_no_prazo_e_acompanhamento(pendente):
    """A maquete v2: o Edital encerrado, a reservada no prazo, e um registro depois."""
    relatorio = ler(pendente)
    assert relatorio.especie == rel.ACOMPANHAMENTO
    assert relatorio.situacao_no_gps == "Encerrado em 20/10/2026"
    assert relatorio.pendencias == [
        "Professor de Informática: 1 convocação aguardando resposta, até 30/10/2026"
    ]
    assert relatorio.especie_explicada == "ainda há providência em curso."
    rotulos = [rotulo for rotulo, _, _ in relatorio.posteriores]
    assert rotulos == ["desfecho de convocação", "nova apuração das vagas"]
    titulos = [titulo for titulo, _ in relatorio.pontos_de_atencao]
    assert titulos == [
        "O Edital está encerrado no GPS, mas ainda há providência pendente.",
        "A trilha de auditoria tem 2 registros depois do encerramento.",
        "O GPS não registra matrículas.",
    ]


def test_prazo_encerrado_sem_resposta_e_pendencia_e_nao_desfecho(pendente):
    """Caso-limite: o não atendimento só existe quando a comissão o registra (`019`)."""
    relatorio = ler(pendente, agora=dia(1, 11, 9))
    assert relatorio.pendencias == [
        "Professor de Informática: 1 convocação com prazo encerrado sem registro de resposta"
    ]
    assert relatorio.especie == rel.ACOMPANHAMENTO


def test_encerrado_sem_pendencia_e_encerramento_e_nao_diz_concluido(db):
    """FR-2525: sem pendência registrada, encerramento — e o limite do que o GPS acompanha."""
    cenario = montar_cenario(final="sem-pendencia")
    relatorio = ler(cenario)
    assert relatorio.especie == rel.ENCERRAMENTO
    assert relatorio.providencias == "nenhuma providência pendente registrada no GPS"
    assert "não há providência pendente registrada no GPS" in relatorio.especie_explicada
    assert "como a matrícula, não estão refletidas" in relatorio.especie_explicada
    assert relatorio.posteriores == []
    textos = " ".join(relatorio.frases + [t for p in relatorio.pontos_de_atencao for t in p])
    assert "concluíd" not in textos.lower()


def test_inscricoes_abertas_e_acompanhamento_com_numeros_parciais(db):
    """Edital publicado, período correndo: parcial, e etapas sem registro não dizem 0."""
    cenario = montar_cenario(final="aberto")
    relatorio = ler(cenario, agora=REFERENCIA_ABERTA)
    assert relatorio.especie == rel.ACOMPANHAMENTO
    assert relatorio.periodo_aberto
    enviadas = next(i for i in relatorio.indicadores if i.rotulo == "inscrições enviadas")
    assert enviadas.numero.parcial
    assert "segue aberto" in " ".join(relatorio.frases)
    assert any("ainda não divulgado" in p for p in relatorio.pendencias)
    professor, tecnico = relatorio.perfis
    assert rel.interpretar(professor.classificadas) == "ainda não divulgado"
    # Em 20/08 o Técnico tem menos de cinco inscrições, e o Professor é omitido com ele, para que
    # o detalhe do Técnico não se deduza dos totais (100, FR-2587). As etapas sem registro, que
    # este caso também cobria, estão no unitário de `_linhas_das_etapas`.
    assert tecnico.motivo_da_omissao == rel.FRASE_DE_PRIVACIDADE
    assert professor.motivo_da_omissao == rel.FRASE_COMPLEMENTAR
    assert professor.etapas == () and professor.convocacoes is None


def test_cancelado_e_interrupcao_sem_resultado_como_pendencia(db):
    cenario = montar_cenario(final="cancelado")
    relatorio = ler(cenario)
    assert relatorio.especie == rel.INTERRUPCAO
    assert relatorio.situacao_no_gps == "Cancelado em 10/09/2026"
    assert relatorio.pendencias == []
    assert relatorio.frases[0] == "O Edital foi cancelado em 10/09/2026."


def test_comunicacao_depois_do_encerramento_conta_como_registro_posterior(pendente):
    """FR-2526: a mensagem enviada depois do encerramento é auditada sob a comunicação emitida."""
    from processo_seletivo.convocacao.application.comunicar import comunicar
    from tests.fixtures.relatorio import PPP, em

    with em(dia(22, 10, 9)):
        comunicar(
            actor=pendente.presidencia,
            processo_id=pendente.processo.id,
            convocacao_id=pendente.convocacoes[PPP]["id"],
            idempotency_key="099-comunicar",
            correlation_id="teste-099",
            endereco_do_portal="https://gps.exemplo/inscricoes/",
        )
    rotulos = [rotulo for rotulo, _, _ in ler(pendente).posteriores]
    assert "comunicação de convocação" in rotulos
