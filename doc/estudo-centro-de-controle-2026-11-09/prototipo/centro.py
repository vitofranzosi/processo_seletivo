"""A composição do Centro de Controle do Edital — protótipo do estudo de 2026-11-09.

**Leitura de leitura.** Nada aqui deriva fato novo do banco. A entrada é o `Andamento` que a `127`
já monta (`interface/andamento.do_edital`), com as sete situações por ponto e por lista; esta
camada só **agrupa** os pontos em macrofases e **agrega** as situações de cada grupo, por regra fixa
e pura. Se a derivação da `127` mudar, a mudança chega aqui sem tocar neste arquivo.

**O que a macrofase é, e o que ela não é.** É um rótulo de apresentação para um conjunto de pontos
que a derivação já conhece. Não é coluna, não é estado persistido, e o Edital não tem "a" macrofase
atual: várias podem estar em andamento ao mesmo tempo, porque as listas andam separadas e porque o
resultado corre em paralelo com o corte e a convocação (D-006 e R2 da `133`). Por isso a trilha
marca **todas** as que têm coisa em aberto — é a resposta honesta a "onde estou?".

As frases pedagógicas (`CONCEITOS`) são texto de protótipo, conferido contra os guias de
`doc/guia-jornada-do-sorteio-2026-11-05/` e `doc/gps-por-dentro/`. Não são regra.
"""

from dataclasses import dataclass, field

from processo_seletivo.interface import andamento as a

# ---------------------------------------------------------------------------------------------
# As macrofases
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
    (VAGAS, "Vagas", "Quem a faixa alcança, e que vaga cada um ocupa?", "lista"),
    (CONVOCACAO, "Convocação", "Quem foi chamado, entregou e foi conferido?", "lista"),
    (CONCLUSAO, "Conclusão", "Tudo tem desfecho, e o Edital pode ser encerrado?", "Edital"),
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


def macrofase_do_ponto(ponto):
    if ponto.tipo == a.ETAPA:
        # A Etapa governada pela faixa (a documental, quase sempre) corre entre o corte e a
        # apuração (D-014 da 127): para quem conduz, é parte de "quem ocupa as vagas".
        return VAGAS if ponto.grupo == a.GRUPO_DA_GOVERNADA else AVALIACAO
    return _DO_TIPO.get(ponto.tipo, CLASSIFICACAO)


# ---------------------------------------------------------------------------------------------
# A agregação — a única regra nova, e é de apresentação
# ---------------------------------------------------------------------------------------------

CONCLUIDA, ACAO, AGUARDANDO, IMPEDIDA = "concluida", "acao", "aguardando", "impedida"
PARCIAL, NAO_INICIADA, NAO_SE_APLICA = "parcial", "nao_iniciada", "nao_se_aplica"

ROTULOS = {
    CONCLUIDA: "Concluída",
    ACAO: "Ação disponível",
    AGUARDANDO: "Aguardando",
    IMPEDIDA: "Com impedimento",
    PARCIAL: "Em andamento",
    NAO_INICIADA: "Ainda não",
    NAO_SE_APLICA: "Não se aplica",
}
SINAIS = {
    CONCLUIDA: "✓",
    ACAO: "●",
    AGUARDANDO: "◷",
    IMPEDIDA: "⊘",
    PARCIAL: "◐",
    NAO_INICIADA: "·",
    NAO_SE_APLICA: "—",
}
#: A ordem em que uma situação "vence" outra quando se juntam listas: o que pede gesto primeiro.
_PESO = (ACAO, IMPEDIDA, AGUARDANDO, PARCIAL, NAO_INICIADA, CONCLUIDA, NAO_SE_APLICA)
EM_CURSO = frozenset({ACAO, AGUARDANDO, IMPEDIDA, PARCIAL})


def agregar(celulas):
    """A situação de um grupo de células — de uma macrofase numa lista.

    Puro, e por regra fixa: há ato a praticar → *ação disponível*; senão, impedimento; senão,
    espera; feito ao lado de *Depois* → *em andamento*; tudo feito → *concluída*. Nunca devolve
    "pendente" para o que a derivação chamou de *Depois* — a ausência de ato não é pendência (D-007
    da 127).
    """
    s = [c.situacao for c in celulas if c is not None]
    if not s:
        return None
    if all(x in (a.FEITO, a.NAO_SE_APLICA) for x in s):
        return CONCLUIDA if a.FEITO in s else NAO_SE_APLICA
    if any(x in a.A_PRATICAR for x in s):
        return ACAO
    if a.IMPEDIDO in s:
        return IMPEDIDA
    if a.AGUARDA in s:
        return AGUARDANDO
    if a.FEITO in s:
        return PARCIAL
    return NAO_INICIADA


