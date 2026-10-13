"""CENÁRIO A — seleção realista: pós-graduação EaD com polos, cotas e sorteio (forma do 28/2026).

Dados fictícios. Nenhum dado pessoal real. Banco isolado ps_auditoria_pdf.
"""

import sys

sys.path.insert(0, "/private/tmp/claude-501/-Users-saymoncastro-Projetos-processo-seletivo--claude-worktrees-auditoria-edital-pdf-d33731/fba18c90-9168-4aeb-8300-d572628e7dd7/scratchpad")
from comum import (  # noqa: E402
    anexos,
    autoridade,
    criar,
    elaborar,
    previa,
    publicar,
    requerimento,
    teto,
    uid,
)

P = "A"
POLOS = [
    ("INF-BJN", "Polo Bom Jesus do Norte"),
    ("INF-IUN", "Polo Iúna"),
    ("INF-SMT", "Polo São Mateus"),
    ("INF-VAL", "Polo Vargem Alta"),
]

EV = {nome: uid(P, f"ev-{nome}") for nome in [
    "inscricoes", "habilitados", "sorteio", "res-sorteio", "analise", "preliminar",
    "recurso", "final", "homologacao", "aulas",
]}
ETAPA_DOC = uid(P, "etapa-documental")

METODO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "Concurso 6010",
    "occurrenceAt": "2026-11-14T19:00:00-03:00",
    "derivation": "A extração de sábado imediatamente anterior à data publicada do sorteio.",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "Os cinco números sorteados, na ordem dos prêmios, separados por espaço.",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "Não havendo extração na data prevista, vale a extração seguinte da mesma fonte.",
    },
}


