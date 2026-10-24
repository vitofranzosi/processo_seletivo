"""O documento do relatório do Edital: a camada executiva e o anexo técnico (099).

**Nada aqui consulta banco nem decide número.** A composição recebe o `Relatorio` pronto e o
escreve, na ordem do contrato (`contracts/relatorio.md`). Quem decide ausência, espécie e
privacidade é a derivação; aqui se decide só como cada coisa aparece.

**O escritor é o do Edital, e não o do comprovante** (R-004). O do comprovante não faz link, e o do
Edital transforma em link todo endereço `https://` escrito inteiro e grava os marcadores das seções;
embute a fonte, de modo que o texto institucional sai com os acentos; e é determinístico, sem data
de criação nem identificador, o que dá a FR-2520 sem esforço: mesmos fatos e mesmo instante, mesmos
bytes. O `estrito` dele recusa caractere sem grafia em vez de trocá-lo por "?" — a emissão falha
alto, como a do Edital (achado de 08/10).
"""

from processo_seletivo.interface.relatorio_do_edital import (
    ENCERRAMENTO,
    FRASE_DE_PRIVACIDADE,
    FRASE_DO_EDITAL,
    INTERRUPCAO,
    data_curta,
    dia_e_mes,
    instante_por_extenso,
    interpretar,
    semanas,
    texto_das_vagas,
    texto_do_indicador,
)
from processo_seletivo.publicacoes.infrastructure.pdf import (
    ALTURA_DO_BRASAO,
    ANTES_DE_BLOCO,
    ANTES_DE_LINHA,
    ANTES_DE_PARAGRAFO,
    CENTRO,
    CORPO_ATO,
    CORPO_NOTA,
    CORPO_SUBSECAO,
    CORPO_TEXTO,
    CORPO_TITULO_DE_SECAO,
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
    "as publicações oficiais."
)
INTEGRIDADE = (
    "O resumo SHA-256 permite conferir que um arquivo tem o mesmo conteúdo do documento registrado "
    "no GPS. Ele não comprova, sozinho, a publicação oficial: a referência é a página pública da "
    "seleção."
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


def _secao(composicao, texto):
    composicao.escrever(
        texto,
        tamanho=CORPO_TITULO_DE_SECAO,
        fonte=NEGRITO,
        antes=ANTES_DE_BLOCO * 2,
        junto=True,
    )


def _subtitulo(composicao, texto):
    composicao.escrever(
        texto, tamanho=CORPO_SUBSECAO, fonte=NEGRITO, antes=ANTES_DE_BLOCO, junto=True
    )


def _paragrafo(composicao, texto, *, antes=ANTES_DE_PARAGRAFO):
    composicao.escrever(texto, tamanho=CORPO_TEXTO, antes=antes, justificar=True)


def _nota(composicao, texto):
    composicao.escrever(texto, tamanho=CORPO_NOTA, antes=ANTES_DE_LINHA)


def _par(composicao, rotulo, valor):
    composicao.escrever(rotulo, tamanho=CORPO_NOTA, antes=ANTES_DE_LINHA, junto=True)
    composicao.escrever(valor, tamanho=CORPO_TEXTO, fonte=NEGRITO)


def _identificacao(relatorio):
    edital = relatorio.edital
    return (
        f"Relatório do Edital {edital.number}/{edital.year} · dados até "
        f"{instante_por_extenso(relatorio.referencia)} · relatório gerencial"
    )


def _cabecalho(composicao, relatorio, emissao):
    unidade = UnidadeDoAto(cabecalho=tuple(relatorio.unidade["cabecalho"]), local="")
    composicao.espaco(ALTURA_DO_BRASAO - 10)
    for indice, linha in enumerate(linhas_do_orgao(unidade)):
        composicao.escrever(
            linha, tamanho=CORPO_TEXTO, alinhamento=CENTRO, antes=0.0 if indice else 4.0
        )
    composicao.escrever(
        relatorio.titulo.upper(), tamanho=CORPO_ATO, fonte=NEGRITO, antes=16, alinhamento=CENTRO
    )
    composicao.escrever(
        f"{relatorio.especie_por_extenso} — {relatorio.especie_explicada}",
        tamanho=CORPO_TEXTO,
        fonte=NEGRITO,
        antes=ANTES_DE_LINHA,
        alinhamento=CENTRO,
    )
    composicao.escrever(NATUREZA, tamanho=CORPO_NOTA, antes=ANTES_DE_LINHA, alinhamento=CENTRO)
    edital = relatorio.edital
    _par(composicao, "Seleção", f"{edital.title} — {edital.processo.title}")
    _par(composicao, "Situação no GPS", relatorio.situacao_no_gps)
    _par(composicao, "Situação das providências", relatorio.providencias)
    _par(
        composicao,
        "Dados até",
        f"{instante_por_extenso(relatorio.referencia)} — emissão nº {emissao}",
    )


def _visao_geral(composicao, relatorio):
    _secao(composicao, "1. Visão geral")
    _paragrafo(composicao, " ".join(relatorio.frases))


def _numeros(composicao, relatorio):
    _secao(composicao, "2. Principais números")
    linhas = []
    for indicador in relatorio.indicadores:
        rotulo = indicador.rotulo[:1].upper() + indicador.rotulo[1:]
        linhas.append([rotulo, texto_do_indicador(indicador), indicador.base])
    _tabela(
        composicao,
        ["Indicador", "Valor", "O que o número diz"],
        linhas,
        recuo=0.0,
        alinhamentos=[ESQUERDA, DIREITA, ESQUERDA],
    )


def _atencao(composicao, relatorio):
    if not relatorio.pontos_de_atencao:
        return
    _secao(composicao, "3. Pontos de atenção")
    for indice, (titulo, texto) in enumerate(relatorio.pontos_de_atencao, 1):
        composicao.escrever(
            f"{indice}. {titulo}", tamanho=CORPO_TEXTO, fonte=NEGRITO, antes=ANTES_DE_PARAGRAFO
        )
        composicao.escrever(texto, tamanho=CORPO_TEXTO, recuo=12.0, justificar=True)


def _perfis(composicao, relatorio):
    _secao(composicao, "4. Resultados por perfil de vaga")
    linhas = []
    for perfil in relatorio.perfis:
        vagas = texto_das_vagas(perfil)
        nome = perfil.nome + (f" — {perfil.local}" if perfil.local else "")
        linhas.append(
            [
                nome,
                vagas,
                interpretar(perfil.inscricoes),
                interpretar(perfil.por_vaga),
                interpretar(perfil.classificadas),
                perfil.situacao_das_vagas,
            ]
        )
    _tabela(
        composicao,
        [
            "Perfil de vaga",
            "Vagas imediatas",
            "Inscrições",
            "Por vaga",
            "Classificação publicada",
            "Situação das vagas",
        ],
        linhas,
        recuo=0.0,
        alinhamentos=[ESQUERDA, ESQUERDA, DIREITA, DIREITA, DIREITA, ESQUERDA],
    )
    _nota(
        composicao,
        "Os totais contam inscrições: quem se inscreve em mais de um perfil conta uma vez em "
        "cada um.",
    )


def _procura(composicao, relatorio):
    blocos = semanas(relatorio)
    if not blocos:
        return
    _secao(composicao, "5. Procura")
    linhas = []
    for semana in blocos:
        marca = ""
        if semana.termino_original:
            marca = "término previsto no Edital"
        elif semana.acrescentada:
            marca = "período acrescentado"
        linhas.append(
            [f"{dia_e_mes_d(semana.inicio)} a {dia_e_mes_d(semana.fim)}", str(semana.envios), marca]
        )
    _tabela(
        composicao,
        ["Semana", "Inscrições enviadas", ""],
        linhas,
        recuo=0.0,
        alinhamentos=[ESQUERDA, DIREITA, ESQUERDA],
    )
    if relatorio.termino_original:
        _nota(
            composicao,
            f"O Edital previa o fim das inscrições em {dia_e_mes(relatorio.termino_original)}; "
            f"{relatorio.no_periodo_acrescentado} inscrições chegaram depois disso, no período "
            "acrescentado pela prorrogação.",
        )


def dia_e_mes_d(dia):
    return dia.strftime("%d/%m")


def _alteracoes_e_recursos(composicao, relatorio):
    _secao(composicao, "6. Alterações e recursos")
    if not relatorio.retificacoes:
        _paragrafo(composicao, "Nenhuma Retificação publicada.")
    for retificacao in relatorio.retificacoes:
        _subtitulo(
            composicao,
            f"Retificação nº {retificacao.numero} — {data_curta(retificacao.publicada_em)}",
        )
        descritas = [
            f"{a.get('campo', '')} — {a.get('onde', '')}: de {a.get('antes', '—')} para "
            f"{a.get('depois', '—')}"
            for a in retificacao.alteracoes
            if a.get("antes") is not None
        ]
        if descritas:
            for descrita in descritas:
                _paragrafo(composicao, descrita, antes=ANTES_DE_LINHA)
        else:
            _paragrafo(composicao, "Alteração não descrita automaticamente.", antes=ANTES_DE_LINHA)
        _nota(composicao, f"Justificativa registrada: “{retificacao.justificativa}”")
    rec = relatorio.recursos
    _subtitulo(composicao, "Recursos")
    if relatorio.total_omitido:
        _paragrafo(composicao, FRASE_DO_EDITAL[:1].upper() + FRASE_DO_EDITAL[1:] + ".")
    elif rec.apresentados:
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
        apresentados = "recurso apresentado" if rec.apresentados == 1 else "recursos apresentados"
        _paragrafo(composicao, f"{rec.apresentados} {apresentados}: " + "; ".join(partes) + ".")
    else:
        _paragrafo(composicao, "Nenhum recurso apresentado.")


def _datas(composicao, relatorio):
    _secao(composicao, "7. Datas principais")
    linhas = []
    for data in relatorio.datas:
        quando = data_curta(data.dia)
        if data.ate and data.ate.date() != data.dia.date():
            quando = f"{dia_e_mes(data.dia)} a {data_curta(data.ate)}"
        linhas.append([quando, data.texto, data.natureza])
    _tabela(composicao, ["Data", "O que", "Natureza"], linhas, recuo=0.0)
    _nota(
        composicao,
        "Publicação: ato publicado. Registrado: ato gravado no GPS. Previsto e prazo: datas que o "
        "Edital ou a convocação declaram. O GPS não registra se um evento previsto aconteceu.",
    )


def _documentos(composicao, relatorio):
    _secao(composicao, "8. Documentos oficiais")
    _paragrafo(
        composicao,
        "O Edital, as retificações e os resultados estão na página pública da seleção: "
        f"{relatorio.endereco_da_selecao}",
    )
    vigentes = [d for d in relatorio.documentos if d.resultado_vigente]
    for documento in vigentes:
        _paragrafo(composicao, f"{documento.titulo}: {documento.endereco}", antes=ANTES_DE_LINHA)
    _nota(
        composicao,
        "Os nomes dos classificados estão nos resultados publicados, e não neste relatório.",
    )


def _anexo(composicao, relatorio, emissao):
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
        "Para a equipe responsável e as instâncias de controle. As regras são as publicadas no "
        "Edital em vigor no instante dos dados.",
    )

    _secao(composicao, "A. Etapas de avaliação")
    for perfil in relatorio.perfis:
        _subtitulo(composicao, perfil.nome)
        if perfil.omitido:
            frase = perfil.motivo_da_omissao or FRASE_DE_PRIVACIDADE
            _paragrafo(composicao, frase[:1].upper() + frase[1:] + ".")
            continue
        linhas = []
        for etapa in perfil.etapas:
            if not etapa.registrada:
                linhas.append([etapa.nome, etapa.regra, "ainda não disponível", "", "", ""])
                continue
            linhas.append(
                [
                    etapa.nome,
                    etapa.regra,
                    str(etapa.avaliadas),
                    str(etapa.habilitadas),
                    str(etapa.eliminadas) if etapa.elimina else "não elimina",
                    str(etapa.por_ocorrencia),
                ]
            )
        _tabela(
            composicao,
            [
                "Etapa",
                "Regra do Edital",
                "Avaliadas",
                "Habilitadas",
                "Eliminadas",
                "Por ocorrência",
            ],
            linhas,
            recuo=0.0,
            alinhamentos=[ESQUERDA, ESQUERDA, DIREITA, DIREITA, DIREITA, DIREITA],
        )
    _nota(
        composicao,
        "Avaliadas: inscrições com avaliação registrada na etapa. Por ocorrência: eliminação "
        "registrada pela comissão sem avaliação, com motivo escrito. O GPS não registra presença.",
    )

    _secao(composicao, "B. Classificação e vagas por lista")
    linhas = [
        [
            perfil.nome,
            lista.marco,
            lista.lista,
            interpretar(lista.classificadas),
            interpretar(lista.vagas),
            lista.natureza,
        ]
        for perfil in relatorio.perfis
        for lista in perfil.listas
    ]
    if linhas:
        _tabela(
            composicao,
            ["Perfil", "Resultado", "Lista", "Classificação publicada", "Vagas", "Natureza"],
            linhas,
            recuo=0.0,
            alinhamentos=[ESQUERDA, ESQUERDA, ESQUERDA, DIREITA, DIREITA, ESQUERDA],
        )
        _nota(
            composicao,
            "Quem concorre a vaga reservada aparece também na lista de ampla concorrência: as "
            "listas não se somam.",
        )
    else:
        _paragrafo(composicao, "Nenhum resultado publicado.")

    _secao(composicao, "C. Recursos e convocações por perfil")
    linhas = []
    for perfil in relatorio.perfis:
        if perfil.omitido:
            linhas.append(
                [perfil.nome, perfil.motivo_da_omissao or FRASE_DE_PRIVACIDADE, "", "", "", "", ""]
            )
            continue
        r = perfil.recursos
        c = perfil.convocacoes
        linhas.append(
            [
                perfil.nome,
                str(r.apresentados if r else 0),
                str(r.nao_admitidos if r else 0),
                str(r.indeferidos if r else 0),
                str(r.deferidos if r else 0),
                str(c.realizadas if c else 0),
                str(c.aceitas if c else 0),
            ]
        )
    _tabela(
        composicao,
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
        recuo=0.0,
        alinhamentos=[ESQUERDA, *[DIREITA] * 6],
    )
    _nota(
        composicao,
        "Deferido agrupa os três desfechos favoráveis que o candidato lê no GPS: resultado "
        "corrigido, etapa reavaliada e ato corretivo pela instituição.",
    )

    _secao(composicao, "D. Cronograma: previsto, retificado e registrado")
    _tabela(
        composicao,
        ["Evento", "Previsto no Edital", "Após retificação", "Registrado no GPS"],
        [[c.evento, c.previsto, c.retificado, c.registrado] for c in relatorio.cronograma],
        recuo=0.0,
    )

    _secao(composicao, "E. Documentos e verificação")
    _tabela(
        composicao,
        ["Documento", "Publicado em", "SHA-256 do arquivo"],
        [[d.titulo, data_curta(d.publicado_em), d.sha256] for d in relatorio.documentos],
        recuo=0.0,
    )
    _nota(composicao, INTEGRIDADE)

    _secao(composicao, "F. Como cada número foi obtido")
    for rotulo, texto in DEFINICOES:
        composicao.escrever(rotulo, tamanho=CORPO_TEXTO, fonte=NEGRITO, antes=ANTES_DE_LINHA)
        composicao.escrever(texto, tamanho=CORPO_TEXTO)
    _paragrafo(
        composicao,
        f"Cadastros de candidato distintos com inscrição enviada: {relatorio.cadastros_distintos}.",
    )

    _secao(composicao, "G. O que o GPS não registra")
    _paragrafo(
        composicao,
        "Estes fatos podem ter acontecido, mas o GPS não os controla, e por isso não há números "
        "para eles: " + "; ".join(NAO_REGISTRADOS) + ".",
    )

    _secao(composicao, "H. Sobre esta emissão")
    especie = (
        "de encerramento porque o Edital está encerrado e não há providência pendente registrada "
        "no GPS"
        if relatorio.especie == ENCERRAMENTO
        else "de interrupção porque o Edital foi cancelado"
        if relatorio.especie == INTERRUPCAO
        else "de acompanhamento porque o Edital não está encerrado ou ainda há providência pendente"
    )
    _paragrafo(
        composicao,
        f"Emissão nº {emissao} deste Edital, com dados até "
        f"{instante_por_extenso(relatorio.referencia)}. Uma nova emissão pode mostrar números "
        "diferentes se houver novos registros. Cada emissão fica registrada na auditoria do GPS, "
        f"com data, autor e o resumo do arquivo. Este relatório é {especie}. Encerrado e sem "
        "pendência, o relatório se chama de encerramento; com o Edital cancelado, de interrupção; "
        "nos demais casos, de acompanhamento.",
    )


