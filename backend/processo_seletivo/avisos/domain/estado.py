"""Em que estado está cada destinatário, derivado dos registros e do relógio (066, data-model §2).

**Derivado, e nunca coluna**, pela razão que a `016` e a `019` já escreveram: coluna exigiria
`UPDATE` em tabela append-only, e o relógio andaria dentro de um registro imutável. Expirar é ler a
idade do aviso, e não gravar que ele expirou.

**A janela de despacho é o que impede o disparo antigo** (`R-016`, `FR-1283`). A chave de
habilitação é configuração do ambiente e o banco não a vê mudar; a idade do aviso ele vê. Religar a
chave, ou o timer que volta depois de dias, alcança só o que ainda está dentro da janela.

Funções puras: nada aqui consulta o banco ou lê o relógio sozinho.
"""

from dataclasses import dataclass
from datetime import timedelta

from processo_seletivo.avisos.domain import nomes

#: Tentativa sem resultado mais nova que isto está **em envio**; mais velha, ninguém a concluirá.
#: O despacho grava a indeterminada ao encontrá-la (contracts/despacho.md, passo 2); este prazo só
#: decide o que a tela diz até lá.
EM_ENVIO_ATE_MIN = 5


@dataclass(frozen=True)
class Tentativa:
    numero: int
    iniciada_em: object
    resultado: str | None = None
    registrado_em: object = None


def janela_passou(*, solicitado_em, agora, janela_horas):
    return agora >= solicitado_em + timedelta(hours=janela_horas)


def proxima_tentativa_em(tentativas, *, intervalos):
    """Quando a próxima tentativa de uma falha temporária pode começar (`FR-1269`, `R-005`)."""
    ultima = tentativas[-1]
    if not intervalos:
        return ultima.registrado_em
    espera = intervalos[min(len(tentativas) - 1, len(intervalos) - 1)]
    return ultima.registrado_em + timedelta(minutes=espera)


def estado_do_destinatario(
    *,
    elegibilidade,
    endereco,
    tentativas,
    interrompido,
    solicitado_em,
    agora,
    max_tentativas,
    janela_horas,
):
    """O estado de um destinatário, pela precedência do data-model §2.

    `tentativas` vem em ordem de número. A primeira condição que se aplica vence.
    """
    if elegibilidade != nomes.ELEGIVEL:
        return nomes.NAO_ELEGIVEL
    if not endereco:
        return nomes.SEM_ENDERECO
    if not tentativas:
        if interrompido:
            return nomes.INTERROMPIDO_ANTES_DO_ENVIO
        if janela_passou(solicitado_em=solicitado_em, agora=agora, janela_horas=janela_horas):
            return nomes.EXPIRADA_SEM_ENVIO
        return nomes.PENDENTE
    ultima = tentativas[-1]
    if ultima.resultado is None:
        if agora < ultima.iniciada_em + timedelta(minutes=EM_ENVIO_ATE_MIN):
            return nomes.EM_ENVIO
        return nomes.ESTADO_INDETERMINADA
    if ultima.resultado == nomes.ACEITA:
        return nomes.ESTADO_ACEITA
    if ultima.resultado == nomes.FALHA_DEFINITIVA:
        return nomes.ESTADO_FALHA_DEFINITIVA
    if ultima.resultado == nomes.INDETERMINADA:
        return nomes.ESTADO_INDETERMINADA
    # Falha temporária: o limite a torna definitiva; a interrupção e a janela a param antes disso.
    if len(tentativas) >= max_tentativas:
        return nomes.ESTADO_FALHA_DEFINITIVA
    if interrompido:
        return nomes.INTERROMPIDO_ANTES_DO_ENVIO
    if janela_passou(solicitado_em=solicitado_em, agora=agora, janela_horas=janela_horas):
        return nomes.EXPIRADA_SEM_ENVIO
    return nomes.ESTADO_FALHA_TEMPORARIA


def elegivel_ao_despacho(*, estado, tentativas, agora, intervalos, habilitado):
    """O destinatário que o despacho pode tentar agora (data-model §2).

    **Com a chave desligada, ninguém** (`FR-1282`). Pendente sempre pode; a falha temporária, só
    depois do intervalo. Indeterminada, nunca: só um aviso filho, confirmado por uma pessoa.
    """
    if not habilitado:
        return False
    if estado == nomes.PENDENTE:
        return True
    if estado == nomes.ESTADO_FALHA_TEMPORARIA:
        return agora >= proxima_tentativa_em(tentativas, intervalos=intervalos)
    return False


#: Os estados de quem ainda pode sair. O aviso sem nenhum deles está concluído.
EM_CURSO = (nomes.PENDENTE, nomes.EM_ENVIO, nomes.ESTADO_FALHA_TEMPORARIA)


def concluido(estados):
    return not any(estado in EM_CURSO for estado in estados)


__all__ = [
    "EM_CURSO",
    "EM_ENVIO_ATE_MIN",
    "Tentativa",
    "concluido",
    "elegivel_ao_despacho",
    "estado_do_destinatario",
    "janela_passou",
    "proxima_tentativa_em",
]
