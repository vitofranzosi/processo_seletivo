"""Tradução entre o que a pessoa digita e o payload que os commands esperam.

Aqui não há regra de domínio: a validação real acontece em `editais.domain`, invocada pelo
command. O que existe aqui é conversão de tipo e agrupamento de campos indexados — e as
mensagens que tornam um erro de conversão compreensível antes de chegar ao domínio.
"""

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.classificacao.domain.faixa import ALVO_FIXO
from processo_seletivo.editais.domain import duplicacao, secoes
from processo_seletivo.editais.domain.perfis import identidade_da_linha_geral, listas_reservadas
from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.shared.tempo import ZONA as ZONA_INSTITUCIONAL

# A zona institucional mora em `shared/tempo.py` desde a 018: a contagem do prazo recursal é
# domínio, e domínio não importa de `interface` (T-008).
ZONA = ZONA_INSTITUCIONAL

RESERVA = [
    ("NONE", "Não há cadastro reserva"),
    ("LIMITED", "Cadastro reserva limitado"),
    ("UNLIMITED", "Cadastro reserva ilimitado"),
]


def _indices(dados, prefixo):
    """Índices presentes no formulário, em ordem — as linhas podem ter buracos após remoções."""
    vistos = set()
    for chave in dados:
        if chave.startswith(f"{prefixo}-") and chave.endswith("-id"):
            vistos.add(chave[len(prefixo) + 1 : -3])
    return sorted(vistos, key=lambda valor: int(valor) if valor.isdigit() else valor)


def _texto(dados, chave):
    return (dados.get(chave) or "").strip()


def _inteiro_opcional(dados, chave):
    """Vazio é `None` — "não declarado" —, e não zero.

    `_inteiro` tem padrão porque `order` sempre existe; aqui a ausência é significativa: ela é o
    que a `012` lê como uma avaliação por inscrição (FR-009).
    """
    bruto = _texto(dados, chave)
    if not bruto:
        return None
    try:
        return int(bruto)
    except ValueError as exc:
        raise ValueError(f"'{bruto}' não é um número inteiro.") from exc


def _inteiro(dados, chave, padrao=0):
    bruto = _texto(dados, chave)
    if not bruto:
        return padrao
    try:
        return int(bruto)
    except ValueError as exc:
        raise ValueError(f"'{bruto}' não é um número inteiro.") from exc


def _decimal(dados, chave):
    """Vazio é ausência, e ausência tem significado: 'esta Etapa não pondera'."""
    bruto = _texto(dados, chave)
    if not bruto:
        return None
    try:
        return Decimal(bruto.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"'{bruto}' não é um número válido.") from exc


def _marcado(dados, chave):
    return bool(_texto(dados, chave))


def _instante(dados, chave):
    """`datetime-local` chega sem fuso; a zona institucional é aplicada aqui."""
    bruto = _texto(dados, chave)
    if not bruto:
        return None
    try:
        return datetime.fromisoformat(bruto).replace(tzinfo=ZONA)
    except ValueError as exc:
        raise ValueError(f"'{bruto}' não é uma data e hora válidas.") from exc


def _modalidades(dados, prefixo):
    """As modalidades de um Perfil, em campos próprios.

    Substitui a caixa de texto no formato `CÓDIGO — Nome`, que perdia tudo o que não coubesse em
    duas palavras: percentual, fundamento e versão do fundamento não tinham onde ser digitados, e
    a Regra Normativa era destruída a cada gravação.

    A Regra só é montada quando há fundamento. Ela é opcional; o que não é opcional é a `version`
    quando ela existe — o command a exige desde a `001`.
    """
    modalidades = []
    for indice in _indices(dados, prefixo):
        base = f"{prefixo}-{indice}"
        fundamento = _texto(dados, f"{base}-foundation")
        modalidade = {
            "id": _texto(dados, f"{base}-id"),
            "code": _texto(dados, f"{base}-code"),
            "name": _texto(dados, f"{base}-name"),
            "description": _texto(dados, f"{base}-description"),
        }
        if fundamento or _texto(dados, f"{base}-version") or _texto(dados, f"{base}-percentage"):
            modalidade["normativeRule"] = {
                "id": _texto(dados, f"{base}-ruleId"),
                "foundation": fundamento,
                "version": _texto(dados, f"{base}-version"),
                "percentage": _decimal(dados, f"{base}-percentage"),
            }
        modalidades.append(modalidade)
    return modalidades


def _fatos(dados, prefixo):
    """Os fatos declarados de um Perfil, pelo mesmo esquema de prefixo composto da modalidade."""
    fatos = []
    for indice in _indices(dados, prefixo):
        base = f"{prefixo}-{indice}"
        fatos.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "code": _texto(dados, f"{base}-code"),
                "label": _texto(dados, f"{base}-label"),
                "type": _texto(dados, f"{base}-type"),
            }
        )
    return fatos


def _linhas(dados, prefixo):
    """As linhas do quadro de vagas de um Perfil, pelo mesmo prefixo composto da modalidade.

    **Quantidade em branco não grava linha** (FR-159, D-006). A tela oferece uma linha para a ampla
    concorrência e uma para cada Modalidade declarada; quem não declara a quantidade de uma delas
    está dizendo que o Edital não declarou aquela repartição — e não que ela é zero. Quem quiser
    dizer zero digita `0`, que é linha com `0` e não ausência.

    `modalityId` vazio **é** a linha geral, a da ampla concorrência, e não uma referência faltando
    (D-002, D-004).
    """
    linhas = []
    for indice in _indices(dados, prefixo):
        base = f"{prefixo}-{indice}"
        quantidade = _texto(dados, f"{base}-immediateVacancies")
        if not quantidade:
            continue
        linhas.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "modalityId": _texto(dados, f"{base}-modalityId") or None,
                "immediateVacancies": _inteiro(dados, f"{base}-immediateVacancies"),
            }
        )
    return linhas


def ler_classificacao(dados):
    """Os marcos de cada Perfil, indexados pelo identificador do Perfil.

    A chave é a identidade do Perfil, e não o índice de tela: este passo funde os marcos sobre
    Perfis já persistidos, e o índice diria respeito à ordem em que a tela os desenhou.
    """
    return {
        identificador: _marcos(dados, f"marco-{identificador}")
        for identificador in dados.getlist("perfil_id")
    }


def _marcos(dados, prefixo):
    """Os marcos classificatórios de um Perfil, com seus critérios de desempate.

    Duas indexações aninhadas, e não uma: `marco-<perfil>-<sub>` para o marco, e
    `criterio-<perfil>-<sub>-<n>` para cada critério dentro dele. É a mesma composição de prefixo
    que a modalidade usa, um nível mais fundo — porque o critério pertence ao marco, e renumerá-lo
    por Perfil faria dois marcos irmãos disputarem a mesma linha.

    A `order` do critério vem do formulário, e não da posição: é campo publicado, e a Retificação o
    altera por identidade (015, FR-015).
    """
    marcos = []
    for indice in _indices(dados, prefixo):
        base = f"{prefixo}-{indice}"
        criterios = []
        # O critério pertence ao marco, e o marco ao Perfil: o prefixo carrega os dois níveis.
        # `criterio-<perfil>-<marco>-<n>`, e não `criterio-<marco>-<n>` — sem o Perfil, dois
        # Perfis com marco de mesmo índice disputariam a mesma linha do formulário.
        dono = prefixo.removeprefix("marco-")
        for sub_indice in _indices(dados, f"criterio-{dono}-{indice}"):
            criterio_base = f"criterio-{dono}-{indice}-{sub_indice}"
            tipo = _texto(dados, f"{criterio_base}-type")
            # O parâmetro é **do tipo**: quem compara pontuação aponta Etapa, quem compara fato
            # aponta fato. Guardar os dois faria o critério declarar um alvo que ele não consome.
            alvo = _texto(dados, f"{criterio_base}-target")
            parametros = {}
            if alvo:
                parametros = (
                    {"stageId": alvo} if tipo == "MAIOR_PONTUACAO_NA_ETAPA" else {"factId": alvo}
                )
            criterios.append(
                {
                    "id": _texto(dados, f"{criterio_base}-id"),
                    "order": _inteiro(dados, f"{criterio_base}-order"),
                    "type": tipo,
                    "parameters": parametros,
                    "whenMissing": _texto(dados, f"{criterio_base}-whenMissing"),
                }
            )
        escala = _inteiro_opcional(dados, f"{base}-scale")
        modo = _texto(dados, f"{base}-mode")
        marcos.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "code": _texto(dados, f"{base}-code"),
                "name": _texto(dados, f"{base}-name"),
                # A pergunta de entrada do cartão (030, FR-413). É ela que governa quais campos o
                # fragmento seguinte renderiza — e, por isso, precisa viajar no envio como
                # qualquer outra declaração. `""` é o marco composto antes desta feature, relido
                # sem que a tela lhe atribua forma nenhuma.
                "orderProduction": _texto(dados, f"{base}-orderProduction"),
                # As Etapas enumeradas: seleção múltipla, e a ordem aqui não é normativa.
                # `getlist` de um campo vazio devolve `[""]`, que é lista truthy: sem o filtro, um
                # marco sem Etapa alguma passaria pela validação que exige ao menos uma.
                "stages": [item for item in dados.getlist(f"{base}-stages") if item],
                "operation": _texto(dados, f"{base}-operation"),
                "normalization": _texto(dados, f"{base}-normalization"),
                # Escala e modo viajam mesmo vazios: é a validação que recusa, com mensagem que
                # nomeia o que falta — e não o formulário, que devolveria silêncio.
                "rounding": {"scale": escala, "mode": modo},
                # A janela recursal do marco. **Ausente quando o marco não a declara**, e a
                # ausência é a afirmação certa: sem prazo publicado, ninguém inventa prazo
                # (FR-020, FR-028, FR-030).
                "appealWindow": _janela_recursal(dados, base),
                # O método do sorteio, **ausente quando o marco não sorteia** — que é a maioria
                # deles. A ausência é a afirmação certa: sem método publicado, o sistema não
                # escolhe um (021, FR-013, FR-066).
                "drawMethod": _metodo_de_sorteio(dados, base),
                # A regra de corte, **ausente quando o marco não corta** — que é a maioria deles. A
                # ausência é a afirmação certa: marco sem regra não corta, e a Etapa que ele
                # alimentaria continua recebendo o conjunto que a progressão da 013 entrega
                # (014, FR-178, FR-214).
                "cutRule": _regra_de_corte(dados, base),
                "tiebreakers": criterios,
            }
        )
    return marcos


