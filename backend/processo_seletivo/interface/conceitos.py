"""Os nomes e as frases do Centro de Controle do Edital (136).

**Por que um módulo só** (D-006). Os nomes das fases, dos grupos e dos passos, e as frases que
explicam cada passo, são exatamente o que a validação com operadores vai medir. Trocá-los tem de ser
editar uma tabela, e não caçar texto em template. Por isso `centro.py` conhece só as chaves, e o
template recebe o texto pronto.

**Os textos valem como estão** (138, D-001). São os da versão 2 do protótipo do estudo de 09/11/2026
(`doc/estudo-centro-de-controle-2026-11-09/07-refinamento.md`). Em 10/11/2026 o usuário dispensou a
validação com operadores, pôs o Centro na rota do Edital e aprovou os textos como estão, o que
responde à sétima decisão do estudo (quem aprova os textos pedagógicos). Mudar um nome continua
sendo editar uma tabela daqui.

**O que nenhum texto daqui usa**: «recorte», «faixa» e «geração». A varredura de vocabulário
(`test_vocabulario_da_composicao.py`) exige que a tela defina esses termos no primeiro uso, e ela lê
o template — texto que chega por variável escaparia dela calado. O teste destes conceitos prende a
ausência.

Os nomes simples vêm **antes** do termo do GPS, que continua à vista ("no GPS: congelar a relação"):
o vocabulário do domínio não é trocado, só deixa de ser a primeira coisa que a pessoa precisa saber.
"""

from processo_seletivo.interface import andamento as a

# ---------------------------------------------------------------------------------------------
# As fases e os grupos
# ---------------------------------------------------------------------------------------------

PUBLICACAO, INSCRICOES, AVALIACAO, CLASSIFICACAO = (
    "publicacao",
    "inscricoes",
    "avaliacao",
    "classificacao",
)
RESULTADO, VAGAS, CONVOCACAO, CONCLUSAO = "resultado", "vagas", "convocacao", "conclusao"

#: `(chave, nome, a pergunta que a fase responde)`, na ordem do mapa.
FASES = (
    (PUBLICACAO, "Edital", "O Edital está publicado e vigente?"),
    (INSCRICOES, "Inscrições", "Quem se inscreveu, e o período acabou?"),
    (AVALIACAO, "Avaliação", "As Etapas foram avaliadas e consolidadas?"),
    (CLASSIFICACAO, "Classificação", "Em que ordem cada lista ficou?"),
    (RESULTADO, "Resultado e recursos", "O resultado foi divulgado, e cabe recurso?"),
    (VAGAS, "Vagas", "Quem a lista alcança, e que vaga cada um ocupa?"),
    (CONVOCACAO, "Convocação", "Quem foi chamado, entregou e foi conferido?"),
    (CONCLUSAO, "Conclusão", "Tudo tem desfecho, e o Edital pode ser encerrado?"),
)
CHAVES = tuple(chave for chave, _, _ in FASES)
NOMES = {chave: nome for chave, nome, _ in FASES}
PERGUNTAS = {chave: pergunta for chave, _, pergunta in FASES}
#: O nome no meio de uma frase ("Há algo em aberto em …"): minúsculo, menos "Edital", que é nome
#: do ato e se escreve com maiúscula em todo o sistema.
NA_FRASE = {chave: nome if chave == PUBLICACAO else nome.lower() for chave, nome, _ in FASES}
#: As fases que andam por lista; as outras três são do Edital inteiro.
POR_LISTA = (AVALIACAO, CLASSIFICACAO, RESULTADO, VAGAS, CONVOCACAO)

#: Os grupos só orientam a leitura do mapa, e não mudam regra nenhuma (FR-4708).
GRUPOS = (
    ("Abertura", (PUBLICACAO, INSCRICOES)),
    ("Seleção", (AVALIACAO, CLASSIFICACAO, RESULTADO, VAGAS)),
    ("Ocupação", (CONVOCACAO, CONCLUSAO)),
)

# ---------------------------------------------------------------------------------------------
# O andamento da fase — a primeira leitura
# ---------------------------------------------------------------------------------------------

