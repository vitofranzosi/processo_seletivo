"""Quem entra na relação, e com que número — projeção de fatos oficiais, nunca digitação.

**A relação não aceita inclusão, exclusão nem numeração à mão** (FR-002, D-011). Ela é a projeção,
sob a versão vigente do Edital, de fatos que já existem: inscrições submetidas do recorte e, quando
o Edital declara Etapa anterior de habilitação, o Resultado vigente favorável nela. Correção
posterior segue a cadeia — fato sucedido, relação nova, ocorrência nova, ato novo —, e não a edição
de uma linha.

**A numeração é por protocolo crescente** (R-011, D-004). Precisa de regra determinística porque
entra na chave do sorteio: por instante de submissão publicaria quem chegou primeiro; por nome
dependeria de dado editável e não único; sorteá-la seria sortear antes do sorteio.

Função pura sobre dados já lidos: quem consulta o banco é a camada de aplicação. É o que permite ao
teste de projeção exercitar a regra sem montar um certame inteiro.
"""

FRASE_AMPLA = (
    "Todas as inscrições submetidas do recorte de vaga, numeradas de 1 a {n} em ordem "
    "crescente de protocolo."
)
FRASE_RESERVA = (
    "As inscrições submetidas do recorte de vaga que declararam a modalidade {modalidade}, "
    "numeradas de 1 a {n} em ordem crescente de protocolo."
)
COMPLEMENTO_DA_HABILITACAO = (
    " Entram apenas as inscrições com resultado vigente favorável na Etapa {etapa}."
)


def elegiveis(inscricoes, *, lista_id=None, habilitadas=None):
    """As inscrições que entram na relação daquele recorte, ainda sem numerar.

    `habilitadas` é o conjunto de identidades com Resultado vigente favorável na Etapa anterior de
    habilitação, quando o Edital declara uma. `None` significa que o Edital **não** declara nenhuma
    — que é o caso dos quatro Editais lidos, em que a análise documental vem depois do sorteio — e
    não que ninguém se habilitou. Confundir as duas coisas produziria relação vazia num certame
    inteiro (R-012).
    """
    selecionadas = [
        inscricao
        for inscricao in inscricoes
        if lista_id is None or str(inscricao.modality_id or "") == str(lista_id)
    ]
    if habilitadas is not None:
        selecionadas = [inscricao for inscricao in selecionadas if str(inscricao.id) in habilitadas]
    return selecionadas


def numerar(inscricoes):
    """`[(numero, inscricao), …]`, de 1 a N, por protocolo crescente.

    O desempate por identidade existe para o caso patológico de dois protocolos iguais: a ordem
    precisa ser total, ou duas projeções do mesmo universo produziriam numerações diferentes e o
    resumo da relação deixaria de ser reproduzível.
    """
    ordenadas = sorted(inscricoes, key=lambda item: ((item.protocolo or ""), str(item.id)))
    return list(enumerate(ordenadas, start=1))


def criterio(*, lista_id=None, nome_da_modalidade="", quantidade=0, nome_da_etapa=""):
    """A frase publicada de quem entrou e por quê (R-012, FR-011).

    Publicada junto com a relação porque o cidadão precisa saber **o que** aquele universo é antes
    de conferir quem está nele. Uma relação sem critério escrito é uma lista de nomes.
    """
    if lista_id is None:
        frase = FRASE_AMPLA.format(n=quantidade)
    else:
        frase = FRASE_RESERVA.format(modalidade=nome_da_modalidade or lista_id, n=quantidade)
    if nome_da_etapa:
        frase += COMPLEMENTO_DA_HABILITACAO.format(etapa=nome_da_etapa)
    return frase


def conteudo_canonico(
    *,
    relacao_id,
    edital_id,
    versao_id,
    perfil_id,
    marco_id,
    lista_id,
    metodo_hash,
    criterio_publicado,
    participantes,
):
    """O que o `resumo` da relação cobre — **e é exatamente a projeção pública** (R-015, FR-006).

    Número, nome e protocolo: os três dados que o portal mostra, e nada além. O `registrationId`
    esteve aqui e saiu: o manifesto e a FR-005 proíbem identificador interno no canal público, e
    enquanto o resumo o cobrisse o cidadão receberia um número que **não conseguiria recalcular** da
    relação que lê — teria de acreditar nele, que é a palavra que esta feature existe para não
    pedir.

    `participantes` é `[(numero, inscricao), …]`, já numerado.
    """
    return {
        "relationId": str(relacao_id),
        "editalId": str(edital_id),
        "versionId": str(versao_id),
        "profileId": str(perfil_id),
        "milestoneId": str(marco_id),
        "listId": str(lista_id) if lista_id else None,
        "methodHash": metodo_hash,
        "criterion": criterio_publicado,
        "participants": [
            {
                "publicNumber": numero,
                "name": inscricao.nome or "",
                "protocol": inscricao.protocolo or "",
            }
            for numero, inscricao in participantes
        ],
    }


__all__ = ["conteudo_canonico", "criterio", "elegiveis", "numerar"]