def metodo_comum_do_formulario(dados):
    """O método do sorteio comum ao Edital, lido do passo da Classificação (030, FR-429).

    **Reusa `_metodo_de_sorteio`**, com a base `edital` em vez do prefixo do marco: é o mesmo
    objeto normativo, com os mesmos campos e a mesma regra de tudo-ou-nada — só muda de quem ele é.
    Uma segunda leitura própria divergiria da do marco no primeiro campo novo.

    **Sem a Etapa de habilitação**, que é do marco: qual Etapa habilita a participar do sorteio
    depende de quais Etapas aquele marco enumera, e um valor comum a todos endereçaria Etapa que
    parte deles não mede. É a diferença entre os nove campos do Edital e os dez do marco.
    """
    metodo = _metodo_de_sorteio(dados, "edital")
    if metodo is None:
        return None
    return {chave: valor for chave, valor in metodo.items() if chave != "qualifyingStageId"}


def metodo_comum_para_exibicao(edital):
    """O método comum de volta para a tela, achatado no prefixo `draw`, como o do marco."""
    return _metodo_para_exibicao(edital.metodo_de_sorteio_comum)


def metodo_comum_digitado(dados):
    """O método comum **como está no formulário**, para a reexibição depois de uma recusa (030).

    Existe pela mesma razão que `blocos_opcionais_do_marco`: a recusa existe para que a pessoa
    corrija o que errou, e não para apagar o que ela acertou. A validação do método acontece
    **antes** da gravação — um método pela metade é recusado inteiro —, de modo que ler o Edital do
    banco devolveria a tela com os nove campos vazios, e quem esqueceu a regra de substituição
    teria de redigitar os outros oito.

    Passa pelo mesmo achatamento do marco, e não por uma leitura própria: são os mesmos campos, e
    duas cópias divergiriam na primeira que mudasse.
    """
    return _metodo_para_exibicao(metodo_comum_do_formulario(dados))


# Os seis campos do método, na ordem em que a tela os pede. `normalization` e `substitutionRule`
# são pares `{rule, text}` — o identificador que a máquina aplica e a frase que a pessoa lê —, e é
# por isso que eles não estão nesta tupla simples (021, FR-013).
CAMPOS_SIMPLES_DO_METODO = ("algorithm", "source", "occurrence", "occurrenceAt", "derivation")


def opcoes_do_metodo():
    """As listas fechadas do método, lidas de quem as executa — nas três telas (035, FR-507).

    **Ela nasceu na Retificação, e a composição não a tinha.** A Retificação já oferecia quatro
    campos fechados como escolha; a composição deixava digitar os mesmos quatro e recusava ao
    gravar, de modo que a pessoa descobria o vocabulário por tentativa. Mudá-la de lugar é o que
    torna a `FR-507` *generalizar* em vez de *criar* — e é o que impede a segunda lista: duas
    origens para o mesmo vocabulário divergem na primeira vez que ele muda, e a divergência
    apareceria como a Retificação oferecendo o que a composição não oferece.

    Importadas aqui dentro, e não no topo: `sorteios` é outro contexto, e a tela só precisa das
    listas quando desenha um marco que sorteia.
    """
    from processo_seletivo.sorteios.domain.chave import ALGORITMOS
    from processo_seletivo.sorteios.domain.normalizacao import REGRAS as NORMALIZACOES
    from processo_seletivo.sorteios.domain.substituicao import REGRAS as SUBSTITUICOES
    from processo_seletivo.sorteios.infrastructure.fontes import fontes_publicadas

    return {
        "drawMethod/algorithm": tuple((nome, nome) for nome in sorted(ALGORITMOS)),
        "drawMethod/source": tuple((nome, nome) for nome in sorted(fontes_publicadas())),
        "drawMethod/normalization/rule": tuple((nome, nome) for nome in sorted(NORMALIZACOES)),
        "drawMethod/substitutionRule/rule": tuple((nome, nome) for nome in sorted(SUBSTITUICOES)),
    }


def _metodo_de_sorteio(dados, base):
    """`{...}` quando o marco declara o método do sorteio; `None` quando não declara.

    **Nada de meio-declarado sai daqui.** Se a pessoa não preencheu nada, o método é ausente e a
    ausência viaja como ausência. Se preencheu alguma coisa, o objeto viaja inteiro e a validação
    do Perfil é que recusa a metade, nomeando o que falta — o formulário devolveria silêncio, e
    silêncio sobre método é o que faz a escolha voltar para a mesa no dia do sorteio (FR-015).
    """
    valores = {campo: _texto(dados, f"{base}-draw-{campo}") for campo in CAMPOS_SIMPLES_DO_METODO}
    regra_normalizacao = _texto(dados, f"{base}-draw-normalizationRule")
    texto_normalizacao = _texto(dados, f"{base}-draw-normalizationText")
    regra_substituicao = _texto(dados, f"{base}-draw-substitutionRule")
    texto_substituicao = _texto(dados, f"{base}-draw-substitutionText")
    etapa_de_habilitacao = _texto(dados, f"{base}-draw-qualifyingStageId")
    preenchidos = [
        *valores.values(),
        regra_normalizacao,
        texto_normalizacao,
        regra_substituicao,
        texto_substituicao,
        etapa_de_habilitacao,
    ]
    if not any(preenchidos):
        return None
    return {
        **valores,
        "normalization": {"rule": regra_normalizacao, "text": texto_normalizacao},
        "substitutionRule": {"rule": regra_substituicao, "text": texto_substituicao},
        # `None` quando não declarada, e não `""`: a ausência é "não há Etapa de habilitação antes
        # do sorteio", que é o caso dos quatro Editais lidos (021, R-012).
        "qualifyingStageId": etapa_de_habilitacao or None,
    }


# As três escolhas da janela recursal, como viajam no formulário. Nomes em português porque é o
# que a pessoa marca na tela; o conteúdo publicado continua falando `admits` (FR-020, FR-113).
ADMITE, NAO_ADMITE, NAO_DECLARADA = "admite", "nao_admite", "nao_declarada"


def _janela_recursal(dados, base):
    """`{"admits": ..., "durationDays": ..., "unit": ...}` — ou `None`, quando não declarada.

    **Três estados, e uma escolha de três** (FR-020, FR-113). Era caixa de marcação, e caixa de
    marcação tem dois: a negativa só nascia se a pessoa desmarcasse a caixa **e** digitasse um
    prazo — que é exatamente o que ninguém digita para um marco que não admite recurso. O terceiro
    estado ficava inalcançável pela tela que existe para declará-lo, e confundir a negativa com o
    silêncio troca "não cabe recurso" por "cabe para sempre".

    **A negativa não carrega prazo**: marco que não admite recurso não tem duração a declarar, e
    declarar uma seria contradição — a validação do Perfil recusa a metade, não a negativa inteira.

    A unidade viaja como campo publicado porque a frase normativa do documento a cita: *"no prazo
    de 5 (cinco) dias corridos"*. Ela é única na V1, e mesmo assim é conteúdo, e não constante de
    código: o dia em que outra unidade existir, os Editais já publicados continuarão dizendo em que
    unidade o prazo deles corria.
    """
    declaracao = _texto(dados, f"{base}-appealDeclaration")
    if declaracao == NAO_ADMITE:
        return {"admits": False, "durationDays": None, "unit": _unidade(dados, base)}
    if declaracao != ADMITE:
        return None
    return {
        "admits": True,
        "durationDays": _inteiro_opcional(dados, f"{base}-appealDurationDays"),
        "unit": _unidade(dados, base),
    }


