"""Duas unidades nas áreas que ainda não tinham teste com a segunda (110, FR-3336, `D-014`).

A revisão arquitetural de 30/10 achou o isolamento por escopo testado na maior parte da gestão, e
quatro áreas sem caso com outra unidade: a ocupação e a vaga acrescida, a admissibilidade e o
julgamento de recurso, o requerimento de matrícula e o documento no dossiê, e a API administrativa.
Em cada uma, o caminho de maior risco — o que recebe o identificador do objeto e grava, ou mostra
dado pessoal.

**Cada caso tem a sua prova de controle.** Primeiro quem é da unidade alcança o objeto; depois o
mesmo papel, noutra unidade registrada, recebe a resposta de objeto inexistente, e nada do que a
tela gravaria muda. Sem o controle, um 404 por rota errada passaria pelo isolamento.

Mora em `tests/interface/` porque o dossiê com requerimento é montado por fixtures daqui.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.ocupacao.models import AcrescimoDeVagas
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade
from processo_seletivo.requerimentos.application import preencher
from tests.fixtures.autoridades import registrar_unidade
from tests.fixtures.convocacao import habilitar_na_etapa_governada
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import complete_draft
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao
from tests.fixtures.recursos_us4 import assinatura_de as assinatura_da_peca
from tests.fixtures.recursos_us4 import cenario_julgavel
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

OUTRA = "campus-a"


@pytest.fixture
def outra_unidade(db):
    """A segunda unidade, registrada: o ator dela é de uma unidade que existe, como em produção."""
    return registrar_unidade(OUTRA)


def _eventos():
    return RegistroAuditoria.objects.count()


# --- Ocupação: a vaga acrescida e o desfazimento ----------------------------------------------


def _conferir_acrescimo(client, edital, **campos):
    dados = {
        "lista": "",
        "chave": "isolamento-110",
        "quantidade": 1,
        "origem": "Edital Multicampi nº 20/2026, Campus Vitória",
        "fundamento": "Vaga não preenchida no Edital regular",
        **campos,
    }
    return client.post(reverse("interface:acrescentar-vagas", args=[edital.id, MARCO]), dados)


def _leitura(pagina):
    marcador = 'name="leitura" value="'
    inicio = pagina.index(marcador) + len(marcador)
    return pagina[inicio : pagina.index('"', inicio)]


def test_a_ocupacao_alheia_e_inexistente_e_nao_grava(
    client,
    seletor_ligado,
    outra_unidade,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    edital, _, inscricoes = montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="isolamento-110",
        geral=0,
        reserva="UNLIMITED",
    )
    habilitar_na_etapa_governada(edital, inscricoes[:3])

    # Controle: quem apura no Cefor acrescenta.
    identificar(client, "carlos", ["gestor"])
    pagina = _conferir_acrescimo(client, edital).content.decode()
    _conferir_acrescimo(client, edital, confirmar="1", leitura=_leitura(pagina))
    acrescimo = AcrescimoDeVagas.objects.get()
    acrescimos, eventos = AcrescimoDeVagas.objects.count(), _eventos()

    identificar(client, "carlos", ["gestor"], escopo=OUTRA)
    acrescentar = _conferir_acrescimo(client, edital, confirmar="1", leitura=_leitura(pagina))
    desfazer = client.post(
        reverse("interface:desfazer-acrescimo", args=[edital.id, MARCO]),
        {
            "acrescimo": acrescimo.id,
            "quantidade": 1,
            "chave": "isolamento-110-d",
            "motivo": "Matrícula efetivada no Edital regular",
            "confirmar": "1",
            "leitura": _leitura(pagina),
        },
    )
    ocupacao = client.get(reverse("interface:ocupacao", args=[edital.id, MARCO]))

    assert (acrescentar.status_code, desfazer.status_code, ocupacao.status_code) == (404, 404, 404)
    assert AcrescimoDeVagas.objects.count() == acrescimos
    assert _eventos() == eventos


# --- Recursos: a admissibilidade e o julgamento ------------------------------------------------


def test_o_recurso_alheio_e_inexistente_e_nao_grava(
    client, seletor_ligado, outra_unidade, gestor, api_client, manager_headers, process_payload
):
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=171,
        codigo="0711",
        admitir_a_peca=False,
    )
    recurso = peca["recurso"]

    # Controle: quem julga no Cefor abre a peça.
    identificar(client, "marta.julgadora", ["julgador"])
    assert client.get(reverse("interface:recurso", args=[recurso.id])).status_code == 200
    juizos, decisoes, eventos = (
        JuizoDeAdmissibilidade.objects.count(),
        DecisaoRecurso.objects.count(),
        _eventos(),
    )

    identificar(client, "marta.julgadora", ["julgador"], escopo=OUTRA)
    leitura = client.get(reverse("interface:recurso", args=[recurso.id]))
    admitir = client.post(
        reverse("interface:recurso-admitir", args=[recurso.id]),
        {
            "admitido": "sim",
            "motivo": "Tempestivo e regularmente instruído.",
            "assinatura": assinatura_da_peca(recurso),
        },
    )
    julgar = client.post(
        reverse("interface:recurso-julgar", args=[recurso.id]),
        {"especie": "DEFERIDO", "motivacao": "Procede."},
    )

    assert (leitura.status_code, admitir.status_code, julgar.status_code) == (404, 404, 404)
    assert b"A prova did" not in leitura.content, "a fundamentação de quem recorreu não aparece"
    assert JuizoDeAdmissibilidade.objects.count() == juizos
    assert DecisaoRecurso.objects.count() == decisoes
    assert _eventos() == eventos


# --- Requerimento de matrícula e documento no dossiê -------------------------------------------


@pytest.fixture
def inscricao_com_requerimento(selecao_na_inscricao, candidatos_registrados, campos_declarados):
    """A inscrição com o requerimento enviado, pelo comando de verdade (o mesmo da `029`)."""
    from tests.fixtures.candidato import MARIA

    inscricao = pronta_para_enviar(selecao_na_inscricao)
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)
    preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )
    return inscricao


def test_o_requerimento_e_o_documento_alheios_sao_inexistentes(
    client, seletor_ligado, outra_unidade, inscricao_com_requerimento, campos_declarados
):
    dossie = reverse("interface:inscricao-recebida", args=[inscricao_com_requerimento.id])
    documento = reverse(
        "interface:documento-da-inscricao",
        args=[inscricao_com_requerimento.id, DOCUMENTO_DE_TODOS],
    )
    mae = campos_declarados["nome_da_mae"].encode()

    # Controle: quem conduz no Cefor lê o requerimento e abre o documento.
    identificar(client, "ana.gestora", ["gestor"])
    assert mae in client.get(dossie).content
    # O arquivo sai em `FileResponse`, que precisa ser fechado: a cópia conferida aberta acusaria
    # `ResourceWarning`, que o `pyproject.toml` promove a erro.
    controle = client.get(documento)
    assert b"".join(controle.streaming_content).startswith(b"%PDF")
    controle.close()
    eventos = _eventos()

    identificar(client, "ana.gestora", ["gestor"], escopo=OUTRA)
    lido, aberto = client.get(dossie), client.get(documento)

    assert (lido.status_code, aberto.status_code) == (404, 404)
    assert mae not in lido.content
    assert not aberto.streaming, "a recusa é a página de inexistente, e não o arquivo"
    assert b"%PDF" not in aberto.content
    assert _eventos() == eventos, "a consulta negada não fica registrada como consulta"


# --- A API administrativa ----------------------------------------------------------------------


def _da_outra_unidade(permissoes, chave):
    return {
        "HTTP_AUTHORIZATION": f"Bearer gestor-a|{OUTRA}|{','.join(permissoes)}",
        "HTTP_IDEMPOTENCY_KEY": chave,
        "HTTP_X_CORRELATION_ID": "isolamento-110",
    }


def test_a_api_administrativa_nao_alcanca_processo_nem_edital_alheios(
    api_client, outra_unidade, manager_headers, process_payload
):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    processo = ProcessoSeletivo.objects.get(pk=criado.json()["id"])
    edital = Edital.objects.get(processo=processo)
    antes = (processo.status, processo.revision, edital.status, edital.revision, _eventos())

    pedidos = {
        # Corpos válidos, para que a recusa venha da conferência do escopo: a validação do corpo é
        # anterior a ela, e responde 422 igual para objeto alheio e inexistente — não vaza nada.
        "rascunho": api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            complete_draft(),
            format="json",
            HTTP_IF_MATCH=f'"{edital.revision}"',
            **_da_outra_unidade(["edital:elaborar"], "isolamento-110-rascunho"),
        ),
        "submissão": api_client.post(
            f"/api/v1/admin/editais/{edital.id}/submissoes",
            format="json",
            HTTP_IF_MATCH=f'"{edital.revision}"',
            **_da_outra_unidade(["edital:submeter"], "isolamento-110-submissao"),
        ),
        "ativação": api_client.post(
            f"/api/v1/admin/processos/{processo.id}/ativacoes",
            {"reason": "Isolamento"},
            format="json",
            HTTP_IF_MATCH=f'"{processo.revision}"',
            **_da_outra_unidade(["processo:ativar"], "isolamento-110-ativacao"),
        ),
        "cancelamento": api_client.post(
            f"/api/v1/admin/editais/{edital.id}/cancelamentos",
            {"reason": "Isolamento"},
            format="json",
            HTTP_IF_MATCH=f'"{edital.revision}"',
            **_da_outra_unidade(["edital:cancelar"], "isolamento-110-cancelamento"),
        ),
    }

    assert {nome: resposta.status_code for nome, resposta in pedidos.items()} == {
        nome: 404 for nome in pedidos
    }
    processo.refresh_from_db()
    edital.refresh_from_db()
    assert (processo.status, processo.revision, edital.status, edital.revision, _eventos()) == antes
