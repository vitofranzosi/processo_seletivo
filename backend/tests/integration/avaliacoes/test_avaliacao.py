"""Registrar a avaliação: salvar, validar contra o publicado, e concluir em ato distinto (US4)."""

from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.avaliacao import concluir, gravar
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, ConclusaoAvaliacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, constituir, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def edital_com_regra(db, api_client, manager_headers):
    """Etapa eliminatória, máxima 100 e nota mínima 70 — as três regras que a validação usa."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0031"},
        {
            "institutionalCode": "PS-2026-031",
            "title": "Processo com regra publicada",
            "firstEdital": {"number": "31", "year": 2026, "title": "Edital com regra"},
        },
        seed=3,
        avaliacoes=2,
        maxima="100.0000",
        minima="70.0000",
    )


@pytest.fixture
def etapa(edital_com_regra):
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A1, 3)


@pytest.fixture
def cenario(gestor, edital_com_regra, etapa):
    processo = edital_com_regra.processo
    membros = constituir(
        gestor,
        processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO), ("ana", Funcao.MEMBRO)],
        prefixo="aval",
    )
    for nome in ("joao", "ana"):
        alocar_em(gestor, processo, membros[nome], edital_com_regra, etapa)
    inscricoes = inscrever(edital_com_regra, 2, primeiro=300)
    distribuir(
        actor=gestor,
        processo_id=processo.id,
        edital_id=edital_com_regra.id,
        etapa_id=etapa,
        membro_ids=[membros["joao"].id, membros["ana"].id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="aval",
        correlation_id="teste",
    )
    return {"membros": membros, "inscricoes": inscricoes}


def argumentos(edital, etapa, inscricao, *, subject="joao", **extra):
    """Os argumentos comuns, com a versão vigente já reconhecida.

    `versao_reconhecida` é **obrigatória** na conclusão: sem ela, omitir o campo do envio
    desligaria FR-073 pelo cliente. `gravar` a ignora, e passá-la aqui não a torna opcional lá.
    """
    return {
        "ator": ator_institucional(subject),
        "edital": edital,
        "etapa_id": etapa,
        "inscricao_id": inscricao.id,
        "correlation_id": "teste",
        **extra,
    }


def para_concluir(edital, etapa, inscricao, **extra):
    versao = edital.versoes_consolidadas.latest("materialized_at")
    return argumentos(edital, etapa, inscricao, versao_reconhecida=versao.id, **extra)


def test_o_rascunho_e_gravado_sem_exigir_conclusao(edital_com_regra, etapa, cenario):
    """FR-031: a Avaliação nasce rascunho, e sair e voltar encontra o que se escreveu."""
    avaliacao, _ = gravar(
        **argumentos(
            edital_com_regra,
            etapa,
            cenario["inscricoes"][0],
            pontuacao="80",
            parecer="Em análise",
            expected_revision=1,
        )
    )

    assert avaliacao.estado == Avaliacao.Estado.RASCUNHO
    assert avaliacao.pontuacao == Decimal("80.0000")
    assert avaliacao.versao is None
    assert avaliacao.concluida_em is None


def test_pontuacao_acima_da_maxima_publicada_e_recusada(edital_com_regra, etapa, cenario):
    """FR-033: o limite é o que o Edital publicou, e a recusa o nomeia."""
    with pytest.raises(DomainError) as recusa:
        concluir(
            **para_concluir(
                edital_com_regra,
                etapa,
                cenario["inscricoes"][0],
                pontuacao="120",
                parecer="",
                expected_revision=1,
            )
        )

    assert recusa.value.status == 422
    assert "100.0000" in recusa.value.detail


def test_abaixo_da_minima_e_aceita_e_exige_parecer(edital_com_regra, etapa, cenario):
    """A nota mínima **não recusa** — ela torna o parecer obrigatório (FR-033, FR-034)."""
    inscricao = cenario["inscricoes"][0]

    with pytest.raises(DomainError) as sem_parecer:
        concluir(
            **para_concluir(
                edital_com_regra, etapa, inscricao, pontuacao="50", parecer="", expected_revision=1
            )
        )

    avaliacao, _ = concluir(
        **para_concluir(
            edital_com_regra,
            etapa,
            inscricao,
            pontuacao="50",
            parecer="Não apresentou o diploma exigido.",
            expected_revision=1,
        )
    )

    assert sem_parecer.value.code == "parecer_obrigatorio"
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert avaliacao.pontuacao == Decimal("50.0000")


def test_concluir_grava_a_versao_e_a_conclusao_preservada(edital_com_regra, etapa, cenario):
    """FR-071 e FR-094: a regra que governou o ato, e o que ele afirmou."""
    avaliacao, _ = concluir(
        **para_concluir(
            edital_com_regra,
            etapa,
            cenario["inscricoes"][0],
            pontuacao="90",
            parecer="Atende",
            expected_revision=1,
        )
    )

    assert avaliacao.versao is not None
    assert avaliacao.concluida_por == "joao"
    preservada = ConclusaoAvaliacao.objects.get(avaliacao=avaliacao)
    assert preservada.ordem == 1
    assert preservada.pontuacao == Decimal("90.0000")
    assert preservada.versao_id == avaliacao.versao_id


def test_concluida_e_imutavel_para_o_avaliador(edital_com_regra, etapa, cenario):
    """FR-035, e a guarda vale no comando — não na tela que esconde o formulário."""
    inscricao = cenario["inscricoes"][0]
    concluir(
        **para_concluir(
            edital_com_regra,
            etapa,
            inscricao,
            pontuacao="90",
            parecer="Atende",
            expected_revision=1,
        )
    )

    with pytest.raises(DomainError) as recusa:
        gravar(
            **argumentos(
                edital_com_regra, etapa, inscricao, pontuacao="95", parecer="", expected_revision=2
            )
        )

    assert recusa.value.code == "avaliacao_concluida"
    assert Avaliacao.objects.get(inscricao_id=inscricao.id).pontuacao == Decimal("90.0000")


def test_duas_abas_do_mesmo_avaliador_nao_se_sobrescrevem(edital_com_regra, etapa, cenario):
    """FR-081, EC-016: a segunda gravação parte de uma revisão que já não existe."""
    inscricao = cenario["inscricoes"][0]
    gravar(
        **argumentos(
            edital_com_regra, etapa, inscricao, pontuacao="80", parecer="A", expected_revision=1
        )
    )

    with pytest.raises(DomainError) as recusa:
        gravar(
            **argumentos(
                edital_com_regra, etapa, inscricao, pontuacao="10", parecer="B", expected_revision=1
            )
        )

    assert recusa.value.code == "stale_revision"
    assert Avaliacao.objects.get(inscricao_id=inscricao.id).parecer == "A"


def test_dois_avaliadores_concluem_a_mesma_inscricao_sem_interferir(
    edital_com_regra, etapa, cenario
):
    """EC-007: são duas Avaliações, de duas Atribuições — elas não competem.

    A Etapa declara duas avaliações, então as duas cabem; e cada uma tem revisão própria, de modo
    que a conclusão de uma não invalida a precondição da outra.
    """
    inscricao = cenario["inscricoes"][0]

    do_joao, _ = concluir(
        **para_concluir(
            edital_com_regra,
            etapa,
            inscricao,
            pontuacao="90",
            parecer="Atende",
            expected_revision=1,
        )
    )
    da_ana, _ = concluir(
        **para_concluir(
            edital_com_regra,
            etapa,
            inscricao,
            subject="ana",
            pontuacao="70",
            parecer="Parcial",
            expected_revision=1,
        )
    )

    assert do_joao.id != da_ana.id
    assert do_joao.pontuacao == Decimal("90.0000")
    assert da_ana.pontuacao == Decimal("70.0000")
    assert Avaliacao.objects.filter(inscricao_id=inscricao.id).count() == 2


def test_quem_nao_recebeu_a_inscricao_nao_avalia(edital_com_regra, etapa, cenario):
    """A autorização composta vale no comando, e não só na rota (FR-043)."""
    with pytest.raises(DomainError) as recusa:
        gravar(
            **argumentos(
                edital_com_regra,
                etapa,
                cenario["inscricoes"][0],
                subject="maria",
                pontuacao="80",
                parecer="",
                expected_revision=1,
            )
        )

    assert recusa.value.status == 404


def test_nada_disso_produz_resultado(edital_com_regra, etapa, cenario):
    """SC-013: concluir não torna a inscrição apta nem inapta — isso é da 013 (FR-037)."""
    inscricao = cenario["inscricoes"][0]
    concluir(
        **para_concluir(
            edital_com_regra,
            etapa,
            inscricao,
            pontuacao="90",
            parecer="Atende",
            expected_revision=1,
        )
    )

    inscricao.refresh_from_db()
    assert inscricao.status == "SUBMETIDA"
    campos = {campo.name for campo in Avaliacao._meta.get_fields()}
    for proibido in ("media", "situacao", "apto", "resultado", "quorum", "classificacao"):
        assert proibido not in campos


def test_pela_tela_o_avaliador_salva_e_conclui(
    client, seletor_ligado, edital_com_regra, etapa, cenario
):
    """O canal do ator, que é onde o princípio VI cobra a demonstração."""
    inscricao = cenario["inscricoes"][0]
    identificar(client, "joao", [])
    pagina = reverse("interface:mesa-inscricao", args=[edital_com_regra.id, etapa, inscricao.id])

    client.post(
        reverse("interface:mesa-avaliacao-gravar", args=[edital_com_regra.id, etapa, inscricao.id]),
        {"pontuacao": "85", "parecer": "Em análise", "expected_revision": "1"},
    )
    depois_de_salvar = client.get(pagina).content.decode()
    avaliacao = Avaliacao.objects.get(inscricao_id=inscricao.id, identity_subject="joao")
    client.post(
        reverse(
            "interface:mesa-avaliacao-concluir", args=[edital_com_regra.id, etapa, inscricao.id]
        ),
        {
            "pontuacao": "85",
            "parecer": "Atende",
            "expected_revision": str(avaliacao.revision),
            "versao_reconhecida": str(
                avaliacao.atribuicao.edital.versoes_consolidadas.latest("materialized_at").id
            ),
        },
    )
    depois_de_concluir = client.get(pagina).content.decode()

    assert "Rascunho salvo." in depois_de_salvar
    assert "Em análise" in depois_de_salvar
    assert "Avaliação concluída" in depois_de_concluir
    # Concluída não é formulário desabilitado: é a ausência do formulário (FR-035).
    assert "Concluir avaliação" not in depois_de_concluir
    assert Atribuicao.objects.get(inscricao=inscricao, membro__identity_subject="joao")


@pytest.mark.parametrize(
    "impossivel", ["Infinity", "-Infinity", "NaN", "sNaN", "1E+100", "1000", "80,5", "abc"]
)
def test_a_forma_recusa_o_que_nao_e_pontuacao(edital_com_regra, etapa, cenario, impossivel):
    """O rascunho valida a **forma**, e a forma inclui o que `Decimal` aceita e o banco não.

    `Infinity`, `sNaN` e expoentes extremos atravessam o construtor e explodem depois — no
    `quantize` ou no `INSERT`. Recusar aqui é o que impede que um valor impossível vire erro
    interno em vez de recusa legível.
    """
    with pytest.raises(DomainError) as recusa:
        gravar(
            **argumentos(
                edital_com_regra,
                etapa,
                cenario["inscricoes"][0],
                pontuacao=impossivel,
                parecer="",
                expected_revision=1,
            )
        )

    assert recusa.value.status == 422
    assert recusa.value.code == "pontuacao_invalida"


def test_o_rascunho_aceita_acima_da_maxima_e_a_conclusao_nao(edital_com_regra, etapa, cenario):
    """A separação que a spec declara: forma no rascunho, regra publicada na conclusão.

    Quem está no meio do trabalho pode gravar um valor que ainda não decidiu; cobrar a máxima ali
    obrigaria a concluir para descobrir se o número passa (FR-031, FR-032, FR-033).
    """
    inscricao = cenario["inscricoes"][0]

    avaliacao, _ = gravar(
        **argumentos(
            edital_com_regra, etapa, inscricao, pontuacao="150", parecer="", expected_revision=1
        )
    )

    with pytest.raises(DomainError) as recusa:
        concluir(
            **para_concluir(
                edital_com_regra,
                etapa,
                inscricao,
                pontuacao="150",
                parecer="Atende",
                expected_revision=2,
            )
        )

    assert avaliacao.pontuacao == Decimal("150.0000")
    assert "100.0000" in recusa.value.detail


def test_concluir_sem_declarar_a_versao_e_recusado(edital_com_regra, etapa, cenario):
    """FR-073 não pode ser desligado pelo cliente.

    Se a comparação só acontecesse quando o campo viesse, omiti-lo do envio bastaria para concluir
    sem reconhecer uma Retificação — que é exatamente o que o requisito existe para impedir.
    """
    with pytest.raises(DomainError) as recusa:
        concluir(
            **argumentos(
                edital_com_regra,
                etapa,
                cenario["inscricoes"][0],
                pontuacao="88",
                parecer="Atende",
                expected_revision=1,
                versao_reconhecida=None,
            )
        )

    assert recusa.value.code == "versao_nao_reconhecida"
    assert not Avaliacao.objects.filter(estado=Avaliacao.Estado.CONCLUIDA).exists()
