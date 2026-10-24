"""O documento do Relatório Consolidado de Gestão: camada executiva, seções e anexo (100).

**Nada aqui consulta banco nem decide número.** A composição recebe o `Consolidado` pronto e o
dispõe em blocos (`interface/diagramacao.py`), na ordem do contrato e com a organização da maquete
aprovada: a primeira página é o painel — ficha do conjunto, síntese, os seis indicadores em
cartões e os pontos de atenção —; as seções põem lado a lado o que se lê junto; o anexo abre página
própria.

**A série é gráfico**, com o número escrito ao lado de cada barra e o texto alternativo na
estrutura do arquivo. Com um mês só, uma barra não compara nada, e a série vira uma frase; sem
envio, a ausência é dita. O título diz "por mês do envio", e não "no semestre": os meses podem
passar do período que escolheu os Editais (FR-2578).

**Mesmos fatos, conjunto e instante, mesmos bytes** (FR-2568): a diagramação é determinística.
"""

from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface.diagramacao import (
    DESTAQUE,
    DIREITA,
    ESQUERDA,
    NEGRITO,
    REGULAR,
    TINTA,
    TINTA_3,
    Atencao,
    Barras,
    Cabecalho,
    Cartao,
    Cartoes,
    Celula,
    Colunas,
    Definicoes,
    Documento,
    Ficha,
    Lista,
    Nota,
    QuebraDePagina,
    Subtitulo,
    Tabela,
    Texto,
    TituloDeSecao,
    Trecho,
)
from processo_seletivo.interface.relatorio_do_edital import (
    MINIMO_PARA_DETALHAR,
    instante_por_extenso,
    interpretar,
)
from processo_seletivo.publicacoes.infrastructure.pdf import INSTITUICAO

NATUREZA = (
    "Relatório gerencial com base nos registros do GPS. Não é ato administrativo e não substitui "
    "as publicações oficiais de cada Edital."
)
NAO_REGISTRADOS = (
    "quantas pessoas participaram: o GPS conta inscrições, e a mesma pessoa pode estar em vários "
    "Editais;",
    "matrícula efetivada, nem quantas vagas foram de fato preenchidas;",
    "a data em que um evento previsto aconteceu: o GPS guarda as datas previstas e as dos atos "
    "registrados;",
    "homologação, cancelamento ou desistência de inscrição, e presença em prova;",
    "a causa de procura alta ou baixa.",
)
DEFINICOES = (
    (
        "Vagas imediatas",
        "Soma das vagas imediatas do quadro em vigor de cada Edital, com as Retificações. "
        "Cadastro de reserva não é vaga e não entra. Unidade: vaga.",
    ),
    (
        "Inscrições enviadas",
        "Inscrições com envio concluído. Unidade: inscrição, e não pessoa. Parcial enquanto algum "
        "Edital tiver o período aberto.",
    ),
    (
        "Inscrições por vaga",
        "Soma das inscrições nos perfis com vaga imediata dividida pela soma dessas vagas, com uma "
        "casa. Perfis só de cadastro de reserva ficam fora dos dois termos. Nunca é média das "
        "razões dos Editais.",
    ),
    (
        "Resultados definitivos",
        "Um resultado previsto por marco de classificação de cada perfil; definitivo quando o "
        "resultado em vigor é definitivo em todas as listas. Perfil sem inscrição não tem "
        "resultado previsto.",
    ),
    (
        "Vagas com inscrição classificada e habilitada",
        "Soma das apurações de vagas em vigor e atualizadas, do último marco de cada perfil. Não é "
        "matrícula nem aceite.",
    ),
    (
        "Convocações",
        "Convocações em vigor, pela resposta registrada mais recente. A mesma inscrição chamada "
        "duas vezes conta duas convocações.",
    ),
    (
        "Recursos",
        "Pedidos de recurso, pela situação: não admitido, indeferido, deferido (qualquer decisão "
        "que não seja indeferimento) e aguardando.",
    ),
    (
        "Providências em curso",
        "As do relatório de cada Edital: resultado não divulgado ou só preliminar, recurso ou "
        "reavaliação pendente, apuração desatualizada, convocação sem resposta.",
    ),
    (
        "Registros depois do encerramento",
        f"Registros da trilha de auditoria sobre o Edital e os atos dele. {rc.NOTA_DA_TRILHA}",
    ),
)
#: O que acompanha o "de N" de cada cartão: "6 de 6 apuradas" não se lê como "6 de 8 vagas".
COMPLEMENTOS_DO_DE = {
    "Editais com todos os resultados definitivos": "com resultado previsto",
    "vagas com inscrição classificada e habilitada": "apuradas",
    "convocações aceitas": "realizadas",
}
ENDERECOS_LOCAIS = (
    "Os endereços públicos das seleções não aparecem nesta emissão: ela foi feita num ambiente "
    "local, e o endereço não valeria para quem recebe o arquivo."
)
ENDERECOS_PUBLICOS = (
    "A página pública de cada seleção é a referência dos atos; no arquivo, a indicação abaixo do "
    "título abre o endereço."
)


