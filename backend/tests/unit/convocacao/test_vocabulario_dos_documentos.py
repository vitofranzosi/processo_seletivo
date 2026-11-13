"""O nome do documento reenviado, uma fonte só (154, FR-6211, FR-6212, D-004, SC-2004)."""

from processo_seletivo.avisos.application import pendencias
from processo_seletivo.convocacao.domain import vocabulario_dos_documentos as v
from processo_seletivo.interface import views
from processo_seletivo.interface.templatetags.interface_extras import reenviados


def test_o_rotulo_tem_o_travessao_com_espaco_dos_dois_lados():
    assert v.REENVIADO == "Reenviado — aguardando nova conferência"


def test_dentro_de_frase_em_minuscula():
    assert v.reenviado_em_frase() == "reenviado — aguardando nova conferência"
    assert v.reenviado_em_frase(plural=True) == "reenviados — aguardando nova conferência"


def test_a_contagem_tem_singular_e_plural_sem_parenteses():
    assert v.reenviados(1) == "1 reenviado — aguardando nova conferência"
    assert v.reenviados(2) == "2 reenviados — aguardando nova conferência"
    assert "(s)" not in v.reenviados(1) + v.reenviados(2)


def test_o_rotulo_da_contagem_e_o_rotulo_do_item_no_singular():
    assert v.rotulo_da_contagem(1) == v.REENVIADO
    assert v.rotulo_da_contagem(2) == "Reenviados — aguardando nova conferência"


def test_o_resumo_de_cartoes_diz_o_rotulo_com_o_numero_a_parte():
    assert reenviados(1, "rotulo") == v.REENVIADO
    assert reenviados(2, "rotulo") == "Reenviados — aguardando nova conferência"
    assert reenviados(2) == v.reenviados(2)


def test_as_superficies_dizem_o_mesmo_nome_salvo_a_caixa_da_inicial():
    """SC-2004: o item, a exclusão do aviso e as contagens leem do vocabulário."""
    nome = v.reenviado_em_frase()

    assert views.ROTULO_DO_ITEM["COMPLEMENTADO"] == v.REENVIADO
    assert pendencias.COMPLEMENTADA == f"documento {nome}"
    assert v.REENVIADO.lower() == nome
    assert nome in v.reenviados(1)


def test_o_resumo_renderizado_diz_o_singular_e_o_plural():
    """T023: a contagem com um e com dois, no parcial da página de documentos (FR-6212, D-004)."""
    from django.template.loader import render_to_string

    def resumo(quantos):
        contagens = {
            "conformes": 0,
            "recebidos": 0,
            "complementados": quantos,
            "pendentes": 0,
            "a_apresentar": 0,
            "nao_se_aplica": 0,
        }
        linha = {"passo": {"tom": "acao", "frase": "", "acao": ""}, "aviso": None}
        return render_to_string(
            "interface/_situacao_dos_documentos.html",
            {"linha": linha, "leitura": {"contagens": contagens}},
        )

    assert "<strong>1</strong>Reenviado — aguardando nova conferência</li>" in resumo(1)
    assert "<strong>2</strong>Reenviados — aguardando nova conferência</li>" in resumo(2)
    assert "complementad" not in (resumo(1) + resumo(2)).lower()
