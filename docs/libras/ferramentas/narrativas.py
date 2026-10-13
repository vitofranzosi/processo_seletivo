"""A camada comunicativa (rodada 2): três narrativas por edital, como dados.

Cada narrativa reúne, em torno de uma pergunta do candidato, os enunciados normativos que a respondem —
vindos de qualquer seção —, com destinatário, condição, ação, consequência, prazo, alcance e exceções, as
linhas de cobertura que os sustentam, as ambiguidades que dependem da área responsável e perguntas para
verificar a compreensão. A **ação** é síntese documental em português, para conferência: não é tradução.

Modalidades: OBRIGAÇÃO, POSSIBILIDADE, PROIBIÇÃO, CONDIÇÃO (requisito para algo valer), REGRA (como algo
funciona), CONSEQUÊNCIA, PRAZO, INFORMAÇÃO, AUSÊNCIA (o edital nada declara; não equivale a proibição).
"""


def E(
    id_,
    modalidade,
    acao,
    fontes,
    destinatario="",
    condicao="",
    consequencia="",
    prazo="",
    alcance="",
    nota="",
    variante="",
    pendencia="",
    atos=(),
):
    """`pendencia`: o que o enunciado afirma e ainda depende de esclarecimento (rodada 4). `atos`: documentos fora da
    versão inventariada que mudam ou contradizem o enunciado — Retificação, comunicado, página do processo."""
    return dict(
        pendencia=pendencia,
        atos=list(atos),
        id=id_,
        modalidade=modalidade,
        acao=acao,
        fontes=fontes,
        destinatario=destinatario,
        condicao=condicao,
        consequencia=consequencia,
        prazo=prazo,
        alcance=alcance,
        nota=nota,
        variante=variante,
    )


def A(tipo, texto, fontes, pergunta):
    return dict(tipo=tipo, texto=texto, fontes=fontes, pergunta=pergunta)


def P(pergunta, resposta, fontes, nota="", estado="definitiva", pendencia=""):
    """`estado`: “definitiva” (o edital responde, sem divergência conhecida), “com pendência” (o edital responde, mas
    há divergência entre documentos ou alcance a esclarecer) ou “o edital não responde”. Uma pergunta com pendência
    não tem gabarito fechado: a resposta esperada é a que comunica a pendência sem resolvê-la."""
    return dict(pergunta=pergunta, resposta=resposta, fontes=fontes, nota=nota, estado=estado, pendencia=pendencia)


TITULOS = {
    "inscricao": "Como realizar uma inscrição válida",
    "classificacao": "Como ocorre a classificação e quem pode progredir",
    "recurso": "Como contestar cada decisão",
}

N = {}

# ═════════════════════════════════════════════════════════════════════════════════════════════════
# 91/2026 — Pós-graduação EaD, quatro polos, sorteio
# ═════════════════════════════════════════════════════════════════════════════════════════════════
N["E91"] = {}
N["E91"]["inscricao"] = dict(
    pergunta="Quero estudar num dos quatro polos: posso me inscrever, como, até quando, o que envio e o que pode invalidar a inscrição?",
    destinatarios="Pessoas graduadas que queiram uma vaga no curso, num dos quatro polos; com obrigações a mais para quem concorre nas listas PPI e PcD.",
    enunciados=[
        E(
            "INS-91-01",
            "CONDIÇÃO",
            "Ter diploma de graduação — bacharelado, licenciatura ou tecnologia — reconhecido pelo MEC, e acesso a computador com internet.",
            ["E91-014", "E91-016", "E91-024", "E91-036", "E91-037"],
            destinatario="Todos",
            alcance="Os requisitos estão na subseção comum 5.5; cada polo remete a ela.",
            nota="O público-alvo (seção 3) diz “em qualquer área do conhecimento”; os requisitos enumeram graus. Equivalência provável (LIB-0021).",
        ),
        E(
            "INS-91-02",
            "OBRIGAÇÃO",
            "Inscrever-se exclusivamente pela internet, no endereço eletrônico do certame.",
            ["E91-048", "E91-009"],
            destinatario="Todos",
            consequencia="Outra via não está prevista.",
            nota="O endereço não está escrito no edital.",
        ),
        E(
            "INS-91-03",
            "PRAZO",
            "O período de inscrições vai de 13/10/2026, às 09h, a 30/10/2026, às 23h59.",
            ["E91-073", "E91-048"],
            destinatario="Todos",
            prazo="13/10/2026 09h a 30/10/2026 23h59 (v1); até 04/11/2026 23h59 desde a Retificação de 11/10/2026 (v2).",
            nota="A Retificação mudou só o término.",
        ),
        E(
            "INS-91-04",
            "OBRIGAÇÃO",
            "Na inscrição, indicar o polo e a lista de concorrência (ampla ou reserva).",
            ["E91-049", "E91-018", "E91-019", "E91-021"],
            destinatario="Todos",
            alcance="Polos e vagas: Tabela 1; vagas por lista: Tabela 2; o que é cada lista: Tabela 3.",
        ),
        E(
            "INS-91-05",
            "REGRA",
            "Quem concorre a vaga reservada concorre também às vagas de ampla concorrência do mesmo polo.",
            ["E91-050"],
            destinatario="Candidatos das listas PPI e PcD",
        ),
        E(
            "INS-91-06",
            "CONDIÇÃO",
            "Cada pessoa pode ter apenas 1 inscrição enviada neste edital.",
            ["E91-051"],
            destinatario="Todos",
            consequencia="O edital não diz o que acontece com uma segunda inscrição; o sistema recusa o envio (auditoria, §6).",
            alcance="Conta a inscrição enviada; o rascunho não.",
        ),
        E(
            "INS-91-07",
            "OBRIGAÇÃO",
            "Enviar: documento de identificação com foto (frente e verso, arquivo único, PDF); comprovante de inscrição no CPF; diploma (ou declaração de conclusão com histórico); certidão de quitação eleitoral.",
            ["E91-053", "E91-054", "E91-055", "E91-056", "E91-057"],
            destinatario="Todos",
        ),
        E(
            "INS-91-08",
            "POSSIBILIDADE",
            "Pedir o uso do nome social, por requerimento facultativo.",
            ["E91-058"],
            destinatario="Quem quiser usar o nome social",
        ),
        E(
            "INS-91-09",
            "OBRIGAÇÃO",
            "Enviar a autodeclaração étnico-racial, no modelo do Anexo I.",
            ["E91-059", "E91-060", "E91-095"],
            destinatario="Quem concorre na lista PPI",
        ),
        E(
            "INS-91-10",
            "OBRIGAÇÃO",
            "Enviar laudo médico emitido nos últimos 12 meses, com o código da CID.",
            ["E91-061", "E91-062"],
            destinatario="Quem concorre na lista PcD",
        ),
        E(
            "INS-91-11",
            "OBRIGAÇÃO",
            "Enviar o Requerimento de Matrícula já na inscrição, declarando, sob as penas da lei, que as informações são verdadeiras.",
            ["E91-090", "E91-091"],
            destinatario="Todos",
            consequencia="A falsidade de qualquer informação cancela a matrícula, a qualquer tempo.",
            nota="Está na seção 14 (Da Matrícula), mas é ato da inscrição.",
        ),
        E(
            "INS-91-12",
            "REGRA",
            "Toda inscrição enviada participa do sorteio; os documentos só são analisados depois, para os sorteados até o número de vagas, mais suplentes.",
            ["E91-043", "E91-045", "E91-067", "E91-070"],
            destinatario="Todos",
            consequencia="Documentação irregular não impede o sorteio; leva ao indeferimento na análise documental, que é eliminatória.",
            nota="Relação entre a seção 5 (marco), a 9 (Etapa) e a 10 (texto livre).",
        ),
    ],
    ambiguidades=[
        A(
            "lacuna",
            "O endereço eletrônico do certame não está escrito no edital.",
            ["E91-009", "E91-048"],
            "Qual é o endereço, e onde o candidato o encontra?",
        ),
        A(
            "questão jurídica",
            "Nenhuma cláusula sobre recursos de acessibilidade na inscrição. Para ingresso em curso, a LBI, art. 30, II, prevê formulário de inscrição com campos para o candidato com deficiência informar os recursos de que precisa. Ausência de cláusula não é ausência de direito.",
            [],
            "O formulário do sistema oferece esses campos, e o edital deveria dizê-lo?",
        ),
        A(
            "ambiguidade",
            "“Arquivo único, em PDF” aparece só na identificação; não se sabe se vale para os demais documentos.",
            ["E91-054"],
            "O formato vale para todos os documentos?",
        ),
        A(
            "lacuna",
            "Não se diz como comprovar o acesso a computador com internet.",
            ["E91-037"],
            "É declaração, ou não há comprovação?",
        ),
    ],
    perguntas=[
        P(
            "Tenho diploma de tecnólogo. Posso me inscrever?",
            "Sim: o requisito aceita graduação em bacharelado, licenciatura ou tecnologia, reconhecida pelo MEC.",
            ["E91-036"],
        ),
        P(
            "Até quando posso me inscrever?",
            "Até 04/11/2026, às 23h59, desde a Retificação de 11/10/2026. Antes dela, o prazo era 30/10/2026.",
            ["E91-073"],
            nota="Resposta depende da versão vigente.",
        ),
        P(
            "Concorro na lista PPI. Que documento a mais envio?",
            "A autodeclaração étnico-racial, no modelo do Anexo I.",
            ["E91-060"],
        ),
        P(
            "Se concorrer pela reserva, perco a vaga da ampla concorrência?",
            "Não: concorre também às vagas de ampla do mesmo polo.",
            ["E91-050"],
        ),
        P("Posso me inscrever em dois polos?", "Não: cada pessoa pode ter apenas uma inscrição enviada.", ["E91-051"]),
        P(
            "Esqueci um documento. Fico fora do sorteio?",
            "Não: toda inscrição enviada participa do sorteio. Mas, se você for sorteado, a falta leva ao indeferimento na análise documental, que é eliminatória.",
            ["E91-043", "E91-067"],
        ),
    ],
    decisoes=[
        "Agrupar por destinatário (todos, PPI, PcD) ou por momento (antes, durante, depois do envio).",
        "Como relacionar polo e lista no espaço de sinalização, e se a Tabela 1 entra no vídeo.",
        "Se as datas, os nomes dos documentos e os anexos aparecem também por escrito.",
    ],
    reaproveitamento=dict(
        roteiro="A sequência requisitos → canal e prazo → escolha de polo e lista → documentos por destinatário → limite de inscrições → Requerimento se aplica a outros editais de ingresso em curso; o conteúdo de cada passo muda.",
        solucao="Candidatas a solução comum, se a área e o profissional confirmarem: limite de inscrições (LIB-0034), cabeçalhos de grupos de documentos (LIB-0035, LIB-0041), momento do Requerimento (LIB-0064), concorrência simultânea (LIB-0033). A terminologia (polo, lista, ampla concorrência) precisa estar decidida antes.",
        gravacao="Improvável por inteiro: prazos, polos e documentos mudam. Possível, se validado, para trechos de texto fixo do sistema que entrem do mesmo modo noutra narrativa.",
    ),
)
N["E91"]["classificacao"] = dict(
    pergunta="Como se decide quem entra no curso, e o que acontece depois do sorteio?",
    destinatarios="Inscritos de cada polo, separados por lista de concorrência.",
    enunciados=[
        E(
            "CLA-91-01",
            "REGRA",
            "Cada polo tem a sua própria classificação e o seu próprio resultado: os candidatos de um polo não concorrem com os de outro.",
            ["E91-039", "E91-025", "E91-028", "E91-031", "E91-034"],
            alcance="Vale para o marco SORTEIO, impresso uma vez para os quatro polos (5.6).",
        ),
        E(
            "CLA-91-02",
            "REGRA",
            "A ordem de classificação é produzida por sorteio.",
            ["E91-040", "E91-041", "E91-069"],
            condicao="O texto livre da seção 10 diz “havendo mais inscritos que vagas”; o marco não põe condição.",
        ),
        E(
            "CLA-91-03",
            "REGRA",
            "Participam do sorteio todas as inscrições enviadas; a relação de participantes é divulgada em 10/11/2026, às 17h.",
            ["E91-043", "E91-074"],
        ),
        E(
            "CLA-91-04",
            "INFORMAÇÃO",
            "O sorteio usa o resultado do concurso 6010 da Loteria Federal (14/11/2026, às 19h): os cinco números sorteados, na ordem dos prêmios, formam a semente; se não houver extração na data, vale a seguinte. O sorteio é público em 16/11/2026, às 10h, transmitido pelo canal do Cefor no YouTube, e a ordem sai às 17h.",
            ["E91-042", "E91-075", "E91-076"],
            nota="São dois momentos: a extração da loteria (14/11) e a execução do sorteio (16/11).",
        ),
        E(
            "CLA-91-05",
            "REGRA",
            "Seguem para a análise documental os primeiros da ordem, até o número de vagas do polo e da lista, mais 15 suplentes.",
            ["E91-045", "E91-018", "E91-019", "E91-070"],
            alcance="Número de vagas por polo e lista na Tabela 2 (v1: 28 ampla, 10 PPI, 2 PcD; v2: 33 na ampla do polo BJN).",
        ),
        E(
            "CLA-91-06",
            "CONDIÇÃO",
            "A análise documental é eliminatória e resulta em Deferida ou Indeferida; ocorre de 17/11/2026 a 24/11/2026.",
            ["E91-067", "E91-077"],
            consequencia="Indeferida, a pessoa sai do processo.",
            nota="A consequência do indeferimento decorre do caráter eliminatório; não está escrita por extenso.",
        ),
        E(
            "CLA-91-07",
            "OBRIGAÇÃO",
            "Os sorteados para vagas reservadas a pretos e pardos são convocados à verificação complementar da autodeclaração, por webconferência, em data a divulgar.",
            ["E91-064"],
            destinatario="Sorteados para vagas reservadas a pretos e pardos",
        ),
        E(
            "CLA-91-08",
            "CONSEQUÊNCIA",
            "Autodeclaração indeferida: a pessoa permanece apenas na lista de ampla concorrência.",
            ["E91-065", "E91-050"],
        ),
        E(
            "CLA-91-09",
            "REGRA",
            "Sem aprovados na reserva, a vaga vai para a ampla concorrência do mesmo polo.",
            ["E91-020"],
        ),
        E(
            "CLA-91-10",
            "POSSIBILIDADE",
            "Pode haver chamada além do corte, na mesma ordem; havendo desistência, os suplentes são chamados na ordem do sorteio, por publicação.",
            ["E91-046", "E91-087", "E91-022"],
        ),
        E(
            "CLA-91-11",
            "PRAZO",
            "Resultado preliminar da análise documental em 25/11/2026; resultado final em 02/12/2026; matrículas homologadas em 07/12/2026; aulas a partir de 01/03/2027.",
            ["E91-078", "E91-080", "E91-081", "E91-082"],
        ),
    ],
    ambiguidades=[
        A(
            "ambiguidade",
            "O texto livre condiciona o sorteio a “haver mais inscritos que vagas”; o marco publica o sorteio sem condição.",
            ["E91-069", "E91-041"],
            "Com menos inscritos que vagas, há sorteio (para a ordem) ou não?",
        ),
        A(
            "ambiguidade",
            "Não se diz se há uma ordem por polo ou uma por polo e lista; o corte fala em “recorte” (polo e lista).",
            ["E91-045", "E91-076"],
            "Quantas ordens são divulgadas por polo?",
        ),
        A(
            "inconsistência",
            "A seção 8 fala em “pretos e pardos”; a lista reservada é PPI (pretos, pardos e indígenas).",
            ["E91-064", "E91-021"],
            "Indígenas passam pela verificação? Por qual procedimento?",
        ),
        A(
            "lacuna",
            "Não se diz quem substitui quem é indeferido na análise documental, nem até quando se chama.",
            ["E91-046", "E91-087"],
            "Os suplentes cobrem também os indeferidos?",
        ),
    ],
    perguntas=[
        P(
            "Sou do polo de Iúna. Concorro com os candidatos de Vargem Alta?",
            "Não: cada polo tem classificação e resultado próprios.",
            ["E91-039"],
        ),
        P("Quem participa do sorteio?", "Todas as inscrições enviadas.", ["E91-043"]),
        P(
            "Fiquei em 30º na ampla concorrência do polo Bom Jesus do Norte. Meus documentos serão analisados?",
            "Sim: seguem os primeiros até o número de vagas da lista (28; 33 desde a Retificação), mais 15 suplentes.",
            ["E91-045", "E91-019"],
        ),
        P(
            "Se ninguém da lista PcD for aprovado, o que acontece com as 2 vagas?",
            "Vão para a ampla concorrência do mesmo polo.",
            ["E91-020"],
        ),
        P(
            "Minha autodeclaração foi indeferida. Saio do processo?",
            "Não: você permanece apenas na lista de ampla concorrência.",
            ["E91-065"],
        ),
        P("Quando sai a ordem do sorteio?", "Em 16/11/2026, às 17h.", ["E91-076"]),
    ],
    decisoes=[
        "Como explicar semente e algoritmo sem alterar a norma.",
        "Como representar a relação entre polos, listas e suplentes.",
        "Se a sequência no tempo (relação, sorteio, ordem, análise, resultado) organiza o vídeo.",
    ],
    reaproveitamento=dict(
        roteiro="Reaproveitável em editais de ingresso por sorteio: universo → método → corte → análise documental → verificação → reversão → chamadas.",
        solucao="As frases do sistema (LIB-0023, LIB-0025, LIB-0027, LIB-0030, LIB-0015) são as candidatas mais fortes; o método (LIB-0026) só com a mesma fonte e as mesmas regras de semente e substituição.",
        gravacao="O bloco do método muda a cada edital (concurso, datas). Uma explicação conceitual do que é a semente poderia ser gravada à parte, se o profissional e a área a aceitarem como trecho autônomo.",
    ),
)
N["E91"]["recurso"] = dict(
    pergunta="Discordo de uma decisão: posso recorrer, contra o quê, até quando e por onde?",
    destinatarios="Inscritos afetados por cada decisão.",
    enunciados=[
        E(
            "REC-91-01",
            "PRAZO",
            "Contra a ordem do sorteio (resultado do marco “Classificação por sorteio eletrônico”): recurso em 2 dias corridos, contados da divulgação desse resultado.",
            ["E91-044", "E91-076"],
            variante="Contra a ordem do sorteio",
            prazo="2 dias corridos a partir de 16/11/2026, 17h.",
            nota="Não há Evento de Cronograma para este recurso, nem canal dito.",
        ),
        E(
            "REC-91-02",
            "PRAZO",
            "Contra o resultado preliminar da análise documental (25/11/2026): recurso no prazo do Cronograma, de 26/11/2026, às 00h, a 27/11/2026, às 23h59.",
            ["E91-084", "E91-079", "E91-078"],
            variante="Contra o resultado preliminar da análise documental",
        ),
        E(
            "REC-91-03",
            "OBRIGAÇÃO",
            "Recorrer exclusivamente pelo sistema de inscrição.",
            ["E91-084"],
            variante="Contra o resultado preliminar da análise documental",
        ),
        E(
            "REC-91-04",
            "PROIBIÇÃO",
            "Recursos por e-mail ou fora do prazo não são aceitos.",
            ["E91-085"],
            variante="Contra o resultado preliminar da análise documental",
            alcance="Escrito logo depois do recurso da análise documental; não se diz se vale também para o recurso do sorteio.",
        ),
        E(
            "REC-91-05",
            "AUSÊNCIA",
            "O edital nada declara sobre recurso contra o indeferimento da autodeclaração.",
            ["E91-065"],
            variante="Contra o indeferimento da autodeclaração",
            nota="Ausência de cláusula não é proibição; o compositor só imprime negativa expressa quando declarada. Se vias legais fora do edital se aplicam (Lei nº 9.784/1999, arts. 56 a 59) é questão jurídica.",
        ),
    ],
    ambiguidades=[
        A(
            "lacuna",
            "Não se diz por onde se recorre da ordem do sorteio.",
            ["E91-044", "E91-084"],
            "O canal da seção 12 vale para todo recurso?",
        ),
        A(
            "ambiguidade",
            "O Evento 7 se chama “Prazo para interposição de recurso”, sem dizer contra o quê.",
            ["E91-079"],
            "Renomear em Retificação futura? (decisão da área)",
        ),
        A(
            "ambiguidade",
            "“2 dias corridos contados da divulgação” sem hora final declarada.",
            ["E91-044"],
            "O prazo termina às 23h59 do segundo dia?",
        ),
        A(
            "questão jurídica",
            "Silêncio sobre recurso da verificação da autodeclaração.",
            ["E91-064", "E91-065"],
            "Há recurso administrativo? Com que prazo?",
        ),
    ],
    perguntas=[
        P(
            "Discordo da ordem do sorteio. Posso recorrer? Em quanto tempo?",
            "Sim, em 2 dias corridos contados da divulgação da ordem (16/11/2026, 17h). O edital não diz o canal.",
            ["E91-044", "E91-076"],
        ),
        P(
            "Meus documentos foram indeferidos no resultado preliminar. Até quando recorro, e por onde?",
            "De 26/11/2026, às 00h, a 27/11/2026, às 23h59, só pelo sistema de inscrição.",
            ["E91-079", "E91-084"],
        ),
        P("Posso mandar o recurso por e-mail?", "Não.", ["E91-085"]),
        P(
            "O período de 26 e 27/11 serve para recorrer do sorteio?",
            "Não: é o prazo contra o resultado preliminar da análise documental. O do sorteio é outro.",
            ["E91-084", "E91-044"],
        ),
        P(
            "O edital diz que não cabe recurso contra o indeferimento da autodeclaração?",
            "Não diz nada. Ausência de cláusula não é proibição.",
            ["E91-065"],
        ),
    ],
    decisoes=[
        "Como separar visualmente os dois objetos de recurso, para que não se confundam.",
        "Como comunicar o que o edital não diz (canal do recurso do sorteio) sem completar a norma.",
    ],
    reaproveitamento=dict(
        roteiro="O esquema objeto → prazo e início → canal → vedações → o que o edital não diz se aplica a qualquer edital; os objetos mudam.",
        solucao="A frase do recurso do marco (LIB-0028) é parametrizável pelo nome do marco e pelos dias — variáveis de condição: cada objeto pede a sua tradução.",
        gravacao="Pouco provável: cada objeto tem prazo e datas próprios.",
    ),
)

