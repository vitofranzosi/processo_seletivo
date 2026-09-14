"""O que pode ser corrigido depois de publicado, e o que não pode — campo a campo.

Toda vez que o conteúdo publicado de um Edital ganha um campo, alguém precisa ter decidido se ele
pode ser corrigido depois da publicação. Até a `026`, ninguém decidia: a auditoria de 13/09/2026
mediu de 13 a 23 campos de norma publicada por Edital sobre os quais não existia decisão nenhuma —
nem "sim", nem "não", nem "não se aplica".

**Decidir depois é tarde por construção.** O precedente está escrito no próprio código, sobre o
`callForm`: *"o primeiro Edital publicado com a forma declarada nasceria irretificável nela"*. Por
isso este módulo existe antes da interface, e por isso um teste-guardião compara o que o snapshot
publica com o que este dicionário classifica, falhando por **omissão** nos dois sentidos.

**A chave é `(coleção, caminho relativo)`**, e nunca o nome do campo. O nome colide entre coleções
— `name` existe em cinco, `order` em três —, e o último segmento colide dentro da mesma coleção:
`drawMethod/normalization/rule` e `drawMethod/substitutionRule/rule` dariam a mesma chave, e o
contrato não conseguiria representar nominalmente os dez campos do método do sorteio. O caminho
relativo é a grafia que `interface/retificacao.py` já pratica em `CAMPOS_REGRA`.

**A classificação vigente governa os atos futuros** (D-011), inclusive sobre Edital publicado antes
dela: uma Retificação é ato novo, praticado hoje, sob a norma de hoje. O que nenhuma reclassificação
alcança é o conteúdo já publicado, que a Constituição torna imutável. Congelar a classificação em
cada Publicação foi considerado e recusado — faria o contrato deixar de ser código, obrigaria o
guardião a guardar toda classificação histórica, e prenderia cada Edital à classificação do dia em
que foi publicado, que é o precedente do `callForm` outra vez.

**Nenhuma heurística atribui natureza** (D-008). Cada campo é decidido nominalmente, e a decisão
viaja com a razão. Uma classificação inferida por regra geral seria a mesma omissão de hoje, com
aparência de método.

**Limite conhecido**: a *forma* das seis coleções aninhadas continua não declarada em
`validation.py` (015, T-009). Enumerar um campo e declarar o tipo dele são coisas diferentes, e o
contrato precisa só da primeira (FR-300).
"""

from dataclasses import dataclass
from enum import StrEnum


class Natureza(StrEnum):
    """As quatro naturezas de mutabilidade. Partição total e exclusiva (D-001)."""

    #: Corrigível administrativamente depois da publicação. A tela de Retificação o oferece.
    RETIFICAVEL = "RETIFICAVEL"
    #: Mudá-lo exige outro mecanismo. Carrega razão **normativa** escrita (D-002).
    NAO_RETIFICAVEL = "NAO_RETIFICAVEL"
    #: Muda como consequência de outro campo. Não aparece na tela, e não precisa de razão própria.
    DERIVADO = "DERIVADO"
    #: Não pertence ao objeto de Retificação: identidade, ou estrutura que outra coleção endereça.
    ESTRUTURAL = "ESTRUTURAL"


class ContratoInvalido(Exception):
    """Entrada incoerente do contrato. Levanta na **carga do módulo**, e não num teste.

    Quem escreve o contrato descobre no `import`, e não depois de rodar a suíte inteira.
    """


