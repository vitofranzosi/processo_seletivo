"""O cenário da US5: uma Etapa que declara duas avaliações, e uma banca que as executa.

Fica separado dos testes porque quatro arquivos da Phase 7 partem do mesmo ponto — dois avaliadores
alocados, inscrições distribuídas — e repetir a montagem faria cada um deles divergir do outro com
o tempo.
"""

from processo_seletivo.avaliacoes.application.avaliacao import concluir
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.conftest import ator_institucional
from tests.fixtures.comissao import (
    ETAPA_A1,
    alocar_em,
    constituir,
    inscrever,
    publicar_processo_com_etapas,
)
from tests.fixtures.edital import identificador


def montar_banca(gestor, api_client, manager_headers, *, seed, codigo, avaliadores=("joao", "ana")):
    """Edital publicado com dupla avaliação, comissão constituída e avaliadores alocados."""
    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {"number": codigo, "year": 2026, "title": f"Edital {codigo}"},
        },
        seed=seed,
        avaliacoes=2,
        maxima="100.0000",
    )
    etapa = identificador(ETAPA_A1, seed)
    processo = edital.processo
    pessoas = [("maria", Funcao.PRESIDENTE)] + [(nome, Funcao.MEMBRO) for nome in avaliadores]
    membros = constituir(gestor, processo, pessoas, prefixo=f"banca-{seed}")
    for nome in avaliadores:
        alocar_em(gestor, processo, membros[nome], edital, etapa, chave=f"aloc-{seed}-{nome}")
    return {"edital": edital, "etapa": etapa, "processo": processo, "membros": membros}


def distribuir_para(cenario, gestor, nomes, inscricoes, *, chave="lote"):
    return distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[cenario["membros"][nome].id for nome in nomes],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def concluir_como(cenario, subject, inscricao, *, pontuacao="80", parecer="Atende", revisao=1):
    versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    avaliacao, _ = concluir(
        ator=ator_institucional(subject),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
        pontuacao=pontuacao,
        parecer=parecer,
        expected_revision=revisao,
        versao_reconhecida=versao.id,
        correlation_id="teste",
    )
    return avaliacao


def inscricoes_de(cenario, quantas, *, primeiro):
    return inscrever(cenario["edital"], quantas, primeiro=primeiro)


def constituir_presidencia(gestor, cenario, *, subject="paula"):
    """Outra pessoa preside, para que a presidência anterior possa ser rebaixada.

    A 011 recusa deixar a comissão sem presidente enquanto há alocação ativa, e o invariante dela
    continua valendo aqui.
    """
    from processo_seletivo.comissoes.application.comissao import adicionar_membro

    membro, _ = adicionar_membro(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject=subject,
        funcao=Funcao.PRESIDENTE,
        idempotency_key=f"sucessao-{cenario['processo'].id}",
        correlation_id="teste",
    )
    return membro
