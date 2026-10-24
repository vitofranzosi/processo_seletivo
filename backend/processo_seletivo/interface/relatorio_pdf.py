"""O documento do relatório do Edital: a camada executiva e o anexo técnico (099).

**Nada aqui consulta banco nem decide número.** A composição recebe o `Relatorio` pronto e o
dispõe em blocos, na ordem do contrato (`contracts/relatorio.md`). Quem decide ausência, espécie e
privacidade é a derivação; aqui se decide só como cada coisa aparece.

**O compositor é o da `100`** (`interface/diagramacao.py`), e não mais o escritor do Edital. O
escritor do Edital é um paginador de texto corrido: os seis indicadores saíam numa tabela, e a
procura numa tabela de semanas, porque ele não desenha gráfico (FR-2536, na redação de antes). A
maquete aprovada pedia o painel — cartões, colunas, a série dia a dia —, e o relatório consolidado
já o tinha. Os dois documentos gerenciais passam a ter a mesma identidade: a abertura, os cartões,
a faixa de cada página e o pé são as mesmas peças (FR-2601).

**Mesmos fatos e mesmo instante, mesmos bytes** (FR-2520): a diagramação é determinística, e o
texto continua recusando o caractere sem grafia (`CaractereSemGrafia`) em vez de trocá-lo por "?".
"""

from processo_seletivo.interface.diagramacao import (
    BARRA,
    DESTAQUE,
    DIREITA,
    ESQUERDA,
    LARGURA_UTIL,
    NEGRITO,
    REGULAR,
    TINTA,
    TINTA_3,
    Atencao,
    BarrasVerticais,
    Cartao,
    Cartoes,
    Celula,
    Colunas,
    Definicoes,
    Documento,
    Lista,
    Nota,
    QuebraDePagina,
    Subtitulo,
    Tabela,
    Texto,
    TituloDeSecao,
    Trecho,
    abertura,
)
from processo_seletivo.interface.relatorio_do_edital import (
    ACOMPANHAMENTO,
    ENCERRAMENTO,
    FRASE_DE_PRIVACIDADE,
    FRASE_DO_EDITAL,
    INTERRUPCAO,
    ZONA,
    data_curta,
    dia_e_mes,
    instante_por_extenso,
    interpretar,
    texto_das_vagas,
)
from processo_seletivo.publicacoes.infrastructure.pdf import INSTITUICAO

