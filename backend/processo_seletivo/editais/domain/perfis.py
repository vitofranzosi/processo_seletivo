from decimal import Decimal, InvalidOperation


class RecusaDeCampo(ValueError):
    """Uma recusa do domínio que sabe **a que campo pertence**.

    FR-033 pede que a recusa apareça em resumo ancorado e junto do campo. A interface não tinha
    como fazer isso porque estas exceções carregavam mensagem e nada mais — e ancorar exige saber
    qual campo, de qual linha.

    `campo` é o nome canônico (`name`, `startAt`, `reserveLimit`); `identidade` é o `id` da entidade
    quando ela tem um, para que a interface encontre a linha certa. Os dois são **opcionais**: as
    regras que valem para a coleção inteira — "o Edital deve possuir ao menos um Perfil" — não
    pertencem a campo nenhum, e forçá-las a apontar um seria pior do que não apontar.
    """

    def __init__(self, mensagem, *, campo="", identidade=""):
        super().__init__(mensagem)
        self.campo = campo
        self.identidade = str(identidade or "")


class ProfileValidationError(RecusaDeCampo):
    pass


def validate_normative_rule(rule: dict) -> None:
    """A faixa do percentual vive aqui, e não no serializer (FR-030).

    A interface administrativa invoca o command diretamente e não atravessa o serializer da API:
    validar apenas ali deixaria sem verificação justamente o canal onde o dado é digitado.

    **Zero não é reserva de nenhuma vaga: é ausência de reserva.** Modalidade sem percentual
    exprime-se pela ausência da regra ou do campo, e um zero afirmaria uma reserva que reserva
    nada. Não se valida soma entre modalidades — cotas não somam cem por cento (PPI 20% e PcD 5%
    convivem), e a regra de composição pertence à jornada do candidato, que está fora de escopo.
    """
    bruto = rule.get("percentage")
    if bruto is None:
        return
    try:
        percentual = Decimal(str(bruto))
    except InvalidOperation as exc:
        raise ProfileValidationError(
            f"'{bruto}' não é um percentual válido para a Regra Normativa."
        ) from exc
    if not 0 < percentual <= 100:
        raise ProfileValidationError(
            "O percentual da Regra Normativa, quando informado, deve ser maior que zero e "
            "menor ou igual a cem."
        )


def validate_profile(profile: dict) -> None:
    immediate = profile.get("immediateVacancies", 0)
    reserve_type = profile.get("reserveType")
    reserve_limit = profile.get("reserveLimit")
    if immediate < 0:
        raise ProfileValidationError(
            "Vagas imediatas não podem ser negativas.",
            campo="immediateVacancies",
            identidade=profile.get("id", ""),
        )
    if reserve_type == "NONE" and reserve_limit is not None:
        raise ProfileValidationError(
            "Cadastro Reserva inexistente não admite limite.",
            campo="reserveLimit",
            identidade=profile.get("id", ""),
        )
    if reserve_type == "LIMITED" and (reserve_limit is None or reserve_limit < 0):
        raise ProfileValidationError(
            "Cadastro Reserva limitado exige limite não negativo.",
            campo="reserveLimit",
            identidade=profile.get("id", ""),
        )
    if reserve_type == "UNLIMITED" and reserve_limit is not None:
        raise ProfileValidationError(
            "Cadastro Reserva ilimitado não admite limite.",
            campo="reserveLimit",
            identidade=profile.get("id", ""),
        )
    if reserve_type not in {"NONE", "LIMITED", "UNLIMITED"}:
        raise ProfileValidationError("Tipo de Cadastro Reserva inválido.")
    modalities = profile.get("competitionModalities", [])
    modality_codes = [item["code"] for item in modalities]
    if len(modality_codes) != len(set(modality_codes)):
        raise ProfileValidationError("Modalidades de Concorrência não podem se repetir no Perfil.")
    for modality in modalities:
        rule = modality.get("normativeRule")
        if rule:
            validate_normative_rule(rule)
    validate_declared_facts(profile.get("declaredFacts", []))
    validate_classification_milestones(profile.get("classificationMilestones", []))


