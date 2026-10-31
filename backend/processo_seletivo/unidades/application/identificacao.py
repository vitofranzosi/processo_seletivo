"""Como a unidade se apresenta fora do documento oficial: na moldura, na assinatura, no atendimento.

**Uma resposta, e cada um pergunta com o seu contexto** (109). Até aqui a marca "Cefor/Ifes" estava
escrita em dez arquivos, e o canal de atendimento era um só para a implantação. O documento oficial
já não dependia disso — o PDF lê a unidade do ato desde a 060 —, mas a moldura das telas e a
assinatura das mensagens diriam "Cefor" a quem atua num campus. Quem pergunta é quem sabe o
contexto: a gestão, pelo escopo do ator; o Edital, pelo dele; a página do ato, pelo que o ato
gravou; o que não tem unidade nenhuma — o portal, a página de acesso, a 404, a conta do candidato —,
pela implantação.

**A identidade do Ifes não sai do registro.** Ela é a mesma para toda unidade, e fica aqui em
constante. O compositor do PDF tem as suas (`SIGLA_DA_INSTITUICAO` e as linhas do cabeçalho), e as
duas não se importam uma à outra de propósito (D-007): este módulo entra em toda página, e o
compositor só no ato. Um teste confere que dizem o mesmo.

**Nenhuma memória entre pedidos** (D-001). O registro muda pelo `sincronizar_unidades`, que roda
noutro processo; guardar a sigla no servidor a faria envelhecer em silêncio até o reinício. A
tabela tem uma linha por unidade, e a leitura é pela chave.
"""

from dataclasses import dataclass

from django.conf import settings

from processo_seletivo.unidades.models import Unidade

SIGLA_DA_INSTITUICAO = "Ifes"
NOME_DA_INSTITUICAO = "Instituto Federal do Espírito Santo"


@dataclass(frozen=True)
class Identificacao:
    """A unidade ao lado do Ifes — ou só o Ifes, quando não há unidade a dizer.

    `sigla` vazia é a identificação **só da instituição**, e nunca a recaída num Cefor implícito:
    um escopo sem unidade registrada, o da administração institucional e a implantação com mais de
    uma unidade ativa dizem "Ifes", e não escolhem uma unidade por quem lê (FR-3201, FR-3202).
    """

    sigla: str = ""
    # O canal **da unidade**, sem a recaída. Quem precisa do canal a dizer pergunta a `canal()`.
    atendimento: str = ""

    @property
    def instituicao(self):
        return SIGLA_DA_INSTITUICAO

    @property
    def nome_da_instituicao(self):
        return NOME_DA_INSTITUICAO

    @property
    def rotulo(self):
        """ "Cefor/Ifes", ou "Ifes" — a forma da marca, do título e da assinatura das mensagens."""
        return f"{self.sigla}/{SIGLA_DA_INSTITUICAO}" if self.sigla else SIGLA_DA_INSTITUICAO

    @property
    def nome_curto(self):
        """ "Cefor", ou "Ifes" — a forma de "quem administra o sistema no Cefor"."""
        return self.sigla or SIGLA_DA_INSTITUICAO

    def canal(self, padrao=""):
        """O canal a dizer ao candidato: o da unidade, o da instituição, o `padrao` (FR-3212)."""
        return self.atendimento or canal_institucional() or padrao


SO_A_INSTITUICAO = Identificacao()


def _de(unidade):
    if unidade is None:
        return SO_A_INSTITUICAO
    return Identificacao(sigla=unidade.sigla, atendimento=unidade.atendimento)


def da_unidade(codigo):
    """A identificação do escopo pelo registro, ativa a unidade ou não.

    Desativada, ela continua sendo a unidade dos Editais que nela correm: o certame em curso
    termina com o nome que começou, como `exigir_unidade` já decide para as autoridades.
    """
    return _de(Unidade.objects.filter(codigo=str(codigo or "")).first())


def da_implantacao():
    """A unidade ativa, quando há exatamente uma; só o Ifes, com nenhuma ou com várias (D-002).

    É a regra do título da vitrine (FR-1611 da 072) levada às superfícies que não têm unidade de
    contexto. Sem o canal da unidade: essas superfícies são da conta do candidato e da instituição,
    e o atendimento delas é o institucional (FR-3214).
    """
    ativas = list(Unidade.objects.filter(ativa=True).values_list("sigla", flat=True)[:2])
    return Identificacao(sigla=ativas[0]) if len(ativas) == 1 else SO_A_INSTITUICAO


def do_ato(sigla_gravada, codigo):
    """A unidade como o ato a gravou (D-004), para a moldura e a assinatura do que é do ato.

    A sigla vem da Publicação, porque a página e o comprovante do ato não se reescrevem quando a
    unidade é renomeada (FR-3216). Sem o canal, e sem consultar o registro: quem precisa dizer por
    onde falar com a unidade hoje pergunta a `da_unidade`. Publicação anterior à 060, sem unidade
    gravada, recai no registro pelo escopo.
    """
    return Identificacao(sigla=sigla_gravada) if sigla_gravada else da_unidade(codigo)


def canal_da_unidade_por_escopo(campo_do_escopo="institution_scope"):
    """O canal da unidade como subconsulta, para quem já lê o Edital e não pode ler mais uma vez.

    O assistente de dúvidas tem orçamento exato de consultas (070): a unidade entra na leitura do
    Edital, anotada, e a recaída continua sendo a de `Identificacao.canal`.
    """
    from django.db.models import OuterRef, Subquery

    return Subquery(
        Unidade.objects.filter(codigo=OuterRef(campo_do_escopo)).values("atendimento")[:1]
    )


def canal_institucional():
    """O `PORTAL_ATENDIMENTO`: o canal da instituição, e a recaída do canal de cada unidade."""
    return (getattr(settings, "PORTAL_ATENDIMENTO", "") or "").strip()


__all__ = [
    "NOME_DA_INSTITUICAO",
    "SIGLA_DA_INSTITUICAO",
    "SO_A_INSTITUICAO",
    "Identificacao",
    "canal_da_unidade_por_escopo",
    "canal_institucional",
    "da_implantacao",
    "da_unidade",
    "do_ato",
]
