"""As sete situações, ponto a ponto, sem banco (127, FR-4052, FR-4062, FR-4065 a FR-4076, SC-1235).

**Por que sem banco** (R-001). As regras do andamento recebem os fatos que as telas de ato já leem e
devolvem a célula. Testá-las puras deixa provar cada situação em cada família — inclusive S3 e P3,
que o banco de demonstração não tem — sem montar um certame por caso. A coerência com as telas, que
é o outro lado, está em `tests/interface/test_andamento_coerencia.py`.

A regra que atravessa todos os casos: **ausência de ato não é pendência**. Sem ato vigente, a célula
é *Depois*, *Aguarda*, *Impedido*, *Não se aplica* ou *Pendente* — e só *Pendente* manda agir.
"""

from datetime import UTC, datetime, timedelta

import pytest

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.divulgacao.domain import publicabilidade as p
from processo_seletivo.interface import andamento as a

AGORA = datetime(2026, 11, 6, 12, tzinfo=UTC)


def celula(situacao, **campos):
    return a.Celula(situacao, **campos)


# --- a Etapa ----------------------------------------------------------------------------------


def etapa(**fatos):
    base = {
        "nome": "Prova de Títulos",
        "expectativa": a.ESPERADA,
        "url": "/distribuicao",
        "participantes": 12,
        "carentes": 0,
        "sem_conclusao": 0,
        "prontas": 0,
        "consolidadas": 0,
        "reavaliacoes": 0,
        "com_faixa": True,
    }
    base.update(fatos)
    return a.situacoes_da_etapa(base)


def test_a_etapa_sem_efeito_nao_e_cobrada():
    """D-010: a Etapa que nada consome não vira providência."""
    resumo, providencias = etapa(expectativa=a.SEM_EFEITO, carentes=12)
    assert resumo.situacao == a.NAO_SE_APLICA
    assert resumo.nota == "sem efeito no GPS"
    assert providencias == []


def test_a_etapa_espera_o_fim_das_inscricoes():
    resumo, providencias = etapa(inscricoes_em_curso="As inscrições ficam abertas até 10/11")
    assert resumo.situacao == a.AGUARDA
    assert resumo.responsavel == ""
    assert providencias == [resumo]


def test_a_etapa_com_regra_insuficiente_e_impedida_e_quem_resolve_e_a_retificacao():
    resumo, providencias = etapa(bloqueio=("regra_insuficiente", "a decisória não elimina."))
    assert resumo.situacao == a.IMPEDIDO
    assert resumo.quem_resolve == a.RETIFICA
    assert resumo.razao == "a decisória não elimina"


def test_a_regra_insuficiente_nao_cala_a_avaliacao_de_quem_tem_inscricao_atribuida():
    _, providencias = etapa(
        bloqueio=("regra_de_combinacao_ausente", "duas avaliações."),
        minhas=3,
        url_da_mesa="/mesa",
    )
    assert [c.natureza for c in providencias] == [a.ETAPA, a.AVALIAR]


def test_a_etapa_governada_sem_corte_e_depois():
    resumo, providencias = etapa(governada=True, com_faixa=False, carentes=12)
    assert resumo.situacao == a.DEPOIS
    assert providencias == []


def test_o_corte_obsoleto_que_governa_impede_a_etapa():
    resumo, _ = etapa(bloqueio=("corte-obsoleto", "a faixa está para trás"))
    assert resumo.situacao == a.IMPEDIDO
    assert resumo.natureza == a.CORTE


def test_sem_participante_nao_se_aplica():
    resumo, providencias = etapa(participantes=0)
    assert resumo.situacao == a.NAO_SE_APLICA
    assert providencias == []


def test_distribuir_avaliar_e_consolidar_sao_tres_providencias():
    """FR-4062: uma Etapa pode pedir três coisas, de responsáveis diferentes."""
    _, providencias = etapa(carentes=4, sem_conclusao=9, prontas=2, consolidadas=1)
    assert [(c.natureza, c.responsavel, c.contagem) for c in providencias] == [
        (a.DISTRIBUIR, a.CONDUZ, 4),
        (a.AVALIAR, a.AVALIA, 5),
        (a.CONSOLIDAR, a.CONDUZ, 2),
    ]


