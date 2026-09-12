"""Escrever, na forma nova, o que o conteúdo antigo já dizia por omissão.

O incremento da `012` acrescentou duas propriedades à Etapa publicada e subiu a versão canônica de
4 para 5. Sem conversão, todo Edital publicado antes dele ficaria travado na primeira comparação de
`_assert_versao_canonica`, e deixar de ser retificável por evolução de esquema é consequência de
produto — não detalhe de implantação (012, D-002).

**Por que converter aqui é legítimo, e não era nos incrementos anteriores.** A recusa do mecanismo
nasceu com o comentário de que a alternativa "construiria compatibilidade para conteúdo que não
existe", e isso era exato: 2 → 3 e 3 → 4 acrescentaram seções ao catálogo e a coleção
`documentRequirements` inteira, e qualquer valor inventado para elas seria afirmação normativa —
dizer que um Edital não exige documento algum **é dizer alguma coisa**. Este incremento é aditivo
sobre uma coleção que já existe, e a spec declara o que a ausência significa: uma avaliação por
inscrição, limite não declarado (FR-009, FR-066). A função abaixo não escolhe nada.

**Onde ela roda, e onde não roda.** Só dentro do fluxo de Retificação — elaboração, composição,
consolidação —, e sobre o conteúdo **lido**. Nenhuma linha de `VersaoConsolidada`, `Publicacao` ou
`AlteracaoNormativa` é escrita. Fora desse fluxo nada é elevado: a consulta pública, o comprovante e
o documento de uma Publicação já existente servem o conteúdo **literal**, que é o que o
`content_hash` cobre — elevar ali faria a tela mostrar uma coisa e o hash provar outra (T-002).

**Por que ela alcança os atos, e não só a base.** A consolidação não parte da última versão: parte
do conteúdo original e reaplica todos os atos publicados, que carregam o valor literal gravado
quando foram elaborados. Um ato v4 que acrescentou Etapa reintroduziria essa Etapa fora de forma, e
a publicação inteira falharia na materialização — nada inválido fica gravado, porque a transação
reverte, mas um ato legítimo e já homologado se tornaria impublicável (T-001).

**Por que não é preciso etiquetar cada ato com a versão em que nasceu.** A elevação é idempotente:
entidade que já tem as duas propriedades atravessa inalterada, e `null` continua `null`, porque
ausente e nulo significam a mesma coisa. Aplicá-la incondicionalmente produz o mesmo resultado que
uma consolidação etiquetada por versão produziria, sem armazenar versão por ato.
"""

from processo_seletivo.shared.canonical import SCHEMA_VERSION

# O que a ausência de cada propriedade quer dizer, **por degrau**, dito uma vez. É a mesma leitura
# que `avaliacoes/domain/previsao.py` aplica no consumo; aqui ela vira grafia.
#
# `forma` é o único que a elevação escreve com valor, e ela pode fazê-lo porque a spec declara o
# que a ausência significa: até a versão 5 o domínio não admitia outra forma, e escrever "PONTUADA"
# não afirma nada que o conteúdo já não dissesse (012, FR-120). Os rótulos continuam nulos, porque
# na forma pontuada não há sentido a nomear.
DEGRAUS = {
    5: {"evaluationsPerRegistration": 1, "maximumScore": None},
    6: {"forma": "PONTUADA", "rotuloFavoravel": None, "rotuloDesfavoravel": None},
}

