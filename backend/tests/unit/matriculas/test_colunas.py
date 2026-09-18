"""Uma asserção por coluna, no caso normal e no vazio (`FR-445`, `T014`).

**É a fase em que o erro silencioso morre.** O defeito desta feature não aparece na geração: ele
aparece depois da matrícula, no Registro Acadêmico, com a pessoa no meio. Trinta e quatro colunas
testadas isoladas custam pouco e são a única barreira que pega uma tradução errada antes de o
arquivo sair.

**Nenhum valor aqui vem da linha `2` da planilha de amostra** (`D-006`).
"""

import pytest

from processo_seletivo.matriculas.domain import colunas, nomes
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.unit.matriculas.conftest import dossie_de_exemplo, requerimento_de_exemplo


def celula(dossie, cabecalho):
    """O valor de **uma** coluna, pelo cabeçalho — como quem confere o arquivo a procuraria."""
    por_cabecalho = {coluna.cabecalho: coluna.serializador for coluna in colunas.COLUNAS}
    return por_cabecalho[cabecalho](dossie)


def sem(campo):
    """O mesmo dossiê, com um campo do requerimento não declarado."""
    vazio = None if campo.endswith("_em") or campo.startswith("data") else ""
    return dossie_de_exemplo(requerimento=requerimento_de_exemplo(**{campo: vazio}))


# ---------------------------------------------------------------------------
# A forma do arquivo
# ---------------------------------------------------------------------------


def test_sao_trinta_e_quatro_colunas_na_ordem_do_destino():
    """`FR-436`: 34 cabeçalhos, na ordem e na grafia do destino — acentos inclusive."""
    assert len(colunas.COLUNAS) == 34
    assert colunas.CABECALHOS[0] == "INSC"
    assert colunas.CABECALHOS[23] == "ENDEREÇO"
    assert colunas.CABECALHOS[24] == "NÚMERO"
    assert colunas.CABECALHOS[-1] == "COD_POLO"


def test_toda_celula_e_texto(dossie):
    """`FR-437`: nenhuma coluna devolve número, data ou `None` — tudo é texto."""
    textos, _ = colunas.linha(dossie)
    assert len(textos) == 34
    assert all(isinstance(texto, str) for texto in textos)


# ---------------------------------------------------------------------------
# As três que saem sempre vazias (`D-001`, `FR-438`, `SC-145`)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cabecalho", ["COD_CURSO", "COD_TURNO", "COD_POLO"])
def test_as_tres_colunas_externas_saem_vazias_e_nomeadas(dossie, cabecalho):
    """`SC-145`: vazias, com a razão declarada — e **nunca** deduzidas.

    O teste é sobre a decisão central da spec: o valor é vocabulário do sistema acadêmico, e uma
    célula vazia gerada por regra é uma afirmação verificável de ausência.
    """
    produzida = celula(dossie, cabecalho)
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.EXTERNA
    assert "sistema acadêmico" in produzida.lacuna.razao


def test_nenhuma_coluna_externa_recebe_valor_deduzido():
    """Nem o nome do polo, que **é** conhecido, vaza para o código do polo."""
    dossie = dossie_de_exemplo(polo="Campus Serra")
    assert celula(dossie, "NOME_POLO").texto == "Campus Serra"
    assert celula(dossie, "COD_POLO").texto == ""


# ---------------------------------------------------------------------------
# Coluna a coluna
# ---------------------------------------------------------------------------


def test_protocolo_sai_opaco_como_esta(dossie):
    """`Q-3`: o protocolo não é tornado sequencial para caber no destino."""
    assert celula(dossie, "INSC").texto == "INS-2026-K7M4Q2PX"


def test_nome_vem_da_identidade(dossie):
    assert celula(dossie, "NOME").texto == "Joana Ferreira Gonçalves"


def test_classificacao_fica_vazia_ate_a_questao_ser_respondida(dossie):
    """`FR-448`: a exportação **não escolhe** entre classificação e numeração de linha."""
    produzida = celula(dossie, "CLASSIF_CURSO_FINAL")
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.EXTERNA


def test_forma_de_ingresso_traz_ac_quando_nao_ha_modalidade(dossie):
    """`FR-443`, `D-003`: a ausência de Modalidade **é** ampla concorrência."""
    assert celula(dossie, "COD_FORMA_INGRESSO").texto == "AC"


def test_forma_de_ingresso_traz_o_codigo_publicado():
    assert celula(dossie_de_exemplo(modalidade_code="PPI"), "COD_FORMA_INGRESSO").texto == "PPI"


