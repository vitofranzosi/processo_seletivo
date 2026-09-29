"""A janela recursal declarada pelo Edital — o degrau 8, e o que a ausência dela significa.

**A ausência é uma afirmação, e não uma omissão a corrigir** (FR-028, FR-029). Edital que não
declara janela não tem prazo de zero dias: tem prazo não computável, e a tempestividade volta a ser
juízo humano motivado, que é a degradação declarada pela D-004.

**A contagem exclui o dia do começo e inclui o do vencimento** — a regra geral do processo
administrativo —, e fecha ao fim do último dia na zona institucional. **Sem prorrogação**:
prorrogar o vencimento que cai em dia sem expediente exige um calendário de feriados que o Edital
não publica, e é a mesma razão pela qual a unidade é dias corridos (D-004, FR-023).

**A âncora é a publicação que divulgou pela primeira vez aquele ato** (FR-025). Publicar de novo o
**mesmo** ato mudando só a natureza não abre janela nova: nada de novo foi divulgado para se
contestar. Publicar ato **diferente** abre, porque contra ele ninguém recorreu ainda. A comparação
é por **identidade do ato**, e não por resumo do conteúdo — o resumo mudaria só por causa do rótulo
da natureza no cabeçalho.

**Publicação atrasada não produz prazo vencido antes de existir**: a janela abre no instante em que
a publicação existe, e não na data que alguém digitou no Cronograma. É por isso que a âncora é o
ato, e não uma data absoluta.
"""

from datetime import datetime, time, timedelta

from processo_seletivo.shared.tempo import ZONA

UNIDADE_ADMISSIVEL = "DIAS_CORRIDOS"


def declaracao_do_marco(conteudo, marco_id):
    """O objeto `appealWindow` daquele marco no conteúdo publicado, ou `None`."""
    alvo = str(marco_id)
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == alvo:
                return marco.get("appealWindow")
    return None


def admite_recurso(declaracao):
    """`True`, `False` ou `None` — e os três são respostas diferentes (FR-020).

    ```text
    None    o Edital não declarou nada sobre recurso naquele marco
    False   o Edital declarou que aquele marco NÃO admite recurso por esta via
    True    admite, e a duração diz por quanto tempo
    ```

    **Confundir `False` com `None` transforma "não cabe recurso" em "cabe para sempre"** — que é o
    oposto exato do que a norma disse. A ausência é silêncio, e o silêncio devolve a tempestividade
    ao juízo humano; a negativa é norma publicada, e norma publicada se aplica.
    """
    if not isinstance(declaracao, dict):
        return None
    admite = declaracao.get("admits")
    return None if admite is None else bool(admite)


def computavel(declaracao):
    """A janela é computável quando o Edital declara que o marco admite recurso **e por quanto**.

    Três coisas que não são janela computável, e as três chegam como `None` de propósito:

    ```text
    ausente ou nula   →  janela não declarada (todo Edital anterior ao degrau 8)
    admits falso      →  o marco não admite recurso por essa via
    sem duração       →  declarada e não computável: não há o que contar
    ```

    A validação na publicação recusa a terceira como erro de conteúdo; aqui ela é lida como
    ausência, porque um Edital já publicado com esse defeito não pode travar a leitura.
    """
    if not isinstance(declaracao, dict):
        return None
    if not declaracao.get("admits"):
        return None
    duracao = declaracao.get("durationDays")
    if not isinstance(duracao, int) or duracao <= 0:
        return None
    if str(declaracao.get("unit") or UNIDADE_ADMISSIVEL) != UNIDADE_ADMISSIVEL:
        return None
    return {"dias": duracao, "unidade": UNIDADE_ADMISSIVEL}


