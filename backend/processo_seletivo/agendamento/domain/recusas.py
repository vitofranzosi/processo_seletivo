"""As frases da agenda da Etapa, transcritas de `contracts/recusas.md` (167, T-008, UX-766).

**Toda frase diz o que fazer**, e não só o que está errado (UX-766). As frases vêm do protótipo
aprovado, salvo onde a spec as fixa literalmente — e então vale a da spec, como a do cenário 4 da
US1, que os testes conferem palavra por palavra.

Uma função por frase, e não um dicionário de modelos: cada uma recebe o que a compõe com o nome do
que é, e o teste que a confere não precisa conhecer a ordem dos marcadores.
"""

from dataclasses import dataclass

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import (
    dia_curto,
    dia_por_extenso,
    faixa,
    horario_curto,
    periodo_por_extenso,
)
from processo_seletivo.shared.api.problems import DomainError


@dataclass(frozen=True)
class Recusa:
    codigo: str
    frase: str


def plural(quantidade, singular, plural_):
    return f"{quantidade} {singular if quantidade == 1 else plural_}"


# --- §1 a configuração ----------------------------------------------------------------------------


def duracao_nao_positiva():
    return Recusa(nomes.DURACAO_NAO_POSITIVA, "Informe a duração de cada atendimento, em minutos.")


def intervalo_negativo():
    return Recusa(
        nomes.INTERVALO_NEGATIVO,
        "O intervalo entre atendimentos não pode ser negativo. Use 0 para nenhum intervalo.",
    )


def sem_dia():
    return Recusa(nomes.SEM_DIA, "Acrescente ao menos um dia de atendimento.")


def sem_banca():
    return Recusa(nomes.SEM_BANCA, "Acrescente ao menos uma banca.")


def dia_fora_do_periodo(dia, periodo):
    return Recusa(
        nomes.DIA_FORA_DO_PERIODO,
        f"{dia_por_extenso(dia)} está fora do período da Etapa no cronograma publicado "
        f"({periodo_por_extenso(periodo)}). Escolha um dia dentro dele; mudar o período pede "
        "Retificação.",
    )


def janela_invertida(dia, inicio, fim):
    return Recusa(
        nomes.JANELA_INVERTIDA,
        f"Em {dia_curto(dia)}, a janela {faixa(inicio, fim)} termina antes de começar.",
    )


def janela_menor_que_a_duracao(dia, inicio, fim, duracao, *, com_dia):
    """A frase literal do cenário 4 da US1; com mais de um dia, o dia vem antes dela."""
    corpo = (
        f"a janela {faixa(inicio, fim)} não comporta um atendimento de {duracao} minutos. "
        "Amplie a janela ou reduza a duração."
    )
    frase = f"Em {dia_curto(dia)}, {corpo}" if com_dia else corpo[0].upper() + corpo[1:]
    return Recusa(nomes.JANELA_MENOR_QUE_A_DURACAO, frase)


def janelas_sobrepostas(dia, primeira, segunda):
    return Recusa(
        nomes.JANELAS_SOBREPOSTAS,
        f"Em {dia_curto(dia)}, as janelas {faixa(*primeira)} e {faixa(*segunda)} se sobrepõem. "
        "Ajuste uma delas.",
    )


def banca_sem_nome():
    return Recusa(nomes.BANCA_SEM_NOME, 'Dê um nome a cada banca, como "Banca 1".')


def bancas_com_o_mesmo_nome(nome):
    return Recusa(
        nomes.BANCAS_COM_O_MESMO_NOME,
        f'Duas bancas se chamam "{nome}". Os nomes aparecem para o candidato e precisam ser '
        "distintos.",
    )


def dia_repetido(dia):
    return Recusa(
        nomes.DIA_REPETIDO, f"{dia_curto(dia)} aparece duas vezes. Junte as janelas num dia só."
    )


@dataclass
class ConfiguracaoRecusada(DomainError):
    """A configuração inteira recusada, com **todos** os problemas (T-005, UX-766).

    É um `DomainError` como os outros — a tela e a API o tratam igual —, e carrega a lista, porque
    a comissão corrige tudo numa passada, e não um problema por tentativa.
    """

    problemas: tuple = ()


def configuracao_recusada(problemas):
    return ConfiguracaoRecusada(
        nomes.CONFIGURACAO_RECUSADA,
        " ".join(problema.frase for problema in problemas),
        422,
        problemas=tuple(problemas),
    )


# --- §3 a montagem --------------------------------------------------------------------------------


def horario_ocupado():
    return DomainError(
        nomes.HORARIO_OCUPADO,
        "Esse horário acabou de ser ocupado por outra pessoa da comissão, noutra sessão. A grade "
        "foi atualizada; escolha outro.",
        409,
    )


def pessoa_ja_agendada(nome, inicio):
    return DomainError(
        nomes.PESSOA_JA_AGENDADA,
        f"{nome} já tem horário, em {horario_curto(inicio)}. A grade foi atualizada.",
        409,
    )