# **O degrau 7 não é de Etapa, e é o primeiro que não é.** A leva da `015` acrescentou uma coleção
# dentro do Perfil — duas, na verdade — e um campo na raiz do conteúdo. Os dois dicionários abaixo
# existem separados de `DEGRAUS` por isso: cada um responde por um **nível** da árvore, e fundi-los
# obrigaria a função a descobrir onde cada chave mora, que é o modo de falha que este módulo recusa
# em toda parte — decidir por presença de chave em vez de por posição declarada.
#
# O que a ausência de cada um significa, e por que escrevê-la não inventa nada: Edital publicado
# antes da `015` não declarou marco (e Edital sem marco não classifica), não exigiu fato do
# candidato, e não limitou o total de inscrições dele no certame (015, T-008).
DEGRAUS_DE_PERFIL = {
    7: {"classificationMilestones": [], "declaredFacts": []},
    # **O degrau 12 é o quadro de vagas** (025, D-005). Lista vazia diz "este Edital não publicou
    # quadro", e é verdade sobre todos eles porque a capacidade não existia — nunca "zero vaga".
    #
    # É de Perfil, e não de raiz, porque o quadro é do Perfil: um Edital de sete polos publica sete
    # quadros, e uma coleção de raiz teria de carregar a referência ao Perfil em cada linha,
    # inventando uma segunda forma de dizer o que o aninhamento já diz.
    12: {"vacancyTable": []},
    # **O degrau 13 também é de Perfil**, e não só de marco: junto com a regra de corte entra a
    # declaração de qual Modalidade é a ampla concorrência (014, D-014). `None` diz "este Perfil não
    # declarou nenhuma", e é verdade sobre todo Edital publicado antes — a capacidade não existia.
    #
    # Os dois campos do degrau 13 entram **juntos** de propósito: a conferência do alvo derivado
    # precisa dos dois para saber quais recortes exigem linha de quadro, e separá-los seria duas
    # elevações e dois caminhos de leitura para uma decisão só.
    13: {"generalCompetitionModalityId": None},
    # **O degrau 14 é a declaração da reversão** (016, D-007). `None` diz "este Edital não declara
    # reversão", e é verdade sobre todos eles — a capacidade não existia. Conversão sem invenção,
    # como os degraus 12 e 13.
    #
    # E a ausência **não** é padrão de comportamento: o 57/2026 proíbe por escrito o remanejamento
    # entre cursos, e um sistema que revertesse por conta própria produziria ali o que ele veda.
    14: {"vacancyReversion": None},
}

DEGRAUS_DA_RAIZ = {
    7: {"maxInscricoesPorCandidato": None},
    # **O degrau 9 traz uma coleção inteira nova para a raiz**, e é o segundo a fazê-lo — o
    # primeiro foi `documentRequirements`, no 3→4, que **não** foi convertido. A diferença é o
    # significado da ausência: lá, escrever a coleção vazia teria afirmado que o Edital não exigia
    # documento nenhum, o que não era verdade — ele exigia, em prosa. Aqui a lista vazia diz "este
    # Edital não declarou anexo", e isso é verdade sobre todos eles, porque a capacidade não
    # existia (020, R-004).
    9: {"attachments": []},
}

# **O degrau 9 é o quarto nível**, e o primeiro dentro de `documentRequirements`. `attachmentId`
# nulo diz que o requisito **não fornece modelo** — não que o modelo se perdeu. É o que todo
# requisito publicado antes deste degrau afirma, e continua afirmando depois dele: o Edital que
# mandava o candidato a um anexo inexistente continua mandando, e é a `020` que passa a permitir
# que ele deixe de mandar (020, FR-020).
DEGRAUS_DE_DOCUMENTO = {
    9: {"attachmentId": None},
}

COLECAO_DE_DOCUMENTOS = "documentRequirements"
COLECAO_DE_DOCUMENTOS_ENDERECADA = f"/{COLECAO_DE_DOCUMENTOS}"

# **O degrau 8 é o terceiro nível**, e o primeiro dentro de uma coleção que já mora no Perfil. A
# janela recursal é declarada por marco, e não pelo Edital: marcos diferentes admitem recurso ou
# não, e por prazos diferentes.
#
# **`None` significa janela não declarada — e não janela de zero dias.** É o que a ausência diz em
# todo Edital publicado antes deste degrau, e é uma afirmação, não uma omissão a corrigir: sem
# declaração o sistema não inventa prazo, e a tempestividade volta a ser juízo de admissibilidade
# motivado, que é a degradação que a D-004 declarou (FR-028, FR-029).
# **O degrau 10 é o segundo dentro do marco**, e a razão é a mesma do 8: o que o marco declara é
# dele, e não do Edital — marcos diferentes ordenam por regras diferentes, e só um deles sorteia.
#
# `None` significa **método não declarado**, e não método padrão. É o que todo Edital publicado
# antes deste degrau afirma, e é verdade sobre todos eles: a capacidade não existia, e nenhum deles
# declarou fonte, ocorrência ou regra de normalização. Há, portanto, conversão sem invenção — e o
# sistema recusa congelar relação em marco sem método, em vez de escolher um por conta própria
# (021, FR-066, D-013).
# **O degrau 13 é a regra de corte** (014, D-011 a D-014). `None` significa **marco que não corta**,
# e é verdade sobre todo Edital publicado antes dele: a capacidade não existia, e nenhum deles
# declarou alvo, excedente, desfecho de empate, Etapa governada ou política de continuação. Há,
# portanto, conversão sem invenção, como nos dois degraus anteriores do mesmo objeto.
#
# `None` e não `{}`: os dois vizinhos já fixaram `None` para "não declarado", e um dicionário vazio
# seria uma segunda grafia da mesma ausência — o modo de falha que este módulo recusa em toda parte.
DEGRAUS_DE_MARCO = {
    8: {"appealWindow": None},
    10: {"drawMethod": None},
    13: {"cutRule": None},
}