def _regra_de_corte(dados, base):
    """Os seis campos da regra, ou `None` quando o marco não corta (014, FR-178).

    **A espécie do alvo é o interruptor.** Vazia significa "este marco não corta", e é o estado de
    quase todo marco — não há caixa de marcação separada para isso, pela razão que a janela recursal
    aprendeu a duras penas: um estado que só nasce de uma combinação que ninguém faz é um estado
    inalcançável pela tela que existe para declará-lo.

    **Os quatro campos sem padrão viajam mesmo vazios**, como escala e modo do arredondamento já
    fazem: quem recusa é a aferição de publicabilidade, com mensagem que nomeia o que falta — e não
    o formulário, que devolveria silêncio. O rascunho pode estar pela metade; a publicação não.
    """
    especie = _texto(dados, f"{base}-cutTargetKind")
    if not especie:
        return None
    return {
        "targetKind": especie,
        # `targetCount` só na espécie fixa: o alvo tem uma fonte só, e mandar o número junto com a
        # derivada faria o conteúdo publicado afirmar duas origens para a mesma quantidade.
        "targetCount": (
            _inteiro_opcional(dados, f"{base}-cutTargetCount") if especie == ALVO_FIXO else None
        ),
        "surplusCount": _inteiro_opcional(dados, f"{base}-cutSurplusCount") or 0,
        "tieOutcome": _texto(dados, f"{base}-cutTieOutcome"),
        "governedStage": _texto(dados, f"{base}-cutGovernedStage"),
        "continuation": _texto(dados, f"{base}-cutContinuation"),
    }


def _ou_vazio(valor):
    """Zero é valor, e `None` é ausência: o `or ""` de sempre confundiria os dois aqui."""
    return "" if valor is None else valor


def _corte_para_exibicao(regra):
    """A regra de volta para a tela, campo a campo — e a ausência de volta como ausência."""
    regra = regra or {}
    return {
        "cutTargetKind": regra.get("targetKind") or "",
        "cutTargetCount": _ou_vazio(regra.get("targetCount")),
        "cutSurplusCount": _ou_vazio(regra.get("surplusCount")),
        "cutTieOutcome": regra.get("tieOutcome") or "",
        "cutGovernedStage": regra.get("governedStage") or "",
        "cutContinuation": regra.get("continuation") or "",
    }


def _unidade(dados, base):
    return _texto(dados, f"{base}-appealUnit") or "DIAS_CORRIDOS"


def _metodo_para_exibicao(metodo):
    """Os seis campos do método de volta para a tela, achatados no prefixo `draw`.

    Achatados porque o formulário é plano: `{rule, text}` viraria dois campos de qualquer forma, e
    montá-los aqui é o que mantém o template sem lógica. Vazio quando não há método, e vazio é o
    que a tela desenha — nada de rótulo institucional por padrão.
    """
    declarado = metodo or {}
    normalizacao = declarado.get("normalization") or {}
    substituicao = declarado.get("substitutionRule") or {}
    return {
        "drawAlgorithm": declarado.get("algorithm") or "",
        "drawSource": declarado.get("source") or "",
        "drawOccurrence": declarado.get("occurrence") or "",
        "drawOccurrenceAt": declarado.get("occurrenceAt") or "",
        "drawDerivation": declarado.get("derivation") or "",
        "drawNormalizationRule": normalizacao.get("rule") or "",
        "drawNormalizationText": normalizacao.get("text") or "",
        "drawSubstitutionRule": substituicao.get("rule") or "",
        "drawSubstitutionText": substituicao.get("text") or "",
        "drawQualifyingStageId": declarado.get("qualifyingStageId") or "",
    }


def marco_do_formulario(dados, indice, sub):
    """O marco de índice `sub` do Perfil `indice`, lido do formulário — `None` se não está lá.

    Existe para o fragmento que recompõe o cartão quando a forma da ordem muda (030, FR-413): o que
    precisa ser relido é o que está **digitado agora**, e não o que está gravado — a pessoa está
    decidindo sobre o preenchimento em curso, e recompor sobre o banco apagaria tudo o que ela
    escreveu desde a última gravação.

    Lê pelo caminho público do passo inteiro, `_marcos`, e não por uma segunda leitura própria:
    duas leituras do mesmo formulário divergiriam no primeiro campo novo.
    """
    for posicao, marco in zip(
        _indices(dados, f"marco-{indice}"), _marcos(dados, f"marco-{indice}"), strict=True
    ):
        if str(posicao) == str(sub):
            return marco
    return None


def blocos_opcionais_do_marco(marco):
    """Janela recursal, método do sorteio e regra de corte — do contrato para a tela.

    Existe porque a reexibição depois de uma recusa os perdia. `_reexibir_marco` montava o marco
    digitado com identidade, Etapas, arredondamento e critérios, e **não** com estes três: quem
    declarava um corte, errava outro campo e recebia a recusa via o corte sumir da tela — e o
    salvamento seguinte gravava o Edital sem ele, sem que nada avisasse. É a mesma classe de perda
    que `_marco_persistido` nomeia três vezes, num quarto caminho.

    O mapeamento é o do persistido, e por isso mora aqui em vez de na view: são as mesmas chaves,
    e duas cópias divergiriam na primeira que mudasse.
    """
    janela = marco.get("appealWindow") or {}
    return {
        "appealDeclaration": _declaracao_do_marco(marco.get("appealWindow")),
        "appealDurationDays": janela.get("durationDays") or "",
        "appealUnit": janela.get("unit") or "DIAS_CORRIDOS",
        **_metodo_para_exibicao(marco.get("drawMethod")),
        **_corte_para_exibicao(marco.get("cutRule")),
    }


def _declaracao_do_marco(janela):
    """Qual das três escolhas a tela deve reexibir marcada.

    **Vazio é não declarada, e não negativa.** O rascunho guarda `{}` quando nada foi declarado —
    o campo tem `default=dict` —, e ler isso como "não admite recurso" faria a tela inventar norma
    que ninguém escreveu, e gravá-la no salvamento seguinte.
    """
    if not janela:
        return NAO_DECLARADA
    return ADMITE if janela.get("admits") else NAO_ADMITE


def ler_identificacao(dados):
    """Título e descrição; número e ano continuam sendo da criação do Edital."""
    return {"title": _texto(dados, "title"), "description": _texto(dados, "description")}


def ler_perfis(dados):
    perfis = []
    for indice in _indices(dados, "perfil"):
        base = f"perfil-{indice}"
        reserva = _texto(dados, f"{base}-reserveType") or "NONE"
        limite = _texto(dados, f"{base}-reserveLimit")
        perfis.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "code": _texto(dados, f"{base}-code"),
                "name": _texto(dados, f"{base}-name"),
                "description": _texto(dados, f"{base}-description"),
                "requirements": [
                    linha.strip()
                    for linha in _texto(dados, f"{base}-requirements").splitlines()
                    if linha.strip()
                ],
                "immediateVacancies": _inteiro(dados, f"{base}-immediateVacancies"),
                # Qual das Modalidades é a ampla concorrência (014, D-014, FR-231). Vazio significa
                # que o Perfil não declara nenhuma, que é o formato em que ela existe só como a
                # linha geral do quadro.
                "generalCompetitionModalityId": _texto(
                    dados, f"{base}-generalCompetitionModalityId"
                )
                or None,
                # A reversão declarada (016, D-007). Objeto quando há gatilho, `None` quando não —
                # nunca objeto pela metade, que a publicação recusaria nomeando o Perfil.
                "vacancyReversion": (
                    {"kind": especie}
                    if (especie := _texto(dados, f"{base}-vacancyReversion"))
                    else None
                ),
                # Como este Perfil comunica a convocação (019, D-009). Vazio significa que o Edital
                # **não declarou forma** — e não que convoca por publicação: as duas formas da
                # amostra são normais, e a `019` recusa convocar sem declaração em vez de escolher.
                "callForm": _texto(dados, f"{base}-callForm") or None,
                "reserveType": reserva,
                "reserveLimit": int(limite) if reserva == "LIMITED" and limite else None,
                "locality": _texto(dados, f"{base}-locality"),
                "duties": _texto(dados, f"{base}-duties"),
                "workload": _texto(dados, f"{base}-workload"),
                "compensation": _texto(dados, f"{base}-compensation"),
                # As linhas de modalidade são indexadas dentro do índice do Perfil, e não
                # renumeradas: `modalidade-3-…` pertence ao Perfil cujo prefixo é `perfil-3`.
                "competitionModalities": _modalidades(dados, f"modalidade-{indice}"),
                # Pelo mesmo esquema de prefixo composto: `marco-3-…` pertence ao `perfil-3`.
                "declaredFacts": _fatos(dados, f"fato-{indice}"),
                "classificationMilestones": _marcos_do_perfil(dados, indice),
                # Travessia 1 de 4. As outras três são `perfis_persistidos`, `perfis_do_edital` e
                # a recriação em `draft.replace_draft`: `replace_draft` apaga e recria tudo, e uma
                # coleção do Perfil que falte em qualquer uma delas **some** na gravação da etapa
                # seguinte, sem erro nenhum (025, R-009).
                "vacancyTable": _linhas(dados, f"linha-{indice}"),
            }
        )
    return perfis


