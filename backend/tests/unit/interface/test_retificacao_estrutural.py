"""Acrescentar e remover Perfil e Evento por Retificação, agora sem coreografia de ordem.

Este arquivo existia para provar que a ordem de emissão estava certa: REPLACE antes de REMOVE,
REMOVE do maior índice para o menor, ADD por último. Toda essa exigência vinha de índice
deslocar. Com o caminho nomeando a entidade, o que se prova aqui mudou: **nenhuma ordem produz
resultado diferente de outra**, e é isso que os testes verificam.

Como antes, as alterações são aplicadas com o mesmo `apply_changes` do domínio, sobre o mesmo
conteúdo — a comparação é com o resultado, não com a lista de operações.
"""

from copy import deepcopy
from itertools import permutations

import pytest

from processo_seletivo.interface import retificacao
from processo_seletivo.publicacoes.domain.changes import apply_changes
from tests.fixtures.snapshot import EVENTO, PERFIL, evento, perfil


@pytest.fixture
def conteudo():
    return {
        "title": "Edital",
        "description": "",
        "profiles": [
            perfil(PERFIL["A"], "A", "Primeiro"),
            perfil(PERFIL["B"], "B", "Segundo"),
            perfil(PERFIL["C"], "C", "Terceiro"),
        ],
        "schedule": [
            evento(EVENTO["A"], "Inscrições", 1, "2026-10-01T12:00:00+00:00"),
            evento(EVENTO["B"], "Prova", 2, "2026-10-01T12:00:00+00:00"),
        ],
    }


def referencias(conteudo):
    """Do caminho para a referência opaca que o formulário usa — o inverso do que a tela faz."""
    grupos = retificacao.campos_editaveis(conteudo)
    de_grupo = {grupo["caminho"]: grupo["referencia"] for grupo in grupos}
    de_campo = {
        campo["caminho"]: campo["referencia"] for grupo in grupos for campo in grupo["campos"]
    }
    return de_grupo, de_campo


def formulario(conteudo, *, remover=(), alterar=(), **extras):
    de_grupo, de_campo = referencias(conteudo)
    dados = {f"remover:{de_grupo[caminho]}": "1" for caminho in remover}
    dados.update({f"campo:{de_campo[caminho]}": valor for caminho, valor in alterar})
    dados.update(extras)
    return dados


def aplicar(conteudo, dados):
    alteracoes, resumo = retificacao.diferencas(conteudo, dados)
    resultado, _ = apply_changes(conteudo, alteracoes, publication_id="p1")
    return resultado, alteracoes, resumo


def test_remover_dois_perfis_apaga_os_marcados_e_nao_os_vizinhos(conteudo):
    resultado, _, resumo = aplicar(
        conteudo,
        formulario(
            conteudo, remover=[f"/profiles/id={PERFIL['A']}", f"/profiles/id={PERFIL['C']}"]
        ),
    )

    assert [p["code"] for p in resultado["profiles"]] == ["B"]
    assert [item["rotulo"] for item in resumo] == ["Remoção", "Remoção"]


def test_alterar_e_remover_na_mesma_retificacao_atinge_cada_entidade(conteudo):
    """Antes isto dependia de o REPLACE vir antes do REMOVE. Agora não depende de nada."""
    resultado, _, _ = aplicar(
        conteudo,
        formulario(
            conteudo,
            remover=[f"/profiles/id={PERFIL['A']}"],
            alterar=[(f"/profiles/id={PERFIL['C']}/name", "Terceiro alterado")],
        ),
    )

    assert [p["name"] for p in resultado["profiles"]] == ["Segundo", "Terceiro alterado"]


def test_qualquer_ordem_de_emissao_produz_o_mesmo_ato(conteudo):
    """A garantia passou da sequência para a chave: é o cenário 2 de US2.

    Se alguma permutação divergir, é porque sobrou dependência de posição em algum lugar.
    """
    alteracoes, _ = retificacao.diferencas(
        conteudo,
        formulario(
            conteudo,
            remover=[f"/profiles/id={PERFIL['A']}"],
            alterar=[(f"/profiles/id={PERFIL['C']}/name", "Terceiro alterado")],
            **{"novo-perfil-9-code": "D", "novo-perfil-9-name": "Quarto"},
        ),
    )
    assert len(alteracoes) == 3

    resultados = [
        apply_changes(deepcopy(conteudo), list(ordem), publication_id="p1")[0]
        for ordem in permutations(alteracoes)
    ]
    assert all(resultado == resultados[0] for resultado in resultados)


