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

from processo_seletivo.editais.domain import mutabilidade
from processo_seletivo.publicacoes.domain.alteracoes import alteracao_legivel, alteracoes_legiveis
from processo_seletivo.publicacoes.domain.colecoes import FORMA_DA_COLECAO

PERFIL = "11111111-1111-4111-8111-111111111111"
EVENTO = "22222222-2222-4222-8222-222222222222"
ETAPA = "33333333-3333-4333-8333-333333333333"
ANEXO = "44444444-4444-4444-8444-444444444444"
SECAO = "55555555-5555-4555-8555-555555555555"
DOCUMENTO = "66666666-6666-4666-8666-666666666666"
MODALIDADE = "77777777-7777-4777-8777-777777777777"
COTA = "88888888-8888-4888-8888-888888888888"
LINHA_GERAL = "99999999-9999-4999-8999-999999999999"
LINHA_DA_COTA = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
MARCO = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
CRITERIO = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
FATO = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"


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
            "competitionModalities": [
                {"id": MODALIDADE, "name": "Ampla concorrência"},
                {"id": COTA, "name": "Pessoas pretas e pardas", "normativeRule": {}},
            ],
            "vacancyTable": [
                {"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": 1},
                {"id": LINHA_DA_COTA, "modalityId": COTA, "immediateVacancies": 1},
            ],
            "declaredFacts": [
                {"id": FATO, "code": "nascimento", "label": "Data de nascimento", "type": "DATA"}
            ],
            "classificationMilestones": [
                {
                    "id": MARCO,
                    "name": "Resultado final",
                    "stages": [ETAPA],
                    "tiebreakers": [{"id": CRITERIO, "order": 1}],
                }
            ],
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


def test_o_recorte_transversal_vira_linha_com_o_campo_e_sem_valor():
    """A 044 (FR-721, D-008): nomeado, como toda linha — e não descartado em silêncio.

    A tela emite `REPLACE` para as três operações sobre o campo (passar a recortar, deixar de
    recortar, trocar o código), e as três se leem igual: o campo mudou.
    """
    linha = alteracao_legivel(BASE, Alteracao(f"/documentRequirements/id={DOCUMENTO}/modalityCode"))

    assert linha == {
        "onde": "Documento exigido “Diploma”",
        "campo": "Modalidade em todos os Perfis",
        "operacao": "alterado",
    }
    assert DOCUMENTO not in str(linha), "nenhum identificador interno"


@pytest.mark.parametrize(
    ("campo", "rotulo"),
    [("profileId", "Exigido apenas do Perfil"), ("modalityId", "Exigido apenas da modalidade")],
)
def test_o_recorte_exato_tambem_vira_linha(campo, rotulo):
    """A conferência de 25/09: a Retificação declarou 7 alterações, e o portal mostrou 6.

    A que faltava era a do laudo, que passou a valer só no C1 — a mais consequente para quem se
    inscreve, e a única que o resumo calava, porque o dicionário conhecia `modalityCode` e não os
    dois campos do recorte exato. O rótulo é o da tela da gestão, para que quem retifica e quem se
    inscreve leiam o mesmo nome.
    """
    linha = alteracao_legivel(BASE, Alteracao(f"/documentRequirements/id={DOCUMENTO}/{campo}"))

    assert linha == {"onde": "Documento exigido “Diploma”", "campo": rotulo, "operacao": "alterado"}


# ------------------------------------------------ o dicionário acompanha o contrato (RC-111)


def _caminho_sintetico(colecao, caminho):
    """Um caminho concreto para o par do contrato: a forma da gramática, com cada `*` trocado por
    um seletor de identidade que o conteúdo-base não tem — o elemento sem nome lido é o caso mais
    pobre, e é nele que a linha ainda precisa existir."""
    forma = FORMA_DA_COLECAO[colecao].replace("*", "id=00000000-0000-4000-8000-000000000000")
    return f"{forma}/{caminho}"


RETIFICAVEIS = sorted(
    (colecao, caminho)
    for (colecao, caminho), decisao in mutabilidade.CONTRATO.items()
    if decisao.natureza is mutabilidade.Natureza.RETIFICAVEL
)
NASCEM = sorted(
    (colecao, objeto)
    for (colecao, objeto), (pode, _razao) in mutabilidade.PODE_PASSAR_A_EXISTIR.items()
    if pode
)


@pytest.mark.parametrize(("colecao", "caminho"), RETIFICAVEIS + NASCEM)
def test_todo_campo_retificavel_do_contrato_vira_linha(colecao, caminho):
    """O guardião que faltava (024, FR-130): cada Retificação exibida traz o que foi alterado.

    O silêncio do tradutor é deliberado para o caminho que ninguém sabe ler — e é por isso que o
    que se sabe ler precisa cobrir o que o contrato deixa retificar. Sem este teste, um campo
    novo entrava no contrato, passava na Retificação e sumia do resumo público, sem que nenhuma
    das duas pontas reprovasse: foi assim que 45 dos 84 campos retificáveis ficaram calados até
    27/09 (`doc/achado-o-que-mudou-cala-campos-retificaveis.md`).

    Os objetos que **nascem** por Retificação entram junto: nascer é `REPLACE` sobre o `null`
    publicado, e o ato que só declara a regra de corte mostraria "O que mudou" vazio.
    """
    lida = alteracao_legivel({}, Alteracao(_caminho_sintetico(colecao, caminho)))

    assert lida is not None, (
        f"({colecao}, {caminho}) é retificável e o resumo público não o traduz: "
        "acrescente o rótulo em publicacoes/domain/alteracoes.py, com o nome da tela da "
        "Retificação"
    )
    assert lida["campo"], "a linha precisa nomear o campo, e não só a entidade"
    assert "/" not in lida["campo"] and "id=" not in lida["onde"]