def _marcos_do_perfil(dados, indice):
    """Os marcos que viajam com o Perfil nesta etapa — quase sempre nenhum.

    A etapa Perfis não desenha marco: eles são da Classificação, e a gravação os **preserva** do
    que está gravado (`PRESERVADO_DA_ETAPA`). A exceção é o Perfil criado por duplicação e ainda não
    gravado (043, R-003): ele não tem par gravado de onde preservar, e leva os marcos da origem num
    campo oculto, na forma do contrato. `_preservando` deixa atravessar o que Perfil novo traz, e é
    por isso que a gravação não precisou mudar.

    **É a quinta travessia dos marcos**, ao lado das quatro que a `025` nomeou (R-009). Como elas,
    a que faltar apaga em silêncio — e esta faltaria na recusa, que devolve o digitado.

    **O campo diz também quais marcos têm identidade derivada**, e a leitura a deriva de novo do
    Código e da denominação **digitados agora**: quem corrige o Código da cópia no cartão antes de
    gravar publicaria, sem isso, o marco com o Código de antes da correção (FR-644).
    """
    bruto = _texto(dados, f"perfil-{indice}-marcosEmTransito")
    if not bruto:
        return _marcos(dados, f"marco-{indice}")
    try:
        transito = json.loads(bruto)
        marcos, derivados = transito["marcos"], transito["derivados"]
        legivel = (
            isinstance(marcos, list)
            and all(isinstance(marco, dict) for marco in marcos)
            and isinstance(derivados, list)
            and len(derivados) == len(marcos)
            and all(isinstance(par, list) and len(par) == 2 for par in derivados)
        )
    except (json.JSONDecodeError, TypeError, KeyError):
        legivel = False
    if not legivel:
        raise ValueError(
            "Os marcos de classificação que este Perfil trouxe da duplicação não puderam ser "
            "lidos. Remova este Perfil e duplique a origem de novo."
        )
    return duplicacao.rederivar(
        marcos,
        [(bool(codigo), bool(nome)) for codigo, nome in derivados],
        codigo=_texto(dados, f"perfil-{indice}-code"),
        nome=_texto(dados, f"perfil-{indice}-name"),
    )


def ler_eventos(dados):
    """A ordem é dado enviado, e não a posição de leitura das linhas.

    `_indices` devolve os índices **ordenados numericamente**, de modo que a posição da linha no
    documento é descartada antes de chegar aqui: mover a linha na tela, sozinho, não mudaria nada, e
    o defeito seria silencioso — a tela mostraria a ordem nova e o banco guardaria a antiga. Por
    isso cada linha carrega o próprio `order`, que os botões de subir e descer atualizam.

    A renumeração final é do servidor: o que vem do formulário estabelece a **sequência**, e não os
    números, que precisam ser 1..n sem buraco por causa da unicidade de `(cronograma, order)`.
    """
    eventos = []
    for indice in _indices(dados, "evento"):
        base = f"evento-{indice}"
        eventos.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "type": _texto(dados, f"{base}-type"),
                "description": _texto(dados, f"{base}-description"),
                "startAt": _instante(dados, f"{base}-startAt"),
                "endAt": _instante(dados, f"{base}-endAt"),
                "order": _inteiro(dados, f"{base}-order", 0),
                # Onde o evento acontece (021, D-008). Vazio significa "não declarado", e é o que
                # a tela desenha por padrão: nenhum valor institucional se aplica sozinho.
                "location": _texto(dados, f"{base}-location"),
            }
        )
    return _renumerar(eventos)


def _renumerar(itens):
    """A sequência vem do formulário; os números, do servidor.

    A unicidade de `(edital, order)` não admite buraco nem repetição, e o formulário pode chegar
    com as duas coisas — uma remoção deixa buraco, e um navegador sem JavaScript manda tudo igual.
    A ordenação é estável, então nesse último caso a ordem de leitura prevalece, que é o
    comportamento anterior.
    """
    itens.sort(key=lambda item: item["order"])
    for ordem, item in enumerate(itens, 1):
        item["order"] = ordem
    return itens


def ler_etapas(dados):
    etapas = []
    for indice in _indices(dados, "etapa"):
        base = f"etapa-{indice}"
        # A forma governa quatro dos campos ao lado, e o domínio é categórico: a pontuada **proíbe**
        # os rótulos do resultado, a decisória **proíbe** as notas (012, FR-033, FR-121). A tela
        # agora esconde o que a escolha marcada torna inaplicável — mas esconder não é descartar:
        # quem digitou "Deferido" e depois marcou "Com pontuação" continua enviando o rótulo, e
        # envio forjado envia o que quiser. Quem decide o que sobrevive é aqui.
        #
        # É o mesmo lugar e a mesma razão de `_janela_recursal`, que já descarta o prazo do marco
        # que não admite recurso. Sem isto, o formulário oferecia um campo e a submissão o recusava
        # — a recusa era correta, e o convite é que não devia existir.
        #
        # `forma` continua sendo lida crua: trocá-la por um dos dois valores conhecidos faria uma
        # forma inválida virar PONTUADA em silêncio, e a validação deixaria de alcançá-la.
        decisoria = (_texto(dados, f"{base}-forma") or Forma.PONTUADA) == Forma.DECISORIA
        etapas.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "name": _texto(dados, f"{base}-name"),
                "order": _inteiro(dados, f"{base}-order", 0),
                "weight": _decimal(dados, f"{base}-weight"),
                "eliminatory": _marcado(dados, f"{base}-eliminatory"),
                "classificatory": _marcado(dados, f"{base}-classificatory"),
                "minimumScore": (None if decisoria else _decimal(dados, f"{base}-minimumScore")),
                # As duas do incremento da `012`. Vazio é "não declarado", e o assistente precisa
                # devolvê-las porque ele reenvia o rascunho inteiro a cada passo: campo que ele não
                # lê vira `null` na próxima gravação de qualquer outra Etapa (FR-007).
                "evaluationsPerRegistration": _inteiro_opcional(
                    dados, f"{base}-evaluationsPerRegistration"
                ),
                "maximumScore": (None if decisoria else _decimal(dados, f"{base}-maximumScore")),
                # As três do incremento da revisão (D-008). A forma vem sempre preenchida, porque o
                # controle é um par de opções com uma marcada: `_texto` vazio só acontece em envio
                # forjado, e ali `or PONTUADA` devolve o que a ausência significa (FR-120). Os
                # rótulos vazios significam "não se aplica" e viajam como vazio até o snapshot.
                "forma": _texto(dados, f"{base}-forma") or Forma.PONTUADA,
                "rotuloFavoravel": (_texto(dados, f"{base}-rotuloFavoravel") if decisoria else ""),
                "rotuloDesfavoravel": (
                    _texto(dados, f"{base}-rotuloDesfavoravel") if decisoria else ""
                ),
                # Vazio é "não vinculada a Evento", e não Evento inexistente.
                "scheduleEventId": _texto(dados, f"{base}-scheduleEventId") or None,
            }
        )
    return _renumerar(etapas)


def _modalidade_para_o_formulario(modalidade):
    regra = getattr(modalidade, "regra_normativa", None)
    return {
        "id": str(modalidade.id),
        "code": modalidade.code,
        "name": modalidade.name,
        "description": modalidade.description,
        # A linha carrega os dois identificadores. O da Regra existe mesmo quando ela ainda não
        # existe: a linha nova precisa nascer com identidade, ou não há o que preservar.
        "ruleId": str(regra.id) if regra else str(uuid4()),
        "foundation": regra.foundation if regra else "",
        "version": regra.version if regra else "",
        "percentage": "" if regra is None or regra.percentage is None else f"{regra.percentage:f}",
    }


def ler_secoes(dados):
    """Só as textuais, e só as que **mudaram** em relação ao catálogo.

    A tela mostra as sete seções e envia as quatro textuais preenchidas; gravar todas criaria linha
    para seção que ninguém tocou, e a regra "ausência de linha significa texto padrão do catálogo"
    deixaria de valer no primeiro salvamento desta etapa. O efeito prático seria congelar a redação
    institucional: corrigir o texto padrão em código não alcançaria mais nenhum Edital que tivesse
    passado por aqui, e não haveria como distinguir texto revisado de texto intocado.

    A comparação é sobre o texto sem espaço nas bordas: um `\\r\\n` que o navegador acrescenta não é
    edição.
    """
    editadas = []
    for chave in sorted(secoes.CHAVES_TEXTUAIS):
        digitado = _texto(dados, f"secao-{chave}")
        padrao = secoes.POR_CHAVE[chave].default_text
        if digitado and digitado != padrao.strip():
            editadas.append({"key": chave, "content": digitado})
    return editadas


def secoes_do_edital(edital):
    """O catálogo inteiro, na ordem, com o texto vigente de cada seção textual.

    As geradas aparecem para que quem elabora veja a estrutura do documento — e leia, ao lado de
    cada uma, de que dado ela vem. Elas não têm campo de texto: o conteúdo se corrige no dado que
    o origina.
    """
    redigidas = {item.key: item.content for item in edital.secoes.all()}
    return [
        {
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "gerada": secao.gerada,
            "source": secao.source,
            "origem": ORIGEM.get(secao.source, (secao.source, ""))[0],
            "etapa_da_origem": ORIGEM.get(secao.source, ("", ""))[1],
            "content": redigidas.get(secao.key, secao.default_text),
            "editada": secao.key in redigidas,
        }
        for secao in secoes.CATALOGO
    ]