def test_grafia_desconhecida_recusa_a_geracao_e_nomeia_o_codigo_e_o_edital():
    """`FR-441`, `SC-147`: `PPP` publicado **não** vira `PPI` — a geração para.

    É o caso real do `seed_demo`: duas letras de diferença para o mesmo instituto jurídico, e
    reescrever a grafia faria o arquivo discordar do Edital publicado.
    """
    dossie = dossie_de_exemplo(modalidade_code="PPP", edital_codigo="77/2026")
    with pytest.raises(DomainError) as recusa:
        celula(dossie, "COD_FORMA_INGRESSO")
    assert recusa.value.code == nomes.MODALIDADE_DESCONHECIDA
    assert "PPP" in recusa.value.detail
    assert "77/2026" in recusa.value.detail


def test_cpf_preserva_o_zero_a_esquerda(dossie):
    """`SC-144`: onze dígitos, sem pontuação, com o zero inicial."""
    assert celula(dossie, "CPF").texto == "01234567890"


def test_sexo_sai_no_codigo_dos_dois_lados(dossie):
    assert celula(dossie, "SEXO").texto == requerimento_nomes.FEMININO


def test_estado_civil_e_flexionado_e_nunca_traz_a_forma_da_tela(dossie):
    """`FR-442`, `D-004`: `Casada`, e nunca `Casado(a)` — que é o que `legivel()` devolveria."""
    assert celula(dossie, "ESTADO_CIVIL").texto == "Casada"


def test_estado_civil_fica_vazio_sem_sexo_declarado():
    """Sem os dois não há flexão: escolher uma das formas poria na boca da pessoa o que ela
    não disse."""
    dossie = dossie_de_exemplo(requerimento=requerimento_de_exemplo(sexo=""))
    assert celula(dossie, "ESTADO_CIVIL").texto == ""


def test_email_vem_da_credencial_principal(dossie):
    assert celula(dossie, "EMAIL").texto == "joana.goncalves@exemplo.br"


def test_a_lacuna_do_email_fala_de_email(dossie):
    """A razão da ausência é a da coluna, e não a de uma vizinha.

    A primeira redação desta função pediu emprestada a frase do telefone celular: o relatório dizia
    que faltava *telefone* numa linha da coluna `EMAIL`, e quem o lesse iria procurar o campo
    errado. Uma razão emprestada é pior que nenhuma.
    """
    produzida = celula(dossie_de_exemplo(email=""), "EMAIL")
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.AUSENCIA
    assert "e-mail" in produzida.lacuna.razao
    assert "telefone" not in produzida.lacuna.razao.lower()


def test_data_de_nascimento_sai_em_dia_mes_ano(dossie):
    """`FR-437`: `dd/mm/aaaa`, sem depender do idioma do servidor."""
    assert celula(dossie, "DATA_NASCIMENTO").texto == "12/07/1994"


def test_data_de_nascimento_ausente_sai_vazia():
    assert (
        sem("data_de_nascimento")
        and celula(sem("data_de_nascimento"), "DATA_NASCIMENTO").texto == ""
    )


def test_cor_sai_na_grafia_do_destino(dossie):
    assert celula(dossie, "COR").texto == "Parda"


def test_cor_indigena_sai_vazia_e_nomeia_a_pessoa():
    """`FR-440`, `SC-146`, `R-1`: o destino não comporta o valor declarado.

    **Nunca substituída por valor próximo.** Mapear *indígena* para *parda* apagaria uma declaração
    em silêncio, dentro de um arquivo que ninguém confere linha a linha — e a contradição é do
    destino: a Modalidade `PPP` reserva vaga com fundamento na lei que nomeia indígenas.
    """
    dossie = dossie_de_exemplo(
        requerimento=requerimento_de_exemplo(cor_raca=requerimento_nomes.INDIGENA)
    )
    produzida = celula(dossie, "COR")
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.NOMINAL
    assert produzida.lacuna.valor_declarado == "Indígena"


def test_filiacao_ausente_e_ausencia_declarada():
    """`FR-384` da `029`: pai não declarado é situação comum e legítima, e não erro."""
    dossie = dossie_de_exemplo()
    produzida = celula(dossie, "NOME_PAI")
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.AUSENCIA
    assert celula(dossie, "NOME_MAE").texto == "Antônia Ferreira Gonçalves"


def test_cidade_natal_nao_se_confunde_com_a_cidade_do_endereco(dossie):
    assert celula(dossie, "CIDADE_NATAL").texto == "Cariacica"
    assert celula(dossie, "CIDADE").texto == "Vitória"


def test_nacionalidade_brasil_sai_como_br(dossie):
    """`FR-453`, `SC-154`."""
    assert celula(dossie, "COD_NACIONALIDADE").texto == "BR"