def test_a_avaliacao_da_pessoa_e_separada_da_dos_outros_avaliadores():
    """FR-4063: "avaliar" é da pessoa só quando ela tem inscrição pendente na mesa."""
    _, providencias = etapa(sem_conclusao=12, minhas=8, url_da_mesa="/mesa")
    assert [(c.ato, c.url) for c in providencias] == [
        ("Avaliar 8 inscrições", "/mesa"),
        ("Avaliar 4 inscrições distribuídas", ""),
    ]


def test_a_reavaliacao_determinada_e_obsoleto():
    resumo, providencias = etapa(reavaliacoes=1, consolidadas=12)
    assert resumo.situacao == a.OBSOLETO
    assert providencias[0].natureza == a.REAVALIAR


def test_todas_consolidadas_e_feito():
    resumo, providencias = etapa(consolidadas=12)
    assert resumo.situacao == a.FEITO
    assert resumo.nota == "12 de 12 consolidadas"
    assert providencias == []


def test_no_perfil_a_etapa_feita_para_ele_e_feita_mesmo_com_trabalho_noutro():
    """D-013: a Etapa vale para o Edital; o Perfil só muda duas leituras."""
    do_edital, _ = etapa(sem_conclusao=3)
    assert a.situacao_da_etapa_no_perfil(do_edital, participantes=4, consolidadas=4).situacao == (
        a.FEITO
    )
    assert a.situacao_da_etapa_no_perfil(do_edital, participantes=0, consolidadas=0).situacao == (
        a.NAO_SE_APLICA
    )
    assert a.situacao_da_etapa_no_perfil(do_edital, participantes=4, consolidadas=1).situacao == (
        a.PENDENTE
    )


# --- o sorteio (S1, S2, S3) -------------------------------------------------------------------


def relacao(**fatos):
    base = {"congelada": False, "projetados": 3, "url": "/sorteio"}
    base.update(fatos)
    return a.situacao_da_relacao(base)


def test_a_relacao_pendente_e_congelar():
    assert relacao().situacao == a.PENDENTE
    assert relacao().ato == "Congelar a relação"


def test_a_relacao_sem_ninguem_nao_se_aplica():
    """A lista não constituída: congelar seria recusado (`relation_would_be_empty`)."""
    assert relacao(projetados=0).situacao == a.NAO_SE_APLICA


def test_a_relacao_espera_o_fim_das_inscricoes():
    assert relacao(inscricoes_em_curso="As inscrições ficam abertas").situacao == a.AGUARDA


def test_a_relacao_que_condenaria_o_sorteio_e_impedida():
    situacao = relacao(congelar_inviavel={"dia": AGORA.date()})
    assert situacao.situacao == a.IMPEDIDO
    assert situacao.quem_resolve == a.RETIFICA


def test_a_relacao_congelada_e_feita_e_a_condenada_e_obsoleta():
    assert relacao(congelada=True, participantes=3).situacao == a.FEITO
    assert relacao(congelada=True, diagnostico={"dia": AGORA}).situacao == a.OBSOLETO


def test_s3_a_relacao_espera_a_etapa_de_habilitacao():
    """S3: com Etapa de habilitação ainda não feita, congelar não é a vez."""
    pendente = celula(a.PENDENTE)
    assert relacao(habilitacao=pendente).situacao == a.DEPOIS
    assert relacao(habilitacao=celula(a.FEITO)).situacao == a.PENDENTE


def semente(**fatos):
    base = {"alguma_congelada": True, "observada": False, "agora": AGORA, "url": "/s"}
    base.update(fatos)
    return a.situacao_da_semente(base)


def test_a_semente_em_cada_situacao():
    assert semente(alguma_congelada=False).situacao == a.DEPOIS
    assert semente(observada=True).situacao == a.FEITO
    assert semente(recusa={"causa": "cadeia", "detalhe": "Esgotou."}).situacao == a.IMPEDIDO
    futura = semente(ocorre_em=AGORA + timedelta(days=2), referencia="6116")
    assert futura.situacao == a.AGUARDA
    assert futura.ate == AGORA + timedelta(days=2)
    assert semente(ocorre_em=AGORA - timedelta(days=1)).situacao == a.PENDENTE
    # Sem instante declarado o sistema não sabe se é cedo, e observar é o ato (contrato §5).
    assert semente().situacao == a.PENDENTE


def sorteio(relacao_, semente_, ordem=None, anulavel=True):
    return a.situacao_do_sorteio(
        {
            "relacao": relacao_,
            "semente": semente_,
            "ordem": ordem or {},
            "anulavel": anulavel,
            "url": "/s",
        }
    )


