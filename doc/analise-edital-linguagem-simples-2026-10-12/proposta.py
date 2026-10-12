"""Amostra: os cenários A e B da auditoria de 08/10, compostos como o lote 1 os comporia.

Não é implementação. É uma composição com as primitivas do compositor de hoje (`Composicao`,
`_tabela`, `_quebrar`, `_instante`, brasão, órgão, fecho, autoridade), para que a proposta fique
presa ao que o motor atual sabe paginar. O que ele não tem está aqui, pequeno e declarado:

- **E1** caixa com fundo claro (o motor só tem contorno);
- **E2** item de lista com recuo pendente (ED-16);
- **E3** sumário com número de página, por duas passadas da paginação que já existe;
- **E4** no arquivo: título, idioma, marcadores e links;
- **E5** fonte TrueType embutida (subconjunto WinAnsi), quando `--fontes` aponta para ela;
- **E6** larguras medidas na fonte embutida — o `pdf.py` mede "í" como "i" (222 em vez de 278).

**Nada aqui é escrito para um cenário.** O mesmo código compõe os dois: agrupa por identidade do
dado, decide entre um quadro único de vagas e dois quadros pelo próprio dado (todo Perfil tem vaga
imediata?), gera as frases da classificação pelo tipo da regra (sorteio ou pontuação, tipo de
corte, de empate, de desempate) e só imprime o que existe. O que é de cada cenário é a **redação do
Elaborador** — o texto livre das seções, reescrito seguindo o guia, nos dicionários `REDACAO_*` —,
porque é isso que, no produto, viria de quem elabora, e não do sistema.

Uso, de `backend/`:
    uv run python ../doc/analise-edital-linguagem-simples-2026-10-12/proposta.py A <saída.pdf> \\
        [--fontes <pasta com LiberationSans-Regular.ttf e LiberationSans-Bold.ttf>]

Sem `--fontes`, o documento sai com Helvetica não embutida, como hoje. Com elas, precisa do
`fonttools` (`uv run --with fonttools …`).
"""

import json
import os
import re
import sys
import zlib
from datetime import date
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
import django  # noqa: E402

django.setup()

from processo_seletivo.publicacoes.infrastructure import brasao  # noqa: E402
from processo_seletivo.publicacoes.infrastructure import pdf  # noqa: E402
from processo_seletivo.publicacoes.infrastructure.pdf import (  # noqa: E402
    CENTRO,
    CORPO_NOTA,
    CORPO_TEXTO,
    DIREITA,
    ESQUERDA,
    LARGURA,
    MARGEM,
    NEGRITO,
    REGULAR,
    AutoridadeSignataria,
    Composicao,
    UnidadeDoAto,
)

RAIZ = Path(__file__).resolve().parents[2]
UNIDADE = UnidadeDoAto(
    cabecalho=("Centro de Referência em Formação", "e em Educação a Distância"), local="Vitória (ES)"
)
CARGO = "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância"
DATA_DO_ATO = date(2026, 10, 8)
# As siglas que a caixa alta não pode alterar (ED-24): a da instituição e a da Unidade, que o
# registro da 060 já tem. Palavra com maiúscula depois de minúscula ("EaD") também se preserva.
SIGLAS = {"Ifes", "Cefor", "Cefor/Ifes"}

# O endereço do certame. Hoje nenhuma fonte o dá por inteiro (§3.4 do relatório): a rota existe, o
# domínio não. Aqui ele aparece só onde o **Elaborador** o escreveria, com o formato que a fonte
# proposta produziria, e marcado como exemplo.
ENDERECO = "https://exemplo.ifes.edu.br/selecoes/{numero}-{ano}"

# ---------------------------------------------------------------------------------------------
# Redação do Elaborador. Cada chave é a seção do snapshot de onde o texto vem. Nada foi tirado;
# a numeração digitada ("1.1", "3.2"…) saiu, porque a do documento é calculada (065).
# ---------------------------------------------------------------------------------------------
REDACAO_A = {
    "disposicoes-preliminares": [
        "Este processo seletivo será conduzido por uma Comissão de Seleção designada pela "
        "Diretora-Geral do Cefor.",
        "Dúvidas sobre este Edital são esclarecidas somente pelo e-mail "
        "selecao.demo@exemplo.ifes.edu.br, de segunda a sexta-feira, das 8h às 17h.",
        "Todas as publicações deste processo seletivo serão feitas em {endereco}.",
    ],
    "informacoes-gerais": [
        "O curso é oferecido totalmente a distância, no Ambiente Virtual de Aprendizagem (AVA). "
        "Há encontros síncronos (ao vivo) obrigatórios para as avaliações finais e para a "
        "apresentação do Trabalho Final de Curso.",
        "Carga horária: 480 horas. Duração prevista: 18 meses.",
    ],
    "publico-alvo": [
        "Pode se inscrever quem tem diploma de curso superior de graduação, em qualquer área do "
        "conhecimento.",
    ],
    "requisitos-gerais": [
        "Para se inscrever, é preciso atender a todos os requisitos abaixo.",
    ],
    "inscricao": [
        "A inscrição é feita somente pela internet, em {endereco}.",
        "• Escolha o polo e a lista de concorrência: ampla concorrência ou uma das reservas de "
        "vagas (item {vagas}).",
        "• Anexe os documentos do item {documentos}.",
        "• Envie o Requerimento de Matrícula, que faz parte da inscrição (item {matricula}).",
        "Quem concorre a uma vaga reservada concorre também às vagas de ampla concorrência do "
        "mesmo polo.",
    ],
    "classificacao": [
        "Havendo mais inscritos que vagas, a ordem de classificação será definida por sorteio "
        "eletrônico, pelo método descrito no item {sorteio}.",
        "Após o sorteio, serão analisados os documentos dos sorteados até o número de vagas do "
        "polo e da lista, mais os suplentes previstos.",
    ],
    "verificacao-autodeclaracao": [
        "Quem for sorteado para as vagas reservadas a pretos e pardos será convocado para a "
        "verificação complementar da autodeclaração, por webconferência, em data a ser divulgada.",
        "Se a autodeclaração for indeferida, o candidato permanece apenas na lista de ampla "
        "concorrência.",
    ],
    "recursos": [
        "Contra o resultado preliminar da análise documental: no prazo do Cronograma (nº 7), "
        "somente pelo sistema de inscrição.",
        "Não serão aceitos recursos enviados por e-mail ou fora do prazo.",
    ],
    "convocacao": [
        "Havendo desistência, serão convocados os suplentes, na ordem do sorteio, por publicação "
        "em {endereco}.",
    ],
    "matricula": [
        "A matrícula será feita com a documentação enviada na inscrição, sem necessidade de "
        "comparecimento presencial.",
    ],
    "certificado": [
        "Terá direito ao certificado de especialista o aluno aprovado em todos os componentes "
        "curriculares e no Trabalho Final de Curso.",
    ],
    "disposicoes-finais": [
        "Os casos omissos — situações que este Edital não prevê — serão resolvidos pela Comissão "
        "de Seleção, ouvida a Diretoria de Ensino do Cefor.",
    ],
    # A descrição do Perfil, reescrita sem repetir o polo, que já é a localidade: idênticas nos
    # quatro, saem uma vez, pela identidade de texto da 064 e da 068.
    "descricao-do-perfil": "Curso de pós-graduação lato sensu, a distância, com encontros síncronos.",
}

