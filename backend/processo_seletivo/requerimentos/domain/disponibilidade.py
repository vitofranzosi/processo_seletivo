"""Quando o requerimento é exigível, quando está disponível, e quando já foi enviado.

**Por que isto é domínio, e não tela.** A Constituição, no Princípio IV: *"Regras que afetem
direitos, elegibilidade, documentação (…) DEVEM residir e ser verificadas no domínio/backend.
Validações no frontend PODEM melhorar a experiência, mas **NÃO são fronteira de segurança**"*. Uma
disponibilidade que só a tela conhece é regra de domínio morando na tela — e o `POST` que chega sem
passar por ela não encontra nada que o recuse.

**Duas perguntas, e não uma — e a repartição não é estilo.** `convocacao` importa `inscricoes`: a
`Convocacao` aponta a `Inscricao`. Se a submissão da inscrição consultasse a política inteira,
`inscricoes` alcançaria `convocacao` e o ciclo `inscricoes → requerimentos → convocacao →
inscricoes` se fecharia. Nenhum teste o proíbe hoje — `A_MONTANTE` de
`test_dependencia_da_convocacao` é `("ocupacao", "classificacao", "resultados")` —, mas este
repositório mantém duas varreduras dedicadas a sentido de import, e fechar ciclo com elas por perto
é escolher o defeito que elas existem para impedir.

A saída é que a submissão pergunta **menos**: no instante em que alguém submete uma inscrição, o
ramo da convocação nunca se aplica — não há chamada para quem ainda não se inscreveu.
`exigido_na_inscricao` responde essa metade sem tocar em `convocacao`.

**E a separação precisa ser de módulo, não de função.** Este arquivo é domínio puro e não importa
nada; do lado da aplicação, a pergunta estreita mora em `application/exigencia.py` justamente
porque `application/preencher.py` importa `convocacao`. Uma redação anterior deixava as duas no
mesmo arquivo e chamava isso de repartição: quem importasse a função estreita carregaria o módulo
inteiro, e o ciclo se fecharia do mesmo jeito — o interpretador carrega módulos, não funções.
"""

from dataclasses import dataclass

from processo_seletivo.requerimentos.domain import nomes


@dataclass(frozen=True)
class Disponibilidade:
    """O que o domínio responde sobre uma Inscrição, e o que a tela traduz.

    `chamada` é a convocação concreta que abriu o requerimento, ou `None`. Ela viaja junto porque
    quem abre o rascunho precisa **persisti-la** em `convocacao_autorizadora` — devolver só um
    booleano obrigaria a aplicação a perguntar de novo, e duas leituras divergiriam.
    """

    exigido: bool
    momento: str
    disponivel: bool
    chamada: object | None = None
    # O estado do requerimento vigente, ou `""` quando não há linha. **Injetado**, como a chamada:
    # o domínio não consulta o banco, e quem chama já leu a linha para gravá-la.
    status_do_requerimento: str = ""

    @property
    def enviado(self) -> bool:
        return self.status_do_requerimento == nomes.ENVIADO

    @property
    def estado_de_leitura(self):
        """O vocabulário de tela, derivado — nunca coluna (`FR-405`).

        **`enviado` é conferido antes de `disponivel`**, e a ordem é a regra. A chamada que abriu o
        requerimento pode ter sido desfechada depois do envio; lida na outra ordem, a tela diria
        *"ainda indisponível"* a quem já enviou, e o que a pessoa mandou sumiria da vista dela
        (`FR-406`). Enviado é estado terminal de leitura: o que se recebeu continua legível.
        """
        if not self.exigido:
            return nomes.NAO_APLICAVEL
        if self.enviado:
            return nomes.ESTADO_ENVIADO
        if not self.disponivel:
            return nomes.AINDA_INDISPONIVEL
        if self.status_do_requerimento == nomes.RASCUNHO:
            return nomes.EM_PREENCHIMENTO
        return nomes.DISPONIVEL


def momento_declarado(conteudo) -> str:
    """O momento que o Edital publicou, ou `""` quando ele não declarou.

    **`null` com a chave presente é o "não exige"**, e não a ausência da chave: é a grafia que
    `publish_edital` pratica em `vacancyReversion` e `callForm`. Ler com `or {}` trata os dois
    casos sem que o chamador precise saber qual deles o conteúdo traz.
    """
    declaracao = (conteudo or {}).get("matriculationRequest") or {}
    momento = declaracao.get("moment") or ""
    return momento if momento in nomes.MOMENTOS else ""


def exigido_na_inscricao(conteudo) -> bool:
    """A metade que a submissão da inscrição consulta — e que **não alcança `convocacao`**.

    É a única pergunta que existe no instante da submissão, e mantê-la separada é o que impede o
    ciclo entre apps descrito no topo deste módulo.
    """
    return momento_declarado(conteudo) == nomes.NA_INSCRICAO


def apurar(conteudo, *, chamada_em_aberto=None, requerimento=None) -> Disponibilidade:
    """A política inteira: **se é exigível, se está disponível e se já foi enviado**.

    As duas leituras de banco são **injetadas** por quem chama — a aplicação as obtém, e o domínio
    não consulta nada por conta própria. `chamada_em_aberto` vem do seletor único da `019`;
    `requerimento` é a linha vigente, que quem chama já precisa ter em mãos.

    **Chamada em aberto, e não vigente**: uma convocação com desfecho continua vigente, e a própria
    feature de convocação registra o beco que confundir as duas produziu.
    """
    status = getattr(requerimento, "status", "") or ""
    momento = momento_declarado(conteudo)
    if not momento:
        return Disponibilidade(
            exigido=False, momento="", disponivel=False, status_do_requerimento=status
        )
    if momento == nomes.NA_INSCRICAO:
        # **A chamada viaja também neste ramo.** Ela não decide a *disponibilidade* aqui — quem
        # coleta na inscrição abre para todo mundo —, mas decide a **correção**: quem declarou em
        # março e é convocado em setembro precisa poder atualizar o endereço (`FR-410`, `R-2`).
        #
        # Descartá-la era o que fazia *conferir e atualizar* nunca aparecer justamente para quem
        # mais precisa dele, e o buraco não aparecia nos testes porque todos usavam o outro momento.
        return Disponibilidade(
            exigido=True,
            momento=momento,
            disponivel=True,
            chamada=chamada_em_aberto,
            status_do_requerimento=status,
        )
    return Disponibilidade(
        exigido=True,
        momento=momento,
        disponivel=chamada_em_aberto is not None,
        chamada=chamada_em_aberto,
        status_do_requerimento=status,
    )