@dataclass(frozen=True)
class Mutabilidade:
    """A decisão sobre um campo publicado.

    `razao` é obrigatória para `NAO_RETIFICAVEL` e proibida para as outras três: derivado e
    estrutural se explicam pela própria natureza, e retificável não precisa justificar-se.

    **A razão precisa ser normativa, e não técnica** (D-002). Uma razão que descreva limitação de
    implementação — "caixa de texto publicaria valor que o cálculo não interpreta" — deixa de valer
    quando a limitação some, e ninguém percebe. Uma que descreva norma — "trocar o tipo do fato
    reinterpretaria valor já congelado" — continua valendo. Isso nenhum código confere: é leitura
    humana, em revisão de código.

    `fechou_caminho` é a marca da FR-315: esta entrada resulta de uma reclassificação que **fechou**
    um caminho de correção que existia. Só faz sentido com `NAO_RETIFICAVEL`.

    **O que a marca é**: declaração de quem reclassificou, como a razão já é. O contrato guarda só o
    vigente (D-011), então nada aqui *detecta* a transição — quem a vê é a revisão de código, no
    diff, e a marca é o que faz o diff dizer o que aconteceu em vez de só mostrar uma palavra
    trocada.

    **O que a marca não é**: garantia de que toda transição R→N seja marcada. Isso exigiria guardar
    o passado, que é a alternativa que a D-011 recusou. A verificação cobre uma direção só — marca
    incoerente é recusada; marca ausente, não.
    """

    natureza: Natureza
    razao: str = ""
    fechou_caminho: bool = False

    def __post_init__(self):
        if self.natureza is Natureza.NAO_RETIFICAVEL and not self.razao.strip():
            raise ContratoInvalido(
                "Natureza 'não retificável' exige razão escrita, e a razão precisa ser normativa: "
                "sem ela a exclusão é indistinguível de esquecimento."
            )
        if self.natureza is not Natureza.NAO_RETIFICAVEL and self.razao:
            raise ContratoInvalido(
                f"Natureza {self.natureza} não carrega razão: derivado e estrutural se explicam "
                "pela própria natureza, e retificável não precisa justificar-se."
            )
        if self.fechou_caminho and self.natureza is not Natureza.NAO_RETIFICAVEL:
            raise ContratoInvalido(
                "A marca de caminho fechado só cabe em 'não retificável': ela registra que uma "
                "reclassificação retirou capacidade de quem já publicou (FR-315)."
            )


def retificavel() -> Mutabilidade:
    return Mutabilidade(Natureza.RETIFICAVEL)


def nao_retificavel(razao: str, *, fechou_caminho: bool = False) -> Mutabilidade:
    return Mutabilidade(Natureza.NAO_RETIFICAVEL, razao, fechou_caminho)


def derivado() -> Mutabilidade:
    return Mutabilidade(Natureza.DERIVADO)


def estrutural() -> Mutabilidade:
    return Mutabilidade(Natureza.ESTRUTURAL)


#: O nome da coleção que designa a raiz do Edital — os campos soltos do conteúdo canônico.
#: Palavra, e não `""`: ela aparece em mensagem de falha, e "raiz" diz o que `''` não diz.
RAIZ = "raiz"

#: Os objetos **opacos**: o conteúdo de dentro deles não tem forma declarada, e o conjunto de
#: folhas que carregam depende do Edital. A travessia **não desce** neles, e o contrato classifica
#: cada um inteiro.
#:
#: **O critério é quem lê, e não ser `JSONField`.** `rounding` do marco e `parameters` do critério
#: de desempate também são `JSONField` livre — e não são opacos: `classificacao/domain/combinacao`
#: valida `scale` e `mode`, e `classificacao/domain/desempate` lê `stageId`/`factId`. A forma deles
#: é conhecida e o cálculo depende dela; tratá-los como opacos seria classificar **por onde o dado
#: está guardado**, que é razão técnica — exatamente o que a D-002 proíbe.
#:
#: Declarar um objeto como opaco é decisão escrita. Um `grep` que encontre leitor para um opaco
#: declarado é o sinal de que a declaração envelheceu.
OPACOS = frozenset(
    {
        ("profiles", "classificationInformation"),
        ("profiles", "callInformation"),
        ("competitionModalities", "normativeRule/calculation"),
        ("competitionModalities", "normativeRule/rounding"),
        ("competitionModalities", "normativeRule/distribution"),
        ("competitionModalities", "normativeRule/callRules"),
    }
)


