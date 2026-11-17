"""A data de nascimento serve para conferir, e nunca para entrar (180, FR-8310, SC-2904).

**Por varredura, e não só caso a caso.** Um caso prova que a retomada de hoje não lê a data; não
prova nada sobre o caminho de acesso que alguém escrever amanhã — e "confirme sua data de nascimento
para recuperar o acesso" é exatamente a ideia que parece boa a quem a tem. O que se prende aqui é
**quem lê a coluna**: a lista é literal, e quem acrescentar um leitor tem de vir aqui dizer por quê.

A lista literal está certa para este risco, que é o leitor que **aparece**: um arquivo novo que cite
o campo reprova, e um da lista que deixe de citá-lo também, para que ela não envelheça.

É o mesmo que prende a FR-8311 para as publicações: nenhum módulo de publicação, de resultado ou de
divulgação está na lista, e o que entrar reprova aqui antes de publicar a data de alguém.
"""

import ast
from pathlib import Path

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.models import Inscricao

RAIZ = Path(__file__).resolve().parents[3] / "processo_seletivo"
CAMPO = "data_nascimento"

#: Quem cita o campo, e para quê. Migrations ficam fora: são história, e não leitura.
LEITORES = {
    # O dado e a regra do núcleo: pedir, validar, congelar.
    "identidade/models.py": "a coluna do cadastro",
    "identidade/application/credenciais.py": "o núcleo: falta, recusa, grava e congela",
    # A tela em que a própria pessoa informa e relê o que informou.
    "portal/identidade.py": "o contrato que a sessão do titular carrega",
    "portal/views.py": "a tela Seus dados",
    "portal/templates/portal/meus_dados.html": "o campo de Seus dados",
    "portal/templates/portal/revisao.html": "a linha da revisão, para o titular, antes do envio",
    # O ato do envio, que congela na inscrição o que o cadastro tinha.
    "inscricoes/models.py": "a coluna da inscrição",
    "inscricoes/application/submissao.py": "a recusa do envio sem data e a gravação no ato",
    # A única leitura da gestão: por ato, com motivo e trilha (D-002).
    "inscricoes/application/consulta.py": "a conferência de identidade",
    "interface/templates/interface/conferencia_de_identidade.html": "a página da conferência",
    # O requerimento de matrícula nasce com ela (D-003).
    "requerimentos/application/preencher.py": "o preenchimento inicial do requerimento",
    # Dados de demonstração e de treinamento: gravam, e não leem para decidir nada.
    "processos/management/commands/seed_demo.py": "as identidades da demonstração",
    "treinamento/construcao.py": "as identidades dos cenários de treinamento",
}

#: Onde, dentro dos módulos que também abrigam caminhos de acesso, o campo pode aparecer. O resto
#: de cada módulo — entrar, provar o e-mail, reconciliar, retomar, acrescentar ou remover credencial
#: — fica obrigado a não citá-lo.
FUNCOES_QUE_PODEM_CITAR = {
    "identidade/application/credenciais.py": {
        "falta_o_nucleo",
        "data_editavel",
        "recusas",
        "gravar_nucleo",
    },
    "portal/views.py": {"meus_dados"},
    "inscricoes/application/consulta.py": {"identidade_para_conferencia"},
}

#: Os métodos do ORM que **procuram** por um valor, pelo nome do argumento. `update`, `values_list`
#: e `get_or_create` com `defaults` gravam ou leem a coluna, e não decidem de quem é um cadastro.
BUSCAS_POR_NOME = {"filter", "exclude", "get"}
#: E os que recebem o nome da coluna como texto. `get` fica fora desta:
#: `dados.get("data_nascimento")` é leitura de dicionário, e é assim que a tela "Seus dados" lê o
#: que a pessoa digitou.
BUSCAS_POR_TEXTO = {"order_by", "latest", "earliest", "distinct"}


def _arquivos():
    for caminho in sorted(RAIZ.rglob("*")):
        if caminho.suffix not in {".py", ".html", ".txt", ".js"}:
            continue
        if "migrations" in caminho.parts or "__pycache__" in caminho.parts:
            continue
        yield caminho


def _quem_cita():
    return {
        str(caminho.relative_to(RAIZ))
        for caminho in _arquivos()
        if CAMPO in caminho.read_text(encoding="utf-8")
    }