# ═════════════════════════════════════════════════════════════════════════════════════════════════
# 92/2026 — Tutores UAB, cadastro de reserva, prova de títulos
# ═════════════════════════════════════════════════════════════════════════════════════════════════
N["E92"] = {}
N["E92"]["inscricao"] = dict(
    pergunta="Posso concorrer a uma bolsa de tutor, e o que preciso fazer para a inscrição valer?",
    destinatarios="Pessoas que queiram atuar como tutor a distância (2 Perfis) ou presencial (16 polos); obrigações a mais por Perfil e por modalidade.",
    enunciados=[
        E(
            "INS-92-01",
            "CONDIÇÃO",
            "Ser brasileiro nato ou naturalizado, ou estrangeiro em situação regular; estar quite com as obrigações eleitorais e, se do sexo masculino, militares.",
            ["E92-012", "E92-013"],
            destinatario="Todos",
        ),
        E(
            "INS-92-02",
            "CONDIÇÃO",
            "Não ter vínculo com outra bolsa da CAPES ou do FNDE no período de atuação.",
            ["E92-014", "E92-010"],
            destinatario="Todos",
            nota="O item 1.4 proíbe o acúmulo; o 2.3 o faz requisito (LIB-0136, LIB-0137).",
        ),
        E(
            "INS-92-03",
            "CONDIÇÃO",
            "Tutor a distância do Curso Técnico em Administração (TD-ADM): graduação em Administração, Ciências Contábeis ou Economia, e um ano no magistério.",
            ["E92-025", "E92-026"],
            destinatario="Candidatos ao TD-ADM",
        ),
        E(
            "INS-92-04",
            "CONDIÇÃO",
            "Tutor a distância da Pós-graduação em Informática na Educação (TD-INFO-EDU): mestrado em qualquer área, com graduação em Computação ou Informática, e um ano no magistério superior.",
            ["E92-032", "E92-033"],
            destinatario="Candidatos ao TD-INFO-EDU",
        ),
        E(
            "INS-92-05",
            "CONDIÇÃO",
            "Tutor presencial (TP-01 a TP-16): graduação em qualquer área; um ano no magistério básico ou superior, ou vínculo a pós-graduação, comprovado por declaração; residir no município do polo ou em limítrofe; disponibilidade de 20 horas semanais, inclusive aos sábados; habilidade com computador e o Moodle.",
            ["E92-039", "E92-135", "E92-136", "E92-137", "E92-138", "E92-139"],
            destinatario="Candidatos aos Perfis TP",
        ),
        E(
            "INS-92-06",
            "OBRIGAÇÃO",
            "Inscrever-se exclusivamente pelo sistema de inscrições, de 14/10/2026, às 09h, a 28/10/2026, às 23h59.",
            ["E92-151", "E92-190"],
            destinatario="Todos",
        ),
        E(
            "INS-92-07",
            "OBRIGAÇÃO",
            "Anexar um único PDF, de até 10 MB, com os documentos obrigatórios e os pontuáveis, nomeado no padrão “EDITAL 92.2026_CÓDIGO DE INSCRIÇÃO_MODALIDADE_NOME DO CANDIDATO”.",
            ["E92-152"],
            destinatario="Todos",
        ),
        E(
            "INS-92-08",
            "PROIBIÇÃO",
            "Documentação com mais de 30 páginas leva ao indeferimento da inscrição.",
            ["E92-154"],
            destinatario="Todos",
            consequencia="Inscrição indeferida, sem possibilidade de recurso.",
        ),
        E(
            "INS-92-09",
            "REGRA",
            "Não há conferência dos documentos no envio; a responsabilidade pelo que se envia é exclusiva do candidato.",
            ["E92-153"],
            destinatario="Todos",
        ),
        E(
            "INS-92-10",
            "CONDIÇÃO",
            "Cada pessoa pode ter apenas 1 inscrição enviada e concorrer a um só código de inscrição.",
            ["E92-155", "E92-185"],
            destinatario="Todos",
            nota="Dita duas vezes, com vocabulários diferentes (LIB-0034, LIB-0110).",
        ),
        E(
            "INS-92-11",
            "OBRIGAÇÃO",
            "Enviar: identificação com foto (Carteira de Identidade, CNH, carteira de conselho profissional ou passaporte, legível); comprovante de situação cadastral no CPF; diploma de graduação; comprovante de experiência no magistério; declaração de disponibilidade (modelo do Anexo II). Os documentos pontuáveis (Anexo IV) são facultativos.",
            ["E92-157", "E92-158", "E92-159", "E92-160", "E92-161", "E92-162", "E92-163"],
            destinatario="Todos",
        ),
        E(
            "INS-92-12",
            "OBRIGAÇÃO",
            "Enviar documentos a mais conforme o Perfil e a modalidade: TP-01, comprovante de residência; TD-INFO-EDU, diploma de mestrado; PPIQ, autodeclaração étnico-racial (Anexo V); PcD, laudo de especialista com CID e limitações funcionais; PTT, autodeclaração de identidade de gênero (Anexo VI).",
            [
                "E92-164",
                "E92-165",
                "E92-166",
                "E92-167",
                "E92-168",
                "E92-169",
                "E92-170",
                "E92-171",
                "E92-172",
                "E92-173",
            ],
            destinatario="Conforme o Perfil e a modalidade",
        ),
        E(
            "INS-92-13",
            "OBRIGAÇÃO",
            "Informar, na inscrição, os meses de experiência em tutoria na educação a distância e a data de nascimento.",
            ["E92-027"],
            destinatario="Todos os Perfis",
            nota="Esses dados decidem o desempate (CLA-92-04).",
        ),
        E(
            "INS-92-14",
            "POSSIBILIDADE",
            "Quem tem deficiência e precisa de atendimento especializado pode pedi-lo no formulário de inscrição, indicando os recursos necessários.",
            ["E92-179"],
            destinatario="Candidatos com deficiência",
            nota="A Retificação de 11/10/2026 retira esta cláusula do edital (v2). A retirada da cláusula não suprime direitos previstos em lei; qual norma alcança esta seleção de bolsistas é questão jurídica.",
        ),
    ],
    ambiguidades=[
        A(
            "inconsistência",
            "O comprovante de residência é pedido só ao TP-01, embora o requisito valha para os 16 polos.",
            ["E92-164", "E92-137"],
            "O comprovante vale para todos os TP? (conteúdo da simulação)",
        ),
        A(
            "ambiguidade",
            "“Código de inscrição” parece designar o Perfil, num vocabulário que o resto do edital não usa.",
            ["E92-152", "E92-185"],
            "Código de inscrição é o código do Perfil?",
        ),
        A(
            "lacuna",
            "Não se diz como comprovar residência, disponibilidade e habilidade com o Moodle nos Perfis em que não há documento pedido.",
            ["E92-137", "E92-138", "E92-139"],
            "Por declaração? Na análise documental?",
        ),
        A(
            "questão jurídica",
            "A cláusula de atendimento especializado sai na v2.",
            ["E92-179"],
            "Que norma assegura acessibilidade nesta seleção, e o edital precisa dizê-la?",
        ),
    ],
    perguntas=[
        P(
            "Sou mestre em Educação, graduado em Computação, e dei aula por dois anos no ensino superior. Posso concorrer ao TD-INFO-EDU?",
            "Sim: mestrado em qualquer área, graduação em Computação e um ano no magistério superior.",
            ["E92-032", "E92-033"],
        ),
        P(
            "Moro num município vizinho ao polo de Alegre. Posso concorrer ao TP-02?",
            "Sim: vale residir no município do polo ou em município limítrofe.",
            ["E92-137"],
        ),
        P(
            "Meu PDF tem 32 páginas. O que acontece?",
            "A inscrição é indeferida, sem possibilidade de recurso.",
            ["E92-154"],
        ),
        P(
            "Já recebo uma bolsa da CAPES. Posso me inscrever?",
            "Não, se o vínculo for no período de atuação.",
            ["E92-014", "E92-010"],
        ),
        P(
            "Concorro na modalidade PTT. Que documento a mais envio?",
            "A autodeclaração de identidade de gênero, no modelo do Anexo VI.",
            ["E92-173"],
        ),
        P(
            "Alguém confere meus documentos quando eu envio?",
            "Não: não há conferência no envio, e a responsabilidade é sua.",
            ["E92-153"],
        ),
    ],
    decisoes=[
        "Como organizar 18 Perfis em três grupos de requisitos sem perder as diferenças entre eles.",
        "Se o padrão do nome do arquivo aparece por escrito.",
        "Como apresentar documentos por Perfil e por modalidade.",
    ],
    reaproveitamento=dict(
        roteiro="Reaproveitável em seleções de bolsistas: requisitos gerais → requisitos por Perfil → canal e prazo → arquivo → limite → documentos por destinatário → dados exigidos.",
        solucao="Candidatas: limite de inscrições (LIB-0034), cabeçalhos de documentos (LIB-0035, LIB-0101, LIB-0041), ausência de conferência (LIB-0096), que é cláusula frequente nos editais reais.",
        gravacao="Os requisitos por Perfil mudam; a repetição interna (16 blocos TP) favorece um roteiro único, não necessariamente uma gravação única.",
    ),
)
N["E92"]["classificacao"] = dict(
    pergunta="Como minha nota é formada, quem segue para a próxima etapa e o que acontece num cadastro de reserva?",
    destinatarios="Inscritos de cada um dos 18 Perfis, separados por lista.",
    enunciados=[
        E(
            "CLA-92-01",
            "REGRA",
            "Cada Perfil tem a sua própria classificação e o seu próprio resultado.",
            ["E92-141", "E92-028", "E92-035", "E92-041"],
            alcance="Marco FINAL, impresso uma vez para os 18 Perfis (3.21).",
        ),
        E(
            "CLA-92-02",
            "REGRA",
            "A ordem é pela nota da prova de títulos (peso 1), sem normalização, com 2 casas decimais, arredondamento meio para cima; a nota final é a da prova depois dos recursos, em ordem decrescente por código de inscrição.",
            ["E92-142", "E92-143", "E92-144", "E92-181", "E92-184"],
        ),
        E(
            "CLA-92-03",
            "INFORMAÇÃO",
            "A prova de títulos é classificatória, vale até 100 pontos, tem uma avaliação por inscrição e ocorre de 05/11/2026 a 13/11/2026; os documentos pontuáveis seguem a ficha do Anexo IV.",
            ["E92-181", "E92-194", "E92-162"],
        ),
        E(
            "CLA-92-04",
            "REGRA",
            "Desempate, nesta ordem: quem nasceu antes (menor data de nascimento); quem tem mais meses de experiência em tutoria; maior pontuação na prova de títulos. Sem o dado, a pessoa fica por último no critério; no terceiro, o critério não se aplica.",
            ["E92-149", "E92-027"],
            nota="A paráfrase “quem nasceu antes” precisa de validação (LIB-0094).",
        ),
        E(
            "CLA-92-05",
            "REGRA",
            "Seguem para a análise documental dos requisitos os 10 primeiros, mais 5 suplentes; havendo empate na última posição, seguem todos os empatados.",
            ["E92-146", "E92-147"],
        ),
        E(
            "CLA-92-06",
            "CONDIÇÃO",
            "A análise documental dos requisitos é eliminatória (Habilitado ou Não habilitado), de 30/11/2026 a 04/12/2026.",
            ["E92-182", "E92-200"],
            consequencia="Não habilitado, a pessoa sai do processo (decorre do caráter eliminatório).",
        ),
        E(
            "CLA-92-07",
            "OBRIGAÇÃO",
            "Quem se autodeclara preto ou pardo passa por heteroidentificação, por comissão, por webconferência, considerando só características fenotípicas; a convocação individual sai por e-mail com 48 horas de antecedência; ocorre de 23/11/2026 a 25/11/2026.",
            ["E92-175", "E92-176", "E92-197"],
            destinatario="Autodeclarados pretos ou pardos",
        ),
        E(
            "CLA-92-08",
            "CONSEQUÊNCIA",
            "Quem não comparece à heteroidentificação é excluído da lista reservada e permanece na ampla concorrência.",
            ["E92-177"],
        ),
        E(
            "CLA-92-09",
            "INFORMAÇÃO",
            "Há vagas imediatas só nos dois Perfis de tutoria a distância (6 e 4); os 16 Perfis presenciais formam cadastro de reserva limitado a 15.",
            ["E92-017", "E92-018"],
        ),
        E(
            "CLA-92-10",
            "REGRA",
            "Vagas reservadas não preenchidas vão para a ampla concorrência do mesmo Perfil.",
            ["E92-019"],
        ),
        E(
            "CLA-92-11",
            "REGRA",
            "A seleção forma cadastro de reserva; a convocação depende da necessidade dos cursos, durante a validade do edital: 2 anos do resultado final, prorrogáveis uma vez.",
            ["E92-008", "E92-214"],
        ),
        E("CLA-92-12", "POSSIBILIDADE", "Pode haver chamada além do corte, na mesma ordem.", ["E92-148"]),
        E(
            "CLA-92-13",
            "PRAZO",
            "Resultado preliminar da prova em 16/11/2026; da heteroidentificação em 26/11/2026; da análise documental em 07/12/2026; resultado final e homologação em 15/12/2026.",
            ["E92-195", "E92-198", "E92-201", "E92-203"],
        ),
    ],
    ambiguidades=[
        A(
            "inconsistência",
            "O 3º critério de desempate é a pontuação na prova de títulos — a única Etapa que forma a nota. Se houve empate, essa pontuação também empata.",
            ["E92-149", "E92-144"],
            "O 3º critério pode decidir algum empate?",
        ),
        A(
            "ambiguidade",
            "“Ordem decrescente por código de inscrição” (texto livre) e a ordem por Perfil (marco).",
            ["E92-184", "E92-141"],
            "Por código de inscrição quer dizer por Perfil?",
        ),
        A(
            "ambiguidade",
            "Nos Perfis só de cadastro, o corte (10 + 5) coincide com o limite do cadastro (15), mas o edital não relaciona os dois.",
            ["E92-146", "E92-017"],
            "O cadastro é formado pelos que passam no corte?",
        ),
        A(
            "lacuna",
            "A modalidade PTT não tem percentual nem vaga na Tabela 2; não se diz como os candidatos dela são classificados e convocados.",
            ["E92-020", "E92-018"],
            "Como a lista PTT funciona?",
        ),
        A(
            "questão jurídica",
            "Os Perfis só de cadastro são convocados fora do sistema (aviso na submissão); o edital diz só “conforme a necessidade”.",
            ["E92-008"],
            "Qual é o critério e o meio da convocação desses Perfis?",
        ),
    ],
    perguntas=[
        P(
            "Empatei com outra pessoa na prova de títulos. Quem fica à frente?",
            "Quem nasceu antes; persistindo, quem tem mais meses de experiência em tutoria.",
            ["E92-149"],
            nota="O 3º critério não decide empate na mesma prova (ambiguidade registrada).",
        ),
        P(
            "Fiquei em 12º no TP-05. Sigo para a análise documental?",
            "Sim: seguem os 10 primeiros e mais 5 suplentes.",
            ["E92-146"],
        ),
        P("E se houver empate na 15ª posição?", "Seguem todos os empatados.", ["E92-147"]),
        P(
            "Não compareci à heteroidentificação. Fui eliminado?",
            "Não: você sai da lista reservada e permanece na ampla concorrência.",
            ["E92-177"],
        ),
        P(
            "O TP-07 não tem vaga imediata. Por que me inscrever?",
            "Porque a seleção forma cadastro de reserva: a convocação depende da necessidade dos cursos, durante 2 anos, prorrogáveis.",
            ["E92-008", "E92-214"],
        ),
    ],
    decisoes=[
        "Como explicar o desempate sem paráfrase não validada.",
        "Como relacionar a sequência de resultados preliminares, recursos e resultado final.",
    ],
    reaproveitamento=dict(
        roteiro="Reaproveitável em seleções por pontuação com cadastro de reserva: formação da nota → desempate → corte e empate → análise documental → verificação → cadastro e validade.",
        solucao="Frases do sistema já vistas noutro edital: marcos por Perfil (LIB-0023), ordem por pontuação (LIB-0090), empate com excedente (LIB-0093), continuação (LIB-0030).",
        gravacao="O bloco do corte depende de N, suplentes e Etapa — variáveis de condição; a gravação do 01/2026 não serve sem nova análise.",
    ),
)
N["E92"]["recurso"] = dict(
    pergunta="Quero contestar uma decisão — ou o próprio edital: contra o quê, até quando, por onde, e o que não posso fazer?",
    destinatarios="Qualquer interessado (impugnação); inscritos afetados por cada resultado (recursos).",
    enunciados=[
        E(
            "REC-92-01",
            "PRAZO",
            "Impugnar o edital de 10/10/2026, às 00h, a 13/10/2026, às 23h59, pelo formulário eletrônico na página do certame.",
            ["E92-189"],
            variante="Contra o próprio edital (impugnação)",
        ),
        E(
            "REC-92-02",
            "PRAZO",
            "Contra a homologação preliminar das inscrições (30/10/2026): de 31/10/2026 a 02/11/2026, às 23h59.",
            ["E92-191", "E92-192"],
            variante="Contra a homologação preliminar das inscrições",
        ),
        E(
            "REC-92-03",
            "PRAZO",
            "Contra o resultado preliminar da prova de títulos (16/11/2026): de 17/11/2026 a 19/11/2026, às 23h59.",
            ["E92-195", "E92-196"],
            variante="Contra o resultado preliminar da prova de títulos",
        ),
        E(
            "REC-92-04",
            "PRAZO",
            "Contra o resultado do marco “Classificação final pela prova de títulos”: 3 dias corridos, contados da divulgação desse resultado.",
            ["E92-145"],
            variante="Contra o resultado do marco classificatório",
            nota="Pode ser o mesmo recurso do item anterior (ambiguidade).",
        ),
        E(
            "REC-92-05",
            "PRAZO",
            "Contra o resultado preliminar da heteroidentificação (26/11/2026): de 27/11/2026 a 28/11/2026, às 23h59.",
            ["E92-198", "E92-199"],
            variante="Contra o resultado preliminar da heteroidentificação",
        ),
        E(
            "REC-92-06",
            "PRAZO",
            "Contra o resultado preliminar da análise documental (07/12/2026): de 08/12/2026 a 10/12/2026, às 23h59.",
            ["E92-201", "E92-202"],
            variante="Contra o resultado preliminar da análise documental",
        ),
        E(
            "REC-92-07",
            "OBRIGAÇÃO",
            "Todo recurso se interpõe só pelo formulário eletrônico de recursos, cujo link fica na página do processo, nos prazos do Cronograma.",
            ["E92-207"],
            variante="Regras comuns aos recursos",
        ),
        E(
            "REC-92-08",
            "PROIBIÇÃO",
            "Não se admite envio de documentos na fase recursal.",
            ["E92-208"],
            variante="Regras comuns aos recursos",
        ),
        E(
            "REC-92-09",
            "PROIBIÇÃO",
            "Não se aceitam recursos por Correios, e-mail ou outra forma diferente da prevista no item 11.1.",
            ["E92-209"],
            variante="Regras comuns aos recursos",
            nota="Na v2, o “item 11.1” deixa de ser o dos recursos (retificacoes.md).",
        ),
        E(
            "REC-92-10",
            "PROIBIÇÃO",
            "Indeferimento por excesso de páginas não admite recurso.",
            ["E92-154"],
            variante="Exceção expressa",
        ),
    ],
    ambiguidades=[
        A(
            "ambiguidade",
            "O recurso do marco (3 dias da divulgação) e o Evento 9 (17 a 19/11, contra o resultado preliminar da prova) podem ser o mesmo recurso, ou dois.",
            ["E92-145", "E92-196"],
            "São o mesmo recurso?",
        ),
        A(
            "inconsistência",
            "Na v2, a remissão “item 11.1” aponta para a seção da convocação (renumerada), e não para a dos recursos.",
            ["E92-209"],
            "Corrigir em nova Retificação? (decisão da área)",
        ),
        A(
            "lacuna",
            "Não se diz se cabe recurso contra o resultado final.",
            ["E92-203"],
            "Há recurso contra o resultado final? (ausência de cláusula não é proibição)",
        ),
    ],
    perguntas=[
        P(
            "Minha inscrição não foi homologada. Até quando recorro, e por onde?",
            "De 31/10/2026 a 02/11/2026, às 23h59, pelo formulário eletrônico de recursos.",
            ["E92-192", "E92-207"],
        ),
        P(
            "Posso juntar um certificado novo ao recurso contra a nota dos títulos?",
            "Não: não se admite envio de documentos na fase recursal.",
            ["E92-208"],
        ),
        P(
            "Minha inscrição foi indeferida por ter 35 páginas. Posso recorrer?",
            "O edital diz que não: é exceção expressa.",
            ["E92-154"],
        ),
        P(
            "Discordo de uma regra do edital. O que faço?",
            "Pode impugná-lo de 10/10/2026 a 13/10/2026, pelo formulário eletrônico na página do certame.",
            ["E92-189"],
        ),
        P("Posso mandar o recurso pelos Correios?", "Não.", ["E92-209"]),
    ],
    decisoes=[
        "Como apresentar seis objetos de contestação sem fundi-los.",
        "Como comunicar a exceção expressa (sem recurso) ao lado da regra geral.",
    ],
    reaproveitamento=dict(
        roteiro="As regras comuns (canal, sem documentos, vedações) e a lista de objetos com prazos formam um roteiro aplicável a muitos editais.",
        solucao="Regras comuns de canal e vedação são frequentes nos editais reais (sondagem); a solução se aproveita onde a regra for a mesma — aqui ela é mais ampla que no 91 (LIB-0149 × LIB-0133).",
        gravacao="Cada objeto tem datas próprias; as regras comuns, se idênticas noutro edital, são as candidatas.",
    ),
)

