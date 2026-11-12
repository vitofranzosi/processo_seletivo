"""O catálogo de cenários de treinamento (134, FR-4650 a FR-4655).

Cada cenário é **uma ficha e uma receita**: a ficha diz à pessoa o que ela vai encontrar e o que
fazer (os campos da seção 7 do pedido), e a receita monta o estado inicial pelos passos de
`construcao.py`. As receitas se apoiam umas nas outras — a convocação parte da classificação, que
parte das inscrições encerradas — porque é assim que o certame chega lá: nenhum estado avançado é
gravado sem o histórico que o produz (FR-4641).

**A versão da definição** sobe quando a receita muda o estado que produz. A rodada gravada guarda a
versão com que nasceu, e a verificação acusa quando ela é anterior à do código: o cenário continua
válido, mas não é mais o que o roteiro descreve, e restaurá-lo traz a versão nova.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import timedelta

from django.utils import timezone

from processo_seletivo.treinamento import construcao as c
from processo_seletivo.treinamento.construcao import (
    AVALIACAO_1,
    ELABORACAO,
    ETAPA_DOCUMENTAL,
    ETAPA_PROVA,
    ETAPA_TITULOS,
    FORMALIZACAO,
    GESTAO,
    HOMOLOGACAO,
    PRESIDENCIA,
    PUBLICACAO,
    notas_de,
)


@dataclass(frozen=True)
class Cenario:
    codigo: str
    nome: str
    objetivo: str
    tipo_de_selecao: str
    metodo: str
    estado_inicial: str
    precondicoes: tuple
    papeis: tuple
    proxima_acao: str
    resultado_esperado: str
    dependencias: tuple
    montar: object
    versao: str = "1"
    # Quantos dias depois de gerado o cenário continua no estado da ficha, quando há prazo que
    # corre: o período de inscrições aberto, a janela recursal. `None` é sem prazo.
    validade_dias: int | None = None
    exige_fonte_de_demonstracao: bool = False
    # O C16 e o C17 provisionam a pessoa do setor e o vínculo dela (FR-6720 a FR-6729); só eles.
    provisiona_formalizacao: bool = False
    restauracao: str = (
        "restaurar_cenario_de_treinamento cria uma rodada nova, no estado inicial e com datas "
        "contadas do dia da restauração; a rodada anterior é cancelada pelo comando de "
        "cancelamento, e nada é excluído."
    )
    limitacoes: tuple = field(default=())


# ---------------------------------------------------------------------------------------------
# As receitas
# ---------------------------------------------------------------------------------------------

# Notas de dez candidatos na prova (peso 2, mínima 6,0) e nos títulos (peso 1). Os pares foram
# escolhidos para que o exercício tenha o que conferir: 1 e 2 empatam no total e o desempate pela
# prova os separa; 3 e 4 são idênticos e permanecem empatados; 8 é eliminado na prova; 9 e 10
# concorrem na modalidade reservada.
NOTAS_DA_CLASSIFICACAO = (
    ("9.0", "8.0"),
    ("8.5", "9.0"),
    ("8.0", "7.0"),
    ("8.0", "7.0"),
    ("7.5", "6.0"),
    ("7.0", "5.0"),
    ("6.5", "4.0"),
    ("5.0", None),
    ("7.0", "8.0"),
    ("6.0", "6.0"),
)
RESERVADAS_DA_CLASSIFICACAO = (9, 10)

# Seis candidatos, todos da ampla, para a cadeia que chega à convocação — o recorte que o
# `seed_demo` percorre até convocar, e que a suíte prova a cada commit.
NOTAS_DA_CONVOCACAO = (
    ("9.0", "9.0"),
    ("8.5", "8.0"),
    ("8.0", "8.0"),
    ("7.5", "7.0"),
    ("7.0", "6.0"),
    ("6.5", "5.0"),
)


def _edital_de_notas(
    m, *, inscritos, reservada=(), encerrar=True, janela="declarada", documentos=None
):
    m.criar()
    m.elaborar(
        perfis=c.perfil_de_notas(janela=janela),
        inicio=m.agora - timedelta(days=10),
        duracao_dias=40,
        documentos=c.documentos_de_notas() if documentos is None else documentos,
    )
    m.publicar()
    inscricoes = m.inscrever(inscritos, reservada=reservada) if inscritos else []
    if encerrar:
        m.encerrar_inscricoes(timezone.now())
    return inscricoes


def _avaliar_as_pontuadas(m, inscricoes, notas):
    """As duas Etapas pontuadas, concluídas e consolidadas; a segunda só para quem passou."""
    prova = notas_de(inscricoes, [nota for nota, _ in notas])
    m.avaliar(ETAPA_PROVA, prova)
    titulos = {
        inscricao: valor
        for inscricao, (_, valor) in zip(inscricoes, notas, strict=True)
        if valor is not None
    }
    m.avaliar(ETAPA_TITULOS, notas_de(list(titulos), list(titulos.values())))


def montar_c01(m):
    """Elaboração: o rascunho com Perfil, Cronograma e Etapas, e sem os Documentos Exigidos."""
    m.criar()
    m.elaborar(
        perfis=c.perfil_de_notas(),
        inicio=m.agora + timedelta(days=7),
        duracao_dias=30,
        documentos=[],
    )


def montar_c02(m):
    _edital_de_notas(m, inscritos=3, encerrar=False)


def montar_c03(m):
    _edital_de_notas(m, inscritos=8, reservada=(7, 8))


def montar_c04(m):
    inscricoes = _edital_de_notas(
        m, inscritos=len(NOTAS_DA_CLASSIFICACAO), reservada=RESERVADAS_DA_CLASSIFICACAO
    )
    m.constituir_comissao(alocar_em=(ETAPA_PROVA, ETAPA_TITULOS, ETAPA_DOCUMENTAL))
    _avaliar_as_pontuadas(m, inscricoes, NOTAS_DA_CLASSIFICACAO)


def montar_c05(m):
    """Avaliação pendente: a prova distribuída à avaliação 1, com três de oito concluídas."""
    inscricoes = _edital_de_notas(m, inscritos=8, reservada=(7, 8))
    m.constituir_comissao(alocar_em=(ETAPA_PROVA, ETAPA_TITULOS, ETAPA_DOCUMENTAL))
    m.distribuir(ETAPA_PROVA, inscricoes)
    from processo_seletivo.avaliacoes.application.avaliacao import concluir
    from processo_seletivo.publicacoes.application.selectors import effective_version

    versao = effective_version(edital_id=m.edital.id)
    for inscricao, nota in zip(inscricoes[:3], ("8.5", "7.0", "5.5"), strict=True):
        concluir(
            ator=m.ator(AVALIACAO_1),
            edital=m.edital,
            etapa_id=m.id(ETAPA_PROVA),
            inscricao_id=inscricao.id,
            pontuacao=c.Decimal(nota),
            parecer=f"Avaliação de treinamento. {c.MARCA}.",
            expected_revision=1,
            versao_reconhecida=versao.id,
            correlation_id=m.correlacao,
        )


def _ate_o_resultado(m, notas, *, natureza="PRELIMINAR", janela="declarada", documentos=None):
    inscricoes = _edital_de_notas(m, inscritos=len(notas), janela=janela, documentos=documentos)
    m.constituir_comissao(alocar_em=(ETAPA_PROVA, ETAPA_TITULOS, ETAPA_DOCUMENTAL))
    _avaliar_as_pontuadas(m, inscricoes, notas)
    ato = m.emitir_ordem()
    declaracao = ""
    if natureza == "DEFINITIVA" and janela == "negada":
        # O marco nega recurso, e por isso não há janela que o sistema compute: o definitivo pede a
        # declaração expressa, com fundamento (a FR-085 da `018`). Ela é dita, e não contornada.
        declaracao = (
            "O marco classificatório deste Edital não admite recurso, conforme publicado; não há "
            f"prazo recursal a aguardar. {c.MARCA}."
        )
    m.divulgar(ato, natureza, declaracao)
    return inscricoes


def montar_c08(m):
    _ate_o_resultado(m, NOTAS_DA_CLASSIFICACAO[:8])


def montar_c09(m):
    """O definitivo sem preliminar: o marco declara que não admite recurso (`--janela negada`)."""
    _ate_o_resultado(m, NOTAS_DA_CONVOCACAO, natureza="DEFINITIVA", janela="negada")


def _ate_a_apuracao(m, notas, *, habilitadas=None, documentos=None):
    inscricoes = _ate_o_resultado(m, notas, documentos=documentos)
    habilitadas = inscricoes if habilitadas is None else habilitadas
    m.avaliar(
        ETAPA_DOCUMENTAL,
        {
            inscricao: ("FAVORAVEL" if inscricao in habilitadas else "DESFAVORAVEL")
            for inscricao in inscricoes
        },
    )
    m.cortar_e_apurar()
    return inscricoes


def montar_c10(m):
    _ate_a_apuracao(m, NOTAS_DA_CONVOCACAO)


def _convocar_e_comunicar(m, inscricoes):
    convocacoes = []
    for ordem, inscricao in enumerate(inscricoes, 1):
        convocacao = m.convocar(inscricao, ordem)
        m.comunicar(convocacao, ordem)
        convocacoes.append(convocacao)
    return convocacoes


def montar_c11(m):
    """Três convocados: nada entregue; diploma entregue e devolvido como pendente; tudo entregue."""
    inscricoes = _ate_a_apuracao(m, NOTAS_DA_CONVOCACAO)
    primeira, segunda, terceira = _convocar_e_comunicar(m, inscricoes[:3])
    diploma = m.apresentar(segunda, inscricoes[1], c.DOC_DIPLOMA)
    m.conferir(
        segunda,
        c.DOC_DIPLOMA,
        diploma,
        "PENDENTE",
        motivo="Arquivo ilegível: envie novamente, com todas as páginas (treinamento).",
    )
    m.apresentar(terceira, inscricoes[2], c.DOC_DIPLOMA)
    m.apresentar(terceira, inscricoes[2], c.DOC_RESIDENCIA)


def montar_c12(m):
    """Três convocados com diploma e residência entregues, nenhum item conferido ainda.

    **Nenhum já conforme, e é regra, não escolha**: conferir como conforme exige que o próprio
    conferente tenha aberto o arquivo (FR-3611 da `115`), e a abertura é registrada pela tela que o
    serve. O gerador não a fabrica — a primeira conferência é do operador, como deve ser.
    """
    inscricoes = _ate_a_apuracao(m, NOTAS_DA_CONVOCACAO)
    convocacoes = _convocar_e_comunicar(m, inscricoes[:3])
    for convocacao, inscricao in zip(convocacoes, inscricoes[:3], strict=True):
        m.apresentar(convocacao, inscricao, c.DOC_DIPLOMA)
        m.apresentar(convocacao, inscricao, c.DOC_RESIDENCIA)


def montar_c13(m):
    _edital_de_notas(m, inscritos=2, encerrar=False)


def montar_c14(m):
    _ate_o_resultado(m, NOTAS_DA_CONVOCACAO, natureza="DEFINITIVA", janela="negada")


def montar_c15(m):
    """Vagas que sobram: três inscritos para quatro vagas, um inabilitado na análise documental."""
    notas = NOTAS_DA_CONVOCACAO[:3]
    inscricoes = _ate_o_resultado(m, notas)
    m.avaliar(
        ETAPA_DOCUMENTAL,
        {
            inscricoes[0]: "FAVORAVEL",
            inscricoes[1]: "FAVORAVEL",
            inscricoes[2]: "DESFAVORAVEL",
        },
    )
    m.cortar_e_apurar()


def _aptas_para_formalizacao(m):
    """Três convocados com aceite, e a definição com a identificação (FR-6720, FR-6728, D-010).

    O Edital não pede documento na convocação: o aceite passa sem conferência, e a pessoa nasce
    apta. A pessoa do setor nasce habilitada — o vínculo Formalização na unidade (FR-6722).
    """
    inscricoes = _ate_a_apuracao(m, NOTAS_DA_CONVOCACAO, documentos=c.documentos_da_formalizacao())
    for ordem, convocacao in enumerate(_convocar_e_comunicar(m, inscricoes[:3]), 1):
        m.desfechar(convocacao, ordem)
    m.definir_formalizacao([c.DOC_IDENTIFICACAO])
    return m.habilitar_formalizacao()


def montar_c16(m):
    """Exportar: a pessoa do setor habilitada **e** designada (FR-6723)."""
    m.designar_formalizacao(_aptas_para_formalizacao(m))


def montar_c17(m):
    """Designar: a pessoa do setor só habilitada, sem designação (FR-6723)."""
    _aptas_para_formalizacao(m)


# Quem declara a cota PPP no cenário de sorteio: três dos dez, de modo que a relação da cota tenha
# mais inscritos que a única vaga reservada e o sorteio dela também decida alguma coisa.
COTISTAS_DO_SORTEIO = (2, 5, 9)


def _edital_de_sorteio(m, *, inscritos=10):
    m.criar()
    m.elaborar(
        perfis=c.perfil_de_sorteio(),
        inicio=m.agora - timedelta(days=10),
        duracao_dias=40,
        documentos=c.documentos_de_sorteio(),
        metodo=c.metodo_do_sorteio(concurso_da_rodada(m.unidade, m.codigo, m.rodada)),
        etapas=(ETAPA_TITULOS,),
    )
    m.publicar()
    m.inscrever(inscritos, reservada=COTISTAS_DO_SORTEIO)
    m.encerrar_inscricoes(timezone.now())
    m.constituir_comissao()


def concurso_da_rodada(unidade, codigo, rodada):
    """`807001NNN` para o C07 na rodada 1 da unidade NNN — acima do 5000 que a fonte de
    demonstração dá por feito.

    **A ocorrência é única por fonte e referência no banco inteiro**, e não por unidade: sem a
    unidade no número, o C07 da segunda unidade a carregar era recusado, porque o concurso dele já
    tinha sido observado pela primeira. Os três últimos dígitos são um resumo do código da
    unidade; duas unidades que caíssem no mesmo resumo teriam o cenário de sorteio recusado na
    pré-visualização, com o motivo — não há colisão silenciosa. A rodada tem três dígitos, para que
    a rodada 100 de um cenário não se confunda com a 10 de outra unidade.
    """
    resumo = int(hashlib.sha256(unidade.encode()).hexdigest(), 16) % 1000
    return f"8{int(codigo[1:]):02d}{rodada:03d}{resumo:03d}"


def montar_c06(m):
    _edital_de_sorteio(m)


def montar_c07(m):
    _edital_de_sorteio(m)
    m.congelar_relacao()
    m.congelar_relacao(reservada=True)


# ---------------------------------------------------------------------------------------------
# As fichas
# ---------------------------------------------------------------------------------------------

_SELECAO = "Professor substituto (Perfil docente de Informática, com cota PPP)"
_CURSO = "Curso técnico EaD (ampla concorrência e cota PPP)"
_EQUIPE_DA_PUBLICACAO = (
    f"Elaborador ({ELABORACAO})",
    f"Homologador ({HOMOLOGACAO})",
    f"Publicador ({PUBLICACAO})",
)

CENARIOS = (
    Cenario(
        codigo="C01",
        nome="Elaboração de edital",
        objetivo="Completar um Edital em elaboração e levá-lo à publicação.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial=(
            "Edital EM ELABORAÇÃO com Perfil, vagas, modalidades, Cronograma e Etapas; sem "
            "Documentos Exigidos."
        ),
        precondicoes=("Inscrições previstas para começar daqui a 7 dias.",),
        papeis=_EQUIPE_DA_PUBLICACAO,
        proxima_acao=(
            "Elaborador: acrescentar os Documentos Exigidos, revisar e submeter; Homologador: "
            "homologar; Publicador: publicar."
        ),
        resultado_esperado="Edital PUBLICADO, com a versão consolidada e o documento oficial.",
        dependencias=("Uma autoridade vigente na unidade.",),
        montar=montar_c01,
        validade_dias=7,
    ),
    Cenario(
        codigo="C02",
        nome="Inscrições abertas",
        objetivo="Percorrer a jornada do candidato e acompanhar as inscrições na gestão.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial="Edital PUBLICADO, período de inscrições aberto, 3 inscrições enviadas.",
        precondicoes=("Período de inscrições aberto por 30 dias a partir da geração.",),
        papeis=("Candidato (portal, por código no e-mail)", f"Gestor ({GESTAO})"),
        proxima_acao="Inscrever-se pelo portal; consultar as inscrições como Gestor.",
        resultado_esperado="Nova inscrição enviada, com protocolo e comprovante.",
        dependencias=("Correio do ambiente para o código de acesso do candidato.",),
        montar=montar_c02,
        validade_dias=30,
    ),
    Cenario(
        codigo="C03",
        nome="Inscrições encerradas",
        objetivo="Consultar inscritos e preparar a avaliação depois do prazo.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial=(
            "Edital PUBLICADO, inscrições encerradas por Retificação, 8 inscrições (2 na cota)."
        ),
        precondicoes=("Sem comissão constituída.",),
        papeis=(f"Gestor ({GESTAO})",),
        proxima_acao="Consultar os inscritos; constituir a comissão e alocar as Etapas.",
        resultado_esperado="Comissão constituída, pronta para distribuir as avaliações.",
        dependencias=(),
        montar=montar_c03,
    ),
    Cenario(
        codigo="C04",
        nome="Classificação por notas",
        objetivo="Emitir a ordem classificatória e conferir empates, desempate e listas.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas: soma ponderada, desempate pela maior nota na prova",
        estado_inicial=(
            "10 inscritos (2 na cota), prova e títulos avaliados e consolidados; nenhuma ordem "
            "emitida."
        ),
        precondicoes=(
            "Empate no total resolvido pela prova (candidatos 01 e 02).",
            "Empate residual (03 e 04).",
            "Eliminado na prova (08).",
            "Quatro vagas: três na ampla e uma na cota.",
        ),
        papeis=(f"Presidência da comissão ({PRESIDENCIA})", f"Publicador ({PUBLICACAO})"),
        proxima_acao="Presidência: conferir a prévia e emitir a ordem; Publicador: divulgar.",
        resultado_esperado="Ordem emitida por recorte; resultado preliminar divulgado.",
        dependencias=(),
        montar=montar_c04,
    ),
    Cenario(
        codigo="C05",
        nome="Avaliação pendente",
        objetivo="Registrar avaliações na Mesa e consolidar a Etapa.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial="8 inscritos; prova distribuída à avaliação 1, 3 concluídas e 5 pendentes.",
        precondicoes=("Comissão constituída e alocada nas três Etapas.",),
        papeis=(f"Avaliação ({AVALIACAO_1})", f"Presidência ({PRESIDENCIA})"),
        proxima_acao="Avaliação 1: concluir as pendentes; Presidência: consolidar a prova.",
        resultado_esperado="Prova consolidada, com a eliminação de quem ficar abaixo de 6,0.",
        dependencias=(),
        montar=montar_c05,
    ),
    Cenario(
        codigo="C06",
        nome="Sorteio antes do congelamento",
        objetivo=(
            "Conferir as inscrições e congelar as relações do sorteio: a da ampla concorrência e "
            "a da cota PPP."
        ),
        tipo_de_selecao=_CURSO,
        metodo="Sorteio (Fonte de demonstração)",
        estado_inicial=(
            "Edital de sorteio PUBLICADO, 10 inscrições (3 declaram a cota PPP), inscrições "
            "encerradas."
        ),
        precondicoes=(
            "Comissão constituída.",
            "Quatro vagas para dez inscritos: três na ampla concorrência e uma na cota PPP.",
            "A cota se declara na inscrição, sem anexo; a autodeclaração é pedida na convocação.",
        ),
        papeis=(f"Presidência da comissão ({PRESIDENCIA})",),
        proxima_acao=(
            "Presidência: conferir e congelar a relação da ampla concorrência e, em seguida, a da "
            "cota PPP."
        ),
        resultado_esperado=(
            "Duas relações congeladas e publicadas: 10 participantes na ampla, 3 na cota."
        ),
        dependencias=("SORTEIO_FONTE_DE_DEMONSTRACAO=true no ambiente.",),
        montar=montar_c06,
        exige_fonte_de_demonstracao=True,
    ),
    Cenario(
        codigo="C07",
        nome="Sorteio pronto para execução",
        objetivo="Executar os dois sorteios, conferir o resultado e as listas.",
        tipo_de_selecao=_CURSO,
        metodo="Sorteio (Fonte de demonstração)",
        estado_inicial=(
            "Relações congeladas — 10 participantes na ampla concorrência e 3 na cota PPP; "
            "ocorrência ainda não observada."
        ),
        precondicoes=(
            "A fonte de demonstração responde na hora: não há extração futura a esperar.",
            "Os cotistas figuram nas duas listas, com número próprio em cada uma.",
        ),
        papeis=(f"Presidência da comissão ({PRESIDENCIA})",),
        proxima_acao=(
            "Presidência: observar a ocorrência e realizar o sorteio de cada lista — a mesma "
            "extração semeia as duas."
        ),
        resultado_esperado=(
            "Dois sorteios constituídos, com ordem, manifesto e verificação públicos; a "
            "comprovação da cota fica para a convocação."
        ),
        dependencias=("SORTEIO_FONTE_DE_DEMONSTRACAO=true no ambiente.",),
        montar=montar_c07,
        exige_fonte_de_demonstracao=True,
        limitacoes=(
            "A semente vem da Fonte de demonstração, e não da Loteria Federal: o resultado é "
            "reprodutível e serve só para treinamento (D-004).",
        ),
    ),
    Cenario(
        codigo="C08",
        nome="Resultado preliminar e recursos",
        objetivo="Interpor e julgar recursos contra o resultado preliminar.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial="Resultado PRELIMINAR divulgado; janela recursal de 5 dias aberta.",
        precondicoes=("Candidato 08 eliminado na prova, com motivo para recorrer.",),
        papeis=(
            "Candidato (portal)",
            "Julgador de recursos (papel do seletor)",
            f"Presidência ({PRESIDENCIA})",
        ),
        proxima_acao="Candidato: recorrer; Julgador: decidir; Presidência: cumprir a decisão.",
        resultado_esperado="Recurso julgado e, se deferido, a ordem sucessora.",
        dependencias=("Correio do ambiente para o código de acesso do candidato.",),
        montar=montar_c08,
        validade_dias=5,
    ),
    Cenario(
        codigo="C09",
        nome="Resultado definitivo",
        objetivo="Examinar o resultado definitivo e preparar a convocação.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas, com marco que não admite recurso",
        estado_inicial="Resultado DEFINITIVO divulgado; Etapa documental ainda não avaliada.",
        precondicoes=("O marco declara expressamente que não admite recurso.",),
        papeis=(f"Presidência ({PRESIDENCIA})", f"Gestor ({GESTAO})"),
        proxima_acao="Examinar listas e situações; habilitar na Etapa documental para convocar.",
        resultado_esperado="Etapa documental consolidada, com corte e apuração emitidos.",
        dependencias=(),
        montar=montar_c09,
    ),
    Cenario(
        codigo="C10",
        nome="Convocação",
        objetivo="Convocar candidatos para as vagas apuradas.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial=(
            "6 candidatos habilitados; faixa de corte e apuração emitidas; ninguém convocado."
        ),
        precondicoes=("Documentos da convocação: diploma, residência e autodeclaração da cota.",),
        papeis=(f"Presidência ({PRESIDENCIA})",),
        proxima_acao="Presidência: convocar e comunicar a convocação.",
        resultado_esperado="Convocações praticadas, com a lista de documentos de cada pessoa.",
        dependencias=(),
        montar=montar_c10,
    ),
    Cenario(
        codigo="C11",
        nome="Entrega documental",
        objetivo="Experimentar a entrega dos documentos da convocação, como candidato.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial=(
            "3 convocados comunicados: 01 sem entrega; 02 com o diploma devolvido como "
            "pendente; 03 com tudo entregue, aguardando conferência."
        ),
        precondicoes=("Prazo da convocação de 30 dias.",),
        papeis=("Candidato (portal)", f"Presidência ({PRESIDENCIA})"),
        proxima_acao="Candidatos 01 e 02: entregar e corrigir; Presidência: conferir.",
        resultado_esperado="Itens entregues e conferidos; convocação pronta para o desfecho.",
        dependencias=("Correio do ambiente para o código de acesso do candidato.",),
        montar=montar_c11,
        validade_dias=30,
    ),
    Cenario(
        codigo="C12",
        nome="Conferência documental",
        objetivo="Conferir documentos, um a um e em lote, e registrar o desfecho.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial=(
            "3 convocados com diploma e residência entregues e nada conferido; autodeclaração "
            "'não se aplica' a quem é da ampla."
        ),
        precondicoes=("Prazo da convocação de 30 dias.",),
        papeis=(f"Presidência ({PRESIDENCIA})",),
        proxima_acao="Presidência: conferir os itens, devolver um como pendente, desfechar.",
        resultado_esperado="Conferências registradas e desfecho de cada convocação.",
        dependencias=(),
        montar=montar_c12,
        validade_dias=30,
    ),
    Cenario(
        codigo="C13",
        nome="Retificação",
        objetivo="Retificar um Edital publicado e ver o efeito nos inscritos.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial="Edital PUBLICADO, inscrições abertas, 2 inscrições enviadas.",
        precondicoes=("Período de inscrições aberto por 30 dias a partir da geração.",),
        papeis=_EQUIPE_DA_PUBLICACAO,
        proxima_acao="Elaborador: criar a Retificação; Homologador e Publicador: concluir.",
        resultado_esperado="Retificação publicada e versão consolidada nova.",
        dependencias=(),
        montar=montar_c13,
        validade_dias=30,
    ),
    Cenario(
        codigo="C14",
        nome="Encerramento",
        objetivo="Ler as pendências finais e encerrar o Edital e o Processo.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas, com marco que não admite recurso",
        estado_inicial="Resultado DEFINITIVO divulgado; convocação não iniciada.",
        precondicoes=("Gestor tem processo:encerrar e edital:encerrar.",),
        papeis=(f"Gestor ({GESTAO}, ou qualquer identidade com o papel Gestor)",),
        proxima_acao="Gestor: abrir o encerramento, ler as advertências e encerrar.",
        resultado_esperado="Edital e Processo ENCERRADOS, com o histórico na trilha.",
        dependencias=(),
        montar=montar_c14,
    ),
    Cenario(
        codigo="C15",
        nome="Vagas não preenchidas",
        objetivo="Ver a apuração com menos habilitados que vagas, e a cota sem candidato.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos)",
        estado_inicial=(
            "3 inscritos para 4 vagas; 1 inabilitado na análise documental; corte e apuração "
            "emitidos."
        ),
        precondicoes=("Nenhum inscrito na cota.",),
        papeis=(f"Presidência ({PRESIDENCIA})",),
        proxima_acao="Presidência: ler a apuração e convocar os dois habilitados.",
        resultado_esperado="Duas convocações; vagas restantes apontadas como não preenchidas.",
        dependencias=(),
        montar=montar_c15,
    ),
    Cenario(
        codigo="C16",
        nome="Exportação à formalização",
        objetivo="Verificar e exportar, como o setor, os documentos das pessoas aptas.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos); documento só na inscrição",
        estado_inicial=(
            "3 convocados com aceite, aptos para formalização; definição dos documentos gravada "
            f"(a identificação); {FORMALIZACAO} com o papel Formalização e designada."
        ),
        precondicoes=(f"Entrar pela página de acesso com {FORMALIZACAO}, marcando Formalização.",),
        papeis=(f"Formalização ({FORMALIZACAO})", f"Presidência ({PRESIDENCIA})"),
        proxima_acao="Formalização: abrir o Edital, verificar e exportar o pacote.",
        resultado_esperado=(
            "Pacote baixado e registrado; o Centro conta as pessoas como disponibilizadas."
        ),
        dependencias=(),
        montar=montar_c16,
        provisiona_formalizacao=True,
        limitacoes=(
            "O pacote leva só a identificação: o aceite com documento da convocação exigiria "
            "conferência conforme, que o gerador não fabrica (D-010).",
        ),
    ),
    Cenario(
        codigo="C17",
        nome="Designação para a formalização",
        objetivo="Designar a pessoa do setor que vai receber os documentos do Edital.",
        tipo_de_selecao=_SELECAO,
        metodo="Notas (prova + títulos); documento só na inscrição",
        estado_inicial=(
            "3 convocados com aceite, aptos para formalização; definição gravada; "
            f"{FORMALIZACAO} com o papel Formalização e sem designação."
        ),
        precondicoes=(f"{FORMALIZACAO} tem o papel Formalização na unidade.",),
        papeis=("Administrador de acessos da unidade", f"Formalização ({FORMALIZACAO})"),
        proxima_acao=(
            f"Administrador de acessos: designar {FORMALIZACAO}; Formalização: ver o Edital."
        ),
        resultado_esperado="Designação vigente; o Centro deixa de dizer que ninguém recebe.",
        dependencias=(
            "Quem designa tem o papel Administrador de acessos, que o seletor de demonstração "
            "não oferece: pela demonstração, o exercício depende da revisão da 117 que dá a "
            "designação à presidência.",
        ),
        montar=montar_c17,
        provisiona_formalizacao=True,
    ),
)

POR_CODIGO = {cenario.codigo: cenario for cenario in CENARIOS}
