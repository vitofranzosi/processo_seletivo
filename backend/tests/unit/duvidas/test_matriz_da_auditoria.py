"""A matriz da auditoria de 12/10, nos casos pertinentes à Fase A (070, `FR-1450`, `SC-530`).

Cada caso diz no nome o `CA-` que prende, e roda sobre o conteúdo publicado do corpus (a camada de
conteúdo). Os casos que dependem do banco — versão no instante pelo fluxo real, mudança de versão,
desfecho — estão em `tests/integration/duvidas/`.

A tabela de cada caso, com o comportamento esperado e a fonte, está em
`doc/auditoria-assistente-de-duvidas-do-edital-2026-10-12.md`, §7.1.
"""

import copy

from processo_seletivo.duvidas.domain.estruturas import (
    DADO,
    DEPENDE_DA_LEITURA,
    FONTES_DIVERGENTES,
    NAO_INFORMA,
    RESPONDIDA,
    TEXTO,
)
from processo_seletivo.duvidas.domain.respostas import responder
from tests.fixtures.corpus import conteudo, contexto_do_corpus
from tests.unit.duvidas.conftest import em

DEPOIS_DAS_RETIFICACOES = em("2026-10-20T12:00:00-03:00")
SEM_CANAL = "Nem o Edital nem a implantação informam um canal para dúvidas."


def responder_no_corpus(nome, codigo, instante=DEPOIS_DAS_RETIFICACOES, **parametros):
    return responder(contexto_do_corpus(nome, instante), codigo, **parametros)


def dados(resposta):
    return {r.rotulo: r for r in resposta.referencias if r.natureza == DADO}


def textos(resposta):
    return [r.conteudo for r in resposta.referencias if r.natureza == TEXTO]


# ---- US1 -------------------------------------------------------------------------------------


def test_ca01_as_vagas_do_polo_retificado_e_a_origem_de_cada_linha():
    resposta = responder_no_corpus("91", "P-03", perfil="INF-BJN")
    cartoes = dados(resposta)
    assert resposta.tipo == RESPONDIDA
    assert cartoes["Vagas imediatas"].conteudo == "45"
    assert cartoes["Vagas da ampla concorrência"].conteudo == "33"
    assert cartoes["Vagas da modalidade PPI — Pretos, pardos e indígenas"].conteudo == "10"
    assert cartoes["Vagas da modalidade PcD — Pessoas com deficiência"].conteudo == "2"
    # O 45 e o 33 foram fixados pela Retificação; o 10 e o 2, pela publicação original.
    assert [o.publicacao_id for o in cartoes["Vagas imediatas"].origens] == ["91-pub2"]
    assert [o.publicacao_id for o in cartoes["Vagas da ampla concorrência"].origens] == ["91-pub2"]
    linha_ppi = cartoes["Vagas da modalidade PPI — Pretos, pardos e indígenas"]
    assert [o.publicacao_id for o in linha_ppi.origens] == ["91-pub1"]
    assert "45 vagas imediatas: 33 de ampla concorrência" in resposta.explicacao.conteudo


def test_ca03_a_ampla_concorrencia_e_a_linha_sem_modalidade_e_nunca_zero():
    resposta = responder_no_corpus("91", "P-03", perfil="INF-IUN")
    cartoes = dados(resposta)
    assert cartoes["Vagas da ampla concorrência"].conteudo == "28"
    # A modalidade "AC" está declarada no Perfil e não tem linha no quadro.
    assert not [rotulo for rotulo in cartoes if "modalidade AC" in rotulo]
    assert " 0 " not in f" {resposta.explicacao.conteudo} "


def test_ca04_e_ca05_a_inscricao_e_a_verificacao_saem_inteiras_com_a_modalidade():
    resposta = responder_no_corpus("91", "P-05", perfil="INF-BJN", modalidade="PPI")
    corpo = textos(resposta)
    assert any(
        "Os candidatos às vagas reservadas concorrem também às vagas de ampla concorrência" in t
        for t in corpo
    )
    assert any(
        "O candidato cuja autodeclaração for indeferida permanecerá apenas na lista de ampla "
        "concorrência." in t
        for t in corpo
    )