def test_o_sorteio_em_cada_situacao():
    feita, pendente = celula(a.FEITO), celula(a.PENDENTE)
    assert sorteio(celula(a.NAO_SE_APLICA), pendente).situacao == a.NAO_SE_APLICA
    assert sorteio(pendente, pendente).situacao == a.DEPOIS
    assert sorteio(feita, pendente).situacao == a.DEPOIS
    assert sorteio(celula(a.OBSOLETO), feita).situacao == a.IMPEDIDO
    assert sorteio(feita, feita).situacao == a.PENDENTE
    assert sorteio(feita, feita, {"estado": "feito"}).situacao == a.FEITO
    assert sorteio(feita, feita, {"estado": "obsoleto"}).situacao == a.OBSOLETO


def test_anular_sem_relacao_nova_e_ocorrencia_nova_e_impedido():
    """A tela só oferece anular com os dois insumos; o passo 1 é retificar."""
    feita = celula(a.FEITO)
    situacao = sorteio(feita, feita, {"estado": "obsoleto"}, anulavel=False)
    assert situacao.situacao == a.IMPEDIDO
    assert situacao.quem_resolve == a.RETIFICA


def test_a_ocorrencia_sem_instante_impede_sortear():
    """A tela pede a ocorrência válida, com o instante: sem ele, "Realizar" não aparece."""
    assert semente(sem_instante=True).situacao == a.IMPEDIDO


# --- a ordem por pontuação (P1, P2, P3) -------------------------------------------------------


def test_a_ordem_espera_as_etapas_que_le():
    """G-01 do estudo: nada recusa a ordem sem avaliação, e mesmo assim não é a vez."""
    situacao = a.situacao_da_ordem({"celula": {"estado": "falta"}, "faltam": ["Prova de Títulos"]})
    assert situacao.situacao == a.DEPOIS
    assert "Prova de Títulos" in situacao.razao


def test_a_ordem_em_cada_situacao():
    assert a.situacao_da_ordem({"celula": {"estado": "falta"}}).situacao == a.PENDENTE
    feita = a.situacao_da_ordem({"celula": {"estado": "feito", "nota": "ninguém concorreu"}})
    assert (feita.situacao, feita.nota) == (a.FEITO, "ninguém concorreu")
    assert a.situacao_da_ordem({"celula": {"estado": "obsoleto"}}).situacao == a.OBSOLETO
    assert a.situacao_da_ordem({"celula": {"estado": "nao_se_aplica"}}).situacao == (
        a.NAO_SE_APLICA
    )


def test_o_corte_depende_da_ordem():
    sem_ordem = a.situacao_do_corte({"celula": {"estado": "falta"}, "ordem": celula(a.DEPOIS)})
    assert sem_ordem.situacao == a.DEPOIS
    com_ordem = a.situacao_do_corte({"celula": {"estado": "falta"}, "ordem": celula(a.FEITO)})
    assert com_ordem.situacao == a.PENDENTE
    assert (
        a.situacao_do_corte({"celula": {"estado": "nao_se_aplica", "nota": "o marco não corta"}})
    ).situacao == a.NAO_SE_APLICA
    assert a.situacao_do_corte({"celula": {"estado": "obsoleto"}}).situacao == a.OBSOLETO


def test_p2_a_apuracao_espera_a_etapa_governada():
    """D-014: apurar antes da governada apuraria ninguém."""
    fatos = {"celula": {"estado": "falta"}, "ordem": celula(a.FEITO)}
    assert a.situacao_da_apuracao(fatos).situacao == a.PENDENTE
    governada = {**fatos, "governada": celula(a.PENDENTE), "nome_da_governada": "Entrevista"}
    situacao = a.situacao_da_apuracao(governada)
    assert situacao.situacao == a.DEPOIS
    assert "Entrevista" in situacao.razao
    feita = {**fatos, "governada": celula(a.FEITO)}
    assert a.situacao_da_apuracao(feita).situacao == a.PENDENTE


def test_no_marco_que_corta_a_apuracao_espera_o_corte():
    """D-018: sem faixa, a apuração contaria todas as vagas como faltando (o beco J-06)."""
    fatos = {"celula": {"estado": "falta"}, "ordem": celula(a.FEITO), "corte": celula(a.PENDENTE)}
    assert a.situacao_da_apuracao(fatos).situacao == a.DEPOIS
    fatos["corte"] = celula(a.FEITO)
    assert a.situacao_da_apuracao(fatos).situacao == a.PENDENTE
    fatos["corte"] = celula(a.NAO_SE_APLICA, nota="o marco não corta")
    assert a.situacao_da_apuracao(fatos).situacao == a.PENDENTE


