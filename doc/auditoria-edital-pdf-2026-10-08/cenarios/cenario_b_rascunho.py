"""CENÁRIO B — estresse: cadastro de reserva de tutores UAB em 16 polos (forma do 90/2026).

Dados fictícios. Nenhum dado pessoal real. Banco isolado ps_auditoria_pdf_b.
"""

import sys

sys.path.insert(0, "/private/tmp/claude-501/-Users-saymoncastro-Projetos-processo-seletivo--claude-worktrees-auditoria-edital-pdf-d33731/fba18c90-9168-4aeb-8300-d572628e7dd7/scratchpad")
from comum import anexos, autoridade, criar, elaborar, previa, publicar, teto, uid  # noqa: E402

P = "B"
POLOS = [
    "Afonso Cláudio", "Alegre", "Aracruz", "Baixo Guandu", "Bom Jesus do Norte",
    "Cachoeiro de Itapemirim", "Domingos Martins", "Ecoporanga", "Itapemirim", "Iúna",
    "Linhares", "Mantenópolis", "Montanha", "Nova Venécia", "Pinheiros", "Santa Leopoldina",
]
ETAPA_DOC, ETAPA_TIT = uid(P, "etapa-doc"), uid(P, "etapa-titulos")

ATRIBUICOES_TP = (
    "● Mediar a comunicação de conteúdos entre o professor formador e os estudantes, no polo de apoio presencial.\n"
    "● Acompanhar as atividades discentes, conforme o cronograma do curso, e apoiar o professor formador nas atividades presenciais.\n"
    "● Manter regularidade de acesso ao Ambiente Virtual de Aprendizagem e responder às solicitações dos estudantes no prazo máximo de 24 horas.\n"
    "● Participar das atividades de capacitação e atualização promovidas pela instituição de ensino.\n"
    "● Elaborar relatórios mensais de acompanhamento dos estudantes e encaminhá-los à coordenação de tutoria."
)
ATRIBUICOES_TD = (
    "● Mediar, a distância, a comunicação de conteúdos entre o professor formador e os estudantes.\n"
    "● Corrigir atividades avaliativas no Ambiente Virtual de Aprendizagem, segundo as orientações do professor formador.\n"
    "● Participar de webconferências semanais com a coordenação do curso."
)

REQUISITOS_TP = [
    "Diploma de curso superior de graduação, em qualquer área, reconhecido pelo MEC",
    "Experiência mínima de 1 (um) ano no magistério do ensino básico ou superior, ou vinculação a programa de pós-graduação, conforme a Portaria CAPES nº 309/2024, alterada pela Portaria CAPES nº 83/2026, comprovada por declaração da instituição em papel timbrado",
    "Residir no município do polo ou em município limítrofe",
    "Disponibilidade de 20 horas semanais, inclusive aos sábados",
    "Habilidade para utilizar computador e o Ambiente Virtual de Aprendizagem Moodle",
]

METODO_NENHUM = None


def modalidades(prefixo):
    ac, ppiq, pcd, ptt = (uid(P, f"{prefixo}-{m}") for m in ("ac", "ppiq", "pcd", "ptt"))
    lista = [
        {"id": ac, "code": "AC", "name": "Ampla concorrência"},
        {"id": ppiq, "code": "PPIQ", "name": "Pessoas pretas, pardas, indígenas e quilombolas",
         "normativeRule": {"id": uid(P, f"{prefixo}-r-ppiq"), "foundation": "Lei nº 15.142, de 3 de junho de 2025, e Decreto nº 12.536, de 27 de junho de 2025", "version": "2025", "percentage": "30.0000"}},
        {"id": pcd, "code": "PcD", "name": "Pessoas com deficiência",
         "normativeRule": {"id": uid(P, f"{prefixo}-r-pcd"), "foundation": "Decreto nº 9.508, de 24 de setembro de 2018", "version": "2018", "percentage": "5.0000"}},
        {"id": ptt, "code": "PTT", "name": "Pessoas transgênero e travestis",
         "normativeRule": {"id": uid(P, f"{prefixo}-r-ptt"), "foundation": "Portaria CAPES nº 309, de 27 de setembro de 2024, alterada pela Portaria CAPES nº 83, de 6 de fevereiro de 2026", "version": "2026"}},
    ]
    return lista, ac, ppiq, pcd, ptt