def juntar(situacoes):
    """A situação de uma macrofase no Edital, a partir das situações por lista."""
    s = [x for x in situacoes if x is not None]
    if not s:
        return None
    if all(x == NAO_SE_APLICA for x in s):
        return NAO_SE_APLICA
    s = [x for x in s if x != NAO_SE_APLICA]
    if all(x == CONCLUIDA for x in s):
        return CONCLUIDA
    # Uma lista concluída ao lado de outra que nem começou é andamento, e não "ainda não".
    vencedora = min(s, key=_PESO.index)
    if vencedora in (NAO_INICIADA,) and CONCLUIDA in s:
        return PARCIAL
    return vencedora


# ---------------------------------------------------------------------------------------------
# O texto pedagógico — curto, opcional, por conceito
# ---------------------------------------------------------------------------------------------

#: `{chave: (o que é, por que existe, o que acontece ao confirmar)}`. Chave = tipo do ponto ou
#: natureza da providência.
CONCEITOS = {
    a.RELACAO: (
        "Congelar a relação",
        "É publicar, para cada lista, quem participa do sorteio e com que número, num registro que "
        "não muda mais.",
        "Encerrar as inscrições impede que entre gente nova; congelar fixa a lista **antes** de a "
        "semente existir, para que ninguém possa montá-la já sabendo o resultado.",
        "Irreversível. Uma correção depois disso exige Retificação e uma relação sucessora. Congele "
        "todas as listas do marco antes de observar a extração: a relação congelada depois da "
        "semente conhecida é recusada.",
    ),
    a.SEMENTE: (
        "Observar a extração",
        "A semente são os números da extração declarada no Edital (a Loteria Federal, no certame "
        "real). Ela é uma só para todas as listas do marco.",
        "Ninguém escolhe a semente: ela vem de uma fonte pública, depois do congelamento. É o que "
        "torna o sorteio verificável por qualquer pessoa.",
        "Com a Loteria Federal, só depois da data da extração. Se a fonte não responde, nada é "
        "gravado: observa-se de novo; não existe digitar os números à mão.",
    ),
    a.SORTEIO: (
        "Realizar o sorteio",
        "O algoritmo publicado no Edital aplica a semente à relação congelada e produz a ordem da "
        "lista.",
        "A mesma relação e a mesma semente dão sempre a mesma ordem: o resultado pode ser "
        "reproduzido no canal público.",
        "Grava a ordem da lista como ato imutável, com manifesto e página de verificação.",
    ),
    a.ORDEM: (
        "Emitir a ordem",
        "É gravar a classificação da lista, calculada pelas notas consolidadas, pesos e critérios "
        "de desempate do Edital.",
        "A ordem é a base de tudo o que vem depois: corte, apuração, resultado e convocação leem a "
        "ordem vigente.",
        "Irreversível. Se uma nota mudar depois (um recurso deferido, por exemplo), a ordem fica "
        "obsoleta e é preciso emitir uma sucessora, com motivo. Numa lista sem inscritos, emitir "
        "declara que ninguém concorreu ali.",
    ),
    a.CORTE: (
        "Emitir o corte",
        "O corte define a faixa: até que posição de cada lista as pessoas seguem — para as vagas e "
        "para a reserva, se o Edital a prevê.",
        "Ele limita quem passa à Etapa governada (a análise documental, em geral) e quem a "
        "apuração considera.",
        "Com o prazo de recurso aberto, a recomendação é esperar: um recurso deferido tornaria o "
        "corte obsoleto.",
    ),
    a.APURACAO: (
        "Apurar a ocupação",
        "A apuração cruza as listas (ampla concorrência e cotas) e decide que vaga cada pessoa "
        "alcançada ocupa, sem contar ninguém duas vezes.",
        "Quem está bem colocado na ampla ocupa pela ampla, e a vaga da cota passa ao próximo da "
        "cota. A convocação chama quem a apuração indicou.",
        "Grava a apuração vigente. Uma desistência ou um corte novo a tornam obsoleta, e ela é "
        "refeita.",
    ),
    a.RESULTADO: (
        "Divulgar o resultado",
        "O resultado é a ordem tornada pública. O preliminar abre o prazo de recurso; o definitivo "
        "vem depois que o prazo acaba e os recursos são decididos.",
        "O definitivo não é pré-requisito do corte, da apuração nem da convocação — mas um recurso "
        "deferido pode mudá-los.",
        "Publicar é ato do Publicador, com documento próprio.",
    ),
    a.RECURSO: (
        "Decidir recursos",
        "O candidato pode recorrer do resultado preliminar dentro do prazo. O recurso é admitido e "
        "julgado por quem tem a atribuição de julgar.",
        "Um recurso deferido pode mudar uma nota, e com ela a ordem, o corte e a apuração.",
        "A decisão é registrada e comunicada; a ordem afetada passa a pedir sucessora.",
    ),
    a.CONVOCACAO: (
        "Convocar",
        "Chamar, com prazo, quem a apuração indicou para ocupar a vaga. Cada convocação é "
        "comunicada e acompanhada até o desfecho.",
        "É a passagem da classificação para a ocupação real da vaga. Quem não responde no prazo "
        "tem o não atendimento registrado, e a fila anda.",
        "A convocação e a comunicação são atos registrados. A matrícula acontece fora do GPS.",
    ),
    a.CONFERIR: (
        "Conferir documentos",
        "Cada documento entregue pelo convocado é aberto e marcado como conforme ou pendente, com "
        "motivo.",
        "O GPS só aceita 'conforme' de quem abriu o arquivo. Com tudo conforme, registra-se o "
        "desfecho da convocação.",
        "A pendência volta ao candidato, que pode reenviar dentro do prazo.",
    ),
    a.ETAPA: (
        "Avaliar uma Etapa",
        "A Etapa (prova, títulos, análise documental) é distribuída a avaliadores, avaliada e "
        "consolidada.",
        "Só a Etapa consolidada alimenta a ordem. Distribuir é atribuir as inscrições a avaliadores "
        "alocados.",
        "Consolidar fecha os resultados da Etapa; mudá-los depois é reavaliação, por recurso.",
    ),
}
for _n in (a.DISTRIBUIR, a.AVALIAR, a.CONSOLIDAR, a.REAVALIAR):
    CONCEITOS[_n] = CONCEITOS[a.ETAPA]