def test_cr_sem_quadro_a_apuracao_nao_se_aplica():
    situacao = a.situacao_da_apuracao(
        {"celula": {"estado": "nao_se_aplica", "nota": "sem quadro de vagas publicado"}}
    )
    assert situacao.situacao == a.NAO_SE_APLICA


# --- o resultado (D-008, D-009) ---------------------------------------------------------------


def resultado(celula_, **fatos):
    return a.situacao_do_resultado({"celula": celula_, "ordem": celula(a.FEITO), **fatos})


def test_o_resultado_sem_ordem_e_depois_e_nao_falta():
    situacao = a.situacao_do_resultado(
        {"celula": {"estado": "falta", "nota": "falta a ordem"}, "ordem": celula(a.DEPOIS)}
    )
    assert situacao.situacao == a.DEPOIS


def test_o_resultado_nunca_divulgado_e_de_quem_publica():
    situacao = resultado({"estado": "falta"}, url_da_previa="/previa")
    assert (situacao.situacao, situacao.responsavel, situacao.url) == (
        a.PENDENTE,
        a.PUBLICA,
        "/previa",
    )


def test_o_preliminar_com_a_definitiva_publicavel_e_pendente():
    situacao = resultado(
        {"estado": "feito", "nota": "resultado preliminar", "natureza": "PRELIMINAR"},
        definitiva={"nivel": p.AVISO},
    )
    assert situacao.situacao == a.PENDENTE
    assert situacao.ato == "Publicar o resultado definitivo"


def test_o_preliminar_na_janela_recursal_aguarda():
    situacao = resultado(
        {"estado": "feito", "nota": "resultado preliminar", "natureza": "PRELIMINAR"},
        definitiva={"nivel": p.IMPEDIMENTO, "codigo": p.JANELA_ABERTA, "mensagem": "Aguarde."},
    )
    assert situacao.situacao == a.AGUARDA
    assert situacao.responsavel == ""


def test_com_a_ordem_obsoleta_divulgar_e_depois():
    """Item 1 da revisão: a prévia recusaria o ato sucedido ou desatualizado."""
    situacao = a.situacao_do_resultado({"celula": {"estado": "falta"}, "ordem": celula(a.OBSOLETO)})
    assert situacao.situacao == a.DEPOIS


def test_a_afericao_que_impede_a_publicacao_e_impedido():
    situacao = resultado(
        {"estado": "falta"},
        afericao={"nivel": p.IMPEDIMENTO, "codigo": p.CORTE_OBSOLETO, "mensagem": "Emita."},
    )
    assert situacao.situacao == a.IMPEDIDO
    assert situacao.quem_resolve == a.CONDUZ


def test_o_definitivo_e_feito_e_o_defasado_e_obsoleto():
    assert (
        resultado(
            {"estado": "feito", "nota": "resultado definitivo", "natureza": "DEFINITIVA"}
        ).situacao
        == a.FEITO
    )
    assert resultado({"estado": "obsoleto"}).situacao == a.OBSOLETO


# --- a convocação -----------------------------------------------------------------------------


def convocacao(**fatos):
    base = {"apuracao": celula(a.FEITO), "url": "/convocacao"}
    base.update(fatos)
    return a.situacoes_da_convocacao(base)


def test_a_convocacao_espera_a_apuracao():
    resumo, providencias = convocacao(apuracao=celula(a.DEPOIS))
    assert resumo.situacao == a.DEPOIS
    assert providencias == []
    resumo, _ = convocacao(apuracao=celula(a.OBSOLETO))
    assert resumo.situacao == a.DEPOIS, "a apuração obsoleta é que é a providência"


def test_a_convocacao_sem_forma_declarada_e_impedida():
    resumo, _ = convocacao(
        impedimento={"codigo": nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA, "detalhe": "Declare."}
    )
    assert resumo.situacao == a.IMPEDIDO
    assert resumo.quem_resolve == a.RETIFICA


