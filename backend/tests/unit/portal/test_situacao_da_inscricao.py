"""A situação da inscrição, degrau por degrau, sem banco (063, D-002).

A precedência é a regra da feature, e por isso cada degrau tem caso próprio **e** cada par de
degraus vizinhos tem o caso em que os dois se aplicam e o de cima vence. Os objetos são montados em
memória: a função é pura, e um teste que precisasse do banco para provar uma tabela de precedência
estaria provando outra coisa.
"""

import inspect
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
from processo_seletivo.portal import situacao
from processo_seletivo.recursos.application.selectors import (
    AGUARDANDO_JULGAMENTO,
    DECIDIDO,
)

INSTANTE = datetime(2026, 9, 23, 13, 0, tzinfo=UTC)
PPI = uuid.uuid4()

PERFIL = {
    "id": "perfil",
    "competitionModalities": [{"id": str(PPI), "name": "Pessoas pretas, pardas e indígenas"}],
    "reserveType": "LIMITED",
    "reserveLimit": 9,
    "callForm": "INDIVIDUAL_MESSAGE",
}


def inscricao():
    return SimpleNamespace(id=uuid.uuid4(), submitted_at=INSTANTE)


def cartao(
    *,
    lista_id=None,
    lista="Ampla concorrência",
    posicao=8,
    natureza="DEFINITIVA",
    classificada=True,
    motivo="",
    marco="Classificação final",
    codigo="M1",
):
    rotulo = {"DEFINITIVA": "Resultado definitivo", "PRELIMINAR": "Resultado preliminar"}
    return {
        "publicacao": SimpleNamespace(
            id=uuid.uuid4(),
            lista_id=lista_id,
            natureza=natureza,
            publicado_em=INSTANTE,
            get_natureza_display=lambda: rotulo[natureza],
        ),
        "marco": marco,
        "marco_codigo": codigo,
        "natureza_rotulo": rotulo[natureza],
        "lista": lista,
        "lista_id": lista_id,
        "classificada": classificada,
        "posicao": posicao if classificada else None,
        "compartilhada": False,
        "pontuacao": "7,50" if classificada else "",
        "motivo": motivo,
    }


def convocacao(*, lista_id=None, vencimento=INSTANTE, especie="Para vaga inicial"):
    return SimpleNamespace(
        id=uuid.uuid4(),
        lista_id=lista_id,
        chamada=1,
        vencimento=vencimento,
        criado_em=INSTANTE,
        get_especie_display=lambda: especie,
    )


def desfecho(especie):
    return SimpleNamespace(
        especie=especie,
        fundamento="Registro da comissão.",
        registrado_em=INSTANTE,
        get_especie_display=lambda: especie,
    )


def eliminada(etapa="Prova didática", motivo="pontuação inferior à nota mínima"):
    return {"id": uuid.uuid4(), "etapa": etapa, "habilitada": False, "motivo": motivo}


def calcular(**kwargs):
    argumentos = {
        "inscricao": inscricao(),
        "perfil": PERFIL,
        "cartoes": [],
        "resultados_das_etapas": [],
        "convocacao": None,
        "desfecho": None,
        "estado": None,
        "requerimento": "",
        "recorriveis": [],
        "recursos": [],
    }
    argumentos.update(kwargs)
    return situacao.situacao_da_inscricao(**argumentos)


def textos(resultado):
    return " ".join(linha.texto for linha in resultado.porque)


EM_CURSO = convocacao_nomes.CONVOCADO_PRAZO_EM_CURSO