REDACAO_B = {
    "disposicoes-preliminares": [
        "Este processo seletivo é regido por este Edital e executado pela Comissão de Seleção "
        "designada por portaria da Diretora-Geral do Cefor.",
        "A seleção forma cadastro de reserva. Os classificados serão convocados conforme a "
        "necessidade dos cursos, durante o prazo de validade deste Edital.",
        "A atuação como bolsista não gera vínculo empregatício com o Ifes nem com a CAPES.",
        "É proibido acumular bolsas pagas pelos programas de fomento da CAPES e do FNDE.",
    ],
    "requisitos-gerais": [
        "Para se inscrever, é preciso:",
        "• ser brasileiro nato ou naturalizado, ou estrangeiro com situação regular no país;",
        "• estar quite com as obrigações eleitorais e, se do sexo masculino, com as obrigações "
        "militares;",
        "• não ter vínculo com outra bolsa paga pela CAPES ou pelo FNDE no período de atuação;",
        "• atender aos requisitos específicos do Perfil pretendido, listados abaixo.",
    ],
    "inscricao": [
        "A inscrição é feita somente pelo sistema de inscrições.",
        "Anexe, num único arquivo PDF de até 10 MB, os documentos obrigatórios e os documentos "
        "que serão pontuados. Dê ao arquivo o nome no formato EDITAL 92.2026_CÓDIGO DE "
        "INSCRIÇÃO_MODALIDADE_NOME DO CANDIDATO.",
        "Os documentos não são conferidos no momento da inscrição. O candidato é o único "
        "responsável pela documentação que enviar.",
        "Atenção: a documentação com mais de 30 (trinta) páginas leva ao indeferimento da "
        "inscrição, sem possibilidade de recurso.",
    ],
    "atendimento-pcd": [
        "O candidato com deficiência que precisar de atendimento especializado para participar das "
        "etapas deve pedi-lo no formulário de inscrição, indicando os recursos necessários.",
    ],
    "classificacao": [
        "A nota final, depois da fase de recursos, será a pontuação obtida na prova de títulos, "
        "apresentada em ordem decrescente por código de inscrição.",
        "Cada candidato pode concorrer a apenas um código de inscrição.",
    ],
    "verificacao-autodeclaracao": [
        "Quem se autodeclarar preto ou pardo passará pelo procedimento de heteroidentificação, "
        "feito por comissão designada para esse fim, por webconferência.",
        "A comissão considerará somente as características fenotípicas do candidato.",
        "Quem não comparecer ao procedimento será excluído da lista reservada e permanecerá na "
        "lista de ampla concorrência.",
    ],
    "recursos": [
        "Os recursos devem ser apresentados somente pelo formulário eletrônico de recursos, cujo "
        "link será disponibilizado na página do processo seletivo, nos prazos do Cronograma.",
        "Não é permitido enviar documentos na fase de recursos.",
        "Não serão aceitos recursos enviados por Correios, e-mail ou qualquer outra forma.",
    ],
    "convocacao": [
        "A mensagem será enviada ao endereço eletrônico informado na inscrição. O convocado terá "
        "2 (dois) dias úteis, contados do envio, para manifestar interesse.",
        "Quem não se manifestar no prazo será considerado desistente e substituído pelo próximo "
        "classificado do mesmo código de inscrição.",
    ],
    "prazo-de-validade": [
        "Este processo seletivo vale por 2 (dois) anos, contados da publicação do resultado final, "
        "e pode ser prorrogado uma única vez, por igual período.",
    ],
    "disposicoes-finais": [
        "A inscrição implica o conhecimento e a aceitação das normas deste Edital.",
        "Os casos omissos — situações que este Edital não prevê — serão resolvidos pela Comissão "
        "de Seleção, ouvida a Coordenação UAB do Ifes.",
        "Dúvidas podem ser enviadas ao e-mail selecao.uab.demo@exemplo.ifes.edu.br.",
    ],
}

CENARIOS = {
    "A": {
        "snapshot": "doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json",
        "redacao": REDACAO_A,
        "autoridade": AutoridadeSignataria(
            nome="Fulana de Tal",
            cargo=CARGO,
            ato_de_nomeacao="Portaria nº 0000, de 2 de janeiro de 2026 (fictícia)",
        ),
        "titulo": "Edital nº 91/2026 — Pós-graduação em Informática na Educação (DEMONSTRAÇÃO)",
    },
    "B": {
        "snapshot": "doc/auditoria-edital-pdf-2026-10-08/snapshots/B-conteudo-publicado.json",
        "redacao": REDACAO_B,
        # O cenário B publica com a autoridade só pelo cargo (ED-10), como o registro do Cefor.
        "autoridade": AutoridadeSignataria(nome="", cargo=CARGO, ato_de_nomeacao=""),
        "titulo": "Edital nº 92/2026 — Cadastro de reserva de tutores UAB (DEMONSTRAÇÃO)",
    },
}

CORPO_SECAO = 12.5
CORPO_SUBSECAO = 11.0
ANTES_DA_SECAO = 22.0
PENDENTE = 14.0
# Seção ou bloco até esta altura é coeso: não começa no pé de uma página para continuar na outra.
# Acima dela, flui, e só os sub-blocos são coesos — senão o branco no pé da página vira regra.
ALTURA_COESA = 0.45 * (pdf.TOPO - (pdf.RODAPE + 24))


# ---------------------------------------------------------------------------------------------
# E5, E6: fonte embutida e larguras da própria fonte
# ---------------------------------------------------------------------------------------------
class Fontes:
    """O subconjunto WinAnsi da Liberation Sans, com as larguras que o compositor passa a medir."""

    def __init__(self, pasta):
        from fontTools import subset
        from fontTools.ttLib import TTFont

        self.dados = {}
        for chave, arquivo in ((REGULAR, "LiberationSans-Regular.ttf"), (NEGRITO, "LiberationSans-Bold.ttf")):
            # Sem recalcular a data do `head` ao salvar: senão cada execução gera bytes diferentes.
            fonte = TTFont(Path(pasta) / arquivo, recalcTimestamp=False)
            unidades = fonte["head"].unitsPerEm
            mapa = fonte.getBestCmap()
            larguras = {}
            for codigo in range(32, 256):
                try:
                    caractere = bytes([codigo]).decode("cp1252")
                except UnicodeDecodeError:
                    continue
                glifo = mapa.get(ord(caractere))
                if glifo is not None:
                    larguras[codigo] = round(fonte["hmtx"][glifo][0] * 1000 / unidades)
            opcoes = subset.Options()
            opcoes.recalc_timestamp = False
            opcoes.name_IDs = ["*"]
            opcoes.notdef_outline = True
            sub = subset.Subsetter(opcoes)
            sub.populate(unicodes=[ord(bytes([c]).decode("cp1252")) for c in larguras])
            sub.subset(fonte)
            saida = BytesIO()
            fonte.save(saida)
            cabeca, os2 = fonte["head"], fonte["OS/2"]
            self.dados[chave] = {
                "nome": ("AAAAAA+" if chave == REGULAR else "AAAAAB+")
                + ("LiberationSans" if chave == REGULAR else "LiberationSans-Bold"),
                "arquivo": saida.getvalue(),
                "larguras": larguras,
                "bbox": [round(v * 1000 / unidades) for v in (cabeca.xMin, cabeca.yMin, cabeca.xMax, cabeca.yMax)],
                "ascent": round(os2.sTypoAscender * 1000 / unidades),
                "descent": round(os2.sTypoDescender * 1000 / unidades),
                "cap": round(getattr(os2, "sCapHeight", 0) * 1000 / unidades) or 700,
            }

    def largura(self, texto, tamanho, fonte=REGULAR):
        larguras = self.dados[fonte]["larguras"]
        total = 0
        for caractere in str(texto):
            try:
                codigo = caractere.encode("cp1252")[0]
            except (UnicodeEncodeError, IndexError):
                codigo = None
            total += larguras.get(codigo, 1000)
        return total * tamanho / 1000

    def objetos(self, primeiro):
        """Os objetos das duas fontes, a partir do número `primeiro`; devolve (objetos, ids)."""
        objetos, ids = [], {}
        numero = primeiro
        for chave in (REGULAR, NEGRITO):
            d = self.dados[chave]
            comprimido = zlib.compress(d["arquivo"], 9)
            larguras = " ".join(str(d["larguras"].get(c, 0)) for c in range(32, 256))
            ids[chave] = numero
            objetos.append(
                f"<< /Type /Font /Subtype /TrueType /BaseFont /{d['nome']} /FirstChar 32 "
                f"/LastChar 255 /Widths [{larguras}] /Encoding /WinAnsiEncoding "
                f"/FontDescriptor {numero + 1} 0 R >>".encode()
            )
            objetos.append(
                f"<< /Type /FontDescriptor /FontName /{d['nome']} /Flags 32 "
                f"/FontBBox [{' '.join(map(str, d['bbox']))}] /ItalicAngle 0 /Ascent {d['ascent']} "
                f"/Descent {d['descent']} /CapHeight {d['cap']} "
                f"/StemV {80 if chave == REGULAR else 140} /FontFile2 {numero + 2} 0 R >>".encode()
            )
            objetos.append(
                f"<< /Length {len(comprimido)} /Length1 {len(d['arquivo'])} /Filter /FlateDecode "
                f">>\nstream\n".encode()
                + comprimido
                + b"\nendstream"
            )
            numero += 3
        return objetos, ids


