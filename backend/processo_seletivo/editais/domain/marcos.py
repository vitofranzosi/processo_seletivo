"""As regras **derivadas** do marco classificatório, num lugar só (030).

Três perguntas que a tela, a validação, o cálculo e os serializers fazem — e que, antes desta
feature, cada um respondia por conta própria:

1. **Este marco ordena por sorteio?** Até aqui era inferido da presença de `drawMethod`, em cinco
   lugares diferentes. A inferência não distingue *não sorteia* de *sorteia e ainda não declarei o
   método*, que é justamente o estado de quem acabou de acrescentar um marco de sorteio (FR-414).
   A FR-413 criou a informação que faltava; este módulo é onde ela é lida.

2. **Este marco precisa enumerar Etapa?** Precisa quando a ordem nasce da pontuação, e não precisa
   quando nasce de sorteio — o sorteio costuma preceder a análise documental, e a ajuda da própria
   tela já mandava deixar a habilitação em nenhuma. A validação exigia Etapa de todos porque não
   tinha como distinguir os dois (FR-432).

3. **Com uma Etapa só, o que a combinação faz?** É a regra derivada de FR-416, e o princípio IV da
   Constituição exige que ela seja derivada **uma vez**: escrevê-la no template e no cálculo seriam
   duas respostas para a mesma pergunta.

**Por que aqui, e não no app do sorteio.** O que estas funções leem é conteúdo do marco, que é do
`editais`. `sorteios/domain/metodo` continua sendo o ponto único do *método* — qual método governa
um marco —, que é outra pergunta.

**A ausência é lida, e nunca preenchida.** Marco composto antes desta feature tem `""`, e sobre ele
estas funções devolvem exatamente o comportamento de sempre. Nada aqui retroage a conteúdo
publicado (FR-431, SC-142).
"""

POR_PONTUACAO = "POR_PONTUACAO"
POR_SORTEIO = "POR_SORTEIO"

#: A combinação que torna verdadeira a declaração de FR-416 — "com uma Etapa, a pontuação combinada
#: é a dela".
#:
#: **Média, e não soma.** `combinar` multiplica a pontuação pelo peso publicado da Etapa: a soma
#: ponderada de uma Etapa só devolve `nota × peso`, que é a nota apenas quando o peso é 1. A média
#: divide pela soma dos pesos e devolve a nota, qualquer que seja o peso — que é o que a tela
#: declara e o que quem compõe espera ler.
REGRA_DE_ETAPA_UNICA = {"operation": "MEDIA_PONDERADA", "normalization": "NENHUMA"}

#: O arredondamento que o marco **novo** já traz preenchido, e editável (FR-419).
#:
#: **É o que o próprio projeto pratica onde já escolheu**: `seed_demo` usa este par nos dois
#: Editais que semeia, e as fixtures de referência o repetem. Duas obrigatórias sem valor padrão
#: eram duas das vinte e oito perguntas do Edital mais simples — e pedir arredondamento a quem
#: ainda não sabe o que se arredonda é o ponto em que a auditoria observou a primeira hesitação.
#:
#: **Padrão de marco novo, e nunca de marco existente** (FR-421): ele nasce no fragmento que cria a
#: linha, e não na releitura do que já foi declarado. Retificação não o vê chegar por conta própria.
ARREDONDAMENTO_PADRAO = {"scale": 2, "mode": "MEIO_PARA_CIMA"}


def identidade_derivada(*, codigo_do_perfil, nome_do_perfil, codigos_em_uso=()):
    """`(code, name)` iniciais do marco, derivados do Perfil a que ele pertence (FR-420).

    **Do Perfil, e não de um catálogo**: quem acrescenta um marco acabou de ler o Perfil, e não tem
    de inventar um código para um objeto cujo nome leu pela primeira vez há um instante. Os dois
    continuam editáveis — o que se entrega é um começo verdadeiro, e não uma decisão tomada.

    `uq_marco_perfil_code` continua valendo, e por isso o desempate: um Perfil com dois marcos
    precisa de dois códigos, e um fragmento que entregasse o mesmo produziria uma recusa na
    gravação que ninguém pediu.
    """
    base = (codigo_do_perfil or "").strip()
    nome = f"Classificação final — {nome_do_perfil}".strip(" —") if nome_do_perfil else ""
    if not base:
        return "", nome
    em_uso = {str(item) for item in codigos_em_uso}
    if base not in em_uso:
        return base, nome
    sufixo = 2
    while f"{base}-{sufixo}" in em_uso:
        sufixo += 1
    return f"{base}-{sufixo}", nome


def ordena_por_sorteio(forma_da_ordem, *, metodo_declarado) -> bool:
    """A ordem deste marco nasce de sorteio?

    `forma_da_ordem` é o que o marco declara — `""` quando não declara nada. `metodo_declarado` é
    se ele carrega método de sorteio, que é a única evidência que existia antes da FR-413 e que
    continua valendo para todo Edital publicado antes dela.
    """
    if forma_da_ordem == POR_SORTEIO:
        return True
    if forma_da_ordem == POR_PONTUACAO:
        return False
    return bool(metodo_declarado)


def exige_etapa(forma_da_ordem, *, metodo_declarado) -> bool:
    """Este marco precisa enumerar ao menos uma Etapa? (FR-432)

    **A exigência não foi removida — foi condicionada.** Quem ordena por pontuação continua
    precisando de Etapa: sem Etapa não há pontuação a combinar, e a ordem não sai. Quem ordena por
    sorteio não precisa, porque a ordem vem da relação de habilitados e não de nota nenhuma.

    O marco que não declara a forma **continua exigindo Etapa**, como sempre exigiu: é o estado de
    todo Edital anterior a esta feature, e afrouxar a regra sobre ele mudaria o que já se publicou.
    """
    if forma_da_ordem == POR_SORTEIO:
        return False
    return True


