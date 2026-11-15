"""O nome publicado da Modalidade, para a página do vídeo dizer "você se inscreveu em …".

174, FR-7853.

Pura, sobre o conteúdo já lido: nenhuma consulta a mais (data-model da 174).
"""

from processo_seletivo.editais.domain.alcance import nome_da_modalidade
from processo_seletivo.verificacao.application.disponibilidade import PODE_GRAVAR, Situacao

CONTEUDO = {
    "profiles": [
        {
            "id": "p1",
            "competitionModalities": [
                {"id": "m1", "code": "PPI", "name": "Pretos, pardos e indígenas"},
                {"id": "m2", "code": "AC"},
            ],
        }
    ]
}


def test_o_nome_publicado_vem_antes_do_codigo():
    assert nome_da_modalidade(CONTEUDO, "p1", "m1") == "Pretos, pardos e indígenas"
    assert nome_da_modalidade(CONTEUDO, "p1", "m2") == "AC"


def test_sem_a_modalidade_no_conteudo_o_nome_fica_vazio():
    assert nome_da_modalidade(CONTEUDO, "p1", "m9") == ""
    assert nome_da_modalidade(CONTEUDO, "p9", "m1") == ""
    assert nome_da_modalidade(None, "p1", "m1") == ""


def test_a_situacao_nasce_sem_modalidade():
    assert Situacao(PODE_GRAVAR, etapa={}).modalidade == ""
