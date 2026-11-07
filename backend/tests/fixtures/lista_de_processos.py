"""Processos e Editais montados direto no banco, para o recorte da lista (129).

O que se exercita é a **leitura** — o grupo, a busca, a página, a faixa sobre a unidade —, e
atravessar o ciclo de publicação dezenas de vezes custaria minutos sem acrescentar garantia. É o
mesmo padrão de `tests/performance/test_visao_institucional.py::publicar_direto`. Os casos que
precisam de um Edital publicado de verdade (recurso, Retificação) usam as fixtures do ciclo e
acrescentam Processos daqui em volta.
"""

from datetime import timedelta
from itertools import count

from django.utils import timezone

from processo_seletivo.processos.models import Edital, ProcessoSeletivo

_sequencia = count()


def _letras(indice):
    """O código padrão sem dígito: um "PS-LISTA-0090" casaria a busca por "90" pelo código, e o
    caso que busca número acharia Processo que não pediu."""
    letras = ""
    indice += 1
    while indice:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(ord("A") + resto) + letras
    return letras


def processo(
    titulo="Processo",
    *,
    status=ProcessoSeletivo.Status.ATIVO,
    editais=(),
    codigo=None,
    escopo="cefor",
    ha_minutos=None,
):
    """Um Processo com os seus Editais.

    `editais` é uma sequência de `(numero, ano, situacao)` ou `(numero, ano, situacao, titulo)`.
    `ha_minutos` fixa a criação no passado, para a ordem "do mais recente ao mais antigo" ser a
    que o caso escolhe, e não a do relógio entre duas linhas.
    """
    indice = next(_sequencia)
    agora = timezone.now()
    criado = agora - timedelta(minutes=ha_minutos) if ha_minutos is not None else agora
    criado_ps = ProcessoSeletivo.objects.create(
        institution_scope=escopo,
        institutional_code=codigo or f"PS-LISTA-{_letras(indice)}",
        title=titulo,
        status=status,
        created_at=criado,
        created_by="carga",
        last_changed_at=criado,
    )
    for edital in editais:
        numero, ano, situacao, *resto = edital
        Edital.objects.create(
            processo=criado_ps,
            institution_scope=escopo,
            number=numero,
            year=ano,
            title=resto[0] if resto else titulo,
            status=situacao,
            created_at=criado,
            created_by="carga",
            last_edited_by="carga",
        )
    return criado_ps


def muitos(
    quantos, *, status=ProcessoSeletivo.Status.ATIVO, situacao_do_edital="PUBLICADO", desde=0
):
    """`quantos` Processos de um Edital cada, o primeiro o mais recente.

    Os Editais são de 2019, para não colidirem com os de `publicar_direto`, que numera a partir de
    zero no ano que o caso pede.
    """
    return [
        processo(
            f"Processo {desde + indice:03d}",
            status=status,
            editais=[(f"{desde + indice + 100}", 2019, situacao_do_edital)],
            ha_minutos=desde + indice + 1,
        )
        for indice in range(quantos)
    ]