def conceito(chave):
    dados = CONCEITOS.get(chave)
    if not dados:
        return None
    titulo, oque, porque, ao_confirmar = dados
    return {"titulo": titulo, "oque": oque, "porque": porque, "ao_confirmar": ao_confirmar}


# ---------------------------------------------------------------------------------------------
# A composição
# ---------------------------------------------------------------------------------------------


@dataclass
class PassoDoRoteiro:
    titulo: str
    situacao: str
    feitas: int
    total: int
    unico: bool

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


@dataclass
class CelulaNaFase:
    lista: str
    ponto: str
    celula: object
    conceito: dict | None


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
    #: `[(perfil, [ListaNaFase])]` — o detalhamento por lista
    perfis: list = field(default_factory=list)
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
        return self.situacao in EM_CURSO


@dataclass
class ListaNoCentro:
    rotulo: str
    curto: str
    fases: list  # [(chave, situacao)]
    agora: object  # Celula ou None
    agora_fase: str
    concluida: bool
    atos: list = field(default_factory=list)


@dataclass
class PerfilNoCentro:
    nome: str
    forma: str
    inscritos: int
    listas: list
    resumo: str
    matriz: object  # o PerfilNoAndamento, para o "ver tudo"
    matricula_fora: bool


@dataclass
class Centro:
    fases: list
    perfis: list
    providencias: dict
    onde: str
    em_curso: list
    principal: object = None
    alcance: str = ""
    ve_a_matriz: bool = False


def _curto(rotulo):
    if rotulo.startswith("Ampla concorrência"):
        return "Ampla concorrência"
    if "(" in rotulo and rotulo.endswith(")"):
        return rotulo[rotulo.rfind("(") + 1 : -1]
    return rotulo


