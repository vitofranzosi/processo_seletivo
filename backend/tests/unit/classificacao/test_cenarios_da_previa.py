"""Os candidatos fictícios da prévia: determinísticos, e função só do que define a fronteira (094).

O que estes testes prendem é a promessa da D-003 revista: na população estável, os mesmos candidatos
e as mesmas notas enquanto o painel está aberto, qualquer que seja a regra digitada (FR-2205,
SC-849); nos casos-limite, a situação plantada sobre a fronteira de agora (FR-2206).
"""

import datetime

from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios

ESCRITA = {"id": "e1", "name": "Prova Escrita", "order": 1, "forma": "PONTUADA", "weight": "2"}
TITULOS = {"id": "e2", "name": "Prova de Títulos", "order": 2, "forma": "PONTUADA", "weight": "1"}
DOCUMENTOS = {"id": "e3", "name": "Análise documental", "order": 3, "forma": "DECISORIA"}
NASCIMENTO = {"id": "f1", "code": "NASC", "label": "Data de nascimento", "type": "DATA"}
SERVICO = {"id": "f2", "code": "SERV", "label": "Tempo de serviço", "type": "INTEIRO"}


def estavel(**fronteiras):
    argumentos = {"alvo": 10, "faixa": 15, "vagas": 10, **fronteiras}
    return cenarios.populacao_estavel(
        etapas_enumeradas=[ESCRITA, TITULOS],
        etapa_do_marco=TITULOS,
        fatos=[NASCIMENTO, SERVICO],
        **argumentos,
    )


def test_a_populacao_estavel_e_deterministica():
    assert estavel() == estavel()


def test_a_populacao_estavel_depende_so_das_fronteiras_da_montagem():
    """As fronteiras de montagem são argumento; a regra digitada nem chega aqui."""
    candidatos, _ = estavel()
    outra, _ = estavel(alvo=10, faixa=15, vagas=10)
    assert [c["notas"] for c in candidatos] == [c["notas"] for c in outra]
    diferente, _ = estavel(alvo=20, faixa=25, vagas=20)
    assert len(diferente) != len(candidatos)


def test_os_empates_plantados_ficam_na_ultima_vaga_e_na_ultima_posicao_da_faixa():
    candidatos, plantados = estavel()
    assert candidatos[9]["notas"] == candidatos[10]["notas"]
    assert candidatos[9]["fatos"] == candidatos[10]["fatos"]
    assert candidatos[14]["notas"] == candidatos[15]["notas"]
    assert any("10ª" in p for p in plantados)
    assert any("15ª" in p for p in plantados)


def test_vagas_e_faixa_vizinhas_nao_fundem_dois_empates():
    candidatos, plantados = estavel(alvo=10, faixa=11, vagas=10)
    assert sum("empate de dois" in p for p in plantados) == 1
    assert candidatos[10]["notas"] != candidatos[11]["notas"]


def test_o_trio_tem_as_mesmas_notas_e_so_os_fatos_o_separam():
    candidatos, _ = estavel()
    inicio = 2
    trio = candidatos[inicio : inicio + 3]
    assert trio[0]["notas"] == trio[1]["notas"] == trio[2]["notas"]
    assert trio[0]["fatos"]["f1"] < trio[1]["fatos"]["f1"] == trio[2]["fatos"]["f1"]
    assert trio[1]["fatos"]["f2"] != trio[2]["fatos"]["f2"]


def test_os_dois_sem_posicao_vem_no_fim():
    candidatos, _ = estavel()
    sem_nota, eliminado = candidatos[-2:]
    assert sem_nota["notas"]["e2"] is None
    assert eliminado["eliminado_em"] == "e2"


def test_o_teto_e_seiscentos():
    candidatos, _ = estavel(alvo=900, faixa=900, vagas=900)
    assert len(candidatos) == cenarios.TETO + 2


def test_a_nota_e_a_mesma_em_toda_etapa_com_nota():
    """É o que torna a ordem fora dos empates independente do peso (R-005)."""
    candidatos, _ = estavel()
    assert all(len(set(c["notas"].values()) - {None}) <= 1 for c in candidatos)


def test_os_inscritos_tem_a_forma_do_caminho_oficial_e_nenhum_e_real():
    candidatos, _ = estavel()
    inscritos = cenarios.inscritos(candidatos)
    assert {"inscricao_id", "protocolo", "nome", "identity_subject", "modalidade_id"} <= set(
        inscritos[0]
    )
    assert all(i["inscricao_id"].startswith("F") for i in inscritos)
    assert all(i["modalidade_id"] is None for i in inscritos)
    eliminado = inscritos[-1]
    assert any(r["consequencia"] == "ELIMINADA" for r in eliminado["resultados"])


def test_a_porta_decisoria_entra_como_resultado_sem_nota():
    candidatos, _ = cenarios.populacao_estavel(
        etapas_enumeradas=[ESCRITA, DOCUMENTOS],
        etapa_do_marco=DOCUMENTOS,
        fatos=[],
        alvo=5,
        faixa=5,
        vagas=5,
    )
    resultado = cenarios.inscritos(candidatos)[0]["resultados"]
    assert {"etapa_id": "e3", "pontuacao": None} == {
        k: resultado[-1][k] for k in ("etapa_id", "pontuacao")
    }


def caso(chave, **fronteiras):
    argumentos = {"alvo": 10, "suplentes": 5, "vagas": 10, "corta": True, **fronteiras}
    return cenarios.caso_limite(
        chave,
        etapas_enumeradas=[ESCRITA, TITULOS],
        etapa_do_marco=TITULOS,
        fatos=[NASCIMENTO, SERVICO],
        **argumentos,
    )


def test_o_caso_limite_acompanha_a_fronteira():
    com_cinco, onde = caso("empate_na_faixa")
    assert com_cinco[14]["notas"] == com_cinco[15]["notas"]
    assert "15ª" in onde
    sem_suplentes, onde = caso("empate_na_faixa", suplentes=0)
    assert sem_suplentes[9]["notas"] == sem_suplentes[10]["notas"]
    assert "10ª" in onde


def test_o_caso_do_valor_ausente_tira_a_data_de_um_dos_empatados():
    candidatos, _ = caso("valor_ausente")
    assert "f1" not in candidatos[6]["fatos"]
    assert candidatos[5]["notas"] == candidatos[6]["notas"]
    assert candidatos[1]["notas"]["e2"] is None
    assert candidatos[3]["eliminado_em"] == "e2"


def test_datas_e_inteiros_distintos_por_candidato():
    candidatos, _ = caso("sem_empate")
    datas = [c["fatos"]["f1"] for c in candidatos]
    assert len(set(datas)) == len(datas)
    assert all(isinstance(d, datetime.date) for d in datas)