def pessoa_nao_participa(nome, motivo):
    return DomainError(
        nomes.PESSOA_NAO_PARTICIPA,
        f"{nome} não participa desta Etapa: {_sem_ponto(motivo)}.",
        422,
    )


def horario_inexistente():
    return DomainError(
        nomes.HORARIO_INEXISTENTE,
        "Esse horário não existe mais na configuração. A grade foi atualizada.",
        409,
    )


def agenda_mudou_desde_a_previa():
    return DomainError(
        nomes.AGENDA_MUDOU_DESDE_A_PREVIA,
        "A agenda mudou desde a prévia. Veja a prévia nova antes de aplicar.",
        409,
    )


def sem_configuracao():
    return DomainError(
        nomes.SEM_CONFIGURACAO,
        "Esta Etapa ainda não tem agenda. Configure os dias, os horários e as bancas primeiro.",
        409,
    )


def sem_horario_para_liberar(nome):
    """Outra sessão liberou antes: a pessoa já está em "Sem horário", e a grade o mostra."""
    return DomainError(
        nomes.SEM_HORARIO_PARA_LIBERAR,
        f'{nome} já está em "Sem horário". A grade foi atualizada.',
        409,
    )


def agenda_publicada():
    """Preencher, agendar ou liberar com a agenda publicada (FR-7240)."""
    return DomainError(
        nomes.AGENDA_PUBLICADA,
        "A agenda já foi publicada. Para mudar uma pessoa, use Remarcar na agenda publicada.",
        409,
    )


# --- §1 depois da publicação (FR-7208, T-015) ---------------------------------------------------


def horario_publicado_removido(nome, protocolo, inicio, banca):
    return Recusa(
        nomes.HORARIO_PUBLICADO_REMOVIDO,
        f"A agenda já foi publicada, e {nome} ({protocolo}) tem horário em "
        f"{horario_curto(inicio)}, {banca}, que esta configuração removeria. Depois da "
        "publicação, só se acrescenta dia, janela ou banca; para mudar uma pessoa, use Remarcar.",
    )


def parametro_publicado_alterado(duracao, intervalo, forma):
    atendimento = "remoto" if forma == nomes.REMOTA else "presencial"
    return Recusa(
        nomes.PARAMETRO_PUBLICADO_ALTERADO,
        f"A agenda já foi publicada com {duracao} minutos e {intervalo} de intervalo, em "
        f"atendimento {atendimento}. Depois da publicação, só se acrescenta dia, janela ou banca.",
    )


# --- §4 a conferência ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Impedimento:
    """Um impedimento da publicação, com o caminho de corrigir (FR-7221, UX-766).

    `caminho` é o nome do destino — `montar`, `configurar` ou `unidades` —, e a tela o resolve; o
    domínio não conhece rota. `pessoas` é a lista nominal, quando há.
    """

    codigo: str
    titulo: str
    frase: str
    caminho: str
    rotulo_do_caminho: str
    pessoas: tuple = ()


def participantes_sem_horario(pessoas):
    quantas = len(pessoas)
    sujeito = plural(quantas, "pessoa está", "pessoas estão")
    alvo = "essa pessoa" if quantas == 1 else "essas pessoas"
    return Impedimento(
        nomes.PARTICIPANTES_SEM_HORARIO,
        f"{sujeito} sem horário",
        f"{sujeito} sem horário. Toda pessoa que participa da Etapa precisa de um horário antes "
        f"da publicação: a ausência tem consequência no Edital. Volte à montagem e agende {alvo}.",
        "montar",
        "Voltar à montagem",
        tuple(f"{pessoa.nome} ({pessoa.protocolo})" for pessoa in pessoas),
    )


def agendado_que_nao_participa(nome, protocolo, motivo):
    return Impedimento(
        nomes.AGENDADOS_QUE_NAO_PARTICIPAM,
        f"{nome} tem horário e não participa mais",
        f"{nome} ({protocolo}) tem horário, mas não participa mais da Etapa: "
        f"{_sem_ponto(motivo)}. Volte à montagem e libere o horário.",
        "montar",
        "Voltar à montagem",
    )


def configuracao_invalida(problemas):
    return Impedimento(
        nomes.CONFIGURACAO_INVALIDA,
        "A configuração tem problemas",
        "A configuração tem problemas: " + " ".join(problema.frase for problema in problemas),
        "configurar",
        "Ajustar a configuração",
    )


def banca_sem_local(banca, forma):
    falta = "endereço da sala" if forma == nomes.REMOTA else "local"
    return Impedimento(
        nomes.BANCA_SEM_LOCAL,
        f"{banca} sem {falta}",
        f"{banca} sem {falta}. Quem for atendido nessa banca não saberia aonde ir. Informe na "
        "configuração.",
        "configurar",
        "Ajustar a configuração",
    )


def sem_autoridade_vigente():
    return Impedimento(
        nomes.SEM_AUTORIDADE_VIGENTE,
        "Sem autoridade signatária vigente",
        "A unidade do Edital não tem autoridade signatária vigente. Peça ao Administrador "
        'institucional que registre uma na tela "Unidades".',
        "unidades",
        "Unidades",
    )