def test_campo_de_linha_removida_nao_vira_alteracao(conteudo):
    """Alterar o que será apagado não tem efeito e poluiria o resumo mostrado antes de confirmar."""
    _, alteracoes, resumo = aplicar(
        conteudo,
        formulario(
            conteudo,
            remover=[f"/profiles/id={PERFIL['B']}"],
            alterar=[(f"/profiles/id={PERFIL['B']}/name", "irrelevante")],
        ),
    )

    assert [a["operation"] for a in alteracoes] == ["REMOVE"]
    assert len(resumo) == 1


def test_alteracoes_emitidas_nomeiam_a_entidade_e_nunca_a_posicao(conteudo):
    """FR-019, segunda condição: o que a tela emite usa a forma por chave."""
    _, alteracoes, _ = aplicar(
        conteudo,
        formulario(
            conteudo,
            remover=[f"/profiles/id={PERFIL['B']}"],
            alterar=[(f"/schedule/id={EVENTO['A']}/description", "Nova descrição")],
        ),
    )

    caminhos = [a["targetPath"] for a in alteracoes]
    assert caminhos == [f"/schedule/id={EVENTO['A']}/description", f"/profiles/id={PERFIL['B']}"]


def test_perfil_acrescentado_nasce_com_a_forma_do_snapshot(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        {
            "novo-perfil-77-code": "D",
            "novo-perfil-77-name": "Quarto",
            "novo-perfil-77-immediateVacancies": "2",
            "novo-perfil-77-requirements": "Ensino médio\nExperiência",
        },
    )

    acrescentado = resultado["profiles"][-1]
    assert acrescentado["code"] == "D"
    assert acrescentado["requirements"] == ["Ensino médio", "Experiência"]
    assert acrescentado["immediateVacancies"] == 2
    assert set(acrescentado) == set(conteudo["profiles"][0]), (
        "um subconjunto quebraria a consulta pública e o PDF"
    )


def test_acrescentar_e_remover_juntos_preserva_o_que_nao_foi_tocado(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        formulario(
            conteudo,
            remover=[f"/profiles/id={PERFIL['B']}"],
            **{"novo-perfil-9-code": "D", "novo-perfil-9-name": "Quarto"},
        ),
    )

    assert [p["code"] for p in resultado["profiles"]] == ["A", "C", "D"]


def test_linha_nova_em_branco_e_ignorada(conteudo):
    """Acrescentar e desistir de preencher não pode virar Perfil vazio no Edital publicado."""
    _, alteracoes, _ = aplicar(conteudo, {"novo-perfil-5-code": "", "novo-perfil-5-name": "  "})

    assert alteracoes == []


def test_evento_acrescentado_continua_a_ordem_existente(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        {
            "novo-evento-3-type": "Resultado",
            "novo-evento-3-description": "Divulgação",
            "novo-evento-3-startAt": "2026-12-01T09:00",
        },
    )

    assert [e["order"] for e in resultado["schedule"]] == [1, 2, 3]
    assert resultado["schedule"][-1]["type"] == "Resultado"


def test_nada_marcado_nem_acrescentado_nao_produz_alteracao(conteudo):
    _, alteracoes, _ = aplicar(conteudo, {})
    assert alteracoes == []


def test_abrir_e_nao_tocar_em_nada_nao_produz_alteracao_de_instante():
    """O campo tem precisão de minuto e o snapshot guarda segundos.

    Com comparação de precisão total, todo Evento cujo instante não terminasse em zero segundos
    aparecia como alterado — abrir a tela e reenviar listava mudanças que ninguém fez.
    """
    conteudo = {
        "title": "Edital",
        "description": "",
        "profiles": [],
        "schedule": [
            evento(EVENTO["A"], "Inscrições", 1, "2026-10-01T12:00:37.482913+00:00"),
        ],
    }
    reenviado = {
        f"campo:{campo['referencia']}": campo["valor"]
        for grupo in retificacao.campos_editaveis(conteudo)
        for campo in grupo["campos"]
    }

    alteracoes, _ = retificacao.diferencas(conteudo, reenviado)
    assert alteracoes == []


