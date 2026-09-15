"""Os oito invariantes da §5 da spec da `027`, um teste por invariante.

Eles são verificáveis **a qualquer momento, em qualquer estado do acervo** — é o que a spec exige
para fechar a feature. Cinco deles são de **ausência**, e é por isso que este arquivo existe em vez
de a verificação ficar espalhada: ausência não se prova exercitando um caminho, e sim varrendo os
que existem. Um caminho novo que os viole nasce com este arquivo vermelho.

É o mesmo molde que a `025` usou, e pela mesma razão.
"""

import re
from pathlib import Path

from processo_seletivo.classificacao.application.corte import linha_do_quadro
from processo_seletivo.editais.domain.perfis import derivar_linha_geral, listas_reservadas
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    blocking_findings,
    validate_for_publication,
)

CODIGO = Path(__file__).resolve().parents[3] / "processo_seletivo"
PERFIL = "cccccccc-0000-4000-8000-000000000801"
PPI = "cccccccc-0000-4000-8000-000000000802"


def perfil(**alteracoes):
    base = {
        "id": PERFIL,
        "code": "C1",
        "name": "Curso",
        "immediateVacancies": 80,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": [],
        "vacancyTable": [],
        "generalCompetitionModalityId": None,
    }
    return {**base, **alteracoes}


def snapshot(um_perfil):
    return {
        "title": "Edital",
        "description": "…",
        "schedule": [{"id": PERFIL, "type": "X", "description": "…"}],
        "profiles": [um_perfil],
    }


def fontes(padrao):
    """Onde o padrão aparece no código de produção, arquivo a arquivo."""
    return {
        arquivo.relative_to(CODIGO).as_posix()
        for arquivo in CODIGO.rglob("*.py")
        if "__pycache__" not in arquivo.parts and re.search(padrao, arquivo.read_text("utf-8"))
    }


# --- 1 · a quantidade de um recorte não é declarável em dois lugares --------------------------


def test_invariante_1_sem_lista_reservada_a_tela_nao_oferece_dois_campos():
    """O campo da linha geral só é desenhado quando há repartição a pedir.

    A verificação é sobre o **template**, porque é ali que a segunda caixa existia: o modelo sempre
    teve dois lugares — o total do Perfil e a linha do quadro —, e o defeito era a tela pedir os
    dois ao mesmo tempo, um rotulado em português corrente e o outro sem explicação visível.
    """
    linha = (CODIGO / "interface/templates/interface/_linha_do_quadro.html").read_text("utf-8")
    assert "{% if linha.derivada %}" in linha, "a linha derivada não desenha caixa"

    # **A condição é procurada nos templates, e não num arquivo nomeado.** Ela já mudou de casa uma
    # vez — saiu de `_perfil.html` para `_quadro_do_perfil.html` quando o seletor da ampla passou a
    # reconstruir o quadro durante a edição —, e um invariante que prendesse o caminho estaria
    # medindo onde o código mora em vez de o que ele garante.
    templates = (CODIGO / "interface/templates/interface").glob("*.html")
    onde = [
        arquivo.name
        for arquivo in templates
        if "{% if perfil.tem_lista_reservada %}" in arquivo.read_text("utf-8")
    ]
    assert onde, "o bloco do quadro é condicionado à existência de lista reservada"


# --- 2 · todo Perfil publicado por esta interface publica linha geral -------------------------


def test_invariante_2_publicar_sem_linha_geral_e_impeditivo():
    achados = {
        item.code for item in blocking_findings(validate_for_publication(snapshot(perfil())))
    }
    assert "vacancy_general_row_missing" in achados


def test_invariante_2_a_derivacao_cobre_todo_perfil_sem_lista_reservada():
    """E a outra ponta: gravado pelo command, o Perfil nunca chega à publicação sem ela."""
    for total in (0, 1, 80, 999):
        derivado = derivar_linha_geral(perfil(immediateVacancies=total))
        assert derivado["vacancyTable"][0]["immediateVacancies"] == total


# --- 3 · nenhuma linha é inferida na leitura de conteúdo publicado ----------------------------


def test_invariante_3_a_leitura_nao_infere_linha_ausente():
    publicado = snapshot(perfil(immediateVacancies=40))
    assert linha_do_quadro(publicado, perfil_id=PERFIL, lista_id=None) is None


def test_invariante_3_nenhum_leitor_deriva_do_total_do_perfil():
    """Varredura: só o domínio de elaboração deriva, e só ele importa `derivar_linha_geral`.

    É o guarda da classe: um leitor novo que decidisse "se não há linha, use o total" passaria em
    todos os testes de caminho feliz e reescreveria o acervo por interpretação.
    """
    assert fontes(r"\bderivar_linha_geral\b") == {
        "editais/domain/perfis.py",
        "editais/application/draft.py",
    }


# --- 4 · nenhum conteúdo publicado muda sem Retificação ---------------------------------------