# **O degrau 11 é o primeiro dentro do Evento do Cronograma.** Vazio significa **não declarado**, e
# não "acontece em lugar nenhum": é o que todo Edital publicado antes dele afirma, porque a
# capacidade não existia — e nenhum deles publicou o local em campo estruturado, ainda que muitos o
# dissessem em prosa. Conversão sem invenção, portanto (021, D-008, R-009).
#
# String e não `None`, pela convenção do próprio objeto: `description` e `type` do Evento são
# strings, e uma terceira grafia para texto ausente faria a versão canônica admitir mais de uma
# forma para o mesmo Edital.
DEGRAUS_DE_EVENTO = {
    11: {"location": ""},
}

COLECAO_DE_EVENTOS = "schedule"

COLECAO_DE_MARCOS = "classificationMilestones"

AUSENCIA_DE_PERFIL = {
    chave: valor for degrau in DEGRAUS_DE_PERFIL.values() for chave, valor in degrau.items()
}

COLECAO_DE_PERFIS = "/profiles"

# O que a Etapa na versão vigente carrega, somando todos os degraus. Serve à idempotência: entidade
# que já tem tudo atravessa sem cópia.
AUSENCIA = {chave: valor for degrau in DEGRAUS.values() for chave, valor in degrau.items()}

COLECAO_DE_ETAPAS = "/stages"

# **A conversão é uma cadeia, e não um mecanismo genérico de compatibilidade.** Um degrau por
# incremento, cada um sabendo só a sua origem e o seu destino, aplicados em sequência enquanto
# houver degrau. Conteúdo em versão anterior à 4 continua recusado por `_assert_versao_canonica`,
# como a 007 e a 009 decidiram — ali a conversão inventaria norma, e a recusa é a resposta certa.
# Sem esta guarda, um snapshot v3 sairia carimbado como 6 e a verificação de versão deixaria de
# verificar coisa alguma (D-002).
#
# Elevar v4 direto para v6 seria menos linhas e pior significado: saltaria uma forma que existiu de
# verdade, e a função passaria a decidir por ausência de chave em vez de por versão — o modo de
# falha que `colecoes.py` recusa, acertar hoje e falhar em silêncio quando nascer o degrau seguinte.
VERSAO_DE_ORIGEM = 4
VERSOES_ELEVAVEIS = frozenset(range(VERSAO_DE_ORIGEM, SCHEMA_VERSION + 1))


def elevar_etapa(etapa, *, de=VERSAO_DE_ORIGEM):
    """A Etapa na forma vigente. Idempotente: o que já está na forma nova atravessa igual.

    `de` é a versão em que a Etapa está; os degraus aplicados são os que vêm **depois** dela. Quando
    a origem não é conhecida — o `newValue` de um ato, que não carrega versão —, aplicam-se todos, e
    o resultado é o mesmo: a chave que já existe não é reescrita.
    """
    if not isinstance(etapa, dict):
        return etapa
    faltando = {
        chave: valor
        for versao, degrau in sorted(DEGRAUS.items())
        if versao > de
        for chave, valor in degrau.items()
        if chave not in etapa
    }
    return {**etapa, **faltando} if faltando else etapa


