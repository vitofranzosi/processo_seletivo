"""O catálogo fechado das perguntas sugeridas (070, `FR-1417` a `FR-1420`, `D-002`, `D-007`).

**Fechado, e não classificado.** A Fase A não recebe texto livre (`FR-1419`): classificar uma frase
por palavra-chave para cair numa destas perguntas seria interpretar linguagem sem modelo, e erraria
em silêncio. A pergunta livre é a Fase B.

**Oferecida pelo conteúdo.** Cada pergunta só aparece quando o Edital tem com que respondê-la.

**A pertinência é declarada, e não calculada** (`D-007`). Para cada pergunta, duas listas de seções:

- as que **tratam do assunto**: se estiverem preenchidas, a resposta depende de ler o texto, e o
  tipo muda (`R-013`);
- as que **acompanham**: saem inteiras ao lado da resposta, para que nenhuma ressalva fique de fora,
  mas não mudam o tipo.

A tabela erra para mais de propósito: texto a mais é lido e descartado; texto a menos omitiria a
exceção.
"""

from __future__ import annotations

from dataclasses import dataclass

from processo_seletivo.duvidas.domain import leitura
from processo_seletivo.inscricoes.domain.periodo import evento_designado

PERFIL, MODALIDADE = "perfil", "modalidade"
SEM_MODALIDADE = "nenhuma"


@dataclass(frozen=True)
class Pergunta:
    codigo: str
    texto: str
    parametros: tuple[str, ...]
    trata: tuple[str, ...] = ()
    acompanha: tuple[str, ...] = ()
    #: Só na `P-05`: com lista de concorrência que não seja a ampla, estas também acompanham.
    acompanha_com_modalidade: tuple[str, ...] = ()


PERGUNTAS = (
    Pergunta("P-01", "Até quando posso me inscrever?", (), acompanha=("inscricao",)),
    Pergunta("P-02", "Quais são as próximas datas?", ()),
    Pergunta("P-03", "Quantas vagas há neste Perfil?", (PERFIL,), acompanha=("publico-alvo",)),
    Pergunta(
        "P-04",
        "Quais são os requisitos deste Perfil?",
        (PERFIL,),
        trata=("requisitos-gerais",),
        acompanha=("publico-alvo",),
    ),
    Pergunta(
        "P-05",
        "Que documentos preciso enviar?",
        (PERFIL, MODALIDADE),
        acompanha=("inscricao",),
        acompanha_com_modalidade=("verificacao-autodeclaracao", "atendimento-pcd"),
    ),
    Pergunta("P-06", "Posso me inscrever em mais de um Perfil?", (), trata=("inscricao",)),
    Pergunta("P-07", "Como será a seleção?", (PERFIL,), acompanha=("classificacao",)),
    Pergunta("P-08", "Posso recorrer? Em que prazo?", (PERFIL,), trata=("recursos",)),
    Pergunta("P-09", "Como funciona o sorteio?", (PERFIL,), acompanha=("classificacao",)),
    Pergunta("P-10", "Como serei convocado?", (PERFIL,), trata=("convocacao", "matricula")),
    Pergunta("P-11", "Onde tiro dúvidas?", ()),
    Pergunta("P-12", "Onde estão o Edital e os anexos?", ()),
)
POR_CODIGO = {pergunta.codigo: pergunta for pergunta in PERGUNTAS}


def _algum_marco(conteudo, condicao):
    return any(
        condicao(marco)
        for perfil in conteudo.get("profiles") or []
        for marco in perfil.get("classificationMilestones") or []
    )


def _oferecida(codigo, conteudo) -> bool:
    perfis = conteudo.get("profiles") or []
    if codigo == "P-01":
        return evento_designado(conteudo) is not None
    if codigo == "P-02":
        return bool(conteudo.get("schedule"))
    if codigo == "P-04":
        return any(perfil.get("requirements") for perfil in perfis) or bool(
            leitura.texto_da_secao(leitura.secao_por_chave(conteudo, "requisitos-gerais"))
        )
    if codigo == "P-05":
        return bool(conteudo.get("documentRequirements"))
    if codigo == "P-06":
        return len(perfis) > 1
    if codigo == "P-07":
        return bool(conteudo.get("stages")) or _algum_marco(conteudo, lambda marco: True)
    if codigo == "P-09":
        return _algum_marco(conteudo, lambda marco: marco.get("orderProduction") == "POR_SORTEIO")
    if codigo in ("P-03", "P-08", "P-10"):
        return bool(perfis)
    return True


