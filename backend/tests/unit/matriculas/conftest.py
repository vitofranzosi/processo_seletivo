"""Um dossiê de exemplo — **sem banco**, porque os serializadores não precisam de nenhum.

`RequerimentoDeMatricula` é instanciado e nunca salvo: instanciar um modelo Django não toca o banco,
e usar o modelo de verdade em vez de um objeto solto é o que faz um campo renomeado quebrar aqui, no
teste barato, em vez de na geração.

**Nenhum valor daqui vem da linha `2` da planilha de amostra** (`D-006`): aquela linha traz dados de
uma pessoa real, e não vira fixture, exemplo nem caso de teste.
"""

from datetime import date

import pytest

from processo_seletivo.matriculas.domain import colunas
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula


def requerimento_de_exemplo(**sobrescritas):
    """Um requerimento completo, com o que cada coluna precisa de diferente."""
    valores = {
        "data_de_nascimento": date(1994, 7, 12),
        "municipio_natal": "Cariacica",
        "uf_natal": "ES",
        "nacionalidade": requerimento_nomes.BRASIL,
        "sexo": requerimento_nomes.FEMININO,
        "cor_raca": requerimento_nomes.PARDA,
        "estado_civil": requerimento_nomes.CASADO,
        "nome_da_mae": "Antônia Ferreira Gonçalves",
        "nome_do_pai": "",
        "rg": "0123456",
        "rg_orgao_emissor": "SSP-ES",
        "rg_expedido_em": date(2015, 6, 1),
        "titulo_eleitoral": "012345678901",
        "zona_eleitoral": "034",
        "secao_eleitoral": "0128",
        "telefone_celular": "(27) 98888-7766",
        "necessidade_especifica": "NENHUMA",
        "renda_familiar_faixa": requerimento_nomes.DE_UM_E_MEIO_A_DOIS_E_MEIO,
        "cep": "29040860",
        "logradouro": "Rua das Palmeiras",
        "numero": "s/n",
        "complemento": "",
        "bairro": "Jucutuquara",
        "municipio": "Vitória",
        "uf": "ES",
    }
    valores.update(sobrescritas)
    return RequerimentoDeMatricula(**valores)


def dossie_de_exemplo(**sobrescritas):
    valores = {
        "protocolo": "INS-2026-K7M4Q2PX",
        "nome": "Joana Ferreira Gonçalves",
        # **Começa por zero de propósito**: é o caso que o formato de célula `@` existe para
        # proteger (`SC-144`).
        "cpf": "01234567890",
        "email": "joana.goncalves@exemplo.br",
        "requerimento": requerimento_de_exemplo(),
        "modalidade_code": None,
        "polo": "Campus Serra",
        "edital_codigo": "77/2026",
    }
    valores.update(sobrescritas)
    return colunas.Dossie(**valores)


@pytest.fixture
def dossie():
    return dossie_de_exemplo()