# ---------------------------------------------------------------------------------------------
# Escrita
# ---------------------------------------------------------------------------------------------
class Titulos:
    def __init__(self):
        self.itens = []
        self.paginas = {}
        self.sumario = []


def caixa_alta(texto):
    """Caixa alta do anúncio, preservando as siglas (ED-24)."""
    return " ".join(
        palavra
        if palavra.strip("(),.") in SIGLAS or re.search(r"[a-zà-ú][A-ZÀ-Ú]", palavra)
        else palavra.upper()
        for palavra in texto.split(" ")
    )


def item(c, marcador, texto, *, recuo=0.0, antes=3.0, fonte=REGULAR):
    """E2: o marcador na margem e todas as linhas do texto alinhadas depois dele."""
    linhas = pdf._quebrar(texto, CORPO_TEXTO, recuo + PENDENTE, fonte)
    # Um item não se parte entre páginas: a continuação de um critério sozinha no topo da página
    # seguinte perde o número que diz de que critério ela é.
    with c.bloco(coeso=True):
        c.escrever(marcador, recuo=recuo, antes=antes)
        for indice, linha in enumerate(linhas):
            c.escrever(
                linha,
                fonte=fonte,
                recuo=recuo + PENDENTE,
                antes=-(CORPO_TEXTO * 1.45) if indice == 0 else 0.0,
            )


def paragrafo(c, texto, *, antes=6.0, recuo=0.0):
    """Linha que o Elaborador abre com "•" vira item de lista; as demais, parágrafo justificado."""
    if texto.startswith("• "):
        item(c, "•", texto[2:], antes=3.0, recuo=recuo)
        return
    c.escrever(texto, antes=antes, recuo=recuo, justificar=True)


def rotulo_e_valor(c, rotulo, valor, *, coluna=88.0, antes=3.0):
    linhas = pdf._quebrar(valor, CORPO_TEXTO, coluna)
    c.escrever(rotulo, fonte=NEGRITO, antes=antes)
    for indice, linha in enumerate(linhas):
        c.escrever(linha, recuo=coluna, antes=-(CORPO_TEXTO * 1.45) if indice == 0 else 0.0)


def rotulo_de_grupo(c, texto):
    c.escrever(texto, fonte=NEGRITO, antes=8, junto=True)


def coeso(c, compor):
    """Compõe à parte e decide: o que cabe em `ALTURA_COESA` não se separa na quebra de página."""
    rascunho = Composicao()
    compor(rascunho)
    altura = sum(Composicao._altura(i) for i in rascunho.itens)
    if altura <= ALTURA_COESA:
        c.itens.append(("abre", False, True))
        c.itens.extend(rascunho.itens)
        c.itens.append(("fecha", False, True))
    else:
        c.itens.extend(rascunho.itens)


# Tabela até esta altura não se parte: a de B deixava uma linha só (TP-16) na página seguinte.
# Acima dela, a cascata de hoje quebra entre linhas e repete o cabeçalho.
ALTURA_DA_TABELA_COESA = 0.6 * (pdf.TOPO - (pdf.RODAPE + 24))


def tabela(c, legenda, cabecalho, linhas, *, alinhamentos=None, rodape=None):
    rascunho = Composicao()
    pdf._tabela(
        rascunho, cabecalho, linhas, recuo=0.0, alinhamentos=alinhamentos, legenda=legenda, rodape=rodape
    )
    altura = sum(Composicao._altura(i) for i in rascunho.itens)
    coesa = altura <= ALTURA_DA_TABELA_COESA
    if coesa:
        c.itens.append(("abre", False, True))
    c.itens.extend(rascunho.itens)
    if coesa:
        c.itens.append(("fecha", False, True))


def periodo(inicio, fim=None):
    if not fim:
        return pdf._instante(inicio)
    return f"de {pdf._instante(inicio)}, a {pdf._instante(fim)}"


def por_extenso(numero):
    palavra = pdf.POR_EXTENSO.get(numero)
    return f"{numero} ({palavra})" if palavra else str(numero)


def enumerar(partes):
    partes = list(partes)
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " e " + partes[-1]


def codigos(perfis):
    """Os códigos de um grupo; faixa ("TP-01 a TP-16") só quando é contígua e sem lacuna."""
    lista = [p["code"] for p in perfis]
    partes = [re.fullmatch(r"(.*?)(\d+)", codigo) for codigo in lista]
    if len(lista) > 2 and all(partes):
        prefixos = {m.group(1) for m in partes}
        numeros = [int(m.group(2)) for m in partes]
        larguras = {len(m.group(2)) for m in partes}
        if len(prefixos) == 1 and len(larguras) == 1 and numeros == list(
            range(numeros[0], numeros[0] + len(numeros))
        ):
            return f"{lista[0]} a {lista[-1]}"
    return enumerar(lista)


def agrupar(perfis, chave):
    """Os Perfis que têm o mesmo valor, na ordem do snapshot — a identidade da 064 e da 068."""
    grupos = {}
    for perfil in perfis:
        grupos.setdefault(json.dumps(chave(perfil), sort_keys=True, ensure_ascii=False), []).append(perfil)
    return list(grupos.values())


def linhas_de(texto):
    return [linha.strip().lstrip("●•").strip() for linha in str(texto or "").splitlines() if linha.strip()]


# ---------------------------------------------------------------------------------------------
# As frases geradas do lote 1 (G): a regra dita na voz do candidato, pelo tipo declarado
# ---------------------------------------------------------------------------------------------
REVERSAO = {
    "ON_EXHAUSTION": "Se não houver candidatos aprovados para as vagas reservadas de um código, "
    "essas vagas passam para a ampla concorrência do mesmo código.",
    "ON_BALANCE": "As vagas reservadas de um código que não forem preenchidas passam para a "
    "ampla concorrência do mesmo código.",
}
CONVOCACAO = {
    "PUBLICATION": "A convocação dos classificados será feita por publicação.",
    "INDIVIDUAL_MESSAGE": "A convocação será feita por mensagem individual à pessoa convocada.",
}