# Como cada origem é lida por quem elabora, e onde ela se edita. A chave é a coleção do snapshot,
# e o valor liga o vocabulário do conteúdo publicado ao do assistente — que é o que permite
# oferecer, ao lado de uma seção gerada, o caminho para o dado que a origina.
# As cinco origens que o catálogo de seções gera. Faltavam duas, e a ausência não era silenciosa:
# a seção caía no token inglês — "Composta automaticamente a partir de attachments" — e perdia o
# link para a etapa que a origina, que é o segundo elemento de cada par.
ORIGEM = {
    "profiles": ("Perfis de Vaga", "perfis"),
    "schedule": ("Cronograma", "cronograma"),
    "stages": ("Etapas de Avaliação", "etapas"),
    "documentRequirements": ("Documentos Exigidos", "inscricao"),
    "attachments": ("Anexos do Edital", "anexos"),
}


def secoes_persistidas(edital):
    """Seções textuais já editadas, no formato do command — para preservá-las ao salvar outra
    etapa. Ausência de linha continua significando "texto padrão do catálogo"."""
    return [{"key": item.key, "content": item.content} for item in edital.secoes.all()]


def perfis_do_edital(edital):
    """Perfis persistidos, no formato que o formulário renderiza."""
    return [
        {
            "id": str(perfil.id),
            "code": perfil.code,
            "name": perfil.name,
            "description": perfil.description,
            "requirements": "\n".join(perfil.requirements or []),
            "immediateVacancies": perfil.immediate_vacancies,
            "reserveType": perfil.reserve_type,
            "reserveLimit": perfil.reserve_limit,
            "locality": perfil.locality,
            "duties": perfil.duties,
            "workload": perfil.workload,
            "compensation": perfil.compensation,
            # Travessia 3: sem isto a declaração gravada não voltaria à tela, e a gravação seguinte
            # a apagaria — porque `ler_perfis` leria um formulário sem ela.
            "generalCompetitionModalityId": (
                str(perfil.modalidade_ampla_concorrencia)
                if perfil.modalidade_ampla_concorrencia
                else ""
            ),
            # Travessia 3, pela mesma razão: sem isto a espécie gravada não voltaria à tela, e a
            # gravação seguinte a apagaria — `ler_perfis` leria um formulário sem ela.
            "vacancyReversion": perfil.especie_de_reversao,
            # Travessia 3 de novo, e o defeito que ela evita é o mesmo: declarada a forma e gravado
            # qualquer passo seguinte, o formulário voltaria sem ela e a gravação a apagaria — um
            # Edital publicado sem declarar como convoca, sem que ninguém tenha desfeito nada.
            "callForm": perfil.forma_de_convocacao,
            "modalidades": [
                _modalidade_para_o_formulario(m) for m in perfil.modalidades.order_by("code")
            ],
            "marcos": [_marco_para_o_formulario(m) for m in perfil.marcos.order_by("code")],
            "fatos": [_fato_para_o_formulario(f) for f in perfil.fatos.order_by("code")],
            # Travessia 3 de 4: sem isto o quadro gravado não voltaria à tela, e a gravação
            # seguinte o apagaria — porque `ler_perfis` leria um formulário sem linha nenhuma.
            "quadro": _quadro_para_o_formulario(perfil),
            # **O bloco do quadro só existe quando há repartição a pedir** (027, D-002, FR-321).
            # Sem lista reservada não há o que repartir, e desenhá-lo é o que produzia o defeito:
            # dois campos para o mesmo número, um rotulado em português corrente e o outro sem
            # explicação visível.
            "tem_lista_reservada": bool(_listas_reservadas_do_modelo(perfil)),
        }
        for perfil in edital.perfis.prefetch_related(
            "modalidades__regra_normativa",
            "marcos__criterios",
            "fatos",
            # `quadro_de_vagas`, e **não** `quadro_de_vagas__modalidade`: o rótulo da linha vem de
            # `perfil.modalidades`, e daqui só saem `modalidade_id` e a quantidade — que já estão
            # na própria linha. Descer até a Modalidade era uma consulta a mais por página, para
            # carregar objetos que nenhuma linha deste arquivo lê.
            "quadro_de_vagas",
        ).order_by("code")
    ]


def quadro_do_formulario(perfil):
    """As linhas do quadro **a partir do que está no formulário**, e não do que está no banco.

    É a metade que a reexibição depois de uma recusa precisa, e é a que faz a UX-021 valer no
    momento em que ela importa: quem acrescenta uma Modalidade e digita a quantidade dela antes de
    gravar precisa ver a linha — a Modalidade ainda não existe no banco, e derivar dali devolveria
    uma tela que perdeu o que a pessoa acabou de escrever (R-009).

    A ordem é a mesma da tela: a geral primeiro, e uma por Modalidade declarada. Quantidade não
    digitada volta **em branco**, porque em branco é o que ela era — e nunca zero.
    """
    # **A primeira ocorrência vence, e não a última.** Um envio com duas linhas para o mesmo
    # recorte é recusado pelo domínio, e a tela precisa devolver o que a pessoa digitou para que
    # ela possa corrigir. Com a última vencendo, a linha duplicada **sobrescrevia** a boa: quem
    # tinha `56` na ampla concorrência recebia de volta a quantidade da duplicata, e o número certo
    # sumia na tela que existe para mostrá-lo (025, E2E25-004).
    digitadas = {}
    for linha in perfil.get("vacancyTable") or []:
        digitadas.setdefault(str(linha.get("modalityId") or ""), linha)
    geral = digitadas.get("")
    # Pela mesma razão de `_quadro_para_o_formulario`, do outro lado: aqui o Perfil é o que veio do
    # formulário, e a lista reservada é lida dele (027, FR-317).
    derivada = not listas_reservadas(perfil)
    linhas = [
        {
            "id": (geral or {}).get("id") or str(identidade_da_linha_geral(perfil.get("id"))),
            "modalityId": "",
            "rotulo": "Ampla concorrência",
            "geral": True,
            "derivada": derivada,
            "immediateVacancies": (
                perfil.get("immediateVacancies", "")
                if derivada
                else (geral or {}).get("immediateVacancies", "")
            ),
        }
    ]
    # **A Modalidade declarada como ampla concorrência não recebe linha** (025, D-004, FR-176; 027,
    # FR-317). A quantidade dela mora na linha geral, e oferecer uma caixa própria seria oferecer um
    # campo cujo preenchimento a publicação recusa — `general_competition_modality_with_row`. Era o
    # segundo campo para o mesmo número voltando pela porta dos fundos: no Perfil que só declara a
    # ampla, a caixa aparecia inclusive fora do bloco que esta feature condicionou.
    ampla = str(perfil.get("generalCompetitionModalityId") or "")
    for modalidade in perfil.get("competitionModalities") or []:
        chave = str(modalidade.get("id") or "")
        if ampla and chave == ampla:
            continue
        digitada = digitadas.get(chave)
        nome = modalidade.get("name") or ""
        codigo = modalidade.get("code") or ""
        linhas.append(
            {
                "id": (digitada or {}).get("id") or str(uuid4()),
                "modalityId": chave,
                "rotulo": f"{nome} ({codigo})" if nome or codigo else "Modalidade sem denominação",
                "geral": False,
                "immediateVacancies": (digitada or {}).get("immediateVacancies", ""),
            }
        )
    return linhas


def _listas_reservadas_do_modelo(perfil):
    """As listas reservadas de um Perfil **do banco** (027, FR-317).

    `listas_reservadas` lê a carga; esta lê o modelo. O conceito é um só e está escrito lá — as
    Modalidades declaradas menos a que o Perfil aponta como a da ampla concorrência —, e duplicar
    a regra seria pedir que as duas divirjam na primeira mudança. O que muda é de onde vem o dado.
    """
    ampla = perfil.modalidade_ampla_concorrencia
    return {modalidade.id for modalidade in perfil.modalidades.all() if modalidade.id != ampla}


def _quadro_para_o_formulario(perfil):
    """As linhas que a tela desenha: a geral primeiro, e uma por Modalidade declarada.

    **As linhas são oferecidas, e não digitadas** (UX-021, SC-048). O rótulo de cada uma vem da
    Modalidade que já está declarada no Perfil; o que falta é a quantidade. Modalidade sem linha
    gravada aparece com o campo **vazio** — que é "não declarado", e nunca zero (FR-159).

    A identidade de uma linha ainda não gravada nasce aqui, e não no navegador: a gravação preserva
    o `id` recebido, e linha que nascesse sem identidade não teria o que preservar — é o mesmo
    argumento que a Modalidade e a Regra Normativa já registram.
    """
    gravadas = {
        str(linha.modalidade_id) if linha.modalidade_id else "": linha
        for linha in perfil.quadro_de_vagas.all()
    }
    geral = gravadas.get("")
    # **A linha geral é projeção enquanto não há lista reservada** (027, D-001, FR-318). Aí ela não
    # tem caixa: pedir o mesmo número duas vezes é o que criava a divergência que o Princípio II
    # proíbe. Ela continua viajando no formulário — identidade e quantidade em campo oculto —,
    # porque é ela que a gravação preserva e a Retificação alcança depois de publicada.
    derivada = not _listas_reservadas_do_modelo(perfil)
    linhas = [
        {
            "id": str(geral.id) if geral else str(identidade_da_linha_geral(perfil.id)),
            "modalityId": "",
            "rotulo": "Ampla concorrência",
            "geral": True,
            "derivada": derivada,
            "immediateVacancies": (
                perfil.immediate_vacancies if derivada else (geral.vagas_imediatas if geral else "")
            ),
        }
    ]
    # **A Modalidade declarada como ampla concorrência não recebe linha** (025, D-004, FR-176; 027,
    # FR-317). A quantidade dela mora na linha geral, e oferecer uma caixa própria seria oferecer um
    # campo cujo preenchimento a publicação recusa — `general_competition_modality_with_row`. Era o
    # segundo campo para o mesmo número voltando pela porta dos fundos: no Perfil que só declara a
    # ampla, a caixa aparecia inclusive fora do bloco que esta feature condicionou.
    for modalidade in perfil.modalidades.order_by("code"):
        if modalidade.id == perfil.modalidade_ampla_concorrencia:
            continue
        gravada = gravadas.get(str(modalidade.id))
        linhas.append(
            {
                "id": str(gravada.id) if gravada else str(uuid4()),
                "modalityId": str(modalidade.id),
                "rotulo": f"{modalidade.name} ({modalidade.code})",
                "geral": False,
                "immediateVacancies": gravada.vagas_imediatas if gravada else "",
            }
        )
    return linhas


