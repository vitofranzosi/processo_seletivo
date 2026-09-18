"""Quem entra no arquivo — escolhido explicitamente, e nunca por omissão (`FR-433`, `FR-434`).

**Não existe *"exportar tudo"***, e a ausência é a minimização em ato: o arquivo tem o conjunto que
alguém escolheu e nomeou. Uma população padrão implícita faria a tela entregar, a um clique
distraído, o dado pessoal de todo mundo que já passou pelo Edital.

**Duas espécies, e as duas são atos que já existem no domínio**: os convocados de um marco de
classificação, e o conjunto de um resultado divulgado. Nenhuma das duas é inventada aqui — a
exportação **lê** (`FR-449`).

**Cada pessoa vem com a versão do Edital sob a qual o ato que a alcançou foi praticado.** Não é
detalhe de implementação: é o Princípio II — *"regras atuais NÃO PODEM substituir regras
históricas"*. Quem foi convocado sob a versão 3 é exportado com o Perfil, a Modalidade e o polo da
versão 3, ainda que a 4 tenha retificado os três. Ler a norma de hoje faria a Retificação alterar,
em silêncio, o arquivo de quem já foi chamado — e, no caso de uma Modalidade removida, faria a
geração **recusar** uma pessoa que concorreu legitimamente por ela.

**Só requerimentos enviados** (`FR-434`): rascunho não é declaração, e quem falta é **nomeado** na
recusa em vez de sumir do arquivo (`FR-435`). Um arquivo com a linha faltando é pior que nenhum
arquivo: ele parece completo.
"""

from dataclasses import dataclass

from processo_seletivo.convocacao.application.selectors import desfecho_de, vigentes
from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.divulgacao.models import (
    Natureza,
    PublicacaoResultado,
    SituacaoDivulgada,
)
from processo_seletivo.matriculas.domain import nomes
from processo_seletivo.ocupacao.domain import nomes as ocupacao_nomes
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.requerimentos.application.exigencia import vigente_de
from processo_seletivo.requerimentos.domain import disponibilidade
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.shared.api.problems import DomainError


@dataclass(frozen=True)
class Populacao:
    """Um conjunto de pessoas que alguém escolheu e que tem nome.

    `rotulo` existe para o registro da geração e para a tela: quem ler o registro meses depois não
    deve precisar resolver um UUID para entender o que foi exportado.
    """

    especie: str
    referencia: str
    rotulo: str


@dataclass(frozen=True)
class Alcancado:
    """Uma pessoa da população, e **sob qual versão do Edital** o ato que a alcançou foi praticado.

    As duas viajam juntas porque separá-las é o defeito: uma lista de Inscrições sem a versão de
    cada uma obriga quem a consome a escolher uma norma, e a escolha natural — a vigente — é a
    errada (Princípio II).
    """

    inscricao: object
    versao_id: str


def exige_requerimento(edital) -> bool:
    """Este certame pede Requerimento de Matrícula?

    **É esta declaração que confina a feature a processos de alunos**, e a razão está escrita no
    próprio modelo do Edital (`029`, `D-002`): o sistema não tem taxonomia de natureza do Processo,
    e criá-la seria inventar um eixo que nenhuma outra feature consome. Um Edital de tutores,
    bolsistas ou servidores simplesmente **não declara** — e nele a capacidade não existe.

    **A versão é a vigente, e aqui ela é a certa**: a pergunta é *"este certame pede
    requerimento?"* — sobre o Edital agora, e não sobre um ato praticado no passado.
    """
    try:
        conteudo = effective_version(edital_id=edital.id).content
    except DomainError:
        return False
    return bool(disponibilidade.momento_declarado(conteudo))


def exigir_requerimento_declarado(edital) -> None:
    """Recusa a exportação num certame que não coleta requerimento (§9, *Edge Cases*).

    **E a recusa diz isso, em vez de nomear quem "falta"** (`UX-061`). Sem esta guarda, um Edital de
    servidores com convocados chegaria à `FR-435` e listaria todo mundo como se cada pessoa tivesse
    deixado de declarar algo — quando ninguém deixou: o certame nunca pediu. A frase certa é a
    diferença entre *"cobre estas pessoas"* e *"você está no Edital errado"*.
    """
    if not exige_requerimento(edital):
        raise DomainError(
            nomes.NAO_EXIGIDO,
            f"O Edital {edital.number}/{edital.year} não pede Requerimento de Matrícula, e a "
            "exportação lê o que foi declarado nele. Certames que não coletam o requerimento — de "
            "servidores, bolsistas ou tutores — não têm o que exportar.",
            422,
        )


