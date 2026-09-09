"""O método do sorteio é declarado na composição do Edital, e não na gestão do sorteio (021, D-013).

**Por que este teste existe, e por que ele olha dois caminhos.** A FR-014 exige que alterar o
método seja Retificação. Isso só é verdade se o método for conteúdo publicado do Edital — e ele só
chega ao conteúdo publicado se sobreviver aos **dois** caminhos do assistente: a coleta do
formulário e o reenvio do rascunho já persistido. A `018` perdeu a janela recursal exatamente aí
(E2E18-005): declarada no passo Classificação, ela sumia ao gravar qualquer passo seguinte, porque
o reenvio não a carregava. Fechar um caminho só deixa o defeito vivo.

A leitura do método pela tela do sorteio — que exibe e **não** edita — é afirmada em
`tests/integration/sorteios/test_metodo_nao_e_escolha.py`, que varre as superfícies do módulo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from tests.interface.test_compor import PERFIL
from tests.interface.test_compor_classificacao import (
    ETAPA_CLASSIFICATORIA,
    MARCO,
    marco_form,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

_METODO_VALIDO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5900",
    "derivation": "a extração de sábado anterior",
    "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os cinco números"},
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "vale a seguinte",
    },
}

METODO_NO_FORMULARIO = {
    f"marco-{PERFIL}-0-draw-algorithm": "IFES-SORTEIO-SHA256-v1",
    f"marco-{PERFIL}-0-draw-source": "Loteria Federal",
    f"marco-{PERFIL}-0-draw-occurrence": "extração imediatamente anterior ao sorteio",
    f"marco-{PERFIL}-0-draw-derivation": "a extração de sábado anterior à data publicada",
    f"marco-{PERFIL}-0-draw-normalizationRule": "DIGITOS_EM_SEQUENCIA",
    f"marco-{PERFIL}-0-draw-normalizationText": "os cinco números, na ordem dos prêmios",
    f"marco-{PERFIL}-0-draw-substitutionRule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
    f"marco-{PERFIL}-0-draw-substitutionText": "não havendo extração, vale a seguinte",
}


def _compor(client, edital, **extra):
    return client.post(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"]),
        marco_form(**extra),
    )


def test_a_tela_oferece_os_seis_campos_do_metodo(client, com_etapas):
    # O fragmento do marco só é desenhado quando existe marco: o passo nasce sem nenhum, e é o
    # `hx-get` que o acrescenta. Gravar um primeiro é o mesmo percurso de quem compõe de verdade.
    _compor(client, com_etapas)

    resposta = client.get(reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]))
    corpo = resposta.content.decode()

    assert "Método do sorteio, se este marco ordena por sorteio" in corpo
    for campo in ("algorithm", "source", "occurrence", "derivation"):
        assert f'name="marco-{PERFIL}-0-draw-{campo}"' in corpo
    assert f'name="marco-{PERFIL}-0-draw-normalizationRule"' in corpo
    assert f'name="marco-{PERFIL}-0-draw-substitutionRule"' in corpo


def test_o_marco_que_nao_sorteia_nao_declara_metodo(client, com_etapas):
    """A ausência é a maioria dos casos, e é resposta legítima — nada de valor padrão."""
    resposta = _compor(client, com_etapas)

    assert resposta.status_code == 302, resposta.content
    assert MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio == {}


def test_o_metodo_declarado_chega_ao_rascunho(client, com_etapas):
    resposta = _compor(client, com_etapas, **METODO_NO_FORMULARIO)

    assert resposta.status_code == 302, resposta.content
    metodo = MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio
    assert metodo["algorithm"] == "IFES-SORTEIO-SHA256-v1"
    assert metodo["source"] == "Loteria Federal"
    assert metodo["normalization"] == {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números, na ordem dos prêmios",
    }
    assert metodo["substitutionRule"]["rule"] == "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE"


def test_o_metodo_volta_para_a_tela_na_reexibicao(client, com_etapas):
    _compor(client, com_etapas, **METODO_NO_FORMULARIO)

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert 'value="Loteria Federal"' in corpo
    assert '<option value="DIGITOS_EM_SEQUENCIA" selected>' in corpo
    assert '<option value="OCORRENCIA_SEGUINTE_DA_MESMA_FONTE" selected>' in corpo


def test_gravar_outro_passo_nao_apaga_o_metodo_declarado(client, com_etapas):
    """**O segundo caminho de perda**, e o que a `018` aprendeu do jeito difícil (E2E18-005).

    Declarar no passo Classificação e gravar o passo seguinte não pode publicar um Edital que nada
    declara sobre sorteio: o reenvio carrega o contrato inteiro do marco, e não só os campos que a
    tela da vez desenha.
    """
    _compor(client, com_etapas, **METODO_NO_FORMULARIO)

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "identificacao"]),
        {"title": "Título alterado depois do método", "description": "Descrição qualquer."},
    )

    assert resposta.status_code in (200, 302), resposta.content
    metodo = MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio
    assert metodo, "o método declarado sumiu ao gravar outro passo do assistente"
    assert metodo["source"] == "Loteria Federal"


def test_metodo_pela_metade_e_recusado_nomeando_o_que_falta(client, com_etapas):
    """Sem regra de substituição, a escolha volta para a mesa no dia do sorteio (FR-015)."""
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        validate_classification_milestones,
    )

    incompleto = {
        "id": MARCO,
        "code": "SORTEIO",
        "name": "Sorteio",
        "stages": [ETAPA_CLASSIFICATORIA],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
        "drawMethod": {
            "algorithm": "IFES-SORTEIO-SHA256-v1",
            "source": "Loteria Federal",
            "occurrence": "extração anterior",
            "derivation": "sábado anterior",
            "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os dígitos"},
        },
    }

    with pytest.raises(ProfileValidationError, match="substitutionRule"):
        validate_classification_milestones([incompleto])


def test_regra_de_normalizacao_fora_do_vocabulario_e_recusada_na_elaboracao():
    """O defeito aparece no dia em que alguém a escreve, e não ao vivo no dia do sorteio."""
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
    )

    with pytest.raises(ProfileValidationError, match="não publicada por este sistema"):
        _validar_metodo_de_sorteio(
            {
                "algorithm": "IFES-SORTEIO-SHA256-v1",
                "source": "Loteria Federal",
                "occurrence": "x",
                "derivation": "y",
                "normalization": {"rule": "O_QUE_A_COMISSAO_ACHAR", "text": "z"},
                "substitutionRule": {"rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE", "text": "w"},
            }
        )


def test_um_algoritmo_que_o_sistema_nao_executa_e_recusado():
    """O manifesto publicaria um nome, e a ordem viria de outro (021, FR-027).

    A validação só conferia que `algorithm` estava preenchido, e a constituição sempre usava
    `IFES-SORTEIO-SHA256-v1`: um Edital podia declarar `SORTEIO-XPTO-v3` e publicar um manifesto
    que ninguém consegue reimplementar. Quem tentasse chegaria a outra ordem — e concluiria,
    corretamente, que o sorteio não confere.
    """
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
    )

    with pytest.raises(ProfileValidationError, match="não publicado por este sistema"):
        _validar_metodo_de_sorteio(
            {
                **{k: v for k, v in _METODO_VALIDO.items()},
                "algorithm": "SORTEIO-XPTO-v3",
            }
        )


def test_uma_regra_de_substituicao_que_o_sistema_nao_executa_e_recusada():
    """Prosa não é aplicável "sem escolha humana no momento da execução" (021, FR-015)."""
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
    )

    with pytest.raises(ProfileValidationError, match="Regra de substituição não publicada"):
        _validar_metodo_de_sorteio(
            {
                **_METODO_VALIDO,
                "substitutionRule": {"rule": "O_QUE_A_COMISSAO_DECIDIR", "text": "…"},
            }
        )


def test_o_algoritmo_declarado_e_o_que_o_dominio_executa():
    """A afirmação positiva: o vocabulário fechado **é** o que `chave.py` implementa."""
    from processo_seletivo.sorteios.domain.chave import ALGORITMO, ALGORITMOS

    assert _METODO_VALIDO["algorithm"] in ALGORITMOS
    assert ALGORITMOS == frozenset({ALGORITMO})