def validate_declared_facts(facts: list[dict]) -> None:
    """Código único no Perfil, e tipo entre os dois que existem (D-2).

    O tipo é verificado aqui **além** do serializer porque a interface administrativa invoca o
    command diretamente e não atravessa aquele caminho — é a mesma razão pela qual a faixa do
    percentual é verificada no domínio.
    """
    codes = [fato.get("code") for fato in facts]
    if len(codes) != len(set(codes)):
        raise ProfileValidationError("Fatos declarados não podem repetir código no Perfil.")
    for fato in facts:
        if fato.get("type") not in {"DATA", "INTEIRO"}:
            raise ProfileValidationError(
                "O tipo de um fato declarado deve ser data ou número inteiro."
            )


def validate_classification_milestones(milestones: list[dict]) -> None:
    """O que a elaboração do marco recusa antes de a publicação sequer ser tentada (015, D-001).

    Aqui não se verifica se a Etapa enumerada existe ou é classificatória — isso depende do conteúdo
    inteiro, e mora em `validate_for_publication`. O que se verifica é o que se decide olhando só o
    Perfil: identidade legível, ordem sem empate e comportamento declarado para valor ausente.
    """
    codes = [marco.get("code") for marco in milestones]
    if len(codes) != len(set(codes)):
        raise ProfileValidationError("Marcos classificatórios não podem repetir código no Perfil.")
    for marco in milestones:
        if not marco.get("stages"):
            raise ProfileValidationError(
                "Um marco classificatório deve enumerar ao menos uma Etapa: sem Etapa não há "
                "pontuação a combinar, e a ordem não sai."
            )
        criterios = marco.get("tiebreakers", [])
        ordens = [criterio.get("order") for criterio in criterios]
        if len(ordens) != len(set(ordens)):
            raise ProfileValidationError(
                "Critérios de desempate não podem compartilhar a mesma ordem: "
                "a ordem é a norma, e duas na mesma posição exigiriam desempatar o desempate."
            )
        for criterio in criterios:
            # A ausência é declarada, nunca inferida: o silêncio não vira zero nem último lugar
            # — ele impede a publicação da regra (FR-018).
            parametros = criterio.get("parameters") or {}
            if not (parametros.get("stageId") or parametros.get("factId")):
                raise ProfileValidationError(
                    "Todo critério de desempate deve declarar o que compara: uma Etapa ou um fato "
                    "declarado."
                )
            if not criterio.get("whenMissing"):
                raise ProfileValidationError(
                    "Todo critério de desempate deve declarar o que fazer quando o valor "
                    "que ele consome não existe."
                )
        _validar_janela_recursal(marco.get("appealWindow"))
        _validar_metodo_de_sorteio(marco.get("drawMethod"), etapas=marco.get("stages") or [])


CAMPOS_DO_METODO = (
    ("algorithm", "o algoritmo e a sua versão"),
    ("source", "a fonte pública externa da semente"),
    ("occurrence", "a ocorrência que fixará a semente"),
    ("derivation", "como a ocorrência decorre da data programada"),
    ("normalization", "como o material bruto vira semente"),
    ("substitutionRule", "o que vale se a ocorrência faltar, atrasar, bifurcar ou vier inválida"),
)


def _validar_metodo_de_sorteio(metodo, *, etapas=()) -> None:
    """O método declarado vale inteiro, ou não é declarado (021, FR-013, FR-015).

    **A ausência é válida e significa alguma coisa**: marco que não sorteia não declara método, e a
    maioria não sorteia. O que se recusa é a declaração pela metade — um método sem regra de
    substituição prometeria conduta mecânica numa hipótese que ninguém escreveu, e no dia da
    indisponibilidade a escolha voltaria para a mesa, que é exatamente o que a FR-015 proíbe.

    **A regra de normalização e a de substituição são pares**: o identificador, que a máquina
    aplica e o terceiro reimplementa, e a frase, que é o que a pessoa lê. Prosa sozinha não atende
    à FR-015 nem à FR-027 — ninguém executa uma frase, e duas pessoas lendo "os dígitos sorteados"
    produzem seis grafias da mesma semente.
    """
    if metodo is None:
        return
    if not isinstance(metodo, dict):
        raise ProfileValidationError(
            "O método do sorteio deve ser declarado como um objeto, ou não ser declarado."
        )
    for campo, o_que_e in CAMPOS_DO_METODO:
        if not metodo.get(campo):
            raise ProfileValidationError(
                f"O método do sorteio não declara {o_que_e} (`{campo}`). Um método declarado pela "
                "metade devolve ao dia do sorteio a escolha que ele existe para eliminar."
            )
    for campo in ("normalization", "substitutionRule"):
        regra = metodo.get(campo)
        if not isinstance(regra, dict) or not regra.get("rule") or not regra.get("text"):
            raise ProfileValidationError(
                f"`{campo}` deve declarar `rule` — o identificador que a máquina aplica e o "
                "terceiro reimplementa — e `text`, a frase publicada que a pessoa lê."
            )
    _validar_regra_publicada(metodo["normalization"]["rule"])
    _validar_etapa_de_habilitacao(metodo.get("qualifyingStageId"), etapas)


