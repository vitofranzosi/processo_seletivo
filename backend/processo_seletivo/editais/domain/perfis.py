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


def validate_profile(profile: dict, *, modalidades_do_edital: set[str] | None = None) -> None:
    """As regras que se decidem olhando um Perfil só.

    `modalidades_do_edital` é o **escopo** de que a referência cruzada do quadro precisa e que um
    Perfil isolado não tem: distinguir "a Modalidade é de outro Perfil" de "a Modalidade não é de
    Perfil nenhum deste Edital" exige conhecer os irmãos. `validate_profiles` o calcula e o passa
    adiante; o serializer da API, que valida Perfil a Perfil, não o tem — e ali a conferência é
    **adiada**, e não afrouxada: `replace_draft` chama `validate_profiles` logo em seguida, com o
    escopo inteiro, e é lá que a recusa acontece com a mensagem certa (025, FR-158).
    """
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
    validate_vacancy_table(profile, modalidades_do_edital=modalidades_do_edital)


def validate_vacancy_table(profile: dict, *, modalidades_do_edital: set[str] | None = None) -> None:
    """O quadro de vagas do Perfil: uma linha geral, uma linha por Modalidade (025, D-002).

    **A validação mora no domínio, e não só no serializer**, pela razão que este módulo já registra
    acima: a interface administrativa invoca o command diretamente e não atravessa o serializer da
    API. Validar só ali deixaria sem verificação justamente o canal onde o dado é digitado.

    **A soma não é conferida aqui.** A conferência contra o total de vagas imediatas do Perfil é
    achado da operação de publicar — `editais/domain/validation.py` —, porque ela precisa alcançar
    também o conteúdo que uma Retificação produziria (FR-161, FR-177). O que se decide olhando só o
    Perfil é o que está abaixo: identidade, unicidade e forma da quantidade.

    **Ausência de linha nunca é zero** (FR-159, D-006). Um quadro sem linha para a PcD diz que o
    Edital não declarou aquela quantidade; quem quiser dizer zero declara a linha com `0`. Por isso
    não há verificação alguma de completude aqui: quadro parcial é legítimo, e quadro ausente
    também.
    """
    linhas = profile.get("vacancyTable") or []
    if not linhas:
        return

    identidade_do_perfil = profile.get("id", "")
    modalidades_do_perfil = {
        str(modalidade["id"])
        for modalidade in profile.get("competitionModalities") or []
        if modalidade.get("id")
    }

    gerais = 0
    reservadas: set[str] = set()
    for linha in linhas:
        identidade = linha.get("id", "")
        quantidade = linha.get("immediateVacancies")
        # `bool` é `int` em Python, e `True` passaria por inteiro não negativo sem esta recusa.
        if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade < 0:
            raise ProfileValidationError(
                "A quantidade de vagas de uma linha do quadro deve ser um número inteiro maior ou "
                "igual a zero.",
                campo="immediateVacancies",
                identidade=identidade or identidade_do_perfil,
            )

        modalidade_id = linha.get("modalityId")
        if not modalidade_id:
            gerais += 1
            if gerais > 1:
                raise ProfileValidationError(
                    "A ampla concorrência tem uma linha só no quadro de vagas do Perfil.",
                    campo="modalityId",
                    identidade=identidade or identidade_do_perfil,
                )
            continue

        modalidade_id = str(modalidade_id)
        if modalidade_id in reservadas:
            raise ProfileValidationError(
                "Uma Modalidade de Concorrência tem no máximo uma linha no quadro de vagas.",
                campo="modalityId",
                identidade=identidade or identidade_do_perfil,
            )
        reservadas.add(modalidade_id)

        if modalidade_id in modalidades_do_perfil:
            continue
        if modalidades_do_edital is None:
            # Escopo desconhecido: quem sabe distinguir os dois casos é `validate_profiles`, e
            # errar a mensagem seria pior do que adiá-la por uma chamada.
            continue
        # A mensagem separa os dois casos porque a correção é outra — é a mesma frase que
        # `documentos.py` já monta para o Documento Exigido, com o sujeito trocado (FR-158).
        motivo = (
            "não pertence ao Perfil declarado"
            if modalidade_id in modalidades_do_edital
            else "não é de nenhum Perfil deste Edital"
        )
        raise ProfileValidationError(
            f"A linha do quadro aponta uma modalidade que {motivo}.",
            campo="modalityId",
            identidade=identidade or identidade_do_perfil,
        )


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
    ("occurrence", "a ocorrência concreta que fixará a semente"),
    ("occurrenceAt", "o instante publicado em que a ocorrência acontece"),
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
    _validar_algoritmo_publicado(metodo["algorithm"])
    _validar_fonte_publicada(metodo["source"])
    _validar_instante_da_ocorrencia(metodo["occurrenceAt"])
    _validar_regra_publicada(metodo["normalization"]["rule"])
    _validar_substituicao_publicada(metodo["substitutionRule"]["rule"])
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


