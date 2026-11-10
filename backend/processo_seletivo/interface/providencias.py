"""As providências do Edital, na ordem em que o nível 1 as mostra (127, FR-4080 a FR-4087).

**Puro.** Recebe as providências que `andamento.py` derivou das células em aberto e decide só duas
coisas de apresentação: quais viram uma linha só (D-016) e em que ordem aparecem (FR-4082). A
derivação não escolhe nada; a apresentação ordena, sempre do mesmo jeito (contrato §4).

**A forma é a do objeto de trabalho da `104`** (`trabalho.ObjetoDeTrabalho`), com os campos que o
contrato de derivação acrescenta: a situação, o responsável, se é da pessoa, a razão e o prazo.
"""

import re
from dataclasses import dataclass, field, replace
from datetime import datetime

from processo_seletivo.interface import andamento as a

#: Quantas providências o nível 1 mostra antes de "Mais N" (o `MOSTRADOS` da `104`).
MOSTRADAS = 5

SUA, DE_OUTRO, EM_ESPERA = "sua", "de_outro", "em_espera"


@dataclass(frozen=True)
class Providencia:
    natureza: str
    chave: tuple
    onde: str
    ato: str
    situacao: str
    responsavel: str = ""
    sua: bool = False
    url: str = ""
    razao: str = ""
    nota: str = ""
    condicional: bool = False
    ate: datetime | None = None
    desde: datetime | None = None
    contagem: int | None = None
    #: O texto do papel quando ele não é um dos de `andamento.PAPEIS` (a Retificação diz o dela).
    papel: str = ""
    quem_resolve: str = ""
    pode_resolver: bool = False
    url_da_saida: str = ""
    marco_id: str = ""
    perfil_id: str = ""
    listas: tuple = ()
    lugar: str = ""
    #: A condução do marco, para onde vai a providência que junta listas de telas diferentes.
    url_do_marco: str = ""
    #: A espera é recomendação: o ato é aceito, e a tela diz por que esperar (133, FR-4542).
    recomendacao: bool = False
    #: A ordem de lista em que ninguém concorre (135, FR-4673): o dado, para a apresentação tratá-la
    #: sem ler a frase do ato.
    lista_vazia: bool = False

    @classmethod
    def da_celula(
        cls,
        celula,
        *,
        onde,
        sua,
        chave,
        marco_id="",
        perfil_id="",
        lista=None,
        pode_resolver=False,
        url_da_saida="",
        url_do_marco="",
        lugar=None,
    ):
        rotulo = lista[1] if lista else ""
        # **O lugar vem dito, e não recortado de `onde`** (item 1 do code review): o nome do Perfil
        # pode ter " · " ("Oferta de Vagas … · Polo Vitória"), e o recorte o trocava pelo de outro.
        lugar = onde if lugar is None else lugar
        return cls(
            natureza=celula.natureza,
            chave=chave,
            onde=onde,
            ato=celula.ato or a.ROTULOS[celula.situacao],
            situacao=celula.situacao,
            responsavel=celula.responsavel,
            sua=sua,
            url=celula.url if sua else "",
            razao=celula.razao,
            nota=celula.nota,
            condicional=celula.condicional,
            ate=celula.ate,
            contagem=celula.contagem,
            quem_resolve=celula.quem_resolve,
            pode_resolver=pode_resolver,
            url_da_saida=url_da_saida,
            marco_id=marco_id,
            perfil_id=perfil_id,
            listas=(rotulo,) if rotulo else (),
            lugar=lugar,
            url_do_marco=url_do_marco if sua else "",
            recomendacao=celula.recomendacao,
            lista_vazia=celula.lista_vazia,
        )

    @classmethod
    def do_objeto(cls, objeto, *, natureza, responsavel):
        """Um objeto de trabalho da `104`, que é sempre da pessoa: a `104` só emite os dela."""
        return cls(
            natureza=natureza,
            chave=objeto.chave,
            onde=objeto.titulo,
            ato=objeto.ato,
            situacao=a.PENDENTE,
            responsavel=responsavel,
            sua=True,
            url=objeto.url,
            desde=objeto.desde,
            lugar=objeto.titulo,
        )

    @property
    def grupo(self):
        if self.situacao in (a.AGUARDA, a.IMPEDIDO):
            return EM_ESPERA
        return SUA if self.sua else DE_OUTRO

    @property
    def texto_do_papel(self):
        if self.papel:
            return self.papel[:1].upper() + self.papel[1:]
        return a.PAPEIS.get(self.responsavel, "")

    @property
    def texto_de_quem_resolve(self):
        return a.PAPEIS.get(self.quem_resolve, "")

    @property
    def onde_por_extenso(self):
        """ "Cefor · Ampla concorrência e PPI" — o lugar e as listas que a providência cobre."""
        if not self.listas:
            return self.onde
        return f"{self.lugar} · {a._lista_de_nomes(self.listas)}"

    @property
    def ato_no_meio_da_frase(self):
        """O ato depois de "Quem publica resultado:", com a inicial minúscula."""
        return self.ato[:1].lower() + self.ato[1:]

    @property
    def rotulo(self):
        return a.ROTULOS[self.situacao]

    @property
    def sinal(self):
        return a.SINAIS[self.situacao]


