"""A confirmação de "Encerrar Processo" adverte o que está em aberto nos Editais (130).

A tela é lida como o gestor a lê: o bloco antes das consequências, as frases da `113` e da `099`
Edital a Edital, nenhuma pessoa nomeada; e, se a lista mudou entre abrir e confirmar, a confirmação
volta com a lista de agora, sem encerrar (FR-4365). Nada disso impede o encerramento.

Os cenários são os do relatório (`tests/fixtures/relatorio`), com o relógio posto em `REFERENCIA`:
o final `pendente` é o Edital encerrado com a reservada aguardando resposta até 30/10/2026.
"""

import re
from unittest import mock

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import encerramento
from processo_seletivo.interface.relatorio_do_edital import (
    fatos_do_edital,
    leitura_consistente,
    texto_da_pendencia,
)
from processo_seletivo.processos.application import pendencias_do_edital as p
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.encerramento import encerrar_antes_da_113
from tests.fixtures.recursos_us4 import cenario_julgavel
from tests.fixtures.relatorio import REFERENCIA, dia, em, montar_cenario
from tests.interface.test_auditoria_passagem_da_retificacao import sessao

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("seletor_ligado")]

TITULO = "Em aberto nos Editais deste Processo"
ABERTURA = (
    "Encerrar o Processo não conclui estas providências, e os Editais dele deixam de aceitar "
    "alteração."
)
CONVOCADO = (
    "Quem foi convocado e ainda está no prazo não poderá mais apresentar documento nem enviar o "
    "Requerimento de Matrícula."
)
NADA = (
    "Nenhuma providência em aberto registrada no GPS nos Editais deste Processo. O GPS não sabe se "
    "ainda haverá convocação do cadastro de reserva: a validade dele está no texto do Edital."
)
RENOVADA = (
    "As providências em aberto mudaram desde que você abriu esta tela. Confira a lista atual e "
    "confirme de novo."
)
CONFIRMAR = "Confirmar: Encerrar Processo"


def url_do_ato(processo, acao="encerrar"):
    return reverse("interface:processo-ato", args=[processo.id, acao])


def abrir(cliente, processo, acao="encerrar"):
    resposta = cliente.get(url_do_ato(processo, acao))
    assert resposta.status_code == 200
    return resposta


def enviar(cliente, processo, aberta, motivo="Certame concluído", **extra):
    dados = {"chave_idempotencia": aberta.context["chave_idempotencia"], "motivo": motivo}
    advertencia = aberta.context.get("advertencia")
    if advertencia is not None:
        dados["resumo_das_providencias"] = advertencia.resumo
    dados.update(extra)
    return cliente.post(url_do_ato(processo), dados)


def texto(resposta):
    return resposta.content.decode()


def visivel(resposta):
    """O texto que se lê, sem atributos: um UUID num `href` não é vazamento de protocolo."""
    return " ".join(re.sub(r"<[^>]+>", " ", texto(resposta)).split())


def gestor():
    return sessao("gabi.gestora", ["gestor"])


def mensagens(advertencia):
    return {str(g.edital.id): [i.mensagem for i in g.itens] for g in advertencia.grupos}


def atos_do_processo(processo):
    return AtoAdministrativo.objects.filter(aggregate_id=processo.id).count()


@pytest.fixture
def pendente():
    return montar_cenario(final="pendente")


# ---------------------------------------------------------------------------------------------
# História 1 — o convocado que o encerramento vai cortar (FR-4350, FR-4363, UX-275, UX-276)
# ---------------------------------------------------------------------------------------------


def test_o_bloco_mostra_a_convocacao_no_prazo_antes_das_consequencias(pendente):
    with em(REFERENCIA):
        corpo = texto(abrir(gestor(), pendente.processo))

    edital = pendente.edital
    assert TITULO in corpo
    assert ABERTURA in corpo
    assert CONVOCADO in corpo
    assert f"{edital.number}/{edital.year}</a>" in corpo
    assert reverse("interface:detalhe", args=[edital.id]) in corpo
    assert "1 convocação aguardando resposta, até 30/10/2026." in corpo
    assert corpo.index(TITULO) < corpo.index(CONVOCADO) < corpo.index("1 convocação aguardando")
    assert corpo.index("1 convocação aguardando") < corpo.index("Este ato não pode ser desfeito")
    assert 'name="resumo_das_providencias"' in corpo
    assert CONFIRMAR in corpo


