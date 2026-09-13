"""As correções de interface que a auditoria exploratória de 13/09/2026 abriu.

Cada teste guarda um caminho que existia e não era alcançável, ou um estado que a tela conhecia e
não dizia. Não há regra de negócio nova aqui: o que muda é o que a interface oferece e o que ela
declara — e é exatamente por isso que os testes são de tela, e não de domínio.

O relatório está em `doc/auditoria-exploratoria-ux-2026-09-13.md`.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import views
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def rascunho(db, api_client, manager_headers):
    """Um Processo novo, com o primeiro Edital em elaboração — e só ele.

    Criado aqui, e não pela fixture `edital` do conftest: aquela devolve "o único Edital do banco",
    e o que este módulo precisa é de um Edital cujo estado o teste conheça.
    """
    from processo_seletivo.processos.models import Edital  # noqa: PLC0415

    resposta = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-HARDENING-2026",
            "title": "Processo do endurecimento",
            "firstEdital": {"number": "91", "year": 2026, "title": "Edital 91/2026"},
        },
        format="json",
        # Chave própria: a do `manager_headers` é fixa, e reusá-la faz a segunda criação da mesma
        # sessão de testes voltar 409 em vez de criar.
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "hardening-pos-auditoria-0001"},
    )
    assert resposta.status_code in (200, 201), resposta.content
    return Edital.objects.get(number="91", year=2026)


# --- Roteamento da pendência -------------------------------------------------------------------
#
# `_destino` casava o **primeiro** segmento do caminho, e todo marco vive sob `/profiles/…`: a
# pendência do marco terminava em "Ir para Perfis de Vaga", que é a única etapa do assistente onde
# aquele conteúdo não se corrige.


PERFIL = "11111111-1111-1111-1111-111111111111"
MARCO = "22222222-2222-2222-2222-222222222222"
DENTRO_DO_MARCO = f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}"


def test_pendencia_do_marco_vai_para_a_classificacao():
    etapa, ancora, corrigivel = views._destino(
        f"{DENTRO_DO_MARCO}/operation", "milestone_sem_operacao"
    )

    assert etapa == "classificacao"
    assert ancora == "#titulo-classificacao"
    assert corrigivel


def test_peso_ausente_vai_para_as_etapas_e_nao_para_a_classificacao():
    """O campo a corrigir é o `weight` da Etapa, e ele não existe no cartão do marco."""
    etapa, ancora, _ = views._destino(f"{DENTRO_DO_MARCO}/stages", "milestone_stage_without_weight")

    assert (etapa, ancora) == ("etapas", "#etapas-titulo")


def test_pendencia_de_perfil_continua_nos_perfis():
    etapa, _, _ = views._destino(f"/profiles/id={PERFIL}/name", "x")
    assert etapa == "perfis"


def test_periodo_de_inscricoes_continua_vencendo_por_caminho_exato():
    """A chave exata `/schedule` vence a busca por segmento — era assim antes e continua sendo."""
    etapa, _, _ = views._destino("/schedule", "schedule_sem_periodo")
    assert etapa == "inscricao"


# --- Caminho normativo dito em português -------------------------------------------------------


def test_caminho_normativo_vira_entidade_e_campo():
    identificador = "1705f922-7fbe-4f03-abd4-d4df14cc3268"
    base = {"schedule": [{"id": identificador, "description": "Inscrições pelo portal"}]}

    onde, campo = views._onde_e_campo(base, f"/schedule/id={identificador}/endAt")

    assert "Evento do cronograma" in onde
    assert "Inscrições pelo portal" in onde
    assert campo == "Término"


def test_caminho_que_nao_resolve_nao_derruba_a_conferencia():
    """A tela onde o ato irreversível é assinado degrada para o nome da coleção."""
    onde, _ = views._onde_e_campo({}, "/profiles/id=nao-e-uuid/name")
    assert onde == "Perfil"


def test_instante_do_conteudo_sai_no_fuso_institucional():
    """Um término digitado como 10/10/2026 23:59 aparecia como 2026-10-11T02:59:00+00:00."""
    assert views._resumo_de_linha("2026-10-11T02:59:00+00:00") == "10/10/2026 23:59"


def test_texto_que_comeca_com_numero_nao_e_convertido():
    assert views._resumo_de_linha("2026 foi o ano da primeira turma") == (
        "2026 foi o ano da primeira turma"
    )


# --- Portas de entrada -------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_abre_o_edital_pelo_numero_e_pelo_titulo(client, seletor_ligado, publicado):
    """Da página inicial, as únicas portas eram as ações — "Cancelar" entre elas."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    destino = reverse("interface:detalhe", args=[publicado.id])
    assert corpo.count(f'href="{destino}"') >= 2


