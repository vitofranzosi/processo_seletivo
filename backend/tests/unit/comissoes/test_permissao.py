"""T004 — a permissão sistêmica existe; a presidência **não** é papel.

Este teste existe para falhar no dia em que alguém acrescentar `comissao:presidir` a `PAPEIS`.
Fazer isso transformaria a presidência em papel global — a pessoa presidiria todas as comissões
de todos os Processos —, que é exatamente o que P-003 e o SC-011 proíbem.
"""

from processo_seletivo.comissoes.domain.autorizacao import BASE_PRESIDENCIA, PERMISSAO_SISTEMICA
from processo_seletivo.interface.identidade import PAPEIS, permissoes_de


def test_gestor_pode_gerir_comissao():
    assert PERMISSAO_SISTEMICA in permissoes_de(["gestor"])


def test_nenhum_outro_papel_pode_gerir_comissao():
    outros = [papel for papel in PAPEIS if papel != "gestor"]
    for papel in outros:
        assert PERMISSAO_SISTEMICA not in permissoes_de([papel]), papel


def test_presidencia_nao_e_papel_do_sistema():
    """É rótulo de trilha, e nada mais: quem preside, preside **um** Processo."""
    todas = {permissao for papel in PAPEIS for permissao in permissoes_de([papel])}
    assert BASE_PRESIDENCIA not in todas
