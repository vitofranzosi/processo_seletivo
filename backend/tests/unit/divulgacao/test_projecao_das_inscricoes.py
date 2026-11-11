"""A projeção da publicação das inscrições — a conta que a prévia, o ato e a divergência dividem (148).

Pura: nada de banco nem relógio. É aqui que se prende a fronteira pública (D-010) — o conteúdo que
vira bytes não tem como carregar motivo, modalidade nem dado pessoal, porque a função que o monta
nunca os recebe —, e a ordem que torna o ato determinístico (FR-5422).
"""

from datetime import UTC, datetime
from types import SimpleNamespace

from processo_seletivo.divulgacao.domain import inscricoes as dominio
from processo_seletivo.shared.canonical import canonical_bytes

PERFIL_A = "00000000-0000-0000-0000-00000000000a"
PERFIL_B = "00000000-0000-0000-0000-00000000000b"
PERFIS = [(PERFIL_A, "Professor de Matemática"), (PERFIL_B, "Tutor a distância")]


def inscricao(numero, nome, perfil=PERFIL_A):
    return {
        "id": f"00000000-0000-0000-0000-{numero:012d}",
        "perfil_id": perfil,
        "nome": nome,
        "protocolo": f"INS-2026-{numero:04d}",
    }


INSCRICOES = [
    inscricao(1, "Érica Souza"),
    inscricao(2, "ana Lima"),
    inscricao(3, "Bruno Alves", PERFIL_B),
    inscricao(4, "Ana Lima"),
]


def resultado(numero, habilitada):
    return {"id": f"10000000-0000-0000-0000-{numero:012d}", "habilitada": habilitada}


def test_a_relacao_de_recebidas_contempla_todas_e_nao_le_resultado():
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS, inscricoes=INSCRICOES, resultados=None, perfis=PERFIS
    )

    assert projecao.total == 4
    assert {item.situacao for item in projecao.itens} == {dominio.RECEBIDA}
    assert all(item.resultado_id is None for item in projecao.itens)
    assert [grupo["perfil"] for grupo in projecao.perfis] == [
        "Professor de Matemática",
        "Tutor a distância",
    ]


def test_a_ordem_ignora_caixa_e_acento_e_desempata_pelo_protocolo():
    """`ana Lima` e `Ana Lima` são a mesma chave de nome: o protocolo decide, e a ordem é estável."""
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS, inscricoes=INSCRICOES, resultados=None, perfis=PERFIS
    )

    nomes = [linha["candidato"] for linha in projecao.perfis[0]["constam"]]
    protocolos = [linha["protocolo"] for linha in projecao.perfis[0]["constam"]]
    assert nomes == ["ana Lima", "Ana Lima", "Érica Souza"]
    assert protocolos == ["INS-2026-0002", "INS-2026-0004", "INS-2026-0001"]


def test_o_preliminar_le_o_resultado_e_so_conta_a_indeferida():
    resultados = {
        INSCRICOES[0]["id"]: resultado(1, True),
        INSCRICOES[1]["id"]: resultado(2, False),
        INSCRICOES[2]["id"]: resultado(3, True),
        INSCRICOES[3]["id"]: resultado(4, True),
    }

    projecao = dominio.projetar(
        natureza=dominio.PRELIMINAR, inscricoes=INSCRICOES, resultados=resultados, perfis=PERFIS
    )

    matematica = projecao.perfis[0]
    assert [linha["protocolo"] for linha in matematica["constam"]] == [
        "INS-2026-0004",
        "INS-2026-0001",
    ]
    assert matematica["nao_constam"] == 1
    assert projecao.indeferidas == 1
    indeferida = next(item for item in projecao.itens if item.situacao == dominio.INDEFERIDA)
    assert indeferida.resultado_id == resultado(2, False)["id"]


def test_inscricao_sem_resultado_e_pendente_e_fica_fora():
    resultados = {INSCRICOES[0]["id"]: resultado(1, True)}

    projecao = dominio.projetar(
        natureza=dominio.PRELIMINAR, inscricoes=INSCRICOES, resultados=resultados, perfis=PERFIS
    )

    assert projecao.pendentes == 3
    assert projecao.total == 1


