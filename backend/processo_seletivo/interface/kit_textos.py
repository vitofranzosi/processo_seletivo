"""O kit textual do Edital: formas fechadas, preenchidas só com valores da ficha (111, FR-3412).

**Nenhuma frase diz o estado do momento.** "Inscrições abertas", "faltam 3 dias", "último dia": o
material circula por semanas, e a frase verdadeira no dia da geração fica falsa no dia seguinte. O
que se escreve é a norma, o período em data e hora absolutas, que continua verdadeira enquanto o
Edital não a retificar. A situação decide **se** há material, e não o que ele diz (`FR-3414`).

**Sem período designado, a palavra "inscrição" não aparece.** O sistema não sabe onde nem quando
essa inscrição acontece (`FR-3416`; FR-149 da `024`).

Sem campo livre e sem modelo de linguagem (`FR-3413`): quem quiser outro texto copia e muda fora, e
o texto mudado passa a ser dele.
"""

from processo_seletivo.portal.ficha import COM_PERIODO, NEUTRO, SEM_MATERIAL

# As frases fixas que acompanham os dados. Nomeadas, para que a varredura de vocabulário as leia e
# para que a mudança de uma delas apareça no diff como mudança de redação.
INSTITUICAO = "Ifes"
RESSALVA = (
    "As informações repetem o {identificacao}, conforme a versão vigente desde {desde}. "
    "Em caso de divergência, vale o Edital."
)
CHAMADA_A_PAGINA = "Condições, documentos exigidos e cronograma completo na página oficial"
BUSCA = "Acesse {caminho} e busque por {numero}/{ano}{sigla}."

#: O teto único de opções listadas, na peça e na legenda (`FR-3425`).
TETO_DE_OPCOES = 4

TITULOS = {
    "resumo": "Resumo institucional",
    "legenda": "Legenda para rede social",
    "chamada_para_o_site": "Chamada curta para o site",
    "texto_para_mensagem": "Texto para mensagens",
    "link_oficial": "Link oficial",
    "links_por_opcao": "Link de cada opção",
    "ressalva": "Ressalva",
}


def assinatura(ficha):
    return f"{ficha.unidade_sigla}/{INSTITUICAO}" if ficha.unidade_sigla else INSTITUICAO


def titulo(ficha):
    return ficha.titulo_sem_numero or ficha.titulo


def frase_do_periodo(ficha):
    if ficha.inicio_data and ficha.fim_data:
        return (
            f"Inscrições de {ficha.inicio_data} a {ficha.fim_data}, "
            f"até as {ficha.fim_hora} (horário de Brasília)."
        )
    if ficha.inicio_data:
        # Sem término declarado: o sistema não inventa fechamento (`EC-6`).
        return f"Inscrições a partir de {ficha.inicio_data}, às {ficha.inicio_hora}."
    return f"Inscrições até {ficha.fim_data}, às {ficha.fim_hora} (horário de Brasília)."


def frase_da_prorrogacao(ficha):
    if not ficha.prorrogado:
        return ""
    return (
        f"Prazo prorrogado por Retificação: o término passou de {ficha.fim_original_texto} "
        f"para {ficha.fim_vigente_texto}."
    )


def rotulo_da_oferta(oferta, ficha):
    """O que distingue a opção das outras, e nada inventado (`FR-3409`).

    Com o mesmo nome em todas (91/2026: um curso em quatro polos), o que distingue é a localidade.
    Sem localidade, o nome. Nunca "polo", "campus" ou "curso" que o dado não escreveu.
    """
    if ficha.nomes_iguais and oferta.localidade:
        return oferta.localidade
    return " — ".join(filter(None, (oferta.nome, oferta.localidade)))


def rotulos_distintos(ficha):
    """As opções se distinguem pelo que o dado escreve? Sem isso, listar repete a mesma linha."""
    rotulos = [rotulo_da_oferta(oferta, ficha) for oferta in ficha.ofertas]
    return len(set(rotulos)) == len(rotulos)


def lista_as_opcoes(ficha):
    return 0 < len(ficha.ofertas) <= TETO_DE_OPCOES and rotulos_distintos(ficha)


def linhas_da_oferta(ficha):
    return [
        f"{rotulo_da_oferta(oferta, ficha)}: {oferta.quantidade}"
        if oferta.quantidade
        else rotulo_da_oferta(oferta, ficha)
        for oferta in ficha.ofertas
    ]