def aplicavel_ao_perfil(codigo, perfil, conteudo) -> bool:
    """A coluna "Oferecida quando" da `FR-1417`, no Perfil escolhido.

    A oferta do Edital diz que **algum** Perfil tem com que responder; o Perfil escolhido pode não
    ter. Sem esta conferência, a `P-09` de um Perfil sem sorteio, num Edital em que outro Perfil
    sorteia, respondia "não classifica por sorteio" sobre um Perfil que não declara marco nenhum —
    negativa que o Edital não faz.
    """
    marcos = perfil.get("classificationMilestones") or []
    if codigo == "P-04":
        return bool(perfil.get("requirements")) or bool(
            leitura.texto_da_secao(leitura.secao_por_chave(conteudo, "requisitos-gerais"))
        )
    if codigo == "P-07":
        return bool(marcos) or bool(conteudo.get("stages"))
    if codigo == "P-09":
        return any(marco.get("orderProduction") == "POR_SORTEIO" for marco in marcos)
    return True


def oferecidas(conteudo) -> tuple[Pergunta, ...]:
    """As perguntas que este Edital, nesta versão, sabe responder — na ordem do catálogo."""
    return tuple(pergunta for pergunta in PERGUNTAS if _oferecida(pergunta.codigo, conteudo))


def opcoes_de_perfil(conteudo):
    """`(código, rótulo)` de cada Perfil, na ordem publicada (`FR-1418`)."""
    return tuple(
        (perfil.get("code"), leitura.onde_perfil(perfil))
        for perfil in conteudo.get("profiles") or []
    )


def opcoes_de_modalidade(perfil):
    """A lista de concorrência da `P-05`: "sem modalidade" e as do Perfil (`R-008`).

    As mesmas leituras que a página pública faz em `_documentos_anunciados`: o que vale para todos
    no Perfil, e o que cada modalidade acrescenta. Uma modalidade "AC" declarada aparece como as
    outras — é ela que um documento pode apontar —, mas as vagas da ampla concorrência ficam na
    linha sem modalidade do quadro (`FR-1427`).
    """
    opcoes = [(SEM_MODALIDADE, "Sem modalidade — o que vale para todos neste Perfil")]
    for modalidade in (perfil or {}).get("competitionModalities") or []:
        opcoes.append(
            (modalidade.get("code"), f"{modalidade.get('code')} — {modalidade.get('name', '')}")
        )
    return tuple(opcoes)


@dataclass(frozen=True)
class Parametros:
    perfil: dict | None = None
    modalidade: dict | None = None

    def como_pares(self):
        return (
            (PERFIL, (self.perfil or {}).get("code")),
            (MODALIDADE, (self.modalidade or {}).get("code") if self.modalidade else None),
        )


class ParametroRecusado(ValueError):
    """O parâmetro não existe na versão vigente, ou a pergunta não se aplica (`FR-1418`)."""


def resolver(pergunta, conteudo, *, perfil=None, modalidade=None) -> Parametros:
    """Os parâmetros da pergunta, lidos na versão vigente — ou a recusa, com o motivo."""
    if pergunta.codigo not in {oferecida.codigo for oferecida in oferecidas(conteudo)}:
        raise ParametroRecusado("Esta pergunta não se aplica a este Edital.")
    if PERFIL not in pergunta.parametros:
        return Parametros()
    if not perfil:
        raise ParametroRecusado("Escolha o Perfil.")
    encontrado = leitura.perfil_por_codigo(conteudo, perfil)
    if encontrado is None:
        raise ParametroRecusado(f"O Perfil {perfil} não existe na versão vigente deste Edital.")
    if not aplicavel_ao_perfil(pergunta.codigo, encontrado, conteudo):
        raise ParametroRecusado(f"Esta pergunta não se aplica ao Perfil {perfil}.")
    if MODALIDADE not in pergunta.parametros or not modalidade or modalidade == SEM_MODALIDADE:
        return Parametros(perfil=encontrado)
    for item in encontrado.get("competitionModalities") or []:
        if item.get("code") == modalidade:
            return Parametros(perfil=encontrado, modalidade=item)
    raise ParametroRecusado(f"A modalidade {modalidade} não existe no Perfil {perfil}.")