def pergunta_a_combinacao(etapas) -> bool:
    """A combinação e a normalização são perguntadas? Só com **duas ou mais** Etapas (FR-415).

    Com uma, a resposta é dedutível do que já foi declarado — e SC-139 proíbe perguntar o que é
    dedutível. Com nenhuma, não há o que combinar.
    """
    return len(etapas or []) >= 2


def combinacao_efetiva(*, operacao, normalizacao, etapas):
    """A combinação que este marco aplica — declarada quando declarada, derivada quando não.

    **A derivação não sobrescreve declaração** (FR-421). Um marco composto antes desta feature pode
    enumerar uma Etapa e declarar soma ponderada; a tela deixa de perguntar, e o que ele declarou
    permanece. O que se deriva é o vazio — o marco novo, que nunca respondeu.

    Com duas ou mais Etapas a pergunta volta a ser feita, e nada se deriva aqui: o que falta é
    cobrado na publicação, como sempre foi.
    """
    if pergunta_a_combinacao(etapas):
        return {"operation": operacao or "", "normalization": normalizacao or ""}
    return {
        "operation": operacao or REGRA_DE_ETAPA_UNICA["operation"],
        "normalization": normalizacao or REGRA_DE_ETAPA_UNICA["normalization"],
    }


def pontuacao_combinada_e_a_da_etapa(*, operacao, normalizacao) -> bool:
    """A combinação declarada devolve a pontuação da Etapa única, sem alterá-la? (FR-416)

    Serve à frase que a tela escreve. Ela precisa ser **verdadeira sobre este marco**, e não sobre
    o caso comum: um marco antigo que declarou soma ponderada sobre uma Etapa de peso 2 publica o
    dobro da nota, e dizer-lhe que "a pontuação combinada é a dela" seria mentir na tela onde a
    pessoa decide.
    """
    if normalizacao == "PELA_SOMA_DOS_PESOS":
        return True
    return operacao == REGRA_DE_ETAPA_UNICA["operation"]


def marco_no_conteudo(conteudo, *, perfil_id, marco_id):
    """O marco, dentro do Perfil, no conteúdo publicado. `None` quando não existe.

    **Atravessa conteúdo malformado sem quebrar**, e a guarda não é zelo: desde a `032` esta
    leitura é chamada de dentro de `validate_for_publication`, que roda sobre conteúdo que ainda
    não foi conferido — um Perfil que é string em vez de objeto é exatamente o que a validação
    existe para acusar. Uma exceção aqui apagaria todos os achados seguintes, inclusive o que diz
    **por que** o conteúdo está malformado.
    """
    for perfil in (conteudo or {}).get("profiles") or []:
        if not isinstance(perfil, dict) or str(perfil.get("id")) != str(perfil_id):
            continue
        for marco in perfil.get("classificationMilestones") or []:
            if isinstance(marco, dict) and str(marco.get("id")) == str(marco_id):
                return marco
    return None


def metodo_que_governa(conteudo, *, perfil_id, marco_id):
    """O método de sorteio que governa este marco — o dele, senão o comum do Edital (FR-429).

    **O ponto único de resolução.** Sete Perfis de sorteio declaravam a mesma regra sete vezes —
    mesmo algoritmo, mesma fonte, mesma ocorrência —, porque o sorteio é **um evento**: a mesma
    extração semeia todas as listas do certame. O Edital passa a poder declará-la uma vez, e cada
    marco a referencia.

    **A divergência vem primeiro, e é ela que o marco carrega** (FR-430): quem declarou o próprio
    método quis o próprio, e a divergência se lê do documento sem inferência — a chave está lá,
    preenchida, sob o marco.

    **Nada disto alcança Edital publicado antes desta feature** (FR-431, SC-142): cada marco dele
    carrega o método literal, e é exatamente esse que a resolução devolve. A chave do Edital não
    existe naquele conteúdo.

    **Por que aqui, e não no app do sorteio.** A `021` decidiu por escrito que a dependência corre
    `sorteios → classificacao`, e nunca o contrário — e `classificacao` é um dos leitores desta
    pergunta. Pôr a regra em `sorteios/domain/metodo` obrigaria `classificacao` a importá-lo e
    inverteria a direção; pô-la aqui não inverte nada, porque o que se lê é conteúdo do **marco**,
    que é do `editais`. `sorteios/domain/metodo` continua sendo o ponto de leitura do método no
    conteúdo versionado: ele delega para cá, e nada duplica.
    """
    marco = marco_no_conteudo(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    if marco is None:
        # Sem marco não há o que referenciar, e devolver o comum do Edital responderia sobre um
        # marco que não existe: quem chama precisa distinguir as duas ausências.
        return None
    proprio = marco.get("drawMethod") or None
    if proprio is not None:
        return proprio
    return (conteudo or {}).get("drawMethod") or None


def marco_ordena_por_sorteio(conteudo, *, perfil_id, marco_id) -> bool:
    """Este marco, no conteúdo publicado, produz a ordem por sorteio? (FR-414)

    A regra é a de `ordena_por_sorteio`, acima — a mesma que a tela e a validação aplicam. O que
    esta função acrescenta é achar o marco na versão e **resolver o método comum antes de
    perguntar**: um marco que referencia o método do Edital sorteia, e quem lesse só a chave dele
    concluiria que não.
    """
    marco = marco_no_conteudo(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    if marco is None:
        return False
    return ordena_por_sorteio(
        marco.get("orderProduction") or "",
        metodo_declarado=bool(metodo_que_governa(conteudo, perfil_id=perfil_id, marco_id=marco_id)),
    )
