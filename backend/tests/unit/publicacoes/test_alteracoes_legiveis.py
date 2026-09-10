"""O que a Retificação alterou, dito em linguagem do domínio (024, FR-130, D-005, D-009).

**O que este arquivo protege.** `target_path` é endereçamento estrutural — a forma certa para o
sistema achar o que mudou, e a forma errada para dizer a alguém o que mudou. Um caminho com
`id=<uuid>` numa página pública é vocabulário nosso vazando para a língua do Edital, contra o
Princípio I.

Duas garantias, e a segunda é a que se esquece: o tradutor **acerta** os caminhos que conhece, e
**cala** nos que não conhece. Inventar rótulo genérico para caminho desconhecido produziria uma
linha que afirma algo sobre o Edital que ninguém disse.
"""

from dataclasses import dataclass

import pytest

from processo_seletivo.publicacoes.domain.alteracoes import alteracao_legivel, alteracoes_legiveis

PERFIL = "11111111-1111-4111-8111-111111111111"
EVENTO = "22222222-2222-4222-8222-222222222222"
ETAPA = "33333333-3333-4333-8333-333333333333"
ANEXO = "44444444-4444-4444-8444-444444444444"
SECAO = "55555555-5555-4555-8555-555555555555"
DOCUMENTO = "66666666-6666-4666-8666-666666666666"
MODALIDADE = "77777777-7777-4777-8777-777777777777"


@dataclass
class Alteracao:
    """O par que o tradutor precisa. A `AlteracaoNormativa` persistida serve igual — receber a
    forma mínima é o que mantém este arquivo sem banco."""

    target_path: str
    operation: str = "REPLACE"


BASE = {
    "title": "Edital de seleção",
    "profiles": [
        {
            "id": PERFIL,
            "name": "Professor de Informática",
            "immediateVacancies": 2,
            "competitionModalities": [{"id": MODALIDADE, "name": "Ampla concorrência"}],
        }
    ],
    "schedule": [{"id": EVENTO, "description": "Período de inscrições"}],
    "stages": [{"id": ETAPA, "name": "Prova de títulos"}],
    "sections": [{"id": SECAO, "title": "Das disposições finais"}],
    "attachments": [{"id": ANEXO, "label": "Anexo I — Formulário"}],
    "documentRequirements": [{"id": DOCUMENTO, "name": "Diploma"}],
}


@pytest.mark.parametrize(
    ("caminho", "onde", "campo"),
    [
        (
            f"/profiles/id={PERFIL}/immediateVacancies",
            "Perfil “Professor de Informática”",
            "Vagas imediatas",
        ),
        (f"/profiles/id={PERFIL}/compensation", "Perfil “Professor de Informática”", "Remuneração"),
        (f"/schedule/id={EVENTO}/endAt", "Evento do cronograma “Período de inscrições”", "Término"),
        (
            f"/schedule/id={EVENTO}/location",
            "Evento do cronograma “Período de inscrições”",
            "Local",
        ),
        (f"/stages/id={ETAPA}/weight", "Etapa “Prova de títulos”", "Peso"),
        (f"/sections/id={SECAO}/content", "Seção “Das disposições finais”", "Texto"),
        (f"/attachments/id={ANEXO}/label", "Anexo “Anexo I — Formulário”", "Rótulo"),
        (
            f"/documentRequirements/id={DOCUMENTO}/required",
            "Documento exigido “Diploma”",
            "Obrigatoriedade",
        ),
        ("/title", "O Edital", "Título do Edital"),
    ],
)
def test_cada_colecao_publicada_tem_traducao(caminho, onde, campo):
    """Uma linha por coleção do conteúdo publicado — é a varredura que a T-002 exige.

    O nome da entidade vem do **conteúdo-base**: é o que o Edital dizia quando a Retificação foi
    escrita, e é o que quem lê o histórico reconhece. Ler do banco daria o nome de hoje, que pode
    ser justamente o que a Retificação mudou.
    """
    lida = alteracao_legivel(BASE, Alteracao(caminho))

    assert lida == {"onde": onde, "campo": campo, "operacao": "alterado"}