def test_confirmar_com_a_lista_vista_encerra_e_grava_so_o_ato_de_hoje(pendente):
    processo = pendente.processo
    antes = atos_do_processo(processo)
    with em(REFERENCIA):
        cliente = gestor()
        resposta = enviar(cliente, processo, abrir(cliente, processo))

    assert resposta.status_code == 302
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ENCERRADO
    assert atos_do_processo(processo) == antes + 1
    ato = AtoAdministrativo.objects.filter(aggregate_id=processo.id).latest("occurred_at")
    assert ato.reason == "Certame concluído"


def test_nenhum_dado_pessoal_na_confirmacao(pendente):
    """SC-1323: nome, CPF, e-mail e protocolo de cada inscrição, no texto que se lê."""
    with em(REFERENCIA):
        lido = visivel(abrir(gestor(), pendente.processo))
    inscricoes = Inscricao.objects.filter(edital=pendente.edital)
    assert inscricoes.exists()
    for inscricao in inscricoes:
        for dado in (inscricao.nome, inscricao.cpf_normalizado, inscricao.email):
            if dado:
                assert dado not in lido
        if inscricao.protocolo:
            assert not re.search(rf"\b{re.escape(inscricao.protocolo)}\b", lido)


# ---------------------------------------------------------------------------------------------
# História 2 — os tipos da 113 e da 099, por Edital (FR-4351 a FR-4358, SC-1321)
# ---------------------------------------------------------------------------------------------


def _esperadas(edital, agora):
    """As frases que a 113 e a 099 dizem deste Edital, redigidas por elas, e não pela composição.

    As da `099` vêm da redação do relatório (`texto_da_pendencia`, com a maiúscula e o ponto que a
    confirmação do Edital acrescenta); as da `113`, de `pendencias_do_edital.frase`. Se a composição
    redigisse por conta própria, ou filtrasse diferente, a comparação acusaria.
    """
    with leitura_consistente():
        situacoes = p.situacoes(edital, agora=agora, ato="encerrar", com_advertencias=True)
        relatorio = fatos_do_edital(edital, agora=agora).pendencias
    da_113 = {
        p.frase(s, "encerrar") + "." for s in situacoes if s.tipo in encerramento.TIPOS_NO_PROCESSO
    }
    da_099 = set()
    for pendencia in relatorio:
        if pendencia.tipo in encerramento.DA_099:
            frase = texto_da_pendencia(pendencia)
            da_099.add(frase[:1].upper() + frase[1:] + ".")
    return da_113 | da_099


GESTORA = Actor("gabi.gestora", "cefor", frozenset({"processo:encerrar"}))


def test_as_frases_sao_as_da_confirmacao_do_edital_e_do_relatorio(pendente):
    edital = pendente.edital
    with leitura_consistente():
        advertencia = encerramento.do_processo(pendente.processo, GESTORA, agora=REFERENCIA)
        relatorio = fatos_do_edital(edital, agora=REFERENCIA).pendencias

    do_relatorio = [x for x in relatorio if x.tipo in encerramento.DA_099]
    assert do_relatorio, "o cenário precisa de providência do relatório para a prova não ser vazia"
    lidas = mensagens(advertencia)[str(edital.id)]
    assert len(lidas) == len(set(lidas)), "cada providência uma vez só"
    assert set(lidas) == _esperadas(edital, REFERENCIA)
    assert "1 convocação aguardando resposta, até 30/10/2026." in lidas


def _edital_cancelado_antes_de_publicar(processo):
    from processo_seletivo.processos.application.commands import add_edital
    from processo_seletivo.processos.application.finalizacao import cancel_edital

    criado, _ = add_edital(
        actor=Actor("gabi.gestora", "cefor", frozenset({"edital:criar"})),
        processo_id=processo.id,
        data={"number": "64", "year": 2026, "title": "Nunca publicado", "description": "-"},
        idempotency_key="add-130-64",
        correlation_id="teste-130",
    )
    cancel_edital(
        actor=Actor("gabi.gestora", "cefor", frozenset({"edital:cancelar"})),
        edital_id=criado.id,
        expected_revision=criado.revision,
        reason="Não será publicado",
        idempotency_key="cancelar-130-64",
        correlation_id="teste-130",
    )
    return criado