def _maiuscula(texto):
    return texto[:1].upper() + texto[1:]


def _plural(n, singular, plural):
    return singular if n == 1 else plural


def _edital(edital):
    return f"{edital.number}/{edital.year}"


# --- A primeira página: o painel ----------------------------------------------------------------


def _cabecalho_e_ficha(c):
    unidade = c.unidade
    linhas_da_unidade = tuple(getattr(unidade, "cabecalho", None) or ())
    criterio = c.conjunto.criterio
    retirados = (
        "; retirados: " + ", ".join(_edital(e) for e in c.conjunto.retirados)
        if c.conjunto.retirados
        else ""
    )
    sigla = getattr(unidade, "sigla", "") or ""
    return [
        Cabecalho(linhas=(INSTITUICAO[0], INSTITUICAO[1], " ".join(linhas_da_unidade))),
        Texto(
            rc.TITULO,
            tamanho=16.5,
            fonte=NEGRITO,
            entrelinha=1.18,
            antes=12.0,
            tipo="H1",
            marcador="Relatório consolidado",
        ),
        Texto(
            f"{_maiuscula(criterio.periodo_curto)} — {c.editais} "
            f"{_plural(c.editais, 'Edital', 'Editais')}",
            tamanho=10.0,
            fonte=NEGRITO,
            cor=DESTAQUE,
            antes=3.0,
        ),
        Texto(NATUREZA, tamanho=8.2, cor=TINTA_3, antes=1.0),
        Ficha(
            [
                (
                    "Conjunto analisado",
                    criterio.rotulo + (f", da unidade {sigla}" if sigla else "") + retirados,
                    "",
                    False,
                ),
                (
                    "Data dos dados",
                    f"dados até {instante_por_extenso(c.referencia)}",
                    c.data_dos_dados,
                    False,
                ),
                ("Situação no GPS", c.situacao_no_gps, "", False),
                ("Situação das providências", c.providencias, "", bool(c.com_pendencia)),
            ]
        ),
    ]


def _cartoes(c):
    cartoes = []
    for indicador in c.indicadores:
        numero = indicador.numero
        if numero.existe:
            valor = interpretar(numero)
            de = ""
            if indicador.de is not None:
                complemento = COMPLEMENTOS_DO_DE.get(indicador.rotulo, "")
                de = f"de {indicador.de}" + (f" {complemento}" if complemento else "")
            if numero.parcial:
                de = f"{de} · parcial" if de else "parcial"
            base = indicador.base
        else:
            # A ausência é o próprio valor dito: "—" no número, e o motivo na primeira linha.
            valor, de = "—", ""
            motivo = interpretar(numero)
            base = motivo if indicador.base == motivo else f"{motivo}. {indicador.base}"
        cartoes.append(
            Cartao(valor=valor, rotulo=_maiuscula(indicador.rotulo), base=_maiuscula(base), de=de)
        )
    return Cartoes(cartoes)


