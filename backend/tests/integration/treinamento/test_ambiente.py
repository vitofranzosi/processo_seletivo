"""As barreiras do gerador: produção, chave e banco por extenso (134, FR-4601 a FR-4605).

Toda recusa é conferida duas vezes: pela frase, e pelo banco — nada pode ter sido gravado.
"""

import pytest
from django.core.management import CommandError

from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.treinamento import carregar, comando, restaurar, verificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

COMANDOS = (
    "carregar_cenarios_de_treinamento",
    "listar_cenarios_de_treinamento",
    "verificar_cenarios_de_treinamento",
    "restaurar_cenario_de_treinamento",
)


def _rodar(nome):
    """Cada comando com o que ele aceita — a recusa tem de vir antes de qualquer outra coisa."""
    if nome.startswith("restaurar"):
        return comando(nome, "C07", confirmar="C07")
    if nome.startswith("carregar"):
        return comando(nome, "C07")
    return comando(nome, "C07", escrever=False)


def _nada_gravado():
    assert not ProcessoSeletivo.objects.exists()
    assert not CenarioDeTreinamento.objects.exists()


@pytest.mark.parametrize("nome", COMANDOS)
def test_todo_comando_recusa_em_producao_mesmo_com_a_chave_ligada(nome, treinamento):
    treinamento.AMBIENTE_DE_PRODUCAO = True
    with pytest.raises(CommandError, match="produção"):
        _rodar(nome)
    _nada_gravado()


@pytest.mark.parametrize("nome", COMANDOS)
def test_todo_comando_recusa_com_as_configuracoes_de_producao_no_ambiente(
    nome, treinamento, monkeypatch
):
    """Não basta a marca: o módulo de configuração também é conferido (não confiar só no DEBUG)."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.production")
    with pytest.raises(CommandError, match="produção"):
        _rodar(nome)
    _nada_gravado()


@pytest.mark.parametrize("nome", COMANDOS)
def test_todo_comando_recusa_sem_a_chave_do_ambiente(nome, settings, raiz_de_arquivos):
    settings.CENARIOS_DE_TREINAMENTO = False
    with pytest.raises(CommandError, match="CENARIOS_DE_TREINAMENTO"):
        _rodar(nome)
    _nada_gravado()


def test_a_carga_exige_o_nome_do_banco_por_extenso(treinamento):
    with pytest.raises(CommandError, match="--banco"):
        carregar("C03", banco="")
    with pytest.raises(CommandError, match="não é o banco conectado"):
        carregar("C03", banco="processo_seletivo_producao")
    _nada_gravado()


def test_a_restauracao_exige_o_nome_do_banco_por_extenso(treinamento):
    with pytest.raises(CommandError, match="--banco"):
        restaurar("C03", banco="", confirmar="C03")
    _nada_gravado()


def test_a_pre_visualizacao_mostra_o_destino_e_o_plano_sem_gravar(treinamento):
    saida = carregar(dry_run=True)
    assert "Pré-visualização" in saida
    assert "Banco " in saida
    for codigo in ("C01", "C07", "C15"):
        assert codigo in saida
    assert saida.count("CRIAR") == 17
    _nada_gravado()


def test_a_pre_visualizacao_recusa_o_sorteio_sem_a_fonte_de_demonstracao(treinamento):
    """Sem a fonte, o sorteio esperaria a Caixa — o cenário é recusado, e dito, antes de começar."""
    treinamento.SORTEIO_FONTE_DE_DEMONSTRACAO = False
    saida = carregar("C06", "C07", "C04", dry_run=True)
    assert saida.count("RECUSAR") == 2
    assert "SORTEIO_FONTE_DE_DEMONSTRACAO" in saida
    _nada_gravado()


def test_cenario_desconhecido_e_recusado_pelo_nome(treinamento):
    with pytest.raises(CommandError, match="C99"):
        carregar("C99", dry_run=True)


def test_listar_e_verificar_so_leem(treinamento):
    assert "AUSENTE" in comando("listar_cenarios_de_treinamento", escrever=False)
    assert "AUSENTE" in verificar()
    _nada_gravado()


def test_a_carga_sem_autoridade_vigente_recusa_sem_criar_configuracao(treinamento):
    """O gerador não cadastra autoridade: é registro institucional, com trilha (FR-4615)."""
    from processo_seletivo.unidades.models import AutoridadeHabilitada
    from tests.fixtures.autoridades import registrar_unidade

    registrar_unidade("sem-autoridade")
    antes = AutoridadeHabilitada.objects.count()
    with pytest.raises(CommandError, match="autoridade vigente"):
        carregar("C03", unidade="sem-autoridade")
    assert AutoridadeHabilitada.objects.count() == antes
    _nada_gravado()