def test_os_quatro_estados_da_convocacao():
    """Prazo não iniciado e vencido são de quem conduz; o prazo em curso espera o convocado."""
    _, providencias = convocacao(
        pendentes=1, vencidos=2, em_curso=3, ate=AGORA + timedelta(days=4), titulares=1
    )
    assert [(c.situacao, c.ato) for c in providencias] == [
        (a.PENDENTE, "Emitir 1 comunicação"),
        (a.PENDENTE, "Registrar o não atendimento de 2 convocações vencidas"),
        (a.PENDENTE, "Convocar 1 titular"),
        (a.AGUARDA, "Resposta de 3 convocações"),
    ]


def test_o_prazo_em_curso_diz_a_hora_e_concorda_com_o_numero():
    """Problema novo N-02 da reavaliação de 12/11/2026: "1 aguardam documentos", e um prazo que
    acaba no meio da tarde dito só pelo dia."""
    from django.utils import timezone

    ate = AGORA + timedelta(days=4)
    _, providencias = convocacao(em_curso=2, ate=ate, aguardando_documentos=1)
    [espera] = [c for c in providencias if c.situacao == a.AGUARDA]
    local = timezone.localtime(ate)
    assert espera.razao == (
        f"o prazo corre até {local:%d/%m/%Y} às {local:%H:%M}; 1 aguarda documentos"
    )
    _, providencias = convocacao(em_curso=3, ate=ate, aguardando_documentos=2)
    [espera] = [c for c in providencias if c.situacao == a.AGUARDA]
    assert espera.razao.endswith("; 2 aguardam documentos")


def test_a_forma_por_publicacao_registra_a_publicacao():
    _, providencias = convocacao(pendentes=2, por_publicacao=True)
    assert providencias[0].ato == "Registrar a publicação de 2 convocações"


def test_nova_chamada_e_faixa_seguinte_sao_condicionais():
    _, fila = convocacao(faltando=1, fila=3)
    assert fila[0].ato == "Chamar a próxima da fila" and fila[0].condicional
    _, faixa = convocacao(faltando=1, fila=0, esgotou=True, corte_vigente=True, com_quadro=True)
    assert faixa[0].ato == "Pedir a faixa seguinte" and faixa[0].natureza == a.APURACAO
    _, sem_corte = convocacao(
        faltando=1, fila=0, esgotou=True, corte_vigente=False, com_quadro=True
    )
    assert [c.ato for c in sem_corte] == ["Ocupar a vaga"], "D-018: sem corte, nada a ampliar"
    assert sem_corte[0].situacao == a.IMPEDIDO


def test_a_vaga_sem_quem_a_ocupe_da_lugar_ao_caminho_disponivel():
    """155, UX-602: no lugar de "Ocupar a vaga — impedida", a declaração, de quem conduz."""
    vaga = {
        "disponivel": True,
        "ato": "Declarar a vaga não preenchida",
        "quantidade": 1,
        "frase": "1 vaga da PPI sem quem a ocupe.",
        "impedimentos": [],
    }
    _, providencias = convocacao(
        faltando=1,
        fila=0,
        esgotou=True,
        corte_vigente=True,
        com_quadro=True,
        vaga=vaga,
        url_da_ocupacao="/ocupacao",
    )

    assert [(c.situacao, c.ato) for c in providencias] == [
        (a.PENDENTE, "Declarar a vaga não preenchida")
    ], "e não a faixa seguinte, que não alcançaria ninguém"
    assert providencias[0].url == "/ocupacao"
    assert providencias[0].razao == "1 vaga da PPI sem quem a ocupe"


def test_a_vaga_impedida_nomeia_o_impedimento_e_a_data():
    ate = AGORA + timedelta(days=3)
    vaga = {
        "disponivel": False,
        "ato": "Declarar a vaga não preenchida",
        "impedimentos": [{"frase": "o prazo de recurso ainda corre", "ate": ate}],
    }
    _, providencias = convocacao(faltando=1, fila=0, esgotou=True, corte_vigente=False, vaga=vaga)

    assert [(c.situacao, c.ato) for c in providencias] == [
        (a.IMPEDIDO, "Declarar a vaga não preenchida")
    ]
    assert providencias[0].razao == "o prazo de recurso ainda corre"
    assert providencias[0].ate == ate