def opcoes(edital) -> list:
    """As populações escolhíveis deste Edital, para a tela oferecer.

    **A lista pode vir vazia, e isso é informação**: um Edital sem convocação e sem resultado
    definitivo vigente não tem quem matricular, e dizer isso é melhor do que oferecer um botão que
    recusa.
    """
    return [*_marcos_com_convocados(edital), *_resultados_divulgados(edital)]


def _marcos_com_convocados(edital) -> list:
    """Um item por marco em que alguém foi chamado.

    O nome vem do **conteúdo publicado**, e não da linha de elaboração: é a identidade estável que
    sobrevive à Retificação, pela razão que a `015` e a `019` já registram.

    **Aqui a versão vigente é a certa**, e é o único lugar em que ela é: o que se monta é o
    **rótulo** que a tela mostra agora. O conteúdo de cada linha do arquivo continua vindo da versão
    do ato que alcançou a pessoa.
    """
    chamados = {
        str(marco)
        for marco in Convocacao.objects.filter(edital=edital)
        .values_list("marco_id", flat=True)
        .distinct()
    }
    if not chamados:
        return []
    conteudo = effective_version(edital_id=edital.id).content
    encontrados = []
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) in chamados:
                encontrados.append(
                    Populacao(
                        nomes.CONVOCACAO,
                        str(marco.get("id")),
                        f"Convocados — {perfil.get('name', '')} · {marco.get('name', '')}",
                    )
                )
    return encontrados


def _resultados_divulgados(edital) -> list:
    """Os resultados **definitivos e vigentes**. Nem toda publicação serve para matricular.

    **Preliminar não entra** (`D-007` da `017`): ele existe para ser contestado, e o prazo recursal
    pode reordenar quem está dentro. Exportar dele levaria ao Registro Acadêmico uma lista que o
    julgamento de um recurso ainda pode mudar — e a matrícula, uma vez feita, não se desfaz por
    reordenação.

    **Publicação sucedida não entra**: correção é sucessão, e a sucedida continua legível no
    histórico justamente por **não** ser a que vale. Oferecer as duas faria quem conduz escolher,
    numa lista, entre o resultado e a versão dele que já foi corrigida.
    """
    sucedidas = set(
        PublicacaoResultado.objects.filter(
            edital=edital, publicacao_anterior__isnull=False
        ).values_list("publicacao_anterior_id", flat=True)
    )
    return [
        Populacao(
            nomes.RESULTADO,
            str(publicacao.id),
            f"Resultado definitivo divulgado em {publicacao.publicado_em.strftime('%d/%m/%Y')}",
        )
        for publicacao in PublicacaoResultado.objects.filter(
            edital=edital, natureza=Natureza.DEFINITIVA
        ).order_by("publicado_em")
        if publicacao.id not in sucedidas
    ]


def escolher(edital, especie: str, referencia: str) -> Populacao:
    """A população nomeada, ou a recusa de quem não escolheu (`FR-433`).

    **A recusa é da aplicação, e a tela apenas a antecipa** (Princípio IV): quem montar o `POST` à
    mão, sem escolher, encontra aqui a mesma resposta que o botão desabilitado dá. E quem apontar
    para um resultado preliminar, sucedido ou de outro Edital não o encontra nesta lista — a
    recusa é a mesma de quem apontou para nada.
    """
    if not especie or not referencia:
        raise DomainError(
            nomes.POPULACAO_NAO_ESCOLHIDA,
            "Escolha quem entra no arquivo: os convocados de um marco, ou o conjunto de um "
            "resultado definitivo. Não há população padrão.",
            422,
        )
    for opcao in opcoes(edital):
        if opcao.especie == especie and opcao.referencia == str(referencia):
            return opcao
    raise DomainError(
        nomes.POPULACAO_NAO_ESCOLHIDA,
        "A população escolhida não pertence a este Edital, ou não é um conjunto do qual se "
        "matricula: resultado preliminar e publicação já corrigida não são oferecidos.",
        404,
    )


def _convocados(edital, marco_id) -> list:
    """Quem foi chamado naquele marco e continua a caminho da matrícula.

    **Quem saiu não entra**, e essa é a diferença entre um recorte útil e um beco: desistência,
    indeferimento, não atendimento, inércia e reclassificação **excluem** a pessoa do conjunto de
    ocupantes — e quem saiu nunca vai enviar requerimento, de modo que incluí-la recusaria a geração
    para sempre, por uma ausência que é o desfecho funcionando.

    **Quem ainda não respondeu entra.** A chamada está em aberto, a pessoa ainda pode declarar, e é
    justamente sobre ela que a `FR-435` fala: a recusa a nomeia, e quem conduz decide se espera ou
    se registra o desfecho.

    **Só as vigentes**: correção é sucessão, e a convocação sucedida continua legível no histórico
    sem entrar duas vezes no arquivo.
    """
    convocacoes = Convocacao.objects.filter(edital=edital, marco_id=marco_id).prefetch_related(
        "desfechos", "sucessoras"
    )
    conjunto = {}
    for convocacao in vigentes(convocacoes):
        desfecho = desfecho_de(convocacao)
        if desfecho is not None:
            efeito = convocacao_nomes.EFEITO_POR_DESFECHO.get(desfecho.especie)
            if efeito == ocupacao_nomes.EFEITO_EXCLUSAO:
                continue
        conjunto[convocacao.inscricao_id] = convocacao
    return list(conjunto.values())