@pytest.mark.django_db
@pytest.mark.integration
def test_quem_julga_recurso_chega_a_tela_de_recursos(client, seletor_ligado, publicado):
    """A tela existia e nada apontava para ela: nem o Edital, nem o Processo, nem o cabeçalho."""
    identificar(client, "marta.julgadora", ["julgador"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()

    assert reverse("interface:recursos", args=[publicado.id]) in corpo
    assert "Recursos recebidos" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_quem_nao_julga_nao_recebe_o_caminho_dos_recursos(client, seletor_ligado, publicado):
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()

    assert reverse("interface:recursos", args=[publicado.id]) not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_anexos_tem_a_navegacao_do_assistente(client, seletor_ligado, rascunho):
    """Era a única das nove etapas sem ‹ Voltar e Avançar ›: o avanço do assistente parava ali."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[rascunho.id, "anexos"])
    ).content.decode()

    assert reverse("interface:compor-etapa", args=[rascunho.id, "inscricao"]) in corpo
    assert reverse("interface:compor-etapa", args=[rascunho.id, "conteudo"]) in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_a_etapa_de_perfis_explica_as_quatro_decisoes_de_efeito_tardio(
    client, seletor_ligado, rascunho
):
    """Três `<select>` e uma caixa de número decidiam semanas depois, sem dica visível nenhuma.

    O controle é `<select>`, que não tem `placeholder` onde a versão visível pudesse morar — e por
    isso, em `.oculto`, a frase não chegava a quem enxerga. A explicação volta **na etapa**, e não
    no cartão: `test_medida_dos_campos` guarda que explicação que não muda de um Perfil para o
    outro não se imprime uma vez por Perfil.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[rascunho.id, "perfis"])
    ).content.decode()

    assert "Quadro de vagas" in corpo
    assert "a ocupação e a convocação ficam sem o que apurar" in corpo
    assert "A declarada não recebe linha própria no quadro" in corpo
    assert "Declarar a reversão exige quadro de vagas publicado" in corpo
    assert "o sistema recusa convocar" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_processo_nomeia_quem_e_aguardado(client, seletor_ligado, rascunho):
    """Quem não elabora via só "Ativar" e "Cancelar", sem nada dizer que o certame espera alguém."""
    identificar(client, "gestor.unico", ["gestor"])
    corpo = client.get(
        reverse("interface:processo-detalhe", args=[rascunho.processo_id])
    ).content.decode()

    assert "Aguardando quem elabora" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_ativar_processo_declara_que_a_publicacao_ja_ativa(client, seletor_ligado, rascunho):
    """O ato continua existindo; o que muda é ele deixar de parecer o passo que falta."""
    identificar(client, "gestor.unico", ["gestor"])
    corpo = client.get(
        reverse("interface:processo-detalhe", args=[rascunho.processo_id])
    ).content.decode()

    assert "Publicar o primeiro Edital deste Processo já o ativa" in corpo


# --- Emitir não é divulgar --------------------------------------------------------------------


def test_marco_sem_ato_nao_fala_de_divulgacao():
    """Sem ato emitido não há o que divulgar, e a tela não inventa um estado."""
    assert views._divulgacao_do_marco(None, None, None) == {"divulgacao": None}


@pytest.mark.django_db
@pytest.mark.integration
def test_marco_diz_quando_a_divulgacao_ficou_para_tras(monkeypatch):
    """O estado que a auditoria encontrou depois de um recurso deferido: ato B, divulgação A.

    A tela dizia "Ordem emitida. O ato é imutável" e não mencionava publicação em lugar nenhum,
    enquanto a página do candidato seguia afirmando "Este é o resultado vigente" com a ordem
    anterior.

    **Estado, e não ação**: a `017`, SC-002, mantém a ação na tela do ato, e
    `test_publicar_resultado` guarda isso.
    """

    class AtoFalso:
        id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    class PublicacaoFalsa:
        ato_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

    monkeypatch.setattr(
        views,
        "historico_das_publicacoes",
        lambda **_: [{"publicacao": PublicacaoFalsa(), "vigente": True}],
    )
    estado = views._divulgacao_do_marco(object(), "marco", AtoFalso())["divulgacao"]

    assert not estado["nunca_divulgado"]
    assert len(estado["defasadas"]) == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_marco_silencia_quando_a_divulgacao_corresponde_ao_ato(monkeypatch):
    identidade = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    class AtoFalso:
        id = identidade

    class PublicacaoFalsa:
        ato_id = identidade

    monkeypatch.setattr(
        views,
        "historico_das_publicacoes",
        lambda **_: [{"publicacao": PublicacaoFalsa(), "vigente": True}],
    )
    estado = views._divulgacao_do_marco(object(), "marco", AtoFalso())["divulgacao"]

    assert not estado["nunca_divulgado"]
    assert estado["defasadas"] == []
