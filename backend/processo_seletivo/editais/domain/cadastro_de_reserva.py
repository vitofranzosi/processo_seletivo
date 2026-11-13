"""O número do cadastro de reserva, lido do corte do marco que convoca (162).

**O defeito que este módulo fecha.** Até a `162` o Perfil declarava "cadastro reserva limitado em N"
num campo digitado, e o documento, o portal, a Revisão, o relatório e o assistente o repetiam.
Nenhuma regra o lia: quem a ordem alcança é decidido pelo **corte** do marco que convoca — o alvo, o
excedente e a continuação —, que a faixa calcula (`014`), a ocupação apura (`016`) e a convocação
respeita. Eram duas declarações da mesma norma, e o documento se contradizia: um Perfil só de
reserva limitado em 6, com corte fixo de 10 e continuação, imprimia *"Seguem no processo os 10 (dez)
primeiros […] Depois, poderão ser chamados outros"* e *"cadastro de reserva de até 6 (seis)"*.

**A fonte é o corte** (`D-001`). Nos Editais da amostra, o número "limitado" é o de suplentes — o 77
publica *"até 30 (trinta) suplentes"*, o 57 *"até 20 (vinte) por código de vaga"* —, e é exatamente
o excedente que a `014` modelou a partir deles. O número do cadastro é o que o corte alcança **além
das vagas** da lista (`D-002`), por lista de concorrência (`D-004`).

**O legado é um fato do conteúdo, e não uma data** (T-002). Depois da `162`, nenhum caminho grava o
número; o Perfil publicado antes, que o traz, continua dizendo o que disse (FR-6944), e as telas da
condução dizem que ele não é aplicado (FR-6947).

**Puro.** Recebe o Perfil do conteúdo — publicado ou composto do rascunho — e responde. A direção
`editais → classificacao.domain` já existe (`validation.py` importa a combinação), e as duas peças
que vêm de lá são a forma normalizada da regra e a definição de marco intermediário da `133`.
"""

from dataclasses import dataclass

from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.classificacao.domain.marco_intermediario import marco_que_le

NAO_HA = "NONE"
LIMITADO = "LIMITED"
ILIMITADO = "UNLIMITED"

#: Como a linha geral se chama ao lado das Modalidades. É o nome que o portal já dá à convocação sem
#: lista, e o código é o que os Editais escrevem na ordem de chamada ("1ª AC · 2ª PcD").
NOME_DA_LINHA_GERAL = "Ampla concorrência"
CODIGO_DA_LINHA_GERAL = "AC"


@dataclass(frozen=True)
class Lista:
    """O número do cadastro numa lista de concorrência: o alcance da faixa menos as vagas dela."""

    lista_id: str | None
    nome: str
    codigo: str
    numero: int


@dataclass(frozen=True)
class Marco:
    """O que importa de um marco que convoca: quem é e o que o corte dele dá em cada lista."""

    marco_id: str
    nome: str
    tem_corte: bool
    continuacao: bool
    empate: bool
    listas: tuple


