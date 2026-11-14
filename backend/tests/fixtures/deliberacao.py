"""O Edital da spec 165: a Heteroidentificação colegiada, com três pareceres e uma regra.

```text
1  Análise documental   pontuada, eliminatória, nota mínima 60   todas as inscrições   1 avaliação
2  Heteroidentificação  decisória, eliminatória                   só PPI               3 pareceres
3  Prova didática       pontuada, classificatória                 todas as inscrições   1 avaliação
```

O Edital da `163` e da `164` (`tests/fixtures/alcance.py`), com a Heteroidentificação colegiada. A
comissão: `maria` preside; `joao` faz a Análise; `ana`, `bruno` e `carla` dão os pareceres da
Heteroidentificação. `montar_colegiada` já consolida a Análise de todas as inscrições, de modo que a
Heteroidentificação começa com todas participando.

Função, e não fixture, pela regra de `tests/fixtures/corte.py`: cada módulo declara a sua.
"""

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PPI, rascunho_com_alcance
from tests.fixtures.comissao import ETAPA_A1, ETAPA_A2, alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original
from tests.fixtures.resultado import ETAPA_A3

PARECERISTAS = ("ana", "bruno", "carla")


def rascunho_colegiado(seed, *, regra="MAJORITY", avaliacoes=3, efeito=None, alcance=("PPI",)):
    """O rascunho acima. `regra=None` publica a Etapa colegiada **sem** regra (o acervo)."""
    rascunho = rascunho_com_alcance(seed, alcance=alcance, efeito=efeito)
    hetero = rascunho["stages"][1]
    hetero["evaluationsPerRegistration"] = avaliacoes
    hetero["deliberationRule"] = regra
    hetero["rotuloFavoravel"] = "Deferido"
    hetero["rotuloDesfavoravel"] = "Indeferido"
    return rascunho


def montar_colegiada(
    gestor,
    api_client,
    manager_headers,
    *,
    seed,
    regra="MAJORITY",
    avaliacoes=3,
    quantas=3,
    efeito=None,
    pareceristas=PARECERISTAS,
    presidencia_parecerista=False,
):
    """Publica, constitui a comissão, aloca, inscreve e consolida a Análise de todas.

    `presidencia_parecerista` aloca também `maria`, a presidência, na Heteroidentificação: é o caso
    da equipe pequena, em que quem preside também dá parecer (FR-7056).
    """
    codigo = f"165{seed}"
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"deliberacao-165-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {"number": codigo, "year": 2026, "title": f"Edital {codigo}"},
        },
        draft=rascunho_colegiado(seed, regra=regra, avaliacoes=avaliacoes, efeito=efeito),
    )
    processo = edital.processo
    pessoas = [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)]
    pessoas += [(nome, Funcao.MEMBRO) for nome in pareceristas]
    membros = constituir(gestor, processo, pessoas, prefixo=f"deliberacao-{seed}")
    analise = identificador(ETAPA_A1, seed)
    hetero = identificador(ETAPA_A3, seed)
    prova = identificador(ETAPA_A2, seed)
    alocar_em(gestor, processo, membros["joao"], edital, analise, chave=f"aloc-165-{seed}-a")
    na_hetero = list(pareceristas) + (["maria"] if presidencia_parecerista else [])
    for nome in na_hetero:
        alocar_em(gestor, processo, membros[nome], edital, hetero, chave=f"aloc-165-{seed}-{nome}")
    perfil = identificador(401, seed)
    inscricoes = inscrever(
        edital,
        quantas,
        primeiro=1,
        modalidades={indice: MODALIDADE_PPI for indice in range(quantas)},
        perfil=perfil,
    )
    cenario = {
        "edital": edital,
        "processo": processo,
        "membros": membros,
        "etapa": analise,
        "analise": analise,
        "hetero": hetero,
        "prova": prova,
        "perfil": perfil,
        "inscricoes": inscricoes,
    }
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave=f"analise-165-{seed}")
    for inscricao in inscricoes:
        concluir_como(cenario, "joao", inscricao, pontuacao="80")
    consolidar_na(cenario, analise, inscricoes, chave=f"consolidar-analise-165-{seed}")
    return cenario


def na_hetero(cenario):
    return {**cenario, "etapa": cenario["hetero"]}


def distribuir_na_hetero(cenario, gestor, inscricoes, *, nomes=PARECERISTAS, chave):
    return distribuir_para(na_hetero(cenario), gestor, list(nomes), inscricoes, chave=chave)


def concluir_pareceres(cenario, inscricao, sentidos):
    """`sentidos`: `{subject: "FAVORAVEL" | "DESFAVORAVEL"}`. Devolve as Avaliações, na ordem."""
    return [
        concluir_como(
            na_hetero(cenario),
            subject,
            inscricao,
            sentido=sentido,
            parecer=f"Parecer de {subject}: {sentido.lower()}.",
        )
        for subject, sentido in sentidos.items()
    ]


def consolidar_na(cenario, etapa, inscricoes, *, chave, ator="maria"):
    return consolidar(
        actor=ator_institucional(ator),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa,
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )
