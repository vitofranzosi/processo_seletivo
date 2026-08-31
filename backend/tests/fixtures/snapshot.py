"""Snapshot normativo com coleções aninhadas, para os testes de endereçamento por chave.

`complete_draft` basta para publicar, mas tem um Perfil só, sem Modalidades e sem Requisitos —
não alcança nada do que esta feature decide. Aqui o conteúdo tem três Perfis, Modalidades dentro
de Perfil, `requirements` (a coleção sem identificador) e dois Eventos, que é o mínimo para
distinguir resolver por chave de resolver por posição.

Os identificadores são fixos e legíveis: um teste que falha aponta para `…0501` e não para um
UUID aleatório que não diz de quem o ato falava.
"""

PERFIL = {
    "A": "00000000-0000-0000-0000-000000000501",
    "B": "00000000-0000-0000-0000-000000000502",
    "C": "00000000-0000-0000-0000-000000000503",
}
EVENTO = {
    "A": "00000000-0000-0000-0000-000000000521",
    "B": "00000000-0000-0000-0000-000000000522",
}
MODALIDADE = {
    "A": "00000000-0000-0000-0000-000000000541",
    "B": "00000000-0000-0000-0000-000000000542",
}
ETAPA = {
    "A": "00000000-0000-0000-0000-000000000561",
    "B": "00000000-0000-0000-0000-000000000562",
}
DOCUMENTO = {
    "A": "00000000-0000-0000-0000-000000000581",
    "B": "00000000-0000-0000-0000-000000000582",
}
# A Regra Normativa de cada modalidade, por identificador da modalidade.
REGRA = {
    MODALIDADE["A"]: "00000000-0000-0000-0000-000000000551",
    MODALIDADE["B"]: "00000000-0000-0000-0000-000000000552",
}


def modalidade(identificador, sigla, percentual):
    """Modalidade na forma que `edital_snapshot` produz.

    `normativeRule` tem `id` e **não** é item de lista: continua endereçada pelo nome da chave.
    É o caso que FR-005 distingue.

    O identificador da Regra vem de `REGRA`, e não de aritmética sobre o da modalidade. A versão
    anterior o derivava com `f"{identificador[:-1]}9"`, que produzia o **mesmo** valor para as duas
    modalidades — inofensivo enquanto o command descartava o `id` recebido, e uma violação de
    chave primária no instante em que ele passou a preservá-lo.
    """
    return {
        "id": identificador,
        "code": sigla,
        "name": f"Modalidade {sigla}",
        "description": f"Modalidade {sigla}",
        "normativeRule": {
            "id": REGRA[identificador],
            "foundation": "Lei 12.711/2012",
            "version": "1",
            "percentage": str(percentual),
            "calculation": {},
            "rounding": {},
            "distribution": {},
            "callRules": {},
            "effectiveFrom": None,
        },
    }


def perfil(identificador, sigla, nome, *, modalidades=(), requisitos=()):
    return {
        "id": identificador,
        "code": sigla,
        "name": nome,
        "description": f"Perfil {sigla}",
        "requirements": list(requisitos),
        "immediateVacancies": 1,
        "reserveType": "NONE",
        "reserveLimit": None,
        "locality": "Vitória",
        "duties": "Ministrar aulas e participar das atividades do campus.",
        "workload": "20 horas semanais",
        "compensation": "R$ 4.200,00 mensais",
        "classificationInformation": {},
        "callInformation": {},
        "competitionModalities": list(modalidades),
    }


def evento(identificador, tipo, ordem, inicio):
    return {
        "id": identificador,
        "type": tipo,
        "description": f"Evento {tipo}",
        "startAt": inicio,
        "endAt": None,
        "order": ordem,
        "status": "PLANEJADO",
        # A forma publicada exige o campo em todo Evento; a marca em si é de um só, e os testes
        # que falam dela a ligam explicitamente.
        "isRegistrationPeriod": False,
    }


def conteudo_normativo():
    """Conteúdo canônico com as quatro situações de endereçamento que a feature decide."""
    return {
        "title": "Edital de teste",
        "description": "Conteúdo para os testes de endereçamento",
        "profiles": [
            perfil(
                PERFIL["A"],
                "P1",
                "Perfil A",
                modalidades=[
                    modalidade(MODALIDADE["A"], "AC", 100),
                    modalidade(MODALIDADE["B"], "PPI", 20),
                ],
                requisitos=["Diploma", "Registro profissional"],
            ),
            perfil(PERFIL["B"], "P2", "Perfil B", requisitos=["Diploma"]),
            perfil(PERFIL["C"], "P3", "Perfil C"),
        ],
        "schedule": [
            evento(EVENTO["A"], "INSCRICAO", 1, "2026-09-01T12:00:00+00:00"),
            evento(EVENTO["B"], "PROVA", 2, "2026-10-01T12:00:00+00:00"),
        ],
    }


def rascunho_publicavel():
    """O mesmo conteúdo, na forma que o endpoint de rascunho aceita.

    O rascunho carrega `profiles` e `schedule`; título e descrição vêm do Processo. Manter um
    construtor só evita que os testes de domínio e os de ponta a ponta divirjam no conteúdo.

    **Os identificadores das modalidades e das Regras viajam desde a `006`.** Antes dela o rascunho
    não os declarava porque o command os ignorava: a modalidade nascia com um identificador do
    servidor e trocava de identidade a cada gravação, de modo que os testes que precisavam dela
    tinham de lê-la do conteúdo já publicado. Com a identidade preservada, o conteúdo declarado e o
    publicado passam a coincidir — que é o que torna o caminho de Retificação verificável a partir
    daqui.
    """
    base = conteudo_normativo()
    for perfil_ in base["profiles"]:
        for modalidade_ in perfil_["competitionModalities"]:
            modalidade_["normativeRule"] = {
                chave: valor
                for chave, valor in modalidade_["normativeRule"].items()
                if valor not in ({}, None)
            }
    return {"profiles": base["profiles"], "schedule": base["schedule"]}


