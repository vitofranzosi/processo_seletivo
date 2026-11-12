"""A vaga sem quem a ocupe: a condição, os impedimentos e a situação, puros (155, R-004).

**Uma conta só, para as três telas e para o comando** (155, D-004, FR-6301). A ocupação, o Centro e
a convocação dizem a mesma situação, e a declaração de vaga não preenchida a reavalia sob a trava:
duas contas divergiriam na primeira regra nova, e a tela ofereceria o ato que o comando recusa
(FR-6302).

**Nada aqui toca banco**, pela razão de `apuracao.py`: os fatos chegam prontos — as posições da
ordem, os efeitos da `019`, quem a faixa alcança e o que a divulgação, os recursos e a condução
disseram.

**Esta entrega lê a condição e não move vaga** (155, "Esta entrega"). Onde o Edital declara a
reversão, quem a aplica continua sendo a apuração da lista, pela regra de antes da `155`
(`reversao.quantidade_a_reverter`); a conta daqui só diz por que a vaga ainda não saiu. O ato que a
destina por conta própria, com a condição de cada gatilho (FR-6305, FR-6308), ficou para a próxima
entrega, preservada na branch `claude/155-destinacao-completa`.
"""

from collections import namedtuple

from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.ocupacao.domain import nomes

# --- Os estados da vaga sem quem a ocupe (data-model, "Estados") --------------------------------
# **Derivados, e não gravados**: a situação muda com o mundo em volta (um desfecho, um recurso, a
# publicação do definitivo), e guardá-la exigiria `UPDATE` numa tabela append-only.
SEM_VAGA_A_DESTINAR = "sem_vaga_a_destinar"
NAO_PREENCHIDA_DISPONIVEL = "nao_preenchida_disponivel"
IMPEDIDA = "impedida"
# **A vaga da reserva que o Edital manda reverter e que a apuração ainda não cedeu.** Nenhum ato
# é oferecido: a reversão é da apuração, e a declaração de não preenchida é recusada onde o Edital
# declara para onde a vaga vai (FR-6327). O estado existe para que a tela diga por que a vaga não
# sai e qual é o próximo passo, em vez de calar ou de oferecer o que o comando recusaria (FR-6302).
REVERSAO_PELA_APURACAO = "reversao_pela_apuracao"

# --- Os impedimentos da FR-6306 -----------------------------------------------------------------
# A ordem é a do caminho, e não a da gravidade — a de `publicabilidade._impedimento_da_definitiva`:
# quem lê a recusa recebe o próximo passo. Primeiro o que é da divulgação (o resultado e o prazo),
# depois os recursos, depois o que é de quem conduz, e por último a apuração.
RESULTADO_NAO_DEFINITIVO = "resultado_nao_definitivo"
PRAZO_RECURSAL_ABERTO = "prazo_recursal_aberto"
RECURSO_PENDENTE = "recurso_pendente"
PRAZO_DA_ELIMINACAO_ABERTO = "prazo_da_eliminacao_aberto"
RECURSO_DA_ELIMINACAO_PENDENTE = "recurso_da_eliminacao_pendente"
CHAMADA_EM_CURSO = "chamada_em_curso"
OCUPACAO_PELA_AMPLA_PODE_MUDAR = "ocupacao_pela_ampla_pode_mudar"
APURACAO_OBSOLETA = "apuracao_obsoleta"

#: `ate` é o instante em que o impedimento pode acabar, quando há um (FR-6303): "aguarde" sem data
#: manda a pessoa tentar de novo às cegas.
Impedimento = namedtuple("Impedimento", "codigo frase ate")


def chave(identificador):
    """A identidade comparável — a mesma normalização da apuração, e não uma segunda."""
    return calculo.chave_da_inscricao(identificador)


def excluidos_por_efeito(efeitos_lidos):
    """Quem saiu do recorte por desfecho excludente, pelo **último** efeito de cada pessoa.

    É a regra de `apuracao.ocupantes`: a pessoa indeferida e depois regularizada voltou, e contá-la
    como saída pela primeira linha a tiraria da reserva que a recebeu de volta.
    """
    ultimo = {}
    for especie, inscricao in efeitos_lidos:
        ultimo[chave(inscricao)] = especie
    return {pessoa for pessoa, especie in ultimo.items() if especie == nomes.EFEITO_EXCLUSAO}


def incluidos_por_efeito(efeitos_lidos):
    """Quem entrou no recorte por desfecho que inclui, pelo último efeito de cada pessoa.

    Na ampla, é quem **confirmou** a ocupação por ela (155, R-004): o efeito de inclusão é da
    ocupação, e distinguir o titular de quem confirmou não exige ler a condução.
    """
    ultimo = {}
    for especie, inscricao in efeitos_lidos:
        ultimo[chave(inscricao)] = especie
    return {pessoa for pessoa, especie in ultimo.items() if especie == nomes.EFEITO_INCLUSAO}


