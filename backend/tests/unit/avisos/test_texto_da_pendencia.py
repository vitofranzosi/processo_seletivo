"""O texto do aviso de pendência, como função pura (134, FR-4613 a FR-4617, D-004, D-007)."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.avisos.domain import pendencia
from processo_seletivo.avisos.domain.pendencia import Pendente
from processo_seletivo.avisos.domain.variaveis import resolver_no_envio
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar

FUSO = ZoneInfo("America/Sao_Paulo")


def _compor(pendentes, *, prazo=None):
    assunto, corpo = pendencia.compor(
        instituicao="Ifes",
        edital="Edital 72/2026",
        pendentes=pendentes,
        prazo=prazo,
        link="http://testserver/selecoes/inscricoes/x/convocacao",
        atendimento="a comissão do certame",
        assinatura="Cefor/Ifes",
    )
    # O que sai é o que o despacho resolve no envio: as chaves escapadas voltam a ser chaves.
    return (
        resolver_no_envio(assunto, nome_do_candidato="X"),
        resolver_no_envio(corpo, nome_do_candidato="X"),
    )


def test_um_documento_de_modalidade_e_uma_frase_so():
    linhas = pendencia.linhas_dos_documentos(
        [Pendente("Comprovante de residência", False), Pendente("Laudo médico", True)]
    )

    assert linhas == ["Comprovante de residência", pendencia.DOCUMENTO_DE_MODALIDADE]


def test_dois_de_modalidade_viram_uma_linha_com_a_contagem():
    linhas = pendencia.linhas_dos_documentos(
        [
            Pendente("Laudo médico", True),
            Pendente("Comprovante de residência", False),
            Pendente("Autodeclaração", True),
        ]
    )

    assert linhas == ["2 documentos da sua modalidade de concorrência", "Comprovante de residência"]


def test_o_assunto_nao_comeca_por_convocacao_e_o_rodape_e_fixo():
    assunto, corpo = _compor([Pendente("Comprovante de residência", False)])

    assert assunto == "Ifes · Edital 72/2026: há documento da sua convocação para revisar"
    assert not assunto.startswith("Convocação")
    assert "—\nEste aviso não é a convocação e não altera o seu prazo." in corpo
    assert corpo.startswith("Há um documento da sua convocação no Edital 72/2026 que precisa")


def test_varios_documentos_no_plural():
    _, corpo = _compor([Pendente("A", False), Pendente("B", False)])

    assert corpo.startswith("Há documentos da sua convocação no Edital 72/2026 que precisam")


def test_o_prazo_tem_dia_data_e_hora_e_nenhuma_contagem():
    vencimento = datetime(2026, 11, 12, 20, 0, tzinfo=UTC)  # 17h00 em São Paulo, quinta-feira
    prazo = apresentar(vencimento, datetime(2026, 11, 8, 12, 0, tzinfo=UTC), FUSO)

    _, corpo = _compor([Pendente("A", False)], prazo=prazo)

    assert "O prazo continua sendo até quinta-feira, 12/11/2026, às 17h00." in corpo
    assert "faltam" not in corpo


def test_sem_vencimento_o_prazo_e_o_da_convocacao():
    _, corpo = _compor([Pendente("A", False)])

    assert "O prazo continua o da sua convocação." in corpo


def test_chave_no_nome_do_documento_chega_como_foi_escrita():
    _, corpo = _compor([Pendente("Anexo {I}", False)])

    assert "- Anexo {I}" in corpo


def test_sem_pendente_nao_ha_texto():
    with pytest.raises(ValueError):
        _compor([])
