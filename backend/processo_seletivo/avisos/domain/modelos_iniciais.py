"""Os modelos com que toda unidade começa (066, `D-008`, contracts/mensagem.md; 171, FR-7320).

**Ponto de partida, e não padrão institucional.** Eles são criados uma vez por unidade e, daí em
diante, são da unidade: editados, inativados, reativados como qualquer outro. Uma correção futura
neste arquivo **não alcança** a unidade que já os tem — o texto passa a ser da seleção, e não há
versionamento de modelo institucional.

**Assunto neutro nos três** (`D-007`): o assunto aparece na notificação do celular e na lista da
caixa de entrada, e não diz de que lista, modalidade ou procedimento se trata. **E o corpo não diz a
situação de ninguém**: orienta a consulta na área do candidato, que é autenticada.
"""

ASSUNTO_NEUTRO = "Processo Seletivo Ifes — Nova publicação disponível"

MODELOS_INICIAIS = (
    (
        "Divulgação de resultado",
        ASSUNTO_NEUTRO,
        "Olá, {nome_do_candidato}.\n\n"
        "Foi publicado em {data_da_publicacao} o resultado {natureza_do_resultado} da etapa "
        "{etapa}, do {perfil}, no {edital}.\n\n"
        "Para consultar a sua situação, entre na área do candidato:\n"
        "{area_do_candidato}\n\n"
        "Se o Edital prevê recurso contra este resultado, o prazo e a forma estão na publicação.",
    ),
    (
        "Publicação retificadora",
        ASSUNTO_NEUTRO,
        "Olá, {nome_do_candidato}.\n\n"
        "Foi publicada em {data_da_publicacao} uma publicação retificadora do resultado "
        "{natureza_do_resultado} da etapa {etapa}, do {perfil}, no {edital}.\n\n"
        "Consulte a publicação vigente e a sua situação na área do candidato:\n"
        "{area_do_candidato}",
    ),
    (
        "Nova chamada publicada",
        ASSUNTO_NEUTRO,
        "Olá, {nome_do_candidato}.\n\n"
        "Foi publicada em {data_da_publicacao} uma nova chamada do {perfil}, no {edital}, e a "
        "sua inscrição está entre as convocadas.\n\n"
        "O que fazer e até quando estão na publicação oficial. Acompanhe também pela área do "
        "candidato: {area_do_candidato}",
    ),
)

# **O quarto, o do passo de uma Etapa restrita** (171, FR-7319, FR-7320), com marca própria: ele
# nasce também na unidade que já tem os três (research T-005). O corpo diz o nome da etapa e o
# período, e **não** diz a lista, a reserva nem o motivo do passo — o e-mail pode ser lido por outra
# pessoa, e a autodeclaração é dado sensível. O resto, o titular lê no acompanhamento, autenticado.
MODELO_DO_PASSO = (
    "Aviso do passo de uma etapa",
    ASSUNTO_NEUTRO,
    "Olá, {nome_do_candidato}.\n\n"
    "Há um passo a mais para você no {processo_seletivo}: a etapa {etapa}{periodo_da_etapa}.\n\n"
    "Veja na área do candidato quando e como participar:\n"
    "{area_do_candidato}",
)

__all__ = ["ASSUNTO_NEUTRO", "MODELOS_INICIAIS", "MODELO_DO_PASSO"]