# ═════════════════════════════════════════════════════════════════════════════════════════════════
# 01/2026 — Professor e técnico (seed_demo), sem seções textuais
# ═════════════════════════════════════════════════════════════════════════════════════════════════
N["E01"] = {}
N["E01"]["inscricao"] = dict(
    pergunta="Posso concorrer a professor de Informática ou a técnico de laboratório, e o que preciso fazer?",
    destinatarios="Candidatos aos Perfis DOC-INFO (2 vagas; 3 desde a Retificação a) e TEC-LAB (cadastro de reserva).",
    enunciados=[
        E(
            "INS-01-01",
            "CONDIÇÃO",
            "DOC-INFO: mestrado em Computação ou área afim. TEC-LAB: curso técnico em Informática.",
            ["E01-011", "E01-021"],
            destinatario="Conforme o Perfil",
        ),
        E(
            "INS-01-02",
            "PRAZO",
            "Inscrições de 11/10/2026 a 31/10/2026 (às 09h43).",
            ["E01-043"],
            prazo="Até 31/10/2026 (v1 e v2); até 10/11/2026 pela Retificação b (v3), com vigência a partir de 26/10/2026.",
            nota="A descrição do Evento diz “pelo sistema”; não há outra menção ao canal.",
        ),
        E(
            "INS-01-03",
            "REGRA",
            "Há isenção de taxa até o 5º dia.",
            ["E01-043"],
            nota="Regra só na descrição do Evento (LIB-0152); o edital não diz se há taxa, quanto, nem como se pede a isenção.",
        ),
        E(
            "INS-01-04",
            "CONDIÇÃO",
            "Cada pessoa pode ter apenas 1 inscrição enviada.",
            ["E01-029"],
            destinatario="Todos",
        ),
        E(
            "INS-01-05",
            "OBRIGAÇÃO",
            "Enviar documento de identificação com foto, frente e verso, em arquivo único.",
            ["E01-031", "E01-032"],
            destinatario="Todos",
        ),
        E(
            "INS-01-06",
            "OBRIGAÇÃO",
            "Enviar diploma de graduação, ou certidão de conclusão com histórico.",
            ["E01-033", "E01-034"],
            destinatario="Candidatos ao DOC-INFO",
        ),
        E(
            "INS-01-07",
            "OBRIGAÇÃO",
            "Enviar autodeclaração étnico-racial, no modelo do Anexo do Edital.",
            ["E01-035", "E01-036", "E01-050"],
            destinatario="Quem concorre na modalidade PPP (só no DOC-INFO)",
        ),
        E(
            "INS-01-08",
            "OBRIGAÇÃO",
            "Informar meses de experiência na área e data de nascimento.",
            ["E01-012"],
            destinatario="Candidatos ao DOC-INFO",
        ),
        E(
            "INS-01-09",
            "OBRIGAÇÃO",
            "Enviar o Requerimento de Matrícula na inscrição, declarando, sob as penas da lei, que as informações são verdadeiras.",
            ["E01-047", "E01-048"],
            destinatario="Todos",
            consequencia="A inexatidão ou a falsidade de qualquer informação cancela a matrícula, a qualquer tempo.",
        ),
    ],
    ambiguidades=[
        A(
            "lacuna",
            "Não há seção textual de inscrição: o canal só aparece como “pelo sistema” na descrição do Evento.",
            ["E01-043", "E01-028"],
            "Qual é o canal, e onde está o sistema?",
        ),
        A(
            "lacuna",
            "A regra de taxa está só na descrição do Evento.",
            ["E01-043"],
            "Há taxa? Quem é isento? “5º dia” contado de quando?",
        ),
        A(
            "lacuna",
            "O TEC-LAB exige curso técnico, mas nenhum documento comprova o requisito.",
            ["E01-021", "E01-031"],
            "Como se comprova o curso técnico?",
        ),
        A(
            "ambiguidade",
            "“Conforme o modelo do Anexo do Edital” não diz qual dos dois anexos.",
            ["E01-036", "E01-050"],
            "É o Anexo I?",
        ),
        A(
            "questão jurídica",
            "Seleção de professor substituto (Lei nº 8.745/1993, art. 2º, IV, e art. 3º): o Decreto nº 9.508/2018 assegura reserva e tratamento diferenciado a quem o requerer na inscrição (art. 4º, § 1º). O edital não traz cláusula sobre isso.",
            [],
            "O formulário oferece o pedido de tratamento diferenciado, e o edital deveria dizê-lo?",
        ),
    ],
    perguntas=[
        P(
            "Até quando posso me inscrever?",
            "Até 31/10/2026. Pela Retificação b, publicada em 11/10 e vigente a partir de 26/10/2026, o prazo passa a 10/11/2026.",
            ["E01-043"],
            nota="A resposta depende da data da consulta.",
        ),
        P(
            "Vou concorrer ao TEC-LAB. Que documentos envio?",
            "Só o documento de identificação com foto e o Requerimento de Matrícula.",
            ["E01-031", "E01-032", "E01-047"],
        ),
        P(
            "Para o DOC-INFO, posso enviar a certidão de conclusão em vez do diploma?",
            "Sim, com o histórico.",
            ["E01-034"],
        ),
        P(
            "Preciso pagar taxa?",
            "O edital diz só que há isenção de taxa até o 5º dia; não diz o valor nem como pedir.",
            ["E01-043"],
        ),
    ],
    decisoes=["Como tratar regras que só aparecem na descrição de um Evento."],
    reaproveitamento=dict(
        roteiro="O mesmo esquema do 91 e do 92, com menos conteúdo: sem seção textual, a narrativa se monta só com a estrutura do sistema.",
        solucao="Limite de inscrições (LIB-0034), cabeçalhos de documentos (LIB-0035, LIB-0101, LIB-0041) e momento do Requerimento (LIB-0064), com texto idêntico ao dos outros editais.",
        gravacao="Os trechos de texto fixo são os mesmos do 91 e do 92; se a gravação serve depende do contexto em que entram.",
    ),
)
N["E01"]["classificacao"] = dict(
    pergunta="Como se forma a nota e quem segue adiante em cada Perfil?",
    destinatarios="Inscritos do DOC-INFO e do TEC-LAB, cada Perfil com regra própria.",
    enunciados=[
        E(
            "CLA-01-01",
            "REGRA",
            "Nos dois Perfis, a ordem é pela soma ponderada da prova objetiva (peso 2) e da análise de títulos (peso 1), sem normalização, com 2 casas decimais, meio para cima.",
            ["E01-014", "E01-015", "E01-023", "E01-024"],
        ),
        E(
            "CLA-01-02",
            "CONDIÇÃO",
            "A prova objetiva é eliminatória e classificatória, com nota mínima 6, em 15/11/2026.",
            ["E01-038", "E01-044"],
            consequencia="Abaixo da nota mínima, eliminação — decorre de “eliminatória” com “nota mínima”; não está escrito por extenso.",
        ),
        E("CLA-01-03", "INFORMAÇÃO", "A análise de títulos é classificatória (peso 1); não tem data.", ["E01-039"]),
        E(
            "CLA-01-04",
            "REGRA",
            "DOC-INFO: seguem para a análise documental os 2 primeiros, mais 1 suplente; com empate na última posição, a quantidade não é excedida; não haverá chamada além do corte.",
            ["E01-017", "E01-018", "E01-019"],
            variante="DOC-INFO",
        ),
        E(
            "CLA-01-05",
            "CONDIÇÃO",
            "A análise documental é eliminatória (Deferido ou Indeferido); não tem data.",
            ["E01-040"],
            variante="DOC-INFO",
        ),
        E(
            "CLA-01-06",
            "REGRA",
            "TEC-LAB: seguem os 3 primeiros; com empate na última posição, seguem todos os empatados; não haverá chamada além.",
            ["E01-025", "E01-026", "E01-027"],
            variante="TEC-LAB",
            nota="O corte não diz para onde se segue: o marco não governa Etapa.",
        ),
        E(
            "CLA-01-07",
            "INFORMAÇÃO",
            "Vagas: DOC-INFO 2 (1 ampla, 1 PPP), cadastro limitado a 6; TEC-LAB 0, cadastro ilimitado. Desde a Retificação a, DOC-INFO 3 (2 ampla, 1 PPP).",
            ["E01-005", "E01-006", "E01-007", "E01-008"],
        ),
        E("CLA-01-08", "INFORMAÇÃO", "A convocação é por mensagem individual.", ["E01-009"]),
        E("CLA-01-09", "PRAZO", "Resultado final em 10/12/2026.", ["E01-045"]),
    ],
    ambiguidades=[
        A(
            "lacuna",
            "Não há critério de desempate, e o empate no corte do DOC-INFO “não excede a quantidade”: não se diz quem fica.",
            ["E01-018", "E01-013"],
            "Como se resolve o empate na 3ª posição do DOC-INFO?",
        ),
        A(
            "inconsistência",
            "Desde a Retificação a, o DOC-INFO tem 3 vagas, mas o corte continua em 2 + 1 suplente e não há continuação.",
            ["E01-017", "E01-019", "E01-005"],
            "A terceira vaga se preenche como?",
        ),
        A(
            "ambiguidade",
            "No TEC-LAB, o cadastro é ilimitado, mas o corte é de 3.",
            ["E01-025", "E01-005"],
            "O cadastro de reserva tem só 3 pessoas?",
        ),
    ],
    perguntas=[
        P(
            "Tirei 5,5 na prova objetiva. Continuo?",
            "A prova é eliminatória com nota mínima 6; abaixo dela, a eliminação decorre dessas duas informações, embora o edital não a escreva por extenso.",
            ["E01-038"],
            nota="Pergunta que testa uma consequência implícita.",
        ),
        P(
            "Como se calcula a minha nota?",
            "Duas vezes a nota da prova objetiva, mais a nota dos títulos, com 2 casas decimais.",
            ["E01-015"],
        ),
        P(
            "Fiquei em 3º no DOC-INFO. Meus documentos serão analisados?",
            "Sim: seguem os 2 primeiros e mais 1 suplente.",
            ["E01-017"],
        ),
        P(
            "Empatei na 3ª posição do TEC-LAB. Sigo?",
            "Sim: no TEC-LAB, todos os empatados na última posição seguem.",
            ["E01-026"],
        ),
    ],
    decisoes=["Como contrastar duas regras de empate opostas no mesmo edital."],
    reaproveitamento=dict(
        roteiro="Dois Perfis, duas regras: o roteiro precisa da variante por Perfil, como o de recurso do 91 precisa da variante por objeto.",
        solucao="As frases de empate e continuação existem nas duas espécies (LIB-0093 × LIB-0123; LIB-0030 × LIB-0124): o contraste é teste natural de solução padronizada.",
        gravacao="O corte (LIB-0092) muda N, suplentes e Etapa entre os dois Perfis — variáveis de condição.",
    ),
)
N["E01"]["recurso"] = dict(
    pergunta="Discordo do resultado: posso recorrer, até quando, e por onde?",
    destinatarios="Inscritos de cada Perfil.",
    enunciados=[
        E(
            "REC-01-01",
            "PRAZO",
            "DOC-INFO: recurso contra o resultado de “Classificação final” em 5 dias corridos, contados da divulgação desse resultado (previsto para 10/12/2026).",
            ["E01-016", "E01-045"],
            variante="DOC-INFO — contra a classificação final",
        ),
        E(
            "REC-01-02",
            "AUSÊNCIA",
            "TEC-LAB: o marco não declara prazo de recurso, e o edital nada diz.",
            ["E01-022"],
            variante="TEC-LAB",
            nota="Ausência de cláusula não é proibição; a negativa expressa seria impressa se declarada. Se vias legais fora do edital se aplicam (Lei nº 9.784/1999, arts. 56 a 59) é questão jurídica.",
        ),
        E(
            "REC-01-03",
            "INFORMAÇÃO",
            "O Cronograma anuncia o “resultado final e abertura do prazo recursal” em 10/12/2026, sem dizer contra o quê nem até quando.",
            ["E01-045"],
            variante="Os dois Perfis",
            nota="Regra embutida na descrição do Evento (LIB-0153).",
        ),
    ],
    ambiguidades=[
        A(
            "lacuna",
            "Não há seção Dos Recursos: não se diz o canal, nem vedações.",
            ["E01-016"],
            "Por onde se recorre?",
        ),
        A(
            "ambiguidade",
            "A abertura de prazo recursal no Evento 3 vale para os dois Perfis, ou só para o DOC-INFO?",
            ["E01-045", "E01-022"],
            "O TEC-LAB tem recurso?",
        ),
        A(
            "questão jurídica",
            "Silêncio do marco do TEC-LAB.",
            ["E01-022"],
            "Aplica-se o recurso administrativo da Lei nº 9.784/1999?",
        ),
    ],
    perguntas=[
        P(
            "Sou do DOC-INFO e discordo da classificação final. Até quando posso recorrer?",
            "Por 5 dias corridos, contados da divulgação do resultado, prevista para 10/12/2026.",
            ["E01-016", "E01-045"],
        ),
        P(
            "Sou do TEC-LAB. Posso recorrer?",
            "O edital não declara prazo para o TEC-LAB, e também não diz que não cabe. O Cronograma anuncia abertura de prazo recursal sem dizer para quem.",
            ["E01-022", "E01-045"],
            nota="Testa a distinção entre ausência e proibição.",
        ),
        P("Por onde envio o recurso?", "O edital não diz.", ["E01-016"]),
    ],
    decisoes=["Como comunicar o que o edital não diz sem afirmar que não existe."],
    reaproveitamento=dict(
        roteiro="O mesmo esquema do 91 e do 92; aqui, a parte “o que o edital não diz” é a maior.",
        solucao="A frase de recurso do marco (LIB-0028) com outro prazo e outro nome: variáveis de condição.",
        gravacao="Pouco provável.",
    ),
)