class TestCadaDegrau:
    def test_desfecho_aceite_e_vaga_aceita(self):
        resultado = calcular(
            convocacao=convocacao(),
            desfecho=desfecho(convocacao_nomes.ACEITE),
            estado=convocacao_nomes.DESFECHADO,
        )
        assert resultado.rotulo == "Vaga aceita"
        assert "Registro da comissão." in textos(resultado)
        assert resultado.o_que_fazer.principal == situacao.NADA_POR_ENQUANTO
        assert not resultado.provisoria

    @pytest.mark.parametrize("especie", convocacao_nomes.ESPECIES_DE_DESFECHO)
    def test_cada_desfecho_tem_o_rotulo_da_tabela(self, especie):
        resultado = calcular(convocacao=convocacao(), desfecho=desfecho(especie))
        assert resultado.rotulo == situacao.DESFECHOS[especie]
        assert resultado.codigo == f"DESFECHO_{especie}"

    def test_convocacao_aberta_e_convocado(self):
        resultado = calcular(convocacao=convocacao(), estado=EM_CURSO)
        assert resultado.codigo == situacao.CONVOCADO
        assert resultado.provisoria
        assert "pela lista Ampla concorrência" in textos(resultado)
        assert "1ª chamada" in textos(resultado)

    def test_eliminado_em_etapa(self):
        resultado = calcular(resultados_das_etapas=[eliminada()])
        assert resultado.rotulo == "Eliminado"
        assert "Prova didática" in textos(resultado)
        assert "nota mínima" in textos(resultado)

    def test_classificado_em_definitiva_aguarda_chamada(self):
        resultado = calcular(cartoes=[cartao()])
        assert resultado.rotulo == "Aguardando chamada"
        assert resultado.provisoria
        assert resultado.o_que_fazer.consequencia == situacao.NOVAS_CHAMADAS

    def test_classificado_so_em_preliminar_aguarda_definitivo(self):
        resultado = calcular(cartoes=[cartao(natureza="PRELIMINAR")])
        assert resultado.rotulo == "Aguardando resultado definitivo"
        assert situacao.PRELIMINAR_PODE_MUDAR in textos(resultado)
        assert resultado.o_que_fazer.consequencia == ""

    def test_sem_posicao_em_todas_e_nao_classificado(self):
        resultado = calcular(
            cartoes=[cartao(classificada=False, motivo="não atingiu a nota mínima")]
        )
        assert resultado.rotulo == "Não classificado"
        assert "não atingiu a nota mínima" in textos(resultado)

    def test_nada_divulgado_e_inscricao_enviada(self):
        resultado = calcular()
        assert resultado.rotulo == "Inscrição enviada"
        assert "23/09/2026" in textos(resultado)
        assert resultado.o_que_fazer.principal == situacao.RESULTADO_CONFORME_O_EDITAL


class TestDegrausVizinhos:
    """Os dois se aplicam, e o de cima vence."""

    def test_desfecho_vence_convocacao(self):
        resultado = calcular(
            convocacao=convocacao(),
            desfecho=desfecho(convocacao_nomes.NAO_ATENDIMENTO),
            estado=convocacao_nomes.DESFECHADO,
        )
        assert resultado.rotulo == "Convocação não atendida"

    def test_convocacao_vence_eliminacao(self):
        """A convocação para regularizar existe justamente depois de um indeferimento."""
        resultado = calcular(
            convocacao=convocacao(especie="Para regularizar o indeferimento"),
            estado=EM_CURSO,
            resultados_das_etapas=[eliminada()],
        )
        assert resultado.codigo == situacao.CONVOCADO

    def test_eliminacao_vence_classificacao(self):
        resultado = calcular(resultados_das_etapas=[eliminada()], cartoes=[cartao()])
        assert resultado.codigo == situacao.ELIMINADO

    def test_definitiva_vence_preliminar(self):
        resultado = calcular(
            cartoes=[cartao(), cartao(lista_id=PPI, lista="PPI", natureza="PRELIMINAR")]
        )
        assert resultado.codigo == situacao.AGUARDANDO_CHAMADA

    def test_preliminar_classificada_vence_sem_posicao(self):
        resultado = calcular(
            cartoes=[
                cartao(natureza="PRELIMINAR"),
                cartao(lista_id=PPI, lista="PPI", classificada=False),
            ]
        )
        assert resultado.codigo == situacao.AGUARDANDO_DEFINITIVO

    def test_sem_posicao_vence_inscricao_enviada(self):
        resultado = calcular(cartoes=[cartao(classificada=False)])
        assert resultado.codigo == situacao.NAO_CLASSIFICADO


class TestDuasListas:
    def test_cada_lista_com_a_sua_posicao_oficial(self):
        """O caso do Edital 72/2026: 8º na ampla, 2º na PPI, e nenhuma "melhor classificação"."""
        resultado = calcular(
            cartoes=[
                cartao(posicao=8),
                cartao(lista_id=PPI, lista="Pessoas pretas, pardas e indígenas", posicao=2),
            ]
        )
        texto = textos(resultado)
        assert "Ampla concorrência: 8º lugar" in texto
        assert "Pessoas pretas, pardas e indígenas: 2º lugar" in texto
        assert situacao.MAIS_DE_UMA_LISTA in texto

    def test_classificada_numa_lista_e_sem_posicao_noutra(self):
        resultado = calcular(
            cartoes=[
                cartao(posicao=3),
                cartao(lista_id=PPI, lista="PPI", classificada=False, motivo="sem nota"),
            ]
        )
        assert resultado.codigo == situacao.AGUARDANDO_CHAMADA
        assert "Ampla concorrência: 3º lugar" in textos(resultado)
        assert "PPI: sem posição" in textos(resultado)

    def test_uma_lista_so_nao_ganha_a_frase_das_listas(self):
        assert situacao.MAIS_DE_UMA_LISTA not in textos(calcular(cartoes=[cartao()]))