NATUREZA = (
    "Relatório gerencial com base nos registros do GPS. Não é ato administrativo e não substitui "
    "as publicações oficiais."
)
#: O pé de toda página dos dois documentos gerenciais (099 e 100).
PE = "Relatório gerencial: não é ato administrativo e não substitui as publicações oficiais"
INTEGRIDADE = (
    "O resumo SHA-256 permite conferir que um arquivo tem o mesmo conteúdo do documento registrado "
    "no GPS. Ele não comprova, sozinho, a publicação oficial: a referência é a página pública da "
    "seleção."
)
ENDERECO_LOCAL = (
    "O endereço público da seleção não aparece nesta emissão: ela foi feita num ambiente local, e "
    "o endereço não valeria para quem recebe o arquivo."
)
NAO_REGISTRADOS = (
    "homologação, indeferimento, cancelamento ou desistência de inscrição",
    "presença em prova — a eliminação por ausência aparece como ocorrência registrada",
    "a data em que um evento previsto aconteceu",
    "matrícula efetivada",
)
DEFINICOES = (
    (
        "Vagas imediatas",
        "Quadro de vagas da versão do Edital em vigor no instante dos dados, com as retificações "
        "aplicadas. Unidade: vaga.",
    ),
    (
        "Inscrições enviadas; iniciadas e não enviadas",
        "Inscrições que o candidato enviou, e rascunhos abertos e não enviados. "
        "Unidade: inscrição.",
    ),
    (
        "Cadastros de candidato",
        "Cadastros de acesso distintos entre as inscrições enviadas. A mesma pessoa pode ter mais "
        "de um cadastro, e o CPF é declarado, e não comprovado: o número não é de pessoas.",
    ),
    (
        "Inscrições por vaga",
        "Inscrições enviadas nos perfis com vaga imediata, divididas pelas vagas imediatas desses "
        "perfis. Não se aplica a perfil só de cadastro de reserva.",
    ),
    (
        "Classificação publicada",
        "Inscrições com posição no resultado em vigor. Num perfil, cada inscrição conta uma vez, "
        "mesmo se estiver em mais de uma lista.",
    ),
    (
        "Vagas com inscrição classificada e habilitada",
        "Apuração das vagas em vigor: inscrição dentro do número de vagas e habilitada na "
        "etapa que o Edital exige antes da convocação. Não é matrícula.",
    ),
    (
        "Convocações aceitas",
        "Convocações com o aceite registrado pela comissão. Não é matrícula.",
    ),
    (
        "Registros depois do encerramento",
        "Registros da trilha de auditoria do GPS sobre o Edital e os atos dele, com data "
        "posterior ao encerramento. A contagem cobre os atos que a trilha registra, e não todo "
        "acontecimento.",
    ),
)
#: Como cada natureza de data aparece (FR-2538). "Prazo" só existe para prazo ainda aberto na data
#: dos dados — a derivação não o lista depois de vencido —, e por isso se diz "em curso".
NATUREZAS = {
    "publicação": "Publicação",
    "registrado": "Registrado no GPS",
    "previsto": "Previsto no Edital",
    "prazo": "Prazo em curso",
}
#: O que acompanha o "de N" de cada cartão: "1 de 2 realizadas", e não "1 de 2" solto.
COMPLEMENTOS_DO_DE = {"convocações aceitas": "realizadas"}
#: A barra mais estreita que ainda se lê. Abaixo dela, a série passa de dia para semana.
FATIA_MINIMA = 3.5
#: Acima desta altura, a coluna de alterações não fica ao lado do gráfico: as colunas não se
#: partem, e um Edital com muitas Retificações empurraria o par inteiro para a página seguinte.
ALTURA_MAXIMA_DAS_COLUNAS = 300.0


def _maiuscula(texto):
    return texto[:1].upper() + texto[1:]


def _plural(n, singular, plural):
    return singular if n == 1 else plural


# --- Peças que os dois documentos gerenciais compartilham ---------------------------------------


def cartoes(indicadores, complementos=None):
    """Os indicadores em cartões: o número, o rótulo e a base — a mesma peça no 099 e no 100.

    A ausência é o próprio valor dito: "—" no número, e o motivo na primeira linha da base, para
    que o cartão nunca mostre zero onde não há número (FR-2548).
    """
    complementos = complementos or {}
    lista = []
    for indicador in indicadores:
        numero = indicador.numero
        if numero.existe:
            valor = interpretar(numero)
            de = ""
            if indicador.de is not None:
                complemento = complementos.get(indicador.rotulo, "")
                de = f"de {indicador.de}" + (f" {complemento}" if complemento else "")
            if numero.parcial:
                de = f"{de} · parcial" if de else "parcial"
            base = indicador.base
        else:
            valor, de = "—", ""
            motivo = interpretar(numero)
            base = motivo if indicador.base == motivo else f"{motivo}. {indicador.base}"
        lista.append(
            Cartao(valor=valor, rotulo=_maiuscula(indicador.rotulo), base=_maiuscula(base), de=de)
        )
    return Cartoes(lista)


# --- A primeira página: o painel ----------------------------------------------------------------


def _panorama(r, emissao):
    edital = r.edital
    blocos = [
        *abertura(
            orgao=(INSTITUICAO[0], INSTITUICAO[1], " ".join(r.unidade.get("cabecalho") or ())),
            titulo=r.titulo,
            subtitulo=f"{r.especie_por_extenso} — {r.especie_explicada}",
            natureza=NATUREZA,
            pares=[
                ("Seleção", f"{edital.title} — {edital.processo.title}", "", False),
                (
                    "Dados até",
                    instante_por_extenso(r.referencia),
                    f"emissão nº {emissao}; uma nova emissão pode trazer números diferentes",
                    False,
                ),
                ("Situação no GPS", r.situacao_no_gps, "", False),
                ("Situação das providências", r.providencias, "", bool(r.pendencias)),
            ],
            marcador="Relatório do Edital",
        ),
        TituloDeSecao("Visão geral", antes=12.0),
        Texto(" ".join(r.frases), tamanho=9.8, entrelinha=1.45, antes=5.0),
        TituloDeSecao("Principais números", antes=10.0),
        cartoes(r.indicadores, COMPLEMENTOS_DO_DE),
    ]
    if r.pontos_de_atencao:
        blocos.append(Atencao("Pontos de atenção", list(r.pontos_de_atencao)))
    return blocos


