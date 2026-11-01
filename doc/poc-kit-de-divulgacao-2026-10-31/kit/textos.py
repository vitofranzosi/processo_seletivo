"""O kit textual: formas fechadas, preenchidas só com valores da ficha.

**Nenhuma frase diz o estado do momento.** "Inscrições abertas", "faltam 3 dias", "último dia":
o material circula por semanas, e a frase verdadeira no dia da geração fica falsa no dia seguinte.
O que se escreve é a norma — o período, em data e hora absolutas —, que continua verdadeira enquanto
o Edital não a retificar. A situação decide **se** há material, e não o que ele diz (estudo, Eixo C).

**Sem período designado, a palavra "inscrição" não aparece.** O sistema não sabe onde nem quando
essa inscrição acontece, e dizê-la seria inventar o que o Edital não declarou ao GPS (024, FR-149).

Sem IA, sem campo livre: quem quiser outro texto copia e muda fora, e o texto mudado passa a ser
dele.
"""

from processo_seletivo.portal import leitura

from .ficha import COM_PERIODO, INDISPONIVEL, NEUTRO

# As frases fixas que acompanham os dados. Ficam nomeadas para que a conferência de vocabulário as
# leia junto com o texto composto, e para que a mudança de uma delas apareça no diff como mudança de
# redação, e não perdida no meio da montagem.
INSTITUICAO = "Ifes"
RESSALVA = (
    "As informações repetem o {identificacao}, conforme a versão vigente desde {desde}. "
    "Em caso de divergência, vale o Edital."
)
CHAMADA_A_PAGINA = "Condições, documentos exigidos e cronograma completo na página oficial"
BUSCA = "Acesse {caminho} e busque por {numero}/{ano}."
TETO_NA_LEGENDA = 5


def assinatura(ficha):
    return f"{ficha['unidade_sigla']}/{INSTITUICAO}" if ficha["unidade_sigla"] else INSTITUICAO


def frase_do_periodo(ficha):
    if ficha["inicio_data"] and ficha["fim_data"]:
        return (
            f"Inscrições de {ficha['inicio_data']} a {ficha['fim_data']}, "
            f"até as {ficha['fim_hora']} (horário de Brasília)."
        )
    if ficha["inicio_data"]:
        # Sem término declarado: o sistema não inventa fechamento (`periodo_de_inscricoes`).
        return f"Inscrições a partir de {ficha['inicio_data']}, às {ficha['inicio_hora']}."
    return f"Inscrições até {ficha['fim_data']}, às {ficha['fim_hora']} (horário de Brasília)."


def frase_da_prorrogacao(ficha):
    if not ficha["prorrogado"]:
        return ""
    return (
        f"Prazo prorrogado por Retificação: o término passou de {ficha['fim_original_data']} "
        f"para {ficha['fim_data']}."
    )


def rotulo_da_oferta(oferta, ficha):
    """Como cada opção se chama numa lista: o que a distingue das outras, e nada inventado.

    Com o mesmo nome em todas (91/2026: um curso em quatro polos), o que distingue é a localidade.
    Sem localidade, o nome. Nunca "polo", "campus" ou "curso" que o dado não escreveu (069, FR-1365).
    """
    if ficha["nomes_iguais"] and oferta["localidade"]:
        return oferta["localidade"]
    return " — ".join(filter(None, (oferta["nome"], oferta["localidade"])))


def rotulos_distintos(ficha):
    """As opções se distinguem pelo que o dado escreve? Sem isso, listar é repetir a mesma linha.

    Quatro Perfis de mesmo nome sem localidade dariam quatro linhas iguais com 40 vagas cada — lidas
    como a mesma oferta quatro vezes. Aí o material conta as opções e manda à página.
    """
    rotulos = [rotulo_da_oferta(oferta, ficha) for oferta in ficha["ofertas"]]
    return len(set(rotulos)) == len(rotulos)


def linhas_da_oferta(ficha, teto=TETO_NA_LEGENDA):
    if not rotulos_distintos(ficha):
        return []
    mostradas, sobram = leitura.os_primeiros(ficha["ofertas"], teto)
    linhas = [
        f"{rotulo_da_oferta(oferta, ficha)}: {oferta['quantidade']}"
        if oferta["quantidade"]
        else rotulo_da_oferta(oferta, ficha)
        for oferta in mostradas
    ]
    if sobram:
        linhas.append(f"e mais {sobram} opç{'ões' if sobram > 1 else 'ão'} na página oficial")
    return linhas


def frase_da_oferta(ficha):
    ofertas = ficha["ofertas"]
    if not ofertas:
        return ""
    if len(ofertas) == 1:
        linha = linhas_da_oferta(ficha)[0]
        return f"Oferta: {linha}."
    # "Em N localidades" só quando toda opção declara a sua: sem localidade, o que há são N opções
    # de mesmo nome, e chamá-las de localidades afirmaria o que o Edital não escreveu.
    cabeca = (
        f"{ofertas[0]['nome']}, em {len(ofertas)} localidades"
        if ficha["nomes_iguais"] and all(oferta["localidade"] for oferta in ofertas)
        else f"{len(ofertas)} opções de oferta"
    )
    total = f" São {ficha['total_de_vagas']} vagas no total." if ficha["total_de_vagas"] else ""
    return f"{cabeca}.{total}"


def ressalva(ficha):
    return RESSALVA.format(identificacao=ficha["identificacao"], desde=ficha["versao_desde_texto"])