@dataclass(frozen=True)
class Cadastro:
    especie: str
    legado: bool
    publicado: int | None
    por_lista: tuple
    alcance_cresce: bool
    admite_empate: bool
    com_modalidade: bool
    vagas: int
    marcos: tuple = ()

    @property
    def numero_unico(self):
        """O número, quando é o mesmo em todas as listas; `None` sem corte ou quando diferem."""
        numeros = {lista.numero for lista in self.por_lista}
        return next(iter(numeros)) if len(numeros) == 1 else None

    @property
    def marco_que_convoca(self):
        """O primeiro marco que convoca com corte, ou o primeiro que convoca, ou `None`."""
        com_corte = [marco for marco in self.marcos if marco.tem_corte]
        if com_corte:
            return com_corte[0]
        return self.marcos[0] if self.marcos else None

    @property
    def so_de_reserva(self):
        return self.vagas == 0 and self.especie in (LIMITADO, ILIMITADO)

    def numero_mostrado(self):
        """O número que as telas dizem: o publicado no legado, o derivado nos demais."""
        return self.publicado if self.legado else self.numero_unico

    def descricao_curta(self):
        """O texto das telas de gestão — Revisão, relatório, visão institucional (contrato D)."""
        if self.especie == ILIMITADO:
            return "Sem limite"
        if self.especie != LIMITADO:
            return "Não há"
        if self.legado:
            return f"Limitado em {self.publicado}"
        if not self.por_lista:
            return "Limitado, sem corte no marco que convoca"
        return f"Limitado: {self._ate()}"

    def resumo_limitado(self):
        """O `data-resumo` da opção "limitado" na tabela da etapa (contrato P).

        Calculado sobre o corte salvo, qualquer que seja a espécie marcada agora: quem troca para
        "limitado" vê o número que o corte já declarado produziria.
        """
        if not self.por_lista:
            return "limitado"
        return f"limitado: {self._ate()}"

    def _ate(self):
        unico = self.numero_unico
        if unico is not None:
            return f"até {unico}" + (" por lista" if self.com_modalidade else "")
        partes = [f"{lista.numero} {lista.codigo}" for lista in self.por_lista]
        return "até " + ", ".join(partes)


def _inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _listas(perfil):
    """`(lista_id, nome, codigo, vagas)` na ordem do quadro; sem quadro, a linha geral (T-006)."""
    modalidades = {
        str(modalidade.get("id")): modalidade
        for modalidade in perfil.get("competitionModalities") or []
        if isinstance(modalidade, dict)
    }
    linhas = [linha for linha in perfil.get("vacancyTable") or [] if isinstance(linha, dict)]
    if not linhas:
        total = perfil.get("immediateVacancies")
        return [(None, NOME_DA_LINHA_GERAL, CODIGO_DA_LINHA_GERAL, total if _inteiro(total) else 0)]
    listas = []
    for linha in linhas:
        vagas = linha.get("immediateVacancies")
        vagas = vagas if _inteiro(vagas) else 0
        modalidade_id = linha.get("modalityId")
        if not modalidade_id:
            listas.append((None, NOME_DA_LINHA_GERAL, CODIGO_DA_LINHA_GERAL, vagas))
            continue
        modalidade = modalidades.get(str(modalidade_id)) or {}
        listas.append(
            (
                str(modalidade_id),
                modalidade.get("name") or "",
                modalidade.get("code") or modalidade.get("name") or "",
                vagas,
            )
        )
    return listas


def _numeros(regra, listas):
    """O alcance da faixa sem continuação, menos as vagas da linha (T-006, `D-002`)."""
    excedente = int(regra.get("surplusCount") or 0)
    resultado = []
    for lista_id, nome, codigo, vagas in listas:
        if regra.get("targetKind") == faixa.ALVO_FIXO:
            alcance = int(regra.get("targetCount") or 0) + excedente
        else:
            alcance = vagas + excedente
        resultado.append(Lista(lista_id, nome, codigo, alcance - vagas))
    return tuple(resultado)


def marcos_que_convocam(perfil):
    """Os marcos que não são intermediários (`133`, FR-4531), na ordem do Perfil."""
    marcos = [
        m for m in (perfil or {}).get("classificationMilestones") or [] if isinstance(m, dict)
    ]
    return [marco for marco in marcos if marco_que_le(perfil, marco.get("id")) is None]


