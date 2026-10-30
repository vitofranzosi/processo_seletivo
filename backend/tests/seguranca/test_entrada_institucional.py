"""A entrada institucional pela tela, com o provedor simulado (106, US2).

Cobre os testes 3, 4, 5, 8 e 9 do pedido, e as defesas do retorno: cabeçalho forjado, estado
ausente, repetido ou divergente, e provedor trocado.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
from processo_seletivo.comissoes.models import Funcao, MembroComissao
from processo_seletivo.interface.identidade import CHAVE_SESSAO, PAPEIS
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.models import AutoridadeHabilitada
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import SIGNATORY
from tests.seguranca.apoio import AGORA, ator_do_cliente, entrar, pessoa, vincular

pytestmark = pytest.mark.django_db


def _gestor_de_acessos():
    administrador = pessoa("admin-cefor")
    vincular(administrador, "cefor", "administrador-de-acessos")
    return Actor(
        administrador.username, "cefor", acessos.permissoes_dos_papeis(["administrador-de-acessos"])
    )


# --- Teste 3: a identidade simulada produz o Actor esperado ---------------------------------------


def test_a_entrada_institucional_produz_o_ator_dos_vinculos(client, provedor):
    ana = pessoa("ana-1", nome="Ana")
    vincular(ana, "cefor", "elaborador")

    resposta = entrar(client, "ana-1", nome="Ana")

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:lista")
    ator = ator_do_cliente(client)
    assert ator == Actor(ana.username, "cefor", frozenset(PAPEIS["elaborador"][1]))
    assert ator.subject.startswith("pessoa-")
    # Nada de papel na sessão: só a origem, a unidade e a identidade externa (`FR-3017`).
    assert set(client.session[CHAVE_SESSAO]) == {"origem", "unidade", "identidade_externa"}


def test_o_primeiro_acesso_cria_a_pessoa_e_o_seguinte_nao_muda_o_identificador(client, provedor):
    entrar(client, "novo-1", nome="Nome Antigo", email="a@ifes.edu.br")
    criada = get_user_model().objects.get()
    assert criada.username.startswith("pessoa-")
    assert not criada.has_usable_password()

    client.post(reverse("interface:sair"))
    entrar(client, "novo-1", nome="Nome Novo", email="b@ifes.edu.br")

    mesma = get_user_model().objects.get()
    assert mesma.username == criada.username
    assert (mesma.first_name, mesma.email) == ("Nome Novo", "b@ifes.edu.br")


def test_sem_vinculo_entra_mas_nao_tem_ator(client, provedor):
    entrar(client, "sem-acesso")

    assert ator_do_cliente(client) is None
    assert client.get(reverse("interface:lista")).status_code == 302


def test_a_entrada_vai_a_trilha_com_escopo(client, provedor):
    ana = pessoa("ana-2")
    vincular(ana, "cefor", "auditor")
    entrar(client, "ana-2")
    client.post(reverse("interface:sair"))

    eventos = RegistroAuditoria.objects.filter(actor_subject=ana.username).order_by("occurred_at")
    assert [(e.operation, e.institution_scope, e.aggregate_type) for e in eventos] == [
        ("ENTRADA", "cefor", "IdentidadeExterna"),
        ("SAIDA", "cefor", "IdentidadeExterna"),
    ]
    assert CHAVE_SESSAO not in client.session


def test_o_mesmo_fluxo_da_gestao_funciona_com_a_identidade_institucional(client, provedor):
    """A tela de autoridades, que a demonstração percorre, pelo `Actor` institucional."""
    gestora = pessoa("gestora-1")
    vincular(gestora, "cefor", "gestor")
    entrar(client, "gestora-1")

    resposta = client.post(
        reverse("interface:autoridades"),
        {
            "acao": "cadastrar",
            "cargo": "Diretor-Geral",
            "nome": "Fulana",
            "inicio_vigencia": "2026-11-01",
        },
    )

    assert resposta.status_code == 302, resposta.content
    assert AutoridadeHabilitada.objects.get(nome="Fulana").cadastrada_por == gestora.username


def test_o_ator_custa_no_maximo_duas_consultas_por_requisicao(
    client, provedor, django_assert_max_num_queries
):
    from django.test import RequestFactory

    from processo_seletivo.interface import identidade

    ana = pessoa("ana-3")
    vincular(ana, "cefor", "gestor")
    entrar(client, "ana-3")
    request = RequestFactory().get("/gestao/")
    request.session = client.session
    # A leitura da sessão é do middleware, e já existia: o que se mede é o que a 106 acrescenta.
    dict(request.session.items())

    with django_assert_max_num_queries(2):
        for _ in range(20):
            assert identidade.ator_da_sessao(request) is not None
            identidade.contexto_identidade(request)


# --- Teste 4: duas unidades, papéis diferentes ---------------------------------------------------


def test_a_mesma_pessoa_em_duas_unidades_tem_as_permissoes_da_unidade_ativa(
    client, provedor, campus_a
):
    paula = pessoa("paula")
    vincular(paula, "cefor", "gestor")
    vincular(paula, "campus-a", "elaborador")
    entrar(client, "paula")

    no_cefor = ator_do_cliente(client)
    assert no_cefor.institution_scope == "campus-a"  # a primeira em ordem de código
    assert no_cefor.permissions == frozenset(PAPEIS["elaborador"][1])

    assert client.post(reverse("interface:unidade-ativa"), {"unidade": "cefor"}).status_code == 302
    no_outro = ator_do_cliente(client)
    assert no_outro.institution_scope == "cefor"
    assert no_outro.permissions == frozenset(PAPEIS["gestor"][1])
    assert not no_outro.can("edital:elaborar")
    assert RegistroAuditoria.objects.filter(
        operation="TROCA_DE_UNIDADE", actor_subject=paula.username, institution_scope="cefor"
    ).exists()


def test_a_troca_para_unidade_sem_vinculo_e_recusada(client, provedor, campus_a):
    paula = pessoa("paula-2")
    vincular(paula, "cefor", "gestor")
    entrar(client, "paula-2")

    resposta = client.post(reverse("interface:unidade-ativa"), {"unidade": "campus-a"})

    assert resposta.status_code == 403
    assert ator_do_cliente(client).institution_scope == "cefor"


# --- Teste 5: revogação impede novas operações ----------------------------------------------------


def test_a_revogacao_vale_na_requisicao_seguinte(client, provedor):
    gestora = pessoa("gestora-2")
    vinculo = vincular(gestora, "cefor", "gestor")
    entrar(client, "gestora-2")
    assert client.get(reverse("interface:autoridades")).status_code == 200

    acessos.revogar(_gestor_de_acessos(), vinculo=vinculo, motivo="Portaria 12", now=AGORA)

    tentativa = client.post(
        reverse("interface:autoridades"),
        {
            "acao": "cadastrar",
            "cargo": "Diretor-Geral",
            "nome": "Beltrana",
            "inicio_vigencia": "2026-11-01",
        },
    )
    assert tentativa.status_code == 302
    # A 107 manda quem perdeu o acesso à tela sem acesso, e não mais à página de acesso, onde ele
    # entraria de novo e voltaria ao mesmo lugar (`FR-3101` da 107). O que este caso prova não muda:
    # o ato é recusado, nada é gravado e não há ator.
    assert tentativa["Location"] == reverse("interface:sem-acesso")
    assert not AutoridadeHabilitada.objects.filter(nome="Beltrana").exists()
    assert ator_do_cliente(client) is None


def test_a_revogacao_de_um_papel_tira_so_aquele(client, provedor):
    ana = pessoa("ana-4")
    vincular(ana, "cefor", "gestor")
    auditora = vincular(ana, "cefor", "auditor")
    entrar(client, "ana-4")

    acessos.revogar(_gestor_de_acessos(), vinculo=auditora, motivo="Fim da designação", now=AGORA)

    ator = ator_do_cliente(client)
    assert ator.can("autoridade:gerir")
    assert not ator.can("auditoria:consultar")


def test_pessoa_desativada_perde_a_sessao(client, provedor):
    ana = pessoa("ana-5")
    vincular(ana, "cefor", "gestor")
    entrar(client, "ana-5")
    get_user_model().objects.filter(pk=ana.pk).update(is_active=False)

    assert ator_do_cliente(client) is None
    assert entrar(client, "ana-5").status_code == 403


# --- Teste 8: a segregação usa a identidade estável -----------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_a_segregacao_reconhece_a_pessoa_em_outra_sessao(
    client, provedor, api_client, manager_headers, process_payload
):
    """Elabora, homologa, sai, entra com outro nome e e-mail — e não publica.

    O `Actor` institucional vai aos mesmos comandos pela porta que a suíte usa para levá-los a
    publicação: a API de desenvolvimento, com o `subject` e as permissões que a gestão resolveu.
    """
    ana = pessoa("ana-6", nome="Ana", email="ana@ifes.edu.br")
    for papel in ("elaborador", "homologador", "publicador"):
        vincular(ana, "cefor", papel)
    entrar(client, "ana-6", nome="Ana")
    primeira = ator_do_cliente(client)

    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    cabecalhos = actor_headers(primeira.subject, sorted(primeira.permissions))
    for metodo, caminho, corpo in (
        ("put", "rascunho", complete_draft()),
        ("post", "submissoes", None),
        ("post", "homologacoes", {"reason": "Conferido"}),
    ):
        edital.refresh_from_db()
        resposta = getattr(api_client, metodo)(
            f"/api/v1/admin/editais/{edital.id}/{caminho}",
            corpo,
            format="json",
            **{**cabecalhos, "HTTP_IF_MATCH": f'"{edital.revision}"'},
        )
        assert resposta.status_code < 400, resposta.content

    client.post(reverse("interface:sair"))
    entrar(client, "ana-6", nome="Ana Maria", email="ana.maria@ifes.edu.br")
    segunda = ator_do_cliente(client)
    assert segunda.subject == primeira.subject

    edital.refresh_from_db()
    negada = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers(
                segunda.subject, sorted(segunda.permissions), key="publicacao-da-segunda-sessao"
            ),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert negada.status_code == 403, negada.content
    assert negada.json()["code"] == "segregation_of_duties"


# --- Teste 9: a comissão não abre caminho depois da revogação ------------------------------------


def _processo_com_presidente(subject):
    processo = ProcessoSeletivo.objects.create(
        institutional_code="PS-106",
        title="Processo da 106",
        institution_scope="cefor",
        created_at=AGORA,
        created_by="fixture",
        last_changed_at=AGORA,
    )
    MembroComissao.objects.create(
        processo=processo,
        identity_subject=subject,
        funcao=Funcao.PRESIDENTE,
        criado_em=AGORA,
        criado_por="fixture",
    )
    return processo


def test_a_presidencia_nao_alcanca_quem_perdeu_o_vinculo(client, provedor, campus_a):
    pres = pessoa("presidente")
    integrante = vincular(pres, "cefor", "integrante")
    vincular(pres, "campus-a", "integrante")
    processo = _processo_com_presidente(pres.username)
    entrar(client, "presidente")
    client.post(reverse("interface:unidade-ativa"), {"unidade": "cefor"})
    assert pode_gerir_comissao(ator_do_cliente(client), processo) is not None

    acessos.revogar(_gestor_de_acessos(), vinculo=integrante, motivo="Saiu do Cefor", now=AGORA)

    assert ator_do_cliente(client) is None
    assert pode_gerir_comissao(ator_do_cliente(client), processo) is None
    # Nem pela outra unidade, onde o vínculo continua: o escopo do ator não é o do Processo.
    assert (
        client.post(reverse("interface:unidade-ativa"), {"unidade": "campus-a"}).status_code == 302
    )
    assert pode_gerir_comissao(ator_do_cliente(client), processo) is None
    # E de volta ao Cefor, não: a troca exige vínculo vigente lá.
    assert client.post(reverse("interface:unidade-ativa"), {"unidade": "cefor"}).status_code == 403


# --- As defesas do retorno -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "cabecalhos",
    [
        {"HTTP_REMOTE_USER": "ana-7"},
        {"HTTP_X_REMOTE_USER": "ana-7"},
        {"HTTP_X_FORWARDED_USER": "ana-7"},
        {"REMOTE_USER": "ana-7"},
    ],
)
def test_cabecalho_do_cliente_nao_autentica(client, provedor, cabecalhos):
    vincular(pessoa("ana-7"), "cefor", "gestor")
    client.get(reverse("interface:entrar-institucional"))
    estado = provedor.ultima_ida()["estado"]

    resposta = client.get(
        reverse("interface:retorno-institucional"),
        {"state": estado, "identificador": "ana-7", "provedor": "simulado"},
        **cabecalhos,
    )

    assert resposta.status_code == 403
    assert ator_do_cliente(client) is None
    assert not RegistroAuditoria.objects.filter(operation="ENTRADA").exists()


def test_retorno_sem_a_ida_e_recusado_sem_criar_pessoa(client, provedor):
    bilhete = provedor.emitir("ana-8")

    resposta = client.get(
        reverse("interface:retorno-institucional"), {"state": "qualquer", "bilhete": bilhete}
    )

    assert resposta.status_code == 403
    assert not get_user_model().objects.exists()


def test_retorno_com_estado_divergente_e_recusado(client, provedor):
    client.get(reverse("interface:entrar-institucional"))
    bilhete = provedor.emitir("ana-9")

    resposta = client.get(
        reverse("interface:retorno-institucional"), {"state": "outro", "bilhete": bilhete}
    )

    assert resposta.status_code == 403
    assert not get_user_model().objects.exists()


def test_o_retorno_nao_vale_duas_vezes(client, provedor):
    vincular(pessoa("ana-10"), "cefor", "gestor")
    client.get(reverse("interface:entrar-institucional"))
    estado = provedor.ultima_ida()["estado"]
    primeiro = provedor.emitir("ana-10")
    assert (
        client.get(
            reverse("interface:retorno-institucional"), {"state": estado, "bilhete": primeiro}
        ).status_code
        == 302
    )
    client.post(reverse("interface:sair"))

    repetido = client.get(
        reverse("interface:retorno-institucional"),
        {"state": estado, "bilhete": provedor.emitir("ana-10")},
    )

    assert repetido.status_code == 403


def test_identidade_de_outro_provedor_e_recusada(client, provedor):
    client.get(reverse("interface:entrar-institucional"))
    estado = provedor.ultima_ida()["estado"]
    bilhete = provedor.emitir("ana-11", provedor="outro")

    resposta = client.get(
        reverse("interface:retorno-institucional"), {"state": estado, "bilhete": bilhete}
    )

    assert resposta.status_code == 403
    assert not get_user_model().objects.exists()


def test_a_entrada_troca_a_sessao(client, provedor):
    vincular(pessoa("ana-12"), "cefor", "gestor")
    client.get(reverse("interface:entrar-institucional"))
    antes = client.session.session_key
    estado = provedor.ultima_ida()["estado"]

    client.get(
        reverse("interface:retorno-institucional"),
        {"state": estado, "bilhete": provedor.emitir("ana-12")},
    )

    assert antes and client.session.session_key != antes


def test_o_destino_pedido_e_respeitado(client, provedor):
    vincular(pessoa("ana-13"), "cefor", "gestor")

    resposta = entrar(client, "ana-13", proximo=reverse("interface:autoridades"))

    assert resposta["Location"] == reverse("interface:autoridades")


# --- O estado na fronteira do protocolo (revisão do #345) ----------------------------------------


def test_o_retorno_le_o_state_do_protocolo_e_nao_o_nome_interno(client, provedor):
    """Um provedor OIDC devolve o estado em `state`; `estado` é só o nome de dentro da gestão.

    O simulado da primeira versão usava `estado` na ida e na volta, e mascarava a recusa: um
    provedor convencional devolvia o valor certo em `state` e recebia 403 sem chegar ao adaptador.
    """
    vincular(pessoa("ana-14"), "cefor", "gestor")
    ida = client.get(reverse("interface:entrar-institucional"))
    assert "state=" in ida["Location"]
    estado = provedor.ultima_ida()["estado"]

    so_o_nome_interno = client.get(
        reverse("interface:retorno-institucional"),
        {"estado": estado, "bilhete": provedor.emitir("ana-14")},
    )
    assert so_o_nome_interno.status_code == 403

    client.get(reverse("interface:entrar-institucional"))
    estado = provedor.ultima_ida()["estado"]
    pelo_protocolo = client.get(
        reverse("interface:retorno-institucional"),
        {"state": estado, "bilhete": provedor.emitir("ana-14")},
    )
    assert pelo_protocolo.status_code == 302
    assert ator_do_cliente(client) is not None


def test_o_adaptador_pode_dizer_onde_o_estado_volta(client, settings, provedor):
    """Outro protocolo põe o estado em outro lugar; a comparação com a sessão continua da gestão."""
    import sys
    import types

    class ComRelayState(provedor.ProvedorSimulado):
        def estado_do_retorno(self, request):
            return request.GET.get("RelayState", "")

    modulo = types.ModuleType("provedor_com_relay_state")
    modulo.Provedor = ComRelayState
    sys.modules[modulo.__name__] = modulo
    try:
        settings.GESTAO_PROVEDOR_INSTITUCIONAL = "provedor_com_relay_state.Provedor"
        vincular(pessoa("ana-15"), "cefor", "gestor")
        client.get(reverse("interface:entrar-institucional"))
        estado = provedor.ultima_ida()["estado"]

        errado = client.get(
            reverse("interface:retorno-institucional"),
            {"RelayState": "outro", "state": estado, "bilhete": provedor.emitir("ana-15")},
        )
        assert errado.status_code == 403

        client.get(reverse("interface:entrar-institucional"))
        estado = provedor.ultima_ida()["estado"]
        certo = client.get(
            reverse("interface:retorno-institucional"),
            {"RelayState": estado, "bilhete": provedor.emitir("ana-15")},
        )
        assert certo.status_code == 302
    finally:
        del sys.modules[modulo.__name__]