@pytest.mark.parametrize("grafia", ["Brasil", "Brasileira", "BRASILEIRO", "brasil"])
def test_nacionalidade_reconhece_a_grafia_historica(grafia):
    """O campo foi texto livre por dois dias, e o que foi **enviado** não é reescrito.

    Quem lê reconhece a grafia; o banco preserva a declaração de quem já enviou.
    """
    dossie = dossie_de_exemplo(requerimento=requerimento_de_exemplo(nacionalidade=grafia))
    assert celula(dossie, "COD_NACIONALIDADE").texto == "BR"


def test_outro_pais_sai_vazio_e_nomeado():
    """`FR-453`: um exemplo só não prova o esquema ISO — `PT` por Portugal é invenção (`Q-7`)."""
    dossie = dossie_de_exemplo(
        requerimento=requerimento_de_exemplo(nacionalidade=requerimento_nomes.OUTRO_PAIS)
    )
    produzida = celula(dossie, "COD_NACIONALIDADE")
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.NOMINAL
    assert produzida.lacuna.valor_declarado == "Outro país"


def test_documento_de_identidade_sai_como_texto(dossie):
    assert celula(dossie, "RG").texto == "0123456"
    assert celula(dossie, "EMISSOR").texto == "SSP-ES"
    assert celula(dossie, "IDENTIDADE_DATA").texto == "01/06/2015"


def test_titulo_eleitoral_sai_em_tres_blocos_de_quatro(dossie):
    """`FR-451`, `SC-152`."""
    assert celula(dossie, "TITULO_ELE").texto == "0123 4567 8901"


def test_zona_e_secao_preservam_os_zeros_a_esquerda(dossie):
    """`SC-152`: `034` não vira `34`, e `0128` não vira `128`."""
    assert celula(dossie, "ZONA_ELE").texto == "034"
    assert celula(dossie, "SECAO_ELE").texto == "0128"


def test_os_tres_eleitorais_ausentes_saem_vazios():
    for campo, cabecalho in (
        ("titulo_eleitoral", "TITULO_ELE"),
        ("zona_eleitoral", "ZONA_ELE"),
        ("secao_eleitoral", "SECAO_ELE"),
    ):
        produzida = celula(sem(campo), cabecalho)
        assert produzida.texto == ""
        assert produzida.lacuna.especie == nomes.AUSENCIA


def test_cep_sai_com_hifen(dossie):
    """`FR-444`: guardado sem pontuação, emitido com ela."""
    assert celula(dossie, "CEP").texto == "29040-860"


def test_endereco_sai_como_declarado(dossie):
    assert celula(dossie, "ENDEREÇO").texto == "Rua das Palmeiras"
    assert celula(dossie, "BAIRRO").texto == "Jucutuquara"
    assert celula(dossie, "ESTADO").texto == "ES"


def test_numero_sem_numero_sai_como_texto(dossie):
    """*"s/n"* existe, e um número obrigatório obrigaria a inventá-lo."""
    assert celula(dossie, "NÚMERO").texto == "s/n"


def test_complemento_vazio_e_o_caso_normal(dossie):
    produzida = celula(dossie, "COMPLEMENTO")
    assert produzida.texto == ""
    assert produzida.lacuna.especie == nomes.AUSENCIA


def test_celular_sai_sem_pontuacao(dossie):
    """`FR-444`: a forma de cada coluna é a do destino, e não a deste sistema."""
    assert celula(dossie, "CELULAR").texto == "27988887766"


def test_renda_traz_a_faixa_da_familia_sem_conversao(dossie):
    """`D-002`: a coluna recebe a faixa **da família**, e o relatório declara a divergência.

    A pessoa do dossiê declarou *de 1,5 a 2,5* somados. A coluna recebe *1,5 a 2,5* — sem dividir
    por ninguém, porque dividir uma faixa por um número não produz uma faixa.
    """
    assert celula(dossie, "RENDA_PER_CAPITA_PNP").texto == "1,5 a 2,5"


def test_necessidades_especiais_e_texto_livre(dossie):
    assert celula(dossie, "NECESSIDADES_ESPECIAIS").texto == "NENHUMA"


def test_nome_do_polo_vem_da_localidade_publicada(dossie):
    assert celula(dossie, "NOME_POLO").texto == "Campus Serra"


# ---------------------------------------------------------------------------
# A versão dos mapeamentos (`FR-454`)
# ---------------------------------------------------------------------------


def test_a_versao_dos_mapeamentos_e_um_numero_declarado_a_mao():
    """`FR-454`: alterada por quem mudar qualquer serializador, no molde de `SCHEMA_VERSION`."""
    assert isinstance(colunas.VERSAO_DOS_MAPEAMENTOS, int)
    assert colunas.VERSAO_DOS_MAPEAMENTOS >= 1