def marco(prefixo, fatos):
    nasc, exp = fatos
    return {
        "id": uid(P, f"{prefixo}-marco"),
        "code": "FINAL",
        "name": "Classificação final pela prova de títulos",
        "orderProduction": "POR_PONTUACAO",
        "stages": [ETAPA_TIT],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "appealWindow": {"admits": True, "durationDays": 3, "unit": "DIAS_CORRIDOS"},
        "cutRule": {"targetKind": "FIXED", "targetCount": 10, "surplusCount": 5, "tieOutcome": "ADMITS_SURPLUS", "governedStage": ETAPA_DOC, "continuation": "ALLOWED"},
        "tiebreakers": [
            {"id": uid(P, f"{prefixo}-c1"), "order": 1, "type": "MENOR_VALOR_DE_FATO", "parameters": {"factId": nasc}, "whenMissing": "ULTIMO_NO_CRITERIO"},
            {"id": uid(P, f"{prefixo}-c2"), "order": 2, "type": "MAIOR_VALOR_DE_FATO", "parameters": {"factId": exp}, "whenMissing": "ULTIMO_NO_CRITERIO"},
            {"id": uid(P, f"{prefixo}-c3"), "order": 3, "type": "MAIOR_PONTUACAO_NA_ETAPA", "parameters": {"stageId": ETAPA_TIT}, "whenMissing": "CRITERIO_NAO_SE_APLICA"},
        ],
    }


def perfil(codigo, nome, localidade, *, vagas=0, quadro=None, duties, requisitos, workload, compensation, reserva=("LIMITED", 15)):
    lista, ac, ppiq, pcd, ptt = modalidades(codigo)
    fatos = (uid(P, f"{codigo}-f-nasc"), uid(P, f"{codigo}-f-exp"))
    quadro = quadro or (vagas, 0, 0, 0)
    return {
        "id": uid(P, f"perfil-{codigo}"),
        "code": codigo,
        "name": nome,
        "requirements": requisitos,
        "immediateVacancies": vagas,
        "reserveType": reserva[0],
        "reserveLimit": reserva[1],
        "locality": localidade,
        "duties": duties,
        "workload": workload,
        "compensation": compensation,
        "callForm": "INDIVIDUAL_MESSAGE",
        "competitionModalities": lista,
        "generalCompetitionModalityId": ac,
        "vacancyTable": [
            {"id": uid(P, f"{codigo}-l-ac"), "modalityId": None, "immediateVacancies": quadro[0]},
            {"id": uid(P, f"{codigo}-l-ppiq"), "modalityId": ppiq, "immediateVacancies": quadro[1]},
            {"id": uid(P, f"{codigo}-l-pcd"), "modalityId": pcd, "immediateVacancies": quadro[2]},
            {"id": uid(P, f"{codigo}-l-ptt"), "modalityId": ptt, "immediateVacancies": quadro[3]},
        ],
        "vacancyReversion": {"kind": "ON_BALANCE"},
        "declaredFacts": [
            {"id": fatos[0], "code": "NASCIMENTO", "label": "Data de nascimento", "type": "DATA"},
            {"id": fatos[1], "code": "EXPERIENCIA", "label": "Meses de experiência em tutoria na educação a distância", "type": "INTEIRO"},
        ],
        "classificationMilestones": [marco(codigo, fatos)],
    }


PERFIS = [
    perfil(
        f"TP-{indice:02d}",
        "Tutor presencial",
        f"Polo UAB de {polo} — endereço fictício de demonstração, s/n, Centro",
        duties=ATRIBUICOES_TP,
        requisitos=REQUISITOS_TP,
        workload="20 horas semanais",
        compensation="Bolsa mensal no valor de referência fixado pela CAPES para tutor",
    )
    for indice, polo in enumerate(POLOS, 1)
]
PERFIS += [
    perfil(
        "TD-ADM",
        "Tutor a distância do Curso Técnico em Administração na modalidade a distância, vinculado à Rede e-Tec Brasil e ao Programa Universidade Aberta do Brasil",
        "Cefor — atuação remota",
        vagas=6,
        quadro=(3, 2, 1, 0),
        duties=ATRIBUICOES_TD,
        requisitos=["Graduação em Administração, Ciências Contábeis ou Economia", "Experiência mínima de 1 (um) ano no magistério"],
        workload="20 horas semanais",
        compensation="Bolsa mensal no valor de referência fixado pela CAPES para tutor",
    ),
    perfil(
        "TD-INFO-EDU",
        "Tutor a distância da Pós-graduação em Informática na Educação",
        "Cefor — atuação remota",
        vagas=4,
        quadro=(2, 1, 1, 0),
        duties=ATRIBUICOES_TD + "\nOrientar os estudantes na elaboração do Trabalho Final de Curso, sob supervisão do professor orientador.",
        requisitos=["Mestrado em qualquer área, com graduação em Computação ou Informática", "Experiência mínima de 1 (um) ano no magistério superior"],
        workload="20 horas semanais",
        compensation="Bolsa mensal no valor de referência fixado pela CAPES para tutor",
    ),
]

