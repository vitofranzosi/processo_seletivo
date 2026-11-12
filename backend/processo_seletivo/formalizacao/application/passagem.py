"""A passagem ao setor, em contagens: o que falta para os documentos das pessoas aptas chegarem a
ele (153, FR-6100 a FR-6107).

**Uma derivação, quatro leitores.** O nível 1 da `127`, o bloco da fase Conclusão do Centro, o
relatório do Edital da `099` e as duas confirmações de encerrar leem daqui. A `113` exige que a
confirmação advirta pela mesma regra do relatório (FR-3535 da `113`), e uma segunda contagem no
Centro divergiria dela na primeira mudança.

**Só registros, nunca arquivo** (FR-6105, D-008 da `153`). As pessoas aptas e o conjunto de cada uma
vêm do seletor único da `117` (`conjunto.aptos`), que também não lê arquivo. O documento
indisponível aparece onde já aparece: na verificação, a quem exporta.

**Cada pessoa numa situação só** (FR-6106, D-004). A ordem importa:

1. **disponibilizada**: incluída em algum pacote do Edital, em qualquer versão da definição e em
   qualquer chamada (P-2, respondida em 11/11/2026);
2. **sem definição**: a definição nunca foi gravada;
3. **sem documento**: definição gravada, e nenhum documento incluído no conjunto. Não há o que
   disponibilizar, e o pacote exige arquivo (`ck_exportacao_formalizacao_com_arquivo`);
4. **sem quem receba**: nenhuma designação efetiva cobre o Perfil dela;
5. **a exportar**: o resto. Só o setor resolve.

Nada aqui é gravado.
"""

from dataclasses import dataclass
from datetime import datetime

#: As causas de uma pessoa pendente, na ordem da FR-6106.
SEM_DEFINICAO = "sem_definicao"
SEM_QUEM_RECEBA = "sem_quem_receba"
A_EXPORTAR = "a_exportar"
CAUSAS = (SEM_DEFINICAO, SEM_QUEM_RECEBA, A_EXPORTAR)

#: Os estados em que há passagem ao setor (FR-6100). O encerrado continua: a exportação não fecha
#: com o encerramento (FR-3710 da `117`).
ESTADOS = frozenset({"PUBLICADO", "ENCERRADO"})


@dataclass(frozen=True)
class Passagem:
    aptas: int
    disponibilizadas: int
    sem_documento: int
    #: `{causa: quantas}`, com as três causas sempre presentes.
    pendentes: dict
    #: A definição vigente: `None` se nunca gravada.
    definida_em: datetime | None
    definicao_vazia: bool
    #: As designações efetivas: vigentes, de quem tem o papel na unidade e está ativo (FR-6107).
    designadas: int
    #: Quantas pessoas da unidade têm o papel Formalização vigente (FR-6113).
    com_o_papel: int
    ultimo_pacote_em: datetime | None

    @property
    def definida(self):
        return self.definida_em is not None

    @property
    def total_pendentes(self):
        return sum(self.pendentes.values())

    @property
    def causas(self):
        """`((causa, quantas), …)` das causas com pessoa, na ordem da FR-6106."""
        return tuple((causa, self.pendentes[causa]) for causa in CAUSAS if self.pendentes[causa])

    @property
    def completa(self):
        """Todas as pessoas aptas estão disponibilizadas, ou não têm documento a disponibilizar."""
        return not self.total_pendentes


def da_passagem(edital):
    """A `Passagem` do Edital, ou `None` fora de publicado ou encerrado, ou sem pessoa apta."""
    from processo_seletivo.formalizacao.application import conjunto, definir
    from processo_seletivo.formalizacao.domain import nomes
    from processo_seletivo.formalizacao.domain.autorizacao import designacoes_vigentes
    from processo_seletivo.seguranca.application import acessos

    if edital.status not in ESTADOS:
        return None
    definicao = definir.vigente(edital)
    pessoas = conjunto.aptos(edital, definicao=definicao, com_exportacoes=False)
    if not pessoas:
        return None
    exportacoes = conjunto.exportacoes_do_edital(edital)
    incluidas = {str(p["inscricao"]) for e in exportacoes for p in e.incluidas}
    com_o_papel = set(
        acessos.vigentes()
        .filter(escopo=edital.institution_scope, papel=nomes.PAPEL, pessoa__is_active=True)
        .values_list("pessoa__username", flat=True)
    )
    efetivas = [d for d in designacoes_vigentes(edital=edital) if d.pessoa in com_o_papel]

    disponibilizadas = sem_documento = 0
    pendentes = dict.fromkeys(CAUSAS, 0)
    for pessoa in pessoas:
        if pessoa.inscricao_id in incluidas:
            disponibilizadas += 1
        elif definicao is None:
            pendentes[SEM_DEFINICAO] += 1
        elif not pessoa.incluiveis:
            sem_documento += 1
        elif not any(d.cobre(pessoa.perfil_id) for d in efetivas):
            pendentes[SEM_QUEM_RECEBA] += 1
        else:
            pendentes[A_EXPORTAR] += 1
    return Passagem(
        aptas=len(pessoas),
        disponibilizadas=disponibilizadas,
        sem_documento=sem_documento,
        pendentes=pendentes,
        definida_em=definicao.definido_em if definicao else None,
        definicao_vazia=definicao is not None and not definicao.requisitos,
        designadas=len({d.pessoa for d in efetivas}),
        com_o_papel=len(com_o_papel),
        ultimo_pacote_em=exportacoes[0].exportado_em if exportacoes else None,
    )