# --- Resultados por perfil ----------------------------------------------------------------------


def _perfis(r):
    linhas = []
    for perfil in r.perfis:
        nome = [(perfil.nome, None, NEGRITO, TINTA, None)]
        if perfil.local:
            nome.append((perfil.local, 7.4, REGULAR, TINTA_3, None))
        linhas.append(
            [
                Celula(nome),
                texto_das_vagas(perfil),
                interpretar(perfil.inscricoes),
                interpretar(perfil.por_vaga),
                interpretar(perfil.classificadas),
                perfil.situacao_das_vagas,
            ]
        )
    return [
        QuebraDePagina(),
        TituloDeSecao("Resultados por perfil de vaga", antes=0.0),
        Tabela(
            [
                "Perfil de vaga",
                "Vagas imediatas",
                "Inscrições",
                "Por vaga",
                "Classificação publicada",
                "Situação das vagas",
            ],
            linhas,
            larguras=[1.9, 1.45, 0.95, 0.95, 1.2, 2.75],
            alinhamentos=[ESQUERDA, ESQUERDA, DIREITA, DIREITA, DIREITA, ESQUERDA],
            tamanho=8.2,
        ),
        Nota(
            "Os totais contam inscrições: quem se inscreve em mais de um perfil conta uma vez em "
            "cada um."
        ),
    ]


# --- Procura, alterações e recursos -------------------------------------------------------------


def _dia(dia):
    return dia.strftime("%d/%m")


def _grupos(pontos, dias, original):
    """Os pontos somados de `dias` em `dias`, com o término original sempre entre dois grupos.

    Contados a partir do primeiro dia, uma semana podia ter dias antes e depois do término
    original, e a cor da barra mentiria sobre metade dela. Por isso os grupos de antes se contam
    do término para trás, e os de depois, do dia seguinte para a frente: o primeiro e o último
    podem ter menos dias. Devolve os grupos e o índice do último antes do término, quando houver.
    """
    antes = [p for p in pontos if original and p.dia <= original]
    depois = pontos[len(antes) :]
    grupos = [antes[max(0, fim - dias) : fim] for fim in range(len(antes), 0, -dias)][::-1]
    marca = len(grupos) - 1 if grupos and depois else None
    grupos += [depois[i : i + dias] for i in range(0, len(depois), dias)]
    return grupos, marca


