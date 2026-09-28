"""Os Editais que o sistema executa continuam publicáveis (046, `SC-276`, Cenário B).

**A contraprova do gate inteiro.** Um gate que recusasse demais passaria em todos os casos de recusa
desta feature — e seria descoberto no primeiro Edital real. Cada rascunho abaixo é o que a suíte
publica para modelar um Edital da amostra, e nenhum deles pode receber achado das três regras novas.

**Pelo conteúdo, e não pelo nome da fixture.** As fixtures mudaram na `046` — marcos ganharam a
regra que não governa Etapa, e a *Análise documental* ganhou nota mínima zero —, e o que se prende
aqui é o resultado: o rascunho que a suíte usa para aquela família publica sem achado desta família.
"""

import pytest

from processo_seletivo.editais.domain.validation import ATO_DE_PUBLICACAO, validate_for_publication
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.corte import rascunho as rascunho_do_corte
from tests.fixtures.divulgacao import rascunho_com_marco
from tests.fixtures.edital import complete_draft
from tests.fixtures.ocupacao import rascunho_com_quadro
from tests.fixtures.ocupacao_sorteada import rascunho_sorteado_com_quadro
from tests.fixtures.selecao import rascunho_de_selecao

DA_046 = {"stage_result_unreachable", "stage_without_result", "profile_without_cut_rule"}

#: O rascunho, e o Edital da amostra que ele modela.
EXECUTAVEIS = {
    "69/2026 — sorteia e corta sem governar Etapa": lambda: complete_draft(),
    "14/2026 — pontua, corta e governa a Etapa seguinte": lambda: rascunho_do_corte()[0],
    "14/2026 com quadro de vagas": lambda: rascunho_com_quadro()[0],
    "28/2026 e 57/2026 — sorteio com cotas e corte": lambda: rascunho_sorteado_com_quadro(
        com_corte=True
    ),
    "classificação por pontuação, com marco intermediário": lambda: rascunho_com_marco(
        com_intermediario=True
    ),
    "seleção de dois Perfis, com reserva": lambda: rascunho_de_selecao(),
    "as duas Etapas da comissão": lambda: rascunho_com_etapas(),
}


@pytest.mark.parametrize("modela", list(EXECUTAVEIS))
def test_o_executavel_publica_sem_achado_da_046(modela):
    achados = [
        (item.code, item.path)
        for item in validate_for_publication(EXECUTAVEIS[modela](), ato=ATO_DE_PUBLICACAO)
        if item.code in DA_046
    ]

    assert achados == [], f"{modela}: o gate recusaria o que o sistema executa"