def _panorama(c):
    return [
        *_cabecalho_e_ficha(c),
        TituloDeSecao("Visão geral", antes=12.0),
        Texto(" ".join(c.frases), tamanho=9.8, entrelinha=1.45, antes=5.0),
        TituloDeSecao("Principais números", antes=10.0),
        _cartoes(c),
        Atencao("Pontos de atenção", list(c.pontos_de_atencao)),
    ]


# --- Oferta e procura ---------------------------------------------------------------------------


def _tabela_simples(pares, *, larguras=(3.2, 1.0)):
    return Tabela(
        None,
        [[rotulo, valor] for rotulo, valor in pares],
        larguras=list(larguras),
        alinhamentos=[ESQUERDA, DIREITA],
    )


def _serie(c):
    if not c.envios_por_mes:
        return [Texto("Nenhuma inscrição enviada nos Editais do conjunto.", tamanho=8.8)]
    if len(c.envios_por_mes) == 1:
        (ano, mes), n = c.envios_por_mes[0]
        return [
            Texto(
                f"Todas as {n} inscrições enviadas chegaram em {rc.mes_por_extenso(ano, mes)}: "
                "com um mês só, não há série a comparar.",
                tamanho=8.8,
            )
        ]
    itens = [(rc.mes_por_extenso(ano, mes), n) for (ano, mes), n in c.envios_por_mes]
    alt = "Inscrições enviadas, por mês do envio: " + "; ".join(f"{r}, {n}" for r, n in itens) + "."
    return [Barras(itens, alt=alt)]


def _por_edital(c):
    linhas = []
    for linha in c.linhas:
        inscricoes = interpretar(linha.inscricoes)
        if linha.inscricoes.existe and linha.inscricoes.parcial:
            inscricoes += " (parcial)"
        linhas.append(
            [
                _edital(linha.edital),
                linha.edital.title,
                str(linha.perfis),
                str(linha.vagas) if linha.vagas else "só cadastro de reserva",
                inscricoes,
                interpretar(linha.por_vaga),
            ]
        )
    return Tabela(
        ["Edital", "Seleção", "Perfis", "Vagas imediatas", "Inscrições", "Por vaga"],
        linhas,
        larguras=[0.9, 3.6, 0.8, 1.2, 1.2, 1.0],
        alinhamentos=[ESQUERDA, ESQUERDA, DIREITA, DIREITA, DIREITA, DIREITA],
    )


def _perfis_com_marca(c):
    if not c.perfis_com_marca:
        return Texto("Nenhum, entre os perfis com o período de inscrições encerrado.", tamanho=8.8)
    itens = []
    for edital, nome, n, vagas, _ in c.perfis_com_marca:
        if n == 0:
            procura = "nenhuma inscrição" + (
                " no cadastro de reserva" if not vagas else f" para {vagas} vagas"
            )
        else:
            procura = (
                f"{n} {_plural(n, 'inscrição', 'inscrições')} para {vagas} "
                f"{_plural(vagas, 'vaga', 'vagas')}"
            )
        itens.append(f"{_edital(edital)} — {nome}: {procura}")
    return Lista(itens)