def perfil(indice, codigo, polo):
    ac, ppi, pcd = (uid(P, f"{codigo}-{m}") for m in ("ac", "ppi", "pcd"))
    return {
        "id": uid(P, f"perfil-{codigo}"),
        "code": codigo,
        "name": "Especialização em Informática na Educação",
        "description": f"Curso de pós-graduação lato sensu, a distância, com encontros síncronos. {polo}.",
        "requirements": [
            "Diploma de curso superior de graduação (bacharelado, licenciatura ou tecnologia) reconhecido pelo MEC",
            "Acesso a computador com conexão à internet",
        ],
        "immediateVacancies": 40,
        "reserveType": "NONE",
        "locality": polo,
        "workload": "480 horas",
        "callForm": "PUBLICATION",
        "competitionModalities": [
            {"id": ac, "code": "AC", "name": "Ampla concorrência"},
            {
                "id": ppi,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "normativeRule": {
                    "id": uid(P, f"{codigo}-regra-ppi"),
                    "foundation": "Resolução CS nº 10/2017 do Ifes",
                    "version": "2017",
                    "percentage": "25.0000",
                },
            },
            {
                "id": pcd,
                "code": "PcD",
                "name": "Pessoas com deficiência",
                "normativeRule": {
                    "id": uid(P, f"{codigo}-regra-pcd"),
                    "foundation": "Resolução CS nº 10/2017 do Ifes",
                    "version": "2017",
                    "percentage": "5.0000",
                },
            },
        ],
        "generalCompetitionModalityId": ac,
        "vacancyTable": [
            {"id": uid(P, f"{codigo}-linha-ac"), "modalityId": None, "immediateVacancies": 28},
            {"id": uid(P, f"{codigo}-linha-ppi"), "modalityId": ppi, "immediateVacancies": 10},
            {"id": uid(P, f"{codigo}-linha-pcd"), "modalityId": pcd, "immediateVacancies": 2},
        ],
        "vacancyReversion": {"kind": "ON_EXHAUSTION"},
        "classificationMilestones": [
            {
                "id": uid(P, f"{codigo}-marco"),
                "code": "SORTEIO",
                "name": "Classificação por sorteio eletrônico",
                "orderProduction": "POR_SORTEIO",
                "stages": [],
                "operation": "SOMA_PONDERADA",
                "normalization": "NENHUMA",
                "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                "tiebreakers": [],
                "appealWindow": {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"},
                "cutRule": {
                    "targetKind": "FROM_VACANCY_TABLE",
                    "surplusCount": 15,
                    "tieOutcome": "STRICT",
                    "governedStage": ETAPA_DOC,
                    "continuation": "ALLOWED",
                },
            }
        ],
    }


def evento(chave, ordem, tipo, descricao, inicio, fim=None, local="", inscricao=False):
    return {
        "id": EV[chave],
        "type": tipo,
        "description": descricao,
        "startAt": inicio,
        "endAt": fim,
        "order": ordem,
        "isRegistrationPeriod": inscricao,
        **({"location": local} if local else {}),
    }


CRONOGRAMA = [
    evento("inscricoes", 1, "Inscrições", "Período de inscrições", "2026-10-13T09:00:00-03:00", "2026-10-30T23:59:00-03:00", inscricao=True),
    evento("habilitados", 2, "Habilitados", "Divulgação da relação de inscrições que participarão do sorteio", "2026-11-10T17:00:00-03:00"),
    evento("sorteio", 3, "Sorteio", "Sorteio eletrônico público", "2026-11-16T10:00:00-03:00", local="Transmissão pelo canal do Cefor no YouTube"),
    evento("res-sorteio", 4, "Resultado", "Divulgação da ordem do sorteio", "2026-11-16T17:00:00-03:00"),
    evento("analise", 5, "Análise", "Análise documental dos sorteados", "2026-11-17T08:00:00-03:00", "2026-11-24T17:00:00-03:00"),
    evento("preliminar", 6, "Resultado", "Resultado preliminar da análise documental", "2026-11-25T17:00:00-03:00"),
    evento("recurso", 7, "Recurso", "Prazo para interposição de recurso", "2026-11-26T00:00:00-03:00", "2026-11-27T23:59:00-03:00"),
    evento("final", 8, "Resultado", "Resultado final", "2026-12-02T17:00:00-03:00"),
    evento("homologacao", 9, "Matrícula", "Divulgação das matrículas homologadas", "2026-12-07T17:00:00-03:00"),
    evento("aulas", 10, "Aulas", "Início das aulas", "2027-03-01T08:00:00-03:00", local="Ambiente Virtual de Aprendizagem"),
]

ETAPAS = [
    {
        "id": ETAPA_DOC,
        "name": "Análise documental",
        "order": 1,
        "eliminatory": True,
        "classificatory": False,
        "forma": "DECISORIA",
        "rotuloFavoravel": "Deferida",
        "rotuloDesfavoravel": "Indeferida",
        "scheduleEventId": EV["analise"],
    }
]

SECOES = [
    ("apresentacao", "A Diretora-Geral do Centro de Referência em Formação e em Educação a Distância do Ifes, no uso de suas atribuições legais, torna pública a abertura de inscrições para o processo seletivo de alunos do curso de Pós-graduação Lato Sensu em Informática na Educação, na modalidade a distância, com ingresso em 2027/1. [DOCUMENTO DE DEMONSTRAÇÃO — dados fictícios, sem valor normativo.]"),
    ("disposicoes-preliminares", "O processo seletivo será conduzido por Comissão de Seleção designada pela Diretora-Geral do Cefor.\nAs dúvidas sobre este Edital serão esclarecidas exclusivamente pelo e-mail selecao.demo@exemplo.ifes.edu.br, de segunda a sexta-feira, das 8h às 17h.\nTodas as publicações deste processo seletivo serão feitas no endereço eletrônico do certame."),
    ("informacoes-gerais", "O curso é ofertado integralmente a distância, por meio do Ambiente Virtual de Aprendizagem, com encontros síncronos obrigatórios para avaliações finais e apresentação do Trabalho Final de Curso.\nO curso tem carga horária de 480 horas e duração prevista de 18 meses."),
    ("publico-alvo", "Portadores de diploma de curso superior de graduação em qualquer área do conhecimento."),
    ("requisitos-gerais", "Para se inscrever, o candidato deverá atender aos requisitos do polo pretendido, descritos na seção Perfis de Vaga."),
    ("inscricao", "A inscrição será feita exclusivamente pela internet, no endereço eletrônico do certame, no período previsto no Cronograma.\nNo ato da inscrição, o candidato indicará o polo e a lista de concorrência (ampla concorrência ou reserva de vagas) a que concorrerá.\nOs candidatos às vagas reservadas concorrem também às vagas de ampla concorrência do mesmo polo."),
    ("verificacao-autodeclaracao", "Os candidatos sorteados para as vagas reservadas a pretos e pardos serão convocados para o procedimento de verificação complementar da autodeclaração, por webconferência, em data a ser divulgada.\nO candidato cuja autodeclaração for indeferida permanecerá apenas na lista de ampla concorrência."),
    ("classificacao", "Havendo mais inscritos que vagas, a ordem de classificação será definida por sorteio eletrônico, conforme o método publicado na seção Perfis de Vaga.\nApós o sorteio, serão analisados os documentos dos sorteados até o número de vagas do polo e da lista, mais os suplentes previstos."),
    ("recursos", "Caberá recurso contra o resultado preliminar da análise documental, no prazo previsto no Cronograma, exclusivamente pelo sistema de inscrição.\nNão serão aceitos recursos enviados por e-mail ou fora do prazo."),
    ("convocacao", "Havendo desistência, serão convocados os suplentes, na ordem do sorteio, por publicação no endereço eletrônico do certame."),
    ("matricula", "A matrícula será efetivada a partir da documentação enviada na inscrição, sem necessidade de comparecimento presencial."),
    ("certificado", "Fará jus ao certificado de especialista o aluno aprovado em todos os componentes curriculares e no Trabalho Final de Curso."),
    ("disposicoes-finais", "Os casos omissos serão resolvidos pela Comissão de Seleção, ouvida a Diretoria de Ensino do Cefor."),
]

DOCUMENTOS = [
    {"id": uid(P, "doc-id"), "key": "identificacao", "name": "Documento de identificação com foto", "instructions": "Frente e verso em arquivo único, em PDF.", "required": True, "order": 1},
    {"id": uid(P, "doc-cpf"), "key": "cpf", "name": "Comprovante de inscrição no CPF", "required": True, "order": 2},
    {"id": uid(P, "doc-diploma"), "key": "diploma", "name": "Diploma de graduação", "instructions": "Frente e verso, ou declaração de conclusão acompanhada do histórico.", "required": True, "order": 3},
    {"id": uid(P, "doc-eleitoral"), "key": "eleitoral", "name": "Certidão de quitação eleitoral", "required": True, "order": 4},
    {"id": uid(P, "doc-nome-social"), "key": "nome-social", "name": "Requerimento de uso do nome social", "required": False, "order": 5},
    {"id": uid(P, "doc-autodecl"), "key": "autodeclaracao", "name": "Autodeclaração étnico-racial", "instructions": "Conforme o modelo do Anexo I.", "required": True, "order": 6, "modalityCode": "PPI"},
    {"id": uid(P, "doc-laudo"), "key": "laudo", "name": "Laudo médico", "instructions": "Emitido nos últimos 12 meses, com o código da CID.", "required": True, "order": 7, "modalityCode": "PcD"},
]

aut = autoridade("A", "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância", nome="Fulana de Tal", ato="Portaria nº 0000, de 2 de janeiro de 2026 (fictícia)")
edital = criar(
    "PS-AUD-A-2026",
    "Processo Seletivo de Alunos — Pós-graduação EaD 2027/1 (DEMONSTRAÇÃO)",
    "91",
    2026,
    "Edital nº 91/2026 – Curso de Pós-graduação Lato Sensu em Informática na Educação na modalidade EaD (DEMONSTRAÇÃO)",
    "Processo seletivo de alunos para o curso de Pós-graduação Lato Sensu em Informática na Educação, a distância, em quatro polos.",
)
elaborar(
    edital,
    profiles=[perfil(i, c, p) for i, (c, p) in enumerate(POLOS)],
    schedule=CRONOGRAMA,
    stages=ETAPAS,
    sections=[{"key": k, "content": v} for k, v in SECOES],
    documents=DOCUMENTOS,
    draw_method=METODO,
)
requerimento(edital, "AT_ENROLLMENT", "Declaro, sob as penas da lei, que as informações prestadas neste Requerimento de Matrícula são verdadeiras e estou ciente de que a falsidade de qualquer delas acarreta o cancelamento da matrícula, a qualquer tempo.")
teto(edital, 1)
anexos(edital, ["ANEXO I — MODELO DE AUTODECLARAÇÃO ÉTNICO-RACIAL", "ANEXO II — MODELO DE LAUDO MÉDICO", "ANEXO III — MATRIZ CURRICULAR DO CURSO"], {"autodeclaracao": 1, "laudo": 2})
previa(edital, "A-previa")
publicar(edital, aut.pk, "A-publicado")
print("EDITAL_A", edital.id)
