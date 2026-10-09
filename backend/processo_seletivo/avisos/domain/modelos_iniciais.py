"""Os três modelos com que toda unidade começa (066, `D-008`, contracts/mensagem.md).

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
        "Foi publicado em {data_da_publicacao} o resultado {natureza_do_resultado} da etapa\n"
        "{etapa}, do {perfil}, no {edital}.\n\n"
        "Para consultar a sua situação, entre na área do candidato:\n"
        "{area_do_candidato}\n\n"
        "Se o Edital prevê recurso contra este resultado, o prazo e a forma estão na publicação.",
    ),
    (
        "Publicação retificadora",
        ASSUNTO_NEUTRO,
        "Olá, {nome_do_candidato}.\n\n"
        "Foi publicada em {data_da_publicacao} uma publicação retificadora do resultado\n"
        "{natureza_do_resultado} da etapa {etapa}, do {perfil}, no {edital}.\n\n"
        "Consulte a publicação vigente e a sua situação na área do candidato:\n"
        "{area_do_candidato}",
    ),
    (
        "Nova chamada publicada",
        ASSUNTO_NEUTRO,
        "Olá, {nome_do_candidato}.\n\n"
        "Foi publicada em {data_da_publicacao} uma nova chamada do {perfil}, no {edital}, e a\n"
        "sua inscrição está entre as convocadas.\n\n"
        "O que fazer e até quando estão na publicação oficial. Acompanhe também pela área do\n"
        "candidato: {area_do_candidato}",
    ),
)

__all__ = ["ASSUNTO_NEUTRO", "MODELOS_INICIAIS"]