def test_os_editais_em_ordem_sem_o_nunca_publicado_e_sem_os_que_nada_tem():
    """Cinco Editais finais e um cancelado antes de publicar, no mesmo Processo.

    O Processo de cada cenário é um só por construção; os outros Editais são postos no do 61 por
    `update`, como `encerrar_o_processo` faz com o estado: o que se prende é a composição, e não o
    caminho até ela. O 62 está encerrado sem pendência; o 63 foi cancelado antes do resultado e da
    convocação, e por isso nada tem em aberto; 61, 65 e 66 têm a reservada no prazo.
    """
    c61 = montar_cenario(final="pendente")
    outros = {
        "62": montar_cenario(final="sem-pendencia", numero="62", publicado_em=dia(10, 2, 9)),
        "63": montar_cenario(final="cancelado", numero="63", maximo=4),
        "65": montar_cenario(final="pendente", numero="65"),
        "66": montar_cenario(final="pendente", numero="66"),
    }
    processo = c61.processo
    Edital.objects.filter(pk__in=[c.edital.id for c in outros.values()]).update(processo=processo)
    nunca = _edital_cancelado_antes_de_publicar(processo)

    with leitura_consistente():
        advertencia = encerramento.do_processo(processo, GESTORA, agora=REFERENCIA)

    ids = [str(g.edital.id) for g in advertencia.grupos]
    esperados = [str(c61.edital.id), str(outros["65"].edital.id), str(outros["66"].edital.id)]
    assert ids == esperados, "sem o nunca publicado, sem os que nada têm, por ano e número"
    assert str(nunca.id) not in ids
    assert _esperadas(outros["63"].edital, REFERENCIA) == set()
    for grupo in advertencia.grupos:
        assert {i.mensagem for i in grupo.itens} == _esperadas(grupo.edital, REFERENCIA)

    with em(REFERENCIA):
        corpo = texto(abrir(gestor(), processo))
    assert corpo.count('<ul class="impedimentos">') == 3, "um grupo por Edital, sem truncar"
    assert "Continuam depois do encerramento" not in corpo  # UX-278


def test_periodo_e_retificacao_nao_aparecem(api_client, manager_headers, process_payload):
    """D-002: num Edital encerrado com uma Retificação em revisão, a regra da `113` a produz, e
    ela não chega ao Processo. O período fica fora pelo conjunto (teste unitário)."""
    from processo_seletivo.processos.application.finalizacao import close_edital
    from processo_seletivo.publicacoes.models_retificacao import Retificacao
    from tests.fixtures.publicacao import publish_original
    from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import levar_a
    from tests.unit.processos.test_pendencias_do_edital import criar

    edital = publish_original(api_client, manager_headers, process_payload)
    levar_a(criar(api_client, edital), Retificacao.Status.EM_REVISAO)
    edital.refresh_from_db()
    close_edital(
        actor=Actor("gabi.gestora", "cefor", frozenset({"edital:encerrar"})),
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Etapas concluídas",
        idempotency_key="encerrar-130-d002",
        correlation_id="teste-130",
    )
    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO

    from django.utils import timezone

    agora = timezone.now()
    situacoes = {s.tipo for s in p.situacoes(edital, agora=agora, com_advertencias=True)}
    assert p.RETIFICACAO_EM_CURSO in situacoes, "a prova não é vazia"
    with leitura_consistente():
        advertencia = encerramento.do_processo(edital.processo, GESTORA, agora=agora)
    tipos = {i.tipo for g in advertencia.grupos for i in g.itens}
    assert not tipos & encerramento.TIPOS_FORA_DO_PROCESSO

    corpo = texto(abrir(gestor(), edital.processo))
    assert "põe fim ao recebimento" not in corpo
    assert "Retificação" not in corpo.split("Este ato não pode ser desfeito")[0].split(TITULO)[-1]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=1301, codigo="1301"
    )


def _encerrar_o_edital_com_o_recurso_pendente(peca):
    edital = peca["cenario"]["edital"]
    edital.refresh_from_db()
    encerrar_antes_da_113(
        actor=Actor("gabi.gestora", "cefor", frozenset({"edital:encerrar"})),
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Encerrado antes da 113",
        idempotency_key="encerrar-130-recurso",
        correlation_id="teste-130",
    )
    return Edital.objects.get(pk=edital.id)


