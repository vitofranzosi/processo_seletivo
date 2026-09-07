"""As **duas** projeções do ato, e a fronteira que passa entre elas.

`compor(ato)` lê o ato, as suas posições, as inscrições consideradas e a versão normativa que ele
cita, e devolve duas coisas que **não** se misturam:

- **a pública** — o que a instituição divulga: posição, nome, protocolo, modalidade e pontuação, de
  quem recebeu posição. Sem identificador de inscrição, sem dado pessoal interno, sem valor de
  desempate (FR-018 a FR-020);
- **a individual** — uma linha por participante **considerado**, inclusive quem não recebeu
  posição, com a situação e o motivo. É o que a Área do Candidato lê, e é o que **não** atravessa a
  fronteira pública (FR-017, FR-059).

Elas vão para lugares diferentes de propósito (T-010): a pública vira `conteudo_publico`, bytes
canônicos com resumo; a individual vira linhas de `SituacaoDivulgada`. Guardá-las juntas faria toda
leitura pública carregar também o individual, e a fronteira passaria a depender de o template não
renderizar o que a view já tem em mãos.

**Todo rótulo já vem resolvido** (FR-013). Nada na renderização traduz enum nem resolve
identificador: quem lê os bytes lê texto de gente. A única exceção declarada é `marco_codigo`, que
é dado de **ordenação** e não de leitura — ver abaixo.

**`PosicaoNaOrdem.desempate` não é lido.** A coluna não aparece na consulta, e é assim que a FR-020
deixa de depender de disciplina: não há valor em mãos a filtrar depois.
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.classificacao.domain.nomes import edital_por_extenso, nomes_do_marco
from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.divulgacao.models import Natureza, SituacaoDivulgada

# As colunas que a projeção lê. `desempate` está **fora**, e a ausência é o requisito (FR-020).
COLUNAS_DA_POSICAO = (
    "inscricao_id",
    "posicao",
    "pontuacao_combinada",
    "modalidade_id",
    "consequencia",
    "motivo",
    "empate_residual",
    "inscricao__nome",
    "inscricao__protocolo",
)

ESCALA_PADRAO = 2


def compor(ato):
    """As duas projeções do ato, com os rótulos da versão que ele cita já resolvidos.

    Devolve `{"cabecalho": ..., "posicoes": ..., "situacoes": ...}`. O cabeçalho traz só o que
    existe **antes** do ato de publicar: natureza, autoridade e instante são escolha ou consequência
    do POST, e entram em `conteudo_divulgado`.
    """
    conteudo = ato.versao.content
    nomes = nomes_do_marco(conteudo, perfil_id=ato.perfil_id, marco_id=ato.marco_id)
    perfil, marco, modalidades = nomes["perfil"], nomes["marco"], nomes["modalidades"]
    escala = _escala(marco)

    linhas = list(
        PosicaoNaOrdem.objects.filter(ato=ato)
        .order_by("posicao", "inscricao__protocolo", "inscricao_id")
        .values(*COLUNAS_DA_POSICAO)
    )

    posicoes, situacoes = [], []
    for linha in linhas:
        pontuacao = _apresentar(linha["pontuacao_combinada"], escala)
        if linha["posicao"] is None:
            situacoes.append(
                {
                    "inscricao_id": linha["inscricao_id"],
                    "situacao": SituacaoDivulgada.Situacao.SEM_POSICAO,
                    "posicao": None,
                    "compartilhada": False,
                    "pontuacao": "",
                    "motivo": linha["motivo"] or "",
                }
            )
            continue
        posicoes.append(
            {
                "posicao": linha["posicao"],
                # O empate residual dito como ele é: posição compartilhada. Nenhum desempate é
                # inventado para desfazê-lo, e nenhum valor de critério atravessa (FR-014).
                "compartilhada": bool(linha["empate_residual"]),
                "candidato": linha["inscricao__nome"] or "",
                "protocolo": linha["inscricao__protocolo"] or "",
                "modalidade": modalidades.get(str(linha["modalidade_id"]), ""),
                "pontuacao": pontuacao,
            }
        )
        situacoes.append(
            {
                "inscricao_id": linha["inscricao_id"],
                "situacao": SituacaoDivulgada.Situacao.CLASSIFICADA,
                "posicao": linha["posicao"],
                "compartilhada": bool(linha["empate_residual"]),
                "pontuacao": pontuacao,
                "motivo": "",
            }
        )

    return {
        "cabecalho": {
            "processo": nomes["processo"],
            "edital": edital_por_extenso(conteudo, ato.edital),
            "perfil": perfil.get("name", "") or "",
            "marco": marco.get("name", "") or "",
            # **Dado de ordenação, não de leitura.** A 015 emite os marcos ordenados por `code`, e
            # essa é a ordem normativa em que eles se sucedem no certame. Congelá-lo é o que
            # permite à Área do Candidato ordenar os blocos sem reabrir a versão do ato — leitura
            # que a fronteira pública não faz — e sem cair na ordem em que a instituição divulgou,
            # que não é a ordem em que os marcos existem. Nem a página, nem o documento, nem a Área
            # o exibem: o que se mostra é `marco`, o nome publicado (FR-013).
            "marco_codigo": marco.get("code", "") or "",
            "ato": {"id": str(ato.id), "emitido_em": ato.emitido_em.isoformat()},
        },
        "posicoes": posicoes,
        "situacoes": situacoes,
    }


def conteudo_divulgado(composicao, *, natureza, publicado_em, signatario, retificacoes=()):
    """A forma final de `conteudo_publico` — a pública, acrescida do que o ato de publicar decide.

    **A projeção individual não entra.** O resumo publicado é o do que foi divulgado, que é o que a
    SC-004 afirma; incluí-la faria o resumo cobrir também o que não foi divulgado (T-010).

    **As causas da retificação entram, e são decididas aqui** (FR-088, FR-112). A página e o
    documento leem estes mesmos bytes, e é daí que vem a correspondência entre os dois: derivá-las
    de novo na renderização faria uma decisão posterior mudar a frase de um ato já praticado. A
    chave só existe quando há causa — divulgação que não corrige nada não carrega campo vazio.

    **São várias, e não uma.** Um ato pode citar mais de uma decisão, e a ordem em que elas entram
    é a que o selector fixa: o conteúdo entra no resumo canônico, e ordem instável faria o mesmo
    ato produzir bytes diferentes a cada publicação.
    """
    rotulo = Natureza(natureza).label
    cabecalho = composicao["cabecalho"]
    return {
        "cabecalho": {
            **cabecalho,
            "titulo": _titulo(rotulo, cabecalho["perfil"]),
            "natureza": str(natureza),
            "natureza_rotulo": rotulo,
            "publicado_em": publicado_em.isoformat(),
            "signatario_nome": signatario.nome,
            "signatario_cargo": signatario.cargo,
            **({"retificacoes": list(retificacoes)} if retificacoes else {}),
        },
        "posicoes": composicao["posicoes"],
    }


def _titulo(rotulo, perfil):
    return f"{rotulo} — {perfil}" if perfil else rotulo


def _escala(marco):
    """As casas decimais que o **marco** declarou — a apresentação não decide de novo.

    A pontuação já foi arredondada pela regra do marco quando a ordem foi calculada; aqui só se
    escreve o número com as casas que ele declara. Ler a escala de outro lugar faria a divulgação
    apresentar uma precisão que o ato não tem.
    """
    escala = (marco.get("rounding") or {}).get("scale")
    return escala if isinstance(escala, int) and escala >= 0 else ESCALA_PADRAO


def _apresentar(valor, escala):
    """`185,00` — decimal já formatado como texto, na apresentação institucional.

    Vai formatado para os bytes porque reformatar na renderização seria decidir de novo: a página
    e o documento leem os mesmos bytes, e é daí que vem a correspondência entre os dois (FR-064).
    """
    if valor is None:
        return ""
    try:
        numero = Decimal(str(valor)).quantize(Decimal(1).scaleb(-escala))
    except (InvalidOperation, TypeError, ValueError):
        return str(valor)
    return f"{numero:f}".replace(".", ",")


__all__ = ["compor", "conteudo_divulgado"]