def do_perfil(perfil) -> Cadastro:
    perfil = perfil if isinstance(perfil, dict) else {}
    especie = perfil.get("reserveType") or NAO_HA
    digitado = perfil.get("reserveLimit")
    legado = especie == LIMITADO and _inteiro(digitado)
    listas = _listas(perfil)
    marcos = []
    for marco in marcos_que_convocam(perfil):
        regra = (
            faixa.normalizar(marco.get("cutRule"))
            if isinstance(marco.get("cutRule"), dict)
            else None
        )
        marcos.append(
            Marco(
                marco_id=str(marco.get("id")),
                nome=marco.get("name") or "",
                tem_corte=regra is not None,
                continuacao=faixa.admite_continuacao(regra),
                empate=bool(regra) and regra.get("tieOutcome") == faixa.EMPATE_ADMITE_EXCEDENTE,
                listas=_numeros(regra, listas) if regra else (),
            )
        )
    com_corte = [marco for marco in marcos if marco.tem_corte]
    total = perfil.get("immediateVacancies")
    return Cadastro(
        especie=especie,
        legado=legado,
        publicado=digitado if legado else None,
        por_lista=com_corte[0].listas if com_corte else (),
        alcance_cresce=any(marco.continuacao for marco in com_corte),
        admite_empate=any(marco.empate for marco in com_corte),
        com_modalidade=any(lista_id is not None for lista_id, *_ in listas),
        vagas=total if _inteiro(total) else 0,
        marcos=tuple(marcos),
    )


def frase_das_listas(por_lista, *, numero=str, unidade=None):
    """`3 na ampla concorrência, 1 na lista PcD e 1 na lista PPI` — o número de cada lista.

    **Uma redação só** para o documento, o portal e a nota da condução (FR-6930). `numero` formata o
    número (o documento o escreve por extenso); `unidade`, quando dada, vem depois do primeiro
    número, no singular ou no plural dele ("1 pessoa", "2 classificados").
    """
    partes = []
    for indice, lista in enumerate(por_lista):
        quantos = numero(lista.numero)
        if indice == 0 and unidade is not None:
            quantos = f"{quantos} {unidade(lista.numero)}"
        onde = "na ampla concorrência" if lista.lista_id is None else f"na lista {lista.nome}"
        partes.append(f"{quantos} {onde}")
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + f" e {partes[-1]}"


LIMITADO_COM_CONTINUACAO = "reserve_limited_with_continuation"
ILIMITADO_SEM_CONTINUACAO = "reserve_unlimited_without_continuation"
LIMITADO_SEM_CORTE = "reserve_limited_without_cut"
LIMITADO_A_NINGUEM = "reserve_limited_to_nobody"
LIMITADO_COM_MARCOS_DIVERGENTES = "reserve_limited_divergent_milestones"


def nome_do_marco(marco):
    """`o marco “Classificação final”` — pelo nome entre aspas, sem supor o gênero dele.

    O nome é do Edital: "Classificação final" e "Sorteio público" convivem, e "a Sorteio público"
    era o que a forma "a {nome}" escrevia. Quem compõe a frase põe o `d` antes: "do marco".
    """
    return f"o marco “{marco.nome}”" if marco and marco.nome else "o marco que convoca deste Perfil"


def _na_lista(cadastro, lista):
    if not cadastro.com_modalidade:
        return ""
    if lista.lista_id is None:
        return " na ampla concorrência"
    return f" na lista {lista.nome}"