def frases_do_marco(s, marco, etapas, fatos, sem_cadastro=False):
    """A regra de classificação de um marco, em itens. Devolve (itens, caixa_do_sorteio)."""
    itens = []
    corte = marco.get("cutRule") or {}
    governada = etapas.get(corte.get("governedStage"), {}).get("name", "a etapa seguinte")
    if marco["orderProduction"] == "POR_SORTEIO":
        itens.append("Participam do sorteio todas as inscrições enviadas.")
    else:
        das_etapas = [etapas[e] for e in marco.get("stages", []) if e in etapas]
        if len(das_etapas) == 1 and marco.get("normalization") == "NENHUMA":
            itens.append(f"A nota final é a pontuação obtida na Etapa “{das_etapas[0]['name']}”.")
        else:
            itens.append(
                "A nota final é a soma ponderada das Etapas "
                + enumerar(f"“{e['name']}” (peso {pdf.humano.decimal(e['weight'])})" for e in das_etapas)
                + "."
            )
        arredondamento = marco.get("rounding") or {}
        if arredondamento.get("scale") is not None:
            casas = por_extenso(arredondamento["scale"]).replace(" (", " ").rstrip(")")
            regra = {
                "MEIO_PARA_CIMA": "; a partir da metade, arredonda-se para cima",
                "TRUNCAMENTO": ", desprezando-se as demais",
            }.get(arredondamento.get("mode"), "")
            itens.append(f"A nota final é arredondada para {arredondamento['scale']} casas decimais{regra}.")
    if corte:
        # O corte é uma unidade: o empate fala de "esse número", e a continuação de "além desses".
        # Separadas na partilha parcial, as frases perderiam o referente (a amostra errou assim).
        unidade = []
        if corte["targetKind"] == "FROM_VACANCY_TABLE":
            quantos = "os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista no código"
        else:
            quantos = f"os {por_extenso(corte['targetCount'])} primeiros classificados"
        frase = f"Passam para a Etapa “{governada}” {quantos}"
        if corte.get("surplusCount"):
            frase += f", mais {por_extenso(corte['surplusCount'])} suplentes"
        unidade.append(frase + ".")
        if corte.get("tieOutcome") == "ADMITS_SURPLUS":
            unidade.append(
                "Se houver empate na última posição, passam todos os empatados, mesmo que "
                "ultrapassem esse número."
            )
        elif corte.get("tieOutcome") == "STRICT" and marco["orderProduction"] != "POR_SORTEIO":
            unidade.append("Se houver empate na última posição, esse número não é ultrapassado.")
        # Frase nova, que descreve a regra do sistema (019, 050: suplente só é chamado para vaga
        # imediata não preenchida). Só sai sem cadastro de reserva: com ele, a relação entre os
        # suplentes e o cadastro é a pendência DP-05, e o documento não pode explicá-la.
        if corte.get("surplusCount") and sem_cadastro:
            unidade.append(
                "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem "
                "preenchidas pelos primeiros classificados."
            )
        if corte.get("continuation") == "ALLOWED":
            # Sem condição: a norma publicada não diz "se sobrarem vagas" (a primeira redação da
            # amostra acrescentou essa condição, e a conferência de equivalência a pegou).
            unidade.append("Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem.")
        itens.append(("unidade", unidade))
    desempates = sorted(marco.get("tiebreakers") or [], key=lambda t: t["order"])
    if desempates:
        partes = []
        for t in desempates:
            ausente = {
                "ULTIMO_NO_CRITERIO": "quem não {o} informar fica em último lugar neste critério",
                "CRITERIO_NAO_SE_APLICA": "para quem não a tiver, o critério não se aplica",
            }.get(t["whenMissing"], "")
            if t["type"] == "MAIOR_PONTUACAO_NA_ETAPA":
                alvo = etapas.get(t["parameters"].get("stageId"), {}).get("name", "")
                texto = f"maior pontuação na Etapa “{alvo}”"
            else:
                fato = fatos.get(t["parameters"].get("factId"), {})
                rotulo = fato.get("label", "")
                if fato.get("type") == "DATA" and t["type"] == "MENOR_VALOR_DE_FATO":
                    texto = f"maior idade ({rotulo.lower()} mais antiga, informada na inscrição)"
                elif fato.get("type") == "DATA":
                    texto = f"menor idade ({rotulo.lower()} mais recente, informada na inscrição)"
                else:
                    sentido = "maior" if t["type"] == "MAIOR_VALOR_DE_FATO" else "menor"
                    texto = f"{sentido} número de {rotulo[0].lower()}{rotulo[1:]}, informado na inscrição"
            genero = "a" if fatos.get(t["parameters"].get("factId"), {}).get("type") == "DATA" else "o"
            partes.append(f"{t['order']}º {texto}; {ausente.format(o=genero)}")
        itens.append(("desempate", partes))
    return itens


def frase_do_recurso(marco):
    janela = marco.get("appealWindow") or {}
    if not janela:
        return None
    if not janela.get("admits"):
        return f"Não caberá recurso contra o resultado de “{marco['name']}”."
    unidade = {"DIAS_CORRIDOS": "dias corridos", "DIAS_UTEIS": "dias úteis"}.get(janela.get("unit"), "dias")
    return (
        f"Contra o resultado de “{marco['name']}”: no prazo de {por_extenso(janela['durationDays'])} "
        f"{unidade}, contados da divulgação desse resultado."
    )


def rotulo_do_grupo(grupo, total):
    if len(grupo) == total:
        return "Para todos os Perfis"
    if len(grupo) == 1:
        return f"Para o Perfil {grupo[0]['code']} — {grupo[0]['name']}"
    return f"Para os Perfis {codigos(grupo)}"