def test_invariante_4_a_feature_nao_acrescenta_migration_nem_degrau():
    """Nenhuma conversão do acervo: a `027` não abre degrau de schema nem escreve migration.

    Era a alternativa tentadora — "converter tudo de uma vez" — e ela está recusada por escrito na
    `D-005`: publicação é ato imutável, e fazer um Edital publicado passar a afirmar uma quantidade
    que ele não publicou é reescrevê-lo por interpretação.
    """
    migrations = sorted(
        arquivo.name for arquivo in (CODIGO / "editais/migrations").glob("00*_*.py")
    )
    assert not [nome for nome in migrations if "quadro" in nome and "0016" not in nome], (
        "a única migration do quadro é a da `025`"
    )


# --- 5 · nenhuma advertência desta feature bloqueia --------------------------------------------


def test_invariante_5_as_advertencias_nunca_sao_impeditivas():
    com_lista_sem_linha = perfil(
        competitionModalities=[{"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"}],
        vacancyTable=[{"id": "l1", "modalityId": None, "immediateVacancies": 80}],
    )
    achados = validate_for_publication(snapshot(com_lista_sem_linha))
    codigos = {item.code for item in achados if item.severity == Severity.WARNING}
    assert {
        "vacancy_reserved_list_without_row",
        "general_competition_modality_undeclared",
    } <= codigos
    impeditivos = {item.code for item in blocking_findings(achados)}
    assert not (impeditivos & codigos), "advertência que bloqueia é defeito, e não zelo"


def test_invariante_5_a_advertencia_do_acervo_tambem_nao_bloqueia():
    achados = validate_for_publication(snapshot(perfil()), ato=ATO_DE_RETIFICACAO)
    do_acervo = [item for item in achados if item.code == "vacancy_table_absent_in_archive"]
    assert do_acervo and do_acervo[0].severity == Severity.WARNING
    assert not blocking_findings(do_acervo)


# --- 6 · quem constata ausência nomeia o ato ---------------------------------------------------


def test_invariante_6_toda_constatacao_de_ausencia_nomeia_o_ato():
    """As três telas que dizem "não há quantidade" dizem também por qual ato ela passa a haver."""
    ocupacao = (CODIGO / "interface/templates/interface/ocupacao.html").read_text("utf-8")
    convocacao = (CODIGO / "interface/templates/interface/convocacao.html").read_text("utf-8")
    emissao = (CODIGO / "ocupacao/application/emissao.py").read_text("utf-8")

    for origem, texto in (("ocupacao", ocupacao), ("convocacao", convocacao), ("ato", emissao)):
        assert "Retificação do Perfil" in texto, f"{origem} constata a ausência e não nomeia o ato"


# --- 7 · nenhuma tela desta feature ocupa, convoca ou corta -------------------------------------


def test_invariante_7_a_linha_do_quadro_carrega_quantidade_e_nunca_pessoa():
    """O corte que a `025` manteve, e que a `027` não move.

    Verificado na **forma** do modelo, e não na prosa: a linha tem o recorte e a quantidade, e nada
    que aponte uma pessoa. Uma coluna nova que ligasse candidato a linha faria esta feature ocupar
    vaga sem que nenhum requisito o tivesse decidido.
    """
    from processo_seletivo.editais.models.perfis import LinhaDoQuadroDeVagas

    campos = {campo.name for campo in LinhaDoQuadroDeVagas._meta.get_fields()}
    assert campos == {"id", "perfil", "modalidade", "vagas_imediatas", "ordem"}


def test_invariante_7_o_dominio_da_elaboracao_nao_conhece_inscricao():
    """E o domínio que deriva a linha não importa nada de quem se inscreve."""
    perfis = (CODIGO / "editais/domain/perfis.py").read_text("utf-8")
    importacoes = [linha for linha in perfis.splitlines() if linha.startswith(("import ", "from "))]
    assert not [linha for linha in importacoes if "inscricoes" in linha or "classificacao" in linha]


# --- 8 · a derivação tem uma fonte só ----------------------------------------------------------


def test_invariante_8_a_derivacao_ignora_tudo_menos_o_total():
    """Percentual, fundamento e regra normativa não entram na conta, em combinação nenhuma."""
    com_regra = perfil(
        immediateVacancies=80,
        competitionModalities=[
            {
                "id": PPI,
                "code": "AC",
                "name": "Ampla concorrência",
                "normativeRule": {"percentage": "20", "foundation": "Lei 12.990/2014"},
            }
        ],
        generalCompetitionModalityId=PPI,
    )
    assert listas_reservadas(com_regra) == set(), "a apontada como ampla não é lista reservada"
    assert derivar_linha_geral(com_regra)["vacancyTable"][0]["immediateVacancies"] == 80


def test_invariante_8_o_ato_de_publicacao_e_o_padrao_de_quem_esquece():
    """E a guarda do recorte por ato: esquecer o parâmetro erra pelo lado que recusa."""
    sem_dizer = {item.code for item in validate_for_publication(snapshot(perfil()))}
    dizendo = {
        item.code for item in validate_for_publication(snapshot(perfil()), ato=ATO_DE_PUBLICACAO)
    }
    assert sem_dizer == dizendo