# ═════════════════════════════════════════════════════════════════════════════════════════════════
# RODADA 3 — editais REAIS. As sínteses dizem o que o documento oficial diz, inclusive quando ele se
# contradiz: a contradição vai para as ambiguidades, e a resposta esperada a registra sem resolvê-la.
# ═════════════════════════════════════════════════════════════════════════════════════════════════

# 28/2026 — Pós-graduação lato sensu em Informática na Educação, EaD, sete polos, cotas, sorteio
N["E28"] = {}
N["E28"]["inscricao"] = dict(
    pergunta="Quero fazer a especialização em Informática na Educação, a distância: posso me inscrever, como, até quando, o que envio e o que pode invalidar a inscrição?",
    destinatarios="Pessoas graduadas em qualquer área — ou que colarão grau antes do início do curso — que queiram uma vaga num dos sete polos; com documentos a mais para quem concorre às vagas PPI (e, entre elas, os indígenas) e PcD.",
    enunciados=[
        E("INS-28-01", "CONDIÇÃO", "Ter diploma de graduação (bacharelado, licenciatura ou tecnologia) reconhecido pelo MEC, acesso a computador com internet e conhecimentos intermediários de Informática; ler o edital.",
          ["E28-013", "E28-015", "E28-016", "E28-017", "E28-018"], destinatario="Todos",
          nota="Não se diz como se comprova o nível intermediário de Informática."),
        E("INS-28-02", "POSSIBILIDADE", "Quem ainda não colou grau pode se inscrever com declaração da instituição, reconhecida pelo MEC, com a data da colação, que deve ser anterior ao início do curso.",
          ["E28-056", "E28-039"], destinatario="Quem ainda não colou grau",
          consequencia="Fica obrigado a comprovar o término da graduação.", prazo="Até 30 dias após o início do curso (E28-057)."),
        E("INS-28-03", "OBRIGAÇÃO", "Inscrever-se pelo link nas páginas do Cefor ou do Ifes, só pela internet, passando pelo cadastro no Gov.br (criar a conta ou atualizar os dados).",
          ["E28-032", "E28-030"], destinatario="Todos"),
        E("INS-28-04", "CONDIÇÃO", "O e-mail do cadastro no Gov.br precisa estar todo em letras minúsculas.",
          ["E28-031"], destinatario="Todos", consequencia="Sem isso, não é possível se inscrever."),
        E("INS-28-05", "PRAZO", "As inscrições vão até 06/05/2026, às 23h59 (Brasília); depois, o sistema não aceita novas inscrições.",
          ["E28-166", "E28-032"], destinatario="Todos", prazo="Início escrito “07/04/2025” no Cronograma; término 06/05/2026, 23h59.",
          nota="O edital foi publicado em 07/04/2026 (E28-165); o ano do início diverge."),
        E("INS-28-06", "OBRIGAÇÃO", "Assinalar o curso e uma só modalidade de vaga (código de vaga) — ampla concorrência, PPI ou PcD —, num dos sete polos.",
          ["E28-033", "E28-024", "E28-020", "E28-027"], destinatario="Todos",
          alcance="Cada polo tem 40 vagas: 28 de ampla concorrência, 10 PPI e 2 PcD (Quadro 2)."),
        E("INS-28-07", "REGRA", "Quem concorre a vaga reservada concorre ao mesmo tempo à ampla concorrência.",
          ["E28-026", "E28-106"], destinatario="Candidatos às vagas PPI e PcD"),
        E("INS-28-08", "OBRIGAÇÃO", "Enviar, cada um no seu campo do formulário, em PDF de até 7 MB, digitalizado do original, nítido e sem cortes: identidade (frente e verso), CPF, comprovante de votação de 2024 ou certidão de quitação eleitoral, certidão de nascimento ou casamento, diploma (ou declaração de conclusão com histórico, ou de colação), documento militar (homens) e o Requerimento de Matrícula (Anexo II) preenchido, com a declaração de veracidade marcada.",
          ["E28-034", "E28-035", "E28-036", "E28-037", "E28-038", "E28-039", "E28-040", "E28-041", "E28-183", "E28-185"],
          destinatario="Todos", consequencia="Requerimento incompleto ou incorreto indefere o candidato (E28-041)."),
        E("INS-28-09", "OBRIGAÇÃO", "Enviar também a autodeclaração étnico-racial (Anexo III), preenchida.",
          ["E28-042", "E28-187", "E28-188", "E28-189"], destinatario="Candidatos às vagas PPI", variante="Documentos a mais, por lista"),
        E("INS-28-10", "OBRIGAÇÃO", "Enviar também a declaração de pertencimento da comunidade (Anexo V), assinada pelo cacique ou vice e por duas lideranças, com contatos, e a declaração da Funai ou o comprovante de residência em comunidade indígena — tudo no ato da inscrição.",
          ["E28-043", "E28-044", "E28-091", "E28-195"], destinatario="Candidatos indígenas", variante="Documentos a mais, por lista"),
        E("INS-28-11", "OBRIGAÇÃO", "Enviar também o laudo de médico especialista, com espécie e grau da deficiência e o CID, e a autodeclaração de pessoa com deficiência (Anexo IV).",
          ["E28-045", "E28-046", "E28-191", "E28-193"], destinatario="Candidatos às vagas PcD", variante="Documentos a mais, por lista"),
        E("INS-28-12", "OBRIGAÇÃO", "Documento emitido fora do Brasil vai com tradução juramentada; diploma estrangeiro, revalidado.",
          ["E28-047", "E28-048"], destinatario="Quem tem documento estrangeiro"),
        E("INS-28-13", "OBRIGAÇÃO", "Ler o termo de consentimento de dados pessoais (Anexo VI) e marcar a opção no formulário.",
          ["E28-058", "E28-196", "E28-197", "E28-198"], destinatario="Todos",
          alcance="Não consentir não anula o direito à matrícula (E28-206)."),
        E("INS-28-14", "OBRIGAÇÃO", "Clicar em “confirmar inscrição”, no fim do formulário, para a inscrição valer.",
          ["E28-049", "E28-050"], destinatario="Todos"),
        E("INS-28-15", "PROIBIÇÃO", "Inscrição e documentos por e-mail não são aceitos.", ["E28-059"], destinatario="Todos"),
        E("INS-28-16", "CONSEQUÊNCIA", "Inscrição com dados incompletos, arquivo anexado incorretamente ou com problema técnico que impeça abri-lo é indeferida, sem possibilidade de recurso.",
          ["E28-051"], destinatario="Todos", alcance="Proibição expressa de recurso.", variante="O que invalida a inscrição"),
        E("INS-28-17", "CONSEQUÊNCIA", "Inscrição é indeferida se os documentos estiverem fora do PDF, incompletos, ilegíveis, cortados, desatualizados, rasurados ou vencidos.",
          ["E28-053", "E28-052"], destinatario="Todos", variante="O que invalida a inscrição"),
        E("INS-28-18", "INFORMAÇÃO", "As informações são de responsabilidade do candidato, sob as penas da lei; o Cefor não responde por erro de preenchimento nem por falha técnica ou de comunicação.",
          ["E28-054", "E28-055"], destinatario="Todos", variante="O que invalida a inscrição"),
        E("INS-28-19", "CONDIÇÃO", "Inscrever-se é estar de acordo com o edital e aceitar as suas condições, sem poder alegar desconhecimento.",
          ["E28-029", "E28-155"], destinatario="Todos"),
        E("INS-28-20", "INFORMAÇÃO", "Dúvidas “exclusivamente” pelo e-mail da seleção ou pelo WhatsApp, das 8h às 17h.",
          ["E28-008"], destinatario="Todos"),
    ],
    ambiguidades=[
        A("contradição", "O 5.7 diz que os documentos vão “em um único arquivo pdf”; o 5.4 diz um arquivo no campo de cada documento; o 5.8 repete o 5.7 sem a menção.",
          ["E28-049", "E28-034", "E28-050"], "Um arquivo por documento ou um arquivo único?"),
        A("erro material", "O Cronograma escreve o início das inscrições como “07/04/2025”.", ["E28-166", "E28-165"], "O início é 07/04/2026?"),
        A("remissão", "O 4.2.3 remete ao “quadro 2 do item 4.5”; o quadro está no 4.4.", ["E28-024", "E28-027"], "Confirmar a remissão."),
        A("remissão", "O 6.10.2 pede a documentação “dos itens 5.2 e 6”; os documentos do indígena estão no 5.4, alínea i.", ["E28-091", "E28-043"], "Confirmar a remissão."),
        A("lacuna", "Não se diz como se comprova o conhecimento intermediário de Informática, nem o que acontece se a colação não for comprovada em 30 dias.",
          ["E28-018", "E28-057"], "Há verificação? Qual a consequência?"),
        A("acessibilidade", "O edital não prevê canal acessível nem atendimento específico durante a inscrição; o Napne só entra depois da classificação, para o candidato PcD.",
          ["E28-008", "E28-149"], "Há atendimento em Libras para dúvidas na inscrição? (questão para a área)"),
    ],
    perguntas=[
        P("Ainda não colei grau. Posso me inscrever?", "Sim, com declaração da instituição com a data da colação, que deve ser antes do início do curso; o término se comprova em até 30 dias após o início.", ["E28-056", "E28-057"]),
        P("O e-mail do meu cadastro no Gov.br tem letras maiúsculas. Isso importa?", "Sim: tem de estar todo em minúsculas, senão não é possível se inscrever.", ["E28-031"]),
        P("Posso mandar os documentos por e-mail?", "Não.", ["E28-059"]),
        P("Anexei um arquivo que não abre, e a inscrição foi indeferida. Posso recorrer?", "Não: o edital diz que não há possibilidade de recurso.", ["E28-051"]),
        P("Sou candidato indígena. O que envio além dos documentos de todos?", "A autodeclaração (Anexo III), a declaração da comunidade (Anexo V) e a declaração da Funai ou o comprovante de residência em comunidade indígena, tudo na inscrição.",
          ["E28-042", "E28-043", "E28-044", "E28-091"]),
        P("Se eu não consentir com o tratamento dos meus dados, perco a vaga?", "Não: o termo diz que não consentir não anula o direito à matrícula.", ["E28-206"]),
        P("Os documentos vão num arquivo só ou separados?", "O edital diz as duas coisas (5.4 e 5.7); a pergunta é para a área.", ["E28-034", "E28-049"],
          nota="Testa se a contradição foi comunicada sem ser resolvida."),
    ],
    decisoes=[
        "Como apresentar os documentos por destinatário (todos, PPI, indígenas, PcD) sem que quem concorre à ampla concorrência entenda que precisa de tudo.",
        "Como tratar as contradições do original — arquivo único × um por campo; o ano de 2025 — até a área responder: traduzir o texto, sinalizar a divergência ou esperar a correção.",
        "Os anexos são formulários: decidir se a tradução explica campo a campo ou diz o que cada formulário é e para que serve.",
    ],
    reaproveitamento=dict(
        roteiro="O esquema requisitos → canal e prazo → documentos por destinatário → causas de indeferimento é o mesmo do 91/2026; os itens mudam.",
        solucao="Formato do envio, identidade, documento militar e causas de indeferimento (LIB-0178, LIB-0193, LIB-0198, LIB-0184, LIB-0186) têm o mesmo texto, ou quase, no 59/2026: candidatas a solução comum, a validar.",
        gravacao="Possível só nos blocos de texto idêntico entre 28 e 59, se a sequência e o contexto permitirem; não em requisitos, prazos e documentos de cotas.",
    ),
)