def _validar_fonte_publicada(fonte) -> None:
    """A fonte declarada precisa ser uma que este sistema consulta (021, FR-076).

    Era texto livre, e o adaptador ignorava o argumento: um Edital podia declarar `Random.org`, o
    sistema consultava a Caixa de qualquer jeito, e o manifesto publicava uma fonte que nunca foi
    consultada. A identidade da fonte é conteúdo normativo — se ela não determina de onde a semente
    vem, não é conteúdo normativo de nada.
    """
    from processo_seletivo.sorteios.infrastructure.fontes import FONTES

    if fonte not in FONTES:
        raise ProfileValidationError(
            f"Fonte de sorteio não publicada por este sistema: {fonte!r}. "
            f"As publicadas são: {', '.join(sorted(FONTES))}. Declarar uma fonte que o sistema não "
            "consulta faria o manifesto publicar uma origem que a semente não teve."
        )


def _validar_instante_da_ocorrencia(instante) -> None:
    """Quando a ocorrência acontece, publicado **antes** do congelamento (021, FR-077).

    **É este campo que impede descartar a ocorrência antes da hora.** Sem ele, bastava observar de
    manhã — a fonte ainda não publicou nada —, registrar a ausência como definitiva e deixar a
    regra de substituição avançar sozinha para a extração seguinte: a escolha da ocorrência voltava
    para a mesa, com a aparência de automatismo.

    Declarado, ele é norma: até esse instante, "a fonte não publicou" significa *ainda não*, e não
    *não haverá*.
    """
    from django.utils.dateparse import parse_datetime

    lido = parse_datetime(str(instante))
    if lido is None:
        raise ProfileValidationError(
            "O instante em que a ocorrência acontece (`occurrenceAt`) deve ser publicado no "
            "formato RFC 3339 com fuso — como 2026-11-20T20:00:00-03:00. É ele que separa 'a "
            "fonte ainda não publicou' de 'a fonte não publicará'."
        )
    if lido.utcoffset() is None:
        raise ProfileValidationError(
            "O instante da ocorrência deve declarar o fuso: sem ele, o mesmo texto designaria "
            "momentos diferentes conforme quem lê, e a fronteira entre 'ainda não' e 'não haverá' "
            "mudaria de lugar."
        )


def _validar_algoritmo_publicado(algoritmo) -> None:
    """O algoritmo declarado precisa ser um que este sistema executa (021, FR-027).

    Sem isto, o Edital declarava um nome, a constituição usava outro, e o manifesto publicava o
    nome declarado: quem reimplementasse a partir do que foi publicado chegaria a outra ordem — e
    concluiria, corretamente, que o sorteio não confere. O algoritmo é conteúdo normativo, e
    conteúdo normativo que o sistema não sabe executar é promessa.
    """
    from processo_seletivo.sorteios.domain.chave import ALGORITMOS

    if algoritmo not in ALGORITMOS:
        raise ProfileValidationError(
            f"Algoritmo de sorteio não publicado por este sistema: {algoritmo!r}. "
            f"Os publicados são: {', '.join(sorted(ALGORITMOS))}. Declarar um algoritmo que o "
            "sistema não executa faria o manifesto publicar um nome e a ordem vir de outro."
        )


def _validar_substituicao_publicada(regra) -> None:
    """A regra de substituição precisa ser executável, e não só escrita (021, FR-015).

    Prosa não é aplicável "sem escolha humana no momento da execução": no dia da indisponibilidade
    alguém teria de decidir qual é a ocorrência substituta, que é a escolha que a FR-015 proíbe.
    """
    from processo_seletivo.sorteios.domain.substituicao import REGRAS

    if regra not in REGRAS:
        raise ProfileValidationError(
            f"Regra de substituição não publicada por este sistema: {regra!r}. "
            f"As publicadas são: {', '.join(sorted(REGRAS))}."
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
    # O escopo que a referência cruzada do quadro precisa, e que só existe aqui: a distinção entre
    # "de outro Perfil" e "de Perfil nenhum deste Edital" pede conhecer os irmãos (025, FR-158).
    modalidades_do_edital = {
        str(modalidade["id"])
        for profile in profiles
        for modalidade in profile.get("competitionModalities") or []
        if modalidade.get("id")
    }
    for profile in profiles:
        validate_profile(profile, modalidades_do_edital=modalidades_do_edital)