def _serie(r, largura):
    """A série de envios: dia a dia quando cabe, semana a semana quando os dias não cabem.

    Dia a dia é o que a maquete pede, e o que o GPS registra. Com o período longo, a barra de um dia
    ficaria mais estreita que `FATIA_MINIMA`; aí cada barra soma até sete dias, e a nota diz qual
    das duas é. O número de cada barra está no texto alternativo, que é o que o leitor de tela lê.
    """
    pontos = list(r.serie)
    if not pontos:
        return [Texto("O período de inscrições não tem início declarado no Edital.", tamanho=8.8)]
    total = sum(p.quantidade for p in pontos)
    if not total:
        return [Texto("Nenhuma inscrição enviada no período.", tamanho=8.8)]
    original = r.termino_original.astimezone(ZONA).date() if r.termino_original else None
    diaria = len(pontos) * FATIA_MINIMA <= largura
    grupos, indice = _grupos(pontos, 1 if diaria else 7, original)
    itens = [(_dia(g[0].dia), sum(p.quantidade for p in g)) for g in grupos]
    marca, legenda = None, []
    if indice is not None:
        marca = (indice, f"término original ({original.strftime('%d/%m')})")
        antes = sum(n for _, n in itens[: indice + 1])
        legenda = [
            (f"até o término original: {antes}", BARRA),
            (f"no período acrescentado: {total - antes}", DESTAQUE),
        ]
    if diaria:
        descricao, valores = "por dia de envio", "; ".join(f"{d}, {n}" for d, n in itens)
        nota = "Cada barra é um dia"
    else:
        descricao = "por semana de envio"
        valores = "; ".join(f"semana de {d}, {n}" for d, n in itens)
        nota = "Cada barra soma até sete dias" + (
            ", contados a partir do término original, para que ele caia entre duas barras"
            if marca
            else ", a contar do primeiro dia do período"
        )
    alt = (
        f"Inscrições enviadas {descricao}, de {_dia(pontos[0].dia)} a {_dia(pontos[-1].dia)}: "
        f"{valores}."
        + (f" O término original do prazo era {original.strftime('%d/%m')}." if marca else "")
    )
    nota += "; o número escrito é o do maior. O GPS registra o instante de cada envio."
    if r.termino_original:
        nota += (
            f" O Edital previa o fim das inscrições em {dia_e_mes(r.termino_original)}; "
            f"{r.no_periodo_acrescentado} inscrições chegaram depois disso, no período "
            "acrescentado pela prorrogação."
        )
    return [BarrasVerticais(itens, alt=alt, marca=marca, legenda=legenda), Nota(nota)]


def _alteracoes(r):
    blocos = [Subtitulo("Alterações e recursos", antes=0.0)]
    if not r.retificacoes:
        blocos.append(Texto("Nenhuma Retificação publicada.", tamanho=8.8))
    for retificacao in r.retificacoes:
        blocos.append(
            Texto(
                f"Retificação nº {retificacao.numero} — {data_curta(retificacao.publicada_em)}",
                tamanho=8.8,
                fonte=NEGRITO,
                antes=6.0,
                junto=True,
            )
        )
        descritas = [
            f"{a.get('campo', '')} — {a.get('onde', '')}: de {a.get('antes', '—')} para "
            f"{a.get('depois', '—')}"
            for a in retificacao.alteracoes
            if a.get("antes") is not None
        ]
        if descritas:
            blocos.append(Lista(descritas, tamanho=8.4))
        else:
            blocos.append(Texto("Alteração não descrita automaticamente.", tamanho=8.6, antes=2.0))
        blocos.append(Nota(f"Justificativa registrada: “{retificacao.justificativa}”"))
    blocos.append(Texto("Recursos", tamanho=8.8, fonte=NEGRITO, antes=8.0, junto=True))
    blocos.append(Texto(_frase_dos_recursos(r), tamanho=8.6, antes=2.0))
    return blocos


def _frase_dos_recursos(r):
    rec = r.recursos
    if r.total_omitido:
        return _maiuscula(FRASE_DO_EDITAL) + "."
    if not rec.apresentados:
        return "Nenhum recurso apresentado."
    partes = [
        f"{n} {singular if n == 1 else plural}"
        for n, singular, plural in (
            (rec.indeferidos, "indeferido", "indeferidos"),
            (rec.deferidos, "deferido", "deferidos"),
            (
                rec.nao_admitidos,
                "não admitido, sem análise do pedido",
                "não admitidos, sem análise do pedido",
            ),
            (rec.aguardando, "aguardando decisão", "aguardando decisão"),
        )
        if n
    ]
    apresentados = _plural(rec.apresentados, "recurso apresentado", "recursos apresentados")
    return f"{rec.apresentados} {apresentados}: " + "; ".join(partes) + "."


def _procura_e_alteracoes(r):
    """Lado a lado, como na maquete — salvo quando as alterações não cabem ao lado do gráfico."""
    titulo = Subtitulo("Procura ao longo do período", antes=0.0)
    meia = (LARGURA_UTIL - Colunas.espaco) / 2
    alteracoes = _alteracoes(r)
    altura = sum((b.antes if i else 0.0) + b.medir(meia) for i, b in enumerate(alteracoes))
    if r.serie and altura <= ALTURA_MAXIMA_DAS_COLUNAS:
        return [Colunas([titulo, *_serie(r, meia)], alteracoes, antes=14.0)]
    titulo.antes = 14.0
    alteracoes[0].antes = 14.0
    return [titulo, *_serie(r, LARGURA_UTIL), *alteracoes]


