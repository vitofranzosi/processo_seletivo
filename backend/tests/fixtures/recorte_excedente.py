"""O certame com a Modalidade AC apontada como a ampla, e o acervo que o sorteio fazia nela (122).

**O acervo é montado pelo caminho antigo, com a recusa desligada só durante a montagem.** Depois da
`122`, congelar, sortear e divulgar no recorte excedente são recusados no comando (FR-3897 a
FR-3899), e o único jeito de reproduzir o que a instalação já tem gravado é chamar os mesmos
comandos sem a recusa. Gravar as linhas à mão produziria um acervo que nenhum comando produziu, e os
testes do histórico falariam de uma coisa que não existe.

Funções ficam aqui, e as fixtures em `tests/conftest.py` — a regra que `tests/fixtures/corte.py`
registra para não redefinir fixture no importador.
"""

from contextlib import ExitStack, contextmanager
from unittest import mock

from tests.fixtures.ocupacao_sorteada import rascunho_sorteado_com_quadro
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, MARCO, METODO, presidente

LISTA_AC = "00000000-0000-4000-8000-000000000a61"
# Uma reserva **sem linha no quadro**: é a única que uma Retificação pode apontar como a ampla
# (a validação recusa apontar Modalidade com linha própria), e é ela que o T3 precisa.
LISTA_OUTRA = "00000000-0000-4000-8000-000000000a62"

OPERACIONAIS = (None, LISTA_PPI, LISTA_PCD)

# Quem declara o quê: duas pessoas declaram AC, uma PPI, uma PcD, e as duas últimas nada.
DECLARADAS = {0: LISTA_PPI, 1: LISTA_PCD, 2: LISTA_AC, 3: LISTA_AC}

_ONDE_A_RECUSA_MORA = (
    "processo_seletivo.sorteios.application.relacao.exigir_recorte_operacional",
    "processo_seletivo.sorteios.application.sorteio.exigir_recorte_operacional",
    "processo_seletivo.divulgacao.application.publicar.exigir_recorte_operacional",
)


@contextmanager
def sem_a_recusa():
    """Os comandos como eram antes da `122`: o recorte excedente congela, sorteia e divulga."""
    with ExitStack() as pilha:
        for alvo in _ONDE_A_RECUSA_MORA:
            pilha.enter_context(mock.patch(alvo, lambda *a, **k: None))
        yield


def rascunho_com_ac(*, apontada=True, com_outra=False, **quadro):
    """O rascunho do certame de cotas com a Modalidade AC declarada e, se pedido, apontada."""
    from tests.fixtures.edital import PROFILE_ID

    rascunho = rascunho_sorteado_com_quadro(**quadro)
    for perfil in rascunho["profiles"]:
        if str(perfil["id"]) != PROFILE_ID:
            continue
        perfil["competitionModalities"] = [
            {"id": LISTA_AC, "code": "AC", "name": "Ampla Concorrência", "reservedVacancies": 0},
            *perfil["competitionModalities"],
        ]
        if com_outra:
            perfil["competitionModalities"].append(
                {"id": LISTA_OUTRA, "code": "OUT", "name": "Outra reserva", "reservedVacancies": 0}
            )
        if apontada:
            perfil["generalCompetitionModalityId"] = LISTA_AC
    return rascunho