def incoerencias(cadastro, *, rotulo, na_publicacao):
    """`[(codigo, frase)]` — o que impede publicar este cadastro com este corte (FR-6933 a 6939).

    **Recortadas pelo ato** (T-004). O ilimitado sem continuação e o limitado sem corte só se
    conferem na publicação: a espécie não se retifica, e o ilimitado não tem marca de legado — a
    Retificação do acervo seria recusada por uma regra que ele não conheceu. O limitado com
    continuação, o zero e a divergência valem também na Retificação, porque o corte nasce e o alvo
    e o excedente mudam por ela (FR-6951). O legado não é conferido: ele publicou o número
    digitado (FR-6948).

    **O vocabulário é o do documento** (UX-726): "cadastro de reserva", "continuação", "corte".
    """
    achados = []
    perfil = f"O Perfil '{rotulo}'"
    if cadastro.especie == ILIMITADO and na_publicacao:
        for marco in cadastro.marcos:
            if marco.tem_corte and not marco.continuacao:
                achados.append(
                    (
                        ILIMITADO_SEM_CONTINUACAO,
                        f"{perfil} declara cadastro de reserva sem limite, e o corte d"
                        f"{nome_do_marco(marco)} não admite chamar além da faixa: o cadastro "
                        "pararia nos primeiros que ela alcança. Admita a continuação no corte d"
                        f"{nome_do_marco(marco)}, ou declare o cadastro de reserva limitado.",
                    )
                )
        return achados
    if cadastro.especie != LIMITADO or cadastro.legado:
        return achados
    com_corte = [marco for marco in cadastro.marcos if marco.tem_corte]
    if na_publicacao:
        if not com_corte:
            marco = cadastro.marco_que_convoca
            onde = (
                f"{nome_do_marco(marco)} não tem regra de corte"
                if marco
                else "nenhum marco de classificação deste Perfil convoca"
            )
            final = (
                f"Declare o corte d{nome_do_marco(marco)}"
                if marco
                else "Declare um marco de classificação com corte"
            )
            achados.append(
                (
                    LIMITADO_SEM_CORTE,
                    f"{perfil} declara cadastro de reserva limitado, e {onde}: o número do "
                    f"cadastro vem do corte. {final}, ou declare o cadastro de reserva sem limite.",
                )
            )
            return achados
    # **A continuação também na Retificação** (FR-6933): a espécie e a continuação de um corte que
    # existe não se retificam, mas o corte **nasce** por Retificação (`PODE_PASSAR_A_EXISTIR`), e um
    # marco que convoca pode passar a cortar com continuação. O legado já saiu acima.
    for marco in com_corte:
        if marco.continuacao:
            achados.append(
                (
                    LIMITADO_COM_CONTINUACAO,
                    f"{perfil} declara cadastro de reserva limitado, e {nome_do_marco(marco)} "
                    "admite chamar candidatos além da faixa: o cadastro não teria limite. "
                    f"Retire a continuação do corte d{nome_do_marco(marco)}, ou declare o cadastro "
                    "de reserva sem limite.",
                )
            )
    for marco in com_corte:
        for lista in marco.listas:
            if lista.numero <= 0:
                achados.append(
                    (
                        LIMITADO_A_NINGUEM,
                        f"{perfil} declara cadastro de reserva limitado, e o corte d"
                        f"{nome_do_marco(marco)} não alcança ninguém além das vagas"
                        f"{_na_lista(cadastro, lista)}: o cadastro seria de zero classificados. "
                        "Aumente o alvo ou o excedente do corte, ou declare que não há cadastro "
                        "de reserva.",
                    )
                )
    primeiro = com_corte[0] if com_corte else None
    for outro in com_corte[1:]:
        for lista, comparada in zip(primeiro.listas, outro.listas, strict=True):
            if lista.numero != comparada.numero:
                achados.append(
                    (
                        LIMITADO_COM_MARCOS_DIVERGENTES,
                        f"{perfil} declara cadastro de reserva limitado, e os cortes d"
                        f"{nome_do_marco(primeiro)} e d{nome_do_marco(outro)} dão números "
                        f"diferentes{_na_lista(cadastro, lista)} "
                        f"({lista.numero} e {comparada.numero}): o documento não teria um "
                        "número para dizer. Iguale o alvo e o excedente dos dois cortes.",
                    )
                )
    return achados


__all__ = [
    "CODIGO_DA_LINHA_GERAL",
    "ILIMITADO_SEM_CONTINUACAO",
    "LIMITADO_A_NINGUEM",
    "LIMITADO_COM_CONTINUACAO",
    "LIMITADO_COM_MARCOS_DIVERGENTES",
    "LIMITADO_SEM_CORTE",
    "incoerencias",
    "Cadastro",
    "ILIMITADO",
    "LIMITADO",
    "Lista",
    "Marco",
    "NAO_HA",
    "NOME_DA_LINHA_GERAL",
    "do_perfil",
    "frase_das_listas",
    "marcos_que_convocam",
    "nome_do_marco",
]
