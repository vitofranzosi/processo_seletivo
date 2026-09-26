"""Criar um Perfil de Vaga a partir de outro do mesmo Edital (043).

Função pura, pela mesma razão de `reaproveitamento`: é aqui que a feature erra **em silêncio** se
errar. Uma referência da cópia que continue apontando a origem é coerente com os vizinhos, atravessa
a gravação e não falha nunca — porque, ao contrário do reuso de Edital inteiro, a origem continua
existindo no mesmo Edital. O LP02 publicaria a ampla concorrência do LP01, e nada acusaria.

**O remapeamento é o da `023`, e não um segundo.** `remapear` já percorre a lista fechada de
referências do Perfil e falha alto diante da que não conhece; uma travessia própria aqui divergiria
na primeira referência nova — o `generalCompetitionModalityId`, que nasceu na `014` e só entrou no
remapeamento na `027`, é o precedente (R-001).

**E o mapa é estendido, e não afrouxado.** No reuso, as Etapas também são copiadas e ganham
identidade nova. Aqui elas são do mesmo Edital e ficam (FR-642): cada Etapa **do Edital** é mapeada
para si mesma. Uma Etapa que não seja do Edital continua sem mapa, e continua estourando.
"""

import copy
import uuid

from processo_seletivo.editais.domain import marcos
from processo_seletivo.editais.domain.perfis import identidade_da_linha_geral
from processo_seletivo.editais.domain.reaproveitamento import (
    CAMPOS_SEM_TELA,
    mapa_de_identidades,
    remapear,
)


def duplicar_perfil(
    perfil,
    *,
    codigo,
    localidade,
    etapas_do_edital,
    codigo_gravado=None,
    nome_gravado=None,
    nova=uuid.uuid4,
):
    """O Perfil novo, com identidades novas, referências internas trocadas e as externas mantidas.

    `perfil` é a origem na forma de `forms.ler_perfis`, com `classificationMilestones` já trazido de
    onde ele mora — a etapa Perfis não o desenha (R-003). Não é alterado.

    `codigo_gravado` e `nome_gravado` são os da origem **no banco**, quando ela está gravada: o
    marco derivado foi derivado deles, e quem mudou o Código na tela sem gravar não pode fazer o
    marco parecer escrito à mão (R-005).
    """
    origem = _com_identidades(copy.deepcopy(perfil), nova)
    conteudo = {"profiles": [origem]}
    mapa = mapa_de_identidades(conteudo, nova=nova)
    mapa.update({str(etapa): str(etapa) for etapa in etapas_do_edital})
    copia = remapear(conteudo, mapa)["profiles"][0]

    # A linha geral é projeção do Perfil, e a identidade dela também (027): o que o mapa lhe deu é
    # sorteio, e sorteio faria a mesma linha nascer com duas identidades em duas gravações.
    copia["vacancyTable"] = [
        (
            {**linha, "id": str(identidade_da_linha_geral(copia["id"]))}
            if not linha.get("modalityId")
            else linha
        )
        for linha in copia.get("vacancyTable") or []
    ]
    copia["code"] = codigo
    # Vazia é vazia, e nunca a da origem: afirmar a Localidade de outro Perfil é o erro que passa
    # despercebido numa revisão de dezesseis cartões iguais (D-003).
    copia["locality"] = localidade
    copia["classificationMilestones"] = _marcos_da_copia(
        copia.get("classificationMilestones") or [],
        codigos_da_origem={perfil.get("code"), codigo_gravado},
        nomes_da_origem={perfil.get("name"), nome_gravado},
        codigo=codigo,
        nome=copia.get("name") or "",
    )
    # Conteúdo normativo que nenhuma tela desenha não viaja: a cópia o carregaria sem que quem
    # compõe pudesse revisá-lo ou removê-lo — a mesma razão do reuso (023).
    for campo in CAMPOS_SEM_TELA:
        copia.pop(campo, None)
    return copia


