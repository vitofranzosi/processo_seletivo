"""A composição do Centro de Controle do Edital — protótipo do estudo de 2026-11-09 (versão 2).

**Leitura de leitura.** Nada aqui deriva fato novo do banco. A entrada é o `Andamento` que a `127`
já monta (`interface/andamento.do_edital`), com as sete situações por ponto e por lista. Esta
camada só **agrupa** os pontos em macrofases e **agrega** as situações, por regras fixas e puras.

**Duas leituras separadas** (refinamento de 09/11). A primeira versão dava a cada fase uma situação
só — "ação disponível", "aguardando", "em andamento" —, misturando duas perguntas:

- **em que ponto a fase está** (o andamento: ainda não, em curso, concluída);
- **o que ela oferece agora, e a quem** (as providências: suas, de outro papel, em espera,
  impedidas).

Uma fase pode estar em curso, com uma lista concluída, e ainda assim oferecer duas ações — uma sua,
outra de outro papel. As duas leituras agora são dados diferentes, e a tela as desenha diferente.

**O que a macrofase é, e o que ela não é.** É um rótulo de apresentação para um conjunto de pontos
que a derivação já conhece. Não é coluna nem estado persistido, e o Edital não tem "a" macrofase
atual: várias podem estar em curso ao mesmo tempo.

As frases pedagógicas (`CONCEITOS`) são texto de protótipo, conferido contra os guias de
`doc/guia-jornada-do-sorteio-2026-11-05/` e `doc/gps-por-dentro/`. Não são regra.
"""

from dataclasses import dataclass, field

from processo_seletivo.interface import andamento as a

# ---------------------------------------------------------------------------------------------
# As macrofases, em três grupos
# ---------------------------------------------------------------------------------------------

PUBLICACAO, INSCRICOES, AVALIACAO, CLASSIFICACAO = (
    "publicacao",
    "inscricoes",
    "avaliacao",
    "classificacao",
)
RESULTADO, VAGAS, CONVOCACAO, CONCLUSAO = "resultado", "vagas", "convocacao", "conclusao"

#: (chave, nome, pergunta que a macrofase responde, escopo)
MACROFASES = (
    (PUBLICACAO, "Edital", "O Edital está publicado e vigente?", "Edital"),
    (INSCRICOES, "Inscrições", "Quem se inscreveu, e o período acabou?", "Edital"),
    (AVALIACAO, "Avaliação", "As Etapas foram avaliadas e consolidadas?", "Perfil"),
    (CLASSIFICACAO, "Classificação", "Em que ordem cada lista ficou?", "lista"),
    (RESULTADO, "Resultado e recursos", "O resultado foi divulgado, e cabe recurso?", "lista"),
    (VAGAS, "Vagas", "Quem a lista alcança, e que vaga cada um ocupa?", "lista"),
    (CONVOCACAO, "Convocação", "Quem foi chamado, entregou e foi conferido?", "lista"),
    (CONCLUSAO, "Conclusão", "Tudo tem desfecho, e o Edital pode ser encerrado?", "Edital"),
)
#: Os grupos só orientam a leitura do mapa; não mudam nenhuma regra.
GRUPOS = (
    ("Abertura", (PUBLICACAO, INSCRICOES)),
    ("Seleção", (AVALIACAO, CLASSIFICACAO, RESULTADO, VAGAS)),
    ("Ocupação", (CONVOCACAO, CONCLUSAO)),
)
NOMES = {chave: nome for chave, nome, _, _ in MACROFASES}
POR_LISTA = (AVALIACAO, CLASSIFICACAO, RESULTADO, VAGAS, CONVOCACAO)

_DO_TIPO = {
    a.RELACAO: CLASSIFICACAO,
    a.SEMENTE: CLASSIFICACAO,
    a.SORTEIO: CLASSIFICACAO,
    a.ORDEM: CLASSIFICACAO,
    a.CORTE: VAGAS,
    a.APURACAO: VAGAS,
    a.RESULTADO: RESULTADO,
    a.CONVOCACAO: CONVOCACAO,
}
_DA_NATUREZA = {
    **_DO_TIPO,
    a.DISTRIBUIR: AVALIACAO,
    a.AVALIAR: AVALIACAO,
    a.CONSOLIDAR: AVALIACAO,
    a.REAVALIAR: AVALIACAO,
    a.ETAPA: AVALIACAO,
    a.CONFERIR: CONVOCACAO,
    a.RECURSO: RESULTADO,
}
_DA_ETAPA = (a.DISTRIBUIR, a.AVALIAR, a.CONSOLIDAR, a.REAVALIAR, a.ETAPA)


