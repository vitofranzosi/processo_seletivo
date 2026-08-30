"""Quem assina institucionalmente um Edital — declarado, e não cadastrado.

**O achado era estreito, e a resposta é proporcional.** Publicar exigia digitar um UUID à mão, com
um exemplo de trinta e seis caracteres como dica, no ato de maior consequência do sistema. Na
prática, alguém manteria esse número num bloco de notas.

A resposta é oferecer uma escolha — não construir um cadastro. O catálogo declarado dá o que se
precisa (escolher sem digitar, revisável em diff, sem migration) e não traz o que não se precisa
(entidade, tela de gestão, permissão nova, ciclo de vida, migração de dados). É o mesmo padrão do
catálogo de seções da `006`, e usá-lo duas vezes é o que o torna um padrão.

**Sobre o identificador.** `Publicacao` exige `signatory_id` além de nome e cargo, e é por ele que
a auditoria responde quem assinou. O catálogo não o **introduz**: ele já era exigido, e era digitado
à mão — que foi exatamente o defeito. O que muda é a origem. Ele nunca é digitado, exibido ao
operador nem impresso no documento: é dado de vínculo, não de leitura (FR-044).

**Retirar uma autoridade daqui não afeta Publicação já praticada.** O ato persiste nome, cargo e
identificador no momento em que ocorre, e é imutável — o catálogo é a origem da escolha, não a fonte
de verdade do que foi assinado (FR-046).
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Autoridade:
    """Nome e cargo no exercício de atribuição pública, e nada além (FR-044).

    Sem CPF, matrícula, endereço, telefone, e-mail ou foto: é o mínimo que a Constituição já exige
    que o ato normativo registre, e o máximo que este catálogo pode conter.
    """

    chave: str
    identificador: UUID
    nome: str
    cargo: str

    def __str__(self):
        return f"{self.nome} — {self.cargo}"


CATALOGO: tuple[Autoridade, ...] = (
    Autoridade(
        chave="reitoria",
        identificador=UUID("11111111-1111-4111-8111-111111111111"),
        nome="Reitora do Ifes",
        cargo="Reitora",
    ),
    Autoridade(
        chave="pro-reitoria-ensino",
        identificador=UUID("22222222-2222-4222-8222-222222222222"),
        nome="Pró-Reitor de Ensino",
        cargo="Pró-Reitor de Ensino",
    ),
    Autoridade(
        chave="diretoria-cefor",
        identificador=UUID("33333333-3333-4333-8333-333333333333"),
        nome="Diretora do Cefor",
        cargo="Diretora-Geral do Centro de Referência em Formação e em Educação a Distância",
    ),
)

POR_CHAVE = {autoridade.chave: autoridade for autoridade in CATALOGO}


def escolher(chave):
    """A autoridade daquela chave, ou `None` quando a chave não está no catálogo.

    Devolver `None` em vez de levantar é deliberado: quem chama precisa recusar a publicação com a
    mensagem do formulário, e não com uma exceção que a tela traduziria de qualquer jeito.
    """
    return POR_CHAVE.get(str(chave or ""))
