"""O canal de atendimento: achado no Edital, nunca escolhido (070, `R-011`, `D-005`, T035)."""

from processo_seletivo.duvidas.domain.canal import canal, contatos
from processo_seletivo.duvidas.domain.estruturas import CANAL_DO_EDITAL, CANAL_INSTITUCIONAL
from tests.fixtures.corpus import conteudo


def _com_secao(texto, chave="disposicoes-finais"):
    return {
        "sections": [
            {
                "id": "s1",
                "key": chave,
                "title": "Disposições Finais",
                "type": "TEXT",
                "content": texto,
            }
        ]
    }


def test_91_um_canal_com_exclusividade():
    achado = canal(conteudo("91", 2))
    assert achado.origem == CANAL_DO_EDITAL
    assert achado.contatos == ("selecao.demo@exemplo.ifes.edu.br",)
    assert achado.exclusividade
    assert [p.localizacao for p in achado.paragrafos] == ["Seção “Disposições Preliminares”"]
    assert achado.paragrafos[0].conteudo.startswith(
        "As dúvidas sobre este Edital serão esclarecidas exclusivamente pelo e-mail"
    )


def test_92_um_canal_sem_exclusividade_e_o_formulario_de_recursos_fica_fora():
    achado = canal(conteudo("92", 2))
    assert achado.contatos == ("selecao.uab.demo@exemplo.ifes.edu.br",)
    assert not achado.exclusividade
    assert all("11.1" not in p.conteudo for p in achado.paragrafos)


def test_01_sem_canal_no_edital_vale_o_institucional():
    achado = canal(conteudo("01", 3), "atendimento@exemplo.ifes.edu.br")
    assert achado.origem == CANAL_INSTITUCIONAL
    assert achado.contatos == ("atendimento@exemplo.ifes.edu.br",)
    assert achado.paragrafos == ()


def test_sem_edital_e_sem_implantacao_nao_ha_canal():
    achado = canal(conteudo("01", 3), "")
    assert achado.origem == CANAL_INSTITUCIONAL
    assert achado.contatos == ()


def test_dois_emails_distintos_sao_divergentes():
    achado = canal(
        _com_secao(
            "Dúvidas pelo e-mail a@exemplo.br.\nEsclarecimentos sobre a matrícula: b@exemplo.br."
        )
    )
    assert achado.divergente
    assert achado.contatos == ("a@exemplo.br", "b@exemplo.br")


def test_o_mesmo_email_em_dois_paragrafos_e_um_canal_so():
    achado = canal(_com_secao("Dúvidas: A@Exemplo.br.\nAtendimento pelo e-mail a@exemplo.br."))
    assert not achado.divergente
    assert achado.contatos == ("a@exemplo.br",)
    assert len(achado.paragrafos) == 2


def test_paragrafo_sem_termo_de_duvida_nao_e_canal():
    publicado = _com_secao(
        "Informações Gerais: as publicações estarão em https://selecoes.exemplo.br."
    )
    assert canal(publicado, "").contatos == ()


def test_telefone_com_e_sem_ddd():
    assert contatos("Atendimento pelo telefone (27) 3357-7500.") == ("2733577500",)
    assert contatos("Atendimento pelo telefone 3357-7500.") == ("33577500",)


def test_endereco_eletronico_e_normalizado():
    assert contatos("Dúvidas em https://Exemplo.br/duvidas/.") == ("https://exemplo.br/duvidas",)