def _oferta_e_procura(c):
    blocos = [QuebraDePagina(), TituloDeSecao("Oferta e procura", antes=0.0)]
    if not c.universo:
        blocos.append(Texto("Não se aplica: todos os Editais do conjunto foram cancelados."))
        return blocos
    oferecido = [
        Subtitulo("O que foi oferecido", antes=0.0),
        _tabela_simples(
            [
                ("Vagas imediatas", str(c.vagas)),
                ("Em listas de ampla concorrência", str(c.vagas - c.vagas_reservadas)),
                ("Em listas reservadas", str(c.vagas_reservadas)),
                ("Perfis de vaga", str(c.perfis)),
                ("Perfis só de cadastro de reserva", str(c.perfis_so_reserva)),
            ]
        ),
        Nota(
            "As listas reservadas não se somam por modalidade: cada Edital nomeia as suas, e o GPS "
            "não tem catálogo comum entre Editais."
            + (" O Edital cancelado fica fora destes números." if c.cancelados else "")
        ),
    ]
    procura = [Subtitulo(rc.TITULO_DA_SERIE, antes=0.0), *_serie(c), Nota(rc.NOTA_DA_SERIE)]
    return [
        *blocos,
        Colunas(oferecido, procura, antes=6.0),
        Subtitulo("Por Edital", antes=12.0),
        _por_edital(c),
        Nota(
            "Inscrições por vaga de cada Edital conta só os perfis com vaga imediata. Editais de "
            "natureza diferente não são comparáveis por esta razão, e a tabela não os ordena por "
            "ela."
        ),
        Subtitulo("Perfis sem procura ou com procura menor que a oferta", antes=10.0),
        _perfis_com_marca(c),
        Nota(
            "Fato aritmético, com o período de inscrições encerrado. Ele não diz a causa: "
            "divulgação, calendário, requisitos e oferta concorrente não são registrados pelo GPS."
        ),
    ]


# --- Execução e resultados ----------------------------------------------------------------------


def _fora_pequenos(c):
    if not c.fora_dos_nao_publicos:
        return ""
    n = c.fora_dos_nao_publicos
    return (
        f" Conta {c.universo - n} dos {c.universo} Editais: {n} "
        f"{_plural(n, 'Edital', 'Editais')} com menos de {MINIMO_PARA_DETALHAR} inscrições "
        "enviadas "
        + _plural(
            n,
            "fica fora, porque o relatório dele omite",
            "ficam fora, porque o relatório deles omite",
        )
        + " estes totais."
    )


def _omitido():
    return Texto(_maiuscula(rc.OMITIDO_NO_CONJUNTO.ausencia.motivo) + ".", tamanho=8.8)


def _situacao_dos_editais(c):
    publicados = sum(1 for linha in c.relacao if linha.situacao == "Publicado")
    return [
        Subtitulo("Situação dos Editais", antes=0.0),
        Tabela(
            ["Espécie do relatório de cada Edital", "Editais"],
            [
                [
                    "De encerramento — encerrado, sem providência registrada",
                    str(c.por_especie[rel.ENCERRAMENTO]),
                ],
                [
                    "De acompanhamento — encerrado com providência em curso",
                    str(c.encerrados_com_pendencia),
                ],
                ["De acompanhamento — ainda publicado", str(publicados)],
                ["De interrupção — cancelado", str(c.por_especie[rel.INTERRUPCAO])],
            ],
            larguras=[3.4, 0.9],
            alinhamentos=[ESQUERDA, DIREITA],
        ),
        Nota("Encerrado no GPS quer dizer inscrições fechadas, e não seleção concluída."),
    ]


def _recursos(c):
    if c.recursos is None:
        return [Subtitulo("Recursos", antes=12.0), _omitido()]
    r = c.recursos
    return [
        Subtitulo("Recursos", antes=12.0),
        Tabela(
            ["Apresentados", "Não admitidos", "Indeferidos", "Deferidos", "Aguardando decisão"],
            [
                [
                    str(r.apresentados),
                    str(r.nao_admitidos),
                    str(r.indeferidos),
                    str(r.deferidos),
                    str(r.aguardando),
                ]
            ],
            larguras=[1, 1, 1, 1, 1.2],
            alinhamentos=[DIREITA] * 5,
        ),
        Nota(
            "Recursos contra etapas e resultados diferentes, somados como pedidos. Não há taxa de "
            "deferimento do conjunto: são objetos diferentes." + _fora_pequenos(c)
        ),
    ]


