"""Os atalhos dos testes do gerador de cenários de treinamento (134).

Funções aqui, fixture no `conftest.py` da pasta, pela regra de `tests/fixtures/corte.py`.
"""

import json
from collections import Counter
from io import StringIO

from django.core.management import call_command
from django.db import connection


def comando(nome, *cenarios, escrever=True, **opcoes):
    saida, erros = StringIO(), StringIO()
    if escrever and "dry_run" not in opcoes:
        opcoes.setdefault("banco", connection.settings_dict["NAME"])
    call_command(nome, *(), cenario=list(cenarios), stdout=saida, stderr=erros, **opcoes)
    return saida.getvalue() + erros.getvalue()


def carregar(*cenarios, **opcoes):
    return comando("carregar_cenarios_de_treinamento", *cenarios, **opcoes)


def verificar(*cenarios):
    return comando("verificar_cenarios_de_treinamento", *cenarios, escrever=False)


def restaurar(cenario, **opcoes):
    return comando("restaurar_cenario_de_treinamento", cenario, **opcoes)


def instantaneo():
    """Toda linha de toda tabela do banco, como texto — para provar que nada preexistente mudou.

    **Linha a linha e campo a campo**, e não contagem: um `UPDATE` num Edital real não muda a
    contagem de nada, e é exatamente o que o pedido proíbe (18.1).
    """
    foto = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        for (tabela,) in cursor.fetchall():
            cursor.execute(f'SELECT row_to_json(t)::text FROM "{tabela}" t')  # noqa: S608
            foto[tabela] = Counter(linha for (linha,) in cursor.fetchall())
    return foto


def removidas(antes, depois):
    """As linhas de `antes` que não estão mais, idênticas, em `depois` — por tabela."""
    faltando = {}
    for tabela, linhas in antes.items():
        diferenca = linhas - depois.get(tabela, Counter())
        if diferenca:
            faltando[tabela] = [json.loads(linha) for linha in diferenca.elements()]
    return faltando


def retomar(manifesto, autoridade=None):
    """A montagem de uma rodada já criada — para o teste agir no cenário como a equipe agiria.

    Os atores, os identificadores e as pessoas são os da rodada; a comissão e as inscrições são as
    do banco. Nada é recriado.
    """
    from processo_seletivo.comissoes.models import MembroComissao
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.processos.models import Edital
    from processo_seletivo.treinamento import identificadores
    from processo_seletivo.treinamento.construcao import Montagem
    from processo_seletivo.treinamento.servico import autoridade_vigente

    montagem = Montagem(
        codigo=manifesto.codigo,
        rodada=manifesto.rodada,
        unidade=manifesto.unidade,
        autoridade_id=autoridade_vigente(manifesto.unidade, autoridade),
        titulo="",
    )
    montagem.processo = manifesto.processo
    montagem.edital = Edital.objects.get(processo=manifesto.processo)
    montagem.membros = {
        membro.identity_subject: membro
        for membro in MembroComissao.objects.filter(processo=manifesto.processo)
    }
    inscricoes = list(Inscricao.objects.filter(pk__in=manifesto.registros.get("inscricao", [])))
    por_id = {str(inscricao.id): inscricao for inscricao in inscricoes}
    montagem.inscricoes = [por_id[pk] for pk in manifesto.registros.get("inscricao", [])]
    montagem.pessoas = [
        identificadores.pessoa(manifesto.unidade, manifesto.codigo, manifesto.rodada, ordem)
        for ordem in range(1, len(montagem.inscricoes) + 1)
    ]
    return montagem
