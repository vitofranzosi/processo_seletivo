"""A publicação de convocados no GPS: o ato, os dois efeitos e o prazo (149, US1, US3, US4).

**O que estes casos prendem é a fronteira entre ato oficial e relação informativa.** Na forma *por
publicação*, a publicação é o ato que convoca: ela grava a comunicação, e o prazo corre dela. Em
todo o resto — a mensagem enviada, a publicação registrada fora do GPS —, a relação é informativa, e
nenhum instante de prazo pode mudar. Um teste que só olhasse a página não veria a diferença.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.comunicar import COMUNICAR
from processo_seletivo.convocacao.application.publicar import (
    NADA_A_PUBLICAR,
    PREVIA_OBSOLETA,
    PUBLICAR,
    VEICULO_NAO_DECLARADO,
    previa_da_publicacao,
    publicar_convocados,
)
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.domain import publicacao as dominio
from processo_seletivo.convocacao.models import (
    ComunicacaoEmitida,
    Convocacao,
    ConvocacaoPublicada,
    DocumentoDaPublicacaoDeConvocados,
    PublicacaoDeConvocados,
)
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

VEICULO = "item 7.2 do Edital"
REFERENCIA_EXTERNA = "site do Cefor, 11/11/2026"
CINCO_DIAS = timedelta(days=5)

postgresql = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e privilégio só existem no PostgreSQL"
)


@pytest.fixture
def caixa_de_saida(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def fixtures(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return gestor, api_client, manager_headers, process_payload


def certame(fixtures, *, forma=FORMA_POR_PUBLICACAO, prefixo, **extras):
    gestor, api_client, manager_headers, process_payload = fixtures
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo=prefixo, forma=forma, **extras
    )


def chamar(cenario, gestor, chave, *, vencimento=None):
    return cenarios.convocar_primeira(
        cenario, gestor, chave=chave, vencimento=vencimento or timezone.now() + CINCO_DIAS
    )


def previa(edital, recortes=None):
    return previa_da_publicacao(edital=edital, recortes=recortes, at=timezone.now())


def publicar(edital, gestor, *, chave, veiculo=VEICULO, alcance=None, recortes=None):
    return publicar_convocados(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        recortes=recortes,
        alcance_confirmado=alcance
        if alcance is not None
        else previa(edital, recortes)["assinatura"],
        autoridade=str(AUTORIDADE_DO_RESULTADO),
        declaracao_do_veiculo=veiculo,
        idempotency_key=chave,
        correlation_id="teste-148",
    )


def registrar_fora(edital, gestor, convocacao, chave):
    from processo_seletivo.convocacao.application.comunicar import comunicar

    return comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        idempotency_key=chave,
        correlation_id="teste-148",
        referencia_da_publicacao=REFERENCIA_EXTERNA,
    )


def contagem():
    return (
        PublicacaoDeConvocados.objects.count(),
        ConvocacaoPublicada.objects.count(),
        DocumentoDaPublicacaoDeConvocados.objects.count(),
        ComunicacaoEmitida.objects.count(),
        RegistroAuditoria.objects.count(),
    )


def recusada(codigo, praticar):
    antes = contagem()
    with pytest.raises(DomainError) as erro:
        praticar()
    assert erro.value.code == codigo, erro.value.detail
    assert contagem() == antes, "a recusa não grava ato, vínculo, documento, comunicação nem trilha"
    return erro.value


# --- A prévia não pratica nada (FR-5708, SC-1864) -------------------------------------------------


def test_a_previa_mostra_o_que_seria_publicado_e_nao_grava_nada(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-previa")
    pessoa, _ = chamar(cenario, gestor, "p148-previa")
    antes = contagem()

    lida = previa(edital)
    escolhida_nenhuma = previa(edital, recortes=set())

    assert contagem() == antes
    assert lida["numero"] == 1 and lida["convoca"] == 1 and lida["divulga"] == 0
    [grupo] = lida["grupos"]
    assert grupo["efeito"] == dominio.CONVOCA
    assert [p["protocolo"] for p in grupo["pessoas"]] == [pessoa.protocolo]
    assert escolhida_nenhuma["escolhidas"] == [], "desmarcar o recorte tira as pessoas dele"


# --- B. Publicação nativa como ato oficial (FR-5702, SC-1852) -------------------------------------


def test_a_publicacao_nativa_convoca_e_o_prazo_corre_dela(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-nativa")
    pessoa, convocacao = chamar(cenario, gestor, "p148-nativa")
    assert not selectors.visivel_ao_candidato(convocacao), "a premissa: K-pub, invisível"

    declarado = publicar(edital, gestor, chave="p148-nativa-pub")

    ato = PublicacaoDeConvocados.objects.get(id=declarado["id"])
    [emitida] = ComunicacaoEmitida.objects.filter(convocacao=convocacao)
    assert (emitida.forma, emitida.resultado) == (FORMA_POR_PUBLICACAO, "ENVIADA")
    assert emitida.enviado_em == ato.publicado_em, "um instante só (D-003)"
    assert emitida.referencia_da_publicacao == dominio.referencia_nativa(1, ato.publicado_em)
    vinculo = ConvocacaoPublicada.objects.get(convocacao=convocacao)
    assert (vinculo.efeito, vinculo.comunicacao_id, vinculo.publicacao_id) == (
        "CONVOCA",
        emitida.id,
        ato.id,
    )
    assert (ato.numero, ato.declaracao_do_veiculo, ato.publicado_por) == (
        1,
        VEICULO,
        gestor.subject,
    )
    assert ato.signatario_id == AUTORIDADE_DO_RESULTADO
    assert ato.documento.bytes[:5] == b"%PDF-"
    # A visibilidade e o prazo pela regra de sempre (FR-3981 da `125`), sem regra nova.
    convocacao = Convocacao.objects.get(id=convocacao.id)
    assert selectors.visivel_ao_candidato(convocacao)
    assert selectors.estado_de(convocacao, agora=timezone.now()) == nomes.CONVOCADO_PRAZO_EM_CURSO
    assert selectors.vigentes_por_inscricao([pessoa.id])[pessoa.id] == convocacao
    # A trilha do ato e a da comunicação (FR-5711).
    assert RegistroAuditoria.objects.filter(operation=PUBLICAR, aggregate_id=ato.id).exists()
    trilha = RegistroAuditoria.objects.get(operation=COMUNICAR, aggregate_id=emitida.id)
    assert "1ª publicação de convocados" in trilha.reason


def test_sem_a_declaracao_do_veiculo_a_publicacao_que_convoca_e_recusada(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-veiculo")
    chamar(cenario, gestor, "p148-veiculo")

    erro = recusada(
        VEICULO_NAO_DECLARADO, lambda: publicar(edital, gestor, chave="p148-v", veiculo="  ")
    )
    assert erro.campo == "declaracao_do_veiculo"


def test_vencimento_ja_passado_fica_fora_com_o_motivo(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-vencido")
    _, convocacao = chamar(cenario, gestor, "p148-vencido")
    # A convocação é append-only: quem anda é o relógio da prévia.
    lida = previa_da_publicacao(edital=edital, at=convocacao.vencimento + timedelta(minutes=1))

    assert lida["escolhidas"] == []
    [recorte] = lida["recortes"]
    assert recorte["fora"][0]["motivo"] == dominio.MOTIVOS_DE_FORA[dominio.FORA_VENCIMENTO_PASSADO]


# --- A. Mensagem individual: informativa, sem mexer no prazo (FR-5705, SC-1851) ------------------


def test_a_mensagem_enviada_entra_como_divulgacao_e_o_prazo_nao_muda(
    fixtures, gestor, caixa_de_saida
):
    edital, _, _ = cenario = certame(
        fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="p148-msg"
    )
    _, convocacao = chamar(cenario, gestor, "p148-msg")
    cenarios.comunicar(edital, gestor, convocacao, chave="p148-msg-envio")
    [enviada] = ComunicacaoEmitida.objects.filter(convocacao=convocacao)
    estado_antes = selectors.estado_de(convocacao, agora=timezone.now())

    declarado = publicar(edital, gestor, chave="p148-msg-pub", veiculo="")

    assert list(ComunicacaoEmitida.objects.filter(convocacao=convocacao)) == [enviada]
    assert ComunicacaoEmitida.objects.get(id=enviada.id).enviado_em == enviada.enviado_em
    convocacao = Convocacao.objects.get(id=convocacao.id)
    assert selectors.estado_de(convocacao, agora=timezone.now()) == estado_antes
    vinculo = ConvocacaoPublicada.objects.get(convocacao=convocacao)
    assert (vinculo.efeito, vinculo.comunicacao_id) == ("DIVULGA", enviada.id)
    ato = PublicacaoDeConvocados.objects.get(id=declarado["id"])
    assert ato.declaracao_do_veiculo == "", "sem convocar ninguém, a declaração não tem objeto"
    assert (declarado["convoca"], declarado["divulga"]) == (0, 1)
    assert len(caixa_de_saida) == 1, "a publicação não envia mensagem nenhuma"


def test_a_mensagem_que_nao_saiu_nao_entra_em_publicacao_nenhuma(fixtures, gestor):
    """A publicação não substitui o envio individual (FR-5706)."""
    edital, _, _ = cenario = certame(
        fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="p148-msg-k"
    )
    chamar(cenario, gestor, "p148-msg-k")

    lida = previa(edital)

    assert lida["escolhidas"] == []
    [recorte] = lida["recortes"]
    assert recorte["fora"][0]["motivo"] == dominio.MOTIVOS_DE_FORA[dominio.FORA_MENSAGEM_PENDENTE]
    recusada(NADA_A_PUBLICAR, lambda: publicar(edital, gestor, chave="p148-msg-k-pub"))


# --- C. Publicação externa: preservada, e espelhável (FR-5734, SC-1853) --------------------------


def test_a_publicacao_externa_registrada_continua_e_a_relacao_a_cita(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-ext")
    _, convocacao = chamar(cenario, gestor, "p148-ext")
    registrar_fora(edital, gestor, convocacao, "p148-ext-reg")
    [registrada] = ComunicacaoEmitida.objects.filter(convocacao=convocacao)

    declarado = publicar(edital, gestor, chave="p148-ext-pub", veiculo="")

    assert list(ComunicacaoEmitida.objects.filter(convocacao=convocacao)) == [registrada]
    ato = PublicacaoDeConvocados.objects.get(id=declarado["id"])
    [grupo] = _conteudo(ato)["grupos"]
    assert grupo["efeito"] == "DIVULGA"
    assert grupo["canal"] == f"publicada em {REFERENCIA_EXTERNA}"


# --- Publicações sucessivas, sucessão e correção (SC-1854, SC-1856, SC-1857) ----------------------


def test_a_suplente_chamada_depois_entra_na_2a_publicacao(fixtures, gestor):
    edital, _, inscricoes = cenario = certame(fixtures, prefixo="p148-suplencia")
    _, primeira = chamar(cenario, gestor, "p148-sup-1")
    publicar(edital, gestor, chave="p148-sup-pub-1")
    documento_da_1a = PublicacaoDeConvocados.objects.get(numero=1, edital=edital).documento
    cenarios.desfechar(
        edital,
        gestor,
        Convocacao.objects.get(id=primeira.id),
        nomes.DESISTENCIA_EXPRESSA,
        "p148-sup-desiste",
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    suplente = Convocacao.objects.get(
        id=convocar(
            edital,
            gestor,
            fila[0],
            idempotency_key="p148-sup-2",
            vencimento=timezone.now() + CINCO_DIAS,
        )["id"]
    )

    declarado = publicar(edital, gestor, chave="p148-sup-pub-2")

    assert declarado["numero"] == 2 and declarado["convoca"] == 1
    assert ConvocacaoPublicada.objects.get(convocacao=suplente).publicacao.numero == 2
    assert ConvocacaoPublicada.objects.get(convocacao=primeira).publicacao.numero == 1
    depois = PublicacaoDeConvocados.objects.get(numero=1, edital=edital).documento
    assert bytes(depois.bytes) == bytes(documento_da_1a.bytes), "a 1ª não muda"


def test_a_correcao_de_convocacao_publicada_sai_marcada_na_seguinte(fixtures, gestor):
    from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

    edital, _, _ = cenario = certame(fixtures, prefixo="p148-correcao")
    pessoa, publicada = chamar(cenario, gestor, "p148-cor-1")
    publicar(edital, gestor, chave="p148-cor-pub-1")
    primeira = PublicacaoDeConvocados.objects.get(edital=edital, numero=1)
    bytes_da_1a, hash_da_1a = bytes(primeira.documento.bytes), primeira.conteudo_publico_hash

    corrigir(edital, gestor, Convocacao.objects.get(id=publicada.id), chave="p148-cor-120")
    sucessora = Convocacao.objects.get(convocacao_anterior=publicada)
    lida = previa(edital)
    [grupo] = lida["grupos"]
    assert grupo["pessoas"][0]["corrige"] == 1
    declarado = publicar(edital, gestor, chave="p148-cor-pub-2")

    segunda = PublicacaoDeConvocados.objects.get(id=declarado["id"])
    assert _conteudo(segunda)["grupos"][0]["pessoas"][0]["corrige"] == 1
    assert MOTIVO_DA_CORRECAO_NAO_VAI not in bytes(segunda.conteudo_publico).decode()
    primeira = PublicacaoDeConvocados.objects.get(id=primeira.id)
    assert bytes(primeira.documento.bytes) == bytes_da_1a
    assert primeira.conteudo_publico_hash == hash_da_1a
    emitida = ComunicacaoEmitida.objects.get(convocacao=sucessora)
    assert emitida.enviado_em == segunda.publicado_em, "o prazo da correção corre da 2ª"
    assert selectors.vigentes_por_inscricao([pessoa.id])[pessoa.id] == sucessora


MOTIVO_DA_CORRECAO_NAO_VAI = "A mensagem saiu com dois dias de atraso"


# --- Duplicidade e idempotência (FR-5707, FR-5708, SC-1858) ---------------------------------------


def test_a_mesma_chave_devolve_o_mesmo_ato_e_outra_chave_e_recusada(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-dup")
    chamar(cenario, gestor, "p148-dup")
    assinatura = previa(edital)["assinatura"]

    primeiro = publicar(edital, gestor, chave="p148-dup-a", alcance=assinatura)
    repetido = publicar(edital, gestor, chave="p148-dup-a", alcance=assinatura)

    assert repetido == primeiro
    assert PublicacaoDeConvocados.objects.filter(edital=edital).count() == 1
    recusada(
        PREVIA_OBSOLETA, lambda: publicar(edital, gestor, chave="p148-dup-b", alcance=assinatura)
    )


def test_a_previa_que_envelheceu_e_recusada(fixtures, gestor, caixa_de_saida):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-velha")
    _, convocacao = chamar(cenario, gestor, "p148-velha")
    velha = previa(edital)["assinatura"]
    registrar_fora(edital, gestor, convocacao, "p148-velha-reg")

    recusada(PREVIA_OBSOLETA, lambda: publicar(edital, gestor, chave="p148-v", alcance=velha))


def test_o_banco_recusa_a_mesma_convocacao_em_duas_publicacoes(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-uq")
    _, convocacao = chamar(cenario, gestor, "p148-uq")
    publicar(edital, gestor, chave="p148-uq-pub")
    vinculo = ConvocacaoPublicada.objects.get(convocacao=convocacao)
    outra = PublicacaoDeConvocados.objects.create(
        **{
            campo.attname: getattr(vinculo.publicacao, campo.attname)
            for campo in PublicacaoDeConvocados._meta.concrete_fields
            if campo.attname != "id"
        }
        | {"numero": 2}
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        ConvocacaoPublicada.objects.create(
            publicacao=outra,
            convocacao=convocacao,
            comunicacao=vinculo.comunicacao,
            efeito="DIVULGA",
        )


# --- Append-only nas camadas do banco (FR-5710) ---------------------------------------------------


@postgresql
def test_as_tres_tabelas_recusam_alteracao_e_exclusao_no_banco(fixtures, gestor):
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-ao")
    chamar(cenario, gestor, "p148-ao")
    publicar(edital, gestor, chave="p148-ao-pub")
    for tabela in (
        "convocacao_publicacaodeconvocados",
        "convocacao_convocacaopublicada",
        "convocacao_documentodapublicacaodeconvocados",
    ):
        for comando in (f"UPDATE {tabela} SET id = id", f"DELETE FROM {tabela}"):
            with pytest.raises(Exception, match="append-only"), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(comando)


@postgresql
def test_o_gatilho_recusa_vinculo_com_comunicacao_que_nao_saiu(fixtures, gestor):
    """O que `CHECK` não alcança: a comunicação citada precisa ser a bem-sucedida da convocação."""
    edital, _, _ = cenario = certame(fixtures, prefixo="p148-coer")
    _, convocacao = chamar(cenario, gestor, "p148-coer")
    publicar(edital, gestor, chave="p148-coer-pub")
    vinculo = ConvocacaoPublicada.objects.get(convocacao=convocacao)
    outra = PublicacaoDeConvocados.objects.create(
        **{
            campo.attname: getattr(vinculo.publicacao, campo.attname)
            for campo in PublicacaoDeConvocados._meta.concrete_fields
            if campo.attname != "id"
        }
        | {"numero": 2}
    )
    falha = ComunicacaoEmitida.objects.create(
        convocacao=convocacao, forma=FORMA_POR_PUBLICACAO, resultado="FALHA"
    )

    with pytest.raises(Exception, match="did not succeed"), transaction.atomic():
        ConvocacaoPublicada.objects.create(
            publicacao=outra, convocacao=convocacao, comunicacao=falha, efeito="DIVULGA"
        )


def _conteudo(ato):
    import json

    return json.loads(bytes(ato.conteudo_publico).decode("utf-8"))


# --- Uma publicação, duas listas da mesma vaga (SC-1855) ------------------------------------------


def test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada(fixtures, gestor):
    """A ampla e a reserva PPI da mesma vaga, com ordem, corte e apuração próprios (034, 016)."""
    from processo_seletivo.classificacao.application.corte import calcular_corte
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta as assinatura_do_corte,
    )
    from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
    from tests.fixtures.convocacao import apurar
    from tests.fixtures.ocupacao import MODALIDADE_PPI
    from tests.fixtures.recortes import emitir_recorte

    edital, _, _ = cenario = certame(
        fixtures, prefixo="p148-listas", ppi=1, modalidades={2: MODALIDADE_PPI}
    )
    _, ampla = chamar(cenario, gestor, "p148-l-ampla")
    with CaptureQueriesContext(connection) as com_um_recorte:
        previa(edital)
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="p148-l-ordem-ppi")
    proposta = calcular_corte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=MODALIDADE_PPI
    )
    emitir_corte(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=MODALIDADE_PPI,
        idempotency_key="p148-l-corte-ppi",
        correlation_id="teste-148",
        confirmacao_do_calculo=assinatura_do_corte(proposta),
    )
    apurar(edital, gestor, chave="p148-l-apura-ppi", lista_id=MODALIDADE_PPI)
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=MODALIDADE_PPI
    )["fila"]
    reservada = Convocacao.objects.get(
        id=convocar(
            edital,
            gestor,
            fila[0],
            lista_id=MODALIDADE_PPI,
            idempotency_key="p148-l-ppi",
            vencimento=timezone.now() + CINCO_DIAS,
        )["id"]
    )

    with CaptureQueriesContext(connection) as com_dois_recortes:
        lida = previa(edital)
    declarado = publicar(edital, gestor, chave="p148-l-pub")

    # SC-1865, metade da gestão: a prévia lê o Edital em consultas fixas (FR-5736).
    assert len(com_dois_recortes) == len(com_um_recorte)

    assert [grupo["lista"] for grupo in lida["grupos"]] == [
        "Ampla concorrência",
        "Pretos, pardos e indígenas",
    ]
    assert len(lida["recortes"]) == 2
    ato = PublicacaoDeConvocados.objects.get(id=declarado["id"])
    assert {v.convocacao_id for v in ato.convocacoes_publicadas.all()} == {ampla.id, reservada.id}
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    documento = texto_de_pdf_bytes(bytes(ato.documento.bytes))
    assert "Ampla concorrência" in documento and "Pretos, pardos e indígenas" in documento


# --- O aviso aos convocados de uma chamada publicada alcança a nativa (FR-5735) -------------------


def test_o_aviso_da_chamada_publicada_alcanca_a_publicacao_nativa(fixtures, gestor):
    from processo_seletivo.avisos.models import Aviso
    from tests.fixtures.avisos import avisar_chamada

    edital, _, _ = cenario = certame(fixtures, prefixo="p148-aviso")
    _, convocacao = chamar(cenario, gestor, "p148-aviso")
    publicar(edital, gestor, chave="p148-aviso-pub")
    emitida = ComunicacaoEmitida.objects.get(convocacao=convocacao)

    declarado = avisar_chamada(edital, MARCO, emitida.id, ator=gestor, agora=timezone.now())

    aviso = Aviso.objects.get(pk=declarado["aviso"])
    assert aviso.referencia_da_publicacao == emitida.referencia_da_publicacao
    assert "1ª publicação de convocados" in aviso.corpo
    assert declarado["destinatarios"] == 1


# --- No mesmo gesto, a ordem da fila (FR-5714, revista em 12/11/2026) ----------------------------


def test_no_mesmo_gesto_a_relacao_segue_a_classificacao(fixtures, gestor, caixa_de_saida):
    """O defeito da demonstração do C10: as três do gesto saíam pela ordem do identificador interno.

    As convocadas num gesto nascem no mesmo instante; sem a posição, o desempate era o UUID. Com
    dois titulares, metade das montagens já sai na ordem certa por acaso — e por isso o caso confere
    contra a classificação, e não contra uma ordem fixa.
    """
    from processo_seletivo.classificacao.models import PosicaoNaOrdem
    from tests.fixtures.corte import regra
    from tests.integration.convocacao.test_lista_da_chamada_no_gesto import convocar_titulares

    edital, _, _ = certame(
        fixtures,
        forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
        prefixo="p149-ordem",
        geral=2,
        cut=regra(surplusCount=1),
    )
    praticadas = [
        Convocacao.objects.get(id=c["id"])
        for c in convocar_titulares(edital, gestor, chave="p149-ordem-gesto")["convocadas"]
    ]
    assert len({c.criado_em for c in praticadas}) == 1, "a premissa: o mesmo instante"
    posicao = {
        p.inscricao_id: p.posicao
        for p in PosicaoNaOrdem.objects.filter(ato_id=praticadas[0].ato_de_ordenacao_id)
    }
    esperada = [
        c.inscricao.protocolo for c in sorted(praticadas, key=lambda c: posicao[c.inscricao_id])
    ]

    [grupo] = previa(edital)["grupos"]

    assert [p["protocolo"] for p in grupo["pessoas"]] == esperada
