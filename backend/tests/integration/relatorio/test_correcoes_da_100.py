"""As três correções que a `100` fez no relatório do Edital, sobre o cenário coerente.

**Supressão complementar** (FR-2587, FR-2588): o Perfil pequeno leva o menor dos outros, para que o
total menos as linhas não o devolva; e o Edital inteiro abaixo do limiar cala os totais não
públicos. **Perfil sem inscrição** (FR-2589): o marco dele não é pendência que nenhum ato cumpriria.
**Trilha** (FR-2581): os registros posteriores são ditos como registros da trilha.
"""

import pytest

from processo_seletivo.interface import relatorio_do_edital as rel
from tests.fixtures.relatorio import montar_cenario
from tests.integration.relatorio.conftest import executiva_e_anexo, ler, texto_do_documento

pytestmark = pytest.mark.django_db


def _indicador(relatorio, rotulo):
    return next(i for i in relatorio.indicadores if i.rotulo == rotulo)


def test_perfil_pequeno_leva_o_outro_e_o_total_continua(db):
    cenario = montar_cenario(final="pendente", tecnicos=3)
    relatorio = ler(cenario)
    professor, tecnico = relatorio.perfis
    assert tecnico.motivo_da_omissao == rel.FRASE_DE_PRIVACIDADE
    assert professor.motivo_da_omissao == rel.FRASE_COMPLEMENTAR
    for perfil in (professor, tecnico):
        assert perfil.convocacoes is None and perfil.recursos is None and perfil.etapas == ()
    # O total do Edital continua dito: 26 + 3 inscrições, acima do limiar.
    assert not relatorio.total_omitido
    aceitas = _indicador(relatorio, "convocações aceitas")
    assert aceitas.numero.existe
    texto = texto_do_documento(relatorio)
    assert "não se deduza dos totais" in texto
    # Nenhuma linha de Perfil traz número de convocação: não há o que subtrair do total.
    assert "Professor de Informática: 1 convocação" not in texto


def test_edital_abaixo_do_limiar_cala_os_totais_nao_publicos(db):
    cenario = montar_cenario(final="cancelado", maximo=4)
    relatorio = ler(cenario)
    assert relatorio.total_omitido
    for rotulo in ("vagas com inscrição classificada e habilitada", "convocações aceitas"):
        indicador = _indicador(relatorio, rotulo)
        assert not indicador.numero.existe
        assert rel.interpretar(indicador.numero) == rel.FRASE_DO_EDITAL
    assert "Detalhe omitido: menos de 5 inscrições neste Edital." in texto_do_documento(relatorio)
    assert not any(d.texto == "Recursos julgados" for d in relatorio.datas)


def test_perfil_sem_inscricao_nao_deve_resultado(db):
    cenario = montar_cenario(final="sem-pendencia", tecnicos=0)
    relatorio = ler(cenario)
    professor, tecnico = relatorio.perfis
    assert tecnico.inscricoes.valor == 0
    assert rel.interpretar(tecnico.classificadas) == "não se aplica: nenhuma inscrição enviada"
    assert not any("Técnico de Laboratório" in p for p in relatorio.pendencias)
    definitivos = _indicador(relatorio, "resultados definitivos publicados")
    assert definitivos.de == 1, "o marco do Técnico não é resultado previsto"
    assert relatorio.especie == rel.ENCERRAMENTO


def test_a_trilha_e_dita_pelo_que_registra(pendente):
    relatorio = ler(pendente)
    titulos = [titulo for titulo, _ in relatorio.pontos_de_atencao]
    assert "A trilha de auditoria tem 2 registros depois do encerramento." in titulos
    _, anexo = executiva_e_anexo(texto_do_documento(relatorio))
    assert "A contagem cobre os atos que a trilha registra, e não todo acontecimento." in anexo
