"""Quantas situações fazem o sistema enviar mensagem — contadas, e não presumidas (`FR-084`).

**A regra tem um mecanismo de revisão escrito dentro dela**, e esta varredura é o que o torna real:
a `FR-084` da `010` enumera as situações e diz que acrescentar outra exige revisá-la. Sem um teste
que conte, a quarta entraria como as anteriores — uma chamada de `send_mail` num módulo novo, sem
que nada acusasse que a norma ficou para trás.

**A `019` acrescentou a terceira**, e o custo dela é este arquivo: a convocação é ato da
Administração dirigido ao candidato, e não recibo de ato que ele praticou — o critério que unia as
duas primeiras. Admiti-la exigiu a revisão, que está datada na spec e declarada em
`convocacao/application/comunicar.py`.
"""

import io
import tokenize
from pathlib import Path

import pytest

from processo_seletivo.convocacao.application.comunicar import REVISAO_DA_FR_084

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
SPEC_DA_010 = Path(__file__).resolve().parents[2] / "specs" / "010-area-do-candidato" / "spec.md"

# As três situações da `FR-084` revisada, e o módulo onde cada uma vive. **Declaradas, e não
# descobertas**: é a lista contra a qual a varredura compara, e acrescentar uma linha aqui é o
# gesto que obriga a revisar a norma antes — não depois.
SITUACOES = {
    "identidade/application/mensagem.py": "o código de acesso e o aviso de mudança de credencial",
    "inscricoes/application/mensagem.py": "a confirmação do envio da inscrição",
    "convocacao/application/comunicar.py": "a convocação, quando o Edital a comunica por mensagem",
}


#: Os nomes que põem mensagem na fila de envio do Django.
REMETENTES = {"send_mail", "EmailMessage", "EmailMultiAlternatives"}


def _nomes_do_codigo(arquivo):
    """Os identificadores que o arquivo usa **como código**, sem comentário nem literal.

    **Varrer o texto bruto acusaria prosa.** Este repositório explica em comentário por que um
    módulo *não* envia mensagem — `identidade/application/mensagem.py` faz exatamente isso —, e uma
    busca por substring leria a explicação como se fosse a coisa explicada. O teste que existe para
    achar a quarta situação passaria a apontar para um parágrafo.
    """
    codigo = arquivo.read_text(encoding="utf-8")
    fluxo = io.StringIO(codigo).readline
    return {item.string for item in tokenize.generate_tokens(fluxo) if item.type == tokenize.NAME}


def modulos_que_enviam():
    """Todo módulo de produção que põe mensagem na fila de envio."""
    achados = set()
    for arquivo in RAIZ.rglob("*.py"):
        if "migrations" in arquivo.parts:
            continue
        if _nomes_do_codigo(arquivo) & REMETENTES:
            achados.add(str(arquivo.relative_to(RAIZ)))
    return achados


def test_nenhum_modulo_envia_fora_das_situacoes_declaradas():
    """O guarda serve para isto: um `send_mail` novo em módulo não declarado é falha de suíte.

    O modo de errar aqui não dá erro nenhum em produção — dá um Edital comunicando por um caminho
    que a norma da `010` não admite, descoberto por quem recebeu a mensagem.
    """
    assert modulos_que_enviam() <= set(SITUACOES), (
        "um módulo novo passou a enviar mensagem: ou ele é uma situação nova — e a FR-084 da 010 "
        "precisa ser revisada de novo antes —, ou o envio não deveria estar ali"
    )


def test_a_varredura_le_o_codigo_e_nao_a_prosa(tmp_path):
    """Comentário que **cita** `send_mail` não é um módulo que envia.

    O modo de errar aqui reprova a suíte por um parágrafo, e o parágrafo costuma ser justamente a
    explicação de por que aquele módulo não envia nada.
    """
    so_prosa = tmp_path / "so_prosa.py"
    so_prosa.write_text(
        '"""Este módulo não usa send_mail, e o comentário abaixo diz por quê."""\n'
        "# Nada aqui chama send_mail: o envio mora em `inscricoes`.\n"
        'AVISO = "não chame send_mail daqui"\n',
        encoding="utf-8",
    )
    envia = tmp_path / "envia.py"
    envia.write_text("from django.core.mail import send_mail\n", encoding="utf-8")

    assert not _nomes_do_codigo(so_prosa) & REMETENTES
    assert _nomes_do_codigo(envia) & REMETENTES


def test_sao_tres_situacoes_e_a_terceira_e_a_convocacao():
    """Três, e não duas: a contagem asseverada é a da regra **revisada** (019, `T027`)."""
    assert len(SITUACOES) == 3
    assert "convocacao/application/comunicar.py" in SITUACOES


@pytest.mark.skipif(not SPEC_DA_010.exists(), reason="a árvore de specs não está neste checkout")
def test_a_declaracao_no_codigo_concorda_com_a_norma_escrita():
    """A guarda de implantação existe para que norma e código não fiquem contraditórios (`FR-289`).

    **É aqui que a contradição é achada, e não em tempo de execução.** `comunicar.py` declara a data
    da revisão numa constante em vez de ler `specs/` ao enviar: ler a árvore de documentação de
    dentro do envio faria a convocação falhar, em produção, por ausência de um arquivo que o
    contêiner não carrega — falha pior do que a que a guarda impede. Quem lê as duas é a suíte.
    """
    texto = SPEC_DA_010.read_text(encoding="utf-8")
    trecho = texto[texto.index("- **FR-084**") : texto.index("- **FR-084a**")]

    if REVISAO_DA_FR_084:
        assert "revisada pela `019`" in trecho, (
            "o código declara a revisão da FR-084 e a spec não a registra: ou a revisão foi "
            "desfeita, ou REVISAO_DA_FR_084 foi declarada antes de existir"
        )
        assert REVISAO_DA_FR_084 in trecho, "a data declarada não é a que a spec registra"
        assert "três" in trecho, "a regra revisada precisa dizer quantas situações admite"
        assert "Redação anterior" in trecho, (
            "a regra mandava revisá-la, e não substituí-la em silêncio: a redação anterior fica"
        )
    else:
        assert "revisada pela `019`" not in trecho