def agrupar(providencias):
    """Uma providência por ato, e não por célula (D-016, FR-4085).

    O mesmo ato, na mesma situação, do mesmo responsável e do mesmo marco, em várias listas, é uma
    coisa a fazer numa tela só. **Só junta o ato sem número**: "Emitir 1 comunicação" em duas listas
    não é "Emitir 1 comunicação" nas duas, e somar exigiria flexionar o texto de novo. As contagens
    ficam por lista.

    E o que **espera** pela mesma razão — o fim das inscrições, que segura a relação e a
    distribuição — vira uma linha só, com os atos juntos: a razão é uma, e repeti-la empurraria o
    resto para o "Mais N".

    **A lista vazia não se junta à lista com inscritos** (135, FR-4674): a chave a separa pelo
    dado, e não só pela frase do ato, que pode mudar. Duas vazias se juntam, no plural.
    """
    saida, por_chave = [], {}
    for item in providencias:
        if item.grupo == EM_ESPERA and item.razao:
            chave = ("espera", item.situacao, _primeira_frase(item.razao))
        elif not re.search(r"\d", item.ato):
            chave = (
                item.natureza,
                item.marco_id or item.chave,
                item.situacao,
                item.responsavel,
                item.ato,
                item.sua,
                item.lista_vazia,
            )
        else:
            chave = None
        if chave is None or chave not in por_chave:
            if chave is not None:
                por_chave[chave] = len(saida)
            saida.append(item)
            continue
        indice = por_chave[chave]
        saida[indice] = _juntar(saida[indice], item)
    return saida


#: O ato de duas ou mais listas vazias juntadas (135, FR-4674): a sucessora também, e não só a
#: primeira emissão — a revisão do PR #441 achou a sucessora no singular.
_PLURAL_DA_LISTA_VAZIA = {
    a.ATO_DA_ORDEM_VAZIA: a.ATO_DAS_ORDENS_VAZIAS,
    a.ATO_DA_SUCESSORA_VAZIA: a.ATO_DAS_SUCESSORAS_VAZIAS,
}


def _juntar(primeira, outra):
    if primeira.grupo == EM_ESPERA and (primeira.ato != outra.ato or primeira.lugar != outra.lugar):
        atos = _unicos([*primeira.ato.split("; "), outra.ato])
        lugares = _unicos([*primeira.lugar.split("; "), outra.lugar])
        return replace(
            primeira,
            ato="; ".join(atos),
            lugar="; ".join(lugares),
            onde="; ".join(lugares),
            listas=(),
            razao=_primeira_frase(primeira.razao),
            ate=min((d for d in (primeira.ate, outra.ate) if d), default=None),
        )
    # **Telas diferentes, um caminho comum** (item 15 da revisão): "Publicar o resultado — Ampla e
    # PPI" levava só à prévia da Ampla. Com destinos diferentes, vai para a condução do marco, onde
    # cada lista tem a sua célula; o sorteio e a convocação navegam entre listas pela mesma tela.
    url = primeira.url
    if outra.url and _sem_lista(outra.url) != _sem_lista(primeira.url):
        url = primeira.url_do_marco or primeira.url
    elif outra.url and outra.url != primeira.url:
        url = _sem_lista(primeira.url)
    lugares = _unicos([*primeira.lugar.split("; "), outra.lugar])
    listas = tuple(_unicos([*primeira.listas, *outra.listas]))
    ato = primeira.ato
    if primeira.lista_vazia and len(listas) > 1:
        ato = _PLURAL_DA_LISTA_VAZIA.get(ato, ato)
    return replace(
        primeira,
        url=url,
        ato=ato,
        listas=listas,
        lugar="; ".join(lugares),
        onde=primeira.onde if len(lugares) == 1 else "; ".join(lugares),
    )


