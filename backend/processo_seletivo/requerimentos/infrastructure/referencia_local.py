"""A implementação da porta do endereço sobre a base carregada nesta instituição.

**Leitura por chave primária, e nada além.** A tabela é grande — a base de origem declara mais de um
milhão de CEPs —, e o acesso é sempre por igualdade no `cep`. Não há busca por logradouro, nem por
município: seriam varreduras sobre uma tabela desse tamanho, para uma pergunta que ninguém faz.

**Tabela vazia é estado válido.** Instituição que não carregou a base tem o sistema funcionando com
o preenchimento manual — e é isso que impede a referência de virar porta de entrada do processo
(`FR-390`).
"""

from processo_seletivo.requerimentos.domain.endereco import EnderecoDeReferencia
from processo_seletivo.requerimentos.models import ReferenciaDeCep


def buscar(cep_normalizado: str) -> EnderecoDeReferencia | None:
    linha = ReferenciaDeCep.objects.filter(pk=cep_normalizado).first()
    if linha is None:
        return None
    return EnderecoDeReferencia(
        cep=linha.cep,
        logradouro=linha.logradouro,
        bairro=linha.bairro,
        municipio=linha.municipio,
        uf=linha.uf,
        codigo_ibge=linha.codigo_ibge,
    )
