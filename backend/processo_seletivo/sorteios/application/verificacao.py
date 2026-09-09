"""Reproduzir a ordem **das entradas**, e nunca das posições publicadas (FR-039, FR-040, FR-049).

**A distinção é a feature inteira.** Uma verificação que lesse as posições gravadas e as comparasse
consigo mesmas sempre concordaria: ela provaria que o banco é consistente, e não que a ordem é a
que o algoritmo produz. Aqui as entradas são a relação congelada, a semente derivada e o método
citado — e a ordem é recalculada do zero.

**Nada de conteúdo vigente entra.** O método vem da versão que a relação cita, a semente vem do
material bruto registrado, os números públicos vêm dos participantes gravados. Uma Retificação
posterior não altera o veredito, porque não há nada de atual sendo lido (FR-039).

O relatório é em linguagem de gente porque o destinatário é o cidadão: "sorteio verificado, 237
participantes, relação íntegra, ordem reproduzida integralmente" diz mais do que um booleano, e,
quando falha, precisa dizer **o que** divergiu (FR-050).
"""

from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.domain import chave as dominio_da_chave
from processo_seletivo.sorteios.domain import manifesto as dominio_do_manifesto
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import normalizacao, projecao

CONFERIDO = "conferido"
DIVERGENTE = "divergente"


def reproduzir(sorteio):
    """A ordem que as entradas congeladas produzem — sem olhar para as posições gravadas.

    Devolve `(ordem, chaves, metodo, semente)`. É esta função que a `015` chamaria de "estratégia
    própria para os atos constituídos por sorteio" (FR-041): o contrato da reprodução continua o
    mesmo, e o caminho de dentro é outro porque a origem é outra.
    """
    relacao = sorteio.relacao
    metodo = dominio_do_metodo.metodo_declarado(
        relacao.versao.content, perfil_id=relacao.perfil_id, marco_id=relacao.marco_id
    )
    semente = normalizacao.normalizar(
        material_bruto=sorteio.ocorrencia.material_bruto,
        regra=((metodo or {}).get("normalization") or {}).get("rule", ""),
    )
    numeros = list(
        relacao.participantes.order_by("numero_publico").values_list("numero_publico", flat=True)
    )
    chaves = dominio_da_chave.chaves(
        relation_hash=relacao.resumo,
        draw_scope_id=dominio_da_chave.recorte(
            perfil_id=relacao.perfil_id, lista_id=relacao.lista_id
        ),
        seed=semente,
        public_numbers=numeros,
    )
    return dominio_da_chave.ordenar(chaves), chaves, metodo, semente


def verificar(sorteio):
    """Confere as quatro coisas que o cidadão precisa saber, e diz o que conferiu.

    A ordem das conferências é a da confiança: primeiro o universo — a relação publicada é a que o
    resumo diz —, depois o método comprometido, depois a semente, e só então a ordem. Uma
    divergência no primeiro degrau torna as seguintes irrelevantes, e dizer isso é mais honesto do
    que listar quatro falhas de uma causa só.
    """
    relacao = sorteio.relacao
    conferencias = []

    conferencias.append(_conferir_relacao(relacao))
    conferencias.append(_conferir_metodo(sorteio, relacao))
    ordem, chaves, metodo, semente = reproduzir(sorteio)
    conferencias.append(_conferir_semente(sorteio, semente))
    conferencias.append(_conferir_ordem(sorteio, ordem))
    conferencias.append(_conferir_manifesto(sorteio, relacao, metodo, chaves, ordem))

    integro = all(item["situacao"] == CONFERIDO for item in conferencias)
    return {
        "integro": integro,
        "quantidade": relacao.quantidade,
        "conferencias": conferencias,
        "resumo": (
            f"Sorteio verificado: {relacao.quantidade} participantes; relação íntegra; "
            "semente íntegra; ordem reproduzida integralmente."
            if integro
            else "Verificação com divergência: veja abaixo o que não confere."
        ),
    }


def _conferencia(nome, situacao, descricao):
    return {"nome": nome, "situacao": situacao, "descricao": descricao}