def elevar_perfil(perfil, *, de=VERSAO_DE_ORIGEM):
    """O Perfil na forma vigente. Idempotente, pela mesma regra de `elevar_etapa`.

    As coleções nascem **vazias**, e a lista vazia é a grafia da ausência: um Edital que não declara
    marco nenhum não classifica, e um que não declara fato nenhum não exige nada do candidato além
    do que a `009` já pede. Nenhuma das duas afirma norma que o conteúdo não tivesse.
    """
    if not isinstance(perfil, dict):
        return perfil
    faltando = {
        chave: valor
        for versao, degrau in sorted(DEGRAUS_DE_PERFIL.items())
        if versao > de
        for chave, valor in degrau.items()
        if chave not in perfil
    }
    return {**perfil, **faltando} if faltando else perfil


def elevar_marco(marco, *, de=VERSAO_DE_ORIGEM):
    """O marco classificatório na forma vigente. Simétrico a `elevar_etapa` e `elevar_perfil`.

    Terceiro nível da árvore, e por isso terceiro dicionário: cada um responde por um nível, e
    fundi-los obrigaria a função a descobrir onde cada chave mora — decidir por presença de chave em
    vez de por posição declarada, que é o modo de falha que este módulo recusa em toda parte.
    """
    if not isinstance(marco, dict):
        return marco
    faltando = {
        chave: valor
        for versao, degrau in sorted(DEGRAUS_DE_MARCO.items())
        if versao > de
        for chave, valor in degrau.items()
        if chave not in marco
    }
    return {**marco, **faltando} if faltando else marco


def elevar_evento(evento, *, de=VERSAO_DE_ORIGEM):
    """O Evento do Cronograma na forma vigente. Simétrico aos demais degraus por entidade."""
    if not isinstance(evento, dict):
        return evento
    faltando = {
        chave: valor
        for versao, degrau in sorted(DEGRAUS_DE_EVENTO.items())
        if versao > de
        for chave, valor in degrau.items()
        if chave not in evento
    }
    return {**evento, **faltando} if faltando else evento


def elevar_documento(documento, *, de=VERSAO_DE_ORIGEM):
    """O Documento Exigido na forma vigente. Idempotente, como os demais degraus por entidade."""
    if not isinstance(documento, dict):
        return documento
    faltando = {
        chave: valor
        for versao, degrau in sorted(DEGRAUS_DE_DOCUMENTO.items())
        if versao > de
        for chave, valor in degrau.items()
        if chave not in documento
    }
    return {**documento, **faltando} if faltando else documento


def elevar(conteudo):
    """O conteúdo publicado na versão canônica vigente, sem inventar nada.

    Devolve o mesmo objeto quando não há o que elevar, de modo que o caminho comum — conteúdo já
    na versão vigente — não pague cópia de dicionário a cada leitura.
    """
    if not isinstance(conteudo, dict):
        return conteudo
    declarada = conteudo.get("schemaVersion")
    if declarada not in VERSOES_ELEVAVEIS:
        # Versão que esta conversão não conhece atravessa **intacta**, para ser recusada onde a
        # recusa é dita: em `_assert_versao_canonica`. Carimbá-la aqui seria afirmar uma forma que
        # o conteúdo não tem — exatamente o que aquela verificação existe para impedir.
        return conteudo
    etapas = conteudo.get("stages")
    elevadas = (
        [elevar_etapa(item, de=declarada) for item in etapas]
        if isinstance(etapas, list)
        else etapas
    )
    perfis = conteudo.get("profiles")
    perfis_elevados = (
        [_elevar_perfil_e_marcos(item, declarada) for item in perfis]
        if isinstance(perfis, list)
        else perfis
    )
    documentos = conteudo.get(COLECAO_DE_DOCUMENTOS)
    documentos_elevados = (
        [elevar_documento(item, de=declarada) for item in documentos]
        if isinstance(documentos, list)
        else documentos
    )
    eventos = conteudo.get(COLECAO_DE_EVENTOS)
    eventos_elevados = (
        [elevar_evento(item, de=declarada) for item in eventos]
        if isinstance(eventos, list)
        else eventos
    )
    raiz = {
        chave: valor
        for versao, degrau in sorted(DEGRAUS_DA_RAIZ.items())
        if versao > declarada
        for chave, valor in degrau.items()
        if chave not in conteudo
    }
    if (
        declarada == SCHEMA_VERSION
        and elevadas == etapas
        and perfis_elevados == perfis
        and documentos_elevados == documentos
        and eventos_elevados == eventos
        and not raiz
    ):
        return conteudo
    elevado = {**conteudo, **raiz, "schemaVersion": SCHEMA_VERSION}
    if isinstance(etapas, list):
        elevado["stages"] = elevadas
    if isinstance(perfis, list):
        elevado["profiles"] = perfis_elevados
    if isinstance(documentos, list):
        elevado[COLECAO_DE_DOCUMENTOS] = documentos_elevados
    if isinstance(eventos, list):
        elevado[COLECAO_DE_EVENTOS] = eventos_elevados
    return elevado