EVENTOS = [
    ("Publicação", "Publicação do Edital", "2026-10-09T17:00:00-03:00", None, ""),
    ("Impugnação", "Prazo para impugnação do Edital", "2026-10-10T00:00:00-03:00", "2026-10-13T23:59:00-03:00", "Formulário eletrônico na página do certame"),
    ("Inscrições", "Período de inscrições e envio da documentação comprobatória", "2026-10-14T09:00:00-03:00", "2026-10-28T23:59:00-03:00", "Sistema de inscrições"),
    ("Homologação", "Homologação preliminar das inscrições", "2026-10-30T18:00:00-03:00", None, ""),
    ("Recurso", "Recurso contra a homologação preliminar das inscrições", "2026-10-31T00:00:00-03:00", "2026-11-02T23:59:00-03:00", "Formulário eletrônico de recursos"),
    ("Homologação", "Homologação final das inscrições", "2026-11-04T18:00:00-03:00", None, ""),
    ("Títulos", "Prova de títulos — análise da documentação conforme a Ficha de Avaliação do Anexo IV", "2026-11-05T08:00:00-03:00", "2026-11-13T17:00:00-03:00", ""),
    ("Resultado", "Resultado preliminar da prova de títulos", "2026-11-16T18:00:00-03:00", None, ""),
    ("Recurso", "Recurso contra o resultado preliminar da prova de títulos", "2026-11-17T00:00:00-03:00", "2026-11-19T23:59:00-03:00", "Formulário eletrônico de recursos"),
    ("Heteroidentificação", "Verificação da autodeclaração (heteroidentificação) dos candidatos às vagas reservadas a pretos e pardos, por webconferência, conforme convocação individual enviada por e-mail com 48 horas de antecedência", "2026-11-23T08:00:00-03:00", "2026-11-25T18:00:00-03:00", "Sala virtual informada na convocação individual"),
    ("Resultado", "Resultado preliminar da heteroidentificação", "2026-11-26T18:00:00-03:00", None, ""),
    ("Recurso", "Recurso contra o resultado preliminar da heteroidentificação", "2026-11-27T00:00:00-03:00", "2026-11-28T23:59:00-03:00", "Formulário eletrônico de recursos"),
    ("Análise", "Análise documental dos requisitos mínimos dos classificados até o corte", "2026-11-30T08:00:00-03:00", "2026-12-04T17:00:00-03:00", ""),
    ("Resultado", "Resultado preliminar da análise documental", "2026-12-07T18:00:00-03:00", None, ""),
    ("Recurso", "Recurso contra o resultado preliminar da análise documental", "2026-12-08T00:00:00-03:00", "2026-12-10T23:59:00-03:00", "Formulário eletrônico de recursos"),
    ("Resultado", "Resultado final e homologação do processo seletivo", "2026-12-15T18:00:00-03:00", None, ""),
    ("Formação", "Curso de formação em mediação pedagógica para os convocados que não o possuírem", "2027-01-11T08:00:00-03:00", "2027-02-12T23:59:00-03:00", "Ambiente Virtual de Aprendizagem do Cefor"),
    ("Convocação", "Início das convocações, conforme a demanda dos cursos", "2027-02-15T08:00:00-03:00", None, "Mensagem individual ao endereço eletrônico informado na inscrição"),
]
CRONOGRAMA = [
    {"id": uid(P, f"ev-{i}"), "type": t, "description": d, "startAt": s, "endAt": e, "order": i,
     "isRegistrationPeriod": t == "Inscrições", **({"location": loc} if loc else {})}
    for i, (t, d, s, e, loc) in enumerate(EVENTOS, 1)
]
EV_TIT, EV_ANALISE = uid(P, "ev-7"), uid(P, "ev-13")

ETAPAS = [
    {"id": ETAPA_TIT, "name": "Prova de títulos, conforme a Ficha de Avaliação do Anexo IV — formação acadêmica, experiência em tutoria e cursos de capacitação", "order": 1,
     "weight": "1.0000", "eliminatory": False, "classificatory": True, "maximumScore": "100.0000", "evaluationsPerRegistration": 1, "scheduleEventId": EV_TIT},
    {"id": ETAPA_DOC, "name": "Análise documental dos requisitos mínimos de formação e experiência exigidos para o perfil", "order": 2,
     "eliminatory": True, "classificatory": False, "forma": "DECISORIA", "rotuloFavoravel": "Habilitado", "rotuloDesfavoravel": "Não habilitado", "scheduleEventId": EV_ANALISE},
]

