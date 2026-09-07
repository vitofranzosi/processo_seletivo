"""O cenário julgável da US4: uma peça interposta e admitida, com o Resultado ainda vigente.

Ela existe porque quatro módulos de teste precisam do mesmo ponto de partida — julgar, piorar,
concorrer e a cadeia a jusante —, e montá-lo em cada um faria os quatro divergirem no primeiro
ajuste da fixture.

**O caminho é o real**: interpor pelo comando do candidato e admitir pelo comando da instituição.
Gravar por atalho provaria o julgamento contra um estado que o produto não produz.
"""

from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.recursos.application.interpor import interpor
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato

JULGADORA = "helena.julgadora"


def julgador(subject=JULGADORA):
    return ator_institucional(subject, "recurso:julgar")


def cenario_julgavel(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    seed,
    codigo,
    pontuacoes=("55.0000", "90.0000"),
    admitir_a_peca=True,
    publicar=True,
    na_primeira_etapa=False,
):
    """Edital publicado, marco divulgado, recurso interposto pela primeira inscrição e admitido.

    A primeira nota é **abaixo da mínima de 60** de propósito: é a inscrição eliminada, que é quem
    de fato recorre — e é contra a eliminação dela que a *non reformatio* será medida.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato

    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        # O marco intermediário existe quando a eliminação é na primeira Etapa: é ele que divulga
        # o resultado dela, e sem divulgação não há objeto recorrível — a interposição seria
        # recusada por `appeal_not_visible`, com razão.
        com_intermediario=na_primeira_etapa,
        # A Etapa do marco é eliminatória com mínima 60: é o que faz existir uma **eliminação** a
        # contestar. Sem regra publicada, toda nota habilita, e a US4 inteira ficaria provando o
        # deferimento de quem nunca foi prejudicado.
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    # `na_primeira_etapa` existe para a US8: a progressão retroativa só se enxerga quando a
    # eliminação está numa Etapa **anterior** à seguinte, e a Etapa do marco é a última. Sem isso,
    # "reaparece na Etapa seguinte" não teria Etapa seguinte para reaparecer.
    alvo = cenario["primeira"] if na_primeira_etapa else cenario["etapa"]
    cenario["inscricoes"] = pontuar(
        cenario, gestor, list(pontuacoes), primeiro=seed * 10 + 1, sufixo=str(seed), etapa=alvo
    )
    cenario["etapa_do_recurso"] = alvo
    marco = cenario["marco_intermediario"] if na_primeira_etapa else cenario["marco"]
    cenario["marco_do_recurso"] = marco
    cenario["ato"] = emitir(cenario, gestor, marco=marco, chave=f"emitir-018-{seed}")
    publicacao = (
        publicar_o_ato(cenario, chave=f"publicar-018-{seed}", ato=cenario["ato"])
        if publicar
        else None
    )

    inscricao = cenario["inscricoes"][0]
    superado = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=alvo)
    recurso = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=superado,
        fundamentacao="A prova didática entregue não foi considerada no parecer.",
        assinatura_do_objeto=str(superado.pk),
        idempotency_key=f"interpor-{seed}",
    )
    chave_da_admissao = f"admitir-{seed}"
    if admitir_a_peca:
        admitir(
            actor=julgador(),
            recurso_id=recurso.id,
            admitido=True,
            motivo="Tempestivo e regularmente instruído.",
            assinatura_do_estado="",
            idempotency_key=chave_da_admissao,
        )
        recurso.refresh_from_db()
    return {
        "cenario": cenario,
        "recurso": recurso,
        "superado": superado,
        "inscricao": inscricao,
        "publicacao": publicacao,
        "versao": selecao_publica(edital_id=inscricao.edital_id),
        "chave_da_admissao": chave_da_admissao,
    }