def total_em_frase(ficha):
    """A soma, sempre com o número de opções que a repartem (`FR-3425`).

    É a exceção declarada à FR-1607 da `072`: "160 vagas" sozinho se lê como de cada polo.
    """
    if not ficha.total_de_vagas:
        return ""
    if len(ficha.ofertas) == 1:
        return ""
    return f"{ficha.total_de_vagas} vagas em {len(ficha.ofertas)} opções"


def frase_da_oferta(ficha):
    ofertas = ficha.ofertas
    if not ofertas:
        return ""
    if len(ofertas) == 1:
        return f"Oferta: {linhas_da_oferta(ficha)[0]}."
    # "Em N localidades" só quando toda opção declara a sua: sem localidade, o que há são N opções
    # de mesmo nome, e chamá-las de localidades afirmaria o que o Edital não escreveu.
    cabeca = (
        f"{ofertas[0].nome}, em {len(ofertas)} localidades"
        if ficha.nomes_iguais and all(oferta.localidade for oferta in ofertas)
        else f"{len(ofertas)} opções de oferta"
    )
    total = total_em_frase(ficha)
    return f"{cabeca}: {total}." if total else f"{cabeca}."


def ressalva(ficha):
    return RESSALVA.format(identificacao=ficha.identificacao, desde=ficha.versao_desde_texto)


def busca(ficha):
    sigla = f" – {ficha.unidade_sigla}" if ficha.unidade_sigla else ""
    return BUSCA.format(
        caminho=ficha.caminho_curto, numero=ficha.numero, ano=ficha.ano, sigla=sigla
    )


def compor(ficha):
    """`{nome: texto}` — o kit textual publicável, ou vazio quando não há material."""
    if ficha.modo == SEM_MATERIAL:
        return {}
    quem = assinatura(ficha)
    # Em host local não há endereço público (FR-3447): a frase termina na chamada, e o link
    # oficial não sai. Um texto pronto para copiar não pode levar um aviso no lugar do link.
    destino = f"{CHAMADA_A_PAGINA}: {ficha.endereco}" if ficha.endereco else f"{CHAMADA_A_PAGINA}."

    resumo = [f"O {quem} publicou o {ficha.identificacao}: {titulo(ficha)}."]
    if ficha.modo == COM_PERIODO:
        resumo.append(frase_do_periodo(ficha))
        if ficha.prorrogado:
            resumo.append(frase_da_prorrogacao(ficha))
    if ficha.ofertas:
        resumo.append(frase_da_oferta(ficha))

    legenda = [f"{ficha.identificacao} — {quem}", titulo(ficha), ""]
    if ficha.modo == COM_PERIODO:
        legenda.append(frase_do_periodo(ficha))
        if ficha.prorrogado:
            legenda.append(frase_da_prorrogacao(ficha))
        legenda.append("")
    if ficha.ofertas:
        legenda.append(frase_da_oferta(ficha))
        if lista_as_opcoes(ficha) and len(ficha.ofertas) > 1:
            legenda.extend(f"• {linha}" for linha in linhas_da_oferta(ficha))
        elif len(ficha.ofertas) > 1:
            legenda.append("Confira todas as opções na página oficial.")
        legenda.append("")
    # Link em legenda de rede social não é clicável, e o endereço da seleção é um UUID que ninguém
    # digita. A busca pelo número, com a sigla, leva à mesma página (`FR-3418`).
    if ficha.caminho_curto:
        legenda.append(f"{CHAMADA_A_PAGINA}. {busca(ficha)}")
    else:
        legenda.append(f"{CHAMADA_A_PAGINA}.")
    legenda += ["", ressalva(ficha)]

    if ficha.modo == COM_PERIODO and ficha.inicio_data and ficha.fim_data:
        prazo = f"inscrições de {ficha.inicio_data} a {ficha.fim_data}"
    elif ficha.modo == COM_PERIODO:
        prazo = frase_do_periodo(ficha).rstrip(".").lower()
    else:
        prazo = "Edital publicado; consulte as condições"
    chamada = f"{ficha.identificacao} — {titulo(ficha)}: {prazo}."

    publicaveis = {
        "resumo": " ".join([*resumo, destino]),
        "legenda": "\n".join(legenda).strip(),
        "chamada_para_o_site": chamada,
        "texto_para_mensagem": " ".join([*resumo, destino]),
        "link_oficial": ficha.endereco or "",
        "links_por_opcao": "\n".join(
            f"{rotulo_da_oferta(o, ficha)}: {ficha.endereco}{o.ancora}"
            for o in ficha.ofertas
            if ficha.endereco
        ),
        "ressalva": ressalva(ficha),
    }
    return {chave: texto for chave, texto in publicaveis.items() if texto}