def test_o_edital_silente_tem_um_ato_por_caminho():
    """155, FR-6321, UX-602: a declaração de não preenchida e, se a fase admite, a Retificação."""
    vaga = {
        "disponivel": True,
        "silente": True,
        "ato": "Declarar a vaga não preenchida",
        "quantidade": 1,
        "frase": "1 vaga da PPP sem quem a ocupe.",
        "impedimentos": [],
    }
    fatos = {
        "faltando": 1,
        "fila": 0,
        "esgotou": True,
        "corte_vigente": True,
        "com_quadro": True,
        "continuacao_admitida": False,
        "vaga": vaga,
        "url_da_ocupacao": "/ocupacao",
        "url_da_retificacao": "/retificar",
    }

    _, providencias = convocacao(**fatos, retificacao_admitida=True)
    _, encerrado = convocacao(**fatos, retificacao_admitida=False)

    assert [(c.situacao, c.ato, c.responsavel) for c in providencias] == [
        (a.PENDENTE, "Declarar a vaga não preenchida", a.CONDUZ),
        (a.PENDENTE, "Retificar o Edital para declarar a reversão", a.RETIFICA),
    ]
    assert providencias[1].url == "/retificar"
    assert [c.ato for c in encerrado] == ["Declarar a vaga não preenchida"]


def test_a_reversao_que_a_apuracao_nao_aplica_diz_a_regra_e_nenhum_ato():
    """155, FR-6303, FR-6327: onde o Edital declara a reversão e a vaga não sai, a frase diz por
    quê e o próximo passo, no lugar do "não há mais quem chamar" — sem ato a oferecer, e sem a faixa
    seguinte, que não alcançaria ninguém."""
    ate = AGORA + timedelta(days=3)
    vaga = {
        "disponivel": False,
        "reversao": True,
        "ato": "",
        "impedimentos": [{"frase": "o prazo de recurso ainda corre", "ate": ate}],
        "frase": "A reversão declarada é aplicada pela apuração desta lista.",
    }

    _, providencias = convocacao(
        faltando=1, fila=0, esgotou=True, corte_vigente=True, com_quadro=True, vaga=vaga
    )

    assert [(c.situacao, c.ato, c.razao) for c in providencias] == [
        (a.IMPEDIDO, "Ocupar a vaga", "A reversão declarada é aplicada pela apuração desta lista")
    ]
    assert providencias[0].ate == ate


def test_a_convocacao_espera_a_etapa_governada_mesmo_com_a_apuracao_feita():
    """FR-4070: a fila é de quem habilitou na governada; com ela aberta, nada a chamar."""
    resumo, providencias = convocacao(
        governada=celula(a.PENDENTE), nome_da_governada="Entrevista", titulares=2
    )
    assert resumo.situacao == a.DEPOIS and "Entrevista" in resumo.razao
    assert providencias == []


def test_a_apuracao_obsoleta_espera_a_governada():
    fatos = {"celula": {"estado": "obsoleto"}, "governada": celula(a.PENDENTE)}
    assert a.situacao_da_apuracao(fatos).situacao == a.DEPOIS


def test_documentos_a_conferir_e_desfecho_pronto():
    _, providencias = convocacao(conferir=2, decidir=1, url_da_conferencia="/conv")
    assert [(c.natureza, c.responsavel) for c in providencias] == [
        (a.CONVOCACAO, a.CONDUZ),
        (a.CONFERIR, a.CONFERE),
    ]


def test_sem_vaga_e_sem_convocacao_nao_se_aplica_e_tudo_desfechado_e_feito():
    resumo, _ = convocacao(faltando=0, convocadas=0)
    assert resumo.situacao == a.NAO_SE_APLICA
    resumo, _ = convocacao(faltando=0, convocadas=3, desfechadas=3)
    assert resumo.situacao == a.FEITO


@pytest.mark.parametrize("situacao", a.SITUACOES)
def test_toda_situacao_tem_palavra_e_sinal(situacao):
    """UX-230: palavra e sinal, nunca só cor."""
    assert a.ROTULOS[situacao] and a.SINAIS[situacao]


def test_com_o_processo_encerrado_ninguem_pratica():
    """D-021: todo comando da comissão recusa no Processo em estado final; o andamento se lê."""
    alcance = a.Alcance(
        conduz=True, consulta=True, publica=True, julga=True, retifica=True, ativo=False
    )
    assert not any(alcance.pratica(papel) for papel in (a.CONDUZ, a.PUBLICA, a.JULGA, a.RETIFICA))
    assert alcance.consulta, "a leitura continua"


# --- 133: o corte espera o prazo recursal, como recomendação (FR-4541 a FR-4546, D-003) -------