def eventos_do_edital(edital):
    cronograma = getattr(edital, "cronograma", None)
    if cronograma is None:
        return []
    return [
        {
            "id": str(evento.id),
            "type": evento.type,
            "description": evento.description,
            "startAt": evento.start_at.astimezone(ZONA).strftime("%Y-%m-%dT%H:%M"),
            "endAt": evento.end_at.astimezone(ZONA).strftime("%Y-%m-%dT%H:%M")
            if evento.end_at
            else "",
            "order": evento.order,
            "location": evento.location,
            # O rótulo que a Etapa mostra ao escolher o vínculo (FR-036). A Etapa se vincula a um
            # Evento **para herdar as datas** — é o que a ajuda promete —, e a lista mostrava
            # "tipo — descrição", cortava por falta de largura e não mostrava data nenhuma: para
            # saber que datas estava herdando, era preciso voltar ao Cronograma.
            "rotulo": (
                f"{evento.type} · {evento.start_at.astimezone(ZONA).strftime('%d/%m/%Y %H:%M')}"
            ),
        }
        for evento in cronograma.eventos.order_by("order")
    ]


def perfis_persistidos(edital):
    """Perfis já salvos, no formato do command — para preservá-los ao salvar outra etapa."""
    return [
        {
            "id": str(perfil.id),
            "code": perfil.code,
            "name": perfil.name,
            "description": perfil.description,
            "requirements": perfil.requirements or [],
            "immediateVacancies": perfil.immediate_vacancies,
            "reserveType": perfil.reserve_type,
            "reserveLimit": perfil.reserve_limit,
            # **Travessia 2, e ela vale para este campo tanto quanto para o quadro**: sem esta
            # linha, declarar a ampla concorrência no passo dos Perfis e gravar qualquer etapa
            # seguinte publicaria um Edital que não a declara — e a conferência do alvo derivado
            # voltaria a exigir linha de quadro para ela (014, FR-231).
            "generalCompetitionModalityId": (
                str(perfil.modalidade_ampla_concorrencia)
                if perfil.modalidade_ampla_concorrencia
                else None
            ),
            "vacancyReversion": (
                {"kind": perfil.especie_de_reversao} if perfil.especie_de_reversao else None
            ),
            # **Travessia 2, e ela vale aqui pela mesma razão.** Sem esta linha, declarar a forma
            # no passo dos Perfis e gravar qualquer etapa seguinte publicaria um Edital que não a
            # declara — e a `019` recusaria convocar nele, sem que nada explicasse por quê.
            "callForm": perfil.forma_de_convocacao or None,
            "locality": perfil.locality,
            "duties": perfil.duties,
            "workload": perfil.workload,
            "compensation": perfil.compensation,
            # A modalidade inteira, com a Regra e os dois identificadores. Antes daqui só `code` e
            # `name` viajavam: salvar o Cronograma relia os Perfis, reenviava metade da modalidade
            # e apagava a Regra Normativa — configurar cotas e ir a outra etapa destruía o que
            # tinha sido configurado.
            "competitionModalities": [
                _modalidade_persistida(m) for m in perfil.modalidades.order_by("code")
            ],
            # Pela razão do comentário acima, e ela vale igual: sem isto, gravar o Cronograma
            # apagaria os marcos configurados no passo dos Perfis.
            "classificationMilestones": [
                _marco_persistido(m) for m in perfil.marcos.order_by("code")
            ],
            "declaredFacts": [_fato_persistido(f) for f in perfil.fatos.order_by("code")],
            # Travessia 2 de 4, e é a que mata em silêncio: `replace_draft` apaga e recria tudo, de
            # modo que o quadro que não for reenviado ao gravar **outra** etapa some sem erro
            # nenhum — quantidade publicável desaparecendo por causa de uma visita ao Cronograma.
            "vacancyTable": [_linha_persistida(linha) for linha in perfil.quadro_de_vagas.all()],
            # Pela mesma razão dos dois acima, e com um agravante: nenhuma tela do assistente os
            # desenha. Conteúdo normativo que só o contrato administrativo escreve atravessaria o
            # assistente uma vez e sumiria na primeira gravação — sem que houvesse tela onde
            # reparar a perda (E2E17-001, classe do defeito).
            "classificationInformation": perfil.classification_information,
            "callInformation": perfil.call_information,
        }
        for perfil in edital.perfis.prefetch_related(
            "modalidades__regra_normativa", "marcos__criterios", "quadro_de_vagas"
        ).order_by("code")
    ]


def _linha_persistida(linha):
    return {
        "id": str(linha.id),
        "modalityId": str(linha.modalidade_id) if linha.modalidade_id else None,
        "immediateVacancies": linha.vagas_imediatas,
    }


def _fato_para_o_formulario(fato):
    return {"id": str(fato.id), "code": fato.code, "label": fato.label, "type": fato.tipo}


def _fato_persistido(fato):
    return {"id": str(fato.id), "code": fato.code, "label": fato.label, "type": fato.tipo}


def _marco_para_o_formulario(marco):
    arredondamento = marco.arredondamento or {}
    return {
        "id": str(marco.id),
        "code": marco.code,
        "name": marco.name,
        "orderProduction": marco.forma_da_ordem,
        "etapas": [str(etapa) for etapa in marco.etapas],
        "operation": marco.operacao,
        "normalization": marco.normalizacao,
        "scale": arredondamento.get("scale", ""),
        "mode": arredondamento.get("mode", ""),
        # Os três estados voltam **como três** para a reexibição: devolver a negativa como
        # "não declarada" apagaria a norma no salvamento seguinte, sem que ninguém pedisse.
        "appealDeclaration": _declaracao_do_marco(marco.janela_recursal),
        "appealDurationDays": (marco.janela_recursal or {}).get("durationDays") or "",
        "appealUnit": (marco.janela_recursal or {}).get("unit") or "DIAS_CORRIDOS",
        **_metodo_para_exibicao(marco.metodo_de_sorteio),
        **_corte_para_exibicao(marco.regra_de_corte),
        "criterios": [
            {
                "id": str(criterio.id),
                "order": criterio.ordem,
                "type": criterio.tipo,
                # O alvo é um só, e a tela o oferece conforme o tipo — guardar `stageId` e
                # `factId` separados aqui faria a reexibição escolher qual mostrar.
                "target": (criterio.parametros or {}).get("stageId")
                or (criterio.parametros or {}).get("factId")
                or "",
                "whenMissing": criterio.quando_ausente,
            }
            for criterio in sorted(marco.criterios.all(), key=lambda item: item.ordem)
        ],
    }


def marcos_persistidos(perfil):
    """Os marcos de um Perfil gravado, no formato do contrato do rascunho, ordenados por código.

    Pública porque a duplicação (043) precisa deles fora deste módulo. Ordena em memória, e não por
    `order_by`, para aproveitar o `prefetch` de quem chama.
    """
    return [_marco_persistido(marco) for marco in sorted(perfil.marcos.all(), key=lambda m: m.code)]


