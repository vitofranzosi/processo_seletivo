"""Snapshot normativo com coleções aninhadas, para os testes de endereçamento por chave.

`complete_draft` basta para publicar, mas tem um Perfil só, sem Modalidades e sem Requisitos —
não alcança nada do que esta feature decide. Aqui o conteúdo tem três Perfis, Modalidades dentro
de Perfil, `requirements` (a coleção sem identificador) e dois Eventos, que é o mínimo para
distinguir resolver por chave de resolver por posição.

Os identificadores são fixos e legíveis: um teste que falha aponta para `…0501` e não para um
UUID aleatório que não diz de quem o ato falava.
"""

import hashlib
from uuid import NAMESPACE_URL, uuid5

from tests.fixtures.edital import identidade_do_marco, marco_minimo

PERFIL = {
    "A": "00000000-0000-0000-0000-000000000501",
    "B": "00000000-0000-0000-0000-000000000502",
    "C": "00000000-0000-0000-0000-000000000503",
}
EVENTO = {
    "A": "00000000-0000-0000-0000-000000000521",
    "B": "00000000-0000-0000-0000-000000000522",
}
ANEXO = {
    "A": "00000000-0000-0000-0000-000000000531",
    "B": "00000000-0000-0000-0000-000000000532",
}
ARTEFATO = {
    "A": "00000000-0000-0000-0000-000000000541",
    "B": "00000000-0000-0000-0000-000000000542",
}
FATO = {
    "NASCIMENTO": "00000000-0000-0000-0000-000000000531",
    "EXPERIENCIA": "00000000-0000-0000-0000-000000000532",
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
# As identidades que o Edital máximo acrescenta (026, T001).
MARCO = "00000000-0000-0000-0000-000000000591"
CRITERIO = {
    "ETAPA": "00000000-0000-0000-0000-000000000592",
    "FATO": "00000000-0000-0000-0000-000000000593",
}
LINHA = {
    "GERAL": "00000000-0000-0000-0000-000000000594",
    "PPI": "00000000-0000-0000-0000-000000000595",
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


def fato(identificador, sigla, rotulo, tipo):
    """Um fato declarado pelo Edital (D-2), na forma **publicada**."""
    return {"id": identificador, "code": sigla, "label": rotulo, "type": tipo}


# O quadro que o construtor monta quando ninguém diz qual é (027, FR-318). **Não é conveniência de
# teste**: é a forma que todo Perfil gravado por `replace_draft` passou a ter, e um construtor que
# produzisse Perfil sem linha geral estaria produzindo conteúdo que a publicação recusa.
#
# Quem precisa da forma do **acervo** — publicado antes de a capacidade existir — passa `quadro=()`
# e recebe a lista vazia, que é a grafia da ausência (025, D-005).
DERIVADA = object()


def perfil(identificador, sigla, nome, *, modalidades=(), requisitos=(), fatos=(), quadro=DERIVADA):
    vagas = 1
    if quadro is DERIVADA:
        quadro = [
            {
                "id": str(uuid5(NAMESPACE_URL, f"quadro-geral:{identificador}")),
                "modalityId": None,
                "immediateVacancies": vagas,
            }
        ]
    return {
        "id": identificador,
        "code": sigla,
        "name": nome,
        "description": f"Perfil {sigla}",
        "requirements": list(requisitos),
        "immediateVacancies": vagas,
        "reserveType": "NONE",
        "reserveLimit": None,
        "locality": "Vitória",
        "duties": "Ministrar aulas e participar das atividades do campus.",
        "workload": "20 horas semanais",
        "compensation": "R$ 4.200,00 mensais",
        "classificationInformation": {},
        "callInformation": {},
        "competitionModalities": list(modalidades),
        # As duas da versão 7. `classificationMilestones` fica vazia enquanto a elaboração do marco
        # não existir; a chave, porém, é obrigatória — no conteúdo publicado não há campo opcional,
        # e a versão canônica identifica **uma** grafia.
        "declaredFacts": list(fatos),
        # **O marco deixou de poder faltar** (032, FR-457): um Perfil sem marco não classifica
        # ninguém, e desde a `032` a publicação recusa. A identidade é derivada da do Perfil pelo
        # mesmo `uuid5` que a linha geral do quadro usa — o construtor precisa ser reproduzível
        # sem ler o conteúdo publicado, e um identificador literal colidiria entre os três Perfis.
        "classificationMilestones": [
            marco_minimo(identidade_do_marco(identificador), codigo=f"{sigla}-M")
        ],
        # A da versão 12. Vazia significa "este Edital não publicou quadro" — o que todo Edital do
        # acervo afirma —, e nunca "zero vaga" (025, D-005). O construtor a preenche por padrão
        # porque desde a `027` a linha geral é materializada na gravação; `quadro=()` devolve a
        # forma do acervo.
        "vacancyTable": list(quadro),
        # A da versão 13, pela mesma razão: `None` significa "este Perfil não declarou qual das suas
        # Modalidades é a ampla concorrência", que é o que todo Edital publicado antes do degrau
        # afirma — e nunca "não há ampla concorrência" (014, D-014, FR-231).
        "generalCompetitionModalityId": None,
        # A da versão 14, pela mesma razão: `None` significa "este Edital não declara reversão de
        # vaga reservada" — que é o que todo Edital publicado antes do degrau afirma —, e nunca
        # "reverte do jeito comum" (016, D-007, FR-245).
        "vacancyReversion": None,
        # A da versão 15, pela mesma razão: `None` significa "este Edital não declarou como comunica
        # a convocação" — que é o que todo Edital publicado antes do degrau afirma —, e nunca
        # "convoca por publicação" (019, D-009, FR-287).
        "callForm": None,
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
        # Onde o Evento acontece (021, D-008; declarado na forma publicada pela 026). String sempre
        # presente, `""` quando não declarado — nunca `null`, nunca chave omitida.
        "location": "",
        # A forma publicada exige o campo em todo Evento; a marca em si é de um só, e os testes
        # que falam dela a ligam explicitamente.
        "isRegistrationPeriod": False,
    }


def anexo(identificador, rotulo, ordem, artefato):
    """Um Anexo na forma publicada. O resumo é derivado do artefato, para ser estável e legível."""
    return {
        "id": identificador,
        "label": rotulo,
        "order": ordem,
        "artifactId": artefato,
        "artifactHash": hashlib.sha256(artefato.encode("utf-8")).hexdigest(),
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
            perfil(
                PERFIL["B"],
                "P2",
                "Perfil B",
                requisitos=["Diploma"],
                fatos=[
                    fato(FATO["NASCIMENTO"], "NASCIMENTO", "Data de nascimento", "DATA"),
                    fato(FATO["EXPERIENCIA"], "EXPERIENCIA", "Meses de experiência", "INTEIRO"),
                ],
            ),
            perfil(PERFIL["C"], "P3", "Perfil C"),
        ],
        "schedule": [
            evento(EVENTO["A"], "INSCRICAO", 1, "2026-09-01T12:00:00+00:00"),
            evento(EVENTO["B"], "PROVA", 2, "2026-10-01T12:00:00+00:00"),
        ],
        # Dois Anexos, e não um: com um só, resolver por chave e resolver por posição dariam o
        # mesmo resultado, que é justamente o que este conteúdo existe para distinguir (020).
        #
        # Os dois apontam artefatos distintos porque é o caso normal; o caso de artefato repetido
        # é legítimo e tem teste próprio, já que o resumo não é chave de unicidade (FR-011).
        "attachments": [
            anexo(ANEXO["A"], "ANEXO I — REQUERIMENTO DE INSCRIÇÃO", 1, ARTEFATO["A"]),
            anexo(ANEXO["B"], "ANEXO II — AUTODECLARAÇÃO ÉTNICO-RACIAL", 2, ARTEFATO["B"]),
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
        # O rascunho ainda não declara as duas coleções da versão 7: a elaboração do fato e a do
        # marco são da `US2` e da `US1`, e o serializer do rascunho recusa campo desconhecido. O
        # conteúdo **publicado** as tem porque a emissão as deriva dos modelos; o rascunho, não.
        perfil_.pop("declaredFacts", None)
        # O quadro é opcional no rascunho e obrigatório no publicado — a assimetria é a D-005 no
        # contrato: depois do degrau 12 todo conteúdo publicado tem a chave, vazia nos anteriores.
        perfil_.pop("vacancyTable", None)
        # Pela mesma assimetria: opcional no rascunho, presente no publicado (014, FR-231).
        perfil_.pop("generalCompetitionModalityId", None)
        perfil_.pop("vacancyReversion", None)
        perfil_.pop("callForm", None)
        # **Mas a ampla concorrência é declarada** (027, FR-317). Quem compõe um Perfil com uma
        # Modalidade chamada "AC" e não diz que ela é a da ampla publica um Edital cujo total não
        # governa recorte nenhum — o sistema não a reconhece pelo nome, e a `025` recusou por
        # escrito identificá-la assim. Declarada, a linha geral é materializada na gravação; não
        # declarada, a publicação recusa, que é a `FR-323` fazendo o seu trabalho. Este construtor
        # é o do Edital que **publica**, e por isso declara.
        ampla = next(
            (m["id"] for m in perfil_["competitionModalities"] if m.get("code") == "AC"), None
        )
        if ampla:
            perfil_["generalCompetitionModalityId"] = ampla
        # **E o Perfil com lista reservada declara a repartição**, porque ali ela não é derivada:
        # derivar escreveria, na ampla concorrência, um número que o Edital não repartiu. A linha
        # geral leva o total e cada reservada leva zero — quadro completo que fecha, que é o que um
        # Perfil com cota precisa ter para publicar.
        reservadas = [
            m["id"] for m in perfil_["competitionModalities"] if m["id"] != ampla and m.get("id")
        ]
        if reservadas:
            perfil_["vacancyTable"] = [
                {
                    "id": str(uuid5(NAMESPACE_URL, f"quadro-geral:{perfil_['id']}")),
                    "modalityId": None,
                    "immediateVacancies": perfil_["immediateVacancies"],
                },
                *(
                    {
                        "id": str(uuid5(NAMESPACE_URL, f"quadro-{identidade}")),
                        "modalityId": identidade,
                        "immediateVacancies": 0,
                    }
                    for identidade in reservadas
                ),
            ]
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
            # **Com peso**: quem enumera a Etapa num marco declara o peso dela, porque ausência não
            # é equivalência e o cálculo não a interpreta (015). O Edital máximo enumera as duas.
            "weight": "1.0000",
            "eliminatory": False,
            "classificatory": True,
        },
    ]
    return base


def _marco_completo():
    """Um marco classificatório com **todos** os seus objetos declarados (026, T001).

    Cada objeto aqui existe porque a travessia do contrato de mutabilidade precisa encontrá-lo:
    `rounding` e `parameters` porque a `026` decidiu que eles **não** são opacos e a travessia
    desce neles; `appealWindow`, `drawMethod` e `cutRule` porque são dez, três e seis campos que
    nenhum outro construtor materializa. Os dois critérios de desempate são de espécies diferentes
    de propósito: um consome Etapa e o outro consome fato declarado, e são as duas chaves de
    `parameters` que o contrato classifica separadamente.
    """
    return {
        "id": MARCO,
        "code": "FINAL",
        "name": "Classificação final",
        # A forma da ordem declarada (030, FR-413). **`POR_SORTEIO` e não `POR_PONTUACAO`**: este
        # marco declara o método do sorteio inteiro, e um marco de pontuação não publica método —
        # a fronteira de FR-418 o descartaria, e os dez campos do método sumiriam da travessia do
        # contrato de mutabilidade.
        "orderProduction": "POR_SORTEIO",
        "stages": [ETAPA["A"], ETAPA["B"]],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "appealWindow": {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"},
        "drawMethod": {
            "algorithm": "IFES-SORTEIO-SHA256-v1",
            # A fonte de demonstração, e não a Loteria Federal: o teste não tem rede, e a fonte
            # declarada é o que determina o adaptador consultado (021, FR-076).
            "source": "Fonte de demonstração",
            "occurrence": "5901",
            "occurrenceAt": "2020-01-01T20:00:00-03:00",
            "derivation": "A extração de sábado imediatamente anterior à data publicada.",
            "normalization": {
                "rule": "DIGITOS_EM_SEQUENCIA",
                "text": "Os cinco números sorteados, na ordem dos prêmios.",
            },
            "substitutionRule": {
                "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
                "text": "Não havendo extração na data prevista, vale a seguinte da mesma fonte.",
            },
            # Declarada, e não `None`: é o décimo campo do método, e o guarda precisa encontrá-lo
            # com valor. Precisa ser uma das Etapas que o próprio marco enumera.
            "qualifyingStageId": ETAPA["A"],
        },
        # Alvo **fixo**, e não derivado do quadro: o alvo derivado impõe coerência com as linhas de
        # cada recorte, e o que este conteúdo precisa é materializar os seis campos da regra.
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 3,
            "surplusCount": 1,
            "tieOutcome": "ADMITS_SURPLUS",
            "governedStage": "NONE",
            "continuation": "ALLOWED",
        },
        "tiebreakers": [
            {
                "id": CRITERIO["ETAPA"],
                "order": 1,
                "type": "MAIOR_PONTUACAO_NA_ETAPA",
                "parameters": {"stageId": ETAPA["A"]},
                "whenMissing": "ULTIMO_NO_CRITERIO",
            },
            {
                "id": CRITERIO["FATO"],
                "order": 2,
                "type": "MAIOR_VALOR_DE_FATO",
                "parameters": {"factId": FATO["EXPERIENCIA"]},
                "whenMissing": "CRITERIO_NAO_SE_APLICA",
            },
        ],
    }


#: O método do sorteio comum ao Edital (030, FR-429). **Nove campos, e não dez**: a Etapa que
#: habilita a participar do sorteio é do marco, porque depende de quais Etapas aquele marco
#: enumera — um valor comum a todos endereçaria Etapa que parte deles não mede.
METODO_COMUM = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Fonte de demonstração",
    "occurrence": "5902",
    "occurrenceAt": "2020-01-08T20:00:00-03:00",
    "derivation": "A extração de sábado imediatamente anterior à data publicada.",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "Os cinco números sorteados, na ordem dos prêmios.",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "Não havendo extração na data prevista, vale a seguinte da mesma fonte.",
    },
}


