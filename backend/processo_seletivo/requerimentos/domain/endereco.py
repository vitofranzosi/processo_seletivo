"""A porta do endereço: dado um CEP, o que uma referência sabe dizer sobre ele.

**O domínio não nomeia fornecedor** (`FR-389`). Quem implementa esta porta pode ser uma tabela
carregada por comando, um arquivo, um serviço — e a decisão de hoje é a base local, com a razão
escrita na `D-009`: consultar serviço de terceiro em tempo real transmitiria continuamente o CEP de
candidatos identificados para fora da instituição, e poria um certame em curso na dependência de
disponibilidade alheia.

**A porta pode devolver `None`, e isso não é erro.** CEP ausente da base, base vazia, base
desatualizada — os três são o mesmo caso para quem chama, e nenhum deles impede preenchimento,
envio, inscrição ou matrícula (`FR-390`). Serviço de referência é auxiliar; se ele pudesse barrar,
seria porta de entrada.

**Sem latitude e longitude** (`D-008`). A base de origem as oferece e adverte, ela própria, que a
confiabilidade delas é variável. Elas são recalculáveis a partir do CEP guardado, não têm consumidor
nesta feature, e a coordenada de um CEP não é a casa de ninguém: ela pode representar o logradouro,
o centro da localidade, um estabelecimento ou o município inteiro.
"""

from dataclasses import dataclass

TAMANHO = 8


@dataclass(frozen=True)
class EnderecoDeReferencia:
    """O que a referência afirma sobre um CEP. Campos vazios são normais, e não falha.

    `logradouro` vazio acontece em CEP de localidade, que não nomeia rua; `codigo_ibge` vazio
    acontece quando a base não o traz. Nos dois casos o que falta fica editável na tela, e o envio
    conclui — **exceto** o código IBGE, que nunca é digitável (`FR-388`).
    """

    cep: str
    logradouro: str
    bairro: str
    municipio: str
    uf: str
    codigo_ibge: str


def normalizar(cep) -> str:
    """Só dígitos, oito posições — ou `""` quando não é CEP.

    **Uma forma só, guardada uma vez** (`FR-387`). O candidato digita com traço, sem traço, com
    espaço; a comparação nunca pode depender de qual. É a mesma decisão que `cpf_normalizado` já
    registra na Inscrição, e pela mesma razão.
    """
    digitos = "".join(caractere for caractere in str(cep or "") if caractere.isdigit())
    return digitos if len(digitos) == TAMANHO else ""


# O fornecedor da referência, registrado por quem monta a aplicação — `apps.py::ready()`. **O
# domínio não o importa**, e é essa ausência que torna a `FR-389` real: uma importação daqui para
# `infrastructure` deixaria o domínio nomeando fornecedor enquanto a documentação jurava o
# contrário, e a promessa só se romperia no dia da troca.
#
# `None` é estado válido, e é o mesmo caso de base vazia: nada registrado, nenhum CEP reconhecido,
# e o preenchimento manual segue (`FR-390`).
_fornecedor = None


def registrar_fornecedor(fornecedor) -> None:
    """Liga a porta à implementação. Chamado uma vez, na inicialização do app."""
    global _fornecedor
    _fornecedor = fornecedor


def referencia_de_cep(cep) -> EnderecoDeReferencia | None:
    """A porta. A implementação concreta é **injetada**, e o domínio não sabe qual é.

    Mantida como função de módulo — e não como classe abstrata — porque há **uma** operação e um
    consumidor. Uma hierarquia aqui seria estrutura antes da regra que a consome, que é o que este
    repositório recusa desde os campos descritivos do Perfil.
    """
    normalizado = normalizar(cep)
    if not normalizado or _fornecedor is None:
        return None
    return _fornecedor(normalizado)