N["E28"]["classificacao"] = dict(
    pergunta="Como se decide quem fica com as vagas, e o que pode me tirar da lista?",
    destinatarios="Inscritos habilitados ao sorteio; regras a mais para os candidatos às vagas PPI (pretos e pardos, por entrevista; indígenas, por documentos) e PcD.",
    enunciados=[
        E("CLA-28-01", "REGRA", "Se houver mais inscritos do que vagas, as vagas se preenchem por sorteio eletrônico; acompanhar o sorteio não é obrigatório.",
          ["E28-099", "E28-100"], destinatario="Todos", variante="Sorteio"),
        E("CLA-28-02", "CONDIÇÃO", "Só entram no sorteio as inscrições com dados completos e a documentação do 5.4; a lista dos habilitados, com o número de cada um, sai dois dias antes do sorteio.",
          ["E28-103", "E28-168"], destinatario="Todos", prazo="Lista em 08/05/2026; sorteio em 11/05/2026.", variante="Sorteio"),
        E("CLA-28-03", "INFORMAÇÃO", "Dois servidores fazem o sorteio, on-line, transmitido no canal do Cefor no YouTube e gravado; para auditoria, a “semente” fica no fim da página do sorteio.",
          ["E28-104", "E28-101", "E28-169", "E28-170"], destinatario="Todos", prazo="11/05/2026, às 10h; link em 08/05/2026.", variante="Sorteio"),
        E("CLA-28-04", "REGRA", "Primeiro se sorteia a ampla concorrência, com todos os inscritos, inclusive os cotistas; depois, as vagas reservadas.",
          ["E28-106"], destinatario="Todos", variante="Sorteio"),
        E("CLA-28-05", "REGRA", "Cotista sorteado dentro das vagas nas duas listas fica na ampla concorrência, e não conta nas reservadas: a vaga reservada passa ao próximo autodeclarado. Se um sorteado em vaga reservada desistir, também.",
          ["E28-107", "E28-108"], destinatario="Candidatos às vagas PPI e PcD", variante="Sorteio"),
        E("CLA-28-06", "REGRA", "Depois do sorteio, analisam-se os documentos dos primeiros sorteados, até o número de vagas; documentação incompleta ou incorreta indefere a inscrição, e analisa-se o próximo da ordem.",
          ["E28-102", "E28-105", "E28-171", "E28-172"], destinatario="Sorteados", prazo="Classificação preliminar em 12/05/2026; resultado preliminar da análise em 08/06/2026.",
          variante="Análise da documentação"),
        E("CLA-28-07", "OBRIGAÇÃO", "Participar da entrevista de verificação por videoconferência, quando convocado, com documento original com foto, equipamento com câmera e microfone, boa iluminação, roupa sem estampa, sem boné ou acessório e sem maquiagem, entrando na sala até 5 minutos antes. A entrevista é gravada.",
          ["E28-070", "E28-073", "E28-074", "E28-075", "E28-076", "E28-077", "E28-078", "E28-085", "E28-175", "E28-176"],
          destinatario="Candidatos autodeclarados pretos ou pardos", prazo="Convocação em 12/06/2026; entrevistas de 15/06 a 02/07/2026.",
          alcance="Menor de 18 anos com o responsável; sem ele, com um servidor (E28-071, E28-072).", variante="Verificação da autodeclaração"),
        E("CLA-28-08", "REGRA", "A comissão considera só as características fenotípicas, e não a ascendência.", ["E28-086"],
          destinatario="Candidatos autodeclarados pretos ou pardos", variante="Verificação da autodeclaração"),
        E("CLA-28-09", "REGRA", "Falha do candidato na conexão: três tentativas, e a entrevista fica pendente; tirar print da tela e mandar justificativa por e-mail em até 24 horas. Só há nova convocação com essa justificativa. Queda de mais de 10 minutos cancela a entrevista; se a falha for do sistema, ela é reagendada.",
          ["E28-081", "E28-082", "E28-083", "E28-084"], destinatario="Candidatos autodeclarados pretos ou pardos", variante="Verificação da autodeclaração"),
        E("CLA-28-10", "CONSEQUÊNCIA", "A autodeclaração é indeferida se o formulário estiver incorreto, se o candidato não comparecer, recusar as orientações ou a filmagem, ou se a comissão, por unanimidade, não constatar as características fenotípicas.",
          ["E28-087"], destinatario="Candidatos autodeclarados pretos ou pardos", variante="Verificação da autodeclaração"),
        E("CLA-28-11", "CONSEQUÊNCIA", "Quem não comparece à comissão, ou tem a autodeclaração indeferida, não ocupa vaga reservada e permanece só na ampla concorrência.",
          ["E28-109", "E28-088"], destinatario="Candidatos autodeclarados pretos ou pardos",
          alcance="O 6.9.15 diz isso só do indeferimento por fenótipo; o 8.10, de qualquer indeferimento e da ausência.", variante="Verificação da autodeclaração"),
        E("CLA-28-12", "REGRA", "A verificação do candidato indígena é por análise documental, pela comissão local; o resultado sai em listagem. É indeferida se o formulário estiver incorreto, se faltarem documentos ou se houver fraude.",
          ["E28-090", "E28-092", "E28-093", "E28-177"], destinatario="Candidatos indígenas", prazo="Resultado preliminar em 03/07/2026.", variante="Verificação da autodeclaração"),
        E("CLA-28-13", "REGRA", "Uma equipe multiprofissional verifica se o candidato é elegível à vaga de pessoa com deficiência, pelas categorias da lei.",
          ["E28-096", "E28-095", "E28-097"], destinatario="Candidatos às vagas PcD", variante="Verificação da pessoa com deficiência"),
        E("CLA-28-14", "AUSÊNCIA", "O edital não diz quando nem como acontece a verificação da pessoa com deficiência, nem o que acontece com quem for considerado não elegível.",
          ["E28-096"], destinatario="Candidatos às vagas PcD", variante="Verificação da pessoa com deficiência",
          nota="O 8.10, que mantém na ampla concorrência, fala só de pretos e pardos."),
        E("CLA-28-15", "OBRIGAÇÃO", "O candidato PcD classificado participa de entrevista com o Napne antes do início do curso, para identificar o atendimento específico de que precisa; se o Napne não fizer contato, o candidato o procura pelo e-mail.",
          ["E28-149", "E28-150"], destinatario="Candidatos PcD classificados", variante="Verificação da pessoa com deficiência"),
        E("CLA-28-16", "REGRA", "Para cada código de vaga, analisam-se os documentos de até 15 suplentes; desistência, antes ou depois do resultado final, chama o próximo habilitado na ordem do sorteio.",
          ["E28-111", "E28-110"], destinatario="Suplentes", variante="Suplentes e matrícula"),
        E("CLA-28-17", "CONSEQUÊNCIA", "Só se efetiva a matrícula de quem estiver como “matrícula homologada”.", ["E28-122", "E28-180"],
          destinatario="Classificados", prazo="Resultado final e homologação em 13/07/2026.", variante="Suplentes e matrícula"),
        E("CLA-28-18", "POSSIBILIDADE", "Sobrando vagas, a Administração pode chamar, na ordem do sorteio, quem teve a matrícula indeferida, para regularizar; a convocação é por e-mail.",
          ["E28-127", "E28-128"], destinatario="Indeferidos", prazo="2 dias úteis, contados do recebimento do e-mail.", consequencia="Sem regularizar no prazo, chama-se o próximo.",
          variante="Suplentes e matrícula"),
        E("CLA-28-19", "CONSEQUÊNCIA", "Quem não acessa a primeira disciplina no ambiente virtual em 5 dias corridos é considerado desistente e tem a matrícula cancelada; chama-se o suplente.",
          ["E28-135"], destinatario="Matriculados", variante="Suplentes e matrícula"),
        E("CLA-28-20", "CONSEQUÊNCIA", "O cotista PPI matriculado pode ser verificado de novo a qualquer tempo, por denúncia ou de ofício; confirmada a irregularidade, perde o vínculo, sem prejuízo das sanções penais.",
          ["E28-068"], destinatario="Matriculados em vaga PPI", variante="Suplentes e matrícula"),
    ],
    ambiguidades=[
        A("contradição", "Documentação irregular depois do sorteio: o 8.3 indefere a inscrição; o 8.6 diz que a matrícula não se efetiva.", ["E28-102", "E28-105"], "Qual é o ato, e de que se recorre?"),
        A("contradição", "Ausência à entrevista: o 8.10 mantém o candidato na ampla concorrência; o 10.1, d, cancela a matrícula de quem não participa da verificação quando convocado.",
          ["E28-109", "E28-124"], "Faltar tira só a vaga reservada, ou também a matrícula?"),
        A("alcance", "O 6.9.15 mantém na ampla só o indeferido por fenótipo; o 8.10, qualquer indeferido.", ["E28-088", "E28-109"], "O indeferido por formulário incorreto continua na ampla?"),
        A("lacuna", "A verificação da pessoa com deficiência não tem data, forma nem consequência.", ["E28-096"], "Quando acontece, como, e o que ocorre com o não elegível?"),
        A("desatualização", "A videoconferência é justificada pela pandemia, e os requisitos pedem o Adobe Flash Player, descontinuado.", ["E28-065", "E28-074"], "Manter, atualizar ou retirar em Retificação? (decisão da área)"),
        A("acessibilidade", "A entrevista por videoconferência não prevê intérprete de Libras nem outra forma de entrevista para o candidato surdo ou com deficiência auditiva.",
          ["E28-070", "E28-074", "E28-149"], "Há intérprete? Quem pede, e como?"),
        A("remissão", "O Evento 8 do Cronograma remete a um “item 9.13” que não existe.", ["E28-172"], "Confirmar a remissão."),
    ],
    perguntas=[
        P("Preciso assistir ao sorteio?", "Não.", ["E28-100"]),
        P("Concorro a vaga PPI e fui sorteado também na ampla concorrência. O que acontece?", "Você fica na ampla concorrência, e a vaga reservada passa ao próximo autodeclarado.", ["E28-107", "E28-108"]),
        P("A minha internet caiu na hora da entrevista. E agora?", "Tire print da tela e mande e-mail à comissão com a justificativa em até 24 horas; só há nova convocação com ela.", ["E28-081", "E28-083", "E28-084"]),
        P("Posso usar boné ou maquiagem na entrevista?", "Não.", ["E28-076", "E28-077"]),
        P("Faltei à entrevista de verificação. Perco tudo?", "O edital diz duas coisas: no 8.10, você fica só na ampla concorrência; no 10.1, d, a matrícula é cancelada. A pergunta é para a área.",
          ["E28-109", "E28-124"], nota="Testa se a contradição foi comunicada sem ser resolvida."),
        P("Sou pessoa com deficiência e fui classificado. O que vem depois?", "Uma entrevista com o Napne antes do início do curso, para identificar o atendimento de que você precisa; o Napne agenda, e, se não fizer contato, você o procura pelo e-mail.",
          ["E28-149", "E28-150"]),
    ],
    decisoes=[
        "Como representar a ordem dos dois sorteios (ampla concorrência, depois reservas) e a passagem do cotista entre as listas.",
        "A instrução técnica da videoconferência (6.9.5 e 6.9.7) é operacional: decidir se se traduz inteira, se resume com remissão ou se apoia em imagens da tela.",
    ],
    reaproveitamento=dict(
        roteiro="Sorteio → análise da documentação → verificação → suplentes e matrícula, como no 91/2026; aqui a verificação tem muito mais regra.",
        solucao="O texto do software, da análise dos sorteados e da substituição (LIB-0237, LIB-0238) é o mesmo no 59/2026: solução comum possível. A heteroidentificação vem da Resolução CS 61/2019 e deve se repetir nos editais do Cefor com cotas — a confirmar noutro edital.",
        gravacao="Possível para o bloco do software e da semente, se o contexto for o mesmo; improvável para o restante, que depende de datas e de cotas.",
    ),
)