def _macrofase_da_providencia(prov, perfis):
    natureza = prov.natureza
    if natureza in (a.DISTRIBUIR, a.AVALIAR, a.CONSOLIDAR, a.REAVALIAR, a.ETAPA):
        governadas = {
            p.titulo for pf in perfis for p in pf.pontos if p.grupo == a.GRUPO_DA_GOVERNADA
        }
        if any(nome in (prov.onde or "") for nome in governadas):
            return VAGAS
    return _DA_NATUREZA.get(natureza, CLASSIFICACAO)


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
        situacao, resumo = IMPEDIDA, "Cancelado"
    else:
        situacao, resumo = ACAO, "Em elaboração"
    nota = ""
    if em_curso:
        nota = f"{len(em_curso)} Retificação em curso — ela pode mudar datas, vagas ou regras."
        if situacao == CONCLUIDA:
            situacao = PARCIAL
    return situacao, resumo, nota


def _fase_inscricoes(inscricoes):
    from processo_seletivo.inscricoes.domain import periodo

    estado = inscricoes.get("estado")
    enviadas = inscricoes.get("enviadas") or 0
    if inscricoes.get("cancelado"):
        return IMPEDIDA, f"Período cancelado · {enviadas} enviadas"
    if estado == periodo.ENCERRADO:
        return CONCLUIDA, f"{enviadas} inscriç{'ão' if enviadas == 1 else 'ões'} · encerradas"
    if estado == periodo.ABERTO:
        return AGUARDANDO, f"Abertas · {enviadas} até agora"
    if estado == periodo.FUTURO:
        return NAO_INICIADA, "Ainda não abertas"
    return NAO_INICIADA, "Período não designado"