def rascunho_completo():
    """O rascunho **máximo**: toda coleção presente, e todo objeto opcional declarado.

    Existe para o guarda de cobertura: uma coleção declarada mas ausente do conteúdo publicado
    passaria despercebida, porque o guarda só enxerga o que o snapshot materializa. Os demais
    construtores continuam mínimos de propósito — um teste que não fala de documento exigido não
    deve passar a publicar um só porque a coleção nasceu.

    **Por que ele precisa ser máximo, e não só completo** (026, D-012). O contrato de mutabilidade
    enumera os campos publicados percorrendo o conteúdo canônico deste Edital. Enumerar sobre um
    Edital pobre produz guardião **silenciosamente incompleto** — que é o mesmo defeito que a
    feature existe para fechar, um nível acima. Antes da `026` este construtor trazia
    `classificationMilestones: []`, `vacancyReversion: None` e `callForm: None`, e uma travessia
    sobre ele não encontraria **nenhum** dos dez campos do método do sorteio.

    Simplificar qualquer coisa aqui encolhe a garantia do guardião sem que nada acuse — e é por
    isso que existe um teste medindo a cobertura desta fixture (SC-103).

    Os dois requisitos cobrem duas das quatro aplicabilidades: um para todos, um restrito a Perfil.
    """
    base = rascunho_com_etapas()
    # O método comum do Edital, que o guardião do contrato precisa encontrar preenchido: as nove
    # entradas `(RAIZ, "drawMethod/…")` só são alcançadas pela travessia se o Edital máximo as
    # publicar. O marco continua declarando o **próprio** método — é a divergência da FR-430, e é
    # ela que mantém as dez entradas do marco vivas.
    base["drawMethod"] = METODO_COMUM
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
    # O Evento ganha local: `location` é emitido no conteúdo publicado e, até a `026`, não era
    # declarado em `EVENTO_PUBLICADO` — nenhum teste acusava, porque o guarda confere coleções e
    # não campos. É o canário 1 da feature (FR-305).
    base["schedule"][1]["location"] = "Campus Serra — Auditório"
    for perfil_ in base["profiles"]:
        # Sempre presentes no conteúdo publicado desde os degraus 13 a 15; declarados aqui com
        # **valor**, e não com a grafia da ausência, porque o que a travessia não encontra não é
        # classificado.
        perfil_["callForm"] = "PUBLICATION"
        perfil_["classificationInformation"] = {"criterio": "A ordem sai da soma ponderada."}
        perfil_["callInformation"] = {"forma": "A convocação segue a ordem publicada."}
    principal = base["profiles"][0]
    # **Só no Perfil principal**, e a restrição é do domínio: quem declara reversão precisa publicar
    # quadro, porque sem quantidade por recorte não há o que reverter (016). Um Perfil declarando é
    # o bastante — a travessia toma a união das chaves dos itens da coleção.
    principal["vacancyReversion"] = {"kind": "ON_EXHAUSTION"}
    # Os fatos que os critérios de desempate consomem, e o marco que os declara.
    principal["declaredFacts"] = [
        fato(FATO["NASCIMENTO"], "NASCIMENTO", "Data de nascimento", "DATA"),
        fato(FATO["EXPERIENCIA"], "EXPERIENCIA", "Meses de experiência", "INTEIRO"),
    ]
    principal["classificationMilestones"] = [_marco_completo()]
    # A Modalidade `AC` é a ampla concorrência declarada, e por isso **não** recebe linha própria:
    # a quantidade dela é a da linha geral (025, FR-231).
    principal["generalCompetitionModalityId"] = MODALIDADE["A"]
    principal["vacancyTable"] = [
        {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 1},
        {"id": LINHA["PPI"], "modalityId": MODALIDADE["B"], "immediateVacancies": 0},
    ]
    # A Regra Normativa inteira: os quatro objetos de forma livre precisam vir com conteúdo, ou a
    # travessia não os encontra — e o contrato os classifica como opacos justamente por eles não
    # terem forma declarada (026).
    # **Em todas as Modalidades do Perfil**, e não só numa: a travessia acha o campo pela união
    # das chaves dos itens, mas a *tela* desenha um grupo por Modalidade — e um grupo com o campo
    # vazio esconderia que ele chega ao formulário.
    for modalidade_ in principal["competitionModalities"]:
        regra = modalidade_["normativeRule"]
        regra["calculation"] = {"formula": "percentual sobre as vagas imediatas"}
        regra["rounding"] = {"modo": "PARA_CIMA"}
        regra["distribution"] = {"criterio": "alternância entre as listas"}
        regra["callRules"] = {"observacao": "a convocação alterna entre ampla e reserva"}
        regra["effectiveFrom"] = "2014-06-09T00:00:00+00:00"
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