def test_o_recurso_que_impediria_o_edital_e_advertencia_no_processo(peca):
    """D-003: o recurso aguardando aparece, com a quem pedir, e o Confirmar continua."""
    edital = _encerrar_o_edital_com_o_recurso_pendente(peca)

    do_gestor = texto(abrir(sessao("gabi.gestora", ["gestor"]), edital.processo))
    assert "1 recurso aguarda decisão." in do_gestor
    assert "Peça a quem julga recursos." in do_gestor
    assert CONFIRMAR in do_gestor

    de_quem_julga = texto(abrir(sessao("gabi.gestora", ["gestor", "julgador"]), edital.processo))
    assert f'href="{reverse("interface:recursos", args=[edital.id])}"' in de_quem_julga
    assert "Peça a quem julga recursos" not in de_quem_julga


def test_cancelar_processo_nao_tem_o_bloco(pendente):
    """FR-4364, SC-1325: o "Cancelar Processo" é o de hoje."""
    with em(REFERENCIA):
        corpo = texto(abrir(gestor(), pendente.processo, "cancelar"))
    assert TITULO not in corpo
    assert 'name="resumo_das_providencias"' not in corpo


def test_com_edital_fora_de_estado_final_nada_e_lido(pendente):
    """D-004: com recusa certa o bloco não existe, nem o resumo."""
    from processo_seletivo.processos.application.commands import add_edital

    add_edital(
        actor=Actor("gabi.gestora", "cefor", frozenset({"edital:criar"})),
        processo_id=pendente.processo.id,
        data={"number": "70", "year": 2026, "title": "Ainda em elaboração", "description": "-"},
        idempotency_key="add-130",
        correlation_id="teste-130",
    )
    with em(REFERENCIA):
        resposta = abrir(gestor(), pendente.processo)
    corpo = texto(resposta)
    assert "Este ato será recusado." in corpo
    assert TITULO not in corpo and NADA not in corpo
    assert "advertencia" not in resposta.context


# ---------------------------------------------------------------------------------------------
# História 5 — a lista mudou depois que a tela abriu (FR-4365 a FR-4367, UX-279, SC-1327)
# ---------------------------------------------------------------------------------------------


def test_a_lista_mudou_a_confirmacao_volta_sem_encerrar(pendente):
    processo = pendente.processo
    antes = atos_do_processo(processo)
    with em(REFERENCIA):
        cliente = gestor()
        aberta = abrir(cliente, processo)
    pendente.aceitar(pendente.PPP, dia(24, 10, 14))  # a reservada responde com a tela aberta

    with em(dia(24, 10, 15)):
        resposta = enviar(cliente, processo, aberta, motivo="Etapas concluídas")

    assert resposta.status_code == 409
    corpo = texto(resposta)
    assert RENOVADA in corpo
    assert "1 convocação aguardando" not in corpo, "a lista é a de agora"
    assert CONVOCADO not in corpo
    assert ">Etapas concluídas</textarea>" in corpo
    assert resposta.context["chave_idempotencia"] == aberta.context["chave_idempotencia"]
    assert resposta.context["advertencia"].resumo != aberta.context["advertencia"].resumo
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ATIVO
    assert atos_do_processo(processo) == antes

    with em(dia(24, 10, 15, 5)):
        de_novo = enviar(cliente, processo, resposta, motivo="Etapas concluídas")
    assert de_novo.status_code == 302
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ENCERRADO


def test_confirmar_de_novo_encerra_mesmo_com_providencia_em_aberto(pendente):
    """FR-4366: a renovação não é barreira. Sem resumo, volta; com o resumo de agora, encerra."""
    processo = pendente.processo
    with em(REFERENCIA):
        cliente = gestor()
        aberta = abrir(cliente, processo)
        sem_resumo = cliente.post(
            url_do_ato(processo),
            {"chave_idempotencia": aberta.context["chave_idempotencia"], "motivo": "Concluído"},
        )
        assert sem_resumo.status_code == 409
        assert RENOVADA in texto(sem_resumo)
        assert "1 convocação aguardando resposta" in texto(sem_resumo)

        resposta = enviar(cliente, processo, sem_resumo)
    assert resposta.status_code == 302
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ENCERRADO


def test_a_renovacao_vem_antes_do_motivo(pendente):
    with em(REFERENCIA):
        cliente = gestor()
        aberta = abrir(cliente, processo := pendente.processo)
    pendente.aceitar(pendente.PPP, dia(24, 10, 14))
    with em(dia(24, 10, 15)):
        resposta = enviar(cliente, processo, aberta, motivo="")
    assert resposta.status_code == 409
    assert RENOVADA in texto(resposta)
    assert "é obrigatório" not in texto(resposta)