def macrofase_do_ponto(ponto):
    if ponto.tipo == a.ETAPA:
        # A Etapa governada pela faixa (a documental, quase sempre) corre entre o corte e a
        # apuração (D-014 da 127): para quem conduz, é parte de "quem ocupa as vagas".
        return VAGAS if ponto.grupo == a.GRUPO_DA_GOVERNADA else AVALIACAO
    return _DO_TIPO.get(ponto.tipo, CLASSIFICACAO)


# ---------------------------------------------------------------------------------------------
# Primeira leitura: o andamento da fase
# ---------------------------------------------------------------------------------------------

CONCLUIDA, EM_CURSO, NAO_INICIADA, NAO_SE_APLICA = (
    "concluida",
    "em_curso",
    "nao_iniciada",
    "nao_se_aplica",
)
ROTULOS = {
    CONCLUIDA: "Concluída",
    EM_CURSO: "Em curso",
    NAO_INICIADA: "Ainda não começou",
    NAO_SE_APLICA: "Não se aplica",
}
SINAIS = {CONCLUIDA: "✓", EM_CURSO: "◐", NAO_INICIADA: "○", NAO_SE_APLICA: "—"}
_PESO = (EM_CURSO, NAO_INICIADA, CONCLUIDA, NAO_SE_APLICA)


def agregar(celulas):
    """O andamento de um grupo de células — de uma macrofase numa lista.

    Puro e fixo: tudo feito → *concluída*; só *Depois* → *ainda não começou*; o resto (algo feito,
    ou algo em aberto) → *em curso*. **Não diz se há o que fazer**: isso é a segunda leitura, das
    providências. A ausência de ato nunca é pendência (D-007 da 127).
    """
    s = [c.situacao for c in celulas if c is not None]
    if not s:
        return None
    if all(x in (a.FEITO, a.NAO_SE_APLICA) for x in s):
        return CONCLUIDA if a.FEITO in s else NAO_SE_APLICA
    if all(x in (a.DEPOIS, a.NAO_SE_APLICA) for x in s):
        return NAO_INICIADA
    return EM_CURSO


def juntar(situacoes):
    """O andamento de uma macrofase no Edital, a partir do andamento em cada lista."""
    s = [x for x in situacoes if x is not None and x != NAO_SE_APLICA]
    if not s:
        return NAO_SE_APLICA if situacoes else None
    if all(x == CONCLUIDA for x in s):
        return CONCLUIDA
    if all(x == NAO_INICIADA for x in s):
        return NAO_INICIADA
    # Uma lista concluída ao lado de outra que não começou é andamento, e não "ainda não".
    return EM_CURSO


# ---------------------------------------------------------------------------------------------
# A linguagem: o que o operador faz, antes do termo técnico
# ---------------------------------------------------------------------------------------------