def _apuracao(c):
    if c.convocacoes is None:
        return [Subtitulo("Vagas imediatas, pela apuração", antes=0.0), _omitido()]
    fora = ""
    if c.fora_dos_nao_publicos:
        fora = (
            f" Fora {c.vagas_fora_dos_nao_publicos} "
            f"{_plural(c.vagas_fora_dos_nao_publicos, 'vaga', 'vagas')} de "
            f"{c.fora_dos_nao_publicos} {_plural(c.fora_dos_nao_publicos, 'Edital', 'Editais')} "
            f"com menos de {MINIMO_PARA_DETALHAR} inscrições enviadas."
        )
    return [
        Subtitulo("Vagas imediatas, pela apuração", antes=0.0),
        _tabela_simples(
            [
                ("Com inscrição classificada e habilitada", str(c.vagas_habilitadas)),
                (
                    "Apuradas sem inscrição habilitada para elas",
                    str(c.vagas_apuradas - c.vagas_habilitadas),
                ),
                ("Com apuração desatualizada", str(c.vagas_desatualizadas)),
                ("Ainda não apuradas", str(c.vagas_nao_apuradas)),
            ]
        ),
        Nota("Classificada e habilitada é a apuração da vaga, e não matrícula nem aceite." + fora),
    ]


def _convocacoes(c):
    if c.convocacoes is None:
        return [Subtitulo("Convocações", antes=12.0), _omitido()]
    k = c.convocacoes
    return [
        Subtitulo("Convocações", antes=12.0),
        Tabela(
            [
                "Realizadas",
                "Convocação aceita",
                "Aguardando resposta",
                "Prazo encerrado sem registro",
                "Outras respostas",
            ],
            [
                [
                    str(k["realizadas"]),
                    str(k["aceitas"]),
                    str(k["aguardando"]),
                    str(k["vencidas"]),
                    str(k["outros"]),
                ]
            ],
            larguras=[1, 1.1, 1.1, 1.3, 1.1],
            alinhamentos=[DIREITA] * 5,
        ),
        Nota(
            "Outras respostas são desistência, não atendimento, indeferimento da documentação e "
            "as demais registradas pela comissão. Prazo encerrado sem registro não é não "
            "atendimento: este só existe quando a comissão o registra." + _fora_pequenos(c)
        ),
    ]


def _execucao_e_resultados(c):
    blocos = [TituloDeSecao("Execução e resultados", antes=18.0)]
    if not c.universo:
        return [*blocos, *_situacao_dos_editais(c)]
    alteracoes = [
        Subtitulo("Alterações", antes=0.0),
        _tabela_simples(
            [
                ("Retificações publicadas", str(c.retificacoes)),
                ("Editais retificados", f"{c.editais_retificados} de {c.universo}"),
                ("Editais com prazo de inscrição prorrogado", str(c.prorrogados)),
            ]
        ),
        Nota(
            "A prorrogação é uma Retificação que adia o término das inscrições; as demais mudanças "
            "de data estão no relatório de cada Edital."
        ),
    ]
    resultados = [
        Subtitulo("Resultados publicados", antes=0.0),
        _tabela_simples(
            [
                ("Resultados previstos (um por marco de cada perfil)", str(c.marcos_declarados)),
                ("Com resultado definitivo em vigor", str(c.marcos_definitivos)),
                ("Ainda sem resultado definitivo", str(c.marcos_declarados - c.marcos_definitivos)),
            ]
        ),
    ]
    return [
        *blocos,
        Colunas(_situacao_dos_editais(c), alteracoes, antes=6.0),
        *_recursos(c),
        Colunas(resultados, _apuracao(c), antes=12.0),
        *_convocacoes(c),
    ]


# --- Providências -------------------------------------------------------------------------------