# --- Datas e documentos -------------------------------------------------------------------------


def _datas(r):
    linhas = []
    for data in r.datas:
        quando = data_curta(data.dia)
        if data.ate and data.ate.astimezone(ZONA).date() != data.dia.astimezone(ZONA).date():
            quando = f"{dia_e_mes(data.dia)} a {data_curta(data.ate)}"
        natureza = NATUREZAS.get(data.natureza, _maiuscula(data.natureza))
        linhas.append([quando, data.texto, Celula([(natureza, 7.6, NEGRITO, TINTA_3, None)])])
    return [
        TituloDeSecao("Datas principais", antes=14.0),
        Tabela(["Data", "O que", "Natureza"], linhas, larguras=[1.45, 4.3, 1.35], tamanho=8.2),
        Nota(
            "Publicação: ato publicado. Registrado no GPS: ato gravado no GPS. Previsto no Edital: "
            "data que o Edital declara — o GPS não registra se o evento aconteceu nela. Prazo em "
            "curso: prazo ainda aberto na data dos dados."
        ),
    ]


def _documentos(r):
    """A página pública e os resultados em vigor, numa tabela só, com os links (FR-2539).

    Sem endereço público — emissão feita num ambiente local —, a tabela fica sem os endereços e a
    nota diz por quê, em vez de imprimir um endereço que não abre para quem recebe (FR-2603).
    """
    publico = bool(r.endereco_da_selecao)
    edital = next((d for d in r.documentos if not d.resultado_vigente), None)
    pagina = [
        (
            "Página pública da seleção: o Edital, as retificações e os resultados",
            None,
            NEGRITO,
            TINTA,
            None,
        )
    ]
    if publico:
        pagina.append((r.endereco_da_selecao, 7.2, REGULAR, DESTAQUE, r.endereco_da_selecao))
    linhas = [[Celula(pagina), f"desde {data_curta(edital.publicado_em)}" if edital else ""]]
    for documento in (d for d in r.documentos if d.resultado_vigente):
        # O endereço de cada resultado é longo e não se lê no papel: o título é o link, e quem lê
        # impresso chega pela página da seleção, cujo endereço está escrito na linha de cima.
        link = documento.endereco if publico and documento.endereco else None
        linhas.append(
            [
                Celula([(documento.titulo, None, REGULAR, DESTAQUE if link else TINTA, link)]),
                data_curta(documento.publicado_em),
            ]
        )
    nota = (
        "Os nomes dos classificados estão nos resultados publicados, e não neste relatório. O "
        "resumo de cada arquivo, para conferência, está no anexo."
    )
    return [
        TituloDeSecao("Documentos oficiais", antes=14.0),
        Tabela(["Documento oficial", "Publicado em"], linhas, larguras=[5.4, 1.1], tamanho=8.4),
        Nota(nota if publico else f"{ENDERECO_LOCAL} {nota}"),
    ]


# --- O anexo técnico ----------------------------------------------------------------------------


def _omissao(perfil):
    return _maiuscula(perfil.motivo_da_omissao or FRASE_DE_PRIVACIDADE) + "."


def _etapas(r):
    blocos = [TituloDeSecao("A. Etapas de avaliação", antes=12.0)]
    for perfil in r.perfis:
        blocos.append(Subtitulo(perfil.nome, antes=8.0))
        if perfil.omitido:
            blocos.append(Texto(_omissao(perfil), tamanho=8.6, antes=2.0))
            continue
        linhas = []
        for etapa in perfil.etapas:
            nome = Celula(
                [
                    (etapa.nome, None, NEGRITO, TINTA, None),
                    (etapa.regra, 7.4, REGULAR, TINTA_3, None),
                ]
            )
            if not etapa.registrada:
                linhas.append([nome, "ainda não disponível", "", "", ""])
                continue
            linhas.append(
                [
                    nome,
                    str(etapa.avaliadas),
                    str(etapa.habilitadas),
                    str(etapa.eliminadas) if etapa.elimina else "não elimina",
                    str(etapa.por_ocorrencia),
                ]
            )
        if linhas:
            blocos.append(
                Tabela(
                    [
                        "Etapa e regra do Edital",
                        "Avaliadas",
                        "Habilitadas",
                        "Eliminadas",
                        "Por ocorrência",
                    ],
                    linhas,
                    larguras=[3.4, 1.0, 1.0, 1.0, 1.1],
                    alinhamentos=[ESQUERDA, DIREITA, DIREITA, DIREITA, DIREITA],
                )
            )
        else:
            blocos.append(Texto("Nenhuma etapa de avaliação declarada.", tamanho=8.6, antes=2.0))
    blocos.append(
        Nota(
            "Avaliadas: inscrições com avaliação registrada na etapa. Por ocorrência: eliminação "
            "registrada pela comissão sem avaliação, com motivo escrito. O GPS não registra "
            "presença."
        )
    )
    return blocos