SECOES = (
    "1. Visão geral",
    "2. Principais números",
    "3. Pontos de atenção",
    "4. Resultados por perfil de vaga",
    "5. Procura",
    "6. Alterações e recursos",
    "7. Datas principais",
    "8. Documentos oficiais",
    "A. Etapas de avaliação",
    "B. Classificação e vagas por lista",
    "C. Recursos e convocações por perfil",
    "D. Cronograma: previsto, retificado e registrado",
    "E. Documentos e verificação",
    "F. Como cada número foi obtido",
    "G. O que o GPS não registra",
    "H. Sobre esta emissão",
)


def composicao(relatorio, *, emissao):
    """A composição inteira, antes de virar arquivo — é o que os testes de conteúdo leem."""
    c = Composicao(metrica=METRICA_DO_EDITAL)
    _cabecalho(c, relatorio, emissao)
    _visao_geral(c, relatorio)
    _numeros(c, relatorio)
    _atencao(c, relatorio)
    _perfis(c, relatorio)
    _procura(c, relatorio)
    _alteracoes_e_recursos(c, relatorio)
    _datas(c, relatorio)
    _documentos(c, relatorio)
    _anexo(c, relatorio, emissao)
    return c


def compor(relatorio, *, emissao) -> bytes:
    """Os bytes do documento. Mesmo relatório e mesma emissão, mesmos bytes (FR-2520)."""
    navegacao = Navegacao(
        titulo=relatorio.titulo,
        autor=relatorio.unidade.get("nome") or "",
        marcadores=tuple((1, secao, secao.split(" ", 1)[0] + " ") for secao in SECOES),
        sumario=(),
    )
    return _arquivo_do_edital(
        composicao(relatorio, emissao=emissao),
        identificacao=_identificacao(relatorio),
        navegacao=navegacao,
    )