def _marco_persistido(marco):
    return {
        "id": str(marco.id),
        "code": marco.code,
        "name": marco.name,
        # Travessia da forma da ordem, pela mesma razão da janela, do método e do corte abaixo: o
        # reenvio carrega **o contrato inteiro**, e não os campos que a tela da etapa atual
        # desenha. Sem esta linha, declarar a forma no passo Classificação e gravar qualquer passo
        # seguinte apagaria a declaração — e o marco voltaria a ser lido por inferência (030).
        "orderProduction": marco.forma_da_ordem,
        "stages": [str(etapa) for etapa in marco.etapas],
        "operation": marco.operacao,
        "normalization": marco.normalizacao,
        "rounding": marco.arredondamento,
        # A janela recursal, pelo mesmo motivo que `status` e `isRegistrationPeriod` viajam no
        # Evento: o reenvio precisa carregar **o contrato inteiro**, e não os campos que a tela da
        # etapa atual desenha. Sem ela, declarar "admite recurso em 5 dias" no passo Classificação
        # e gravar qualquer passo seguinte publicava um Edital que nada declara sobre recurso —
        # e todo recurso nascia sem prazo computável (E2E18-005).
        # `or None` como em `publish_edital`: `{}` é a ausência, e a ausência viaja como ausência.
        "appealWindow": marco.janela_recursal or None,
        # **E o método pelo mesmo motivo, no mesmo lugar.** São dois caminhos de perda, e fechar só
        # um deixa o defeito vivo: sem esta linha, declarar o método no passo Classificação e
        # gravar qualquer passo seguinte publicaria um Edital que não declara método nenhum — e o
        # congelamento da relação seria recusado sem que ninguém entendesse por quê.
        "drawMethod": marco.metodo_de_sorteio or None,
        # **E a regra de corte pela mesma razão, no mesmo lugar.** São três caminhos de perda, e
        # fechar dois deixa o defeito vivo: sem esta linha, declarar o corte no passo Classificação
        # e gravar qualquer passo seguinte publicaria um Edital que não corta — e a Etapa governada
        # voltaria a receber todos os habilitados sem que ninguém pedisse.
        "cutRule": marco.regra_de_corte or None,
        "tiebreakers": [
            {
                "id": str(criterio.id),
                "order": criterio.ordem,
                "type": criterio.tipo,
                "parameters": criterio.parametros,
                "whenMissing": criterio.quando_ausente,
            }
            for criterio in sorted(marco.criterios.all(), key=lambda item: item.ordem)
        ],
    }


def _modalidade_persistida(modalidade):
    regra = getattr(modalidade, "regra_normativa", None)
    persistida = {
        "id": str(modalidade.id),
        "code": modalidade.code,
        "name": modalidade.name,
        "description": modalidade.description,
    }
    if regra is not None:
        persistida["normativeRule"] = {
            "id": str(regra.id),
            "foundation": regra.foundation,
            "version": regra.version,
            "percentage": regra.percentage,
            "calculation": regra.calculation,
            "rounding": regra.rounding,
            "distribution": regra.distribution,
            "callRules": regra.call_rules,
            "effectiveFrom": regra.effective_from,
        }
    return persistida


def ler_distribuicao(dados):
    """O corpo do lote e o da remoção, na mesma porta.

    `acao` decide qual, e não a presença dos campos: um envio com `acao=remover` que carregasse
    `inscricao_id` por sobra de formulário não pode distribuir — foi assim que a 011 descobriu que
    ramo irmão decide sozinho.
    """
    acao = (_texto(dados, "acao") or "distribuir").strip()
    conhecidas = {"remover", "propor", "confirmar_rodizio"}
    return {
        "acao": acao if acao in conhecidas else "distribuir",
        "membro_ids": dados.getlist("membro_id"),
        "inscricao_ids": dados.getlist("inscricao_id"),
        "atribuicao_ids": dados.getlist("atribuicao_id"),
        # A assinatura da proposta que a pessoa leu. O comando a confere depois da trava.
        "assinatura": _texto(dados, "assinatura"),
    }


def ler_impedimento(dados):
    """Quem, sobre qual inscrição, e por quê. O motivo é o que faz do impedimento um ato."""
    return {
        "identity_subject": _texto(dados, "identity_subject"),
        "inscricao_id": _texto(dados, "inscricao_id"),
        "motivo": _texto(dados, "motivo"),
    }


def ler_reabertura(dados):
    return {
        "avaliacao_id": _texto(dados, "avaliacao_id"),
        "motivo": _texto(dados, "motivo"),
        "expected_revision": _inteiro(dados, "expected_revision", 0),
    }


def ler_avaliacao(dados):
    """Pontuação, parecer e a revisão esperada — que não é opcional.

    `expected_revision` é a precondição de FR-081: sem ela, duas abas do mesmo avaliador se
    sobrescreveriam em silêncio. Vazio vira `0`, que nunca corresponde a revisão real e produz a
    recusa por revisão obsoleta em vez de uma gravação cega.
    """
    return {
        "pontuacao": _texto(dados, "pontuacao"),
        # O instrumento da outra forma chega vazio quando a tela é a certa, e preenchido quando
        # alguém forjou o envio — e é o domínio que recusa, não a leitura (FR-122).
        "sentido": _texto(dados, "sentido"),
        "parecer": _texto(dados, "parecer"),
        "expected_revision": _inteiro(dados, "expected_revision", 0),
        "versao_reconhecida": _texto(dados, "versao_reconhecida") or None,
    }


def etapas_do_edital(edital):
    """Etapas persistidas, no formato que o formulário renderiza."""
    return [
        {
            "id": str(etapa.id),
            "name": etapa.name,
            "order": etapa.order,
            "weight": "" if etapa.weight is None else f"{etapa.weight:f}",
            "eliminatory": etapa.eliminatory,
            "classificatory": etapa.classificatory,
            "minimumScore": "" if etapa.minimum_score is None else f"{etapa.minimum_score:f}",
            "evaluationsPerRegistration": (
                ""
                if etapa.evaluations_per_registration is None
                else etapa.evaluations_per_registration
            ),
            "maximumScore": "" if etapa.maximum_score is None else f"{etapa.maximum_score:f}",
            "forma": etapa.forma,
            "rotuloFavoravel": etapa.rotulo_favoravel,
            "rotuloDesfavoravel": etapa.rotulo_desfavoravel,
            "scheduleEventId": "" if etapa.evento_id is None else str(etapa.evento_id),
        }
        for etapa in edital.etapas.order_by("order")
    ]


def etapas_persistidas(edital):
    """Etapas já salvas, no formato do command — para preservá-las ao salvar outra etapa."""
    return [
        {
            "id": str(etapa.id),
            "name": etapa.name,
            "order": etapa.order,
            "weight": etapa.weight,
            "eliminatory": etapa.eliminatory,
            "classificatory": etapa.classificatory,
            "minimumScore": etapa.minimum_score,
            "evaluationsPerRegistration": etapa.evaluations_per_registration,
            "maximumScore": etapa.maximum_score,
            "forma": etapa.forma,
            "rotuloFavoravel": etapa.rotulo_favoravel,
            "rotuloDesfavoravel": etapa.rotulo_desfavoravel,
            "scheduleEventId": None if etapa.evento_id is None else str(etapa.evento_id),
        }
        for etapa in edital.etapas.order_by("order")
    ]


def eventos_persistidos(edital):
    """Eventos já salvos, no formato do command — para preservá-los ao salvar outra etapa.

    **O contrato inteiro, e não os campos que a tela do Cronograma desenha.** `replace_draft`
    substitui o rascunho inteiro e reconstrói cada Evento a partir do que recebe: campo omitido
    aqui volta ao padrão do modelo na gravação seguinte, sem recusa e sem aviso. `status` e
    `isRegistrationPeriod` faltavam, e a marca do período — que é decisão da etapa `Inscrição` —
    morria no passo seguinte do assistente. O Edital era publicado anunciando prazo de inscrição
    que o sistema não receberia (E2E17-001).
    """
    cronograma = getattr(edital, "cronograma", None)
    if cronograma is None:
        return []
    return [
        {
            "id": str(evento.id),
            "type": evento.type,
            "description": evento.description,
            "startAt": evento.start_at,
            "endAt": evento.end_at,
            "order": evento.order,
            # **Só o cancelamento viaja** (045, `FR-737`). Um rascunho gravado pela API antes da
            # `045` pode guardar `EM_ANDAMENTO` ou `CONCLUIDO`, que o domínio passou a recusar; a
            # pessoa nunca os digitou nesta tela, e recusar a gravação por eles seria travá-la num
            # valor que a leitura nem considera mais. O rascunho não foi publicado: normalizar aqui
            # não reescreve ato nenhum.
            "status": (
                evento.status
                if evento.status == EventoCronograma.Status.CANCELADO
                else EventoCronograma.Status.PLANEJADO
            ),
            "isRegistrationPeriod": evento.is_registration_period,
            # **E o local pelo mesmo motivo.** É o terceiro campo a entrar nesta lista pela lição
            # que a E2E17-001 deixou: campo omitido aqui volta ao padrão do modelo na gravação
            # seguinte, sem recusa e sem aviso — e o Edital seria publicado sem o local que alguém
            # digitou dois passos antes (021, FR-057).
            "location": evento.location,
        }
        for evento in cronograma.eventos.order_by("order")
    ]


