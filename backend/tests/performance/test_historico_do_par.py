"""O histórico do par no painel da Etapa custa o mesmo com um par corrigido e com muitos.

A revisão do PR encontrou o laço: `_historicos_superados` chamava `historico_do_par` uma vez por
linha corrigida, e o painel da Etapa lista até vinte e cinco por página. Com metade das linhas
corrigidas por recurso, a tela pagava mais de uma dezena de leituras extras — e o custo crescia com
o **sucesso** dos recursos, que é justamente o que a instituição espera que aconteça.

Contagem de consultas, e não tempo de parede: o que se protege é a propriedade — o custo não cresce
com a população.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.resultados.application.selectors import historicos_dos_pares
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]


@pytest.fixture
def etapa_com_pares(gestor, api_client, manager_headers, process_payload):
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=190, codigo="0890"
    )
    cenario["inscricoes"] = pontuar(
        cenario,
        gestor,
        ["70.0000"] * 8,
        primeiro=1901,
        sufixo="190",
    )
    # A publicação do marco é o que torna o Resultado da Etapa visível ao titular, e sem ela não há
    # objeto recorrível: a interposição seria recusada por `appeal_not_visible`, com razão (D-003).
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-historico-190")
    cenario["publicacao"] = publicar_o_ato(cenario, chave="publicar-historico-190")
    return cenario


def superar(cenario, inscricao, pontuacao, *, indice):
    """Um sucessor do par, pelo caminho de verdade: interpor, admitir, julgar.

    **Não dá para forjá-lo.** O sucessor precisa citar decisão de recurso da mesma inscrição e da
    mesma Etapa, e três gatilhos cobram isso — o que é a garantia funcionando. Montar o par à mão
    mediria o custo de ler uma cadeia que o produto nunca produziria.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.recursos_us4 import assinatura_de, julgador

    anterior = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    peca = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=anterior,
        fundamentacao="A prova entregue não foi considerada no parecer.",
        assinatura_do_objeto=str(anterior.pk),
        idempotency_key=f"interpor-historico-{indice}",
    )
    admitir(
        actor=julgador(),
        recurso_id=peca.id,
        admitido=True,
        motivo="Tempestivo e regularmente instruído.",
        assinatura_do_estado=assinatura_de(peca),
        idempotency_key=f"admitir-historico-{indice}",
    )
    peca.refresh_from_db()
    julgar(
        actor=julgador(),
        recurso_id=peca.id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="O documento juntado na inscrição não foi considerado.",
        etapa_id=cenario["etapa"],
        pontuacao=pontuacao,
        assinatura_do_resultado=str(anterior.id),
        idempotency_key=f"julgar-historico-{indice}",
    )


def custo(cenario, inscricoes):
    with CaptureQueriesContext(connection) as capturadas:
        historicos_dos_pares([item.id for item in inscricoes], cenario["etapa"])
    return len(capturadas)


def test_o_custo_nao_cresce_com_o_numero_de_pares_corrigidos(etapa_com_pares):
    """Um par corrigido e oito custam o mesmo: a diferença seria o N+1 que a revisão encontrou."""
    inscricoes = etapa_com_pares["inscricoes"]

    superar(etapa_com_pares, inscricoes[0], "80.0000", indice=0)
    com_um = custo(etapa_com_pares, inscricoes)

    for indice, inscricao in enumerate(inscricoes[1:], start=1):
        superar(etapa_com_pares, inscricao, "80.0000", indice=indice)

    assert custo(etapa_com_pares, inscricoes) == com_um == 1


def test_sem_par_algum_nao_consulta(etapa_com_pares):
    """Lista vazia não paga leitura: o painel sem correção nenhuma é o caso comum."""
    assert custo(etapa_com_pares, []) == 0


def test_o_conteudo_e_o_mesmo_que_a_leitura_por_par_devolvia(etapa_com_pares):
    """Trocar o laço por um lote não pode trocar a resposta."""
    from processo_seletivo.resultados.application.selectors import historico_do_par

    inscricoes = etapa_com_pares["inscricoes"][:3]
    for indice, inscricao in enumerate(inscricoes):
        superar(etapa_com_pares, inscricao, "80.0000", indice=indice)

    em_lote = historicos_dos_pares([item.id for item in inscricoes], etapa_com_pares["etapa"])

    for inscricao in inscricoes:
        um_a_um = historico_do_par(inscricao.id, etapa_com_pares["etapa"])
        assert [linha["resultado"].id for linha in em_lote[inscricao.id]] == [
            linha["resultado"].id for linha in um_a_um
        ]
        assert [linha["vigente"] for linha in em_lote[inscricao.id]] == [
            linha["vigente"] for linha in um_a_um
        ]


def test_a_tela_da_etapa_paga_uma_leitura_para_a_pagina_inteira(etapa_com_pares):
    """O que o painel chama é `_historicos_superados`, e é ali que o laço morava.

    Medir o selector prova a propriedade; medir a função que a tela usa prova que ela **consome** o
    selector. Sem esta, trocar a implementação de volta por um laço passaria despercebido.
    """
    from processo_seletivo.interface.views import _historicos_superados
    from processo_seletivo.resultados.models import ResultadoEtapa

    for indice, inscricao in enumerate(etapa_com_pares["inscricoes"]):
        superar(etapa_com_pares, inscricao, "80.0000", indice=indice)
    linhas = list(
        ResultadoEtapa.vigentes.filter(
            edital=etapa_com_pares["edital"], etapa_id=etapa_com_pares["etapa"]
        )
    )
    assert sum(1 for linha in linhas if linha.resultado_anterior_id is not None) == 8

    with CaptureQueriesContext(connection) as capturadas:
        historicos = _historicos_superados(linhas, etapa_com_pares["etapa"])

    assert len(capturadas) == 1, "oito pares corrigidos, uma leitura"
    assert len(historicos) == 8