def test_o_guardiao_enxerga_os_campos_compostos():
    """Contraprova: o teste acima não passa por acaso. Os pares compostos — os que o tradutor
    antigo não sabia ler, porque lia um segmento só — estão entre os que ele percorre."""
    compostos = {caminho for _colecao, caminho in RETIFICAVEIS if "/" in caminho}

    assert {"normativeRule/percentage", "appealWindow/durationDays", "drawMethod/source"} <= (
        compostos
    )
    assert ("vacancyTable", "immediateVacancies") in RETIFICAVEIS


@pytest.mark.parametrize(
    ("caminho", "onde", "campo"),
    [
        (
            f"/profiles/id={PERFIL}/competitionModalities/id={COTA}/normativeRule/percentage",
            "Perfil “Professor de Informática” — Modalidade de concorrência “Pessoas pretas e "
            "pardas”",
            "Percentual (%)",
        ),
        (
            f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/appealWindow/durationDays",
            "Perfil “Professor de Informática” — Marco de classificação “Resultado final”",
            "Prazo em dias",
        ),
        (
            f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}"
            "/drawMethod/normalization/rule",
            "Perfil “Professor de Informática” — Marco de classificação “Resultado final”",
            "Regra de normalização",
        ),
        ("/drawMethod/source", "O Edital", "Fonte pública da semente"),
        ("/maxInscricoesPorCandidato", "O Edital", "Teto de inscrições por candidato"),
    ],
)
def test_o_campo_composto_se_le_pelo_caminho_inteiro(caminho, onde, campo):
    """`normativeRule` sozinho não diz se mudou o percentual ou o fundamento.

    O tradutor lia um segmento depois da entidade, e o percentual da cota — o que mais pesa para
    quem se inscreve por ela — não virava linha.
    """
    assert alteracao_legivel(BASE, Alteracao(caminho)) == {
        "onde": onde,
        "campo": campo,
        "operacao": "alterado",
    }


@pytest.mark.parametrize(
    ("linha", "nome"),
    [(LINHA_GERAL, "Ampla concorrência"), (LINHA_DA_COTA, "Pessoas pretas e pardas")],
)
def test_a_linha_do_quadro_se_chama_pela_lista_de_concorrencia(linha, nome):
    """A linha não tem nome: ela é a lista a que dá vagas. A geral é a sem Modalidade, e é assim
    que a tela da Retificação a chama."""
    lida = alteracao_legivel(
        BASE, Alteracao(f"/profiles/id={PERFIL}/vacancyTable/id={linha}/immediateVacancies")
    )

    assert lida == {
        "onde": f"Perfil “Professor de Informática” — Linha do quadro de vagas “{nome}”",
        "campo": "Vagas imediatas",
        "operacao": "alterado",
    }


def test_o_criterio_de_desempate_nomeia_os_tres_niveis():
    """Dois níveis de coleção aninhada: o critério mora no marco, que mora no Perfil."""
    lida = alteracao_legivel(
        BASE,
        Alteracao(
            f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/tiebreakers/id={CRITERIO}"
            "/order"
        ),
    )

    assert lida == {
        "onde": "Perfil “Professor de Informática” — Marco de classificação “Resultado final” — "
        "Critério de desempate nº 1",
        "campo": "Ordem de aplicação",
        "operacao": "alterado",
    }


def test_o_fato_declarado_se_chama_pelo_rotulo_e_nao_pelo_tipo():
    """O tipo é `DATA` ou `INTEIRO` — vocabulário nosso, e não o nome que o candidato lê."""
    lida = alteracao_legivel(
        BASE, Alteracao(f"/profiles/id={PERFIL}/declaredFacts/id={FATO}", operation="REMOVE")
    )

    assert lida == {
        "onde": "Perfil “Professor de Informática” — Fato declarado “Data de nascimento”",
        "campo": "",
        "operacao": "removido",
    }


def test_o_objeto_que_nasce_vira_linha():
    """A regra de corte que nasce por Retificação (048) é `REPLACE` sobre o `null` publicado."""
    lida = alteracao_legivel(
        BASE, Alteracao(f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/cutRule")
    )

    assert lida["campo"] == "Regra de corte"


@pytest.mark.parametrize(
    "caminho",
    [
        # A parte da regra que não se retifica continua sem linha: completar o dicionário não é
        # traduzir por prefixo.
        f"/profiles/id={PERFIL}/competitionModalities/id={COTA}/normativeRule/calculation",
        f"/profiles/id={PERFIL}/competitionModalities/id={COTA}/normativeRule",
        # `stages` do marco é campo, e não a coleção de Etapas do Edital: não se desce nele.
        f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/stages",
        f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/stages/id={ETAPA}/name",
        "/drawMethod/inventado",
    ],
)
def test_o_composto_desconhecido_continua_calado(caminho):
    """D-009, do outro lado: o campo composto só vira linha pelo caminho inteiro declarado."""
    assert alteracao_legivel(BASE, Alteracao(caminho)) is None