def alcancados_de(edital, populacao: Populacao) -> list:
    """As pessoas da população, cada uma com a versão do ato que a alcançou.

    A ordem daqui **não** é a do arquivo — essa é decidida em `exportar.py` (`FR-446`) —, mas ela
    precisa ser estável para que a recusa nomeie quem falta sempre na mesma ordem.

    **Do resultado entra quem foi classificado.** `SEM_POSICAO` é a situação de quem o ato
    considerou e **não** posicionou: ele está na publicação porque tem direito de ler a própria
    situação, e não porque vai se matricular. Exportá-lo mandaria ao Registro Acadêmico gente que
    o certame não selecionou.
    """
    if populacao.especie == nomes.CONVOCACAO:
        alcancados = [
            # A versão que **aquela chamada** citou. Duas convocações do mesmo marco podem citar
            # versões diferentes, quando uma Retificação acontece entre elas — e cada pessoa é
            # exportada sob a norma que a alcançou.
            Alcancado(convocacao.inscricao, str(convocacao.versao_id))
            for convocacao in _convocados(edital, populacao.referencia)
        ]
    else:
        publicacao = PublicacaoResultado.objects.select_related("ato").get(pk=populacao.referencia)
        # A versão do **ato de ordenação** que a publicação divulgou: é a norma sob a qual a ordem
        # foi constituída, e é ela que diz o que cada Perfil e cada Modalidade eram naquele dia.
        versao_id = str(publicacao.ato.versao_id)
        alcancados = [
            Alcancado(situacao.inscricao, versao_id)
            for situacao in SituacaoDivulgada.objects.filter(
                publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.CLASSIFICADA
            ).select_related("inscricao")
        ]
    return sorted(alcancados, key=lambda alcancado: alcancado.inscricao.protocolo)


@dataclass(frozen=True)
class Declaracoes:
    """O requerimento vigente de cada pessoa da população, e quem não tem nenhum enviado."""

    por_inscricao: dict
    faltando: tuple


def declaracoes_de(alcancados) -> Declaracoes:
    """O requerimento **enviado** e vigente de cada pessoa (`FR-434`).

    **Rascunho não entra, e a distinção é a feature inteira.** Um rascunho é o que alguém começou a
    preencher; declarado é o que a pessoa enviou e assinou. Exportar rascunho levaria ao Registro
    Acadêmico dado que ninguém declarou.
    """
    por_inscricao = {}
    faltando = []
    for alcancado in alcancados:
        requerimento = vigente_de(alcancado.inscricao)
        if requerimento is None or requerimento.status != requerimento_nomes.ENVIADO:
            faltando.append(alcancado.inscricao)
            continue
        por_inscricao[alcancado.inscricao.id] = requerimento
    return Declaracoes(por_inscricao, tuple(faltando))


def exigir_completude(populacao: Populacao, alcancados, declaracoes: Declaracoes) -> None:
    """Recusa a geração quando falta gente ou falta declaração (`FR-435`, `UX-061`).

    **A recusa diz o que falta e de quem**, nunca *"não foi possível gerar"*: quem conduz precisa
    saber se cobra a pessoa, se registra um desfecho ou se escolheu a população errada.

    **População vazia recusa em vez de gerar um arquivo de zero linhas** (§9, *Edge Cases*). Um
    arquivo vazio parece um arquivo pronto, e alguém o importaria antes de perceber.
    """
    if not alcancados:
        raise DomainError(
            nomes.POPULACAO_VAZIA,
            f"«{populacao.rotulo}» não tem ninguém. Nada foi gerado: um arquivo de zero linhas "
            "pareceria um arquivo pronto.",
            422,
        )
    if declaracoes.faltando:
        quem = ", ".join(
            f"{inscricao.nome} ({inscricao.protocolo})" for inscricao in declaracoes.faltando
        )
        raise DomainError(
            nomes.DECLARACAO_FALTANDO,
            f"Falta o Requerimento de Matrícula enviado de: {quem}. Rascunho não é declaração, e o "
            "arquivo não é gerado com a linha faltando.",
            422,
        )