def certame_com_ac(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    apontada=True,
    acervo=False,
    sortear_ac=True,
    com_outra=False,
    prefixo="recorte-122",
    **quadro,
):
    """Edital publicado, inscrições com AC declarada, e os três recortes operacionais sorteados.

    - `apontada`: o Perfil aponta AC como a ampla. Sem apontamento, AC é recorte operacional e é
      sorteada como as outras — é o ponto de partida do registro **tornado** excedente.
    - `acervo`: com apontamento, sorteia também AC pelo caminho antigo — o registro **nascido**.
    - `sortear_ac`: com `False`, a relação de AC fica congelada e sem sorteio (T6, FR-3898).

    Devolve o certame com `atos` e `relacoes` por `lista_id`.
    """
    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from processo_seletivo.comissoes.domain.funcoes import Funcao
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
        draft=rascunho_com_ac(apontada=apontada, com_outra=com_outra, **quadro),
    )
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo=prefixo)
    declaradas = dict(DECLARADAS)
    if com_outra:
        declaradas[4] = LISTA_OUTRA
    inscricoes = inscrever(edital, 6, primeiro=1201, modalidades=declaradas)

    recortes = (
        OPERACIONAIS
        + ((LISTA_OUTRA,) if com_outra else ())
        + ((LISTA_AC,) if (acervo or not apontada) else ())
    )
    with sem_a_recusa():
        relacoes = {
            lista: publicar_relacao(
                actor=presidente(),
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=PROFILE_ID,
                marco_id=MARCO,
                lista_id=lista,
                idempotency_key=f"{prefixo}-relacao-{indice}",
                correlation_id="teste-122",
            )["relacao"]
            for indice, lista in enumerate(recortes)
        }
        ocorrencia = observar_ocorrencia(
            actor=presidente(),
            processo_id=edital.processo_id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key=f"{prefixo}-ocorrencia",
            correlation_id="teste-122",
            fonte_externa=FonteDeTeste(),
        )["ocorrencia"]
        for indice, (lista, relacao) in enumerate(relacoes.items()):
            if lista == LISTA_AC and not sortear_ac:
                continue
            constituir_sorteio(
                actor=presidente(),
                processo_id=edital.processo_id,
                edital_id=edital.id,
                relacao_id=relacao,
                ocorrencia_id=ocorrencia,
                idempotency_key=f"{prefixo}-sorteio-{indice}",
                correlation_id="teste-122",
            )
    atos = {
        (str(ato.lista_id) if ato.lista_id else None): ato
        for ato in AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO)
    }
    return {
        "edital": edital,
        "processo": edital.processo,
        "perfil": PROFILE_ID,
        "marco": MARCO,
        "inscricoes": inscricoes,
        "relacoes": {
            (str(lista) if lista else None): relacao for lista, relacao in relacoes.items()
        },
        "ocorrencia": ocorrencia,
        "atos": atos,
    }


def divulgar(certame, lista, *, chave, natureza="PRELIMINAR", recusa_desligada=False):
    """Divulga o ato vigente daquele recorte pelo command, recalculando a assinatura como a tela.

    Não usa `publicar_o_ato` porque ele lê a publicação anterior **da ampla**: com três recortes
    divulgados no mesmo marco, a assinatura do segundo sairia com o predecessor errado.
    """
    from processo_seletivo.divulgacao.application.publicar import (
        assinatura_da_previa,
        publicar_resultado,
    )
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.conteudo import compor
    from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
    from tests.fixtures.divulgacao import ator_publicador

    ato = certame["atos"][lista]
    anterior = vigente_do_marco(
        edital=certame["edital"], marco_id=ato.marco_id, lista_id=ato.lista_id
    )

    def publicar():
        return publicar_resultado(
            actor=ator_publicador(),
            processo_id=certame["edital"].processo_id,
            edital_id=certame["edital"].id,
            marco_id=ato.marco_id,
            ato_id=ato.id,
            natureza=natureza,
            autoridade=str(AUTORIDADE_DO_RESULTADO),
            confirmacao_da_previa=assinatura_da_previa(
                ato=ato, publicacao_anterior=anterior, projecao=compor(ato)
            ),
            idempotency_key=chave,
            correlation_id="teste-122",
            declaracao_de_encerramento=(
                "O prazo recursal encerrou-se sem interposição, conforme o Edital."
                if natureza == "DEFINITIVA"
                else ""
            ),
        )

    if recusa_desligada:
        with sem_a_recusa():
            return publicar()
    return publicar()


def retificar_o_apontamento(api_client, edital, valor, *, suffix):
    """Publica uma Retificação que troca o apontamento da ampla do Perfil para `valor`."""
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.publicacao import retify

    return retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PROFILE_ID}/generalCompetitionModalityId",
                "operation": "REPLACE",
                "newValue": valor,
            }
        ],
        suffix=suffix,
    )