#: `{tipo do ponto ou natureza: {...}}`. `simples` é o nome do passo na língua de quem conduz;
#: `termo` é o nome no GPS; `curta` fica sempre visível; `porque` e `ao_confirmar`, sob demanda.
CONCEITOS = {
    a.RELACAO: {
        "simples": "Fixar os participantes",
        "termo": "congelar a relação",
        "curta": "Publica, para cada lista, quem participa do sorteio e com que número — e isso "
        "não muda mais.",
        "porque": "Encerrar as inscrições impede que entre gente nova; fixar a lista antes de a "
        "semente existir impede que alguém a monte já sabendo o resultado.",
        "ao_confirmar": "Irreversível: corrigir exige Retificação e uma relação nova. Fixe todas as "
        "listas do marco antes de obter a semente — depois dela, a relação é recusada.",
    },
    a.SEMENTE: {
        "simples": "Obter a semente pública",
        "termo": "observar a extração",
        "curta": "Registra os números da extração declarada no Edital (a Loteria Federal, no "
        "certame real). Uma só semente vale para todas as listas.",
        "porque": "Ninguém escolhe a semente: ela vem de uma fonte pública, depois que os "
        "participantes estão fixados. É o que torna o sorteio verificável.",
        "ao_confirmar": "Com a Loteria Federal, só depois da data da extração. Se a fonte não "
        "responde, nada é gravado e se tenta de novo; não se digitam números à mão.",
    },
    a.SORTEIO: {
        "simples": "Realizar o sorteio",
        "termo": "sorteio",
        "curta": "Aplica a semente à lista fixada e produz a ordem dos participantes.",
        "porque": "A mesma lista e a mesma semente dão sempre a mesma ordem: qualquer pessoa pode "
        "reproduzir o resultado no canal público.",
        "ao_confirmar": "Grava a ordem da lista como ato imutável, com página de verificação.",
    },
    a.ORDEM: {
        "simples": "Classificar a lista",
        "termo": "emitir a ordem",
        "curta": "Grava a classificação da lista, pelas notas consolidadas, pesos e desempates do "
        "Edital.",
        "porque": "A ordem é a base do que vem depois: resultado, faixa de chamada, vagas e "
        "convocação a leem.",
        "ao_confirmar": "Irreversível. Se uma nota mudar (um recurso deferido, por exemplo), é "
        "preciso emitir uma ordem nova, com motivo. Numa lista sem inscritos, emitir declara que "
        "ninguém concorreu ali.",
    },
    a.CORTE: {
        "simples": "Definir até onde se chama",
        "termo": "emitir o corte",
        "curta": "Fixa até que posição de cada lista as pessoas seguem — para as vagas e para a "
        "reserva, se houver.",
        "porque": "Limita quem passa à análise de documentos e quem disputa as vagas.",
        "ao_confirmar": "Com o prazo de recurso aberto, a recomendação é esperar: um recurso "
        "deferido tornaria a faixa obsoleta.",
    },
    a.APURACAO: {
        "simples": "Distribuir as vagas entre as listas",
        "termo": "apurar a ocupação",
        "curta": "Cruza ampla concorrência e cotas e decide que vaga cada pessoa alcançada ocupa, "
        "sem contar ninguém duas vezes.",
        "porque": "Quem está bem colocado na ampla ocupa pela ampla, e a vaga da cota passa ao "
        "próximo da cota. A convocação chama quem a apuração indicou.",
        "ao_confirmar": "Uma desistência ou uma faixa nova tornam a apuração obsoleta, e ela é "
        "refeita.",
    },
    a.RESULTADO: {
        "simples": "Divulgar o resultado",
        "termo": "publicar resultado",
        "curta": "Torna a ordem pública: o preliminar abre o prazo de recurso; o definitivo vem "
        "depois do prazo e dos recursos.",
        "porque": "O definitivo não é pré-requisito da faixa, das vagas nem da convocação — mas um "
        "recurso deferido pode mudá-las.",
        "ao_confirmar": "Ato de quem publica resultados, com documento próprio.",
    },
    a.RECURSO: {
        "simples": "Decidir os recursos",
        "termo": "recursos",
        "curta": "Julga os pedidos de revisão feitos no prazo.",
        "porque": "Um recurso deferido pode mudar uma nota, e com ela a ordem, a faixa e as vagas.",
        "ao_confirmar": "A decisão é registrada e comunicada; a ordem afetada passa a pedir uma nova.",
    },
    a.CONVOCACAO: {
        "simples": "Convocar e decidir",
        "termo": "convocação",
        "curta": "Chama, com prazo, quem a apuração indicou, e acompanha cada chamada até o "
        "desfecho.",
        "porque": "É a passagem da classificação para a vaga ocupada. Quem não responde no prazo "
        "tem o não atendimento registrado, e a fila anda.",
        "ao_confirmar": "Convocação e comunicação são atos registrados. A matrícula acontece fora "
        "do GPS.",
    },
    a.CONFERIR: {
        "simples": "Conferir os documentos",
        "termo": "conferência documental",
        "curta": "Abre cada documento entregue e o marca como conforme ou pendente, com motivo.",
        "porque": "O GPS só aceita 'conforme' de quem abriu o arquivo. Com tudo conforme, "
        "registra-se o desfecho.",
        "ao_confirmar": "A pendência volta ao candidato, que pode reenviar no prazo.",
    },
    a.ETAPA: {
        "simples": "Avaliar a Etapa",
        "termo": "Etapa",
        "curta": "Distribui as inscrições a avaliadores, registra as avaliações e consolida.",
        "porque": "Só a Etapa consolidada alimenta a classificação.",
        "ao_confirmar": "Consolidar fecha os resultados; mudá-los depois é reavaliação, por "
        "recurso.",
    },
}
for _n in _DA_ETAPA:
    CONCEITOS.setdefault(_n, CONCEITOS[a.ETAPA])