def _validar_etapa_de_habilitacao(etapa_id, etapas) -> None:
    """A Etapa que habilita a participar do sorteio, quando o Edital declara uma (021, R-012).

    **Sétimo campo, e opcional** — `null` significa "nenhuma", e é o caso dos quatro Editais lidos,
    em que a análise documental vem **depois** do sorteio. `null` e conjunto vazio são coisas
    diferentes: o primeiro diz que não há Etapa de habilitação, e o segundo diria que há e ninguém
    passou. Confundi-los esvaziaria um certame inteiro.

    Declarada, ela precisa ser uma das Etapas que o próprio marco enumera: uma Etapa de fora seria
    critério de entrada que a norma do marco não menciona, e ninguém saberia lê-lo no Edital.
    """
    if not etapa_id:
        return
    if str(etapa_id) not in {str(item) for item in etapas}:
        raise ProfileValidationError(
            "A Etapa que habilita ao sorteio precisa ser uma das Etapas enumeradas pelo marco: "
            "uma Etapa de fora seria critério de entrada que a norma do marco não declara."
        )


def _validar_regra_publicada(regra) -> None:
    """Regra de normalização fora do vocabulário publicado é recusada na elaboração.

    Recusar aqui é o que impede o Edital de publicar uma regra que ninguém executa: o defeito
    apareceria no dia do sorteio, ao vivo, e não no dia em que alguém a escreveu.
    """
    from processo_seletivo.sorteios.domain.normalizacao import REGRAS

    if regra not in REGRAS:
        raise ProfileValidationError(
            f"Regra de normalização não publicada por este sistema: {regra!r}. "
            f"As publicadas são: {', '.join(sorted(REGRAS))}."
        )


def _validar_janela_recursal(janela) -> None:
    """A janela declarada precisa ser computável — ou não ser declarada (FR-020, FR-021).

    **A ausência é válida e significa alguma coisa**: janela não declarada, e a tempestividade
    volta a ser juízo de admissibilidade motivado. O que se recusa é a declaração pela metade, que
    prometeria ao candidato um prazo que o sistema não sabe contar.
    """
    if janela is None:
        return
    if not isinstance(janela, dict):
        raise ProfileValidationError(
            "A janela recursal do marco deve ser declarada como um objeto, ou não ser declarada."
        )
    unidade = janela.get("unit", "DIAS_CORRIDOS")
    if unidade != "DIAS_CORRIDOS":
        # Dias úteis exigiriam o calendário de dias sem expediente, que o Edital não publica — e
        # contá-los sem esse calendário produziria um prazo errado com aparência de exato. A
        # alternativa honesta é não declarar a janela.
        raise ProfileValidationError(
            "A janela recursal só admite contagem em dias corridos: contar em dias úteis exige o "
            "calendário de dias sem expediente, que o Edital não publica. Se a contagem do certame "
            "for outra, não declare a janela — a tempestividade continua sendo juízo motivado."
        )
    if not janela.get("admits"):
        # Marco que não admite recurso não precisa de duração, e declarar uma seria contradição.
        return
    duracao = janela.get("durationDays")
    if duracao is None:
        raise ProfileValidationError(
            "O marco declara que admite recurso e não declara por quantos dias: uma janela sem "
            "duração não é computável, e prometeria ao candidato um prazo que ninguém sabe contar."
        )
    if not isinstance(duracao, int) or isinstance(duracao, bool) or duracao <= 0:
        raise ProfileValidationError(
            "A duração da janela recursal deve ser um número inteiro de dias maior que zero: "
            "prazo de zero dias não é prazo."
        )


def validate_profiles(profiles: list[dict]) -> None:
    if not profiles:
        raise ProfileValidationError("O Edital deve possuir ao menos um Perfil.")
    codes = [profile["code"] for profile in profiles]
    if len(codes) != len(set(codes)):
        raise ProfileValidationError("Códigos de Perfil não podem se repetir no Edital.")
    for profile in profiles:
        validate_profile(profile)
