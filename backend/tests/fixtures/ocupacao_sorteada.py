"""O certame de sorteio com cotas, com quadro de vagas — o cenário que a `016` precisava.

**Por que ele existe, e não bastava o da `014`.** Apurar a ocupação de uma cota exige **ordem
vigente daquele recorte**, e `emitir_ordem` fixa `lista_id` nulo por decisão declarada (PR #85): um
ato computado é sempre o da ampla concorrência, e **só o sorteio emite por lista**. Logo a reversão
de cota e a concorrência concomitante só são alcançáveis aqui.

E é coerente com a amostra: o 28/2026 e o 57/2026 — os dois Editais que declaram reversão e os dois
que têm concorrência concomitante — são certames de **sorteio**.

**O que este módulo acrescenta ao `certame_com_cotas` da `021`** é o quadro de vagas, a declaração
da reversão, e o percurso completo até haver `AtoDeOrdenacao` **por lista**: relação publicada por
recorte, ocorrência observada uma vez, e o sorteio constituído três vezes.

Funções ficam aqui, e a fixture fica no `conftest.py` de cada pasta — a regra que
`tests/fixtures/corte.py` registra para não redefinir fixture no importador.
"""

from tests.fixtures.sorteio import (
    LISTA_PCD,
    LISTA_PPI,
    MARCO,
    METODO,
    marco_com_metodo,
    presidente,
)

LINHA_GERAL = "00000000-0000-4000-8000-000000000841"
LINHA_PPI = "00000000-0000-4000-8000-000000000842"
LINHA_PCD = "00000000-0000-4000-8000-000000000843"

# Os recortes na ordem em que a tela os lista: a linha geral primeiro, as reservas depois.
RECORTES = (None, LISTA_PPI, LISTA_PCD)


def rascunho_sorteado_com_quadro(*, geral=2, ppi=1, pcd=1, reversao=None, ampla_declarada=None):
    """O rascunho do certame de cotas, com quadro publicado e reversão opcional.

    **O total do Perfil acompanha o quadro**, senão a conferência da soma da `025` recusa a
    submissão — descobri isso pela recusa `blocking_findings`, que é exatamente onde ela deve
    aparecer.
    """
    from tests.fixtures.comissao import rascunho_com_etapas
    from tests.fixtures.edital import PROFILE_ID

    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    for perfil in rascunho["profiles"]:
        if str(perfil["id"]) != PROFILE_ID:
            continue
        perfil["competitionModalities"] = [
            {
                "id": LISTA_PPI,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "reservedVacancies": ppi,
            },
            {
                "id": LISTA_PCD,
                "code": "PCD",
                "name": "Pessoas com deficiência",
                "reservedVacancies": pcd,
            },
        ]
        perfil["vacancyTable"] = [
            {"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": geral},
            {"id": LINHA_PPI, "modalityId": LISTA_PPI, "immediateVacancies": ppi},
            {"id": LINHA_PCD, "modalityId": LISTA_PCD, "immediateVacancies": pcd},
        ]
        perfil["immediateVacancies"] = geral + ppi + pcd
        if reversao is not None:
            perfil["vacancyReversion"] = {"kind": reversao}
        if ampla_declarada is not None:
            perfil["generalCompetitionModalityId"] = ampla_declarada
    return rascunho


def certame_sorteado_com_quadro(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    quantos=6,
    prefixo="ocupacao-016-sort",
    **quadro,
):
    """Edital publicado, cotistas inscritos, e **uma ordem por recorte** — ampla, PPI e PcD.

    Devolve o dicionário do certame acrescido de `atos`, que mapeia cada `lista_id` ao
    `AtoDeOrdenacao` daquele recorte. É esse mapa que torna a US4 alcançável.
    """
    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
    from processo_seletivo.sorteios.application.relacao import publicar_relacao
    from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
    from tests.fixtures.comissao import constituir, inscrever
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_sorteado_com_quadro(**quadro),
    )
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo=prefixo)
    inscricoes = inscrever(edital, quantos, primeiro=701)
    # **Os dois primeiros declaram cota, e é isso que a concorrência concomitante exercita**: eles
    # figuram na lista de ampla concorrência **e** na reserva deles, com numeração própria em cada
    # (021, FR-004; 28/2026, itens 4.3.1 e 8.7).
    Inscricao.objects.filter(pk=inscricoes[0].pk).update(modality_id=LISTA_PPI)
    Inscricao.objects.filter(pk=inscricoes[1].pk).update(modality_id=LISTA_PCD)
    for inscricao in inscricoes:
        inscricao.refresh_from_db()

    relacoes = {
        lista: publicar_relacao(
            actor=presidente(),
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=lista,
            idempotency_key=f"{prefixo}-relacao-{indice}",
            correlation_id="teste-ocupacao-016",
        )["relacao"]
        for indice, lista in enumerate(RECORTES)
    }
    # **A ocorrência é uma só para os três recortes**: o sorteio é o mesmo evento, e o que muda por
    # recorte é a relação que ele ordena.
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=edital.processo_id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key=f"{prefixo}-ocorrencia",
        correlation_id="teste-ocupacao-016",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]
    # O `lista` não entra no corpo: quem identifica o recorte é a relação, e o sorteio a lê.
    for indice, relacao in enumerate(relacoes.values()):
        constituir_sorteio(
            actor=presidente(),
            processo_id=edital.processo_id,
            edital_id=edital.id,
            relacao_id=relacao,
            ocorrencia_id=ocorrencia,
            idempotency_key=f"{prefixo}-sorteio-{indice}",
            correlation_id="teste-ocupacao-016",
        )
    atos = {
        ato.lista_id: ato for ato in AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO)
    }
    return {
        "edital": edital,
        "processo": edital.processo,
        "perfil": PROFILE_ID,
        "marco": MARCO,
        "inscricoes": inscricoes,
        "cotista_ppi": inscricoes[0],
        "cotista_pcd": inscricoes[1],
        "atos": atos,
    }