CONCLUIDA, EM_CURSO, NAO_INICIADA, NAO_SE_APLICA = (
    "concluida",
    "em_curso",
    "nao_iniciada",
    "nao_se_aplica",
)
#: Palavra e sinal, sempre juntos: a cor da folha nunca é a única pista (FR-4748).
ROTULOS = {
    CONCLUIDA: "Concluída",
    EM_CURSO: "Em curso",
    NAO_INICIADA: "Ainda não começou",
    NAO_SE_APLICA: "Não se aplica",
}
#: A forma curta, para a célula da tabela por lista, onde "Ainda não começou" não cabe.
ROTULOS_CURTOS = {**ROTULOS, NAO_INICIADA: "Ainda não"}
SINAIS = {CONCLUIDA: "✓", EM_CURSO: "◐", NAO_INICIADA: "○", NAO_SE_APLICA: "—"}

# ---------------------------------------------------------------------------------------------
# Os passos, na língua de quem conduz
# ---------------------------------------------------------------------------------------------

#: `{tipo do ponto ou natureza da providência: {...}}`. `simples` é o nome do passo para quem
#: conduz; `termo`, o nome no GPS; `curta` fica sempre à vista; `porque` e `ao_confirmar`, só sob
#: demanda (FR-4736, FR-4743).
CONCEITOS = {
    a.RELACAO: {
        "simples": "Fixar os participantes",
        "termo": "congelar a relação",
        "curta": "Publica, para cada lista, quem participa do sorteio e com que número — e isso "
        "não muda mais.",
        "porque": "Encerrar as inscrições impede que entre gente nova; fixar a lista antes de a "
        "semente existir impede que alguém a monte já sabendo o resultado.",
        "ao_confirmar": "Irreversível: corrigir exige Retificação e uma relação nova. Fixe todas "
        "as listas do marco antes de obter a semente — depois dela, a relação é recusada.",
    },
    a.SEMENTE: {
        "simples": "Obter a semente pública",
        "termo": "observar a extração",
        "curta": "Registra os números da extração declarada no Edital (a Loteria Federal, no "
        "certame real). Uma só semente vale para todas as listas.",
        "porque": "Ninguém escolhe a semente: ela vem de uma fonte pública, depois que os "
        "participantes estão fixados. É o que torna o sorteio verificável.",
        "ao_confirmar": "Com a Loteria Federal, só depois da data da extração. Se a fonte não "
        "responde, nada é gravado e se tenta de novo; não se digitam números à mão.",
    },
    a.SORTEIO: {
        "simples": "Realizar o sorteio",
        "termo": "sorteio",
        "curta": "Aplica a semente à lista fixada e produz a ordem dos participantes.",
        "porque": "A mesma lista e a mesma semente dão sempre a mesma ordem: qualquer pessoa pode "
        "reproduzir o resultado no canal público.",
        "ao_confirmar": "Grava a ordem da lista como ato imutável, com página de verificação.",
    },
    a.ORDEM: {
        "simples": "Classificar a lista",
        "termo": "emitir a ordem",
        "curta": "Grava a classificação da lista, pelas notas consolidadas, pesos e desempates do "
        "Edital.",
        "porque": "A ordem é a base do que vem depois: o resultado, o limite de chamada, as vagas "
        "e a convocação a leem.",
        "ao_confirmar": "Irreversível. Se uma nota mudar (um recurso deferido, por exemplo), é "
        "preciso emitir uma ordem nova, com motivo. Numa lista sem inscritos, emitir declara que "
        "ninguém concorreu ali.",
    },
    a.CORTE: {
        "simples": "Definir até onde se chama",
        "termo": "emitir o corte",
        "curta": "Fixa até que posição de cada lista as pessoas seguem — para as vagas e para a "
        "reserva, se houver.",
        "porque": "Limita quem passa à análise de documentos e quem disputa as vagas.",
        "ao_confirmar": "Com o prazo de recurso aberto, a recomendação é esperar: um recurso "
        "deferido tornaria o corte obsoleto.",
    },
    a.APURACAO: {
        "simples": "Distribuir as vagas entre as listas",
        "termo": "apurar a ocupação",
        "curta": "Cruza ampla concorrência e cotas e decide que vaga cada pessoa alcançada ocupa, "
        "sem contar ninguém duas vezes.",
        "porque": "Quem está bem colocado na ampla ocupa pela ampla, e a vaga da cota passa ao "
        "próximo da cota. A convocação chama quem a apuração indicou.",
        "ao_confirmar": "Uma desistência ou um corte novo tornam a apuração obsoleta, e ela é "
        "refeita.",
    },
    a.RESULTADO: {
        "simples": "Divulgar o resultado",
        "termo": "publicar resultado",
        "curta": "Torna a ordem pública: o preliminar abre o prazo de recurso; o definitivo vem "
        "depois do prazo e dos recursos.",
        "porque": "O definitivo não é pré-requisito do corte, das vagas nem da convocação — mas um "
        "recurso deferido pode mudá-los.",
        "ao_confirmar": "Ato de quem publica resultados, com documento próprio.",
    },
    a.RECURSO: {
        "simples": "Decidir os recursos",
        "termo": "recursos",
        "curta": "Julga os pedidos de revisão feitos no prazo.",
        "porque": "Um recurso deferido pode mudar uma nota, e com ela a ordem, o corte e as vagas.",
        "ao_confirmar": "A decisão é registrada e comunicada; a ordem afetada passa a pedir uma "
        "nova.",
    },
    a.CONVOCACAO: {
        "simples": "Convocar e decidir",
        "termo": "convocação",
        "curta": "Chama, com prazo, quem a apuração indicou, e acompanha cada chamada até o "
        "desfecho.",
        "porque": "É a passagem da classificação para a vaga ocupada. Quem não responde no prazo "
        "tem o não atendimento registrado, e a fila anda.",
        "ao_confirmar": "Convocação e comunicação são atos registrados. A matrícula acontece fora "
        "do GPS.",
    },
    a.CONFERIR: {
        "simples": "Conferir os documentos",
        "termo": "conferência documental",
        "curta": "Abre cada documento entregue e o marca como conforme ou pendente, com motivo.",
        "porque": "O GPS só aceita «conforme» de quem abriu o arquivo. Com tudo conforme, "
        "registra-se o desfecho.",
        "ao_confirmar": "A pendência volta ao candidato, que pode reenviar no prazo.",
    },
    a.ETAPA: {
        "simples": "Avaliar a Etapa",
        "termo": "Etapa",
        "curta": "Distribui as inscrições a avaliadores, registra as avaliações e consolida.",
        "porque": "Só a Etapa consolidada alimenta a classificação.",
        "ao_confirmar": "Consolidar fecha os resultados; mudá-los depois é reavaliação, por "
        "recurso.",
    },
}
#: Os atos da Etapa leem o mesmo conceito: distribuir, avaliar, consolidar e reavaliar são partes
#: de "avaliar a Etapa", e a frase vale para todos.
for _natureza in (a.DISTRIBUIR, a.AVALIAR, a.CONSOLIDAR, a.REAVALIAR):
    CONCEITOS[_natureza] = CONCEITOS[a.ETAPA]