def rascunho_com_etapas():
    """O mesmo rascunho, com duas Etapas — uma vinculada a Evento e outra não.

    Fica separado de `rascunho_publicavel` de propósito: os testes que não falam de Etapas não
    devem passar a publicá-las só porque a coleção passou a existir, e os que falam precisam de
    um conteúdo em que o vínculo com Evento seja verificável.
    """
    base = rascunho_publicavel()
    base["stages"] = [
        {
            "id": ETAPA["A"],
            "name": "Prova didática",
            "order": 1,
            "weight": "2.0000",
            "eliminatory": True,
            "classificatory": True,
            "minimumScore": "7.0000",
            "scheduleEventId": EVENTO["B"],
        },
        {
            "id": ETAPA["B"],
            "name": "Análise de títulos",
            "order": 2,
            "eliminatory": False,
            "classificatory": True,
        },
    ]
    return base


def rascunho_completo():
    """O rascunho em que **toda** coleção-raiz de entidades está presente e não vazia.

    Existe para o guarda de cobertura: uma coleção declarada mas ausente do conteúdo publicado
    passaria despercebida, porque o guarda só enxerga o que o snapshot materializa. Os demais
    construtores continuam mínimos de propósito — um teste que não fala de documento exigido não
    deve passar a publicar um só porque a coleção nasceu.

    Os dois requisitos cobrem duas das quatro aplicabilidades: um para todos, um restrito a Perfil.
    """
    base = rascunho_com_etapas()
    base["documentRequirements"] = [
        {
            "id": DOCUMENTO["A"],
            "key": "identificacao",
            "name": "Documento de identificação",
            "instructions": "Frente e verso, em arquivo único.",
            "required": True,
            "order": 1,
        },
        {
            "id": DOCUMENTO["B"],
            "key": "diploma",
            "name": "Diploma de graduação",
            "required": True,
            "order": 2,
            "profileId": PERFIL["A"],
        },
    ]
    return base


def colecoes_nao_declaradas(conteudo):
    """Listas presentes em `conteudo` que a declaração do domínio não cobre.

    É o guarda de FR-012, compartilhado entre o teste de unidade — que roda contra este
    construtor — e o de integração, que roda contra um snapshot efetivamente publicado. Uma
    coleção nova que nasça sem identificador aparece aqui, em vez de passar em silêncio e tornar
    falso o pressuposto de que `requirements` é a única coleção atômica.
    """
    from processo_seletivo.publicacoes.domain import colecoes

    achadas = []

    def percorrer(valor, forma):
        if isinstance(valor, dict):
            for chave, sub in valor.items():
                percorrer(sub, f"{forma}/{colecoes.escapar(chave)}")
        elif isinstance(valor, list):
            if not colecoes.tem_chave(forma) and not colecoes.e_atomica(forma):
                achadas.append(forma)
            for item in valor:
                percorrer(item, f"{forma}/{colecoes.CURINGA}")

    percorrer(conteudo, "")
    return sorted(set(achadas))


def elementos_sem_chave(conteudo):
    """Elementos de coleção declarada com chave que não carregam identificador."""
    from processo_seletivo.publicacoes.domain import colecoes

    sem = []
    for forma, lista in colecoes.colecoes_com_chave(conteudo):
        sem.extend(
            forma
            for elemento in lista
            if not isinstance(elemento, dict) or not elemento.get(colecoes.CAMPO_CHAVE)
        )
    return sorted(set(sem))


# Uma variante por violação da forma publicada, para que os testes das duas histórias falem da
# mesma coisa. Cada entrada é (rótulo, campo, valor) e produz um Perfil malformado de um jeito só.
VIOLACOES_DE_PERFIL = (
    ("campo ausente", "name", ...),
    ("tipo diferente", "name", []),
    ("nulo indevido", "locality", None),
    ("formato inválido", "id", "não-é-uuid"),
    ("fora da restrição", "immediateVacancies", -3),
)

VIOLACOES_DE_EVENTO = (
    ("campo ausente", "description", ...),
    ("tipo diferente", "order", "primeiro"),
    ("nulo indevido", "startAt", None),
    ("formato inválido", "startAt", "ontem"),
    ("fora da restrição", "order", -1),
)

AUSENTE = ...


def com_violacao(conteudo, colecao, posicao, campo, valor):
    """`conteudo` com um único campo de uma única entidade violado.

    `AUSENTE` como valor apaga o campo; qualquer outro o substitui. Um defeito por vez é o que
    permite afirmar qual achado corresponde a qual violação.
    """
    entidade = conteudo[colecao][posicao]
    if valor is AUSENTE:
        entidade.pop(campo, None)
    else:
        entidade[campo] = valor
    return conteudo


def perfil_mutilado(identificador):
    """O Perfil reduzido ao que os esquemas de **entrada** exigem — cinco dos doze campos.

    É o `REPLACE` parcial que a spec cita: cada campo isolado é plausível, e o conjunto não é um
    Perfil. Era o que passava antes desta feature.
    """
    return {
        "id": identificador,
        "code": "MUTILADO",
        "name": "Perfil sem o resto",
        "immediateVacancies": 1,
        "reserveType": "NONE",
    }