SECOES = [
    ("apresentacao", "A Diretora-Geral do Centro de Referência em Formação e em Educação a Distância do Instituto Federal do Espírito Santo, no uso de suas atribuições legais, e considerando o disposto na Portaria CAPES nº 309, de 27 de setembro de 2024, torna pública a abertura de processo seletivo simplificado para a formação de cadastro de reserva de tutores presenciais e a distância para atuarem nos cursos do Programa Universidade Aberta do Brasil (UAB) ofertados pelo Cefor/Ifes. [DOCUMENTO DE DEMONSTRAÇÃO — dados fictícios, sem valor normativo.]"),
    ("disposicoes-preliminares", "1.1 O processo seletivo será regido por este Edital e executado pela Comissão de Seleção designada por portaria da Diretora-Geral do Cefor.\n1.2 A seleção destina-se à formação de cadastro de reserva, e a convocação dos classificados dar-se-á conforme a necessidade dos cursos, durante o prazo de validade deste Edital.\n1.3 A atuação como bolsista não gera vínculo empregatício com o Ifes nem com a CAPES.\n1.4 É vedado o acúmulo de bolsas pagas no âmbito dos programas de fomento da CAPES e do FNDE."),
    ("requisitos-gerais", "2.1 Ser brasileiro nato ou naturalizado, ou estrangeiro com situação regular no país.\n2.2 Estar quite com as obrigações eleitorais e, se do sexo masculino, com as obrigações militares.\n2.3 Não possuir vínculo com outra bolsa paga pela CAPES ou pelo FNDE no período de atuação.\n2.4 Possuir os requisitos específicos do perfil pretendido, descritos neste Edital."),
    ("inscricao", "3.1 A inscrição será realizada exclusivamente pelo sistema de inscrições, no período previsto no Cronograma.\n3.2 O candidato deverá anexar, em arquivo PDF único de até 10 MB, os documentos obrigatórios e os documentos passíveis de pontuação, nomeando o arquivo no formato EDITAL 92.2026_CÓDIGO DE INSCRIÇÃO_MODALIDADE_NOME DO CANDIDATO.\n3.3 Não haverá conferência de documentação no momento da inscrição, e a responsabilidade pela documentação enviada é exclusiva do candidato.\n3.4 O candidato que enviar documentação com quantidade de páginas superior a 30 (trinta) terá a inscrição indeferida, sem possibilidade de interposição de recurso."),
    ("verificacao-autodeclaracao", "4.1 Os candidatos que se autodeclararem pretos ou pardos serão submetidos ao procedimento de heteroidentificação, realizado por comissão designada para esse fim, por webconferência.\n4.2 A comissão considerará exclusivamente as características fenotípicas do candidato.\n4.3 O não comparecimento ao procedimento implicará a exclusão do candidato da lista reservada, permanecendo na lista de ampla concorrência."),
    ("atendimento-pcd", "O candidato com deficiência que necessitar de atendimento especializado para participar das etapas deverá solicitá-lo no formulário de inscrição, indicando os recursos necessários."),
    ("classificacao", "A nota final do candidato, após a fase de recursos, será a pontuação obtida na prova de títulos, apresentada em ordem decrescente por código de inscrição.\nO candidato poderá concorrer a apenas um código de inscrição."),
    ("recursos", "8.1 Os recursos deverão ser interpostos exclusivamente por meio do formulário eletrônico de recursos, cujo link será disponibilizado na página do processo seletivo, observados os prazos do Cronograma.\n8.2 Não será admitido o envio de documentos na etapa recursal.\n8.3 Não serão aceitos recursos encaminhados por Correios, e-mail ou qualquer outra forma distinta da prevista no item 8.1."),
    ("convocacao", "11.1 A convocação será feita por mensagem individual ao endereço eletrônico informado na inscrição, e o convocado terá 2 (dois) dias úteis, contados do envio, para manifestar interesse.\n11.2 O candidato que não se manifestar no prazo será considerado desistente e substituído pelo próximo classificado do mesmo código de inscrição."),
    ("prazo-de-validade", "Este processo seletivo terá validade de 2 (dois) anos, contados da publicação do resultado final, podendo ser prorrogado uma única vez por igual período."),
    ("disposicoes-finais", "14.1 A inscrição implica o conhecimento e a aceitação das normas deste Edital.\n14.2 Os casos omissos serão resolvidos pela Comissão de Seleção, ouvida a Coordenação UAB do Ifes.\n14.3 Dúvidas poderão ser enviadas ao e-mail selecao.uab.demo@exemplo.ifes.edu.br."),
]