ETAPA_SEM_EVENTO = (
    "Esta Etapa não tem período publicado no cronograma; os dias não foram conferidos contra ele."
)


def publicacao_impedida(impedimentos):
    return DomainError(
        nomes.PUBLICACAO_IMPEDIDA,
        " ".join(impedimento.frase for impedimento in impedimentos),
        409,
    )


def agenda_mudou_desde_a_conferencia():
    return DomainError(
        nomes.AGENDA_MUDOU_DESDE_A_CONFERENCIA,
        "A agenda mudou desde esta conferência. Confira de novo.",
        409,
    )


def veiculo_nao_escolhido():
    return DomainError(
        nomes.VEICULO_NAO_ESCOLHIDO,
        "Escolha onde a agenda é publicada: na página pública do GPS, ou fora dele.",
        422,
        campo="veiculo",
    )


def declaracao_do_veiculo_ausente():
    return DomainError(
        nomes.DECLARACAO_DO_VEICULO_AUSENTE,
        "Diga o item do Edital que admite a página pública do GPS como veículo da publicação.",
        422,
        campo="declaracao",
    )


def publicacao_externa_incompleta():
    return DomainError(
        nomes.PUBLICACAO_EXTERNA_INCOMPLETA,
        "Diga onde e quando a agenda foi publicada fora do GPS.",
        422,
        campo="onde",
    )


def autoridade_invalida():
    return DomainError(
        nomes.AUTORIDADE_INVALIDA,
        "A autoridade escolhida não está vigente na unidade do Edital. Escolha outra.",
        422,
        campo="autoridade",
    )


def autoridade_nao_escolhida():
    """A frase do protótipo para o campo vazio: diz o que fica gravado, e não só que falta."""
    return DomainError(
        nomes.AUTORIDADE_INVALIDA,
        "Escolha a autoridade signatária: o nome e o cargo ficam gravados na publicação.",
        422,
        campo="autoridade",
    )


def fora_do_periodo_vigente(quantos):
    if quantos == 1:
        return (
            "O Evento da Etapa foi retificado depois da publicação, e 1 horário publicado está "
            "fora do período vigente. Ele continua valendo como foi publicado."
        )
    return (
        f"O Evento da Etapa foi retificado depois da publicação, e {quantos} horários publicados "
        "estão fora do período vigente. Eles continuam valendo como foram publicados."
    )


# --- §2 e §3 as frases que informam, sem recusar --------------------------------------------------


def sobra_no_fim(janela):
    return (
        f"Em {dia_curto(janela.dia)}, o último atendimento da janela "
        f"{faixa(janela.inicio, janela.fim)} termina às {janela.ultimo_fim:%H:%M}: sobram "
        f"{janela.sobra} minutos, que não cabem outro atendimento."
    )


def lista_aberta(participantes):
    return (
        "A Etapa anterior ainda não tem Resultado: as "
        f"{plural(participantes, 'pessoa', 'pessoas')} são as que participam hoje, e a lista "
        "ainda pode mudar."
        if participantes != 1
        else "A Etapa anterior ainda não tem Resultado: a pessoa que participa hoje pode não ser a "
        "única, e a lista ainda pode mudar."
    )


def agendada_a_mao(nome, inicio, banca):
    return f"{nome} agendada em {horario_curto(inicio)}, {banca}."


def mudanca(nome, de, para):
    return f"{nome} passou de {horario_curto(de)} para {horario_curto(para)}."


def liberacao(nome):
    return f'Horário liberado. {nome} voltou para "Sem horário".'


def aplicada(quantas):
    return "1 pessoa recebeu horário." if quantas == 1 else f"{quantas} pessoas receberam horário."


def nao_participa_mais(nome, motivo):
    return (
        f"{nome} tem horário, mas não participa mais da Etapa: {_sem_ponto(motivo)}. Libere o "
        "horário."
    )


def devolvidos_pela_configuracao(nomes_, quando):
    quantas = len(nomes_)
    sujeito = (
        "1 pessoa voltou" if quantas == 1 else f"{quantas} pessoas voltaram"
    )  # FR-7208: diz quem
    return (
        f'{sujeito} para "Sem horário" porque a configuração de {quando:%d/%m} às {quando:%H:%M} '
        f"removeu o horário {'dela' if quantas == 1 else 'delas'}: {', '.join(nomes_)}."
    )


def configuracao_salva(devolvidos):
    if not devolvidos:
        return (
            "Configuração salva. A agenda continua em rascunho: nada é público até você conferir "
            "e publicar."
        )
    quantas = len(devolvidos)
    sujeito = "1 pessoa voltou" if quantas == 1 else f"{quantas} pessoas voltaram"
    return (
        f'Configuração salva, e {sujeito} para "sem horário", porque o horário '
        f"{'dela' if quantas == 1 else 'delas'} deixou de existir: {', '.join(devolvidos)}."
    )


def completa(participantes):
    return (
        "A única pessoa que participa tem horário."
        if participantes == 1
        else f"Todas as {participantes} pessoas têm horário."
    )


def _sem_ponto(texto):
    return (texto or "").rstrip().rstrip(".")
