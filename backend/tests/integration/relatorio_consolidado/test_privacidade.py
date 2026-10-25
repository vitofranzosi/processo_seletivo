"""Privacidade: nada pessoal, nada por Perfil ou lista, e o Edital pequeno fora (100, FR-2585 a
FR-2592, SC-941)."""

import re

import pytest

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import relatorio_consolidado_pdf
from tests.fixtures.relatorio import montar_cenario
from tests.integration.relatorio_consolidado.conftest import conjunto, ler, texto_do_documento
from tests.interface.test_fluxo import texto_de_pdf_bytes

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
    assert "conta 1 dos 2 Editais — fora 1 Edital" in " ".join(i.base for i in com.indicadores)


def test_nenhum_dado_pessoal_nem_fato_nao_publico_por_perfil(db):
    cenario = montar_cenario(final="pendente")
    lido = ler(conjunto("criterio=numero&ano=2026"))
    texto = texto_do_documento(lido)
    # Cada comando de texto do PDF é uma linha desenhada: é nela que Perfil e fato se juntariam.
    linhas = texto_de_pdf_bytes(relatorio_consolidado_pdf.compor(lido, emissao=1))
    for inscricao in Inscricao.objects.filter(edital=cenario.edital):
        for valor in (inscricao.nome, inscricao.cpf, inscricao.email, inscricao.protocolo):
            assert not valor or valor not in texto, valor
    assert not re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto)
    # Convocação, recurso e apuração não aparecem com nome de Perfil nem de lista: nenhuma linha
    # do documento junta os dois. (O nome do Perfil aparece no título do Edital, que é público.)
    for linha in linhas.splitlines():
        if any(p in linha for p in ("Técnico de Laboratório:", "Professor de Informática:")):
            assert not any(f in linha for f in ("convoca", "recurso", "apura")), linha
    assert "pretas, pardas" not in texto
