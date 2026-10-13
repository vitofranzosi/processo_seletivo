"""O corpus passa inteiro pelo fluxo real (070, T004, `R-016`).

É o ensaio que decide a camada de banco dos testes da 070: se o conteúdo publicado em 11/10/2026
volta a ser publicado, igual, pelos comandos de hoje, os casos que dependem de versão, fronteira e
origem rodam sobre os mesmos três Editais que a camada de conteúdo usa. Se não volta, a diferença
aparece aqui, nomeada, e não como uma falha estranha num caso distante.

"Igual" exclui só o que o fluxo não reproduz por construção: as datas, deslocadas; os
identificadores do Processo e do Edital, que o banco gera; a identidade das seções, que é
`uuid5(edital:key)` e por isso muda com o Edital; e o artefato de cada anexo, cujos bytes são de
teste.
"""

import pytest

from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.corpus import conteudo, deslocar, publicacoes_do, publicar_do_corpus

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _comparavel(valor):
    valor = dict(valor)
    for chave in ("editalId", "processoId", "processoCode"):
        valor.pop(chave, None)
    valor["sections"] = [
        {k: v for k, v in secao.items() if k != "id"} for secao in valor.get("sections") or []
    ]
    valor["attachments"] = [
        {k: v for k, v in anexo.items() if k not in ("artifactId", "artifactHash")}
        for anexo in valor.get("attachments") or []
    ]
    return valor


@pytest.mark.parametrize("nome", ["01", "91", "92"])
def test_o_conteudo_vigente_republicado_e_o_do_corpus(api_client, nome):
    edital, deslocamento = publicar_do_corpus(api_client, nome)
    final = publicacoes_do(nome)
    esperado = deslocar(conteudo(nome, final), deslocamento)
    # A última versão do corpus pode ter vigência futura (01/2026, v3): lê-se no instante dela.
    ultima = VersaoConsolidada.objects.filter(edital=edital).order_by("-valid_from").first()
    vigente = effective_version(edital_id=edital.id, at=ultima.valid_from)

    assert _comparavel(vigente.content) == _comparavel(esperado)
