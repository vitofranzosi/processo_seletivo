"""O manifesto público, derivado deterministicamente (021, FR-042, FR-043, R-007).

**Derivado, e não copiado.** O que se grava no `Sorteio` é o `manifestHash`; o download regenera o
pacote a partir da relação congelada, do método citado, da ocorrência e do ato. Guardar os bytes
seria guardar uma segunda verdade a manter coerente com a primeira.

**Estável por construção** (regra 4 do contrato): tudo o que entra aqui é histórico e imutável — a
versão que a relação cita, o material bruto observado, os instantes gravados. Dois downloads do
mesmo sorteio produzem bytes idênticos porque não há nada de vigente sendo lido.

**Sem dado pessoal além do que a relação publicada já expõe** (FR-044): o participante é
identificado por `publicNumber`, e só. A relação publicada mostra nome e protocolo, e é dela que o
verificador recalcula o `relationHash` — o manifesto não precisa repeti-los para ser conferível.
"""

from processo_seletivo.shared.canonical import canonical_sha256

VERSAO_DO_MANIFESTO = 1


def derivar(*, sorteio, relacao, metodo, chaves, ordem):
    """O objeto do manifesto, sem o campo `manifestHash`.

    `participants` sai **ordenado por número público**, e não por posição: quem confere lê a
    entrada, não o resultado. Uma lista já em ordem de sorteio convidaria a conferir o que se quer
    provar (regra 2 do contrato).
    """
    posicao_por_numero = {numero: posicao for posicao, numero in enumerate(ordem, start=1)}
    return {
        "manifestVersion": VERSAO_DO_MANIFESTO,
        "drawId": str(sorteio.id),
        "process": {
            "processId": str(relacao.edital.processo_id),
            "editalId": str(relacao.edital_id),
            "editalNumber": f"{relacao.edital.number}/{relacao.edital.year}",
            "versionId": str(relacao.versao_id),
        },
        "scope": {
            "profileId": str(relacao.perfil_id),
            "milestoneId": str(relacao.marco_id),
            "listId": str(relacao.lista_id) if relacao.lista_id else None,
        },
        "method": {
            **metodo,
            # O resumo que a relação gravou ao congelar: é ele que prova que este método é o que o
            # universo comprometeu, e não um que tenha vindo depois (FR-067).
            "methodHash": relacao.metodo_hash,
        },
        "relation": {
            "relationId": str(relacao.id),
            "criterion": relacao.criterio_de_projecao,
            "count": relacao.quantidade,
            "publishedAt": relacao.publicada_em.isoformat(),
            "relationHash": relacao.resumo,
        },
        "seed": {
            "source": sorteio.ocorrencia.fonte,
            "occurrence": sorteio.ocorrencia.referencia,
            "rawMaterial": sorteio.ocorrencia.material_bruto,
            "normalized": sorteio.semente_normalizada,
            "observedAt": sorteio.ocorrencia.observada_em.isoformat(),
        },
        "execution": {"executedAt": sorteio.executado_em.isoformat()},
        "participants": [
            {
                "publicNumber": numero,
                "key": chaves[numero],
                "position": posicao_por_numero[numero],
            }
            for numero in sorted(chaves)
        ],
    }


def resumo_do_manifesto(manifesto) -> str:
    """`canonical_sha256` do objeto **sem** o próprio campo — como o contrato declara."""
    return canonical_sha256({k: v for k, v in manifesto.items() if k != "manifestHash"})


def publicar(manifesto):
    """O manifesto com o seu resumo dentro, que é a forma que o download entrega."""
    return {**manifesto, "manifestHash": resumo_do_manifesto(manifesto)}


__all__ = ["VERSAO_DO_MANIFESTO", "derivar", "publicar", "resumo_do_manifesto"]