def _elevar_perfil_e_marcos(perfil, declarada):
    """O Perfil elevado, e os marcos dentro dele — na mesma passagem.

    Os marcos são coleção **do Perfil**, e por isso não têm passagem própria em `elevar`: percorrer
    a lista de perfis duas vezes para elevar dois níveis daria o mesmo resultado pagando duas
    varreduras, e faria a ordem entre elas virar detalhe a lembrar.
    """
    elevado = elevar_perfil(perfil, de=declarada)
    if not isinstance(elevado, dict):
        return elevado
    marcos = elevado.get(COLECAO_DE_MARCOS)
    if not isinstance(marcos, list):
        return elevado
    marcos_elevados = [elevar_marco(item, de=declarada) for item in marcos]
    if marcos_elevados == marcos:
        return elevado
    return {**elevado, COLECAO_DE_MARCOS: marcos_elevados}


def _e_entidade_de_etapa(target_path):
    """Se o caminho endereça uma Etapa inteira — e não um campo dela, nem outra coleção.

    A classificação é **declarada**, e não descoberta por "é dict, logo é entidade": acertar hoje e
    falhar em silêncio no dia em que nascer coleção nova é o modo de falha que `colecoes.py` já
    recusa. São três formas, e só três:

        /stages/-              acréscimo, pelo token de fim de lista — é assim que o ADD endereça
        /stages/id=<uuid>      substituição da Etapa inteira
        /stages                a coleção, se algum dia for endereçável assim

    `/stages/id=<uuid>/<campo>` carrega escalar, e elevá-lo seria corrompê-lo.
    """
    if target_path == COLECAO_DE_ETAPAS:
        return "colecao"
    prefixo = f"{COLECAO_DE_ETAPAS}/"
    if not target_path.startswith(prefixo):
        return None
    resto = target_path[len(prefixo) :]
    if "/" in resto:
        return None
    return "entidade"


def diz_o_mesmo_que_a_ausencia(etapa):
    """Se os campos novos desta Etapa ainda exprimem o que a ausência deles exprimiria.

    **`null` e ausência são a mesma coisa**, e o contrato declara isso: `evaluationsPerRegistration`
    nulo é uma avaliação, `maximumScore` nulo é limite não declarado, `forma` nula é forma pontuada
    e rótulo nulo é rótulo não publicado. Comparar por igualdade com o
    valor da ausência erraria justamente aí — `None != 1` —, e a grafia literal seria recusada para
    uma Etapa que não declarou nada (T-002, T-017).

    A leitura é a mesma de `avaliacoes/domain/previsao.py`; o que muda é a pergunta: lá, "quanto
    vale"; aqui, "isto ainda é ausência".
    """
    if not isinstance(etapa, dict):
        return False
    previstas = etapa.get("evaluationsPerRegistration")
    if previstas not in (None, AUSENCIA["evaluationsPerRegistration"]):
        return False
    if etapa.get("maximumScore") is not None:
        return False
    # O degrau da revisão, pela mesma régua: `forma` ausente e `"PONTUADA"` dizem a mesma coisa, e
    # os rótulos ausentes dizem "não se aplica". Sem isto, uma Retificação elaborada antes do salto
    # entraria em conflito com o conteúdo elevado por uma diferença que não é diferença (T-017).
    if etapa.get("forma") not in (None, AUSENCIA["forma"]):
        return False
    return etapa.get("rotuloFavoravel") is None and etapa.get("rotuloDesfavoravel") is None