#: As naturezas cujo nome no GPS é jargão: a providência mostra primeiro o nome simples.
JARGAO = frozenset({a.RELACAO, a.SEMENTE, a.ORDEM, a.CORTE, a.APURACAO})


def conceito(chave):
    return CONCEITOS.get(chave)


# ---------------------------------------------------------------------------------------------
# As estruturas
# ---------------------------------------------------------------------------------------------


@dataclass
class PassoDoRoteiro:
    simples: str
    termo: str
    curta: str
    situacao: str
    feitas: int
    total: int
    unico: bool
    tem_acao: bool = False
    porque: str = ""
    ao_confirmar: str = ""
    #: Por que o passo ainda não começou — a razão que a derivação já dá à célula *Depois*.
    razao: str = ""

    @property
    def sinal(self):
        return SINAIS.get(self.situacao, "")

    @property
    def rotulo(self):
        return ROTULOS.get(self.situacao, "")


@dataclass
class ItemDeProvidencia:
    p: object
    fase: str
    fase_chave: str
    conceito: dict | None
    paralela: str = ""
    #: O nome do ato na língua de quem conduz; o `p.ato` da 127 vira a linha "No GPS".
    titulo: str = ""
    no_gps: str = ""


@dataclass
class CelulaNaFase:
    ponto: str
    celula: object

    @property
    def ato(self):
        """O ato da célula na língua da coluna: "Classificar a lista", e não "Emitir a ordem"."""
        c = self.celula
        if c.natureza in JARGAO and c.natureza in CONCEITOS and c.situacao in a.A_PRATICAR:
            return CONCEITOS[c.natureza]["simples"]
        return c.ato


@dataclass
class ListaNaFase:
    rotulo: str
    situacao: str | None
    celulas: list


@dataclass
class Macrofase:
    chave: str
    nome: str
    pergunta: str
    escopo: str
    situacao: str | None
    resumo: str = ""
    nota: str = ""
    perfis: list = field(default_factory=list)  # [(perfil, [ListaNaFase], [PassoDoRoteiro])]
    providencias: list = field(default_factory=list)
    paralela: str = ""
    espera_ate: object = None

    @property
    def rotulo(self):
        return ROTULOS.get(self.situacao, "")

    @property
    def sinal(self):
        return SINAIS.get(self.situacao, "")

    @property
    def em_curso(self):
        return self.situacao == EM_CURSO

    # A segunda leitura: o que a fase oferece agora, e a quem.
    @property
    def suas(self):
        return [i for i in self.providencias if i.p.grupo == "sua"]

    @property
    def de_outros(self):
        return [i for i in self.providencias if i.p.grupo == "de_outro"]

    @property
    def aguardando(self):
        return [i for i in self.providencias if i.p.situacao == a.AGUARDA]

    @property
    def impedidas(self):
        return [i for i in self.providencias if i.p.situacao == a.IMPEDIDO]

    @property
    def parada(self):
        """Em curso, mas sem nada que alguém possa fazer agora: depende de outra fase."""
        return self.situacao == EM_CURSO and not self.providencias


@dataclass
class ListaNoCentro:
    rotulo: str
    curto: str
    fases: list  # [(chave, andamento)]
    concluida: bool
    atos: list = field(default_factory=list)  # [(fase, Celula, nome)] a praticar, um por fase
    espera: object = None  # a primeira célula em espera ou impedida, sem ato a praticar


@dataclass
class PerfilNoCentro:
    nome: str
    forma: str
    inscritos: int
    listas: list
    resumo: str
    matriz: object
    matricula_fora: bool


@dataclass
class Destaque:
    item: object
    porque: str
    destrava: list = field(default_factory=list)


@dataclass
class Centro:
    fases: list
    grupos: list
    perfis: list
    providencias: dict
    onde: str
    onde_detalhe: str
    em_curso: list
    destaque: object = None
    sem_destaque: str = ""
    alcance: str = ""
    ve_a_matriz: bool = False


# ---------------------------------------------------------------------------------------------
# A composição
# ---------------------------------------------------------------------------------------------


