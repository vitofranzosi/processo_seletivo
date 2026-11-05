"""Gera as três variantes a partir de `maquetes/convocacao.html` (versão 2).

A maquete principal marca com comentários o trecho que muda: `CORPO` (o prazo, o resumo e a ação)
e `COMUNICACAO` (a linha dos dados do ato). Fora deles, as variantes são idênticas a ela.
"""

import os
import re
import sys

os.chdir(sys.argv[1])
BASE = open("convocacao.html").read()


def marcado(html, nome, novo):
    return re.sub(rf"<!-- {nome} -->.*?<!-- /{nome} -->", novo, html, count=1, flags=re.S)


def cartao(html, chave, novo):
    i = html.index(f'id="item-{chave}"')
    i = html.rindex("<li", 0, i)
    j = html.index("</li>", i) + len("</li>")
    return html[:i] + novo + html[j:]


def recebido(chave, nome, quando="", conferido=False):
    if conferido:
        selo, texto = "conferido", "Conferido: de acordo com o Edital."
        rotulo = "Conferido"
    else:
        selo, rotulo = "comissao", "Aguardando conferência"
        texto = f"Recebido em {quando}. A comissão vai conferir; você não precisa fazer nada agora."
    return (
        f'<li class="requisito cartao-do-documento" id="item-{chave}" tabindex="-1">\n'
        f"      <h3>{nome}</h3>\n"
        f'      <p class="selos"><span class="selo selo-{selo}">{rotulo}</span></p>\n'
        f'      <p class="situacao-do-documento">{texto}</p>\n'
        f'      <p class="arquivo"><a href="#">Ver o arquivo recebido'
        f'<span class="oculto">: {nome}</span></a></p>\n'
        "    </li>"
    )


def contagem(html, a, b, c, rotulo_a="a enviar"):
    novo = (
        '<ul class="contagem-das-obrigacoes">\n'
        f'    <li class="a-fazer"><span class="numero">{a}</span>'
        f'<span class="rotulo">{rotulo_a}</span></li>\n'
        f'    <li><span class="numero">{b}</span><span class="rotulo">aguardando conferência</span></li>\n'
        f'    <li class="conferido"><span class="numero">{c}</span>'
        '<span class="rotulo">conferidos</span></li>\n'
        "  </ul>"
    )
    return re.sub(r'<ul class="contagem-das-obrigacoes">.*?</ul>', novo, html, count=1, flags=re.S)


def prazo(data, dia, contagem_, correcao=""):
    linha = f'\n    <p class="correcao">{correcao}</p>' if correcao else ""
    return (
        f'<div class="prazo-da-convocacao" id="prazo">{linha}\n'
        '    <p class="rotulo-do-prazo">Prazo para atender</p>\n'
        f'    <p class="data-do-prazo">{data}</p>\n'
        f'    <p class="dia-e-contagem">{dia} · {contagem_}</p>\n'
        "  </div>"
    )


def enviados(html, itens, depois=""):
    bloco = (
        '<section class="bloco-dos-formularios" id="o-que-voce-ja-enviou" '
        'aria-labelledby="titulo-enviado">\n'
        '  <h2 id="titulo-enviado">O que você já enviou</h2>\n'
        '  <ul class="requisitos-lista">\n    ' + "\n    ".join(itens) + "\n  </ul>\n"
        + depois
        + "</section>\n\n"
    )
    return html.replace("<!-- Os dados do ato", bloco + "<!-- Os dados do ato")


def nota(html, texto):
    return html.replace(
        "<!-- Os dados do ato",
        f'<p class="nota-da-maquete"><strong>Maquete.</strong> {texto}</p>\n\n<!-- Os dados do ato',
    )


NOVE_DE_NOV = prazo("10/11/2026, às 10h23", "terça-feira", "faltam 5 dias")

# --- Depois do envio do primeiro documento -----------------------------------------------------
h = BASE.replace("<title>Sua convocação", "<title>Sua convocação (depois do envio)")
h = h.replace(
    '<p class="contexto">',
    '<div class="confirmacao-do-envio" id="confirmacao" role="status" tabindex="-1" data-confirmacao>\n'
    "    <p><strong>Recebemos: Certidão de nascimento ou casamento</strong>, em 05/11/2026, "
    "às 10h25. Ela aguarda a conferência da comissão.</p>\n"
    '    <p>Próxima tarefa: <a href="#item-historico">Histórico escolar do ensino médio</a></p>\n'
    "  </div>\n"
    '  <p class="contexto">',
    1,
)
h = marcado(
    h,
    "CORPO",
    NOVE_DE_NOV
    + '\n  <p class="resumo-do-que-falta">Você ainda precisa enviar 3 documentos e o Requerimento '
    "de Matrícula.</p>\n"
    '  <a class="principal" href="#item-historico">Ver o que preciso fazer</a>',
)
h = contagem(h, 4, 1, 0)
h = cartao(h, "certidao", "")
h = enviados(h, [recebido("certidao", "Certidão de nascimento ou casamento", "05/11/2026, às 10h25")])
h = nota(
    h,
    "O envio volta a <code>#confirmacao</code>, e não ao cartão: a confirmação, o prazo, o que "
    "falta e a próxima tarefa ficam juntos. Como a confirmação tem <code>tabindex=\"-1\"</code>, o "
    "próprio navegador põe o foco nela ao seguir a âncora, sem script: o leitor de tela lê "
    "\"Recebemos: ‹documento›\", e o teclado fica a um Tab da próxima tarefa. (Voltar a uma âncora "
    "da seção punha o foco na seção, e o leitor anunciava o título dela; e um script que movesse o "
    "foco perdia para a âncora, que é seguida depois dele — as duas coisas foram medidas.) No último "
    "envio, a frase da próxima tarefa vira a da FR-3728 da 118: <em>\"Você não tem mais documentos "
    "para enviar agora. A comissão ainda vai concluir a análise.\"</em>",
)
open("convocacao-apos-envio.html", "w").write(h)

