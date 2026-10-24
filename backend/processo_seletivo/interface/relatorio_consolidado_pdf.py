"""O documento do relatório consolidado da unidade: camada executiva, seções e anexo (100).

**Nada aqui consulta banco nem decide número.** A composição recebe o `Consolidado` pronto e o
escreve, na ordem do contrato (`contracts/relatorio-consolidado.md`). O escritor é o do relatório
do Edital (R-011): links, marcadores, fonte embutida e saída determinística — mesmos fatos, mesmo
conjunto e mesmo instante, mesmos bytes (FR-2568).

**Não há gráfico.** O motor não o desenha, e a série de envios é uma tabela por mês — que é o
próprio equivalente textual. O título diz "por mês do envio", e não "no semestre": os meses podem
passar do período que escolheu os Editais (FR-2578).
"""

from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface.relatorio_do_edital import (
    MINIMO_PARA_DETALHAR,
    instante_por_extenso,
    interpretar,
    texto_do_indicador,
)
from processo_seletivo.interface.relatorio_pdf import (
    _nota,
    _par,
    _paragrafo,
    _secao,
    _subtitulo,
)
from processo_seletivo.publicacoes.infrastructure.pdf import (
    ALTURA_DO_BRASAO,
    ANTES_DE_BLOCO,
    ANTES_DE_LINHA,
    ANTES_DE_PARAGRAFO,
    CENTRO,
    CORPO_ATO,
    CORPO_NOTA,
    CORPO_TEXTO,
    DIREITA,
    ESQUERDA,
    METRICA_DO_EDITAL,
    NEGRITO,
    Composicao,
    Navegacao,
    UnidadeDoAto,
    _arquivo_do_edital,
    _tabela,
    linhas_do_orgao,
)

