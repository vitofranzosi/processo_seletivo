"""O que está em curso no conjunto (100, FR-2576, FR-2580, FR-2581, FR-2589)."""

import pytest

from tests.fixtures.relatorio import montar_cenario
from tests.integration.relatorio_consolidado.conftest import conjunto, ler, texto_do_documento

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_encerrado_com_convocacao_no_prazo_e_registros_na_trilha(tres_editais):
    c = ler(conjunto("criterio=numero&ano=2026"))
    assert c.encerrados_com_pendencia == 1
    assert ("convocação aguardando resposta", 1, 1) in c.pendencias_por_tipo
    (providencia,) = c.providencias_por_edital
    assert providencia.edital.number == "61"
    assert c.pontos_de_atencao[0][0] == (
        "1 Edital está encerrado no GPS, mas ainda tem providência registrada."
    )
    assert c.pontos_de_atencao[1][0] == (
        "1 Edital tem registros na trilha de auditoria depois do encerramento."
    )
    assert c.pontos_de_atencao[2][0] == "O GPS não registra matrículas."
    texto = texto_do_documento(c)
    assert "não todo acontecimento" in texto
    assert "convocações aceitas, e não matrículas efetivadas" in texto


def test_perfil_sem_inscricao_nao_vira_pendencia_no_conjunto(db):
    vazio = montar_cenario(final="sem-pendencia", numero="66", tecnicos=0)
    c = ler(conjunto(f"criterio=manual&edital={vazio.edital.pk}"))
    assert c.pendencias_por_tipo == []
    assert c.marcos_declarados == 1 and c.editais_definitivos == 1
    assert c.providencias == "nenhuma providência pendente registrada no GPS"