def test_so_os_leitores_declarados_citam_a_data():
    """Nenhum caminho de acesso, nenhuma publicação e nenhum relatório está na lista."""
    citam = _quem_cita()

    novos = sorted(citam - set(LEITORES))
    assert novos == [], (
        "estes arquivos passaram a citar a data de nascimento:\n  "
        + "\n  ".join(novos)
        + "\n\nA data é declarada, serve para a equipe conferir o CPF na Receita, e não pode "
        "provar identidade nem aparecer em área pública (FR-8310, FR-8311 da 180). Se a leitura "
        "nova respeita isso, declare-a em LEITORES com a razão."
    )
    sumidos = sorted(set(LEITORES) - citam)
    assert sumidos == [], f"a lista envelheceu — estes não citam mais o campo: {sumidos}"


def test_a_varredura_enxerga_os_modulos_de_acesso():
    """Sem isto, um caminho errado faria a lista passar sobre uma pasta vazia."""
    assert (RAIZ / "identidade/application/desafio.py").exists()
    assert (RAIZ / "identidade/application/associacao.py").exists()
    assert len(list(_arquivos())) > 300


def _funcoes_que_citam(caminho):
    fonte = caminho.read_text(encoding="utf-8")
    arvore = ast.parse(fonte)
    # Só as de primeiro nível: a função interna é corpo da que a contém.
    return {
        no.name
        for no in arvore.body
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and CAMPO in (ast.get_source_segment(fonte, no) or "")
    }


def test_nos_modulos_de_acesso_so_o_nucleo_e_a_conferencia_citam_a_data():
    """FR-8310: entrar, reconciliar, retomar e trocar de e-mail não conhecem a data.

    `credenciais.py` e `portal/views.py` abrigam as duas coisas — o núcleo, que pede a data, e os
    caminhos de acesso, que não podem lê-la. A fronteira é por função.
    """
    for relativo, permitidas in FUNCOES_QUE_PODEM_CITAR.items():
        citam = _funcoes_que_citam(RAIZ / relativo)
        assert citam == permitidas, (
            f"{relativo}: a data de nascimento aparece em {sorted(citam - permitidas)} e deixou de "
            f"aparecer em {sorted(permitidas - citam)}"
        )


def test_os_demais_modulos_da_identidade_nao_citam_a_data():
    """O desafio, a associação de credencial, o endereço e a mensagem: nenhum a conhece."""
    for caminho in sorted((RAIZ / "identidade").rglob("*.py")):
        relativo = str(caminho.relative_to(RAIZ))
        if "migrations" in caminho.parts or relativo in LEITORES:
            continue
        assert CAMPO not in caminho.read_text(encoding="utf-8"), relativo


def _buscas_pela_data(caminho):
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    achadas = []
    for no in ast.walk(arvore):
        if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)):
            continue
        por_nome = no.func.attr in BUSCAS_POR_NOME and any(
            chave.arg and chave.arg.startswith(CAMPO) for chave in no.keywords
        )
        por_texto = no.func.attr in BUSCAS_POR_TEXTO and any(
            isinstance(valor, ast.Constant)
            and isinstance(valor.value, str)
            and CAMPO in valor.value
            for valor in no.args
        )
        if por_nome or por_texto:
            achadas.append(f"{caminho.relative_to(RAIZ)}:{no.lineno} .{no.func.attr}(…)")
    return achadas


def test_ninguem_procura_cadastro_ou_inscricao_pela_data():
    """A data não é chave de nada: não se filtra, não se ordena e não se localiza ninguém por ela.

    É a forma que "decidir a quem pertence um cadastro" teria no código: uma consulta que recebe
    CPF e data e devolve uma identidade.
    """
    achadas = [
        busca
        for caminho in _arquivos()
        if caminho.suffix == ".py"
        for busca in _buscas_pela_data(caminho)
    ]

    assert achadas == [], "consulta que procura pela data de nascimento:\n  " + "\n  ".join(achadas)


def test_a_coluna_nao_e_chave_nem_indice():
    """Sem unicidade e sem índice: nada no banco convida a procurar por ela (data-model da 180)."""
    for modelo in (CandidateIdentity, Inscricao):
        campo = modelo._meta.get_field(CAMPO)
        assert not campo.unique and not campo.db_index and campo.null
        em_indices = [indice.name for indice in modelo._meta.indexes if CAMPO in indice.fields]
        em_restricoes = [
            restricao.name
            for restricao in modelo._meta.constraints
            if CAMPO in (getattr(restricao, "fields", None) or ())
            or CAMPO in str(getattr(restricao, "condition", "") or "")
        ]
        assert em_indices == [] and em_restricoes == [], modelo.__name__
