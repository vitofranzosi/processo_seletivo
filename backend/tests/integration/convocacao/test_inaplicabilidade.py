"""A inaplicabilidade documental com fundamento publicado, pelos serviços (131).

O cenário é o 72/2026 em miniatura, com dois titulares convocados num gesto só. Uma das inscrições
declara PPI, e a convocação pede:

- a certidão e o histórico, incondicionais (figura B);
- o certificado de alistamento militar, com a condição publicada (figura C);
- a autodeclaração étnico-racial, por recorte à modalidade PPI e sem condição — obrigatória para
  quem a declarou e excluída pelo recorte para a outra (figuras B e A).

O que se prova, na numeração dos cenários de `contracts/cenarios.md`:

- 1, 10: o incondicional não se afasta, por ninguém;
- 2, 8: o condicional se afasta, pelo alocado, com o fato;
- 5, 6: o motivo ausente ou sem palavra é recusado;
- 7: com arquivo, o "não se aplica" pede a abertura, e depois tranca o envio;
- 11: o item fora do recorte não existe para a conferência;
- 12: a correção da convocação herda condição e conferência;
- a substituição que envolve o "não se aplica" pede motivo, haja ou não arquivo.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application import documentos as servico
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ConferenciaDeDocumento, Convocacao
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    HISTORICO,
    abrir,
    apresentar,
    conferir,
    item,
    lido,
)
from tests.fixtures.edital import PROFILE_ID, identificador
from tests.fixtures.ocupacao import MODALIDADE_PPI

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

ALISTAMENTO = identificador(1311, 1)
AUTODECLARACAO = identificador(1311, 2)
CONDICAO = "no caso de candidatos do sexo masculino, maiores de 18 anos"
FATO = "Candidata do sexo feminino, conforme o documento de identidade."
VENCIMENTO = timezone.now() + timedelta(days=3)


def _documentos():
    return [
        *cenarios.documentos_do_aluno()[:3],
        {
            "id": ALISTAMENTO,
            "key": "alistamento",
            "name": "Certificado de alistamento militar ou de reservista",
            "instructions": "",
            "required": True,
            "order": 4,
            "moment": "AT_CALL",
            "requiredWhen": CONDICAO,
        },
        {
            "id": AUTODECLARACAO,
            "key": "autodeclaracao-ppi",
            "name": "Autodeclaração étnico-racial",
            "instructions": "",
            "required": True,
            "order": 5,
            "moment": "AT_CALL",
            "modalityId": MODALIDADE_PPI,
        },
    ]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    edital, _, inscricoes = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=_documentos(),
        prefixo="inaplicabilidade-131",
        geral=2,
        cut=regra(surplusCount=1),
        ppi=0,
        modalidades={0: MODALIDADE_PPI},
    )
    assinatura = fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
        "assinatura"
    ]
    praticadas = fluxo.convocar_titulares(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=assinatura,
        idempotency_key="titulares-131",
        vencimento=VENCIMENTO,
    )
    por_inscricao = {
        c.inscricao_id: c
        for c in Convocacao.objects.filter(
            id__in=[linha["id"] for linha in praticadas["convocadas"]]
        )
    }
    ppi = por_inscricao[inscricoes[0].id]
    ampla = next(c for i, c in por_inscricao.items() if i != inscricoes[0].id)
    return {
        "edital": edital,
        "ppi": ppi,
        "ampla": ampla,
        "pessoa_ppi": inscricoes[0],
        "pessoa_ampla": next(i for i in inscricoes if i.id == ampla.inscricao_id),
    }


@pytest.fixture
def alocado(cenario, gestor):
    """O membro `joao`, só alocado à conferência deste Edital: sem papel nenhum de gestão."""
    from processo_seletivo.comissoes.application.alocacao import alocar_a_conferencia
    from processo_seletivo.comissoes.models import MembroComissao

    edital = cenario["edital"]
    membro = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar_a_conferencia(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        idempotency_key="alocar-131",
        correlation_id="teste-131",
    )
    return Actor("joao", gestor.institution_scope, frozenset())


def _recusa(funcao):
    with pytest.raises(DomainError) as recusa:
        funcao()
    return recusa.value


def _conferencias(convocacao, requisito):
    return ConferenciaDeDocumento.objects.filter(item=item(convocacao, requisito)).count()


# --- 1 e 10: o incondicional não se afasta ----------------------------------------------------


@pytest.mark.parametrize("requisito", [CERTIDAO, HISTORICO, AUTODECLARACAO])
def test_incondicional_nao_se_afasta(cenario, alocado, gestor, requisito):
    """Nem pelo alocado nem por quem gere a comissão: não há quem dispense (2ª decisão)."""
    convocacao = cenario["ppi"]
    for ator, chave in ((alocado, "a"), (gestor, "g")):
        recusa = _recusa(
            lambda ator=ator, chave=chave: conferir(
                ator,
                convocacao,
                requisito,
                "NAO_SE_APLICA",
                chave=f"{chave}-{requisito}",
                motivo=FATO,
            )
        )
        assert recusa.code == nomes.NAO_SE_APLICA_SEM_CONDICAO
    assert _conferencias(convocacao, requisito) == 0


def test_tres_incondicionais_afastados_nao_chegam_ao_aceite(cenario, alocado):
    """O cenário do estudo de 07/11, que o aceite deixava passar: agora nem se registra."""
    convocacao = cenario["ppi"]
    for requisito in (CERTIDAO, HISTORICO, AUTODECLARACAO):
        _recusa(
            lambda requisito=requisito: conferir(
                alocado,
                convocacao,
                requisito,
                "NAO_SE_APLICA",
                chave=f"t-{requisito}",
                motivo="Dispensado.",
            )
        )

    pendentes = {
        lido.nome for lido in servico.leitura_da_chamada(convocacao).pendencias_para_incluir
    }
    assert {"Autodeclaração étnico-racial", "Histórico escolar do ensino médio"} <= pendentes


# --- 2 e 8: o condicional, pelo alocado -------------------------------------------------------


def test_o_alocado_registra_o_nao_se_aplica_no_condicional(cenario, alocado):
    convocacao = cenario["ppi"]

    conferencia = conferir(
        alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="ok", motivo=FATO
    )

    assert conferencia.conferido_por == "joao"
    assert conferencia.motivo == FATO
    assert conferencia.apresentacao_id is None
    item_lido = lido(convocacao, ALISTAMENTO)
    assert item_lido.estado == nomes.ITEM_NAO_SE_APLICA
    assert item_lido.condicao == CONDICAO
    assert item_lido not in servico.leitura_da_chamada(convocacao).pendencias_para_incluir


# --- 5 e 6: o motivo ----------------------------------------------------------------------------


def test_nao_se_aplica_sem_motivo_e_recusado(cenario, alocado):
    recusa = _recusa(
        lambda: conferir(alocado, cenario["ppi"], ALISTAMENTO, "NAO_SE_APLICA", chave="sem")
    )
    assert recusa.code == nomes.MOTIVO_DA_CONFERENCIA_OBRIGATORIO


@pytest.mark.parametrize("motivo", [".", "-", "...", " . ", "—", "?!"])
@pytest.mark.parametrize("resultado", ["NAO_SE_APLICA", "PENDENTE"])
def test_motivo_sem_palavra_e_recusado(cenario, alocado, motivo, resultado):
    convocacao = cenario["ppi"]

    recusa = _recusa(
        lambda: conferir(
            alocado, convocacao, ALISTAMENTO, resultado, chave=f"{resultado}{motivo}", motivo=motivo
        )
    )

    assert recusa.code == nomes.MOTIVO_SEM_CONTEUDO
    assert _conferencias(convocacao, ALISTAMENTO) == 0


# --- 7: com arquivo -------------------------------------------------------------------------------


def test_com_arquivo_o_nao_se_aplica_pede_a_abertura_e_depois_tranca(cenario, alocado):
    convocacao, pessoa = cenario["ppi"], cenario["pessoa_ppi"]
    enviada = apresentar(pessoa, convocacao, ALISTAMENTO, corpo=b"reservista").apresentacao

    recusa = _recusa(
        lambda: conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="x", motivo=FATO)
    )
    assert recusa.code == nomes.NAO_SE_APLICA_SEM_ABERTURA

    abrir(alocado, enviada)
    conferencia = conferir(
        alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="y", motivo=FATO
    )
    assert conferencia.apresentacao_id == enviada.id
    assert conferencia.hash_conferido == enviada.content_hash

    trancado = _recusa(lambda: apresentar(pessoa, convocacao, ALISTAMENTO, corpo=b"outro"))
    assert trancado.code == nomes.DOCUMENTO_JA_CONFERIDO


# --- a substituição -------------------------------------------------------------------------------


def test_trocar_para_nao_se_aplica_sem_arquivo_pede_motivo(cenario, alocado):
    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, ALISTAMENTO, "PENDENTE", chave="p", motivo="Falta o arquivo.")

    recusa = _recusa(
        lambda: conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)
    )
    assert recusa.code == nomes.MOTIVO_DA_SUBSTITUICAO_OBRIGATORIO

    conferir(
        alocado,
        convocacao,
        ALISTAMENTO,
        "NAO_SE_APLICA",
        chave="n2",
        motivo=FATO,
        motivo_da_substituicao="A candidata apresentou a identidade na conferência.",
    )
    assert lido(convocacao, ALISTAMENTO).estado == nomes.ITEM_NAO_SE_APLICA


def test_sair_do_nao_se_aplica_tambem_pede_motivo(cenario, alocado):
    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)

    recusa = _recusa(
        lambda: conferir(alocado, convocacao, ALISTAMENTO, "PENDENTE", chave="p", motivo="Envie.")
    )
    assert recusa.code == nomes.MOTIVO_DA_SUBSTITUICAO_OBRIGATORIO


def test_a_pendencia_sem_arquivo_continua_sem_motivo_de_revisao(cenario, alocado):
    """A liberdade que a `115` prende para a pendência não muda: só o "não se aplica" pede."""
    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, CERTIDAO, "PENDENTE", chave="p1", motivo="Falta a certidão.")

    conferir(alocado, convocacao, CERTIDAO, "PENDENTE", chave="p2", motivo="Ainda falta.")

    assert lido(convocacao, CERTIDAO).estado == nomes.ITEM_PENDENTE


# --- 11: fora do recorte --------------------------------------------------------------------------


@pytest.mark.parametrize("resultado", ["CONFORME", "PENDENTE", "NAO_SE_APLICA"])
def test_item_fora_do_recorte_nao_se_confere(cenario, gestor, resultado):
    convocacao = cenario["ampla"]
    assert item(convocacao, AUTODECLARACAO).situacao == "NAO_SE_APLICA"

    recusa = _recusa(
        lambda: conferir(
            gestor, convocacao, AUTODECLARACAO, resultado, chave=f"fora-{resultado}", motivo=FATO
        )
    )

    assert recusa.status == 404
    assert _conferencias(convocacao, AUTODECLARACAO) == 0


# --- 12: a correção da convocação ----------------------------------------------------------------


def test_a_correcao_herda_condicao_e_conferencia(cenario, gestor, alocado):
    """A sucessora usa a lista e as conferências da chamada (FR-3573 da `115`)."""
    from tests.fixtures.convocacao import convocar

    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)

    declarado = convocar(
        cenario["edital"],
        gestor,
        convocacao.inscricao_id,
        idempotency_key="corrigir-131",
        motivo="Vencimento corrigido.",
        vencimento=VENCIMENTO + timedelta(days=2),
    )
    sucessora = Convocacao.objects.get(id=declarado["id"])

    herdado = lido(sucessora, ALISTAMENTO)
    assert herdado.estado == nomes.ITEM_NAO_SE_APLICA
    assert herdado.condicao == CONDICAO


def test_a_condicao_se_le_da_versao_da_lista(cenario):
    """FR-4456: o requisito é o da versão que o item cita, e não o da vigente."""
    alvo = item(cenario["ppi"], ALISTAMENTO)

    assert servico.requisito_do_item(alvo)["requiredWhen"] == CONDICAO
    assert alvo.versao_id == cenario["ppi"].versao_id


# --- 9: o aceite com ciência ----------------------------------------------------------------------


def _pronta_com_um_nao_se_aplica(cenario, alocado):
    """A pessoa PPI com os incondicionais conformes e o alistamento afastado pelo alocado."""
    convocacao, pessoa = cenario["ppi"], cenario["pessoa_ppi"]
    for requisito in (CERTIDAO, HISTORICO, AUTODECLARACAO):
        apresentar(pessoa, convocacao, requisito, corpo=f"arquivo {requisito}".encode())
        conferir(alocado, convocacao, requisito, "CONFORME", chave=f"c-{requisito}")
    afastada = conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)
    return convocacao, afastada


def _aceite(cenario, gestor, convocacao, *, chave, ciencia=None, especie="ACEITE"):
    from processo_seletivo.convocacao.application.desfechar import desfechar

    return desfechar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        convocacao_id=convocacao.id,
        especie=especie,
        fundamento="Apto para formalização.",
        idempotency_key=chave,
        correlation_id="teste-131",
        ciencia=ciencia,
    )


def _assinatura(convocacao):
    return servico.leitura_da_chamada(convocacao).assinatura_das_inaplicabilidades


def test_a_leitura_separa_conformes_e_nao_se_aplica(cenario, alocado):
    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)

    leitura = servico.leitura_da_chamada(convocacao)

    assert leitura.estado == nomes.DOCUMENTOS_PRONTA
    assert leitura.contagens["conformes"] == 3
    assert leitura.contagens["nao_se_aplica"] == 1
    assert [lido.nome for lido in leitura.inaplicabilidades] == [
        "Certificado de alistamento militar ou de reservista"
    ]


def test_aceite_sem_ciencia(cenario, alocado, gestor):
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao

    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)

    for ciencia in (None, {"assinatura": _assinatura(convocacao), "marcada": False}):
        recusa = _recusa(
            lambda ciencia=ciencia: _aceite(cenario, gestor, convocacao, chave="s", ciencia=ciencia)
        )
        assert recusa.code == nomes.CIENCIA_DAS_INAPLICABILIDADES
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()


def test_aceite_com_ciencia_superada(cenario, alocado, gestor):
    """O conjunto mudou entre a tela e o clique: a ciência não vale para o que não se viu."""
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao

    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)
    vista = _assinatura(convocacao)
    conferir(
        alocado,
        convocacao,
        ALISTAMENTO,
        "NAO_SE_APLICA",
        chave="n-de-novo",
        motivo="Candidata do sexo feminino, conforme a certidão.",
        motivo_da_substituicao="Corrigido o documento citado.",
    )

    recusa = _recusa(
        lambda: _aceite(
            cenario, gestor, convocacao, chave="v", ciencia={"assinatura": vista, "marcada": True}
        )
    )

    assert recusa.code == nomes.INAPLICABILIDADES_MUDARAM
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()


def test_aceite_com_ciencia(cenario, alocado, gestor):
    from processo_seletivo.auditoria.models import RegistroAuditoria
    from processo_seletivo.convocacao.application.desfechar import DESFECHAR

    convocacao, afastada = _pronta_com_um_nao_se_aplica(cenario, alocado)

    declarado = _aceite(
        cenario,
        gestor,
        convocacao,
        chave="ok",
        ciencia={"assinatura": _assinatura(convocacao), "marcada": True},
    )

    assert declarado["especie"] == "ACEITE"
    trilha = RegistroAuditoria.objects.get(operation=DESFECHAR, aggregate_id=declarado["id"])
    assert str(afastada.id) in trilha.reason
    assert FATO not in trilha.reason


def test_indeferimento_sem_ciencia(cenario, alocado, gestor):
    """Os desfechos que não incluem não leem o estado documental (FR-3593 da `115`)."""
    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)

    declarado = _aceite(cenario, gestor, convocacao, chave="i", especie="INDEFERIMENTO")

    assert declarado["especie"] == "INDEFERIMENTO"


def test_sem_inaplicabilidade_o_aceite_e_o_de_antes(cenario, alocado, gestor):
    convocacao, pessoa = cenario["ppi"], cenario["pessoa_ppi"]
    for requisito in (CERTIDAO, HISTORICO, AUTODECLARACAO, ALISTAMENTO):
        apresentar(pessoa, convocacao, requisito, corpo=f"arquivo {requisito}".encode())
        conferir(alocado, convocacao, requisito, "CONFORME", chave=f"c-{requisito}")

    assert _aceite(cenario, gestor, convocacao, chave="a")["especie"] == "ACEITE"


# --- a 11ª decisão: o "não se aplica" antigo, sem condição publicada -------------------------


def _nao_se_aplica_antigo(convocacao, requisito):
    """A linha que a `115` deixava gravar num incondicional, posta direto no banco, como estava."""
    alvo = item(convocacao, requisito)
    return ConferenciaDeDocumento.objects.create(
        item=alvo,
        resultado="NAO_SE_APLICA",
        motivo="Dispensado.",
        conferido_por="joao",
        unidade_de_atuacao="cefor",
        conferido_em=timezone.now(),
    )


def test_p1_chamada_aberta_o_antigo_nao_atende(cenario, alocado, gestor):
    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)
    gravada = ConferenciaDeDocumento.objects.filter(item=item(convocacao, CERTIDAO)).count()
    _nao_se_aplica_antigo(convocacao, CERTIDAO)

    lido_antigo = lido(convocacao, CERTIDAO)
    assert lido_antigo.sem_condicao_publicada
    assert servico.leitura_da_chamada(convocacao).estado == nomes.DOCUMENTOS_COM_PENDENCIA
    recusa = _recusa(
        lambda: _aceite(
            cenario,
            gestor,
            convocacao,
            chave="p1",
            ciencia={"assinatura": _assinatura(convocacao), "marcada": True},
        )
    )
    assert recusa.code == nomes.DOCUMENTOS_NAO_CONFERIDOS
    assert "registrado sem condição publicada" in recusa.detail
    # O registro antigo continua gravado e legível: nada se reescreve (FR-4476).
    assert (
        ConferenciaDeDocumento.objects.filter(item=item(convocacao, CERTIDAO)).count()
        == gravada + 1
    )


def test_p1_chamada_decidida_continua(cenario, alocado, gestor):
    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)
    _aceite(
        cenario,
        gestor,
        convocacao,
        chave="a",
        ciencia={"assinatura": _assinatura(convocacao), "marcada": True},
    )
    _nao_se_aplica_antigo(convocacao, CERTIDAO)

    leitura = servico.leitura_da_chamada(convocacao, decidida=True)

    assert leitura.estado == nomes.DOCUMENTOS_DECIDIDA
    assert lido(convocacao, CERTIDAO).sem_condicao_publicada


# --- as telas: a página dos documentos, a condução e o POST do desfecho ------------------------


@pytest.fixture
def na_gestao(client, settings):
    """O cliente identificado como quem gere a comissão, pelo seletor da demonstração."""
    from django.urls import reverse

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    resposta = client.post(
        reverse("interface:identificar"), {"subject": "carlos", "papeis": ["gestor"]}
    )
    assert resposta.status_code == 302
    return client


def _rotas(cenario, convocacao):
    from django.urls import reverse

    edital = cenario["edital"]
    return {
        "pagina": reverse(
            "interface:documentos-da-convocacao", args=[edital.id, MARCO, convocacao.id]
        ),
        "conducao": reverse("interface:convocacao", args=[edital.id, MARCO]),
        "desfecho": reverse("interface:desfechar", args=[edital.id, MARCO, convocacao.id]),
    }


def test_a_pagina_so_oferece_o_nao_se_aplica_no_condicional(cenario, na_gestao):
    corpo = na_gestao.get(_rotas(cenario, cenario["ppi"])["pagina"]).content.decode()

    assert corpo.count('value="NAO_SE_APLICA"') == 1
    assert f"Condição publicada: {CONDICAO}." in corpo
    assert "que fato da pessoa a põe fora da condição?" in corpo


def test_a_conducao_separa_as_contagens_e_mostra_o_bloco(cenario, alocado, na_gestao):
    convocacao, afastada = _pronta_com_um_nao_se_aplica(cenario, alocado)

    corpo = na_gestao.get(_rotas(cenario, convocacao)["conducao"]).content.decode()

    assert "3 de 4 conformes · 1 não se aplica após análise" in corpo
    assert "Documentos obrigatórios considerados não aplicáveis" in corpo
    assert f"condição publicada: {CONDICAO}. Motivo: {FATO}" in corpo
    assert f'name="inaplicabilidades" value="{_assinatura(convocacao)}"' in corpo
    assert 'name="ciencia_das_inaplicabilidades"' in corpo


def _desfechar_pela_tela(cliente, rota, campos):
    """O POST do desfecho, pelos dois passos da conferência do texto da `125`."""
    from processo_seletivo.interface.conferencia_do_texto import CHAVE

    cliente.post(rota, campos)
    resumo = cliente.session[CHAVE]["resumo"]
    return cliente.post(rota, {**campos, "etapa": "confirmar", "texto_conferido": resumo})


def test_o_post_do_desfecho_leva_a_ciencia(cenario, alocado, na_gestao):
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao

    convocacao, _ = _pronta_com_um_nao_se_aplica(cenario, alocado)
    rota = _rotas(cenario, convocacao)["desfecho"]
    campos = {
        "especie": "ACEITE",
        "fundamento": "Apto para formalização.",
        "inaplicabilidades": _assinatura(convocacao),
        "chave": "sem-ciencia",
    }

    _desfechar_pela_tela(na_gestao, rota, campos)
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()

    _desfechar_pela_tela(
        na_gestao, rota, {**campos, "chave": "com-ciencia", "ciencia_das_inaplicabilidades": "1"}
    )
    assert DesfechoDaConvocacao.objects.get(convocacao=convocacao).especie == "ACEITE"
