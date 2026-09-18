"""O Edital de sorteio publicado carrega o método, e quem o recebe consegue conferir (032, SC-158).

**É a única entrega desta feature que alcança quem está fora da instituição.** A `021` construiu a
verificação pública do sorteio: o manifesto declara algoritmo e semente, e um terceiro reimplementa
a ordem. O que faltava era a outra ponta — a **norma** contra a qual aquele resultado se confere.
Sem o método no Edital, a candidata que recebe a relação do sorteio tem um número e nenhuma regra
publicada que diga de onde ele deveria ter vindo.

**Pelo caminho de publicação, e não pelo renderizador direto.** Os casos de `tests/unit/publicacoes`
afirmam o que `_marcos` desenha; este afirma o que **o documento publicado contém**, depois de
atravessar a submissão, a homologação e o ato de publicação. A diferença importa porque é o
documento guardado que a candidata baixa — e porque ele é composto uma vez e nunca se regenera.

**O que se prova é `SC-158`, e nada mais forte**: com o documento na mão e sem acesso ao sistema,
uma terceira pessoa consegue dizer **qual ocorrência fixará a semente**, **como ela vira semente** e
**o que vale se ela faltar**. Não é a semente que se reproduz a partir do Edital — no dia da
publicação ela ainda não existe.
"""

import re

import pytest

from processo_seletivo.publicacoes.models import DocumentoPublicado
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import MARCO, METODO, marco_com_metodo
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def publicado_com_sorteio(api_client, manager_headers, process_payload):
    """Um Edital publicado cujo marco ordena por sorteio e declara o método próprio, inteiro."""
    rascunho = rascunho_com_etapas()
    marco_com_metodo(
        rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"], marco_id=MARCO
    )
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def documento(edital):
    """O texto desenhado no documento guardado, com as quebras de refluxo desfeitas.

    Colapsar espaço em branco só pode criar coincidência, nunca escondê-la: as afirmações de
    ausência ficam mais estritas, e não menos. É a mesma leitura que `test_pdf_classificacao.py`
    faz, e pela mesma razão — uma frase normativa longa atravessa duas linhas desenhadas.
    """
    guardado = DocumentoPublicado.objects.get(publicacao__edital=edital)
    return re.sub(r"\s+", " ", texto_de(bytes(guardado.bytes)))


def test_o_documento_publicado_diz_que_a_ordem_daquele_marco_vem_de_sorteio(publicado_com_sorteio):
    """`FR-464`, no artefato que a candidata baixa."""
    assert "Ordem: por sorteio" in documento(publicado_com_sorteio)


def test_quem_recebe_o_documento_sabe_qual_ocorrencia_fixara_a_semente(publicado_com_sorteio):
    """A primeira metade de `SC-158`, e ela é o que falta para conferir o sorteio.

    A ocorrência e o instante em que ela acontece: com os dois, quem recebe o Edital sabe **onde**
    procurar o material bruto e **quando** ele existirá, sem pedir nada à instituição.
    """
    escrito = documento(publicado_com_sorteio)

    assert METODO["occurrence"] in escrito
    assert "Fonte de demonstração" in escrito
    assert "01/01/2020, às 20h" in escrito, "o instante publicado da ocorrência"


def test_quem_recebe_o_documento_sabe_como_a_ocorrencia_vira_semente(publicado_com_sorteio):
    """A segunda metade: a regra de normalização, publicada como frase que a pessoa lê."""
    assert METODO["normalization"]["text"] in documento(publicado_com_sorteio)


def test_quem_recebe_o_documento_sabe_o_que_vale_se_a_ocorrencia_faltar(publicado_com_sorteio):
    """A terceira, e é a que a `021` chama de `FR-015`: nenhuma escolha volta para a mesa.

    Sem a regra de substituição publicada, a hipótese de a extração não acontecer devolveria a
    decisão ao dia do sorteio — que é exatamente o que o método existe para eliminar.
    """
    assert METODO["substitutionRule"]["text"] in documento(publicado_com_sorteio)


def test_o_documento_do_sorteio_nao_afirma_combinacao_de_pontuacoes(publicado_com_sorteio):
    """`FR-468`, no artefato publicado: o documento parava de dizer a verdade exatamente aqui."""
    escrito = documento(publicado_com_sorteio)

    assert "Combinação" not in escrito
    assert "soma ponderada" not in escrito


def test_o_documento_nao_publica_a_semente(publicado_com_sorteio):
    """O limite de `SC-158`, dito como teste.

    **Não é a semente que se reproduz a partir do Edital.** No dia da publicação ela não existe, e
    um documento que a trouxesse estaria publicando o resultado antes do sorteio. Quem publica a
    semente é o documento do **resultado**, e a verificação pública compara os dois.
    """
    escrito = documento(publicado_com_sorteio)

    assert "Semente:" in escrito, "a regra que produz a semente é publicada"
    assert "DIGITOS_EM_SEQUENCIA" not in escrito, "o identificador é da máquina, e não do papel"
