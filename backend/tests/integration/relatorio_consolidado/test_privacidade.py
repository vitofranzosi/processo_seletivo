"""Privacidade: nada pessoal, nada por Perfil ou lista, e o Edital pequeno fora (100, FR-2585 a
FR-2592, SC-941)."""

import re

import pytest

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.relatorio import montar_cenario
from tests.integration.relatorio_consolidado.conftest import conjunto, ler, texto_do_documento

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_o_edital_pequeno_nao_muda_numero_nao_publico_entre_emissoes(db):
    """Com e sem o Edital de 4 inscrições, os números não públicos são os mesmos — e a diferença
    entre as duas emissões não devolve o que o relatório dele esconde."""
    grande = montar_cenario(final="pendente")
    pequeno = montar_cenario(final="aberto", numero="65", maximo=4)
    sem = ler(conjunto(f"criterio=manual&edital={grande.edital.pk}"))
    com = ler(conjunto(f"criterio=manual&edital={grande.edital.pk}&edital={pequeno.edital.pk}"))
    for campo in ("vagas_habilitadas", "vagas_apuradas", "convocacoes", "recursos"):
        assert getattr(com, campo) == getattr(sem, campo), campo
    assert com.fora_dos_nao_publicos == 1
    assert com.inscricoes.valor == sem.inscricoes.valor + 4
    assert "fora 1 Edital com menos de 5 inscrições enviadas" in " ".join(
        i.base for i in com.indicadores
    )


def test_nenhum_dado_pessoal_nem_fato_nao_publico_por_perfil(db):
    cenario = montar_cenario(final="pendente")
    texto = texto_do_documento(ler(conjunto("criterio=numero&ano=2026")))
    for inscricao in Inscricao.objects.filter(edital=cenario.edital):
        for valor in (inscricao.nome, inscricao.cpf, inscricao.email, inscricao.protocolo):
            assert not valor or valor not in texto, valor
    assert not re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto)
    # Convocação e recurso não aparecem com nome de Perfil nem de lista.
    for perfil in ("Professor de Informática", "Técnico de Laboratório", "pretas, pardas"):
        assert perfil not in texto, perfil
