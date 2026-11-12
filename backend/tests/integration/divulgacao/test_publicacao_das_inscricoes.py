"""Publicar as inscrições — o ato, as recusas que o antecedem e o que ele congela (148).

```text
relação de recebidas            →  todas as enviadas, nenhum rascunho, bytes e PDF gravados
período em curso                →  409, dizendo até quando
Edital sem inscrição enviada    →  409
análise incompleta              →  409, dizendo quantas faltam
preliminar sem prazo escolhido  →  422
natureza que regride            →  422 (e o gatilho, por baixo)
mesma natureza sem motivo       →  422; com motivo, sucede
prévia obsoleta                 →  409
mesma chave                     →  o mesmo ato
homologação sem análise         →  só sem Etapa decisória
```
"""

import pytest
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from processo_seletivo.divulgacao.application.inscricoes import (
    aferir,
    divergencia_do_vigente,
    publicar_inscricoes,
)
from processo_seletivo.divulgacao.models import InscricaoNaPublicacao, PublicacaoDasInscricoes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.shared.tempo import ZONA
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.inscricoes_publicadas import (
    analisar,
    ator_publicador,
    evento_de_recurso,
    inscrever_no,
    montar,
    publicar,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar(gestor, api_client, manager_headers, seed=1480, codigo="1480")


def _recusa(funcao, codigo):
    with pytest.raises(DomainError) as excinfo:
        funcao()
    assert excinfo.value.code == codigo, excinfo.value.detail
    return excinfo.value


# ---------------------------------------------------------------------------
# A relação de recebidas (US1)
# ---------------------------------------------------------------------------


def test_a_relacao_de_recebidas_congela_conteudo_linhas_e_documento(cenario):
    inscricoes = inscrever_no(cenario, 3, primeiro=11)
    Inscricao.objects.create(
        created_at=timezone.now(),
        identity_subject="cpf:rascunho-0001",
        edital=cenario["edital"],
        profile_id=cenario["perfil"],
        nome="Quem não enviou",
    )

    ato = publicar(cenario, "RECEBIDAS", chave="recebidas-1")

    assert ato.natureza == "RECEBIDAS"
    assert ato.quantidade == 3
    assert ato.etapa_id is None
    assert ato.signatario_id == AUTORIDADE_DO_RESULTADO
    assert ato.unidade_sigla == "Cefor"
    assert bytes(ato.documento).startswith(b"%PDF")
    assert ato.conteudo_publico_hash == canonical_sha256(_conteudo(ato))
    itens = InscricaoNaPublicacao.objects.filter(publicacao=ato)
    assert {item.inscricao_id for item in itens} == {inscricao.id for inscricao in inscricoes}
    assert {item.situacao for item in itens} == {"RECEBIDA"}
    texto = bytes(ato.conteudo_publico).decode()
    assert "Quem não enviou" not in texto
    for inscricao in inscricoes:
        assert inscricao.protocolo in texto
        assert inscricao.nome in texto
        # Nenhum dado pessoal além de nome e protocolo atravessa (SC-1702).
        assert inscricao.cpf_normalizado not in texto
        assert inscricao.email not in texto
        assert str(inscricao.id) not in texto


def test_o_documento_nao_carrega_cpf_nem_email(cenario):
    inscricoes = inscrever_no(cenario, 2, primeiro=21)
    ato = publicar(cenario, "RECEBIDAS", chave="recebidas-pdf")
    documento = bytes(ato.documento)
    for inscricao in inscricoes:
        assert inscricao.cpf_normalizado.encode() not in documento
        assert inscricao.email.encode() not in documento


def test_edital_sem_inscricao_enviada_e_recusado(cenario):
    _recusa(lambda: publicar(cenario, "RECEBIDAS", chave="vazio"), "inscricoes_publicacao_vazia")
    assert not PublicacaoDasInscricoes.objects.exists()


def test_periodo_em_curso_e_recusado_dizendo_ate_quando(gestor, api_client, manager_headers):
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        seed=1481,
        codigo="1481",
        cronograma_extra=(
            {
                "id": "00000000-0000-0000-0000-000000099481",
                "type": "INSCRICAO",
                "description": "Período de inscrições",
                "startAt": "2026-01-01T00:00:00-03:00",
                "endAt": "2099-01-01T00:00:00-03:00",
                "order": 3,
                "isRegistrationPeriod": True,
            },
        ),
    )
    inscrever_no(cenario, 1, primeiro=31)

    recusa = _recusa(
        lambda: publicar(cenario, "RECEBIDAS", chave="em-curso"), "inscricoes_em_curso"
    )
    assert "01/01/2099" in recusa.detail


# ---------------------------------------------------------------------------
# A análise (US2) e as recusas da cadeia
# ---------------------------------------------------------------------------