def compor(edital, andamento, *, documentos, em_curso, alcance=None):
    perfis_c, fases_lista = [], {chave: [] for chave in POR_LISTA}
    for perfil in andamento.perfis:
        listas = []
        pontos_por_fase = {chave: [] for chave in POR_LISTA}
        for ponto in perfil.pontos:
            pontos_por_fase[macrofase_do_ponto(ponto)].append(ponto)
        detalhes = {chave: [] for chave in POR_LISTA}
        for lista_id, rotulo in perfil.listas:
            fases, agora, agora_fase = [], None, ""
            for chave in POR_LISTA:
                celulas = [p.celula(lista_id) for p in pontos_por_fase[chave]]
                sit = agregar(celulas)
                fases.append((chave, sit))
                detalhes[chave].append(
                    ListaNaFase(
                        _curto(rotulo),
                        sit,
                        [
                            CelulaNaFase(
                                _curto(rotulo),
                                p.titulo,
                                p.celula(lista_id),
                                conceito(p.tipo),
                            )
                            for p in pontos_por_fase[chave]
                            if p.celula(lista_id) is not None
                        ],
                    )
                )
            # "Agora nesta lista": os atos a praticar, um por macrofase, na ordem da jornada — e não
            # só o primeiro, porque a Etapa paralela vem antes do sorteio na sequência e esconderia a
            # frente principal. Sem ato a praticar, a primeira espera ou impedimento (a preferência
            # de `da_lista`, FR-4543 da 133).
            vistas = set()
            agora_varios = []
            for ponto in perfil.pontos:
                c = ponto.celula(lista_id)
                fase_do_ponto = macrofase_do_ponto(ponto)
                if c is not None and c.situacao in a.A_PRATICAR and fase_do_ponto not in vistas:
                    vistas.add(fase_do_ponto)
                    agora_varios.append((NOMES[fase_do_ponto], c))
            if agora_varios:
                agora_fase, agora = agora_varios[0][0], agora_varios[0][1]
            if agora is None:
                for ponto in perfil.pontos:
                    c = ponto.celula(lista_id)
                    if c is not None and c.em_aberto:
                        agora, agora_fase = c, macrofase_do_ponto(ponto)
                        break
            concluida = all(s in (CONCLUIDA, NAO_SE_APLICA, None) for _, s in fases)
            item = ListaNoCentro(rotulo, _curto(rotulo), fases, agora, agora_fase, concluida)
            item.atos = agora_varios
            listas.append(item)
        for chave in POR_LISTA:
            if pontos_por_fase[chave]:
                roteiro = []
                for ponto in pontos_por_fase[chave]:
                    celulas = [ponto.celula(lista_id) for lista_id, _ in perfil.listas]
                    validas = [
                        c for c in celulas if c is not None and c.situacao != a.NAO_SE_APLICA
                    ]
                    roteiro.append(
                        PassoDoRoteiro(
                            ponto.titulo,
                            agregar(celulas) or NAO_SE_APLICA,
                            sum(1 for c in validas if c.situacao == a.FEITO),
                            len(validas),
                            # A semente vale para o marco inteiro, e a Etapa para o Perfil: uma só.
                            ponto.tipo in (a.SEMENTE, a.ETAPA),
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

    # As providências, cada uma na macrofase dela — as mesmas do nível 1, sem reordenar.
    nivel = andamento.nivel_1
    todas = list(nivel.mostradas) + list(nivel.demais) if nivel else []

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
            elif all(lst.concluida for p in perfis_c for lst in p.listas) and perfis_c:
                sit, resumo = ACAO, "Tudo com desfecho — pronto para encerrar"
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
        sit = juntar(por_lista)
        conta = [s for s in por_lista if s not in (None, NAO_SE_APLICA)]
        feitas = sum(1 for s in conta if s == CONCLUIDA)
        if sit is None:
            resumo = "Não há neste Edital"
            sit = NAO_SE_APLICA
        elif sit == NAO_SE_APLICA:
            resumo = "Não se aplica"
        elif len(conta) > 1 and 0 < feitas < len(conta):
            resumo = f"{feitas} de {len(conta)} listas concluídas"
        elif len(conta) > 1 and sit == CONCLUIDA:
            resumo = f"{len(conta)} listas"
        else:
            resumo = ""
        fase = Macrofase(chave, nome, pergunta, escopo, sit, resumo, perfis=detalhe)
        if chave == AVALIACAO:
            fase.paralela = _avaliacao_paralela(andamento)
        if chave == RESULTADO:
            # **Lacuna G-3 do estudo.** O preliminar publicado não muda a situação da célula (D8a da
            # 127: ela segue o definitivo); só a nota o diz. O protótipo lê a nota para a trilha não
            # afirmar "nada divulgado" — a spec precisa de um campo estruturado no lugar disto.
            preliminares = sum(
                1
                for _, listas, _ in detalhe
                for lst in listas
                for c in lst.celulas
                if "preliminar" in (c.celula.nota or "")
            )
            if preliminares:
                fase.resumo = f"preliminar publicado em {preliminares} lista" + (
                    "s" if preliminares > 1 else ""
                )
        fases.append(fase)

    em_curso_ = [f for f in fases if f.em_curso]
    onde = _onde(em_curso_, fases)

    def item(prov):
        chave = _macrofase_da_providencia(prov, andamento.perfis)
        return ItemDeProvidencia(prov, NOMES[chave], chave, conceito(prov.natureza))

    itens = [item(p) for p in todas]
    for fase in fases:
        fase.providencias = [i for i in itens if i.fase_chave == fase.chave]
        for i in fase.providencias:
            i.paralela = fase.paralela
        datas = [i.p.ate for i in fase.providencias if i.p.situacao == a.AGUARDA and i.p.ate]
        fase.espera_ate = min(datas) if datas else None
    suas = [i for i in itens if i.p.grupo == "sua"]
    principal = suas[0] if len(suas) == 1 else None
    return Centro(
        fases=fases,
        perfis=perfis_c,
        providencias={
            "suas": suas,
            "de_outros": [i for i in itens if i.p.grupo == "de_outro"],
            "impedidas": [i for i in itens if i.p.situacao == a.IMPEDIDO],
            "aguardando": [i for i in itens if i.p.situacao == a.AGUARDA],
            "total": len(itens),
        },
        onde=onde,
        em_curso=em_curso_,
        principal=principal,
        alcance=_texto_do_alcance(alcance),
        ve_a_matriz=andamento.ve_a_matriz,
    )


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
                        "Independente do sorteio: a relação, a semente e o sorteio não leem o "
                        "resultado desta Etapa. Ela segue em paralelo."
                    )
    return ""


def _onde(em_curso, fases):
    if not em_curso:
        if fases and fases[-1].situacao == CONCLUIDA:
            return "Seleção concluída. Nada em aberto."
        return "Nada em andamento agora."
    nomes = [
        f"{f.nome.lower() if f.chave != RESULTADO else 'resultado e recursos'}" for f in em_curso
    ]
    if len(nomes) == 1:
        return f"A seleção está na fase de {nomes[0]}."
    return (
        f"A seleção avança em {len(nomes)} frentes ao mesmo tempo: "
        + ", ".join(nomes[:-1])
        + f" e {nomes[-1]}."
    )


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
    texto = "Você " + ", ".join(partes[:-1]) + (" e " if len(partes) > 1 else "") + partes[-1]
    if not alcance.ativo:
        texto += " — mas o Processo está encerrado, e nenhum ato é seu"
    return texto + "."