def _sem_lista(url):
    return url.split("?", 1)[0]


def _primeira_frase(texto):
    """A razão até o primeiro ponto: "As inscrições ficam abertas até 10/11/2026 às 18:00"."""
    return (texto or "").split(". ", 1)[0]


def _unicos(itens):
    vistos, saida = set(), []
    for item in itens:
        if item and item not in vistos:
            vistos.add(item)
            saida.append(item)
    return saida


def ordenar(providencias):
    """A regra fixa do contrato §4 (FR-4082): as suas, as de outros papéis, as que esperam.

    As suas: primeiro as que têm prazo, pelo mais próximo; depois pela espera mais antiga; o resto,
    na ordem da derivação — a do Perfil e a da jornada, que é estável. As de outros papéis, por
    papel, para que a pessoa leia "quem publica resultado" uma vez. As que esperam, na ordem da
    derivação. Nada aqui sugere urgência que o sistema não sabe.
    """
    indice = {id(item): n for n, item in enumerate(providencias)}
    suas = sorted(
        (p for p in providencias if p.grupo == SUA),
        key=lambda p: (
            p.ate is None,
            p.ate.timestamp() if p.ate else 0,
            p.desde is None,
            p.desde.timestamp() if p.desde else 0,
            indice[id(p)],
        ),
    )
    ordem_dos_papeis = {papel: n for n, papel in enumerate(a.ORDEM_DOS_PAPEIS)}
    outras = sorted(
        (p for p in providencias if p.grupo == DE_OUTRO),
        key=lambda p: (ordem_dos_papeis.get(p.responsavel, len(ordem_dos_papeis)), indice[id(p)]),
    )
    espera = [p for p in providencias if p.grupo == EM_ESPERA]
    return suas + outras + espera


@dataclass
class Nivel1:
    """O que o cartão "O que fazer agora" desenha depois da publicação."""

    brutas: list
    itens: list = field(init=False)

    def __post_init__(self):
        self.itens = ordenar(agrupar(self.brutas))

    @property
    def total(self):
        return len(self.itens)

    @property
    def suas(self):
        return sum(1 for item in self.itens if item.grupo == SUA)

    @property
    def mostradas(self):
        return self.itens[:MOSTRADAS]

    @property
    def demais(self):
        return self.itens[MOSTRADAS:]

    def _do_grupo(self, itens, grupo):
        return [item for item in itens if item.grupo == grupo]

    @property
    def suas_mostradas(self):
        return self._do_grupo(self.mostradas, SUA)

    @property
    def de_outros_mostradas(self):
        return self._do_grupo(self.mostradas, DE_OUTRO)

    @property
    def em_espera_mostradas(self):
        return self._do_grupo(self.mostradas, EM_ESPERA)

    @property
    def suas_demais(self):
        return self._do_grupo(self.demais, SUA)

    @property
    def de_outros_demais(self):
        return self._do_grupo(self.demais, DE_OUTRO)

    @property
    def em_espera_demais(self):
        return self._do_grupo(self.demais, EM_ESPERA)

    def __bool__(self):
        return bool(self.itens)


def contagem(nivel):
    """ "2 providências em aberto · 1 é sua" — sem percentual e sem fase (FR-4080)."""
    total, suas = nivel.total, nivel.suas
    if not total:
        return ""
    em_aberto = f"{total} {'providência' if total == 1 else 'providências'} em aberto"
    if not suas:
        return f"{em_aberto} · nenhuma é sua"
    return f"{em_aberto} · {suas} {'é sua' if suas == 1 else 'são suas'}"


def porque_nada(andamento, edital):
    """O porquê de "Nada em aberto" (FR-4086): o que a derivação viu, e não uma frase genérica."""
    perfis = [p for p in andamento.perfis if not p.sem_inscricao]
    if not perfis:
        return "nenhum Perfil com marco recebeu inscrição"
    if edital.status == "ENCERRADO":
        return "o Edital está encerrado, e nenhum ato esperado ficou para trás"
    return "todo ato esperado das listas está feito, ou não se aplica a elas"


def frase_da_atencao(atencoes):
    """A "Atenção" das Etapas sem efeito, numa frase só (D-010, FR-4087)."""
    nomes = [atencao.etapa for atencao in atencoes]
    if not nomes:
        return ""
    if len(nomes) == 1:
        return f"{nomes[0]} {a.SEM_EFEITO_NO_GPS}."
    return (
        f"{a._lista_de_nomes(nomes)} estão declaradas no Edital, e nenhum ato do GPS depende do "
        "resultado delas."
    )