def compor(ficha):
    """`{nome: texto}` — o kit textual inteiro, ou vazio quando não há material."""
    if ficha["modo"] == INDISPONIVEL:
        return {}
    quem = assinatura(ficha)
    titulo = ficha["titulo_sem_numero"] or ficha["titulo"]
    busca = BUSCA.format(caminho=ficha["caminho_curto"], numero=ficha["numero"], ano=ficha["ano"])
    resumo = [f"O {quem} publicou o {ficha['identificacao']}: {titulo}."]
    if ficha["modo"] == COM_PERIODO:
        resumo.append(frase_do_periodo(ficha))
        if ficha["prorrogado"]:
            resumo.append(frase_da_prorrogacao(ficha))
    if ficha["ofertas"]:
        resumo.append(frase_da_oferta(ficha))
    resumo.append(f"{CHAMADA_A_PAGINA}: {ficha['endereco']}")

    legenda = [f"{ficha['identificacao']} — {quem}", titulo, ""]
    if ficha["modo"] == COM_PERIODO:
        legenda.append(frase_do_periodo(ficha))
        if ficha["prorrogado"]:
            legenda.append(frase_da_prorrogacao(ficha))
        legenda.append("")
    if ficha["ofertas"]:
        legenda.append(frase_da_oferta(ficha))
        legenda.extend(f"• {linha}" for linha in linhas_da_oferta(ficha))
        legenda.append("")
    # Link em legenda de rede social não é clicável, e o endereço da seleção é um UUID que ninguém
    # digita. A busca pelo número leva à mesma página, e funciona hoje (`portal/leitura.py`).
    legenda.append(f"{CHAMADA_A_PAGINA}. {busca}")
    legenda.append("")
    legenda.append(ressalva(ficha))

    if ficha["modo"] == COM_PERIODO:
        prazo = (
            f"inscrições de {ficha['inicio_data']} a {ficha['fim_data']}"
            if ficha["inicio_data"] and ficha["fim_data"]
            else frase_do_periodo(ficha).rstrip(".").lower()
        )
        chamada = f"{ficha['identificacao']} — {titulo}: {prazo}."
    else:
        chamada = f"{ficha['identificacao']} — {titulo}: Edital publicado. Consulte as condições."

    mensagem = " ".join(resumo[:-1]) + f" {CHAMADA_A_PAGINA}: {ficha['endereco']}"

    textos = {
        "resumo": " ".join(resumo),
        "legenda": "\n".join(legenda).strip(),
        "chamada_para_o_site": chamada,
        "texto_para_mensagem": mensagem,
        "link_oficial": ficha["endereco"],
        "links_por_opcao": "\n".join(
            f"{rotulo_da_oferta(o, ficha)}: {o['endereco']}" for o in ficha["ofertas"]
        ),
        "ressalva": ressalva(ficha),
    }
    return textos


def notas_para_quem_divulga(ficha):
    """O que só a comunicação lê: validade, Retificação a vigorar, o que conferir.

    **Não promete validade futura.** "Válido até 04/11" seria promessa que a próxima Retificação pode
    desmentir; o que se diz é até quando **a versão de hoje** descreve o Edital, quando isso se sabe.
    """
    notas = [
        f"Gerado sobre a versão vigente desde {ficha['versao_desde_texto']} ({ficha['versao_ato']}).",
        f"Situação conferida em {ficha['referencia_texto']}: {ficha['situacao_rotulo'] or 'sem marca'}.",
    ]
    if ficha["modo"] == NEUTRO:
        notas.append(ficha["motivo"])
    if ficha["retificacao_a_vigorar"]:
        notas.append(
            "Há Retificação publicada que passa a valer em "
            f"{ficha['retificacao_a_vigorar_texto']}. Este material descreve o Edital antes dela: "
            "gere de novo a partir dessa data."
        )
    if ficha["modo"] == COM_PERIODO and ficha["fim_data"]:
        notas.append(
            f"O período publicado termina em {ficha['fim_data']}, às {ficha['fim_hora']}. Depois disso, "
            "não republique este material."
        )
    notas.append(
        "Uma Retificação publicada depois desta geração pode mudar os dados: o GPS avisa na tela do "
        "kit quando a ficha mudar."
    )
    return notas


def em_markdown(ficha, textos, notas):
    partes = [f"# Kit de divulgação — {ficha['identificacao']}", ""]
    if ficha["modo"] == INDISPONIVEL:
        return "\n".join([*partes, f"**Sem material:** {ficha['motivo']}", ""])
    partes += ["## Para quem divulga", "", *[f"- {nota}" for nota in notas], ""]
    titulos = {
        "resumo": "Resumo institucional",
        "legenda": "Legenda para rede social",
        "chamada_para_o_site": "Chamada curta para o site",
        "texto_para_mensagem": "Texto para mensagens",
        "link_oficial": "Link oficial",
        "links_por_opcao": "Link de cada opção",
        "ressalva": "Ressalva",
    }
    for chave, titulo in titulos.items():
        if not textos.get(chave):
            continue
        partes += [f"## {titulo}", "", "```text", textos[chave], "```", ""]
    return "\n".join(partes)


def em_texto(ficha, textos, notas):
    if ficha["modo"] == INDISPONIVEL:
        return f"Sem material: {ficha['motivo']}\n"
    blocos = ["PARA QUEM DIVULGA\n" + "\n".join(f"- {n}" for n in notas)]
    for chave, texto in textos.items():
        blocos.append(f"{chave.replace('_', ' ').upper()}\n{texto}")
    return "\n\n".join(blocos) + "\n"