def _curto(rotulo):
    if rotulo.startswith("Ampla concorrência"):
        return "Ampla concorrência"
    if "(" in rotulo and rotulo.endswith(")"):
        return rotulo[rotulo.rfind("(") + 1 : -1]
    return rotulo


def _macrofase_da_providencia(prov, perfis):
    if prov.natureza in _DA_ETAPA:
        governadas = {
            p.titulo for pf in perfis for p in pf.pontos if p.grupo == a.GRUPO_DA_GOVERNADA
        }
        if any(nome in (prov.onde or "") for nome in governadas):
            return VAGAS
    return _DA_NATUREZA.get(prov.natureza, CLASSIFICACAO)


def _passo(ponto):
    """`(nome simples, termo, dados)` de um ponto da jornada."""
    dados = CONCEITOS.get(ponto.tipo) or CONCEITOS[a.ETAPA]
    if ponto.tipo == a.ETAPA:
        # A Etapa tem nome próprio no Edital ("Prova objetiva"), que é o nome que a pessoa conhece.
        return ponto.titulo, "Etapa", dados
    return dados["simples"], dados["termo"], dados


def _fase_edital_publicacao(edital, documentos, em_curso):
    retificacoes = sum(1 for d in documentos if d["retificacao_id"])
    if edital.status in ("PUBLICADO", "ENCERRADO"):
        situacao = CONCLUIDA
        resumo = "Publicado" + (
            f" · {retificacoes} Retificaç{'ão' if retificacoes == 1 else 'ões'}"
            if retificacoes
            else ""
        )
    elif edital.status == "CANCELADO":
        situacao, resumo = CONCLUIDA, "Cancelado"
    else:
        situacao, resumo = EM_CURSO, "Em elaboração"
    nota = ""
    if em_curso:
        nota = f"{len(em_curso)} Retificação em curso — ela pode mudar datas, vagas ou regras."
        situacao = EM_CURSO
    return situacao, resumo, nota


def _fase_inscricoes(inscricoes):
    from processo_seletivo.inscricoes.domain import periodo

    estado = inscricoes.get("estado")
    enviadas = inscricoes.get("enviadas") or 0
    quantas = f"{enviadas} inscriç{'ão' if enviadas == 1 else 'ões'}"
    if inscricoes.get("cancelado"):
        return CONCLUIDA, f"Período cancelado · {quantas}"
    if estado == periodo.ENCERRADO:
        return CONCLUIDA, f"{quantas} · encerradas"
    if estado == periodo.ABERTO:
        return EM_CURSO, f"Abertas · {quantas} até agora"
    if estado == periodo.FUTURO:
        return NAO_INICIADA, "Ainda não abertas"
    return NAO_INICIADA, "Período não designado"