def ler_inscricao(dados):
    """O contrato operacional de inscrição: qual Evento é o período, e o que se exige do candidato.

    Duas coisas numa etapa só porque são uma coisa só para quem elabora — "como este Edital recebe
    inscrição" —, embora vivam em coleções diferentes do rascunho. Partir isso em duas etapas
    obrigaria a procurar metade do contrato em cada lugar.

    Vazio em `periodo` é decisão legítima: o Edital não recebe inscrições por este sistema, e a
    publicação avisa sem impedir.
    """
    documentos = []
    for indice in _indices(dados, "documento"):
        base = f"documento-{indice}"
        documentos.append(
            {
                "id": _texto(dados, f"{base}-id"),
                "key": _texto(dados, f"{base}-key"),
                "name": _texto(dados, f"{base}-name"),
                "instructions": _texto(dados, f"{base}-instructions"),
                "required": _marcado(dados, f"{base}-required"),
                "order": _inteiro(dados, f"{base}-order", 0),
                # Vazio é "não restringe", e é a ausência dos dois que faz o requisito valer para
                # todos. `None` e não `""`: o command grava chave estrangeira.
                "profileId": _texto(dados, f"{base}-profileId") or None,
                # O seletor da modalidade carrega as duas formas (044, R-009): o valor `codigo:X` é
                # a modalidade de código X em todos os Perfis; um UUID é a Modalidade de um Perfil.
                # Um seletor só é o que torna as duas exclusivas — não há como escolher ambas.
                **_modalidade_escolhida(_texto(dados, f"{base}-modalityId")),
                # A tela ainda não oferece o campo; a chave viaja vazia para que `_preservando`
                # tenha onde encaixar o que já estava gravado (020, FR-020).
                "attachmentId": _texto(dados, f"{base}-attachmentId") or None,
            }
        )
    return {
        "periodo": _texto(dados, "periodo-inscricoes"),
        "documentos": _renumerar(documentos),
        # **O Requerimento de Matrícula entra nesta etapa, e não numa nova** (029, `T-003`). É aqui
        # que quem elabora decide o que se pede ao candidato — o período e os Documentos Exigidos já
        # são compostos neste mesmo lugar, e o requerimento é a terceira face da mesma decisão.
        #
        # **Dois campos, e nem um a mais.** O Edital liga e agenda; quais campos o requerimento tem
        # é decisão de domínio, escrita em spec (`D-002`). Não há construtor de formulário aqui, e
        # a ausência é o que mantém essa recusa real.
        "requerimento_momento": _texto(dados, "requerimento-momento"),
        "requerimento_declaracao": _texto(dados, "requerimento-declaracao"),
    }


PREFIXO_DO_CODIGO = "codigo:"


def _modalidade_escolhida(valor):
    """`modalityId` e `modalityCode` a partir do valor do seletor único da modalidade."""
    if valor.startswith(PREFIXO_DO_CODIGO):
        return {"modalityId": None, "modalityCode": valor[len(PREFIXO_DO_CODIGO) :] or None}
    return {"modalityId": valor or None, "modalityCode": None}


def documentos_do_edital(edital):
    """As linhas de Documento Exigido, no formato do formulário."""
    return [
        {
            "id": str(documento.id),
            "key": documento.key,
            "name": documento.name,
            "instructions": documento.instructions,
            "required": documento.required,
            "order": documento.order,
            "profileId": "" if documento.perfil_id is None else str(documento.perfil_id),
            "modalityId": "" if documento.modalidade_id is None else str(documento.modalidade_id),
            "modalityCode": documento.modalidade_codigo,
            "attachmentId": "" if documento.anexo_id is None else str(documento.anexo_id),
        }
        for documento in edital.documentos_exigidos.order_by("order")
    ]


def anexos_do_edital(edital):
    """Os Anexos que a etapa `Inscrição` oferece como modelo (020, FR-020).

    Só os deste Edital: o vínculo é com a identidade do Anexo, e oferecer o de outro Edital seria
    oferecer uma referência que a publicação recusaria como pendurada.
    """
    return [
        {"id": str(anexo.id), "rotulo": anexo.rotulo or "sem rótulo"}
        for anexo in edital.anexos.order_by("order")
    ]


def documentos_persistidos(edital):
    """Como o command os espera — para preservá-los ao gravar outra etapa."""
    return [
        {
            "id": str(documento.id),
            "key": documento.key,
            "name": documento.name,
            "instructions": documento.instructions,
            "required": documento.required,
            "order": documento.order,
            "profileId": None if documento.perfil_id is None else str(documento.perfil_id),
            "modalityId": None if documento.modalidade_id is None else str(documento.modalidade_id),
            # Sem ele, gravar qualquer outra etapa apagaria o recorte transversal em silêncio: as
            # linhas são recriadas a cada gravação (044).
            "modalityCode": documento.modalidade_codigo or None,
            "attachmentId": None if documento.anexo_id is None else str(documento.anexo_id),
        }
        for documento in edital.documentos_exigidos.order_by("order")
    ]


def periodo_do_edital(edital):
    """O identificador do Evento marcado como período de inscrições, ou vazio."""
    cronograma = getattr(edital, "cronograma", None)
    if cronograma is None:
        return ""
    evento = cronograma.eventos.filter(is_registration_period=True).first()
    return "" if evento is None else str(evento.id)


def alcance_da_aplicabilidade(edital):
    """Perfis e modalidades a que um Documento Exigido pode se restringir.

    A modalidade carrega o Perfil a que pertence porque a tela precisa recusar a combinação
    impossível antes do servidor — e o servidor recusa de novo, que é onde a regra vale.
    """
    perfis = []
    for perfil in edital.perfis.order_by("code"):
        perfis.append(
            {
                "id": str(perfil.id),
                "rotulo": f"{perfil.code} — {perfil.name}",
                "modalidades": [
                    {
                        "id": str(modalidade.id),
                        "rotulo": f"{modalidade.code} — {modalidade.name}",
                    }
                    for modalidade in perfil.modalidades.order_by("code")
                ],
            }
        )
    return perfis


def modalidades_em_todos_os_perfis(edital):
    """As opções do recorte transversal: uma por código do Edital, fora a ampla (044, UX-080).

    O rótulo diz o alcance — *"Pessoas com Deficiência (PcD) — em todos os Perfis que a têm (16 de
    16)"* —, porque "em todos os Perfis" num Edital em que só três têm a modalidade prometeria mais
    do que o documento faz. **O código declarado ampla em qualquer Perfil não aparece** (FR-704): a
    ampla concorrência é a linha geral, e não recorta documento. A denominação é a do primeiro
    Perfil que tem o código; se houver duas, a publicação as acusa (FR-706).
    """
    perfis = list(edital.perfis.prefetch_related("modalidades").order_by("code"))
    total = len(perfis)
    por_codigo = {}
    amplas = set()
    for perfil in perfis:
        for modalidade in perfil.modalidades.all():
            codigo = (modalidade.code or "").strip()
            if not codigo:
                continue
            if perfil.modalidade_ampla_concorrencia and str(
                perfil.modalidade_ampla_concorrencia
            ) == str(modalidade.id):
                amplas.add(codigo)
            item = por_codigo.setdefault(codigo, {"denominacao": modalidade.name, "perfis": 0})
            item["perfis"] += 1
    return [
        {
            "valor": f"{PREFIXO_DO_CODIGO}{codigo}",
            "codigo": codigo,
            "rotulo": (
                f"{item['denominacao'] or codigo} ({codigo}) — em todos os Perfis que a têm "
                f"({item['perfis']} de {total})"
            ),
        }
        for codigo, item in sorted(por_codigo.items())
        if codigo not in amplas
    ]


# ---------------------------------------------------------------------------
# A comissão e a alocação (011). Leitura, e nada além: quem decide se a pessoa existe, se pode
# ser alocada e se a Etapa é vigente é o command.
# ---------------------------------------------------------------------------


def ler_membro(dados):
    """Identificador, rótulo e função. O rótulo é leitura humana e não identifica ninguém."""
    return {
        "identity_subject": _texto(dados, "identity_subject"),
        "display_label": _texto(dados, "display_label"),
        # Sem padrão: "não informado" e "informado como MEMBRO" são coisas diferentes, e
        # confundi-las rebaixaria uma presidente em silêncio num formulário truncado. Quem
        # valida é o command, que recusa função fora do conjunto.
        "funcao": _texto(dados, "funcao"),
    }


def ler_alocacao(dados):
    return {
        "membro_id": _texto(dados, "membro_id"),
        "edital_id": _texto(dados, "edital_id"),
        "etapa_id": _texto(dados, "etapa_id"),
    }


def ler_membros_em_lote(dados):
    """Uma pessoa por linha: `identificador` ou `identificador, Nome de exibição`.

    Colar a lista é como a informação chega de verdade — de uma portaria, de uma planilha, de um
    e-mail. Exigir um formulário por pessoa era transformar quarenta linhas em oitenta envios.
    """
    bruto = dados.get("lista") or ""
    entradas = []
    for linha in bruto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        identificador, separador, rotulo = linha.partition(",")
        if not separador:
            identificador, separador, rotulo = linha.partition(";")
        entradas.append((identificador.strip(), rotulo.strip()))
    return {"entradas": entradas, "funcao": _texto(dados, "funcao"), "lista": bruto}


def ultimo_local_declarado(edital):
    """O local do último Evento que declarou um — a sugestão que a tela oferece (021, FR-059).

    **Sugestão, e não preenchimento.** Ela chega ao template como `placeholder`: o campo continua
    vazio, e vazio continua significando "não declarado". Um `value` aqui aplicaria ao Edital um
    local que ninguém escreveu, que é a degradação que os rótulos da Etapa e o default institucional
    do Evento já recusaram (FR-058).
    """
    cronograma = getattr(edital, "cronograma", None)
    if cronograma is None:
        return ""
    for evento in cronograma.eventos.order_by("-order"):
        if evento.location:
            return evento.location
    return ""