def test_a_colecao_aninhada_nomeia_as_duas_entidades():
    """A Modalidade dentro do Perfil: sem a de fora, "Ampla concorrência" não diz de qual vaga."""
    lida = alteracao_legivel(
        BASE, Alteracao(f"/profiles/id={PERFIL}/competitionModalities/id={MODALIDADE}/name")
    )

    assert lida["onde"] == (
        "Perfil “Professor de Informática” — Modalidade de concorrência “Ampla concorrência”"
    )
    assert lida["campo"] == "Denominação"


def test_a_colecao_inteira_e_entrada_ou_saida_do_Edital():
    """Sem campo, a alteração é sobre o elemento: ele entrou ou saiu."""
    acrescimo = alteracao_legivel(BASE, Alteracao("/attachments/-", operation="ADD"))
    remocao = alteracao_legivel(BASE, Alteracao(f"/profiles/id={PERFIL}", operation="REMOVE"))

    assert acrescimo == {"onde": "Anexo", "campo": "", "operacao": "acrescentado"}
    assert remocao["operacao"] == "removido"
    assert remocao["campo"] == ""


def test_entidade_que_o_conteudo_base_nao_tem_devolve_so_o_tipo():
    """Acrescentar não tem "antes": o elemento ainda não existia para ter nome.

    Devolver "Perfil" já diz mais do que um UUID, e não afirma nada que o Edital não diga.
    """
    lida = alteracao_legivel(BASE, Alteracao("/profiles/id=00000000-0000-4000-8000-000000000000"))

    assert lida["onde"] == "Perfil"


@pytest.mark.parametrize(
    "caminho",
    [
        "/inventado/id=x/campo",
        f"/profiles/id={PERFIL}/campoQueNaoExiste",
        f"/attachments/id={ANEXO}/artifactHash",
        "/campoDeTopoDesconhecido",
        "profiles/sem-barra-inicial",
        "",
    ],
)
def test_caminho_que_nao_se_sabe_ler_nao_produz_linha(caminho):
    """D-009 — a omissão é honesta; a linha errada, não.

    `artifactHash` está aqui de propósito, e não é desconhecido: ele anda junto do arquivo e não é
    decisão própria. Mostrá-lo como linha separada diria duas vezes a mesma substituição, uma delas
    em SHA-256 — é a correção que a `020` já fez na tela da gestão.
    """
    assert alteracao_legivel(BASE, Alteracao(caminho)) is None


def test_a_lista_omite_o_ilegivel_e_preserva_a_ordem_do_ato():
    """A ordem é a que o ato declarou; o que não se lê some sem deixar buraco numerado."""
    lidas = alteracoes_legiveis(
        BASE,
        [
            Alteracao(f"/profiles/id={PERFIL}/immediateVacancies"),
            Alteracao("/inventado/id=x/campo"),
            Alteracao(f"/schedule/id={EVENTO}/endAt"),
        ],
    )

    assert [item["campo"] for item in lidas] == ["Vagas imediatas", "Término"]


def test_nenhuma_saida_carrega_enderecamento_estrutural():
    """A prova mecânica da D-005: nada do vocabulário do sistema atravessa para a tela.

    Sem esta asserção, um `campo` novo copiado do caminho passaria despercebido — foi assim que a
    tela da gestão ficou meses devolvendo `/attachments/id=…` cru para quem homologava.
    """
    caminhos = [
        f"/profiles/id={PERFIL}/immediateVacancies",
        f"/schedule/id={EVENTO}/endAt",
        f"/profiles/id={PERFIL}/competitionModalities/id={MODALIDADE}/name",
        "/attachments/-",
        "/title",
    ]

    for lida in alteracoes_legiveis(BASE, [Alteracao(caminho) for caminho in caminhos]):
        texto = f"{lida['onde']}{lida['campo']}"
        assert "/" not in texto
        assert "id=" not in texto
        assert PERFIL not in texto and EVENTO not in texto and MODALIDADE not in texto
