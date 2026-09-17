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
    """O CEP na geração **vigente** — nunca numa geração antiga que ainda não foi recolhida.

    O recorte por `carga__vigente` é o que torna a troca de geração invisível para quem preenche:
    durante a carga nova, esta consulta continua respondendo pela anterior, inteira; no instante em
    que a vigência muda de dono, ela passa a responder pela nova. Não há janela em que ela veja uma
    mistura das duas.
    """
    linha = ReferenciaDeCep.objects.filter(cep=cep_normalizado, carga__vigente=True).first()
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