def declaracao_aplicavel(citada, vigente):
    """A declaração que governa o prazo de um ato divulgado: a citada, salvo se a vigente concede.

    **Decidido pelo usuário em 28/09, em duas perguntas** (RC-121; o registro está em
    `doc/registro-pre-piloto-2026-09-28.md`, *O que foi decidido*). A janela recursal de ato já
    divulgado segue a versão do Edital que o ato citou, e não a vigente: uma Retificação que
    **encurte** ou **retire** a janela não alcança o prazo de resultado já divulgado. Antes, a
    interposição lia a vigente, e encurtar alcançava.
    A Retificação que **concede** alcança: a janela que nasce onde o ato citava silêncio ou negativa
    (a `048`, caso-limite *"Janela que nasce depois da divulgação"*), e o prazo maior do que o
    citado (a `026`, US3 e `SC-099`: o prazo publicado curto demais se corrige, e o candidato lê a
    data nova). É a razão que o contrato já dava para a janela ser retificável — conceder é menos
    grave do que retirar — tornada regra dos dois lados.

    Função pura sobre os dois objetos `appealWindow`; quem os lê do conteúdo é quem chama.
    """
    nova = computavel(vigente)
    if nova is None:
        return citada
    antiga = computavel(citada)
    if antiga is None or nova["dias"] > antiga["dias"]:
        return vigente
    return citada


def janela_do_ato(ato, marco_id, *, vigente=None):
    """A janela computável que governa o ato, pela versão que ele cita e pela vigente (RC-121).

    **O ato, e não a publicação**, porque a janela conta da publicação que divulgou o ato pela
    primeira vez (`ancora`), e toda publicação da cadeia até ela divulga o mesmo ato — a versão
    citada é uma só. Serve também ao ato que ainda vai ser divulgado: a declaração que a definitiva
    exige depende da janela que vai valer para ele depois, e ela sai daqui, pela mesma regra.

    `vigente` é o conteúdo vigente, quando quem chama já o tem; sem ele, a função o lê.
    """
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    if vigente is None:
        vigente = conteudo_vigente(ato.edital)
    return computavel(
        declaracao_aplicavel(
            declaracao_do_marco(ato.versao.content, marco_id),
            declaracao_do_marco(vigente, marco_id),
        )
    )


def contar(*, abertura, dias):
    """`(abre, fecha)` — a janela que uma publicação naquele instante produz.

    Exclui-se o dia do começo e inclui-se o do vencimento: uma janela de 5 dias aberta numa
    terça-feira fecha ao fim do domingo seguinte, e não ao fim do sábado. O erro de um dia aqui é o
    erro que tira o recurso de alguém, e é por isso que a regra é escrita e não deduzida.

    O encerramento é o **último instante** do dia do vencimento na zona institucional — quem
    interpõe às 23h59 do último dia está dentro do prazo, e o segundo seguinte já não está.
    """
    local = abertura.astimezone(ZONA)
    vencimento = (local + timedelta(days=int(dias))).date()
    fecha = datetime.combine(vencimento, time.max, tzinfo=ZONA)
    return abertura, fecha


def ancora(publicacao):
    """A publicação que divulgou **pela primeira vez** o ato que esta publica (FR-025).

    Sobe a cadeia enquanto a antecessora divulgar o **mesmo** ato. Republicar o mesmo ato mudando a
    natureza não abre prazo novo: quem já teve a chance de recorrer daquele conteúdo a teve. Ato
    diferente interrompe a subida, e a janela conta da publicação que o trouxe.
    """
    corrente = publicacao
    while corrente is not None:
        anterior = corrente.publicacao_anterior
        if anterior is None or anterior.ato_id != corrente.ato_id:
            return corrente
        corrente = anterior
    return publicacao


def janela_da_publicacao(publicacao, declaracao):
    """`(abre, fecha)` da publicação vigente sob a norma declarada, ou `None`.

    `None` em duas situações que são a mesma coisa para quem lê: não há janela declarada, ou não há
    publicação. Nos dois casos o sistema **não inventa prazo**.
    """
    computada = computavel(declaracao)
    if publicacao is None or computada is None:
        return None
    return contar(abertura=ancora(publicacao).publicado_em, dias=computada["dias"])


__all__ = [
    "UNIDADE_ADMISSIVEL",
    "ancora",
    "computavel",
    "contar",
    "declaracao_aplicavel",
    "declaracao_do_marco",
    "janela_da_publicacao",
    "janela_do_ato",
]
