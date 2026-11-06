"""Os certames do andamento da seleção (127), um por família da matriz de compatibilidade.

Cada função monta o mínimo que a família precisa, sobre as fixtures que as features de origem já
usam — o sorteio da `021`, o corte da `014`, a convocação da `019` —, para que quem leia reconheça o
cenário. S3 e P3 não estão aqui: são compostos à mão nos testes puros
(`tests/unit/interface/test_andamento_composicao.py`), porque nem o banco de demonstração os tem.
"""

from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import alocar_em, constituir, inscrever, publicar_processo_com_etapas
from tests.fixtures.corte import rascunho
from tests.fixtures.edital import corte_que_nao_governa
from tests.fixtures.mesa import distribuir_para
from tests.fixtures.publicacao import publish_original


def certame_s1(gestor, api_client, manager_headers, process_payload, *, quantos=3, seed=0):
    """S1 (35, 57): sorteio que não enumera Etapa, e as duas Etapas do rascunho sem ligação.

    A presidência é `maria`, como no sorteio da `021`: os comandos do sorteio passam pela comissão.
    """
    edital = publicar_processo_com_etapas(api_client, manager_headers, process_payload, seed=seed)
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo=f"s1-{seed}")
    inscricoes = inscrever(edital, quantos, primeiro=701) if quantos else []
    return {"edital": edital, "inscricoes": inscricoes}


def certame_p1(gestor, api_client, manager_headers, process_payload, *, quantos=3, distribuidas=2):
    """P1 (91): pontuação que enumera a Prova didática; a Entrevista vem depois e nada a consome.

    `joao` é avaliador alocado da Prova, com `distribuidas` inscrições atribuídas e nenhuma
    concluída; `maria` preside. É a situação do 91 no estudo: avaliar e distribuir em aberto, e a
    ordem esperando as duas.
    """
    draft, pontuada = rascunho(cut=corte_que_nao_governa())
    edital = publish_original(api_client, manager_headers, process_payload, draft=draft)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="p1-127",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, pontuada["id"])
    inscricoes = inscrever(edital, quantos, primeiro=801)
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": pontuada["id"],
    }
    if distribuidas:
        distribuir_para(contexto, gestor, ["joao"], inscricoes[:distribuidas], chave="p1-127-lote")
    return {**contexto, "inscricoes": inscricoes, "pontuada": pontuada}
