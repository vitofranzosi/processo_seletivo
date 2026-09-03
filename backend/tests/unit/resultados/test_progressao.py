"""A Etapa anterior, e todas as anteriores — sobre ordem publicada que não é contígua."""

from uuid import UUID

from processo_seletivo.resultados.domain.progressao import etapa_anterior, etapas_anteriores

# Identidades reais, e não rótulos: `etapas_vigentes` chaveia por UUID e o conteúdo publicado
# traz string, de modo que a normalização faz parte do que esta função promete.
E1 = UUID("00000000-0000-0000-0000-0000000000e1")
E2 = UUID("00000000-0000-0000-0000-0000000000e2")
E3 = UUID("00000000-0000-0000-0000-0000000000e3")


def vigentes(*pares):
    return {identidade: {"id": identidade, "order": ordem} for identidade, ordem in pares}


def test_primeira_etapa_nao_tem_anterior():
    assert etapa_anterior(vigentes((E1, 0), (E2, 1)), E1) is None
    assert etapas_anteriores(vigentes((E1, 0), (E2, 1)), E1) == []


def test_a_anterior_e_a_de_maior_ordem_menor_e_nao_ordem_menos_um():
    """A Retificação remove Etapa sem reordenar: com ordens 0 e 5, a anterior de 5 é a de 0."""
    anterior = etapa_anterior(vigentes((E1, 0), (E3, 5)), E3)
    assert anterior is not None and anterior[0] == E1


def test_todas_as_anteriores_vem_da_mais_proxima_para_a_mais_distante():
    identidades = [i for i, _ in etapas_anteriores(vigentes((E1, 0), (E2, 1), (E3, 2)), E3)]
    assert identidades == [E2, E1]


def test_identidade_ausente_do_vigente_nao_tem_anterior():
    """Etapa removida por Retificação: não há anterior, e inventar uma seria pior que não ter."""
    ausente = UUID("00000000-0000-0000-0000-0000000000ff")
    assert etapas_anteriores(vigentes((E1, 0), (E2, 1)), ausente) == []


def test_a_identidade_pode_chegar_como_texto():
    """O conteúdo publicado traz `id` como string; a chave do vigente é UUID."""
    anterior = etapa_anterior(vigentes((E1, 0), (E2, 1)), str(E2))
    assert anterior is not None and anterior[0] == E1