#: A classificação de cada campo do conteúdo canônico publicado, transcrita da matriz aprovada em
#: 13/09/2026 (`specs/026-contrato-de-mutabilidade-normativa/matriz.md`).
#:
#: A ordem segue a do conteúdo publicado, e não a alfabética: quem confere lê na mesma sequência em
#: que `publish_edital.edital_snapshot` emite.
CONTRATO: dict[tuple[str, str], Mutabilidade] = {
    # ---- Raiz do Edital ---------------------------------------------------------------------
    (RAIZ, "schemaVersion"): estrutural(),
    (RAIZ, "editalId"): estrutural(),
    (RAIZ, "processoId"): estrutural(),
    (RAIZ, "processoCode"): derivado(),
    (RAIZ, "processoTitle"): derivado(),
    (RAIZ, "number"): nao_retificavel(
        "O número do Edital é como o certame é citado em todo lugar — outros atos, ofícios, o "
        "Diário. Trocá-lo por Retificação faria dois documentos nomearem coisas diferentes com o "
        "mesmo nome."
    ),
    (RAIZ, "year"): nao_retificavel(
        "Mesma razão do número: ano e número identificam o certame perante terceiros, e a "
        "identificação não se corrige sem desfazer as citações que já existem."
    ),
    (RAIZ, "title"): retificavel(),
    (RAIZ, "description"): retificavel(),
    (RAIZ, "maxInscricoesPorCandidato"): nao_retificavel(
        "Governa quantas inscrições a pessoa pôde fazer. Reduzi-lo depois de aberto o prazo "
        "invalidaria inscrição já aceita; aumentá-lo daria a quem se inscreveu depois uma chance "
        "que os primeiros não tiveram."
    ),
    # ---- profiles ---------------------------------------------------------------------------
    ("profiles", "id"): estrutural(),
    ("profiles", "code"): estrutural(),
    ("profiles", "name"): retificavel(),
    ("profiles", "description"): retificavel(),
    ("profiles", "requirements"): retificavel(),
    ("profiles", "immediateVacancies"): retificavel(),
    ("profiles", "reserveType"): nao_retificavel(
        "A espécie do cadastro reserva define **o que o Edital ofereceu** — nenhum, limitado ou "
        "ilimitado. Quem se inscreveu decidiu concorrer sabendo se havia reserva e de que tipo; "
        "trocá-la depois não corrige um erro de redação, oferece outra coisa. O limite dentro da "
        "espécie é parâmetro, e esse se corrige."
    ),
    ("profiles", "reserveLimit"): retificavel(),
    ("profiles", "locality"): retificavel(),
    ("profiles", "duties"): retificavel(),
    ("profiles", "workload"): retificavel(),
    ("profiles", "compensation"): retificavel(),
    ("profiles", "classificationInformation"): nao_retificavel(
        "O domínio não reconhece forma nem semântica para este objeto; portanto, não consegue "
        "determinar o que seria uma correção administrativa válida. Atribuir-lhe significado "
        "normativo exige decisão e especificação próprias, não uma Retificação. "
        "A ausência de consumidores é evidência do problema, não a justificativa: nenhum canal o "
        "exibe, mas não é por faltar tela que ele é irretificável — é por não haver o que se "
        "corrija. Ver doc/achado-objeto-normativo-sem-forma.md."
    ),
    ("profiles", "callInformation"): nao_retificavel(
        "Mesma razão: o domínio não reconhece forma nem semântica para este objeto, e por isso não "
        "consegue determinar o que seria uma correção válida. O contraponto — `callForm` ao lado é "
        "retificável e é exibido — reforça a decisão: ele tem forma declarada, valor de lista "
        "fechada e destino observável, e é exatamente isso que falta aqui."
    ),
    ("profiles", "generalCompetitionModalityId"): retificavel(),
    ("profiles", "vacancyReversion/kind"): retificavel(),
    ("profiles", "callForm"): retificavel(),
    # ---- competitionModalities --------------------------------------------------------------
    ("competitionModalities", "id"): estrutural(),
    ("competitionModalities", "code"): estrutural(),
    ("competitionModalities", "name"): retificavel(),
    ("competitionModalities", "description"): retificavel(),
    ("competitionModalities", "normativeRule/id"): estrutural(),
    ("competitionModalities", "normativeRule/foundation"): retificavel(),
    ("competitionModalities", "normativeRule/version"): retificavel(),
    ("competitionModalities", "normativeRule/percentage"): retificavel(),
    ("competitionModalities", "normativeRule/effectiveFrom"): retificavel(),
    ("competitionModalities", "normativeRule/calculation"): nao_retificavel(
        "A Constituição determina que os parâmetros da cota mudam por **versionamento**, e não por "
        "correção: 'Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar "
        "modalidade, fundamento, percentual, cálculo, arredondamento, distribuição e vigência'. O "
        "cálculo da reserva é um deles. O caminho de correção existe e é outro — `version` e "
        "`effectiveFrom`, ambos retificáveis. Corrigir o parâmetro no lugar de versionar a regra "
        "apagaria sob qual norma cada Edital anterior concorreu."
    ),
    ("competitionModalities", "normativeRule/rounding"): nao_retificavel(
        "Mesma razão constitucional: o arredondamento é um dos parâmetros da cota que mudam por "
        "versionamento. Ele decide quantas vagas a reserva recebe, e reescrevê-lo sem versionar a "
        "regra apagaria sob qual norma cada Edital anterior concorreu."
    ),
    ("competitionModalities", "normativeRule/distribution"): nao_retificavel(
        "Mesma razão constitucional: a distribuição é um dos parâmetros que mudam por "
        "versionamento, e não por correção do texto publicado."
    ),
    ("competitionModalities", "normativeRule/callRules"): nao_retificavel(
        "Mesma razão constitucional: as regras de convocação da reserva são parâmetro da cota, e "
        "mudam por versionamento da regra normativa."
    ),
    # ---- vacancyTable -----------------------------------------------------------------------
    ("vacancyTable", "id"): estrutural(),
    ("vacancyTable", "modalityId"): retificavel(),
    ("vacancyTable", "immediateVacancies"): retificavel(),
    # ---- declaredFacts ----------------------------------------------------------------------
    ("declaredFacts", "id"): estrutural(),
    ("declaredFacts", "code"): estrutural(),
    ("declaredFacts", "label"): retificavel(),
    ("declaredFacts", "type"): nao_retificavel(
        "Trocar o tipo reinterpretaria valor já congelado sob o tipo anterior: mudar o tipo é "
        "remover um fato e acrescentar outro, e o que foi congelado sob o primeiro permanece "
        "legível sob a norma que o governou (015, FR-058)."
    ),
    # ---- classificationMilestones -----------------------------------------------------------
    ("classificationMilestones", "id"): estrutural(),
    ("classificationMilestones", "code"): estrutural(),
    ("classificationMilestones", "name"): retificavel(),
    ("classificationMilestones", "stages"): nao_retificavel(
        "Quais Etapas o marco mede é **o que o marco é**, e não um parâmetro dele. Um marco que "
        "passa a medir outras Etapas não é o mesmo marco corrigido: é outro marco, sob o mesmo "
        "nome e o mesmo código, com as pontuações já registradas valendo para uma pergunta que "
        "ninguém fez. O caminho para mudar o que se mede é declarar marco novo."
    ),
    ("classificationMilestones", "operation"): nao_retificavel(
        "Como as pontuações se combinam reinterpreta **toda pontuação já registrada** sob o marco: "
        "a mesma nota passa a significar outra posição sem que ninguém a tenha reavaliado. Trocar "
        "soma por média não corrige o que foi publicado, recalcula o certame."
    ),
    ("classificationMilestones", "normalization"): nao_retificavel(
        "Mesma razão da combinação, um passo antes: a normalização é o que torna as notas "
        "comparáveis entre si, e mudá-la depois de publicada reinterpreta cada nota já lançada."
    ),
    ("classificationMilestones", "rounding/scale"): retificavel(),
    ("classificationMilestones", "rounding/mode"): retificavel(),
    ("classificationMilestones", "appealWindow/admits"): retificavel(),
    ("classificationMilestones", "appealWindow/durationDays"): retificavel(),
    ("classificationMilestones", "appealWindow/unit"): retificavel(),
    ("classificationMilestones", "drawMethod/algorithm"): retificavel(),
    ("classificationMilestones", "drawMethod/source"): retificavel(),
    ("classificationMilestones", "drawMethod/occurrence"): retificavel(),
    ("classificationMilestones", "drawMethod/occurrenceAt"): retificavel(),
    ("classificationMilestones", "drawMethod/derivation"): retificavel(),
    ("classificationMilestones", "drawMethod/normalization/rule"): retificavel(),
    ("classificationMilestones", "drawMethod/normalization/text"): retificavel(),
    ("classificationMilestones", "drawMethod/substitutionRule/rule"): retificavel(),
    ("classificationMilestones", "drawMethod/substitutionRule/text"): retificavel(),
    ("classificationMilestones", "drawMethod/qualifyingStageId"): retificavel(),
    ("classificationMilestones", "cutRule/targetKind"): nao_retificavel(
        "A espécie do alvo diz se o corte tem número fixo ou derivado do quadro — são **duas "
        "regras diferentes**, e não dois valores da mesma. A quantidade dentro da espécie fixa é "
        "parâmetro, e essa se corrige."
    ),
    ("classificationMilestones", "cutRule/targetCount"): retificavel(),
    ("classificationMilestones", "cutRule/surplusCount"): retificavel(),
    ("classificationMilestones", "cutRule/tieOutcome"): retificavel(),
    ("classificationMilestones", "cutRule/governedStage"): nao_retificavel(
        "A razão está escrita em `classificacao/domain/faixa.etapa_governada`: trocá-la 'moveria "
        "em silêncio quem continua no certame'. É o campo que decide quem progride, e corrigi-lo "
        "depois do corte aplicado mudaria quem passou sem reavaliar ninguém."
    ),
    ("classificationMilestones", "cutRule/continuation"): nao_retificavel(
        "Mesma razão da Etapa governada, do outro lado: admitir ou não continuação além da faixa "
        "decide quem segue no certame, e mudá-la depois do corte reescreveria o resultado de um "
        "ato já praticado."
    ),
    # ---- tiebreakers ------------------------------------------------------------------------
    ("tiebreakers", "id"): estrutural(),
    ("tiebreakers", "order"): retificavel(),
    ("tiebreakers", "type"): nao_retificavel(
        "O que o critério compara é **o que ele é**: trocá-lo não corrige o desempate, substitui-o "
        "por outro, e os empates já resolvidos sob o anterior ficariam resolvidos por um critério "
        "que o Edital não tem mais."
    ),
    ("tiebreakers", "parameters/stageId"): nao_retificavel(
        "Mesma razão do tipo: a Etapa que o critério compara é parte do que ele é, e trocá-la "
        "substitui o critério em vez de corrigi-lo."
    ),
    ("tiebreakers", "parameters/factId"): nao_retificavel(
        "Mesma razão: o fato que o critério compara é parte do que ele é."
    ),
    ("tiebreakers", "whenMissing"): nao_retificavel(
        "O que fazer quando o valor não existe é regra de desempate como qualquer outra, e "
        "`editais/domain/perfis` registra por que ela é declarada e nunca inferida: 'o silêncio "
        "não vira zero nem último lugar'. Mudá-la depois de empates resolvidos os resolveria de "
        "outro jeito."
    ),
    # ---- schedule ---------------------------------------------------------------------------
    ("schedule", "id"): estrutural(),
    ("schedule", "type"): nao_retificavel(
        "A espécie do Evento é o que liga o Cronograma às regras que dependem dele — o período de "
        "inscrições, a Etapa vinculada. Trocá-la depois de publicado muda a que o Evento serve, e "
        "não o que ele diz."
    ),
    ("schedule", "description"): retificavel(),
    ("schedule", "startAt"): retificavel(),
    ("schedule", "endAt"): retificavel(),
    ("schedule", "order"): estrutural(),
    ("schedule", "status"): derivado(),
    # Canário 1 da `026` (FR-305). **Informar local onde não havia é alteração de valor, e não
    # acréscimo de campo**: `location` é sempre presente no conteúdo publicado, com `""` para "não
    # declarado" — a convenção que `publish_edital` documenta e que `duties` e `workload` já
    # seguem. Não há caminho inexistente a endereçar, e por isso a gramática da `004` não precisou
    # de regra nova para o segundo cenário de aceitação da história.
    ("schedule", "location"): retificavel(),
    ("schedule", "isRegistrationPeriod"): nao_retificavel(
        "Qual Evento é o período de inscrições determina quando as inscrições estiveram abertas. "
        "Trocá-lo depois de publicado redefiniria retroativamente a janela em que as pessoas "
        "podiam se inscrever — e há inscrição aceita sob a janela anterior."
    ),
    # ---- stages -----------------------------------------------------------------------------
    ("stages", "id"): estrutural(),
    ("stages", "order"): estrutural(),
    ("stages", "scheduleEventId"): estrutural(),
    ("stages", "name"): retificavel(),
    ("stages", "weight"): retificavel(),
    ("stages", "minimumScore"): retificavel(),
    ("stages", "maximumScore"): retificavel(),
    ("stages", "evaluationsPerRegistration"): retificavel(),
    ("stages", "eliminatory"): retificavel(),
    ("stages", "classificatory"): retificavel(),
    ("stages", "forma"): retificavel(),
    ("stages", "rotuloFavoravel"): retificavel(),
    ("stages", "rotuloDesfavoravel"): retificavel(),
    # ---- sections ---------------------------------------------------------------------------
    ("sections", "id"): estrutural(),
    ("sections", "key"): estrutural(),
    ("sections", "title"): nao_retificavel(
        "As seções do Edital são um **catálogo institucional**, e não escolha deste Edital: "
        "título, ordem e espécie são os mesmos em todo Edital do Cefor, e é isso que torna um "
        "Edital legível por quem já leu outro. Corrigi-los aqui mudaria este Edital em relação aos "
        "demais. O que este Edital escreve é o conteúdo, e esse se corrige."
    ),
    ("sections", "order"): nao_retificavel(
        "Mesma razão: é a ordem do catálogo institucional, e não deste Edital."
    ),
    ("sections", "type"): nao_retificavel(
        "Mesma razão: é a espécie declarada pelo catálogo institucional."
    ),
    ("sections", "content"): retificavel(),
    ("sections", "source"): estrutural(),
    # ---- attachments ------------------------------------------------------------------------
    ("attachments", "id"): estrutural(),
    ("attachments", "label"): retificavel(),
    ("attachments", "order"): retificavel(),
    ("attachments", "artifactId"): retificavel(),
    ("attachments", "artifactHash"): derivado(),
    # ---- documentRequirements ---------------------------------------------------------------
    ("documentRequirements", "id"): estrutural(),
    ("documentRequirements", "key"): nao_retificavel(
        "É a identificação estável com que a inscrição já submetida nomeia o arquivo enviado, e "
        "trocá-la depois de publicado desligaria o documento do que os candidatos mandaram."
    ),
    ("documentRequirements", "name"): retificavel(),
    ("documentRequirements", "instructions"): retificavel(),
    ("documentRequirements", "required"): retificavel(),
    ("documentRequirements", "order"): retificavel(),
    ("documentRequirements", "profileId"): retificavel(),
    ("documentRequirements", "modalityId"): retificavel(),
    ("documentRequirements", "attachmentId"): retificavel(),
}


