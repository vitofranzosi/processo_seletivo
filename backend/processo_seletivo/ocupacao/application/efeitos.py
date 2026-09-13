"""A porta de efeitos: como a `019` mexe no conjunto de ocupantes de um recorte (019, `R-003`).

**Uma função, e a assinatura é o contrato.** A `D-006` fixou que a exclusão chega por porta que a
`016` define, para a seta continuar `ocupacao → classificacao` e nunca o contrário. Este módulo
**é** essa porta: a `019` a chama, e `ocupacao` não importa `convocacao` em lugar nenhum.

**O que esta camada exige, e o que ela recusa saber.** Exige fundamento e proveniência — quem
originou o efeito, com rótulo legível. Recusa saber o que é convocação, desfecho ou suplência: para
ela, uma inscrição saiu do conjunto de ocupantes ou entrou nele. Quem dá sentido ao fundamento é
quem o escreveu (`FR-296`).

**Nenhuma apuração é reescrita aqui.** O efeito registrado torna a apuração vigente **obsoleta** —
causa nomeada em `selectors.causas_de_obsolescencia` —, e o número novo sai na **emissão seguinte**
(`D-006`). Escrever na apuração seria `UPDATE` em tabela append-only, e o provisionamento instala a
proibição que barra isso.
"""

from django.db import transaction

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import EfeitoDeOcupacao
from processo_seletivo.shared.api.problems import DomainError


def registrar_efeito(
    *,
    edital,
    perfil_id,
    marco_id,
    inscricao_id,
    especie,
    fundamento,
    ato_de_origem_id,
    rotulo_da_origem,
    registrado_por,
    registrado_em,
    lista_id=None,
):
    """Grava um efeito de ocupação e devolve a linha criada.

    **Transacional, e chamada de dentro da transação de quem desfecha.** O desfecho e o efeito que
    ele produz são um fato só: gravar um sem o outro deixaria ou uma exclusão sem causa, ou um
    desfecho que prometeu mexer no número e não mexeu. `atomic` aninhado vira savepoint, que é
    exatamente o comportamento desejado quando `desfechar` já abriu a sua.
    """
    especie = (especie or "").strip()
    if especie not in nomes.ESPECIES_DE_EFEITO:
        raise DomainError(
            nomes.ESPECIE_DE_EFEITO_INVALIDA,
            "O efeito de ocupação é exclusão ou inclusão, e nada mais.",
            422,
            campo="especie",
        )
    texto = (fundamento or "").strip()
    if not texto:
        # **Recusado aqui e no banco, e as duas não são redundantes.** O `CHECK` vale para quem
        # chegue por fora da aplicação; esta recusa é a que nomeia o campo para quem está na tela.
        raise DomainError(
            nomes.FUNDAMENTO_OBRIGATORIO,
            "Declare o fundamento do efeito de ocupação.",
            422,
            campo="fundamento",
        )
    rotulo = (rotulo_da_origem or "").strip()
    if not ato_de_origem_id or not rotulo:
        # **Proveniência não é opcional** (`FR-294`). Sem ela o efeito seria um número que mudou
        # sem ato que o explique — e a `016` não tem como perguntar à `019` de onde ele veio: o
        # `ato_de_origem_id` é opaco justamente para que ela não precise.
        raise DomainError(
            nomes.PROVENIENCIA_OBRIGATORIA,
            "Declare o ato que originou o efeito e o rótulo que o descreve.",
            422,
            campo="ato_de_origem_id",
        )
    with transaction.atomic():
        return EfeitoDeOcupacao.objects.create(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            inscricao_id=inscricao_id,
            especie=especie,
            fundamento=texto,
            ato_de_origem_id=ato_de_origem_id,
            rotulo_da_origem=rotulo,
            registrado_por=registrado_por,
            registrado_em=registrado_em,
        )


def efeitos_do_recorte(*, edital, perfil_id, marco_id, lista_id=None):
    """Os efeitos do recorte, **na ordem em que foram registrados**.

    A ordem não é decoração: `apuracao.ocupantes` aplica o último efeito de cada pessoa, e é ela que
    faz a suplente que aceitou e depois teve a matrícula cancelada sair da contagem. Sem `order_by`,
    o PostgreSQL não promete ordem nenhuma, e o número mudaria entre duas leituras iguais.
    """
    return list(
        EfeitoDeOcupacao.objects.filter(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        ).order_by("registrado_em", "id")
    )


def efeitos_lidos_por(efeitos):
    """`(especie, inscricao_id)` na forma que `apuracao.apurar` consome."""
    return [(efeito.especie, efeito.inscricao_id) for efeito in efeitos]


__all__ = ["efeitos_do_recorte", "efeitos_lidos_por", "registrar_efeito"]