#: Os atos cujo nome no GPS é jargão: a providência mostra primeiro o nome simples, e o do GPS
#: depois, como "no GPS: …" (FR-4729).
JARGAO = frozenset({a.RELACAO, a.SEMENTE, a.ORDEM, a.CORTE, a.APURACAO})

#: **Os atos da vaga sem quem a ocupe já têm nome próprio** (155, FR-6321, UX-602), e não são a
#: apuração: a derivação os põe na natureza dela só para que caiam na fase das vagas. Trocá-los
#: pelo nome simples da apuração fazia o Centro anunciar "Distribuir as vagas entre as listas", com
#: a frase de quem apura, para quem ia declarar a vaga não preenchida — e, para quem elabora, a
#: mesma frase no lugar da Retificação (problema novo N-01 da reavaliação de 12/11/2026). Os nomes
#: são os da derivação (`andamento.py`), que não pode importar este módulo.
CONCEITOS_DE_ATO = {
    "Declarar a vaga não preenchida": {
        "simples": "Declarar a vaga não preenchida",
        "termo": "declarar a vaga não preenchida",
        "curta": "Registra, com fundamento, que a vaga reservada fica sem ocupante: ninguém mais "
        "pode ocupá-la, e o Edital não declara para onde ela vai.",
        "porque": "Sem a declaração, a vaga continua contando como a ocupar, e a fase das vagas "
        "não se fecha.",
        "ao_confirmar": "Passa pela conferência antes de ser registrada. Desfazer é ato "
        "contrário, com motivo.",
    },
    "Retificar o Edital para declarar a reversão": {
        "simples": "Retificar o Edital para declarar a reversão",
        "termo": "retificar o Edital",
        "curta": "Abre a Retificação que publica para onde vai a vaga reservada que ficar sem "
        "ocupante.",
        "porque": "Sem a reversão publicada no Edital, a vaga não passa à ampla concorrência.",
        "ao_confirmar": "A Retificação segue o fluxo de aprovação e publicação do Edital.",
    },
}