N["E28"]["recurso"] = dict(
    pergunta="Discordo de uma decisão: posso recorrer, contra o quê, até quando e por onde?",
    destinatarios="Inscritos afetados por cada decisão: indeferidos na análise da documentação (sorteados e suplentes) e autodeclarados indeferidos na verificação.",
    enunciados=[
        E("REC-28-01", "POSSIBILIDADE", "Cabe recurso somente contra a verificação da autodeclaração e contra o resultado preliminar da análise da documentação.",
          ["E28-114"], destinatario="Todos", alcance="Restrição expressa: contra os demais atos, o edital diz que não cabe.", variante="O que se pode contestar"),
        E("REC-28-02", "PROIBIÇÃO", "Contra a ordem do sorteio e os demais atos não cabe recurso, pela restrição do 9.1.", ["E28-114", "E28-171"],
          destinatario="Todos", variante="O que se pode contestar",
          nota="Proibição por restrição expressa, e não ausência de cláusula. Se vias legais fora do edital se aplicam (Lei nº 9.784/1999, arts. 56 a 59) é questão jurídica."),
        E("REC-28-03", "PROIBIÇÃO", "Contra o indeferimento da inscrição por dados incompletos ou arquivo com problema técnico não há possibilidade de recurso.",
          ["E28-051"], destinatario="Inscritos indeferidos por esse motivo", variante="O que se pode contestar"),
        E("REC-28-04", "PRAZO", "Contra o resultado preliminar da análise da documentação: recurso de 08/06 a 10/06/2026; o resultado dos recursos sai em seguida.",
          ["E28-172", "E28-173", "E28-174"], destinatario="Sorteados e suplentes indeferidos", variante="Contra o resultado preliminar da análise da documentação",
          nota="O Cronograma escreve o resultado dos recursos em “12/06/2025”."),
        E("REC-28-05", "POSSIBILIDADE", "O suplente com documentação indeferida pode recorrer, no prazo do Cronograma.", ["E28-112", "E28-172"],
          destinatario="Suplentes indeferidos", variante="Contra o resultado preliminar da análise da documentação",
          nota="O Evento 8 inclui os suplentes; o edital não diz se o prazo é o do Evento 9."),
        E("REC-28-06", "PRAZO", "Contra o resultado preliminar da verificação da autodeclaração: recurso de 03/07 a 06/07/2026; o resultado após os recursos sai em 13/07/2026.",
          ["E28-177", "E28-178", "E28-179"], destinatario="Autodeclarados indeferidos", variante="Contra a verificação da autodeclaração"),
        E("REC-28-07", "REGRA", "Recursos fundamentados contra a comissão local (CLVA) são julgados pela comissão permanente do Ifes (CPVA), instância recursal de toda a verificação.",
          ["E28-064"], destinatario="Autodeclarados indeferidos", variante="Contra a verificação da autodeclaração"),
        E("REC-28-08", "OBRIGAÇÃO", "Recorrer pelo formulário on-line na página do Cefor, no link do edital, dentro do prazo.", ["E28-116"],
          destinatario="Quem recorre", variante="Para todo recurso"),
        E("REC-28-09", "PROIBIÇÃO", "Recurso por correio, fax, e-mail ou outro meio, ou sem fundamentação, é indeferido; fora do prazo, não se aceita.",
          ["E28-117", "E28-118"], destinatario="Quem recorre", variante="Para todo recurso"),
        E("REC-28-10", "INFORMAÇÃO", "Recorrer não garante mudança do resultado; equívocos verificados são corrigidos. O resultado sai na página do Cefor.",
          ["E28-115", "E28-119"], destinatario="Quem recorre", variante="Para todo recurso"),
    ],
    ambiguidades=[
        A("alcance", "A seção 7, da pessoa com deficiência, se chama “procedimento complementar de verificação da autodeclaração”, como o objeto do 9.1.", ["E28-114", "E28-094", "E28-096"],
          "O 9.1 dá recurso também contra a decisão sobre a pessoa com deficiência?"),
        A("lacuna", "O 8.12 dá recurso ao suplente “no prazo previsto no cronograma”, que não tem Evento próprio para suplentes.", ["E28-112", "E28-173"], "O prazo é o do Evento 9?"),
        A("alcance", "O indeferimento pelo 5.11 (formato e legibilidade) acontece antes do sorteio, na situação de inscrição; o 9.1 fala da análise da documentação.",
          ["E28-053", "E28-167", "E28-114"], "Cabe recurso contra a situação de inscrição?"),
        A("erro material", "Resultado dos recursos datado “12/06/2025”; o Evento 8 remete a um “item 9.13” inexistente.", ["E28-174", "E28-172"], "Confirmar data e remissão."),
        A("questão jurídica", "Três dias de prazo e recurso “somente” contra dois atos.", ["E28-114", "E28-173"],
          "É compatível com a Lei nº 9.784/1999 (arts. 56 a 59)? Não se decide aqui."),
    ],
    perguntas=[
        P("Discordo da ordem do sorteio. Posso recorrer?", "Não: o 9.1 limita o recurso à verificação da autodeclaração e ao resultado preliminar da análise da documentação.", ["E28-114"]),
        P("Meus documentos foram indeferidos no resultado preliminar. Até quando recorro, e como?", "De 08/06 a 10/06/2026, pelo formulário on-line na página do Cefor.", ["E28-173", "E28-116"]),
        P("Posso mandar o recurso por e-mail?", "Não: é indeferido.", ["E28-117"]),
        P("Basta dizer que discordo?", "Não: recurso sem fundamentação é indeferido.", ["E28-117"]),
        P("A minha autodeclaração foi indeferida. Quem julga o recurso, e até quando?", "A comissão permanente do Ifes (CPVA); o prazo vai de 03/07 a 06/07/2026.", ["E28-064", "E28-178"]),
        P("O meu arquivo deu problema e a inscrição foi indeferida. Recorro?", "Não: o 5.9 diz que não há possibilidade de recurso.", ["E28-051"]),
    ],
    decisoes=[
        "Como distinguir o que o edital proíbe expressamente (recurso contra os demais atos; recurso da inscrição com arquivo problemático) do que ele apenas não diz.",
        "Como mostrar dois períodos de recurso, com objetos e instâncias diferentes, sem que se confundam.",
    ],
    reaproveitamento=dict(
        roteiro="Objeto → prazo → canal → vedações → o que não cabe, como no 91/2026; aqui o “não cabe” é expresso.",
        solucao="As cláusulas 9.2 a 9.6 têm o mesmo texto, ou quase, no 59/2026 (LIB-0253 a LIB-0255, LIB-0148, LIB-0149): candidatas a solução comum, a validar.",
        gravacao="Possível para as vedações e o “não garante”, de texto e contexto iguais entre 28 e 59; não para objetos e prazos.",
    ),
)