# ---------------------------------------------------------------------------------------------
# A composição
# ---------------------------------------------------------------------------------------------
def compor(s, redacao, autoridade, titulos, hash_):
    c = Composicao()
    tabelas = pdf._Numerador()
    perfis = s["profiles"]
    etapas = {e["id"]: e for e in s["stages"]}
    endereco = ENDERECO.format(numero=s["number"], ano=s["year"])
    inscricoes = next((e for e in s["schedule"] if e.get("isRegistrationPeriod")), None)
    secoes = {x["key"]: x for x in s["sections"]}

    # A numeração é decidida antes: só entra seção com conteúdo, e o texto do Elaborador remete
    # aos números calculados, como a 065 exige.
    plano = []

    def tem(chave):
        return bool(redacao.get(chave))

    marcos_por_perfil = [p.get("classificationMilestones") or [] for p in perfis]
    tem_requerimento = (s.get("matriculationRequest") or {}).get("moment") == "AT_ENROLLMENT"
    for chave, titulo, presente in (
        ("disposicoes-preliminares", "Disposições preliminares", tem("disposicoes-preliminares")),
        ("informacoes-gerais", "Sobre o curso", tem("informacoes-gerais")),
        ("quem-pode", "Quem pode se inscrever?", True),
        ("vagas", "Quantas vagas há, e onde?", True),
        ("cronograma", "Cronograma", bool(s["schedule"])),
        ("inscricao", "Como se inscrever?", True),
        ("documentos", "Quais documentos enviar?", bool(s["documentRequirements"])),
        ("selecao", "Como será a seleção?", True),
        ("recursos", "Como recorrer?", True),
        ("convocacao", "Como será a convocação?", True),
        ("matricula", "Como será a matrícula?", tem("matricula") or tem_requerimento),
        ("certificado", "Certificado", tem("certificado")),
        ("prazo-de-validade", "Prazo de validade", tem("prazo-de-validade")),
        ("anexos", "Anexos", bool(s["attachments"])),
        ("disposicoes-finais", "Disposições finais", tem("disposicoes-finais")),
    ):
        if presente:
            plano.append((chave, titulo))
    numero = {chave: indice for indice, (chave, _) in enumerate(plano, 1)}
    sorteio = any(m["orderProduction"] == "POR_SORTEIO" for ms in marcos_por_perfil for m in ms)
    referencias = {
        "endereco": endereco,
        "vagas": numero["vagas"],
        "documentos": numero.get("documentos", ""),
        "matricula": numero.get("matricula", ""),
        "sorteio": f"{numero['selecao']}.2" if sorteio else "",
    }

    def redigido(chave):
        return [t.format(**referencias) for t in redacao.get(chave, [])]

    def secao(cc, chave):
        rotulo = f"{numero[chave]}. {dict(plano)[chave]}"
        titulos.itens.append((1, rotulo))
        cc.escrever(rotulo, tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ANTES_DA_SECAO, junto=True)
        cc.espaco(3)
        cc.regua()
        cc.espaco(2)

    def subsecao(cc, rotulo):
        titulos.itens.append((2, rotulo))
        cc.escrever(rotulo, tamanho=CORPO_SUBSECAO, fonte=NEGRITO, antes=12, junto=True)

    # ---- Abertura ----
    c.espaco(pdf.ALTURA_DO_BRASAO + 6)
    for indice, linha in enumerate(pdf.linhas_do_orgao(UNIDADE)):
        c.escrever(linha, tamanho=pdf.CORPO_INSTITUCIONAL, alinhamento=CENTRO, antes=0 if indice else 4)
    anuncio = caixa_alta(pdf.anuncio_do_ato(s))
    for indice, linha in enumerate(pdf._quebrar(anuncio, pdf.CORPO_ATO, 40, NEGRITO)):
        c.escrever(linha, tamanho=pdf.CORPO_ATO, fonte=NEGRITO, antes=20 if not indice else 0, alinhamento=CENTRO)
    c.escrever(secoes["apresentacao"]["content"], antes=16, justificar=True)

    # ---- Resumo (só dado estruturado, cada linha com o item) ----
    total = sum(p["immediateVacancies"] for p in perfis)
    com_vaga = [p for p in perfis if p["immediateVacancies"]]
    reservas = {(p["reserveType"], p.get("reserveLimit")) for p in perfis}
    marcos = [m for ms in marcos_por_perfil for m in ms]
    with c.bloco(moldura=True, coeso=True):
        c.escrever("Resumo deste Edital", tamanho=CORPO_SUBSECAO, fonte=NEGRITO, antes=10)
        if len(com_vaga) == len(perfis):
            locais = [p["locality"] for p in perfis]
            vagas = f"{total}, em {len(perfis)} Perfis: {enumerar(locais)} (item {numero['vagas']})."
        else:
            vagas = (
                f"{total} imediatas, nos Perfis {codigos(com_vaga)}; os demais "
                f"{len(perfis) - len(com_vaga)} Perfis formam só cadastro de reserva (item {numero['vagas']})."
            )
        rotulo_e_valor(c, "Vagas", vagas)
        if len(reservas) == 1:
            tipo, limite = reservas.pop()
            cadastro = {
                "NONE": "não há.",
                "LIMITED": f"até {por_extenso(limite)} classificados em cada Perfil.",
                "UNLIMITED": "sem limite de classificados.",
            }[tipo]
            rotulo_e_valor(c, "Cadastro", f"{cadastro[0].upper()}{cadastro[1:]}")
        if inscricoes:
            rotulo_e_valor(c, "Inscrições", f"{periodo(inscricoes['startAt'], inscricoes['endAt'])} (item {numero['inscricao']}).")
        if s.get("maxInscricoesPorCandidato"):
            rotulo_e_valor(
                c, "Por candidato", f"{por_extenso(s['maxInscricoesPorCandidato']).replace('1 (um)', '1 (uma)')} inscrição enviada neste Edital."
            )
        formas = {m["orderProduction"] for m in marcos}
        governadas = {
            etapas.get((m.get("cutRule") or {}).get("governedStage"), {}).get("name") for m in marcos
        } - {None}
        if len(formas) == 1 and len(governadas) <= 1:
            forma = "sorteio eletrônico" if formas == {"POR_SORTEIO"} else "pontuação"
            seguinte = f", seguida da Etapa “{governadas.pop()}”" if governadas else ""
            rotulo_e_valor(c, "Seleção", f"classificação por {forma} em cada Perfil{seguinte} (item {numero['selecao']}).")
        rotulo_e_valor(c, "Datas", f"todas no Cronograma (item {numero['cronograma']}).")
        c.escrever(
            "Este resumo repete informações do Edital. As regras completas estão nos itens indicados.",
            tamanho=CORPO_NOTA + 1,
            antes=6,
        )

    # ---- Sumário (E3) ----
    c.itens.append(("abre", False, True))
    c.escrever("Sumário", tamanho=CORPO_SUBSECAO, fonte=NEGRITO, antes=18, junto=True)
    for _, texto in titulos.sumario:
        pagina = str(titulos.paginas.get(texto, "0"))
        disponivel = LARGURA - 2 * MARGEM - pdf.largura(pagina, CORPO_TEXTO) - 6
        pontos = " ." * int((disponivel - pdf.largura(texto, CORPO_TEXTO) - 6) / pdf.largura(" .", CORPO_TEXTO))
        c.escrever(texto + pontos, antes=1.5)
        c.escrever(pagina, alinhamento=DIREITA, antes=-(CORPO_TEXTO * 1.45))
    c.itens.append(("fecha", False, True))
    titulos.itens = []

    # ---- Seções ----
    def textual(chave):
        def compor_secao(cc):
            secao(cc, chave)
            for t in redigido(chave):
                paragrafo(cc, t)
        coeso(c, compor_secao)

    if "disposicoes-preliminares" in numero:
        textual("disposicoes-preliminares")
    if "informacoes-gerais" in numero:
        textual("informacoes-gerais")

    # Quem pode: o texto do Elaborador e os requisitos de cada grupo de Perfis com a mesma lista.
    grupos_de_requisitos = agrupar(perfis, lambda p: p["requirements"])

    def quem_pode(cc):
        secao(cc, "quem-pode")
        for t in redigido("publico-alvo") + redigido("requisitos-gerais"):
            paragrafo(cc, t)
        for grupo in grupos_de_requisitos:
            if not grupo[0]["requirements"]:
                continue
            if len(grupos_de_requisitos) > 1:
                rotulo_de_grupo(cc, rotulo_do_grupo(grupo, len(perfis)) + ":")
            for requisito in grupo[0]["requirements"]:
                item(cc, "•", requisito.rstrip(".") + ".")
    coeso(c, quem_pode)

    # Vagas: um quadro só quando todo Perfil tem vaga imediata; senão, Perfis e vagas à parte.
    def vagas_por_codigo(perfil):
        nomes = {m["id"]: m["code"] for m in perfil["competitionModalities"]}
        ampla = nomes[perfil["generalCompetitionModalityId"]]
        return {(nomes[l["modalityId"]] if l["modalityId"] else ampla): l["immediateVacancies"] for l in perfil["vacancyTable"]}

    ampla = {m["id"]: m for m in perfis[0]["competitionModalities"]}[perfis[0]["generalCompetitionModalityId"]]
    listas = [
        {m["id"]: m for m in perfis[0]["competitionModalities"]}[l["modalityId"]]
        for l in perfis[0]["vacancyTable"]
        if l["modalityId"]
    ]
    comuns = {
        campo: perfis[0][campo]
        for campo in ("name", "workload", "compensation", "reserveType", "reserveLimit", "locality")
        if len({json.dumps(p.get(campo)) for p in perfis}) == 1 and perfis[0].get(campo)
    }
    descricoes = {redacao.get("descricao-do-perfil") or p["description"] for p in perfis}

    def quadro_de_vagas(cc):
        secao(cc, "vagas")
        unico = len(com_vaga) == len(perfis)
        if unico:
            linhas = []
            for p in perfis:
                v = vagas_por_codigo(p)
                linhas.append(
                    [p["code"], *([] if "name" in comuns else [p["name"]]), p["locality"],
                     str(v.get(ampla["code"], 0)), *[str(v.get(m["code"], 0)) for m in listas], str(p["immediateVacancies"])]
                )
            fixas = 2 if "name" in comuns else 3
            soma = ["Total", *[""] * (fixas - 1), *[str(sum(int(l[i]) for l in linhas)) for i in range(fixas, len(linhas[0]))]]
            tabela(
                cc,
                tabelas.legenda("Vagas por Perfil e lista de concorrência"),
                ["Código", *([] if "name" in comuns else ["Perfil"]), "Localidade", "Ampla concorrência", *[m["code"] for m in listas], "Total"],
                linhas,
                alinhamentos=[CENTRO, *[ESQUERDA] * (fixas - 1), *[CENTRO] * (len(listas) + 2)],
                rodape=soma,
            )
        else:
            # Perfis do mesmo nome numa tabela própria, com o nome na legenda: dezesseis linhas
            # repetindo "Tutor presencial" eram o que fazia a tabela ocupar duas páginas.
            paragrafo(cc, f"São {total} vagas imediatas, nos Perfis {codigos(com_vaga)}. Os demais formam cadastro de reserva.", antes=4)
            grupos = agrupar(perfis, lambda p: p["name"])
            avulsos = [g[0] for g in grupos if len(g) == 1]
            if avulsos:
                tabela(
                    cc,
                    tabelas.legenda("Perfis"),
                    ["Código", "Perfil", "Localidade", "Vagas imediatas"],
                    [[p["code"], p["name"], p["locality"], str(p["immediateVacancies"])] for p in avulsos],
                    alinhamentos=[CENTRO, ESQUERDA, ESQUERDA, CENTRO],
                )
            for grupo in (g for g in grupos if len(g) > 1):
                tabela(
                    cc,
                    tabelas.legenda(f"{grupo[0]['name']} — Perfis {codigos(grupo)}"),
                    ["Código", "Localidade", "Vagas imediatas"],
                    [[p["code"], p["locality"], str(p["immediateVacancies"])] for p in grupo],
                    alinhamentos=[CENTRO, ESQUERDA, CENTRO],
                )


    def atributos_comuns(cc):
        partes = []
        if "name" in comuns:
            descricao = descricoes.pop() if len(descricoes) == 1 else ""
            partes.append(
                comuns["name"] + (f" — {descricao[0].lower()}{descricao[1:].rstrip('.')}" if descricao else "")
            )
        if "workload" in comuns:
            partes.append(f"carga horária de {comuns['workload']}")
        if "compensation" in comuns:
            partes.append(f"remuneração: {comuns['compensation'][0].lower()}{comuns['compensation'][1:]}")
        if "reserveType" in comuns:
            partes.append(
                {
                    "NONE": "não há cadastro de reserva",
                    "LIMITED": f"cadastro de reserva de até {por_extenso(comuns.get('reserveLimit'))} classificados por Perfil",
                    "UNLIMITED": "cadastro de reserva sem limite de classificados",
                }[comuns["reserveType"]]
            )
        if partes:
            cc.escrever("Em todos os Perfis: " + "; ".join(partes) + ".", antes=8, justificar=True)

    def reserva(cc):
        if len(com_vaga) != len(perfis):
            linhas = []
            for p in com_vaga:
                v = vagas_por_codigo(p)
                linhas.append([p["code"], str(v.get(ampla["code"], 0)), *[str(v.get(m["code"], 0)) for m in listas], str(p["immediateVacancies"])])
            tabela(
                cc,
                tabelas.legenda("Vagas imediatas por lista de concorrência"),
                ["Código", "Ampla concorrência", *[m["code"] for m in listas], "Total"],
                linhas,
                alinhamentos=[CENTRO] * (len(listas) + 3),
            )
        tabela(
            cc,
            tabelas.legenda("Reserva de vagas"),
            ["Lista", "Percentual", "Fundamento"],
            [
                [
                    f"{m['code']} — {m['name']}",
                    f"{float(m['normativeRule']['percentage']):g}%" if (m.get("normativeRule") or {}).get("percentage") else "—",
                    (m.get("normativeRule") or {}).get("foundation") or "—",
                ]
                for m in listas
            ],
            alinhamentos=[ESQUERDA, CENTRO, ESQUERDA],
        )
        especies = {p["vacancyReversion"]["kind"] for p in com_vaga if p.get("vacancyReversion")}
        if len(especies) == 1:
            frase = REVERSAO[especies.pop()]
            if len(com_vaga) != len(perfis):
                frase = frase.replace("de um código", f"de um código com vagas imediatas ({codigos(com_vaga)})")
            paragrafo(cc, frase, antes=8)

    def vagas(cc):
        quadro_de_vagas(cc)
        atributos_comuns(cc)
        coeso(cc, reserva)

    vagas(c)

    grupos_de_atribuicoes = agrupar(perfis, lambda p: linhas_de(p.get("duties")))
    if any(linhas_de(p.get("duties")) for p in perfis):
        subsecao(c, f"{numero['vagas']}.1 Atribuições")
        for grupo in grupos_de_atribuicoes:
            def atribuicoes(cc, grupo=grupo):
                rotulo_de_grupo(cc, rotulo_do_grupo(grupo, len(perfis)) + ":")
                for linha in linhas_de(grupo[0].get("duties")):
                    item(cc, "•", linha)
            coeso(c, atribuicoes)

    # Cronograma, logo depois das vagas (art. 5º, X): "Quando" numa coluna, com "de … a …".
    def cronograma(cc):
        secao(cc, "cronograma")
        tem_local = any((e.get("location") or "").strip() for e in s["schedule"])
        tabela(
            cc,
            tabelas.legenda("Cronograma"),
            ["Nº", "O que acontece", "Quando", *(["Onde"] if tem_local else [])],
            [
                [str(e["order"]), e["description"], periodo(e["startAt"], e.get("endAt")), *([e.get("location") or "—"] if tem_local else [])]
                for e in s["schedule"]
            ],
            alinhamentos=[CENTRO, ESQUERDA, ESQUERDA, ESQUERDA][: 4 if tem_local else 3],
        )
    coeso(c, cronograma)

    # Inscrição: o período (do Evento marcado), os dados declarados e o teto são gerados.
    fatos = {}
    for p in perfis:
        for f in p.get("declaredFacts") or []:
            fatos[f["id"]] = f
    grupos_de_fatos = agrupar(perfis, lambda p: [(f["code"], f["label"], f["type"]) for f in p.get("declaredFacts") or []])

    def inscricao(cc):
        secao(cc, "inscricao")
        primeira, *demais = redigido("inscricao")
        paragrafo(cc, primeira)
        if inscricoes:
            paragrafo(cc, f"Período de inscrições: {periodo(inscricoes['startAt'], inscricoes['endAt'])} (Cronograma, nº {inscricoes['order']}).")
        for t in demais:
            paragrafo(cc, t)
        if len(grupos_de_fatos) == 1 and grupos_de_fatos[0][0].get("declaredFacts"):
            paragrafo(cc, "Na inscrição, informe também:")
            declarados = grupos_de_fatos[0][0]["declaredFacts"]
            for indice, f in enumerate(declarados):
                rotulo = f["label"]
                fim = "." if indice == len(declarados) - 1 else ";"
                item(cc, "•", f"{'a' if f['type'] == 'DATA' else 'o número de'} {rotulo[0].lower()}{rotulo[1:]}{fim}")
            paragrafo(cc, f"Esses dados são usados no desempate (item {numero['selecao']}.1).", antes=3)
        if s.get("maxInscricoesPorCandidato"):
            paragrafo(cc, f"Cada candidato pode enviar apenas {por_extenso(s['maxInscricoesPorCandidato']).replace('1 (um)', '1 (uma)')} inscrição neste Edital.")
    coeso(c, inscricao)
    if redacao.get("atendimento-pcd"):
        def atendimento(cc):
            subsecao(cc, f"{numero['inscricao']}.1 Atendimento especializado")
            for t in redigido("atendimento-pcd"):
                paragrafo(cc, t)
        coeso(c, atendimento)

    # Documentos por destinatário, com a remissão ao Requerimento (ED-18).
    if "documentos" in numero:
        def documentos(cc):
            secao(cc, "documentos")
            grupos = [("De todos os candidatos:", [d for d in s["documentRequirements"] if not d["modalityCode"] and not d["profileId"]])]
            for p in perfis:
                docs = [d for d in s["documentRequirements"] if d["profileId"] == p["id"]]
                if docs:
                    grupos.append((f"Também, de quem concorre ao Perfil {p['code']} — {p['name']}:", docs))
            for m in listas:
                docs = [d for d in s["documentRequirements"] if d["modalityCode"] == m["code"]]
                if docs:
                    grupos.append((f"Também, de quem concorre às vagas para {m['name'][0].lower()}{m['name'][1:]} ({m['code']}):", docs))
            for titulo, docs in grupos:
                if not docs:
                    continue
                rotulo_de_grupo(cc, titulo)
                for letra, d in zip("abcdefghijklmnop", docs):
                    texto = d["name"] + ("" if d["required"] else " (facultativo)")
                    if d["instructions"]:
                        texto += f" — {d['instructions'][0].lower()}{d['instructions'][1:]}"
                    item(cc, f"{letra})", texto)
            if tem_requerimento:
                paragrafo(cc, f"Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item {numero['matricula']}).")
        coeso(c, documentos)

    # Seleção: a regra que hoje está em quatro lugares, numa seção.
    def selecao_intro(cc):
        secao(cc, "selecao")
        for t in redigido("classificacao"):
            paragrafo(cc, t)
    coeso(c, selecao_intro)

    sem_cadastro = all(p["reserveType"] == "NONE" for p in perfis)
    grupos_de_marcos = agrupar(
        perfis,
        lambda p: [json.dumps(frases_do_marco(s, m, etapas, fatos, sem_cadastro), ensure_ascii=False) for m in p.get("classificationMilestones") or []],
    )
    # Partilha parcial (§6.3 do relatório): o que é igual em todos os grupos sai uma vez, e cada
    # grupo traz só o que é dele. Comparar é por frase impressa, nunca por semelhança.
    def escrever_frases(cc, frases):
        for frase in frases:
            if isinstance(frase, (tuple, list)) and frase[0] == "unidade":
                for parte in frase[1]:
                    item(cc, "•", parte)
            elif isinstance(frase, (tuple, list)):
                paragrafo(cc, "Critérios de desempate, nesta ordem:", antes=4)
                for parte in frase[1]:
                    item(cc, parte.split(" ", 1)[0], parte.split(" ", 1)[1] + ".")
            else:
                item(cc, "•", frase)

    def chave(frase):
        return json.dumps(frase, ensure_ascii=False)

    por_grupo = [
        [f for m in grupo[0].get("classificationMilestones") or [] for f in frases_do_marco(s, m, etapas, fatos, sem_cadastro)]
        for grupo in grupos_de_marcos
    ]
    comuns_a_todos = [f for f in por_grupo[0] if all(chave(f) in map(chave, outras) for outras in por_grupo[1:])]
    forma = {m["orderProduction"] for ms in marcos_por_perfil for m in ms}
    titulo_da_ordem = "Sorteio" if forma == {"POR_SORTEIO"} else "Classificação"

    def classificacao_comum(cc):
        subsecao(cc, f"{numero['selecao']}.1 {titulo_da_ordem}")
        paragrafo(
            cc,
            "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria "
            "classificação e o seu próprio resultado.",
        )
        if len(grupos_de_marcos) > 1:
            paragrafo(cc, "Para todos os Perfis:", antes=4)
        escrever_frases(cc, comuns_a_todos)
    coeso(c, classificacao_comum)
    if len(grupos_de_marcos) > 1:
        for grupo, frases in zip(grupos_de_marcos, por_grupo):
            proprias = [f for f in frases if chave(f) not in map(chave, comuns_a_todos)]
            def classificacao_do_grupo(cc, grupo=grupo, proprias=proprias):
                rotulo_de_grupo(cc, rotulo_do_grupo(grupo, len(perfis)) + ":")
                escrever_frases(cc, proprias)
            coeso(c, classificacao_do_grupo)

    proxima = 2
    metodo = s.get("drawMethod")
    if sorteio and metodo:
        def dados_do_sorteio(cc):
            with cc.bloco(moldura=True, coeso=True):
                subsecao(cc, f"{numero['selecao']}.{proxima} Dados para conferir o sorteio")
                paragrafo(
                    cc,
                    f"A ordem será definida a partir do resultado do {metodo['occurrence']} da {metodo['source']}, de "
                    f"{pdf._instante(metodo['occurrenceAt'])}. Com os dados abaixo, qualquer pessoa pode refazer o sorteio e "
                    "conferir o resultado.",
                )
                for rotulo, valor in (
                    ("Método", f"comum a este Edital; algoritmo {metodo['algorithm']}."),
                    ("Qual concurso", metodo["derivation"]),
                    ("Semente", "o número usado no sorteio: " + metodo["normalization"]["text"][0].lower() + metodo["normalization"]["text"][1:]),
                    ("Se faltar", metodo["substitutionRule"]["text"]),
                ):
                    rotulo_e_valor(cc, rotulo, valor, coluna=82)
                cc.espaco(4)
        coeso(c, dados_do_sorteio)
        proxima += 1

    for etapa in sorted(s["stages"], key=lambda e: e["order"]):
        evento = next((e for e in s["schedule"] if e["id"] == etapa.get("scheduleEventId")), None)

        def compor_etapa(cc, etapa=etapa, evento=evento, sub=proxima):
            subsecao(cc, f"{numero['selecao']}.{sub} {etapa['name']}")
            if etapa["forma"] == "DECISORIA":
                frase = f"Etapa eliminatória: o resultado é “{etapa['rotuloFavoravel']}” ou “{etapa['rotuloDesfavoravel']}”."
            else:
                carater = " e ".join(n for k, n in (("eliminatory", "eliminatória"), ("classificatory", "classificatória")) if etapa.get(k))
                frase = f"Etapa {carater}, com pontuação máxima de {pdf.humano.decimal(etapa['maximumScore'])}"
                if etapa.get("minimumScore"):
                    frase += f" e nota mínima de {pdf.humano.decimal(etapa['minimumScore'])}"
                frase += f" e peso {pdf.humano.decimal(etapa['weight'])}."
                if etapa.get("evaluationsPerRegistration"):
                    n = etapa["evaluationsPerRegistration"]
                    frase += f" Cada inscrição recebe {por_extenso(n).replace('1 (um)', '1 (uma)')} avaliação."
            if evento:
                frase += f" Será feita {periodo(evento['startAt'], evento.get('endAt'))}."
            paragrafo(cc, frase)
        coeso(c, compor_etapa)
        proxima += 1

    if redacao.get("verificacao-autodeclaracao"):
        def verificacao(cc, sub=proxima):
            subsecao(cc, f"{numero['selecao']}.{sub} Verificação da autodeclaração")
            for t in redigido("verificacao-autodeclaracao"):
                paragrafo(cc, t)
        coeso(c, verificacao)

    # Recursos: a frase do marco vem para a seção que trata de recurso.
    def recursos(cc):
        secao(cc, "recursos")
        vistas = []
        for grupo in grupos_de_marcos:
            for marco in grupo[0].get("classificationMilestones") or []:
                frase = frase_do_recurso(marco)
                if frase and frase not in vistas:
                    vistas.append(frase)
                    rotulo = "" if len(grupos_de_marcos) == 1 else f"{rotulo_do_grupo(grupo, len(perfis))} — "
                    paragrafo(cc, rotulo + (frase[0].lower() + frase[1:] if rotulo else frase))
        for t in redigido("recursos"):
            paragrafo(cc, t)
    coeso(c, recursos)

    def convocacao(cc):
        secao(cc, "convocacao")
        formas = {p["callForm"] for p in perfis}
        if len(formas) == 1:
            paragrafo(cc, CONVOCACAO[formas.pop()])
        for t in redigido("convocacao"):
            paragrafo(cc, t)
    coeso(c, convocacao)

    if "matricula" in numero:
        def matricula(cc):
            secao(cc, "matricula")
            for t in redigido("matricula"):
                paragrafo(cc, t)
            if tem_requerimento:
                paragrafo(cc, "O Requerimento de Matrícula é enviado no ato da inscrição. Ao enviá-lo, o candidato declara:")
                with cc.bloco(moldura=True, coeso=True):
                    cc.escrever(s["matriculationRequest"]["declarationText"], recuo=8, antes=8, justificar=True)
                    cc.espaco(2)
        coeso(c, matricula)

    for chave in ("certificado", "prazo-de-validade"):
        if chave in numero:
            textual(chave)

    if "anexos" in numero:
        def anexos(cc):
            secao(cc, "anexos")
            for anexo in s["attachments"]:
                item(cc, "•", anexo["label"])
        coeso(c, anexos)
    # A última seção e o fecho não se separam: uma página só com local, data e autoridade é o
    # defeito que a primeira versão da amostra mostrou.
    with c.bloco(coeso=True):
        if "disposicoes-finais" in numero:
            secao(c, "disposicoes-finais")
            for t in redigido("disposicoes-finais"):
                paragrafo(c, t)
        pdf._autoridade(c, autoridade, DATA_DO_ATO, UNIDADE.local)
        c.espaco(pdf.ANTES_DE_SECAO)
        c.regua()
        c.escrever(
            "Autenticidade — este documento corresponde integralmente à versão homologada do Edital identificada abaixo.",
            tamanho=CORPO_NOTA,
            antes=6,
        )
        c.escrever(
            f"Edital {s['number']}/{s['year']} · Processo Seletivo {s['processoCode']} — {s['processoTitle']}",
            tamanho=CORPO_NOTA,
        )
        c.escrever(f"SHA-256 do conteúdo: {hash_}", tamanho=CORPO_NOTA)
    return c