DOCUMENTOS = [
    {"id": uid(P, "d1"), "key": "identificacao", "name": "Documento de identificação com foto", "instructions": "Carteira de Identidade, Carteira Nacional de Habilitação, carteira de conselho profissional ou passaporte, frente e verso, legível e sem cortes.", "required": True, "order": 1},
    {"id": uid(P, "d2"), "key": "cpf", "name": "Comprovante de situação cadastral no CPF", "required": True, "order": 2},
    {"id": uid(P, "d3"), "key": "diploma", "name": "Diploma de graduação", "instructions": "Frente e verso.", "required": True, "order": 3},
    {"id": uid(P, "d4"), "key": "experiencia", "name": "Comprovante de experiência no magistério", "instructions": "Declaração da instituição em papel timbrado, com carimbo, data e assinatura, informando o período de atuação, ou carteira de trabalho com as páginas de identificação e do contrato.", "required": True, "order": 4},
    {"id": uid(P, "d5"), "key": "titulos", "name": "Documentos passíveis de pontuação", "instructions": "Conforme os itens da Ficha de Avaliação do Anexo IV, na ordem dos itens.", "required": False, "order": 5},
    {"id": uid(P, "d6"), "key": "disponibilidade", "name": "Declaração de disponibilidade", "instructions": "Conforme o modelo do Anexo II, preenchida e assinada.", "required": True, "order": 6},
    {"id": uid(P, "d7"), "key": "residencia", "name": "Comprovante de residência no município do polo ou em município limítrofe", "required": True, "order": 7, "profileId": PERFIS[0]["id"]},
    {"id": uid(P, "d8"), "key": "mestrado", "name": "Diploma de mestrado", "required": True, "order": 8, "profileId": PERFIS[-1]["id"]},
    {"id": uid(P, "d9"), "key": "autodeclaracao", "name": "Autodeclaração étnico-racial", "instructions": "Conforme o modelo do Anexo V.", "required": True, "order": 9, "modalityCode": "PPIQ"},
    {"id": uid(P, "d10"), "key": "laudo", "name": "Laudo médico", "instructions": "Emitido nos últimos 12 (doze) meses por médico especialista, com o código correspondente da CID e a descrição das limitações funcionais.", "required": True, "order": 10, "modalityCode": "PcD"},
    {"id": uid(P, "d11"), "key": "autodeclaracao-ptt", "name": "Autodeclaração de identidade de gênero", "instructions": "Conforme o modelo do Anexo VI.", "required": True, "order": 11, "modalityCode": "PTT"},
]

aut = autoridade("B", "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância")
edital = criar(
    "PS-AUD-B-2026",
    "Seleção de Tutores UAB — Cadastro de Reserva 2026 (DEMONSTRAÇÃO)",
    "92",
    2026,
    "Edital nº 92/2026 – Seleção de cadastro de reserva de tutores presenciais e a distância para atuarem nos cursos técnicos e de pós-graduação do Programa Universidade Aberta do Brasil (UAB) ofertados pelo Cefor/Ifes (DEMONSTRAÇÃO)",
    "Seleção de bolsistas para cadastro de reserva de tutoria em 16 polos e em dois cursos a distância.",
)
elaborar(edital, profiles=PERFIS, schedule=CRONOGRAMA, stages=ETAPAS, sections=[{"key": k, "content": v} for k, v in SECOES], documents=DOCUMENTOS)
teto(edital, 1)
anexos(edital, [
    "ANEXO I — CRONOGRAMA DETALHADO POR POLO",
    "ANEXO II — DECLARAÇÃO DE DISPONIBILIDADE DE CARGA HORÁRIA PARA O EXERCÍCIO DA TUTORIA NOS POLOS DE APOIO PRESENCIAL",
    "ANEXO III — QUADRO DE PERFIS",
    "ANEXO IV — FICHA DE AVALIAÇÃO DA PROVA DE TÍTULOS",
    "ANEXO V — MODELO DE AUTODECLARAÇÃO ÉTNICO-RACIAL",
    "ANEXO VI — MODELO DE AUTODECLARAÇÃO DE IDENTIDADE DE GÊNERO",
], {"disponibilidade": 2, "titulos": 4, "autodeclaracao": 5, "autodeclaracao-ptt": 6})
print("RASCUNHO", edital.id)
print("EDITAL_B", edital.id)
