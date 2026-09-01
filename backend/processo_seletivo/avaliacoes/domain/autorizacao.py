"""A segunda pergunta da autorização — e só ela.

A 011 respondeu a primeira: esta pessoa pode atuar nesta Etapa? A `012` acrescenta a segunda: esta
inscrição foi atribuída a ela? Nenhuma das duas basta sozinha, e a primeira **não se refaz aqui**:
`pode_atuar_na_etapa` é chamado, não reimplementado (P-001, FR-043).

```text
pode_atuar_na_etapa (011)  →  Atribuição ativa desta pessoa para esta inscrição  →  sim
```

São **duas** condições, e não três. O impedimento não entra na cadeia porque age antes dela,
inativando a Atribuição no ato em que é registrado: somá-lo aqui acrescentaria uma verificação por
linha a toda listagem da feature, que é o que FR-048 proíbe (FR-080).

**Rota individual usa esta função; listagem nunca usa.** Quem desenha lista chama
`etapas_autorizadas` uma vez e filtra o conjunto — o guard por linha faria dele o gargalo da
feature, que é exatamente o que a 011 antecipou ao entregar a forma em lote (FR-024, FR-048).
"""

from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.comissoes.domain.autorizacao import membro_ativo, pode_atuar_na_etapa


def atribuicao_ativa(ator, edital, etapa_id, inscricao_id):
    """A Atribuição que autoriza esta pessoa nesta inscrição, ou `None`.

    Devolve a linha, e não um booleano, porque quem autoriza costuma precisar dela em seguida — a
    Avaliação pende dali, e buscá-la de novo custaria uma consulta por acesso.
    """
    membro = membro_ativo(ator, edital.processo)
    if membro is None:
        return None
    return Atribuicao.objects.filter(
        membro=membro,
        edital=edital,
        etapa_id=etapa_id,
        inscricao_id=inscricao_id,
        ativo=True,
    ).first()


def pode_avaliar_inscricao(ator, edital, etapa_id, inscricao_id):
    """A composição, na ordem em que ela é barata: a Etapa antes da inscrição.

    Perder a alocação faz a primeira condição falhar **sem que nenhuma linha de `Atribuicao` tenha
    sido tocada** — é assim que retirar alguém de uma Etapa com quinhentas atribuições custa uma
    escrita, e devolver a alocação restaura o acesso às mesmas linhas (FR-046, FR-069, D-004).
    """
    if not pode_atuar_na_etapa(ator, edital, etapa_id):
        return None
    return atribuicao_ativa(ator, edital, etapa_id, inscricao_id)