NATUREZA = (
    "Relatório gerencial com base nos registros do GPS. Não é ato administrativo e não substitui "
    "as publicações oficiais de cada Edital."
)
NAO_REGISTRADOS = (
    "quantas pessoas participaram: o GPS conta inscrições, e a mesma pessoa pode estar em vários "
    "Editais",
    "matrícula efetivada, nem quantas vagas foram de fato preenchidas",
    "a data em que um evento previsto aconteceu: o GPS guarda as datas previstas e as dos atos "
    "registrados",
    "homologação, cancelamento ou desistência de inscrição, e presença em prova",
    "a causa de procura alta ou baixa",
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
SECOES = (
    "1. Visão geral",
    "2. Principais números",
    "3. Pontos de atenção",
    "4. Oferta e procura",
    "5. Execução e resultados",
    "6. Providências",
    "A1. Editais considerados",
    "A2. Critério do conjunto",
    "A3. Definição de cada número",
    "A4. Limitações",
    "A5. Sobre esta emissão",
)


def _maiuscula(texto):
    return texto[:1].upper() + texto[1:]


def _identificacao(c, emissao):
    return (
        f"Relatório consolidado · {c.conjunto.criterio.periodo_curto} · dados até "
        f"{instante_por_extenso(c.referencia)} · emissão nº {emissao} · relatório gerencial"
    )


def _cabecalho(composicao, c, emissao):
    unidade = UnidadeDoAto(cabecalho=tuple(getattr(c.unidade, "cabecalho", None) or ()), local="")
    composicao.espaco(ALTURA_DO_BRASAO - 10)
    for indice, linha in enumerate(linhas_do_orgao(unidade)):
        composicao.escrever(
            linha, tamanho=CORPO_TEXTO, alinhamento=CENTRO, antes=0.0 if indice else 4.0
        )
    composicao.escrever(
        c.titulo.upper(), tamanho=CORPO_ATO, fonte=NEGRITO, antes=16, alinhamento=CENTRO
    )
    composicao.escrever(
        f"{_maiuscula(c.conjunto.criterio.periodo_curto)} — {c.editais} "
        f"{'Edital' if c.editais == 1 else 'Editais'}",
        tamanho=CORPO_TEXTO,
        fonte=NEGRITO,
        antes=ANTES_DE_LINHA,
        alinhamento=CENTRO,
    )
    composicao.escrever(NATUREZA, tamanho=CORPO_NOTA, antes=ANTES_DE_LINHA, alinhamento=CENTRO)
    sigla = getattr(c.unidade, "sigla", "") or ""
    _par(
        composicao,
        "Conjunto analisado",
        f"{c.conjunto.criterio.rotulo}" + (f", da unidade {sigla}" if sigla else ""),
    )
    _par(composicao, "Data dos dados", f"dados até {instante_por_extenso(c.referencia)}")
    _nota(composicao, c.data_dos_dados)
    _par(composicao, "Situação no GPS", c.situacao_no_gps)
    _par(composicao, "Situação das providências", c.providencias)
    _par(composicao, "Emissão", f"nº {emissao}")


def _visao_geral(composicao, c):
    _secao(composicao, "1. Visão geral")
    _paragrafo(composicao, " ".join(c.frases))


def _numeros(composicao, c):
    _secao(composicao, "2. Principais números")
    _tabela(
        composicao,
        ["Indicador", "Valor", "O que o número diz"],
        [[_maiuscula(i.rotulo), texto_do_indicador(i), i.base] for i in c.indicadores],
        recuo=0.0,
        alinhamentos=[ESQUERDA, DIREITA, ESQUERDA],
    )


def _atencao(composicao, c):
    _secao(composicao, "3. Pontos de atenção")
    for indice, (titulo, texto) in enumerate(c.pontos_de_atencao, 1):
        composicao.escrever(
            f"{indice}. {titulo}", tamanho=CORPO_TEXTO, fonte=NEGRITO, antes=ANTES_DE_PARAGRAFO
        )
        composicao.escrever(texto, tamanho=CORPO_TEXTO, recuo=12.0, justificar=True)


def _oferta_e_procura(composicao, c):
    _secao(composicao, "4. Oferta e procura")
    if not c.universo:
        _paragrafo(composicao, "Não se aplica: todos os Editais do conjunto foram cancelados.")
        return
    _subtitulo(composicao, "O que foi oferecido")
    linhas = [
        ["Vagas imediatas", str(c.vagas)],
        ["Em listas de ampla concorrência", str(c.vagas - c.vagas_reservadas)],
        ["Em listas reservadas", str(c.vagas_reservadas)],
        ["Perfis de vaga", str(c.perfis)],
        ["Perfis só de cadastro de reserva", str(c.perfis_so_reserva)],
    ]
    _tabela(composicao, ["", "Total"], linhas, recuo=0.0, alinhamentos=[ESQUERDA, DIREITA])
    _nota(
        composicao,
        "As listas reservadas não se somam por modalidade: cada Edital nomeia as suas, e o GPS não "
        "tem catálogo comum entre Editais."
        + (" O Edital cancelado fica fora destes números." if c.cancelados else ""),
    )

    _subtitulo(composicao, rc.TITULO_DA_SERIE)
    if c.envios_por_mes:
        _tabela(
            composicao,
            ["Mês do envio", "Inscrições enviadas"],
            [[rc.mes_por_extenso(ano, mes), str(n)] for (ano, mes), n in c.envios_por_mes],
            recuo=0.0,
            alinhamentos=[ESQUERDA, DIREITA],
        )
        _nota(composicao, rc.NOTA_DA_SERIE)
    else:
        _paragrafo(composicao, "Nenhuma inscrição enviada.")

    _subtitulo(composicao, "Por Edital")
    _tabela(
        composicao,
        ["Edital", "Seleção", "Perfis", "Vagas imediatas", "Inscrições enviadas", "Por vaga"],
        [
            [
                f"{linha.edital.number}/{linha.edital.year}",
                linha.edital.title,
                str(linha.perfis),
                str(linha.vagas) if linha.vagas else "só cadastro de reserva",
                interpretar(linha.inscricoes)
                + (" (parcial)" if linha.inscricoes.existe and linha.inscricoes.parcial else ""),
                interpretar(linha.por_vaga),
            ]
            for linha in c.linhas
        ],
        recuo=0.0,
        alinhamentos=[ESQUERDA, ESQUERDA, DIREITA, DIREITA, DIREITA, DIREITA],
    )
    _nota(
        composicao,
        "Inscrições por vaga de cada Edital conta só os perfis com vaga imediata. Editais de "
        "natureza diferente não são comparáveis por esta razão, e a tabela não os ordena por ela.",
    )

    _subtitulo(composicao, "Perfis sem procura ou com procura menor que a oferta")
    if c.perfis_com_marca:
        for edital, nome, n, vagas, _ in c.perfis_com_marca:
            if n == 0:
                procura = "nenhuma inscrição" + (
                    " no cadastro de reserva" if not vagas else f" para {vagas} vagas"
                )
            else:
                procura = (
                    f"{n} {'inscrição' if n == 1 else 'inscrições'} para {vagas} "
                    f"{'vaga' if vagas == 1 else 'vagas'}"
                )
            _paragrafo(
                composicao,
                f"{edital.number}/{edital.year} — {nome}: {procura}",
                antes=ANTES_DE_LINHA,
            )
    else:
        _paragrafo(composicao, "Nenhum, entre os perfis com o período de inscrições encerrado.")
    _nota(
        composicao,
        "Fato aritmético, com o período de inscrições encerrado. Ele não diz a causa: divulgação, "
        "calendário, requisitos e oferta concorrente não são registrados pelo GPS.",
    )


def _execucao_e_resultados(composicao, c):
    _secao(composicao, "5. Execução e resultados")
    _subtitulo(composicao, "Situação dos Editais")
    especies = c.por_especie
    publicados = sum(1 for linha in c.relacao if linha.situacao == "Publicado")
    _tabela(
        composicao,
        ["Espécie do relatório de cada Edital", "Editais"],
        [
            [
                "De encerramento — encerrado, sem providência registrada",
                str(especies[rel.ENCERRAMENTO]),
            ],
            [
                "De acompanhamento — encerrado com providência em curso",
                str(c.encerrados_com_pendencia),
            ],
            ["De acompanhamento — ainda publicado", str(publicados)],
            ["De interrupção — cancelado", str(especies[rel.INTERRUPCAO])],
        ],
        recuo=0.0,
        alinhamentos=[ESQUERDA, DIREITA],
    )
    _nota(
        composicao,
        "Encerrado no GPS quer dizer inscrições fechadas, e não seleção concluída.",
    )
    if not c.universo:
        return

    _subtitulo(composicao, "Alterações")
    _tabela(
        composicao,
        ["", "Total"],
        [
            ["Retificações publicadas", str(c.retificacoes)],
            ["Editais retificados", f"{c.editais_retificados} de {c.universo}"],
            ["Editais com prazo de inscrição prorrogado", str(c.prorrogados)],
        ],
        recuo=0.0,
        alinhamentos=[ESQUERDA, DIREITA],
    )
    _nota(
        composicao,
        "A prorrogação é uma Retificação que adia o término das inscrições; as demais mudanças de "
        "data estão no relatório de cada Edital.",
    )

    _subtitulo(composicao, "Recursos")
    if c.recursos is None:
        _paragrafo(composicao, _maiuscula(rc.OMITIDO_NO_CONJUNTO.ausencia.motivo) + ".")
    else:
        r = c.recursos
        _tabela(
            composicao,
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
            recuo=0.0,
            alinhamentos=[DIREITA] * 5,
        )
        _nota(
            composicao,
            "Recursos contra etapas e resultados diferentes, somados como pedidos. Não há taxa de "
            "deferimento do conjunto: são objetos diferentes." + _fora_pequenos(c),
        )

    _subtitulo(composicao, "Resultados publicados")
    _tabela(
        composicao,
        ["", "Total"],
        [
            [
                "Resultados previstos (um por marco de classificação de cada perfil)",
                str(c.marcos_declarados),
            ],
            ["Com resultado definitivo em vigor", str(c.marcos_definitivos)],
            [
                "Ainda sem resultado definitivo",
                str(c.marcos_declarados - c.marcos_definitivos),
            ],
        ],
        recuo=0.0,
        alinhamentos=[ESQUERDA, DIREITA],
    )

    _subtitulo(composicao, "Vagas imediatas, pela apuração")
    if c.convocacoes is None:
        _paragrafo(composicao, _maiuscula(rc.OMITIDO_NO_CONJUNTO.ausencia.motivo) + ".")
    else:
        _tabela(
            composicao,
            ["", "Vagas"],
            [
                ["Com inscrição classificada e habilitada", str(c.vagas_habilitadas)],
                [
                    "Apuradas sem inscrição habilitada para elas",
                    str(c.vagas_apuradas - c.vagas_habilitadas),
                ],
                ["Com apuração desatualizada", str(c.vagas_desatualizadas)],
                ["Ainda não apuradas", str(c.vagas_nao_apuradas)],
            ],
            recuo=0.0,
            alinhamentos=[ESQUERDA, DIREITA],
        )
        _nota(
            composicao,
            "Classificada e habilitada é a apuração da vaga, e não matrícula nem aceite."
            + _fora_pequenos(c),
        )

    _subtitulo(composicao, "Convocações")
    if c.convocacoes is None:
        _paragrafo(composicao, _maiuscula(rc.OMITIDO_NO_CONJUNTO.ausencia.motivo) + ".")
    else:
        k = c.convocacoes
        _tabela(
            composicao,
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
            recuo=0.0,
            alinhamentos=[DIREITA] * 5,
        )
        _nota(
            composicao,
            "Outras respostas são desistência, não atendimento, indeferimento da documentação e as "
            "demais registradas pela comissão. Prazo encerrado sem registro não é não atendimento: "
            "este só existe quando a comissão o registra." + _fora_pequenos(c),
        )


def _fora_pequenos(c):
    if not c.fora_dos_nao_publicos:
        return ""
    n = c.fora_dos_nao_publicos
    return (
        f" Fora {n} {'Edital' if n == 1 else 'Editais'} com menos de {MINIMO_PARA_DETALHAR} "
        "inscrições enviadas, cujo relatório individual omite estes totais."
    )


def _providencias(composicao, c):
    _secao(composicao, "6. Providências")
    _subtitulo(composicao, "Em curso, por tipo")
    if c.pendencias_por_tipo:
        _tabela(
            composicao,
            ["Tipo", "Editais", "Ocorrências"],
            [[_maiuscula(tipo), str(e), str(n)] for tipo, e, n in c.pendencias_por_tipo],
            recuo=0.0,
            alinhamentos=[ESQUERDA, DIREITA, DIREITA],
        )
        _nota(
            composicao,
            "Cada tipo é uma regra do relatório do Edital. O conjunto não cria pendência: conta as "
            "de cada Edital.",
        )
    else:
        _paragrafo(composicao, "Nenhuma providência pendente registrada no GPS.")

    if c.providencias_por_edital:
        _subtitulo(composicao, "Por Edital")
        linhas = []
        for p in c.providencias_por_edital:
            itens = [rc.texto_do_item(tipo, n) for tipo, n in p.itens]
            if p.omitido:
                itens.append(
                    f"providência com detalhe omitido: menos de {MINIMO_PARA_DETALHAR} inscrições "
                    "neste Edital"
                )
            linhas.append([f"{p.edital.number}/{p.edital.year}", p.situacao, "; ".join(itens)])
        _tabela(
            composicao,
            ["Edital", "Situação no GPS", "Providências em curso"],
            linhas,
            recuo=0.0,
            alinhamentos=[ESQUERDA, ESQUERDA, ESQUERDA],
        )

    _subtitulo(composicao, "Registros na trilha depois do encerramento")
    if c.posteriores_por_edital:
        _tabela(
            composicao,
            ["Edital", "Encerrado em", "Registros na trilha"],
            [
                [
                    f"{edital.number}/{edital.year}",
                    rc.texto_da_primeira(desfecho),
                    str(n),
                ]
                for edital, desfecho, n in c.posteriores_por_edital
            ],
            recuo=0.0,
            alinhamentos=[ESQUERDA, ESQUERDA, DIREITA],
        )
        _nota(
            composicao,
            f"{rc.NOTA_DA_TRILHA} Registro depois do encerramento não é irregularidade: "
            "suplência e resposta a convocação podem ser exatamente o que o Edital previa.",
        )
    else:
        _paragrafo(composicao, "Nenhum registro na trilha depois do encerramento.")

    _subtitulo(composicao, "O que este relatório não diz")
    for item in NAO_REGISTRADOS:
        _paragrafo(composicao, f"— {item};", antes=ANTES_DE_LINHA)


def _anexo(composicao, c, emissao):
    composicao.escrever(
        "ANEXO TÉCNICO",
        tamanho=CORPO_ATO,
        fonte=NEGRITO,
        antes=ANTES_DE_BLOCO * 3,
        alinhamento=CENTRO,
        junto=True,
    )
    _nota(
        composicao,
        "Para a equipe responsável e as instâncias de controle. Cada Edital tem relatório próprio, "
        "emitido na tela dele, com etapas, listas, cronograma e documentos oficiais.",
    )

    _secao(composicao, "A1. Editais considerados")
    # Uma frase entre o título e a grade: tabela colada ao título, na virada da página, sai com o
    # cabeçalho repetido fora da grade (o paginador leva os dois juntos e repete o cabeçalho).
    n = len(c.relacao)
    _paragrafo(
        composicao,
        f"{n} {'Edital' if n == 1 else 'Editais'}, na ordem da primeira publicação.",
    )
    _tabela(
        composicao,
        ["Edital", "Seleção", "1ª publicação", "Situação no GPS", "Espécie"],
        [
            [
                f"{linha.edital.number}/{linha.edital.year}",
                linha.edital.title,
                rc.texto_da_primeira(linha.primeira),
                linha.situacao,
                linha.especie,
            ]
            for linha in c.relacao
        ],
        recuo=0.0,
        alinhamentos=[ESQUERDA, ESQUERDA, ESQUERDA, ESQUERDA, ESQUERDA],
    )
    for linha in c.relacao:
        endereco = c.enderecos.get(linha.edital.pk)
        if endereco:
            _paragrafo(
                composicao,
                f"{linha.edital.number}/{linha.edital.year}: {endereco}",
                antes=ANTES_DE_LINHA,
            )
    _nota(composicao, "A página pública de cada seleção é a referência dos atos.")

    _secao(composicao, "A2. Critério do conjunto")
    conjunto = c.conjunto
    _par(composicao, "Critério", conjunto.criterio.rotulo + ".")
    if conjunto.criterio.modo == rc.PUBLICACAO:
        _nota(
            composicao,
            "A data é a da primeira publicação do Edital no GPS, e não a das Retificações.",
        )
    elif conjunto.criterio.modo == rc.NUMERO:
        _nota(
            composicao,
            "O ano é o do número do Edital, e não o da publicação nem o de ingresso.",
        )
    if conjunto.retirados:
        _par(
            composicao,
            "Retirados por escolha",
            ", ".join(f"{e.number}/{e.year}" for e in conjunto.retirados),
        )
    elif conjunto.escolha and conjunto.criterio.modo != rc.MANUAL:
        _par(composicao, "Retirados por escolha", "nenhum")
    if conjunto.fora:
        _par(
            composicao,
            "Fora do conjunto",
            "; ".join(f"{e.number}/{e.year}, {motivo}" for e, motivo in conjunto.fora),
        )
    _par(composicao, "Data dos dados", instante_por_extenso(c.referencia))
    _nota(composicao, c.data_dos_dados + " O relatório não reconstitui o passado.")

    _secao(composicao, "A3. Definição de cada número")
    for rotulo, texto in DEFINICOES:
        composicao.escrever(rotulo, tamanho=CORPO_TEXTO, fonte=NEGRITO, antes=ANTES_DE_LINHA)
        composicao.escrever(texto, tamanho=CORPO_TEXTO)

    _secao(composicao, "A4. Limitações")
    for texto in (
        "Fatos não públicos — recursos, convocações, apurações — aparecem no total do conjunto e "
        "por Edital, nunca por perfil ou por lista. O Edital com menos de "
        f"{MINIMO_PARA_DETALHAR} inscrições enviadas não entra neles, porque o relatório dele os "
        "omite; ele continua nas vagas e nas inscrições.",
        "As listas reservadas não se somam entre Editais por modalidade, e a localidade do perfil "
        "é texto do Edital: nenhuma das duas vira agrupamento.",
        "O Edital cancelado conta como Edital, na situação e na relação, e fica fora de todo "
        "número.",
    ):
        _paragrafo(composicao, texto, antes=ANTES_DE_LINHA)

    _secao(composicao, "A5. Sobre esta emissão")
    sigla = getattr(c.unidade, "sigla", "") or "da unidade"
    _paragrafo(
        composicao,
        f"Emissão nº {emissao} do relatório consolidado da unidade {sigla}, com dados até "
        f"{instante_por_extenso(c.referencia)}. Fica registrada na trilha de auditoria do GPS, com "
        "o critério, os Editais incluídos, a data, o autor e o resumo do arquivo. Uma nova emissão "
        "pode trazer números diferentes para os mesmos Editais.",
    )


def composicao(c, *, emissao):
    """A composição inteira, antes de virar arquivo — é o que os testes de conteúdo leem."""
    comp = Composicao(metrica=METRICA_DO_EDITAL)
    _cabecalho(comp, c, emissao)
    _visao_geral(comp, c)
    _numeros(comp, c)
    _atencao(comp, c)
    _oferta_e_procura(comp, c)
    _execucao_e_resultados(comp, c)
    _providencias(comp, c)
    _anexo(comp, c, emissao)
    return comp


def compor(c, *, emissao) -> bytes:
    """Os bytes do documento. Mesmo consolidado e mesma emissão, mesmos bytes (FR-2568)."""
    navegacao = Navegacao(
        titulo=f"{c.titulo} — {c.conjunto.criterio.periodo_curto}",
        autor=getattr(c.unidade, "nome", "") or "",
        marcadores=tuple((1, secao, secao.split(" ", 1)[0] + " ") for secao in SECOES),
        sumario=(),
    )
    return _arquivo_do_edital(
        composicao(c, emissao=emissao),
        identificacao=_identificacao(c, emissao),
        navegacao=navegacao,
    )
