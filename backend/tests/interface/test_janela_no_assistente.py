"""Os **três** estados da janela recursal, como o elaborador os escreve (FR-020, FR-030, FR-113).

A caminhada da T125 encontrou o buraco. O domínio distingue três coisas desde o começo —

```text
declarada     o marco admite recurso, e por tantos dias
negada        o marco NÃO admite recurso por esta via — norma publicada
não declarada o Edital nada disse; a tempestividade volta ao juízo humano motivado
```

— e a aplicação as trata como três; mas o assistente oferecia uma **caixa de marcação**, e caixa de
marcação tem dois estados. A negativa da FR-113 só nascia por acidente de codificação: desmarcar a
caixa **e** digitar um prazo, que é justamente o que ninguém digita para um marco que não admite
recurso. Na prática, o terceiro estado era inalcançável pela tela que existe para declará-lo.

Confundir a negativa com o silêncio troca *"não cabe recurso"* por *"cabe para sempre"* — o oposto
exato do que a norma disse.
"""

import pytest
from django.urls import reverse

from tests.interface.test_compor import PERFIL
from tests.interface.test_compor_classificacao import marco_form

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CAMPO = f"marco-{PERFIL}-0-appealDeclaration"


def _salvar(client, edital, **alteracoes):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"]),
        marco_form(**alteracoes),
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital.perfis.first().marcos.first()


def test_a_tela_oferece_os_tres_estados(client, com_etapas):
    """Não dá para declarar o que a tela não pergunta."""
    client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert 'value="admite"' in corpo
    assert 'value="nao_admite"' in corpo
    assert 'value="nao_declarada"' in corpo


def test_a_negativa_e_declarada_e_nao_confundida_com_silencio(client, com_etapas):
    """FR-113: `admits` falso é norma publicada, e precisa chegar ao conteúdo como falso."""
    marco = _salvar(client, com_etapas, **{CAMPO: "nao_admite"})

    assert marco.janela_recursal is not None, "a negativa é declaração, não ausência"
    assert marco.janela_recursal["admits"] is False


def test_o_silencio_continua_sendo_silencio(client, com_etapas):
    """FR-028: não declarar é escolha legítima, e é o padrão do formulário.

    O rascunho guarda `{}` — o campo tem `default=dict` —, e o que importa é que a leitura do
    domínio responda "não declarada": `admits` ausente é silêncio, não negativa.
    """
    from processo_seletivo.recursos.domain.janela import admite_recurso

    marco = _salvar(client, com_etapas, **{CAMPO: "nao_declarada"})

    assert not marco.janela_recursal
    assert admite_recurso(marco.janela_recursal or None) is None


def test_a_declaracao_positiva_carrega_o_prazo(client, com_etapas):
    marco = _salvar(
        client,
        com_etapas,
        **{CAMPO: "admite", f"marco-{PERFIL}-0-appealDurationDays": "5"},
    )

    assert marco.janela_recursal == {
        "admits": True,
        "durationDays": 5,
        "unit": "DIAS_CORRIDOS",
    }


def test_o_silencio_volta_como_silencio_ao_reabrir(client, com_etapas):
    """Reexibir `{}` como negativa gravaria, no salvamento seguinte, norma que ninguém escreveu."""
    _salvar(client, com_etapas, **{CAMPO: "nao_declarada"})

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert "checked" in corpo.split('value="nao_declarada"')[1].split(">")[0]
    assert "checked" not in corpo.split('value="nao_admite"')[1].split(">")[0]


def test_a_negativa_volta_selecionada_ao_reabrir(client, com_etapas):
    """Reexibir errado apagaria a norma no próximo salvamento."""
    _salvar(client, com_etapas, **{CAMPO: "nao_admite"})

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    marcado = corpo.split('value="nao_admite"')[1].split(">")[0]
    assert "checked" in marcado
