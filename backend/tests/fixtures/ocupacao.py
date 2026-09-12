"""O cenário da ocupação e os atalhos que os arquivos de teste da `016` usam.

**Funções ficam aqui, e a fixture fica no `conftest.py` de cada pasta.** Importar uma fixture de
outro módulo de teste a redefine no importador, que é o que o `F811` acusa; importar uma função
comum não tem esse problema. É a mesma regra que `tests/fixtures/corte.py` registra.

O cenário é o do corte da `014`, mais o **quadro de vagas** que esta feature exige: sem linha
publicada não há quantidade a apurar, e a emissão recusa dizendo isso (`FR-242`).
"""

from tests.fixtures.corte import emitir as emitir_corte_do_cenario
from tests.fixtures.corte import montar_cenario_do_corte, rascunho

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
            # A forma que o rascunho aceita é a de `tests/fixtures/divulgacao.py`: `vacancies`, e
            # não `normativeRule`. Inventar o campo devolve `invalid_payload` na submissão.
            {
                "id": MODALIDADE_PPI,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "vacancies": 0,
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


def montar_cenario_da_ocupacao(
    gestor, api_client, manager_headers, process_payload, *, prefixo="ocupacao-016", **quadro
):
    """Edital publicado com quadro, ordem emitida e corte emitido.

    Devolve `(edital, etapa_pontuada, inscricoes)` — a mesma forma que a `014` usa, para que quem
    leia os dois arquivos reconheça o cenário.
    """

    def monta(cut=None):
        return rascunho_com_quadro(cut=cut, **quadro)

    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        draft_factory=monta,
    )
    emitir_corte_do_cenario(edital, gestor, chave=f"{prefixo}-corte")
    return edital, pontuada, inscricoes