def quem_ainda_pode_ocupar(
    *,
    posicoes,
    excluidos=(),
    ocupam_a_ampla_confirmados=(),
    alcancaveis=None,
    inabilitados=(),
    ocupantes=(),
):
    """Quem, na ordem vigente da reserva, ainda pode ocupar uma vaga dela — na ordem (FR-6304).

    `posicoes` é `[(inscricao, posicao)]` da ordem vigente. Ainda pode ocupar quem:

    - **tem posição** — o eliminado antes da ordem fica com a posição vazia (V-5);
    - **não saiu por desfecho excludente** (`excluidos`) — a desistência de V-1;
    - **não ocupa a ampla com a ocupação confirmada** (`ocupam_a_ampla_confirmados`) — V-4. O
      titular da ampla que ainda não confirmou **conta**: a ocupação dele pela ampla ainda pode
      mudar, e é impedimento à parte (FR-6306);
    - **não foi inabilitado** na Etapa que o corte governa, com o prazo e os recursos dela fechados
      (`inabilitados`) — V-2, tratada como eliminação (155, D-007);
    - **é alcançável** (`alcancaveis`) — dentro da faixa vigente; `None` quando o Edital admite
      continuação, e então a ordem inteira.

    **Quem já ocupa a reserva fica de fora** (`ocupantes`): a pergunta é se há alguém para a vaga
    que sobra, e o titular habilitado já ocupa outra. A primeira forma desta conta, a da `095`,
    comparava o número de posições com o de ocupadas, e com isso contava como "quem ocupar" quem
    tinha saído por desfecho — a reserva sem mais ninguém nunca esgotava (V-1).
    """
    fora = (
        {chave(i) for i in excluidos}
        | {chave(i) for i in ocupam_a_ampla_confirmados}
        | {chave(i) for i in inabilitados}
        | {chave(i) for i in ocupantes}
    )
    alcance = None if alcancaveis is None else {chave(i) for i in alcancaveis}
    restantes, vistas = [], set()
    for inscricao, _ in sorted(
        ((i, p) for i, p in posicoes if p is not None), key=lambda par: par[1]
    ):
        pessoa = chave(inscricao)
        if pessoa in vistas or pessoa in fora:
            continue
        if alcance is not None and pessoa not in alcance:
            continue
        vistas.add(pessoa)
        restantes.append(inscricao)
    return restantes


def ainda_podem_ocupar(**fatos):
    """Quantas pessoas ainda podem ocupar a vaga que sobra (FR-6304). Zero é a reserva esgotada."""
    return len(quem_ainda_pode_ocupar(**fatos))


def impedimentos(fatos):
    """`[Impedimento(codigo, frase, ate)]` da FR-6306, na ordem do caminho. Vazio é nenhum.

    `fatos` é um dicionário — os externos chegam da interface, os da ocupação do seletor:

    - `natureza_do_resultado`: a do resultado vigente do marco, `None` quando nada foi divulgado;
    - `prazo_recursal_ate`: quando o prazo do marco fecha, se ainda corre;
    - `recursos_pendentes`: quantos recursos sobre o marco estão sem decisão;
    - `prazo_da_eliminacao_ate` e `recursos_da_eliminacao`: o mesmo, sobre a eliminação de alguém da
      ordem da reserva na Etapa que o corte governa — só pesam quando há eliminado nela;
    - `chamadas_em_curso`: as pessoas da reserva chamadas para a vaga e ainda sem desfecho, como
      `[{"rotulo", "ate"}]`;
    - `ocupam_a_ampla_sem_confirmacao`: quantas pessoas da reserva ocupam a ampla sem a ocupação
      confirmada;
    - `apuracao_obsoleta`: se a apuração vigente da reserva tem causa de obsolescência.

    **Resultado não divulgado é não definitivo**: a vaga só é "sem quem a ocupe" depois de a lista
    ser definitiva, e ausência de publicação não é publicação definitiva.
    """
    achados = []
    if fatos.get("natureza_do_resultado") != "DEFINITIVA":
        achados.append(
            Impedimento(
                RESULTADO_NAO_DEFINITIVO,
                "o resultado deste marco ainda não é definitivo"
                if fatos.get("natureza_do_resultado")
                else "o resultado deste marco ainda não foi divulgado",
                None,
            )
        )
    if fatos.get("prazo_recursal_ate"):
        achados.append(
            Impedimento(
                PRAZO_RECURSAL_ABERTO,
                "o prazo de recurso contra o resultado deste marco ainda corre",
                fatos["prazo_recursal_ate"],
            )
        )
    if fatos.get("recursos_pendentes"):
        achados.append(
            Impedimento(
                RECURSO_PENDENTE,
                f"{_contagem(fatos['recursos_pendentes'], 'recurso', 'recursos')} sobre este "
                "marco ainda sem decisão",
                None,
            )
        )
    if fatos.get("prazo_da_eliminacao_ate"):
        achados.append(
            Impedimento(
                PRAZO_DA_ELIMINACAO_ABERTO,
                "o prazo de recurso contra a eliminação de alguém desta lista ainda corre",
                fatos["prazo_da_eliminacao_ate"],
            )
        )
    if fatos.get("recursos_da_eliminacao"):
        achados.append(
            Impedimento(
                RECURSO_DA_ELIMINACAO_PENDENTE,
                f"{_contagem(fatos['recursos_da_eliminacao'], 'recurso', 'recursos')} contra a "
                "eliminação de alguém desta lista ainda sem decisão",
                None,
            )
        )
    chamadas = list(fatos.get("chamadas_em_curso") or [])
    if chamadas:
        # **Diz qual chamada impede** (US1.4), e não só que há uma: a pessoa que lê precisa saber
        # quem está respondendo pela vaga, e até quando.
        rotulos = "; ".join(c.get("rotulo") or "" for c in chamadas if c.get("rotulo"))
        ate = min((c["ate"] for c in chamadas if c.get("ate")), default=None)
        achados.append(
            Impedimento(
                CHAMADA_EM_CURSO,
                f"há {_contagem(len(chamadas), 'pessoa chamada', 'pessoas chamadas')} para esta "
                "vaga, com prazo em curso" + (f": {rotulos}" if rotulos else ""),
                ate,
            )
        )
    if fatos.get("ocupam_a_ampla_sem_confirmacao"):
        quantas = fatos["ocupam_a_ampla_sem_confirmacao"]
        achados.append(
            Impedimento(
                OCUPACAO_PELA_AMPLA_PODE_MUDAR,
                f"{_contagem(quantas, 'pessoa', 'pessoas')} desta lista "
                + ("ocupa" if quantas == 1 else "ocupam")
                + " vaga da ampla concorrência sem a ocupação confirmada, e a ocupação pela ampla "
                "ainda pode mudar",
                None,
            )
        )
    if fatos.get("apuracao_obsoleta"):
        achados.append(
            Impedimento(
                APURACAO_OBSOLETA,
                "a apuração desta lista está obsoleta: emita a seguinte antes",
                None,
            )
        )
    return achados


