"""A base de referência de CEP montada à mão, para os testes que precisam de um CEP reconhecido.

**Por que isto virou fixture compartilhada.** Desde que a carga passou a ser por geração, não existe
mais referência solta: toda linha pertence a uma `CargaDeCep`, e só a geração **vigente** responde.
Um teste que criasse a linha sozinho voltaria a esbarrar no `carga_id` nulo — foi assim que a
regressão apareceu, num arquivo de interface que ninguém lembrou de ajustar junto com o modelo.
"""

from django.utils import timezone

from processo_seletivo.requerimentos.models import CargaDeCep, ReferenciaDeCep

CEP = "29040860"


def carga_vigente():
    """A geração que responde, criada uma vez por teste.

    **Reaproveita a existente em vez de criar outra**, porque o índice parcial único admite uma
    vigente só: duas chamadas numa mesma montagem quebrariam no banco, e o erro falaria da
    constraint em vez do cenário.
    """
    existente = CargaDeCep.objects.filter(vigente=True).first()
    if existente is not None:
        return existente
    return CargaDeCep.objects.create(
        geracao=1,
        origem="teste.zip",
        checksum="0" * 64,
        iniciada_em=timezone.now(),
        concluida_em=timezone.now(),
        vigente=True,
    )


def referencia(**campos):
    """Uma linha da base, na geração vigente. O endereço padrão é o conferido na carga real."""
    return ReferenciaDeCep.objects.create(
        **{
            "carga": carga_vigente(),
            "cep": CEP,
            "logradouro": "Rua Barão de Mauá",
            "bairro": "Jucutuquara",
            "municipio": "Vitória",
            "uf": "ES",
            "codigo_ibge": "3205309",
            **campos,
        }
    )