COM_RECURSO = {"id": "m", "appealWindow": {"admits": True, "durationDays": 3}}
FECHA = datetime(2026, 12, 13, 2, 59, tzinfo=UTC)


def test_sem_recurso_declarado_o_corte_nao_espera():
    assert a.espera_do_corte({"id": "m"}, divulgado=False, definitiva=None) is None


def test_sem_divulgacao_o_corte_espera_sem_data():
    espera = a.espera_do_corte(COM_RECURSO, divulgado=False, definitiva=None)
    assert espera["ate"] is None
    assert "divulgação" in espera["razao"]


@pytest.mark.parametrize("codigo", [p.JANELA_ABERTA, p.RECURSO_PENDENTE])
def test_com_o_prazo_ou_o_recurso_em_aberto_o_corte_espera(codigo):
    espera = a.espera_do_corte(
        COM_RECURSO,
        divulgado=True,
        definitiva={"nivel": p.IMPEDIMENTO, "codigo": codigo, "mensagem": "", "ate": FECHA},
    )
    assert espera["ate"] == FECHA
    assert "obsoleto" in espera["razao"]


def test_prazo_encerrado_sem_pendencia_e_sem_definitiva_o_corte_nao_espera():
    """D-003: a publicação da definitiva não é condição — o domínio não a exige para cortar."""
    assert a.espera_do_corte(COM_RECURSO, divulgado=True, definitiva={"nivel": p.AVISO}) is None


def test_o_corte_em_espera_e_recomendacao_e_nao_e_de_ninguem():
    espera = {"ate": FECHA, "razao": "Aguarde"}
    situacao = a.situacao_do_corte(
        {"celula": {"estado": "falta"}, "ordem": celula(a.FEITO), "espera": espera}
    )
    assert (situacao.situacao, situacao.recomendacao, situacao.responsavel) == (
        a.AGUARDA,
        True,
        "",
    )
    assert situacao.ate == FECHA
    assert situacao.ato == "Emitir o corte"


def test_o_corte_feito_ou_obsoleto_ignora_a_espera():
    espera = {"ate": FECHA, "razao": "Aguarde"}
    feito = a.situacao_do_corte({"celula": {"estado": "feito"}, "espera": espera})
    assert feito.situacao == a.FEITO
    obsoleto = a.situacao_do_corte({"celula": {"estado": "obsoleto"}, "espera": espera})
    assert obsoleto.situacao == a.OBSOLETO


# --- 133: a divulgação com ordem obsoleta (FR-4550, CV-04) ------------------------------------


def test_com_a_preliminar_feita_e_a_ordem_obsoleta_a_definitiva_e_depois():
    situacao = a.situacao_do_resultado(
        {
            "celula": {"estado": "feito", "nota": "resultado preliminar", "natureza": "PRELIMINAR"},
            "ordem": celula(a.OBSOLETO),
        }
    )
    assert situacao.situacao == a.DEPOIS
    assert "ordem vigente" in situacao.razao


def test_com_o_corte_obsoleto_a_definitiva_e_impedida_e_nao_pendente():
    """FR-4551, como a R-007 ajustou: a aferição já devolve o impedimento do corte obsoleto."""
    situacao = resultado(
        {"estado": "feito", "nota": "resultado preliminar", "natureza": "PRELIMINAR"},
        definitiva={
            "nivel": p.IMPEDIMENTO,
            "codigo": p.CORTE_OBSOLETO,
            "mensagem": "A faixa está para trás.",
        },
    )
    assert situacao.situacao == a.IMPEDIDO
    assert situacao.situacao != a.PENDENTE


def test_o_sorteio_com_recurso_declarado_tambem_espera():
    """A espera vale para todo marco com prazo recursal, inclusive o sorteio (FR-4541): o rito do
    Edital 35 — publicar a preliminar e cortar no mesmo dia — passa a ver o corte em espera.

    **Preso de propósito**: se a decisão for outra para o sorteio, é aqui que ela se diz (registrado
    na verificação da `133` como pergunta ao usuário).
    """
    sorteio = {
        "id": "s",
        "orderProduction": "POR_SORTEIO",
        "appealWindow": {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"},
    }
    espera = a.espera_do_corte(
        sorteio,
        divulgado=True,
        definitiva={
            "nivel": p.IMPEDIMENTO,
            "codigo": p.JANELA_ABERTA,
            "mensagem": "",
            "ate": FECHA,
        },
    )
    assert espera["ate"] == FECHA