# --- Com pendência (o cenário F, numa volta três dias depois) ----------------------------------
h = BASE.replace("<title>Sua convocação", "<title>Sua convocação (com pendência)")
h = marcado(
    h,
    "CORPO",
    prazo("10/11/2026, às 10h23", "terça-feira", "faltam 2 dias")
    + '\n  <p class="resumo-do-que-falta">A comissão pediu a correção de 1 documento, e falta '
    "enviar 1.</p>\n"
    '  <a class="principal" href="#item-historico">Ver o que preciso fazer</a>',
)
h = contagem(h, 2, 0, 2, rotulo_a="a corrigir ou enviar")
h = cartao(h, "certidao", "")
h = cartao(h, "certificado", "")
h = cartao(h, "requerimento", "")
h = cartao(
    h,
    "historico",
    '<li class="requisito cartao-do-documento destaque" id="item-historico" tabindex="-1">\n'
    "      <h3>Histórico escolar do ensino médio</h3>\n"
    '      <p class="selos"><span class="selo selo-correcao">Precisa de correção</span></p>\n'
    '      <p class="instrucao">Todas as páginas, em arquivo único.</p>\n'
    '      <p class="situacao-do-documento" id="situacao-historico">Precisa de correção: Falta a '
    "página 2. Envie um novo arquivo até 10/11/2026, às 10h23.</p>\n"
    '      <p class="arquivo"><a href="#">Ver o arquivo recebido<span class="oculto">: Histórico '
    "escolar do ensino médio</span></a></p>\n"
    '      <div class="envio"><form method="post" action="#">\n'
    '        <div class="escolher">\n'
    '          <input type="file" id="arquivo-historico" name="arquivo" accept="application/pdf" '
    'aria-describedby="situacao-historico ajuda-historico">\n'
    '          <label class="botao-arquivo" for="arquivo-historico">Escolher o novo arquivo PDF'
    '<span class="oculto"> para Histórico escolar do ensino médio</span></label>\n'
    '          <span class="nome-do-arquivo">Nenhum arquivo escolhido</span>\n'
    '          <button type="submit" class="acao">Enviar<span class="oculto">: Histórico escolar '
    "do ensino médio</span></button>\n"
    "        </div>\n"
    '        <span class="ajuda limite" id="ajuda-historico">Somente PDF, até 10 MB.</span>\n'
    "      </form></div>\n"
    "    </li>",
)
h = enviados(
    h,
    [
        recebido("certidao", "Certidão de nascimento ou casamento", conferido=True),
        recebido("certificado", "Certificado de conclusão do ensino médio", conferido=True),
    ],
    '  <p class="requerimento-nas-obrigacoes"><span aria-hidden="true">✓</span> Requerimento de '
    'Matrícula enviado. <a href="#">Conferir o Requerimento de Matrícula enviado</a></p>\n',
)
h = nota(
    h,
    "O motivo da pendência aparece só aqui, no portal (115, FR-3584). A ação leva ao cartão pendente, "
    "que é a primeira obrigação que exige atenção. A política de aviso da seção 7 do estudo diria por "
    'e-mail apenas que "há documento da convocação que precisa de atenção".',
)
open("convocacao-pendencia.html", "w").write(h)

# --- A sucessora (correção da 120) ---------------------------------------------------------------
h = BASE.replace("<title>Sua convocação", "<title>Sua convocação (corrigida)")
h = marcado(
    h,
    "CORPO",
    prazo(
        "12/11/2026, às 10h23",
        "quinta-feira",
        "faltam 7 dias",
        correcao="Convocação corrigida: este é o prazo válido.",
    )
    + '\n  <p class="resumo-do-que-falta">Você ainda precisa enviar 4 documentos e o Requerimento '
    "de Matrícula.</p>\n"
    '  <a class="principal" href="#item-certidao">Ver o que preciso fazer</a>',
)
h = marcado(
    h,
    "COMUNICACAO",
    "<dt>Comunicação</dt><dd>Mensagem da correção enviada em 05/11/2026, às 10h24. O prazo conta a "
    "partir deste envio.</dd>\n"
    "    <dt>Convocação substituída</dt><dd>Comunicada em 05/11/2026, às 10h23, com prazo até "
    "10/11/2026, às 10h23. Esse prazo não vale mais.</dd>",
)
h = nota(
    h,
    "A correção é dita dentro do cartão do prazo, que é o que ela corrigiu, e a mensagem substituída "
    "fica nos dados do ato, com o prazo antigo por extenso: quem guardou a primeira mensagem reconhece "
    "a data e lê que ela não vale mais. O motivo da correção continua fora do portal (120, linhas "
    "486–487).",
)
open("convocacao-sucessora.html", "w").write(h)
print("ok")
