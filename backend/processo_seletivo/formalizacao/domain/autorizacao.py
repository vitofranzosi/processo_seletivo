"""O predicado único do acesso à documentação da formalização (117, FR-3664 a FR-3667).

**Um lugar decide**, para a página, cada arquivo, a verificação e a exportação. Quatro condições, na
mesma requisição:

1. a unidade ativa é a do Edital — senão, **inexistente** (404), porque o ator não deve saber o que
   há fora do seu escopo (`033`);
2. o ator tem a capacidade do papel Formalização na unidade ativa — senão, a **recusa de
   autorização**, nomeando o papel (FR-3666);
3. há designação vigente do ator no Edital — senão, inexistente;
4. a designação cobre o Perfil da pessoa, e a pessoa está apta — senão, inexistente.

A quarta condição tem duas metades, e esta camada responde a primeira: se a pessoa está apta, quem
sabe é o seletor do conjunto, que lê o desfecho na hora (FR-3669).

**O papel e a suspensão não se conferem aqui**, porque já se conferem antes: a capacidade vem dos
vínculos vigentes, recalculados a cada requisição, e a pessoa suspensa não tem ator. É por isso que
revogar o papel corta todas as designações de uma vez, e suspender corta tudo (FR-3667).

**Disjunto da conferência** (FR-3665): nada aqui alcança a página dos documentos da convocação da
`115`, a condução ou o dossiê, e nada lá alcança o que está aqui.
"""

from dataclasses import dataclass

from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import DesignacaoParaFormalizacao
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import (
    Base,
    require_authorization_base,
)
from processo_seletivo.shared.api.problems import DomainError

#: A base que falta a quem não tem o papel (FR-3666). **Papel, e não permissão**: é assim que a
#: gestão de acessos o concede, e é a quem a administra que se pede.
BASE_DO_PAPEL = Base(f"o papel {nomes.NOME_DO_PAPEL}", "a quem administra os acessos da unidade")


def inexistente():
    return DomainError("not_found", "Recurso não encontrado.", 404)


@dataclass(frozen=True)
class Acesso:
    """O que o predicado decidiu: o Edital e a designação que autoriza."""

    edital: object
    designacao: DesignacaoParaFormalizacao

    def cobre(self, perfil_id):
        return self.designacao.cobre(perfil_id)


def designacoes_vigentes(*, pessoa=None, edital=None):
    designacoes = DesignacaoParaFormalizacao.objects.filter(revogacao__isnull=True)
    if pessoa is not None:
        designacoes = designacoes.filter(pessoa=pessoa)
    if edital is not None:
        designacoes = designacoes.filter(edital=edital)
    return designacoes


def exigir_o_papel(actor):
    """A capacidade do papel, ou a recusa que o nomeia (FR-3666)."""
    require_authorization_base(actor.can(nomes.CAPACIDADE), bases=[BASE_DO_PAPEL])


def pode_acessar(actor, edital_id, *, perfil_id=None):
    """`Acesso`, ou a recusa da matriz: 404 fora do alcance, 403 sem o papel.

    `perfil_id`, quando dado, é o Perfil da pessoa que se quer alcançar: fora da designação, ela é
    inexistente para este ator (FR-3666).
    """
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise inexistente()
    exigir_o_papel(actor)
    designacao = (
        designacoes_vigentes(pessoa=actor.subject, edital=edital)
        .order_by("-designado_em", "-id")
        .first()
    )
    if designacao is None:
        raise inexistente()
    if perfil_id is not None and not designacao.cobre(perfil_id):
        raise inexistente()
    return Acesso(edital=edital, designacao=designacao)