def test_ca06_os_documentos_a_mais_de_cada_modalidade_nao_se_misturam():
    def nomes(modalidade):
        resposta = responder_no_corpus("92", "P-05", perfil="TD-ADM", modalidade=modalidade)
        return {
            r.localizacao for r in resposta.referencias if r.localizacao.startswith("Documento")
        }

    comuns = nomes("nenhuma")
    assert nomes("PPIQ") - comuns == {"Documento exigido “Autodeclaração étnico-racial”"}
    assert nomes("PTT") - comuns == {"Documento exigido “Autodeclaração de identidade de gênero”"}
    assert nomes("PcD") - comuns == {"Documento exigido “Laudo médico”"}


def test_ca06_as_instrucoes_saem_literais():
    resposta = responder_no_corpus("92", "P-05", perfil="TD-ADM", modalidade="PcD")
    assert any(
        t.startswith("Emitido nos últimos 12 (doze) meses por médico especialista")
        for t in textos(resposta)
    )


def test_ca07_o_comprovante_de_residencia_so_no_tp01():
    def tem_comprovante(perfil):
        resposta = responder_no_corpus("92", "P-05", perfil=perfil, modalidade="nenhuma")
        return any("Comprovante de residência" in r.localizacao for r in resposta.referencias)

    assert tem_comprovante("TP-01")
    assert not tem_comprovante("TD-ADM")


def test_ca08_o_desempate_na_ordem_com_a_regra_da_ausencia_e_sem_fundamento_acrescentado():
    resposta = responder_no_corpus("92", "P-07", perfil="TD-ADM")
    criterios = [
        r.conteudo for r in resposta.referencias if r.rotulo.endswith("critério de desempate")
    ]
    assert criterios[0].startswith("menor valor declarado de Data de nascimento")
    assert criterios[1].startswith("maior valor declarado de Meses de experiência em tutoria")
    assert criterios[2].startswith("maior pontuação na Etapa Prova de títulos")
    assert all("fica por último" in c or "não se aplica" in c for c in criterios)
    assert "idoso" not in resposta.explicacao.conteudo.lower()


def test_ca09_o_corte_fixo_e_as_vagas_retificadas_sem_conciliar():
    selecao = responder_no_corpus("01", "P-07", perfil="DOC-INFO")
    corte = dados(selecao)
    assert corte["Quantidade que progride"].conteudo == "2"
    assert corte["Suplentes além dessa quantidade"].conteudo == "1"
    vagas = responder_no_corpus("01", "P-03", perfil="DOC-INFO")
    assert dados(vagas)["Vagas imediatas"].conteudo == "3"
    assert "corte" not in selecao.explicacao.conteudo.lower()


def test_ca16_a_secao_e_dita_pelo_titulo_e_nao_pelo_numero():
    resposta = responder_no_corpus("92", "P-08", perfil="TD-ADM")
    secao = [r for r in resposta.referencias if r.localizacao.startswith("Seção")]
    assert [r.localizacao for r in secao] == ["Seção “Dos Recursos”"]
    # O texto digitado "11.1" sai como está, porque é texto do Edital.
    assert secao[0].conteudo.startswith("11.1 Os recursos deverão ser interpostos")


# ---- US2 -------------------------------------------------------------------------------------


def test_ca02_o_termino_das_inscricoes_antes_e_depois_da_retificacao():
    antes = responder_no_corpus("91", "P-01", instante=em("2026-10-11T12:01:30-03:00"))
    depois = responder_no_corpus("91", "P-01")
    assert dados(antes)["Término"].conteudo == "30/10/2026, às 23h59"
    assert dados(depois)["Término"].conteudo == "04/11/2026, às 23h59"
    assert antes.versao.id != depois.versao.id
    assert [o.publicacao_id for o in dados(depois)["Término"].origens] == ["91-pub2"]