def compor(edital, andamento, *, documentos, em_curso, alcance=None):
    perfis_c, fases_lista = [], {chave: [] for chave in POR_LISTA}
    for perfil in andamento.perfis:
        pontos_por_fase = {chave: [] for chave in POR_LISTA}
        for ponto in perfil.pontos:
            pontos_por_fase[macrofase_do_ponto(ponto)].append(ponto)
        detalhes = {chave: [] for chave in POR_LISTA}
        listas = []
        for lista_id, rotulo in perfil.listas:
            fases = []
            for chave in POR_LISTA:
                celulas = [p.celula(lista_id) for p in pontos_por_fase[chave]]
                andamento_da_lista = agregar(celulas)
                fases.append((chave, andamento_da_lista))
                detalhes[chave].append(
                    ListaNaFase(
                        _curto(rotulo),
                        andamento_da_lista,
                        [
                            CelulaNaFase(_passo(p)[0], p.celula(lista_id))
                            for p in pontos_por_fase[chave]
                            if p.celula(lista_id) is not None
                        ],
                    )
                )
            # "Agora nesta lista": os atos a praticar, um por fase, na ordem da jornada; sem eles,
            # a primeira espera ou impedimento (a preferência de `da_lista`, FR-4543 da 133).
            vistas, atos, espera = set(), [], None
            for ponto in perfil.pontos:
                c = ponto.celula(lista_id)
                if c is None:
                    continue
                fase_do_ponto = macrofase_do_ponto(ponto)
                if c.situacao in a.A_PRATICAR and fase_do_ponto not in vistas:
                    vistas.add(fase_do_ponto)
                    nome_do_ato = c.ato
                    if c.natureza in JARGAO and c.natureza in CONCEITOS:
                        nome_do_ato = CONCEITOS[c.natureza]["simples"]
                    atos.append((NOMES[fase_do_ponto], c, nome_do_ato))
                elif espera is None and c.situacao in (a.AGUARDA, a.IMPEDIDO):
                    espera = c
            concluida = all(s in (CONCLUIDA, NAO_SE_APLICA, None) for _, s in fases)
            listas.append(ListaNoCentro(rotulo, _curto(rotulo), fases, concluida, atos, espera))
        for chave in POR_LISTA:
            if not pontos_por_fase[chave]:
                continue
            roteiro = []
            for ponto in pontos_por_fase[chave]:
                celulas = [ponto.celula(lista_id) for lista_id, _ in perfil.listas]
                validas = [c for c in celulas if c is not None and c.situacao != a.NAO_SE_APLICA]
                simples, termo, dados = _passo(ponto)
                roteiro.append(
                    PassoDoRoteiro(
                        simples,
                        termo,
                        dados["curta"],
                        agregar(celulas) or NAO_SE_APLICA,
                        sum(1 for c in validas if c.situacao == a.FEITO),
                        len(validas),
                        # A semente vale para o marco inteiro, e a Etapa para o Perfil: uma só.
                        ponto.tipo in (a.SEMENTE, a.ETAPA),
                        any(c.situacao in a.A_PRATICAR for c in validas),
                        dados["porque"],
                        dados["ao_confirmar"],
                        next(
                            (c.razao for c in validas if c.situacao == a.DEPOIS and c.razao),
                            "",
                        ),
                    )
                )
            fases_lista[chave].append((perfil, detalhes[chave], roteiro))
        perfis_c.append(
            PerfilNoCentro(
                perfil.nome,
                perfil.forma,
                perfil.inscritos,
                listas,
                perfil.resumo,
                perfil,
                a.matricula_fora(perfil),
            )
        )

    fases = []
    for chave, nome, pergunta, escopo in MACROFASES:
        if chave == PUBLICACAO:
            sit, resumo, nota = _fase_edital_publicacao(edital, documentos, em_curso)
            fases.append(Macrofase(chave, nome, pergunta, escopo, sit, resumo, nota))
            continue
        if chave == INSCRICOES:
            sit, resumo = _fase_inscricoes(andamento.inscricoes)
            fases.append(Macrofase(chave, nome, pergunta, escopo, sit, resumo))
            continue
        if chave == CONCLUSAO:
            if edital.status == "ENCERRADO":
                sit, resumo = CONCLUIDA, "Edital encerrado"
            elif perfis_c and all(lst.concluida for p in perfis_c for lst in p.listas):
                # **Nunca uma ação daqui.** Se o Edital pode ser encerrado, quem decide são as
                # pendências do encerramento (prazos, recursos, Retificações, rascunhos), que a tela
                # do ato confere; dizê-lo daqui seria uma regra de disponibilidade nova, mais fraca.
                sit, resumo = EM_CURSO, "Listas concluídas — o encerramento é do Gestor"
            else:
                sit, resumo = NAO_INICIADA, "Depois das convocações"
            nota = (
                "A matrícula acontece fora do GPS."
                if any(p.matricula_fora for p in perfis_c)
                else ""
            )
            fases.append(Macrofase(chave, nome, pergunta, escopo, sit, resumo, nota))
            continue
        detalhe = fases_lista[chave]
        por_lista = [lst.situacao for _, listas, _ in detalhe for lst in listas]
        sit = juntar(por_lista) or NAO_SE_APLICA
        conta = [s for s in por_lista if s not in (None, NAO_SE_APLICA)]
        feitas = sum(1 for s in conta if s == CONCLUIDA)
        resumo = ""
        if not detalhe:
            resumo = "Não há neste Edital"
        elif len(conta) > 1 and 0 < feitas < len(conta):
            resumo = f"{feitas} de {len(conta)} listas concluídas"
        fase = Macrofase(chave, nome, pergunta, escopo, sit, resumo, perfis=detalhe)
        if chave == AVALIACAO:
            fase.paralela = _avaliacao_paralela(andamento)
        if chave == RESULTADO:
            # **Lacuna G-3 do estudo** (spec 135). O preliminar publicado não muda a situação da
            # célula — por decisão: D8a do estudo de 06/11, adotada pela 127 —, e só a nota o diz.
            # O protótipo lê a nota para a trilha não afirmar "nada divulgado".
            preliminares = sum(
                1
                for _, listas, _ in detalhe
                for lst in listas
                for c in lst.celulas
                if "preliminar" in (c.celula.nota or "")
            )
            if preliminares:
                fase.resumo = "Preliminar publicado" + (
                    f" em {preliminares} listas" if preliminares > 1 else ""
                )
        fases.append(fase)

    # A segunda leitura: as providências, as mesmas do nível 1 da 127, cada uma na sua fase.
    nivel = andamento.nivel_1
    todas = list(nivel.mostradas) + list(nivel.demais) if nivel else []
    paralela_da = {f.chave: f.paralela for f in fases}

    def item(prov):
        chave = _macrofase_da_providencia(prov, andamento.perfis)
        dados = conceito(prov.natureza)
        titulo, no_gps = prov.ato, ""
        if dados and prov.natureza in JARGAO:
            titulo, no_gps = dados["simples"], prov.ato
        return ItemDeProvidencia(
            prov, NOMES[chave], chave, dados, paralela_da.get(chave, ""), titulo, no_gps
        )

    itens = [item(p) for p in todas]
    for fase in fases:
        fase.providencias = [i for i in itens if i.fase_chave == fase.chave]
        datas = [i.p.ate for i in fase.aguardando if i.p.ate]
        fase.espera_ate = min(datas) if datas else None

    suas = [i for i in itens if i.p.grupo == "sua"]
    destaque, sem_destaque = _destaque(suas, fases)
    onde, onde_detalhe = _onde(fases, itens)
    grupos = [(rotulo, [f for f in fases if f.chave in chaves]) for rotulo, chaves in GRUPOS]
    return Centro(
        fases=fases,
        grupos=grupos,
        perfis=perfis_c,
        providencias={
            "suas": suas,
            "de_outros": [i for i in itens if i.p.grupo == "de_outro"],
            "impedidas": [i for i in itens if i.p.situacao == a.IMPEDIDO],
            "aguardando": [i for i in itens if i.p.situacao == a.AGUARDA],
            "total": len(itens),
        },
        onde=onde,
        onde_detalhe=onde_detalhe,
        em_curso=[f for f in fases if f.em_curso],
        destaque=destaque,
        sem_destaque=sem_destaque,
        alcance=_texto_do_alcance(alcance),
        ve_a_matriz=andamento.ve_a_matriz,
    )


