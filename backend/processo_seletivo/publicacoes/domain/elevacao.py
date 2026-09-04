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
    if declarada == SCHEMA_VERSION and elevadas == etapas:
        return conteudo
    elevado = {**conteudo, "schemaVersion": SCHEMA_VERSION}
    if isinstance(etapas, list):
        elevado["stages"] = elevadas
    return elevado


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


def elevar_valor(target_path, valor):
    """O `newValue` de uma Alteração, elevado quando — e só quando — ele é uma Etapa."""
    forma = _e_entidade_de_etapa(target_path or "")
    if forma == "entidade":
        return elevar_etapa(valor)
    if forma == "colecao" and isinstance(valor, list):
        return [elevar_etapa(item) for item in valor]
    return valor


def elevar_alteracoes(changes):
    """As Alterações com o `newValue` na forma vigente. `REMOVE` não tem valor a elevar."""
    return [
        {**change, "newValue": elevar_valor(change.get("targetPath"), change.get("newValue"))}
        if "newValue" in change
        else change
        for change in changes
    ]