def test_ca17_a_retificacao_de_vigencia_futura_e_dita_e_nao_aplicada():
    antes = responder_no_corpus("01", "P-01", instante=em("2026-10-20T12:00:00-03:00"))
    termino = dados(antes)["Término"]
    assert termino.conteudo == "31/10/2026, às 09h43"
    assert [valor.valor for valor in termino.futuro] == ["10/11/2026, às 09h43"]
    aviso = next(a for a in antes.avisos if a.tipo == "RETIFICACAO_FUTURA")
    assert "A partir de 26/10/2026" in aviso.texto and "10/11/2026, às 09h43" in aviso.texto

    depois = responder_no_corpus("01", "P-01", instante=em("2026-10-27T12:00:00-03:00"))
    assert dados(depois)["Término"].conteudo == "10/11/2026, às 09h43"
    assert not dados(depois)["Término"].futuro
    assert [o.publicacao_id for o in dados(depois)["Término"].origens] == ["01-pub3"]


def test_ca28_as_inscricoes_abertas_no_instante():
    resposta = responder_no_corpus("91", "P-01")
    assert resposta.explicacao.conteudo == "As inscrições estão abertas até 04/11/2026, às 23h59."
    assert resposta.situacao.periodo == "aberto"
    assert resposta.situacao.instante == DEPOIS_DAS_RETIFICACOES


def test_ca18_a_versao_anterior_informada_gera_o_aviso_de_mudanca():
    contexto = contexto_do_corpus("91", DEPOIS_DAS_RETIFICACOES, versao_anterior="91-v1")
    resposta = responder(contexto, "P-03", perfil="INF-BJN")
    assert resposta.mudanca is not None
    assert [ato.publicacao_id for ato in resposta.mudanca.atos] == ["91-pub2"]
    mesma = responder(
        contexto_do_corpus("91", DEPOIS_DAS_RETIFICACOES, versao_anterior="91-v2"),
        "P-03",
        perfil="INF-BJN",
    )
    assert mesma.mudanca is None


def test_o_desfecho_do_edital_prevalece_sobre_o_periodo():
    from processo_seletivo.duvidas.domain.estruturas import Desfecho

    cancelado = Desfecho("EDITAL", "CANCELADO", em("2026-10-15T10:00:00-03:00"), True)
    resposta = responder(
        contexto_do_corpus("91", DEPOIS_DAS_RETIFICACOES, desfecho=cancelado), "P-01"
    )
    assert resposta.explicacao.conteudo.startswith("As inscrições não estão em curso")
    assert any(
        a.tipo == "DESFECHO" and "cancelado em 15/10/2026" in a.texto for a in resposta.avisos
    )


# ---- US3 -------------------------------------------------------------------------------------


def _sintetico(nome, publicacao, mudar):
    publicado = copy.deepcopy(conteudo(nome, publicacao))
    mudar(publicado)
    return contexto_do_corpus(nome, DEPOIS_DAS_RETIFICACOES, conteudo_substituto=publicado)


def test_ca10_tec_lab_depende_da_leitura_pelo_evento_que_fala_de_recurso():
    resposta = responder_no_corpus("01", "P-08", perfil="TEC-LAB")
    assert resposta.tipo == DEPENDE_DA_LEITURA
    assert "Resultado final e abertura do prazo recursal." in textos(resposta)
    assert "não cabe" not in resposta.explicacao.conteudo
    # O corpus não tem canal: o encaminhamento diz que não há, e não manda a atendimento nenhum
    # (`FR-1441`; o caso com canal está em `test_casos_da_revisao.py`).
    assert SEM_CANAL in resposta.explicacao.conteudo


def test_ca10_ausencia_pura_e_o_edital_nao_informa_e_nunca_nao_cabe():
    def sem_recurso(publicado):
        for evento in publicado["schedule"]:
            evento["description"] = evento["description"].replace("abertura do prazo recursal", "")

    contexto = _sintetico("01", 3, sem_recurso)
    resposta = responder(contexto, "P-08", perfil="TEC-LAB")
    assert resposta.tipo == NAO_INFORMA
    assert "não cabe" not in resposta.explicacao.conteudo.replace("não caiba", "")
    assert "Isso não quer dizer que não caiba" in resposta.explicacao.conteudo
    assert SEM_CANAL in resposta.explicacao.conteudo