def notas_para_quem_divulga(ficha):
    """O que só a comunicação lê (`FR-3421`). **Não promete validade**: diz até quando a versão de
    hoje descreve o Edital, quando isso se sabe, e que uma Retificação pode mudar os dados."""
    notas = [
        f"Gerado sobre a versão vigente desde {ficha.versao_desde_texto} ({ficha.versao_ato}).",
        f"Situação conferida em {ficha.referencia_texto}: {ficha.situacao_rotulo or 'sem marca'}.",
    ]
    if ficha.modo == NEUTRO:
        notas.append(ficha.motivo)
    if ficha.retificacao_a_vigorar:
        notas.append(
            "Há Retificação publicada que passa a valer em "
            f"{ficha.retificacao_a_vigorar_texto}. Este material descreve o Edital antes dela: "
            "gere de novo a partir dessa data."
        )
    if ficha.modo == COM_PERIODO and ficha.fim_data:
        notas.append(
            f"O período publicado termina em {ficha.fim_data}, às {ficha.fim_hora}. Depois disso, "
            "não republique este material."
        )
    if not ficha.endereco:
        notas.append("Acesso por endereço local: os textos saem sem link absoluto.")
    notas.append(
        "Uma Retificação publicada depois desta geração pode mudar os dados: o GPS avisa na tela "
        "do kit quando o material exportado deixar de corresponder ao Edital."
    )
    return notas


def conferencia(ficha):
    """As informações oficiais, para conferir antes de usar, com a origem de cada valor."""
    # O título sem o prefixo que repete o número: "Edital nº 91/2026 — Edital nº 91/2026 – …" era o
    # mesmo dado duas vezes na primeira linha. As linhas vão sem marcador: quem as desenha o põe.
    linhas = [f"{ficha.identificacao} — {titulo(ficha)}", f"Unidade: {assinatura(ficha)}"]
    if ficha.modo == COM_PERIODO:
        linhas.append(frase_do_periodo(ficha))
        if ficha.prorrogado:
            linhas.append(frase_da_prorrogacao(ficha))
    linhas += [f"Oferta — {linha}" for linha in linhas_da_oferta(ficha)]
    if ficha.endereco:
        linhas.append(f"Página oficial: {ficha.endereco}")
    linhas.append(f"Versão: {ficha.versao_ato}, vigente desde {ficha.versao_desde_texto}.")
    for origem in ficha.origens:
        linhas.append(f"Origem — {origem.campo}: {', '.join(origem.atos) or 'sem registro'}")
    for termo in ficha.termos_em_valor_oficial:
        linhas.append(f"Atenção: o valor oficial «{termo}» tem termo que o material não usaria.")
    return linhas


def em_markdown(ficha, textos, notas):
    partes = [f"# Kit de divulgação — {ficha.identificacao}", ""]
    if ficha.modo == SEM_MATERIAL:
        return "\n".join([*partes, f"**Sem material:** {ficha.motivo}", ""])
    partes += ["## Informações oficiais", "", *[f"- {linha}" for linha in conferencia(ficha)], ""]
    partes += ["## Para quem divulga", "", *[f"- {nota}" for nota in notas], ""]
    for chave, nome in TITULOS.items():
        if textos.get(chave):
            partes += [f"## {nome}", "", "```text", textos[chave], "```", ""]
    return "\n".join(partes)


def em_texto(ficha, textos, notas):
    if ficha.modo == SEM_MATERIAL:
        return f"Sem material: {ficha.motivo}\n"
    blocos = [
        "INFORMAÇÕES OFICIAIS\n" + "\n".join(f"- {linha}" for linha in conferencia(ficha)),
        "PARA QUEM DIVULGA\n" + "\n".join(f"- {n}" for n in notas),
    ]
    for chave, nome in TITULOS.items():
        if textos.get(chave):
            blocos.append(f"{nome.upper()}\n{textos[chave]}")
    return "\n\n".join(blocos) + "\n"
