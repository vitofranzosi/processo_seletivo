"""A projeção da publicação das inscrições — a conta da prévia, do ato e da divergência (148).

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
    """`ana Lima` e `Ana Lima` têm a mesma chave: o protocolo decide, e a ordem é estável."""
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS, inscricoes=INSCRICOES, resultados=None, perfis=PERFIS
    )

    nomes = [linha["candidato"] for linha in projecao.perfis[0]["listas"][0]["constam"]]
    protocolos = [linha["protocolo"] for linha in projecao.perfis[0]["listas"][0]["constam"]]
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

    matematica = projecao.perfis[0]["listas"][0]
    assert [linha["protocolo"] for linha in matematica["constam"]] == [
        "INS-2026-0004",
        "INS-2026-0001",
    ]
    assert matematica["nao_constam"] == 1
    assert projecao.indeferidas == 1
    indeferida = next(item for item in projecao.itens if item.situacao == dominio.INDEFERIDA)
    assert indeferida.resultado_id == resultado(2, False)["id"]


def test_perfil_sem_inscricao_aparece_vazio_e_nao_some():
    """Visto na validação: num Edital de dois Perfis, o que não recebeu inscrição sumia do ato."""
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS, inscricoes=INSCRICOES[:1], resultados=None, perfis=PERFIS
    )

    assert [grupo["perfil"] for grupo in projecao.perfis] == [
        "Professor de Matemática",
        "Tutor a distância",
    ]
    assert projecao.perfis[1]["listas"] == [
        {"lista": dominio.AMPLA_CONCORRENCIA, "constam": [], "nao_constam": 0}
    ]


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
        for lista in grupo["listas"]:
            for linha in lista["constam"]:
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


# ---------------------------------------------------------------------------
# A relação por lista — revisão de 12/11/2026 (D-011)
# ---------------------------------------------------------------------------

PCD = "00000000-0000-0000-0000-0000000000c1"
PPI = "00000000-0000-0000-0000-0000000000c2"
AMPLA_APONTADA = "00000000-0000-0000-0000-0000000000c3"
LISTAS = {PERFIL_A: [(PCD, "Pessoas com deficiência"), (PPI, "Pretos, pardos e indígenas")]}


def com_modalidade(numero, nome, modalidade, perfil=PERFIL_A):
    return {**inscricao(numero, nome, perfil), "modalidade_id": modalidade}


COTAS = [
    com_modalidade(1, "Ana Lima", None),
    com_modalidade(2, "Bruno Alves", PPI),
    com_modalidade(3, "Carla Dias", PCD),
    com_modalidade(4, "Davi Reis", PPI),
]


def _listas(grupo):
    return {
        lista["lista"]: [linha["protocolo"] for linha in lista["constam"]]
        for lista in grupo["listas"]
    }


def test_o_cotista_consta_na_ampla_e_na_lista_dele_e_e_uma_inscricao_so():
    """FR-5441, FR-5442 e FR-5444: duas vezes no grupo, uma vez nos itens e no total."""
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS,
        inscricoes=COTAS,
        resultados=None,
        perfis=PERFIS,
        listas=LISTAS,
    )

    assert _listas(projecao.perfis[0]) == {
        "Ampla concorrência": [
            "INS-2026-0001",
            "INS-2026-0002",
            "INS-2026-0003",
            "INS-2026-0004",
        ],
        "Pessoas com deficiência": ["INS-2026-0003"],
        "Pretos, pardos e indígenas": ["INS-2026-0002", "INS-2026-0004"],
    }
    assert projecao.total == 4
    assert sorted(item.inscricao_id for item in projecao.itens) == sorted(
        item["id"] for item in COTAS
    )


def test_as_listas_vem_na_ordem_dos_recortes_e_aparecem_mesmo_vazias():
    """FR-5440: a ampla primeiro, as reservadas na ordem do Perfil; sem cota, só a ampla."""
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS,
        inscricoes=COTAS[:1],
        resultados=None,
        perfis=PERFIS,
        listas=LISTAS,
    )

    matematica, tutor = projecao.perfis
    assert [lista["lista"] for lista in matematica["listas"]] == [
        "Ampla concorrência",
        "Pessoas com deficiência",
        "Pretos, pardos e indígenas",
    ]
    assert matematica["listas"][1]["constam"] == []
    assert [lista["lista"] for lista in tutor["listas"]] == ["Ampla concorrência"]


def test_modalidade_que_nao_e_lista_fica_so_na_ampla():
    """FR-5441 e SC-1711: a apontada como a ampla, e a que a versão não declara, não abrem lista."""
    inscricoes = [
        com_modalidade(1, "Ana Lima", AMPLA_APONTADA),
        com_modalidade(2, "Bruno Alves", "00000000-0000-0000-0000-0000000000ff"),
    ]

    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS,
        inscricoes=inscricoes,
        resultados=None,
        perfis=PERFIS[:1],
        listas=LISTAS,
    )

    assert _listas(projecao.perfis[0]) == {
        "Ampla concorrência": ["INS-2026-0001", "INS-2026-0002"],
        "Pessoas com deficiência": [],
        "Pretos, pardos e indígenas": [],
    }


def test_a_indeferida_e_contada_em_cada_lista_a_que_pertence():
    """FR-5443: o cotista indeferido conta na ampla e na lista dele, e não é nomeado em nenhuma."""
    resultados = {
        COTAS[0]["id"]: resultado(1, True),
        COTAS[1]["id"]: resultado(2, False),
        COTAS[2]["id"]: resultado(3, True),
        COTAS[3]["id"]: resultado(4, True),
    }

    projecao = dominio.projetar(
        natureza=dominio.PRELIMINAR,
        inscricoes=COTAS,
        resultados=resultados,
        perfis=PERFIS[:1],
        listas=LISTAS,
    )

    ampla, pcd, ppi = projecao.perfis[0]["listas"]
    assert (ampla["nao_constam"], pcd["nao_constam"], ppi["nao_constam"]) == (1, 0, 1)
    assert "INS-2026-0002" not in {
        linha["protocolo"] for lista in projecao.perfis[0]["listas"] for linha in lista["constam"]
    }
    assert projecao.indeferidas == 1


def test_a_linha_da_lista_reservada_tambem_tem_so_protocolo_e_nome():
    """SC-1702 revisto: a Modalidade aparece como lista, e nunca como coluna."""
    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS,
        inscricoes=COTAS,
        resultados=None,
        perfis=PERFIS[:1],
        listas=LISTAS,
    )

    for lista in projecao.perfis[0]["listas"]:
        for linha in lista["constam"]:
            assert set(linha) == {"protocolo", "candidato"}
    texto = canonical_bytes(projecao.perfis).decode()
    for proibido in (PCD, PPI, "modalidade"):
        assert proibido not in texto


ANTERIOR_A_REVISAO = {
    "cabecalho": {
        "titulo": "Relação de inscrições recebidas",
        "natureza": "RECEBIDAS",
        "processo": "Processo 2026",
        "edital": "Edital 01/2026",
        "etapa": "",
        "publicado_em": "2026-11-11T12:00:00+00:00",
        "signatario_nome": "",
        "signatario_cargo": "Diretoria",
        "signatario_ato_de_nomeacao": "",
        "unidade": {"sigla": "Cefor", "nome": "Cefor", "cabecalho": ["Cefor"]},
    },
    "rotulo_constam": "Inscrições recebidas",
    "rotulo_nao_constam": "",
    "perfis": [
        {
            "perfil": "Professor de Matemática",
            "constam": [{"protocolo": "INS-2026-0001", "candidato": "Ana Lima"}],
            "nao_constam": 0,
        }
    ],
    "total": 1,
}


def test_o_ato_anterior_a_revisao_e_lido_como_uma_lista_sem_nome():
    """FR-5447: o formato gravado em 11/11 continua legível, e não ganha "Ampla concorrência"."""
    grupos = dominio.grupos_publicados(ANTERIOR_A_REVISAO)

    assert grupos == [
        {
            "perfil": "Professor de Matemática",
            "listas": [
                {
                    "lista": "",
                    "constam": [{"protocolo": "INS-2026-0001", "candidato": "Ana Lima"}],
                    "nao_constam": 0,
                }
            ],
        }
    ]
    assert not dominio.tem_lista_reservada(grupos)


def test_o_documento_nomeia_as_listas_e_explica_a_repeticao():
    from processo_seletivo.divulgacao.infrastructure.documento_das_inscricoes import (
        render_inscricoes_pdf,
    )
    from tests.unit.publicacoes.test_pdf import texto_de

    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS,
        inscricoes=COTAS,
        resultados=None,
        perfis=PERFIS[:1],
        listas=LISTAS,
    )
    conteudo = dominio.conteudo_publico(
        projecao=projecao,
        natureza=dominio.RECEBIDAS,
        processo="Processo 2026",
        edital="Edital 01/2026",
        etapa="",
        prazo=None,
        publicado_em=datetime(2026, 11, 12, 12, tzinfo=UTC),
        signatario=SimpleNamespace(nome="", cargo="Diretoria", ato_de_nomeacao=""),
        unidade=SimpleNamespace(sigla="Cefor", nome="Cefor", cabecalho=("Cefor",)),
    )

    texto = texto_de(render_inscricoes_pdf(conteudo))

    for titulo in (
        "Ampla concorrência (4)",
        "Pessoas com deficiência (1)",
        "Pretos, pardos e indígenas (2)",
    ):
        assert titulo in texto
    assert "consta também na ampla concorrência" in " ".join(texto.split())


def test_o_documento_do_ato_anterior_a_revisao_nao_ganha_lista():
    from processo_seletivo.divulgacao.infrastructure.documento_das_inscricoes import (
        render_inscricoes_pdf,
    )
    from tests.unit.publicacoes.test_pdf import texto_de

    texto = texto_de(render_inscricoes_pdf(ANTERIOR_A_REVISAO))

    assert "Ana Lima" in texto
    assert "Ampla concorrência" not in texto
    assert "consta também" not in texto


def test_a_assinatura_da_previa_muda_com_a_versao_citada():
    """FR-5430 depois da D-011: as listas vêm da versão, e a confirmação tem de tê-la visto."""
    from processo_seletivo.divulgacao.application.inscricoes import Afericao, assinatura_da_previa

    projecao = dominio.projetar(
        natureza=dominio.RECEBIDAS, inscricoes=COTAS, resultados=None, perfis=PERFIS[:1]
    )

    def afericao(versao):
        return Afericao(
            natureza=dominio.RECEBIDAS,
            conteudo={},
            versao=SimpleNamespace(pk=versao),
            etapa=None,
            etapas=[],
            eventos=[],
            anterior=None,
            projecao=projecao,
        )

    assert assinatura_da_previa(afericao("v1")) == assinatura_da_previa(afericao("v1"))
    assert assinatura_da_previa(afericao("v1")) != assinatura_da_previa(afericao("v2"))