def test_negativa_declarada_e_dado_e_dita_como_o_edital_a_declara():
    def nega(publicado):
        perfil = next(p for p in publicado["profiles"] if p["code"] == "TEC-LAB")
        perfil["classificationMilestones"][0]["appealWindow"] = {
            "admits": False,
            "durationDays": None,
            "unit": "DIAS_CORRIDOS",
        }
        for evento in publicado["schedule"]:
            evento["description"] = evento["description"].replace("abertura do prazo recursal", "")

    resposta = responder(_sintetico("01", 3, nega), "P-08", perfil="TEC-LAB")
    assert resposta.tipo == RESPONDIDA
    assert "O Edital declara que não cabe recurso" in resposta.explicacao.conteudo
    assert any(r.conteudo == "não cabe, como o Edital declara" for r in resposta.referencias)


def test_ca11_tres_fontes_inteiras_e_nenhuma_escolhida():
    resposta = responder_no_corpus("91", "P-08", perfil="INF-BJN")
    assert resposta.tipo == DEPENDE_DA_LEITURA
    rotulos = [r.rotulo for r in resposta.referencias if r.natureza == DADO]
    assert "Recurso contra o resultado de “Classificação por sorteio eletrônico”" in rotulos
    assert any(
        t.startswith("Caberá recurso contra o resultado preliminar da análise documental")
        for t in textos(resposta)
    )
    assert "Prazo para interposição de recurso" in textos(resposta)
    assert "não os concilia" in resposta.explicacao.conteudo


def test_ca12_o_texto_do_sorteio_sai_inteiro_e_a_explicacao_nao_afirma_o_que_o_sistema_fara():
    resposta = responder_no_corpus("91", "P-09", perfil="INF-BJN")
    assert any(t.startswith("Havendo mais inscritos que vagas") for t in textos(resposta))
    assert "havendo" not in resposta.explicacao.conteudo.lower()


def test_ca13_o_detalhe_da_prova_de_titulos_esta_no_anexo_iv():
    resposta = responder_no_corpus("92", "P-07", perfil="TD-ADM")
    aviso = next(a for a in resposta.avisos if a.tipo == "DETALHE_EM_ANEXO")
    assert "ANEXO IV — FICHA DE AVALIAÇÃO DA PROVA DE TÍTULOS" in aviso.texto
    assert "que esta consulta não lê" in aviso.texto
    assert [link.rotulo for link in aviso.links] == [
        "ANEXO IV — FICHA DE AVALIAÇÃO DA PROVA DE TÍTULOS"
    ]
    assert "pontos" not in resposta.explicacao.conteudo


def test_ca14_a_isencao_de_taxa_sai_no_texto_do_evento_e_a_explicacao_nao_fala_de_taxa():
    resposta = responder_no_corpus("01", "P-01")
    assert "Inscrições pelo sistema, com isenção de taxa até o 5º dia." in textos(resposta)
    assert "taxa" not in resposta.explicacao.conteudo


def test_ca15_a_secao_retirada_nao_aparece_e_nada_se_afirma_da_ausencia():
    resposta = responder_no_corpus("92", "P-05", perfil="TD-ADM", modalidade="PcD")
    assert not [t for t in textos(resposta) if "atendimento especializado" in t]
    assert "atendimento" not in resposta.explicacao.conteudo.lower()


# ---- US4 -------------------------------------------------------------------------------------


def test_ca27_o_canal_do_edital_no_paragrafo_literal():
    no_91 = responder_no_corpus("91", "P-11")
    assert no_91.tipo == RESPONDIDA
    assert "selecao.demo@exemplo.ifes.edu.br" in no_91.explicacao.conteudo
    assert any("exclusivamente pelo e-mail" in t for t in textos(no_91))

    no_92 = responder_no_corpus("92", "P-11")
    assert "selecao.uab.demo@exemplo.ifes.edu.br" in no_92.explicacao.conteudo
    assert any(t.startswith("15.3 Dúvidas poderão ser enviadas") for t in textos(no_92))


def test_ca27_dois_canais_nao_sao_escolhidos():
    def dois(publicado):
        secao = next(s for s in publicado["sections"] if s["key"] == "disposicoes-finais")
        secao["content"] += "\nDúvidas sobre a matrícula: matricula.demo@exemplo.ifes.edu.br."

    resposta = responder(_sintetico("92", 2, dois), "P-11")
    assert resposta.tipo == FONTES_DIVERGENTES
    assert "não escolhe" in resposta.explicacao.conteudo
    assert len([t for t in textos(resposta) if "@" in t]) == 2