def endereca_etapa(target_path):
    """Se o caminho endereça a **entidade** Etapa — a mesma classificação que a elevação usa.

    Exposta porque a precondição de conteúdo precisa exatamente dela: a equivalência de grafias vale
    onde a elevação alcança, e em lugar nenhum além (T-017).
    """
    return _e_entidade_de_etapa(target_path or "") == "entidade"


def _e_entidade_de_marco(target_path):
    """Se o caminho endereça um marco classificatório inteiro — e não um campo dele.

    O endereço do marco passa **dentro** do Perfil, e por isso não é prefixo fixo:

        /profiles/id=<uuid>/classificationMilestones/-           acréscimo
        /profiles/id=<uuid>/classificationMilestones/id=<uuid>   substituição do marco inteiro
        /profiles/id=<uuid>/classificationMilestones             a coleção

    `.../classificationMilestones/id=<uuid>/appealWindow` carrega o objeto da janela, e elevá-lo
    seria corrompê-lo — quem o endereça já está escrevendo a forma nova.
    """
    caminho = target_path or ""
    marca = f"/{COLECAO_DE_MARCOS}"
    if not caminho.endswith(marca) and marca + "/" not in caminho:
        return None
    if caminho.endswith(marca):
        return "colecao"
    resto = caminho.split(marca + "/", 1)[1]
    return None if "/" in resto else "entidade"


def _e_entidade_de_documento(target_path):
    """Se o caminho endereça um Documento Exigido inteiro — e não um campo dele.

    Mesma régua declarada de `_e_entidade_de_etapa`, e as mesmas três formas:

        /documentRequirements/-            acréscimo
        /documentRequirements/id=<uuid>    substituição do requisito inteiro
        /documentRequirements              a coleção

    `/documentRequirements/id=<uuid>/attachmentId` carrega escalar, e elevá-lo seria corrompê-lo.
    """
    if target_path == COLECAO_DE_DOCUMENTOS_ENDERECADA:
        return "colecao"
    prefixo = f"{COLECAO_DE_DOCUMENTOS_ENDERECADA}/"
    if not target_path.startswith(prefixo):
        return None
    return None if "/" in target_path[len(prefixo) :] else "entidade"


def elevar_valor(target_path, valor):
    """O `newValue` de uma Alteração, elevado quando — e só quando — ele é entidade elevável.

    Três coleções alcançam a elevação: as Etapas, desde a 012; os marcos classificatórios, desde a
    018; e os Documentos Exigidos, desde a 020. Nas três a regra é a mesma — a **entidade inteira**
    é elevada, e o campo isolado não é, porque quem endereça um campo está escrevendo a forma que
    ele já tem.

    Os Anexos não entram aqui, e não é esquecimento: a coleção nasceu no degrau 9, então não existe
    Alteração anterior a ela cujo valor precisasse ser elevado. A entrada vem no dia em que o Anexo
    ganhar um campo — não antes.
    """
    forma = _e_entidade_de_etapa(target_path or "")
    if forma == "entidade":
        return elevar_etapa(valor)
    if forma == "colecao" and isinstance(valor, list):
        return [elevar_etapa(item) for item in valor]
    forma_do_marco = _e_entidade_de_marco(target_path)
    if forma_do_marco == "entidade":
        return elevar_marco(valor)
    if forma_do_marco == "colecao" and isinstance(valor, list):
        return [elevar_marco(item) for item in valor]
    forma_do_documento = _e_entidade_de_documento(target_path or "")
    if forma_do_documento == "entidade":
        return elevar_documento(valor)
    if forma_do_documento == "colecao" and isinstance(valor, list):
        return [elevar_documento(item) for item in valor]
    return valor


def elevar_alteracoes(changes):
    """As Alterações com o `newValue` na forma vigente. `REMOVE` não tem valor a elevar."""
    return [
        {**change, "newValue": elevar_valor(change.get("targetPath"), change.get("newValue"))}
        if "newValue" in change
        else change
        for change in changes
    ]