@pytest.mark.parametrize(
    ("caminho_do_campo", "bruto", "trecho"),
    [
        (f"/profiles/id={PERFIL['A']}/immediateVacancies", "muitas", "número inteiro"),
        (f"/schedule/id={EVENTO['A']}/startAt", "ontem", "data e hora"),
    ],
)
def test_valor_mal_digitado_vira_erro_legivel(conteudo, caminho_do_campo, bruto, trecho):
    """A mensagem precisa dizer qual campo e o que foi digitado; um traceback não serve."""
    with pytest.raises(ValueError, match=trecho):
        retificacao.diferencas(conteudo, formulario(conteudo, alterar=[(caminho_do_campo, bruto)]))


# ---------------------------------------------------------------------------
# 007 — o que o Edital diz sobre a vaga também se corrige depois de publicado
# ---------------------------------------------------------------------------


def test_retificar_alcanca_atribuicoes_carga_horaria_e_remuneracao(conteudo):
    """FR-016: sem isto, corrigir uma remuneração publicada exigiria chamada de API.

    É o mesmo defeito que o achado 03 da auditoria apontou para cotas, Etapas e seções — e que a
    `006.1` corrigiu para aquelas três. Os campos que a `007` cria nasceriam com ele de novo.
    """
    perfil_a = f"/profiles/id={PERFIL['A']}"
    resultado, _, resumo = aplicar(
        conteudo,
        formulario(
            conteudo,
            alterar=[
                (f"{perfil_a}/duties", "Ministrar aulas.\nOrientar projetos."),
                (f"{perfil_a}/workload", "20 horas semanais"),
                (f"{perfil_a}/compensation", "R$ 3.000,00 mensais"),
            ],
        ),
    )

    alterado = next(p for p in resultado["profiles"] if p["id"] == PERFIL["A"])
    assert alterado["duties"] == "Ministrar aulas.\nOrientar projetos."
    assert alterado["workload"] == "20 horas semanais"
    assert alterado["compensation"] == "R$ 3.000,00 mensais"
    assert resumo, "a alteração precisa aparecer no resumo de quem confirma"


def test_perfil_acrescentado_traz_os_tres_campos_ainda_que_vazios(conteudo):
    """A forma v3 tem de estar completa, mesmo quando quem retifica não preenche nada.

    `_perfil_completo` existe por isto, e seu docstring diz o porquê: um subconjunto quebraria a
    consulta pública. A `007` acrescentou três chaves à forma — se elas não entrarem aqui, a
    própria feature que as criou produziria conteúdo de versão 3 incompleto.
    """
    resultado, _, _ = aplicar(
        conteudo,
        {
            "novo-perfil-01-code": "Z",
            "novo-perfil-01-name": "Acrescentado sem os campos novos",
            "novo-perfil-01-immediateVacancies": "1",
        },
    )

    acrescentado = resultado["profiles"][-1]
    for campo in ("duties", "workload", "compensation"):
        assert campo in acrescentado, f"{campo} ausente quebraria a forma canônica v3"
        assert acrescentado[campo] == "", "ausência se exprime por string vazia, não por null"


def test_perfil_acrescentado_com_os_campos_novos_os_preserva(conteudo):
    resultado, _, _ = aplicar(
        conteudo,
        {
            "novo-perfil-01-code": "Z",
            "novo-perfil-01-name": "Acrescentado",
            "novo-perfil-01-immediateVacancies": "1",
            "novo-perfil-01-duties": "Coordenar o laboratório.",
            "novo-perfil-01-workload": "40 horas semanais",
            "novo-perfil-01-compensation": "R$ 5.000,00 mensais",
        },
    )

    acrescentado = resultado["profiles"][-1]
    assert acrescentado["duties"] == "Coordenar o laboratório."
    assert acrescentado["workload"] == "40 horas semanais"
    assert acrescentado["compensation"] == "R$ 5.000,00 mensais"