# 59/2026 — Curso FIC de Libras, presencial, sem reserva de vagas, sorteio
N["E59"] = {}
N["E59"]["inscricao"] = dict(
    pergunta="Quero fazer o curso de Libras, presencial, no Cefor: posso me inscrever, como, até quando, o que envio e o que pode invalidar a inscrição?",
    destinatarios="Pessoas com ensino médio completo e disponibilidade para as aulas presenciais em Vitória; o edital não tem reserva de vagas.",
    enunciados=[
        E("INS-59-01", "CONDIÇÃO", "Ter ensino médio completo, disponibilidade para as aulas presenciais semanais, acesso a computador com internet e habilidade no uso do computador; ler o edital.",
          ["E59-012", "E59-014", "E59-015", "E59-016", "E59-017", "E59-018"], destinatario="Todos",
          nota="O 2.1 diz “desejável (não obrigatório)” ter o curso Libras Básico A1."),
        E("INS-59-02", "INFORMAÇÃO", "São 80 vagas, em duas turmas de 40: segundas e quintas, das 9h às 11h ou das 13h às 15h. O curso tem 15 semanas e 60 horas, no Cefor.",
          ["E59-020", "E59-021", "E59-007"], destinatario="Todos",
          nota="O 1.2 remete ao “quadro 3 do item 4.1”; os horários estão no Quadro 2."),
        E("INS-59-03", "OBRIGAÇÃO", "Inscrever-se pelo link nas páginas do Cefor ou do Ifes, só pela internet.", ["E59-024"], destinatario="Todos"),
        E("INS-59-04", "PRAZO", "As inscrições vão de 09/07 a 23/07/2026, até as 23h59 (Brasília); depois, o sistema não aceita novas.",
          ["E59-094", "E59-024"], destinatario="Todos",
          nota="O Cronograma está marcado “(RETIFICADO)”; sem o ato de Retificação, não se sabe o que mudou."),
        E("INS-59-05", "OBRIGAÇÃO", "Enviar, cada um no seu campo, em PDF de até 7 MB, digitalizado do original, nítido e sem cortes: identidade (frente e verso), CPF, comprovante de votação de 2024 ou certidão de quitação eleitoral, certidão de nascimento, casamento ou averbação, comprovação do ensino médio, documento militar (homens) e o Requerimento de Matrícula (Anexo II), com a declaração de veracidade marcada.",
          ["E59-026", "E59-027", "E59-028", "E59-029", "E59-030", "E59-031", "E59-032", "E59-033", "E59-104", "E59-106"], destinatario="Todos",
          alcance="Quem envia declaração de união estável tem de enviar a certidão de nascimento (E59-030)."),
        E("INS-59-06", "OBRIGAÇÃO", "Documento emitido fora do Brasil vai traduzido por tradutor juramentado; diplomas e certificados estrangeiros, revalidados.",
          ["E59-034", "E59-035"], destinatario="Quem tem documento estrangeiro"),
        E("INS-59-07", "OBRIGAÇÃO", "Ler o termo de consentimento de dados pessoais (Anexo III) e marcar a opção no formulário.", ["E59-043"], destinatario="Todos",
          nota="O Anexo III não está no PDF."),
        E("INS-59-08", "OBRIGAÇÃO", "Clicar em “confirmar inscrição” e, depois, imprimir e salvar o comprovante.", ["E59-036", "E59-037"], destinatario="Todos"),
        E("INS-59-09", "PROIBIÇÃO", "Em hipótese alguma se aceitam inscrição ou documentos por e-mail.", ["E59-042"], destinatario="Todos"),
        E("INS-59-10", "CONSEQUÊNCIA", "Inscrição com dados incompletos, arquivo anexado incorretamente ou com problema técnico (externo ao Cefor) que impeça abri-lo é indeferida, sem possibilidade de recurso.",
          ["E59-039"], destinatario="Todos", alcance="Proibição expressa de recurso.", variante="O que invalida a inscrição"),
        E("INS-59-11", "CONSEQUÊNCIA", "Requerimento de Matrícula incompleto ou incorreto indefere o candidato, sem recurso.", ["E59-033"],
          destinatario="Todos", alcance="Proibição expressa de recurso.", variante="O que invalida a inscrição"),
        E("INS-59-12", "CONSEQUÊNCIA", "Inscrição é indeferida se os documentos estiverem fora do PDF, cortados, incompletos, ilegíveis, mal digitalizados, rasurados ou vencidos.",
          ["E59-040"], destinatario="Todos", variante="O que invalida a inscrição"),
        E("INS-59-13", "INFORMAÇÃO", "Preencher, enviar e informar corretamente é responsabilidade do candidato, sob as penas da lei; o Cefor não responde por erro de preenchimento nem por falha técnica.",
          ["E59-025", "E59-041", "E59-038"], destinatario="Todos", variante="O que invalida a inscrição"),
        E("INS-59-14", "CONDIÇÃO", "Ao se inscrever, o candidato autoriza o Cefor a usar a sua imagem e voz para fins educacionais, em caráter definitivo e gratuito.",
          ["E59-053"], destinatario="Todos", nota="A cláusula está na seção do processo seletivo (6.8), e não na da inscrição."),
        E("INS-59-15", "CONDIÇÃO", "Inscrever-se é aceitar o edital e os anexos, sem poder alegar desconhecimento, e cumprir os prazos do Cronograma, sob pena de desclassificação.",
          ["E59-023", "E59-081", "E59-085", "E59-087"], destinatario="Todos"),
        E("INS-59-16", "INFORMAÇÃO", "Informações sobre inscrição e seleção, exclusivamente pelo e-mail da seleção.", ["E59-088"], destinatario="Todos"),
    ],
    ambiguidades=[
        A("contradição", "O curso é “Libras Iniciante – Nível A1” no título e no preâmbulo, e “Libras Básico – Nível A2” no 10.8 e no Requerimento; o 2.1 diz desejável ter o “Libras Básico – Nível A1”.",
          ["E59-002", "E59-003", "E59-012", "E59-085", "E59-105"], "Qual é o curso e o nível?"),
        A("remissão", "O 5.14 remete ao Anexo III, que o PDF não traz.", ["E59-043"], "Onde está o termo?"),
        A("remissão", "O 1.2 remete ao “quadro 3 do item 4.1”; os horários estão no Quadro 2, no item 4.", ["E59-007", "E59-021"], "Confirmar a remissão."),
        A("lacuna", "Há duas turmas (códigos de vaga), mas o edital não diz como o candidato escolhe a turma.", ["E59-021", "E59-055"], "A turma se escolhe na inscrição?"),
        A("lacuna", "Não se diz como se comprova a habilidade no uso do computador.", ["E59-018"], "Há verificação?"),
    ],
    perguntas=[
        P("Preciso ter feito um curso de Libras antes?", "Não é obrigatório; o edital diz que é “desejável” ter o Libras Básico A1 — o que, num curso de nível A1, pede esclarecimento da área.",
          ["E59-012"], nota="Testa se a dúvida do original foi comunicada sem ser resolvida."),
        P("Posso escolher o horário?", "Há uma turma de manhã e outra de tarde; o edital não diz como se escolhe.", ["E59-021"]),
        P("Enviei o Requerimento incompleto. Posso recorrer?", "Não: o candidato é indeferido, sem recurso.", ["E59-033"]),
        P("Preciso guardar alguma coisa depois de confirmar?", "Sim: imprimir e salvar o comprovante de inscrição.", ["E59-037"]),
        P("Ao me inscrever, autorizo o uso da minha imagem?", "Sim, para fins educacionais, em caráter definitivo e gratuito, diz o 6.8.", ["E59-053"]),
    ],
    decisoes=[
        "Decidir com a área e a comunidade surda a quem a tradução deste edital se dirige: um curso inicial de Libras atrai sobretudo quem ainda não sinaliza, mas a tradução é também para a pessoa surda que se inscreva.",
        "Como tratar o nome divergente do curso até a área corrigi-lo.",
    ],
    reaproveitamento=dict(
        roteiro="O do 28/2026, sem o bloco de cotas.",
        solucao="Formato do envio, identidade, CPF, documento militar e causas de indeferimento têm texto idêntico, ou quase, ao do 28/2026.",
        gravacao="Candidata nos blocos idênticos ao 28/2026, se a sequência e o contexto forem compatíveis — avaliação do profissional.",
    ),
)

N["E59"]["classificacao"] = dict(
    pergunta="Como se decide quem fica com as 80 vagas, e o que pode me tirar da lista?",
    destinatarios="Inscritos habilitados ao sorteio, sorteados e suplentes.",
    enunciados=[
        E("CLA-59-01", "REGRA", "Se houver mais inscritos do que vagas, as vagas se preenchem por sorteio eletrônico; a presença do candidato não é obrigatória.",
          ["E59-045", "E59-046", "E59-050"], destinatario="Todos", variante="Sorteio"),
        E("CLA-59-02", "CONDIÇÃO", "Só entram no sorteio as inscrições com dados completos e a documentação do 5.4; a lista dos habilitados, com o número de cada um, sai dois dias antes do sorteio.",
          ["E59-049", "E59-095"], destinatario="Todos", prazo="Situação da inscrição e habilitados em 24/07/2026.", variante="Sorteio"),
        E("CLA-59-03", "INFORMAÇÃO", "Dois servidores fazem o sorteio, que é gravado e disponibilizado nos sítios do Cefor e do Ifes; o 6.5 diz que é no salão de reuniões do Cefor, e o 6.6, que é on-line, transmitido no YouTube.",
          ["E59-050", "E59-051", "E59-096", "E59-097"], destinatario="Todos", prazo="27/07/2026, às 10h.", variante="Sorteio"),
        E("CLA-59-04", "INFORMAÇÃO", "Para auditoria, a “semente” fica no fim da página do sorteio.", ["E59-047"], destinatario="Todos", variante="Sorteio"),
        E("CLA-59-05", "REGRA", "Depois do sorteio, analisam-se os documentos dos primeiros sorteados, até o número de vagas; documentação incompleta ou incorreta indefere a inscrição, e analisa-se o próximo da ordem.",
          ["E59-048", "E59-052", "E59-098", "E59-099"], destinatario="Sorteados",
          prazo="Classificação preliminar em 27/07/2026; resultado preliminar da análise em 30/07/2026.", variante="Análise da documentação"),
        E("CLA-59-06", "REGRA", "Para cada código de vaga, analisam-se os documentos de até 30 suplentes; desistência, antes ou depois do resultado final, chama o próximo habilitado, em publicação no sítio do processo seletivo.",
          ["E59-055", "E59-054"], destinatario="Suplentes", variante="Suplentes e matrícula"),
        E("CLA-59-07", "POSSIBILIDADE", "O processo vale por 6 meses do resultado final, prorrogáveis; havendo nova turma nesse prazo, suplentes podem ser convocados. Acompanhar as publicações é do candidato.",
          ["E59-057"], destinatario="Suplentes", variante="Suplentes e matrícula"),
        E("CLA-59-08", "CONSEQUÊNCIA", "Só se efetiva a matrícula de quem estiver como “matrícula homologada”.", ["E59-067", "E59-102"],
          destinatario="Classificados", prazo="Resultado final e homologação em 07/08/2026.", variante="Suplentes e matrícula"),
        E("CLA-59-09", "POSSIBILIDADE", "Sobrando vagas, a Administração pode chamar, na ordem do sorteio, quem teve a matrícula indeferida, para regularizar; a convocação é por e-mail.",
          ["E59-070", "E59-071"], destinatario="Indeferidos", prazo="2 dias úteis, contados do recebimento do e-mail.", consequencia="Sem regularizar no prazo, chama-se o próximo.",
          variante="Suplentes e matrícula"),
        E("CLA-59-10", "CONSEQUÊNCIA", "Quem falta às aulas da primeira semana sem justificativa legal (atestado, laudo ou documento equivalente) é considerado desistente e tem a matrícula cancelada; chama-se o suplente.",
          ["E59-072", "E59-103"], destinatario="Matriculados", prazo="Início do curso em 10/08/2026.", variante="Suplentes e matrícula"),
        E("CLA-59-11", "CONSEQUÊNCIA", "Documentação falsa cancela a matrícula; informação inexata elimina, ainda que descoberta depois; fraude leva à perda da vaga, mesmo após a matrícula.",
          ["E59-068", "E59-078", "E59-080"], destinatario="Todos", variante="Suplentes e matrícula"),
    ],
    ambiguidades=[
        A("contradição", "O 6.5 põe o sorteio no salão de reuniões do Cefor; o 6.6 e o Cronograma, on-line, no YouTube.", ["E59-050", "E59-051", "E59-097"], "Presencial, on-line ou os dois?"),
        A("erro material", "O Evento 4 publica o “link da gravação” do sorteio em 24/07, três dias antes do sorteio (27/07).", ["E59-096", "E59-097"], "É o link da transmissão?"),
        A("lacuna", "Os suplentes se contam “por código de vaga” (turma), mas o edital não diz como o candidato entra numa turma.", ["E59-055", "E59-021"], "São 30 suplentes por turma?"),
    ],
    perguntas=[
        P("Preciso ir ao Cefor no dia do sorteio?", "Não: a presença não é obrigatória.", ["E59-050"]),
        P("O sorteio é presencial ou on-line?", "O edital diz as duas coisas (6.5 e 6.6); a pergunta é para a área.", ["E59-050", "E59-051"],
          nota="Testa se a contradição foi comunicada sem ser resolvida."),
        P("Fui sorteado, mas meus documentos estavam incompletos. O que acontece?", "A inscrição é indeferida, e a vaga passa ao próximo da ordem do sorteio.", ["E59-048", "E59-052"]),
        P("Não fui sorteado. Ainda tenho chance?", "Sim, como suplente: se alguém desistir, ou se houver nova turma em até 6 meses do resultado final, prorrogáveis.", ["E59-054", "E59-055", "E59-057"]),
        P("Faltei na primeira semana, com atestado médico. Perco a vaga?", "Não: perde a vaga quem falta sem justificativa legal.", ["E59-072"]),
    ],
    decisoes=["Como representar sorteio, análise e suplência como uma sequência no tempo, com as datas do Cronograma."],
    reaproveitamento=dict(
        roteiro="O do 28/2026, sem as cotas e sem a verificação da autodeclaração.",
        solucao="Software e semente, análise dos sorteados e substituição têm o mesmo texto do 28/2026 (LIB-0237, LIB-0238).",
        gravacao="Candidata para o bloco do software e da semente; não para o local do sorteio, que aqui é outro e está em contradição.",
    ),
)

N["E59"]["recurso"] = dict(
    pergunta="Discordo de uma decisão: posso recorrer, contra o quê, até quando e por onde?",
    destinatarios="Sorteados e suplentes com documentação indeferida.",
    enunciados=[
        E("REC-59-01", "POSSIBILIDADE", "Cabe recurso somente contra o resultado preliminar — o da análise da documentação dos sorteados.", ["E59-059", "E59-099"],
          destinatario="Sorteados indeferidos", alcance="Restrição expressa.", variante="O que se pode contestar"),
        E("REC-59-02", "PROIBIÇÃO", "Contra a ordem do sorteio e os demais atos não cabe recurso, pela restrição do 7.1.", ["E59-059", "E59-098"],
          destinatario="Todos", variante="O que se pode contestar",
          nota="Proibição por restrição expressa, e não ausência de cláusula. Vias legais fora do edital: questão jurídica."),
        E("REC-59-03", "PROIBIÇÃO", "Contra o indeferimento por dados incompletos, por arquivo com problema ou por Requerimento incorreto não há recurso.",
          ["E59-039", "E59-033"], destinatario="Inscritos indeferidos por esses motivos", variante="O que se pode contestar"),
        E("REC-59-04", "PRAZO", "Recurso de 30/07 a 03/08/2026; o resultado dos recursos sai em 05/08/2026.", ["E59-100", "E59-101"],
          destinatario="Sorteados indeferidos", variante="Contra o resultado preliminar"),
        E("REC-59-05", "POSSIBILIDADE", "O suplente com documentação indeferida pode recorrer, no prazo do Cronograma.", ["E59-056"],
          destinatario="Suplentes indeferidos", variante="Contra o resultado preliminar"),
        E("REC-59-06", "OBRIGAÇÃO", "Recorrer pelo formulário on-line nas páginas do Cefor e do Ifes, no link do edital, dentro do prazo.", ["E59-060"],
          destinatario="Quem recorre", variante="Para todo recurso"),
        E("REC-59-07", "PROIBIÇÃO", "Recurso por correio, fax, e-mail ou outro meio, ou sem fundamentação, é indeferido; fora do prazo, não se aceita.",
          ["E59-062", "E59-063"], destinatario="Quem recorre", variante="Para todo recurso"),
        E("REC-59-08", "INFORMAÇÃO", "Recorrer não garante mudança; equívocos verificados são corrigidos. O resultado sai nos sítios do Ifes e do Cefor.",
          ["E59-061", "E59-064"], destinatario="Quem recorre", variante="Para todo recurso"),
    ],
    ambiguidades=[
        A("alcance", "O 7.1 diz só “resultado preliminar”; o Cronograma o descreve como o da análise da documentação dos sorteados.", ["E59-059", "E59-099"], "É esse o único objeto?"),
        A("alcance", "O 6.10 dá recurso ao suplente, e o 7.1 limita o recurso ao resultado preliminar; o Cronograma não tem Evento para suplentes.", ["E59-056", "E59-059", "E59-100"],
          "O recurso do suplente segue o prazo do Evento 8?"),
        A("alcance", "O indeferimento pelo 5.11 (formato e legibilidade) sai na situação de inscrição, antes do sorteio, que o 7.1 não inclui.", ["E59-040", "E59-095", "E59-059"],
          "Cabe recurso contra a situação de inscrição?"),
        A("questão jurídica", "Recurso “somente” contra um ato, em cinco dias.", ["E59-059", "E59-100"], "É compatível com a Lei nº 9.784/1999 (arts. 56 a 59)? Não se decide aqui."),
    ],
    perguntas=[
        P("Discordo do resultado do sorteio. Posso recorrer?", "Não: só cabe recurso contra o resultado preliminar.", ["E59-059"]),
        P("Até quando recorro do resultado preliminar, e como?", "De 30/07 a 03/08/2026, pelo formulário on-line.", ["E59-100", "E59-060"]),
        P("Sou suplente e meus documentos foram indeferidos. Posso recorrer?", "Sim, diz o 6.10, no prazo do Cronograma — que não tem Evento próprio para suplentes.", ["E59-056"],
          nota="A segunda parte testa se a lacuna foi comunicada."),
        P("Posso recorrer por e-mail?", "Não: é indeferido.", ["E59-062"]),
    ],
    decisoes=["Como distinguir a restrição expressa do 7.1 do que o edital não diz."],
    reaproveitamento=dict(
        roteiro="O do 28/2026, com um objeto só.",
        solucao="As cláusulas 7.2 a 7.6 repetem as 9.2 a 9.6 do 28/2026: candidatas a solução comum, a validar.",
        gravacao="Possível para as vedações e o “não garante”, se o contexto for compatível; não para o objeto e o prazo.",
    ),
)