def conceito(chave):
    return CONCEITOS.get(chave)


def conceito_da_providencia(natureza, ato):
    """O conceito do ato, quando ele tem nome próprio; senão, o da natureza."""
    return CONCEITOS_DE_ATO.get(ato) or conceito(natureza)


def ato_simples(natureza, ato):
    """O nome do ato na língua de quem conduz: "Classificar a lista", e não "Emitir a ordem".

    Só o jargão muda (FR-4729); os demais atos já se chamam como quem os pratica os chama. Uma
    função só, lida pela providência, pela tabela da fase e pela linha de cada lista — com três
    cópias, uma natureza nova entrava no jargão de uma e não das outras.
    """
    if ato in CONCEITOS_DE_ATO:
        return ato
    if natureza in JARGAO:
        return CONCEITOS[natureza]["simples"]
    return ato


# ---------------------------------------------------------------------------------------------
# As frases fixas da página
# ---------------------------------------------------------------------------------------------

#: O "Por que esta" de cada regra do destaque (D-005).
PORQUE_UNICA = "É a única ação sua disponível agora."
PORQUE_DESTRAVA_UMA = "É a que destrava os próximos passos. A outra ação sua corre em paralelo e "
PORQUE_DESTRAVA_UMA += "não segura nada."
PORQUE_DESTRAVA_VARIAS = "É a que destrava os próximos passos. As outras correm em paralelo e não "
PORQUE_DESTRAVA_VARIAS += "seguram nada."
#: Sem destaque, com mais de uma ação sua (FR-4724). `{n}` é o número de ações.
SEM_DESTAQUE = (
    "Você tem {n} ações disponíveis agora. Todas já podem ser feitas — o que depende de outro ato "
    "ainda não aparece aqui — e o GPS não escolhe a ordem entre elas."
)
#: A Avaliação que o sorteio não lê (D-008).
PARALELA = (
    "Paralela ao sorteio: fixar os participantes, obter a semente e sortear não dependem desta "
    "Etapa."
)
RETIFICACAO_EM_CURSO = "Retificação em curso — ela pode mudar datas, vagas ou regras."
CONCLUSAO_PRONTA = "Listas concluídas — o encerramento é do Gestor"
CONCLUSAO_DEPOIS = "Depois das convocações"
MATRICULA_FORA = "A matrícula acontece fora do GPS."
#: O limite da responsabilidade do GPS na passagem ao setor (153, FR-6120). Sem "encaminhado",
#: "entregue" nem "recebido": o GPS afirma só o que ele fez (a decisão de terminologia da `117`).
LIMITE_DA_PASSAGEM = (
    "O GPS termina ao disponibilizar os documentos ao setor. A matrícula, a bolsa ou o contrato "
    "acontecem fora do GPS, e ele não registra o recebimento."
)
