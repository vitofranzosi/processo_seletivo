"""A vaga que vaga é chamada para o próximo do **mesmo** recorte (019, `SC-086`, `US2`).

**É o que impede a primeira desistência de parar o certame.** Hoje isso acontece numa planilha: a
pessoa desiste, alguém anota, e o próximo é chamado por leitura manual da lista. O risco não é o
trabalho — é chamar o próximo da lista **errada**.

**Uma vaga reservada que vagasse e fosse chamada na ampla moveria quantidade entre listas sem ato**,
e é exatamente o que a `FR-270` proíbe. Mover quantidade é a reversão da `016`, que é declarada,
motivada e registrada — e não uma consequência silenciosa de alguém ter desistido.
"""

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.convocar import convocar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.application.selectors import ocupacao_do_recorte
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, MARCO, certame_sorteado_com_quadro

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def certame(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Certame de cotas com **três** candidatas na PPI e **uma** vaga reservada.

    Uma titular e duas suplentes na mesma lista: é o mínimo para que a vaga que vaga tenha para onde
    ir sem atravessar recorte.
    """
    certame = certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="suplencia-019",
        com_corte=True,
        quantos=6,
        cotistas_ppi=4,
        geral=1,
        ppi=1,
        pcd=1,
        # **A faixa precisa ser maior que o alvo, senão não existe suplente nenhum.** Com alvo 1 na
        # ampla, uma pessoa ocupa vaga de ampla e sai da reserva; o excedente de 3 garante que a
        # faixa da PPI alcance mais de uma das quatro cotistas, que é o que a suplência exige.
        excedente=3,
    )
    _habilitar(certame, certame["inscricoes"])
    _emitir_cortes(certame, gestor)
    return certame


def _habilitar(certame, inscricoes):
    versao = effective_version(edital_id=certame["edital"].id)
    agora = timezone.now()
    for inscricao in inscricoes:
        ResultadoEtapa.objects.create(
            inscricao=inscricao,
            edital=certame["edital"],
            versao=versao,
            etapa_id=certame["etapa_governada"],
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="Documentação deferida",
            consolidado_em=agora,
            consolidado_por="teste",
        )


def _emitir_cortes(certame, gestor):
    from processo_seletivo.classificacao.application.corte import calcular_corte
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta,
        emitir_corte,
    )

    for indice, lista in enumerate((None, LISTA_PPI)):
        proposta = calcular_corte(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista
        )
        emitir_corte(
            actor=gestor,
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=lista,
            idempotency_key=f"suplencia-019-corte-{indice}",
            correlation_id="teste-convocacao-019",
            confirmacao_do_calculo=assinatura_da_proposta(proposta),
        )


def apurar(certame, gestor, *, lista_id, chave, motivo=""):
    return emitir_apuracao(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
        motivo=motivo,
    )


def contexto(certame, lista_id):
    return selectors.contexto_do_recorte(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )


def chamar(certame, gestor, inscricao, *, lista_id, chave, especie=nomes.VAGA_INICIAL):
    return convocar(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        inscricao_id=inscricao,
        especie=especie,
        fundamento="No interesse da Administração, item 8.2 do Edital 77/2026.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
    )


def responder(certame, gestor, convocacao_id, especie, chave):
    return desfechar(
        actor=gestor,
        processo_id=certame["processo"].id,
        convocacao_id=convocacao_id,
        especie=especie,
        fundamento="Manifestação registrada em processo.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
    )


def test_a_fila_da_lista_reservada_so_tem_quem_concorre_nela(certame, gestor):
    """`SC-086`: o recorte é `(perfil, marco, lista)`, e a fila é montada sobre a faixa dele.

    **A premissa dos demais testes, dita em voz alta.** Se a fila da PPI trouxesse gente da ampla, a
    chamada seguinte atravessaria recorte sem que nada acusasse.
    """
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="sup-apura-ppi")
    cotistas = {i.id for i in certame["cotistas_ppi"]}

    fila = contexto(certame, LISTA_PPI)["fila"]

    assert fila, "a PPI tem gente chamável"
    assert set(fila) <= cotistas, "e ninguém de fora da lista reservada"


def test_a_desistencia_na_reservada_abre_vaga_na_mesma_lista(certame, gestor):
    """O ciclo da `US2` dentro de um recorte só (`SC-086`).

    A vaga reservada que vagou **continua sendo da reserva**: quantidade nenhuma muda de lista, e a
    fila seguinte continua sendo a da mesma lista.

    **A ordem do sorteio é sorteada**, e por isso este teste afirma o que vale qualquer que ela
    seja: a vaga volta a faltar na reserva, e quem pode ocupá-la concorre nela. O ciclo numérico
    completo — desistência, chamada e o número voltando — está medido no `test_ciclo_do_77`, onde a
    ordem é determinística.
    """
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="sup-apura-1")
    cotistas = {i.id for i in certame["cotistas_ppi"]}
    titular = contexto(certame, LISTA_PPI)["fila"][0]

    convocada = chamar(certame, gestor, titular, lista_id=LISTA_PPI, chave="sup-titular")
    responder(certame, gestor, convocada["id"], nomes.DESISTENCIA_EXPRESSA, "sup-desiste")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="sup-apura-2", motivo="Desistência")

    numeros = ocupacao_do_recorte(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=LISTA_PPI
    )
    assert numeros["faltando"] == 1, "a vaga reservada voltou a faltar"

    seguinte = contexto(certame, LISTA_PPI)["fila"]
    assert titular not in seguinte, "quem desistiu não é chamável de novo"
    assert set(seguinte) <= cotistas, "e quem pode ser chamado concorre nesta lista"


def test_o_aceite_do_suplente_da_mesma_lista_devolve_o_numero(certame, gestor):
    """E é a metade que fecha o ciclo: a reserva volta a ter a vaga ocupada, por gente dela."""
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="ac-apura-1")
    titular = contexto(certame, LISTA_PPI)["fila"][0]
    convocada = chamar(certame, gestor, titular, lista_id=LISTA_PPI, chave="ac-titular")
    responder(certame, gestor, convocada["id"], nomes.DESISTENCIA_EXPRESSA, "ac-desiste")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="ac-apura-2", motivo="Desistência")
    fila = contexto(certame, LISTA_PPI)["fila"]
    assert fila, "a faixa da reserva alcança mais de uma cotista, e a vaga tem para onde ir"

    chamada = chamar(
        certame, gestor, fila[0], lista_id=LISTA_PPI, chave="ac-suplente", especie=nomes.SUPLENCIA
    )
    responder(certame, gestor, chamada["id"], nomes.ACEITE, "ac-aceite")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="ac-apura-3", motivo="Aceite da suplente")

    numeros = ocupacao_do_recorte(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=LISTA_PPI
    )
    assert numeros["faltando"] == 0, "o aceite da suplente devolve o número"


def test_a_desistencia_na_reservada_nao_move_quantidade_para_a_ampla(certame, gestor):
    """`FR-270`: mover quantidade entre recortes é a reversão da `016`, e ela é ato declarado.

    O que este teste impede não dá erro: dá uma vaga reservada virando vaga de ampla concorrência
    porque alguém desistiu — sem ato, sem motivo e sem registro.
    """
    from processo_seletivo.ocupacao.models import MovimentoDeVaga

    apurar(certame, gestor, lista_id=None, chave="sup-apura-ampla")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="sup-apura-ppi-2")
    antes = ocupacao_do_recorte(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    titular = contexto(certame, LISTA_PPI)["fila"][0]
    convocada = chamar(certame, gestor, titular, lista_id=LISTA_PPI, chave="sup-mv-titular")

    responder(certame, gestor, convocada["id"], nomes.DESISTENCIA_EXPRESSA, "sup-mv-desiste")
    apurar(certame, gestor, lista_id=LISTA_PPI, chave="sup-mv-apura", motivo="Desistência")

    depois = ocupacao_do_recorte(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert depois["publicadas"] == antes["publicadas"]
    assert depois["efetivas"] == antes["efetivas"]
    assert not MovimentoDeVaga.objects.filter(apuracao__edital=certame["edital"]).exists()