def _listas(r):
    blocos = [TituloDeSecao("B. Classificação e vagas por lista", antes=14.0)]
    linhas = [
        [
            perfil.nome,
            lista.marco,
            lista.lista,
            interpretar(lista.classificadas),
            interpretar(lista.vagas),
            lista.natureza,
        ]
        for perfil in r.perfis
        for lista in perfil.listas
    ]
    if not linhas:
        blocos.append(Texto("Nenhum resultado publicado.", tamanho=8.8))
        return blocos
    blocos.append(
        Tabela(
            ["Perfil", "Resultado", "Lista", "Classificação publicada", "Vagas", "Natureza"],
            linhas,
            larguras=[1.6, 1.4, 1.8, 1.15, 0.75, 1.1],
            alinhamentos=[ESQUERDA, ESQUERDA, ESQUERDA, DIREITA, DIREITA, ESQUERDA],
        )
    )
    blocos.append(
        Nota(
            "Quem concorre a vaga reservada aparece também na lista de ampla concorrência: as "
            "listas não se somam."
        )
    )
    return blocos


def _recursos_e_convocacoes(r):
    linhas = []
    for perfil in r.perfis:
        if perfil.omitido:
            nome = Celula(
                [
                    (perfil.nome, None, REGULAR, TINTA, None),
                    (_omissao(perfil), 7.2, REGULAR, TINTA_3, None),
                ]
            )
            linhas.append([nome, "—", "—", "—", "—", "—", "—"])
            continue
        rec, conv = perfil.recursos, perfil.convocacoes
        linhas.append(
            [
                perfil.nome,
                str(rec.apresentados if rec else 0),
                str(rec.nao_admitidos if rec else 0),
                str(rec.indeferidos if rec else 0),
                str(rec.deferidos if rec else 0),
                str(conv.realizadas if conv else 0),
                str(conv.aceitas if conv else 0),
            ]
        )
    return [
        TituloDeSecao("C. Recursos e convocações por perfil", antes=14.0),
        Tabela(
            [
                "Perfil",
                "Recursos",
                "Não admitidos",
                "Indeferidos",
                "Deferidos",
                "Convocações",
                "Aceitas",
            ],
            linhas,
            larguras=[2.2, 1.0, 1.05, 1.05, 0.95, 1.2, 0.85],
            alinhamentos=[ESQUERDA, *[DIREITA] * 6],
        ),
        Nota(
            "Deferido agrupa os três desfechos favoráveis que o candidato lê no GPS: resultado "
            "corrigido, etapa reavaliada e ato corretivo pela instituição. O traço é número "
            "omitido, e não zero."
        ),
    ]


def _cronograma(r):
    return [
        TituloDeSecao("D. Cronograma: previsto, retificado e registrado", antes=14.0),
        Tabela(
            ["Evento", "Previsto no Edital", "Após retificação", "Registrado no GPS"],
            [[c.evento, c.previsto, c.retificado, c.registrado] for c in r.cronograma],
            larguras=[1.6, 1.3, 1.3, 1.9],
        ),
    ]


def _resumo(sha256):
    """O resumo em duas metades: 64 caracteres sem espaço não se quebram sozinhos."""
    if not sha256:
        return "—"
    meio = len(sha256) // 2
    return Celula(
        [(sha256[:meio], 7.0, REGULAR, TINTA, None), (sha256[meio:], 7.0, REGULAR, TINTA, None)]
    )


