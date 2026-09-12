"""O cenário da ocupação: o do corte, mais o quadro de vagas que esta feature exige.

A `014` monta Edital, comissão, avaliações, Resultado consolidado e ordem emitida. O que falta para
apurar ocupação é o **quadro** — sem linha publicada não há quantidade a apurar, e a emissão recusa
dizendo isso (`FR-242`). Aqui o quadro entra no rascunho antes da publicação.
"""

import pytest

from tests.fixtures.corte import MARCO, montar_cenario_do_corte, rascunho
from tests.fixtures.corte import emitir as emitir_corte_do_cenario
from tests.fixtures.edital import PROFILE_ID

LINHA_GERAL = "00000000-0000-4000-8000-000000000471"
LINHA_PPI = "00000000-0000-4000-8000-000000000472"
MODALIDADE_PPI = "00000000-0000-4000-8000-000000000473"


def rascunho_com_quadro(*, geral=3, ppi=None, reversao=None, cut=None):
    """O rascunho do corte com quadro de vagas publicado.

    `geral` é a linha da ampla concorrência — a de `modalityId` nulo, que é onde a quantidade da
    ampla mora. `ppi` acrescenta a cota, e `reversao` declara a espécie do gatilho.

    **O padrão é 3 vagas na linha geral de propósito**: o cenário da `014` tem quatro inscritos e
    alvo 2, e um quadro com 3 deixa o caso interessante — a faixa alcança 2, a ocupação conta
    quantos deles habilitaram, e sobra vaga a ocupar.
    """
    base, pontuada = rascunho(cut=cut)
    perfil = base["profiles"][0]
    linhas = [{"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": geral}]
    if ppi is not None:
        perfil.setdefault("competitionModalities", []).append(
            {
                "id": MODALIDADE_PPI,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "normativeRule": None,
            }
        )
        linhas.append({"id": LINHA_PPI, "modalityId": MODALIDADE_PPI, "immediateVacancies": ppi})
    perfil["vacancyTable"] = linhas
    # **O total do Perfil acompanha o quadro, senão o Edital não publica.** A conferência da `025`
    # exige igualdade quando o quadro é completo — linha geral presente e nenhuma Modalidade
    # declarada sem linha —, e a fixture da `014` declara `immediateVacancies: 1`. Descobri isso
    # pela recusa `blocking_findings` na submissão, que é exatamente onde ela deve aparecer.
    perfil["immediateVacancies"] = geral + (ppi or 0)
    if reversao is not None:
        perfil["vacancyReversion"] = {"kind": reversao}
    return base, pontuada


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Edital publicado com quadro, ordem emitida e corte emitido.

    Devolve `(edital, etapa_pontuada, inscricoes)` — a mesma forma que a `014` usa, para que quem
    leia os dois arquivos reconheça o cenário.
    """
    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-016",
        draft_factory=rascunho_com_quadro,
    )
    emitir_corte_do_cenario(edital, gestor, chave="ocupacao-016-corte")
    return edital, pontuada, inscricoes


@pytest.fixture
def recorte():
    """O recorte da ampla concorrência do cenário: Perfil, marco e lista nula."""
    return {"perfil_id": PROFILE_ID, "marco_id": MARCO, "lista_id": None}