def natureza_de(colecao: str, caminho: str) -> Mutabilidade:
    """A decisão sobre um campo publicado. Levanta `KeyError` para par não declarado.

    **Não devolve padrão**, e a ausência é deliberada: um padrão seria a decisão implícita que a
    D-008 proíbe — o campo novo herdaria em silêncio a natureza mais conveniente, que é exatamente
    o estado que esta feature veio fechar, com outro nome.
    """
    return CONTRATO[(colecao, caminho)]


#: Os objetos normativos que podem **estar ausentes** do conteúdo publicado, e se a declaração pode
#: passar a existir por Retificação (FR-313, D-007).
#:
#: `None` não é campo sem natureza: é declaração que não foi feita. A natureza de cada campo de
#: dentro continua sendo a que `CONTRATO` diz quando o objeto existe; o que se decide aqui é se o
#: objeto pode **nascer** por Retificação — que é acréscimo de declaração, e não alteração de valor.
#:
#: Transcrito da matriz aprovada em 13/09/2026.
PODE_PASSAR_A_EXISTIR: dict[tuple[str, str], tuple[bool, str]] = {
    ("classificationMilestones", "cutRule"): (
        True,
        "Um marco que não cortava passa a cortar por Retificação, com a regra inteira num ato só — "
        "declarar pela metade é o que a validação já recusa.",
    ),
    ("classificationMilestones", "appealWindow"): (
        True,
        "Declarar janela onde não havia **concede** prazo, e conceder é menos grave do que "
        "retirar: quem já tinha o direito de recorrer continua tendo.",
    ),
    ("classificationMilestones", "drawMethod"): (
        False,
        "Um marco que não declarou método não sorteia. Fazê-lo sortear depois de publicado muda a "
        "**espécie** da ordenação, e não um parâmetro dela — quem se inscreveu sabendo que a ordem "
        "sairia da pontuação passaria a concorrer por sorteio.",
    ),
    ("profiles", "vacancyReversion"): (
        True,
        "A `016` já trata a reversão como declaração do Edital, e dizer como as vagas "
        "reservadas não preenchidas revertem não retira nada de quem concorre.",
    ),
    ("competitionModalities", "normativeRule"): (
        False,
        "Modalidade sem regra normativa é Modalidade sem fundamento; acrescentá-lo depois é criar "
        "reserva que o Edital publicado não tinha, e não corrigir a que ele tinha.",
    ),
}