class TestConsequenciaDoConvocado:
    """Nenhuma perda automática: a frase só existe com o prazo correndo (FR-1177, FR-274)."""

    def test_prazo_em_curso_com_vencimento(self):
        acao = calcular(convocacao=convocacao(), estado=EM_CURSO).o_que_fazer
        assert acao.prazo == INSTANTE
        assert acao.consequencia == situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO
        assert acao.aviso_de_prazo == ""

    def test_sem_envio_ou_com_falha_o_prazo_nao_comecou(self):
        """O envio com falha não conta (`envio_de` ignora a falha), e chega como não iniciado."""
        acao = calcular(
            convocacao=convocacao(), estado=convocacao_nomes.CONVOCADO_PRAZO_NAO_INICIADO
        ).o_que_fazer
        assert acao.aviso_de_prazo == situacao.PRAZO_NAO_INICIADO
        assert acao.consequencia == ""

    def test_vencimento_decorrido_sem_desfecho_continua_convocado(self):
        resultado = calcular(
            convocacao=convocacao(), estado=convocacao_nomes.CONVOCADO_VENCIMENTO_DECORRIDO
        )
        assert resultado.codigo == situacao.CONVOCADO
        acao = resultado.o_que_fazer
        assert "terminou em 23/09/2026" in acao.aviso_de_prazo
        assert "ainda não foi registrado" in acao.aviso_de_prazo
        assert acao.consequencia == ""
        assert "perd" not in acao.aviso_de_prazo

    def test_sem_vencimento_nenhuma_consequencia(self):
        acao = calcular(convocacao=convocacao(vencimento=None), estado=EM_CURSO).o_que_fazer
        assert acao.consequencia == ""
        assert acao.prazo is None

    def test_nenhuma_frase_de_consequencia_diz_perder(self):
        assert all(
            "perder" not in frase and "perderá" not in frase for frase in situacao.CONSEQUENCIAS
        )


class TestAcaoDoConvocado:
    def test_requerimento_disponivel(self):
        acao = calcular(
            convocacao=convocacao(), estado=EM_CURSO, requerimento="preencher"
        ).o_que_fazer
        assert acao.principal == situacao.PREENCHER_REQUERIMENTO
        assert "/requerimento" in acao.link

    def test_requerimento_enviado(self):
        acao = calcular(
            convocacao=convocacao(), estado=EM_CURSO, requerimento="conferir"
        ).o_que_fazer
        assert acao.principal == situacao.REQUERIMENTO_ENVIADO

    def test_sem_requerimento_a_instrucao_neutra(self):
        acao = calcular(convocacao=convocacao(), estado=EM_CURSO).o_que_fazer
        assert acao.principal == situacao.SIGA_AS_INSTRUCOES
        assert "atrícula" not in acao.principal
        assert "contrata" not in acao.principal

    def test_lista_da_convocacao_pela_modalidade_do_perfil(self):
        resultado = calcular(convocacao=convocacao(lista_id=PPI), estado=EM_CURSO)
        assert "pela lista Pessoas pretas, pardas e indígenas" in textos(resultado)

    def test_lista_retirada_do_perfil_usa_o_nome_do_cartao(self):
        retirada = uuid.uuid4()
        resultado = calcular(
            convocacao=convocacao(lista_id=retirada),
            estado=EM_CURSO,
            cartoes=[cartao(lista_id=retirada, lista="Pessoas com deficiência")],
        )
        assert "pela lista Pessoas com deficiência" in textos(resultado)


class TestCanalEReserva:
    def test_publicacao(self):
        frase = situacao.frase_do_canal({"callForm": "PUBLICATION"})
        assert "por publicação" in frase
        assert "mensagem" not in frase
        assert "e-mail" not in frase

    def test_sem_forma_declarada_nenhum_canal(self):
        assert situacao.frase_do_canal({"callForm": None}) == ""
        assert situacao.frase_do_canal(None) == ""

    @pytest.mark.parametrize(
        ("tipo", "limite", "esperado"),
        [
            ("LIMITED", 9, "de até 9 pessoas"),
            ("LIMITED", 1, "de até 1 pessoa para"),
            ("UNLIMITED", None, "sem limite de pessoas"),
            ("NONE", None, ""),
        ],
    )
    def test_reserva_do_edital(self, tipo, limite, esperado):
        frase = situacao.frase_da_reserva({"reserveType": tipo, "reserveLimit": limite})
        assert (esperado in frase) if esperado else frase == ""
        assert "você está" not in frase

    def test_perfil_retirado_nenhuma_frase(self):
        resultado = calcular(perfil=None, cartoes=[cartao()])
        assert resultado.o_que_fazer.canal == ""
        assert resultado.o_que_fazer.reserva == ""

    def test_aguardando_chamada_leva_canal_e_reserva(self):
        acao = calcular(cartoes=[cartao()]).o_que_fazer
        assert "mensagem individual" in acao.canal
        assert "de até 9 pessoas" in acao.reserva