# ═════════════════════════════════════════════════════════════════════════════════════════════════
# RODADA 4 (2026-10-11) — consolidação, após revisão: pendências nos enunciados e nas respostas esperadas, e as
# versões reconstruídas a partir dos atos baixados (editais/*/retificacoes.md). Nada do que a rodada 3 escreveu se
# apaga: cada mudança fica no histórico da narrativa.
# ═════════════════════════════════════════════════════════════════════════════════════════════════
R4 = "2026-10-11 (rodada 4)"
PAGINA_28 = "Página do processo seletivo do 28/2026, consultada em 11/10/2026"
PAGINA_59 = "Página do processo seletivo do 59/2026, consultada em 11/10/2026"
RET_28 = "Retificação nº 01 do Edital 28/2026, de 21/07/2026"
COM_28 = "Comunicado de alteração da data de início do curso, 28/2026, de 24/08/2026"
RET_59 = "Retificação do Edital 59/2026, de 30/07/2026"
COM_59 = "Comunicado de não realização do sorteio, 59/2026, de 27/07/2026"
JURIDICA = ("Se há via de contestação fora do edital (Lei nº 9.784/1999, arts. 56 a 59) é questão jurídica: o edital "
            "não a responde, e a tradução não deve respondê-la por ele.")


def _hist(n, texto):
    n.setdefault("historico", []).append(f"{R4} — {texto}")


def rev(ed, nome, id_, motivo, **campos):
    n = N[ed][nome]
    e = next(e for e in n["enunciados"] if e["id"] == id_)
    for k, v in campos.items():
        e[k] = list(e[k]) + list(v) if k == "atos" else v
    _hist(n, f"{id_}: {motivo}")


def revp(ed, nome, inicio, motivo, **campos):
    n = N[ed][nome]
    p = next(p for p in n["perguntas"] if p["pergunta"].startswith(inicio))
    p.update(campos)
    _hist(n, f"pergunta “{p['pergunta']}”: {motivo}")


def novo(ed, nome, enunciado, motivo):
    N[ed][nome]["enunciados"].append(enunciado)
    _hist(N[ed][nome], f"{enunciado['id']}: {motivo}")


def novap(ed, nome, pergunta, motivo):
    N[ed][nome]["perguntas"].append(pergunta)
    _hist(N[ed][nome], f"pergunta nova “{pergunta['pergunta']}”: {motivo}")


# ── 28/2026, inscrição ───────────────────────────────────────────────────────────────────────────
rev("E28", "inscricao", "INS-28-05", "a divergência de ano passou ao enunciado.",
    pendencia="O Cronograma escreve o início como “07/04/2025” no edital consolidado e no Anexo I publicado à parte; a "
              "página do processo informa 07/04/2026 a 06/05/2026.",
    atos=[PAGINA_28, "Anexo I — Cronograma, publicado à parte (arquivo de 07/04/2026)"])
rev("E28", "inscricao", "INS-28-06", "as vagas foram alteradas pela Retificação nº 01, que a versão consolidada não incorporou.",
    alcance="No edital inventariado (consolidado de 24/08/2026): 40 vagas por polo — 28 de ampla concorrência, 10 PPI e 2 "
            "PcD —, 280 no total (Quadro 2 e item 4.1). A Retificação nº 01, de 21/07/2026, passou o Quadro 2 a 60 por "
            "polo — 42, 15 e 3 —, 420 no total.",
    pendencia="Quantas vagas vigoram? A versão consolidada, posterior à Retificação, não a incorporou, e o item 4.1 não "
              "foi retificado. Pergunta para a área.",
    atos=[RET_28])
novap("E28", "inscricao", P(
    "Quantas vagas há em cada polo?",
    "O edital diz 40 (28 de ampla concorrência, 10 PPI e 2 PcD). A Retificação nº 01, de 21/07/2026, diz 60 (42, 15 e 3), "
    "e a versão consolidada de 24/08 não a incorporou. A divergência é para a área.",
    ["E28-027", "E28-020"], estado="com pendência",
    pendencia="vagas vigentes: 280 (consolidado) ou 420 (Retificação nº 01)"),
    "a Retificação nº 01 mudou o número de vagas.")
revp("E28", "inscricao", "Anexei um arquivo", "a resposta deixou de afirmar o que o edital não decide.",
     resposta="O edital diz que não há possibilidade de recurso (5.9). " + JURIDICA,
     estado="com pendência", pendencia="alcance jurídico da proibição")
revp("E28", "inscricao", "Os documentos vão", "o estado passou a registrar a contradição.", estado="com pendência",
     pendencia="arquivo único (5.7) × um por campo (5.4)")

# ── 28/2026, classificação ───────────────────────────────────────────────────────────────────────
rev("E28", "classificacao", "CLA-28-06", "o número de vagas mudou depois do resultado final.",
    pendencia="A Retificação nº 01 (21/07/2026) passou de 280 para 420 vagas depois do sorteio (11/05) e do resultado "
              "final (13/07); a versão consolidada não a incorporou. Como a análise “até o número de vagas” se aplica às "
              "vagas novas não está dito.",
    atos=[RET_28])
rev("E28", "classificacao", "CLA-28-16", "a página registra a análise e o recurso dos suplentes, que o Cronograma não tem.",
    atos=[PAGINA_28 + ": resultado preliminar da análise de documentos dos suplentes publicado em 24/07/2026, recurso de "
          "24/07 a 26/07 e nova convocação de suplentes para a verificação"],
    nota="O que a página informa é prática do certame, e não texto do edital.")
revp("E28", "classificacao", "Faltei à entrevista", "o estado passou a registrar a contradição.", estado="com pendência",
     pendencia="8.10 (fica na ampla) × 10.1, d (matrícula cancelada)")

# ── 28/2026, recurso ─────────────────────────────────────────────────────────────────────────────
rev("E28", "recurso", "REC-28-02", "o enunciado separa o que o edital prevê do alcance ainda não esclarecido.",
    acao="O 9.1 só prevê recurso contra a verificação da autodeclaração e contra o resultado preliminar da análise da "
         "documentação; a ordem do sorteio e os demais atos não estão entre os objetos.",
    pendencia="Se o 9.1 alcança a decisão sobre a pessoa com deficiência (ver as ambiguidades), e se há outra via fora do "
              "edital. " + JURIDICA)
rev("E28", "recurso", "REC-28-03", "a proibição expressa ganhou a questão jurídica que o edital não responde.",
    pendencia=JURIDICA)
rev("E28", "recurso", "REC-28-04", "a página confirma o ano que o Cronograma escreve errado.",
    pendencia="O Cronograma escreve o resultado dos recursos em “12/06/2025”; a página o registra publicado em 12/06/2026.",
    atos=[PAGINA_28])
rev("E28", "recurso", "REC-28-05", "a página informa um prazo que o edital não tem.",
    pendencia="O edital não tem Evento para o recurso do suplente. A página do processo informou recurso de 24/07 a "
              "26/07/2026, contra a análise de documentos dos suplentes publicada em 24/07.",
    atos=[PAGINA_28])
rev("E28", "recurso", "REC-28-06", "o prazo diverge entre o Cronograma e a página.",
    pendencia="O Cronograma diz 03/07 a 06/07/2026; a página do processo informou 03/07 a 05/07/2026.",
    atos=[PAGINA_28])
revp("E28", "recurso", "Discordo da ordem do sorteio", "a resposta deixou de ser um “Não” categórico.",
     resposta="O edital não prevê esse recurso: o 9.1 limita o recurso à verificação da autodeclaração e ao resultado "
              "preliminar da análise da documentação. " + JURIDICA,
     estado="com pendência", pendencia="alcance do 9.1 e vias fora do edital")
revp("E28", "recurso", "A minha autodeclaração", "o prazo diverge entre o Cronograma e a página.",
     resposta="A comissão permanente do Ifes (CPVA). O prazo é de 03/07 a 06/07/2026 pelo Cronograma; a página do processo "
              "informou 03/07 a 05/07. A divergência é para a área.",
     estado="com pendência", pendencia="término do prazo: 05/07 ou 06/07")
revp("E28", "recurso", "O meu arquivo deu problema", "a resposta deixou de afirmar o que o edital não decide.",
     resposta="O edital diz que não há possibilidade de recurso (5.9). " + JURIDICA,
     estado="com pendência", pendencia="alcance jurídico da proibição")

# ── 59/2026, inscrição ───────────────────────────────────────────────────────────────────────────
revp("E59", "inscricao", "Preciso ter feito um curso", "o estado passou a registrar a contradição.", estado="com pendência",
     pendencia="nome e nível do curso: “Iniciante – A1” (título), “Básico – A2” (10.8, Anexo II), “Básico – A1” (página)")
revp("E59", "inscricao", "Enviei o Requerimento", "a resposta deixou de afirmar o que o edital não decide.",
     resposta="O edital diz que o candidato é indeferido, sem recurso (5.4, g). " + JURIDICA,
     estado="com pendência", pendencia="alcance jurídico da proibição")
rev("E59", "inscricao", "INS-59-02", "a página dá ao curso um terceiro nome.",
    pendencia="O curso tem três nomes nos documentos: “Libras Iniciante – Nível A1” (título e preâmbulo), “Libras Básico – "
              "Nível A2” (10.8 e Anexo II, também no Anexo II publicado à parte) e “Libras Básico – Nível A1” (título da "
              "página do processo).",
    atos=[PAGINA_59, "Anexo II — Requerimento de Matrícula, publicado à parte"])

# ── 59/2026, classificação ───────────────────────────────────────────────────────────────────────
novo("E59", "classificacao", E(
    "CLA-59-12", "INFORMAÇÃO",
    "Neste certame não houve sorteio: o número de inscritos foi menor que o de vagas. A regra do 6.1 — sorteio só se houver "
    "mais inscritos que vagas — é a que o comunicado aplica.",
    ["E59-046"], destinatario="Todos", variante="Sorteio", atos=[COM_59],
    nota="Fato posterior ao edital, publicado em ato próprio; não muda o texto do edital."),
    "o Comunicado de 27/07/2026 registra que não houve sorteio.")
rev("E59", "classificacao", "CLA-59-05", "a data do resultado preliminar foi retificada.",
    prazo="Classificação preliminar em 27/07/2026; resultado preliminar da análise em 30/07/2026 (o Anexo I original dizia "
          "31/07; a Retificação passou a 30/07).",
    atos=[RET_59, "Anexo I — Cronograma, publicado à parte (versão original)"])
rev("E59", "classificacao", "CLA-59-10", "a data de início foi retificada, e a versão consolidada não acompanhou.",
    pendencia="A Retificação de 30/07/2026 passou o início do curso de 10/08 para 24/08/2026; a versão consolidada, do mesmo "
              "dia e anterior à Retificação, ainda diz 10/08.",
    atos=[RET_59])
revp("E59", "classificacao", "O sorteio é presencial", "o comunicado de não realização entrou na resposta.",
     resposta="O edital diz as duas coisas (6.5 e 6.6), e a pergunta é para a área. Neste certame não houve sorteio: o "
              "número de inscritos foi menor que o de vagas (Comunicado de 27/07/2026).",
     estado="com pendência", pendencia="local do sorteio, quando houver")
revp("E59", "classificacao", "Não fui sorteado", "o comunicado de não realização entrou na resposta.",
     resposta="O edital prevê a suplência, por desistência, e a convocação para nova turma em até 6 meses do resultado "
              "final, prorrogáveis. Neste certame não houve sorteio, porque o número de inscritos foi menor que o de vagas.",
     nota="A premissa da pergunta não vale para este certame: testa se o comunicado foi comunicado.")

# ── 59/2026, recurso ─────────────────────────────────────────────────────────────────────────────
rev("E59", "recurso", "REC-59-02", "o enunciado separa o que o edital prevê do alcance ainda não esclarecido.",
    acao="O 7.1 só prevê recurso contra o resultado preliminar; a ordem do sorteio e os demais atos não estão entre os "
         "objetos. Neste certame não houve sorteio.",
    pendencia=JURIDICA, atos=[COM_59])
rev("E59", "recurso", "REC-59-03", "a proibição expressa ganhou a questão jurídica que o edital não responde.",
    pendencia=JURIDICA)
rev("E59", "recurso", "REC-59-04", "o prazo e a data do resultado divergem entre os documentos.",
    acao="Recurso até 03/08/2026, pelo Cronograma da versão consolidada e pela Retificação; o resultado dos recursos, em "
         "05/08/2026.",
    prazo="Início em 30/07/2026 (o Anexo I original dizia 31/07; a Retificação passou a 30/07).",
    pendencia="A página do processo informou o recurso de 30/07 a 02/08/2026 e registra o resultado dos recursos publicado "
              "em 07/08/2026.",
    atos=[RET_59, PAGINA_59])
revp("E59", "recurso", "Discordo do resultado do sorteio", "a resposta deixou de ser um “Não” categórico.",
     resposta="O edital não prevê esse recurso: o 7.1 só admite recurso contra o resultado preliminar. Neste certame não "
              "houve sorteio. " + JURIDICA,
     estado="com pendência", pendencia="alcance do 7.1 e vias fora do edital")
revp("E59", "recurso", "Até quando recorro", "o prazo diverge entre os documentos.",
     resposta="Até 03/08/2026, pelo Cronograma e pela Retificação; a página do processo informou até 02/08. O recurso é pelo "
              "formulário on-line. A divergência é para a área.",
     estado="com pendência", pendencia="término do prazo: 02/08 ou 03/08")
revp("E59", "recurso", "Sou suplente", "o estado passou a registrar a lacuna.", estado="com pendência",
     pendencia="o Cronograma não tem prazo para o suplente")