def _verificacao(r):
    return [
        TituloDeSecao("E. Documentos e verificação", antes=14.0),
        Tabela(
            ["Documento", "Publicado em", "SHA-256 do arquivo"],
            [[d.titulo, data_curta(d.publicado_em), _resumo(d.sha256)] for d in r.documentos],
            larguras=[3.8, 1.1, 1.9],
            tamanho=8.2,
        ),
        Nota(INTEGRIDADE),
    ]


def _sobre_a_emissao(r, emissao):
    especie = {
        ENCERRAMENTO: "de encerramento porque o Edital está encerrado e não há providência "
        "pendente registrada no GPS",
        INTERRUPCAO: "de interrupção porque o Edital foi cancelado",
        ACOMPANHAMENTO: "de acompanhamento porque o Edital não está encerrado ou ainda há "
        "providência pendente",
    }[r.especie]
    return Texto(
        [
            Trecho(f"Emissão nº {emissao}", NEGRITO),
            Trecho(
                f" deste Edital, com dados até {instante_por_extenso(r.referencia)}. Uma nova "
                "emissão pode mostrar números diferentes se houver novos registros. Cada emissão "
                "fica registrada na auditoria do GPS, com data, autor e o resumo do arquivo. Este "
                f"relatório é {especie}. Encerrado e sem pendência, o relatório se chama de "
                "encerramento; com o Edital cancelado, de interrupção; nos demais casos, de "
                "acompanhamento."
            ),
        ],
        tamanho=8.8,
    )


def _definicoes(r):
    """As definições, com a contagem de cadastros dita junto da definição que a explica."""
    pares = []
    for termo, definicao in DEFINICOES:
        if termo == "Cadastros de candidato":
            definicao += (
                f" Neste Edital: {r.cadastros_distintos} cadastros distintos com inscrição enviada."
            )
        pares.append((termo, definicao))
    return pares


def _anexo(r, emissao):
    return [
        QuebraDePagina(),
        TituloDeSecao("Anexo técnico", antes=0.0, tamanho=13.0, tipo="H1"),
        Nota(
            "Para a equipe responsável e as instâncias de controle. As regras são as publicadas no "
            "Edital em vigor no instante dos dados.",
            antes=4.0,
        ),
        *_etapas(r),
        *_listas(r),
        *_recursos_e_convocacoes(r),
        *_cronograma(r),
        *_verificacao(r),
        TituloDeSecao("F. Como cada número foi obtido", antes=14.0),
        Definicoes(_definicoes(r)),
        TituloDeSecao("G. O que o GPS não registra", antes=14.0),
        Texto(
            "Estes fatos podem ter acontecido, mas o GPS não os controla, e por isso não há "
            "números para eles: " + "; ".join(NAO_REGISTRADOS) + ".",
            tamanho=8.8,
        ),
        TituloDeSecao("H. Sobre esta emissão", antes=14.0),
        _sobre_a_emissao(r, emissao),
    ]


def documento(relatorio, *, emissao):
    """O documento inteiro, em blocos — é o que os testes de diagramação leem."""
    r = relatorio
    especie = {
        ACOMPANHAMENTO: "acompanhamento",
        ENCERRAMENTO: "encerramento",
        INTERRUPCAO: "interrupção",
    }[r.especie]
    return Documento(
        blocos=[
            *_panorama(r, emissao),
            *_perfis(r),
            *_procura_e_alteracoes(r),
            *_datas(r),
            *_documentos(r),
            *_anexo(r, emissao),
        ],
        faixa_esquerda=f"{r.titulo} · relatório de {especie}",
        faixa_direita=f"dados até {instante_por_extenso(r.referencia)} · emissão nº {emissao}",
        pe=PE,
        titulo=r.titulo,
        autor=r.unidade.get("nome") or "",
    )


def compor(relatorio, *, emissao) -> bytes:
    """Os bytes do documento. Mesmo relatório e mesma emissão, mesmos bytes (FR-2520)."""
    return documento(relatorio, emissao=emissao).compor()