def situacao(
    *,
    declaracao,
    lista_id,
    saldo,
    restantes=(),
    pendentes=(),
    impedimentos=(),
):
    """O estado da vaga sem quem a ocupe, com o que a tela precisa para dizê-lo (155, R-008).

    - `declaracao`: a espécie de reversão que o Perfil declara (`reversao.declarada`), `None`
      quando nada;
    - `lista_id`: o recorte, `None` na linha geral;
    - `saldo`: as vagas a ocupar da apuração vigente, `None` sem apuração;
    - `restantes`: quem ainda pode ocupar (`quem_ainda_pode_ocupar`);
    - `pendentes`: os dos `restantes` cuja ocupação está em suspenso — chamados com prazo em curso,
      os que ocupam a ampla sem confirmação e os eliminados com recurso possível. Eles contam como
      quem ainda pode ocupar (FR-6304), e a razão de a vaga não sair é o impedimento deles, e não
      "chame o próximo".

    **A ordem das perguntas** é a que impede a tela de oferecer o que o comando recusa: sem vaga a
    ocupar não há nada a dizer; com alguém livre na ordem, o caminho é chamá-lo; com reversão
    declarada na reserva, a vaga é da apuração, e nenhum ato é oferecido; e só então o impedimento,
    que separa a vaga sem quem a ocupe da que ainda pode ser ocupada.
    """
    restantes = list(restantes)
    pendentes = {chave(i) for i in pendentes}
    livres = [i for i in restantes if chave(i) not in pendentes]
    base = {
        "declaracao": declaracao,
        "listaId": lista_id,
        "quantidade": 0,
        "aindaPodemOcupar": len(restantes),
        "livres": len(livres),
        "impedimentos": list(impedimentos),
    }
    if saldo is None or int(saldo) <= 0:
        return {**base, "estado": SEM_VAGA_A_DESTINAR}
    if livres:
        return {**base, "estado": SEM_VAGA_A_DESTINAR}
    if declaracao in nomes.ESPECIES_DE_REVERSAO and lista_id is not None:
        return {**base, "estado": REVERSAO_PELA_APURACAO, "quantidade": int(saldo)}
    if impedimentos or restantes:
        # `restantes` sem livres e sem impedimento não acontece com os fatos completos — os
        # pendentes nascem dos mesmos fatos que os impedimentos —, mas a guarda fica: oferecer a
        # declaração com alguém ainda na reserva é o defeito que esta feature corrige (V-1).
        return {**base, "estado": IMPEDIDA}
    # Sem reversão declarada, ou na linha geral: a declaração de vaga não preenchida (155, D-006,
    # D-014).
    return {**base, "estado": NAO_PREENCHIDA_DISPONIVEL, "quantidade": int(saldo)}


def _contagem(quantidade, singular, plural):
    return f"{quantidade} {singular if quantidade == 1 else plural}"


__all__ = [
    "IMPEDIDA",
    "Impedimento",
    "NAO_PREENCHIDA_DISPONIVEL",
    "REVERSAO_PELA_APURACAO",
    "SEM_VAGA_A_DESTINAR",
    "ainda_podem_ocupar",
    "excluidos_por_efeito",
    "impedimentos",
    "incluidos_por_efeito",
    "quem_ainda_pode_ocupar",
    "situacao",
]