def _conferir_relacao(relacao):
    participantes = [
        (p.numero_publico, p.inscricao)
        for p in relacao.participantes.select_related("inscricao").order_by("numero_publico")
    ]
    recalculado = canonical_sha256(
        projecao.conteudo_canonico(
            relacao_id=relacao.id,
            edital_id=relacao.edital_id,
            versao_id=relacao.versao_id,
            perfil_id=relacao.perfil_id,
            marco_id=relacao.marco_id,
            lista_id=relacao.lista_id,
            metodo_hash=relacao.metodo_hash,
            criterio_publicado=relacao.criterio_de_projecao,
            participantes=participantes,
        )
    )
    if recalculado != relacao.resumo:
        return _conferencia(
            "A relação publicada",
            DIVERGENTE,
            "O resumo publicado da relação não corresponde aos participantes publicados nela. O "
            "universo divulgado não é o que o resumo afirma.",
        )
    return _conferencia(
        "A relação publicada",
        CONFERIDO,
        f"Os {relacao.quantidade} participantes publicados produzem exatamente o resumo "
        f"publicado da relação.",
    )


def _conferir_metodo(sorteio, relacao):
    if sorteio.metodo_hash != relacao.metodo_hash:
        return _conferencia(
            "O método comprometido",
            DIVERGENTE,
            "O sorteio cita um método diferente do que a relação comprometeu ao congelar.",
        )
    metodo = dominio_do_metodo.metodo_declarado(
        relacao.versao.content, perfil_id=relacao.perfil_id, marco_id=relacao.marco_id
    )
    if metodo is None or dominio_do_metodo.resumo_do_metodo(metodo) != relacao.metodo_hash:
        return _conferencia(
            "O método comprometido",
            DIVERGENTE,
            "O método declarado na versão do Edital que a relação cita não é o que ela "
            "comprometeu.",
        )
    return _conferencia(
        "O método comprometido",
        CONFERIDO,
        "O método usado é o que o Edital declarava quando a relação foi congelada — antes, "
        "portanto, de a semente existir.",
    )


def _conferir_semente(sorteio, semente):
    if semente != sorteio.semente_normalizada:
        return _conferencia(
            "A semente",
            DIVERGENTE,
            "A semente gravada não é a que a regra publicada produz sobre o material observado "
            "na fonte.",
        )
    return _conferencia(
        "A semente",
        CONFERIDO,
        f"O material observado na fonte, sob a regra publicada, produz exatamente a semente "
        f"usada: {semente}.",
    )


def _conferir_ordem(sorteio, ordem):
    numero_por_inscricao = {
        p.inscricao_id: p.numero_publico for p in sorteio.relacao.participantes.all()
    }
    publicada = [
        numero_por_inscricao.get(posicao.inscricao_id)
        for posicao in PosicaoNaOrdem.objects.filter(ato=sorteio.ato).order_by("posicao")
    ]
    if publicada != ordem:
        divergentes = [
            posicao + 1
            for posicao, (esperado, obtido) in enumerate(zip(ordem, publicada, strict=False))
            if esperado != obtido
        ]
        return _conferencia(
            "A ordem publicada",
            DIVERGENTE,
            "A ordem publicada não é a que o algoritmo produz a partir das entradas. Primeira "
            f"posição divergente: {divergentes[0] if divergentes else len(ordem) + 1}.",
        )
    return _conferencia(
        "A ordem publicada",
        CONFERIDO,
        f"As {len(ordem)} posições publicadas são exatamente as que o algoritmo produz a partir "
        "da relação, da semente e do método.",
    )


def _conferir_manifesto(sorteio, relacao, metodo, chaves, ordem):
    if metodo is None:
        return _conferencia(
            "O manifesto", DIVERGENTE, "Sem método declarado não há manifesto a derivar."
        )
    resumo = dominio_do_manifesto.resumo_do_manifesto(
        dominio_do_manifesto.derivar(
            sorteio=sorteio, relacao=relacao, metodo=metodo, chaves=chaves, ordem=ordem
        )
    )
    if resumo != sorteio.manifesto_hash:
        return _conferencia(
            "O manifesto",
            DIVERGENTE,
            "O manifesto regenerado das entradas não produz o resumo gravado no ato.",
        )
    return _conferencia(
        "O manifesto",
        CONFERIDO,
        "O manifesto regenerado das entradas produz exatamente o resumo publicado com o ato.",
    )


def manifesto_publicado(sorteio):
    """O manifesto regenerado, pronto para download (FR-047, R-007)."""
    ordem, chaves, metodo, _semente = reproduzir(sorteio)
    return dominio_do_manifesto.publicar(
        dominio_do_manifesto.derivar(
            sorteio=sorteio, relacao=sorteio.relacao, metodo=metodo, chaves=chaves, ordem=ordem
        )
    )


__all__ = ["CONFERIDO", "DIVERGENTE", "manifesto_publicado", "reproduzir", "verificar"]