# ---------------------------------------------------------------------------------------------
# O arquivo (E1, E4, E5)
# ---------------------------------------------------------------------------------------------
CINZA_DA_CAIXA = "0.95"


def onde(paginas, alvo, *, contem=False):
    for numero, (linhas, _) in enumerate(paginas, 1):
        for texto, fonte, tamanho, x, y, _ in linhas:
            if (alvo in texto) if contem else (texto == alvo):
                return numero, x, y, texto, tamanho
    return None


def _utf16(texto):
    return b"<FEFF" + texto.encode("utf-16-be").hex().upper().encode() + b">"


def arquivo(c, titulos, titulo, identificacao, fontes, uris):
    paginas = c.paginar()
    total = len(paginas)
    fluxos = []
    for numero, (linhas, tracos) in enumerate(paginas, 1):
        caixas = [t for t in tracos if t[0] == "ret" and t[1] < MARGEM]
        fundo = b"".join(
            f"{CINZA_DA_CAIXA} g {x:.1f} {y:.1f} {w:.1f} {h:.1f} re f 0 g\n".encode() for _, x, y, w, h in caixas
        )
        fluxos.append(
            fundo
            + pdf._fluxo_da_pagina(
                linhas, identificacao, f"Página {numero} de {total}", tracos=tracos, com_brasao=numero == 1, estrito=True
            )
        )

    # 1 catálogo, 2 páginas, 3–4 fontes base-14 (ou referências), 5 brasão, 6 info, 7 marcadores.
    objetos_das_fontes, ids_das_fontes = ([], {})
    primeiro_livre = 8
    if fontes:
        objetos_das_fontes, ids_das_fontes = fontes.objetos(primeiro_livre)
        primeiro_livre += len(objetos_das_fontes)
    ids = [primeiro_livre + i * 2 for i in range(total)]
    proximo = primeiro_livre + total * 2

    marcadores = []
    for nivel, texto in titulos.itens:
        achado = onde(paginas, texto)
        if achado:
            marcadores.append((nivel, texto, achado[0], achado[2] + 14))
    ids_dos_marcadores = list(range(proximo, proximo + len(marcadores)))
    proximo += len(marcadores)

    anotacoes = {n: [] for n in range(1, total + 1)}
    for _, texto in titulos.sumario:
        destino = onde(paginas, texto)
        for numero, (linhas, _) in enumerate(paginas, 1):
            for t, fonte, tamanho, x, y, _ in linhas:
                if t.startswith(texto + " .") and destino:
                    anotacoes[numero].append(
                        f"<< /Type /Annot /Subtype /Link /Border [0 0 0] /Rect [{x:.1f} {y - 2:.1f} "
                        f"{LARGURA - MARGEM:.1f} {y + tamanho:.1f}] /Dest [{ids[destino[0] - 1]} 0 R "
                        f"/XYZ 0 {destino[2] + 16:.1f} null] >>".encode()
                    )
    for alvo, uri in uris:
        for numero, (linhas, _) in enumerate(paginas, 1):
            for texto, fonte, tamanho, x, y, _ in linhas:
                if alvo in texto:
                    inicio = x + pdf.largura(texto[: texto.index(alvo)], tamanho, fonte)
                    fim = inicio + pdf.largura(alvo, tamanho, fonte)
                    anotacoes[numero].append(
                        f"<< /Type /Annot /Subtype /Link /Border [0 0 0] /Rect [{inicio:.1f} {y - 2:.1f} "
                        f"{fim:.1f} {y + tamanho:.1f}] /A << /S /URI /URI (".encode()
                        + pdf._texto_pdf(uri)
                        + b") >> >>"
                    )
    ids_das_anotacoes, corpos = {}, []
    for numero in range(1, total + 1):
        ids_das_anotacoes[numero] = []
        for anotacao in anotacoes[numero]:
            ids_das_anotacoes[numero].append(proximo)
            corpos.append(anotacao)
            proximo += 1

    # 3 e 4 continuam sendo as base-14; com a fonte embutida as páginas apontam para os objetos
    # dela, e estes ficam sem uso — o preço de manter a numeração fixa do escritor de hoje.
    fonte_regular = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R /Lang (pt-BR) /Outlines 7 0 R /PageMode /UseOutlines "
        b"/ViewerPreferences << /DisplayDocTitle true >> >>",
        b"<< /Type /Pages /Kids [" + b" ".join(f"{i} 0 R".encode() for i in ids) + f"] /Count {total} >>".encode(),
        fonte_regular,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        (
            f"<< /Type /XObject /Subtype /Image /Width {brasao.LARGURA} /Height {brasao.ALTURA} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(brasao.FLUXO)} "
            ">>\nstream\n".encode()
            + brasao.FLUXO
            + b"\nendstream"
        ),
        b"<< /Title " + _utf16(titulo) + b" /Author " + _utf16("Cefor/Ifes") + b" >>",
    ]
    pais, filhos, ultimo = {}, {}, None
    for indice, (nivel, *_r) in enumerate(marcadores):
        pais[indice] = None if nivel == 1 else ultimo
        if nivel == 1:
            ultimo = indice
        filhos.setdefault(pais[indice], []).append(indice)
    raiz = filhos.get(None, [])
    objetos.append(
        f"<< /Type /Outlines /First {ids_dos_marcadores[raiz[0]]} 0 R /Last {ids_dos_marcadores[raiz[-1]]} 0 R "
        f"/Count {len(raiz)} >>".encode()
    )
    objetos.extend(objetos_das_fontes)
    f1 = f"{ids_das_fontes[REGULAR]} 0 R" if fontes else "3 0 R"
    f2 = f"{ids_das_fontes[NEGRITO]} 0 R" if fontes else "4 0 R"
    for indice, numero in enumerate(ids):
        anot = ids_das_anotacoes[indice + 1]
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {pdf.ALTURA}] ".encode()
            + f"/Resources << /Font << /F1 {f1} /F2 {f2} >> ".encode()
            + f"/XObject << /{pdf.NOME_DO_BRASAO} 5 0 R >> >> ".encode()
            + (f"/Annots [{' '.join(f'{a} 0 R' for a in anot)}] ".encode() if anot else b"")
            + f"/Contents {numero + 1} 0 R >>".encode()
        )
        comprimido = zlib.compress(fluxos[indice], 9)
        objetos.append(b"<< /Length " + str(len(comprimido)).encode() + b" /Filter /FlateDecode >>\nstream\n" + comprimido + b"\nendstream")
    for indice, (nivel, texto, pagina, y) in enumerate(marcadores):
        irmaos = filhos[pais[indice]]
        posicao = irmaos.index(indice)
        pai = ids_dos_marcadores[pais[indice]] if pais[indice] is not None else 7
        partes = [b"<< /Title " + _utf16(texto), f" /Parent {pai} 0 R /Dest [{ids[pagina - 1]} 0 R /XYZ 0 {y:.1f} null]".encode()]
        if posicao > 0:
            partes.append(f" /Prev {ids_dos_marcadores[irmaos[posicao - 1]]} 0 R".encode())
        if posicao < len(irmaos) - 1:
            partes.append(f" /Next {ids_dos_marcadores[irmaos[posicao + 1]]} 0 R".encode())
        if indice in filhos:
            partes.append(
                f" /First {ids_dos_marcadores[filhos[indice][0]]} 0 R /Last {ids_dos_marcadores[filhos[indice][-1]]} 0 R "
                f"/Count -{len(filhos[indice])}".encode()
            )
        objetos.append(b"".join(partes) + b" >>")
    objetos.extend(corpos)

    saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    deslocamentos = []
    for indice, objeto in enumerate(objetos, 1):
        deslocamentos.append(len(saida))
        saida.extend(f"{indice} 0 obj\n".encode() + objeto + b"\nendobj\n")
    xref = len(saida)
    saida.extend(f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode())
    for deslocamento in deslocamentos:
        saida.extend(f"{deslocamento:010d} 00000 n \n".encode())
    saida.extend(f"trailer << /Size {len(objetos) + 1} /Root 1 0 R /Info 6 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(saida), total


def principal(argumentos):
    cenario, saida = argumentos[0], argumentos[1]
    fontes = None
    if "--fontes" in argumentos:
        fontes = Fontes(argumentos[argumentos.index("--fontes") + 1])
        # E6: o compositor passa a medir com as larguras da fonte que o arquivo embute.
        pdf.largura = fontes.largura
    dados = CENARIOS[cenario]
    envelope = json.loads((RAIZ / dados["snapshot"]).read_text())
    s = pdf._grafado(envelope["content"], previa=False)
    if "--variante-marcos" in argumentos:
        # Variante **declarada**, só para testar a forma: os Perfis a distância passam a ter corte e
        # prazo de recurso próprios. Não é o cenário da auditoria, e o hash impresso deixa de
        # corresponder ao conteúdo — o documento sai marcado como variante no título do arquivo.
        for perfil in s["profiles"]:
            if perfil["code"].startswith("TD-"):
                for marco in perfil["classificationMilestones"]:
                    marco["cutRule"]["targetCount"] = 3
                    marco["appealWindow"]["durationDays"] = 5
        dados = {**dados, "titulo": dados["titulo"] + " — VARIANTE DE TESTE"}
    hash_ = envelope["hash"]

    titulos = Titulos()
    compor(s, dados["redacao"], dados["autoridade"], titulos, hash_)
    titulos.sumario = [(n, t) for n, t in titulos.itens if n == 1]
    for _ in range(3):
        rascunho = compor(s, dados["redacao"], dados["autoridade"], titulos, hash_)
        paginas = rascunho.paginar()
        titulos.paginas = {t: achado[0] for _, t in titulos.sumario if (achado := onde(paginas, t))}
    final = compor(s, dados["redacao"], dados["autoridade"], titulos, hash_)
    emails = sorted(set(re.findall(r"[\w.]+@[\w.]+\w", json.dumps(dados["redacao"], ensure_ascii=False))))
    uris = [(e, f"mailto:{e}") for e in emails]
    endereco = ENDERECO.format(numero=s["number"], ano=s["year"])
    uris.append((endereco, endereco))
    conteudo, total = arquivo(
        final,
        titulos,
        dados["titulo"],
        f"Edital {s['number']}/{s['year']} · Verificação {hash_[:16]}…",
        fontes,
        uris,
    )
    Path(saida).write_bytes(conteudo)
    print(saida, total, "páginas", "(fonte embutida)" if fontes else "(Helvetica não embutida)")


if __name__ == "__main__":
    principal(sys.argv[1:])
