"""O que se retifica no Requerimento de Matrícula, e o que não (029, `US3`, T051).

**A `026` governa esta feature, e não é alterada por ela.** O contrato de mutabilidade exige que
todo campo publicado tenha natureza classificada, e que a `NAO_RETIFICAVEL` traga **razão escrita**.
Este arquivo confere que os dois caminhos novos respeitam essa exigência — e que a razão do que não
se retifica vem do contrato, e não de um comentário solto em código.

**Por que o momento não se retifica.** Mudá-lo depois de publicado moveria a coleta de um ponto do
certame para outro com pessoas já inscritas sob a regra anterior: quem enviou o requerimento na
inscrição descobriria que ele valia para a convocação, ou o contrário. O caminho de correção existe
e é outro — publicar Edital novo, ou não coletar.

**Por que o texto se retifica.** Erro de redação numa declaração é o caso comum, e publicação é ato
imutável: sem retificação, um texto com erro nasceria incorrigível. O que protege quem já aceitou é
o resumo guardado no envio — a Retificação muda o texto vigente e **não** reescreve o que cada
pessoa leu (`FR-393`, `SC-129`).
"""

import pytest

from processo_seletivo.editais.domain.mutabilidade import (
    CONTRATO,
    RAIZ,
    Natureza,
    natureza_de,
)

MOMENTO = "matriculationRequest/moment"
TEXTO = "matriculationRequest/declarationText"


def test_os_dois_caminhos_estao_classificados():
    """Campo publicado sem natureza derruba o guardião — e é assim que ele deve falhar."""
    assert (RAIZ, MOMENTO) in CONTRATO
    assert (RAIZ, TEXTO) in CONTRATO


def test_o_momento_nao_e_retificavel_e_a_razao_esta_escrita():
    classificacao = natureza_de(RAIZ, MOMENTO)

    assert classificacao.natureza is Natureza.NAO_RETIFICAVEL
    assert classificacao.razao.strip(), "a razão é obrigatória, e o contrato a exige por construção"


def test_a_razao_do_momento_explica_o_efeito_sobre_quem_ja_se_inscreveu():
    """Razão que apenas repete *"não pode"* não é razão: ela tem de dizer **o que aconteceria**."""
    razao = natureza_de(RAIZ, MOMENTO).razao.lower()

    assert "inscri" in razao or "convoca" in razao


def test_o_texto_da_declaracao_e_retificavel():
    classificacao = natureza_de(RAIZ, TEXTO)

    assert classificacao.natureza is Natureza.RETIFICAVEL
    assert classificacao.razao == "", "razão é proibida para o que se retifica"


def test_o_texto_retificavel_tem_tela_e_o_momento_tem_rotulo():
    """`FR-304`: retificável sem canal do ator é promessa, e não caminho.

    O guardião global já cobra as duas coisas — `test_todo_campo_retificavel_tem_tela` e
    `test_todo_campo_excluido_tem_rotulo_em_portugues`. A asserção aqui é a da feature: ela falha
    junto com a spec, e não três arquivos adiante.
    """
    from processo_seletivo.interface.retificacao import CAMPOS_RAIZ, ROTULO_DO_EXCLUIDO

    assert TEXTO in [caminho for caminho, _, _ in CAMPOS_RAIZ]
    assert (RAIZ, MOMENTO) in ROTULO_DO_EXCLUIDO
    assert ROTULO_DO_EXCLUIDO[(RAIZ, MOMENTO)] != MOMENTO, "em português, e não a chave"


@pytest.mark.parametrize("caminho", [MOMENTO, TEXTO])
def test_a_classificacao_vale_para_a_raiz_e_nao_para_uma_colecao(caminho):
    """São campos de **raiz**, como `title` — e não itens de coleção.

    A distinção não é decorativa: `natureza_de` resolve por `(coleção, caminho)`, e classificá-los
    sob uma coleção os deixaria sem natureza na raiz — que é onde `publish_edital` os emite.
    """
    assert natureza_de(RAIZ, caminho) is CONTRATO[(RAIZ, caminho)]