class TestRecurso:
    def test_recurso_em_analise_nao_muda_a_situacao(self):
        peca = {
            "recurso": SimpleNamespace(id=uuid.uuid4()),
            "protocolo": "REC-2026-0001",
            "situacao": AGUARDANDO_JULGAMENTO,
            "situacao_rotulo": "Admitido, aguardando julgamento",
        }
        resultado = calcular(cartoes=[cartao()], recursos=[peca])
        assert resultado.codigo == situacao.AGUARDANDO_CHAMADA
        linha = resultado.porque[-1]
        assert "REC-2026-0001 está em análise" in linha.texto
        assert linha.link

    def test_recurso_julgado_nao_entra_no_porque(self):
        peca = {
            "recurso": SimpleNamespace(id=uuid.uuid4()),
            "protocolo": "REC-2026-0002",
            "situacao": DECIDIDO,
            "situacao_rotulo": "Julgado",
        }
        assert "REC-2026-0002" not in textos(calcular(cartoes=[cartao()], recursos=[peca]))

    def test_prazo_aberto_vira_acao_opcional(self):
        alvo = {
            "tipo": "publicacao",
            "id": 1,
            "rotulo": "Classificação final",
            "fecha_em": INSTANTE,
        }
        acao = calcular(cartoes=[cartao()], recorriveis=[alvo]).o_que_fazer
        assert acao.principal == situacao.NADA_POR_ENQUANTO
        assert acao.recurso == ({"rotulo": "Classificação final", "fecha_em": INSTANTE},)


class TestRotulosQueNaoSeConfundem:
    """Achados da revisão de código da 063."""

    def test_o_recurso_de_cada_lista_diz_a_lista(self):
        """Duas listas no mesmo marco davam duas linhas "Classificação final" idênticas."""
        ampla = cartao(posicao=8)
        ppi = cartao(lista_id=PPI, lista="Pessoas pretas, pardas e indígenas", posicao=2)
        recorriveis = [
            {
                "tipo": "publicacao",
                "id": c["publicacao"].id,
                "rotulo": "Classificação final",
                "fecha_em": INSTANTE,
            }
            for c in (ampla, ppi)
        ]
        recurso = calcular(cartoes=[ampla, ppi], recorriveis=recorriveis).o_que_fazer.recurso

        assert [alvo["rotulo"] for alvo in recurso] == [
            "Ampla concorrência — Classificação final",
            "Pessoas pretas, pardas e indígenas — Classificação final",
        ]

    def test_o_recurso_de_etapa_continua_nomeado_pela_etapa(self):
        alvo = {
            "tipo": "resultado",
            "id": uuid.uuid4(),
            "rotulo": "Prova escrita",
            "fecha_em": INSTANTE,
        }
        recurso = calcular(cartoes=[cartao()], recorriveis=[alvo]).o_que_fazer.recurso
        assert recurso[0]["rotulo"] == "Prova escrita"

    def test_sem_natureza_no_cabecalho_usa_a_da_publicacao(self):
        sem_natureza = {**cartao(), "natureza_rotulo": ""}
        texto = textos(calcular(cartoes=[sem_natureza]))
        assert "no resultado definitivo de Classificação final" in texto
        assert "no  de" not in texto


class TestOQueAFuncaoNaoSabe:
    def test_corte_e_apuracao_nao_sao_entradas(self):
        """FR-1169 e FR-1171: sem os dois na assinatura, nada aqui deduz vaga da posição."""
        parametros = set(inspect.signature(situacao.situacao_da_inscricao).parameters)
        assert not {p for p in parametros if "corte" in p or "apuracao" in p or "ocupa" in p}

    def test_nenhum_rotulo_afirma_aprovacao(self):
        rotulos = [*situacao.ROTULOS.values(), *situacao.DESFECHOS.values()]
        proibidos = ("Classificado", "Aprovado", "Dentro das vagas", "atriculado", "ontratado")
        assert not [r for r in rotulos for p in proibidos if p in r]

    def test_ordem_dos_cartoes_marco_e_depois_lista_do_perfil(self):
        ampla_m2 = cartao(codigo="M2", marco="Final")
        ppi_m1 = cartao(lista_id=PPI, lista="PPI", codigo="M1")
        ampla_m1 = cartao(codigo="M1")
        ordenados = situacao.ordenar_cartoes([ampla_m2, ppi_m1, ampla_m1], PERFIL)
        assert ordenados == [ampla_m1, ppi_m1, ampla_m2]