def test_o_preliminar_espera_a_analise_inteira(cenario, gestor):
    inscricoes = inscrever_no(cenario, 3, primeiro=41)
    analisar(cenario, gestor, [(inscricoes[0], "FAVORAVEL")], sufixo="parcial")

    recusa = _recusa(
        lambda: publicar(cenario, "PRELIMINAR", prazo="SEM_RECURSO", chave="parcial"),
        "inscricoes_analise_incompleta",
    )
    assert "2 inscrição(ões)" in recusa.detail
    assert "Análise documental" in recusa.detail


def test_o_preliminar_exige_o_prazo_e_recusa_evento_vencido(cenario, gestor):
    inscricoes = inscrever_no(cenario, 1, primeiro=51)
    analisar(cenario, gestor, [(inscricoes[0], "FAVORAVEL")], sufixo="prazo")

    _recusa(
        lambda: publicar(cenario, "PRELIMINAR", chave="sem-prazo"), "inscricoes_prazo_obrigatorio"
    )
    _recusa(
        lambda: publicar(
            cenario, "PRELIMINAR", prazo="00000000-0000-0000-0000-000000000000", chave="outro"
        ),
        "inscricoes_prazo_invalido",
    )


def test_o_preliminar_nomeia_deferidas_conta_indeferidas_e_congela_o_prazo(cenario, gestor):
    inscricoes = inscrever_no(cenario, 3, primeiro=61)
    analisar(
        cenario,
        gestor,
        [
            (inscricoes[0], "FAVORAVEL"),
            (inscricoes[1], "DESFAVORAVEL"),
            (inscricoes[2], "FAVORAVEL"),
        ],
        sufixo="preliminar",
    )

    ato = publicar(
        cenario, "PRELIMINAR", prazo=evento_de_recurso(cenario["seed"]), chave="preliminar"
    )

    assert str(ato.etapa_id) == cenario["etapa"]
    assert ato.admite_recurso is True
    assert str(ato.recurso_evento_id) == evento_de_recurso(cenario["seed"])
    # O término do Evento, no fuso institucional — em UTC ele já é o dia seguinte.
    assert ato.recurso_ate.astimezone(ZONA).date().isoformat() == "2099-12-31"
    conteudo = _conteudo(ato)
    (grupo,) = conteudo["perfis"]
    # O Perfil sem Modalidade reservada tem uma lista só, a ampla, nomeada (FR-5440).
    (lista,) = grupo["listas"]
    assert lista["lista"] == "Ampla concorrência"
    assert {linha["protocolo"] for linha in lista["constam"]} == {
        inscricoes[0].protocolo,
        inscricoes[2].protocolo,
    }
    assert lista["nao_constam"] == 1
    texto = bytes(ato.conteudo_publico).decode()
    # A indeferida não é nomeada, nem o motivo atravessa (D-010).
    assert inscricoes[1].nome not in texto
    assert inscricoes[1].protocolo not in texto
    assert "Faltou o diploma" not in texto
    assert conteudo["cabecalho"]["prazo"]["admite"] is True
    situacoes = dict(
        InscricaoNaPublicacao.objects.filter(publicacao=ato).values_list("inscricao_id", "situacao")
    )
    assert situacoes[inscricoes[1].id] == "INDEFERIDA"


def test_a_natureza_nao_regride_nem_pela_aplicacao_nem_pelo_banco(cenario, gestor):
    inscricoes = inscrever_no(cenario, 1, primeiro=71)
    analisar(cenario, gestor, [(inscricoes[0], "FAVORAVEL")], sufixo="regride")
    publicar(cenario, "PRELIMINAR", prazo="SEM_RECURSO", chave="p1")

    _recusa(lambda: publicar(cenario, "RECEBIDAS", chave="r1"), "inscricoes_natureza_regride")


def test_mesma_natureza_e_correcao_e_exige_motivo(cenario):
    inscrever_no(cenario, 1, primeiro=81)
    primeira = publicar(cenario, "RECEBIDAS", chave="c1")
    inscrever_no(cenario, 1, primeiro=82)
    assert divergencia_do_vigente(cenario["edital"])["novas"] == 1

    _recusa(lambda: publicar(cenario, "RECEBIDAS", chave="c2"), "inscricoes_motivo_obrigatorio")
    segunda = publicar(
        cenario, "RECEBIDAS", motivo="Inscrição recebida após a reabertura do prazo.", chave="c3"
    )

    assert segunda.publicacao_anterior_id == primeira.id
    assert segunda.quantidade == 2
    assert divergencia_do_vigente(cenario["edital"])["total"] == 0
    sucede = _conteudo(segunda)["cabecalho"]["sucede"]
    assert sucede["motivo"] == "Inscrição recebida após a reabertura do prazo."
    # A primeira continua como foi publicada.
    primeira.refresh_from_db()
    assert primeira.quantidade == 1


