"""A conferência da declaração de reversão (016, `FR-249`, `FR-250`, `FR-251`).

**Três recusas, e a ausência do objeto não é nenhuma delas.** `null` é declaração legítima — "este
Edital não declara reversão" —, e o 57/2026 prova por que ela precisa ser respeitada: o item 4.5
dele proíbe por escrito o remanejamento de vagas remanescentes entre os cursos.

**A que mais importa é a segunda: objeto sem `kind` não vira espécie padrão.** Os dois Editais da
amostra escrevem o gatilho de modo diferente, e escolher por eles fixaria em ato publicado uma
decisão de **norma**. Vaga revertida sob a leitura larga num Edital que manda a estreita é vaga que
saiu do recorte reservado sem fundamento — e publicação é ato imutável.
"""

import pytest

from processo_seletivo.editais.domain.validation import _reversao_declarada
from processo_seletivo.ocupacao.domain import nomes

BASE = "/profiles/id=99999999-9999-9999-9999-999999999999"
LINHA = {"id": "aaaaaaaa-0000-0000-0000-000000000001", "modalityId": None, "immediateVacancies": 3}


def perfil(reversao=..., *, com_quadro=True):
    dados = {"vacancyTable": [LINHA] if com_quadro else []}
    if reversao is not ...:
        dados["vacancyReversion"] = reversao
    return dados


def conferir(perfil_dado):
    return [(f.code, f.path) for f in _reversao_declarada(perfil_dado, base=BASE)]


class TestAusenciaEDeclaracaoLegitima:
    """Nem a chave ausente nem o objeto nulo são recusa (`D-002`)."""

    def test_perfil_sem_a_chave_passa(self):
        assert conferir(perfil()) == []

    def test_objeto_nulo_passa(self):
        assert conferir(perfil(None)) == []


class TestAsTresRecusas:
    def test_objeto_sem_kind_e_recusado(self):
        """**`FR-251`**: a ausência do gatilho impede a publicação, e não vira padrão."""
        achados = conferir(perfil({}))

        assert achados == [("vacancy_reversion_kind_required", f"{BASE}/vacancyReversion/kind")]

    def test_kind_vazio_tambem_e_recusado(self):
        """Vazio é ausência escrita, e recusar só `None` deixaria passar a metade mais provável."""
        assert conferir(perfil({"kind": ""}))[0][0] == "vacancy_reversion_kind_required"

    def test_kind_fora_do_enum_e_recusado(self):
        achados = conferir(perfil({"kind": "QUANDO_DER"}))

        assert achados == [("vacancy_reversion_kind_unknown", f"{BASE}/vacancyReversion/kind")]

    def test_reversao_sem_quadro_e_recusada(self):
        """Reverter pressupõe quantidade por recorte: sem quadro a regra é inexequível.

        É a mesma lógica que a `014` aplica ao alvo derivado — regra publicada inexequível é regra
        que não devia ter publicado, e descobri-la no dia da emissão custa Retificação.
        """
        achados = conferir(perfil({"kind": nomes.REVERSAO_POR_SALDO}, com_quadro=False))

        assert achados == [("vacancy_reversion_sem_quadro", f"{BASE}/vacancyReversion")]

    def test_objeto_que_nao_e_dicionario_e_recusado(self):
        assert conferir(perfil("ON_BALANCE"))[0][1] == f"{BASE}/vacancyReversion"


class TestAsDuasEspeciesPublicam:
    @pytest.mark.parametrize("especie", [nomes.REVERSAO_POR_ESGOTAMENTO, nomes.REVERSAO_POR_SALDO])
    def test_declaracao_completa_com_quadro_passa(self, especie):
        assert conferir(perfil({"kind": especie})) == []
