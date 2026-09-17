"""A resposta da política, traduzida para o vocabulário da tela (029, `US2`, `FR-405`).

**Este módulo apenas traduz.** Ele não relê a declaração do Edital, não chama `chamada_em_aberto` e
não consulta o banco: recebe a `Disponibilidade` pronta e a converte em palavras. A razão é a que o
resto desta feature já pratica — duas leituras da mesma pergunta divergem na primeira mudança, e
quem paga é o candidato, que lê na tela um estado que o comando não reconhece.

**Os cinco estados não são coluna, e isso é decisão.** *Não aplicável*, *ainda indisponível* e
*disponível* derivam da declaração do Edital lida contra a ausência de linha vigente; coluna para
eles exigiria manter estado que ninguém escreve, e ela ficaria errada no instante em que a
convocação mudasse sem que nada tocasse o requerimento. É como a ocupação e a convocação já derivam
vigência.

**A distinção que este módulo existe para preservar**: *"este certame não pede requerimento"* não é
*"ainda não chegou a sua vez"*. Colapsá-las diria a quem ainda tem chance que ela não tem — e a
pessoa pararia de acompanhar. A tela de convocação já é obrigada à mesma distinção, pela mesma
razão.

**O vencimento do prazo não fecha nada aqui** (`FR-374`). Quem decide a consequência do prazo é a
convocação, que registra o desfecho; contá-lo uma segunda vez neste módulo produziria duas contagens
do mesmo prazo, e elas divergiriam.
"""

from dataclasses import dataclass

from processo_seletivo.requerimentos.domain import nomes


@dataclass(frozen=True)
class LeituraDoRequerimento:
    """O que a tela mostra, e o que ela oferece. Nada aqui é decidido de novo.

    `pode_escrever` e `pode_enviar` são **espelhos** da política, e não uma segunda regra: o comando
    recusa por si quem chegar sem passar pela tela (Princípio IV), e o que vive aqui é só a decisão
    de qual botão desenhar.
    """

    estado: str
    titulo: str
    explicacao: str
    pode_escrever: bool
    pode_enviar: bool


# As quatro frases que a tela diz, uma por estado que a pessoa pode encontrar. **Nenhuma delas usa
# *deferido*, *indeferido*, *homologado* nem *matrícula efetivada*** (`SC-132`): enviar o
# requerimento não decide nada — quem decide a vaga é a convocação, e quem efetiva a matrícula é o
# Registro Acadêmico. Prometer qualquer uma dessas coisas aqui seria dizer à pessoa que ela tem o
# que ainda não tem.
_FRASES = {
    nomes.NAO_APLICAVEL: (
        "Este certame não pede Requerimento de Matrícula",
        "Nada a preencher aqui.",
    ),
    nomes.AINDA_INDISPONIVEL: (
        "Ainda não é a hora",
        "Este Processo Seletivo pede o Requerimento de Matrícula quando você for convocado. Esta "
        "página passa a aceitar o preenchimento assim que a sua convocação acontecer — continue "
        "acompanhando.",
    ),
    nomes.DISPONIVEL: (
        "O que falta você informar",
        "Você pode guardar o que preencher e voltar depois.",
    ),
    nomes.EM_PREENCHIMENTO: (
        "O que falta você informar",
        "Você pode guardar o que preencher e voltar depois.",
    ),
    nomes.ESTADO_ENVIADO: (
        "Enviado",
        "Enviado não é alterado. Se algo mudar e você for convocado, esta página oferece a "
        "atualização.",
    ),
}


def leitura(apurado) -> LeituraDoRequerimento:
    """A `Disponibilidade` do domínio, dita em palavras de tela."""
    estado = apurado.estado_de_leitura
    titulo, explicacao = _FRASES[estado]
    escrevivel = estado in (nomes.DISPONIVEL, nomes.EM_PREENCHIMENTO)
    return LeituraDoRequerimento(
        estado=estado,
        titulo=titulo,
        explicacao=explicacao,
        pode_escrever=escrevivel,
        pode_enviar=escrevivel,
    )


def para_o_dossie(inscricao):
    """O requerimento desta Inscrição, pronto para quem **conduz** ler (029, `US4`).

    **Devolve `None` quando não há requerimento vigente**, e o dossiê simplesmente não desenha o
    bloco. Um bloco dizendo *"não há"* apareceria em todo Edital que não coleta — que é a maioria —
    e alongaria uma tela já longa com uma ausência que não é informação.

    **O rascunho aparece, e aparece dito como rascunho.** Esconder o que a pessoa começou a
    preencher faria quem conduz concluir que ela não declarou nada; e mostrá-lo sem dizer que é
    rascunho faria tratar como declarado o que ninguém enviou. A distinção é a mesma que a `009` já
    faz entre inscrição em preenchimento e inscrição recebida.

    **Sem rota própria e sem listagem** (`FR-400`). Este seletor é chamado de dentro do dossiê da
    inscrição, sob `inscricao:consultar`: uma listagem de requerimentos de um Edital seria
    superfície nova sobre dado pessoal — cor/raça, filiação, endereço de todo mundo numa tela só —
    sem jornada que a peça.
    """
    from processo_seletivo.requerimentos.application.exigencia import vigente_de
    from processo_seletivo.requerimentos.domain import rotulos

    requerimento = vigente_de(inscricao)
    if requerimento is None:
        return None
    return {
        "requerimento": requerimento,
        "enviado": requerimento.status == nomes.ENVIADO,
        "grupos": [
            {
                "titulo": titulo,
                "linhas": [
                    {
                        "rotulo": rotulos.ROTULOS[campo],
                        "valor": rotulos.legivel(campo, getattr(requerimento, campo)),
                    }
                    for campo in campos
                ],
            }
            for titulo, campos in rotulos.GRUPOS
        ],
        # **O endereço foi conferido contra a base, ou é o que a pessoa digitou?** Quem lê um
        # endereço para expedir documento precisa saber de qual dos dois se trata.
        "conferido_por_referencia": requerimento.endereco_conferido_por_referencia,
        # A cadeia, para quem precisa reconstituir o que foi corrigido e sob qual autorização.
        "sucede": requerimento.requerimento_anterior_id,
        "convocacao_autorizadora": requerimento.convocacao_autorizadora_id,
    }