def _com_identidades(perfil, nova):
    """Identidade própria para cada item que chegou sem nenhuma (R-002).

    `forms._texto` devolve `""` para campo ausente, e `mapa_de_identidades` registra **por valor**:
    duas Regras com `id` vazio seriam mapeadas para a mesma identidade nova, e a cópia nasceria com
    duas Modalidades partilhando uma Regra. O conteúdo publicado sempre tem identidade; o formulário
    não tem essa garantia.
    """

    def garantir(item):
        if isinstance(item, dict) and not item.get("id"):
            item["id"] = str(nova())

    garantir(perfil)
    for modalidade in perfil.get("competitionModalities") or []:
        garantir(modalidade)
        if modalidade.get("normativeRule"):
            garantir(modalidade["normativeRule"])
    for colecao in ("declaredFacts", "vacancyTable", "classificationMilestones"):
        for item in perfil.get(colecao) or []:
            garantir(item)
    for marco in perfil.get("classificationMilestones") or []:
        for criterio in marco.get("tiebreakers") or []:
            garantir(criterio)
    return perfil


def _marcos_da_copia(marcos_copiados, *, codigos_da_origem, nomes_da_origem, codigo, nome):
    """Código e denominação derivados da origem viram derivados da cópia (FR-644, D-004).

    A `FR-420` da `030` manda derivar a identidade do marco **novo** a partir do Perfil; a `FR-421`
    protege o que já foi declarado. A cópia é conteúdo novo — e o que foi escrito à mão continua
    protegido, porque ali há decisão e não derivação.
    """
    return rederivar(
        marcos_copiados,
        derivacoes(marcos_copiados, codigos=codigos_da_origem, nomes=nomes_da_origem),
        codigo=codigo,
        nome=nome,
    )


def derivacoes(marcos_do_perfil, *, codigos, nomes):
    """Para cada marco, se o código e se a denominação são os que o sistema derivaria do Perfil.

    **Só o que `identidade_derivada` produz de fato**: o código do Perfil, ou ele seguido do
    desempate `-2`, `-3`… — e o desempate nunca passa do número de marcos do Perfil mais um. Um
    padrão aberto, de número qualquer, tomaria por derivado o `LP01-2025` que alguém escreveu à
    mão, e a cópia o reescreveria: exatamente a decisão que a `FR-421` protege.

    `codigos` e `nomes` são conjuntos porque o Perfil pode ter mais de um que valha — o digitado e o
    gravado (R-005).
    """
    limite = len(marcos_do_perfil) + 1
    derivaveis = {
        variante
        for base in codigos
        if base
        for variante in (base, *(f"{base}-{n}" for n in range(2, limite + 1)))
    }
    nomes_derivados = {
        marcos.identidade_derivada(codigo_do_perfil="", nome_do_perfil=item)[1]
        for item in nomes
        if item
    }
    return [
        ((marco.get("code") or "") in derivaveis, (marco.get("name") or "") in nomes_derivados)
        for marco in marcos_do_perfil
    ]


def rederivar(marcos_do_perfil, derivados, *, codigo, nome):
    """Os marcos com código e denominação derivados refeitos a partir de `codigo` e `nome`.

    `derivados` é o que `derivacoes` respondeu — um par por marco. Serve à cópia, no ato de
    duplicar, e ao **Perfil ainda não gravado que leva marcos em trânsito**: quem corrige o Código
    da cópia no cartão antes de gravar espera que o marco derivado acompanhe, e sem isso ele
    publicaria o Código de antes da correção.

    O desempate `-2`, `-3` é reproduzido passando os códigos já atribuídos — **começando pelos
    escritos à mão**, que ficam como estão e não podem ser disputados.
    """
    em_uso = [
        marco.get("code")
        for marco, (codigo_derivado, _) in zip(marcos_do_perfil, derivados, strict=True)
        if not codigo_derivado
    ]
    resultado = []
    for marco, (codigo_derivado, nome_derivado) in zip(marcos_do_perfil, derivados, strict=True):
        novo = dict(marco)
        if codigo_derivado or nome_derivado:
            codigo_novo, nome_novo = marcos.identidade_derivada(
                codigo_do_perfil=codigo, nome_do_perfil=nome, codigos_em_uso=em_uso
            )
            if codigo_derivado:
                novo["code"] = codigo_novo
                em_uso.append(codigo_novo)
            if nome_derivado:
                novo["name"] = nome_novo
        resultado.append(novo)
    return resultado