def _destaque(suas, fases):
    """`(Destaque | None, frase quando não há destaque)`. **O critério, dito na tela.**

    1. Uma ação sua só → é ela, porque não há outra.
    2. Várias, e só uma **destrava** passos seguintes enquanto as outras correm em paralelo (a Etapa
       que o sorteio não lê, D-019 da 127) → é a que destrava, e a tela diz quais passos esperam
       por ela. É dependência que a derivação já conhece, e não prioridade inventada.
    3. Qualquer outro caso → nenhum destaque. Toda providência *Pendente* já pode ser praticada —
       o que depende de outro ato fica *Depois* e nem vira providência —, e o GPS não tem como
       saber qual importa mais.
    """
    if not suas:
        return None, ""
    por_chave = {f.chave: f for f in fases}
    if len(suas) == 1:
        item = suas[0]
        return Destaque(
            item, "É a única ação sua disponível agora.", _destrava(item, por_chave)
        ), ""
    principais = [i for i in suas if not i.paralela]
    if len(principais) == 1:
        item = principais[0]
        destrava = _destrava(item, por_chave)
        if destrava:
            outras = [i for i in suas if i is not item]
            return (
                Destaque(
                    item,
                    "É a que destrava os próximos passos. "
                    + (
                        "A outra ação sua corre em paralelo"
                        if len(outras) == 1
                        else "As outras correm em paralelo"
                    )
                    + " e não segura nada.",
                    destrava,
                ),
                "",
            )
    return None, (
        f"Você tem {len(suas)} ações disponíveis agora. Todas já podem ser feitas — o que depende "
        "de outro ato ainda não aparece aqui — e o GPS não escolhe a ordem entre elas."
    )


