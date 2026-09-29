"""A Revisão diz de onde veio cada valor, e o que não se corrige depois (051, US4).

É a forma que a Constituição 1.2.0 deixou para as specs: o materializado aparece com o gesto que o
gravou, enquanto for o valor gravado; o padrão e a derivação, pela comparação; e os campos
definitivos, derivados do contrato de mutabilidade, antes do botão de submeter.
"""

import html
import re

import pytest

from processo_seletivo.editais.domain import mutabilidade
from processo_seletivo.interface import revisao
from processo_seletivo.interface.origens import _itens, _no_caminho
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.test_aplicar_a_todos import (
    P1,
    P2,
    _classificacao,
    _impressao,
    _url,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _texto(resposta):
    """O texto da página, sem marcação: a Revisão põe rótulo e valor em elementos vizinhos."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", resposta.content.decode())).split())


def _aplicar_o_marco_do_lp01_ao_lp02(client, edital):
    previa = client.post(_url(edital), _classificacao(aplicar=f"marco:{P1}:0"))
    resposta = client.post(
        _url(edital),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_destino=[P2],
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )
    assert resposta.status_code == 302, resposta.content


def test_o_marco_aplicado_aparece_com_a_origem_e_o_autor(client, tres_perfis):
    _aplicar_o_marco_do_lp01_ao_lp02(client, tres_perfis)

    corpo = _texto(client.get(_url(tres_perfis, "revisao")))

    assert "Origem: LP02 — aplicado a partir do Perfil LP01, por ana.elaboradora, em" in corpo
    # O corte da fixture é o padrão, e a Revisão o diz.
    assert "(padrão do sistema)" in corpo


def test_o_marco_editado_depois_deixa_de_ser_atribuido_ao_gesto(client, tres_perfis):
    _aplicar_o_marco_do_lp01_ao_lp02(client, tres_perfis)
    from processo_seletivo.editais.models.perfis import MarcoClassificatorio

    marco = MarcoClassificatorio.objects.get(perfil_id=P2)
    dados = _classificacao()
    base = f"marco-{P2}-0"
    dados.update(
        {
            f"{base}-id": str(marco.id),
            f"{base}-code": marco.code,
            f"{base}-name": marco.name,
            f"{base}-orderProduction": "POR_PONTUACAO",
            f"{base}-stages": marco.etapas,
            f"{base}-operation": marco.operacao,
            f"{base}-normalization": marco.normalizacao,
            f"{base}-scale": "2",
            f"{base}-mode": "MEIO_PARA_CIMA",
            # A edição à mão: o prazo do recurso muda só no LP02.
            f"{base}-appealDeclaration": "admite",
            f"{base}-appealDurationDays": "9",
            f"{base}-cutTargetKind": "FROM_VACANCY_TABLE",
            f"{base}-cutSurplusCount": "0",
            f"{base}-cutTieOutcome": "STRICT",
            f"{base}-cutGovernedStage": "NONE",
            f"{base}-cutContinuation": "ALLOWED",
        }
    )
    for criterio in marco.criterios.all():
        prefixo = f"criterio-{P2}-0-0"
        dados.update(
            {
                f"{prefixo}-id": str(criterio.id),
                f"{prefixo}-order": str(criterio.ordem),
                f"{prefixo}-type": criterio.tipo,
                f"{prefixo}-target": criterio.parametros.get("factId"),
                f"{prefixo}-whenMissing": criterio.quando_ausente,
            }
        )
    assert client.post(_url(tres_perfis), dados).status_code == 302

    corpo = _texto(client.get(_url(tres_perfis, "revisao")))

    assert "Origem: LP02" not in corpo


def test_os_campos_definitivos_aparecem_antes_de_submeter(client, tres_perfis):
    corpo = _texto(client.get(_url(tres_perfis, "revisao")))

    assert "O que não se corrige depois de publicado" in corpo
    assert "Código do Perfil LP01, LP02, LP03" in corpo
    assert "Espécie do Cadastro Reserva não há — LP01, LP02, LP03" in corpo
    assert corpo.index("O que não se corrige depois de publicado") < corpo.index(
        "Submeter para revisão"
    )


def test_o_bloco_dos_definitivos_cobre_o_contrato():
    """SC-346: todo campo não retificável que o Edital declara aparece — derivado do contrato."""
    conteudo = rascunho_completo()
    conteudo["profiles"][0]["competitionModalities"][0]["normativeRule"]["rounding"] = {
        "mode": "PARA_CIMA"
    }
    declarados = {item["chave"] for item in revisao.definitivos(conteudo)}

    esperados = set()
    for (colecao, caminho), decisao in mutabilidade.CONTRATO.items():
        if decisao.natureza is not mutabilidade.Natureza.NAO_RETIFICAVEL:
            continue
        if (colecao, caminho) in mutabilidade.OPACOS and caminho != "normativeRule/rounding":
            continue
        itens = [item for _, item in _itens(conteudo, colecao)]
        if any(_no_caminho(item, caminho) not in (None, "", [], {}) for item in itens):
            esperados.add((colecao, caminho))

    assert esperados, "a fixture não declara campo não retificável nenhum"
    assert esperados <= declarados, sorted(esperados - declarados)


def test_nenhum_cartao_da_composicao_ganhou_o_aviso(client, tres_perfis):
    """FR-937: o aviso mora na Revisão; os cartões continuam sem ajuda visível (030, FR-428)."""
    for etapa in ("perfis", "classificacao", "etapas"):
        corpo = client.get(_url(tres_perfis, etapa)).content.decode()
        assert "não se corrige depois de publicado" not in corpo


def test_a_forma_de_convocacao_aplicada_pelo_edital_aparece_com_a_origem(client, tres_perfis):
    """O defeito que o percurso no navegador achou: a Revisão quebrava ao ler o gesto do Edital."""
    from tests.interface.test_aplicar_a_todos import _perfis_no_formulario

    formulario = {**_perfis_no_formulario(), "edital-callForm": "INDIVIDUAL_MESSAGE"}
    previa = client.post(_url(tres_perfis, "perfis"), {**formulario, "aplicar": "edital:callForm"})
    assert "Aplicar a forma de convocação a todos os Perfis" in _texto(previa)
    client.post(
        _url(tres_perfis, "perfis"),
        {
            **formulario,
            "confirmar_aplicacao": "edital:callForm",
            "aplicar_destino": ["0", "1", "2"],
            "aplicar_impressao": _impressao(previa.content.decode()),
        },
    )

    corpo = _texto(client.get(_url(tres_perfis, "revisao")))

    assert (
        "Como a convocação é comunicada: por mensagem individual à pessoa convocada "
        "(aplicado pelo Edital, por ana.elaboradora, em"
    ) in corpo