def test_a_mesma_chave_devolve_o_mesmo_ato_e_a_previa_obsoleta_e_recusada(cenario):
    inscrever_no(cenario, 1, primeiro=91)
    afericao = aferir(edital=cenario["edital"], natureza="RECEBIDAS", at=timezone.now())

    def publicar_com(chave, assinatura):
        return publicar_inscricoes(
            actor=ator_publicador(),
            edital_id=cenario["edital"].id,
            natureza="RECEBIDAS",
            autoridade=str(AUTORIDADE_DO_RESULTADO),
            confirmacao_da_previa=assinatura,
            idempotency_key=chave,
        )

    inscrever_no(cenario, 1, primeiro=92)
    _recusa(lambda: publicar_com("obsoleta", afericao.assinatura), "publication_preview_stale")

    nova = aferir(edital=cenario["edital"], natureza="RECEBIDAS", at=timezone.now()).assinatura
    primeira = publicar_com("mesma", nova)
    assert publicar_com("mesma", nova).id == primeira.id
    assert PublicacaoDasInscricoes.objects.count() == 1


def test_o_ato_e_append_only_na_aplicacao_e_no_banco(cenario):
    inscrever_no(cenario, 1, primeiro=101)
    ato = publicar(cenario, "RECEBIDAS", chave="imutavel")
    item = InscricaoNaPublicacao.objects.get(publicacao=ato)

    with pytest.raises(TypeError):
        ato.save()
    with pytest.raises(TypeError):
        item.delete()
    if connection.vendor != "postgresql":
        return
    for comando in (
        "UPDATE divulgacao_publicacaodasinscricoes SET quantidade = 9",
        "DELETE FROM divulgacao_publicacaodasinscricoes",
        "UPDATE divulgacao_inscricaonapublicacao SET situacao = 'DEFERIDA'",
    ):
        with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(comando)


def test_a_inscricao_enviada_continua_imutavel_depois_do_ato(cenario):
    """O ato não abre porta nenhuma: a enviada não muda, e o ato não tem o que reler."""
    (inscricao,) = inscrever_no(cenario, 1, primeiro=111)
    publicar(cenario, "RECEBIDAS", chave="enviada")

    inscricao.nome = "Outro nome"
    with pytest.raises(TypeError):
        inscricao.save()


def test_sem_capacidade_e_403_e_fora_do_escopo_e_404(cenario):
    inscrever_no(cenario, 1, primeiro=121)
    assinatura = aferir(
        edital=cenario["edital"], natureza="RECEBIDAS", at=timezone.now()
    ).assinatura

    def publicar_como(ator):
        return publicar_inscricoes(
            actor=ator,
            edital_id=cenario["edital"].id,
            natureza="RECEBIDAS",
            autoridade=str(AUTORIDADE_DO_RESULTADO),
            confirmacao_da_previa=assinatura,
            idempotency_key="autorizacao",
        )

    _recusa(lambda: publicar_como(ator_institucional("gestor", "comissao:gerir")), "forbidden")
    alheio = ator_institucional("paula", "resultado:publicar", escopo="outra-unidade")
    _recusa(lambda: publicar_como(alheio), "not_found")


# ---------------------------------------------------------------------------
# Sem análise individual (US5, D-007)
# ---------------------------------------------------------------------------


def test_sem_etapa_decisoria_a_homologacao_contempla_todas(gestor, api_client, manager_headers):
    cenario = montar(gestor, api_client, manager_headers, seed=1482, codigo="1482", decisoria=False)
    inscricoes = inscrever_no(cenario, 2, primeiro=131)

    _recusa(
        lambda: publicar(cenario, "PRELIMINAR", prazo="SEM_RECURSO", chave="sem-etapa"),
        "inscricoes_sem_etapa_de_analise",
    )
    ato = publicar(cenario, "HOMOLOGACAO", chave="homologa-todas")

    assert ato.etapa_id is None
    assert {item.situacao for item in InscricaoNaPublicacao.objects.filter(publicacao=ato)} == {
        "DEFERIDA"
    }
    texto = bytes(ato.conteudo_publico).decode()
    assert all(inscricao.protocolo in texto for inscricao in inscricoes)


def test_com_etapa_decisoria_a_homologacao_espera_a_analise(cenario):
    """A homologação sem análise não é escolhível onde há Etapa que decide (FR-5412)."""
    inscrever_no(cenario, 1, primeiro=141)
    _recusa(
        lambda: publicar(cenario, "HOMOLOGACAO", chave="sem-analise"),
        "inscricoes_analise_incompleta",
    )


def _conteudo(ato):
    import json

    return json.loads(bytes(ato.conteudo_publico))