def test_a_homologacao_sem_analise_defere_todas():
    projecao = dominio.projetar(
        natureza=dominio.HOMOLOGACAO, inscricoes=INSCRICOES, resultados=None, perfis=PERFIS
    )

    assert {item.situacao for item in projecao.itens} == {dominio.DEFERIDA}
    assert projecao.pendentes == 0


def test_o_conteudo_publico_tem_so_protocolo_e_nome():
    """SC-1702 na fonte: as chaves de cada linha são exatamente duas."""
    resultados = {item["id"]: resultado(n, n != 2) for n, item in enumerate(INSCRICOES, start=1)}
    projecao = dominio.projetar(
        natureza=dominio.PRELIMINAR, inscricoes=INSCRICOES, resultados=resultados, perfis=PERFIS
    )
    conteudo = dominio.conteudo_publico(
        projecao=projecao,
        natureza=dominio.PRELIMINAR,
        processo="Processo 2026",
        edital="Edital 01/2026",
        etapa="Análise documental",
        prazo={"admite": True, "evento": "Recurso", "ate": "2026-12-01T23:59:00-03:00"},
        publicado_em=datetime(2026, 11, 11, 12, tzinfo=UTC),
        signatario=SimpleNamespace(nome="", cargo="Diretoria", ato_de_nomeacao=""),
        unidade=SimpleNamespace(sigla="Cefor", nome="Cefor", cabecalho=("Cefor",)),
    )

    for grupo in conteudo["perfis"]:
        for linha in grupo["constam"]:
            assert set(linha) == {"protocolo", "candidato"}
    texto = canonical_bytes(conteudo).decode()
    for proibido in ("resultado_id", "inscricao_id", "habilitada", "10000000-0000"):
        assert proibido not in texto
    assert conteudo["rotulo_nao_constam"] == "inscrições indeferidas"


def test_a_divergencia_conta_novas_saidas_e_mudancas():
    antes = [
        dominio.Item("a", dominio.DEFERIDA, "r1"),
        dominio.Item("b", dominio.INDEFERIDA, "r2"),
        dominio.Item("c", dominio.DEFERIDA, "r3"),
    ]
    agora = [
        dominio.Item("a", dominio.DEFERIDA, "r1"),
        dominio.Item("b", dominio.DEFERIDA, "r2b"),
        dominio.Item("d", dominio.DEFERIDA, "r4"),
    ]

    assert dominio.divergencia(antes, agora) == {"novas": 1, "sairam": 1, "mudadas": 1, "total": 3}
    assert dominio.divergencia(antes, antes)["total"] == 0


def test_a_ordem_das_naturezas_nao_regride():
    assert dominio.regride(dominio.HOMOLOGACAO, dominio.PRELIMINAR)
    assert dominio.regride(dominio.PRELIMINAR, dominio.RECEBIDAS)
    assert not dominio.regride(dominio.RECEBIDAS, dominio.HOMOLOGACAO)
    assert not dominio.regride(dominio.PRELIMINAR, dominio.PRELIMINAR)
    assert not dominio.regride(None, dominio.RECEBIDAS)


def test_so_etapa_decisoria_e_eliminatoria_e_analise():
    conteudo = {
        "stages": [
            {"id": "1", "order": 2, "forma": "DECISORIA", "eliminatory": True},
            {"id": "2", "order": 1, "forma": "DECISORIA", "eliminatory": False},
            {"id": "3", "order": 3, "forma": "PONTUADA", "eliminatory": True},
        ]
    }

    assert [etapa["id"] for etapa in dominio.etapas_de_analise(conteudo)] == ["1"]


def test_evento_de_recurso_so_com_termino_por_vir():
    agora = datetime(2026, 11, 11, 12, tzinfo=UTC)
    conteudo = {
        "schedule": [
            {"id": "p", "isRegistrationPeriod": True, "endAt": "2099-01-01T00:00:00Z"},
            {"id": "v", "description": "Vencido", "endAt": "2026-11-01T00:00:00Z"},
            {"id": "f", "description": "Futuro", "endAt": "2026-12-01T00:00:00Z"},
            {"id": "s", "description": "Sem término", "endAt": None},
            {
                "id": "c",
                "description": "Cancelado",
                "endAt": "2026-12-01T00:00:00Z",
                "status": "CANCELADO",
            },
        ]
    }

    assert [evento["id"] for evento in dominio.eventos_de_recurso(conteudo, agora)] == ["f"]