def _providencias(c):
    blocos = [TituloDeSecao("Providências", antes=18.0), Subtitulo("Em curso, por tipo", antes=4.0)]
    if c.pendencias_por_tipo:
        blocos.append(
            Tabela(
                ["Tipo", "Editais", "Ocorrências"],
                [[_maiuscula(tipo), str(e), str(n)] for tipo, e, n in c.pendencias_por_tipo],
                larguras=[4.0, 0.9, 1.1],
                alinhamentos=[ESQUERDA, DIREITA, DIREITA],
            )
        )
        blocos.append(
            Nota(
                "Cada tipo é uma regra do relatório do Edital. O conjunto não cria pendência: "
                "conta as de cada Edital."
            )
        )
    else:
        blocos.append(Texto("Nenhuma providência pendente registrada no GPS.", tamanho=8.8))

    if c.providencias_por_edital:
        linhas = []
        for p in c.providencias_por_edital:
            itens = [rc.texto_do_item(tipo, n) for tipo, n in p.itens]
            if p.omitido:
                itens.append(
                    f"providência com detalhe omitido: menos de {MINIMO_PARA_DETALHAR} inscrições "
                    "neste Edital"
                )
            linhas.append([_edital(p.edital), p.situacao, "; ".join(itens)])
        blocos.append(Subtitulo("Por Edital", antes=10.0))
        blocos.append(
            Tabela(
                ["Edital", "Situação no GPS", "Providências em curso"],
                linhas,
                larguras=[0.9, 1.9, 4.2],
            )
        )

    blocos.append(Subtitulo("Registros na trilha depois do encerramento", antes=10.0))
    if c.posteriores_por_edital:
        blocos.append(
            Tabela(
                ["Edital", "Encerrado em", "Registros na trilha"],
                [
                    [_edital(edital), rc.texto_da_primeira(desfecho), str(n)]
                    for edital, desfecho, n in c.posteriores_por_edital
                ],
                larguras=[1.2, 1.6, 1.6],
                alinhamentos=[ESQUERDA, ESQUERDA, DIREITA],
            )
        )
        blocos.append(
            Nota(
                f"{rc.NOTA_DA_TRILHA} Registro depois do encerramento não é irregularidade: "
                "suplência e resposta a convocação podem ser exatamente o que o Edital previa."
            )
        )
    else:
        blocos.append(Texto("Nenhum registro na trilha depois do encerramento.", tamanho=8.8))
    blocos.append(Subtitulo("O que este relatório não diz", antes=10.0))
    blocos.append(Lista(list(NAO_REGISTRADOS)))
    return blocos


# --- O anexo técnico ----------------------------------------------------------------------------


def _relacao(c):
    linhas = []
    for linha in c.relacao:
        endereco = c.enderecos.get(linha.edital.pk)
        titulo = [(linha.edital.title, None, REGULAR, TINTA, None)]
        if endereco:
            titulo.append(("página pública da seleção", 7.2, REGULAR, DESTAQUE, endereco))
        linhas.append(
            [
                _edital(linha.edital),
                Celula(titulo),
                rc.texto_da_primeira(linha.primeira),
                linha.situacao,
                linha.especie,
            ]
        )
    return Tabela(
        ["Edital", "Seleção", "1ª publicação", "Situação no GPS", "Espécie"],
        linhas,
        larguras=[0.9, 3.4, 1.1, 1.7, 1.3],
    )


