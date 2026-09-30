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
    """Cargo, nome e ato de nomeação no exercício de atribuição pública, e nada além (FR-044).

    Sem CPF, matrícula, endereço, telefone, e-mail ou foto: é o mínimo que a Constituição já exige
    que o ato normativo registre, e o máximo que este catálogo pode conter.

    **O cargo é obrigatório; o nome e o ato de nomeação, não** (054, FR-992, D-005). O campo de nome
    trazia a designação do cargo — "Diretora do Cefor" —, e o fecho do documento oficial a imprimia
    onde o leitor espera um nome: um nome que não é nome. Enquanto o Cefor não fornece o nome de
    quem assina e a portaria que o nomeou, as entradas ficam só com o cargo, e o fecho diz o cargo.
    Quando vierem, entram aqui, revisados em diff, e a publicação seguinte os imprime sem outra
    mudança. A portaria acompanha o nome porque nomeia a pessoa: as duas respostas vêm juntas.
    """

    chave: str
    identificador: UUID
    cargo: str
    nome: str = ""
    ato_de_nomeacao: str = ""

    def __str__(self):
        return quem_assinou(self.nome, self.cargo)


def quem_assinou(nome, cargo):
    """`nome — cargo`, ou só o cargo quando não há nome (054, FR-994).

    Uma função, e não a mesma f-string em cada tela: sem nome, a f-string deixava um travessão
    pendurado — " — Diretora-Geral…" —, e cada tela que a repetisse teria de lembrar a exceção.
    """
    nome = str(nome or "").strip()
    cargo = str(cargo or "").strip()
    return f"{nome} — {cargo}" if nome and cargo else nome or cargo


CATALOGO: tuple[Autoridade, ...] = (
    Autoridade(
        chave="reitoria",
        identificador=UUID("11111111-1111-4111-8111-111111111111"),
        cargo="Reitora",
    ),
    Autoridade(
        chave="pro-reitoria-ensino",
        identificador=UUID("22222222-2222-4222-8222-222222222222"),
        cargo="Pró-Reitor de Ensino",
    ),
    Autoridade(
        chave="diretoria-cefor",
        identificador=UUID("33333333-3333-4333-8333-333333333333"),
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