def _destrava(item, por_chave):
    """Os passos da mesma fase que ainda não começaram e vêm depois do passo desta providência."""
    fase = por_chave.get(item.fase_chave)
    if fase is None:
        return []
    nomes = []
    for _, _, roteiro in fase.perfis:
        visto_o_atual = False
        for passo in roteiro:
            if passo.tem_acao:
                visto_o_atual = True
                continue
            if visto_o_atual and passo.situacao == NAO_INICIADA and passo.simples not in nomes:
                nomes.append(passo.simples)
    return nomes


def _avaliacao_paralela(andamento):
    """Diz, quando a derivação o sabe, que a Etapa não segura o sorteio (D-019 da 127).

    A Etapa enumerada por marco de sorteio é esperada — dá visibilidade e recurso — mas nada a
    jusante a lê, salvo a de habilitação (`qualifyingStageId`). Sem habilitação declarada, avaliar e
    sortear são frentes independentes.
    """
    for perfil in andamento.perfis:
        for ponto in perfil.pontos:
            marco = ponto.marco or {}
            if ponto.tipo == a.RELACAO and not (marco.get("drawMethod") or {}).get(
                "qualifyingStageId"
            ):
                if any(p.tipo == a.ETAPA for p in perfil.pontos):
                    return (
                        "Paralela ao sorteio: fixar os participantes, obter a semente e sortear "
                        "não dependem desta Etapa."
                    )
    return ""


def _lista_de(nomes):
    return nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]


def _onde(fases, itens):
    """`(frase, detalhe)`. Nomeia as fases com algo em aberto **agora**, e não "N frentes".

    A primeira versão dizia "a seleção avança em 4 frentes ao mesmo tempo", e contava como frente a
    fase em curso sem nada a fazer. Com muitas fases parcialmente ativas, o número deixava de dizer
    alguma coisa. Agora a frase lista as fases que têm providência, e a segunda diz de quem é.
    """
    abertas = [f for f in fases if f.providencias]
    if not abertas:
        if fases and fases[-1].situacao == CONCLUIDA:
            return "Seleção concluída. Nada em aberto.", ""
        em_curso = [f.nome.lower() for f in fases if f.em_curso]
        if em_curso:
            return (
                f"Nada em aberto agora. Em curso: {_lista_de(em_curso)}.",
                "",
            )
        return "Nada em aberto agora.", ""
    nomes = [f.nome.lower() for f in abertas]
    frase = (
        f"Há algo em aberto em {_lista_de(nomes)}."
        if len(nomes) > 1
        else f"Há algo em aberto em {nomes[0]}."
    )
    suas = sum(1 for i in itens if i.p.grupo == "sua")
    de_outros = sum(1 for i in itens if i.p.grupo == "de_outro")
    aguardando = [i for i in itens if i.p.situacao == a.AGUARDA]
    impedidas = sum(1 for i in itens if i.p.situacao == a.IMPEDIDO)
    partes = []
    if suas:
        partes.append(f"{suas} {'ação é sua' if suas == 1 else 'ações são suas'}")
    if de_outros:
        partes.append(
            f"{de_outros} {'está com outro papel' if de_outros == 1 else 'estão com outros papéis'}"
        )
    if aguardando:
        datas = [i.p.ate for i in aguardando if i.p.ate]
        ate = f" (a primeira até {min(datas):%d/%m})" if datas else ""
        partes.append(
            f"{len(aguardando)} {'aguarda' if len(aguardando) == 1 else 'aguardam'} prazo ou "
            f"resposta{ate}"
        )
    if impedidas:
        partes.append(f"{impedidas} {'está impedida' if impedidas == 1 else 'estão impedidas'}")
    detalhe = _lista_de(partes) + "." if partes else ""
    detalhe = detalhe[:1].upper() + detalhe[1:]
    return frase, detalhe


def _texto_do_alcance(alcance):
    if alcance is None:
        return ""
    partes = []
    if alcance.conduz:
        partes.append("conduz a seleção")
    elif alcance.consulta:
        partes.append("acompanha a seleção")
    if alcance.publica:
        partes.append("publica resultados")
    if alcance.julga:
        partes.append("julga recursos")
    if alcance.retifica:
        partes.append("propõe Retificações")
    if not partes:
        return "Você acompanha este Edital sem ato a praticar nele."
    texto = "Você " + _lista_de(partes)
    if not alcance.ativo:
        texto += " — mas o Processo está encerrado, e nenhum ato é seu"
    return texto + "."