def _criterio(c):
    conjunto = c.conjunto
    pares = [("Critério", conjunto.criterio.rotulo + ".")]
    if conjunto.criterio.modo == rc.PUBLICACAO:
        pares.append(
            ("A data", "É a da primeira publicação do Edital no GPS, e não a das Retificações.")
        )
    elif conjunto.criterio.modo == rc.NUMERO:
        pares.append(("O ano", "É o do número do Edital, e não o da publicação nem o de ingresso."))
    if conjunto.retirados:
        pares.append(
            ("Retirados por escolha", ", ".join(_edital(e) for e in conjunto.retirados) + ".")
        )
    if conjunto.fora:
        pares.append(
            (
                "Fora do conjunto",
                "; ".join(f"{_edital(e)}, {motivo}" for e, motivo in conjunto.fora) + ".",
            )
        )
    pares.append(
        (
            "Data dos dados",
            f"{instante_por_extenso(c.referencia)}. {c.data_dos_dados} O relatório não "
            "reconstitui o passado.",
        )
    )
    return Definicoes(pares)


def _anexo(c, emissao):
    sigla = getattr(c.unidade, "sigla", "") or "da unidade"
    return [
        QuebraDePagina(),
        TituloDeSecao("Anexo técnico", antes=0.0, tamanho=13.0, tipo="H1"),
        Nota(
            "Para a equipe responsável e as instâncias de controle. Cada Edital tem relatório "
            "próprio, emitido na tela dele, com etapas, listas, cronograma e documentos oficiais.",
            antes=4.0,
        ),
        TituloDeSecao("A1. Editais considerados", antes=12.0),
        _relacao(c),
        Nota(ENDERECOS_LOCAIS if c.enderecos_locais else ENDERECOS_PUBLICOS),
        TituloDeSecao("A2. Critério do conjunto", antes=14.0),
        _criterio(c),
        TituloDeSecao("A3. Definição de cada número", antes=14.0),
        Definicoes(list(DEFINICOES)),
        TituloDeSecao("A4. Limitações", antes=14.0),
        Lista(
            [
                "Fatos não públicos — recursos, convocações, apurações — aparecem no total do "
                "conjunto e por Edital, nunca por perfil ou por lista. O Edital com menos de "
                f"{MINIMO_PARA_DETALHAR} inscrições enviadas não entra neles, porque o relatório "
                "dele os omite; ele continua nas vagas e nas inscrições.",
                "As listas reservadas não se somam entre Editais por modalidade, e a localidade do "
                "perfil é texto do Edital: nenhuma das duas vira agrupamento.",
                "O Edital cancelado conta como Edital, na situação e na relação, e fica fora de "
                "todo número.",
            ]
        ),
        TituloDeSecao("A5. Sobre esta emissão", antes=14.0),
        Texto(
            [
                Trecho(f"Emissão nº {emissao}", NEGRITO),
                Trecho(
                    f" do relatório consolidado da unidade {sigla}, com dados até "
                    f"{instante_por_extenso(c.referencia)}. Fica registrada na trilha de auditoria "
                    "do GPS, com o critério, os Editais incluídos, a data, o autor e o resumo do "
                    "arquivo. Uma nova emissão pode trazer números diferentes para os mesmos "
                    "Editais."
                ),
            ],
            tamanho=8.8,
        ),
    ]


def documento(c, *, emissao):
    """O documento inteiro, em blocos — é o que os testes de diagramação leem."""
    return Documento(
        blocos=[
            *_panorama(c),
            *_oferta_e_procura(c),
            *_execucao_e_resultados(c),
            *_providencias(c),
            *_anexo(c, emissao),
        ],
        faixa_esquerda=f"Relatório Consolidado de Gestão · {c.conjunto.criterio.periodo_curto}",
        faixa_direita=f"dados até {instante_por_extenso(c.referencia)} · emissão nº {emissao}",
        pe="Relatório gerencial: não é ato administrativo e não substitui as publicações oficiais",
        titulo=f"{rc.TITULO} — {c.conjunto.criterio.periodo_curto}",
        autor=getattr(c.unidade, "nome", "") or "",
    )


def compor(c, *, emissao) -> bytes:
    """Os bytes do documento. Mesmo consolidado e mesma emissão, mesmos bytes (FR-2568)."""
    return documento(c, emissao=emissao).compor()