def test_o_prazo_que_vence_com_a_tela_aberta_renova_a_confirmacao(pendente):
    """Caso-limite: "aguardando resposta" passa a "prazo encerrado" entre abrir e enviar."""
    processo = pendente.processo
    with em(dia(30, 10, 23, 0)):
        cliente = gestor()
        aberta = abrir(cliente, processo)
    assert "1 convocação aguardando resposta, até 30/10/2026." in texto(aberta)

    with em(dia(31, 10, 0, 30)):
        resposta = enviar(cliente, processo, aberta)
    assert resposta.status_code == 409
    assert "1 convocação com prazo encerrado sem registro de resposta." in texto(resposta)


def test_cancelar_processo_sem_resumo_segue_como_hoje(pendente):
    processo = pendente.processo
    with em(REFERENCIA):
        cliente = gestor()
        aberta = abrir(cliente, processo, "cancelar")
        resposta = cliente.post(
            url_do_ato(processo, "cancelar"),
            {"chave_idempotencia": aberta.context["chave_idempotencia"], "motivo": "Desistência"},
        )
    assert resposta.status_code == 302
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.CANCELADO


# ---------------------------------------------------------------------------------------------
# História 3 — nada em aberto, sem prometer que acabou (FR-4359, UX-277)
# ---------------------------------------------------------------------------------------------


def test_sem_nada_em_aberto_a_frase_nao_promete_conclusao():
    cenario = montar_cenario(final="sem-pendencia")
    with em(REFERENCIA):
        cliente = gestor()
        aberta = abrir(cliente, cenario.processo)
        corpo = texto(aberta)
        assert NADA in corpo
        assert TITULO not in corpo
        assert aberta.context["advertencia"].vazia
        assert 'name="resumo_das_providencias"' in corpo
        for promessa in ("concluíd", "foi encerrad", "certame acabou"):
            assert promessa not in corpo.split(NADA)[1].split("</p>")[0]
        resposta = enviar(cliente, cenario.processo, aberta)
    assert resposta.status_code == 302


# ---------------------------------------------------------------------------------------------
# História 4 — a recusa por outro motivo reexibe a advertência atual (FR-4360, FR-4357)
# ---------------------------------------------------------------------------------------------


def test_motivo_vazio_volta_com_o_bloco_lido_uma_vez(pendente):
    with em(REFERENCIA):
        cliente = gestor()
        aberta = abrir(cliente, pendente.processo)
        with mock.patch.object(
            encerramento, "do_processo", wraps=encerramento.do_processo
        ) as composicao:
            resposta = enviar(cliente, pendente.processo, aberta, motivo="")
    assert composicao.call_count == 1, "a lista lida no pedido basta; o comando nem foi chamado"
    assert resposta.status_code == 422
    corpo = texto(resposta)
    assert "Motivo do encerramento é obrigatório." in corpo
    assert TITULO in corpo
    assert "1 convocação aguardando resposta" in corpo


def test_depois_do_422_a_mudanca_volta_pela_renovacao(pendente):
    processo = pendente.processo
    with em(REFERENCIA):
        cliente = gestor()
        recusada = enviar(cliente, processo, abrir(cliente, processo), motivo="")
    assert recusada.status_code == 422
    pendente.aceitar(pendente.PPP, dia(24, 10, 14))
    with em(dia(24, 10, 15)):
        resposta = enviar(cliente, processo, recusada, motivo="Agora com motivo")
    assert resposta.status_code == 409
    assert RENOVADA in texto(resposta)
    processo.refresh_from_db()
    assert processo.status == ProcessoSeletivo.Status.ATIVO


def test_processo_encerrado_por_outra_sessao_nao_mostra_o_bloco(pendente):
    processo = pendente.processo
    with em(REFERENCIA):
        primeira, segunda = gestor(), sessao("outra.gestora", ["gestor"])
        aberta = abrir(segunda, processo)
        assert enviar(primeira, processo, abrir(primeira, processo)).status_code == 302
        resposta = enviar(segunda, processo, aberta)
    assert resposta.status_code == 409
    corpo = texto(resposta)
    assert TITULO not in corpo
    assert CONFIRMAR not in corpo
